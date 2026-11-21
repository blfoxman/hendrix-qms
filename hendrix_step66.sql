-- Hendrix QMS - step 66: people change their own sign-in email
-- When someone changes their email (My account > Email address) and opens the confirmation link,
-- Supabase updates auth.users. This copies the new email to their Hendrix profile, so task lists,
-- urgent alerts and the team list use the new address.
-- Safe to run more than once.

-- 1. copy the new email to hx_profiles (never blocks the sign-in service: any problem is skipped)
create or replace function public.hx_auth_email_sync() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if new.email is distinct from old.email and coalesce(new.email, '') <> '' then
    begin
      update public.hx_profiles set email = new.email where id = new.id and email is distinct from new.email;
    exception when others then
      raise warning 'hx_auth_email_sync skipped: %', sqlerrm;
    end;
  end if;
  return new;
end $$;

do $$ begin
  execute 'drop trigger if exists hx_auth_email_sync on auth.users';
  execute 'create trigger hx_auth_email_sync after update of email on auth.users for each row execute function public.hx_auth_email_sync()';
exception when insufficient_privilege then
  raise notice 'Could not add the trigger on auth.users; the app copies the email with hx_sync_my_email() instead.';
end $$;

-- 2. the app also calls this after sign-in when the two emails differ (works even without the trigger)
create or replace function public.hx_sync_my_email() returns text
language plpgsql security definer set search_path = public as $$
declare v_em text;
begin
  if auth.uid() is null then return null; end if;
  select email into v_em from auth.users where id = auth.uid();
  if coalesce(v_em, '') = '' then return null; end if;
  update hx_profiles set email = v_em where id = auth.uid() and email is distinct from v_em;
  return v_em;
end $$;
revoke all on function public.hx_sync_my_email() from public, anon;
grant execute on function public.hx_sync_my_email() to authenticated;

-- 3. one time: catch up anyone whose email already changed
update hx_profiles p set email = u.email
from auth.users u
where u.id = p.id and coalesce(u.email, '') <> '' and p.email is distinct from u.email;

notify pgrst, 'reload schema';
