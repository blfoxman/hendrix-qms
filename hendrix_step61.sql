-- =====================================================================
-- Hendrix QMS  -  Step 61: Manufacturing Process (production runs)
--
--   * Production > Manufacturing Process (manufacturing / processor licenses only):
--       Part 1  Material used       METRC tag # | item | weight   (add as many rows as needed)
--       Part 2  Product produced    METRC tag # | item | weight   (add rows) + waste
--       Part 3+ Additional process  same as Part 2; "Required additional process" adds another
--   * Each license keeps its own item list (hx_mp_items) that fills the Item drop-downs.
--     Anyone who can Edit batches adds items; Full access renames or switches them off.
--     Items are switched off, never deleted (finished runs keep the item name).
--   * A run is never deleted: later changes need a reason, a run is voided with a reason, and
--     every change is in the Audit Trail.
--   Access module 'batch' (Batch Tracker): View sees runs / Edit records runs and adds items /
--   Full voids runs and manages the item list.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-60.
-- Safe to run more than once.
-- =====================================================================

-- ---------- per-license item list ----------
create table if not exists hx_mp_items (
  id          text primary key,
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  name        text not null check (length(trim(name)) > 0),
  unit        text not null default 'g' check (unit in ('g','kg','oz','lb','ml','l','each')),
  use_in      text not null default 'both' check (use_in in ('material','product','both')),
  notes       text not null default '',
  active      boolean not null default true,
  sort        int not null default 0,
  created_by  text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create unique index if not exists hx_mp_items_name on hx_mp_items(license_id, lower(trim(name)));

create or replace function hx_mp_item_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Items are not deleted - switch the item off. Finished runs keep the item name.'; end if;
  if not exists (select 1 from hx_licenses where id = new.license_id and state_id = new.state_id) then raise exception 'The license is not in this state.'; end if;
  new.name := trim(new.name);
  if tg_op = 'INSERT' then
    if not hx_can('batch', 2, new.license_id) then raise exception 'Edit access to batches is needed to add an item.'; end if;
    new.created_by := coalesce(hx_me(), ''); new.created_at := now();
  else
    if not hx_can('batch', 3, new.license_id) then raise exception 'Full access to batches is needed to change or switch off an item.'; end if;
    if new.license_id <> old.license_id then raise exception 'An item cannot move to another license.'; end if;
    new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_mp_item_guard on hx_mp_items;
create trigger hx_mp_item_guard before insert or update or delete on hx_mp_items for each row execute function hx_mp_item_guard();
drop trigger if exists hx_mp_items_audit on hx_mp_items;
create trigger hx_mp_items_audit after insert or update on hx_mp_items for each row execute function hx_audit();
alter table hx_mp_items enable row level security;
drop policy if exists hx_mp_items_read on hx_mp_items;
drop policy if exists hx_mp_items_insert on hx_mp_items;
drop policy if exists hx_mp_items_update on hx_mp_items;
create policy hx_mp_items_read on hx_mp_items for select to authenticated using (hx_lic_ok(license_id) and hx_can('batch', 1, license_id));
create policy hx_mp_items_insert on hx_mp_items for insert to authenticated with check (hx_can('batch', 2, license_id));
create policy hx_mp_items_update on hx_mp_items for update to authenticated using (hx_can('batch', 3, license_id)) with check (hx_can('batch', 3, license_id));
grant select, insert, update on hx_mp_items to authenticated;

-- ---------- production runs ----------
--   materials: [{tag, item, weight, unit}]
--   produced:  [{rows:[{tag, item, weight, unit}], waste:{weight, unit, note}}]   (stage 1 = Part 2, stage 2 = Part 3 ...)
create table if not exists hx_mp_runs (
  id          text primary key,
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  number      text not null default '',
  run_date    date not null default current_date,
  note        text not null default '',
  materials   jsonb not null default '[]'::jsonb,
  produced    jsonb not null default '[]'::jsonb,
  created_by  text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  edit_reason text,
  voided      boolean not null default false,
  void_reason text,
  voided_by   uuid,
  voided_at   timestamptz
);
create unique index if not exists hx_mp_runs_number on hx_mp_runs(license_id, number);
create index if not exists hx_mp_runs_lic_date on hx_mp_runs(license_id, run_date desc);

create or replace function hx_mp_rows_ok(p_rows jsonb, p_what text) returns void
language plpgsql immutable as $$
declare r jsonb;
begin
  if jsonb_typeof(p_rows) <> 'array' or jsonb_array_length(p_rows) = 0 then raise exception '% needs at least one row.', p_what; end if;
  if jsonb_array_length(p_rows) > 200 then raise exception '% has too many rows.', p_what; end if;
  for r in select x from jsonb_array_elements(p_rows) x loop
    if jsonb_typeof(r) <> 'object' then raise exception '% has a row that is not valid.', p_what; end if;
    if coalesce(trim(r->>'item'), '') = '' then raise exception 'Every row in % needs an item.', p_what; end if;
    if coalesce(r->>'weight', '') !~ '^[0-9]+(\.[0-9]+)?$' then raise exception 'Every row in % needs a weight (a number, 0 or more).', p_what; end if;
    if length(coalesce(r->>'tag', '')) > 40 then raise exception 'A METRC tag in % is too long.', p_what; end if;
  end loop;
end $$;

create or replace function hx_mp_run_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s jsonb; i int := 0; n int;
begin
  if tg_op = 'DELETE' then raise exception 'Runs cannot be deleted. Void the run with a reason instead.'; end if;
  if not exists (select 1 from hx_licenses where id = new.license_id and state_id = new.state_id) then raise exception 'The license is not in this state.'; end if;
  if tg_op = 'UPDATE' and coalesce(new.voided, false) then
    if not hx_can('batch', 3, new.license_id) then raise exception 'Full access to batches is needed to void a run.'; end if;
    return new;     -- the shared record guard checks the reason and that nothing else changed
  end if;
  if not hx_can('batch', 2, new.license_id) then raise exception 'Edit access to batches is needed to record a run.'; end if;
  perform hx_mp_rows_ok(new.materials, 'Part 1 (material used)');
  if jsonb_typeof(new.produced) <> 'array' or jsonb_array_length(new.produced) = 0 then raise exception 'Part 2 (product produced) needs at least one row.'; end if;
  if jsonb_array_length(new.produced) > 10 then raise exception 'Too many additional processes.'; end if;
  for s in select x from jsonb_array_elements(new.produced) x loop
    i := i + 1;
    perform hx_mp_rows_ok(s->'rows', 'Part ' || (i + 1) || ' (product produced)');
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
  else
    if new.license_id <> old.license_id then raise exception 'A run cannot move to another license.'; end if;
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_mp_runs_guard on hx_mp_runs;
create trigger hx_mp_runs_guard before insert or update or delete on hx_mp_runs for each row execute function hx_mp_run_guard();
-- later changes need a reason, voiding needs a reason (shared record guard from step 6)
drop trigger if exists hx_mp_runs_record_guard on hx_mp_runs;
create trigger hx_mp_runs_record_guard before update or delete on hx_mp_runs for each row execute function hx_record_guard();
drop trigger if exists hx_mp_runs_audit on hx_mp_runs;
create trigger hx_mp_runs_audit after insert or update on hx_mp_runs for each row execute function hx_audit();
alter table hx_mp_runs enable row level security;
drop policy if exists hx_mp_runs_read on hx_mp_runs;
drop policy if exists hx_mp_runs_insert on hx_mp_runs;
drop policy if exists hx_mp_runs_update on hx_mp_runs;
create policy hx_mp_runs_read on hx_mp_runs for select to authenticated using (hx_lic_ok(license_id) and hx_can('batch', 1, license_id));
create policy hx_mp_runs_insert on hx_mp_runs for insert to authenticated with check (hx_can('batch', 2, license_id));
create policy hx_mp_runs_update on hx_mp_runs for update to authenticated using (hx_can('batch', 2, license_id)) with check (hx_can('batch', 2, license_id));
grant select, insert, update on hx_mp_runs to authenticated;

notify pgrst, 'reload schema';
