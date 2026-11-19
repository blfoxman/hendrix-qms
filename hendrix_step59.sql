-- =====================================================================
-- Hendrix QMS  -  Step 59: Cultivation takeover (Perryville board: Cul 60, Cul 22, Cul 24)
--
--   * Grow areas become a layout: house -> table / bay, with a code that matches the map
--     zone and the METRC location (60-H8-T4, E-H3-B2-NW, E-H4-B3-T4N), plant capacity,
--     a veg flag and a delay for houses that run longer than the cycle (Cul 22 H1).
--   * Harvest batches (hx_harvests): one row per METRC harvest batch, METRC numbers
--     (wet, waste, packaged, current, active / finished, drying location) plus the
--     post-harvest weights and dates the team enters in Hendrix (out of the dry room,
--     out of cure, trimmed, test, packaged, shipped). A harvest recorded in Hendrix
--     creates its harvest batch.
--   * METRC packages from cultivation (hx_cul_packages): tag, product bucket, grams,
--     source harvest batches and packages, transferred to.
--   * hx_cul_import: loads the Perryville takeover file and METRC exports, all or
--     nothing, Full access on Cultivation. Nothing is ever written to METRC.
--   * Capacity targets: clean and reset days, overplant %.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-58.
-- Safe to run more than once.
-- =====================================================================

-- ---------- layout ----------
alter table hx_grow_areas add column if not exists parent_id text references hx_grow_areas(id);
alter table hx_grow_areas add column if not exists code text not null default '';
alter table hx_grow_areas add column if not exists alias text not null default '';
alter table hx_grow_areas add column if not exists plant_cap int;
alter table hx_grow_areas add column if not exists veg boolean not null default false;
alter table hx_grow_areas add column if not exists delay_days int not null default 0;
alter table hx_grow_areas drop constraint if exists hx_grow_areas_kind_check;
alter table hx_grow_areas add constraint hx_grow_areas_kind_check check (kind in ('indoor','greenhouse','outdoor','mother','propagation','dry','cure','trim','house','table','bay'));
alter table hx_grow_areas drop constraint if exists hx_grow_areas_cap_check;
alter table hx_grow_areas add constraint hx_grow_areas_cap_check check (plant_cap is null or plant_cap between 0 and 100000);
alter table hx_grow_areas drop constraint if exists hx_grow_areas_delay_check;
alter table hx_grow_areas add constraint hx_grow_areas_delay_check check (delay_days between -60 and 120);
create unique index if not exists hx_grow_areas_code on hx_grow_areas(license_id, code) where code <> '';
create index if not exists hx_grow_areas_parent on hx_grow_areas(parent_id);

create or replace function hx_grow_area_tree() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record;
begin
  new.code := trim(coalesce(new.code, '')); new.alias := upper(regexp_replace(coalesce(new.alias, ''), '\s', '', 'g'));
  if new.parent_id is not null then
    if new.parent_id = new.id then raise exception 'An area cannot be inside itself.'; end if;
    select * into p from hx_grow_areas where id = new.parent_id;
    if p.id is null or p.license_id <> new.license_id then raise exception 'The house must be on the same license.'; end if;
    if p.parent_id is not null then raise exception 'Tables and bays sit inside a house (one level).'; end if;
    if new.kind = 'house' then raise exception 'A house cannot sit inside another house.'; end if;
  end if;
  if tg_op = 'UPDATE' and new.kind <> 'house' and old.kind = 'house' and exists (select 1 from hx_grow_areas where parent_id = new.id) then
    raise exception 'This house has tables / bays. Move them first.'; end if;
  return new;
end $$;
drop trigger if exists hx_grow_areas_tree on hx_grow_areas;
create trigger hx_grow_areas_tree before insert or update on hx_grow_areas for each row execute function hx_grow_area_tree();

-- ---------- targets ----------
alter table hx_cul_settings add column if not exists reset_days int not null default 7;
alter table hx_cul_settings add column if not exists overplant_pct int not null default 10;
alter table hx_cul_settings drop constraint if exists hx_cul_settings_reset_check;
alter table hx_cul_settings add constraint hx_cul_settings_reset_check check (reset_days between 0 and 60 and overplant_pct between 0 and 100);

-- veg batch -> the flower table it is lined up for
alter table hx_plant_batches add column if not exists next_area_id text references hx_grow_areas(id);

-- ---------- harvest batches ----------
create table if not exists hx_harvests (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  name             text not null check (length(trim(name)) > 0),
  strain           text not null default '',
  harvest_date     date,
  plants           int,
  wet_g            numeric,
  waste_g          numeric,
  packaged_g       numeric,
  current_g        numeric,
  finished         boolean not null default false,
  finished_on      date,
  active           boolean not null default true,
  drying_location  text not null default '',
  harvest_type     text not null default '',
  metrc_id         text not null default '',
  zone             text not null default '',
  area_id          text references hx_grow_areas(id),
  planted_on       date,
  flip_on          date,
  plant_batch_id   text references hx_plant_batches(id),
  metrc_stage      text not null default '',
  fresh_frozen     boolean not null default false,
  -- entered in Hendrix
  dry_start        date,
  dry_done         date,
  dry_room_g       numeric check (dry_room_g is null or dry_room_g >= 0),
  cure_done        date,
  cure_out_g       numeric check (cure_out_g is null or cure_out_g >= 0),
  test_sent        date,
  test_result      text not null default '' check (test_result in ('','passed','failed','retest')),
  trim_done        date,
  trimmed_g        numeric check (trimmed_g is null or trimmed_g >= 0),
  smalls_g         numeric check (smalls_g is null or smalls_g >= 0),
  shake_g          numeric check (shake_g is null or shake_g >= 0),
  packaged_on      date,
  shipped_on       date,
  note             text not null default '',
  source           text not null default 'metrc' check (source in ('metrc','hendrix','board')),
  imported_at      timestamptz,
  updated_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_harvests_name on hx_harvests(license_id, name);
create index if not exists hx_harvests_lic on hx_harvests(license_id, active, harvest_date desc);

create or replace function hx_harvest_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_int boolean := coalesce(current_setting('hx.internal', true), '') = 'on';
begin
  if tg_op = 'DELETE' then raise exception 'Harvest batches are never deleted.'; end if;
  perform hx_cultivation_lic(new.license_id);
  if new.area_id is not null and not exists (select 1 from hx_grow_areas where id = new.area_id and license_id = new.license_id) then raise exception 'That area belongs to another license.'; end if;
  if new.plant_batch_id is not null and not exists (select 1 from hx_plant_batches where id = new.plant_batch_id and license_id = new.license_id) then raise exception 'That plant batch belongs to another license.'; end if;
  if tg_op = 'INSERT' then
    if not v_int then raise exception 'Harvest batches come from a harvest record or the METRC import.'; end if;
  else
    new.license_id := old.license_id; new.state_id := old.state_id; new.created_at := old.created_at;
    if not v_int then
      if not hx_can('cultivation', 2, old.license_id) then raise exception 'You need Edit access to Cultivation.'; end if;
      -- the METRC side only changes through the import
      if (new.name, new.strain, new.harvest_date, new.plants, new.wet_g, new.waste_g, new.packaged_g, new.current_g, new.finished, new.finished_on, new.active, new.drying_location, new.harvest_type, new.metrc_id, new.metrc_stage, new.source, new.imported_at)
         is distinct from (old.name, old.strain, old.harvest_date, old.plants, old.wet_g, old.waste_g, old.packaged_g, old.current_g, old.finished, old.finished_on, old.active, old.drying_location, old.harvest_type, old.metrc_id, old.metrc_stage, old.source, old.imported_at) then
        raise exception 'METRC numbers change only through the METRC import.'; end if;
    end if;
  end if;
  if new.dry_done is not null and coalesce(new.dry_start, new.harvest_date) is not null and new.dry_done < coalesce(new.dry_start, new.harvest_date) then raise exception 'Dry done is before the drying started.'; end if;
  if new.cure_done is not null and new.dry_done is not null and new.cure_done < new.dry_done then raise exception 'Cure done is before dry done.'; end if;
  if greatest(new.dry_done, new.cure_done, new.test_sent, new.trim_done, new.packaged_on, new.shipped_on) > current_date then raise exception 'Dates cannot be in the future.'; end if;
  new.updated_by := coalesce(hx_me(), new.updated_by); new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_harvests_guard on hx_harvests;
create trigger hx_harvests_guard before insert or update or delete on hx_harvests for each row execute function hx_harvest_guard();
drop trigger if exists hx_harvests_place on hx_harvests;
create trigger hx_harvests_place before insert or update on hx_harvests for each row execute function hx_fl_guard();
drop trigger if exists hx_harvests_audit on hx_harvests;
create trigger hx_harvests_audit after insert or update on hx_harvests for each row execute function hx_audit();
alter table hx_harvests enable row level security;
drop policy if exists hx_harvests_read on hx_harvests;
drop policy if exists hx_harvests_update on hx_harvests;
create policy hx_harvests_read on hx_harvests for select to authenticated using (hx_can('cultivation',1,license_id));
create policy hx_harvests_update on hx_harvests for update to authenticated using (hx_can('cultivation',2,license_id)) with check (hx_can('cultivation',2,license_id));
grant select, update on hx_harvests to authenticated;

-- a harvest recorded in Hendrix opens its harvest batch (one way in)
create or replace function hx_grow_event_harvest() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record;
begin
  if new.kind <> 'harvest' or coalesce(trim(new.tag), '') = '' then return new; end if;
  select * into b from hx_plant_batches where id = new.batch_id;
  perform set_config('hx.internal', 'on', true);
  insert into hx_harvests (id, state_id, license_id, name, strain, harvest_date, plants, wet_g, waste_g, area_id, planted_on, plant_batch_id, source, dry_start)
  values ('hv-' || replace(gen_random_uuid()::text, '-', ''), new.state_id, new.license_id, trim(new.tag), b.cultivar, new.done_on, b.plant_count, new.wet_weight, new.waste_weight,
          coalesce(new.area_id, b.area_id), b.planted_on, b.id, 'hendrix', new.done_on)
  on conflict (license_id, name) do update set plant_batch_id = coalesce(hx_harvests.plant_batch_id, excluded.plant_batch_id),
    area_id = coalesce(hx_harvests.area_id, excluded.area_id), planted_on = coalesce(hx_harvests.planted_on, excluded.planted_on),
    wet_g = coalesce(hx_harvests.wet_g, excluded.wet_g), plants = coalesce(hx_harvests.plants, excluded.plants), harvest_date = coalesce(hx_harvests.harvest_date, excluded.harvest_date);
  perform set_config('hx.internal', '', true);
  return new;
end $$;
drop trigger if exists hx_grow_events_harvest on hx_grow_events;
create trigger hx_grow_events_harvest after insert on hx_grow_events for each row execute function hx_grow_event_harvest();

-- ---------- METRC packages (cultivation output) ----------
create table if not exists hx_cul_packages (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  tag              text not null check (tag ~ '^[0-9A-Z]{10,30}$'),
  bucket           text not null default '',
  item             text not null default '',
  strain           text not null default '',
  created_g        numeric,
  current_g        numeric,
  packaged_on      date,
  status           text not null default 'active',
  transferred_to   text not null default '',
  transferred_on   date,
  lab_status       text not null default '',
  source_harvests  text[] not null default '{}',
  source_packages  text[] not null default '{}',
  imported_at      timestamptz not null default now()
);
create unique index if not exists hx_cul_packages_tag on hx_cul_packages(license_id, tag);
create index if not exists hx_cul_packages_src on hx_cul_packages using gin (source_harvests);
create or replace function hx_cul_package_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if coalesce(current_setting('hx.internal', true), '') <> 'on' then raise exception 'METRC packages change only through the METRC import.'; end if;
  if tg_op = 'DELETE' then return old; end if;
  perform hx_cultivation_lic(new.license_id);
  return new;
end $$;
drop trigger if exists hx_cul_packages_guard on hx_cul_packages;
create trigger hx_cul_packages_guard before insert or update or delete on hx_cul_packages for each row execute function hx_cul_package_guard();
alter table hx_cul_packages enable row level security;
drop policy if exists hx_cul_packages_read on hx_cul_packages;
create policy hx_cul_packages_read on hx_cul_packages for select to authenticated using (hx_can('cultivation',1,license_id));
grant select on hx_cul_packages to authenticated;

-- ---------- import (Perryville takeover file, METRC exports) ----------
-- p: { areas:[{code,name,kind,parent,cap,veg,alias,delay}], harvests:[{...}], harvests_full:bool,
--      packages:[{...}], plants:[{batch,strain,count,planted,stage,area}], settings:{...} }
create or replace function hx_cul_import(p_lic text, p jsonb) returns jsonb
language plpgsql volatile security definer set search_path = public as $$
declare l record; a jsonb; h jsonb; k jsonb; v_id text; v_par text; v_area text; n_a int := 0; n_h int := 0; n_hn int := 0; n_k int := 0; n_b int := 0; n_bu int := 0; n_off int := 0;
        v_names text[] := '{}'; v_stage text; v_pb text;
begin
  select * into l from hx_licenses where id = p_lic;
  if l.id is null then raise exception 'Unknown license.'; end if;
  if not hx_can('cultivation', 3, p_lic) then raise exception 'Only Full access on Cultivation can import.'; end if;
  perform hx_cultivation_lic(p_lic);
  perform set_config('hx.reason', 'Cultivation import (' || coalesce(nullif(p->>'source', ''), 'METRC') || ')', true);

  -- houses first, then tables / bays / rooms
  for a in select x from jsonb_array_elements(coalesce(p->'areas', '[]'::jsonb)) x order by (x->>'kind' = 'house') desc loop
    if coalesce(a->>'code', '') = '' or coalesce(trim(a->>'name'), '') = '' then continue; end if;
    v_par := null;
    if coalesce(a->>'parent', '') <> '' then select id into v_par from hx_grow_areas where license_id = p_lic and code = a->>'parent'; end if;
    select id into v_id from hx_grow_areas where license_id = p_lic and code = a->>'code';
    if v_id is null then
      insert into hx_grow_areas (id, state_id, license_id, name, kind, code, alias, parent_id, plant_cap, veg, delay_days, sort)
      values ('ga-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, p_lic, left(a->>'name', 120), coalesce(a->>'kind', 'table'), a->>'code', coalesce(a->>'alias', ''), v_par,
              nullif(a->>'cap', '')::numeric::int, coalesce((a->>'veg')::boolean, false), coalesce((a->>'delay')::int, 0), coalesce((a->>'sort')::int, 0));
    else
      update hx_grow_areas set name = left(a->>'name', 120), kind = coalesce(a->>'kind', kind), alias = coalesce(nullif(a->>'alias', ''), alias), parent_id = coalesce(v_par, parent_id),
             plant_cap = coalesce(nullif(a->>'cap', '')::numeric::int, plant_cap), veg = coalesce((a->>'veg')::boolean, veg) where id = v_id;
    end if;
    n_a := n_a + 1;
  end loop;

  perform set_config('hx.internal', 'on', true);
  -- current plants in the ground (METRC plant batches by bed) -> plant batches
  for k in select x from jsonb_array_elements(coalesce(p->'plants', '[]'::jsonb)) x loop
    -- no planting date, no plant batch (dates are never made up)
    if coalesce(k->>'batch', '') = '' or coalesce((k->>'count')::int, 0) <= 0 or coalesce(k->>'planted', '') = '' then continue; end if;
    v_area := null;
    if coalesce(k->>'area', '') <> '' then select id into v_area from hx_grow_areas where license_id = p_lic and (code = k->>'area' or alias = upper(regexp_replace(k->>'area', '\s', '', 'g'))) limit 1; end if;
    v_stage := case when k->>'stage' ~* 'flower' then 'flowering' when k->>'stage' ~* 'veg' then 'vegetative' else 'propagation' end;
    select id into v_pb from hx_plant_batches where license_id = p_lic and metrc_tag = k->>'batch' and stage not in ('done','destroyed') limit 1;
    if v_pb is null then
      insert into hx_plant_batches (id, state_id, license_id, cultivar, source_kind, source_note, planted_on, plant_count, metrc_tag, area_id, stage, created_by)
      values ('pb-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, p_lic, coalesce(nullif(trim(k->>'strain'), ''), 'Unknown'), 'seed_own', 'Imported from METRC',
              (k->>'planted')::date, (k->>'count')::int, k->>'batch', v_area, v_stage, '');
      n_b := n_b + 1;
    else
      update hx_plant_batches set plant_count = (k->>'count')::int, area_id = coalesce(v_area, area_id),
             stage = case when stage in ('propagation','vegetative','flowering') then v_stage else stage end where id = v_pb;
      n_bu := n_bu + 1;
    end if;
  end loop;

  for h in select x from jsonb_array_elements(coalesce(p->'harvests', '[]'::jsonb)) x loop
    if coalesce(trim(h->>'name'), '') = '' then continue; end if;
    v_names := v_names || (h->>'name');
    v_area := null;
    if coalesce(h->>'zone', '') <> '' then select id into v_area from hx_grow_areas where license_id = p_lic and (code = h->>'zone' or alias = upper(regexp_replace(h->>'zone', '\s', '', 'g'))) limit 1; end if;
    select id into v_id from hx_harvests where license_id = p_lic and name = h->>'name';
    if v_id is null then
      insert into hx_harvests (id, state_id, license_id, name, source) values ('hv-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, p_lic, h->>'name', coalesce(nullif(p->>'source_kind', ''), 'metrc')) returning id into v_id;
      n_hn := n_hn + 1;
    end if;
    update hx_harvests set
      strain = coalesce(nullif(h->>'strain', ''), strain), harvest_date = coalesce(nullif(h->>'date', '')::date, harvest_date),
      plants = coalesce(nullif(h->>'plants', '')::numeric::int, plants), wet_g = coalesce(nullif(h->>'wet', '')::numeric, wet_g), waste_g = coalesce(nullif(h->>'waste', '')::numeric, waste_g),
      packaged_g = coalesce(nullif(h->>'packaged', '')::numeric, packaged_g), current_g = coalesce(nullif(h->>'current', '')::numeric, current_g),
      finished = coalesce((h->>'finished')::boolean, finished), finished_on = coalesce(nullif(h->>'finished_on', '')::date, finished_on),
      active = coalesce((h->>'active')::boolean, not coalesce((h->>'finished')::boolean, finished)),
      drying_location = coalesce(nullif(h->>'location', ''), drying_location), harvest_type = coalesce(nullif(h->>'type', ''), harvest_type), metrc_id = coalesce(nullif(h->>'metrc_id', ''), metrc_id),
      zone = coalesce(nullif(h->>'zone', ''), zone), area_id = coalesce(v_area, area_id),
      planted_on = coalesce(nullif(h->>'planted', '')::date, planted_on), flip_on = coalesce(nullif(h->>'flip', '')::date, flip_on), metrc_stage = coalesce(nullif(h->>'stage', ''), metrc_stage),
      fresh_frozen = coalesce((h->>'fresh_frozen')::boolean, fresh_frozen),
      -- post-harvest dates / weights from the old board only fill what Hendrix does not have yet
      dry_start = coalesce(dry_start, nullif(h->>'dry_start', '')::date), dry_done = coalesce(dry_done, nullif(h->>'dry_done', '')::date), cure_done = coalesce(cure_done, nullif(h->>'cure_done', '')::date),
      test_sent = coalesce(test_sent, nullif(h->>'test_sent', '')::date), trim_done = coalesce(trim_done, nullif(h->>'trim_done', '')::date), packaged_on = coalesce(packaged_on, nullif(h->>'packaged_on', '')::date),
      test_result = case when test_result = '' and coalesce(h->>'test_result', '') in ('passed','failed','retest') then h->>'test_result' else test_result end,
      dry_room_g = coalesce(dry_room_g, nullif(h->>'dry_room_g', '')::numeric), cure_out_g = coalesce(cure_out_g, nullif(h->>'cure_out_g', '')::numeric),
      note = case when note = '' then coalesce(h->>'note', '') else note end, imported_at = now()
    where id = v_id;
    n_h := n_h + 1;
  end loop;
  -- a full METRC active list: harvest batches not on it are no longer active
  if coalesce((p->>'harvests_full')::boolean, false) then
    update hx_harvests set active = false, imported_at = now() where license_id = p_lic and active and source <> 'hendrix' and not (name = any(v_names));
    get diagnostics n_off = row_count;
  end if;

  for k in select x from jsonb_array_elements(coalesce(p->'packages', '[]'::jsonb)) x loop
    if coalesce(k->>'tag', '') !~ '^[0-9A-Z]{10,30}$' then continue; end if;
    insert into hx_cul_packages (id, state_id, license_id, tag, bucket, item, strain, created_g, current_g, packaged_on, status, transferred_to, transferred_on, lab_status, source_harvests, source_packages, imported_at)
    values ('cp-' || replace(gen_random_uuid()::text, '-', ''), l.state_id, p_lic, k->>'tag', coalesce(k->>'bucket', ''), coalesce(k->>'item', ''), coalesce(k->>'strain', ''),
            nullif(k->>'created_g', '')::numeric, nullif(k->>'current_g', '')::numeric, nullif(k->>'packaged_on', '')::date, coalesce(nullif(k->>'status', ''), 'active'),
            coalesce(k->>'to', ''), nullif(k->>'to_on', '')::date, coalesce(k->>'lab', ''),
            coalesce(array(select jsonb_array_elements_text(k->'harvests')), '{}'), coalesce(array(select jsonb_array_elements_text(k->'sources')), '{}'), now())
    on conflict (license_id, tag) do update set bucket = coalesce(nullif(excluded.bucket, ''), hx_cul_packages.bucket), item = coalesce(nullif(excluded.item, ''), hx_cul_packages.item),
      strain = coalesce(nullif(excluded.strain, ''), hx_cul_packages.strain), created_g = coalesce(excluded.created_g, hx_cul_packages.created_g), current_g = coalesce(excluded.current_g, hx_cul_packages.current_g),
      packaged_on = coalesce(excluded.packaged_on, hx_cul_packages.packaged_on), status = excluded.status, transferred_to = coalesce(nullif(excluded.transferred_to, ''), hx_cul_packages.transferred_to),
      transferred_on = coalesce(excluded.transferred_on, hx_cul_packages.transferred_on), lab_status = coalesce(nullif(excluded.lab_status, ''), hx_cul_packages.lab_status),
      source_harvests = case when cardinality(excluded.source_harvests) > 0 then excluded.source_harvests else hx_cul_packages.source_harvests end,
      source_packages = case when cardinality(excluded.source_packages) > 0 then excluded.source_packages else hx_cul_packages.source_packages end, imported_at = now();
    n_k := n_k + 1;
  end loop;

  if jsonb_typeof(p->'settings') = 'object' then
    insert into hx_cul_settings (license_id, state_id) values (p_lic, l.state_id) on conflict (license_id) do nothing;
    update hx_cul_settings set cycle_days = coalesce((p->'settings'->>'cycle_days')::int, cycle_days), veg_days = coalesce((p->'settings'->>'veg_days')::int, veg_days),
      window_days = coalesce((p->'settings'->>'window_days')::int, window_days), reset_days = coalesce((p->'settings'->>'reset_days')::int, reset_days),
      overplant_pct = coalesce((p->'settings'->>'overplant_pct')::int, overplant_pct) where license_id = p_lic;
  end if;
  perform set_config('hx.internal', '', true);
  return jsonb_build_object('areas', n_a, 'plant_batches_new', n_b, 'plant_batches_updated', n_bu, 'harvests', n_h, 'harvests_new', n_hn, 'harvests_closed', n_off, 'packages', n_k);
end $$;
revoke all on function hx_cul_import(text, jsonb) from public, anon;
grant execute on function hx_cul_import(text, jsonb) to authenticated;

notify pgrst, 'reload schema';
