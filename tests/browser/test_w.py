import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f', has=pgx.locator('span', has_text=label)).locator('input,select,textarea').first
T['hx_log_lists'].append({'id':'old1','state_id':'st-mo','license_id':'lic-mo','list_key':'waste.cameras','name':'Legacy Cam','spec':{},'sort':0,'active':True})
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_logtab","waste");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.get_by_role('button', name='Facility Logs').click(); pg.wait_for_selector('h2 >> text=Waste Destruction Log')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    check(field(md, 'Camera #1').locator('option', has_text='Legacy Cam').count() == 1, 'old shared list still feeds camera #1')
    check(field(md, 'Camera #3').evaluate('e=>e.tagName') == 'INPUT' and field(md, 'Location of Disposal').evaluate('e=>e.tagName') == 'INPUT', 'empty lists = type-in')
    md.get_by_role('button', name='Cancel').click()
    pg.get_by_role('button', name='Manage lists').click()
    titles = pg.locator('.md .card h3').all_inner_texts()
    check(all(any(t.startswith('Camera #%d' % i) for t in titles) for i in (1, 2, 3, 4)) and 'Locations of Disposal' in titles and any('Old shared' in t for t in titles), 'lists: cameras 1-4, disposal, old list shown')
    for title, name in [('Camera #1 names', 'Waste 1'), ('Camera #3 names', 'Waste 3'), ('Camera #4 names', 'Waste 4'), ('Locations of Disposal', 'GFL Landfill, Pevely MO')]:
        sec = pg.locator('.md .card', has=pg.locator('h3', has_text=title)); sec.locator('input').first.fill(name); sec.get_by_role('button', name='+ Add').click(); pg.wait_for_selector('.md td >> text=' + name)
    pg.mouse.click(5, 5)
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    opts1 = field(md, 'Camera #1').locator('option').all_inner_texts()
    check('Waste 1' in opts1 and 'Legacy Cam' not in opts1, 'camera #1 uses its own list once set')
    check(field(md, 'Camera #2').locator('option', has_text='Legacy Cam').count() == 1, 'camera #2 still on old list')
    check(field(md, 'Camera #3').locator('option', has_text='Waste 3').count() == 1 and field(md, 'Camera #4').locator('option', has_text='Waste 4').count() == 1, 'cameras 3 and 4 have lists')
    field(md, 'Agent / Badge ID').fill('A1'); field(md, 'Category').fill('Flower'); field(md, 'Track-and-Trace').fill('1A4'); field(md, 'Quantity of Waste').fill('5')
    field(md, 'Method Used').fill('Ground'); field(md, 'Supervisor Name').fill('Sup')
    field(md, 'Camera #1').select_option('Waste 1'); field(md, 'Camera #3').select_option('Waste 3'); field(md, 'Camera #4').select_option('Waste 4')
    field(md, 'Location of Disposal').select_option('GFL Landfill, Pevely MO')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_selector('td >> text=Flower')
    d = T['hx_facility_log'][-1]['data']
    check(d['camera_1'] == 'Waste 1' and d['camera_3'] == 'Waste 3' and d['camera_4'] == 'Waste 4' and d['disposal_location'] == 'GFL Landfill, Pevely MO', 'saved cameras 1/3/4 + disposal location')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
