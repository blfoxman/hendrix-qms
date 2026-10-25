-- =====================================================================
-- Hendrix QMS  -  Step 7: Batch Tracker
-- Batch production records for the 8 Black Fox batch types, using the
-- SKUs / flavors / formulations from Products (step 5).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-6.
-- Safe to run more than once.
--
-- Rules built into the database:
--   * every batch belongs to one state AND one license (never movable)
--   * batch / lot number is required and unique within a license
--   * the SKU must be a SKU of that state, switched on, made under that
--     license, and of the same product type; the flavor must be that SKU's
--   * a batch record is never deleted: it is VOIDED with a reason
--   * team members can continue a batch by filling in BLANK fields only;
--     a value that is already there can only be changed by an admin, and
--     an admin change needs a reason for change (kept in the audit trail)
--   * signature, creator and creation time are fixed
-- =====================================================================

alter table hx_states add column if not exists tracking_system text not null default 'METRC';

create or replace function hx_valid_batch_type(p text) returns boolean
language sql immutable as $$
  select coalesce(p,'') in ('ethanol_extraction','butane_extraction','pre_rolls','cartridges',
                            'gummies','infused_flower','moon_rocks','snow_caps');
$$;

create table if not exists hx_batches (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  batch_type    text not null check (hx_valid_batch_type(batch_type)),
  batch_number  text not null check (length(trim(batch_number)) > 0),
  sku_id        text references hx_skus(id),
  sku           text not null default '',
  flavor_id     text references hx_flavors(id),
  flavor        text not null default '',
  status        text not null default '',
  data          jsonb not null default '{}'::jsonb,
  attachments   jsonb not null default '[]'::jsonb,
  performed_by  text not null default '',
  signature     text,
  source        text not null default 'app',
  created_by    uuid default auth.uid(),
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  edit_reason   text,
  voided        boolean not null default false,
  void_reason   text,
  voided_by     uuid,
  voided_at     timestamptz
);
create unique index if not exists hx_batches_number on hx_batches(license_id, lower(trim(batch_number)));
create index if not exists hx_batches_lic on hx_batches(license_id, batch_type, created_at desc);

-- keys a team member may change even when they already hold a value:
-- dropdown choices (status, R&D and mandatory test results) and auto-calculated results
create or replace function hx_batch_free_key(k text) returns boolean
language sql immutable as $$
  select k in ('status','mandatory_testing','mandatory_test','gummy_mandatory_test',
               'rd1_result','rd2_result','primed_rd1','primed_rd2','gummy_rd1','gummy_rd2',
               'total_biomass_used','yield_quality_pct','yield_quality_band',
               'gummy_mixture_used','total_sugar_coated_gummies','total_packaged_gummies')
      or k ~ '(_expected|_status|_suggested)$';
$$;

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
      if not hx_fl_is_admin() then raise exception 'Only an admin can void a batch.'; end if;
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
  v_admin := hx_fl_is_admin();
  if v_admin then
    if coalesce(trim(new.edit_reason), '') = '' then
      raise exception 'A reason for the change is required.';
    end if;
    perform set_config('hx.reason', trim(new.edit_reason), true);
  else
    -- team members: fill in blanks only
    if coalesce(trim(old.batch_number),'') <> '' and new.batch_number is distinct from old.batch_number then
      raise exception 'Only blank fields can be filled in. Ask an admin to change the batch number.';
    end if;
    if old.sku_id is not null and new.sku_id is distinct from old.sku_id then
      raise exception 'Only blank fields can be filled in. Ask an admin to change the SKU.';
    end if;
    if (old.flavor_id is not null or coalesce(old.flavor,'') <> '') and (new.flavor_id is distinct from old.flavor_id or new.flavor is distinct from old.flavor) then
      raise exception 'Only blank fields can be filled in. Ask an admin to change the flavor.';
    end if;
    for k, ov in select * from jsonb_each(old.data) loop
      continue when hx_batch_free_key(k);
      nv := new.data -> k;
      if jsonb_typeof(ov) = 'string' and trim(ov #>> '{}') <> '' and nv is distinct from ov then
        raise exception 'Only blank fields can be filled in. "%" already has a value; ask an admin to change it.', replace(k,'_',' ');
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

drop trigger if exists hx_batches_guard on hx_batches;
create trigger hx_batches_guard before insert or update or delete on hx_batches
  for each row execute function hx_batch_guard();
drop trigger if exists hx_batches_place on hx_batches;
create trigger hx_batches_place before insert or update on hx_batches
  for each row execute function hx_fl_guard();
drop trigger if exists hx_batches_audit on hx_batches;
create trigger hx_batches_audit after insert or update or delete on hx_batches
  for each row execute function hx_audit();

alter table hx_batches enable row level security;
drop policy if exists hx_batches_read on hx_batches;
drop policy if exists hx_batches_insert on hx_batches;
drop policy if exists hx_batches_update on hx_batches;
create policy hx_batches_read   on hx_batches for select to authenticated using (hx_fl_is_approved());
create policy hx_batches_insert on hx_batches for insert to authenticated with check (hx_fl_is_approved() and source = 'app');
create policy hx_batches_update on hx_batches for update to authenticated using (hx_fl_is_approved()) with check (hx_fl_is_approved());
grant select, insert, update on hx_batches to authenticated;
grant execute on function hx_valid_batch_type(text) to authenticated;
grant execute on function hx_batch_free_key(text) to authenticated;

notify pgrst, 'reload schema';
