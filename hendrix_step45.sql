-- =====================================================================
-- Hendrix QMS  -  Step 45: choose a new password after an admin reset, without the current password
--
--   When Supabase Auth has "Secure password change" on, a normal password change
--   asks for the current password. After an admin set a temporary password the
--   person should not need it again: hx_set_own_password sets the new password on
--   the server, but ONLY while the account is flagged "must change password"
--   (set by hx_admin_set_password, step 42). The flag is cleared at once, so the
--   function cannot be used again until an admin resets the password again.
--   The change is in the Audit Trail ("New password chosen after a reset").
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-44.
-- Safe to run more than once.
-- =====================================================================

create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;

create or replace function hx_set_own_password(p_password text) returns boolean
language plpgsql volatile security definer set search_path = public, extensions as $$
declare v_uid uuid := nullif(auth.uid()::text, '')::uuid;
begin
  if v_uid is null then raise exception 'Sign in first.'; end if;
  if not exists (select 1 from hx_profiles where id = v_uid and must_change_password) then
    raise exception 'No temporary password to replace. Change your password under My account.';
  end if;
  if length(coalesce(p_password, '')) < 8 then raise exception 'Use at least 8 characters.'; end if;
  if length(p_password) > 72 then raise exception 'Use at most 72 characters.'; end if;
  if exists (select 1 from auth.users where id = v_uid and encrypted_password = extensions.crypt(p_password, encrypted_password)) then
    raise exception 'Choose a password different from the temporary one.';
  end if;
  update auth.users set encrypted_password = extensions.crypt(p_password, extensions.gen_salt('bf', 10)), updated_at = now() where id = v_uid;
  if not found then raise exception 'This person has no sign-in account.'; end if;
  perform set_config('hx.reason', 'New password chosen after a reset', true);
  update hx_profiles set must_change_password = false where id = v_uid;
  return true;
end $$;
revoke all on function hx_set_own_password(text) from public, anon;
grant execute on function hx_set_own_password(text) to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 45 (new password after a reset, no current password) installed' as result;
