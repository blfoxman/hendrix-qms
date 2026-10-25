import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_env_points'] = []; T['hx_env_tests'] = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_env_points' and m == 'POST':
        r = json.loads(request.post_data); r.setdefault('active', True); r.setdefault('location', ''); r.setdefault('notes', ''); r.setdefault('source', ''); T['hx_env_points'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_env_tests' and m == 'POST':
        r = json.loads(request.post_data); p = next(x for x in T['hx_env_points'] if x['id'] == r['point_id'])
        if p['lab_required'] and not r['lab_accredited']: return jr(route, {'message': 'This test must be done by an ISO/IEC 17025 accredited lab.'}, 400)
        r.update({'recorded_by': 'Sam', 'voided': False}); T['hx_env_tests'].append(r); return jr(route, [r], 201)
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def prow(pg, name): return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(name) + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('.card.gold', has_text='Facility tests').locator('text=No test plan yet').count() == 1, 'dashboard: no test plan yet')
    pg.get_by_role('button', name='Facility Tests').click(); pg.wait_for_selector('text=CSQ test plan for a manufacturing license')
    check(pg.locator('text=Irrigation water').count() == 0 and pg.locator('text=Process gas (CO2 / nitrogen / hydrocarbon)').count() >= 1, 'manufacturing plan: process water and gases, no irrigation / soil')
    pg.get_by_role('button', name='Add the test plan').click(); pg.wait_for_selector('.msg >> text=Added 6 test points')
    check(len(T['hx_env_points']) == 6 and pg.locator('.card.gold', has_text='Overdue or never tested').locator('.v').inner_text() == '6', '6 test points, all never tested')
    prow(pg, 'Incoming water (point of use)').get_by_role('button', name='Record result').click(); md = pg.locator('.md')
    field(md, 'Lab *').fill('Pace Analytical'); md.locator('label.ck', has_text='ISO/IEC 17025 accredited').locator('input').uncheck()
    field(md, 'Results (values)').fill('E. coli ND; coliforms <1'); md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.md .msg.err >> text=ISO/IEC 17025')
    md.locator('label.ck', has_text='ISO/IEC 17025 accredited').locator('input').check(); md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.msg >> text=Recorded a pass for Incoming water')
    nxt = (dt.date.today() + dt.timedelta(days=365)).isoformat()
    pg.wait_for_selector('tr:has-text("Incoming water") .badge:has-text("Next")'); check(prow(pg, 'Incoming water (point of use)').locator('.badge', has_text='Next ' + nxt).count() == 1, 'next due a year after the sample')
    prow(pg, 'Food-contact surface swabs').get_by_role('button', name='Record result').click(); md = pg.locator('.md')
    field(md, 'Result').select_option('fail'); field(md, 'Results (values)').fill('ATP 450 RLU on filler nozzle'); md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.md .msg.err >> text=corrective action')
    field(md, 'Corrective action *').fill('Re-cleaned, re-swabbed 30 RLU'); md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.msg >> text=Recorded a FAIL')
    pg.wait_for_selector('tr:has-text("Food-contact surface swabs") .badge:has-text("Failed")')
    check(prow(pg, 'Food-contact surface swabs').locator('.badge', has_text='Failed').count() == 1 and T['hx_env_tests'][1]['lab_accredited'] is False, 'swab without a lab: failed result recorded with corrective action')
    prow(pg, 'Food-contact surface swabs').get_by_role('button', name='History').click(); md = pg.locator('.md')
    check(md.locator('text=Corrective action: Re-cleaned').count() == 1 and md.get_by_role('button', name='Deviation').count() == 1, 'history shows the corrective action and can raise a deviation')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print program').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Facility test program' in html and 'NEVER TESTED' in html and '2A.7' in html and 'ISO/IEC 17025 lab' in html, 'printable test program with CSQ clauses'); w.close()
    pg.get_by_role('button', name='+ Test point').click(); md = pg.locator('.md')
    field(md, 'Name *').fill('Ice machine'); field(md, 'What is tested').select_option('process_water'); field(md, 'Every (days) *').fill('180')
    check(md.locator('text=Supports CSQ 2A.7, 3B.1.3, 3B.1.7, 3C.1.5.').count() == 1, 'test point shows the CSQ clauses it supports')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Ice machine.')
    pg.screenshot(path=OUT + 'envtests.png')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Open facility tests')
    check(pg.locator('.card.gold', has_text='Open facility tests').locator('text=/5 overdue or never tested · 1 failed/').count() == 1, 'dashboard: overdue and failed counts')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
