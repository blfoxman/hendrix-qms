# Paper SOP records: effective date from the paper SOP and signatures made on paper (step 50), shown as "signed on paper"
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
ROSTER = [{'id': 'u-ana', 'name': 'Ana Lopez', 'role_ids': [], 'license_ids': ['lic-mo'], 'is_admin': False},
          {'id': 'u-jakob', 'name': 'Jakob Neu', 'role_ids': [], 'license_ids': ['lic-mo'], 'is_admin': False},
          {'id': 'u-ben', 'name': 'Ben Ortiz', 'role_ids': [], 'license_ids': ['lic-mo'], 'is_admin': False}]
for i, n in enumerate(['SOP-PR-001', 'SOP-PR-002']):
    T['hx_sops'].append({'id': 'sop-p%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Paper SOP %d' % (i + 1), 'sop_number': n, 'version': '1.0', 'status': 'published',
                         'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'steps': [{'n': 1, 'title': 'Do', 'text': 'Do it.'}], 'folder': 'General', 'category': '', 'description': '',
                         'regulatory_references': [], 'attachments': [], 'effective_date': '2026-11-01', 'next_review': '2027-11-01', 'approved_by': 'Sam', 'approved_at': '2026-11-10T16:00:00Z'})
T['hx_sop_acks'].append({'id': 'ack-ana', 'sop_id': 'sop-p0', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'version': '1.0', 'user_id': 'u-ana', 'name': 'Ana Lopez', 'role_names': '', 'signature': None, 'at': '2026-11-05T15:00:00Z'})
CALLS = []
def handle_p(route, request):
    u = request.url
    if '/rest/v1/rpc/hx_sop_roster' in u:
        return route.fulfill(status=200, content_type='application/json', body=json.dumps(ROSTER))
    if '/rest/v1/rpc/hx_sop_paper_records' in u:
        b = json.loads(request.post_data); CALLS.append(b); new = upd = 0
        for s in T['hx_sops']:
            if s['id'] not in b['p_sop_ids']: continue
            s['effective_date'] = b['p_on']; s['next_review'] = str(int(b['p_on'][:4]) + 1) + b['p_on'][4:]
            for p in ROSTER:
                if p['id'] not in b['p_user_ids']: continue
                a = next((x for x in T['hx_sop_acks'] if x['sop_id'] == s['id'] and x['user_id'] == p['id']), None)
                if a: a.update({'paper_on': b['p_on'], 'paper_by': 'Sam', 'paper_note': b['p_note']}); upd += 1
                else:
                    T['hx_sop_acks'].append({'id': 'ackp-' + s['id'] + p['id'], 'sop_id': s['id'], 'state_id': 'st-mo', 'license_id': 'lic-mo', 'version': s['version'], 'user_id': p['id'], 'name': p['name'], 'role_names': '',
                                             'signature': None, 'at': '2026-11-13T15:00:00Z', 'paper_on': b['p_on'], 'paper_by': 'Sam', 'paper_note': b['p_note']}); new += 1
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'sops': len(b['p_sop_ids']), 'new': new, 'updated': upd}))
    return handle(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle_p)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    dialogs = []
    pg.on('dialog', lambda d: (dialogs.append(d.message), d.accept()))
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    pg.get_by_role('button', name='SOPs', exact=True).click(); pg.wait_for_selector('text=Paper SOP 1')
    pg.get_by_role('button', name='Paper records').click(); md = pg.locator('.md')
    check(md.locator('label', has_text='SOP-PR-001 Paper SOP 1').locator('input').is_checked() and md.locator('label', has_text='Jakob Neu').locator('input').is_checked(), 'all published SOPs and all people are ticked to start')
    md.get_by_role('button', name='Record paper records').click()
    check(md.locator('.msg.err', has_text='Enter the date written on the paper.').count() == 1 and not CALLS, 'the paper date is required')
    md.locator('input[type=date]').fill('2026-05-07')
    md.locator('label', has_text='Jakob Neu').locator('input').uncheck()
    md.get_by_role('button', name='Record paper records').click(); pg.wait_for_selector('.msg >> text=Saved paper records')
    c = CALLS[-1] if CALLS else {}
    check(c.get('p_on') == '2026-05-07' and sorted(c.get('p_user_ids', [])) == ['u-ana', 'u-ben'] and sorted(c.get('p_sop_ids', [])) == ['sop-p0', 'sop-p1'] and c.get('p_note') == 'Signed paper copies', 'saved for the chosen SOPs and people (Jakob left out), date and note')
    check(any('May 7, 2026' in d and 'entered from paper' in d for d in dialogs), 'asks to confirm, saying it is entered from paper')
    check(pg.locator('.msg', has_text='4 signatures marked as signed on paper').count() == 1, 'result message: ' + pg.locator('.msg').first.inner_text())
    pg.locator('.card', has_text='Paper SOP 1').first.click(); md = pg.locator('.md'); md.locator('text=Ana Lopez').first.wait_for()
    t = md.inner_text()
    a = next((x for x in T['hx_sop_acks'] if x['sop_id'] == 'sop-p0' and x['user_id'] == 'u-ana'), {})
    check('signed on paper May 7, 2026' in t and not any(x['user_id'] == 'u-jakob' for x in T['hx_sop_acks']) and a.get('at') == '2026-11-05T15:00:00Z', 'signature list shows "signed on paper May 7, 2026"; Jakob not added; Ana keeps her Hendrix signing time')
    check(md.locator('[title*="entered Nov 13, 2026 by Sam"]').count() >= 1, 'hover shows when and by whom it was entered')
    check('2026-05-07' in t and 'May 7, 2026 (paper SOP; entered in Hendrix Nov 10, 2026)' in t and 'Nov 1, 2027' not in t, 'SOP shows the paper date: effective 2026-05-07 and approved May 7, 2026 (paper SOP)')
    check('2027-05-07' in t, 'next review a year after the paper date')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
