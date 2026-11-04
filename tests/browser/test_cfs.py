# Missouri CFS checklist: food safety SOP pack, GMP Hygiene Walk, private Employee Illness and Exclusion Log, person in charge role
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_sops'].append({'id': 'sop-old', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Handwashing and Hand and Arm Hygiene', 'sop_number': 'SOP-GEN-009', 'version': '1.0', 'status': 'published',
                     'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'steps': [], 'folder': 'General', 'category': '', 'description': '', 'regulatory_references': [], 'attachments': []})
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    # SOP pack
    pg.get_by_role('button', name='SOPs', exact=True).click(); pg.wait_for_selector('text=12 of 13 food safety SOPs are not in Hendrix yet')
    pg.locator('.card.gold', has_text='food safety SOPs').get_by_role('button', name='Add them').click(); md = pg.locator('.md')
    check(md.locator('label', has_text='Handwashing and Hand and Arm Hygiene').locator('.badge', has_text='In Hendrix').count() == 1, 'an SOP already in Hendrix (same title) is not added again')
    md.get_by_role('button', name='Add 12 SOPs as drafts').click(); pg.wait_for_selector('.msg >> text=Added 12 food safety SOPs as drafts'); check(pg.locator('text=food safety SOPs are not in Hendrix yet').count() == 0 and pg.locator('.msg.err', has_text='Added 12').count() == 0, 'banner gone once all are in; message not shown as an error')
    new = [s for s in T['hx_sops'] if s['sop_number'].startswith('SOP-CFS-')]
    check(len(new) == 12 and all(s['status'] == 'draft' and s['generated_content']['steps'] and s['regulatory_references'] for s in new), '12 SOPs added as drafts with steps and references')
    ill = next(s for s in new if s['title'].startswith('Employee Health'))
    check(ill['sop_number'] == 'SOP-CFS-003' and ill['folder'] == 'HR' and any('117.10(a)' in r for r in ill['regulatory_references']) and any('24 hours' in x['instruction'] for x in ill['generated_content']['steps']), 'sick policy: 21 CFR 117.10(a), return after 24 hours, HR folder')
    pg.locator('.card', has_text='Employee Health, Illness Reporting').first.click(); pg.wait_for_selector('.md >> text=Return to work')
    check(pg.locator('.md').locator('text=Reportable symptoms').count() >= 1, 'SOP opens with its definitions and steps')
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5); pg.wait_for_timeout(300)
    pg.get_by_role('button', name='Food safety SOP pack').click(); md = pg.locator('.md')
    check(md.get_by_role('button', name='All SOPs are in Hendrix').is_disabled(), 'pack again: nothing left to add')
    md.get_by_role('button', name='Cancel').click()
    # GMP walk
    pg.get_by_role('button', name='Facility Logs').click(); pg.locator('.tabs button', has_text='GMP Hygiene Walk').click()
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    for sel in md.locator('select').all():
        opts = sel.locator('option').all_inner_texts()
        if 'Pass' in opts and 'Fail' in opts: sel.select_option('Pass')
    field(md, 'No food, drinks, gum or tobacco').select_option('Fail')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_timeout(300)
    check(md.locator('.msg.err').count() == 1 and len([r for r in T['hx_facility_log'] if r['log_type'] == 'gmp_walk']) == 0, 'a Fail needs a corrective action')
    field(md, 'Corrective Action (for every Fail)').fill('Water bottle removed from Gummy Room; operator reminded')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_timeout(800)
    w = [r for r in T['hx_facility_log'] if r['log_type'] == 'gmp_walk']
    check(len(w) == 1 and w[0]['result'] == 'Fail' and w[0]['data']['hair'] == 'Pass', 'GMP walk saved with the failed item')
    # illness log: no QR, open until return
    pg.locator('.tabs button', has_text='Employee Illness and Exclusion').click(); pg.wait_for_selector('text=Each time an employee')
    check(pg.locator('text=Kiosk QR - Employee Illness').count() == 0, 'illness log has no QR form')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    field(md, 'Employee').fill('Lee Worker'); field(md, 'Recorded By (person in charge)').fill('Sam')
    field(md, 'Reason (category only').select_option('Vomiting'); field(md, 'Action').select_option('Excluded - sent home / not allowed in')
    md.get_by_role('button', name='Submit entry').click(); pg.wait_for_timeout(800)
    i = [r for r in T['hx_facility_log'] if r['log_type'] == 'illness']
    check(len(i) == 1 and i[0]['result'] == 'Open', 'exclusion stays open until the return date')
    # access: Facility Logs (all) never opens the illness log
    check("illness:'hr_health'" in HTML and not re.match(r'^logs_', 'hr_health') and "if(m.priv)return;" in HTML, 'illness log uses its own access setting (not Facility Logs (all), skipped by the All buttons)')
    check("'Person in charge (manufacturing)','Person in charge backup'" in HTML, 'org chart: person in charge and backup roles')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
