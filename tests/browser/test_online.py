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
        return jr(route, rows, 201)
    if '/rest/v1/hx_training_courses' in u and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); c = next(x for x in T['hx_training_courses'] if x['id'] == cid)
        old = dict(c); c.update(b)
        if c.get('content_status') == 'published' and any(old.get(k) != c.get(k) for k in ('lessons', 'quiz', 'content_status', 'pass_mark', 'content_source', 'minutes')):
            if c['topic'] in ('HACCP', 'CSQ program'): c.update(old); return jr(route, {'message': 'outside certification'}, 400)
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
    pg.wait_for_selector('.msg >> text=7 online courses are ready to review and publish', timeout=15000)
    drafts = [c for c in T['hx_training_courses'] if c['content_status'] == 'draft']
    check(len(drafts) == 7 and any(c['topic'] == 'Extraction' for c in drafts) and not any(c['topic'] == 'cGACP' for c in T['hx_training_courses']) and not any(c['topic'] in ('HACCP', 'CSQ program', 'Required by law') for c in drafts), '7 starter courses as drafts incl. Extraction and HACCP basics; no cGACP on a manufacturing license')
    hb = next(c for c in drafts if c['topic'] == 'HACCP basics'); hk = next(k for k in T['hx_training_keys'] if k['course_id'] == hb['id'])
    check(len(hb['lessons']) == 8 and len(hb['quiz']) == 15 and len(hk['answers']) == 15 and 'does not replace the HACCP certificate' in hb['lessons'][-1]['body'], 'HACCP basics: 8 lessons, 15 questions, says it does not replace the certificate')
    cg = course('Current Good'); key = next(k for k in T['hx_training_keys'] if k['course_id'] == cg['id'])
    check(len(cg['lessons']) == 5 and len(cg['quiz']) == 10 and all('answer' not in q for q in cg['quiz']) and len(key['answers']) == 10, 'cGMP: 5 lessons, 10 questions; answers kept only in the key table')
    pg.wait_for_selector('.card >> text=Online courses ready'); check(pg.locator('.card', has_text='Online courses ready').count() == 1, 'banner: online courses ready')
    pg.get_by_role('button', name='Publish all').click(); pg.wait_for_selector('.msg >> text=Published 7 online courses')
    check(all(c['content_status'] == 'published' and c['content_version'] == 1 for c in T['hx_training_courses'] if c['content_status'] != 'none'), 'published (version 1)')
    pg.locator('.tabs button', has_text='Courses').click(); pg.wait_for_selector('text=Online · v1 · pass 80%')
    hc = pg.locator('.card', has_text='HACCP certification')
    check(hc.locator('text=Outside certification').count() == 1 and hc.get_by_role('button', name='Online course').count() == 0, 'HACCP stays an outside certification')
    # take and pass
    pg.locator('.card', has_text='Current Good Manufacturing').get_by_role('button', name='Take course').click(); pg.wait_for_selector('.md >> text=What cGMP means')
    check(pg.locator('.md').locator('text=Lesson 1 of 5').count() == 1, 'lesson player')
    take(pg, key['answers'])
    check(pg.locator('.md').locator('text=Passed - your training is recorded').count() == 1, 'pass screen 100%')
    r = [x for x in T['hx_training_records'] if x['course_id'] == cg['id']]
    check(len(r) == 1 and r[0]['method'] == 'Online course' and r[0]['assessment'] == 'Passed' and r[0]['score'] == '10/10 (100%)', 'pass recorded as training (Online course, Passed, score)')
    pg.locator('.md').get_by_role('button', name='Done').click()
    # take again and fail
    pg.locator('.card', has_text='Current Good Manufacturing').get_by_role('button', name='Take course').click(); pg.wait_for_selector('.md >> text=What cGMP means')
    take(pg, [(a + 1) % 4 for a in key['answers']])
    check(pg.locator('.md').locator('text=Not passed (pass mark 80%)').count() == 1 and pg.locator('.md').locator('text=cGMP means Current Good Manufacturing Practices').count() == 1, 'fail screen with explanations for wrong answers')
    check(len([x for x in T['hx_training_records'] if x['course_id'] == cg['id']]) == 1 and len(T['hx_training_attempts']) == 2, 'failed attempt kept, no training record added')
    pg.screenshot(path=OUT + 'course_fail.png')
    pg.locator('.md').get_by_role('button', name='Read again and retake').click(); check(pg.locator('.md').locator('text=Lesson 1 of 5').count() == 1, 'retake starts from the lessons')
    pg.locator('.mo').first.click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(300)
    # edit content -> new version
    pg.locator('.tabs button', has_text='Courses').click(); pg.locator('.card', has_text='Current Good Manufacturing').get_by_role('button', name='Online course').click(); md = pg.locator('.md')
    pg.wait_for_selector('.md >> text=Published v1 by Sam'); md.locator('input[placeholder="Lesson title"]').first.fill('What cGMP means (updated)')
    md.get_by_role('button', name='Publish new version').click(); pg.wait_for_selector('.msg >> text=Published Current Good')
    check(course('Current Good')['content_version'] == 2 and course('Current Good')['lessons'][0]['title'].endswith('(updated)'), 'content change published as version 2')
    # law course AI draft
    pg.locator('.card', has_text='Missouri regulatory compliance').get_by_role('button', name='Online course').click(); md = pg.locator('.md')
    AIF['mode'] = 'unreachable'; md.get_by_role('button', name='Draft from the Missouri Rulebook with AI').click(); pg.wait_for_selector('.md .msg.err >> text=Hendrix cannot reach the AI')
    check(md.locator('text=Failed to fetch').count() == 0, 'AI unreachable: says the function is not deployed instead of "Failed to fetch"')
    AIF['mode'] = 'drop'; md.get_by_role('button', name='Draft from the Missouri Rulebook with AI').click(); pg.wait_for_selector('.md .msg.err >> text=The AI function is set up, but the connection closed')
    check(True, 'AI connection dropped: says it is set up but closed early')
    AIF['mode'] = 'ok'; n0 = len(AICALLS)
    md.get_by_role('button', name='Draft from the Missouri Rulebook with AI').click(); pg.wait_for_selector('.md input[value="Missouri inventory rules"]')
    check(len(AICALLS) - n0 == 2 and 'Return ONLY JSON: {"lessons"' in AICALLS[-2]['messages'][0]['content'] and 'LESSONS:' in AICALLS[-1]['messages'][0]['content'], 'law course drafted in two shorter AI requests (lessons, then quiz)')
    check(field(md, 'Source of the content').input_value().startswith('AI draft from the Missouri Rulebook (2 rules)'), 'AI draft from the Missouri Rulebook')
    md.get_by_role('button', name='Save draft').click(); pg.wait_for_selector('.msg >> text=Draft saved')
    law = course('Missouri regulatory'); lk = next(k for k in T['hx_training_keys'] if k['course_id'] == law['id'])
    check(law['content_status'] == 'draft' and lk['answers'] == [1], 'law course saved as draft for review (not published)')
    # records tab attempts
    pg.locator('.tabs button', has_text='Records').click(); pg.wait_for_selector('text=Online quiz attempts (2)')
    check(pg.locator('tr', has_text='Not passed').count() == 1 and pg.locator('tr', has_text='10/10 (100%)').count() >= 1, 'attempt log for inspectors')
    pg.locator('.tabs button', has_text='Training matrix').click(); pg.wait_for_selector('td >> text=Lee Worker')
    sam = pg.locator('tr', has=pg.locator('td', has_text='Sam')).first
    check(sam.locator('.trcell').evaluate_all('els=>els.map(e=>getComputedStyle(e).backgroundColor)').count('rgb(95, 191, 138)') >= 1, 'matrix shows the passed online course green')
    pg.screenshot(path=OUT + 'online_matrix.png')
    # view-only learner
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'training': 'read'}; ROSTER[:] = [ROSTER[0]]
    pg.reload(); pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_selector('text=My required training')
    check(pg.locator('.card', has_text='My required training').get_by_role('button', name='Take course').count() >= 4, 'learner sees Take course on required online courses')
    pg.locator('.card', has_text='My required training').get_by_role('button', name='Take course').first.click(); pg.wait_for_selector('.md >> text=Lesson 1 of')
    pg.screenshot(path=OUT + 'course_lesson.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
