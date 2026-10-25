import re, subprocess, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
SP = OUT
PGDB = os.environ.get('HX_PGDB', 'lmtest')
def pgcmd(*a): return ['psql', '-X', '-q', '-d', PGDB] + list(a)
T['hx_license_settings'] = [{'license_id': 'lic-mo', 'state_id': 'st-mo', 'legal_name': '', 'dba': '', 'address': '', 'phone': '', 'email': '', 'print_footer': '', 'logo': None,
                             'break1_min': 15, 'break2_min': 30, 'break3_min': 15, 'log_due': {}, 'review_days': {}, 'linemap_idle_hours': 4}]
STATE = {'missing': False, 'calls': 0}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def pgmap(lic):
    # the real step-36 function on the local Postgres copy (the bridge under test)
    out = subprocess.run(pgcmd('-Atc', "set test.uid='11111111-1111-1111-1111-111111111111'; select hx_line_map('%s')::text" % lic), capture_output=True, text=True)
    return json.loads(out.stdout.strip().split('\n')[-1])
_h = handle
def handle(route, request):
    u = request.url; m = request.method; path = urllib.parse.urlparse(u).path; tbl = path.split('/')[-1]
    if path.endswith('/rpc/hx_line_map'):
        STATE['calls'] += 1
        if STATE['missing']: return jr(route, {'code': 'PGRST202', 'message': 'Could not find the function public.hx_line_map(p_lic) in the schema cache'}, 404)
        b = json.loads(request.post_data)
        return jr(route, pgmap(b['p_lic']))
    if tbl == 'hx_license_settings' and m == 'PATCH':
        b = json.loads(request.post_data); r = T['hx_license_settings'][0]; r.update(b); return jr(route, [r])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def train(pg, label): return pg.locator('button[aria-label^="%s,"]' % label)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1500, 'height': 1000}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.wait_for_selector('.card.gold >> text=Line map')
    card = pg.locator('.card.gold', has_text='Line map')
    check(card.locator('text=5 batches stopped').count() == 1, 'dashboard card: 5 batches stopped')
    pg.get_by_role('button', name='Line Map', exact=True).click(); pg.wait_for_selector('text=Production Line Map'); pg.wait_for_selector('text=Stops right now')
    kp = lambda k: pg.locator('.card', has=pg.locator('.k', has_text=re.compile('^' + k + '$'))).first.inner_text()
    print(kp('In production').replace('\n', ' | '), '/', kp('Stopped').replace('\n', ' | '))
    check(kp('In production').split('\n')[1] == '7' and kp('Moving').split('\n')[1] == '1' and kp('Stopped').split('\n')[1] == '5' and kp('At the lab').split('\n')[1] == '1', 'KPIs: 7 in production, 1 moving, 5 stopped, 1 at the lab')
    check(kp('Shipped').split('\n')[1] == '1' and '1 planned' in kp('Shipped') and kp('On the floor').split('\n')[1] == '1', 'KPIs: 1 shipped, 1 planned, 1 on the floor')
    lines = [t for t in ['Cartridges', 'Gummies', 'Pre-Rolls'] if pg.locator('div', has_text=re.compile('^' + t + '$')).count()]
    check(lines == ['Cartridges', 'Gummies', 'Pre-Rolls'] and pg.locator('text=Ethanol Extraction').count() == 0, 'one subway line per product type in use: ' + str(lines))
    check(pg.locator('text=Primed Oil').count() >= 1 and pg.locator('text=Infused Joints').count() >= 1 and pg.locator('text=Lab testing').count() >= 1, 'stations come from the batch record sections + shared trunk')
    # stop reasons from every bridge
    check(train(pg, 'CT-2026-118').locator('text=EQUIPMENT').count() == 0 and 'deviation' in train(pg, 'CT-2026-118').get_attribute('aria-label').lower(), 'CT-118: stopped by its open deviation (equipment of its clearance is fine)')
    check('Line clearance not cleared' in train(pg, 'CT-2026-119').get_attribute('aria-label'), 'CT-119: line clearance not cleared')
    check('EQ-014 Cone filler is past its calibration date' in train(pg, 'PR-2026-207').get_attribute('aria-label'), 'PR-207: equipment of its line clearance past calibration')
    check('CCP Cooking temperature out of limits' in train(pg, 'GM-2026-045').get_attribute('aria-label'), 'GM-045: CCP out of limits waiting for verification')
    check(pg.locator('button[aria-label^="2 batches at Lab testing"]').count() == 1, 'two batches at Lab testing grouped into one marker')
    check(train(pg, 'CT-2026-112').locator('text=MOVING').count() == 1 and train(pg, 'GM-2026-038').locator('text=SHIPPED').count() == 1 and train(pg, 'PP-2026-019').locator('text=PLANNED').count() == 1, 'released batch moving at QC release; shipped batch; plan on the Planned station')
    check(pg.locator('text=GM-2025-001').count() == 0 and pg.locator('text=MI-1').count() == 0, 'old batches and other licenses are not on the map')
    # click a stopped batch: why + journey + jump
    train(pg, 'CT-2026-119').click(); pg.wait_for_selector('text=WHY IT IS STOPPED')
    det = pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
    check(det.locator('text=Residue on the filler nozzle').count() == 1 and det.locator('text=Line clearance LC-2026-212').count() == 1 and det.locator('text=No update for 9 h').count() == 1, 'detail: both reasons with the source record')
    check(det.locator('text=Fix the issues and record a line clearance that passes.').count() == 1 and det.locator('text=Journey').count() == 1, 'detail: what clears it + journey')
    pg.screenshot(path=SP + 'linemap_detail.png', full_page=True)
    # group -> pick the held batch
    pg.locator('button[aria-label^="2 batches at Lab testing"]').click(); pg.wait_for_selector('text=2 batches at Lab testing')
    pg.locator('.card button', has_text='GM-2026-041').first.click(); pg.wait_for_selector('text=On hold: Potency 8% over the label claim; retest ordered')
    det = pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
    check(det.locator('text=Hold HOLD-2026-012').count() == 1 and det.locator('text=Failed test on tag 1A4-GM41; no passing retest yet').count() == 1, 'held batch: hold + failed test, longest first')
    # stops list order (longest first) and the waiting batch
    rows = pg.locator('.card', has=pg.locator('h3', has_text='Stops right now')).locator('button b').all_inner_texts()
    print(rows)
    check(rows[0] == 'GM-2026-041' and rows[-1] == 'CT-2026-115' and len(rows) == 6, 'stops list: longest stop first, waiting batch last')
    # stops only filter dims the moving ones
    pg.get_by_role('button', name='Stops only').click()
    check(float(train(pg, 'CT-2026-112').evaluate('e=>getComputedStyle(e).opacity')) < .5 and float(train(pg, 'PR-2026-207').evaluate('e=>getComputedStyle(e).opacity')) == 1, 'Stops only dims moving batches')
    pg.get_by_role('button', name='All batches').click()
    # jump to the source module
    det.get_by_role('button', name='Open Hold and Release').click(); pg.wait_for_selector('h1 >> text=Hold')
    check(True, 'jump from a stop to the Hold and Release page')
    # idle threshold from Settings changes the map
    pg.get_by_role('button', name='Settings', exact=True).click(); pg.get_by_role('button', name='Line Map', exact=True).last.click()
    pg.locator('input[aria-label="Hours without an update"]').fill('12'); pg.get_by_role('button', name='Save settings').click(); pg.wait_for_selector('.msg >> text=Settings saved')
    check(T['hx_license_settings'][0]['linemap_idle_hours'] == 12, 'Settings > Line Map saves the idle hours (12)')
    subprocess.run(pgcmd('-c', "set session_replication_role=replica; update hx_license_settings set linemap_idle_hours=12 where license_id='lic-mo'"))
    pg.locator('.nav button', has_text='Line Map').click(); pg.wait_for_selector('text=Stops right now')
    check('No update' not in train(pg, 'CT-2026-119').get_attribute('aria-label') or 'Line clearance' in train(pg, 'CT-2026-119').get_attribute('aria-label'), 'idle rule follows the setting')
    pg.locator('button[aria-label^="CT-2026-119,"]').click(); pg.wait_for_selector('text=WHY IT IS STOPPED')
    check(pg.locator('text=No update for 9 h').count() == 0, 'with 12 h idle time the 9 h batch is no longer idle-stopped')
    subprocess.run(pgcmd('-c', "set session_replication_role=replica; update hx_license_settings set linemap_idle_hours=4 where license_id='lic-mo'"))
    # live data: a new hold appears on refresh
    subprocess.run(pgcmd('-c', "set session_replication_role=replica; insert into hx_holds(id,state_id,license_id,number,kind,batch_id,item,reason,status,placed_by,created_at) values ('lm-h9','st-mo','lic-mo','HOLD-2026-015','batch','lm-g','CT-2026-112','Customer return check','open','QA',now())"))
    pg.get_by_role('button', name='Refresh').click(); pg.wait_for_timeout(600)
    check('On hold: Customer return check' in train(pg, 'CT-2026-112').get_attribute('aria-label'), 'a new hold stops the batch on the next refresh')
    subprocess.run(pgcmd('-c', "set session_replication_role=replica; delete from hx_holds where id='lm-h9'"))
    pg.get_by_role('button', name='Refresh').click(); pg.wait_for_timeout(600)
    pg.screenshot(path=SP + 'linemap.png', full_page=True)
    # view-only executive: sees the map, no jump buttons to modules they cannot open
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'linemap': 'read'}
    pg.reload(); pg.wait_for_selector('.nav')
    check(pg.locator('.nav button', has_text='Line Map').count() == 1 and pg.locator('.nav button', has_text='Hold and Release').count() == 0, 'executive with Line Map only: sees the map in the menu')
    pg.locator('.nav button', has_text='Line Map').click(); pg.wait_for_selector('text=Stops right now')
    train(pg, 'PR-2026-207').click(); pg.wait_for_selector('text=WHY IT IS STOPPED')
    check(pg.get_by_role('button', name='Open Equipment').count() == 0 and pg.get_by_role('button', name='Open Batch Tracker').count() == 0, 'no jump buttons to modules the person cannot open')
    T['hx_profiles'][0]['perms'] = {'qms': 'read'}
    pg.reload(); pg.wait_for_selector('.nav')
    check(pg.locator('.nav button', has_text='Line Map').count() == 0, 'no Line Map access: not in the menu')
    T['hx_profiles'][0]['role'] = 'admin'; T['hx_profiles'][0]['perms'] = {}
    # not installed yet
    STATE['missing'] = True; pg.reload(); pg.wait_for_selector('.nav'); pg.locator('.nav button', has_text='Line Map').click()
    pg.wait_for_selector('text=run hendrix_step36.sql')
    check(True, 'clear message when step 36 is not installed')
    STATE['missing'] = False
    # roles: Line Map in the access list and the starter roles
    pg.get_by_role('button', name='Roles', exact=True).click(); pg.wait_for_timeout(300)
    check('Line Map' in pg.content(), 'Line Map listed in roles / access')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
