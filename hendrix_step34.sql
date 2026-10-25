-- =====================================================================
-- Hendrix QMS  -  Step 34: Settings (per license)
-- Like the Black Fox Settings module, one place for each license's settings:
--   * General: business details for printouts (legal name, DBA, address,
--     phone, email, footer) and the company logo; Hendrix prints them at
--     the top of every record and on badges and the time clock kiosk
--   * Time clock: break limits (minutes for the 1st, 2nd and 3rd break);
--     the kiosk and missed punches use them to flag late returns
--   * Facility logs: after how many days without an entry a log is flagged
--     as not kept up (dashboard and Standards evidence)
--   * Review cycles: how often risks are reviewed by level
--   * where everything else is set (products, roles, pick lists, labels...)
-- Only Full access on 'settings' (or an admin) changes them; everyone at the
-- license reads them. Every change is in the audit trail.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-33.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_license_settings (
  license_id    text primary key references hx_licenses(id),
  state_id      text not null references hx_states(id),
  legal_name    text not null default '',
  dba           text not null default '',
  address       text not null default '',
  phone         text not null default '',
  email         text not null default '',
  print_footer  text not null default '',
  logo          text,
  break1_min    int not null default 15 check (break1_min between 1 and 240),
  break2_min    int not null default 30 check (break2_min between 1 and 240),
  break3_min    int not null default 15 check (break3_min between 1 and 240),
  log_due       jsonb not null default '{}'::jsonb,
  review_days   jsonb not null default '{}'::jsonb,
  updated_by    text not null default '',
  updated_at    timestamptz not null default now()
);

create or replace function hx_license_settings_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Settings are not deleted.'; end if;
  if not hx_can('settings', 3, new.license_id) then raise exception 'Only Full access on Settings can change the settings of this license.'; end if;
  if tg_op = 'UPDATE' and new.license_id <> old.license_id then raise exception 'Settings cannot move to another license.'; end if;
  if new.logo is not null and (length(new.logo) > 300000 or new.logo !~ '^data:image/(png|jpeg|webp|svg\+xml);base64,') then raise exception 'The logo must be a PNG, JPG, WEBP or SVG image under 200 KB.'; end if;
  if new.email <> '' and new.email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'Check the email address.'; end if;
  if jsonb_typeof(new.log_due) <> 'object' or jsonb_typeof(new.review_days) <> 'object' then raise exception 'Bad settings.'; end if;
  for k, v in select * from jsonb_each(new.log_due) loop
    if jsonb_typeof(v) <> 'number' or (v::text)::numeric < 1 or (v::text)::numeric > 400 then raise exception 'Log due days must be between 1 and 400.'; end if;
  end loop;
  for k, v in select * from jsonb_each(new.review_days) loop
    if jsonb_typeof(v) <> 'number' or (v::text)::numeric < 7 or (v::text)::numeric > 1095 then raise exception 'Review cycles must be between 7 and 1095 days.'; end if;
  end loop;
  new.updated_by := coalesce(hx_me(), ''); new.updated_at := now();
  perform set_config('hx.reason', 'Settings changed', true);
  return new;
end $$;
drop trigger if exists hx_license_settings_guard on hx_license_settings;
create trigger hx_license_settings_guard before insert or update or delete on hx_license_settings for each row execute function hx_license_settings_guard();
drop trigger if exists hx_license_settings_place on hx_license_settings;
create trigger hx_license_settings_place before insert or update on hx_license_settings for each row execute function hx_fl_guard();
drop trigger if exists hx_license_settings_audit on hx_license_settings;
create trigger hx_license_settings_audit after insert or update on hx_license_settings for each row execute function hx_audit();

alter table hx_license_settings enable row level security;
drop policy if exists hx_license_settings_read on hx_license_settings;
drop policy if exists hx_license_settings_insert on hx_license_settings;
drop policy if exists hx_license_settings_update on hx_license_settings;
create policy hx_license_settings_read   on hx_license_settings for select to authenticated using (hx_lic_ok(license_id));
create policy hx_license_settings_insert on hx_license_settings for insert to authenticated with check (hx_can('settings',3,license_id));
create policy hx_license_settings_update on hx_license_settings for update to authenticated using (hx_can('settings',3,license_id)) with check (hx_can('settings',3,license_id));
grant select, insert, update on hx_license_settings to authenticated;

-- break limit for the return punch ('break1_in' ...), from the license settings
create or replace function hx_break_limit(p_lic text, p_in text) returns int
language sql stable security definer set search_path = public as $$
  select coalesce((select case p_in when 'break1_in' then break1_min when 'break2_in' then break2_min else break3_min end from hx_license_settings where license_id = p_lic),
                  case p_in when 'break2_in' then 30 else 15 end);
$$;
revoke all on function hx_break_limit(text,text) from public, anon, authenticated;

-- kiosks show the company logo and name, and the time clock its break limits
create or replace function hx_kiosk_check(p_state text, p_lic text) returns json
language plpgsql stable security definer set search_path = public as $$
declare r json;
begin
  if coalesce(p_state,'') = '' or coalesce(p_lic,'') = '' then
    return null;
  end if;
  select json_build_object('id', l.id, 'name', l.name, 'license_number', l.license_number,
                           'state_id', s.id, 'state', s.name,
                           'display_name', coalesce(nullif(ls.dba,''), nullif(ls.legal_name,''), l.name), 'logo', ls.logo,
                           'breaks', json_build_array(coalesce(ls.break1_min,15), coalesce(ls.break2_min,30), coalesce(ls.break3_min,15)))
    into r
    from hx_licenses l join hx_states s on s.id = l.state_id left join hx_license_settings ls on ls.license_id = l.id
   where l.id = p_lic and l.state_id = p_state and l.active = true;
  return r;
end $$;
revoke all on function hx_kiosk_check(text,text) from public;
grant execute on function hx_kiosk_check(text,text) to anon, authenticated;

-- the time clock uses the license break limits (same as step 32 otherwise)
create or replace function hx_kiosk_clock(p_state text, p_lic text, p_code text, p_date date) returns json
language plpgsql volatile security definer set search_path = public as $$
declare b record; p record; v_last record; v_next text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int; v_now timestamptz := now();
  seq text[] := array['entry','break1_out','break1_in','break2_out','break2_in','break3_out','break3_in','clockout'];
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This kiosk is not linked to an active license in this state.'; end if;
  if p_date is null or p_date < current_date - 1 or p_date > current_date + 1 then raise exception 'The kiosk date is wrong. Check the tablet clock.'; end if;
  select * into b from hx_badges where code = upper(trim(coalesce(p_code,'')));
  if b.profile_id is null or not b.active then return json_build_object('error', 'Badge not recognized.'); end if;
  select * into p from hx_profiles where id = b.profile_id;
  if not hx_person_at(p.id, p_lic) then
    return json_build_object('error', 'Not authorized at this license.', 'name', coalesce(nullif(p.name,''), p.email), 'photo', b.photo, 'title', b.title);
  end if;
  perform pg_advisory_xact_lock(hashtext('clock' || p.id::text || p_lic));
  select * into v_last from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided order by ts desc limit 1;
  if v_last.id is not null and v_now - v_last.ts < interval '60 seconds' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_last.event_type, 'ts', v_last.ts, 'late', v_last.late, 'late_minutes', v_last.late_minutes, 'repeat', true);
  end if;
  if v_last.id is null then v_next := 'entry';
  elsif v_last.event_type = 'clockout' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'done', true);
  else v_next := seq[array_position(seq, v_last.event_type) + 1];
  end if;
  if v_next in ('break1_in','break2_in','break3_in') then
    v_lim := hx_break_limit(p_lic, v_next);
    select * into v_out from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided and event_type = replace(v_next, '_in', '_out') order by ts desc limit 1;
    if v_out.id is not null then
      v_el := extract(epoch from (v_now - v_out.ts)) / 60;
      v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end;
    end if;
  end if;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', 'Badge scan', true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, recorded_by)
  values ('tc-' || replace(gen_random_uuid()::text,'-',''), p_state, p_lic, p.id, coalesce(nullif(p.name,''), p.email), v_next, v_now, p_date, v_late, v_lm, 'kiosk', 'Kiosk');
  perform set_config('hx.internal', '', true);
  return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_next, 'ts', v_now, 'late', v_late, 'late_minutes', v_lm);
end $$;

create or replace function hx_clock_fix(p_lic text, p_profile uuid, p_date date, p_event text, p_ts timestamptz, p_reason text) returns text
language plpgsql volatile security definer set search_path = public as $$
declare v_state text; v_name text; v_id text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int;
begin
  if not hx_can('timeclock', 3, p_lic) then raise exception 'Only Full access can add a missed punch.'; end if;
  if coalesce(trim(p_reason),'') = '' then raise exception 'A reason is required.'; end if;
  if not hx_person_at(p_profile, p_lic) then raise exception 'That person does not work at this license.'; end if;
  if p_ts > now() then raise exception 'The time cannot be in the future.'; end if;
  if exists (select 1 from hx_time_clock where profile_id = p_profile and license_id = p_lic and event_date = p_date and event_type = p_event and not voided) then
    raise exception 'That punch is already recorded for the day. Void it first to replace it.';
  end if;
  if p_event in ('break1_in','break2_in','break3_in') then
    v_lim := hx_break_limit(p_lic, p_event);
    select * into v_out from hx_time_clock where profile_id = p_profile and license_id = p_lic and event_date = p_date and not voided and event_type = replace(p_event, '_in', '_out') limit 1;
    if v_out.id is not null then v_el := extract(epoch from (p_ts - v_out.ts)) / 60; v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end; end if;
  end if;
  select state_id into v_state from hx_licenses where id = p_lic;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id = p_profile;
  v_id := 'tc-' || replace(gen_random_uuid()::text,'-','');
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', 'Missed punch added: ' || trim(p_reason), true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, reason, recorded_by)
  values (v_id, v_state, p_lic, p_profile, v_name, p_event, p_ts, p_date, v_late, v_lm, 'manual', trim(p_reason), coalesce(hx_me(),''));
  perform set_config('hx.internal', '', true);
  return v_id;
end $$;

revoke all on function hx_kiosk_clock(text,text,text,date) from public;
revoke all on function hx_clock_fix(text,uuid,date,text,timestamptz,text) from public;
grant execute on function hx_kiosk_clock(text,text,text,date) to anon, authenticated;
grant execute on function hx_clock_fix(text,uuid,date,text,timestamptz,text) to authenticated;

notify pgrst, 'reload schema';
