-- =====================================================================
-- Hendrix QMS  -  Step 4: Facility Logs (matches Black Fox field-for-field)
-- Sanitation, Waste Destruction, Scale Calibration, Security Malfunction,
-- Security Equipment Inspection, Pest Control, Equipment Maintenance,
-- Temp / Humidity, Environmental Monitoring.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER
-- hendrix_setup.sql, hendrix_step2.sql and hendrix_step3.sql.
-- Safe to run more than once, and safe to run over the earlier step 4.
--
-- Walls built into the database (not just the app):
--   * every list item and every log entry carries BOTH state and license
--   * the license must belong to that state, or the save is refused
--   * entries can never be moved to another state or license
--   * a list item picked on an entry must belong to the same license
--   * kiosk (QR) saves need state + license + log + name + signature
-- =====================================================================

-- ---------- helpers ----------
create or replace function hx_fl_is_approved() returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from hx_profiles where id::text = auth.uid()::text and approved = true);
$$;

create or replace function hx_fl_is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from hx_profiles where id::text = auth.uid()::text and approved = true and role = 'admin');
$$;

create or replace function hx_fl_valid_type(p_type text) returns boolean
language sql immutable as $$
  select coalesce(p_type,'') in ('sanitation','waste','scale_calibration','security','security_inspection',
                                 'pest','equipment','temperature','environmental');
$$;

-- ---------- tables ----------
-- Admin-created lists per license. list_key = '<log>.<list>' (e.g. 'sanitation.areas',
-- 'security_inspection.cameras', 'scale_calibration.scales') or 'common.<list>' (e.g. 'common.shifts').
create table if not exists hx_log_lists (
  id          text primary key,
  state_id    text not null references hx_states(id) on delete cascade,
  license_id  text not null references hx_licenses(id) on delete cascade,
  list_key    text not null,
  name        text not null check (length(trim(name)) > 0),
  spec        jsonb not null default '{}'::jsonb,   -- extra details, e.g. scale serial/tolerance, room temp range
  sort        int  not null default 0,
  active      boolean not null default true,
  created_at  timestamptz not null default now()
);
create index if not exists hx_log_lists_lic on hx_log_lists(license_id, list_key);

-- One table for all logs; log_type says which one; every form field lives in data.
create table if not exists hx_facility_log (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  log_type      text not null,
  item_id       text,
  item          text not null default '',
  data          jsonb not null default '{}'::jsonb,
  result        text not null default '',
  performed_by  text not null default '',
  signature     text,
  source        text not null default 'app' check (source in ('app','kiosk')),
  created_by    uuid default auth.uid(),
  created_at    timestamptz not null default now()
);
create index if not exists hx_facility_log_lic on hx_facility_log(license_id, log_type, created_at desc);

-- (re)set the allowed values; NOT VALID keeps any test rows from the earlier step 4
alter table hx_facility_log drop constraint if exists hx_facility_log_log_type_check;
alter table hx_facility_log add constraint hx_facility_log_log_type_check check (hx_fl_valid_type(log_type)) not valid;
alter table hx_log_lists drop constraint if exists hx_log_lists_list_key_check;
alter table hx_log_lists add constraint hx_log_lists_list_key_check check (list_key ~ '^[a-z_]+\.[a-z_]+$') not valid;
drop function if exists hx_fl_list_key(text);

-- ---------- guards ----------
create or replace function hx_fl_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_state text;
begin
  if coalesce(new.state_id,'') = '' or coalesce(new.license_id,'') = '' then
    raise exception 'Every entry needs both a state and a license.';
  end if;
  if tg_op = 'UPDATE' and (new.state_id is distinct from old.state_id or new.license_id is distinct from old.license_id) then
    raise exception 'Records cannot be moved to another state or license.';
  end if;
  select state_id into v_state from hx_licenses where id = new.license_id;
  if v_state is null then
    raise exception 'Unknown license.';
  end if;
  if v_state <> new.state_id then
    raise exception 'This license does not belong to that state.';
  end if;
  return new;
end $$;

create or replace function hx_fl_item_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_name text; v_key text; v_lic text;
begin
  if tg_op = 'UPDATE' and new.log_type is distinct from old.log_type then
    raise exception 'The log type of an entry cannot be changed.';
  end if;
  if coalesce(new.item_id,'') <> '' and (tg_op = 'INSERT' or new.item_id is distinct from old.item_id) then
    select name, list_key, license_id into v_name, v_key, v_lic from hx_log_lists where id = new.item_id;
    if v_lic is null then
      raise exception 'That list item no longer exists.';
    end if;
    if v_lic <> new.license_id then
      raise exception 'That list item belongs to a different license.';
    end if;
    if split_part(v_key,'.',1) not in (new.log_type, 'common') then
      raise exception 'That list item does not belong to this log.';
    end if;
    new.item := v_name;   -- name comes from the database, not the client
  end if;
  return new;
end $$;

drop trigger if exists hx_log_lists_guard on hx_log_lists;
create trigger hx_log_lists_guard before insert or update on hx_log_lists
  for each row execute function hx_fl_guard();

drop trigger if exists hx_facility_log_guard on hx_facility_log;
create trigger hx_facility_log_guard before insert or update on hx_facility_log
  for each row execute function hx_fl_guard();

drop trigger if exists hx_facility_log_item_guard on hx_facility_log;
create trigger hx_facility_log_item_guard before insert or update on hx_facility_log
  for each row execute function hx_fl_item_guard();

-- ---------- row level security ----------
alter table hx_log_lists    enable row level security;
alter table hx_facility_log enable row level security;

drop policy if exists hx_log_lists_read   on hx_log_lists;
drop policy if exists hx_log_lists_insert on hx_log_lists;
drop policy if exists hx_log_lists_update on hx_log_lists;
drop policy if exists hx_log_lists_delete on hx_log_lists;
create policy hx_log_lists_read   on hx_log_lists for select to authenticated using (hx_fl_is_approved());
create policy hx_log_lists_insert on hx_log_lists for insert to authenticated with check (hx_fl_is_admin());
create policy hx_log_lists_update on hx_log_lists for update to authenticated using (hx_fl_is_admin()) with check (hx_fl_is_admin());
create policy hx_log_lists_delete on hx_log_lists for delete to authenticated using (hx_fl_is_admin());

drop policy if exists hx_facility_log_read   on hx_facility_log;
drop policy if exists hx_facility_log_insert on hx_facility_log;
drop policy if exists hx_facility_log_update on hx_facility_log;
drop policy if exists hx_facility_log_delete on hx_facility_log;
create policy hx_facility_log_read   on hx_facility_log for select to authenticated using (hx_fl_is_approved());
create policy hx_facility_log_insert on hx_facility_log for insert to authenticated with check (hx_fl_is_approved() and source = 'app');
create policy hx_facility_log_update on hx_facility_log for update to authenticated using (hx_fl_is_admin()) with check (hx_fl_is_admin());
create policy hx_facility_log_delete on hx_facility_log for delete to authenticated using (hx_fl_is_admin());

-- ---------- kiosk (QR) functions: no login, state + license both required ----------
create or replace function hx_kiosk_check(p_state text, p_lic text) returns json
language plpgsql stable security definer set search_path = public as $$
declare r json;
begin
  if coalesce(p_state,'') = '' or coalesce(p_lic,'') = '' then
    return null;
  end if;
  select json_build_object('id', l.id, 'name', l.name, 'license_number', l.license_number,
                           'state_id', s.id, 'state', s.name)
    into r
    from hx_licenses l join hx_states s on s.id = l.state_id
   where l.id = p_lic and l.state_id = p_state and l.active = true;
  return r;
end $$;

create or replace function hx_kiosk_log_setup(p_state text, p_lic text, p_type text) returns json
language plpgsql stable security definer set search_path = public as $$
declare v_lic json;
begin
  v_lic := hx_kiosk_check(p_state, p_lic);
  if v_lic is null then
    return null;
  end if;
  if not hx_fl_valid_type(p_type) then
    raise exception 'Unknown log type.';
  end if;
  return json_build_object(
    'license', v_lic,
    'items', coalesce((select json_agg(json_build_object('id', id, 'list_key', list_key, 'name', name, 'spec', spec) order by sort, name)
                         from hx_log_lists
                        where license_id = p_lic and active = true
                          and split_part(list_key,'.',1) in (p_type, 'common')), '[]'::json));
end $$;

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

revoke all on function hx_kiosk_check(text,text) from public;
revoke all on function hx_kiosk_log_setup(text,text,text) from public;
revoke all on function hx_kiosk_log_add(text,text,text,jsonb) from public;
grant execute on function hx_kiosk_check(text,text) to anon, authenticated;
grant execute on function hx_kiosk_log_setup(text,text,text) to anon, authenticated;
grant execute on function hx_kiosk_log_add(text,text,text,jsonb) to anon, authenticated;
grant execute on function hx_fl_is_approved() to authenticated;
grant execute on function hx_fl_is_admin() to authenticated;
grant execute on function hx_fl_valid_type(text) to anon, authenticated;

grant select, insert, update, delete on hx_log_lists, hx_facility_log to authenticated;

notify pgrst, 'reload schema';
