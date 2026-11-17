\set ON_ERROR_STOP 0
-- step 53: upload inventory from Excel
set session_replication_role=replica;
delete from hx_lots where license_id='lic-mo' and metrc_tag like '1A4053%';
delete from hx_suppliers where id like 't53%';
insert into hx_suppliers(id,state_id,license_id,license_ids,name,status) values ('t53-ok','st-mo','lic-mo','{lic-mo}','Greenway Packaging','approved'),('t53-p','st-mo','lic-mo','{lic-mo}','Pending Co','pending');
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'U1', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Greenway Packaging","coa_ok":true}]','x.xlsx');
set test.uid='11111111-1111-1111-1111-111111111111';
select 'U2', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Nobody Inc","coa_ok":true}]','x.xlsx');
select 'U3', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Pending Co","coa_ok":true}]','x.xlsx');
select 'U4', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Greenway Packaging","coa_ok":false}]','x.xlsx');
select 'U5', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"greenway packaging","coa_ok":true,"metrc_tag":"1A4053000000000000000001"},{"item":"Lids","quantity":0,"unit":"each","supplier":"Greenway Packaging","coa_ok":true}]','x.xlsx');
select 'U6 nothing saved', count(*) from hx_lots where license_id='lic-mo' and metrc_tag like '1A4053%';
select 'U7', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Greenway Packaging","coa_ok":true,"metrc_tag":"1A4053000000000000000001"},{"item":"Jars","quantity":5,"unit":"each","supplier":"Greenway Packaging","coa_ok":true,"metrc_tag":"1A40-5300-0000-0000-0000-0001"}]','x.xlsx');
select 'U8 ok', (hx_lots_import('lic-mo','[{"item":"Glass jars 3.5g","category":"Packaging","quantity":1200,"unit":"each","supplier":"Greenway Packaging","coa_ok":true,"metrc_tag":"1A4053000000000000000001","received_on":"2026-11-01","location":"Warehouse A"},{"item":"Biomass","category":"Cannabis (flower, trim, biomass)","quantity":2.5,"unit":"kg","supplier":"Greenway Packaging","status":"quarantine","metrc_tag":"1A4053000000000000000002"}]','inventory.xlsx'))->>'count';
select 'U9 lots', item, status, quantity, unit, coa_ok, received_on, location, supplier_name, number like 'RCV-%', decision_notes like 'Inventory uploaded from inventory.xlsx%' from hx_lots where license_id='lic-mo' and metrc_tag like '1A4053%' order by metrc_tag;
select 'U10 dup', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Greenway Packaging","coa_ok":true,"metrc_tag":"1a4053000000000000000001"}]','x.xlsx');
select 'U11 audit', count(*) from hx_audit_log a join hx_lots l on l.id=a.row_id where l.metrc_tag='1A4053000000000000000001' and a.reason in ('Lot received from Greenway Packaging','Accepted: inventory uploaded from inventory.xlsx');
select 'U12', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Greenway Packaging","coa_ok":true,"received_on":"2099-01-01"}]','x.xlsx');
select 'U13', hx_lots_import('lic-mo','[{"item":"Jars","quantity":10,"unit":"each","supplier":"Greenway Packaging","coa_ok":true,"status":"done"}]','x.xlsx');
