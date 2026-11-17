-- =====================================================================
-- Hendrix QMS  -  Step 57: Solventless batches and Rooms
--
--   * Batch Tracker > Solventless: Fresh Frozen tags (weight adds up) -> Hash (METRC tag,
--     grams, hash yield) -> Rosin (hash used, rosin produced, METRC tag, rosin yield)
--     -> Testing -> Storage room. "solventless" becomes a valid batch type and product type.
--   * Facility > Rooms: the license's rooms (storage, freezer, production, vault, lab ...).
--     Batches pick their storage room from this list and Receiving suggests them as lot
--     locations. Rooms are switched off, never deleted (records keep their room name).
--     Access module 'rooms': View sees the list / Full adds and edits rooms.
--   * Low yield alerts: a BAD / VERY BAD distillate, hash or rosin yield shows on the Dashboard of
--     the General Manager, Directors, Production Manager, Extraction Manager, Assistant Production
--     Manager (role names) and system admins, and is emailed (module batches).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-56.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_valid_product_type(p text) returns boolean
language sql immutable as $$
  select coalesce(p,'') in ('ethanol_extraction','butane_extraction','solventless','pre_rolls','cartridges',
                            'gummies','infused_flower','moon_rocks','snow_caps');
$$;
create or replace function hx_valid_batch_type(p text) returns boolean
language sql immutable as $$
  select coalesce(p,'') in ('ethanol_extraction','butane_extraction','solventless','pre_rolls','cartridges',
                            'gummies','infused_flower','moon_rocks','snow_caps');
$$;

-- Solventless batches have no SKU (like ethanol extraction): hx_batch_guard from step 8 with that one change
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
      if new.batch_type not in ('ethanol_extraction','solventless') then
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

create table if not exists hx_rooms (
  id          text primary key,
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  name        text not null check (length(trim(name)) > 0),
  kind        text not null default 'storage' check (kind in ('storage','freezer','cooler','vault','production','lab','quarantine','other')),
  conditions  text not null default '',
  notes       text not null default '',
  active      boolean not null default true,
  sort        int not null default 0,
  created_by  text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create unique index if not exists hx_rooms_name on hx_rooms(license_id, lower(trim(name)));

create or replace function hx_room_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Rooms are not deleted - switch the room off. Records keep the room name.'; end if;
  if not hx_can('rooms', 3, new.license_id) then raise exception 'Only Full access to Rooms can add or change rooms.'; end if;
  if not exists (select 1 from hx_licenses where id = new.license_id and state_id = new.state_id) then raise exception 'The license is not in this state.'; end if;
  new.name := trim(new.name);
  if tg_op = 'INSERT' then new.created_by := coalesce(hx_me(), ''); new.created_at := now();
  else
    if new.license_id <> old.license_id then raise exception 'A room cannot move to another license.'; end if;
    new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_room_guard on hx_rooms;
create trigger hx_room_guard before insert or update or delete on hx_rooms for each row execute function hx_room_guard();
drop trigger if exists hx_rooms_audit on hx_rooms;
create trigger hx_rooms_audit after insert or update on hx_rooms for each row execute function hx_audit();
alter table hx_rooms enable row level security;
drop policy if exists hx_rooms_read on hx_rooms;
drop policy if exists hx_rooms_insert on hx_rooms;
drop policy if exists hx_rooms_update on hx_rooms;
-- everyone who can work on the license sees its rooms (batch forms and Receiving pick from them)
create policy hx_rooms_read on hx_rooms for select to authenticated using (hx_lic_ok(license_id));
create policy hx_rooms_insert on hx_rooms for insert to authenticated with check (hx_can('rooms', 3, license_id));
create policy hx_rooms_update on hx_rooms for update to authenticated using (hx_can('rooms', 3, license_id)) with check (hx_can('rooms', 3, license_id));
grant select, insert, update on hx_rooms to authenticated;

-- ---------- low yield alerts (Dashboard) ----------
--   A batch whose distillate (ethanol), hash or rosin (solventless) yield is BAD or VERY BAD
--   (or under the expected range) raises an alert on the Dashboard for the General Manager,
--   Directors, Production Manager, Extraction Manager and Assistant Production Manager
--   (by role name) and system admins, and is emailed with the other alerts (module batches).
--   The alert closes by itself when the yield is corrected or the batch is voided.
create or replace function hx_yield_band(p_kind text, p_pct numeric) returns text
language sql immutable as $$
  select case when coalesce(p_pct, 0) <= 0 then 'none'
    when p_kind = 'distillate' then case when p_pct >= 20 and p_pct <= 24 then 'excellent' when p_pct >= 15 and p_pct < 20 then 'very_good'
      when p_pct >= 12 and p_pct < 15 then 'good' when p_pct >= 10 and p_pct < 12 then 'normal' when p_pct >= 6 and p_pct < 10 then 'bad'
      when p_pct >= 3 and p_pct < 6 then 'very_bad' else 'out_of_range' end
    when p_kind = 'hash' then case when p_pct >= 6 and p_pct <= 8 then 'very_good' when p_pct >= 5 and p_pct < 6 then 'good'
      when p_pct >= 3 and p_pct < 5 then 'bad' when p_pct >= 1 and p_pct < 3 then 'very_bad' else 'out_of_range' end
    when p_kind = 'rosin' then case when p_pct >= 4 and p_pct <= 6 then 'very_good' when p_pct >= 3 and p_pct < 4 then 'good'
      when p_pct >= 2 and p_pct < 3 then 'bad' when p_pct >= 1 and p_pct < 2 then 'very_bad' else 'out_of_range' end
    else 'none' end;
$$;
create or replace function hx_yield_low(p_kind text, p_pct numeric) returns boolean
language sql immutable as $$
  select coalesce(p_pct, 0) > 0 and (hx_yield_band(p_kind, p_pct) in ('bad', 'very_bad')
    or (hx_yield_band(p_kind, p_pct) = 'out_of_range' and p_pct < case p_kind when 'distillate' then 3 else 1 end));
$$;

create table if not exists hx_yield_alerts (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  batch_id      text not null references hx_batches(id),
  batch_number  text not null default '',
  batch_type    text not null default '',
  stage         text not null,
  pct           numeric not null,
  band          text not null,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  resolved_at   timestamptz,
  seen_by       text[] not null default '{}'
);
create index if not exists hx_yield_alerts_open on hx_yield_alerts(license_id, updated_at desc) where resolved_at is null;
drop trigger if exists hx_yield_alerts_audit on hx_yield_alerts;
create trigger hx_yield_alerts_audit after insert or update on hx_yield_alerts for each row execute function hx_audit();

create or replace function hx_yield_alert_me() returns boolean
language plpgsql stable security definer set search_path = public as $$
declare p record;
begin
  select * into p from hx_profiles where id::text = auth.uid()::text;
  if p.id is null or not coalesce(p.approved, false) then return false; end if;
  if p.role = 'admin' then return true; end if;
  return exists (select 1 from hx_roles r where r.id = any(p.role_ids)
    and (lower(trim(r.name)) in ('general manager', 'production manager', 'extraction manager', 'assistant production manager', 'assistant of production manager')
         or r.name ~* 'director'));
end $$;

create or replace function hx_batch_yield_alert() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v_pct numeric; v_band text; v_id text; v_old record; v_label text;
begin
  if new.batch_type not in ('ethanol_extraction', 'solventless') then return new; end if;
  foreach k in array case new.batch_type when 'ethanol_extraction' then array['distillate'] else array['hash', 'rosin'] end loop
    v_id := 'ya-' || new.id || '-' || k;
    begin
      v_pct := nullif(new.data ->> case k when 'distillate' then 'yield_quality_pct' when 'hash' then 'hash_yield_pct' else 'rosin_yield_pct' end, '')::numeric;
    exception when others then v_pct := null; end;
    if not coalesce(new.voided, false) and hx_yield_low(k, v_pct) then
      v_band := hx_yield_band(k, v_pct);
      select * into v_old from hx_yield_alerts where id = v_id;
      insert into hx_yield_alerts(id, state_id, license_id, batch_id, batch_number, batch_type, stage, pct, band)
      values (v_id, new.state_id, new.license_id, new.id, coalesce(new.batch_number, ''), new.batch_type, k, v_pct, v_band)
      on conflict (id) do update set pct = excluded.pct, band = excluded.band, batch_number = excluded.batch_number, updated_at = now(), resolved_at = null,
        seen_by = case when hx_yield_alerts.band <> excluded.band or hx_yield_alerts.resolved_at is not null then '{}'::text[] else hx_yield_alerts.seen_by end;
      if v_old.id is null or v_old.band <> v_band or v_old.resolved_at is not null then
        v_label := case v_band when 'bad' then 'BAD' when 'very_bad' then 'VERY BAD' else 'BELOW RANGE' end;
        insert into hx_notify_queue(state_id, license_id, module, kind, title, detail, page, ref)
        values (new.state_id, new.license_id, 'batches', 'yield_low',
          'Low ' || k || ' yield: ' || coalesce(new.batch_number, '') || ' ' || v_pct || '% (' || v_label || ')',
          case k when 'distillate' then 'Distillate / biomass. Expected 12-24% (Good to Excellent).' when 'hash' then 'Hash / fresh frozen. Expected 5-8% (Good to Very good).'
            else 'Rosin / fresh frozen. Expected 3-6% (Good to Very good).' end, 'batches', new.id);
      end if;
    else
      update hx_yield_alerts set resolved_at = now(), updated_at = now() where id = v_id and resolved_at is null;
    end if;
  end loop;
  return new;
end $$;
drop trigger if exists hx_batches_yield_alert on hx_batches;
create trigger hx_batches_yield_alert after insert or update on hx_batches for each row execute function hx_batch_yield_alert();

create or replace function hx_yield_alert_seen(p_id text) returns void
language plpgsql volatile security definer set search_path = public as $$
declare a record;
begin
  select * into a from hx_yield_alerts where id = p_id;
  if a.id is null then raise exception 'Unknown alert.'; end if;
  if not hx_yield_alert_me() or not hx_lic_ok(a.license_id) then raise exception 'This alert is not for you.'; end if;
  update hx_yield_alerts set seen_by = array_append(array_remove(seen_by, auth.uid()::text), auth.uid()::text) where id = p_id;
end $$;
alter table hx_yield_alerts enable row level security;
drop policy if exists hx_yield_alerts_read on hx_yield_alerts;
create policy hx_yield_alerts_read on hx_yield_alerts for select to authenticated using (hx_yield_alert_me() and hx_lic_ok(license_id));
grant select on hx_yield_alerts to authenticated;
revoke all on function hx_yield_alert_seen(text) from public;
grant execute on function hx_yield_alert_seen(text) to authenticated;
grant execute on function hx_yield_alert_me() to authenticated;

notify pgrst, 'reload schema';
