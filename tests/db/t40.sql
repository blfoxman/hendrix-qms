\set ON_ERROR_STOP 0
-- step 40: kiosks keep working without internet (hx_kiosk_sync)
set session_replication_role=replica;
delete from hx_time_clock where profile_id='22222222-2222-2222-2222-222222222222';
delete from hx_kiosk_receipts where client_id like 't40%';
delete from hx_facility_log where performed_by='T40 Tester';
delete from hx_visitor_log where visitor_name='T40 Visitor';
delete from hx_badges where profile_id='22222222-2222-2222-2222-222222222222';
insert into hx_badges(profile_id, code, badge_no) values ('22222222-2222-2222-2222-222222222222','T40MEM','9040');
update hx_profiles set license_ids='{lic-mo}', approved=true where id='22222222-2222-2222-2222-222222222222';
set session_replication_role=origin;
set role anon;
-- offline punches, in the order they were scanned
select 'C1 entry', r->>'event', r->>'name' from (select hx_kiosk_sync('st-mo','lic-mo','clock','t40-c1-0001', now()-interval '3 hours', jsonb_build_object('code','t40mem','date',(now()-interval '3 hours')::date)) r) x;
select 'C2 again', r->>'event', r->>'duplicate' from (select hx_kiosk_sync('st-mo','lic-mo','clock','t40-c1-0001', now()-interval '3 hours', jsonb_build_object('code','t40mem','date',(now()-interval '3 hours')::date)) r) x;
select 'C3 break out', hx_kiosk_sync('st-mo','lic-mo','clock','t40-c3-0003', now()-interval '2 hours', jsonb_build_object('code','T40MEM','date',(now()-interval '2 hours')::date))->>'event';
select 'C4 break in', r->>'event', r->>'late', r->>'late_minutes' from (select hx_kiosk_sync('st-mo','lic-mo','clock','t40-c4-0004', now()-interval '90 minutes', jsonb_build_object('code','T40MEM','date',(now()-interval '90 minutes')::date)) r) x;
select 'C5 double scan', hx_kiosk_sync('st-mo','lic-mo','clock','t40-c5-0005', now()-interval '89 minutes 30 seconds', jsonb_build_object('code','T40MEM','date',(now()-interval '90 minutes')::date))->>'repeat';
select 'C6 too old', hx_kiosk_sync('st-mo','lic-mo','clock','t40-c6-0006', now()-interval '80 hours', jsonb_build_object('code','T40MEM'))->>'error';
select 'C7 future', hx_kiosk_sync('st-mo','lic-mo','clock','t40-c7-0007', now()+interval '1 hour', jsonb_build_object('code','T40MEM'))->>'error';
select 'C8 unknown badge', hx_kiosk_sync('st-mo','lic-mo','clock','t40-c8-0008', now()-interval '1 hour', jsonb_build_object('code','NOPE'))->>'error';
select 'C9 wrong license', hx_kiosk_sync('st-mi','lic-mo','clock','t40-c9-0009', now()-interval '1 hour', jsonb_build_object('code','T40MEM'))->>'error';
select 'C10 short id', hx_kiosk_sync('st-mo','lic-mo','clock','x', now(), '{}');
-- back online: the live kiosk carries on from the offline punches
select 'K1 live', hx_kiosk_clock('st-mo','lic-mo','T40MEM',(now())::date)->>'event';
reset role;
select 'R1 rows', string_agg(event_type || ':' || offline::text || ':' || (synced_at is not null)::text, ',' order by ts) from hx_time_clock where profile_id='22222222-2222-2222-2222-222222222222';
select 'R2 audit reason', count(*) from hx_audit_log where table_name='hx_time_clock' and reason like 'Badge scan (saved on the kiosk while offline)%';
set role anon;
-- facility log and visitor saved offline
select 'L1 log', (hx_kiosk_sync('st-mo','lic-mo','log','t40-l1-0001', now()-interval '5 hours', jsonb_build_object('type','pest','item','Bench','result','pass','performed_by','T40 Tester','signature','data:image/png;base64,xx','data',jsonb_build_object('note','ok'))) ? 'id');
select 'L2 no signature', hx_kiosk_sync('st-mo','lic-mo','log','t40-l2-0002', now()-interval '5 hours', jsonb_build_object('type','pest','performed_by','T40 Tester'))->>'error';
select 'V1 visitor', (hx_kiosk_sync('st-mo','lic-mo','visitor','t40-v1-0001', now()-interval '4 hours', jsonb_build_object('visitor_name','T40 Visitor','purpose','Audit','signature',repeat('x',60),'gmp_ack',true,'ill',false)) ? 'id');
select 'X1 receipts closed', count(*) from hx_kiosk_receipts;
reset role;
select 'L3 performed_at', offline, abs(extract(epoch from (performed_at - (now()-interval '5 hours')))) < 5, created_at > performed_at from hx_facility_log where performed_by='T40 Tester';
select 'V2 time in', offline, abs(extract(epoch from (time_in - (now()-interval '4 hours')))) < 5 from hx_visitor_log where visitor_name='T40 Visitor';
set test.uid='11111111-1111-1111-1111-111111111111';
select 'H1 health', (hx_health_extra()->>'step40')::boolean, (hx_health_extra()->>'kiosk_refused_7d')::int >= 4;
