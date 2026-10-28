import os, re, base64, copy
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 38: electronic signatures (password re-entry), two-step sign-in (TOTP), automatic sign-out
errors = []
PW = 'Correct-Horse-9'
T['hx_profiles'][0].update({'email': 's@x', 'mfa_required': False})
T['hx_profiles'].append({'id': 'u-lee', 'name': 'Lee Worker', 'email': 'lee@x', 'role': 'member', 'approved': True, 'role_ids': [], 'license_ids': ['lic-mo'], 'perms': {'sops': 'read'}, 'mfa_required': False, 'created_at': '2026-02-01'})
SET0 = {'license_id': 'lic-mo', 'state_id': 'st-mo', 'legal_name': '', 'dba': '', 'address': '', 'phone': '', 'email': '', 'print_footer': '', 'logo': None,
        'break1_min': 15, 'break2_min': 30, 'break3_min': 15, 'log_due': {}, 'review_days': {}, 'linemap_idle_hours': 4, 'esig_password': True, 'idle_signout_min': 30}
T['hx_license_settings'] = [copy.deepcopy(SET0)]
T['hx_esignatures'] = []
SOP = {'id': 'sop-1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Cart Filling', 'sop_number': 'SOP-PRD-001', 'version': '1.0', 'status': 'draft',
       'folder': 'Production', 'department': 'Production', 'description': 'Fill carts.', 'steps': [{'n': 1, 'text': 'Inspect carts.'}], 'attachments': [], 'created_by': 'Sam', 'created_by_id': ADMIN,
       'created_at': '2026-10-20T10:00:00Z', 'updated_at': '2026-10-20T10:00:00Z', 'approved_by': '', 'approved_at': None, 'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [],
       'previous_folder': '', 'revision_note': '', 'effective_date': None, 'next_review': None, 'generated_content': None}
T['hx_sops'] = [dict(SOP), dict(SOP, id='sop-2', title='Line Cleaning', sop_number='SOP-PRD-002')]
AUTH = {'logins': [], 'factors': [], 'verify': [], 'pw_changed': None}
def jwt(aal):
    p = base64.urlsafe_b64encode(json.dumps({'sub': ADMIN, 'aal': aal}).encode()).decode().rstrip('=')
    return 'h.' + p + '.s'
def sess_json(aal, uid=ADMIN, email='s@x'):
    return {'access_token': jwt(aal), 'refresh_token': 'r', 'expires_in': 3600, 'user': {'id': uid, 'email': email}}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    if '/auth/v1/' in u:
        body = json.loads(request.post_data) if request.post_data else {}
        if path.endswith('/token'):
            AUTH['logins'].append(body.get('email'))
            if body.get('password') == PW: return jr(route, sess_json('aal1'))
            return jr(route, {'error': 'invalid_grant', 'error_description': 'Invalid login credentials'}, 400)
        if path.endswith('/user') and request.method == 'GET':
            return jr(route, {'id': ADMIN, 'email': 's@x', 'factors': AUTH['factors']})
        if path.endswith('/user') and request.method == 'PUT':
            AUTH['pw_changed'] = body.get('password'); AUTH['pw_current'] = body.get('current_password'); return jr(route, {'id': ADMIN})
        if path.endswith('/factors') and request.method == 'POST':
            f = {'id': 'f-%d' % (len(AUTH['factors']) + 1), 'factor_type': 'totp', 'status': 'unverified', 'friendly_name': body.get('friendly_name'),
                 'totp': {'qr_code': '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>', 'secret': 'JBSWY3DPEHPK3PXP', 'uri': 'otpauth://totp/x'}}
            AUTH['factors'].append({k: f[k] for k in ('id', 'factor_type', 'status', 'friendly_name')}); return jr(route, f)
        m = re.search(r'/factors/([^/]+)(/challenge|/verify)?$', path)
        if m and request.method == 'DELETE':
            AUTH['factors'] = [x for x in AUTH['factors'] if x['id'] != m.group(1)]; return jr(route, {})
        if m and m.group(2) == '/challenge': return jr(route, {'id': 'ch-1', 'expires_at': 9999999999})
        if m and m.group(2) == '/verify':
            AUTH['verify'].append(body)
            if body.get('code') != '123456': return jr(route, {'code': 'mfa_verification_failed', 'msg': 'Invalid TOTP code entered'}, 422)
            for x in AUTH['factors']:
                if x['id'] == m.group(1): x['status'] = 'verified'
            return jr(route, sess_json('aal2'))
        return jr(route, {})
    if path.endswith('/rpc/hx_my_security'):
        p = T['hx_profiles'][0]; return jr(route, {'approved': True, 'mfa_required': p.get('mfa_required'), 'aal': 'aal1', 'name': p['name']})
    if path.endswith('/hx_esignatures') and request.method == 'POST':
        b = json.loads(request.post_data); b.update({'user_id': ADMIN, 'signer_name': 'Sam', 'signer_email': 's@x', 'signed_at': now()}); T['hx_esignatures'].append(b)
        return jr(route, [b], 201)
    if path.endswith('/hx_license_settings') and request.method == 'PATCH':
        b = json.loads(request.post_data); T['hx_license_settings'][0].update(b); return jr(route, [T['hx_license_settings'][0]])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def new_ctx(b, aal='aal1', clock=False):
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    s = {'access_token': jwt(aal), 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN, 'email': 's@x'}}
    ctx.add_init_script('if(!sessionStorage.getItem("hx_t")){sessionStorage.setItem("hx_t","1");localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");}' % json.dumps(json.dumps(s)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    if clock: pg.clock.install()
    return ctx, pg
def aal_of(pg):
    t = json.loads(pg.evaluate('localStorage.getItem("hx_session")') or '{}').get('access_token', '..').split('.')[1]
    return json.loads(base64.urlsafe_b64decode(t + '=' * (-len(t) % 4)) or b'{}').get('aal')
def close_md(pg):
    while pg.locator('.md').count():
        c = pg.locator('.md').last.get_by_role('button', name='Close')
        c.click() if c.count() else pg.mouse.click(5, 5)
        pg.wait_for_timeout(150)
def esig_modal(pg): return pg.locator('.md', has=pg.locator('text=Electronic signature'))
def open_sop(pg, title):
    pg.locator('.nav').get_by_role('button', name='SOPs', exact=True).click(); pg.wait_for_selector('.card >> text=' + title)
    pg.locator('.card', has_text=title).first.click(); pg.wait_for_selector('.md')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx, pg = new_ctx(b); pg.goto(BASE); pg.wait_for_selector('.nav')
    # ---- electronic signature on SOP approval ----
    open_sop(pg, 'Cart Filling'); pg.get_by_role('button', name='✓ Approve & publish').click()
    md = esig_modal(pg); md.wait_for()
    txt = md.inner_text()
    check('Approved and published this SOP' in txt and 'Cart Filling' in txt and 's@x' in txt and 'Sam' in txt, 'signature box shows the signer, the meaning and the record')
    check(md.locator('input[aria-label="Authenticator code"]').count() == 0, 'no authenticator code asked when two-step sign-in is off')
    check(md.get_by_role('button', name='Sign').is_disabled(), 'Sign is disabled until the password is typed')
    md.get_by_role('button', name='Cancel').click(); pg.wait_for_selector('text=Signature cancelled - nothing was saved.')
    check(T['hx_sops'][0]['status'] == 'draft' and not T['hx_esignatures'], 'cancel: nothing is saved')
    pg.get_by_role('button', name='✓ Approve & publish').click(); md = esig_modal(pg); md.wait_for()
    md.locator('input[aria-label="Password"]').fill('wrong-one'); md.get_by_role('button', name='Sign').click(); md.locator('text=That password is not correct.').wait_for()
    check(T['hx_sops'][0]['status'] == 'draft' and AUTH['logins'][-1] == 's@x', 'wrong password: refused, the record is not saved (re-checked with the signed-in email)')
    md.locator('input[aria-label="Password"]').fill(PW); md.get_by_role('button', name='Sign').click(); pg.wait_for_selector('text=Published: Cart Filling')
    pg.wait_for_timeout(300)
    es = T['hx_esignatures']
    check(T['hx_sops'][0]['status'] == 'published', 'right password: the SOP is published')
    check(len(es) == 1 and es[0]['meaning'] == 'Approved and published this SOP' and es[0]['record_table'] == 'hx_sops' and es[0]['record_id'] == 'sop-1' and es[0]['record_label'] == 'Cart Filling' and es[0]['license_id'] == 'lic-mo' and es[0]['state_id'] == 'st-mo',
          'signature kept: meaning, record, license')
    check(esig_modal(pg).count() == 0, 'signature box closes')
    pg.screenshot(path=OUT + 'sec_signed.png', full_page=True); close_md(pg)
    # ---- Settings > Security ----
    pg.locator('.nav').get_by_role('button', name='Settings', exact=True).click(); pg.get_by_role('button', name='Security', exact=True).click()
    box = pg.locator('label.ck', has_text='Ask for the password when signing').locator('input')
    check(box.is_checked() and pg.locator('input[aria-label="Minutes without activity"]').input_value() == '30', 'Security tab shows the secure defaults (password on, 30 minutes)')
    pg.locator('input[aria-label="Minutes without activity"]').fill('600'); pg.get_by_role('button', name='Save settings').click()
    pg.wait_for_selector('text=Automatic sign-out must be between 0 and 480 minutes')
    pg.locator('input[aria-label="Minutes without activity"]').fill('15'); box.uncheck(); pg.wait_for_selector('text=Auditors expect them to be')
    pg.get_by_role('button', name='Save settings').click(); pg.wait_for_selector('.msg >> text=Settings saved')
    s0 = T['hx_license_settings'][0]
    check(s0['esig_password'] is False and s0['idle_signout_min'] == 15, 'Security settings saved (password off, 15 minutes)')
    open_sop(pg, 'Line Cleaning'); pg.get_by_role('button', name='✓ Approve & publish').click(); pg.wait_for_selector('text=Published: Line Cleaning')
    check(esig_modal(pg).count() == 0 and len(T['hx_esignatures']) == 1, 'with the password switched off, no signature box')
    T['hx_license_settings'][0].update({'esig_password': True, 'idle_signout_min': 30}); close_md(pg)
    # ---- My account: set up two-step sign-in ----
    pg.reload(); pg.wait_for_selector('.nav')
    pg.locator('.top').get_by_role('button', name='Sam', exact=True).click(); pg.wait_for_selector('h1 >> text=My account')
    check(pg.locator('.badge', has_text='Off').count() == 1, 'My account: two-step sign-in is Off')
    pg.get_by_role('button', name='Set up two-step sign-in').click(); pg.wait_for_selector('img[alt="QR code for the authenticator app"]')
    check(pg.locator('code', has_text='JBSWY3DPEHPK3PXP').count() == 1, 'QR code and typed key shown')
    pg.locator('input[aria-label="6-digit code"]').fill('000000'); pg.get_by_role('button', name='Turn on two-step sign-in').click()
    pg.wait_for_selector('text=That code is not correct or has expired')
    check(T['hx_profiles'][0]['mfa_required'] is False, 'wrong code: not turned on')
    pg.locator('input[aria-label="6-digit code"]').fill('123 456'); pg.get_by_role('button', name='Turn on two-step sign-in').click()
    pg.wait_for_selector('text=Two-step sign-in is on.')
    check(AUTH['verify'][-1] == {'challenge_id': 'ch-1', 'code': '123456'} and T['hx_profiles'][0]['mfa_required'] is True, 'right code: factor verified, the account now requires two-step sign-in')
    check(aal_of(pg) == 'aal2', 'session upgraded to the second step (aal2)')
    pg.wait_for_selector('.badge >> text=Required for your account')
    pg.screenshot(path=OUT + 'sec_account.png', full_page=True)
    # password change (asks for the current password: Supabase may require it)
    check(pg.get_by_role('button', name='Change password').is_disabled(), 'password change needs the current password')
    pg.locator('input[aria-label="Current password"]').fill('Old-Pass-123')
    pg.locator('input[aria-label="New password"]').fill('short'); pg.locator('input[aria-label="New password again"]').fill('short'); pg.get_by_role('button', name='Change password').click()
    pg.wait_for_selector('text=Use at least 8 characters.')
    pg.locator('input[aria-label="New password"]').fill('New-Pass-123'); pg.locator('input[aria-label="New password again"]').fill('New-Pass-124'); pg.get_by_role('button', name='Change password').click()
    pg.wait_for_selector('text=The two passwords are not the same.')
    pg.locator('input[aria-label="New password again"]').fill('New-Pass-123'); pg.get_by_role('button', name='Change password').click(); pg.wait_for_selector('text=Password changed.')
    check(AUTH['pw_changed'] == 'New-Pass-123' and AUTH.get('pw_current') == 'Old-Pass-123', 'password changed, current password sent to Supabase')
    # ---- signature with two-step on: password + code ----
    T['hx_sops'][1]['status'] = 'draft'
    open_sop(pg, 'Line Cleaning'); pg.get_by_role('button', name='✓ Approve & publish').click(); md = esig_modal(pg); md.wait_for()
    check(md.locator('input[aria-label="Authenticator code"]').count() == 1, 'two-step on: the signature also asks for the authenticator code')
    md.locator('input[aria-label="Password"]').fill(PW); md.locator('input[aria-label="Authenticator code"]').fill('999999'); md.get_by_role('button', name='Sign').click()
    md.locator('text=That code is not correct').wait_for()
    check(T['hx_sops'][1]['status'] == 'draft', 'wrong code: not signed')
    md.locator('input[aria-label="Authenticator code"]').fill('123456'); md.get_by_role('button', name='Sign').click(); pg.wait_for_selector('text=Published: Line Cleaning')
    pg.wait_for_timeout(300)
    check(T['hx_sops'][1]['status'] == 'published' and len(T['hx_esignatures']) == 2, 'password + code: signed and kept'); close_md(pg)
    # ---- Team and Access: require two-step sign-in for a person ----
    pg.locator('.nav').get_by_role('button', name='Team and Access').click(); pg.locator('tr', has_text='Lee Worker').get_by_role('button', name='Manage').click()
    md = pg.locator('.md'); md.locator('label.ck', has_text='Require two-step sign-in').locator('input').check()
    md.get_by_role('button', name=re.compile('^Save')).click(); pg.wait_for_selector('.md', state='detached')
    check(T['hx_profiles'][1]['mfa_required'] is True, 'Team and Access: an admin requires two-step sign-in for Lee')
    ctx.close()
    # ---- sign-in gate: two-step required, session only aal1 ----
    ctx, pg = new_ctx(b, 'aal1'); pg.goto(BASE); pg.wait_for_selector('h2 >> text=Two-step sign-in')
    check(pg.locator('.nav').count() == 0, 'two-step required: nothing opens before the code')
    pg.locator('input[aria-label="Code"]').fill('111111'); pg.get_by_role('button', name='Continue').click(); pg.wait_for_selector('text=That code is not correct')
    pg.locator('input[aria-label="Code"]').fill('123456'); pg.get_by_role('button', name='Continue').click(); pg.wait_for_selector('.nav')
    check(aal_of(pg) == 'aal2', 'code accepted: signed in at the second step')
    ctx.close()
    # gate when no authenticator is set up yet: enrolment
    AUTH['factors'] = []
    ctx, pg = new_ctx(b, 'aal1'); pg.goto(BASE); pg.wait_for_selector('text=Your account needs two-step sign-in')
    pg.wait_for_selector('img[alt="QR code for the authenticator app"]')
    pg.locator('input[aria-label="6-digit code"]').fill('123456'); pg.get_by_role('button', name='Turn on two-step sign-in').click(); pg.wait_for_selector('.nav')
    check(AUTH['factors'][-1]['status'] == 'verified', 'required but not set up: set up at sign-in, then in')
    pg.screenshot(path=OUT + 'sec_gate.png')
    ctx.close()
    # gate: sign out link
    ctx, pg = new_ctx(b, 'aal1'); pg.goto(BASE); pg.wait_for_selector('h2 >> text=Two-step sign-in')
    pg.get_by_text('Sign out', exact=True).click(); pg.wait_for_selector('input[type=password]')
    check(True, 'sign out from the two-step screen'); ctx.close()
    T['hx_profiles'][0]['mfa_required'] = False
    # ---- automatic sign-out ----
    T['hx_license_settings'][0]['idle_signout_min'] = 2
    ctx, pg = new_ctx(b, 'aal1', clock=True); pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.clock.run_for(45000)
    check(pg.locator('[role=alert]', has_text='you will be signed out').count() == 0, 'no warning after 45 s (limit 2 minutes)')
    pg.clock.run_for(30000); pg.wait_for_selector('[role=alert] >> text=you will be signed out')
    check(True, 'warning in the last minute')
    pg.mouse.move(200, 200); pg.mouse.move(260, 240); pg.clock.run_for(2000)
    check(pg.locator('[role=alert]', has_text='you will be signed out').count() == 0, 'activity keeps the person signed in')
    pg.clock.run_for(125000); pg.wait_for_selector('text=You were signed out after 2 minutes without activity.')
    check(pg.evaluate('localStorage.getItem("hx_session")') is None and pg.locator('.nav').count() == 0, 'signed out after 2 minutes idle; the session is removed')
    ctx.close()
    T['hx_license_settings'][0]['idle_signout_min'] = 0
    ctx, pg = new_ctx(b, 'aal1', clock=True); pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.clock.run_for(3 * 3600 * 1000)
    check(pg.locator('.nav').count() == 1, '0 minutes = never signed out')
    ctx.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
