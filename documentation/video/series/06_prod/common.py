# Shared setup for video 06 (prod): kit import, seeds, mock emulation of what the database stamps, helpers.
import os, sys, re, json, subprocess, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(HERE + '/../../kit'))
import hxvideo as hv
hv.set_project(HERE)
SCR = hv.SCR
SNAP = os.path.abspath(HERE + '/../../index_snapshot2.html')
F = hv.field
ME = 'Sam Salari'

# Keep pop-up windows clear of the burned-in captions (bottom ~120 CSS px): lift and shorten them a little.
CAP_CSS = '.main{padding-bottom:170px !important}.mo{align-items:flex-start !important;padding:14px 14px 124px !important}.md{max-height:calc(100vh - 150px) !important}'
CAP_INIT = "addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);});" % json.dumps(CAP_CSS)


def reseed_lm():
    """Fresh Line Map data in the lmtest Postgres copy (times are relative to the real now())."""
    subprocess.run(SCR + 'pg.sh lmtest -q -f - < ' + SCR + 'lm_seed.sql', shell=True, check=True, capture_output=True)
    subprocess.run([SCR + 'pg.sh', 'lmtest', '-qc', "set session_replication_role=replica; update hx_batches set voided=true where id not like 'lm%';"], check=True, capture_output=True)


def setup_lm():
    ns = hv.load_setup('lm', path=SCR + 'shots_lm.py', snapshot=SNAP)
    ns['T']['hx_profiles'][0]['name'] = ME
    return ns


def setup_prod():
    """prod seed + emulation of database stamps (numbers, who / when) the plain mock leaves out."""
    ns = hv.load_setup('prod', snapshot=SNAP); T = ns['T']
    T['hx_profiles'][0]['name'] = ME
    tick = [0]
    def now():                                    # database now(): just after 10:40 CDT on the fixed day
        tick[0] += 3; s = 15 * 3600 + 40 * 60 + tick[0]
        return '2026-10-24T%02d:%02d:%02d.000Z' % (s // 3600, s // 60 % 60, s % 60)
    ns['now'] = now; ns['NOWD'] = '2026-10-24T15:40:00Z'
    h0 = ns['handle']
    def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
    def nxt(tbl, pre):
        n = [int(x['number'].split('-')[-1]) for x in T.get(tbl, []) if re.match(r'^' + re.escape(pre) + r'\d+$', x.get('number') or '')]
        return '%s%03d' % (pre, max(n + [0]) + 1)
    def handle(route, request):
        u = request.url; m = request.method; path = urllib.parse.urlparse(u).path; tbl = path.split('/')[-1]
        if 'supabase' in u and path.endswith('/rpc/hx_line_map'): return jr(route, None)
        if '/functions/v1/hendrix-ai' in u:          # Hendrix AI reading the pre-roll COA uploaded in the Testing scene
            coa = {'lab_name': 'Green Leaf Lab', 'lab_license_number': 'TES000777', 'report_date': '2026-10-23', 'sample_metrc_tag': ns['tag'](1252), 'overall_status': 'Pass',
                   'potency': {'unit': '%', 'total_thc': 40.6, 'total_cbd': 0.1, 'thca': 44.2, 'd9_thc': 1.8, 'cbn': 0.3, 'cbg': 0.8},
                   'categories': {'pesticides': {'status': 'Pass', 'analytes': []}, 'microbials': {'status': 'Pass', 'analytes': [{'name': 'Total yeast and mold', 'result': '<100', 'limit': '10000', 'unit': 'CFU/g', 'status': 'Pass'}]},
                                  'mycotoxins': {'status': 'Pass', 'analytes': []}, 'heavy_metals': {'status': 'Pass', 'analytes': [{'name': 'Lead', 'result': '0.04', 'limit': '0.5', 'unit': 'ug/g', 'status': 'Pass'}]},
                                  'foreign_matter': {'status': 'Pass', 'analytes': []}, 'moisture': {'status': 'Pass', 'analytes': [{'name': 'Water activity', 'result': '0.51', 'limit': '0.65', 'unit': 'aw', 'status': 'Pass'}]}},
                   'terpenes': [{'name': 'Limonene', 'value': 0.58}, {'name': 'beta-Myrcene', 'value': 0.44}, {'name': 'beta-Caryophyllene', 'value': 0.31}], 'total_terpenes': 1.52}
            return jr(route, {'content': [{'type': 'text', 'text': json.dumps(coa)}]})
        if 'supabase' in u and m == 'POST' and '/rest/v1/' in path and '/rpc/' not in path and request.post_data:
            bd = json.loads(request.post_data); rows = bd if isinstance(bd, list) else [bd]; changed = False
            for x in rows:
                if tbl == 'hx_plant_batches' and not x.get('number'): x['number'] = nxt(tbl, 'PB-2026-'); x.setdefault('created_by', ME); x.setdefault('stage', 'propagation'); x.setdefault('harvest_after', None); x.setdefault('wet_weight', None); x.setdefault('dry_weight', None); x.setdefault('harvest_tag', ''); changed = True
                if tbl == 'hx_grow_events':
                    x.setdefault('recorded_by', ME); x.setdefault('voided', False); changed = True
                    if x.get('kind') == 'crop_protection' and x.get('phi_days') is not None:   # database: earliest harvest = latest application + PHI
                        import datetime as _d
                        pb = next((y for y in T['hx_plant_batches'] if y['id'] == x.get('batch_id')), None)
                        ha = (_d.date.fromisoformat(x['done_on']) + _d.timedelta(days=int(x['phi_days']))).isoformat()
                        if pb and (not pb.get('harvest_after') or ha > pb['harvest_after']): pb['harvest_after'] = ha
                if tbl == 'hx_tests': x.setdefault('performed_by', ME); changed = True
                if tbl == 'hx_label_prints': x.setdefault('printed_by', ME); x.setdefault('created_at', now()); changed = True
                if tbl == 'hx_batches': x.setdefault('performed_by', ME); changed = True
                if tbl == 'hx_grow_areas': x.setdefault('active', True); changed = True
            if changed:
                return _post(route, request, bd)
        if 'supabase' in u and m == 'POST' and tbl == 'hx_production_plans':
            x = json.loads(request.post_data); x.update({'number': 'PP-2026-%03d' % ns['PSEQ'][0], 'status': 'planned', 'created_by': ME, 'created_at': now()}); ns['PSEQ'][0] += 1
            T['hx_production_plans'].insert(0, x); return jr(route, [x], 201)
        out = h0(route, request)
        if m != 'GET':
            for a in T.get('hx_audit_log', []):
                if a.get('user_name') == 'Sam': a['user_name'] = ME
        return out
    class _Req:                                   # re-feed the mock with the stamped body
        def __init__(self, r, bd): self._r = r; self.post_data = json.dumps(bd); self.url = r.url; self.method = r.method
        def __getattr__(self, k): return getattr(self._r, k)
    def _post(route, request, bd):
        out = h0(route, _Req(request, bd))
        for a in T.get('hx_audit_log', []):
            if a.get('user_name') == 'Sam': a['user_name'] = ME
        return out
    ns['handle'] = handle
    return ns


def app(pw, ns, name, extra='', fixed=hv.FIXED_DAY, wait='text=Quality standard'):
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, fixed=fixed, session=hv.session_script(extra=extra))
    ctx.add_init_script(CAP_INIT)
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_selector(wait); pg.wait_for_timeout(800)
    r = hv.Rec(ctx, pg, name)
    return b, pg, r


def navb(pg, name): return pg.locator('.nav').get_by_role('button', name=name, exact=True).first


def go(r, pg, name, wait):
    r.click(navb(pg, name), after=0.05); pg.evaluate('window.scrollTo(0,0)')
    pg.wait_for_selector(wait); r.wait(0.3)


def mclick(r, loc, **kw):
    """Click a button inside a scrolling dialog: bring it into the dialog's view first."""
    loc.wait_for(state='visible', timeout=15000)
    loc.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'nearest'})"); r.wait(0.6)
    r.click(loc, **kw)


def closeall(r, pg):
    for _ in range(6):
        if not pg.locator('.mo').count(): return
        pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); r.wait(0.3)
