import os, sys, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE + '/../../kit')
import hxvideo as hv
from playwright.sync_api import sync_playwright
hv.set_project(HERE)
SNAP = HERE + '/../../index_snapshot2.html'
O = HERE + '/probe/'
ns = hv.load_setup('qual', snapshot=SNAP)
with sync_playwright() as pw:
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script())
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(800)
    nav = lambda n: pg.locator('.nav').get_by_role('button', name=n, exact=True).click()
    def sh(n): pg.wait_for_timeout(500); pg.screenshot(path=O + n + '.png')
    nav('QMS'); pg.wait_for_selector('text=Needs action'); sh('qms_dash')
    pg.locator('.tabs button', has_text='Deviations').click(); pg.wait_for_timeout(300); sh('qms_devs')
    pg.locator('.card', has_text='DEV-2026-007').first.click(); pg.wait_for_selector('.md'); sh('dev7')
    print([x.inner_text() for x in pg.locator('.md button').all()])
    pg.locator('.md').get_by_role('button', name='Close deviation').first.click(); pg.wait_for_timeout(400); sh('dev7_close')
    pg.locator('.md').last.get_by_role('button', name='Cancel').click(); pg.wait_for_timeout(300)
    pg.locator('.md').last.get_by_role('button', name='Close', exact=True).click(); pg.wait_for_timeout(300)
    nav('Complaints'); pg.wait_for_selector('text=Repeat complaints'); sh('cmp_list')
    nav('Internal Audits'); pg.wait_for_selector('text=IA-2026-002'); sh('ia_list')
    pg.locator('.card', has_text='IA-2026-002').first.click(); pg.wait_for_selector('.md'); sh('ia2')
    print([x.inner_text() for x in pg.locator('.md button').all()])
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    while pg.locator('.mo').count(): pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); pg.wait_for_timeout(200)
    nav('SOPs'); pg.wait_for_selector('.card >> text=Cart Filling and Capping'); sh('sops')
    nav('Training'); pg.wait_for_timeout(3000); sh('training0')
    print('errs', errs)
    b.close()
