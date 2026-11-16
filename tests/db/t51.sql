\set ON_ERROR_STOP 0
-- step 51: remove from Hendrix, restore, delete a sign-up request
alter table auth.users add column if not exists banned_until timestamptz;
set session_replication_role=replica;
delete from hx_profiles where id in ('51515151-0000-0000-0000-000000000001','51515151-0000-0000-0000-000000000002');
delete from auth.users where id in ('51515151-0000-0000-0000-000000000001','51515151-0000-0000-0000-000000000002');
insert into hx_profiles(id,name,email,role,approved,role_ids,perms) values
  ('51515151-0000-0000-0000-000000000001','Leaver One','l1@x','member',true,'{}','{"sops":"editor"}'),
  ('51515151-0000-0000-0000-000000000002','Request Two','r2@x','member',false,'{}','{}');
insert into auth.users(id,email) values ('51515151-0000-0000-0000-000000000001','l1@x'),('51515151-0000-0000-0000-000000000002','r2@x');
insert into auth.sessions(user_id) values ('51515151-0000-0000-0000-000000000001');
insert into hx_audit_log(table_name,row_id,action,user_id,user_name) values ('hx_sop_acks','x','INSERT','51515151-0000-0000-0000-000000000001','Leaver One');
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'R1 not admin', hx_admin_remove_user('51515151-0000-0000-0000-000000000001','left');
set test.uid='11111111-1111-1111-1111-111111111111';
select 'R2 no reason', hx_admin_remove_user('51515151-0000-0000-0000-000000000001','  ');
select 'R3 self', hx_admin_remove_user('11111111-1111-1111-1111-111111111111','x');
select 'R4 removed', hx_admin_remove_user('51515151-0000-0000-0000-000000000001','Left the company');
select 'R5 profile', approved, role, perms::text, removed_reason, removed_by is not null from hx_profiles where id='51515151-0000-0000-0000-000000000001';
select 'R6 blocked', banned_until = 'infinity'::timestamptz, (select count(*) from auth.sessions where user_id='51515151-0000-0000-0000-000000000001') from auth.users where id='51515151-0000-0000-0000-000000000001';
select 'R7 records kept', count(*) from hx_audit_log where user_id='51515151-0000-0000-0000-000000000001' and table_name='hx_sop_acks';
select 'R8 delete worked-in', hx_admin_delete_request('51515151-0000-0000-0000-000000000001');
select 'R9 restore', hx_admin_restore_user('51515151-0000-0000-0000-000000000001');
select 'R10 restored', approved, removed_at is null, (select banned_until is null from auth.users where id='51515151-0000-0000-0000-000000000001') from hx_profiles where id='51515151-0000-0000-0000-000000000001';
select 'R11 delete request', hx_admin_delete_request('51515151-0000-0000-0000-000000000002');
select 'R12 gone', (select count(*) from hx_profiles where id='51515151-0000-0000-0000-000000000002'), (select count(*) from auth.users where id='51515151-0000-0000-0000-000000000002');
select 'R13 audit', count(*) from hx_audit_log where row_id='51515151-0000-0000-0000-000000000001' and reason like 'Removed from Hendrix: Left the company';
