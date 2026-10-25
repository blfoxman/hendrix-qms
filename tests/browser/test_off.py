import os, re, subprocess, threading, http.server, functools, socketserver, shutil, tempfile
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 40: kiosks keep working without internet (outbox on the tablet + hx_kiosk_sync on the real database)
errors = []
PGDB = os.environ.get('HX_PGDB', 'hxtest')
MEM = '44444444-4444-4444-4444-444444444444'   # a person only this test uses
def pg(sql):
    return subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB, '-c', sql], capture_output=True, text=True).stdout.strip()
pg("insert into hx_profiles(id, name, email, role, approved) values ('%s','Olga Off','olga@x','member',true) on conflict (id) do nothing" % MEM)
pg("set session_replication_role=replica; delete from hx_time_clock where profile_id='%s'; delete from hx_badges where profile_id='%s'; "
   "insert into hx_badges(profile_id, code, badge_no) values ('%s','OFFMEM','9041'); update hx_profiles set license_ids='{lic-mo}', approved=true where id='%s'; "
   "delete from hx_facility_log where performed_by='Offline Olga'; delete from hx_visitor_log where visitor_name='Offline Otto';" % (MEM, MEM, MEM, MEM))
NET = {'down': False, 'sync': []}
def db_call(fn, args):
    # run the real kiosk function as the anonymous kiosk role
    vs = []; names = []
    for i, (k, v) in enumerate(args.items()):
        vs += ['-v', 'a%d=%s' % (i, json.dumps(v) if isinstance(v, (dict, list)) else str(v))]; names.append("%s => :'a%d'" % (k, i))
    out = subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB] + vs, input="set role anon;\nselect to_jsonb(%s(%s))::text;\n" % (fn, ', '.join(names)), capture_output=True, text=True)
    if out.returncode or 'ERROR' in out.stderr: return None, out.stderr.split('ERROR:')[-1].strip().split('\n')[0]
    return json.loads(out.stdout.strip().split('\n')[-1]), None
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    if u.startswith(SB) and NET['down']: return route.abort('internetdisconnected')
    for fn in ('hx_kiosk_sync', 'hx_kiosk_clock'):
        if path.endswith('/rpc/' + fn):
            a = json.loads(request.post_data)
            if fn == 'hx_kiosk_sync': NET['sync'].append(a)
            r, e = db_call(fn, a)
            return route.fulfill(status=400 if e else 200, content_type='application/json', body=json.dumps({'message': e} if e else r))
    if path.endswith('/rpc/hx_kiosk_log_add'):
        r, e = db_call('hx_kiosk_log_add', json.loads(request.post_data))
        return route.fulfill(status=400 if e else 200, content_type='application/json', body=json.dumps({'message': e} if e else r))
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
def scan(p, code):
    p.keyboard.type(code, delay=5); p.keyboard.press('Enter')
def outbox(p): return json.loads(p.evaluate('localStorage.getItem("hx_outbox")') or '[]')
def online(p): p.evaluate('window.dispatchEvent(new Event("online"))')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1100, 'height': 950}); ctx.route('**/*', handle)
    k = ctx.new_page(); k.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    # ---- time clock ----
    k.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Scan your badge')
    NET['down'] = True
    scan(k, 'OFFMEM'); k.wait_for_selector('text=Scan saved on this tablet')
    check(len(outbox(k)) == 1 and outbox(k)[0]['p']['code'] == 'OFFMEM', 'no internet: the scan is saved on the tablet')
    check(k.locator('.obar', has_text='1 entry saved on this tablet').count() == 1, 'kiosk shows what is waiting')
    # pretend the first scan was two hours ago (the tablet was offline all that time)
    k.evaluate("(()=>{const l=JSON.parse(localStorage.getItem('hx_outbox'));l[0].at=new Date(Date.now()-7200000).toISOString();localStorage.setItem('hx_outbox',JSON.stringify(l));})()")
    k.wait_for_timeout(4700)
    scan(k, 'OFFMEM'); k.wait_for_selector('text=Scan saved on this tablet')
    k.wait_for_timeout(4700)
    scan(k, 'NOPE99'); k.wait_for_selector('text=Scan saved on this tablet')
    check(len(outbox(k)) == 3, 'three scans waiting')
    # still offline after a reload: the kiosk starts from what it kept
    k.reload(); k.wait_for_selector('text=Scan your badge')
    check(k.locator('.obar', has_text='3 entries saved').count() == 1, 'reload without internet: kiosk starts and keeps the waiting scans')
    # internet back
    NET['down'] = False; online(k)
    k.wait_for_selector('text=Not accepted by Hendrix')
    rows = pg("select string_agg(event_type||':'||offline::text||':'||(abs(extract(epoch from ts-(now()-interval '2 hours')))<120)::text, ',' order by ts) from hx_time_clock where profile_id='%s'" % MEM)
    check(rows == 'entry:true:true,break1_out:true:false', 'sent in scan order: entry kept the time 2 hours ago, then the break (%s)' % rows)
    check(len(outbox(k)) == 0 and k.locator('.obar', has_text='entries saved').count() == 0, 'outbox empty after sending')
    check('Badge not recognized.' in k.locator('.obar').inner_text(), 'refused scan is shown to the people at the kiosk')
    # the same item sent again (a dropped answer) is not recorded twice
    again, _ = db_call('hx_kiosk_sync', NET['sync'][0])
    check(again.get('duplicate') is True and pg("select count(*) from hx_time_clock where profile_id='%s'" % MEM) == '2', 'resending an item does not make a second punch')
    k.locator('.obar').get_by_role('button', name='OK').click()
    check(k.locator('.obar').count() == 0, 'manager clears the refused list')
    # online again: the live kiosk works as before
    k.wait_for_timeout(4700)
    scan(k, 'OFFMEM'); k.wait_for_selector('text=Already recorded')
    check(len(outbox(k)) == 0, 'online: scans go straight to Hendrix (a scan within 60 s of the synced one is the same scan)')
    k.screenshot(path=OUT + 'off_clock.png')
    # ---- facility log ----
    k.goto(BASE + '?kiosk=log&type=environmental&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Environmental Monitoring Log')
    NET['down'] = True; k.reload(); k.wait_for_selector('text=Environmental Monitoring Log')
    check(True, 'log kiosk opens without internet (set-up kept on the tablet)')
    field(k.locator('.box'), 'Performed By').fill('Offline Olga'); field(k.locator('.box'), 'Sampling Location').fill('Drain 2'); sign(k)
    k.get_by_role('button', name='Submit entry').click(); k.wait_for_selector('text=Saved on this tablet (no internet)')
    check(len(outbox(k)) == 1 and outbox(k)[0]['kind'] == 'log' and outbox(k)[0]['p']['type'] == 'environmental', 'log entry saved on the tablet')
    NET['down'] = False; k.get_by_role('button', name='Send now').click(); k.wait_for_function('!JSON.parse(localStorage.getItem("hx_outbox")||"[]").length')
    check(pg("select offline::text||','||(performed_at < created_at)::text||','||source from hx_facility_log where performed_by='Offline Olga'") == 'true,true,kiosk', 'log entry arrived, marked offline with the time it was done')
    # ---- visitors ----
    k.goto(BASE + '?kiosk=visitor&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Facility GMP rules for visitors')
    NET['down'] = True
    field(k, 'Full name').fill('Offline Otto'); field(k, 'Purpose of visit').select_option(index=1); sign(k)
    k.get_by_role('button', name='No', exact=True).click(); k.locator('label', has_text='I have read the GMP rules').locator('input').check()
    k.get_by_role('button', name='Sign in', exact=True).last.click(); k.wait_for_selector('text=saved on this tablet')
    k.get_by_role('button', name='Done').click(); k.get_by_role('button', name='Sign out', exact=True).click()
    k.wait_for_selector('text=signing out works again when the internet is back')
    check(True, 'sign-out list: clear message without internet')
    NET['down'] = False; online(k); k.wait_for_function('!JSON.parse(localStorage.getItem("hx_outbox")||"[]").length')
    check(pg("select offline::text||','||gmp_ack::text from hx_visitor_log where visitor_name='Offline Otto'") == 'true,true', 'visitor sign-in arrived, marked offline')
    ctx.close()

    # ---- the kiosk page itself opens without internet (service worker) ----
    tmp = tempfile.mkdtemp()
    shutil.copy(os.path.join(HERE, '..', '..', 'sw.js'), tmp)
    open(os.path.join(tmp, 'index.html'), 'w', encoding='utf8').write(HTML)
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(Q, directory=tmp)); port = srv.server_address[1]
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    LOCAL = 'http://127.0.0.1:%d/' % port
    def handle2(route, request):
        if request.url.startswith(LOCAL): return route.continue_()
        return handle(route, request)
    ctx2 = b.new_context(viewport={'width': 1000, 'height': 800}, service_workers='allow'); ctx2.route('**/*', handle2)
    w = ctx2.new_page(); w.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    url = LOCAL + 'index.html?kiosk=clock&state=st-mo&lic=lic-mo&sw=1'
    w.goto(url); w.wait_for_selector('text=Scan your badge')
    w.evaluate('navigator.serviceWorker.ready.then(()=>true)')
    # in the test the service worker cannot reach the CDN (only page requests are routed): put the libraries in its cache
    VMAP = [('react.production', 'react/umd/react.production.min.js'), ('react-dom.production', 'react-dom/umd/react-dom.production.min.js'), ('qrcode.min', 'qrcodejs/qrcode.min.js'), ('jspdf.umd', 'jspdf/dist/jspdf.umd.min.js')]
    for src in w.evaluate('Array.from(document.querySelectorAll("script[src]")).map(x=>x.src)'):
        f = next(v for k2, v in VMAP if k2 in src)
        w.evaluate('([u,t])=>caches.open("hendrix-kiosk-v1").then(c=>c.put(u,new Response(t,{headers:{"Content-Type":"application/javascript"}})))', [src, open(VENDOR + f).read()])
    w.wait_for_function('caches.open("hendrix-kiosk-v1").then(c=>c.match(location.origin+location.pathname)).then(m=>window.__pg=!!m) && window.__pg', timeout=15000)
    w.reload(); w.wait_for_selector('text=Scan your badge')
    check(w.evaluate('!!navigator.serviceWorker.controller'), 'kiosk page is kept by the service worker')
    srv.shutdown(); srv.server_close(); NET['down'] = True
    w.reload(); w.wait_for_selector('text=Scan your badge', timeout=15000)
    check(True, 'kiosk page opens again with no internet at all (page from the tablet, set-up from the tablet)')
    scan(w, 'OFFMEM'); w.wait_for_selector('text=Scan saved on this tablet')
    check(True, 'and keeps saving scans')
    NET['down'] = False
    ctx2.close(); shutil.rmtree(tmp, ignore_errors=True)
    b.close()
pg("set session_replication_role=replica; delete from hx_time_clock where profile_id='%s';" % MEM)
print('\nJS/assert errors:', errors if errors else 'none')
