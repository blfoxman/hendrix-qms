# hendrixqms.com/training: Training Center - company sign-in, videos picked by access and job title (step 68)
import os, subprocess, tempfile, json
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
out = tempfile.mkdtemp(prefix='hxtc_')
r = subprocess.run([os.path.join(ROOT, 'tools', 'build_site.sh'), out], capture_output=True, text=True)
check(r.returncode == 0 and os.path.exists(os.path.join(out, 'training', 'index.html')), 'Training Center is built: ' + (r.stdout + r.stderr).strip())
comp = open(os.path.join(out, 'training', 'companies.js')).read()
check('"summitsolutions"' in comp and '"Summit Solutions"' in comp and 'bqrncllndvzbhmxanitq' in comp, 'companies: code, name and the public sign-in address')
cat = json.loads(open(os.path.join(out, 'training', 'catalog.js')).read().split('window.HX_VIDEOS=', 1)[1].rstrip().rstrip(';'))
ids = [v['id'] for v in cat]
check(len(cat) >= 10 and all(os.path.getsize(os.path.join(out, 'training', v['file'])) > 200000 and os.path.exists(os.path.join(out, 'training', v['poster'])) and v['seconds'] > 20 for v in cat), 'every video and its poster are published (%d videos)' % len(cat))
SBU = 'https://bqrncllndvzbhmxanitq.supabase.co'
ALL = {}
for v in cat:
    for a in v['access']: ALL[a[0]] = 0
USERS = {'tech@x.com': {'pw': 'Tech-Pass-26', 'tok': 'tok-tech', 'p': {'approved': True, 'name': 'Lee Park', 'title': 'Extraction Technician', 'admin': False, 'mfa_needed': False,
                                                                     'access': {**ALL, 'linemap': 1, 'logs': 2, 'logs_sanitation': 2, 'logs_pest': 2}}},
         'qa@x.com': {'pw': 'Qa-Pass-2026', 'tok': 'tok-qa', 'p': {'approved': True, 'name': 'Alex Rivera', 'title': 'QA Manager', 'admin': True, 'mfa_needed': False, 'access': {k: 3 for k in ALL}}},
         'mfa@x.com': {'pw': 'Mfa-Pass-26', 'tok': 'tok-mfa', 'p': {'approved': True, 'name': 'Dana Brooks', 'title': '', 'admin': False, 'mfa_needed': True, 'access': {**ALL}}},
         'wait@x.com': {'pw': 'Wait-Pass-26', 'tok': 'tok-wait', 'p': {'approved': False, 'name': 'New Person'}}}
ST = {'missing': False, 'mods': None, 'verified': False, 'auth': []}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def handle(route, request):
    u = request.url
    if not u.startswith(SBU):
        if u.startswith('file://'): return route.continue_()
        return route.abort()
    path = urllib.parse.urlparse(u).path; b = json.loads(request.post_data) if request.post_data else {}
    tok = (request.headers.get('authorization') or '').replace('Bearer ', '')
    ST['auth'].append(path)
    if path.endswith('/auth/v1/token'):
        us = USERS.get((b.get('email') or '').lower())
        if not us or us['pw'] != b.get('password'): return jr(route, {'error': 'invalid_grant', 'error_description': 'Invalid login credentials'}, 400)
        return jr(route, {'access_token': us['tok'], 'refresh_token': 'r', 'expires_in': 3600, 'user': {'id': 'u-' + us['tok']}})
    if path.endswith('/auth/v1/user'): return jr(route, {'id': 'u-' + tok, 'factors': [{'id': 'f1', 'factor_type': 'totp', 'status': 'verified'}]})
    if path.endswith('/factors/f1/challenge'): return jr(route, {'id': 'c1'})
    if path.endswith('/factors/f1/verify'):
        if b.get('code') != '123456': return jr(route, {'msg': 'Invalid TOTP code entered'}, 422)
        ST['verified'] = True; return jr(route, {'access_token': 'tok-mfa-aal2', 'refresh_token': 'r2', 'expires_in': 3600, 'user': {'id': 'u-tok-mfa'}})
    if path.endswith('/rest/v1/rpc/hx_my_training_profile'):
        if ST['missing']: return jr(route, {'code': 'PGRST202', 'message': 'Could not find the function public.hx_my_training_profile(p_modules) in the schema cache'}, 404)
        ST['mods'] = b.get('p_modules')
        if tok == 'tok-mfa-aal2': return jr(route, {**USERS['mfa@x.com']['p'], 'mfa_needed': False, 'access': {**ALL, 'chemicals': 1}})
        us = next((x for x in USERS.values() if x['tok'] == tok), None)
        return jr(route, us['p']) if us else jr(route, {'message': 'JWT expired'}, 401)
    return route.abort()
def visible_ids(pg, grid): return [x.get_attribute('data-id') for x in pg.locator('#' + grid + ' .vid').all()]
def sign_in(pg, code, email, pw):
    pg.locator('#code').fill(code); pg.locator('#email').fill(email); pg.locator('#pw').fill(pw); pg.locator('#go').click()
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    url = 'file://' + out + '/training/index.html'
    pg.goto(url + '?company=summitsolutions'); pg.wait_for_selector('#signin')
    check(pg.locator('#code').input_value() == 'summitsolutions' and pg.locator('#gate h1').inner_text() == 'Training Center', 'sign-in page; company filled in from the link')
    sign_in(pg, 'acme', 'tech@x.com', 'x'); pg.wait_for_selector('#err:has-text("There is no Hendrix at hendrixqms.com/acme")')
    sign_in(pg, 'hendrixqms.com/SummitSolutions/', 'tech@x.com', 'wrong'); pg.wait_for_selector('#err:has-text("do not match a Hendrix account at summitsolutions")')
    check(True, 'unknown company and wrong password: clear messages (pasted address and capitals are fine)')
    # technician: only the videos for their access, the role picks first
    sign_in(pg, 'summitsolutions', 'tech@x.com', 'Tech-Pass-26'); pg.wait_for_selector('#lib:not([hidden])')
    got = visible_ids(pg, 'grid-all'); picks = visible_ids(pg, 'grid-pick')
    check(set(ST['mods'] or []) == set(ALL), 'Hendrix is asked about every area the videos need (%d)' % len(ST['mods'] or []))
    check(got == [i for i in ids if i in ('getting-started', 'facility-logs', 'line-map', 'taking-training')], 'technician sees getting started, facility logs, line map and training only: %s' % got)
    check(picks == ['facility-logs', 'line-map'] and not pg.locator('#shelf-pick').is_hidden(), 'picked for the role (Extraction Technician): %s' % picks)
    check(pg.locator('#who-name').inner_text() == 'Lee Park' and pg.locator('#who-title').inner_text() == 'Extraction Technician' and 'Lee, here are your videos' in pg.locator('#lib-title').inner_text(), 'name and title shown')
    check(pg.locator('#prog-txt').inner_text() == '0 of 4 watched', 'progress starts at 0 of 4')
    pg.screenshot(path=OUT + 'trc_tech.png', full_page=True)
    # play, next, watched
    pg.locator('#grid-all .vid[data-id="line-map"]').click(); pg.wait_for_selector('#player:not([hidden])')
    check(pg.locator('#p-video').get_attribute('src') == 'media/line-map.mp4' and pg.locator('#p-title').inner_text() == next(v['title'] for v in cat if v['id'] == 'line-map'), 'player opens the video')
    pg.evaluate("document.getElementById('p-video').dispatchEvent(new Event('ended'))")
    pg.locator('#p-close').click(); pg.wait_for_selector('#player[hidden]', state='attached')
    check(pg.locator('#grid-all .vid[data-id="line-map"] .done').count() == 1 and pg.locator('#prog-txt').inner_text() == '1 of 4 watched', 'watched video marked, progress 1 of 4')
    pg.locator('#grid-all .vid[data-id="getting-started"]').click(); pg.wait_for_selector('#player:not([hidden])'); pg.locator('#p-next').click()
    check(pg.locator('#p-video').get_attribute('src') == 'media/' + got[1] + '.mp4', 'Next video plays the next one in the list')
    pg.keyboard.press('Escape'); pg.wait_for_selector('#player[hidden]', state='attached')
    # stays signed in on reload, then sign out
    pg.reload(); pg.wait_for_selector('#lib:not([hidden])'); check(visible_ids(pg, 'grid-all') == got, 'still signed in after a reload')
    pg.locator('#signout').click(); pg.wait_for_selector('#gate:not([hidden])'); check(pg.locator('#lib').is_hidden(), 'Sign out goes back to the sign-in form')
    # admin: everything
    sign_in(pg, 'summitsolutions', 'qa@x.com', 'Qa-Pass-2026'); pg.wait_for_selector('#lib:not([hidden])')
    check(visible_ids(pg, 'grid-all') == ids and 'You are a Hendrix admin' in pg.locator('#lib-sub').inner_text(), 'an admin sees every video (%d)' % len(ids))
    pg.screenshot(path=OUT + 'trc_admin.png', full_page=True)
    pg.locator('#signout').click()
    # two-step sign-in
    sign_in(pg, 'summitsolutions', 'mfa@x.com', 'Mfa-Pass-26'); pg.wait_for_selector('#mfa:not([hidden])')
    pg.locator('#code6').fill('111111'); pg.locator('#go6').click(); pg.wait_for_selector('#err6:has-text("not right")')
    pg.locator('#code6').fill('123456'); pg.locator('#go6').click(); pg.wait_for_selector('#lib:not([hidden])')
    check(ST['verified'] and 'chemicals-sds' in visible_ids(pg, 'grid-all') and pg.locator('#shelf-pick').is_hidden(), 'two-step: the authenticator code, then the videos for that access (no title: no role picks)')
    pg.locator('#signout').click()
    # waiting for approval / step 68 not run
    sign_in(pg, 'summitsolutions', 'wait@x.com', 'Wait-Pass-26'); pg.wait_for_selector('#err:has-text("waiting for an admin")'); check(True, 'not approved yet: told to wait')
    ST['missing'] = True; sign_in(pg, 'summitsolutions', 'tech@x.com', 'Tech-Pass-26'); pg.wait_for_selector('#err:has-text("hendrix_step68.sql")'); check(True, 'step 68 not run: says so')
    ST['missing'] = False
    ctx.close()
    # phone
    ctx = b.new_context(viewport={'width': 390, 'height': 844}); ctx.route('**/*', handle); pg = ctx.new_page()
    pg.goto(url); pg.wait_for_selector('#signin'); check(pg.evaluate('document.documentElement.scrollWidth') <= 390, 'sign-in fits a phone')
    sign_in(pg, 'summitsolutions', 'tech@x.com', 'Tech-Pass-26'); pg.wait_for_selector('#lib:not([hidden])')
    check(pg.evaluate('document.documentElement.scrollWidth') <= 390, 'video list fits a phone'); pg.screenshot(path=OUT + 'trc_phone.png', full_page=True)
    ctx.close()
    # home page tab
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}); ctx.route('**/*', handle); pg = ctx.new_page()
    pg.goto('file://' + out + '/index.html'); pg.wait_for_selector('h1')
    check(pg.locator('header a.tc').get_attribute('href') == 'training/' and 'Training Center' in pg.locator('header a.tc').inner_text(), 'Training Center tab on the home page')
    ctx.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
