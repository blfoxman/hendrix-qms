import os, re
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 42: admin sets a temporary password; the person chooses a new one at the next sign-in
errors = []
MEM = '22222222-2222-2222-2222-222222222222'
T['hx_profiles'][0].update({'email': 's@x'})
T['hx_profiles'].append({'id': MEM, 'name': 'Maria Lopez', 'email': 'maria@x', 'role': 'member', 'approved': True, 'role_ids': [], 'license_ids': [], 'perms': {'qms': 'read'}, 'must_change_password': False, 'created_at': '2026-02-01'})
ST = {'set': [], 'changed': [], 'put': [], 'missing': False}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    b = json.loads(request.post_data) if request.post_data else {}
    if path.endswith('/rpc/hx_admin_set_password'):
        if ST['missing']: return jr(route, {'code': 'PGRST202', 'message': 'Could not find the function public.hx_admin_set_password(p_password, p_user) in the schema cache'}, 404)
        ST['set'].append(b); p = next(x for x in T['hx_profiles'] if x['id'] == b['p_user']); p['must_change_password'] = b['p_user'] != ADMIN; return jr(route, True)
    if path.endswith('/rpc/hx_password_changed'):
        ST['changed'].append(1); [p.update({'must_change_password': False}) for p in T['hx_profiles']]; return jr(route, True)
    if path.endswith('/auth/v1/user') and request.method == 'PUT':
        ST['put'].append(b.get('password')); return jr(route, {'id': MEM})
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def ctx_for(b, uid):
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    if uid:
        s = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': uid}}
        ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(s)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    return ctx, pg
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    # sign-in page: forgot password
    ctx, pg = ctx_for(b, None); pg.goto(BASE); pg.wait_for_selector('text=Forgot your password?')
    pg.get_by_text('Forgot your password?').click(); pg.wait_for_selector('text=Ask a Hendrix admin to set a temporary password')
    check(True, 'sign-in page: forgot password tells people to ask an admin'); ctx.close()
    # admin sets a temporary password
    ctx, pg = ctx_for(b, ADMIN); pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.locator('.nav').get_by_role('button', name='Team and Access').click(); pg.locator('tr', has_text='Maria Lopez').get_by_role('button', name='Manage').click()
    md = pg.locator('.md'); md.get_by_role('button', name='Set a temporary password').click()
    tmp = md.locator('input[aria-label="Temporary password"]').input_value()
    check(re.match(r'^[A-Za-z2-9]{4}-[A-Za-z2-9]{4}-[A-Za-z2-9]{4}$', tmp) is not None and not re.search(r'[01OlI]', tmp), 'a readable temporary password is generated (%s)' % tmp)
    md.get_by_role('button', name='Generate').click()
    check(md.locator('input[aria-label="Temporary password"]').input_value() != tmp, 'Generate makes a new one')
    md.locator('input[aria-label="Temporary password"]').fill('short'); check(md.get_by_role('button', name='Set password').is_disabled(), 'fewer than 8 characters: cannot set')
    md.locator('input[aria-label="Temporary password"]').fill('Temp-Pass-2026'); md.get_by_role('button', name='Set password').click()
    md.locator('text=Give it to them in person').wait_for(); md.locator('code', has_text='Temp-Pass-2026').wait_for(timeout=5000)
    check(ST['set'] == [{'p_user': MEM, 'p_password': 'Temp-Pass-2026'}] and md.locator('code', has_text='Temp-Pass-2026').count() == 1, 'temporary password set for Maria and shown once to the admin (%s)' % ST['set'])
    pg.screenshot(path=OUT + 'pw_admin.png')
    ST['missing'] = True; md.get_by_role('button', name='Set a temporary password').click(); md.get_by_role('button', name='Set password').click()
    md.locator('text=run hendrix_step42.sql').wait_for(); check(True, 'clear message when step 42 is not installed'); ST['missing'] = False
    ctx.close()
    # Maria signs in with the temporary password: must choose a new one first
    ctx, pg = ctx_for(b, MEM); pg.goto(BASE); pg.wait_for_selector('h2 >> text=Choose a new password')
    check(pg.locator('.nav').count() == 0, 'nothing opens before the new password is chosen')
    pg.locator('input[aria-label="New password"]').fill('abc'); pg.locator('input[aria-label="New password again"]').fill('abc'); pg.get_by_role('button', name='Save my new password').click()
    pg.wait_for_selector('text=Use at least 8 characters.')
    pg.locator('input[aria-label="New password"]').fill('Maria-Own-2026'); pg.locator('input[aria-label="New password again"]').fill('Maria-Own-2027'); pg.get_by_role('button', name='Save my new password').click()
    pg.wait_for_selector('text=The two passwords are not the same.')
    pg.screenshot(path=OUT + 'pw_new.png')
    pg.locator('input[aria-label="New password again"]').fill('Maria-Own-2026'); pg.get_by_role('button', name='Save my new password').click(); pg.wait_for_selector('.nav')
    check(ST['put'] == ['Maria-Own-2026'] and len(ST['changed']) == 1, 'new password saved and the reset flag cleared; Hendrix opens')
    ctx.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
