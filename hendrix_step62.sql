-- =====================================================================
-- Hendrix QMS  -  Step 62: Management / HR company on each license
--
--   * Settings > General: "Management / HR company" - the company that employs the staff at this
--     license (e.g. HMBF Management in Missouri, HRMGMT10 in Michigan). The legal name stays the
--     license owner. Shown as "Employer" on the time clock sign-in sheet, the roll call and the
--     training records. Blank = not shown.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-61.
-- Safe to run more than once.
-- =====================================================================

alter table hx_license_settings add column if not exists hr_company text not null default '';
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'hx_license_settings_hr_chk') then
    alter table hx_license_settings add constraint hx_license_settings_hr_chk check (length(hr_company) <= 120);
  end if;
end $$;

notify pgrst, 'reload schema';
