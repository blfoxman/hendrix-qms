import calendar
import re, datetime as dt
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today()
def addm(d, m):
    mm = d.month - 1 + m; return dt.date(d.year + mm // 12, mm % 12 + 1, min(d.day, calendar.monthrange(d.year + mm // 12, mm % 12 + 1)[1])).isoformat()
T['hx_tests'] += [{'id': 't1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'tag': 'A', 'lab_name': 'Green Lab', 'voided': False, 'status': 'Passed'},
                  {'id': 't2', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'tag': 'B', 'lab_name': 'Cheap Labs LLC', 'voided': False, 'status': 'Passed'}]
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def jerr(route, m): return jr(route, {'message': m}, 400)
def full(): return T['hx_profiles'][0]['role'] == 'admin' or (T['hx_profiles'][0].get('perms') or {}).get('suppliers') == 'admin'
def audit(tbl, r, action, reason):
    T['hx_audit_log'].append({'id': len(T['hx_audit_log']) + 1, 'at': now(), 'table_name': tbl, 'row_id': r['id'], 'action': action, 'state_id': r.get('state_id'), 'license_id': r.get('license_id'), 'user_name': 'Sam', 'reason': reason, 'changed': None, 'old_data': None, 'new_data': r})
def sguard(new, old):
    # emulates hx_supplier_guard
    if old is None:
        new.setdefault('status', 'pending'); new.setdefault('license_ids', [new['license_id']]); new.setdefault('ever_approved', False)
        if new['status'] not in ('pending', 'emergency') and not full(): return 'Only someone with Full access to Suppliers can approve or change a status.'
    if any(x['id'] != new['id'] and new['license_id'] == x['license_id'] and x['name'].strip().lower() == new['name'].strip().lower() for x in T['hx_suppliers']):
        return 'duplicate key value violates unique constraint "hx_suppliers_name"'
    ch = old is not None and new['status'] != old['status']
    if ch and not full(): return 'Only someone with Full access to Suppliers can approve or change a status.'
    if new['status'] == 'emergency' and not (new.get('emergency_verification') or '').strip(): return 'An emergency supplier needs a note on how materials are checked before use.'
    if new['status'] in ('approved', 'conditional') and (old is None or ch):
        if not (new.get('approval_basis') or '').strip(): return 'Write what the approval is based on.'
        if new['category'] == 'Testing Lab' and not any(c.get('kind') == 'ISO/IEC 17025 accreditation' for c in new.get('credentials') or []): return 'A testing lab needs its ISO/IEC 17025 accreditation on file before approval.'
        if new['category'] == 'Co-manufacturer' and not new.get('last_audit'): return 'Record the audit of the contract manufacturer before approval.'
        new.update({'approved_by': 'Sam', 'approved_at': now(), 'ever_approved': True})
        if not new.get('next_review'): new['next_review'] = addm(TODAY, 6 if new['risk'] == 'high' else 12)
    if ch and new['status'] in ('suspended', 'disqualified') and not (new.get('status_reason') or '').strip(): return 'A reason is required.'
    return None
def handle(route, request):
    u = request.url; m = request.method
    if '/rest/v1/hx_suppliers' in u and m in ('POST', 'PATCH', 'DELETE'):
        if m == 'POST':
            r = json.loads(request.post_data); r = dict(r); r['created_at'] = now()
            for k, v in {'credentials': [], 'certificates': [], 'approval_basis': '', 'status_reason': '', 'last_review': None, 'next_review': None, 'approved_by': '', 'approved_at': None}.items(): r.setdefault(k, v)
            g = sguard(r, None)
            if g: return jerr(route, g)
            T['hx_suppliers'].append(r); audit('hx_suppliers', r, 'INSERT', 'Supplier added'); return jr(route, [r], 201)
        sid = urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]); old = next(x for x in T['hx_suppliers'] if x['id'] == sid)
        if m == 'DELETE':
            if old.get('ever_approved'): return jerr(route, 'This supplier has been approved before. Disqualify it instead of deleting it.')
            T['hx_suppliers'].remove(old); return route.fulfill(status=204, body='')
        new = {**json.loads(json.dumps(old)), **json.loads(request.post_data)}
        g = sguard(new, old)
        if g: return jerr(route, g)
        old.clear(); old.update(new); audit('hx_suppliers', old, 'UPDATE', new.get('status_reason') if new['status'] in ('suspended', 'disqualified') else 'Supplier ' + new['status']); return jr(route, [old])
    if '/rest/v1/hx_supplier_reviews' in u and m == 'POST':
        r = json.loads(request.post_data)
        if not full(): return jerr(route, 'Only someone with Full access to Suppliers can record a review.')
        if r['result'] in ('Suspend', 'Disqualify') and not r['notes'].strip(): return jerr(route, 'Write the reason.')
        s = next(x for x in T['hx_suppliers'] if x['id'] == r['supplier_id']); r['reviewer'] = 'Sam'; r['created_at'] = now(); T['hx_supplier_reviews'].append(r)
        s['last_review'] = r['review_date']; s['next_review'] = addm(dt.date.fromisoformat(r['review_date']), 6 if s['risk'] == 'high' else 12)
        s['status'] = {'Keep approved': s['status'], 'Approve with conditions': 'conditional', 'Suspend': 'suspended', 'Disqualify': 'disqualified'}[r['result']]
        if r['result'] in ('Suspend', 'Disqualify'): s['status_reason'] = r['notes']
        audit('hx_supplier_reviews', r, 'INSERT', 'Supplier review: ' + r['rating'] + ' - ' + r['result']); return jr(route, [r], 201)
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def sup(name): return next(x for x in T['hx_suppliers'] if x['name'] == name)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Open suppliers')
    check(pg.locator('.card', has_text='Open suppliers').locator('text=None yet').count() == 1, 'dashboard card: no suppliers yet')
    check(pg.locator('.badge', has_text=re.compile('^Suppliers$')).count() == 0, 'Suppliers removed from Coming next')
    pg.get_by_role('button', name='Suppliers', exact=True).click(); pg.wait_for_selector('text=No suppliers yet for Black Fox')
    # add Futurola
    pg.get_by_role('button', name='+ Add supplier').click(); md = pg.locator('.md')
    field(md, 'Supplier name').fill('Futurola USA'); field(md, 'Category / type').select_option('Cones/Pre-roll Supplies'); field(md, 'Products / services supplied').fill('98mm cones')
    field(md, 'Specifications the supplier must meet').fill('Food-grade paper, COA with every lot'); field(md, 'Contact email').fill('sales@futurola.com')
    md.get_by_role('button', name='Add supplier').click(); pg.wait_for_selector('.msg >> text=Added Futurola USA')
    f = sup('Futurola USA'); check(f['status'] == 'pending' and f['specs'].startswith('Food-grade') and f['license_ids'] == ['lic-mo'], 'supplier added as pending with specs')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # add lab with 17025 expiring soon
    pg.get_by_role('button', name='+ Add supplier').click(); md = pg.locator('.md')
    field(md, 'Supplier name').fill('Green Lab'); field(md, 'Category / type').select_option('Testing Lab'); field(md, 'Risk').select_option('high')
    md.get_by_role('button', name='+ Add credential').click(); cr = md.locator('div.grid', has=pg.locator('input[placeholder=Number]')).last
    check(cr.locator('select').input_value() == 'ISO/IEC 17025 accreditation', 'lab credential defaults to ISO/IEC 17025')
    cr.locator('input[placeholder=Number]').fill('L-2231'); cr.locator('input[type=date]').fill((TODAY + dt.timedelta(days=30)).isoformat())
    cr.locator('input[type=file]').set_input_files({'name': 'iso17025.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4'}); pg.wait_for_selector('.md >> text=\U0001f4ce')
    md.get_by_role('button', name='Add supplier').click(); pg.wait_for_selector('.msg >> text=Added Green Lab')
    gl = sup('Green Lab'); check(gl['credentials'][0]['number'] == 'L-2231' and gl['credentials'][0]['file']['name'] == 'iso17025.pdf', 'credential with number, expiry and file')
    pg.locator('.md').get_by_role('button', name='Close').click()
    check(pg.locator('.msg.err', has_text='not approved with a current ISO/IEC 17025').locator('text=Cheap Labs LLC').count() == 1 and pg.locator('.msg.err', has_text='Green Lab').count() == 1, 'labs used in Testing but not approved are flagged')
    # approve Futurola
    pg.locator('.card', has_text='Futurola USA').click(); pg.locator('.md').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.get_by_role('button', name='Approve supplier').click(); check(md.locator('.msg.err', has_text='based on').count() == 1, 'approval requires a basis')
    md.locator('textarea').fill('Questionnaire, food-grade certificate and trial lot reviewed'); md.get_by_role('button', name='Approve supplier').click(); pg.wait_for_selector('.msg >> text=Approved Futurola USA')
    f = sup('Futurola USA'); check(f['status'] == 'approved' and f['ever_approved'] and f['approved_by'] == 'Sam' and f['next_review'] == addm(TODAY, 12), 'approved: who, when, next review in 12 months')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # approve lab (high risk -> 6 months)
    pg.locator('.card', has_text='Green Lab').first.click(); pg.locator('.md').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    check(field(md, 'Next review').input_value() == (lambda d: addm(TODAY, 6))(0), 'high risk: next review 6 months')
    md.locator('textarea').fill('ISO 17025 scope covers cannabis potency and contaminants'); md.get_by_role('button', name='Approve supplier').click(); pg.wait_for_selector('.msg >> text=Approved Green Lab')
    pg.locator('.md').get_by_role('button', name='Close').click()
    check(pg.locator('.msg.err', has_text='17025').locator('text=Green Lab').count() == 0 and pg.locator('.msg.err', has_text='Cheap Labs LLC').count() == 1, 'approved lab clears the flag; unapproved lab still flagged')
    check(pg.locator('.card', has_text='Green Lab').locator('.badge', has_text='1 expiring').count() == 1, 'expiring accreditation badge')
    check(pg.locator('.card.gold', has_text='Credentials expiring').locator('.v').inner_text() == '1' and pg.locator('.card.gold', has_text='Approved').first.locator('.v').inner_text() == '2', 'stats: 2 approved, 1 expiring')
    # review -> conditional
    pg.locator('.card', has_text='Futurola USA').click(); pg.locator('.md').get_by_role('button', name='Record review').click(); md = pg.locator('.md')
    field(md, 'Rating').select_option('Needs improvement'); field(md, 'Result').select_option('Approve with conditions'); field(md, 'Notes').fill('Two late COAs this year')
    md.get_by_role('button', name='Save review').click(); pg.wait_for_selector('.msg >> text=Review saved')
    f = sup('Futurola USA'); check(f['status'] == 'conditional' and f['last_review'] == TODAY.isoformat(), 'review sets conditional + last review')
    pg.wait_for_selector('.md >> text=Two late COAs this year', timeout=5000); check(pg.locator('.md').locator('text=Two late COAs this year').count() == 1, 'review shown in history')
    # disqualify
    pg.locator('.md').get_by_role('button', name='Disqualify').click(); md = pg.locator('.md')
    check(md.get_by_role('button', name='Disqualify').is_disabled(), 'disqualify needs a reason')
    md.locator('textarea').fill('Failed contamination test on two lots'); md.get_by_role('button', name='Disqualify').click(); pg.wait_for_selector('.msg >> text=Disqualified Futurola USA')
    check(sup('Futurola USA')['status'] == 'disqualified' and pg.locator('.md').get_by_role('button', name='Delete').count() == 0 and pg.locator('.md').get_by_role('button', name='Edit').count() == 0, 'disqualified: no edit, no delete (was approved)')
    pg.locator('.md').get_by_role('button', name='Close').click()
    # emergency supplier
    pg.get_by_role('button', name='+ Add supplier').click(); md = pg.locator('.md')
    field(md, 'Supplier name').fill('Rush Packaging'); field(md, 'Category / type').select_option('Packaging'); field(md, 'Status').select_option('emergency')
    md.get_by_role('button', name='Add supplier').click(); check(md.locator('.msg.err', has_text='checked before use').count() == 1, 'emergency supplier needs verification note')
    field(md, 'How materials are checked before use').fill('Visual inspection and spec check of every lot'); md.get_by_role('button', name='Add supplier').click(); pg.wait_for_selector('.msg >> text=Added Rush Packaging')
    check(sup('Rush Packaging')['status'] == 'emergency', 'emergency supplier recorded')
    pg.locator('.md').get_by_role('button', name='Delete').click(); pg.wait_for_selector('.msg >> text=Deleted Rush Packaging')
    check(not any(x['name'] == 'Rush Packaging' for x in T['hx_suppliers']), 'never-approved supplier can be deleted')
    # filters + print
    pg.locator('select').filter(has=pg.locator('option', has_text='Every status')).select_option('ACTIVE')
    check(pg.locator('.card', has_text='Green Lab').count() == 1 and pg.locator('.card', has_text='Futurola USA').count() == 0, 'status filter')
    pg.screenshot(path=OUT + 'suppliers.png')
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Approved supplier list').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('Approved supplier list' in html and 'Green Lab' in html and 'Futurola USA' in html and 'Failed contamination' in html and 'L-2231' in html, 'printable approved supplier list (incl. disqualified with reason)')
    # standards evidence
    T['hx_standards'].append({'id': 'st1', 'code': 'CSQ-MFG', 'name': 'CSQ', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 'st1', 'target_level': 1, 'status': 'Following'})
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    rr = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile(r'^2A\.11$'))).first; rr.locator('div.row').first.click()
    check(rr.locator('text=Approved supplier list').count() >= 1 and rr.locator('text=1 approved').count() >= 1, '2A.11 shows live supplier evidence')
    rr2 = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile(r'^2A\.12\.9$'))).first; rr2.locator('div.row').first.click()
    check(rr2.locator('text=not approved: Cheap Labs LLC').count() == 1, '2A.12.9 flags lab used without approval')
    # Edit-level user
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'suppliers': 'editor'}
    pg.reload(); pg.get_by_role('button', name='Suppliers', exact=True).click(); pg.wait_for_selector('.card >> text=Green Lab')
    pg.locator('.card', has_text='Green Lab').first.click()
    check(pg.locator('.md').get_by_role('button', name='Edit').count() == 1 and pg.locator('.md').get_by_role('button', name='Record review').count() == 0 and pg.locator('.md').get_by_role('button', name='Disqualify').count() == 0, 'Edit level: edit only, no approve/review/disqualify')
    pg.locator('.md').get_by_role('button', name='Close').click()
    pg.get_by_role('button', name='+ Add supplier').click(); check(field(pg.locator('.md'), 'Status').locator('option').count() == 2, 'Edit level can add pending or emergency only')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
