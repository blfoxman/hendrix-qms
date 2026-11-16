-- =====================================================================
-- Hendrix QMS  -  Step 52: Cultivation Batch Tracker
--
--   Cultivation > Batch tracker: every running plant batch on one screen, on an
--   8-step lifecycle (Veg, Flower, Harvest, Dry, Cure, Test + trim, Package, Ship),
--   with the day count, the next step and its date, late flags, plants and weights.
--
--   * After the cure (final dry weight) a batch now goes on to Test + trim, Package
--     and Ship instead of closing. New grow records: Sent to the lab, Test passed (COA),
--     Packaged, Shipped / transferred. "Shipped / transferred" closes the batch.
--     Batches that were already closed stay closed.
--   * A planned harvest start can be set on a batch (for example after a trichome check).
--   * Each cultivation license has its own targets: seed to harvest days, veg days,
--     harvest window and the days allowed for dry, cure, test + trim, package and ship.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-51.
-- Safe to run more than once.
-- =====================================================================

alter table hx_plant_batches drop constraint if exists hx_plant_batches_stage_check;
alter table hx_plant_batches add constraint hx_plant_batches_stage_check check (stage in ('propagation','vegetative','flowering','drying','curing','trim','package','ship','done','destroyed'));
alter table hx_plant_batches add column if not exists harvest_start date;
alter table hx_grow_events drop constraint if exists hx_grow_events_kind_check;
alter table hx_grow_events add constraint hx_grow_events_kind_check check (kind in ('input','crop_protection','scouting','stage','harvest','dry','cure','lab','tested','packaged','shipped','destroy','note'));

create table if not exists hx_cul_settings (
  license_id     text primary key references hx_licenses(id),
  state_id       text not null references hx_states(id),
  cycle_days     int not null default 80 check (cycle_days between 20 and 400),
  veg_days       int not null default 20 check (veg_days between 0 and 200),
  window_days    int not null default 4 check (window_days between 0 and 60),
  dry_days       int not null default 7 check (dry_days between 1 and 90),
  cure_days      int not null default 14 check (cure_days between 1 and 180),
  trim_days      int not null default 7 check (trim_days between 1 and 90),
  package_days   int not null default 7 check (package_days between 1 and 90),
  ship_days      int not null default 7 check (ship_days between 1 and 90),
  updated_by     text not null default '',
  updated_at     timestamptz not null default now()
);
create or replace function hx_cul_settings_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Cultivation targets are not deleted.'; end if;
  if not hx_can('cultivation', 3, new.license_id) then raise exception 'Only Full access on Cultivation can change the targets.'; end if;
  perform hx_cultivation_lic(new.license_id);
  if tg_op = 'UPDATE' and new.license_id <> old.license_id then raise exception 'Targets cannot move to another license.'; end if;
  if new.veg_days >= new.cycle_days then raise exception 'Veg days must be shorter than seed to harvest days.'; end if;
  new.updated_by := coalesce(hx_me(), ''); new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_cul_settings_guard on hx_cul_settings;
create trigger hx_cul_settings_guard before insert or update or delete on hx_cul_settings for each row execute function hx_cul_settings_guard();
drop trigger if exists hx_cul_settings_audit on hx_cul_settings;
create trigger hx_cul_settings_audit after insert or update on hx_cul_settings for each row execute function hx_audit();
alter table hx_cul_settings enable row level security;
drop policy if exists hx_cul_settings_read on hx_cul_settings;
drop policy if exists hx_cul_settings_insert on hx_cul_settings;
drop policy if exists hx_cul_settings_update on hx_cul_settings;
create policy hx_cul_settings_read on hx_cul_settings for select to authenticated using (hx_can('cultivation',1,license_id));
create policy hx_cul_settings_insert on hx_cul_settings for insert to authenticated with check (hx_can('cultivation',3,license_id));
create policy hx_cul_settings_update on hx_cul_settings for update to authenticated using (hx_can('cultivation',3,license_id)) with check (hx_can('cultivation',3,license_id));
grant select, insert, update on hx_cul_settings to authenticated;

create or replace function hx_grow_event_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; c record; v_phi date;
begin
  if tg_op = 'DELETE' then raise exception 'Grow records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('cultivation', 3, old.license_id) then raise exception 'Only Full access can void a grow record.'; end if;
      if old.kind in ('harvest','dry','cure','destroy','stage','tested','packaged','shipped') then raise exception 'Stage, harvest, drying, curing, testing, packaging, shipping and destruction records cannot be voided. Record a correction note instead.'; end if;
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
  elsif new.kind = 'lab' then
    if b.stage <> 'trim' then raise exception 'Record the cure (final dry weight) before sending to the lab.'; end if;
    if coalesce(trim(new.observations), '') = '' then raise exception 'Enter the lab and the sample sent.'; end if;
  elsif new.kind = 'tested' then
    if b.stage <> 'trim' then raise exception 'Only a batch in Test + trim can get its test result.'; end if;
    if coalesce(trim(new.tag), '') = '' then raise exception 'Enter the COA or sample number of the passing test.'; end if;
  elsif new.kind = 'packaged' then
    if b.stage <> 'package' then raise exception 'Record the passing test result before packaging.'; end if;
    if coalesce(trim(new.observations), '') = '' then raise exception 'Describe what was packaged (units, sizes, package tags).'; end if;
  elsif new.kind = 'shipped' then
    if b.stage not in ('trim','package','ship') then raise exception 'Only a cured batch can be shipped or transferred.'; end if;
    if coalesce(trim(new.observations), '') = '' then raise exception 'Enter where it went (customer, license or manufacturing) and the manifest.'; end if;
  elsif new.kind = 'destroy' then
    if not hx_can('cultivation', 3, new.license_id) then raise exception 'Only Full access can destroy a plant batch.'; end if;
    if coalesce(trim(new.observations), '') = '' then raise exception 'Give the reason and how it was destroyed (waste log / METRC).'; end if;
  end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  return new;
end $$;

create or replace function hx_grow_event_apply() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_why text;
begin
  v_why := case new.kind when 'input' then 'Nutrient applied' when 'crop_protection' then 'Crop protection applied' when 'stage' then 'Moved' when 'harvest' then 'Harvested'
    when 'dry' then 'Drying recorded' when 'cure' then 'Cured, dry weight recorded' when 'lab' then 'Sent to the lab' when 'tested' then 'Test passed (COA)' when 'packaged' then 'Packaged' when 'shipped' then 'Shipped / transferred' when 'destroy' then 'Destroyed: ' || new.observations else 'Grow record' end || case when new.voided then ' (voided)' else '' end;
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
      update hx_plant_batches set stage = 'trim', dry_weight = new.dry_weight where id = new.batch_id;
    elsif new.kind = 'tested' then
      update hx_plant_batches set stage = 'package' where id = new.batch_id;
    elsif new.kind = 'packaged' then
      update hx_plant_batches set stage = 'ship' where id = new.batch_id;
    elsif new.kind = 'shipped' then
      update hx_plant_batches set stage = 'done' where id = new.batch_id;
    elsif new.kind = 'destroy' then
      update hx_plant_batches set stage = 'destroyed' where id = new.batch_id;
    end if;
  end if;
  perform set_config('hx.internal', '', true);
  return null;
end $$;

notify pgrst, 'reload schema';
