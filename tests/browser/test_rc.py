import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'); TODAY = dt.date.today().isoformat()
for t in ('hx_risks', 'hx_risk_reviews', 'hx_changes'): T[t] = []
SEQ = {'RK': 0, 'CC': 0}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def rscore(r):
    r['score'] = r['likelihood'] * r['severity']
    r['residual_score'] = r['residual_likelihood'] * r['residual_severity'] if r.get('residual_likelihood') and r.get('residual_severity') else None
    r['next_review'] = (dt.date.fromisoformat(r['last_reviewed']) + dt.timedelta(days=r.get('review_every_days', 365))).isoformat()
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_risks' and m == 'POST':
        r = json.loads(request.post_data)
        if r['likelihood'] * r['severity'] >= 10 and (not r.get('immediate_action') or not r.get('target_date')): return jr(route, {'message': 'A high or critical risk needs an immediate action and a target date'}, 400)
        SEQ['RK'] += 1; r.update({'number': 'RK-%03d' % SEQ['RK'], 'status': 'open', 'last_reviewed': TODAY, 'created_at': NOW, 'created_by': 'Sam', 'residual_likelihood': None, 'residual_severity': None, 'verification': '', 'verified_by': '', 'verified_on': None, 'close_reason': None})
        r.setdefault('review_every_days', 365); rscore(r); T['hx_risks'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_risks' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_risks'] if x['id'] == cid)
        if b.get('status') == 'controlled' and not (b.get('verification') and b.get('verified_by') and b.get('residual_likelihood')): return jr(route, {'message': 'Record how the permanent action was verified'}, 400)
        if b.get('status') == 'closed' and not b.get('close_reason'): return jr(route, {'message': 'Give a reason'}, 400)
        r.update(b); rscore(r); return jr(route, [r])
    if tbl == 'hx_risk_reviews' and m == 'POST':
        v = json.loads(request.post_data); T['hx_risk_reviews'].append(v); r = next(x for x in T['hx_risks'] if x['id'] == v['risk_id'])
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
        T['hx_changes'].append(c); return jr(route, [c], 201)
    if tbl == 'hx_changes' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); c = next(x for x in T['hx_changes'] if x['id'] == cid); n = {**c, **b}
        if b.get('status') == 'approved': b['approved_by'] = 'Sam'; b['approved_at'] = NOW
        if b.get('status') == 'implemented':
            if not n['actions'] or any(not a.get('done') for a in n['actions']): return jr(route, {'message': 'actions not done'}, 400)
            if n['training_required'] and not n['training_done']: return jr(route, {'message': 'Training must be given before the change is used.'}, 400)
            if n['impacts'].get('haccp') and not n['haccp_reviewed']: return jr(route, {'message': 'HACCP is affected'}, 400)
            if n['notify'].get('regulator') and not n['notified_on']: return jr(route, {'message': 'Record when the regulator was told'}, 400)
        if b.get('status') == 'closed' and not b.get('effectiveness'): return jr(route, {'message': 'Record the effectiveness check'}, 400)
        c.update(b); return jr(route, [c])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def rrow(pg, title): return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(title) + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.wait_for_selector('.card.gold >> text=Risk and change')
    check(pg.locator('.card.gold', has_text='Risk and change').locator('text=No risks assessed').count() == 1, 'dashboard: no risks assessed yet')
    pg.get_by_role('button', name='Risk Register').click(); pg.wait_for_selector('text=No risks yet.')
    pg.get_by_role('button', name='Suggested risks').click(); md = pg.locator('.md')
    check(md.locator('text=Residual solvent above the limit').count() == 1 and md.locator('text=Pesticide drift').count() == 0, 'manufacturing suggestions (no cultivation site risks)')
    md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 12 risks')
    check(len(T['hx_risks']) == 12 and all(r['owner'] == 'Sam' for r in T['hx_risks']), '12 suggested risks added with an owner')
    hi = [r for r in T['hx_risks'] if r['score'] >= 10]
    check(all(r['target_date'] and r['immediate_action'] for r in hi), 'high suggested risks got an immediate action and a 90-day target')
    check(pg.locator('.card.gold', has_text='High or critical').locator('.v').inner_text() == str(len(hi)), 'stat: high / critical count')
    check(pg.locator('.badge', has_text='CSQ 1.9').count() == 1 and pg.locator('text=CSQ 3A.1.2').count() == 0, 'category list shows CSQ links, no site risk on manufacturing')
    # new risk
    pg.get_by_role('button', name='+ Risk').click(); md = pg.locator('.md')
    field(md, 'Risk *').fill('Glass breakage near the filling line'); field(md, 'Hazard - what could go wrong').fill('Glass in cartridges')
    field(md, 'Root cause - why it could happen').fill('Glass jars of distillate opened at the line'); field(md, 'Likelihood').select_option('4'); field(md, 'Severity').select_option('4')
    check(md.locator('.badge', has_text='Critical 16').count() == 1, 'live rating badge: critical 16')
    check(field(md, 'Review every').input_value() == '90', 'critical risk defaults to a 3-month review')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md .msg.err >> text=immediate action')
    field(md, 'Immediate action').fill('Move jar opening to the prep room'); field(md, 'Permanent fix by').fill('2026-12-01')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved risk RK-013')
    # heat map filter
    pg.locator('button[title*="4 Likely x 4 Major"]').click(); pg.wait_for_timeout(200)
    check(pg.locator('tbody tr').count() == 1 and rrow(pg, 'Glass breakage near the filling line').count() == 1, 'heat map cell filters the register')
    pg.get_by_role('button', name='Clear heat map filter').click()
    rrow(pg, 'Glass breakage near the filling line').get_by_role('button', name='Controlled').click(); md = pg.locator('.md')
    field(md, 'Permanent action taken').fill('Distillate moved to plastic, glass banned from line'); md.get_by_role('button', name='Mark controlled').click(); pg.wait_for_selector('.md .msg.err >> text=verified')
    field(md, 'Verification - how you know it works').fill('Glass audit x4 weeks, none found'); md.get_by_role('button', name='Mark controlled').click(); pg.wait_for_selector('.msg >> text=RK-013 is controlled')
    r13 = next(r for r in T['hx_risks'] if r['number'] == 'RK-013')
    check(r13['status'] == 'controlled' and r13['residual_score'] == 8 and rrow(pg, 'Glass breakage near the filling line').locator('text=was 16').count() == 1, 'controlled with residual rating 8 (was 16)')
    rrow(pg, 'Glass breakage near the filling line').get_by_role('button', name='Review').click(); md = pg.locator('.md')
    md.locator('label.ck', has_text='Controls are in place').locator('input').uncheck(); check(md.locator('text=The risk goes back to Open').count() == 1, 'review warns the risk re-opens')
    md.get_by_role('button', name='Record review').click(); pg.wait_for_selector('.md .msg.err >> text=describe what will be done')
    field(md, 'Notes').fill('Glass jar found at line on 10/20'); md.get_by_role('button', name='Record review').click(); pg.wait_for_selector('.msg >> text=re-opened')
    check(r13['status'] == 'open' and len(T['hx_risk_reviews']) == 1, 'ineffective review re-opens the risk')
    rrow(pg, 'Glass breakage near the filling line').get_by_role('link').first.click() if False else pg.locator('a', has_text='Glass breakage near the filling line').click()
    md = pg.locator('.md'); check(md.locator('text=Glass jar found at line').count() == 1 and md.locator('text=Reviews (routine surveillance)').count() == 1, 'risk detail shows the review history')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print register').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Risk register' in html and 'CSQ 5.1.6' in html and 'Glass breakage' in html, 'printable risk register'); w.close()
    rrow(pg, 'Power or HVAC failure').get_by_role('button', name='Close').click(); md = pg.locator('.md')
    md.locator('textarea').fill('Moved to a facility with backup power'); md.get_by_role('button', name='Close risk').click(); pg.wait_for_selector('.msg >> text=Closed RK-010')
    check(rrow(pg, 'Power or HVAC failure').count() == 0, 'closed risk leaves the live list')
    pg.screenshot(path=OUT + 'risks.png', full_page=True)
    # change control
    pg.locator('.tabs').get_by_role('button', name='Change control').click(); pg.wait_for_selector('text=No changes yet.')
    pg.get_by_role('button', name='+ Change').click(); md = pg.locator('.md')
    field(md, 'Change *').fill('Silicone gummy molds on line 2'); field(md, 'What changes').fill('Replace starch trays with silicone molds'); field(md, 'Why').fill('Faster release, less starch dust')
    md.get_by_role('button', name='Request change').click(); pg.wait_for_selector('.md .msg.err >> text=impact assessment')
    md.locator('label.ck', has_text='HACCP plan / flow diagram').locator('input').check(); md.locator('label.ck', has_text=re.compile('^Training$')).locator('input').check()
    check(md.locator('label.ck', has_text='Training needed before').locator('input').is_checked(), 'ticking Training makes training required')
    md.locator('label.ck', has_text='State regulator').locator('input').check()
    md.get_by_role('button', name='+ Action').click(); md.locator('input[placeholder="Action"]').fill('Buy and validate molds'); md.locator('input[placeholder="Who"]').fill('Lee')
    md.get_by_role('button', name='Request change').click(); pg.wait_for_selector('.msg >> text=Requested CC-2026-001')
    pg.get_by_role('button', name='Approve', exact=True).click(); md = pg.locator('.md'); check(md.locator('text=tell State regulator').count() == 1, 'approval screen lists what is needed before use')
    md.get_by_role('button', name='Approve').click(); pg.wait_for_selector('.msg >> text=Approved CC-2026-001')
    check(pg.locator('td', has_text='1 action open, training before use, HACCP plan review, notifications').count() == 1, 'next step lists the blockers')
    pg.get_by_role('button', name='Work', exact=True).click(); md = pg.locator('.md')
    check(md.get_by_role('button', name='Mark implemented').is_disabled(), 'cannot implement with open items')
    md.locator('input[type=checkbox][title=Done]').check(); md.locator('label.ck', has_text='Training given before use').locator('input').check()
    md.locator('label.ck', has_text='HACCP plan reviewed').locator('input').check(); field(md, 'Told on').fill(TODAY)
    md.get_by_role('button', name='Mark implemented').click(); pg.wait_for_selector('.msg >> text=CC-2026-001 is implemented')
    c1 = T['hx_changes'][0]; check(c1['status'] == 'implemented' and c1['actions'][0]['done'] and c1['actions'][0]['done_on'] == TODAY, 'implemented with the action done')
    pg.locator('tr', has_text='CC-2026-001').get_by_role('button', name='Close').click(); md = pg.locator('.md')
    md.locator('textarea').fill('5 batches, no starch dust, release OK'); md.get_by_role('button', name='Close change').click(); pg.wait_for_selector('.msg >> text=Closed CC-2026-001')
    with pg.expect_popup() as pop: pg.locator('tr', has_text='CC-2026-001').get_by_role('button', name='Print').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Change CC-2026-001' in html and 'Closed' in html and 'Buy and validate molds' in html and '5 batches' in html, 'printable change record'); w.close()
    pg.screenshot(path=OUT + 'changes.png', full_page=True)
    T['hx_standards'].append({'id': 's1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C', '4A', '5'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 's1', 'target_level': 3, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    def clause(c):
        r = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(c) + '$'))).first; r.locator('div.row').first.click(timeout=5000); pg.wait_for_timeout(300); return r.inner_text()
    pg.screenshot(path=OUT + 'rc_std.png'); e516, e19, e515, e4a10 = clause('5.1.6'), clause('1.9'), clause('5.1.5'), clause('4A.10')
    print(e516.replace('\n', ' | ')[:600]); print(e515.replace('\n', ' | ')[:600])
    check('12 risks with hazard, root cause and owner' in e516 and 'Risk register' in e516, '5.1.6 live risk register evidence')
    check('Threat assessment' in e19 and '1 risk on the register' in e19, '1.9 threat assessment from the risk register')
    check('1 change in 12 months' in e515 and '1 of 1 implemented were approved first' in e515 and 'training before use 1/1' in e515, '5.1.5 live change control evidence')
    check('1 change affecting HACCP' in e4a10 and '1 with the plan reviewed' in e4a10, '4A.10 HACCP changes reviewed')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Risk and change')
    check(pg.locator('.card.gold', has_text='Risk and change').locator('text=/high \\/ critical risk/').count() == 1, 'dashboard card shows high risks')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
