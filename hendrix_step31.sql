-- =====================================================================
-- Hendrix QMS  -  Step 31: Management review and Verification schedule (CSQ Level 3)
-- Management review (CSQ 5.1.3):
--   * numbered MR-YYYY-###; the period reviewed, chair (senior management),
--     attendees; every input with the facts (filled from Hendrix records)
--     and the discussion: actions from the last review, complaints and
--     feedback, internal / external / regulatory audits, deviations and
--     CAPAs, risks, HACCP, quality objectives / KPIs, CSQ conformance,
--     changes, suppliers, training, resources
--   * decisions, resource needs, actions (what, who, due, done), the next
--     review date (within 12 months), who the minutes were shared with
--   * "held" (signed) by Full access only when the required inputs were
--     discussed; after that the minutes are frozen - only actions can be
--     ticked done and the sharing recorded
-- Verification schedule (CSQ 5.1.8):
--   * VS-###: the activity verified, how, who, how often, and where it is
--     recorded; many are linked to Hendrix records (sanitation log
--     verification, CCP record review, HACCP verification, calibration,
--     internal audits, facility tests, risk reviews, KPI reviews,
--     management review, supplier reviews) so the last date is automatic
--   * hx_verification_records: each verification done by hand, with the
--     result; issues need the action taken; never deleted (void with reason)
-- Access modules 'mgmtreview' and 'verification': View / Edit / Full.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-30.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_mgmt_reviews (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  number        text not null default '',
  meeting_date  date not null default current_date,
  period_from   date,
  period_to     date,
  chair         text not null default '',
  attendees     text not null default '',
  inputs        jsonb not null default '{}'::jsonb,
  decisions     text not null default '',
  resources     text not null default '',
  actions       jsonb not null default '[]'::jsonb,
  next_review   date,
  shared_with   text not null default '',
  shared_on     date,
  status        text not null default 'draft' check (status in ('draft','held','cancelled')),
  signed_by     text not null default '',
  signed_at     timestamptz,
  cancel_reason text,
  files         jsonb not null default '[]'::jsonb,
  created_by    text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists hx_mgmt_reviews_number on hx_mgmt_reviews(license_id, number);

create or replace function hx_mgmt_review_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v_miss text := '';
begin
  if tg_op = 'DELETE' then raise exception 'Management reviews are never deleted. Cancel a draft with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_mgmt_reviews', new.license_id, 'MR');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.status := 'draft'; new.signed_by := ''; new.signed_at := null; new.cancel_reason := null;
    perform set_config('hx.reason', 'Management review started', true);
    new.updated_at := now(); return new;
  end if;
  new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  if old.status = 'cancelled' then raise exception 'This management review was cancelled.'; end if;
  if old.status = 'held' then
    if new.status <> 'held' then raise exception 'A held management review cannot be cancelled or reopened.'; end if;
    if (to_jsonb(new) - 'actions' - 'shared_with' - 'shared_on' - 'files' - 'updated_at') is distinct from (to_jsonb(old) - 'actions' - 'shared_with' - 'shared_on' - 'files' - 'updated_at') then
      raise exception 'The minutes are signed. Only actions, sharing and files can be updated.';
    end if;
    if jsonb_array_length(coalesce(new.actions, '[]'::jsonb)) <> jsonb_array_length(coalesce(old.actions, '[]'::jsonb)) then
      raise exception 'Actions decided in the review cannot be added or removed after it is signed.';
    end if;
    if new.shared_on is not null and new.shared_on > current_date then raise exception 'The sharing date cannot be in the future.'; end if;
    perform set_config('hx.reason', case when new.shared_on is distinct from old.shared_on then 'Minutes shared' else 'Review actions updated' end, true);
    new.updated_at := now(); return new;
  end if;
  if new.status = 'cancelled' then
    if not hx_can('mgmtreview', 3, new.license_id) then raise exception 'Only Full access can cancel a management review.'; end if;
    if coalesce(trim(new.cancel_reason), '') = '' then raise exception 'A reason is required.'; end if;
    perform set_config('hx.reason', 'Management review cancelled: ' || trim(new.cancel_reason), true);
  elsif new.status = 'held' then
    if not hx_can('mgmtreview', 3, new.license_id) then raise exception 'Only Full access (senior management) can sign the management review.'; end if;
    if new.meeting_date > current_date then raise exception 'The meeting date cannot be in the future.'; end if;
    if coalesce(trim(new.chair), '') = '' or coalesce(trim(new.attendees), '') = '' then raise exception 'Enter the chair and who attended.'; end if;
    foreach k in array array['prev_actions','complaints','audits','deviations','risks','csq','changes','resources'] loop
      if coalesce(trim(new.inputs->k->>'notes'), '') = '' then v_miss := v_miss || k || ' '; end if;
    end loop;
    if v_miss <> '' then raise exception 'Discuss every required input before signing (missing: %).', trim(v_miss); end if;
    if coalesce(trim(new.decisions), '') = '' then raise exception 'Record the decisions and conclusions.'; end if;
    if new.next_review is null or new.next_review <= new.meeting_date or new.next_review > new.meeting_date + 366 then
      raise exception 'Set the next review within 12 months of this one.';
    end if;
    new.signed_by := coalesce(hx_me(), ''); new.signed_at := now();
    perform set_config('hx.reason', 'Management review held and signed', true);
  else
    perform set_config('hx.reason', 'Management review draft updated', true);
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_mgmt_reviews_guard on hx_mgmt_reviews;
create trigger hx_mgmt_reviews_guard before insert or update or delete on hx_mgmt_reviews for each row execute function hx_mgmt_review_guard();
drop trigger if exists hx_mgmt_reviews_place on hx_mgmt_reviews;
create trigger hx_mgmt_reviews_place before insert or update on hx_mgmt_reviews for each row execute function hx_fl_guard();
drop trigger if exists hx_mgmt_reviews_audit on hx_mgmt_reviews;
create trigger hx_mgmt_reviews_audit after insert or update on hx_mgmt_reviews for each row execute function hx_audit();

create table if not exists hx_verification_plan (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  number          text not null default '',
  activity        text not null check (length(trim(activity)) > 0),
  method          text not null default '',
  responsible     text not null default '',
  frequency_days  int  not null default 30 check (frequency_days between 1 and 1095),
  source          text not null default 'manual',
  record_where    text not null default '',
  clause          text not null default '',
  active          boolean not null default true,
  created_by      text not null default '',
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_verification_plan_number on hx_verification_plan(license_id, number);

create or replace function hx_verification_plan_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Verification activities are never deleted. Turn the activity off instead.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_verification_plan', new.license_id, 'VS'); new.created_by := coalesce(hx_me(), ''); new.created_at := now();
    perform set_config('hx.reason', 'Verification activity added', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if new.active is distinct from old.active and not new.active and not hx_can('verification', 3, new.license_id) then raise exception 'Only Full access can turn a verification activity off.'; end if;
    perform set_config('hx.reason', case when new.active is distinct from old.active then (case when new.active then 'Verification activity turned on' else 'Verification activity turned off' end) else 'Verification activity updated' end, true);
  end if;
  if coalesce(trim(new.responsible), '') = '' then raise exception 'Enter who does the verification.'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_verification_plan_guard on hx_verification_plan;
create trigger hx_verification_plan_guard before insert or update or delete on hx_verification_plan for each row execute function hx_verification_plan_guard();
drop trigger if exists hx_verification_plan_place on hx_verification_plan;
create trigger hx_verification_plan_place before insert or update on hx_verification_plan for each row execute function hx_fl_guard();
drop trigger if exists hx_verification_plan_audit on hx_verification_plan;
create trigger hx_verification_plan_audit after insert or update on hx_verification_plan for each row execute function hx_audit();

create table if not exists hx_verification_records (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  plan_id       text not null references hx_verification_plan(id),
  done_on       date not null default current_date,
  done_by       text not null default '',
  result        text not null default 'ok' check (result in ('ok','issues')),
  findings      text not null default '',
  action        text not null default '',
  deviation_id  text,
  files         jsonb not null default '[]'::jsonb,
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_verification_records_plan on hx_verification_records(plan_id);

create or replace function hx_verification_record_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Verification records are never deleted. Void it with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('verification', 3, old.license_id) then raise exception 'Only Full access can void a verification record.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a record without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true); return new;
    end if;
    if (to_jsonb(new) - 'deviation_id' - 'files') is distinct from (to_jsonb(old) - 'deviation_id' - 'files') then raise exception 'A verification record cannot be changed. Void it and record it again.'; end if;
    return new;
  end if;
  if not exists (select 1 from hx_verification_plan where id = new.plan_id and license_id = new.license_id) then raise exception 'That activity belongs to another license.'; end if;
  if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
  if coalesce(trim(new.done_by), '') = '' then raise exception 'Enter who did the verification.'; end if;
  if new.result = 'issues' and (coalesce(trim(new.findings), '') = '' or coalesce(trim(new.action), '') = '') then raise exception 'Describe the issues found and the action taken.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  perform set_config('hx.reason', case when new.result = 'ok' then 'Verified - no issues' else 'Verified - issues found' end, true);
  return new;
end $$;
drop trigger if exists hx_verification_records_guard on hx_verification_records;
create trigger hx_verification_records_guard before insert or update or delete on hx_verification_records for each row execute function hx_verification_record_guard();
drop trigger if exists hx_verification_records_place on hx_verification_records;
create trigger hx_verification_records_place before insert or update on hx_verification_records for each row execute function hx_fl_guard();
drop trigger if exists hx_verification_records_audit on hx_verification_records;
create trigger hx_verification_records_audit after insert or update on hx_verification_records for each row execute function hx_audit();

-- deviations can be raised from a verification with issues
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment','facility_test','haccp','verification'));

alter table hx_mgmt_reviews enable row level security;
alter table hx_verification_plan enable row level security;
alter table hx_verification_records enable row level security;
drop policy if exists hx_mgmt_reviews_read on hx_mgmt_reviews;
drop policy if exists hx_mgmt_reviews_insert on hx_mgmt_reviews;
drop policy if exists hx_mgmt_reviews_update on hx_mgmt_reviews;
create policy hx_mgmt_reviews_read   on hx_mgmt_reviews for select to authenticated using (hx_can('mgmtreview',1,license_id));
create policy hx_mgmt_reviews_insert on hx_mgmt_reviews for insert to authenticated with check (hx_can('mgmtreview',2,license_id));
create policy hx_mgmt_reviews_update on hx_mgmt_reviews for update to authenticated using (hx_can('mgmtreview',2,license_id)) with check (hx_can('mgmtreview',2,license_id));
drop policy if exists hx_verification_plan_read on hx_verification_plan;
drop policy if exists hx_verification_plan_insert on hx_verification_plan;
drop policy if exists hx_verification_plan_update on hx_verification_plan;
create policy hx_verification_plan_read   on hx_verification_plan for select to authenticated using (hx_can('verification',1,license_id));
create policy hx_verification_plan_insert on hx_verification_plan for insert to authenticated with check (hx_can('verification',2,license_id));
create policy hx_verification_plan_update on hx_verification_plan for update to authenticated using (hx_can('verification',2,license_id)) with check (hx_can('verification',2,license_id));
drop policy if exists hx_verification_records_read on hx_verification_records;
drop policy if exists hx_verification_records_insert on hx_verification_records;
drop policy if exists hx_verification_records_update on hx_verification_records;
create policy hx_verification_records_read   on hx_verification_records for select to authenticated using (hx_can('verification',1,license_id));
create policy hx_verification_records_insert on hx_verification_records for insert to authenticated with check (hx_can('verification',2,license_id));
create policy hx_verification_records_update on hx_verification_records for update to authenticated using (hx_can('verification',2,license_id)) with check (hx_can('verification',2,license_id));
grant select, insert, update on hx_mgmt_reviews, hx_verification_plan, hx_verification_records to authenticated;

notify pgrst, 'reload schema';
