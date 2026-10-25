import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + '/../../kit')
import hxvideo as hv
from playwright.sync_api import sync_playwright
hv.set_project(HERE)
SNAP = HERE + '/../../index_snapshot2.html'
O = HERE + '/probe/'
ns = hv.load_setup('qual', snapshot=SNAP); ns['nowiso'] = hv.day_now
F = hv.field
with sync_playwright() as pw:
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(800)
    nav = lambda n: pg.locator('.nav').get_by_role('button', name=n, exact=True).click()
    def sh(n): pg.wait_for_timeout(500); pg.screenshot(path=O + n + '.png')
    def closeall():
        for _ in range(5):
            if not pg.locator('.mo').count(): return
            pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); pg.wait_for_timeout(200)
    # complaints
    nav('Complaints'); pg.wait_for_selector('text=Repeat complaints')
    pg.get_by_role('button', name='+ Log complaint').click(); md = pg.locator('.md')
    F(md, 'Type').select_option('dispensary'); F(md, 'Priority').select_option('major')
    F(md, 'Title').fill('Pre-roll boxes missing child-resistant seal'); F(md, 'Received by').select_option('Email'); F(md, 'Complainant').fill('Dev Patel (store manager)'); F(md, 'Contact').fill('dev@midtowncannabis.test')
    F(md, 'Customer (dispensary)').fill('Midtown Cannabis Co.'); F(md, 'Category').select_option('Hardware / packaging failure'); F(md, 'Batch').select_option('b-pr')
    F(md, 'Description').fill('4 of 30 boxes in the case arrived with the child-resistant seal not engaged.')
    sh('cmp_form1'); md.evaluate('e=>e.scrollTop=9999'); sh('cmp_form2')
    print([x.inner_text() for x in md.locator('button').all()])
    md.get_by_role('button', name='Log complaint').click(); pg.wait_for_timeout(800); sh('cmp_saved')
    md = pg.locator('.md').last
    print([x.inner_text() for x in md.locator('button').all()])
    print(md.inner_text()[:3000])
    md.evaluate('e=>e.scrollTop=700'); sh('cmp_saved2')
    closeall()
    # audits
    nav('Internal Audits'); pg.wait_for_selector('text=IA-2026-002')
    pg.locator('.tabs button', has_text='Annual program').click(); pg.wait_for_timeout(500); sh('ia_prog')
    pg.locator('.tabs button', has_text='Audits').click()
    pg.get_by_role('button', name='+ Plan audit').click(); md = pg.locator('.md'); sh('ia_form0')
    print(md.inner_text()[:2500])
    closeall()
    # sops
    nav('SOPs'); pg.wait_for_selector('.card >> text=Cart Filling and Capping'); pg.evaluate('scrollTo(0,0)'); sh('sops_top')
    pg.get_by_role('button', name='+ Manual SOP').click(); md = pg.locator('.md'); sh('sop_form0')
    print(md.inner_text()[:2500])
    closeall()
    pg.locator('.card', has_text='Cart Filling and Capping').first.click(); pg.wait_for_selector('.md'); sh('sop_cart')
    print([x.inner_text() for x in pg.locator('.md button').all()])
    closeall()
    # training
    nav('Training'); pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses', timeout=20000); sh('tr_created')
    pg.wait_for_selector('.card >> text=Online courses ready'); pg.get_by_role('button', name='Publish all').click(); pg.wait_for_selector('.msg >> text=/Published \\d+ online course/')
    print('courses', [c['name'] for c in ns['T']['hx_training_courses']])
    print('errs', errs)
    b.close()
