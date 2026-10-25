import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
D = OUT + 'rbpdf/'
AIREQ = []
_h = handle
def handle(route, request):
    u = request.url
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AIREQ.append(b)
        txt = b['messages'][0]['content']
        if b.get('module') != 'rulebook': return _h(route, request)
        if 'Find the line where each separate rule' in txt:
            out = []
            for ln in txt.split('\n'):
                m = re.match(r'^(\d+)\|(Hand washing|Visitors|Product labels)$', ln)
                if m: out.append({'line': int(m.group(1)), 'citation': '', 'title': m.group(2), 'category': 'Facility' if m.group(2) == 'Hand washing' else 'Security' if m.group(2) == 'Visitors' else 'Labeling'})
            return route.fulfill(status=200, content_type='application/json', body=json.dumps({'content': [{'type': 'text', 'text': json.dumps({'rules': out})}]}))
        if 'Sort each cannabis regulation' in txt:
            c = [[int(ln.split('|')[0]), 'Training'] for ln in txt.split('\n') if re.match(r'^\d+\|', ln)]
            return route.fulfill(status=200, content_type='application/json', body=json.dumps({'content': [{'type': 'text', 'text': json.dumps({'c': c})}]}))
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def rrow(md, cit): return md.locator('div.rbrow', has=md.page.locator('span', has_text=re.compile('^' + re.escape(cit) + '$')))
def upload(pg, f):
    pg.locator('label', has_text='Upload rules PDF').locator('input[type=file]').set_input_files(D + f)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Missouri Rulebook').click(); pg.wait_for_selector('text=Upload rules PDF')
    n0 = len(T['hx_rules'])
    # scanned PDF
    upload(pg, 'scan.pdf'); pg.wait_for_selector('text=This PDF has no readable text')
    check(True, 'scanned PDF: clear message'); pg.locator('.md').get_by_role('button', name='Close').click()
    # Missouri CSR, two columns
    upload(pg, 'mo.pdf'); pg.wait_for_selector('text=7 rules found', timeout=30000)
    md = pg.locator('.md')
    check(md.locator('text=Missouri Code of State Regulations (CSR)').count() == 1 and md.get_by_role('button', name='New 7').count() == 1, 'Missouri PDF: 7 rules, CSR format, all new')
    cats = {c: rrow(md, c).locator('select').input_value() for c in ['19 CSR 100-1.010', '19 CSR 100-1.020', '19 CSR 100-1.040', '19 CSR 100-1.090', '19 CSR 100-1.100', '19 CSR 100-1.120', '19 CSR 100-1.140']}
    print(cats)
    check(cats == {'19 CSR 100-1.010': 'General', '19 CSR 100-1.020': 'Licensing', '19 CSR 100-1.040': 'Licensing', '19 CSR 100-1.090': 'Inventory / Tracking', '19 CSR 100-1.100': 'Security', '19 CSR 100-1.120': 'Packaging', '19 CSR 100-1.140': 'Testing'}, 'categories sorted automatically')
    check(rrow(md, '19 CSR 100-1.040').locator('input:not([type=checkbox])').input_value() == 'Denials, Revocations, Suspensions, and Penalties', 'wrapped title joined')
    rrow(md, '19 CSR 100-1.100').get_by_role('button', name='Text').click()
    t = rrow(md, '19 CSR 100-1.100').inner_text()
    check('PURPOSE: This rule establishes facility security standards.' in t and '(2) Alarm system.' in t and 'AUTHORITY:' in t and 'CODE OF STATE REGULATIONS' not in t and 'Rules of' not in t, 'rule text in order, headers / footers removed')
    # split into sections
    md.locator('label.ck', has_text='Split each rule into its numbered sections').locator('input').check()
    check(rrow(md, '19 CSR 100-1.100(1)').count() == 1 and rrow(md, '19 CSR 100-1.100(1)').locator('input:not([type=checkbox])').input_value() == 'Security Requirements — Video surveillance' and rrow(md, '19 CSR 100-1.020(3)').locator('select').input_value() == 'Licensing', 'split into sections with headings and categories')
    md.locator('label.ck', has_text='Split each rule into its numbered sections').locator('input').uncheck()
    rrow(md, '19 CSR 100-1.040').locator('select').select_option('Other')
    md.get_by_role('button', name='Import 7 rules').click()
    pg.wait_for_selector('.msg >> text=Imported from mo.pdf: 7 new, 0 updated.', timeout=20000)
    new = [r for r in T['hx_rules'] if r.get('source_id')]
    src = T['hx_rule_sources']
    check(len(T['hx_rules']) == n0 + 7 and len(src) == 1 and src[0]['added'] == 7 and src[0]['rules_found'] == 7 and src[0]['file_path'] in STORE and all(r['source_id'] == src[0]['id'] for r in new), 'saved: 7 rules, source PDF kept and listed')
    check(next(r for r in new if r['citation'] == '19 CSR 100-1.040')['category'] == 'Other' and sorted(r['sort'] for r in new) == [10, 20, 30, 40, 50, 60, 70], 'category change kept; official order saved')
    check(pg.locator('text=Source PDFs').count() == 1 and pg.locator('text=mo.pdf').count() >= 1 and pg.get_by_role('button', name='Open PDF').count() == 1, 'source PDFs listed with Open PDF')
    sec = pg.locator('.card.gold', has=pg.locator('.k', has_text=re.compile('^Security$')))
    titles = sec.locator('div[style*="font-weight: 700"]').all_inner_texts()
    check(titles[:2] == ['Security Requirements', 'Camera coverage'], 'imported rules in official order, hand-typed rules after')
    gen = pg.locator('.card.gold', has=pg.locator('.k', has_text=re.compile('^General$')))
    check(gen.get_by_role('button', name=re.compile(r'^Show all \(')).count() == 1, 'long rule text collapsed')
    gen.get_by_role('button', name=re.compile(r'^Show all \(')).click()
    check(gen.locator('text=Seed-to-sale tracking system means').count() == 1 and gen.get_by_role('button', name='Show less').count() == 1, 'Show all opens the full text')
    pg.screenshot(path=OUT + 'rulebook_import.png')
    # newer PDF: 1.100 changed, 1.040 repealed
    upload(pg, 'mo2.pdf'); pg.wait_for_selector('text=6 rules found', timeout=30000); md = pg.locator('.md')
    check(md.get_by_role('button', name='New 0').count() == 1 and md.get_by_role('button', name='Changed 1').count() == 1 and md.get_by_role('button', name='Same 5').count() == 1, 'newer PDF: 1 changed, 5 the same')
    check(rrow(md, '19 CSR 100-1.100').locator('.badge').inner_text().lower() == 'changed' and rrow(md, '19 CSR 100-1.100').locator('input[type=checkbox]').is_checked() and not rrow(md, '19 CSR 100-1.010').locator('input[type=checkbox]').is_checked(), 'changed rule ticked, same rules not')
    md.get_by_role('button', name='Sort categories with AI').click(); pg.wait_for_function("document.querySelectorAll('.md div.rbrow select')[0].value==='Training'")
    check(AIREQ[-1]['module'] == 'rulebook', 'AI sort uses the rulebook module')
    rrow(md, '19 CSR 100-1.100').locator('select').select_option('Security')
    dl = md.locator('label.ck', has_text='Delete the 1 rule from an earlier PDF')
    check(dl.count() == 1, 'offers to delete the repealed rule')
    dl.locator('input').check()
    md.get_by_role('button', name='Import 1 rule').click()
    pg.wait_for_selector('.msg >> text=Imported from mo2.pdf: 0 new, 1 updated, 1 removed.', timeout=20000)
    r100 = next(r for r in T['hx_rules'] if r['citation'] == '19 CSR 100-1.100')
    check('ninety days' in r100['body'] and r100['category'] == 'Security' and not any(r['citation'] == '19 CSR 100-1.040' for r in T['hx_rules']) and any(r['id'] == 'r1' for r in T['hx_rules']), 'rule updated, repealed rule deleted, hand-typed rule kept')
    check(len(T['hx_rule_sources']) == 2 and pg.locator('text=latest').count() == 1, 'second PDF listed as latest')
    # Michigan in the Michigan rulebook
    pg.locator('select').first.select_option('st-mi'); pg.wait_for_timeout(600)
    if pg.locator('text=Upload rules PDF').count() == 0: pg.get_by_role('button', name='Michigan Rulebook').click()
    pg.wait_for_selector('h1 >> text=Michigan')
    upload(pg, 'mi.pdf'); pg.wait_for_selector('text=5 rules found', timeout=30000); md = pg.locator('.md')
    check(md.locator('text=Michigan Administrative Code (R numbers)').count() == 1 and rrow(md, 'R 420.305').locator('select').input_value() == 'Testing' and rrow(md, 'R 420.602').locator('select').input_value() == 'Security', 'Michigan PDF: R numbers, categories')
    md.get_by_role('button', name='Import 5 rules').click(); pg.wait_for_selector('.msg >> text=Imported from mi.pdf: 5 new', timeout=20000)
    check(len([r for r in T['hx_rules'] if r['state_id'] == 'st-mi']) == 5 + len([r for r in T['hx_rules'] if r['state_id'] == 'st-mi' and not r.get('source_id')]), 'Michigan rules saved to Michigan only')
    # PDF without rule numbers -> AI finds the starts
    upload(pg, 'plain.pdf'); pg.wait_for_selector('text=3 rules found', timeout=30000); md = pg.locator('.md')
    check(md.locator('text=Found by AI (no standard rule numbers)').count() == 1 and md.locator('div.rbrow input[value="Visitors"]').count() == 1 and md.locator('div.rbrow').nth(1).locator('select').input_value() == 'Security', 'no rule numbers: AI finds each rule, text kept')
    md.locator('div.rbrow').nth(1).get_by_role('button', name='Text').click()
    check('All visitors sign in at reception' in md.locator('div.rbrow').nth(1).inner_text(), 'AI split keeps the PDF text word for word')
    md.get_by_role('button', name='Cancel').click()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
