-- =====================================================================
-- Hendrix QMS  -  Step 40: kiosks keep working without internet
--
--   The time clock, facility log and visitor kiosks save scans and entries on
--   the tablet when the internet is down, and send them when it is back
--   (hx_kiosk_sync). Every offline record keeps the real time it was made on
--   the tablet and is marked "offline" with the time it reached Hendrix:
--     * time clock: the punch time is the scan time (late breaks are worked
--       out from it); offline = true, synced_at = when it arrived;
--     * facility logs: performed_at = when it was done on the tablet;
--     * visitor log: time in = when the visitor signed in on the tablet.
--   Each saved item has a one-time id from the tablet, so sending it twice
--   (a dropped connection) never makes two records. Scans older than 72 hours
--   or in the future are refused.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-39.
-- Safe to run more than once.
-- =====================================================================

alter table hx_time_clock add column if not exists offline boolean not null default false;
alter table hx_time_clock add column if not exists synced_at timestamptz;
alter table hx_facility_log add column if not exists performed_at timestamptz;
alter table hx_facility_log add column if not exists offline boolean not null default false;
alter table hx_visitor_log add column if not exists offline boolean not null default false;

-- one row per item a tablet sent: the same item sent again gets the same answer
create table if not exists hx_kiosk_receipts (
  client_id    text primary key,
  kind         text not null,
  license_id   text not null,
  made_at      timestamptz not null,
  result       jsonb not null,
  received_at  timestamptz not null default now()
);
alter table hx_kiosk_receipts enable row level security;
revoke all on hx_kiosk_receipts from anon, authenticated;

-- one badge scan at a given time (shared by the live kiosk and the offline queue)
create or replace function hx_clock_punch(p_state text, p_lic text, p_code text, p_date date, p_at timestamptz, p_offline boolean) returns json
language plpgsql volatile security definer set search_path = public as $$
declare b record; p record; v_last record; v_next text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int := 0;
  seq text[] := array['entry','break1_out','break1_in','break2_out','break2_in','break3_out','break3_in','clockout'];
begin
  select * into b from hx_badges where code = upper(trim(coalesce(p_code,'')));
  if b.profile_id is null or not b.active then return json_build_object('error', 'Badge not recognized.'); end if;
  select * into p from hx_profiles where id = b.profile_id;
  if not hx_person_at(p.id, p_lic) then
    return json_build_object('error', 'Not authorized at this license.', 'name', coalesce(nullif(p.name,''), p.email), 'photo', b.photo, 'title', b.title);
  end if;
  perform pg_advisory_xact_lock(hashtext('clock' || p.id::text || p_lic));
  -- a second scan within 60 seconds of another one is the same scan
  select * into v_last from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided
    and ts between p_at - interval '60 seconds' and p_at + interval '60 seconds' order by ts desc limit 1;
  if v_last.id is not null then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_last.event_type, 'ts', v_last.ts, 'late', v_last.late, 'late_minutes', v_last.late_minutes, 'repeat', true);
  end if;
  select * into v_last from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided and ts < p_at order by ts desc limit 1;
  if v_last.id is null then v_next := 'entry';
  elsif v_last.event_type = 'clockout' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'done', true);
  else v_next := seq[array_position(seq, v_last.event_type) + 1];
  end if;
  if exists (select 1 from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided and event_type = v_next) then
    return json_build_object('error', 'This punch (' || replace(v_next, '_', ' ') || ') is already recorded for the day.', 'name', coalesce(nullif(p.name,''), p.email), 'photo', b.photo, 'title', b.title);
  end if;
  if v_next in ('break1_in','break2_in','break3_in') then
    v_lim := hx_break_limit(p_lic, v_next);
    select * into v_out from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided and event_type = replace(v_next, '_in', '_out') order by ts desc limit 1;
    if v_out.id is not null then
      v_el := extract(epoch from (p_at - v_out.ts)) / 60;
      v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end;
    end if;
  end if;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', case when p_offline then 'Badge scan (saved on the kiosk while offline)' else 'Badge scan' end, true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, recorded_by, offline, synced_at)
  values ('tc-' || replace(gen_random_uuid()::text,'-',''), p_state, p_lic, p.id, coalesce(nullif(p.name,''), p.email), v_next, p_at, p_date, v_late, v_lm, 'kiosk',
          case when p_offline then 'Kiosk (offline)' else 'Kiosk' end, p_offline, case when p_offline then now() end);
  perform set_config('hx.internal', '', true);
  return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_next, 'ts', p_at, 'late', v_late, 'late_minutes', v_lm);
end $$;
revoke all on function hx_clock_punch(text,text,text,date,timestamptz,boolean) from public, anon, authenticated;

-- the live kiosk: same as step 34, now through hx_clock_punch
create or replace function hx_kiosk_clock(p_state text, p_lic text, p_code text, p_date date) returns json
language plpgsql volatile security definer set search_path = public as $$
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This kiosk is not linked to an active license in this state.'; end if;
  if p_date is null or p_date < current_date - 1 or p_date > current_date + 1 then raise exception 'The kiosk date is wrong. Check the tablet clock.'; end if;
  return hx_clock_punch(p_state, p_lic, p_code, p_date, now(), false);
end $$;
revoke all on function hx_kiosk_clock(text,text,text,date) from public;
grant execute on function hx_kiosk_clock(text,text,text,date) to anon, authenticated;

-- an item saved on a kiosk while offline: kind 'clock' | 'log' | 'visitor'
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

-- System Health and the step list: offline kiosks installed
create or replace function hx_health_extra() returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only an admin can run the system health check.'; end if;
  return jsonb_build_object(
    'step38', to_regclass('public.hx_esignatures') is not null,
    'step39', to_regprocedure('public.hx_my_tasks(text)') is not null,
    'step40', to_regclass('public.hx_kiosk_receipts') is not null,
    'admins_without_2fa', (select count(*) from hx_profiles where approved and role = 'admin' and not mfa_required),
    'esig_off_licenses', coalesce((select jsonb_agg(l.name) from hx_licenses l left join hx_license_settings s on s.license_id = l.id
                                    where l.active and s.license_id is not null and not s.esig_password), '[]'::jsonb),
    'signatures', (select count(*) from hx_esignatures),
    'email_last_sent', (select max(sent_at) from hx_notify_log where status = 'sent'),
    'email_pending_alerts', (select count(*) from hx_notify_queue where sent_at is null and created_at < now() - interval '1 hour'),
    'kiosk_offline_7d', (select count(*) from hx_kiosk_receipts where received_at > now() - interval '7 days'),
    'kiosk_refused_7d', (select count(*) from hx_kiosk_receipts where received_at > now() - interval '7 days' and result ? 'error'));
end $$;

notify pgrst, 'reload schema';
select 'Hendrix step 40 (kiosks keep working without internet) installed' as result;
