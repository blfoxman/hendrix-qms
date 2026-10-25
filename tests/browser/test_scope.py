import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
for t in ('hx_standards', 'hx_standard_clauses', 'hx_license_standards', 'hx_conformance'): T[t] = []
T['hx_licenses'].append({'id': 'lic-cul', 'state_id': 'st-mo', 'name': 'Green Acres', 'license_number': 'CUL000777', 'license_type': 'Cultivation', 'active': True})
T['hx_roles'] += [{'id': 'gm', 'name': 'General Manager', 'description': '', 'perms': {}, 'sort': 0}, {'id': 'ex', 'name': 'Extraction Manager', 'description': '', 'perms': {}, 'sort': 1}]
# an install made before this step: old name, only some clauses
T['hx_standards'].append({'id': 'std1', 'code': 'CSQ-MFG', 'name': 'CSQ Standard for Manufacturing', 'publisher': 'CSQ', 'version': '2.0', 'issued': 'October 2025', 'scope': 'old', 'levels': [], 'modules': {'1': 'x'}, 'audit_notes': [], 'file_path': '', 'file_name': '', 'docs': []})
T['hx_standard_clauses'].append({'id': 'old1', 'standard_id': 'std1', 'clause': '1.1', 'module': '1', 'title': 'x', 'summary': 'x', 'level': 1, 'hx_pages': [], 'hx_support': '', 'hx_planned': [], 'applies_to': '', 'sort': 0})
ROSTER = [{'id': ADMIN, 'name': 'Sam', 'role_ids': ['gm'], 'license_ids': [], 'is_admin': True}]
_h = handle
def handle(route, request):
    u = request.url
    if '/rest/v1/rpc/hx_training_roster' in u: return route.fulfill(status=200, content_type='application/json', body=json.dumps(ROSTER))
    if '/rest/v1/rpc/hx_training_sop_acks' in u: return route.fulfill(status=200, content_type='application/json', body='[]')
    if '/rest/v1/hx_training_courses' in u and request.method == 'POST':
        rows = json.loads(request.post_data); rows = rows if isinstance(rows, list) else [rows]
        for r in rows: r.setdefault('license_ids', [r['license_id']]); r.setdefault('active', True); r.setdefault('role_ids', []); r.setdefault('sop_id', None); T['hx_training_courses'].append(r)
        return route.fulfill(status=201, content_type='application/json', body=json.dumps(rows))
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def clause_row(pg, num): return pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(num) + '$')))
def mod_opts(pg): return pg.locator('select').filter(has_text='All modules').locator('option').all_inner_texts()
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    # existing install is upgraded
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=129 clauses are missing')
    pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated: 129 clauses added')
    st = T['hx_standards'][0]; mods = {c['module'] for c in T['hx_standard_clauses']}
    check(st['name'] == 'CSQ Standards (Manufacturing, Extraction, Cultivation)' and '3A' in st['modules'] and '3B' in st['modules'] and {'3A', '3B', '3C'} <= mods and len(T['hx_standard_clauses']) == 130, 'existing library updated: new name, Modules 3A and 3B added (130 clauses)')
    # manufacturing license
    check(pg.locator('label', has_text='Upload Manufacturing PDF').count() == 1 and pg.locator('label', has_text='Upload Extraction PDF').count() == 1 and pg.locator('label', has_text='Upload Cultivation PDF').count() == 0, 'MAN license: Manufacturing + Extraction PDFs, no Cultivation')
    pg.get_by_role('button', name='Adopt for this license').click(); md = pg.locator('.md')
    check(md.locator('text=License operation: Manufacturing').count() == 1 and md.locator('label.ck', has_text='CSQ Standard for Manufacturing').count() == 1 and md.locator('label.ck', has_text='CSQ Standard for Extraction').count() == 1 and md.locator('label.ck', has_text='Cultivation').count() == 0, 'adopt: Manufacturing and Extraction offered, Cultivation not')
    md.get_by_role('button', name='Adopt standard').click(); pg.wait_for_selector('text=0% complete')
    a = T['hx_license_standards'][0]; check(sorted(a['scopes']) == ['3B', '3C'], 'MAN adoption scopes 3C + 3B')
    o = mod_opts(pg); check(any(x.startswith('Module 3B') for x in o) and any(x.startswith('Module 3C') for x in o) and not any(x.startswith('Module 3A') for x in o), 'module list: 3B and 3C, no 3A')
    check(pg.get_by_text('84 clauses', exact=True).count() == 1 and clause_row(pg, '3B.1.5').count() == 1 and clause_row(pg, '3A.1.1').count() == 0, 'Level 1: 84 clauses incl. extraction, no cultivation')
    check(pg.locator('text=Manufacturing (processing, extraction, infusion) · CSQ Standard for Manufacturing + CSQ Standard for Extraction').count() == 1, 'license card names both standards')
    pg.get_by_role('button', name='Inspector view').click(); pg.wait_for_selector('text=Inspector view · read only')
    check(pg.locator('text=Follows CSQ Standard for Manufacturing + CSQ Standard for Extraction v2.0').count() == 1, 'inspector view: follows Manufacturing + Extraction')
    pg.get_by_role('button', name='Exit inspector view').click()
    # cultivation license
    pg.locator('select').nth(1).select_option('lic-cul'); pg.wait_for_timeout(500)
    if pg.locator('text=Adopt for this license').count() == 0: pg.get_by_role('button', name='Standards (CSQ)').click()
    pg.wait_for_selector('text=Adopt for this license')
    check(pg.locator('label', has_text='Upload Cultivation PDF').count() == 1 and pg.locator('label', has_text='Upload Extraction PDF').count() == 0, 'CUL license: Cultivation PDF only')
    pg.get_by_role('button', name='Adopt for this license').click(); md = pg.locator('.md')
    cb = md.locator('label.ck', has_text='CSQ Standard for Cultivation').locator('input')
    check(cb.is_checked() and cb.is_disabled() and md.locator('label.ck', has_text='Extraction').count() == 0 and md.locator('label.ck', has_text='CSQ Standard for Manufacturing').count() == 0, 'adopt: Cultivation only (fixed) for a CUL license')
    md.get_by_role('button', name='Adopt standard').click(); pg.wait_for_selector('text=0% complete')
    a2 = next(x for x in T['hx_license_standards'] if x['license_id'] == 'lic-cul'); check(a2['scopes'] == ['3A'], 'CUL adoption scopes 3A')
    o = mod_opts(pg); check(any(x.startswith('Module 3A') for x in o) and not any(x.startswith('Module 3B') or x.startswith('Module 3C') for x in o), 'module list: 3A only')
    check(pg.get_by_text('73 clauses', exact=True).count() == 1 and clause_row(pg, '3A.1.7').count() == 1 and clause_row(pg, '3C.1.1').count() == 0, 'Level 1: 73 clauses (1, 2A, 3A)')
    pg.locator('select').filter(has_text='My target level only').select_option('all')
    check(clause_row(pg, '3B.1.1').count() == 0 and clause_row(pg, '3C.2.6').count() == 0, 'all levels still hide Manufacturing / Extraction for a CUL license')
    r = clause_row(pg, '2A.13.2').first; r.locator('div.row').first.click()
    check(r.locator('text=cGACP').count() >= 1, '2A.13.2 mentions cGACP')
    pg.get_by_role('button', name='Inspector view').click(); pg.wait_for_selector('text=Follows CSQ Standard for Cultivation v2.0')
    check(True, 'inspector view: follows Cultivation')
    pg.get_by_role('button', name='Exit inspector view').click()
    pg.screenshot(path=OUT + 'standards_cul.png')
    # internal audits for CUL
    pg.get_by_role('button', name='Internal Audits', exact=True).click(); pg.wait_for_selector('text=+ Plan audit')
    pg.get_by_role('button', name='+ Plan audit').click(); md = pg.locator('.md')
    check(md.get_by_role('button', name=re.compile(r'^\+ Module 3A')).count() == 1 and md.get_by_role('button', name=re.compile(r'^\+ Module 3[BC]')).count() == 0, 'audit checklist: Cultivation module only')
    md.get_by_role('button', name='Cancel').click()
    pg.locator('.tabs button', has_text='Annual program').click(); pg.wait_for_selector('text=Annual audit program')
    check(pg.locator('h3', has_text='CSQ Standard for Cultivation').count() == 1 and pg.locator('text=Module 3A · Cultivation').count() >= 1, 'coverage uses the Cultivation scope')
    # training for CUL
    pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses')
    cul = [c for c in T['hx_training_courses'] if c['license_id'] == 'lic-cul']
    check(any(c['topic'] == 'cGACP' and c['required_mode'] == 'everyone' for c in cul) and not any(c['topic'] == 'Extraction' for c in cul), 'CUL license: cGACP course for everyone, no Extraction course')
    # locations
    pg.get_by_role('button', name='States and Licenses').click(); pg.wait_for_selector('td >> text=Green Acres')
    check(pg.locator('tr', has_text='Green Acres').locator('td', has_text='Cultivation').count() >= 1 and pg.locator('tr', has_text='MAN000109').locator('td', has_text='Manufacturing + Extraction').count() == 1, 'licenses table shows the CSQ standards per license')
    pg.locator('tr', has_text='Green Acres').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    check('Automatic: Cultivation (CUL)' in field(md, 'Operation').locator('option').first.inner_text() and md.locator('text=CSQ Standard for Cultivation (Module 3A).').count() == 1, 'license form: operation guessed from CUL number')
    md.get_by_role('button', name='Cancel').click()
    # suppliers categories
    pg.get_by_role('button', name='Suppliers', exact=True).click(); pg.get_by_role('button', name='+ Add supplier').click()
    check(field(pg.locator('.md'), 'Category / type').locator('option', has_text='Nutrients / Fertilizers').count() == 1, 'cultivation supplier categories')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
