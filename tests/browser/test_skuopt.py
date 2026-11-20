# Pre-Roll SKU settings (Sam, Nov 20 2026): Infused? -> Infused with (own list); Coated? -> Coated with (own list); new
# infusion ingredients get METRC # + amount on the batch form; custom coatings rename the Kief steps
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
import re
T['hx_sku_options'] = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label, exact=False):
    pgx = md if hasattr(md, 'goto') else md.page
    sp = pgx.locator('span', has_text=re.compile('^' + re.escape(label) + ('$' if exact else '')))
    return md.locator('label.f, div.f', has=sp).locator('input,select,textarea').first
def sku(n): return next(k for k in T['hx_skus'] if k['name'] == n)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 1000}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_ptype","pre_rolls");localStorage.setItem("hx_btype","pre_rolls");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.get_by_role('button', name='Products', exact=True).click(); pg.wait_for_selector('text=No Pre-Rolls SKUs in Missouri yet')
    pg.get_by_role('button', name='+ New SKU').click(); md = pg.locator('.md')
    inf = field(md, 'Infused?', True)
    check(inf.locator('option').all_inner_texts() == ['Infused', 'Not infused'], 'Infused? is Infused / Not infused')
    check(md.locator('span', has_text='Infused with').count() == 1 and md.locator('label.ck', has_text='Live Resin').count() == 1, 'infused: the Infused with list shows')
    check(field(md, 'Coated?', True).input_value() == 'No' and md.locator('span', has_text='Coated with').count() == 0 and md.locator('span', has_text='after coating').count() == 0, 'not coated by default: no coating choices')
    inf.select_option('Ground')
    check(md.locator('span', has_text='Infused with').count() == 0, 'not infused: no Infused with')
    inf.select_option('Infused')
    field(md, 'Coated?', True).select_option('Yes')
    co = field(md, 'Coated with')
    check(co.locator('option').all_inner_texts() == ['Kief', 'Diamond', '+ Add a new coating...'], 'coated: Coated with drop-down (Kief, Diamond, add new)')
    co.select_option('__new'); md.locator('input[placeholder^="New coating"]').fill('Moon Dust'); md.get_by_role('button', name='Add', exact=True).click()
    pg.wait_for_function('() => [...document.querySelectorAll(".md select option")].some(o => o.textContent === "Moon Dust")')
    check(any(o['kind'] == 'coating' and o['name'] == 'Moon Dust' and o['state_id'] == 'st-mo' for o in T['hx_sku_options']), 'new coating saved to the Missouri list')
    check(field(md, 'Coated with').input_value() == 'Moon Dust', 'and picked')
    md.get_by_role('button', name='+ Add a new ingredient').click(); md.locator('input[placeholder^="New ingredient"]').fill('Live Rosin'); md.locator('input[placeholder^="New ingredient"]').press('Enter')
    pg.wait_for_selector('.md label.ck:has-text("Live Rosin")')
    check(md.locator('label.ck', has_text='Live Rosin').locator('input').is_checked(), 'new ingredient added and ticked')
    md.locator('label.ck', has_text=re.compile('^THCA$')).locator('input').check()
    field(md, 'SKU name').fill('Rosin Moon 1g'); field(md, 'Grams per joint, filled').fill('1'); field(md, 'Grams per joint after coating').fill('1.1'); pg.screenshot(path=OUT + 'sku_form.png'); field(md, 'Grams per joint after coating').fill('')
    md.get_by_role('button', name='Next: formulation').click()
    check(md.locator('.msg.err', has_text='Enter grams per joint after coating').count() == 1, 'coated needs grams after coating')
    field(md, 'Grams per joint after coating').fill('1.1'); md.get_by_role('button', name='Next: formulation').click()
    md.get_by_role('button', name='+ Add Material').click(); li = md.locator('.li').first; li.locator('input').nth(0).fill('Flower'); li.locator('input').nth(1).fill('1000')
    md.get_by_role('button', name='Save SKU and formulation').click(); pg.wait_for_selector('.card >> text=Rosin Moon 1g')
    k = sku('Rosin Moon 1g')
    check(k['spec'] == {'grams_filled': 1, 'flower_type': 'Infused', 'coated': 'Yes', 'coating': 'Moon Dust', 'grams_kiefed': 1.1, 'ingredients': ['Live Rosin', 'THCA']}, 'SKU saved: %s' % k['spec'])
    check(pg.locator('.card', has_text='Rosin Moon 1g').locator('text=Coated with: Moon Dust').count() == 1, 'summary shows the coating')
    # lists modal
    pg.get_by_role('button', name='Infused with / Coated with lists').click(); md = pg.locator('.md')
    check(md.locator('td', has_text='Moon Dust').count() == 1 and md.locator('td', has_text='Live Rosin').count() == 1, 'lists show the state choices')
    md.locator('input[placeholder="Add a ingredient..."]').fill('Kief Hash'); md.get_by_role('button', name='Add ingredient').click(); pg.wait_for_selector('.md td:has-text("Kief Hash")')
    md.locator('input[placeholder="Add a coating..."]').fill('kief'); md.get_by_role('button', name='Add coating').click()
    check(md.locator('.msg.err', has_text='already built in').count() == 1, 'built-in names not added twice')
    md.locator('tr', has_text='Kief Hash').get_by_role('button', name='Switch off').click(); pg.wait_for_selector('.md td:has-text("Kief Hash (off)")')
    check(next(o for o in T['hx_sku_options'] if o['name'] == 'Kief Hash')['active'] is False, 'switched off, not deleted')
    md.get_by_role('button', name='Done').click()
    # edit: not infused + not coated clears those settings
    pg.locator('.card', has_text='Rosin Moon 1g').get_by_role('button', name='Edit').first.click(); md = pg.locator('.md')
    check(md.locator('label.ck', has_text='Kief Hash').count() == 0, 'switched-off choice not offered')
    check(field(md, 'Coated with').input_value() == 'Moon Dust' and field(md, 'Coated?', True).input_value() == 'Yes', 'editor shows saved settings')
    field(md, 'Infused?', True).select_option('Ground'); field(md, 'Coated?', True).select_option('No')
    md.get_by_role('button', name='Save', exact=True).click(); pg.wait_for_selector('.md', state='detached')
    k = sku('Rosin Moon 1g')
    check(k['spec'] == {'grams_filled': 1, 'flower_type': 'Ground', 'coated': 'No'}, 'not infused / not coated clears the rest: %s' % k['spec'])
    # an older SKU (no "coated" saved) shows Coated? Yes from its after-coating weight
    T['hx_skus'].append({'id': 'old1', 'state_id': 'st-mo', 'product_type': 'pre_rolls', 'name': 'Old Mates', 'spec': {'grams_filled': 0.55, 'grams_kiefed': 0.6, 'ingredients': ['THCA'], 'coating': 'Kief'}, 'license_ids': [], 'active': True, 'sort': 5})
    # batch form with a custom ingredient and coating
    k = sku('Rosin Moon 1g'); k['spec'] = {'grams_filled': 1, 'flower_type': 'Infused', 'coated': 'Yes', 'coating': 'Moon Dust', 'grams_kiefed': 1.1, 'ingredients': ['Live Rosin', 'THCA']}; k['active'] = True
    pg.goto(BASE); pg.get_by_role('button', name='Products', exact=True).click(); pg.wait_for_selector('.card >> text=Old Mates')
    pg.locator('.card', has_text='Old Mates').get_by_role('button', name='Edit').first.click(); md = pg.locator('.md')
    check(field(md, 'Coated?', True).input_value() == 'Yes' and field(md, 'Coated with').input_value() == 'Kief', 'older SKU: coated Yes (Kief) from its saved weight')
    md.get_by_role('button', name='Cancel').click()
    pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('h1 >> text=Tracker')
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Rosin Moon 1g')
    check(field(md, 'Live Rosin METRC #').count() == 1 and field(md, 'Live Rosin Used').count() == 1 and field(md, 'THCA Used').count() == 1, 'custom ingredient has its METRC # and amount')
    check(md.locator('text=Infused Moon Dust Coated Preroll').count() >= 1 and field(md, 'Moon Dust QTY Used').count() == 1, 'Kief steps renamed to the coating')
    field(md, 'Batch / Lot Number').fill('PR-RM1'); field(md, 'Flower Used').fill('1000'); field(md, 'THCA Used').fill('100'); field(md, 'Live Rosin Used').fill('140')
    field(md, 'Live Rosin METRC #').fill('1A4000000000000000007777'); field(md, 'Infused Flower Total WT').fill('1240')
    check(md.locator('.chkp.ok', has_text='flower weight matches').count() == 1, 'custom ingredient counts in the flower check (1000+100+140 = 1240)')
    md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=PR-RM1')
    d = T['hx_batches'][-1]['data']
    check(d.get('xi_live_rosin_qty') == '140' and d.get('xi_live_rosin_metrc') == '1A4000000000000000007777' and d.get('flower_check_status') == 'pass', 'saved with the batch')
    b.close()
print('FAIL' if errors else 'ALL PASS'); sys.exit(1 if errors else 0)
