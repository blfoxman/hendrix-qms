-- =====================================================================
-- Hendrix QMS  -  Step 14: Deviations and CAPA
-- Black Fox QMS Deviations + CAPAs (same fields), plus CSQ 1.6:
--   * every deviation gets a number (DEV-YYYY-###, per license) and must have an
--     immediate correction before it is closed
--   * an authorized person (Full access) decides whether a root cause analysis is
--     needed; when it is, the root cause is required before closing
--   * owner and due date (timescale) on deviations and CAPAs
--   * a CAPA (CAPA-YYYY-###) closes only after the fix is VERIFIED: verification
--     evidence, who verified, and rated Effective. "Partially effective" or
--     "Ineffective" keeps it open
--   * deviations can come from a facility log entry, a batch, a test, a visitor or
--     a standard clause (source link), so the record shows where it started
--   * nothing is deleted: records are CANCELLED with a reason (Full access)
--   * every change is in the audit trail
-- Access module 'qms': View = see and REPORT deviations, Edit = update deviations
--   and create / work CAPAs, Full = RCA decision, close, verify, cancel.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-13.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_deviations (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  title            text not null check (length(trim(title)) > 0),
  dept             text not null default 'Production',
  category         text not null default '',
  description      text not null default '',
  product_affected text not null default '',
  lot_number       text not null default '',
  occurred_on      date,
  source_type      text not null default 'manual' check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit')),
  source_id        text not null default '',
  source_label     text not null default '',
  immediate_action text not null default '',
  rca_required     boolean,
  rca_decided_by   text not null default '',
  root_cause       text not null default '',
  owner_name       text not null default '',
  due_date         date,
  priority         text not null default 'major' check (priority in ('critical','major','minor')),
  status           text not null default 'open' check (status in ('open','in_progress','closed','cancelled')),
  close_note       text not null default '',
  closed_by        text not null default '',
  closed_at        timestamptz,
  cancel_reason    text not null default '',
  attachments      jsonb not null default '[]'::jsonb,
  reported_by      text not null default '',
  reported_by_id   uuid default auth.uid(),
  created_at       timestamptz not null default now(),
  updated_by       text not null default '',
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_deviations_number on hx_deviations(license_id, number) where number <> '';
create index if not exists hx_deviations_lic on hx_deviations(license_id, created_at desc);
create index if not exists hx_deviations_src on hx_deviations(source_type, source_id);

create table if not exists hx_capas (
  id                      text primary key,
  state_id                text not null references hx_states(id),
  license_id              text not null references hx_licenses(id),
  number                  text not null default '',
  title                   text not null check (length(trim(title)) > 0),
  deviation_id            text references hx_deviations(id),
  dept                    text not null default 'Production',
  issue_description       text not null default '',
  root_cause              text not null default '',
  correction              text not null default '',
  preventive_action       text not null default '',
  responsible_person_id   text not null default '',
  responsible_person_name text not null default '',
  due_date                date,
  verification_method     text not null default '',
  verification_evidence   text not null default '',
  verified_by             text not null default '',
  verified_at             timestamptz,
  effectiveness_rating    text not null default '' check (effectiveness_rating in ('','effective','partially','ineffective')),
  priority                text not null default 'major' check (priority in ('critical','major','minor')),
  status                  text not null default 'open' check (status in ('open','in_progress','closed','cancelled')),
  closed_by               text not null default '',
  closed_at               timestamptz,
  cancel_reason           text not null default '',
  attachments             jsonb not null default '[]'::jsonb,
  created_by              text not null default '',
  created_by_id           uuid default auth.uid(),
  created_at              timestamptz not null default now(),
  updated_by              text not null default '',
  updated_at              timestamptz not null default now()
);
create unique index if not exists hx_capas_number on hx_capas(license_id, number) where number <> '';
create index if not exists hx_capas_lic on hx_capas(license_id, created_at desc);
create index if not exists hx_capas_dev on hx_capas(deviation_id);

-- ---------- numbering ----------
create or replace function hx_qms_next_number(p_table text, p_lic text, p_prefix text) returns text
language plpgsql security definer set search_path = public as $$
declare v_year text := to_char(now(), 'YYYY'); v_max int;
begin
  perform pg_advisory_xact_lock(hashtext(p_table || p_lic));
  execute format('select coalesce(max((regexp_match(number, %L))[1]::int), 0) from %I where license_id = $1',
                 '^' || p_prefix || '-' || v_year || '-(\d+)$', p_table) into v_max using p_lic;
  return p_prefix || '-' || v_year || '-' || lpad((v_max + 1)::text, 3, '0');
end $$;

-- ---------- guards ----------
create or replace function hx_deviation_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_name text; v_full boolean := hx_perm('qms') >= 3; v_edit boolean := hx_perm('qms') >= 2;
begin
  if tg_op = 'DELETE' then raise exception 'Deviations are never deleted. Cancel it with a reason.'; end if;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  new.updated_at := now(); new.updated_by := coalesce(v_name, new.updated_by);

  if tg_op = 'INSERT' then
    new.number := hx_qms_next_number('hx_deviations', new.license_id, 'DEV');
    new.reported_by := coalesce(v_name, new.reported_by); new.reported_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('open','in_progress') then raise exception 'A new deviation starts open.'; end if;
    if not v_full then new.rca_required := null; new.rca_decided_by := ''; end if;
    if new.rca_required is not null then new.rca_decided_by := coalesce(v_name,''); end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Deviation reported', true);
    return new;
  end if;

  if new.number <> old.number or new.reported_by_id is distinct from old.reported_by_id or new.created_at <> old.created_at
     or new.state_id <> old.state_id or new.license_id <> old.license_id then
    raise exception 'The number, reporter, date and license of a deviation cannot be changed.';
  end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'Only someone with Full access to QMS can reopen a closed deviation.'; end if;
    if new.status in ('closed','cancelled') and new.status = old.status then raise exception 'This deviation is % and cannot be changed. Reopen it first.', old.status; end if;
  end if;
  if not v_edit then raise exception 'You need Edit access to QMS to change a deviation.'; end if;
  if new.rca_required is distinct from old.rca_required then
    if not v_full then raise exception 'Only an authorized person (Full access to QMS) decides whether a root cause analysis is needed.'; end if;
    new.rca_decided_by := coalesce(v_name,'');
  end if;
  if new.status = 'closed' and old.status <> 'closed' then
    if not v_full then raise exception 'Only someone with Full access to QMS can close a deviation.'; end if;
    if coalesce(trim(new.immediate_action),'') = '' then raise exception 'Every deviation needs its correction (immediate action) recorded before it is closed.'; end if;
    if new.rca_required is null then raise exception 'Decide whether a root cause analysis is needed before closing.'; end if;
    if new.rca_required and coalesce(trim(new.root_cause),'') = '' then raise exception 'A root cause is required before closing (RCA was marked as needed).'; end if;
    new.closed_by := coalesce(v_name,''); new.closed_at := now();
    perform set_config('hx.reason', 'Deviation closed' || case when trim(new.close_note) <> '' then ': ' || trim(new.close_note) else '' end, true);
  elsif new.status = 'cancelled' and old.status <> 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access to QMS can cancel a deviation.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel a deviation.'; end if;
    perform set_config('hx.reason', 'Deviation cancelled: ' || trim(new.cancel_reason), true);
  elsif old.status in ('closed','cancelled') then
    new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Deviation reopened', true);
  else
    perform set_config('hx.reason', 'Deviation updated', true);
  end if;
  return new;
end $$;

create or replace function hx_capa_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_name text; v_full boolean := hx_perm('qms') >= 3; v_dev record;
begin
  if tg_op = 'DELETE' then raise exception 'CAPAs are never deleted. Cancel it with a reason.'; end if;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  new.updated_at := now(); new.updated_by := coalesce(v_name, new.updated_by);
  if new.deviation_id is not null then
    select license_id into v_dev from hx_deviations where id = new.deviation_id;
    if v_dev.license_id is distinct from new.license_id then raise exception 'That deviation belongs to a different license.'; end if;
  end if;

  if tg_op = 'INSERT' then
    new.number := hx_qms_next_number('hx_capas', new.license_id, 'CAPA');
    new.created_by := coalesce(v_name, new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('open','in_progress') then raise exception 'A new CAPA starts open.'; end if;
    new.verified_by := ''; new.verified_at := null; new.effectiveness_rating := ''; new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'CAPA opened', true);
    return new;
  end if;

  if new.number <> old.number or new.created_by_id is distinct from old.created_by_id or new.created_at <> old.created_at
     or new.state_id <> old.state_id or new.license_id <> old.license_id then
    raise exception 'The number, creator, date and license of a CAPA cannot be changed.';
  end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'Only someone with Full access to QMS can reopen a closed CAPA.'; end if;
    if new.status = old.status then raise exception 'This CAPA is % and cannot be changed. Reopen it first.', old.status; end if;
  end if;
  if new.effectiveness_rating is distinct from old.effectiveness_rating or new.verification_evidence is distinct from old.verification_evidence then
    if not v_full then raise exception 'Only someone with Full access to QMS verifies effectiveness.'; end if;
    if new.effectiveness_rating <> '' then new.verified_by := coalesce(v_name,''); new.verified_at := now(); end if;
  end if;
  if new.status = 'closed' and old.status <> 'closed' then
    if not v_full then raise exception 'Only someone with Full access to QMS can close a CAPA.'; end if;
    if coalesce(trim(new.correction),'') = '' then raise exception 'Record the correction before closing the CAPA.'; end if;
    if coalesce(trim(new.verification_evidence),'') = '' then raise exception 'Record how the fix was verified (evidence) before closing the CAPA.'; end if;
    if new.effectiveness_rating <> 'effective' then raise exception 'A CAPA closes only when it is verified Effective. Partially effective or ineffective stays open with more action.'; end if;
    new.closed_by := coalesce(v_name,''); new.closed_at := now();
    perform set_config('hx.reason', 'CAPA verified effective and closed', true);
  elsif new.status = 'cancelled' and old.status <> 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access to QMS can cancel a CAPA.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel a CAPA.'; end if;
    perform set_config('hx.reason', 'CAPA cancelled: ' || trim(new.cancel_reason), true);
  elsif old.status in ('closed','cancelled') then
    new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'CAPA reopened', true);
  else
    perform set_config('hx.reason', case when new.effectiveness_rating is distinct from old.effectiveness_rating then 'Effectiveness rated ' || coalesce(nullif(new.effectiveness_rating,''),'(cleared)') else 'CAPA updated' end, true);
  end if;
  return new;
end $$;

drop trigger if exists hx_deviations_guard on hx_deviations;
create trigger hx_deviations_guard before insert or update or delete on hx_deviations for each row execute function hx_deviation_guard();
drop trigger if exists hx_deviations_place on hx_deviations;
create trigger hx_deviations_place before insert or update on hx_deviations for each row execute function hx_fl_guard();
drop trigger if exists hx_deviations_audit on hx_deviations;
create trigger hx_deviations_audit after insert or update or delete on hx_deviations for each row execute function hx_audit();
drop trigger if exists hx_capas_guard on hx_capas;
create trigger hx_capas_guard before insert or update or delete on hx_capas for each row execute function hx_capa_guard();
drop trigger if exists hx_capas_place on hx_capas;
create trigger hx_capas_place before insert or update on hx_capas for each row execute function hx_fl_guard();
drop trigger if exists hx_capas_audit on hx_capas;
create trigger hx_capas_audit after insert or update or delete on hx_capas for each row execute function hx_audit();

-- people who can be named responsible for a CAPA (names only)
create or replace function hx_qms_people(p_lic text) returns table(id text, name text)
language sql stable security definer set search_path = public as $$
  select p.id::text, coalesce(nullif(p.name,''), p.email) from hx_profiles p
   where p.approved and hx_perm('qms') >= 1 and hx_lic_ok(p_lic)
     and (p.role = 'admin' or coalesce(array_length(p.license_ids,1),0) = 0 or p_lic = any(p.license_ids))
   order by 2;
$$;
grant execute on function hx_qms_people(text) to authenticated;

-- ---------- access ----------
alter table hx_deviations enable row level security;
alter table hx_capas enable row level security;
drop policy if exists hx_deviations_read on hx_deviations;
drop policy if exists hx_deviations_insert on hx_deviations;
drop policy if exists hx_deviations_update on hx_deviations;
create policy hx_deviations_read   on hx_deviations for select to authenticated using (hx_can('qms',1,license_id));
create policy hx_deviations_insert on hx_deviations for insert to authenticated with check (hx_can('qms',1,license_id));
create policy hx_deviations_update on hx_deviations for update to authenticated using (hx_can('qms',2,license_id)) with check (hx_can('qms',2,license_id));
drop policy if exists hx_capas_read on hx_capas;
drop policy if exists hx_capas_insert on hx_capas;
drop policy if exists hx_capas_update on hx_capas;
create policy hx_capas_read   on hx_capas for select to authenticated using (hx_can('qms',1,license_id));
create policy hx_capas_insert on hx_capas for insert to authenticated with check (hx_can('qms',2,license_id));
create policy hx_capas_update on hx_capas for update to authenticated using (hx_can('qms',2,license_id)) with check (hx_can('qms',2,license_id));
grant select, insert, update on hx_deviations, hx_capas to authenticated;

notify pgrst, 'reload schema';
