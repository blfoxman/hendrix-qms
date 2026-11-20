-- =====================================================================
-- Hendrix QMS  -  Step 63: Manufacturing Process runs get a status, and can be saved unfinished
--
--   * Status: In process -> Testing -> Passed / Failed -> Complete
--   * Until a run is Complete it can be saved with weights left blank (and with no product rows yet),
--     then opened again to enter the numbers. Changes to an open run need no reason - the audit
--     trail records "Saved while in process" or "Status: Testing -> Passed".
--   * Complete needs every weight in every part. Changing a Complete run needs a reason.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-62.
-- Safe to run more than once.
-- =====================================================================

alter table hx_mp_runs add column if not exists status text not null default 'in_process';
alter table hx_mp_runs add column if not exists completed_at timestamptz;
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'hx_mp_runs_status_chk') then
    alter table hx_mp_runs add constraint hx_mp_runs_status_chk check (status in ('in_process','testing','passed','failed','complete'));
  end if;
end $$;
create index if not exists hx_mp_runs_lic_status on hx_mp_runs(license_id, status);

create or replace function hx_mp_status_label(p text) returns text language sql immutable as $$
  select case p when 'in_process' then 'In process' when 'testing' then 'Testing' when 'passed' then 'Passed'
                when 'failed' then 'Failed' when 'complete' then 'Complete' else coalesce(p, '') end
$$;

-- rows of one part. p_strict (Complete): at least one row and every weight entered.
-- Otherwise rows may be missing and weights blank, but an entered weight must be a number.
create or replace function hx_mp_rows_ok(p_rows jsonb, p_what text, p_strict boolean, p_min int) returns void
language plpgsql immutable as $$
declare r jsonb;
begin
  if jsonb_typeof(p_rows) <> 'array' then raise exception '% is not valid.', p_what; end if;
  if jsonb_array_length(p_rows) < greatest(p_min, case when p_strict then 1 else 0 end) then raise exception '% needs at least one row.', p_what; end if;
  if jsonb_array_length(p_rows) > 200 then raise exception '% has too many rows.', p_what; end if;
  for r in select x from jsonb_array_elements(p_rows) x loop
    if jsonb_typeof(r) <> 'object' then raise exception '% has a row that is not valid.', p_what; end if;
    if coalesce(trim(r->>'item'), '') = '' then raise exception 'Every row in % needs an item.', p_what; end if;
    if coalesce(r->>'weight', '') = '' then
      if p_strict then raise exception 'Every row in % needs a weight before the run is Complete.', p_what; end if;
    elsif (r->>'weight') !~ '^[0-9]+(\.[0-9]+)?$' then
      raise exception 'A weight in % must be a number (0 or more).', p_what;
    end if;
    if length(coalesce(r->>'tag', '')) > 40 then raise exception 'A METRC tag in % is too long.', p_what; end if;
  end loop;
end $$;

create or replace function hx_mp_run_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s jsonb; i int := 0; n int; v_full boolean;
begin
  if tg_op = 'DELETE' then raise exception 'Runs cannot be deleted. Void the run with a reason instead.'; end if;
  if not exists (select 1 from hx_licenses where id = new.license_id and state_id = new.state_id) then raise exception 'The license is not in this state.'; end if;
  if tg_op = 'UPDATE' and coalesce(new.voided, false) then
    if not hx_can('batch', 3, new.license_id) then raise exception 'Full access to batches is needed to void a run.'; end if;
    return new;     -- the shared record guard checks the reason and that nothing else changed
  end if;
  if not hx_can('batch', 2, new.license_id) then raise exception 'Edit access to batches is needed to record a run.'; end if;
  new.status := coalesce(new.status, 'in_process');
  v_full := new.status = 'complete';
  perform hx_mp_rows_ok(new.materials, 'Part 1 (material used)', v_full, 1);
  if jsonb_typeof(new.produced) <> 'array' or jsonb_array_length(new.produced) = 0 then raise exception 'Part 2 (product produced) needs at least one row.'; end if;
  if jsonb_array_length(new.produced) > 10 then raise exception 'Too many additional processes.'; end if;
  for s in select x from jsonb_array_elements(new.produced) x loop
    i := i + 1;
    perform hx_mp_rows_ok(coalesce(s->'rows', '[]'::jsonb), 'Part ' || (i + 1) || ' (product produced)', v_full, 0);
    if s ? 'waste' and jsonb_typeof(s->'waste') = 'object' and coalesce(s->'waste'->>'weight', '') <> '' and (s->'waste'->>'weight') !~ '^[0-9]+(\.[0-9]+)?$' then
      raise exception 'The waste weight in Part % must be a number.', i + 1;
    end if;
  end loop;
  if tg_op = 'INSERT' then
    perform pg_advisory_xact_lock(hashtext('hx_mp_runs' || new.license_id));
    select count(*) + 1 into n from hx_mp_runs where license_id = new.license_id and run_date = new.run_date;
    new.number := 'PR-' || to_char(new.run_date, 'YYMMDD') || '-' || lpad(n::text, 2, '0');
    while exists (select 1 from hx_mp_runs where license_id = new.license_id and number = new.number) loop
      n := n + 1; new.number := 'PR-' || to_char(new.run_date, 'YYMMDD') || '-' || lpad(n::text, 2, '0');
    end loop;
    new.created_by := coalesce(hx_me(), ''); new.created_at := now();
    new.voided := false; new.void_reason := null; new.edit_reason := null;
    new.completed_at := case when v_full then now() else null end;
  else
    if new.license_id <> old.license_id then raise exception 'A run cannot move to another license.'; end if;
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    new.completed_at := case when not v_full then null when old.status = 'complete' then old.completed_at else now() end;
    -- an open run is a work in progress: no reason needed, the audit trail says what happened
    if old.status <> 'complete' and coalesce(trim(new.edit_reason), '') = '' then
      new.edit_reason := case when new.status <> old.status
        then 'Status: ' || hx_mp_status_label(old.status) || ' -> ' || hx_mp_status_label(new.status)
        else 'Saved while ' || lower(hx_mp_status_label(old.status)) end;
    end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_mp_runs_guard on hx_mp_runs;
create trigger hx_mp_runs_guard before insert or update or delete on hx_mp_runs for each row execute function hx_mp_run_guard();

notify pgrst, 'reload schema';
