# Manufacturing Process (step 61): material used -> product produced + waste -> required additional process, per-license item list
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_licenses'].append({'id': 'lic-cul', 'state_id': 'st-mo', 'name': 'Cul 60', 'license_number': 'CUL000060', 'license_type': 'Cultivation', 'active': True})
T['hx_mp_runs'] = []; T['hx_mp_items'] = []
import datetime as dt
_h0 = handle
def handle(route, request):
    if urllib.parse.urlparse(request.url).path.endswith('/rpc/hx_line_map'):   # no batches - only the runs on the map
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'now': dt.datetime.now(dt.timezone.utc).isoformat(), 'idle_hours': 4, 'batches': [], 'plans': [], 'equipment_issues': []}))
    return _h0(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def start(ctx, lic):
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","%s");' % (json.dumps(json.dumps(sess)), lic))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.goto(BASE); pg.wait_for_selector('text=Dashboard'); return pg
def add_item(pg, name, unit='g'):
    md = pg.locator('.md').last
    md.locator('input[placeholder^="e.g. Rosin, Hash"]').fill(name)
    md.locator('select').last.select_option(unit); md.get_by_role('button', name='Add item').click()
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 1000}); ctx.route('**/*', handle)
    pg = start(ctx, 'lic-mo')
    check(pg.locator('.nav').get_by_role('button', name='Manufacturing Process').count() == 0, 'no separate sidebar entry - it lives in Batch Tracker')
    pg.locator('.nav').get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('.tabs >> text=Pre-Rolls')
    pg.locator('.tabs').get_by_role('button', name='Manufacturing Process').click()
    check(pg.locator('h1', has_text='Tracker').count() == 1, 'Manufacturing Process opens as a Batch Tracker tab')
    pg.wait_for_selector('text=No runs yet.')
    check(pg.get_by_role('button', name='+ New run').count() == 1, 'New run button')
    pg.get_by_role('button', name='+ New run').click(); md = pg.locator('.md').first
    check(md.locator('text=Part 1').count() >= 1 and md.locator('text=Part 2').count() >= 1 and md.locator('text=Waste').count() >= 1, 'Part 1, Part 2 and Waste are on the form')
    check(md.locator('th', has_text='METRC tag #').count() == 2 and md.locator('th', has_text='Item').count() == 2 and md.locator('th', has_text='Weight').count() == 2, 'tag, item, weight columns in both parts')
    check(md.get_by_role('button', name='+ Required additional process').count() == 1 and md.locator('text=Part 3 \u00b7 Additional').count() == 0, 'Required additional process button; no Part 3 yet')
    # Part 1 row 1: tag + new item
    md.locator('input[placeholder="1A4..."]').nth(0).fill('1a4 0000 0000 0000 0000 6101')
    md.locator('td select').nth(0).select_option('__new'); add_item(pg, 'Hash'); pg.wait_for_selector('.md >> text=Add an item', state='detached')
    check(md.locator('td select').nth(0).input_value() == 'Hash', 'the new item is picked on the row')
    md.locator('input[type=number]').nth(0).fill('500')
    # add a second material row
    md.get_by_role('button', name='+ Add row').nth(0).click()
    check(md.locator('input[placeholder="1A4..."]').count() == 3, 'rows can be added')
    md.locator('td select').nth(1).select_option('Hash'); md.locator('input[type=number]').nth(1).fill('25')
    # Part 2: new item Rosin, weight, waste
    md.locator('td select').nth(2).select_option('__new'); add_item(pg, 'Rosin'); pg.wait_for_selector('.md >> text=Add an item', state='detached')
    md.locator('input[placeholder="1A4..."]').nth(2).fill('1A4000000000000000006102'); md.locator('input[type=number]').nth(2).fill('300')
    md.locator('input[placeholder="0"]').last.fill('20'); md.locator('input[placeholder^="e.g. press loss"]').fill('press loss')
    check(md.locator('text=yield 57.1%').count() == 1, 'mass balance and yield shown (300 g out of 525 g in)')
    # required additional process -> Part 3
    md.get_by_role('button', name='+ Required additional process').click()
    check(md.locator('text=Part 3 · Additional process').count() == 1, 'Part 3 appears')
    sel = md.locator('td select'); n = sel.count()
    sel.nth(n - 1).select_option('Rosin'); md.locator('input[type=number]').nth(md.locator('input[type=number]').count() - 2).fill('280')
    check(md.get_by_role('button', name='+ Another required additional process').count() == 1, 'another additional process can follow')
    pg.screenshot(path=OUT + 'mp_form.png')
    md.get_by_role('button', name='Save run').click(); pg.wait_for_selector('.msg >> text=Run saved - In process.')
    r = T['hx_mp_runs'][-1]
    check(len(r['materials']) == 2 and r['materials'][0]['tag'] == '1A400000000000000006101' and r['materials'][0]['item'] == 'Hash' and r['materials'][0]['weight'] == '500', 'material rows saved (tag cleaned)')
    check(len(r['produced']) == 2 and r['produced'][0]['rows'][0]['item'] == 'Rosin' and r['produced'][0]['waste']['weight'] == '20' and r['produced'][0]['waste']['note'] == 'press loss', 'Part 2 and its waste saved')
    check(r['produced'][1]['rows'][0]['item'] == 'Rosin' and r['produced'][1]['rows'][0]['weight'] == '280', 'Part 3 saved')
    check(len(T['hx_mp_items']) == 2 and {i['name'] for i in T['hx_mp_items']} == {'Hash', 'Rosin'}, 'items saved to this license')
    check(pg.locator('tr', has_text='Rosin 280 g').count() == 1 and pg.locator('tr', has_text='Hash 500 g').count() == 1, 'the run is in the list')
    check(r.get('status') == 'in_process' and pg.locator('tr', has_text='Rosin 280 g').locator('select.mpst').input_value() == 'in_process', 'a new run starts In process')
    # an open run changes without a reason
    pg.get_by_role('button', name='Open / edit').click(); md = pg.locator('.md').first
    check(md.locator('text=Reason for the change').count() == 0, 'no reason asked while the run is open')
    md.locator('input[type=number]').nth(0).fill('510'); md.get_by_role('button', name='Save changes').click(); pg.wait_for_selector('.msg >> text=Saved PR-')
    check(T['hx_mp_runs'][-1]['materials'][0]['weight'] == '510', 'change saved')
    # status from the list: Testing -> Passed -> Complete
    for v, lbl in (('testing', 'Testing'), ('passed', 'Passed'), ('complete', 'Complete')):
        pg.locator('tr', has_text='Rosin 280 g').locator('select.mpst').select_option(v); pg.wait_for_selector('.msg >> text=: ' + lbl + '.')
    check(T['hx_mp_runs'][-1]['status'] == 'complete', 'status changed from the list (In process -> Testing -> Passed -> Complete)')
    # a Complete run needs a reason to change
    pg.get_by_role('button', name='Open / edit').click(); md = pg.locator('.md').first
    md.locator('input[type=number]').nth(0).fill('511'); md.get_by_role('button', name='Save changes').click()
    check(md.locator('.msg.err', has_text='This run is Complete. Say why').count() == 1, 'a Complete run needs a reason')
    md.locator('input[placeholder^="e.g. corrected"]').fill('scale re-check'); md.get_by_role('button', name='Save changes').click(); pg.wait_for_selector('.msg >> text=Saved PR-')
    check(T['hx_mp_runs'][-1]['materials'][0]['weight'] == '511' and T['hx_mp_runs'][-1]['edit_reason'] == 'scale re-check', 'changed with the reason')
    # save unfinished and come back for the number
    pg.get_by_role('button', name='+ New run').click(); md = pg.locator('.md').first
    md.locator('td select').nth(0).select_option('Hash'); md.locator('input[type=number]').nth(0).fill('1294')
    md.locator('input[placeholder="1A4..."]').nth(1).fill('1A40C03000060E1000003277'); md.locator('td select').nth(1).select_option('Rosin')
    check(md.locator('input[type=number]').nth(1).get_attribute('placeholder') == 'later', 'blank weight says later')
    md.locator('select').nth(0).select_option('complete'); md.get_by_role('button', name='Save run').click()
    check(md.locator('.msg.err', has_text='enter every weight before marking the run Complete').count() == 1, 'Complete needs every weight')
    md.locator('select').nth(0).select_option('in_process'); md.get_by_role('button', name='Save run').click(); pg.wait_for_selector('.msg >> text=1 weight still to enter')
    r2 = T['hx_mp_runs'][-1]
    check(r2['status'] == 'in_process' and r2['produced'][0]['rows'][0]['weight'] == '' and r2['produced'][0]['rows'][0]['tag'] == '1A40C03000060E1000003277', 'saved with the weight blank')
    row2 = pg.locator('tr', has_text='Rosin (weight to come)')
    check(row2.locator('text=1 weight to enter').count() == 1, 'list shows the weight still to enter')
    row2.locator('select.mpst').select_option('complete')
    check(pg.locator('.msg.err', has_text='enter every weight before marking it Complete').count() == 1 and T['hx_mp_runs'][-1]['status'] == 'in_process', 'cannot complete from the list with a weight missing')
    row2.get_by_role('button', name='Open / edit').click(); md = pg.locator('.md').first
    md.locator('input[type=number]').nth(1).fill('1100'); md.locator('select').nth(0).select_option('complete'); md.get_by_role('button', name='Save changes').click(); pg.wait_for_selector('.msg >> text=- Complete.')
    check(T['hx_mp_runs'][-1]['status'] == 'complete' and T['hx_mp_runs'][-1]['produced'][0]['rows'][0]['weight'] == '1100', 'came back, entered the number and completed it')
    pg.locator('.md').wait_for(state='detached') if pg.locator('.md').count() else None
    pg.locator('select[title="Show runs by status"]').select_option('open')
    check(pg.locator('text=No runs with this status.').count() == 1, 'filter: no open runs left')
    pg.locator('select[title="Show runs by status"]').select_option('')
    # items list
    pg.get_by_role('button', name='Items (2)').click(); md = pg.locator('.md').first
    check(md.locator('td', has_text='Hash').count() == 1 and md.locator('td', has_text='Rosin').count() == 1, 'items list')
    md.locator('input[placeholder^="e.g. Hash, Rosin"]').fill('Pre-roll 1g'); md.locator('select').nth(0).select_option('each'); md.get_by_role('button', name='Add', exact=True).click()
    pg.wait_for_selector('.md >> text=Pre-roll 1g')
    check(any(i['name'] == 'Pre-roll 1g' and i['unit'] == 'each' for i in T['hx_mp_items']), 'a license can add its own product with its own unit')
    md.get_by_role('button', name='Done').click()
    # void
    pg.locator('tr', has_text='Hash 1294 g').get_by_role('button', name='Void').click(); pg.locator('.md textarea').fill('wrong license'); pg.locator('.md').get_by_role('button', name='Void').last.click()
    pg.wait_for_selector('.msg >> text=Voided'); check(T['hx_mp_runs'][-1]['voided'] is True and T['hx_mp_runs'][-1]['void_reason'] == 'wrong license', 'run voided with a reason')
    pg.reload(); pg.wait_for_selector('text=Dashboard'); pg.locator('.nav').get_by_role('button', name='Batch Tracker').click()
    pg.wait_for_selector('.tabs button.on:has-text("Manufacturing Process")')
    check(pg.locator('text=What went in, what came out').count() == 1, 'Batch Tracker reopens on the Manufacturing Process tab')
    pg.locator('.tabs').get_by_role('button', name='Pre-Rolls').click(); pg.wait_for_selector('input[placeholder="Search batches..."]')
    check(pg.locator('tr', has_text='Rosin 280 g').count() == 0, 'other tabs show their batches again')
    # Line Map: open runs on the Manufacturing Process line, then Testing, Passed / Failed, Completed
    NW = dt.datetime.now(dt.timezone.utc); iso = lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ')
    def run(i, num, stt, w2, upd, **kw):
        x = {'id': 'lm%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': num, 'run_date': NW.strftime('%Y-%m-%d'), 'status': stt, 'voided': False, 'note': '',
             'materials': [{'tag': '', 'item': 'HTE', 'weight': '1294', 'unit': 'g'}], 'produced': [{'rows': [{'tag': '', 'item': 'Decarbed Cured Resin', 'weight': w2, 'unit': 'g'}], 'waste': {'weight': '', 'note': ''}}],
             'created_at': iso(upd), 'updated_at': iso(upd), 'created_by': 'Sam'}
        x.update(kw); return x
    T['hx_mp_runs'] = [run(1, 'PR-LM-01', 'in_process', '', NW), run(2, 'PR-LM-02', 'testing', '900', NW), run(3, 'PR-LM-03', 'failed', '900', NW),
                       run(4, 'PR-LM-04', 'complete', '900', NW, completed_at=iso(NW)), run(5, 'PR-LM-05', 'complete', '900', NW - dt.timedelta(days=9), completed_at=iso(NW - dt.timedelta(days=9))),
                       run(6, 'PR-LM-06', 'in_process', '', NW - dt.timedelta(hours=9), produced=[{'rows': [{'tag': '', 'item': 'Rosin', 'weight': '700', 'unit': 'g'}, {'tag': '', 'item': 'Rosin', 'weight': '', 'unit': 'g'}], 'waste': {}}]), run(7, 'PR-LM-07', 'in_process', '1', NW, voided=True)]
    pg.locator('.nav').get_by_role('button', name='Line Map').click(); pg.wait_for_selector('text=Production Line Map')
    def tr(label): return pg.locator('button[aria-label^="%s,"]' % label)
    pg.wait_for_timeout(800); pg.screenshot(path=OUT + 'lm_mp.png')
    check(pg.locator('div', has_text=re.compile('^Manufacturing Process$')).count() >= 1 and pg.locator('text=Material used').count() >= 1 and pg.locator('text=Product produced').count() >= 1, 'Line Map has a Manufacturing Process line (Material used -> Product produced -> Additional process)')
    check(tr('PR-LM-01').count() == 1 and 'moving' in tr('PR-LM-01').get_attribute('aria-label'), 'an open run is moving on the line')
    check(tr('PR-LM-02').count() == 1 and 'waiting' in tr('PR-LM-02').get_attribute('aria-label'), 'a run in Testing is waiting for the result')
    check(tr('PR-LM-03').count() == 1 and 'Run marked Failed' in tr('PR-LM-03').get_attribute('aria-label'), 'a Failed run is stopped')
    check(tr('PR-LM-04').count() == 1 and 'done' in tr('PR-LM-04').get_attribute('aria-label'), 'a Complete run sits at Completed')
    check(tr('PR-LM-06').count() == 1 and 'No update for 9 h' in tr('PR-LM-06').get_attribute('aria-label') and '1 weight still to enter' in tr('PR-LM-06').get_attribute('aria-label'), 'a run left open with no update is flagged, with its missing weights')
    check(tr('PR-LM-05').count() == 0 and tr('PR-LM-07').count() == 0, 'old completed and void runs are not on the map')
    tr('PR-LM-06').click(); pg.wait_for_selector('text=Open the run')
    check(pg.locator('text=Manufacturing Process line').count() == 1, 'run details show its line')
    pg.get_by_role('button', name='Open the run').click(); pg.wait_for_selector('.tabs button.on:has-text("Manufacturing Process")')
    check(pg.locator('tr', has_text='PR-LM-06').count() == 1, 'Open the run goes to Batch Tracker > Manufacturing Process')
    pg.locator('.nav').get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Line map')
    check(pg.locator('.card.gold', has_text='Line map').locator('text=2 batches stopped').count() == 1, 'dashboard line map card counts the stopped runs')
    pg.close(); ctx.close()
    # a cultivation license has no Manufacturing Process tab
    ctx2 = b.new_context(viewport={'width': 1400, 'height': 1000}); ctx2.route('**/*', handle)
    pg = start(ctx2, 'lic-cul')
    check(pg.locator('.nav').get_by_role('button', name='Manufacturing Process').count() == 0 and pg.locator('.nav').get_by_role('button', name='Batch Tracker').count() == 0, 'no Batch Tracker / Manufacturing Process on a cultivation license')
    b.close()
print('FAIL' if errors else 'ALL PASS'); sys.exit(1 if errors else 0)
