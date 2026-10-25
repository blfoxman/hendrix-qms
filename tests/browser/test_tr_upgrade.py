import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors=[]
T['hx_roles'] += [{'id': 'gm', 'name': 'General Manager', 'description': '', 'perms': {}, 'sort': 0}, {'id': 'co', 'name': 'Compliance Officer', 'description': '', 'perms': {}, 'sort': 1}, {'id': 'tm', 'name': 'Team Member', 'description': '', 'perms': {}, 'sort': 2}, {'id': 'sa', 'name': 'Sanitation', 'description': '', 'perms': {}, 'sort': 3}]
old = [('Regulatory compliance (state rules)','everyone'),('Chemical safety and SDS','optional'),('CSQ Certification Program Overview','at_least'),('HACCP certification (International HACCP Alliance)','at_least')]
for i,(n,m) in enumerate(old):
    T['hx_training_courses'].append({'id':'c%d'%i,'state_id':'st-mo','license_id':'lic-mo','license_ids':['lic-mo'],'name':n,'topic':'HACCP' if 'HACCP' in n else 'CSQ program' if 'CSQ' in n else 'Safety','description':'','required_mode':m,'role_ids':[],'min_people':2 if 'HACCP' in n else 1,'refresher_months':12,'assessment_required':False,'sop_id':None,'active':True,'sort':i})
_h=handle
def handle(route, request):
    if '/rest/v1/rpc/hx_training_roster' in request.url: return route.fulfill(status=200, content_type='application/json', body=json.dumps([{'id': ADMIN, 'name': 'Sam', 'role_ids': ['gm'], 'license_ids': [], 'is_admin': True}]))
    if '/rest/v1/rpc/hx_training_sop_acks' in request.url: return route.fulfill(status=200, content_type='application/json', body='[]')
    return _h(route, request)
def check(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: errors.append(m)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Open training'); pg.get_by_role('button', name='Training', exact=True).click()
    pg.wait_for_selector('.msg >> text=3 courses are now required manager training')
    check(pg.locator('.msg', has_text='regulatory course is now Missouri regulatory compliance (state rules)').count() == 1, 'generic law course renamed for Missouri')
    C={c['id']:c for c in T['hx_training_courses']}
    check(C['c0']['required_mode']=='everyone', 'everyone course stays for everyone')
    check(C['c2']['required_mode']=='roles' and sorted(C['c2']['role_ids'])==['co','gm'] and C['c3']['required_mode']=='roles', 'CSQ overview + HACCP become manager training (GM, Compliance)')
    check(sorted(C['c1']['role_ids'])==['co','gm','sa'], 'chemical safety: managers + sanitation, not team members')
    pg.reload(); pg.get_by_role('button', name='Training', exact=True).click(); pg.wait_for_timeout(800)
    check(pg.locator('.msg', has_text='manager training').count()==0, 'runs once (no change on the next visit)')
    check(C['c0']['name']=='Missouri regulatory compliance (state rules)' and C['c0']['required_mode']=='everyone', 'Missouri law course keeps its records and stays for everyone')
    # Michigan license gets its own courses with Michigan law
    pg.locator('header select, .top select').first.select_option(label='Michigan') if pg.locator('header select, .top select').count() else pg.locator('select').first.select_option(label='Michigan')
    pg.wait_for_timeout(600); pg.get_by_role('button', name='Training', exact=True).click()
    pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses')
    mi=[c for c in T['hx_training_courses'] if c['license_id']=='lic-mi']; mo=[c for c in T['hx_training_courses'] if c['license_id']=='lic-mo']
    check(len(mo)==5 and len(mi)==9 and any(c['name']=='Michigan regulatory compliance (state rules)' and 'CRA' in c['description'] for c in mi) and not any('Missouri' in c['name'] for c in mi), 'Michigan gets Michigan regulatory training; Missouri courses untouched')
    pg.locator('.tabs button', has_text='Courses').click(); pg.wait_for_selector('text=Michigan regulatory compliance')
    check(pg.locator('text=Missouri regulatory compliance').count()==0, 'Michigan screen shows no Missouri course')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
