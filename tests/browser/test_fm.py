import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today()
def ds(n): return (TODAY - dt.timedelta(days=n)).isoformat()
def iso(h): return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=h)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
T['hx_licenses'] += [{'id': 'lic-c60', 'state_id': 'st-mo', 'name': 'Heritage Cul 60', 'license_number': 'CUL000060', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'},
                     {'id': 'lic-c22', 'state_id': 'st-mo', 'name': 'Heritage Cul 22', 'license_number': 'CUL000022', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'}]
T['hx_grow_areas'] = [{'id': 'ga-t1', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': 'H2 T1', 'kind': 'indoor', 'active': True, 'sort': 0},
                      {'id': 'ga-t2', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': 'H2 T2', 'kind': 'indoor', 'active': True, 'sort': 1},
                      {'id': 'ga-dry', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': 'Drying room', 'kind': 'dry', 'active': True, 'sort': 2},
                      {'id': 'ga-e1', 'state_id': 'st-mo', 'license_id': 'lic-c22', 'name': 'E-H1-B1-NE', 'kind': 'greenhouse', 'active': True, 'sort': 0}]
def B(i, cult, lic, planted, stage, area, plants=40, **kw):
    r = {'id': 'pb-' + i, 'state_id': 'st-mo', 'license_id': lic, 'number': 'PB-' + i, 'cultivar': cult, 'source_kind': 'seed_own', 'source_lot_id': None, 'planted_on': ds(planted), 'plant_count': plants,
         'area_id': area, 'stage': stage, 'harvest_after': None, 'harvest_start': None, 'wet_weight': None, 'dry_weight': None, 'harvest_tag': '', 'metrc_tag': '', 'created_at': ds(planted)}
    r.update(kw); return r
T['hx_plant_batches'] = [B('fl', 'Gelato', 'lic-c60', 50, 'flowering', 'ga-t1', 40), B('veg', 'Zkittlez', 'lic-c60', 10, 'vegetative', 'ga-t2', 30),
                         B('dry', 'OG Kush', 'lic-c60', 100, 'drying', 'ga-dry', 36, wet_weight=12000), B('e1', 'Cherry Pie', 'lic-c22', 60, 'flowering', 'ga-e1', 20)]
T['hx_grow_events'] = [{'id': 'ge-1', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'batch_id': 'pb-dry', 'kind': 'harvest', 'done_on': ds(10), 'voided': False, 'done_by': 'Sam', 'created_at': ds(10)}]
T['hx_cul_settings'] = []
T['hx_lots'] = [{'id': 'lt-1', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'number': 'RCV-1', 'item': 'Packaged flower 3.5 g', 'category': 'Packaged flower', 'status': 'accepted', 'quantity': 400, 'qty_used': 100, 'unit': 'each'}]
T['hx_equipment'] = [{'id': 'eq-1', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'number': 'EQ-1', 'name': 'Dehumidifier 1', 'status': 'in_service'}]
T['hx_site_maps'] = [{'id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'license_ids': ['lic-c60'], 'name': 'Cul 60 range', 'width': 1000, 'height': 600, 'font_size': None, 'decor': [{'x': 20, 'y': 580, 'text': 'CORRIDOR'}],
                      'drawing_path': None, 'drawing_note': '', 'sort': 0, 'active': True, 'updated_at': '1'}]
def Z(i, code, kind, x, y, w, h, **kw):
    r = {'id': i, 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'code': code, 'label': '', 'name': '', 'kind': kind, 'x': x, 'y': y, 'w': w, 'h': h, 'parent_id': None, 'cap': None, 'info': '', 'vert': False,
         'area_id': None, 'day_f': None, 'night_f': None, 'rh_target': None, 'note': '', 'sort': 0}
    r.update(kw); return r
T['hx_map_zones'] = [Z('mz-h2', '60-H2', 'house', 20, 20, 560, 300, label='House 2', name='House 2', day_f=78, night_f=78, rh_target=55),
                     Z('mz-t1', '60-H2-T1', 'bed', 40, 70, 150, 230, label='T1', parent_id='mz-h2', area_id='ga-t1', cap=60),
                     Z('mz-t2', '60-H2-T2', 'bed', 210, 70, 150, 230, label='T2', parent_id='mz-h2', area_id='ga-t2'),
                     Z('mz-t3', '60-H2-T3', 'bed', 380, 70, 150, 230, label='T3', parent_id='mz-h2'),
                     Z('mz-dry', '60-DRY', 'room', 620, 20, 340, 140, label='Drying room', name='Drying room', info='dry', area_id='ga-dry'),
                     Z('mz-vault', '60-VAULT', 'room', 620, 200, 340, 120, label='Vault', name='Vault', info='vault')]
T['hx_zone_readings'] = [{'id': 'zr-1', 'zone_id': 'mz-t1', 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'read_at': iso(3), 'temp_f': 83, 'rh': 60, 'note': '', 'recorded_by': 'Sam', 'voided': False},
                         {'id': 'zr-2', 'zone_id': 'mz-t1', 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'read_at': iso(1), 'temp_f': 85, 'rh': 62, 'note': '', 'recorded_by': 'Sam', 'voided': False},
                         {'id': 'zr-3', 'zone_id': 'mz-h2', 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'read_at': iso(2), 'temp_f': 77, 'rh': 55, 'note': '', 'recorded_by': 'Sam', 'voided': False}]
T['hx_map_pins'] = [{'id': 'mp-1', 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'zone_id': 'mz-t1', 'x': 115, 'y': 150, 'type': 'light', 'name': 'LED 645', 'model': '', 'watts': 645, 'qty': 6, 'hrs': 12, 'gen_kw': None, 'serves': [], 'fov': None, 'dir': None, 'equipment_id': None, 'note': ''},
                    {'id': 'mp-2', 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'zone_id': None, 'x': 600, 'y': 560, 'type': 'generator', 'name': 'Gen A', 'model': '', 'watts': None, 'qty': 1, 'hrs': 24, 'gen_kw': 5, 'serves': ['mz-h2'], 'fov': None, 'dir': None, 'equipment_id': None, 'note': ''},
                    {'id': 'mp-3', 'map_id': 'sm-60', 'state_id': 'st-mo', 'license_id': 'lic-c60', 'zone_id': 'mz-t3', 'x': 400, 'y': 90, 'type': 'camera', 'name': 'Cam 1', 'model': '', 'watts': None, 'qty': 1, 'hrs': 24, 'gen_kw': None, 'serves': [], 'fov': 90, 'dir': 45, 'equipment_id': None, 'note': ''}]
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    return md.locator('label.f, div.f', has=md.page.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
IMPORT = json.dumps({'name': 'East Cul 22', 'vb': [0, 0, 800, 400], 'zones': [
    {'id': 'E-H1', 'label': 'H1', 'kind': 'house', 'x': 10, 'y': 10, 'w': 380, 'h': 300, 'lic': '22'},
    {'id': 'E-H1-B1-NE', 'label': 'B1 NE', 'kind': 'bay', 'x': 20, 'y': 40, 'w': 160, 'h': 120, 'lic': '22', 'cap': 50},
    {'id': 'E-DRY', 'label': 'Dry', 'kind': 'room', 'x': 420, 'y': 10, 'w': 200, 'h': 120, 'lic': '22', 'info': 'dry'}]})
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1440, 'height': 1000}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-c60");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Facility Map', exact=True).click(); pg.wait_for_selector('#fm-wall g[data-zid]')
    w = pg.locator('#fm-wall')
    check(w.locator('.lmx-title', has_text='Facility Map').count() == 1, 'Facility Map opens from the sidebar (Facility group)')
    check(w.locator('g[data-zid]').count() == 6, 'map draws every zone of the map')
    fill = lambda zid: w.locator('g[data-zid="%s"] > rect' % zid).first.get_attribute('fill')
    text = lambda zid: ' '.join(w.locator('g[data-zid="%s"] text' % zid).all_text_contents())
    check(fill('mz-t1') == '#46A96A', 'Stage: flowering bed is green')
    check(fill('mz-t2') == '#C8932B', 'Stage: veg bed is amber')
    check(fill('mz-t3') == 'url(#fm-hatch)', 'Stage: bed with no grow area is hatched (not assigned)')
    check('Gelato · 40' in text('mz-t1'), 'Stage: bed shows strain and plants')
    check('1 drying' in text('mz-dry'), 'Dry room shows what is drying')
    check('1 lot' in text('mz-vault'), 'Vault shows lots on hand')
    check(w.locator('.fmx-leg', has_text='Harvest Ready').count() == 1, 'Stage legend')
    check(w.locator('text=CORRIDOR').count() == 1, 'decor drawn')
    kp = lambda c: w.locator('.lmx-kpi', has=pg.locator('.c', has_text=c)).locator('.b').inner_text()
    check(kp('Plants in ground') == '70', 'KPI: plants in ground on mapped beds (40 + 30)')
    check(kp('Beds planted now') == '2 / 3', 'KPI: beds planted now')
    check(kp('Zones with a reading') == '2 / 6', 'KPI: zones with a fresh reading')
    check(kp('Connected load') == '3.9 kW', 'KPI: connected load from pins (645 W x 6)')
    w.locator('g[data-zid="mz-t1"]').click()
    side = w.locator('.fmx-side')
    check(side.locator('h3', has_text='T1').count() == 1 and 'Gelato' in side.inner_text() and 'Flowering' in side.inner_text(), 'click a bed: panel shows strain and stage')
    check('40 / 60 capacity' in side.inner_text(), 'panel: plants against capacity')
    check('85 °F' in side.inner_text() and 'Hot' in side.inner_text(), 'panel: latest reading and band against the house target (inherited)')
    check('LED 645' in side.inner_text() and '3.9 kW' in side.inner_text(), 'panel: equipment and connected load')
    check(side.locator('svg polyline').count() == 1, 'panel: temperature sparkline')
    w.locator('g[data-zid="mz-dry"]').click()
    check('drying now' in side.inner_text().lower() and 'OG Kush' in side.inner_text() and side.locator('.late', has_text='day 10 of 7').count() == 1, 'dry room panel: batch drying, days against the 7-day target, late in red')
    w.locator('g[data-zid="mz-vault"]').click()
    check('Packaged flower' in side.inner_text() and '300 each' in side.inner_text(), 'vault panel: on hand by category')
    # Plants overlay
    w.locator('.fmx-pills button', has_text='Plants').click()
    check(fill('mz-t1') == 'rgba(212,175,55,0.90)' and fill('mz-t2') == 'rgba(212,175,55,0.72)', 'Plants: gold heat scaled to the busiest bed')
    # Temperature overlay
    w.locator('.fmx-pills button', has_text='Temperature').click()
    check(fill('mz-t1') == '#C05B4E', 'Temperature: 85 vs 78 target is Hot')
    check('77°*' in text('mz-t2'), 'Temperature: bed with no reading shows the house reading with *')
    check(fill('mz-t2') == '#46A96A', 'Temperature: inherited reading on target')
    # Power overlay
    w.locator('.fmx-pills button', has_text='Power').click()
    check('3.9 kW' in text('mz-t1'), 'Power: bed shows connected load')
    check(w.locator('.fmx-tbl', has_text='Gen A').count() == 1 and w.locator('.fmx-tbl tr', has_text='Gen A').locator('text=3.9 kW (77%)').count() == 1, 'Power: generator served load against capacity')
    # Equipment overlay: place a fan in T2
    w.locator('.fmx-pills button', has_text='Equipment').click()
    check(w.locator('g[data-pid]').count() == 3, 'Equipment: pins drawn')
    check(w.locator('g[data-pid="mp-3"] path').count() >= 2, 'Equipment: camera draws its coverage cone')
    w.locator('.fmx-leg button', has_text='Fan').click()
    bb = w.locator('g[data-zid="mz-t2"] > rect').bounding_box()
    pg.mouse.click(bb['x'] + bb['width'] / 2, bb['y'] + bb['height'] * 0.8)
    md = pg.locator('.md', has_text='Equipment pin'); md.wait_for()
    check('T2' in md.locator('h2').inner_text() or '60-H2-T2' in md.locator('h2').inner_text(), 'placed pin finds its zone')
    field(md, 'Watts').fill('150'); field(md, 'Quantity').fill('2'); md.get_by_role('button', name='Save').click(); md.wait_for(state='detached')
    pin = [p for p in T['hx_map_pins'] if p['type'] == 'fan']
    check(len(pin) == 1 and pin[0]['zone_id'] == 'mz-t2' and pin[0]['watts'] == 150 and pin[0]['qty'] == 2, 'fan pin saved in T2 with watts and quantity')
    pg.wait_for_timeout(300)
    check(kp('Connected load') == '4.2 kW', 'connected load updates (3870 + 300 W)')
    # drag the fan to T3
    w.locator('.fmx-leg button.on').click() if w.locator('.fmx-leg button.on').count() else None
    pg.wait_for_timeout(200)
    pb = w.locator('g[data-pid="%s"]' % pin[0]['id']).bounding_box(); t3 = w.locator('g[data-zid="mz-t3"] > rect').bounding_box()
    pg.mouse.move(pb['x'] + pb['width'] / 2, pb['y'] + pb['height'] / 2); pg.mouse.down()
    pg.mouse.move(t3['x'] + t3['width'] / 2, t3['y'] + t3['height'] * 0.7, steps=8); pg.mouse.up(); pg.wait_for_timeout(400)
    check(pin[0]['zone_id'] == 'mz-t3', 'dragging a pin moves it and re-detects its zone')
    # log a reading on T3
    w.locator('.fmx-pills button', has_text='Stage').click()
    w.locator('g[data-zid="mz-t3"]').click()
    side.get_by_role('button', name='Log a reading').click()
    md = pg.locator('.md', has_text='Log a reading'); field(md, 'Temperature').fill('72'); field(md, 'Humidity').fill('50')
    md.get_by_role('button', name='Log reading').click(); md.wait_for(state='detached')
    r = [x for x in T['hx_zone_readings'] if x['zone_id'] == 'mz-t3']
    check(len(r) == 1 and r[0]['temp_f'] == 72 and r[0]['rh'] == 50, 'reading logged for the zone')
    # set targets on T3
    side.get_by_role('button', name='Set targets').click()
    md = pg.locator('.md', has_text='Targets'); field(md, 'Day target').fill('76'); field(md, 'RH target').fill('50'); md.get_by_role('button', name='Save').click(); md.wait_for(state='detached')
    z3 = next(z for z in T['hx_map_zones'] if z['id'] == 'mz-t3')
    check(z3['day_f'] == 76 and z3['night_f'] is None and z3['rh_target'] == 50, 'targets saved on the zone')
    # edit map: draw a new zone
    w.get_by_role('button', name='Edit map').click()
    w.get_by_role('button', name='Draw zone').click()
    svgb = w.locator('.fmx-map svg').bounding_box()
    pg.mouse.move(svgb['x'] + svgb['width'] * 0.15, svgb['y'] + svgb['height'] * 0.8); pg.mouse.down()
    pg.mouse.move(svgb['x'] + svgb['width'] * 0.35, svgb['y'] + svgb['height'] * 0.92, steps=6); pg.mouse.up()
    md = pg.locator('.md', has_text='New zone'); md.wait_for()
    field(md, 'Zone id').fill('60-H2-T3'); md.get_by_role('button', name='Save').click()
    check(md.locator('.msg.err', has_text='already on this map').count() == 1, 'zone id must be unique on the map')
    field(md, 'Zone id').fill('60-MIX'); field(md, 'Label on the map').fill('Mix room'); field(md, 'Kind').select_option('room')
    md.get_by_role('button', name='Save').click(); md.wait_for(state='detached'); pg.wait_for_timeout(300)
    nz = next((z for z in T['hx_map_zones'] if z['code'] == '60-MIX'), None)
    check(nz is not None and nz['w'] > 50 and nz['h'] > 20 and w.locator('g[data-zid="%s"]' % nz['id']).count() == 1, 'drawn zone saved with its rectangle and drawn')
    # move it by dragging
    w.locator('g[data-zid="%s"]' % nz['id']).click(); pg.wait_for_timeout(100)
    zb = w.locator('g[data-zid="%s"] > rect' % nz['id']).first.bounding_box(); x0 = nz['x']
    pg.mouse.move(zb['x'] + zb['width'] / 2, zb['y'] + zb['height'] / 2); pg.mouse.down(); pg.mouse.move(zb['x'] + zb['width'] / 2 + 40, zb['y'] + zb['height'] / 2, steps=5); pg.mouse.up(); pg.wait_for_timeout(300)
    check(nz['x'] > x0 + 10, 'selected zone moves by dragging (edit mode)')
    # zoom buttons
    vb0 = w.locator('.fmx-map svg').get_attribute('viewBox')
    w.locator('.fmx-zoom button[title="Zoom in"]').click(); vb1 = w.locator('.fmx-map svg').get_attribute('viewBox')
    check(float(vb1.split()[2]) < float(vb0.split()[2]), 'zoom in narrows the view')
    w.locator('.fmx-zoom button', has_text='Fit').click()
    check(w.locator('.fmx-map svg').get_attribute('viewBox') == vb0, 'Fit shows the whole map again')
    # export JSON
    with pg.expect_download() as dl: w.get_by_role('button', name='Export JSON').click()
    ex = json.loads(open(dl.value.path()).read())
    check(len(ex['zones']) == 7 and any(z['id'] == '60-H2-T1' and z['parent'] == '60-H2' and z['lic'] == 'CUL000060' for z in ex['zones']), 'Export JSON writes the zone list (ids, parents, licenses)')
    # import a new map from JSON (Perryville format)
    w.get_by_role('button', name='Import a new map').click()
    md = pg.locator('.md', has_text='Import a map'); md.locator('textarea').fill(IMPORT)
    check('3 zones' in md.inner_text() and '1 houses' in md.inner_text(), 'import preview counts the zones')
    check(md.locator('select').first.input_value() == 'lic-c22', 'import matches "lic": "22" to Cul 22')
    md.get_by_role('button', name='Import').click(); md.wait_for(state='detached'); pg.wait_for_timeout(400)
    m2 = next((m for m in T['hx_site_maps'] if m['name'] == 'East Cul 22'), None)
    zz = [z for z in T['hx_map_zones'] if m2 and z['map_id'] == m2['id']]
    check(m2 is not None and m2['license_ids'] == ['lic-c22'] and m2['width'] == 800, 'import made the map with its license and size')
    hz = next((z for z in zz if z['code'] == 'E-H1'), {}); bz = next((z for z in zz if z['code'] == 'E-H1-B1-NE'), {})
    check(len(zz) == 3 and bz.get('parent_id') == hz.get('id') and bz.get('cap') == 50, 'import: bays found their house (parent) and capacity')
    check(bz.get('area_id') == 'ga-e1', 'import: bay linked to the grow area with the same name')
    check(w.locator('.fmx-pills button.on', has_text='East Cul 22').count() == 1, 'imported map opens')
    pg.wait_for_selector('#fm-wall g[data-zid="%s"]' % bz['id'])
    check('Cherry Pie · 20' in text(bz['id']), 'imported map colours from plant batches straight away')
    # re-import into the same map updates by id
    w.get_by_role('button', name='Import zones (JSON)').click()
    md = pg.locator('.md', has_text='Import zones into'); md.locator('textarea').fill(IMPORT.replace('"w": 160', '"w": 170'))
    md.get_by_role('button', name='Import').click(); md.wait_for(state='detached'); pg.wait_for_timeout(300)
    zz = [z for z in T['hx_map_zones'] if z['map_id'] == m2['id']]
    check(len(zz) == 3 and next(z for z in zz if z['code'] == 'E-H1-B1-NE')['w'] == 170, 'importing again updates zones by id (no duplicates)')
    check(any(a['table_name'] == 'hx_map_zones' for a in T['hx_audit_log']), 'zone changes in the audit trail')
    w.locator('.fmx-pills button', has_text='Cul 60 range').click(); pg.wait_for_selector('#fm-wall g[data-zid="mz-t1"]')
    check(w.get_by_role('button', name='Edit map').count() == 1, 'switching maps leaves edit mode')
    w.locator('g[data-zid="mz-t1"]').click()
    pg.screenshot(path=OUT + 'facility_map.png', full_page=True)
    for o in ('Temperature', 'Equipment', 'Stage'):
        w.locator('.fmx-pills button', has_text=o).click(); pg.wait_for_timeout(150); w.locator('.fmx-grid').screenshot(path=OUT + 'fm_%s.png' % o.lower())
    # phone
    pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
    check(pg.evaluate('document.documentElement.scrollWidth') <= 392, 'phone: no sideways scroll')
    check(w.locator('.fmx-side').bounding_box()['y'] > w.locator('.fmx-map').bounding_box()['y'] + 100, 'phone: panel goes under the map')
    b.close()
check(not [e for e in errors if e.startswith('JS')], 'no JS errors')
print('errors:', errors)
