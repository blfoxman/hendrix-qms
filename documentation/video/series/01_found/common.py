# Shared setup for video 01 (found): kit import, richer seed data, helpers.
import os, sys, re, json, urllib.parse, datetime as _dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(HERE + '/../../kit'))
import hxvideo as hv
hv.set_project(HERE)
SNAP = os.path.abspath(HERE + '/../../index_snapshot2.html')
SCR = hv.SCR
field = hv.field

MERGE_Q = ['hx_deviations', 'hx_capas', 'hx_complaints', 'hx_audits', 'hx_audit_findings', 'hx_sops', 'hx_sop_acks', 'hx_sop_versions']
MERGE_S = ['hx_suppliers', 'hx_supplier_reviews', 'hx_lots', 'hx_lot_uses', 'hx_holds', 'hx_shipments', 'hx_recalls', 'hx_recall_contacts']


def load_found(rich=True):
    """found seed + QMS and supply data so the Dashboard cards look like a working license."""
    ns = hv.load_setup('found', snapshot=SNAP); T = ns['T']
    for p in T['hx_profiles']:
        if p['name'] == 'Sam': p['name'] = 'Sam Salari'
    if not rich: return ns
    q = hv.load_setup('qual', snapshot=SNAP); s = hv.load_setup('supply', snapshot=SNAP)
    for t in MERGE_Q: T[t] = q['T'][t]
    for t in MERGE_S: T[t] = s['T'][t]
    for t in ('hx_batches', 'hx_tests'):
        T[t] = T[t] + [x for x in s['T'][t] if x['id'] not in {y['id'] for y in T[t]}]
    for x in T['hx_holds']:
        if x.get('placed_by') == 'Jordan Ortiz': x['placed_by'] = 'Derek Hall'
    _h = ns['handle']
    def handle(route, request):
        u = request.url
        if '/rest/v1/rpc/' in u:
            fn = urllib.parse.urlparse(u).path.split('/')[-1]
            if fn in ('hx_qms_people', 'hx_sop_roster', 'hx_training_roster', 'hx_training_sop_acks'): return q['handle'](route, request)
            if fn == 'hx_trace_data': return s['handle'](route, request)
        return _h(route, request)
    ns['handle'] = handle; ns['_q'] = q; ns['_s'] = s
    return ns


def open_app(b, ns, wait='.nav', **kw):
    kw.setdefault('session', hv.session_script())
    ctx = hv.new_context(b, ns, **kw)
    pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept())
    pg.goto(ns['BASE']); pg.wait_for_selector(wait); pg.wait_for_timeout(700)
    return ctx, pg


def nav(pg, name):
    return pg.locator('.nav').get_by_role('button', name=name, exact=True)


def add_roles(b, ns):
    """Add the Black Fox starter roles through the app (off camera) and give people roles."""
    ctx, pg = open_app(b, ns)
    nav(pg, 'Roles').click(); pg.wait_for_selector('text=No roles yet')
    pg.get_by_role('button', name='Add Black Fox roles').click(); pg.wait_for_selector('.card >> text=Production Lead')
    ctx.close()
    T = ns['T']; R = {r['name']: r for r in T['hx_roles']}
    R['Production Lead']['requirements'] = 'High school diploma; 1 year cannabis production experience; cGMP and state compliance training; forklift certification'
    R['Compliance Officer']['requirements'] = "Bachelor's degree in a science field; 2 years QA or compliance; CSQ Program Overview course; HACCP certified"
    R['General Manager']['requirements'] = '5 years manufacturing management; cGMP training; CSQ Program Overview course'
    M = {p['name']: p for p in T['hx_profiles']}
    M['Maria Lopez']['role_ids'] = [R['Production Lead']['id']]
    M['Derek Hall']['role_ids'] = [R['Security Manager']['id'], R['Compliance Officer']['id']]
    return R


def prep_standards(b, ns, conformance=True):
    """Add the CSQ standard, adopt it at Level 2 and fill realistic conformance (off camera)."""
    T = ns['T']
    ctx, pg = open_app(b, ns)
    nav(pg, 'Standards (CSQ)').click(); pg.wait_for_selector('text=No standard added yet')
    pg.get_by_role('button', name=re.compile('^Add CSQ Standard')).click(); pg.wait_for_selector('.msg >> text=Added')
    pg.get_by_role('button', name='Adopt for this license').click(); md = pg.locator('.md')
    field(md, 'Target level').select_option('2'); field(md, 'Status').select_option('Audit scheduled'); field(md, 'Certification body').fill('Kiwa ASI')
    field(md, 'Audit date').fill('2026-12-08'); field(md, 'Notes').fill('First certification audit. Offsite document review the week before.')
    md.get_by_role('button', name='Adopt standard').click(); pg.wait_for_selector('text=0% complete')
    ctx.close()
    if not conformance: return
    std = T['hx_standards'][0]
    insc = [c for c in T['hx_standard_clauses'] if c['level'] <= 2 and (not c['module'].startswith('3') or c['module'] in ('3B', '3C'))]
    skip = {'1.4', '2A.3', '2A.5.1'}
    for i, c in enumerate([x for x in insc if x['clause'] not in skip]):
        if i % 10 in (0, 1, 2, 3, 4, 5): st, ow, du, ev = 'Conforming', 'Compliance Officer', None, 'SOP and records in Hendrix; reviewed during the September internal audit.'
        elif i % 10 in (6, 7): st, ow, du, ev = 'Partial', 'Production Manager', '2026-11-20', 'SOP drafted; training still to be recorded for second shift.'
        elif i % 10 == 8: continue
        else: st, ow, du, ev = ('Not conforming', 'General Manager', '2026-10-15', 'Gap found in the September internal audit; CAPA open.') if i % 20 == 9 else ('Partial', 'QA Lead', '2026-11-30', 'In progress.')
        T['hx_conformance'].append({'id': 'cf%d' % i, 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': std['id'], 'clause_id': c['id'], 'status': st, 'owner': ow, 'due_date': du,
                                    'doc_ref': 'SOP-QA-%03d' % (i + 1), 'evidence': ev, 'files': [], 'reviewed_at': '2026-10-%02dT15:00:00.000Z' % (2 + i % 20)})


def audit_rows(ns):
    T = ns['T']
    def ago(d, h=0):
        return (hv.FIXED_DAY - _dt.timedelta(days=d, hours=h)).astimezone(_dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
    T['hx_audit_log'] += [
        {'id': 900, 'at': ago(2, 5), 'table_name': 'hx_batches', 'row_id': 'b0', 'action': 'UPDATE', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Sam Salari', 'reason': 'Scale printout showed 812 g; typo on first entry',
         'changed': ['data'], 'old_data': {'batch_number': 'CART-2026-118', 'batch_type': 'cartridges', 'data': {'input_weight': '800'}}, 'new_data': {'batch_number': 'CART-2026-118', 'batch_type': 'cartridges', 'data': {'input_weight': '812'}}},
        {'id': 901, 'at': ago(3, 2), 'table_name': 'hx_facility_log', 'row_id': 'fl7', 'action': 'VOID', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Derek Hall', 'reason': 'Entered on the wrong license',
         'changed': ['void_reason', 'voided'], 'old_data': {'log_type': 'waste', 'item': 'Trim and stems'}, 'new_data': {'log_type': 'waste', 'item': 'Trim and stems', 'voided': True}},
        {'id': 902, 'at': ago(4, 1), 'table_name': 'hx_tests', 'row_id': 'te2', 'action': 'UPDATE', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Derek Hall', 'reason': 'Lab issued an amended COA',
         'changed': ['status'], 'old_data': {'batch_number': 'PR-2026-071', 'status': 'Passed'}, 'new_data': {'batch_number': 'PR-2026-071', 'status': 'Failed'}},
        {'id': 903, 'at': ago(1, 3), 'table_name': 'hx_facility_log', 'row_id': 'fl1', 'action': 'UPDATE', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Maria Lopez', 'reason': 'Wrong area ticked; corrected after supervisor check',
         'changed': ['item'], 'old_data': {'log_type': 'sanitation', 'item': 'Line 1'}, 'new_data': {'log_type': 'sanitation', 'item': 'Line 2'}},
        {'id': 904, 'at': ago(5, 4), 'table_name': 'hx_batches', 'row_id': 'b1', 'action': 'UPDATE', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'user_name': 'Sam Salari', 'reason': 'Flavor recorded on the wrong line of the batch sheet',
         'changed': ['flavor'], 'old_data': {'batch_number': 'CART-2026-112', 'batch_type': 'cartridges', 'flavor': 'Blue Dream'}, 'new_data': {'batch_number': 'CART-2026-112', 'batch_type': 'cartridges', 'flavor': 'Sour Diesel'}}]
    for a in T['hx_audit_log']:
        if a['user_name'] == 'Sam': a['user_name'] = 'Sam Salari'
    T['hx_audit_log'] = [a for a in T['hx_audit_log'] if a['table_name'] not in ('hx_conformance', 'hx_license_standards', 'hx_license_settings', 'hx_standards', 'hx_standard_clauses', 'hx_rule_sources')]
    T['hx_audit_log'].sort(key=lambda a: a['at'])
    for i, a in enumerate(T['hx_audit_log']): a['id'] = i + 1
