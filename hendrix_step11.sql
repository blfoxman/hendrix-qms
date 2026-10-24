-- =====================================================================
-- Hendrix QMS  -  Step 11: Standards (CSQ Standard for Manufacturing)
-- The published standards the company follows, clause by clause, and each
-- license's conformance to them: status, owner, due date, evidence, files.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-10.
-- Safe to run more than once.
--
-- Rules built into the database:
--   * a standard and its clauses are one shared library (not per state): the
--     standard is the same everywhere; conformance is kept per license
--   * a license must ADOPT a standard (with a target level) before conformance
--     can be recorded for it; adoption is never deleted (set status Withdrawn)
--   * one conformance record per license + clause; never deleted; every change
--     is in the audit trail
--   * "Not applicable" needs a written justification
--   * a clause with conformance records cannot be removed
-- Access module: 'standards'
--   View = read the standard and conformance
--   Edit = update conformance (status, owner, evidence, files)
--   Full = add or change the standard, adopt it for a license, set the target level
-- =====================================================================

create table if not exists hx_standards (
  id          text primary key,
  code        text not null unique check (length(trim(code)) > 0),
  name        text not null check (length(trim(name)) > 0),
  publisher   text not null default '',
  version     text not null default '',
  issued      text not null default '',
  scope       text not null default '',
  levels      jsonb not null default '[]'::jsonb,
  modules     jsonb not null default '{}'::jsonb,
  audit_notes jsonb not null default '[]'::jsonb,
  file_path   text not null default '',
  file_name   text not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create table if not exists hx_standard_clauses (
  id           text primary key,
  standard_id  text not null references hx_standards(id) on delete cascade,
  clause       text not null check (length(trim(clause)) > 0),
  module       text not null default '',
  title        text not null default '',
  summary      text not null default '',
  level        int  not null default 1 check (level between 1 and 3),
  applies_to   text not null default '',
  hx_pages     text[] not null default '{}',
  hx_support   text not null default '',
  hx_planned   text[] not null default '{}',
  sort         int  not null default 0,
  updated_at   timestamptz not null default now()
);
alter table hx_standards add column if not exists audit_notes jsonb not null default '[]'::jsonb;

create unique index if not exists hx_standard_clauses_one on hx_standard_clauses(standard_id, clause);

create table if not exists hx_license_standards (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  standard_id   text not null references hx_standards(id),
  target_level  int  not null default 1 check (target_level between 1 and 3),
  status        text not null default 'Following' check (status in ('Following','Audit scheduled','Certified','Suspended','Withdrawn')),
  cert_body     text not null default '',
  audit_date    date,
  cert_number   text not null default '',
  cert_expiry   date,
  notes         text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists hx_license_standards_one on hx_license_standards(license_id, standard_id);

create table if not exists hx_conformance (
  id           text primary key,
  state_id     text not null references hx_states(id),
  license_id   text not null references hx_licenses(id),
  standard_id  text not null references hx_standards(id),
  clause_id    text not null references hx_standard_clauses(id) on delete restrict,
  status       text not null default 'Not assessed' check (status in ('Not assessed','Conforming','Partial','Not conforming','Not applicable')),
  owner        text not null default '',
  due_date     date,
  doc_ref      text not null default '',
  evidence     text not null default '',
  files        jsonb not null default '[]'::jsonb,
  reviewed_at  timestamptz,
  reviewed_by  uuid,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);
create unique index if not exists hx_conformance_one on hx_conformance(license_id, clause_id);
create index if not exists hx_conformance_lic on hx_conformance(license_id, standard_id);

-- ---------- guards ----------
create or replace function hx_std_touch() returns trigger
language plpgsql as $$
begin new.updated_at := now(); return new; end $$;

create or replace function hx_license_std_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    raise exception 'A standard cannot be removed from a license. Set its status to Withdrawn instead.';
  end if;
  if tg_op = 'UPDATE' and new.standard_id is distinct from old.standard_id then
    raise exception 'The standard of an adoption cannot be changed.';
  end if;
  new.updated_at := now();
  return new;
end $$;

create or replace function hx_conformance_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_std text;
begin
  if tg_op = 'DELETE' then
    raise exception 'Conformance records cannot be deleted.';
  end if;
  select standard_id into v_std from hx_standard_clauses where id = new.clause_id;
  if v_std is null then raise exception 'Unknown clause.'; end if;
  if v_std <> new.standard_id then raise exception 'That clause belongs to a different standard.'; end if;
  if tg_op = 'UPDATE' and (new.clause_id is distinct from old.clause_id or new.standard_id is distinct from old.standard_id) then
    raise exception 'The clause of a conformance record cannot be changed.';
  end if;
  if not exists (select 1 from hx_license_standards
                 where license_id = new.license_id and standard_id = new.standard_id and status <> 'Withdrawn') then
    raise exception 'This license has not adopted that standard yet.';
  end if;
  if new.status = 'Not applicable' and coalesce(trim(new.evidence), '') = '' then
    raise exception 'Write why the clause does not apply (justification) before marking it Not applicable.';
  end if;
  if tg_op = 'INSERT' or new.status is distinct from old.status or new.evidence is distinct from old.evidence then
    new.reviewed_at := now(); new.reviewed_by := auth.uid();
  end if;
  if tg_op = 'UPDATE' then new.created_at := old.created_at; end if;
  new.updated_at := now();
  perform set_config('hx.reason', 'Conformance ' || case when tg_op = 'INSERT' then 'recorded' else 'updated' end, true);
  return new;
end $$;

drop trigger if exists hx_standards_touch on hx_standards;
create trigger hx_standards_touch before update on hx_standards for each row execute function hx_std_touch();
drop trigger if exists hx_standard_clauses_touch on hx_standard_clauses;
create trigger hx_standard_clauses_touch before update on hx_standard_clauses for each row execute function hx_std_touch();

drop trigger if exists hx_license_standards_guard on hx_license_standards;
create trigger hx_license_standards_guard before insert or update or delete on hx_license_standards for each row execute function hx_license_std_guard();
drop trigger if exists hx_license_standards_place on hx_license_standards;
create trigger hx_license_standards_place before insert or update on hx_license_standards for each row execute function hx_fl_guard();

drop trigger if exists hx_conformance_guard on hx_conformance;
create trigger hx_conformance_guard before insert or update or delete on hx_conformance for each row execute function hx_conformance_guard();
drop trigger if exists hx_conformance_place on hx_conformance;
create trigger hx_conformance_place before insert or update on hx_conformance for each row execute function hx_fl_guard();

drop trigger if exists hx_standards_audit on hx_standards;
create trigger hx_standards_audit after insert or update or delete on hx_standards for each row execute function hx_audit();
drop trigger if exists hx_standard_clauses_audit on hx_standard_clauses;
create trigger hx_standard_clauses_audit after insert or update or delete on hx_standard_clauses for each row execute function hx_audit();
drop trigger if exists hx_license_standards_audit on hx_license_standards;
create trigger hx_license_standards_audit after insert or update or delete on hx_license_standards for each row execute function hx_audit();
drop trigger if exists hx_conformance_audit on hx_conformance;
create trigger hx_conformance_audit after insert or update or delete on hx_conformance for each row execute function hx_audit();

-- ---------- access ----------
alter table hx_standards enable row level security;
alter table hx_standard_clauses enable row level security;
alter table hx_license_standards enable row level security;
alter table hx_conformance enable row level security;

drop policy if exists hx_standards_read on hx_standards;
drop policy if exists hx_standards_insert on hx_standards;
drop policy if exists hx_standards_update on hx_standards;
drop policy if exists hx_standards_delete on hx_standards;
create policy hx_standards_read   on hx_standards for select to authenticated using (hx_can('standards',1));
create policy hx_standards_insert on hx_standards for insert to authenticated with check (hx_can('standards',3));
create policy hx_standards_update on hx_standards for update to authenticated using (hx_can('standards',3)) with check (hx_can('standards',3));
create policy hx_standards_delete on hx_standards for delete to authenticated using (hx_can('standards',3));

drop policy if exists hx_standard_clauses_read on hx_standard_clauses;
drop policy if exists hx_standard_clauses_insert on hx_standard_clauses;
drop policy if exists hx_standard_clauses_update on hx_standard_clauses;
drop policy if exists hx_standard_clauses_delete on hx_standard_clauses;
create policy hx_standard_clauses_read   on hx_standard_clauses for select to authenticated using (hx_can('standards',1));
create policy hx_standard_clauses_insert on hx_standard_clauses for insert to authenticated with check (hx_can('standards',3));
create policy hx_standard_clauses_update on hx_standard_clauses for update to authenticated using (hx_can('standards',3)) with check (hx_can('standards',3));
create policy hx_standard_clauses_delete on hx_standard_clauses for delete to authenticated using (hx_can('standards',3));

drop policy if exists hx_license_standards_read on hx_license_standards;
drop policy if exists hx_license_standards_insert on hx_license_standards;
drop policy if exists hx_license_standards_update on hx_license_standards;
create policy hx_license_standards_read   on hx_license_standards for select to authenticated using (hx_can('standards',1,license_id));
create policy hx_license_standards_insert on hx_license_standards for insert to authenticated with check (hx_can('standards',3,license_id));
create policy hx_license_standards_update on hx_license_standards for update to authenticated using (hx_can('standards',3,license_id)) with check (hx_can('standards',3,license_id));

drop policy if exists hx_conformance_read on hx_conformance;
drop policy if exists hx_conformance_insert on hx_conformance;
drop policy if exists hx_conformance_update on hx_conformance;
create policy hx_conformance_read   on hx_conformance for select to authenticated using (hx_can('standards',1,license_id));
create policy hx_conformance_insert on hx_conformance for insert to authenticated with check (hx_can('standards',2,license_id));
create policy hx_conformance_update on hx_conformance for update to authenticated using (hx_can('standards',2,license_id)) with check (hx_can('standards',2,license_id));

grant select, insert, update, delete on hx_standards, hx_standard_clauses to authenticated;
grant select, insert, update on hx_license_standards, hx_conformance to authenticated;

notify pgrst, 'reload schema';
