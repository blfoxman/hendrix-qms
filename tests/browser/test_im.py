import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_equipment'] = [{'id': 'q1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'EQ-001', 'name': 'Bench scale', 'category': 'Scale / balance', 'status': 'in_service'}]
T['hx_skus'] += [{'id': 'k-c', 'state_id': 'st-mo', 'product_type': 'cartridges', 'name': '2G AIO', 'spec': {}, 'license_ids': [], 'active': True, 'sort': 0}]
T['hx_flavors'] += [{'id': 'fx', 'state_id': 'st-mo', 'sku_id': 'k-c', 'name': 'Blue Dream', 'active': True, 'sort': 0}]
T['hx_org_positions'] = []; AIQ = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AIQ.append(b)
        out = {'mapping': {'name': 'Equipment', 'category': 'Type', 'location': 'Room', 'make': 'Manufacturer', 'model': 'Model #', 'serial': 'Serial No', 'cal_required': 'Calibrate?', 'cal_interval_months': 'Cal Freq (months)', 'installed_on': 'Installed', 'notes': 'Notes'},
               'values': {'category': {'Mixer': 'Production', 'Scale': 'Scale / balance'}}}
        return jr(route, {'content': [{'type': 'text', 'text': json.dumps(out)}]})
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def sel(pg, label): return pg.locator('select[aria-label="' + label + '"]')
def prow(pg, n): return pg.locator('tr', has=pg.locator('td', has_text=re.compile('^' + str(n) + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('text=Coming next').count() == 0, 'nothing left on the coming-next list')
    pg.get_by_role('button', name='Import (Excel / Sheets)').click(); pg.wait_for_selector('text=1. What are you importing?')
    check(pg.locator('button.card').count() == 7, 'seven kinds of lists can be imported')
    pg.locator('button.card', has_text='Equipment').click(); pg.locator('input[type=file]').set_input_files(OUT + 'import_eq.xlsx'); pg.wait_for_selector('text=import_eq.xlsx')
    check(pg.locator('input[type=number]').first.input_value() == '2' and pg.locator('select', has=pg.locator('option', has_text='Suppliers')).count() == 1, 'title row skipped: header found on row 2; sheet picker')
    opt = lambda f: sel(pg, f).evaluate('s=>s.options[s.selectedIndex].text')
    check(opt('Equipment name') == 'Equipment' and opt('Location') == 'Room' and opt('Make') == 'Manufacturer' and opt('Serial number') == 'Serial No' and opt('Calibrate every (months)') == 'Cal Freq (months)' and opt('Installed on') == 'Installed', 'columns matched without AI')
    check(pg.locator('.badge', has_text='2 to import').count() == 1 and pg.locator('.badge', has_text='1 with problems').count() == 1 and pg.locator('.badge', has_text='1 already in Hendrix').count() == 1, 'preview: 2 to import, 1 missing name, 1 duplicate')
    check(prow(pg, 6).locator('text=Equipment name is missing').count() == 1 and prow(pg, 3).locator('text=Already in Hendrix').count() == 1, 'row problems explained')
    pg.get_by_role('button', name='Match with AI').click(); pg.wait_for_selector('text=Columns matched by the AI')
    check(AIQ[0]['module'] == 'import' and AIQ[0]['target'] == 'equipment' and 'Mixer' in AIQ[0]['messages'][0]['content'], 'AI asked with the columns, sample rows and values (target module checked)')
    check(prow(pg, 4).locator('td', has_text='Production').count() == 1 and prow(pg, 5).locator('text=2025-03-10').count() == 1, 'AI maps "Mixer" to Production; US dates read')
    pg.get_by_role('button', name='Import 2 rows').click(); pg.wait_for_selector('text=Imported 2.')
    new = [e for e in T['hx_equipment'] if e['id'] != 'q1']
    f3 = next(e for e in new if e['name'] == 'Filler #3'); ab = next(e for e in new if e['name'] == 'Analytical balance')
    check(len(new) == 2 and f3['category'] == 'Production' and f3['installed_on'] == '2025-06-15' and f3['cal_required'] is False and ab['cal_required'] is True and ab['cal_interval_months'] == 6 and ab['category'] == 'Scale / balance' and ab['license_id'] == 'lic-mo', 'equipment saved with the right fields')
    pg.wait_for_selector('.badge >> text=3 already in Hendrix'); check(pg.locator('.badge', has_text='0 to import').count() == 1, 'after the import the same rows show as already in Hendrix (no double import)')
    pg.screenshot(path=OUT + 'import.png', full_page=True)
    # products from pasted Google Sheets cells
    pg.locator('button.card', has_text='Products (SKUs and flavors)').click()
    pg.locator('textarea').fill('Product line\tSKU\tFlavor\nCartridges\t2G AIO\tBlue Dream\nCartridges\t2G AIO\tMango\nGummies\tGummies 10pk\tWatermelon\nGummies\tGummies 10pk\tGrape')
    pg.get_by_role('button', name='Use pasted cells').click(); pg.wait_for_selector('text=Pasted cells')
    pg.get_by_role('button', name='Import 4 rows').click(); pg.wait_for_selector('text=Imported 4.')
    gm = next(k for k in T['hx_skus'] if k['name'] == 'Gummies 10pk')
    fl = lambda sid: sorted(f['name'] for f in T['hx_flavors'] if f['sku_id'] == sid)
    check(gm['product_type'] == 'gummies' and gm['active'] is False and fl(gm['id']) == ['Grape', 'Watermelon'] and fl('k-c') == ['Blue Dream', 'Mango'] and len([k for k in T['hx_skus'] if k['name'] == '2G AIO']) == 1, 'products: new SKU switched off, flavors added, existing SKU gets only the new flavor')
    # org chart from CSV with reporting lines
    pg.locator('button.card', has_text='Org chart').click(); pg.locator('input[type=file]').set_input_files(OUT + 'import_org.csv'); pg.wait_for_selector('text=import_org.csv')
    pg.get_by_role('button', name='Import 4 rows').click(); pg.wait_for_selector('text=Imported 4')
    P = {p['title']: p for p in T['hx_org_positions']}
    check(P['Quality Manager']['reports_to'] == P['General Manager']['id'] and P['QA Tech']['reports_to'] == P['Quality Manager']['id'] and P['QA Tech'].get('person_name', '') == '', 'org chart reporting lines linked by position title')
    check(pg.locator('text=Reports to "Plant Manager" not found').count() == 1, 'unknown manager reported, not guessed')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
