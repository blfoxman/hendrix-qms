import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today()
def ds(d): return d.isoformat()
T['hx_licenses'].append({'id': 'lic-cul', 'state_id': 'st-mo', 'name': 'Green Acres', 'license_number': 'CUL000777', 'license_type': 'Cultivation', 'active': True, 'operation': 'cultivation'})
T['hx_lots'] += [{'id': 'lt-cl', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'RCV-2026-010', 'item': 'Gelato clones', 'category': 'Clones / seeds', 'status': 'accepted', 'received_on': ds(TODAY), 'supplier_id': 's1'},
                 {'id': 'lt-md', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'RCV-2026-011', 'item': 'Coco coir', 'category': 'Grow media / soil', 'status': 'accepted', 'received_on': ds(TODAY), 'supplier_id': 's1'}]
T['hx_chemicals'] = [{'id': 'ch-n', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'CHEM-001', 'name': 'Bloom A+B', 'manufacturer': 'GH', 'purpose': 'Nutrient / fertilizer', 'grade': 'non_food', 'status': 'approved', 'sds_files': [{'path': 'x', 'name': 'sds.pdf'}], 'storage_area': 'Nutrient room', 'epa_reg': ''},
                     {'id': 'ch-p', 'state_id': 'st-mo', 'license_id': 'lic-cul', 'number': 'CHEM-002', 'name': 'Neem oil', 'manufacturer': 'X', 'purpose': 'Pesticide / crop protection', 'grade': 'non_food', 'status': 'approved', 'sds_files': [{'path': 'y', 'name': 'sds2.pdf'}], 'storage_area': 'Shed', 'epa_reg': '70051-2'}]
for t in ('hx_grow_areas', 'hx_plant_batches', 'hx_grow_events'): T[t] = []
SEQ = [0]
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def apply(bid):
    b = next(x for x in T['hx_plant_batches'] if x['id'] == bid); cps = [v for v in T['hx_grow_events'] if v['batch_id'] == bid and v['kind'] == 'crop_protection' and not v['voided'] and v.get('phi_days') is not None]
    b['harvest_after'] = max(ds(dt.date.fromisoformat(v['done_on']) + dt.timedelta(days=v['phi_days'])) for v in cps) if cps else None
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_grow_areas' and m == 'POST':
        r = json.loads(request.post_data); r.setdefault('active', True); T['hx_grow_areas'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_plant_batches' and m == 'POST':
        r = json.loads(request.post_data); SEQ[0] += 1; r.update({'number': 'PB-2026-%03d' % SEQ[0], 'stage': 'propagation', 'harvest_after': None, 'wet_weight': None, 'dry_weight': None, 'harvest_tag': '', 'created_at': now()}); T['hx_plant_batches'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_grow_events' and m == 'POST':
        r = json.loads(request.post_data); b = next(x for x in T['hx_plant_batches'] if x['id'] == r['batch_id'])
        if r['kind'] == 'harvest' and b['harvest_after'] and r['done_on'] < b['harvest_after']: return jr(route, {'message': 'Too early to harvest'}, 400)
        if r['chemical_id']:
            c = next(x for x in T['hx_chemicals'] if x['id'] == r['chemical_id']); r['product'] = c['name']; r['epa_reg'] = c['epa_reg']
        r.update({'recorded_by': 'Sam', 'voided': False, 'created_at': now()}); T['hx_grow_events'].append(r)
        if r['kind'] == 'stage': b['stage'] = r['stage'] or b['stage']; b['area_id'] = r['area_id'] or b['area_id']
        if r['kind'] == 'harvest': b.update({'stage': 'drying', 'wet_weight': r['wet_weight'], 'harvest_tag': r['tag'], 'area_id': r['area_id'] or b['area_id']})
        if r['kind'] == 'dry': b['stage'] = 'curing'
        if r['kind'] == 'cure': b.update({'stage': 'done', 'dry_weight': r['dry_weight']})
        apply(b['id']); return jr(route, [r], 201)
    if tbl == 'hx_grow_events' and m == 'PATCH':
        bd = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); v = next(x for x in T['hx_grow_events'] if x['id'] == cid); v.update(bd); apply(v['batch_id']); return jr(route, [v])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def pb(): return T['hx_plant_batches'][0]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.get_by_role('button', name='Cultivation', exact=True).count() == 0, 'no Cultivation menu on a manufacturing license')
    pg.locator('select').nth(1).select_option('lic-cul'); pg.wait_for_timeout(600)
    pg.get_by_role('button', name='Cultivation', exact=True).click(); pg.wait_for_selector('text=Start by adding your grow areas')
    for name, kind in (('Flower 1', 'indoor'), ('Dry room', 'dry')):
        pg.get_by_role('button', name='+ Grow area').click(); md = pg.locator('.md'); field(md, 'Name *').fill(name); field(md, 'Type').select_option(kind)
        if kind == 'indoor': field(md, 'Temperature / humidity / airflow limits').fill('68-80 F, 40-60% RH'); field(md, 'Irrigation / fertigation system').fill('Drip')
        md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved ' + name)
    pg.get_by_role('button', name='+ Grow area').click(); md = pg.locator('.md'); field(md, 'Name *').fill('Field A'); field(md, 'Type').select_option('outdoor')
    field(md, 'Risk assessed on (yearly)').fill(ds(TODAY)); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md .msg.err >> text=Describe the site risk assessment')
    field(md, 'Risk assessment (topography, animals, run-off, controls, toilets / handwashing)').fill('Former pasture, fenced, portable toilets'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Field A')
    pg.get_by_role('button', name='+ Plant batch').click(); md = pg.locator('.md')
    field(md, 'Cultivar / strain *').fill('Gelato'); field(md, 'Plants *').fill('50'); field(md, 'Planted on').fill(ds(TODAY - dt.timedelta(days=70)))
    check(md.locator('option', has_text='RCV-2026-010 · Gelato clones').count() == 1, 'propagation lots offered from Receiving')
    field(md, 'Lot (Receiving) *').select_option('lt-cl'); field(md, 'Grow media lot').select_option('lt-md'); field(md, 'METRC plant batch tag').fill('1A4-PB-01')
    field(md, 'Starts in area').select_option(label='Flower 1 · Indoor grow room'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Gelato')
    check(pb()['source_lot_id'] == 'lt-cl' and pb()['media_lot_id'] == 'lt-md' and pb()['area_id'], 'plant batch traced to the clone lot and media lot')
    pg.locator('tr', has_text='PB-2026-001').get_by_role('button', name='Open').click(); md = pg.locator('.md')
    with pg.expect_popup() as pop: md.get_by_role('button', name='Print label').click()
    w = pop.value; w.wait_for_load_state(); html = w.content(); check('Gelato' in html and 'Lot RCV-2026-010 Gelato clones' in html and 'Planted' in html, 'printable plant label with name, source and date'); w.close()
    md.get_by_role('button', name='Nutrients').click(); md = pg.locator('.md')
    field(md, 'Approved nutrient / amendment (Chemicals)').select_option('ch-n'); field(md, 'Amount / rate *').fill('2 mL/L'); field(md, 'Method').fill('Drip')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Nutrients / amendment recorded')
    md = pg.locator('.md').first
    md.get_by_role('button', name='Crop protection').click(); md = pg.locator('.md')
    check(md.locator('option', has_text='Neem oil · EPA 70051-2').count() == 1 and md.locator('option', has_text='Bloom').count() == 0, 'crop protection offers approved pesticides only')
    field(md, 'Approved pesticide (Chemicals) *').select_option('ch-p'); field(md, 'Rate (label) *').fill('1 oz/gal'); md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.md .msg.err >> text=re-entry')
    field(md, 'Re-entry (hours) *').fill('4'); field(md, 'Pre-harvest (days) *').fill('14'); field(md, 'Target pest / disease').fill('Spider mites')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Crop protection recorded')
    hold = ds(TODAY + dt.timedelta(days=14))
    check(pg.locator('tr', has_text='PB-2026-001').locator('.badge', has_text='Not before ' + hold).count() == 1, 'pre-harvest interval shown on the batch')
    md = pg.locator('.md').first
    md.get_by_role('button', name='Stage / move').click(); md = pg.locator('.md'); field(md, 'Stage').select_option('flowering'); md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Stage / move recorded')
    md = pg.locator('.md').first
    check(md.locator('.msg.err', has_text='no harvest before ' + hold).count() == 1, 'batch detail warns of the pre-harvest interval')
    md.get_by_role('button', name='Harvest').click(); md = pg.locator('.md')
    check(md.locator('.msg.err', has_text='earliest harvest ' + hold).count() == 1, 'harvest form blocks a harvest inside the PHI')
    md.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(200)
    md = pg.locator('.md').first
    md.locator('tr', has_text='Crop protection').get_by_role('button', name='Void').click(); vm = pg.locator('.md').last; vm.locator('textarea').fill('Applied to the wrong room'); vm.get_by_role('button', name=re.compile('^Void')).click()
    pg.wait_for_selector('.msg >> text=Voided.')
    md = pg.locator('.md').first
    md.get_by_role('button', name='Harvest').click(); md = pg.locator('.md')
    field(md, 'Wet weight (g) *').fill('12000'); field(md, 'Harvest batch tag (METRC) *').fill('1A4-HB-77'); field(md, 'Hung in (dry room)').select_option(label='Dry room · Dry room')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Harvest recorded')
    md = pg.locator('.md').first
    md.get_by_role('button', name='Drying').click(); md = pg.locator('.md'); field(md, 'Room conditions *').fill('60 F, 60% RH'); md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Drying recorded')
    md = pg.locator('.md').first
    md.get_by_role('button', name='Cured (dry weight)').click(); md = pg.locator('.md'); field(md, 'Final dry weight (g) *').fill('2600'); md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Cured (dry weight) recorded')
    check(pb()['stage'] == 'done' and pb()['wet_weight'] == 12000 and pb()['dry_weight'] == 2600 and pb()['harvest_tag'] == '1A4-HB-77', 'harvest, drying and curing complete the batch')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    pg.locator('.tabs button', has_text='Applications').click(); pg.wait_for_selector('td >> text=Bloom A+B')
    check(pg.locator('td', has_text='Neem oil').count() == 0, 'voided application not in the application log')
    pg.locator('.tabs button', has_text='Approved inputs').click(); pg.wait_for_selector('td >> text=Neem oil')
    check(pg.locator('td', has_text='70051-2').count() == 1, 'approved inputs list (nutrient plan)')
    pg.locator('.tabs button', has_text='Grow areas').click(); pg.wait_for_selector('td >> text=Field A')
    check(pg.locator('tr', has_text='Field A').locator('.badge', has_text=ds(TODAY)).count() == 1, 'outdoor site risk assessment date shown')
    pg.screenshot(path=OUT + 'cultivation.png')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Open cultivation')
    check(True, 'dashboard cultivation card')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
