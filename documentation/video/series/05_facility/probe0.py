import sys; from common import *
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    ns = setup(); b, ctx, pg = open_app(pw, ns)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    for i, name in enumerate(['Facility Logs', 'Visitor Log', 'Equipment', 'Chemicals and SDS', 'Facility Tests', 'Line Clearance and Rework', 'Time Clock and Badges']):
        navb(pg, name).click(); pg.wait_for_timeout(1500)
        pg.screenshot(path=HERE + '/work/probe/p0_%d.png' % i)
        print(name, '|', [t for t in pg.locator('.main button').all_inner_texts() if t.strip()][:40])
    print('errs', errs); b.close()
