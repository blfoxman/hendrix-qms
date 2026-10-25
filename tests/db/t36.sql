\set ON_ERROR_STOP 0
set session_replication_role=replica;
delete from hx_holds where id like 'lm%'; delete from hx_tests where id like 'lm%'; delete from hx_line_clearances where id like 'lm%';
delete from hx_deviations where id like 'lm%'; delete from hx_haccp_monitoring where id like 'lm%'; delete from hx_label_prints where id like 'lm%';
delete from hx_shipments where id like 'lm%'; delete from hx_production_plans where id like 'lm%'; delete from hx_time_clock where id like 'lm%';
delete from hx_equipment where id like 'lm%'; delete from hx_batches where id like 'lm%';
insert into hx_batches(id,state_id,license_id,batch_type,batch_number,sku,flavor,status,data,created_at,updated_at) values
 ('lm-a','st-mo','lic-mo','cartridges','LM-A','1g AIO','Blue Dream','In Progress','{"batch_number":"LM-A","notes":"secret"}', now()-interval '2 days', now()-interval '10 minutes'),
 ('lm-b','st-mo','lic-mo','cartridges','LM-B','1g AIO','Mango','In Progress','{}', now()-interval '3 days', now()-interval '9 hours'),
 ('lm-c','st-mo','lic-mo','gummies','LM-C','Gummies','Grape','Completed','{}', now()-interval '5 days', now()-interval '1 day'),
 ('lm-d','st-mo','lic-mo','gummies','LM-D','Gummies','Mango','Completed','{}', now()-interval '6 days', now()-interval '1 day'),
 ('lm-old','st-mo','lic-mo','gummies','LM-OLD','Gummies','Mango','Completed','{}', now()-interval '200 days', now()-interval '190 days'),
 ('lm-void','st-mo','lic-mo','gummies','LM-VOID','Gummies','Mango','','{}', now()-interval '1 day', now()),
 ('lm-mi','st-mi','lic-mi','cartridges','LM-MI','x','y','','{}', now()-interval '1 day', now());
update hx_batches set voided=true, void_reason='test' where id='lm-void';
insert into hx_equipment(id,state_id,license_id,number,name,category,status,cal_required,cal_interval_months,cal_due) values
 ('lm-eq1','st-mo','lic-mo','EQ-901','Cone filler','Production','in_service',true,6,current_date-4),
 ('lm-eq2','st-mo','lic-mo','EQ-902','Mixer','Production','in_service',false,null,null),
 ('lm-eq3','st-mo','lic-mo','EQ-903','Old press','Production','out_of_service',false,null,null);
insert into hx_line_clearances(id,state_id,license_id,number,batch_id,batch_label,area,equipment_ids,result,recorded_by,created_at) values
 ('lm-lc1','st-mo','lic-mo','LC-2026-901','lm-a','LM-A','Line 1','{lm-eq1,lm-eq2}','cleared','Ana',now()-interval '1 day'),
 ('lm-lc2','st-mo','lic-mo','LC-2026-902','lm-b','LM-B','Line 2','{lm-eq2}','not_cleared','Ana',now()-interval '2 days');
insert into hx_tests(id,state_id,license_id,batch_id,batch_number,tag,status,lab_name,created_at,updated_at) values
 ('lm-t1','st-mo','lic-mo','lm-c','LM-C','TAG-C','Failed','Lab',now()-interval '3 days',now()-interval '2 days'),
 ('lm-t2','st-mo','lic-mo','lm-d','LM-D','TAG-D','Passed','Lab',now()-interval '3 days',now()-interval '2 days');
insert into hx_holds(id,state_id,license_id,number,kind,batch_id,item,reason,status,created_at) values
 ('lm-h1','st-mo','lic-mo','HOLD-2026-901','batch','lm-c','LM-C','Potency over label claim','open',now()-interval '2 days');
insert into hx_deviations(id,state_id,license_id,number,title,dept,category,description,occurred_on,source_type,source_id,status,priority,created_at) values
 ('lm-dv1','st-mo','lic-mo','DEV-2026-901','Fill weight low','Production','Process','x',current_date,'batch','lm-a','open','minor',now()-interval '1 hour');
insert into hx_label_prints(id,state_id,license_id,batch_number,tag,sku,flavor,count,created_at) values ('lm-lp1','st-mo','lic-mo','lm-d','TAG-D','Gummies','Mango',20,now()-interval '20 hours');
update hx_label_prints set batch_number='LM-D' where id='lm-lp1';
insert into hx_shipments(id,state_id,license_id,number,ship_date,customer,items,status,created_at) values
 ('lm-s1','st-mo','lic-mo','SHP-2026-901',current_date,'Green Leaf','[{"batch_id":"lm-d","batch_number":"LM-D","qty":20}]','shipped',now());
insert into hx_production_plans(id,state_id,license_id,number,product_type,sku_name,planned_for,units_per_flavor,lines,status) values
 ('lm-p1','st-mo','lic-mo','PP-2026-901','cartridges','1g AIO',current_date+1,500,'[{"flavor":"Grape"},{"flavor":"Lime"}]','planned'),
 ('lm-p2','st-mo','lic-mo','PP-2026-902','cartridges','1g AIO',current_date,500,'[{"flavor":"Grape"}]','completed');
insert into hx_time_clock(id,state_id,license_id,profile_id,person_name,event_type,ts,event_date,source) values
 ('lm-tc1','st-mo','lic-mo','22222222-2222-2222-2222-222222222222','Dana','entry',now()-interval '3 hours',current_date,'kiosk'),
 ('lm-tc2','st-mo','lic-mo','11111111-1111-1111-1111-111111111111','Sam','entry',now()-interval '5 hours',current_date,'kiosk'),
 ('lm-tc3','st-mo','lic-mo','11111111-1111-1111-1111-111111111111','Sam','clockout',now()-interval '1 hours',current_date,'kiosk');
insert into hx_license_settings(license_id,state_id) values ('lic-mo','st-mo') on conflict (license_id) do nothing;
set session_replication_role=origin;

-- 1. admin reads the map
set test.uid='11111111-1111-1111-1111-111111111111';
set role authenticated;
select 'T1 idle', (hx_line_map('lic-mo')->>'idle_hours');
select 'T1 batches', string_agg(x->>'batch_number', ',' order by x->>'batch_number') from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id' like 'lm%';
select 'T1 notes hidden', (select x->'data' ? 'notes' from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-a');
select 'T1 lc A', (select jsonb_array_length(x->'clearances') from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-a');
select 'T1 dev A', (select x->'deviations'->0->>'number' from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-a');
select 'T1 hold C', (select x->'holds'->0->>'number' from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-c');
select 'T1 tests C', (select x->'tests'->0->>'status' from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-c');
select 'T1 labels D', (select x->'labels'->>'count' from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-d');
select 'T1 ship D', (select x->'shipments'->0->>'number' from jsonb_array_elements(hx_line_map('lic-mo')->'batches') x where x->>'id'='lm-d');
select 'T1 equipment', (select string_agg(e->>'number'||':'||(e->>'issue'), ' | ' order by e->>'number') from jsonb_array_elements(hx_line_map('lic-mo')->'equipment_issues') e where e->>'id' like 'lm%');
select 'T1 plans', (select string_agg((p->>'number')||'='||(p->'flavors')::text, ',') from jsonb_array_elements(hx_line_map('lic-mo')->'plans') p where p->>'id' like 'lm%');
select 'T1 on floor', hx_line_map('lic-mo')->>'on_floor';
-- 2. license of another state is fine for admin, but only its own batches
select 'T2 mi batches', (select string_agg(x->>'batch_number', ',') from jsonb_array_elements(hx_line_map('lic-mi')->'batches') x where x->>'id' like 'lm%');
-- 3. member without linemap access is refused
set test.uid='22222222-2222-2222-2222-222222222222';
select 'T3 no access', hx_line_map('lic-mo') is not null;
reset role;
-- 4. give the member linemap View: allowed, but only for licenses they may use
set test.uid='11111111-1111-1111-1111-111111111111';
update hx_profiles set perms = '{"linemap":"read"}', license_ids='{lic-mo}' where id='22222222-2222-2222-2222-222222222222';
set test.uid='22222222-2222-2222-2222-222222222222';
set role authenticated;
select 'T4 member ok', jsonb_array_length(hx_line_map('lic-mo')->'batches') > 0;
select 'T4 other license', hx_line_map('lic-mi') is not null;
reset role;
-- 5. unapproved user is refused
set test.uid='33333333-3333-3333-3333-333333333333';
set role authenticated;
select 'T5 unapproved', hx_line_map('lic-mo') is not null;
reset role;
-- 6. anon cannot call it
set role anon;
select 'T6 anon', hx_line_map('lic-mo') is not null;
reset role;
-- 7. idle hours setting: allowed range only
set test.uid='11111111-1111-1111-1111-111111111111';
update hx_license_settings set linemap_idle_hours = 6 where license_id='lic-mo';
update hx_license_settings set linemap_idle_hours = 0 where license_id='lic-mo';
set test.uid='11111111-1111-1111-1111-111111111111';
set role authenticated;
select 'T7 idle now', hx_line_map('lic-mo')->>'idle_hours';
reset role;
update hx_license_settings set linemap_idle_hours = 4 where license_id='lic-mo';
update hx_profiles set perms = '{}', license_ids='{}' where id='22222222-2222-2222-2222-222222222222';
