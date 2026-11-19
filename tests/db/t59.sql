\set ON_ERROR_STOP 0
-- step 59: cultivation takeover - layout, harvest batches, METRC packages, import
\set bundle `cat tests/db/cul_takeover_fixture.json`
set session_replication_role=replica;
insert into hx_licenses(id,state_id,name,license_number,license_type,active) values ('lic-c59','st-mo','Cul 60 test','CUL000060','Cultivation',true) on conflict do nothing;
update hx_licenses set operation='cultivation' where id='lic-c59';
delete from hx_cul_packages where license_id='lic-c59'; delete from hx_harvests where license_id='lic-c59'; delete from hx_grow_events where license_id='lic-c59';
delete from hx_plant_batches where license_id='lic-c59'; update hx_grow_areas set parent_id=null where license_id='lic-c59'; delete from hx_grow_areas where license_id='lic-c59'; delete from hx_cul_settings where license_id='lic-c59';
set session_replication_role=origin;
set test.uid='11111111-1111-1111-1111-111111111111';
select 'I1 import', hx_cul_import('lic-c59', (:'bundle'::jsonb)->'licenses'->'Cul 60');
select 'A1 houses', count(*) filter (where kind='house'), count(*) filter (where kind='table'), count(*) filter (where kind in ('dry','cure')) from hx_grow_areas where license_id='lic-c59';
select 'A2 table', a.name, a.alias, a.plant_cap, p.code, a.veg from hx_grow_areas a join hx_grow_areas p on p.id=a.parent_id where a.license_id='lic-c59' and a.code='60-H8-T4';
select 'A3 veg', bool_and(veg) from hx_grow_areas where license_id='lic-c59' and (code='60-H1' or code like '60-H1-%');
select 'H1 harvests', count(*), count(*) filter (where active), count(*) filter (where fresh_frozen), count(*) filter (where area_id is not null) from hx_harvests where license_id='lic-c59';
select 'H2 blizzard', h.strain, h.wet_g, h.drying_location, h.metrc_stage, a.code, h.planted_on, h.flip_on from hx_harvests h left join hx_grow_areas a on a.id=h.area_id where h.license_id='lic-c59' and h.name='Test41-11-14-26';
select 'H3 sour', test_result, cure_done, packaged_on from hx_harvests where license_id='lic-c59' and name='TestSauce-07-02-26';
select 'K1 packages', count(*), count(*) filter (where cardinality(source_harvests)>0), count(*) filter (where status='transferred') from hx_cul_packages where license_id='lic-c59';
select 'P1 plants', count(*), sum(plant_count), count(*) filter (where area_id is not null) from hx_plant_batches where license_id='lic-c59';
select 'S1 settings', cycle_days, veg_days, reset_days, overplant_pct from hx_cul_settings where license_id='lic-c59';
-- the team's post-harvest entries are kept on the next import; METRC numbers are not hand-edited
update hx_harvests set dry_room_g=150000, dry_done=current_date-1, note='hung on lines 1-4' where license_id='lic-c59' and name='Test41-11-14-26';
update hx_harvests set wet_g=1 where license_id='lic-c59' and name='Test41-11-14-26';
select 'I2 again', hx_cul_import('lic-c59', (:'bundle'::jsonb)->'licenses'->'Cul 60');
select 'R1 kept', dry_room_g, note, wet_g from hx_harvests where license_id='lic-c59' and name='Test41-11-14-26';
select 'R2 no dupes', count(*) from hx_harvests where license_id='lic-c59';
select 'I3 full list', hx_cul_import('lic-c59', jsonb_build_object('harvests', jsonb_build_array(jsonb_build_object('name','Test41-11-14-26')), 'harvests_full', true))->>'harvests_closed';
select 'R3 active', count(*) filter (where active) from hx_harvests where license_id='lic-c59';
insert into hx_harvests(id,state_id,license_id,name) values ('hv-x','st-mo','lic-c59','by hand');
insert into hx_cul_packages(id,state_id,license_id,tag) values ('cp-x','st-mo','lic-c59','1A4000000000000000000001');
-- layout rules
insert into hx_grow_areas(id,state_id,license_id,name,kind,parent_id) select 'ga-t59x','st-mo','lic-c59','Bad','table',id from hx_grow_areas where license_id='lic-c59' and code='60-H8-T4';
insert into hx_grow_areas(id,state_id,license_id,name,kind,code) values ('ga-t59y','st-mo','lic-c59','Dup','table','60-H8-T4');
-- a harvest recorded in Hendrix opens its harvest batch
set session_replication_role=replica; update hx_plant_batches set stage='flowering' where id=(select id from hx_plant_batches where license_id='lic-c59' order by planted_on, id limit 1); set session_replication_role=origin;
insert into hx_grow_events(id,state_id,license_id,batch_id,kind,done_on,done_by,wet_weight,tag)
  select 'ge59-1','st-mo','lic-c59',id,'harvest',current_date,'Sam',5000,'TEST-H59' from hx_plant_batches where license_id='lic-c59' and stage in ('vegetative','flowering') order by planted_on limit 1;
select 'E1 harvest batch', h.source, h.wet_g, h.plant_batch_id is not null, h.area_id is not null from hx_harvests h where license_id='lic-c59' and name='TEST-H59';
-- only Full access imports
set test.uid='22222222-2222-2222-2222-222222222222';
set session_replication_role=replica; update hx_profiles set perms='{"cultivation":"editor"}', role_ids='{}', role='user', approved=true, license_ids='{lic-c59}' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
select hx_cul_import('lic-c59', '{}'::jsonb);
update hx_harvests set cure_out_g=99000 where license_id='lic-c59' and name='Test41-11-14-26';
select 'U1 edit', cure_out_g from hx_harvests where license_id='lic-c59' and name='Test41-11-14-26';
set test.uid='11111111-1111-1111-1111-111111111111';
