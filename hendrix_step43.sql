-- =====================================================================
-- Hendrix QMS  -  Step 43: Maintenance Requests, Purchase Requests, sign-in on QR forms
--
--   * Two new facility forms, each with its own QR code, access module and list:
--       - Maintenance Request (logs_maintenance): what is broken, where, priority,
--         production impact. Status: Open > In progress > Done (or Cancelled).
--       - Purchase Request (logs_purchase): what people need management to buy,
--         quantity, needed by, why. Status: Requested > Approved > Ordered >
--         Received (or Rejected).
--     Managers with Full access update the status (kept in the audit trail);
--     open requests are in their My Tasks; an urgent maintenance request is
--     emailed at once.
--   * QR forms need the person's own Hendrix sign-in, so every entry carries a
--     verified name (performed_by_id). Exceptions that stay open without sign-in:
--     Pest Control Log (outside pest company) and Security Malfunction Log.
--     Signed-in QR entries are saved by hx_kiosk_log_add_user (also when sent
--     later from a kiosk that had no internet: same one-time id and time rules).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-42.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_fl_valid_type(p_type text) returns boolean
language sql immutable as $$
  select coalesce(p_type,'') in ('sanitation','waste','scale_calibration','security','security_inspection',
                                 'pest','equipment','temperature','environmental','maintenance_request','purchase_request');
$$;
create or replace function hx_log_mod(p_type text) returns text
language sql immutable as $$
  select case p_type
    when 'sanitation' then 'logs_sanitation' when 'waste' then 'logs_waste'
    when 'scale_calibration' then 'logs_scale' when 'security' then 'logs_security'
    when 'security_inspection' then 'logs_security' when 'pest' then 'logs_pest'
    when 'equipment' then 'logs_equipment' when 'temperature' then 'logs_temp'
    when 'environmental' then 'logs_env' when 'visitor' then 'logs_visitor'
    when 'maintenance_request' then 'logs_maintenance' when 'purchase_request' then 'logs_purchase'
    else 'logs' end;
$$;
-- QR forms that work without signing in
create or replace function hx_kiosk_login_free(p_type text) returns boolean
language sql immutable as $$ select coalesce(p_type, '') in ('pest', 'security') $$;
grant execute on function hx_kiosk_login_free(text) to anon, authenticated;

alter table hx_facility_log add column if not exists performed_by_id uuid;

-- the open QR form (no sign-in): only the logs that do not need it
create or replace function hx_kiosk_log_add(p_state text, p_lic text, p_type text, p jsonb) returns text
language plpgsql volatile security definer set search_path = public as $$
declare v_id text;
begin
  if hx_kiosk_check(p_state, p_lic) is null then
    raise exception 'This QR code is not linked to an active license in this state.';
  end if;
  if not hx_fl_valid_type(p_type) then
    raise exception 'Unknown log type.';
  end if;
  if not hx_kiosk_login_free(p_type) then
    raise exception 'Sign in with your Hendrix account to fill this log.';
  end if;
  if coalesce(trim(p->>'performed_by'),'') = '' then
    raise exception 'Please enter your name.';
  end if;
  if coalesce(p->>'signature','') = '' then
    raise exception 'Please sign in the box.';
  end if;
  if length(p->>'signature') > 400000 or length(coalesce((p->'data')::text,'')) > 200000 then
    raise exception 'Entry is too large.';
  end if;
  v_id := 'fl-' || replace(gen_random_uuid()::text, '-', '');
  insert into hx_facility_log (id, state_id, license_id, log_type, item_id, item, data, result, performed_by, signature, source)
  values (v_id, p_state, p_lic, p_type,
          nullif(p->>'item_id',''),
          left(coalesce(p->>'item',''), 200),
          case when jsonb_typeof(p->'data') = 'object' then p->'data' else '{}'::jsonb end,
          left(coalesce(p->>'result',''), 20),
          left(trim(p->>'performed_by'), 120),
          p->>'signature',
          'kiosk');
  return v_id;
end $$;
revoke all on function hx_kiosk_log_add(text,text,text,jsonb) from public;
grant execute on function hx_kiosk_log_add(text,text,text,jsonb) to anon, authenticated;

-- kiosk items saved without internet (step 40): same rule
create or replace function hx_kiosk_sync(p_state text, p_lic text, p_kind text, p_client_id text, p_at timestamptz, p jsonb) returns jsonb
language plpgsql volatile security definer set search_path = public as $$
declare r jsonb; v_id text; l record; v_date date;
begin
  if coalesce(length(p_client_id), 0) not between 8 and 80 then raise exception 'Missing kiosk item id.'; end if;
  select result into r from hx_kiosk_receipts where client_id = p_client_id;
  if r is not null then return r || jsonb_build_object('duplicate', true); end if;
  begin
    if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This kiosk is not linked to an active license in this state.'; end if;
    if p_at is null or p_at > now() + interval '5 minutes' then raise exception 'The tablet clock is ahead of the real time: check the tablet clock.'; end if;
    if p_at < now() - interval '72 hours' then raise exception 'Saved more than 72 hours ago: too old to be added automatically. A manager can add it by hand with a reason.'; end if;
    if p_kind = 'clock' then
      v_date := coalesce(nullif(p->>'date','')::date, p_at::date);
      if v_date < (p_at - interval '36 hours')::date or v_date > (p_at + interval '36 hours')::date then raise exception 'The kiosk date is wrong. Check the tablet clock.'; end if;
      r := hx_clock_punch(p_state, p_lic, p->>'code', v_date, p_at, true)::jsonb;
    elsif p_kind = 'log' then
      if not hx_fl_valid_type(p->>'type') then raise exception 'Unknown log type.'; end if;
      if not hx_kiosk_login_free(p->>'type') then raise exception 'Sign in with your Hendrix account to fill this log.'; end if;
      if coalesce(trim(p->>'performed_by'),'') = '' then raise exception 'Please enter your name.'; end if;
      if coalesce(p->>'signature','') = '' then raise exception 'Please sign in the box.'; end if;
      if length(p->>'signature') > 400000 or length(coalesce((p->'data')::text,'')) > 200000 then raise exception 'Entry is too large.'; end if;
      v_id := 'fl-' || replace(gen_random_uuid()::text, '-', '');
      insert into hx_facility_log (id, state_id, license_id, log_type, item_id, item, data, result, performed_by, signature, source, performed_at, offline)
      values (v_id, p_state, p_lic, p->>'type', nullif(p->>'item_id',''), left(coalesce(p->>'item',''), 200),
              case when jsonb_typeof(p->'data') = 'object' then p->'data' else '{}'::jsonb end, left(coalesce(p->>'result',''), 20),
              left(trim(p->>'performed_by'), 120), p->>'signature', 'kiosk', p_at, true);
      r := jsonb_build_object('id', v_id);
    elsif p_kind = 'visitor' then
      select id, state_id, active into l from hx_licenses where id = p_lic;
      if length(trim(coalesce(p->>'visitor_name',''))) = 0 then raise exception 'Please enter your name.'; end if;
      if length(trim(coalesce(p->>'purpose',''))) = 0 then raise exception 'Please choose the purpose of your visit.'; end if;
      if length(coalesce(p->>'signature','')) < 50 then raise exception 'Please sign in the box.'; end if;
      if coalesce((p->>'gmp_ack')::boolean, false) is not true then raise exception 'Please confirm you have read and will follow the GMP rules.'; end if;
      if not (p ? 'ill') or jsonb_typeof(p->'ill') <> 'boolean' then raise exception 'Please answer the illness question.'; end if;
      v_id := 'vis-' || to_char(clock_timestamp(), 'YYMMDDHH24MISSMS') || substr(md5(random()::text), 1, 4);
      insert into hx_visitor_log(id, state_id, license_id, visitor_name, company, purpose, host, vehicle, signature, source, gmp_ack, ill, ack_at, time_in, offline)
      values (v_id, l.state_id, l.id, left(trim(p->>'visitor_name'),120), left(trim(coalesce(p->>'company','')),120), left(p->>'purpose',80),
              left(trim(coalesce(p->>'host','')),120), left(trim(coalesce(p->>'vehicle','')),30), p->>'signature', 'kiosk', true, (p->>'ill')::boolean, p_at, p_at, true);
      r := jsonb_build_object('id', v_id);
    else
      raise exception 'Unknown kiosk item.';
    end if;
  exception when others then
    r := jsonb_build_object('error', sqlerrm);
  end;
  insert into hx_kiosk_receipts(client_id, kind, license_id, made_at, result) values (p_client_id, coalesce(p_kind, ''), coalesce(p_lic, ''), coalesce(p_at, now()), r)
    on conflict (client_id) do nothing;
  return r;
end $$;
revoke all on function hx_kiosk_sync(text,text,text,text,timestamptz,jsonb) from public;
grant execute on function hx_kiosk_sync(text,text,text,text,timestamptz,jsonb) to anon, authenticated;

-- a QR form filled by a signed-in person (now or, with p_client_id / p_at, sent later by a kiosk that had no internet)
create or replace function hx_kiosk_log_add_user(p_state text, p_lic text, p_type text, p jsonb, p_client_id text default null, p_at timestamptz default null) returns jsonb
language plpgsql volatile security definer set search_path = public as $$
declare me record; v_id text; r jsonb; v_req boolean := p_type in ('maintenance_request', 'purchase_request'); v_data jsonb; v_res text;
begin
  if auth.uid() is null then raise exception 'Sign in with your Hendrix account first.'; end if;
  if p_client_id is not null then
    if length(p_client_id) not between 8 and 80 then raise exception 'Missing kiosk item id.'; end if;
    select result into r from hx_kiosk_receipts where client_id = p_client_id;
    if r is not null then return r || jsonb_build_object('duplicate', true); end if;
  end if;
  select * into me from hx_profiles where id::text = auth.uid()::text;
  if me.id is null or not coalesce(me.approved, false) then raise exception 'Your Hendrix account is not approved yet. Ask an admin.'; end if;
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This QR code is not linked to an active license in this state.'; end if;
  if not hx_lic_ok(p_lic) then raise exception 'Your account does not have access to this license. Ask an admin (Team and Access).'; end if;
  if not hx_fl_valid_type(p_type) then raise exception 'Unknown log type.'; end if;
  if not v_req and coalesce(p->>'signature', '') = '' then raise exception 'Please sign in the box.'; end if;
  if length(coalesce(p->>'signature', '')) > 400000 or length(coalesce((p->'data')::text, '')) > 200000 then raise exception 'Entry is too large.'; end if;
  if p_at is not null and p_at > now() + interval '5 minutes' then raise exception 'The tablet clock is ahead of the real time: check the tablet clock.'; end if;
  if p_at is not null and p_at < now() - interval '72 hours' then raise exception 'Saved more than 72 hours ago: too old to be added automatically.'; end if;
  v_data := case when jsonb_typeof(p->'data') = 'object' then p->'data' else '{}'::jsonb end;
  v_res := left(coalesce(p->>'result', ''), 20);
  if p_type = 'maintenance_request' then
    if coalesce(trim(v_data->>'problem'), '') = '' then raise exception 'Describe the problem.'; end if;
    v_data := v_data || jsonb_build_object('status', 'Open'); v_res := 'Open';
  elsif p_type = 'purchase_request' then
    if coalesce(trim(v_data->>'item_name'), '') = '' then raise exception 'Enter what needs to be purchased.'; end if;
    v_data := v_data || jsonb_build_object('status', 'Requested'); v_res := 'Requested';
  end if;
  v_id := 'fl-' || replace(gen_random_uuid()::text, '-', '');
  insert into hx_facility_log (id, state_id, license_id, log_type, item_id, item, data, result, performed_by, performed_by_id, signature, source, performed_at, offline)
  values (v_id, p_state, p_lic, p_type, nullif(p->>'item_id', ''), left(coalesce(p->>'item', ''), 200), v_data, v_res,
          left(coalesce(nullif(trim(me.name), ''), me.email), 120), me.id, nullif(p->>'signature', ''), 'kiosk', p_at, p_at is not null);
  r := jsonb_build_object('id', v_id);
  if p_client_id is not null then
    insert into hx_kiosk_receipts(client_id, kind, license_id, made_at, result) values (p_client_id, 'ulog', p_lic, coalesce(p_at, now()), r) on conflict (client_id) do nothing;
  end if;
  return r;
end $$;
revoke all on function hx_kiosk_log_add_user(text,text,text,jsonb,text,timestamptz) from public, anon;
grant execute on function hx_kiosk_log_add_user(text,text,text,jsonb,text,timestamptz) to authenticated;

-- My Tasks: open requests for the managers
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

  -- maintenance and purchase requests waiting for a manager (Full access on that log)
  if hx_perm('logs_maintenance') >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('maintenance_request', 'approve', 'logs',
             'Maintenance request: ' || left(coalesce(nullif(f.data ->> 'problem', ''), f.item, ''), 90),
             concat_ws(' · ', nullif(f.data ->> 'location', ''), nullif(f.data ->> 'priority', ''), f.result, 'by ' || f.performed_by),
             case when f.data ->> 'priority' ~* '^urgent' then f.created_at::date when f.data ->> 'priority' ~* '^high' then f.created_at::date + 2 else f.created_at::date + 7 end, f.id))
      from hx_facility_log f where f.license_id = p_lic and f.log_type = 'maintenance_request' and not f.voided and f.result in ('Open', 'In progress')), '[]'::jsonb);
  end if;
  if hx_perm('logs_purchase') >= 3 then
    v := v || coalesce((select jsonb_agg(hx_task('purchase_request', 'approve', 'logs',
             (case f.result when 'Approved' then 'Order: ' when 'Ordered' then 'Receive: ' else 'Purchase request: ' end) || left(coalesce(nullif(f.data ->> 'item_name', ''), f.item, ''), 90),
             concat_ws(' · ', nullif(trim(coalesce(f.data ->> 'quantity', '') || ' ' || coalesce(f.data ->> 'unit', '')), ''), f.result, 'by ' || f.performed_by),
             case when coalesce(f.data ->> 'needed_by', '') ~ '^\d{4}-\d{2}-\d{2}$' then (f.data ->> 'needed_by')::date end, f.id))
      from hx_facility_log f where f.license_id = p_lic and f.log_type = 'purchase_request' and not f.voided and f.result in ('Requested', 'Approved', 'Ordered')), '[]'::jsonb);
  end if;

  -- overdue first, then by due date, then the rest
  return coalesce((select jsonb_agg(t order by (t ->> 'overdue')::boolean desc, (t ->> 'due') nulls last, t ->> 'title') from jsonb_array_elements(v) t), '[]'::jsonb);
end $$;
revoke all on function hx_my_tasks(text) from public, anon;
grant execute on function hx_my_tasks(text) to authenticated;

-- urgent maintenance request: emailed at once to people with Full access on Maintenance Requests
create or replace function hx_notify_add() returns trigger
language plpgsql security definer set search_path = public as $$
declare m text; k text; t text; dt text := ''; pg text;
begin
  if tg_table_name = 'hx_facility_log' then
    if tg_op = 'INSERT' and new.log_type = 'maintenance_request' and coalesce(new.data ->> 'priority', '') ~* '^urgent' then
      m := 'logs_maintenance'; pg := 'logs'; k := 'maintenance_urgent'; t := 'URGENT maintenance request: ' || left(coalesce(new.data ->> 'problem', new.item, ''), 120);
      dt := concat_ws(' · ', nullif(new.data ->> 'location', ''), nullif(new.data ->> 'equipment', ''), 'by ' || new.performed_by);
    else
      return new;
    end if;
  elsif tg_table_name = 'hx_holds' and tg_op = 'INSERT' then
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
drop trigger if exists hx_facility_log_notify on hx_facility_log;
create trigger hx_facility_log_notify after insert on hx_facility_log for each row execute function hx_notify_add();

notify pgrst, 'reload schema';
select 'Hendrix step 43 (maintenance and purchase requests, sign-in on QR forms) installed' as result;
