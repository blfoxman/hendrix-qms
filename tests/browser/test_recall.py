import re, math, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
def iso(): return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
T['hx_suppliers'] += [{'id': 's1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Futurola USA', 'category': 'Packaging', 'status': 'approved', 'contact_name': 'Ana', 'contact_email': 'ana@f.com', 'contact_phone': '555-1000'},
                      {'id': 's2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Terp Co', 'category': 'Terpenes', 'status': 'approved', 'contact_name': '', 'contact_email': '', 'contact_phone': ''}]
T['hx_lots'] += [{'id': 'l1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-001', 'received_on': '2026-10-01', 'supplier_id': 's1', 'supplier_name': 'Futurola USA', 'item': '98mm cones', 'category': 'Packaging', 'supplier_lot': 'FU-7781', 'metrc_tag': '', 'quantity': 1000, 'unit': 'each', 'qty_used': 300, 'status': 'accepted', 'coa_ok': True, 'expiry_date': None, 'location': 'Rack B2'},
                 {'id': 'l2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-002', 'received_on': '2026-10-02', 'supplier_id': 's2', 'supplier_name': 'Terp Co', 'item': 'Limonene', 'category': 'Terpenes', 'supplier_lot': 'TC-55', 'metrc_tag': '', 'quantity': 5, 'unit': 'L', 'qty_used': 1, 'status': 'accepted', 'coa_ok': True, 'expiry_date': None, 'location': ''}]
T['hx_batches'] += [{'id': 'b1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'preroll', 'batch_number': 'PR-100', 'sku': 'Pre-roll 1g', 'flavor': 'OG', 'status': '', 'voided': False, 'created_at': '2026-10-05T10:00:00Z', 'data': {}},
                    {'id': 'b2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'cart', 'batch_number': 'CT-9', 'sku': 'Cart', 'flavor': '', 'status': '', 'voided': False, 'created_at': '2026-10-06T10:00:00Z', 'data': {}}]
T['hx_lot_uses'] += [{'id': 'u1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'lot_id': 'l1', 'batch_id': 'b1', 'batch_number': 'PR-100', 'quantity': 300, 'used_on': '2026-10-05', 'voided': False},
                     {'id': 'u2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'lot_id': 'l2', 'batch_id': 'b1', 'batch_number': 'PR-100', 'quantity': 1, 'used_on': '2026-10-05', 'voided': False}]
T['hx_tests'] += [{'id': 't1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b1', 'tag': '1A4000000000000000000777', 'sample_tag': '', 'status': 'Passed', 'voided': False, 'created_at': '2026-10-07T10:00:00Z', 'lab_name': 'Green Lab'}]
T['hx_shipments'] += [{'id': 'sh1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'SHP-2026-001', 'ship_date': '2026-10-10', 'customer': 'Dispensary A', 'customer_license': 'DIS-1', 'destination': '1 Main St', 'manifest_number': 'M-1', 'status': 'delivered',
                       'items': [{'batch_id': 'b1', 'batch_number': 'PR-100', 'product': 'Pre-roll 1g', 'tag': '1A4000000000000000000777', 'qty': '200', 'unit': 'units'}]},
                      {'id': 'sh2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'SHP-2026-002', 'ship_date': '2026-10-11', 'customer': 'Dispensary B', 'customer_license': 'DIS-2', 'destination': '', 'manifest_number': 'M-2', 'status': 'shipped',
                       'items': [{'batch_id': 'b1', 'batch_number': 'PR-100', 'product': 'Pre-roll 1g', 'tag': '1A4000000000000000000888', 'qty': '100', 'unit': 'units'}, {'batch_id': 'b2', 'batch_number': 'CT-9', 'product': 'Cart', 'tag': '1A4999', 'qty': '50', 'unit': 'units'}]}]
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def jerr(route, m): return jr(route, {'message': m}, 400)
def full(): return T['hx_profiles'][0]['role'] == 'admin' or (T['hx_profiles'][0].get('perms') or {}).get('recall') == 'admin'
def handle(route, request):
    u = request.url; m = request.method
    if '/rest/v1/rpc/hx_trace_data' in u:
        return jr(route, {'lots': T['hx_lots'], 'uses': [x for x in T['hx_lot_uses'] if not x.get('voided')], 'batches': [b for b in T['hx_batches'] if not b['voided']], 'tests': T['hx_tests'], 'ships': T['hx_shipments'], 'holds': T['hx_holds'], 'suppliers': T['hx_suppliers']})
    if '/rest/v1/hx_holds' in u and m == 'POST':
        r = json.loads(request.post_data); r.update({'number': 'HOLD-2026-%03d' % (len(T['hx_holds']) + 1), 'status': 'open', 'created_at': iso(), 'tag': '', 'item': ''}); T['hx_holds'].append(r)
        if r['kind'] == 'lot': next(l for l in T['hx_lots'] if l['id'] == r['lot_id'])['status'] = 'on_hold'
        return jr(route, [r], 201)
    if '/rest/v1/hx_recalls' in u and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST':
            if b['kind'] != 'mock' and not full(): return jerr(route, 'Only someone with Full access to Recall can start a recall or withdrawal.')
            pre = 'MOCK' if b['kind'] == 'mock' else 'RCL'
            r = dict(b); r.update({'number': '%s-2026-%03d' % (pre, sum(1 for x in T['hx_recalls'] if x['number'].startswith(pre)) + 1), 'started_at': iso(), 'status': 'open', 'result': '', 'duration_minutes': None, 'ended_at': None, 'step_times': {}, 'started_by': 'Sam', 'closed_by': '', 'cancel_reason': ''})
            for k in ('notified', 'files'): r.setdefault(k, [])
            for k in ('qty_made', 'qty_on_hand', 'qty_recovered', 'findings', 'actions', 'recall_class'): r.setdefault(k, '')
            T['hx_recalls'].append(r); return jr(route, [r], 201)
        rid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_recalls'] if x['id'] == rid)
        if r['status'] != 'open': return jerr(route, 'closed')
        for k, v in (b.get('steps') or {}).items():
            if v and not r['steps'].get(k): r['step_times'][k] = iso()
        r.update({k: v for k, v in b.items() if k != 'step_times'})
        if b.get('status') == 'closed':
            if not r['findings']: return jerr(route, 'Write the findings before closing.')
            allok = all(r['steps'].values())
            if r['kind'] != 'mock' and not allok: r['status'] = 'open'; return jerr(route, 'Complete every recall step before closing.')
            r['ended_at'] = iso(); r['duration_minutes'] = 1; r['closed_by'] = 'Sam'; r['result'] = ('Pass' if allok else 'Fail') if r['kind'] == 'mock' else 'Completed'
        return jr(route, [r])
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
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Open recall')
    check(pg.locator('.card', has_text='Open recall').locator('text=Never run').count() == 1, 'dashboard: mock recall never run')
    check(pg.locator('.badge', has_text=re.compile('^Traceability and Recall$')).count() == 0, 'removed from Coming next')
    pg.get_by_role('button', name='Traceability and Recall').click(); pg.wait_for_selector('text=Type a received lot number')
    # trace a batch
    pg.locator('input[placeholder^="Search a lot"]').fill('PR-100'); pg.locator('.card', has_text='PR-100').first.click(); pg.wait_for_selector('text=One step back')
    check(pg.locator('text=Futurola USA → RCV-2026-001').count() == 1 and pg.locator('text=Terp Co → RCV-2026-002').count() == 1, 'batch traced back to both suppliers and lots')
    check(pg.locator('.card', has_text='Dispensary A (DIS-1)').count() == 1 and pg.locator('.card', has_text='Dispensary B (DIS-2)').count() == 1, 'batch traced forward to both customers')
    check(pg.locator('.card.gold', has_text='Shipped').locator('.v').inner_text() == '300 units', 'shipped quantity totaled (300 units)')
    pg.screenshot(path=OUT + 'trace.png')
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Print trace').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('One step back' in html and 'FU-7781' in html and 'Dispensary B' in html and 'M-2' in html, 'printable trace report')
    # trace a tag -> only that customer
    pg.locator('input[placeholder^="Search a lot"]').fill('0777'); pg.locator('.card', has_text='1A4000000000000000000777').first.click(); pg.wait_for_selector('text=One step forward')
    check(pg.locator('.card', has_text='Dispensary A (DIS-1)').count() == 1 and pg.locator('.card', has_text='Dispensary B').count() == 0, 'package tag traced to its one customer')
    # trace a lot forward
    pg.locator('input[placeholder^="Search a lot"]').fill('FU-7781'); pg.locator('.card', has_text='RCV-2026-001').first.click(); pg.wait_for_selector('text=One step forward')
    check(pg.locator('.card', has_text='Batch PR-100').count() == 1 and pg.locator('.card', has_text='Dispensary B').count() == 1 and pg.locator('.card', has_text='CT-9').count() == 0, 'supplier lot traced forward to batch and customers')
    # contacts
    pg.locator('.tabs button', has_text='Recall team and contacts').click(); pg.wait_for_selector('text=Missing from the contact list')
    check(pg.locator('.msg.err', has_text='Recall team, Emergency services, Regulators, Certification body').count() == 1, 'required contact types flagged')
    pg.get_by_role('button', name='Add 2 customers from shipments').click(); pg.wait_for_selector('.msg >> text=Added 2 customers')
    for kind, name, role in [('team', 'Sam Salari', 'Recall coordinator'), ('regulator', 'DCR Compliance', ''), ('certification', 'CSQ certification body', ''), ('emergency', 'Fire / police 911', '')]:
        pg.get_by_role('button', name='+ Add contact').click(); md = pg.locator('.md'); field(md, 'Type').select_option(kind); field(md, 'Name').fill(name)
        if role: field(md, 'Recall role').fill(role)
        field(md, 'Phone').fill('555-0100'); n0 = len(T['hx_recall_contacts']); md.get_by_role('button', name='Save contact').click()
        for _ in range(50):
            if len(T['hx_recall_contacts']) > n0 and pg.locator('.md').count() == 0: break
            pg.wait_for_timeout(100)
    pg.wait_for_timeout(300)
    check(pg.locator('text=Missing from the contact list').count() == 0, 'all required contact types present')
    check(pg.locator('text=2 contacts have not been verified').count() == 1, 'customers added from shipments flagged as not verified')
    pg.get_by_role('button', name='Mark all verified today').click(); pg.wait_for_selector('.msg >> text=Verified 6 contacts')
    # mock recall: pass
    pg.locator('.tabs button', has_text='Trace').click(); pg.locator('input[placeholder^="Search a lot"]').fill('PR-100'); pg.locator('.card', has_text='PR-100').first.click()
    pg.get_by_role('button', name='Start mock recall from this').click(); md = pg.locator('.md')
    check(md.locator('text=PR-100').count() >= 1, 'mock recall prefilled with the traced batch')
    md.get_by_role('button', name='Start the clock').click(); pg.wait_for_selector('.md >> text=Elapsed (limit 2:00:00)')
    t1 = pg.locator('.md').locator('div[style*="tabular-nums"]').inner_text(); pg.wait_for_timeout(1300); t2 = pg.locator('.md').locator('div[style*="tabular-nums"]').inner_text()
    check(t1 != t2 and re.match(r'^\d+:\d\d$', t2), 'live timer running (%s -> %s)' % (t1, t2))
    md = pg.locator('.md'); check(md.locator('label.ck', has_text='Dispensary A').count() == 1 and md.locator('label.ck', has_text='Sam Salari').count() == 1, 'contacts to confirm include traced customers and team')
    for c in md.locator('label.ck input[type=checkbox]').all(): c.check()
    field(md, 'Made / received').fill('300'); field(md, 'On hand').fill('0')
    check(md.locator('text=Accounted for: 100% of what was made').count() == 1, 'quantity reconciliation 100%')
    field(md, 'Findings').fill('Traced back to 2 suppliers and forward to 2 customers in 14 minutes'); md.get_by_role('button', name='Stop the clock and close').click(); pg.wait_for_selector('.msg >> text=Closed MOCK-2026-001')
    r = T['hx_recalls'][0]; check(r['status'] == 'closed' and r['result'] == 'Pass' and len(r['step_times']) == 8 and len(r['notified']) >= 6 and 'PR-100' in r['trace']['batches'], 'mock recall closed: pass, step times, contacts, trace snapshot')
    check(pg.locator('.md').locator('.badge', has_text='Pass').count() == 1, 'result shown')
    with ctx.expect_page() as pi: pg.locator('.md').get_by_role('button', name='Print report').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('MOCK-2026-001' in html and 'Pass' in html and 'Recall team assembled' in html and 'One step forward' in html, 'printable mock recall report with steps and trace')
    pg.locator('.md').get_by_role('button', name='Close').last.click()
    # failing mock
    pg.get_by_role('button', name='Start mock recall').click(); md = pg.locator('.md'); field(md, 'Lot, batch or package tag').fill('CT-9'); md.locator('.row', has_text='CT-9').first.click()
    md.get_by_role('button', name='Start the clock').click(); pg.wait_for_selector('.md >> text=Elapsed')
    md = pg.locator('.md'); field(md, 'Findings').fill('No input lots recorded for CT-9'); md.get_by_role('button', name='Stop the clock and close').click(); pg.wait_for_selector('.msg >> text=Closed MOCK-2026-002')
    pg.wait_for_selector('.md >> .badge >> text=Fail', timeout=5000)
    check(T['hx_recalls'][1]['result'] == 'Fail' and pg.locator('.md').get_by_role('button', name='Deviation').count() == 1, 'incomplete mock fails; deviation button offered')
    pg.locator('.md').get_by_role('button', name='Close').last.click()
    check(pg.locator('tr', has_text='MOCK-2026-001').locator('.badge', has_text='Pass').count() == 1 and pg.locator('.card.gold', has_text='Next due').count() == 1, 'exercise list + next due')
    # real recall puts product on hold
    pg.get_by_role('button', name='Start recall').click(); md = pg.locator('.md')
    check(field(md, 'Type').input_value() == 'recall', 'Start recall opens as a recall')
    field(md, 'Lot, batch or package tag').fill('PR-100'); md.locator('.row', has_text='PR-100').first.click()
    md.get_by_role('button', name='Start recall').click(); check(md.locator('.msg.err', has_text='reason').count() == 1, 'recall needs a reason')
    field(md, 'Reason').fill('Mold found in retained sample'); md.get_by_role('button', name='Start recall').click(); pg.wait_for_selector('.msg >> text=Started RCL-2026-001')
    pg.locator('.md').get_by_role('button', name='Put every affected batch and lot on hold').click(); pg.wait_for_selector('.msg >> text=Put 3 items on hold')
    check(len(T['hx_holds']) == 3 and all(h['source'] == 'Recall' for h in T['hx_holds']) and T['hx_lots'][0]['status'] == 'on_hold' and T['hx_recalls'][2]['steps']['hold'] is True and 'hold' in T['hx_recalls'][2]['step_times'], 'batch + 2 input lots put on hold with source Recall')
    pg.screenshot(path=OUT + 'recall_run.png')
    pg.locator('.md').get_by_role('button', name='Close').last.click()
    check(pg.locator('.msg.err', has_text='RCL-2026-001 running').count() == 1, 'open recall banner')
    # standards evidence
    T['hx_standards'].append({'id': 'st1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 'st1', 'target_level': 1, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    def clause(c):
        rr = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(c) + '$'))).first; rr.locator('div.row').first.click(); return rr
    r1 = clause('1.8'); check(r1.locator('text=Last').count() >= 1 and r1.locator('text=1 team member').count() == 1, '1.8: mock recall + recall team evidence')
    r2 = clause('2A.10.1'); check(r2.locator('text=1 of 2 shipped batches (12 months) traced back to received lots').count() == 1, '2A.10.1: traceability coverage (CT-9 has no input lots)')
    # view-only user
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'recall': 'read'}
    pg.reload(); pg.get_by_role('button', name='Traceability and Recall').click(); pg.wait_for_selector('text=Type a received lot number')
    check(pg.get_by_role('button', name='Start mock recall').count() == 0 and pg.get_by_role('button', name='Start recall').count() == 0, 'View: can trace, cannot start')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
