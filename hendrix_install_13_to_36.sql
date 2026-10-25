-- =====================================================================
-- Hendrix QMS - ONE-FILE INSTALL of steps 13 to 36 (SOPs ... Settings, Line Map)
-- For a Hendrix database that already has steps 1-12.
-- Paste the whole file into Supabase > SQL Editor > Run (one time).
-- Safe to run again: every step can run more than once.
-- Step 35 (Import from Excel / Sheets) needs no SQL.
-- The separate hendrix_stepNN.sql files stay in the repo; this is the same SQL, in order.
-- =====================================================================

-- ###################################################################
-- ### hendrix_step13.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 13: SOPs and document control
-- Black Fox SOP module (manual SOPs, AI generator, revise, folders, read-and-sign
-- with signature, PDF) plus CSQ document control (CSQ 1.1, 1.4, 2A.12.1, 5.2):
--   * every SOP has a document number (unique per license), version, status
--   * only someone with Full access to SOPs can publish (approve) an SOP; who
--     approved it and when is stamped by the database
--   * changing a published SOP is a REVISION: a new version number and a reason
--     are required, the old version is kept unchanged in hx_sop_versions, and
--     everyone must sign the new version
--   * effective date and next review date (default 1 year) are kept for every SOP
--   * signatures (read and understood) are permanent: one per person, SOP and version,
--     never changed or deleted, and only ever in the signer's own name
--   * published and archived SOPs are never deleted; only drafts can be deleted
-- Access module 'sops': View = read and sign, Edit = write drafts (manual or AI),
--   Full = publish / approve, revise published SOPs, archive, delete drafts.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-12.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_sops (
  id                    text primary key,
  state_id              text not null references hx_states(id),
  license_id            text not null references hx_licenses(id),
  license_ids           text[] not null default '{}',
  sop_number            text not null default '',
  title                 text not null check (length(trim(title)) > 0),
  folder                text not null default 'General',
  previous_folder       text not null default '',
  category              text not null default '',
  description           text not null default '',
  steps                 jsonb not null default '[]'::jsonb,
  generated_content     jsonb,
  regulatory_references jsonb not null default '[]'::jsonb,
  attachments           jsonb not null default '[]'::jsonb,
  version               text not null default '1.0',
  status                text not null default 'draft' check (status in ('draft','published','archived')),
  target_mode           text not null default 'license' check (target_mode in ('license','roles','people')),
  target_role_ids       text[] not null default '{}',
  target_user_ids       text[] not null default '{}',
  effective_date        date,
  next_review           date,
  approved_by           text not null default '',
  approved_by_id        uuid,
  approved_at           timestamptz,
  revision_note         text not null default '',
  revised_by            text not null default '',
  revised_at            timestamptz,
  created_by            text not null default '',
  created_by_id         uuid default auth.uid(),
  created_at            timestamptz not null default now(),
  updated_by            text not null default '',
  updated_at            timestamptz not null default now()
);
create unique index if not exists hx_sops_number on hx_sops(license_id, lower(trim(sop_number))) where trim(sop_number) <> '';
create index if not exists hx_sops_lic on hx_sops(license_id, status);

create table if not exists hx_sop_versions (
  id             text primary key,
  sop_id         text not null references hx_sops(id) on delete cascade,
  state_id       text not null,
  license_id     text not null,
  version        text not null,
  snapshot       jsonb not null,
  revision_note  text not null default '',
  superseded_by  text not null default '',
  superseded_at  timestamptz not null default now()
);
create index if not exists hx_sop_versions_sop on hx_sop_versions(sop_id, superseded_at desc);

create table if not exists hx_sop_acks (
  id          text primary key,
  sop_id      text not null references hx_sops(id) on delete cascade,
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  version     text not null,
  user_id     uuid not null default auth.uid(),
  name        text not null default '',
  role_names  text not null default '',
  signature   text,
  at          timestamptz not null default now()
);
create unique index if not exists hx_sop_acks_one on hx_sop_acks(sop_id, version, user_id);
create index if not exists hx_sop_acks_lic on hx_sop_acks(license_id, at desc);

-- ---------- guards ----------
create or replace function hx_sop_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_name text; v_content_changed boolean;
begin
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  if tg_op = 'DELETE' then
    if old.status <> 'draft' then
      raise exception 'Published and archived SOPs are controlled documents and cannot be deleted. Archive it instead.';
    end if;
    if hx_perm('sops') < 3 then raise exception 'Only someone with Full access to SOPs can delete a draft.'; end if;
    return old;
  end if;

  if new.folder not in ('General','Production','HR','Compliance','Security','Distribution','Sales','Archived') then
    raise exception 'Unknown folder.';
  end if;
  if not (new.license_id = any(new.license_ids)) then new.license_ids := array_prepend(new.license_id, new.license_ids); end if;
  if exists (select 1 from unnest(new.license_ids) l left join hx_licenses x on x.id = l where x.id is null or x.state_id <> new.state_id) then
    raise exception 'Every license of an SOP must belong to its state.';
  end if;
  new.updated_at := now();
  new.updated_by := coalesce(v_name, new.updated_by);

  if tg_op = 'INSERT' then
    new.created_by := coalesce(v_name, new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status = 'archived' then raise exception 'A new SOP cannot start archived.'; end if;
    if new.status = 'published' then
      if hx_perm('sops') < 3 then raise exception 'Only someone with Full access to SOPs can publish (approve) an SOP. Save it as a draft.'; end if;
      new.approved_by := coalesce(v_name,''); new.approved_by_id := auth.uid(); new.approved_at := now();
      new.effective_date := coalesce(new.effective_date, current_date);
      new.next_review := coalesce(new.next_review, (coalesce(new.effective_date, current_date) + interval '1 year')::date);
    else
      new.approved_by := ''; new.approved_by_id := null; new.approved_at := null;
    end if;
    perform set_config('hx.reason', 'SOP created', true);
    return new;
  end if;

  -- UPDATE
  if new.id <> old.id or new.created_by_id is distinct from old.created_by_id or new.created_at <> old.created_at then
    raise exception 'The identity of an SOP cannot be changed.';
  end if;
  if new.state_id <> old.state_id or new.license_id <> old.license_id then
    raise exception 'An SOP cannot be moved to another state or primary license.';
  end if;
  v_content_changed := new.title is distinct from old.title or new.description is distinct from old.description
    or new.steps is distinct from old.steps or new.generated_content is distinct from old.generated_content
    or new.regulatory_references is distinct from old.regulatory_references or new.attachments is distinct from old.attachments
    or new.sop_number is distinct from old.sop_number;

  if old.status = 'draft' then
    if hx_perm('sops') < 2 then raise exception 'You need Edit access to SOPs to change a draft.'; end if;
    if new.status = 'published' then
      if hx_perm('sops') < 3 then raise exception 'Only someone with Full access to SOPs can publish (approve) an SOP.'; end if;
      new.approved_by := coalesce(v_name,''); new.approved_by_id := auth.uid(); new.approved_at := now();
      new.effective_date := coalesce(new.effective_date, current_date);
      new.next_review := coalesce(new.next_review, (new.effective_date + interval '1 year')::date);
      perform set_config('hx.reason', 'SOP approved and published (v' || new.version || ')', true);
    elsif new.status = 'archived' then
      raise exception 'Publish a draft or delete it; drafts are not archived.';
    else
      perform set_config('hx.reason', 'Draft updated', true);
    end if;
    return new;
  end if;

  -- published or archived: Full access only
  if hx_perm('sops') < 3 then raise exception 'Only someone with Full access to SOPs can change a published SOP.'; end if;
  if new.status = 'draft' then raise exception 'A published SOP cannot go back to draft. Revise it instead.'; end if;
  if new.approved_by is distinct from old.approved_by or new.approved_by_id is distinct from old.approved_by_id then
    if not (v_content_changed or new.version is distinct from old.version) then
      raise exception 'Approval stamps are set by the system.';
    end if;
  end if;

  if v_content_changed or new.version is distinct from old.version then
    -- a revision
    if new.version is not distinct from old.version then
      raise exception 'Changing a published SOP is a revision: give it a new version number.';
    end if;
    if coalesce(trim(new.revision_note), '') = '' or new.revision_note is not distinct from old.revision_note then
      raise exception 'A reason for the revision is required.';
    end if;
    insert into hx_sop_versions(id, sop_id, state_id, license_id, version, snapshot, revision_note, superseded_by)
    values ('sv-' || to_char(clock_timestamp(),'YYMMDDHH24MISSMS') || substr(md5(random()::text),1,4), old.id, old.state_id, old.license_id, old.version,
            to_jsonb(old), new.revision_note, coalesce(v_name,''));
    new.revised_by := coalesce(v_name,''); new.revised_at := now();
    new.approved_by := coalesce(v_name,''); new.approved_by_id := auth.uid(); new.approved_at := now();
    new.status := case when new.status = 'archived' then 'archived' else 'published' end;
    new.effective_date := current_date;
    new.next_review := (current_date + interval '1 year')::date;
    perform set_config('hx.reason', 'Revised to v' || new.version || ': ' || trim(new.revision_note), true);
    return new;
  end if;

  if new.status = 'archived' and old.status <> 'archived' then
    new.previous_folder := old.folder; new.folder := 'Archived';
    perform set_config('hx.reason', 'SOP archived', true);
  elsif new.status = 'published' and old.status = 'archived' then
    new.folder := coalesce(nullif(old.previous_folder,''), 'General');
    perform set_config('hx.reason', 'SOP restored from archive', true);
  else
    perform set_config('hx.reason', 'SOP details updated', true);
  end if;
  return new;
end $$;

create or replace function hx_sop_version_guard() returns trigger
language plpgsql as $$
begin
  if tg_op = 'DELETE' and exists (select 1 from hx_sops where id = old.sop_id) then
    raise exception 'Superseded SOP versions are kept permanently.';
  end if;
  if tg_op = 'UPDATE' then raise exception 'Superseded SOP versions cannot be changed.'; end if;
  return coalesce(new, old);
end $$;

create or replace function hx_sop_ack_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; v_name text; v_roles text;
begin
  if tg_op <> 'INSERT' then raise exception 'SOP signatures are permanent and cannot be changed or deleted.'; end if;
  select * into s from hx_sops where id = new.sop_id;
  if s.id is null then raise exception 'Unknown SOP.'; end if;
  if s.status <> 'published' then raise exception 'Only a published SOP can be signed.'; end if;
  if new.user_id is distinct from auth.uid() then raise exception 'You can only sign in your own name.'; end if;
  if coalesce(length(new.signature),0) < 50 then raise exception 'Draw your signature to acknowledge this SOP.'; end if;
  select coalesce(nullif(p.name,''), p.email),
         coalesce((select string_agg(r.name, ', ' order by r.name) from hx_roles r where r.id = any(p.role_ids)), '')
    into v_name, v_roles from hx_profiles p where p.id::text = auth.uid()::text;
  new.state_id := s.state_id; new.version := s.version;
  if new.license_id is null or not (new.license_id = any(s.license_ids)) then new.license_id := s.license_id; end if;
  new.name := coalesce(v_name, new.name); new.role_names := v_roles; new.at := now();
  perform set_config('hx.reason', 'Signed: read and understood v' || s.version, true);
  return new;
end $$;

drop trigger if exists hx_sops_guard on hx_sops;
create trigger hx_sops_guard before insert or update or delete on hx_sops for each row execute function hx_sop_guard();
drop trigger if exists hx_sops_audit on hx_sops;
create trigger hx_sops_audit after insert or update or delete on hx_sops for each row execute function hx_audit();
drop trigger if exists hx_sop_versions_guard on hx_sop_versions;
create trigger hx_sop_versions_guard before update or delete on hx_sop_versions for each row execute function hx_sop_version_guard();
drop trigger if exists hx_sop_acks_guard on hx_sop_acks;
create trigger hx_sop_acks_guard before insert or update or delete on hx_sop_acks for each row execute function hx_sop_ack_guard();
drop trigger if exists hx_sop_acks_audit on hx_sop_acks;
create trigger hx_sop_acks_audit after insert on hx_sop_acks for each row execute function hx_audit();

-- who has to sign (for progress and pending lists): approved people, names and roles only
create or replace function hx_sop_roster(p_lic text) returns table(id text, name text, role_ids text[], license_ids text[], is_admin boolean)
language sql stable security definer set search_path = public as $$
  select p.id::text, coalesce(nullif(p.name,''), p.email), p.role_ids, p.license_ids, p.role = 'admin'
    from hx_profiles p
   where p.approved and hx_perm('sops') >= 2 and hx_lic_ok(p_lic)
     and (p.role = 'admin' or coalesce(array_length(p.license_ids,1),0) = 0 or p_lic = any(p.license_ids))
   order by 2;
$$;
grant execute on function hx_sop_roster(text) to authenticated;

-- ---------- access ----------
alter table hx_sops enable row level security;
alter table hx_sop_versions enable row level security;
alter table hx_sop_acks enable row level security;

drop policy if exists hx_sops_read on hx_sops;
drop policy if exists hx_sops_insert on hx_sops;
drop policy if exists hx_sops_update on hx_sops;
drop policy if exists hx_sops_delete on hx_sops;
-- drafts: Edit and up; archived: Full; published: everyone with View on one of its licenses
create policy hx_sops_read on hx_sops for select to authenticated using (
  exists (select 1 from unnest(license_ids) l where hx_can('sops',1,l))
  and (status = 'published' or (status = 'draft' and hx_perm('sops') >= 2) or (status = 'archived' and hx_perm('sops') >= 3)));
create policy hx_sops_insert on hx_sops for insert to authenticated with check (hx_can('sops',2,license_id));
create policy hx_sops_update on hx_sops for update to authenticated using (hx_can('sops',2,license_id)) with check (hx_can('sops',2,license_id));
create policy hx_sops_delete on hx_sops for delete to authenticated using (hx_can('sops',3,license_id));

drop policy if exists hx_sop_versions_read on hx_sop_versions;
create policy hx_sop_versions_read on hx_sop_versions for select to authenticated using (hx_can('sops',1,license_id));

drop policy if exists hx_sop_acks_read on hx_sop_acks;
drop policy if exists hx_sop_acks_insert on hx_sop_acks;
create policy hx_sop_acks_read on hx_sop_acks for select to authenticated using (user_id = auth.uid() or hx_can('sops',2,license_id));
create policy hx_sop_acks_insert on hx_sop_acks for insert to authenticated with check (user_id = auth.uid() and hx_can('sops',1,license_id));

grant select, insert, update, delete on hx_sops to authenticated;
grant select on hx_sop_versions to authenticated;
grant select, insert on hx_sop_acks to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step14.sql
-- ###################################################################
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


-- ###################################################################
-- ### hendrix_step15.sql
-- ###################################################################
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


-- ###################################################################
-- ### hendrix_step16.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 16: Suppliers and vendor qualification (CSQ 2A.11)
-- Black Fox / Michigan Suppliers tab (name, category, status, products, contact,
-- COA expiry, last audit, notes, certificates) plus CSQ supplier control:
--   * supplier type, risk level, the specifications each supplier must meet
--   * credentials with numbers and expiry dates (ISO/IEC 17025 for labs, pest
--     control licenses, food-grade / GMP certificates, insurance...)
--   * approval only by Full access, stamped (who, when, on what basis)
--   * annual review (or every 6 months for high risk): every review is kept,
--     the result can keep, condition, suspend or disqualify the supplier
--   * emergency (temporary) suppliers must say how materials are verified first
--   * ethical sourcing confirmed; contract manufacturers need an audit date
--   * suppliers that were ever approved are never deleted (disqualify instead)
-- Access module 'suppliers': View = see the approved list, Edit = add suppliers,
--   credentials and files, Full = approve, review, suspend, disqualify.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-15.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_suppliers (
  id                     text primary key,
  state_id               text not null references hx_states(id),
  license_id             text not null references hx_licenses(id),
  license_ids            text[] not null default '{}',
  name                   text not null check (length(trim(name)) > 0),
  category               text not null default 'Other',
  status                 text not null default 'pending' check (status in ('pending','approved','conditional','emergency','suspended','disqualified')),
  risk                   text not null default 'medium' check (risk in ('low','medium','high')),
  products_supplied      text not null default '',
  specs                  text not null default '',
  contact_name           text not null default '',
  contact_email          text not null default '',
  contact_phone          text not null default '',
  address                text not null default '',
  credentials            jsonb not null default '[]'::jsonb,
  certificates           jsonb not null default '[]'::jsonb,
  coa_expiry             date,
  last_audit             date,
  approval_basis         text not null default '',
  approved_by            text not null default '',
  approved_at            timestamptz,
  last_review            date,
  next_review            date,
  emergency_verification text not null default '',
  ethical_sourcing       boolean not null default false,
  status_reason          text not null default '',
  notes                  text not null default '',
  ever_approved          boolean not null default false,
  created_by             text not null default '',
  created_by_id          uuid default auth.uid(),
  created_at             timestamptz not null default now(),
  updated_by             text not null default '',
  updated_at             timestamptz not null default now()
);
create unique index if not exists hx_suppliers_name on hx_suppliers(license_id, lower(trim(name)));
create index if not exists hx_suppliers_lic on hx_suppliers(license_id, status);

create table if not exists hx_supplier_reviews (
  id           text primary key,
  state_id     text not null references hx_states(id),
  license_id   text not null references hx_licenses(id),
  supplier_id  text not null references hx_suppliers(id),
  review_date  date not null default current_date,
  reviewer     text not null default '',
  rating       text not null default 'Satisfactory' check (rating in ('Satisfactory','Needs improvement','Unsatisfactory')),
  result       text not null default 'Keep approved' check (result in ('Keep approved','Approve with conditions','Suspend','Disqualify')),
  notes        text not null default '',
  files        jsonb not null default '[]'::jsonb,
  created_by   uuid default auth.uid(),
  created_at   timestamptz not null default now()
);
create index if not exists hx_supplier_reviews_sup on hx_supplier_reviews(supplier_id, review_date desc);

create or replace function hx_supplier_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_name text; v_full boolean := hx_perm('suppliers') >= 3;
begin
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  if tg_op = 'DELETE' then
    if old.ever_approved then raise exception 'A supplier that was approved stays on file. Disqualify it instead of deleting it.'; end if;
    if not v_full then raise exception 'Only someone with Full access to Suppliers can delete a supplier.'; end if;
    return old;
  end if;
  if not (new.license_id = any(new.license_ids)) then new.license_ids := array_prepend(new.license_id, new.license_ids); end if;
  if exists (select 1 from unnest(new.license_ids) l left join hx_licenses x on x.id = l where x.id is null or x.state_id <> new.state_id) then
    raise exception 'Every license of a supplier must belong to its state.';
  end if;
  new.updated_at := now(); new.updated_by := coalesce(v_name, new.updated_by);
  if tg_op = 'INSERT' then
    new.created_by := coalesce(v_name, new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    new.ever_approved := false; new.approved_by := ''; new.approved_at := null; new.last_review := null;
    if new.status not in ('pending','emergency') and not v_full then
      raise exception 'Only someone with Full access to Suppliers can approve a supplier. Add it as pending.';
    end if;
  else
    if new.created_at <> old.created_at or new.created_by_id is distinct from old.created_by_id or new.state_id <> old.state_id or new.license_id <> old.license_id then
      raise exception 'The license and creator of a supplier cannot be changed.';
    end if;
    if new.ever_approved = false and old.ever_approved then new.ever_approved := true; end if;
    if new.status is distinct from old.status and not v_full then
      raise exception 'Only someone with Full access to Suppliers can change a supplier''s approval status.';
    end if;
    if (new.approved_by is distinct from old.approved_by or new.approved_at is distinct from old.approved_at) and new.status is not distinct from old.status then
      new.approved_by := old.approved_by; new.approved_at := old.approved_at;
    end if;
  end if;
  if new.status = 'emergency' and coalesce(trim(new.emergency_verification),'') = '' then
    raise exception 'An emergency supplier needs a note on how its materials are checked before use (CSQ 2A.11 g).';
  end if;
  if new.status in ('approved','conditional') and (tg_op = 'INSERT' or old.status not in ('approved','conditional')) then
    if coalesce(trim(new.approval_basis),'') = '' then raise exception 'Record what the approval is based on (questionnaire, certificates, COA review, audit...).'; end if;
    if new.category = 'Testing Lab' and not exists (select 1 from jsonb_array_elements(new.credentials) c where c->>'kind' = 'ISO/IEC 17025 accreditation') then
      raise exception 'A testing lab needs its ISO/IEC 17025 accreditation recorded before approval (CSQ 2A.12.9 g).';
    end if;
    if new.category = 'Co-manufacturer' and new.last_audit is null then
      raise exception 'A contract manufacturer needs a second- or third-party audit date before approval (CSQ 2A.11 i).';
    end if;
    new.approved_by := coalesce(v_name,''); new.approved_at := now(); new.ever_approved := true;
    new.next_review := coalesce(new.next_review, (current_date + make_interval(months => case new.risk when 'high' then 6 else 12 end))::date);
    perform set_config('hx.reason', 'Supplier approved: ' || trim(new.approval_basis), true);
  elsif new.status in ('suspended','disqualified') and (tg_op = 'INSERT' or old.status <> new.status) then
    if coalesce(trim(new.status_reason),'') = '' then raise exception 'A reason is required to % a supplier.', case new.status when 'suspended' then 'suspend' else 'disqualify' end; end if;
    perform set_config('hx.reason', 'Supplier ' || new.status || ': ' || trim(new.status_reason), true);
  elsif coalesce(current_setting('hx.reason', true), '') = '' then
    perform set_config('hx.reason', case when tg_op = 'INSERT' then 'Supplier added' else 'Supplier updated' end, true);
  end if;
  return new;
end $$;

create or replace function hx_supplier_review_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; v_name text;
begin
  if tg_op <> 'INSERT' then raise exception 'Supplier reviews are permanent records and cannot be changed or deleted.'; end if;
  if hx_perm('suppliers') < 3 then raise exception 'Only someone with Full access to Suppliers can record a supplier review.'; end if;
  select * into s from hx_suppliers where id = new.supplier_id;
  if s.id is null or s.license_id <> new.license_id then raise exception 'Unknown supplier for this license.'; end if;
  if new.review_date > current_date then raise exception 'The review date cannot be in the future.'; end if;
  if new.result in ('Suspend','Disqualify') and coalesce(trim(new.notes),'') = '' then raise exception 'Write the reason in the review notes.'; end if;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  new.reviewer := coalesce(v_name, new.reviewer); new.created_by := auth.uid(); new.created_at := now();
  perform set_config('hx.reason', 'Supplier review: ' || new.rating || ' - ' || new.result, true);
  return new;
end $$;

create or replace function hx_supplier_review_apply() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; v_status text;
begin
  select * into s from hx_suppliers where id = new.supplier_id;
  perform set_config('hx.reason', 'Supplier review ' || new.review_date || ': ' || new.rating || ' - ' || new.result, true);
  v_status := case new.result when 'Keep approved' then (case when s.status in ('pending','emergency','suspended') then s.status else 'approved' end)
                              when 'Approve with conditions' then 'conditional' when 'Suspend' then 'suspended' else 'disqualified' end;
  update hx_suppliers set last_review = new.review_date,
         next_review = (new.review_date + make_interval(months => case s.risk when 'high' then 6 else 12 end))::date,
         status = v_status,
         status_reason = case when v_status in ('suspended','disqualified') then new.notes else status_reason end,
         approval_basis = case when v_status in ('approved','conditional') and coalesce(trim(approval_basis),'') = '' then 'Supplier review ' || new.review_date else approval_basis end
   where id = new.supplier_id;
  return null;
end $$;

drop trigger if exists hx_suppliers_guard on hx_suppliers;
create trigger hx_suppliers_guard before insert or update or delete on hx_suppliers for each row execute function hx_supplier_guard();
drop trigger if exists hx_suppliers_place on hx_suppliers;
create trigger hx_suppliers_place before insert or update on hx_suppliers for each row execute function hx_fl_guard();
drop trigger if exists hx_suppliers_audit on hx_suppliers;
create trigger hx_suppliers_audit after insert or update or delete on hx_suppliers for each row execute function hx_audit();
drop trigger if exists hx_supplier_reviews_guard on hx_supplier_reviews;
create trigger hx_supplier_reviews_guard before insert or update or delete on hx_supplier_reviews for each row execute function hx_supplier_review_guard();
drop trigger if exists hx_supplier_reviews_place on hx_supplier_reviews;
create trigger hx_supplier_reviews_place before insert on hx_supplier_reviews for each row execute function hx_fl_guard();
drop trigger if exists hx_supplier_reviews_apply on hx_supplier_reviews;
create trigger hx_supplier_reviews_apply after insert on hx_supplier_reviews for each row execute function hx_supplier_review_apply();
drop trigger if exists hx_supplier_reviews_audit on hx_supplier_reviews;
-- named so it runs before hx_supplier_reviews_apply (triggers fire in name order) and keeps the review reason
drop trigger if exists hx_supplier_reviews_a_audit on hx_supplier_reviews;
create trigger hx_supplier_reviews_a_audit after insert on hx_supplier_reviews for each row execute function hx_audit();

alter table hx_suppliers enable row level security;
alter table hx_supplier_reviews enable row level security;
drop policy if exists hx_suppliers_read on hx_suppliers;
drop policy if exists hx_suppliers_insert on hx_suppliers;
drop policy if exists hx_suppliers_update on hx_suppliers;
drop policy if exists hx_suppliers_delete on hx_suppliers;
create policy hx_suppliers_read   on hx_suppliers for select to authenticated using (exists (select 1 from unnest(license_ids) l where hx_can('suppliers',1,l)));
create policy hx_suppliers_insert on hx_suppliers for insert to authenticated with check (hx_can('suppliers',2,license_id));
create policy hx_suppliers_update on hx_suppliers for update to authenticated using (hx_can('suppliers',2,license_id)) with check (hx_can('suppliers',2,license_id));
create policy hx_suppliers_delete on hx_suppliers for delete to authenticated using (hx_can('suppliers',3,license_id));
drop policy if exists hx_supplier_reviews_read on hx_supplier_reviews;
drop policy if exists hx_supplier_reviews_insert on hx_supplier_reviews;
create policy hx_supplier_reviews_read   on hx_supplier_reviews for select to authenticated using (hx_can('suppliers',1,license_id));
create policy hx_supplier_reviews_insert on hx_supplier_reviews for insert to authenticated with check (hx_can('suppliers',3,license_id));
grant select, insert, update, delete on hx_suppliers to authenticated;
grant select, insert on hx_supplier_reviews to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step17.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 17: Receiving, Hold and Release, Shipping
-- (CSQ 2A.9.4, 2A.10.1, 2A.10.2, 2A.10.3, 2A.10.4, 2A.12.4, 3C.1)
--   * Receiving: every incoming lot gets a number (RCV-YYYY-###), comes only
--     from a supplier approved for that license, is inspected on arrival
--     (packaging, damage, pests, seals, labels, matches documents), keeps its
--     COA / certificate of conformance and documents, and waits in QUARANTINE
--     until someone with Full access accepts or rejects it. Rejected lots are
--     put on hold automatically (held apart until returned or destroyed).
--   * Inventory: what is used from each lot in which batch (one step back
--     traceability), quantity left, expiry; expired or held lots cannot be used.
--   * Hold and release: anyone with Edit can put a lot, batch, product tag or
--     customer return on hold (HOLD-YYYY-###); only Full can decide (release,
--     destroy, return to supplier, rework) and must write why. Held lots and
--     batches cannot be used or shipped. Holds are never deleted.
--   * Shipping: shipments (SHP-YYYY-###) list batches and package tags per
--     customer (one step forward traceability), the state manifest, the
--     transporter, and a pre-load inspection that must pass. Batches on hold
--     or with a failed test and no passing retest cannot be shipped.
-- Access modules 'receiving', 'holds', 'shipping': View / Edit / Full.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-16.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_lots (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  number          text not null default '',
  received_on     date not null default current_date,
  supplier_id     text not null references hx_suppliers(id),
  supplier_name   text not null default '',
  supplier_status text not null default '',
  item            text not null check (length(trim(item)) > 0),
  category        text not null default 'Other',
  supplier_lot    text not null default '',
  metrc_tag       text not null default '',
  quantity        numeric not null check (quantity > 0),
  unit            text not null default 'each',
  qty_used        numeric not null default 0,
  expiry_date     date,
  location        text not null default '',
  po_number       text not null default '',
  coa_ok          boolean not null default false,
  checks          jsonb not null default '{}'::jsonb,
  checks_ok       boolean not null default false,
  inspection_notes text not null default '',
  files           jsonb not null default '[]'::jsonb,
  status          text not null default 'quarantine' check (status in ('quarantine','accepted','rejected','on_hold','returned','destroyed')),
  decision_notes  text not null default '',
  decided_by      text not null default '',
  decided_at      timestamptz,
  received_by     text not null default '',
  received_by_id  uuid default auth.uid(),
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_lots_number on hx_lots(license_id, number);
create index if not exists hx_lots_lic on hx_lots(license_id, status, received_on desc);
create index if not exists hx_lots_sup on hx_lots(supplier_id);

create table if not exists hx_lot_uses (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  lot_id        text not null references hx_lots(id),
  batch_id      text references hx_batches(id),
  batch_number  text not null default '',
  used_on       date not null default current_date,
  quantity      numeric not null check (quantity > 0),
  notes         text not null default '',
  used_by       text not null default '',
  used_by_id    uuid default auth.uid(),
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_by     uuid,
  voided_at     timestamptz
);
create index if not exists hx_lot_uses_lot on hx_lot_uses(lot_id);
create index if not exists hx_lot_uses_batch on hx_lot_uses(batch_id);

create table if not exists hx_holds (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  number         text not null default '',
  kind           text not null default 'lot' check (kind in ('lot','batch','product','return','other')),
  lot_id         text references hx_lots(id),
  batch_id       text references hx_batches(id),
  tag            text not null default '',
  item           text not null default '',
  quantity       text not null default '',
  source         text not null default 'Other',
  reason         text not null check (length(trim(reason)) > 0),
  deviation_id   text,
  shipment_id    text,
  location       text not null default '',
  prev_status    text not null default '',
  status         text not null default 'open' check (status in ('open','released','destroyed','returned','reworked')),
  decision_notes text not null default '',
  decided_by     text not null default '',
  decided_at     timestamptz,
  placed_by      text not null default '',
  placed_by_id   uuid default auth.uid(),
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create unique index if not exists hx_holds_number on hx_holds(license_id, number);
create index if not exists hx_holds_lic on hx_holds(license_id, status, created_at desc);

create table if not exists hx_shipments (
  id                text primary key,
  state_id          text not null references hx_states(id),
  license_id        text not null references hx_licenses(id),
  number            text not null default '',
  ship_date         date not null default current_date,
  customer          text not null check (length(trim(customer)) > 0),
  customer_license  text not null default '',
  destination       text not null default '',
  manifest_number   text not null default '',
  transporter       text not null default '',
  driver            text not null default '',
  vehicle           text not null default '',
  items             jsonb not null default '[]'::jsonb,
  checks            jsonb not null default '{}'::jsonb,
  checks_ok         boolean not null default false,
  notes             text not null default '',
  files             jsonb not null default '[]'::jsonb,
  status            text not null default 'shipped' check (status in ('shipped','delivered','cancelled')),
  delivered_on      date,
  cancel_reason     text not null default '',
  shipped_by        text not null default '',
  shipped_by_id     uuid default auth.uid(),
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create unique index if not exists hx_shipments_number on hx_shipments(license_id, number);
create index if not exists hx_shipments_lic on hx_shipments(license_id, ship_date desc);

-- generic per-license numbering (same as QMS)
create or replace function hx_next_number(p_table text, p_lic text, p_prefix text) returns text
language plpgsql security definer set search_path = public as $$
declare v_year text := to_char(now(), 'YYYY'); v_max int;
begin
  perform pg_advisory_xact_lock(hashtext(p_table || p_lic));
  execute format('select coalesce(max((regexp_match(number, %L))[1]::int), 0) from %I where license_id = $1',
                 '^' || p_prefix || '-' || v_year || '-(\d+)$', p_table) into v_max using p_lic;
  return p_prefix || '-' || v_year || '-' || lpad((v_max + 1)::text, 3, '0');
end $$;

create or replace function hx_me() returns text language sql stable security definer set search_path = public as $$
  select coalesce(nullif(name,''), email) from hx_profiles where id::text = auth.uid()::text;
$$;

-- ---------- receiving ----------
create or replace function hx_lot_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; v_full boolean := hx_perm('receiving') >= 3; a jsonb; n jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Received lots are never deleted. Reject the lot or put it on hold.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    select * into s from hx_suppliers where id = new.supplier_id;
    if s.id is null or not (new.license_id = any(s.license_ids)) then raise exception 'That supplier is not on file for this license.'; end if;
    if s.status not in ('approved','conditional','emergency') then
      raise exception '% is % - receive only from approved suppliers (CSQ 2A.11).', s.name, case s.status when 'pending' then 'not approved yet' else s.status end;
    end if;
    if new.received_on > current_date then raise exception 'The receiving date cannot be in the future.'; end if;
    new.number := hx_next_number('hx_lots', new.license_id, 'RCV');
    new.supplier_name := s.name; new.supplier_status := s.status;
    new.received_by := coalesce(hx_me(), new.received_by); new.received_by_id := auth.uid(); new.created_at := now();
    new.qty_used := 0; new.decided_by := ''; new.decided_at := null; new.decision_notes := '';
    new.checks_ok := not exists (select 1 from jsonb_each(new.checks) c where c.value <> 'true'::jsonb) and new.checks <> '{}'::jsonb;
    if new.status not in ('quarantine') then raise exception 'A received lot starts in quarantine until it is accepted.'; end if;
    perform set_config('hx.reason', 'Lot received from ' || s.name, true);
    return new;
  end if;
  if new.number <> old.number or new.supplier_id <> old.supplier_id or new.received_by_id is distinct from old.received_by_id or new.created_at <> old.created_at
     or new.state_id <> old.state_id or new.license_id <> old.license_id or new.supplier_name <> old.supplier_name or new.supplier_status <> old.supplier_status then
    raise exception 'The number, supplier, receiver and license of a lot cannot be changed.';
  end if;
  if current_setting('hx.internal', true) = 'on' then return new; end if;  -- quantity / hold updates from other triggers
  if new.qty_used <> old.qty_used then raise exception 'Use from a lot is recorded under Inventory, not by editing the lot.'; end if;
  new.checks_ok := not exists (select 1 from jsonb_each(new.checks) c where c.value <> 'true'::jsonb) and new.checks <> '{}'::jsonb;
  if new.status is distinct from old.status then
    if old.status = 'on_hold' or new.status in ('on_hold','returned','destroyed') then raise exception 'This lot is controlled by its hold. Decide the hold under Hold and Release.'; end if;
    if not v_full then raise exception 'Only someone with Full access to Receiving can accept or reject a lot.'; end if;
    if old.status <> 'quarantine' then raise exception 'Only a lot in quarantine can be accepted or rejected.'; end if;
    if coalesce(trim(new.decision_notes),'') = '' and new.status = 'rejected' then raise exception 'Write why the lot is rejected.'; end if;
    if new.status = 'accepted' then
      if not new.coa_ok then raise exception 'The lot needs its COA or certificate of conformance before it can be accepted (CSQ 2A.10.2).'; end if;
      if not new.checks_ok and coalesce(trim(new.decision_notes),'') = '' then raise exception 'The receiving inspection did not pass every check. Write why the lot is still accepted, or reject it.'; end if;
      if new.supplier_status = 'emergency' and coalesce(trim(new.decision_notes),'') = '' then raise exception 'This lot is from an emergency supplier. Write how it was verified before use (CSQ 2A.11 g).'; end if;
      if new.expiry_date is not null and new.expiry_date < current_date then raise exception 'This lot is past its expiry date and cannot be accepted.'; end if;
    end if;
    new.decided_by := coalesce(hx_me(),''); new.decided_at := now();
    perform set_config('hx.reason', 'Lot ' || new.status || coalesce(': ' || nullif(trim(new.decision_notes),''), ''), true);
    return new;
  end if;
  if old.status not in ('quarantine') then
    a := to_jsonb(old); n := to_jsonb(new);
    if (n - 'files' - 'location' - 'updated_at' - 'inspection_notes') is distinct from (a - 'files' - 'location' - 'updated_at' - 'inspection_notes') then
      raise exception 'After the decision only the storage location, files and notes of a lot can change.';
    end if;
  end if;
  if hx_perm('receiving') < 2 then raise exception 'You need Edit access to Receiving.'; end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Lot updated', true); end if;
  return new;
end $$;

-- after a rejection the lot is held apart automatically
create or replace function hx_lot_after() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.status = 'rejected' and old.status = 'quarantine' then
    perform set_config('hx.internal', 'on', true);
    insert into hx_holds(id, state_id, license_id, kind, lot_id, item, quantity, source, reason, location, prev_status)
    values ('hold-' || replace(gen_random_uuid()::text,'-',''), new.state_id, new.license_id, 'lot', new.id, new.item || ' (' || new.number || ')',
            new.quantity || ' ' || new.unit, 'Receiving inspection', 'Rejected at receiving: ' || new.decision_notes, new.location, 'rejected');
    perform set_config('hx.internal', 'off', true);
  end if;
  return null;
end $$;

create or replace function hx_lot_use_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare l record; b record; v_left numeric;
begin
  if tg_op = 'DELETE' then raise exception 'Use records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'INSERT' then
    select * into l from hx_lots where id = new.lot_id for update;
    if l.id is null or l.license_id <> new.license_id then raise exception 'Unknown lot for this license.'; end if;
    if l.status <> 'accepted' then raise exception 'Lot % is % and cannot be used.', l.number, case l.status when 'quarantine' then 'still in quarantine (not accepted yet)' when 'on_hold' then 'on hold' else l.status end; end if;
    if l.expiry_date is not null and l.expiry_date < new.used_on then raise exception 'Lot % expired on % and cannot be used.', l.number, l.expiry_date; end if;
    if new.used_on > current_date then raise exception 'The date cannot be in the future.'; end if;
    v_left := l.quantity - l.qty_used;
    if new.quantity > v_left then raise exception 'Only % % left in lot %.', v_left, l.unit, l.number; end if;
    if new.batch_id is not null then
      select * into b from hx_batches where id = new.batch_id;
      if b.id is null or b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
      if b.voided then raise exception 'That batch is void.'; end if;
      new.batch_number := b.batch_number;
    end if;
    new.used_by := coalesce(hx_me(), new.used_by); new.used_by_id := auth.uid(); new.created_at := now();
    new.voided := false; new.void_reason := null; new.voided_by := null; new.voided_at := null;
    perform set_config('hx.reason', 'Used ' || new.quantity || ' ' || l.unit || ' of ' || l.number || coalesce(' in batch ' || nullif(new.batch_number,''), ''), true);
    perform set_config('hx.internal', 'on', true);
    update hx_lots set qty_used = qty_used + new.quantity where id = new.lot_id;
    perform set_config('hx.internal', 'off', true);
    -- the lot's audit row consumed the reason; set it again for this record
    perform set_config('hx.reason', 'Used ' || new.quantity || ' ' || l.unit || ' of ' || l.number || coalesce(' in batch ' || nullif(new.batch_number,''), ''), true);
    return new;
  end if;
  if old.voided then raise exception 'This use record is void.'; end if;
  if not new.voided or (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_by' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_by' - 'voided_at') then
    raise exception 'A use record cannot be changed. Void it with a reason and record it again.';
  end if;
  if hx_perm('receiving') < 3 then raise exception 'Only someone with Full access to Receiving can void a use record.'; end if;
  if coalesce(trim(new.void_reason),'') = '' then raise exception 'A reason is required to void a use record.'; end if;
  new.voided_by := auth.uid(); new.voided_at := now();
  perform set_config('hx.reason', 'Use voided: ' || trim(new.void_reason), true);
  perform set_config('hx.internal', 'on', true);
  update hx_lots set qty_used = greatest(qty_used - old.quantity, 0) where id = old.lot_id;
  perform set_config('hx.internal', 'off', true);
  perform set_config('hx.reason', 'Use voided: ' || trim(new.void_reason), true);
  return new;
end $$;

-- ---------- hold and release ----------
create or replace function hx_hold_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare l record; b record; v_int boolean := current_setting('hx.internal', true) = 'on';
begin
  if tg_op = 'DELETE' then raise exception 'Holds are never deleted. Decide the hold (release, destroy, return, rework) with a reason.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    if not v_int and hx_perm('holds') < 2 then raise exception 'You need Edit access to Hold and Release to place something on hold.'; end if;
    new.number := hx_next_number('hx_holds', new.license_id, 'HOLD');
    new.placed_by := coalesce(hx_me(), new.placed_by); new.placed_by_id := auth.uid(); new.created_at := now();
    new.status := 'open'; new.decided_by := ''; new.decided_at := null; new.decision_notes := '';
    perform set_config('hx.reason', 'Placed on hold: ' || trim(new.reason), true);
    if new.kind = 'lot' then
      select * into l from hx_lots where id = new.lot_id;
      if l.id is null or l.license_id <> new.license_id then raise exception 'Pick the lot to put on hold.'; end if;
      if l.status in ('returned','destroyed') then raise exception 'Lot % is already %.', l.number, l.status; end if;
      if l.status = 'on_hold' then raise exception 'Lot % is already on hold.', l.number; end if;
      if not v_int then new.prev_status := l.status; end if;
      new.item := coalesce(nullif(new.item,''), l.item || ' (' || l.number || ')');
      perform set_config('hx.internal', 'on', true);
      update hx_lots set status = 'on_hold' where id = l.id;
      perform set_config('hx.internal', case when v_int then 'on' else 'off' end, true);
      perform set_config('hx.reason', 'Placed on hold: ' || trim(new.reason), true);
    elsif new.kind in ('batch','return') or new.batch_id is not null then
      select * into b from hx_batches where id = new.batch_id;
      if new.kind = 'batch' and b.id is null then raise exception 'Pick the batch to put on hold.'; end if;
      if b.id is not null and b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
      if b.id is not null then new.item := coalesce(nullif(new.item,''), coalesce(nullif(b.sku,''), b.batch_type) || ' batch ' || b.batch_number); end if;
    end if;
    if new.kind = 'product' and coalesce(trim(new.tag),'') = '' then raise exception 'Enter the package tag to put on hold.'; end if;
    if coalesce(trim(new.item),'') = '' then new.item := coalesce(nullif(trim(new.tag),''), 'Held item'); end if;
    return new;
  end if;
  if new.number <> old.number or new.kind <> old.kind or new.lot_id is distinct from old.lot_id or new.batch_id is distinct from old.batch_id or new.tag <> old.tag
     or new.created_at <> old.created_at or new.placed_by_id is distinct from old.placed_by_id or new.license_id <> old.license_id or new.reason <> old.reason then
    raise exception 'What is held and why cannot be changed. Decide this hold and open a new one.';
  end if;
  if old.status <> 'open' then raise exception 'This hold was already decided (%) and cannot be changed.', old.status; end if;
  if new.status = 'open' then
    if hx_perm('holds') < 2 then raise exception 'You need Edit access to Hold and Release.'; end if;
    if (to_jsonb(new) - 'location' - 'updated_at' - 'deviation_id') is distinct from (to_jsonb(old) - 'location' - 'updated_at' - 'deviation_id') then raise exception 'Only the location and the linked deviation of an open hold can change.'; end if;
    perform set_config('hx.reason', 'Hold updated', true);
    return new;
  end if;
  if hx_perm('holds') < 3 then raise exception 'Only someone with Full access to Hold and Release can decide a hold (CSQ 2A.10.4).'; end if;
  if coalesce(trim(new.decision_notes),'') = '' then raise exception 'Write the reason for the decision.'; end if;
  if new.status = 'released' and new.kind = 'lot' and old.prev_status = 'rejected' then raise exception 'This lot was rejected at receiving. Return it to the supplier or destroy it.'; end if;
  if new.status = 'released' and new.batch_id is not null and exists (select 1 from hx_tests t where t.batch_id = new.batch_id and not t.voided and t.status = 'Failed')
     and not exists (select 1 from hx_tests t where t.batch_id = new.batch_id and not t.voided and t.status = 'Passed' and t.created_at > (select max(created_at) from hx_tests f where f.batch_id = new.batch_id and not f.voided and f.status = 'Failed')) then
    raise exception 'This batch has a failed test and no passing retest after it. It cannot be released.';
  end if;
  new.decided_by := coalesce(hx_me(),''); new.decided_at := now();
  perform set_config('hx.reason', 'Hold ' || new.status || ': ' || trim(new.decision_notes), true);
  if new.kind = 'lot' then
    perform set_config('hx.internal', 'on', true);
    update hx_lots set status = case new.status when 'released' then coalesce(nullif(old.prev_status,''),'quarantine') when 'destroyed' then 'destroyed' when 'returned' then 'returned' else 'quarantine' end
     where id = new.lot_id;
    perform set_config('hx.internal', 'off', true);
    perform set_config('hx.reason', 'Hold ' || new.status || ': ' || trim(new.decision_notes), true);
  end if;
  return new;
end $$;

-- ---------- shipping ----------
create or replace function hx_shipment_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare it jsonb; b record; v_tag text;
begin
  if tg_op = 'DELETE' then raise exception 'Shipments are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    if hx_perm('shipping') < 2 then raise exception 'You need Edit access to Shipping.'; end if;
    if new.ship_date > current_date then raise exception 'The ship date cannot be in the future.'; end if;
    if jsonb_typeof(new.items) <> 'array' or jsonb_array_length(new.items) = 0 then raise exception 'Add at least one batch or package to the shipment.'; end if;
    new.checks_ok := not exists (select 1 from jsonb_each(new.checks) c where c.value <> 'true'::jsonb) and new.checks <> '{}'::jsonb;
    if not new.checks_ok then raise exception 'Every pre-load inspection check must pass before loading (CSQ 2A.9.4). Fix the problem first.'; end if;
    for it in select * from jsonb_array_elements(new.items) loop
      v_tag := coalesce(it->>'tag','');
      if coalesce(it->>'batch_id','') = '' then raise exception 'Every shipped item needs its batch (for traceability).'; end if;
      select * into b from hx_batches where id = it->>'batch_id';
      if b.id is null or b.license_id <> new.license_id then raise exception 'A batch in this shipment belongs to a different license.'; end if;
      if b.voided then raise exception 'Batch % is void.', b.batch_number; end if;
      if exists (select 1 from hx_holds h where h.status = 'open' and h.license_id = new.license_id and (h.batch_id = b.id or (v_tag <> '' and upper(regexp_replace(h.tag,'[^A-Za-z0-9]','','g')) = upper(regexp_replace(v_tag,'[^A-Za-z0-9]','','g'))))) then
        raise exception 'Batch % is on hold and cannot be shipped (CSQ 2A.10.4).', b.batch_number || case when v_tag <> '' then ' / tag ' || v_tag else '' end;
      end if;
      if exists (select 1 from hx_tests t where t.batch_id = b.id and not t.voided and t.status = 'Failed')
         and not exists (select 1 from hx_tests t where t.batch_id = b.id and not t.voided and t.status = 'Passed' and t.created_at > (select max(created_at) from hx_tests f where f.batch_id = b.id and not f.voided and f.status = 'Failed')) then
        raise exception 'Batch % has a failed test and no passing retest. It cannot be shipped.', b.batch_number;
      end if;
    end loop;
    new.number := hx_next_number('hx_shipments', new.license_id, 'SHP');
    new.shipped_by := coalesce(hx_me(), new.shipped_by); new.shipped_by_id := auth.uid(); new.created_at := now();
    new.status := 'shipped'; new.delivered_on := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Shipped to ' || new.customer, true);
    return new;
  end if;
  if (to_jsonb(new) - 'status' - 'delivered_on' - 'cancel_reason' - 'notes' - 'files' - 'updated_at' - 'manifest_number')
     is distinct from (to_jsonb(old) - 'status' - 'delivered_on' - 'cancel_reason' - 'notes' - 'files' - 'updated_at' - 'manifest_number') then
    raise exception 'What was shipped, to whom and when cannot be changed. Cancel the shipment with a reason and record it again.';
  end if;
  if old.status = 'cancelled' then raise exception 'This shipment is cancelled.'; end if;
  if hx_perm('shipping') < 2 then raise exception 'You need Edit access to Shipping.'; end if;
  if new.status = 'cancelled' and old.status <> 'cancelled' then
    if hx_perm('shipping') < 3 then raise exception 'Only someone with Full access to Shipping can cancel a shipment.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel a shipment.'; end if;
    perform set_config('hx.reason', 'Shipment cancelled: ' || trim(new.cancel_reason), true);
  elsif new.status = 'delivered' and old.status <> 'delivered' then
    new.delivered_on := coalesce(new.delivered_on, current_date);
    perform set_config('hx.reason', 'Delivered ' || new.delivered_on, true);
  elsif new.status = 'shipped' and old.status = 'delivered' then
    raise exception 'A delivered shipment cannot go back to shipped.';
  else
    perform set_config('hx.reason', 'Shipment updated', true);
  end if;
  return new;
end $$;

drop trigger if exists hx_lots_guard on hx_lots;
create trigger hx_lots_guard before insert or update or delete on hx_lots for each row execute function hx_lot_guard();
drop trigger if exists hx_lots_place on hx_lots;
create trigger hx_lots_place before insert or update on hx_lots for each row execute function hx_fl_guard();
drop trigger if exists hx_lots_a_audit on hx_lots;
create trigger hx_lots_a_audit after insert or update or delete on hx_lots for each row execute function hx_audit();
drop trigger if exists hx_lots_b_after on hx_lots;
create trigger hx_lots_b_after after update on hx_lots for each row execute function hx_lot_after();

drop trigger if exists hx_lot_uses_guard on hx_lot_uses;
create trigger hx_lot_uses_guard before insert or update or delete on hx_lot_uses for each row execute function hx_lot_use_guard();
drop trigger if exists hx_lot_uses_place on hx_lot_uses;
create trigger hx_lot_uses_place before insert or update on hx_lot_uses for each row execute function hx_fl_guard();
drop trigger if exists hx_lot_uses_audit on hx_lot_uses;
create trigger hx_lot_uses_audit after insert or update on hx_lot_uses for each row execute function hx_audit();

drop trigger if exists hx_holds_guard on hx_holds;
create trigger hx_holds_guard before insert or update or delete on hx_holds for each row execute function hx_hold_guard();
drop trigger if exists hx_holds_place on hx_holds;
create trigger hx_holds_place before insert or update on hx_holds for each row execute function hx_fl_guard();
drop trigger if exists hx_holds_audit on hx_holds;
create trigger hx_holds_audit after insert or update on hx_holds for each row execute function hx_audit();

drop trigger if exists hx_shipments_guard on hx_shipments;
create trigger hx_shipments_guard before insert or update or delete on hx_shipments for each row execute function hx_shipment_guard();
drop trigger if exists hx_shipments_place on hx_shipments;
create trigger hx_shipments_place before insert or update on hx_shipments for each row execute function hx_fl_guard();
drop trigger if exists hx_shipments_audit on hx_shipments;
create trigger hx_shipments_audit after insert or update on hx_shipments for each row execute function hx_audit();

alter table hx_lots enable row level security;
alter table hx_lot_uses enable row level security;
alter table hx_holds enable row level security;
alter table hx_shipments enable row level security;
drop policy if exists hx_lots_read on hx_lots;
drop policy if exists hx_lots_insert on hx_lots;
drop policy if exists hx_lots_update on hx_lots;
create policy hx_lots_read   on hx_lots for select to authenticated using (hx_can('receiving',1,license_id) or hx_can('holds',1,license_id));
create policy hx_lots_insert on hx_lots for insert to authenticated with check (hx_can('receiving',2,license_id));
create policy hx_lots_update on hx_lots for update to authenticated using (hx_can('receiving',2,license_id)) with check (hx_can('receiving',2,license_id));
drop policy if exists hx_lot_uses_read on hx_lot_uses;
drop policy if exists hx_lot_uses_insert on hx_lot_uses;
drop policy if exists hx_lot_uses_update on hx_lot_uses;
create policy hx_lot_uses_read   on hx_lot_uses for select to authenticated using (hx_can('receiving',1,license_id) or hx_can('batch',1,license_id));
create policy hx_lot_uses_insert on hx_lot_uses for insert to authenticated with check (hx_can('receiving',2,license_id) or hx_can('batch',2,license_id));
create policy hx_lot_uses_update on hx_lot_uses for update to authenticated using (hx_can('receiving',3,license_id)) with check (hx_can('receiving',3,license_id));
drop policy if exists hx_holds_read on hx_holds;
drop policy if exists hx_holds_insert on hx_holds;
drop policy if exists hx_holds_update on hx_holds;
create policy hx_holds_read   on hx_holds for select to authenticated using (hx_can('holds',1,license_id) or hx_can('receiving',1,license_id) or hx_can('shipping',1,license_id));
create policy hx_holds_insert on hx_holds for insert to authenticated with check (hx_can('holds',2,license_id) or hx_can('receiving',3,license_id));
create policy hx_holds_update on hx_holds for update to authenticated using (hx_can('holds',2,license_id)) with check (hx_can('holds',2,license_id));
drop policy if exists hx_shipments_read on hx_shipments;
drop policy if exists hx_shipments_insert on hx_shipments;
drop policy if exists hx_shipments_update on hx_shipments;
create policy hx_shipments_read   on hx_shipments for select to authenticated using (hx_can('shipping',1,license_id));
create policy hx_shipments_insert on hx_shipments for insert to authenticated with check (hx_can('shipping',2,license_id));
create policy hx_shipments_update on hx_shipments for update to authenticated using (hx_can('shipping',2,license_id)) with check (hx_can('shipping',2,license_id));
grant select, insert, update on hx_lots, hx_lot_uses, hx_holds, hx_shipments to authenticated;
grant execute on function hx_me() to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step18.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 18: Traceability and Recall (CSQ 1.8, 1.11, 2A.10.1)
--   * Trace any received lot, batch or package tag one step back (supplier,
--     supplier lot, COA) and one step forward (batches that used it, shipments,
--     customers), with quantities made, shipped, on hand and on hold.
--   * Recall team and contact list per license: team with roles, emergency
--     services, customers, suppliers, regulators, certification body, lab;
--     each contact has a "verified on" date (kept up to date yearly).
--   * Mock recalls, recalls and withdrawals (MOCK-YYYY-### / RCL-YYYY-###):
--     the clock starts on the server when the exercise starts and stops when it
--     is closed, so the duration cannot be edited. A mock recall passes only
--     when every step is done within 2 hours. Real recalls and withdrawals
--     are started and closed by Full access. Never deleted (cancel with reason).
-- Access module 'recall': View / Edit (contacts, run mock recalls) / Full
--   (start and close real recalls and withdrawals, cancel).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-17.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_recall_contacts (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  kind          text not null default 'team' check (kind in ('team','emergency','regulator','certification','customer','supplier','lab','other')),
  name          text not null check (length(trim(name)) > 0),
  role          text not null default '',
  organization  text not null default '',
  phone         text not null default '',
  after_hours   text not null default '',
  email         text not null default '',
  notes         text not null default '',
  is_backup     boolean not null default false,
  verified_on   date,
  active        boolean not null default true,
  sort          int not null default 0,
  updated_by    text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index if not exists hx_recall_contacts_lic on hx_recall_contacts(license_id, kind);

create table if not exists hx_recalls (
  id                 text primary key,
  state_id           text not null references hx_states(id),
  license_id         text not null references hx_licenses(id),
  number             text not null default '',
  kind               text not null default 'mock' check (kind in ('mock','recall','withdrawal')),
  recall_class       text not null default '',
  target_type        text not null default 'batch' check (target_type in ('lot','batch','tag')),
  target_id          text not null default '',
  target_label       text not null default '',
  reason             text not null default '',
  started_at         timestamptz not null default now(),
  ended_at           timestamptz,
  duration_minutes   int,
  steps              jsonb not null default '{}'::jsonb,
  step_times         jsonb not null default '{}'::jsonb,
  notified           jsonb not null default '[]'::jsonb,
  trace              jsonb not null default '{}'::jsonb,
  qty_made           text not null default '',
  qty_shipped        text not null default '',
  qty_on_hand        text not null default '',
  qty_recovered      text not null default '',
  findings           text not null default '',
  actions            text not null default '',
  files              jsonb not null default '[]'::jsonb,
  status             text not null default 'open' check (status in ('open','closed','cancelled')),
  result             text not null default '',
  cancel_reason      text not null default '',
  started_by         text not null default '',
  started_by_id      uuid default auth.uid(),
  closed_by          text not null default '',
  updated_at         timestamptz not null default now()
);
create unique index if not exists hx_recalls_number on hx_recalls(license_id, number);
create index if not exists hx_recalls_lic on hx_recalls(license_id, started_at desc);

create or replace function hx_recall_contact_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if hx_perm('recall') < 3 then raise exception 'Only someone with Full access to Recall can delete a contact. Switch it off instead.'; end if;
    return old;
  end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  if tg_op = 'INSERT' then new.created_at := now(); end if;
  if new.verified_on is not null and new.verified_on > current_date then raise exception 'The verified date cannot be in the future.'; end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then
    perform set_config('hx.reason', case when tg_op = 'INSERT' then 'Recall contact added' when new.verified_on is distinct from old.verified_on then 'Contact verified' else 'Recall contact updated' end, true);
  end if;
  return new;
end $$;

create or replace function hx_recall_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_full boolean := hx_perm('recall') >= 3; v_edit boolean := hx_perm('recall') >= 2; v_all boolean; k text;
begin
  if tg_op = 'DELETE' then raise exception 'Recall records are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now();
  if tg_op = 'INSERT' then
    if new.kind = 'mock' and not v_edit then raise exception 'You need Edit access to Recall to start a mock recall.'; end if;
    if new.kind <> 'mock' and not v_full then raise exception 'Only someone with Full access to Recall can start a recall or withdrawal.'; end if;
    if coalesce(trim(new.target_label),'') = '' then raise exception 'Pick the lot, batch or package tag to trace.'; end if;
    if new.kind <> 'mock' and coalesce(trim(new.reason),'') = '' then raise exception 'Write the reason for the recall.'; end if;
    new.number := hx_next_number('hx_recalls', new.license_id, case when new.kind = 'mock' then 'MOCK' else 'RCL' end);
    new.started_at := now(); new.ended_at := null; new.duration_minutes := null; new.status := 'open'; new.result := ''; new.cancel_reason := ''; new.closed_by := '';
    new.started_by := coalesce(hx_me(), new.started_by); new.started_by_id := auth.uid();
    perform set_config('hx.reason', case new.kind when 'mock' then 'Mock recall started: ' else initcap(new.kind) || ' started: ' end || new.target_label, true);
    return new;
  end if;
  if new.number <> old.number or new.kind <> old.kind or new.started_at <> old.started_at or new.started_by_id is distinct from old.started_by_id
     or new.target_type <> old.target_type or new.target_id <> old.target_id or new.license_id <> old.license_id then
    raise exception 'The number, type, start time and traced product of a recall cannot be changed.';
  end if;
  if old.status <> 'open' then raise exception 'This % is % and cannot be changed.', case old.kind when 'mock' then 'mock recall' else old.kind end, old.status; end if;
  if not v_edit then raise exception 'You need Edit access to Recall.'; end if;
  -- stamp the time each step is first ticked
  for k in select key from jsonb_each(new.steps) where value = 'true'::jsonb loop
    if not (old.steps ? k and old.steps->k = 'true'::jsonb) then new.step_times := new.step_times || jsonb_build_object(k, to_char(now() at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')); end if;
  end loop;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access to Recall can cancel.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    new.ended_at := now(); new.closed_by := coalesce(hx_me(),'');
    perform set_config('hx.reason', 'Cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status = 'closed' then
    if old.kind <> 'mock' and not v_full then raise exception 'Only someone with Full access to Recall can close a recall or withdrawal.'; end if;
    if coalesce(trim(new.findings),'') = '' then raise exception 'Write the findings before closing.'; end if;
    new.ended_at := now(); new.closed_by := coalesce(hx_me(),'');
    new.duration_minutes := ceil(extract(epoch from (new.ended_at - new.started_at)) / 60.0)::int;
    v_all := not exists (select 1 from jsonb_each(new.steps) s where s.value <> 'true'::jsonb) and new.steps <> '{}'::jsonb;
    if old.kind = 'mock' then
      new.result := case when v_all and new.duration_minutes <= 120 then 'Pass' else 'Fail' end;
    else
      if not v_all then raise exception 'Complete every recall step before closing.'; end if;
      new.result := 'Completed';
    end if;
    perform set_config('hx.reason', 'Closed in ' || new.duration_minutes || ' min' || case when new.result <> '' then ' - ' || new.result else '' end, true);
    return new;
  end if;
  new.ended_at := null; new.duration_minutes := null; new.result := '';
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Recall progress updated', true); end if;
  return new;
end $$;

-- everything needed to trace, for people with Recall access (they may not have Receiving or Shipping access)
create or replace function hx_trace_data(p_lic text) returns jsonb
language sql stable security definer set search_path = public as $$
  select case when not hx_can('recall',1,p_lic) then null else jsonb_build_object(
    'lots', coalesce((select jsonb_agg(jsonb_build_object('id',id,'number',number,'received_on',received_on,'supplier_id',supplier_id,'supplier_name',supplier_name,'item',item,'category',category,
              'supplier_lot',supplier_lot,'metrc_tag',metrc_tag,'quantity',quantity,'unit',unit,'qty_used',qty_used,'status',status,'coa_ok',coa_ok,'expiry_date',expiry_date,'location',location)) from hx_lots where license_id = p_lic), '[]'::jsonb),
    'uses', coalesce((select jsonb_agg(jsonb_build_object('id',id,'lot_id',lot_id,'batch_id',batch_id,'batch_number',batch_number,'quantity',quantity,'used_on',used_on)) from hx_lot_uses where license_id = p_lic and not voided), '[]'::jsonb),
    'batches', coalesce((select jsonb_agg(jsonb_build_object('id',id,'batch_number',batch_number,'batch_type',batch_type,'sku',sku,'flavor',flavor,'created_at',created_at,'status',status)) from hx_batches where license_id = p_lic and not voided), '[]'::jsonb),
    'tests', coalesce((select jsonb_agg(jsonb_build_object('id',id,'batch_id',batch_id,'tag',tag,'sample_tag',sample_tag,'status',status,'lab_name',lab_name,'created_at',created_at)) from hx_tests where license_id = p_lic and not voided), '[]'::jsonb),
    'ships', coalesce((select jsonb_agg(jsonb_build_object('id',id,'number',number,'ship_date',ship_date,'customer',customer,'customer_license',customer_license,'destination',destination,'manifest_number',manifest_number,'items',items,'status',status,'delivered_on',delivered_on)) from hx_shipments where license_id = p_lic and status <> 'cancelled'), '[]'::jsonb),
    'holds', coalesce((select jsonb_agg(jsonb_build_object('id',id,'number',number,'kind',kind,'lot_id',lot_id,'batch_id',batch_id,'tag',tag,'status',status,'quantity',quantity,'source',source,'reason',reason)) from hx_holds where license_id = p_lic), '[]'::jsonb),
    'suppliers', coalesce((select jsonb_agg(jsonb_build_object('id',id,'name',name,'status',status,'contact_name',contact_name,'contact_email',contact_email,'contact_phone',contact_phone)) from hx_suppliers where p_lic = any(license_ids)), '[]'::jsonb))
  end;
$$;
grant execute on function hx_trace_data(text) to authenticated;

drop trigger if exists hx_recall_contacts_guard on hx_recall_contacts;
create trigger hx_recall_contacts_guard before insert or update or delete on hx_recall_contacts for each row execute function hx_recall_contact_guard();
drop trigger if exists hx_recall_contacts_place on hx_recall_contacts;
create trigger hx_recall_contacts_place before insert or update on hx_recall_contacts for each row execute function hx_fl_guard();
drop trigger if exists hx_recall_contacts_audit on hx_recall_contacts;
create trigger hx_recall_contacts_audit after insert or update or delete on hx_recall_contacts for each row execute function hx_audit();
drop trigger if exists hx_recalls_guard on hx_recalls;
create trigger hx_recalls_guard before insert or update or delete on hx_recalls for each row execute function hx_recall_guard();
drop trigger if exists hx_recalls_place on hx_recalls;
create trigger hx_recalls_place before insert or update on hx_recalls for each row execute function hx_fl_guard();
drop trigger if exists hx_recalls_audit on hx_recalls;
create trigger hx_recalls_audit after insert or update on hx_recalls for each row execute function hx_audit();

alter table hx_recall_contacts enable row level security;
alter table hx_recalls enable row level security;
drop policy if exists hx_recall_contacts_read on hx_recall_contacts;
drop policy if exists hx_recall_contacts_insert on hx_recall_contacts;
drop policy if exists hx_recall_contacts_update on hx_recall_contacts;
drop policy if exists hx_recall_contacts_delete on hx_recall_contacts;
create policy hx_recall_contacts_read   on hx_recall_contacts for select to authenticated using (hx_can('recall',1,license_id));
create policy hx_recall_contacts_insert on hx_recall_contacts for insert to authenticated with check (hx_can('recall',2,license_id));
create policy hx_recall_contacts_update on hx_recall_contacts for update to authenticated using (hx_can('recall',2,license_id)) with check (hx_can('recall',2,license_id));
create policy hx_recall_contacts_delete on hx_recall_contacts for delete to authenticated using (hx_can('recall',3,license_id));
drop policy if exists hx_recalls_read on hx_recalls;
drop policy if exists hx_recalls_insert on hx_recalls;
drop policy if exists hx_recalls_update on hx_recalls;
create policy hx_recalls_read   on hx_recalls for select to authenticated using (hx_can('recall',1,license_id));
create policy hx_recalls_insert on hx_recalls for insert to authenticated with check (hx_can('recall',2,license_id));
create policy hx_recalls_update on hx_recalls for update to authenticated using (hx_can('recall',2,license_id)) with check (hx_can('recall',2,license_id));
grant select, insert, update, delete on hx_recall_contacts to authenticated;
grant select, insert, update on hx_recalls to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step19.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 19: Complaints and Internal Audits (CSQ 1.5, 1.7, 5.3)
-- Complaints (Black Fox / Michigan fields: title, type consumer / dispensary /
-- product return / adverse event, priority, product, lot number, description,
-- resolution, attachments) plus CSQ complaint management:
--   * numbered (CMP-YYYY-###), received date and channel, complainant and
--     customer, category, link to the batch / package tag (traceable)
--   * named investigator with a due date, investigation, root cause,
--     resolution, corrective action, linked deviation (-> CAPA) and hold
--   * response to the complainant; adverse events must be reported to the
--     state regulator before closing
--   * customer feedback with a 1-5 satisfaction rating (CSQ 5.3)
--   * never deleted (cancel with reason, Full access); closing is audited
-- Internal audits (Black Fox / Michigan fields: title, audit type, department,
-- date, lead auditor, scope, findings with severity and corrective action,
-- recommendations, conclusion, next audit date, attachments) plus CSQ 1.5:
--   * numbered (IA-YYYY-###), planned date, auditor qualification, auditor
--     confirmed independent of the area audited
--   * checklist of CSQ clauses with a result and evidence for each; the
--     standards page shows which clauses were audited in the last 12 months
--   * every nonconforming clause needs a finding; findings have an owner,
--     due date and a linked deviation (-> CAPA); a finding closes only with a
--     verification and only after its deviation is closed
--   * results shared with staff (who, when) before the audit is closed;
--     an audit closes only when every finding is closed
-- Access modules 'complaints' and 'intaudits': View (see; anyone with View can
--   log a complaint) / Edit (investigate, plan and run audits, findings) /
--   Full (close audits, reopen, cancel).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-18.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_complaints (
  id                     text primary key,
  state_id               text not null references hx_states(id),
  license_id             text not null references hx_licenses(id),
  number                 text not null default '',
  received_on            date not null default current_date,
  title                  text not null check (length(trim(title)) > 0),
  type                   text not null default 'consumer' check (type in ('consumer','dispensary','return','adverse_event','feedback')),
  priority               text not null default 'minor' check (priority in ('critical','major','minor')),
  channel                text not null default '',
  complainant            text not null default '',
  complainant_contact    text not null default '',
  customer               text not null default '',
  category               text not null default '',
  product                text not null default '',
  lot_number             text not null default '',
  batch_id               text references hx_batches(id),
  tag                    text not null default '',
  description            text not null default '',
  rating                 int check (rating between 1 and 5),
  investigator           text not null default '',
  due_date               date,
  investigation          text not null default '',
  root_cause             text not null default '',
  resolution             text not null default '',
  corrective_action      text not null default '',
  deviation_id           text,
  deviation_number       text not null default '',
  hold_id                text,
  response               text not null default '',
  responded_on           date,
  regulator_reported_on  date,
  status                 text not null default 'open' check (status in ('open','investigating','closed','cancelled')),
  closed_by              text not null default '',
  closed_at              timestamptz,
  cancel_reason          text not null default '',
  attachments            jsonb not null default '[]'::jsonb,
  created_by             text not null default '',
  created_by_id          uuid default auth.uid(),
  created_at             timestamptz not null default now(),
  updated_by             text not null default '',
  updated_at             timestamptz not null default now()
);
create unique index if not exists hx_complaints_number on hx_complaints(license_id, number);
create index if not exists hx_complaints_lic on hx_complaints(license_id, received_on desc);

create table if not exists hx_audits (
  id                     text primary key,
  state_id               text not null references hx_states(id),
  license_id             text not null references hx_licenses(id),
  number                 text not null default '',
  title                  text not null check (length(trim(title)) > 0),
  audit_type             text not null default 'CSQ internal audit',
  dept                   text not null default '',
  planned_date           date,
  audit_date             date,
  auditor_name           text not null default '',
  auditor_qualification  text not null default '',
  independent            boolean not null default false,
  scope                  text not null default '',
  clauses                jsonb not null default '[]'::jsonb,
  recommendations        text not null default '',
  conclusion             text not null default '',
  shared_with            text not null default '',
  shared_on              date,
  status                 text not null default 'planned' check (status in ('planned','in_progress','completed','closed','cancelled')),
  next_audit_date        date,
  attachments            jsonb not null default '[]'::jsonb,
  cancel_reason          text not null default '',
  closed_by              text not null default '',
  closed_at              timestamptz,
  created_by             text not null default '',
  created_by_id          uuid default auth.uid(),
  created_at             timestamptz not null default now(),
  updated_by             text not null default '',
  updated_at             timestamptz not null default now()
);
create unique index if not exists hx_audits_number on hx_audits(license_id, number);
create index if not exists hx_audits_lic on hx_audits(license_id, coalesce(audit_date, planned_date) desc);

create table if not exists hx_audit_findings (
  id                 text primary key,
  state_id           text not null references hx_states(id),
  license_id         text not null references hx_licenses(id),
  audit_id           text not null references hx_audits(id),
  clause             text not null default '',
  severity           text not null default 'minor' check (severity in ('critical','major','minor','observation')),
  description        text not null check (length(trim(description)) > 0),
  corrective_action  text not null default '',
  owner_name         text not null default '',
  due_date           date,
  deviation_id       text,
  deviation_number   text not null default '',
  status             text not null default 'open' check (status in ('open','closed')),
  verification       text not null default '',
  closed_by          text not null default '',
  closed_at          timestamptz,
  created_by         text not null default '',
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);
create index if not exists hx_audit_findings_audit on hx_audit_findings(audit_id);

-- ---------- complaints ----------
create or replace function hx_complaint_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; d record; v_edit boolean := hx_perm('complaints') >= 2; v_full boolean := hx_perm('complaints') >= 3;
begin
  if tg_op = 'DELETE' then raise exception 'Complaints are never deleted. Cancel with a reason.'; end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  if new.batch_id is not null then
    select * into b from hx_batches where id = new.batch_id;
    if b.id is null or b.license_id <> new.license_id then raise exception 'That batch belongs to a different license.'; end if;
    if coalesce(trim(new.lot_number),'') = '' then new.lot_number := b.batch_number; end if;
  end if;
  if new.deviation_id is not null then
    select id, number into d from hx_deviations where id = new.deviation_id and license_id = new.license_id;
    if d.id is null then raise exception 'Unknown deviation for this license.'; end if;
    new.deviation_number := d.number;
  end if;
  if new.type <> 'feedback' then new.rating := null; end if;
  if tg_op = 'INSERT' then
    if hx_perm('complaints') < 1 then raise exception 'You need access to Complaints.'; end if;
    if new.received_on > current_date then raise exception 'The received date cannot be in the future.'; end if;
    new.number := hx_next_number('hx_complaints', new.license_id, case when new.type = 'feedback' then 'FBK' else 'CMP' end);
    new.created_by := coalesce(hx_me(), new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('open','investigating') then raise exception 'A new complaint starts open.'; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', case when new.type = 'feedback' then 'Customer feedback logged' else 'Complaint logged' end, true);
    return new;
  end if;
  if new.number <> old.number or new.created_at <> old.created_at or new.created_by_id is distinct from old.created_by_id or new.license_id <> old.license_id then
    raise exception 'The number, date logged and license of a complaint cannot be changed.';
  end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'This complaint is %. Only someone with Full access can reopen it.', old.status; end if;
    if new.status = old.status then raise exception 'This complaint is %. Reopen it first.', old.status; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Complaint reopened', true);
    return new;
  end if;
  if not v_edit then raise exception 'You need Edit access to Complaints to investigate.'; end if;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access can cancel a complaint.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Complaint cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status = 'closed' then
    if new.type <> 'feedback' then
      if coalesce(trim(new.investigator),'') = '' then raise exception 'Name who investigated the complaint (CSQ 1.7 a).'; end if;
      if coalesce(trim(new.investigation),'') = '' then raise exception 'Record the investigation before closing.'; end if;
      if coalesce(trim(new.resolution),'') = '' then raise exception 'Record the resolution before closing.'; end if;
      if (coalesce(trim(new.complainant_contact),'') <> '' or coalesce(trim(new.customer),'') <> '') and new.responded_on is null then
        raise exception 'Record when the complainant was answered before closing (CSQ 1.7 a).';
      end if;
      if new.type = 'adverse_event' and new.regulator_reported_on is null then
        raise exception 'An adverse event must be reported to the state regulator before it is closed.';
      end if;
    end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Complaint closed: ' || left(coalesce(nullif(trim(new.resolution),''), 'feedback recorded'), 200), true);
    return new;
  end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Complaint updated', true); end if;
  return new;
end $$;

-- ---------- internal audits ----------
create or replace function hx_audit_rec_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_edit boolean := hx_perm('intaudits') >= 2; v_full boolean := hx_perm('intaudits') >= 3; c jsonb; v_missing text;
begin
  if tg_op = 'DELETE' then
    if old.status <> 'planned' or not v_full then raise exception 'Internal audits are never deleted once started. Cancel with a reason.'; end if;
    return old;
  end if;
  new.updated_at := now(); new.updated_by := coalesce(hx_me(), new.updated_by);
  if tg_op = 'INSERT' then
    if not v_edit then raise exception 'You need Edit access to Internal Audits.'; end if;
    new.number := hx_next_number('hx_audits', new.license_id, 'IA');
    new.created_by := coalesce(hx_me(), new.created_by); new.created_by_id := auth.uid(); new.created_at := now();
    if new.status not in ('planned','in_progress') then raise exception 'A new audit starts planned or in progress.'; end if;
    new.closed_by := ''; new.closed_at := null; new.cancel_reason := '';
    perform set_config('hx.reason', 'Internal audit ' || new.status, true);
    return new;
  end if;
  if new.number <> old.number or new.created_at <> old.created_at or new.license_id <> old.license_id then raise exception 'The number and license of an audit cannot be changed.'; end if;
  if old.status in ('closed','cancelled') then
    if not v_full then raise exception 'This audit is %. Only someone with Full access can reopen it.', old.status; end if;
    if new.status = old.status then raise exception 'This audit is %. Reopen it first.', old.status; end if;
    new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Audit reopened', true);
    return new;
  end if;
  if not v_edit then raise exception 'You need Edit access to Internal Audits.'; end if;
  if new.status = 'cancelled' then
    if not v_full then raise exception 'Only someone with Full access can cancel an audit.'; end if;
    if coalesce(trim(new.cancel_reason),'') = '' then raise exception 'A reason is required to cancel.'; end if;
    perform set_config('hx.reason', 'Audit cancelled: ' || trim(new.cancel_reason), true);
    return new;
  end if;
  if new.status in ('completed','closed') then
    if new.audit_date is null or new.audit_date > current_date then raise exception 'Enter the date the audit was done (not in the future).'; end if;
    if coalesce(trim(new.auditor_name),'') = '' or coalesce(trim(new.auditor_qualification),'') = '' then raise exception 'Name the auditor and their qualification (CSQ 1.5 b).'; end if;
    if not new.independent then raise exception 'Confirm the auditor does not audit their own work (CSQ 1.5 c).'; end if;
    if jsonb_array_length(new.clauses) = 0 and coalesce(trim(new.scope),'') = '' then raise exception 'Record what was audited (clauses or scope).'; end if;
    if exists (select 1 from jsonb_array_elements(new.clauses) x where coalesce(x->>'result','') = '') then raise exception 'Every clause on the checklist needs a result.'; end if;
    select string_agg(x->>'clause', ', ') into v_missing from jsonb_array_elements(new.clauses) x
     where x->>'result' = 'Nonconforming' and not exists (select 1 from hx_audit_findings f where f.audit_id = new.id and f.clause = x->>'clause');
    if v_missing is not null then raise exception 'Record a finding for each nonconforming clause: %', v_missing; end if;
  end if;
  if new.status = 'closed' and old.status <> 'closed' then
    if not v_full then raise exception 'Only someone with Full access can close an audit.'; end if;
    if exists (select 1 from hx_audit_findings f where f.audit_id = new.id and f.status <> 'closed') then raise exception 'Close every finding first (CSQ 1.5 f).'; end if;
    if new.shared_on is null or coalesce(trim(new.shared_with),'') = '' then raise exception 'Record who the results were shared with and when (CSQ 1.5 e).'; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Audit closed', true);
    return new;
  end if;
  if new.status = 'completed' and old.status <> 'completed' then perform set_config('hx.reason', 'Audit completed', true);
  elsif coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Audit updated', true); end if;
  return new;
end $$;

create or replace function hx_finding_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare a record; v_dst text; v_dno text;
begin
  if tg_op = 'DELETE' then
    select * into a from hx_audits where id = old.audit_id;
    if a.status not in ('planned','in_progress') or hx_perm('intaudits') < 2 then raise exception 'Findings of a completed audit are never deleted.'; end if;
    return old;
  end if;
  select * into a from hx_audits where id = new.audit_id;
  if a.id is null or a.license_id <> new.license_id then raise exception 'Unknown audit for this license.'; end if;
  if a.status in ('closed','cancelled') then raise exception 'This audit is %.', a.status; end if;
  if hx_perm('intaudits') < 2 then raise exception 'You need Edit access to Internal Audits.'; end if;
  new.updated_at := now();
  if new.deviation_id is not null then
    select number, status into v_dno, v_dst from hx_deviations where id = new.deviation_id and license_id = new.license_id;
    if v_dno is null then raise exception 'Unknown deviation for this license.'; end if;
    new.deviation_number := v_dno;
  end if;
  if tg_op = 'INSERT' then
    new.created_by := coalesce(hx_me(),''); new.created_at := now(); new.status := 'open'; new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Finding recorded (' || new.severity || ')', true);
    return new;
  end if;
  if old.status = 'closed' then
    if hx_perm('intaudits') < 3 then raise exception 'This finding is closed. Only someone with Full access can reopen it.'; end if;
    if new.status = 'closed' then raise exception 'This finding is closed. Reopen it first.'; end if;
    new.closed_by := ''; new.closed_at := null;
    perform set_config('hx.reason', 'Finding reopened', true);
    return new;
  end if;
  if new.status = 'closed' then
    if coalesce(trim(new.verification),'') = '' then raise exception 'Record how the correction was verified as effective (CSQ 1.5 f).'; end if;
    if new.severity <> 'observation' and new.deviation_id is null and coalesce(trim(new.corrective_action),'') = '' then raise exception 'Record the corrective action (or link a deviation) before closing.'; end if;
    if new.deviation_id is not null and coalesce(v_dst,'') <> 'closed' then raise exception 'Close deviation % first (corrective action process).', v_dno; end if;
    new.closed_by := coalesce(hx_me(),''); new.closed_at := now();
    perform set_config('hx.reason', 'Finding closed: ' || left(trim(new.verification), 200), true);
    return new;
  end if;
  if coalesce(current_setting('hx.reason', true), '') = '' then perform set_config('hx.reason', 'Finding updated', true); end if;
  return new;
end $$;

drop trigger if exists hx_complaints_guard on hx_complaints;
create trigger hx_complaints_guard before insert or update or delete on hx_complaints for each row execute function hx_complaint_guard();
drop trigger if exists hx_complaints_place on hx_complaints;
create trigger hx_complaints_place before insert or update on hx_complaints for each row execute function hx_fl_guard();
drop trigger if exists hx_complaints_audit on hx_complaints;
create trigger hx_complaints_audit after insert or update on hx_complaints for each row execute function hx_audit();
drop trigger if exists hx_audits_guard on hx_audits;
create trigger hx_audits_guard before insert or update or delete on hx_audits for each row execute function hx_audit_rec_guard();
drop trigger if exists hx_audits_place on hx_audits;
create trigger hx_audits_place before insert or update on hx_audits for each row execute function hx_fl_guard();
drop trigger if exists hx_audits_audit on hx_audits;
create trigger hx_audits_audit after insert or update or delete on hx_audits for each row execute function hx_audit();
drop trigger if exists hx_audit_findings_guard on hx_audit_findings;
create trigger hx_audit_findings_guard before insert or update or delete on hx_audit_findings for each row execute function hx_finding_guard();
drop trigger if exists hx_audit_findings_place on hx_audit_findings;
create trigger hx_audit_findings_place before insert or update on hx_audit_findings for each row execute function hx_fl_guard();
drop trigger if exists hx_audit_findings_audit on hx_audit_findings;
create trigger hx_audit_findings_audit after insert or update or delete on hx_audit_findings for each row execute function hx_audit();

alter table hx_complaints enable row level security;
alter table hx_audits enable row level security;
alter table hx_audit_findings enable row level security;
drop policy if exists hx_complaints_read on hx_complaints;
drop policy if exists hx_complaints_insert on hx_complaints;
drop policy if exists hx_complaints_update on hx_complaints;
create policy hx_complaints_read   on hx_complaints for select to authenticated using (hx_can('complaints',1,license_id));
create policy hx_complaints_insert on hx_complaints for insert to authenticated with check (hx_can('complaints',1,license_id));
create policy hx_complaints_update on hx_complaints for update to authenticated using (hx_can('complaints',2,license_id)) with check (hx_can('complaints',2,license_id));
drop policy if exists hx_audits_read on hx_audits;
drop policy if exists hx_audits_insert on hx_audits;
drop policy if exists hx_audits_update on hx_audits;
drop policy if exists hx_audits_delete on hx_audits;
create policy hx_audits_read   on hx_audits for select to authenticated using (hx_can('intaudits',1,license_id));
create policy hx_audits_insert on hx_audits for insert to authenticated with check (hx_can('intaudits',2,license_id));
create policy hx_audits_update on hx_audits for update to authenticated using (hx_can('intaudits',2,license_id)) with check (hx_can('intaudits',2,license_id));
create policy hx_audits_delete on hx_audits for delete to authenticated using (hx_can('intaudits',3,license_id));
drop policy if exists hx_audit_findings_read on hx_audit_findings;
drop policy if exists hx_audit_findings_insert on hx_audit_findings;
drop policy if exists hx_audit_findings_update on hx_audit_findings;
drop policy if exists hx_audit_findings_delete on hx_audit_findings;
create policy hx_audit_findings_read   on hx_audit_findings for select to authenticated using (hx_can('intaudits',1,license_id));
create policy hx_audit_findings_insert on hx_audit_findings for insert to authenticated with check (hx_can('intaudits',2,license_id));
create policy hx_audit_findings_update on hx_audit_findings for update to authenticated using (hx_can('intaudits',2,license_id)) with check (hx_can('intaudits',2,license_id));
create policy hx_audit_findings_delete on hx_audit_findings for delete to authenticated using (hx_can('intaudits',2,license_id));
grant select, insert, update on hx_complaints to authenticated;
grant select, insert, update, delete on hx_audits, hx_audit_findings to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step20.sql
-- ###################################################################
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


-- ###################################################################
-- ### hendrix_step21.sql
-- ###################################################################
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


-- ###################################################################
-- ### hendrix_step22.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 22: Rulebook PDF import
-- Upload the state's official rules PDF (for example Missouri 19 CSR 100-1,
-- or the Michigan CRA administrative rules) in the Rulebook and Hendrix
-- splits it into rules, sorts them into categories and keeps them in the
-- official order. Uploading a newer PDF later shows what is new / changed
-- and updates the Rulebook.
--   * hx_rules.sort       official order of the rule in its PDF
--   * hx_rules.source_id  the PDF the rule came from (blank = typed by hand)
--   * hx_rule_sources     every PDF imported per state: file kept in the
--                         private hendrix-files bucket, date, who, counts
-- Access module 'rulebook': View (see) / Edit (import, add, edit) /
--   Full (delete rules, remove a PDF from the list).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-21.
-- Safe to run more than once.
-- =====================================================================

alter table hx_rules add column if not exists sort int;
alter table hx_rules add column if not exists source_id text;
create index if not exists hx_rules_state on hx_rules(state_id);

create table if not exists hx_rule_sources (
  id            text primary key,
  state_id      text not null references hx_states(id),
  name          text not null default '',
  file_path     text not null default '',
  pages         int not null default 0,
  format        text not null default '',
  rules_found   int not null default 0,
  added         int not null default 0,
  updated       int not null default 0,
  removed       int not null default 0,
  created_by    uuid default auth.uid(),
  created_by_name text not null default '',
  created_at    timestamptz not null default now()
);
create index if not exists hx_rule_sources_state on hx_rule_sources(state_id);

drop trigger if exists hx_rule_sources_audit on hx_rule_sources;
create trigger hx_rule_sources_audit after insert or update or delete on hx_rule_sources for each row execute function hx_audit();

alter table hx_rule_sources enable row level security;
drop policy if exists hx_rule_sources_read on hx_rule_sources;
drop policy if exists hx_rule_sources_insert on hx_rule_sources;
drop policy if exists hx_rule_sources_update on hx_rule_sources;
drop policy if exists hx_rule_sources_delete on hx_rule_sources;
create policy hx_rule_sources_read   on hx_rule_sources for select to authenticated using (hx_can('rulebook',1));
create policy hx_rule_sources_insert on hx_rule_sources for insert to authenticated with check (hx_can('rulebook',2));
create policy hx_rule_sources_update on hx_rule_sources for update to authenticated using (hx_can('rulebook',2)) with check (hx_can('rulebook',2));
create policy hx_rule_sources_delete on hx_rule_sources for delete to authenticated using (hx_can('rulebook',3));
grant select, insert, update, delete on hx_rule_sources to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step23.sql
-- ###################################################################
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


-- ###################################################################
-- ### hendrix_step24.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 24: Equipment register and Chemical register (SDS)
-- Equipment (CSQ 2A.2.1 equipment, 2A.2.2 maintenance, 2A.2.3 calibration,
-- 5.1.7 validation, 3A.1.4 cultivation equipment, 3B.1.1-3B.1.2 extraction):
--   * every piece of equipment and instrument per license: number EQ-###,
--     category, location, make / model / serial / asset tag, product contact,
--     critical to safety or quality, status (in service / out of service / retired)
--   * master preventive maintenance schedule: interval and the manufacturer's
--     tasks; the work itself is recorded in the Equipment Maintenance Log
--     (Facility Logs, also on the kiosk) - the register picks it up
--   * calibration: interval, method, reference standard (NIST / ASTM),
--     protection from adjustment; each calibration with its certificate and
--     the next due date; a failed calibration takes it out of service
--   * validation IQ / OQ / PQ with yearly revalidation
--   * temporary repairs with a fix-by date until made permanent
--   * out of service / back in service (tools, lubricants and debris removed,
--     cleaned, checked working)
-- Chemicals (CSQ 2A.9.2 chemical controls, 2A.5.1 pest control chemicals):
--   * approved chemical list per license: number CHEM-###, purpose, food grade
--     or not, SDS on file (required to approve), storage area, restricted,
--     hazards, PPE, first aid, spill response, disposal, EPA registration for
--     pesticides; approval by Full access; removal with a reason
-- Access modules 'equipment' and 'chemicals': View / Edit (add, record) /
--   Full (retire, approve chemicals, remove, void events).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-23.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_next_seq(p_table text, p_lic text, p_prefix text) returns text
language plpgsql security definer set search_path = public as $$
declare v_max int;
begin
  perform pg_advisory_xact_lock(hashtext(p_table || p_lic));
  execute format('select coalesce(max((regexp_match(number, %L))[1]::int), 0) from %I where license_id = $1',
                 '^' || p_prefix || '-(\d+)$', p_table) into v_max using p_lic;
  return p_prefix || '-' || lpad((v_max + 1)::text, 3, '0');
end $$;

-- ---------- equipment ----------
create table if not exists hx_equipment (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  name             text not null check (length(trim(name)) > 0),
  category         text not null default 'Production',
  location         text not null default '',
  make             text not null default '',
  model            text not null default '',
  serial           text not null default '',
  asset_tag        text not null default '',
  product_contact  boolean not null default false,
  critical         boolean not null default false,
  status           text not null default 'in_service' check (status in ('in_service','out_of_service','retired')),
  installed_on     date,
  controls_note    text not null default '',
  pm_interval_days int check (pm_interval_days is null or pm_interval_days > 0),
  pm_tasks         text not null default '',
  cal_required     boolean not null default false,
  cal_interval_months int check (cal_interval_months is null or cal_interval_months > 0),
  cal_method       text not null default '',
  cal_standard     text not null default '',
  cal_protection   text not null default '',
  cal_last         date,
  cal_due          date,
  val_required     boolean not null default false,
  iq_on            date,
  oq_on            date,
  pq_on            date,
  reval_due        date,
  log_item_id      text,
  files            jsonb not null default '[]'::jsonb,
  notes            text not null default '',
  retired_reason   text,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_equipment_number on hx_equipment(license_id, number);
create index if not exists hx_equipment_lic on hx_equipment(license_id, status);

create table if not exists hx_equipment_events (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  equipment_id  text not null references hx_equipment(id),
  kind          text not null check (kind in ('calibration','validation','temporary_repair','out_of_service','return_to_service','note')),
  done_on       date not null default current_date,
  done_by       text not null default '',
  details       text not null default '',
  result        text not null default '' check (result in ('','pass','fail')),
  stage         text not null default '' check (stage in ('','IQ','OQ','PQ','Revalidation')),
  standard      text not null default '',
  next_due      date,
  fix_by        date,
  closed_on     date,
  closed_by     text not null default '',
  closure       text not null default '',
  checks        jsonb not null default '{}'::jsonb,
  deviation_id  text,
  files         jsonb not null default '[]'::jsonb,
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_equipment_events_eq on hx_equipment_events(equipment_id, done_on desc);

create or replace function hx_equipment_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_equipment_events where equipment_id = old.id) then
      raise exception 'This equipment has calibration, validation or service records. Retire it instead of deleting it.';
    end if;
    if not hx_can('equipment', 3, old.license_id) then raise exception 'Only Full access can delete equipment.'; end if;
    return old;
  end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_equipment', new.license_id, 'EQ');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now();
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  if coalesce(current_setting('hx.internal', true), '') <> 'on' then
    if new.status = 'retired' and (tg_op = 'INSERT' or old.status <> 'retired') then
      if not hx_can('equipment', 3, new.license_id) then raise exception 'Only Full access can retire equipment.'; end if;
      if coalesce(trim(new.retired_reason), '') = '' then raise exception 'Give a reason for retiring this equipment.'; end if;
      perform set_config('hx.reason', 'Retired: ' || trim(new.retired_reason), true);
    end if;
    if tg_op = 'UPDATE' and old.status = 'retired' and new.status <> 'retired' and not hx_can('equipment', 3, new.license_id) then
      raise exception 'Only Full access can bring retired equipment back.';
    end if;
    -- status, calibration and validation dates come from the recorded events
    if tg_op = 'UPDATE' and (new.status in ('in_service','out_of_service') and old.status in ('in_service','out_of_service') and new.status <> old.status) then
      raise exception 'Use "Out of service" / "Back in service" so the reason and checks are recorded.';
    end if;
    if tg_op = 'UPDATE' and (new.cal_last, new.cal_due, new.iq_on, new.oq_on, new.pq_on, new.reval_due) is distinct from (old.cal_last, old.cal_due, old.iq_on, old.oq_on, old.pq_on, old.reval_due) then
      raise exception 'Calibration and validation dates come from the recorded calibrations and validations.';
    end if;
  end if;
  if new.cal_required and new.cal_interval_months is null then raise exception 'Enter how often it is calibrated (months).'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_equipment_guard on hx_equipment;
create trigger hx_equipment_guard before insert or update or delete on hx_equipment for each row execute function hx_equipment_guard();
drop trigger if exists hx_equipment_place on hx_equipment;
create trigger hx_equipment_place before insert or update on hx_equipment for each row execute function hx_fl_guard();
drop trigger if exists hx_equipment_audit on hx_equipment;
create trigger hx_equipment_audit after insert or update or delete on hx_equipment for each row execute function hx_audit();

create or replace function hx_equipment_event_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare e record; v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then raise exception 'Equipment records are never deleted. Void the record with a reason.'; end if;
  select * into e from hx_equipment where id = coalesce(new.equipment_id, old.equipment_id);
  if e.id is null then raise exception 'Unknown equipment.'; end if;
  if tg_op = 'INSERT' then
    if e.license_id <> new.license_id then raise exception 'That equipment belongs to another license.'; end if;
    if e.status = 'retired' then raise exception 'This equipment is retired.'; end if;
    if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
    new.recorded_by := v_me; new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
    new.closed_on := null; new.closed_by := ''; new.closure := '';
    if new.kind = 'calibration' then
      if new.result = '' then raise exception 'Record the calibration result (pass or fail).'; end if;
      if jsonb_array_length(new.files) = 0 and coalesce(trim(new.standard), '') = '' then
        raise exception 'Attach the calibration certificate or name the reference standard used (e.g. NIST-traceable weights).';
      end if;
      if new.result = 'pass' and new.next_due is null then
        new.next_due := case when e.cal_interval_months is not null then (new.done_on + make_interval(months => e.cal_interval_months))::date end;
        if new.next_due is null then raise exception 'Enter the next calibration due date.'; end if;
      end if;
    elsif new.kind = 'validation' then
      if new.stage = '' then raise exception 'Choose IQ, OQ, PQ or revalidation.'; end if;
      if new.result = '' then raise exception 'Record the validation result (pass or fail).'; end if;
    elsif new.kind = 'temporary_repair' then
      if coalesce(trim(new.details), '') = '' then raise exception 'Describe the temporary repair.'; end if;
      if new.fix_by is null then raise exception 'Set the date the permanent repair must be done by.'; end if;
    elsif new.kind = 'out_of_service' then
      if coalesce(trim(new.details), '') = '' then raise exception 'Say why it is out of service.'; end if;
      if e.status <> 'in_service' then raise exception 'It is already out of service.'; end if;
    elsif new.kind = 'return_to_service' then
      if e.status <> 'out_of_service' then raise exception 'It is not out of service.'; end if;
      if coalesce((new.checks->>'cleared')::boolean, false) is not true or coalesce((new.checks->>'cleaned')::boolean, false) is not true
         or coalesce((new.checks->>'working')::boolean, false) is not true then
        raise exception 'Confirm tools, lubricants and debris are removed, the equipment is cleaned and sanitized, and it was checked working.';
      end if;
      if e.cal_required and (e.cal_due is null or e.cal_due < current_date) then raise exception 'The calibration is out of date. Record a calibration first.'; end if;
    end if;
    return new;
  end if;
  -- updates: close a temporary repair, add files, or void
  if old.voided then raise exception 'This record is void.'; end if;
  if new.voided then
    if not hx_can('equipment', 3, old.license_id) then raise exception 'Only Full access can void an equipment record.'; end if;
    if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
    new.voided_at := now();
    perform set_config('hx.reason', trim(new.void_reason), true);
    return new;
  end if;
  if (to_jsonb(new) - 'files' - 'closed_on' - 'closed_by' - 'closure' - 'deviation_id') is distinct from (to_jsonb(old) - 'files' - 'closed_on' - 'closed_by' - 'closure' - 'deviation_id') then
    raise exception 'An equipment record cannot be changed. Void it and record it again.';
  end if;
  if new.closed_on is not null and old.closed_on is null then
    if old.kind <> 'temporary_repair' then raise exception 'Only temporary repairs are closed.'; end if;
    if coalesce(trim(new.closure), '') = '' then raise exception 'Describe the permanent repair.'; end if;
    new.closed_by := v_me;
    perform set_config('hx.reason', 'Temporary repair made permanent', true);
  elsif old.closed_on is not null and new.closed_on is distinct from old.closed_on then
    raise exception 'This repair is already closed.';
  end if;
  return new;
end $$;
drop trigger if exists hx_equipment_events_guard on hx_equipment_events;
create trigger hx_equipment_events_guard before insert or update or delete on hx_equipment_events for each row execute function hx_equipment_event_guard();
drop trigger if exists hx_equipment_events_place on hx_equipment_events;
create trigger hx_equipment_events_place before insert or update on hx_equipment_events for each row execute function hx_fl_guard();
drop trigger if exists hx_equipment_events_audit on hx_equipment_events;
create trigger hx_equipment_events_audit after insert or update on hx_equipment_events for each row execute function hx_audit();

-- the equipment's status, calibration and validation dates follow its events
create or replace function hx_equipment_event_apply() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_id text := new.equipment_id; c record; v_why text;
begin
  v_why := case new.kind when 'calibration' then 'Calibration ' || coalesce(nullif(new.result,''),'recorded') when 'validation' then new.stage || ' ' || coalesce(nullif(new.result,''),'recorded')
    when 'out_of_service' then 'Out of service: ' || new.details when 'return_to_service' then 'Back in service' when 'temporary_repair' then 'Temporary repair' else 'Equipment record' end
    || case when new.voided then ' (record voided)' else '' end;
  perform set_config('hx.internal', 'on', true);
  select done_on, next_due into c from hx_equipment_events
   where equipment_id = v_id and kind = 'calibration' and result = 'pass' and not voided order by done_on desc, created_at desc limit 1;
  perform set_config('hx.reason', v_why, true);
  update hx_equipment set cal_last = c.done_on, cal_due = c.next_due,
     iq_on = (select max(done_on) from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage = 'IQ' and result = 'pass' and not voided),
     oq_on = (select max(done_on) from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage = 'OQ' and result = 'pass' and not voided),
     pq_on = (select max(done_on) from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage in ('PQ','Revalidation') and result = 'pass' and not voided),
     reval_due = (select (max(done_on) + interval '1 year')::date from hx_equipment_events where equipment_id = v_id and kind = 'validation' and stage in ('PQ','Revalidation') and result = 'pass' and not voided)
   where id = v_id;
  if tg_op = 'INSERT' and not new.voided then
    perform set_config('hx.reason', v_why, true);
    if new.kind = 'out_of_service' or (new.kind in ('calibration','validation') and new.result = 'fail') then
      update hx_equipment set status = 'out_of_service' where id = v_id and status = 'in_service';
    elsif new.kind = 'return_to_service' then
      update hx_equipment set status = 'in_service' where id = v_id and status = 'out_of_service';
    end if;
  end if;
  perform set_config('hx.internal', '', true);
  return null;
end $$;
drop trigger if exists hx_equipment_events_zapply on hx_equipment_events;
create trigger hx_equipment_events_zapply after insert or update on hx_equipment_events for each row execute function hx_equipment_event_apply();

-- ---------- chemicals ----------
create table if not exists hx_chemicals (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  name             text not null check (length(trim(name)) > 0),
  manufacturer     text not null default '',
  product_code     text not null default '',
  purpose          text not null default 'Cleaner',
  grade            text not null default 'non_food' check (grade in ('food_grade','food_contact_sanitizer','non_food')),
  status           text not null default 'pending' check (status in ('pending','approved','removed')),
  sds_files        jsonb not null default '[]'::jsonb,
  sds_date         date,
  hazards          text not null default '',
  ppe              text not null default '',
  first_aid        text not null default '',
  spill            text not null default '',
  storage_area     text not null default '',
  restricted       boolean not null default false,
  disposal         text not null default '',
  epa_reg          text not null default '',
  supplier_id      text,
  notes            text not null default '',
  approved_by      text not null default '',
  approved_at      timestamptz,
  removed_reason   text,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_chemicals_number on hx_chemicals(license_id, number);

create or replace function hx_chemical_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if old.status <> 'pending' then raise exception 'An approved chemical is never deleted. Remove it from use with a reason.'; end if;
    return old;
  end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_chemicals', new.license_id, 'CHEM');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now();
    if new.status <> 'pending' and not hx_can('chemicals', 3, new.license_id) then new.status := 'pending'; end if;
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  end if;
  if new.status = 'approved' then
    if tg_op = 'INSERT' or old.status <> 'approved' then
      if not hx_can('chemicals', 3, new.license_id) then raise exception 'Only Full access can approve a chemical.'; end if;
      new.approved_by := coalesce(hx_me(), ''); new.approved_at := now();
      perform set_config('hx.reason', 'Chemical approved for use', true);
    else
      new.approved_by := old.approved_by; new.approved_at := old.approved_at;
    end if;
    if jsonb_array_length(new.sds_files) = 0 then raise exception 'Attach the Safety Data Sheet (SDS) before approving.'; end if;
    if coalesce(trim(new.storage_area), '') = '' then raise exception 'Enter where it is stored.'; end if;
    if coalesce(trim(new.ppe), '') = '' then raise exception 'Enter the PPE needed (from the SDS).'; end if;
    if new.purpose = 'Pesticide / crop protection' and coalesce(trim(new.epa_reg), '') = '' then raise exception 'Enter the EPA registration number of the pesticide.'; end if;
  elsif new.status = 'removed' then
    if tg_op = 'INSERT' or old.status <> 'removed' then
      if not hx_can('chemicals', 3, new.license_id) then raise exception 'Only Full access can remove a chemical from use.'; end if;
      if coalesce(trim(new.removed_reason), '') = '' then raise exception 'Give a reason for removing this chemical.'; end if;
      perform set_config('hx.reason', 'Removed from use: ' || trim(new.removed_reason), true);
    end if;
  else
    if tg_op = 'UPDATE' and old.status <> 'pending' and not hx_can('chemicals', 3, new.license_id) then raise exception 'Only Full access can change the status.'; end if;
    new.approved_by := ''; new.approved_at := null;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_chemicals_guard on hx_chemicals;
create trigger hx_chemicals_guard before insert or update or delete on hx_chemicals for each row execute function hx_chemical_guard();
drop trigger if exists hx_chemicals_place on hx_chemicals;
create trigger hx_chemicals_place before insert or update on hx_chemicals for each row execute function hx_fl_guard();
drop trigger if exists hx_chemicals_audit on hx_chemicals;
create trigger hx_chemicals_audit after insert or update or delete on hx_chemicals for each row execute function hx_audit();

-- ---------- access ----------
alter table hx_equipment enable row level security;
alter table hx_equipment_events enable row level security;
alter table hx_chemicals enable row level security;
drop policy if exists hx_equipment_read on hx_equipment;
drop policy if exists hx_equipment_insert on hx_equipment;
drop policy if exists hx_equipment_update on hx_equipment;
drop policy if exists hx_equipment_delete on hx_equipment;
create policy hx_equipment_read   on hx_equipment for select to authenticated using (hx_can('equipment',1,license_id));
create policy hx_equipment_insert on hx_equipment for insert to authenticated with check (hx_can('equipment',2,license_id));
create policy hx_equipment_update on hx_equipment for update to authenticated using (hx_can('equipment',2,license_id)) with check (hx_can('equipment',2,license_id));
create policy hx_equipment_delete on hx_equipment for delete to authenticated using (hx_can('equipment',3,license_id));
drop policy if exists hx_equipment_events_read on hx_equipment_events;
drop policy if exists hx_equipment_events_insert on hx_equipment_events;
drop policy if exists hx_equipment_events_update on hx_equipment_events;
create policy hx_equipment_events_read   on hx_equipment_events for select to authenticated using (hx_can('equipment',1,license_id));
create policy hx_equipment_events_insert on hx_equipment_events for insert to authenticated with check (hx_can('equipment',2,license_id));
create policy hx_equipment_events_update on hx_equipment_events for update to authenticated using (hx_can('equipment',2,license_id)) with check (hx_can('equipment',2,license_id));
drop policy if exists hx_chemicals_read on hx_chemicals;
drop policy if exists hx_chemicals_insert on hx_chemicals;
drop policy if exists hx_chemicals_update on hx_chemicals;
drop policy if exists hx_chemicals_delete on hx_chemicals;
create policy hx_chemicals_read   on hx_chemicals for select to authenticated using (hx_can('chemicals',1,license_id));
create policy hx_chemicals_insert on hx_chemicals for insert to authenticated with check (hx_can('chemicals',2,license_id));
create policy hx_chemicals_update on hx_chemicals for update to authenticated using (hx_can('chemicals',2,license_id)) with check (hx_can('chemicals',2,license_id));
create policy hx_chemicals_delete on hx_chemicals for delete to authenticated using (hx_can('chemicals',3,license_id));
grant select, insert, update, delete on hx_equipment, hx_chemicals to authenticated;
grant select, insert, update on hx_equipment_events to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step25.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 25: Line clearance and Rework
-- Line clearance / pre-operational inspection (CSQ 2A.12.3, 3B.1.2):
--   * numbered LC-YYYY-###, linked to a batch (or a room / line), the
--     equipment used from the Equipment register, a checklist (previous
--     product and labels removed, cleaned and sanitized, equipment in date,
--     right materials staged, cGMP dress, no foreign matter, tools counted;
--     extraction adds gas detection / fire safety and ventilation)
--   * every failed item needs the problem and its correction; the line is
--     cleared only when every failure was corrected
--   * the database refuses "cleared" while any equipment used is out of
--     service, retired, or past its calibration due date
-- Rework (CSQ 2A.12.5, 3B.1.12 e):
--   * numbered RW-YYYY-###, dated and tagged, from a batch, a hold or other
--   * inspected and analyzed before use (pass / fail); approved by Full
--     access, confirmed like-to-like; its expiry must not be before the
--     expiry of the product it goes into; used in a target batch (traceable)
--     or destroyed with a reason
-- Access modules 'lineclear' and 'rework': View / Edit (record) /
--   Full (void line clearances; approve rework, destroy).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-24.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_line_clearances (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  number        text not null default '',
  batch_id      text references hx_batches(id),
  batch_label   text not null default '',
  batch_type    text not null default '',
  area          text not null default '',
  equipment_ids text[] not null default '{}',
  checks        jsonb not null default '{}'::jsonb,
  issues        text not null default '',
  corrections   text not null default '',
  result        text not null default 'cleared' check (result in ('cleared','not_cleared')),
  checked_by    text not null default '',
  verified_by   text not null default '',
  deviation_id  text,
  checked_at    timestamptz not null default now(),
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create unique index if not exists hx_line_clearances_number on hx_line_clearances(license_id, number);
create index if not exists hx_line_clearances_batch on hx_line_clearances(batch_id);

create or replace function hx_line_clearance_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v jsonb; n_fail int := 0; n_unfixed int := 0; e record; v_bad text := '';
begin
  if tg_op = 'DELETE' then raise exception 'Line clearances are never deleted. Void it with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This line clearance is void.'; end if;
    if new.voided then
      if not hx_can('lineclear', 3, old.license_id) then raise exception 'Only Full access can void a line clearance.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a line clearance.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then
        raise exception 'Void a line clearance without changing anything else.';
      end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'deviation_id') is distinct from (to_jsonb(old) - 'deviation_id') then
      raise exception 'A line clearance cannot be changed. Void it and record a new one.';
    end if;
    return new;
  end if;
  new.number := hx_next_number('hx_line_clearances', new.license_id, 'LC');
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.checked_at := now();
  new.voided := false; new.void_reason := null; new.voided_at := null;
  if coalesce(trim(new.checked_by), '') = '' then raise exception 'Enter who did the inspection.'; end if;
  if new.batch_id is not null then
    if not exists (select 1 from hx_batches b where b.id = new.batch_id and b.license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
  elsif coalesce(trim(new.area), '') = '' then
    raise exception 'Choose the batch or enter the room / line inspected.';
  end if;
  if jsonb_typeof(new.checks) <> 'object' or new.checks = '{}'::jsonb then raise exception 'Complete the checklist.'; end if;
  for k, v in select * from jsonb_each(new.checks) loop
    if v->>'r' not in ('pass','fail','na') then raise exception 'Answer every item on the checklist.'; end if;
    if v->>'r' = 'fail' then n_fail := n_fail + 1; if coalesce((v->>'fixed')::boolean, false) is not true then n_unfixed := n_unfixed + 1; end if; end if;
  end loop;
  if n_fail > 0 and (coalesce(trim(new.issues), '') = '' or coalesce(trim(new.corrections), '') = '') then
    raise exception 'Describe each problem found and the correction or corrective action.';
  end if;
  for e in select * from hx_equipment where id = any(new.equipment_ids) loop
    if e.license_id <> new.license_id then raise exception 'Equipment % belongs to another license.', e.number; end if;
    if e.status <> 'in_service' then v_bad := v_bad || e.number || ' ' || e.name || ' is ' || replace(e.status, '_', ' ') || '. '; end if;
    if e.cal_required and (e.cal_due is null or e.cal_due < current_date) then v_bad := v_bad || e.number || ' ' || e.name || ' calibration is out of date. '; end if;
  end loop;
  if new.result = 'cleared' then
    if n_unfixed > 0 then raise exception 'The line cannot be cleared: % failed item(s) not corrected.', n_unfixed; end if;
    if v_bad <> '' then raise exception 'The line cannot be cleared: %', v_bad; end if;
  end if;
  perform set_config('hx.reason', case when new.result = 'cleared' then 'Line cleared' else 'Line NOT cleared' end, true);
  return new;
end $$;
drop trigger if exists hx_line_clearances_guard on hx_line_clearances;
create trigger hx_line_clearances_guard before insert or update or delete on hx_line_clearances for each row execute function hx_line_clearance_guard();
drop trigger if exists hx_line_clearances_place on hx_line_clearances;
create trigger hx_line_clearances_place before insert or update on hx_line_clearances for each row execute function hx_fl_guard();
drop trigger if exists hx_line_clearances_audit on hx_line_clearances;
create trigger hx_line_clearances_audit after insert or update on hx_line_clearances for each row execute function hx_audit();

create table if not exists hx_rework (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  source_kind      text not null default 'batch' check (source_kind in ('batch','hold','other')),
  source_batch_id  text references hx_batches(id),
  source_hold_id   text references hx_holds(id),
  source_text      text not null default '',
  material         text not null check (length(trim(material)) > 0),
  product          text not null default '',
  quantity         text not null default '',
  unit             text not null default 'g',
  reason           text not null check (length(trim(reason)) > 0),
  identified_on    date not null default current_date,
  tag              text not null default '',
  location         text not null default '',
  expires_on       date,
  status           text not null default 'identified' check (status in ('identified','inspected','approved','used','destroyed')),
  inspection       text not null default '',
  analysis         text not null default '',
  inspection_result text not null default '' check (inspection_result in ('','pass','fail')),
  inspected_by     text not null default '',
  inspected_on     date,
  like_to_like     boolean not null default false,
  like_note        text not null default '',
  approved_by      text not null default '',
  approved_at      timestamptz,
  target_batch_id  text references hx_batches(id),
  target_expires   date,
  used_on          date,
  used_qty         text not null default '',
  destroyed_reason text,
  deviation_id     text,
  files            jsonb not null default '[]'::jsonb,
  notes            text not null default '',
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_rework_number on hx_rework(license_id, number);

create or replace function hx_rework_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then raise exception 'Rework records are never deleted. Destroy the rework with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_rework', new.license_id, 'RW');
    new.created_by := v_me; new.created_at := now(); new.status := 'identified';
    new.inspection_result := ''; new.approved_by := ''; new.approved_at := null; new.target_batch_id := null; new.used_on := null; new.destroyed_reason := null;
    if new.source_kind = 'batch' and new.source_batch_id is null then raise exception 'Choose the batch the rework comes from.'; end if;
    if new.source_kind = 'hold' and new.source_hold_id is null then raise exception 'Choose the hold the rework comes from.'; end if;
    if new.source_batch_id is not null and not exists (select 1 from hx_batches where id = new.source_batch_id and license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
    if new.identified_on > current_date then raise exception 'The date cannot be in the future.'; end if;
    perform set_config('hx.reason', 'Rework identified', true);
    new.updated_at := now();
    return new;
  end if;
  new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  if old.status in ('used','destroyed') and (to_jsonb(new) - 'files' - 'notes' - 'deviation_id' - 'updated_at') is distinct from (to_jsonb(old) - 'files' - 'notes' - 'deviation_id' - 'updated_at') then
    raise exception 'This rework is closed (%).', old.status;
  end if;
  if new.status = 'destroyed' and old.status <> 'destroyed' then
    if not hx_can('rework', 3, new.license_id) then raise exception 'Only Full access can destroy rework.'; end if;
    if coalesce(trim(new.destroyed_reason), '') = '' then raise exception 'Give a reason and how it was destroyed (waste log / METRC).'; end if;
    perform set_config('hx.reason', 'Rework destroyed: ' || trim(new.destroyed_reason), true);
  elsif new.status = 'inspected' and old.status = 'identified' then
    if coalesce(trim(new.inspection), '') = '' or new.inspection_result = '' then raise exception 'Record the inspection and its result (pass or fail).'; end if;
    if coalesce(trim(new.analysis), '') = '' then raise exception 'Record the analysis (test results / COA) before release.'; end if;
    if new.inspected_on is null then new.inspected_on := current_date; end if;
    if coalesce(trim(new.inspected_by), '') = '' then new.inspected_by := v_me; end if;
    perform set_config('hx.reason', 'Rework inspected: ' || new.inspection_result, true);
  elsif new.status = 'approved' and old.status = 'inspected' then
    if not hx_can('rework', 3, new.license_id) then raise exception 'Only Full access (qualified person) can approve rework.'; end if;
    if old.inspection_result <> 'pass' then raise exception 'Rework that failed inspection cannot be approved. Destroy it.'; end if;
    if not new.like_to_like then raise exception 'Confirm the rework goes into the same product (like-to-like).'; end if;
    if new.expires_on is null then raise exception 'Enter the rework expiry date.'; end if;
    new.approved_by := v_me; new.approved_at := now();
    perform set_config('hx.reason', 'Rework approved for use', true);
  elsif new.status = 'used' and old.status = 'approved' then
    if new.target_batch_id is null then raise exception 'Choose the batch the rework went into.'; end if;
    if not exists (select 1 from hx_batches where id = new.target_batch_id and license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
    if new.used_on is null then new.used_on := current_date; end if;
    if new.target_expires is not null and old.expires_on is not null and old.expires_on < new.target_expires then
      raise exception 'The rework expires (%) before the finished product (%). It cannot be used in this batch.', old.expires_on, new.target_expires;
    end if;
    perform set_config('hx.reason', 'Rework used in a batch', true);
  elsif new.status <> old.status then
    raise exception 'Rework goes identified -> inspected -> approved -> used (or destroyed).';
  else
    -- details may be corrected before inspection; approval and use facts stay as recorded
    if old.status <> 'identified' and (new.material, new.quantity, new.source_batch_id, new.source_hold_id, new.identified_on, new.inspection, new.analysis, new.inspection_result)
         is distinct from (old.material, old.quantity, old.source_batch_id, old.source_hold_id, old.identified_on, old.inspection, old.analysis, old.inspection_result) then
      raise exception 'After inspection the rework details cannot be changed.';
    end if;
    new.approved_by := old.approved_by; new.approved_at := old.approved_at;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_rework_guard on hx_rework;
create trigger hx_rework_guard before insert or update or delete on hx_rework for each row execute function hx_rework_guard();
drop trigger if exists hx_rework_place on hx_rework;
create trigger hx_rework_place before insert or update on hx_rework for each row execute function hx_fl_guard();
drop trigger if exists hx_rework_audit on hx_rework;
create trigger hx_rework_audit after insert or update on hx_rework for each row execute function hx_audit();

-- deviations can be raised from a line clearance, a rework or a piece of equipment
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment'));

alter table hx_line_clearances enable row level security;
alter table hx_rework enable row level security;
drop policy if exists hx_line_clearances_read on hx_line_clearances;
drop policy if exists hx_line_clearances_insert on hx_line_clearances;
drop policy if exists hx_line_clearances_update on hx_line_clearances;
create policy hx_line_clearances_read   on hx_line_clearances for select to authenticated using (hx_can('lineclear',1,license_id));
create policy hx_line_clearances_insert on hx_line_clearances for insert to authenticated with check (hx_can('lineclear',2,license_id));
create policy hx_line_clearances_update on hx_line_clearances for update to authenticated using (hx_can('lineclear',2,license_id)) with check (hx_can('lineclear',2,license_id));
drop policy if exists hx_rework_read on hx_rework;
drop policy if exists hx_rework_insert on hx_rework;
drop policy if exists hx_rework_update on hx_rework;
create policy hx_rework_read   on hx_rework for select to authenticated using (hx_can('rework',1,license_id));
create policy hx_rework_insert on hx_rework for insert to authenticated with check (hx_can('rework',2,license_id));
create policy hx_rework_update on hx_rework for update to authenticated using (hx_can('rework',2,license_id)) with check (hx_can('rework',2,license_id));
grant select, insert, update on hx_line_clearances, hx_rework to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step26.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 26: Facility tests (air, water, soil, gases, swabs)
-- CSQ 2A.6 air, 2A.7 water (+ backflow), 2A.3 sanitation verification,
-- 3A.1.1 / 3A.1.9 / 3A.1.10 / 3A.1.12 cultivation air, soil and irrigation
-- water, 3B.1.3 / 3B.1.5 / 3B.1.7 / 3B.1.11 extraction water, gases and air,
-- 3C.1.5 manufacturing water.
--   * test points per license: what is tested (air, incoming water, process
--     water / ice, irrigation water, wastewater, soil / media, process gas,
--     surface swabs, backflow device), where, what for (analytes), limits,
--     how often, whether an ISO/IEC 17025 accredited lab is required
--   * results: sampled date and by whom, lab and accreditation, report file,
--     pass / fail, values; a failed result needs the corrective action and
--     can raise a deviation; next due date from the frequency
--   * results are never deleted (void with a reason, Full access)
-- Access module 'envtests': View / Edit (record results, add points) /
--   Full (void results, switch points off).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-25.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_env_points (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  name           text not null check (length(trim(name)) > 0),
  kind           text not null default 'water' check (kind in ('air','water','process_water','irrigation_water','wastewater','soil','process_gas','surface','backflow')),
  location       text not null default '',
  source         text not null default '',
  analytes       text not null default '',
  limits         text not null default '',
  frequency_days int not null default 365 check (frequency_days > 0),
  lab_required   boolean not null default true,
  active         boolean not null default true,
  sort           int not null default 0,
  notes          text not null default '',
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create index if not exists hx_env_points_lic on hx_env_points(license_id);

create table if not exists hx_env_tests (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  point_id       text not null references hx_env_points(id),
  sampled_on     date not null,
  sampled_by     text not null default '',
  lab_name       text not null default '',
  lab_accredited boolean not null default false,
  report_number  text not null default '',
  result         text not null check (result in ('pass','fail')),
  values_text    text not null default '',
  corrective     text not null default '',
  deviation_id   text,
  files          jsonb not null default '[]'::jsonb,
  recorded_by    text not null default '',
  created_at     timestamptz not null default now(),
  voided         boolean not null default false,
  void_reason    text,
  voided_at      timestamptz
);
create index if not exists hx_env_tests_point on hx_env_tests(point_id, sampled_on desc);

create or replace function hx_env_point_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_env_tests where point_id = old.id) then raise exception 'This test point has results. Switch it off instead of deleting it.'; end if;
    return old;
  end if;
  if tg_op = 'UPDATE' and old.active and not new.active and not hx_can('envtests', 3, new.license_id) then
    raise exception 'Only Full access can switch a test point off.';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_env_points_guard on hx_env_points;
create trigger hx_env_points_guard before insert or update or delete on hx_env_points for each row execute function hx_env_point_guard();
drop trigger if exists hx_env_points_place on hx_env_points;
create trigger hx_env_points_place before insert or update on hx_env_points for each row execute function hx_fl_guard();
drop trigger if exists hx_env_points_audit on hx_env_points;
create trigger hx_env_points_audit after insert or update or delete on hx_env_points for each row execute function hx_audit();

create or replace function hx_env_test_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record;
begin
  if tg_op = 'DELETE' then raise exception 'Test results are never deleted. Void the result with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This result is void.'; end if;
    if new.voided then
      if not hx_can('envtests', 3, old.license_id) then raise exception 'Only Full access can void a test result.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a test result.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a result without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'files' - 'deviation_id') is distinct from (to_jsonb(old) - 'files' - 'deviation_id') then
      raise exception 'A test result cannot be changed. Void it and record it again.';
    end if;
    return new;
  end if;
  select * into p from hx_env_points where id = new.point_id;
  if p.id is null or p.license_id <> new.license_id then raise exception 'That test point belongs to another license.'; end if;
  if new.sampled_on > current_date then raise exception 'The sample date cannot be in the future.'; end if;
  if p.lab_required then
    if coalesce(trim(new.lab_name), '') = '' then raise exception 'Enter the lab that tested the sample.'; end if;
    if not new.lab_accredited then raise exception 'This test must be done by an ISO/IEC 17025 accredited lab. Confirm the lab is accredited.'; end if;
  end if;
  if jsonb_array_length(new.files) = 0 and coalesce(trim(new.values_text), '') = '' then raise exception 'Attach the report or enter the results.'; end if;
  if new.result = 'fail' and coalesce(trim(new.corrective), '') = '' then raise exception 'A failed result needs the corrective action.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  perform set_config('hx.reason', 'Facility test ' || new.result || ': ' || p.name, true);
  return new;
end $$;
drop trigger if exists hx_env_tests_guard on hx_env_tests;
create trigger hx_env_tests_guard before insert or update or delete on hx_env_tests for each row execute function hx_env_test_guard();
drop trigger if exists hx_env_tests_place on hx_env_tests;
create trigger hx_env_tests_place before insert or update on hx_env_tests for each row execute function hx_fl_guard();
drop trigger if exists hx_env_tests_audit on hx_env_tests;
create trigger hx_env_tests_audit after insert or update on hx_env_tests for each row execute function hx_audit();

-- deviations can be raised from a failed facility test
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment','facility_test'));

alter table hx_env_points enable row level security;
alter table hx_env_tests enable row level security;
drop policy if exists hx_env_points_read on hx_env_points;
drop policy if exists hx_env_points_insert on hx_env_points;
drop policy if exists hx_env_points_update on hx_env_points;
drop policy if exists hx_env_points_delete on hx_env_points;
create policy hx_env_points_read   on hx_env_points for select to authenticated using (hx_can('envtests',1,license_id));
create policy hx_env_points_insert on hx_env_points for insert to authenticated with check (hx_can('envtests',2,license_id));
create policy hx_env_points_update on hx_env_points for update to authenticated using (hx_can('envtests',2,license_id)) with check (hx_can('envtests',2,license_id));
create policy hx_env_points_delete on hx_env_points for delete to authenticated using (hx_can('envtests',3,license_id));
drop policy if exists hx_env_tests_read on hx_env_tests;
drop policy if exists hx_env_tests_insert on hx_env_tests;
drop policy if exists hx_env_tests_update on hx_env_tests;
create policy hx_env_tests_read   on hx_env_tests for select to authenticated using (hx_can('envtests',1,license_id));
create policy hx_env_tests_insert on hx_env_tests for insert to authenticated with check (hx_can('envtests',2,license_id));
create policy hx_env_tests_update on hx_env_tests for update to authenticated using (hx_can('envtests',2,license_id)) with check (hx_can('envtests',2,license_id));
grant select, insert, update, delete on hx_env_points to authenticated;
grant select, insert, update on hx_env_tests to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step27.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 27: Cultivation records (CUL licenses)
-- CSQ Standard for Cultivation, Module 3A (3A.1.1-3A.1.3, 3A.1.5, 3A.1.7,
-- 3A.1.8, 3A.1.12-3A.1.16):
--   * grow areas: rooms, greenhouses and fields (type, canopy, irrigation
--     system, water source; outdoor land-use history and a risk assessment
--     re-evaluated every year)
--   * plant batches PB-YYYY-###: cultivar, source (received clone / seed lot,
--     own mother batch), planting date, plant count, grow media lot, METRC
--     tag, area and stage (propagation, vegetative, flowering, drying,
--     curing, done, destroyed)
--   * grow records per plant batch: nutrient / fertilizer / amendment
--     applications (approved chemical or received lot), crop protection
--     applications (approved pesticide with EPA number, rate, applicator,
--     re-entry and pre-harvest intervals), scouting, stage / area moves,
--     harvest (wet weight, harvest tag), drying and curing (dry weight,
--     room conditions), destruction
--   * harvest is refused before the pre-harvest interval of every crop
--     protection application has passed
-- Access module 'cultivation': View / Edit (record) / Full (void records,
--   destroy plant batches, switch areas off).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-26.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_grow_areas (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  name           text not null check (length(trim(name)) > 0),
  kind           text not null default 'indoor' check (kind in ('indoor','greenhouse','outdoor','mother','propagation','dry','cure','trim')),
  canopy_sqft    numeric,
  irrigation     text not null default '',
  water_source   text not null default '',
  limits         text not null default '',
  land_use       text not null default '',
  risk_assessed_on date,
  risk_notes     text not null default '',
  active         boolean not null default true,
  sort           int not null default 0,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

create table if not exists hx_plant_batches (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  number         text not null default '',
  cultivar       text not null check (length(trim(cultivar)) > 0),
  source_kind    text not null default 'lot' check (source_kind in ('lot','mother','seed_own')),
  source_lot_id  text references hx_lots(id),
  mother_batch_id text references hx_plant_batches(id),
  source_note    text not null default '',
  planted_on     date not null default current_date,
  plant_count    int not null check (plant_count > 0),
  media_lot_id   text references hx_lots(id),
  media          text not null default '',
  metrc_tag      text not null default '',
  area_id        text references hx_grow_areas(id),
  stage          text not null default 'propagation' check (stage in ('propagation','vegetative','flowering','drying','curing','done','destroyed')),
  harvest_after  date,
  wet_weight     numeric,
  dry_weight     numeric,
  harvest_tag    text not null default '',
  notes          text not null default '',
  created_by     text not null default '',
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create unique index if not exists hx_plant_batches_number on hx_plant_batches(license_id, number);

create table if not exists hx_grow_events (
  id             text primary key,
  state_id       text not null references hx_states(id),
  license_id     text not null references hx_licenses(id),
  batch_id       text not null references hx_plant_batches(id),
  kind           text not null check (kind in ('input','crop_protection','scouting','stage','harvest','dry','cure','destroy','note')),
  done_on        date not null default current_date,
  done_by        text not null default '',
  area_id        text references hx_grow_areas(id),
  chemical_id    text references hx_chemicals(id),
  lot_id         text references hx_lots(id),
  product        text not null default '',
  epa_reg        text not null default '',
  amount         text not null default '',
  method         text not null default '',
  rei_hours      int,
  phi_days       int,
  stage          text not null default '',
  observations   text not null default '',
  wet_weight     numeric,
  dry_weight     numeric,
  waste_weight   numeric,
  tag            text not null default '',
  conditions     text not null default '',
  files          jsonb not null default '[]'::jsonb,
  recorded_by    text not null default '',
  created_at     timestamptz not null default now(),
  voided         boolean not null default false,
  void_reason    text,
  voided_at      timestamptz
);
create index if not exists hx_grow_events_batch on hx_grow_events(batch_id, done_on desc);

create or replace function hx_cultivation_lic(p_lic text) returns void
language plpgsql security definer set search_path = public as $$
declare v_op text;
begin
  select coalesce(nullif(operation,''), hx_license_op(license_number, license_type)) into v_op from hx_licenses where id = p_lic;
  if v_op <> 'cultivation' then raise exception 'Cultivation records are only for cultivation (CUL) licenses.'; end if;
end $$;

create or replace function hx_grow_area_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    if exists (select 1 from hx_plant_batches where area_id = old.id) or exists (select 1 from hx_grow_events where area_id = old.id) then raise exception 'This area has grow records. Switch it off instead of deleting it.'; end if;
    return old;
  end if;
  perform hx_cultivation_lic(new.license_id);
  if new.kind = 'outdoor' and new.risk_assessed_on is not null and coalesce(trim(new.risk_notes), '') = '' then raise exception 'Describe the site risk assessment (land use, neighboring land, animals, controls).'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_grow_areas_guard on hx_grow_areas;
create trigger hx_grow_areas_guard before insert or update or delete on hx_grow_areas for each row execute function hx_grow_area_guard();
drop trigger if exists hx_grow_areas_place on hx_grow_areas;
create trigger hx_grow_areas_place before insert or update on hx_grow_areas for each row execute function hx_fl_guard();
drop trigger if exists hx_grow_areas_audit on hx_grow_areas;
create trigger hx_grow_areas_audit after insert or update or delete on hx_grow_areas for each row execute function hx_audit();

create or replace function hx_plant_batch_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Plant batches are never deleted. Destroy the batch with a reason.'; end if;
  if tg_op = 'INSERT' then
    perform hx_cultivation_lic(new.license_id);
    new.number := hx_next_number('hx_plant_batches', new.license_id, 'PB');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.stage := coalesce(nullif(new.stage, ''), 'propagation');
    if new.stage not in ('propagation','vegetative','flowering') then new.stage := 'propagation'; end if;
    new.harvest_after := null; new.wet_weight := null; new.dry_weight := null; new.harvest_tag := '';
    if new.source_kind = 'lot' and new.source_lot_id is null then raise exception 'Choose the received clone / seed lot (Receiving), or the mother plant batch.'; end if;
    if new.source_kind = 'mother' and new.mother_batch_id is null then raise exception 'Choose the mother plant batch.'; end if;
    if new.source_lot_id is not null and not exists (select 1 from hx_lots where id = new.source_lot_id and license_id = new.license_id and status = 'accepted') then
      raise exception 'Propagation material must come from an accepted lot of this license.';
    end if;
    if new.planted_on > current_date then raise exception 'The planting date cannot be in the future.'; end if;
    perform set_config('hx.reason', 'Plant batch started', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if coalesce(current_setting('hx.internal', true), '') <> 'on' then
      if (new.stage, new.area_id, new.harvest_after, new.wet_weight, new.dry_weight, new.harvest_tag) is distinct from (old.stage, old.area_id, old.harvest_after, old.wet_weight, old.dry_weight, old.harvest_tag) then
        raise exception 'Stage, area, harvest and weights change through the grow records.';
      end if;
      if old.stage in ('done','destroyed') then raise exception 'This plant batch is closed.'; end if;
    end if;
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_plant_batches_guard on hx_plant_batches;
create trigger hx_plant_batches_guard before insert or update or delete on hx_plant_batches for each row execute function hx_plant_batch_guard();
drop trigger if exists hx_plant_batches_place on hx_plant_batches;
create trigger hx_plant_batches_place before insert or update on hx_plant_batches for each row execute function hx_fl_guard();
drop trigger if exists hx_plant_batches_audit on hx_plant_batches;
create trigger hx_plant_batches_audit after insert or update on hx_plant_batches for each row execute function hx_audit();

create or replace function hx_grow_event_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare b record; c record; v_phi date;
begin
  if tg_op = 'DELETE' then raise exception 'Grow records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('cultivation', 3, old.license_id) then raise exception 'Only Full access can void a grow record.'; end if;
      if old.kind in ('harvest','dry','cure','destroy','stage') then raise exception 'Stage, harvest, drying, curing and destruction records cannot be voided. Record a correction note instead.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a record without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'files') is distinct from (to_jsonb(old) - 'files') then raise exception 'A grow record cannot be changed. Void it and record it again.'; end if;
    return new;
  end if;
  select * into b from hx_plant_batches where id = new.batch_id;
  if b.id is null or b.license_id <> new.license_id then raise exception 'That plant batch belongs to another license.'; end if;
  if b.stage in ('done','destroyed') and new.kind <> 'note' then raise exception 'This plant batch is closed (%).', b.stage; end if;
  if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
  if new.done_on < b.planted_on then raise exception 'The date is before the batch was planted.'; end if;
  if coalesce(trim(new.done_by), '') = '' then raise exception 'Enter who did it.'; end if;
  if new.chemical_id is not null then
    select * into c from hx_chemicals where id = new.chemical_id;
    if c.license_id <> new.license_id or c.status <> 'approved' then raise exception 'Only chemicals approved in the Chemical register can be applied.'; end if;
    if coalesce(trim(new.product), '') = '' then new.product := c.name; end if;
    if coalesce(trim(new.epa_reg), '') = '' then new.epa_reg := c.epa_reg; end if;
  end if;
  if new.lot_id is not null and not exists (select 1 from hx_lots where id = new.lot_id and license_id = new.license_id and status = 'accepted') then
    raise exception 'Inputs must come from an accepted lot of this license.';
  end if;
  if new.kind = 'input' then
    if new.chemical_id is null and new.lot_id is null then raise exception 'Choose the approved nutrient / amendment (Chemical register) or the received lot.'; end if;
    if coalesce(trim(new.amount), '') = '' then raise exception 'Enter the amount or rate applied.'; end if;
  elsif new.kind = 'crop_protection' then
    if new.chemical_id is null or c.purpose <> 'Pesticide / crop protection' then raise exception 'Crop protection must use a pesticide approved in the Chemical register.'; end if;
    if coalesce(trim(new.amount), '') = '' then raise exception 'Enter the rate applied (as on the label).'; end if;
    if new.phi_days is null or new.rei_hours is null then raise exception 'Enter the re-entry interval (hours) and the pre-harvest interval (days) from the label.'; end if;
  elsif new.kind = 'scouting' then
    if coalesce(trim(new.observations), '') = '' then raise exception 'Record what was seen (pests, disease, plant health).'; end if;
  elsif new.kind = 'stage' then
    if new.stage not in ('vegetative','flowering') and new.area_id is null then raise exception 'Choose the new stage or area.'; end if;
  elsif new.kind = 'harvest' then
    if b.stage not in ('vegetative','flowering') then raise exception 'Only a growing batch can be harvested.'; end if;
    if new.wet_weight is null or new.wet_weight <= 0 then raise exception 'Enter the wet weight.'; end if;
    if coalesce(trim(new.tag), '') = '' then raise exception 'Enter the harvest batch tag (METRC).'; end if;
    select max(done_on + phi_days) into v_phi from hx_grow_events where batch_id = new.batch_id and kind = 'crop_protection' and not voided and phi_days is not null;
    if v_phi is not null and new.done_on < v_phi then raise exception 'Too early to harvest: the pre-harvest interval of a crop protection application ends on %.', v_phi; end if;
  elsif new.kind = 'dry' then
    if b.stage not in ('drying','curing') then raise exception 'Record the harvest first.'; end if;
    if coalesce(trim(new.conditions), '') = '' then raise exception 'Record the drying room conditions (temperature, humidity).'; end if;
  elsif new.kind = 'cure' then
    if b.stage not in ('drying','curing') then raise exception 'Record the harvest first.'; end if;
    if new.dry_weight is null or new.dry_weight <= 0 then raise exception 'Enter the final dry weight.'; end if;
  elsif new.kind = 'destroy' then
    if not hx_can('cultivation', 3, new.license_id) then raise exception 'Only Full access can destroy a plant batch.'; end if;
    if coalesce(trim(new.observations), '') = '' then raise exception 'Give the reason and how it was destroyed (waste log / METRC).'; end if;
  end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  return new;
end $$;
drop trigger if exists hx_grow_events_guard on hx_grow_events;
create trigger hx_grow_events_guard before insert or update or delete on hx_grow_events for each row execute function hx_grow_event_guard();
drop trigger if exists hx_grow_events_place on hx_grow_events;
create trigger hx_grow_events_place before insert or update on hx_grow_events for each row execute function hx_fl_guard();
drop trigger if exists hx_grow_events_audit on hx_grow_events;
create trigger hx_grow_events_audit after insert or update on hx_grow_events for each row execute function hx_audit();

-- the plant batch follows its records: stage, area, earliest harvest, weights
create or replace function hx_grow_event_apply() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_why text;
begin
  v_why := case new.kind when 'input' then 'Nutrient applied' when 'crop_protection' then 'Crop protection applied' when 'stage' then 'Moved' when 'harvest' then 'Harvested'
    when 'dry' then 'Drying recorded' when 'cure' then 'Cured, dry weight recorded' when 'destroy' then 'Destroyed: ' || new.observations else 'Grow record' end || case when new.voided then ' (voided)' else '' end;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', v_why, true);
  update hx_plant_batches set harvest_after = (select max(done_on + phi_days) from hx_grow_events where batch_id = new.batch_id and kind = 'crop_protection' and not voided and phi_days is not null)
   where id = new.batch_id;
  if tg_op = 'INSERT' then
    perform set_config('hx.reason', v_why, true);
    if new.kind = 'stage' then
      update hx_plant_batches set stage = case when new.stage in ('vegetative','flowering') then new.stage else stage end, area_id = coalesce(new.area_id, area_id) where id = new.batch_id;
    elsif new.kind = 'harvest' then
      update hx_plant_batches set stage = 'drying', wet_weight = new.wet_weight, harvest_tag = new.tag, area_id = coalesce(new.area_id, area_id) where id = new.batch_id;
    elsif new.kind = 'dry' then
      update hx_plant_batches set stage = 'curing', area_id = coalesce(new.area_id, area_id) where id = new.batch_id;
    elsif new.kind = 'cure' then
      update hx_plant_batches set stage = 'done', dry_weight = new.dry_weight where id = new.batch_id;
    elsif new.kind = 'destroy' then
      update hx_plant_batches set stage = 'destroyed' where id = new.batch_id;
    end if;
  end if;
  perform set_config('hx.internal', '', true);
  return null;
end $$;
drop trigger if exists hx_grow_events_zapply on hx_grow_events;
create trigger hx_grow_events_zapply after insert or update on hx_grow_events for each row execute function hx_grow_event_apply();

alter table hx_grow_areas enable row level security;
alter table hx_plant_batches enable row level security;
alter table hx_grow_events enable row level security;
do $$ declare t text; begin
  foreach t in array array['hx_grow_areas','hx_plant_batches','hx_grow_events'] loop
    execute format('drop policy if exists %I on %I', t||'_read', t);
    execute format('drop policy if exists %I on %I', t||'_insert', t);
    execute format('drop policy if exists %I on %I', t||'_update', t);
    execute format('create policy %I on %I for select to authenticated using (hx_can(''cultivation'',1,license_id))', t||'_read', t);
    execute format('create policy %I on %I for insert to authenticated with check (hx_can(''cultivation'',2,license_id))', t||'_insert', t);
    execute format('create policy %I on %I for update to authenticated using (hx_can(''cultivation'',2,license_id)) with check (hx_can(''cultivation'',2,license_id))', t||'_update', t);
  end loop;
end $$;
drop policy if exists hx_grow_areas_delete on hx_grow_areas;
create policy hx_grow_areas_delete on hx_grow_areas for delete to authenticated using (hx_can('cultivation',3,license_id));
grant select, insert, update, delete on hx_grow_areas to authenticated;
grant select, insert, update on hx_plant_batches, hx_grow_events to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step28.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 28: HACCP (CSQ Module 4A, Level 2)
-- The 12 Codex steps, kept live per license:
--   * HACCP team (4A.2): members, role, department; one person and a backup
--     certified (International HACCP Alliance) - certificates come from the
--     Training records (HACCP course) or are attached here
--   * HACCP plans per product / process (4A.1, 4A.3-4A.7): product description
--     (name, safety characteristics, ingredients, allergens, packaging,
--     intended use, target market, shelf life, labeling, storage /
--     distribution), the process flow (inputs, steps, rework, outsourced,
--     end products, waste) with the CCPs marked, the hazard analysis for
--     every step (biological, chemical, physical, allergen: cause, control,
--     significant or not), and the CCPs with critical limits, monitoring,
--     corrective action and verification
--   * a plan becomes active only when it is complete and validated (4A.10),
--     approved by Full access; revising it starts a new version
--   * CCP monitoring records (4A.8, 4A.9): value, within limits or not; a
--     deviation needs the corrective action and what happened to the product;
--     records reviewed (verified) by a second person
--   * verification (4A.11): records review, yearly reanalysis, validation,
--     calibration checks - with findings and files
-- Access module 'haccp': View / Edit (monitoring, drafts, verification) /
--   Full (validate, activate, retire plans, void records).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-27.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_haccp_team (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  name          text not null check (length(trim(name)) > 0),
  user_id       text,
  role          text not null default 'Member' check (role in ('Team leader','Backup','Member')),
  department    text not null default '',
  certified     boolean not null default false,
  cert_provider text not null default '',
  cert_date     date,
  cert_files    jsonb not null default '[]'::jsonb,
  active        boolean not null default true,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table if not exists hx_haccp_plans (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  number          text not null default '',
  name            text not null check (length(trim(name)) > 0),
  batch_types     text[] not null default '{}',
  description     jsonb not null default '{}'::jsonb,
  flow            jsonb not null default '[]'::jsonb,
  hazards         jsonb not null default '[]'::jsonb,
  ccps            jsonb not null default '[]'::jsonb,
  status          text not null default 'draft' check (status in ('draft','validated','active','retired')),
  version         int not null default 0,
  validated_on    date,
  validation      text not null default '',
  validation_files jsonb not null default '[]'::jsonb,
  validated_by    text not null default '',
  approved_by     text not null default '',
  approved_at     timestamptz,
  flow_reviewed_on date,
  retired_reason  text,
  created_by      text not null default '',
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_haccp_plans_number on hx_haccp_plans(license_id, number);

create table if not exists hx_haccp_monitoring (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  plan_id       text not null references hx_haccp_plans(id),
  plan_version  int not null default 0,
  ccp_id        text not null,
  ccp_name      text not null default '',
  batch_id      text references hx_batches(id),
  checked_at    timestamptz not null default now(),
  checked_by    text not null default '',
  value         text not null default '',
  within_limits boolean not null,
  corrective    text not null default '',
  disposition   text not null default '' check (disposition in ('','held','reworked','destroyed','released_after_evaluation')),
  deviation_id  text,
  verified_by   text not null default '',
  verified_at   timestamptz,
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_haccp_monitoring_plan on hx_haccp_monitoring(plan_id, checked_at desc);
create index if not exists hx_haccp_monitoring_batch on hx_haccp_monitoring(batch_id);

create table if not exists hx_haccp_verifications (
  id          text primary key,
  state_id    text not null references hx_states(id),
  license_id  text not null references hx_licenses(id),
  plan_id     text references hx_haccp_plans(id),
  kind        text not null check (kind in ('records_review','reanalysis','validation','calibration','other')),
  done_on     date not null default current_date,
  done_by     text not null default '',
  findings    text not null default '',
  result      text not null default 'ok' check (result in ('ok','changes_needed')),
  files       jsonb not null default '[]'::jsonb,
  recorded_by text not null default '',
  created_at  timestamptz not null default now(),
  voided      boolean not null default false,
  void_reason text,
  voided_at   timestamptz
);

-- plans: complete and validated before they go live; active plans are frozen
create or replace function hx_haccp_plan_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare st jsonb; c jsonb; h jsonb; n int; v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then
    if old.status <> 'draft' or old.version > 0 or exists (select 1 from hx_haccp_monitoring where plan_id = old.id) then
      raise exception 'Only a never-used draft can be deleted. Retire the plan instead.';
    end if;
    return old;
  end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_haccp_plans', new.license_id, 'HP');
    new.created_by := v_me; new.created_at := now(); new.status := 'draft'; new.version := 0;
    new.approved_by := ''; new.approved_at := null; new.validated_on := null; new.validated_by := '';
    new.updated_at := now();
    return new;
  end if;
  new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  if old.status in ('active','retired') and new.status = old.status
     and (new.name, new.batch_types, new.description, new.flow, new.hazards, new.ccps, new.validation, new.validation_files)
         is distinct from (old.name, old.batch_types, old.description, old.flow, old.hazards, old.ccps, old.validation, old.validation_files) then
    raise exception 'An active plan cannot be edited. Click "Revise" to start a new version.';
  end if;
  if new.status = 'retired' and old.status <> 'retired' then
    if not hx_can('haccp', 3, new.license_id) then raise exception 'Only Full access can retire a HACCP plan.'; end if;
    if coalesce(trim(new.retired_reason), '') = '' then raise exception 'Give a reason for retiring the plan.'; end if;
    perform set_config('hx.reason', 'HACCP plan retired: ' || trim(new.retired_reason), true);
  elsif new.status = 'draft' and old.status = 'active' then
    if not hx_can('haccp', 3, new.license_id) then raise exception 'Only Full access can revise an active plan.'; end if;
    new.validated_on := null; new.validated_by := ''; new.validation := ''; new.validation_files := '[]'::jsonb;
    perform set_config('hx.reason', 'HACCP plan revision started (was version ' || old.version || ')', true);
  elsif new.status in ('validated','active') and old.status not in ('validated','active') or (new.status = 'active' and old.status = 'validated') then
    if not hx_can('haccp', 3, new.license_id) then raise exception 'Only Full access can validate or activate a HACCP plan.'; end if;
    -- completeness (Codex steps 1-10)
    if coalesce(trim(new.description->>'intended_use'), '') = '' or coalesce(trim(new.description->>'ingredients'), '') = '' or coalesce(trim(new.description->>'allergens'), '') = ''
       or coalesce(trim(new.description->>'packaging'), '') = '' or coalesce(trim(new.description->>'storage'), '') = '' then
      raise exception 'Complete the product description (ingredients, allergens, packaging, intended use, storage and distribution).';
    end if;
    if jsonb_array_length(new.flow) < 2 then raise exception 'Draw the process flow (at least the inputs and the steps).'; end if;
    for st in select * from jsonb_array_elements(new.flow) loop
      if coalesce((st->>'nohazard')::boolean, false) is not true and not exists (select 1 from jsonb_array_elements(new.hazards) x where x->>'step' = st->>'id') then
        raise exception 'Step "%" has no hazard analysis. Add its hazards or mark it "no hazards reasonably expected".', st->>'name';
      end if;
    end loop;
    for h in select * from jsonb_array_elements(new.hazards) loop
      if coalesce(trim(h->>'control'), '') = '' then raise exception 'Hazard "%" needs its control measure.', h->>'hazard'; end if;
    end loop;
    select count(*) into n from jsonb_array_elements(new.ccps);
    if n = 0 and exists (select 1 from jsonb_array_elements(new.hazards) x where coalesce((x->>'significant')::boolean, false)) then
      raise exception 'Significant hazards need a Critical Control Point (or a documented reason they are controlled by prerequisite programs).';
    end if;
    for c in select * from jsonb_array_elements(new.ccps) loop
      if coalesce(trim(c->>'limit'), '') = '' or coalesce(trim(c->>'monitoring'), '') = '' or coalesce(trim(c->>'frequency'), '') = ''
         or coalesce(trim(c->>'corrective'), '') = '' or coalesce(trim(c->>'verification'), '') = '' then
        raise exception 'CCP "%" needs its critical limit, monitoring (what, how, frequency), corrective action and verification.', c->>'name';
      end if;
    end loop;
    if (select count(*) from hx_haccp_team where license_id = new.license_id and active and certified) < 2 then
      raise exception 'The HACCP team needs one person and a backup certified in an International HACCP Alliance course.';
    end if;
    if new.status = 'validated' or old.status <> 'validated' then
      if coalesce(trim(new.validation), '') = '' then raise exception 'Record how the control measures and critical limits were validated (studies, tests, references).'; end if;
      new.validated_on := current_date; new.validated_by := v_me;
    end if;
    if new.status = 'active' then
      new.version := old.version + 1; new.approved_by := v_me; new.approved_at := now(); new.flow_reviewed_on := current_date;
      perform set_config('hx.reason', 'HACCP plan version ' || new.version || ' activated', true);
    else
      perform set_config('hx.reason', 'HACCP plan validated', true);
    end if;
  elsif new.status <> old.status then
    raise exception 'A plan goes draft -> validated -> active (or retired).';
  end if;
  if new.status = 'draft' and old.status = 'validated' and (new.flow, new.hazards, new.ccps) is distinct from (old.flow, old.hazards, old.ccps) then
    new.validated_on := null; new.validated_by := '';
  end if;
  if old.status = 'validated' and new.status = 'validated' and (new.flow, new.hazards, new.ccps, new.description) is distinct from (old.flow, old.hazards, old.ccps, old.description) then
    new.status := 'draft'; new.validated_on := null; new.validated_by := '';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_haccp_plans_guard on hx_haccp_plans;
create trigger hx_haccp_plans_guard before insert or update or delete on hx_haccp_plans for each row execute function hx_haccp_plan_guard();

create or replace function hx_haccp_monitoring_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record; c jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Monitoring records are never deleted. Void the record with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('haccp', 3, old.license_id) then raise exception 'Only Full access can void a monitoring record.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a record without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'verified_by' - 'verified_at' - 'deviation_id') is distinct from (to_jsonb(old) - 'verified_by' - 'verified_at' - 'deviation_id') then
      raise exception 'A monitoring record cannot be changed. Void it and record it again.';
    end if;
    if new.verified_at is not null and old.verified_at is null then
      new.verified_by := coalesce(hx_me(), ''); new.verified_at := now();
      if new.verified_by = old.checked_by or new.verified_by = old.recorded_by then raise exception 'Records are verified by someone other than the person who did the check.'; end if;
      perform set_config('hx.reason', 'CCP record verified', true);
    elsif old.verified_at is not null and (new.verified_at is distinct from old.verified_at) then
      raise exception 'This record is already verified.';
    end if;
    return new;
  end if;
  select * into p from hx_haccp_plans where id = new.plan_id;
  if p.id is null or p.license_id <> new.license_id then raise exception 'That HACCP plan belongs to another license.'; end if;
  if p.status <> 'active' then raise exception 'Monitoring is recorded against an active HACCP plan.'; end if;
  select x into c from jsonb_array_elements(p.ccps) x where x->>'id' = new.ccp_id;
  if c is null then raise exception 'That CCP is not in the active plan.'; end if;
  if new.batch_id is not null and not exists (select 1 from hx_batches where id = new.batch_id and license_id = new.license_id) then raise exception 'That batch belongs to another license.'; end if;
  if coalesce(trim(new.checked_by), '') = '' then raise exception 'Enter who did the check.'; end if;
  if coalesce(trim(new.value), '') = '' then raise exception 'Enter the measured value.'; end if;
  if not new.within_limits then
    if coalesce(trim(new.corrective), '') = '' then raise exception 'Out of the critical limit: record the corrective action.'; end if;
    if new.disposition = '' then raise exception 'Out of the critical limit: record what happened to the product (held, reworked, destroyed, released after evaluation).'; end if;
  end if;
  new.plan_version := p.version; new.ccp_name := coalesce(c->>'name', '');
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.verified_by := ''; new.verified_at := null;
  new.voided := false; new.void_reason := null; new.voided_at := null;
  perform set_config('hx.reason', case when new.within_limits then 'CCP within limits' else 'CCP OUT of limits' end, true);
  return new;
end $$;
drop trigger if exists hx_haccp_monitoring_guard on hx_haccp_monitoring;
create trigger hx_haccp_monitoring_guard before insert or update or delete on hx_haccp_monitoring for each row execute function hx_haccp_monitoring_guard();

create or replace function hx_haccp_verification_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Verification records are never deleted. Void it with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('haccp', 3, old.license_id) then raise exception 'Only Full access can void a verification record.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
      return new;
    end if;
    if (to_jsonb(new) - 'files') is distinct from (to_jsonb(old) - 'files') then raise exception 'A verification record cannot be changed. Void it and record it again.'; end if;
    return new;
  end if;
  if new.plan_id is not null and not exists (select 1 from hx_haccp_plans where id = new.plan_id and license_id = new.license_id) then raise exception 'That plan belongs to another license.'; end if;
  if coalesce(trim(new.done_by), '') = '' then raise exception 'Enter who did the verification.'; end if;
  if coalesce(trim(new.findings), '') = '' then raise exception 'Record what was checked and found.'; end if;
  if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  if new.kind = 'reanalysis' and new.plan_id is not null then
    perform set_config('hx.internal', 'on', true);
    update hx_haccp_plans set flow_reviewed_on = new.done_on where id = new.plan_id;
    perform set_config('hx.internal', '', true);
  end if;
  return new;
end $$;
drop trigger if exists hx_haccp_verifications_guard on hx_haccp_verifications;
create trigger hx_haccp_verifications_guard before insert or update or delete on hx_haccp_verifications for each row execute function hx_haccp_verification_guard();

do $$ declare t text; begin
  foreach t in array array['hx_haccp_team','hx_haccp_plans','hx_haccp_monitoring','hx_haccp_verifications'] loop
    execute format('drop trigger if exists %I on %I', t||'_place', t);
    execute format('create trigger %I before insert or update on %I for each row execute function hx_fl_guard()', t||'_place', t);
    execute format('drop trigger if exists %I on %I', t||'_audit', t);
    execute format('create trigger %I after insert or update or delete on %I for each row execute function hx_audit()', t||'_audit', t);
    execute format('alter table %I enable row level security', t);
    execute format('drop policy if exists %I on %I', t||'_read', t);
    execute format('drop policy if exists %I on %I', t||'_insert', t);
    execute format('drop policy if exists %I on %I', t||'_update', t);
    execute format('drop policy if exists %I on %I', t||'_delete', t);
    execute format('create policy %I on %I for select to authenticated using (hx_can(''haccp'',1,license_id))', t||'_read', t);
    execute format('create policy %I on %I for insert to authenticated with check (hx_can(''haccp'',2,license_id))', t||'_insert', t);
    execute format('create policy %I on %I for update to authenticated using (hx_can(''haccp'',2,license_id)) with check (hx_can(''haccp'',2,license_id))', t||'_update', t);
    execute format('create policy %I on %I for delete to authenticated using (hx_can(''haccp'',3,license_id))', t||'_delete', t);
  end loop;
end $$;
grant select, insert, update, delete on hx_haccp_team, hx_haccp_plans to authenticated;
grant select, insert, update on hx_haccp_monitoring, hx_haccp_verifications to authenticated;

-- the team table: Full access manages it
create or replace function hx_haccp_team_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if not hx_can('haccp', 3, coalesce(new.license_id, old.license_id)) then raise exception 'Only Full access can change the HACCP team.'; end if;
  if tg_op = 'DELETE' then return old; end if;
  if new.certified and new.cert_date is null and jsonb_array_length(new.cert_files) = 0 and coalesce(trim(new.cert_provider), '') = '' then
    raise exception 'Enter the certificate (provider, date or file) for a certified member.';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_haccp_team_guard on hx_haccp_team;
create trigger hx_haccp_team_guard before insert or update or delete on hx_haccp_team for each row execute function hx_haccp_team_guard();

-- deviations can be raised from a CCP out of limits
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment','facility_test','haccp'));

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step29.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 29: Risk register and Change control (CSQ Level 3)
-- Risk register (CSQ 5.1.6; also 1.9 product defense threat assessment,
-- 1.10 fraud vulnerability, 2A.12.7 allergens, 3A.1.2 outdoor site risk):
--   * numbered RK-###; the hazard, its root cause, the owner, the inherent
--     rating (likelihood x severity, 1-5 each), existing controls, the
--     immediate action and the timescale (target date) for a permanent fix
--   * high and critical risks (score 10+) need an immediate action and a
--     target date before they can be saved
--   * "controlled" needs the permanent action, its verification (what, who,
--     when) and the residual rating
--   * routine surveillance: every risk is reviewed on a schedule (review
--     every N days); each review is a record (hx_risk_reviews) that updates
--     the current rating and the next review date
--   * closing a risk needs Full access and a reason; risks are never deleted
-- Change control (CSQ 5.1.5, 5.4.1; 4A.10 / 4A.11 after significant change):
--   * numbered CC-YYYY-###: type (product, process, equipment, facility,
--     material / supplier, people / organization, document / SOP,
--     regulatory, IT / system), what changes and why, the impact
--     assessment (HACCP, allergens, labels, specs, SOPs, training,
--     equipment, suppliers, testing, facility, license, customers, METRC)
--   * requested -> approved (Full access = qualified person) -> implemented
--     -> closed (effectiveness check); or rejected / cancelled with a reason
--   * implemented only when every action is done, training was given before
--     use (when required), a trial run passed (when required), the HACCP plan
--     was reviewed (when HACCP is affected) and the regulator / certification
--     body / customers were told (when required)
--   * after approval the change itself cannot be rewritten
-- Access modules 'risks' and 'changes': View / Edit (record, review,
--   request, record actions) / Full (close risks; approve, reject, close
--   changes).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-28.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_risks (
  id                  text primary key,
  state_id            text not null references hx_states(id),
  license_id          text not null references hx_licenses(id),
  number              text not null default '',
  title               text not null check (length(trim(title)) > 0),
  category            text not null default 'product_safety',
  area                text not null default '',
  hazard              text not null default '',
  root_cause          text not null default '',
  owner               text not null default '',
  source_type         text not null default '',
  source_label        text not null default '',
  likelihood          int  not null default 3 check (likelihood between 1 and 5),
  severity            int  not null default 3 check (severity between 1 and 5),
  score               int  generated always as (likelihood * severity) stored,
  controls            text not null default '',
  immediate_action    text not null default '',
  permanent_action    text not null default '',
  target_date         date,
  capa_id             text,
  residual_likelihood int check (residual_likelihood between 1 and 5),
  residual_severity   int check (residual_severity between 1 and 5),
  residual_score      int  generated always as (residual_likelihood * residual_severity) stored,
  verification        text not null default '',
  verified_by         text not null default '',
  verified_on         date,
  review_every_days   int  not null default 365 check (review_every_days between 7 and 1095),
  last_reviewed       date,
  next_review         date,
  status              text not null default 'open' check (status in ('open','controlled','closed')),
  close_reason        text,
  closed_by           text not null default '',
  closed_at           timestamptz,
  files               jsonb not null default '[]'::jsonb,
  notes               text not null default '',
  created_by          text not null default '',
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);
create unique index if not exists hx_risks_number on hx_risks(license_id, number);

create or replace function hx_risk_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_me text := coalesce(hx_me(), '');
begin
  if tg_op = 'DELETE' then raise exception 'Risks are never deleted. Close the risk with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_risks', new.license_id, 'RK');
    new.created_by := v_me; new.created_at := now(); new.status := 'open';
    new.close_reason := null; new.closed_by := ''; new.closed_at := null;
    new.residual_likelihood := null; new.residual_severity := null; new.verification := ''; new.verified_by := ''; new.verified_on := null;
    new.last_reviewed := current_date;
    perform set_config('hx.reason', 'Risk assessed', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if coalesce(current_setting('hx.internal', true), '') = 'on' then
      new.next_review := coalesce(new.last_reviewed, old.created_at::date) + new.review_every_days; new.updated_at := now(); return new;
    end if;
    if old.status = 'closed' then
      if (to_jsonb(new) - 'files' - 'notes' - 'updated_at') is distinct from (to_jsonb(old) - 'files' - 'notes' - 'updated_at') then
        raise exception 'This risk is closed.';
      end if;
      new.updated_at := now(); return new;
    end if;
    new.last_reviewed := old.last_reviewed;   -- only a review moves the review date
    if new.status = 'closed' then
      if not hx_can('risks', 3, new.license_id) then raise exception 'Only Full access can close a risk.'; end if;
      if coalesce(trim(new.close_reason), '') = '' then raise exception 'Give a reason to close the risk (for example: the process no longer exists).'; end if;
      new.closed_by := v_me; new.closed_at := now();
      perform set_config('hx.reason', 'Risk closed: ' || trim(new.close_reason), true);
    elsif new.status = 'controlled' and old.status = 'open' then
      if coalesce(trim(new.permanent_action), '') = '' then raise exception 'Record the permanent action before marking the risk controlled.'; end if;
      if coalesce(trim(new.verification), '') = '' or coalesce(trim(new.verified_by), '') = '' or new.verified_on is null then
        raise exception 'Record how the permanent action was verified, by whom and when.';
      end if;
      if new.verified_on > current_date then raise exception 'The verification date cannot be in the future.'; end if;
      if new.residual_likelihood is null or new.residual_severity is null then raise exception 'Rate the risk again with the controls in place (residual rating).'; end if;
      perform set_config('hx.reason', 'Risk controlled and verified', true);
    elsif new.status = 'open' and old.status = 'controlled' then
      perform set_config('hx.reason', 'Risk re-opened', true);
    elsif new.status <> old.status then
      raise exception 'A risk goes open -> controlled, or is closed.';
    elsif old.status = 'controlled' and (new.verification, new.verified_by, new.verified_on) is distinct from (old.verification, old.verified_by, old.verified_on) then
      raise exception 'The verification is recorded. Re-open the risk to change it.';
    end if;
  end if;
  if coalesce(trim(new.hazard), '') = '' then raise exception 'Describe the hazard (what could go wrong).'; end if;
  if coalesce(trim(new.root_cause), '') = '' then raise exception 'Enter the root cause (why it could happen).'; end if;
  if coalesce(trim(new.owner), '') = '' then raise exception 'Every risk needs an owner.'; end if;
  if new.status = 'open' and new.likelihood * new.severity >= 10 and (coalesce(trim(new.immediate_action), '') = '' or new.target_date is null) then
    raise exception 'A high or critical risk (score %) needs an immediate action and a target date for the permanent fix.', new.likelihood * new.severity;
  end if;
  new.next_review := coalesce(new.last_reviewed, current_date) + new.review_every_days;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_risks_guard on hx_risks;
create trigger hx_risks_guard before insert or update or delete on hx_risks for each row execute function hx_risk_guard();
drop trigger if exists hx_risks_place on hx_risks;
create trigger hx_risks_place before insert or update on hx_risks for each row execute function hx_fl_guard();
drop trigger if exists hx_risks_audit on hx_risks;
create trigger hx_risks_audit after insert or update on hx_risks for each row execute function hx_audit();

-- routine surveillance: each review is kept and moves the next review date
create table if not exists hx_risk_reviews (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  risk_id       text not null references hx_risks(id),
  reviewed_on   date not null default current_date,
  reviewed_by   text not null default '',
  likelihood    int  not null check (likelihood between 1 and 5),
  severity      int  not null check (severity between 1 and 5),
  effective     boolean not null default true,
  notes         text not null default '',
  recorded_by   text not null default '',
  created_at    timestamptz not null default now()
);
create index if not exists hx_risk_reviews_risk on hx_risk_reviews(risk_id);

create or replace function hx_risk_review_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare r record;
begin
  if tg_op <> 'INSERT' then raise exception 'Risk reviews cannot be changed or deleted. Record a new review.'; end if;
  select * into r from hx_risks where id = new.risk_id;
  if r.id is null or r.license_id <> new.license_id then raise exception 'That risk belongs to another license.'; end if;
  if r.status = 'closed' then raise exception 'This risk is closed.'; end if;
  if new.reviewed_on > current_date then raise exception 'The review date cannot be in the future.'; end if;
  if coalesce(trim(new.reviewed_by), '') = '' then raise exception 'Enter who reviewed the risk.'; end if;
  if not new.effective and coalesce(trim(new.notes), '') = '' then raise exception 'The controls are not effective: describe what will be done.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now();
  perform set_config('hx.reason', 'Risk reviewed', true);
  return new;
end $$;
drop trigger if exists hx_risk_reviews_guard on hx_risk_reviews;
create trigger hx_risk_reviews_guard before insert or update or delete on hx_risk_reviews for each row execute function hx_risk_review_guard();
drop trigger if exists hx_risk_reviews_place on hx_risk_reviews;
create trigger hx_risk_reviews_place before insert or update on hx_risk_reviews for each row execute function hx_fl_guard();
drop trigger if exists hx_risk_reviews_audit on hx_risk_reviews;
create trigger hx_risk_reviews_audit after insert on hx_risk_reviews for each row execute function hx_audit();

create or replace function hx_risk_review_apply() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  perform set_config('hx.reason', case when not new.effective then 'Risk review: controls not effective' else 'Risk reviewed' end, true);
  perform set_config('hx.internal', 'on', true);
  update hx_risks set
    last_reviewed = greatest(coalesce(last_reviewed, new.reviewed_on), new.reviewed_on),
    residual_likelihood = case when status = 'controlled' then new.likelihood else residual_likelihood end,
    residual_severity   = case when status = 'controlled' then new.severity   else residual_severity end,
    likelihood = case when status = 'open' then new.likelihood else likelihood end,
    severity   = case when status = 'open' then new.severity   else severity end,
    status = case when status = 'controlled' and not new.effective then 'open' else status end
  where id = new.risk_id;
  perform set_config('hx.internal', '', true);
  return null;
end $$;
drop trigger if exists hx_risk_reviews_zapply on hx_risk_reviews;
create trigger hx_risk_reviews_zapply after insert on hx_risk_reviews for each row execute function hx_risk_review_apply();

create table if not exists hx_changes (
  id                text primary key,
  state_id          text not null references hx_states(id),
  license_id        text not null references hx_licenses(id),
  number            text not null default '',
  title             text not null check (length(trim(title)) > 0),
  change_type       text not null default 'process',
  description       text not null default '',
  reason            text not null default '',
  product           text not null default '',
  requested_by      text not null default '',
  requested_on      date not null default current_date,
  impacts           jsonb not null default '{}'::jsonb,
  impact_notes      text not null default '',
  risk_level        text not null default 'medium' check (risk_level in ('low','medium','high')),
  risk_id           text references hx_risks(id),
  sop_ids           text[] not null default '{}',
  plan_ids          text[] not null default '{}',
  course_ids        text[] not null default '{}',
  actions           jsonb not null default '[]'::jsonb,
  training_required boolean not null default false,
  training_done     boolean not null default false,
  training_note     text not null default '',
  trial_required    boolean not null default false,
  trial_result      text not null default '' check (trial_result in ('','pass','fail')),
  trial_note        text not null default '',
  haccp_reviewed    boolean not null default false,
  notify            jsonb not null default '{}'::jsonb,
  notified_on       date,
  notified_note     text not null default '',
  target_date       date,
  status            text not null default 'requested' check (status in ('requested','approved','implemented','closed','rejected','cancelled')),
  approved_by       text not null default '',
  approved_at       timestamptz,
  approval_note     text not null default '',
  implemented_on    date,
  effectiveness     text not null default '',
  closed_by         text not null default '',
  closed_at         timestamptz,
  stop_reason       text,
  files             jsonb not null default '[]'::jsonb,
  notes             text not null default '',
  created_by        text not null default '',
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create unique index if not exists hx_changes_number on hx_changes(license_id, number);

create or replace function hx_change_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare v_me text := coalesce(hx_me(), ''); a jsonb; n_open int := 0; n_act int := 0;
begin
  if tg_op = 'DELETE' then raise exception 'Change records are never deleted. Cancel or reject the change with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_changes', new.license_id, 'CC');
    new.created_by := v_me; new.created_at := now(); new.status := 'requested';
    new.approved_by := ''; new.approved_at := null; new.implemented_on := null; new.effectiveness := ''; new.closed_by := ''; new.closed_at := null; new.stop_reason := null;
    if coalesce(trim(new.requested_by), '') = '' then new.requested_by := v_me; end if;
    perform set_config('hx.reason', 'Change requested', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if old.status in ('closed','rejected','cancelled') then
      if (to_jsonb(new) - 'files' - 'notes' - 'updated_at') is distinct from (to_jsonb(old) - 'files' - 'notes' - 'updated_at') then
        raise exception 'This change is %.', old.status;
      end if;
      new.updated_at := now(); return new;
    end if;
    if old.status <> 'requested' and (new.title, new.change_type, new.description, new.reason, new.product, new.impacts, new.impact_notes, new.risk_level, new.requested_by, new.requested_on)
         is distinct from (old.title, old.change_type, old.description, old.reason, old.product, old.impacts, old.impact_notes, old.risk_level, old.requested_by, old.requested_on) then
      raise exception 'The change was approved as written. Cancel it and request a new change to change what it is.';
    end if;
    if old.status <> 'requested' and (new.training_required, new.trial_required) is distinct from (old.training_required, old.trial_required) then
      raise exception 'Training and trial requirements were set at approval.';
    end if;
    new.approved_by := old.approved_by; new.approved_at := old.approved_at;
    if new.status <> old.status then
      if new.status in ('rejected','cancelled') then
        if not hx_can('changes', 3, new.license_id) then raise exception 'Only Full access can % a change.', case when new.status = 'rejected' then 'reject' else 'cancel' end; end if;
        if new.status = 'rejected' and old.status <> 'requested' then raise exception 'Only a requested change can be rejected. Cancel it instead.'; end if;
        if old.status = 'implemented' then raise exception 'This change is already implemented. Close it with the effectiveness check, or request a new change to undo it.'; end if;
        if coalesce(trim(new.stop_reason), '') = '' then raise exception 'A reason is required.'; end if;
        new.closed_by := v_me; new.closed_at := now();
        perform set_config('hx.reason', 'Change ' || new.status || ': ' || trim(new.stop_reason), true);
      elsif new.status = 'approved' and old.status = 'requested' then
        if not hx_can('changes', 3, new.license_id) then raise exception 'Only Full access (a qualified person) can approve a change.'; end if;
        new.approved_by := v_me; new.approved_at := now();
        perform set_config('hx.reason', 'Change approved', true);
      elsif new.status = 'implemented' and old.status = 'approved' then
        for a in select * from jsonb_array_elements(coalesce(new.actions, '[]'::jsonb)) loop
          n_act := n_act + 1; if coalesce((a->>'done')::boolean, false) is not true then n_open := n_open + 1; end if;
        end loop;
        if n_act = 0 then raise exception 'List the actions that put the change in place.'; end if;
        if n_open > 0 then raise exception '% action(s) are not done yet.', n_open; end if;
        if new.training_required and not new.training_done then raise exception 'Training must be given before the change is used.'; end if;
        if new.trial_required and new.trial_result <> 'pass' then raise exception 'A trial run must pass before the change is implemented.'; end if;
        if coalesce((new.impacts->>'haccp')::boolean, false) and not new.haccp_reviewed then
          raise exception 'HACCP is affected: review (and revalidate) the HACCP plan before the change is implemented.';
        end if;
        if (coalesce((new.notify->>'regulator')::boolean, false) or coalesce((new.notify->>'cert_body')::boolean, false) or coalesce((new.notify->>'customers')::boolean, false)) and new.notified_on is null then
          raise exception 'Record when the regulator / certification body / customers were told.';
        end if;
        if new.implemented_on is null then new.implemented_on := current_date; end if;
        if new.implemented_on > current_date then raise exception 'The implementation date cannot be in the future.'; end if;
        perform set_config('hx.reason', 'Change implemented', true);
      elsif new.status = 'closed' and old.status = 'implemented' then
        if not hx_can('changes', 3, new.license_id) then raise exception 'Only Full access can close a change.'; end if;
        if coalesce(trim(new.effectiveness), '') = '' then raise exception 'Record the effectiveness check (did the change work as planned?).'; end if;
        new.closed_by := v_me; new.closed_at := now();
        perform set_config('hx.reason', 'Change closed after effectiveness check', true);
      else
        raise exception 'A change goes requested -> approved -> implemented -> closed (or rejected / cancelled).';
      end if;
    elsif old.status = 'approved' then
      perform set_config('hx.reason', 'Change plan updated', true);
    elsif old.status = 'implemented' and (new.actions, new.training_done, new.trial_result, new.haccp_reviewed, new.notified_on, new.implemented_on)
         is distinct from (old.actions, old.training_done, old.trial_result, old.haccp_reviewed, old.notified_on, old.implemented_on) then
      raise exception 'This change is implemented. Its actions are on record.';
    end if;
  end if;
  if coalesce(trim(new.description), '') = '' then raise exception 'Describe what changes.'; end if;
  if coalesce(trim(new.reason), '') = '' then raise exception 'Give the reason for the change.'; end if;
  if not exists (select 1 from jsonb_each(coalesce(new.impacts, '{}'::jsonb)) e where e.value = 'true'::jsonb) then
    raise exception 'Complete the impact assessment (tick what the change affects, or "Nothing else is affected").';
  end if;
  if new.risk_id is not null and not exists (select 1 from hx_risks where id = new.risk_id and license_id = new.license_id) then raise exception 'That risk belongs to another license.'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_changes_guard on hx_changes;
create trigger hx_changes_guard before insert or update or delete on hx_changes for each row execute function hx_change_guard();
drop trigger if exists hx_changes_place on hx_changes;
create trigger hx_changes_place before insert or update on hx_changes for each row execute function hx_fl_guard();
drop trigger if exists hx_changes_audit on hx_changes;
create trigger hx_changes_audit after insert or update on hx_changes for each row execute function hx_audit();

alter table hx_risks enable row level security;
alter table hx_risk_reviews enable row level security;
alter table hx_changes enable row level security;
drop policy if exists hx_risks_read on hx_risks;
drop policy if exists hx_risks_insert on hx_risks;
drop policy if exists hx_risks_update on hx_risks;
create policy hx_risks_read   on hx_risks for select to authenticated using (hx_can('risks',1,license_id));
create policy hx_risks_insert on hx_risks for insert to authenticated with check (hx_can('risks',2,license_id));
create policy hx_risks_update on hx_risks for update to authenticated using (hx_can('risks',2,license_id)) with check (hx_can('risks',2,license_id));
drop policy if exists hx_risk_reviews_read on hx_risk_reviews;
drop policy if exists hx_risk_reviews_insert on hx_risk_reviews;
create policy hx_risk_reviews_read   on hx_risk_reviews for select to authenticated using (hx_can('risks',1,license_id));
create policy hx_risk_reviews_insert on hx_risk_reviews for insert to authenticated with check (hx_can('risks',2,license_id));
drop policy if exists hx_changes_read on hx_changes;
drop policy if exists hx_changes_insert on hx_changes;
drop policy if exists hx_changes_update on hx_changes;
create policy hx_changes_read   on hx_changes for select to authenticated using (hx_can('changes',1,license_id));
create policy hx_changes_insert on hx_changes for insert to authenticated with check (hx_can('changes',2,license_id));
create policy hx_changes_update on hx_changes for update to authenticated using (hx_can('changes',2,license_id)) with check (hx_can('changes',2,license_id));
grant select, insert, update on hx_risks, hx_changes to authenticated;
grant select, insert on hx_risk_reviews to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step30.sql
-- ###################################################################
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


-- ###################################################################
-- ### hendrix_step31.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 31: Management review and Verification schedule (CSQ Level 3)
-- Management review (CSQ 5.1.3):
--   * numbered MR-YYYY-###; the period reviewed, chair (senior management),
--     attendees; every input with the facts (filled from Hendrix records)
--     and the discussion: actions from the last review, complaints and
--     feedback, internal / external / regulatory audits, deviations and
--     CAPAs, risks, HACCP, quality objectives / KPIs, CSQ conformance,
--     changes, suppliers, training, resources
--   * decisions, resource needs, actions (what, who, due, done), the next
--     review date (within 12 months), who the minutes were shared with
--   * "held" (signed) by Full access only when the required inputs were
--     discussed; after that the minutes are frozen - only actions can be
--     ticked done and the sharing recorded
-- Verification schedule (CSQ 5.1.8):
--   * VS-###: the activity verified, how, who, how often, and where it is
--     recorded; many are linked to Hendrix records (sanitation log
--     verification, CCP record review, HACCP verification, calibration,
--     internal audits, facility tests, risk reviews, KPI reviews,
--     management review, supplier reviews) so the last date is automatic
--   * hx_verification_records: each verification done by hand, with the
--     result; issues need the action taken; never deleted (void with reason)
-- Access modules 'mgmtreview' and 'verification': View / Edit / Full.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-30.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_mgmt_reviews (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  number        text not null default '',
  meeting_date  date not null default current_date,
  period_from   date,
  period_to     date,
  chair         text not null default '',
  attendees     text not null default '',
  inputs        jsonb not null default '{}'::jsonb,
  decisions     text not null default '',
  resources     text not null default '',
  actions       jsonb not null default '[]'::jsonb,
  next_review   date,
  shared_with   text not null default '',
  shared_on     date,
  status        text not null default 'draft' check (status in ('draft','held','cancelled')),
  signed_by     text not null default '',
  signed_at     timestamptz,
  cancel_reason text,
  files         jsonb not null default '[]'::jsonb,
  created_by    text not null default '',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists hx_mgmt_reviews_number on hx_mgmt_reviews(license_id, number);

create or replace function hx_mgmt_review_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v_miss text := '';
begin
  if tg_op = 'DELETE' then raise exception 'Management reviews are never deleted. Cancel a draft with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_mgmt_reviews', new.license_id, 'MR');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.status := 'draft'; new.signed_by := ''; new.signed_at := null; new.cancel_reason := null;
    perform set_config('hx.reason', 'Management review started', true);
    new.updated_at := now(); return new;
  end if;
  new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
  if old.status = 'cancelled' then raise exception 'This management review was cancelled.'; end if;
  if old.status = 'held' then
    if new.status <> 'held' then raise exception 'A held management review cannot be cancelled or reopened.'; end if;
    if (to_jsonb(new) - 'actions' - 'shared_with' - 'shared_on' - 'files' - 'updated_at') is distinct from (to_jsonb(old) - 'actions' - 'shared_with' - 'shared_on' - 'files' - 'updated_at') then
      raise exception 'The minutes are signed. Only actions, sharing and files can be updated.';
    end if;
    if jsonb_array_length(coalesce(new.actions, '[]'::jsonb)) <> jsonb_array_length(coalesce(old.actions, '[]'::jsonb)) then
      raise exception 'Actions decided in the review cannot be added or removed after it is signed.';
    end if;
    if new.shared_on is not null and new.shared_on > current_date then raise exception 'The sharing date cannot be in the future.'; end if;
    perform set_config('hx.reason', case when new.shared_on is distinct from old.shared_on then 'Minutes shared' else 'Review actions updated' end, true);
    new.updated_at := now(); return new;
  end if;
  if new.status = 'cancelled' then
    if not hx_can('mgmtreview', 3, new.license_id) then raise exception 'Only Full access can cancel a management review.'; end if;
    if coalesce(trim(new.cancel_reason), '') = '' then raise exception 'A reason is required.'; end if;
    perform set_config('hx.reason', 'Management review cancelled: ' || trim(new.cancel_reason), true);
  elsif new.status = 'held' then
    if not hx_can('mgmtreview', 3, new.license_id) then raise exception 'Only Full access (senior management) can sign the management review.'; end if;
    if new.meeting_date > current_date then raise exception 'The meeting date cannot be in the future.'; end if;
    if coalesce(trim(new.chair), '') = '' or coalesce(trim(new.attendees), '') = '' then raise exception 'Enter the chair and who attended.'; end if;
    foreach k in array array['prev_actions','complaints','audits','deviations','risks','csq','changes','resources'] loop
      if coalesce(trim(new.inputs->k->>'notes'), '') = '' then v_miss := v_miss || k || ' '; end if;
    end loop;
    if v_miss <> '' then raise exception 'Discuss every required input before signing (missing: %).', trim(v_miss); end if;
    if coalesce(trim(new.decisions), '') = '' then raise exception 'Record the decisions and conclusions.'; end if;
    if new.next_review is null or new.next_review <= new.meeting_date or new.next_review > new.meeting_date + 366 then
      raise exception 'Set the next review within 12 months of this one.';
    end if;
    new.signed_by := coalesce(hx_me(), ''); new.signed_at := now();
    perform set_config('hx.reason', 'Management review held and signed', true);
  else
    perform set_config('hx.reason', 'Management review draft updated', true);
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_mgmt_reviews_guard on hx_mgmt_reviews;
create trigger hx_mgmt_reviews_guard before insert or update or delete on hx_mgmt_reviews for each row execute function hx_mgmt_review_guard();
drop trigger if exists hx_mgmt_reviews_place on hx_mgmt_reviews;
create trigger hx_mgmt_reviews_place before insert or update on hx_mgmt_reviews for each row execute function hx_fl_guard();
drop trigger if exists hx_mgmt_reviews_audit on hx_mgmt_reviews;
create trigger hx_mgmt_reviews_audit after insert or update on hx_mgmt_reviews for each row execute function hx_audit();

create table if not exists hx_verification_plan (
  id              text primary key,
  state_id        text not null references hx_states(id),
  license_id      text not null references hx_licenses(id),
  number          text not null default '',
  activity        text not null check (length(trim(activity)) > 0),
  method          text not null default '',
  responsible     text not null default '',
  frequency_days  int  not null default 30 check (frequency_days between 1 and 1095),
  source          text not null default 'manual',
  record_where    text not null default '',
  clause          text not null default '',
  active          boolean not null default true,
  created_by      text not null default '',
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create unique index if not exists hx_verification_plan_number on hx_verification_plan(license_id, number);

create or replace function hx_verification_plan_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Verification activities are never deleted. Turn the activity off instead.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_seq('hx_verification_plan', new.license_id, 'VS'); new.created_by := coalesce(hx_me(), ''); new.created_at := now();
    perform set_config('hx.reason', 'Verification activity added', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if new.active is distinct from old.active and not new.active and not hx_can('verification', 3, new.license_id) then raise exception 'Only Full access can turn a verification activity off.'; end if;
    perform set_config('hx.reason', case when new.active is distinct from old.active then (case when new.active then 'Verification activity turned on' else 'Verification activity turned off' end) else 'Verification activity updated' end, true);
  end if;
  if coalesce(trim(new.responsible), '') = '' then raise exception 'Enter who does the verification.'; end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_verification_plan_guard on hx_verification_plan;
create trigger hx_verification_plan_guard before insert or update or delete on hx_verification_plan for each row execute function hx_verification_plan_guard();
drop trigger if exists hx_verification_plan_place on hx_verification_plan;
create trigger hx_verification_plan_place before insert or update on hx_verification_plan for each row execute function hx_fl_guard();
drop trigger if exists hx_verification_plan_audit on hx_verification_plan;
create trigger hx_verification_plan_audit after insert or update on hx_verification_plan for each row execute function hx_audit();

create table if not exists hx_verification_records (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  plan_id       text not null references hx_verification_plan(id),
  done_on       date not null default current_date,
  done_by       text not null default '',
  result        text not null default 'ok' check (result in ('ok','issues')),
  findings      text not null default '',
  action        text not null default '',
  deviation_id  text,
  files         jsonb not null default '[]'::jsonb,
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_verification_records_plan on hx_verification_records(plan_id);

create or replace function hx_verification_record_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Verification records are never deleted. Void it with a reason.'; end if;
  if tg_op = 'UPDATE' then
    if old.voided then raise exception 'This record is void.'; end if;
    if new.voided then
      if not hx_can('verification', 3, old.license_id) then raise exception 'Only Full access can void a verification record.'; end if;
      if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a record.'; end if;
      if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then raise exception 'Void a record without changing anything else.'; end if;
      new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true); return new;
    end if;
    if (to_jsonb(new) - 'deviation_id' - 'files') is distinct from (to_jsonb(old) - 'deviation_id' - 'files') then raise exception 'A verification record cannot be changed. Void it and record it again.'; end if;
    return new;
  end if;
  if not exists (select 1 from hx_verification_plan where id = new.plan_id and license_id = new.license_id) then raise exception 'That activity belongs to another license.'; end if;
  if new.done_on > current_date then raise exception 'The date cannot be in the future.'; end if;
  if coalesce(trim(new.done_by), '') = '' then raise exception 'Enter who did the verification.'; end if;
  if new.result = 'issues' and (coalesce(trim(new.findings), '') = '' or coalesce(trim(new.action), '') = '') then raise exception 'Describe the issues found and the action taken.'; end if;
  new.recorded_by := coalesce(hx_me(), ''); new.created_at := now(); new.voided := false; new.void_reason := null; new.voided_at := null;
  perform set_config('hx.reason', case when new.result = 'ok' then 'Verified - no issues' else 'Verified - issues found' end, true);
  return new;
end $$;
drop trigger if exists hx_verification_records_guard on hx_verification_records;
create trigger hx_verification_records_guard before insert or update or delete on hx_verification_records for each row execute function hx_verification_record_guard();
drop trigger if exists hx_verification_records_place on hx_verification_records;
create trigger hx_verification_records_place before insert or update on hx_verification_records for each row execute function hx_fl_guard();
drop trigger if exists hx_verification_records_audit on hx_verification_records;
create trigger hx_verification_records_audit after insert or update on hx_verification_records for each row execute function hx_audit();

-- deviations can be raised from a verification with issues
alter table hx_deviations drop constraint if exists hx_deviations_source_type_check;
alter table hx_deviations add constraint hx_deviations_source_type_check
  check (source_type in ('manual','facility_log','batch','test','visitor','standard','complaint','audit','line_clearance','rework','equipment','facility_test','haccp','verification'));

alter table hx_mgmt_reviews enable row level security;
alter table hx_verification_plan enable row level security;
alter table hx_verification_records enable row level security;
drop policy if exists hx_mgmt_reviews_read on hx_mgmt_reviews;
drop policy if exists hx_mgmt_reviews_insert on hx_mgmt_reviews;
drop policy if exists hx_mgmt_reviews_update on hx_mgmt_reviews;
create policy hx_mgmt_reviews_read   on hx_mgmt_reviews for select to authenticated using (hx_can('mgmtreview',1,license_id));
create policy hx_mgmt_reviews_insert on hx_mgmt_reviews for insert to authenticated with check (hx_can('mgmtreview',2,license_id));
create policy hx_mgmt_reviews_update on hx_mgmt_reviews for update to authenticated using (hx_can('mgmtreview',2,license_id)) with check (hx_can('mgmtreview',2,license_id));
drop policy if exists hx_verification_plan_read on hx_verification_plan;
drop policy if exists hx_verification_plan_insert on hx_verification_plan;
drop policy if exists hx_verification_plan_update on hx_verification_plan;
create policy hx_verification_plan_read   on hx_verification_plan for select to authenticated using (hx_can('verification',1,license_id));
create policy hx_verification_plan_insert on hx_verification_plan for insert to authenticated with check (hx_can('verification',2,license_id));
create policy hx_verification_plan_update on hx_verification_plan for update to authenticated using (hx_can('verification',2,license_id)) with check (hx_can('verification',2,license_id));
drop policy if exists hx_verification_records_read on hx_verification_records;
drop policy if exists hx_verification_records_insert on hx_verification_records;
drop policy if exists hx_verification_records_update on hx_verification_records;
create policy hx_verification_records_read   on hx_verification_records for select to authenticated using (hx_can('verification',1,license_id));
create policy hx_verification_records_insert on hx_verification_records for insert to authenticated with check (hx_can('verification',2,license_id));
create policy hx_verification_records_update on hx_verification_records for update to authenticated using (hx_can('verification',2,license_id)) with check (hx_can('verification',2,license_id));
grant select, insert, update on hx_mgmt_reviews, hx_verification_plan, hx_verification_records to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step32.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 32: Time Clock and Badges (from the Michigan app)
-- Badges (one per person, used at every license they have access to):
--   * photo (square, zoom / position), title on the card, ID number, and a
--     secret badge code printed as a QR code and a Code 128 barcode
--   * badges live in hx_badges, which no one reads directly: the badge code
--     never reaches other users (no "buddy punching" from a copied QR);
--     only Edit on Time Clock issues and prints badges (via functions)
--   * a lost badge is re-issued by Full access with a reason: the old QR and
--     barcode stop working at once
--   * anyone scanning a badge with a phone sees a verification page (name,
--     title, photo, valid or not) - nothing else
-- Time clock (same rules as the Michigan time clock):
--   * fixed 8 punches per person per day: Clock in, 1st break out / back,
--     2nd break out / back, 3rd break out / back, Clock out
--   * break limits 15 / 30 / 15 minutes; a late return is flagged with the
--     minutes over, for review on the sign-in sheet
--   * the kiosk (QR link per state + license, no login) takes a USB / Bluetooth
--     scanner or the tablet camera; the database picks the next punch, checks
--     the person has access to that license and ignores a double scan within
--     60 seconds
--   * punches are never edited: Full access voids a wrong punch or adds a
--     missed punch, always with a reason (audit trail)
-- Access module 'timeclock': View (sign-in sheet, on site now) / Edit
-- (badges) / Full (re-issue badges, fix punches).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-31.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_badges (
  profile_id     uuid primary key references hx_profiles(id),
  code           text not null unique,
  badge_no       text not null unique,
  title          text not null default '',
  photo          text,
  zoom           numeric not null default 1,
  pos_x          int not null default 0,
  pos_y          int not null default 0,
  active         boolean not null default true,
  issued_at      timestamptz not null default now(),
  issued_by      text not null default '',
  updated_at     timestamptz not null default now()
);
alter table hx_badges enable row level security;   -- no policies: read and written only through the functions below
revoke all on hx_badges from anon, authenticated;

create table if not exists hx_time_clock (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  profile_id    uuid not null references hx_profiles(id),
  person_name   text not null default '',
  event_type    text not null check (event_type in ('entry','break1_out','break1_in','break2_out','break2_in','break3_out','break3_in','clockout')),
  ts            timestamptz not null default now(),
  event_date    date not null,
  late          boolean not null default false,
  late_minutes  int,
  source        text not null default 'kiosk' check (source in ('kiosk','manual')),
  reason        text not null default '',
  recorded_by   text not null default '',
  created_at    timestamptz not null default now(),
  voided        boolean not null default false,
  void_reason   text,
  voided_at     timestamptz
);
create index if not exists hx_time_clock_day on hx_time_clock(license_id, event_date);
create index if not exists hx_time_clock_person on hx_time_clock(profile_id, event_date);

-- only voiding is allowed after a punch is written
create or replace function hx_time_clock_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Punches are never deleted. Void it with a reason.'; end if;
  if tg_op = 'INSERT' then
    if coalesce(current_setting('hx.internal', true), '') <> 'on' then raise exception 'Punches are recorded by the time clock kiosk (or as a missed punch by Full access).'; end if;
    return new;
  end if;
  if old.voided then raise exception 'This punch is void.'; end if;
  if not new.voided then raise exception 'A punch cannot be changed. Void it and add the right one.'; end if;
  if not hx_can('timeclock', 3, old.license_id) then raise exception 'Only Full access can void a punch.'; end if;
  if coalesce(trim(new.void_reason), '') = '' then raise exception 'A reason is required to void a punch.'; end if;
  if (to_jsonb(new) - 'voided' - 'void_reason' - 'voided_at') is distinct from (to_jsonb(old) - 'voided' - 'void_reason' - 'voided_at') then
    raise exception 'Void a punch without changing anything else.';
  end if;
  new.voided_at := now(); perform set_config('hx.reason', trim(new.void_reason), true);
  return new;
end $$;
drop trigger if exists hx_time_clock_guard on hx_time_clock;
create trigger hx_time_clock_guard before insert or update or delete on hx_time_clock for each row execute function hx_time_clock_guard();
drop trigger if exists hx_time_clock_place on hx_time_clock;
create trigger hx_time_clock_place before insert or update on hx_time_clock for each row execute function hx_fl_guard();
drop trigger if exists hx_time_clock_audit on hx_time_clock;
create trigger hx_time_clock_audit after insert or update on hx_time_clock for each row execute function hx_audit();

alter table hx_time_clock enable row level security;
drop policy if exists hx_time_clock_read on hx_time_clock;
drop policy if exists hx_time_clock_update on hx_time_clock;
create policy hx_time_clock_read   on hx_time_clock for select to authenticated using (hx_can('timeclock',1,license_id) or profile_id::text = auth.uid()::text);
create policy hx_time_clock_update on hx_time_clock for update to authenticated using (hx_can('timeclock',3,license_id)) with check (hx_can('timeclock',3,license_id));
grant select, update on hx_time_clock to authenticated;

-- does this person work at this license?
create or replace function hx_person_at(p_profile uuid, p_lic text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from hx_profiles p where p.id = p_profile and coalesce(p.approved,false)
                 and (p.role = 'admin' or coalesce(array_length(p.license_ids,1),0) = 0 or p_lic = any(p.license_ids)));
$$;

create or replace function hx_badge_log(p_profile uuid, p_lic text, p_action text, p_reason text) returns void
language plpgsql security definer set search_path = public as $$
declare v_name text; v_state text;
begin
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id::text = auth.uid()::text;
  select state_id into v_state from hx_licenses where id = p_lic;
  insert into hx_audit_log(table_name, row_id, action, state_id, license_id, user_id, user_name, reason, changed, old_data, new_data)
  values ('hx_badges', p_profile::text, p_action, v_state, p_lic, auth.uid(), v_name, p_reason, null, null,
          (select jsonb_build_object('person', coalesce(nullif(name,''), email)) from hx_profiles where id = p_profile));
end $$;
revoke all on function hx_badge_log(uuid,text,text,text) from public, anon, authenticated;

-- people at a license with their badge (the code only for Edit, to print the card)
create or replace function hx_badge_roster(p_lic text) returns json
language plpgsql stable security definer set search_path = public as $$
declare v_edit boolean;
begin
  if not hx_can('timeclock', 1, p_lic) then raise exception 'No access to the time clock at this license.'; end if;
  v_edit := hx_can('timeclock', 2, p_lic);
  return coalesce((select json_agg(json_build_object('id', p.id, 'name', coalesce(nullif(p.name,''), p.email), 'email', p.email,
            'has_badge', b.profile_id is not null and b.active, 'badge_no', b.badge_no, 'title', b.title,
            'photo', b.photo, 'zoom', b.zoom, 'pos_x', b.pos_x, 'pos_y', b.pos_y, 'issued_at', b.issued_at, 'issued_by', b.issued_by,
            'code', case when v_edit then b.code end) order by lower(coalesce(nullif(p.name,''), p.email)))
     from hx_profiles p left join hx_badges b on b.profile_id = p.id
    where hx_person_at(p.id, p_lic)), '[]'::json);
end $$;

create or replace function hx_new_badge_code() returns text
language sql volatile set search_path = public as $$
  select upper(substr(md5(gen_random_uuid()::text || clock_timestamp()::text || random()::text), 1, 12));
$$;

create or replace function hx_badge_save(p_lic text, p_profile uuid, p_title text, p_photo text, p_zoom numeric, p_x int, p_y int) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_new boolean; v_no text; v_code text; n int := 0;
begin
  if not hx_can('timeclock', 2, p_lic) then raise exception 'Only Edit access on the time clock can make badges.'; end if;
  if not hx_person_at(p_profile, p_lic) then raise exception 'That person does not work at this license.'; end if;
  if p_photo is not null and length(p_photo) > 400000 then raise exception 'The photo is too large.'; end if;
  if p_photo is not null and p_photo !~ '^data:image/(jpeg|png|webp);base64,' then raise exception 'The photo must be an image.'; end if;
  v_new := not exists (select 1 from hx_badges where profile_id = p_profile);
  if v_new then
    loop
      n := n + 1; v_no := lpad((1000 + floor(random() * 9000))::int::text, 4, '0'); v_code := hx_new_badge_code();
      exit when not exists (select 1 from hx_badges where badge_no = v_no or code = v_code) or n > 50;
    end loop;
    insert into hx_badges(profile_id, code, badge_no, title, photo, zoom, pos_x, pos_y, issued_by)
    values (p_profile, v_code, v_no, left(coalesce(trim(p_title),''), 60), p_photo, coalesce(p_zoom,1), coalesce(p_x,0), coalesce(p_y,0), coalesce(hx_me(),''));
    perform hx_badge_log(p_profile, p_lic, 'INSERT', 'Badge issued');
  else
    update hx_badges set title = left(coalesce(trim(p_title),''), 60), photo = p_photo, zoom = coalesce(p_zoom,1), pos_x = coalesce(p_x,0), pos_y = coalesce(p_y,0), updated_at = now()
     where profile_id = p_profile;
    perform hx_badge_log(p_profile, p_lic, 'UPDATE', 'Badge photo / title updated');
  end if;
  return (select json_build_object('badge_no', badge_no, 'code', code) from hx_badges where profile_id = p_profile);
end $$;

-- lost or stolen badge: a new code, the old card stops working
create or replace function hx_badge_reissue(p_lic text, p_profile uuid, p_reason text) returns json
language plpgsql volatile security definer set search_path = public as $$
declare v_code text;
begin
  if not hx_can('timeclock', 3, p_lic) then raise exception 'Only Full access can re-issue a badge.'; end if;
  if coalesce(trim(p_reason),'') = '' then raise exception 'A reason is required (for example: badge lost).'; end if;
  if not exists (select 1 from hx_badges where profile_id = p_profile) then raise exception 'This person has no badge yet.'; end if;
  loop v_code := hx_new_badge_code(); exit when not exists (select 1 from hx_badges where code = v_code); end loop;
  update hx_badges set code = v_code, active = true, issued_at = now(), issued_by = coalesce(hx_me(),''), updated_at = now() where profile_id = p_profile;
  perform hx_badge_log(p_profile, p_lic, 'UPDATE', 'Badge re-issued: ' || trim(p_reason));
  return (select json_build_object('badge_no', badge_no, 'code', code) from hx_badges where profile_id = p_profile);
end $$;

-- public badge check (someone scans a badge with their phone): name, title, photo only
create or replace function hx_badge_lookup(p_code text) returns json
language sql stable security definer set search_path = public as $$
  select json_build_object('name', coalesce(nullif(p.name,''), split_part(p.email,'@',1)), 'title', b.title, 'photo', b.photo, 'badge_no', b.badge_no,
                           'valid', b.active and coalesce(p.approved,false))
    from hx_badges b join hx_profiles p on p.id = b.profile_id
   where b.code = upper(trim(p_code));
$$;

-- the kiosk punch: next event in the day's sequence, break lateness, double-scan guard
create or replace function hx_kiosk_clock(p_state text, p_lic text, p_code text, p_date date) returns json
language plpgsql volatile security definer set search_path = public as $$
declare b record; p record; v_last record; v_next text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int; v_now timestamptz := now();
  seq text[] := array['entry','break1_out','break1_in','break2_out','break2_in','break3_out','break3_in','clockout'];
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This kiosk is not linked to an active license in this state.'; end if;
  if p_date is null or p_date < current_date - 1 or p_date > current_date + 1 then raise exception 'The kiosk date is wrong. Check the tablet clock.'; end if;
  select * into b from hx_badges where code = upper(trim(coalesce(p_code,'')));
  if b.profile_id is null or not b.active then return json_build_object('error', 'Badge not recognized.'); end if;
  select * into p from hx_profiles where id = b.profile_id;
  if not hx_person_at(p.id, p_lic) then
    return json_build_object('error', 'Not authorized at this license.', 'name', coalesce(nullif(p.name,''), p.email), 'photo', b.photo, 'title', b.title);
  end if;
  perform pg_advisory_xact_lock(hashtext('clock' || p.id::text || p_lic));
  select * into v_last from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided order by ts desc limit 1;
  if v_last.id is not null and v_now - v_last.ts < interval '60 seconds' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_last.event_type, 'ts', v_last.ts, 'late', v_last.late, 'late_minutes', v_last.late_minutes, 'repeat', true);
  end if;
  if v_last.id is null then v_next := 'entry';
  elsif v_last.event_type = 'clockout' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'done', true);
  else v_next := seq[array_position(seq, v_last.event_type) + 1];
  end if;
  if v_next in ('break1_in','break2_in','break3_in') then
    v_lim := case v_next when 'break2_in' then 30 else 15 end;
    select * into v_out from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided and event_type = replace(v_next, '_in', '_out') order by ts desc limit 1;
    if v_out.id is not null then
      v_el := extract(epoch from (v_now - v_out.ts)) / 60;
      v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end;
    end if;
  end if;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', 'Badge scan', true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, recorded_by)
  values ('tc-' || replace(gen_random_uuid()::text,'-',''), p_state, p_lic, p.id, coalesce(nullif(p.name,''), p.email), v_next, v_now, p_date, v_late, v_lm, 'kiosk', 'Kiosk');
  perform set_config('hx.internal', '', true);
  return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_next, 'ts', v_now, 'late', v_late, 'late_minutes', v_lm);
end $$;

-- a missed punch added by Full access (reason required)
create or replace function hx_clock_fix(p_lic text, p_profile uuid, p_date date, p_event text, p_ts timestamptz, p_reason text) returns text
language plpgsql volatile security definer set search_path = public as $$
declare v_state text; v_name text; v_id text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int;
begin
  if not hx_can('timeclock', 3, p_lic) then raise exception 'Only Full access can add a missed punch.'; end if;
  if coalesce(trim(p_reason),'') = '' then raise exception 'A reason is required.'; end if;
  if not hx_person_at(p_profile, p_lic) then raise exception 'That person does not work at this license.'; end if;
  if p_ts > now() then raise exception 'The time cannot be in the future.'; end if;
  if exists (select 1 from hx_time_clock where profile_id = p_profile and license_id = p_lic and event_date = p_date and event_type = p_event and not voided) then
    raise exception 'That punch is already recorded for the day. Void it first to replace it.';
  end if;
  if p_event in ('break1_in','break2_in','break3_in') then
    v_lim := case p_event when 'break2_in' then 30 else 15 end;
    select * into v_out from hx_time_clock where profile_id = p_profile and license_id = p_lic and event_date = p_date and not voided and event_type = replace(p_event, '_in', '_out') limit 1;
    if v_out.id is not null then v_el := extract(epoch from (p_ts - v_out.ts)) / 60; v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end; end if;
  end if;
  select state_id into v_state from hx_licenses where id = p_lic;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id = p_profile;
  v_id := 'tc-' || replace(gen_random_uuid()::text,'-','');
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', 'Missed punch added: ' || trim(p_reason), true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, reason, recorded_by)
  values (v_id, v_state, p_lic, p_profile, v_name, p_event, p_ts, p_date, v_late, v_lm, 'manual', trim(p_reason), coalesce(hx_me(),''));
  perform set_config('hx.internal', '', true);
  return v_id;
end $$;

revoke all on function hx_badge_roster(text) from public;
revoke all on function hx_badge_save(text,uuid,text,text,numeric,int,int) from public;
revoke all on function hx_badge_reissue(text,uuid,text) from public;
revoke all on function hx_badge_lookup(text) from public;
revoke all on function hx_kiosk_clock(text,text,text,date) from public;
revoke all on function hx_clock_fix(text,uuid,date,text,timestamptz,text) from public;
revoke all on function hx_person_at(uuid,text) from public;
revoke all on function hx_new_badge_code() from public;
grant execute on function hx_badge_roster(text) to authenticated;
grant execute on function hx_badge_save(text,uuid,text,text,numeric,int,int) to authenticated;
grant execute on function hx_badge_reissue(text,uuid,text) to authenticated;
grant execute on function hx_clock_fix(text,uuid,date,text,timestamptz,text) to authenticated;
grant execute on function hx_badge_lookup(text) to anon, authenticated;
grant execute on function hx_kiosk_clock(text,text,text,date) to anon, authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step33.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 33: Production Planner (from Black Fox / Michigan)
-- Same calculator as Black Fox: product type, SKU, flavors, units per
-- flavor, extra instructions ("5% waste buffer"):
--   * flavors with a saved formulation (Formulation Bank) are calculated
--     exactly from the recipe's reference batch; a SKU's base recipe covers
--     every flavor (the terpene is named per flavor)
--   * only flavors with no recipe at all go to the AI (hendrix-ai, module
--     'planner')
--   * per-flavor ingredients, grand total for the run, production worksheet
--     PDFs with the tracking blanks and signatures
-- Hendrix adds:
--   * plans are saved (PP-YYYY-###) with the date they are planned for;
--     batches made from the plan (Batch Tracker, "Start batch") show on it
--   * the grand total is checked against accepted inventory (Receiving)
--   * formulations stay private to the Formulation Bank: the planner reads
--     ingredient names and amounts only (no costs) through a function
-- Access module 'planner': View / Edit (plan, save, start batches) / Full
-- (cancel plans).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-32.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_production_plans (
  id               text primary key,
  state_id         text not null references hx_states(id),
  license_id       text not null references hx_licenses(id),
  number           text not null default '',
  product_type     text not null,
  sku_id           text references hx_skus(id),
  sku_name         text not null default '',
  planned_for      date not null default current_date,
  units_per_flavor int  not null check (units_per_flavor > 0),
  instructions     text not null default '',
  lines            jsonb not null default '[]'::jsonb,
  grand_total      jsonb not null default '[]'::jsonb,
  status           text not null default 'planned' check (status in ('planned','in_progress','completed','cancelled')),
  close_note       text,
  created_by       text not null default '',
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);
create unique index if not exists hx_production_plans_number on hx_production_plans(license_id, number);

create or replace function hx_plan_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then raise exception 'Plans are never deleted. Cancel the plan with a reason.'; end if;
  if tg_op = 'INSERT' then
    new.number := hx_next_number('hx_production_plans', new.license_id, 'PP');
    new.created_by := coalesce(hx_me(), ''); new.created_at := now(); new.status := 'planned'; new.close_note := null;
    perform set_config('hx.reason', 'Production plan saved', true);
  else
    new.number := old.number; new.created_by := old.created_by; new.created_at := old.created_at;
    if old.status in ('completed','cancelled') then raise exception 'This plan is %.', old.status; end if;
    if (new.product_type, new.sku_id, new.units_per_flavor, new.lines, new.grand_total) is distinct from (old.product_type, old.sku_id, old.units_per_flavor, old.lines, old.grand_total)
       and old.status <> 'planned' then
      raise exception 'Production has started on this plan. Cancel it and make a new plan to change the amounts.';
    end if;
    if new.status = 'cancelled' then
      if not hx_can('planner', 3, new.license_id) then raise exception 'Only Full access can cancel a plan.'; end if;
      if coalesce(trim(new.close_note), '') = '' then raise exception 'A reason is required to cancel a plan.'; end if;
      perform set_config('hx.reason', 'Plan cancelled: ' || trim(new.close_note), true);
    elsif new.status <> old.status then
      perform set_config('hx.reason', 'Plan ' || replace(new.status, '_', ' '), true);
    end if;
  end if;
  if jsonb_typeof(new.lines) <> 'array' or jsonb_array_length(new.lines) = 0 then raise exception 'Calculate the plan first (no flavors).'; end if;
  if new.sku_id is not null and not exists (select 1 from hx_skus s join hx_licenses l on l.id = new.license_id where s.id = new.sku_id and s.state_id = l.state_id) then
    raise exception 'That SKU belongs to another state.';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists hx_production_plans_guard on hx_production_plans;
create trigger hx_production_plans_guard before insert or update or delete on hx_production_plans for each row execute function hx_plan_guard();
drop trigger if exists hx_production_plans_place on hx_production_plans;
create trigger hx_production_plans_place before insert or update on hx_production_plans for each row execute function hx_fl_guard();
drop trigger if exists hx_production_plans_audit on hx_production_plans;
create trigger hx_production_plans_audit after insert or update on hx_production_plans for each row execute function hx_audit();

alter table hx_production_plans enable row level security;
drop policy if exists hx_production_plans_read on hx_production_plans;
drop policy if exists hx_production_plans_insert on hx_production_plans;
drop policy if exists hx_production_plans_update on hx_production_plans;
create policy hx_production_plans_read   on hx_production_plans for select to authenticated using (hx_can('planner',1,license_id));
create policy hx_production_plans_insert on hx_production_plans for insert to authenticated with check (hx_can('planner',2,license_id));
create policy hx_production_plans_update on hx_production_plans for update to authenticated using (hx_can('planner',2,license_id)) with check (hx_can('planner',2,license_id));
grant select, insert, update on hx_production_plans to authenticated;

-- recipe ingredients for the planner: names and amounts only, never costs, packaging or labor
create or replace function hx_planner_recipes(p_lic text, p_sku text) returns json
language plpgsql stable security definer set search_path = public as $$
begin
  if not (hx_can('planner', 1, p_lic) or hx_can('formbank', 1, p_lic)) then raise exception 'No access to the Production Planner at this license.'; end if;
  return coalesce((select json_agg(json_build_object('flavor_id', f.flavor_id, 'name', f.name, 'batch_size', f.batch_size,
            'raw_materials', coalesce((select json_agg(json_build_object('name', m->>'name', 'qty', m->>'qty', 'unit', coalesce(nullif(m->>'unit',''),'g')))
                                         from jsonb_array_elements(f.raw_materials) m where coalesce(trim(m->>'name'),'') <> ''), '[]'::json)))
     from hx_formulations f join hx_skus s on s.id = f.sku_id join hx_licenses l on l.id = p_lic
    where f.sku_id = p_sku and s.state_id = l.state_id), '[]'::json);
end $$;
revoke all on function hx_planner_recipes(text,text) from public;
grant execute on function hx_planner_recipes(text,text) to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step34.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 34: Settings (per license)
-- Like the Black Fox Settings module, one place for each license's settings:
--   * General: business details for printouts (legal name, DBA, address,
--     phone, email, footer) and the company logo; Hendrix prints them at
--     the top of every record and on badges and the time clock kiosk
--   * Time clock: break limits (minutes for the 1st, 2nd and 3rd break);
--     the kiosk and missed punches use them to flag late returns
--   * Facility logs: after how many days without an entry a log is flagged
--     as not kept up (dashboard and Standards evidence)
--   * Review cycles: how often risks are reviewed by level
--   * where everything else is set (products, roles, pick lists, labels...)
-- Only Full access on 'settings' (or an admin) changes them; everyone at the
-- license reads them. Every change is in the audit trail.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-33.
-- Safe to run more than once.
-- =====================================================================

create table if not exists hx_license_settings (
  license_id    text primary key references hx_licenses(id),
  state_id      text not null references hx_states(id),
  legal_name    text not null default '',
  dba           text not null default '',
  address       text not null default '',
  phone         text not null default '',
  email         text not null default '',
  print_footer  text not null default '',
  logo          text,
  break1_min    int not null default 15 check (break1_min between 1 and 240),
  break2_min    int not null default 30 check (break2_min between 1 and 240),
  break3_min    int not null default 15 check (break3_min between 1 and 240),
  log_due       jsonb not null default '{}'::jsonb,
  review_days   jsonb not null default '{}'::jsonb,
  updated_by    text not null default '',
  updated_at    timestamptz not null default now()
);

create or replace function hx_license_settings_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare k text; v jsonb;
begin
  if tg_op = 'DELETE' then raise exception 'Settings are not deleted.'; end if;
  if not hx_can('settings', 3, new.license_id) then raise exception 'Only Full access on Settings can change the settings of this license.'; end if;
  if tg_op = 'UPDATE' and new.license_id <> old.license_id then raise exception 'Settings cannot move to another license.'; end if;
  if new.logo is not null and (length(new.logo) > 300000 or new.logo !~ '^data:image/(png|jpeg|webp|svg\+xml);base64,') then raise exception 'The logo must be a PNG, JPG, WEBP or SVG image under 200 KB.'; end if;
  if new.email <> '' and new.email !~ '^[^@\s]+@[^@\s]+\.[^@\s]+$' then raise exception 'Check the email address.'; end if;
  if jsonb_typeof(new.log_due) <> 'object' or jsonb_typeof(new.review_days) <> 'object' then raise exception 'Bad settings.'; end if;
  for k, v in select * from jsonb_each(new.log_due) loop
    if jsonb_typeof(v) <> 'number' or (v::text)::numeric < 1 or (v::text)::numeric > 400 then raise exception 'Log due days must be between 1 and 400.'; end if;
  end loop;
  for k, v in select * from jsonb_each(new.review_days) loop
    if jsonb_typeof(v) <> 'number' or (v::text)::numeric < 7 or (v::text)::numeric > 1095 then raise exception 'Review cycles must be between 7 and 1095 days.'; end if;
  end loop;
  new.updated_by := coalesce(hx_me(), ''); new.updated_at := now();
  perform set_config('hx.reason', 'Settings changed', true);
  return new;
end $$;
drop trigger if exists hx_license_settings_guard on hx_license_settings;
create trigger hx_license_settings_guard before insert or update or delete on hx_license_settings for each row execute function hx_license_settings_guard();
drop trigger if exists hx_license_settings_place on hx_license_settings;
create trigger hx_license_settings_place before insert or update on hx_license_settings for each row execute function hx_fl_guard();
drop trigger if exists hx_license_settings_audit on hx_license_settings;
create trigger hx_license_settings_audit after insert or update on hx_license_settings for each row execute function hx_audit();

alter table hx_license_settings enable row level security;
drop policy if exists hx_license_settings_read on hx_license_settings;
drop policy if exists hx_license_settings_insert on hx_license_settings;
drop policy if exists hx_license_settings_update on hx_license_settings;
create policy hx_license_settings_read   on hx_license_settings for select to authenticated using (hx_lic_ok(license_id));
create policy hx_license_settings_insert on hx_license_settings for insert to authenticated with check (hx_can('settings',3,license_id));
create policy hx_license_settings_update on hx_license_settings for update to authenticated using (hx_can('settings',3,license_id)) with check (hx_can('settings',3,license_id));
grant select, insert, update on hx_license_settings to authenticated;

-- break limit for the return punch ('break1_in' ...), from the license settings
create or replace function hx_break_limit(p_lic text, p_in text) returns int
language sql stable security definer set search_path = public as $$
  select coalesce((select case p_in when 'break1_in' then break1_min when 'break2_in' then break2_min else break3_min end from hx_license_settings where license_id = p_lic),
                  case p_in when 'break2_in' then 30 else 15 end);
$$;
revoke all on function hx_break_limit(text,text) from public, anon, authenticated;

-- kiosks show the company logo and name, and the time clock its break limits
create or replace function hx_kiosk_check(p_state text, p_lic text) returns json
language plpgsql stable security definer set search_path = public as $$
declare r json;
begin
  if coalesce(p_state,'') = '' or coalesce(p_lic,'') = '' then
    return null;
  end if;
  select json_build_object('id', l.id, 'name', l.name, 'license_number', l.license_number,
                           'state_id', s.id, 'state', s.name,
                           'display_name', coalesce(nullif(ls.dba,''), nullif(ls.legal_name,''), l.name), 'logo', ls.logo,
                           'breaks', json_build_array(coalesce(ls.break1_min,15), coalesce(ls.break2_min,30), coalesce(ls.break3_min,15)))
    into r
    from hx_licenses l join hx_states s on s.id = l.state_id left join hx_license_settings ls on ls.license_id = l.id
   where l.id = p_lic and l.state_id = p_state and l.active = true;
  return r;
end $$;
revoke all on function hx_kiosk_check(text,text) from public;
grant execute on function hx_kiosk_check(text,text) to anon, authenticated;

-- the time clock uses the license break limits (same as step 32 otherwise)
create or replace function hx_kiosk_clock(p_state text, p_lic text, p_code text, p_date date) returns json
language plpgsql volatile security definer set search_path = public as $$
declare b record; p record; v_last record; v_next text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int; v_now timestamptz := now();
  seq text[] := array['entry','break1_out','break1_in','break2_out','break2_in','break3_out','break3_in','clockout'];
begin
  if hx_kiosk_check(p_state, p_lic) is null then raise exception 'This kiosk is not linked to an active license in this state.'; end if;
  if p_date is null or p_date < current_date - 1 or p_date > current_date + 1 then raise exception 'The kiosk date is wrong. Check the tablet clock.'; end if;
  select * into b from hx_badges where code = upper(trim(coalesce(p_code,'')));
  if b.profile_id is null or not b.active then return json_build_object('error', 'Badge not recognized.'); end if;
  select * into p from hx_profiles where id = b.profile_id;
  if not hx_person_at(p.id, p_lic) then
    return json_build_object('error', 'Not authorized at this license.', 'name', coalesce(nullif(p.name,''), p.email), 'photo', b.photo, 'title', b.title);
  end if;
  perform pg_advisory_xact_lock(hashtext('clock' || p.id::text || p_lic));
  select * into v_last from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided order by ts desc limit 1;
  if v_last.id is not null and v_now - v_last.ts < interval '60 seconds' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_last.event_type, 'ts', v_last.ts, 'late', v_last.late, 'late_minutes', v_last.late_minutes, 'repeat', true);
  end if;
  if v_last.id is null then v_next := 'entry';
  elsif v_last.event_type = 'clockout' then
    return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'done', true);
  else v_next := seq[array_position(seq, v_last.event_type) + 1];
  end if;
  if v_next in ('break1_in','break2_in','break3_in') then
    v_lim := hx_break_limit(p_lic, v_next);
    select * into v_out from hx_time_clock where profile_id = p.id and license_id = p_lic and event_date = p_date and not voided and event_type = replace(v_next, '_in', '_out') order by ts desc limit 1;
    if v_out.id is not null then
      v_el := extract(epoch from (v_now - v_out.ts)) / 60;
      v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end;
    end if;
  end if;
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', 'Badge scan', true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, recorded_by)
  values ('tc-' || replace(gen_random_uuid()::text,'-',''), p_state, p_lic, p.id, coalesce(nullif(p.name,''), p.email), v_next, v_now, p_date, v_late, v_lm, 'kiosk', 'Kiosk');
  perform set_config('hx.internal', '', true);
  return json_build_object('name', coalesce(nullif(p.name,''), p.email), 'title', b.title, 'photo', b.photo, 'event', v_next, 'ts', v_now, 'late', v_late, 'late_minutes', v_lm);
end $$;

create or replace function hx_clock_fix(p_lic text, p_profile uuid, p_date date, p_event text, p_ts timestamptz, p_reason text) returns text
language plpgsql volatile security definer set search_path = public as $$
declare v_state text; v_name text; v_id text; v_out record; v_lim int; v_el numeric; v_late boolean := false; v_lm int;
begin
  if not hx_can('timeclock', 3, p_lic) then raise exception 'Only Full access can add a missed punch.'; end if;
  if coalesce(trim(p_reason),'') = '' then raise exception 'A reason is required.'; end if;
  if not hx_person_at(p_profile, p_lic) then raise exception 'That person does not work at this license.'; end if;
  if p_ts > now() then raise exception 'The time cannot be in the future.'; end if;
  if exists (select 1 from hx_time_clock where profile_id = p_profile and license_id = p_lic and event_date = p_date and event_type = p_event and not voided) then
    raise exception 'That punch is already recorded for the day. Void it first to replace it.';
  end if;
  if p_event in ('break1_in','break2_in','break3_in') then
    v_lim := hx_break_limit(p_lic, p_event);
    select * into v_out from hx_time_clock where profile_id = p_profile and license_id = p_lic and event_date = p_date and not voided and event_type = replace(p_event, '_in', '_out') limit 1;
    if v_out.id is not null then v_el := extract(epoch from (p_ts - v_out.ts)) / 60; v_late := v_el > v_lim; v_lm := case when v_late then round(v_el - v_lim) else 0 end; end if;
  end if;
  select state_id into v_state from hx_licenses where id = p_lic;
  select coalesce(nullif(name,''), email) into v_name from hx_profiles where id = p_profile;
  v_id := 'tc-' || replace(gen_random_uuid()::text,'-','');
  perform set_config('hx.internal', 'on', true);
  perform set_config('hx.reason', 'Missed punch added: ' || trim(p_reason), true);
  insert into hx_time_clock(id, state_id, license_id, profile_id, person_name, event_type, ts, event_date, late, late_minutes, source, reason, recorded_by)
  values (v_id, v_state, p_lic, p_profile, v_name, p_event, p_ts, p_date, v_late, v_lm, 'manual', trim(p_reason), coalesce(hx_me(),''));
  perform set_config('hx.internal', '', true);
  return v_id;
end $$;

revoke all on function hx_kiosk_clock(text,text,text,date) from public;
revoke all on function hx_clock_fix(text,uuid,date,text,timestamptz,text) from public;
grant execute on function hx_kiosk_clock(text,text,text,date) to anon, authenticated;
grant execute on function hx_clock_fix(text,uuid,date,text,timestamptz,text) to authenticated;

notify pgrst, 'reload schema';


-- ###################################################################
-- ### hendrix_step36.sql
-- ###################################################################
-- =====================================================================
-- Hendrix QMS  -  Step 36: Production Line Map
-- A live "subway map" of production for general managers and executives:
-- every batch of the license sits at its real station (plan, line clearance,
-- the sections of its batch record, lab testing, QC release, labels,
-- shipped) and is shown as STOPPED with the reason when Hendrix sees:
--   * an open hold on the batch                         (Hold and Release)
--   * a failed test with no later passing test           (Testing)
--   * batch status QC Hold or Failed                     (Batch Tracker)
--   * no line clearance, or the last one not cleared     (Line Clearance)
--   * equipment of its line clearance out of service or
--     past its calibration date                          (Equipment)
--   * an open deviation raised from the batch            (QMS)
--   * a CCP reading out of limits not yet verified       (HACCP)
--   * no update for the license's idle time (default 4 h) (Settings)
--
-- The map reads all of this through ONE function, hx_line_map(license),
-- so a person needs only the new access module 'linemap' (View) for that
-- license - not access to every module behind it. The function returns
-- only what the map shows (no costs, no files, no personal data beyond
-- names already on the records).
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-34.
-- Safe to run more than once.
-- =====================================================================

-- ---------- idle time per license (Settings > Time clock / Line Map) ----------
alter table hx_license_settings add column if not exists linemap_idle_hours int not null default 4;
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'hx_license_settings_idle_chk') then
    alter table hx_license_settings add constraint hx_license_settings_idle_chk check (linemap_idle_hours between 1 and 72);
  end if;
end $$;

-- ---------- the bridge: one call returns everything the map needs ----------
create or replace function hx_line_map(p_lic text, p_days int default 45) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare
  v_lic   record;
  v_idle  int;
  v_since timestamptz;
  v_out   jsonb;
begin
  if p_lic is null or not hx_can('linemap', 1, p_lic) then
    raise exception 'You need access to the Line Map for this license.';
  end if;
  select l.id, l.name, l.license_number, l.state_id into v_lic from hx_licenses l where l.id = p_lic;
  if v_lic.id is null then raise exception 'Unknown license.'; end if;
  select s.linemap_idle_hours into v_idle from hx_license_settings s where s.license_id = p_lic;
  v_idle  := coalesce(v_idle, 4);
  v_since := now() - make_interval(days => greatest(7, least(coalesce(p_days, 45), 180)));

  select jsonb_build_object(
    'now', now(),
    'idle_hours', v_idle,
    'license', jsonb_build_object('id', v_lic.id, 'name', v_lic.name, 'license_number', v_lic.license_number),
    'batches', coalesce((
      select jsonb_agg(x order by x->>'created_at') from (
        select jsonb_build_object(
          'id', b.id, 'batch_type', b.batch_type, 'batch_number', b.batch_number, 'sku', b.sku, 'flavor', b.flavor,
          'status', b.status, 'data', b.data - 'notes', 'performed_by', b.performed_by,
          'created_at', b.created_at, 'updated_at', b.updated_at,
          'tests', coalesce((select jsonb_agg(jsonb_build_object('id', t.id, 'status', t.status, 'tag', t.tag, 'lab_name', t.lab_name,
                      'submitted_at', t.submitted_at, 'result_at', t.result_at, 'created_at', t.created_at, 'updated_at', t.updated_at) order by t.created_at)
                    from hx_tests t where t.batch_id = b.id and not t.voided), '[]'::jsonb),
          'holds', coalesce((select jsonb_agg(jsonb_build_object('id', h.id, 'number', h.number, 'reason', h.reason, 'status', h.status,
                      'created_at', h.created_at, 'placed_by', h.placed_by, 'decided_at', h.decided_at) order by h.created_at)
                    from hx_holds h where h.batch_id = b.id), '[]'::jsonb),
          'clearances', coalesce((select jsonb_agg(jsonb_build_object('id', c.id, 'number', c.number, 'result', c.result, 'area', c.area,
                      'equipment_ids', to_jsonb(c.equipment_ids), 'issues', c.issues, 'recorded_by', c.recorded_by, 'created_at', c.created_at) order by c.created_at)
                    from hx_line_clearances c where c.batch_id = b.id and not c.voided), '[]'::jsonb),
          'deviations', coalesce((select jsonb_agg(jsonb_build_object('id', d.id, 'number', d.number, 'title', d.title, 'status', d.status,
                      'owner_name', d.owner_name, 'created_at', d.created_at) order by d.created_at)
                    from hx_deviations d where d.source_type = 'batch' and d.source_id = b.id and d.status in ('open', 'in_progress')), '[]'::jsonb),
          'ccp_out', coalesce((select jsonb_agg(jsonb_build_object('id', m.id, 'ccp_name', m.ccp_name, 'value', m.value, 'created_at', m.created_at) order by m.created_at)
                    from hx_haccp_monitoring m where m.batch_id = b.id and not m.voided and not m.within_limits and m.verified_at is null), '[]'::jsonb),
          'labels', (select jsonb_build_object('count', count(*), 'last_at', max(lp.created_at))
                    from hx_label_prints lp where lp.license_id = b.license_id and lower(trim(lp.batch_number)) = lower(trim(b.batch_number))),
          'shipments', coalesce((select jsonb_agg(jsonb_build_object('id', s.id, 'number', s.number, 'customer', s.customer, 'ship_date', s.ship_date,
                      'status', s.status, 'created_at', s.created_at) order by s.created_at)
                    from hx_shipments s where s.license_id = b.license_id and s.status in ('shipped', 'delivered')
                      and exists (select 1 from jsonb_array_elements(s.items) it where it->>'batch_id' = b.id)), '[]'::jsonb),
          'last_activity', greatest(b.updated_at,
                    (select max(c.created_at) from hx_line_clearances c where c.batch_id = b.id),
                    (select max(t.updated_at) from hx_tests t where t.batch_id = b.id),
                    (select max(m.created_at) from hx_haccp_monitoring m where m.batch_id = b.id))
        ) x
        from hx_batches b
        where b.license_id = p_lic and not b.voided and b.created_at >= v_since
      ) q), '[]'::jsonb),
    'equipment_issues', coalesce((
      select jsonb_agg(jsonb_build_object('id', e.id, 'number', e.number, 'name', e.name, 'status', e.status, 'cal_due', e.cal_due,
               'issue', case when e.status <> 'in_service' then 'out of service'
                             else 'past its calibration date (' || to_char(e.cal_due, 'Mon DD') || ')' end))
      from hx_equipment e
      where e.license_id = p_lic and (e.status <> 'in_service' or (e.cal_required and e.cal_due is not null and e.cal_due < current_date))), '[]'::jsonb),
    'plans', coalesce((
      select jsonb_agg(jsonb_build_object('id', pp.id, 'number', pp.number, 'product_type', pp.product_type, 'sku_name', pp.sku_name,
               'planned_for', pp.planned_for, 'units_per_flavor', pp.units_per_flavor, 'status', pp.status, 'created_at', pp.created_at,
               'flavors', coalesce((select jsonb_agg(li->>'flavor') from jsonb_array_elements(pp.lines) li where coalesce(li->>'flavor', '') <> ''), '[]'::jsonb))
             order by pp.planned_for nulls last, pp.created_at)
      from hx_production_plans pp where pp.license_id = p_lic and pp.status = 'planned'), '[]'::jsonb),
    'on_floor', (
      select count(*) from (
        select distinct on (tc.profile_id) tc.event_type, tc.ts
        from hx_time_clock tc
        where tc.license_id = p_lic and not tc.voided and tc.ts > now() - interval '16 hours'
        order by tc.profile_id, tc.ts desc
      ) z where z.event_type <> 'clockout')
  ) into v_out;
  return v_out;
end $$;

revoke all on function hx_line_map(text, int) from public, anon;
grant execute on function hx_line_map(text, int) to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 36 (Production Line Map) installed' as result;


notify pgrst, 'reload schema';
select 'Hendrix steps 13-36 installed' as result;
