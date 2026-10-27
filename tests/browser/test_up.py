import os, re, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# 1) SOP PDF: procedure text stays inside the page, also after critical steps and regulation notes
# 2) an open page notices a newer published Hendrix (bar with Reload; kiosks reload by themselves when idle)
errors = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
STEPS = [
 ('Line Clearance and Area Verification', 'Verify the filling station is clean, sanitized, and free of materials from any previous batch or product. Have a second employee verify and sign the line clearance checklist before starting.', 'Line clearance prevents cross-contamination and product mix-ups (cGMP; CSQ Standard).', True),
 ('Material and Batch Verification', 'Confirm the oil batch/lot number, METRC package tag, and COA status against the production order. Verify that the Bodega Boyz 2g devices and components match the work order and have been inspected for defects.', 'Only tested, released oil with a passing COA may be used; the package must be traceable in METRC.', True),
 ('Equipment Calibration and Setup', 'Check that the scale and filling equipment are calibrated, clean, and within calibration dates. Set the filling equipment to the target 2g fill weight and verify with a test weight or check unit.', 'Uncalibrated equipment may produce inaccurate fill weights and label claim violations.', True),
 ('Oil Preparation', 'Heat the oil to the validated temperature range and mix it until it is homogeneous and flows consistently. Do not exceed the approved temperature or time limits.', '', False),
 ('Fill Devices', 'Fill each device to the target 2g weight using the calibrated equipment, with the operator wearing clean PPE (gloves, hairnet, lab coat). Avoid contact with the mouthpiece and air channels, and wipe off any spilled oil.', '', False)]
GEN = {'title': 'Filling Bodega Boyz 2g Devices', 'purpose': 'Fill devices consistently.', 'required_materials': ['Quarantine bins/trays with status labels'],
       'steps': [{'step_number': i + 1, 'title': a, 'instruction': b, 'regulatory_note': c, 'critical': d} for i, (a, b, c, d) in enumerate(STEPS)]}
T['hx_sops'].append({'id': 'sop-up', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Fill Bodega', 'sop_number': 'SOP-PRD-010', 'version': '1.0', 'status': 'published',
    'folder': 'Production', 'category': '', 'created_by': 'Sam', 'created_at': '2026-10-01T00:00:00Z', 'updated_at': '2026-10-01T00:00:00Z', 'approved_by': 'Sam', 'approved_at': '2026-10-01T00:00:00Z',
    'effective_date': '2026-10-01', 'next_review': '2027-10-01', 'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'attachments': [], 'steps': [], 'revision_note': '', 'generated_content': GEN})
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    pg.get_by_role('button', name='SOPs', exact=True).click(); pg.locator('.card', has_text='Fill Bodega').first.click(); pg.wait_for_selector('.md')
    with pg.expect_download() as di: pg.get_by_role('button', name='📄 Download PDF').click()
    di.value.save_as(OUT + 'sop_width.pdf')
    bb = subprocess.run(['pdftotext', '-bbox', OUT + 'sop_width.pdf', '-'], capture_output=True, text=True).stdout
    words = re.findall(r'xMax="([\d.]+)"[^>]*>([^<]*)</word>', bb)
    over = [(w, x) for x, w in words if float(x) > 565]   # right margin: 612 - 48
    check(len(words) > 100 and not over, 'SOP PDF: no text past the right margin after critical steps and notes %s' % over[:5])
    txt = subprocess.run(['pdftotext', OUT + 'sop_width.pdf', '-'], capture_output=True, text=True).stdout
    check('inspected for defects' in txt and 'time limits' in txt, 'SOP PDF: every step printed in full')
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5)
    # new version check
    pg.evaluate('window.hxUpdateCheckNow()'); pg.wait_for_timeout(400)
    check(pg.locator('#hx-update').count() == 0, 'same version published: no bar')
    HTML_OLD = HTML; HTML = re.sub(r"const HX_RELEASE='[^']*'", "const HX_RELEASE='Release 99'", HTML)
    pg.evaluate('window.hxUpdateCheckNow()'); pg.wait_for_selector('#hx-update')
    check('newer version of Hendrix' in pg.locator('#hx-update').inner_text(), 'newer version published: bar asks to save and reload')
    pg.locator('#hx-update').get_by_role('button', name='Later').click()
    check(pg.locator('#hx-update').count() == 0, 'Later hides the bar')
    pg.locator('.nav').get_by_role('button', name='SOPs', exact=True).click(); pg.evaluate('window.hxUpdateCheckNow()'); pg.wait_for_selector('#hx-update')
    pg.locator('#hx-update').get_by_role('button', name='Reload').click(); pg.wait_for_selector('text=Dashboard')
    check(pg.locator('#hx-update').count() == 0 and 'Release 99' in pg.content(), 'Reload opens the newer version')
    ctx.close()
    # kiosk: no bar; reloads by itself once nobody has touched it for 2 minutes
    HTML_NEW = HTML; HTML = HTML_OLD
    ctx = b.new_context(viewport={'width': 900, 'height': 900}); ctx.route('**/*', handle)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.clock.install(); pg.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); pg.wait_for_selector('text=Scan your badge')
    HTML = HTML_NEW; pg.evaluate('window.hxUpdateCheckNow()'); pg.wait_for_timeout(400)
    check(pg.locator('#hx-update').count() == 0, 'kiosk: no bar')
    pg.clock.fast_forward(60000); pg.wait_for_timeout(300)
    check('Release 99' not in pg.content(), 'kiosk: not reloaded while recently used')
    with pg.expect_navigation(): pg.clock.fast_forward(100000)
    pg.wait_for_selector('text=Scan your badge')
    check(pg.evaluate('document.documentElement.innerHTML.indexOf("Release 99")>=0'), 'kiosk: reloaded to the newer version when idle')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
