import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today().isoformat()
T['hx_suppliers'] += [{'id': 's-ok', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Futurola USA', 'category': 'Packaging', 'status': 'approved', 'specs': 'Food-grade paper', 'emergency_verification': ''},
                      {'id': 's-pend', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Pending Paper Co', 'category': 'Packaging', 'status': 'pending', 'specs': '', 'emergency_verification': ''}]
T['hx_batches'] += [{'id': 'b-ok', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'preroll', 'batch_number': 'PR-100', 'sku': 'Pre-roll 1g', 'flavor': 'OG', 'voided': False, 'created_at': '2026-10-01T10:00:00Z', 'data': {}},
                    {'id': 'b-bad', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'cart', 'batch_number': 'CT-200', 'sku': 'Cart 1g', 'flavor': 'Lemon', 'voided': False, 'created_at': '2026-10-02T10:00:00Z', 'data': {}}]
T['hx_tests'] += [{'id': 'tt1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b-ok', 'tag': 'A', 'status': 'Passed', 'voided': False, 'created_at': '2026-10-05T10:00:00Z'},
                  {'id': 'tt2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b-bad', 'tag': 'B', 'status': 'Failed', 'voided': False, 'created_at': '2026-10-05T10:00:00Z'}]
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def jerr(route, m): return jr(route, {'message': m}, 400)
def lvl(mod):
    p = T['hx_profiles'][0]
    return 3 if p['role'] == 'admin' else {'admin': 3, 'editor': 2, 'read': 1}.get((p.get('perms') or {}).get(mod), 0)
def nxt(tbl, pre):
    n = sum(1 for x in T[tbl] if x.get('number', '').startswith(pre + '-')) + 1
    return '%s-2026-%03d' % (pre, n)
def audit(tbl, r, action, reason):
    T['hx_audit_log'].append({'id': len(T['hx_audit_log']) + 1, 'at': now(), 'table_name': tbl, 'row_id': r['id'], 'action': action, 'state_id': r.get('state_id'), 'license_id': r.get('license_id'), 'user_name': 'Sam', 'reason': reason, 'changed': None, 'old_data': None, 'new_data': r})
LOTCK = ['docs', 'intact', 'clean', 'sealed', 'labeled', 'condition', 'vehicle']
def failed(bid):
    t = [x for x in T['hx_tests'] if x.get('batch_id') == bid and not x.get('voided')]
    lf = max([x['created_at'] for x in t if x['status'] == 'Failed'] or [''])
    return bool(lf) and not any(x['status'] == 'Passed' and x['created_at'] > lf for x in t)
def add_hold(r, internal=False):
    r = dict(r); r.update({'number': nxt('hx_holds', 'HOLD'), 'status': 'open', 'placed_by': 'Sam', 'created_at': now(), 'decided_by': '', 'decision_notes': ''})
    for k in ('lot_id', 'batch_id', 'tag', 'item', 'quantity', 'location', 'prev_status'): r.setdefault(k, '' if k not in ('lot_id', 'batch_id') else None)
    if r['kind'] == 'lot':
        l = next(x for x in T['hx_lots'] if x['id'] == r['lot_id'])
        if l['status'] == 'on_hold': return None, 'Lot is already on hold.'
        if not internal: r['prev_status'] = l['status']
        r['item'] = r['item'] or l['item'] + ' (' + l['number'] + ')'; l['status'] = 'on_hold'
    elif r.get('batch_id'):
        b = next(x for x in T['hx_batches'] if x['id'] == r['batch_id']); r['item'] = r['item'] or b['sku'] + ' batch ' + b['batch_number']
    T['hx_holds'].append(r); audit('hx_holds', r, 'INSERT', 'Placed on hold: ' + r['reason']); return r, None
def handle(route, request):
    u = request.url; m = request.method
    tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl not in ('hx_lots', 'hx_lot_uses', 'hx_holds', 'hx_shipments') or m == 'GET': return _h(route, request)
    body = json.loads(request.post_data) if request.post_data else {}
    rid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]) if 'id=eq.' in u else None
    if m == 'DELETE': return jerr(route, 'never deleted')
    if tbl == 'hx_lots':
        if m == 'POST':
            s = next(x for x in T['hx_suppliers'] if x['id'] == body['supplier_id'])
            if s['status'] not in ('approved', 'conditional', 'emergency'): return jerr(route, s['name'] + ' is not approved yet - receive only from approved suppliers (CSQ 2A.11).')
            r = dict(body); r.update({'number': nxt('hx_lots', 'RCV'), 'supplier_name': s['name'], 'supplier_status': s['status'], 'qty_used': 0, 'received_by': 'Sam', 'created_at': now(), 'decided_by': '', 'decided_at': None, 'decision_notes': '',
                                      'checks_ok': all(r['checks'].get(k) for k in LOTCK)})
            T['hx_lots'].append(r); audit('hx_lots', r, 'INSERT', 'Lot received from ' + s['name']); return jr(route, [r], 201)
        l = next(x for x in T['hx_lots'] if x['id'] == rid)
        if 'status' in body and body['status'] != l['status']:
            if lvl('receiving') < 3: return jerr(route, 'Only someone with Full access to Receiving can accept or reject a lot.')
            if body['status'] == 'accepted' and not l['coa_ok']: return jerr(route, 'The lot needs its COA')
            if body['status'] == 'rejected' and not body.get('decision_notes'): return jerr(route, 'Write why the lot is rejected.')
            l.update(body); l['decided_by'] = 'Sam'; l['decided_at'] = now() + ''; audit('hx_lots', l, 'UPDATE', 'Lot ' + l['status'])
            if l['status'] == 'rejected':
                add_hold({'id': 'hold-auto%d' % seq[0], 'state_id': l['state_id'], 'license_id': l['license_id'], 'kind': 'lot', 'lot_id': l['id'], 'source': 'Receiving inspection', 'reason': 'Rejected at receiving: ' + l['decision_notes'], 'prev_status': 'rejected'}, True)
            return jr(route, [l])
        l.update(body); audit('hx_lots', l, 'UPDATE', 'Lot updated'); return jr(route, [l])
    if tbl == 'hx_lot_uses':
        if m == 'POST':
            l = next(x for x in T['hx_lots'] if x['id'] == body['lot_id'])
            if l['status'] != 'accepted': return jerr(route, 'Lot is not accepted')
            if body['quantity'] > l['quantity'] - l['qty_used']: return jerr(route, 'Only %s left' % (l['quantity'] - l['qty_used']))
            r = dict(body); b = next((x for x in T['hx_batches'] if x['id'] == r.get('batch_id')), None); r.update({'batch_number': b['batch_number'] if b else '', 'used_by': 'Sam', 'voided': False, 'created_at': now()})
            l['qty_used'] += r['quantity']; T['hx_lot_uses'].append(r); audit('hx_lot_uses', r, 'INSERT', 'Used'); return jr(route, [r], 201)
        x = next(x for x in T['hx_lot_uses'] if x['id'] == rid); x.update(body)
        if body.get('voided'): next(l for l in T['hx_lots'] if l['id'] == x['lot_id'])['qty_used'] -= x['quantity']
        return jr(route, [x])
    if tbl == 'hx_holds':
        if m == 'POST':
            if lvl('holds') < 2: return jerr(route, 'You need Edit access to Hold and Release')
            r, e = add_hold(body)
            return jerr(route, e) if e else jr(route, [r], 201)
        h = next(x for x in T['hx_holds'] if x['id'] == rid)
        if lvl('holds') < 3: return jerr(route, 'Only someone with Full access to Hold and Release can decide a hold (CSQ 2A.10.4).')
        if body['status'] == 'released' and h['kind'] == 'lot' and h['prev_status'] == 'rejected': return jerr(route, 'This lot was rejected at receiving.')
        if body['status'] == 'released' and h.get('batch_id') and failed(h['batch_id']): return jerr(route, 'This batch has a failed test and no passing retest after it. It cannot be released.')
        h.update(body); h['decided_by'] = 'Sam'; h['decided_at'] = now()
        if h['kind'] == 'lot':
            l = next(x for x in T['hx_lots'] if x['id'] == h['lot_id']); l['status'] = {'released': h['prev_status'] or 'quarantine', 'destroyed': 'destroyed', 'returned': 'returned'}.get(h['status'], 'quarantine')
        audit('hx_holds', h, 'UPDATE', 'Hold ' + h['status'] + ': ' + h['decision_notes']); return jr(route, [h])
    if tbl == 'hx_shipments':
        if m == 'POST':
            if not all(body['checks'].values()): return jerr(route, 'Every pre-load inspection check must pass')
            for it in body['items']:
                if any(h['status'] == 'open' and h.get('batch_id') == it['batch_id'] for h in T['hx_holds']): return jerr(route, 'on hold')
                if failed(it['batch_id']): return jerr(route, 'failed test')
            r = dict(body); r.update({'number': nxt('hx_shipments', 'SHP'), 'status': 'shipped', 'shipped_by': 'Sam', 'created_at': now(), 'checks_ok': True, 'delivered_on': None, 'cancel_reason': ''})
            T['hx_shipments'].append(r); audit('hx_shipments', r, 'INSERT', 'Shipped to ' + r['customer']); return jr(route, [r], 201)
        s = next(x for x in T['hx_shipments'] if x['id'] == rid); s.update(body); return jr(route, [s])
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def lot(n): return next(x for x in T['hx_lots'] if x['number'] == n)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Receiving and holds')
    check(pg.locator('.card', has_text='Receiving and holds').locator('text=0 on hold').count() == 1, 'dashboard card')
    pg.get_by_role('button', name='Receiving', exact=True).click(); pg.wait_for_selector('text=Nothing received yet')
    # receive lot 1 (all checks + COA)
    pg.get_by_role('button', name='+ Receive lot').click(); md = pg.locator('.md')
    opts = field(md, 'Supplier').locator('option').all_inner_texts()
    check(any('Futurola' in o for o in opts) and not any('Pending Paper' in o for o in opts), 'only approved suppliers can be picked')
    field(md, 'Supplier').select_option('s-ok'); check(md.locator('text=Specs this supplier must meet: Food-grade paper').count() == 1, 'supplier specs shown at receiving')
    field(md, 'Item received').fill('98mm cones'); field(md, 'Quantity').fill('1000'); field(md, 'Supplier lot #').fill('FU-7781'); field(md, 'Expiry / best before').fill('2028-01-01')
    for c in md.locator('label.ck input[type=checkbox]').all(): c.check()
    md.locator('input[type=file]').set_input_files({'name': 'coa.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4'}); pg.wait_for_selector('.md >> text=coa.pdf')
    md.get_by_role('button', name='Receive into quarantine').click(); pg.wait_for_selector('.msg >> text=Received RCV-2026-001 into quarantine')
    l1 = lot('RCV-2026-001'); check(l1['status'] == 'quarantine' and l1['coa_ok'] and l1['checks_ok'] and l1['files'][0]['name'] == 'coa.pdf', 'lot 1 in quarantine with COA, passed inspection, document')
    pg.locator('.md').get_by_role('button', name='Accept').click(); pg.locator('.md').get_by_role('button', name='Accept lot').click(); pg.wait_for_selector('.msg >> text=Accepted RCV-2026-001')
    check(lot('RCV-2026-001')['status'] == 'accepted', 'lot 1 accepted')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # lot 2: no COA, failed check
    pg.get_by_role('button', name='+ Receive lot').click(); md = pg.locator('.md')
    field(md, 'Supplier').select_option('s-ok'); field(md, 'Item received').fill('109mm cones'); field(md, 'Quantity').fill('500')
    for c in md.locator('label.ck input[type=checkbox]').all()[:5]: c.check()
    md.get_by_role('button', name='Receive into quarantine').click(); pg.wait_for_selector('.msg >> text=Received RCV-2026-002')
    pg.locator('.md').get_by_role('button', name='Accept').click(); md = pg.locator('.md')
    check(md.locator('text=No COA or certificate').count() == 1 and md.get_by_role('button', name='Accept lot').is_disabled() and md.locator('text=Not every receiving check passed').count() == 1, 'accept blocked without COA; failed checks listed')
    md.get_by_role('button', name='Cancel').click(); pg.locator('.md').get_by_role('button', name='Reject').click(); md = pg.locator('.md')
    md.get_by_role('button', name='Reject lot').click(); check(md.locator('.msg.err', has_text='rejected').count() == 1, 'reject needs a reason')
    md.locator('textarea').fill('Wet cartons, no COA'); md.get_by_role('button', name='Reject lot').click(); pg.wait_for_selector('.msg >> text=Rejected RCV-2026-002')
    check(lot('RCV-2026-002')['status'] == 'on_hold' and len(T['hx_holds']) == 1 and T['hx_holds'][0]['prev_status'] == 'rejected', 'rejected lot put on hold automatically')
    pg.locator('.md').get_by_role('button', name='Close').click()
    check(pg.locator('.tabs button', has_text='Hold and Release (1)').count() == 1 and pg.locator('.msg.err', has_text='1 item is on hold').count() == 1, 'hold count on tab + banner')
    check(pg.locator('tr', has_text='RCV-2026-002').locator('.badge', has_text='Failed').count() == 1, 'receiving list shows failed inspection')
    # inventory + use
    pg.locator('.tabs button', has_text='Inventory').click(); pg.wait_for_selector('td >> text=98mm cones')
    check(pg.locator('tr', has_text='RCV-2026-001').locator('text=Use first').count() == 1 and pg.locator('tr', has_text='RCV-2026-002').locator('.badge', has_text='On hold').count() == 1 and pg.locator('tr', has_text='RCV-2026-002').locator('text=Use first').count() == 0, 'inventory: accepted lot, FIFO badge; held lot not usable')
    pg.get_by_role('button', name='+ Record use').click(); md = pg.locator('.md')
    field(md, 'Lot').select_option(index=1); field(md, 'Used in batch').select_option('b-ok'); field(md, 'Quantity').fill('100'); md.get_by_role('button', name='Record use').click(); pg.wait_for_selector('.msg >> text=Use recorded')
    pg.wait_for_selector('text=900 / 1000 each', timeout=5000)
    check(lot('RCV-2026-001')['qty_used'] == 100 and pg.locator('tr', has_text='RCV-2026-001').first.locator('text=900 / 1000 each').count() == 1, 'use recorded: 900 left, linked to batch PR-100')
    # holds: decide rejected lot
    pg.locator('.tabs button', has_text='Hold and Release').click(); pg.locator('.card', has_text='HOLD-2026-001').click()
    pg.locator('.md').get_by_role('button', name='Decide').click(); md = pg.locator('.md')
    o = field(md, 'Decision').locator('option').all_inner_texts()
    check(not any('Release' in x for x in o) and any('Return to supplier' in x for x in o), 'rejected lot cannot be released, only returned/destroyed')
    field(md, 'Decision').select_option('returned'); field(md, 'Reason / evidence for the decision').fill('Returned to Futurola, RMA 55'); md.get_by_role('button', name='Save decision').click(); pg.wait_for_selector('.msg >> text=Decided HOLD-2026-001')
    check(lot('RCV-2026-002')['status'] == 'returned', 'lot returned to supplier')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # put batch on hold
    pg.get_by_role('button', name='+ Put on hold').click(); md = pg.locator('.md')
    field(md, 'What is held').select_option('batch'); field(md, 'Batch').select_option('b-ok'); field(md, 'Reason').fill('Odor complaint from Dispensary A'); field(md, 'Source').select_option('Complaint')
    md.get_by_role('button', name='Put on hold').click(); pg.wait_for_selector('.msg >> text=Put on hold: HOLD-2026-002')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # shipping blocked
    pg.locator('.tabs button', has_text='Shipping').click(); pg.get_by_role('button', name='+ New shipment').click(); md = pg.locator('.md')
    field(md, 'Customer').fill('Dispensary A'); md.locator('select').filter(has=pg.locator('option', has_text='(batch)')).first.select_option('b-ok')
    check(md.locator('text=On hold (HOLD-2026-002): cannot ship').count() == 1, 'shipping: held batch flagged')
    md.locator('select').filter(has=pg.locator('option', has_text='(batch)')).first.select_option('b-bad')
    check(md.locator('text=Failed test, no passing retest: cannot ship').count() == 1, 'shipping: failed-test batch flagged')
    for c in md.locator('label.ck input[type=checkbox]').all(): c.check()
    check(md.get_by_role('button', name='Record shipment').is_disabled(), 'record shipment disabled while a batch is blocked')
    md.get_by_role('button', name='Cancel').click()
    # release the batch hold, then ship
    pg.locator('.tabs button', has_text='Hold and Release').click(); pg.locator('.card', has_text='HOLD-2026-002').click(); pg.locator('.md').get_by_role('button', name='Decide').click(); md = pg.locator('.md')
    field(md, 'Decision').select_option('released'); field(md, 'Reason / evidence for the decision').fill('Retained sample checked, no off odor'); md.get_by_role('button', name='Save decision').click(); pg.wait_for_selector('.msg >> text=Decided HOLD-2026-002')
    pg.locator('.md').get_by_role('button', name='Close').click()
    pg.locator('.tabs button', has_text='Shipping').click(); pg.get_by_role('button', name='+ New shipment').click(); md = pg.locator('.md')
    field(md, 'Customer').fill('Dispensary A'); field(md, 'Customer license #').fill('DIS000123'); field(md, 'State manifest #').fill('0001234567')
    md.locator('select').filter(has=pg.locator('option', has_text='(batch)')).first.select_option('b-ok'); md.locator('input[placeholder="Package tag"]').fill('1A4000000000000000000777'); md.locator('input[placeholder=Qty]').fill('200')
    check(md.locator('text=Test passed').count() == 1, 'passed test shown')
    check(md.get_by_role('button', name='Record shipment').is_disabled(), 'pre-load checks required before recording')
    for c in md.locator('label.ck input[type=checkbox]').all(): c.check()
    md.get_by_role('button', name='Record shipment').click(); pg.wait_for_selector('.msg >> text=Shipment SHP-2026-001 recorded')
    sh = T['hx_shipments'][0]; check(sh['items'][0]['batch_number'] == 'PR-100' and sh['items'][0]['tag'].endswith('777') and sh['manifest_number'] == '0001234567', 'shipment traced to batch, tag and manifest')
    pg.locator('.md').get_by_role('button', name='Mark delivered').click(); pg.wait_for_selector('.msg >> text=Delivered SHP-2026-001')
    check(T['hx_shipments'][0]['status'] == 'delivered' and T['hx_shipments'][0]['delivered_on'] == TODAY, 'marked delivered')
    pg.locator('.md').get_by_role('button', name='Record return').click(); md = pg.locator('.md')
    check(field(md, 'What is held').input_value() == 'return' and field(md, 'Batch').input_value() == 'b-ok', 'return prefilled from shipment')
    field(md, 'Quantity held').fill('12 units'); field(md, 'Reason').fill('Leaking cartridges returned'); md.get_by_role('button', name='Put on hold').click(); pg.wait_for_selector('.msg >> text=Put on hold: HOLD-2026-003')
    check(T['hx_holds'][-1]['kind'] == 'return' and T['hx_holds'][-1]['shipment_id'] == sh['id'], 'customer return recorded as a hold linked to the shipment')
    pg.screenshot(path=OUT + 'holds.png')
    pg.locator('.md').get_by_role('button', name='Close').click()
    pg.locator('.tabs button', has_text='Shipping').click(); pg.wait_for_selector('tr >> text=SHP-2026-001'); pg.screenshot(path=OUT + 'shipping.png')
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Shipping log').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('Shipment SHP-2026-001' in html and 'PR-100' in html and 'Pre-load inspection' in html, 'printable shipping log')
    pg.locator('.tabs button', has_text='Receiving').click(); pg.wait_for_selector('tr >> text=RCV-2026-001')
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Receiving log').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('Receiving log' in html and 'Wet cartons' in html and 'Failed:' in html, 'printable receiving log with inspection results and decisions')
    pg.screenshot(path=OUT + 'receiving.png')
    # standards evidence
    T['hx_standards'].append({'id': 'st1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 'st1', 'target_level': 1, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    def clause(c):
        rr = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(c) + '$'))).first; rr.locator('div.row').first.click(); return rr
    r1 = clause('2A.10.2'); check(r1.locator('text=2 lots received').count() == 1, '2A.10.2 live receiving evidence')
    r2 = clause('2A.10.4'); check(r2.locator('text=1 open').count() >= 1 and r2.locator('text=1 customer return').count() >= 1, '2A.10.4 live hold evidence')
    r3 = clause('2A.10.1'); check(r3.locator('text=1 of 1 lines traced to a batch').count() == 1 and r3.locator('text=Inventory by lot').count() == 1, '2A.10.1 traceability evidence (back and forward)')
    # Edit-level
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'receiving': 'editor', 'holds': 'editor'}
    pg.reload(); pg.get_by_role('button', name='Receiving', exact=True).click(); pg.wait_for_selector('tr >> text=RCV-2026-001')
    check(pg.get_by_role('button', name='Shipping', exact=True).count() == 0 and pg.locator('.tabs button', has_text='Shipping').count() == 0, 'no shipping without access')
    pg.get_by_role('button', name='+ Receive lot').click(); md = pg.locator('.md'); field(md, 'Supplier').select_option('s-ok'); field(md, 'Item received').fill('Labels'); field(md, 'Quantity').fill('10')
    md.get_by_role('button', name='Receive into quarantine').click(); pg.wait_for_selector('.msg >> text=Received RCV-2026-003')
    pg.locator('.md').get_by_role('button', name='Put on hold').wait_for(timeout=8000)
    check(pg.locator('.md').get_by_role('button', name='Accept').count() == 0 and pg.locator('.md').get_by_role('button', name='Put on hold').count() == 1, 'Edit: can receive and hold, cannot accept')
    pg.locator('.md').get_by_role('button', name='Close').click(); pg.locator('.tabs button', has_text='Hold and Release').click(); pg.locator('.card', has_text='HOLD-2026-003').click()
    check(pg.locator('.md').get_by_role('button', name='Decide').count() == 0, 'Edit: cannot decide holds')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
