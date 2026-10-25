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
chk(len(h['steps']) == 34 and all(x['ok'] for x in h['steps']), 'health: all 34 database steps (4-38) detected')
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
print('\nDB checks:', 'all passed' if not fails else '%d failed' % len(fails))
sys.exit(1 if fails else 0)
