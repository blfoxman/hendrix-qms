import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); td = dt.date.today(); TODAY = td.isoformat()
D2 = (td - dt.timedelta(days=2)).isoformat(); D10 = (td - dt.timedelta(days=10)).isoformat(); D40 = (td - dt.timedelta(days=40)).isoformat()
for t in ('hx_mgmt_reviews', 'hx_verification_plan', 'hx_verification_records', 'hx_risks', 'hx_risk_reviews'): T[t] = []
L = {'state_id': 'st-mo', 'license_id': 'lic-mo'}
T['hx_complaints'] = [{**L, 'id': 'co1', 'number': 'CMP-1', 'received_on': D40, 'category': 'Product quality', 'type': 'complaint', 'status': 'closed'}, {**L, 'id': 'co2', 'number': 'CMP-2', 'received_on': D10, 'category': 'Product quality', 'type': 'complaint', 'status': 'open'}]
T['hx_deviations'] = [{**L, 'id': 'dv1', 'number': 'DEV-1', 'title': 'x', 'created_at': D10 + 'T10:00:00Z', 'category': 'Sanitation', 'priority': 'major', 'status': 'open'}]
T['hx_capas'] = [{**L, 'id': 'ca1', 'number': 'CAPA-1', 'title': 'x', 'status': 'open', 'due_date': D2}]
T['hx_conformance'] = [{**L, 'id': 'cf1', 'standard_id': 's1', 'clause_id': 'c1', 'status': 'Conforming'}, {**L, 'id': 'cf2', 'standard_id': 's1', 'clause_id': 'c2', 'status': 'Partial'}]
T['hx_risks'] = [{**L, 'id': 'rk1', 'number': 'RK-001', 'title': 'Residual solvent', 'status': 'open', 'likelihood': 3, 'severity': 4, 'score': 12, 'residual_likelihood': None, 'residual_severity': None, 'next_review': '2027-01-01', 'created_at': D40 + 'T10:00:00Z', 'category': 'product_safety'}]
T['hx_risk_reviews'] = [{**L, 'id': 'rr1', 'risk_id': 'rk1', 'reviewed_on': D10, 'likelihood': 3, 'severity': 4, 'effective': True}]
T['hx_facility_log'] = [{**L, 'id': 'fl1', 'log_type': 'sanitation', 'created_at': D2 + 'T14:00:00Z', 'data': {'verified_by': 'Lee'}, 'voided': False, 'result': 'Pass'}]
SEQ = {'MR': 0, 'VS': 0}
REQ = ['prev_actions', 'complaints', 'audits', 'deviations', 'risks', 'csq', 'changes', 'resources']
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_mgmt_reviews' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST': SEQ['MR'] += 1; r = {**b, 'number': 'MR-2026-%03d' % SEQ['MR'], 'status': 'draft', 'signed_by': '', 'shared_on': None, 'shared_with': '', 'created_at': NOW}; T['hx_mgmt_reviews'].append(r); return jr(route, [r], 201)
        cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_mgmt_reviews'] if x['id'] == cid); n = {**r, **b}
        if b.get('status') == 'held' and r['status'] != 'held':
            miss = [k for k in REQ if not (n['inputs'].get(k) or {}).get('notes')]
            if miss: return jr(route, {'message': 'Discuss every required input before signing (missing: %s).' % ' '.join(miss)}, 400)
            if not n['decisions']: return jr(route, {'message': 'Record the decisions'}, 400)
            n['signed_by'] = 'Sam'; n['signed_at'] = NOW
        r.update(n); return jr(route, [r])
    if tbl == 'hx_verification_plan' and m == 'POST':
        r = json.loads(request.post_data); SEQ['VS'] += 1; r.update({'number': 'VS-%03d' % SEQ['VS'], 'active': True}); T['hx_verification_plan'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_verification_records' and m == 'POST':
        r = json.loads(request.post_data)
        if r['result'] == 'issues' and not (r['findings'] and r['action']): return jr(route, {'message': 'Describe the issues found and the action taken.'}, 400)
        r.update({'voided': False, 'recorded_by': 'Sam', 'created_at': NOW}); T['hx_verification_records'].append(r); return jr(route, [r], 201)
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def inp(md, label): return md.locator('.card', has=md.page.locator('b', has_text=re.compile('^' + re.escape(label) + r'( \*)?$'))).first
def vrow(pg, a): return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(a) + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.wait_for_selector('.card.gold >> text=Review and verification')
    check(pg.locator('.card.gold', has_text='Review and verification').locator('text=No management review').count() == 1, 'dashboard: no management review')
    check(pg.locator('text=Level 3:').count() == 0, 'no Level 3 modules left on the coming-soon list')
    pg.get_by_role('button', name='Management Review').click(); pg.wait_for_selector('text=No management reviews yet.')
    pg.get_by_role('button', name='+ Management review').click(); md = pg.locator('.md'); md.locator('text=Filled from Hendrix records').wait_for()
    fx = lambda k: inp(md, k).locator('textarea').first.input_value()
    check('2 complaints received' in fx('Complaints and customer feedback') and '1 open today' in fx('Complaints and customer feedback'), 'complaints filled from records')
    check('1 deviation' in fx('Deviations and corrective actions (CAPA)') and '1 overdue' in fx('Deviations and corrective actions (CAPA)'), 'deviations and CAPAs filled')
    check('1 high / critical' in fx('Risks and opportunities') and 'CSQ self-assessment: 1 conforming, 1 partial' in fx('CSQ conformance'), 'risks and CSQ conformance filled')
    check(fx('Actions from the last review') == 'First management review on record.', 'first review noted')
    field(md, 'Attendees').fill('Sam (GM), Lee (QA)'); md.get_by_role('button', name='Sign as held').click(); pg.wait_for_selector('.md .msg.err >> text=Discuss every required input')
    for k in ['Actions from the last review', 'Complaints and customer feedback', 'Internal, external and regulatory audits', 'Deviations and corrective actions (CAPA)', 'Risks and opportunities', 'CSQ conformance', 'Changes that could affect the system', 'Resources (people, equipment, facility, budget)']:
        inp(md, k).locator('textarea').nth(1).fill('Reviewed - ok')
    md.get_by_role('button', name='Sign as held').click(); pg.wait_for_selector('.md .msg.err >> text=decisions')
    field(md, 'Decisions and conclusions').fill('System is effective; add a QA technician'); md.get_by_role('button', name='+ Action').click()
    md.locator('input[placeholder="Action"]').fill('Hire a QA technician'); md.locator('input[placeholder="Who"]').fill('Sam')
    md.get_by_role('button', name='Sign as held').click(); pg.wait_for_selector('.msg >> text=Signed management review MR-2026-001.')
    r0 = T['hx_mgmt_reviews'][0]; check(r0['status'] == 'held' and r0['signed_by'] == 'Sam' and r0['next_review'] and len(r0['actions']) == 1, 'review signed with an action and next date')
    pg.wait_for_selector('.card.gold >> text=Minutes shared'); check(pg.locator('.card.gold', has_text='Last review').locator('.v').inner_text() == TODAY, 'stat: last review today')
    pg.get_by_role('button', name='Follow-up').click(); md = pg.locator('.md')
    md.locator('input[type=checkbox][title=Done]').check(); field(md, 'Minutes shared with').fill('All managers'); field(md, 'Shared on').fill(TODAY); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved MR-2026-001.')
    check(r0['actions'][0]['done'] and r0['shared_on'] == TODAY, 'action done and minutes shared')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Management review MR-2026-001' in html and 'CSQ 5.1.3' in html and '2 complaints received' in html and 'add a QA technician' in html and 'All managers' in html, 'printable minutes'); w.close()
    pg.screenshot(path=OUT + 'mgmtreview.png', full_page=True)
    # verification schedule
    pg.locator('.tabs').get_by_role('button', name='Verification schedule').click(); pg.wait_for_selector('text=No verification schedule yet.')
    pg.get_by_role('button', name='Suggested schedule').click(); md = pg.locator('.md'); md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 13 verification activities.')
    vrow(pg, 'Sanitation records reviewed and signed').locator('text=from Sanitation log').wait_for()
    check(vrow(pg, 'Sanitation records reviewed and signed').locator('td').nth(4).inner_text().startswith(D2), 'sanitation verification dated from the facility log')
    check(vrow(pg, 'Risk register review').locator('td').nth(4).inner_text().startswith(D10) and vrow(pg, 'Management review').locator('td').nth(4).inner_text().startswith(TODAY), 'risk review and management review dated from their records')
    check(vrow(pg, 'Labels checked against the batch').locator('.badge', has_text='Due now').count() == 1, 'manual activity never done = due now')
    vrow(pg, 'Labels checked against the batch').get_by_role('button', name='Record').click(); md = pg.locator('.md')
    field(md, 'Result').select_option('issues'); field(md, 'Findings').fill('Gummy label shows old THC limit'); md.get_by_role('button', name='Record', exact=True).click(); pg.wait_for_selector('.md .msg.err >> text=action taken')
    field(md, 'Action taken').fill('Labels reprinted, template fixed'); md.get_by_role('button', name='Record', exact=True).click(); pg.wait_for_selector('.msg >> text=Recorded: Labels checked against the batch.')
    vrow(pg, 'Labels checked against the batch').locator('td').nth(4).filter(has_text=TODAY).wait_for()
    check(vrow(pg, 'Labels checked against the batch').locator('.badge', has_text='Due now').count() == 0, 'recorded verification moves the next due date')
    vrow(pg, 'Labels checked against the batch').get_by_role('button', name='History').click(); md = pg.locator('.md')
    check(md.locator('text=Action: Labels reprinted').count() == 1 and md.get_by_role('button', name='Deviation').count() == 1, 'history shows the issue and can raise a deviation')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print schedule').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Verification schedule' in html and 'CSQ 5.1.8' in html and 'every 7 days' in html, 'printable verification schedule'); w.close()
    pg.screenshot(path=OUT + 'verification.png', full_page=True)
    T['hx_standards'].append({'id': 's1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [], 'modules': {}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 's1', 'target_level': 3, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    def clause(c):
        r = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(c) + '$'))).first; r.locator('div.row').first.click(timeout=5000); pg.wait_for_timeout(400); return r.inner_text()
    e513, e518 = clause('5.1.3'), clause('5.1.8')
    print(e513.replace('\n', ' | ')[250:650]); print(e518.replace('\n', ' | ')[250:700])
    check('Last held ' + TODAY in e513 and '8 of 8 required inputs discussed' in e513 and 'minutes shared' in e513, '5.1.3 management review evidence')
    check('13 verification activities' in e518 and 'overdue' in e518.lower(), '5.1.8 verification evidence (overdue flagged)')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Review and verification')
    pg.locator('.card.gold', has_text='Review and verification').locator('text=/verifications? overdue/').wait_for(timeout=8000)
    check(True, 'dashboard shows overdue verifications')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
