-- =====================================================================
-- Hendrix QMS  -  Step 23: Shared training across licenses
-- One person, one pass: training done once counts at every license where the
-- same course applies, and a course's online content is written once.
--   * hx_training_courses.share_key links the copies of one course:
--       csq:<topic>     the CSQ starter courses (cGMP, cannabis safety, hygiene,
--                       product defense, chemical safety, CSQ Program Overview,
--                       HACCP, cGACP, Extraction) - every license, both states
--       law:<state id>  the state regulatory course - every license of that state
--       custom:<name>   a course you mark "same course at all licenses"
--       (blank)         this license only (SOP-linked and job-specific courses)
--   * hx_training_shared(license): the valid records a person has for the same
--     course at OTHER licenses, so the matrix, "My training", dashboards and
--     PDFs count them (the record itself stays where the training was done)
--   * publishing a shared course copies its lessons, quiz and answer key to
--     every license that shares it (where the publisher has Full access);
--     a new license's copy starts from the latest published version
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-22.
-- Then open Training once (Full access): Hendrix links the existing courses.
-- Safe to run more than once.
-- =====================================================================

alter table hx_training_courses add column if not exists share_key text;
create index if not exists hx_training_courses_share on hx_training_courses(share_key) where share_key is not null;

-- the copy of a shared course is created / updated by the server, not edited
create or replace function hx_course_content_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k record;
begin
  if new.online and new.topic in ('HACCP','CSQ program') then
    raise exception 'This course is an outside certification. Record it with the certificate instead of an online quiz.';
  end if;
  -- shared content copied from another license: keep its version, author and date
  if coalesce(current_setting('hx.internal', true), '') = 'on' then return new; end if;
  if tg_op = 'UPDATE' and (new.lessons, new.quiz, new.pass_mark, new.online, new.content_status, new.content_source, new.minutes)
       is not distinct from (old.lessons, old.quiz, old.pass_mark, old.online, old.content_status, old.content_source, old.minutes) then
    new.content_version := old.content_version; new.content_by := old.content_by; new.content_at := old.content_at;
    return new;
  end if;
  if new.content_status = 'published' then
    if jsonb_array_length(new.lessons) = 0 then raise exception 'Add at least one lesson before publishing.'; end if;
    if jsonb_array_length(new.quiz) = 0 then raise exception 'Add quiz questions before publishing.'; end if;
    select * into k from hx_training_keys where course_id = new.id;
    if k.course_id is null or jsonb_array_length(k.answers) <> jsonb_array_length(new.quiz) then raise exception 'Every quiz question needs its correct answer before publishing.'; end if;
    if not new.assessment_required then new.assessment_required := true; end if;
    new.content_version := coalesce(case when tg_op = 'UPDATE' then old.content_version end, 0) + 1;
    new.content_by := coalesce(hx_me(), ''); new.content_at := now();
    perform set_config('hx.reason', 'Online course published (version ' || new.content_version || ')', true);
  else
    if tg_op = 'UPDATE' then new.content_version := old.content_version; new.content_by := old.content_by; new.content_at := old.content_at; end if;
  end if;
  return new;
end $$;

-- copy published content between the licenses that share a course
create or replace function hx_course_copy(p_src text, p_dst text, p_why text) returns void
language plpgsql security definer set search_path = public as $$
declare s record; k record;
begin
  select * into s from hx_training_courses where id = p_src;
  select * into k from hx_training_keys where course_id = p_src;
  if s.id is null or k.course_id is null then return; end if;
  perform set_config('hx.internal', 'on', true);
  insert into hx_training_keys(course_id, answers, explain) values (p_dst, k.answers, k.explain)
    on conflict (course_id) do update set answers = excluded.answers, explain = excluded.explain;
  perform set_config('hx.reason', p_why, true);
  update hx_training_courses set online = s.online, lessons = s.lessons, quiz = s.quiz, pass_mark = s.pass_mark, minutes = s.minutes,
         content_source = s.content_source, content_status = 'published', assessment_required = true,
         content_version = s.content_version, content_by = s.content_by, content_at = s.content_at
   where id = p_dst;
  perform set_config('hx.internal', '', true);
end $$;
revoke all on function hx_course_copy(text, text, text) from public;

create or replace function hx_course_share_sync() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; src record; v_from text;
begin
  if coalesce(current_setting('hx.internal', true), '') = 'on' or new.share_key is null then return null; end if;
  if tg_op = 'UPDATE' and new.content_status = 'published' and new.content_version is distinct from old.content_version then
    -- published here: every other license that shares the course gets the same version
    select name into v_from from hx_licenses where id = new.license_id;
    for s in select c.* from hx_training_courses c where c.share_key = new.share_key and c.id <> new.id loop
      if hx_can('training', 3, s.license_id) then
        perform hx_course_copy(new.id, s.id, 'Shared course content v' || new.content_version || ' published at ' || coalesce(v_from, new.license_id));
      end if;
    end loop;
  elsif new.content_status <> 'published' and (tg_op = 'INSERT' or old.share_key is distinct from new.share_key) then
    -- new or newly linked copy: start from the latest published version elsewhere
    select c.* into src from hx_training_courses c where c.share_key = new.share_key and c.id <> new.id and c.content_status = 'published'
     order by c.content_at desc nulls last limit 1;
    if src.id is not null and hx_can('training', 3, new.license_id) then
      select name into v_from from hx_licenses where id = src.license_id;
      perform hx_course_copy(src.id, new.id, 'Shared course content v' || src.content_version || ' from ' || coalesce(v_from, src.license_id));
    end if;
  end if;
  return null;
end $$;
drop trigger if exists hx_training_courses_share on hx_training_courses;
create trigger hx_training_courses_share after insert or update on hx_training_courses for each row execute function hx_course_share_sync();

-- training a person did for the same course at other licenses (records stay where they were made)
create or replace function hx_training_shared(p_lic text)
returns table(id text, course_id text, share_key text, user_id text, person_name text, completed_on date, expires_on date,
              trainer_name text, trainer_qualification text, method text, assessment text, score text, files jsonb,
              license_id text, license_name text, state_name text)
language sql stable security definer set search_path = public as $$
  select r.id, r.course_id, c.share_key, r.user_id, r.person_name, r.completed_on, r.expires_on,
         r.trainer_name, r.trainer_qualification, r.method, r.assessment, r.score, r.files,
         r.license_id, l.name, s.name
    from hx_training_records r
    join hx_training_courses c on c.id = r.course_id
    join hx_licenses l on l.id = r.license_id
    join hx_states s on s.id = l.state_id
   where hx_can('training', 1, p_lic)
     and c.share_key is not null
     and c.share_key in (select x.share_key from hx_training_courses x where p_lic = any(x.license_ids) and x.share_key is not null)
     and not (p_lic = any(c.license_ids))
     and not r.voided and r.assessment <> 'Failed'
     and r.user_id in (select ro.id from hx_training_roster(p_lic) ro);
$$;
grant execute on function hx_training_shared(text) to authenticated;

notify pgrst, 'reload schema';
