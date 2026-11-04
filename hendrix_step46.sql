-- =====================================================================
-- Hendrix QMS  -  Step 46: food safety records for the Missouri CFS checklist (21 CFR 117.10)
--
--   * Two new facility logs:
--       - GMP Hygiene Walk (gmp_walk, access "GMP Hygiene Walk" / logs_gmp):
--         the person in charge checks people (hair, jewelry, nails, garments,
--         gloves, illness, handwashing) and areas (no food or drink, hand sinks,
--         warewashing sink, chemicals, surfaces, pests, hoses) every shift.
--         A Fail needs a corrective action.
--       - Employee Illness and Exclusion Log (illness, access "Employee Illness
--         and Exclusion Log" / hr_health): who was excluded or restricted, the
--         reason category (no medical details), and the return to work.
--         PRIVATE: hr_health does not start with logs_, so "Facility Logs (all)"
--         never gives access to it; only that setting (or admin) does.
--   * hx_fl_types() lists every facility log type; hx_fl_valid_type uses it.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-45.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_fl_types() returns text[]
language sql immutable as $$
  select array['sanitation','waste','scale_calibration','security','security_inspection','pest','equipment',
               'temperature','environmental','maintenance_request','purchase_request','gmp_walk','illness'];
$$;
create or replace function hx_fl_valid_type(p_type text) returns boolean
language sql immutable as $$
  select coalesce(p_type,'') = any(hx_fl_types());
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
    when 'gmp_walk' then 'logs_gmp' when 'illness' then 'hr_health'
    else 'logs' end;
$$;
grant execute on function hx_fl_types() to authenticated;

-- the illness log has no QR form: entries come only from signed-in people with its own access (insert policy)
create or replace function hx_fl_private_guard() returns trigger
language plpgsql as $$
begin
  if new.log_type = 'illness' and coalesce(new.source, '') <> 'app' then
    raise exception 'The Employee Illness and Exclusion Log is filled in Hendrix only (no QR form).';
  end if;
  return new;
end $$;
drop trigger if exists hx_fl_private_guard on hx_facility_log;
create trigger hx_fl_private_guard before insert on hx_facility_log for each row execute function hx_fl_private_guard();
