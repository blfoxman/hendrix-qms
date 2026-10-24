-- =====================================================================
-- Hendrix QMS  -  Step 27: Cultivation records (CUL licenses)
-- CSQ Standard for Cultivation, Module 3A (3A.1.1-3A.1.3, 3A.1.5, 3A.1.7,
-- 3A.1.8, 3A.1.12-3A.1.16):
--   * grow areas: rooms, greenhouses and fields (type, canopy, irrigation
--     system, water source; outdoor land-use history and a risk assessment
--     re-evaluated every year)
--   * plant batches PB-YYYY-###: cultivar, source (received clone / seed lot,
--     own mother batch), planting date, plant count, grow media lot, METRC
--     tag, area and stage (propagation, vegetative, flowering, drying,
--     curing, done, destroyed)
--   * grow records per plant batch: nutrient / fertilizer / amendment
--     applications (approved chemical or received lot), crop protection
--     applications (approved pesticide with EPA number, rate, applicator,
--     re-entry and pre-harvest intervals), scouting, stage / area moves,
--     harvest (wet weight, harvest tag), drying and curing (dry weight,
--     room conditions), destruction
--   * harvest is refused before the pre-harvest interval of every crop
--     protection application has passed
-- Access module 'cultivation': View / Edit (record) / Full (void records,
--   destroy plant batches, switch areas off).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-26.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_grow_areas (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  name           text not null check (length(trim(name)) > 0),
  kind           text not null default 'indoor' check (kind in ('indoor','greenhouse','outdoor','mother','propagation','dry','cure','trim')),
  canopy_sqft    numeric,
  irrigation     text not null default '',
  water_source   text not null default '',
  limits         text not null default '',
  land_use       text not null default '',
  risk_assessed_on date,
  risk_notes     text not null default '',
  active         boolean not null default true,
  sort           int not null default 0,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create table if not exists hx_plant_batches (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  number         text not null default '',
  cultivar       text not null check (length(trim(cultivar)) > 0),
  source_kind    text not null default 'lot' check (source_kind in ('lot','mother','seed_own')),
  source_lot_id  text references hx_lots(id),
  mother_batch_id text references hx_plant_batches(id),
  source_note    text not null default '',
  planted_on     date not null default current_date,
  plant_count    int not null check (plant_count > 0),
  media_lot_id   text references hx_lots(id),
  media          text not null default '',
  metrc_tag      text not null default '',
  area_id        text references hx_grow_areas(id),
  stage          text not null default 'propagation' check (stage in ('propagation','vegetative','flowering','drying','curing','done','destroyed')),
  harvest_after  date,
  wet_weight     numeric,
  dry_weight     numeric,
  harvest_tag    text not null default '',
  notes          text not null default '',
  created_by     text not null default '',
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create unique index if not exists hx_plant_batches_number on hx_plant_batches(license_id, number);

create table if not exists hx_grow_events (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  batch_id       text not null references hx_plant_batches(id),
  kind           text not null check (kind in ('input','crop_protection','scouting','stage','harvest','dry','cure','destroy','note')),
  done_on        date not null default current_date,
  done_by        text not null default '',
  area_id        text references hx_grow_areas(id),
  chemical_id    text references hx_chemicals(id),
  lot_id         text references hx_lots(id),
  product        text not null default '',
  epa_reg        text not null default '',
  amount         text not null default '',
  method         text not null default '',
  rei_hours      int,
  phi_days       int,
  stage          text not null default '',
  observations   text not null default '',
  wet_weight     numeric,
  dry_weight     numeric,
  waste_weight   numeric,
  tag            text not null default '',
  conditions     text not null default '',
  files          jsonb not null default '[]'::jsonb,
  recorded_by    text not null default '',
  created_at     timestamptz not null default now(),
  voided         boolean not null default false,
  void_reason    text,
  voided_at      timestamptz
);
create index if not exists hx_grow_events_batch on hx_grow_events(batch_id, done_on desc);

create or replace function hx_cultivation_lic(p_lic text) returns void
language plpgsql security definer set search_path = public as $$
declare v_op text;
begin
  select coalesce(nullif(operation,''), hx_license_op(license_number, license_type)) into v_op from hx_licenses where id = p_lic;
  if v_op <> 'cultivation' then raise exception 'Cultivation records are only for cultivation (CUL) licenses.'; end if;
end $$;

create or replace function hx_grow_area_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_plant_batches where area_id = old.id) or exists (select 1 from hx_grow_events where area_id = old.id) then raise exception 'This area has grow records. Switch it off instead of deleting it.'; end if;
    return old;
  end if;
  perform hx_cultivation_lic(new.license_id);
  if new.kind = 'outdoor' and new.risk_assessed_on is not null and coalesce(trim(new.risk_notes), '') = '' then raise exception 'Describe the site risk assessment (land use, neighboring land, animals, controls).'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_grow_areas_guard on hx_grow_areas;
create trigger hx_grow_areas_guard before insert or update or delete on hx_grow_areas for each row execute function hx_grow_area_guard();
drop trigger if exists hx_grow_areas_place on hx_grow_areas;
create trigger hx_grow_areas_place before insert or update on hx_grow_areas for each row execute function hx_fl_guard();
drop trigger if exists hx_grow_areas_audit on hx_grow_areas;
create trigger hx_grow_areas_audit after insert or update or delete on hx_grow_areas for each row execute function hx_audit();

create or replace function hx_plant_batch_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Plant batches are never deleted. Destroy the batch with a reason.'; end if;
  if tg_op = 'INSERT' then
    perform hx_cultivation_lic(new.license_id);
    new.number := hx_next_number('hx_plant_batches', new.license_id, 'PB');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.stage := coalesce(nullif(new.stage, ''), 'propagation');
    if new.stage not in ('propagation','vegetative','flowering') then new.stage := 'propagation'; end if;
    new.harvest_after := null; new.wet_weight := null; new.dry_weight := null; new.harvest_tag := '';
    if new.source_kind = 'lot' and new.source_lot_id is null then raise exception 'Choose the received clone / seed lot (Receiving), or the mother plant batch.'; end if;
    if new.source_kind = 'mother' and new.mother_batch_id is null then raise exception 'Choose the mother plant batch.'; end if;
    if new.source_lot_id is not null and not exists (select 1 from hx_lots where id = new.source_lot_id and license_id = new.license_id and status = 'accepted') then
      raise exception 'Propagation material must come from an accepted lot of this license.';
    end if;
    if new.planted_on > current_date then raise exception 'The planting date cannot be in the future.'; end if;
    perform set_config('hx.reason', 'Plant batch started', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if coalesce(current_setting('hx.internal', true), '') <> 'on' then
      if (new.stage, new.area_id, new.harvest_after, new.wet_weight, new.dry_weight, new.harvest_tag) is distinct from (old.stage, old.area_id, old.harvest_after, old.wet_weight, old.dry_weight, old.harvest_tag) then
        raise exception 'Stage, area, harvest and weights change through the grow records.';
      end if;
      if old.stage in ('done','destroyed') then raise exception 'This plant batch is closed.'; end if;
    end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_plant_batches_guard on hx_plant_batches;
create trigger hx_plant_batches_guard before insert or update or delete on hx_plant_batches for each row execute function hx_plant_batch_guard();
drop trigger if exists hx_plant_batches_place on hx_plant_batches;
create trigger hx_plant_batches_place before insert or update on hx_plant_batches for each row execute function hx_fl_guard();
drop trigger if exists hx_plant_batches_audit on hx_plant_batches;
create trigger hx_plant_batches_audit after insert or update on hx_plant_batches for each row execute function hx_audit();

create or replace function hx_grow_event_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; c record; v_phi date;
begin
  if tg_op = 'DELETE' then raise exception 'Grow records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('cultivation', 3, old.license_id) then raise exception 'Only Full access can void a grow record.'; end if;
      if old.kind in ('harvest','dry','cure','destroy','stage') then raise exception 'Stage, harvest, drying, curing and destruction records cannot be voided. Record a correction note instead.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a record without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'files') is distinct from (to_jsonb(old) - 'files') then raise exception 'A grow record cannot be changed. Void it and record it again.'; end if;
    return new;
  end if;
  select * into b from hx_plant_batches where id = new.batch_id;
  if b.id is null or b.license_id <> new.license_id then raise exception 'That plant batch belongs to another license.'; end if;
  if b.stage in ('done','destroyed') and new.kind <> 'note' then raise exception 'This plant batch is closed (%).', b.stage; end if;
  if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
  if new.done_on < b.planted_on then raise exception 'The date is before the batch was planted.'; end if;
  if coalesce(trim(new.done_by), '') = '' then raise exception 'Enter who did it.'; end if;
  if new.chemical_id is not null then
    select * into c from hx_chemicals where id = new.chemical_id;
    if c.license_id <> new.license_id or c.status <> 'approved' then raise exception 'Only chemicals approved in the Chemical register can be applied.'; end if;
    if coalesce(trim(new.product), '') = '' then new.product := c.name; end if;
    if coalesce(trim(new.epa_reg), '') = '' then new.epa_reg := c.epa_reg; end if;
  end if;
  if new.lot_id is not null and not exists (select 1 from hx_lots where id = new.lot_id and license_id = new.license_id and status = 'accepted') then
    raise exception 'Inputs must come from an accepted lot of this license.';
  end if;
  if new.kind = 'input' then
    if new.chemical_id is null and new.lot_id is null then raise exception 'Choose the approved nutrient / amendment (Chemical register) or the received lot.'; end if;
    if coalesce(trim(new.amount), '') = '' then raise exception 'Enter the amount or rate applied.'; end if;
  elsif new.kind = 'crop_protection' then
    if new.chemical_id is null or c.purpose <> 'Pesticide / crop protection' then raise exception 'Crop protection must use a pesticide approved in the Chemical register.'; end if;
    if coalesce(trim(new.amount), '') = '' then raise exception 'Enter the rate applied (as on the label).'; end if;
    if new.phi_days is null or new.rei_hours is null then raise exception 'Enter the re-entry interval (hours) and the pre-harvest interval (days) from the label.'; end if;
  elsif new.kind = 'scouting' then
    if coalesce(trim(new.observations), '') = '' then raise exception 'Record what was seen (pests, disease, plant health).'; end if;
  elsif new.kind = 'stage' then
    if new.stage not in ('vegetative','flowering') and new.area_id is null then raise exception 'Choose the new stage or area.'; end if;
  elsif new.kind = 'harvest' then
    if b.stage not in ('vegetative','flowering') then raise exception 'Only a growing batch can be harvested.'; end if;
    if new.wet_weight is null or new.wet_weight <= 0 then raise exception 'Enter the wet weight.'; end if;
    if coalesce(trim(new.tag), '') = '' then raise exception 'Enter the harvest batch tag (METRC).'; end if;
    select max(done_on + phi_days) into v_phi from hx_grow_events where batch_id = new.batch_id and kind = 'crop_protection' and not voided and phi_days is not null;
    if v_phi is not null and new.done_on < v_phi then raise exception 'Too early to harvest: the pre-harvest interval of a crop protection application ends on %.', v_phi; end if;
  elsif new.kind = 'dry' then
    if b.stage not in ('drying','curing') then raise exception 'Record the harvest first.'; end if;
    if coalesce(trim(new.conditions), '') = '' then raise exception 'Record the drying room conditions (temperature, humidity).'; end if;
  elsif new.kind = 'cure' then
    if b.stage not in ('drying','curing') then raise exception 'Record the harvest first.'; end if;
    if new.dry_weight is null or new.dry_weight <= 0 then raise exception 'Enter the final dry weight.'; end if;
  elsif new.kind = 'destroy' then
    if not hx_can('cultivation', 3, new.license_id) then raise exception 'Only Full access can destroy a plant batch.'; end if;
    if coalesce(trim(new.observations), '') = '' then raise exception 'Give the reason and how it was destroyed (waste log / METRC).'; end if;
  end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  return new;
end $$;
drop trigger if exists hx_grow_events_guard on hx_grow_events;
create trigger hx_grow_events_guard before insert or update or delete on hx_grow_events for each row execute function hx_grow_event_guard();
drop trigger if exists hx_grow_events_place on hx_grow_events;
create trigger hx_grow_events_place before insert or update on hx_grow_events for each row execute function hx_fl_guard();
drop trigger if exists hx_grow_events_audit on hx_grow_events;
create trigger hx_grow_events_audit after insert or update on hx_grow_events for each row execute function hx_audit();

-- the plant batch follows its records: stage, area, earliest harvest, weights
create or replace function hx_grow_event_apply() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_why text;
begin
  v_why := case new.kind when 'input' then 'Nutrient applied' when 'crop_protection' then 'Crop protection applied' when 'stage' then 'Moved' when 'harvest' then 'Harvested'
    when 'dry' then 'Drying recorded' when 'cure' then 'Cured, dry weight recorded' when 'destroy' then 'Destroyed: ' || new.observations else 'Grow record' end || case when new.voided then ' (voided)' else '' end;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', v_why, true);
  update hx_plant_batches set harvest_after = (select max(done_on + phi_days) from hx_grow_events where batch_id = new.batch_id and kind = 'crop_protection' and not voided and phi_days is not null)
   where id = new.batch_id;
  if tg_op = 'INSERT' then
    perform set_config('hx.reason', v_why, true);
    if new.kind = 'stage' then
      update hx_plant_batches set stage = case when new.stage in ('vegetative','flowering') then new.stage else stage end, area_id = coalesce(new.area_id, area_id) where id = new.batch_id;
    elsif new.kind = 'harvest' then
      update hx_plant_batches set stage = 'drying', wet_weight = new.wet_weight, harvest_tag = new.tag, area_id = coalesce(new.area_id, area_id) where id = new.batch_id;
    elsif new.kind = 'dry' then
      update hx_plant_batches set stage = 'curing', area_id = coalesce(new.area_id, area_id) where id = new.batch_id;
    elsif new.kind = 'cure' then
      update hx_plant_batches set stage = 'done', dry_weight = new.dry_weight where id = new.batch_id;
    elsif new.kind = 'destroy' then
      update hx_plant_batches set stage = 'destroyed' where id = new.batch_id;
    end if;
  end if;
  perform set_config('hx.internal', '', true);
  return null;
end $$;
drop trigger if exists hx_grow_events_zapply on hx_grow_events;
create trigger hx_grow_events_zapply after insert or update on hx_grow_events for each row execute function hx_grow_event_apply();

alter table hx_grow_areas enable row level security;
alter table hx_plant_batches enable row level security;
alter table hx_grow_events enable row level security;
do $$ declare t text; begin
  foreach t in array array['hx_grow_areas','hx_plant_batches','hx_grow_events'] loop
    execute format('drop policy if exists %I on %I', t||'_read', t);
    execute format('drop policy if exists %I on %I', t||'_insert', t);
    execute format('drop policy if exists %I on %I', t||'_update', t);
    execute format('create policy %I on %I for select to authenticated using (hx_can(''cultivation'',1,license_id))', t||'_read', t);
    execute format('create policy %I on %I for insert to authenticated with check (hx_can(''cultivation'',2,license_id))', t||'_insert', t);
    execute format('create policy %I on %I for update to authenticated using (hx_can(''cultivation'',2,license_id)) with check (hx_can(''cultivation'',2,license_id))', t||'_update', t);
  end loop;
end $$;
drop policy if exists hx_grow_areas_delete on hx_grow_areas;
create policy hx_grow_areas_delete on hx_grow_areas for delete to authenticated using (hx_can('cultivation',3,license_id));
grant select, insert, update, delete on hx_grow_areas to authenticated;
grant select, insert, update on hx_plant_batches, hx_grow_events to authenticated;

notify pgrst, 'reload schema';
