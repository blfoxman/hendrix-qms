-- =====================================================================
-- Hendrix QMS  -  Step 20: Online training courses (read, quiz, pass)
-- (CSQ 2A.13.2 a, e, f, g, i, k)
--   * a course can be taken online: lessons to read and a quiz with a pass mark
--   * the correct answers are kept in a separate table only Full access can
--     read; the quiz is graded on the server (hx_course_submit), so answers are
--     never sent to the browser
--   * every attempt is kept (score, answers, time spent, content version)
--   * a pass records the training automatically: date, "Passed", the score,
--     the content version and who approved the content (trainer qualification)
--   * content is published by Full access only; every change to published
--     content creates a new content version, stamped with who published it
--   * outside certifications (HACCP, CSQ Program Overview) are not taken online
--     (certificate upload stays the evidence)
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-19.
-- Also redeploy the hendrix-ai Edge Function from the new hendrix-ai.ts (AI drafts
-- of the state regulatory course). Safe to run more than once.
-- =====================================================================

alter table hx_training_courses add column if not exists online          boolean not null default false;
alter table hx_training_courses add column if not exists lessons         jsonb   not null default '[]'::jsonb;
alter table hx_training_courses add column if not exists quiz            jsonb   not null default '[]'::jsonb;
alter table hx_training_courses add column if not exists pass_mark       int     not null default 80;
alter table hx_training_courses add column if not exists content_status  text    not null default 'none';
alter table hx_training_courses add column if not exists content_version int     not null default 0;
alter table hx_training_courses add column if not exists content_source  text    not null default '';
alter table hx_training_courses add column if not exists content_by      text    not null default '';
alter table hx_training_courses add column if not exists content_at      timestamptz;
alter table hx_training_courses add column if not exists minutes         int     not null default 15;
do $$ begin
  alter table hx_training_courses add constraint hx_training_courses_pass check (pass_mark between 50 and 100);
exception when duplicate_object then null; end $$;
do $$ begin
  alter table hx_training_courses add constraint hx_training_courses_cstatus check (content_status in ('none','draft','published'));
exception when duplicate_object then null; end $$;

-- answer key: index of the correct option and an explanation, per question
create table if not exists hx_training_keys (
  course_id   text primary key references hx_training_courses(id) on delete cascade,
  answers     jsonb not null default '[]'::jsonb,
  explain     jsonb not null default '[]'::jsonb,
  updated_at  timestamptz not null default now()
);

create table if not exists hx_training_attempts (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  course_id        text not null references hx_training_courses(id),
  user_id          text not null,
  person_name      text not null default '',
  content_version  int not null default 0,
  started_at       timestamptz,
  finished_at      timestamptz not null default now(),
  minutes          int,
  answers          jsonb not null default '[]'::jsonb,
  correct          int not null default 0,
  total            int not null default 0,
  score            int not null default 0,
  passed           boolean not null default false,
  record_id        text
);
create index if not exists hx_training_attempts_user on hx_training_attempts(user_id, course_id);
create index if not exists hx_training_attempts_lic on hx_training_attempts(license_id, finished_at desc);

-- publishing rules for course content
create or replace function hx_course_content_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k record;
begin
  if new.online and new.topic in ('HACCP','CSQ program') then
    raise exception 'This course is an outside certification. Record it with the certificate instead of an online quiz.';
  end if;
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
drop trigger if exists hx_training_courses_content on hx_training_courses;
create trigger hx_training_courses_content before insert or update on hx_training_courses for each row execute function hx_course_content_guard();

create or replace function hx_training_key_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare c record;
begin
  select * into c from hx_training_courses where id = coalesce(new.course_id, old.course_id);
  if c.id is null or not hx_can('training', 3, c.license_id) then raise exception 'Only someone with Full access to Training can change quiz answers.'; end if;
  if tg_op <> 'DELETE' then new.updated_at := now(); return new; end if;
  return old;
end $$;
drop trigger if exists hx_training_keys_guard on hx_training_keys;
create trigger hx_training_keys_guard before insert or update or delete on hx_training_keys for each row execute function hx_training_key_guard();

-- grade a quiz on the server and record the training when it is passed
create or replace function hx_course_submit(p_course text, p_lic text, p_answers jsonb, p_started timestamptz) returns jsonb
language plpgsql security definer set search_path = public as $$
declare c record; k record; l record; p record; v_total int; v_ok int := 0; i int; v_score int; v_pass boolean; v_att text; v_rec text := null; v_wrong jsonb := '[]'::jsonb; v_min int;
begin
  select * into c from hx_training_courses where id = p_course;
  if c.id is null or not c.active or not c.online or c.content_status <> 'published' then raise exception 'This course is not available online.'; end if;
  if not (p_lic = any(c.license_ids)) then raise exception 'This course does not apply to this license.'; end if;
  if not hx_can('training', 1, p_lic) then raise exception 'You need access to Training.'; end if;
  select * into p from hx_profiles where id::text = auth.uid()::text and approved;
  if p.id is null then raise exception 'Your account is not approved yet.'; end if;
  if not (p.role = 'admin' or coalesce(array_length(p.license_ids,1),0) = 0 or p_lic = any(p.license_ids)) then raise exception 'You are not assigned to this license.'; end if;
  select * into k from hx_training_keys where course_id = c.id;
  v_total := jsonb_array_length(coalesce(k.answers, '[]'::jsonb));
  if v_total = 0 or v_total <> jsonb_array_length(c.quiz) then raise exception 'This quiz is not ready. Ask a manager to check the answers.'; end if;
  if jsonb_typeof(p_answers) <> 'array' or jsonb_array_length(p_answers) <> v_total then raise exception 'Answer every question.'; end if;
  for i in 0 .. v_total - 1 loop
    if (p_answers->i) = (k.answers->i) then v_ok := v_ok + 1;
    else v_wrong := v_wrong || jsonb_build_object('q', i, 'explain', coalesce(k.explain->>i, '')); end if;
  end loop;
  v_score := round(v_ok * 100.0 / v_total);
  v_pass := v_score >= c.pass_mark;
  v_min := case when p_started is not null and p_started <= now() then greatest(0, round(extract(epoch from (now() - p_started)) / 60.0))::int else null end;
  select * into l from hx_licenses where id = p_lic;
  v_att := 'att-' || replace(gen_random_uuid()::text, '-', '');
  if v_pass then
    v_rec := 'trr-' || replace(gen_random_uuid()::text, '-', '');
    insert into hx_training_records(id, state_id, license_id, course_id, user_id, completed_on, trainer_name, trainer_qualification, method, language, assessment, score, notes)
    values (v_rec, l.state_id, p_lic, c.id, p.id::text, current_date, 'Hendrix online course',
            'Course content version ' || c.content_version || ' approved by ' || coalesce(nullif(c.content_by,''), 'Full access') || coalesce(' (' || nullif(c.content_source,'') || ')', ''),
            'Online course', 'English', 'Passed', v_ok || '/' || v_total || ' (' || v_score || '%)', 'Online attempt ' || v_att || coalesce(', ' || v_min || ' min', ''));
  end if;
  insert into hx_training_attempts(id, state_id, license_id, course_id, user_id, person_name, content_version, started_at, minutes, answers, correct, total, score, passed, record_id)
  values (v_att, l.state_id, p_lic, c.id, p.id::text, coalesce(nullif(p.name,''), p.email), c.content_version, p_started, v_min, p_answers, v_ok, v_total, v_score, v_pass, v_rec);
  return jsonb_build_object('attempt', v_att, 'correct', v_ok, 'total', v_total, 'score', v_score, 'pass_mark', c.pass_mark, 'passed', v_pass, 'record_id', v_rec, 'wrong', v_wrong);
end $$;
grant execute on function hx_course_submit(text, text, jsonb, timestamptz) to authenticated;

alter table hx_training_keys enable row level security;
alter table hx_training_attempts enable row level security;
drop policy if exists hx_training_keys_all on hx_training_keys;
create policy hx_training_keys_all on hx_training_keys for all to authenticated
  using (exists (select 1 from hx_training_courses c where c.id = course_id and hx_can('training',3,c.license_id)))
  with check (exists (select 1 from hx_training_courses c where c.id = course_id and hx_can('training',3,c.license_id)));
drop policy if exists hx_training_attempts_read on hx_training_attempts;
create policy hx_training_attempts_read on hx_training_attempts for select to authenticated
  using (hx_can('training',2,license_id) or (user_id = auth.uid()::text and hx_can('training',1,license_id)));
grant select, insert, update, delete on hx_training_keys to authenticated;
grant select on hx_training_attempts to authenticated;

notify pgrst, 'reload schema';
