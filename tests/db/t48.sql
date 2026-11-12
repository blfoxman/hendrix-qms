\set ON_ERROR_STOP 0
-- step 48: alert trigger reads only the fields of the table being saved
set session_replication_role=replica;
delete from hx_notify_queue where ref like 't48%'; delete from hx_tests where id like 't48%'; delete from hx_deviations where id like 't48%';
set session_replication_role=origin;
insert into hx_tests(id,state_id,license_id,tag,tag_label,status,performed_by) values ('t48-t1','st-mo','lic-mo','1A40C03000060E1000004848','Packaged METRC Tag','Submitted','Sam');
select 'S1 submitted', count(*) from hx_tests where id='t48-t1';
update hx_tests set status='Passed' where id='t48-t1';
select 'S2 passed', status from hx_tests where id='t48-t1';
insert into hx_tests(id,state_id,license_id,tag,tag_label,status,performed_by) values ('t48-t2','st-mo','lic-mo','1A40C03000060E1000004849','Packaged METRC Tag','Submitted','Sam');
update hx_tests set status='Failed', result_notes='Yeast over limit' where id='t48-t2';
update hx_tests set result_notes='Yeast over limit (retest)' where id='t48-t2';
select 'S3 failed alert', count(*) from hx_notify_queue where ref='t48-t2' and kind='test_failed';
select 'S4 triggers', count(*) from pg_trigger where tgfoid='hx_notify_row'::regproc and not tgisinternal;
select 'S5 old gone', count(*) from pg_proc where proname='hx_notify_add';
