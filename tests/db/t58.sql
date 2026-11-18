\set ON_ERROR_STOP 0
-- step 58: store complaint QR form (no login)
set session_replication_role=replica;
delete from hx_complaints where channel='QR form';
set session_replication_role=origin;
set test.uid='';
set role anon;
select 'Q1 number', hx_complaint_qr('st-mo','lic-mo', jsonb_build_object('store','Green Leaf KC','name','Ana','contact','ana@gl.com','product','2G AIO Blue Dream','tag','1a4 0000 1234','lot','LOT-9','category','Hardware / packaging failure','description','Three carts leak at the mouthpiece.','purchased','2026-11-15','photos',jsonb_build_array('data:image/jpeg;base64,/9j/abc'))) ~ '^CMP-\d{4}-\d{3}$';
select hx_complaint_qr('st-mo','lic-mo', jsonb_build_object('store','Green Leaf KC','name','Ana','contact','ana@gl.com','product','Gummies','description','Customer threw up after one gummy.','health',true));
select hx_complaint_qr('st-mo','lic-mo', jsonb_build_object('store','','name','Ana','contact','x','product','p','description','long enough text'));
select hx_complaint_qr('st-mo','lic-mo', jsonb_build_object('store','S','name','Ana','contact','x','product','p','description','short'));
select hx_complaint_qr('st-mi','lic-mo', jsonb_build_object('store','S','name','Ana','contact','x','product','p','description','long enough text'));
select hx_complaint_qr('st-mo','lic-mo', jsonb_build_object('store','S','name','Ana','contact','x','product','p','description','long enough text','photos',jsonb_build_array('data:text/html;base64,PGI+')));
select hx_complaint_qr('st-mo','lic-mo', jsonb_build_object('store','S','name','Ana','contact','x','product','p','description','long enough text','category','Bad vibes'));
insert into hx_complaints(id,state_id,license_id,title) values ('t58-x','st-mo','lic-mo','direct');
select 'A1 anon cannot read', count(*) from hx_complaints;
reset role;
select 'C1 dispensary', type, priority, status, channel, customer, complainant, complainant_contact, tag, lot_number, jsonb_array_length(qr_photos), created_by from hx_complaints where channel='QR form' and product='2G AIO Blue Dream';
select 'C2 adverse', type, priority, description like '%sick or hurt%' from hx_complaints where channel='QR form' and product='Gummies';
select 'C3 audit', count(*) from hx_audit_log where table_name='hx_complaints' and reason='Complaint filed by a store (QR form)';
select 'C4 alert', count(*) from hx_notify_queue q join hx_complaints c on c.id = q.ref where c.channel='QR form';
-- the step 19 rule still holds for people signed in
set test.uid='22222222-2222-2222-2222-222222222222';
set session_replication_role=replica; update hx_profiles set perms='{}', role_ids='{}', role='user', approved=true where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
select set_config('hx.cmp_qr','',false);
insert into hx_complaints(id,state_id,license_id,title) values ('t58-y','st-mo','lic-mo','no access');
set test.uid='11111111-1111-1111-1111-111111111111';
select 'H1 health', ok from hx_system_health() h, jsonb_to_recordset(h->'steps') as s(step int, ok boolean) where step=58;
set session_replication_role=replica; delete from hx_complaints where channel='QR form'; set session_replication_role=origin;
