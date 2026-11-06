import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
import re
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label, exact=False):
    pgx = md if hasattr(md, 'goto') else md.page
    sp = pgx.locator('span', has_text=re.compile('^' + re.escape(label) + ('$' if exact else ''))) 
    return md.locator('label.f, div.f', has=sp).locator('input,select,textarea').first
T['hx_lots'] = [{'id': 'lot1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-001', 'item': 'Flower OG', 'category': 'Cannabis', 'metrc_tag': '1A40C03000060E1000003275', 'supplier_lot': '', 'unit': 'g', 'quantity': 1240, 'qty_used': 0, 'status': 'accepted', 'received_on': '2026-11-01', 'expiry_date': None},
                {'id': 'lot2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'number': 'RCV-2026-002', 'item': 'Flower GSC', 'category': 'Cannabis', 'metrc_tag': '1A40C03000060E1000004411', 'supplier_lot': '', 'unit': 'kg', 'quantity': 2, 'qty_used': 0, 'status': 'accepted', 'received_on': '2026-11-02', 'expiry_date': None}]
T['hx_lot_uses'] = []
_hb = handle
def handle(route, request):
    u = request.url
    if '/rest/v1/rpc/hx_batch_lots' in u:
        return route.fulfill(status=200, content_type='application/json', body=json.dumps([{**l, 'qty_left': l['quantity'] - l['qty_used']} for l in T['hx_lots'] if l['status'] == 'accepted' and l['quantity'] - l['qty_used'] > 0]))
    if '/rest/v1/hx_lot_uses' in u and request.method == 'POST':
        b = json.loads(request.post_data); l = next(x for x in T['hx_lots'] if x['id'] == b['lot_id'])
        if b['quantity'] > l['quantity'] - l['qty_used']: return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'Only %s %s left in lot %s.' % (l['quantity'] - l['qty_used'], l['unit'], l['number'])}))
        l['qty_used'] += b['quantity']; b['voided'] = False; T['hx_lot_uses'].append(b)
        return route.fulfill(status=201, content_type='application/json', body=json.dumps([b]))
    if '/rest/v1/hx_lot_uses' in u:
        return route.fulfill(status=200, content_type='application/json', body=json.dumps(T['hx_lot_uses']))
    return _hb(route, request)
T['hx_states'][0]['tracking_system'] = 'METRC'; T['hx_states'][1]['tracking_system'] = 'BioTrack'
T['hx_skus'] += [
 {'id':'pr1','state_id':'st-mo','product_type':'pre_rolls','name':'Mates THCA 5 x 0.6g','spec':{'grams_filled':0.55,'grams_kiefed':0.6,'units_per_package':5,'ingredients':['THCA','Terpene'],'coating':'Kief'},'license_ids':[],'active':True,'sort':0},
 {'id':'pr2','state_id':'st-mo','product_type':'pre_rolls','name':'Off SKU','spec':{},'license_ids':[],'active':False,'sort':1},
 {'id':'bh1','state_id':'st-mo','product_type':'butane_extraction','name':'THCA/HTE','spec':{'dual':'Yes'},'license_ids':[],'active':True,'sort':0},
 {'id':'ca1','state_id':'st-mo','product_type':'cartridges','name':'2G AIO','spec':{'oil_per_unit':2},'license_ids':[],'active':True,'sort':0},
 {'id':'if1','state_id':'st-mo','product_type':'infused_flower','name':'Infused Flower 3.5g','spec':{'unit_size':3.5},'license_ids':[],'active':True,'sort':0},
 {'id':'if7','state_id':'st-mo','product_type':'infused_flower','name':'Infused Flower 7G','spec':{},'license_ids':[],'active':True,'sort':1}]
T['hx_flavors'] += [{'id':'fl1','state_id':'st-mo','sku_id':'pr1','name':'Berry Blast','active':True,'sort':0},{'id':'fl2','state_id':'st-mo','sku_id':'pr1','name':'Honey Melon','active':True,'sort':1}]
T['hx_formulations'] += [{'id':'fo1','state_id':'st-mo','sku_id':'pr1','flavor_id':None,'name':'Mates base','batch_size':'1000','raw_materials':[{'name':'Flower','qty':'1000','unit':'g'},{'name':'THCA','qty':'200','unit':'g'}],'packaging':[],'labor':[],'notes':''}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_btype","pre_rolls");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('h1 >> text=Tracker')
    check(pg.locator('.tabs button').count() == 8, '8 batch types')
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    opts = field(md, 'SKU').locator('option').all_inner_texts()
    check('Mates THCA 5 x 0.6g' in opts and 'Off SKU' not in opts, 'only switched-on SKUs offered')
    field(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); field(md, 'Flavor').select_option(label='Honey Melon')
    check(md.locator('text=Formulation — Mates base').count() == 1, 'formulation card shown to admin')
    check(field(md, 'THCA Used').count() == 1 and field(md, 'Terpene Used').count() == 1 and md.locator('span', has_text='Live Resin Used').count() == 0, 'only the SKU ingredients shown')
    check(md.locator('span', has_text='Mandatory Testing').count() == 0 and md.locator('span', has_text='R&D 2').count() == 0, 'mandatory testing + R&D 2 hidden until R&D 1')
    field(md, 'Batch / Lot Number').fill('PR-001')
    field(md, 'Flower Used').fill('1000'); field(md, 'THCA Used').fill('200'); field(md, 'Terpene Used').fill('40'); field(md, 'Infused Flower Total WT').fill('1240')
    field(md, 'Infused Flower Used').fill('550'); field(md, 'Total Joint Filled').fill('1000')
    field(md, 'Total Kiefed Infused Joints').fill('920'); field(md, 'Kiefed Infused Joints Used').fill('900'); field(md, 'Total Jar Packaged').fill('180')
    chks = md.locator('.chkp.ok').count()
    check(chks == 4, '4 system checks PASS (flower, joints, kiefed, packaging): %d' % chks)
    field(md, 'Total Jar Packaged').fill('230')
    check(md.locator('.chkp.bad', has_text='UNDER WEIGHT').count() == 1, 'too many jars = under weight')
    field(md, 'Total Jar Packaged').fill('180')
    md.locator('div.f', has=pg.locator('span', has_text='R&D 1')).get_by_role('button', name='Failed').click()
    check(md.locator('span', has_text='R&D 2').count() == 1, 'R&D 2 appears after R&D 1 failed')
    md.locator('div.f', has=pg.locator('span', has_text='R&D 2')).get_by_role('button', name='Passed').click()
    check(md.locator('span', has_text='Mandatory Testing').count() == 1, 'mandatory testing after R&D passed')
    md.locator('label.ck', has_text='Recorded on METRC?').first.locator('input').check()
    md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=PR-001')
    bt = T['hx_batches'][-1]
    check(bt['sku'] == 'Mates THCA 5 x 0.6g' and bt['flavor'] == 'Honey Melon' and bt['data']['joints_check_status'] == 'pass' and bt['data']['packaging_check_expected'] == '180', 'batch saved with checks + names from DB')
    check(pg.locator('.badge', has_text='METRC 1/').count() == 1, 'METRC x/y badge')
    pg.screenshot(path=OUT + 'batches.png', full_page=True)
    # pick the flower tag from Receiving inventory: type the last digits, pick the lot, the amount used is deducted
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); field(md, 'Batch / Lot Number').fill('PR-002')
    field(md, 'Flower METRC #').fill('3275'); pg.wait_for_selector('.lotopt')
    check(md.locator('.lotopt').count() == 1 and '1240 g left' in md.locator('.lotopt').inner_text(), 'typing the last 4 digits lists the matching lot with what is left')
    md.locator('.lotopt').first.click()
    check(field(md, 'Flower METRC #').input_value() == '1A40C03000060E1000003275' and md.locator('text=From inventory: RCV-2026-001').count() == 1, 'picking fills the full tag and links the lot')
    field(md, 'Flower Used').fill('5000'); md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_timeout(400)
    check('Only 1240 g left in 1A40C03000060E1000003275' in md.locator('.msg.err').inner_text() and not any(b['batch_number'] == 'PR-002' for b in T['hx_batches']), 'more than is left: refused before saving')
    field(md, 'Flower Used').fill('1,000g'); md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=PR-002')
    pb = next(b for b in T['hx_batches'] if b['batch_number'] == 'PR-002'); us = [x for x in T['hx_lot_uses'] if x['batch_id'] == pb['id']]
    check(len(us) == 1 and us[0]['lot_id'] == 'lot1' and us[0]['quantity'] == 1000 and '[bt:flower_qty]' in us[0]['notes'] and T['hx_lots'][0]['qty_used'] == 1000, 'saved: 1,000 g recorded against the lot and the batch (240 g left)')
    # a kg lot: grams typed in the batch are converted
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); field(md, 'Batch / Lot Number').fill('PR-003')
    field(md, 'Flower METRC #').fill('4411'); pg.wait_for_selector('.lotopt'); md.locator('.lotopt').first.click()
    field(md, 'Flower Used').fill('500'); md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=PR-003')
    pb = next(b for b in T['hx_batches'] if b['batch_number'] == 'PR-003'); us = [x for x in T['hx_lot_uses'] if x['batch_id'] == pb['id']]
    check(len(us) == 1 and us[0]['quantity'] == 0.5, '500 g from a kg lot = 0.5 kg deducted')
    # a tag that is not in Receiving: saved, nothing deducted
    n_uses = len(T['hx_lot_uses'])
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); field(md, 'Batch / Lot Number').fill('PR-004')
    field(md, 'Flower METRC #').fill('1A40ZZZZ0000'); check(md.locator('text=Not in Receiving inventory').count() == 1, 'unknown tag: told nothing will be deducted')
    field(md, 'Flower Used').fill('100'); md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=PR-004')
    check(len(T['hx_lot_uses']) == n_uses, 'unknown tag: batch saved, no use recorded')
    T['hx_batches'][:] = [b for b in T['hx_batches'] if b['batch_number'] not in ('PR-002', 'PR-003', 'PR-004')]
    pg.reload(); pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('.card >> text=PR-001')
    # duplicate number
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Mates THCA 5 x 0.6g'); field(md, 'Batch / Lot Number').fill(' pr-001')
    md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.md .msg.err')
    check('already used under this license' in md.locator('.msg.err').inner_text(), 'duplicate batch number refused (friendly)')
    md.get_by_role('button', name='Cancel').click()
    # ethanol
    pg.locator('.tabs button', has_text='Ethanol Extraction').click()
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    check(md.locator('span', has_text=re.compile('^SKU')).count() == 0, 'ethanol has no SKU')
    field(md, 'Batch / Lot Number').fill('ETH-001')
    md.get_by_role('button', name='+ Add Biomass Tag').click(); md.get_by_role('button', name='+ Add Biomass Tag').click()
    rows = md.locator('.li'); rows.nth(0).locator('input').nth(0).fill('1A4000001'); rows.nth(0).locator('input').nth(1).fill('1000'); rows.nth(1).locator('input').nth(0).fill('1A4000002'); rows.nth(1).locator('input').nth(1).fill('500')
    check(md.locator('.autov', has_text='1500').count() == 1 and md.locator('text=1155 (77% of Total Biomass Used)').count() == 1, 'biomass total + 77% suggestion')
    field(md, 'Total Distillate Produced').fill('240')
    check(md.locator('.chkp.ok', has_text='VERY GOOD').count() == 1, 'yield 16% = VERY GOOD')
    md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=ETH-001')
    # BHO dual
    pg.locator('.tabs button', has_text='BHO Extraction').click()
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='THCA/HTE')
    check(md.locator('span', has_text='HTE Final Qty').count() == 1 and md.locator('span', has_text='Product Final Qty').count() == 0, 'dual SKU shows THCA/HTE fields only')
    md.get_by_role('button', name='Cancel').click()
    # admin edit needs reason, then view history
    pg.locator('.tabs button', has_text='Pre-Rolls').click(); pg.wait_for_selector('.card >> text=PR-001')
    pg.get_by_role('button', name='Edit', exact=True).click(); md = pg.locator('.md'); md.wait_for(state='visible'); pg.wait_for_selector('.md >> text=Reason for change')
    field(md, 'Total Joint Filled').fill('990')
    md.get_by_role('button', name='Save changes').click()
    check(md.locator('.msg.err', has_text='reason for change').count() == 1, 'admin edit needs reason')
    field(md, 'Reason for change').fill('Recount at end of shift'); md.get_by_role('button', name='Save changes').click(); pg.wait_for_selector('.md', state='detached')
    check(T['hx_batches'][0]['data']['total_joint_filled'] == '990' and T['hx_batches'][0]['flavor'] == 'Honey Melon', 'edit saved, flavor kept')
    pg.get_by_role('button', name='View', exact=True).first.click(); pg.wait_for_selector('.md .hxrec')
    txt = pg.locator('.md .hxrec').inner_text()
    check('Recount at end of shift' in txt and 'Total Joint Filled: 1000 → 990' in txt and 'Batch Record' in txt, 'record view with history')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # member continue
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'batch': 'editor', 'products': 'read'}; pg.reload(); pg.get_by_role('button', name='Batch Tracker').click(); pg.wait_for_selector('.card >> text=PR-001')
    check(pg.get_by_role('button', name='Edit', exact=True).count() == 0 and pg.get_by_role('button', name='Void').count() == 0, 'member: no Edit/Void')
    pg.get_by_role('button', name='Continue').click(); md = pg.locator('.md'); pg.wait_for_selector('.md >> text=fill in the blank fields')
    check(field(md, 'Flower Used').is_disabled() and not field(md, 'Infused Pre Roll METRC Tag').is_disabled(), 'filled fields locked, blanks open')
    check(md.locator('text=Formulation —').count() == 0, 'member does not see formulation')
    field(md, 'Infused Pre Roll METRC Tag').fill('1A400000555'); md.get_by_role('button', name='Save', exact=True).click(); pg.wait_for_selector('.md', state='detached')
    check(T['hx_batches'][0]['data'].get('infused_preroll_metrc') == '1A400000555' and T['hx_audit_log'][-1]['reason'] == 'Filled in blank fields', 'member filled a blank')
    # infused flower: total packaged (bags x unit size) and packaged METRC tag
    pg.locator('.tabs button', has_text='Infused Flower').click(); pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Infused Flower 3.5g'); field(md, 'Batch / Lot Number').fill('IF-001')
    check(md.locator('.msg', has_text='Mark the R&D Test Passed to fill in').count() == 1 and field(md, 'Total Bags Filled').count() == 0, 'packaging fields wait for R&D Passed, with a note saying so')
    md.locator('div.f', has=pg.locator('span', has_text='R&D Test')).first.get_by_role('button', name='Passed').click()
    field(md, 'Infused Flower Used').fill('360'); field(md, 'Total Bags Filled').fill('100'); field(md, 'Packaged METRC Tag').fill('1A4000000000000000000123')
    check(md.locator('label.f, div.f', has=pg.locator('span', has_text='Total Infused Flower Packaged (g)')).locator('.autov').inner_text() == '350', 'total infused flower packaged = 100 bags x 3.5 g')
    md.get_by_role('button', name='Submit & Sign').click(); pg.wait_for_selector('.card >> text=IF-001')
    d = T['hx_batches'][-1]['data']
    check(d['if_total_packaged'] == '350' and d['metrc_tag'] == '1A4000000000000000000123', 'saved with total packaged and the packaged METRC tag')
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    field(md, 'SKU').select_option(label='Infused Flower 7G'); field(md, 'Batch / Lot Number').fill('IF-002')
    md.locator('div.f', has=pg.locator('span', has_text='R&D Test')).first.get_by_role('button', name='Passed').click()
    field(md, 'Total Bags Filled').fill('100')
    check(md.locator('label.f, div.f', has=pg.locator('span', has_text='Total Infused Flower Packaged (g)')).locator('.autov').inner_text() == '700', '7G SKU (size from the name): 100 bags = 700 g')
    md.get_by_role('button', name='Cancel').click()
    # Michigan label uses BioTrack
    pg.locator('.ctx select').first.select_option(label='Michigan'); pg.locator('.tabs button', has_text='Ethanol Extraction').click()
    pg.get_by_role('button', name='+ New Batch').click(); md = pg.locator('.md')
    check(md.locator('text=Recorded on BioTrack?').count() >= 1 and md.locator('text=Recorded on METRC?').count() == 0, 'labels use the state tracking system')
    md.get_by_role('button', name='Cancel').click()
    T['hx_profiles'][0]['role'] = 'admin'; T['hx_profiles'][0]['perms'] = {}
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
sys.exit(1 if errors else 0)
