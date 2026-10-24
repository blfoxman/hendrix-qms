-- =====================================================================
-- Hendrix QMS  -  Step 28: HACCP (CSQ Module 4A, Level 2)
-- The 12 Codex steps, kept live per license:
--   * HACCP team (4A.2): members, role, department; one person and a backup
--     certified (International HACCP Alliance) - certificates come from the
--     Training records (HACCP course) or are attached here
--   * HACCP plans per product / process (4A.1, 4A.3-4A.7): product description
--     (name, safety characteristics, ingredients, allergens, packaging,
--     intended use, target market, shelf life, labeling, storage /
--     distribution), the process flow (inputs, steps, rework, outsourced,
--     end products, waste) with the CCPs marked, the hazard analysis for
--     every step (biological, chemical, physical, allergen: cause, control,
--     significant or not), and the CCPs with critical limits, monitoring,
--     corrective action and verification
--   * a plan becomes active only when it is complete and validated (4A.10),
--     approved by Full access; revising it starts a new version
--   * CCP monitoring records (4A.8, 4A.9): value, within limits or not; a
--     deviation needs the corrective action and what happened to the product;
--     records reviewed (verified) by a second person
--   * verification (4A.11): records review, yearly reanalysis, validation,
--     calibration checks - with findings and files
-- Access module 'haccp': View / Edit (monitoring, drafts, verification) /
--   Full (validate, activate, retire plans, void records).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-27.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_haccp_team (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  name          text not null check (length(trim(name)) > 0),
  user_id       text,
  role          text not null default 'Member' check (role in ('Team leader','Backup','Member')),
  department    text not null default '',
  certified     boolean not null default false,
  cert_provider text not null default '',
  cert_date     date,
  cert_files    jsonb not null default '[]'::jsonb,
  active        boolean not null default true,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table if not exists hx_haccp_plans (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  number          text not null default '',
  name            text not null check (length(trim(name)) > 0),
  batch_types     text[] not null default '{}',
  description     jsonb not null default '{}'::jsonb,
  flow            jsonb not null default '[]'::jsonb,
  hazards         jsonb not null default '[]'::jsonb,
  ccps            jsonb not null default '[]'::jsonb,
  status          text not null default 'draft' check (status in ('draft','validated','active','retired')),
  version         int not null default 0,
  validated_on    date,
  validation      text not null default '',
  validation_files jsonb not null default '[]'::jsonb,
  validated_by    text not null default '',
  approved_by     text not null default '',
  approved_at     timestamptz,
  flow_reviewed_on date,
  retired_reason  text,
  created_by      text not null default '',
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_haccp_plans_number on hx_haccp_plans(license_id, number);

create table if not exists hx_haccp_monitoring (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  plan_id       text not null references hx_haccp_plans(id),
  plan_version  int not null default 0,
  ccp_id        text not null,
  ccp_name      text not null default '',
  batch_id      text references hx_batches(id),
  checked_at    timestamptz not null default now(),
  checked_by    text not null default '',
  value         text not null default '',
  within_limits boolean not null,
  corrective    text not null default '',
  disposition   text not null default '' check (disposition in ('','held','reworked','destroyed','released_after_evaluation')),
  deviation_id  text,
  verified_by   text not null default '',
  verified_at   timestamptz,
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_haccp_monitoring_plan on hx_haccp_monitoring(plan_id, checked_at desc);
create index if not exists hx_haccp_monitoring_batch on hx_haccp_monitoring(batch_id);

create table if not exists hx_haccp_verifications (
  id          text primary key,
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  plan_id     text references hx_haccp_plans(id),
  kind        text not null check (kind in ('records_review','reanalysis','validation','calibration','other')),
  done_on     date not null default current_date,
  done_by     text not null default '',
  findings    text not null default '',
  result      text not null default 'ok' check (result in ('ok','changes_needed')),
  files       jsonb not null default '[]'::jsonb,
  recorded_by text not null default '',
  created_at  timestamptz not null default now(),
  voided      boolean not null default false,
  void_reason text,
  voided_at   timestamptz
);

-- plans: complete and validated before they go live; active plans are frozen
create or replace function hx_haccp_plan_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare st jsonb; c jsonb; h jsonb; n int; v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then
    if old.status <> 'draft' or old.version > 0 or exists (select 1 from hx_haccp_monitoring where plan_id = old.id) then
      raise exception 'Only a never-used draft can be deleted. Retire the plan instead.';
    end if;
    return old;
  end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_haccp_plans', new.license_id, 'HP');
    new.created_by := v_me; new.created_at := now(); new.status := 'draft'; new.version := 0;
    new.approved_by := ''; new.approved_at := null; new.validated_on := null; new.validated_by := '';
    new.updated_at := now();
    return new;
  end if;
  new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  if old.status in ('active','retired') and new.status = old.status
     and (new.name, new.batch_types, new.description, new.flow, new.hazards, new.ccps, new.validation, new.validation_files)
         is distinct from (old.name, old.batch_types, old.description, old.flow, old.hazards, old.ccps, old.validation, old.validation_files) then
    raise exception 'An active plan cannot be edited. Click "Revise" to start a new version.';
  end if;
  if new.status = 'retired' and old.status <> 'retired' then
    if not hx_can('haccp', 3, new.license_id) then raise exception 'Only Full access can retire a HACCP plan.'; end if;
    if coalesce(trim(new.retired_reason), '') = '' then raise exception 'Give a reason for retiring the plan.'; end if;
    perform set_config('hx.reason', 'HACCP plan retired: ' || trim(new.retired_reason), true);
  elsif new.status = 'draft' and old.status = 'active' then
    if not hx_can('haccp', 3, new.license_id) then raise exception 'Only Full access can revise an active plan.'; end if;
    new.validated_on := null; new.validated_by := ''; new.validation := ''; new.validation_files := '[]'::jsonb;
    perform set_config('hx.reason', 'HACCP plan revision started (was version ' || old.version || ')', true);
  elsif new.status in ('validated','active') and old.status not in ('validated','active') or (new.status = 'active' and old.status = 'validated') then
    if not hx_can('haccp', 3, new.license_id) then raise exception 'Only Full access can validate or activate a HACCP plan.'; end if;
    -- completeness (Codex steps 1-10)
    if coalesce(trim(new.description->>'intended_use'), '') = '' or coalesce(trim(new.description->>'ingredients'), '') = '' or coalesce(trim(new.description->>'allergens'), '') = ''
       or coalesce(trim(new.description->>'packaging'), '') = '' or coalesce(trim(new.description->>'storage'), '') = '' then
      raise exception 'Complete the product description (ingredients, allergens, packaging, intended use, storage and distribution).';
    end if;
    if jsonb_array_length(new.flow) < 2 then raise exception 'Draw the process flow (at least the inputs and the steps).'; end if;
    for st in select * from jsonb_array_elements(new.flow) loop
      if coalesce((st->>'nohazard')::boolean, false) is not true and not exists (select 1 from jsonb_array_elements(new.hazards) x where x->>'step' = st->>'id') then
        raise exception 'Step "%" has no hazard analysis. Add its hazards or mark it "no hazards reasonably expected".', st->>'name';
      end if;
    end loop;
    for h in select * from jsonb_array_elements(new.hazards) loop
      if coalesce(trim(h->>'control'), '') = '' then raise exception 'Hazard "%" needs its control measure.', h->>'hazard'; end if;
    end loop;
    select count(*) into n from jsonb_array_elements(new.ccps);
    if n = 0 and exists (select 1 from jsonb_array_elements(new.hazards) x where coalesce((x->>'significant')::boolean, false)) then
      raise exception 'Significant hazards need a Critical Control Point (or a documented reason they are controlled by prerequisite programs).';
    end if;
    for c in select * from jsonb_array_elements(new.ccps) loop
      if coalesce(trim(c->>'limit'), '') = '' or coalesce(trim(c->>'monitoring'), '') = '' or coalesce(trim(c->>'frequency'), '') = ''
         or coalesce(trim(c->>'corrective'), '') = '' or coalesce(trim(c->>'verification'), '') = '' then
        raise exception 'CCP "%" needs its critical limit, monitoring (what, how, frequency), corrective action and verification.', c->>'name';
      end if;
    end loop;
    if (select count(*) from hx_haccp_team where license_id = new.license_id and active and certified) < 2 then
      raise exception 'The HACCP team needs one person and a backup certified in an International HACCP Alliance course.';
    end if;
    if new.status = 'validated' or old.status <> 'validated' then
      if coalesce(trim(new.validation), '') = '' then raise exception 'Record how the control measures and critical limits were validated (studies, tests, references).'; end if;
      new.validated_on := current_date; new.validated_by := v_me;
    end if;
    if new.status = 'active' then
      new.version := old.version + 1; new.approved_by := v_me; new.approved_at := now(); new.flow_reviewed_on := current_date;
      perform set_config('hx.reason', 'HACCP plan version ' || new.version || ' activated', true);
    else
      perform set_config('hx.reason', 'HACCP plan validated', true);
    end if;
  elsif new.status <> old.status then
    raise exception 'A plan goes draft -> validated -> active (or retired).';
  end if;
  if new.status = 'draft' and old.status = 'validated' and (new.flow, new.hazards, new.ccps) is distinct from (old.flow, old.hazards, old.ccps) then
    new.validated_on := null; new.validated_by := '';
  end if;
  if old.status = 'validated' and new.status = 'validated' and (new.flow, new.hazards, new.ccps, new.description) is distinct from (old.flow, old.hazards, old.ccps, old.description) then
    new.status := 'draft'; new.validated_on := null; new.validated_by := '';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_haccp_plans_guard on hx_haccp_plans;
create trigger hx_haccp_plans_guard before insert or update or delete on hx_haccp_plans for each row execute function hx_haccp_plan_guard();

create or replace function hx_haccp_monitoring_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record; c jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Monitoring records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('haccp', 3, old.license_id) then raise exception 'Only Full access can void a monitoring record.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a record without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'verified_by' - 'verified_at' - 'deviation_id') is distinct from (to_jsonb(old) - 'verified_by' - 'verified_at' - 'deviation_id') then
      raise exception 'A monitoring record cannot be changed. Void it and record it again.';
    end if;
    if new.verified_at is not null and old.verified_at is null then
      new.verified_by := coalesce(hx_me(), ''); new.verified_at := now();
      if new.verified_by = old.checked_by or new.verified_by = old.recorded_by then raise exception 'Records are verified by someone other than the person who did the check.'; end if;
      perform set_config('hx.reason', 'CCP record verified', true);
    elsif old.verified_at is not null and (new.verified_at is distinct from old.verified_at) then
      raise exception 'This record is already verified.';
    end if;
    return new;
  end if;
  select * into p from hx_haccp_plans where id = new.plan_id;
  if p.id is null or p.license_id <> new.license_id then raise exception 'That HACCP plan belongs to another license.'; end if;
  if p.status <> 'active' then raise exception 'Monitoring is recorded against an active HACCP plan.'; end if;
  select x into c from jsonb_array_elements(p.ccps) x where x->>'id' = new.ccp_id;
  if c is null then raise exception 'That CCP is not in the active plan.'; end if;
  if new.batch_id is not null and not exists (select 1 from hx_batches where id = new.batch_id and license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
  if coalesce(trim(new.checked_by), '') = '' then raise exception 'Enter who did the check.'; end if;
  if coalesce(trim(new.value), '') = '' then raise exception 'Enter the measured value.'; end if;
  if not new.within_limits then
    if coalesce(trim(new.corrective), '') = '' then raise exception 'Out of the critical limit: record the corrective action.'; end if;
    if new.disposition = '' then raise exception 'Out of the critical limit: record what happened to the product (held, reworked, destroyed, released after evaluation).'; end if;
  end if;
  new.plan_version := p.version; new.ccp_name := coalesce(c->>'name', '');
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.verified_by := ''; new.verified_at := null;
  new.voided := false; new.void_reason := null; new.voided_at := null;
  perform set_config('hx.reason', case when new.within_limits then 'CCP within limits' else 'CCP OUT of limits' end, true);
  return new;
end $$;
drop trigger if exists hx_haccp_monitoring_guard on hx_haccp_monitoring;
create trigger hx_haccp_monitoring_guard before insert or update or delete on hx_haccp_monitoring for each row execute function hx_haccp_monitoring_guard();

create or replace function hx_haccp_verification_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Verification records are never deleted. Void it with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('haccp', 3, old.license_id) then raise exception 'Only Full access can void a verification record.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'files') is distinct from (to_jsonb(old) - 'files') then raise exception 'A verification record cannot be changed. Void it and record it again.'; end if;
    return new;
  end if;
  if new.plan_id is not null and not exists (select 1 from hx_haccp_plans where id = new.plan_id and license_id = new.license_id) then raise exception 'That plan belongs to another license.'; end if;
  if coalesce(trim(new.done_by), '') = '' then raise exception 'Enter who did the verification.'; end if;
  if coalesce(trim(new.findings), '') = '' then raise exception 'Record what was checked and found.'; end if;
  if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  if new.kind = 'reanalysis' and new.plan_id is not null then
    perform set_config('hx.internal', 'on', true);
    update hx_haccp_plans set flow_reviewed_on = new.done_on where id = new.plan_id;
    perform set_config('hx.internal', '', true);
  end if;
  return new;
end $$;
drop trigger if exists hx_haccp_verifications_guard on hx_haccp_verifications;
create trigger hx_haccp_verifications_guard before insert or update or delete on hx_haccp_verifications for each row execute function hx_haccp_verification_guard();

do $$ declare t text; begin
  foreach t in array array['hx_haccp_team','hx_haccp_plans','hx_haccp_monitoring','hx_haccp_verifications'] loop
    execute format('drop trigger if exists %I on %I', t||'_place', t);
    execute format('create trigger %I before insert or update on %I for each row execute function hx_fl_guard()', t||'_place', t);
    execute format('drop trigger if exists %I on %I', t||'_audit', t);
    execute format('create trigger %I after insert or update or delete on %I for each row execute function hx_audit()', t||'_audit', t);
    execute format('alter table %I enable row level security', t);
    execute format('drop policy if exists %I on %I', t||'_read', t);
    execute format('drop policy if exists %I on %I', t||'_insert', t);
    execute format('drop policy if exists %I on %I', t||'_update', t);
    execute format('drop policy if exists %I on %I', t||'_delete', t);
    execute format('create policy %I on %I for select to authenticated using (hx_can(''haccp'',1,license_id))', t||'_read', t);
    execute format('create policy %I on %I for insert to authenticated with check (hx_can(''haccp'',2,license_id))', t||'_insert', t);
    execute format('create policy %I on %I for update to authenticated using (hx_can(''haccp'',2,license_id)) with check (hx_can(''haccp'',2,license_id))', t||'_update', t);
    execute format('create policy %I on %I for delete to authenticated using (hx_can(''haccp'',3,license_id))', t||'_delete', t);
  end loop;
end $$;
grant select, insert, update, delete on hx_haccp_team, hx_haccp_plans to authenticated;
grant select, insert, update on hx_haccp_monitoring, hx_haccp_verifications to authenticated;

-- the team table: Full access manages it
create or replace function hx_haccp_team_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not hx_can('haccp', 3, coalesce(new.license_id, old.license_id)) then raise exception 'Only Full access can change the HACCP team.'; end if;
  if tg_op = 'DELETE' then return old; end if;
  if new.certified and new.cert_date is null and jsonb_array_length(new.cert_files) = 0 and coalesce(trim(new.cert_provider), '') = '' then
    raise exception 'Enter the certificate (provider, date or file) for a certified member.';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_haccp_team_guard on hx_haccp_team;
create trigger hx_haccp_team_guard before insert or update or delete on hx_haccp_team for each row execute function hx_haccp_team_guard();

-- deviations can be raised from a CCP out of limits
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment','facility_test','haccp'));

notify pgrst, 'reload schema';
