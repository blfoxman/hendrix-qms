# Sidebar groups: modules grouped by job, collapsible, the current page's group opens, Find a module, remembered per device
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    shut = json.dumps({'production': 1, 'inventory': 1, 'facility': 1, 'quality': 1, 'docs': 1, 'mgmt': 1, 'admin': 1, 'other': 1})
    ctx.add_init_script('if(!sessionStorage.getItem("s1")){sessionStorage.setItem("s1","1");localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_side_shut",%s);}' % (json.dumps(json.dumps(sess)), json.dumps(shut)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    nav = pg.locator('.side .nav')
    heads = nav.locator('button.gbtn').all_inner_texts()
    check([re.sub(r'[\s›\d]+', ' ', h).strip() for h in heads][:5] == ['PRODUCTION', 'INVENTORY AND SHIPPING', 'FACILITY', 'QUALITY', 'SOPS AND TRAINING'], 'groups in order: ' + ' | '.join(h.replace('\n', ' ') for h in heads))
    check(nav.get_by_role('button', name='Dashboard').is_visible() and nav.get_by_role('button', name='My Tasks').is_visible(), 'Dashboard and My Tasks always shown')
    check(not nav.get_by_role('button', name='Batch Tracker', exact=True).is_visible(), 'a closed group hides its modules')
    nav.locator('button.gbtn', has_text='Production').click()
    check(nav.get_by_role('button', name='Batch Tracker', exact=True).is_visible() and nav.locator('button.gbtn', has_text='Production').get_attribute('aria-expanded') == 'true', 'clicking the header opens the group')
    nav.get_by_role('button', name='Batch Tracker', exact=True).click()
    # Find a module: jumps across groups; the page's group opens
    nav.locator('input.nfind').fill('sop'); 
    check(nav.get_by_role('button', name='SOPs', exact=True).is_visible() and nav.locator('button.gbtn').count() == 0, 'Find a module lists matches from every group')
    nav.locator('input.nfind').press('Enter'); pg.wait_for_selector('h1:has-text("SOPs")')
    check(nav.locator('input.nfind').input_value() == '' and nav.locator('button.gbtn', has_text='SOPs and training').get_attribute('aria-expanded') == 'true', 'Enter opens the first match; its group opens')
    saved = json.loads(pg.evaluate('localStorage.getItem("hx_side_shut")'))
    check(saved.get('production') == 0 and saved.get('docs') == 0 and saved.get('quality') == 1, 'open / closed groups remembered on this device')
    pg.reload(); pg.wait_for_selector('text=Dashboard')
    pg.wait_for_timeout(300); pg.locator('.side').screenshot(path=OUT + 'sidebar_groups.png')
    check(nav.get_by_role('button', name='Batch Tracker', exact=True).is_visible() and not nav.get_by_role('button', name='Complaints', exact=True).is_visible(), 'after a reload the same groups are open')
    every = set(re.findall(r"\['([a-z0-9]+)','", HTML.split('const SIDE_GROUPS=[')[1].split('];')[0]))
    mods = set(re.findall(r"can\('([a-z]+)',1\)&&\['([a-z]+)'", HTML)) 
    check(all(m[1] in HTML.split('const SIDE_GROUPS=[')[1].split('];')[0] for m in mods), 'every module has a group')
    # phone width: one scrolling row, no group headers
    pg.set_viewport_size({'width': 400, 'height': 800}); pg.wait_for_timeout(200)
    check(not nav.locator('button.gbtn').first.is_visible() and nav.get_by_role('button', name='Complaints', exact=True).is_visible(), 'on a phone all modules are in the scrolling bar, no headers')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
