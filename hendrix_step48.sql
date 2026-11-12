-- =====================================================================
-- Hendrix QMS  -  Step 48: fix "record new has no field priority"
--
--   The email-alert trigger from steps 39 and 43 (critical deviation or
--   complaint, failed test, hold, recall, urgent maintenance request) read
--   the deviation / complaint "priority" field while saving rows of OTHER
--   tables. Saving such a row then failed with:
--       record "new" has no field "priority"
--   Seen on: Batch Tracker > Submit for testing, entering a test result
--   (Passed, Pending ...), starting a mock recall.
--
--   hx_notify_row() checks the table first and reads only that table's
--   fields. All six alert triggers now use it. Same alerts as before.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-47.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_notify_row() returns trigger
language plpgsql security definer set search_path = public as $$
declare m text; k text; t text; dt text := ''; pg text;
begin
  if tg_table_name = 'hx_facility_log' then
    if tg_op <> 'INSERT' or new.log_type is distinct from 'maintenance_request' then return new; end if;
    if coalesce(new.data ->> 'priority', '') !~* '^urgent' then return new; end if;
    m := 'logs_maintenance'; pg := 'logs'; k := 'maintenance_urgent'; t := 'URGENT maintenance request: ' || left(coalesce(new.data ->> 'problem', new.item, ''), 120);
    dt := concat_ws(' · ', nullif(new.data ->> 'location', ''), nullif(new.data ->> 'equipment', ''), 'by ' || new.performed_by);
  elsif tg_table_name = 'hx_holds' then
    if tg_op <> 'INSERT' then return new; end if;
    m := 'holds'; pg := 'holds'; k := 'hold'; t := 'Hold placed: ' || new.number || ' ' || coalesce(nullif(new.item, ''), new.tag, new.kind); dt := coalesce(new.reason, '');
  elsif tg_table_name = 'hx_tests' then
    if new.status is distinct from 'Failed' or coalesce(new.voided, false) then return new; end if;
    if tg_op = 'UPDATE' then
      if old.status = 'Failed' then return new; end if;
    end if;
    m := 'testing'; pg := 'testing'; k := 'test_failed'; t := 'Test FAILED: ' || coalesce(nullif(new.batch_number, ''), new.tag) || coalesce(' ' || nullif(new.sku, ''), ''); dt := coalesce(nullif(new.result_notes, ''), new.lab_name, '');
  elsif tg_table_name = 'hx_deviations' then
    if new.priority is distinct from 'critical' then return new; end if;
    if tg_op = 'UPDATE' then
      if old.priority = 'critical' then return new; end if;
    end if;
    m := 'qms'; pg := 'qms'; k := 'deviation_critical'; t := 'Critical deviation ' || new.number || ': ' || new.title; dt := left(coalesce(new.description, ''), 300);
  elsif tg_table_name = 'hx_complaints' then
    if new.priority is distinct from 'critical' then return new; end if;
    if tg_op = 'UPDATE' then
      if old.priority = 'critical' then return new; end if;
    end if;
    m := 'complaints'; pg := 'complaints'; k := 'complaint_critical'; t := 'Critical complaint ' || new.number || ': ' || new.title; dt := left(coalesce(new.description, ''), 300);
  elsif tg_table_name = 'hx_recalls' then
    if tg_op <> 'INSERT' or new.kind not in ('recall', 'withdrawal') then return new; end if;
    m := 'recall'; pg := 'recall'; k := 'recall'; t := initcap(new.kind) || ' started: ' || new.number || ' ' || coalesce(new.target_label, ''); dt := coalesce(new.reason, '');
  else
    return new;
  end if;
  insert into hx_notify_queue(state_id, license_id, module, kind, title, detail, page, ref) values (new.state_id, new.license_id, m, k, t, dt, pg, new.id);
  return new;
end $$;

drop trigger if exists hx_holds_notify on hx_holds;
create trigger hx_holds_notify after insert on hx_holds for each row execute function hx_notify_row();
drop trigger if exists hx_tests_notify on hx_tests;
create trigger hx_tests_notify after insert or update on hx_tests for each row execute function hx_notify_row();
drop trigger if exists hx_deviations_notify on hx_deviations;
create trigger hx_deviations_notify after insert or update on hx_deviations for each row execute function hx_notify_row();
drop trigger if exists hx_complaints_notify on hx_complaints;
create trigger hx_complaints_notify after insert or update on hx_complaints for each row execute function hx_notify_row();
drop trigger if exists hx_recalls_notify on hx_recalls;
create trigger hx_recalls_notify after insert on hx_recalls for each row execute function hx_notify_row();
drop trigger if exists hx_facility_log_notify on hx_facility_log;
create trigger hx_facility_log_notify after insert on hx_facility_log for each row execute function hx_notify_row();

-- the old trigger function is no longer used by any trigger
drop function if exists hx_notify_add();

notify pgrst, 'reload schema';
select 'Hendrix step 48 (alert trigger fix: Submit for testing, test results, mock recall) installed' as result;
