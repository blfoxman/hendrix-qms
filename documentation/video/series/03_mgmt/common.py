# Shared setup for video 03 (mgmt): kit import, fixed dates, seed helpers.
import os, sys, re, json, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
V = '/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/video/'
sys.path.insert(0, V + 'kit')
import hxvideo as hv
hv.set_project(HERE)
SNAP = V + 'index_snapshot2.html'
DUMP = HERE + '/work/seed_dump.json'
TODAY = '2026-10-24'; NOW = '2026-10-24T15:40:00Z'


def setup():
    """Fresh mgmt namespace with the mock's 'today' matched to the browser clock."""
    ns = hv.load_setup('mgmt', snapshot=SNAP)
    ns['TODAY'] = TODAY; ns['NOW'] = NOW
    return ns


def apply_dump(ns, tables):
    d = json.load(open(DUMP))
    for t in tables: ns['T'][t] = json.loads(json.dumps(d[t]))
    for k, v in d['SEQ'].items(): ns['SEQ'][k] = max(ns['SEQ'][k], v)


def menu(pg, name):
    return pg.locator('.nav').get_by_role('button', name=name, exact=True).first


def open_page(pg, ns, name, wait):
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(500)
    menu(pg, name).click(); pg.wait_for_selector(wait); pg.wait_for_timeout(700)


# ------------------------------------------------------------------ direct seeds (copied from manual/shots_mgmt.py)
def seed_changes(ns):
    L = ns['L']; ME = ns['ME']
    def ch(i, num, title, typ, status, req_on, by, desc, why, imp, **kw):
        return {**L, 'id': i, 'number': num, 'title': title, 'change_type': typ, 'product': kw.get('product', ''), 'description': desc, 'reason': why, 'requested_by': by, 'requested_on': req_on, 'target_date': kw.get('target'),
             'impacts': imp, 'impact_notes': kw.get('notes', ''), 'risk_level': kw.get('risk', 'medium'), 'risk_id': None, 'sop_ids': [], 'plan_ids': kw.get('plans', []), 'course_ids': [],
             'actions': kw.get('actions', []), 'training_required': kw.get('tr', False), 'training_done': kw.get('trd', False), 'training_note': kw.get('trn', ''), 'trial_required': kw.get('tri', False), 'trial_result': kw.get('trr', ''), 'trial_note': kw.get('trin', ''),
             'haccp_reviewed': kw.get('hr', False), 'notify': kw.get('notify', {}), 'notified_on': kw.get('non'), 'notified_note': kw.get('nnote', ''), 'status': status,
             'approved_by': ME if status not in ('requested', 'rejected') else '', 'approved_at': kw.get('app'), 'approval_note': kw.get('appn', ''), 'implemented_on': kw.get('impl'), 'effectiveness': kw.get('eff', ''),
             'closed_by': ME if status in ('closed', 'rejected') else '', 'closed_at': kw.get('closed'), 'stop_reason': kw.get('stop'), 'files': [], 'notes': '', 'created_at': req_on + 'T12:00:00Z'}
    A = lambda w, who, due, done=None: {'id': 'a' + w[:4], 'what': w, 'who': who, 'due': due, 'done': bool(done), 'done_on': done}
    ns['T']['hx_changes'] = [
        ch('cc5', 'CC-2026-005', 'Switch exit bags to a non child-resistant supplier', 'material', 'rejected', '2026-10-08', 'Marcus Bell', 'Buy exit bags from a cheaper supplier', 'Cost', {'labels': True, 'license': True}, stop='Missouri requires child-resistant exit packaging; not acceptable', closed='2026-10-09T15:00:00Z'),
        ch('cc4', 'CC-2026-004', 'Pre-roll filling SOP: add a cone weight check', 'document', 'requested', '2026-10-19', 'Priya Shah', 'Add a 10-cone weight check every hour to SOP-PRD-012', 'Two complaints about light pre-rolls', {'sops': True, 'training': True}, tr=True),
        ch('cc3', 'CC-2026-003', 'Silicone gummy molds on line 2', 'equipment', 'approved', '2026-10-02', 'Maria Lopez', 'Replace starch trays with food-grade silicone molds on line 2', 'Faster release, less starch dust', {'haccp': True, 'training': True, 'equipment': True, 'license': True},
           product='Gummies 10pk 100mg', plans=[], tr=True, trn='Line 2 crew on mold handling and cleaning', notify={'regulator': True}, app='2026-10-06T16:00:00Z',
           actions=[A('Buy and validate molds (3 trial batches)', 'Maria Lopez', '2026-10-20', '2026-10-18'), A('Update the sanitation SOP for molds', 'Jordan Reyes', '2026-10-30')]),
        ch('cc2', 'CC-2026-002', 'Longer purge time for BHO live resin', 'process', 'implemented', '2026-09-03', 'Maria Lopez', 'Purge 72 h instead of 48 h at 100 F', 'Residual solvent failure on BHO-2609-002', {'haccp': True, 'sops': True, 'specs': True},
           hr=True, app='2026-09-04T14:00:00Z', impl='2026-09-15', actions=[A('Update purge SOP', 'Maria Lopez', '2026-09-10', '2026-09-09'), A('Revalidate CCP 1 limits', 'Lee Park', '2026-09-14', '2026-09-14')]),
        ch('cc1', 'CC-2026-001', 'Approve a second terpene supplier', 'material', 'closed', '2026-08-11', ME, 'Add a second inhalation-grade terpene supplier', 'Single source risk (RK-012)', {'suppliers': True, 'specs': True},
           app='2026-08-12T14:00:00Z', impl='2026-08-29', eff='Two orders received with COAs; blends matched spec in 3 batches', closed='2026-09-30T15:00:00Z', actions=[A('Supplier approval and COA review', 'Lee Park', '2026-08-25', '2026-08-24')])]
    ns['SEQ']['CC'] = 5


def seed_org(ns):
    L = ns['L']; ME = ns['ME']
    def pos(i, t, p, to, dep, resp, roles, bk='', s=0): return {**L, 'id': i, 'title': t, 'person_name': p, 'reports_to': to, 'department': dep, 'responsibilities': resp, 'quality_roles': roles, 'backup_name': bk, 'sort': s, 'created_at': '2026-09-01T12:00:00Z'}
    ns['T']['hx_org_positions'] = [
        pos('op1', 'General Manager', ME, None, 'Management', 'Runs the facility; provides resources for the quality system; chairs the management review', ['Senior management'], 'Lee Park'),
        pos('op2', 'Quality Manager', 'Lee Park', 'op1', 'Quality', 'CSQ practitioner; owns the QMS, CAPA, HACCP and internal audits; releases batches', ['Quality / CSQ lead', 'HACCP team leader', 'Recall coordinator'], 'Maria Lopez', 1),
        pos('op3', 'Production Manager', 'Maria Lopez', 'op1', 'Production', 'Plans and runs production; batch records; line clearance', ['Quality backup', 'Food safety / product defense'], 'Jordan Reyes', 2),
        pos('op4', 'Compliance Specialist', 'Marcus Bell', 'op1', 'Compliance', 'METRC, state reporting, label review, rule changes', ['Regulatory contact (state / METRC)'], ME, 3),
        pos('op5', 'QA Technician', 'Priya Shah', 'op2', 'Quality', 'Sampling, COA review, CCP record review, training records', ['Training coordinator', 'Internal auditor'], 'Lee Park'),
        pos('op6', 'Production Lead', 'Jordan Reyes', 'op3', 'Production', 'Leads the gummy and cartridge lines; sanitation and changeovers', ['Sanitation lead'], 'Maria Lopez'),
        pos('op7', 'Maintenance Technician', '', 'op3', 'Production', 'Preventive maintenance and calibration of scales and meters', ['Maintenance / calibration'], 'Jordan Reyes', 1)]


def seed_objectives(ns):
    L = ns['L']; ME = ns['ME']; T = ns['T']
    T['hx_sops'] = [{**L, 'id': 'sp1', 'license_ids': ['lic-mo'], 'sop_number': 'SOP-QA-001', 'title': 'Safety, Quality and Compliance Policy', 'version': '3', 'status': 'published'},
                    {**L, 'id': 'sp2', 'license_ids': ['lic-mo'], 'sop_number': 'SOP-PRD-012', 'title': 'Pre-roll filling', 'version': '2', 'status': 'published'}]
    T['hx_qms_settings'] = [{**L, 'policy_sop_id': 'sp1', 'policy_note': 'Signed by all staff at hire and on each new version; posted in the break room; reviewed every year in the management review'}]
    T['hx_capas'] = [{**L, 'id': 'ca%d' % i, 'number': 'CAPA-2026-%03d' % (10 + i), 'title': t, 'status': 'closed', 'closed_at': c + 'T15:00:00Z', 'due_date': d, 'effectiveness_rating': 'effective'}
                     for i, (t, c, d) in enumerate([('Label misprint on gummies', '2026-09-08', '2026-09-10'), ('Scale out of calibration', '2026-09-12', '2026-09-15'), ('Light pre-rolls', '2026-09-22', '2026-09-18'), ('Missing sanitation signature', '2026-09-26', '2026-09-30')])]
    T['hx_capas'] += [{**L, 'id': 'ca9', 'number': 'CAPA-2026-019', 'title': 'Residual solvent failure CART-2610-008', 'status': 'open', 'closed_at': None, 'due_date': '2026-11-21', 'effectiveness_rating': None},
                      {**L, 'id': 'ca8', 'number': 'CAPA-2026-018', 'title': 'Pest trap map out of date', 'status': 'in_progress', 'closed_at': None, 'due_date': '2026-10-20', 'effectiveness_rating': None}]
    def obj(i, n, name, cat, metric, unit, dirn, tgt, freq, owner, desc='', plan=''):
        return {**L, 'id': i, 'number': n, 'name': name, 'category': cat, 'description': desc, 'metric': metric, 'unit': unit, 'direction': dirn, 'target': tgt, 'frequency': freq, 'owner': owner, 'start_on': '2026-04-01', 'due_on': None, 'action_plan': plan, 'status': 'active', 'close_note': None, 'created_at': '2026-04-01T12:00:00Z'}
    T['hx_objectives'] = [obj('ob1', 'OBJ-001', 'CAPAs closed on time', 'quality', 'capa_on_time', '%', 'up', 90, 'monthly', 'Lee Park', 'Policy: we fix problems at the root, on time'),
                          obj('ob2', 'OBJ-002', 'Deviations per month', 'quality', 'deviations', 'deviations', 'down', 4, 'monthly', 'Maria Lopez'),
                          obj('ob3', 'OBJ-003', 'CCP checks within critical limits', 'food_safety', 'ccp_ok', '%', 'up', 98, 'monthly', 'Lee Park'),
                          obj('ob4', 'OBJ-004', 'Batch tests passed first time', 'quality', 'tests_pass', '%', 'up', 95, 'monthly', 'Lee Park'),
                          obj('ob5', 'OBJ-005', 'Complaints per quarter', 'customer', 'complaints', 'complaints', 'down', 3, 'quarterly', 'Marcus Bell'),
                          obj('ob6', 'OBJ-006', 'On-time delivery to dispensaries', 'customer', 'manual', '%', 'up', 95, 'quarterly', ME, '', 'Weekly shipping plan with the sales team')]
    ns['SEQ']['OBJ'] = 6
    def res(o, p, v, mt, act=''): T['hx_objective_results'].append({**L, 'id': 'or-%s-%s' % (o, p), 'objective_id': o, 'period': p, 'value': v, 'met': mt, 'auto': True, 'comment': '', 'action': act, 'recorded_by': 'Lee Park', 'created_at': p[:7] + '-28T12:00:00Z' if '-Q' not in p else '2026-07-05T12:00:00Z', 'updated_at': '2026-10-05T12:00:00Z'})
    for p, v in (('2026-05', 100), ('2026-06', 86), ('2026-07', 92), ('2026-08', 95)): res('ob1', p, v, v >= 90, 'CAPA review added to the weekly production meeting' if v < 90 else '')
    for p, v in (('2026-05', 3), ('2026-06', 5), ('2026-07', 2), ('2026-08', 4), ('2026-09', 3)): res('ob2', p, v, v <= 4, 'Line clearance retraining for the cartridge crew' if v > 4 else '')
    for p, v in (('2026-05', 100), ('2026-06', 100), ('2026-07', 97.5), ('2026-08', 100), ('2026-09', 100)): res('ob3', p, v, v >= 98, 'Curing room humidity alarm installed' if v < 98 else '')
    for p, v in (('2026-05', 96), ('2026-06', 100), ('2026-07', 94), ('2026-08', 97), ('2026-09', 92)): res('ob4', p, v, v >= 95, 'Residual solvent investigation (CAPA-2026-019); purge time extended' if v < 95 else '')
    for p, v in (('2026-Q1', 2), ('2026-Q2', 4), ('2026-Q3', 2)): res('ob5', p, v, v <= 3, 'Pre-roll weight check added (CC-2026-004)' if v > 3 else '')
    for p, v in (('2026-Q2', 93), ('2026-Q3', 97)): res('ob6', p, v, v >= 95, 'Weekly shipping plan with sales' if v < 95 else '')


def seed_review(ns):
    L = ns['L']; ME = ns['ME']; T = ns['T']; REQ = ns['REQ']
    T['hx_complaints'] = [{**L, 'id': 'co%d' % i, 'number': 'CMP-2026-%03d' % i, 'received_on': d, 'category': c, 'type': 'complaint', 'status': s} for i, (d, c, s) in
                          enumerate([('2026-02-11', 'Product quality', 'closed'), ('2026-05-02', 'Packaging', 'closed'), ('2026-06-19', 'Product quality', 'closed'), ('2026-08-30', 'Potency', 'closed'), ('2026-10-17', 'Product quality', 'investigating')], 1)]
    T['hx_deviations'] = [{**L, 'id': 'dv%d' % i, 'number': 'DEV-2026-%03d' % (20 + i), 'title': 'x', 'created_at': d + 'T10:00:00Z', 'category': c, 'priority': p, 'status': 'closed' if i < 5 else 'open'} for i, (d, c, p) in
                          enumerate([('2026-03-04', 'Sanitation', 'minor'), ('2026-05-18', 'Labeling', 'major'), ('2026-06-07', 'Process / procedure', 'minor'), ('2026-08-21', 'Equipment', 'minor'), ('2026-10-22', 'Process / procedure', 'critical')], 1)]
    T['hx_audits'] = [{**L, 'id': 'au1', 'audit_date': '2026-09-15', 'audit_type': 'internal', 'status': 'completed'}, {**L, 'id': 'au2', 'audit_date': '2026-04-09', 'audit_type': 'regulatory', 'status': 'closed'}]
    T['hx_audit_findings'] = [{**L, 'id': 'af1', 'severity': 'minor', 'status': 'open', 'due_date': '2026-11-15'}]
    T['hx_conformance'] = [{**L, 'id': 'cf%d' % i, 'standard_id': 's1', 'clause_id': 'c%d' % i, 'status': s} for i, s in enumerate(['Conforming'] * 38 + ['Partial'] * 6 + ['Not conforming'] * 1 + ['Not applicable'] * 3)]
    T['hx_suppliers'] = [{**L, 'license_ids': ['lic-mo'], 'id': 'su%d' % i, 'name': n, 'status': s, 'next_review': nr, 'last_review': lr} for i, (n, s, nr, lr) in
                         enumerate([('Ceramic hardware supplier', 'approved', '2027-03-01', '2026-03-01'), ('Terpene supplier A', 'approved', '2027-08-24', '2026-08-24'), ('Packaging supplier', 'conditional', '2026-10-01', '2025-10-01')])]
    T['hx_mgmt_reviews'] = [{**L, 'id': 'mr0', 'number': 'MR-2025-001', 'meeting_date': '2025-10-20', 'period_from': '2024-10-21', 'period_to': '2025-10-20', 'chair': ME, 'attendees': 'Sam Salari (GM), Lee Park (QA), Maria Lopez (Production)',
                             'inputs': {k: {'data': '', 'notes': 'Reviewed'} for k in REQ}, 'decisions': 'System suitable; start CSQ Level 3', 'resources': 'Hire a QA technician', 'status': 'held', 'signed_by': ME, 'signed_at': '2025-10-20T20:00:00Z',
                             'actions': [{'id': 'x1', 'what': 'Hire a QA technician', 'who': ME, 'due': '2026-01-31', 'done': True, 'done_on': '2026-01-12'}, {'id': 'x2', 'what': 'Build the HACCP plans for gummies and cartridges', 'who': 'Lee Park', 'due': '2026-06-30', 'done': True, 'done_on': '2026-06-24'},
                                         {'id': 'x3', 'what': 'Approve a second hardware supplier', 'who': 'Marcus Bell', 'due': '2026-09-30', 'done': False}],
                             'next_review': '2026-10-20', 'shared_with': 'All managers', 'shared_on': '2025-10-24', 'files': [], 'created_at': '2025-10-20T15:00:00Z'}]


def seed_verif_links(ns):
    L = ns['L']; T = ns['T']
    T['hx_facility_log'] = [{**L, 'id': 'fl1', 'log_type': 'sanitation', 'created_at': '2026-10-22T14:00:00Z', 'data': {'verified_by': 'Jordan Reyes'}, 'voided': False, 'result': 'Pass'}]
    T['hx_equipment_events'] = [{**L, 'id': 'ee1', 'kind': 'calibration', 'done_on': '2026-10-05', 'voided': False}]
    T['hx_line_clearances'] = [{**L, 'id': 'lc1', 'checked_at': '2026-09-14T13:00:00Z', 'verified_by': 'Maria Lopez', 'voided': False, 'result': 'cleared', 'batch_id': 'b1'}]
    T['hx_env_tests'] = [{**L, 'id': 'et1', 'sampled_on': '2026-03-04', 'voided': False, 'result': 'pass'}]


def seed_all(ns):
    apply_dump(ns, ['hx_haccp_plans', 'hx_haccp_monitoring', 'hx_haccp_verifications', 'hx_risks', 'hx_risk_reviews', 'hx_verification_plan', 'hx_verification_records'])
    seed_changes(ns); seed_org(ns); seed_objectives(ns); seed_review(ns); seed_verif_links(ns)
