-- =====================================================================
-- Hendrix QMS  -  Step 15: Training (CSQ 2A.13.2, 1.3c, 1.9f, 4A.2b, 5.1.4)
-- Black Fox / Michigan training matrix (SOP signatures per person, employee
-- training report, compliance snapshot) plus a real training program:
--   * courses with a topic, who must take them (everyone, chosen roles, or at
--     least N people, e.g. CSQ Program Overview, HACCP certified + backup),
--     refresher period (default 12 months) and whether an assessment is required
--   * a course can be met by signing an SOP (read-and-sign training)
--   * training records: who, course, date, trainer and qualification, method,
--     language, assessment result, certificate files; expiry is calculated
--   * records are never deleted (void with a reason, Full access) and are audited
-- Access module 'training': View = see your OWN record, Edit = record training and
--   see the matrix for the license, Full = manage courses, void records.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-14.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_training_courses (
  id                  text primary key,
  state_id            text not null references hx_states(id),
  license_id          text not null references hx_licenses(id),
  license_ids         text[] not null default '{}',
  name                text not null check (length(trim(name)) > 0),
  topic               text not null default 'Job-specific',
  description         text not null default '',
  required_mode       text not null default 'everyone' check (required_mode in ('everyone','roles','at_least','optional')),
  role_ids            text[] not null default '{}',
  min_people          int not null default 1 check (min_people >= 1),
  refresher_months    int not null default 12 check (refresher_months >= 0),
  assessment_required boolean not null default false,
  sop_id              text references hx_sops(id),
  active              boolean not null default true,
  sort                int not null default 0,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);
create unique index if not exists hx_training_courses_name on hx_training_courses(license_id, lower(trim(name)));

create table if not exists hx_training_records (
  id                    text primary key,
  state_id              text not null references hx_states(id),
  license_id            text not null references hx_licenses(id),
  course_id             text not null references hx_training_courses(id),
  user_id               text not null,
  person_name           text not null default '',
  completed_on          date not null,
  expires_on            date,
  trainer_name          text not null default '',
  trainer_qualification text not null default '',
  method                text not null default 'Classroom',
  language              text not null default 'English',
  assessment            text not null default 'Not required' check (assessment in ('Not required','Passed','Failed')),
  score                 text not null default '',
  files                 jsonb not null default '[]'::jsonb,
  notes                 text not null default '',
  recorded_by           text not null default '',
  recorded_by_id        uuid default auth.uid(),
  created_at            timestamptz not null default now(),
  edit_reason           text,
  voided                boolean not null default false,
  void_reason           text,
  voided_by             uuid,
  voided_at             timestamptz
);
create index if not exists hx_training_records_lic on hx_training_records(license_id, completed_on desc);
create index if not exists hx_training_records_user on hx_training_records(user_id);

create or replace function hx_training_course_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_sop record;
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_training_records where course_id = old.id) then
      raise exception 'This course has training records. Switch it off instead of deleting it.';
    end if;
    return old;
  end if;
  if not (new.license_id = any(new.license_ids)) then new.license_ids := array_prepend(new.license_id, new.license_ids); end if;
  if exists (select 1 from unnest(new.license_ids) l left join hx_licenses x on x.id = l where x.id is null or x.state_id <> new.state_id) then
    raise exception 'Every license of a course must belong to its state.';
  end if;
  if new.sop_id is not null then
    select license_ids into v_sop from hx_sops where id = new.sop_id;
    if v_sop.license_ids is null or not (new.license_id = any(v_sop.license_ids)) then raise exception 'That SOP does not apply to this license.'; end if;
  end if;
  if new.required_mode = 'roles' and coalesce(array_length(new.role_ids,1),0) = 0 then raise exception 'Pick at least one role for this course.'; end if;
  new.updated_at := now();
  return new;
end $$;

create or replace function hx_training_record_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare c record; v_name text; a jsonb; n jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Training records are never deleted. Void the record with a reason.'; end if;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  if tg_op = 'INSERT' then
    select * into c from hx_training_courses where id = new.course_id;
    if c.id is null then raise exception 'Unknown course.'; end if;
    if not (new.license_id = any(c.license_ids)) then raise exception 'That course does not apply to this license.'; end if;
    if not exists (select 1 from hx_profiles p where p.id::text = new.user_id and p.approved) then raise exception 'Unknown person.'; end if;
    if new.completed_on > current_date then raise exception 'The training date cannot be in the future.'; end if;
    if c.assessment_required and new.assessment = 'Not required' then raise exception 'This course requires an assessment: record Passed or Failed.'; end if;
    select coalesce(nullif(name,''), email) into new.person_name from hx_profiles where id::text = new.user_id;
    new.expires_on := case when c.refresher_months > 0 then (new.completed_on + make_interval(months => c.refresher_months))::date else null end;
    new.recorded_by := coalesce(v_name,''); new.recorded_by_id := auth.uid(); new.created_at := now();
    new.voided := false; new.void_reason := null; new.voided_by := null; new.voided_at := null; new.edit_reason := null;
    perform set_config('hx.reason', 'Training recorded', true);
    return new;
  end if;
  if old.voided then raise exception 'This training record is void and cannot be changed.'; end if;
  a := to_jsonb(old); n := to_jsonb(new);
  if new.voided then
    if hx_perm('training') < 3 then raise exception 'Only someone with Full access to Training can void a record.'; end if;
    if coalesce(trim(new.void_reason),'') = '' then raise exception 'A reason is required to void a training record.'; end if;
    if (n - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason') is distinct from (a - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason') then
      raise exception 'Void a record without changing anything else.';
    end if;
    new.voided_at := now(); new.voided_by := auth.uid(); new.edit_reason := null;
    perform set_config('hx.reason', trim(new.void_reason), true);
    return new;
  end if;
  -- corrections: files and notes only (add a certificate later); anything else = void and record again
  if (n - 'files' - 'notes' - 'edit_reason') is distinct from (a - 'files' - 'notes' - 'edit_reason') then
    raise exception 'A training record cannot be changed. Void it with a reason and record it again.';
  end if;
  perform set_config('hx.reason', coalesce(nullif(trim(new.edit_reason),''), 'Certificate / notes added'), true);
  new.edit_reason := null;
  return new;
end $$;

drop trigger if exists hx_training_courses_guard on hx_training_courses;
create trigger hx_training_courses_guard before insert or update or delete on hx_training_courses for each row execute function hx_training_course_guard();
drop trigger if exists hx_training_courses_place on hx_training_courses;
create trigger hx_training_courses_place before insert or update on hx_training_courses for each row execute function hx_fl_guard();
drop trigger if exists hx_training_courses_audit on hx_training_courses;
create trigger hx_training_courses_audit after insert or update or delete on hx_training_courses for each row execute function hx_audit();
drop trigger if exists hx_training_records_guard on hx_training_records;
create trigger hx_training_records_guard before insert or update or delete on hx_training_records for each row execute function hx_training_record_guard();
drop trigger if exists hx_training_records_place on hx_training_records;
create trigger hx_training_records_place before insert or update on hx_training_records for each row execute function hx_fl_guard();
drop trigger if exists hx_training_records_audit on hx_training_records;
create trigger hx_training_records_audit after insert or update or delete on hx_training_records for each row execute function hx_audit();

-- the people in the matrix: Edit and up see everyone on the license, others only themselves
create or replace function hx_training_roster(p_lic text) returns table(id text, name text, role_ids text[], license_ids text[], is_admin boolean)
language sql stable security definer set search_path = public as $$
  select p.id::text, coalesce(nullif(p.name,''), p.email), p.role_ids, p.license_ids, p.role = 'admin'
    from hx_profiles p
   where p.approved and hx_lic_ok(p_lic) and hx_perm('training') >= 1
     and (p.role = 'admin' or coalesce(array_length(p.license_ids,1),0) = 0 or p_lic = any(p.license_ids))
     and (hx_perm('training') >= 2 or p.id::text = auth.uid()::text)
   order by 2;
$$;
grant execute on function hx_training_roster(text) to authenticated;

-- SOP signatures for the matrix (Edit+ see everyone, others their own)
create or replace function hx_training_sop_acks(p_lic text) returns table(sop_id text, version text, user_id text, at timestamptz)
language sql stable security definer set search_path = public as $$
  select a.sop_id, a.version, a.user_id::text, a.at from hx_sop_acks a join hx_sops s on s.id = a.sop_id
   where p_lic = any(s.license_ids) and hx_can('training',1,p_lic)
     and (hx_perm('training') >= 2 or a.user_id = auth.uid());
$$;
grant execute on function hx_training_sop_acks(text) to authenticated;

alter table hx_training_courses enable row level security;
alter table hx_training_records enable row level security;
drop policy if exists hx_training_courses_read on hx_training_courses;
drop policy if exists hx_training_courses_insert on hx_training_courses;
drop policy if exists hx_training_courses_update on hx_training_courses;
drop policy if exists hx_training_courses_delete on hx_training_courses;
create policy hx_training_courses_read   on hx_training_courses for select to authenticated using (exists (select 1 from unnest(license_ids) l where hx_can('training',1,l)));
create policy hx_training_courses_insert on hx_training_courses for insert to authenticated with check (hx_can('training',3,license_id));
create policy hx_training_courses_update on hx_training_courses for update to authenticated using (hx_can('training',3,license_id)) with check (hx_can('training',3,license_id));
create policy hx_training_courses_delete on hx_training_courses for delete to authenticated using (hx_can('training',3,license_id));
drop policy if exists hx_training_records_read on hx_training_records;
drop policy if exists hx_training_records_insert on hx_training_records;
drop policy if exists hx_training_records_update on hx_training_records;
create policy hx_training_records_read   on hx_training_records for select to authenticated using (hx_can('training',2,license_id) or (user_id = auth.uid()::text and hx_can('training',1,license_id)));
create policy hx_training_records_insert on hx_training_records for insert to authenticated with check (hx_can('training',2,license_id));
create policy hx_training_records_update on hx_training_records for update to authenticated using (hx_can('training',2,license_id)) with check (hx_can('training',2,license_id));
grant select, insert, update, delete on hx_training_courses to authenticated;
grant select, insert, update on hx_training_records to authenticated;

notify pgrst, 'reload schema';
