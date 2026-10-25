import os, re, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
# Step 41: METRC Check - upload the METRC export, compare with Hendrix (real database functions)
errors = []
PGDB = os.environ.get('HX_PGDB', 'hxtest')
HERE_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db')
subprocess.run(['psql', '-X', '-q', '-d', PGDB, '-f', os.path.join(HERE_DB, 't41.sql')], capture_output=True, text=True)   # Hendrix records with METRC tags
ST = {'api': 'nokeys', 'saves': []}
def db_json(sql_fn, args):
    vs = []; names = []
    for i, (k, v) in enumerate(args.items()):
        vs += ['-v', 'a%d=%s' % (i, json.dumps(v) if isinstance(v, (dict, list)) else str(v))]; names.append("%s => :'a%d'" % (k, i))
    out = subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB] + vs, input="set test.uid='%s';\nselect to_jsonb(%s(%s))::text;\n" % (ADMIN, sql_fn, ', '.join(names)), capture_output=True, text=True)
    if 'ERROR' in out.stderr: return None, out.stderr.split('ERROR:')[-1].strip().split('\n')[0]
    return json.loads(out.stdout.strip().split('\n')[-1]), None
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    for fn in ('hx_metrc_save', 'hx_metrc_reconcile'):
        if path.endswith('/rpc/' + fn):
            a = json.loads(request.post_data)
            if fn == 'hx_metrc_save': ST['saves'].append(a)
            r, e = db_json(fn, a)
            return jr(route, {'message': e}, 400) if e else jr(route, r)
    if path.endswith('/rest/v1/hx_metrc_snapshots'):
        out = subprocess.run(['psql', '-X', '-q', '-At', '-d', PGDB, '-c', "select coalesce(jsonb_agg(s order by s.created_at desc),'[]')::text from hx_metrc_snapshots s where license_id='lic-mo'"], capture_output=True, text=True)
        return jr(route, json.loads(out.stdout.strip()))
    if '/functions/v1/hendrix-metrc' in u:
        if ST['api'] == 'nokeys': return jr(route, {'error': {'message': 'METRC keys are not set for license MAN000109: add METRC_VENDOR_KEY and this license in METRC_USER_KEYS (Supabase > Edge Functions > Secrets). Until then, upload the METRC export (CSV).'}}, 400)
        return route.fulfill(status=404, body='not found')
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
# a METRC export the way METRC writes it: title rows, "Quantity" with the unit, M/D/YYYY dates
CSV = ('Packages - Active\n"Exported 10/25/2026"\n'
       'Tag,Src. H\'s,Item,Category,Item Strain,Quantity,P.B. No.,Lab Testing,A.H.,Date,Location\n'
       '1A40 TEST1,,Cart 1g,Vape Cartridge,,10 Each,B-1,SubmittedForTesting,,10/20/2026,Vault\n'
       '1A40-TEST2,,Cart 1g,Vape Cartridge,,10 Each,B-2,TestFailed,,10/20/2026,Vault\n'
       '1A40-HOLD,,Gummies,Edible,,40 Each,,TestPassed,,10/19/2026,Vault\n'
       '1A40-MHOLD,,Flower,Flower,OG,"1,200 Grams",,TestPassed,Yes,10/18/2026,Vault\n'
       '1A40-LOT1,,Distillate,Concentrate,,700 Grams,,TestPassed,,10/10/2026,Lab\n'
       '1A40-SHIP,,Pre-roll,Pre-Roll,,5 Each,,TestPassed,,10/12/2026,Dock\n'
       '1A40-NEW,,Rosin,Concentrate,,3 Grams,B-77,NotSubmitted,,10/22/2026,Vault\n')
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN, 'email': 's@x'}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('.nav')
    pg.locator('.nav button', has_text='METRC Check').click(); pg.wait_for_selector('h1 >> text=METRC Check')
    pg.locator('input[aria-label="METRC export file"]').set_input_files({'name': 'Packages.csv', 'mimeType': 'text/csv', 'buffer': CSV.encode()})
    pg.wait_for_selector('.mcrow')
    rows = ST['saves'][-1]['p_rows']; r1 = next(r for r in rows if r['tag'] == '1A40-MHOLD')
    check(len(rows) == 7 and r1['quantity'] == '1200' and r1['unit'] == 'Grams' and r1['on_hold'] is True and r1['packaged_date'] == '2026-10-18' and r1['lab_state'] == 'TestPassed' and r1['batch_no'] == '', 'METRC export read: title rows skipped, quantity and unit split, dates, on hold')
    txt = pg.locator('.card', has=pg.locator('.mcrow')).inner_text()
    for t, m in [('Passed in Hendrix, METRC lab status is SubmittedForTesting', 'lab status difference'), ('On hold in METRC, no open hold in Hendrix', 'hold in METRC only'),
                 ('Open hold HOLD-T41-1 in Hendrix, not on hold in METRC', 'hold in Hendrix only'), ('still active in METRC', 'shipped but still active in METRC'),
                 ('Lot LOT-T41-2 has 50 g left in Hendrix, not active in METRC', 'lot missing from METRC'), ('Quantity: Hendrix 800 g, METRC 700 Grams', 'quantity difference')]:
        check(t in txt, 'shown: ' + m)
    check(pg.locator('.mcrow').first.locator('.badge', has_text='Fix now').count() == 1, 'most serious first')
    check(pg.locator('.card', has=pg.locator('.k', has_text='Packages in METRC')).inner_text().split('\n')[-1] == '7', 'package count')
    pg.locator('.card .k', has_text=re.compile('^Not in Hendrix$')).click()
    check(pg.locator('.mcrow').count() >= 1 and pg.locator('.mcrow', has_text='1A40-NEW').count() == 1, 'information list: packages Hendrix does not know')
    pg.locator('.card .k', has_text=re.compile('^Packages in METRC$')).click()
    pg.screenshot(path=OUT + 'metrc.png', full_page=True)
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print report').click()
    w = pop.value; w.wait_for_load_state(); html = w.content()
    check('METRC check' in html and '1A40-LOT2' in html and 'Reviewed by' in html, 'printable report with sign-off'); w.close()
    pg.locator('.mcrow', has_text='Open hold HOLD-T41-1').get_by_role('button', name='Open').click(); pg.wait_for_selector('h1 >> text=Hold')
    check(True, 'Open goes to the module (Hold and Release)')
    # read from METRC without keys: clear message
    pg.locator('.nav button', has_text='METRC Check').click(); pg.wait_for_selector('.mcrow')
    pg.get_by_role('button', name='Read from METRC now').click(); pg.wait_for_selector('text=METRC keys are not set for license MAN000109')
    check(True, 'METRC keys missing: the reason is shown (CSV still works)')
    ST['api'] = 'none'; pg.get_by_role('button', name='Read from METRC now').click(); pg.wait_for_selector('text=deploy hendrix-metrc.ts')
    check(True, 'METRC function not deployed: clear message')
    # a file that is not a METRC export
    pg.locator('input[aria-label="METRC export file"]').set_input_files({'name': 'other.csv', 'mimeType': 'text/csv', 'buffer': b'Name,Price\nA,1\n'})
    pg.wait_for_selector('text=No tag column found')
    check(True, 'wrong file: explained')
    # access: View can see checks, cannot upload
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'metrc': 'read'}
    pg.reload(); pg.wait_for_selector('.nav'); pg.locator('.nav button', has_text='METRC Check').click(); pg.wait_for_selector('.mcrow')
    check(pg.locator('input[aria-label="METRC export file"]').count() == 0 and pg.get_by_role('button', name='Read from METRC now').count() == 0, 'View access: sees the checks, cannot upload')
    T['hx_profiles'][0]['perms'] = {'qms': 'read'}
    pg.reload(); pg.wait_for_selector('.nav')
    check(pg.locator('.nav button', has_text='METRC Check').count() == 0, 'no access: not in the menu')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
