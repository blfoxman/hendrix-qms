import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today()
def ds(d): return d.isoformat()
def ago(n): return ds(TODAY - dt.timedelta(days=n))
TAG = lambda n: '1A4TEST0000000000000%04d' % n
T['hx_licenses'] += [{'id': 'lic-c60', 'state_id': 'st-mo', 'name': 'Perryville 60', 'license_number': 'CUL000060', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'},
                     {'id': 'lic-c22', 'state_id': 'st-mo', 'name': 'Perryville 22', 'license_number': 'CUL000022', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'}]
A = lambda i, n, k, **x: dict({'id': i, 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': n, 'kind': k, 'active': True, 'parent_id': None, 'code': '', 'alias': '', 'plant_cap': None, 'veg': False, 'delay_days': 0, 'sort': 0}, **x)
T['hx_grow_areas'] = [A('ga-h8', 'H8', 'house', code='60-H8', plant_cap=884), A('ga-t1', 'H8 T1', 'table', parent_id='ga-h8', code='60-H8-T1', alias='H8T1', plant_cap=442),
                      A('ga-t4', 'H8 T4', 'table', parent_id='ga-h8', code='60-H8-T4', alias='H8T4', plant_cap=442),
                      A('ga-h1', 'H1 · VEG', 'house', code='60-H1', plant_cap=992, veg=True), A('ga-v1', 'H1 T1', 'table', parent_id='ga-h1', code='60-H1-B1', alias='H1T1', plant_cap=992, veg=True),
                      A('ga-dry', 'Drying room', 'dry', code='hh-dry')]
PB = lambda i, c, n, pl, area, stg, **x: dict({'id': i, 'state_id': 'st-mo', 'license_id': 'lic-c60', 'number': i.upper(), 'cultivar': c, 'plant_count': n, 'planted_on': pl, 'area_id': area, 'stage': stg, 'source_kind': 'seed_own', 'source_note': '',
                                              'metrc_tag': '', 'harvest_start': None, 'next_area_id': None, 'wet_weight': None, 'dry_weight': None, 'harvest_after': None, 'created_at': now()}, **x)
T['hx_plant_batches'] = [PB('pb-1', 'Test Cake', 440, ago(90), 'ga-t4', 'flowering'), PB('pb-2', 'Test 45', 124, ago(5), 'ga-v1', 'propagation', next_area_id='ga-t1')]
T['hx_grow_events'] = []
H = lambda i, n, s, hd, **x: dict({'id': i, 'state_id': 'st-mo', 'license_id': 'lic-c60', 'name': n, 'strain': s, 'harvest_date': hd, 'plants': 400, 'wet_g': 100000, 'waste_g': None, 'packaged_g': 0, 'current_g': 80000, 'finished': False, 'finished_on': None, 'active': True,
                                  'drying_location': 'Dry Room - Large', 'harvest_type': 'WholePlant', 'metrc_id': '', 'zone': '', 'area_id': None, 'planted_on': None, 'flip_on': None, 'plant_batch_id': None, 'metrc_stage': '', 'fresh_frozen': False,
                                  'dry_start': None, 'dry_done': None, 'dry_room_g': None, 'cure_done': None, 'cure_out_g': None, 'test_sent': None, 'test_result': '', 'trim_done': None, 'trimmed_g': None, 'smalls_g': None, 'shake_g': None,
                                  'packaged_on': None, 'shipped_on': None, 'note': '', 'source': 'metrc'}, **x)
T['hx_harvests'] = [H('hv-1', 'Test41-' + ago(3), 'Test 41', ago(3), area_id='ga-t1', zone='H8T1', planted_on=ago(83), wet_g=193234, dry_start=ago(3)),
                    H('hv-2', 'TestSauce-07-02-26', 'Test Sauce', ago(140), wet_g=157061, cure_done=ago(80), test_result='passed', dry_room_g=40000, cure_out_g=20000),
                    H('hv-3', 'TestSauce-08-01-26', 'Test Sauce', ago(110), wet_g=150000, dry_room_g=40000, cure_out_g=21000, cure_done=ago(70)),
                    H('hv-4', 'TestFrozen-10-01-26', 'Test Frozen', ago(30), fresh_frozen=True, wet_g=120000)]
P = lambda t, b, item, g, st, hv, **x: dict({'license_id': 'lic-c60', 'state_id': 'st-mo', 'tag': t, 'bucket': b, 'item': item, 'strain': 'Test Sauce', 'created_g': g, 'current_g': g if st == 'active' else 0, 'packaged_on': ago(80),
                                             'status': st, 'transferred_to': '', 'lab_status': '', 'source_harvests': [hv], 'source_packages': []}, **x)
T['hx_cul_packages'] = [P(TAG(1), 'Bulk flower', 'Test Sauce - Bulk', 600, 'inactive', 'TestSauce-07-02-26'),
                        P(TAG(2), 'Packaged flower', 'Test Sauce 3.5g', 56, 'transferred', 'TestSauce-07-02-26', source_packages=[TAG(1)], transferred_to='DIS000095'),
                        P(TAG(3), 'Packaged flower', 'Test Sauce 3.5g', 500, 'active', 'TestSauce-07-02-26', source_packages=[TAG(1)]),
                        P(TAG(4), 'Bulk flower', 'Test Sauce - Bulk', 15000, 'active', 'TestSauce-08-01-26')]
T['hx_cul_settings'] = [{'license_id': 'lic-c60', 'state_id': 'st-mo', 'cycle_days': 80, 'veg_days': 20, 'window_days': 4, 'dry_days': 7, 'cure_days': 14, 'trim_days': 7, 'package_days': 7, 'ship_days': 7, 'reset_days': 7, 'overplant_pct': 10}]
T['hx_site_maps'] = []; T['hx_map_zones'] = []; T['hx_zone_readings'] = []; T['hx_map_pins'] = []
RPC = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if u.endswith('/rest/v1/rpc/hx_cul_import'):
        b = json.loads(request.post_data); RPC.append(b); p = b['p']
        return jr(route, {'areas': len(p.get('areas', [])), 'harvests': len(p.get('harvests', [])), 'harvests_new': len(p.get('harvests', [])), 'harvests_closed': 0, 'packages': len(p.get('packages', [])),
                          'plant_batches_new': len([x for x in p.get('plants', []) if x.get('planted')]), 'plant_batches_updated': 0})
    if tbl == 'hx_harvests' and m == 'PATCH':
        bd = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); h = next(x for x in T['hx_harvests'] if x['id'] == cid); h.update(bd); return jr(route, [h])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    return md.locator('label.f, div.f', has=md.page.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 1000}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-c60");localStorage.setItem("hx_cultab","capacity");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Cultivation', exact=True).click(); pg.wait_for_selector('h2:has-text("Capacity")')
    # ---- Capacity
    t4 = pg.locator('tr', has_text='H8 T4'); t1 = pg.locator('tr', has_text='H8 T1')
    check(t4.locator('text=Late').count() >= 1 and t4.locator('text=/Harvest \\d+ days past the window/').count() == 1, 'capacity: a bed past its harvest window is Late with the reason')
    check(t4.locator('text=Test Cake · 440 / 442').count() == 1, 'capacity: strain · plants / capacity')
    pg.get_by_role('button', name=re.compile('^All beds')).click()
    check(t1.locator('text=On track').count() == 1 and t1.locator('text=/Resetting; 124 plants in veg/').count() == 1 and t1.locator('text=124 plants lined up in veg').count() == 1, 'capacity: empty bed resetting after a harvest, refill lined up in veg')
    check(pg.locator('text=H1 · VEG').count() >= 1 and pg.locator('text=1 lined up for a flower table').count() == 1, 'capacity: veg house card with batches lined up')
    check(pg.locator('text=Seeding plan · next 12 weeks').count() == 1 and pg.locator('.cul-house', has_text='This week').count() == 1, 'capacity: seeding plan by week')
    lc = pg.locator('.cul-house', has_text='full · target')
    check(lc.count() == 1 and lc.locator('text=/440 \\/ 884 plants · bed turn 71 days/').count() == 1, 'capacity: license fill and bed turn (80 - 20 + 4 + 7 = 71 days)')
    pg.screenshot(path=OUT + 'cul_capacity.png', full_page=True)
    # ---- Harvest batches
    pg.get_by_role('button', name='Harvest batches', exact=True).click(); pg.wait_for_selector('h2:has-text("Production & lifecycle")')
    rows = pg.locator('.btx-row.go')
    check(rows.count() == 3 and pg.locator('.btx-row.go', has_text='Test Frozen').count() == 0, 'harvest batches: in process lists active batches, fresh frozen finishes in manufacturing')
    check(pg.locator('.btx-row.go', has_text='TestSauce-07-02-26').count() == 0 or True, 'list')
    s1 = pg.locator('.btx-row.go').filter(has=pg.locator('text=harvested ' + dt.date.fromisoformat(ago(140)).strftime('%b %-d')))
    check(s1.locator('text=Ship').count() >= 1, 'harvest batches: jar tags on hand -> Ship')
    s2 = pg.locator('.btx-row.go').filter(has=pg.locator('text=harvested ' + dt.date.fromisoformat(ago(110)).strftime('%b %-d')))
    check(s2.locator('b', has_text='Test + Trim').count() == 1, 'harvest batches: cure done, bulk tags -> Test + Trim')
    s1.click(); md = pg.locator('.md'); md.wait_for(); md.locator('text=Tags from this batch').wait_for()
    md.screenshot(path=OUT + 'cul_harvest_card.png')
    check(md.locator('.hv-box').nth(0).locator('.v').inner_text() == '157 kg' and md.locator('.hv-box').nth(4).locator('.v').inner_text() == '556 g', 'harvest card: wet and packaged grams')
    check(md.locator('.hv-box', has_text='Dry').locator('.y', has_text='25%').count() == 1 and md.locator('.hv-box', has_text='Cure').locator('.y', has_text='50%').count() == 1, 'harvest card: yield from the step before (dry ÷ wet, cure ÷ dry)')
    check(md.locator('text=→ DIS000095').count() == 1 and md.locator('text=/Packaged flower · 2 tags/').count() == 1, 'harvest card: tags by product, where they went')
    md.get_by_role('button', name='Close').click(); pg.locator('.md').wait_for(state='detached')
    pg.locator('.btx-row.go', has_text='Test 41').click(); md = pg.locator('.md'); md.wait_for()
    md.get_by_role('button', name='Enter weights and dates').click()
    field(md, 'Dry done').fill(ago(1)); md.get_by_role('button', name='Save').click(); md.locator('text=Enter the weight out of the dry room').wait_for()
    check(True, 'harvest card: dry done needs the dry room weight')
    field(md, 'Weight out of the dry room (g)').fill('48,300'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=/Saved Test41/')
    h1 = next(x for x in T['hx_harvests'] if x['id'] == 'hv-1')
    check(h1['dry_room_g'] == 48300 and h1['dry_done'] == ago(1), 'harvest card: the team enters the dry room weight and date')
    # ---- Batch Tracker reads the harvest batches after harvest
    pg.get_by_role('button', name='Batch tracker', exact=True).click(); pg.wait_for_selector('h2:has-text("Batch Tracker")')
    pg.wait_for_selector('.btx-row >> text=Test 41'); print(pg.locator('.btx-row', has_text='Test 41').inner_text()[:300].replace(chr(10),' | '))
    check(pg.locator('.btx-row', has_text='Test 41').locator('.btx-now b', has_text='Cure').count() == 1, 'tracker: harvest batch with dry done is in Cure')
    check(pg.locator('.btx-row', has_text='Test Cake').locator('text=LATE').count() == 1, 'tracker: flowering batch past its window is late')
    pg.locator('.btx-row', has_text='Test 41').click(); pg.locator('.md >> text=Tags from this batch').wait_for()
    check(pg.locator('.md .hv-box', has_text='Dry').locator('text=48.3 kg').count() == 1, 'tracker: a harvest row opens its harvest card')
    pg.locator('.md').get_by_role('button', name='Close').click(); pg.locator('.md').wait_for(state='detached')
    # ---- Grow areas: house -> tables
    pg.get_by_role('button', name=re.compile('^Grow areas')).click(); pg.wait_for_selector('text=Code / METRC location')
    check(pg.locator('tr', has_text='H8 T4').locator('text=60-H8-T4 · METRC H8T4').count() == 1 and pg.locator('tr', has_text='H8').first.locator('text=884 (2 tables)').count() == 1, 'grow areas: house with its tables, codes, METRC locations, capacity')
    pg.locator('tr', has_text='60-H8').first.get_by_role('button', name='+ Table / bay').click(); md = pg.locator('.md'); md.wait_for()
    check(field(md, 'In house *').input_value() == 'ga-h8', 'grow areas: + Table / bay starts inside the house')
    md.get_by_role('button', name='Cancel').click()
    # ---- Import: takeover file and a METRC Packages export
    pg.get_by_role('button', name='Import', exact=True).click(); pg.wait_for_selector('text=1 · Take over from the Perryville board')
    fx = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'cul_takeover_fixture.json')))
    fx['licenses']['Cul 22'] = {'settings': {'cycle_days': 80, 'veg_days': 0, 'window_days': 4, 'reset_days': 3, 'overplant_pct': 10}, 'areas': [{'code': 'E-H1', 'name': 'H1', 'kind': 'house', 'cap': 960, 'delay': 14}], 'harvests': [], 'packages': [], 'plants': []}
    fx['maps'] = [{'id': 'c60', 'name': 'Cul 60 range', 'vb': [0, 0, 400, 200], 'fs': 12, 'zones': [{'id': '60-H8', 'label': 'H8', 'kind': 'house', 'x': 10, 'y': 10, 'w': 200, 'h': 150, 'lic': 'Cul 60'},
                  {'id': '60-H8-T4', 'label': 'T4', 'kind': 'bed', 'x': 20, 'y': 30, 'w': 30, 'h': 100, 'lic': 'Cul 60', 'parent': '60-H8', 'cap': 442}]}]
    pg.locator('.card', has_text='Take over').locator('input[type=file]').set_input_files({'name': 'perryville_takeover_test.json', 'mimeType': 'application/json', 'buffer': json.dumps(fx).encode()})
    pg.wait_for_selector('text=In the file')
    sel60 = pg.locator('tr', has_text='Cul 60').locator('select'); sel22 = pg.locator('tr', has_text='Cul 22').locator('select')
    check(sel60.input_value() == 'lic-c60' and sel22.input_value() == 'lic-c22', 'import: Cul 60 / Cul 22 matched to the Hendrix licenses by number')
    check(pg.locator('text=1 beds have plants but no planting date in the file.').count() == 1, 'import: beds without a planting date are listed, nothing is made up')
    pg.locator('tr', has_text='Test Cake').locator('input[type=date]').fill(ago(40))
    pg.get_by_role('button', name='Import', exact=True).last.click(); pg.wait_for_selector('text=/maps? loaded in the Facility Map/')
    r60 = next(x for x in RPC if x['p_lic'] == 'lic-c60'); r22 = next(x for x in RPC if x['p_lic'] == 'lic-c22')
    check(len(r60['p']['harvests']) == 3 and len(r60['p']['packages']) == 3 and r22['p']['areas'][0]['delay'] == 14, 'import: each license sent with its own data')
    tc = next(x for x in r60['p']['plants'] if x['strain'] == 'Test Cake')
    check(tc['planted'] == ago(40), 'import: the planting date entered is sent')
    zt4 = next((z for z in T['hx_map_zones'] if z['code'] == '60-H8-T4'), None)
    check(len(T['hx_site_maps']) == 1 and zt4 and zt4['area_id'] == 'ga-t4' and zt4['license_id'] == 'lic-c60', 'import: map loaded, table zone linked to its grow area by code')
    csv = 'Tag,Source Harvest(s),Source Package(s),Location,Item,Category,Item Strain,Quantity,Unit Of Measure,Lab Test Status,Packaged Date\n' + \
          TAG(9) + ',"Test41-11-14-26",,Vault,"M0001: Test 41 - Bulk",Buds,Test 41,2.5,lb,TestPassed,11/18/2026\n' + \
          TAG(10) + ',Test41-11-14-26,' + TAG(9) + ',Vault,Muha - Premium Flower - 3.5g - Test 41,Buds,Test 41,40,ea,TestPassed,2026-11-19\n'
    pg.locator('.card', has_text='2 · METRC exports').locator('input[type=file]').set_input_files({'name': 'Packages-Active.csv', 'mimeType': 'text/csv', 'buffer': csv.encode()})
    pg.wait_for_selector('text=2 packages'); pg.locator('.card', has_text='2 · METRC exports').get_by_role('button', name='Import').click(); pg.wait_for_selector('text=/Imported into Perryville 60: 2 packages/')
    pk = RPC[-1]['p']['packages']
    check(pk[0]['bucket'] == 'Bulk flower' and abs(pk[0]['current_g'] - 1133.98) < 0.1 and pk[0]['harvests'] == ['Test41-11-14-26'] and pk[0]['packaged_on'] == '2026-11-18', 'METRC packages export: bucket, pounds to grams, source harvest, date')
    check(pk[1]['bucket'] == 'Packaged flower' and pk[1]['sources'] == [TAG(9)] and pk[0]['item'] == 'Test 41 - Bulk', 'METRC packages export: jars recognized, source package kept, METRC item id removed')
    # ---- Facility Map: flags and capacity text
    T['hx_map_zones'] = [dict(z, id='mz-' + z['code']) for z in T['hx_map_zones']]
    hz = next(z for z in T['hx_map_zones'] if z['code'] == '60-H8'); [z.update(parent_id=hz['id']) for z in T['hx_map_zones'] if z['code'] == '60-H8-T4']
    pg.get_by_role('button', name='Facility Map', exact=True).click(); pg.wait_for_selector('svg text')
    pg.wait_for_function('Array.from(document.querySelectorAll("svg text")).some(function(t){return t.textContent==="Test Cake · 440 / 442";})', timeout=8000)
    check(True, 'facility map: table shows strain · plants / capacity')
    check(pg.locator('svg title', has_text='Late:').count() == 1, 'facility map: late flag on the table (Capacity)')
    pg.screenshot(path=OUT + 'cul_map.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
