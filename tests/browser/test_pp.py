import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
T['hx_skus'] += [{'id': 'k-pr', 'state_id': 'st-mo', 'product_type': 'pre_rolls', 'name': 'Infused 1g', 'spec': {}, 'license_ids': [], 'active': True, 'sort': 0},
                 {'id': 'k-gm', 'state_id': 'st-mo', 'product_type': 'gummies', 'name': 'Gummies 10pk', 'spec': {'grams_per_gummy': 4.6}, 'license_ids': [], 'active': True, 'sort': 0}]
T['hx_flavors'] += [{'id': 'f1', 'state_id': 'st-mo', 'sku_id': 'k-pr', 'name': 'Blue Dream', 'active': True, 'sort': 0}, {'id': 'f2', 'state_id': 'st-mo', 'sku_id': 'k-pr', 'name': 'Mango', 'active': True, 'sort': 1},
                    {'id': 'f3', 'state_id': 'st-mo', 'sku_id': 'k-pr', 'name': 'Grape', 'active': True, 'sort': 2}, {'id': 'g1', 'state_id': 'st-mo', 'sku_id': 'k-gm', 'name': 'Watermelon', 'active': True, 'sort': 0}]
RECIPES = {'k-pr': [{'flavor_id': None, 'name': 'Infused 1g base', 'batch_size': '100', 'raw_materials': [{'name': 'Flower', 'qty': '55', 'unit': 'g'}, {'name': 'THCA', 'qty': '10', 'unit': 'g'}, {'name': 'Terpene', 'qty': '2', 'unit': 'g'}]},
                   {'flavor_id': 'f1', 'name': 'Blue Dream', 'batch_size': '100', 'raw_materials': [{'name': 'Flower', 'qty': '50', 'unit': 'g'}, {'name': 'Terpene - Blue Dream', 'qty': '3', 'unit': 'g'}]}], 'k-gm': []}
T['hx_lots'] = [{'id': 'l1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'item': 'Flower', 'unit': 'kg', 'quantity': 1, 'qty_used': 0, 'status': 'accepted'},
                {'id': 'l2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'item': 'THCA isolate', 'unit': 'g', 'quantity': 500, 'qty_used': 100, 'status': 'accepted'}]
T['hx_production_plans'] = []; SEQ = [0]; AIQ = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; path = urllib.parse.urlparse(u).path
    if path.endswith('/rpc/hx_planner_recipes'): return jr(route, RECIPES.get(json.loads(request.post_data)['p_sku'], []))
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AIQ.append(b)
        return jr(route, {'content': [{'type': 'text', 'text': json.dumps({'flavors': {'Watermelon': [{'name': 'Distillate', 'qty': '460', 'unit': 'g'}, {'name': 'Gummy base', 'qty': '45540', 'unit': 'g'}]}})}]})
    tbl = path.split('/')[-1]
    if tbl == 'hx_production_plans' and m == 'POST':
        r = json.loads(request.post_data); SEQ[0] += 1; r.update({'number': 'PP-2026-%03d' % SEQ[0], 'status': 'planned', 'created_by': 'Sam', 'created_at': NOW}); T['hx_production_plans'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_production_plans' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_production_plans'] if x['id'] == cid)
        if b.get('status') == 'cancelled' and not b.get('close_note'): return jr(route, {'message': 'A reason is required'}, 400)
        r.update(b); return jr(route, [r])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def fcard(pg, fl): return pg.locator('.card', has=pg.locator('b', has_text=re.compile('^' + re.escape(fl) + '$'))).first
def ing(card, name): return card.locator('.row', has=card.page.locator('span', has_text=re.compile('^' + re.escape(name) + '$'))).locator('b').first.inner_text()
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.wait_for_selector('.card.gold >> text=Production plans')
    check(pg.locator('.card.gold', has_text='Production plans').locator('text=Nothing planned').count() == 1 and pg.locator('.badge.off', has_text='Production Planner').count() == 0, 'dashboard card; planner off the coming-soon list')
    pg.get_by_role('button', name='Production Planner').click(); pg.wait_for_selector('text=Calculate ingredients')
    field(pg, 'Product type').select_option('pre_rolls'); field(pg, 'SKU').select_option('k-pr')
    pg.get_by_role('link', name='Select all').click(); pg.wait_for_selector('text=Exact amounts from saved formulations (base recipe covers every flavor)')
    field(pg, 'Units per flavor').fill('1000'); field(pg, 'Additional instructions (optional)').fill('5% waste buffer')
    pg.get_by_role('button', name='Calculate ingredients').click(); pg.wait_for_selector('text=Grand total')
    bd, mg = fcard(pg, 'Blue Dream'), fcard(pg, 'Mango')
    check(ing(bd, 'Flower') == '525 g' and ing(bd, 'Terpene - Blue Dream') == '31.5 g' and bd.locator('.badge', has_text='Formulation').count() == 1, 'Blue Dream from its own formulation, scaled with the 5% buffer')
    check(ing(mg, 'Flower') == '577.5 g' and ing(mg, 'THCA') == '105 g' and ing(mg, 'Terpene - Mango') == '21 g' and mg.locator('.badge', has_text='Base recipe').count() == 1, 'Mango from the base recipe with its terpene named')
    gt = pg.locator('.card.gold', has_text='Grand total'); print(gt.inner_text().replace('\n',' | '))
    check(gt.locator('text=1680 g').count() == 1 and gt.locator('text=short 1000 g').count() == 1 and gt.locator('text=on hand 400 g').count() == 1 and gt.locator('.badge', has_text='1 short in inventory').count() == 1, 'grand total checked against accepted inventory (kg converted)')
    check(len(AIQ) == 0 and mg.locator('input').count() == 7, 'no AI call when recipes cover everything; pre-roll tracking blanks')
    with pg.expect_download() as dl: pg.get_by_role('button', name='Worksheets PDF (3)').click()
    d = dl.value; pth = d.path(); check(open(pth, 'rb').read(5) == b'%PDF-' and d.suggested_filename.endswith('_worksheets.pdf'), 'worksheets PDF (one page per flavor)')
    pg.get_by_role('button', name='Save plan').click(); pg.wait_for_selector('.msg >> text=Saved plan PP-2026-001.'); pg.wait_for_selector('text=← All plans')
    p0 = T['hx_production_plans'][0]; check(p0['units_per_flavor'] == 1000 and len(p0['lines']) == 3 and p0['instructions'] == '5% waste buffer', 'plan saved with its lines')
    pg.screenshot(path=OUT + 'planner.png', full_page=True)
    fcard(pg, 'Mango').get_by_role('button', name='Start batch').click(); pg.wait_for_selector('.md')
    md = pg.locator('.md'); check(field(md, 'SKU').input_value() == 'k-pr' and field(md, 'Flavor').input_value() == 'f2', 'Start batch opens the Batch Tracker form with the SKU and flavor')
    check(p0['status'] == 'in_progress', 'plan moves to In production')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    pg.get_by_role('button', name='Production Planner').click(); pg.wait_for_selector('text=Calculate ingredients')
    field(pg, 'Product type').select_option('gummies'); field(pg, 'SKU').select_option('k-gm'); pg.wait_for_selector('text=No formulation for this SKU yet')
    pg.get_by_role('button', name='Watermelon').click(); field(pg, 'Units per flavor').fill('1000'); pg.get_by_role('button', name='Calculate ingredients').click(); pg.wait_for_selector('text=Grand total')
    wm = fcard(pg, 'Watermelon'); check(len(AIQ) == 1 and AIQ[0]['module'] == 'planner' and ing(wm, 'Distillate') == '460 g' and wm.locator('.badge', has_text='AI estimate').count() == 1, 'flavor without a recipe estimated by the AI (module planner)')
    check('Gummies 10pk' in AIQ[0]['messages'][0]['content'] and 'grams_per_gummy' in AIQ[0]['messages'][0]['content'], 'AI gets the SKU settings')
    pg.locator('.tabs').get_by_role('button', name=re.compile('^Plans')).click(); pg.wait_for_selector('td >> text=PP-2026-001')
    check(pg.locator('tr', has_text='PP-2026-001').locator('.badge', has_text='In production').count() == 1, 'plans list shows the status')
    pg.locator('tr', has_text='PP-2026-001').get_by_role('button', name='Open').click(); pg.get_by_role('button', name='Cancel plan').click(); md = pg.locator('.md')
    md.locator('textarea').fill('Order cancelled by the dispensary'); md.get_by_role('button', name='Cancel plan').click(); pg.wait_for_selector('.msg >> text=Cancelled PP-2026-001.')
    check(p0['status'] == 'cancelled' and p0['close_note'].startswith('Order cancelled'), 'plan cancelled with a reason')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Production plans')
    check(pg.locator('.badge.off', has_text='Production Planner').count() == 0, 'planner not on the coming-next list')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
