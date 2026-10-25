import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
td = dt.date.today(); lm_end = td.replace(day=1) - dt.timedelta(days=1); LM = lm_end.strftime('%Y-%m'); LMD = lm_end.replace(day=10).isoformat()
MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; LML = MON[lm_end.month - 1] + ' ' + str(lm_end.year)
for t in ('hx_org_positions', 'hx_objectives', 'hx_objective_results', 'hx_qms_settings'): T[t] = []
T['hx_sops'] = [{'id': 'sp1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'sop_number': 'SOP-QA-001', 'title': 'Safety, Quality and Compliance Policy', 'version': '2', 'status': 'published'}]
T['hx_capas'] = [{'id': 'ca1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'CAPA-1', 'title': 'a', 'status': 'closed', 'closed_at': LMD + 'T15:00:00Z', 'due_date': lm_end.isoformat()},
                 {'id': 'ca2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'CAPA-2', 'title': 'b', 'status': 'closed', 'closed_at': LMD + 'T15:00:00Z', 'due_date': lm_end.replace(day=2).isoformat()}]
SEQ = [0]
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def met(o, v): return v >= o['target'] if o['direction'] == 'up' else v <= o['target']
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_org_positions' and m == 'DELETE':
        cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0])
        if any(p.get('reports_to') == cid for p in T['hx_org_positions']): return jr(route, {'message': 'People report to this position. Move them to another position first.'}, 400)
    if tbl == 'hx_qms_settings' and m == 'POST':
        r = json.loads(request.post_data); T['hx_qms_settings'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_objectives' and m == 'POST':
        o = json.loads(request.post_data); SEQ[0] += 1; o.update({'number': 'OBJ-%03d' % SEQ[0], 'status': 'active', 'close_note': None, 'created_at': NOW}); o.setdefault('description', ''); o.setdefault('action_plan', ''); o.setdefault('due_on', None)
        T['hx_objectives'].append(o); return jr(route, [o], 201)
    if tbl == 'hx_objectives' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); o = next(x for x in T['hx_objectives'] if x['id'] == cid)
        if b.get('status') in ('achieved', 'dropped') and not b.get('close_note'): return jr(route, {'message': 'Add a note'}, 400)
        o.update(b); return jr(route, [o])
    if tbl == 'hx_objective_results' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST': r = b
        else: cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_objective_results'] if x['id'] == cid); r = {**r, **b}
        o = next(x for x in T['hx_objectives'] if x['id'] == r['objective_id']); r['met'] = met(o, r['value']); r['updated_at'] = NOW; r['created_at'] = r.get('created_at', NOW)
        if not r['met'] and not r.get('action'): return jr(route, {'message': 'The target was missed: record the action that will be taken.'}, 400)
        if m == 'POST': T['hx_objective_results'].append(r)
        else: next(x for x in T['hx_objective_results'] if x['id'] == r['id']).update(r)
        return jr(route, [r], 201 if m == 'POST' else 200)
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def orow(pg, t): return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(t) + '$')))
def card(pg, name): return pg.locator('.card', has=pg.locator('b', has_text=re.compile('^' + re.escape(name) + '$'))).first
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.wait_for_selector('.card.gold >> text=Quality objectives')
    check(pg.locator('.card.gold', has_text='Quality objectives').locator('text=No objectives set').count() == 1, 'dashboard: no objectives set')
    pg.get_by_role('button', name='Org Chart').click(); pg.wait_for_selector('text=No org chart yet.')
    pg.get_by_role('button', name='+ Position').click(); md = pg.locator('.md')
    field(md, 'Position *').fill('General Manager'); field(md, 'Person').fill('Sam'); md.locator('label.ck', has_text='Senior management').locator('input').check()
    field(md, 'Functions and responsibilities').fill('Runs the facility; provides resources for the quality system'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved General Manager.')
    orow(pg, 'General Manager').get_by_role('button', name='+ Under').click(); md = pg.locator('.md')
    check(field(md, 'Reports to').input_value() == T['hx_org_positions'][0]['id'], '"+ Under" pre-selects the manager')
    field(md, 'Position *').fill('Quality Manager'); field(md, 'Person').fill('Lee'); md.locator('label.ck', has_text='Quality / CSQ lead').locator('input').check()
    field(md, 'Functions and responsibilities').fill('CSQ practitioner; owns the QMS, CAPA and internal audits'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Quality Manager.')
    orow(pg, 'Quality Manager').get_by_role('button', name='+ Under').click(); md = pg.locator('.md')
    field(md, 'Position *').fill('QA Technician'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved QA Technician.')
    check(pg.locator('.card svg rect').count() == 3 and pg.locator('.card svg path').count() == 2, 'org chart drawn: 3 boxes, 2 reporting lines')
    check(pg.locator('.card.gold', has_text='Key CSQ roles').locator('.v').inner_text() == '2 / 3' and pg.locator('.row', has_text='Quality backup').locator('.badge', has_text='Not assigned').count() == 1, 'key roles: quality backup flagged as not assigned')
    check(orow(pg, 'QA Technician').locator('.badge', has_text='Vacant').count() == 1, 'vacant position shown')
    orow(pg, 'General Manager').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    opts = md.locator('label.f', has=pg.locator('span', has_text='Reports to')).locator('option').all_inner_texts()
    check(not any('Quality Manager' in o or 'QA Technician' in o for o in opts), 'cannot report to someone below you (no loops)')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    orow(pg, 'General Manager').get_by_role('button', name='Remove').click(); pg.wait_for_selector('.msg.err >> text=People report to this position')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print org chart').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Organization chart' in html and 'CSQ 5.1.1' in html and 'Quality Manager' in html and '<svg' in html, 'printable org chart with the diagram'); w.close()
    pg.screenshot(path=OUT + 'orgchart.png', full_page=True)
    # objectives
    pg.locator('.tabs').get_by_role('button', name='Quality objectives').click(); pg.wait_for_selector('text=No quality policy linked')
    pg.get_by_role('button', name='Link the policy SOP').click(); md = pg.locator('.md')
    field(md, 'Policy SOP').select_option('sp1'); field(md, 'How it is shared with staff').fill('Signed by all staff, posted in the break room'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Policy saved.'); pg.wait_for_selector('text=SOP-QA-001 Safety, Quality and Compliance Policy v2')
    check(pg.locator('text=SOP-QA-001 Safety, Quality and Compliance Policy v2').count() == 1 and T['hx_qms_settings'][0]['policy_sop_id'] == 'sp1', 'policy SOP linked')
    pg.get_by_role('button', name='Suggested objectives').click(); md = pg.locator('.md'); md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 8 objectives.')
    check(len(T['hx_objectives']) == 8 and all(o['owner'] == 'Sam' for o in T['hx_objectives']), '8 suggested objectives')
    card(pg, 'CAPAs closed on time').get_by_role('button', name='Record result').click(); md = pg.locator('.md')
    md.locator('text=1 of 2 CAPAs closed on time').wait_for()
    check(field(md, 'Value (%)').input_value() == '50' and md.locator('.badge', has_text='Target missed').count() == 1, 'KPI counted from CAPA records: 50% (missed)')
    md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.md .msg.err >> text=record the action')
    field(md, 'Action to get back on target').fill('Weekly CAPA review in the production meeting'); md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.msg >> text=' + LML + ': 50% - target missed.')
    r0 = T['hx_objective_results'][0]; check(r0['period'] == LM and r0['auto'] is True and r0['met'] is False, 'result stored for last month, marked as counted by Hendrix')
    card(pg, 'CAPAs closed on time').locator('.badge', has_text='Off target').wait_for(timeout=5000)
    c = card(pg, 'CAPAs closed on time'); check(c.locator('.badge', has_text='Off target').count() == 1 and c.locator('text=Action: Weekly CAPA review').count() == 1 and c.locator('svg rect').count() == 6, 'card: off target, action, 6-period chart')
    pg.get_by_role('button', name='+ Objective').click(); md = pg.locator('.md')
    field(md, 'Objective *').fill('On-time delivery to dispensaries'); field(md, 'Target *').fill('95'); field(md, 'Unit').fill('%'); field(md, 'How often').select_option('quarterly')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved objective OBJ-009.')
    card(pg, 'On-time delivery to dispensaries').get_by_role('button', name=re.compile('^Record')).click(); md = pg.locator('.md')
    check(md.get_by_role('button', name='Get from Hendrix').count() == 0, 'manual KPI has no automatic count')
    field(md, 'Value (%)').fill('97'); md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.msg >> text=target met.')
    card(pg, 'On-time delivery to dispensaries').locator('.badge', has_text='On target').wait_for(timeout=5000)
    check(card(pg, 'On-time delivery to dispensaries').locator('.badge', has_text='On target').count() == 1, 'manual KPI on target')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print KPI board').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Quality objectives and KPIs' in html and 'SOP-QA-001' in html and 'MISSED' in html and 'Weekly CAPA review' in html, 'printable KPI board with the policy'); w.close()
    card(pg, 'Facility tests passed').get_by_role('button', name='Drop').click(); md = pg.locator('.md')
    md.locator('textarea').fill('No facility test lab yet - restart in Q1'); md.get_by_role('button', name='Drop objective').click(); pg.wait_for_selector('.msg >> text=Marked OBJ-007 dropped.'); pg.wait_for_selector('text=Show achieved and dropped (1)')
    check(card(pg, 'Facility tests passed').count() == 0 and pg.locator('text=Show achieved and dropped (1)').count() == 1, 'dropped objective hidden, can be shown')
    pg.screenshot(path=OUT + 'objectives.png', full_page=True)
    # standards evidence
    T['hx_standards'].append({'id': 's1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [], 'modules': {}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 's1', 'target_level': 3, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    def clause(c):
        r = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(c) + '$'))).first; r.locator('div.row').first.click(timeout=5000); pg.wait_for_timeout(300); return r.inner_text()
    e511, e512, e514 = clause('5.1.1'), clause('5.1.2'), clause('5.1.4')
    print(e511.replace('\n', ' | ')[300:700]); print(e514.replace('\n', ' | ')[300:700])
    check('3 positions with reporting lines' in e511 and 'not assigned: quality backup' in e511.lower(), '5.1.1 org chart evidence')
    check('Policy: SOP-QA-001' in e512 and '8 measurable objectives' in e512, '5.1.2 policy and objectives evidence')
    check('2 of 8 active objectives measured in the last quarter' in e514, '5.1.4 KPI review evidence')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Quality objectives')
    check(pg.locator('.card.gold', has_text='Quality objectives').locator('text=1 of 8 on target').count() == 1, 'dashboard: 1 of 8 on target')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
