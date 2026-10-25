import re, copy
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
PEOPLE = [{'id': ADMIN, 'name': 'Sam'}, {'id': 'u-lee', 'name': 'Lee Worker'}]
_h = handle
def fail(route, m): return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': m}))
def handle(route, request):
    u = request.url
    if '/rest/v1/rpc/hx_qms_people' in u: return route.fulfill(status=200, content_type='application/json', body=json.dumps(PEOPLE))
    for tbl, pre in (('hx_deviations', 'DEV'), ('hx_capas', 'CAPA')):
        if '/rest/v1/' + tbl in u and request.method in ('POST', 'PATCH'):
            b = json.loads(request.post_data)
            if request.method == 'POST':
                n = len([x for x in T[tbl] if x['license_id'] == b['license_id']]) + 1
                b.update({'number': '%s-2026-%03d' % (pre, n), 'created_at': now(), 'updated_at': now(), 'reported_by': 'Sam', 'created_by': 'Sam', 'reported_by_id': ADMIN, 'rca_decided_by': 'Sam' if b.get('rca_required') is not None else '',
                          'closed_by': '', 'closed_at': None, 'cancel_reason': '', 'effectiveness_rating': '', 'verification_evidence': '', 'verified_by': '', 'close_note': ''})
                for k in ('rca_required',): b.setdefault(k, None)
                T[tbl].append(b); return route.fulfill(status=201, content_type='application/json', body=json.dumps([b]))
            rid = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)['id'][0].replace('eq.', '')
            r = next(x for x in T[tbl] if x['id'] == rid); new = {**r, **b}
            if b.get('status') == 'closed' and r['status'] != 'closed':
                if tbl == 'hx_deviations':
                    if not new.get('immediate_action'): return fail(route, 'Every deviation needs its correction (immediate action) recorded before it is closed.')
                    if new.get('rca_required') is None: return fail(route, 'Decide whether a root cause analysis is needed before closing.')
                    if new['rca_required'] and not new.get('root_cause'): return fail(route, 'A root cause is required before closing (RCA was marked as needed).')
                else:
                    if not new.get('verification_evidence') or new.get('effectiveness_rating') != 'effective': return fail(route, 'A CAPA closes only when it is verified Effective.')
                b.update({'closed_by': 'Sam', 'closed_at': now()})
            if 'effectiveness_rating' in b and b['effectiveness_rating']: b.update({'verified_by': 'Sam', 'verified_at': now()})
            if 'rca_required' in b and b['rca_required'] != r.get('rca_required'): b['rca_decided_by'] = 'Sam'
            if b.get('status') == 'cancelled' and not b.get('cancel_reason'): return fail(route, 'A reason is required.')
            b['updated_at'] = now(); r.update(b); return route.fulfill(status=200, content_type='application/json', body=json.dumps([r]))
    return _h(route, request)
def open_card(pg, name):
    if pg.locator('.md').count():
        pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click(); pg.wait_for_timeout(150)
    pg.locator('.card', has_text=name).first.click(); pg.wait_for_selector('.md')
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
T['hx_facility_log'] += [{'id': 'flx', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'log_type': 'temperature', 'item': 'Vault 1', 'created_at': now(), 'voided': False, 'result': 'Fail', 'performed_by': 'Lee', 'data': {'date': '2026-10-22', 'temperature_f': '79', 'humidity_pct': '50', 'in_range': 'No'}}]
T['hx_tests'] += [{'id': 'tf', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': None, 'batch_number': 'PR-1', 'batch_type': 'pre_rolls', 'sku': 'Shorties', 'flavor': 'Mango', 'tag': '1A4000000000000000009999', 'tag_label': '', 'sample_tag': '', 'lab_name': 'Lab A', 'lab_license': '', 'status': 'Failed',
                   'result_at': now(), 'result_thc': '', 'result_cbd': '', 'result_notes': 'Yeast and mold over limit', 'notes': '', 'coa_path': '', 'coa_filename': '', 'coa_analysis': None, 'voided': False, 'created_at': now()}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_logtab","temperature");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Deviations & CAPA')
    check(pg.locator('.nav button.soon').count() == 0, 'no more "Soon" placeholders in the menu')
    # raise from facility log
    pg.get_by_role('button', name='Facility Logs').click(); pg.wait_for_selector('td >> text=Vault 1')
    pg.locator('tr', has_text='Vault 1').get_by_role('button', name='Deviation').click(); md = pg.locator('.md')
    check(md.locator('text=Source: Facility log').count() == 1 and field(md, 'Deviation title').input_value().startswith('Temp / Humidity Log: Fail') and field(md, 'Category').input_value() == 'Environment / temperature', 'log deviation prefilled from the entry')
    field(md, 'Correction / immediate action taken').fill('Moved product to Vault 2.')
    md.get_by_role('button', name='Submit deviation').click(); pg.wait_for_selector('tr >> text=✓ DEV-2026-001')
    d1 = T['hx_deviations'][0]
    check(d1['source_type'] == 'facility_log' and d1['source_id'] == 'flx' and d1['number'] == 'DEV-2026-001' and d1['occurred_on'] == '2026-10-22', 'deviation stored with source link and number')
    # raise from failed test
    pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=PR-1')
    pg.locator('.card', has_text='PR-1').get_by_role('button', name='Deviation').click(); md = pg.locator('.md')
    check(field(md, 'Priority').input_value() == 'critical' and field(md, 'Lot / batch number').input_value() == 'PR-1', 'failed test deviation: critical + lot prefilled')
    md.get_by_role('button', name='Submit deviation').click(); pg.wait_for_timeout(500)
    check(len(T['hx_deviations']) == 2 and T['hx_deviations'][1]['category'] == 'Testing result', 'test deviation saved')
    # QMS page
    pg.get_by_role('button', name='QMS', exact=True).click(); pg.wait_for_selector('text=Needs action')
    check(pg.locator('.card', has_text='Open deviations').locator('text=2').count() >= 1, 'dashboard: 2 open deviations')
    check(pg.locator('text=Root cause analysis decision needed').count() == 2, 'needs action: RCA decisions')
    pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click() if pg.locator('.md').count() else None
    pg.locator('.tabs button', has_text='Deviations').click(); open_card(pg, 'DEV-2026-001'); md = pg.locator('.md')
    check(md.locator('text=Source: Facility log').count() == 1 and md.get_by_role('button', name='Open').count() == 1, 'detail shows source with link')
    md.get_by_role('button', name='Close deviation').click(); md = pg.locator('.md')
    check(md.locator('.badge.bad').count() >= 1 and md.get_by_role('button', name='Close deviation').is_disabled(), 'close blocked until RCA decided')
    md.get_by_role('button', name='Cancel').click()
    open_card(pg, 'DEV-2026-001'); pg.locator('.md').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    field(md, 'Root cause analysis needed').select_option('yes'); field(md, 'Root cause *').fill('HVAC compressor failed'); field(md, 'Owner (who resolves it)').fill('Facility Mgr'); field(md, 'Due date').fill('2020-01-01')
    md.get_by_role('button', name='Update').click(); pg.wait_for_selector('.msg >> text=Saved')
    check(d1['rca_required'] is True and d1['rca_decided_by'] == 'Sam' and d1['root_cause'], 'RCA decision + root cause saved')
    pg.locator('.card', has_text='DEV-2026-001').locator('.badge', has_text='Overdue').first.wait_for(timeout=8000)
    check(pg.locator('.card', has_text='DEV-2026-001').locator('.badge', has_text='Overdue').count() == 1, 'overdue deviation flagged')
    # CAPA from deviation
    open_card(pg, 'DEV-2026-001'); pg.locator('.md').get_by_role('button', name='+ Create CAPA').click(); md = pg.locator('.md')
    check(field(md, 'CAPA title').input_value().startswith('CAPA for DEV-2026-001') and field(md, 'Correction (immediate fix)').input_value() == 'Moved product to Vault 2.', 'CAPA prefilled from deviation')
    md.get_by_role('button', name='Create CAPA').click(); pg.wait_for_timeout(200)
    check(md.locator('.msg.err', has_text='due date').count() == 1, 'CAPA needs a due date')
    field(md, 'Due date').fill('2027-01-15'); field(md, 'Responsible person').select_option('u-lee'); field(md, 'Preventive action (long-term fix)').fill('Quarterly HVAC service; alarm on vault.')
    field(md, 'Verification method').fill('30 days of in-range logs')
    md.get_by_role('button', name='Create CAPA').click(); pg.wait_for_selector('.msg >> text=Created: CAPA-2026-001')
    c1 = T['hx_capas'][0]
    check(c1['deviation_id'] == d1['id'] and c1['responsible_person_name'] == 'Lee Worker', 'CAPA linked + responsible person')
    md = pg.locator('.md'); md.get_by_role('button', name='Verify effectiveness').click(); md = pg.locator('.md')
    field(md, 'Verification evidence').fill('Logs reviewed for 30 days; one excursion.'); field(md, 'Effectiveness').select_option('partially')
    check(md.get_by_role('button', name='Verify & close CAPA').count() == 0, 'partially effective cannot close')
    md.get_by_role('button', name='Save rating').click(); pg.wait_for_selector('.msg >> text=Verified')
    check(c1['effectiveness_rating'] == 'partially' and c1['status'] == 'in_progress', 'partially effective keeps CAPA open (in progress)')
    pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click() if pg.locator('.md').count() else None
    pg.locator('.tabs button', has_text='CAPAs').click(); open_card(pg, 'CAPA-2026-001'); pg.locator('.md').get_by_role('button', name='Verify effectiveness').click(); md = pg.locator('.md')
    field(md, 'Verification evidence').fill('60 days in range after alarm install.'); field(md, 'Effectiveness').select_option('effective'); md.get_by_role('button', name='Verify & close CAPA').click()
    for _ in range(30):
        if c1['status'] == 'closed': break
        pg.wait_for_timeout(100)
    pg.wait_for_timeout(300)
    check(c1['status'] == 'closed' and c1['verified_by'] == 'Sam', 'CAPA verified effective and closed')
    # close deviation
    pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click() if pg.locator('.md').count() else None
    pg.locator('.tabs button', has_text='Deviations').click(); open_card(pg, 'DEV-2026-001'); pg.locator('.md').get_by_role('button', name='Close deviation').click(); md = pg.locator('.md')
    field(md, 'Closing note').fill('CAPA-2026-001 effective'); md.get_by_role('button', name='Close deviation').click(); pg.wait_for_selector('.msg >> text=Closed DEV-2026-001')
    check(d1['status'] == 'closed' and d1['closed_by'] == 'Sam', 'deviation closed with all checks met')
    # cancel needs reason; print
    pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click() if pg.locator('.md').count() else None
    pg.locator('select').filter(has_text='Open + in progress').select_option('ALL')
    open_card(pg, 'DEV-2026-002'); pg.locator('.md').get_by_role('button', name='Cancel').click(); md = pg.locator('.md')
    check(md.get_by_role('button', name='Cancel record').is_disabled(), 'cancel needs a reason')
    field(md, 'Reason').fill('Duplicate - retest ordered under DEV-2026-003'); md.get_by_role('button', name='Cancel record').click(); pg.wait_for_selector('.msg >> text=Cancelled DEV-2026-002')
    check(T['hx_deviations'][1]['status'] == 'cancelled' and len(T['hx_deviations']) == 2, 'cancelled, never deleted')
    open_card(pg, 'DEV-2026-001')
    with ctx.expect_page() as pi: pg.locator('.md').get_by_role('button', name='Print / PDF').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('DEV-2026-001' in html and 'HVAC compressor failed' in html and 'CAPA-2026-001' in html, 'printable deviation record')
    pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click() if pg.locator('.md').count() else None
    # trends
    pg.locator('.tabs button', has_text='Trends').click(); pg.wait_for_selector('text=By category')
    check(pg.locator('svg rect').count() >= 12 and pg.locator('text=Environment / temperature').count() >= 1, 'trend charts drawn')
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Print annual trend review').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('trend review' in html and 'BY CATEGORY' in html and 'Reviewed by' in html, 'annual trend review prints')
    pg.screenshot(path=OUT + 'qms_trends.png')
    pg.locator('.tabs button', has_text='Dashboard').click(); pg.wait_for_selector('text=Last 12 months'); pg.screenshot(path=OUT + 'qms_dash.png')
    # standards evidence
    T['hx_standards'].append({'id': 's1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 's1', 'target_level': 1, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    r = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile(r'^1\.6$'))).first; r.locator('div.row').first.click()
    check(r.locator('text=2 deviations in 12 months').count() == 1 and r.locator('text=1 closed after verifying effective').count() == 1, '1.6 live QMS evidence')
    # View-only can report but not edit
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'qms': 'read'}
    pg.reload(); pg.get_by_role('button', name='QMS', exact=True).click(); pg.wait_for_selector('text=Needs action')
    check(pg.get_by_role('button', name='+ Report deviation').count() == 1 and pg.get_by_role('button', name='+ New CAPA').count() == 0, 'View: can report deviations, not CAPAs')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
