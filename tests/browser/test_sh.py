import os, re, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
PGDB = os.environ.get('HX_PGDB', 'hxtest')
AI = {'mode': 'ok', 'calls': []}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def health_from_db(fn='hx_system_health'):
    # the real step-37/38 functions on PostgreSQL (the check under test), run as the admin
    out = subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB, '-c', "set test.uid='11111111-1111-1111-1111-111111111111'; select " + fn + "()::text"], capture_output=True, text=True)
    return json.loads(out.stdout.strip().split('\n')[-1])
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    if path.endswith('/rpc/hx_health_extra'): return jr(route, health_from_db('hx_health_extra'))
    if path.endswith('/rpc/hx_system_health'):
        if AI.get('missing'): return jr(route, {'code': 'PGRST202', 'message': 'Could not find the function public.hx_system_health without parameters in the schema cache'}, 404)
        return jr(route, health_from_db())
    if '/functions/v1/hendrix-ai' in u:
        AI['calls'].append(json.loads(request.post_data))
        m = AI['mode']
        if m == 'ok': return jr(route, {'ok': True, 'model': 'claude-sonnet-5-5', 'version': 'hendrix-ai 37'})
        if m == 'badkey': return jr(route, {'error': {'message': 'Anthropic refused the ANTHROPIC_API_KEY saved in Supabase (Edge Functions > Secrets). Create a new key at console.anthropic.com > API Keys, paste it there (whole key, no spaces or quotes) and retry.'}}, 502)
        if m == 'old': return jr(route, {'error': {'message': 'messages missing'}}, 400)
        if m == 'none': return route.fulfill(status=404, body='not found')
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def row(pg, label): return pg.locator('.card .row', has=pg.locator('div', has_text=re.compile('^' + re.escape(label) + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.get_by_role('button', name='System Health', exact=True).click(); pg.wait_for_selector('text=Database steps installed')
    check(pg.locator('text=All 39 steps (4 to 43) are installed.').count() == 1, 'all database steps detected from the real database')
    check(row(pg, 'Audit trail locked').locator('text=✓').count() == 1 and row(pg, 'Every change goes to the audit trail').locator('text=✓').count() == 1, 'audit trail: covered and locked')
    check(row(pg, 'Password at every signature').locator('text=✓').count() == 1 and row(pg, 'Two-step sign-in for admins').locator('text=!').count() == 1, 'step 38: signatures on everywhere; admin without two-step sign-in flagged')
    check(row(pg, 'Kiosk entries saved without internet (7 days)').count() == 1, 'step 40: offline kiosk check shown')
    check(row(pg, 'Urgent alerts going out').count() == 1 and row(pg, 'Email sent by Hendrix').count() == 1, 'step 39: email checks shown')
    check(row(pg, 'Private file storage').locator('text=✓').count() == 1, 'private file bucket')
    check(pg.locator('text=Off on: hx_licenses, hx_profiles, hx_states').count() == 1, 'row level security gaps are named (test database stubs for steps 1-3)')
    check(row(pg, 'Accounts waiting for approval').locator('text=!').count() == 1, 'waiting approvals flagged')
    check(pg.locator('text=Not done yet: CSQ standard adopted.').count() >= 1, 'per-license setup gaps listed')
    check(pg.get_by_text('Not tested', exact=True).count() == 1 and len(AI['calls']) == 0, 'AI is not called until asked (each test is a paid request)')
    pg.get_by_role('button', name='Test the AI connection').click(); pg.wait_for_selector('text=The AI works')
    check(AI['calls'][-1] == {'module': 'health'} and pg.locator('text=Working').count() == 1, 'AI test: working (key, credit, model)')
    AI['mode'] = 'badkey'; pg.get_by_role('button', name='Test the AI connection').click(); pg.wait_for_selector('text=Anthropic refused the ANTHROPIC_API_KEY')
    check(pg.locator('text=took too long').count() == 0, 'AI key refused: the real reason is shown (not "took too long")')
    AI['mode'] = 'old'; pg.get_by_role('button', name='Test the AI connection').click(); pg.wait_for_selector('text=older version')
    check(True, 'old AI function version detected')
    AI['mode'] = 'none'; pg.get_by_role('button', name='Test the AI connection').click(); pg.wait_for_selector('text=is not deployed in Supabase')
    check(True, 'AI function not deployed detected')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print IQ evidence').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Installation Qualification evidence' in html and 'Row level security' in html and 'FAIL' in html and 'Reviewed by (QA)' in html, 'IQ evidence printout with results and sign-off lines'); w.close()
    pg.screenshot(path=OUT + 'health.png', full_page=True)
    # Settings > Everything else links to it
    pg.get_by_role('button', name='Settings', exact=True).click(); pg.get_by_role('button', name='Everything else').click()
    check(pg.locator('.card b', has_text='System Health').count() == 1, 'Settings links to System Health')
    # not installed
    AI['missing'] = True; pg.get_by_role('button', name='System Health', exact=True).click(); pg.wait_for_selector('text=run hendrix_step37.sql')
    check(True, 'clear message when step 37 is not installed'); AI['missing'] = False
    # members never see it
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'settings': 'admin', 'qms': 'admin'}
    pg.reload(); pg.wait_for_selector('.nav')
    check(pg.get_by_role('button', name='System Health', exact=True).count() == 0, 'only admins see System Health')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
