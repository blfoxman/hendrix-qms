import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []

T['hx_roles'] += [{'id': 'pm', 'name': 'Production Manager', 'description': '', 'perms': {}, 'sort': 0}, {'id': 'tm', 'name': 'Team Member', 'description': '', 'perms': {}, 'sort': 1},
                  {'id': 'sm', 'name': 'Security Manager', 'description': '', 'perms': {}, 'sort': 2}, {'id': 'so', 'name': 'Security Officer', 'description': '', 'perms': {}, 'sort': 3}]
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
        return jr(route, rows, 201)
    if '/rest/v1/hx_training_courses' in u and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); c = next(x for x in T['hx_training_courses'] if x['id'] == cid)
        old = dict(c); c.update(b)
        if c.get('content_status') == 'published' and any(old.get(k) != c.get(k) for k in ('lessons', 'quiz', 'content_status', 'pass_mark', 'content_source', 'minutes')):
            if c['topic'] == 'HACCP': c.update(old); return jr(route, {'message': 'outside certification'}, 400)
            c['content_version'] = old.get('content_version', 0) + 1; c['content_by'] = 'Sam'; c['assessment_required'] = True
        return jr(route, [c])
    return _h(route, request)
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
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Open training'); pg.get_by_role('button', name='Training', exact=True).click()
    pg.wait_for_selector('.msg >> text=9 online courses are ready to review and publish', timeout=15000)
    sec = course('Missouri security manager training')
    check(sec['required_mode'] == 'roles' and sec['role_ids'] == ['sm'] and sec['share_key'] == 'sec:st-mo' and 'Only for the Security Manager role' in sec['description'], 'Missouri security manager course: required for Security Manager only (not Security Officer), shared across Missouri licenses')
    check(course('CSQ Certification')['role_ids'] == ['pm'] and course('HACCP certification')['role_ids'] == ['pm'], 'manager courses do not go to the Security Manager')
    check(sec['content_status'] == 'draft' and len(sec['lessons']) == 7 and len(sec['quiz']) == 14 and '19 CSR 100-1.090' in sec['content_source'] and sec['content_source'].startswith('Hendrix starter'), 'Missouri content: 7 lessons, 14 questions from 19 CSR 100-1.090')
    check(any('1920 x 1080' in l['body'] for l in sec['lessons']) and not any('720p' in l['body'] for l in sec['lessons']), 'Missouri camera rule (1080p), not Michigan')
    pg.get_by_role('button', name='Publish all').click(); pg.wait_for_selector('.msg >> text=Published 9 online courses')
    pg.locator('.tabs button', has_text='Courses').click(); pg.wait_for_selector('text=Missouri security manager training')
    sc = pg.locator('.card', has_text='Missouri security manager training')
    check(sc.locator('text=Chosen roles: Security Manager').count() == 1 and sc.get_by_role('button', name='Take course').count() == 0, 'courses list: Security Manager only; no Take course for a production manager')
    pg.locator('.tabs button', has_text='My training').click(); pg.wait_for_selector('text=Other online courses')
    check(pg.locator('.card', has_text='Other online courses').locator('text=security manager').count() == 0, 'not offered to other roles as an optional course')
    # Sam becomes the security manager
    ROSTER[0]['role_ids'] = ['sm']; T['hx_profiles'][0]['role_ids'] = ['sm']
    pg.reload(); pg.wait_for_selector('text=Open training'); pg.get_by_role('button', name='Training', exact=True).click()
    pg.locator('.tabs button', has_text='My training').click(); pg.wait_for_selector('text=My required training')
    mr = pg.locator('.card', has_text='My required training')
    check(mr.locator('text=Missouri security manager training (state rules)').count() == 1, 'security manager sees it as required training')
    mr.locator('.row', has_text='Missouri security manager').get_by_role('button', name='Take course').click(); pg.wait_for_selector('.md >> text=Your role as security manager')
    key = next(k for k in T['hx_training_keys'] if k['course_id'] == sec['id']); take(pg, key['answers'])
    check(pg.locator('.md').locator('text=Passed - your training is recorded').count() == 1, 'security manager passes the Missouri course')
    pg.locator('.md').get_by_role('button', name='Done').click()
    # Michigan
    ROSTER[0]['role_ids'] = ['pm']; T['hx_profiles'][0]['role_ids'] = ['pm']
    pg.locator('header select, .top select').first.select_option(label='Michigan') if pg.locator('header select, .top select').count() else pg.locator('select').first.select_option(label='Michigan')
    pg.wait_for_timeout(600); pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('.msg >> text=Created the 11 CSQ training courses', timeout=15000)
    mi = course('Michigan security manager training')
    check(mi['license_id'] == 'lic-mi' and mi['share_key'] == 'sec:st-mi' and mi['role_ids'] == ['sm'] and len(mi['lessons']) == 7 and len(mi['quiz']) == 12 and 'R 420.209' in mi['content_source'], 'Michigan gets its own security manager course with Michigan content')
    check(any('720p' in l['body'] for l in mi['lessons']) and not any('19 CSR' in l['body'] for l in mi['lessons']), 'Michigan camera rule (720p), no Missouri rules')
    check(not any(c['license_id'] == 'lic-mi' and 'Missouri' in c['name'] for c in T['hx_training_courses']), 'no Missouri course on the Michigan license')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
