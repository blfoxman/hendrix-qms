\set ON_ERROR_STOP 0
-- step 62: management / HR company on a license
set test.uid='11111111-1111-1111-1111-111111111111';
set session_replication_role=replica; delete from hx_license_settings where license_id='lic-t61'; set session_replication_role=origin;
insert into hx_licenses(id,state_id,name,license_number,license_type,active) values ('lic-t61','st-mo','T61 Mfg','MAN000961','Manufacturing',true) on conflict do nothing;
insert into hx_license_settings(license_id,state_id,legal_name,hr_company) values ('lic-t61','st-mo','Black Fox Manufacturing LLC','HMBF Management Inc.');
select 'H1 saved', legal_name, hr_company from hx_license_settings where license_id='lic-t61';
update hx_license_settings set hr_company=repeat('x',121) where license_id='lic-t61';
select 'H2 too long kept', hr_company from hx_license_settings where license_id='lic-t61';
