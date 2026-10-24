-- =====================================================================
-- Hendrix QMS  -  Step 29: Risk register and Change control (CSQ Level 3)
-- Risk register (CSQ 5.1.6; also 1.9 product defense threat assessment,
-- 1.10 fraud vulnerability, 2A.12.7 allergens, 3A.1.2 outdoor site risk):
--   * numbered RK-###; the hazard, its root cause, the owner, the inherent
--     rating (likelihood x severity, 1-5 each), existing controls, the
--     immediate action and the timescale (target date) for a permanent fix
--   * high and critical risks (score 10+) need an immediate action and a
--     target date before they can be saved
--   * "controlled" needs the permanent action, its verification (what, who,
--     when) and the residual rating
--   * routine surveillance: every risk is reviewed on a schedule (review
--     every N days); each review is a record (hx_risk_reviews) that updates
--     the current rating and the next review date
--   * closing a risk needs Full access and a reason; risks are never deleted
-- Change control (CSQ 5.1.5, 5.4.1; 4A.10 / 4A.11 after significant change):
--   * numbered CC-YYYY-###: type (product, process, equipment, facility,
--     material / supplier, people / organization, document / SOP,
--     regulatory, IT / system), what changes and why, the impact
--     assessment (HACCP, allergens, labels, specs, SOPs, training,
--     equipment, suppliers, testing, facility, license, customers, METRC)
--   * requested -> approved (Full access = qualified person) -> implemented
--     -> closed (effectiveness check); or rejected / cancelled with a reason
--   * implemented only when every action is done, training was given before
--     use (when required), a trial run passed (when required), the HACCP plan
--     was reviewed (when HACCP is affected) and the regulator / certification
--     body / customers were told (when required)
--   * after approval the change itself cannot be rewritten
-- Access modules 'risks' and 'changes': View / Edit (record, review,
--   request, record actions) / Full (close risks; approve, reject, close
--   changes).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-28.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_risks (
  id                  text primary key,
  state_id            text not null references hx_states(id),
  license_id          text not null references hx_licenses(id),
  number              text not null default '',
  title               text not null check (length(trim(title)) > 0),
  category            text not null default 'product_safety',
  area                text not null default '',
  hazard              text not null default '',
  root_cause          text not null default '',
  owner               text not null default '',
  source_type         text not null default '',
  source_label        text not null default '',
  likelihood          int  not null default 3 check (likelihood between 1 and 5),
  severity            int  not null default 3 check (severity between 1 and 5),
  score               int  generated always as (likelihood * severity) stored,
  controls            text not null default '',
  immediate_action    text not null default '',
  permanent_action    text not null default '',
  target_date         date,
  capa_id             text,
  residual_likelihood int check (residual_likelihood between 1 and 5),
  residual_severity   int check (residual_severity between 1 and 5),
  residual_score      int  generated always as (residual_likelihood * residual_severity) stored,
  verification        text not null default '',
  verified_by         text not null default '',
  verified_on         date,
  review_every_days   int  not null default 365 check (review_every_days between 7 and 1095),
  last_reviewed       date,
  next_review         date,
  status              text not null default 'open' check (status in ('open','controlled','closed')),
  close_reason        text,
  closed_by           text not null default '',
  closed_at           timestamptz,
  files               jsonb not null default '[]'::jsonb,
  notes               text not null default '',
  created_by          text not null default '',
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);
create unique index if not exists hx_risks_number on hx_risks(license_id, number);

create or replace function hx_risk_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then raise exception 'Risks are never deleted. Close the risk with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_risks', new.license_id, 'RK');
    new.created_by := v_me; new.created_at := now(); new.status := 'open';
    new.close_reason := null; new.closed_by := ''; new.closed_at := null;
    new.residual_likelihood := null; new.residual_severity := null; new.verification := ''; new.verified_by := ''; new.verified_on := null;
    new.last_reviewed := current_date;
    perform set_config('hx.reason', 'Risk assessed', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if coalesce(current_setting('hx.internal', true), '') = 'on' then
      new.next_review := coalesce(new.last_reviewed, old.created_at::date) + new.review_every_days; new.updated_at := now(); return new;
    end if;
    if old.status = 'closed' then
      if (to_jsonb(new) - 'files' - 'notes' - 'updated_at') is distinct from (to_jsonb(old) - 'files' - 'notes' - 'updated_at') then
        raise exception 'This risk is closed.';
      end if;
      new.updated_at := now(); return new;
    end if;
    new.last_reviewed := old.last_reviewed;   -- only a review moves the review date
    if new.status = 'closed' then
      if not hx_can('risks', 3, new.license_id) then raise exception 'Only Full access can close a risk.'; end if;
      if coalesce(trim(new.close_reason), '') = '' then raise exception 'Give a reason to close the risk (for example: the process no longer exists).'; end if;
      new.closed_by := v_me; new.closed_at := now();
      perform set_config('hx.reason', 'Risk closed: ' || trim(new.close_reason), true);
    elsif new.status = 'controlled' and old.status = 'open' then
      if coalesce(trim(new.permanent_action), '') = '' then raise exception 'Record the permanent action before marking the risk controlled.'; end if;
      if coalesce(trim(new.verification), '') = '' or coalesce(trim(new.verified_by), '') = '' or new.verified_on is null then
        raise exception 'Record how the permanent action was verified, by whom and when.';
      end if;
      if new.verified_on > current_date then raise exception 'The verification date cannot be in the future.'; end if;
      if new.residual_likelihood is null or new.residual_severity is null then raise exception 'Rate the risk again with the controls in place (residual rating).'; end if;
      perform set_config('hx.reason', 'Risk controlled and verified', true);
    elsif new.status = 'open' and old.status = 'controlled' then
      perform set_config('hx.reason', 'Risk re-opened', true);
    elsif new.status <> old.status then
      raise exception 'A risk goes open -> controlled, or is closed.';
    elsif old.status = 'controlled' and (new.verification, new.verified_by, new.verified_on) is distinct from (old.verification, old.verified_by, old.verified_on) then
      raise exception 'The verification is recorded. Re-open the risk to change it.';
    end if;
  end if;
  if coalesce(trim(new.hazard), '') = '' then raise exception 'Describe the hazard (what could go wrong).'; end if;
  if coalesce(trim(new.root_cause), '') = '' then raise exception 'Enter the root cause (why it could happen).'; end if;
  if coalesce(trim(new.owner), '') = '' then raise exception 'Every risk needs an owner.'; end if;
  if new.status = 'open' and new.likelihood * new.severity >= 10 and (coalesce(trim(new.immediate_action), '') = '' or new.target_date is null) then
    raise exception 'A high or critical risk (score %) needs an immediate action and a target date for the permanent fix.', new.likelihood * new.severity;
  end if;
  new.next_review := coalesce(new.last_reviewed, current_date) + new.review_every_days;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_risks_guard on hx_risks;
create trigger hx_risks_guard before insert or update or delete on hx_risks for each row execute function hx_risk_guard();
drop trigger if exists hx_risks_place on hx_risks;
create trigger hx_risks_place before insert or update on hx_risks for each row execute function hx_fl_guard();
drop trigger if exists hx_risks_audit on hx_risks;
create trigger hx_risks_audit after insert or update on hx_risks for each row execute function hx_audit();

-- routine surveillance: each review is kept and moves the next review date
create table if not exists hx_risk_reviews (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  risk_id       text not null references hx_risks(id),
  reviewed_on   date not null default current_date,
  reviewed_by   text not null default '',
  likelihood    int  not null check (likelihood between 1 and 5),
  severity      int  not null check (severity between 1 and 5),
  effective     boolean not null default true,
  notes         text not null default '',
  recorded_by   text not null default '',
  created_at    timestamptz not null default now()
);
create index if not exists hx_risk_reviews_risk on hx_risk_reviews(risk_id);

create or replace function hx_risk_review_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare r record;
begin
  if tg_op <> 'INSERT' then raise exception 'Risk reviews cannot be changed or deleted. Record a new review.'; end if;
  select * into r from hx_risks where id = new.risk_id;
  if r.id is null or r.license_id <> new.license_id then raise exception 'That risk belongs to another license.'; end if;
  if r.status = 'closed' then raise exception 'This risk is closed.'; end if;
  if new.reviewed_on > current_date then raise exception 'The review date cannot be in the future.'; end if;
  if coalesce(trim(new.reviewed_by), '') = '' then raise exception 'Enter who reviewed the risk.'; end if;
  if not new.effective and coalesce(trim(new.notes), '') = '' then raise exception 'The controls are not effective: describe what will be done.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now();
  perform set_config('hx.reason', 'Risk reviewed', true);
  return new;
end $$;
drop trigger if exists hx_risk_reviews_guard on hx_risk_reviews;
create trigger hx_risk_reviews_guard before insert or update or delete on hx_risk_reviews for each row execute function hx_risk_review_guard();
drop trigger if exists hx_risk_reviews_place on hx_risk_reviews;
create trigger hx_risk_reviews_place before insert or update on hx_risk_reviews for each row execute function hx_fl_guard();
drop trigger if exists hx_risk_reviews_audit on hx_risk_reviews;
create trigger hx_risk_reviews_audit after insert on hx_risk_reviews for each row execute function hx_audit();

create or replace function hx_risk_review_apply() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform set_config('hx.reason', case when not new.effective then 'Risk review: controls not effective' else 'Risk reviewed' end, true);
  perform set_config('hx.internal', 'on', true);
  update hx_risks set
    last_reviewed = greatest(coalesce(last_reviewed, new.reviewed_on), new.reviewed_on),
    residual_likelihood = case when status = 'controlled' then new.likelihood else residual_likelihood end,
    residual_severity   = case when status = 'controlled' then new.severity   else residual_severity end,
    likelihood = case when status = 'open' then new.likelihood else likelihood end,
    severity   = case when status = 'open' then new.severity   else severity end,
    status = case when status = 'controlled' and not new.effective then 'open' else status end
  where id = new.risk_id;
  perform set_config('hx.internal', '', true);
  return null;
end $$;
drop trigger if exists hx_risk_reviews_zapply on hx_risk_reviews;
create trigger hx_risk_reviews_zapply after insert on hx_risk_reviews for each row execute function hx_risk_review_apply();

create table if not exists hx_changes (
  id                text primary key,
  state_id          text not null references hx_states(id),
  license_id        text not null references hx_licenses(id),
  number            text not null default '',
  title             text not null check (length(trim(title)) > 0),
  change_type       text not null default 'process',
  description       text not null default '',
  reason            text not null default '',
  product           text not null default '',
  requested_by      text not null default '',
  requested_on      date not null default current_date,
  impacts           jsonb not null default '{}'::jsonb,
  impact_notes      text not null default '',
  risk_level        text not null default 'medium' check (risk_level in ('low','medium','high')),
  risk_id           text references hx_risks(id),
  sop_ids           text[] not null default '{}',
  plan_ids          text[] not null default '{}',
  course_ids        text[] not null default '{}',
  actions           jsonb not null default '[]'::jsonb,
  training_required boolean not null default false,
  training_done     boolean not null default false,
  training_note     text not null default '',
  trial_required    boolean not null default false,
  trial_result      text not null default '' check (trial_result in ('','pass','fail')),
  trial_note        text not null default '',
  haccp_reviewed    boolean not null default false,
  notify            jsonb not null default '{}'::jsonb,
  notified_on       date,
  notified_note     text not null default '',
  target_date       date,
  status            text not null default 'requested' check (status in ('requested','approved','implemented','closed','rejected','cancelled')),
  approved_by       text not null default '',
  approved_at       timestamptz,
  approval_note     text not null default '',
  implemented_on    date,
  effectiveness     text not null default '',
  closed_by         text not null default '',
  closed_at         timestamptz,
  stop_reason       text,
  files             jsonb not null default '[]'::jsonb,
  notes             text not null default '',
  created_by        text not null default '',
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create unique index if not exists hx_changes_number on hx_changes(license_id, number);

create or replace function hx_change_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_me text := coalesce(hx_me(), ''); a jsonb; n_open int := 0; n_act int := 0;
begin
  if tg_op = 'DELETE' then raise exception 'Change records are never deleted. Cancel or reject the change with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_changes', new.license_id, 'CC');
    new.created_by := v_me; new.created_at := now(); new.status := 'requested';
    new.approved_by := ''; new.approved_at := null; new.implemented_on := null; new.effectiveness := ''; new.closed_by := ''; new.closed_at := null; new.stop_reason := null;
    if coalesce(trim(new.requested_by), '') = '' then new.requested_by := v_me; end if;
    perform set_config('hx.reason', 'Change requested', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if old.status in ('closed','rejected','cancelled') then
      if (to_jsonb(new) - 'files' - 'notes' - 'updated_at') is distinct from (to_jsonb(old) - 'files' - 'notes' - 'updated_at') then
        raise exception 'This change is %.', old.status;
      end if;
      new.updated_at := now(); return new;
    end if;
    if old.status <> 'requested' and (new.title, new.change_type, new.description, new.reason, new.product, new.impacts, new.impact_notes, new.risk_level, new.requested_by, new.requested_on)
         is distinct from (old.title, old.change_type, old.description, old.reason, old.product, old.impacts, old.impact_notes, old.risk_level, old.requested_by, old.requested_on) then
      raise exception 'The change was approved as written. Cancel it and request a new change to change what it is.';
    end if;
    if old.status <> 'requested' and (new.training_required, new.trial_required) is distinct from (old.training_required, old.trial_required) then
      raise exception 'Training and trial requirements were set at approval.';
    end if;
    new.approved_by := old.approved_by; new.approved_at := old.approved_at;
    if new.status <> old.status then
      if new.status in ('rejected','cancelled') then
        if not hx_can('changes', 3, new.license_id) then raise exception 'Only Full access can % a change.', case when new.status = 'rejected' then 'reject' else 'cancel' end; end if;
        if new.status = 'rejected' and old.status <> 'requested' then raise exception 'Only a requested change can be rejected. Cancel it instead.'; end if;
        if old.status = 'implemented' then raise exception 'This change is already implemented. Close it with the effectiveness check, or request a new change to undo it.'; end if;
        if coalesce(trim(new.stop_reason), '') = '' then raise exception 'A reason is required.'; end if;
        new.closed_by := v_me; new.closed_at := now();
        perform set_config('hx.reason', 'Change ' || new.status || ': ' || trim(new.stop_reason), true);
      elsif new.status = 'approved' and old.status = 'requested' then
        if not hx_can('changes', 3, new.license_id) then raise exception 'Only Full access (a qualified person) can approve a change.'; end if;
        new.approved_by := v_me; new.approved_at := now();
        perform set_config('hx.reason', 'Change approved', true);
      elsif new.status = 'implemented' and old.status = 'approved' then
        for a in select * from jsonb_array_elements(coalesce(new.actions, '[]'::jsonb)) loop
          n_act := n_act + 1; if coalesce((a->>'done')::boolean, false) is not true then n_open := n_open + 1; end if;
        end loop;
        if n_act = 0 then raise exception 'List the actions that put the change in place.'; end if;
        if n_open > 0 then raise exception '% action(s) are not done yet.', n_open; end if;
        if new.training_required and not new.training_done then raise exception 'Training must be given before the change is used.'; end if;
        if new.trial_required and new.trial_result <> 'pass' then raise exception 'A trial run must pass before the change is implemented.'; end if;
        if coalesce((new.impacts->>'haccp')::boolean, false) and not new.haccp_reviewed then
          raise exception 'HACCP is affected: review (and revalidate) the HACCP plan before the change is implemented.';
        end if;
        if (coalesce((new.notify->>'regulator')::boolean, false) or coalesce((new.notify->>'cert_body')::boolean, false) or coalesce((new.notify->>'customers')::boolean, false)) and new.notified_on is null then
          raise exception 'Record when the regulator / certification body / customers were told.';
        end if;
        if new.implemented_on is null then new.implemented_on := current_date; end if;
        if new.implemented_on > current_date then raise exception 'The implementation date cannot be in the future.'; end if;
        perform set_config('hx.reason', 'Change implemented', true);
      elsif new.status = 'closed' and old.status = 'implemented' then
        if not hx_can('changes', 3, new.license_id) then raise exception 'Only Full access can close a change.'; end if;
        if coalesce(trim(new.effectiveness), '') = '' then raise exception 'Record the effectiveness check (did the change work as planned?).'; end if;
        new.closed_by := v_me; new.closed_at := now();
        perform set_config('hx.reason', 'Change closed after effectiveness check', true);
      else
        raise exception 'A change goes requested -> approved -> implemented -> closed (or rejected / cancelled).';
      end if;
    elsif old.status = 'approved' then
      perform set_config('hx.reason', 'Change plan updated', true);
    elsif old.status = 'implemented' and (new.actions, new.training_done, new.trial_result, new.haccp_reviewed, new.notified_on, new.implemented_on)
         is distinct from (old.actions, old.training_done, old.trial_result, old.haccp_reviewed, old.notified_on, old.implemented_on) then
      raise exception 'This change is implemented. Its actions are on record.';
    end if;
  end if;
  if coalesce(trim(new.description), '') = '' then raise exception 'Describe what changes.'; end if;
  if coalesce(trim(new.reason), '') = '' then raise exception 'Give the reason for the change.'; end if;
  if not exists (select 1 from jsonb_each(coalesce(new.impacts, '{}'::jsonb)) e where e.value = 'true'::jsonb) then
    raise exception 'Complete the impact assessment (tick what the change affects, or "Nothing else is affected").';
  end if;
  if new.risk_id is not null and not exists (select 1 from hx_risks where id = new.risk_id and license_id = new.license_id) then raise exception 'That risk belongs to another license.'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_changes_guard on hx_changes;
create trigger hx_changes_guard before insert or update or delete on hx_changes for each row execute function hx_change_guard();
drop trigger if exists hx_changes_place on hx_changes;
create trigger hx_changes_place before insert or update on hx_changes for each row execute function hx_fl_guard();
drop trigger if exists hx_changes_audit on hx_changes;
create trigger hx_changes_audit after insert or update on hx_changes for each row execute function hx_audit();

alter table hx_risks enable row level security;
alter table hx_risk_reviews enable row level security;
alter table hx_changes enable row level security;
drop policy if exists hx_risks_read on hx_risks;
drop policy if exists hx_risks_insert on hx_risks;
drop policy if exists hx_risks_update on hx_risks;
create policy hx_risks_read   on hx_risks for select to authenticated using (hx_can('risks',1,license_id));
create policy hx_risks_insert on hx_risks for insert to authenticated with check (hx_can('risks',2,license_id));
create policy hx_risks_update on hx_risks for update to authenticated using (hx_can('risks',2,license_id)) with check (hx_can('risks',2,license_id));
drop policy if exists hx_risk_reviews_read on hx_risk_reviews;
drop policy if exists hx_risk_reviews_insert on hx_risk_reviews;
create policy hx_risk_reviews_read   on hx_risk_reviews for select to authenticated using (hx_can('risks',1,license_id));
create policy hx_risk_reviews_insert on hx_risk_reviews for insert to authenticated with check (hx_can('risks',2,license_id));
drop policy if exists hx_changes_read on hx_changes;
drop policy if exists hx_changes_insert on hx_changes;
drop policy if exists hx_changes_update on hx_changes;
create policy hx_changes_read   on hx_changes for select to authenticated using (hx_can('changes',1,license_id));
create policy hx_changes_insert on hx_changes for insert to authenticated with check (hx_can('changes',2,license_id));
create policy hx_changes_update on hx_changes for update to authenticated using (hx_can('changes',2,license_id)) with check (hx_can('changes',2,license_id));
grant select, insert, update on hx_risks, hx_changes to authenticated;
grant select, insert on hx_risk_reviews to authenticated;

notify pgrst, 'reload schema';
