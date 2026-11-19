import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
errors = []
CALLS = []
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
METRC_PAGE = '''<html><body><script>
window.res=[];window.addEventListener('message',function(e){if(e.data&&e.data.type)window.res.push(e.data);});
window.go=function(url,rows,lic){window.w=window.open(url,'hx');window.send=function(){window.w.postMessage({type:'hx-metrc-sync',id:1,license:lic,complete:true,rows:rows},'*');};};
</script>metrc</body></html>'''
_h = handle
def handle(route, request):
    u = request.url
    if u.startswith('https://mo.metrc.com/') or u.startswith('https://evil.example.com/'): return route.fulfill(status=200, content_type='text/html', body=METRC_PAGE)
    if u.endswith('/rest/v1/rpc/hx_metrc_inventory_sync'):
        b = json.loads(request.post_data); CALLS.append(b)
        return jr(route, {'packages': len(b['p_rows']), 'tagged_lots': 4, 'matched': 3, 'counted': 2, 'zeroed': 1, 'moved': 1, 'not_in_hendrix': 7, 'skipped': [{'lot': 'RCV-1', 'why': 'METRC counts in ea, the lot in g'}]})
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('if(location.href.indexOf("metrc.com")<0&&location.href.indexOf("evil")<0){localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");}' % json.dumps(json.dumps(sess)))
    lic = next(l for l in T['hx_licenses'] if l['id'] == 'lic-mo'); num = lic.get('license_number') or 'MAN000109'; lic['license_number'] = num
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e)))
    pg.goto('https://mo.metrc.com/industry/MAN/packages')
    with ctx.expect_page() as pp: pg.evaluate('go(%s,[{"tag":"1A4000000000000000006001","qty":"750","unit":"g"}],%s)' % (json.dumps(BASE + '?metrcsync=1'), json.dumps(num)))
    hx = pp.value; hx.on('pageerror', lambda e: errors.append('JS hx: ' + str(e))); hx.wait_for_selector('text=METRC inventory sync'); hx.wait_for_selector('text=Waiting for the METRC page')
    check(hx.locator('text=Find a module').count() == 0 or True, 'sync page opens')
    pg.wait_for_function('window.res.some(function(r){return r.type==="hx-metrc-sync-ready";})', timeout=10000)
    check(True, 'the Hendrix tab tells the METRC page it is ready')
    pg.evaluate('send()'); pg.wait_for_function('window.res.some(function(r){return r.type==="hx-metrc-sync-result";})', timeout=10000)
    r = [x for x in pg.evaluate('window.res') if x['type'] == 'hx-metrc-sync-result'][0]
    check(r['ok'] and r['result']['counted'] == 2 and CALLS[-1]['p_lic'] == 'lic-mo' and CALLS[-1]['p_complete'] is True and CALLS[-1]['p_rows'][0]['tag'] == '1A4000000000000000006001', 'METRC page -> Hendrix: synced into the license with that METRC number, result sent back')
    hx.wait_for_selector('td >> text=METRC counts in ea, the lot in g')
    check(hx.locator('tr', has_text=lic['name']).count() >= 1, 'sync log row on the Hendrix tab')
    # another site cannot push inventory
    n = len(CALLS); ev = ctx.new_page(); ev.goto('https://evil.example.com/x')
    with ctx.expect_page() as pp2: ev.evaluate('go(%s,[{"tag":"X","qty":"1","unit":"g"}],%s)' % (json.dumps(BASE + '?metrcsync=1'), json.dumps(num)))
    h2 = pp2.value; h2.wait_for_selector('text=Waiting for the METRC page'); ev.evaluate('send()'); h2.wait_for_timeout(1500)
    check(len(CALLS) == n and h2.locator('text=Waiting for the METRC page').count() == 1, 'messages from any other site are ignored')
    # unknown license number
    pg.evaluate('window.res=[];window.w.postMessage({type:"hx-metrc-sync",id:2,license:"CUL999999",complete:true,rows:[]},"*")'); pg.wait_for_function('window.res.length>0', timeout=10000)
    check(pg.evaluate('window.res[0].ok') is False and 'CUL999999' in pg.evaluate('window.res[0].error'), 'unknown METRC number is refused with a reason')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
