-- =====================================================================
-- Hendrix QMS  -  Step 51: remove a person from Hendrix (and delete sign-up requests)
--
--   Team and Access > Manage > "Remove from Hendrix" (system admins):
--     the person can no longer sign in (sign-in account blocked, signed out everywhere),
--     loses approval, admin rights, roles and custom access, and moves to the "Removed" list
--     with the date, who removed them and why. Everything they signed or recorded stays,
--     with their name, as the records require. "Restore" lets them sign in again
--     (an admin then approves them and gives access again).
--   A sign-up request that was never approved can be deleted completely.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-50.
-- Safe to run more than once.
-- =====================================================================

alter table hx_profiles add column if not exists removed_at timestamptz;
alter table hx_profiles add column if not exists removed_by text;
alter table hx_profiles add column if not exists removed_reason text;

create or replace function hx_admin_remove_user(p_user uuid, p_reason text) returns boolean
language plpgsql volatile security definer set search_path = public as $$
declare v_me text; v_reason text := nullif(trim(coalesce(p_reason, '')), '');
begin
  if not hx_fl_is_admin() then raise exception 'Only a system admin can remove someone from Hendrix.'; end if;
  if p_user::text = auth.uid()::text then raise exception 'You cannot remove yourself.'; end if;
  if v_reason is null then raise exception 'Write why this person is removed (for example: left the company).'; end if;
  if not exists (select 1 from hx_profiles where id = p_user) then raise exception 'Unknown person.'; end if;
  select coalesce(nullif(name, ''), email) into v_me from hx_profiles where id::text = auth.uid()::text;
  perform set_config('hx.reason', 'Removed from Hendrix: ' || v_reason, true);
  update hx_profiles set approved = false, role = 'member', role_ids = '{}', perms = '{}',
         removed_at = now(), removed_by = v_me, removed_reason = v_reason where id = p_user;
  -- block the sign-in account and sign the person out everywhere
  begin execute 'update auth.users set banned_until = ''infinity''::timestamptz where id = $1' using p_user; exception when undefined_column or undefined_table then null; end;
  begin execute 'delete from auth.sessions where user_id = $1' using p_user; exception when undefined_table then null; end;
  begin execute 'delete from auth.refresh_tokens where user_id = $1::text' using p_user; exception when undefined_table or undefined_column then null; end;
  return true;
end $$;
revoke all on function hx_admin_remove_user(uuid, text) from public, anon;
grant execute on function hx_admin_remove_user(uuid, text) to authenticated;

create or replace function hx_admin_restore_user(p_user uuid) returns boolean
language plpgsql volatile security definer set search_path = public as $$
begin
  if not hx_fl_is_admin() then raise exception 'Only a system admin can restore someone.'; end if;
  perform set_config('hx.reason', 'Restored to Hendrix (waiting for approval)', true);
  update hx_profiles set removed_at = null, removed_by = null, removed_reason = null where id = p_user and removed_at is not null;
  if not found then raise exception 'This person is not removed.'; end if;
  begin execute 'update auth.users set banned_until = null where id = $1' using p_user; exception when undefined_column or undefined_table then null; end;
  return true;
end $$;
revoke all on function hx_admin_restore_user(uuid) from public, anon;
grant execute on function hx_admin_restore_user(uuid) to authenticated;

-- a sign-up that was never approved and has no records: delete the account completely
create or replace function hx_admin_delete_request(p_user uuid) returns boolean
language plpgsql volatile security definer set search_path = public as $$
declare p hx_profiles;
begin
  if not hx_fl_is_admin() then raise exception 'Only a system admin can delete a sign-up request.'; end if;
  select * into p from hx_profiles where id = p_user;
  if not found then raise exception 'Unknown person.'; end if;
  if p.approved or p.removed_at is not null then raise exception 'Only a sign-up request that was never approved can be deleted. Use "Remove from Hendrix" for anyone who has worked in Hendrix.'; end if;
  if exists (select 1 from hx_audit_log where user_id = p_user and table_name <> 'hx_profiles') then
    raise exception 'This person already has records in Hendrix. Use "Remove from Hendrix" so the records keep their name.';
  end if;
  perform set_config('hx.reason', 'Sign-up request deleted', true);
  delete from hx_profiles where id = p_user;
  begin execute 'delete from auth.users where id = $1' using p_user; exception when undefined_table then null; end;
  return true;
end $$;
revoke all on function hx_admin_delete_request(uuid) from public, anon;
grant execute on function hx_admin_delete_request(uuid) to authenticated;

notify pgrst, 'reload schema';
select 'Hendrix step 51 (remove from Hendrix) installed' as result;
