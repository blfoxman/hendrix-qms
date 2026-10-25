# Build the seed data that the app itself generates (HACCP drafts, suggested risks, suggested schedule) once, headless,
# by running the same steps as manual/shots_mgmt.py (no screenshots), then dump the tables to work/seed_dump.json.
from common import *
from playwright.sync_api import sync_playwright
ns = setup(); T = ns['T']; field = hv.field; ME = ns['ME']; L = ns['L']; rscore = ns['rscore']
with sync_playwright() as pw:
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script(extra='localStorage.setItem("hx_hptab","plans");'))
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(500)
    menu(pg, 'HACCP').click(); pg.wait_for_selector('text=No HACCP plans yet')
    def new_plan(name, btype, ingr, allerg, shelf, valid, activate=True):
        pg.get_by_role('button', name='+ HACCP plan').click(); md = pg.locator('.md')
        field(md, 'Plan name *').fill(name); field(md, 'Covers batch type').select_option(btype)
        md.get_by_role('button', name='Start from a draft for this batch type').click(); pg.wait_for_timeout(200)
        field(md, 'Ingredients *').fill(ingr); field(md, 'Allergens *').fill(allerg); field(md, 'Shelf life / date').fill(shelf)
        md.locator('.tabs button', has_text='5. Validation').click(); field(md, 'How the plan was validated *').fill(valid)
        md.get_by_role('button', name='Activate plan' if activate else 'Save draft').click(); pg.wait_for_selector('.msg >> text=' + ('Activated ' if activate else 'Saved ') + name)
    new_plan('Infused gummies', 'gummies', 'Sugar, corn syrup, pectin, citric acid, natural mango and watermelon flavors, color, cannabis distillate', 'None declared (pectin-based; gelatin-free)', '12 months from the batch date',
             'Homogeneity study on 3 consecutive batches (RSD < 5%); aw limit 0.85 from FDA guidance, confirmed by 3 batch tests (aw 0.72-0.78)')
    new_plan('Vape cartridges', 'cartridges', 'Cannabis distillate, cannabis-derived terpenes (inhalation grade)', 'None', '12 months', 'Release on a passing state COA is required by 19 CSR 100-1; 3 consecutive batches released on passing COAs')
    # risks
    menu(pg, 'Risk Register').click(); pg.wait_for_selector('text=No risks yet.')
    pg.get_by_role('button', name='Suggested risks').click(); md = pg.locator('.md'); field(md, 'Owner for these risks *').fill('Lee Park')
    md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 12 risks')
    # verification schedule
    menu(pg, 'Verification Schedule').click(); pg.wait_for_selector('text=No verification schedule yet.')
    pg.get_by_role('button', name='Suggested schedule').click(); md = pg.locator('.md'); field(md, 'Who does them *').fill('Lee Park')
    md.get_by_role('button', name='Add selected').click(); pg.wait_for_selector('.msg >> text=Added 13 verification activities.')
    b.close()
print('errors', errs)
gp, cp = T['hx_haccp_plans'][0], T['hx_haccp_plans'][1]
c1, c2, k1 = gp['ccps'][0], gp['ccps'][1], cp['ccps'][0]
print('plans', [(p['number'], p['name'], p['status'], p['version']) for p in T['hx_haccp_plans']], [c['name'] for c in gp['ccps']], [c['name'] for c in cp['ccps']])
def mon(i, p, c, bid, val, ok, when, by, ver=None, corr='', disp=''):
    T['hx_haccp_monitoring'].append({**L, 'id': i, 'plan_id': p['id'], 'plan_version': 1, 'ccp_id': c['id'], 'ccp_name': c['name'], 'batch_id': bid, 'checked_at': when, 'checked_by': by, 'value': val,
        'within_limits': ok, 'corrective': corr, 'disposition': disp, 'verified_by': ver or '', 'verified_at': (when[:10] + 'T21:00:00Z') if ver else None, 'recorded_by': by, 'created_at': when, 'voided': False})
mon('m1', gp, c1, 'b1', '51.1 g (target 51.0 g)', True, '2026-10-14T14:10:00Z', 'Maria Lopez', 'Lee Park')
mon('m2', gp, c2, 'b1', 'aw 0.78', True, '2026-10-15T15:30:00Z', 'Lee Park', ME)
mon('m3', cp, k1, 'b3', 'COA TES-26-1182 passed, tag matches', True, '2026-10-12T16:00:00Z', 'Lee Park', ME)
mon('m4', gp, c1, 'b2', '50.9 g (target 51.0 g)', True, '2026-10-21T13:45:00Z', 'Maria Lopez')
mon('m5', cp, k1, 'b4', 'COA TES-26-1240: residual solvents FAIL', False, '2026-10-22T17:20:00Z', 'Lee Park', None, 'Batch kept on hold; remediation request filed with DCR; root cause investigation opened', 'held')
T['hx_haccp_verifications'].append({**L, 'id': 'hv1', 'plan_id': gp['id'], 'kind': 'records_review', 'done_on': '2026-10-16', 'done_by': ME, 'findings': 'Reviewed all CCP 1 and CCP 2 records for 10/01-10/15: complete, signed, within limits', 'result': 'ok', 'files': [], 'voided': False})
T['hx_haccp_verifications'].append({**L, 'id': 'hv2', 'plan_id': None, 'kind': 'calibration', 'done_on': '2026-10-05', 'done_by': 'Jordan Reyes', 'findings': 'Water activity meter checked against 0.760 aw standard: reads 0.762. Scale SC-02 checked with 50 g certified weight: OK', 'result': 'ok', 'files': [], 'voided': False})
# risks: owners, areas, controlled ones, reviews (as in shots_mgmt.py)
R = {r['title']: r for r in T['hx_risks']}
own = {'Residual solvent above the limit': 'Maria Lopez', 'Power or HVAC failure': 'Jordan Reyes', 'A rule change is missed': 'Marcus Bell', 'Single-source critical supplier fails': ME, 'Intentional adulteration or theft': ME}
for t, o in own.items(): R[t]['owner'] = o
areas = {'Microbial growth in infused edibles': 'Gummy line', 'Residual solvent above the limit': 'Extraction room', 'Unsafe additives in vape cartridges': 'Cartridge filling', 'Heavy metals from cartridge hardware': 'Cartridge filling', 'Allergen cross-contact between runs': 'Kitchen'}
for t, a in areas.items(): R[t]['area'] = a
x = R['Microbial growth in infused edibles']; x.update({'status': 'controlled', 'permanent_action': 'Water activity CCP added to the gummy HACCP plan; curing room humidity alarm installed', 'verification': '3 months of aw results all below 0.80; no microbial failures', 'verified_by': 'Lee Park', 'verified_on': '2026-09-18', 'residual_likelihood': 1, 'residual_severity': 4, 'last_reviewed': '2026-09-18'}); rscore(x)
x = R['Heavy metals from cartridge hardware']; x.update({'status': 'controlled', 'permanent_action': 'Only ceramic hardware from approved supplier with lot heavy-metal reports', 'verification': 'Filled carts from 4 hardware lots tested ND for lead', 'verified_by': 'Lee Park', 'verified_on': '2026-08-28', 'residual_likelihood': 1, 'residual_severity': 4, 'last_reviewed': '2026-08-28'}); rscore(x)
x = R['Residual solvent above the limit']; x.update({'last_reviewed': '2026-07-10', 'review_every_days': 90}); rscore(x)
for i, (t, d, by, l, s, ok, nt) in enumerate([('Microbial growth in infused edibles', '2026-09-18', 'Lee Park', 1, 4, True, 'aw trend reviewed, no failures since the CCP was added'),
                                               ('Heavy metals from cartridge hardware', '2026-08-28', 'Lee Park', 1, 4, True, 'Hardware lot reports on file for every lot received')]):
    T['hx_risk_reviews'].append({**L, 'id': 'rr%d' % i, 'risk_id': R[t]['id'], 'reviewed_on': d, 'reviewed_by': by, 'likelihood': l, 'severity': s, 'effective': ok, 'notes': nt, 'recorded_by': by, 'created_at': d + 'T15:00:00Z'})
print('risks', [(r['number'], r['title'], r['score'], r['status']) for r in T['hx_risks']])
VP = {p['activity']: p for p in T['hx_verification_plan']}
print('vs', list(VP))
VP['Scale and equipment calibration']['responsible'] = 'Jordan Reyes'; VP['Sanitation records reviewed and signed']['responsible'] = 'Maria Lopez'; VP['Management review']['responsible'] = ME
T['hx_verification_records'] += [{**L, 'id': 'vr1', 'plan_id': VP['Pest control service reports reviewed']['id'], 'done_on': '2026-10-02', 'done_by': 'Priya Shah', 'result': 'ok', 'findings': 'October service report reviewed; no activity in interior traps', 'action': '', 'files': [], 'voided': False, 'recorded_by': 'Priya Shah', 'created_at': '2026-10-02T15:00:00Z'},
                                 {**L, 'id': 'vr2', 'plan_id': VP['Labels checked against the batch']['id'], 'done_on': '2026-09-10', 'done_by': 'Priya Shah', 'result': 'ok', 'findings': '5 batch labels checked against COA and formulation', 'action': '', 'files': [], 'voided': False, 'recorded_by': 'Priya Shah', 'created_at': '2026-09-10T15:00:00Z'},
                                 {**L, 'id': 'vr3', 'plan_id': VP['Labels checked against the batch']['id'], 'done_on': '2026-08-11', 'done_by': 'Priya Shah', 'result': 'issues', 'findings': 'Watermelon gummy label showed the old THC per serving', 'action': 'Template corrected and 2 rolls reprinted', 'files': [], 'voided': False, 'recorded_by': 'Priya Shah', 'created_at': '2026-08-11T15:00:00Z'}]
out = {t: T[t] for t in ('hx_haccp_plans', 'hx_haccp_monitoring', 'hx_haccp_verifications', 'hx_risks', 'hx_risk_reviews', 'hx_verification_plan', 'hx_verification_records')}
out['SEQ'] = ns['SEQ']
json.dump(out, open(DUMP, 'w'), indent=1); print('dumped', {k: len(v) for k, v in out.items() if k != 'SEQ'}, ns['SEQ'])
