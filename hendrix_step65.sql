-- =====================================================================
-- Hendrix QMS  -  Step 65: old urgent alerts expire instead of waiting forever
--
--   * Urgent alert emails go out only while the alert is less than 3 days old. An older one
--     (for example a hold placed before email was set up) is now closed out and shown in
--     Settings > Email as "expired" - the item itself stays on My Tasks and the daily list.
--   * Clears the System Health warning "Urgent alerts going out" for such old alerts.
--
-- Run in the Hendrix Supabase project (bqrncllndvzbhmxanitq) AFTER steps 1-64.
-- Safe to run more than once.
-- =====================================================================

create or replace function hx_notify_pending() returns jsonb
language plpgsql security definer set search_path = public as $$
declare q record; p record; r jsonb; out jsonb := '[]'::jsonb; lic record;
  c0 text := current_setting('request.jwt.claims', true); s0 text := current_setting('request.jwt.claim.sub', true); u0 text := current_setting('test.uid', true);
begin
  perform hx_notify_service_only();
  -- alerts older than 3 days are old news: close them out (logged as expired) instead of leaving them waiting forever
  insert into hx_notify_log(kind, email, subject, items, status, error)
    select 'alert', '', left(title, 300), 1, 'expired', 'Not emailed: it was more than 3 days old when email could send it. It stays on My Tasks.'
      from hx_notify_queue where sent_at is null and created_at <= now() - interval '3 days';
  update hx_notify_queue set sent_at = now(), recipients = 0 where sent_at is null and created_at <= now() - interval '3 days';
  for q in select * from hx_notify_queue where sent_at is null and created_at > now() - interval '3 days' order by id limit 200 loop
    r := '[]'::jsonb;
    for p in select * from hx_profiles where approved and coalesce(email, '') like '%@%' order by name loop
      perform hx_as_user(p.id);
      if hx_lic_ok(q.license_id) and hx_perm(q.module) >= 3 then r := r || jsonb_build_object('name', p.name, 'email', p.email); end if;
    end loop;
    select x.name, x.license_number, s.name as state into lic from hx_licenses x join hx_states s on s.id = x.state_id where x.id = q.license_id;
    out := out || jsonb_build_object('id', q.id, 'kind', q.kind, 'title', q.title, 'detail', q.detail, 'page', q.page, 'license', lic.name, 'license_number', lic.license_number,
                                     'state', lic.state, 'license_id', q.license_id, 'created_at', q.created_at, 'recipients', r);
  end loop;
  perform set_config('request.jwt.claims', coalesce(c0, ''), true); perform set_config('request.jwt.claim.sub', coalesce(s0, ''), true); perform set_config('test.uid', coalesce(u0, ''), true);
  return out;
end $$;
revoke all on function hx_notify_pending() from public, anon, authenticated;
do $$ begin
  if exists (select 1 from pg_roles where rolname = 'service_role') then
    execute 'grant execute on function hx_notify_pending() to service_role';
  end if;
end $$;

-- close out the ones already waiting
insert into hx_notify_log(kind, email, subject, items, status, error)
  select 'alert', '', left(title, 300), 1, 'expired', 'Not emailed: it was more than 3 days old when email could send it. It stays on My Tasks.'
    from hx_notify_queue where sent_at is null and created_at <= now() - interval '3 days';
update hx_notify_queue set sent_at = now(), recipients = 0 where sent_at is null and created_at <= now() - interval '3 days';

notify pgrst, 'reload schema';
