-- =====================================================================
-- Hendrix QMS  -  Step 37: System Health
-- One admin-only function, hx_system_health(), that checks the installation the
-- way an auditor's Installation Qualification (IQ) does:
--   * which database steps are installed (4 to 39)
--   * row level security switched on for every Hendrix table
--   * every Hendrix table written to the audit trail, and the audit trail locked
--   * the private file bucket exists and is not public
--   * people: admins, approved users, people waiting for approval, approved
--     people with no role and no access
--   * licenses missing their settings, operation or adopted standard
--   * the database clock and time zone
-- The app shows the result on Settings > System Health and can print it as IQ evidence.
-- Nothing is changed by this function. This step also adds the audit trail to
-- hx_qms_settings (the quality policy link), which step 30 left out.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-36.
-- Safe to run more than once.
-- =====================================================================

-- the quality policy link (step 30) was not written to the audit trail: add it
drop trigger if exists hx_qms_settings_audit on hx_qms_settings;
create trigger hx_qms_settings_audit after insert or update on hx_qms_settings for each row execute function hx_audit();

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
      (37,'System health','f','hx_system_health'),(38,'Security: e-signatures, two-step sign-in','t','hx_esignatures'),(39,'My Tasks and email alerts','t','hx_notify_queue')) as s(step, name, kind, obj)
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
                   and c.relname not in ('hx_audit_log', 'hx_badges', 'hx_training_keys', 'hx_sop_versions', 'hx_training_attempts', 'hx_notify_queue', 'hx_notify_log')
                   and not exists (select 1 from pg_trigger t join pg_proc p on p.oid = t.tgfoid where t.tgrelid = c.oid and not t.tgisinternal and p.proname = 'hx_audit')), '[]'::jsonb),
    'audit_by_design', '["hx_badges (badge codes are secret)", "hx_training_keys (answer keys are secret)", "hx_sop_versions (frozen copies, insert only)", "hx_training_attempts (quiz attempts, insert only)", "hx_notify_queue and hx_notify_log (email outbox and email log, written by the system)"]'::jsonb,
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
select 'Hendrix step 37 (System Health) installed' as result;
