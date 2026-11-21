-- =====================================================================
-- Hendrix QMS  -  Step 67: security questions for a forgotten password
--
--   * Every person sets 3 security questions (My account, or at sign-in until they do).
--     Only a one-way hash of each answer is kept, never the answer itself.
--   * Forgot your password? and no access to the email: answer the 3 questions and choose
--     a new password. 5 wrong tries per email per hour, then wait or ask an admin.
--   * A reset signs the person out everywhere and goes in the Audit Trail.
--     Two-step sign-in (authenticator) still applies at the next sign-in.
--
-- Run in the Hendrix Supabase project AFTER steps 1-66. Safe to run more than once.
-- =====================================================================

create table if not exists hx_security_answers (
  user_id     uuid primary key,
  questions   text[] not null,
  answers     text[] not null,          -- bcrypt hashes of the normalized answers, never the answers
  updated_at  timestamptz not null default now(),
  constraint hx_security_answers_three check (array_length(questions, 1) = 3 and array_length(answers, 1) = 3)
);
alter table hx_security_answers enable row level security;   -- no policies: only the functions below read or write it
revoke all on hx_security_answers from anon, authenticated;

create table if not exists hx_recovery_attempts (
  id     bigint generated always as identity primary key,
  email  text not null,
  at     timestamptz not null default now(),
  ok     boolean not null
);
create index if not exists hx_recovery_attempts_email on hx_recovery_attempts (email, at desc);
alter table hx_recovery_attempts enable row level security;
revoke all on hx_recovery_attempts from anon, authenticated;

-- answers compare without case and extra spaces ("  New  York " = "new york")
create or replace function hx_secq_norm(p text) returns text
language sql immutable as $$ select lower(regexp_replace(btrim(coalesce(p, '')), '\s+', ' ', 'g')) $$;

create or replace function hx_secq_list() returns text[]
language sql immutable as $$ select array[
  'What was the name of your first pet?',
  'In what city were you born?',
  'What is your mother''s maiden name?',
  'What was the make of your first car?',
  'What was the name of your elementary school?',
  'What street did you grow up on?',
  'What was your childhood nickname?',
  'What was the name of your favorite teacher?',
  'What was your first job?',
  'In what city did your parents meet?'] $$;

-- the signed-in person: which questions are set (never the answers)
create or replace function hx_my_security_questions() returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare r hx_security_answers;
begin
  if auth.uid() is null then raise exception 'Sign in first.'; end if;
  select * into r from hx_security_answers where user_id = auth.uid();
  if not found then return jsonb_build_object('set', false, 'questions', '[]'::jsonb); end if;
  return jsonb_build_object('set', true, 'questions', to_jsonb(r.questions), 'updated_at', r.updated_at);
end $$;
revoke all on function hx_my_security_questions() from public, anon;
grant execute on function hx_my_security_questions() to authenticated;

create or replace function hx_set_security_questions(p_questions text[], p_answers text[]) returns boolean
language plpgsql volatile security definer set search_path = public, extensions as $$
declare q text[] := '{}'; a text[] := '{}'; i int; v_name text;
begin
  if auth.uid() is null then raise exception 'Sign in first.'; end if;
  if coalesce(array_length(p_questions, 1), 0) <> 3 or coalesce(array_length(p_answers, 1), 0) <> 3 then
    raise exception 'Choose 3 questions and answer each one.';
  end if;
  for i in 1..3 loop
    q := q || btrim(regexp_replace(coalesce(p_questions[i], ''), '\s+', ' ', 'g'));
    if length(q[i]) < 8 then raise exception 'Question % is too short. Choose one from the list or write a full question.', i; end if;
    if length(q[i]) > 140 then raise exception 'Question % is too long (140 characters at most).', i; end if;
    if length(hx_secq_norm(p_answers[i])) < 2 then raise exception 'Answer question % (at least 2 characters).', i; end if;
    if length(p_answers[i]) > 100 then raise exception 'Answer % is too long (100 characters at most).', i; end if;
  end loop;
  if lower(q[1]) = lower(q[2]) or lower(q[1]) = lower(q[3]) or lower(q[2]) = lower(q[3]) then
    raise exception 'Choose 3 different questions.';
  end if;
  if hx_secq_norm(p_answers[1]) = hx_secq_norm(p_answers[2]) and hx_secq_norm(p_answers[2]) = hx_secq_norm(p_answers[3]) then
    raise exception 'Use a different answer for each question.';
  end if;
  for i in 1..3 loop a := a || extensions.crypt(hx_secq_norm(p_answers[i]), extensions.gen_salt('bf', 8)); end loop;
  insert into hx_security_answers (user_id, questions, answers, updated_at) values (auth.uid(), q, a, now())
  on conflict (user_id) do update set questions = excluded.questions, answers = excluded.answers, updated_at = now();
  select coalesce(nullif(name, ''), email) into v_name from hx_profiles where id = auth.uid();
  insert into hx_audit_log (table_name, row_id, action, user_id, user_name, reason, changed, new_data)
  values ('hx_security_answers', auth.uid()::text, 'UPDATE', auth.uid(), v_name, 'Security questions set', array['questions'], jsonb_build_object('questions', to_jsonb(q)));
  return true;
end $$;
revoke all on function hx_set_security_questions(text[], text[]) from public, anon;
grant execute on function hx_set_security_questions(text[], text[]) to authenticated;

-- sign-in screen, before sign-in: the questions for this email.
-- An email with no account (or no questions) always gets the same 3 questions from the list,
-- so the answer never tells anyone whether an email has a Hendrix account.
create or replace function hx_recovery_questions(p_email text) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare v_em text := lower(btrim(coalesce(p_email, ''))); v_uid uuid; r hx_security_answers; L text[] := hx_secq_list(); n int; h bigint;
begin
  if v_em !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'Enter the email you sign in with.'; end if;
  select id into v_uid from auth.users where lower(email) = v_em limit 1;
  if v_uid is not null then
    select * into r from hx_security_answers where user_id = v_uid;
    if found then return jsonb_build_object('questions', to_jsonb(r.questions)); end if;
  end if;
  n := array_length(L, 1);
  h := ('x' || substr(md5(v_em), 1, 7))::bit(28)::int;
  return jsonb_build_object('questions', jsonb_build_array(L[1 + h % n], L[1 + (h + 3) % n], L[1 + (h + 7) % n]));
end $$;
revoke all on function hx_recovery_questions(text) from public;
grant execute on function hx_recovery_questions(text) to anon, authenticated;

-- answer the 3 questions and choose a new password (no sign-in needed)
create or replace function hx_recover_with_answers(p_email text, p_answers text[], p_password text) returns jsonb
language plpgsql volatile security definer set search_path = public, extensions as $$
declare v_em text := lower(btrim(coalesce(p_email, ''))); v_uid uuid; r hx_security_answers; v_ok boolean := true; i int; v_fail int; v_banned boolean := false; v_name text;
begin
  if v_em !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'Enter the email you sign in with.'; end if;
  if length(coalesce(p_password, '')) < 8 then raise exception 'Use at least 8 characters for the new password.'; end if;
  if length(p_password) > 72 then raise exception 'The new password can have at most 72 characters.'; end if;
  delete from hx_recovery_attempts where at < now() - interval '30 days';
  select count(*) into v_fail from hx_recovery_attempts where email = v_em and not ok and at > now() - interval '1 hour';
  if v_fail >= 5 then
    return jsonb_build_object('ok', false, 'locked', true, 'left', 0,
      'error', 'Too many wrong answers. Wait an hour and try again, or ask a Hendrix admin for a temporary password.');
  end if;
  select id into v_uid from auth.users where lower(email) = v_em limit 1;
  if v_uid is not null then select * into r from hx_security_answers where user_id = v_uid; end if;
  if v_uid is null or r.user_id is null or coalesce(array_length(p_answers, 1), 0) <> 3 then
    v_ok := false;
  else
    for i in 1..3 loop
      if r.answers[i] is distinct from extensions.crypt(hx_secq_norm(p_answers[i]), r.answers[i]) then v_ok := false; end if;
    end loop;
  end if;
  insert into hx_recovery_attempts (email, ok) values (v_em, v_ok);
  if not v_ok then
    return jsonb_build_object('ok', false, 'locked', v_fail + 1 >= 5, 'left', greatest(0, 4 - v_fail),
      'error', case when v_fail + 1 >= 5 then 'Too many wrong answers. Wait an hour and try again, or ask a Hendrix admin for a temporary password.'
                    else 'Those answers do not match. Check the spelling and try again.' end);
  end if;
  begin execute 'select coalesce(banned_until > now(), false) from auth.users where id = $1' into v_banned using v_uid;
  exception when undefined_column then v_banned := false; end;
  if v_banned then
    return jsonb_build_object('ok', false, 'locked', false, 'left', 0, 'error', 'Your access to Hendrix was removed. Ask a system admin if this is a mistake.');
  end if;
  update auth.users set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf', 10)), updated_at = now() where id = v_uid;
  begin execute 'delete from auth.sessions where user_id = $1' using v_uid; exception when undefined_table then null; end;
  begin execute 'delete from auth.refresh_tokens where user_id = $1::text' using v_uid; exception when undefined_table or undefined_column then null; end;
  perform set_config('hx.reason', 'Password reset with security questions', true);
  update hx_profiles set must_change_password = false where id = v_uid and must_change_password;
  select coalesce(nullif(name, ''), email) into v_name from hx_profiles where id = v_uid;
  insert into hx_audit_log (table_name, row_id, action, user_id, user_name, reason, changed)
  values ('auth.users', v_uid::text, 'UPDATE', v_uid, v_name, 'Password reset with security questions', array['password']);
  return jsonb_build_object('ok', true);
end $$;
revoke all on function hx_recover_with_answers(text, text[], text) from public;
grant execute on function hx_recover_with_answers(text, text[], text) to anon, authenticated;

-- Team and Access: who has set their questions (true / false only)
create or replace function hx_security_questions_status() returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only a system admin can see this.'; end if;
  return coalesce((select jsonb_object_agg(user_id::text, true) from hx_security_answers), '{}'::jsonb);
end $$;
revoke all on function hx_security_questions_status() from public, anon;
grant execute on function hx_security_questions_status() to authenticated;

-- System Health: the two new tables are audited by design; steps 61-67 in the installed-steps list
create or replace function hx_system_health() returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare
  v_steps jsonb := '[]'::jsonb;
  r record;
  v_ok boolean;
begin
  if not hx_fl_is_admin() then raise exception 'Only an admin can run the system health check.'; end if;
  for r in select * from (values
      (4,'Facility logs','t','hx_log_lists'),(5,'Products','t','hx_skus'),(6,'Audit trail','t','hx_audit_log'),(7,'Batch Tracker','t','hx_batches'),
      (8,'Roles and access','t','hx_roles'),(9,'Testing','t','hx_tests'),(10,'Label templates','t','hx_label_templates'),(11,'Standards (CSQ)','t','hx_standards'),
      (12,'CSQ operations / label prints','t','hx_label_prints'),(13,'SOPs','t','hx_sops'),(14,'Deviations and CAPA','t','hx_deviations'),(15,'Training','t','hx_training_courses'),
      (16,'Suppliers','t','hx_suppliers'),(17,'Receiving, holds, shipping','t','hx_lots'),(18,'Traceability and recall','t','hx_recall_contacts'),(19,'Complaints and internal audits','t','hx_complaints'),
      (20,'Online courses','t','hx_training_keys'),(21,'License operation (scopes)','c','hx_licenses.operation'),(22,'Rulebook PDF import','t','hx_rule_sources'),(23,'Shared training','c','hx_training_courses.share_key'),
      (24,'Equipment and chemicals','t','hx_equipment'),(25,'Line clearance and rework','t','hx_line_clearances'),(26,'Facility tests','t','hx_env_points'),(27,'Cultivation','t','hx_grow_areas'),
      (28,'HACCP','t','hx_haccp_team'),(29,'Risk register and change control','t','hx_risks'),(30,'Org chart and objectives','t','hx_org_positions'),(31,'Management review and verification','t','hx_mgmt_reviews'),
      (32,'Time clock and badges','t','hx_badges'),(33,'Production planner','t','hx_production_plans'),(34,'Settings','t','hx_license_settings'),(36,'Line Map','f','hx_line_map'),
      (37,'System health','f','hx_system_health'),(38,'Security: e-signatures, two-step sign-in','t','hx_esignatures'),(39,'My Tasks and email alerts','t','hx_notify_queue'),(40,'Kiosks keep working offline','t','hx_kiosk_receipts'),(41,'METRC check','t','hx_metrc_snapshots'),(42,'Temporary passwords','f','hx_admin_set_password'),(43,'Maintenance and purchase requests, QR sign-in','f','hx_kiosk_log_add_user'),(44,'CSQ Program Overview online course','f','hx_course_cert_only'),(45,'New password after a reset','f','hx_set_own_password'),(46,'Food safety records (GMP walk, illness log)','f','hx_fl_types'),(47,'Batch Tracker tags from Receiving inventory','f','hx_batch_lots'),(48,'Alert trigger fix (Submit for testing, test results)','f','hx_notify_row'),(49,'Spanish SOPs and courses','c','hx_sops.es'),(50,'Paper SOP records (effective date, paper signatures)','f','hx_sop_paper_records'),(51,'Remove from Hendrix (people who left)','f','hx_admin_remove_user'),(52,'Cultivation Batch Tracker (test, package, ship)','t','hx_cul_settings'),(53,'Upload inventory from Excel','f','hx_lots_import'),(54,'Facility Map (zones, overlays, equipment pins)','t','hx_map_zones'),(55,'METRC tags on cannabis lots','f','hx_lot_set_tag'),(56,'Update inventory from Excel (counts)','t','hx_lot_counts'),(57,'Solventless batches and Rooms','t','hx_rooms'),(58,'Store complaint QR form (METRC tag check)','c','hx_complaints.tag_check'),(59,'Cultivation takeover (layout, harvest batches, METRC packages)','t','hx_harvests'),(60,'METRC inventory sync','t','hx_metrc_syncs'),(61,'Manufacturing Process, SKU options','t','hx_sku_options'),(62,'Management / HR company','c','hx_license_settings.hr_company'),(63,'Run status (save and come back)','c','hx_mp_runs.status'),(66,'Change your own email','f','hx_sync_my_email'),(67,'Security questions','f','hx_recover_with_answers')) as s(step, name, kind, obj)
  loop
    v_ok := case r.kind
      when 't' then to_regclass('public.' || r.obj) is not null
      when 'f' then exists (select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = r.obj)
      else exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = split_part(r.obj, '.', 1) and column_name = split_part(r.obj, '.', 2)) end;
    v_steps := v_steps || jsonb_build_object('step', r.step, 'name', r.name, 'ok', v_ok);
  end loop;

  return jsonb_build_object(
    'checked_at', now(),
    'db_time_zone', current_setting('TimeZone'),
    'steps', v_steps,
    'tables', (select count(*) from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relkind = 'r' and c.relname like 'hx\_%'),
    'rls_off', coalesce((select jsonb_agg(c.relname order by c.relname) from pg_class c join pg_namespace n on n.oid = c.relnamespace
                 where n.nspname = 'public' and c.relkind = 'r' and c.relname like 'hx\_%' and not c.relrowsecurity), '[]'::jsonb),
    'not_audited', coalesce((select jsonb_agg(c.relname order by c.relname) from pg_class c join pg_namespace n on n.oid = c.relnamespace
                 where n.nspname = 'public' and c.relkind = 'r' and c.relname like 'hx\_%'
                   and c.relname not in ('hx_audit_log', 'hx_badges', 'hx_training_keys', 'hx_sop_versions', 'hx_training_attempts', 'hx_notify_queue', 'hx_notify_log', 'hx_kiosk_receipts', 'hx_metrc_packages', 'hx_cul_packages', 'hx_metrc_syncs', 'hx_security_answers', 'hx_recovery_attempts')
                   and not exists (select 1 from pg_trigger t join pg_proc p on p.oid = t.tgfoid where t.tgrelid = c.oid and not t.tgisinternal and p.proname = 'hx_audit')), '[]'::jsonb),
    'audit_by_design', '["hx_badges (badge codes are secret)", "hx_training_keys (answer keys are secret)", "hx_sop_versions (frozen copies, insert only)", "hx_training_attempts (quiz attempts, insert only)", "hx_notify_queue and hx_notify_log (email outbox and email log, written by the system)", "hx_kiosk_receipts (receipts of items sent by offline kiosks; the records themselves are audited)", "hx_metrc_packages (copy of a METRC export; each upload is audited in hx_metrc_snapshots)", "hx_cul_packages (copy of METRC cultivation packages, changed only by the cultivation import)", "hx_metrc_syncs (log of METRC syncs; each change is a lot count in the Audit Trail)", "hx_security_answers (answer hashes are secret; each change is in the Audit Trail as Security questions set)", "hx_recovery_attempts (log of password reset tries, written by the system)"]'::jsonb,
    'audit_locked', exists (select 1 from pg_trigger t join pg_proc p on p.oid = t.tgfoid where t.tgrelid = to_regclass('public.hx_audit_log') and p.proname = 'hx_audit_lock'),
    'audit_rows', (select count(*) from hx_audit_log),
    'bucket', (select jsonb_build_object('exists', count(*) > 0, 'public', coalesce(bool_or(b.public), false)) from storage.buckets b where b.id = 'hendrix-files'),
    'people', (select jsonb_build_object(
        'admins', count(*) filter (where approved and role = 'admin'),
        'approved', count(*) filter (where approved),
        'waiting', count(*) filter (where not coalesce(approved, false)),
        'no_access', count(*) filter (where approved and role <> 'admin' and coalesce(array_length(role_ids, 1), 0) = 0 and coalesce(perms, '{}'::jsonb) = '{}'::jsonb))
      from hx_profiles),
    'licenses', coalesce((select jsonb_agg(jsonb_build_object('id', l.id, 'name', l.name, 'license_number', l.license_number,
        'settings', exists (select 1 from hx_license_settings s where s.license_id = l.id),
        'operation', coalesce(to_jsonb(l) ->> 'operation', ''),
        'standard', exists (select 1 from hx_license_standards ls where ls.license_id = l.id)) order by l.name)
      from hx_licenses l where l.active), '[]'::jsonb)
  );
end $$;

revoke all on function hx_system_health() from public, anon;
grant execute on function hx_system_health() to authenticated;

notify pgrst, 'reload schema';
