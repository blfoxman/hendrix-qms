-- =====================================================================
-- Hendrix QMS  -  Step 9: Testing (lab submissions, results, COAs)
-- Black Fox Testing module: a batch is submitted for mandatory testing
-- (one record per FINAL package tag), status is tracked, the COA file is
-- stored privately and can be read by AI (hendrix-ai edge function).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-8.
-- Safe to run more than once.
--
-- Rules built into the database:
--   * every test belongs to one state and one license; a linked batch must be
--     of that same license and not void; batch details are copied by the database
--   * one live test record per batch + package tag
--   * test records are never deleted: they are VOIDED with a reason (Full access)
--   * changing a final result (Passed / Failed) needs Full access and a reason
--   * COA files go in a private storage bucket; files cannot be replaced or deleted
-- Access module: 'testing'  (View / Edit / Full), set on Roles or per person.
-- =====================================================================

create table if not exists hx_tests (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  batch_id         text references hx_batches(id),
  batch_number     text not null default '',
  batch_type       text not null default '',
  sku              text not null default '',
  flavor           text not null default '',
  tag              text not null default '',
  tag_label        text not null default '',
  sample_tag       text not null default '',
  lab_name         text not null default '',
  lab_license      text not null default '',
  status           text not null default 'Pending' check (status in ('Pending','Submitted','Passed','Failed','Retest')),
  submitted_at     timestamptz,
  result_at        timestamptz,
  result_thc       text not null default '',
  result_cbd       text not null default '',
  result_notes     text not null default '',
  notes            text not null default '',
  coa_path         text not null default '',
  coa_filename     text not null default '',
  coa_analysis     jsonb,
  performed_by     text not null default '',
  created_by       uuid default auth.uid(),
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now(),
  edit_reason      text,
  voided           boolean not null default false,
  void_reason      text,
  voided_by        uuid,
  voided_at        timestamptz
);
create unique index if not exists hx_tests_batch_tag on hx_tests(batch_id, upper(regexp_replace(tag, '[^A-Za-z0-9]', '', 'g')))
  where batch_id is not null and not voided;
create index if not exists hx_tests_lic on hx_tests(license_id, created_at desc);
create index if not exists hx_tests_batch on hx_tests(batch_id);

create or replace function hx_test_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; a jsonb; n jsonb; k text;
begin
  if tg_op = 'DELETE' then
    raise exception 'Test records cannot be deleted. Void the record with a reason instead.';
  end if;

  if tg_op = 'INSERT' then
    if new.batch_id is not null then
      select * into b from hx_batches where id = new.batch_id;
      if b.id is null then raise exception 'Unknown batch.'; end if;
      if b.license_id <> new.license_id or b.state_id <> new.state_id then raise exception 'That batch belongs to a different license.'; end if;
      if b.voided then raise exception 'That batch is void.'; end if;
      new.batch_number := b.batch_number; new.batch_type := b.batch_type; new.sku := b.sku; new.flavor := b.flavor;
    end if;
    if new.status = 'Submitted' and new.submitted_at is null then new.submitted_at := now(); end if;
    if new.status in ('Passed','Failed') and new.result_at is null then new.result_at := now(); end if;
    new.edit_reason := null; new.voided := false; new.void_reason := null; new.voided_by := null; new.voided_at := null;
    return new;
  end if;

  -- UPDATE
  if old.voided then raise exception 'This test record is void and cannot be changed.'; end if;
  a := to_jsonb(old); n := to_jsonb(new);
  foreach k in array array['id','batch_id','batch_number','batch_type','sku','flavor','created_by','created_at'] loop
    if (a -> k) is distinct from (n -> k) then
      raise exception 'The % of a test record cannot be changed.', replace(k, '_', ' ');
    end if;
  end loop;
  if new.voided then
    if hx_perm('testing') < 3 then raise exception 'Only someone with Full access to Testing can void a record.'; end if;
    if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
    if (n - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason' - 'updated_at')
       is distinct from (a - 'voided' - 'void_reason' - 'voided_by' - 'voided_at' - 'edit_reason' - 'updated_at') then
      raise exception 'Void a record without changing anything else.';
    end if;
    new.voided_at := now(); new.voided_by := auth.uid(); new.edit_reason := null;
    perform set_config('hx.reason', trim(new.void_reason), true);
    return new;
  end if;
  if old.status in ('Passed','Failed') and new.status is distinct from old.status then
    if hx_perm('testing') < 3 then
      raise exception 'Changing a final result (%) needs Full access to Testing.', old.status;
    end if;
    if coalesce(trim(new.edit_reason), '') = '' then
      raise exception 'A reason is required to change a final result.';
    end if;
  end if;
  if new.coa_path is distinct from old.coa_path and coalesce(old.coa_path,'') <> '' and coalesce(trim(new.edit_reason),'') = '' then
    new.edit_reason := 'COA replaced';
  end if;
  if new.status = 'Submitted' and new.submitted_at is null then new.submitted_at := now(); end if;
  if new.status in ('Passed','Failed') and new.status is distinct from old.status then new.result_at := now(); end if;
  perform set_config('hx.reason', coalesce(nullif(trim(new.edit_reason),''), 'Testing record updated'), true);
  new.edit_reason := null;
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists hx_tests_guard on hx_tests;
create trigger hx_tests_guard before insert or update or delete on hx_tests for each row execute function hx_test_guard();
drop trigger if exists hx_tests_place on hx_tests;
create trigger hx_tests_place before insert or update on hx_tests for each row execute function hx_fl_guard();
drop trigger if exists hx_tests_audit on hx_tests;
create trigger hx_tests_audit after insert or update or delete on hx_tests for each row execute function hx_audit();

alter table hx_tests enable row level security;
drop policy if exists hx_tests_read on hx_tests;
drop policy if exists hx_tests_insert on hx_tests;
drop policy if exists hx_tests_update on hx_tests;
create policy hx_tests_read   on hx_tests for select to authenticated using (hx_can('testing',1,license_id));
create policy hx_tests_insert on hx_tests for insert to authenticated with check (hx_can('testing',2,license_id));
create policy hx_tests_update on hx_tests for update to authenticated using (hx_can('testing',2,license_id)) with check (hx_can('testing',2,license_id));
grant select, insert, update on hx_tests to authenticated;

-- ---------- private file storage for COAs (and later other documents) ----------
insert into storage.buckets (id, name, public)
values ('hendrix-files', 'hendrix-files', false)
on conflict (id) do update set public = false;

drop policy if exists hx_files_read on storage.objects;
drop policy if exists hx_files_insert on storage.objects;
create policy hx_files_read on storage.objects for select to authenticated
  using (bucket_id = 'hendrix-files' and hx_fl_is_approved());
create policy hx_files_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'hendrix-files' and hx_fl_is_approved());
-- no update / delete policies: a stored COA cannot be overwritten or removed

notify pgrst, 'reload schema';
