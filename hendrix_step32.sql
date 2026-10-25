-- =====================================================================
-- Hendrix QMS  -  Step 32: Time Clock and Badges (from the Michigan app)
-- Badges (one per person, used at every license they have access to):
--   * photo (square, zoom / position), title on the card, ID number, and a
--     secret badge code printed as a QR code and a Code 128 barcode
--   * badges live in hx_badges, which no one reads directly: the badge code
--     never reaches other users (no "buddy punching" from a copied QR);
--     only Edit on Time Clock issues and prints badges (via functions)
--   * a lost badge is re-issued by Full access with a reason: the old QR and
--     barcode stop working at once
--   * anyone scanning a badge with a phone sees a verification page (name,
--     title, photo, valid or not) - nothing else
-- Time clock (same rules as the Michigan time clock):
--   * fixed 8 punches per person per day: Clock in, 1st break out / back,
--     2nd break out / back, 3rd break out / back, Clock out
--   * break limits 15 / 30 / 15 minutes; a late return is flagged with the
--     minutes over, for review on the sign-in sheet
--   * the kiosk (QR link per state + license, no login) takes a USB / Bluetooth
--     scanner or the tablet camera; the database picks the next punch, checks
--     the person has access to that license and ignores a double scan within
--     60 seconds
--   * punches are never edited: Full access voids a wrong punch or adds a
--     missed punch, always with a reason (audit trail)
-- Access module 'timeclock': View (sign-in sheet, on site now) / Edit
-- (badges) / Full (re-issue badges, fix punches).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-31.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_badges (
  profile_id     uuid primary key references hx_profiles(id),
  code           text not null unique,
  badge_no       text not null unique,
  title          text not null default '',
  photo          text,
  zoom           numeric not null default 1,
  pos_x          int not null default 0,
  pos_y          int not null default 0,
  active         boolean not null default true,
  issued_at      timestamptz not null default now(),
  issued_by      text not null default '',
  updated_at     timestamptz not null default now()
);
alter table hx_badges enable row level security;   -- no policies: read and written only through the functions below
revoke all on hx_badges from anon, authenticated;

create table if not exists hx_time_clock (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  profile_id    uuid not null references hx_profiles(id),
  person_name   text not null default '',
  event_type    text not null check (event_type in ('entry','break1_out','break1_in','break2_out','break2_in','break3_out','break3_in','clockout')),
  ts            timestamptz not null default now(),
  event_date    date not null,
  late          boolean not null default false,
  late_minutes  int,
  source        text not null default 'kiosk' check (source in ('kiosk','manual')),
  reason        text not null default '',
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_time_clock_day on hx_time_clock(license_id, event_date);
create index if not exists hx_time_clock_person on hx_time_clock(profile_id, event_date);

-- only voiding is allowed after a punch is written
create or replace function hx_time_clock_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Punches are never deleted. Void it with a reason.'; end if;
  if tg_op = 'INSERT' then
    if coalesce(current_setting('hx.internal', true), '') <> 'on' then raise exception 'Punches are recorded by the time clock kiosk (or as a missed punch by Full access).'; end if;
    return new;
  end if;
  if old.voided then raise exception 'This punch is void.'; end if;
  if not new.voided then raise exception 'A punch cannot be changed. Void it and add the right one.'; end if;
  if not hx_can('timeclock', 3, old.license_id) then raise exception 'Only Full access can void a punch.'; end if;
  if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a punch.'; end if;
  if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then
    raise exception 'Void a punch without changing anything else.';
  end if;
  new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
  return new;
end $$;
drop trigger if exists hx_time_clock_guard on hx_time_clock;
create trigger hx_time_clock_guard before insert or update or delete on hx_time_clock for each row execute function hx_time_clock_guard();
drop trigger if exists hx_time_clock_place on hx_time_clock;
create trigger hx_time_clock_place before insert or update on hx_time_clock for each row execute function hx_fl_guard();
drop trigger if exists hx_time_clock_audit on hx_time_clock;
create trigger hx_time_clock_audit after insert or update on hx_time_clock for each row execute function hx_audit();

alter table hx_time_clock enable row level security;
drop policy if exists hx_time_clock_read on hx_time_clock;
drop policy if exists hx_time_clock_update on hx_time_clock;
create policy hx_time_clock_read   on hx_time_clock for select to authenticated using (hx_can('timeclock',1,license_id) or profile_id::text = auth.uid()::text);
create policy hx_time_clock_update on hx_time_clock for update to authenticated using (hx_can('timeclock',3,license_id)) with check (hx_can('timeclock',3,license_id));
grant select, update on hx_time_clock to authenticated;

-- does this person work at this license?
create or replace function hx_person_at(p_profile uuid, p_lic text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from hx_profiles p where p.id = p_profile and coalesce(p.approved,false)
                 and (p.role = 'admin' or coalesce(array_length(p.license_ids,1),0) = 0 or p_lic = any(p.license_ids)));
$$;

create or replace function hx_badge_log(p_profile uuid, p_lic text, p_action text, p_reason text) returns void
language plpgsql security definer set search_path = public as $$
declare v_name text; v_state text;
begin
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  select state_id into v_state from hx_licenses where id = p_lic;
  insert into hx_audit_log(table_name, row_id, action, state_id, license_id, user_id, user_name, reason, changed, old_data, new_data)
  values ('hx_badges', p_profile::text, p_action, v_state, p_lic, auth.uid(), v_name, p_reason, null, null,
          (select jsonb_build_object('person', coalesce(nullif(name,''), email)) from hx_profiles where id = p_profile));
end $$;
revoke all on function hx_badge_log(uuid,text,text,text) from public, anon, authenticated;

-- people at a license with their badge (the code only for Edit, to print the card)
create or replace function hx_badge_roster(p_lic text) returns json
language plpgsql stable security definer set search_path = public as $$
declare v_edit boolean;
begin
  if not hx_can('timeclock', 1, p_lic) then raise exception 'No access to the time clock at this license.'; end if;
  v_edit := hx_can('timeclock', 2, p_lic);
  return coalesce((select json_agg(json_build_object('id', p.id, 'name', coalesce(nullif(p.name,''), p.email), 'email', p.email,
            'has_badge', b.profile_id is not null and b.active, 'badge_no', b.badge_no, 'title', b.title,
            'photo', b.photo, 'zoom', b.zoom, 'pos_x', b.pos_x, 'pos_y', b.pos_y, 'issued_at', b.issued_at, 'issued_by', b.issued_by,
            'code', case when v_edit then b.code end) order by lower(coalesce(nullif(p.name,''), p.email)))
     from hx_profiles p left join hx_badges b on b.profile_id = p.id
    where hx_person_at(p.id, p_lic)), '[]'::json);
end $$;

create or replace function hx_new_badge_code() returns text
language sql volatile set search_path = public as $$
  select upper(substr(md5(gen_random_uuid()::text || clock_timestamp()::text || random()::text), 1, 12));
$$;

create or replace function hx_badge_save(p_lic text, p_profile uuid, p_title text, p_photo text, p_zoom numeric, p_x int, p_y int) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_new boolean; v_no text; v_code text; n int := 0;
begin
  if not hx_can('timeclock', 2, p_lic) then raise exception 'Only Edit access on the time clock can make badges.'; end if;
  if not hx_person_at(p_profile, p_lic) then raise exception 'That person does not work at this license.'; end if;
  if p_photo is not null and length(p_photo) > 400000 then raise exception 'The photo is too large.'; end if;
  if p_photo is not null and p_photo !~ '^data:image/(jpeg|png|webp);base64,' then raise exception 'The photo must be an image.'; end if;
  v_new := not exists (select 1 from hx_badges where profile_id = p_profile);
  if v_new then
    loop
      n := n + 1; v_no := lpad((1000 + floor(random() * 9000))::int::text, 4, '0'); v_code := hx_new_badge_code();
      exit when not exists (select 1 from hx_badges where badge_no = v_no or code = v_code) or n > 50;
    end loop;
    insert into hx_badges(profile_id, code, badge_no, title, photo, zoom, pos_x, pos_y, issued_by)
    values (p_profile, v_code, v_no, left(coalesce(trim(p_title),''), 60), p_photo, coalesce(p_zoom,1), coalesce(p_x,0), coalesce(p_y,0), coalesce(hx_me(),''));
    perform hx_badge_log(p_profile, p_lic, 'INSERT', 'Badge issued');
  else
    update hx_badges set title = left(coalesce(trim(p_title),''), 60), photo = p_photo, zoom = coalesce(p_zoom,1), pos_x = coalesce(p_x,0), pos_y = coalesce(p_y,0), updated_at = now()
     where profile_id = p_profile;
    perform hx_badge_log(p_profile, p_lic, 'UPDATE', 'Badge photo / title updated');
  end if;
  return (select json_build_object('badge_no', badge_no, 'code', code) from hx_badges where profile_id = p_profile);
end $$;

-- lost or stolen badge: a new code, the old card stops working
create or replace function hx_badge_reissue(p_lic text, p_profile uuid, p_reason text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_code text;
begin
  if not hx_can('timeclock', 3, p_lic) then raise exception 'Only Full access can re-issue a badge.'; end if;
  if coalesce(trim(p_reason),'') = '' then raise exception 'A reason is required (for example: badge lost).'; end if;
  if not exists (select 1 from hx_badges where profile_id = p_profile) then raise exception 'This person has no badge yet.'; end if;
  loop v_code := hx_new_badge_code(); exit when not exists (select 1 from hx_badges where code = v_code); end loop;
  update hx_badges set code = v_code, active = true, issued_at = now(), issued_by = coalesce(hx_me(),''), updated_at = now() where profile_id = p_profile;
  perform hx_badge_log(p_profile, p_lic, 'UPDATE', 'Badge re-issued: ' || trim(p_reason));
  return (select json_build_object('badge_no', badge_no, 'code', code) from hx_badges where profile_id = p_profile);
end $$;

-- public badge check (someone scans a badge with their phone): name, title, photo only
create or replace function hx_badge_lookup(p_code text) returns json
language sql stable security definer set search_path = public as $$
  select json_build_object('name', coalesce(nullif(p.name,''), split_part(p.email,'@',1)), 'title', b.title, 'photo', b.photo, 'badge_no', b.badge_no,
                           'valid', b.active and coalesce(p.approved,false))
    from hx_badges b join hx_profiles p on p.id = b.profile_id
   where b.code = upper(trim(p_code));
$$;

-- the kiosk punch: next event in the day's sequence, break lateness, double-scan guard
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
    v_lim := case v_next when 'break2_in' then 30 else 15 end;
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

-- a missed punch added by Full access (reason required)
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
    v_lim := case p_event when 'break2_in' then 30 else 15 end;
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

revoke all on function hx_badge_roster(text) from public;
revoke all on function hx_badge_save(text,uuid,text,text,numeric,int,int) from public;
revoke all on function hx_badge_reissue(text,uuid,text) from public;
revoke all on function hx_badge_lookup(text) from public;
revoke all on function hx_kiosk_clock(text,text,text,date) from public;
revoke all on function hx_clock_fix(text,uuid,date,text,timestamptz,text) from public;
revoke all on function hx_person_at(uuid,text) from public;
revoke all on function hx_new_badge_code() from public;
grant execute on function hx_badge_roster(text) to authenticated;
grant execute on function hx_badge_save(text,uuid,text,text,numeric,int,int) to authenticated;
grant execute on function hx_badge_reissue(text,uuid,text) to authenticated;
grant execute on function hx_clock_fix(text,uuid,date,text,timestamptz,text) to authenticated;
grant execute on function hx_badge_lookup(text) to anon, authenticated;
grant execute on function hx_kiosk_clock(text,text,text,date) to anon, authenticated;

notify pgrst, 'reload schema';
