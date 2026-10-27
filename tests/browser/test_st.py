import re, datetime as dt, struct, zlib
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
NOW = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
T['hx_license_settings'] = []
T['hx_risks'] = [{'id': 'rk1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RK-001', 'title': 'Residual solvent', 'category': 'product_safety', 'hazard': 'Solvent', 'root_cause': 'Purge', 'owner': 'Sam', 'status': 'open', 'likelihood': 2, 'severity': 4, 'score': 8,
                  'residual_likelihood': None, 'residual_severity': None, 'controls': '', 'immediate_action': '', 'permanent_action': '', 'target_date': None, 'review_every_days': 365, 'last_reviewed': NOW[:10], 'next_review': '2027-10-24', 'created_at': NOW}]
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; path = urllib.parse.urlparse(u).path; tbl = path.split('/')[-1]
    if tbl == 'hx_license_settings' and m == 'POST':
        r = json.loads(request.post_data); T['hx_license_settings'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_license_settings' and m == 'PATCH':
        b = json.loads(request.post_data); r = T['hx_license_settings'][0]; r.update(b); return jr(route, [r])
    if path.endswith('/rpc/hx_kiosk_check'):
        s = T['hx_license_settings'][0] if T['hx_license_settings'] else {}
        return jr(route, {'id': 'lic-mo', 'name': 'Black Fox', 'license_number': 'MAN000109', 'state_id': 'st-mo', 'state': 'Missouri', 'display_name': s.get('dba') or 'Black Fox', 'logo': s.get('logo'), 'breaks': [s.get('break1_min', 15), s.get('break2_min', 30), s.get('break3_min', 15)]})
    if path.endswith('/rpc/hx_badge_roster'):
        return jr(route, [{'id': ADMIN, 'name': 'Sam', 'email': 's@x', 'has_badge': True, 'badge_no': '4001', 'title': 'Owner', 'photo': None, 'zoom': 1, 'pos_x': 0, 'pos_y': 0, 'code': 'ABCDEF123456'}])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def png(w, h):
    raw = b''.join(b'\x00' + bytes([212, 175, 55]) * w for _ in range(h))
    def ch(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
open(OUT + 'logo.png', 'wb').write(png(300, 100))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('.badge.off', has_text='Settings').count() == 0, 'Settings off the coming-soon list')
    pg.get_by_role('button', name='Settings', exact=True).click(); pg.wait_for_selector('text=Business details on printouts')
    check(pg.locator('text=MAN000109').count() >= 1, 'license details shown')
    field(pg, 'Legal name').fill('Black Fox Manufacturing LLC'); field(pg, 'Doing business as').fill('Black Fox'); field(pg, 'Address').fill('100 Main St\nSt. Louis, MO')
    field(pg, 'Phone').fill('314-555-0100'); field(pg, 'Footer on printouts').fill('Controlled copy - do not distribute')
    pg.locator('input[type=file]').set_input_files(OUT + 'logo.png'); pg.wait_for_selector('img[alt=logo]')
    check(pg.locator('text=Black Fox Manufacturing LLC').count() >= 1 and pg.locator('text=Controlled copy - do not distribute').count() >= 1, 'printout header preview')
    pg.get_by_role('button', name='Time clock', exact=True).click(); field(pg, '1st break (min)').fill('10')
    pg.get_by_role('button', name='Facility logs', exact=True).click(); check(pg.locator('.row', has_text='Sanitation Log').last.locator('text=hours (default 48)').count() == 1, 'sanitation cycle is set in hours'); pg.locator('.row', has_text='Sanitation Log').last.locator('input').fill('12')
    pg.get_by_role('button', name='Review cycles').click(); pg.locator('.row', has_text='High (10-14)').last.locator('input').fill('120')
    pg.get_by_role('button', name='Save settings').click(); pg.wait_for_selector('.msg >> text=Settings saved for Black Fox.')
    s0 = T['hx_license_settings'][0]
    check(s0['break1_min'] == 10 and s0['log_due'] == {'sanitation_h': 12} and s0['review_days'] == {'high': 120} and s0['logo'].startswith('data:image/png') and s0['address'].startswith('100 Main'), 'settings saved for the license')
    pg.get_by_role('button', name='Everything else').click(); check(pg.locator('.card b', has_text='Products').count() == 1 and pg.locator('.card b', has_text='Roles (access templates)').count() == 1, 'directory of where everything else is set')
    pg.get_by_role('button', name='Time Clock and Badges').click(); pg.wait_for_selector('text=three breaks (10 / 30 / 15 min)')
    check(True, 'time clock uses the saved break limits')
    pg.locator('.tabs').get_by_role('button', name='Badges').click(); pg.locator('div', has_text=re.compile('^Sam')).last.click(); pg.wait_for_selector('.hxbadge')
    check(pg.locator('.hxbadge img[src^="data:image/png"]').count() >= 1 and pg.locator('.hxbadge', has_text='BLACK FOX').count() == 1, 'badge shows the company logo')
    pg.get_by_role('button', name='Risk Register').click(); pg.wait_for_selector('text=Residual solvent')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print register').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Black Fox Manufacturing LLC' in html and 'data:image/png' in html and 'Controlled copy - do not distribute' in html and '314-555-0100' in html, 'every printout carries the business header and footer'); w.close()
    kp = ctx.new_page(); kp.on('pageerror', lambda e: errors.append('KIOSK JS: ' + str(e))); kp.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); kp.wait_for_selector('text=Scan your badge')
    check(kp.locator('img[src^="data:image/png"]').count() == 1 and kp.locator('text=Break limits: 10 / 30 / 15 min').count() == 1, 'kiosk shows the logo and the break limits'); kp.close()
    pg.screenshot(path=OUT + 'settings_risk.png')
    # view only
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'settings': 'read', 'risks': 'read'}
    pg.reload(); pg.wait_for_selector('text=States and Licenses'); pg.get_by_role('button', name='Settings', exact=True).click(); pg.wait_for_selector('text=View only: Full access on Settings')
    check(pg.get_by_role('button', name='Save settings').count() == 0 and field(pg, 'Legal name').is_disabled(), 'view-only access cannot change settings')
    pg.get_by_role('button', name='General', exact=True).click(); pg.screenshot(path=OUT + 'settings.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
