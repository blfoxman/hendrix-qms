import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
for t in ('hx_equipment', 'hx_equipment_events', 'hx_chemicals'): T[t] = []
T['hx_log_lists'] += [{'id': 'll-f2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'list_key': 'equipment.equipment', 'name': 'Filler #2', 'spec': {'serial': 'FL-778'}, 'sort': 0, 'active': True, 'created_at': '1'},
                      {'id': 'll-sc1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'list_key': 'scale_calibration.scales', 'name': 'SCALE-01', 'spec': {'location': 'Production', 'make': 'Ohaus Scout', 'serial': 'S123'}, 'sort': 1, 'active': True, 'created_at': '1'}]
T['hx_facility_log'].append({'id': 'fl-m1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'log_type': 'equipment', 'item_id': 'll-f2', 'item': 'Filler #2', 'data': {'date': (dt.date.today() - dt.timedelta(days=100)).isoformat(), 'maintenance_type': 'Routine/Preventive', 'description': 'Greased chain', 'performed_by': 'Lee'},
                             'result': 'OK', 'performed_by': 'Lee', 'source': 'app', 'created_at': '2026-07-01T10:00:00Z', 'voided': False})
SEQ = {'EQ': 0, 'CHEM': 0}
def today(): return dt.date.today().isoformat()
def addm(d, m):
    d = dt.date.fromisoformat(d); mm = d.month - 1 + m; return dt.date(d.year + mm // 12, mm % 12 + 1, min(d.day, 28)).isoformat()
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def eq_apply(eid):
    e = next(x for x in T['hx_equipment'] if x['id'] == eid); ev = [v for v in T['hx_equipment_events'] if v['equipment_id'] == eid and not v.get('voided')]
    cal = sorted([v for v in ev if v['kind'] == 'calibration' and v['result'] == 'pass'], key=lambda v: v['done_on'])
    e['cal_last'] = cal[-1]['done_on'] if cal else None; e['cal_due'] = cal[-1]['next_due'] if cal else None
    pq = [v['done_on'] for v in ev if v['kind'] == 'validation' and v['result'] == 'pass' and v['stage'] in ('PQ', 'Revalidation')]
    e['pq_on'] = max(pq) if pq else None; e['reval_due'] = addm(max(pq), 12) if pq else None
_h = handle
def handle(route, request):
    u = request.url; m = request.method
    tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if tbl == 'hx_equipment' and m == 'POST':
        rows = json.loads(request.post_data); rows = rows if isinstance(rows, list) else [rows]
        for r in rows:
            SEQ['EQ'] += 1
            r.update({'number': 'EQ-%03d' % SEQ['EQ'], 'status': 'in_service', 'created_at': now(), 'cal_last': None, 'cal_due': None, 'iq_on': None, 'oq_on': None, 'pq_on': None, 'reval_due': None})
            for k, v in (('files', []), ('notes', ''), ('pm_interval_days', None), ('val_required', False), ('cal_required', False), ('installed_on', None), ('asset_tag', ''), ('log_item_id', None)): r.setdefault(k, v)
            T['hx_equipment'].append(r)
        return jr(route, rows, 201)
    if tbl == 'hx_equipment' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); e = next(x for x in T['hx_equipment'] if x['id'] == cid)
        if b.get('status') == 'retired' and not b.get('retired_reason'): return jr(route, {'message': 'Give a reason for retiring this equipment.'}, 400)
        e.update(b); return jr(route, [e])
    if tbl == 'hx_equipment_events' and m == 'POST':
        r = json.loads(request.post_data); e = next(x for x in T['hx_equipment'] if x['id'] == r['equipment_id'])
        if r['kind'] == 'calibration' and not r['files'] and not r['standard']: return jr(route, {'message': 'Attach the calibration certificate or name the reference standard used'}, 400)
        if r['kind'] == 'return_to_service' and not all(r['checks'].get(k) for k in ('cleared', 'cleaned', 'working')): return jr(route, {'message': 'Confirm tools...'}, 400)
        if r['kind'] == 'calibration' and r['result'] == 'pass' and not r.get('next_due'): r['next_due'] = addm(r['done_on'], e['cal_interval_months'])
        r.update({'recorded_by': 'Sam', 'created_at': now(), 'voided': False, 'closed_on': None, 'closure': ''}); T['hx_equipment_events'].append(r)
        if r['kind'] == 'out_of_service' or (r['kind'] in ('calibration', 'validation') and r['result'] == 'fail'): e['status'] = 'out_of_service'
        if r['kind'] == 'return_to_service': e['status'] = 'in_service'
        eq_apply(e['id']); return jr(route, [r], 201)
    if tbl == 'hx_equipment_events' and m == 'PATCH':
        b = json.loads(request.post_data); cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); v = next(x for x in T['hx_equipment_events'] if x['id'] == cid); v.update(b); eq_apply(v['equipment_id']); return jr(route, [v])
    if tbl == 'hx_chemicals' and m in ('POST', 'PATCH'):
        b = json.loads(request.post_data)
        if m == 'POST': SEQ['CHEM'] += 1; c = {**b, 'number': 'CHEM-%03d' % SEQ['CHEM'], 'status': b.get('status', 'pending'), 'created_at': now(), 'approved_by': '', 'approved_at': None}
        else: cid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); c = {**next(x for x in T['hx_chemicals'] if x['id'] == cid), **b}
        if c['status'] == 'approved':
            if not c['sds_files']: return jr(route, {'message': 'Attach the Safety Data Sheet (SDS) before approving.'}, 400)
            if c['purpose'] == 'Pesticide / crop protection' and not c['epa_reg']: return jr(route, {'message': 'Enter the EPA registration number of the pesticide.'}, 400)
            if not c['approved_by']: c['approved_by'] = 'Sam'; c['approved_at'] = now()
        if m == 'POST': T['hx_chemicals'].append(c)
        else: next(x for x in T['hx_chemicals'] if x['id'] == c['id']).update(c)
        return jr(route, [c], 201 if m == 'POST' else 200)
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def eq(name): return next(x for x in T['hx_equipment'] if x['name'] == name)
def eqrow(pg, name): return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(name) + '$')))
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    check(pg.locator('.card.gold', has_text='Equipment').locator('text=No equipment yet').count() == 1 and pg.locator('.card.gold', has_text='Chemicals and SDS').count() == 1, 'dashboard cards for equipment and chemicals')
    pg.get_by_role('button', name='Equipment', exact=True).click(); pg.wait_for_selector('text=2 items in your Facility Log lists are not in the register')
    pg.get_by_role('button', name='Add them to the register').click(); pg.wait_for_selector('.msg >> text=Added 2 items from the Facility Log lists')
    sc = eq('SCALE-01'); fl = eq('Filler #2')
    check(sc['category'] == 'Scale / balance' and sc['cal_required'] and sc['cal_interval_months'] == 12 and fl['log_item_id'] == 'll-f2' and sc['number'] == 'EQ-002', 'imported from the Facility Log lists (scale needs calibration, filler linked to its log item)')
    # new extraction equipment
    pg.get_by_role('button', name='+ Equipment').click(); md = pg.locator('.md')
    field(md, 'Name *').fill('Closed loop BHO system'); field(md, 'Category').select_option('Extraction'); field(md, 'Location / room').fill('C1D1 room')
    check(md.locator('label.ck', has_text='Needs validation').locator('input').is_checked(), 'extraction equipment needs validation by default')
    field(md, 'Every (days)').fill('30'); field(md, 'Tasks (manufacturer requirements)').fill('Leak test, replace o-rings')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Closed loop BHO system.')
    bho = eq('Closed loop BHO system'); li = [x for x in T['hx_log_lists'] if x['list_key'] == 'equipment.equipment' and x['name'] == 'Closed loop BHO system']
    check(bho['number'] == 'EQ-003' and len(li) == 1 and bho['log_item_id'] == li[0]['id'], 'saved with a number and added to the Equipment Maintenance Log list (log item linked)')
    check(eqrow(pg, 'Closed loop BHO system').locator('.badge', has_text='Never recorded').count() == 1 and eqrow(pg, 'Closed loop BHO system').locator('.badge', has_text='Not validated').count() == 1, 'new equipment: maintenance never recorded, not validated')
    # filler: PM every 90 days, last PM 100 days ago in the log -> overdue
    eqrow(pg, 'Filler #2').get_by_role('button', name='Open').click(); md = pg.locator('.md'); md.get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    field(md, 'Every (days)').fill('90'); md.get_by_role('button', name='Save').click(); pg.wait_for_selector('.msg >> text=Saved Filler #2.')
    eqrow(pg, 'Filler #2').locator('.badge', has_text='Overdue').wait_for(timeout=8000)
    check(eqrow(pg, 'Filler #2').locator('.badge', has_text='Overdue').count() == 1, 'preventive maintenance overdue from the Equipment Maintenance Log (last PM 100 days ago, every 90)')
    # calibrate the scale
    eqrow(pg, 'SCALE-01').get_by_role('button', name='Open').click(); md = pg.locator('.md')
    check(md.locator('.badge', has_text='Never calibrated').count() == 1, 'scale: never calibrated')
    md.get_by_role('button', name='Record calibration').click(); md = pg.locator('.md')
    field(md, 'Calibrated by (person / company)').fill('Midwest Scale Co'); md.locator('label', has_text='+ Certificate').locator('input[type=file]').set_input_files({'name': 'cert.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 cert'})
    pg.wait_for_selector('.md >> text=cert.pdf'); md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Calibration recorded for SCALE-01.')
    sc = eq('SCALE-01'); scl = next(x for x in T['hx_log_lists'] if x['id'] == 'll-sc1')
    check(sc['cal_due'] == addm(today(), 12) and scl['spec'].get('cert_date') == today() and scl['spec'].get('make') == 'Ohaus Scout', 'calibration sets the next due date and the Scale Calibration Log list gets the certification date')
    check(pg.locator('.md').locator('.badge', has_text='Next ' + addm(today(), 12)).count() >= 1, 'detail shows the next calibration date')
    pg.locator('.md').get_by_role('button', name='Out of service').click(); md = pg.locator('.md')
    field(md, 'Reason *').fill('Display flickers'); md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Out of service recorded')
    check(eq('SCALE-01')['status'] == 'out_of_service', 'out of service')
    pg.locator('.md').get_by_role('button', name='Back in service').click(); md = pg.locator('.md')
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.md .msg.err >> text=Tick every check')
    for lab in ('Tools, parts', 'Cleaned and sanitized', 'Checked working'): md.locator('label.ck', has_text=lab).locator('input').check()
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Back in service recorded')
    check(eq('SCALE-01')['status'] == 'in_service', 'back in service only after the checks')
    # temporary repair on the filler
    pg.locator('.md').get_by_role('button', name='Close').click() if pg.locator('.md').get_by_role('button', name='Close').count() else pg.locator('.mo').click(position={'x': 5, 'y': 5})
    pg.wait_for_timeout(200)
    if pg.locator('.md').count(): pg.locator('.mo').click(position={'x': 5, 'y': 5})
    eqrow(pg, 'Filler #2').get_by_role('button', name='Open').click(); md = pg.locator('.md'); md.get_by_role('button', name='Temporary repair').click(); md = pg.locator('.md')
    field(md, 'Temporary repair (what was done) *').fill('Hose clamp on cracked line'); field(md, 'Permanent repair must be done by *').fill((dt.date.today() + dt.timedelta(days=7)).isoformat())
    md.get_by_role('button', name='Record').click(); pg.wait_for_selector('.msg >> text=Temporary repair recorded')
    pg.locator('.md').locator('text=1 open').wait_for(timeout=8000)
    check(pg.locator('.md').locator('text=1 open').count() == 1, 'temporary repair open on the detail')
    pg.locator('.md').get_by_role('button', name='Made permanent').click(); md = pg.locator('.md').last
    md.locator('textarea').fill('Replaced the line'); md.get_by_role('button', name='Close temporary repair').click(); pg.wait_for_selector('.msg >> text=Temporary repair closed.')
    tr = next(v for v in T['hx_equipment_events'] if v['kind'] == 'temporary_repair')
    check(tr['closed_on'] == today() and tr['closure'] == 'Replaced the line', 'temporary repair made permanent')
    check(pg.locator('.md').locator('text=Greased chain').count() == 1, 'detail history includes the Equipment Maintenance Log entry')
    pg.locator('.mo').click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(200)
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print register').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Equipment register' in html and 'SCALE-01' in html and 'Closed loop BHO system' in html, 'printable register for inspectors'); w.close()
    pg.screenshot(path=OUT + 'equipment.png')
    # chemicals
    pg.get_by_role('button', name='Chemicals and SDS', exact=True).click(); pg.wait_for_selector('text=No chemicals yet')
    pg.get_by_role('button', name='+ Chemical').click(); md = pg.locator('.md')
    field(md, 'Product name *').fill('Quat sanitizer 200'); field(md, 'Used for').select_option('Food-contact sanitizer')
    check(field(md, 'Grade').input_value() == 'food_contact_sanitizer', 'food-contact sanitizer grade set automatically')
    md.get_by_role('button', name='Save and approve').click(); pg.wait_for_selector('.md .msg.err >> text=Attach the Safety Data Sheet')
    md.locator('label', has_text='+ SDS').locator('input[type=file]').set_input_files({'name': 'quat_sds.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF sds'}); pg.wait_for_selector('.md >> text=quat_sds.pdf')
    field(md, 'Storage area *').fill('Chemical cage'); field(md, 'PPE (SDS section 8) *').fill('Nitrile gloves, goggles'); field(md, 'First aid (SDS section 4)').fill('Rinse eyes 15 min')
    md.get_by_role('button', name='Save and approve').click(); pg.wait_for_selector('.msg >> text=Approved Quat sanitizer 200.')
    c = T['hx_chemicals'][0]
    check(c['status'] == 'approved' and c['number'] == 'CHEM-001' and c['approved_by'] == 'Sam', 'chemical approved with SDS, storage and PPE')
    pg.get_by_role('button', name='+ Chemical').click(); md = pg.locator('.md')
    field(md, 'Product name *').fill('Bug-B-Gone'); field(md, 'Used for').select_option('Pesticide / crop protection'); md.locator('label', has_text='+ SDS').locator('input[type=file]').set_input_files({'name': 'bug_sds.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF'})
    pg.wait_for_selector('.md >> text=bug_sds.pdf'); field(md, 'Storage area *').fill('Pesticide shed'); field(md, 'PPE (SDS section 8) *').fill('Gloves')
    md.get_by_role('button', name='Save and approve').click(); pg.wait_for_selector('.md .msg.err >> text=EPA registration')
    md.get_by_role('button', name='Save', exact=True).click(); pg.wait_for_selector('.msg >> text=Saved Bug-B-Gone.')
    pg.locator('.card.gold', has_text='Waiting for approval').locator('.v', has_text='1').wait_for(timeout=8000)
    check(T['hx_chemicals'][1]['status'] == 'pending' and pg.locator('.card.gold', has_text='Waiting for approval').locator('.v').inner_text() == '1', 'pesticide without EPA number stays pending')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print storage area lists').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('Chemicals stored here' in html and 'Chemical cage' in html and 'Quat sanitizer 200' in html and 'Rinse eyes 15 min' in html and 'Bug-B-Gone' not in html, 'storage area list: approved chemicals with PPE and first aid'); w.close()
    pg.locator('tr', has_text='Quat sanitizer 200').get_by_role('button', name='Remove').click(); md = pg.locator('.md')
    md.locator('textarea').fill('Switched brands'); md.get_by_role('button', name='Remove from use').click(); pg.wait_for_selector('.msg >> text=Removed Quat sanitizer 200 from use.')
    check(T['hx_chemicals'][0]['status'] == 'removed' and T['hx_chemicals'][0]['removed_reason'] == 'Switched brands', 'removed from use with a reason')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Open equipment')
    check(pg.locator('.card.gold', has_text='Open equipment').locator('text=/maintenance overdue/').count() == 1, 'dashboard equipment card shows maintenance status')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
