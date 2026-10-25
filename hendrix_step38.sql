-- =====================================================================
-- Hendrix QMS  -  Step 38: Security - electronic signatures, auto sign-out,
--                  two-step sign-in (21 CFR Part 11 benchmark)
--
--   * Electronic signatures: when a license has "Ask for the password when
--     signing" on (default ON), Hendrix asks for the person's password (and the
--     authenticator code when two-step sign-in is on) before an approval,
--     release, decision or signature. Every confirmed signature is kept in
--     hx_esignatures: who (from the sign-in, never typed), what record, the
--     meaning ("Approved", "Released", ...) and the server time. Signatures are
--     permanent: they cannot be changed or deleted.
--   * Auto sign-out: each license sets the minutes without activity after which
--     Hendrix signs the person out (default 30, 0 = never). Kiosks are not affected.
--   * Two-step sign-in (authenticator app, TOTP): an admin can require it for a
--     person (Team and Access), and anyone can turn it on for themselves (My
--     account). While it is required, the database gives that person NO access
--     until they sign in with the second step (session level aal2). Only an admin
--     can turn the requirement off again.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-37.
-- Supabase > Authentication > Multi-factor: TOTP must be enabled (it is by default).
-- Safe to run more than once.
-- =====================================================================

-- ---------- settings per license ----------
alter table hx_license_settings add column if not exists esig_password boolean not null default true;
alter table hx_license_settings add column if not exists idle_signout_min int not null default 30;
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'hx_license_settings_idle_signout_chk') then
    alter table hx_license_settings add constraint hx_license_settings_idle_signout_chk check (idle_signout_min between 0 and 480);
  end if;
end $$;

-- every license gets its settings row (so the secure defaults apply everywhere), now and when a license is added
alter table hx_license_settings disable trigger hx_license_settings_guard;
insert into hx_license_settings(license_id, state_id) select l.id, l.state_id from hx_licenses l
  where not exists (select 1 from hx_license_settings s where s.license_id = l.id);
alter table hx_license_settings enable trigger hx_license_settings_guard;
create or replace function hx_license_new_settings() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into hx_license_settings(license_id, state_id) values (new.id, new.state_id) on conflict (license_id) do nothing;
  return new;
end $$;
drop trigger if exists hx_licenses_new_settings on hx_licenses;
create trigger hx_licenses_new_settings after insert on hx_licenses for each row execute function hx_license_new_settings();

-- ---------- two-step sign-in ----------
alter table hx_profiles add column if not exists mfa_required boolean not null default false;

-- the session's assurance level from the sign-in token: aal1 = password, aal2 = password + authenticator
create or replace function hx_aal() returns text
language sql stable as $$
  select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'aal', 'aal1');
$$;
-- true when the signed-in person does not need two-step sign-in, or has completed it
create or replace function hx_mfa_ok() returns boolean
language sql stable security definer set search_path = public as $$
  select not coalesce((select p.mfa_required from hx_profiles p where p.id::text = auth.uid()::text), false) or hx_aal() = 'aal2';
$$;

create or replace function hx_fl_is_approved() returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from hx_profiles where id::text = auth.uid()::text and approved = true) and hx_mfa_ok();
$$;
create or replace function hx_fl_is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select exists(select 1 from hx_profiles where id::text = auth.uid()::text and approved = true and role = 'admin') and hx_mfa_ok();
$$;
create or replace function hx_perm(p_mod text) returns int
language plpgsql stable security definer set search_path = public as $$
declare p record; v int; v_child boolean := p_mod like 'logs\_%';
begin
  select * into p from hx_profiles where id::text = auth.uid()::text;
  if p.id is null or not coalesce(p.approved, false) then return 0; end if;
  if coalesce(p.mfa_required, false) and hx_aal() <> 'aal2' then return 0; end if;
  if p.role = 'admin' then return 3; end if;
  if coalesce(p.perms, '{}'::jsonb) ? p_mod then return hx_rank(p.perms ->> p_mod); end if;
  if v_child and coalesce(p.perms, '{}'::jsonb) ? 'logs' then return hx_rank(p.perms ->> 'logs'); end if;
  select coalesce(max(hx_rank(coalesce(r.perms ->> p_mod, case when v_child then r.perms ->> 'logs' end))), 0)
    into v from hx_roles r where r.id = any(p.role_ids);
  return v;
end $$;
create or replace function hx_lic_ok(p_lic text) returns boolean
language plpgsql stable security definer set search_path = public as $$
declare p record;
begin
  select * into p from hx_profiles where id::text = auth.uid()::text;
  if p.id is null or not coalesce(p.approved, false) then return false; end if;
  if coalesce(p.mfa_required, false) and hx_aal() <> 'aal2' then return false; end if;
  if p.role = 'admin' or coalesce(array_length(p.license_ids, 1), 0) = 0 then return true; end if;
  return p_lic = any(p.license_ids);
end $$;

-- who may change mfa_required: an admin either way; the person themselves only to turn it ON
create or replace function hx_profile_mfa_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.mfa_required is distinct from old.mfa_required and auth.uid() is not null then
    if not hx_fl_is_admin()
       and not (new.id::text = auth.uid()::text and new.mfa_required) then
      raise exception 'Only an admin can turn off two-step sign-in.';
    end if;
  end if;
  return new;
end $$;
drop trigger if exists hx_profiles_mfa_guard on hx_profiles;
create trigger hx_profiles_mfa_guard before update on hx_profiles for each row execute function hx_profile_mfa_guard();

-- ---------- electronic signatures ----------
create table if not exists hx_esignatures (
  id            text primary key,
  state_id      text not null references hx_states(id),
  license_id    text not null references hx_licenses(id),
  user_id       uuid,
  signer_name   text not null default '',
  signer_email  text not null default '',
  meaning       text not null check (length(trim(meaning)) > 0),
  record_table  text not null default '',
  record_id     text not null default '',
  record_label  text not null default '',
  method        text not null default 'password' check (method in ('password','password+authenticator')),
  signed_at     timestamptz not null default now()
);
create index if not exists hx_esignatures_lic on hx_esignatures(license_id, signed_at desc);
create index if not exists hx_esignatures_rec on hx_esignatures(record_table, record_id);

create or replace function hx_esig_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare p record;
begin
  if tg_op <> 'INSERT' then raise exception 'Electronic signatures are permanent: they cannot be changed or deleted.'; end if;
  if auth.uid() is null then raise exception 'Sign in to sign.'; end if;
  select * into p from hx_profiles where id::text = auth.uid()::text;
  if p.id is null or not coalesce(p.approved, false) or not hx_lic_ok(new.license_id) then raise exception 'You cannot sign records of this license.'; end if;
  -- the signer is always the signed-in person, with the server time
  new.user_id := auth.uid(); new.signer_name := coalesce(p.name, ''); new.signer_email := coalesce(p.email, ''); new.signed_at := now();
  new.method := case when hx_aal() = 'aal2' then 'password+authenticator' else 'password' end;
  return new;
end $$;
drop trigger if exists hx_esignatures_guard on hx_esignatures;
create trigger hx_esignatures_guard before insert or update or delete on hx_esignatures for each row execute function hx_esig_guard();
drop trigger if exists hx_esignatures_place on hx_esignatures;
create trigger hx_esignatures_place before insert on hx_esignatures for each row execute function hx_fl_guard();

alter table hx_esignatures enable row level security;
drop policy if exists hx_esignatures_read on hx_esignatures;
drop policy if exists hx_esignatures_insert on hx_esignatures;
create policy hx_esignatures_read on hx_esignatures for select to authenticated
  using (hx_lic_ok(license_id) and (user_id = auth.uid() or hx_perm('audit') >= 1));
create policy hx_esignatures_insert on hx_esignatures for insert to authenticated with check (hx_lic_ok(license_id));
revoke all on hx_esignatures from anon;
grant select, insert on hx_esignatures to authenticated;

-- the app asks this right after sign-in (it works before the second step is done)
create or replace function hx_my_security() returns jsonb
language sql stable security definer set search_path = public as $$
  select jsonb_build_object('approved', coalesce(p.approved, false), 'mfa_required', coalesce(p.mfa_required, false), 'aal', hx_aal(), 'name', p.name)
  from hx_profiles p where p.id::text = auth.uid()::text;
$$;
revoke all on function hx_my_security() from public, anon;
grant execute on function hx_my_security() to authenticated;
grant execute on function hx_aal() to authenticated;
grant execute on function hx_mfa_ok() to authenticated;

-- System Health: steps list now ends at 38
drop trigger if exists hx_esignatures_audit on hx_esignatures;
create trigger hx_esignatures_audit after insert on hx_esignatures for each row execute function hx_audit();

create or replace function hx_health_extra() returns jsonb
language plpgsql stable security definer set search_path = public as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only an admin can run the system health check.'; end if;
  return jsonb_build_object(
    'step38', to_regclass('public.hx_esignatures') is not null,
    'admins_without_2fa', (select count(*) from hx_profiles where approved and role = 'admin' and not mfa_required),
    'esig_off_licenses', coalesce((select jsonb_agg(l.name) from hx_licenses l left join hx_license_settings s on s.license_id = l.id
                                    where l.active and s.license_id is not null and not s.esig_password), '[]'::jsonb),
    'signatures', (select count(*) from hx_esignatures));
end $$;
revoke all on function hx_health_extra() from public, anon;
grant execute on function hx_health_extra() to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 38 (Security: e-signatures, auto sign-out, two-step sign-in) installed' as result;
