import re, datetime as dt
exec(open('/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/mock_c.py').read())
SHOTS = '/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/manual/shots/'
errors = []
NOWU = dt.datetime.now(dt.timezone.utc)
def iso(d): return d.strftime('%Y-%m-%dT%H:%M:%S.000Z')
def ago(minutes): return iso(NOWU - dt.timedelta(minutes=minutes))
MO = {'state_id': 'st-mo', 'license_id': 'lic-mo'}
T['hx_profiles'][0]['name'] = 'Sam Salari'
ALLCK = {k: True for k in ['docs', 'intact', 'clean', 'sealed', 'labeled', 'condition', 'vehicle']}

# ---------------- suppliers ----------------
def sup(i, name, cat, status, risk, prod, specs, contact, creds=None, **kw):
    r = {'id': i, **MO, 'license_ids': ['lic-mo'], 'name': name, 'category': cat, 'status': status, 'risk': risk, 'products_supplied': prod, 'specs': specs,
         'contact_name': contact[0], 'contact_email': contact[1], 'contact_phone': contact[2], 'address': '', 'credentials': creds or [], 'certificates': [],
         'coa_expiry': None, 'last_audit': None, 'approval_basis': '', 'approved_by': '', 'approved_at': None, 'last_review': None, 'next_review': None,
         'emergency_verification': '', 'ethical_sourcing': False, 'status_reason': '', 'notes': '', 'ever_approved': status not in ('pending', 'emergency'), 'created_at': '2026-01-10T10:00:00Z'}
    r.update(kw); return r
T['hx_suppliers'] += [
    sup('s-fut', 'Futurola USA', 'Cones/Pre-roll Supplies', 'approved', 'low', '98mm and 109mm pre-roll cones', 'Food-grade unbleached paper; COA with every lot', ('Ana Torres', 'ana@futurola-usa.example', '(555) 201-4400'),
        [{'kind': 'Food-grade / GMP certificate', 'number': 'FG-22817', 'expires': '2027-03-31', 'file': {'path': 'suppliers/lic-mo/fg.pdf', 'name': 'futurola-food-grade.pdf'}}],
        approval_basis='Supplier questionnaire, food-grade certificate and COA reviewed; trial lot passed incoming inspection', approved_by='Sam Salari', approved_at='2026-02-10T15:00:00Z',
        last_review='2026-02-10', next_review='2027-02-10', coa_expiry='2027-03-31', ethical_sourcing=True),
    sup('s-nor', 'Northline Hardware Co.', 'Packaging', 'approved', 'medium', '1g ceramic cartridges, 510 batteries', 'Heavy-metal leach test per lot; no lead solder', ('Kevin Marsh', 'orders@northline.example', '(555) 330-1180'),
        [{'kind': 'Spec sheet / COA', 'number': 'NL-1G-CER', 'expires': '2027-01-15'}], approval_basis='Spec sheet and heavy-metal leach COA reviewed; supplier audit questionnaire', approved_by='Sam Salari', approved_at='2026-03-02T15:00:00Z',
        last_review='2026-03-02', next_review='2027-03-02'),
    sup('s-gct', 'Gold Coast Terpenes', 'Terpenes', 'conditional', 'high', 'Strain-specific terpene blends', 'Inhalation-grade, no diluents, COA with every lot', ('Rina Patel', 'rina@goldcoastterps.example', '(555) 712-0090'),
        [{'kind': 'Inhalation-grade statement', 'number': 'GCT-IG-2026', 'expires': '2027-06-30'}], approval_basis='Inhalation-grade statement and COAs reviewed', approved_by='Sam Salari', approved_at='2026-04-14T15:00:00Z',
        last_review='2026-08-20', next_review='2027-02-20'),
    sup('s-mdp', 'Midwest Distillate Partners', 'Distillate/Extract', 'approved', 'high', 'THC distillate (bulk)', 'Full-panel COA from ISO 17025 lab; METRC transfer manifest', ('Luis Herrera', 'luis@mwdistillate.example', '(555) 404-7720'),
        [{'kind': 'State license', 'number': 'MAN000233', 'expires': '2027-05-01'}], approval_basis='State license verified; full-panel COAs on the last three lots', approved_by='Sam Salari', approved_at='2026-05-06T15:00:00Z',
        last_review='2026-05-06', next_review='2026-11-06'),
    sup('s-lab', 'Show-Me Analytical Labs', 'Testing Lab', 'approved', 'high', 'Compliance testing: potency, pesticides, metals, solvents', 'ISO/IEC 17025 scope covers cannabis potency and contaminants', ('QA Desk', 'qa@showmelabs.example', '(555) 600-2525'),
        [{'kind': 'ISO/IEC 17025 accreditation', 'number': 'L-2231', 'expires': '2026-12-05', 'file': {'path': 'suppliers/lic-mo/iso.pdf', 'name': 'iso17025-certificate.pdf'}},
         {'kind': 'State license', 'number': 'TES000777', 'expires': '2027-08-01'}],
        approval_basis='ISO/IEC 17025 certificate and scope reviewed; state testing license verified', approved_by='Sam Salari', approved_at='2026-01-20T15:00:00Z', last_review='2026-07-15', next_review='2027-01-15'),
    sup('s-ops', 'Ozark Pest Solutions', 'Pest Control', 'approved', 'medium', 'Monthly integrated pest management service', 'Licensed applicator; only approved products; written report per visit', ('Dale Kim', 'service@ozarkpest.example', '(555) 818-3300'),
        [{'kind': 'Pest control applicator license', 'number': 'PCA-55102', 'expires': '2027-02-28'}], approval_basis='Applicator license and product list reviewed', approved_by='Sam Salari', approved_at='2025-09-12T15:00:00Z',
        last_review='2025-09-30', next_review='2026-09-30'),
    sup('s-rlp', 'Rapid Label & Print', 'Labels', 'emergency', 'medium', 'Gummy jar labels (rush order)', 'Matches approved label artwork; adhesive rated for refrigeration', ('Front desk', 'rush@rapidlabel.example', '(555) 250-6060'),
        emergency_verification='Every roll checked against approved artwork and spec by QA before release'),
    sup('s-ppg', 'Prairie Packaging Group', 'Packaging', 'pending', 'low', 'Child-resistant mylar bags', 'ASTM D3475 child-resistant certificate; opaque', ('Mia Olsen', 'mia@prairiepack.example', '(555) 909-1212'),
        [{'kind': 'Organic / other certification', 'number': 'ASTM-D3475-8841', 'expires': '2028-01-31'}]),
]
T['hx_supplier_reviews'] += [
    {'id': 'rv1', **MO, 'supplier_id': 's-gct', 'review_date': '2026-08-20', 'reviewer': 'Sam Salari', 'rating': 'Needs improvement', 'result': 'Approve with conditions', 'notes': 'Two COAs arrived after the product; must send COA before shipping', 'files': []},
    {'id': 'rv2', **MO, 'supplier_id': 's-fut', 'review_date': '2026-02-10', 'reviewer': 'Sam Salari', 'rating': 'Satisfactory', 'result': 'Keep approved', 'notes': 'On-time deliveries, every lot passed inspection', 'files': []},
    {'id': 'rv3', **MO, 'supplier_id': 's-lab', 'review_date': '2026-07-15', 'reviewer': 'Sam Salari', 'rating': 'Satisfactory', 'result': 'Keep approved', 'notes': 'Turnaround under 5 days; no reporting errors', 'files': []},
]

# ---------------- batches + tests ----------------
def bat(i, num, typ, sku, fl, made): return {'id': i, **MO, 'batch_type': typ, 'batch_number': num, 'sku': sku, 'flavor': fl, 'status': '', 'voided': False, 'created_at': made + 'T14:00:00Z', 'data': {}}
T['hx_batches'] += [bat('b-ct2', 'CT-2026-1008', 'cart', 'Cart 1g', 'Strawberry Cough', '2026-10-08'), bat('b-gm', 'GM-2026-1003', 'gummy', 'Gummies 10pk', 'Watermelon', '2026-10-03'),
                    bat('b-ct1', 'CT-2026-0930', 'cart', 'Cart 1g', 'Lemon Haze', '2026-09-30'), bat('b-pr', 'PR-2026-0915', 'preroll', 'Pre-roll 1g', 'Blue Dream', '2026-09-15')]
def tst(i, bid, tag, status, at): return {'id': i, **MO, 'batch_id': bid, 'tag': tag, 'sample_tag': '', 'status': status, 'voided': False, 'created_at': at + 'T10:00:00Z', 'lab_name': 'Show-Me Analytical Labs'}
T['hx_tests'] += [tst('t1', 'b-pr', '1A4000000000000000021001', 'Passed', '2026-09-19'), tst('t2', 'b-ct1', '1A4000000000000000021044', 'Passed', '2026-10-03'),
                  tst('t3', 'b-gm', '1A4000000000000000021090', 'Submitted', '2026-10-06'), tst('t4', 'b-ct2', '1A4000000000000000021120', 'Failed', '2026-10-13')]

# ---------------- lots ----------------
def lot(i, num, rec, sid, item, cat, slot, qty, unit, used, status, coa=True, checks=None, **kw):
    s = next(x for x in T['hx_suppliers'] if x['id'] == sid)
    r = {'id': i, **MO, 'number': num, 'received_on': rec, 'supplier_id': sid, 'supplier_name': s['name'], 'supplier_status': s['status'], 'item': item, 'category': cat, 'supplier_lot': slot,
         'metrc_tag': '', 'quantity': qty, 'unit': unit, 'qty_used': used, 'expiry_date': None, 'location': '', 'po_number': '', 'coa_ok': coa, 'checks': checks or dict(ALLCK),
         'checks_ok': (checks or ALLCK) == ALLCK, 'inspection_notes': '', 'files': [{'path': 'receiving/lic-mo/coa-%s.pdf' % i, 'name': 'COA %s.pdf' % slot}] if coa else [],
         'status': status, 'decision_notes': '', 'decided_by': 'Sam Salari' if status != 'quarantine' else '', 'decided_at': rec + 'T18:00:00Z' if status != 'quarantine' else None,
         'received_by': 'Jordan Ortiz', 'created_at': rec + 'T15:00:00Z'}
    r.update(kw); return r
T['hx_lots'] += [
    lot('l18', 'RCV-2026-018', '2026-10-22', 's-rlp', 'Gummy jar labels', 'Labels', 'RL-10-2231', 4, 'roll', 0, 'quarantine', coa=False,
        checks={**ALLCK, 'labeled': False}, inspection_notes='One roll has no lot label on the core', location='Quarantine shelf Q1'),
    lot('l17', 'RCV-2026-017', '2026-10-20', 's-mdp', 'THC distillate', 'Distillate / extract', 'MDP-DST-0917', 1000, 'g', 0, 'quarantine', metrc_tag='1A40A0300001234000000456', expiry_date='2027-10-01',
        po_number='PO-4471', location='Quarantine fridge Q2', inspection_notes='Seal intact, 2 x 500 g jars, received at 4 C'),
    lot('l16', 'RCV-2026-016', '2026-10-02', 's-gct', 'Limonene terpene blend', 'Terpenes', 'GCT-LIM-0926', 2, 'L', 0.4, 'accepted', expiry_date='2027-04-01', location='Terpene cabinet T1', decision_notes='COA reviewed before use (supplier condition)'),
    lot('l15', 'RCV-2026-015', '2026-09-29', 's-nor', '1g ceramic cartridges', 'Hardware (cartridges, batteries)', 'NL-0921-A', 3000, 'each', 900, 'accepted', location='Rack B2'),
    lot('l14', 'RCV-2026-014', '2026-09-22', 's-fut', '98mm pre-roll cones', 'Cones / pre-roll supplies', 'FU-7781', 5000, 'each', 1200, 'accepted', expiry_date='2028-01-01', location='Rack A1'),
    lot('l13', 'RCV-2026-013', '2026-09-15', 's-nor', '510 batteries', 'Hardware (cartridges, batteries)', 'NL-0908-B', 400, 'each', 0, 'on_hold', checks={**ALLCK, 'intact': False},
        decision_notes='Crushed cartons, 37 batteries cracked', location='Quarantine cage'),
    lot('l11', 'RCV-2026-011', '2026-09-08', 's-mdp', 'THC distillate', 'Distillate / extract', 'MDP-DST-0901', 1000, 'g', 760, 'accepted', metrc_tag='1A40A0300001234000000301', expiry_date='2027-09-01', location='Vault fridge V1'),
    lot('l09', 'RCV-2026-009', '2026-08-28', 's-fut', '98mm pre-roll cones', 'Cones / pre-roll supplies', 'FU-7702', 5000, 'each', 4700, 'accepted', expiry_date='2027-12-01', location='Rack A1'),
]
for l in T['hx_lots']:
    if l['id'] == 'l13': l['status'] = 'on_hold'; l['decided_at'] = '2026-09-15T18:00:00Z'
def use(i, lid, bid, bn, q, d): return {'id': i, **MO, 'lot_id': lid, 'batch_id': bid, 'batch_number': bn, 'quantity': q, 'used_on': d, 'notes': '', 'used_by': 'Jordan Ortiz', 'voided': False, 'created_at': d + 'T16:00:00Z'}
T['hx_lot_uses'] += [use('u6', 'l16', 'b-ct2', 'CT-2026-1008', 0.2, '2026-10-08'), use('u5', 'l15', 'b-ct2', 'CT-2026-1008', 450, '2026-10-08'), use('u4', 'l11', 'b-ct2', 'CT-2026-1008', 380, '2026-10-08'),
                     use('u3', 'l16', 'b-ct1', 'CT-2026-0930', 0.2, '2026-09-30'), use('u2', 'l15', 'b-ct1', 'CT-2026-0930', 450, '2026-09-30'), use('u1', 'l11', 'b-ct1', 'CT-2026-0930', 380, '2026-09-30'),
                     use('u0', 'l14', 'b-pr', 'PR-2026-0915', 1200, '2026-09-15'), use('u00', 'l09', 'b-pr', 'PR-2026-0915', 4700, '2026-09-15')]

# ---------------- holds ----------------
def hold(i, num, kind, item, src, reason, created, status='open', **kw):
    r = {'id': i, **MO, 'number': num, 'kind': kind, 'lot_id': None, 'batch_id': None, 'tag': '', 'item': item, 'quantity': '', 'source': src, 'reason': reason, 'deviation_id': None, 'shipment_id': None,
         'location': 'Quarantine area', 'prev_status': '', 'status': status, 'decision_notes': '', 'decided_by': '', 'decided_at': None, 'placed_by': 'Jordan Ortiz', 'created_at': created}
    r.update(kw); return r
T['hx_holds'] += [
    hold('h7', 'HOLD-2026-007', 'return', 'Returned by Riverbend Cannabis Co. (SHP-2026-031)', 'Customer return', 'Customer reports 12 cartridges leaking at the mouthpiece', '2026-10-19T15:20:00Z',
         batch_id='b-ct1', tag='1A4000000000000000021044', quantity='12 units', location='Returns shelf R1', shipment_id='sh31'),
    hold('h6', 'HOLD-2026-006', 'batch', 'Cart 1g batch CT-2026-1008', 'Failed test', 'Failed residual solvents test (Show-Me Analytical COA 26-4471)', '2026-10-13T17:05:00Z', batch_id='b-ct2', quantity='2,400 units', location='Vault cage V3'),
    hold('h5', 'HOLD-2026-005', 'lot', '510 batteries (RCV-2026-013)', 'Receiving inspection', 'Rejected at receiving: Crushed cartons, 37 batteries cracked', '2026-09-15T18:00:00Z', lot_id='l13', quantity='400 each', prev_status='rejected', location='Quarantine cage', placed_by='Sam Salari'),
    hold('h4', 'HOLD-2026-004', 'batch', 'Pre-roll 1g batch PR-2026-0915', 'Complaint', 'Harsh smoke complaint from Greenway Dispensary', '2026-09-24T14:00:00Z', batch_id='b-pr', status='released',
         decision_notes='Retained samples checked; moisture 11%, in spec. Complaint not confirmed', decided_by='Sam Salari', decided_at='2026-09-26T16:00:00Z'),
]

# ---------------- shipments ----------------
SHIPCK = {k: True for k in ['vehicle_clean', 'secure', 'temp', 'sealed', 'match', 'labels', 'released', 'separate']}
def ship(i, num, d, cust, lic, dest, man, items, status, **kw):
    r = {'id': i, **MO, 'number': num, 'ship_date': d, 'customer': cust, 'customer_license': lic, 'destination': dest, 'manifest_number': man, 'transporter': 'Black Fox fleet', 'driver': 'Chris Lane', 'vehicle': 'Van MO-4KT-221',
         'items': items, 'checks': dict(SHIPCK), 'checks_ok': True, 'notes': '', 'files': [], 'status': status, 'delivered_on': None, 'cancel_reason': '', 'shipped_by': 'Jordan Ortiz', 'created_at': d + 'T13:00:00Z'}
    r.update(kw); return r
def it(bid, bn, prod, tag, q): return {'batch_id': bid, 'batch_number': bn, 'product': prod, 'tag': tag, 'qty': q, 'unit': 'units'}
T['hx_shipments'] += [
    ship('sh33', 'SHP-2026-033', '2026-10-21', 'Greenway Dispensary St. Louis', 'DIS000412', '4120 Delmar Blvd, St. Louis, MO', '', [it('b-ct1', 'CT-2026-0930', 'Cart 1g · Lemon Haze', '1A4000000000000000021046', '300')], 'shipped'),
    ship('sh32', 'SHP-2026-032', '2026-10-16', 'Ozark Leaf Dispensary', 'DIS000588', '88 Commercial St, Springfield, MO', '0004471203',
         [it('b-pr', 'PR-2026-0915', 'Pre-roll 1g · Blue Dream', '1A4000000000000000021003', '500'), it('b-ct1', 'CT-2026-0930', 'Cart 1g · Lemon Haze', '1A4000000000000000021045', '400')], 'shipped'),
    ship('sh31', 'SHP-2026-031', '2026-10-09', 'Riverbend Cannabis Co.', 'DIS000291', '15 River Rd, Cape Girardeau, MO', '0004470988', [it('b-ct1', 'CT-2026-0930', 'Cart 1g · Lemon Haze', '1A4000000000000000021044', '600')], 'delivered', delivered_on='2026-10-10'),
    ship('sh30', 'SHP-2026-030', '2026-10-06', 'Greenway Dispensary St. Louis', 'DIS000412', '4120 Delmar Blvd, St. Louis, MO', '0004470811', [it('b-pr', 'PR-2026-0915', 'Pre-roll 1g · Blue Dream', '1A4000000000000000021001', '800')], 'delivered', delivered_on='2026-10-06'),
    ship('sh29', 'SHP-2026-029', '2026-10-02', 'Ozark Leaf Dispensary', 'DIS000588', '', '', [it('b-pr', 'PR-2026-0915', 'Pre-roll 1g · Blue Dream', '1A4000000000000000021002', '200')], 'cancelled', cancel_reason='Customer moved the order to next week'),
]

# ---------------- recall ----------------
def con(i, kind, name, role='', org='', phone='', email='', ver='2026-09-02', backup=False):
    return {'id': i, **MO, 'kind': kind, 'name': name, 'role': role, 'organization': org, 'phone': phone, 'after_hours': '', 'email': email, 'notes': '', 'is_backup': backup, 'verified_on': ver, 'active': True, 'sort': 0}
T['hx_recall_contacts'] += [
    con('c1', 'team', 'Sam Salari', 'Recall coordinator', 'Black Fox Manufacturing', '(555) 100-0001', 'sam@blackfox.example'),
    con('c2', 'team', 'Dana Whitfield', 'Quality / compliance', 'Black Fox Manufacturing', '(555) 100-0002'),
    con('c3', 'team', 'Jordan Ortiz', 'Inventory and distribution', 'Black Fox Manufacturing', '(555) 100-0003', backup=True),
    con('c4', 'emergency', 'Fire / police / EMS', '', 'St. Louis County', '911'),
    con('c5', 'regulator', 'DCR Compliance Section', 'Compliance officer', 'Missouri Division of Cannabis Regulation', '(555) 751-0000', 'compliance@dcr.example'),
    con('c6', 'certification', 'CSQ certification body', 'Lead auditor', 'ASI', '(555) 300-4000'),
    con('c7', 'customer', 'Greenway Dispensary St. Louis', 'License DIS000412', 'Greenway Dispensary St. Louis', '(555) 420-4120'),
    con('c8', 'customer', 'Riverbend Cannabis Co.', 'License DIS000291', 'Riverbend Cannabis Co.', '(555) 335-1500'),
    con('c9', 'customer', 'Ozark Leaf Dispensary', 'License DIS000588', 'Ozark Leaf Dispensary', '(555) 862-0088', ver='2025-08-14'),
    con('c10', 'lab', 'Show-Me Analytical Labs', 'QA desk', 'Show-Me Analytical Labs', '(555) 600-2525'),
]
MS = ['team', 'identify', 'back', 'forward', 'quantities', 'locate', 'contacts', 'report']
T['hx_recalls'] += [
    {'id': 'rc2', **MO, 'number': 'MOCK-2026-002', 'kind': 'mock', 'recall_class': '', 'target_type': 'batch', 'target_id': 'b-ct1', 'target_label': 'CT-2026-0930 · Cart 1g · Lemon Haze · cart',
     'reason': 'Q4 mock recall: cartridge batch', 'started_at': ago(38), 'ended_at': None, 'duration_minutes': None,
     'steps': {'team': True, 'identify': True, 'back': True, 'forward': True, 'quantities': False, 'locate': False, 'contacts': False, 'report': False},
     'step_times': {'team': ago(36), 'identify': ago(33), 'back': ago(24), 'forward': ago(15)},
     'notified': [{'id': 'c1', 'name': 'Sam Salari', 'kind': 'team', 'at': ago(36)}, {'id': 'c2', 'name': 'Dana Whitfield', 'kind': 'team', 'at': ago(35)}],
     'trace': {}, 'qty_made': '2400', 'qty_shipped': '1300 units', 'qty_on_hand': '', 'qty_recovered': '', 'findings': '', 'actions': '', 'files': [], 'status': 'open', 'result': '', 'cancel_reason': '',
     'started_by': 'Sam Salari', 'closed_by': ''},
    {'id': 'rc1', **MO, 'number': 'MOCK-2026-001', 'kind': 'mock', 'recall_class': '', 'target_type': 'batch', 'target_id': 'b-pr', 'target_label': 'PR-2026-0915 · Pre-roll 1g · Blue Dream · preroll',
     'reason': 'Yearly mock recall 2026', 'started_at': '2026-09-18T14:00:00Z', 'ended_at': '2026-09-18T14:47:00Z', 'duration_minutes': 47, 'steps': {k: True for k in MS},
     'step_times': {}, 'notified': [], 'trace': {}, 'qty_made': '6000', 'qty_shipped': '1500 units', 'qty_on_hand': '4500', 'qty_recovered': '1500', 'findings': 'Traced back to 2 cone lots and forward to 2 dispensaries in 47 minutes',
     'actions': '', 'files': [], 'status': 'closed', 'result': 'Pass', 'cancel_reason': '', 'started_by': 'Sam Salari', 'closed_by': 'Sam Salari'},
    {'id': 'rc0', **MO, 'number': 'MOCK-2025-001', 'kind': 'mock', 'recall_class': '', 'target_type': 'lot', 'target_id': 'l09', 'target_label': 'RCV-2025-031 · 98mm pre-roll cones', 'reason': 'Yearly mock recall 2025',
     'started_at': '2025-10-02T14:00:00Z', 'ended_at': '2025-10-02T16:21:00Z', 'duration_minutes': 141, 'steps': {k: True for k in MS}, 'step_times': {}, 'notified': [], 'trace': {}, 'qty_made': '', 'qty_shipped': '', 'qty_on_hand': '',
     'qty_recovered': '', 'findings': 'Took over 2 hours: customer contact list out of date', 'actions': 'Contact list moved into Hendrix and verified yearly', 'files': [], 'status': 'closed', 'result': 'Fail', 'cancel_reason': '', 'started_by': 'Sam Salari', 'closed_by': 'Sam Salari'},
]

_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def handle(route, request):
    u = request.url
    if '/rest/v1/rpc/hx_trace_data' in u:
        return jr(route, {'lots': T['hx_lots'], 'uses': [x for x in T['hx_lot_uses'] if not x.get('voided')], 'batches': [b for b in T['hx_batches'] if not b['voided']], 'tests': T['hx_tests'],
                          'ships': [s for s in T['hx_shipments'] if s['status'] != 'cancelled'], 'holds': T['hx_holds'], 'suppliers': T['hx_suppliers']})
    return _h(route, request)

def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def mshot(pg, name, loc=None, h=1700):
    pg.set_viewport_size({'width': 1440, 'height': h}); pg.wait_for_timeout(250)
    pg.evaluate("document.querySelectorAll('.md').forEach(function(e){e.scrollTop=0;})")
    (loc or pg.locator('.md').last).screenshot(path=SHOTS + name)
    pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(150)
def vshot(pg, name):
    pg.evaluate("window.scrollTo(0,0);document.querySelectorAll('*').forEach(function(e){if(e.scrollTop)e.scrollTop=0;})"); pg.wait_for_timeout(300); pg.screenshot(path=SHOTS + name)
def close1(pg):
    pg.locator('.md').last.get_by_role('button', name=re.compile('^(Close|Cancel|Back)$')).last.click(); pg.wait_for_timeout(250)
def close(pg):
    for _ in range(4):
        if not pg.locator('.md').count(): return
        close1(pg)

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell')
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Open suppliers')

    # ===== Suppliers =====
    pg.get_by_role('button', name='Suppliers', exact=True).click(); pg.wait_for_selector('.card >> text=Futurola USA')
    vshot(pg, 'supply_suppliers_list.png')
    pg.get_by_role('button', name='+ Add supplier').click(); md = pg.locator('.md')
    field(md, 'Supplier name').fill('Heartland Glass & Jars'); field(md, 'Category / type').select_option('Packaging'); field(md, 'Risk').select_option('medium')
    field(md, 'Products / services supplied').fill('Child-resistant glass jars, 3.5 g and 7 g')
    field(md, 'Specifications the supplier must meet').fill('Food-grade glass; ASTM D3475 child-resistant lid; certificate of conformance with every lot')
    field(md, 'Contact name').fill('Erin Brooks'); field(md, 'Contact email').fill('erin@heartlandglass.example'); field(md, 'Phone').fill('(555) 640-7788')
    field(md, 'Address').fill('2200 Industrial Dr, Kansas City, MO'); field(md, 'COA expiry date').fill('2027-06-30')
    md.get_by_role('button', name='+ Add credential').click(); cr = md.locator('div.grid', has=pg.locator('input[placeholder=Number]')).last
    cr.locator('select').select_option('Food-grade / GMP certificate'); cr.locator('input[placeholder=Number]').fill('FDA-FCS-10442'); cr.locator('input[type=date]').fill('2027-06-30')
    cr.locator('input[type=file]').set_input_files({'name': 'food-grade.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4'}); pg.wait_for_selector('.md >> text=\U0001f4ce')
    md.locator('label.ck', has_text='Ethical sourcing').locator('input').check()
    mshot(pg, 'supply_suppliers_form.png'); close(pg)
    pg.locator('.card', has_text='Show-Me Analytical Labs').first.click(); pg.wait_for_selector('.md >> text=Credentials')
    mshot(pg, 'supply_suppliers_detail.png'); close(pg)
    pg.locator('.card', has_text='Prairie Packaging Group').first.click(); pg.locator('.md').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.locator('textarea').fill('Supplier questionnaire, ASTM D3475 certificate and spec sheet reviewed; trial lot of 500 bags passed incoming inspection')
    mshot(pg, 'supply_suppliers_approve.png'); close(pg)
    pg.locator('.card', has_text='Ozark Pest Solutions').first.click(); pg.locator('.md').get_by_role('button', name='Record review').click(); md = pg.locator('.md')
    field(md, 'Rating').select_option('Satisfactory'); field(md, 'Result').select_option('Keep approved')
    field(md, 'Notes').fill('12 monthly service reports on file; applicator license current; no pest activity trends')
    mshot(pg, 'supply_suppliers_review.png'); close(pg)
    if pg.locator('.md').count(): close(pg)

    # ===== Receiving =====
    pg.get_by_role('button', name='Receiving', exact=True).click(); pg.wait_for_selector('tr >> text=RCV-2026-018')
    vshot(pg, 'supply_receiving_list.png')
    pg.get_by_role('button', name='+ Receive lot').click(); md = pg.locator('.md')
    field(md, 'Supplier').select_option('s-mdp'); field(md, 'Item received').fill('THC distillate'); field(md, 'Category').select_option('Distillate / extract')
    field(md, 'Quantity').fill('500'); field(md, 'Unit').select_option('g'); field(md, 'Supplier lot #').fill('MDP-DST-1019'); field(md, 'Expiry / best before').fill('2027-10-15')
    field(md, 'METRC tag (cannabis)').fill('1A40A0300001234000000512'); field(md, 'PO / invoice #').fill('PO-4502'); field(md, 'Storage location').fill('Quarantine fridge Q2')
    for c in md.locator('label.ck input[type=checkbox]').all(): c.check()
    md.locator('input[type=file]').set_input_files({'name': 'COA MDP-DST-1019.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4'}); pg.wait_for_selector('.md >> text=COA MDP-DST-1019.pdf')
    field(md, 'Inspection notes').fill('Seal intact, 1 x 500 g jar, received at 4 C')
    mshot(pg, 'supply_receiving_form.png'); close(pg)
    pg.locator('tr', has_text='RCV-2026-018').click(); pg.wait_for_selector('.md >> text=Receiving inspection')
    mshot(pg, 'supply_receiving_detail.png')
    pg.locator('.md').get_by_role('button', name='Accept').click(); pg.wait_for_selector('.md >> text=No COA')
    mshot(pg, 'supply_receiving_accept.png'); close(pg)
    if pg.locator('.md').count(): close(pg)
    pg.locator('.tabs button', has_text='Inventory').click(); pg.wait_for_selector('td >> text=98mm pre-roll cones')
    vshot(pg, 'supply_receiving_inventory.png')
    pg.get_by_role('button', name='+ Record use').click(); md = pg.locator('.md')
    field(md, 'Lot').select_option('l14'); field(md, 'Used in batch').select_option('b-pr'); field(md, 'Quantity').fill('500'); field(md, 'Notes').fill('Line 2, morning shift')
    pg.wait_for_selector('.md >> text=FIFO')
    mshot(pg, 'supply_receiving_use.png'); close(pg)

    # ===== Hold and Release =====
    pg.locator('.tabs button', has_text='Hold and Release').click(); pg.wait_for_selector('.card >> text=HOLD-2026-007')
    vshot(pg, 'supply_holds_list.png')
    pg.get_by_role('button', name='+ Put on hold').click(); md = pg.locator('.md')
    field(md, 'What is held').select_option('batch'); field(md, 'Source').select_option('Complaint'); field(md, 'Batch').select_option('b-gm')
    field(md, 'Quantity held').fill('1,150 units'); field(md, 'Held at (location)').fill('Vault cage V3')
    field(md, 'Reason').fill('Consumer complaint: gummies sticking together in the jar. Hold pending retained-sample check.')
    mshot(pg, 'supply_holds_form.png'); close(pg)
    pg.locator('.card', has_text='HOLD-2026-007').click(); pg.locator('.md').get_by_role('button', name='Decide').click(); md = pg.locator('.md')
    field(md, 'Decision').select_option('destroyed'); field(md, 'Reason / evidence for the decision').fill('Leak confirmed on all 12 returned units; destroy and record in Waste Destruction Log and METRC')
    mshot(pg, 'supply_holds_decide.png'); close(pg)
    if pg.locator('.md').count(): close(pg)

    # ===== Shipping =====
    pg.locator('.tabs button', has_text='Shipping').click(); pg.wait_for_selector('tr >> text=SHP-2026-033')
    vshot(pg, 'supply_shipping_list.png')
    pg.get_by_role('button', name='+ New shipment').click(); md = pg.locator('.md')
    field(md, 'Customer').fill('Riverbend Cannabis Co.'); field(md, 'Customer license #').fill('DIS000291'); field(md, 'Destination address').fill('15 River Rd, Cape Girardeau, MO')
    field(md, 'State manifest #').fill('0004472019'); field(md, 'Transporter').fill('Black Fox fleet'); field(md, 'Driver').fill('Chris Lane'); field(md, 'Vehicle').fill('Van MO-4KT-221')
    sels = md.locator('select').filter(has=pg.locator('option', has_text='(batch)'))
    sels.first.select_option('b-pr'); md.locator('input[placeholder="Package tag"]').first.fill('1A4000000000000000021004'); md.locator('input[placeholder=Qty]').first.fill('400')
    md.get_by_role('button', name='+ Add batch / package').click()
    sels.nth(1).select_option('b-ct2'); md.locator('input[placeholder="Package tag"]').nth(1).fill('1A4000000000000000021121'); md.locator('input[placeholder=Qty]').nth(1).fill('200')
    for c in md.locator('label.ck input[type=checkbox]').all(): c.check()
    pg.wait_for_selector('.md >> text=cannot ship')
    mshot(pg, 'supply_shipping_form.png'); close(pg)
    pg.locator('tr', has_text='SHP-2026-032').click(); pg.wait_for_selector('.md >> text=Pre-load inspection')
    mshot(pg, 'supply_shipping_detail.png'); close(pg)

    # ===== Traceability and Recall =====
    pg.get_by_role('button', name='Traceability and Recall').click(); pg.wait_for_selector('text=Type a received lot number')
    pg.locator('input[placeholder^="Search a lot"]').fill('CT-2026-0930'); pg.locator('.card', has_text='CT-2026-0930').first.click(); pg.wait_for_selector('text=One step back')
    vshot(pg, 'supply_recall_trace.png')
    pg.locator('.tabs button', has_text='Mock recalls and recalls').click(); pg.wait_for_selector('tr >> text=MOCK-2026-001')
    if pg.locator('.md').count(): close(pg)
    vshot(pg, 'supply_recall_exercises.png')
    pg.locator('tr', has_text='MOCK-2026-002').click(); pg.wait_for_selector('.md >> text=Elapsed (limit 2:00:00)')
    md = pg.locator('.md'); field(md, 'On hand').fill('1100')
    mshot(pg, 'supply_recall_run.png', h=3000); close(pg)
    pg.locator('.tabs button', has_text='Recall team and contacts').click(); pg.wait_for_selector('text=Sam Salari')
    vshot(pg, 'supply_recall_contacts.png')
    pg.get_by_role('button', name='Start recall', exact=True).click(); md = pg.locator('.md')
    field(md, 'Lot, batch or package tag').fill('NL-0921-A'); md.locator('.row', has_text='RCV-2026-015').first.click()
    field(md, 'Class').select_option('Class II (temporary or reversible health risk)')
    field(md, 'Reason').fill('Cartridges from hardware lot NL-0921-A leak at the mouthpiece; returns from Riverbend and Greenway')
    mshot(pg, 'supply_recall_start.png'); close(pg)
    b.close()
print('JS errors:', errors if errors else 'none')
