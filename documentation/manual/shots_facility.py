# Screenshots for the "facility" chapter (Facility Logs, Visitor Log, Equipment, Chemicals and SDS,
# Facility Tests, Line Clearance and Rework, Time Clock and Badges).
import re, datetime as dt, base64, io, math
exec(open('/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/mock_c.py').read())
from PIL import Image, ImageDraw
errors = []
SH = OUT + 'manual/shots/'
TODAY = '2026-10-23'
FIXED = dt.datetime(2026, 10, 23, 11, 42, 0, tzinfo=dt.timezone(dt.timedelta(hours=-5)))  # Missouri, CDT
def Z(day, hm):  # local CDT time -> UTC ISO
    h, m = map(int, hm.split(':')); d = dt.datetime.fromisoformat(day + 'T00:00:00-05:00') + dt.timedelta(hours=h, minutes=m)
    return d.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')
L = {'state_id': 'st-mo', 'license_id': 'lic-mo'}

# ---------- images: signatures and badge photos ----------
def sig_png(seed):
    im = Image.new('RGB', (600, 180), 'white'); d = ImageDraw.Draw(im); pts = []
    for i in range(60):
        x = 40 + i * 8; y = 95 + 35 * math.sin(i / (3.0 + seed)) * math.cos(i / 7.0 + seed)
        pts.append((x, y))
    d.line(pts, fill='#111', width=4)
    b = io.BytesIO(); im.save(b, 'PNG'); return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
def avatar(bg, skin, hair):
    S = 500; im = Image.new('RGB', (S, S), bg); d = ImageDraw.Draw(im)
    for y in range(S):  # soft gradient
        c = tuple(int(v * (0.75 + 0.35 * y / S)) for v in bg); d.line([(0, y), (S, y)], fill=tuple(min(255, x) for x in c))
    d.ellipse([90, 330, 410, 700], fill=(40, 40, 46))  # shoulders
    d.rectangle([215, 290, 285, 360], fill=skin)  # neck
    d.ellipse([150, 90, 350, 330], fill=skin)  # head
    d.chord([140, 70, 360, 260], 180, 360, fill=hair)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=85); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
SIG = sig_png(0.4)

# ---------- people ----------
PEOPLE = [('u-lee', 'Lee Park', 'lee@blackfoxmfg.com'), ('u-maria', 'Maria Gonzalez', 'maria@blackfoxmfg.com'), ('u-devon', 'Devon Brooks', 'devon@blackfoxmfg.com'),
          ('u-aisha', 'Aisha Khan', 'aisha@blackfoxmfg.com'), ('u-tom', 'Tom Becker', 'tom@blackfoxmfg.com')]
T['hx_profiles'][0].update({'name': 'Sam Salari'})
for pid, nm, em in PEOPLE:
    T['hx_profiles'].append({'id': pid, 'name': nm, 'email': em, 'role': 'member', 'approved': True, 'license_ids': ['lic-mo'], 'role_ids': [], 'perms': {}, 'created_at': '2026-01-01'})
BADGES = {'u-lee': {'code': 'K7Q2M9X4B1TZ', 'badge_no': '4127', 'title': 'Extraction Technician', 'photo': avatar((70, 90, 120), (224, 186, 150), (40, 28, 20))},
          'u-maria': {'code': 'R3D8W1N6P0LA', 'badge_no': '4133', 'title': 'QA Lead', 'photo': avatar((96, 70, 110), (196, 150, 112), (25, 18, 14))},
          'u-devon': {'code': 'H5J0C2V7S9EM', 'badge_no': '4141', 'title': 'Packaging Technician', 'photo': avatar((60, 105, 90), (140, 98, 70), (20, 15, 12))},
          'u-aisha': {'code': 'F9L4T6Y3G8QD', 'badge_no': '4152', 'title': 'Sanitation Technician', 'photo': avatar((120, 90, 60), (170, 120, 90), (30, 22, 18))}}
for b in BADGES.values(): b.update({'zoom': 1, 'pos_x': 0, 'pos_y': 0})

# ---------- Facility Logs: lists ----------
def li(key, name, spec=None, i=0): return {**L, 'id': 'li-%s-%d' % (key.replace('.', '-'), i), 'list_key': key, 'name': name, 'spec': spec or {}, 'sort': i, 'active': True, 'created_at': '1'}
LISTS = []
for key, names in [('sanitation.areas', ['Production Floor', 'Packaging Room', 'Extraction Room', 'Restrooms', 'Break Room']),
                   ('sanitation.equip_san', ['Hand Wash Sinks', 'Mop Sink', 'Door Handles']), ('sanitation.equip_clean', ['Filling Nozzles', 'Weighing Pans', 'Utensils']),
                   ('sanitation.weekly', ['Warehouse', 'Vault']), ('sanitation.monthly', ['HVAC Returns', 'Ceiling Vents']),
                   ('scale_calibration.locations', ['Packaging Room', 'Extraction Room']),
                   ('pest.stations', ['BS-01', 'BS-02', 'BS-03', 'GT-01', 'GT-02'])]:
    for i, n in enumerate(names): LISTS.append(li(key, n, None, i))
for i, (n, s) in enumerate([('Storage Vault', {'min': 60, 'max': 75, 'hmin': 45, 'hmax': 62}), ('Packaging Room', {'min': 62, 'max': 78, 'hmin': 40, 'hmax': 60}),
                            ('Gummy Curing Room', {'min': 64, 'max': 72, 'hmin': 35, 'hmax': 50}), ('Walk-in Cooler', {'min': 34, 'max': 40})]):
    LISTS.append(li('temperature.rooms', n, s, i))
LISTS.append(li('scale_calibration.scales', 'SCALE-01', {'location': 'Packaging Room', 'make': 'Ohaus Scout', 'model': 'SKX2202', 'serial': '0083451', 'capacity': '2200 g x 0.01 g', 'ntep': '13-123', 'cert_date': '2025-11-10', 'cert_company': 'Midwest Scale Co', 'tol': 0.1}, 0))
LISTS.append(li('scale_calibration.scales', 'SCALE-02', {'location': 'Extraction Room', 'make': 'Ohaus Defender', 'model': 'D52', 'serial': '0091277', 'capacity': '60 kg x 5 g', 'cert_date': '2025-10-01', 'cert_company': 'Midwest Scale Co', 'tol': 5}, 1))
LISTS.append(li('equipment.equipment', 'Cartridge filler #1', {'serial': 'CF1-22871'}, 0))
LISTS.append(li('equipment.equipment', 'Gummy depositor', {'serial': 'GD-5501'}, 1))
T['hx_log_lists'] = LISTS
T['hx_rules'].append({'id': 'r3', 'state_id': 'st-mo', 'category': 'Facility', 'citation': '', 'title': 'Facility kept clean and sanitary', 'body': 'Keep cleaning records for every area.', 'created_at': '2'})

FL = []
def fl(i, typ, item, data, result, by, day, hm, src='app', item_id=None):
    FL.append({**L, 'id': 'fl-%s-%d' % (typ, i), 'log_type': typ, 'item_id': item_id, 'item': item, 'data': data, 'result': result, 'performed_by': by, 'source': src, 'created_at': Z(day, hm), 'voided': False, 'signature': SIG})
AREAS = ['Production Floor', 'Packaging Room', 'Extraction Room', 'Restrooms', 'Break Room']
def san(done, wk=None, verified=''):
    d = {'areas': {a: a in done for a in AREAS}, 'equip_san': {'Hand Wash Sinks': True, 'Mop Sink': True, 'Door Handles': True}, 'equip_clean': {'Filling Nozzles': True, 'Weighing Pans': True, 'Utensils': True}}
    if wk: d['weekly'] = {'Warehouse': True, 'Vault': True}
    return d
for i, (day, shift, by, extra, ver, res) in enumerate([
        ('2026-10-23', 'Day', 'Aisha Khan', {}, 'Maria Gonzalez', 'Verified'), ('2026-10-22', 'Evening', 'Tom Becker', {}, '', 'Logged'),
        ('2026-10-22', 'Day', 'Aisha Khan', {'weekly': 1}, 'Maria Gonzalez', 'Verified'), ('2026-10-21', 'Day', 'Aisha Khan', {}, 'Maria Gonzalez', 'Flag'),
        ('2026-10-20', 'Day', 'Devon Brooks', {}, 'Maria Gonzalez', 'Verified'), ('2026-10-19', 'Day', 'Aisha Khan', {}, '', 'Logged')]):
    done = AREAS if i != 1 else AREAS[:4]
    d = {'date': day, 'time': '16:30', 'shift': shift, 'cleaned_by': by, 'sanitizer_used': 'Quat sanitizer 200 ppm', 'concentration': '1:256 dilution', **san(done, extra.get('weekly'))}
    if ver: d.update({'verified_by': ver, 'verify_method': 'ATP swab' if i % 2 == 0 else 'Visual inspection', 'verify_result': 'Re-clean required' if res == 'Flag' else 'Acceptable'})
    fl(i, 'sanitation', shift, d, res, by, day, '16:35', 'kiosk' if i in (1, 5) else 'app')
for i, (day, room, t, h, res, by) in enumerate([('2026-10-23', 'Storage Vault', '68.4', '52', 'Pass', 'Devon Brooks'), ('2026-10-23', 'Packaging Room', '71.0', '48', 'Pass', 'Devon Brooks'),
                                                ('2026-10-22', 'Gummy Curing Room', '70.2', '53', 'Fail', 'Lee Park'), ('2026-10-22', 'Storage Vault', '67.9', '50', 'Pass', 'Tom Becker')]):
    fl(i, 'temperature', room, {'date': day, 'time': '08:05', 'shift': 'Day', 'recorded_by': by, 'location': room, 'temperature_f': t, 'humidity_pct': h, 'in_range': 'Yes — within range' if res == 'Pass' else 'No — out of range (action taken)',
        **({'corrective_action': 'Dehumidifier set to 45%, re-checked 53 -> 48 at 10:15'} if res == 'Fail' else {})}, res, by, day, '08:06', item_id='li-temperature-rooms-%d' % ['Storage Vault', 'Packaging Room', 'Gummy Curing Room', 'Walk-in Cooler'].index(room))
fl(0, 'equipment', 'Cartridge filler #1', {'date': '2026-08-10', 'equipment_name': 'Cartridge filler #1', 'equipment_id': 'CF1-22871', 'maintenance_type': 'Routine/Preventive', 'performed_by': 'Lee Park', 'description': 'Replaced nozzle O-rings, lubricated slides with H1 grease, test fill 50 carts', 'pass_fail': 'Pass — returned to service'}, 'OK', 'Lee Park', '2026-10-01', '09:00', item_id='li-equipment-equipment-0')
fl(1, 'equipment', 'Gummy depositor', {'date': '2026-09-10', 'equipment_name': 'Gummy depositor', 'equipment_id': 'GD-5501', 'maintenance_type': 'Routine/Preventive', 'performed_by': 'Lee Park', 'description': 'Cleaned hopper heaters, checked piston seals, calibrated deposit weight', 'parts_replaced': 'Piston seal kit PS-12', 'pass_fail': 'Pass — returned to service'}, 'OK', 'Lee Park', '2026-10-02', '09:00', item_id='li-equipment-equipment-1')
fl(2, 'equipment', 'Gummy depositor', {'date': '2026-10-15', 'equipment_name': 'Gummy depositor', 'equipment_id': 'GD-5501', 'maintenance_type': 'Corrective/Repair', 'performed_by': 'Lee Park', 'description': 'Hopper heater band cracked; clamped temporarily, part ordered', 'pass_fail': 'Conditional — monitor closely'}, 'Flag', 'Lee Park', '2026-10-15', '14:10', item_id='li-equipment-equipment-1')
T['hx_facility_log'] = FL

# ---------- Visitor Log ----------
T['hx_visitor_log'] = [
    {**L, 'id': 'vis1', 'visitor_name': 'Rachel Ortiz', 'company': 'Midwest Scale Co', 'purpose': 'Contractor / maintenance', 'host': 'Lee Park', 'vehicle': 'MO 7KD-492', 'time_in': Z('2026-10-23', '09:12'), 'time_out': None, 'source': 'kiosk', 'gmp_ack': True, 'ill': False, 'signature': SIG, 'voided': False},
    {**L, 'id': 'vis2', 'visitor_name': 'James Whitfield', 'company': 'Green Leaf Dispensary', 'purpose': 'Customer / buyer', 'host': 'Sam Salari', 'vehicle': '', 'time_in': Z('2026-10-22', '13:30'), 'time_out': Z('2026-10-22', '14:45'), 'source': 'kiosk', 'gmp_ack': True, 'ill': False, 'signature': SIG, 'voided': False},
    {**L, 'id': 'vis3', 'visitor_name': 'Priya Natarajan', 'company': 'Gateway Pest Solutions', 'purpose': 'Vendor / delivery', 'host': 'Maria Gonzalez', 'vehicle': 'MO 2HT-118', 'time_in': Z('2026-10-21', '08:05'), 'time_out': Z('2026-10-21', '09:20'), 'source': 'kiosk', 'gmp_ack': True, 'ill': False, 'signature': SIG, 'voided': False},
    {**L, 'id': 'vis4', 'visitor_name': 'Kevin Doyle', 'company': 'Show-Me Packaging', 'purpose': 'Vendor / delivery', 'host': 'Devon Brooks', 'vehicle': '', 'time_in': Z('2026-10-20', '10:40'), 'time_out': Z('2026-10-20', '11:05'), 'source': 'kiosk', 'gmp_ack': True, 'ill': True, 'signature': SIG, 'voided': False},
    {**L, 'id': 'vis5', 'visitor_name': 'Angela Brooks', 'company': 'Missouri DCR', 'purpose': 'Inspector / regulator', 'host': 'Sam Salari', 'vehicle': '', 'time_in': Z('2026-10-16', '09:00'), 'time_out': Z('2026-10-16', '15:30'), 'source': 'manual', 'gmp_ack': True, 'ill': False, 'signature': None, 'voided': False},
    {**L, 'id': 'vis6', 'visitor_name': 'Marcus Lee', 'company': 'Arch HVAC Services', 'purpose': 'Contractor / maintenance', 'host': 'Lee Park', 'vehicle': 'MO 9RB-330', 'time_in': Z('2026-10-14', '07:45'), 'time_out': Z('2026-10-14', '12:10'), 'source': 'kiosk', 'gmp_ack': True, 'ill': False, 'signature': SIG, 'voided': False}]

# ---------- Equipment ----------
def eqr(i, name, cat, loc, **k):
    base = {**L, 'id': 'eq%d' % i, 'number': 'EQ-%03d' % i, 'name': name, 'category': cat, 'location': loc, 'make': '', 'model': '', 'serial': '', 'asset_tag': '', 'product_contact': False, 'critical': False, 'status': 'in_service',
            'installed_on': None, 'controls_note': '', 'pm_interval_days': None, 'pm_tasks': '', 'cal_required': False, 'cal_interval_months': None, 'cal_method': '', 'cal_standard': '', 'cal_protection': '', 'cal_last': None, 'cal_due': None,
            'val_required': False, 'iq_on': None, 'oq_on': None, 'pq_on': None, 'reval_due': None, 'log_item_id': None, 'files': [], 'notes': '', 'retired_reason': None, 'created_by': 'Sam Salari', 'created_at': '2026-03-01T10:00:00Z'}
    base.update(k); return base
T['hx_equipment'] = [
    eqr(1, 'Cartridge filler #1', 'Production', 'Filling room', make='FillTech', model='CF-300', serial='CF1-22871', product_contact=True, critical=True, pm_interval_days=90, pm_tasks='Replace nozzle O-rings, lubricate slides with H1 grease, verify fill volume', log_item_id='li-equipment-equipment-0', installed_on='2025-06-01'),
    eqr(2, 'SCALE-01', 'Scale / balance', 'Packaging Room', make='Ohaus', model='Scout SKX2202', serial='0083451', critical=True, cal_required=True, cal_interval_months=12, cal_method='Manufacturer procedure, NIST HB 44', cal_standard='NIST-traceable class F weights', cal_protection='Sealed calibration switch', cal_last='2025-11-10', cal_due='2026-11-10'),
    eqr(3, 'SCALE-02', 'Scale / balance', 'Extraction Room', make='Ohaus', model='Defender D52', serial='0091277', cal_required=True, cal_interval_months=12, cal_standard='NIST-traceable class F weights', cal_last='2025-10-01', cal_due='2026-10-01'),
    eqr(4, 'Rotary evaporator', 'Extraction', 'Extraction Room', make='LabPro', model='RV-20', serial='RV20-1188', product_contact=True, critical=True, pm_interval_days=60, pm_tasks='Check vacuum seals, clean condenser, inspect glassware', val_required=True, iq_on='2026-02-02', oq_on='2026-02-09', pq_on='2026-03-15', reval_due='2027-03-15', installed_on='2026-02-01'),
    eqr(5, 'Gummy depositor', 'Production', 'Kitchen', make='CandyWorks', model='GD-1', serial='GD-5501', product_contact=True, critical=True, pm_interval_days=30, pm_tasks='Clean hopper heaters, check piston seals, verify deposit weight', log_item_id='li-equipment-equipment-1', installed_on='2025-09-15'),
    eqr(6, 'Closed-loop BHO system', 'Extraction', 'C1D1 room', make='ExtraSys', model='CL-10', serial='CL10-0042', product_contact=True, critical=True, status='out_of_service', val_required=True, pm_interval_days=30, pm_tasks='Leak test, replace O-rings, check pressure relief valve'),
    eqr(7, 'Walk-in cooler', 'Facility (HVAC, water, air)', 'Cold storage', make='PolarBox', model='WC-810', pm_interval_days=180, pm_tasks='Clean coils, check door gaskets, verify thermostat', installed_on='2026-05-01'),
    eqr(8, 'Hydrocarbon gas detector', 'Safety system (gas, fire)', 'C1D1 room', make='SafeAir', model='HC-4', serial='HC4-7781', critical=True, cal_required=True, cal_interval_months=6, cal_standard='Certified 25% LEL butane span gas', cal_last='2026-07-20', cal_due='2027-01-20')]
def ev(i, eid, kind, day, **k):
    b = {**L, 'id': 'eqe%d' % i, 'equipment_id': eid, 'kind': kind, 'done_on': day, 'done_by': '', 'details': '', 'result': '', 'stage': '', 'standard': '', 'next_due': None, 'fix_by': None, 'closed_on': None, 'closed_by': '', 'closure': '',
         'checks': {}, 'deviation_id': None, 'files': [], 'recorded_by': 'Lee Park', 'created_at': day + 'T15:00:00Z', 'voided': False, 'void_reason': None, 'voided_at': None}
    b.update(k); return b
CERT = [{'path': 'equipment/lic-mo/scale01_cert_2025.pdf', 'name': 'SCALE-01 certificate 2025-11-10.pdf'}]
T['hx_equipment_events'] = [
    ev(1, 'eq2', 'calibration', '2025-11-10', done_by='Midwest Scale Co', result='pass', standard='NIST-traceable class F weights', next_due='2026-11-10', files=CERT),
    ev(2, 'eq3', 'calibration', '2025-10-01', done_by='Midwest Scale Co', result='pass', standard='NIST-traceable class F weights', next_due='2026-10-01'),
    ev(3, 'eq4', 'validation', '2026-02-02', stage='IQ', result='pass', done_by='LabPro field service', details='Installed per drawing, utilities verified'),
    ev(4, 'eq4', 'validation', '2026-02-09', stage='OQ', result='pass', done_by='Lee Park', details='Vacuum, bath temperature and rotation within spec'),
    ev(5, 'eq4', 'validation', '2026-03-15', stage='PQ', result='pass', done_by='Lee Park', details='3 consecutive batches within spec'),
    ev(6, 'eq5', 'temporary_repair', '2026-10-15', done_by='Lee Park', details='Hose clamp on cracked hopper heater band', fix_by='2026-10-30'),
    ev(7, 'eq6', 'out_of_service', '2026-10-18', done_by='Lee Park', details='Pressure relief valve failed leak test; tagged out'),
    ev(8, 'eq8', 'calibration', '2026-07-20', done_by='SafeAir service', result='pass', standard='Certified 25% LEL butane span gas', next_due='2027-01-20')]

# ---------- Chemicals ----------
def chem(i, name, mfr, purpose, grade, status, area, **k):
    b = {**L, 'id': 'ch%d' % i, 'number': 'CHEM-%03d' % i, 'name': name, 'manufacturer': mfr, 'product_code': '', 'purpose': purpose, 'grade': grade, 'status': status,
         'sds_files': [{'path': 'chemicals/lic-mo/sds%d.pdf' % i, 'name': name.split(' ')[0] + '_SDS.pdf'}], 'sds_date': '2025-06-01', 'hazards': '', 'ppe': 'Nitrile gloves, safety glasses', 'first_aid': '', 'spill': '',
         'storage_area': area, 'restricted': False, 'disposal': '', 'epa_reg': '', 'supplier_id': None, 'notes': '', 'approved_by': 'Maria Gonzalez' if status == 'approved' else '', 'approved_at': '2026-04-02T15:00:00Z' if status == 'approved' else None,
         'removed_reason': None, 'created_by': 'Maria Gonzalez', 'created_at': '2026-04-01T10:00:00Z'}
    b.update(k); return b
T['hx_chemicals'] = [
    chem(1, 'Quat sanitizer 200', 'CleanCo', 'Food-contact sanitizer', 'food_contact_sanitizer', 'approved', 'Chemical cage', hazards='Corrosive, causes eye damage', ppe='Nitrile gloves, splash goggles', first_aid='Rinse eyes 15 min; call poison control', spill='Absorb, rinse area with water', disposal='Dilute to drain per SDS'),
    chem(2, 'Isopropyl alcohol 70%', 'LabChem', 'Sanitizer', 'non_food', 'approved', 'Chemical cage', hazards='Flammable liquid', ppe='Nitrile gloves', first_aid='Fresh air; rinse skin', spill='Absorb with pads, ventilate'),
    chem(3, 'H1 food-grade grease', 'LubeRite', 'Lubricant (food grade H1)', 'food_grade', 'approved', 'Maintenance shelf', ppe='Nitrile gloves', first_aid='Wash skin with soap'),
    chem(4, 'Ethanol 190 proof', 'Midwest Grain Solvents', 'Extraction solvent or gas', 'food_grade', 'approved', 'Flammables cabinet', restricted=True, hazards='Highly flammable liquid and vapor', ppe='Nitrile gloves, goggles, FR lab coat', first_aid='Fresh air; rinse eyes 15 min', spill='Eliminate ignition sources, absorb'),
    chem(5, 'n-Butane 99.5%', 'GasPro', 'Extraction solvent or gas', 'food_grade', 'approved', 'Gas cage (C1D1)', restricted=True, hazards='Extremely flammable gas under pressure', ppe='Cryo gloves, face shield', first_aid='Fresh air; warm frostbite gently'),
    chem(6, 'Neem oil concentrate', 'GreenGuard', 'Pesticide / crop protection', 'non_food', 'pending', 'Pesticide shelf'),
    chem(7, 'Heavy-duty degreaser', 'CleanCo', 'Cleaner', 'non_food', 'pending', 'Janitor closet', sds_files=[], ppe='')]

# ---------- Facility Tests ----------
def pt(i, name, kind, analytes, limits, every, lab, loc):
    return {**L, 'id': 'envp%d' % i, 'name': name, 'kind': kind, 'location': loc, 'source': 'City water' if 'water' in kind else '', 'analytes': analytes, 'limits': limits, 'frequency_days': every, 'lab_required': lab, 'active': True, 'sort': i, 'notes': '', 'created_at': '1'}
T['hx_env_points'] = [
    pt(0, 'Incoming water (point of use)', 'water', 'Total coliforms, E. coli, lead, nitrate', 'Meets EPA drinking water standards (potable)', 365, True, 'Kitchen hand sink'),
    pt(1, 'Production room air', 'air', 'Total yeast and mold, total aerobic count, particulates', 'Within the room specification; no growth trend', 365, True, 'Packaging Room'),
    pt(2, 'Backflow preventer', 'backflow', 'Annual test by a certified backflow tester', 'Passes the annual test', 365, False, 'Mechanical room'),
    pt(3, 'Food-contact surface swabs', 'surface', 'ATP after cleaning', 'ATP below 150 RLU', 30, False, 'Filling nozzles, depositor'),
    pt(4, 'Process gas (CO2 / nitrogen / hydrocarbon)', 'process_gas', 'Purity, moisture, oil; COA per delivery', 'At least 99.5% pure', 365, False, 'Gas cage (C1D1)'),
    pt(5, 'Process water and ice', 'process_water', 'Total coliforms, E. coli, purity', 'Potable; at least 99.5% pure', 365, True, 'RO system outlet')]
def et(i, p, day, res, lab, acc, vals, corr='', rep=''):
    return {**L, 'id': 'envt%d' % i, 'point_id': p, 'sampled_on': day, 'sampled_by': 'Maria Gonzalez', 'lab_name': lab, 'lab_accredited': acc, 'report_number': rep, 'result': res, 'values_text': vals, 'corrective': corr,
            'deviation_id': None, 'files': [{'path': 'envtests/lic-mo/r%d.pdf' % i, 'name': 'report_%s.pdf' % day}] if lab else [], 'recorded_by': 'Maria Gonzalez', 'created_at': day + 'T18:00:00Z', 'voided': False, 'void_reason': None, 'voided_at': None}
T['hx_env_tests'] = [
    et(1, 'envp0', '2026-02-12', 'pass', 'Pace Analytical', True, 'E. coli not detected; total coliforms <1 CFU/100 mL; lead 2 ppb', rep='PA-26-0412'),
    et(2, 'envp1', '2025-10-01', 'pass', 'Pace Analytical', True, 'Yeast and mold 40 CFU/m3; TAC 210 CFU/m3', rep='PA-25-2290'),
    et(3, 'envp2', '2026-05-20', 'pass', 'Gateway Backflow Testing', False, 'RP assembly passed, cert #BF-2219'),
    et(4, 'envp3', '2026-09-24', 'pass', '', False, 'ATP 42 / 38 / 55 RLU'),
    et(5, 'envp3', '2026-10-14', 'fail', '', False, 'ATP 450 RLU on filler nozzle 2', corr='Re-cleaned with quat sanitizer, re-swabbed 36 RLU; retrained on nozzle disassembly'),
    et(6, 'envp4', '2026-09-03', 'pass', 'GasPro (supplier COA)', False, 'n-Butane 99.7%, moisture <10 ppm')]

# ---------- Batches, line clearance, rework ----------
def bat(i, typ, num, sku, flav, day):
    return {**L, 'id': 'bt%d' % i, 'batch_type': typ, 'batch_number': num, 'sku_id': None, 'sku': sku, 'flavor_id': None, 'flavor': flav, 'status': 'In Progress', 'data': {'date': day}, 'attachments': [], 'performed_by': 'Lee Park', 'created_at': day + 'T13:00:00Z', 'updated_at': day + 'T13:00:00Z', 'voided': False}
T['hx_batches'] = [bat(1, 'cartridges', 'CART-261020-01', 'Live Resin Cart 1g', 'Blue Dream', '2026-10-20'), bat(2, 'gummies', 'GUM-261021-02', 'Gummies 100mg', 'Mango', '2026-10-21'),
                   bat(3, 'ethanol_extraction', 'ETH-261022-01', '', '', '2026-10-22'), bat(4, 'pre_rolls', 'PR-261022-03', 'Pre-Roll 1g', 'Wedding Cake', '2026-10-22'), bat(5, 'butane_extraction', 'BHO-261023-01', '', '', '2026-10-23')]
def ck(fails=(), extra=False):
    items = ['removed', 'clean', 'equip', 'materials', 'gmp', 'foreign', 'tools'] + (['safety', 'solvent'] if extra else [])
    return {k: {'r': 'fail' if k in fails else 'pass', 'fixed': k in fails and k != 'clean', 'l': k} for k in items}
T['hx_line_clearances'] = [
    {**L, 'id': 'lc1', 'number': 'LC-2026-014', 'batch_id': 'bt1', 'batch_label': 'Cartridges CART-261020-01 · Live Resin Cart 1g Blue Dream', 'batch_type': 'cartridges', 'area': 'Filling line 1', 'equipment_ids': ['eq1', 'eq2'], 'checks': ck(), 'issues': '', 'corrections': '', 'result': 'cleared', 'checked_by': 'Devon Brooks', 'verified_by': 'Maria Gonzalez', 'deviation_id': None, 'checked_at': Z('2026-10-20', '07:40'), 'recorded_by': 'Devon Brooks', 'created_at': Z('2026-10-20', '07:40'), 'voided': False},
    {**L, 'id': 'lc2', 'number': 'LC-2026-015', 'batch_id': 'bt2', 'batch_label': 'Gummies GUM-261021-02 · Gummies 100mg Mango', 'batch_type': 'gummies', 'area': 'Kitchen', 'equipment_ids': ['eq5'], 'checks': ck(('tools',)), 'issues': 'Spatula missing from the tool board', 'corrections': 'Found in the wash sink, cleaned, sanitized and returned', 'result': 'cleared', 'checked_by': 'Lee Park', 'verified_by': 'Maria Gonzalez', 'deviation_id': None, 'checked_at': Z('2026-10-21', '06:55'), 'recorded_by': 'Lee Park', 'created_at': Z('2026-10-21', '06:55'), 'voided': False},
    {**L, 'id': 'lc3', 'number': 'LC-2026-016', 'batch_id': 'bt3', 'batch_label': 'Ethanol Extraction ETH-261022-01', 'batch_type': 'ethanol_extraction', 'area': 'Extraction Room', 'equipment_ids': ['eq4'], 'checks': ck(('clean',), True), 'issues': 'Residue on the evaporator condenser', 'corrections': 'Line stopped, re-clean scheduled before start', 'result': 'not_cleared', 'checked_by': 'Lee Park', 'verified_by': '', 'deviation_id': None, 'checked_at': Z('2026-10-22', '07:10'), 'recorded_by': 'Lee Park', 'created_at': Z('2026-10-22', '07:10'), 'voided': False},
    {**L, 'id': 'lc4', 'number': 'LC-2026-017', 'batch_id': 'bt3', 'batch_label': 'Ethanol Extraction ETH-261022-01', 'batch_type': 'ethanol_extraction', 'area': 'Extraction Room', 'equipment_ids': ['eq4'], 'checks': ck((), True), 'issues': '', 'corrections': '', 'result': 'cleared', 'checked_by': 'Lee Park', 'verified_by': 'Maria Gonzalez', 'deviation_id': None, 'checked_at': Z('2026-10-22', '09:30'), 'recorded_by': 'Lee Park', 'created_at': Z('2026-10-22', '09:30'), 'voided': False},
    {**L, 'id': 'lc5', 'number': 'LC-2026-018', 'batch_id': 'bt4', 'batch_label': 'Pre-Rolls PR-261022-03 · Pre-Roll 1g Wedding Cake', 'batch_type': 'pre_rolls', 'area': 'Pre-roll room', 'equipment_ids': [], 'checks': ck(), 'issues': '', 'corrections': '', 'result': 'cleared', 'checked_by': 'Devon Brooks', 'verified_by': '', 'deviation_id': None, 'checked_at': Z('2026-10-22', '12:20'), 'recorded_by': 'Devon Brooks', 'created_at': Z('2026-10-22', '12:20'), 'voided': False}]
def rw(i, num, status, src, material, qty, unit, reason, ident, **k):
    b = {**L, 'id': 'rw%d' % i, 'number': num, 'source_kind': 'batch', 'source_batch_id': src, 'source_hold_id': None, 'source_text': '', 'material': material, 'product': '', 'quantity': qty, 'unit': unit, 'reason': reason, 'identified_on': ident,
         'tag': '', 'location': 'Rework shelf, vault', 'expires_on': None, 'status': status, 'inspection': '', 'analysis': '', 'inspection_result': '', 'inspected_by': '', 'inspected_on': None, 'like_to_like': False, 'like_note': '', 'approved_by': '', 'approved_at': None,
         'target_batch_id': None, 'target_expires': None, 'used_on': None, 'used_qty': '', 'destroyed_reason': None, 'deviation_id': None, 'files': [], 'notes': '', 'created_by': 'Lee Park', 'created_at': ident + 'T15:00:00Z'}
    b.update(k); return b
T['hx_rework'] = [
    rw(6, 'RW-2026-006', 'identified', 'bt4', 'Pre-roll cones with torn tips (re-grind flower)', '320', 'g', 'Cone tips torn in the filler', '2026-10-22', product='Pre-Roll 1g Wedding Cake', tag='1A4000000000000000031177'),
    rw(5, 'RW-2026-005', 'inspected', 'bt1', 'Distillate recovered from overfilled carts', '41.5', 'g', 'Overfill recovered from rejected carts', '2026-10-20', product='Live Resin Cart 1g Blue Dream', tag='1A4000000000000000031102',
       inspection='Clear amber, no debris, no hardware fragments', analysis='In-house potency 88.1% THC, residual solvents pass (COA 26-1020)', inspection_result='pass', inspected_by='Maria Gonzalez', inspected_on='2026-10-21'),
    rw(4, 'RW-2026-004', 'approved', 'bt2', 'Mis-shaped gummies (re-melt)', '1.8', 'kg', 'Deposit weight out of spec', '2026-10-14', product='Gummies 100mg Mango', inspection='No foreign matter', analysis='Potency 10.2 mg/piece, within spec', inspection_result='pass', inspected_by='Maria Gonzalez',
       inspected_on='2026-10-15', like_to_like=True, approved_by='Maria Gonzalez', approved_at='2026-10-15T20:00:00Z', expires_on='2027-04-14'),
    rw(3, 'RW-2026-003', 'used', 'bt3', 'Winterized crude from tail fraction', '850', 'g', 'Potency below spec, re-distill', '2026-10-02', inspection='Clear, no debris', analysis='Potency 71%, solvents pass', inspection_result='pass', inspected_by='Maria Gonzalez',
       like_to_like=True, approved_by='Maria Gonzalez', approved_at='2026-10-03T20:00:00Z', expires_on='2027-10-02', target_batch_id='bt3', target_expires='2027-09-01', used_on='2026-10-22', used_qty='850'),
    rw(2, 'RW-2026-002', 'destroyed', None, 'Spilled kief from the floor', '60', 'g', 'Floor spill', '2026-09-28', source_kind='other', source_text='Floor sweep, pre-roll room', destroyed_reason='Contaminated; destroyed per Waste Destruction Log 2026-09-28')]
T['hx_holds'] = []
T['hx_line_clearances'].sort(key=lambda x: x['checked_at'], reverse=True)
T['hx_env_tests'].sort(key=lambda x: x['sampled_on'], reverse=True)

# ---------- Time clock ----------
TC = []
def tc(i, pid, nm, ev, hm, late=False, lm=None, src='kiosk', reason='', voided=False, vr=None, by='Kiosk'):
    TC.append({**L, 'id': 'tc%d' % i, 'profile_id': pid, 'person_name': nm, 'event_type': ev, 'ts': Z(TODAY, hm), 'event_date': TODAY, 'late': late, 'late_minutes': lm, 'source': src, 'reason': reason, 'recorded_by': by, 'created_at': Z(TODAY, hm), 'voided': voided, 'void_reason': vr})
n = 0
for pid, nm, evs in [('u-lee', 'Lee Park', [('entry', '06:58'), ('break1_out', '09:30'), ('break1_in', '09:49', True, 4), ('break2_out', '11:30')]),
                     ('u-maria', 'Maria Gonzalez', [('entry', '07:02'), ('break1_out', '09:15'), ('break1_in', '09:29')]),
                     ('u-devon', 'Devon Brooks', [('entry', '06:45'), ('break1_out', '08:50'), ('break1_in', '09:04'), ('break2_out', '10:40'), ('break2_in', '11:08')]),
                     ('u-aisha', 'Aisha Khan', [('entry', '05:00'), ('break1_out', '07:00'), ('break1_in', '07:14'), ('break2_out', '09:00'), ('break2_in', '09:29'), ('clockout', '11:15')])]:
    for e in evs:
        n += 1; tc(n, pid, nm, e[0], e[1], *(e[2:] if len(e) > 2 else ()))
tc(90, 'u-tom', 'Tom Becker', 'entry', '07:30', src='manual', reason='Forgot badge at home, arrival confirmed by Maria Gonzalez', by='Sam Salari')
tc(91, 'u-devon', 'Devon Brooks', 'break3_out', '11:09', voided=True, vr='Double scan by mistake, Devon was not on break')
T['hx_time_clock'] = TC

def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def person(pid): return next(p for p in T['hx_profiles'] if p['id'] == pid)
_h = handle
def handle(route, request):
    u = request.url; path = urllib.parse.urlparse(u).path
    if path.startswith('/rest/v1/rpc/'):
        fn = path.split('/')[-1]; b = json.loads(request.post_data or '{}')
        if fn == 'hx_badge_roster':
            out = []
            for p in T['hx_profiles']:
                bd = BADGES.get(p['id'])
                out.append({'id': p['id'], 'name': p['name'], 'email': p['email'], 'has_badge': bool(bd), **({k: bd[k] for k in ('badge_no', 'title', 'photo', 'zoom', 'pos_x', 'pos_y', 'code')} if bd else {}), 'issued_at': bd and '2026-09-02T15:00:00Z', 'issued_by': bd and 'Sam Salari'})
            return jr(route, sorted(out, key=lambda x: x['name'].lower()))
        if fn == 'hx_badge_lookup':
            hit = [(k, v) for k, v in BADGES.items() if v['code'] == b['p_code']]
            if not hit: return jr(route, None)
            p = person(hit[0][0]); return jr(route, {'name': p['name'], 'title': hit[0][1]['title'], 'photo': hit[0][1]['photo'], 'badge_no': hit[0][1]['badge_no'], 'valid': True})
        if fn == 'hx_kiosk_clock':
            hit = [(k, v) for k, v in BADGES.items() if v['code'] == b['p_code'].upper()]
            if not hit: return jr(route, {'error': 'Badge not recognized.'})
            pid, bd = hit[0]; p = person(pid)
            return jr(route, {'name': p['name'], 'title': bd['title'], 'photo': bd['photo'], 'event': 'break2_in', 'ts': FIXED.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z'), 'late': False, 'late_minutes': 0})
        if fn == 'hx_kiosk_open_visitors':
            return jr(route, [{'id': v['id'], 'visitor_name': v['visitor_name'], 'time_in': v['time_in']} for v in T['hx_visitor_log'] if not v.get('time_out')])
    return _h(route, request)

def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def sign(pg):
    cv = pg.locator('canvas').last; cv.scroll_into_view_if_needed(); bb = cv.bounding_box()
    pg.mouse.move(bb['x'] + 30, bb['y'] + 60); pg.mouse.down()
    for i in range(1, 25): pg.mouse.move(bb['x'] + 30 + i * 9, bb['y'] + 60 + 25 * math.sin(i / 2.2))
    pg.mouse.up()
FULL_CSS = '.mo{position:absolute!important;align-items:flex-start!important;bottom:auto!important;min-height:100vh;height:auto!important} .md{max-height:none!important}'
def mshot(pg, name, full=True):
    pg.evaluate('document.activeElement && document.activeElement.blur && document.activeElement.blur()')
    try: pg.mouse.move(2, pg.viewport_size['height'] - 2)
    except Exception: pass
    h = pg.add_style_tag(content=FULL_CSS) if full else None
    pg.wait_for_timeout(300); pg.locator('.md').last.screenshot(path=SH + name)
    if h: h.evaluate('e=>e.remove()')
    print('shot', name)
def vshot(pg, name, top=True):
    if top: pg.evaluate('window.scrollTo(0,0)')
    try: pg.mouse.move(pg.viewport_size['width'] - 5, pg.viewport_size['height'] - 5)
    except Exception: pass
    pg.wait_for_timeout(400); pg.screenshot(path=SH + name); print('shot', name)
def close_modal(pg):
    while pg.locator('.mo').count():
        pg.locator('.mo').last.click(position={'x': 5, 'y': 5}); pg.wait_for_timeout(150)
def nav(pg, name): pg.get_by_role('button', name=name, exact=True).first.click()
def row(pg, name): return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(name) + '$')))

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell')
    def newctx(w=1440, h=900, touch=False):
        c = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1.5, timezone_id='America/Chicago', has_touch=touch)
        c.clock.set_fixed_time(FIXED); c.route('**/*', handle); return c
    ctx = newctx()
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Quality standard')

    # ===== 1. Facility Logs =====
    nav(pg, 'Facility Logs'); pg.wait_for_selector('h2 >> text=Sanitation Log'); pg.wait_for_selector('td >> text=Aisha Khan')
    vshot(pg, 'facility_logs_overview.png')
    pg.locator('.tabs button', has_text='Temp / Humidity').click(); pg.wait_for_selector('h2 >> text=Temp / Humidity Log'); pg.wait_for_selector('td >> text=Gummy Curing Room')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    field(md, 'Location / Room').select_option(label='Storage Vault'); field(md, 'Temperature').fill('70.5'); field(md, 'Relative Humidity').fill('66')
    field(md, 'Corrective Action').fill('Dehumidifier in the vault switched on, door seal checked; re-reading in 1 hour'); sign(pg)
    mshot(pg, 'facility_logs_temp_form.png'); close_modal(pg)
    pg.get_by_role('button', name='Manage lists').click(); pg.wait_for_selector('.md >> text=Storage Vault')
    mshot(pg, 'facility_logs_lists.png', full=False); close_modal(pg)
    pg.locator('.tabs button', has_text='Scale Calibration').click(); pg.wait_for_selector('h2 >> text=Scale Calibration Log')
    pg.get_by_role('button', name='+ New entry').click(); md = pg.locator('.md')
    field(md, 'Scale ID').select_option(label='SCALE-01')
    for k in ('check_clean', 'check_level', 'check_shield', 'check_zero'): pass
    for lab in ('Scale and weighing pan are clean', 'Scale is level', 'No draft', 'Display reads zero', 'Certification seal'): md.locator('label.ck', has_text=lab).locator('input').check()
    for i, nm in enumerate(['Front Left', 'Front Right', 'Back Left', 'Back Right', 'Middle'], 1):
        field(md, 'Point %d — %s — Test Weight' % (i, nm)).fill('500')
        field(md, 'Point %d — %s — Scale Reading' % (i, nm)).fill('500.20' if i == 3 else ['500.00', '500.01', '', '499.99', '500.00'][i - 1])
    field(md, 'Scale status after check').select_option(index=2)
    field(md, 'Corrective Action').fill('Back-left reading 0.20 g high: re-leveled, re-zeroed and re-checked 500.00 g')
    field(md, 'Reviewed / Verified By').fill('Maria Gonzalez')
    mshot(pg, 'facility_logs_scale_form.png'); close_modal(pg)
    # kiosk on a phone
    kc = newctx(430, 1260, True); k = kc.new_page(); k.on('pageerror', lambda e: errors.append('KJS: ' + str(e)))
    k.goto(BASE + '?kiosk=log&type=temperature&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Temp / Humidity Log')
    bx = k.locator('.box'); field(bx, 'Recorded By').fill('Devon Brooks'); field(bx, 'Location / Room').select_option(label='Packaging Room')
    field(bx, 'Temperature').fill('71.2'); field(bx, 'Relative Humidity').fill('49'); sign(k)
    vshot(k, 'facility_logs_kiosk.png'); kc.close()

    # ===== 2. Visitor Log =====
    nav(pg, 'Visitor Log'); pg.wait_for_selector('td >> text=Rachel Ortiz')
    vshot(pg, 'facility_visitor_log_overview.png')
    pg.get_by_role('button', name='+ Manual entry').click(); md = pg.locator('.md')
    field(md, 'Full name').fill('Daniel Reyes'); field(md, 'Company').fill('Show-Me Packaging'); field(md, 'Purpose').select_option('Vendor / delivery')
    field(md, 'Visiting').fill('Devon Brooks'); field(md, 'Vehicle plate').fill('MO 4LC-207'); md.get_by_role('button', name='No', exact=True).click()
    md.locator('label', has_text='The visitor read the GMP rules').locator('input').check()
    mshot(pg, 'facility_visitor_log_manual.png'); close_modal(pg)
    kc = newctx(430, 1300, True); k = kc.new_page(); k.on('pageerror', lambda e: errors.append('KJS: ' + str(e)))
    k.goto(BASE + '?kiosk=visitor&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Facility GMP rules for visitors')
    field(k, 'Full name').fill('Rachel Ortiz'); field(k, 'Company').fill('Midwest Scale Co'); field(k, 'Purpose of visit').select_option('Contractor / maintenance')
    field(k, 'Who are you visiting').fill('Lee Park'); field(k, 'Vehicle plate').fill('MO 7KD-492'); sign(k)
    k.get_by_role('button', name='No', exact=True).click(); k.locator('label', has_text='I have read the GMP rules').locator('input').check()
    vshot(k, 'facility_visitor_kiosk_signin.png')
    k.get_by_role('button', name='Sign out', exact=True).first.click(); k.wait_for_selector('text=In at')
    k.set_viewport_size({'width': 430, 'height': 540}); vshot(k, 'facility_visitor_kiosk_signout.png'); kc.close()

    # ===== 3. Equipment =====
    nav(pg, 'Equipment'); pg.wait_for_selector('b >> text=Gummy depositor'); pg.wait_for_selector('tr:has-text("Gummy depositor") .badge:has-text("Overdue")')
    vshot(pg, 'facility_equipment_register.png')
    pg.get_by_role('button', name='+ Equipment').click(); md = pg.locator('.md')
    field(md, 'Name *').fill('Pre-roll cone filler'); field(md, 'Category').select_option('Production'); field(md, 'Location / room').fill('Pre-roll room')
    field(md, 'Make').fill('ConeTech'); field(md, 'Model').fill('CF-121'); field(md, 'Serial number').fill('CT121-0457'); field(md, 'Asset tag').fill('BF-EQ-0457'); field(md, 'Installed on').fill('2026-10-19')
    md.locator('label.ck', has_text='Touches product').locator('input').check()
    field(md, 'Controls').fill('Vibration timer 45 s, approved by QA (Maria Gonzalez)')
    field(md, 'Every (days)').fill('30'); field(md, 'Tasks (manufacturer requirements)').fill('Clean cone trays, check vibration motor mounts, replace tamping pins as needed')
    mshot(pg, 'facility_equipment_form.png'); close_modal(pg)
    row(pg, 'Gummy depositor').get_by_role('button', name='Open').click(); pg.wait_for_selector('.md >> text=Hose clamp')
    mshot(pg, 'facility_equipment_detail.png'); close_modal(pg)
    row(pg, 'SCALE-01').get_by_role('button', name='Open').click(); pg.locator('.md').get_by_role('button', name='Record calibration').click(); md = pg.locator('.md')
    field(md, 'Calibrated by').fill('Midwest Scale Co (R. Ortiz)')
    md.locator('label', has_text='+ Certificate').locator('input[type=file]').set_input_files({'name': 'SCALE-01 certificate 2026-10-23.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 cert'})
    pg.wait_for_selector('.md >> text=SCALE-01 certificate 2026-10-23.pdf')
    field(md, 'Details').fill('As found 500.02 g / as left 500.00 g at 500 g; 2000 g within 0.01 g')
    mshot(pg, 'facility_equipment_calibration.png'); close_modal(pg)

    # ===== 4. Chemicals =====
    nav(pg, 'Chemicals and SDS'); pg.wait_for_selector('b >> text=Quat sanitizer 200')
    vshot(pg, 'facility_chemicals_list.png')
    pg.locator('tr', has_text='Neem oil concentrate').get_by_role('button', name='Review').click(); md = pg.locator('.md')
    field(md, 'EPA registration').fill('70051-2'); field(md, 'Hazards').fill('May cause eye irritation; toxic to aquatic life')
    field(md, 'PPE (SDS section 8) *').fill('Nitrile gloves, safety glasses, long sleeves'); field(md, 'First aid').fill('Rinse eyes 15 min; wash skin with soap and water')
    field(md, 'Spill response').fill('Absorb with sand or pads, bag for disposal'); field(md, 'Disposal').fill('Per label; never into drains')
    md.locator('label.ck', has_text='Restricted').locator('input').check()
    mshot(pg, 'facility_chemicals_form.png'); close_modal(pg)
    with pg.expect_popup() as pop: pg.get_by_role('button', name='Print storage area lists').click()
    w = pop.value; w.wait_for_load_state(); w.set_viewport_size({'width': 960, 'height': 720}); w.wait_for_timeout(500); w.screenshot(path=SH + 'facility_chemicals_storage_sheet.png'); print('shot facility_chemicals_storage_sheet.png'); w.close()

    # ===== 5. Facility Tests =====
    nav(pg, 'Facility Tests'); pg.wait_for_selector('b >> text=Production room air')
    vshot(pg, 'facility_envtests_overview.png')
    row(pg, 'Production room air').get_by_role('button', name='Record result').click(); md = pg.locator('.md')
    field(md, 'Sampled on').fill('2026-10-20'); field(md, 'Sampled by').fill('Maria Gonzalez'); field(md, 'Report #').fill('PA-26-3381')
    field(md, 'Results (values)').fill('Yeast and mold 35 CFU/m3; total aerobic count 180 CFU/m3; PM2.5 9 ug/m3')
    md.locator('label', has_text='+ Report').locator('input[type=file]').set_input_files({'name': 'Pace_PA-26-3381_air.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 air'})
    pg.wait_for_selector('.md >> text=Pace_PA-26-3381_air.pdf')
    mshot(pg, 'facility_envtests_result_form.png'); close_modal(pg)
    row(pg, 'Food-contact surface swabs').get_by_role('button', name='History').click(); pg.wait_for_selector('.md >> text=Corrective action')
    mshot(pg, 'facility_envtests_history.png', full=False); close_modal(pg)

    # ===== 6. Line Clearance and Rework =====
    nav(pg, 'Line Clearance and Rework'); pg.wait_for_selector('text=LC-2026-018')
    vshot(pg, 'facility_lineclear_list.png')
    pg.get_by_role('button', name='+ Line clearance').click(); md = pg.locator('.md')
    pg.wait_for_selector('.md option >> text=BHO-261023-01', state='attached')
    field(md, 'Batch').select_option(label='BHO Extraction BHO-261023-01'); field(md, 'Room / line').fill('C1D1 room')
    md.locator('label.ck', has_text='EQ-008 Hydrocarbon gas detector').locator('input').check(); md.locator('label.ck', has_text='EQ-003 SCALE-02').locator('input').check()
    rows = md.locator('div.card div.row')
    for i in range(rows.count()): rows.nth(i).get_by_role('button', name='Pass').click()
    md.locator('div.row', has=pg.locator('span', has_text='Tools and utensils counted')).last.get_by_role('button', name='Fail').click()
    md.locator('div.row', has=pg.locator('span', has_text='Tools and utensils counted')).last.locator('label.ck input').check()
    field(md, 'Problems found *').fill('Torque wrench missing from the shadow board'); field(md, 'Corrections / corrective action *').fill('Found on the recovery pump cart, wiped down and returned')
    field(md, 'Verified by').fill('Maria Gonzalez')
    mshot(pg, 'facility_lineclear_form.png'); close_modal(pg)
    pg.locator('.tabs button', has_text='Rework').click(); pg.wait_for_selector('text=RW-2026-006')
    vshot(pg, 'facility_rework_list.png')
    pg.locator('tr', has_text='RW-2026-005').get_by_role('button', name='Approve').click(); md = pg.locator('.md')
    md.locator('label.ck', has_text='Like-to-like').locator('input').check(); field(md, 'Note').fill('Re-blend into the next Blue Dream live resin batch, max 5% of batch')
    field(md, 'Rework expires on *').fill('2027-04-20')
    mshot(pg, 'facility_rework_approve.png'); close_modal(pg)

    # ===== 7. Time Clock and Badges =====
    nav(pg, 'Time Clock and Badges'); pg.wait_for_selector('td >> text=Lee Park')
    vshot(pg, 'facility_timeclock_sheet.png')
    pg.locator('.tabs').get_by_role('button', name='On site now').click(); pg.wait_for_selector('text=In since')
    vshot(pg, 'facility_timeclock_onsite.png')
    pg.locator('.tabs').get_by_role('button', name='Badges').click(); pg.wait_for_selector('text=Choose a person')
    pg.locator('div', has_text=re.compile('^Maria Gonzalez')).last.click(); pg.wait_for_selector('h3 >> text=Maria Gonzalez'); pg.wait_for_timeout(600)
    vshot(pg, 'facility_timeclock_badges.png')
    kc = newctx(1024, 768); k = kc.new_page(); k.on('pageerror', lambda e: errors.append('KJS: ' + str(e)))
    k.goto(BASE + '?kiosk=clock&state=st-mo&lic=lic-mo'); k.wait_for_selector('text=Scan your badge')
    vshot(k, 'facility_timeclock_kiosk.png')
    kc.close()
    kc = newctx(390, 844, True); k = kc.new_page()
    k.goto(BASE + '?badge=' + BADGES['u-maria']['code']); k.wait_for_selector('text=Valid Hendrix badge')
    vshot(k, 'facility_timeclock_badge_check.png'); kc.close()
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
