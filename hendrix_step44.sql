-- =====================================================================
-- Hendrix QMS  -  Step 44: CSQ Certification Program Overview as an online course
--
--   CSQ 2A.13.2 h asks that at least one person responsible for CSQ conformance
--   completes "the CSQ Certification Program Overview training course or
--   equivalent". Hendrix now has an equivalent online course (lessons and a quiz
--   written from the CSQ v2.0 standards and audit checklist), so the course
--   "CSQ Certification Program Overview" can be taken online; a certificate from
--   the program's own course can still be uploaded instead.
--   The HACCP certification course stays certificate-only: CSQ 4A.2 needs a
--   certificate from an International HACCP Alliance approved course.
--   (The separate "HACCP basics" online course is awareness and refresher.)
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-43.
-- Then open Training once (Full access): the course content loads as a draft
-- to review and publish. Safe to run more than once.
-- =====================================================================

-- topics that can only be met with an outside certificate
create or replace function hx_course_cert_only(p_topic text) returns boolean
language sql immutable as $$ select coalesce(p_topic, '') = 'HACCP'; $$;

create or replace function hx_course_content_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k record;
begin
  if new.online and hx_course_cert_only(new.topic) then
    raise exception 'This course is an outside certification (HACCP certificate from an International HACCP Alliance approved course). Record it with the certificate instead of an online quiz.';
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

notify pgrst, 'reload schema';
select 'Hendrix step 44 (CSQ Program Overview online course) installed' as result;
