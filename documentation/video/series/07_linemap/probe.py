from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'; os.makedirs(P, exist_ok=True)
reseed_lm()
ns = setup_lm()
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe')
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.screenshot(path=P + 'dash.png', full_page=True)
    navb(pg, 'Line Map').click(); pg.wait_for_selector('text=Stops right now'); pg.wait_for_timeout(800)
    pg.screenshot(path=P + 'lm1.png'); pg.screenshot(path=P + 'lm_full.png', full_page=True)
    for x in pg.locator('button[aria-label]').all(): print('TRAIN', x.get_attribute('aria-label'))
    det = pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
    for bn in ('GM-2026-045', 'PR-2026-207', 'CT-2026-119'):
        train(pg, bn).click(); pg.wait_for_selector('text=WHY IT IS STOPPED'); pg.wait_for_timeout(400)
        print('====', bn); print(det.inner_text())
        print([x.inner_text() for x in det.get_by_role('button').all()])
        pg.screenshot(path=P + 'det_%s.png' % bn, full_page=True)
    sr = pg.locator('.card', has=pg.locator('h3', has_text='Stops right now')).first
    print('==== STOPS'); print(sr.inner_text())
    print(errs)
    b.close()
    # executive
    b, pg, r = app(pw, ns, 'probe', uid=EXEC, wait=None)
    pg.wait_for_timeout(1500); pg.screenshot(path=P + 'exec_home.png', full_page=True)
    print('NAV', pg.locator('.nav').inner_text())
    navb(pg, 'Line Map').click(); pg.wait_for_selector('text=Stops right now'); pg.wait_for_timeout(800)
    train(pg, 'PR-2026-207').click(); pg.wait_for_selector('text=WHY IT IS STOPPED'); pg.wait_for_timeout(400)
    det = pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
    print('EXEC DET', det.inner_text()); print([x.inner_text() for x in det.get_by_role('button').all()])
    pg.screenshot(path=P + 'exec_det.png', full_page=True)
    b.close()
