\set ON_ERROR_STOP 0
-- step 42: admin sets a temporary password
update hx_profiles set role='member', approved=true, mfa_required=false where id='22222222-2222-2222-2222-222222222222';
set test.uid='22222222-2222-2222-2222-222222222222';
select hx_admin_set_password('11111111-1111-1111-1111-111111111111','Hacked-123');
set test.uid='11111111-1111-1111-1111-111111111111';
select hx_admin_set_password('22222222-2222-2222-2222-222222222222','short');
select 'P1 set', hx_admin_set_password('22222222-2222-2222-2222-222222222222','Temp-Pass-2026');
select 'P2 hash', encrypted_password like '$2a$10$%', encrypted_password = extensions.crypt('Temp-Pass-2026', encrypted_password), encrypted_password <> 'Temp-Pass-2026' from auth.users where id='22222222-2222-2222-2222-222222222222';
select 'P3 signed out', (select count(*) from auth.sessions where user_id='22222222-2222-2222-2222-222222222222'), (select count(*) from auth.refresh_tokens where user_id='22222222-2222-2222-2222-222222222222'), (select count(*) from auth.sessions where user_id='11111111-1111-1111-1111-111111111111');
select 'P4 must change', must_change_password from hx_profiles where id='22222222-2222-2222-2222-222222222222';
select 'P5 audit', count(*) > 0 from hx_audit_log where table_name='hx_profiles' and row_id='22222222-2222-2222-2222-222222222222' and reason='Password reset by an admin';
set test.uid='22222222-2222-2222-2222-222222222222';
select hx_password_changed();
select 'P6 changed', must_change_password from hx_profiles where id='22222222-2222-2222-2222-222222222222';
set test.uid='11111111-1111-1111-1111-111111111111';
select hx_admin_set_password('99999999-9999-9999-9999-999999999999','Temp-Pass-2026');
select 'P7 own', hx_admin_set_password('11111111-1111-1111-1111-111111111111','Own-Pass-2026'), (select must_change_password from hx_profiles where id='11111111-1111-1111-1111-111111111111');
