# Hendrix QMS training · Video 02 · Quality system (group qual)
#   python3 make.py synth | intro | qms | complaints | audits | sops | training | outro | build
# Record one scene at a time (2-core machine). PROBE=1 saves r.snap() screenshots to work/probe/.
import os, sys, re, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(HERE + '/../../kit'))
import hxvideo as hv
from playwright.sync_api import sync_playwright

hv.set_project(HERE)
SNAP = os.path.abspath(HERE + '/../../index_snapshot2.html')
SERIES = os.path.abspath(HERE + '/..') + '/'
OUT = SERIES + '02 - Quality system.mp4'
F = hv.field
SCENES = [('intro', 'Introduction'), ('qms', 'QMS'), ('complaints', 'Complaints'), ('audits', 'Internal Audits'),
          ('sops', 'SOPs'), ('training', 'Training'), ('outro', 'Wrap-up')]


def setup():
    ns = hv.load_setup('qual', snapshot=SNAP)
    ns['nowiso'] = hv.day_now                       # stamps on the fixed browser day
    ns['TODAY'] = dt.date(2026, 10, 24)
    return ns


# Keep modals clear of the burned-in captions (bottom ~120 CSS px): lift and shorten them a little.
CAP_CSS = '.main{padding-bottom:170px !important}.mo{padding:14px 14px 124px !important}.md{max-height:calc(100vh - 150px) !important}'


def open_app(pw, ns):
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script())
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_selector('text=Deviations & CAPA'); pg.add_style_tag(content=CAP_CSS); pg.wait_for_timeout(800)
    return b, ctx, pg


def navb(pg, name): return pg.locator('.nav').get_by_role('button', name=name, exact=True)


def go(r, pg, name, wait):
    r.click(navb(pg, name)); pg.wait_for_selector(wait); r.wait(0.3)
    if pg.evaluate('window.scrollY') > 0: r.smooth_top()


def closeall(r, pg):
    for _ in range(6):
        if not pg.locator('.mo').count(): return
        pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); r.wait(0.25)


# ------------------------------------------------------------------------------------ cards
def card(pw, mode):
    html = open(HERE + '/card.html').read()
    b = hv.launch(pw)
    ctx = b.new_context(viewport={'width': 1440, 'height': 810}, device_scale_factor=4 / 3)
    ctx.route('**/*', lambda route, req: route.fulfill(status=200, content_type='text/html', body=html) if '/card/' in req.url else route.abort())
    pg = ctx.new_page(); name = 'intro' if mode == 'title' else 'outro'
    r = hv.Rec(ctx, pg, name); r.mx, r.my = 1500, 900
    pg.goto('https://app.test/card/' + mode); pg.wait_for_timeout(500)
    r.start()
    if mode == 'title':
        r.wait(0.4)
        r.beat('i1', lambda: pg.evaluate('step(0)'))
        r.beat('i2', lambda: pg.evaluate('step(1)'))
        r.wait(1.0)
    else:
        pg.evaluate('step(0)'); r.wait(1.2)
        r.beat('e1', lambda: pg.evaluate('step(1)'))
        r.beat('e2', lambda: pg.evaluate('step(2)'))
        r.wait(1.8)
    r.snap('end')
    r.stop(tail=0.5); b.close()


# ------------------------------------------------------------------------------------ QMS
def scene_qms(pw):
    ns = setup(); T = ns['T']; h0 = ns['handle']
    def handle(route, request):          # CAPA verify: stamp who verified / closed, as the database does
        u = request.url
        if '/rest/v1/hx_capas' in u and request.method == 'PATCH':
            b = json.loads(request.post_data); rid = ns['rid_of'](u); row = next(x for x in T['hx_capas'] if x['id'] == rid)
            if b.get('effectiveness_rating'): b.update({'verified_by': ns['ME_NAME'], 'verified_at': hv.day_now()})
            if b.get('status') == 'closed': b.update({'closed_by': ns['ME_NAME'], 'closed_at': hv.day_now()})
            row.update(b); row['updated_at'] = hv.day_now()
            return route.fulfill(status=200, content_type='application/json', body=json.dumps([row]))
        return h0(route, request)
    ns['handle'] = handle
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'qms'); r.start()

    def q1():
        r.wait(1.5); r.click(navb(pg, 'QMS')); pg.wait_for_selector('text=Needs action'); r.wait(0.6)
        r.point(pg.locator('.card', has_text='Open deviations').first, 0.3)
    r.beat('q1', q1)

    def q2():
        r.point(pg.locator('.card', has_text='Overdue').first, 0.3); r.wait(1.2)
        r.point(pg.get_by_text('Needs action').first, 0.2); r.wait(1.5)
        r.point(pg.get_by_text('Root cause analysis decision needed').first, 0.5); r.wait(1.8)
        r.point(pg.get_by_text('Rated Partially effective', exact=False).first, 0.5); r.snap('dash')
    r.beat('q2', q2)
    md = pg.locator('.md')

    def q3():
        r.click(pg.get_by_role('button', name='+ Report deviation')); pg.wait_for_selector('.md')
        r.type(F(md, 'Deviation title'), 'Distillate drum seal broken on receipt')
        r.select(F(md, 'Department'), value='Warehouse')
        r.select(F(md, 'Category'), value='Supplier / material')
        r.select(F(md, 'Priority'), value='major')
    r.beat('q3', q3)

    def q4():
        r.type(F(md, 'Product affected'), 'Distillate (bulk), 5 kg drum', delay=22)
        r.type(F(md, 'Lot / batch number'), 'D-2610-07', delay=30)
        r.type(F(md, 'What happened?'), 'Tamper seal on drum 2 of 3 was broken on arrival. Weight matched the manifest.', delay=14)
    r.beat('q4', q4)

    def q5():
        r.type(F(md, 'Correction / immediate action taken'), 'Drum put on hold and photographed; supplier notified.', delay=16)
        r.type(F(md, 'Owner (who resolves it)'), 'Ana Morales', delay=30)
        r.fill(F(md, 'Due date'), '2026-10-31'); r.snap('form')
    r.beat('q5', q5)

    def q6():
        r.click(md.get_by_role('button', name='Submit deviation'))
        pg.wait_for_selector('.md >> text=DEV-2026-009'); r.wait(0.5)
        r.point(pg.locator('.md').get_by_text('DEV-2026-009').first); r.snap('saved')
    r.beat('q6', q6)

    def q7():
        r.click(pg.locator('.md').get_by_role('button', name='Close deviation').first); pg.wait_for_selector('text=Root cause analysis decision made')
        r.wait(0.6); r.point(pg.get_by_text('Correction / immediate action recorded').last, 0.3); r.wait(1.6)
        r.point(pg.get_by_text('Root cause analysis decision made').last, 0.3); r.wait(1.4)
        r.point(pg.get_by_text('Root cause recorded (when needed)').last, 0.3); r.wait(1.2)
        r.point(pg.get_by_text('Edit the deviation to complete', exact=False).last, 0.3); r.snap('closecheck')
    r.beat('q7', q7)

    def q8():
        r.click(pg.locator('.md').last.get_by_role('button', name='Cancel')); r.wait(0.4)
        r.point(pg.locator('.md').get_by_role('button', name='+ Create CAPA')); r.wait(1.0)
    r.beat('q8', q8)

    def q9():
        cl = pg.locator('.md').get_by_role('button', name=re.compile('^(Close|Close window)$')).last
        r.click(cl); r.wait(0.3)
        while pg.locator('.md').count():
            pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); pg.wait_for_timeout(200)
        r.click(pg.locator('.tabs button', has_text='CAPAs'))
        r.click(pg.locator('.card', has_text='CAPA-2026-003').first, fx=0.3); pg.wait_for_selector('.md')
        r.click(pg.locator('.md').get_by_role('button', name='Verify effectiveness')); md2 = pg.locator('.md').last
        r.type(F(md2, 'Verification evidence'), clear=True, text='4 of 4 gummy batches passed yeast and mold. No humidity alarms in 30 days.', delay=20)
        r.select(F(md2, 'Effectiveness'), value='effective'); r.snap('verify')
    r.beat('q9', q9)

    def q10():
        r.click(pg.locator('.md').last.get_by_role('button', name='Verify & close CAPA')); r.wait(1.0)
        r.point(pg.locator('.md').last.get_by_text('Effective', exact=False).first, 0.3); r.snap('closed')
    r.beat('q10', q10)

    def q11():
        closeall(r, pg); r.wait(0.3)
        r.click(pg.locator('.tabs button', has_text='Dashboard')); r.wait(0.5)
        r.point(pg.get_by_text('Needs action').first, 0.2)
    r.beat('q11', q11)
    r.stop(); b.close()
    print('capa3', next(x for x in T['hx_capas'] if x['id'] == 'capa-3')['status'])


# ------------------------------------------------------------------------------------ Complaints
def scene_complaints(pw):
    ns = setup(); T = ns['T']; h0 = ns['handle']
    def handle(route, request):          # stamp who logged / updated, as the database does
        u = request.url
        if '/rest/v1/hx_complaints' in u and request.method in ('POST', 'PATCH'):
            b = json.loads(request.post_data)
            if request.method == 'POST':
                b = dict(b); b.update({'created_by': ns['ME_NAME'], 'created_by_id': ns['ADMIN'], 'created_at': hv.day_now(), 'updated_at': hv.day_now()})
                b['number'] = ns['nxt']('hx_complaints', 'FBK' if b['type'] == 'feedback' else 'CMP'); T['hx_complaints'].insert(0, b)
                return route.fulfill(status=201, content_type='application/json', body=json.dumps([b]))
            row = next(x for x in T['hx_complaints'] if x['id'] == ns['rid_of'](u)); row.update(b); row.update({'updated_by': ns['ME_NAME'], 'updated_at': hv.day_now()})
            return route.fulfill(status=200, content_type='application/json', body=json.dumps([row]))
        return h0(route, request)
    ns['handle'] = handle
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'complaints'); r.start()

    def c1():
        r.wait(1.5); go(r, pg, 'Complaints', 'text=Repeat complaints'); r.wait(0.4)
        r.point(pg.locator('.card', has_text='Open').first, 0.3)
    r.beat('c1', c1)

    def c2():
        r.point(pg.locator('.card', has_text='Overdue').first, 0.3); r.wait(1.0)
        r.point(pg.locator('.card', has_text='Customer satisfaction').first, 0.3); r.wait(1.4)
        r.point(pg.get_by_text('Repeat complaints on the same lot', exact=False).first, 0.25); r.snap('list')
    r.beat('c2', c2)
    md = pg.locator('.md')

    def c3():
        r.click(pg.get_by_role('button', name='+ Log complaint')); pg.wait_for_selector('.md')
        r.select(F(md, 'Type'), value='dispensary'); r.select(F(md, 'Priority'), value='major')
        r.type(F(md, 'Title'), 'Pre-roll boxes missing child-resistant seal', delay=26)
    r.beat('c3', c3)

    def c4():
        r.select(F(md, 'Received by'), value='Email')
        r.type(F(md, 'Complainant'), 'Dev Patel (store manager)', delay=20)
        r.type(F(md, 'Contact'), 'dev@midtowncannabis.test', delay=18)
        r.type(F(md, 'Customer (dispensary)'), 'Midtown Cannabis Co.', delay=20)
    r.beat('c4', c4)

    def c5():
        r.select(F(md, 'Category'), value='Hardware / packaging failure')
        r.select(F(md, 'Batch'), value='b-pr')
        r.type(F(md, 'Description'), '4 of 30 boxes arrived with the child-resistant seal not engaged.', delay=16); r.snap('form')
    r.beat('c5', c5)

    def c6():
        r.click(md.get_by_role('button', name='Log complaint')); pg.wait_for_selector('.md >> text=CMP-2026-007'); r.wait(0.5)
        r.point(pg.locator('.md').get_by_text('CMP-2026-007').first, 0.2); r.snap('saved')
    r.beat('c6', c6)

    def c7():
        m = pg.locator('.md').last
        r.point(m.get_by_text('Investigation (CSQ 1.7)').first, 0.2); r.wait(0.4)
        r.type(F(m, 'Investigator (responsible)'), 'Marcus Lee', delay=28)
        r.type(F(m, 'Investigation'), 'Retained boxes from PR-261020 checked: 3 of 20 seals not engaged.', delay=14)
        r.type(F(m, 'Resolution'), '4 boxes replaced; credit issued.', delay=20); r.snap('invest')
    r.beat('c7', c7)

    def c8():
        m = pg.locator('.md').last
        r.click(m.get_by_role('button', name='Save and start investigating')); r.wait(0.8)
        r.point(m.get_by_role('button', name='Raise deviation'), 0.5); r.wait(1.6)
        r.point(m.get_by_role('button', name='Put batch on hold'), 0.5); r.snap('saved2')
    r.beat('c8', c8)

    def c9():
        m = pg.locator('.md').last
        r.point(F(m, 'Investigator (responsible)'), 0.15); r.wait(1.0)
        r.point(F(m, 'Investigation'), 0.15); r.wait(1.0)
        r.point(F(m, 'Resolution'), 0.15); r.wait(1.0)
        r.point(F(m, 'Answered on'), 0.3); r.wait(1.2)
        r.point(m.get_by_role('button', name='Close', exact=True), 0.5); r.snap('checks')
    r.beat('c9', c9)

    def c10():
        closeall(r, pg); r.wait(0.3)
        r.point(pg.get_by_text('Repeat complaints on the same lot', exact=False).first, 0.25)
    r.beat('c10', c10)
    r.stop(); b.close()
    print('cmp7', next(x for x in T['hx_complaints'] if x.get('number') == 'CMP-2026-007').get('status'))


# ------------------------------------------------------------------------------------ Internal Audits
def scene_audits(pw):
    ns = setup(); T = ns['T']; h0 = ns['handle']
    def handle(route, request):
        u = request.url
        if '/rest/v1/hx_audits' in u and request.method == 'POST':
            b = json.loads(request.post_data); b = dict(b[0] if isinstance(b, list) else b)
            b.update({'number': ns['nxt']('hx_audits', 'IA'), 'created_by': ns['ME_NAME'], 'created_at': hv.day_now()}); T['hx_audits'].insert(0, b)
            return route.fulfill(status=201, content_type='application/json', body=json.dumps([b]))
        return h0(route, request)
    ns['handle'] = handle
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'audits'); r.start()

    def a1():
        r.wait(1.5); go(r, pg, 'Internal Audits', 'text=IA-2026-002'); r.wait(0.4)
        r.point(pg.locator('.card', has_text='CSQ clauses audited').first, 0.3)
    r.beat('a1', a1)

    def a2():
        r.point(pg.locator('.card', has_text='CSQ clauses audited').first, 0.3); r.wait(1.6)
        r.point(pg.locator('.card', has_text='Open findings').first, 0.3); r.wait(1.0)
        r.point(pg.locator('.card', has_text='Overdue findings').first, 0.3); r.wait(1.0)
        r.point(pg.locator('.card', has_text='Next planned').first, 0.3)
    r.beat('a2', a2)

    def a3():
        r.click(pg.locator('.tabs button', has_text='Annual program')); pg.wait_for_selector('text=Annual audit program'); r.wait(0.6)
        r.point(pg.get_by_text('Module 1 · Management', exact=False).first, 0.3); r.wait(1.2)
        r.point(pg.locator('tr', has_text='Internal audits').first, 0.3); r.wait(1.0)
        r.point(pg.get_by_role('button', name=re.compile('^Plan an audit of the')), 0.5); r.snap('program')
    r.beat('a3', a3)
    md = pg.locator('.md')

    def a4():
        r.click(pg.locator('.tabs button', has_text='Audits')); r.wait(0.3)
        r.click(pg.get_by_role('button', name='+ Plan audit')); pg.wait_for_selector('.md')
        r.type(F(md, 'Audit title'), 'CSQ Module 2A audit - Q4 storage and receiving', delay=20)
        r.select(F(md, 'Department'), value='Warehouse')
        r.fill(F(md, 'Planned date'), '2026-11-18')
    r.beat('a4', a4)

    def a5():
        r.type(F(md, 'Lead auditor'), 'Chris Novak', delay=28)
        r.type(F(md, 'Auditor qualification'), 'CSQ internal auditor course 2025', delay=18)
        r.click(md.locator('label.ck', has_text='does not audit their own work').locator('input'))
    r.beat('a5', a5)

    def a6():
        r.type(F(md, 'Audit scope'), 'Warehouse, vaults, receiving and hold area.', delay=18)
        sel = md.locator('select').filter(has_text='+ One clause...')
        for c in ['2A.9.1', '2A.9.3', '2A.9.4', '2A.10.2']:
            r.select(sel, value=c)
        r.point(md.get_by_text(re.compile(r'CSQ checklist \(\d+ clauses?\)', re.I)).first, 0.2); r.snap('form')
    r.beat('a6', a6)

    def a7():
        r.click(md.get_by_role('button', name='Save audit')); pg.wait_for_selector('.md >> text=IA-2026-004'); r.wait(0.6)
        r.point(pg.locator('.md').get_by_text('IA-2026-004').first, 0.2); r.wait(1.4)
        r.point(pg.locator('.md').get_by_role('button', name='Start audit'), 0.5); r.snap('saved')
    r.beat('a7', a7)

    def a8():
        closeall(r, pg); r.wait(0.3)
        r.click(pg.locator('.card', has_text='IA-2026-002').first, fx=0.3); pg.wait_for_selector('.md >> text=Findings', timeout=15000); r.wait(0.4)
        r.point(pg.locator('.md').get_by_text('Nonconforming').first, 0.5); r.wait(1.0)
        fnd = pg.locator('.md .card', has_text='Vault 1 temperature logs').first
        r.point(fnd, 0.3); r.wait(1.0)
        r.point(fnd.get_by_text('DEV-2026-007').first, 0.5); r.snap('finding')
    r.beat('a8', a8)

    def a9():
        m = pg.locator('.md')
        r.point(m.get_by_text('Lead auditor', exact=False).first, 0.3); r.wait(1.6)
        r.point(m.get_by_text('Independent auditor', exact=False).first, 0.5); r.wait(1.2)
        r.point(m.get_by_text(re.compile('^Checklist', re.I)).first, 0.2); r.wait(1.4)
        r.point(m.locator('.card', has_text='Vault 1 temperature logs').first.get_by_role('button', name='Close finding'), 0.5); r.wait(1.0)
        r.point(F(m, 'Shared with'), 0.25); r.wait(0.8)
        r.point(m.get_by_role('button', name='Close audit'), 0.5); r.snap('checks')
    r.beat('a9', a9)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ SOPs
def scene_sops(pw):
    ns = setup(); T = ns['T']; h0 = ns['handle']
    def handle(route, request):          # emulate the database: approver / dates on publish, signature stamp
        u = request.url; m = request.method
        if '/rest/v1/hx_sops' in u and m in ('POST', 'PATCH'):
            b = json.loads(request.post_data); rows = b if isinstance(b, list) else [b]; out = []
            for x in rows:
                if m == 'PATCH':
                    row = next(y for y in T['hx_sops'] if y['id'] == ns['rid_of'](u)); row.update(x)
                else:
                    row = dict(x); row.setdefault('created_at', hv.day_now()); row.setdefault('created_by', ns['ME_NAME']); T['hx_sops'].insert(0, row)
                if row.get('status') == 'published':
                    if not row.get('approved_by'): row.update({'approved_by': ns['ME_NAME'], 'approved_at': hv.day_now()})
                    if not row.get('effective_date'): row['effective_date'] = '2026-10-24'
                    if not row.get('next_review'): row['next_review'] = '2027-10-24'
                row.update({'updated_by': ns['ME_NAME'], 'updated_at': hv.day_now()}); out.append(row)
            return route.fulfill(status=200 if m == 'PATCH' else 201, content_type='application/json', body=json.dumps(out))
        if '/rest/v1/hx_sop_acks' in u and m == 'POST':
            b = json.loads(request.post_data); x = dict(b[0] if isinstance(b, list) else b)
            x.update({'at': hv.day_now(), 'role_names': 'Compliance Officer'}); T['hx_sop_acks'].append(x)
            return route.fulfill(status=201, content_type='application/json', body=json.dumps([x]))
        return h0(route, request)
    ns['handle'] = handle
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'sops'); r.start()

    def p1():
        r.wait(1.5); go(r, pg, 'SOPs', '.card >> text=Cart Filling and Capping'); r.wait(0.4)
        r.point(pg.locator('.card', has_text='Needs my signature').first, 0.3)
    r.beat('p1', p1)

    def p2():
        r.point(pg.locator('.card', has_text='Needs my signature').first, 0.3); r.wait(1.6)
        c = pg.locator('.card', has_text='Cart Filling and Capping').first
        r.point(c, 0.2); r.wait(1.4); r.point(c, 0.93, 0.45); r.wait(1.2)
        r.point(pg.locator('.card', has_text='Sanitation of Production Rooms').first.get_by_text('Review overdue', exact=False).first, 0.5); r.snap('list')
    r.beat('p2', p2)
    md = pg.locator('.md')

    def p3a():
        r.point(pg.get_by_role('button', name='+ Manual SOP'), 0.5); r.wait(1.6)
        r.point(pg.get_by_role('button', name=re.compile('AI Generate SOP')), 0.5); r.wait(1.0)
        r.click(pg.get_by_role('button', name='+ Manual SOP')); pg.wait_for_selector('.md')
    r.beat('p3', p3a)

    def p4():
        r.type(F(md, 'Title'), 'Distillate Receiving and Storage', delay=24)
        r.select(F(md, 'Folder'), value='Production')
        r.click(md.get_by_role('button', name='Suggest')); r.wait(0.3)
        r.type(F(md, 'Description / purpose'), 'Receive and store bulk distillate so only accepted lots reach production.', delay=14)
    r.beat('p4', p4)

    def p5():
        r.type(md.locator('textarea[placeholder="Step 1..."]'), 'Check the manifest, METRC tag and COA.', delay=16)
        r.click(md.get_by_role('button', name='+ Add step'))
        r.type(md.locator('textarea[placeholder="Step 2..."]'), 'Inspect the drum seal; hold any broken seal.', delay=16)
        r.click(md.get_by_role('button', name='By role'))
        r.click(md.locator('label.ck', has_text='Production Manager').locator('input'))
        r.click(md.locator('label.ck', has_text='Production Tech').locator('input')); r.snap('form')
    r.beat('p5', p5)

    def p6():
        r.click(md.get_by_role('button', name='Create SOP')); r.wait(1.0)
        if pg.locator('.md').count(): closeall(r, pg)
        c = pg.locator('.card', has_text='Distillate Receiving and Storage').first
        r.click(c, fx=0.3); pg.wait_for_selector('.md'); r.wait(0.4)
        r.click(pg.locator('.md').get_by_role('button', name=re.compile('Approve & publish'))); r.wait(1.0); r.snap('published')
    r.beat('p6', p6)

    def p7():
        closeall(r, pg); r.wait(0.3)
        r.click(pg.locator('.card', has_text='Cart Filling and Capping').first, fx=0.3); pg.wait_for_selector('.md >> text=Signatures'); r.wait(0.4)
        r.point(pg.locator('.md').get_by_text('Procedure', exact=True).first, 0.2); r.wait(1.0)
        r.click(pg.locator('.md').get_by_role('button', name=re.compile('I have read and understood')))
        r.wait(0.4)
    r.beat('p7', p7)

    def p8():
        r.sign(pg.locator('.md canvas').last); r.wait(0.3)
        r.click(pg.locator('.md').last.get_by_role('button', name=re.compile('Sign & acknowledge'))); r.wait(1.0)
        r.point(pg.locator('.md').last.get_by_text('You signed this version', exact=False).first, 0.3); r.snap('signed')
    r.beat('p8', p8)

    def p9():
        r.point(pg.locator('.md').last.get_by_role('button', name=re.compile('Revise SOP')), 0.5); r.wait(3.0)
        r.point(pg.locator('.md').last.get_by_role('button', name='Version history'), 0.5); r.snap('revise')
    r.beat('p9', p9)
    r.stop(); b.close()
    print('acks', len(T['hx_sop_acks']), [s['status'] for s in T['hx_sops'] if s['title'].startswith('Distillate')])


# ------------------------------------------------------------------------------------ Training
def training_seed(ns, pg):
    """Off camera: first Full-access visit creates the CSQ courses; publish the online drafts; add records."""
    T = ns['T']; NAME = ns['NAME']; ADMIN = ns['ADMIN']; S, L = ns['S'], ns['L']
    navb(pg, 'Training').click(); pg.wait_for_selector('.msg >> text=Created the 9 CSQ training courses', timeout=20000)
    pg.wait_for_selector('.card >> text=Online courses ready'); pg.get_by_role('button', name='Publish all').click(); pg.wait_for_selector('.msg >> text=/Published \\d+ online course/')
    course = ns['course']
    def rec(cpre, uid, day, trainer='Dana Brooks', qual='QA Manager, PCQI', method='Classroom', files=None):
        c = course(cpre); d0 = dt.date.fromisoformat(day); mo = c['refresher_months']; exp = None
        if mo: mm = d0.month - 1 + mo; exp = dt.date(d0.year + mm // 12, mm % 12 + 1, min(d0.day, 28)).isoformat()
        a = 'Passed' if c['assessment_required'] else 'Not required'
        T['hx_training_records'].append({'id': 'tr-%d' % len(T['hx_training_records']), 'state_id': S, 'license_id': L, 'course_id': c['id'], 'user_id': uid, 'person_name': NAME[uid], 'completed_on': day, 'expires_on': exp,
            'trainer_name': trainer, 'trainer_qualification': qual, 'method': method, 'language': 'English', 'assessment': a, 'score': '9/10' if a == 'Passed' else '', 'files': files or [], 'notes': '',
            'recorded_by': ns['ME_NAME'], 'voided': False, 'created_at': ns['ts'](day)})
    for uid, day in [(ADMIN, '2026-02-10'), ('u-marcus', '2025-11-05'), ('u-priya', '2025-08-01'), ('u-jordan', '2026-03-14'), ('u-ana', '2026-01-20'), ('u-tess', '2026-05-04')]: rec('Missouri regulatory', uid, day)
    for uid, day in [('u-marcus', '2026-04-11'), ('u-priya', '2026-05-02'), ('u-jordan', '2026-06-15'), ('u-tess', '2026-09-30')]: rec('Current Good', uid, day)
    for uid in [ADMIN, 'u-marcus', 'u-priya', 'u-ana', 'u-tess', 'u-jordan']: rec('Cannabis safety', uid, '2026-03-02' if uid != 'u-tess' else '2026-09-30')
    for uid in [ADMIN, 'u-marcus', 'u-priya', 'u-jordan', 'u-ana']: rec('Personnel hygiene', uid, '2026-09-03', trainer='Ana Morales', qual='Sanitation lead, 6 yrs')
    rec('Personnel hygiene', 'u-tess', '2025-11-15', trainer='Ana Morales', qual='Sanitation lead, 6 yrs')
    for uid in [ADMIN, 'u-marcus', 'u-priya', 'u-jordan', 'u-tess', 'u-ana']: rec('Product defense', uid, '2026-01-12', trainer='Chris Novak', qual='Security manager')
    for uid in [ADMIN, 'u-marcus', 'u-ana']: rec('Chemical safety', uid, '2026-02-20', method='On the job')
    rec('CSQ Certification', ADMIN, '2026-02-01', trainer='ASI / CSQ', qual='CSQ Program Overview course', method='External certification')
    rec('HACCP certification', ADMIN, '2025-06-12', trainer='International HACCP Alliance course', qual='IHA accredited lead instructor', method='External certification')
    rec('Extraction safety', 'u-priya', '2026-07-20', method='On the job')
    navb(pg, 'Dashboard').click(); pg.reload(); pg.wait_for_selector('text=Deviations & CAPA'); pg.add_style_tag(content=CAP_CSS); pg.wait_for_timeout(1000)
    pg.evaluate('window.scrollTo(0,0)')


def scene_training(pw):
    ns = setup(); T = ns['T']; h0 = ns['handle']
    def handle(route, request):
        u = request.url
        if '/rest/v1/hx_training_records' in u and request.method == 'POST':
            b = json.loads(request.post_data); rows = b if isinstance(b, list) else [b]
            for x in rows:                # the database fills the name, the expiry (course refresher) and who recorded it
                c = next(k for k in T['hx_training_courses'] if k['id'] == x['course_id']); d0 = dt.date.fromisoformat(x['completed_on']); mo = c['refresher_months']
                if mo: mm = d0.month - 1 + mo; x['expires_on'] = dt.date(d0.year + mm // 12, mm % 12 + 1, min(d0.day, 28)).isoformat()
                x.update({'person_name': ns['NAME'][x['user_id']], 'recorded_by': ns['ME_NAME'], 'created_at': hv.day_now(), 'voided': False})
                T['hx_training_records'].append(x)
            return route.fulfill(status=201, content_type='application/json', body=json.dumps(rows))
        return h0(route, request)
    ns['handle'] = handle
    b, ctx, pg = open_app(pw, ns)
    training_seed(ns, pg)
    r = hv.Rec(ctx, pg, 'training'); r.start()

    def t1():
        r.wait(1.5); go(r, pg, 'Training', 'td >> text=Tess Whitaker'); r.wait(0.5)
        r.point(pg.locator('.card', has_text='Training current').first, 0.3)
    r.beat('t1', t1)

    def t2():
        row = pg.locator('tr', has_text='Marcus Lee').first
        r.point(row, 0.08); r.wait(1.0)
        r.point(pg.locator('thead').first, 0.45); r.wait(1.2)
        r.point(row.locator('td').nth(2), 0.5); r.wait(1.0)
        r.point(pg.locator('tr', has_text='Tess Whitaker').first.locator('td').nth(4), 0.5); r.wait(1.0)
        r.point(pg.locator('tr', has_text='Ana Morales').first.locator('td').nth(2), 0.5); r.snap('matrix')
    r.beat('t2', t2)
    md = pg.locator('.md')

    def t3():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='+ Record training')); pg.wait_for_selector('.md')
        r.select(F(md, 'Course'), label='Current Good Manufacturing Practices (cGMP)')
        r.fill(F(md, 'Date completed'), '2026-10-23')
        r.click(md.locator('label.ck', has_text='Ana Morales').locator('input'))
    r.beat('t3', t3)

    def t4():
        r.type(F(md, 'Trainer'), 'Dana Brooks', delay=28)
        r.type(F(md, 'Trainer qualification'), 'QA Manager, 8 yrs; PCQI', delay=18)
        r.select(F(md, 'Method'), value='Classroom')
        r.select(F(md, 'Assessment'), value='Passed'); r.snap('form')
    r.beat('t4', t4)

    def t5():
        r.click(md.get_by_role('button', name=re.compile(r'^Save( \d+)? records?$'))); r.wait(1.0)
        if pg.locator('.md').count(): closeall(r, pg)
        r.point(pg.locator('tr', has_text='Ana Morales').first.locator('td').nth(2), 0.5); r.snap('saved')
    r.beat('t5', t5)

    def t6():
        r.click(pg.locator('.tabs button', has_text='Records')); r.wait(0.8)
        row = pg.locator('tr', has_text='Ana Morales').filter(has_text='Current Good').first
        r.point(row, 0.3); r.wait(2.5)
        v = row.get_by_role('button', name='Void')
        if v.count(): r.point(v.first, 0.5)
        r.snap('records')
    r.beat('t6', t6)

    def t7():
        r.smooth_top()
        r.click(pg.locator('.tabs button', has_text='My training')); r.wait(0.6)
        r.click(pg.locator('.card', has_text='Current Good Manufacturing').get_by_role('button', name='Take course').first)
        pg.wait_for_selector('.md >> text=Lesson 1 of'); r.wait(2.0)
        r.click(pg.locator('.md').get_by_role('button', name='Next lesson')); r.snap('lesson')
    r.beat('t7', t7)

    def t8():
        r.wait(1.5); closeall(r, pg); r.wait(0.3)
        r.click(pg.locator('.tabs button', has_text='Training matrix')); r.wait(0.6)
        r.point(pg.locator('tr', has_text='Dana Brooks').first.locator('td').nth(2), 0.5); r.snap('tip')
    r.beat('t8', t8)
    r.stop(); b.close()


if __name__ == '__main__':
    what = sys.argv[1:] or ['synth']
    for w in what:
        if w == 'synth': hv.synth()
        elif w == 'build': hv.build(SCENES, OUT, os.path.splitext(OUT)[0] + '.srt')
        else:
            with sync_playwright() as pw:
                {'intro': lambda: card(pw, 'title'), 'outro': lambda: card(pw, 'end'), 'qms': lambda: scene_qms(pw), 'complaints': lambda: scene_complaints(pw),
                 'audits': lambda: scene_audits(pw), 'sops': lambda: scene_sops(pw), 'training': lambda: scene_training(pw)}[w]()
