import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []

T['hx_roles'] += [{'id': 'pm', 'name': 'Production Manager', 'description': '', 'perms': {}, 'sort': 0}, {'id': 'tm', 'name': 'Team Member', 'description': '', 'perms': {}, 'sort': 1}]
T['hx_rules'] += [{'id': 'r9', 'state_id': 'st-mo', 'category': 'Inventory', 'citation': '19 CSR 100-1.130', 'title': 'Inventory control', 'body': 'Track all product in METRC.', 'created_at': '1'}]
ROSTER = [{'id': ADMIN, 'name': 'Sam', 'role_ids': ['pm'], 'license_ids': [], 'is_admin': True}, {'id': 'u-lee', 'name': 'Lee Worker', 'role_ids': ['tm'], 'license_ids': ['lic-mo'], 'is_admin': False}]
ME = {'id': ADMIN}
AIF = {'mode': 'ok'}; AICALLS = []
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def handle(route, request):
    u = request.url; m = request.method
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AICALLS.append(b)
        if AIF['mode'] == 'unreachable': return route.abort()
        if b.get('probe'): return jr(route, {'error': {'message': 'messages missing'}}, 400)
        if AIF['mode'] == 'drop': return route.abort()
        if b.get('module') == 'training':
            out = {'lessons': [{'title': 'Missouri inventory rules', 'body': 'Track every package in METRC [19 CSR 100-1.130].\n\n- Record transfers the same day.'}],
                   'quiz': [{'q': 'Where is product tracked?', 'options': ['Paper', 'METRC', 'Email', 'Nowhere'], 'answer': 1, 'explain': '19 CSR 100-1.130'}]}
            return jr(route, {'content': [{'type': 'text', 'text': json.dumps(out)}]})
    if '/rest/v1/rpc/hx_training_roster' in u: return jr(route, ROSTER)
    if '/rest/v1/rpc/hx_training_sop_acks' in u: return jr(route, [])
    if '/rest/v1/rpc/hx_course_submit' in u:
        b = json.loads(request.post_data); c = next(x for x in T['hx_training_courses'] if x['id'] == b['p_course'])
        k = next(x for x in T['hx_training_keys'] if x['course_id'] == c['id']); tot = len(k['answers'])
        ok = sum(1 for i in range(tot) if b['p_answers'][i] == k['answers'][i]); sc = round(ok * 100 / tot); ps = sc >= c['pass_mark']
        wrong = [{'q': i, 'explain': k['explain'][i]} for i in range(tot) if b['p_answers'][i] != k['answers'][i]]
        rid = None
        if ps:
            rid = 'trr-%d' % seq[0]; now()
            T['hx_training_records'].append({'id': rid, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'course_id': c['id'], 'user_id': ME['id'], 'person_name': 'Sam' if ME['id'] == ADMIN else 'Lee Worker', 'completed_on': dt.date.today().isoformat(),
                'expires_on': (dt.date.today() + dt.timedelta(days=365)).isoformat(), 'trainer_name': 'Hendrix online course', 'trainer_qualification': 'Course content version %d approved by Sam' % c['content_version'], 'method': 'Online course', 'language': 'English',
                'assessment': 'Passed', 'score': '%d/%d (%d%%)' % (ok, tot, sc), 'files': [], 'voided': False, 'created_at': now()})
        T['hx_training_attempts'].append({'id': 'att-%d' % len(T['hx_training_attempts']), 'state_id': 'st-mo', 'license_id': 'lic-mo', 'course_id': c['id'], 'user_id': ME['id'], 'person_name': 'Sam', 'content_version': c['content_version'], 'finished_at': now(), 'minutes': 3, 'answers': b['p_answers'], 'correct': ok, 'total': tot, 'score': sc, 'passed': ps, 'record_id': rid})
        return jr(route, {'correct': ok, 'total': tot, 'score': sc, 'pass_mark': c['pass_mark'], 'passed': ps, 'record_id': rid, 'wrong': wrong})
    if '/rest/v1/hx_training_keys' in u and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST': T['hx_training_keys'].append(dict(b)); return jr(route, [b], 201)
        cid = urllib.parse.unquote(u.split('course_id=eq.')[1].split('&')[0]); k = next(x for x in T['hx_training_keys'] if x['course_id'] == cid); k.update(b); return jr(route, [k])
    if '/rest/v1/hx_training_courses' in u and m == 'POST':
        rows = json.loads(request.post_data); rows = rows if isinstance(rows, list) else [rows]
        for r in rows:
            r.setdefault('license_ids', [r['license_id']]); r.setdefault('active', True); r.setdefault('role_ids', []); r.setdefault('sop_id', None)
            r.update({'online': False, 'lessons': [], 'quiz': [], 'pass_mark': 80, 'content_status': 'none', 'content_version': 0, 'content_source': '', 'content_by': '', 'minutes': 15}); T['hx_training_courses'].append(r)
            pull(r)
        return jr(route, rows, 201)
    if '/rest/v1/hx_training_courses' in u and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); c = next(x for x in T['hx_training_courses'] if x['id'] == cid)
        old = dict(c); c.update(b)
        if c.get('content_status') == 'published' and any(old.get(k) != c.get(k) for k in ('lessons', 'quiz', 'content_status', 'pass_mark', 'content_source', 'minutes')):
            if c['topic'] in ('HACCP', 'CSQ program'): c.update(old); return jr(route, {'message': 'outside certification'}, 400)
            c['content_version'] = old.get('content_version', 0) + 1; c['content_by'] = 'Sam'; c['assessment_required'] = True
            if c.get('share_key'):
                for s in T['hx_training_courses']:
                    if s['id'] != c['id'] and s.get('share_key') == c['share_key']: copy(c, s)
        elif c.get('share_key') and old.get('share_key') != c.get('share_key'): pull(c)
        return jr(route, [c])
    return _h(route, request)
def copy(src, dst):
    k = next((x for x in T['hx_training_keys'] if x['course_id'] == src['id']), None)
    if not k: return
    T['hx_training_keys'][:] = [x for x in T['hx_training_keys'] if x['course_id'] != dst['id']] + [{'course_id': dst['id'], 'answers': k['answers'], 'explain': k['explain']}]
    for f in ('online', 'lessons', 'quiz', 'pass_mark', 'minutes', 'content_source', 'content_version', 'content_by'): dst[f] = src[f]
    dst['content_status'] = 'published'; dst['assessment_required'] = True; SYNC.append((src['id'], dst['id']))
def pull(c):
    if not c.get('share_key') or c.get('content_status') == 'published': return
    s = [x for x in T['hx_training_courses'] if x['id'] != c['id'] and x.get('share_key') == c['share_key'] and x.get('content_status') == 'published']
    if s: copy(s[-1], c)
SYNC = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def course(prefix): return next(c for c in T['hx_training_courses'] if c['name'].startswith(prefix))
def take(pg, answers):
    md = pg.locator('.md')
    while md.get_by_role('button', name='Next lesson').count(): md.get_by_role('button', name='Next lesson').click()
    md.get_by_role('button', name='Go to the quiz').click()
    for i, a in enumerate(answers):
        md.locator('.card', has=pg.locator('div', has_text=re.compile('^%d\\. ' % (i + 1)))).first.locator('input[type=radio]').nth(a).check()
    md.get_by_role('button', name='Submit answers').click(); pg.wait_for_selector('.md >> text=/\\d+ of \\d+ correct/')

T['hx_licenses'].append({'id': 'lic-mo2', 'state_id': 'st-mo', 'name': 'Second MO', 'license_number': 'MAN000222', 'license_type': 'Manufacturer', 'active': True})
# a Michigan course made before sharing (step 23 column present, not linked yet)
T['hx_training_courses'].append({'id': 'mi-old', 'state_id': 'st-mi', 'license_id': 'lic-mi', 'license_ids': ['lic-mi'], 'name': 'Product defense and security awareness', 'topic': 'Product defense', 'description': '', 'required_mode': 'everyone', 'role_ids': [], 'min_people': 1, 'refresher_months': 12, 'assessment_required': False, 'sop_id': None, 'active': True, 'sort': 0, 'share_key': None,
  'online': False, 'lessons': [], 'quiz': [], 'pass_mark': 80, 'content_status': 'none', 'content_version': 0, 'content_source': '', 'content_by': '', 'minutes': 15})
def lic_courses(l): return [c for c in T['hx_training_courses'] if c['license_id'] == l]
def by(l, prefix): return next(c for c in lic_courses(l) if c['name'].startswith(prefix))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_trtab","matrix");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses')
    mo = lic_courses('lic-mo')
    check(by('lic-mo', 'Current Good Manufacturing')['share_key'] == 'csq:cgmp' and by('lic-mo', 'Missouri regulatory')['share_key'] == 'law:st-mo' and by('lic-mo', 'HACCP')['share_key'] == 'csq:haccp', 'new courses get share keys (CSQ: all licenses, law: per state)')
    pg.get_by_role('button', name='Publish all').click(); pg.wait_for_selector('.msg >> text=/Published \\d+ online course/')
    cg = by('lic-mo', 'Current Good Manufacturing')
    # Sam passed cGMP and the Missouri law course at Black Fox
    for c, rid in ((cg, 'tr-a'), (by('lic-mo', 'Missouri regulatory'), 'tr-b')):
        T['hx_training_records'].append({'id': rid, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'course_id': c['id'], 'user_id': ADMIN, 'person_name': 'Sam', 'completed_on': dt.date.today().isoformat(), 'expires_on': (dt.date.today() + dt.timedelta(days=365)).isoformat(),
            'trainer_name': 'Hendrix online course', 'trainer_qualification': '', 'method': 'Online course', 'language': 'English', 'assessment': 'Passed', 'score': '10/10 (100%)', 'files': [], 'voided': False, 'created_at': now()})
    # second Missouri license
    pg.locator('select').nth(1).select_option('lic-mo2'); pg.wait_for_timeout(600)
    if pg.locator('text=Training matrix \u00b7 Second MO').count() == 0: pg.get_by_role('button', name='Training', exact=True).click()
    pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses')
    c2 = by('lic-mo2', 'Current Good Manufacturing')
    check(c2['content_status'] == 'published' and c2['content_version'] == cg['content_version'] and c2['lessons'] == cg['lessons'] and any(k['course_id'] == c2['id'] for k in T['hx_training_keys']), 'new license copy starts from the published shared content (same version, answer key)')
    pg.locator('.tabs button', has_text='Training matrix').click()
    r = pg.locator('tr', has=pg.locator('td', has_text='Sam')).first
    cells = {}
    for i, c in enumerate([c for c in lic_courses('lic-mo2') if c['active']]):
        pass
    th = pg.locator('thead th').all_inner_texts()
    ci = next(i for i, t in enumerate(th) if t.startswith('Current Good'))
    li = next(i for i, t in enumerate(th) if t.startswith('Missouri regulatory'))
    tds = r.locator('td')
    check(tds.nth(ci).inner_text().strip() == '\u2713' and tds.nth(li).inner_text().strip() == '\u2713', 'Second MO matrix: cGMP and Missouri law passed at Black Fox count here')
    pg.locator('.tabs button', has_text='Records').click(); pg.wait_for_selector('text=Counted from your other licenses (2)')
    check(pg.locator('td', has_text='Black Fox \u00b7 Missouri').count() == 2, 'records tab shows where the shared training was done')
    pg.locator('.tabs button', has_text='Courses').click()
    check(pg.locator('.card', has_text='Current Good Manufacturing').locator('.badge', has_text='Shared \u00b7 all licenses').count() == 1 and pg.locator('.card', has_text='Missouri regulatory').locator('.badge', has_text='Shared \u00b7 all Missouri licenses').count() == 1, 'course cards show what they are shared with')
    # publishing a new version at Second MO updates Black Fox too
    n0 = len(SYNC); pg.locator('.card', has_text='Current Good Manufacturing').get_by_role('button', name='Online course').click(); md = pg.locator('.md')
    pg.wait_for_selector('.md >> text=Published v'); md.locator('input[placeholder="Lesson title"]').first.fill('What cGMP means (shared update)')
    md.get_by_role('button', name='Publish new version').click(); pg.wait_for_selector('.msg >> text=Published Current Good')
    check(cg['lessons'][0]['title'] == 'What cGMP means (shared update)' and cg['content_version'] == c2['content_version'] and len(SYNC) > n0, 'publishing at one license updates the shared course at the others')
    # custom shared course
    pg.get_by_role('button', name='+ Course').click(); md = pg.locator('.md')
    field(md, 'Course name *').fill('Forklift operation'); md.locator('label.ck', has_text='Same course at all my licenses').locator('input').check()
    md.get_by_role('button', name='Save course').click(); pg.wait_for_selector('.msg >> text=Saved.')
    check(by('lic-mo2', 'Forklift')['share_key'] == 'custom:forklift-operation', 'a custom course can be shared with all licenses')
    # Michigan
    pg.locator('select').first.select_option('st-mi'); pg.wait_for_timeout(800)
    if pg.locator('text=Training matrix \u00b7 Key Stone').count() == 0: pg.get_by_role('button', name='Training', exact=True).click()
    pg.wait_for_selector('.msg >> text=now shared with your other licenses')
    check(T['hx_training_courses'][[c['id'] for c in T['hx_training_courses']].index('mi-old')]['share_key'] == 'csq:product-defense', 'existing Michigan course linked to the shared course')
    pg.locator('.tabs button', has_text='Courses').click(); pg.get_by_role('button', name='Add missing CSQ starter courses').click(); pg.wait_for_selector('.msg >> text=/Added \\d+ CSQ starter/')
    check(by('lic-mi', 'Current Good Manufacturing')['content_status'] == 'published' and by('lic-mi', 'Michigan regulatory')['share_key'] == 'law:st-mi', 'Michigan gets the shared published cGMP; its own Michigan law course')
    pg.locator('.tabs button', has_text='Records').click(); pg.wait_for_selector('text=Counted from your other licenses (1)')
    check(pg.locator('td', has_text='Missouri regulatory').count() == 0, 'Missouri law training does not count in Michigan; cGMP does')
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
