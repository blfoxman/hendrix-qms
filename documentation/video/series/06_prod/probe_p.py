from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_prod()
EX = 'localStorage.setItem("hx_ptype","gummies");localStorage.setItem("hx_btype","pre_rolls");localStorage.setItem("hx_pptype","pre_rolls");localStorage.setItem("hx_cultab","batches");'
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_p', extra=EX)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    S = lambda n: pg.screenshot(path=P + 'p_' + n + '.png')
    navb(pg, 'Products').click(); pg.wait_for_selector('.card >> text=Black Fox Gummies 100mg 10pk'); pg.wait_for_timeout(500); S('products')
    pg.get_by_role('button', name='+ New SKU').click(); pg.wait_for_selector('.md'); pg.wait_for_timeout(300); S('wiz1')
    md = pg.locator('.md'); md.get_by_role('button', name='Next: formulation').click(); pg.wait_for_timeout(400); S('wiz2'); print(md.inner_text()[:1500])
    closeall(r, pg)
    navb(pg, 'Batch Tracker').click(); pg.wait_for_selector('.card >> text=PR-2026-041'); pg.wait_for_timeout(400); S('bt')
    pg.get_by_role('button', name='+ New Batch').click(); pg.wait_for_selector('.md'); pg.wait_for_timeout(400); S('bt_new')
    closeall(r, pg)
    navb(pg, 'Testing').click(); pg.wait_for_selector('.card >> text=PR-2026-041'); pg.wait_for_timeout(400); S('test')
    navb(pg, 'Compliance Stickers').click(); pg.wait_for_timeout(800); S('stk')
    pg.locator('select').nth(1).select_option('lic-cul'); pg.wait_for_timeout(700)
    navb(pg, 'Cultivation').click(); pg.wait_for_selector('td >> text=PB-2026-021'); pg.wait_for_timeout(400); S('cul')
    print(errs); b.close()
