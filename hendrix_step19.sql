-- =====================================================================
-- Hendrix QMS  -  Step 19: Complaints and Internal Audits (CSQ 1.5, 1.7, 5.3)
-- Complaints (Black Fox / Michigan fields: title, type consumer / dispensary /
-- product return / adverse event, priority, product, lot number, description,
-- resolution, attachments) plus CSQ complaint management:
--   * numbered (CMP-YYYY-###), received date and channel, complainant and
--     customer, category, link to the batch / package tag (traceable)
--   * named investigator with a due date, investigation, root cause,
--     resolution, corrective action, linked deviation (-> CAPA) and hold
--   * response to the complainant; adverse events must be reported to the
--     state regulator before closing
--   * customer feedback with a 1-5 satisfaction rating (CSQ 5.3)
--   * never deleted (cancel with reason, Full access); closing is audited
-- Internal audits (Black Fox / Michigan fields: title, audit type, department,
-- date, lead auditor, scope, findings with severity and corrective action,
-- recommendations, conclusion, next audit date, attachments) plus CSQ 1.5:
--   * numbered (IA-YYYY-###), planned date, auditor qualification, auditor
--     confirmed independent of the area audited
--   * checklist of CSQ clauses with a result and evidence for each; the
--     standards page shows which clauses were audited in the last 12 months
--   * every nonconforming clause needs a finding; findings have an owner,
--     due date and a linked deviation (-> CAPA); a finding closes only with a
--     verification and only after its deviation is closed
--   * results shared with staff (who, when) before the audit is closed;
--     an audit closes only when every finding is closed
-- Access modules 'complaints' and 'intaudits': View (see; anyone with View can
--   log a complaint) / Edit (investigate, plan and run audits, findings) /
--   Full (close audits, reopen, cancel).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-18.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_complaints (
  id                     text primary key,
  state_id               text not null references hx_states(id),
  license_id             text not null references hx_licenses(id),
  number                 text not null default '',
  received_on            date not null default current_date,
  title                  text not null check (length(trim(title)) > 0),
  type                   text not null default 'consumer' check (type in ('consumer','dispensary','return','adverse_event','feedback')),
  priority               text not null default 'minor' check (priority in ('critical','major','minor')),
  channel                text not null default '',
  complainant            text not null default '',
  complainant_contact    text not null default '',
  customer               text not null default '',
  category               text not null default '',
  product                text not null default '',
  lot_number             text not null default '',
  batch_id               text references hx_batches(id),
  tag                    text not null default '',
  description            text not null default '',
  rating                 int check (rating between 1 and 5),
  investigator           text not null default '',
  due_date               date,
  investigation          text not null default '',
  root_cause             text not null default '',
  resolution             text not null default '',
  corrective_action      text not null default '',
  deviation_id           text,
  deviation_number       text not null default '',
  hold_id                text,
  response               text not null default '',
  responded_on           date,
  regulator_reported_on  date,
  status                 text not null default 'open' check (status in ('open','investigating','closed','cancelled')),
  closed_by              text not null default '',
  closed_at              timestamptz,
  cancel_reason          text not null default '',
  attachments            jsonb not null default '[]'::jsonb,
  created_by             text not null default '',
  created_by_id          uuid default auth.uid(),
  created_at             timestamptz not null default now(),
  updated_by             text not null default '',
  updated_at             timestamptz not null default now()
);
create unique index if not exists hx_complaints_number on hx_complaints(license_id, number);
create index if not exists hx_complaints_lic on hx_complaints(license_id, received_on desc);

create table if not exists hx_audits (
  id                     text primary key,
  state_id               text not null references hx_states(id),
  license_id             text not null references hx_licenses(id),
  number                 text not null default '',
  title                  text not null check (length(trim(title)) > 0),
  audit_type             text not null default 'CSQ internal audit',
  dept                   text not null default '',
  planned_date           date,
  audit_date             date,
  auditor_name           text not null default '',
  auditor_qualification  text not null default '',
  independent            boolean not null default false,
  scope                  text not null default '',
  clauses                jsonb not null default '[]'::jsonb,
  recommendations        text not null default '',
  conclusion             text not null default '',
  shared_with            text not null default '',
  shared_on              date,
  status                 text not null default 'planned' check (status in ('planned','in_progress','completed','closed','cancelled')),
  next_audit_date        date,
  attachments            jsonb not null default '[]'::jsonb,
  cancel_reason          text not null default '',
  closed_by              text not null default '',
  closed_at              timestamptz,
  created_by             text not null default '',
  created_by_id          uuid default auth.uid(),
  created_at             timestamptz not null default now(),
  updated_by             text not null default '',
  updated_at             timestamptz not null default now()
);
create unique index if not exists hx_audits_number on hx_audits(license_id, number);
create index if not exists hx_audits_lic on hx_audits(license_id, coalesce(audit_date, planned_date) desc);

create table if not exists hx_audit_findings (
  id                 text primary key,
  state_id           text not null references hx_states(id),
  license_id         text not null references hx_licenses(id),
  audit_id           text not null references hx_audits(id),
  clause             text not null default '',
  severity           text not null default 'minor' check (severity in ('critical','major','minor','observation')),
  description        text not null check (length(trim(description)) > 0),
  corrective_action  text not null default '',
  owner_name         text not null default '',
  due_date           date,
  deviation_id       text,
  deviation_number   text not null default '',
  status             text not null default 'open' check (status in ('open','closed')),
  verification       text not null default '',
  closed_by          text not null default '',
  closed_at          timestamptz,
  created_by         text not null default '',
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);
create index if not exists hx_audit_findings_audit on hx_audit_findings(audit_id);

-- ---------- complaints ----------
create or replace function hx_complaint_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; d record; v_edit boolean := hx_perm('complaints') >= 2; v_full boolean := hx_perm('complaints') >= 3;
begin
  if tg_op = 'DELETE' then raise exception 'Complaints are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  if new.batch_id is not null then
    select * into b from hx_batches where id = new.batch_id;
    if b.id is null or b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
    if coalesce(trim(new.lot_number),'') = '' then new.lot_number := b.batch_number; end if;
  end if;
  if new.deviation_id is not null then
    select id, number into d from hx_deviations where id = new.deviation_id and license_id = new.license_id;
    if d.id is null then raise exception 'Unknown deviation for this license.'; end if;
    new.deviation_number := d.number;
  end if;
  if new.type <> 'feedback' then new.rating := null; end if;
  if tg_op = 'INSERT' then
    if hx_perm('complaints') < 1 then raise exception 'You need access to Complaints.'; end if;
    if new.received_on > current_date then raise exception 'The received date cannot be in the future.'; end if;
    new.number := hx_next_number('hx_complaints', new.license_id, case when new.type = 'feedback' then 'FBK' else 'CMP' end);
    new.created_by := coalesce(hx_me(), new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('open','investigating') then raise exception 'A new complaint starts open.'; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', case when new.type = 'feedback' then 'Customer feedback logged' else 'Complaint logged' end, true);
    return new;
  end if;
  if new.number <> old.number or new.created_at <> old.created_at or new.created_by_id is distinct from old.created_by_id or new.license_id <> old.license_id then
    raise exception 'The number, date logged and license of a complaint cannot be changed.';
  end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'This complaint is %. Only someone with Full access can reopen it.', old.status; end if;
    if new.status = old.status then raise exception 'This complaint is %. Reopen it first.', old.status; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Complaint reopened', true);
    return new;
  end if;
  if not v_edit then raise exception 'You need Edit access to Complaints to investigate.'; end if;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access can cancel a complaint.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Complaint cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status = 'closed' then
    if new.type <> 'feedback' then
      if coalesce(trim(new.investigator),'') = '' then raise exception 'Name who investigated the complaint (CSQ 1.7 a).'; end if;
      if coalesce(trim(new.investigation),'') = '' then raise exception 'Record the investigation before closing.'; end if;
      if coalesce(trim(new.resolution),'') = '' then raise exception 'Record the resolution before closing.'; end if;
      if (coalesce(trim(new.complainant_contact),'') <> '' or coalesce(trim(new.customer),'') <> '') and new.responded_on is null then
        raise exception 'Record when the complainant was answered before closing (CSQ 1.7 a).';
      end if;
      if new.type = 'adverse_event' and new.regulator_reported_on is null then
        raise exception 'An adverse event must be reported to the state regulator before it is closed.';
      end if;
    end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Complaint closed: ' || left(coalesce(nullif(trim(new.resolution),''), 'feedback recorded'), 200), true);
    return new;
  end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Complaint updated', true); end if;
  return new;
end $$;

-- ---------- internal audits ----------
create or replace function hx_audit_rec_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_edit boolean := hx_perm('intaudits') >= 2; v_full boolean := hx_perm('intaudits') >= 3; c jsonb; v_missing text;
begin
  if tg_op = 'DELETE' then
    if old.status <> 'planned' or not v_full then raise exception 'Internal audits are never deleted once started. Cancel with a reason.'; end if;
    return old;
  end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  if tg_op = 'INSERT' then
    if not v_edit then raise exception 'You need Edit access to Internal Audits.'; end if;
    new.number := hx_next_number('hx_audits', new.license_id, 'IA');
    new.created_by := coalesce(hx_me(), new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('planned','in_progress') then raise exception 'A new audit starts planned or in progress.'; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Internal audit ' || new.status, true);
    return new;
  end if;
  if new.number <> old.number or new.created_at <> old.created_at or new.license_id <> old.license_id then raise exception 'The number and license of an audit cannot be changed.'; end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'This audit is %. Only someone with Full access can reopen it.', old.status; end if;
    if new.status = old.status then raise exception 'This audit is %. Reopen it first.', old.status; end if;
    new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Audit reopened', true);
    return new;
  end if;
  if not v_edit then raise exception 'You need Edit access to Internal Audits.'; end if;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access can cancel an audit.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    perform set_config('hx.reason', 'Audit cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status in ('completed','closed') then
    if new.audit_date is null or new.audit_date > current_date then raise exception 'Enter the date the audit was done (not in the future).'; end if;
    if coalesce(trim(new.auditor_name),'') = '' or coalesce(trim(new.auditor_qualification),'') = '' then raise exception 'Name the auditor and their qualification (CSQ 1.5 b).'; end if;
    if not new.independent then raise exception 'Confirm the auditor does not audit their own work (CSQ 1.5 c).'; end if;
    if jsonb_array_length(new.clauses) = 0 and coalesce(trim(new.scope),'') = '' then raise exception 'Record what was audited (clauses or scope).'; end if;
    if exists (select 1 from jsonb_array_elements(new.clauses) x where coalesce(x->>'result','') = '') then raise exception 'Every clause on the checklist needs a result.'; end if;
    select string_agg(x->>'clause', ', ') into v_missing from jsonb_array_elements(new.clauses) x
     where x->>'result' = 'Nonconforming' and not exists (select 1 from hx_audit_findings f where f.audit_id = new.id and f.clause = x->>'clause');
    if v_missing is not null then raise exception 'Record a finding for each nonconforming clause: %', v_missing; end if;
  end if;
  if new.status = 'closed' and old.status <> 'closed' then
    if not v_full then raise exception 'Only someone with Full access can close an audit.'; end if;
    if exists (select 1 from hx_audit_findings f where f.audit_id = new.id and f.status <> 'closed') then raise exception 'Close every finding first (CSQ 1.5 f).'; end if;
    if new.shared_on is null or coalesce(trim(new.shared_with),'') = '' then raise exception 'Record who the results were shared with and when (CSQ 1.5 e).'; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Audit closed', true);
    return new;
  end if;
  if new.status = 'completed' and old.status <> 'completed' then perform set_config('hx.reason', 'Audit completed', true);
  elsif coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Audit updated', true); end if;
  return new;
end $$;

create or replace function hx_finding_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare a record; v_dst text; v_dno text;
begin
  if tg_op = 'DELETE' then
    select * into a from hx_audits where id = old.audit_id;
    if a.status not in ('planned','in_progress') or hx_perm('intaudits') < 2 then raise exception 'Findings of a completed audit are never deleted.'; end if;
    return old;
  end if;
  select * into a from hx_audits where id = new.audit_id;
  if a.id is null or a.license_id <> new.license_id then raise exception 'Unknown audit for this license.'; end if;
  if a.status in ('closed','cancelled') then raise exception 'This audit is %.', a.status; end if;
  if hx_perm('intaudits') < 2 then raise exception 'You need Edit access to Internal Audits.'; end if;
  new.updated_at := now();
  if new.deviation_id is not null then
    select number, status into v_dno, v_dst from hx_deviations where id = new.deviation_id and license_id = new.license_id;
    if v_dno is null then raise exception 'Unknown deviation for this license.'; end if;
    new.deviation_number := v_dno;
  end if;
  if tg_op = 'INSERT' then
    new.created_by := coalesce(hx_me(),''); new.created_at := now(); new.status := 'open'; new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Finding recorded (' || new.severity || ')', true);
    return new;
  end if;
  if old.status = 'closed' then
    if hx_perm('intaudits') < 3 then raise exception 'This finding is closed. Only someone with Full access can reopen it.'; end if;
    if new.status = 'closed' then raise exception 'This finding is closed. Reopen it first.'; end if;
    new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Finding reopened', true);
    return new;
  end if;
  if new.status = 'closed' then
    if coalesce(trim(new.verification),'') = '' then raise exception 'Record how the correction was verified as effective (CSQ 1.5 f).'; end if;
    if new.severity <> 'observation' and new.deviation_id is null and coalesce(trim(new.corrective_action),'') = '' then raise exception 'Record the corrective action (or link a deviation) before closing.'; end if;
    if new.deviation_id is not null and coalesce(v_dst,'') <> 'closed' then raise exception 'Close deviation % first (corrective action process).', v_dno; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Finding closed: ' || left(trim(new.verification), 200), true);
    return new;
  end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Finding updated', true); end if;
  return new;
end $$;

drop trigger if exists hx_complaints_guard on hx_complaints;
create trigger hx_complaints_guard before insert or update or delete on hx_complaints for each row execute function hx_complaint_guard();
drop trigger if exists hx_complaints_place on hx_complaints;
create trigger hx_complaints_place before insert or update on hx_complaints for each row execute function hx_fl_guard();
drop trigger if exists hx_complaints_audit on hx_complaints;
create trigger hx_complaints_audit after insert or update on hx_complaints for each row execute function hx_audit();
drop trigger if exists hx_audits_guard on hx_audits;
create trigger hx_audits_guard before insert or update or delete on hx_audits for each row execute function hx_audit_rec_guard();
drop trigger if exists hx_audits_place on hx_audits;
create trigger hx_audits_place before insert or update on hx_audits for each row execute function hx_fl_guard();
drop trigger if exists hx_audits_audit on hx_audits;
create trigger hx_audits_audit after insert or update or delete on hx_audits for each row execute function hx_audit();
drop trigger if exists hx_audit_findings_guard on hx_audit_findings;
create trigger hx_audit_findings_guard before insert or update or delete on hx_audit_findings for each row execute function hx_finding_guard();
drop trigger if exists hx_audit_findings_place on hx_audit_findings;
create trigger hx_audit_findings_place before insert or update on hx_audit_findings for each row execute function hx_fl_guard();
drop trigger if exists hx_audit_findings_audit on hx_audit_findings;
create trigger hx_audit_findings_audit after insert or update or delete on hx_audit_findings for each row execute function hx_audit();

alter table hx_complaints enable row level security;
alter table hx_audits enable row level security;
alter table hx_audit_findings enable row level security;
drop policy if exists hx_complaints_read on hx_complaints;
drop policy if exists hx_complaints_insert on hx_complaints;
drop policy if exists hx_complaints_update on hx_complaints;
create policy hx_complaints_read   on hx_complaints for select to authenticated using (hx_can('complaints',1,license_id));
create policy hx_complaints_insert on hx_complaints for insert to authenticated with check (hx_can('complaints',1,license_id));
create policy hx_complaints_update on hx_complaints for update to authenticated using (hx_can('complaints',2,license_id)) with check (hx_can('complaints',2,license_id));
drop policy if exists hx_audits_read on hx_audits;
drop policy if exists hx_audits_insert on hx_audits;
drop policy if exists hx_audits_update on hx_audits;
drop policy if exists hx_audits_delete on hx_audits;
create policy hx_audits_read   on hx_audits for select to authenticated using (hx_can('intaudits',1,license_id));
create policy hx_audits_insert on hx_audits for insert to authenticated with check (hx_can('intaudits',2,license_id));
create policy hx_audits_update on hx_audits for update to authenticated using (hx_can('intaudits',2,license_id)) with check (hx_can('intaudits',2,license_id));
create policy hx_audits_delete on hx_audits for delete to authenticated using (hx_can('intaudits',3,license_id));
drop policy if exists hx_audit_findings_read on hx_audit_findings;
drop policy if exists hx_audit_findings_insert on hx_audit_findings;
drop policy if exists hx_audit_findings_update on hx_audit_findings;
drop policy if exists hx_audit_findings_delete on hx_audit_findings;
create policy hx_audit_findings_read   on hx_audit_findings for select to authenticated using (hx_can('intaudits',1,license_id));
create policy hx_audit_findings_insert on hx_audit_findings for insert to authenticated with check (hx_can('intaudits',2,license_id));
create policy hx_audit_findings_update on hx_audit_findings for update to authenticated using (hx_can('intaudits',2,license_id)) with check (hx_can('intaudits',2,license_id));
create policy hx_audit_findings_delete on hx_audit_findings for delete to authenticated using (hx_can('intaudits',2,license_id));
grant select, insert, update on hx_complaints to authenticated;
grant select, insert, update, delete on hx_audits, hx_audit_findings to authenticated;

notify pgrst, 'reload schema';
