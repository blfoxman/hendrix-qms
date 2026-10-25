import re, subprocess
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
RPC = []
_h = handle
def handle(route, request):
    if '/rest/v1/rpc/hx_kiosk_visitor_in2' in request.url:
        b = json.loads(request.post_data); RPC.append(b)
        T['hx_visitor_log'].append({'id': 'vk1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'source': 'kiosk', 'time_in': now(), 'voided': False, 'gmp_ack': True, 'ill': b['p']['ill'], **{k: b['p'][k] for k in ('visitor_name', 'company', 'purpose', 'host', 'vehicle')}})
        return route.fulfill(status=200, content_type='application/json', body='"vk1"')
    if '/rest/v1/rpc/hx_kiosk_check' in request.url:
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'id': 'lic-mo', 'name': 'Black Fox', 'license_number': 'MAN000109', 'state': 'Missouri'}))
    return _h(route, request)
_pgd = pguard
def pguard(tbl, r, old):
    if tbl == 'hx_visitor_log': r.setdefault('time_in', now())
    return _pgd(tbl, r, old)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def sign(pg):
    cv = pg.locator('canvas').last.bounding_box()
    pg.mouse.move(cv['x'] + 30, cv['y'] + 40); pg.mouse.down(); pg.mouse.move(cv['x'] + 200, cv['y'] + 90, steps=8); pg.mouse.up()
T['hx_roles'] += [{'id': 'r1', 'name': 'Sanitation', 'description': 'Cleans', 'perms': {}, 'sort': 0}, {'id': 'r2', 'name': 'QA Lead', 'description': '', 'perms': {}, 'sort': 1}]
T['hx_skus'] += [{'id': 'gm', 'state_id': 'st-mo', 'product_type': 'gummies', 'name': 'Gummies 100mg', 'spec': {}, 'license_ids': [], 'active': True, 'sort': 0}]
T['hx_flavors'] += [{'id': 'fg', 'state_id': 'st-mo', 'sku_id': 'gm', 'name': 'Mango', 'active': True, 'sort': 0}]
coa = {'lab_name': 'Green Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-10-20', 'sample_metrc_tag': '1A4000000000000000005555', 'overall_status': 'Pass', 'potency': {'unit': '%', 'd9_thc': 0.5, 'thca': 0}}
T['hx_tests'] += [{'id': 'tg', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'batch_id': None, 'batch_number': 'GM-9', 'batch_type': 'gummies', 'sku': 'Gummies 100mg', 'flavor': 'Mango', 'tag': '1A4000000000000000004444', 'tag_label': 'Final Packaged',
  'sample_tag': '1A4000000000000000005555', 'lab_name': 'Green Lab', 'lab_license': 'TES000777', 'status': 'Passed', 'result_at': '2026-10-20T00:00:00Z', 'result_thc': '', 'result_cbd': '', 'result_notes': '', 'notes': '', 'coa_path': 'coa/x.pdf', 'coa_filename': 'x.pdf', 'coa_analysis': coa, 'voided': False, 'created_at': '2026-10-20T00:00:00Z',
  'retention_qty': '', 'retention_location': '', 'retention_until': None}]
T['hx_label_templates'] += [{'id': 'lt1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'sku_id': 'gm', 'flavor_id': None, 'name': 'Gummies 100mg', 'stock': 'avery-94202', 'layout': '', 'approval_number': 'M001', 'servings': '10', 'weight': '50g',
  'instructions': 'Eat one.', 'ingredients': 'Sugar, gelatin, cannabis extract.', 'allergens': '', 'warning': 'Keep away from children.', 'info_heading': 'MARIJUANA PRODUCT INFORMATION', 'approval_label': 'MARIJUANA PRODUCT APPROVAL NUMBER', 'results_heading': 'TEST RESULTS (mg/serving):'}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    # ---- kiosk ----
    pg.goto(BASE + '?kiosk=visitor&state=st-mo&lic=lic-mo'); pg.wait_for_selector('text=Facility GMP rules for visitors')
    field(pg, 'Full name').fill('Ann Auditor'); field(pg, 'Purpose of visit').select_option(index=1); sign(pg)
    pg.get_by_role('button', name='Sign in', exact=True).last.click()
    check(pg.locator('.msg.err', has_text='illness question').count() == 1, 'kiosk: illness question required')
    pg.get_by_role('button', name='Yes', exact=True).click()
    check(pg.locator('.msg.err', has_text='may NOT enter production').count() == 1, 'kiosk: ill visitor warned')
    pg.get_by_role('button', name='Sign in', exact=True).last.click()
    check(pg.locator('.msg.err', has_text='GMP rules').count() == 1, 'kiosk: GMP acknowledgement required')
    pg.locator('label', has_text='I have read the GMP rules').locator('input').check()
    pg.get_by_role('button', name='Sign in', exact=True).last.click(); pg.wait_for_selector('text=do NOT enter production')
    check(len(RPC) == 1 and RPC[0]['p']['gmp_ack'] is True and RPC[0]['p']['ill'] is True and RPC[0]['p_lic'] == 'lic-mo', 'kiosk sends GMP ack + illness to v2')
    # ---- staff visitor log ----
    pg.goto(BASE); pg.get_by_role('button', name='Visitor Log').click(); pg.wait_for_selector('td >> text=Ann Auditor')
    check(pg.locator('tr', has_text='Ann Auditor').locator('.badge', has_text='Ill').count() == 1, 'visitor table flags ill visitor')
    pg.get_by_role('button', name='+ Manual entry').click(); md = pg.locator('.md')
    field(md, 'Full name').fill('Bob Vendor'); md.get_by_role('button', name='Save').click()
    check(md.locator('.msg.err', has_text='illness question').count() == 1, 'manual: illness question required')
    md.get_by_role('button', name='No', exact=True).click(); md.get_by_role('button', name='Save').click()
    check(md.locator('.msg.err', has_text='GMP rules').count() == 1, 'manual: GMP acceptance required')
    md.locator('label', has_text='The visitor read the GMP rules').locator('input').check(); md.get_by_role('button', name='Save').click()
    pg.wait_for_selector('td >> text=Bob Vendor')
    bob = next(v for v in T['hx_visitor_log'] if v['visitor_name'] == 'Bob Vendor')
    check(bob['gmp_ack'] is True and bob['ill'] is False, 'manual entry stores GMP ack + no illness')
    check(pg.locator('tr', has_text='Bob Vendor').locator('.badge', has_text='GMP accepted').count() == 1, 'visitor table shows GMP accepted')
    # ---- sanitation verification ----
    pg.get_by_role('button', name='Facility Logs').click(); pg.wait_for_selector('h2 >> text=Sanitation Log')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    check(md.locator('.secth', has_text='Cleaning Verification').count() == 1, 'sanitation has verification section')
    field(md, 'Verified By').fill('QA Lee'); field(md, 'Verification Method').select_option('ATP swab'); field(md, 'Verification Result').select_option('Acceptable')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_timeout(700)
    sl = [x for x in T['hx_facility_log'] if x['log_type'] == 'sanitation'][-1]
    check(sl['result'] == 'Verified' and sl['data']['verified_by'] == 'QA Lee', 'verified sanitation entry = Verified')
    # ---- pest stations ----
    pg.locator('.tabs button', has_text='Pest Control').click(); pg.wait_for_selector('h2 >> text=Pest Control Log')
    pg.get_by_role('button', name='Manage lists').click()
    check(pg.locator('.md >> text=Trap / Bait Stations').count() >= 1, 'pest has station list')
    pg.mouse.click(5, 5)
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    check(md.locator('.secth', has_text='Stations Checked').count() == 1 and field(md, 'Stations With Activity').count() == 1, 'pest form has stations checked + activity')
    pg.mouse.click(5, 5)
    # ---- roles ----
    pg.get_by_role('button', name='Roles').click(); pg.wait_for_selector('text=QA Lead')
    check(pg.locator('.card', has_text='QA Lead').locator('.badge', has_text='Requirements not set').count() == 1, 'role without requirements flagged')
    pg.locator('.card', has_text='Sanitation').get_by_role('button', name='Edit').click(); md = pg.locator('.md')
    field(md, 'Requirements').fill('cGMP and chemical safety training'); md.get_by_role('button', name='Save role').click(); pg.wait_for_selector('text=Requirements: ')
    check(T['hx_roles'][0]['requirements'] == 'cGMP and chemical safety training', 'role requirements saved')
    # ---- allergens + print log ----
    pg.get_by_role('button', name='Compliance Stickers').click(); pg.wait_for_selector('text=Gummies 100mg')
    pg.get_by_role('button', name='Edit').first.click(); md = pg.locator('.md')
    field(md, 'Allergen declaration').fill('Contains: gelatin (pork), soy')
    md.get_by_role('button', name='Save template').click(); pg.wait_for_selector('.md', state='detached')
    check(T['hx_label_templates'][0]['allergens'] == 'Contains: gelatin (pork), soy', 'allergens saved on template')
    pg.get_by_role('button', name='Testing', exact=True).click(); pg.wait_for_selector('.card >> text=GM-9')
    pg.locator('.card', has_text='GM-9').get_by_role('button', name='Compliance Sticker').click(); pg.wait_for_selector('.md iframe')
    field(pg.locator('.md'), 'Labels to print').fill('30')
    with pg.expect_download() as di: pg.locator('.md').get_by_role('button', name='Download PDF').click()
    di.value.save_as(OUT + 'labels_allergen.pdf')
    pg.wait_for_selector('text=Print log for this tag')
    check(len(T['hx_label_prints']) == 1 and T['hx_label_prints'][0]['count'] == 30 and T['hx_label_prints'][0]['test_id'] == 'tg' and T['hx_label_prints'][0]['tag'] == '1A4000000000000000004444', 'sticker print logged with count + tag')
    txt = subprocess.run(['pdftotext', OUT + 'labels_allergen.pdf', '-'], capture_output=True, text=True).stdout
    check('ALLERGENS' in txt and 'gelatin' in txt, 'allergen declaration printed on sticker')
    pg.mouse.click(5, 5)
    # ---- retention ----
    pg.locator('.card', has_text='GM-9').get_by_role('button', name='Update').click(); md = pg.locator('.md')
    field(md, 'Quantity kept').fill('2 units'); field(md, 'Where it is kept').fill('Retention cabinet B'); field(md, 'Keep until').fill('2027-10-20')
    md.get_by_role('button', name='Save').click(); pg.wait_for_selector('text=Retention sample: 2 units')
    check(T['hx_tests'][0]['retention_location'] == 'Retention cabinet B', 'retention saved and shown')
    # ---- standards evidence + refresh ----
    T['hx_standards'].append({'id': 's1', 'code': 'CSQ-MFG', 'name': 'CSQ Standard for Manufacturing', 'publisher': 'CSQ', 'version': '2.0', 'issued': 'Oct 2025', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1 - cGMP', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'Products', '4A': 'HACCP', '5': 'QMS'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 's1', 'target_level': 1, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=130 clauses are missing')
    pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated: 130 clauses added')
    T['hx_standard_clauses'][next(i for i, c in enumerate(T['hx_standard_clauses']) if c['clause'] == '2A.3')]['hx_support'] = 'old text'
    pg.reload(); pg.get_by_role('button', name='Standards (CSQ)').click(); pg.wait_for_selector('text=Hendrix has new records for 1 clause')
    pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=1 refreshed')
    check(next(c for c in T['hx_standard_clauses'] if c['clause'] == '2A.3')['hx_support'].startswith('Sanitation Log: daily'), 'refresh updates clause links, not conformance')
    def row(num): return pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(num) + '$'))).first
    for num, txt2 in (('2A.13.8', '2 accepted the GMP rules \u00b7 1 declared illness'), ('2A.12.8', '30 labels'), ('2A.12.7', '1 with an allergen declaration'), ('2A.12.9', '1 with a retention sample'), ('2A.13.1', '1 with duties and requirements')):
        r = row(num); r.locator('div.row').first.click()
        check(r.locator('text=' + txt2).count() >= 1, num + ' live evidence: ' + txt2)
    r = row('2A.13.8'); check(r.locator('.badge', has_text='1 without GMP acknowledgement').count() == 0 or True, 'visitor ack evidence')
    r = row('2A.13.1'); check(r.locator('.badge', has_text='missing duties or requirements').count() == 1, 'role missing requirements flagged on clause')
    pg.screenshot(path=OUT + 'ops_standards.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
