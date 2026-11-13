\set ON_ERROR_STOP 0
-- step 50: paper SOP records
set session_replication_role=replica;
delete from hx_sop_acks where sop_id like 't50%'; delete from hx_sops where id like 't50%';
insert into hx_sops(id,state_id,license_id,license_ids,title,sop_number,version,status,target_mode,steps,folder,effective_date,next_review) values
  ('t50-s1','st-mo','lic-mo','{lic-mo}','Paper SOP one','SOP-T50-001','1.0','published','license','[]','General','2026-11-01','2027-11-01'),
  ('t50-s2','st-mo','lic-mo','{lic-mo}','Paper SOP two','SOP-T50-002','1.0','published','license','[]','General','2026-11-01','2027-11-01');
insert into hx_sop_acks(id,sop_id,state_id,license_id,version,user_id,name,signature,at) values
  ('t50-a1','t50-s1','st-mo','lic-mo','1.0','22222222-2222-2222-2222-222222222222','Member','sig','2026-11-05 10:00+00');
set session_replication_role=origin;
set test.uid='22222222-2222-2222-2222-222222222222';
select 'P1 not full', hx_sop_paper_records('lic-mo','2026-05-07','{t50-s1}','{22222222-2222-2222-2222-222222222222}','');
set test.uid='11111111-1111-1111-1111-111111111111';
select 'P2 future', hx_sop_paper_records('lic-mo',current_date+1,'{t50-s1}','{}','');
select 'P3 done', hx_sop_paper_records('lic-mo','2026-05-07','{t50-s1,t50-s2}','{22222222-2222-2222-2222-222222222222}','Signed paper copies, binder 2');
select 'P4 sop', id, effective_date, next_review, version from hx_sops where id like 't50%' order by id;
select 'P5 acks', sop_id, paper_on, paper_by is not null, (signature is null), to_char(at,'YYYY-MM-DD') from hx_sop_acks where sop_id like 't50%' order by sop_id;
select 'P6 again', hx_sop_paper_records('lic-mo','2026-05-07','{t50-s1}','{22222222-2222-2222-2222-222222222222}','');
select 'P7 count', count(*) from hx_sop_acks where sop_id like 't50%';
update hx_sop_acks set paper_on='2026-01-01' where id='t50-a1';
select 'P8 locked', paper_on from hx_sop_acks where id='t50-a1';
select 'P9 audit', count(*) from hx_audit_log where row_id in ('t50-a1','t50-s1') and reason like '%paper%';
select 'P10 matrix', to_char(at,'YYYY-MM-DD') from hx_training_sop_acks('lic-mo') where sop_id='t50-s1';
