from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_lm()
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_lm', fixed=None)
    navb(pg, 'Line Map').click(); pg.wait_for_selector('text=Stops right now'); pg.wait_for_timeout(800)
    pg.locator('button[aria-label^="GM-2026-045,"]').click(); pg.wait_for_selector('text=WHY IT IS STOPPED'); pg.wait_for_timeout(400)
    det = pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
    print(det.inner_text())
    print(det.bounding_box())
    pg.screenshot(path=P + 'lm_det.png', full_page=True)
    pg.get_by_role('button', name='Wall display').click(); pg.wait_for_timeout(1000)
    print('fs', pg.evaluate('!!document.fullscreenElement')); pg.screenshot(path=P + 'lm_wall.png')
    pg.keyboard.press('Escape'); pg.evaluate('document.fullscreenElement&&document.exitFullscreen()'); pg.wait_for_timeout(500)
    navb(pg, 'Settings').click(); pg.wait_for_timeout(500)
    pg.get_by_role('button', name='Line Map', exact=True).last.click(); pg.wait_for_timeout(500)
    pg.screenshot(path=P + 'lm_set.png')
    b.close()
