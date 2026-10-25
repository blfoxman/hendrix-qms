from common import *
from playwright.sync_api import sync_playwright
ns = setup_prod(); T = ns['T']
with sync_playwright() as pw:
    b, pg, r = app(pw, ns, 'probe_c', extra='localStorage.setItem("hx_cultab","batches");')
    pg.on('request', lambda q: q.method != 'GET' and 'supabase' in q.url and print(q.method, q.url[-80:], (q.post_data or '')[:300]))
    pg.on('response', lambda q: q.request.method != 'GET' and 'supabase' in q.url and print('->', q.status, q.text()[:300]))
    pg.locator('select').nth(1).select_option('lic-cul'); pg.wait_for_timeout(800)
    navb(pg, 'Cultivation').click(); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_selector('td >> text=PB-2026-021')
    pg.get_by_role('button', name='+ Plant batch').click(); md = pg.locator('.md')
    F(md, 'Cultivar / strain').fill('Blue Dream'); F(md, 'Plants').fill('36'); F(md, 'Lot (Receiving)').select_option('lt-cl2'); F(md, 'Starts in area').select_option('ga3')
    md.get_by_role('button', name='Save', exact=True).click(); pg.wait_for_timeout(1500)
    print(md.inner_text()[-300:] if md.count() else 'closed'); print([x['number'] for x in T['hx_plant_batches']])
    b.close()
