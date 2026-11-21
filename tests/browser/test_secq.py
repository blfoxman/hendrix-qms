import os, re
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 67: 3 security questions, set at sign-in and in My account; used when the password is forgotten and the email is out of reach
errors = []
MEM = '22222222-2222-2222-2222-222222222222'
T['hx_profiles'][0].update({'email': 's@x'})
T['hx_profiles'].append({'id': MEM, 'name': 'Maria Lopez', 'email': 'maria@x.com', 'role': 'member', 'approved': True, 'role_ids': [], 'license_ids': ['lic-mo'], 'perms': {'qms': 'read'}, 'must_change_password': False, 'created_at': '2026-02-01T00:00:00Z'})
ST = {'secq': {ADMIN: ['What was the name of your first pet?', 'In what city were you born?', 'What was your first job?']}, 'answers': {ADMIN: ['rex', 'new york', 'line cook']},
      'set': [], 'tries': [], 'missing': False, 'fail': 0}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def norm(a): return ' '.join(a.strip().lower().split())
_h = handle
def handle(route, request):
    path = urllib.parse.urlparse(request.url).path; b = json.loads(request.post_data) if request.post_data else {}
    who = MEM if 'tok-mem' in (request.headers.get('authorization') or '') else ADMIN
    if '/rpc/hx_' in path and any(path.endswith(x) for x in ('hx_my_security_questions', 'hx_set_security_questions', 'hx_recovery_questions', 'hx_recover_with_answers')) and ST['missing']:
        return jr(route, {'code': 'PGRST202', 'message': 'Could not find the function public.%s in the schema cache' % path.split('/')[-1]}, 404)
    if path.endswith('/rpc/hx_my_security_questions'):
        q = ST['secq'].get(who); return jr(route, {'set': bool(q), 'questions': q or []})
    if path.endswith('/rpc/hx_set_security_questions'):
        if len(set(x.lower() for x in b['p_questions'])) < 3: return jr(route, {'message': 'Choose 3 different questions.'}, 400)
        ST['set'].append((who, b)); ST['secq'][who] = b['p_questions']; ST['answers'][who] = [norm(a) for a in b['p_answers']]; return jr(route, True)
    if path.endswith('/rpc/hx_recovery_questions'):
        uid = MEM if b['p_email'].strip().lower() == 'maria@x.com' else None
        return jr(route, {'questions': ST['secq'].get(uid) or ['What was your first job?', 'What street did you grow up on?', 'In what city did your parents meet?']})
    if path.endswith('/rpc/hx_recover_with_answers'):
        ST['tries'].append(b); uid = MEM if b['p_email'].strip().lower() == 'maria@x.com' else None
        if ST['fail'] >= 5: return jr(route, {'ok': False, 'locked': True, 'left': 0, 'error': 'Too many wrong answers. Wait an hour and try again, or ask a Hendrix admin for a temporary password.'})
        ok = uid and [norm(a) for a in b['p_answers']] == ST['answers'].get(uid)
        if not ok: ST['fail'] += 1; return jr(route, {'ok': False, 'locked': ST['fail'] >= 5, 'left': max(0, 5 - ST['fail']), 'error': 'Those answers do not match. Check the spelling and try again.'})
        return jr(route, {'ok': True})
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def ctx_for(b, uid):
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    init = 'localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");'
    if uid:
        s = {'access_token': 'tok-mem' if uid == MEM else 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': uid, 'email': 'maria@x.com' if uid == MEM else 's@x'}}
        init += 'localStorage.setItem("hx_session",%s);' % json.dumps(json.dumps(s))
    ctx.add_init_script('if(!sessionStorage.getItem("o")){sessionStorage.setItem("o","1");' + init + '}')
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    return ctx, pg
def q(pg, i): return pg.locator('select[aria-label="Question %d"]' % i)
def a(pg, i): return pg.locator('input[aria-label="Answer %d"]' % i)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    # 1. someone without questions: asked right after sign-in
    ctx, pg = ctx_for(b, MEM); pg.goto(BASE); pg.wait_for_selector('h2 >> text=Set your security questions')
    check(pg.locator('.nav').count() == 0, 'nothing opens until the 3 questions are set')
    pg.get_by_role('button', name='Save and continue').click(); pg.wait_for_selector('text=Choose question 1.')
    q(pg, 1).select_option('What was the name of your first pet?'); a(pg, 1).fill('Biscuit')
    check(q(pg, 2).locator('option[value="What was the name of your first pet?"]').get_attribute('disabled') is not None, 'a question already picked cannot be picked twice')
    q(pg, 2).select_option('__own__'); pg.locator('input[aria-label="Your question 2"]').fill('Boss?'); a(pg, 2).fill('Dee')
    q(pg, 3).select_option('What was your first job?')
    pg.get_by_role('button', name='Save and continue').click(); pg.wait_for_selector('text=Write question 2 as a full question.')
    pg.locator('input[aria-label="Your question 2"]').fill('What was the name of my first boss?')
    pg.get_by_role('button', name='Save and continue').click(); pg.wait_for_selector('text=Answer question 3.')
    check(ST['set'] == [], 'incomplete questions are not saved')
    a(pg, 3).fill('Line cook'); pg.screenshot(path=OUT + 'secq_setup.png')
    pg.get_by_role('button', name='Save and continue').click(); pg.wait_for_selector('.nav')
    check(len(ST['set']) == 1 and ST['set'][0][1]['p_questions'] == ['What was the name of your first pet?', 'What was the name of my first boss?', 'What was your first job?'] and ST['set'][0][1]['p_answers'] == ['Biscuit', 'Dee', 'Line cook'],
          'saved: 2 from the list + 1 of their own, with the answers; Hendrix opens')
    pg.reload(); pg.wait_for_selector('.nav'); check(pg.locator('h2 >> text=Set your security questions').count() == 0, 'not asked again once set')
    # 2. My account: see and change
    pg.locator('button[title^="My account"]').click(); card = pg.locator('.card', has=pg.locator('h3', has_text='Security questions')); card.wait_for()
    card.locator('li', has_text='What was the name of my first boss?').wait_for()
    check(card.locator('li').count() == 3 and 'Dee' not in card.inner_text(), 'My account lists the 3 questions, never the answers')
    card.get_by_role('button', name='Change my questions').click()
    check(q(pg, 2).input_value() == '__own__' and pg.locator('input[aria-label="Your question 2"]').input_value() == 'What was the name of my first boss?' and a(pg, 1).input_value() == '', 'change: questions kept, answers asked again')
    a(pg, 1).fill('Biscuit'); a(pg, 2).fill('Dee'); a(pg, 3).fill('Barista'); card.get_by_role('button', name='Save my security questions').click()
    card.locator('text=Security questions saved.').wait_for(); check(ST['answers'][MEM][2] == 'barista', 'changed answers saved')
    ctx.close()
    # 3. forgot the password, no email: answer the questions
    ctx, pg = ctx_for(b, None); pg.goto(BASE); pg.wait_for_selector('text=Forgot your password?')
    pg.get_by_text('Forgot your password?').click(); pg.get_by_text('No access to that email? Answer your security questions').click()
    pg.wait_for_selector('h2 >> text=Answer your security questions')
    pg.locator('input[aria-label="Email"]').fill('maria@x.com'); pg.get_by_role('button', name='Show my questions').click()
    pg.wait_for_selector('label >> text=What was the name of my first boss?')
    check(pg.locator('input[aria-label^="Answer "]').count() == 3, 'the person\'s own 3 questions are shown')
    a(pg, 1).fill('biscuit'); a(pg, 2).fill('dee'); a(pg, 3).fill('line cook')
    pg.locator('input[aria-label="New password"]').fill('Fresh-Pass-26'); pg.locator('input[aria-label="New password again"]').fill('Fresh-Pass-26')
    pg.get_by_role('button', name='Reset my password').click(); pg.wait_for_selector('text=4 tries left this hour.')
    check(pg.locator('text=Those answers do not match').count() == 1, 'wrong answer: refused with tries left')
    a(pg, 3).fill('  BARISTA '); pg.locator('input[aria-label="New password again"]').fill('Fresh-Pass-27')
    pg.get_by_role('button', name='Reset my password').click(); pg.wait_for_selector('text=The two passwords are not the same.')
    pg.locator('input[aria-label="New password again"]').fill('Fresh-Pass-26'); pg.screenshot(path=OUT + 'secq_recover.png')
    pg.get_by_role('button', name='Reset my password').click(); pg.wait_for_selector('text=Password changed. Sign in with your new password.')
    check(ST['tries'][-1] == {'p_email': 'maria@x.com', 'p_answers': ['biscuit', 'dee', '  BARISTA '], 'p_password': 'Fresh-Pass-26'} and pg.get_by_role('button', name='Sign in').count() == 1,
          'right answers: password changed, back on the sign-in form')
    # an email without an account looks the same (3 questions, then "do not match")
    pg.get_by_text('Forgot your password?').click(); pg.get_by_text('No access to that email? Answer your security questions').click()
    pg.locator('input[aria-label="Email"]').fill('nobody@x.com'); pg.get_by_role('button', name='Show my questions').click()
    pg.wait_for_selector('label >> text=What street did you grow up on?')
    check(pg.locator('input[aria-label^="Answer "]').count() == 3, 'unknown email: 3 questions all the same (no hint whether the account exists)')
    # lockout message
    ST['fail'] = 5; a(pg, 1).fill('x'); a(pg, 2).fill('y'); a(pg, 3).fill('z')
    pg.locator('input[aria-label="New password"]').fill('Fresh-Pass-26'); pg.locator('input[aria-label="New password again"]').fill('Fresh-Pass-26')
    pg.get_by_role('button', name='Reset my password').click(); pg.wait_for_selector('text=Too many wrong answers. Wait an hour')
    check(pg.locator('text=tries left').count() == 0, 'locked: says to wait an hour or ask an admin')
    ctx.close()
    # 4. step 67 not installed: nobody is blocked, recovery says to ask an admin
    ST['missing'] = True; ST['secq'].pop(MEM, None)
    ctx, pg = ctx_for(b, MEM); pg.goto(BASE); pg.wait_for_selector('.nav')
    check(pg.locator('h2 >> text=Set your security questions').count() == 0, 'not installed: sign-in is not blocked')
    ctx.close()
    ctx, pg = ctx_for(b, None); pg.goto(BASE); pg.wait_for_selector('text=Forgot your password?')
    pg.get_by_text('Forgot your password?').click(); pg.get_by_text('No access to that email? Answer your security questions').click()
    pg.locator('input[aria-label="Email"]').fill('maria@x.com'); pg.get_by_role('button', name='Show my questions').click()
    pg.wait_for_selector('text=Security questions are not set up on this Hendrix yet'); check(True, 'not installed: recovery points to an admin')
    ctx.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
