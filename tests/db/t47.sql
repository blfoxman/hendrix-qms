\set ON_ERROR_STOP 0
-- step 47: Batch Tracker picks tags from Receiving; the batch's use is deducted from the lot
set session_replication_role=replica;
delete from hx_lot_uses where id like 't47%'; delete from hx_batches where id like 't47%'; delete from hx_lots where id like 't47%'; delete from hx_suppliers where id like 't47%';
delete from hx_roles where id='t47-batch';
insert into hx_roles (id, name, perms) values ('t47-batch', 'T47 Batch only', '{"batch":"editor"}');
update hx_profiles set role='member', approved=true, mfa_required=false, license_ids='{lic-mo}', perms='{}', role_ids='{t47-batch}' where id='22222222-2222-2222-2222-222222222222';
insert into hx_suppliers(id,state_id,license_id,name,status) values ('t47-sup','st-mo','lic-mo','Black Fox Manufacturing LLC','approved');
insert into hx_lots(id,state_id,license_id,number,received_on,supplier_id,item,quantity,qty_used,unit,metrc_tag,status,expiry_date) values
  ('t47-l1','st-mo','lic-mo','LOT-T47-1',current_date-5,'t47-sup','Flower OG',1240,0,'g','1A40C03000060E1000003275','accepted',null),
  ('t47-l2','st-mo','lic-mo','LOT-T47-2',current_date-5,'t47-sup','Flower quarantine',500,0,'g','1A40C03000060E1000009999','quarantine',null),
  ('t47-l3','st-mo','lic-mo','LOT-T47-3',current_date-5,'t47-sup','Flower used up',100,100,'g','1A40C03000060E1000008888','accepted',null),
  ('t47-l4','st-mo','lic-mo','LOT-T47-4',current_date-50,'t47-sup','Flower expired',100,0,'g','1A40C03000060E1000007777','accepted',current_date-1);
insert into hx_batches(id,state_id,license_id,batch_type,batch_number,sku,flavor,status,data,created_at,updated_at) values
  ('t47-b1','st-mo','lic-mo','pre_rolls','PR-T47','Pre-roll 1g','OG','In Progress','{}',now(),now());
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'L1 lots', string_agg(number||':'||qty_left, ',' order by number) from hx_batch_lots('lic-mo') where number like 'LOT-T47%';
select 'L2 other license', count(*) from hx_batch_lots('lic-mi');
insert into hx_lot_uses(id,state_id,license_id,lot_id,batch_id,quantity,notes) values ('t47-u1','st-mo','lic-mo','t47-l1','t47-b1',300,'Batch Tracker: Flower Used [bt:flower_qty]');
reset test.uid;
select 'U1 deducted', quantity - qty_used from hx_lots where id='t47-l1';
select 'U2 use', batch_number, quantity from hx_lot_uses where id='t47-u1';
set test.uid='22222222-2222-2222-2222-222222222222';
select 'L3 left now', qty_left from hx_batch_lots('lic-mo') where number='LOT-T47-1';
insert into hx_lot_uses(id,state_id,license_id,lot_id,batch_id,quantity,notes) values ('t47-u2','st-mo','lic-mo','t47-l1','t47-b1',5000,'too much');
reset test.uid;
