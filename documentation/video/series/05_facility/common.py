# Shared setup for video 05 (facility): kit import, seed data, mock emulation of the database, helpers.
import os, sys, re, json, urllib.parse, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(HERE + '/../../kit'))
import hxvideo as hv
hv.set_project(HERE)
SNAP = os.path.abspath(HERE + '/../../index_snapshot2.html')
F = hv.field
LOG = []

# Keep pop-up windows clear of the burned-in captions (bottom ~120 CSS px): lift and shorten them a little.
CAP_CSS = '.main{padding-bottom:170px !important}.mo{padding:14px 14px 124px !important}.md{max-height:calc(100vh - 150px) !important}'


def setup():
    """facility seed (browser clock fixed by shots_facility.py: 2026-10-23 11:42 CDT) + database emulation."""
    ns = hv.load_setup('facility', snapshot=SNAP); T = ns['T']
    tick = [0]
    def now():                                   # database now(): just after 11:42 CDT on the fixed day
        tick[0] += 3; s = 16 * 3600 + 42 * 60 + tick[0]
        return '2026-10-23T%02d:%02d:%02d.000Z' % (s // 3600, s // 60 % 60, s % 60)
    ns['now'] = now
    h0 = ns['handle']
    def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
    ME = 'Sam Salari'
    def body(request):
        b = json.loads(request.post_data or '{}'); return b
    def rid(u):
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(u).query)); return q.get('id', '').split('.', 1)[-1]
    def nxt(tbl, pre, width=3):
        n = [int(re.sub(r'\D', '', x['number'].split('-')[-1]) or 0) for x in T.get(tbl, []) if x.get('number')]
        return '%s%0*d' % (pre, width, max(n + [0]) + 1)
    def handle(route, request):
        u = request.url; m = request.method
        if m != 'GET' and 'supabase' in u:
            LOG.append((m, u.split('.co', 1)[-1][:120], (request.post_data or '')[:600]))
        path = urllib.parse.urlparse(u).path
        if 'supabase' in u and path.startswith('/rest/v1/rpc/'):
            fn = path.split('/')[-1]; bd = body(request)
            if fn in ('hx_kiosk_visitor_in2', 'hx_kiosk_visitor_in'):
                p = bd['p']; row = {'id': 'vis-k%d' % len(T['hx_visitor_log']), 'state_id': 'st-mo', 'license_id': bd['p_lic'], 'visitor_name': p['visitor_name'].strip(), 'company': p.get('company', ''),
                     'purpose': p.get('purpose', ''), 'host': p.get('host', ''), 'vehicle': p.get('vehicle', ''), 'signature': p.get('signature'), 'gmp_ack': bool(p.get('gmp_ack')), 'ill': bool(p.get('ill')),
                     'time_in': now(), 'time_out': None, 'source': 'kiosk', 'voided': False}
                T['hx_visitor_log'].insert(0, row); return jr(route, row['id'])
            if fn == 'hx_kiosk_visitor_out':
                v = next(x for x in T['hx_visitor_log'] if x['id'] == bd['p_id']); v['time_out'] = now(); return jr(route, None)
            if fn == 'hx_kiosk_open_visitors':
                return jr(route, [{'id': v['id'], 'visitor_name': v['visitor_name'], 'time_in': v['time_in']} for v in T['hx_visitor_log'] if not v.get('time_out')])
            if fn == 'hx_badge_roster':
                out = []
                for p in T['hx_profiles']:
                    bg = ns['BADGES'].get(p['id'])
                    out.append({'id': p['id'], 'name': p['name'], 'email': p['email'], 'has_badge': bool(bg), **({k: bg[k] for k in ('badge_no', 'title', 'photo', 'zoom', 'pos_x', 'pos_y', 'code')} if bg else {}),
                                'issued_at': bg and bg.get('issued_at', '2026-09-02T15:00:00Z'), 'issued_by': bg and 'Sam Salari'})
                return jr(route, sorted(out, key=lambda x: x['name'].lower()))
            if fn == 'hx_badge_save':
                B = ns['BADGES']; old = B.get(bd['p_profile'])
                code = old['code'] if old else 'T8N3V5K2W7QH'; no = old['badge_no'] if old else '4160'
                B[bd['p_profile']] = {'code': code, 'badge_no': no, 'title': bd['p_title'], 'photo': bd['p_photo'], 'zoom': bd['p_zoom'], 'pos_x': bd['p_x'], 'pos_y': bd['p_y'], 'issued_at': (old or {}).get('issued_at', now())}
                return jr(route, {'code': code, 'badge_no': no})
            if fn == 'hx_kiosk_clock':
                B = ns['BADGES']; hit = [(k, v) for k, v in B.items() if v['code'] == bd['p_code'].upper()]
                if not hit: return jr(route, {'error': 'Badge not recognized.'})
                pid, bg = hit[0]; nm = next(x['name'] for x in T['hx_profiles'] if x['id'] == pid)
                order = ['entry', 'break1_out', 'break1_in', 'break2_out', 'break2_in', 'break3_out', 'break3_in', 'clockout']
                done = [x['event_type'] for x in T['hx_time_clock'] if x['profile_id'] == pid and not x['voided'] and x['event_date'] == ns['TODAY']]
                ev = next(e for e in order if e not in done); ts = now()
                T['hx_time_clock'].append({'state_id': 'st-mo', 'license_id': 'lic-mo', 'id': 'tc-k%d' % len(T['hx_time_clock']), 'profile_id': pid, 'person_name': nm, 'event_type': ev, 'ts': ts, 'event_date': ns['TODAY'],
                                           'late': False, 'late_minutes': None, 'source': 'kiosk', 'reason': '', 'recorded_by': 'Kiosk', 'created_at': ts, 'voided': False, 'void_reason': None})
                return jr(route, {'name': nm, 'title': bg['title'], 'photo': bg['photo'], 'event': ev, 'ts': ts, 'late': False, 'late_minutes': 0})
            if fn in ('hx_training_roster', 'hx_training_sop_acks', 'hx_training_shared', 'hx_line_map'):
                return jr(route, [])
        if 'supabase' in u and m == 'POST' and '/rest/v1/' in path and '/rpc/' not in path:
            tbl = path.split('/')[-1]; bd = body(request); rows = bd if isinstance(bd, list) else [bd]
            pre = {'hx_equipment': ('EQ-', 3), 'hx_chemicals': ('CHEM-', 3), 'hx_line_clearances': ('LC-2026-', 3), 'hx_rework': ('RW-2026-', 3)}
            if tbl in pre or tbl in ('hx_equipment_events', 'hx_env_tests'):
                for x in rows:
                    if tbl in pre and not x.get('number'): x['number'] = nxt(tbl, *pre[tbl])
                    x.setdefault('created_at', now()); x.setdefault('voided', False)
                    if tbl in ('hx_equipment', 'hx_chemicals', 'hx_rework'): x.setdefault('created_by', ME)
                    if tbl in ('hx_equipment_events', 'hx_env_tests', 'hx_line_clearances'): x.setdefault('recorded_by', ME)
                    if tbl == 'hx_line_clearances': x.setdefault('checked_at', x['created_at'])
                    if tbl == 'hx_chemicals' and x.get('status') == 'approved': x.update({'approved_by': ME, 'approved_at': now()})
                    if tbl == 'hx_equipment_events':
                        e = next((y for y in T['hx_equipment'] if y['id'] == x.get('equipment_id')), None)
                        if e and x.get('kind') == 'calibration' and x.get('result') == 'pass':
                            e['cal_last'] = x['done_on']
                            if x.get('next_due'): e['cal_due'] = x['next_due']
                            else:
                                d0 = dt.date.fromisoformat(x['done_on']); mm = d0.month - 1 + int(e.get('cal_interval_months') or 12)
                                e['cal_due'] = dt.date(d0.year + mm // 12, mm % 12 + 1, min(d0.day, 28)).isoformat()
                    T.setdefault(tbl, []).insert(0, x) if tbl in ('hx_line_clearances', 'hx_env_tests') else T.setdefault(tbl, []).append(x)
                return jr(route, rows, 201)
        if 'supabase' in u and m == 'PATCH' and path.split('/')[-1] in ('hx_chemicals', 'hx_rework'):
            tbl = path.split('/')[-1]; bd = body(request); row = next(x for x in T[tbl] if x['id'] == rid(u))
            if tbl == 'hx_chemicals' and bd.get('status') == 'approved' and row.get('status') != 'approved': bd.update({'approved_by': ME, 'approved_at': now()})
            if tbl == 'hx_rework' and bd.get('status') == 'approved' and row.get('status') != 'approved': bd.update({'approved_by': ME, 'approved_at': now()})
            row.update(bd); return jr(route, [row])
        return h0(route, request)
    ns['handle'] = handle
    return ns


def open_app(pw, ns, wait='.nav'):
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, fixed=ns['FIXED'], session=hv.session_script())
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector(wait); pg.wait_for_selector('text=Quality standard'); pg.add_style_tag(content=CAP_CSS); pg.wait_for_timeout(800)
    return b, ctx, pg


def navb(pg, name): return pg.locator('.nav').get_by_role('button', name=name, exact=True)
