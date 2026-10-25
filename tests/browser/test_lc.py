import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today().isoformat(); NOW = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
T['hx_batches'] += [{'id': 'be1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'ethanol_extraction', 'batch_number': 'ETH-501', 'sku_id': None, 'sku': '', 'flavor_id': None, 'flavor': '', 'status': 'In Progress', 'data': {'date': TODAY}, 'attachments': [], 'performed_by': 'Sam', 'created_at': NOW, 'updated_at': NOW, 'voided': False},
                    {'id': 'be2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_type': 'ethanol_extraction', 'batch_number': 'ETH-502', 'sku_id': None, 'sku': '', 'flavor_id': None, 'flavor': '', 'status': 'In Progress', 'data': {'date': TODAY}, 'attachments': [], 'performed_by': 'Sam', 'created_at': NOW, 'updated_at': NOW, 'voided': False}]
T['hx_equipment'] = [{'id': 'q1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'EQ-001', 'name': 'Rotovap', 'category': 'Extraction', 'location': '', 'status': 'in_service', 'cal_required': False, 'cal_due': None},
                     {'id': 'q2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'EQ-002', 'name': 'Bench scale', 'category': 'Scale / balance', 'location': '', 'status': 'in_service', 'cal_required': True, 'cal_due': '2026-01-01'}]
T['hx_line_clearances'] = []; T['hx_rework'] = []
SEQ = {'LC': 0, 'RW': 0}
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; m = request.method; tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_line_clearances' and m == 'POST':
        r = json.loads(request.post_data)
        bad = [e for e in T['hx_equipment'] if e['id'] in r['equipment_ids'] and (e['status'] != 'in_service' or (e['cal_required'] and (not e['cal_due'] or e['cal_due'] < TODAY)))]
        if r['result'] == 'cleared' and (bad or any(v['r'] == 'fail' and not v['fixed'] for v in r['checks'].values())): return jr(route, {'message': 'The line cannot be cleared'}, 400)
        SEQ['LC'] += 1; r.update({'number': 'LC-2026-%03d' % SEQ['LC'], 'checked_at': NOW, 'recorded_by': 'Sam', 'voided': False}); T['hx_line_clearances'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_rework' and m == 'POST':
        r = json.loads(request.post_data); SEQ['RW'] += 1; r.update({'number': 'RW-2026-%03d' % SEQ['RW'], 'status': 'identified', 'inspection_result': '', 'created_at': NOW}); T['hx_rework'].append(r); return jr(route, [r], 201)
    if tbl == 'hx_rework' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); r = next(x for x in T['hx_rework'] if x['id'] == cid)
        if b.get('status') == 'used' and b.get('target_expires') and r.get('expires_on') and r['expires_on'] < b['target_expires']: return jr(route, {'message': 'The rework expires before the finished product'}, 400)
        if b.get('status') == 'approved': b['approved_by'] = 'Sam'
        r.update(b); return jr(route, [r])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def item(md, text): return md.locator('div.row', has=md.page.locator('span', has_text=text)).last
def card(pg, num): return pg.locator('.card', has=pg.locator('b', has_text=re.compile('^' + num + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_btype","ethanol_extraction");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('.card.gold', has_text='Line clearance').locator('text=2 batches not cleared').count() == 1, 'dashboard: 2 batches without a line clearance')
    pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('text=ETH-501')
    check(card(pg, 'ETH-501').locator('.badge', has_text='No line clearance').count() == 1, 'batch card shows no line clearance')
    card(pg, 'ETH-501').get_by_role('button', name='Line clearance').click(); md = pg.locator('.md')
    check(md.locator('text=Gas detection, fire and life safety').count() == 1, 'extraction batch: gas detection / fire safety checks added')
    md.locator('label.ck', has_text='EQ-002 Bench scale').locator('input').check(); md.locator('label.ck', has_text='EQ-001 Rotovap').locator('input').check()
    check(md.locator('label.ck', has_text='EQ-002').locator('.badge', has_text='calibration out of date').count() == 1, 'equipment out of calibration flagged')
    rows = md.locator('div.card div.row')
    for i in range(rows.count()): rows.nth(i).get_by_role('button', name='Pass').click()
    check(md.get_by_role('button', name='Line cleared').is_disabled() and md.locator('.msg.err', has_text='EQ-002 Bench scale calibration out of date').count() == 1, 'cannot clear with equipment out of calibration')
    md.locator('label.ck', has_text='EQ-002 Bench scale').locator('input').uncheck()
    item(md, 'Tools and utensils counted').get_by_role('button', name='Fail').click()
    check(md.get_by_role('button', name='Line cleared').is_disabled(), 'cannot clear with an uncorrected failure')
    item(md, 'Tools and utensils counted').locator('label.ck input').check()
    md.get_by_role('button', name='Line cleared').click(); pg.wait_for_selector('.md .msg.err >> text=Describe each problem')
    field(md, 'Problems found *').fill('Scraper missing'); field(md, 'Corrections / corrective action *').fill('Found under bench, cleaned and returned')
    md.get_by_role('button', name='Line cleared').click(); pg.wait_for_selector('.badge >> text=Line cleared · LC-2026-001')
    lc = T['hx_line_clearances'][0]
    check(lc['batch_id'] == 'be1' and lc['result'] == 'cleared' and lc['equipment_ids'] == ['q1'] and lc['checks']['tools']['r'] == 'fail' and lc['checks']['tools']['fixed'] and 'safety' in lc['checks'], 'line clearance saved with checklist, equipment and correction')
    # not cleared on the second batch
    card(pg, 'ETH-502').get_by_role('button', name='Line clearance').click(); md = pg.locator('.md')
    rows = md.locator('div.card div.row')
    for i in range(rows.count()): rows.nth(i).get_by_role('button', name='Pass').click()
    item(md, 'Area and equipment cleaned').get_by_role('button', name='Fail').click()
    field(md, 'Problems found *').fill('Residue on the evaporator'); field(md, 'Corrections / corrective action *').fill('Line stopped, re-clean scheduled')
    md.get_by_role('button', name='Record NOT cleared').click(); pg.wait_for_function("!document.querySelector('.md')")
    check(T['hx_line_clearances'][1]['result'] == 'not_cleared', 'line recorded as NOT cleared')
    # page
    pg.get_by_role('button', name='Line Clearance and Rework').click(); pg.wait_for_selector('text=LC-2026-002')
    check(pg.locator('.card.gold', has_text='Batches cleared (30 days)').locator('.v').inner_text() == '1 / 2', 'page: 1 of 2 batches cleared')
    check(pg.locator('tr', has_text='LC-2026-002').get_by_role('button', name='Deviation').count() == 1, 'not-cleared line can raise a deviation')
    with pg.expect_popup() as pop: pg.locator('tr', has_text='LC-2026-001').get_by_role('button', name='Print').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('LC-2026-001' in html and 'CLEARED' in html and 'FAIL - corrected' in html and 'EQ-001 Rotovap' in html, 'printable line clearance record'); w.close()
    # rework
    pg.locator('.tabs button', has_text='Rework').click(); pg.wait_for_selector('text=No rework yet.')
    pg.get_by_role('button', name='+ Rework').click(); md = pg.locator('.md')
    field(md, 'Batch *').select_option('be1'); field(md, 'Rework material *').fill('Winterized crude from tail fraction'); field(md, 'Quantity').fill('850')
    field(md, 'Why it is reworked *').fill('Potency below spec, re-distill'); field(md, 'Rework tag / METRC tag').fill('1A4000000000000000009999')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('text=RW-2026-001')
    r = T['hx_rework'][0]; check(r['source_batch_id'] == 'be1' and r['tag'].endswith('9999'), 'rework identified from a batch, tagged')
    pg.locator('tr', has_text='RW-2026-001').get_by_role('button', name='Inspect').click(); md = pg.locator('.md')
    field(md, 'Inspection (what was checked) *').fill('Clear amber, no debris'); md.get_by_role('button', name='Record inspection').click(); pg.wait_for_selector('.md .msg.err >> text=Record the inspection and the analysis')
    field(md, 'Analysis (test results / COA) *').fill('In-house potency 71%, solvents pass'); md.get_by_role('button', name='Record inspection').click(); pg.wait_for_selector('.msg >> text=Inspection recorded')
    pg.locator('tr', has_text='RW-2026-001').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.get_by_role('button', name='Approve').click(); pg.wait_for_selector('.md .msg.err >> text=like-to-like')
    md.locator('label.ck', has_text='Like-to-like').locator('input').check(); field(md, 'Rework expires on *').fill('2027-03-01'); md.get_by_role('button', name='Approve').click(); pg.wait_for_selector('.msg >> text=Approved RW-2026-001')
    pg.locator('tr', has_text='RW-2026-001').get_by_role('button', name='Use in batch').click(); md = pg.locator('.md')
    field(md, 'Batch it went into *').select_option('be2'); field(md, 'Finished product expires on').fill('2027-09-01')
    check(md.locator('.msg.err', has_text='rework must not expire before the finished product').count() == 1, 'rework expiring before the product is blocked')
    field(md, 'Finished product expires on').fill('2027-02-01'); md.get_by_role('button', name='Record use').click(); pg.wait_for_selector('.msg >> text=Recorded RW-2026-001 used')
    r = T['hx_rework'][0]; check(r['status'] == 'used' and r['target_batch_id'] == 'be2' and r['approved_by'] == 'Sam', 'rework used in a traceable batch')
    pg.get_by_role('button', name='+ Rework').click(); md = pg.locator('.md')
    field(md, 'Comes from').select_option('other'); field(md, 'Source').fill('Floor sweep'); field(md, 'Rework material *').fill('Spilled kief'); field(md, 'Why it is reworked *').fill('Spill')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('text=RW-2026-002')
    pg.locator('tr', has_text='RW-2026-002').get_by_role('button', name='Destroy').click(); md = pg.locator('.md')
    md.locator('textarea').fill('Contaminated, destroyed per waste log'); md.get_by_role('button', name='Destroy').click(); pg.wait_for_selector('.msg >> text=Destroyed RW-2026-002.')
    check(T['hx_rework'][1]['status'] == 'destroyed', 'rework destroyed with a reason')
    pg.screenshot(path=OUT + 'rework.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
