-- =====================================================================
-- Hendrix QMS  -  Step 42: admin sets a temporary password
--
--   Until email is set up, a person who forgot their password asks an admin.
--   Team and Access > Manage > "Set a temporary password": the admin types (or
--   generates) a temporary password and gives it to the person in person.
--   * the person's other open sessions are signed out;
--   * at the next sign-in Hendrix makes the person choose their own new
--     password before anything else opens (must_change_password);
--   * the reset is in the Audit Trail ("Password reset by an admin"); the
--     password itself is never stored by Hendrix, only its hash in Supabase Auth.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-41.
-- Safe to run more than once.
-- =====================================================================

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;
alter table hx_profiles add column if not exists must_change_password boolean not null default false;

create or replace function hx_admin_set_password(p_user uuid, p_password text) returns boolean
language plpgsql volatile security definer set search_path = public, extensions as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only a system admin can set a temporary password.'; end if;
  if length(coalesce(p_password, '')) < 8 then raise exception 'The temporary password needs at least 8 characters.'; end if;
  if length(p_password) > 72 then raise exception 'The temporary password can have at most 72 characters.'; end if;
  if not exists (select 1 from hx_profiles where id = p_user) then raise exception 'Unknown person.'; end if;
  update auth.users set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf', 10)), updated_at = now() where id = p_user;
  if not found then raise exception 'This person has no sign-in account.'; end if;
  -- sign the person out everywhere else
  begin execute 'delete from auth.sessions where user_id = $1' using p_user; exception when undefined_table then null; end;
  begin execute 'delete from auth.refresh_tokens where user_id = $1::text' using p_user; exception when undefined_table or undefined_column then null; end;
  perform set_config('hx.reason', 'Password reset by an admin', true);
  update hx_profiles set must_change_password = (p_user::text <> auth.uid()::text) where id = p_user;
  return true;
end $$;
revoke all on function hx_admin_set_password(uuid, text) from public, anon;
grant execute on function hx_admin_set_password(uuid, text) to authenticated;

-- the person chose their own password: clear the flag (the app calls this after changing the password)
create or replace function hx_password_changed() returns boolean
language plpgsql volatile security definer set search_path = public as $$
begin
  if auth.uid() is null then raise exception 'Sign in first.'; end if;
  if exists (select 1 from hx_profiles where id::text = auth.uid()::text and must_change_password) then
    perform set_config('hx.reason', 'New password chosen after a reset', true);
    update hx_profiles set must_change_password = false where id::text = auth.uid()::text;
  end if;
  return true;
end $$;
revoke all on function hx_password_changed() from public, anon;
grant execute on function hx_password_changed() to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 42 (admin sets a temporary password) installed' as result;
