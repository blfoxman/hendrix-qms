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
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f', has=pgx.locator('span', has_text=label)).locator('input,select,textarea').first
def sku(name): return next(k for k in T['hx_skus'] if k['name'] == name)

with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.get_by_role('button', name='Products', exact=True).click()
    pg.wait_for_selector('text=No Ethanol Extraction SKUs in Missouri yet')
    check(pg.locator('.tabs button').count() == 3 + 8, 'admin tabs + 8 Black Fox product types')
    # price library first
    pg.locator('.tabs button', has_text='Ingredient Prices').click()
    field(pg, 'Name').fill('Distillate'); field(pg, 'Unit').fill('g'); field(pg, 'Cost / unit').fill('1.85')
    pg.get_by_role('button', name='+ Add price').click(); pg.wait_for_selector('td >> text=Distillate')
    check(T['hx_cost_library'][0]['cost_per_unit'] == 1.85 and T['hx_cost_library'][0]['state_id'] == 'st-mo', 'price saved for Missouri')
    pg.locator('.tabs button', has_text='SKUs and Flavors').click()
    pg.locator('.tabs button', has_text='Cartridges').click()
    # wizard
    pg.get_by_role('button', name='+ New SKU').click(); md = pg.locator('.md')
    check(field(md, 'Product type').input_value() == 'cartridges', 'wizard opens on current product type')
    field(md, 'SKU name').fill('Muha Meds 2G AIO'); field(md, 'Oil per cartridge').fill('2')
    field(md, 'Flavors - one per line').fill('Honey Melon\nBlue Dream\nhoney melon\n\nStrawberry Lava')
    check(md.locator('text=3 flavors').count() == 1, 'flavor list de-duplicated (3)')
    md.get_by_role('button', name='Next: formulation').click()
    md.get_by_role('button', name='Save SKU and formulation').click()
    check(md.locator('.msg.err', has_text='Add at least one raw material').count() == 1, 'formulation required to save SKU')
    md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).first.select_option(label='Distillate ($1.85/g)')
    md.locator('.li input').nth(1).fill('900')
    md.get_by_role('button', name='+ Add Item').click()
    li = md.locator('.li').nth(1); li.locator('input').nth(0).fill('2G AIO hardware'); li.locator('input').nth(1).fill('1000'); li.locator('input').nth(3).fill('0.90')
    field(md, 'Standard batch size').fill('1000')
    check(md.locator('text=$2565.00').count() >= 1 and md.locator('text=$2.57').count() == 1, 'batch total $2565 and per unit $2.57')
    md.get_by_role('button', name='Save SKU and formulation').click()
    pg.wait_for_selector('.card >> text=Muha Meds 2G AIO')
    k = sku('Muha Meds 2G AIO')
    check(k['active'] and k['spec'] == {'oil_per_unit': 2} and len([f for f in T['hx_flavors'] if f['sku_id'] == k['id']]) == 3, 'SKU active with spec + 3 flavors')
    fm = T['hx_formulations'][0]; check(fm['flavor_id'] is None and fm['name'] == 'Muha Meds 2G AIO — base recipe' and fm['raw_materials'][0]['cost_per_unit'] == '1.85', 'base formulation saved, auto-named, library price pulled')
    check(pg.locator('.badge.ok', has_text='Active').count() == 1, 'card shows Active')
    # duplicate name
    pg.get_by_role('button', name='+ New SKU').click(); md = pg.locator('.md')
    field(md, 'SKU name').fill('muha meds 2g aio'); md.get_by_role('button', name='Next: formulation').click()
    check(md.locator('.msg.err', has_text='already exists').count() == 1, 'duplicate SKU name refused')
    md.get_by_role('button', name='Cancel').click()
    # flavors manager
    pg.get_by_role('button', name='Flavors', exact=True).first.click(); md = pg.locator('.md')
    check(md.locator('text=Uses base recipe').count() == 3, 'flavors use base recipe')
    field(md, 'Add flavors').fill('Blue Dream\nGelato #33')
    md.get_by_role('button', name='+ Add flavors').click(); pg.wait_for_selector('.md td >> text=Gelato #33')
    check(len([f for f in T['hx_flavors'] if f['sku_id'] == k['id']]) == 4, 'only new flavor added')
    md.locator('tr', has_text='Blue Dream').get_by_role('button', name='Own recipe').click()
    md = pg.locator('.md')
    check(field(md, 'Flavor').is_disabled() and 'Blue Dream' in field(md, 'Flavor').locator('option:checked').inner_text(), 'flavor recipe locked to Blue Dream')
    md.get_by_role('button', name='+ Add Material').click(); md.locator('.li').first.locator('input').nth(0).fill('Terpene - Blue Dream'); md.locator('.li').first.locator('input').nth(1).fill('90')
    md.get_by_role('button', name='Save formulation').click()
    pg.wait_for_selector('.md >> text=Own recipe')
    check(any(f.get('flavor_id') for f in T['hx_formulations']), 'flavor formulation saved')
    pg.mouse.click(5, 5)
    # formulation bank, delete both -> SKU off
    pg.locator('.tabs button', has_text='Formulation Bank').click(); pg.wait_for_selector('text=2 formulations')
    pg.screenshot(path=OUT + 'bank.png', full_page=True)
    pg.get_by_role('button', name='✕').first.click(); pg.wait_for_selector('text=1 formulation')
    check(sku('Muha Meds 2G AIO')['active'], 'SKU stays on while a formulation remains')
    pg.get_by_role('button', name='✕').first.click(); pg.wait_for_selector('text=Create a SKU first', state='detached'); pg.wait_for_timeout(300)
    check(not sku('Muha Meds 2G AIO')['active'], 'deleting last formulation switches SKU off')
    pg.locator('.tabs button', has_text='SKUs and Flavors').click(); pg.locator('.tabs button', has_text='Cartridges').click()
    check(pg.locator('.badge.bad', has_text='Needs formulation').count() == 1 and pg.locator('.msg.err', has_text='1 SKU needs a formulation').count() == 1, 'needs-formulation warning')
    pg.get_by_role('button', name='Switch on').click(); pg.wait_for_selector('.msg.err >> text=Enter a formulation', timeout=4000)
    check(pg.locator('.msg.err', has_text='Enter a formulation for this SKU').count() == 1, 'cannot switch on without formulation')
    # pre-roll, no flavors, ingredients
    pg.locator('.tabs button', has_text='Pre-Rolls').click()
    pg.get_by_role('button', name='+ New SKU').click(); md = pg.locator('.md')
    field(md, 'SKU name').fill('Muha Meds 1G Plain Pre Roll'); field(md, 'Grams per joint, filled').fill('1.0'); field(md, 'Joints per package').fill('1')
    md.locator('label.ck', has_text='This SKU has flavors').locator('input').uncheck()
    md.get_by_role('button', name='Next: formulation').click()
    md.get_by_role('button', name='+ Add Material').click(); md.locator('.li input').nth(0).fill('Flower'); md.locator('.li input').nth(1).fill('1000')
    md.get_by_role('button', name='Save SKU and formulation').click(); pg.wait_for_selector('.card >> text=No flavors (plain SKU)')
    check(sku('Muha Meds 1G Plain Pre Roll')['spec'] == {'grams_filled': 1.0, 'units_per_package': 1, 'no_flavor': True}, 'pre-roll production settings saved')
    pg.screenshot(path=OUT + 'products.png', full_page=True)
    # Michigan isolation
    pg.locator('.ctx select').first.select_option(label='Michigan'); pg.wait_for_selector('h1 >> text=Michigan')
    pg.locator('.tabs button', has_text='Pre-Rolls').click()
    check(pg.locator('text=No Pre-Rolls SKUs in Michigan yet').count() == 1, 'Michigan has its own empty catalog')
    # member view
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'products': 'read'}
    pg.reload(); pg.get_by_role('button', name='Products', exact=True).click()
    pg.locator('.ctx select').first.select_option(label='Missouri'); pg.locator('.tabs button', has_text='Pre-Rolls').click()
    pg.wait_for_selector('.card >> text=Muha Meds 1G Plain Pre Roll')
    check(pg.locator('text=Formulation Bank').count() == 0 and pg.get_by_role('button', name='+ New SKU').count() == 0 and pg.get_by_role('button', name='Base recipe').count() == 0, 'member sees SKUs only, no recipes/edits')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
sys.exit(1 if errors else 0)
