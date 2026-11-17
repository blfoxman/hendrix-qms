import re, os, base64
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
CAN = 'Cannabis (flower, trim, biomass)'
T['hx_suppliers'] = [{'id': 's-ok', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Heritage Missouri', 'category': 'Cannabis', 'status': 'approved', 'specs': '', 'emergency_verification': ''}]
def L(i, item, cat, tag, status='accepted', **kw):
    r = {'id': i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-%s' % i[-3:], 'item': item, 'category': cat, 'quantity': 1000, 'qty_used': 0, 'unit': 'g', 'status': status, 'metrc_tag': tag,
         'supplier_id': 's-ok', 'supplier_name': 'Heritage Missouri', 'supplier_status': 'approved', 'received_on': '2026-10-01', 'expiry_date': None, 'coa_ok': True, 'checks': {}, 'files': [], 'created_at': '2026-10-01', 'decided_by': 'Sam', 'decision_notes': ''}
    r.update(kw); return r
T['hx_lots'] = [L('lot-001', 'Gelato trim', CAN, '1A40C03000060E1000001111'), L('lot-002', 'Old flower', CAN, ''), L('lot-003', 'Glass jars', 'Packaging', '', unit='each'),
                L('lot-004', 'Distillate', 'Distillate / extract', '', status='quarantine', decided_by='')]
CALLS = []
_h = handle
def handle(route, request):
    if request.url.split('?')[0].endswith('/rpc/hx_lot_set_tag'):
        a = json.loads(request.post_data); CALLS.append(a)
        l = next(x for x in T['hx_lots'] if x['id'] == a['p_lot'])
        k = lambda t: re.sub('[^A-Z0-9]', '', (t or '').upper())
        o = next((x for x in T['hx_lots'] if x['id'] != l['id'] and k(x['metrc_tag']) == k(a['p_tag'])), None)
        if o: return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'METRC tag %s is already on lot %s.' % (a['p_tag'], o['number'])}))
        l['metrc_tag'] = a['p_tag']; return route.fulfill(status=200, content_type='application/json', body=json.dumps(a['p_tag']))
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    return md.locator('label.f, div.f', has=md.page.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1440, 'height': 1000}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Receiving', exact=True).click(); pg.wait_for_selector('tr >> text=RCV-2026-001')
    check(pg.locator('tr', has_text='RCV-2026-001').locator('text=1A40C03000060E1000001111').count() == 1, 'Receiving list shows the METRC tag under the lot')
    check(pg.locator('tr', has_text='RCV-2026-002').locator('.badge', has_text='No METRC tag').count() == 1, 'Receiving list flags a cannabis lot with no tag')
    check(pg.locator('tr', has_text='RCV-2026-003').locator('.badge', has_text='No METRC tag').count() == 0, 'packaging lot is not flagged')
    pg.locator('.tabs button', has_text='Inventory').click(); pg.wait_for_selector('td >> text=Gelato trim')
    hdr = pg.locator('thead tr').first.inner_text()
    check('METRC TAG' in hdr.upper(), 'Inventory has a METRC tag column')
    check(pg.locator('tr', has_text='Gelato trim').locator('td', has_text='1A40C03000060E1000001111').count() == 1, 'Inventory shows the tag on each lot')
    check(re.search(r'Cannabis lots without a METRC tag', pg.content()) is not None, 'stat: cannabis lots without a METRC tag')
    pg.locator('input[placeholder="Search item, lot, supplier, METRC tag"]').fill('1111')
    check(pg.locator('tbody tr', has_text='Gelato trim').count() == 1 and pg.locator('tbody tr', has_text='Glass jars').count() == 0, 'search by the last digits of the METRC tag')
    pg.locator('input[placeholder="Search item, lot, supplier, METRC tag"]').fill('')
    sel = pg.locator('select', has=pg.locator('option', has_text='Cannabis (METRC)'))
    sel.select_option('canna')
    check(pg.locator('tbody tr', has_text='Glass jars').count() == 0 and pg.locator('tbody tr', has_text='Gelato trim').count() == 1, 'filter: cannabis only')
    sel.select_option('notag')
    check(pg.locator('tbody tr', has_text='Old flower').count() == 1 and pg.locator('tbody tr', has_text='Gelato trim').count() == 0, 'filter: cannabis without a tag')
    sel.select_option('all')
    # add the missing tag from the Inventory row
    pg.locator('tr', has_text='Old flower').get_by_role('button', name='+ Add tag').click()
    md = pg.locator('.md', has=pg.locator('h2', has_text='Add METRC tag'))
    field(md, 'METRC package tag').fill('1A40C03000060E1000001111'); md.get_by_role('button', name='Save tag').click(); md.locator('.msg.err').wait_for()
    check(md.locator('.msg.err', has_text='already on lot RCV-2026-001').count() == 1, 'duplicate tag refused with the other lot')
    field(md, 'METRC package tag').fill('1A40C03000060E1000002222'); md.get_by_role('button', name='Save tag').click(); md.wait_for(state='detached')
    check(pg.locator('.msg', has_text='Added the METRC tag on RCV-2026-002').count() == 1 and T['hx_lots'][1]['metrc_tag'] == '1A40C03000060E1000002222', 'tag added to a lot already in stock')
    pg.wait_for_selector('td >> text=1A40C03000060E1000002222')
    check(pg.locator('tr', has_text='Old flower').locator('td', has_text='1A40C03000060E1000002222').count() == 1, 'Inventory shows the new tag')
    # change an existing tag from the lot detail: needs a reason
    pg.locator('tr', has_text='Gelato trim').get_by_role('button', name='Open').click()
    pg.get_by_role('button', name='Change METRC tag').click()
    md = pg.locator('.md', has=pg.locator('h2', has_text='Change METRC tag'))
    field(md, 'METRC package tag').fill('1A40C03000060E1000003333'); md.get_by_role('button', name='Save tag').click()
    check(md.locator('.msg.err', has_text='Give the reason').count() == 1, 'changing a tag needs a reason')
    field(md, 'Reason for the change').fill('typo at receiving'); md.get_by_role('button', name='Save tag').click(); md.wait_for(state='detached')
    check(CALLS[-1] == {'p_lot': 'lot-001', 'p_tag': '1A40C03000060E1000003333', 'p_reason': 'typo at receiving'}, 'tag change sent with the reason')
    pg.keyboard.press('Escape'); pg.locator('.md').get_by_role('button', name='Close').click() if pg.locator('.md').count() else None
    # receiving a cannabis lot needs a tag
    pg.locator('.tabs button', has_text='Receiving').click()
    pg.get_by_role('button', name='+ Receive lot').click()
    md = pg.locator('.md', has_text='Receive a lot')
    field(md, 'Supplier').select_option('s-ok'); field(md, 'Item received').fill('Runtz flower'); field(md, 'Category').select_option(CAN); field(md, 'Quantity').fill('500')
    check(md.locator('span', has_text='METRC tag *').count() == 1, 'METRC tag is marked required for cannabis')
    md.get_by_role('button', name=re.compile('Receive into')).click()
    check(md.locator('.msg.err', has_text='Every cannabis lot needs one').count() == 1, 'cannabis lot cannot be received without a tag')
    field(md, 'Category').select_option('Packaging')
    check(md.locator('span', has_text='METRC tag (cannabis)').count() == 1, 'tag optional for packaging')
    md.get_by_role('button', name='Cancel').click()
    # accepting an untagged cannabis lot is blocked
    pg.locator('tr', has_text='RCV-2026-004').click()
    pg.get_by_role('button', name='Accept', exact=True).click()
    md = pg.locator('.md', has_text='Accept RCV-2026-004')
    check(md.locator('.msg.err', has_text='has no METRC tag').count() == 1, 'accept warns: cannabis lot has no METRC tag')
    md.get_by_role('button', name=re.compile('^Accept')).last.click()
    check(md.locator('.msg.err', has_text='Add the METRC package tag first').count() == 1 and T['hx_lots'][3]['status'] == 'quarantine', 'untagged cannabis lot is not accepted')
    b.close()
check(not [e for e in errors if e.startswith('JS')], 'no JS errors')
print('errors:', errors)
