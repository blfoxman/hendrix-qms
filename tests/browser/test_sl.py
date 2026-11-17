import os, re
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label, exact=False):
    pgx = md if hasattr(md, 'goto') else md.page
    sp = pgx.locator('span', has_text=re.compile('^' + re.escape(label) + ('$' if exact else '')))
    return md.locator('label.f, div.f', has=sp).locator('input,select,textarea').first
T['hx_rooms'] = [{'id': 'room-v', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'name': 'Vault', 'kind': 'vault', 'conditions': '', 'notes': '', 'active': True, 'sort': 0}]
T['hx_yield_alerts'] = [{'id': 'ya-b1-distillate', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': 'b1', 'batch_number': 'ETH-2026-009', 'batch_type': 'ethanol_extraction', 'stage': 'distillate',
                         'pct': 7.5, 'band': 'bad', 'created_at': '2026-11-16T10:00:00Z', 'updated_at': '2026-11-16T10:00:00Z', 'resolved_at': None, 'seen_by': []}]
SEEN = []
_h = handle
def handle(route, request):
    if request.url.split('?')[0].endswith('/rpc/hx_yield_alert_seen'):
        a = json.loads(request.post_data); SEEN.append(a['p_id'])
        for x in T['hx_yield_alerts']:
            if x['id'] == a['p_id']: x['seen_by'].append(ADMIN)
        return route.fulfill(status=200, content_type='application/json', body='null')
    return _h(route, request)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 1000}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    # dashboard low yield alert
    card = pg.locator('.card', has_text='Low yield')
    check(card.count() == 1 and 'ETH-2026-009' in card.inner_text() and '7.5% BAD' in card.inner_text() and 'Expected 12-24%' in card.inner_text(), 'Dashboard: low yield alert with the batch, yield and expected range')
    card.get_by_role('button', name='Seen').click(); pg.wait_for_timeout(400)
    check(SEEN == ['ya-b1-distillate'] and pg.locator('.card', has_text='Low yield').count() == 0, 'Seen hides it for this person')
    # rooms
    pg.get_by_role('button', name='Rooms', exact=True).click(); pg.wait_for_selector('td >> text=Vault')
    pg.get_by_role('button', name='+ Add room').click(); md = pg.locator('.md')
    field(md, 'Room name').fill('vault'); md.get_by_role('button', name='Save').click()
    check(md.locator('.msg.err', has_text='already a room called vault').count() == 1, 'same room name refused')
    field(md, 'Room name').fill('Freezer 2'); field(md, 'Type').select_option('freezer'); field(md, 'Storage conditions').fill('-20 °F')
    md.get_by_role('button', name='Save').click(); md.wait_for(state='detached')
    r = next((x for x in T['hx_rooms'] if x['name'] == 'Freezer 2'), None)
    check(r is not None and r['kind'] == 'freezer' and r['conditions'] == '-20 °F' and r['license_id'] == 'lic-mo', 'room saved for the license')
    pg.wait_for_selector('td >> text=Freezer 2')
    check(pg.locator('tr', has_text='Freezer 2').locator('td', has_text='Freezer').count() >= 1, 'room listed')
    # solventless batch
    pg.get_by_role('button', name='Batch Tracker', exact=True).click()
    tab = pg.locator('.tabs button', has_text='Solventless')
    check(tab.count() == 1, 'Batch Tracker has a Solventless tab')
    tab.click(); pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    check(md.locator('span', has_text=re.compile('^SKU')).count() == 0, 'solventless has no SKU')
    secs = [x.strip() for x in md.locator('.secth').all_inner_texts()]
    check([x.upper() for x in secs[:5]] == ['FRESH FROZEN', 'HASH', 'ROSIN', 'TESTING', 'STORAGE ROOM'] or [x.upper() for x in secs[1:6]] == ['FRESH FROZEN', 'HASH', 'ROSIN', 'TESTING', 'STORAGE ROOM'], 'sections: Fresh Frozen, Hash, Rosin, Testing, Storage Room: ' + str(secs))
    field(md, 'Batch / Lot Number').fill('SL-001')
    md.get_by_role('button', name='+ Add Fresh Frozen Tag').click(); md.get_by_role('button', name='+ Add Fresh Frozen Tag').click()
    rows = md.locator('.li')
    check(rows.nth(0).locator('input').nth(0).get_attribute('placeholder') == 'Fresh Frozen METRC Tag #', 'fresh frozen tag placeholder')
    rows.nth(0).locator('input').nth(0).fill('1A4000001'); rows.nth(0).locator('input').nth(1).fill('10000'); rows.nth(1).locator('input').nth(0).fill('1A4000002'); rows.nth(1).locator('input').nth(1).fill('5000')
    check(md.locator('.autov', has_text='15000').count() == 1, 'total fresh frozen weight adds up (15000)')
    check(md.locator('text=900 (6% of Total Fresh Frozen Weight)').count() == 1 and md.locator('text=600 (4% of Total Fresh Frozen Weight)').count() == 1, 'hash and rosin suggestions')
    field(md, 'Hash METRC Tag').fill('1A4000010')
    for g, band in (('1050', 'VERY GOOD'), ('825', 'GOOD'), ('600', 'BAD'), ('300', 'VERY BAD'), ('1500', 'OUT OF RANGE')):
        field(md, 'Total Hash Produced').fill(g)
        check(md.locator('.chkp', has_text='g of 15000 g)').filter(has_text=band).count() >= 1, 'hash %s g of 15000 g = %s' % (g, band))
    field(md, 'Total Hash Produced').fill('900')
    check(md.locator('.chkp', has_text='Actual yield: 6%').count() == 1, 'hash yield shown (6%)')
    field(md, 'Total Hash Used').fill('900')
    for g, band in (('750', 'VERY GOOD'), ('525', 'GOOD'), ('375', 'BAD'), ('180', 'VERY BAD')):
        field(md, 'Total Rosin Produced').fill(g)
        check(md.locator('.chkp', has_text='rosin-to-fresh-frozen').filter(has_text=band).count() >= 1, 'rosin %s g of 15000 g = %s' % (g, band))
    field(md, 'Total Rosin Produced').fill('675')
    check(md.locator('.chkp', has_text='press return 75% of hash used').count() == 1, 'rosin panel shows press return of hash used')
    field(md, 'Rosin METRC Tag').fill('1A4000020')
    check('Not submitted yet' in md.inner_text(), 'Testing section explains Submit for testing')
    sel = field(md, 'Storage Room')
    opts = sel.locator('option').all_inner_texts()
    check('Freezer 2 (-20 °F)' in opts and 'Vault' in opts, 'Storage Room picks from the rooms: ' + str(opts))
    sel.select_option('Freezer 2')
    check('Washing' in field(md, 'Status').locator('option').all_inner_texts() and 'Labels' in field(md, 'Status').locator('option').all_inner_texts(), 'status list for solventless')
    md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=SL-001')
    bt = next(x for x in T['hx_batches'] if x['batch_number'] == 'SL-001')
    d = bt['data']
    check(bt['batch_type'] == 'solventless' and not bt.get('sku_id') and str(d['total_biomass_used']) == '15000' and str(d['hash_yield_pct']) == '6' and str(d['rosin_yield_pct']) == '4.5' and str(d['press_yield_pct']) == '75' and d['storage_room'] == 'Freezer 2', 'batch saved with yields and storage room')
    c = pg.locator('.card', has_text='SL-001')
    check('2 fresh frozen tag(s), 15000 g · stored in Freezer 2' in c.inner_text(), 'card: fresh frozen and storage room')
    check(c.get_by_role('button', name='Submit for testing').count() == 1, 'Submit for testing on the card (rosin tag)')
    c.get_by_role('button', name='Submit for testing').click(); pg.wait_for_timeout(600)
    t = [x for x in T['hx_tests'] if x.get('batch_id') == bt['id']]
    check(len(t) == 1 and t[0]['tag'] == '1A4000020', 'rosin tag sent to testing')
    pg.screenshot(path=OUT + 'solventless.png', full_page=True)
    b.close()
check(not [e for e in errors if e.startswith('JS')], 'no JS errors')
print('errors:', errors)
