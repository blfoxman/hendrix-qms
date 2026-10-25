-- =====================================================================
-- Hendrix QMS  -  Step 39: My Tasks inbox + email alerts
--
--   * hx_my_tasks(license): everything waiting for the signed-in person at a
--     license, worked out by the database from the records and the person's
--     access - nothing to keep up to date by hand:
--       - mine:    SOPs to read and sign, training needed / expiring, CAPAs,
--                  deviations, audit findings, complaints, risk reviews,
--                  objectives, change and management review actions, and
--                  verification activities assigned to the person;
--       - approve: decisions that need the person's level (SOP drafts and
--                  reviews, holds, lots in quarantine, suppliers, changes,
--                  calibrations, out-of-limit CCP checks, management review,
--                  test results, deviations without an owner).
--   * Email: a daily task list per person (hx_task_digest) and urgent alerts
--     (hx_notify_queue: hold placed, test failed, critical deviation or
--     complaint, real recall or withdrawal started) to the people with Full
--     access to that area. Sent by the Edge Function "hendrix-notify"
--     (hendrix-notify.ts) through Resend; every email is logged in hx_notify_log.
--     Each person can switch their daily email off in My account.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-38.
-- Safe to run more than once. Email also needs the hendrix-notify function and
-- its schedule (see the end of this file).
-- =====================================================================

alter table hx_profiles add column if not exists task_email boolean not null default true;

create or replace function hx_task(p_kind text, p_grp text, p_page text, p_title text, p_detail text, p_due date, p_ref text) returns jsonb
language sql immutable as $$
  select jsonb_build_object('kind', p_kind, 'group', p_grp, 'page', p_page, 'title', p_title, 'detail', coalesce(p_detail, ''),
    'due', p_due, 'overdue', coalesce(p_due < current_date, false), 'ref', coalesce(p_ref, ''));
$$;

create or replace function hx_my_tasks(p_lic text) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare me record; nm text; d date := current_date; v jsonb := '[]'::jsonb; lvl int;
begin
  select * into me from hx_profiles where id::text = auth.uid()::text;
  if me.id is null or p_lic is null or not hx_lic_ok(p_lic) then return '[]'::jsonb; end if;
  nm := lower(trim(coalesce(me.name, '')));

  -- ---------------- assigned to me ----------------
  if hx_perm('sops') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('sop_sign', 'mine', 'sops', 'Read and sign: ' || s.title,
             trim(coalesce(s.sop_number, '') || ' v' || s.version), null, s.id) order by s.effective_date nulls last)
      from hx_sops s
      where s.status = 'published' and (s.license_id = p_lic or p_lic = any(coalesce(s.license_ids, '{}')))
        and (s.target_mode = 'license'
             or (s.target_mode = 'roles' and coalesce(s.target_role_ids, '{}') && coalesce(me.role_ids, '{}'))
             or (s.target_mode = 'people' and me.id::text = any(coalesce(s.target_user_ids, '{}'))))
        and not exists (select 1 from hx_sop_acks a where a.sop_id = s.id and a.version = s.version and a.user_id::text = me.id::text)), '[]'::jsonb);
  end if;

  if hx_perm('training') >= 1 then
    v := v || coalesce((select jsonb_agg(case when r.id is null then hx_task('training', 'mine', 'training', 'Training needed: ' || c.name, coalesce(c.topic, ''), null, c.id)
                                            else hx_task('training', 'mine', 'training', (case when r.expires_on < d then 'Training expired: ' else 'Training expires soon: ' end) || c.name,
                                                         'Completed ' || to_char(r.completed_on, 'Mon DD, YYYY'), r.expires_on, c.id) end)
      from hx_training_courses c
      left join lateral (select * from hx_training_records x where x.course_id = c.id and x.user_id = me.id::text and not x.voided
                           and coalesce(x.assessment, '') <> 'Failed' order by x.completed_on desc nulls last limit 1) r on true
      where c.active and (c.license_id = p_lic or p_lic = any(coalesce(c.license_ids, '{}')))
        and ((r.id is null and (c.required_mode = 'everyone' or (c.required_mode = 'roles' and coalesce(c.role_ids, '{}') && coalesce(me.role_ids, '{}'))))
             or (r.id is not null and r.expires_on is not null and r.expires_on <= d + 30))), '[]'::jsonb);
  end if;

  if hx_perm('qms') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('capa', 'mine', 'qms', 'CAPA ' || c.number || ': ' || c.title, 'Priority ' || c.priority || ' · ' || replace(c.status, '_', ' '), c.due_date, c.id))
      from hx_capas c where c.license_id = p_lic and c.status not in ('closed', 'cancelled')
        and (c.responsible_person_id = me.id::text or (nm <> '' and lower(trim(c.responsible_person_name)) = nm))), '[]'::jsonb);
    v := v || coalesce((select jsonb_agg(hx_task('deviation', 'mine', 'qms', 'Deviation ' || x.number || ': ' || x.title, 'Priority ' || x.priority || ' · ' || x.status, x.due_date, x.id))
      from hx_deviations x where x.license_id = p_lic and x.status not in ('closed', 'cancelled') and nm <> '' and lower(trim(x.owner_name)) = nm), '[]'::jsonb);
  end if;

  if hx_perm('intaudits') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('finding', 'mine', 'intaudits', 'Audit finding: ' || left(f.description, 90), 'Severity ' || f.severity || coalesce(' · clause ' || nullif(f.clause, ''), ''), f.due_date, f.id))
      from hx_audit_findings f where f.license_id = p_lic and f.status = 'open' and nm <> '' and lower(trim(f.owner_name)) = nm), '[]'::jsonb);
  end if;

  if hx_perm('complaints') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('complaint', 'mine', 'complaints', 'Complaint ' || c.number || ': ' || c.title, 'Priority ' || c.priority || ' · ' || c.status, c.due_date, c.id))
      from hx_complaints c where c.license_id = p_lic and c.status not in ('closed', 'cancelled') and nm <> '' and lower(trim(c.investigator)) = nm), '[]'::jsonb);
  end if;

  if hx_perm('risks') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('risk', 'mine', 'risks', 'Review risk ' || r.number || ': ' || r.title, 'Score ' || r.score || ' · ' || r.status, r.next_review, r.id))
      from hx_risks r where r.license_id = p_lic and r.status <> 'closed' and nm <> '' and lower(trim(r.owner)) = nm and r.next_review is not null and r.next_review <= d + 7), '[]'::jsonb);
  end if;

  if hx_perm('objectives') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('objective', 'mine', 'objectives', 'Objective ' || o.number || ': ' || o.name, 'Target ' || coalesce(o.target::text, '') || ' ' || coalesce(o.unit, ''), o.due_on, o.id))
      from hx_objectives o where o.license_id = p_lic and o.status = 'active' and nm <> '' and lower(trim(o.owner)) = nm and o.due_on is not null and o.due_on <= d + 30), '[]'::jsonb);
  end if;

  if hx_perm('changes') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('action', 'mine', 'changes', 'Change ' || c.number || ' action: ' || coalesce(a ->> 'what', ''), c.title,
                                                case when coalesce(a ->> 'due', '') ~ '^\d{4}-\d{2}-\d{2}$' then (a ->> 'due')::date end, c.id))
      from hx_changes c, jsonb_array_elements(coalesce(c.actions, '[]'::jsonb)) a
      where c.license_id = p_lic and c.status in ('requested', 'approved', 'implemented') and not coalesce((a ->> 'done')::boolean, false)
        and nm <> '' and lower(trim(a ->> 'who')) = nm), '[]'::jsonb);
  end if;

  if hx_perm('mgmtreview') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('action', 'mine', 'mgmtreview', 'Management review ' || m.number || ' action: ' || coalesce(a ->> 'what', ''), 'Meeting ' || to_char(m.meeting_date, 'Mon DD, YYYY'),
                                                case when coalesce(a ->> 'due', '') ~ '^\d{4}-\d{2}-\d{2}$' then (a ->> 'due')::date end, m.id))
      from hx_mgmt_reviews m, jsonb_array_elements(coalesce(m.actions, '[]'::jsonb)) a
      where m.license_id = p_lic and m.status = 'held' and not coalesce((a ->> 'done')::boolean, false)
        and nm <> '' and lower(trim(a ->> 'who')) = nm), '[]'::jsonb);
  end if;

  if hx_perm('verification') >= 1 then
    v := v || coalesce((select jsonb_agg(hx_task('verification', 'mine', 'verification', 'Verify: ' || p.activity, coalesce(p.method, ''), q.due, p.id))
      from hx_verification_plan p
      cross join lateral (select coalesce((select max(r.done_on) from hx_verification_records r where r.plan_id = p.id and not r.voided) + p.frequency_days, d) as due) q
      where p.license_id = p_lic and p.active and nm <> '' and lower(trim(p.responsible)) = nm and q.due <= d + 7), '[]'::jsonb);
  end if;

  -- ---------------- decisions that need my level ----------------
  lvl := hx_perm('sops');
  if lvl >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('sop_approve', 'approve', 'sops', 'Approve SOP draft: ' || s.title, trim(coalesce(s.sop_number, '') || ' v' || s.version), null, s.id))
      from hx_sops s where s.status = 'draft' and (s.license_id = p_lic or p_lic = any(coalesce(s.license_ids, '{}')))), '[]'::jsonb);
    v := v || coalesce((select jsonb_agg(hx_task('sop_review', 'approve', 'sops', 'SOP review due: ' || s.title, trim(coalesce(s.sop_number, '') || ' v' || s.version), s.next_review, s.id))
      from hx_sops s where s.status = 'published' and s.next_review is not null and s.next_review <= d + 30 and (s.license_id = p_lic or p_lic = any(coalesce(s.license_ids, '{}')))), '[]'::jsonb);
  end if;

  if hx_perm('holds') >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('hold', 'approve', 'holds', 'Decide hold ' || h.number || ': ' || coalesce(nullif(h.item, ''), h.tag, h.kind), left(coalesce(h.reason, ''), 120), null, h.id))
      from hx_holds h where h.license_id = p_lic and h.status = 'open'), '[]'::jsonb);
  end if;

  if hx_perm('receiving') >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('lot', 'approve', 'receiving', 'Accept or reject lot ' || l.number || ': ' || l.item, 'Received ' || to_char(l.received_on, 'Mon DD, YYYY') || coalesce(' from ' || nullif(l.supplier_name, ''), ''), null, l.id))
      from hx_lots l where l.license_id = p_lic and l.status = 'quarantine'), '[]'::jsonb);
  end if;

  lvl := hx_perm('suppliers');
  if lvl >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('supplier', 'approve', 'suppliers', 'Approve supplier: ' || s.name, coalesce(s.category, ''), null, s.id))
      from hx_suppliers s where s.status = 'pending' and (s.license_id = p_lic or p_lic = any(coalesce(s.license_ids, '{}')))), '[]'::jsonb);
  end if;
  if lvl >= 2 then
    v := v || coalesce((select jsonb_agg(hx_task('supplier_review', 'approve', 'suppliers', 'Supplier review due: ' || s.name, s.status, s.next_review, s.id))
      from hx_suppliers s where s.status in ('approved', 'conditional') and s.next_review is not null and s.next_review <= d + 30
        and (s.license_id = p_lic or p_lic = any(coalesce(s.license_ids, '{}')))), '[]'::jsonb);
  end if;

  if hx_perm('changes') >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('change', 'approve', 'changes', 'Approve change ' || c.number || ': ' || c.title, concat_ws(' · ', 'Requested by ' || nullif(c.requested_by, ''), 'risk ' || nullif(c.risk_level, '')), c.target_date, c.id))
      from hx_changes c where c.license_id = p_lic and c.status = 'requested'), '[]'::jsonb);
  end if;

  if hx_perm('equipment') >= 2 then
    v := v || coalesce((select jsonb_agg(x.t) from (
        select hx_task('calibration', 'approve', 'equipment', 'Calibration due: ' || e.number || ' ' || e.name, coalesce(e.location, ''), e.cal_due, e.id) t
          from hx_equipment e where e.license_id = p_lic and e.status = 'in_service' and e.cal_required and e.cal_due is not null and e.cal_due <= d + 14
        union all
        select hx_task('revalidation', 'approve', 'equipment', 'Revalidation due: ' || e.number || ' ' || e.name, coalesce(e.location, ''), e.reval_due, e.id)
          from hx_equipment e where e.license_id = p_lic and e.status = 'in_service' and e.val_required and e.reval_due is not null and e.reval_due <= d + 14) x), '[]'::jsonb);
  end if;

  if hx_perm('haccp') >= 2 then
    v := v || coalesce((select jsonb_agg(hx_task('ccp', 'approve', 'haccp', 'Verify out-of-limit CCP check: ' || m.ccp_name, 'Value ' || coalesce(m.value, '') || ' · ' || to_char(m.checked_at, 'Mon DD HH24:MI'), m.checked_at::date + 1, m.id))
      from hx_haccp_monitoring m where m.license_id = p_lic and not m.voided and m.within_limits = false and coalesce(m.verified_by, '') = ''), '[]'::jsonb);
  end if;

  if hx_perm('mgmtreview') >= 2 then
    v := v || coalesce((select jsonb_agg(hx_task('mgmt_review', 'approve', 'mgmtreview', 'Management review due', 'Last review ' || to_char(q.last_meeting, 'Mon DD, YYYY'), q.due, null))
      from (select max(m.next_review) as due, max(m.meeting_date) as last_meeting from hx_mgmt_reviews m where m.license_id = p_lic and m.status = 'held') q
      where q.due is not null and q.due <= d + 30
        and not exists (select 1 from hx_mgmt_reviews m2 where m2.license_id = p_lic and m2.status = 'draft')), '[]'::jsonb);
  end if;

  if hx_perm('testing') >= 2 then
    v := v || coalesce((select jsonb_agg(hx_task('test_result', 'approve', 'testing', 'Enter test result: ' || coalesce(nullif(t.batch_number, ''), t.tag), coalesce(nullif(t.lab_name, ''), 'lab') || ' · sample ' || coalesce(nullif(t.sample_tag, ''), t.tag), (t.submitted_at::date + 7), t.id))
      from hx_tests t where t.license_id = p_lic and not t.voided and t.status = 'Submitted'), '[]'::jsonb);
  end if;

  if hx_perm('qms') >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('deviation_owner', 'approve', 'qms', 'Give deviation ' || x.number || ' an owner: ' || x.title, 'Priority ' || x.priority, x.due_date, x.id))
      from hx_deviations x where x.license_id = p_lic and x.status not in ('closed', 'cancelled') and trim(coalesce(x.owner_name, '')) = ''), '[]'::jsonb);
  end if;

  -- overdue first, then by due date, then the rest
  return coalesce((select jsonb_agg(t order by (t ->> 'overdue')::boolean desc, (t ->> 'due') nulls last, t ->> 'title') from jsonb_array_elements(v) t), '[]'::jsonb);
end $$;
revoke all on function hx_my_tasks(text) from public, anon;
grant execute on function hx_my_tasks(text) to authenticated;

-- my daily task email on / off
create or replace function hx_set_task_email(p_on boolean) returns boolean
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then raise exception 'Sign in first.'; end if;
  perform set_config('hx.reason', case when p_on then 'Daily task email switched on' else 'Daily task email switched off' end, true);
  update hx_profiles set task_email = p_on where id::text = auth.uid()::text;
  return p_on;
end $$;
revoke all on function hx_set_task_email(boolean) from public, anon;
grant execute on function hx_set_task_email(boolean) to authenticated;

-- ---------------- email: urgent alerts queue ----------------
create table if not exists hx_notify_queue (
  id          bigserial primary key,
  state_id    text not null,
  license_id  text not null,
  module      text not null,
  kind        text not null,
  title       text not null,
  detail      text not null default '',
  page        text not null default '',
  ref         text not null default '',
  created_at  timestamptz not null default now(),
  sent_at     timestamptz,
  recipients  int
);
create index if not exists hx_notify_queue_pending on hx_notify_queue(created_at) where sent_at is null;
alter table hx_notify_queue enable row level security;
revoke all on hx_notify_queue from anon, authenticated;

create table if not exists hx_notify_log (
  id          bigserial primary key,
  sent_at     timestamptz not null default now(),
  kind        text not null,            -- digest / alert / test
  email       text not null,
  subject     text not null default '',
  items       int not null default 0,
  status      text not null default 'sent',   -- sent / failed
  error       text not null default ''
);
alter table hx_notify_log enable row level security;
revoke all on hx_notify_log from anon, authenticated;
grant select on hx_notify_log to authenticated;
drop policy if exists hx_notify_log_read on hx_notify_log;
create policy hx_notify_log_read on hx_notify_log for select to authenticated using (hx_fl_is_admin());

create or replace function hx_notify_add() returns trigger
language plpgsql security definer set search_path = public as $$
declare m text; k text; t text; dt text := ''; pg text;
begin
  if tg_table_name = 'hx_holds' and tg_op = 'INSERT' then
    m := 'holds'; pg := 'holds'; k := 'hold'; t := 'Hold placed: ' || new.number || ' ' || coalesce(nullif(new.item, ''), new.tag, new.kind); dt := coalesce(new.reason, '');
  elsif tg_table_name = 'hx_tests' and new.status = 'Failed' and (tg_op = 'INSERT' or old.status is distinct from 'Failed') and not coalesce(new.voided, false) then
    m := 'testing'; pg := 'testing'; k := 'test_failed'; t := 'Test FAILED: ' || coalesce(nullif(new.batch_number, ''), new.tag) || coalesce(' ' || nullif(new.sku, ''), ''); dt := coalesce(nullif(new.result_notes, ''), new.lab_name, '');
  elsif tg_table_name = 'hx_deviations' and new.priority = 'critical' and (tg_op = 'INSERT' or old.priority is distinct from 'critical') then
    m := 'qms'; pg := 'qms'; k := 'deviation_critical'; t := 'Critical deviation ' || new.number || ': ' || new.title; dt := left(coalesce(new.description, ''), 300);
  elsif tg_table_name = 'hx_complaints' and new.priority = 'critical' and (tg_op = 'INSERT' or old.priority is distinct from 'critical') then
    m := 'complaints'; pg := 'complaints'; k := 'complaint_critical'; t := 'Critical complaint ' || new.number || ': ' || new.title; dt := left(coalesce(new.description, ''), 300);
  elsif tg_table_name = 'hx_recalls' and tg_op = 'INSERT' and new.kind in ('recall', 'withdrawal') then
    m := 'recall'; pg := 'recall'; k := 'recall'; t := initcap(new.kind) || ' started: ' || new.number || ' ' || coalesce(new.target_label, ''); dt := coalesce(new.reason, '');
  else
    return new;
  end if;
  insert into hx_notify_queue(state_id, license_id, module, kind, title, detail, page, ref) values (new.state_id, new.license_id, m, k, t, dt, pg, new.id);
  return new;
end $$;
drop trigger if exists hx_holds_notify on hx_holds;
create trigger hx_holds_notify after insert on hx_holds for each row execute function hx_notify_add();
drop trigger if exists hx_tests_notify on hx_tests;
create trigger hx_tests_notify after insert or update on hx_tests for each row execute function hx_notify_add();
drop trigger if exists hx_deviations_notify on hx_deviations;
create trigger hx_deviations_notify after insert or update on hx_deviations for each row execute function hx_notify_add();
drop trigger if exists hx_complaints_notify on hx_complaints;
create trigger hx_complaints_notify after insert or update on hx_complaints for each row execute function hx_notify_add();
drop trigger if exists hx_recalls_notify on hx_recalls;
create trigger hx_recalls_notify after insert on hx_recalls for each row execute function hx_notify_add();

-- ---------------- email: for the hendrix-notify function only (service role) ----------------
create or replace function hx_notify_service_only() returns void
language plpgsql stable as $$
begin
  -- the role of the request (security definer does not change it): the service role key, or the database owner in the SQL editor
  if not (coalesce(current_setting('role', true), '') = 'service_role'
          or coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role', '') = 'service_role'
          or (coalesce(current_setting('role', true), 'none') in ('none', '') and session_user in ('postgres', 'supabase_admin'))) then
    raise exception 'Only the hendrix-notify function can do this.';
  end if;
end $$;

-- act as one person inside this transaction (so access is checked exactly as for them)
create or replace function hx_as_user(p_uid uuid) returns void
language plpgsql as $$
begin
  perform set_config('request.jwt.claims', jsonb_build_object('sub', p_uid::text, 'role', 'authenticated', 'aal', 'aal2')::text, true);
  perform set_config('request.jwt.claim.sub', p_uid::text, true);
  perform set_config('test.uid', p_uid::text, true);
end $$;

-- the daily task list of every person who wants it
create or replace function hx_task_digest() returns jsonb
language plpgsql security definer set search_path = public as $$
declare p record; l record; t jsonb; lics jsonb; out jsonb := '[]'::jsonb;
  c0 text := current_setting('request.jwt.claims', true); s0 text := current_setting('request.jwt.claim.sub', true); u0 text := current_setting('test.uid', true);
begin
  perform hx_notify_service_only();
  for p in select * from hx_profiles where approved and coalesce(task_email, true) and coalesce(email, '') like '%@%' order by name loop
    perform hx_as_user(p.id); lics := '[]'::jsonb;
    for l in select x.id, x.name, x.license_number, s.name as state from hx_licenses x join hx_states s on s.id = x.state_id where x.active order by s.name, x.name loop
      if hx_lic_ok(l.id) then
        t := hx_my_tasks(l.id);
        if jsonb_array_length(t) > 0 then
          lics := lics || jsonb_build_object('license_id', l.id, 'license', l.name, 'license_number', l.license_number, 'state', l.state, 'tasks', t);
        end if;
      end if;
    end loop;
    if jsonb_array_length(lics) > 0 then out := out || jsonb_build_object('user_id', p.id, 'name', p.name, 'email', p.email, 'licenses', lics); end if;
  end loop;
  perform set_config('request.jwt.claims', coalesce(c0, ''), true); perform set_config('request.jwt.claim.sub', coalesce(s0, ''), true); perform set_config('test.uid', coalesce(u0, ''), true);
  return out;
end $$;

-- urgent alerts waiting, each with the people who have Full access to that area at that license
create or replace function hx_notify_pending() returns jsonb
language plpgsql security definer set search_path = public as $$
declare q record; p record; r jsonb; out jsonb := '[]'::jsonb; lic record;
  c0 text := current_setting('request.jwt.claims', true); s0 text := current_setting('request.jwt.claim.sub', true); u0 text := current_setting('test.uid', true);
begin
  perform hx_notify_service_only();
  for q in select * from hx_notify_queue where sent_at is null and created_at > now() - interval '3 days' order by id limit 200 loop
    r := '[]'::jsonb;
    for p in select * from hx_profiles where approved and coalesce(email, '') like '%@%' order by name loop
      perform hx_as_user(p.id);
      if hx_lic_ok(q.license_id) and hx_perm(q.module) >= 3 then r := r || jsonb_build_object('name', p.name, 'email', p.email); end if;
    end loop;
    select x.name, x.license_number, s.name as state into lic from hx_licenses x join hx_states s on s.id = x.state_id where x.id = q.license_id;
    out := out || jsonb_build_object('id', q.id, 'kind', q.kind, 'title', q.title, 'detail', q.detail, 'page', q.page, 'license', lic.name, 'license_number', lic.license_number,
                                     'state', lic.state, 'license_id', q.license_id, 'created_at', q.created_at, 'recipients', r);
  end loop;
  perform set_config('request.jwt.claims', coalesce(c0, ''), true); perform set_config('request.jwt.claim.sub', coalesce(s0, ''), true); perform set_config('test.uid', coalesce(u0, ''), true);
  return out;
end $$;

create or replace function hx_notify_sent(p_ids bigint[], p_log jsonb) returns int
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  perform hx_notify_service_only();
  update hx_notify_queue q set sent_at = now(),
    recipients = coalesce((select count(*) from jsonb_array_elements(coalesce(p_log, '[]'::jsonb)) e where e ->> 'kind' = 'alert' and (e ->> 'ref')::bigint = q.id and e ->> 'status' = 'sent'), 0)
    where q.id = any(coalesce(p_ids, '{}'));
  get diagnostics n = row_count;
  insert into hx_notify_log(kind, email, subject, items, status, error)
    select coalesce(e ->> 'kind', 'digest'), coalesce(e ->> 'email', ''), left(coalesce(e ->> 'subject', ''), 300), coalesce((e ->> 'items')::int, 0), coalesce(e ->> 'status', 'sent'), left(coalesce(e ->> 'error', ''), 500)
    from jsonb_array_elements(coalesce(p_log, '[]'::jsonb)) e;
  return n;
end $$;
revoke all on function hx_task_digest() from public, anon, authenticated;
revoke all on function hx_notify_pending() from public, anon, authenticated;
revoke all on function hx_notify_sent(bigint[], jsonb) from public, anon, authenticated;
revoke all on function hx_as_user(uuid) from public, anon, authenticated;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    execute 'grant execute on function hx_task_digest() to service_role';
    execute 'grant execute on function hx_notify_pending() to service_role';
    execute 'grant execute on function hx_notify_sent(bigint[], jsonb) to service_role';
    execute 'grant select, insert, update on hx_notify_queue, hx_notify_log to service_role';
  end if;
end $$;

-- admins: email status for Settings > Email and System Health
create or replace function hx_notify_status() returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only an admin can see the email status.'; end if;
  return jsonb_build_object(
    'pending_alerts', (select count(*) from hx_notify_queue where sent_at is null),
    'last_sent', (select max(sent_at) from hx_notify_log where status = 'sent'),
    'last_digest', (select max(sent_at) from hx_notify_log where kind = 'digest' and status = 'sent'),
    'failed_7d', (select count(*) from hx_notify_log where status = 'failed' and sent_at > now() - interval '7 days'),
    'sent_7d', (select count(*) from hx_notify_log where status = 'sent' and sent_at > now() - interval '7 days'),
    'people_off', (select count(*) from hx_profiles where approved and not coalesce(task_email, true)),
    'recent', coalesce((select jsonb_agg(x order by x.sent_at desc) from (select sent_at, kind, email, subject, items, status, error from hx_notify_log order by sent_at desc limit 15) x), '[]'::jsonb));
end $$;
revoke all on function hx_notify_status() from public, anon;
grant execute on function hx_notify_status() to authenticated;

-- System Health: step 39 in the steps list
create or replace function hx_health_extra() returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only an admin can run the system health check.'; end if;
  return jsonb_build_object(
    'step38', to_regclass('public.hx_esignatures') is not null,
    'step39', to_regprocedure('public.hx_my_tasks(text)') is not null,
    'admins_without_2fa', (select count(*) from hx_profiles where approved and role = 'admin' and not mfa_required),
    'esig_off_licenses', coalesce((select jsonb_agg(l.name) from hx_licenses l left join hx_license_settings s on s.license_id = l.id
                                    where l.active and s.license_id is not null and not s.esig_password), '[]'::jsonb),
    'signatures', (select count(*) from hx_esignatures),
    'email_last_sent', (select max(sent_at) from hx_notify_log where status = 'sent'),
    'email_pending_alerts', (select count(*) from hx_notify_queue where sent_at is null and created_at < now() - interval '1 hour'));
end $$;

notify pgrst, 'reload schema';
select 'Hendrix step 39 (My Tasks inbox + email alerts) installed' as result;

-- =====================================================================
-- EMAIL SET-UP (one time, after this file):
--  1. resend.com: add and verify your domain, create an API key.
--  2. Supabase > Edge Functions > Deploy new function "hendrix-notify" with hendrix-notify.ts
--     (turn OFF "Verify JWT" for it - it checks its own secret).
--  3. Edge Functions > Secrets: RESEND_API_KEY = the key, HX_MAIL_FROM = Hendrix QMS <qms@yourdomain.com>,
--     HX_CRON_SECRET = a long random text, HX_APP_URL = https://blfoxman.github.io/hendrix-qms/
--  4. Database > Extensions: enable pg_cron and pg_net. Then run (put your secret in both places):
--
--  select cron.schedule('hendrix-alerts', '*/10 * * * *', $c$
--    select net.http_post(url := 'https://bqrncllndvzbhmxanitq.supabase.co/functions/v1/hendrix-notify',
--      headers := '{"Content-Type":"application/json","x-hendrix-cron":"YOUR-SECRET"}'::jsonb, body := '{"mode":"alerts"}'::jsonb) $c$);
--  select cron.schedule('hendrix-daily-tasks', '30 11 * * 1-5', $c$
--    select net.http_post(url := 'https://bqrncllndvzbhmxanitq.supabase.co/functions/v1/hendrix-notify',
--      headers := '{"Content-Type":"application/json","x-hendrix-cron":"YOUR-SECRET"}'::jsonb, body := '{"mode":"digest"}'::jsonb) $c$);
--
--  (11:30 UTC = 7:30 am Eastern in summer, 6:30 am in winter. Alerts go out within 10 minutes.)
-- =====================================================================
