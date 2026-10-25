set session_replication_role=replica;
delete from hx_holds where id like 'lm%'; delete from hx_tests where id like 'lm%'; delete from hx_line_clearances where id like 'lm%';
delete from hx_deviations where id like 'lm%'; delete from hx_haccp_monitoring where id like 'lm%'; delete from hx_label_prints where id like 'lm%';
delete from hx_shipments where id like 'lm%'; delete from hx_production_plans where id like 'lm%'; delete from hx_time_clock where id like 'lm%';
delete from hx_equipment where id like 'lm%'; delete from hx_batches where id like 'lm%';
insert into hx_batches(id,state_id,license_id,batch_type,batch_number,sku,flavor,status,data,performed_by,created_at,updated_at) values
 ('lm-a','st-mo','lic-mo','cartridges','CT-2026-118','1g AIO Cartridge','Blue Dream','In Progress','{"batch_number":"CT-2026-118","oil_source_batch":"DST-0912","notes":"secret"}','Jordan Ortiz', now()-interval '2 days', now()-interval '10 minutes'),
 ('lm-b','st-mo','lic-mo','cartridges','CT-2026-119','1g AIO Cartridge','Mango','In Progress','{}','Jordan Ortiz', now()-interval '3 days', now()-interval '9 hours'),
 ('lm-c','st-mo','lic-mo','gummies','GM-2026-041','Gummies 10pk','Mango','Completed','{"distillate_qty":"460"}','Ana Morales', now()-interval '5 days', now()-interval '1 day'),
 ('lm-d','st-mo','lic-mo','gummies','GM-2026-038','Gummies 10pk','Grape','Completed','{}','Ana Morales', now()-interval '6 days', now()-interval '1 day'),
 ('lm-e','st-mo','lic-mo','pre_rolls','PR-2026-207','Infused 1g Pre-Roll','Blue Dream','In Progress','{"flower_metrc":"1A4-77","infused_flower_used":"512"}','Lee Park', now()-interval '1 day', now()-interval '12 minutes'),
 ('lm-f','st-mo','lic-mo','cartridges','CT-2026-115','1g AIO Cartridge','Blue Dream','Completed','{"cart_packaged":"980"}','Jordan Ortiz', now()-interval '6 days', now()-interval '3 days'),
 ('lm-g','st-mo','lic-mo','cartridges','CT-2026-112','1g AIO Cartridge','Grape','Completed','{"cart_packaged":"990"}','Jordan Ortiz', now()-interval '8 days', now()-interval '2 days'),
 ('lm-h','st-mo','lic-mo','gummies','GM-2026-045','Gummies 10pk','Watermelon','In Progress','{"distillate_qty":"455","units_produced":"9800"}','Ana Morales', now()-interval '1 day', now()-interval '25 minutes'),
 ('lm-old','st-mo','lic-mo','gummies','GM-2025-001','Gummies','Mango','Completed','{}','x', now()-interval '200 days', now()-interval '190 days'),
 ('lm-mi','st-mi','lic-mi','cartridges','MI-1','x','y','','{}','x', now()-interval '1 day', now());
insert into hx_equipment(id,state_id,license_id,number,name,category,status,cal_required,cal_interval_months,cal_due) values
 ('lm-eq1','st-mo','lic-mo','EQ-014','Cone filler','Production','in_service',true,6,current_date-4),
 ('lm-eq2','st-mo','lic-mo','EQ-002','Cartridge filler','Production','in_service',false,null,null),
 ('lm-eq3','st-mo','lic-mo','EQ-031','Old press','Production','out_of_service',false,null,null);
insert into hx_line_clearances(id,state_id,license_id,number,batch_id,batch_label,area,equipment_ids,result,issues,recorded_by,created_at) values
 ('lm-lc1','st-mo','lic-mo','LC-2026-210','lm-a','CT-2026-118','Filling room','{lm-eq2}','cleared','','Jordan Ortiz',now()-interval '2 days'),
 ('lm-lc2','st-mo','lic-mo','LC-2026-212','lm-b','CT-2026-119','Filling room','{lm-eq2}','not_cleared','Residue on the filler nozzle','Jordan Ortiz',now()-interval '10 hours'),
 ('lm-lc3','st-mo','lic-mo','LC-2026-211','lm-e','PR-2026-207','Pre-roll room','{lm-eq1}','cleared','','Lee Park',now()-interval '1 day'),
 ('lm-lc4','st-mo','lic-mo','LC-2026-205','lm-h','GM-2026-045','Kitchen','{lm-eq2}','cleared','','Ana Morales',now()-interval '1 day'),
 ('lm-lc5','st-mo','lic-mo','LC-2026-190','lm-c','GM-2026-041','Kitchen','{}','cleared','','Ana Morales',now()-interval '5 days');
insert into hx_tests(id,state_id,license_id,batch_id,batch_number,tag,status,lab_name,submitted_at,result_at,created_at,updated_at) values
 ('lm-t1','st-mo','lic-mo','lm-c','GM-2026-041','1A4-GM41','Failed','Show-Me Labs',now()-interval '4 days',now()-interval '2 days',now()-interval '4 days',now()-interval '2 days'),
 ('lm-t2','st-mo','lic-mo','lm-d','GM-2026-038','1A4-GM38','Passed','Show-Me Labs',now()-interval '5 days',now()-interval '3 days',now()-interval '5 days',now()-interval '3 days'),
 ('lm-t3','st-mo','lic-mo','lm-f','CT-2026-115','1A4-CT115','Submitted','Show-Me Labs',now()-interval '3 days',null,now()-interval '3 days',now()-interval '3 days'),
 ('lm-t4','st-mo','lic-mo','lm-g','CT-2026-112','1A4-CT112','Passed','Show-Me Labs',now()-interval '4 days',now()-interval '1 day',now()-interval '4 days',now()-interval '1 day');
insert into hx_holds(id,state_id,license_id,number,kind,batch_id,item,reason,status,placed_by,created_at) values
 ('lm-h1','st-mo','lic-mo','HOLD-2026-012','batch','lm-c','GM-2026-041','Potency 8% over the label claim; retest ordered','open','QA Manager',now()-interval '2 days'),
 ('lm-h2','st-mo','lic-mo','HOLD-2026-009','batch','lm-g','CT-2026-112','Label check','released','QA Manager',now()-interval '3 days');
insert into hx_deviations(id,state_id,license_id,number,title,dept,category,description,occurred_on,source_type,source_id,status,priority,owner_name,created_at) values
 ('lm-dv1','st-mo','lic-mo','DEV-2026-031','Fill weight low on 6 carts','Production','Process','x',current_date,'batch','lm-a','open','minor','Jordan Ortiz',now()-interval '1 hour'),
 ('lm-dv2','st-mo','lic-mo','DEV-2026-020','Closed one','Production','Process','x',current_date,'batch','lm-e','closed','minor','Lee Park',now()-interval '1 day');
insert into hx_haccp_monitoring(id,state_id,license_id,plan_id,plan_version,ccp_id,ccp_name,batch_id,value,within_limits,corrective,recorded_by,created_at) values
 ('lm-m1','st-mo','lic-mo','lm-plan',1,'ccp1','Cooking temperature','lm-h','68 C',false,'Re-heated to 75 C','Ana Morales',now()-interval '25 minutes');
insert into hx_label_prints(id,state_id,license_id,batch_number,tag,sku,flavor,count,created_at) values ('lm-lp1','st-mo','lic-mo','GM-2026-038','1A4-GM38','Gummies','Grape',20,now()-interval '20 hours');
insert into hx_shipments(id,state_id,license_id,number,ship_date,customer,items,status,created_at) values
 ('lm-s1','st-mo','lic-mo','SHP-2026-077',current_date,'Green Leaf Dispensary','[{"batch_id":"lm-d","batch_number":"GM-2026-038","qty":20}]','shipped',now());
insert into hx_production_plans(id,state_id,license_id,number,product_type,sku_name,planned_for,units_per_flavor,lines,status) values
 ('lm-p1','st-mo','lic-mo','PP-2026-019','cartridges','1g AIO Cartridge',current_date+1,500,'[{"flavor":"Grape"},{"flavor":"Lime"}]','planned');
insert into hx_time_clock(id,state_id,license_id,profile_id,person_name,event_type,ts,event_date,source) values
 ('lm-tc1','st-mo','lic-mo','22222222-2222-2222-2222-222222222222','Dana','entry',now()-interval '3 hours',current_date,'kiosk');
insert into hx_license_settings(license_id,state_id) values ('lic-mo','st-mo') on conflict (license_id) do nothing;
update hx_license_settings set linemap_idle_hours=4 where license_id='lic-mo';
set session_replication_role=origin;
