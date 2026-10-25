# Shared setup for video 07 (Production Line Map for managers): kit import, Line Map seed via the real
# Postgres function (pgmap bridge in shots_lm.py, as in 06_prod and the tutorial scene 6b), helpers.
import os, sys, re, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(HERE + '/../../kit'))
import hxvideo as hv
hv.set_project(HERE)
SCR = hv.SCR
SNAP = HERE + '/index_snapshot3.html'          # fresh copy of index.html taken for this video
F = hv.field
ME = 'Sam Salari'
EXEC = '44444444-4444-4444-4444-444444444444'   # an executive: View on Line Map only
EXEC_NAME = 'Morgan Hale'

# Keep pop-up windows clear of the burned-in captions (bottom ~120 CSS px): lift and shorten them a little.
CAP_CSS = '.main{padding-bottom:170px !important}.mo{align-items:flex-start !important;padding:14px 14px 124px !important}.md{max-height:calc(100vh - 150px) !important}'
CAP_INIT = "addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent=%s;document.head.appendChild(s);});" % json.dumps(CAP_CSS)


def reseed_lm():
    """Fresh Line Map data in the lmtest Postgres copy (times are relative to the real now())."""
    subprocess.run(SCR + 'pg.sh lmtest -q -f - < ' + SCR + 'lm_seed.sql', shell=True, check=True, capture_output=True)
    subprocess.run([SCR + 'pg.sh', 'lmtest', '-qc', "set session_replication_role=replica; update hx_batches set voided=true where id not like 'lm%';"], check=True, capture_output=True)


def setup_lm():
    ns = hv.load_setup('lm', path=SCR + 'shots_lm.py', snapshot=SNAP); T = ns['T']
    T['hx_profiles'][0]['name'] = ME
    T['hx_profiles'].append({'id': EXEC, 'name': EXEC_NAME, 'email': 'morgan@x', 'role': 'member', 'approved': True, 'created_at': '2026-01-01',
                             'role_ids': [], 'license_ids': [], 'perms': {'linemap': 'read'}})
    return ns


def app(pw, ns, name, uid=hv.ADMIN, extra='', wait='text=Quality standard'):
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, fixed=None, session=hv.session_script(uid=uid, extra=extra))   # real clock: map times come from the database now()
    ctx.add_init_script(CAP_INIT)
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav')
    if wait: pg.wait_for_selector(wait)
    pg.wait_for_timeout(800)
    r = hv.Rec(ctx, pg, name)
    return b, pg, r


def navb(pg, name): return pg.locator('.nav').get_by_role('button', name=name, exact=True).first


def go(r, pg, name, wait):
    r.click(navb(pg, name), after=0.05); pg.evaluate('window.scrollTo(0,0)')
    pg.wait_for_selector(wait); r.wait(0.3)


def train(pg, label): return pg.locator('button[aria-label^="%s,"]' % label)


def scroll_to(r, pg, loc, top=86):
    y = loc.evaluate('e=>e.getBoundingClientRect().top+window.scrollY') - top
    pg.evaluate("y=>window.scrollTo({top:y,behavior:'smooth'})", y); r.wait(0.9)


def eqr(i, num, name, cat, loc, **k):
    base = {'state_id': 'st-mo', 'license_id': 'lic-mo', 'id': 'eq%d' % i, 'number': num, 'name': name, 'category': cat, 'location': loc, 'make': '', 'model': '', 'serial': '', 'asset_tag': '',
            'product_contact': False, 'critical': False, 'status': 'in_service', 'installed_on': None, 'controls_note': '', 'pm_interval_days': None, 'pm_tasks': '', 'cal_required': False,
            'cal_interval_months': None, 'cal_method': '', 'cal_standard': '', 'cal_protection': '', 'cal_last': None, 'cal_due': None, 'val_required': False, 'iq_on': None, 'oq_on': None,
            'pq_on': None, 'reval_due': None, 'log_item_id': None, 'files': [], 'notes': '', 'retired_reason': None, 'created_by': ME, 'created_at': '2026-03-01T10:00:00Z'}
    base.update(k); return base


def seed_equipment(T):
    """The mock's Equipment register, matching the Postgres seed (EQ-014 Cone filler, calibration due 4 days ago)."""
    import datetime as d
    today = d.date.today(); due = (today - d.timedelta(days=4)).isoformat(); last = (today - d.timedelta(days=4 + 182)).isoformat()
    T['hx_equipment'] = [
        eqr(1, 'EQ-001', 'Cartridge filler #1', 'Production', 'Filling room', make='FillTech', model='CF-300', product_contact=True, critical=True, pm_interval_days=90),
        eqr(2, 'EQ-002', 'SCALE-01', 'Scale / balance', 'Packaging Room', make='Ohaus', model='Scout SKX2202', critical=True, cal_required=True, cal_interval_months=12, cal_last='2025-11-10', cal_due='2026-11-10'),
        eqr(5, 'EQ-005', 'Gummy depositor', 'Production', 'Kitchen', make='CandyWorks', model='GD-1', product_contact=True, critical=True, pm_interval_days=30),
        eqr(14, 'EQ-014', 'Cone filler', 'Production', 'Pre-roll room', make='ConeTech', model='CF-6', product_contact=True, critical=True, cal_required=True, cal_interval_months=6,
            cal_standard='Reference weights', cal_last=last, cal_due=due),
    ]
    T.setdefault('hx_equipment_events', [])
