\set ON_ERROR_STOP 0
-- step 66: changing your own sign-in email reaches your Hendrix profile
update auth.users set email='mem.new@x.com' where id='22222222-2222-2222-2222-222222222222';
select 'M1 trigger copied', email from hx_profiles where id='22222222-2222-2222-2222-222222222222';
-- the trigger never blocks the sign-in service, even if the profile update fails
alter table hx_profiles add constraint t66_block check (email <> 'blocked@x.com') not valid;
update auth.users set email='blocked@x.com' where id='22222222-2222-2222-2222-222222222222';
select 'M2 auth still changed', email from auth.users where id='22222222-2222-2222-2222-222222222222';
select 'M2b profile kept', email from hx_profiles where id='22222222-2222-2222-2222-222222222222';
alter table hx_profiles drop constraint t66_block;
-- the app's fallback: hx_sync_my_email() copies only your own email
set test.uid='22222222-2222-2222-2222-222222222222';
select 'M3 sync', hx_sync_my_email();
select 'M3b profile', email from hx_profiles where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=replica; update auth.users set email='sam.new@x.com' where id='11111111-1111-1111-1111-111111111111'; set session_replication_role=origin;
select 'M4 other user untouched', email from hx_profiles where id='11111111-1111-1111-1111-111111111111';
set test.uid='';
select 'M5 signed out', coalesce(hx_sync_my_email(),'null');
-- put things back
set session_replication_role=replica;
update auth.users set email='m@x' where id='22222222-2222-2222-2222-222222222222';
update auth.users set email='s@x' where id='11111111-1111-1111-1111-111111111111';
update hx_profiles set email='m@x' where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
