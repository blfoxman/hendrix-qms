-- =====================================================================
-- Hendrix QMS  -  Step 24: Equipment register and Chemical register (SDS)
-- Equipment (CSQ 2A.2.1 equipment, 2A.2.2 maintenance, 2A.2.3 calibration,
-- 5.1.7 validation, 3A.1.4 cultivation equipment, 3B.1.1-3B.1.2 extraction):
--   * every piece of equipment and instrument per license: number EQ-###,
--     category, location, make / model / serial / asset tag, product contact,
--     critical to safety or quality, status (in service / out of service / retired)
--   * master preventive maintenance schedule: interval and the manufacturer's
--     tasks; the work itself is recorded in the Equipment Maintenance Log
--     (Facility Logs, also on the kiosk) - the register picks it up
--   * calibration: interval, method, reference standard (NIST / ASTM),
--     protection from adjustment; each calibration with its certificate and
--     the next due date; a failed calibration takes it out of service
--   * validation IQ / OQ / PQ with yearly revalidation
--   * temporary repairs with a fix-by date until made permanent
--   * out of service / back in service (tools, lubricants and debris removed,
--     cleaned, checked working)
-- Chemicals (CSQ 2A.9.2 chemical controls, 2A.5.1 pest control chemicals):
--   * approved chemical list per license: number CHEM-###, purpose, food grade
--     or not, SDS on file (required to approve), storage area, restricted,
--     hazards, PPE, first aid, spill response, disposal, EPA registration for
--     pesticides; approval by Full access; removal with a reason
-- Access modules 'equipment' and 'chemicals': View / Edit (add, record) /
--   Full (retire, approve chemicals, remove, void events).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-23.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_next_seq(p_table text, p_lic text, p_prefix text) returns text
language plpgsql security definer set search_path = public as $$
declare v_max int;
begin
  perform pg_advisory_xact_lock(hashtext(p_table || p_lic));
  execute format('select coalesce(max((regexp_match(number, %L))[1]::int), 0) from %I where license_id = $1',
                 '^' || p_prefix || '-(\d+)$', p_table) into v_max using p_lic;
  return p_prefix || '-' || lpad((v_max + 1)::text, 3, '0');
end $$;

-- ---------- equipment ----------
create table if not exists hx_equipment (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  name             text not null check (length(trim(name)) > 0),
  category         text not null default 'Production',
  location         text not null default '',
  make             text not null default '',
  model            text not null default '',
  serial           text not null default '',
  asset_tag        text not null default '',
  product_contact  boolean not null default false,
  critical         boolean not null default false,
  status           text not null default 'in_service' check (status in ('in_service','out_of_service','retired')),
  installed_on     date,
  controls_note    text not null default '',
  pm_interval_days int check (pm_interval_days is null or pm_interval_days > 0),
  pm_tasks         text not null default '',
  cal_required     boolean not null default false,
  cal_interval_months int check (cal_interval_months is null or cal_interval_months > 0),
  cal_method       text not null default '',
  cal_standard     text not null default '',
  cal_protection   text not null default '',
  cal_last         date,
  cal_due          date,
  val_required     boolean not null default false,
  iq_on            date,
  oq_on            date,
  pq_on            date,
  reval_due        date,
  log_item_id      text,
  files            jsonb not null default '[]'::jsonb,
  notes            text not null default '',
  retired_reason   text,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_equipment_number on hx_equipment(license_id, number);
create index if not exists hx_equipment_lic on hx_equipment(license_id, status);

create table if not exists hx_equipment_events (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  equipment_id  text not null references hx_equipment(id),
  kind          text not null check (kind in ('calibration','validation','temporary_repair','out_of_service','return_to_service','note')),
  done_on       date not null default current_date,
  done_by       text not null default '',
  details       text not null default '',
  result        text not null default '' check (result in ('','pass','fail')),
  stage         text not null default '' check (stage in ('','IQ','OQ','PQ','Revalidation')),
  standard      text not null default '',
  next_due      date,
  fix_by        date,
  closed_on     date,
  closed_by     text not null default '',
  closure       text not null default '',
  checks        jsonb not null default '{}'::jsonb,
  deviation_id  text,
  files         jsonb not null default '[]'::jsonb,
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_equipment_events_eq on hx_equipment_events(equipment_id, done_on desc);

create or replace function hx_equipment_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_equipment_events where equipment_id = old.id) then
      raise exception 'This equipment has calibration, validation or service records. Retire it instead of deleting it.';
    end if;
    if not hx_can('equipment', 3, old.license_id) then raise exception 'Only Full access can delete equipment.'; end if;
    return old;
  end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_equipment', new.license_id, 'EQ');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now();
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  if coalesce(current_setting('hx.internal', true), '') <> 'on' then
    if new.status = 'retired' and (tg_op = 'INSERT' or old.status <> 'retired') then
      if not hx_can('equipment', 3, new.license_id) then raise exception 'Only Full access can retire equipment.'; end if;
      if coalesce(trim(new.retired_reason), '') = '' then raise exception 'Give a reason for retiring this equipment.'; end if;
      perform set_config('hx.reason', 'Retired: ' || trim(new.retired_reason), true);
    end if;
    if tg_op = 'UPDATE' and old.status = 'retired' and new.status <> 'retired' and not hx_can('equipment', 3, new.license_id) then
      raise exception 'Only Full access can bring retired equipment back.';
    end if;
    -- status, calibration and validation dates come from the recorded events
    if tg_op = 'UPDATE' and (new.status in ('in_service','out_of_service') and old.status in ('in_service','out_of_service') and new.status <> old.status) then
      raise exception 'Use "Out of service" / "Back in service" so the reason and checks are recorded.';
    end if;
    if tg_op = 'UPDATE' and (new.cal_last, new.cal_due, new.iq_on, new.oq_on, new.pq_on, new.reval_due) is distinct from (old.cal_last, old.cal_due, old.iq_on, old.oq_on, old.pq_on, old.reval_due) then
      raise exception 'Calibration and validation dates come from the recorded calibrations and validations.';
    end if;
  end if;
  if new.cal_required and new.cal_interval_months is null then raise exception 'Enter how often it is calibrated (months).'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_equipment_guard on hx_equipment;
create trigger hx_equipment_guard before insert or update or delete on hx_equipment for each row execute function hx_equipment_guard();
drop trigger if exists hx_equipment_place on hx_equipment;
create trigger hx_equipment_place before insert or update on hx_equipment for each row execute function hx_fl_guard();
drop trigger if exists hx_equipment_audit on hx_equipment;
create trigger hx_equipment_audit after insert or update or delete on hx_equipment for each row execute function hx_audit();

create or replace function hx_equipment_event_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare e record; v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then raise exception 'Equipment records are never deleted. Void the record with a reason.'; end if;
  select * into e from hx_equipment where id = coalesce(new.equipment_id, old.equipment_id);
  if e.id is null then raise exception 'Unknown equipment.'; end if;
  if tg_op = 'INSERT' then
    if e.license_id <> new.license_id then raise exception 'That equipment belongs to another license.'; end if;
    if e.status = 'retired' then raise exception 'This equipment is retired.'; end if;
    if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
    new.recorded_by := v_me; new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
    new.closed_on := null; new.closed_by := ''; new.closure := '';
    if new.kind = 'calibration' then
      if new.result = '' then raise exception 'Record the calibration result (pass or fail).'; end if;
      if jsonb_array_length(new.files) = 0 and coalesce(trim(new.standard), '') = '' then
        raise exception 'Attach the calibration certificate or name the reference standard used (e.g. NIST-traceable weights).';
      end if;
      if new.result = 'pass' and new.next_due is null then
        new.next_due := case when e.cal_interval_months is not null then (new.done_on + make_interval(months => e.cal_interval_months))::date end;
        if new.next_due is null then raise exception 'Enter the next calibration due date.'; end if;
      end if;
    elsif new.kind = 'validation' then
      if new.stage = '' then raise exception 'Choose IQ, OQ, PQ or revalidation.'; end if;
      if new.result = '' then raise exception 'Record the validation result (pass or fail).'; end if;
    elsif new.kind = 'temporary_repair' then
      if coalesce(trim(new.details), '') = '' then raise exception 'Describe the temporary repair.'; end if;
      if new.fix_by is null then raise exception 'Set the date the permanent repair must be done by.'; end if;
    elsif new.kind = 'out_of_service' then
      if coalesce(trim(new.details), '') = '' then raise exception 'Say why it is out of service.'; end if;
      if e.status <> 'in_service' then raise exception 'It is already out of service.'; end if;
    elsif new.kind = 'return_to_service' then
      if e.status <> 'out_of_service' then raise exception 'It is not out of service.'; end if;
      if coalesce((new.checks->>'cleared')::boolean, false) is not true or coalesce((new.checks->>'cleaned')::boolean, false) is not true
         or coalesce((new.checks->>'working')::boolean, false) is not true then
        raise exception 'Confirm tools, lubricants and debris are removed, the equipment is cleaned and sanitized, and it was checked working.';
      end if;
      if e.cal_required and (e.cal_due is null or e.cal_due < current_date) then raise exception 'The calibration is out of date. Record a calibration first.'; end if;
    end if;
    return new;
  end if;
  -- updates: close a temporary repair, add files, or void
  if old.voided then raise exception 'This record is void.'; end if;
  if new.voided then
    if not hx_can('equipment', 3, old.license_id) then raise exception 'Only Full access can void an equipment record.'; end if;
    if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
    new.voided_at := now();
    perform set_config('hx.reason', trim(new.void_reason), true);
    return new;
  end if;
  if (to_jsonb(new) - 'files' - 'closed_on' - 'closed_by' - 'closure' - 'deviation_id') is distinct from (to_jsonb(old) - 'files' - 'closed_on' - 'closed_by' - 'closure' - 'deviation_id') then
    raise exception 'An equipment record cannot be changed. Void it and record it again.';
  end if;
  if new.closed_on is not null and old.closed_on is null then
    if old.kind <> 'temporary_repair' then raise exception 'Only temporary repairs are closed.'; end if;
    if coalesce(trim(new.closure), '') = '' then raise exception 'Describe the permanent repair.'; end if;
    new.closed_by := v_me;
    perform set_config('hx.reason', 'Temporary repair made permanent', true);
  elsif old.closed_on is not null and new.closed_on is distinct from old.closed_on then
    raise exception 'This repair is already closed.';
  end if;
  return new;
end $$;
drop trigger if exists hx_equipment_events_guard on hx_equipment_events;
create trigger hx_equipment_events_guard before insert or update or delete on hx_equipment_events for each row execute function hx_equipment_event_guard();
drop trigger if exists hx_equipment_events_place on hx_equipment_events;
create trigger hx_equipment_events_place before insert or update on hx_equipment_events for each row execute function hx_fl_guard();
drop trigger if exists hx_equipment_events_audit on hx_equipment_events;
create trigger hx_equipment_events_audit after insert or update on hx_equipment_events for each row execute function hx_audit();

-- the equipment's status, calibration and validation dates follow its events
create or replace function hx_equipment_event_apply() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_id text := new.equipment_id; c record; v_why text;
begin
  v_why := case new.kind when 'calibration' then 'Calibration ' || coalesce(nullif(new.result,''),'recorded') when 'validation' then new.stage || ' ' || coalesce(nullif(new.result,''),'recorded')
    when 'out_of_service' then 'Out of service: ' || new.details when 'return_to_service' then 'Back in service' when 'temporary_repair' then 'Temporary repair' else 'Equipment record' end
    || case when new.voided then ' (record voided)' else '' end;
  perform set_config('hx.internal', 'on', true);
  select done_on, next_due into c from hx_equipment_events
   where equipment_id = v_id and kind = 'calibration' and result = 'pass' and not voided order by done_on desc, created_at desc limit 1;
  perform set_config('hx.reason', v_why, true);
  update hx_equipment set cal_last = c.done_on, cal_due = c.next_due,
     iq_on = (select max(done_on) from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage = 'IQ' and result = 'pass' and not voided),
     oq_on = (select max(done_on) from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage = 'OQ' and result = 'pass' and not voided),
     pq_on = (select max(done_on) from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage in ('PQ','Revalidation') and result = 'pass' and not voided),
     reval_due = (select (max(done_on) + interval '1 year')::date from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage in ('PQ','Revalidation') and result = 'pass' and not voided)
   where id = v_id;
  if tg_op = 'INSERT' and not new.voided then
    perform set_config('hx.reason', v_why, true);
    if new.kind = 'out_of_service' or (new.kind in ('calibration','validation') and new.result = 'fail') then
      update hx_equipment set status = 'out_of_service' where id = v_id and status = 'in_service';
    elsif new.kind = 'return_to_service' then
      update hx_equipment set status = 'in_service' where id = v_id and status = 'out_of_service';
    end if;
  end if;
  perform set_config('hx.internal', '', true);
  return null;
end $$;
drop trigger if exists hx_equipment_events_zapply on hx_equipment_events;
create trigger hx_equipment_events_zapply after insert or update on hx_equipment_events for each row execute function hx_equipment_event_apply();

-- ---------- chemicals ----------
create table if not exists hx_chemicals (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  name             text not null check (length(trim(name)) > 0),
  manufacturer     text not null default '',
  product_code     text not null default '',
  purpose          text not null default 'Cleaner',
  grade            text not null default 'non_food' check (grade in ('food_grade','food_contact_sanitizer','non_food')),
  status           text not null default 'pending' check (status in ('pending','approved','removed')),
  sds_files        jsonb not null default '[]'::jsonb,
  sds_date         date,
  hazards          text not null default '',
  ppe              text not null default '',
  first_aid        text not null default '',
  spill            text not null default '',
  storage_area     text not null default '',
  restricted       boolean not null default false,
  disposal         text not null default '',
  epa_reg          text not null default '',
  supplier_id      text,
  notes            text not null default '',
  approved_by      text not null default '',
  approved_at      timestamptz,
  removed_reason   text,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_chemicals_number on hx_chemicals(license_id, number);

create or replace function hx_chemical_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if old.status <> 'pending' then raise exception 'An approved chemical is never deleted. Remove it from use with a reason.'; end if;
    return old;
  end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_chemicals', new.license_id, 'CHEM');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now();
    if new.status <> 'pending' and not hx_can('chemicals', 3, new.license_id) then new.status := 'pending'; end if;
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  if new.status = 'approved' then
    if tg_op = 'INSERT' or old.status <> 'approved' then
      if not hx_can('chemicals', 3, new.license_id) then raise exception 'Only Full access can approve a chemical.'; end if;
      new.approved_by := coalesce(hx_me(), ''); new.approved_at := now();
      perform set_config('hx.reason', 'Chemical approved for use', true);
    else
      new.approved_by := old.approved_by; new.approved_at := old.approved_at;
    end if;
    if jsonb_array_length(new.sds_files) = 0 then raise exception 'Attach the Safety Data Sheet (SDS) before approving.'; end if;
    if coalesce(trim(new.storage_area), '') = '' then raise exception 'Enter where it is stored.'; end if;
    if coalesce(trim(new.ppe), '') = '' then raise exception 'Enter the PPE needed (from the SDS).'; end if;
    if new.purpose = 'Pesticide / crop protection' and coalesce(trim(new.epa_reg), '') = '' then raise exception 'Enter the EPA registration number of the pesticide.'; end if;
  elsif new.status = 'removed' then
    if tg_op = 'INSERT' or old.status <> 'removed' then
      if not hx_can('chemicals', 3, new.license_id) then raise exception 'Only Full access can remove a chemical from use.'; end if;
      if coalesce(trim(new.removed_reason), '') = '' then raise exception 'Give a reason for removing this chemical.'; end if;
      perform set_config('hx.reason', 'Removed from use: ' || trim(new.removed_reason), true);
    end if;
  else
    if tg_op = 'UPDATE' and old.status <> 'pending' and not hx_can('chemicals', 3, new.license_id) then raise exception 'Only Full access can change the status.'; end if;
    new.approved_by := ''; new.approved_at := null;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_chemicals_guard on hx_chemicals;
create trigger hx_chemicals_guard before insert or update or delete on hx_chemicals for each row execute function hx_chemical_guard();
drop trigger if exists hx_chemicals_place on hx_chemicals;
create trigger hx_chemicals_place before insert or update on hx_chemicals for each row execute function hx_fl_guard();
drop trigger if exists hx_chemicals_audit on hx_chemicals;
create trigger hx_chemicals_audit after insert or update or delete on hx_chemicals for each row execute function hx_audit();

-- ---------- access ----------
alter table hx_equipment enable row level security;
alter table hx_equipment_events enable row level security;
alter table hx_chemicals enable row level security;
drop policy if exists hx_equipment_read on hx_equipment;
drop policy if exists hx_equipment_insert on hx_equipment;
drop policy if exists hx_equipment_update on hx_equipment;
drop policy if exists hx_equipment_delete on hx_equipment;
create policy hx_equipment_read   on hx_equipment for select to authenticated using (hx_can('equipment',1,license_id));
create policy hx_equipment_insert on hx_equipment for insert to authenticated with check (hx_can('equipment',2,license_id));
create policy hx_equipment_update on hx_equipment for update to authenticated using (hx_can('equipment',2,license_id)) with check (hx_can('equipment',2,license_id));
create policy hx_equipment_delete on hx_equipment for delete to authenticated using (hx_can('equipment',3,license_id));
drop policy if exists hx_equipment_events_read on hx_equipment_events;
drop policy if exists hx_equipment_events_insert on hx_equipment_events;
drop policy if exists hx_equipment_events_update on hx_equipment_events;
create policy hx_equipment_events_read   on hx_equipment_events for select to authenticated using (hx_can('equipment',1,license_id));
create policy hx_equipment_events_insert on hx_equipment_events for insert to authenticated with check (hx_can('equipment',2,license_id));
create policy hx_equipment_events_update on hx_equipment_events for update to authenticated using (hx_can('equipment',2,license_id)) with check (hx_can('equipment',2,license_id));
drop policy if exists hx_chemicals_read on hx_chemicals;
drop policy if exists hx_chemicals_insert on hx_chemicals;
drop policy if exists hx_chemicals_update on hx_chemicals;
drop policy if exists hx_chemicals_delete on hx_chemicals;
create policy hx_chemicals_read   on hx_chemicals for select to authenticated using (hx_can('chemicals',1,license_id));
create policy hx_chemicals_insert on hx_chemicals for insert to authenticated with check (hx_can('chemicals',2,license_id));
create policy hx_chemicals_update on hx_chemicals for update to authenticated using (hx_can('chemicals',2,license_id)) with check (hx_can('chemicals',2,license_id));
create policy hx_chemicals_delete on hx_chemicals for delete to authenticated using (hx_can('chemicals',3,license_id));
grant select, insert, update, delete on hx_equipment, hx_chemicals to authenticated;
grant select, insert, update on hx_equipment_events to authenticated;

notify pgrst, 'reload schema';
