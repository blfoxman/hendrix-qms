-- =====================================================================
-- Hendrix QMS  -  Step 21: CSQ Manufacturing + Extraction + Cultivation
-- The three CSQ standards (v2.0, October 2025) share Modules 1, 2A, 4A and 5
-- word for word; only Module 3 differs:
--   3A  CSQ Standard for Cultivation    -> cultivation (CUL) licenses ONLY
--   3B  CSQ Standard for Extraction     -> manufacturing licenses
--   3C  CSQ Standard for Manufacturing  -> manufacturing licenses
-- Hendrix keeps ONE CSQ library (the shared clauses are assessed once) and each
-- license adopts the Module 3 parts that match what the license does:
--   * hx_licenses.operation: manufacturing / cultivation / other
--     (filled from the license number and type: CUL... or grower/cultivation =
--     cultivation; MAN... or manufacturer/processor/extraction = manufacturing)
--   * hx_license_standards.scopes: the Module 3 parts in scope
--     (manufacturing: 3C and 3B; cultivation: 3A only)
--   * the database refuses Cultivation (3A) on a non-cultivation license and
--     Extraction / Manufacturing (3B / 3C) on a cultivation license, both for
--     the adoption and for every conformance record
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-20.
-- Then open Standards and click "Update the standard". Safe to run more than once.
-- =====================================================================

alter table hx_licenses add column if not exists operation text not null default '';
do $$ begin
  alter table hx_licenses add constraint hx_licenses_operation check (operation in ('','manufacturing','cultivation','other'));
exception when duplicate_object then null; end $$;

create or replace function hx_license_op(p_number text, p_type text) returns text
language sql immutable as $$
  select case
    when coalesce(p_number,'') ~* '^\s*CUL' or coalesce(p_type,'') ~* 'cultiv|grow|nursery' then 'cultivation'
    when coalesce(p_number,'') ~* '^\s*MAN' or coalesce(p_type,'') ~* 'manufact|process|extract|infus' then 'manufacturing'
    else 'other' end;
$$;
update hx_licenses set operation = hx_license_op(license_number, license_type) where operation = '';

create or replace function hx_license_op_fill() returns trigger
language plpgsql as $$
begin
  if coalesce(new.operation,'') = '' then new.operation := hx_license_op(new.license_number, new.license_type); end if;
  return new;
end $$;
drop trigger if exists hx_licenses_op_fill on hx_licenses;
create trigger hx_licenses_op_fill before insert or update on hx_licenses for each row execute function hx_license_op_fill();

alter table hx_license_standards add column if not exists scopes text[] not null default '{}';
-- one licensed PDF per CSQ standard (Manufacturing, Extraction, Cultivation)
alter table hx_standards add column if not exists docs jsonb not null default '[]'::jsonb;

-- default Module 3 parts for a license operation
create or replace function hx_csq_default_scopes(p_op text) returns text[]
language sql immutable as $$
  select case p_op when 'cultivation' then array['3A'] when 'manufacturing' then array['3C','3B'] else array[]::text[] end;
$$;

create or replace function hx_license_std_scope_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_op text; v_code text; s text;
begin
  select code into v_code from hx_standards where id = new.standard_id;
  if coalesce(v_code,'') <> 'CSQ-MFG' then return new; end if;
  select coalesce(nullif(operation,''), hx_license_op(license_number, license_type)) into v_op from hx_licenses where id = new.license_id;
  if v_op not in ('manufacturing','cultivation') then
    raise exception 'CSQ applies to manufacturing and cultivation licenses. Set this license''s operation (States and Licenses) first.';
  end if;
  if coalesce(array_length(new.scopes,1),0) = 0 then new.scopes := hx_csq_default_scopes(v_op); end if;
  foreach s in array new.scopes loop
    if v_op = 'cultivation' and s <> '3A' then raise exception 'A cultivation license follows the CSQ Standard for Cultivation (Module 3A) only.'; end if;
    if v_op = 'manufacturing' and s not in ('3B','3C') then raise exception 'The CSQ Standard for Cultivation (Module 3A) is only for cultivation (CUL) licenses.'; end if;
  end loop;
  return new;
end $$;
drop trigger if exists hx_license_standards_scope on hx_license_standards;
create trigger hx_license_standards_scope before insert or update on hx_license_standards for each row execute function hx_license_std_scope_guard();

-- existing adoptions: set their scopes from the license operation
update hx_license_standards a set scopes = hx_csq_default_scopes(coalesce(nullif(l.operation,''), hx_license_op(l.license_number, l.license_type)))
  from hx_licenses l, hx_standards s
 where l.id = a.license_id and s.id = a.standard_id and s.code = 'CSQ-MFG' and coalesce(array_length(a.scopes,1),0) = 0
   and coalesce(nullif(l.operation,''), hx_license_op(l.license_number, l.license_type)) in ('manufacturing','cultivation');

-- when a license's operation changes, its CSQ scopes follow
create or replace function hx_license_op_scopes() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.operation is distinct from old.operation and new.operation in ('manufacturing','cultivation') then
    update hx_license_standards a set scopes = hx_csq_default_scopes(new.operation)
      from hx_standards s where s.id = a.standard_id and s.code = 'CSQ-MFG' and a.license_id = new.id;
  end if;
  return null;
end $$;
drop trigger if exists hx_licenses_op_scopes on hx_licenses;
create trigger hx_licenses_op_scopes after update on hx_licenses for each row execute function hx_license_op_scopes();

-- conformance can only be recorded for Module 3 parts in the license's scope
create or replace function hx_conformance_scope_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_mod text; v_code text; v_scopes text[]; v_op text;
begin
  select c.module, s.code into v_mod, v_code from hx_standard_clauses c join hx_standards s on s.id = c.standard_id where c.id = new.clause_id;
  if coalesce(v_code,'') <> 'CSQ-MFG' or v_mod is null or v_mod not like '3%' then return new; end if;
  select a.scopes into v_scopes from hx_license_standards a where a.license_id = new.license_id and a.standard_id = new.standard_id;
  if v_scopes is null or coalesce(array_length(v_scopes,1),0) = 0 then
    select coalesce(nullif(operation,''), hx_license_op(license_number, license_type)) into v_op from hx_licenses where id = new.license_id;
    v_scopes := hx_csq_default_scopes(v_op);
  end if;
  if not (v_mod = any(v_scopes)) then
    raise exception 'Module % is not in this license''s CSQ scope (%).', v_mod,
      case v_mod when '3A' then 'Cultivation is only for cultivation licenses' else 'Extraction and Manufacturing are only for manufacturing licenses' end;
  end if;
  return new;
end $$;
drop trigger if exists hx_conformance_scope on hx_conformance;
create trigger hx_conformance_scope before insert or update on hx_conformance for each row execute function hx_conformance_scope_guard();

notify pgrst, 'reload schema';
