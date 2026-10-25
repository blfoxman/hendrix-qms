import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
T['hx_skus'] += [{'id':'pr2g','state_id':'st-mo','product_type':'pre_rolls','name':'Muha Meds 2G Infused Pre Roll','spec':{},'license_ids':[],'active':True,'sort':0},
                 {'id':'sh','state_id':'st-mo','product_type':'pre_rolls','name':'Bodega Boyz - Shorties','spec':{},'license_ids':[],'active':True,'sort':1}]
T['hx_flavors'] += [{'id':'fbp','state_id':'st-mo','sku_id':'pr2g','name':'Banana Pie','active':True,'sort':0},{'id':'fhm','state_id':'st-mo','sku_id':'pr2g','name':'Honey Melon','active':True,'sort':1},
                    {'id':'fsa','state_id':'st-mo','sku_id':'sh','name':'Sour Apple','active':True,'sort':0}]
coa = {'lab_name':'Green Lab','lab_license_number':'TES000777','report_date':'2026-10-20','sample_metrc_tag':'1A4000000000000000005555','overall_status':'Pass',
       'potency':{'unit':'%','d9_thc':1.1,'thca':42.5,'cbd':0.05,'cbn':0.2}}
T['hx_tests'] += [{'id':'tb','state_id':'st-mo','license_id':'lic-mo','batch_id':None,'batch_number':'PR-777','batch_type':'pre_rolls','sku':'Muha Meds 2G Infused Pre Roll','flavor':'Banana Pie','tag':'1A4000000000000000004444','tag_label':'Final Packaged',
   'sample_tag':'1A4000000000000000005555','lab_name':'Green Lab','lab_license':'TES000777','status':'Passed','result_at':'2026-10-20T00:00:00Z','result_thc':'','result_cbd':'','result_notes':'','notes':'','coa_path':'coa/x.pdf','coa_filename':'x.pdf','coa_analysis':coa,'voided':False,'created_at':'2026-10-20T00:00:00Z'},
  {'id':'ts','state_id':'st-mo','license_id':'lic-mo','batch_id':None,'batch_number':'SH-12','batch_type':'pre_rolls','sku':'Bodega Boyz - Shorties','flavor':'Sour Apple','tag':'1A40000000000000000077','tag_label':'Final Packaged',
   'sample_tag':'1A40000000000000000078','lab_name':'Green Lab','lab_license':'TES000777','status':'Passed','result_at':'2026-10-20T00:00:00Z','result_thc':'','result_cbd':'','result_notes':'','notes':'','coa_path':'coa/y.pdf','coa_filename':'y.pdf','coa_analysis':coa,'voided':False,'created_at':'2026-10-19T00:00:00Z'}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.get_by_role('button', name='Compliance Stickers').click(); pg.wait_for_selector('text=No label templates')
    check(pg.evaluate('!!window.jspdf'), 'jsPDF loaded')
    pg.get_by_role('button', name='Import Black Fox templates').click(); pg.wait_for_selector('.msg >> text=Imported')
    txt = pg.locator('.msg').inner_text()
    check(len(T['hx_label_templates']) == 3 and 'Imported 3' in txt and 'Skipped' in txt, 'imported only matching SKUs/flavors: ' + txt[:140])
    sa = next(t for t in T['hx_label_templates'] if t['flavor_id'] == 'fsa')
    check(sa['layout'] == 'tri' and sa['approval_number'] == 'M00002448284' and len(sa['ingredients']) > 100, 'Shorties template keeps three-column layout + approval + ingredients')
    pg.get_by_role('button', name='Import Black Fox templates').click(); pg.wait_for_selector('.msg >> text=Imported 0')
    check(len(T['hx_label_templates']) == 3, 'import again adds nothing')
    pg.get_by_role('button', name='+ New template').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option('pr2g'); field(md, 'Flavor').select_option('fbp')
    md.get_by_role('button', name='Save template').click(); pg.wait_for_timeout(600)
    check(md.locator('.msg.err', has_text='already has a template').count() == 1, 'duplicate template refused')
    md.get_by_role('button', name='Cancel').click()
    pg.screenshot(path=OUT + 'stickers_page.png', full_page=True)
    # print from Testing
    pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=PR-777')
    pg.locator('.card', has_text='PR-777').get_by_role('button', name='Compliance Sticker').click()
    md = pg.locator('.md'); pg.wait_for_selector('.md iframe')
    check(field(md, 'Template').locator('option:checked').inner_text().endswith('Banana Pie'), 'auto-picked Banana Pie template')
    check(md.locator('.msg.err', has_text='Missing on this label').count() == 0, 'nothing missing')
    with pg.expect_download() as di: md.get_by_role('button', name='Download PDF').click()
    di.value.save_as(OUT + 'labels_std.pdf')
    with pg.expect_download() as di2: md.get_by_role('button', name='Alignment test sheet').click()
    di2.value.save_as(OUT + 'labels_align.pdf')
    pg.screenshot(path=OUT + 'sticker_modal.png')
    md.get_by_role('button', name='×').click() if md.get_by_role('button', name='×').count() else pg.mouse.click(5, 5)
    pg.locator('.card', has_text='SH-12').get_by_role('button', name='Compliance Sticker').click(); pg.wait_for_selector('.md iframe')
    with pg.expect_download() as di3: pg.locator('.md').get_by_role('button', name='Download PDF').click()
    di3.value.save_as(OUT + 'labels_tri.pdf')
    # access: View can print, cannot edit templates
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'stickers': 'read', 'testing': 'read'}
    pg.reload(); pg.get_by_role('button', name='Compliance Stickers').click(); pg.wait_for_selector('.card >> text=Banana Pie')
    check(pg.get_by_role('button', name='+ New template').count() == 0 and pg.get_by_role('button', name='Edit').count() == 0, 'View: no template editing')
    pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=PR-777')
    check(pg.locator('.card', has_text='PR-777').get_by_role('button', name='Compliance Sticker').count() == 1, 'View: can still print stickers')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
