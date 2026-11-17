import re, os, zipfile, base64
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_suppliers'] = [{'id': 's-ok', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Greenway Packaging', 'category': 'Packaging', 'status': 'approved', 'specs': '', 'emergency_verification': ''},
                     {'id': 's-cul', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Heritage Missouri', 'category': 'Cannabis', 'status': 'conditional', 'specs': '', 'emergency_verification': ''},
                     {'id': 's-p', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'name': 'Pending Co', 'category': '', 'status': 'pending', 'specs': '', 'emergency_verification': ''}]
T['hx_lots'] = [{'id': 'lot-j', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-002', 'item': 'Glass jars', 'category': 'Packaging', 'quantity': 1200, 'qty_used': 200, 'unit': 'each', 'status': 'accepted',
                 'metrc_tag': '', 'supplier_id': 's-ok', 'supplier_name': 'Greenway Packaging', 'received_on': '2026-10-01', 'expiry_date': None, 'location': 'Rack 1', 'coa_ok': True, 'created_at': '2026-10-01'},
                {'id': 'lot-f', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-003', 'item': 'FLOWER', 'category': 'Bud/Flower', 'quantity': 5808, 'qty_used': 0, 'unit': 'g', 'status': 'accepted',
                 'metrc_tag': '', 'supplier_id': 's-ok', 'supplier_name': 'Greenway Packaging', 'received_on': '2026-10-01', 'expiry_date': None, 'location': 'Vault', 'coa_ok': True, 'created_at': '2026-10-01'},
                {'id': 'lot-k', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-004', 'item': 'KIEF', 'category': 'Kief', 'quantity': 82, 'qty_used': 0, 'unit': 'g', 'status': 'accepted',
                 'metrc_tag': '1A40C03000060E1000001450', 'supplier_id': 's-ok', 'supplier_name': 'Greenway Packaging', 'received_on': '2026-10-01', 'expiry_date': None, 'location': 'Vault', 'coa_ok': True, 'created_at': '2026-10-01'},
                {'id': 'lot-x', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-001', 'item': 'Old biomass', 'category': 'Other', 'quantity': 10, 'qty_used': 0, 'unit': 'kg', 'status': 'accepted',
                 'metrc_tag': '1A40C03000060E1000009999', 'supplier_id': 's-ok', 'supplier_name': 'Greenway Packaging', 'received_on': '2026-10-01', 'expiry_date': None, 'created_at': '2026-10-01'}]
CALLS = []; UPD = []
_h = handle
def handle(route, request):
    if request.url.split('?')[0].endswith('/rpc/hx_inventory_upload'):
        a = json.loads(request.post_data); UPD.append(a)
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'added': 1, 'first': 'RCV-2026-009', 'last': 'RCV-2026-009', 'counted': 2, 'moved': 1, 'tagged': 1, 'unchanged': 1}))
    if request.url.split('?')[0].endswith('/rpc/hx_lots_import'):
        a = json.loads(request.post_data); CALLS.append(a); n = len(a['p_rows'])
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'count': n, 'first': 'RCV-2026-002', 'last': 'RCV-2026-%03d' % (n + 1)}))
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def make_xlsx(pg, rows, name):
    # fill the template in the browser with SheetJS, as a person would in Excel
    b64 = pg.evaluate('''(rows)=>{const X=window.XLSX,wb=X.utils.book_new();X.utils.book_append_sheet(wb,X.utils.aoa_to_sheet([['How to fill'],['ignore me']]),'How to fill');
      X.utils.book_append_sheet(wb,X.utils.aoa_to_sheet(rows),'Inventory');return X.write(wb,{type:'base64',bookType:'xlsx'});}''', rows)
    p = OUT + name; open(p, 'wb').write(base64.b64decode(b64)); return p
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Receiving', exact=True).click(); pg.locator('.tabs button', has_text='Inventory').click()
    pg.wait_for_selector('button >> text=Upload inventory')
    # template
    with pg.expect_download() as d: pg.get_by_role('button', name='Download template').click()
    tp = d.value.path(); check(d.value.suggested_filename == 'Hendrix inventory template - MAN000109.xlsx', 'template named for the license')
    z = zipfile.ZipFile(tp); wbx = z.read('xl/workbook.xml').decode(); ss = z.read('xl/sharedStrings.xml').decode() if 'xl/sharedStrings.xml' in z.namelist() else ''.join(z.read(n).decode() for n in z.namelist() if n.startswith('xl/worksheets/'))
    sheets = re.findall(r'<sheet [^>]*name="([^"]+)"', wbx)
    check(sheets == ['Inventory', 'How to fill', 'Suppliers', 'Lists'], 'template sheets: Inventory, How to fill, Suppliers, Lists')
    check(all(h in ss for h in ('Item *', 'Quantity on hand *', 'Unit *', 'Supplier *', 'METRC Tag', 'COA on file (Yes/No) *', 'Status (Accepted/Quarantine)', 'Expiry Date')), 'template has the columns to fill')
    check('Greenway Packaging' in ss and 'Heritage Missouri' in ss and 'Pending Co' not in ss, 'Suppliers sheet lists only approved / conditional suppliers')
    check('Cannabis (flower, trim, biomass)' in ss and 'Quarantine' in ss, 'Lists sheet: categories, units, status')
    H = ['Item *', 'Category', 'Quantity on hand *', 'Unit *', 'Supplier *', 'METRC Tag', 'Supplier Lot #', 'Received Date', 'Expiry Date', 'Storage Location', 'PO Number', 'COA on file (Yes/No) *', 'Status (Accepted/Quarantine)', 'Notes']
    # a file with problems
    bad = make_xlsx(pg, [H,
        ['Glass jars', 'Packaging', 1200, 'ea', 'Greenway Packaging', '', '', '2026-11-01', '', 'Rack 3', '', 'Yes', '', ''],
        ['Lids', 'Packaging', 0, 'each', 'Greenway Packaging', '', '', '', '', '', '', 'Yes', '', ''],
        ['Boxes', 'Packaging', 50, 'box', 'Nobody Inc', '', '', '', '', '', '', 'Yes', '', ''],
        ['Biomass', 'Cannabis', 2.5, 'kg', 'Heritage Missouri', '1A40C03000060E1000001111', '', '', '', '', '', 'No', 'Accepted', ''],
        ['Biomass B', 'Cannabis', 2.5, 'kg', 'Heritage Missouri', '1A40 C030 0006 0E10 0000 1111', '', '', '', '', '', 'Yes', 'Quarantine', ''],
        ['Old tag', 'Cannabis', 1, 'kg', 'Heritage Missouri', '1A40C03000060E1000009999', '', '', '', '', '', 'Yes', '', ''],
        ['Pending stuff', '', 1, 'each', 'Pending Co', '', '', '', '', '', '', 'Yes', '', ''],
        ['Future', '', 1, 'each', 'Greenway Packaging', '', '', '2099-01-01', '', '', '', 'Yes', '', '']], 'inv_bad.xlsx')
    pg.get_by_role('button', name='Upload inventory').click(); md = pg.locator('.md')
    md.locator('input[aria-label="Inventory file"]').set_input_files(bad); md.locator('.msg').first.wait_for()
    txt = md.inner_text()
    check('7 of 8 rows need fixing' in txt, 'preview counts the rows to fix')
    check('Quantity must be a number above 0' in txt and 'Supplier "Nobody Inc" is not on file' in txt and 'Accepted needs COA on file = Yes' in txt, 'quantity, unknown supplier, COA rules shown per row')
    check('METRC Tag is in the file more than once' in txt and 'METRC Tag is already on lot RCV-2026-001' in txt, 'duplicate tags in the file and already in Hendrix shown')
    check('Pending Co is not approved' in txt and 'Received Date is in the future' in txt, 'unapproved supplier and future date shown')
    check(md.locator('tr', has_text='Glass jars').locator('td', has_text='1200 each').count() == 1, 'unit "ea" read as each')
    check(md.get_by_role('button', name=re.compile('^(Add|Save)')).is_disabled(), 'nothing can be added while rows need fixing')
    md.screenshot(path=OUT + 'inventory_upload_check.png')
    md.get_by_role('checkbox').check(); check(md.locator('tbody tr').count() == 7, 'show only rows to fix')
    check(len(CALLS) == 0, 'nothing sent to the database')
    # the fixed file
    good = make_xlsx(pg, [H,
        ['Glass jars 3.5 g', 'packaging', 1200, 'ea', 'greenway packaging', '', 'L24-0915', 46327, '2027-11-01', 'Rack 3', 'PO-1043', 'Yes', '', 'Counted'],
        ['Biomass', 'Cannabis', 2.5, 'kg', 'Heritage Missouri', '1A40C03000060E1000001111', '', '11/02/2026', '', 'Vault', '', 'No', 'Quarantine', ''],
        [], ['Cones 98 mm', 'Cones', 5000, 'each', 'Greenway Packaging', '', '', '', '', '', '', 'y', 'accepted', '']], 'inventory_nov16.xlsx')
    md.locator('input[aria-label="Inventory file"]').set_input_files(good); pg.wait_for_selector('.md .msg >> text=3 new lots')
    check('3 new lots (2 Accepted, 1 Quarantine)' in md.inner_text(), 'preview: accepted and quarantine counts')
    md.get_by_role('button', name='Add 3 lots').click(); pg.wait_for_selector('.msg >> text=Uploaded 3 lots from inventory_nov16.xlsx')
    a = CALLS[0]; R = a['p_rows']
    check(a['p_lic'] == 'lic-mo' and a['p_file'] == 'inventory_nov16.xlsx' and len(R) == 3, 'all rows sent in one call with the file name')
    check(R[0]['item'] == 'Glass jars 3.5 g' and R[0]['category'] == 'Packaging' and R[0]['unit'] == 'each' and R[0]['supplier'] == 'Greenway Packaging' and R[0]['quantity'] == 1200, 'names matched to Hendrix lists (category, unit, supplier)')
    check(R[0]['received_on'] == '2026-11-01' and R[0]['expiry_date'] == '2027-11-01' and R[0]['coa_ok'] is True and R[0]['status'] == 'accepted' and R[0]['po_number'] == 'PO-1043' and R[0]['supplier_lot'] == 'L24-0915', 'Excel dates, COA, status, PO and supplier lot read')
    check(R[1]['status'] == 'quarantine' and R[1]['received_on'] == '2026-11-02' and R[1]['metrc_tag'] == '1A40C03000060E1000001111' and R[1]['category'] == 'Cannabis (flower, trim, biomass)', 'quarantine row, US date and METRC tag')
    check(R[2]['item'] == 'Cones 98 mm' and R[2]['category'] == 'Cones / pre-roll supplies' and R[2]['coa_ok'] is True, 'empty rows skipped; "y" means Yes')
    pg.screenshot(path=OUT + 'inventory_upload.png')
    # update: download current inventory, change counts, upload
    pg.wait_for_timeout(300)
    with pg.expect_download() as d: pg.get_by_role('button', name='Download current inventory').click()
    check(re.match(r'Hendrix inventory - MAN000109 - \d{4}-\d{2}-\d{2}\.xlsx$', d.value.suggested_filename) is not None, 'current inventory file named for the license and date: ' + d.value.suggested_filename)
    rows = pg.evaluate('''async(b64)=>{const X=window.XLSX,wb=X.read(b64,{type:'base64'});return X.utils.sheet_to_json(wb.Sheets.Inventory,{header:1,raw:true,defval:''});}''', base64.b64encode(open(d.value.path(), 'rb').read()).decode())
    hd = rows[0]
    check(hd[0] == 'Hendrix Lot # (keep it to update)' and hd[3] == 'Quantity on hand *', 'Lot # first, then the template columns')
    byl = {r[0]: r for r in rows[1:]}
    check(byl.get('RCV-2026-002', [None] * 4)[3] == 1000 and byl['RCV-2026-003'][3] == 5808 and byl['RCV-2026-004'][6] == '1A40C03000060E1000001450', 'every lot in stock with what is left now and its METRC tag')
    check(len(rows) - 1 == 4, 'only lots in stock (4): ' + str(len(rows) - 1))
    up = [hd]
    for r in rows[1:]:
        r = list(r)
        if r[0] == 'RCV-2026-002': r[3] = 950; r[10] = 'Rack 2'
        if r[0] == 'RCV-2026-003': r[3] = 5790; r[6] = '1A40C03000060E1000003258'
        up.append(r)
    up.append(['', 'Lids', 'Packaging', 300, 'each', 'Greenway Packaging', '', '', '', '', '', '', 'Yes', '', ''])
    p = make_xlsx(pg, up, 'count_nov16.xlsx')
    pg.get_by_role('button', name='Upload inventory').click(); md = pg.locator('.md')
    md.locator('input[aria-label="Inventory file"]').set_input_files(p); pg.wait_for_selector('.md .msg >> text=/lots updated|need fixing/')
    t = md.inner_text()
    check('1 new lot (1 Accepted, 0 Quarantine), 2 lots updated' in t and '2 lots unchanged' in t, 'preview: new lot, updated lots, unchanged lots: ' + t[t.find('new lot')-10:t.find('new lot')+90])
    check('On hand 1000 → 950 each' in t and 'Location → Rack 2' in t and 'On hand 5808 → 5790 g' in t and 'METRC tag added' in t, 'preview shows each change')
    md.get_by_role('button', name='Save 3 changes').click(); pg.wait_for_selector('.msg >> text=Saved from count_nov16.xlsx')
    a = UPD[0]; R = {x.get('lot_number', 'new'): x for x in a['p_rows']}
    check(len(a['p_rows']) == 3 and R['RCV-2026-002']['quantity'] == 950 and R['RCV-2026-002']['location'] == 'Rack 2' and R['RCV-2026-003']['metrc_tag'] == '1A40C03000060E1000003258' and R['new']['item'] == 'Lids', 'only changed lots and the new lot sent, in one call')
    check('2 counts recorded' in pg.locator('.msg', has_text='Saved from').inner_text(), 'result message')
    # a changed METRC tag is refused in the preview
    bad2 = [hd] + [[x if i != 6 else ('1A40C03000060E1000009999' if r[0] == 'RCV-2026-004' else x) for i, x in enumerate(r)] for r in rows[1:]]
    p2 = make_xlsx(pg, bad2, 'count_bad.xlsx')
    pg.get_by_role('button', name='Upload inventory').click(); md = pg.locator('.md')
    md.locator('input[aria-label="Inventory file"]').set_input_files(p2); pg.wait_for_selector('.md .msg >> text=/need fixing|lots updated|Nothing to change/')
    check('METRC Tag differs from Hendrix (1A40C03000060E1000001450)' in md.inner_text(), 'a different METRC tag on a lot is refused in the preview')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
