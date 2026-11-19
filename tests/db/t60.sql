\set ON_ERROR_STOP 0
-- step 60: METRC -> Hendrix inventory sync
set session_replication_role=replica;
insert into hx_licenses(id,state_id,name,license_number,license_type,active) values ('lic-t60','st-mo','T60 Mfg','MAN000960','Manufacturing',true) on conflict do nothing;
delete from hx_lot_counts where license_id='lic-t60'; delete from hx_metrc_syncs where license_id='lic-t60'; delete from hx_metrc_snapshots where license_id='lic-t60'; delete from hx_lots where license_id='lic-t60';
insert into hx_suppliers(id,state_id,license_id,license_ids,name,status) values ('t60-s','st-mo','lic-t60','{lic-t60}','T60 Farms','approved') on conflict do nothing;
insert into hx_lots(id,state_id,license_id,number,supplier_id,supplier_name,supplier_status,item,category,quantity,unit,qty_used,status,coa_ok,metrc_tag,location,received_on) values
  ('t60-a','st-mo','lic-t60','RCV-T60A','t60-s','T60 Farms','approved','Flower A','Cannabis (flower, trim, biomass)',1000,'g',0,'accepted',true,'1A4000000000000000006001','Vault',current_date-9),
  ('t60-b','st-mo','lic-t60','RCV-T60B','t60-s','T60 Farms','approved','Distillate B','Distillate / extract',2,'kg',0,'accepted',true,'1A4000000000000000006002','Vault',current_date-8),
  ('t60-c','st-mo','lic-t60','RCV-T60C','t60-s','T60 Farms','approved','Flower C','Cannabis (flower, trim, biomass)',500,'g',100,'accepted',true,'1A4000000000000000006003','Vault',current_date-7),
  ('t60-d','st-mo','lic-t60','RCV-T60D','t60-s','T60 Farms','approved','Carts D','Distillate / extract',100,'each',0,'accepted',true,'1A4000000000000000006004','Vault',current_date-6),
  ('t60-e','st-mo','lic-t60','RCV-T60E','t60-s','T60 Farms','approved','Flower E','Cannabis (flower, trim, biomass)',300,'g',0,'accepted',true,'1A4000000000000000006005','Vault',current_date-5);
set session_replication_role=origin;
set test.uid='11111111-1111-1111-1111-111111111111';
-- A: 750 g; B: 1.5 kg sent as 1500 g; C: gone from METRC (-> 0); D: 'ea' 80; E: METRC in lb vs grams ok (0.5 lb); plus one METRC package not in Hendrix
select 'S1 sync', hx_metrc_inventory_sync('lic-t60', '[{"tag":"1A4000000000000000006001","qty":"750","unit":"g","location":"Production Floor"},
  {"tag":"1A40 0000 0000 0000 0000 6002","qty":"1500","unit":"g"},{"tag":"1A4000000000000000006004","qty":"80","unit":"ea"},
  {"tag":"1A4000000000000000006005","qty":"0.5","unit":"lb"},{"tag":"1A4000000000000000009999","qty":"10","unit":"g","item":"New thing"}]'::jsonb, 'METRC test') - 'id' - 'snapshot';
select 'L1 lots', string_agg(number || '=' || (quantity - qty_used)::text || ' ' || unit || '@' || location, ', ' order by number) from hx_lots where license_id='lic-t60';
select 'C1 counts', count(*), count(*) filter (where counted_qty = 0) from hx_lot_counts where license_id='lic-t60';
select 'K1 snapshot', count(*) from hx_metrc_snapshots where license_id='lic-t60' and source='api';
select 'S2 again', (hx_metrc_inventory_sync('lic-t60', '[{"tag":"1A4000000000000000006001","qty":"750","unit":"g","location":"Production Floor"},{"tag":"1A4000000000000000006002","qty":"1500","unit":"g"},{"tag":"1A4000000000000000006004","qty":"80","unit":"ea"},{"tag":"1A4000000000000000006005","qty":"0.5","unit":"lb"}]'::jsonb, 'METRC test'))->>'counted';
select 'K2 one snapshot an hour', count(*) from hx_metrc_snapshots where license_id='lic-t60' and source='api';
-- a partial read (most tags missing) never empties the inventory
select 'S3 partial', (hx_metrc_inventory_sync('lic-t60', '[{"tag":"1A4000000000000000006001","qty":"700","unit":"g"}]'::jsonb, 'METRC test'))->>'zeroed';
select 'L2 kept', (quantity - qty_used) from hx_lots where id='t60-b';
-- units that do not convert, more than received
select 'S4 skip', (hx_metrc_inventory_sync('lic-t60', '[{"tag":"1A4000000000000000006001","qty":"5","unit":"ea"},{"tag":"1A4000000000000000006002","qty":"9","unit":"kg"},{"tag":"1A4000000000000000006004","qty":"80","unit":"ea"},{"tag":"1A4000000000000000006005","qty":"200","unit":"g"}]'::jsonb, 'METRC test'))->'skipped';
select 'Y1 syncs', count(*) from hx_metrc_syncs where license_id='lic-t60';
-- Full access to Receiving only
set test.uid='22222222-2222-2222-2222-222222222222';
set session_replication_role=replica; update hx_profiles set perms='{"receiving":"editor"}', role_ids='{}', role='user', approved=true, license_ids='{lic-t60}' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
select hx_metrc_inventory_sync('lic-t60', '[]'::jsonb, 'x');
set test.uid='11111111-1111-1111-1111-111111111111';
