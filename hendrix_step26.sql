-- =====================================================================
-- Hendrix QMS  -  Step 26: Facility tests (air, water, soil, gases, swabs)
-- CSQ 2A.6 air, 2A.7 water (+ backflow), 2A.3 sanitation verification,
-- 3A.1.1 / 3A.1.9 / 3A.1.10 / 3A.1.12 cultivation air, soil and irrigation
-- water, 3B.1.3 / 3B.1.5 / 3B.1.7 / 3B.1.11 extraction water, gases and air,
-- 3C.1.5 manufacturing water.
--   * test points per license: what is tested (air, incoming water, process
--     water / ice, irrigation water, wastewater, soil / media, process gas,
--     surface swabs, backflow device), where, what for (analytes), limits,
--     how often, whether an ISO/IEC 17025 accredited lab is required
--   * results: sampled date and by whom, lab and accreditation, report file,
--     pass / fail, values; a failed result needs the corrective action and
--     can raise a deviation; next due date from the frequency
--   * results are never deleted (void with a reason, Full access)
-- Access module 'envtests': View / Edit (record results, add points) /
--   Full (void results, switch points off).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-25.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_env_points (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  name           text not null check (length(trim(name)) > 0),
  kind           text not null default 'water' check (kind in ('air','water','process_water','irrigation_water','wastewater','soil','process_gas','surface','backflow')),
  location       text not null default '',
  source         text not null default '',
  analytes       text not null default '',
  limits         text not null default '',
  frequency_days int not null default 365 check (frequency_days > 0),
  lab_required   boolean not null default true,
  active         boolean not null default true,
  sort           int not null default 0,
  notes          text not null default '',
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create index if not exists hx_env_points_lic on hx_env_points(license_id);

create table if not exists hx_env_tests (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  point_id       text not null references hx_env_points(id),
  sampled_on     date not null,
  sampled_by     text not null default '',
  lab_name       text not null default '',
  lab_accredited boolean not null default false,
  report_number  text not null default '',
  result         text not null check (result in ('pass','fail')),
  values_text    text not null default '',
  corrective     text not null default '',
  deviation_id   text,
  files          jsonb not null default '[]'::jsonb,
  recorded_by    text not null default '',
  created_at     timestamptz not null default now(),
  voided         boolean not null default false,
  void_reason    text,
  voided_at      timestamptz
);
create index if not exists hx_env_tests_point on hx_env_tests(point_id, sampled_on desc);

create or replace function hx_env_point_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_env_tests where point_id = old.id) then raise exception 'This test point has results. Switch it off instead of deleting it.'; end if;
    return old;
  end if;
  if tg_op = 'UPDATE' and old.active and not new.active and not hx_can('envtests', 3, new.license_id) then
    raise exception 'Only Full access can switch a test point off.';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_env_points_guard on hx_env_points;
create trigger hx_env_points_guard before insert or update or delete on hx_env_points for each row execute function hx_env_point_guard();
drop trigger if exists hx_env_points_place on hx_env_points;
create trigger hx_env_points_place before insert or update on hx_env_points for each row execute function hx_fl_guard();
drop trigger if exists hx_env_points_audit on hx_env_points;
create trigger hx_env_points_audit after insert or update or delete on hx_env_points for each row execute function hx_audit();

create or replace function hx_env_test_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record;
begin
  if tg_op = 'DELETE' then raise exception 'Test results are never deleted. Void the result with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This result is void.'; end if;
    if new.voided then
      if not hx_can('envtests', 3, old.license_id) then raise exception 'Only Full access can void a test result.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a test result.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a result without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'files' - 'deviation_id') is distinct from (to_jsonb(old) - 'files' - 'deviation_id') then
      raise exception 'A test result cannot be changed. Void it and record it again.';
    end if;
    return new;
  end if;
  select * into p from hx_env_points where id = new.point_id;
  if p.id is null or p.license_id <> new.license_id then raise exception 'That test point belongs to another license.'; end if;
  if new.sampled_on > current_date then raise exception 'The sample date cannot be in the future.'; end if;
  if p.lab_required then
    if coalesce(trim(new.lab_name), '') = '' then raise exception 'Enter the lab that tested the sample.'; end if;
    if not new.lab_accredited then raise exception 'This test must be done by an ISO/IEC 17025 accredited lab. Confirm the lab is accredited.'; end if;
  end if;
  if jsonb_array_length(new.files) = 0 and coalesce(trim(new.values_text), '') = '' then raise exception 'Attach the report or enter the results.'; end if;
  if new.result = 'fail' and coalesce(trim(new.corrective), '') = '' then raise exception 'A failed result needs the corrective action.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  perform set_config('hx.reason', 'Facility test ' || new.result || ': ' || p.name, true);
  return new;
end $$;
drop trigger if exists hx_env_tests_guard on hx_env_tests;
create trigger hx_env_tests_guard before insert or update or delete on hx_env_tests for each row execute function hx_env_test_guard();
drop trigger if exists hx_env_tests_place on hx_env_tests;
create trigger hx_env_tests_place before insert or update on hx_env_tests for each row execute function hx_fl_guard();
drop trigger if exists hx_env_tests_audit on hx_env_tests;
create trigger hx_env_tests_audit after insert or update on hx_env_tests for each row execute function hx_audit();

-- deviations can be raised from a failed facility test
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment','facility_test'));

alter table hx_env_points enable row level security;
alter table hx_env_tests enable row level security;
drop policy if exists hx_env_points_read on hx_env_points;
drop policy if exists hx_env_points_insert on hx_env_points;
drop policy if exists hx_env_points_update on hx_env_points;
drop policy if exists hx_env_points_delete on hx_env_points;
create policy hx_env_points_read   on hx_env_points for select to authenticated using (hx_can('envtests',1,license_id));
create policy hx_env_points_insert on hx_env_points for insert to authenticated with check (hx_can('envtests',2,license_id));
create policy hx_env_points_update on hx_env_points for update to authenticated using (hx_can('envtests',2,license_id)) with check (hx_can('envtests',2,license_id));
create policy hx_env_points_delete on hx_env_points for delete to authenticated using (hx_can('envtests',3,license_id));
drop policy if exists hx_env_tests_read on hx_env_tests;
drop policy if exists hx_env_tests_insert on hx_env_tests;
drop policy if exists hx_env_tests_update on hx_env_tests;
create policy hx_env_tests_read   on hx_env_tests for select to authenticated using (hx_can('envtests',1,license_id));
create policy hx_env_tests_insert on hx_env_tests for insert to authenticated with check (hx_can('envtests',2,license_id));
create policy hx_env_tests_update on hx_env_tests for update to authenticated using (hx_can('envtests',2,license_id)) with check (hx_can('envtests',2,license_id));
grant select, insert, update, delete on hx_env_points to authenticated;
grant select, insert, update on hx_env_tests to authenticated;

notify pgrst, 'reload schema';
