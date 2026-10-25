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
