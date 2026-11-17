-- =====================================================================
-- Hendrix QMS  -  Step 54: Facility Map (rooms and beds, overlays, equipment pins)
--
--   Facility > Facility Map (from the Perryville Cultivation board): a building is a
--   drawing of rectangles ("zones") - houses / rooms, beds or bays inside them, and
--   other rooms - and overlays recolour the same drawing:
--     * Stage and Plants: from the plant batches in the grow area each zone is linked to;
--     * Temperature: the latest reading of each zone against its day / night target;
--     * Power and Equipment: equipment pins placed on the map (watts x quantity).
--   Rooms tagged Dry, Cure, Vault or Manufacturing show what is in them now.
--
--   Tables
--     hx_site_maps      one drawing (a building or a floor), for one or more licenses
--     hx_map_zones      the rectangles; a bed points at its house (parent_id)
--     hx_zone_readings  temperature / RH readings (kept; voided with a reason, never deleted)
--     hx_map_pins       equipment pins (camera, light, fan, HVAC, generator, ...)
--
--   Access module 'facmap' (Facility Map): View = see the map / Edit = log readings and
--   place, move and edit equipment pins / Full = draw and import maps and zones, set
--   temperature and RH targets, remove pins, void readings.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-53.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_site_maps (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  license_ids   text[] not null default '{}',
  name          text not null check (length(trim(name)) > 0),
  width         numeric not null default 1000 check (width > 0),
  height        numeric not null default 600 check (height > 0),
  font_size     numeric,
  decor         jsonb not null default '[]'::jsonb,
  drawing_path  text,
  drawing_note  text not null default '',
  sort          int not null default 0,
  active        boolean not null default true,
  created_by    text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index if not exists hx_site_maps_state on hx_site_maps(state_id, sort);

create table if not exists hx_map_zones (
  id          text primary key,
  map_id      text not null references hx_site_maps(id),
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  code        text not null check (length(trim(code)) > 0),
  label       text not null default '',
  name        text not null default '',
  kind        text not null default 'room' check (kind in ('house','bed','room')),
  x           numeric not null default 0,
  y           numeric not null default 0,
  w           numeric not null default 10 check (w > 0),
  h           numeric not null default 10 check (h > 0),
  parent_id   text references hx_map_zones(id) on delete set null,
  cap         int check (cap is null or cap >= 0),
  info        text not null default '' check (info in ('','dry','cure','vault','mfg')),
  vert        boolean not null default false,
  area_id     text references hx_grow_areas(id),
  day_f       numeric check (day_f is null or day_f between 0 and 130),
  night_f     numeric check (night_f is null or night_f between 0 and 130),
  rh_target   numeric check (rh_target is null or rh_target between 0 and 100),
  note        text not null default '',
  sort        int not null default 0,
  updated_by  text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create unique index if not exists hx_map_zones_code on hx_map_zones(map_id, code);
create index if not exists hx_map_zones_map on hx_map_zones(map_id);

create table if not exists hx_zone_readings (
  id           text primary key,
  zone_id      text not null references hx_map_zones(id),
  map_id       text not null references hx_site_maps(id),
  state_id     text not null references hx_states(id),
  license_id   text not null references hx_licenses(id),
  read_at      timestamptz not null default now(),
  temp_f       numeric check (temp_f is null or temp_f between -40 and 160),
  rh           numeric check (rh is null or rh between 0 and 100),
  note         text not null default '',
  recorded_by  text not null default '',
  created_at   timestamptz not null default now(),
  voided       boolean not null default false,
  void_reason  text,
  voided_at    timestamptz
);
create index if not exists hx_zone_readings_map on hx_zone_readings(map_id, read_at desc);
create index if not exists hx_zone_readings_zone on hx_zone_readings(zone_id, read_at desc);

create table if not exists hx_map_pins (
  id            text primary key,
  map_id        text not null references hx_site_maps(id),
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  zone_id       text references hx_map_zones(id) on delete set null,
  x             numeric not null,
  y             numeric not null,
  type          text not null default 'other' check (type in ('camera','light','fan','hvac','dehumidifier','heater','pump','sensor','machine','chiller','generator','storage','other')),
  name          text not null default '',
  model         text not null default '',
  watts         numeric check (watts is null or watts >= 0),
  qty           int not null default 1 check (qty >= 1),
  hrs           numeric not null default 24 check (hrs between 0 and 24),
  gen_kw        numeric check (gen_kw is null or gen_kw >= 0),
  serves        text[] not null default '{}',
  fov           numeric check (fov is null or fov between 10 and 360),
  dir           numeric check (dir is null or dir between -360 and 360),
  equipment_id  text references hx_equipment(id),
  note          text not null default '',
  created_by    text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index if not exists hx_map_pins_map on hx_map_pins(map_id);

-- ---------- maps ----------
create or replace function hx_site_map_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare l text;
begin
  if tg_op = 'DELETE' then raise exception 'Maps are not deleted. Switch the map off instead.'; end if;
  if new.license_ids is null or coalesce(array_length(new.license_ids, 1), 0) = 0 then new.license_ids := array[new.license_id]; end if;
  if not (new.license_id = any(new.license_ids)) then new.license_ids := array[new.license_id] || new.license_ids; end if;
  foreach l in array new.license_ids loop
    if not exists (select 1 from hx_licenses where id = l and state_id = new.state_id) then raise exception 'Every license on a map must belong to the map''s state.'; end if;
    if not hx_can('facmap', 3, l) then raise exception 'Only Full access on the Facility Map (for every license on the map) can change a map.'; end if;
  end loop;
  if tg_op = 'INSERT' then new.created_by := coalesce(hx_me(), ''); new.created_at := now();
  else
    new.created_by := old.created_by; new.created_at := old.created_at;
    if new.state_id <> old.state_id then raise exception 'A map cannot move to another state.'; end if;
    if exists (select 1 from hx_map_zones z where z.map_id = new.id and not (z.license_id = any(new.license_ids))) then
      raise exception 'Zones on this map belong to a license you are taking off it. Move or delete those zones first.';
    end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_site_map_guard on hx_site_maps;
create trigger hx_site_map_guard before insert or update or delete on hx_site_maps for each row execute function hx_site_map_guard();
drop trigger if exists hx_site_maps_audit on hx_site_maps;
create trigger hx_site_maps_audit after insert or update on hx_site_maps for each row execute function hx_audit();

-- ---------- zones ----------
create or replace function hx_map_zone_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare m record; p record; v_targets boolean;
begin
  if tg_op = 'DELETE' then
    if not hx_can('facmap', 3, old.license_id) then raise exception 'Only Full access on the Facility Map can delete zones.'; end if;
    if exists (select 1 from hx_zone_readings where zone_id = old.id) then raise exception 'Zone % has temperature readings and is kept. Rename or move it instead.', old.code; end if;
    return old;
  end if;
  select * into m from hx_site_maps where id = new.map_id;
  if m.id is null then raise exception 'Unknown map.'; end if;
  new.state_id := m.state_id;
  if not (new.license_id = any(m.license_ids)) then raise exception 'That license is not on this map.'; end if;
  if not hx_can('facmap', 3, new.license_id) then raise exception 'Only Full access on the Facility Map can draw zones and set targets.'; end if;
  if tg_op = 'UPDATE' and new.map_id <> old.map_id then raise exception 'A zone cannot move to another map.'; end if;
  new.code := trim(new.code);
  if new.parent_id is not null then
    select * into p from hx_map_zones where id = new.parent_id;
    if p.id is null or p.map_id <> new.map_id then raise exception 'The parent zone must be on the same map.'; end if;
    if p.id = new.id then raise exception 'A zone cannot be its own parent.'; end if;
  end if;
  if new.area_id is not null and not exists (select 1 from hx_grow_areas where id = new.area_id and license_id = new.license_id) then
    raise exception 'The linked grow area belongs to another license.';
  end if;
  if new.day_f is not null and new.night_f is null then new.night_f := new.day_f; end if;
  if tg_op = 'UPDATE' then
    v_targets := (new.day_f, new.night_f, new.rh_target) is distinct from (old.day_f, old.night_f, old.rh_target);
    if v_targets then perform set_config('hx.reason', 'Targets: day ' || coalesce(new.day_f::text, '-') || ' F, night ' || coalesce(new.night_f::text, '-') || ' F, RH ' || coalesce(new.rh_target::text, '-') || '%', true); end if;
    new.created_at := old.created_at;
  else new.created_at := now(); end if;
  new.updated_by := coalesce(hx_me(), ''); new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_map_zone_guard on hx_map_zones;
create trigger hx_map_zone_guard before insert or update or delete on hx_map_zones for each row execute function hx_map_zone_guard();
drop trigger if exists hx_map_zones_audit on hx_map_zones;
create trigger hx_map_zones_audit after insert or update or delete on hx_map_zones for each row execute function hx_audit();

-- ---------- readings ----------
create or replace function hx_zone_reading_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare z record;
begin
  if tg_op = 'DELETE' then raise exception 'Readings are never deleted. Void the reading with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This reading is void.'; end if;
    if not new.voided then raise exception 'A reading cannot be changed. Void it and log it again.'; end if;
    if not hx_can('facmap', 3, old.license_id) then raise exception 'Only Full access can void a reading.'; end if;
    if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a reading.'; end if;
    if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a reading without changing anything else.'; end if;
    new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
    return new;
  end if;
  select * into z from hx_map_zones where id = new.zone_id;
  if z.id is null then raise exception 'Unknown zone.'; end if;
  new.map_id := z.map_id; new.state_id := z.state_id; new.license_id := z.license_id;
  if not hx_can('facmap', 2, new.license_id) then raise exception 'Logging a reading needs Edit access on the Facility Map.'; end if;
  if new.temp_f is null and new.rh is null then raise exception 'Enter the temperature, the humidity or both.'; end if;
  if new.read_at > now() + interval '5 minutes' then raise exception 'The reading time cannot be in the future.'; end if;
  if new.read_at < now() - interval '31 days' then raise exception 'A reading older than 31 days cannot be logged here.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  return new;
end $$;
drop trigger if exists hx_zone_reading_guard on hx_zone_readings;
create trigger hx_zone_reading_guard before insert or update or delete on hx_zone_readings for each row execute function hx_zone_reading_guard();
drop trigger if exists hx_zone_readings_audit on hx_zone_readings;
create trigger hx_zone_readings_audit after insert or update on hx_zone_readings for each row execute function hx_audit();

-- ---------- equipment pins ----------
create or replace function hx_map_pin_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare m record; z record;
begin
  if tg_op = 'DELETE' then
    if not hx_can('facmap', 3, old.license_id) then raise exception 'Only Full access on the Facility Map can remove pins.'; end if;
    return old;
  end if;
  select * into m from hx_site_maps where id = new.map_id;
  if m.id is null then raise exception 'Unknown map.'; end if;
  if tg_op = 'UPDATE' and new.map_id <> old.map_id then raise exception 'A pin cannot move to another map.'; end if;
  new.state_id := m.state_id;
  if new.zone_id is not null then
    select * into z from hx_map_zones where id = new.zone_id;
    if z.id is null or z.map_id <> new.map_id then raise exception 'The pin''s zone is on another map.'; end if;
    new.license_id := z.license_id;
  elsif new.license_id is null or not (new.license_id = any(m.license_ids)) then
    new.license_id := m.license_id;
  end if;
  if not hx_can('facmap', 2, new.license_id) then raise exception 'Placing and editing equipment pins needs Edit access on the Facility Map.'; end if;
  if new.equipment_id is not null and not exists (select 1 from hx_equipment where id = new.equipment_id and license_id = new.license_id) then
    raise exception 'The linked equipment belongs to another license.';
  end if;
  if new.x < 0 or new.y < 0 or new.x > m.width or new.y > m.height then raise exception 'The pin is off the map.'; end if;
  if tg_op = 'INSERT' then new.created_by := coalesce(hx_me(), ''); new.created_at := now();
  else new.created_by := old.created_by; new.created_at := old.created_at; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_map_pin_guard on hx_map_pins;
create trigger hx_map_pin_guard before insert or update or delete on hx_map_pins for each row execute function hx_map_pin_guard();
drop trigger if exists hx_map_pins_audit on hx_map_pins;
create trigger hx_map_pins_audit after insert or update or delete on hx_map_pins for each row execute function hx_audit();

-- ---------- row level security ----------
alter table hx_site_maps enable row level security;
alter table hx_map_zones enable row level security;
alter table hx_zone_readings enable row level security;
alter table hx_map_pins enable row level security;
drop policy if exists hx_site_maps_read on hx_site_maps;
drop policy if exists hx_site_maps_insert on hx_site_maps;
drop policy if exists hx_site_maps_update on hx_site_maps;
create policy hx_site_maps_read on hx_site_maps for select to authenticated using (exists (select 1 from unnest(license_ids) l where hx_can('facmap', 1, l)));
create policy hx_site_maps_insert on hx_site_maps for insert to authenticated with check (hx_can('facmap', 3, license_id));
create policy hx_site_maps_update on hx_site_maps for update to authenticated using (hx_can('facmap', 3, license_id)) with check (hx_can('facmap', 3, license_id));
drop policy if exists hx_map_zones_read on hx_map_zones;
drop policy if exists hx_map_zones_insert on hx_map_zones;
drop policy if exists hx_map_zones_update on hx_map_zones;
drop policy if exists hx_map_zones_delete on hx_map_zones;
create policy hx_map_zones_read on hx_map_zones for select to authenticated using (hx_can('facmap', 1, license_id));
create policy hx_map_zones_insert on hx_map_zones for insert to authenticated with check (hx_can('facmap', 3, license_id));
create policy hx_map_zones_update on hx_map_zones for update to authenticated using (hx_can('facmap', 3, license_id)) with check (hx_can('facmap', 3, license_id));
create policy hx_map_zones_delete on hx_map_zones for delete to authenticated using (hx_can('facmap', 3, license_id));
drop policy if exists hx_zone_readings_read on hx_zone_readings;
drop policy if exists hx_zone_readings_insert on hx_zone_readings;
drop policy if exists hx_zone_readings_update on hx_zone_readings;
create policy hx_zone_readings_read on hx_zone_readings for select to authenticated using (hx_can('facmap', 1, license_id));
create policy hx_zone_readings_insert on hx_zone_readings for insert to authenticated with check (hx_can('facmap', 2, license_id));
create policy hx_zone_readings_update on hx_zone_readings for update to authenticated using (hx_can('facmap', 3, license_id)) with check (hx_can('facmap', 3, license_id));
drop policy if exists hx_map_pins_read on hx_map_pins;
drop policy if exists hx_map_pins_insert on hx_map_pins;
drop policy if exists hx_map_pins_update on hx_map_pins;
drop policy if exists hx_map_pins_delete on hx_map_pins;
create policy hx_map_pins_read on hx_map_pins for select to authenticated using (hx_can('facmap', 1, license_id));
create policy hx_map_pins_insert on hx_map_pins for insert to authenticated with check (hx_can('facmap', 2, license_id));
create policy hx_map_pins_update on hx_map_pins for update to authenticated using (hx_can('facmap', 2, license_id)) with check (hx_can('facmap', 2, license_id));
create policy hx_map_pins_delete on hx_map_pins for delete to authenticated using (hx_can('facmap', 3, license_id));
grant select, insert, update on hx_site_maps to authenticated;
grant select, insert, update, delete on hx_map_zones to authenticated;
grant select, insert, update on hx_zone_readings to authenticated;
grant select, insert, update, delete on hx_map_pins to authenticated;

notify pgrst, 'reload schema';
