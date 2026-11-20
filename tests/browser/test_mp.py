# Manufacturing Process (step 61): material used -> product produced + waste -> required additional process, per-license item list
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_licenses'].append({'id': 'lic-cul', 'state_id': 'st-mo', 'name': 'Cul 60', 'license_number': 'CUL000060', 'license_type': 'Cultivation', 'active': True})
T['hx_mp_runs'] = []; T['hx_mp_items'] = []
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
    pg.locator('.nav').get_by_role('button', name='Manufacturing Process').click()
    pg.wait_for_selector('text=No runs yet.')
    check(pg.get_by_role('button', name='+ New run').count() == 1, 'New run button')
    pg.get_by_role('button', name='+ New run').click(); md = pg.locator('.md').first
    check(md.locator('text=Part 1').count() >= 1 and md.locator('text=Part 2').count() >= 1 and md.locator('text=Waste').count() >= 1, 'Part 1, Part 2 and Waste are on the form')
    check(md.locator('th', has_text='METRC tag #').count() == 2 and md.locator('th', has_text='Item').count() == 2 and md.locator('th', has_text='Weight').count() == 2, 'tag, item, weight columns in both parts')
    check(md.get_by_role('button', name='+ Required additional process').count() == 1 and md.locator('text=Part 3 \u00b7 Additional').count() == 0, 'Required additional process button; no Part 3 yet')
    # Part 1 row 1: tag + new item
    md.locator('input[placeholder="1A4..."]').nth(0).fill('1a4 0000 0000 0000 0000 6101')
    md.locator('select').nth(0).select_option('__new'); add_item(pg, 'Hash'); pg.wait_for_selector('.md >> text=Add an item', state='detached')
    check(md.locator('select').nth(0).input_value() == 'Hash', 'the new item is picked on the row')
    md.locator('input[type=number]').nth(0).fill('500')
    # add a second material row
    md.get_by_role('button', name='+ Add row').nth(0).click()
    check(md.locator('input[placeholder="1A4..."]').count() == 3, 'rows can be added')
    md.locator('select').nth(1).select_option('Hash'); md.locator('input[type=number]').nth(1).fill('25')
    # Part 2: new item Rosin, weight, waste
    md.locator('select').nth(2).select_option('__new'); add_item(pg, 'Rosin'); pg.wait_for_selector('.md >> text=Add an item', state='detached')
    md.locator('input[placeholder="1A4..."]').nth(2).fill('1A4000000000000000006102'); md.locator('input[type=number]').nth(2).fill('300')
    md.locator('input[placeholder="0"]').last.fill('20'); md.locator('input[placeholder^="e.g. press loss"]').fill('press loss')
    check(md.locator('text=yield 57.1%').count() == 1, 'mass balance and yield shown (300 g out of 525 g in)')
    # required additional process -> Part 3
    md.get_by_role('button', name='+ Required additional process').click()
    check(md.locator('text=Part 3 · Additional process').count() == 1, 'Part 3 appears')
    sel = md.locator('select'); n = sel.count()
    sel.nth(n - 1).select_option('Rosin'); md.locator('input[type=number]').nth(md.locator('input[type=number]').count() - 2).fill('280')
    check(md.get_by_role('button', name='+ Another required additional process').count() == 1, 'another additional process can follow')
    pg.screenshot(path=OUT + 'mp_form.png')
    md.get_by_role('button', name='Save run').click(); pg.wait_for_selector('.msg >> text=Run saved.')
    r = T['hx_mp_runs'][-1]
    check(len(r['materials']) == 2 and r['materials'][0]['tag'] == '1A400000000000000006101' and r['materials'][0]['item'] == 'Hash' and r['materials'][0]['weight'] == '500', 'material rows saved (tag cleaned)')
    check(len(r['produced']) == 2 and r['produced'][0]['rows'][0]['item'] == 'Rosin' and r['produced'][0]['waste']['weight'] == '20' and r['produced'][0]['waste']['note'] == 'press loss', 'Part 2 and its waste saved')
    check(r['produced'][1]['rows'][0]['item'] == 'Rosin' and r['produced'][1]['rows'][0]['weight'] == '280', 'Part 3 saved')
    check(len(T['hx_mp_items']) == 2 and {i['name'] for i in T['hx_mp_items']} == {'Hash', 'Rosin'}, 'items saved to this license')
    check(pg.locator('tr', has_text='Rosin 280 g').count() == 1 and pg.locator('tr', has_text='Hash 500 g').count() == 1, 'the run is in the list')
    # editing needs a reason
    pg.get_by_role('button', name='Open / edit').click(); md = pg.locator('.md').first
    md.locator('input[type=number]').nth(0).fill('510'); md.get_by_role('button', name='Save changes').click()
    check(md.locator('.msg.err', has_text='Say why you are changing this run').count() == 1, 'a reason is required for a change')
    md.locator('input[placeholder^="e.g. corrected"]').fill('scale re-check'); md.get_by_role('button', name='Save changes').click(); pg.wait_for_selector('.msg >> text=Saved')
    check(T['hx_mp_runs'][-1]['materials'][0]['weight'] == '510', 'change saved')
    # items list
    pg.get_by_role('button', name='Items (2)').click(); md = pg.locator('.md').first
    check(md.locator('td', has_text='Hash').count() == 1 and md.locator('td', has_text='Rosin').count() == 1, 'items list')
    md.locator('input[placeholder^="e.g. Hash, Rosin"]').fill('Pre-roll 1g'); md.locator('select').nth(0).select_option('each'); md.get_by_role('button', name='Add', exact=True).click()
    pg.wait_for_selector('.md >> text=Pre-roll 1g')
    check(any(i['name'] == 'Pre-roll 1g' and i['unit'] == 'each' for i in T['hx_mp_items']), 'a license can add its own product with its own unit')
    md.get_by_role('button', name='Done').click()
    # void
    pg.get_by_role('button', name='Void').click(); pg.locator('.md textarea').fill('wrong license'); pg.locator('.md').get_by_role('button', name='Void').last.click()
    pg.wait_for_selector('.msg >> text=Voided'); check(T['hx_mp_runs'][-1]['voided'] is True and T['hx_mp_runs'][-1]['void_reason'] == 'wrong license', 'run voided with a reason')
    pg.close(); ctx.close()
    # a cultivation license has no Manufacturing Process tab
    ctx2 = b.new_context(viewport={'width': 1400, 'height': 1000}); ctx2.route('**/*', handle)
    pg = start(ctx2, 'lic-cul')
    check(pg.locator('.nav').get_by_role('button', name='Manufacturing Process').count() == 0, 'no Manufacturing Process tab on a cultivation license')
    b.close()
print('FAIL' if errors else 'ALL PASS'); sys.exit(1 if errors else 0)
