\set ON_ERROR_STOP 0
-- step 45: new password after an admin reset, without the current password
update hx_profiles set role='member', approved=true, mfa_required=false where id='22222222-2222-2222-2222-222222222222';
set test.uid='11111111-1111-1111-1111-111111111111';
select 'Q0 reset', hx_admin_set_password('22222222-2222-2222-2222-222222222222','Temp-Pass-2026');
reset test.uid;
select hx_set_own_password('Mine-Pass-2026');
set test.uid='22222222-2222-2222-2222-222222222222';
select hx_set_own_password('short');
select hx_set_own_password('Temp-Pass-2026');
select 'Q1 set', hx_set_own_password('Mine-Pass-2026');
select 'Q2 hash', encrypted_password = extensions.crypt('Mine-Pass-2026', encrypted_password) from auth.users where id='22222222-2222-2222-2222-222222222222';
select 'Q3 flag', must_change_password from hx_profiles where id='22222222-2222-2222-2222-222222222222';
select 'Q4 audit', count(*) > 0 from hx_audit_log where table_name='hx_profiles' and row_id='22222222-2222-2222-2222-222222222222' and reason='New password chosen after a reset';
select hx_set_own_password('Again-Pass-2026');
