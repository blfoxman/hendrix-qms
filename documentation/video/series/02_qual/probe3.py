import make, hxvideo as hv
from playwright.sync_api import sync_playwright
import json
with sync_playwright() as pw:
    ns = make.setup(); T = ns['T']; h0 = ns['handle']
    def handle(route, request):
        if request.method != 'GET' and 'supabase' in request.url:
            print(request.method, request.url[-90:], (request.post_data or '')[:400])
        return h0(route, request)
    ns['handle'] = handle
    b, ctx, pg = make.open_app(pw, ns); make.training_seed(ns, pg)
    make.navb(pg, 'Training').click(); pg.wait_for_selector('td >> text=Tess Whitaker')
    pg.get_by_role('button', name='+ Record training').click(); md = pg.locator('.md')
    make.F(md, 'Course').select_option(label='Current Good Manufacturing Practices (cGMP)')
    md.locator('label.ck', has_text='Ana Morales').locator('input').click()
    make.F(md, 'Trainer').fill('Dana Brooks'); make.F(md, 'Assessment').select_option('Passed')
    md.get_by_role('button', name='Save record').click(); pg.wait_for_timeout(1000); print('msg', pg.locator('.msg, .err').all_inner_texts())
    pg.locator('.tabs button', has_text='Records').click(); pg.wait_for_timeout(800)
    print(len(T['hx_training_records']))
    print(T['hx_training_records'][-1])
    b.close()
