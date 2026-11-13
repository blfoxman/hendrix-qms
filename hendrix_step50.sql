-- =====================================================================
-- Hendrix QMS  -  Step 50: paper SOP records (effective date and signatures on paper)
--
--   For SOPs that were in use, and signed by staff, on paper before they were in Hendrix.
--   SOPs page > "Paper records" (Full access to SOPs): pick the SOPs, the date on the paper,
--   and the people who signed the paper copies.
--     * each chosen published SOP: effective date = that date, next review one year later
--     * each chosen person: their signature for the current version is marked
--       "signed on paper <date>", with who entered it and when (hx_sop_acks.paper_on,
--       paper_by, paper_note). A Hendrix e-signature they already made keeps its own time;
--       a person who has not signed in Hendrix gets a paper signature (no drawn signature).
--   Everything is in the Audit Trail with the reason. Signatures stay permanent otherwise.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-49.
-- Safe to run more than once.
-- =====================================================================

alter table hx_sop_acks add column if not exists paper_on date;
alter table hx_sop_acks add column if not exists paper_by text;
alter table hx_sop_acks add column if not exists paper_note text;

create or replace function hx_sop_ack_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare s record; v_name text; v_roles text;
begin
  -- paper signatures are entered only through hx_sop_paper_records (Full access to SOPs)
  if current_setting('hx.paper', true) = '1' and tg_op <> 'DELETE' then return new; end if;
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

drop trigger if exists hx_sop_acks_audit on hx_sop_acks;
create trigger hx_sop_acks_audit after insert or update on hx_sop_acks for each row execute function hx_audit();

create or replace function hx_sop_paper_records(p_license text, p_on date, p_sop_ids text[], p_user_ids uuid[], p_note text default '')
returns jsonb language plpgsql security definer set search_path = public as $$
declare v_me text; s record; u record; n_sop int := 0; n_new int := 0; n_upd int := 0; v_note text := nullif(trim(coalesce(p_note, '')), '');
begin
  if not hx_can('sops', 3, p_license) then raise exception 'Only someone with Full access to SOPs can enter paper records.'; end if;
  if p_on is null or p_on > current_date then raise exception 'Enter the date written on the paper (not a future date).'; end if;
  if coalesce(array_length(p_sop_ids, 1), 0) = 0 then raise exception 'Pick at least one SOP.'; end if;
  select coalesce(nullif(name, ''), email) into v_me from hx_profiles where id::text = auth.uid()::text;
  perform set_config('hx.paper', '1', true);
  for s in select * from hx_sops where id = any(p_sop_ids) and status = 'published' and p_license = any(license_ids) loop
    perform set_config('hx.reason', 'Effective date from the paper SOP: ' || to_char(p_on, 'YYYY-MM-DD') || coalesce(' (' || v_note || ')', ''), true);
    update hx_sops set effective_date = p_on, next_review = (p_on + interval '1 year')::date where id = s.id;
    n_sop := n_sop + 1;
    for u in select p.id, coalesce(nullif(p.name, ''), p.email) as nm,
                    coalesce((select string_agg(r.name, ', ' order by r.name) from hx_roles r where r.id = any(p.role_ids)), '') as roles
               from hx_profiles p where p.id = any(coalesce(p_user_ids, '{}')) loop
      perform set_config('hx.reason', 'Signed on paper ' || to_char(p_on, 'YYYY-MM-DD') || ', entered by ' || coalesce(v_me, '') || coalesce(' (' || v_note || ')', ''), true);
      update hx_sop_acks set paper_on = p_on, paper_by = v_me, paper_note = v_note where sop_id = s.id and version = s.version and user_id = u.id;
      if found then n_upd := n_upd + 1;
      else
        insert into hx_sop_acks(id, sop_id, state_id, license_id, version, user_id, name, role_names, signature, at, paper_on, paper_by, paper_note)
        values ('ackp-' || substr(md5(s.id || s.version || u.id::text), 1, 16), s.id, s.state_id, p_license, s.version, u.id, u.nm, u.roles, null, now(), p_on, v_me, v_note);
        n_new := n_new + 1;
      end if;
    end loop;
  end loop;
  perform set_config('hx.paper', '', true);
  return jsonb_build_object('sops', n_sop, 'new', n_new, 'updated', n_upd);
end $$;
grant execute on function hx_sop_paper_records(text, date, text[], uuid[], text) to authenticated;

-- the training matrix counts a paper signature from the date on the paper
create or replace function hx_training_sop_acks(p_lic text) returns table(sop_id text, version text, user_id text, at timestamptz)
language sql stable security definer set search_path = public as $$
  select a.sop_id, a.version, a.user_id::text, coalesce(a.paper_on::timestamptz, a.at) from hx_sop_acks a join hx_sops s on s.id = a.sop_id
   where p_lic = any(s.license_ids) and hx_can('training',1,p_lic)
     and (hx_perm('training') >= 2 or a.user_id = auth.uid());
$$;
grant execute on function hx_training_sop_acks(text) to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 50 (paper SOP records) installed' as result;
