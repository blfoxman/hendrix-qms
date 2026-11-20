\set ON_ERROR_STOP 0
-- step 63: run status, save unfinished and come back
set test.uid='11111111-1111-1111-1111-111111111111';
set session_replication_role=replica; delete from hx_mp_runs where id like 't63-%'; set session_replication_role=origin;
insert into hx_licenses(id,state_id,name,license_number,license_type,active) values ('lic-t63','st-mo','T63 Mfg','MAN000963','Manufacturing',true) on conflict do nothing;
insert into hx_mp_runs(id,state_id,license_id,run_date,materials,produced) values
 ('t63-r1','st-mo','lic-t63','2026-11-20','[{"tag":"1A40C03000060E1000003242","item":"HTE","weight":"1294","unit":"g"},{"tag":"1A40C03000060E1000003215","item":"HTE","weight":"","unit":"g"}]',
  '[{"rows":[{"tag":"1A40C03000060E1000003277","item":"Decarbed Cured Resin","weight":"","unit":"g"}],"waste":{"weight":"","note":""}},{"rows":[],"waste":{"weight":"","note":""}}]');
select 'S1 saved unfinished', number, status, completed_at is null from hx_mp_runs where id='t63-r1';
update hx_mp_runs set note='first weights' where id='t63-r1';
select 'S2 no reason while open', reason from hx_audit_log where table_name='hx_mp_runs' and row_id='t63-r1' and action='UPDATE' order by at desc limit 1;
update hx_mp_runs set status='testing' where id='t63-r1';
select 'S3 status change logged', reason from hx_audit_log where table_name='hx_mp_runs' and row_id='t63-r1' and action='UPDATE' order by at desc limit 1;
update hx_mp_runs set status='complete' where id='t63-r1';
select 'S4 complete blocked', status from hx_mp_runs where id='t63-r1';
update hx_mp_runs set materials=jsonb_set(materials,'{1,weight}','"459"') where id='t63-r1';
update hx_mp_runs set materials=jsonb_set(materials,'{1,weight}','"abc"') where id='t63-r1';
update hx_mp_runs set status='passed', produced='[{"rows":[{"tag":"1A40C03000060E1000003277","item":"Decarbed Cured Resin","weight":"1500","unit":"g"}],"waste":{"weight":"40","note":"loss"}}]' where id='t63-r1';
update hx_mp_runs set status='complete' where id='t63-r1';
select 'S5 complete', status, completed_at is not null from hx_mp_runs where id='t63-r1';
update hx_mp_runs set note='after complete' where id='t63-r1';
update hx_mp_runs set status='testing', edit_reason='retest ordered' where id='t63-r1';
select 'S6 reopened', status, completed_at is null, note from hx_mp_runs where id='t63-r1';
update hx_mp_runs set status='done' where id='t63-r1';
select 'S7 status', status from hx_mp_runs where id='t63-r1';
