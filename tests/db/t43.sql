\set ON_ERROR_STOP 0
-- step 43: maintenance and purchase requests, sign-in on QR forms
set session_replication_role=replica;
delete from hx_facility_log where log_type in ('maintenance_request','purchase_request') or performed_by in ('T43 Pest Co','T43 Anon');
delete from hx_kiosk_receipts where client_id like 't43%';
delete from hx_notify_queue where kind='maintenance_urgent';
update hx_profiles set license_ids='{lic-mo}', approved=true, role='member', mfa_required=false where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
set role anon;
select hx_kiosk_log_add('st-mo','lic-mo','sanitation','{"performed_by":"T43 Anon","signature":"data:x","data":{}}');
select 'A1 pest open', hx_kiosk_log_add('st-mo','lic-mo','pest','{"performed_by":"T43 Pest Co","signature":"data:x","data":{}}') like 'fl-%';
select 'A2 sync', hx_kiosk_sync('st-mo','lic-mo','log','t43-sync-0001', now()-interval '1 hour', '{"type":"temperature","performed_by":"T43 Anon","signature":"data:x"}')->>'error';
select hx_kiosk_log_add_user('st-mo','lic-mo','maintenance_request','{"data":{"problem":"x"}}');
reset role;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'U1 maint', (hx_kiosk_log_add_user('st-mo','lic-mo','maintenance_request','{"performed_by":"Someone Else","data":{"problem":"Filler 2 leaking oil","location":"Cart room","priority":"Urgent - safety or production stopped","status":"Done"}}')) ? 'id';
select 'U2 row', performed_by, performed_by_id, result, data->>'status', source from hx_facility_log where log_type='maintenance_request';
select 'U3 purchase', (hx_kiosk_log_add_user('st-mo','lic-mo','purchase_request','{"data":{"item_name":"Nitrile gloves L","quantity":"10","unit":"boxes","needed_by":"2026-11-05","reason":"Running low"}}')) ? 'id';
select hx_kiosk_log_add_user('st-mo','lic-mo','purchase_request','{"data":{"reason":"x"}}');
select hx_kiosk_log_add_user('st-mo','lic-mo','sanitation','{"data":{}}');
select 'U4 sanitation signed', (hx_kiosk_log_add_user('st-mo','lic-mo','sanitation','{"signature":"data:x","data":{"date":"2026-10-27"}}')) ? 'id';
select 'U5 offline', hx_kiosk_log_add_user('st-mo','lic-mo','temperature','{"signature":"data:x","data":{}}','t43-off-0001', now()-interval '2 hours') ? 'id',
  hx_kiosk_log_add_user('st-mo','lic-mo','temperature','{"signature":"data:x","data":{}}','t43-off-0001', now()-interval '2 hours') ->> 'duplicate';
select 'U6 offline row', count(*), bool_and(offline) from hx_facility_log where log_type='temperature' and performed_by_id='22222222-2222-2222-2222-222222222222' and performed_at is not null;
select hx_kiosk_log_add_user('st-mi','lic-mi','purchase_request','{"data":{"item_name":"x"}}');
set test.uid='11111111-1111-1111-1111-111111111111';
select 'T1 tasks', string_agg(t->>'kind', ',' order by t->>'kind') from jsonb_array_elements(hx_my_tasks('lic-mo')) t where t->>'kind' in ('maintenance_request','purchase_request');
select 'N1 urgent alert', count(*) from hx_notify_queue where kind='maintenance_urgent';
update hx_facility_log set result='Approved', data=data||'{"status":"Approved"}', edit_reason='Status: Approved' where log_type='purchase_request';
select 'S1 audit', count(*) > 0 from hx_audit_log where table_name='hx_facility_log' and reason='Status: Approved';
select 'M1 mod', hx_log_mod('maintenance_request'), hx_log_mod('purchase_request');
