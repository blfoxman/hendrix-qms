import re, os, datetime as dt
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
# a METRC Packages > Active export (CSV); HX_MI_FILE can point at a real export (.xlsx) instead
SRC = os.environ.get('HX_MI_FILE')
if not SRC:
    SRC = OUT + 'metrc_active.csv'
    hdr = 'Tag,Source Harvest(s),Location,Item,Category,Item Strain,Quantity,Unit Of Measure,Production Batch Number,Lab Test Status,Finished Goods,Administrative Hold,Packaged Date'
    lines = [hdr]
    for i in range(2400):
        lines.append('1A40C03000060E10000%05d,"H1, H2",Distribution,"M00002426455: Muha Meds - Distillate Vape AIO - 2g - DO-SI OG",Vape Cartridge (Final Packaging),,5,ea,PB%03d,TestPassed,False,False,11/16/2026' % (i, i % 40))
    for i in range(150):
        lines.append('1A40C03000007D10000%05d,,Biomass,M00002721009: Maypop,Biomass,,%d,g,,NotSubmitted,False,%s,11/12/2026' % (i, 1000 + i, 'True' if i == 0 else 'False'))
    lines.append('1A40C03000063390000000001,,Production Vault,M00002922946: Bodega Boyz - Shorties Diamond Infused Preroll - Mango Gelato,Concentrate,,1.5,kg,pb11.16.26,NotSubmitted,False,False,11/16/2026')
    open(SRC, 'w').write('\n'.join(lines))
SNAPS, PKGS, CALLS = [], {}, []
_h = handle
def handle(route, request):
    u = urllib.parse.urlparse(request.url); path = u.path; qs = dict(urllib.parse.parse_qsl(u.query))
    if path.endswith('/rpc/hx_metrc_save'):
        a = json.loads(request.post_data); sid = 'ms-%d' % (len(SNAPS) + 1)
        SNAPS.insert(0, {'id': sid, 'state_id': 'st-mo', 'license_id': a['p_lic'], 'source': 'csv', 'file_name': a['p_file'], 'packages': len(a['p_rows']), 'created_at': now()})
        PKGS[sid] = sorted(a['p_rows'], key=lambda r: r['tag']); return route.fulfill(status=200, content_type='application/json', body=json.dumps(sid))
    if path.endswith('/hx_metrc_snapshots'):
        return route.fulfill(status=200, content_type='application/json', body=json.dumps([s for s in SNAPS if s['license_id'] == qs.get('license_id', '').replace('eq.', '')]))
    if path.endswith('/hx_metrc_packages'):
        CALLS.append(qs); sid = qs['snapshot_id'].replace('eq.', ''); off = int(qs.get('offset', 0)); lim = min(int(qs.get('limit', 1000)), 1000)   # Supabase returns at most 1000 rows
        rows = [dict(r, quantity=float(r['quantity']) if r['quantity'] not in ('', None) else None, packaged_date=r['packaged_date'] or None) for r in PKGS.get(sid, [])[off:off + lim]]
        return route.fulfill(status=200, content_type='application/json', body=json.dumps(rows))
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')
    side = pg.locator('.side, nav, aside').first
    pg.get_by_role('button', name='Cannabis Inventory', exact=True).click(); pg.wait_for_selector('h1 >> text=Cannabis Inventory')
    pg.wait_for_selector('.empty >> text=No METRC inventory yet', timeout=15000)
    check(pg.locator('.empty', has_text='No METRC inventory yet').count() == 1, 'empty page explains how to get the METRC export')
    pg.set_input_files('input[aria-label="METRC export file"]', SRC)
    pg.wait_for_selector('.card.gold >> text=Packages', timeout=120000); pg.wait_for_timeout(500)
    n = SNAPS[0]['packages']
    kp = lambda l: pg.locator('.card.gold', has=pg.locator('.k', has_text=re.compile('^' + l + '$'))).locator('.v').inner_text()
    check(kp('Packages') == '{:,}'.format(n) and n == len(PKGS[SNAPS[0]['id']]), 'every package of the export saved and shown (%d)' % n)
    check(len(CALLS) == (n + 999) // 1000, 'packages read in pages of 1000 (Supabase limit)')
    check('as of' in pg.locator('.sub').first.inner_text() and os.path.basename(SRC) in pg.locator('.sub').first.inner_text(), 'shows which upload it is from')
    if not os.environ.get('HX_MI_FILE'):
        check(kp('Units') == '12,000' and kp('Weight') == '162.7 kg', 'units in each and weight in g + kg added up')
        check(kp('On hold') == '1' and kp('Test passed') == '2,400', 'lab status and holds counted')
        row = pg.locator('tr.mirow', has_text='DO-SI OG')
        check(row.count() == 1 and '2400' in row.inner_text() and '12,000 ea' in row.inner_text() and 'M00002426455' in row.inner_text(), 'grouped by item: packages, on hand, item #')
        row.click(); pg.wait_for_timeout(200)
        check(pg.locator('td code', has_text='1A40C03000060E1000000007').count() == 1, 'click an item to list its packages')
        row.click()
        pg.locator('button', has_text=re.compile(r'^Biomass \(150\)$')).click(); pg.wait_for_timeout(200)
        check(kp('Packages') == '150' and pg.locator('tr.mirow').count() == 1, 'category filter')
        pg.locator('button', has_text=re.compile(r'^All \(')).click()
        pg.fill('input[aria-label="Search inventory"]', 'pb11.16.26'); pg.wait_for_timeout(200)
        check(kp('Packages') == '1' and '1.5 kg' in pg.locator('tr.mirow').inner_text(), 'search by production batch; kg shown')
        pg.fill('input[aria-label="Search inventory"]', '')
        pg.select_option('select[aria-label="Lab status"]', 'NotSubmitted'); pg.wait_for_timeout(200)
        check(kp('Packages') == '151', 'lab status filter')
        pg.select_option('select[aria-label="Lab status"]', '')
        pg.locator('.tabs button', has_text='Packages').click(); pg.wait_for_timeout(300)
        check(pg.locator('tbody tr').count() == 300 and pg.locator('button', has_text='Show more').count() == 1, 'package list shows 300 at a time')
        check(pg.locator('tr', has_text='1A40C03000007D1000000000').locator('.badge', has_text='On hold').count() == 1, 'package on hold flagged')
        pg.locator('.tabs button', has_text='By item').click()
    fx = pg.evaluate('''async()=>{await window.hxXlsx.load();const ws={'!ref':'A1:A2',A1:{t:'s',v:'Tag'},B1:{t:'s',v:'Item'},A2:{t:'s',v:'1A4000000000000000000001'},B2:{t:'s',v:'Gummies'}};return window.hxXlsx.fix(ws)['!ref'];}''')
    check(fx == 'A1:B2', 'Excel sheet that declares a smaller size than its data (METRC export) is read in full')
    with pg.expect_download() as d: pg.get_by_role('button', name='Export CSV').click()
    txt = open(d.value.path()).read(); check(txt.count('\n') == n and txt.startswith('Tag,Item #,Item,Category'), 'Export CSV with every package')
    pg.screenshot(path=OUT + 'cannabis_inventory.png', full_page=False)
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
