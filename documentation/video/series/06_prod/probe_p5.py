from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_prod(); T = ns['T']
EX = 'localStorage.setItem("hx_cultab","batches");'
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_p', extra=EX)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    S = lambda n: pg.screenshot(path=P + 'c_' + n + '.png')
    print([o.inner_text() for o in pg.locator('select').nth(1).locator('option').all()])
    pg.locator('select').nth(1).select_option('lic-cul'); pg.wait_for_timeout(800)
    navb(pg, 'Cultivation').click(); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_selector('td >> text=PB-2026-021'); pg.wait_for_timeout(500); S('list')
    pg.get_by_role('button', name='+ Plant batch').click(); md = pg.locator('.md'); pg.wait_for_timeout(400); S('new'); print(md.inner_text()[:1200])
    print([(o.get_attribute('value'), o.inner_text()) for o in md.locator('option').all()])
    closeall(r, pg)
    pg.locator('tr', has_text='PB-2026-021').get_by_role('button', name='Open').click(); pg.wait_for_selector('.md >> text=Pre-harvest interval running'); pg.wait_for_timeout(300); S('open')
    pg.locator('.md').get_by_role('button', name='Crop protection').click(); md = pg.locator('.md').last; pg.wait_for_timeout(300); S('crop'); print(md.inner_text()[:1000])
    print(errs); b.close()
