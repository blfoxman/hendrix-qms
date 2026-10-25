\set ON_ERROR_STOP 0
-- step 39: My Tasks inbox + email alerts
set test.uid='11111111-1111-1111-1111-111111111111';
set session_replication_role=replica;
delete from hx_sop_acks where id like 't39%'; delete from hx_sops where id like 't39%'; delete from hx_capas where id like 't39%'; delete from hx_deviations where id like 't39%';
delete from hx_holds where id like 't39%'; delete from hx_training_records where id like 't39%'; delete from hx_training_courses where id like 't39%'; delete from hx_changes where id like 't39%';
delete from hx_equipment where id like 't39%'; delete from hx_notify_queue; delete from hx_notify_log;
update hx_profiles set perms='{"sops":"read","qms":"read","training":"read","changes":"read"}', role_ids='{}', license_ids='{lic-mo}', mfa_required=false, task_email=true where id='22222222-2222-2222-2222-222222222222';
insert into hx_sops(id,state_id,license_id,license_ids,title,sop_number,version,status,target_mode,effective_date) values
  ('t39-s1','st-mo','lic-mo','{lic-mo}','Cart Filling','SOP-PRD-001','1.0','published','license',current_date-5),
  ('t39-s2','st-mo','lic-mo','{lic-mo}','Line Cleaning','SOP-PRD-002','1.0','draft','license',null),
  ('t39-s3','st-mi','lic-mi','{lic-mi}','Michigan Only','SOP-MI-001','1.0','published','license',current_date-5),
  ('t39-s4','st-mo','lic-mo','{lic-mo}','Lead Only','SOP-PRD-003','1.0','published','people',current_date-5);
update hx_sops set target_user_ids='{11111111-1111-1111-1111-111111111111}' where id='t39-s4';
insert into hx_sop_acks(id,sop_id,state_id,license_id,version,user_id,name,signature) values ('t39-a1','t39-s1','st-mo','lic-mo','1.0','11111111-1111-1111-1111-111111111111','Sam','data:x');
insert into hx_capas(id,state_id,license_id,number,title,responsible_person_name,due_date,status,priority) values
  ('t39-c1','st-mo','lic-mo','CAPA-T39-1','Fix the filler','mem',current_date-1,'open','major'),
  ('t39-c2','st-mo','lic-mo','CAPA-T39-2','Closed one','Mem',current_date-1,'closed','major');
insert into hx_deviations(id,state_id,license_id,number,title,owner_name,status,priority) values ('t39-d1','st-mo','lic-mo','DEV-T39-1','Spill','','open','minor');
insert into hx_holds(id,state_id,license_id,number,kind,item,reason,status) values ('t39-h1','st-mo','lic-mo','HOLD-T39-1','lot','Distillate','COA missing','open');
insert into hx_training_courses(id,state_id,license_id,license_ids,name,required_mode,active) values ('t39-tc1','st-mo','lic-mo','{lic-mo}','GMP Basics','everyone',true),('t39-tc2','st-mo','lic-mo','{lic-mo}','Forklift','optional',true);
insert into hx_training_records(id,state_id,license_id,course_id,user_id,person_name,completed_on,expires_on,voided) values
  ('t39-tr1','st-mo','lic-mo','t39-tc2','22222222-2222-2222-2222-222222222222','Mem',current_date-350,current_date+10,false);
insert into hx_changes(id,state_id,license_id,number,title,status,actions) values
  ('t39-ch1','st-mo','lic-mo','CC-T39-1','New filler','approved','[{"what":"Update SOP","who":"Mem ","due":"2026-01-02","done":false},{"what":"Train","who":"Mem","done":true},{"what":"Order parts","who":"Sam"}]'),
  ('t39-ch2','st-mo','lic-mo','CC-T39-2','New label','requested','[]');
insert into hx_equipment(id,state_id,license_id,number,name,status,cal_required,cal_due) values ('t39-e1','st-mo','lic-mo','EQ-T39','Scale 1','in_service',true,current_date+3);
set session_replication_role=origin;

-- member Mem at Black Fox
set test.uid='22222222-2222-2222-2222-222222222222';
select 'M1 kinds', string_agg(t->>'kind' || ':' || coalesce(t->>'ref',''), ',' order by t->>'kind', t->>'ref') from jsonb_array_elements(hx_my_tasks('lic-mo')) t where t->>'ref' like 't39%';
select 'M2 first overdue', (hx_my_tasks('lic-mo')->0->>'ref'), (hx_my_tasks('lic-mo')->0->>'overdue');
select 'M3 other license', jsonb_array_length(hx_my_tasks('lic-mi'));
select 'M4 training detail', t->>'title' from jsonb_array_elements(hx_my_tasks('lic-mo')) t where t->>'kind'='training' order by 2;
-- admin Sam
set test.uid='11111111-1111-1111-1111-111111111111';
select 'A1 kinds', string_agg(t->>'kind' || ':' || coalesce(t->>'ref',''), ',' order by t->>'kind', t->>'ref') from jsonb_array_elements(hx_my_tasks('lic-mo')) t where t->>'ref' like 't39%';
-- nobody signed in
set test.uid='';
select 'N1 anonymous', jsonb_array_length(hx_my_tasks('lic-mo'));
-- signing removes the task
set session_replication_role=replica;
insert into hx_sop_acks(id,sop_id,state_id,license_id,version,user_id,name,signature) values ('t39-a2','t39-s1','st-mo','lic-mo','1.0','22222222-2222-2222-2222-222222222222','Mem','data:x');
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'M5 after signing', count(*) from jsonb_array_elements(hx_my_tasks('lic-mo')) t where t->>'kind'='sop_sign' and t->>'ref'='t39-s1';
select hx_set_task_email(false);
select 'M6 email off', task_email from hx_profiles where id='22222222-2222-2222-2222-222222222222';
select 'M7 digest skips', count(*) from jsonb_array_elements(hx_task_digest()) x where x->>'name'='Mem';
select hx_set_task_email(true);
-- alerts: a hold and a failed test go to the queue
set test.uid='11111111-1111-1111-1111-111111111111';
set session_replication_role=replica; delete from hx_holds where id='t39-h2'; set session_replication_role=origin;
insert into hx_holds(id,state_id,license_id,number,kind,item,reason) values ('t39-h2','st-mo','lic-mo','HOLD-T39-2','other','Gummies','Foreign matter');
select 'Q1 queue', kind, title, module from hx_notify_queue where ref='t39-h2';
-- the hendrix-notify function's view (service role; here the database owner)
select 'D1 digest', string_agg(x->>'name' || '=' || (select count(*) from jsonb_array_elements(l->'tasks'))::text, ',' order by x->>'name')
  from jsonb_array_elements(hx_task_digest()) x, jsonb_array_elements(x->'licenses') l where l->>'license_id'='lic-mo';
select 'D2 claims restored', current_setting('test.uid', true);
select 'P1 alert recipients', (select string_agg(r->>'email', ',') from jsonb_array_elements(q->'recipients') r) from jsonb_array_elements(hx_notify_pending()) q where q->>'title' like 'Hold placed:%Gummies';
select 'P2 sent', hx_notify_sent(array(select id from hx_notify_queue where ref='t39-h2'), '[{"kind":"alert","email":"s@x","subject":"Hold placed","items":1,"status":"sent","ref":"0"}]');
select 'P3 not pending', count(*) from jsonb_array_elements(hx_notify_pending()) q where q->>'title' like 'Hold placed:%Gummies';
-- the service-only functions are closed to signed-in people
set role authenticated;
select hx_task_digest();
select hx_notify_pending();
reset role;
select 'S1 status', (hx_notify_status()->>'sent_7d')::int >= 1;
set test.uid='22222222-2222-2222-2222-222222222222';
select hx_notify_status();
