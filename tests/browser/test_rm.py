# Team and Access: Remove from Hendrix (people who left), Restore, delete a sign-up request (step 51)
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
T['hx_profiles'] += [{'id': 'u-ana', 'name': 'Ana Lopez', 'email': 'ana@x', 'role': 'member', 'approved': True, 'role_ids': [], 'license_ids': [], 'perms': {'sops': 'editor'}, 'created_at': '2026-02-01'},
                     {'id': 'u-req', 'name': 'Random Signup', 'email': 'rs@x', 'role': 'member', 'approved': False, 'role_ids': [], 'license_ids': [], 'perms': {}, 'created_at': '2026-11-15'}]
CALLS = []
def handle_r(route, request):
    u = request.url
    for fn in ('hx_admin_remove_user', 'hx_admin_restore_user', 'hx_admin_delete_request'):
        if '/rest/v1/rpc/' + fn in u:
            b = json.loads(request.post_data); CALLS.append((fn, b)); p = next(x for x in T['hx_profiles'] if x['id'] == b['p_user'])
            if fn == 'hx_admin_remove_user': p.update({'approved': False, 'role': 'member', 'role_ids': [], 'perms': {}, 'removed_at': '2026-11-16T15:00:00Z', 'removed_by': 'Sam', 'removed_reason': b['p_reason']})
            elif fn == 'hx_admin_restore_user': p.update({'removed_at': None, 'removed_by': None, 'removed_reason': None})
            else: T['hx_profiles'].remove(p)
            return route.fulfill(status=200, content_type='application/json', body='true')
    return handle(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle_r)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    dialogs = []
    pg.on('dialog', lambda d: (dialogs.append(d.message), d.accept()))
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    pg.locator('.nav').get_by_role('button', name='Team and Access').click()
    pg.locator('tr', has_text='Sam').get_by_role('button', name='Manage').click(); md = pg.locator('.md')
    check(md.get_by_role('button', name='Remove...').count() == 0, 'no Remove for yourself')
    md.get_by_role('button', name='Cancel').last.click()
    pg.locator('tr', has_text='Ana Lopez').get_by_role('button', name='Manage').click(); md = pg.locator('.md')
    md.get_by_role('button', name='Remove...').click(); md.get_by_role('button', name='Remove from Hendrix').click()
    check(md.locator('.msg.err', has_text='Write why this person is removed').count() == 1 and not CALLS, 'a reason is required')
    md.locator('input[placeholder^="e.g. Left the company"]').fill('Left the company on 11/14/2026')
    md.get_by_role('button', name='Remove from Hendrix').click(); pg.wait_for_selector('.msg >> text=Removed Ana Lopez from Hendrix.')
    check(CALLS[-1] == ('hx_admin_remove_user', {'p_user': 'u-ana', 'p_reason': 'Left the company on 11/14/2026'}) and any('Everything they signed or recorded stays' in d for d in dialogs), 'removed with the reason, after a confirmation that records stay')
    pg.wait_for_selector('h3:has-text("Removed (1)")')
    check(pg.locator('tr', has_text='Ana Lopez').count() == 0 and pg.locator('h3', has_text='Removed (1)').count() == 1, 'removed person leaves the team list; Removed (1) shown: %d %d' % (pg.locator('tr', has_text='Ana Lopez').count(), pg.locator('h3', has_text='Removed (1)').count()))
    pg.get_by_role('button', name='Show').click()
    row = pg.locator('tr', has_text='Ana Lopez')
    check('Left the company on 11/14/2026' in row.inner_text() and 'by Sam' in row.inner_text(), 'removed list shows when, by whom and why')
    row.get_by_role('button', name='Restore').click(); pg.wait_for_selector('.msg >> text=Restored Ana Lopez')
    check(pg.locator('.card.gold', has_text='waiting for approval').locator('tr', has_text='Ana Lopez').count() == 1, 'restored person waits for approval')
    # a sign-up request that was never approved: delete
    pg.locator('tr', has_text='Random Signup').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.get_by_role('button', name='Delete request').click(); pg.wait_for_selector('.msg >> text=Removed Random Signup (sign-up request deleted).')
    check(CALLS[-1][0] == 'hx_admin_delete_request' and pg.locator('tr', has_text='Random Signup').count() == 0, 'sign-up request deleted')
    # a removed (blocked) account trying to sign in
    pg.evaluate('localStorage.removeItem("hx_session")'); pg.reload(); pg.wait_for_selector('.auth')
    check("/banned/i.test(m)?'Your access to Hendrix was removed." in HTML, 'a blocked account gets "Your access to Hendrix was removed" at sign-in')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
