# Screenshots for the manual chapter "Quality system" (group qual):
# QMS, Complaints, Internal Audits, SOPs, Training.
import re, copy, base64, io, subprocess, datetime as dt
exec(open('/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/mock_c.py').read())
from PIL import Image, ImageDraw

SHOTS = OUT + 'manual/shots/'
ME_NAME = 'Dana Brooks'
T['hx_profiles'][0]['name'] = ME_NAME
S, L = 'st-mo', 'lic-mo'
TODAY = dt.date.today()
def d(s): return s
def ts(day, hm='10:15'): return day + 'T' + hm + ':00.000Z'

# ---------------- people and roles ----------------
T['hx_roles'] += [{'id': 'r-pm', 'name': 'Production Manager', 'description': 'Runs production', 'perms': {}, 'sort': 0},
                  {'id': 'r-co', 'name': 'Compliance Officer', 'description': 'QA and compliance', 'perms': {}, 'sort': 1},
                  {'id': 'r-pt', 'name': 'Production Tech', 'description': 'Line work', 'perms': {}, 'sort': 2},
                  {'id': 'r-ex', 'name': 'Extraction Tech', 'description': 'Extraction and refinement', 'perms': {}, 'sort': 3},
                  {'id': 'r-sa', 'name': 'Sanitation', 'description': 'Cleaning and sanitation', 'perms': {}, 'sort': 4}]
T['hx_profiles'][0]['role_ids'] = ['r-co']
ROSTER = [{'id': ADMIN, 'name': ME_NAME, 'role_ids': ['r-co'], 'license_ids': [], 'is_admin': True},
          {'id': 'u-marcus', 'name': 'Marcus Lee', 'role_ids': ['r-pm'], 'license_ids': [L], 'is_admin': False},
          {'id': 'u-priya', 'name': 'Priya Shah', 'role_ids': ['r-ex'], 'license_ids': [L], 'is_admin': False},
          {'id': 'u-jordan', 'name': 'Jordan Ellis', 'role_ids': ['r-pt'], 'license_ids': [L], 'is_admin': False},
          {'id': 'u-tess', 'name': 'Tess Whitaker', 'role_ids': ['r-pt'], 'license_ids': [L], 'is_admin': False},
          {'id': 'u-ana', 'name': 'Ana Morales', 'role_ids': ['r-sa'], 'license_ids': [L], 'is_admin': False}]
NAME = {p['id']: p['name'] for p in ROSTER}
for p in ROSTER[1:]:
    T['hx_profiles'].append({'id': p['id'], 'name': p['name'], 'email': p['name'].split()[0].lower() + '@blackfox.test', 'role': 'member', 'approved': True, 'role_ids': p['role_ids'], 'license_ids': p['license_ids'], 'created_at': '2026-01-05'})

# ---------------- batches (for complaints) ----------------
T['hx_batches'] += [
  {'id': 'b-ct', 'state_id': S, 'license_id': L, 'batch_type': 'cart', 'batch_number': 'CT-261003', 'sku': 'Live Resin Cart 1g', 'flavor': 'Blue Dream', 'status': '', 'voided': False, 'created_at': ts('2026-10-03'), 'data': {}},
  {'id': 'b-gm', 'state_id': S, 'license_id': L, 'batch_type': 'gummy', 'batch_number': 'GM-260930', 'sku': 'Gummies 10pk 100mg', 'flavor': 'Sour Watermelon', 'status': '', 'voided': False, 'created_at': ts('2026-09-30'), 'data': {}},
  {'id': 'b-pr', 'state_id': S, 'license_id': L, 'batch_type': 'pre_rolls', 'batch_number': 'PR-261020', 'sku': 'Shorties 0.5g Pre-Roll 5pk', 'flavor': 'Mango Haze', 'status': '', 'voided': False, 'created_at': ts('2026-10-20'), 'data': {}}]

# ---------------- QMS: deviations and CAPAs ----------------
def dev(n, day, title, dept, cat, pri, desc, status, **k):
    r = {'id': 'dev-%d' % n, 'state_id': S, 'license_id': L, 'number': 'DEV-2026-%03d' % n, 'title': title, 'dept': dept, 'category': cat, 'priority': pri, 'description': desc,
         'product_affected': '', 'lot_number': '', 'occurred_on': day, 'source_type': 'manual', 'source_id': '', 'source_label': '', 'immediate_action': '', 'rca_required': None, 'rca_decided_by': '',
         'root_cause': '', 'owner_name': '', 'due_date': None, 'status': status, 'close_note': '', 'closed_by': '', 'closed_at': None, 'cancel_reason': '', 'attachments': [],
         'reported_by': 'Marcus Lee', 'reported_by_id': 'u-marcus', 'created_at': ts(day, '09:40'), 'updated_by': ME_NAME, 'updated_at': ts(day, '16:05')}
    r.update(k); return r
T['hx_deviations'] = [
  dev(8, '2026-10-22', 'Pre-roll weight under spec on line 2', 'Production', 'Product quality', 'major',
      'Hourly weight check found 14 of 120 Mango Haze shorties at 0.44-0.46 g (spec 0.48-0.52 g).', 'in_progress',
      product_affected='Shorties 0.5g Pre-Roll 5pk · Mango Haze', lot_number='PR-261020', immediate_action='Line 2 stopped. All 120 units re-weighed; 14 underweight units pulled and refilled.',
      rca_required=True, rca_decided_by=ME_NAME, root_cause='Cone filler auger worn; the filler was 3 weeks past its calibration date.', owner_name='Marcus Lee', due_date='2026-11-05', updated_at=ts('2026-10-23', '11:20')),
  dev(7, '2026-10-19', 'Temp / Humidity Log: Fail — Vault 1', 'Facility', 'Environment / temperature', 'critical',
      'Vault 1 read 79 °F and 68% RH at the 6 am check (limit 60-75 °F, 45-62% RH).', 'open', source_type='facility_log', source_id='fl-1', source_label='Temp / Humidity Log 2026-10-19 · Vault 1',
      product_affected='Distillate drums (bulk)', immediate_action='Distillate drums moved to Vault 2. HVAC contractor called.', owner_name='Chris Novak', due_date='2026-10-21', reported_by='Ana Morales', reported_by_id='u-ana', updated_at=ts('2026-10-19', '08:10')),
  dev(6, '2026-09-30', 'Lab test Failed: GM-260930 (yeast and mold)', 'Compliance', 'Testing result', 'critical',
      'COA from Green Lab: total yeast and mold 14,000 CFU/g (limit 10,000).', 'in_progress', source_type='test', source_id='t-1', source_label='Lab test GM-260930 · 1A4000000000000000004412',
      product_affected='Gummies 10pk 100mg · Sour Watermelon', lot_number='GM-260930', immediate_action='Batch put on hold H-2026-004. Retained samples sent for retest.',
      rca_required=True, rca_decided_by=ME_NAME, root_cause='Curing room humidity above 65% for 2 days; dehumidifier drain was blocked.', owner_name=ME_NAME, due_date='2026-11-15', reported_by=ME_NAME, reported_by_id=ADMIN, updated_at=ts('2026-10-12', '14:30')),
  dev(5, '2026-09-18', 'Wrong flavor label on Live Resin carts', 'Production', 'Labeling / packaging', 'major',
      '40 Blue Dream carts labeled as Gelato during packaging.', 'closed', product_affected='Live Resin Cart 1g · Blue Dream', lot_number='CT-260915', immediate_action='All 40 units relabeled before release; label roll returned.',
      rca_required=True, rca_decided_by=ME_NAME, root_cause='Two label rolls on the same bench at changeover.', owner_name='Marcus Lee', due_date='2026-09-30', close_note='CAPA-2026-002 verified effective.', closed_by=ME_NAME, closed_at=ts('2026-10-08', '15:00'), updated_at=ts('2026-10-08', '15:00')),
  dev(4, '2026-09-08', 'Terpene lot received without COA', 'Warehouse', 'Supplier / material', 'minor',
      'Two 1 kg terpene bottles (Blue Dream profile) arrived without the supplier COA.', 'closed', product_affected='Terpenes - Blue Dream profile', lot_number='TRP-0826-11', immediate_action='Lot held at receiving until the COA was emailed the next day.',
      rca_required=False, rca_decided_by=ME_NAME, owner_name='Ana Morales', close_note='COA received and filed.', closed_by=ME_NAME, closed_at=ts('2026-09-10', '10:00'), updated_at=ts('2026-09-10', '10:00')),
  dev(3, '2026-08-12', 'Sanitation log missed in extraction room', 'Sanitation', 'Sanitation', 'minor',
      'End-of-shift clean of the extraction room was not logged on Aug 11.', 'closed', immediate_action='Room re-cleaned and logged before the next run.', rca_required=False, rca_decided_by=ME_NAME, owner_name='Ana Morales',
      closed_by=ME_NAME, closed_at=ts('2026-08-13', '09:00'), updated_at=ts('2026-08-13', '09:00')),
  dev(2, '2026-07-07', 'Pest station 4 activity found', 'Facility', 'Pest', 'major', 'Rodent droppings at exterior station 4 near the loading dock.', 'closed',
      immediate_action='Pest contractor serviced the station; dock door seal checked.', rca_required=True, rca_decided_by=ME_NAME, root_cause='Dock door seal torn at the bottom corner.', owner_name='Chris Novak',
      closed_by=ME_NAME, closed_at=ts('2026-07-20', '11:00'), updated_at=ts('2026-07-20', '11:00')),
  dev(1, '2026-05-14', 'Gummy depositor temperature out of range', 'Production', 'Equipment', 'minor', 'Depositor hopper read 92 °C, above the 85 °C limit, for 10 minutes.', 'closed',
      immediate_action='Run paused until the hopper cooled; product from the 10 minutes held and passed QC.', rca_required=False, rca_decided_by=ME_NAME, owner_name='Marcus Lee',
      closed_by=ME_NAME, closed_at=ts('2026-05-16', '13:00'), updated_at=ts('2026-05-16', '13:00'))]
def capa(n, devn, day, title, status, **k):
    dv = next(x for x in T['hx_deviations'] if x['number'] == 'DEV-2026-%03d' % devn)
    r = {'id': 'capa-%d' % n, 'state_id': S, 'license_id': L, 'number': 'CAPA-2026-%03d' % n, 'title': title, 'deviation_id': dv['id'], 'dept': dv['dept'], 'priority': dv['priority'],
         'issue_description': dv['description'], 'root_cause': dv['root_cause'], 'correction': dv['immediate_action'], 'preventive_action': '', 'responsible_person_id': '', 'responsible_person_name': '',
         'due_date': None, 'verification_method': '', 'verification_evidence': '', 'verified_by': '', 'verified_at': None, 'effectiveness_rating': '', 'status': status, 'closed_by': '', 'closed_at': None,
         'cancel_reason': '', 'attachments': [], 'created_by': ME_NAME, 'created_by_id': ADMIN, 'created_at': ts(day, '11:00'), 'updated_by': ME_NAME, 'updated_at': ts(day, '11:00')}
    r.update(k); return r
T['hx_capas'] = [
  capa(4, 8, '2026-10-23', 'CAPA for DEV-2026-008: Pre-roll weight under spec on line 2', 'open', preventive_action='Replace the auger; add the cone filler to the monthly calibration schedule; weight check every 30 minutes for 2 weeks.',
       responsible_person_id='u-marcus', responsible_person_name='Marcus Lee', due_date='2026-11-20', verification_method='20 consecutive shifts of in-spec weight checks on line 2'),
  capa(3, 6, '2026-10-02', 'CAPA for DEV-2026-006: Lab test Failed: GM-260930 (yeast and mold)', 'in_progress', preventive_action='Weekly drain check on the curing room dehumidifier; humidity alarm at 60% RH.',
       responsible_person_id='u-ana', responsible_person_name='Ana Morales', due_date='2026-11-15', verification_method='Next 4 gummy batches pass yeast and mold; no humidity alarms for 30 days',
       verification_evidence='3 of 4 batches passed. GM-261014 tested 9,800 CFU/g (pass, close to the limit).', effectiveness_rating='partially', verified_by=ME_NAME, verified_at=ts('2026-10-21', '15:30'), updated_at=ts('2026-10-21', '15:30')),
  capa(2, 5, '2026-09-19', 'CAPA for DEV-2026-005: Wrong flavor label on Live Resin carts', 'closed', preventive_action='One label roll per bench; second-person label check signed on the batch record.',
       responsible_person_id='u-marcus', responsible_person_name='Marcus Lee', due_date='2026-10-10', verification_method='Review the next 10 cart batch records for the second-person check',
       verification_evidence='10 batch records reviewed (CT-260920 to CT-261003): second-person label check signed on all. No repeat.', effectiveness_rating='effective', verified_by=ME_NAME, verified_at=ts('2026-10-08', '14:50'),
       closed_by=ME_NAME, closed_at=ts('2026-10-08', '14:50'), updated_at=ts('2026-10-08', '14:50')),
  capa(1, 2, '2026-07-08', 'CAPA for DEV-2026-002: Pest station 4 activity found', 'closed', preventive_action='Monthly check of all dock door seals added to the Security Inspection log.',
       responsible_person_id='u-marcus', responsible_person_name='Marcus Lee', due_date='2026-08-15', verification_method='No activity at exterior stations for 30 days',
       verification_evidence='Pest log reviewed Jul 20 - Aug 20: no activity at any station.', effectiveness_rating='effective', verified_by=ME_NAME, verified_at=ts('2026-08-21', '10:00'),
       closed_by=ME_NAME, closed_at=ts('2026-08-21', '10:00'), updated_at=ts('2026-08-21', '10:00'))]

# ---------------- Complaints ----------------
def cmp(num, day, typ, title, status, **k):
    r = {'id': 'cmp-' + num, 'state_id': S, 'license_id': L, 'number': num, 'received_on': day, 'title': title, 'type': typ, 'priority': 'minor', 'channel': 'Phone', 'complainant': '', 'complainant_contact': '',
         'customer': '', 'category': '', 'product': '', 'lot_number': '', 'batch_id': None, 'tag': '', 'description': '', 'rating': None, 'investigator': '', 'due_date': None, 'investigation': '', 'root_cause': '',
         'resolution': '', 'corrective_action': '', 'deviation_id': None, 'deviation_number': '', 'hold_id': None, 'response': '', 'responded_on': None, 'regulator_reported_on': None, 'status': status,
         'closed_by': '', 'closed_at': None, 'cancel_reason': '', 'attachments': [], 'created_by': ME_NAME, 'created_by_id': ADMIN, 'created_at': ts(day, '13:00'), 'updated_by': '', 'updated_at': ts(day, '13:00')}
    r.update(k); return r
T['hx_complaints'] = [
  cmp('CMP-2026-006', '2026-10-20', 'dispensary', 'Live Resin carts not hitting', 'investigating', priority='minor', channel='Email', complainant='Kayla Reed (buyer)', complainant_contact='kayla@greenlightmo.test', customer='Greenlight Dispensary',
      category='Hardware / packaging failure', product='Live Resin Cart 1g · Blue Dream', lot_number='CT-261003', batch_id='b-ct', description='6 of 50 carts returned by customers: no vapor on a fully charged battery.', investigator=ME_NAME, due_date='2026-10-22'),
  cmp('CMP-2026-005', '2026-10-15', 'adverse_event', 'Dizziness reported after a Sour Watermelon gummy', 'open', priority='critical', channel='Dispensary', complainant='Anonymous patient', customer='Rooted Remedies',
      category='Adverse health effect', product='Gummies 10pk 100mg · Sour Watermelon', lot_number='GM-260930', batch_id='b-gm', description='Patient reported dizziness and nausea 2 hours after one 10 mg gummy.'),
  cmp('CMP-2026-004', '2026-10-06', 'consumer', 'White spots on Sour Watermelon gummies', 'investigating', priority='critical', channel='Website / social media', complainant='M. Turner', complainant_contact='555-0148',
      customer='Rooted Remedies', category='Mold / contamination', product='Gummies 10pk 100mg · Sour Watermelon', lot_number='GM-260930', batch_id='b-gm', tag='1A4000000000000000004412',
      description='Customer sent photos of white fuzzy spots on 3 gummies in a sealed jar bought Oct 4.', investigator=ME_NAME, due_date='2026-11-06',
      investigation='Retained samples of GM-260930 checked: 2 of 10 jars show spots. Batch COA failed yeast and mold (DEV-2026-006). Curing room humidity log reviewed.',
      root_cause='Curing room humidity above 65% for 2 days (blocked dehumidifier drain).', deviation_id='dev-6', deviation_number='DEV-2026-006', hold_id='hold-4'),
  cmp('CMP-2026-003', '2026-09-28', 'return', 'Pre-roll box returned: cones crushed', 'closed', channel='In person', customer='Midtown Cannabis Co.', category='Hardware / packaging failure', product='Shorties 0.5g Pre-Roll 5pk · Mango Haze', lot_number='PR-260921',
      investigator='Marcus Lee', due_date='2026-10-28', investigation='Case packed with 12 boxes instead of 10; boxes crushed in transit.', resolution='Replacement case shipped Sep 30.', corrective_action='Case pack count added to the shipping checklist.',
      response='Called the buyer and confirmed the replacement.', responded_on='2026-09-30', closed_by=ME_NAME, closed_at=ts('2026-10-01', '10:00')),
  cmp('CMP-2026-002', '2026-09-09', 'dispensary', 'Leaking carts in a case from Greenlight', 'closed', priority='major', channel='Phone', complainant='Kayla Reed (buyer)', complainant_contact='555-0101', customer='Greenlight Dispensary',
      category='Leaking / damage', product='Live Resin Cart 1g · Gelato', lot_number='CT-260901', investigator='Marcus Lee', due_date='2026-10-09', investigation='Retained carts checked: 3 of 20 caps not fully pressed.',
      resolution='12 carts replaced.', corrective_action='Capping press pressure check added at start of shift.', response='Email with replacement details.', responded_on='2026-09-11', closed_by=ME_NAME, closed_at=ts('2026-09-24', '15:00')),
  cmp('CMP-2026-001', '2026-08-12', 'consumer', 'Harsh taste on Blue Dream cart', 'closed', channel='Phone', complainant='J. Alvarez', complainant_contact='555-0177', category='Taste / smell', product='Live Resin Cart 1g · Blue Dream', lot_number='CT-260805',
      investigator=ME_NAME, due_date='2026-09-12', investigation='Retained sample tasted normal; customer battery set to 4.2 V.', resolution='Explained the voltage setting; replacement cart sent.', response='Called back Aug 13.', responded_on='2026-08-13',
      closed_by=ME_NAME, closed_at=ts('2026-08-14', '09:30')),
  cmp('FBK-2026-002', '2026-10-10', 'feedback', 'Rooted Remedies: customers like the new gummy flavor', 'open', channel='In person', customer='Rooted Remedies', rating=4, product='Gummies 10pk 100mg · Sour Watermelon', description='Sell-through good; asks for a 20-pack.'),
  cmp('FBK-2026-001', '2026-09-15', 'feedback', 'Greenlight: Mango Haze shorties selling fast', 'open', channel='Email', customer='Greenlight Dispensary', rating=5, product='Shorties 0.5g Pre-Roll 5pk · Mango Haze')]

# ---------------- Internal audits ----------------
HT = open('/home/claude/hendrix/index.html').read()
CL = {}
for m in re.finditer(r"\n \['([0-9A-Z.]+)','([0-9A-Z]+)','((?:[^'\\]|\\.)+)'", HT): CL[m.group(1)] = (m.group(2), m.group(3).replace("\\'", "'"))
def ck(c, res, ev): return {'clause': c, 'title': CL[c][1], 'result': res, 'evidence': ev}
m1 = [ck(c, 'Conforming', ev) for c, ev in [('1.1', 'Hendrix QMS holds SOPs, logs and the Rulebook'), ('1.2', 'Quality policy SOP signed by all staff'), ('1.3', 'Missouri Rulebook current; training records'),
      ('1.4', 'SOP master list, audit trail reviewed'), ('1.5', 'Annual audit program in Hendrix'), ('1.6', '6 deviations reviewed, CAPAs verified'), ('1.7', 'Complaint log reviewed'), ('1.8', 'Mock recall Mar 2026, 74 min'),
      ('1.9', 'Threat assessment on file'), ('1.10', 'Fraud vulnerability assessment on file')]] + [ck('1.11', 'Observation', 'Crisis plan contact list is 8 months old')]
m2 = [ck(c, r, ev) for c, r, ev in [('2A.2.3', 'Conforming', 'Scale calibration log current'), ('2A.3', 'Conforming', 'Sanitation logs complete for Sept'), ('2A.5.1', 'Conforming', 'Pest contractor reports'),
      ('2A.9.2', 'Conforming', 'Chemical list and SDS binder'), ('2A.9.3', 'Nonconforming', 'Vault 1: 3 excursions in Sept without a deviation'), ('2A.10.4', 'Conforming', 'Hold log'),
      ('2A.12.1', 'Conforming', 'SOPs at workstations are current'), ('2A.12.3', 'Conforming', 'Line clearance records'), ('2A.12.8', 'Conforming', 'Label checks on batch records'),
      ('2A.13.2', 'Conforming', 'Training matrix 91% current'), ('2A.13.6', 'Conforming', 'PPE worn in all rooms'), ('2A.13.7', 'Nonconforming', 'No paper towels at the packaging handwash sink')]]
T['hx_audits'] = [
  {'id': 'ia-3', 'state_id': S, 'license_id': L, 'number': 'IA-2026-003', 'title': 'Extraction room sanitation and solvent controls', 'audit_type': 'Sanitation Audit', 'dept': 'Production', 'planned_date': '2026-11-12', 'audit_date': None,
   'auditor_name': 'Marcus Lee', 'auditor_qualification': 'CSQ internal auditor course 2026', 'independent': False, 'scope': 'Extraction room cleaning, solvent storage and logs.', 'clauses': [], 'recommendations': '', 'conclusion': '',
   'shared_with': '', 'shared_on': None, 'status': 'planned', 'next_audit_date': None, 'attachments': [], 'cancel_reason': '', 'closed_by': '', 'closed_at': None, 'created_by': ME_NAME, 'created_at': ts('2026-10-14')},
  {'id': 'ia-2', 'state_id': S, 'license_id': L, 'number': 'IA-2026-002', 'title': 'CSQ Module 2A cGMP audit - Q3 2026', 'audit_type': 'CSQ internal audit', 'dept': 'Production', 'planned_date': '2026-09-22', 'audit_date': '2026-09-24',
   'auditor_name': ME_NAME, 'auditor_qualification': 'CSQ internal auditor course 2026; PCQI', 'independent': True, 'scope': 'Production floor, storage, sanitation, training and labeling.', 'clauses': m2,
   'recommendations': 'Add Vault 1 to the daily temperature alarm check.', 'conclusion': 'cGMP controls mostly effective; 2 nonconformities to correct.', 'shared_with': '', 'shared_on': None, 'status': 'completed',
   'next_audit_date': '2027-09-24', 'attachments': [], 'cancel_reason': '', 'closed_by': '', 'closed_at': None, 'created_by': ME_NAME, 'created_at': ts('2026-09-15')},
  {'id': 'ia-1', 'state_id': S, 'license_id': L, 'number': 'IA-2026-001', 'title': 'CSQ Module 1 audit - Q2 2026', 'audit_type': 'CSQ internal audit', 'dept': 'Compliance', 'planned_date': '2026-06-15', 'audit_date': '2026-06-18',
   'auditor_name': 'Chris Novak', 'auditor_qualification': 'CSQ internal auditor course 2025', 'independent': True, 'scope': 'Management system, documents, CAPA, complaints, recall, defense.', 'clauses': m1,
   'recommendations': 'Update the crisis plan contact list each quarter.', 'conclusion': 'Module 1 conforming.', 'shared_with': 'Managers meeting', 'shared_on': '2026-06-25', 'status': 'closed', 'next_audit_date': '2027-06-18',
   'attachments': [], 'cancel_reason': '', 'closed_by': ME_NAME, 'closed_at': ts('2026-07-02'), 'created_by': ME_NAME, 'created_at': ts('2026-06-01')}]
def fnd(i, aid, clause, sev, desc, ca, owner, due, status, **k):
    r = {'id': 'fnd-%d' % i, 'state_id': S, 'license_id': L, 'audit_id': aid, 'clause': clause, 'severity': sev, 'description': desc, 'corrective_action': ca, 'owner_name': owner, 'due_date': due,
         'deviation_id': None, 'deviation_number': '', 'status': status, 'verification': '', 'closed_by': '', 'closed_at': None, 'created_by': ME_NAME, 'created_at': ts('2026-09-24', '15:%02d' % i), 'updated_at': ts('2026-09-24')}
    r.update(k); return r
T['hx_audit_findings'] = [
  fnd(1, 'ia-1', '1.11', 'observation', 'Crisis plan contact list last updated Oct 2025.', 'Update the contact list.', 'Chris Novak', '2026-07-15', 'closed', verification='Updated list posted and filed Jun 30.', closed_by=ME_NAME, closed_at=ts('2026-06-30')),
  fnd(2, 'ia-2', '2A.9.3', 'major', 'Vault 1 temperature logs show 3 excursions in September with no deviation raised.', 'Raise deviations for excursions; add an alarm on Vault 1.', 'Chris Novak', '2026-10-24', 'open', deviation_id='dev-7', deviation_number='DEV-2026-007'),
  fnd(3, 'ia-2', '2A.13.7', 'minor', 'No paper towels at the packaging room handwash sink during the audit.', 'Add paper towel refill to the daily sanitation checklist.', 'Ana Morales', '2026-10-01', 'closed', verification='Checked sink on 5 random days in Oct: stocked every time.', closed_by=ME_NAME, closed_at=ts('2026-10-09'))]

# ---------------- SOPs ----------------
def sig_png(seed):
    im = Image.new('RGBA', (320, 90), (255, 255, 255, 0)); dr = ImageDraw.Draw(im)
    pts = [(14 + i * 18, 52 + ((i * 37 + seed * 11) % 30) - 15) for i in range(17)]
    dr.line(pts, fill=(20, 20, 60, 255), width=3, joint='curve'); dr.line([(30, 70), (260, 64)], fill=(20, 20, 60, 255), width=2)
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def sop(id, num, title, folder, cat, ver, status, desc, steps, **k):
    r = {'id': id, 'state_id': S, 'license_id': L, 'license_ids': [L], 'sop_number': num, 'title': title, 'folder': folder, 'previous_folder': '', 'category': cat, 'description': desc,
         'steps': [{'id': 's%d' % i, 'text': t} for i, t in enumerate(steps)], 'generated_content': None, 'regulatory_references': [], 'attachments': [], 'version': ver, 'status': status,
         'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'effective_date': '2026-09-02', 'next_review': '2027-09-02', 'approved_by': ME_NAME, 'approved_at': ts('2026-09-02'),
         'revision_note': '', 'revised_by': '', 'created_by': ME_NAME, 'created_by_id': ADMIN, 'created_at': ts('2026-03-10'), 'updated_by': ME_NAME, 'updated_at': ts('2026-09-02')}
    r.update(k); return r
PRE_ROLL_GEN = {'sop_number': 'SOP-PRD-002', 'title': 'Pre-Roll Infusion', 'revision': '1.0', 'department': 'Production - Pre-Roll',
  'purpose': 'Infuse pre-rolls with distillate and kief consistently and safely, so each unit meets its labeled potency and weight.', 'scope': 'All infused pre-roll production in the pre-roll room at Black Fox.',
  'regulatory_references': ['19 CSR 100-1.120 Packaging and labeling', '19 CSR 100-1.130 Inventory control (METRC)', '19 CSR 100-1.140 Testing'],
  'responsibilities': [{'role': 'Production Manager', 'responsibility': 'Approves the infusion plan and reviews batch records.'}, {'role': 'Production Tech', 'responsibility': 'Performs infusion and records each step.'}],
  'required_materials': ['Nitrile gloves', 'Hair net', 'Calibrated scale (0.01 g)', 'Distillate syringe', 'Kief'],
  'steps': [{'step_number': 1, 'title': 'Line clearance', 'instruction': 'Complete the line clearance and confirm the bench and tools are clean.', 'critical': False},
            {'step_number': 2, 'title': 'Verify materials', 'instruction': 'Check distillate and kief lots are accepted and match the batch record.', 'regulatory_note': 'Record lot numbers in METRC', 'critical': True},
            {'step_number': 3, 'title': 'Apply distillate', 'instruction': 'Apply 0.10 g of distillate per cone with the syringe; weigh every 10th unit.', 'critical': True},
            {'step_number': 4, 'title': 'Coat with kief', 'instruction': 'Roll the infused cone in kief and tap off the excess.', 'critical': False},
            {'step_number': 5, 'title': 'Final weight check', 'instruction': 'Weigh 10 units per tray; all must be 0.48-0.52 g.', 'critical': True},
            {'step_number': 6, 'title': 'Package and tag', 'instruction': 'Package 5 per box and apply the METRC package tag.', 'regulatory_note': '19 CSR 100-1.120', 'critical': False}],
  'quality_checks': ['Weight 0.48-0.52 g', 'Even kief coating', 'Label matches the batch'], 'documentation_required': ['Batch record', 'Line clearance record', 'METRC package report'],
  'deviation_procedure': 'Stop the line and report the deviation in Hendrix QMS before continuing.', 'training_requirements': 'Read and sign this SOP; cGMP training current.',
  'revision_history': [{'revision': '1.0', 'date': '2026-08-20', 'description': 'Initial release', 'approved_by': ME_NAME}]}
T['hx_sops'] = [
  sop('sop-cart', 'SOP-PRD-001', 'Cart Filling and Capping', 'Production', 'Production — Cart Department', '1.2', 'published', 'Fill and cap 1 g vape cartridges to weight with no leaks or mix-ups.',
      ['Complete line clearance; only one product and lot on the bench.', 'Warm distillate to 55 °C in the filling machine.', 'Fill each cart to 1.00 g (0.98-1.03 g); weigh every 20th cart.',
       'Press caps with the capping press; check press pressure at start of shift.', 'Second person checks the label against the batch record.', 'Record counts and rejects on the batch record.'],
      effective_date='2026-10-14', next_review='2027-10-14', approved_at=ts('2026-10-14'), revision_note='Added capping press pressure check (CMP-2026-002).', revised_by=ME_NAME),
  sop('sop-cmp1', 'SOP-CMP-001', 'Deviation and CAPA Procedure', 'Compliance', 'Compliance — METRC', '1.0', 'published', 'How to report, investigate and close deviations and CAPAs in Hendrix QMS.',
      ['Stop and make the product safe.', 'Report the deviation in Hendrix QMS the same shift.', 'QA decides if a root cause analysis is needed.', 'Open a CAPA for major and critical deviations.', 'Verify the CAPA is effective before closing.'],
      effective_date='2026-04-01', next_review='2027-04-01', approved_at=ts('2026-04-01')),
  sop('sop-gum', 'SOP-PRD-003', 'Gummy Depositing and Curing', 'Production', 'Production — Gummy Department', '1.0', 'published', 'Deposit infused gummy mixture and cure it under controlled humidity.',
      ['Verify the infused mixture potency on the batch record.', 'Deposit into molds at 80-85 °C.', 'Cure 24 h at 18-22 °C and below 55% RH.', 'Sugar-coat and package.'],
      target_mode='roles', target_role_ids=['r-pm', 'r-pt'], effective_date='2026-06-10', next_review='2027-06-10', approved_at=ts('2026-06-10')),
  sop('sop-pre', 'SOP-PRD-002', 'Pre-Roll Infusion', 'Production', 'Production — Pre-Roll Department', '1.0', 'published', PRE_ROLL_GEN['purpose'], [], generated_content=PRE_ROLL_GEN,
      regulatory_references=PRE_ROLL_GEN['regulatory_references'], target_mode='roles', target_role_ids=['r-pm', 'r-pt'], effective_date='2026-08-20', next_review='2027-08-20', approved_at=ts('2026-08-20')),
  sop('sop-san', 'SOP-GEN-001', 'Sanitation of Production Rooms', 'General', 'Facility — Sanitation & Cleaning', '2.0', 'published', 'Daily and weekly cleaning and sanitizing of production rooms.',
      ['Remove product and packaging from the room.', 'Dry clean, then wash with detergent.', 'Sanitize with 200 ppm quat; check with a test strip.', 'Record the clean in the Sanitation log.'],
      effective_date='2025-10-01', next_review='2026-10-01', approved_at=ts('2025-10-01')),
  sop('sop-vis', 'SOP-SEC-001', 'Visitor Access and Escort', 'Security', 'Facility — Security', '1.0', 'published', 'Sign in, badge and escort every visitor and contractor.',
      ['Check ID and sign the visitor in on the kiosk.', 'Issue a visitor badge.', 'Escort the visitor at all times in restricted areas.', 'Sign the visitor out and collect the badge.'],
      effective_date='2026-02-15', next_review='2027-02-15', approved_at=ts('2026-02-15')),
  sop('sop-metrc', 'SOP-CMP-002', 'METRC Package Tagging', 'Compliance', 'Compliance — METRC', '1.0', 'draft', 'Create packages and apply METRC tags at packaging.',
      ['Create the package in METRC from the production batch.', 'Print and apply the tag to the case.', 'Scan to confirm.'], approved_by='', approved_at=None, effective_date=None, next_review=None, created_by='Marcus Lee')]
T['hx_sop_versions'] = [
  {'id': 'sv-2', 'sop_id': 'sop-cart', 'state_id': S, 'license_id': L, 'version': '1.1', 'snapshot': {**T['hx_sops'][0], 'version': '1.1', 'approved_at': ts('2026-05-02')}, 'revision_note': 'Added capping press pressure check (CMP-2026-002).', 'superseded_by': ME_NAME, 'superseded_at': ts('2026-10-14')},
  {'id': 'sv-1', 'sop_id': 'sop-cart', 'state_id': S, 'license_id': L, 'version': '1.0', 'snapshot': {**T['hx_sops'][0], 'version': '1.0', 'approved_at': ts('2026-03-10')}, 'revision_note': 'Fill weight range changed to 0.98-1.03 g.', 'superseded_by': ME_NAME, 'superseded_at': ts('2026-05-02')}]
ACKS = []
def ack(sid, uid, day, i):
    s = next(x for x in T['hx_sops'] if x['id'] == sid)
    role = next(r['name'] for r in T['hx_roles'] if r['id'] in next(p for p in ROSTER if p['id'] == uid)['role_ids'])
    ACKS.append({'id': 'ack-%d' % len(ACKS), 'sop_id': sid, 'state_id': S, 'license_id': L, 'version': s['version'], 'user_id': uid, 'name': NAME[uid], 'role_names': role, 'signature': sig_png(i), 'at': ts(day, '%02d:%02d' % (8 + i % 8, 10 + i))})
for i, u in enumerate(['u-marcus', 'u-jordan', 'u-tess', 'u-priya']): ack('sop-cart', u, '2026-10-%02d' % (15 + i), i)
for i, u in enumerate([ADMIN, 'u-marcus', 'u-priya', 'u-jordan', 'u-tess', 'u-ana']): ack('sop-cmp1', u, '2026-04-%02d' % (2 + i), i)
for i, u in enumerate(['u-marcus', 'u-jordan', 'u-tess']): ack('sop-gum', u, '2026-06-%02d' % (11 + i), i)
for i, u in enumerate(['u-marcus', 'u-jordan']): ack('sop-pre', u, '2026-08-%02d' % (21 + i), i)
for i, u in enumerate([ADMIN, 'u-marcus', 'u-ana', 'u-priya', 'u-jordan']): ack('sop-san', u, '2025-10-%02d' % (2 + i), i)
for i, u in enumerate([ADMIN, 'u-marcus', 'u-jordan', 'u-tess', 'u-ana', 'u-priya']): ack('sop-vis', u, '2026-02-%02d' % (16 + i), i)
T['hx_sop_acks'] = ACKS
AI_META = {'sop_number': 'SOP-PRD-004', 'title': 'Terpene Blending for Vape Formulations', 'revision': '1.0', 'department': 'Production - Cart Department',
  'purpose': 'Blend inhalation-grade terpenes into distillate at the formulated ratio so every vape batch tastes the same and stays within its potency target.',
  'scope': 'All terpene blending for 0.5 g and 1 g cartridges in the cart room.', 'regulatory_references': ['19 CSR 100-1.120 Packaging and labeling', '19 CSR 100-1.130 Inventory control', 'CSQ 3C.2.5 Inhalable ingredients'],
  'responsibilities': [{'role': 'Production Manager', 'responsibility': 'Approves the formulation and blend ratio.'}, {'role': 'Production Tech', 'responsibility': 'Weighs, blends and records each batch.'}],
  'required_materials': ['Nitrile gloves', 'Safety glasses', 'Calibrated scale (0.01 g)', 'Glass beaker', 'Hot plate stirrer'], 'deviation_procedure': 'Stop and report in Hendrix QMS; hold the blend.', 'training_requirements': 'Read and sign; cGMP and chemical safety current.'}
AI_STEPS = {'steps': [{'step_number': 1, 'title': 'Check the formulation', 'instruction': 'Confirm the SKU formulation and terpene profile on the batch record.', 'critical': False},
  {'step_number': 2, 'title': 'Verify terpene lot', 'instruction': 'Use only accepted terpene lots with a COA showing they are fit for inhalation.', 'regulatory_note': 'CSQ 3C.2.5', 'critical': True},
  {'step_number': 3, 'title': 'Weigh distillate', 'instruction': 'Tare the beaker and weigh the distillate to 0.01 g.', 'critical': False},
  {'step_number': 4, 'title': 'Add terpenes', 'instruction': 'Add terpenes at the formulated percentage (typically 8-10%); record the actual weight.', 'critical': True},
  {'step_number': 5, 'title': 'Mix', 'instruction': 'Stir at 50 °C for 10 minutes until uniform.', 'critical': False},
  {'step_number': 6, 'title': 'Label and hold', 'instruction': 'Label the blend with SKU, lot and date; hold until filling.', 'critical': False}],
  'quality_checks': ['Terpene % within 0.5% of target', 'Blend clear and uniform', 'Lot numbers recorded'], 'documentation_required': ['Batch record', 'Terpene COA', 'Scale calibration log']}

# ---------------- request handler ----------------
_h = handle
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def jerr(route, m): return jr(route, {'message': m}, 400)
def nowiso(): return dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')
def rid_of(u): return urllib.parse.unquote(u.split('id=eq.')[1].split('&')[0]) if 'id=eq.' in u else None
def nxt(tbl, pre): return '%s-2026-%03d' % (pre, sum(1 for x in T[tbl] if x.get('number', '').startswith(pre + '-')) + 1)
AICALLS = []
def course(prefix): return next(c for c in T['hx_training_courses'] if c['name'].startswith(prefix))
def handle(route, request):
    u = request.url; m = request.method
    if '/storage/v1/' in u: return _h(route, request)
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AICALLS.append(b)
        if b.get('module') == 'sops':
            p = b['messages'][0]['content']; p = p if isinstance(p, str) else p[-1]['text']
            return jr(route, {'content': [{'type': 'text', 'text': json.dumps(AI_META if 'Respond with ONLY this JSON (no markdown, be concise)' in p else AI_STEPS)}]})
        return jr(route, {'content': [{'type': 'text', 'text': '{}'}]})
    if '/rest/v1/rpc/hx_qms_people' in u: return jr(route, [{'id': p['id'], 'name': p['name']} for p in ROSTER] + [{'id': 'u-chris', 'name': 'Chris Novak'}])
    if '/rest/v1/rpc/hx_sop_roster' in u or '/rest/v1/rpc/hx_training_roster' in u: return jr(route, ROSTER)
    if '/rest/v1/rpc/hx_training_sop_acks' in u: return jr(route, [{'sop_id': a['sop_id'], 'version': a['version'], 'user_id': a['user_id'], 'at': a['at']} for a in T['hx_sop_acks']])
    if '/rest/v1/rpc/hx_course_submit' in u:
        b = json.loads(request.post_data); c = next(x for x in T['hx_training_courses'] if x['id'] == b['p_course'])
        k = next(x for x in T['hx_training_keys'] if x['course_id'] == c['id']); tot = len(k['answers'])
        ok = sum(1 for i in range(tot) if b['p_answers'][i] == k['answers'][i]); sc = round(ok * 100 / tot); ps = sc >= c['pass_mark']
        wrong = [{'q': i, 'explain': k['explain'][i]} for i in range(tot) if b['p_answers'][i] != k['answers'][i]]
        rec = None
        if ps:
            rec = 'trr-%d' % len(T['hx_training_records'])
            T['hx_training_records'].append({'id': rec, 'state_id': S, 'license_id': L, 'course_id': c['id'], 'user_id': ADMIN, 'person_name': ME_NAME, 'completed_on': TODAY.isoformat(),
                'expires_on': (TODAY + dt.timedelta(days=365)).isoformat(), 'trainer_name': 'Hendrix online course', 'trainer_qualification': 'Course content version %d approved by %s' % (c['content_version'], c['content_by']),
                'method': 'Online course', 'language': 'English', 'assessment': 'Passed', 'score': '%d/%d (%d%%)' % (ok, tot, sc), 'files': [], 'notes': '', 'voided': False, 'created_at': nowiso()})
        T['hx_training_attempts'].append({'id': 'att-%d' % len(T['hx_training_attempts']), 'state_id': S, 'license_id': L, 'course_id': c['id'], 'user_id': ADMIN, 'person_name': ME_NAME, 'content_version': c['content_version'],
            'finished_at': nowiso(), 'minutes': 18, 'answers': b['p_answers'], 'correct': ok, 'total': tot, 'score': sc, 'passed': ps, 'record_id': rec})
        return jr(route, {'correct': ok, 'total': tot, 'score': sc, 'pass_mark': c['pass_mark'], 'passed': ps, 'record_id': rec, 'wrong': wrong})
    tbl = urllib.parse.urlparse(u).path.split('/')[-1]
    if m == 'GET': return _h(route, request)
    b = json.loads(request.post_data) if request.post_data else {}
    rid = rid_of(u)
    if tbl == 'hx_training_keys' and m in ('POST', 'PATCH'):
        if m == 'POST': T['hx_training_keys'].append(dict(b)); return jr(route, [b], 201)
        cid = urllib.parse.unquote(u.split('course_id=eq.')[1].split('&')[0]); k = next(x for x in T['hx_training_keys'] if x['course_id'] == cid); k.update(b); return jr(route, [k])
    if tbl == 'hx_training_courses' and m == 'POST':
        rows = b if isinstance(b, list) else [b]
        for r in rows:
            r.setdefault('license_ids', [r['license_id']]); r.setdefault('active', True); r.setdefault('role_ids', []); r.setdefault('sop_id', None)
            r.update({'online': False, 'lessons': [], 'quiz': [], 'pass_mark': 80, 'content_status': 'none', 'content_version': 0, 'content_source': '', 'content_by': '', 'minutes': 15}); T['hx_training_courses'].append(r)
        return jr(route, rows, 201)
    if tbl == 'hx_training_courses' and m == 'PATCH':
        c = next(x for x in T['hx_training_courses'] if x['id'] == rid); old = dict(c); c.update(b)
        if c.get('content_status') == 'published' and any(old.get(k) != c.get(k) for k in ('lessons', 'quiz', 'content_status', 'pass_mark', 'content_source', 'minutes')):
            c['content_version'] = old.get('content_version', 0) + 1; c['content_by'] = ME_NAME; c['assessment_required'] = True
        return jr(route, [c])
    if tbl in ('hx_deviations', 'hx_capas') and m in ('POST', 'PATCH'):
        if m == 'POST':
            r = dict(b); r.update({'number': nxt(tbl, 'DEV' if tbl == 'hx_deviations' else 'CAPA'), 'created_at': nowiso(), 'updated_at': nowiso(), 'reported_by': ME_NAME, 'created_by': ME_NAME, 'reported_by_id': ADMIN, 'closed_by': '', 'closed_at': None,
                                 'cancel_reason': '', 'effectiveness_rating': '', 'verification_evidence': '', 'verified_by': '', 'close_note': '', 'rca_decided_by': ME_NAME if b.get('rca_required') is not None else ''})
            T[tbl].insert(0, r); return jr(route, [r], 201)
        r = next(x for x in T[tbl] if x['id'] == rid); r.update(b); r['updated_at'] = nowiso(); return jr(route, [r])
    if tbl in ('hx_complaints', 'hx_audits', 'hx_audit_findings', 'hx_sops', 'hx_sop_acks', 'hx_training_records') and m in ('POST', 'PATCH'):
        if m == 'POST':
            rows = b if isinstance(b, list) else [b]
            for r in rows:
                r.setdefault('created_at', nowiso())
                if tbl == 'hx_complaints': r['number'] = nxt(tbl, 'FBK' if r['type'] == 'feedback' else 'CMP')
                if tbl == 'hx_audits': r['number'] = nxt(tbl, 'IA')
                T[tbl].insert(0, r)
            return jr(route, rows, 201)
        r = next(x for x in T[tbl] if x['id'] == rid); r.update(b); return jr(route, [r])
    return _h(route, request)

def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def shot(pg, name):
    pg.evaluate('window.scrollTo(0,0); document.querySelectorAll("*").forEach(function(e){if(e.scrollTop&&!e.closest(".md"))e.scrollTop=0;})'); pg.wait_for_timeout(350); pg.screenshot(path=SHOTS + 'qual_' + name + '.png'); print('shot', name)
def mshot(pg, name, loc=None):
    pg.evaluate('document.activeElement && document.activeElement.blur()'); pg.wait_for_timeout(350); (loc or pg.locator('.md').last).screenshot(path=SHOTS + 'qual_' + name + '.png'); print('shot', name)
def tall(pg, h=1700): pg.set_viewport_size({'width': 1440, 'height': h}); pg.wait_for_timeout(200)
def norm(pg): pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(200)
def nav(pg, name): pg.locator('.nav').get_by_role('button', name=name, exact=True).click() if pg.locator('.nav').count() else pg.get_by_role('button', name=name, exact=True).click()
def closeall(pg):
    for _ in range(4):
        if not pg.locator('.mo').count(): return
        pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); pg.wait_for_timeout(150)
def sign(pg):
    cv = pg.locator('.md canvas').last.bounding_box()
    pg.mouse.move(cv['x'] + 30, cv['y'] + 40); pg.mouse.down(); pg.mouse.move(cv['x'] + 200, cv['y'] + 70, steps=8); pg.mouse.up()

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell')
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1.5, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda dl: dl.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Deviations & CAPA')

    # ===================== QMS =====================
    nav(pg, 'QMS'); pg.wait_for_selector('text=Needs action'); shot(pg, 'qms_dashboard')
    pg.get_by_role('button', name='+ Report deviation').click(); md = pg.locator('.md')
    field(md, 'Deviation title').fill('Distillate drum seal broken on receipt'); field(md, 'Department').select_option('Warehouse'); field(md, 'Category').select_option('Supplier / material')
    field(md, 'Priority').select_option('major'); field(md, 'Date it happened').fill('2026-10-24'); field(md, 'Product affected').fill('Distillate (bulk), 5 kg drum')
    field(md, 'Lot / batch number').fill('D-2610-07'); field(md, 'What happened?').fill('Tamper seal on drum 2 of 3 from Midwest Extracts was broken when it arrived. Drum weight matched the manifest.')
    field(md, 'Correction / immediate action taken').fill('Drum put on hold at receiving and photographed; supplier notified.'); field(md, 'Owner (who resolves it)').fill('Ana Morales'); field(md, 'Due date').fill('2026-10-31')
    tall(pg); mshot(pg, 'qms_report_form'); norm(pg); md.get_by_role('button', name='Cancel').click()
    pg.locator('.tabs button', has_text='Deviations').click(); pg.locator('select').filter(has_text='Open + in progress').select_option('ALL'); pg.wait_for_timeout(200)
    pg.locator('.card', has_text='DEV-2026-006').first.click(); pg.wait_for_selector('.md'); tall(pg, 1300); mshot(pg, 'qms_deviation_detail'); norm(pg)
    pg.locator('.md').get_by_role('button', name='Close', exact=True).last.click()
    pg.locator('.tabs button', has_text='CAPAs').click(); pg.locator('.card', has_text='CAPA-2026-003').first.click(); pg.wait_for_selector('.md')
    pg.locator('.md').get_by_role('button', name='Verify effectiveness').click(); md = pg.locator('.md')
    field(md, 'Verification evidence').fill('4 of 4 gummy batches passed yeast and mold (GM-261007 to GM-261021). No humidity alarms Oct 3 - Nov 2.'); field(md, 'Effectiveness').select_option('effective')
    mshot(pg, 'qms_capa_verify'); md.get_by_role('button', name='Cancel').click(); closeall(pg)
    pg.locator('.tabs button', has_text='Trends').click(); pg.wait_for_selector('text=By category'); shot(pg, 'qms_trends')

    # ===================== Complaints =====================
    nav(pg, 'Complaints'); pg.wait_for_selector('text=Repeat complaints'); shot(pg, 'complaints_list')
    pg.get_by_role('button', name='+ Log complaint').click(); md = pg.locator('.md')
    field(md, 'Type').select_option('dispensary'); field(md, 'Priority').select_option('major'); field(md, 'Received on').fill('2026-10-24')
    field(md, 'Title').fill('Pre-roll boxes missing child-resistant seal'); field(md, 'Received by').select_option('Email'); field(md, 'Complainant').fill('Dev Patel (store manager)'); field(md, 'Contact').fill('dev@midtowncannabis.test')
    field(md, 'Customer (dispensary)').fill('Midtown Cannabis Co.'); field(md, 'Category').select_option('Hardware / packaging failure'); field(md, 'Batch').select_option('b-pr')
    field(md, 'Package tag').fill('1A4000000000000000005120'); field(md, 'Description').fill('4 of 30 boxes in the case arrived with the child-resistant seal not engaged.')
    tall(pg, 1300); mshot(pg, 'complaints_form'); norm(pg); md.get_by_role('button', name='Cancel').click()
    pg.locator('select').filter(has=pg.locator('option', has_text='Every status')).first.select_option('ALL'); pg.wait_for_timeout(200)
    pg.locator('.card', has_text='CMP-2026-004').first.click(); pg.wait_for_selector('.md'); tall(pg, 1500); mshot(pg, 'complaints_detail'); norm(pg)
    pg.locator('.md').get_by_role('button', name='Close window').click()
    pg.locator('.tabs button', has_text='Trends').click(); pg.wait_for_selector('text=By lot / batch'); shot(pg, 'complaints_trends')

    # ===================== Internal Audits =====================
    nav(pg, 'Internal Audits'); pg.wait_for_selector('text=IA-2026-002'); shot(pg, 'intaudits_list')
    pg.get_by_role('button', name='+ Plan audit').click(); md = pg.locator('.md')
    field(md, 'Audit title').fill('CSQ Module 2A audit - Q4 2026 (storage and receiving)'); field(md, 'Audit type').select_option('CSQ internal audit'); field(md, 'Department').select_option('Warehouse')
    field(md, 'Planned date').fill('2026-11-18'); field(md, 'Lead auditor').fill('Chris Novak'); field(md, 'Auditor qualification').fill('CSQ internal auditor course 2025')
    md.locator('label.ck', has_text='does not audit their own work').locator('input').check(); field(md, 'Audit scope').fill('Warehouse, vaults, receiving and hold area.')
    for c in ['2A.9.1', '2A.9.3', '2A.9.4', '2A.10.1', '2A.10.2', '2A.10.4']:
        md.locator('select').filter(has_text='+ One clause...').select_option(c); pg.wait_for_timeout(80)
    rows = md.locator('div.grid', has=pg.locator('input[placeholder="Evidence seen"]'))
    rows.nth(0).locator('select').select_option('Conforming'); rows.nth(0).locator('input').fill('Racks off the floor, FIFO labels')
    rows.nth(1).locator('select').select_option('Nonconforming'); rows.nth(1).locator('input').fill('Vault 1 alarm not tested this month')
    field(md, 'Next audit date').fill('2027-11-18')
    tall(pg, 1500); mshot(pg, 'intaudits_form'); norm(pg); md.get_by_role('button', name='Cancel').click()
    pg.locator('.card', has_text='IA-2026-002').first.click(); pg.wait_for_selector('.md'); tall(pg, 1500); mshot(pg, 'intaudits_detail'); norm(pg)
    pg.locator('.md').get_by_role('button', name='Close window').click()
    pg.locator('.tabs button', has_text='Annual program').click(); pg.wait_for_selector('text=Annual audit program'); shot(pg, 'intaudits_program')

    # ===================== SOPs =====================
    nav(pg, 'SOPs'); pg.wait_for_selector('.card >> text=Cart Filling and Capping'); shot(pg, 'sops_list')
    pg.get_by_role('button', name='+ Manual SOP').click(); md = pg.locator('.md')
    field(md, 'Title').fill('Distillate Receiving and Storage'); field(md, 'Folder').select_option('Production'); field(md, 'Category').select_option('Distribution — Receiving')
    field(md, 'Folder').select_option('Production'); md.get_by_role('button', name='Suggest').click()
    field(md, 'Description / purpose').fill('Receive, inspect and store bulk distillate so only accepted lots reach production.')
    md.locator('textarea[placeholder="Step 1..."]').fill('Check the manifest, METRC tag and COA against the purchase order.'); md.get_by_role('button', name='+ Add step').click()
    md.locator('textarea[placeholder="Step 2..."]').fill('Inspect the drum seal; put any broken seal on hold and report a deviation.'); md.get_by_role('button', name='+ Add step').click()
    md.locator('textarea[placeholder="Step 3..."]').fill('Store accepted drums in Vault 2 at 60-75 °F.')
    md.get_by_role('button', name='By role').click(); md.locator('label.ck', has_text='Production Manager').locator('input').check(); md.locator('label.ck', has_text='Production Tech').locator('input').check()
    md.locator('input[type=file]').set_input_files({'name': 'receiving_flow.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 x'}); pg.wait_for_selector('.md >> text=receiving_flow.pdf')
    tall(pg, 1500); mshot(pg, 'sops_form'); norm(pg); md.get_by_role('button', name='Cancel').click()
    pg.get_by_role('button', name='🤖 AI Generate SOP').click(); md = pg.locator('.md')
    field(md, 'SOP title').fill('Terpene Blending for Vape Formulations'); field(md, 'Category / department').select_option('Production — Cart Department')
    field(md, 'Instructions for the AI (optional)').fill('Include the inhalation-grade check; keep to 6 steps.')
    md.get_by_role('button', name='Generate SOP with AI').click(); pg.wait_for_selector('.md >> text=Save as draft')
    tall(pg, 1700); mshot(pg, 'sops_ai_review'); norm(pg); pg.locator('.md').get_by_role('button', name='Back').click(); pg.locator('.md').get_by_role('button', name='Cancel').click()
    pg.locator('.card', has_text='Cart Filling and Capping').first.click(); pg.wait_for_selector('.md >> text=Signatures'); tall(pg, 1500); mshot(pg, 'sops_detail'); norm(pg)
    pg.locator('.md').get_by_role('button', name='Close', exact=True).click()
    pg.locator('.card', has_text='Pre-Roll Infusion').first.click(); pg.wait_for_selector('.md')
    with pg.expect_download() as di: pg.locator('.md').get_by_role('button', name='📄 Download PDF').click()
    di.value.save_as(SHOTS + 'qual_sop.pdf')
    subprocess.run(['pdftoppm', '-png', '-r', '110', '-f', '1', '-l', '1', '-singlefile', SHOTS + 'qual_sop.pdf', SHOTS + 'qual_sops_pdf'], check=True); print('shot sops_pdf')
    pg.locator('.md').get_by_role('button', name='Close', exact=True).click()

    # ===================== Training =====================
    nav(pg, 'Training'); pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses', timeout=20000)
    pg.wait_for_selector('.card >> text=Online courses ready'); pg.get_by_role('button', name='Publish all').click(); pg.wait_for_selector('.msg >> text=/Published \\d+ online course/')
    # SOP-linked read-and-sign course
    T['hx_training_courses'].append({'id': 'crs-cart', 'state_id': S, 'license_id': L, 'license_ids': [L], 'name': 'Cart filling (read and sign SOP-PRD-001)', 'topic': 'Job-specific', 'description': 'Met by signing the current version of SOP-PRD-001.',
        'required_mode': 'roles', 'role_ids': ['r-pt', 'r-pm'], 'min_people': 1, 'refresher_months': 0, 'assessment_required': False, 'sop_id': 'sop-cart', 'active': True, 'sort': 20, 'share_key': None,
        'online': False, 'lessons': [], 'quiz': [], 'pass_mark': 80, 'content_status': 'none', 'content_version': 0, 'content_source': '', 'content_by': '', 'minutes': 15})
    def rec(cpre, uid, day, trainer='Dana Brooks', qual='QA Manager, PCQI', method='Classroom', assess=None, score='', files=None):
        c = course(cpre); d0 = dt.date.fromisoformat(day); mo = c['refresher_months']
        exp = None
        if mo: mm = d0.month - 1 + mo; exp = dt.date(d0.year + mm // 12, mm % 12 + 1, min(d0.day, 28)).isoformat()
        a = assess or ('Passed' if c['assessment_required'] else 'Not required')
        T['hx_training_records'].append({'id': 'tr-%d' % len(T['hx_training_records']), 'state_id': S, 'license_id': L, 'course_id': c['id'], 'user_id': uid, 'person_name': NAME[uid], 'completed_on': day, 'expires_on': exp,
            'trainer_name': trainer, 'trainer_qualification': qual, 'method': method, 'language': 'English', 'assessment': a, 'score': score or ('9/10' if a == 'Passed' else ''), 'files': files or [], 'notes': '',
            'recorded_by': ME_NAME, 'voided': False, 'created_at': ts(day)})
    for uid, day in [(ADMIN, '2026-02-10'), ('u-marcus', '2025-11-05'), ('u-priya', '2025-08-01'), ('u-jordan', '2026-03-14'), ('u-ana', '2026-01-20')]: rec('Missouri regulatory', uid, day)
    for uid, day in [('u-marcus', '2026-04-11'), ('u-priya', '2026-05-02'), ('u-jordan', '2026-06-15'), ('u-tess', '2026-09-30')]: rec('Current Good', uid, day, files=[{'path': 'training/x.pdf', 'name': 'signin_sheet.pdf'}])
    for uid in [ADMIN, 'u-marcus', 'u-priya', 'u-ana', 'u-tess']: rec('Cannabis safety', uid, '2026-03-02' if uid != 'u-tess' else '2026-09-30')
    for uid in [ADMIN, 'u-marcus', 'u-priya', 'u-jordan', 'u-ana']: rec('Personnel hygiene', uid, '2026-09-03', trainer='Ana Morales', qual='Sanitation lead, 6 yrs')
    rec('Personnel hygiene', 'u-tess', '2025-10-15', trainer='Ana Morales', qual='Sanitation lead, 6 yrs')
    for uid in [ADMIN, 'u-marcus', 'u-priya', 'u-jordan', 'u-tess', 'u-ana']: rec('Product defense', uid, '2026-01-12', trainer='Chris Novak', qual='Security manager')
    for uid in [ADMIN, 'u-marcus', 'u-ana']: rec('Chemical safety', uid, '2026-02-20', method='On the job')
    rec('CSQ Certification', ADMIN, '2026-02-01', trainer='ASI / CSQ', qual='CSQ Program Overview course', method='External certification', files=[{'path': 'training/csq.pdf', 'name': 'CSQ_overview_certificate.pdf'}])
    rec('HACCP certification', ADMIN, '2025-06-12', trainer='International HACCP Alliance course', qual='IHA accredited lead instructor', method='External certification', files=[{'path': 'training/haccp.pdf', 'name': 'HACCP_certificate.pdf'}])
    rec('Extraction safety', 'u-priya', '2026-07-20', method='On the job', score='10/10')
    pg.reload(); pg.wait_for_selector('text=Deviations & CAPA'); nav(pg, 'Training'); pg.wait_for_selector('td >> text=Tess Whitaker'); pg.wait_for_timeout(600)
    shot(pg, 'training_matrix')
    pg.locator('.tabs button', has_text='Courses').click(); pg.wait_for_selector('text=Outside certification'); shot(pg, 'training_courses')
    pg.get_by_role('button', name='+ Record training').click(); md = pg.locator('.md')
    field(md, 'Course').select_option(label='Current Good Manufacturing Practices (cGMP)'); field(md, 'Date completed').fill('2026-10-23')
    md.locator('label.ck', has_text='Ana Morales').locator('input').check()
    field(md, 'Trainer').fill('Dana Brooks'); field(md, 'Trainer qualification').fill('QA Manager, 8 yrs; PCQI certified'); field(md, 'Method').select_option('Classroom')
    field(md, 'Assessment').select_option('Passed'); field(md, 'Score').fill('18/20'); field(md, 'Notes').fill('Make-up session for the September class.')
    md.locator('input[type=file]').set_input_files({'name': 'cgmp_signin_2026-10-23.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4'}); pg.wait_for_selector('.md >> text=cgmp_signin_2026-10-23.pdf')
    tall(pg, 1300); mshot(pg, 'training_record_form'); norm(pg); md.get_by_role('button', name='Cancel').click()
    pg.locator('.card', has_text='Current Good Manufacturing').get_by_role('button', name='Take course').click(); pg.wait_for_selector('.md >> text=Lesson 1 of')
    md = pg.locator('.md'); md.get_by_role('button', name='Next lesson').click(); md.get_by_role('button', name='Next lesson').click(); pg.wait_for_selector('.md >> text=Lesson 3 of')
    tall(pg, 1300); mshot(pg, 'training_lesson'); norm(pg)
    while md.get_by_role('button', name='Next lesson').count(): md.get_by_role('button', name='Next lesson').click()
    md.get_by_role('button', name='Go to the quiz').click()
    key = next(k for k in T['hx_training_keys'] if k['course_id'] == course('Current Good')['id'])['answers']
    ans = list(key); ans[3] = (ans[3] + 1) % 4
    for i, a in enumerate(ans):
        md.locator('.card', has=pg.locator('div', has_text=re.compile('^%d\\. ' % (i + 1)))).first.locator('input[type=radio]').nth(a).check()
    md.get_by_role('button', name='Submit answers').click(); pg.wait_for_selector('.md >> text=/\\d+ of \\d+ correct/')
    mshot(pg, 'training_quiz_result')
    b.close()
print('\nJS errors:', errors if errors else 'none')
