"""Database rule checks that need a real PostgreSQL (run after setup_db.sh <db>).
Each check runs SQL as a given user (auth.uid() comes from the test.uid setting) and asserts the result or the refusal."""
import subprocess, sys, os, re
DB = sys.argv[1] if len(sys.argv) > 1 else 'hxtest'
HERE = os.path.dirname(os.path.abspath(__file__))
res = subprocess.run(['psql', '-X', '-q', '-At', '-d', DB, '-f', os.path.join(HERE, 't36.sql')], capture_output=True, text=True)
out = res.stdout + res.stderr
fails = []
def expect(pattern, msg):
    ok = re.search(pattern, out, re.M) is not None
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails.append(msg)
expect(r'^T1 idle\|4$', 'line map: default idle time 4 h')
expect(r'^T1 batches\|LM-A,LM-B,LM-C,LM-D$', 'line map: only this license, last 45 days, voided batches left out')
expect(r'^T1 notes hidden\|f$', 'line map: batch notes are not returned')
expect(r'^T1 dev A\|DEV-2026-901$', 'line map: open deviation raised from the batch')
expect(r'^T1 hold C\|HOLD-2026-901$', 'line map: open hold on the batch')
expect(r'^T1 tests C\|Failed$', 'line map: test results')
expect(r'^T1 labels D\|1$', 'line map: label prints by batch number')
expect(r'^T1 ship D\|SHP-2026-901$', 'line map: shipments that carry the batch')
expect(r'^T1 equipment\|EQ-901:past its calibration date .* \| EQ-903:out of service$', 'line map: equipment out of service or past calibration')
expect(r'^T1 plans\|PP-2026-901=\["Grape", "Lime"\]$', 'line map: only open plans, with their flavors')
expect(r'^T1 on floor\|1$', 'line map: people on the floor from the time clock')
expect(r'^T2 mi batches\|LM-MI$', 'line map: another license shows only its own batches')
expect(r'You need access to the Line Map for this license', 'line map: refused without Line Map access')
expect(r'^T4 member ok\|t$', 'line map: member with Line Map View can read it')
expect(r'permission denied for function hx_line_map', 'line map: anonymous callers refused')
expect(r'hx_license_settings_idle_chk', 'line map: idle time outside 1-72 h refused')
expect(r'^T7 idle now\|6$', 'line map: idle time follows Settings')
# ---- step 37: system health
def q(sql, uid='11111111-1111-1111-1111-111111111111'):
    r = subprocess.run(['psql', '-X', '-q', '-At', '-d', DB, '-c', "set test.uid='%s'; %s" % (uid, sql)], capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()
import json as _j
h = _j.loads(q('select hx_system_health()::text').split('\n')[-1])
def chk(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: fails.append(msg)
chk(len(h['steps']) == 35 and all(x['ok'] for x in h['steps']), 'health: all 35 database steps (4-39) detected')
chk(set(h['rls_off']) <= {'hx_licenses', 'hx_profiles', 'hx_states'}, 'health: row level security on every table created by steps 4-37')
chk(h['not_audited'] == [] and h['audit_locked'], 'health: every record table audited and the audit trail locked')
chk(h['bucket'] == {'exists': True, 'public': False}, 'health: private file bucket')
chk(h['people']['admins'] == 1 and h['people']['waiting'] == 1, 'health: people counts')
chk('Only an admin can run the system health check' in q('select hx_system_health()', '22222222-2222-2222-2222-222222222222'), 'health: refused for non-admins')
# ---- step 38: e-signatures, two-step sign-in
r38 = subprocess.run(['psql', '-X', '-q', '-At', '-d', DB, '-f', os.path.join(HERE, 't38.sql')], capture_output=True, text=True)
o38 = r38.stdout + r38.stderr
def e38(pattern, msg):
    chk(re.search(pattern, o38, re.M) is not None, msg)
e38(r'^S1 perm before\|1\|t$', 'two-step: normal access before it is required')
e38(r'^S2 perm aal1\|0\|f\|f$', 'two-step: required + password only = no access at all')
e38(r'^S3 perm aal2\|1\|t$', 'two-step: access back after the authenticator step')
e38(r'Only an admin can turn off two-step sign-in', 'two-step: a person cannot turn it off themselves')
e38(r'^S4 still required\|t$', 'two-step: stays required')
e38(r'You cannot sign records of this license', 'e-signature: refused without the second step')
e38(r'^S5 sig\|Mem\|22222222-2222-2222-2222-222222222222$', 'e-signature: signer is always the signed-in person (typed name ignored)')
e38(r'^S6 sig method\|password\+authenticator$', 'e-signature: method recorded')
chk(o38.count('Electronic signatures are permanent') == 2, 'e-signature: cannot be changed or deleted')
e38(r'This license does not belong to that state', 'e-signature: license must belong to the state')
e38(r'^S7 admin turned off\|f$', 'two-step: an admin can turn it off')
e38(r'hx_license_settings_idle_signout_chk', 'auto sign-out: minutes outside 0-480 refused')
e38(r'^S8 defaults\|t\|30$', 'secure defaults: password at signing ON, auto sign-out 30 min')
e38(r'^S9 extra\|t$', 'health: signatures counted')
# ---- step 39: My Tasks inbox + email alerts
r39 = subprocess.run(['psql', '-X', '-q', '-At', '-d', DB, '-f', os.path.join(HERE, 't39.sql')], capture_output=True, text=True)
o39 = r39.stdout + r39.stderr
def e39(pattern, msg):
    chk(re.search(pattern, o39, re.M) is not None, msg)
e39(r'^M1 kinds\|action:t39-ch1,capa:t39-c1,sop_sign:t39-s1,training:t39-tc1,training:t39-tc2$', 'my tasks (member): SOP to sign, CAPA, change action, training needed + expiring; nothing above their level')
e39(r'^M2 first overdue\|t39-ch1\|true$', 'my tasks: overdue first')
e39(r'^M3 other license\|0$', 'my tasks: nothing from a license the person cannot open')
e39(r'^A1 kinds\|action:t39-ch1,calibration:t39-e1,change:t39-ch2,deviation_owner:t39-d1,hold:t39-h1,sop_approve:t39-s2,sop_sign:t39-s4,training:t39-tc1$', 'my tasks (admin): approvals and decisions, SOPs already signed left out')
e39(r'^N1 anonymous\|0$', 'my tasks: nothing without sign-in')
e39(r'^M5 after signing\|0$', 'my tasks: signing the SOP removes the task')
e39(r'^M6 email off\|f$', 'daily email: a person can switch it off')
e39(r'^M7 digest skips\|0$', 'daily email: people who switched it off get none')
e39(r'^Q1 queue\|hold\|Hold placed: HOLD-[0-9-]+ Gummies\|holds$', 'alerts: a new hold is queued')
e39(r'^D1 digest\|Mem=4,Sam=12$', 'daily email: each person gets their own list (worked out with their own access)')
e39(r'^D2 claims restored\|11111111', 'daily email: the session is restored afterwards')
e39(r'^P1 alert recipients\|s@x$', 'alerts: only people with Full access to the area at that license')
e39(r'^P2 sent\|1$', 'alerts: marked sent and logged')
e39(r'^P3 not pending\|0$', 'alerts: sent alerts are not sent again')
chk(o39.count('permission denied for function') == 2, 'email functions closed to signed-in people (service role only)')
e39(r'^S1 status\|t$', 'email status for admins')
e39(r'Only an admin can see the email status', 'email status refused for non-admins')
print('\nDB checks:', 'all passed' if not fails else '%d failed' % len(fails))
sys.exit(1 if fails else 0)
