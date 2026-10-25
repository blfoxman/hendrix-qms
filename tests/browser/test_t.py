import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
TAG = '1A4000000000000000001234'
T['hx_skus'].append({'id':'ca1','state_id':'st-mo','product_type':'cartridges','name':'2G AIO','spec':{'oil_per_unit':2},'license_ids':[],'active':True,'sort':0})
T['hx_batches'] += [{'id':'b1','state_id':'st-mo','license_id':'lic-mo','batch_type':'cartridges','batch_number':'CART-100','sku_id':'ca1','sku':'2G AIO','flavor_id':None,'flavor':'Honey Melon','status':'In Progress','data':{'date':'2026-10-23','cart_packaged_metrc':TAG},'attachments':[],'performed_by':'Sam','created_at':'2026-10-23T10:00:00Z','updated_at':'2026-10-23T10:00:00Z','voided':False},
  {'id':'b2','state_id':'st-mo','license_id':'lic-mo','batch_type':'cartridges','batch_number':'CART-101','sku_id':'ca1','sku':'2G AIO','flavor_id':None,'flavor':'','status':'In Progress','data':{'date':'2026-10-23'},'attachments':[],'performed_by':'Sam','created_at':'2026-10-23T09:00:00Z','updated_at':'2026-10-23T09:00:00Z','voided':False}]
PDF = OUT + 'fake_coa.pdf'; open(PDF, 'wb').write(b'%PDF-1.4 fake coa')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_btype","cartridges");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('.card >> text=CART-100')
    check(pg.get_by_role('button', name='Submit for testing').count() == 1, 'Submit for testing only on batch with a final tag')
    pg.get_by_role('button', name='Submit for testing').click(); pg.wait_for_selector('.badge >> text=Test: Submitted')
    t = T['hx_tests'][0]
    check(t['tag'] == TAG and t['tag_label'] == 'Cart Packaged' and t['batch_number'] == 'CART-100' and t['status'] == 'Submitted', 'test record created from final tag')
    check(pg.get_by_role('button', name='Submit for testing').count() == 0, 'button gone after submit')
    nav = pg.locator('.nav button:not(.soon)').all_inner_texts()
    check('Testing' in nav, 'Testing in nav')
    pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=CART-100')
    check(pg.locator('.tabs button', has_text='Submitted (1)').count() == 1 and pg.locator('.badge', has_text='VAPES').count() == 1, 'status counts + category')
    pg.locator('label', has_text='Upload COA').locator('input').set_input_files(PDF)
    pg.wait_for_selector('.msg >> text=marked Passed', timeout=10000)
    t = T['hx_tests'][0]
    check(t['status'] == 'Passed' and t['result_thc'] == '88.4' and t['lab_license'] == 'TES000777' and t['coa_path'].startswith('coa/lic-mo/') and t['coa_filename'] == 'fake_coa.pdf', 'COA stored + read: Passed, THC, lab license')
    check(any(k.startswith('coa/lic-mo/') for k in STORE), 'file in private storage')
    pg.wait_for_selector('.barrow >> text=Total THC')
    check(pg.locator('.card .k', has_text='Heavy Metals').count() == 1 and pg.locator('.barrow', has_text='Limonene').count() == 1, 'analysis panel: potency, categories, terpenes')
    pg.screenshot(path=OUT + 'testing.png', full_page=True)
    # update final result needs reason
    pg.get_by_role('button', name='Update').click(); md = pg.locator('.md')
    field(md, 'Status').select_option('Retest')
    md.get_by_role('button', name='Save').click()
    check(md.locator('.msg.err', has_text='needs a reason').count() == 1, 'changing final result needs reason')
    field(md, 'Reason for changing').fill('Lab asked for a resample'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.md', state='detached')
    check(T['hx_tests'][0]['status'] == 'Retest', 'final result changed with reason')
    # mismatch
    pg.get_by_role('button', name='+ New test record').click(); md = pg.locator('.md'); pg.wait_for_selector('.md option >> text=CART-101', state='attached')
    field(md, 'Batch').select_option('b2')
    check(field(md, 'Package tag tested').get_attribute('placeholder') == 'This batch has no final package tag yet', 'warns when batch has no final tag')
    field(md, 'Package tag tested').fill('1A4000000000000000009999'); md.get_by_role('button', name='Create').click(); pg.wait_for_selector('.card >> text=CART-101')
    pg.locator('.card', has_text='CART-101').locator('label', has_text='Upload COA').locator('input').set_input_files(PDF)
    pg.wait_for_selector('.msg >> text=does not match', timeout=10000)
    t2 = next(x for x in T['hx_tests'] if x['batch_number'] == 'CART-101')
    check(t2['status'] == 'Pending' and 'Tag mismatch' in t2['result_notes'], 'mismatch keeps status, notes it')
    check(pg.locator('.card', has_text='CART-101').locator('.badge', has_text='Tag mismatch').count() == 1, 'mismatch badge')
    # AI not deployed
    AI['mode'] = 'missing'
    pg.locator('.card', has_text='CART-101').get_by_role('button', name='Re-read COA').click()
    pg.wait_for_selector('.msg >> text=AI reading is not set up yet', timeout=10000)
    check(True, 'clear message when hendrix-ai is not deployed')
    # member with view only
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'testing': 'read'}
    pg.reload(); pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=CART-100')
    check(pg.locator('label', has_text='Upload COA').count() == 0 and pg.get_by_role('button', name='Update').count() == 0 and pg.get_by_role('button', name='+ New test record').count() == 0 and pg.get_by_role('button', name='COA').count() == 2, 'View-only: sees records and COA, cannot change')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
sys.exit(1 if errors else 0)
