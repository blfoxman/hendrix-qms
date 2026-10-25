from common import *
from playwright.sync_api import sync_playwright
O = HERE + '/work/probe/'; os.makedirs(O, exist_ok=True)
ns = load_found()
errs = []
def sh(pg, n, full=False): pg.wait_for_timeout(500); pg.screenshot(path=O + n + '.png', full_page=full)
def clause_row(pg, num): return pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(num) + '$'))).first
with sync_playwright() as pw:
    b = hv.launch(pw)
    ctx, pg = open_app(b, ns)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    nav(pg, 'Missouri Rulebook').click(); pg.wait_for_selector('text=Upload rules PDF'); sh(pg, 'd_rb0')
    pg.locator('label', has_text='Upload rules PDF').locator('input[type=file]').set_input_files(SCR + 'rbpdf/mo.pdf')
    pg.wait_for_selector('text=7 rules found', timeout=30000); sh(pg, 'd_rb_review')
    md = pg.locator('.md')
    print('review btns', [x.inner_text()[:40] for x in md.locator('button').all()][:40])
    md.get_by_role('button', name='Import 7 rules').click(); pg.wait_for_selector('.msg >> text=Imported from mo.pdf', timeout=20000); sh(pg, 'd_rb_imported')
    pg.get_by_role('button', name='+ Add rule').click(); md = pg.locator('.md'); pg.wait_for_timeout(300); sh(pg, 'd_rb_add')
    md.get_by_role('button', name='Cancel').click()
    # Standards fresh
    nav(pg, 'Standards (CSQ)').click(); pg.wait_for_selector('text=No standard added yet'); sh(pg, 'e_std0')
    pg.get_by_role('button', name=re.compile('^Add CSQ Standard')).click(); pg.wait_for_selector('.msg >> text=Added'); sh(pg, 'e_std_added')
    pg.get_by_role('button', name='Adopt for this license').click(); md = pg.locator('.md'); pg.wait_for_timeout(300); sh(pg, 'e_adopt')
    print('adopt fields', [x.inner_text()[:50] for x in md.locator('label.f, div.f').all()])
    field(md, 'Target level').select_option('2'); field(md, 'Status').select_option('Audit scheduled'); field(md, 'Certification body').fill('Kiwa ASI')
    field(md, 'Audit date').fill('2026-12-08'); sh(pg, 'e_adopt2')
    md.get_by_role('button', name='Adopt standard').click(); pg.wait_for_selector('text=0% complete'); sh(pg, 'e_adopted'); sh(pg, 'e_adopted_full', True)
    r = clause_row(pg, '1.4'); r.locator('div.row').first.click(); pg.wait_for_timeout(500); sh(pg, 'e_c14')
    r.get_by_role('button', name='Record conformance').click(); md = pg.locator('.md')
    field(md, 'Status').select_option('Not applicable'); md.get_by_role('button', name='Save').click(); pg.wait_for_timeout(600); sh(pg, 'e_na_err')
    field(md, 'Status').select_option('Conforming'); sh(pg, 'e_conf')
    print('errs', errs)
    b.close()
