import os, re, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 39: My Tasks inbox (real database function) + email
errors = []
PGDB = os.environ.get('HX_PGDB', 'hxtest')
HERE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db')
# the step-39 test records (CAPA, hold, SOPs, training, change actions, calibration) in the real database
subprocess.run(['psql', '-X', '-q', '-d', PGDB, '-f', os.path.join(HERE_DB, 't39.sql')], capture_output=True, text=True)
ST = {'missing': False, 'email': 'ok', 'emails': [], 'flags': []}
def psql_json(sql):
    out = subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB, '-c', "set test.uid='" + ADMIN + "'; " + sql], capture_output=True, text=True)
    return json.loads(out.stdout.strip().split('\n')[-1])
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    if path.endswith('/rpc/hx_my_tasks'):
        if ST['missing']: return jr(route, {'code': 'PGRST202', 'message': 'Could not find the function public.hx_my_tasks(p_lic) in the schema cache'}, 404)
        lic = json.loads(request.post_data)['p_lic']
        return jr(route, psql_json("select hx_my_tasks('" + lic.replace("'", '') + "')::text"))
    if path.endswith('/rpc/hx_set_task_email'):
        ST['flags'].append(json.loads(request.post_data)['p_on']); return jr(route, ST['flags'][-1])
    if path.endswith('/rpc/hx_notify_status'): return jr(route, psql_json('select hx_notify_status()::text'))
    if '/functions/v1/hendrix-notify' in u:
        b = json.loads(request.post_data); ST['emails'].append(b)
        if ST['email'] == 'none': return route.fulfill(status=404, body='not found')
        if ST['email'] == 'nokey': return jr(route, {'error': {'message': 'Email is not set up: add RESEND_API_KEY and HX_MAIL_FROM in Supabase > Edge Functions > Secrets.'}}, 502)
        return jr(route, {'ok': True, 'sent_to': 's@x', 'items': 9})
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
DBT = psql_json("select hx_my_tasks('lic-mo')::text")
N = len(DBT); OVER = sum(1 for t in DBT if t['overdue'])
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN, 'email': 's@x'}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('.nav')
    check(N >= 8 and OVER >= 1, 'the database finds the admin\'s tasks (%d, %d overdue)' % (N, OVER))
    pg.wait_for_selector('.nav .tkn')
    check(pg.locator('.nav .tkn').inner_text() == str(N), 'menu shows the number of open tasks')
    card = pg.locator('.card', has=pg.locator('.k', has_text=re.compile('^My tasks$')))
    check(card.count() == 1 and (str(N) + ' waiting') in card.inner_text() and (str(OVER) + ' overdue') in card.inner_text(), 'dashboard card: waiting and overdue')
    pg.locator('.nav button', has_text='My Tasks').click(); pg.wait_for_selector('h1 >> text=My Tasks')
    rows = pg.locator('.tkrow')
    check(rows.count() == N, 'every task listed')
    check('Overdue' in rows.first.inner_text(), 'overdue tasks first')
    check(pg.locator('.tkrow', has_text='Decide hold').count() >= 1 and pg.locator('.tkrow', has_text='Approve SOP draft: Line Cleaning').count() == 1 and pg.locator('.tkrow', has_text='Calibration due: EQ-T39 Scale 1').count() == 1, 'decisions listed (hold, SOP draft, calibration)')
    check(pg.locator('.tkrow', has_text='Read and sign: Lead Only').count() == 1 and pg.locator('.tkrow', has_text='Read and sign: Cart Filling').count() == 0, 'SOPs to sign: only the ones still unsigned')
    pg.locator('.card .k', has_text=re.compile('^Overdue$')).click()
    check(rows.count() == OVER, 'Overdue filter')
    pg.locator('.card .k', has_text=re.compile('^Your decision$')).click()
    dec = sum(1 for t in DBT if t['group'] != 'mine')
    check(rows.count() == dec and pg.locator('.tkrow .badge', has_text='Hold').count() >= 1, 'decisions filter')
    pg.screenshot(path=OUT + 'tasks.png', full_page=True)
    pg.locator('.card .k', has_text=re.compile('^All$')).click()
    pg.locator('.tkrow', has_text='Decide hold').first.get_by_role('button', name='Open').click(); pg.wait_for_selector('h1 >> text=Hold')
    check(True, 'Open goes to the module (Hold and Release)')
    # email me
    pg.locator('.nav button', has_text='My Tasks').click(); pg.wait_for_selector('.tkrow')
    pg.get_by_role('button', name='Email me this list').click(); pg.wait_for_selector('text=Sent to s@x (9 tasks).')
    check(ST['emails'][-1] == {'mode': 'test', 'lic': 'lic-mo', 'license': 'Black Fox'}, 'Email me this list: sends my list for this license')
    ST['email'] = 'nokey'; pg.get_by_role('button', name='Email me this list').click(); pg.wait_for_selector('text=add RESEND_API_KEY')
    check(True, 'email not set up: the reason is shown')
    ST['email'] = 'none'; pg.get_by_role('button', name='Email me this list').click(); pg.wait_for_selector('text=deploy hendrix-notify.ts')
    check(True, 'email function not deployed: clear message')
    # My account: daily email switch
    pg.locator('.top').get_by_role('button', name='Sam', exact=True).click(); pg.wait_for_selector('text=Daily task email')
    box = pg.locator('label.ck', has_text='Email me my task list on work days').locator('input')
    check(box.is_checked(), 'daily task email on by default')
    box.click(); pg.wait_for_selector('text=Daily task email switched off.')
    check(ST['flags'] == [False] and not box.is_checked(), 'daily task email switched off (saved)')
    # Settings > Email (admin)
    pg.locator('.nav').get_by_role('button', name='Settings', exact=True).click(); pg.get_by_role('button', name='Email', exact=True).click()
    pg.wait_for_selector('text=Last email sent')
    check(pg.locator('td', has_text='Hold placed').count() >= 1 and pg.get_by_role('button', name='Save settings').count() == 0, 'Settings > Email: status and the email log (no Save button)')
    # not installed
    ST['missing'] = True; pg.locator('.nav button', has_text='My Tasks').click(); pg.wait_for_selector('text=run hendrix_step39.sql')
    check(True, 'clear message when step 39 is not installed'); ST['missing'] = False
    # members do not see the Email tab
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'settings': 'admin'}
    pg.reload(); pg.wait_for_selector('.nav')
    pg.locator('.nav').get_by_role('button', name='Settings', exact=True).click(); pg.wait_for_selector('text=Everything else')
    check(pg.get_by_role('button', name='Email', exact=True).count() == 0, 'Email tab is for admins only')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
