\set ON_ERROR_STOP 0
-- step 49: Spanish versions of SOPs and courses are saved on the record without changing the approved English
set session_replication_role=replica;
delete from hx_sops where id like 't49%'; delete from hx_training_courses where id like 't49%'; delete from hx_roles where id='t49-sop';
insert into hx_roles (id, name, perms) values ('t49-sop', 'T49 SOP editor', '{"sops":"editor","training":"editor"}');
update hx_profiles set role='member', approved=true, mfa_required=false, license_ids='{lic-mo}', perms='{}', role_ids='{t49-sop}' where id='22222222-2222-2222-2222-222222222222';
insert into hx_sops(id,state_id,license_id,license_ids,title,sop_number,version,status,target_mode,steps,folder) values
  ('t49-s1','st-mo','lic-mo','{lic-mo}','Line wipe-down','SOP-T49-001','1.0','published','license','[]','General'),
  ('t49-s2','st-mo','lic-mo','{lic-mo}','Draft wipe-down','SOP-T49-002','0.1','draft','license','[]','General');
insert into hx_training_courses(id,state_id,license_id,license_ids,name,online,lessons,quiz,content_status,content_version) values
  ('t49-c1','st-mo','lic-mo','{lic-mo}','T49 GMP basics',true,'[{"title":"Hands","body":"Wash hands."}]','[{"q":"When?","options":["Before work","Never"]}]','published',3);
set session_replication_role=origin;
select 'E1 columns', count(*) from information_schema.columns where table_schema='public' and column_name='es' and table_name in ('hx_sops','hx_training_courses');
set test.uid='22222222-2222-2222-2222-222222222222';
update hx_sops set es='{"sig":"a","title":"Limpieza del borrador"}' where id='t49-s2';
select 'E2 editor draft', es->>'title' from hx_sops where id='t49-s2';
update hx_sops set es='{"sig":"a","title":"Limpieza"}' where id='t49-s1';
select 'E3 editor published', coalesce(es->>'title','none') from hx_sops where id='t49-s1';
set test.uid='11111111-1111-1111-1111-111111111111';
update hx_sops set es='{"sig":"a","title":"Limpieza de línea"}' where id='t49-s1';
select 'E4 full published', es->>'title', version, (select count(*) from hx_sop_versions where sop_id='t49-s1') from hx_sops where id='t49-s1';
update hx_training_courses set es='{"sig":"b","name":"Fundamentos de GMP"}' where id='t49-c1';
select 'E5 course', es->>'name', content_version, content_status from hx_training_courses where id='t49-c1';
reset test.uid;
