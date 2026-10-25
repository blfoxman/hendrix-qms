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
