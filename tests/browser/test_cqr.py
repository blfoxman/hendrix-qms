import re, base64
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFklEQVR42mP8z8DwnwEJMDGgAQYGBgB2kAQBhXhYswAAAABJRU5ErkJggg==')
JPG1 = 'data:image/jpeg;base64,' + base64.b64encode(PNG).decode()
T['hx_complaints'] = [{'id': 'cq1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'CMP-2026-001', 'title': 'Green Leaf KC: Leaking / damage - 2G AIO', 'type': 'dispensary', 'priority': 'minor', 'status': 'open',
                       'received_on': '2026-11-18', 'channel': 'QR form', 'complainant': 'Ana', 'complainant_contact': 'ana@gl.com', 'customer': 'Green Leaf KC', 'category': 'Leaking / damage', 'product': '2G AIO', 'lot_number': '', 'tag': '1A4000000000000000005801', 'tag_check': 'verified', 'tag_check_note': 'Batch CT-T58 · shipped 2026-11-02 to Green Leaf (SHP-2026-004)',
                       'description': 'Carts leak.', 'attachments': [], 'qr_photos': [JPG1], 'created_by': 'QR form (Ana, Green Leaf KC)', 'created_at': '2026-11-18T10:00:00Z', 'investigator': '', 'due_date': None, 'investigation': '', 'root_cause': '',
                       'resolution': '', 'corrective_action': '', 'response': '', 'responded_on': None, 'regulator_reported_on': None, 'deviation_id': None, 'deviation_number': '', 'closed_by': '', 'closed_at': None, 'cancel_reason': '', 'rating': None, 'batch_id': None}]
CALLS = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    if request.url.endswith('/rest/v1/rpc/hx_complaint_tag_check'):
        t = json.loads(request.post_data)['p_tag']
        return jr(route, {'found': True, 'product': '2G AIO · Blue Dream', 'batch_number': 'CT-T58'} if t == '1A4000000000000000005801' else {'found': False})
    if request.url.endswith('/rest/v1/rpc/hx_complaint_qr'):
        b = json.loads(request.post_data); CALLS.append(b)
        if len(b['p']['description'].strip()) < 10: return jr(route, {'message': 'Describe the problem (at least a sentence).'}, 400)
        return jr(route, 'CMP-2026-007')
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('if(!/kiosk=/.test(location.search)){localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");}' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Complaints', exact=True).click(); pg.wait_for_selector('text=CMP-2026-001')
    pg.get_by_role('button', name='Store QR code').click(); pg.wait_for_selector('text=Store complaint QR')
    link = pg.locator('.card.gold', has_text='Store complaint QR').locator('input').input_value()
    check('kiosk=complaint' in link and 'state=st-mo' in link and 'lic=lic-mo' in link, 'store QR link carries the license')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print QR sign').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Product complaint' in html and 'No account needed' in html, 'printable QR sign for stores'); w.close()
    check(pg.locator('.card', has_text='CMP-2026-001').locator('.badge', has_text='Tag verified').count() == 1, 'complaint list shows Tag verified')
    pg.locator('text=CMP-2026-001').click(); pg.wait_for_selector('.md >> text=Photos from the store')
    check(pg.locator('.md .msg', has_text='METRC tag verified').locator('text=/shipped 2026-11-02 to Green Leaf/').count() == 1, 'complaint shows the METRC tag check (batch, shipped to whom)')
    check(pg.locator('.md img[alt="Store photo 1"]').count() == 1 and pg.locator('.md').locator('text=QR form').count() >= 1, 'complaint shows the store photos and that it came from the QR form')
    # the store's phone: no login
    k = ctx.new_page(); k.on('pageerror', lambda e: errors.append('JS kiosk: ' + str(e)))
    k.goto(BASE + '?kiosk=complaint&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Product complaint')
    check(k.locator('text=No account needed').count() == 1 and k.locator('text=Quality standard').count() == 0, 'store form opens without signing in')
    k.get_by_role('button', name='Send complaint').click(); k.wait_for_selector('.msg.err >> text=Enter the store name')
    fld = lambda l: k.locator('label.f', has=k.locator('span', has_text=l)).locator('input,textarea,select').first
    fld('Store (dispensary)').fill('Green Leaf KC'); fld('Your name').fill('Ana'); fld('Phone or email').fill('ana@gl.com')
    fld('Describe the problem').fill('Customer felt dizzy and the cart leaked.'); fld('Product').fill('Some cart')
    k.get_by_role('button', name='Send complaint').click(); k.wait_for_selector('.msg.err >> text=Enter the METRC package tag')
    fld('METRC package tag').fill('1A40 12'); k.get_by_role('button', name='Send complaint').click(); k.wait_for_selector('.msg.err >> text=24 characters and starts with 1A')
    fld('METRC package tag').fill('1a40 0000 0000 0000 0000 9999'); k.wait_for_selector('text=We cannot find this tag in our records')
    k.get_by_role('button', name='Send complaint').click(); k.wait_for_selector('.msg.err >> text=tick "The tag is correct"')
    check(len(CALLS) == 0, 'an unknown tag is not sent until the store confirms it')
    k.locator('label.ck', has_text='The tag is correct').locator('input').check()
    fld('Product').fill(''); fld('METRC package tag').fill('1A4000000000000000005801'); k.wait_for_selector('text=This is our product: 2G AIO · Blue Dream (batch CT-T58)')
    check(fld('Product').input_value() == '2G AIO · Blue Dream', 'our tag: the product is filled from the batch')
    fld('What is wrong?').select_option('Adverse health effect')
    check(k.locator('input[aria-label="sick or hurt"]').is_checked(), 'choosing "Adverse health effect" ticks "someone got sick or hurt"')
    fld('Describe the problem').fill('short'); k.get_by_role('button', name='Send complaint').click(); k.wait_for_selector('.msg.err >> text=Describe the problem')
    k.screenshot(path=OUT + 'store_complaint_form.png', full_page=True)
    k.locator('label', has_text='+ Photo').locator('input[type=file]').set_input_files({'name': 'cart.png', 'mimeType': 'image/png', 'buffer': PNG}); k.wait_for_selector('img[alt="Photo 1"]')
    fld('Describe the problem').fill('Customer felt dizzy and the cart leaked.'); k.get_by_role('button', name='Send complaint').click(); k.wait_for_selector('text=We received your complaint')
    p = CALLS[-1]
    check(p['p_state'] == 'st-mo' and p['p_lic'] == 'lic-mo' and p['p']['store'] == 'Green Leaf KC' and p['p']['health'] is True and p['p']['tag'] == '1A4000000000000000005801' and p['p']['photos'][0].startswith('data:image/jpeg;base64,'), 'complaint sent with store, tag, health flag and a shrunk JPEG photo')
    check(k.locator('b', has_text='CMP-2026-007').count() == 1, 'store sees its complaint number')
    k.screenshot(path=OUT + 'store_complaint_done.png')
    k.get_by_role('button', name='File another complaint').click(); k.wait_for_selector('text=Send complaint')
    check(fld('Store (dispensary)').input_value() == 'Green Leaf KC' and fld('Product').input_value() == '', 'another complaint keeps the store and contact, clears the product')
    check(fld('METRC package tag').input_value() == '' and k.locator('text=This is our product').count() == 0, 'another complaint clears the tag and its check')
    k.goto(BASE + '?kiosk=complaint&state=st-mi&lic=lic-mo'); k.wait_for_selector('text=not linked to an active license')
    check(True, 'a QR code with the wrong license is refused')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
