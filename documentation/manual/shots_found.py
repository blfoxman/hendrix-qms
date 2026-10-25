import re, datetime as dt
exec(open('/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/mock_c.py').read())
errors = []
SH = OUT + 'manual/shots/'
NOWD = dt.datetime.utcnow()
def ago(d, h=0): return (NOWD - dt.timedelta(days=d, hours=h)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

# ---------------- seed ----------------
T['hx_states'] = [{'id': 'st-mo', 'name': 'Missouri', 'agency': 'Division of Cannabis Regulation (DCR)', 'code': '19 CSR 100-1', 'tracking_system': 'METRC'},
                  {'id': 'st-mi', 'name': 'Michigan', 'agency': 'Cannabis Regulatory Agency (CRA)', 'code': 'R 420', 'tracking_system': 'METRC'}]
T['hx_licenses'] = [
    {'id': 'lic-mo', 'state_id': 'st-mo', 'name': 'Black Fox', 'license_number': 'MAN000109', 'license_type': 'Manufacturer', 'operation': 'manufacturing', 'active': True},
    {'id': 'lic-cul', 'state_id': 'st-mo', 'name': 'Black Fox Farms', 'license_number': 'CUL000412', 'license_type': 'Cultivation', 'operation': 'cultivation', 'active': True},
    {'id': 'lic-dis', 'state_id': 'st-mo', 'name': 'Black Fox Transport', 'license_number': 'TRN000088', 'license_type': 'Transportation', 'operation': 'other', 'active': False},
    {'id': 'lic-mi', 'state_id': 'st-mi', 'name': 'Key Stone', 'license_number': 'PR-000231', 'license_type': 'Processor', 'operation': 'manufacturing', 'active': True}]
W1 = '33333333-3333-3333-3333-333333333333'; W2 = '44444444-4444-4444-4444-444444444444'
M1 = '22222222-2222-2222-2222-222222222222'; M2 = '55555555-5555-5555-5555-555555555555'
T['hx_profiles'] = [
    {'id': ADMIN, 'name': 'Sam Salari', 'email': 'sam@blackfoxmfg.com', 'role': 'admin', 'approved': True, 'role_ids': [], 'perms': {}, 'license_ids': [], 'created_at': '2026-01-05'},
    {'id': M1, 'name': 'Maria Lopez', 'email': 'maria.lopez@blackfoxmfg.com', 'role': 'member', 'approved': True, 'role_ids': [], 'perms': {}, 'license_ids': ['lic-mo'], 'created_at': '2026-02-11'},
    {'id': M2, 'name': 'Derek Hall', 'email': 'derek.hall@blackfoxmfg.com', 'role': 'member', 'approved': True, 'role_ids': [], 'perms': {'logs_visitor': 'admin'}, 'license_ids': [], 'created_at': '2026-03-02'},
    {'id': W1, 'name': 'Jordan Price', 'email': 'jordan.price@blackfoxmfg.com', 'role': 'member', 'approved': False, 'role_ids': [], 'perms': {}, 'license_ids': [], 'created_at': '2026-10-20'},
    {'id': W2, 'name': 'Alicia Chen', 'email': 'alicia.chen@blackfoxmfg.com', 'role': 'member', 'approved': False, 'role_ids': [], 'perms': {}, 'license_ids': [], 'created_at': '2026-10-22'}]
T['hx_rules'] = [{'id': 'r1', 'state_id': 'st-mo', 'category': 'Security', 'citation': '', 'title': 'Camera coverage of the waste area', 'body': 'Internal rule: the waste destruction area stays in view of at least one recording camera at all times.', 'created_at': '1'},
                 {'id': 'r2', 'state_id': 'st-mi', 'category': 'Security', 'citation': 'R 420.602', 'title': 'Michigan security rule', 'body': 'x', 'created_at': '1'}]
for t in ('hx_standards', 'hx_standard_clauses', 'hx_license_standards', 'hx_conformance'): T[t] = []
T['hx_license_settings'] = []
T['hx_equipment'] = [{'id': 'q1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'EQ-001', 'name': 'Bench scale', 'category': 'Scale / balance', 'status': 'in_service'}]
T['hx_org_positions'] = []
# live records for Standards evidence and the dashboard
LT = [('sanitation', 1), ('sanitation', 2), ('sanitation', 3), ('sanitation', 4), ('temperature', 0), ('temperature', 1), ('pest', 12), ('waste', 9), ('scale_calibration', 6), ('equipment', 40)]
T['hx_facility_log'] = [{'id': 'fl%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'log_type': t, 'item': 'Line 2', 'result': 'Pass', 'created_at': ago(d, 3), 'voided': False, 'data': {}} for i, (t, d) in enumerate(LT)]
T['hx_tests'] = [{'id': 'te%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_number': b, 'status': s, 'created_at': ago(d + 3), 'result_at': ago(d), 'coa_path': 'coa/%s.pdf' % b, 'voided': False, 'tag': '1A40000000000000000%05d' % i}
                 for i, (b, s, d) in enumerate([('CART-2026-118', 'Passed', 4), ('GUM-2026-044', 'Passed', 9), ('PR-2026-071', 'Failed', 15), ('CART-2026-112', 'Passed', 21)])]
T['hx_skus'] = [{'id': 'k-c', 'state_id': 'st-mo', 'product_type': 'cartridges', 'name': '1G Distillate Cartridge', 'spec': {}, 'license_ids': [], 'active': True, 'sort': 0}]
T['hx_batches'] = [{'id': 'b%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'cartridges', 'batch_number': n, 'sku_id': 'k-c', 'sku': '1G Distillate Cartridge', 'flavor_id': None, 'flavor': f, 'status': 'Completed',
                    'data': {'date': ago(d)[:10], 'input_weight': '800'}, 'attachments': [], 'performed_by': 'Maria Lopez', 'created_at': ago(d), 'updated_at': ago(d), 'voided': False}
                   for i, (n, f, d) in enumerate([('CART-2026-118', 'Blue Dream', 6), ('CART-2026-112', 'Sour Diesel', 24)])]

_pg0 = pguard
def pguard(tbl, r, old):
    if tbl == 'hx_standards' and any(x['id'] != r['id'] and x['code'] == r['code'] for x in T['hx_standards']): return 'duplicate key value violates unique constraint "hx_standards_code_key"'
    if tbl == 'hx_conformance':
        if not any(a['license_id'] == r['license_id'] and a['standard_id'] == r['standard_id'] for a in T['hx_license_standards']): return 'This license has not adopted that standard yet.'
        if r.get('status') == 'Not applicable' and not (r.get('evidence') or '').strip(): return 'Write why the clause does not apply (justification) before marking it Not applicable.'
        r['reviewed_at'] = now()
    return _pg0(tbl, r, old)

AIQ = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; path = urllib.parse.urlparse(u).path; tbl = path.split('/')[-1]
    if tbl == 'hx_license_settings' and m == 'POST':
        r = json.loads(request.post_data); T['hx_license_settings'].append(r)
        T['hx_audit_log'].append({'id': len(T['hx_audit_log']) + 1, 'at': now(), 'table_name': tbl, 'row_id': r['license_id'], 'action': 'INSERT', 'state_id': r['state_id'], 'license_id': r['license_id'], 'user_name': 'Sam', 'reason': None, 'changed': None, 'old_data': None, 'new_data': r})
        return jr(route, [r], 201)
    if tbl == 'hx_license_settings' and m == 'PATCH':
        b = json.loads(request.post_data); r = T['hx_license_settings'][0]; r.update(b); return jr(route, [r])
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AIQ.append(b)
        if b.get('module') == 'import':
            out = {'mapping': {'name': 'Equipment', 'category': 'Type', 'location': 'Room', 'make': 'Manufacturer', 'model': 'Model #', 'serial': 'Serial No', 'cal_required': 'Calibrate?', 'cal_interval_months': 'Cal Freq (months)', 'installed_on': 'Installed', 'notes': 'Notes'},
                   'values': {'category': {'Mixer': 'Production', 'Scale': 'Scale / balance'}}}
            return jr(route, {'content': [{'type': 'text', 'text': json.dumps(out)}]})
    return _h(route, request)

def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def clause_row(pg, num): return pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(num) + '$'))).first
def shot(pg, name): pg.wait_for_timeout(350); pg.screenshot(path=SH + 'found_' + name + '.png'); print('shot', name)
def mshot(pg, name): pg.wait_for_timeout(350); pg.locator('.md').screenshot(path=SH + 'found_' + name + '.png'); print('mshot', name)
def eshot(loc, name): loc.page.wait_for_timeout(300); loc.screenshot(path=SH + 'found_' + name + '.png'); print('eshot', name)

# logo for Settings
from PIL import Image, ImageDraw, ImageFont
im = Image.new('RGB', (360, 120), (255, 255, 255)); d = ImageDraw.Draw(im)
d.polygon([(60, 10), (100, 32), (100, 88), (60, 110), (20, 88), (20, 32)], outline=(168, 132, 28), width=6)
d.text((44, 38), 'BF', fill=(30, 30, 30), font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 34))
d.text((118, 30), 'BLACK FOX', fill=(20, 20, 20), font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 40))
d.text((120, 78), 'MANUFACTURING', fill=(168, 132, 28), font=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 20))
LOGO = OUT + 'manual/bf_logo.png'; im.save(LOGO)

BROWSER = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
def mkctx(b, uid=None, lic='lic-mo'):
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5); ctx.route('**/*', handle)
    if uid:
        sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': uid}}
        ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","%s");' % (json.dumps(json.dumps(sess)), lic))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda dd: dd.accept())
    return ctx, pg

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=BROWSER)
    # ---------- 1. sign in ----------
    ctx, pg = mkctx(b)
    pg.goto(BASE); pg.wait_for_selector('text=Sign in')
    field(pg, 'Email').fill('jordan.price@blackfoxmfg.com'); field(pg, 'Password').fill('••••••••••')
    eshot(pg.locator('.auth .box'), 'signin_login')
    pg.get_by_role('link', name='Create an account').click(); pg.wait_for_selector('text=Create account')
    field(pg, 'Full name').fill('Jordan Price'); field(pg, 'Email').fill('jordan.price@blackfoxmfg.com'); field(pg, 'Password').fill('summer-shift-2026')
    eshot(pg.locator('.auth .box'), 'signin_create')
    ctx.close()
    ctx, pg = mkctx(b, W1)
    pg.goto(BASE); pg.wait_for_selector('text=Waiting for approval')
    eshot(pg.locator('.auth .box'), 'signin_pending')
    ctx.close()

    # ---------- admin ----------
    ctx, pg = mkctx(b, ADMIN)
    pg.goto(BASE); pg.wait_for_selector('.nav')

    # ---------- 6. Roles ----------
    pg.get_by_role('button', name='Roles', exact=True).click(); pg.wait_for_selector('text=No roles yet')
    pg.get_by_role('button', name='Add Black Fox roles').click(); pg.wait_for_selector('.card >> text=Production Lead')
    check(len(T['hx_roles']) == 12, '12 starter roles')
    R = {r['name']: r for r in T['hx_roles']}
    R['Production Lead']['requirements'] = 'High school diploma; 1 year cannabis production experience; cGMP and state compliance training; forklift certification'
    R['Compliance Officer']['requirements'] = "Bachelor's degree in a science field; 2 years QA or compliance; CSQ Program Overview course; HACCP certified"
    R['General Manager']['requirements'] = '5 years manufacturing management; cGMP training; CSQ Program Overview course'
    M = {p['id']: p for p in T['hx_profiles']}
    M[M1]['role_ids'] = [R['Production Lead']['id']]; M[M2]['role_ids'] = [R['Security Manager']['id'], R['Compliance Officer']['id']]
    pg.reload(); pg.get_by_role('button', name='Roles', exact=True).click(); pg.wait_for_selector('.card >> text=Production Lead')
    shot(pg, 'roles_page')
    pg.locator('.card', has_text='Sanitation').filter(has_text='Fills the sanitation, waste').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    field(md, 'Requirements (CSQ 2A.13.1)').fill('Chemical safety and SDS training; cGMP sanitation training; able to lift 50 lb')
    md.locator('tr', has_text='Chemicals and SDS').locator('select').select_option('editor')
    mshot(pg, 'roles_editor')
    md.get_by_role('button', name='Save role').click(); pg.wait_for_selector('.md', state='detached')
    check(R['Sanitation']['perms'].get('chemicals') == 'editor' or next(r for r in T['hx_roles'] if r['name'] == 'Sanitation')['perms'].get('chemicals') == 'editor', 'role saved')

    # ---------- 5. Team and Access ----------
    pg.get_by_role('button', name='Team and Access').click(); pg.wait_for_selector('text=2 waiting for approval')
    shot(pg, 'team_page')
    pg.locator('tr', has_text='Jordan Price').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.locator('label.ck', has_text='Team Member').locator('input').check()
    md.locator('label.ck', has_text='All licenses, in every state').locator('input').uncheck()
    md.locator('label.ck', has_text='Black Fox (MAN000109)').locator('input').check()
    md.locator('tr', has_text='Batch Tracker').locator('select').select_option('read')
    mshot(pg, 'team_approve')
    md.evaluate('e=>{const r=[...e.querySelectorAll("tr")].find(t=>t.innerText.includes("Batch Tracker"));r.scrollIntoView({block:"center"});}')
    mshot(pg, 'team_custom')
    md.get_by_role('button', name='Approve', exact=True).click(); pg.wait_for_selector('.md', state='detached')
    jp = M[W1]
    check(jp['approved'] and jp['license_ids'] == ['lic-mo'] and jp['perms'] == {'batch': 'read'}, 'Jordan approved')

    # ---------- 2. States and Licenses ----------
    pg.get_by_role('button', name='States and Licenses').click(); pg.wait_for_selector('td >> text=Black Fox Farms')
    shot(pg, 'locations_page')
    pg.locator('tr', has_text='MAN000109').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    mshot(pg, 'locations_license'); md.get_by_role('button', name='Cancel').click()
    pg.locator('.card.gold', has_text='Missouri').get_by_role('button', name='Edit').first.click(); md = pg.locator('.md')
    mshot(pg, 'locations_state'); md.get_by_role('button', name='Cancel').click()

    # ---------- 3. Rulebook ----------
    pg.locator('.nav button', has_text='Missouri Rulebook').click(); pg.wait_for_selector('text=Upload rules PDF')
    pg.locator('label', has_text='Upload rules PDF').locator('input[type=file]').set_input_files(OUT + 'rbpdf/mo.pdf')
    pg.wait_for_selector('text=7 rules found', timeout=30000); md = pg.locator('.md')
    md.locator('div.rbrow', has=pg.locator('span', has_text=re.compile(r'^19 CSR 100-1\.100$'))).get_by_role('button', name='Text').click()
    mshot(pg, 'rulebook_import')
    md.get_by_role('button', name='Import 7 rules').click(); pg.wait_for_selector('.msg >> text=Imported from mo.pdf', timeout=20000)
    for s in T['hx_rule_sources']: s['created_by_name'] = 'Sam Salari'
    pg.get_by_role('button', name='+ Add rule').click(); md = pg.locator('.md')
    field(md, 'Category').fill('Facility'); field(md, 'Citation (section / rule number)').fill('Company policy QA-12')
    field(md, 'Title').fill('Hairnets and beard covers in production rooms')
    field(md, 'Rule text / what it requires').fill('Everyone entering a production room wears a hairnet, and a beard cover where needed. Covers are put on in the gowning room before the airlock.')
    mshot(pg, 'rulebook_add')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md', state='detached')
    pg.wait_for_selector('text=Hairnets and beard covers')
    pg.evaluate('window.scrollTo(0,0)'); shot(pg, 'rulebook_page')

    # ---------- 4. Standards ----------
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=No standard added yet')
    pg.get_by_role('button', name=re.compile('^Add CSQ Standard')).click(); pg.wait_for_selector('.msg >> text=Added')
    check(len(T['hx_standard_clauses']) == 130, '130 clauses')
    pg.get_by_role('button', name='Adopt for this license').click(); md = pg.locator('.md')
    field(md, 'Target level').select_option('2'); field(md, 'Status').select_option('Audit scheduled'); field(md, 'Certification body').fill('Kiwa ASI')
    field(md, 'Audit date').fill('2026-12-08'); field(md, 'Notes').fill('First certification audit. Offsite document review the week before.')
    mshot(pg, 'standards_adopt')
    md.get_by_role('button', name='Adopt standard').click(); pg.wait_for_selector('text=0% complete')
    # bulk conformance so the page is realistic
    A = T['hx_license_standards'][0]; std = T['hx_standards'][0]
    insc = [c for c in T['hx_standard_clauses'] if c['level'] <= 2 and (not c['module'].startswith('3') or c['module'] in ('3B', '3C'))]
    skip = {'1.4', '2A.3', '2A.5.1'}
    for i, c in enumerate([x for x in insc if x['clause'] not in skip]):
        if i % 10 in (0, 1, 2, 3, 4, 5): st, ow, du, ev = 'Conforming', 'Compliance Officer', None, 'SOP and records in Hendrix; reviewed during the September internal audit.'
        elif i % 10 in (6, 7): st, ow, du, ev = 'Partial', 'Production Manager', '2026-11-20', 'SOP drafted; training still to be recorded for second shift.'
        elif i % 10 == 8: st, ow, du, ev = 'Not assessed', '', None, ''
        else: st, ow, du, ev = ('Not conforming', 'General Manager', '2026-10-15', 'Gap found in the September internal audit; CAPA open.') if i % 20 == 9 else ('Partial', 'QA Lead', '2026-11-30', 'In progress.')
        if st == 'Not assessed': continue
        T['hx_conformance'].append({'id': 'cf%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': std['id'], 'clause_id': c['id'], 'status': st, 'owner': ow, 'due_date': du, 'doc_ref': 'SOP-QA-%03d' % (i + 1), 'evidence': ev, 'files': [], 'reviewed_at': ago(10 + i % 20)})
    na = next(c for c in insc if c['clause'] not in skip and c['module'] == '3B' and not any(f['clause_id'] == c['id'] for f in T['hx_conformance']))
    T['hx_conformance'].append({'id': 'cfna', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': std['id'], 'clause_id': na['id'], 'status': 'Not applicable', 'owner': 'Compliance Officer', 'due_date': None, 'doc_ref': '', 'evidence': 'No hydrocarbon extraction at this license; only ethanol extraction is run.', 'files': [], 'reviewed_at': ago(12)})
    # remove 3 clauses to show "Update the standard"
    gone = [c for c in T['hx_standard_clauses'] if c['module'] == '5'][-3:]
    T['hx_standard_clauses'] = [c for c in T['hx_standard_clauses'] if c not in gone]
    pg.reload(); pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=3 clauses are missing')
    pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated: 3 clauses added')
    pg.locator('label', has_text='Upload Manufacturing PDF').locator('input').set_input_files({'name': 'CSQ_Standard_Manufacturing_v2.0.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 csq'})
    pg.wait_for_selector('text=Manufacturing (PDF)')
    pg.locator('label', has_text='Upload Extraction PDF').locator('input').set_input_files({'name': 'CSQ_Standard_Extraction_v2.0.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 csq'})
    pg.wait_for_selector('text=Extraction (PDF)')
    pg.wait_for_selector('text=Sanitation Log', timeout=8000) if pg.locator('text=Sanitation Log').count() else None
    pg.evaluate('window.scrollTo(0,0)'); shot(pg, 'standards_page')
    # record conformance on 1.4
    r = clause_row(pg, '1.4'); r.locator('div.row').first.click()
    r.get_by_role('button', name='Record conformance').click(); md = pg.locator('.md')
    field(md, 'Status').select_option('Conforming'); field(md, 'Owner').fill('Compliance Officer'); field(md, 'Due date').fill('2026-11-15')
    field(md, 'SOP / document reference').fill('SOP-QA-001 Document Control Rev 3')
    field(md, 'Evidence - how we meet this clause').fill('Master list of SOPs and forms in Hendrix SOPs; every record change is in the Audit Trail with who, when and why. Paper forms in ink only, kept 3 years in the QA office.')
    md.locator('input[type=file]').set_input_files({'name': 'document-master-list-2026-10.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 test'})
    pg.wait_for_selector('.md >> text=document-master-list-2026-10.pdf')
    mshot(pg, 'standards_conformance')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md', state='detached')
    # live evidence on 2A.3
    r = clause_row(pg, '2A.3'); r.locator('div.row').first.click(); pg.wait_for_selector('text=Live records in Hendrix')
    r.scroll_into_view_if_needed(); pg.evaluate('window.scrollBy(0,-120)')
    shot(pg, 'standards_clause')
    pg.evaluate('window.scrollTo(0,0)')
    pg.get_by_role('button', name='Inspector view').click(); pg.wait_for_selector('text=Inspector view · read only')
    pg.evaluate('window.scrollTo(0,0)'); shot(pg, 'standards_inspector')
    pg.get_by_role('button', name='Exit inspector view').click()

    # ---------- 8. Settings ----------
    pg.get_by_role('button', name='Settings', exact=True).click(); pg.wait_for_selector('text=Business details on printouts')
    field(pg, 'Legal name').fill('Black Fox Manufacturing LLC'); field(pg, 'Doing business as').fill('Black Fox')
    field(pg, 'Address').fill('4120 Industrial Park Dr\nSt. Louis, MO 63110'); field(pg, 'Phone').fill('314-555-0142'); field(pg, 'Email').fill('compliance@blackfoxmfg.com')
    field(pg, 'Footer on printouts').fill('Controlled copy - printed from Hendrix QMS')
    pg.locator('input[type=file]').set_input_files(LOGO); pg.wait_for_selector('img[alt=logo]')
    shot(pg, 'settings_general')
    pg.get_by_role('button', name='Facility logs', exact=True).click(); pg.locator('.row', has_text='Sanitation Log').last.locator('input').fill('1')
    pg.locator('.row', has_text='Pest Control Log').last.locator('input').fill('30')
    shot(pg, 'settings_logs')
    pg.get_by_role('button', name='Time clock', exact=True).click(); field(pg, '2nd break (min)').fill('30')
    pg.get_by_role('button', name='Save settings').click(); pg.wait_for_selector('.msg >> text=Settings saved for Black Fox.')
    pg.get_by_role('button', name='Everything else').click(); pg.wait_for_selector('.card b >> text=Products')
    shot(pg, 'settings_more')

    # ---------- 9. Import ----------
    pg.get_by_role('button', name='Import (Excel / Sheets)').click(); pg.wait_for_selector('text=1. What are you importing?')
    pg.locator('button.card', has_text='Equipment').click(); pg.locator('input[type=file]').set_input_files(OUT + 'import_eq.xlsx'); pg.wait_for_selector('text=import_eq.xlsx')
    pg.get_by_role('button', name='Match with AI').click(); pg.wait_for_selector('text=Columns matched by the AI')
    shot(pg, 'import_start')
    pg.evaluate("window.scrollTo(0,0)"); pg.evaluate("(()=>{const e=[...document.querySelectorAll('.k')].find(x=>x.textContent.startsWith('4. Preview'));window.scrollTo(0,e.getBoundingClientRect().top+window.scrollY-110);})()")
    shot(pg, 'import_preview')
    pg.get_by_role('button', name='Import 2 rows').click(); pg.wait_for_selector('text=Imported 2.')

    # ---------- 7. Audit Trail ----------
    T['hx_audit_log'] += [
        {'id': 900, 'at': ago(2, 5), 'table_name': 'hx_batches', 'row_id': 'b0', 'action': 'UPDATE', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Sam Salari', 'reason': 'Scale printout showed 812 g; typo on first entry',
         'changed': ['data'], 'old_data': {'batch_number': 'CART-2026-118', 'batch_type': 'cartridges', 'data': {'input_weight': '800'}}, 'new_data': {'batch_number': 'CART-2026-118', 'batch_type': 'cartridges', 'data': {'input_weight': '812'}}},
        {'id': 901, 'at': ago(3, 2), 'table_name': 'hx_facility_log', 'row_id': 'fl7', 'action': 'VOID', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Derek Hall', 'reason': 'Entered on the wrong license',
         'changed': ['void_reason', 'voided'], 'old_data': {'log_type': 'waste', 'item': 'Trim and stems'}, 'new_data': {'log_type': 'waste', 'item': 'Trim and stems', 'voided': True}},
        {'id': 902, 'at': ago(4, 1), 'table_name': 'hx_tests', 'row_id': 'te2', 'action': 'UPDATE', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Derek Hall', 'reason': 'Lab issued an amended COA',
         'changed': ['status'], 'old_data': {'batch_number': 'PR-2026-071', 'status': 'Passed'}, 'new_data': {'batch_number': 'PR-2026-071', 'status': 'Failed'}}]
    for a in T['hx_audit_log']:
        if a['user_name'] == 'Sam': a['user_name'] = 'Sam Salari'
    T['hx_audit_log'] = [a for a in T['hx_audit_log'] if a['table_name'] not in ('hx_conformance', 'hx_license_standards', 'hx_license_settings', 'hx_standards', 'hx_standard_clauses', 'hx_rule_sources')]
    T['hx_audit_log'].sort(key=lambda a: a['at'])
    for i, a in enumerate(T['hx_audit_log']): a['id'] = i + 1
    pg.get_by_role('button', name='Audit Trail').click(); pg.wait_for_selector('h1 >> text=Trail'); pg.wait_for_selector('td >> text=Entered on the wrong license'); pg.evaluate('window.scrollTo(0,0)')
    shot(pg, 'audit_page')
    pg.locator('select').nth(2).select_option('hx_batches'); pg.wait_for_selector('td >> text=typo on first entry'); pg.wait_for_timeout(300)
    shot(pg, 'audit_filtered')

    # ---------- 1. Dashboard ----------
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('text=Quality standard'); pg.wait_for_timeout(1200)
    shot(pg, 'dashboard')
    ctx.close()

    # ---------- View-only member: Settings and Standards read only ----------
    ctx, pg = mkctx(b, M1)
    pg.goto(BASE); pg.wait_for_selector('.nav'); pg.wait_for_timeout(800)
    shot(pg, 'member_dashboard')
    ctx.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
