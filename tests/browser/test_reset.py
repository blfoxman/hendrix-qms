import os, re
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 66: forgot password by email, the reset link, and changing your own email
errors = []
MEM = '22222222-2222-2222-2222-222222222222'
T['hx_profiles'][0].update({'email': 's@x'})
T['hx_profiles'].append({'id': MEM, 'name': 'Maria Lopez', 'email': 'maria@x.com', 'role': 'member', 'approved': True, 'role_ids': [], 'license_ids': ['lic-mo'], 'perms': {'qms': 'read'}, 'must_change_password': False, 'created_at': '2026-02-01T00:00:00Z'})
ST = {'recover': [], 'put': [], 'changed': 0, 'sync': 0, 'user_email': 'maria@x.com', 'aal2_needed': False, 'verified': [], 'recover_err': None, 'email_err': None, 'bad_token': False}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; pr = urllib.parse.urlparse(u); path = pr.path; qs = urllib.parse.parse_qs(pr.query)
    b = json.loads(request.post_data) if request.post_data else {}
    auth = request.headers.get('authorization', '')
    if path.endswith('/auth/v1/recover'):
        if ST['recover_err']: return jr(route, {'code': 500, 'msg': ST['recover_err']}, 500)
        ST['recover'].append({'email': b.get('email'), 'redirect_to': (qs.get('redirect_to') or [''])[0]}); return jr(route, {})
    if path.endswith('/auth/v1/user') and request.method == 'GET':
        if ST['bad_token']: return jr(route, {'code': 401, 'msg': 'invalid JWT'}, 401)
        f = [{'id': 'f1', 'factor_type': 'totp', 'status': 'verified'}] if ST['aal2_needed'] else []
        return jr(route, {'id': MEM, 'email': ST['user_email'], 'factors': f})
    if path.endswith('/auth/v1/user') and request.method == 'PUT':
        if 'password' in b and ST['aal2_needed'] and not ST['verified']: return jr(route, {'code': 401, 'error_code': 'insufficient_aal', 'msg': 'AAL2 session is required to update email or password when MFA is enabled.'}, 401)
        if 'email' in b and ST['email_err']: return jr(route, {'code': 422, 'error_code': 'email_exists', 'msg': ST['email_err']}, 422)
        ST['put'].append({'body': b, 'redirect_to': (qs.get('redirect_to') or [''])[0], 'auth': auth}); return jr(route, {'id': MEM, 'email': ST['user_email']})
    if path.endswith('/auth/v1/factors/f1/challenge'): return jr(route, {'id': 'c1'})
    if path.endswith('/auth/v1/factors/f1/verify'):
        if b.get('code') != '123456': return jr(route, {'code': 422, 'msg': 'Invalid TOTP code entered'}, 422)
        ST['verified'].append(1); return jr(route, {'access_token': 'aal2tok', 'refresh_token': 'r2', 'expires_in': 3600, 'user': {'id': MEM, 'email': ST['user_email']}})
    if path.endswith('/rpc/hx_password_changed'): ST['changed'] += 1; return jr(route, True)
    if path.endswith('/rpc/hx_sync_my_email'):
        ST['sync'] += 1; next(x for x in T['hx_profiles'] if x['id'] == MEM)['email'] = ST['user_email']; return jr(route, ST['user_email'])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def ctx_for(b, uid, email=None):
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    init = 'localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");'
    if uid:
        s = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': uid, 'email': email or ''}}
        init += 'localStorage.setItem("hx_session",%s);' % json.dumps(json.dumps(s))
    ctx.add_init_script('if(!sessionStorage.getItem("hx_t_once")){sessionStorage.setItem("hx_t_once","1");' + init + '}')
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    return ctx, pg
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    # 1. forgot password: email a reset link
    ctx, pg = ctx_for(b, None); pg.goto(BASE); pg.wait_for_selector('text=Forgot your password?')
    pg.get_by_text('Forgot your password?').click(); pg.wait_for_selector('text=Email me a reset link')
    check(pg.locator('input[type=password]').count() == 0, 'forgot password: only the email is asked')
    pg.locator('input[type=email]').fill('maria'); pg.get_by_role('button', name='Email me a reset link').click()
    pg.wait_for_selector('text=Enter the email you sign in with.'); check(ST['recover'] == [], 'a half-typed email is not sent')
    pg.locator('input[type=email]').fill(' maria@x.com '); pg.get_by_role('button', name='Email me a reset link').click()
    pg.wait_for_selector('text=a reset link is on its way')
    check(ST['recover'] == [{'email': 'maria@x.com', 'redirect_to': BASE}], 'reset email asked for, with the link coming back to this Hendrix (%s)' % ST['recover'])
    check(pg.get_by_role('button', name='Sign in').count() == 1, 'back on the sign-in form after sending')
    pg.screenshot(path=OUT + 'reset_sent.png')
    ST['recover_err'] = 'Error sending recovery email'; pg.get_by_text('Forgot your password?').click()
    pg.locator('input[type=email]').fill('maria@x.com'); pg.get_by_role('button', name='Email me a reset link').click()
    pg.wait_for_selector('text=Hendrix could not send the email right now'); check(True, 'email not set up: clear message pointing to an admin'); ST['recover_err'] = None
    ctx.close()
    # 2. expired or used link
    ctx, pg = ctx_for(b, None); pg.goto(BASE + '#error=access_denied&error_code=otp_expired&error_description=Email+link+is+invalid+or+has+expired')
    pg.wait_for_selector('text=That link has expired or was already used. Ask for a new one.')
    check('#' not in pg.url, 'expired link: message shown and the address cleaned up')
    ctx.close()
    # 3. the reset link: choose a new password, then Hendrix opens
    ctx, pg = ctx_for(b, None); pg.goto(BASE + '#access_token=rectok&expires_in=3600&refresh_token=recref&token_type=bearer&type=recovery')
    pg.wait_for_selector('h2 >> text=Choose a new password')
    check('access_token' not in pg.url, 'reset link: the sign-in code is removed from the address bar')
    check(pg.locator('.nav').count() == 0 and pg.locator('text=For maria@x.com').count() == 1, 'reset link: nothing opens before the new password, and it says whose account')
    pg.locator('input[aria-label="New password"]').fill('New-Pass-2026'); pg.locator('input[aria-label="New password again"]').fill('New-Pass-2027')
    pg.get_by_role('button', name='Save my new password').click(); pg.wait_for_selector('text=The two passwords are not the same.')
    pg.screenshot(path=OUT + 'reset_choose.png')
    pg.locator('input[aria-label="New password again"]').fill('New-Pass-2026'); pg.get_by_role('button', name='Save my new password').click(); pg.wait_for_selector('.nav')
    check(len(ST['put']) == 1 and ST['put'][0]['body'] == {'password': 'New-Pass-2026'} and ST['put'][0]['auth'] == 'Bearer rectok' and ST['changed'] == 1,
          'new password saved with the link sign-in, reset flag cleared, Hendrix opens (%s)' % ST['put'])
    pg.reload(); pg.wait_for_selector('.nav'); check(pg.locator('h2 >> text=Choose a new password').count() == 0, 'after a reload: normal Hendrix (the link is used once)')
    ctx.close()
    # 4. reset link for someone with an authenticator app: asks for the code
    ST['put'] = []; ST['aal2_needed'] = True
    ctx, pg = ctx_for(b, None); pg.goto(BASE + '#access_token=rectok2&expires_in=3600&refresh_token=recref2&token_type=bearer&type=recovery')
    pg.wait_for_selector('h2 >> text=Choose a new password')
    pg.locator('input[aria-label="New password"]').fill('New-Pass-2026'); pg.locator('input[aria-label="New password again"]').fill('New-Pass-2026'); pg.get_by_role('button', name='Save my new password').click()
    pg.wait_for_selector('input[aria-label="Authenticator code"]'); check(pg.locator('text=Your account uses two-step sign-in').count() == 1, 'two-step sign-in: asks for the authenticator code')
    pg.locator('input[aria-label="Authenticator code"]').fill('111111'); pg.get_by_role('button', name='Save my new password').click()
    pg.wait_for_selector('text=That code is not correct or has expired'); check(ST['put'] == [], 'wrong code: password not changed')
    pg.locator('input[aria-label="Authenticator code"]').fill('123456'); pg.get_by_role('button', name='Save my new password').click(); pg.wait_for_selector('.nav')
    check(len(ST['put']) == 1 and ST['put'][0]['auth'] == 'Bearer aal2tok', 'right code: password saved after the second step')
    ctx.close(); ST['aal2_needed'] = False; ST['verified'] = []
    # 5. bad or old sign-in code in the link
    ST['bad_token'] = True
    ctx, pg = ctx_for(b, None); pg.goto(BASE + '#access_token=junk&expires_in=3600&type=recovery')
    pg.wait_for_selector('text=That link has expired or was already used'); check(pg.locator('h2 >> text=Choose a new password').count() == 0, 'a bad link goes back to sign-in with a message')
    ctx.close(); ST['bad_token'] = False
    # 6. My account: change my email
    ST['put'] = []
    ctx, pg = ctx_for(b, MEM, 'maria@x.com'); pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.locator('button[title^="My account"]').click(); pg.wait_for_selector('h3 >> text=Email address')
    card = pg.locator('.card', has=pg.locator('h3', has_text='Email address'))
    check(card.locator('b', has_text='maria@x.com').count() == 1, 'My account shows the current email')
    card.locator('input[aria-label="New email"]').fill('maria@'); card.get_by_role('button', name='Change my email').click(); card.locator('text=Enter a full email address').wait_for()
    card.locator('input[aria-label="New email"]').fill('MARIA@x.com'); card.get_by_role('button', name='Change my email').click(); card.locator('text=That is already your email.').wait_for()
    ST['email_err'] = 'A user with this email address has already been registered'
    card.locator('input[aria-label="New email"]').fill('sam@x.com'); card.get_by_role('button', name='Change my email').click(); card.locator('text=Another Hendrix account already uses that email.').wait_for()
    ST['email_err'] = None; check(ST['put'] == [], 'bad, same or taken emails are not changed')
    card.locator('input[aria-label="New email"]').fill('maria.lopez@blackfox.com'); card.get_by_role('button', name='Change my email').click()
    card.locator('text=Check maria.lopez@blackfox.com for a confirmation link').wait_for()
    check(len(ST['put']) == 1 and ST['put'][0]['body'] == {'email': 'maria.lopez@blackfox.com'} and ST['put'][0]['redirect_to'] == BASE, 'email change asked for; the confirmation link comes back to this Hendrix (%s)' % ST['put'])
    check(card.locator('text=keep signing in with maria@x.com').count() == 1, 'it says to keep using the old email until confirmed')
    pg.screenshot(path=OUT + 'email_change.png')
    ctx.close()
    # 7. half-confirmed (secure email change sends two links)
    ctx, pg = ctx_for(b, MEM, 'maria@x.com'); pg.goto(BASE + '#message=Confirmation+link+accepted.+Please+proceed+to+confirm+link+sent+to+the+other+email')
    pg.wait_for_selector('text=One of two confirmations done'); check(pg.locator('h3 >> text=Email address').count() == 1, 'first of two links: My account opens and says to open the other link')
    ctx.close()
    # 8. confirmation link opened: email changed, profile follows
    ST['user_email'] = 'maria.lopez@blackfox.com'; ST['sync'] = 0
    ctx, pg = ctx_for(b, None); pg.goto(BASE + '#access_token=ectok&expires_in=3600&refresh_token=ecref&token_type=bearer&type=email_change')
    pg.wait_for_selector('text=Your email address is now maria.lopez@blackfox.com.')
    card = pg.locator('.card', has=pg.locator('h3', has_text='Email address'))
    check(card.locator('b', has_text='maria.lopez@blackfox.com').count() == 1 and ST['sync'] == 1, 'confirmed: My account shows the new email and the Hendrix profile is updated (sync %d)' % ST['sync'])
    check(next(x for x in T['hx_profiles'] if x['id'] == MEM)['email'] == 'maria.lopez@blackfox.com', 'profile email is the new one (task lists and alerts go there)')
    pg.screenshot(path=OUT + 'email_changed.png')
    ctx.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
