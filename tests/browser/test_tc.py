import re, datetime as dt, base64, struct, zlib
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
TODAY = dt.date.today().isoformat()
def iso(d): return d.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
T['hx_profiles'].append({'id': 'u-lee', 'name': 'Lee Park', 'email': 'lee@x', 'role': 'member', 'approved': True, 'license_ids': ['lic-mo'], 'role_ids': [], 'perms': {}, 'created_at': '2026-01-01'})
T['hx_time_clock'] = []; BADGES = {}; SEQ = ['entry', 'break1_out', 'break1_in', 'break2_out', 'break2_in', 'break3_out', 'break3_in', 'clockout']; CNT = [0]
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def person(pid): return next(p for p in T['hx_profiles'] if p['id'] == pid)
def newcode(): CNT[0] += 1; return 'CODE%08d' % CNT[0]
_h = handle
def handle(route, request):
    u = request.url; m = request.method; path = urllib.parse.urlparse(u).path
    if path.startswith('/rest/v1/rpc/'):
        fn = path.split('/')[-1]; b = json.loads(request.post_data or '{}')
        if fn == 'hx_badge_roster':
            out = []
            for p in T['hx_profiles']:
                if not p.get('approved') or not (p['role'] == 'admin' or not p.get('license_ids') or b['p_lic'] in p['license_ids']): continue
                bd = BADGES.get(p['id'])
                out.append({'id': p['id'], 'name': p['name'], 'email': p['email'], 'has_badge': bool(bd), **({k: bd[k] for k in ('badge_no', 'title', 'photo', 'zoom', 'pos_x', 'pos_y', 'code')} if bd else {}), 'issued_at': bd and '2026-10-24T10:00:00Z', 'issued_by': bd and 'Sam'})
            return jr(route, out)
        if fn == 'hx_badge_save':
            bd = BADGES.get(b['p_profile'])
            if not bd: bd = BADGES[b['p_profile']] = {'code': newcode(), 'badge_no': str(4000 + CNT[0])}
            bd.update({'title': b['p_title'], 'photo': b['p_photo'], 'zoom': b['p_zoom'], 'pos_x': b['p_x'], 'pos_y': b['p_y']})
            return jr(route, {'badge_no': bd['badge_no'], 'code': bd['code']})
        if fn == 'hx_badge_reissue':
            bd = BADGES[b['p_profile']]; bd['code'] = newcode(); return jr(route, {'badge_no': bd['badge_no'], 'code': bd['code']})
        if fn == 'hx_badge_lookup':
            hit = [(k, v) for k, v in BADGES.items() if v['code'] == b['p_code']]
            if not hit: return jr(route, None)
            p = person(hit[0][0]); return jr(route, {'name': p['name'], 'title': hit[0][1]['title'], 'photo': hit[0][1]['photo'], 'badge_no': hit[0][1]['badge_no'], 'valid': True})
        if fn == 'hx_kiosk_clock':
            hit = [(k, v) for k, v in BADGES.items() if v['code'] == b['p_code'].upper()]
            if not hit: return jr(route, {'error': 'Badge not recognized.'})
            pid, bd = hit[0]; p = person(pid); nw = dt.datetime.now(dt.timezone.utc)
            ev = sorted([x for x in T['hx_time_clock'] if x['profile_id'] == pid and x['event_date'] == b['p_date'] and not x['voided']], key=lambda x: x['ts'])
            base = {'name': p['name'], 'title': bd['title'], 'photo': bd['photo']}
            if ev and (nw - dt.datetime.fromisoformat(ev[-1]['ts'].replace('Z', '+00:00'))).total_seconds() < 60: return jr(route, {**base, 'event': ev[-1]['event_type'], 'ts': ev[-1]['ts'], 'repeat': True})
            if ev and ev[-1]['event_type'] == 'clockout': return jr(route, {**base, 'done': True})
            nxt = 'entry' if not ev else SEQ[SEQ.index(ev[-1]['event_type']) + 1]; late = False; lm = None
            if nxt.endswith('_in'):
                o = [x for x in ev if x['event_type'] == nxt.replace('_in', '_out')]
                if o:
                    el_ = (nw - dt.datetime.fromisoformat(o[-1]['ts'].replace('Z', '+00:00'))).total_seconds() / 60; lim = 30 if nxt == 'break2_in' else 15; late = el_ > lim; lm = round(el_ - lim) if late else 0
            r = {'id': 'tc%d' % len(T['hx_time_clock']), 'state_id': b['p_state'], 'license_id': b['p_lic'], 'profile_id': pid, 'person_name': p['name'], 'event_type': nxt, 'ts': iso(nw), 'event_date': b['p_date'], 'late': late, 'late_minutes': lm, 'source': 'kiosk', 'reason': '', 'recorded_by': 'Kiosk', 'voided': False}
            T['hx_time_clock'].append(r); return jr(route, {**base, 'event': nxt, 'ts': r['ts'], 'late': late, 'late_minutes': lm})
        if fn == 'hx_clock_fix':
            if not b['p_reason']: return jr(route, {'message': 'A reason is required.'}, 400)
            p = person(b['p_profile'])
            T['hx_time_clock'].append({'id': 'tcm%d' % len(T['hx_time_clock']), 'state_id': 'st-mo', 'license_id': b['p_lic'], 'profile_id': p['id'], 'person_name': p['name'], 'event_type': b['p_event'], 'ts': b['p_ts'], 'event_date': b['p_date'], 'late': False, 'late_minutes': None, 'source': 'manual', 'reason': b['p_reason'], 'recorded_by': 'Sam', 'voided': False})
            return jr(route, 'tcm')
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def png(w, h):
    raw = b''.join(b'\x00' + bytes([200, 150, 120]) * w for _ in range(h))
    def ch(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
open(OUT + 'face.png', 'wb').write(png(60, 80))
def scan(kp, text):
    kp.keyboard.type(text, delay=5); kp.keyboard.press('Enter')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    pg.wait_for_selector('.card.gold >> text=Time clock')
    check(pg.locator('.card.gold', has_text='Time clock').locator('text=0 on site now').count() == 1, 'dashboard: 0 on site now')
    check(pg.locator('text=Time Clock and Badges').count() >= 1 and pg.locator('.badge.off', has_text='Time Clock').count() == 0, 'time clock no longer on the coming-soon list')
    pg.get_by_role('button', name='Time Clock and Badges').click(); pg.wait_for_selector('text=No scans recorded for this date.')
    pg.locator('.tabs').get_by_role('button', name='Badges').click(); pg.wait_for_selector('text=Choose a person')
    check(pg.locator('.card .badge', has_text='No badge').count() == 2, 'two people at the license, no badges yet')
    pg.locator('div', has_text=re.compile('^Lee Park')).last.click(); pg.wait_for_selector('h3 >> text=Lee Park')
    field(pg, 'Title on the badge').fill('Extraction Technician')
    pg.locator('input[type=file]').first.set_input_files(OUT + 'face.png'); pg.wait_for_selector('text=Drag the photo')
    pg.get_by_role('button', name='Issue badge').click(); pg.wait_for_selector('.msg >> text=Badge issued - ID')
    code = BADGES['u-lee']['code']; check(BADGES['u-lee']['photo'].startswith('data:image/jpeg') and BADGES['u-lee']['title'] == 'Extraction Technician', 'badge issued with a square jpeg photo and title')
    card = pg.locator('.hxbadge'); check(card.locator('text=EXTRACTION TECHNICIAN').count() + card.locator('text=Extraction Technician').count() >= 1 and card.locator('svg rect').count() > 20 and card.locator('img[src^="data:image/png"]').count() == 1, 'card preview: title, Code 128 barcode, QR')
    pg.wait_for_selector('.card .badge.ok >> text=ID ')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print', exact=True).click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('size:2.125in 3.375in' in html.replace(' ', '').replace('size:2.125in3.375in', 'size:2.125in 3.375in') and 'hxbadge' in html and code in html, 'badge prints at CR80 size with its code'); w.close()
    pg.screenshot(path=OUT + 'badges.png')
    # kiosk
    kp = ctx.new_page(); kp.on('pageerror', lambda e: errors.append('KIOSK JS: ' + str(e)))
    kp.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); kp.wait_for_selector('text=Scan your badge')
    scan(kp, BASE + '?badge=' + code); kp.wait_for_selector('.kres >> text=Clock in')
    check(kp.locator('.kres >> text=Lee Park').count() == 1 and len(T['hx_time_clock']) == 1, 'kiosk: badge scan clocks Lee in')
    kp.wait_for_timeout(4800); scan(kp, code); kp.wait_for_selector('.kres >> text=Already recorded')
    check(len(T['hx_time_clock']) == 1, 'double scan within a minute is ignored (barcode text works too)')
    kp.wait_for_timeout(4800); scan(kp, 'NOPE12345'); kp.wait_for_selector('.kres >> text=Badge not recognized')
    kp.screenshot(path=OUT + 'kiosk_clock.png')
    # an hour later Lee went on break 20 minutes ago
    nw = dt.datetime.now(dt.timezone.utc); T['hx_time_clock'][0]['ts'] = iso(nw - dt.timedelta(hours=3))
    T['hx_time_clock'].append({**T['hx_time_clock'][0], 'id': 'tcb', 'event_type': 'break1_out', 'ts': iso(nw - dt.timedelta(minutes=20))})
    kp.wait_for_timeout(4800); scan(kp, BASE + '?badge=' + code); kp.wait_for_selector('.kres >> text=1st break')
    check(kp.locator('.kres >> text=5 min over the break limit').count() == 1, 'late return from a 15-minute break flagged (+5 min)')
    kp.close()
    pg.locator('.tabs').get_by_role('button', name='Sign-in sheet').click(); pg.reload(); pg.wait_for_selector('text=Quality standard')
    pg.get_by_role('button', name='Time Clock and Badges').click(); pg.wait_for_selector('td >> text=Lee Park')
    row = pg.locator('tr', has_text='Lee Park'); check(row.locator('span', has_text='+5').count() == 1 and row.locator('td').count() == 10, 'sign-in sheet: Lee with clock in, break out and late return')
    pg.get_by_role('button', name='+ Missed punch').click(); md = pg.locator('.md')
    field(md, 'Person').select_option(ADMIN); field(md, 'Time').fill(TODAY + 'T07:30'); md.get_by_role('button', name='Add punch').click(); pg.wait_for_selector('.md .msg.err >> text=reason')
    field(md, 'Reason').fill('Forgot badge, confirmed by Lee'); md.get_by_role('button', name='Add punch').click(); pg.wait_for_selector('.msg >> text=Missed punch added.')
    pg.wait_for_selector('tr:has-text("Sam") .badge:has-text("M")'); check(pg.locator('text=Missed punch Clock in').count() == 1, 'missed punch shown with M and the reason listed')
    pg.locator('tr', has_text='Sam').locator('span[title*="click to void"]').first.click(); md = pg.locator('.md'); md.locator('textarea').fill('Entered for the wrong person'); md.get_by_role('button', name=re.compile('Void')).last.click()
    pg.wait_for_selector('.msg >> text=Voided the punch.'); pg.wait_for_selector('text=Voided Clock in')
    check(next(x for x in T['hx_time_clock'] if x['source'] == 'manual')['voided'] is True, 'punch voided with a reason')
    pg.locator('.tabs').get_by_role('button', name='On site now').click(); pg.wait_for_selector('text=In since')
    check(pg.locator('.card', has_text='Lee Park').count() >= 1 and pg.locator('.card.gold', has_text='On site now').locator('.v').inner_text() == '1', 'on site now: Lee')
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print roll call').click()
    w = pop.value; w.wait_for_load_state(); check('roll call' in w.content() and 'Lee Park' in w.content(), 'printable emergency roll call'); w.close()
    pg.locator('.tabs').get_by_role('button', name='Badges').click(); pg.locator('div', has_text=re.compile('^Lee Park')).last.click(); pg.get_by_role('button', name='Re-issue (lost)').click()
    md = pg.locator('.md'); md.locator('textarea').fill('Badge lost in parking lot'); md.get_by_role('button', name='Re-issue').last.click(); pg.wait_for_selector('.msg >> text=Re-issued the badge')
    check(BADGES['u-lee']['code'] != code, 'lost badge re-issued with a new code')
    kp = ctx.new_page(); kp.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); kp.wait_for_selector('text=Scan your badge'); scan(kp, BASE + '?badge=' + code); kp.wait_for_selector('.kres >> text=Badge not recognized')
    check(True, 'old badge refused at the kiosk'); kp.close()
    vp = ctx.new_page(); vp.goto(BASE + '?badge=' + BADGES['u-lee']['code']); vp.wait_for_selector('text=Valid Hendrix badge')
    check(vp.locator('text=Lee Park').count() == 1, 'badge check page for someone scanning with a phone'); vp.close()
    bk = ctx.new_page(); bk.goto(BASE + '?kiosk=clock&state=st-mi&lic=lic-mo'); bk.wait_for_selector('text=not linked to an active license'); check(True, 'kiosk refuses a wrong state / license'); bk.close()
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card.gold >> text=Time clock')
    pg.locator('.card.gold', has_text='Time clock').locator('text=1 on site now').wait_for(timeout=8000); check(True, 'dashboard: 1 on site now')
    b.close()
    # camera mode (Michigan face + badge scan) with a fake camera showing a face patch and Lee's badge QR
    BADGES['u-lee']['code'] = 'CODE00000001'
    b2 = pw.chromium.launch(**LAUNCH,
        args=['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream', '--use-file-for-fake-video-capture=' + OUT + 'fakecam.mjpeg'])
    c2 = b2.new_context(viewport={'width': 1000, 'height': 900}, permissions=['camera']); c2.route('**/*', handle)
    kp = c2.new_page(); kp.on('pageerror', lambda e: errors.append('CAM JS: ' + str(e)))
    kp.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); kp.wait_for_selector('text=Scan your badge'); kp.get_by_role('button', name='Use camera').click()
    kp.wait_for_selector('text=Step 1', timeout=15000); kp.screenshot(path=OUT + 'kiosk_cam.png')
    kp.wait_for_selector('.kres >> text=Lee Park', timeout=30000)
    check(True, 'camera kiosk: face step, then the badge QR is read and the punch recorded')
    b2.close()
print('\nJS/assert errors:', errors if errors else 'none')
