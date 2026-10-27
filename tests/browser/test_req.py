import os, re, base64, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 43: Maintenance / Purchase Requests and sign-in on QR forms (the save goes to the real database function)
errors = []
PGDB = os.environ.get('HX_PGDB', 'hxtest')
MEM = '22222222-2222-2222-2222-222222222222'
PW = 'Mem-Pass-2026'
def pg(sql): return subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB, '-c', sql], capture_output=True, text=True).stdout.strip()
pg("set session_replication_role=replica; delete from hx_facility_log where log_type in ('maintenance_request','purchase_request') or performed_by_id is not null; delete from hx_notify_queue where kind='maintenance_urgent'; "
   "update hx_profiles set license_ids='{lic-mo}', approved=true, role='member', mfa_required=false, must_change_password=false where id='%s'" % MEM)
NET = {'down': False}
def jwt(uid): return 'h.' + base64.urlsafe_b64encode(json.dumps({'sub': uid, 'aal': 'aal1'}).encode()).decode().rstrip('=') + '.s'
def uid_of(request):
    t = (request.headers.get('authorization') or '').split(' ')[-1].split('.')
    try: return json.loads(base64.urlsafe_b64decode(t[1] + '=' * (-len(t[1]) % 4))).get('sub')
    except Exception: return None
def db_call(uid, fn, args):
    vs = []; names = []
    for i, (k, v) in enumerate(args.items()):
        if v is None: continue
        vs += ['-v', 'a%d=%s' % (i, json.dumps(v) if isinstance(v, (dict, list)) else str(v))]; names.append("%s => :'a%d'" % (k, i))
    out = subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB] + vs, input="set test.uid='%s';\nselect to_jsonb(%s(%s))::text;\n" % (uid or '', fn, ', '.join(names)), capture_output=True, text=True)
    if 'ERROR' in out.stderr: return None, out.stderr.split('ERROR:')[-1].strip().split('\n')[0]
    return json.loads(out.stdout.strip().split('\n')[-1]), None
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    if u.startswith(SB) and NET['down']: return route.abort('internetdisconnected')
    if path.endswith('/auth/v1/token'):
        b = json.loads(request.post_data)
        if b.get('password') == PW and b.get('email') == 'm@x': return jr(route, {'access_token': jwt(MEM), 'refresh_token': 'r', 'expires_in': 3600, 'user': {'id': MEM, 'email': 'm@x'}})
        return jr(route, {'error_description': 'Invalid login credentials'}, 400)
    for fn in ('hx_my_security', 'hx_kiosk_log_add_user'):
        if path.endswith('/rpc/' + fn):
            r, e = db_call(uid_of(request), fn, json.loads(request.post_data or '{}'))
            return jr(route, {'message': e}, 400) if e else jr(route, r)
    if path.endswith('/rest/v1/hx_profiles') and request.method == 'GET' and uid_of(request) == MEM:
        return jr(route, [{'id': MEM, 'name': 'Mem', 'email': 'm@x', 'approved': True, 'role': 'member', 'must_change_password': False}])
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def sign(p):
    p.locator('canvas').last.scroll_into_view_if_needed(); cv = p.locator('canvas').last.bounding_box()
    p.mouse.move(cv['x'] + 30, cv['y'] + 40); p.mouse.down(); p.mouse.move(cv['x'] + 200, cv['y'] + 90, steps=8); p.mouse.up()
def signin(k):
    k.wait_for_selector('text=Sign in with your own Hendrix account to fill this form')
    field(k, 'Email').fill('m@x'); field(k, 'Password').fill(PW); k.get_by_role('button', name='Sign in', exact=True).click()
    k.wait_for_selector('text=Signed in as')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    kc = b.new_context(viewport={'width': 420, 'height': 900}); kc.route('**/*', handle)
    k = kc.new_page(); k.on('pageerror', lambda e: errors.append('KJS: ' + str(e)))
    # ---- maintenance request by QR
    k.goto(BASE + '?kiosk=log&type=maintenance_request&state=st-mo&lic=lic-mo')
    k.wait_for_selector('text=Sign in with your own Hendrix account to fill this form')
    check(k.locator('text=Maintenance Request').count() >= 1 and k.locator('.nav').count() == 0, 'QR opens the Maintenance Request sign-in')
    field(k, 'Email').fill('m@x'); field(k, 'Password').fill('wrong'); k.get_by_role('button', name='Sign in', exact=True).click(); k.wait_for_selector('text=Invalid login credentials')
    field(k, 'Password').fill(PW); k.get_by_role('button', name='Sign in', exact=True).click(); k.wait_for_selector('text=Signed in as')
    check(field(k.locator('.box'), 'Requested By').input_value() == 'Mem' and field(k.locator('.box'), 'Requested By').get_attribute('readonly') is not None, 'name comes from the sign-in and cannot be changed')
    check(k.locator('canvas').count() == 0, 'requests need no drawn signature (the sign-in identifies the person)')
    field(k.locator('.box'), 'Area / Room').fill('Cart room'); field(k.locator('.box'), 'What needs fixing?').fill('Filler 2 is leaking oil')
    field(k.locator('.box'), 'Priority').select_option('Urgent - safety or production stopped')
    k.screenshot(path=OUT + 'req_maint.png', full_page=True)
    k.get_by_role('button', name='Send request').click(); k.wait_for_selector('text=Sent. Thank you, Mem.')
    row = pg("select performed_by||'|'||performed_by_id||'|'||result||'|'||source||'|'||(data->>'problem') from hx_facility_log where log_type='maintenance_request'")
    check(row == 'Mem|%s|Open|kiosk|Filler 2 is leaking oil' % MEM, 'maintenance request saved: verified name, Open, QR (%s)' % row)
    check(pg("select count(*) from hx_notify_queue where kind='maintenance_urgent'") == '1', 'urgent request queued for an email alert')
    k.get_by_role('button', name='Done - sign out').click(); k.wait_for_selector('text=Sign in with your own Hendrix account to fill this form')
    check(k.evaluate('localStorage.getItem("hx_session")') is None, 'Done - sign out signs the person out')
    # ---- purchase request
    k.goto(BASE + '?kiosk=log&type=purchase_request&state=st-mo&lic=lic-mo'); signin(k)
    field(k.locator('.box'), 'What is needed?').fill('Nitrile gloves, size L'); field(k.locator('.box'), 'Quantity').fill('10'); field(k.locator('.box'), 'Unit').select_option('Boxes')
    k.get_by_role('button', name='Send request').click(); k.wait_for_selector('.msg.err >> text=What is it for? is required.')
    field(k.locator('.box'), 'What is it for?').fill('Running low on the cart line')
    k.get_by_role('button', name='Send request').click(); k.wait_for_selector('text=Sent. Thank you, Mem.')
    check(pg("select result||'|'||(data->>'item_name')||'|'||(data->>'quantity')||'|'||(data->>'unit') from hx_facility_log where log_type='purchase_request'") == 'Requested|Nitrile gloves, size L|10|Boxes', 'purchase request saved as Requested')
    # ---- a regular log now needs sign-in + signature; offline it waits for the same person
    k.get_by_role('button', name='Send another').click()
    k.goto(BASE + '?kiosk=log&type=environmental&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Signed in as')
    field(k.locator('.box'), 'Sampling Location').fill('Drain 1')
    check(k.locator('canvas').count() == 1, 'regular logs still ask for the drawn signature')
    NET['down'] = True
    sign(k); k.get_by_role('button', name='Submit entry').click(); k.wait_for_selector('text=Saved on this tablet (no internet)')
    ob = json.loads(k.evaluate('localStorage.getItem("hx_outbox")') or '[]')
    check(len(ob) == 1 and ob[0]['kind'] == 'ulog' and ob[0]['p']['_uid'] == MEM, 'no internet: the signed-in entry waits on the tablet with its person')
    NET['down'] = False; k.evaluate('window.dispatchEvent(new Event("online"))'); k.wait_for_function('!JSON.parse(localStorage.getItem("hx_outbox")||"[]").length')
    check(pg("select count(*)||'|'||bool_and(offline) from hx_facility_log where log_type='environmental' and performed_by_id='%s'" % MEM) == '1|true', 'sent when the internet is back, under the same person, marked offline')
    kc.close()
    # ---- managers: status in Facility Logs
    T['hx_facility_log'].append({'id': 'fl-req1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'log_type': 'maintenance_request', 'item': 'Cart room', 'item_id': None,
        'data': {'date': '2026-10-27', 'requested_by': 'Mem', 'location': 'Cart room', 'problem': 'Filler 2 is leaking oil', 'priority': 'Urgent - safety or production stopped', 'status': 'Open'},
        'result': 'Open', 'performed_by': 'Mem', 'source': 'kiosk', 'created_at': '2026-10-27T15:00:00.000Z', 'voided': False})
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    p = ctx.new_page(); p.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    p.goto(BASE); p.wait_for_selector('.nav'); p.locator('.nav').get_by_role('button', name='Facility Logs').click()
    p.locator('button', has_text='Maintenance Request').first.click(); p.wait_for_selector('h2 >> text=Maintenance Request')
    check(p.locator('text=after signing in with their own Hendrix account').count() == 1, 'QR card says staff sign in')
    try: p.locator('td', has_text='Cart room').first.wait_for(timeout=10000); p.locator('.badge', has_text='1 open').first.wait_for(timeout=5000)
    except Exception: pass
    check(p.locator('.badge', has_text='1 open').count() == 1 and p.locator('td', has_text='Cart room').count() == 1, 'open request listed')
    p.get_by_role('button', name='Update status').click(); md = p.locator('.md')
    md.get_by_role('button', name='In progress', exact=True).click(); md.locator('textarea').fill('Technician coming Thursday'); md.get_by_role('button', name='Save status').click()
    p.wait_for_selector('.md', state='detached')
    r = next(x for x in T['hx_facility_log'] if x['id'] == 'fl-req1')
    check(r['result'] == 'In progress' and r['data']['status'] == 'In progress' and r['data']['status_note'] == 'Technician coming Thursday' and r['data']['status_by'] == 'Sam', 'manager updates the status with a note')
    a = [x for x in T['hx_audit_log'] if x.get('row_id') == 'fl-req1']
    check(a and a[-1]['reason'] == 'Status: In progress - Technician coming Thursday', 'status change in the audit trail with its reason')
    p.screenshot(path=OUT + 'req_panel.png', full_page=True)
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
