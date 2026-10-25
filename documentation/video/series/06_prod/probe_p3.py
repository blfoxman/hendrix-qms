from common import *
from playwright.sync_api import sync_playwright
P = HERE + '/work/probe/'
ns = setup_prod(); T = ns['T']
b43 = next(x for x in T['hx_batches'] if x['id'] == 'b-pr43')
EX = 'localStorage.setItem("hx_ptype","cartridges");localStorage.setItem("hx_btype","pre_rolls");localStorage.setItem("hx_pptype","pre_rolls");'
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_p', extra=EX)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    S = lambda n: pg.screenshot(path=P + 'r_' + n + '.png')
    navb(pg, 'Batch Tracker').click(); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_selector('.card >> text=PR-2026-041'); pg.wait_for_timeout(500); S('list')
    print([x.inner_text().replace('\n',' | ')[:300] for x in pg.locator('.card', has_text='PR-2026-04').all()][:6])
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    F(md, 'Batch / Lot Number').fill('PR-2026-045')
    F(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); pg.wait_for_timeout(300)
    print('flavor tag', F(md, 'Flavor').evaluate('e=>e.tagName'))
    F(md, 'Flavor').select_option(label='Berry Blast'); pg.wait_for_timeout(300); S('form1')
    print([l.inner_text() for l in md.locator('label.f > span, div.f > span').all()][:60])
    F(md, 'Infused Flower Used').fill('550'); F(md, 'Total Joint Filled').fill('1180'); pg.wait_for_timeout(300)
    j = md.get_by_text(re.compile('UNDER WEIGHT')).first; print('under', j.count(), j.inner_text() if j.count() else '')
    j.scroll_into_view_if_needed(); S('under')
    md.evaluate('m=>m.scrollTo(0,m.scrollHeight)'); pg.wait_for_timeout(300); S('end')
    print(md.locator('canvas').count(), [x.inner_text() for x in md.get_by_role('button').all()][-8:])
    closeall(r, pg)
    c = pg.locator('.card', has_text='PR-2026-043')
    print('43 buttons', [x.inner_text() for x in c.get_by_role('button').all()])
    c.get_by_role('button', name='Continue').click(); pg.wait_for_timeout(500); S('cont')
    print(pg.locator('.md').inner_text()[:600])
    print(errs); b.close()
