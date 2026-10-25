\set ON_ERROR_STOP 0
-- step 41: METRC check
set session_replication_role=replica;
delete from hx_metrc_snapshots where license_id in ('lic-mo','lic-mi');
delete from hx_holds where id like 't41%'; delete from hx_suppliers where id like 't41%'; delete from hx_lots where id like 't41%'; delete from hx_shipments where id like 't41%'; delete from hx_tests where id like 't41%';
insert into hx_tests(id,state_id,license_id,tag,status,voided,created_at) values ('t41-t1','st-mo','lic-mo','1A40-TEST1','Passed',false,now()-interval '2 days'),('t41-t2','st-mo','lic-mo','1A40-TEST2','Failed',false,now()-interval '2 days'),
  ('t41-t3','st-mo','lic-mo','1A40-TEST3','Pending',false,now()-interval '2 days');
insert into hx_holds(id,state_id,license_id,number,kind,tag,item,reason,status) values ('t41-h1','st-mo','lic-mo','HOLD-T41-1','other','1A40-HOLD','Gummies','Check','open');
insert into hx_suppliers(id,state_id,license_id,name,status) values ('t41-sup','st-mo','lic-mo','T41 Supplier','approved');
insert into hx_lots(id,state_id,license_id,number,received_on,supplier_id,item,quantity,qty_used,unit,metrc_tag,status) values
  ('t41-l1','st-mo','lic-mo','LOT-T41-1',current_date-10,'t41-sup','Distillate',1000,200,'g','1A40-LOT1','accepted'),
  ('t41-l2','st-mo','lic-mo','LOT-T41-2',current_date-10,'t41-sup','Terpenes',50,0,'g','1A40-LOT2','accepted'),
  ('t41-l3','st-mo','lic-mo','LOT-T41-3',current_date-10,'t41-sup','Jars',100,0,'ea','1A40-LOT3','accepted');
insert into hx_shipments(id,state_id,license_id,number,ship_date,customer,status,items) values ('t41-s1','st-mo','lic-mo','SHP-T41',current_date-1,'Dispensary','shipped','[{"tag":"1A40-SHIP","batch_id":"lm-d"}]');
set session_replication_role=origin;
update hx_profiles set perms='{"qms":"read"}' where id='22222222-2222-2222-2222-222222222222';
set test.uid='11111111-1111-1111-1111-111111111111';
select 'M1 save' , left(hx_metrc_save('lic-mo','csv','packages.csv', '[
  {"tag":"1a40 test1","item":"Cart 1g","lab_state":"SubmittedForTesting"},
  {"tag":"1A40-TEST2","item":"Cart 1g","lab_state":"TestFailed"},
  {"tag":"1A40-TEST3","item":"Cart 1g","lab_state":"TestFailed"},
  {"tag":"1A40-HOLD","item":"Gummies","lab_state":"TestPassed","on_hold":false},
  {"tag":"1A40-MHOLD","item":"Flower","lab_state":"TestPassed","on_hold":true},
  {"tag":"1A40-LOT1","item":"Distillate","quantity":"700","unit":"Grams"},
  {"tag":"1A40-LOT3","item":"Jars","quantity":"100","unit":"Each"},
  {"tag":"1A40-SHIP","item":"Pre-roll","lab_state":"TestPassed"},
  {"tag":"1A40-NEW","item":"Rosin","batch_no":"B-77"},
  {"tag":"1A40-NEW","item":"Duplicate row"},
  {"tag":"","item":"no tag"}]'::jsonb), 3);
select 'M2 packages', packages, source, file_name from hx_metrc_snapshots where license_id='lic-mo';
select 'M3 findings', string_agg(f->>'kind' || ':' || (f->>'tag'), ',' order by f->>'kind' collate "C", f->>'tag' collate "C")
  from hx_metrc_snapshots s, jsonb_array_elements(hx_metrc_reconcile(s.id)->'findings') f where s.license_id='lic-mo';
select 'M4 first is high', (hx_metrc_reconcile(s.id)->'findings'->0->>'severity') from hx_metrc_snapshots s where s.license_id='lic-mo';
select 'M5 titles', f->>'title' from hx_metrc_snapshots s, jsonb_array_elements(hx_metrc_reconcile(s.id)->'findings') f where s.license_id='lic-mo' and f->>'kind' in ('quantity','lot','lab') order by 2;
select 'M6 empty', hx_metrc_save('lic-mo','csv','x.csv','[]'::jsonb);
-- a member without METRC access
set test.uid='22222222-2222-2222-2222-222222222222';
select hx_metrc_save('lic-mo','csv','x.csv','[{"tag":"A"}]'::jsonb);
select hx_metrc_reconcile((select id from hx_metrc_snapshots where license_id='lic-mo' limit 1));
set test.uid='11111111-1111-1111-1111-111111111111';
select 'M7 audited', count(*) from hx_audit_log where table_name='hx_metrc_snapshots';
-- leave the shared test database as it was (the other checks count holds, lots and shipments); test_mc.py keeps them (-v keep=1)
\if :{?keep}
\else
set session_replication_role=replica;
delete from hx_holds where id like 't41%'; delete from hx_lots where id like 't41%'; delete from hx_shipments where id like 't41%'; delete from hx_tests where id like 't41%'; delete from hx_suppliers where id like 't41%';
set session_replication_role=origin;
\endif
