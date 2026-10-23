-- =====================================================================
-- Hendrix QMS  -  Step 8: Roles and Access
-- Roles you create (each with its own access per module), custom access per
-- person, and which licenses a person may work in. Enforced by the database.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-7.
-- Safe to run more than once.
--
-- Access levels per module:  none (0)  |  read = View (1)  |  editor = Edit (2)  |  admin = Full (3)
--   View : see the records
--   Edit : create records, continue batches, add and edit catalog items
--   Full : change filled-in records with a reason, void, manage lists, delete catalog items
-- A system admin (role = 'admin' on the profile) always has Full access everywhere.
-- A person's access to a module = their custom setting if one is set, otherwise
-- the highest level any of their roles gives. Inside a role or a custom setting,
-- a single facility log with no setting of its own follows "Facility Logs (all)".
-- =====================================================================

create table if not exists hx_roles (
  id          text primary key,
  name        text not null check (length(trim(name)) > 0),
  description text not null default '',
  perms       jsonb not null default '{}'::jsonb,
  sort        int not null default 0,
  created_at  timestamptz not null default now()
);
create unique index if not exists hx_roles_name on hx_roles(lower(trim(name)));

alter table hx_profiles add column if not exists role_ids    text[] not null default '{}';
alter table hx_profiles add column if not exists perms       jsonb  not null default '{}'::jsonb;
alter table hx_profiles add column if not exists license_ids text[] not null default '{}';

-- ---------- access functions ----------
create or replace function hx_rank(p text) returns int
language sql immutable as $$
  select case p when 'admin' then 3 when 'editor' then 2 when 'read' then 1 else 0 end;
$$;

create or replace function hx_perm(p_mod text) returns int
language plpgsql stable security definer set search_path = public as $$
declare p record; v int; v_child boolean := p_mod like 'logs\_%';
begin
  select * into p from hx_profiles where id::text = auth.uid()::text;
  if p.id is null or not coalesce(p.approved, false) then return 0; end if;
  if p.role = 'admin' then return 3; end if;
  -- 1) custom access on the person wins (a single log, then "Facility Logs (all)")
  if coalesce(p.perms, '{}'::jsonb) ? p_mod then return hx_rank(p.perms ->> p_mod); end if;
  if v_child and coalesce(p.perms, '{}'::jsonb) ? 'logs' then return hx_rank(p.perms ->> 'logs'); end if;
  -- 2) otherwise the best of their roles; inside a role a single log follows that role's "Facility Logs (all)"
  select coalesce(max(hx_rank(coalesce(r.perms ->> p_mod, case when v_child then r.perms ->> 'logs' end))), 0)
    into v from hx_roles r where r.id = any(p.role_ids);
  return v;
end $$;

create or replace function hx_lic_ok(p_lic text) returns boolean
language plpgsql stable security definer set search_path = public as $$
declare p record;
begin
  select * into p from hx_profiles where id::text = auth.uid()::text;
  if p.id is null or not coalesce(p.approved, false) then return false; end if;
  if p.role = 'admin' or coalesce(array_length(p.license_ids, 1), 0) = 0 then return true; end if;
  return p_lic = any(p.license_ids);
end $$;

create or replace function hx_can(p_mod text, p_lvl int, p_lic text default null) returns boolean
language sql stable security definer set search_path = public as $$
  select hx_perm(p_mod) >= p_lvl and (p_lic is null or hx_lic_ok(p_lic));
$$;

create or replace function hx_log_mod(p_type text) returns text
language sql immutable as $$
  select case p_type
    when 'sanitation' then 'logs_sanitation' when 'waste' then 'logs_waste'
    when 'scale_calibration' then 'logs_scale' when 'security' then 'logs_security'
    when 'security_inspection' then 'logs_security' when 'pest' then 'logs_pest'
    when 'equipment' then 'logs_equipment' when 'temperature' then 'logs_temp'
    when 'environmental' then 'logs_env' when 'visitor' then 'logs_visitor'
    else 'logs' end;
$$;

create or replace function hx_list_mod(p_key text) returns text
language sql immutable as $$
  select case when split_part(p_key, '.', 1) = 'common' then 'logs' else hx_log_mod(split_part(p_key, '.', 1)) end;
$$;

grant execute on function hx_rank(text), hx_perm(text), hx_lic_ok(text), hx_can(text,int,text), hx_log_mod(text), hx_list_mod(text) to authenticated;

-- ---------- profiles: only a system admin can change anyone's access ----------
create or replace function hx_profile_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (new.role is distinct from old.role or new.approved is distinct from old.approved
      or new.role_ids is distinct from old.role_ids or new.perms is distinct from old.perms
      or new.license_ids is distinct from old.license_ids)
     and auth.uid() is not null and not hx_fl_is_admin() then
    raise exception 'Only a system admin can change roles and access.';
  end if;
  if old.role = 'admin' and old.approved and (new.role is distinct from 'admin' or not new.approved)
     and not exists (select 1 from hx_profiles where id <> old.id and role = 'admin' and approved) then
    raise exception 'Hendrix needs at least one system admin. Make someone else an admin first.';
  end if;
  return new;
end $$;
drop trigger if exists hx_profiles_access_guard on hx_profiles;
create trigger hx_profiles_access_guard before update on hx_profiles
  for each row execute function hx_profile_guard();

-- ---------- visitor log: staff with Edit can sign visitors out; other changes need Full ----------
create or replace function hx_visitor_level() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then return new; end if;   -- QR kiosk functions
  if old.time_out is null and new.time_out is not null and not coalesce(new.voided, false) then return new; end if;
  if hx_perm('logs_visitor') < 3 then
    raise exception 'You can sign visitors out. Other changes need Full access to the Visitor Log.';
  end if;
  return new;
end $$;
do $$ begin
  if to_regclass('public.hx_visitor_log') is not null then
    execute 'drop trigger if exists hx_visitor_log_level on hx_visitor_log';
    execute 'create trigger hx_visitor_log_level before update on hx_visitor_log for each row execute function hx_visitor_level()';
  end if;
end $$;

-- ---------- batch guard: admin checks become "Full access to Batch Tracker" ----------
create or replace function hx_batch_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  s record; v_fsku text; v_fname text; a jsonb; b jsonb; k text; ov jsonb; nv jsonb; i int; v_admin boolean;
begin
  if tg_op = 'DELETE' then
    raise exception 'Batch records cannot be deleted. Void the batch with a reason instead.';
  end if;

  if tg_op = 'UPDATE' then
    if old.voided then
      raise exception 'This batch is void and cannot be changed.';
    end if;
    a := to_jsonb(old); b := to_jsonb(new);
    foreach k in array array['id','batch_type','signature','source','created_by','created_at'] loop
      if (a -> k) is distinct from (b -> k) then
        raise exception 'The % of a batch cannot be changed.', replace(k, '_', ' ');
      end if;
    end loop;
    -- voiding (admins only, see policy)
    if new.voided then
      if hx_perm('batch') < 3 then raise exception 'Only someone with Full access to the Batch Tracker can void a batch.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then
        raise exception 'A reason is required to void a batch.';
      end if;
      if (b - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason' - 'updated_at')
         is distinct from (a - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason' - 'updated_at') then
        raise exception 'Void a batch without changing anything else.';
      end if;
      new.voided_at := now(); new.voided_by := auth.uid(); new.edit_reason := null;
      perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (b ->> 'void_reason') is distinct from (a ->> 'void_reason') then
      raise exception 'The void reason cannot be changed.';
    end if;
  end if;

  -- names always come from the database: unchanged SKU / flavor keep their names
  if tg_op = 'UPDATE' then
    if new.sku_id is not distinct from old.sku_id then new.sku := old.sku; end if;
    if new.flavor_id is not null and new.flavor_id is not distinct from old.flavor_id then new.flavor := old.flavor; end if;
    if new.flavor is null then new.flavor := old.flavor; end if;
  end if;

  -- SKU / flavor rules (insert, or when they change)
  if tg_op = 'INSERT' or new.sku_id is distinct from old.sku_id or new.flavor_id is distinct from old.flavor_id then
    if new.sku_id is null then
      if new.batch_type <> 'ethanol_extraction' then
        raise exception 'Choose the SKU for this batch.';
      end if;
      new.sku := '';
    else
      select * into s from hx_skus where id = new.sku_id;
      if s.id is null then raise exception 'Unknown SKU.'; end if;
      if s.state_id <> new.state_id then raise exception 'That SKU belongs to a different state.'; end if;
      if s.product_type <> new.batch_type then raise exception 'That SKU is not a % SKU.', replace(new.batch_type,'_',' '); end if;
      if not s.active then raise exception 'That SKU is switched off (it needs a formulation).'; end if;
      if coalesce(array_length(s.license_ids,1),0) > 0 and not (new.license_id = any(s.license_ids)) then
        raise exception 'That SKU is not made under this license.';
      end if;
      new.sku := s.name;
    end if;
    if new.flavor_id is null then
      if tg_op = 'INSERT' or new.sku_id is distinct from old.sku_id then new.flavor := coalesce(new.flavor,''); end if;
    else
      select sku_id, name into v_fsku, v_fname from hx_flavors where id = new.flavor_id;
      if v_fsku is distinct from new.sku_id then raise exception 'That flavor belongs to a different SKU.'; end if;
      new.flavor := v_fname;
    end if;
  end if;

  if tg_op = 'INSERT' then
    new.edit_reason := null; new.voided := false; new.void_reason := null; new.voided_by := null; new.voided_at := null;
    return new;
  end if;

  -- changes to an existing batch
  v_admin := hx_perm('batch') >= 3;
  if v_admin then
    if coalesce(trim(new.edit_reason), '') = '' then
      raise exception 'A reason for the change is required.';
    end if;
    perform set_config('hx.reason', trim(new.edit_reason), true);
  else
    -- team members: fill in blanks only
    if coalesce(trim(old.batch_number),'') <> '' and new.batch_number is distinct from old.batch_number then
      raise exception 'Only blank fields can be filled in. Ask someone with Full access to change the batch number.';
    end if;
    if old.sku_id is not null and new.sku_id is distinct from old.sku_id then
      raise exception 'Only blank fields can be filled in. Ask someone with Full access to change the SKU.';
    end if;
    if (old.flavor_id is not null or coalesce(old.flavor,'') <> '') and (new.flavor_id is distinct from old.flavor_id or new.flavor is distinct from old.flavor) then
      raise exception 'Only blank fields can be filled in. Ask someone with Full access to change the flavor.';
    end if;
    for k, ov in select * from jsonb_each(old.data) loop
      continue when hx_batch_free_key(k);
      nv := new.data -> k;
      if jsonb_typeof(ov) = 'string' and trim(ov #>> '{}') <> '' and nv is distinct from ov then
        raise exception 'Only blank fields can be filled in. "%" already has a value; ask someone with Full access to change it.', replace(k,'_',' ');
      end if;
      if jsonb_typeof(ov) = 'array' and jsonb_array_length(ov) > 0 then
        if nv is null or jsonb_typeof(nv) <> 'array' or jsonb_array_length(nv) < jsonb_array_length(ov) then
          raise exception 'Rows already entered in "%" cannot be removed.', replace(k,'_',' ');
        end if;
        for i in 0 .. jsonb_array_length(ov) - 1 loop
          if (nv -> i) is distinct from (ov -> i) then
            raise exception 'Rows already entered in "%" cannot be changed.', replace(k,'_',' ');
          end if;
        end loop;
      end if;
    end loop;
    if jsonb_array_length(old.attachments) > 0 then
      if jsonb_array_length(new.attachments) < jsonb_array_length(old.attachments) then
        raise exception 'Attachments already on the batch cannot be removed.';
      end if;
      for i in 0 .. jsonb_array_length(old.attachments) - 1 loop
        if (new.attachments -> i) is distinct from (old.attachments -> i) then
          raise exception 'Attachments already on the batch cannot be changed.';
        end if;
      end loop;
    end if;
    perform set_config('hx.reason', coalesce(nullif(trim(new.edit_reason),''), 'Filled in blank fields'), true);
  end if;
  new.edit_reason := null;
  new.updated_at := now();
  return new;
end $$;

-- ---------- replace row-level security on every module table ----------
do $$
declare t text; pol record;
begin
  foreach t in array array['hx_rules','hx_log_lists','hx_facility_log','hx_visitor_log','hx_skus','hx_flavors',
                           'hx_formulations','hx_cost_library','hx_batches','hx_audit_log','hx_roles'] loop
    if to_regclass('public.'||t) is null then
      raise notice 'Table % not found - skipped', t;
      continue;
    end if;
    for pol in select policyname from pg_policies where schemaname = 'public' and tablename = t loop
      execute format('drop policy %I on %I', pol.policyname, t);
    end loop;
    execute format('alter table %I enable row level security', t);
  end loop;
end $$;

alter table hx_roles enable row level security;
create policy hx_roles_read   on hx_roles for select to authenticated using (hx_fl_is_approved());
create policy hx_roles_write  on hx_roles for all    to authenticated using (hx_fl_is_admin()) with check (hx_fl_is_admin());
grant select, insert, update, delete on hx_roles to authenticated;

create policy hx_rules_read   on hx_rules for select to authenticated using (hx_can('rulebook',1));
create policy hx_rules_insert on hx_rules for insert to authenticated with check (hx_can('rulebook',2));
create policy hx_rules_update on hx_rules for update to authenticated using (hx_can('rulebook',2)) with check (hx_can('rulebook',2));
create policy hx_rules_delete on hx_rules for delete to authenticated using (hx_can('rulebook',3));

create policy hx_log_lists_read  on hx_log_lists for select to authenticated using (hx_fl_is_approved() and hx_lic_ok(license_id));
create policy hx_log_lists_write on hx_log_lists for all to authenticated
  using (hx_can(hx_list_mod(list_key),3,license_id)) with check (hx_can(hx_list_mod(list_key),3,license_id));

create policy hx_facility_log_read   on hx_facility_log for select to authenticated using (hx_can(hx_log_mod(log_type),1,license_id));
create policy hx_facility_log_insert on hx_facility_log for insert to authenticated with check (hx_can(hx_log_mod(log_type),2,license_id) and source = 'app');
create policy hx_facility_log_update on hx_facility_log for update to authenticated
  using (hx_can(hx_log_mod(log_type),3,license_id)) with check (hx_can(hx_log_mod(log_type),3,license_id));

do $$ begin
  if to_regclass('public.hx_visitor_log') is not null then
    execute $p$create policy hx_visitor_log_read   on hx_visitor_log for select to authenticated using (hx_can('logs_visitor',1,license_id))$p$;
    execute $p$create policy hx_visitor_log_insert on hx_visitor_log for insert to authenticated with check (hx_can('logs_visitor',2,license_id))$p$;
    execute $p$create policy hx_visitor_log_update on hx_visitor_log for update to authenticated using (hx_can('logs_visitor',2,license_id)) with check (hx_can('logs_visitor',2,license_id))$p$;
  end if;
end $$;

create policy hx_skus_read      on hx_skus for select to authenticated using (hx_fl_is_approved());
create policy hx_skus_insert    on hx_skus for insert to authenticated with check (hx_can('products',2));
create policy hx_skus_update    on hx_skus for update to authenticated using (hx_can('products',2)) with check (hx_can('products',2));
create policy hx_skus_delete    on hx_skus for delete to authenticated using (hx_can('products',3));
create policy hx_flavors_read   on hx_flavors for select to authenticated using (hx_fl_is_approved());
create policy hx_flavors_insert on hx_flavors for insert to authenticated with check (hx_can('products',2));
create policy hx_flavors_update on hx_flavors for update to authenticated using (hx_can('products',2)) with check (hx_can('products',2));
create policy hx_flavors_delete on hx_flavors for delete to authenticated using (hx_can('products',3));

create policy hx_formulations_read   on hx_formulations for select to authenticated using (hx_can('formbank',1));
create policy hx_formulations_insert on hx_formulations for insert to authenticated with check (hx_can('formbank',2));
create policy hx_formulations_update on hx_formulations for update to authenticated using (hx_can('formbank',2)) with check (hx_can('formbank',2));
create policy hx_formulations_delete on hx_formulations for delete to authenticated using (hx_can('formbank',3));

create policy hx_cost_library_read   on hx_cost_library for select to authenticated using (hx_can('cogs',1));
create policy hx_cost_library_insert on hx_cost_library for insert to authenticated with check (hx_can('cogs',2));
create policy hx_cost_library_update on hx_cost_library for update to authenticated using (hx_can('cogs',2)) with check (hx_can('cogs',2));
create policy hx_cost_library_delete on hx_cost_library for delete to authenticated using (hx_can('cogs',3));

create policy hx_batches_read   on hx_batches for select to authenticated using (hx_can('batch',1,license_id));
create policy hx_batches_insert on hx_batches for insert to authenticated with check (hx_can('batch',2,license_id) and source = 'app');
create policy hx_batches_update on hx_batches for update to authenticated using (hx_can('batch',2,license_id)) with check (hx_can('batch',2,license_id));

create policy hx_audit_log_read on hx_audit_log for select to authenticated using (hx_can('audit',1));

-- audit role and access changes too
drop trigger if exists hx_roles_audit on hx_roles;
create trigger hx_roles_audit after insert or update or delete on hx_roles for each row execute function hx_audit();

notify pgrst, 'reload schema';
