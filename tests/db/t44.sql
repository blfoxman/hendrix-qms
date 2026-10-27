\set ON_ERROR_STOP 0
-- step 44: the CSQ Program Overview course can be taken online; HACCP certification stays certificate-only
set session_replication_role=replica;
delete from hx_training_keys where course_id in ('t44-csq','t44-haccp');
delete from hx_training_courses where id in ('t44-csq','t44-haccp');
insert into hx_training_courses(id, state_id, license_id, license_ids, name, topic) values
  ('t44-csq','st-mo','lic-mo','{lic-mo}','T44 CSQ Program Overview','CSQ program'),
  ('t44-haccp','st-mo','lic-mo','{lic-mo}','T44 HACCP certification','HACCP');
set session_replication_role=origin;
select 'C1 cert only', hx_course_cert_only('HACCP'), hx_course_cert_only('CSQ program'), hx_course_cert_only('HACCP basics');
update hx_training_courses set online = true, lessons = '[{"title":"a","body":"b"}]', quiz = '[{"q":"x","options":["a","b"]}]', content_status = 'draft' where id = 't44-csq';
select 'C2 csq online', online, content_status from hx_training_courses where id = 't44-csq';
update hx_training_courses set online = true, content_status = 'draft' where id = 't44-haccp';
select 'C3 haccp online', online from hx_training_courses where id = 't44-haccp';
set session_replication_role=replica;
delete from hx_training_courses where id in ('t44-csq','t44-haccp');
set session_replication_role=origin;
