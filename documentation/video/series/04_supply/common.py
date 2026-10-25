# Shared setup for video 04 (supply): kit import, seed tweaks, and an emulation of the database triggers
# (numbering, who / when stamps, the server-side checks) for the supply tables, following
# /home/claude/hendrix/hendrix_step16/17/18.sql.
import os, sys, re, json, time, math, urllib.parse, datetime as _dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(HERE + '/../../kit'))
import hxvideo as hv
hv.set_project(HERE)
SNAP = os.path.abspath(HERE + '/../../index_snapshot2.html')
field = hv.field
ME = 'Sam Salari'
TODAY = '2026-10-24'
FIX_UTC = hv.FIXED_DAY.astimezone(_dt.timezone.utc)
# keep modals and page content clear of the burned-in captions (bottom ~120 CSS px)
CAP_CSS = '.main{padding-bottom:170px !important}.mo{padding:14px 14px 124px !important}.md{max-height:calc(100vh - 150px) !important}'
CLK = {'t0': time.time(), 'flow': False, 'n': 0}


def now_dt():
    if CLK['flow']:   # browser clock running from FIXED_DAY (recall scene)
        return FIX_UTC + _dt.timedelta(seconds=time.time() - CLK['t0'])
    CLK['n'] += 1     # browser clock fixed at FIXED_DAY: stamp just before it
    return FIX_UTC - _dt.timedelta(seconds=300 - CLK['n'])


def now_iso():
    return now_dt().strftime('%Y-%m-%dT%H:%M:%S.000Z')


def iso(d): return d.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def add_months(d, n):
    y, m = int(d[:4]), int(d[5:7]) + n
    y += (m - 1) // 12; m = (m - 1) % 12 + 1
    return '%04d-%02d-%s' % (y, m, d[8:10])


def failed_no_retest(T, bid):
    ts = [t for t in T['hx_tests'] if t.get('batch_id') == bid and not t.get('voided')]
    f = [t['created_at'] for t in ts if t['status'] == 'Failed']
    if not f: return False
    return not any(t['status'] == 'Passed' and t['created_at'] > max(f) for t in ts)


def setup():
    ns = hv.load_setup('supply', snapshot=SNAP); T = ns['T']
    CLK['t0'] = time.time(); CLK['flow'] = False; CLK['n'] = 0
    # a pre-roll batch started today (for recording use), and no exercise running yet
    T['hx_batches'].append({'id': 'b-pr2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'preroll', 'batch_number': 'PR-2026-1024', 'sku': 'Pre-roll 1g', 'flavor': 'Blue Dream',
                            'status': '', 'voided': False, 'created_at': '2026-10-24T13:30:00Z', 'data': {}})
    T['hx_recalls'] = [r for r in T['hx_recalls'] if r['status'] != 'open']
    T['hx_suppliers'].append(ns['sup']('s-vvs', 'Valley Vape Supply', 'Packaging', 'disqualified', 'medium', '510 cartridges (2025)', 'Lead-free solder; heavy-metal leach COA per lot',
                                       ('Tom Reyes', 'sales@valleyvape.example', '(555) 777-3030'), approval_basis='Spec sheet reviewed', approved_by=ME, approved_at='2025-06-02T15:00:00Z',
                                       status_reason='Lead found in cartridge solder; two failed leach tests in 2025', last_review='2025-11-04'))
    install(ns)
    return ns


def install(ns):
    T = ns['T']; base = ns['handle']

    def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))

    def err(route, m): return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': m, 'code': 'P0001'}))

    def nxt(tbl, prefix):
        ns_ = [int(x['number'].split('-')[-1]) for x in T[tbl] if x.get('number', '').startswith(prefix + '-2026-')]
        return '%s-2026-%03d' % (prefix, 1 + max(ns_ or [0]))

    def find(tbl, rid): return next((x for x in T[tbl] if x['id'] == rid), None)

    def handle(route, request):
        u = request.url; m = request.method; path = urllib.parse.urlparse(u).path
        if '/rest/v1/' not in u or '/rpc/' in u or m not in ('POST', 'PATCH'): return base(route, request)
        tbl = path.split('/')[-1]
        if tbl not in ('hx_suppliers', 'hx_supplier_reviews', 'hx_lots', 'hx_lot_uses', 'hx_holds', 'hx_shipments', 'hx_recalls'): return base(route, request)
        b = json.loads(request.post_data or '{}'); now = now_iso()
        if m == 'POST':
            b = dict(b); b['created_at'] = now
            if tbl == 'hx_suppliers':
                if any(x['name'].strip().lower() == b['name'].strip().lower() for x in T[tbl]): return err(route, 'duplicate key value violates unique constraint "hx_suppliers_name"')
                lids = b.get('license_ids') or []
                if b['license_id'] not in lids: b['license_ids'] = [b['license_id']] + lids
                b.update({'ever_approved': False, 'approved_by': '', 'approved_at': None, 'last_review': None, 'next_review': None, 'approval_basis': '', 'status_reason': '',
                          'certificates': [], 'created_by': ME})
            elif tbl == 'hx_supplier_reviews':
                s = find('hx_suppliers', b['supplier_id'])
                if b['review_date'] > TODAY: return err(route, 'The review date cannot be in the future.')
                if b['result'] in ('Suspend', 'Disqualify') and not b.get('notes', '').strip(): return err(route, 'Write the reason in the review notes.')
                b['reviewer'] = ME; b.setdefault('files', [])
                r = b['result']
                st = (s['status'] if s['status'] in ('pending', 'emergency', 'suspended') else 'approved') if r == 'Keep approved' else 'conditional' if r == 'Approve with conditions' else 'suspended' if r == 'Suspend' else 'disqualified'
                s.update({'last_review': b['review_date'], 'next_review': add_months(b['review_date'], 6 if s['risk'] == 'high' else 12), 'status': st})
                if st in ('suspended', 'disqualified'): s['status_reason'] = b['notes']
            elif tbl == 'hx_lots':
                s = find('hx_suppliers', b.get('supplier_id'))
                if not s: return err(route, 'That supplier is not on file for this license.')
                if s['status'] not in ('approved', 'conditional', 'emergency'):
                    return err(route, '%s is %s - receive only from approved suppliers (CSQ 2A.11).' % (s['name'], 'not approved yet' if s['status'] == 'pending' else s['status']))
                ck = b.get('checks') or {}
                b.update({'number': nxt('hx_lots', 'RCV'), 'supplier_name': s['name'], 'supplier_status': s['status'], 'received_by': ME, 'qty_used': 0, 'decided_by': '', 'decided_at': None,
                          'decision_notes': '', 'checks_ok': bool(ck) and all(v is True for v in ck.values()), 'status': 'quarantine'})
            elif tbl == 'hx_lot_uses':
                l = find('hx_lots', b['lot_id'])
                if l['status'] != 'accepted':
                    return err(route, 'Lot %s is %s and cannot be used.' % (l['number'], {'quarantine': 'still in quarantine (not accepted yet)', 'on_hold': 'on hold'}.get(l['status'], l['status'])))
                if l.get('expiry_date') and l['expiry_date'] < b['used_on']: return err(route, 'Lot %s expired on %s and cannot be used.' % (l['number'], l['expiry_date']))
                left = l['quantity'] - l['qty_used']
                if b['quantity'] > left: return err(route, 'Only %s %s left in lot %s.' % (('%g' % left), l['unit'], l['number']))
                if b.get('batch_id'): b['batch_number'] = find('hx_batches', b['batch_id'])['batch_number']
                b.update({'used_by': ME, 'voided': False}); l['qty_used'] = l['qty_used'] + b['quantity']
            elif tbl == 'hx_holds':
                b.update({'number': nxt('hx_holds', 'HOLD'), 'placed_by': ME, 'status': 'open', 'decided_by': '', 'decided_at': None, 'decision_notes': '', 'deviation_id': None})
                b.setdefault('prev_status', '')
                if b['kind'] == 'lot':
                    l = find('hx_lots', b.get('lot_id'))
                    if not l: return err(route, 'Pick the lot to put on hold.')
                    if l['status'] in ('returned', 'destroyed'): return err(route, 'Lot %s is already %s.' % (l['number'], l['status']))
                    if l['status'] == 'on_hold': return err(route, 'Lot %s is already on hold.' % l['number'])
                    b['prev_status'] = l['status']; b['item'] = b.get('item') or '%s (%s)' % (l['item'], l['number']); l['status'] = 'on_hold'
                elif b.get('batch_id'):
                    bt = find('hx_batches', b['batch_id']); b['item'] = b.get('item') or '%s batch %s' % (bt['sku'] or bt['batch_type'], bt['batch_number'])
                if not (b.get('item') or '').strip(): b['item'] = b.get('tag') or 'Held item'
            elif tbl == 'hx_shipments':
                ck = b.get('checks') or {}; b['checks_ok'] = bool(ck) and all(v is True for v in ck.values())
                if not b['checks_ok']: return err(route, 'Every pre-load inspection check must pass before loading (CSQ 2A.9.4). Fix the problem first.')
                for it in b['items']:
                    bt = find('hx_batches', it['batch_id'])
                    if any(h['status'] == 'open' and (h.get('batch_id') == bt['id'] or (it.get('tag') and h.get('tag') == it['tag'])) for h in T['hx_holds']):
                        return err(route, 'Batch %s is on hold and cannot be shipped (CSQ 2A.10.4).' % bt['batch_number'])
                    if failed_no_retest(T, bt['id']): return err(route, 'Batch %s has a failed test and no passing retest. It cannot be shipped.' % bt['batch_number'])
                b.update({'number': nxt('hx_shipments', 'SHP'), 'shipped_by': ME, 'status': 'shipped', 'delivered_on': None, 'cancel_reason': ''})
            elif tbl == 'hx_recalls':
                b.update({'number': nxt('hx_recalls', 'MOCK' if b['kind'] == 'mock' else 'RCL'), 'started_at': now, 'ended_at': None, 'duration_minutes': None, 'status': 'open', 'result': '',
                          'cancel_reason': '', 'closed_by': '', 'started_by': ME, 'step_times': {}, 'notified': b.get('notified', []), 'trace': b.get('trace', {}), 'files': b.get('files', []),
                          'qty_made': b.get('qty_made', ''), 'qty_on_hand': '', 'qty_recovered': '', 'findings': '', 'actions': ''})
            T[tbl].insert(0, b); print('EMU POST', tbl, b.get('number', b.get('id')))
            return jr(route, [b], 201)
        # PATCH
        rid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); row = find(tbl, rid)
        new = {**row, **b}
        if tbl == 'hx_suppliers':
            if new['status'] != row['status']:
                if new['status'] in ('approved', 'conditional') and row['status'] not in ('approved', 'conditional'):
                    if not (new.get('approval_basis') or '').strip(): return err(route, 'Record what the approval is based on (questionnaire, certificates, COA review, audit...).')
                    if new['category'] == 'Testing Lab' and not any(c['kind'] == 'ISO/IEC 17025 accreditation' for c in new.get('credentials') or []):
                        return err(route, 'A testing lab needs its ISO/IEC 17025 accreditation recorded before approval (CSQ 2A.12.9 g).')
                    new.update({'approved_by': ME, 'approved_at': now, 'ever_approved': True})
                    new['next_review'] = new.get('next_review') or add_months(TODAY, 6 if new['risk'] == 'high' else 12)
                elif new['status'] in ('suspended', 'disqualified') and not (new.get('status_reason') or '').strip():
                    return err(route, 'A reason is required to %s a supplier.' % ('suspend' if new['status'] == 'suspended' else 'disqualify'))
        elif tbl == 'hx_lots':
            if new['status'] != row['status']:
                if row['status'] == 'on_hold' or new['status'] in ('on_hold', 'returned', 'destroyed'): return err(route, 'This lot is controlled by its hold. Decide the hold under Hold and Release.')
                if row['status'] != 'quarantine': return err(route, 'Only a lot in quarantine can be accepted or rejected.')
                if new['status'] == 'rejected' and not new.get('decision_notes', '').strip(): return err(route, 'Write why the lot is rejected.')
                if new['status'] == 'accepted':
                    if not new.get('coa_ok'): return err(route, 'The lot needs its COA or certificate of conformance before it can be accepted (CSQ 2A.10.2).')
                    if not new.get('checks_ok') and not new.get('decision_notes', '').strip(): return err(route, 'The receiving inspection did not pass every check. Write why the lot is still accepted, or reject it.')
                    if new.get('supplier_status') == 'emergency' and not new.get('decision_notes', '').strip(): return err(route, 'This lot is from an emergency supplier. Write how it was verified before use (CSQ 2A.11 g).')
                new.update({'decided_by': ME, 'decided_at': now})
                if new['status'] == 'rejected':
                    T['hx_holds'].insert(0, {'id': 'hold-r' + rid, 'state_id': row['state_id'], 'license_id': row['license_id'], 'number': nxt('hx_holds', 'HOLD'), 'kind': 'lot', 'lot_id': rid, 'batch_id': None,
                                             'tag': '', 'item': '%s (%s)' % (row['item'], row['number']), 'quantity': '%s %s' % (row['quantity'], row['unit']), 'source': 'Receiving inspection',
                                             'reason': 'Rejected at receiving: ' + new['decision_notes'], 'location': row.get('location', ''), 'prev_status': 'rejected', 'status': 'open',
                                             'decision_notes': '', 'decided_by': '', 'decided_at': None, 'placed_by': ME, 'created_at': now, 'deviation_id': None, 'shipment_id': None})
            elif 'checks' in b:
                ck = new.get('checks') or {}; new['checks_ok'] = bool(ck) and all(v is True for v in ck.values())
        elif tbl == 'hx_lot_uses':
            if b.get('voided') and not row.get('voided'):
                l = find('hx_lots', row['lot_id']); l['qty_used'] = max(0, l['qty_used'] - row['quantity'])
        elif tbl == 'hx_holds':
            if row['status'] != 'open': return err(route, 'This hold was already decided (%s) and cannot be changed.' % row['status'])
            if new['status'] != 'open':
                if not new.get('decision_notes', '').strip(): return err(route, 'Write the reason for the decision.')
                if new['status'] == 'released' and new['kind'] == 'lot' and row.get('prev_status') == 'rejected': return err(route, 'This lot was rejected at receiving. Return it to the supplier or destroy it.')
                if new['status'] == 'released' and new.get('batch_id') and failed_no_retest(T, new['batch_id']):
                    return err(route, 'This batch has a failed test and no passing retest after it. It cannot be released.')
                new.update({'decided_by': ME, 'decided_at': now})
                if new['kind'] == 'lot':
                    l = find('hx_lots', new['lot_id'])
                    l['status'] = {'released': row.get('prev_status') or 'quarantine', 'destroyed': 'destroyed', 'returned': 'returned'}.get(new['status'], 'quarantine')
        elif tbl == 'hx_shipments':
            if row['status'] == 'cancelled': return err(route, 'This shipment is cancelled.')
            if new['status'] == 'delivered' and row['status'] != 'delivered': new['delivered_on'] = new.get('delivered_on') or TODAY
            if new['status'] == 'cancelled' and not new.get('cancel_reason', '').strip(): return err(route, 'A reason is required to cancel a shipment.')
        elif tbl == 'hx_recalls':
            if row['status'] != 'open': return err(route, 'This %s is %s and cannot be changed.' % ('mock recall' if row['kind'] == 'mock' else row['kind'], row['status']))
            stt = dict(row.get('step_times') or {})
            for k, v in (new.get('steps') or {}).items():
                if v is True and not (row.get('steps') or {}).get(k) and k not in stt: stt[k] = now
            new['step_times'] = stt
            if new['status'] == 'closed':
                if not new.get('findings', '').strip(): return err(route, 'Write the findings before closing.')
                allv = bool(new['steps']) and all(v is True for v in new['steps'].values())
                dur = math.ceil((now_dt() - _dt.datetime.fromisoformat(row['started_at'].replace('Z', '+00:00'))).total_seconds() / 60)
                if row['kind'] != 'mock' and not allv: return err(route, 'Complete every recall step before closing.')
                new.update({'ended_at': now, 'closed_by': ME, 'duration_minutes': dur, 'result': ('Pass' if allv and dur <= 120 else 'Fail') if row['kind'] == 'mock' else 'Completed'})
        row.clear(); row.update(new); print('EMU PATCH', tbl, row.get('number', rid), {k: b[k] for k in b if k in ('status',)})
        return jr(route, [row])

    ns['handle'] = handle
    return ns


def open_app(b, ns, name, menu=None, wait=None, **kw):
    """Logged-in context on the dashboard (or a page), recorder created but not started."""
    kw.setdefault('session', hv.session_script())
    ctx = hv.new_context(b, ns, **kw)
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.add_style_tag(content=CAP_CSS); pg.wait_for_timeout(600)
    if menu:
        nav(pg, menu).click(); pg.wait_for_selector(wait); pg.wait_for_timeout(800)
    r = hv.Rec(ctx, pg, name)
    return ctx, pg, r


def nav(pg, name):
    return pg.locator('.nav').get_by_role('button', name=name, exact=True).first


def close_modals(r, pg):
    for _ in range(4):
        if not pg.locator('.md').count(): return
        r.click(pg.locator('.md').last.get_by_role('button', name=re.compile('^(Close|Cancel|Back)$')).last, after=0.3)
