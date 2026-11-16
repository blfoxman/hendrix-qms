# Infused flower stickers on Avery 94107 (2" x 2" square, 12 per sheet): sheet geometry, default for infused flower SKUs, one-click move of old templates
import re
import os
import subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
T['hx_skus'] += [{'id': 'if7', 'state_id': 'st-mo', 'product_type': 'infused_flower', 'name': 'Infused Flower 3.5G', 'spec': {}, 'license_ids': [], 'active': True, 'sort': 0},
                 {'id': 'pr2', 'state_id': 'st-mo', 'product_type': 'pre_rolls', 'name': 'Infused Pre Roll 2G', 'spec': {}, 'license_ids': [], 'active': True, 'sort': 1}]
T['hx_flavors'] += [{'id': 'fb', 'state_id': 'st-mo', 'sku_id': 'if7', 'name': 'Banana Pie', 'active': True, 'sort': 0}]
coa = {'lab_name': 'Green Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-11-10', 'overall_status': 'Pass', 'potency': {'unit': '%', 'd9_thc': 0.8, 'thca': 52.0, 'cbd': '<LOQ', 'cbn': 'ND'}}
T['hx_tests'] += [{'id': 'ti', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': None, 'batch_number': 'IF-77', 'batch_type': 'infused_flower', 'sku': 'Infused Flower 3.5G', 'flavor': 'Banana Pie', 'tag': '1A4000000000000000007777', 'tag_label': 'Packaged METRC Tag',
  'sample_tag': '1A4000000000000000007778', 'lab_name': 'Green Lab', 'lab_license': 'TES000777', 'status': 'Passed', 'result_at': '2026-11-10T00:00:00Z', 'result_thc': '', 'result_cbd': '', 'result_notes': '', 'notes': '', 'coa_path': 'coa/i.pdf', 'coa_filename': 'i.pdf', 'coa_analysis': coa, 'voided': False, 'created_at': '2026-11-10T00:00:00Z',
  'retention_qty': '', 'retention_location': '', 'retention_until': None}]
T['hx_label_templates'] += [{'id': 'lti', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'if7', 'flavor_id': None, 'name': 'Infused Flower 3.5G', 'stock': 'avery-94202', 'layout': 'tri', 'approval_number': 'M0077', 'servings': '1', 'weight': '3.5g',
  'instructions': 'Heat flower, inhale smoke. Effects may last up to 4 hours.', 'ingredients': 'Cannabis flower, distillate, terpenes', 'allergens': '', 'warning': 'For use only by adults 21 and older.', 'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    pg.get_by_role('button', name='Compliance Stickers').click(); pg.wait_for_selector('text=Infused Flower 3.5G')
    # old infused flower template on the 1" x 4" sheet: one click moves it
    pg.get_by_role('button', name='Infused flower → 2" x 2" (1)').click(); pg.wait_for_selector('.msg >> text=now prints on Avery 94107')
    t = T['hx_label_templates'][-1]
    check(t['stock'] == 'avery-94107' and t['layout'] == '' and pg.locator('.msg.ok').count() == 1, 'infused flower template moved to Avery 94107 (standard layout)')
    check(pg.locator('.card', has_text='Infused Flower 3.5G').locator('text=2" x 2"').count() == 1 and pg.get_by_role('button', name=re.compile('Infused flower')).count() == 0, 'card shows 2" x 2"; button gone when none are left')
    # new template: an infused flower SKU picks the square sheet, a pre-roll SKU keeps 1" x 4"
    pg.get_by_role('button', name='+ New template').click(); md = pg.locator('.md')
    field(md, 'SKU *').select_option('pr2'); check(field(md, 'Label sheet').input_value() == 'avery-94202', 'pre-roll SKU: 1" x 4" sheet')
    field(md, 'SKU *').select_option('if7'); check(field(md, 'Label sheet').input_value() == 'avery-94107', 'infused flower SKU: Avery 94107 2" x 2"')
    md.get_by_role('button', name='Cancel').click()
    # print from the Testing record: one sheet = 12, laid out 3 x 4 at the Avery positions
    pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=IF-77')
    pg.locator('.card', has_text='IF-77').get_by_role('button', name='Compliance Sticker').click(); pg.wait_for_selector('.md iframe')
    md = pg.locator('.md')
    check(field(md, 'Labels to print').input_value() == '12' and md.locator('text=Avery 94107').count() >= 1, 'sticker print: one full sheet is 12 labels on Avery 94107')
    with pg.expect_download() as di: md.get_by_role('button', name='Download PDF').click()
    di.value.save_as(OUT + 'labels_94107.pdf')
    bb = subprocess.run(['pdftotext', '-bbox', OUT + 'labels_94107.pdf', '-'], capture_output=True, text=True).stdout
    pages = bb.count('<page ')
    words = [{'x0': float(m.group(1)), 'top': float(m.group(2)), 'h': float(m.group(4)) - float(m.group(2)), 'text': m.group(5)}
             for m in re.finditer(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', bb.split('</page>')[0])]
    fit = round(min(w['h'] for w in words if w['text'].strip()) / 1.15, 1)   # glyph box height is about 1.15 x the font size
    starts = sorted({(round(w['x0']), round(w['top'])) for w in words if w['text'].startswith('Active')})
    xs = sorted({x for x, y in starts}); ys = sorted({y for x, y in starts})
    check(pages == 1 and len(starts) == 12 and len(xs) == 3 and len(ys) == 4, '12 labels on one page, 3 across and 4 down: %d / %s / %s' % (pages, xs, ys))
    check(abs(xs[0] - (0.625 * 72 + 6)) <= 2 and abs((xs[1] - xs[0]) - 2.625 * 72) <= 2 and abs((ys[1] - ys[0]) - 2.6 * 72) <= 2 and abs(ys[0] - (0.6 * 72 + 6)) <= 6, 'positions match Avery 94107: side 0.625", top 0.6", pitch 2.625" x 2.6"')
    txt = re.sub(r'\s+', ' ', subprocess.run(['pdftotext', OUT + 'labels_94107.pdf', '-'], capture_output=True, text=True).stdout)
    check('WARNING' in txt and 'M0077' in txt and 'CANNABINOID PROFILE' in txt, 'the whole compliance text fits on the square label')
    check(fit and fit >= 2.8, 'text size on the 2" x 2" label: %s pt' % fit)
    pg.screenshot(path=OUT + 'labels_94107.png')
    subprocess.run(['pdftoppm', '-r', '110', '-png', '-singlefile', OUT + 'labels_94107.pdf', OUT + 'labels_94107_page'])
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
