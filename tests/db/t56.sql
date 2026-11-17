\set ON_ERROR_STOP 0
-- step 56: update inventory from Excel (counts, location, missing tag, new lots)
set session_replication_role=replica;
delete from hx_lot_counts where license_id='lic-mo' and lot_id like 't56%';
delete from hx_lots where license_id='lic-mo' and (id like 't56%' or item like 'T56%');
delete from hx_suppliers where id='t56-s';
insert into hx_suppliers(id,state_id,license_id,license_ids,name,status) values ('t56-s','st-mo','lic-mo','{lic-mo}','T56 Supply','approved');
insert into hx_lots(id,state_id,license_id,number,supplier_id,supplier_name,supplier_status,item,category,quantity,qty_used,unit,status,coa_ok,metrc_tag,location,received_on) values
  ('t56-a','st-mo','lic-mo','RCV-T56A','t56-s','T56 Supply','approved','T56 jars','Packaging',1200,200,'each','accepted',true,'','Rack 1',current_date-20),
  ('t56-b','st-mo','lic-mo','RCV-T56B','t56-s','T56 Supply','approved','T56 flower','Bud/Flower',5000,0,'g','accepted',true,'','Vault',current_date-20),
  ('t56-c','st-mo','lic-mo','RCV-T56C','t56-s','T56 Supply','approved','T56 kief','Kief',100,0,'g','accepted',true,'1A4056000000000000000003','Vault',current_date-20),
  ('t56-x','st-mo','lic-mo','RCV-T56X','t56-s','T56 Supply','approved','T56 bad','Packaging',10,0,'each','rejected',true,'','',current_date-20);
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'C1', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":900}]','count.xlsx');
set test.uid='11111111-1111-1111-1111-111111111111';
select 'C2', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-NOPE","quantity":1,"_row":"7"}]','count.xlsx');
select 'C3', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56X","quantity":1,"_row":"8"}]','count.xlsx');
select 'C4', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":-1,"_row":"9"}]','count.xlsx');
select 'C5', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":5,"unit":"kg","_row":"10"}]','count.xlsx');
select 'C6', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56C","quantity":100,"metrc_tag":"1A4056000000000000000099","_row":"11"}]','count.xlsx');
select 'C7', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":5},{"lot_number":"rcv-t56a","quantity":6}]','count.xlsx');
-- all or nothing: a good update and a bad new row
select 'C8', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":900},{"item":"T56 lids","quantity":5,"unit":"each","supplier":"Nobody","coa_ok":true}]','count.xlsx');
select 'C9 nothing saved', (select quantity-qty_used from hx_lots where id='t56-a'), (select count(*) from hx_lot_counts where lot_id like 't56%');
select 'C10 ok', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":900,"location":"Rack 2","notes":"cycle count"},{"lot_number":"RCV-T56B","quantity":0,"metrc_tag":"1A4056000000000000000002"},{"lot_number":"RCV-T56C","quantity":100,"location":"Vault"},{"item":"T56 lids","quantity":500,"unit":"each","supplier":"T56 Supply","coa_ok":true}]','count.xlsx');
select 'C11 lots', id, quantity, quantity-qty_used, location, metrc_tag from hx_lots where id in ('t56-a','t56-b','t56-c') order by id;
select 'C12 counts', before_qty, counted_qty, unit, source, notes, counted_by<>'' from hx_lot_counts where lot_id like 't56%' order by lot_id;
select 'C13 new lot', status, quantity from hx_lots where item='T56 lids';
select 'C14 audit', count(*) from hx_audit_log where table_name='hx_lots' and row_id='t56-a' and reason='Inventory count from count.xlsx: 1000 -> 900 each';
update hx_lot_counts set counted_qty=1 where lot_id='t56-a';
delete from hx_lot_counts where lot_id='t56-a';
select 'C15 up', hx_inventory_upload('lic-mo','[{"lot_number":"RCV-T56A","quantity":950}]','recount.xlsx');
select 'C16 left', quantity-qty_used from hx_lots where id='t56-a';
