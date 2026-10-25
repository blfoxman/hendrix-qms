from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_prod(); T = ns['T']
b43 = next(x for x in T['hx_batches'] if x['id'] == 'b-pr42')
EX = 'localStorage.setItem("hx_ptype","cartridges");localStorage.setItem("hx_btype","pre_rolls");localStorage.setItem("hx_pptype","pre_rolls");'
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_p', extra=EX)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    S = lambda n: pg.screenshot(path=P + 's_' + n + '.png')
    navb(pg, 'Testing').click(); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_selector('.card >> text=PR-2026-041'); pg.wait_for_timeout(500); S('list')
    c = pg.locator('.card', has_text='PR-2026-042').last
    print([x.inner_text() for x in c.get_by_role('button').all()])
    ns['AI']['tag'] = ns['tag'](1252)
    c.locator('input[type=file]').set_input_files(SCR + 'fake_coa.pdf'); pg.wait_for_timeout(2500); S('uploaded')
    print('MSG', [m.inner_text() for m in pg.locator('.msg').all()])
    c = pg.locator('.card', has_text='PR-2026-042').last; print(c.inner_text()[:600])
    pg.evaluate('window.scrollTo(0,0)')
    pg.locator('.card', has_text='CART-2026-118').last.get_by_role('button', name='Update').click(); md = pg.locator('.md'); pg.wait_for_timeout(300)
    F(md, 'Status').select_option('Retest'); pg.wait_for_timeout(300); S('update'); print(md.inner_text()[:900]); closeall(r, pg)
    pg.locator('.card', has_text='PR-2026-041').last.get_by_role('button', name='Compliance Sticker').click(); pg.wait_for_selector('.md iframe'); pg.wait_for_timeout(1500); S('sticker')
    print(pg.locator('.md').inner_text()[:1500])
    print(errs); b.close()
