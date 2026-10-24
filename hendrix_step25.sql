-- =====================================================================
-- Hendrix QMS  -  Step 25: Line clearance and Rework
-- Line clearance / pre-operational inspection (CSQ 2A.12.3, 3B.1.2):
--   * numbered LC-YYYY-###, linked to a batch (or a room / line), the
--     equipment used from the Equipment register, a checklist (previous
--     product and labels removed, cleaned and sanitized, equipment in date,
--     right materials staged, cGMP dress, no foreign matter, tools counted;
--     extraction adds gas detection / fire safety and ventilation)
--   * every failed item needs the problem and its correction; the line is
--     cleared only when every failure was corrected
--   * the database refuses "cleared" while any equipment used is out of
--     service, retired, or past its calibration due date
-- Rework (CSQ 2A.12.5, 3B.1.12 e):
--   * numbered RW-YYYY-###, dated and tagged, from a batch, a hold or other
--   * inspected and analyzed before use (pass / fail); approved by Full
--     access, confirmed like-to-like; its expiry must not be before the
--     expiry of the product it goes into; used in a target batch (traceable)
--     or destroyed with a reason
-- Access modules 'lineclear' and 'rework': View / Edit (record) /
--   Full (void line clearances; approve rework, destroy).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-24.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_line_clearances (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  number        text not null default '',
  batch_id      text references hx_batches(id),
  batch_label   text not null default '',
  batch_type    text not null default '',
  area          text not null default '',
  equipment_ids text[] not null default '{}',
  checks        jsonb not null default '{}'::jsonb,
  issues        text not null default '',
  corrections   text not null default '',
  result        text not null default 'cleared' check (result in ('cleared','not_cleared')),
  checked_by    text not null default '',
  verified_by   text not null default '',
  deviation_id  text,
  checked_at    timestamptz not null default now(),
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create unique index if not exists hx_line_clearances_number on hx_line_clearances(license_id, number);
create index if not exists hx_line_clearances_batch on hx_line_clearances(batch_id);

create or replace function hx_line_clearance_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v jsonb; n_fail int := 0; n_unfixed int := 0; e record; v_bad text := '';
begin
  if tg_op = 'DELETE' then raise exception 'Line clearances are never deleted. Void it with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This line clearance is void.'; end if;
    if new.voided then
      if not hx_can('lineclear', 3, old.license_id) then raise exception 'Only Full access can void a line clearance.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a line clearance.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then
        raise exception 'Void a line clearance without changing anything else.';
      end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'deviation_id') is distinct from (to_jsonb(old) - 'deviation_id') then
      raise exception 'A line clearance cannot be changed. Void it and record a new one.';
    end if;
    return new;
  end if;
  new.number := hx_next_number('hx_line_clearances', new.license_id, 'LC');
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.checked_at := now();
  new.voided := false; new.void_reason := null; new.voided_at := null;
  if coalesce(trim(new.checked_by), '') = '' then raise exception 'Enter who did the inspection.'; end if;
  if new.batch_id is not null then
    if not exists (select 1 from hx_batches b where b.id = new.batch_id and b.license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
  elsif coalesce(trim(new.area), '') = '' then
    raise exception 'Choose the batch or enter the room / line inspected.';
  end if;
  if jsonb_typeof(new.checks) <> 'object' or new.checks = '{}'::jsonb then raise exception 'Complete the checklist.'; end if;
  for k, v in select * from jsonb_each(new.checks) loop
    if v->>'r' not in ('pass','fail','na') then raise exception 'Answer every item on the checklist.'; end if;
    if v->>'r' = 'fail' then n_fail := n_fail + 1; if coalesce((v->>'fixed')::boolean, false) is not true then n_unfixed := n_unfixed + 1; end if; end if;
  end loop;
  if n_fail > 0 and (coalesce(trim(new.issues), '') = '' or coalesce(trim(new.corrections), '') = '') then
    raise exception 'Describe each problem found and the correction or corrective action.';
  end if;
  for e in select * from hx_equipment where id = any(new.equipment_ids) loop
    if e.license_id <> new.license_id then raise exception 'Equipment % belongs to another license.', e.number; end if;
    if e.status <> 'in_service' then v_bad := v_bad || e.number || ' ' || e.name || ' is ' || replace(e.status, '_', ' ') || '. '; end if;
    if e.cal_required and (e.cal_due is null or e.cal_due < current_date) then v_bad := v_bad || e.number || ' ' || e.name || ' calibration is out of date. '; end if;
  end loop;
  if new.result = 'cleared' then
    if n_unfixed > 0 then raise exception 'The line cannot be cleared: % failed item(s) not corrected.', n_unfixed; end if;
    if v_bad <> '' then raise exception 'The line cannot be cleared: %', v_bad; end if;
  end if;
  perform set_config('hx.reason', case when new.result = 'cleared' then 'Line cleared' else 'Line NOT cleared' end, true);
  return new;
end $$;
drop trigger if exists hx_line_clearances_guard on hx_line_clearances;
create trigger hx_line_clearances_guard before insert or update or delete on hx_line_clearances for each row execute function hx_line_clearance_guard();
drop trigger if exists hx_line_clearances_place on hx_line_clearances;
create trigger hx_line_clearances_place before insert or update on hx_line_clearances for each row execute function hx_fl_guard();
drop trigger if exists hx_line_clearances_audit on hx_line_clearances;
create trigger hx_line_clearances_audit after insert or update on hx_line_clearances for each row execute function hx_audit();

create table if not exists hx_rework (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  source_kind      text not null default 'batch' check (source_kind in ('batch','hold','other')),
  source_batch_id  text references hx_batches(id),
  source_hold_id   text references hx_holds(id),
  source_text      text not null default '',
  material         text not null check (length(trim(material)) > 0),
  product          text not null default '',
  quantity         text not null default '',
  unit             text not null default 'g',
  reason           text not null check (length(trim(reason)) > 0),
  identified_on    date not null default current_date,
  tag              text not null default '',
  location         text not null default '',
  expires_on       date,
  status           text not null default 'identified' check (status in ('identified','inspected','approved','used','destroyed')),
  inspection       text not null default '',
  analysis         text not null default '',
  inspection_result text not null default '' check (inspection_result in ('','pass','fail')),
  inspected_by     text not null default '',
  inspected_on     date,
  like_to_like     boolean not null default false,
  like_note        text not null default '',
  approved_by      text not null default '',
  approved_at      timestamptz,
  target_batch_id  text references hx_batches(id),
  target_expires   date,
  used_on          date,
  used_qty         text not null default '',
  destroyed_reason text,
  deviation_id     text,
  files            jsonb not null default '[]'::jsonb,
  notes            text not null default '',
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_rework_number on hx_rework(license_id, number);

create or replace function hx_rework_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then raise exception 'Rework records are never deleted. Destroy the rework with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_rework', new.license_id, 'RW');
    new.created_by := v_me; new.created_at := now(); new.status := 'identified';
    new.inspection_result := ''; new.approved_by := ''; new.approved_at := null; new.target_batch_id := null; new.used_on := null; new.destroyed_reason := null;
    if new.source_kind = 'batch' and new.source_batch_id is null then raise exception 'Choose the batch the rework comes from.'; end if;
    if new.source_kind = 'hold' and new.source_hold_id is null then raise exception 'Choose the hold the rework comes from.'; end if;
    if new.source_batch_id is not null and not exists (select 1 from hx_batches where id = new.source_batch_id and license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
    if new.identified_on > current_date then raise exception 'The date cannot be in the future.'; end if;
    perform set_config('hx.reason', 'Rework identified', true);
    new.updated_at := now();
    return new;
  end if;
  new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  if old.status in ('used','destroyed') and (to_jsonb(new) - 'files' - 'notes' - 'deviation_id' - 'updated_at') is distinct from (to_jsonb(old) - 'files' - 'notes' - 'deviation_id' - 'updated_at') then
    raise exception 'This rework is closed (%).', old.status;
  end if;
  if new.status = 'destroyed' and old.status <> 'destroyed' then
    if not hx_can('rework', 3, new.license_id) then raise exception 'Only Full access can destroy rework.'; end if;
    if coalesce(trim(new.destroyed_reason), '') = '' then raise exception 'Give a reason and how it was destroyed (waste log / METRC).'; end if;
    perform set_config('hx.reason', 'Rework destroyed: ' || trim(new.destroyed_reason), true);
  elsif new.status = 'inspected' and old.status = 'identified' then
    if coalesce(trim(new.inspection), '') = '' or new.inspection_result = '' then raise exception 'Record the inspection and its result (pass or fail).'; end if;
    if coalesce(trim(new.analysis), '') = '' then raise exception 'Record the analysis (test results / COA) before release.'; end if;
    if new.inspected_on is null then new.inspected_on := current_date; end if;
    if coalesce(trim(new.inspected_by), '') = '' then new.inspected_by := v_me; end if;
    perform set_config('hx.reason', 'Rework inspected: ' || new.inspection_result, true);
  elsif new.status = 'approved' and old.status = 'inspected' then
    if not hx_can('rework', 3, new.license_id) then raise exception 'Only Full access (qualified person) can approve rework.'; end if;
    if old.inspection_result <> 'pass' then raise exception 'Rework that failed inspection cannot be approved. Destroy it.'; end if;
    if not new.like_to_like then raise exception 'Confirm the rework goes into the same product (like-to-like).'; end if;
    if new.expires_on is null then raise exception 'Enter the rework expiry date.'; end if;
    new.approved_by := v_me; new.approved_at := now();
    perform set_config('hx.reason', 'Rework approved for use', true);
  elsif new.status = 'used' and old.status = 'approved' then
    if new.target_batch_id is null then raise exception 'Choose the batch the rework went into.'; end if;
    if not exists (select 1 from hx_batches where id = new.target_batch_id and license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
    if new.used_on is null then new.used_on := current_date; end if;
    if new.target_expires is not null and old.expires_on is not null and old.expires_on < new.target_expires then
      raise exception 'The rework expires (%) before the finished product (%). It cannot be used in this batch.', old.expires_on, new.target_expires;
    end if;
    perform set_config('hx.reason', 'Rework used in a batch', true);
  elsif new.status <> old.status then
    raise exception 'Rework goes identified -> inspected -> approved -> used (or destroyed).';
  else
    -- details may be corrected before inspection; approval and use facts stay as recorded
    if old.status <> 'identified' and (new.material, new.quantity, new.source_batch_id, new.source_hold_id, new.identified_on, new.inspection, new.analysis, new.inspection_result)
         is distinct from (old.material, old.quantity, old.source_batch_id, old.source_hold_id, old.identified_on, old.inspection, old.analysis, old.inspection_result) then
      raise exception 'After inspection the rework details cannot be changed.';
    end if;
    new.approved_by := old.approved_by; new.approved_at := old.approved_at;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_rework_guard on hx_rework;
create trigger hx_rework_guard before insert or update or delete on hx_rework for each row execute function hx_rework_guard();
drop trigger if exists hx_rework_place on hx_rework;
create trigger hx_rework_place before insert or update on hx_rework for each row execute function hx_fl_guard();
drop trigger if exists hx_rework_audit on hx_rework;
create trigger hx_rework_audit after insert or update on hx_rework for each row execute function hx_audit();

-- deviations can be raised from a line clearance, a rework or a piece of equipment
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment'));

alter table hx_line_clearances enable row level security;
alter table hx_rework enable row level security;
drop policy if exists hx_line_clearances_read on hx_line_clearances;
drop policy if exists hx_line_clearances_insert on hx_line_clearances;
drop policy if exists hx_line_clearances_update on hx_line_clearances;
create policy hx_line_clearances_read   on hx_line_clearances for select to authenticated using (hx_can('lineclear',1,license_id));
create policy hx_line_clearances_insert on hx_line_clearances for insert to authenticated with check (hx_can('lineclear',2,license_id));
create policy hx_line_clearances_update on hx_line_clearances for update to authenticated using (hx_can('lineclear',2,license_id)) with check (hx_can('lineclear',2,license_id));
drop policy if exists hx_rework_read on hx_rework;
drop policy if exists hx_rework_insert on hx_rework;
drop policy if exists hx_rework_update on hx_rework;
create policy hx_rework_read   on hx_rework for select to authenticated using (hx_can('rework',1,license_id));
create policy hx_rework_insert on hx_rework for insert to authenticated with check (hx_can('rework',2,license_id));
create policy hx_rework_update on hx_rework for update to authenticated using (hx_can('rework',2,license_id)) with check (hx_can('rework',2,license_id));
grant select, insert, update on hx_line_clearances, hx_rework to authenticated;

notify pgrst, 'reload schema';
