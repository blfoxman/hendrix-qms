\set ON_ERROR_STOP 0
-- step 55: METRC tags on cannabis lots
set session_replication_role=replica;
delete from hx_lots where license_id='lic-mo' and item like 'T55%';
delete from hx_suppliers where id='t55-s';
insert into hx_suppliers(id,state_id,license_id,license_ids,name,status) values ('t55-s','st-mo','lic-mo','{lic-mo}','T55 Farms','approved');
-- an older cannabis lot already in stock with no tag (before step 55)
insert into hx_lots(id,state_id,license_id,number,supplier_id,supplier_name,supplier_status,item,category,quantity,unit,status,coa_ok,metrc_tag,received_on) values
  ('t55-old','st-mo','lic-mo','RCV-T55OLD','t55-s','T55 Farms','approved','T55 old flower','Cannabis (flower, trim, biomass)',1000,'g','accepted',true,'',current_date-30);
set session_replication_role=origin;
set test.uid='11111111-1111-1111-1111-111111111111';
insert into hx_lots(id,state_id,license_id,supplier_id,item,category,quantity,unit,status,coa_ok,checks) values ('t55-a','st-mo','lic-mo','t55-s','T55 flower','Cannabis (flower, trim, biomass)',500,'g','quarantine',true,'{"a":true}');
insert into hx_lots(id,state_id,license_id,supplier_id,item,category,quantity,unit,status,coa_ok,metrc_tag,checks) values ('t55-b','st-mo','lic-mo','t55-s','T55 distillate','Distillate / extract',900,'g','quarantine',true,'  1A40-5500 0000 0000 0000 0001 ','{"a":true}');
insert into hx_lots(id,state_id,license_id,supplier_id,item,category,quantity,unit,status,coa_ok,metrc_tag,checks) values ('t55-c','st-mo','lic-mo','t55-s','T55 trim','Cannabis (flower, trim, biomass)',900,'g','quarantine',true,'1a4055000000000000000001','{"a":true}');
insert into hx_lots(id,state_id,license_id,supplier_id,item,category,quantity,unit,status,coa_ok,checks) values ('t55-d','st-mo','lic-mo','t55-s','T55 jars','Packaging',100,'each','quarantine',true,'{"a":true}');
select 'T1 saved', count(*) from hx_lots where id in ('t55-b','t55-d');
select 'T2 trimmed', metrc_tag from hx_lots where id='t55-b';
update hx_lots set metrc_tag='' where id='t55-b';
update hx_lots set status='accepted', decision_notes='ok' where id='t55-b';
select 'T3 accepted', status from hx_lots where id='t55-b';
select 'T4 add', hx_lot_set_tag('t55-old','1A4055000000000000000099','');
select 'T5 audit', count(*) from hx_audit_log where table_name='hx_lots' and row_id='t55-old' and reason='METRC tag added';
select 'T6 dup', hx_lot_set_tag('t55-d','1A40 5500 0000 0000 0000 0099','');
select 'T7', hx_lot_set_tag('t55-old','','');
select 'T8', hx_lot_set_tag('t55-old','1A4055000000000000000098','');
select 'T9 changed', hx_lot_set_tag('t55-old','1A4055000000000000000098','typo');
select 'T10 audit', count(*) from hx_audit_log where table_name='hx_lots' and row_id='t55-old' and reason='METRC tag changed from 1A4055000000000000000099: typo';
set session_replication_role=replica;
update hx_profiles set perms='{"receiving":"editor"}', license_ids='{}' where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'T11 editor adds', hx_lot_set_tag('t55-d','1A4055000000000000000077','');
select 'T12', hx_lot_set_tag('t55-old','1A4055000000000000000066','x');
set session_replication_role=replica;
update hx_profiles set perms='{}' where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
set test.uid='11111111-1111-1111-1111-111111111111';
select 'T13 import', hx_lots_import('lic-mo','[{"item":"T55 import bud","category":"Cannabis (flower, trim, biomass)","quantity":10,"unit":"g","supplier":"T55 Farms","coa_ok":true}]','x.xlsx');
select 'T14 final', string_agg(id||'='||metrc_tag, ',' order by id) from hx_lots where id in ('t55-old','t55-d');
select 'T15 metrc cats', hx_lot_canna('Bud/Flower'), hx_lot_canna('Ground Shake/Trim'), hx_lot_canna('Concentrate'), hx_lot_canna('Cones / pre-roll supplies'), hx_lot_canna('Hardware (cartridges, batteries)'), hx_lot_canna('Packaging');
