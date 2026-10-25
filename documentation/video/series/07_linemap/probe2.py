from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
reseed_lm()
ns = setup_lm(); seed_equipment(ns['T'])
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe')
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    navb(pg, 'Line Map').click(); pg.wait_for_selector('text=Stops right now'); pg.wait_for_timeout(800)
    pg.locator('button[aria-label^="2 batches at Lab testing"]').click(); pg.wait_for_timeout(600)
    pg.screenshot(path=P + 'grp.png', full_page=True)
    lst = pg.locator('.card', has=pg.locator('text=2 batches at Lab testing')).first
    print('GRP', lst.inner_text())
    lst.get_by_text('GM-2026-041').first.click(); pg.wait_for_timeout(500)
    pg.screenshot(path=P + 'grp2.png', full_page=True)
    pg.get_by_role('button', name='Stops only').click(); pg.wait_for_timeout(500); pg.screenshot(path=P + 'stopsonly.png')
    pg.get_by_role('button', name='All batches').click()
    train(pg, 'PR-2026-207').click(); pg.wait_for_timeout(400)
    pg.get_by_role('button', name='Open Equipment').click(); pg.wait_for_timeout(1200)
    pg.screenshot(path=P + 'equip.png')
    navb(pg, 'Settings').click(); pg.wait_for_timeout(500)
    pg.get_by_role('button', name='Line Map', exact=True).last.click(); pg.wait_for_timeout(400)
    inp = pg.locator('input[aria-label="Hours without an update"]'); inp.fill('0')
    pg.get_by_role('button', name='Save settings').click(); pg.wait_for_timeout(600); pg.screenshot(path=P + 'set0.png')
    inp.fill('6'); pg.get_by_role('button', name='Save settings').click(); pg.wait_for_timeout(800); pg.screenshot(path=P + 'set6.png')
    print('settings', ns['T']['hx_license_settings'][0]['linemap_idle_hours'])
    print(errs)
    b.close()
