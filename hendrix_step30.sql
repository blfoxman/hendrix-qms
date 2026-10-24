-- =====================================================================
-- Hendrix QMS  -  Step 30: Org chart, Quality policy and Quality objectives / KPIs (CSQ Level 3)
-- Org chart (CSQ 5.1.1):
--   * positions per license with the person, who they report to, the
--     department, functions and responsibilities, the safety / quality / CSQ
--     roles they hold (senior management, quality / CSQ lead and backup,
--     HACCP team leader, recall coordinator ...) and a backup
--   * reporting lines cannot loop; a position with people under it cannot be
--     removed until they report to someone else
-- Quality policy and objectives (CSQ 1.2, 5.1.2, 5.1.4):
--   * the quality policy is a signed SOP (signatures per version come from
--     the SOP module); hx_qms_settings records which SOP it is
--   * objectives / KPIs (OBJ-###): what is measured (from Hendrix records or
--     entered), target, higher or lower is better, how often, owner, plan
--   * results per month or quarter (hx_objective_results): the database
--     decides if the target was met; a missed target needs the action
--   * achieved / dropped needs Full access and a note
-- Access modules 'orgchart' and 'objectives': View / Edit / Full.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-29.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_org_positions (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  title            text not null check (length(trim(title)) > 0),
  person_name      text not null default '',
  user_id          text,
  reports_to       text references hx_org_positions(id),
  department       text not null default '',
  responsibilities text not null default '',
  quality_roles    text[] not null default '{}',
  backup_name      text not null default '',
  sort             int not null default 0,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create index if not exists hx_org_positions_lic on hx_org_positions(license_id);

create or replace function hx_org_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_id text; n int := 0;
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_org_positions where reports_to = old.id) then
      raise exception 'People report to this position. Move them to another position first.';
    end if;
    perform set_config('hx.reason', 'Position removed from the org chart', true);
    return old;
  end if;
  if tg_op = 'INSERT' then new.created_by := coalesce(hx_me(), ''); new.created_at := now(); perform set_config('hx.reason', 'Position added to the org chart', true);
  else new.created_by := old.created_by; new.created_at := old.created_at;
    if new.reports_to is distinct from old.reports_to then perform set_config('hx.reason', 'Reporting line changed', true);
    elsif new.person_name is distinct from old.person_name then perform set_config('hx.reason', 'Person in the position changed', true);
    else perform set_config('hx.reason', 'Position updated', true); end if;
  end if;
  if new.reports_to is not null then
    if new.reports_to = new.id then raise exception 'A position cannot report to itself.'; end if;
    if not exists (select 1 from hx_org_positions where id = new.reports_to and license_id = new.license_id) then raise exception 'That position belongs to another license.'; end if;
    v_id := new.reports_to;
    while v_id is not null loop
      n := n + 1;
      if v_id = new.id or n > 200 then raise exception 'That reporting line would loop back to this position.'; end if;
      select reports_to into v_id from hx_org_positions where id = v_id;
    end loop;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_org_positions_guard on hx_org_positions;
create trigger hx_org_positions_guard before insert or update or delete on hx_org_positions for each row execute function hx_org_guard();
drop trigger if exists hx_org_positions_place on hx_org_positions;
create trigger hx_org_positions_place before insert or update on hx_org_positions for each row execute function hx_fl_guard();
drop trigger if exists hx_org_positions_audit on hx_org_positions;
create trigger hx_org_positions_audit after insert or update or delete on hx_org_positions for each row execute function hx_audit();

create table if not exists hx_qms_settings (
  license_id     text primary key references hx_licenses(id),
  state_id       text not null references hx_states(id),
  policy_sop_id  text,
  policy_note    text not null default '',
  updated_by     text not null default '',
  updated_at     timestamptz not null default now()
);
create or replace function hx_qms_settings_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Settings are not deleted.'; end if;
  if not hx_can('objectives', 3, new.license_id) then raise exception 'Only Full access can set the quality policy.'; end if;
  if new.policy_sop_id is not null and not exists (select 1 from hx_sops where id = new.policy_sop_id and (license_id = new.license_id or new.license_id = any(license_ids))) then
    raise exception 'That SOP is not used at this license.';
  end if;
  new.updated_by := coalesce(hx_me(), ''); new.updated_at := now();
  perform set_config('hx.reason', 'Quality policy set', true);
  return new;
end $$;
drop trigger if exists hx_qms_settings_guard on hx_qms_settings;
create trigger hx_qms_settings_guard before insert or update or delete on hx_qms_settings for each row execute function hx_qms_settings_guard();
drop trigger if exists hx_qms_settings_place on hx_qms_settings;
create trigger hx_qms_settings_place before insert or update on hx_qms_settings for each row execute function hx_fl_guard();

create table if not exists hx_objectives (
  id           text primary key,
  state_id     text not null references hx_states(id),
  license_id   text not null references hx_licenses(id),
  number       text not null default '',
  name         text not null check (length(trim(name)) > 0),
  category     text not null default 'quality',
  description  text not null default '',
  metric       text not null default 'manual',
  unit         text not null default '',
  direction    text not null default 'up' check (direction in ('up','down')),
  target       numeric not null,
  frequency    text not null default 'monthly' check (frequency in ('monthly','quarterly')),
  owner        text not null default '',
  start_on     date not null default current_date,
  due_on       date,
  action_plan  text not null default '',
  status       text not null default 'active' check (status in ('active','achieved','dropped')),
  close_note   text,
  closed_by    text not null default '',
  closed_at    timestamptz,
  created_by   text not null default '',
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);
create unique index if not exists hx_objectives_number on hx_objectives(license_id, number);

create or replace function hx_objective_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Objectives are never deleted. Mark it achieved or dropped with a note.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_objectives', new.license_id, 'OBJ');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.status := 'active'; new.close_note := null; new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Objective set', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if old.status <> 'active' then raise exception 'This objective is %.', old.status; end if;
    if new.status <> 'active' then
      if not hx_can('objectives', 3, new.license_id) then raise exception 'Only Full access can mark an objective achieved or dropped.'; end if;
      if coalesce(trim(new.close_note), '') = '' then raise exception 'Add a note (what was achieved, or why it is dropped).'; end if;
      new.closed_by := coalesce(hx_me(), ''); new.closed_at := now();
      perform set_config('hx.reason', 'Objective ' || new.status || ': ' || trim(new.close_note), true);
    elsif (new.target, new.direction, new.metric) is distinct from (old.target, old.direction, old.metric) then
      perform set_config('hx.reason', 'Objective target changed', true);
    end if;
  end if;
  if coalesce(trim(new.owner), '') = '' then raise exception 'Every objective needs an owner.'; end if;
  if new.due_on is not null and new.due_on < new.start_on then raise exception 'The due date is before the start.'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_objectives_guard on hx_objectives;
create trigger hx_objectives_guard before insert or update or delete on hx_objectives for each row execute function hx_objective_guard();
drop trigger if exists hx_objectives_place on hx_objectives;
create trigger hx_objectives_place before insert or update on hx_objectives for each row execute function hx_fl_guard();
drop trigger if exists hx_objectives_audit on hx_objectives;
create trigger hx_objectives_audit after insert or update on hx_objectives for each row execute function hx_audit();

create table if not exists hx_objective_results (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  objective_id  text not null references hx_objectives(id),
  period        text not null check (period ~ '^\d{4}-(0[1-9]|1[0-2]|Q[1-4])$'),
  value         numeric not null,
  met           boolean not null default false,
  auto          boolean not null default false,
  comment       text not null default '',
  action        text not null default '',
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists hx_objective_results_period on hx_objective_results(objective_id, period);

create or replace function hx_objective_result_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare o record;
begin
  if tg_op = 'DELETE' then raise exception 'Results are never deleted. Correct the value with a reason.'; end if;
  select * into o from hx_objectives where id = new.objective_id;
  if o.id is null or o.license_id <> new.license_id then raise exception 'That objective belongs to another license.'; end if;
  if (o.frequency = 'monthly') <> (new.period ~ '-\d\d$') then raise exception 'This objective is measured %; use a % period.', o.frequency, case when o.frequency = 'monthly' then 'YYYY-MM' else 'YYYY-Q#' end; end if;
  if tg_op = 'INSERT' then
    if o.status <> 'active' then raise exception 'This objective is %.', o.status; end if;
    new.recorded_by := coalesce(hx_me(), ''); new.created_at := now();
  else
    new.objective_id := old.objective_id; new.period := old.period; new.recorded_by := old.recorded_by; new.created_at := old.created_at;
    if coalesce(trim(current_setting('hx.reason', true)), '') = '' then perform set_config('hx.reason', 'Result corrected', true); end if;
  end if;
  new.met := case when o.direction = 'up' then new.value >= o.target else new.value <= o.target end;
  if not new.met and coalesce(trim(new.action), '') = '' then raise exception 'The target was missed: record the action that will be taken.'; end if;
  if tg_op = 'INSERT' then perform set_config('hx.reason', case when new.met then 'Result recorded: target met' else 'Result recorded: target missed' end, true); end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_objective_results_guard on hx_objective_results;
create trigger hx_objective_results_guard before insert or update or delete on hx_objective_results for each row execute function hx_objective_result_guard();
drop trigger if exists hx_objective_results_place on hx_objective_results;
create trigger hx_objective_results_place before insert or update on hx_objective_results for each row execute function hx_fl_guard();
drop trigger if exists hx_objective_results_audit on hx_objective_results;
create trigger hx_objective_results_audit after insert or update on hx_objective_results for each row execute function hx_audit();

alter table hx_org_positions enable row level security;
alter table hx_qms_settings enable row level security;
alter table hx_objectives enable row level security;
alter table hx_objective_results enable row level security;
drop policy if exists hx_org_positions_read on hx_org_positions;
drop policy if exists hx_org_positions_insert on hx_org_positions;
drop policy if exists hx_org_positions_update on hx_org_positions;
drop policy if exists hx_org_positions_delete on hx_org_positions;
create policy hx_org_positions_read   on hx_org_positions for select to authenticated using (hx_can('orgchart',1,license_id));
create policy hx_org_positions_insert on hx_org_positions for insert to authenticated with check (hx_can('orgchart',2,license_id));
create policy hx_org_positions_update on hx_org_positions for update to authenticated using (hx_can('orgchart',2,license_id)) with check (hx_can('orgchart',2,license_id));
create policy hx_org_positions_delete on hx_org_positions for delete to authenticated using (hx_can('orgchart',3,license_id));
drop policy if exists hx_qms_settings_read on hx_qms_settings;
drop policy if exists hx_qms_settings_insert on hx_qms_settings;
drop policy if exists hx_qms_settings_update on hx_qms_settings;
create policy hx_qms_settings_read   on hx_qms_settings for select to authenticated using (hx_can('objectives',1,license_id) or hx_can('orgchart',1,license_id));
create policy hx_qms_settings_insert on hx_qms_settings for insert to authenticated with check (hx_can('objectives',3,license_id));
create policy hx_qms_settings_update on hx_qms_settings for update to authenticated using (hx_can('objectives',3,license_id)) with check (hx_can('objectives',3,license_id));
drop policy if exists hx_objectives_read on hx_objectives;
drop policy if exists hx_objectives_insert on hx_objectives;
drop policy if exists hx_objectives_update on hx_objectives;
create policy hx_objectives_read   on hx_objectives for select to authenticated using (hx_can('objectives',1,license_id));
create policy hx_objectives_insert on hx_objectives for insert to authenticated with check (hx_can('objectives',2,license_id));
create policy hx_objectives_update on hx_objectives for update to authenticated using (hx_can('objectives',2,license_id)) with check (hx_can('objectives',2,license_id));
drop policy if exists hx_objective_results_read on hx_objective_results;
drop policy if exists hx_objective_results_insert on hx_objective_results;
drop policy if exists hx_objective_results_update on hx_objective_results;
create policy hx_objective_results_read   on hx_objective_results for select to authenticated using (hx_can('objectives',1,license_id));
create policy hx_objective_results_insert on hx_objective_results for insert to authenticated with check (hx_can('objectives',2,license_id));
create policy hx_objective_results_update on hx_objective_results for update to authenticated using (hx_can('objectives',2,license_id)) with check (hx_can('objectives',2,license_id));
grant select, insert, update, delete on hx_org_positions to authenticated;
grant select, insert, update on hx_qms_settings, hx_objectives, hx_objective_results to authenticated;

notify pgrst, 'reload schema';
