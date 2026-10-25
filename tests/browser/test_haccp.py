import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
T['hx_batches'] += [{'id': 'bg1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'gummies', 'batch_number': 'GUM-100', 'sku_id': None, 'sku': 'Gummies 10pk', 'flavor_id': None, 'flavor': 'Mango', 'status': 'In Progress', 'data': {'date': NOW[:10]}, 'attachments': [], 'performed_by': 'Sam', 'created_at': NOW, 'updated_at': NOW, 'voided': False}]
for t in ('hx_haccp_team', 'hx_haccp_plans', 'hx_haccp_monitoring', 'hx_haccp_verifications'): T[t] = []
SEQ = [0]
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_haccp_plans' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST':
            SEQ[0] += 1; p = {**b, 'number': 'HP-%03d' % SEQ[0], 'status': 'draft', 'version': 0, 'validated_on': None, 'approved_by': '', 'flow_reviewed_on': None, 'created_at': NOW}; st_new = b.get('status'); p['status'] = 'draft'
        else:
            cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); p = next(x for x in T['hx_haccp_plans'] if x['id'] == cid); old = dict(p); st_new = b.get('status'); p.update(b); p['status'] = old['status']
        if st_new in ('validated', 'active'):
            if len([t for t in T['hx_haccp_team'] if t['certified'] and t.get('active', True)]) < 2: return jr(route, {'message': 'The HACCP team needs one person and a backup certified'}, 400)
            if not p.get('validation'): return jr(route, {'message': 'Record how the plan was validated'}, 400)
            p['validated_on'] = NOW[:10]
            if st_new == 'active': p['version'] = p.get('version', 0) + 1; p['approved_by'] = 'Sam'; p['flow_reviewed_on'] = NOW[:10]
            p['status'] = st_new
        elif st_new: p['status'] = st_new
        if m == 'POST': T['hx_haccp_plans'].append(p)
        return jr(route, [p], 201 if m == 'POST' else 200)
    if tbl == 'hx_haccp_monitoring' and m == 'POST':
        r = json.loads(request.post_data); p = next(x for x in T['hx_haccp_plans'] if x['id'] == r['plan_id']); c = next(x for x in p['ccps'] if x['id'] == r['ccp_id'])
        r.update({'plan_version': p['version'], 'ccp_name': c['name'], 'checked_at': NOW, 'recorded_by': 'Sam', 'verified_by': '', 'verified_at': None, 'voided': False}); T['hx_haccp_monitoring'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_haccp_monitoring' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_haccp_monitoring'] if x['id'] == cid)
        if b.get('verified_at') and r['checked_by'] == 'Sam': return jr(route, {'message': 'Records are verified by someone other than the person who did the check.'}, 400)
        r.update(b); r['verified_by'] = 'Sam'; return jr(route, [r])
    if tbl == 'hx_haccp_team' and m == 'POST':
        r = json.loads(request.post_data); T['hx_haccp_team'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_haccp_verifications' and m == 'POST':
        r = json.loads(request.post_data); r.update({'voided': False}); T['hx_haccp_verifications'].append(r); return jr(route, [r], 201)
    if '/rest/v1/rpc/hx_training_roster' in u: return jr(route, [{'id': ADMIN, 'name': 'Sam', 'role_ids': [], 'license_ids': []}, {'id': 'u-lee', 'name': 'Lee QA', 'role_ids': [], 'license_ids': ['lic-mo']}])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_btype","gummies");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('.card.gold', has_text='HACCP').locator('text=No active plan').count() == 1, 'dashboard: no active HACCP plan')
    pg.get_by_role('button', name='HACCP', exact=True).click(); pg.wait_for_selector('text=No HACCP plans yet')
    # team
    pg.locator('.tabs button', has_text='HACCP team').click()
    for who, role, dep in (('u-lee', 'Team leader', 'Quality'), (ADMIN, 'Backup', 'Senior management')):
        pg.get_by_role('button', name='+ Member').click(); md = pg.locator('.md'); field(md, 'Person').select_option(who); field(md, 'Role').select_option(role); field(md, 'Department').fill(dep)
        md.locator('label.ck', has_text='HACCP certified').locator('input').check(); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md .msg.err >> text=Enter the certificate')
        field(md, 'Course / provider').fill('IHA-accredited HACCP course'); md.get_by_role('button', name='Save').click(); pg.wait_for_timeout(300)
    check(len(T['hx_haccp_team']) == 2 and T['hx_haccp_team'][0]['name'] == 'Lee QA', 'team: leader and backup, certified')
    # plan from the gummies draft
    pg.get_by_role('button', name='+ HACCP plan').click(); md = pg.locator('.md')
    field(md, 'Plan name *').fill('Gummies'); field(md, 'Covers batch type').select_option('gummies')
    md.get_by_role('button', name='Start from a draft for this batch type').click()
    md.locator('.tabs button', has_text='2. Process flow').click()
    check(md.locator('svg text', has_text='Dose distillate').count() >= 1 and md.locator('svg text', has_text='CCP').count() == 2, 'starting draft draws the flow with 2 CCPs')
    md.locator('div.card', has=pg.locator('svg')).screenshot(path=OUT + 'haccp_flow.png')
    md.locator('.tabs button', has_text='1. Product').click()
    check(md.locator('text=Product description: Ingredients').count() == 1, 'missing description fields listed')
    field(md, 'Ingredients *').fill('Sugar, corn syrup, pectin, citric acid, flavor, distillate'); field(md, 'Allergens *').fill('None')
    md.get_by_role('button', name='Activate plan').click(); pg.wait_for_timeout(500); print('ERR', md.locator('.msg.err').all_inner_texts()); pg.wait_for_selector('.md .msg.err >> text=validated')
    md.locator('.tabs button', has_text='5. Validation').click(); field(md, 'How the plan was validated *').fill('Homogeneity study on 3 batches (RSD < 5%); aw limit from FDA guidance, verified by 3 batch tests')
    md.get_by_role('button', name='Activate plan').click(); pg.wait_for_selector('.msg >> text=Activated Gummies.')
    p = T['hx_haccp_plans'][0]
    check(p['status'] == 'active' and p['version'] == 1 and len(p['ccps']) == 2 and len(p['hazards']) >= 10, 'plan activated as version 1 with hazards and CCPs')
    pg.locator('.tabs button', has_text='Plans').click(); pg.wait_for_selector('td >> text=HP-001')
    with pg.expect_popup() as pop: pg.locator('tr', has_text='HP-001').get_by_role('button', name='Print').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('HACCP plan summary' in html and '<svg' in html and 'CCP 2 Water activity' in html and 'Lee QA' in html and 'Hazard analysis' in html, 'printable HACCP plan with team, flow diagram, hazard analysis and CCP summary'); w.close()
    # monitoring
    pg.get_by_role('button', name='+ CCP check').click(); md = pg.locator('.md')
    field(md, 'CCP').select_option(label='CCP 2 Water activity'); field(md, 'Batch').select_option('bg1'); field(md, 'Measured value *').fill('aw 0.91'); field(md, 'Within the critical limit?').select_option('no')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.md .msg.err >> text=corrective action')
    field(md, 'Corrective action taken *').fill('Back to curing room 12 h, re-tested'); field(md, 'Product *').select_option('held'); field(md, 'Checked by *').fill('Lee QA')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=OUT of limits')
    pg.locator('.tabs button', has_text='CCP monitoring').click(); pg.wait_for_selector('td >> text=aw 0.91')
    check(pg.locator('tr', has_text='aw 0.91').get_by_role('button', name='Deviation').count() == 1, 'out-of-limit check can raise a deviation')
    pg.locator('tr', has_text='aw 0.91').get_by_role('button', name='Verify').click(); pg.wait_for_selector('.msg >> text=Verified.')
    check(T['hx_haccp_monitoring'][0]['verified_by'] == 'Sam', 'second person verifies the record')
    # batch tracker
    pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('text=GUM-100')
    card = pg.locator('.card', has=pg.locator('b', has_text=re.compile('^GUM-100$')))
    pg.wait_for_selector('.badge >> text=CCP 0/2'); check(card.locator('.badge', has_text='CCP 0/2 · deviation').count() == 1, 'batch card shows CCP status with the deviation')
    card.get_by_role('button', name='CCP check').click(); md = pg.locator('.md')
    field(md, 'CCP').select_option(label='CCP 1 Dosing'); field(md, 'Measured value *').fill('51.2 g (target 51.0)'); md.get_by_role('button', name='Record').click(); pg.wait_for_function("!document.querySelector('.md')")
    pg.wait_for_selector('.badge >> text=CCP 1/2')
    check(True, 'CCP check from the batch card updates the badge')
    # revise and verification
    pg.get_by_role('button', name='HACCP', exact=True).click(); pg.wait_for_selector('text=HP-001')
    pg.locator('.tabs button', has_text='Verification').click(); pg.get_by_role('button', name='+ Verification').click(); md = pg.locator('.md')
    field(md, 'Kind').select_option('reanalysis'); field(md, 'Plan').select_option(label='HP-001 · Gummies'); field(md, 'What was checked and found *').fill('Full reanalysis, no new hazards')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Verification recorded.')
    check(T['hx_haccp_verifications'][0]['kind'] == 'reanalysis', 'yearly reanalysis recorded')
    pg.locator('.tabs button', has_text='Plans').click(); pg.locator('tr', has_text='HP-001').get_by_role('button', name='Revise').click(); pg.wait_for_selector('.msg >> text=Revision started')
    check(T['hx_haccp_plans'][0]['status'] == 'draft', 'revise puts the plan back to draft')
    pg.screenshot(path=OUT + 'haccp.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
