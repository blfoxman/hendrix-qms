from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_prod()
EX = 'localStorage.setItem("hx_ptype","cartridges");localStorage.setItem("hx_btype","pre_rolls");localStorage.setItem("hx_pptype","pre_rolls");'
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_p', extra=EX)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    S = lambda n: pg.screenshot(path=P + 'q_' + n + '.png')
    navb(pg, 'Products').click(); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_selector('.card >> text=Muha Meds 2G AIO'); pg.wait_for_timeout(500); S('products')
    pg.locator('.tabs button', has_text='Gummies').click(); pg.wait_for_timeout(300)
    pg.get_by_role('button', name='+ New SKU').click(); md = pg.locator('.md')
    F(md, 'SKU name').fill('Black Fox Gummies 200mg 20pk'); F(md, 'Grams per gummy').fill('4.6'); F(md, 'Gummies per package').fill('20')
    F(md, 'Flavors - one per line').fill('Watermelon\nSour Apple')
    md.get_by_role('button', name='Next: formulation').click(); pg.wait_for_timeout(300)
    F(md, 'Standard batch size').fill('1000')
    sel = md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).first
    sel.select_option(label='Distillate ($1.85/g)'); md.locator('.li').nth(0).locator('input').nth(1).fill('230')
    sel.select_option(label='Gummy base ($0.02/g)'); md.locator('.li').nth(1).locator('input').nth(1).fill('91770')
    pg.wait_for_timeout(300); S('wiz2'); print(md.inner_text()[:2500])
    md.get_by_role('button', name='Save SKU and formulation').click(); pg.wait_for_timeout(1200); S('saved')
    print('MSG', [m.inner_text() for m in pg.locator('.msg').all()])
    print('SKUs', [(k['name'], k['active']) for k in ns['T']['hx_skus']][-2:])
    pg.locator('.tabs button', has_text='Formulation Bank').click(); pg.wait_for_timeout(500); S('bank')
    print(errs); b.close()
