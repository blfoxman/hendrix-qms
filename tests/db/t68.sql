\set ON_ERROR_STOP 0
-- step 68: Training Center profile (name, title, access)
set session_replication_role=replica;
delete from hx_badges where profile_id='22222222-2222-2222-2222-222222222222';
insert into hx_badges(profile_id, code, badge_no, title) values ('22222222-2222-2222-2222-222222222222','T68MEM','9068','Extraction Technician');
delete from hx_org_positions where id='t68-pos';
insert into hx_org_positions(id, state_id, license_id, title, user_id) values ('t68-pos','st-mo','lic-mo','QA Manager','11111111-1111-1111-1111-111111111111');
update hx_profiles set perms='{"linemap":"read","logs":"editor"}'::jsonb, role_ids='{}', mfa_required=false where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'P1 member', p->>'name', p->>'title', p->>'admin', p->'access'->>'linemap', p->'access'->>'logs_pest', p->'access'->>'audit'
  from (select hx_my_training_profile(array['linemap','logs_pest','audit','bad name!']) p) x;
select 'P2 odd names dropped', hx_my_training_profile(array['bad name!'])->'access';
set test.uid='11111111-1111-1111-1111-111111111111';
select 'P3 admin', p->>'title', p->>'admin', p->'access'->>'audit' from (select hx_my_training_profile(array['audit']) p) x;
set test.uid='33333333-3333-3333-3333-333333333333';
select 'P4 waiting', hx_my_training_profile(array['audit'])->>'approved';
-- two-step required: nothing until the authenticator code
set session_replication_role=replica; update hx_profiles set mfa_required=true where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'P5 mfa', p->>'mfa_needed', p->'access'->>'linemap' from (select hx_my_training_profile(array['linemap']) p) x;
set request.jwt.claims='{"aal":"aal2"}';
select 'P6 aal2', p->>'mfa_needed', p->'access'->>'linemap' from (select hx_my_training_profile(array['linemap']) p) x;
set request.jwt.claims='';
set test.uid='';
select 'P7 signed out', hx_my_training_profile(array['audit']);
set role anon; select 'P8 anon', hx_my_training_profile(array['audit']); reset role;
-- put things back
set session_replication_role=replica;
update hx_profiles set mfa_required=false, perms='{}'::jsonb where id='22222222-2222-2222-2222-222222222222';
delete from hx_badges where profile_id='22222222-2222-2222-2222-222222222222' and code='T68MEM';
delete from hx_org_positions where id='t68-pos';
set session_replication_role=origin;
