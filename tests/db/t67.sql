\set ON_ERROR_STOP 0
-- step 67: security questions for a forgotten password
set session_replication_role=replica; update auth.users set email='mem@test.com' where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
delete from hx_security_answers; delete from hx_recovery_attempts;
insert into auth.sessions(user_id) values ('22222222-2222-2222-2222-222222222222');
set test.uid='22222222-2222-2222-2222-222222222222';
select 'Q0 not set', hx_my_security_questions()->>'set';
select hx_set_security_questions(array['What was the name of your first pet?','In what city were you born?','Pet?'], array['Rex','Paris','a']);
select hx_set_security_questions(array['What was the name of your first pet?','what was the name of your first pet?','In what city were you born?'], array['Rex','Paris','Blue']);
select hx_set_security_questions(array['What was the name of your first pet?','In what city were you born?','What was your first job?'], array['Rex','x','Line cook']);
select hx_set_security_questions(array['What was the name of your first pet?','In what city were you born?','What was your first job?'], array['Rex','  New   York ','Line cook']);
select 'Q1 set', hx_my_security_questions()->>'set', jsonb_array_length(hx_my_security_questions()->'questions'), hx_my_security_questions()->'questions'->>1;
select 'Q2 hashed', bool_and(a <> 'rex' and a like '$2%') from hx_security_answers, unnest(answers) a where user_id='22222222-2222-2222-2222-222222222222';
select 'Q3 audit', reason from hx_audit_log where table_name='hx_security_answers' order by id desc limit 1;
set role authenticated; select 'Q4 direct read', count(*) from hx_security_answers; reset role;
set test.uid='';
set role anon; select 'Q5 anon set', hx_set_security_questions(array['a','b','c'], array['a','b','c']); reset role;
-- recovery (no sign-in)
set role anon;
select 'R1 real', hx_recovery_questions(' MEM@test.com ')->'questions'->>1;
select 'R2 decoy same', hx_recovery_questions('nobody@test.com') = hx_recovery_questions('nobody@test.com'), jsonb_array_length(hx_recovery_questions('nobody@test.com')->'questions');
select 'R2b decoy distinct', count(distinct q) from jsonb_array_elements_text(hx_recovery_questions('nobody@test.com')->'questions') q;
select 'R3 wrong', hx_recover_with_answers('mem@test.com', array['rex','boston','line cook'], 'NewPass-2026')::text;
select hx_recover_with_answers('mem@test.com', array['rex','new york','line cook'], 'short');
select 'R4 unknown', hx_recover_with_answers('nobody@test.com', array['a','b','c'], 'NewPass-2026')->>'error';
select 'R5 ok', hx_recover_with_answers('mem@test.com', array['REX',' New York','LINE   COOK'], 'NewPass-2026')::text;
reset role;
select 'R6 password', encrypted_password = extensions.crypt('NewPass-2026', encrypted_password) from auth.users where id='22222222-2222-2222-2222-222222222222';
select 'R7 signed out', count(*) from auth.sessions where user_id='22222222-2222-2222-2222-222222222222';
select 'R8 audit', reason, user_name from hx_audit_log where table_name='auth.users' order by id desc limit 1;
-- lockout after 5 wrong tries in an hour
set role anon;
select hx_recover_with_answers('mem@test.com', array['x','y','z'], 'NewPass-2027') from generate_series(1,4);
select 'L1 locked', hx_recover_with_answers('mem@test.com', array['rex','new york','line cook'], 'NewPass-2027')::text;
reset role;
select 'L2 password kept', encrypted_password = extensions.crypt('NewPass-2026', encrypted_password) from auth.users where id='22222222-2222-2222-2222-222222222222';
-- admin sees who has set them; a member cannot
set test.uid='11111111-1111-1111-1111-111111111111'; select 'A1 admin', hx_security_questions_status()::text;
set test.uid='22222222-2222-2222-2222-222222222222'; select 'A2 member', hx_security_questions_status();
set test.uid='';
-- put things back
set session_replication_role=replica; update auth.users set email='m@x', encrypted_password=null where id='22222222-2222-2222-2222-222222222222'; set session_replication_role=origin;
delete from hx_recovery_attempts;
