\set ON_ERROR_STOP 0
-- step 52: cultivation batch tracker - post-harvest stages and targets
set session_replication_role=replica;
insert into hx_licenses(id,state_id,name,license_number,license_type,active) values ('lic-c52','st-mo','Cul 52','CUL000052','Cultivation',true) on conflict do nothing;
update hx_licenses set operation='cultivation' where id='lic-c52';
delete from hx_grow_events where license_id='lic-c52'; delete from hx_plant_batches where license_id='lic-c52'; delete from hx_cul_settings where license_id in ('lic-c52','lic-mo');
insert into hx_grow_areas(id,state_id,license_id,name,kind) values ('ga-52','st-mo','lic-c52','Flower 1','indoor') on conflict do nothing;
insert into hx_plant_batches(id,state_id,license_id,number,cultivar,source_kind,planted_on,plant_count,area_id,stage) values
  ('pb-52','st-mo','lic-c52','PB-52','Gelato','seed_own',current_date-100,40,'ga-52','flowering'),
  ('pb-52b','st-mo','lic-c52','PB-52B','Zkittlez','seed_own',current_date-10,20,'ga-52','vegetative');
set session_replication_role=origin;
set test.uid='11111111-1111-1111-1111-111111111111';
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,wet_weight,tag) values ('ge52-1','st-mo','lic-c52','pb-52','harvest',current_date-20,'Sam',10000,'HB-52');
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,conditions) values ('ge52-2','st-mo','lic-c52','pb-52','dry',current_date-12,'Sam','60F 60%');
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,dry_weight) values ('ge52-3','st-mo','lic-c52','pb-52','cure',current_date-5,'Sam',2500);
select 'B1 after cure', stage, dry_weight from hx_plant_batches where id='pb-52';
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by) values ('ge52-x1','st-mo','lic-c52','pb-52','packaged',current_date,'Sam');
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by) values ('ge52-x2','st-mo','lic-c52','pb-52','lab',current_date,'Sam');
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,observations) values ('ge52-4','st-mo','lic-c52','pb-52','lab',current_date-4,'Sam','Kaycha, 30 g sample');
select 'B2 lab stays', stage from hx_plant_batches where id='pb-52';
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by) values ('ge52-x3','st-mo','lic-c52','pb-52','tested',current_date,'Sam');
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,tag) values ('ge52-5','st-mo','lic-c52','pb-52','tested',current_date-2,'Sam','COA-52');
select 'B3 tested', stage from hx_plant_batches where id='pb-52';
update hx_grow_events set voided=true, void_reason='wrong' where id='ge52-5';
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,observations) values ('ge52-6','st-mo','lic-c52','pb-52','packaged',current_date-1,'Sam','400 x 3.5 g');
select 'B4 packaged', stage from hx_plant_batches where id='pb-52';
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by) values ('ge52-x4','st-mo','lic-c52','pb-52','shipped',current_date,'Sam');
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,observations,tag) values ('ge52-7','st-mo','lic-c52','pb-52','shipped',current_date,'Sam','Black Fox MAN000109','MAN-52');
select 'B5 shipped', stage from hx_plant_batches where id='pb-52';
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,observations) values ('ge52-x5','st-mo','lic-c52','pb-52','scouting',current_date,'Sam','late');
select 'B6 audit', count(*) from hx_audit_log where table_name='hx_plant_batches' and row_id='pb-52' and reason in ('Sent to the lab','Test passed (COA)','Packaged','Shipped / transferred');
update hx_plant_batches set harvest_start=current_date+3 where id='pb-52b';
select 'B7 harvest start', harvest_start=current_date+3 from hx_plant_batches where id='pb-52b';
insert into hx_cul_settings(license_id,state_id,cycle_days,veg_days) values ('lic-c52','st-mo',70,70);
insert into hx_cul_settings(license_id,state_id,cycle_days,veg_days) values ('lic-mo','st-mo',70,10);
insert into hx_cul_settings(license_id,state_id,cycle_days,veg_days,cure_days) values ('lic-c52','st-mo',75,0,21);
select 'B8 targets', cycle_days, veg_days, window_days, cure_days, updated_by<>'' from hx_cul_settings where license_id='lic-c52';
set test.uid='22222222-2222-2222-2222-222222222222';
update hx_cul_settings set cycle_days=90 where license_id='lic-c52';
select 'B9 member', cycle_days from hx_cul_settings where license_id='lic-c52';
set test.uid='11111111-1111-1111-1111-111111111111';
select 'B10 unchanged', cycle_days from hx_cul_settings where license_id='lic-c52';
