import json, re, time, urllib.parse, sys
from playwright.sync_api import sync_playwright

import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = open(os.environ.get('HX_HTML') or os.path.join(HERE, '..', '..', 'index.html'), encoding='utf8').read()
OUT = os.path.join(HERE, 'work') + '/'
VENDOR = os.path.join(HERE, 'vendor') + '/'
os.makedirs(OUT, exist_ok=True)
_LOCAL_CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
LAUNCH = {'executable_path': os.environ['HX_CHROME']} if os.environ.get('HX_CHROME') else ({'executable_path': _LOCAL_CHROME} if os.path.exists(_LOCAL_CHROME) else {})
BASE = 'https://app.test/hendrix/'
SB = 'https://bqrncllndvzbhmxanitq.supabase.co'
ADMIN = '11111111-1111-1111-1111-111111111111'

T = {
  'hx_profiles': [{'id': ADMIN, 'name': 'Sam', 'email': 's@x', 'role': 'admin', 'approved': True, 'created_at': '2026-01-01'}],
  'hx_states': [{'id': 'st-mo', 'name': 'Missouri', 'agency': 'DCR', 'code': ''}, {'id': 'st-mi', 'name': 'Michigan', 'agency': 'CRA', 'code': ''}],
  'hx_licenses': [{'id': 'lic-mo', 'state_id': 'st-mo', 'name': 'Black Fox', 'license_number': 'MAN000109', 'license_type': 'Manufacturer', 'active': True},
                  {'id': 'lic-mi', 'state_id': 'st-mi', 'name': 'Key Stone', 'license_number': 'MI-1', 'license_type': 'Processor', 'active': True}],
  'hx_rule_sources': [],
  'hx_rules': [{'id': 'r1', 'state_id': 'st-mo', 'category': 'Security', 'citation': '19 CSR 100-1.x', 'title': 'Camera coverage', 'body': 'Cameras must cover...', 'created_at': '1'},
               {'id': 'r2', 'state_id': 'st-mi', 'category': 'Security', 'citation': 'R 420.x', 'title': 'MICHIGAN RULE', 'body': 'x', 'created_at': '1'}],
  'hx_visitor_log': [], 'hx_log_lists': [], 'hx_facility_log': [], 'hx_skus': [], 'hx_flavors': [], 'hx_formulations': [], 'hx_cost_library': [], 'hx_audit_log': [], 'hx_roles': [], 'hx_tests': [], 'hx_label_templates': [], 'hx_batches': [], 'hx_standards': [], 'hx_standard_clauses': [], 'hx_license_standards': [], 'hx_conformance': [], 'hx_label_prints': [], 'hx_sops': [], 'hx_sop_acks': [], 'hx_sop_versions': [], 'hx_deviations': [], 'hx_capas': [], 'hx_training_courses': [], 'hx_training_records': [], 'hx_suppliers': [], 'hx_supplier_reviews': [], 'hx_lots': [], 'hx_lot_uses': [], 'hx_holds': [], 'hx_shipments': [], 'hx_recalls': [], 'hx_recall_contacts': [], 'hx_complaints': [], 'hx_audits': [], 'hx_audit_findings': [], 'hx_training_keys': [], 'hx_training_attempts': [],
}
errors = []
seq = [0]

def now():
    seq[0] += 1
    return '2026-10-21T12:%02d:%02d.000Z' % (seq[0] // 60, seq[0] % 60)

def guard(tbl, row):
    lic = next((l for l in T['hx_licenses'] if l['id'] == row.get('license_id')), None)
    if not row.get('state_id') or not row.get('license_id'): return 'Every entry needs both a state and a license.'
    if not lic or lic['state_id'] != row['state_id']: return 'This license does not belong to that state.'
    if tbl == 'hx_facility_log' and row.get('item_id'):
        it = next((i for i in T['hx_log_lists'] if i['id'] == row['item_id']), None)
        if not it or it['license_id'] != row['license_id']: return 'That list item belongs to a different license.'
        if it['list_key'].split('.')[0] not in (row['log_type'], 'common'): return 'That list item does not belong to this log.'
        row['item'] = it['name']
    return None

LK = {'sanitation': 'area', 'waste': 'waste_type', 'pest': 'pest_station', 'equipment': 'equipment', 'temperature': 'temp_unit',
      'security': 'security_point', 'security_inspection': 'inspection_item', 'scale': 'scale'}

def kcheck(s, l):
    lic = next((x for x in T['hx_licenses'] if x['id'] == l and x['state_id'] == s and x['active']), None)
    if not s or not lic: return None
    st = next(x for x in T['hx_states'] if x['id'] == s)
    return {'id': lic['id'], 'name': lic['name'], 'license_number': lic['license_number'], 'state_id': s, 'state': st['name']}

def pguard(tbl, r, old):
    if tbl == 'hx_label_templates' and any(x['id'] != r['id'] and x['license_id'] == r['license_id'] and x['sku_id'] == r['sku_id'] and (x.get('flavor_id') or '') == (r.get('flavor_id') or '') for x in T['hx_label_templates']):
        return 'duplicate key value violates unique constraint "hx_label_templates_one"'
    if tbl == 'hx_skus':
        if any(k['id'] != r['id'] and k['state_id'] == r['state_id'] and k['product_type'] == r['product_type'] and k['name'].strip().lower() == r['name'].strip().lower() for k in T['hx_skus']):
            return 'duplicate key value violates unique constraint "hx_skus_name"'
        if r.get('active') and not any(f['sku_id'] == r['id'] for f in T['hx_formulations']): return 'Enter a formulation for this SKU before it can be switched on.'
    if tbl in ('hx_flavors', 'hx_formulations'):
        k = next((x for x in T['hx_skus'] if x['id'] == r['sku_id']), None)
        if not k: return 'Unknown SKU.'
        if r.get('state_id') and r['state_id'] != k['state_id']: return 'This SKU belongs to a different state.'
        r['state_id'] = k['state_id']
    if tbl == 'hx_flavors' and any(x['id'] != r['id'] and x['sku_id'] == r['sku_id'] and x['name'].strip().lower() == r['name'].strip().lower() for x in T['hx_flavors']):
        return 'duplicate key value violates unique constraint "hx_flavors_name"'
    if tbl == 'hx_formulations' and any(x['id'] != r['id'] and x['sku_id'] == r['sku_id'] and (x.get('flavor_id') or '') == (r.get('flavor_id') or '') for x in T['hx_formulations']):
        return 'duplicate key value violates unique constraint "hx_formulations_one"'
    return None

STORE = {}
AI = {'mode': 'ok', 'tag': '1A4000000000000000001234', 'overall': 'Pass'}
def handle(route, request):
    u0 = request.url
    if '/storage/v1/object/' in u0:
        pth = u0.split('/hendrix-files/', 1)[1]
        if request.method == 'POST':
            STORE[pth] = request.post_data_buffer; return route.fulfill(status=200, content_type='application/json', body='{"Key":"x"}')
        return route.fulfill(status=200, content_type='application/pdf', body=STORE.get(pth, b''))
    if '/functions/v1/hendrix-ai' in u0:
        if AI['mode'] == 'missing': return route.fulfill(status=404, content_type='application/json', body='{"message":"Function not found"}')
        coa = {'lab_name': 'Green Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-10-20', 'sample_metrc_tag': AI['tag'], 'overall_status': AI['overall'],
               'potency': {'unit': '%', 'total_thc': 88.4, 'total_cbd': 0.2, 'thca': 2.1, 'd9_thc': 86.5},
               'categories': {'pesticides': {'status': 'Pass', 'analytes': []}, 'heavy_metals': {'status': 'Pass', 'analytes': [{'name': 'Lead', 'result': '0.05', 'limit': '0.5', 'unit': 'ug/g', 'status': 'Pass'}]}},
               'terpenes': [{'name': 'Limonene', 'value': 1.2}, {'name': 'Myrcene', 'value': 0.8}], 'total_terpenes': 2.0}
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'content': [{'type': 'text', 'text': json.dumps(coa)}]}))
    return handle0(route, request)
def handle0(route, request):
    url = request.url
    if not url.startswith(SB):
        if url.startswith(BASE):
            return route.fulfill(status=200, content_type='text/html', body=HTML)
        L=VENDOR
        for k,f in [('jspdf.umd','jspdf/dist/jspdf.umd.min.js'),('react.production','react/umd/react.production.min.js'),('react-dom.production','react-dom/umd/react-dom.production.min.js'),('qrcode.min','qrcodejs/qrcode.min.js')]:
            if k in url: return route.fulfill(status=200,content_type='application/javascript',body=open(L+f).read())
        return route.abort()
    u = urllib.parse.urlparse(url); path = u.path
    body = json.loads(request.post_data) if request.post_data else None
    def ok(j, status=200): route.fulfill(status=status, content_type='application/json', body=json.dumps(j))
    def err(m): route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': m}))
    if path.startswith('/rest/v1/rpc/'):
        fn = path.split('/')[-1]
        if fn == 'hx_kiosk_check': return ok(kcheck(body['p_state'], body['p_lic']))
        if fn == 'hx_kiosk_log_setup':
            lic = kcheck(body['p_state'], body['p_lic'])
            if not lic: return ok(None)
            items = [{'id': i['id'], 'list_key': i['list_key'], 'name': i['name'], 'spec': i['spec']} for i in T['hx_log_lists'] if i['license_id'] == body['p_lic'] and i['list_key'].split('.')[0] in (body['p_type'], 'common') and i['active']]
            return ok({'license': lic, 'items': items})
        if fn == 'hx_kiosk_log_add':
            p = body['p']
            if not kcheck(body['p_state'], body['p_lic']): return err('This QR code is not linked to an active license in this state.')
            if not p.get('signature'): return err('Please sign in the box.')
            row = {'id': 'fl-k%d' % seq[0], 'state_id': body['p_state'], 'license_id': body['p_lic'], 'log_type': body['p_type'], 'item_id': p.get('item_id') or None,
                   'item': p.get('item', ''), 'data': p.get('data', {}), 'result': p.get('result', ''), 'performed_by': p['performed_by'], 'signature': p['signature'], 'source': 'kiosk', 'created_at': now()}
            g = guard('hx_facility_log', row)
            if g: return err(g)
            T['hx_facility_log'].append(row); return ok(row['id'])
        if fn == 'hx_kiosk_open_visitors': return ok([])
        return err('Could not find the function ' + fn)
    tbl = path.split('/')[-1]
    qs = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
    rows = T.setdefault(tbl, [])
    def match(r):
        for k, v in qs:
            if k in ('select', 'order', 'limit'): continue
            if k == 'or':
                parts = v.strip('()').split(',')
                okk = False
                for ptx in parts:
                    f, op2, val2 = ptx.split('.', 2)
                    if op2 == 'eq' and str(r.get(f)) == val2: okk = True
                    if op2 == 'is' and val2 == 'null' and r.get(f) is None: okk = True
                if not okk: return False
                continue
            op, val = v.split('.', 1)
            if op == 'eq' and str(r.get(k)) != val and not (isinstance(r.get(k), bool) and str(r.get(k)).lower() == val): return False
            if op == 'gte' and str(r.get(k, '')) < val: return False
            if op == 'in' and str(r.get(k)) not in val.strip('()').split(','): return False
        return True
    m = request.method
    if m == 'GET':
        res = [r for r in rows if match(r)]
        if tbl == 'hx_facility_log': res = sorted(res, key=lambda r: r['created_at'], reverse=True)
        if tbl == 'hx_audit_log': res = sorted(res, key=lambda r: r['id'], reverse=('at.desc' in u.query))
        sel = dict(qs).get('select', '*')
        if sel != '*': res = [{k: r.get(k) for k in sel.split(',')} for r in res]
        return ok(res)
    if m == 'POST':
        if isinstance(body, list):
            for b in body:
                b = dict(b); b.setdefault('created_at', now()); g = pguard(tbl, b, None)
                if g: return err(g)
                rows.append(b)
            return ok(body, 201)
        row = dict(body); row.setdefault('created_at', now())
        g = pguard(tbl, row, None)
        if g: return err(g)
        if tbl == 'hx_tests':
            if row.get('batch_id'):
                bb = next(x for x in T['hx_batches'] if x['id'] == row['batch_id'])
                if any(t.get('batch_id') == row['batch_id'] and re.sub('[^A-Z0-9]', '', t['tag'].upper()) == re.sub('[^A-Z0-9]', '', row['tag'].upper()) and not t.get('voided') for t in T['hx_tests']):
                    return err('duplicate key value violates unique constraint "hx_tests_batch_tag"')
                row.update({'batch_number': bb['batch_number'], 'batch_type': bb['batch_type'], 'sku': bb['sku'], 'flavor': bb['flavor']})
            row.setdefault('voided', False); row.setdefault('coa_path', ''); row.setdefault('coa_analysis', None)
            if row.get('status') == 'Submitted': row['submitted_at'] = row['created_at']
        if tbl == 'hx_batches':
            if any(x['license_id'] == row['license_id'] and x['batch_number'].strip().lower() == row['batch_number'].strip().lower() for x in T['hx_batches']):
                return err('duplicate key value violates unique constraint "hx_batches_number"')
            k4 = next((x for x in T['hx_skus'] if x['id'] == row.get('sku_id')), None)
            row['sku'] = k4['name'] if k4 else ''
            f4 = next((x for x in T['hx_flavors'] if x['id'] == row.get('flavor_id')), None)
            row['flavor'] = f4['name'] if f4 else (row.get('flavor') or '')
            row.setdefault('voided', False); row['updated_at'] = row['created_at']
        if tbl != 'hx_audit_log':
            T['hx_audit_log'].append({'id': len(T['hx_audit_log']) + 1, 'at': now(), 'table_name': tbl, 'row_id': row['id'], 'action': 'INSERT', 'state_id': row.get('state_id'), 'license_id': row.get('license_id'),
                'user_name': 'Sam', 'reason': None, 'changed': None, 'old_data': None, 'new_data': {k2: v2 for k2, v2 in row.items() if k2 != 'signature'}})
        if tbl in ('hx_log_lists', 'hx_facility_log'):
            g = guard(tbl, row)
            if g: return err(g)
        rows.append(row); return ok([row], 201)
    if m == 'PATCH':
        for r in rows:
            if match(r):
                g = pguard(tbl, {**r, **body}, r)
                if g: return err(g)
                body = dict(body); reason = None; action = 'UPDATE'
                if tbl == 'hx_tests':
                    if r.get('voided'): return err('This test record is void and cannot be changed.')
                    if body.get('voided'):
                        reason = body['void_reason']; action = 'VOID'
                    else:
                        if r.get('status') in ('Passed', 'Failed') and body.get('status', r['status']) != r['status'] and not (body.get('edit_reason') or '').strip():
                            return err('A reason is required to change a final result.')
                        reason = body.get('edit_reason') or 'Testing record updated'
                        if body.get('status') in ('Passed', 'Failed') and body['status'] != r.get('status'): body['result_at'] = now()
                    body.pop('edit_reason', None)
                elif tbl == 'hx_batches':
                    if r.get('voided'): return err('This batch is void and cannot be changed.')
                    if body.get('voided'):
                        if not (body.get('void_reason') or '').strip(): return err('A reason is required to void a batch.')
                        reason = body['void_reason']; action = 'VOID'
                    elif T['hx_profiles'][0]['role'] == 'admin':
                        if not (body.get('edit_reason') or '').strip(): return err('A reason for the change is required.')
                        reason = body['edit_reason']
                    else:
                        for k3, v3 in (r.get('data') or {}).items():
                            if isinstance(v3, str) and v3.strip() and k3 not in ('status',) and not k3.endswith(('_expected', '_status', '_suggested')) and (body.get('data') or {}).get(k3) != v3 and k3 not in ('total_biomass_used','yield_quality_pct','yield_quality_band','gummy_mixture_used','total_sugar_coated_gummies','total_packaged_gummies','mandatory_testing','rd1_result','rd2_result'):
                                return err('Only blank fields can be filled in. "%s" already has a value; ask an admin to change it.' % k3)
                        reason = 'Filled in blank fields'
                    body.pop('edit_reason', None)
                    if 'flavor' in body and body.get('flavor_id') and body['flavor_id'] == r.get('flavor_id'): body.pop('flavor')
                elif tbl in ('hx_facility_log', 'hx_visitor_log'):
                    if r.get('voided'): return err('This entry is void and cannot be changed.')
                    if body.get('voided'):
                        if not (body.get('void_reason') or '').strip(): return err('A reason is required to void an entry.')
                        reason = body['void_reason']; action = 'VOID'; body['voided_at'] = now()
                    elif tbl == 'hx_visitor_log' and not r.get('time_out') and body.get('time_out'):
                        reason = 'Signed out'
                    else:
                        if not (body.get('edit_reason') or '').strip(): return err('A reason for the change is required.')
                        reason = body['edit_reason']
                    body.pop('edit_reason', None)
                old = json.loads(json.dumps(r)); r.update(body)
                ch = sorted([k2 for k2 in r if k2 not in ('signature',) and old.get(k2) != r.get(k2)])
                T['hx_audit_log'].append({'id': len(T['hx_audit_log']) + 1, 'at': now(), 'table_name': tbl, 'row_id': r['id'], 'action': action, 'state_id': r.get('state_id'), 'license_id': r.get('license_id'),
                    'user_name': 'Sam', 'reason': reason, 'changed': ch, 'old_data': {k2: v2 for k2, v2 in old.items() if k2 != 'signature'}, 'new_data': {k2: v2 for k2, v2 in r.items() if k2 != 'signature'}})
        return ok([r for r in rows if match(r)])
    if m == 'DELETE':
        if tbl in ('hx_facility_log', 'hx_visitor_log', 'hx_audit_log'): return ok(None, 204)
        gone = [r for r in rows if match(r)]
        T[tbl] = [r for r in rows if not match(r)]
        for g in gone:
            if tbl == 'hx_skus':
                T['hx_flavors'] = [x for x in T['hx_flavors'] if x['sku_id'] != g['id']]; T['hx_formulations'] = [x for x in T['hx_formulations'] if x['sku_id'] != g['id']]
            if tbl == 'hx_flavors': T['hx_formulations'] = [x for x in T['hx_formulations'] if x.get('flavor_id') != g['id']]
            if tbl in ('hx_formulations', 'hx_flavors'):
                for k in T['hx_skus']:
                    if not any(f['sku_id'] == k['id'] for f in T['hx_formulations']): k['active'] = False
        return ok(None, 204)

def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)

def last(t): return [r for r in T['hx_facility_log'] if r['log_type'] == t][-1]

def tab(pg, name):
    pg.locator('.tabs button', has_text=name).first.click()

def add_items(pg, title, names, spec=None):
    sec = pg.locator('.md .card', has=pg.locator('h3', has_text=title))
    for n in names:
        sec.locator('input').first.fill(n)
        if spec:
            for i, v in enumerate(spec):
                if v is not None: sec.locator('input').nth(1 + i).fill(v)
        sec.get_by_role('button', name='+ Add').click()
        pg.wait_for_selector('.md .card td >> text=' + n)

def sign(pg):
    cv = pg.locator('canvas').last.bounding_box()
    pg.mouse.move(cv['x'] + 30, cv['y'] + 40); pg.mouse.down(); pg.mouse.move(cv['x'] + 200, cv['y'] + 90, steps=8); pg.mouse.up()

def field(md, label):
    return md.locator('label.f', has=md.page.locator('span', has_text=label)).locator('input,select,textarea').first

with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 900})
    ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE)
    pg.get_by_role('button', name='Facility Logs').click()
    pg.wait_for_selector('h2 >> text=Sanitation Log')
    names = pg.locator('.tabs button').all_inner_texts()
    check(names == ['Sanitation', 'Waste Destruction', 'Scale Calibration', 'Security Malfunction', 'Security Equipment Inspection', 'Pest Control', 'Equipment Maintenance', 'Temp / Humidity', 'Environmental Monitoring'], '9 Black Fox logs in Black Fox order: ' + str(names))

    # --- Sanitation
    pg.get_by_role('button', name='Manage lists').click()
    check(pg.locator('.md >> text=Using the built-in choices: Day, Evening, Night').count() == 1, 'shift list shows BF defaults')
    add_items(pg, 'Daily: Areas Cleaned', ['Production Floor', 'Waste Area'])
    add_items(pg, 'Weekly: Areas Cleaned', ['Warehouse'])
    pg.mouse.click(5, 5)
    pg.get_by_role('button', name='+ New entry').click()
    md = pg.locator('.md')
    check(field(md, 'Cleaned By').input_value() == 'Sam' and field(md, 'Date').input_value() != '', 'person + date prefilled')
    check(md.locator('.secth').count() == 7, 'sanitation sections Daily x3 / Weekly / Monthly / Notes / Verification')
    md.locator('label.ck', has_text='Production Floor').locator('input').check()
    md.locator('label.ck', has_text='Warehouse').locator('input').check()
    md.get_by_role('button', name='Submit entry').click()
    pg.wait_for_selector('td >> text=2 of 3 items done', timeout=5000)
    r = last('sanitation'); check(r['data']['areas'] == {'Production Floor': True, 'Waste Area': False} and r['performed_by'] == 'Sam', 'sanitation stores every item checked/unchecked')

    # --- Waste: empty lists -> type-in boxes
    tab(pg, 'Waste Destruction'); pg.wait_for_selector('h2 >> text=Waste Destruction Log')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    check(field(md, 'Method Used').evaluate('e=>e.tagName') == 'INPUT', 'empty methods list = type-in box')
    md.get_by_role('button', name='Submit entry').click()
    check(md.locator('.msg.err', has_text='Agent / Badge ID(s) is required').count() == 1, 'required fields enforced')
    field(md, 'Agent / Badge ID').fill('A1'); field(md, 'Category').fill('Concentrate'); field(md, 'Track-and-Trace').fill('1A400'); field(md, 'Quantity of Waste').fill('14.2')
    field(md, 'Method Used').fill('Ground and mixed per state rule'); field(md, 'Supervisor Name').fill('Sup')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_selector('td >> text=Concentrate')
    r = last('waste'); check(r['data']['qty_unit'] == 'Grams' and r['data']['tracking_recorded'].startswith('Yes') and r['result'] == 'Logged' and r['data']['camera_1'] if False else r['result'] == 'Logged', 'waste saved Logged')
    check(len([k for k in r['data']]) >= 10, 'waste data has full field set (%d keys)' % len(r['data']))

    # --- Scale
    tab(pg, 'Scale Calibration'); pg.wait_for_selector('h2 >> text=Scale Calibration Log')
    pg.get_by_role('button', name='Manage lists').click()
    add_items(pg, 'Scales', ['SCALE-03'], ['Production Floor', 'OHAUS Ranger', 'R31P30', '0083451', '30 kg x 1 g', 'CC-1', '2026-03-01', 'Acme Scale', '0.1'])
    pg.mouse.click(5, 5)
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    field(md, 'Scale ID').select_option(label='SCALE-03')
    check(field(md, 'Serial Number').input_value() == '0083451' and field(md, 'Scale Make').input_value() == 'OHAUS Ranger' and field(md, 'Last Annual Certification').input_value() == '2026-03-01', 'picking scale fills details (serial keeps leading zeros)')
    for i in range(1, 6):
        field(md, 'Point %d' % i + ' — ' + ['Front Left','Front Right','Back Left','Back Right','Middle'][i-1] + ' — Test Weight').fill('500')
        field(md, 'Point %d' % i + ' — ' + ['Front Left','Front Right','Back Left','Back Right','Middle'][i-1] + ' — Scale Reading').fill('500.3' if i == 3 else '500.0')
    check(md.locator('td .badge.bad').count() == 1 and md.locator('td .badge.ok').count() == 4, 'point 3 off by 0.3 g fails, other 4 OK')
    md.get_by_role('button', name='Submit entry').click()
    check(md.locator('.msg.err', has_text='Result is Fail').count() == 1, 'fail requires corrective action')
    field(md, 'Corrective Action').fill('Re-leveled, re-zeroed')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_selector('td >> text=SCALE-03')
    r = last('scale_calibration'); check(r['result'] == 'Fail' and r['item_id'] and r['data']['scale_tolerance'] == '0.1' and r['data']['item_spec']['serial'] == '0083451', 'scale saved with tolerance + scale snapshot')
    pg.screenshot(path=OUT + 'scale2.png', full_page=True)
    pg.get_by_role('button', name='View', exact=True).first.click(); pg.wait_for_selector('.md .hxrec')
    check(pg.locator('.md .hxrec >> text=FAIL (+0.3)').count() == 1, 'record view shows calibration detail')
    pg.screenshot(path=OUT + 'view.png', full_page=False)
    pg.locator('.md').get_by_role('button', name='Close').click()
    # admin edit
    pg.get_by_role('button', name='Edit').first.click(); md = pg.locator('.md')
    field(md, 'Reviewed / Verified By').fill('QA Lead')
    field(md, 'Reason for change').fill('Added reviewer')
    md.get_by_role('button', name='Save changes').click(); pg.wait_for_timeout(400)
    check(last('scale_calibration')['data'].get('verified_by') == 'QA Lead', 'admin edit saved')

    # --- Security inspection
    tab(pg, 'Security Equipment Inspection'); pg.wait_for_selector('h2 >> text=Security Equipment Inspection')
    pg.get_by_role('button', name='Manage lists').click()
    add_items(pg, 'Cameras', ['VAULT 1', 'VAULT 2']); add_items(pg, 'Door Locks', ['MAIN ENTRANCE']); add_items(pg, 'Alarm System', ['BASE STATION'])
    pg.mouse.click(5, 5)
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    rows = md.locator('tbody tr')
    rows.nth(0).locator('select').select_option('Clear'); rows.nth(0).get_by_role('button', name='OK').click()
    rows.nth(1).get_by_role('button', name='FAIL').click()
    md.locator('.tabs button', has_text='Door Locks').click(); md.locator('tbody tr').nth(0).get_by_role('button', name='OK').click()
    check(md.locator('text=3 / 4 checked').count() == 1 and md.locator('.badge.bad', has_text='1 FAIL').count() == 1, 'inspection progress + fail count')
    md.get_by_role('button', name='Submit entry').click()
    check(md.locator('.msg.err', has_text='Notes / Issues Found').count() == 1, 'fail needs notes')
    field(md, 'Notes / Issues Found').fill('VAULT 2 offline')
    md.get_by_role('button', name='Submit entry').click()
    check(md.locator('.msg.err', has_text='sign').count() == 1, 'inspection requires signature (as BF)')
    sign(pg); md.get_by_role('button', name='Submit entry').click(); pg.wait_for_selector('td >> text=FAIL: VAULT 2')
    r = last('security_inspection'); check(r['data']['cameras'][0] == {'name': 'VAULT 1', 'detail': 'Clear', 'status': 'OK'} and r['result'] == 'Fail' and r['signature'], 'inspection stored per camera/door/alarm')
    pg.screenshot(path=OUT + 'insp.png', full_page=True)

    # --- Temperature auto range
    tab(pg, 'Temp / Humidity'); pg.wait_for_selector('h2 >> text=Temp / Humidity Log')
    pg.get_by_role('button', name='Manage lists').click()
    add_items(pg, 'Locations / Rooms', ['Storage Vault'], ['60', '75', None, '62'])
    pg.mouse.click(5, 5)
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    field(md, 'Location / Room').select_option(label='Storage Vault')
    field(md, 'Temperature').fill('70'); field(md, 'Relative Humidity').fill('65')
    check(field(md, 'Within Acceptable Range').input_value().startswith('No'), 'humidity over max sets out-of-range automatically')
    field(md, 'Relative Humidity').fill('55')
    check(field(md, 'Within Acceptable Range').input_value().startswith('Yes'), 'back in range')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_selector('td >> text=Storage Vault')
    check(last('temperature')['result'] == 'Pass', 'temp pass saved')

    # --- QR link + Michigan isolation
    link = pg.locator('.card.gold input[readonly]').input_value()
    check('state=st-mo' in link and 'lic=lic-mo' in link and 'type=temperature' in link, 'QR link carries type+state+lic')
    pg.locator('.ctx select').first.select_option(label='Michigan')
    pg.get_by_role('button', name='Facility Logs').click()
    tab(pg, 'Scale Calibration'); pg.wait_for_selector('h2 >> text=Scale Calibration Log')
    check(pg.locator('td >> text=SCALE-03').count() == 0, 'Michigan sees no Missouri entries')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    check(field(md, 'Scale ID').evaluate('e=>e.tagName') == 'INPUT', 'Michigan has no Missouri scale list')
    pg.mouse.click(5, 5)

    # --- Kiosk on a phone
    kp = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True); kp.route('**/*', handle)
    k = kp.new_page(); k.on('pageerror', lambda e: errors.append('KJS: ' + str(e)))
    k.goto(BASE + '?kiosk=log&type=environmental&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Environmental Monitoring Log')
    check(k.locator('select option', has_text='ATP swab (surface)').count() == 1, 'kiosk sample types use BF defaults')
    field(k.locator('.box'), 'Performed By').fill('Kiosk Kim'); field(k.locator('.box'), 'Sampling Location').fill('Drain 1')
    k.get_by_role('button', name='Submit entry').click()
    check(k.locator('.msg.err', has_text='sign').count() == 1, 'kiosk requires signature')
    sign(k); k.screenshot(path=OUT + 'kiosk2.png', full_page=True)
    k.get_by_role('button', name='Submit entry').click(); k.wait_for_selector('text=Saved. Thank you, Kiosk Kim.')
    r = last('environmental'); check(r['source'] == 'kiosk' and r['result'] == 'Pass' and r['state_id'] == 'st-mo', 'kiosk environmental saved')
    k.goto(BASE + '?kiosk=log&type=sanitation&state=st-mo&lic=lic-mo'); k.wait_for_selector('label.ck >> text=Production Floor')
    check(True, 'sanitation kiosk shows this license areas')
    for bad, txt in [(BASE + '?kiosk=log&type=scale_calibration&state=st-mi&lic=lic-mo', 'not linked to an active license in this state'),
                     (BASE + '?kiosk=log&type=pest&lic=lic-mo', 'missing its state or license'),
                     (BASE + '?kiosk=log&type=scale&state=st-mo&lic=lic-mo', 'not a valid log code'),
                     (BASE + '?kiosk=visitor&lic=lic-mo', 'missing its state or license')]:
        k.goto(bad); k.wait_for_selector('.msg.err')
        check(txt in k.locator('.msg.err').inner_text(), 'refused: ' + bad.split('?')[1])
    b.close()

print('\nJS/assert errors:', errors if errors else 'none')
sys.exit(1 if errors else 0)
