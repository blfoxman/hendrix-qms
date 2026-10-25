from common import *
from playwright.sync_api import sync_playwright
O = HERE + '/work/probe/'; os.makedirs(O, exist_ok=True)
ns = load_found()
audit_rows(ns)
errs = []
def sh(pg, n, full=False): pg.wait_for_timeout(500); pg.screenshot(path=O + n + '.png', full_page=full)
with sync_playwright() as pw:
    b = hv.launch(pw)
    ctx, pg = open_app(b, ns)
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # Settings
    nav(pg, 'Settings').click(); pg.wait_for_selector('text=Business details on printouts'); sh(pg, 'h_set'); sh(pg, 'h_set_full', True)
    pg.get_by_role('button', name='Line Map', exact=True).last.click(); pg.wait_for_timeout(300); sh(pg, 'h_lm')
    pg.locator('input[aria-label="Hours without an update"]').fill('0'); pg.get_by_role('button', name='Save settings').click(); pg.wait_for_timeout(500); sh(pg, 'h_lm_err')
    pg.locator('input[aria-label="Hours without an update"]').fill('6'); pg.get_by_role('button', name='Save settings').click(); pg.wait_for_timeout(800); sh(pg, 'h_lm_ok')
    print('settings', ns['T']['hx_license_settings'])
    pg.get_by_role('button', name='Facility logs', exact=True).click(); pg.wait_for_timeout(300); sh(pg, 'h_logs')
    pg.get_by_role('button', name='Everything else').click(); pg.wait_for_timeout(300); sh(pg, 'h_more')
    # Import
    nav(pg, 'Import (Excel / Sheets)').click(); pg.wait_for_selector('text=1. What are you importing?'); sh(pg, 'i_imp')
    pg.locator('button.card', has_text='Equipment').click(); pg.wait_for_timeout(300); sh(pg, 'i_imp2')
    pg.locator('input[type=file]').set_input_files(SCR + 'import_eq.xlsx'); pg.wait_for_selector('text=import_eq.xlsx'); sh(pg, 'i_file'); sh(pg, 'i_file_full', True)
    pg.get_by_role('button', name='Match with AI').click(); pg.wait_for_selector('text=Columns matched by the AI'); sh(pg, 'i_ai', True)
    pg.get_by_role('button', name='Import 2 rows').click(); pg.wait_for_selector('text=Imported 2.'); sh(pg, 'i_done')
    # Audit
    nav(pg, 'Audit Trail').click(); pg.wait_for_timeout(1200); sh(pg, 'j_audit')
    print('errs', errs)
    b.close()
