import re, datetime as dt
exec(open('/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/mock_c.py').read())
errors = []
SH = OUT + 'manual/shots/'
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); TODAY = dt.date.today().isoformat()
ME = 'Sam Salari'
T['hx_profiles'][0]['name'] = ME
L = {'state_id': 'st-mo', 'license_id': 'lic-mo'}
PEOPLE = [{'id': ADMIN, 'name': ME, 'role_ids': [], 'license_ids': []}, {'id': 'u-lee', 'name': 'Lee Park', 'role_ids': [], 'license_ids': ['lic-mo']},
          {'id': 'u-maria', 'name': 'Maria Lopez', 'role_ids': [], 'license_ids': ['lic-mo']}, {'id': 'u-jordan', 'name': 'Jordan Reyes', 'role_ids': [], 'license_ids': ['lic-mo']},
          {'id': 'u-priya', 'name': 'Priya Shah', 'role_ids': [], 'license_ids': ['lic-mo']}, {'id': 'u-marcus', 'name': 'Marcus Bell', 'role_ids': [], 'license_ids': ['lic-mo']}]
for t in ('hx_haccp_team', 'hx_haccp_plans', 'hx_haccp_monitoring', 'hx_haccp_verifications', 'hx_risks', 'hx_risk_reviews', 'hx_changes', 'hx_org_positions', 'hx_objectives',
          'hx_objective_results', 'hx_qms_settings', 'hx_mgmt_reviews', 'hx_verification_plan', 'hx_verification_records', 'hx_equipment_events', 'hx_line_clearances', 'hx_env_tests'): T[t] = []

def bt(i, typ, num, sku, fl, day):
    return {**L, 'id': i, 'batch_type': typ, 'batch_number': num, 'sku_id': None, 'sku': sku, 'flavor_id': None, 'flavor': fl, 'status': 'In Progress', 'data': {'date': day},
            'attachments': [], 'performed_by': 'Maria Lopez', 'created_at': day + 'T13:00:00Z', 'updated_at': day + 'T13:00:00Z', 'voided': False}
T['hx_batches'] = [bt('b1', 'gummies', 'GUM-2610-014', 'Gummies 10pk 100mg', 'Watermelon', '2026-10-14'), bt('b2', 'gummies', 'GUM-2610-015', 'Gummies 10pk 100mg', 'Mango', '2026-10-21'),
                   bt('b3', 'cartridges', 'CART-2610-007', '1g Vape Cartridge', 'Blue Dream', '2026-10-09'), bt('b4', 'cartridges', 'CART-2610-008', '1g Vape Cartridge', 'Sour Diesel', '2026-10-20'),
                   bt('b5', 'butane_extraction', 'BHO-2610-003', 'Live Resin', 'Gelato', '2026-10-06')]
T['hx_haccp_team'] = [
    {**L, 'id': 'ht1', 'name': 'Lee Park', 'user_id': 'u-lee', 'role': 'Team leader', 'department': 'Quality', 'certified': True, 'cert_provider': 'IHA-accredited HACCP course (Basic HACCP, 16 h)', 'cert_date': '2026-03-12', 'cert_files': [], 'active': True, 'created_at': '2026-03-20T10:00:00Z'},
    {**L, 'id': 'ht2', 'name': ME, 'user_id': ADMIN, 'role': 'Backup', 'department': 'Senior management', 'certified': True, 'cert_provider': 'IHA-accredited HACCP course (Basic HACCP, 16 h)', 'cert_date': '2026-03-12', 'cert_files': [], 'active': True, 'created_at': '2026-03-20T10:01:00Z'},
    {**L, 'id': 'ht3', 'name': 'Maria Lopez', 'user_id': 'u-maria', 'role': 'Member', 'department': 'Production', 'certified': False, 'cert_provider': '', 'cert_date': None, 'cert_files': [], 'active': True, 'created_at': '2026-03-20T10:02:00Z'},
    {**L, 'id': 'ht4', 'name': 'Jordan Reyes', 'user_id': 'u-jordan', 'role': 'Member', 'department': 'Sanitation and maintenance', 'certified': False, 'cert_provider': '', 'cert_date': None, 'cert_files': [], 'active': True, 'created_at': '2026-03-20T10:03:00Z'}]

SEQ = {'HP': 0, 'RK': 0, 'CC': 0, 'OBJ': 0, 'MR': 0, 'VS': 0}
REQ = ['prev_actions', 'complaints', 'audits', 'deviations', 'risks', 'csq', 'changes', 'resources']
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def rid(u): return urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0])
def rscore(r):
    r['score'] = r['likelihood'] * r['severity']
    r['residual_score'] = r['residual_likelihood'] * r['residual_severity'] if r.get('residual_likelihood') and r.get('residual_severity') else None
    r['next_review'] = (dt.date.fromisoformat(r['last_reviewed']) + dt.timedelta(days=r.get('review_every_days', 365))).isoformat()
def met(o, v): return v >= o['target'] if o['direction'] == 'up' else v <= o['target']
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if '/rest/v1/rpc/hx_training_roster' in u: return jr(route, PEOPLE)
    # HACCP
    if tbl == 'hx_haccp_plans' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST':
            SEQ['HP'] += 1; p = {**b, 'number': 'HP-%03d' % SEQ['HP'], 'status': 'draft', 'version': 0, 'validated_on': None, 'validated_by': '', 'approved_by': '', 'approved_at': None, 'flow_reviewed_on': None, 'created_at': NOW}; st_new = b.get('status')
        else:
            p = next(x for x in T['hx_haccp_plans'] if x['id'] == rid(u)); old = dict(p); st_new = b.get('status'); p.update(b); p['status'] = old['status']
        if st_new in ('validated', 'active'):
            if len([t for t in T['hx_haccp_team'] if t['certified'] and t.get('active', True)]) < 2: return jr(route, {'message': 'The HACCP team needs one person and a backup certified in an International HACCP Alliance course.'}, 400)
            if not p.get('validation'): return jr(route, {'message': 'Record how the control measures and critical limits were validated (studies, tests, references).'}, 400)
            p['validated_on'] = TODAY; p['validated_by'] = ME
            if st_new == 'active': p['version'] = p.get('version', 0) + 1; p['approved_by'] = ME; p['approved_at'] = NOW; p['flow_reviewed_on'] = TODAY
            p['status'] = st_new
        elif st_new: p['status'] = st_new
        if m == 'POST': T['hx_haccp_plans'].append(p)
        return jr(route, [p], 201 if m == 'POST' else 200)
    if tbl == 'hx_haccp_monitoring' and m == 'POST':
        r = json.loads(request.post_data); p = next(x for x in T['hx_haccp_plans'] if x['id'] == r['plan_id']); c = next(x for x in p['ccps'] if x['id'] == r['ccp_id'])
        r.update({'plan_version': p['version'], 'ccp_name': c['name'], 'checked_at': TODAY + 'T16:40:00Z', 'recorded_by': ME, 'verified_by': '', 'verified_at': None, 'voided': False}); T['hx_haccp_monitoring'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_haccp_monitoring' and m == 'PATCH':
        b = json.loads(request.post_data); r = next(x for x in T['hx_haccp_monitoring'] if x['id'] == rid(u))
        if b.get('verified_at') and (r['checked_by'] == ME or r.get('recorded_by') == ME): return jr(route, {'message': 'Records are verified by someone other than the person who did the check.'}, 400)
        r.update(b); r['verified_by'] = ME; return jr(route, [r])
    if tbl == 'hx_haccp_verifications' and m == 'POST':
        r = json.loads(request.post_data); r.update({'voided': False, 'recorded_by': ME}); T['hx_haccp_verifications'].append(r); return jr(route, [r], 201)
    # risks and changes
    if tbl == 'hx_risks' and m == 'POST':
        r = json.loads(request.post_data)
        if r['likelihood'] * r['severity'] >= 10 and (not r.get('immediate_action') or not r.get('target_date')): return jr(route, {'message': 'A high or critical risk needs an immediate action and a target date'}, 400)
        SEQ['RK'] += 1; r.update({'number': 'RK-%03d' % SEQ['RK'], 'status': 'open', 'last_reviewed': TODAY, 'created_at': NOW, 'created_by': ME, 'residual_likelihood': None, 'residual_severity': None, 'verification': '', 'verified_by': '', 'verified_on': None, 'close_reason': None})
        r.setdefault('review_every_days', 365); rscore(r); T['hx_risks'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_risks' and m == 'PATCH':
        b = json.loads(request.post_data); r = next(x for x in T['hx_risks'] if x['id'] == rid(u))
        if b.get('status') == 'controlled' and not (b.get('verification') and b.get('verified_by') and b.get('residual_likelihood')): return jr(route, {'message': 'Record how the permanent action was verified, by whom and when.'}, 400)
        if b.get('status') == 'closed' and not b.get('close_reason'): return jr(route, {'message': 'Give a reason'}, 400)
        if b.get('status') == 'closed': b['closed_by'] = ME
        r.update(b); rscore(r); return jr(route, [r])
    if tbl == 'hx_risk_reviews' and m == 'POST':
        v = json.loads(request.post_data); v['recorded_by'] = ME; T['hx_risk_reviews'].append(v); r = next(x for x in T['hx_risks'] if x['id'] == v['risk_id'])
        r['last_reviewed'] = max(r['last_reviewed'], v['reviewed_on'])
        if r['status'] == 'controlled':
            r['residual_likelihood'] = v['likelihood']; r['residual_severity'] = v['severity']
            if not v['effective']: r['status'] = 'open'
        else: r['likelihood'] = v['likelihood']; r['severity'] = v['severity']
        rscore(r); return jr(route, [v], 201)
    if tbl == 'hx_changes' and m == 'POST':
        c = json.loads(request.post_data)
        if not any(c['impacts'].values()): return jr(route, {'message': 'Complete the impact assessment'}, 400)
        SEQ['CC'] += 1; c.update({'number': 'CC-2026-%03d' % SEQ['CC'], 'status': 'requested', 'approved_by': '', 'approved_at': None, 'created_at': NOW, 'training_done': False, 'trial_result': '', 'haccp_reviewed': False, 'notified_on': None, 'implemented_on': None, 'effectiveness': '', 'stop_reason': None})
        T['hx_changes'].insert(0, c); return jr(route, [c], 201)
    if tbl == 'hx_changes' and m == 'PATCH':
        b = json.loads(request.post_data); c = next(x for x in T['hx_changes'] if x['id'] == rid(u)); n = {**c, **b}
        if b.get('status') == 'approved': b['approved_by'] = ME; b['approved_at'] = NOW
        if b.get('status') == 'implemented':
            if not n['actions'] or any(not a.get('done') for a in n['actions']): return jr(route, {'message': 'action(s) are not done yet.'}, 400)
            if n['training_required'] and not n['training_done']: return jr(route, {'message': 'Training must be given before the change is used.'}, 400)
        if b.get('status') == 'closed' and not b.get('effectiveness'): return jr(route, {'message': 'Record the effectiveness check'}, 400)
        c.update(b); return jr(route, [c])
    # org chart and objectives
    if tbl == 'hx_org_positions' and m == 'DELETE':
        if any(p.get('reports_to') == rid(u) for p in T['hx_org_positions']): return jr(route, {'message': 'People report to this position. Move them to another position first.'}, 400)
    if tbl == 'hx_qms_settings' and m == 'POST':
        r = json.loads(request.post_data); T['hx_qms_settings'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_objectives' and m == 'POST':
        o = json.loads(request.post_data); SEQ['OBJ'] += 1; o.update({'number': 'OBJ-%03d' % SEQ['OBJ'], 'status': 'active', 'close_note': None, 'created_at': NOW}); o.setdefault('description', ''); o.setdefault('action_plan', ''); o.setdefault('due_on', None)
        T['hx_objectives'].append(o); return jr(route, [o], 201)
    if tbl == 'hx_objectives' and m == 'PATCH':
        b = json.loads(request.post_data); o = next(x for x in T['hx_objectives'] if x['id'] == rid(u))
        if b.get('status') in ('achieved', 'dropped') and not b.get('close_note'): return jr(route, {'message': 'Add a note'}, 400)
        o.update(b); return jr(route, [o])
    if tbl == 'hx_objective_results' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST': r = b
        else: r = next(x for x in T['hx_objective_results'] if x['id'] == rid(u)); r = {**r, **b}
        o = next(x for x in T['hx_objectives'] if x['id'] == r['objective_id']); r['met'] = met(o, r['value']); r['updated_at'] = NOW; r['created_at'] = r.get('created_at', NOW)
        if not r['met'] and not r.get('action'): return jr(route, {'message': 'The target was missed: record the action that will be taken.'}, 400)
        if m == 'POST': T['hx_objective_results'].append(r)
        else: next(x for x in T['hx_objective_results'] if x['id'] == r['id']).update(r)
        return jr(route, [r], 201 if m == 'POST' else 200)
    # management review and verification
    if tbl == 'hx_mgmt_reviews' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST': SEQ['MR'] += 1; r = {**b, 'number': 'MR-2026-%03d' % SEQ['MR'], 'status': 'draft', 'signed_by': '', 'shared_on': None, 'shared_with': '', 'created_at': NOW}; T['hx_mgmt_reviews'].append(r); return jr(route, [r], 201)
        r = next(x for x in T['hx_mgmt_reviews'] if x['id'] == rid(u)); n = {**r, **b}
        if b.get('status') == 'held' and r['status'] != 'held':
            miss = [k for k in REQ if not (n['inputs'].get(k) or {}).get('notes')]
            if miss: return jr(route, {'message': 'Discuss every required input before signing (missing: %s).' % ' '.join(miss)}, 400)
            if not n['decisions']: return jr(route, {'message': 'Record the decisions and conclusions.'}, 400)
            n['signed_by'] = ME; n['signed_at'] = NOW
        r.update(n); return jr(route, [r])
    if tbl == 'hx_verification_plan' and m == 'POST':
        r = json.loads(request.post_data); SEQ['VS'] += 1; r.update({'number': 'VS-%03d' % SEQ['VS'], 'active': True}); T['hx_verification_plan'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_verification_records' and m == 'POST':
        r = json.loads(request.post_data)
        if r['result'] == 'issues' and not (r['findings'] and r['action']): return jr(route, {'message': 'Describe the issues found and the action taken.'}, 400)
        r.update({'voided': False, 'recorded_by': ME, 'created_at': NOW}); T['hx_verification_records'].append(r); return jr(route, [r], 201)
    return _h(route, request)

def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def tall(pg):
    pg.add_style_tag(content='.md{max-height:none !important;overflow:visible !important}.mo{align-items:flex-start !important;overflow:auto !important}')
def mshot(pg, name):
    pg.wait_for_timeout(350); bb = pg.locator('.md').first.bounding_box(); h = int(bb['height']) + 60
    if h > 900: pg.set_viewport_size({'width': 1440, 'height': h}); pg.wait_for_timeout(300)
    pg.locator('.md').first.screenshot(path=SH + name)
    if h > 900: pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(200)
def vshot(pg, name):
    pg.wait_for_timeout(400); pg.screenshot(path=SH + name)
def closemd(pg):
    pg.locator('.mo').first.click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(250)
def menu(pg, name):
    pg.get_by_role('button', name=name, exact=True).first.click()
def reload(pg, name):
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_timeout(300); menu(pg, name); pg.wait_for_timeout(700)

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell')
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_hptab","plans");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    tall(pg)

    # ================= HACCP =================
    menu(pg, 'HACCP'); pg.wait_for_selector('text=No HACCP plans yet')
    def new_plan(name, btype, ingr, allerg, shelf, valid, activate=True, shots=False):
        pg.get_by_role('button', name='+ HACCP plan').click(); md = pg.locator('.md')
        field(md, 'Plan name *').fill(name); field(md, 'Covers batch type').select_option(btype)
        md.get_by_role('button', name='Start from a draft for this batch type').click(); pg.wait_for_timeout(200)
        field(md, 'Ingredients *').fill(ingr); field(md, 'Allergens *').fill(allerg); field(md, 'Shelf life / date').fill(shelf)
        if shots:
            mshot(pg, 'mgmt_haccp_product.png')
            md.locator('.tabs button', has_text='2. Process flow').click(); mshot(pg, 'mgmt_haccp_flow.png')
            md.locator('.tabs button', has_text='4. CCPs').click(); mshot(pg, 'mgmt_haccp_ccps.png')
        md.locator('.tabs button', has_text='5. Validation').click(); field(md, 'How the plan was validated *').fill(valid)
        md.get_by_role('button', name='Activate plan' if activate else 'Save draft').click(); pg.wait_for_selector('.msg >> text=' + ('Activated ' if activate else 'Saved ') + name)
    new_plan('Infused gummies', 'gummies', 'Sugar, corn syrup, pectin, citric acid, natural mango and watermelon flavors, color, cannabis distillate', 'None declared (pectin-based; gelatin-free)', '12 months from the batch date',
             'Homogeneity study on 3 consecutive batches (RSD < 5%); aw limit 0.85 from FDA guidance, confirmed by 3 batch tests (aw 0.72-0.78)', True, True)
    new_plan('Vape cartridges', 'cartridges', 'Cannabis distillate, cannabis-derived terpenes (inhalation grade)', 'None', '12 months', 'Release on a passing state COA is required by 19 CSR 100-1; 3 consecutive batches released on passing COAs')
    new_plan('BHO extraction', 'butane_extraction', 'Cannabis biomass, n-butane / propane (process aid)', 'None expected', '6 months', '', False)
    check(len(T['hx_haccp_plans']) == 3 and T['hx_haccp_plans'][0]['status'] == 'active', 'HACCP: two active plans and one draft')
    gp, cp = T['hx_haccp_plans'][0], T['hx_haccp_plans'][1]
    c1, c2, k1 = gp['ccps'][0], gp['ccps'][1], cp['ccps'][0]
    def mon(i, p, c, bid, val, ok, when, by, ver=None, corr='', disp=''):
        T['hx_haccp_monitoring'].append({**L, 'id': i, 'plan_id': p['id'], 'plan_version': 1, 'ccp_id': c['id'], 'ccp_name': c['name'], 'batch_id': bid, 'checked_at': when, 'checked_by': by, 'value': val,
            'within_limits': ok, 'corrective': corr, 'disposition': disp, 'verified_by': ver or '', 'verified_at': (when[:10] + 'T21:00:00Z') if ver else None, 'recorded_by': by, 'created_at': when, 'voided': False})
    mon('m1', gp, c1, 'b1', '51.1 g (target 51.0 g)', True, '2026-10-14T14:10:00Z', 'Maria Lopez', 'Lee Park')
    mon('m2', gp, c2, 'b1', 'aw 0.78', True, '2026-10-15T15:30:00Z', 'Lee Park', ME)
    mon('m3', cp, k1, 'b3', 'COA TES-26-1182 passed, tag matches', True, '2026-10-12T16:00:00Z', 'Lee Park', ME)
    mon('m4', gp, c1, 'b2', '50.9 g (target 51.0 g)', True, '2026-10-21T13:45:00Z', 'Maria Lopez')
    mon('m5', cp, k1, 'b4', 'COA TES-26-1240: residual solvents FAIL', False, '2026-10-22T17:20:00Z', 'Lee Park', None, 'Batch kept on hold; remediation request filed with DCR; root cause investigation opened', 'held')
    T['hx_haccp_verifications'].append({**L, 'id': 'hv1', 'plan_id': gp['id'], 'kind': 'records_review', 'done_on': '2026-10-16', 'done_by': ME, 'findings': 'Reviewed all CCP 1 and CCP 2 records for 10/01-10/15: complete, signed, within limits', 'result': 'ok', 'files': [], 'voided': False})
    T['hx_haccp_verifications'].append({**L, 'id': 'hv2', 'plan_id': None, 'kind': 'calibration', 'done_on': '2026-10-05', 'done_by': 'Jordan Reyes', 'findings': 'Water activity meter checked against 0.760 aw standard: reads 0.762. Scale SC-02 checked with 50 g certified weight: OK', 'result': 'ok', 'files': [], 'voided': False})
    reload(pg, 'HACCP'); pg.locator('.tabs button', has_text='Plans').click(); pg.wait_for_selector('td >> text=HP-003')
    vshot(pg, 'mgmt_haccp_plans.png')
    pg.get_by_role('button', name='+ CCP check').click(); md = pg.locator('.md')
    field(md, 'CCP').select_option(label='CCP 2 Water activity'); field(md, 'Batch').select_option('b2'); field(md, 'Measured value *').fill('aw 0.89'); field(md, 'Within the critical limit?').select_option('no')
    field(md, 'Corrective action taken *').fill('Trays back to the curing room for 12 h, re-test before packaging'); field(md, 'Product *').select_option('held'); field(md, 'Checked by *').fill('Maria Lopez')
    mshot(pg, 'mgmt_haccp_ccpcheck.png')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=OUT of limits')
    pg.locator('.tabs button', has_text='CCP monitoring').click(); pg.wait_for_selector('td >> text=aw 0.89')
    vshot(pg, 'mgmt_haccp_monitoring.png')
    pg.locator('.tabs button', has_text='Verification').click(); pg.get_by_role('button', name='+ Verification').click(); md = pg.locator('.md')
    field(md, 'Kind').select_option('reanalysis'); field(md, 'Plan').select_option(label='HP-001 · Infused gummies'); field(md, 'Date').fill('2026-10-23')
    field(md, 'What was checked and found *').fill('Team walked the gummy line against the flow diagram; hazards reviewed against the new mango flavor. No new hazards; flow confirmed.')
    mshot(pg, 'mgmt_haccp_verification.png'); closemd(pg)

    # ================= RISK REGISTER =================
    menu(pg, 'Risk Register'); pg.wait_for_selector('text=No risks yet.')
    pg.get_by_role('button', name='Suggested risks').click(); md = pg.locator('.md'); field(md, 'Owner for these risks *').fill('Lee Park')
    md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 12 risks')
    R = {r['title']: r for r in T['hx_risks']}
    own = {'Residual solvent above the limit': 'Maria Lopez', 'Power or HVAC failure': 'Jordan Reyes', 'A rule change is missed': 'Marcus Bell', 'Single-source critical supplier fails': ME, 'Intentional adulteration or theft': ME}
    for t, o in own.items(): R[t]['owner'] = o
    areas = {'Microbial growth in infused edibles': 'Gummy line', 'Residual solvent above the limit': 'Extraction room', 'Unsafe additives in vape cartridges': 'Cartridge filling', 'Heavy metals from cartridge hardware': 'Cartridge filling', 'Allergen cross-contact between runs': 'Kitchen'}
    for t, a in areas.items(): R[t]['area'] = a
    x = R['Microbial growth in infused edibles']; x.update({'status': 'controlled', 'permanent_action': 'Water activity CCP added to the gummy HACCP plan; curing room humidity alarm installed', 'verification': '3 months of aw results all below 0.80; no microbial failures', 'verified_by': 'Lee Park', 'verified_on': '2026-09-18', 'residual_likelihood': 1, 'residual_severity': 4, 'last_reviewed': '2026-09-18'}); rscore(x)
    x = R['Heavy metals from cartridge hardware']; x.update({'status': 'controlled', 'permanent_action': 'Only ceramic hardware from approved supplier with lot heavy-metal reports', 'verification': 'Filled carts from 4 hardware lots tested ND for lead', 'verified_by': 'Lee Park', 'verified_on': '2026-08-28', 'residual_likelihood': 1, 'residual_severity': 4, 'last_reviewed': '2026-08-28'}); rscore(x)
    x = R['Residual solvent above the limit']; x.update({'last_reviewed': '2026-07-10', 'review_every_days': 90}); rscore(x)
    for i, (t, d, by, l, s, ok, nt) in enumerate([('Microbial growth in infused edibles', '2026-09-18', 'Lee Park', 1, 4, True, 'aw trend reviewed, no failures since the CCP was added'),
                                                   ('Heavy metals from cartridge hardware', '2026-08-28', 'Lee Park', 1, 4, True, 'Hardware lot reports on file for every lot received')]):
        T['hx_risk_reviews'].append({**L, 'id': 'rr%d' % i, 'risk_id': R[t]['id'], 'reviewed_on': d, 'reviewed_by': by, 'likelihood': l, 'severity': s, 'effective': ok, 'notes': nt, 'recorded_by': by, 'created_at': d + 'T15:00:00Z'})
    reload(pg, 'Risk Register'); pg.wait_for_selector('text=Heat map (current rating)')
    vshot(pg, 'mgmt_risk_register.png')
    pg.get_by_role('button', name='+ Risk').click(); md = pg.locator('.md')
    field(md, 'Risk *').fill('Glass breakage near the filling line'); field(md, 'Category').select_option('product_safety')
    field(md, 'Hazard - what could go wrong *').fill('Glass fragments in vape cartridges'); field(md, 'Root cause - why it could happen *').fill('Glass jars of distillate opened at the filling line')
    field(md, 'Area / process / product').fill('Cartridge filling'); field(md, 'Found through').select_option('deviation'); md.locator('input[placeholder="e.g. DEV-2026-004"]').fill('DEV-2026-031')
    field(md, 'Likelihood').select_option('4'); field(md, 'Severity').select_option('4')
    field(md, 'Existing controls').fill('Visual inspection at capping'); field(md, 'Immediate action *').fill('Move jar opening to the prep room; glass check at every changeover')
    field(md, 'Permanent action (planned)').fill('Buy distillate in plastic syringes or tins; ban glass from the line'); field(md, 'Permanent fix by *').fill('2026-12-01')
    mshot(pg, 'mgmt_risk_form.png')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved risk RK-013')
    rr = pg.locator('tr', has=pg.locator('b', has_text=re.compile('^Glass breakage near the filling line$')))
    rr.get_by_role('button', name='Controlled').click(); md = pg.locator('.md')
    field(md, 'Permanent action taken *').fill('Distillate now bought in plastic syringes; glass banned from the filling room (SOP-PRD-007 v4)')
    field(md, 'Verification - how you know it works *').fill('Weekly glass audit for 4 weeks: no glass found; 0 foreign-matter complaints')
    field(md, 'Verified on *').fill('2026-10-23')
    mshot(pg, 'mgmt_risk_controlled.png')
    md.get_by_role('button', name='Mark controlled').click(); pg.wait_for_selector('.msg >> text=RK-013 is controlled')
    rr = pg.locator('tr', has=pg.locator('b', has_text=re.compile('^Residual solvent above the limit$')))
    rr.get_by_role('button', name='Review').click(); md = pg.locator('.md')
    field(md, 'Notes').fill('Reviewed purge records Jul-Oct, 1 failed residual solvent COA (CART-2610-008 input). Controls still working; purge time extended per CC-2026-002.')
    mshot(pg, 'mgmt_risk_review.png')
    md.get_by_role('button', name='Record review').click(); pg.wait_for_selector('.msg >> text=Review recorded')

    # ================= CHANGE CONTROL =================
    def ch(i, num, title, typ, status, req_on, by, desc, why, imp, **kw):
        c = {**L, 'id': i, 'number': num, 'title': title, 'change_type': typ, 'product': kw.get('product', ''), 'description': desc, 'reason': why, 'requested_by': by, 'requested_on': req_on, 'target_date': kw.get('target'),
             'impacts': imp, 'impact_notes': kw.get('notes', ''), 'risk_level': kw.get('risk', 'medium'), 'risk_id': None, 'sop_ids': [], 'plan_ids': kw.get('plans', []), 'course_ids': [],
             'actions': kw.get('actions', []), 'training_required': kw.get('tr', False), 'training_done': kw.get('trd', False), 'training_note': kw.get('trn', ''), 'trial_required': kw.get('tri', False), 'trial_result': kw.get('trr', ''), 'trial_note': kw.get('trin', ''),
             'haccp_reviewed': kw.get('hr', False), 'notify': kw.get('notify', {}), 'notified_on': kw.get('non'), 'notified_note': kw.get('nnote', ''), 'status': status,
             'approved_by': ME if status not in ('requested', 'rejected') else '', 'approved_at': kw.get('app'), 'approval_note': kw.get('appn', ''), 'implemented_on': kw.get('impl'), 'effectiveness': kw.get('eff', ''),
             'closed_by': ME if status in ('closed', 'rejected') else '', 'closed_at': kw.get('closed'), 'stop_reason': kw.get('stop'), 'files': [], 'notes': '', 'created_at': req_on + 'T12:00:00Z'}
        return c
    A = lambda w, who, due, done=None: {'id': 'a' + w[:4], 'what': w, 'who': who, 'due': due, 'done': bool(done), 'done_on': done}
    T['hx_changes'] = [
        ch('cc5', 'CC-2026-005', 'Switch exit bags to a non child-resistant supplier', 'material', 'rejected', '2026-10-08', 'Marcus Bell', 'Buy exit bags from a cheaper supplier', 'Cost', {'labels': True, 'license': True}, stop='Missouri requires child-resistant exit packaging; not acceptable', closed='2026-10-09T15:00:00Z'),
        ch('cc4', 'CC-2026-004', 'Pre-roll filling SOP: add a cone weight check', 'document', 'requested', '2026-10-19', 'Priya Shah', 'Add a 10-cone weight check every hour to SOP-PRD-012', 'Two complaints about light pre-rolls', {'sops': True, 'training': True}, tr=True),
        ch('cc3', 'CC-2026-003', 'Silicone gummy molds on line 2', 'equipment', 'approved', '2026-10-02', 'Maria Lopez', 'Replace starch trays with food-grade silicone molds on line 2', 'Faster release, less starch dust', {'haccp': True, 'training': True, 'equipment': True, 'license': True},
           product='Gummies 10pk 100mg', plans=[], tr=True, trn='Line 2 crew on mold handling and cleaning', notify={'regulator': True}, app='2026-10-06T16:00:00Z',
           actions=[A('Buy and validate molds (3 trial batches)', 'Maria Lopez', '2026-10-20', '2026-10-18'), A('Update the sanitation SOP for molds', 'Jordan Reyes', '2026-10-30')]),
        ch('cc2', 'CC-2026-002', 'Longer purge time for BHO live resin', 'process', 'implemented', '2026-09-03', 'Maria Lopez', 'Purge 72 h instead of 48 h at 100 F', 'Residual solvent failure on BHO-2609-002', {'haccp': True, 'sops': True, 'specs': True},
           hr=True, app='2026-09-04T14:00:00Z', impl='2026-09-15', actions=[A('Update purge SOP', 'Maria Lopez', '2026-09-10', '2026-09-09'), A('Revalidate CCP 1 limits', 'Lee Park', '2026-09-14', '2026-09-14')]),
        ch('cc1', 'CC-2026-001', 'Approve a second terpene supplier', 'material', 'closed', '2026-08-11', ME, 'Add a second inhalation-grade terpene supplier', 'Single source risk (RK-012)', {'suppliers': True, 'specs': True},
           app='2026-08-12T14:00:00Z', impl='2026-08-29', eff='Two orders received with COAs; blends matched spec in 3 batches', closed='2026-09-30T15:00:00Z', actions=[A('Supplier approval and COA review', 'Lee Park', '2026-08-25', '2026-08-24')])]
    SEQ['CC'] = 5
    reload(pg, 'Change Control'); pg.wait_for_selector('td >> text=CC-2026-003')
    vshot(pg, 'mgmt_change_list.png')
    pg.get_by_role('button', name='+ Change').click(); md = pg.locator('.md')
    field(md, 'Change *').fill('Add a mango flavor to the 10-pack gummies'); field(md, 'Type').select_option('product')
    field(md, 'What changes *').fill('New natural mango flavor and orange color in the gummy formulation'); field(md, 'Why *').fill('Dispensary demand; replaces the discontinued peach SKU')
    field(md, 'Product(s)').fill('Gummies 10pk 100mg'); field(md, 'Wanted by').fill('2026-11-30')
    for k in ('Allergens', 'Labels and packaging', 'Product specs / formulation', 'HACCP plan / flow diagram'):
        md.locator('label.ck', has_text=re.compile('^' + re.escape(k) + '$')).locator('input').check()
    field(md, 'How it affects them').fill('New flavor supplier spec and allergen review; new label artwork; formulation; hazard review of the new ingredient')
    md.locator('input[placeholder="What the trial must show"]').fill('3 batches within potency spec and aw below 0.85')
    md.locator('label.ck', has_text='Customers / dispensaries').locator('input').check()
    md.get_by_role('button', name='+ Action').click(); md.locator('input[placeholder="Action"]').last.fill('Approve the flavor supplier and get the allergen statement'); md.locator('input[placeholder="Who"]').last.fill('Lee Park')
    md.get_by_role('button', name='+ Action').click(); md.locator('input[placeholder="Action"]').last.fill('New label template with the flavor and allergens'); md.locator('input[placeholder="Who"]').last.fill('Marcus Bell')
    mshot(pg, 'mgmt_change_form.png')
    md.get_by_role('button', name='Request change').click(); pg.wait_for_selector('.msg >> text=Requested CC-2026-006')
    pg.locator('tr', has_text='CC-2026-003').get_by_role('button', name='Work').click(); md = pg.locator('.md')
    mshot(pg, 'mgmt_change_work.png'); closemd(pg)
    pg.locator('tr', has_text='CC-2026-006').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.locator('input[placeholder="Conditions, or why it is acceptable"]').fill('Approved; trial batches must pass before the SKU is switched on')
    mshot(pg, 'mgmt_change_approve.png'); closemd(pg)

    # ================= ORG CHART =================
    def pos(i, t, p, to, dep, resp, roles, bk='', s=0): return {**L, 'id': i, 'title': t, 'person_name': p, 'reports_to': to, 'department': dep, 'responsibilities': resp, 'quality_roles': roles, 'backup_name': bk, 'sort': s, 'created_at': '2026-09-01T12:00:00Z'}
    T['hx_org_positions'] = [
        pos('op1', 'General Manager', ME, None, 'Management', 'Runs the facility; provides resources for the quality system; chairs the management review', ['Senior management'], 'Lee Park'),
        pos('op2', 'Quality Manager', 'Lee Park', 'op1', 'Quality', 'CSQ practitioner; owns the QMS, CAPA, HACCP and internal audits; releases batches', ['Quality / CSQ lead', 'HACCP team leader', 'Recall coordinator'], 'Maria Lopez', 1),
        pos('op3', 'Production Manager', 'Maria Lopez', 'op1', 'Production', 'Plans and runs production; batch records; line clearance', ['Quality backup', 'Food safety / product defense'], 'Jordan Reyes', 2),
        pos('op4', 'Compliance Specialist', 'Marcus Bell', 'op1', 'Compliance', 'METRC, state reporting, label review, rule changes', ['Regulatory contact (state / METRC)'], ME, 3),
        pos('op5', 'QA Technician', 'Priya Shah', 'op2', 'Quality', 'Sampling, COA review, CCP record review, training records', ['Training coordinator', 'Internal auditor'], 'Lee Park'),
        pos('op6', 'Production Lead', 'Jordan Reyes', 'op3', 'Production', 'Leads the gummy and cartridge lines; sanitation and changeovers', ['Sanitation lead'], 'Maria Lopez'),
        pos('op7', 'Maintenance Technician', '', 'op3', 'Production', 'Preventive maintenance and calibration of scales and meters', ['Maintenance / calibration'], 'Jordan Reyes', 1)]
    reload(pg, 'Org Chart'); pg.wait_for_selector('.card svg rect')
    vshot(pg, 'mgmt_org_chart.png')
    pg.locator('tr', has=pg.locator('b', has_text=re.compile('^Quality Manager$'))).get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    mshot(pg, 'mgmt_org_position.png'); closemd(pg)

    # ================= QUALITY OBJECTIVES =================
    T['hx_sops'] = [{**L, 'id': 'sp1', 'license_ids': ['lic-mo'], 'sop_number': 'SOP-QA-001', 'title': 'Safety, Quality and Compliance Policy', 'version': '3', 'status': 'published'},
                    {**L, 'id': 'sp2', 'license_ids': ['lic-mo'], 'sop_number': 'SOP-PRD-012', 'title': 'Pre-roll filling', 'version': '2', 'status': 'published'}]
    T['hx_qms_settings'] = [{**L, 'policy_sop_id': 'sp1', 'policy_note': 'Signed by all staff at hire and on each new version; posted in the break room; reviewed every year in the management review'}]
    T['hx_capas'] = [{**L, 'id': 'ca%d' % i, 'number': 'CAPA-2026-%03d' % (10 + i), 'title': t, 'status': 'closed', 'closed_at': c + 'T15:00:00Z', 'due_date': d, 'effectiveness_rating': 'effective'}
                     for i, (t, c, d) in enumerate([('Label misprint on gummies', '2026-09-08', '2026-09-10'), ('Scale out of calibration', '2026-09-12', '2026-09-15'), ('Light pre-rolls', '2026-09-22', '2026-09-18'), ('Missing sanitation signature', '2026-09-26', '2026-09-30')])]
    T['hx_capas'] += [{**L, 'id': 'ca9', 'number': 'CAPA-2026-019', 'title': 'Residual solvent failure CART-2610-008', 'status': 'open', 'closed_at': None, 'due_date': '2026-11-21', 'effectiveness_rating': None},
                      {**L, 'id': 'ca8', 'number': 'CAPA-2026-018', 'title': 'Pest trap map out of date', 'status': 'in_progress', 'closed_at': None, 'due_date': '2026-10-20', 'effectiveness_rating': None}]
    def obj(i, n, name, cat, metric, unit, dirn, tgt, freq, owner, desc='', plan=''):
        return {**L, 'id': i, 'number': n, 'name': name, 'category': cat, 'description': desc, 'metric': metric, 'unit': unit, 'direction': dirn, 'target': tgt, 'frequency': freq, 'owner': owner, 'start_on': '2026-04-01', 'due_on': None, 'action_plan': plan, 'status': 'active', 'close_note': None, 'created_at': '2026-04-01T12:00:00Z'}
    T['hx_objectives'] = [obj('ob1', 'OBJ-001', 'CAPAs closed on time', 'quality', 'capa_on_time', '%', 'up', 90, 'monthly', 'Lee Park', 'Policy: we fix problems at the root, on time'),
                          obj('ob2', 'OBJ-002', 'Deviations per month', 'quality', 'deviations', 'deviations', 'down', 4, 'monthly', 'Maria Lopez'),
                          obj('ob3', 'OBJ-003', 'CCP checks within critical limits', 'food_safety', 'ccp_ok', '%', 'up', 98, 'monthly', 'Lee Park'),
                          obj('ob4', 'OBJ-004', 'Batch tests passed first time', 'quality', 'tests_pass', '%', 'up', 95, 'monthly', 'Lee Park'),
                          obj('ob5', 'OBJ-005', 'Complaints per quarter', 'customer', 'complaints', 'complaints', 'down', 3, 'quarterly', 'Marcus Bell'),
                          obj('ob6', 'OBJ-006', 'On-time delivery to dispensaries', 'customer', 'manual', '%', 'up', 95, 'quarterly', ME, '', 'Weekly shipping plan with the sales team')]
    SEQ['OBJ'] = 6
    def res(o, p, v, mt, act=''): T['hx_objective_results'].append({**L, 'id': 'or-%s-%s' % (o, p), 'objective_id': o, 'period': p, 'value': v, 'met': mt, 'auto': True, 'comment': '', 'action': act, 'recorded_by': 'Lee Park', 'created_at': p[:7] + '-28T12:00:00Z' if '-Q' not in p else '2026-07-05T12:00:00Z', 'updated_at': '2026-10-05T12:00:00Z'})
    for p, v in (('2026-05', 100), ('2026-06', 86), ('2026-07', 92), ('2026-08', 95)): res('ob1', p, v, v >= 90, 'CAPA review added to the weekly production meeting' if v < 90 else '')
    for p, v in (('2026-05', 3), ('2026-06', 5), ('2026-07', 2), ('2026-08', 4), ('2026-09', 3)): res('ob2', p, v, v <= 4, 'Line clearance retraining for the cartridge crew' if v > 4 else '')
    for p, v in (('2026-05', 100), ('2026-06', 100), ('2026-07', 97.5), ('2026-08', 100), ('2026-09', 100)): res('ob3', p, v, v >= 98, 'Curing room humidity alarm installed' if v < 98 else '')
    for p, v in (('2026-05', 96), ('2026-06', 100), ('2026-07', 94), ('2026-08', 97), ('2026-09', 92)): res('ob4', p, v, v >= 95, 'Residual solvent investigation (CAPA-2026-019); purge time extended' if v < 95 else '')
    for p, v in (('2026-Q1', 2), ('2026-Q2', 4), ('2026-Q3', 2)): res('ob5', p, v, v <= 3, 'Pre-roll weight check added (CC-2026-004)' if v > 3 else '')
    for p, v in (('2026-Q2', 93), ('2026-Q3', 97)): res('ob6', p, v, v >= 95, 'Weekly shipping plan with sales' if v < 95 else '')
    reload(pg, 'Quality Objectives'); pg.wait_for_selector('text=SOP-QA-001 Safety, Quality and Compliance Policy v3')
    vshot(pg, 'mgmt_objectives_board.png')
    pg.locator('.card', has=pg.locator('b', has_text=re.compile('^CAPAs closed on time$'))).first.get_by_role('button', name=re.compile('^Record')).click(); md = pg.locator('.md')
    md.locator('text=3 of 4 CAPAs closed on time').wait_for()
    field(md, 'Action to get back on target *').fill('Weekly CAPA due-date review in the Monday production meeting')
    mshot(pg, 'mgmt_objectives_result.png')
    md.get_by_role('button', name='Record result').click(); pg.wait_for_selector('.msg >> text=Sep 2026: 75% - target missed.')
    pg.get_by_role('button', name='+ Objective').click(); md = pg.locator('.md')
    field(md, 'Objective *').fill('Line clearance before every batch'); field(md, 'Category').select_option('food_safety'); field(md, 'Measured by').select_option('line_clear')
    field(md, 'Target *').fill('100'); field(md, 'Reach by').fill('2026-12-31')
    field(md, 'Why it matters (link to the quality policy)').fill('Policy: no product is made on a line that has not been cleared')
    field(md, 'Plan to reach it').fill('Supervisor sign-off on the line clearance before the batch record opens')
    mshot(pg, 'mgmt_objectives_form.png'); closemd(pg)

    # ================= MANAGEMENT REVIEW =================
    T['hx_complaints'] = [{**L, 'id': 'co%d' % i, 'number': 'CMP-2026-%03d' % i, 'received_on': d, 'category': c, 'type': 'complaint', 'status': s} for i, (d, c, s) in
                          enumerate([('2026-02-11', 'Product quality', 'closed'), ('2026-05-02', 'Packaging', 'closed'), ('2026-06-19', 'Product quality', 'closed'), ('2026-08-30', 'Potency', 'closed'), ('2026-10-17', 'Product quality', 'investigating')], 1)]
    T['hx_deviations'] = [{**L, 'id': 'dv%d' % i, 'number': 'DEV-2026-%03d' % (20 + i), 'title': 'x', 'created_at': d + 'T10:00:00Z', 'category': c, 'priority': p, 'status': 'closed' if i < 5 else 'open'} for i, (d, c, p) in
                          enumerate([('2026-03-04', 'Sanitation', 'minor'), ('2026-05-18', 'Labeling', 'major'), ('2026-06-07', 'Process / procedure', 'minor'), ('2026-08-21', 'Equipment', 'minor'), ('2026-10-22', 'Process / procedure', 'critical')], 1)]
    T['hx_audits'] = [{**L, 'id': 'au1', 'audit_date': '2026-09-15', 'audit_type': 'internal', 'status': 'completed'}, {**L, 'id': 'au2', 'audit_date': '2026-04-09', 'audit_type': 'regulatory', 'status': 'closed'}]
    T['hx_audit_findings'] = [{**L, 'id': 'af1', 'severity': 'minor', 'status': 'open', 'due_date': '2026-11-15'}]
    T['hx_conformance'] = [{**L, 'id': 'cf%d' % i, 'standard_id': 's1', 'clause_id': 'c%d' % i, 'status': s} for i, s in enumerate(['Conforming'] * 38 + ['Partial'] * 6 + ['Not conforming'] * 1 + ['Not applicable'] * 3)]
    T['hx_suppliers'] = [{**L, 'license_ids': ['lic-mo'], 'id': 'su%d' % i, 'name': n, 'status': s, 'next_review': nr, 'last_review': lr} for i, (n, s, nr, lr) in
                         enumerate([('Ceramic hardware supplier', 'approved', '2027-03-01', '2026-03-01'), ('Terpene supplier A', 'approved', '2027-08-24', '2026-08-24'), ('Packaging supplier', 'conditional', '2026-10-01', '2025-10-01')])]
    T['hx_mgmt_reviews'] = [{**L, 'id': 'mr0', 'number': 'MR-2025-001', 'meeting_date': '2025-10-20', 'period_from': '2024-10-21', 'period_to': '2025-10-20', 'chair': ME, 'attendees': 'Sam Salari (GM), Lee Park (QA), Maria Lopez (Production)',
                             'inputs': {k: {'data': '', 'notes': 'Reviewed'} for k in REQ}, 'decisions': 'System suitable; start CSQ Level 3', 'resources': 'Hire a QA technician', 'status': 'held', 'signed_by': ME, 'signed_at': '2025-10-20T20:00:00Z',
                             'actions': [{'id': 'x1', 'what': 'Hire a QA technician', 'who': ME, 'due': '2026-01-31', 'done': True, 'done_on': '2026-01-12'}, {'id': 'x2', 'what': 'Build the HACCP plans for gummies and cartridges', 'who': 'Lee Park', 'due': '2026-06-30', 'done': True, 'done_on': TODAY},
                                         {'id': 'x3', 'what': 'Approve a second hardware supplier', 'who': 'Marcus Bell', 'due': '2026-09-30', 'done': False}],
                             'next_review': '2026-10-20', 'shared_with': 'All managers', 'shared_on': '2025-10-24', 'files': [], 'created_at': '2025-10-20T15:00:00Z'}]
    menu(pg, 'Management Review'); pg.wait_for_selector('td >> text=MR-2025-001')
    pg.get_by_role('button', name='+ Management review').click(); md = pg.locator('.md'); md.locator('text=Filled from Hendrix records').wait_for()
    field(md, 'Period from').fill('2025-10-21'); field(md, 'Period to').fill('2026-10-23'); field(md, 'Meeting date').fill('2026-10-23')
    md.get_by_role('button', name='Fill from Hendrix').click(); md.locator('text=Filled from Hendrix records for 2025-10-21').wait_for()
    field(md, 'Attendees *').fill('Sam Salari (GM), Lee Park (QA), Maria Lopez (Production), Marcus Bell (Compliance)')
    NOTES = {'Actions from the last review': 'Second hardware supplier still open: carried over, new due date 12/31.',
             'Complaints and customer feedback': 'Product quality complaints down from last year; light pre-rolls fixed by CC-2026-004.',
             'Internal, external and regulatory audits': 'Internal audit 9/15: 1 minor finding open. DCR inspection 4/9: no findings.',
             'Deviations and corrective actions (CAPA)': 'Critical deviation 10/22 (residual solvent) under CAPA-2026-019. One CAPA overdue: escalate.',
             'Risks and opportunities': 'Residual solvent risk stays high until the purge revalidation is verified.',
             'CSQ conformance': '6 partial clauses: plan to close before the Level 3 audit.',
             'Changes that could affect the system': 'Silicone molds and longer purge reviewed against HACCP. New mango SKU pending.',
             'Resources (people, equipment, facility, budget)': 'Second extraction tech and a backup water activity meter approved.'}
    for k, v in NOTES.items(): md.locator('.card', has=pg.locator('b', has_text=re.compile('^' + re.escape(k) + r'( \*)?$'))).first.locator('textarea').nth(1).fill(v)
    field(md, 'Decisions and conclusions (is the system suitable, adequate and effective?) *').fill('The system is suitable, adequate and effective. Go for the CSQ Level 3 audit in Q1 2027.')
    field(md, 'Resource needs').fill('Second extraction technician; backup aw meter'); field(md, 'Next review (within 12 months)').fill('2027-10-15')
    md.get_by_role('button', name='+ Action').click(); md.locator('input[placeholder="Action"]').last.fill('Hire a second extraction technician'); md.locator('input[placeholder="Who"]').last.fill(ME)
    md.get_by_role('button', name='+ Action').click(); md.locator('input[placeholder="Action"]').last.fill('Close the 6 partial CSQ clauses'); md.locator('input[placeholder="Who"]').last.fill('Lee Park')
    mshot(pg, 'mgmt_review_form.png')
    md.get_by_role('button', name='Sign as held').click(); pg.wait_for_selector('.msg >> text=Signed management review MR-2026-001.')
    vshot(pg, 'mgmt_review_list.png')
    pg.locator('tr', has_text='MR-2026-001').get_by_role('button', name='Follow-up').click(); md = pg.locator('.md')
    md.locator('input[type=checkbox][title=Done]').last.check(); field(md, 'Minutes shared with').fill('All managers; summary posted in the break room'); field(md, 'Shared on').fill(TODAY)
    mshot(pg, 'mgmt_review_followup.png')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved MR-2026-001.')

    # ================= VERIFICATION SCHEDULE =================
    T['hx_facility_log'] = [{**L, 'id': 'fl1', 'log_type': 'sanitation', 'created_at': '2026-10-22T14:00:00Z', 'data': {'verified_by': 'Jordan Reyes'}, 'voided': False, 'result': 'Pass'}]
    T['hx_equipment_events'] = [{**L, 'id': 'ee1', 'kind': 'calibration', 'done_on': '2026-10-05', 'voided': False}]
    T['hx_line_clearances'] = [{**L, 'id': 'lc1', 'checked_at': '2026-09-14T13:00:00Z', 'verified_by': 'Maria Lopez', 'voided': False, 'result': 'cleared', 'batch_id': 'b1'}]
    T['hx_env_tests'] = [{**L, 'id': 'et1', 'sampled_on': '2026-03-04', 'voided': False, 'result': 'pass'}]
    menu(pg, 'Verification Schedule'); pg.wait_for_selector('text=No verification schedule yet.')
    pg.get_by_role('button', name='Suggested schedule').click(); md = pg.locator('.md'); field(md, 'Who does them *').fill('Lee Park')
    md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 13 verification activities.')
    VP = {p['activity']: p for p in T['hx_verification_plan']}
    VP['Scale and equipment calibration']['responsible'] = 'Jordan Reyes'; VP['Sanitation records reviewed and signed']['responsible'] = 'Maria Lopez'; VP['Management review']['responsible'] = ME
    T['hx_verification_records'] += [{**L, 'id': 'vr1', 'plan_id': VP['Pest control service reports reviewed']['id'], 'done_on': '2026-10-02', 'done_by': 'Priya Shah', 'result': 'ok', 'findings': 'October service report reviewed; no activity in interior traps', 'action': '', 'files': [], 'voided': False, 'recorded_by': 'Priya Shah', 'created_at': '2026-10-02T15:00:00Z'},
                                     {**L, 'id': 'vr2', 'plan_id': VP['Labels checked against the batch']['id'], 'done_on': '2026-09-10', 'done_by': 'Priya Shah', 'result': 'ok', 'findings': '5 batch labels checked against COA and formulation', 'action': '', 'files': [], 'voided': False, 'recorded_by': 'Priya Shah', 'created_at': '2026-09-10T15:00:00Z'},
                                     {**L, 'id': 'vr3', 'plan_id': VP['Labels checked against the batch']['id'], 'done_on': '2026-08-11', 'done_by': 'Priya Shah', 'result': 'issues', 'findings': 'Watermelon gummy label showed the old THC per serving', 'action': 'Template corrected and 2 rolls reprinted', 'files': [], 'voided': False, 'recorded_by': 'Priya Shah', 'created_at': '2026-08-11T15:00:00Z'}]
    reload(pg, 'Verification Schedule'); pg.wait_for_selector('td >> text=VS-013'); pg.wait_for_selector('text=from Sanitation log')
    vshot(pg, 'mgmt_verification_schedule.png')
    pg.locator('tr', has=pg.locator('b', has_text=re.compile('^Labels checked against the batch$'))).get_by_role('button', name='Record').click(); md = pg.locator('.md')
    field(md, 'By *').fill('Priya Shah'); field(md, 'Result').select_option('issues')
    field(md, 'Findings *').fill('CART-2610-008 label lists the old terpene blend name'); field(md, 'Action taken *').fill('Label template updated; 120 labels reprinted and swapped before release')
    mshot(pg, 'mgmt_verification_record.png')
    md.get_by_role('button', name='Record', exact=True).click(); pg.wait_for_selector('.msg >> text=Recorded: Labels checked against the batch.')
    pg.locator('tr', has=pg.locator('b', has_text=re.compile('^Labels checked against the batch$'))).get_by_role('button', name='History').click(); md = pg.locator('.md')
    md.locator('text=Action: Template corrected').wait_for()
    mshot(pg, 'mgmt_verification_history.png'); closemd(pg)
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
