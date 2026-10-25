from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_lm(); seed_equipment(ns['T'])
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe')
    msgs = []; pg.on('console', lambda m: msgs.append(m.type + ' ' + m.text[:200])); pg.on('pageerror', lambda e: msgs.append('ERR ' + str(e)))
    pg.on('response', lambda x: msgs.append('RESP %s %s' % (x.status, x.url[-120:])) if x.status >= 400 else None)
    navb(pg, 'Equipment').click(); pg.wait_for_timeout(4000)
    pg.screenshot(path=P + 'equip2.png')
    print(pg.locator('.main').inner_text()[:600])
    print('\n'.join(msgs[-30:]))
    b.close()
