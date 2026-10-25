import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
for t in ('hx_standards','hx_standard_clauses','hx_license_standards','hx_conformance'): T[t] = []
_pg = pguard
def pguard(tbl, r, old):
    if tbl == 'hx_standards' and any(x['id'] != r['id'] and x['code'] == r['code'] for x in T['hx_standards']): return 'duplicate key value violates unique constraint "hx_standards_code_key"'
    if tbl == 'hx_conformance':
        if not any(a['license_id'] == r['license_id'] and a['standard_id'] == r['standard_id'] and a.get('status', 'Following') != 'Withdrawn' for a in T['hx_license_standards']):
            return 'This license has not adopted that standard yet.'
        if r.get('status') == 'Not applicable' and not (r.get('evidence') or '').strip(): return 'Write why the clause does not apply (justification) before marking it Not applicable.'
        r['reviewed_at'] = now()
    return _pg(tbl, r, old)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def clause_row(pg, num):
    return pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(num) + '$'))).first
import datetime as _dt
def _ago(d): return (_dt.datetime.utcnow() - _dt.timedelta(days=d)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
T['hx_facility_log'] += [{'id':'fl%d'%i,'state_id':'st-mo','license_id':'lic-mo','log_type':'sanitation','created_at':_ago(5+i),'voided':False,'data':{}} for i in range(4)]
T['hx_facility_log'] += [{'id':'fp1','state_id':'st-mo','license_id':'lic-mo','log_type':'pest','created_at':_ago(3),'voided':False,'data':{}},
                         {'id':'fpv','state_id':'st-mo','license_id':'lic-mo','log_type':'waste','created_at':_ago(1),'voided':True,'data':{}}]
T['hx_tests'] += [{'id':'te1','state_id':'st-mo','license_id':'lic-mo','batch_number':'B1','status':'Passed','created_at':_ago(10),'result_at':_ago(8),'coa_path':'coa/a.pdf','voided':False,'tag':'X'}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('.card', has_text='Quality standard').filter(has_text='Not adopted').count() == 1, 'dashboard: not adopted yet')
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=No standard added yet')
    pg.get_by_role('button', name=re.compile('^Add CSQ Standard')).click(); pg.wait_for_selector('.msg >> text=Added')
    check(len(T['hx_standards']) == 1 and len(T['hx_standard_clauses']) == 130, 'standard + 130 clauses added (Manufacturing, Extraction, Cultivation) (%d)' % len(T['hx_standard_clauses']))
    lv = {c['clause']: c['level'] for c in T['hx_standard_clauses']}
    check(lv['1.1'] == 1 and lv['4A.5'] == 2 and lv['5.3'] == 3, 'levels derived from modules')
    check(pg.get_by_role('button', name='Add missing clauses').count() == 0, 'no missing-clauses prompt when complete')
    pg.get_by_role('button', name='Adopt for this license').click(); md = pg.locator('.md')
    check('UNANNOUNCED' not in md.inner_text(), 'level 1 note shown (announced)')
    field(md, 'Target level').select_option('1'); field(md, 'Certification body').fill('Kiwa ASI')
    md.get_by_role('button', name='Adopt standard').click(); pg.wait_for_selector('text=0% complete')
    a = T['hx_license_standards'][0]
    check(a['target_level'] == 1 and a['license_id'] == 'lic-mo' and a['state_id'] == 'st-mo' and a['cert_body'] == 'Kiwa ASI', 'adopted for lic-mo at Level 1')
    check(pg.get_by_text('84 clauses', exact=True).count() == 1, 'level 1 scope = 84 clauses (1, 2A, 3B, 3C)')
    pg.locator('select').filter(has_text='My target level only').select_option('all')
    check(pg.get_by_text('108 clauses', exact=True).count() == 1, 'all levels = 108 (no Cultivation for a manufacturing license)')
    pg.locator('select').filter(has_text='My target level only').select_option('target')
    r = clause_row(pg, '1.6'); r.locator('div.row').first.click()
    check(r.get_by_role('button', name='Record conformance').count() == 1, 'expanded clause shows Record conformance')
    r.get_by_role('button', name='Record conformance').click(); md = pg.locator('.md')
    field(md, 'Status').select_option('Not applicable'); md.get_by_role('button', name='Save').click()
    check(md.locator('.msg.err', has_text='does not apply').count() == 1, 'N/A needs justification')
    field(md, 'Status').select_option('Partial'); field(md, 'Owner').fill('Compliance Officer'); field(md, 'Due date').fill('2026-01-15')
    field(md, 'SOP / document reference').fill('SOP-QA-006 CAPA'); field(md, 'Evidence - how we meet this clause').fill('Deviations kept on paper until the CAPA module is live.')
    md.locator('input[type=file]').set_input_files({'name': 'capa-log.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 test'})
    pg.wait_for_selector('.md >> text=capa-log.pdf')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md', state='detached')
    cf = T['hx_conformance']
    check(len(cf) == 1 and cf[0]['status'] == 'Partial' and cf[0]['owner'] == 'Compliance Officer' and len(cf[0]['files']) == 1 and cf[0]['files'][0]['path'].startswith('standards/lic-mo/'), 'conformance saved with file')
    check(any(k.startswith('standards/lic-mo/') for k in STORE), 'evidence file uploaded to private storage')
    pg.wait_for_selector('.badge >> text=Overdue 2026-01-15'); r = clause_row(pg, '1.6')
    check(r.locator('.badge', has_text='Overdue 2026-01-15').count() == 1 and r.locator('.badge', has_text='Partial').count() == 1, 'row shows Partial + Overdue')
    check(r.locator('text=SOP-QA-006 CAPA').count() == 1, 'expanded row shows document and evidence')
    r.get_by_role('button', name='Update conformance').click(); md = pg.locator('.md')
    field(md, 'Status').select_option('Conforming'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md', state='detached')
    check(len(T['hx_conformance']) == 1 and T['hx_conformance'][0]['status'] == 'Conforming', 'update edits the same record')
    pg.wait_for_selector('text=1% complete'); check(pg.locator('text=1% complete').count() == 1, 'progress 1/84 = 1%')
    # status filter
    pg.locator('select').filter(has_text='Every status').select_option('Conforming')
    check(pg.locator('text=1 clause').count() >= 1 and clause_row(pg, '1.6').count() == 1 and clause_row(pg, '1.1').count() == 0, 'status filter')
    pg.locator('select').filter(has_text='Every status').select_option('ALL')
    pg.locator('input[placeholder="Search clauses, owners, evidence"]').fill('pest')
    check(clause_row(pg, '2A.5.1').count() == 1 and clause_row(pg, '1.1').count() == 0, 'search finds pest clause')
    pg.locator('input[placeholder="Search clauses, owners, evidence"]').fill('')
    # live evidence + alerts
    al = pg.locator('.card', has=pg.locator('h3', has_text='Operational alerts'))
    pg.wait_for_selector('text=Sanitation Log: last entry 5 days ago')
    check(al.locator('text=Waste Destruction Log: no entries').count() == 1, 'alert: waste log empty (voided entry not counted)')
    check(al.locator('text=Pest Control Log').count() == 0, 'no alert for current pest log')
    check(al.locator('text=not been assessed yet').count() == 1, 'alert: clauses not assessed')
    r = clause_row(pg, '2A.3'); r.locator('div.row').first.click()
    check(r.locator('text=Live records in Hendrix').count() == 1 and r.locator('.badge', has_text='No entry for 5 days').count() == 1 and r.locator('text=4 entries').count() == 1, '2A.3 shows live sanitation records + stale flag')
    r = clause_row(pg, '2A.5.1'); r.locator('div.row').first.click()
    check(r.locator('text=1 entry').count() == 1 and r.locator('.badge.bad').count() == 0, '2A.5.1 pest records current')
    r = clause_row(pg, '2A.12.9'); r.locator('div.row').first.click()
    check(r.locator('text=1 tests').count() == 1 and r.locator('text=1 COAs on file').count() == 1, '2A.12.9 shows live test counts')
    pg.get_by_role('button', name='Inspector view').click(); pg.wait_for_selector('text=Inspector view \u00b7 read only')
    check(pg.get_by_role('button', name='Update conformance').count() == 0 and pg.get_by_role('button', name='Record conformance').count() == 0, 'inspector view is read only')
    check(pg.locator('text=How we meet it:').count() == 1 and pg.locator('text=Proof in Hendrix:').count() == 0 and pg.locator('.badge', has_text='Not assessed yet').count() == 83, 'inspector view: all clauses open with answers')
    check(pg.locator('.card', has=pg.locator('h3', has_text='Operational alerts')).count() == 0, 'internal alerts hidden from inspectors')
    pg.screenshot(path=OUT + 'standards_inspector.png', full_page=False)
    pg.get_by_role('button', name='Exit inspector view').click()
    pg.screenshot(path=OUT + 'standards_page.png', full_page=False)
    # print register
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Print register').click()
    pp = pi.value; pp.wait_for_load_state()
    html = pp.content()
    check('Conformance register' in html and 'Kiwa ASI' in html and 'SOP-QA-006 CAPA' in html and 'Sanitation Log:' in html and 'MODULE 2A' in html and 'MODULE 4A' not in html, 'register prints Level 1 scope with evidence')
    pp.close()
    # proof link navigates
    r = clause_row(pg, '2A.3')
    r.get_by_role('button', name='Facility Logs').click(); pg.wait_for_timeout(400)
    check(pg.locator('h1', has_text='Facility Logs').count() >= 1 or pg.locator('text=Sanitation Log').count() >= 1, 'proof link opens Facility Logs')
    # upload standard pdf
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=1% complete')
    pg.locator('label', has_text='Upload Manufacturing PDF').locator('input').set_input_files({'name': 'CSQ_SAR_Manufacturing_v2.0.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 csq'})
    pg.wait_for_selector('text=Manufacturing (PDF)')
    check(T['hx_standards'][0]['file_name'] == 'CSQ_SAR_Manufacturing_v2.0.pdf', 'standard PDF stored')
    # dashboard card
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('text=CSQ Standard for Manufacturing + CSQ Standard for Extraction v2.0')
    check(pg.locator('.card', has_text='Quality standard').filter(has_text='83 clauses still open').count() == 1, 'dashboard shows progress')
    pg.screenshot(path=OUT + 'standards_dash.png')
    # other license not adopted
    T['hx_profiles'][0]['role'] = 'member'
    for perms, label in (({'standards': 'read'}, 'View'), ({'standards': 'editor'}, 'Edit'), ({}, 'None')):
        T['hx_profiles'][0]['perms'] = perms; pg.reload(); pg.wait_for_selector('text=Dashboard')
        nav = pg.get_by_role('button', name='Standards (CSQ)').count()
        if label == 'None':
            check(nav == 0, 'None: no Standards menu'); continue
        pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=1% complete')
        r = clause_row(pg, '1.6'); r.locator('div.row').first.click()
        rec = r.get_by_role('button', name='Update conformance').count(); adp = pg.get_by_role('button', name='Edit level and certification').count(); up = pg.locator('label', has_text='PDF').count()
        if label == 'View': check(rec == 0 and adp == 0 and up == 0, 'View: read only')
        else: check(rec == 1 and adp == 0 and up == 0, 'Edit: can update conformance, cannot change adoption or standard')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
