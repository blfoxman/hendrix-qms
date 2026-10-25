# Video 01 - Setting up and running Hendrix. Usage: python3 make.py [scene ...] [build]
from common import *
from playwright.sync_api import sync_playwright

OUTDIR = os.path.abspath(HERE + '/..')
FINAL = OUTDIR + '/01 - Setting up and running Hendrix.mp4'
SCENES = [('intro', 'Introduction'), ('dashboard', 'Dashboard'), ('locations', 'States and Licenses'), ('rulebook', 'Rulebook'),
          ('standards', 'Standards (CSQ)'), ('team', 'Team and Access'), ('roles', 'Roles'), ('audit', 'Audit Trail'),
          ('settings', 'Settings'), ('import', 'Import (Excel / Sheets)'), ('end', 'Wrap-up')]
CARD = open(HERE + '/card.html').read()


def ripple(r):
    r.page.evaluate('([x,y])=>window.__ripple&&window.__ripple(x,y)', [r.mx, r.my]); r.wait(0.3)


def rec_page(b, ns, name, wait='.nav', **kw):
    kw.setdefault('session', hv.session_script())
    ctx = hv.new_context(b, ns, **kw)
    pg = ctx.new_page(); pg.goto(ns['BASE']); pg.wait_for_selector(wait); pg.wait_for_timeout(900)
    r = hv.Rec(ctx, pg, name)
    return ctx, pg, r


# ------------------------------------------------------------------ cards
def scene_card(pw, mode):
    b = hv.launch(pw)
    ctx = b.new_context(viewport={'width': 1440, 'height': 810}, device_scale_factor=4 / 3)
    ctx.route('**/*', lambda route, req: route.fulfill(status=200, content_type='text/html', body=CARD) if '/card/' in req.url else route.abort())
    ctx.add_init_script(hv.CURSOR_JS)
    pg = ctx.new_page(); name = 'intro' if mode == 'title' else 'end'
    r = hv.Rec(ctx, pg, name); r.mx, r.my = 1500, 900
    pg.goto('https://app.test/card/' + mode); pg.wait_for_timeout(500)
    r.start()
    if mode == 'title':
        pg.evaluate('step(0)'); r.wait(0.6)
        r.beat('t1')
        r.beat('t2', lambda: pg.evaluate('step(1)'))
        r.wait(0.5)
    else:
        pg.evaluate('step(0)'); r.wait(0.8)
        r.beat('w1')
        r.beat('w2', lambda: (pg.evaluate('step(1)'), r.wait(4.5), pg.evaluate('step(2)')))
        r.wait(1.2)
    r.snap('end'); r.stop(tail=0.5); b.close()


# ------------------------------------------------------------------ Dashboard
def scene_dashboard(pw):
    ns = load_found(); T = ns['T']
    T['hx_rules'] += [{'id': 'mo%d' % i, 'state_id': 'st-mo', 'category': c, 'citation': '19 CSR 100-1.%s' % n, 'title': t, 'body': t + '.', 'created_at': '0%d' % i}
                      for i, (n, t, c) in enumerate([('010', 'Definitions', 'General'), ('020', 'Facility Licenses and Certifications', 'Licensing'),
                                                     ('090', 'Seed-to-Sale Tracking', 'Inventory / Tracking'), ('100', 'Security Requirements', 'Security'),
                                                     ('120', 'Packaging and Labeling', 'Packaging'), ('140', 'Testing Facilities', 'Testing')])]
    b = hv.launch(pw)
    prep_standards(b, ns)
    ctx, pg, r = rec_page(b, ns, 'dashboard', wait='text=Sign in', session=None, routes=[hv.token_route()])
    r.mx, r.my = 1000, 640
    r.start()

    def d1():
        r.wait(0.6)
        r.click(pg.get_by_role('link', name='Create an account')); pg.wait_for_selector('text=Create account'); r.wait(0.3)
        r.type(field(pg, 'Full name'), 'Jordan Price', delay=40)
        r.type(field(pg, 'Email'), 'jordan.price@blackfoxmfg.com', delay=22)
        r.type(field(pg, 'Password'), 'shift1', delay=60)
    r.beat('d1', d1)

    def d2():
        r.click(pg.get_by_role('button', name='Create account')); pg.wait_for_selector('text=Password must be at least 8 characters'); r.wait(0.3)
        r.point(pg.get_by_text('Password must be at least 8 characters').first, 0.4); r.snap('pw')
    r.beat('d2', d2)

    def d3():
        r.click(pg.get_by_role('link', name='Sign in')); pg.wait_for_selector('button:has-text("Sign in")'); r.wait(0.3)
        r.type(field(pg, 'Email'), 'sam@blackfoxmfg.com', delay=40, clear=True)
        r.type(field(pg, 'Password'), 'goldfox-2026', delay=45, clear=True)
        r.click(pg.get_by_role('button', name='Sign in', exact=True)); pg.wait_for_selector('.nav'); r.wait(0.4); r.snap('in')
    r.beat('d3', d3)

    def d4():
        st = pg.locator('select').nth(0); li = pg.locator('select').nth(1)
        r.select(st, value='st-mi'); r.wait(0.8)
        r.select(st, value='st-mo'); r.wait(0.5)
        r.select(li, value='lic-mo'); r.wait(0.3); r.snap('sel')
    r.beat('d4', d4)

    def d5():
        r.point(pg.locator('select').nth(1), 0.4); r.wait(1.5)
        r.point(pg.get_by_text('Black Fox · MAN000109').first, 0.3); r.snap('lic')
    r.beat('d5', d5)

    def d6():
        r.point(pg.locator('.card', has_text='Regulatory agency').first, 0.5, 0.4); r.wait(0.7)
        r.point(pg.locator('.card', has_text='Active license').first, 0.5, 0.4); r.wait(0.7)
        r.point(pg.locator('.card', has_text='State rulebook').first, 0.5, 0.4); r.snap('row1')
    r.beat('d6', d6)

    def d7():
        r.point(pg.locator('.card', has_text='Deviations & CAPA').first, 0.5, 0.3); r.wait(0.8)
        r.point(pg.locator('.card', has_text='Equipment').filter(has_text='All current').first, 0.5, 0.3); r.wait(0.8)
        r.point(pg.get_by_text('Open equipment').first); r.snap('cards')
    r.beat('d7', d7)

    def d8():
        q = pg.locator('.card', has_text='Quality standard').first
        r.point(q, 0.5, 0.4); r.wait(2.6); r.snap('qs')
        r.smooth_top(); r.point(pg.get_by_role('button', name='Sign out'))
    r.beat('d8', d8)
    r.stop(); b.close()


# ------------------------------------------------------------------ States and Licenses
def scene_locations(pw):
    ns = load_found()
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'locations')
    r.start()

    def l1():
        r.click(nav(pg, 'States and Licenses')); pg.wait_for_selector('td >> text=Black Fox Farms'); r.wait(0.5)
        mo = pg.locator('.card.gold', has_text='Missouri').first
        r.point(mo.locator('b, h2, h3, div').filter(has_text=re.compile('^Missouri$')).first, 0.3); r.wait(0.8)
        r.point(pg.locator('td', has_text='MAN000109').first); r.wait(0.6)
        r.point(pg.locator('th', has_text='CSQ').first); r.snap('page')
    r.beat('l1', l1)

    def l2():
        r.click(pg.locator('.card.gold', has_text='Missouri').get_by_role('button', name='+ Add license')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.type(field(md, 'License / facility name'), 'Black Fox North', delay=40)
        r.type(field(md, 'License number'), 'MAN000233', delay=50)
        r.type(field(md, 'License type'), 'Manufacturer', delay=45)
    r.beat('l2', l2)

    def l3():
        md = pg.locator('.md')
        r.point(field(md, 'Operation'), 0.4); r.wait(1.5)
        r.point(md.get_by_text(re.compile('^CSQ Standard for Manufacturing')).first, 0.4); r.snap('op')
    r.beat('l3', l3)

    def l4():
        r.click(pg.locator('.md').get_by_role('button', name='Save')); pg.wait_for_selector('.md', state='detached'); pg.wait_for_selector('td >> text=Black Fox North'); r.wait(0.3)
        row = pg.locator('tr', has_text='MAN000233')
        r.point(row.locator('td').nth(3), 0.4); r.wait(0.8)
        r.point(pg.locator('select').nth(1), 0.4); r.snap('saved')
    r.beat('l4', l4)

    def l5():
        row = pg.locator('tr', has_text='TRN000088')
        r.point(row.locator('td').first, 0.3); r.wait(0.5)
        r.point(row.get_by_text('Inactive', exact=False).first); r.wait(0.6)
        r.point(pg.locator('tr', has_text='MAN000109').get_by_role('button', name='Deactivate')); r.snap('deact')
    r.beat('l5', l5)

    def l6():
        mi = pg.locator('.card.gold', has_text='Michigan').first
        r.click(mi.get_by_role('button', name='Delete').first); pg.wait_for_selector("text=Delete or move this state's licenses first."); r.wait(0.3)
        r.point(pg.get_by_text("Delete or move this state's licenses first.").first, 0.3); r.snap('del')
    r.beat('l6', l6)

    r.beat('l7', lambda: r.point(pg.locator('th', has_text='CSQ').first))
    r.stop(); b.close()


# ------------------------------------------------------------------ Rulebook
def scene_rulebook(pw):
    ns = load_found()
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'rulebook')
    r.start()

    def r1():
        r.click(nav(pg, 'Missouri Rulebook')); pg.wait_for_selector('text=Upload rules PDF'); r.wait(0.6)
        up = pg.locator('label', has_text='Upload rules PDF')
        r.point(up); r.wait(0.3); ripple(r)
        up.locator('input[type=file]').set_input_files(SCR + 'rbpdf/mo.pdf')
        pg.wait_for_selector('text=7 rules found', timeout=30000)
    r.beat('r1', r1)

    def r2():
        md = pg.locator('.md')
        r.point(md.get_by_text('mo.pdf').first, 0.2); r.wait(0.5)
        r.point(md.get_by_text('Missouri Code of State Regulations').first, 0.4); r.wait(0.6)
        r.point(md.get_by_text('7 rules found').first); r.wait(0.6)
        r.point(md.locator('input[type=checkbox]').nth(1)); r.wait(0.4)
        r.point(md.locator('input[type=checkbox]').nth(3)); r.snap('review')
    r.beat('r2', r2)

    def r3():
        md = pg.locator('.md')
        row = md.locator('div.rbrow', has=pg.locator('span', has_text=re.compile(r'^19 CSR 100-1\.100$')))
        r.point(row.locator('input[type=text], input:not([type])').first, 0.3); r.wait(0.4)
        r.point(row.locator('select').first, 0.4); r.wait(0.3)
        r.click(row.get_by_role('button', name='Text')); r.wait(0.6); r.snap('text')
    r.beat('r3', r3)

    def r4():
        md = pg.locator('.md')
        r.point(md.get_by_text('Nothing is saved until you click Import').first, 0.6); r.wait(2.5)
        r.click(md.get_by_role('button', name='Import 7 rules')); pg.wait_for_selector('.msg >> text=Imported from mo.pdf', timeout=20000)
        for s in ns['T']['hx_rule_sources']: s['created_by_name'] = 'Sam Salari'
    r.beat('r4', r4)

    def r5():
        r.point(pg.get_by_text('Source PDFs').first, 0.3); r.wait(0.4)
        r.point(pg.get_by_text('latest').first); r.wait(0.4)
        r.click(pg.get_by_role('button', name='+ Add rule')); md = pg.locator('.md'); md.wait_for()
        r.type(field(md, 'Category'), 'Facility', delay=40)
        r.type(field(md, 'Citation (section / rule number)'), 'Company policy QA-12', delay=28)
        r.type(field(md, 'Title'), 'Hairnets and beard covers in production rooms', delay=20)
        r.type(field(md, 'Rule text / what it requires'), 'Hairnets, and beard covers where needed, in every production room.', delay=12)
        r.click(md.get_by_role('button', name='Save')); pg.wait_for_selector('.md', state='detached'); r.wait(0.3)
    r.beat('r5', r5)

    def r6():
        r.type(pg.get_by_placeholder(re.compile('^Search Missouri rules')), 'security', delay=60)
        r.wait(0.4); r.point(pg.get_by_text('Security Requirements').first, 0.2); r.snap('search')
    r.beat('r6', r6)
    r.stop(); b.close()


# ------------------------------------------------------------------ Standards (CSQ)
def clause_row(pg, num):
    return pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile('^' + re.escape(num) + '$'))).first


def scene_standards(pw):
    ns = load_found()
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'standards')
    r.start()

    def s1():
        r.click(nav(pg, 'Standards (CSQ)')); pg.wait_for_selector('text=No standard added yet'); r.wait(0.5)
        r.point(pg.get_by_text('No standard added yet').first, 0.3); r.wait(1.5)
        r.click(pg.get_by_role('button', name=re.compile('^Add CSQ Standard'))); pg.wait_for_selector('.msg >> text=Added'); r.snap('added')
    r.beat('s1', s1)

    def s2():
        r.point(pg.get_by_text(re.compile('with 130 clauses')).first, 0.5); r.wait(1.6)
        r.point(pg.locator('select').nth(1), 0.4); r.wait(0.8)
        r.click(pg.get_by_role('button', name='Adopt for this license')); pg.locator('.md').wait_for()
    r.beat('s2', s2)

    def s3():
        md = pg.locator('.md')
        r.point(md.get_by_text('CSQ Standard for Manufacturing (Module 3C)').first, 0.3); r.wait(0.4)
        r.select(field(md, 'Target level'), value='2'); r.wait(0.3)
        r.select(field(md, 'Status'), value='Audit scheduled')
        r.type(field(md, 'Certification body'), 'Kiwa ASI', delay=50)
        r.fill(field(md, 'Audit date'), '2026-12-08'); r.snap('adopt')
    r.beat('s3', s3)

    def s4():
        r.click(pg.locator('.md').get_by_role('button', name='Adopt standard')); pg.wait_for_selector('text=0% complete'); r.wait(0.4)
        r.point(pg.get_by_text('Operational alerts').first, 0.3); r.wait(0.8)
        r.point(pg.get_by_text('Level 2 - cGMP + HACCP').first, 0.4); r.wait(0.6)
        r.point(pg.get_by_text('0% complete').first); r.snap('adopted')
    r.beat('s4', s4)

    def s5():
        row = clause_row(pg, '1.4')
        r.click(row.locator('div.row').first, fx=0.3); r.wait(0.5)
        r.click(row.get_by_role('button', name='Record conformance')); pg.locator('.md').wait_for()
    r.beat('s5', s5)

    def s6():
        md = pg.locator('.md')
        r.select(field(md, 'Status'), value='Not applicable'); r.wait(0.2)
        r.click(md.get_by_role('button', name='Save')); pg.wait_for_selector('text=Write why this clause does not apply'); r.wait(0.2)
        r.point(md.get_by_text(re.compile('^Write why this clause does not apply')).first, 0.4); r.snap('na')
    r.beat('s6', s6)

    def s7():
        r.click(pg.locator('.md').get_by_role('button', name='Cancel')); pg.wait_for_selector('.md', state='detached')
        r.click(clause_row(pg, '1.4').get_by_role('button', name='Record conformance')); md = pg.locator('.md'); md.wait_for()
        r.select(field(md, 'Status'), value='Conforming')
        r.type(field(md, 'Owner'), 'Compliance Officer', delay=28)
        r.type(field(md, 'SOP / document reference'), 'SOP-QA-001 Document Control Rev 3', delay=16)
        r.type(md.locator('textarea').first, 'Master list of SOPs in Hendrix; every change is in the Audit Trail.', delay=12)
        r.snap('conf')
        r.click(md.get_by_role('button', name='Save')); pg.wait_for_selector('.md', state='detached'); r.wait(0.3)
    r.beat('s7', s7)

    def s8():
        r.smooth_top(); r.wait(0.2)
        r.click(pg.get_by_role('button', name='Inspector view')); pg.wait_for_selector('text=Inspector view · read only'); r.wait(0.6)
        r.point(pg.get_by_text('Inspector view · read only').first); r.wait(0.6)
        r.wheel(900, steps=40); r.snap('insp')
    r.beat('s8', s8)
    r.stop(); b.close()


# ------------------------------------------------------------------ Team and Access
def scene_team(pw):
    ns = load_found()
    b = hv.launch(pw)
    add_roles(b, ns)
    ctx, pg, r = rec_page(b, ns, 'team')
    r.start()

    def m1():
        r.click(nav(pg, 'Team and Access')); pg.wait_for_selector('text=2 waiting for approval'); r.wait(0.5)
        r.point(pg.get_by_text('2 waiting for approval').first, 0.3); r.wait(0.6)
        r.point(pg.locator('tr', has_text='Jordan Price').locator('td').first, 0.3); r.snap('page')
    r.beat('m1', m1)

    def m2():
        r.click(pg.locator('tr', has_text='Jordan Price').get_by_role('button', name='Approve')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.click(md.locator('label.ck', has_text='Team Member').locator('input'))
        r.click(md.locator('label.ck', has_text='All licenses, in every state').locator('input'))
        r.click(md.locator('label.ck', has_text='Black Fox (MAN000109)').locator('input')); r.snap('approve')
    r.beat('m2', m2)

    def m3():
        md = pg.locator('.md'); sel = md.locator('tr', has_text='Batch Tracker').locator('select')
        r.point(md.get_by_text('Custom access').first, 0.2); r.wait(0.4)
        r.select(sel, value='read'); r.wait(0.4); r.snap('custom')
        r.click(md.get_by_role('button', name='Approve', exact=True)); pg.wait_for_selector('.md', state='detached'); r.wait(0.3)
    r.beat('m3', m3)

    def m4():
        row = pg.locator('tr', has_text='Jordan Price')
        r.point(row.locator('td').nth(1), 0.4); r.wait(0.7)
        r.point(row.locator('td').nth(2), 0.4); r.wait(0.7)
        r.point(row.locator('td').nth(3), 0.4); r.wait(0.7)
        r.point(row.get_by_role('button', name='Manage')); r.snap('row')
    r.beat('m4', m4)

    def m5():
        r.click(pg.locator('tr', has_text='Sam Salari').get_by_role('button', name='Manage')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.point(md.locator('label.ck', has_text='System admin').locator('input'), 0.5); r.wait(0.6)
        r.point(md.get_by_text('You cannot remove your own approval or admin rights.').first, 0.3); r.snap('self')
    r.beat('m5', m5)

    def m6():
        r.click(pg.locator('.md').get_by_role('button', name='Cancel')); r.wait(0.3)
        r.point(nav(pg, 'Roles'))
    r.beat('m6', m6)
    r.stop(); b.close()


# ------------------------------------------------------------------ Roles
def scene_roles(pw):
    ns = load_found()
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'roles')
    r.start()

    def o1():
        r.click(nav(pg, 'Roles')); pg.wait_for_selector('text=No roles yet'); r.wait(0.5)
        r.point(pg.get_by_text('No roles yet').first, 0.3); r.wait(2.2)
        r.click(pg.get_by_role('button', name='Add Black Fox roles')); pg.wait_for_selector('.card >> text=Production Lead'); r.snap('added')
    r.beat('o1', o1)

    def o2():
        c = pg.locator('.card', has_text='General Manager').first
        r.point(c.get_by_text(re.compile('people|person', re.I)).first); r.wait(0.6)
        r.point(c.get_by_text(re.compile('^Leadership')).first, 0.3); r.wait(0.6)
        r.point(c.get_by_text(re.compile('Requirements not set', re.I)).first); r.wait(0.6)
        r.point(c.get_by_text('Rulebook: Edit').first, 0.3); r.snap('cards')
    r.beat('o2', o2)

    def o3():
        card = pg.locator('.card', has_text='Sanitation').filter(has_text='Fills the sanitation, waste')
        r.click(card.get_by_role('button', name='Edit')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.type(field(md, 'Requirements (CSQ 2A.13.1)'), 'Chemical safety and SDS training; cGMP sanitation training', delay=14)
    r.beat('o3', o3)

    def o4():
        md = pg.locator('.md'); sel = md.locator('tr', has_text='Chemicals and SDS').locator('select')
        r.select(sel, value='editor'); r.wait(0.5)
        r.point(md.locator('tr', has_text='Chemicals and SDS').locator('td').first, 0.5); r.snap('edit')
    r.beat('o4', o4)

    def o5():
        r.click(pg.locator('.md').get_by_role('button', name='Save role')); pg.wait_for_selector('.md', state='detached'); r.wait(0.4)
        c = pg.locator('.card', has_text='Sanitation').filter(has_text='Fills the sanitation, waste').first
        r.point(c.get_by_text(re.compile('Chemical safety and SDS')).first, 0.3); r.wait(0.8)
        r.point(c.get_by_text('Chemicals and SDS: Edit').first, 0.3); r.snap('saved')
    r.beat('o5', o5)
    r.stop(); b.close()


# ------------------------------------------------------------------ Audit Trail
def scene_audit(pw):
    ns = load_found(); audit_rows(ns)
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'audit')
    r.start()

    def a1():
        r.click(nav(pg, 'Audit Trail')); pg.wait_for_selector('td >> text=Entered on the wrong license'); r.wait(0.5)
        hdr = pg.locator('thead th')
        for i in range(min(hdr.count(), 7)):
            r.point(hdr.nth(i), dur=0.35); r.wait(0.3)
        r.snap('page')
    r.beat('a1', a1)

    def a2():
        s = pg.get_by_placeholder(re.compile('^Search who'))
        r.type(s, 'Derek', delay=80); r.wait(0.6); r.snap('search')
    r.beat('a2', a2)

    def a3():
        s = pg.get_by_placeholder(re.compile('^Search who'))
        r.type(s, '', clear=True)
        area = pg.locator('select', has=pg.locator('option', has_text='Batch record'))
        r.select(area, value='hx_batches'); pg.wait_for_selector('td >> text=typo on first entry'); r.wait(0.3)
        row = pg.locator('tr', has_text='typo on first entry').first
        r.point(row.locator('td').nth(5), fx=0.3); r.wait(0.8)
        r.point(row.locator('td').nth(6), fx=0.3); r.snap('filtered')
    r.beat('a3', a3)

    def a3b():
        per = pg.locator('select', has=pg.locator('option', has_text='All time'))
        r.point(per, 0.4); r.wait(1.2)
        r.point(pg.locator('label', has_text='Missouri only').first, 0.3); r.wait(2.5)
        row = pg.locator('tr', has_text='typo on first entry').first
        r.point(row.locator('td').nth(6), fx=0.3)
    r.beat('a3b', a3b)

    def a4():
        r.point(pg.locator('thead th').nth(1)); r.wait(2.0)
        r.point(pg.get_by_role('button', name='Export CSV').first); r.snap('csv')
    r.beat('a4', a4)
    r.stop(); b.close()


# ------------------------------------------------------------------ Settings
def scene_settings(pw):
    ns = load_found()
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'settings')
    r.start()

    def e1():
        r.click(nav(pg, 'Settings')); pg.wait_for_selector('text=Business details on printouts'); r.wait(0.4)
        r.point(pg.get_by_text(re.compile('^Managing Black Fox')).first, 0.3); r.wait(0.4)
        r.type(field(pg, 'Legal name'), 'Black Fox Manufacturing LLC', delay=22)
        r.type(field(pg, 'Doing business as'), 'Black Fox', delay=30)
        r.type(field(pg, 'Address'), '4120 Industrial Park Dr, St. Louis, MO 63110', delay=14)
        r.type(field(pg, 'Phone'), '314-555-0142', delay=24)
        r.type(field(pg, 'Email'), 'compliance@blackfoxmfg.com', delay=16)
    r.beat('e1', e1)

    def e2():
        r.point(pg.get_by_text('Upload logo').first); ripple(r)
        pg.locator('input[type=file]').set_input_files(hv.P('work', 'bf_logo.png')); pg.wait_for_selector('img[alt=logo]'); r.wait(0.3)
        r.point(pg.get_by_text('Printout header preview').first, 0.3); r.snap('logo')
    r.beat('e2', e2)

    def e3():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='Time clock', exact=True)); r.wait(0.8)
        r.click(pg.get_by_role('button', name='Facility logs', exact=True)); r.wait(0.3)
        r.type(pg.locator('.row', has_text='Sanitation Log').last.locator('input'), '1', delay=60); r.snap('logs')
    r.beat('e3', e3)

    def e4():
        r.click(pg.get_by_role('button', name='Line Map', exact=True).last); r.wait(0.3)
        r.point(pg.get_by_text('Line Map: a batch is stopped after').first, 0.3); r.wait(1.0)
        r.point(pg.locator('input[aria-label="Hours without an update"]'), 0.4); r.snap('lm')
    r.beat('e4', e4)

    def e5():
        r.type(pg.locator('input[aria-label="Hours without an update"]'), '0', delay=60, clear=True)
        r.click(pg.get_by_role('button', name='Save settings')); pg.wait_for_selector('text=hours without an update must be between 1 and 72'); r.wait(0.2)
        r.point(pg.get_by_text(re.compile('hours without an update must be between')).first, 0.3); r.snap('err')
    r.beat('e5', e5)

    def e6():
        r.type(pg.locator('input[aria-label="Hours without an update"]'), '6', delay=60, clear=True)
        r.click(pg.get_by_role('button', name='Save settings')); pg.wait_for_selector('text=Settings saved for Black Fox.'); r.wait(0.2)
        r.point(pg.get_by_text('Settings saved for Black Fox.').first, 0.3); r.snap('saved')
    r.beat('e6', e6)
    r.stop(); b.close()


# ------------------------------------------------------------------ Import
def scene_import(pw):
    ns = load_found()
    b = hv.launch(pw)
    ctx, pg, r = rec_page(b, ns, 'import')
    r.start()

    def i1():
        r.click(nav(pg, 'Import (Excel / Sheets)')); pg.wait_for_selector('text=1. What are you importing?'); r.wait(0.4)
        for k in ('Suppliers', 'Chemicals and SDS', 'Risk register', 'Org chart'):
            r.point(pg.locator('button.card', has_text=k).first, 0.4, 0.4, dur=0.45); r.wait(0.5)
        r.click(pg.locator('button.card', has_text='Equipment').first); r.snap('kind')
    r.beat('i1', i1)

    def i2():
        btn = pg.get_by_text('Choose .xlsx / .csv file').first
        r.point(btn); ripple(r)
        pg.locator('input[type=file]').set_input_files(SCR + 'import_eq.xlsx'); pg.wait_for_selector('text=import_eq.xlsx'); r.wait(0.3)
        r.point(pg.get_by_text(re.compile('import_eq.xlsx')).first); r.wait(0.5)
        r.point(field(pg, 'Header row'), 0.4); r.snap('file')
    r.beat('i2', i2)

    def i3():
        r.click(pg.get_by_role('button', name='Match with AI')); pg.wait_for_selector('text=Columns matched by the AI'); r.wait(0.4)
        r.point(pg.get_by_text('Columns matched by the AI').first, 0.4); r.wait(0.6)
        r.point(pg.get_by_text('Equipment name *').first, 0.5); r.wait(0.5)
        r.point(pg.get_by_text('Category', exact=True).first, 0.5); r.snap('match')
    r.beat('i3', i3)

    def i4():
        r.point(pg.get_by_text('2 to import').first); r.wait(0.5)
        r.point(pg.get_by_text('1 with problems').first); r.wait(0.5)
        r.point(pg.get_by_text('Equipment name is missing').first, 0.4); r.wait(1.2)
        r.point(pg.get_by_text('Already in Hendrix - skipped').first, 0.4); r.snap('preview')
    r.beat('i4', i4)

    def i5():
        r.click(pg.get_by_role('button', name='Import 2 rows')); pg.wait_for_selector('text=Imported 2.'); r.wait(0.3)
        r.point(pg.get_by_text('Imported 2.').first, 0.3); r.wait(1.5)
        r.point(pg.locator('select').nth(1), 0.4); r.snap('done')
    r.beat('i5', i5)
    r.stop(); b.close()


FUN = {'intro': lambda pw: scene_card(pw, 'title'), 'end': lambda pw: scene_card(pw, 'end'), 'dashboard': scene_dashboard, 'locations': scene_locations,
       'rulebook': scene_rulebook, 'standards': scene_standards, 'team': scene_team, 'roles': scene_roles, 'audit': scene_audit,
       'settings': scene_settings, 'import': scene_import}

if __name__ == '__main__':
    args = sys.argv[1:]
    hv.synth()
    todo = [a for a in args if a in FUN] if args else list(FUN)
    if todo:
        with sync_playwright() as pw:
            for n in todo: FUN[n](pw)
    if not args or 'build' in args:
        hv.build(SCENES, FINAL)
