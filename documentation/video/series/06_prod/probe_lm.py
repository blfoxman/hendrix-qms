from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'; os.makedirs(P, exist_ok=True)
reseed_lm()
ns = setup_lm()
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_lm', fixed=None)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    navb(pg, 'Line Map').click(); pg.wait_for_selector('text=Stops right now'); pg.wait_for_timeout(800)
    pg.screenshot(path=P + 'lm1.png'); pg.screenshot(path=P + 'lm_full.png', full_page=True)
    for x in pg.locator('button[aria-label]').all():
        print(x.get_attribute('aria-label'))
    g = pg.locator('button[aria-label*="batches at"]')
    if g.count():
        g.first.click(); pg.wait_for_timeout(500); pg.screenshot(path=P + 'lm_group.png', full_page=True)
    print(errs)
    b.close()
