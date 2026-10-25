import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today().isoformat()
T['hx_batches'] += [{'id': 'b1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'cart', 'batch_number': 'CT-200', 'sku': 'Cart 1g', 'flavor': 'Lemon', 'status': '', 'voided': False, 'created_at': '2026-10-02T10:00:00Z', 'data': {}}]
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def jerr(route, m): return jr(route, {'message': m}, 400)
def lvl(mod):
    p = T['hx_profiles'][0]
    return 3 if p['role'] == 'admin' else {'admin': 3, 'editor': 2, 'read': 1}.get((p.get('perms') or {}).get(mod), 0)
def nxt(tbl, pre): return '%s-2026-%03d' % (pre, sum(1 for x in T[tbl] if x.get('number', '').startswith(pre + '-')) + 1)
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if m == 'GET' or tbl not in ('hx_complaints', 'hx_audits', 'hx_audit_findings', 'hx_deviations'): return _h(route, request)
    b = json.loads(request.post_data) if request.post_data else {}
    rid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]) if 'id=eq.' in u else None
    if tbl == 'hx_deviations' and m == 'POST':
        r = dict(b); r.update({'number': nxt('hx_deviations', 'DEV'), 'status': 'open', 'created_at': now()}); T['hx_deviations'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_deviations': return _h(route, request)
    def dev(did): return next((d for d in T['hx_deviations'] if d['id'] == did), None)
    if tbl == 'hx_complaints':
        if m == 'POST':
            r = dict(b); r.update({'number': nxt('hx_complaints', 'FBK' if r['type'] == 'feedback' else 'CMP'), 'created_by': 'Sam', 'created_at': now(), 'closed_at': None, 'closed_by': '', 'deviation_id': None, 'deviation_number': '', 'investigator': '', 'investigation': '', 'resolution': '', 'responded_on': None, 'regulator_reported_on': None, 'due_date': None, 'root_cause': '', 'corrective_action': '', 'response': '', 'cancel_reason': ''})
            T['hx_complaints'].append(r); return jr(route, [r], 201)
        c = next(x for x in T['hx_complaints'] if x['id'] == rid); n = {**c, **b}
        if n.get('deviation_id'): n['deviation_number'] = dev(n['deviation_id'])['number']
        if c['status'] in ('closed', 'cancelled') and n['status'] == c['status']: return jerr(route, 'This complaint is closed. Reopen it first.')
        if n['status'] == 'closed' and c['status'] != 'closed' and n['type'] != 'feedback':
            if not n['investigator'].strip(): return jerr(route, 'Name who investigated the complaint (CSQ 1.7 a).')
            if not n['investigation'].strip(): return jerr(route, 'Record the investigation before closing.')
            if not n['resolution'].strip(): return jerr(route, 'Record the resolution before closing.')
            if (n['complainant_contact'] or n['customer']) and not n['responded_on']: return jerr(route, 'Record when the complainant was answered before closing (CSQ 1.7 a).')
            if n['type'] == 'adverse_event' and not n['regulator_reported_on']: return jerr(route, 'An adverse event must be reported to the state regulator before it is closed.')
        if n['status'] == 'closed' and c['status'] != 'closed': n['closed_at'] = now(); n['closed_by'] = 'Sam'
        c.update(n); return jr(route, [c])
    if tbl == 'hx_audits':
        if m == 'POST':
            r = dict(b); r.update({'number': nxt('hx_audits', 'IA'), 'created_at': now(), 'shared_with': '', 'shared_on': None, 'closed_by': ''}); T['hx_audits'].append(r); return jr(route, [r], 201)
        a = next(x for x in T['hx_audits'] if x['id'] == rid); n = {**a, **b}
        if n['status'] in ('completed', 'closed') and a['status'] not in ('completed', 'closed'):
            if not n['audit_date']: return jerr(route, 'Enter the date the audit was done (not in the future).')
            if not n['independent']: return jerr(route, 'Confirm the auditor does not audit their own work (CSQ 1.5 c).')
            miss = [c['clause'] for c in n['clauses'] if c['result'] == 'Nonconforming' and not any(f['audit_id'] == a['id'] and f['clause'] == c['clause'] for f in T['hx_audit_findings'])]
            if miss: return jerr(route, 'Record a finding for each nonconforming clause: ' + ', '.join(miss))
        if n['status'] == 'closed' and a['status'] != 'closed':
            if lvl('intaudits') < 3: return jerr(route, 'Only someone with Full access can close an audit.')
            if any(f['audit_id'] == a['id'] and f['status'] != 'closed' for f in T['hx_audit_findings']): return jerr(route, 'Close every finding first (CSQ 1.5 f).')
            if not n.get('shared_on') or not n.get('shared_with'): return jerr(route, 'Record who the results were shared with and when (CSQ 1.5 e).')
            n['closed_by'] = 'Sam'
        a.update(n); return jr(route, [a])
    if tbl == 'hx_audit_findings':
        if m == 'POST':
            r = dict(b); r.update({'status': 'open', 'created_at': now(), 'deviation_id': None, 'deviation_number': '', 'verification': '', 'closed_by': ''}); T['hx_audit_findings'].append(r); return jr(route, [r], 201)
        f = next(x for x in T['hx_audit_findings'] if x['id'] == rid); n = {**f, **b}
        if n.get('deviation_id'): n['deviation_number'] = dev(n['deviation_id'])['number']
        if n['status'] == 'closed' and f['status'] != 'closed':
            if not n['verification'].strip(): return jerr(route, 'Record how the correction was verified as effective (CSQ 1.5 f).')
            if n.get('deviation_id') and dev(n['deviation_id'])['status'] != 'closed': return jerr(route, 'Close deviation %s first (corrective action process).' % n['deviation_number'])
            n['closed_by'] = 'Sam'
        f.update(n); return jr(route, [f])
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def okmsg(pg, txt): pg.wait_for_selector('.msg >> text=' + txt, timeout=8000)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Open complaints')
    pg.wait_for_timeout(500)
    check('0 open' in pg.locator('.card.gold', has_text='Open complaints').inner_text() and '0% audited' in pg.locator('.card.gold', has_text='Open audits').inner_text(), 'dashboard cards')
    pg.get_by_role('button', name='Complaints', exact=True).click(); pg.wait_for_selector('text=No complaints on record')
    # log complaint
    pg.get_by_role('button', name='+ Log complaint').click(); md = pg.locator('.md')
    field(md, 'Priority').select_option('major'); field(md, 'Title').fill('Harsh taste on Lemon cart'); field(md, 'Complainant').fill('J. Doe'); field(md, 'Contact').fill('555-0101')
    field(md, 'Customer (dispensary)').fill('Dispensary A'); field(md, 'Category').select_option('Taste / smell'); field(md, 'Batch').select_option('b1'); field(md, 'Description').fill('Customer says the cart tastes burnt')
    md.get_by_role('button', name='Log complaint').click(); okmsg(pg, 'Logged CMP-2026-001')
    c1 = T['hx_complaints'][0]; check(c1['batch_id'] == 'b1' and c1['product'] == 'Cart 1g · Lemon' and c1['status'] == 'open', 'complaint logged, linked to batch, product filled from batch')
    md = pg.locator('.md'); md.get_by_role('button', name='Close', exact=True).click(); pg.wait_for_selector('.md .msg.err')
    check(md.locator('.msg.err', has_text='investigat').count() == 1, 'close blocked without investigator/investigation')
    field(md, 'Investigator (responsible)').fill('QA Lead Ana'); field(md, 'Investigation').fill('Retained sample tasted burnt; coil voltage too high'); md.get_by_role('button', name='Save and start investigating').click(); okmsg(pg, 'Saved.')
    check(T['hx_complaints'][0]['status'] == 'investigating' and T['hx_complaints'][0]['due_date'], 'investigating with due date')
    # raise deviation from complaint
    md = pg.locator('.md'); md.get_by_role('button', name='Raise deviation').click(); dm = pg.locator('.md').last
    field(dm, 'What happened?').fill('Burnt taste complaint, batch CT-200'); dm.get_by_role('button', name='Submit deviation').click(); okmsg(pg, 'Linked DEV-2026-001')
    check(T['hx_complaints'][0]['deviation_number'] == 'DEV-2026-001', 'deviation (CAPA) linked to complaint')
    # put batch on hold
    pg.locator('.md').get_by_role('button', name='Put batch on hold').click(); hm = pg.locator('.md')
    check(field(hm, 'Batch').input_value() == 'b1' and field(hm, 'Source').input_value() == 'Complaint', 'hold prefilled with batch and source Complaint')
    hm.get_by_role('button', name='Put on hold').click(); okmsg(pg, 'Put on hold')
    check(T['hx_complaints'][0].get('hold_id') and T['hx_holds'][0]['source'] == 'Complaint', 'batch held from complaint')
    if pg.locator('.md').count() == 0: pg.locator('.card', has_text='CMP-2026-001').click()
    md = pg.locator('.md')
    field(md, 'Resolution').fill('Replacement cart sent'); md.get_by_role('button', name='Close', exact=True).click(); pg.wait_for_selector('.md .msg.err >> text=answered')
    check(True, 'close blocked until complainant answered')
    field(md, 'Response to the complainant').fill('Apologized, replacement sent'); field(md, 'Answered on').fill(TODAY); md.get_by_role('button', name='Close', exact=True).click(); okmsg(pg, 'Closed CMP-2026-001')
    check(T['hx_complaints'][0]['status'] == 'closed', 'complaint closed with investigation, resolution, response')
    pg.locator('.md').get_by_role('button', name='Close window').click()
    # adverse event
    pg.get_by_role('button', name='+ Log complaint').click(); md = pg.locator('.md'); field(md, 'Type').select_option('adverse_event')
    check(md.locator('text=report it to the state regulator').count() == 1, 'adverse event warning')
    field(md, 'Title').fill('Dizziness after use'); field(md, 'Lot number').fill('CT-200'); md.get_by_role('button', name='Log complaint').click(); okmsg(pg, 'Logged CMP-2026-002')
    md = pg.locator('.md'); field(md, 'Investigator (responsible)').fill('Ana'); field(md, 'Investigation').fill('x'); field(md, 'Resolution').fill('y'); md.get_by_role('button', name='Close', exact=True).click(); pg.wait_for_selector('.md .msg.err >> text=regulator')
    check(T['hx_complaints'][1]['status'] == 'open', 'adverse event cannot close until reported to regulator')
    pg.locator('.md').get_by_role('button', name='Close window').click()
    check(pg.locator('.msg.err', has_text='Repeat complaints on the same lot: CT-200 (2)').count() == 1, 'repeat complaints on a lot flagged')
    # feedback
    pg.get_by_role('button', name='+ Feedback').click(); md = pg.locator('.md'); field(md, 'Title').fill('Dispensary A loves the Lemon cart'); field(md, 'Satisfaction').select_option('4')
    md.get_by_role('button', name='Log feedback').click(); okmsg(pg, 'Logged FBK-2026-001'); pg.locator('.md').get_by_role('button', name='Close window').click()
    check(pg.locator('.card.gold', has_text='Customer satisfaction').locator('.v').inner_text() == '4 / 5', 'satisfaction average')
    pg.locator('.tabs button', has_text='Trends').click(); pg.wait_for_selector('text=By category')
    check(pg.locator('.card', has_text='By category').locator('text=Taste / smell').count() == 1 and pg.locator('svg').count() >= 1, 'trend charts')
    pg.screenshot(path=OUT + 'complaints_trends.png')
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Complaint log').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('CMP-2026-001' in html and 'Replacement cart sent' in html and 'DEV-2026-001' in html, 'printable complaint log')
    # ---------- internal audits ----------
    pg.get_by_role('button', name='Internal Audits', exact=True).click(); pg.wait_for_selector('text=No internal audits yet')
    pg.get_by_role('button', name='+ Plan audit').click(); md = pg.locator('.md')
    field(md, 'Audit title').fill('CSQ Module 1 audit'); md.get_by_role('button', name=re.compile(r'^\+ Module 1')).click()
    rows = md.locator('div.grid', has=pg.locator('input[placeholder="Evidence seen"]'))
    n = rows.count(); check(n > 5, 'Module 1 clauses added to checklist (%d)' % n)
    for i in range(n):
        rows.nth(i).locator('select').select_option('Nonconforming' if i == 0 else 'Conforming'); rows.nth(i).locator('input').fill('Records reviewed')
    field(md, 'Audit date (done)').fill(TODAY); field(md, 'Lead auditor').fill('Lee Auditor'); field(md, 'Auditor qualification').fill('CSQ internal auditor course 2026')
    md.get_by_role('button', name='Save audit').click(); okmsg(pg, 'Planned IA-2026-001')
    a1 = T['hx_audits'][0]; first = a1['clauses'][0]['clause']
    pg.locator('.md').get_by_role('button', name='Complete audit').click(); pg.wait_for_selector('.md .msg.err >> text=own work')
    check(T['hx_audits'][0]['status'] == 'planned', 'cannot complete without independence')
    pg.locator('.md').get_by_role('button', name='Edit / checklist').click(); md = pg.locator('.md'); md.locator('label.ck', has_text='does not audit their own work').locator('input').check(); md.get_by_role('button', name='Save').click(); okmsg(pg, 'Saved.')
    pg.locator('.md').get_by_role('button', name='Complete audit').click(); pg.wait_for_selector('.md .msg.err >> text=finding for each nonconforming')
    check(pg.locator('.md').locator('text=Nonconforming clauses without a finding: ' + first).count() == 1, 'nonconforming clause without finding flagged')
    pg.locator('.md').get_by_role('button', name='+ Finding').click(); fm = pg.locator('.md')
    check(field(fm, 'Clause').input_value() == first, 'finding prefilled with the nonconforming clause')
    field(fm, 'Severity').select_option('major'); field(fm, 'Finding').fill('No documented management commitment statement'); field(fm, 'Owner').fill('GM'); fm.get_by_role('button', name='Save finding').click(); okmsg(pg, 'Finding saved')
    pg.locator('.md').get_by_role('button', name='Complete audit').click(); okmsg(pg, 'Completed IA-2026-001')
    # findings through CAPA
    md = pg.locator('.md'); md.get_by_role('button', name='Raise deviation (CAPA)').click(); dm = pg.locator('.md').last
    field(dm, 'What happened?').fill('Audit finding'); dm.get_by_role('button', name='Submit deviation').click(); okmsg(pg, 'Linked DEV-2026-002')
    pg.locator('.md').get_by_role('button', name='Close finding').click(); sm = pg.locator('.md').last; sm.locator('textarea').fill('Statement signed and posted'); sm.get_by_role('button', name='Close finding').click()
    pg.wait_for_selector('.msg.err >> text=Close deviation DEV-2026-002 first')
    check(T['hx_audit_findings'][0]['status'] == 'open', 'finding cannot close while its deviation is open')
    pg.locator('.md').last.get_by_role('button', name='Back').click()
    next(d for d in T['hx_deviations'] if d['number'] == 'DEV-2026-002')['status'] = 'closed'
    pg.locator('.md').get_by_role('button', name='Close finding').click(); sm = pg.locator('.md').last; sm.locator('textarea').fill('Statement signed and posted'); sm.get_by_role('button', name='Close finding').click(); okmsg(pg, 'Finding closed')
    md = pg.locator('.md'); md.get_by_role('button', name='Close audit').click(); pg.wait_for_selector('.md .msg.err >> text=shared')
    field(md, 'Shared with').fill('Managers meeting'); md.get_by_role('button', name='Close audit').click(); okmsg(pg, 'Closed IA-2026-001')
    check(T['hx_audits'][0]['status'] == 'closed' and T['hx_audits'][0]['shared_on'] == TODAY, 'audit closed after findings closed and results shared')
    with ctx.expect_page() as pi: pg.locator('.md').get_by_role('button', name='Print report').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('IA-2026-001' in html and 'Checklist' in html and 'DEV-2026-002' in html and 'Statement signed' in html, 'printable audit report')
    pg.locator('.md').get_by_role('button', name='Close window').click()
    pg.locator('.tabs button', has_text='Annual program').click(); pg.wait_for_selector('text=Annual audit program')
    pct = pg.locator('.card.gold', has_text='CSQ clauses audited').locator('.v').inner_text()
    check(pct != '0%' and pg.locator('text=Not audited').count() > 0 and pg.get_by_role('button', name=re.compile('^Plan an audit of the')).count() == 1, 'coverage shows audited clauses (%s) and the rest not audited' % pct)
    pg.screenshot(path=OUT + 'audit_coverage.png')
    pg.get_by_role('button', name=re.compile('^Plan an audit of the')).click(); md = pg.locator('.md')
    check(md.locator('input[placeholder="Evidence seen"]').count() > 10, 'plan an audit of the remaining clauses (prefilled)')
    md.get_by_role('button', name='Cancel').click()
    # standards evidence
    T['hx_standards'].append({'id': 'st1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}, {'level': 2, 'name': 'Level 2', 'modules': ['4A'], 'audit': ''}, {'level': 3, 'name': 'Level 3', 'modules': ['5'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 'st1', 'target_level': 3, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    def clause(c):
        rr = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(c) + '$'))).first; rr.locator('div.row').first.click(); return rr
    r1 = clause('1.5'); check(r1.locator('text=CSQ clauses audited in 12 months').count() == 1, '1.5 live internal audit evidence')
    r2 = clause('1.7'); check(r2.locator('text=2 complaints in 12 months').count() == 1, '1.7 live complaint evidence')
    r3 = clause('5.3'); check(r3.locator('text=average satisfaction 4 / 5').count() == 1, '5.3 customer feedback evidence')
    # view-only complaints user can log, not investigate
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'complaints': 'read'}
    pg.reload(); pg.get_by_role('button', name='Complaints', exact=True).click(); pg.wait_for_selector('text=+ Log complaint')
    check(pg.get_by_role('button', name='Internal Audits', exact=True).count() == 0, 'no audits without access')
    pg.locator('select').filter(has=pg.locator('option', has_text='Every status')).first.select_option('ALL'); pg.locator('.card', has_text='CMP-2026-002').click()
    check(pg.locator('.md').get_by_role('button', name='Close', exact=True).count() == 0 and field(pg.locator('.md'), 'Investigation').is_disabled(), 'View: cannot investigate or close')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
