# Screenshots of each page with the full seed, at the recording viewport.
from common import *
from playwright.sync_api import sync_playwright
ns = setup(); seed_all(ns)
pages = [('HACCP', 'td >> text=HP-002'), ('Risk Register', 'text=Heat map (current rating)'), ('Change Control', 'td >> text=CC-2026-003'), ('Org Chart', '.card svg rect'),
         ('Quality Objectives', 'text=SOP-QA-001'), ('Management Review', 'td >> text=MR-2025-001'), ('Verification Schedule', 'td >> text=VS-013')]
os.makedirs(HERE + '/work/probe', exist_ok=True)
with sync_playwright() as pw:
    b = hv.launch(pw); ctx = hv.new_context(b, ns, session=hv.session_script(extra='localStorage.setItem("hx_hptab","plans");'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(500)
    for i, (n, w) in enumerate(pages):
        menu(pg, n).click(); pg.wait_for_selector(w); pg.wait_for_timeout(800)
        pg.screenshot(path=HERE + '/work/probe/p%d.png' % i)
        pg.screenshot(path=HERE + '/work/probe/p%d_full.png' % i, full_page=True)
    b.close()
print(errs)
