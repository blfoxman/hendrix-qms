import re, datetime as dt, base64, subprocess, copy
exec(open('/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/mock_c.py').read())  
errors = []
SH = OUT + 'manual/shots/'
NOWD = dt.datetime.utcnow()
def ago(d, h=0): return (NOWD - dt.timedelta(days=d, hours=h)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
def day(d): return (NOWD + dt.timedelta(days=d)).strftime('%Y-%m-%d')
PW = 'Correct-Horse-9'
M1 = '22222222-2222-2222-2222-222222222222'
T['hx_states'] = [{'id': 'st-mo', 'name': 'Missouri', 'agency': 'Division of Cannabis Regulation (DCR)', 'code': '19 CSR 100-1'}, {'id': 'st-mi', 'name': 'Michigan', 'agency': 'Cannabis Regulatory Agency (CRA)', 'code': 'R 420'}]
T['hx_licenses'] = [{'id': 'lic-mo', 'state_id': 'st-mo', 'name': 'Black Fox', 'license_number': 'MAN000109', 'license_type': 'Manufacturer', 'operation': 'manufacturing', 'active': True},
                    {'id': 'lic-mi', 'state_id': 'st-mi', 'name': 'Key Stone', 'license_number': 'PR-000231', 'license_type': 'Processor', 'operation': 'manufacturing', 'active': True}]
T['hx_profiles'] = [{'id': ADMIN, 'name': 'Sam Salari', 'email': 'sam@blackfoxmfg.com', 'role': 'admin', 'approved': True, 'role_ids': [], 'perms': {}, 'license_ids': [], 'mfa_required': False, 'task_email': True, 'created_at': '2026-01-05'},
                    {'id': M1, 'name': 'Maria Lopez', 'email': 'maria.lopez@blackfoxmfg.com', 'role': 'member', 'approved': True, 'role_ids': [], 'perms': {'sops': 'read', 'qms': 'editor'}, 'license_ids': ['lic-mo'], 'mfa_required': False, 'created_at': '2026-02-11'}]
T['hx_license_settings'] = [{'license_id': 'lic-mo', 'state_id': 'st-mo', 'legal_name': 'Black Fox Manufacturing LLC', 'dba': 'Black Fox', 'address': '', 'phone': '', 'email': '', 'print_footer': '', 'logo': None,
                             'break1_min': 15, 'break2_min': 30, 'break3_min': 15, 'log_due': {}, 'review_days': {}, 'linemap_idle_hours': 4, 'esig_password': True, 'idle_signout_min': 30}]
T['hx_sops'] = [{'id': 'sop-1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Cartridge Filling', 'sop_number': 'SOP-PRD-004', 'version': '2.0', 'status': 'draft',
                 'folder': 'Production', 'department': 'Production', 'description': 'Filling 1 g distillate cartridges on Filler 2.', 'steps': [{'n': 1, 'text': 'Line clearance.'}], 'attachments': [], 'created_by': 'Maria Lopez', 'created_by_id': M1,
                 'created_at': ago(2), 'updated_at': ago(2), 'approved_by': '', 'approved_at': None, 'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'previous_folder': '', 'revision_note': 'New filler', 'effective_date': None, 'next_review': None, 'generated_content': None}]
TASKS = [
 {'kind': 'calibration', 'group': 'approve', 'page': 'equipment', 'title': 'Calibration due: EQ-014 Cone filler', 'detail': 'Pre-roll room', 'due': day(-2), 'overdue': True, 'ref': 'e1'},
 {'kind': 'capa', 'group': 'mine', 'page': 'qms', 'title': 'CAPA CAPA-2026-007: Filler 2 overfill', 'detail': 'Priority major · in progress', 'due': day(-1), 'overdue': True, 'ref': 'c1'},
 {'kind': 'ccp', 'group': 'approve', 'page': 'haccp', 'title': 'Verify out-of-limit CCP check: Cooking temperature', 'detail': 'Value 68 C · Oct 25 11:39', 'due': day(1), 'overdue': False, 'ref': 'm1'},
 {'kind': 'test_result', 'group': 'approve', 'page': 'testing', 'title': 'Enter test result: CART-2026-121', 'detail': 'Show-Me Labs · sample 1A4-CT121', 'due': day(3), 'overdue': False, 'ref': 't1'},
 {'kind': 'training', 'group': 'mine', 'page': 'training', 'title': 'Training expires soon: Forklift operation', 'detail': 'Completed Nov 02, 2025', 'due': day(8), 'overdue': False, 'ref': 'tc1'},
 {'kind': 'sop_sign', 'group': 'mine', 'page': 'sops', 'title': 'Read and sign: Allergen Control', 'detail': 'SOP-QA-011 v3.0', 'due': None, 'overdue': False, 'ref': 's2'},
 {'kind': 'sop_approve', 'group': 'approve', 'page': 'sops', 'title': 'Approve SOP draft: Cartridge Filling', 'detail': 'SOP-PRD-004 v2.0', 'due': None, 'overdue': False, 'ref': 'sop-1'},
 {'kind': 'hold', 'group': 'approve', 'page': 'holds', 'title': 'Decide hold HOLD-2026-013: GM-2026-041', 'detail': 'Potency 8% over the label claim; retest ordered', 'due': None, 'overdue': False, 'ref': 'h1'},
 {'kind': 'lot', 'group': 'approve', 'page': 'receiving', 'title': 'Accept or reject lot LOT-2026-088: Distillate', 'detail': 'Received Oct 24, 2026 from Midwest Extracts', 'due': None, 'overdue': False, 'ref': 'l1'},
 {'kind': 'change', 'group': 'approve', 'page': 'changes', 'title': 'Approve change CC-2026-006: Second cartridge filler', 'detail': 'Requested by Maria Lopez · risk medium', 'due': day(14), 'overdue': False, 'ref': 'ch1'}]
NSTAT = {'pending_alerts': 0, 'last_sent': ago(0, 3), 'last_digest': ago(0, 3), 'failed_7d': 0, 'sent_7d': 41, 'people_off': 1, 'recent': [
 {'sent_at': ago(0, 1), 'kind': 'alert', 'email': 'sam@blackfoxmfg.com', 'subject': 'Hendrix ALERT: Hold placed: HOLD-2026-013 GM-2026-041 (Black Fox)', 'items': 1, 'status': 'sent', 'error': ''},
 {'sent_at': ago(0, 3), 'kind': 'digest', 'email': 'sam@blackfoxmfg.com', 'subject': 'Hendrix: 10 tasks waiting (2 overdue)', 'items': 10, 'status': 'sent', 'error': ''},
 {'sent_at': ago(0, 3), 'kind': 'digest', 'email': 'maria.lopez@blackfoxmfg.com', 'subject': 'Hendrix: 3 tasks waiting', 'items': 3, 'status': 'sent', 'error': ''}]}
SNAP = {'id': 'ms-1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'source': 'csv', 'file_name': 'Packages_Active_2026-10-25.csv', 'packages': 214, 'taken_by': 'Sam Salari', 'created_at': ago(0, 1)}
T['hx_metrc_snapshots'] = [SNAP]
FIND = [
 {'kind': 'hold', 'severity': 'high', 'tag': '1A4000000000000000004127', 'title': 'On hold in METRC, no open hold in Hendrix', 'detail': 'Blue Dream 1g Pre-roll', 'page': 'holds', 'ref': ''},
 {'kind': 'lab', 'severity': 'high', 'tag': '1A4000000000000000003981', 'title': 'Passed in Hendrix, METRC lab status is SubmittedForTesting', 'detail': 'Sour Diesel 1g Cartridge · batch CART-2026-118', 'page': 'testing', 'ref': 't'},
 {'kind': 'shipped', 'severity': 'medium', 'tag': '1A4000000000000000003902', 'title': 'Shipped in Hendrix (Oct 23), still active in METRC', 'detail': 'Mixed Berry Gummies 100mg · check the METRC transfer', 'page': 'shipping', 'ref': 's'},
 {'kind': 'lot', 'severity': 'medium', 'tag': '1A4000000000000000003655', 'title': 'Lot LOT-2026-071 has 50 g left in Hendrix, not active in METRC', 'detail': 'Terpene blend', 'page': 'receiving', 'ref': 'l'},
 {'kind': 'quantity', 'severity': 'low', 'tag': '1A4000000000000000003710', 'title': 'Quantity: Hendrix 800 g, METRC 700 Grams', 'detail': 'Lot LOT-2026-080 · Distillate', 'page': 'receiving', 'ref': 'l2'},
 {'kind': 'unknown', 'severity': 'info', 'tag': '1A4000000000000000004188', 'title': 'In METRC, not in Hendrix', 'detail': 'Live Rosin 1g · B-77', 'page': '', 'ref': ''}]
AUTH = {'factors': []}
def jwt(aal):
    return 'h.' + base64.urlsafe_b64encode(json.dumps({'sub': ADMIN, 'aal': aal}).encode()).decode().rstrip('=') + '.s'
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def psql_json(sql):
    out = subprocess.run(['psql', '-X', '-q', '-At', '-h', '/tmp/hxpg', '-U', 'postgres', '-d', 'hxtest', '-c', "set test.uid='" + ADMIN + "'; " + sql], capture_output=True, text=True)
    return json.loads(out.stdout.strip().split('\n')[-1])
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    body = json.loads(request.post_data) if request.post_data else {}
    if '/auth/v1/' in u:
        if path.endswith('/token'):
            return jr(route, {'access_token': jwt('aal1'), 'refresh_token': 'r', 'expires_in': 3600, 'user': {'id': ADMIN, 'email': 'sam@blackfoxmfg.com'}}) if body.get('password') == PW else jr(route, {'error_description': 'Invalid login credentials'}, 400)
        if path.endswith('/user'): return jr(route, {'id': ADMIN, 'factors': AUTH['factors']})
        if path.endswith('/factors'):
            return jr(route, {'id': 'f-1', 'factor_type': 'totp', 'status': 'unverified', 'totp': {'qr_code': QR, 'secret': 'JBSWY3DPEHPK3PXP'}})
        if path.endswith('/challenge'): return jr(route, {'id': 'ch-1'})
        return jr(route, {})
    if path.endswith('/rpc/hx_my_tasks'): return jr(route, TASKS)
    if path.endswith('/rpc/hx_notify_status'): return jr(route, NSTAT)
    if path.endswith('/rpc/hx_metrc_reconcile'): return jr(route, {'snapshot': SNAP, 'findings': FIND})
    if path.endswith('/rpc/hx_system_health'): return jr(route, psql_json('select hx_system_health()::text'))
    if path.endswith('/rpc/hx_health_extra'):
        x = psql_json('select hx_health_extra()::text'); x.update({'kiosk_offline_7d': 12, 'kiosk_refused_7d': 0, 'email_last_sent': ago(0, 3), 'email_pending_alerts': 0, 'admins_without_2fa': 0, 'esig_off_licenses': [], 'signatures': 318}); return jr(route, x)
    if path.endswith('/rpc/hx_my_security'): return jr(route, {'approved': True, 'mfa_required': True, 'aal': 'aal1', 'name': 'Sam Salari'})
    if path.endswith('/hx_esignatures'): return jr(route, [body], 201)
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def shot(pg, name): pg.wait_for_timeout(400); pg.screenshot(path=SH + 'sec_' + name + '.png'); print('shot', name)
def eshot(loc, name): loc.page.wait_for_timeout(300); loc.screenshot(path=SH + 'sec_' + name + '.png'); print('eshot', name)
# a real QR code for the set-up screen
import qrcode, io
qi = qrcode.make('otpauth://totp/Hendrix%20QMS:sam@blackfoxmfg.com?secret=JBSWY3DPEHPK3PXP&issuer=Hendrix%20QMS'); bio = io.BytesIO(); qi.save(bio, format='PNG')
QR = 'data:image/png;base64,' + base64.b64encode(bio.getvalue()).decode()
BROWSER = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
def mkctx(b, aal='aal1', url_extra=None, clock=False, vp=(1440, 900)):
    ctx = b.new_context(viewport={'width': vp[0], 'height': vp[1]}, device_scale_factor=1.5); ctx.route('**/*', handle)
    s = {'access_token': jwt(aal), 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN, 'email': 'sam@blackfoxmfg.com'}}
    ctx.add_init_script('if(!sessionStorage.getItem("x")){sessionStorage.setItem("x","1");localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");}' % json.dumps(json.dumps(s)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    if clock: pg.clock.install()
    return ctx, pg
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=BROWSER)
    ctx, pg = mkctx(b); pg.goto(BASE); pg.wait_for_selector('.nav')
    # My Tasks
    pg.locator('.nav button', has_text='My Tasks').click(); pg.wait_for_selector('.tkrow'); shot(pg, 'tasks')
    pg.locator('.nav button', has_text='Dashboard').click(); pg.wait_for_selector('.k >> text=My tasks')
    eshot(pg.locator('.card', has=pg.locator('.k', has_text=re.compile('^My tasks$'))), 'tasks_card')
    # e-signature
    pg.locator('.nav').get_by_role('button', name='SOPs', exact=True).click(); pg.wait_for_selector('.card >> text=Cartridge Filling')
    pg.locator('.card', has_text='Cartridge Filling').first.click(); pg.wait_for_selector('.md')
    pg.get_by_role('button', name='✓ Approve & publish').click(); md = pg.locator('.md', has=pg.locator('text=Electronic signature')); md.wait_for()
    md.locator('input[aria-label="Password"]').fill('wrong'); md.get_by_role('button', name='Sign').click(); md.locator('text=That password is not correct.').wait_for()
    md.locator('input[aria-label="Password"]').fill('xxxxxxxxxxxx'); eshot(md, 'esign')
    md.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(300)
    # Settings > Security and Email
    while pg.locator('.md').count(): pg.mouse.click(5, 5); pg.wait_for_timeout(150)
    pg.locator('.nav').get_by_role('button', name='Settings', exact=True).click(); pg.get_by_role('button', name='Security', exact=True).click(); pg.wait_for_selector('text=Ask for the password when signing')
    shot(pg, 'settings_security')
    pg.get_by_role('button', name='Email', exact=True).click(); pg.wait_for_selector('text=Last email sent'); shot(pg, 'settings_email')
    # METRC Check
    pg.locator('.nav button', has_text='METRC Check').click(); pg.wait_for_selector('.mcrow'); shot(pg, 'metrc')
    # System Health
    pg.locator('.nav').get_by_role('button', name='System Health', exact=True).click(); pg.wait_for_selector('text=Database steps installed')
    pg.screenshot(path=SH + 'sec_health.png', full_page=True); print('shot health')
    # Team and Access: require two-step sign-in
    pg.locator('.nav').get_by_role('button', name='Team and Access').click(); pg.locator('tr', has_text='Maria Lopez').get_by_role('button', name='Manage').click()
    md = pg.locator('.md'); md.locator('label.ck', has_text='Require two-step sign-in').locator('input').check()
    eshot(md.locator('label.ck', has_text='Require two-step sign-in').locator('xpath=..'), 'team_mfa')
    md.get_by_role('button', name='Cancel').click()
    # My account and two-step set-up
    pg.locator('.top').get_by_role('button', name='Sam Salari', exact=True).click(); pg.wait_for_selector('h1 >> text=My account'); shot(pg, 'account')
    pg.get_by_role('button', name='Set up two-step sign-in').click(); pg.wait_for_selector('img[alt="QR code for the authenticator app"]')
    pg.locator('input[aria-label="6-digit code"]').fill('482 913'); shot(pg, 'account_setup')
    ctx.close()
    # two-step sign-in screen
    T['hx_profiles'][0]['mfa_required'] = True; AUTH['factors'] = [{'id': 'f-1', 'factor_type': 'totp', 'status': 'verified'}]
    ctx, pg = mkctx(b); pg.goto(BASE); pg.wait_for_selector('h2 >> text=Two-step sign-in')
    pg.locator('input[aria-label="Code"]').fill('482913'); eshot(pg.locator('.auth .box'), 'gate')
    ctx.close()
    T['hx_profiles'][0]['mfa_required'] = False
    # automatic sign-out warning
    ctx, pg = mkctx(b, clock=True); pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.clock.run_for(29 * 60000 + 15000); pg.wait_for_selector('[role=alert]'); shot(pg, 'idle')
    pg.clock.run_for(60000); pg.wait_for_selector('text=You were signed out after 30 minutes'); eshot(pg.locator('.auth .box'), 'idle_out')
    ctx.close()
    # offline kiosk
    ctx, pg = mkctx(b, vp=(900, 1000)); pg.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); pg.wait_for_selector('text=Scan your badge')
    pg.route('**/rest/v1/rpc/hx_kiosk_clock', lambda r, q: r.abort('internetdisconnected'))
    pg.route('**/rest/v1/rpc/hx_kiosk_sync', lambda r, q: r.abort('internetdisconnected'))
    pg.evaluate("localStorage.setItem('hx_outbox',JSON.stringify([{id:'k1',kind:'clock',state:'st-mo',lic:'lic-mo',at:new Date(Date.now()-3600000).toISOString(),p:{code:'X'},label:'Badge scan'},{id:'k2',kind:'clock',state:'st-mo',lic:'lic-mo',at:new Date(Date.now()-1800000).toISOString(),p:{code:'Y'},label:'Badge scan'}]))")
    pg.keyboard.type('BADGE7731', delay=5); pg.keyboard.press('Enter'); pg.wait_for_selector('text=Scan saved on this tablet'); shot(pg, 'kiosk_offline')
    pg.evaluate("localStorage.setItem('hx_outbox','[]');localStorage.setItem('hx_outbox_done',JSON.stringify([{id:'d1',kind:'clock',lic:'lic-mo',at:new Date(Date.now()-7200000).toISOString(),label:'Badge scan',sent:new Date().toISOString(),error:'Badge not recognized.'}]))")
    pg.reload(); pg.wait_for_selector('text=Not accepted by Hendrix'); eshot(pg.locator('.obar'), 'kiosk_refused')
    ctx.close()
    b.close()
print('\nerrors:', errors if errors else 'none')
