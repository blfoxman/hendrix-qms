import re, subprocess, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
ROSTER = [{'id': ADMIN, 'name': 'Sam', 'role_ids': ['r2'], 'license_ids': [], 'is_admin': True}, {'id': 'u-lee', 'name': 'Lee Worker', 'role_ids': ['r1'], 'license_ids': ['lic-mo'], 'is_admin': False}]
T['hx_roles'] += [{'id': 'r1', 'name': 'Sanitation', 'description': 'Cleans', 'perms': {}, 'sort': 0}, {'id': 'r2', 'name': 'Production Manager', 'description': 'Runs production', 'perms': {}, 'sort': 1}]
T['hx_sops'] += [{'id': 's1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Cart Filling', 'sop_number': 'SOP-PRD-001', 'version': '1.0', 'status': 'published', 'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'steps': [], 'folder': 'Production'}]
ACKS = [{'sop_id': 's1', 'version': '1.0', 'user_id': 'u-lee', 'at': '2026-10-01T10:00:00Z'}]
COURSES = {}
_h = handle
def handle(route, request):
    u = request.url
    if '/rest/v1/rpc/hx_training_roster' in u: return route.fulfill(status=200, content_type='application/json', body=json.dumps(ROSTER if T['hx_profiles'][0]['role'] == 'admin' else [r for r in ROSTER if r['id'] == ADMIN]))
    if '/rest/v1/rpc/hx_training_sop_acks' in u: return route.fulfill(status=200, content_type='application/json', body=json.dumps(ACKS))
    if '/rest/v1/hx_training_records' in u and request.method == 'POST':
        rows = json.loads(request.post_data); rows = rows if isinstance(rows, list) else [rows]
        for r in rows:
            c = next(x for x in T['hx_training_courses'] if x['id'] == r['course_id'])
            if c['assessment_required'] and r['assessment'] == 'Not required': return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'This course requires an assessment'}))
            d = dt.date.fromisoformat(r['completed_on']); m = c['refresher_months']
            exp = None
            if m: mm = d.month - 1 + m; exp = dt.date(d.year + mm // 12, mm % 12 + 1, min(d.day, 28)).isoformat()
            r.update({'expires_on': exp, 'person_name': next(p['name'] for p in ROSTER if p['id'] == r['user_id']), 'voided': False, 'recorded_by': 'Sam', 'created_at': now()})
            T['hx_training_records'].append(r)
        return route.fulfill(status=201, content_type='application/json', body=json.dumps(rows))
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
def row(pg, name): return pg.locator('tr', has=pg.locator('td', has_text=name)).first
def cellcolors(pg, name): return row(pg, name).locator('.trcell').evaluate_all('els=>els.map(e=>getComputedStyle(e).backgroundColor)')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Open training')
    check(pg.locator('.card', has_text='Open training').locator('text=No courses yet').count() == 1, 'dashboard: training not set up')
    pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses')
    TC = {c['name'][:4]: c for c in T['hx_training_courses']}
    check(any(c['name'] == 'Missouri regulatory compliance (state rules)' and 'Only for Missouri licenses' in c['description'] for c in T['hx_training_courses']), 'law course is Missouri-specific')
    check(len(T['hx_training_courses']) == 9 and any(c['topic'] == 'Extraction' for c in T['hx_training_courses']) and not any(c['topic'] == 'cGACP' for c in T['hx_training_courses']) and sum(1 for c in T['hx_training_courses'] if c['required_mode'] == 'everyone') == 5, 'opening Training creates the 9 CSQ courses for a manufacturing license (incl. Extraction, no cGACP); 5 for everyone')
    check(TC['CSQ ']['required_mode'] == 'roles' and TC['CSQ ']['role_ids'] == ['r2'] and TC['HACC']['role_ids'] == ['r2'] and TC['HACC']['min_people'] == 2 and sorted(TC['Chem']['role_ids']) == ['r1', 'r2'], 'CSQ overview + HACCP = manager training; chemical safety = managers + sanitation')
    pg.locator('.tabs button', has_text='Courses').click(); pg.wait_for_selector('text=at least 2 certified')
    check(pg.locator('.card', has_text='HACCP certification').locator('text=Chosen roles: Production Manager').count() == 1, 'courses list shows manager roles and certified count')
    pg.locator('.card', has_text='Chemical safety and SDS').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    field(md, 'Who must take it').select_option('roles'); md.locator('label.ck', has_text='Sanitation').locator('input').check(); md.get_by_role('button', name='Save course').click(); pg.wait_for_selector('.msg >> text=Saved')
    chem = next(c for c in T['hx_training_courses'] if c['name'].startswith('Chemical'))
    check(chem['required_mode'] == 'roles' and 'r1' in chem['role_ids'], 'chemical safety required for the Sanitation role')
    pg.get_by_role('button', name='+ Course').click(); md = pg.locator('.md')
    field(md, 'Course name').fill('Cart filling (read and sign)'); field(md, 'Met by signing an SOP').select_option('s1'); field(md, 'Refresher every').fill('0')
    md.get_by_role('button', name='Save course').click(); pg.wait_for_selector('.msg >> text=Saved')
    check(T['hx_training_courses'][-1]['sop_id'] == 's1', 'course met by signing SOP')
    # matrix
    pg.locator('.tabs button', has_text='Training matrix').click(); pg.wait_for_selector('td >> text=Lee Worker')
    lee = cellcolors(pg, 'Lee Worker')
    check(lee.count('rgb(95, 191, 138)') == 1, 'Lee: SOP signature counts as the read-and-sign course (1 green)')
    check(row(pg, 'Lee Worker').locator('td', has_text=re.compile(r'^\d+%$')).inner_text() == '14%', 'Lee: 1 of 7 required = 14%')
    # record training (assessment required)
    pg.get_by_role('button', name='+ Record training').click(); md = pg.locator('.md')
    field(md, 'Course').select_option(label='Current Good Manufacturing Practices (cGMP)'); md.get_by_role('button', name='Select all').click(); field(md, 'Trainer').fill('QA Lead Ana')
    field(md, 'Trainer qualification').fill('PCQI, 8 yrs QA'); md.get_by_role('button', name=re.compile('^Save')).click(); pg.wait_for_timeout(200)
    check(md.locator('.msg.err', has_text='assessment').count() == 1, 'assessment required enforced')
    field(md, 'Assessment').select_option('Passed'); field(md, 'Score').fill('19/20')
    md.locator('input[type=file]').set_input_files({'name': 'signin.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4'}); pg.wait_for_selector('.md >> text=signin.pdf')
    md.get_by_role('button', name='Save 2 records').click(); pg.wait_for_selector('.msg >> text=Recorded 2')
    r = T['hx_training_records']
    check(len(r) == 2 and all(x['trainer_qualification'] == 'PCQI, 8 yrs QA' and x['assessment'] == 'Passed' and x['expires_on'] and len(x['files']) == 1 for x in r), 'two records with trainer, qualification, assessment, expiry, certificate')
    # expired + failed + CSQ overview
    reg = next(c for c in T['hx_training_courses'] if c['name'].startswith('Missouri regulatory compliance')); csq = next(c for c in T['hx_training_courses'] if c['name'].startswith('CSQ'))
    T['hx_training_records'] += [{'id': 'old', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'course_id': reg['id'], 'user_id': 'u-lee', 'person_name': 'Lee Worker', 'completed_on': '2024-05-01', 'expires_on': '2025-05-01', 'trainer_name': 'X', 'assessment': 'Not required', 'voided': False, 'files': [], 'method': 'Classroom', 'language': 'English'},
                                 {'id': 'ov', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'course_id': csq['id'], 'user_id': ADMIN, 'person_name': 'Sam', 'completed_on': '2026-02-01', 'expires_on': None, 'trainer_name': 'CSQ', 'assessment': 'Not required', 'voided': False, 'files': [], 'method': 'Online course', 'language': 'English'}]
    pg.reload(); pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('td >> text=Lee Worker')
    check(pg.locator('.card', has_text='CSQ Certification Program Overview').locator('text=1 / 1').count() == 1, 'CSQ overview: 1 of 1 (Sam)')
    check(pg.locator('.card', has_text='HACCP certification').locator('text=0 / 2').count() == 1, 'HACCP: 0 of 2 flagged')
    check(row(pg, 'Lee Worker').locator('td', has_text=re.compile(r'^\d+%$')).inner_text() == '29%' and row(pg, 'Lee Worker').locator('td[title^="expired"]').count() == 1, 'Lee: cGMP now current (29%), regulatory expired')
    pg.screenshot(path=OUT + 'training_matrix.png')
    # print + person PDF
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Print matrix').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('Training matrix' in html and 'Lee Worker' in html and 'EXPIRED' in html, 'printable matrix')
    with pg.expect_download() as di: row(pg, 'Lee Worker').get_by_role('button', name='PDF').click()
    di.value.save_as(OUT + 'training_lee.pdf'); txt = subprocess.run(['pdftotext', OUT + 'training_lee.pdf', '-'], capture_output=True, text=True).stdout
    check('Employee Training Record' in txt and 'Lee Worker' in txt and 'EXPIRED' in txt and 'Cart Filling' in txt and 'signed 2026-10-01' in txt, 'employee training PDF with courses and SOP signatures')
    # SOP signatures tab
    pg.locator('.tabs button', has_text='SOP signatures').click(); pg.wait_for_selector('td >> text=Lee Worker')
    check(row(pg, 'Lee Worker').locator('td', has_text='100%').count() == 1 and row(pg, 'Sam').locator('td', has_text='0%').count() == 1, 'SOP signature matrix (BF parity)')
    # records + void
    pg.locator('.tabs button', has_text='Records').click(); pg.wait_for_selector('td >> text=QA Lead Ana')
    row(pg, 'Online course').get_by_role('button', name='Void').click(); md = pg.locator('.md'); md.locator('textarea').fill('Entered for wrong person'); md.get_by_role('button', name=re.compile('Void')).last.click(); pg.wait_for_selector('.msg >> text=Voided')
    check(next(x for x in T['hx_training_records'] if x['id'] == 'ov')['voided'] is True, 'record voided with reason')
    # standards evidence
    T['hx_standards'].append({'id': 'st1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 'st1', 'target_level': 1, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    rr = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile(r'^2A\.13\.2$'))).first; rr.locator('div.row').first.click()
    check(rr.locator('text=of required training current for 2 people').count() == 1 and rr.locator('text=CSQ Certification Program Overview').count() >= 1, '2A.13.2 shows live training evidence + CSQ overview count')
    # View user
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'training': 'read'}
    pg.reload(); pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('text=My required training')
    check(pg.locator('.tabs button', has_text='Training matrix').count() == 0 and pg.get_by_role('button', name='+ Record training').count() == 0, 'View: own training only')
    check(pg.locator('text=SOPs waiting for my signature').count() >= 1 and pg.locator('text=Cart Filling').count() >= 1, 'View: sees own pending SOP signatures')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
