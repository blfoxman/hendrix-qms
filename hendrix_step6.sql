-- =====================================================================
-- Hendrix QMS  -  Step 6: Audit Trail
-- Who changed what, when, from what to what, and why.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-5.
-- Safe to run more than once. (If a step-5 table is missing, run step 5,
-- then run this file again so those tables are covered too.)
--
-- Rules built into the database:
--   * every insert, change and removal on every Hendrix table is written to
--     hx_audit_log with the old and new values, the user and the time
--   * the audit log is append-only: nobody can edit or delete it
--   * log RECORDS (facility logs, visitor log) can never be deleted; an entry
--     is VOIDED with a reason instead, and a void cannot be undone
--   * changing a record needs a "reason for change"; it is stored in the
--     audit log (a visitor signing out needs no reason)
--   * the signature, source, creator and creation time of a record are fixed
--   * only admins can read the audit log
-- =====================================================================

-- ---------- the audit log ----------
create table if not exists hx_audit_log (
  id          bigint generated always as identity primary key,
  at          timestamptz not null default now(),
  table_name  text not null,
  row_id      text,
  action      text not null,          -- INSERT | UPDATE | DELETE | VOID
  state_id    text,
  license_id  text,
  user_id     uuid,
  user_name   text,
  reason      text,
  changed     text[],
  old_data    jsonb,
  new_data    jsonb
);
create index if not exists hx_audit_log_row on hx_audit_log(table_name, row_id, at);
create index if not exists hx_audit_log_at  on hx_audit_log(at desc);
create index if not exists hx_audit_log_st  on hx_audit_log(state_id, at desc);

create or replace function hx_audit_lock() returns trigger
language plpgsql as $$
begin
  raise exception 'The audit trail cannot be changed or deleted.';
end $$;
drop trigger if exists hx_audit_log_lock on hx_audit_log;
create trigger hx_audit_log_lock before update or delete on hx_audit_log
  for each row execute function hx_audit_lock();

alter table hx_audit_log enable row level security;
drop policy if exists hx_audit_log_read on hx_audit_log;
create policy hx_audit_log_read on hx_audit_log for select to authenticated using (hx_fl_is_admin());
revoke all on hx_audit_log from anon, authenticated;
grant select on hx_audit_log to authenticated;

-- ---------- writes one audit row per change (runs as owner, so it always writes) ----------
create or replace function hx_audit() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  o jsonb; n jsonb; r jsonb; v_changed text[]; v_action text; v_uid uuid; v_name text; v_state text; v_lic text;
begin
  if tg_op <> 'INSERT' then o := to_jsonb(old) - 'signature' - 'edit_reason'; end if;
  if tg_op <> 'DELETE' then n := to_jsonb(new) - 'signature' - 'edit_reason'; end if;
  v_action := tg_op;
  if tg_op = 'UPDATE' then
    select array_agg(k order by k) into v_changed
      from jsonb_each(n) e(k, val)
     where k not in ('updated_at') and (o -> k) is distinct from val;
    if v_changed is null then
      return null;                       -- nothing really changed
    end if;
    if coalesce((n->>'voided')::boolean,false) and not coalesce((o->>'voided')::boolean,false) then
      v_action := 'VOID';
    end if;
  end if;
  r := coalesce(n, o);
  v_state := case tg_table_name when 'hx_states' then r->>'id' else r->>'state_id' end;
  v_lic   := case tg_table_name when 'hx_licenses' then r->>'id' else r->>'license_id' end;
  v_uid := auth.uid();
  if v_uid is not null then
    select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = v_uid::text;
  else
    v_name := case when coalesce(r->>'performed_by', r->>'visitor_name', '') <> ''
                   then 'QR kiosk (' || coalesce(nullif(r->>'performed_by',''), r->>'visitor_name') || ')'
                   else 'System' end;
  end if;
  insert into hx_audit_log(table_name, row_id, action, state_id, license_id, user_id, user_name, reason, changed, old_data, new_data)
  values (tg_table_name, r->>'id', v_action, v_state, v_lic, v_uid, v_name,
          nullif(current_setting('hx.reason', true), ''),
          v_changed,
          o,
          case when tg_op = 'DELETE' then null else n end);
  perform set_config('hx.reason', '', true);
  return null;
end $$;

-- ---------- records: no deletes, reason required, void instead ----------
create or replace function hx_record_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare a jsonb; b jsonb; k text;
begin
  if tg_op = 'DELETE' then
    raise exception 'Records cannot be deleted. Void the entry with a reason instead.';
  end if;
  if coalesce(old.voided, false) then
    raise exception 'This entry is void and cannot be changed.';
  end if;
  a := to_jsonb(old); b := to_jsonb(new);
  foreach k in array array['id','signature','source','created_by','created_at'] loop
    if (a -> k) is distinct from (b -> k) then
      raise exception 'The % of a record cannot be changed.', replace(k, '_', ' ');
    end if;
  end loop;

  -- voiding
  if coalesce(new.voided, false) then
    if coalesce(trim(new.void_reason), '') = '' then
      raise exception 'A reason is required to void an entry.';
    end if;
    if (b - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason')
       is distinct from (a - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason') then
      raise exception 'Void an entry without changing anything else.';
    end if;
    new.voided_at := now();
    new.voided_by := auth.uid();
    new.edit_reason := null;
    perform set_config('hx.reason', trim(new.void_reason), true);
    return new;
  end if;
  if (b ->> 'void_reason') is distinct from (a ->> 'void_reason') then
    raise exception 'The void reason cannot be changed.';
  end if;

  -- a visitor signing out needs no reason
  if tg_table_name = 'hx_visitor_log' and (a -> 'time_out') = 'null'::jsonb and (b -> 'time_out') <> 'null'::jsonb then
    perform set_config('hx.reason', coalesce(nullif(trim(new.edit_reason),''), 'Signed out'), true);
    new.edit_reason := null;
    return new;
  end if;

  if coalesce(trim(new.edit_reason), '') = '' then
    raise exception 'A reason for the change is required.';
  end if;
  perform set_config('hx.reason', trim(new.edit_reason), true);
  new.edit_reason := null;     -- never kept on the row, so every change must give its own reason
  return new;
end $$;

do $$
declare t text;
begin
  -- record columns
  foreach t in array array['hx_facility_log','hx_visitor_log'] loop
    if to_regclass('public.'||t) is null then
      raise notice 'Table % not found - skipped', t;
      continue;
    end if;
    execute format('alter table %I add column if not exists edit_reason text', t);
    execute format('alter table %I add column if not exists voided boolean not null default false', t);
    execute format('alter table %I add column if not exists void_reason text', t);
    execute format('alter table %I add column if not exists voided_by uuid', t);
    execute format('alter table %I add column if not exists voided_at timestamptz', t);
    execute format('drop trigger if exists %I on %I', t||'_record_guard', t);
    execute format('create trigger %I before update or delete on %I for each row execute function hx_record_guard()', t||'_record_guard', t);
  end loop;

  -- audit every Hendrix table
  foreach t in array array['hx_states','hx_licenses','hx_profiles','hx_rules','hx_visitor_log','hx_log_lists',
                           'hx_facility_log','hx_skus','hx_flavors','hx_formulations','hx_cost_library'] loop
    if to_regclass('public.'||t) is null then
      raise notice 'Table % not found - skipped (run its step, then run this file again)', t;
      continue;
    end if;
    execute format('drop trigger if exists %I on %I', t||'_audit', t);
    execute format('create trigger %I after insert or update or delete on %I for each row execute function hx_audit()', t||'_audit', t);
  end loop;
end $$;

-- old delete permissions on records are no longer used
drop policy if exists hx_facility_log_delete on hx_facility_log;

notify pgrst, 'reload schema';
