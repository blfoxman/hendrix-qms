\set ON_ERROR_STOP 0
-- step 61: Manufacturing Process (runs + per-license items)
set session_replication_role=replica;
insert into hx_licenses(id,state_id,name,license_number,license_type,active) values ('lic-t61','st-mo','T61 Mfg','MAN000961','Manufacturing',true) on conflict do nothing;
delete from hx_mp_runs where license_id='lic-t61'; delete from hx_mp_items where license_id='lic-t61';
update hx_profiles set perms='{"batch":"editor"}', role_ids='{}', role='user', approved=true, license_ids='{lic-t61}' where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
set test.uid='11111111-1111-1111-1111-111111111111';
insert into hx_mp_items(id,state_id,license_id,name,unit,use_in) values ('t61-i1','st-mo','lic-t61','Hash','g','both'),('t61-i2','st-mo','lic-t61','Rosin','g','product');
select 'I1 items', count(*) from hx_mp_items where license_id='lic-t61';
insert into hx_mp_items(id,state_id,license_id,name) values ('t61-i3','st-mo','lic-t61',' hash ');
select 'I2 dup name', 'x';
insert into hx_mp_runs(id,state_id,license_id,run_date,materials,produced,status) values
 ('t61-r1','st-mo','lic-t61','2026-11-20','[{"tag":"1A4000000000000000006101","item":"Hash","weight":"500","unit":"g"}]','[{"rows":[{"tag":"1A4000000000000000006102","item":"Rosin","weight":"300","unit":"g"}],"waste":{"weight":"20","note":"press loss"}}]','complete');
insert into hx_mp_runs(id,state_id,license_id,run_date,materials,produced) values
 ('t61-r2','st-mo','lic-t61','2026-11-20','[{"tag":"","item":"Rosin","weight":"300"},{"tag":"","item":"Hash","weight":"10"}]','[{"rows":[{"item":"Rosin","weight":"250"}]},{"rows":[{"item":"Rosin 1g jar","weight":"240"}],"waste":{"weight":"","note":""}}]');
select 'R1 numbers', string_agg(number, ',' order by number), count(*) from hx_mp_runs where license_id='lic-t61';
select 'R2 stages', jsonb_array_length(produced) from hx_mp_runs where id='t61-r2';
insert into hx_mp_runs(id,state_id,license_id,materials,produced) values ('t61-bad1','st-mo','lic-t61','[]','[{"rows":[{"item":"Rosin","weight":"1"}]}]');
insert into hx_mp_runs(id,state_id,license_id,materials,produced) values ('t61-bad2','st-mo','lic-t61','[{"item":"Hash","weight":"abc"}]','[{"rows":[{"item":"Rosin","weight":"1"}]}]');
insert into hx_mp_runs(id,state_id,license_id,materials,produced) values ('t61-bad3','st-mo','lic-t61','[{"item":"Hash","weight":"5"}]','[]');
insert into hx_mp_runs(id,state_id,license_id,materials,produced) values ('t61-bad4','st-mo','lic-t61','[{"item":"","weight":"5"}]','[{"rows":[{"item":"Rosin","weight":"1"}]}]');
select 'B1 rejected', count(*) from hx_mp_runs where id like 't61-bad%';
-- changing a Complete run needs a reason; the number never changes
update hx_mp_runs set note='no reason' where id='t61-r1';
update hx_mp_runs set note='fixed typo', edit_reason='typo', number='HACK' where id='t61-r1';
select 'E1 edit', note, number from hx_mp_runs where id='t61-r1';
select 'E2 audit reason', reason from hx_audit_log where table_name='hx_mp_runs' and row_id='t61-r1' and action='UPDATE' order by at desc limit 1;
delete from hx_mp_runs where id='t61-r1';
-- editor: records runs and adds items, cannot rename items or void
set test.uid='22222222-2222-2222-2222-222222222222';
insert into hx_mp_items(id,state_id,license_id,name) values ('t61-i4','st-mo','lic-t61','Distillate');
select 'P1 editor item', count(*) from hx_mp_items where id='t61-i4';
update hx_mp_items set name='Distillate X' where id='t61-i4';
select 'P2 editor rename blocked', name from hx_mp_items where id='t61-i4';
insert into hx_mp_runs(id,state_id,license_id,run_date,materials,produced) values ('t61-r3','st-mo','lic-t61','2026-11-21','[{"item":"Hash","weight":"5"}]','[{"rows":[{"item":"Rosin","weight":"1"}]}]');
select 'P3 editor run', number from hx_mp_runs where id='t61-r3';
update hx_mp_runs set voided=true, void_reason='nope' where id='t61-r3';
select 'P4 editor void blocked', voided from hx_mp_runs where id='t61-r3';
-- read only: sees, cannot record
set session_replication_role=replica; update hx_profiles set perms='{"batch":"read"}' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
set role authenticated;
select 'V1 read sees', count(*) from hx_mp_runs where license_id='lic-t61';
reset role;
insert into hx_mp_runs(id,state_id,license_id,materials,produced) values ('t61-r4','st-mo','lic-t61','[{"item":"Hash","weight":"5"}]','[{"rows":[{"item":"Rosin","weight":"1"}]}]');
select 'V2 read blocked', count(*) from hx_mp_runs where id='t61-r4';
-- no batch access: sees nothing
set session_replication_role=replica; update hx_profiles set perms='{}' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
set role authenticated;
select 'V3 none sees', (select count(*) from hx_mp_runs where license_id='lic-t61') runs, (select count(*) from hx_mp_items where license_id='lic-t61') items;
reset role;
-- admin voids with a reason
set test.uid='11111111-1111-1111-1111-111111111111';
update hx_mp_runs set voided=true where id='t61-r3';
update hx_mp_runs set voided=true, void_reason='entered on the wrong license' where id='t61-r3';
select 'X1 voided', voided, void_reason from hx_mp_runs where id='t61-r3';
update hx_mp_runs set note='after void', edit_reason='x' where id='t61-r3';
-- SKU option lists (Infused with / Coated with), per state
set test.uid='11111111-1111-1111-1111-111111111111';
set session_replication_role=replica; delete from hx_sku_options where id like 't61-o%'; set session_replication_role=origin;
insert into hx_sku_options(id,state_id,kind,name) values ('t61-o1','st-mo','infusion',' Live Rosin '),('t61-o2','st-mo','coating','Moon Dust');
select 'O1 options', string_agg(name, ',' order by name) from hx_sku_options where id like 't61-o%';
insert into hx_sku_options(id,state_id,kind,name) values ('t61-o3','st-mo','infusion','live rosin');
insert into hx_sku_options(id,state_id,kind,name) values ('t61-o4','st-mo','solvent','X');
select 'O2 dup and bad kind', count(*) from hx_sku_options where id in ('t61-o3','t61-o4');
update hx_sku_options set active=false, kind='coating' where id='t61-o1';
update hx_sku_options set active=false where id='t61-o1';
select 'O3 switched off', active, kind from hx_sku_options where id='t61-o1';
delete from hx_sku_options where id='t61-o1';
select 'O4 no delete', count(*) from hx_sku_options where id='t61-o1';
set session_replication_role=replica; update hx_profiles set perms='{"products":"editor"}' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
insert into hx_sku_options(id,state_id,kind,name) values ('t61-o5','st-mo','infusion','Rosin');
select 'O5 editor adds', count(*) from hx_sku_options where id='t61-o5';
set session_replication_role=replica; update hx_profiles set perms='{"products":"read"}' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
insert into hx_sku_options(id,state_id,kind,name) values ('t61-o6','st-mo','infusion','Kief Hash');
set role authenticated;
select 'O6 read sees, cannot add', (select count(*) from hx_sku_options where id like 't61-o%'), (select count(*) from hx_sku_options where id='t61-o6');
reset role;
