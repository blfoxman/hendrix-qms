-- =====================================================================
-- Hendrix QMS  -  Step 68: Training Center (hendrixqms.com/training)
--
--   * The Training Center signs people in with their company address, email and password,
--     then asks Hendrix who they are: name, job title and what they can open.
--   * Title = the title on their badge (Time Clock and Badges), else their Org Chart position.
--   * Access = the same levels Hendrix itself uses (0 none, 1 view, 2 edit, 3 full) for each
--     area the Training Center asks about. Two-step sign-in is respected: until the person
--     enters the authenticator code, they get no access (and the answer says so).
--
-- Run in the Hendrix Supabase project AFTER steps 1-67. Safe to run more than once.
-- =====================================================================

create or replace function hx_my_training_profile(p_modules text[]) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare p hx_profiles; v_title text; acc jsonb := '{}'::jsonb; m text; v_mfa boolean;
begin
  if auth.uid() is null then raise exception 'Sign in first.'; end if;
  select * into p from hx_profiles where id = auth.uid();
  if not found then raise exception 'There is no Hendrix profile for this account.'; end if;
  if not coalesce(p.approved, false) then
    return jsonb_build_object('approved', false, 'name', coalesce(nullif(p.name, ''), p.email));
  end if;
  v_mfa := coalesce(p.mfa_required, false) and hx_aal() <> 'aal2';
  select nullif(btrim(b.title), '') into v_title from hx_badges b where b.profile_id = p.id and b.active limit 1;
  if v_title is null then
    select nullif(btrim(o.title), '') into v_title from hx_org_positions o where o.user_id = p.id::text order by o.sort, o.title limit 1;
  end if;
  if coalesce(array_length(p_modules, 1), 0) > 80 then raise exception 'Too many areas asked for.'; end if;
  foreach m in array coalesce(p_modules, '{}'::text[]) loop
    if m ~ '^[a-z_]{2,40}$' then acc := acc || jsonb_build_object(m, case when v_mfa then 0 else hx_perm(m) end); end if;
  end loop;
  return jsonb_build_object('approved', true, 'name', coalesce(nullif(p.name, ''), p.email), 'title', coalesce(v_title, ''),
    'admin', p.role = 'admin' and not v_mfa, 'mfa_needed', v_mfa, 'access', acc);
end $$;
revoke all on function hx_my_training_profile(text[]) from public, anon;
grant execute on function hx_my_training_profile(text[]) to authenticated;

notify pgrst, 'reload schema';
