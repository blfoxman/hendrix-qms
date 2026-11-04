\set ON_ERROR_STOP 0
-- step 46: GMP Hygiene Walk and the private Employee Illness and Exclusion Log
set session_replication_role=replica;
delete from hx_roles where id='t46-logs';
insert into hx_roles (id, name, perms) values ('t46-logs', 'T46 Logs admin', '{"logs":"admin"}');
update hx_profiles set role='member', approved=true, mfa_required=false, license_ids='{lic-mo}', perms='{}', role_ids='{t46-logs}' where id='22222222-2222-2222-2222-222222222222';
delete from hx_facility_log where performed_by like 'T46%';
set session_replication_role=origin;
select 'V1 types', hx_fl_valid_type('gmp_walk'), hx_fl_valid_type('illness'), hx_fl_valid_type('nope');
select 'V2 mods', hx_log_mod('gmp_walk'), hx_log_mod('illness');
set test.uid='22222222-2222-2222-2222-222222222222';
select 'P1 logs-all', hx_can('logs_gmp',2,'lic-mo'), hx_can('hr_health',1,'lic-mo');
reset test.uid;
set session_replication_role=replica;
update hx_roles set perms='{"logs":"admin","hr_health":"editor"}' where id='t46-logs';
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'P2 own setting', hx_can('hr_health',2,'lic-mo');
select 'K1 kiosk', hx_kiosk_log_add_user('st-mo','lic-mo','illness','{"signature":"data:x","data":{"employee":"x"}}');
reset test.uid;
insert into hx_facility_log (id, state_id, license_id, log_type, item, data, result, performed_by, source)
  values ('fl-t46a', 'st-mo', 'lic-mo', 'illness', 'T46 Person', '{"reason":"Vomiting"}', 'Open', 'T46 PIC', 'app');
select 'I1 app entry', count(*) from hx_facility_log where id='fl-t46a';
insert into hx_facility_log (id, state_id, license_id, log_type, item, data, result, performed_by, source)
  values ('fl-t46b', 'st-mo', 'lic-mo', 'gmp_walk', 'Gummy Room', '{"hair":"Pass"}', 'Pass', 'T46 PIC', 'app');
select 'G1 walk', count(*) from hx_facility_log where id='fl-t46b';
select 'H1 health', hx_fl_types() @> array['gmp_walk','illness'];
