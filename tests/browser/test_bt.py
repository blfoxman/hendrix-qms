import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today()
def ds(n): return (TODAY - dt.timedelta(days=n)).isoformat()
T['hx_licenses'] += [{'id': 'lic-c60', 'state_id': 'st-mo', 'name': 'Heritage Cul 60', 'license_number': 'CUL000060', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'},
                     {'id': 'lic-c22', 'state_id': 'st-mo', 'name': 'Heritage Cul 22', 'license_number': 'CUL000022', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'}]
T['hx_grow_areas'] = [{'id': 'ga-h2', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': 'H2 T3', 'kind': 'indoor', 'active': True, 'sort': 0},
                      {'id': 'ga-dry', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': 'Drying room', 'kind': 'dry', 'active': True, 'sort': 1}]
T['hx_lots'] = [{'id': 'lt-s1', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'number': 'RCV-1', 'item': 'Gelato seeds', 'category': 'Clones / seeds', 'status': 'accepted', 'quantity': 500, 'qty_used': 0, 'unit': 'each', 'received_on': ds(90), 'supplier_id': 's1'},
                {'id': 'lt-s2', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'number': 'RCV-2', 'item': 'Runtz feminized seeds', 'category': 'Clones / seeds', 'status': 'accepted', 'quantity': 60, 'qty_used': 0, 'unit': 'each', 'received_on': ds(90), 'supplier_id': 's1'},
                {'id': 'lt-cl', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'number': 'RCV-3', 'item': 'Gelato clones', 'category': 'Clones / seeds', 'status': 'accepted', 'quantity': 100, 'qty_used': 0, 'unit': 'each', 'received_on': ds(90), 'supplier_id': 's1'}]
def B(i, cult, lic, planted, stage, area='ga-h2', plants=40, **kw):
    r = {'id': 'pb-' + i, 'state_id': 'st-mo', 'license_id': lic, 'number': 'PB-' + i, 'cultivar': cult, 'source_kind': 'seed_own', 'source_lot_id': None, 'planted_on': ds(planted), 'plant_count': plants,
         'area_id': area, 'stage': stage, 'harvest_after': None, 'harvest_start': None, 'wet_weight': None, 'dry_weight': None, 'harvest_tag': '', 'metrc_tag': '', 'created_at': ds(planted)}
    r.update(kw); return r
T['hx_plant_batches'] = [
    B('veg-ok', 'Zkittlez', 'lic-c60', 10, 'vegetative', source_lot_id='lt-s1', plants=50),
    B('veg-late', 'Runtz', 'lic-c60', 30, 'vegetative'),
    B('flower', 'Gelato', 'lic-c60', 50, 'flowering'),
    B('harv', 'Sour Diesel', 'lic-c60', 82, 'flowering'),
    B('harv-late', 'Blue Dream', 'lic-c60', 90, 'flowering'),
    B('dry-late', 'OG Kush', 'lic-c60', 100, 'drying', area='ga-dry', wet_weight=12000),
    B('cure', 'Wedding Cake', 'lic-c60', 105, 'curing', area='ga-dry', wet_weight=9000),
    B('trim', 'Mimosa', 'lic-c60', 115, 'trim', wet_weight=8000, dry_weight=1900),
    B('pack', 'Lemon Haze', 'lic-c60', 125, 'package', wet_weight=8000, dry_weight=1800),
    B('ship', 'Purple Punch', 'lic-c60', 130, 'ship', wet_weight=8500, dry_weight=2100),
    B('c22', 'Cherry Pie', 'lic-c22', 40, 'flowering', area=None),
    B('done', 'Old batch', 'lic-c60', 200, 'done')]
def E(b, kind, ago, **kw):
    r = {'id': 'ge-%s-%s' % (b, kind), 'state_id': 'st-mo', 'license_id': 'lic-c22' if b == 'c22' else 'lic-c60', 'batch_id': 'pb-' + b, 'kind': kind, 'done_on': ds(ago), 'stage': '', 'voided': False, 'done_by': 'Sam', 'created_at': ds(ago)}
    r.update(kw); return r
T['hx_grow_events'] = [E('flower', 'stage', 30, stage='flowering'), E('dry-late', 'harvest', 10), E('cure', 'harvest', 15), E('cure', 'dry', 6),
                       E('trim', 'cure', 3), E('trim', 'lab', 1), E('pack', 'tested', 2), E('ship', 'packaged', 1)]
T['hx_cul_settings'] = []
_h = handle
def handle(route, request):
    if request.method == 'POST' and urllib.parse.urlparse(request.url).path.endswith('/hx_cul_settings'):
        r = json.loads(request.post_data); r['updated_by'] = 'Sam'; T['hx_cul_settings'].append(r)
        return route.fulfill(status=201, content_type='application/json', body=json.dumps([r]))
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
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-c60");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Cultivation', exact=True).click(); pg.wait_for_selector('#bt-wall .btx-row')
    w = pg.locator('#bt-wall')
    check(w.locator('.lmx-title', has_text='Batch Tracker').count() == 1, 'Batch tracker opens first in Cultivation')
    rows = w.locator('.btx-row:not(.hd)')
    check(rows.count() == 10, 'every running batch of this license listed (closed batch and the other license left out)')
    names = [rows.nth(i).locator('.btx-strain').inner_text() for i in range(rows.count())]
    check(names[0] == 'Purple Punch' and names[-1] in ('Runtz', 'Zkittlez'), 'sorted furthest step first (Ship to Veg)')
    check(names.index('Runtz') < names.index('Zkittlez'), 'late first within a step')
    def row(n): return w.locator('.btx-row', has=pg.locator('.btx-strain', has_text=re.compile('^' + re.escape(n) + '$')))
    def card(lbl): return w.locator('.btx-card', has=pg.locator('.c', has_text=lbl))
    check(card('1 · Veg').locator('.b').inner_text() == '2' and card('1 · Veg').locator('.late').inner_text().lower() == '1 late', 'Veg card: count and late count')
    check('90 plants' in card('1 · Veg').inner_text(), 'Veg card: plants')
    r = row('Runtz'); check('late' in r.get_attribute('class') and '10 days past day 20' in r.inner_text(), 'veg late after day 21: "10 days past day 20 - still in veg"')
    r = row('Zkittlez'); check('Move to flower + METRC tag' in r.inner_text() and 'late' not in r.get_attribute('class'), 'veg on time: next step is the move to flower')
    r = row('Gelato'); txt = r.inner_text(); check('flower' in txt.lower() and 'flower day 31' in txt and 'Harvest window opens' in txt and 'in 30 days' in txt, 'flower: day count from the move to flower, harvest window opens in 30 days')
    r = row('Sour Diesel'); check('Harvest now' in r.inner_text() and 'late' not in r.get_attribute('class'), 'harvest window open: Harvest now')
    r = row('Blue Dream'); check('late' in r.get_attribute('class') and '6 days past window' in r.inner_text(), 'harvest past the 4-day window is late')
    r = row('OG Kush'); check('late' in r.get_attribute('class') and '3 days past the 7-day target' in r.inner_text() and 'wet 12.0 kg' in r.inner_text(), 'dry over 7 days is late; wet weight shown')
    r = row('Wedding Cake'); check('6 of 14 days' in r.inner_text() and 'Cure done' in r.inner_text(), 'cure counts from the dry record against 14 days')
    r = row('Mimosa'); check('Waiting on COA' in r.inner_text() and 'sent to lab' in r.inner_text() and 'dry 1.9 kg' in r.inner_text(), 'test + trim: waiting on COA once sent to the lab')
    check(row('Lemon Haze').locator('.btx-next b').inner_text() == 'Package' and row('Purple Punch').locator('.btx-next b').inner_text() == 'Ship', 'package and ship steps')
    segs = row('Mimosa').locator('.btx-seg'); check(segs.count() == 8 and 'cur' in segs.nth(5).get_attribute('class'), 'lifecycle bar: 8 steps, current step marked')
    check(row('OG Kush').locator('.btx-meta', has_text='Drying room').count() == 1 and 'harvested' in row('OG Kush').inner_text(), 'batch shows its area and harvest date')
    # filter by step
    card('3 · Harvest').click(); pg.wait_for_timeout(150)
    check(rows.count() == 2 and w.get_by_role('button', name='Show every stage').count() == 1, 'click a step card to filter')
    card('3 · Harvest').click(); pg.wait_for_timeout(150); check(rows.count() == 10, 'click again to clear the filter')
    # seed vault
    sv = w.locator('.btx-card', has=pg.locator('.c', has_text='Seed vault'))
    check(sv.locator('.b').inner_text() == '510' and '2 strains' in sv.inner_text() and '1 low' in sv.inner_text().lower(), 'seed vault: seeds on hand (planted seeds taken off), strains, low count')
    sv.click(); pg.wait_for_selector('#bt-wall td >> text=Runtz')
    check(w.locator('tr', has_text='Runtz').locator('td', has_text='60 · low').count() == 1 and w.locator('tr', has_text='Gelato').locator('td').nth(1).inner_text() == '450', 'seed vault list: strain, on hand, low flag')
    sv.click()
    # all licenses
    w.locator('.btx-pills button', has_text='All').click(); pg.wait_for_function('document.querySelectorAll("#bt-wall .btx-row:not(.hd)").length==11')
    check(row('Cherry Pie').locator('.btx-chip', has_text='Cul 22').count() == 1, 'All: both cultivation licenses, license chip on each row')
    check(row('Cherry Pie').get_attribute('title').startswith('Switch to Heritage Cul 22'), 'batch of another license points to the license picker')
    w.locator('.btx-pills button', has_text='Cul 60').click(); pg.wait_for_function('document.querySelectorAll("#bt-wall .btx-row:not(.hd)").length==10')
    pg.screenshot(path=OUT + 'batch_tracker.png', full_page=True)
    # open a batch
    row('Mimosa').click(); md = pg.locator('.md'); md.wait_for()
    check(md.get_by_role('button', name='Test passed (COA)').count() == 1 and md.get_by_role('button', name='Sent to lab').count() == 1, 'row opens the batch with its next records')
    md.get_by_role('button', name='Edit').click(); em = pg.locator('.md').last
    check(field(em, 'Planned harvest start').count() == 0, 'no planned harvest start once harvested')
    em.get_by_role('button', name='Cancel').click(); pg.locator('.mo').first.click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    row('Gelato').click(); md = pg.locator('.md'); md.wait_for(); md.get_by_role('button', name='Edit').click(); em = pg.locator('.md').last
    field(em, 'Planned harvest start').fill((TODAY + dt.timedelta(days=5)).isoformat()); em.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Gelato')
    check(T['hx_plant_batches'][2]['harvest_start'] == (TODAY + dt.timedelta(days=5)).isoformat(), 'planned harvest start saved on the batch')
    pg.locator('.mo').first.click(position={'x': 5, 'y': 5}) if pg.locator('.mo').count() else None
    pg.wait_for_function('document.querySelector("#bt-wall") && document.querySelector("#bt-wall").innerText.indexOf("(in 5 days) · planned")>=0')
    check(True, 'tracker follows the planned harvest start')
    # targets
    w.get_by_role('button', name='Targets').click(); md = pg.locator('.md')
    field(md, 'Veg days before flower').fill('40'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('#bt-wall .msg >> text=Saved the targets for Heritage Cul 60')
    check(T['hx_cul_settings'] and T['hx_cul_settings'][0]['veg_days'] == 40 and T['hx_cul_settings'][0]['cycle_days'] == 80, 'targets saved for the license')
    pg.wait_for_timeout(300); check('late' not in row('Runtz').get_attribute('class'), 'late flags follow the license targets')
    # phone
    pg.set_viewport_size({'width': 390, 'height': 900}); pg.wait_for_timeout(300)
    check(pg.evaluate('document.querySelector("#bt-wall .btx-row.hd").offsetParent===null'), 'phone: header row hidden')
    check(pg.evaluate('document.querySelector("#bt-wall").scrollWidth<=document.querySelector("#bt-wall").clientWidth+2'), 'phone: no sideways scroll')
    w.locator('.btx-row', has_text='Purple Punch').screenshot(path=OUT + 'batch_tracker_phone_row.png')
    pg.screenshot(path=OUT + 'batch_tracker_phone.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
