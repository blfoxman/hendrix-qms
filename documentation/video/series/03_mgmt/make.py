# Video 03: HACCP and the management system.  python3 make.py <scene> [<scene> ...] | build
from common import *
from playwright.sync_api import sync_playwright
field = hv.field
CARD = open(HERE + '/card.html').read()
SCENES = [('intro', 'Introduction'), ('haccp', 'HACCP'), ('risk', 'Risk Register'), ('change', 'Change Control'), ('org', 'Org Chart'),
          ('obj', 'Quality Objectives'), ('review', 'Management Review'), ('verif', 'Verification Schedule'), ('end', 'Wrap-up')]


def card(pw, mode):
    b = hv.launch(pw)
    ctx = b.new_context(viewport={'width': 1440, 'height': 810}, device_scale_factor=4 / 3)
    ctx.route('**/*', lambda route, req: route.fulfill(status=200, content_type='text/html', body=CARD) if '/card/' in req.url else route.abort())
    ctx.add_init_script(hv.CURSOR_JS)
    pg = ctx.new_page(); r = hv.Rec(ctx, pg, mode); r.mx, r.my = 1500, 900
    pg.goto('https://app.test/card/' + mode); pg.wait_for_timeout(600)
    r.start()
    if mode == 'intro':
        r.wait(0.3)
        r.beat('i1', lambda: pg.evaluate('step(0)'))
        r.beat('i2', lambda: pg.evaluate('step(1)'))
        r.wait(0.8)
    else:
        pg.evaluate('step(0)'); r.wait(1.0)
        r.beat('e1', lambda: pg.evaluate('step(1)'))
        r.beat('e2', lambda: pg.evaluate('step(2)'))
        r.wait(1.5)
    r.snap('end'); r.stop(tail=0.5); b.close()


# keep dialogs clear of the burned-in captions (bottom ~170 px of 1080)
FRAME_CSS = "addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');s.textContent='.mo{align-items:flex-start!important;padding-top:22px!important}.md{max-height:calc(100vh - 170px)!important}';document.head.appendChild(s);});"


def app(pw, ns, name, extra=''):
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, session=hv.session_script(extra=extra))
    ctx.add_init_script(FRAME_CSS)
    pg = ctx.new_page()
    pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.wait_for_timeout(800)
    r = hv.Rec(ctx, pg, name)
    return b, pg, r


def mclick(r, loc, **kw):
    """Click a button inside a scrolling dialog: bring it fully into the dialog's view first."""
    loc.wait_for(state='visible', timeout=15000)
    loc.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'nearest'})"); r.wait(0.6)
    r.click(loc, **kw)


def close_modals(r, pg):
    while pg.locator('.md').count():
        btn = pg.locator('.md').last.get_by_role('button', name=re.compile('^(Close|Cancel|Back)$'))
        if btn.count(): mclick(r, btn.last, after=0.3)
        else: r.click(pg.locator('.mo').last, fx=0.6, fy=0.85, after=0.3)   # dialogs without a button close on the backdrop


# ------------------------------------------------------------------------------------------------ HACCP
def s_haccp(pw):
    ns = setup(); apply_dump(ns, ['hx_haccp_plans', 'hx_haccp_monitoring', 'hx_haccp_verifications'])
    b, pg, r = app(pw, ns, 'haccp', 'localStorage.setItem("hx_hptab","plans");')
    r.start()
    def h1():
        r.wait(0.8); r.click(menu(pg, 'HACCP')); pg.wait_for_selector('td >> text=HP-002'); r.wait(0.4)
        r.point(pg.locator('tr', has_text='HP-001'), fx=0.2)
    r.beat('h1', h1)
    def h2():
        cards = pg.locator('.stat, .kpi, .card').filter(has_text=re.compile('Active plans', re.I))
        for t in ('Active plans', 'HACCP certified', 'Out of limits', 'Records to verify', 'Reanalysis due'):
            r.point(pg.get_by_text(t, exact=False).first, fx=0.4, fy=1.6); r.wait(0.9)
    r.beat('h2', h2)
    md = pg.locator('.md')
    def h3():
        r.click(pg.get_by_role('button', name='+ HACCP plan')); pg.wait_for_selector('.md')
        r.type(field(md, 'Plan name'), 'BHO extraction')
        r.select(field(md, 'Covers batch type'), value='butane_extraction')
        r.point(md.get_by_text('Still needed before validation').first, fx=0.3); r.snap('needed')
    r.beat('h3', h3)
    def h4():
        mclick(r, md.get_by_role('button', name='Start from a draft for this batch type')); r.wait(0.6)
        r.point(field(md, 'Ingredients'), fx=0.3); r.wait(0.6)
        r.type(field(md, 'Shelf life / date'), '6 months from the run date', delay=30, clear=True)
        r.snap('product')
    r.beat('h4', h4)
    def h5():
        r.click(md.locator('.tabs button', has_text='2. Process flow')); r.wait(0.6)
        svg = md.locator('svg').last
        r.point(svg, fx=0.5, fy=0.3); r.wait(0.6); r.wheel(320); r.wait(0.4); r.snap('flow')
    r.beat('h5', h5)
    def h5b():
        r.click(md.locator('.tabs button', has_text='4. CCPs')); r.wait(0.6)
        r.point(field(md, 'Critical limit'), fx=0.3); r.wait(0.5); r.point(field(md, 'Corrective action'), fx=0.3); r.snap('ccps')
    r.beat('h5b', h5b)
    def h6():
        r.click(md.locator('.tabs button', has_text='5. Validation')); r.wait(0.5)
        r.point(field(md, 'How the plan was validated'), fx=0.3); r.wait(2.0)
        mclick(r, md.get_by_role('button', name='Save draft')); pg.wait_for_selector('.msg >> text=Saved BHO extraction'); r.wait(0.5)
        if pg.locator('.md').count(): close_modals(r, pg)
        r.smooth_top(); r.point(pg.locator('tr', has_text='HP-003'), fx=0.2); r.snap('saved')
    r.beat('h6', h6)
    def h7():
        r.click(pg.get_by_role('button', name='+ CCP check')); pg.wait_for_selector('.md')
        r.select(field(md, 'HACCP plan'), index=0)
        r.select(field(md, 'CCP'), label='CCP 2 Water activity')
        r.select(field(md, 'Batch'), value='b2'); r.wait(0.3); r.snap('ccp1')
    r.beat('h7', h7)
    def h8():
        r.type(field(md, 'Measured value'), 'aw 0.89')
        r.select(field(md, 'Within the critical limit?'), value='no'); r.wait(0.3)
        r.type(field(md, 'Corrective action taken'), 'Trays back to the curing room for 12 h; re-test', delay=24)
        r.select(field(md, 'Product'), value='held')
        r.type(field(md, 'Checked by'), 'Maria Lopez', clear=True); r.snap('ccp2')
    r.beat('h8', h8)
    def h9():
        mclick(r, md.get_by_role('button', name='Record', exact=True)); pg.wait_for_selector('.msg >> text=OUT of limits'); r.wait(0.4); r.snap('recorded')
    r.beat('h9', h9)
    def h10():
        r.click(pg.locator('.tabs button', has_text='CCP monitoring')); pg.wait_for_selector('td >> text=aw 0.89'); r.wait(0.4)
        r.select(pg.locator('select').filter(has=pg.locator('option[value=unver]')).first, value='unver')
        r.wait(0.5); r.snap('filter')
        row = pg.locator('tr', has_text='50.9 g')
        r.click(row.get_by_role('button', name='Verify')); r.wait(0.8); r.snap('verified')
    r.beat('h10', h10)
    def h11():
        r.point(pg.locator('tr', has_text='aw 0.89').get_by_role('button', name='Deviation'), fx=0.5); r.snap('dev')
    r.beat('h11', h11)
    r.stop(); b.close()


def go(r, pg, name, wait):
    r.click(menu(pg, name), after=0.05); pg.evaluate('window.scrollTo(0,0)')   # short pages would otherwise render scrolled off (blank)
    pg.wait_for_selector(wait); r.wait(0.3); r.smooth_top()


def row_b(pg, title):
    return pg.locator('tr', has=pg.locator('b', has_text=re.compile('^' + re.escape(title) + '$')))


# ------------------------------------------------------------------------------------------------ Risk Register
def s_risk(pw):
    ns = setup(); seed_all(ns)   # full seed so the Dashboard seen in passing matches the rest of the video
    b, pg, r = app(pw, ns, 'risk'); md = pg.locator('.md')
    r.start()
    def r1():
        r.wait(0.5); go(r, pg, 'Risk Register', 'text=Heat map (current rating)')
        r.point(pg.get_by_text('Risks on the register').first, fx=0.3, fy=2); r.wait(1.0)
        r.point(row_b(pg, 'Microbial growth in infused edibles').locator('td').nth(1), fx=0.4)
    r.beat('r1', r1)
    def r2():
        hm = pg.get_by_text('Heat map (current rating)').first
        r.point(hm, fx=0.5, fy=6); r.wait(1.2); r.point(hm, fx=0.75, fy=4); r.wait(1.2)
        r.point(pg.get_by_text('By category').first, fx=0.3, fy=3); r.wait(0.8); r.point(pg.get_by_text('CSQ 1.9').first)
    r.beat('r2', r2)
    def r3():
        r.click(pg.get_by_role('button', name='+ Risk')); pg.wait_for_selector('.md')
        r.type(field(md, 'Risk'), 'Glass breakage near the filling line', delay=30)
        r.type(field(md, 'Hazard - what could go wrong'), 'Glass fragments in vape cartridges', delay=26)
        r.type(field(md, 'Root cause - why it could happen'), 'Glass jars of distillate opened at the line', delay=24)
        r.select(field(md, 'Found through'), value='deviation')
        r.type(md.locator('input[placeholder="e.g. DEV-2026-004"]'), 'DEV-2026-031'); r.snap('form1')
    r.beat('r3', r3)
    def r4():
        r.select(field(md, 'Likelihood'), value='4'); r.wait(0.4)
        r.select(field(md, 'Severity'), value='4'); r.wait(0.6)
        badge = md.get_by_text(re.compile(r'^(Critical|CRITICAL)')).first
        if badge.count(): r.point(badge)
        r.snap('rating')
    r.beat('r4', r4)
    def r5():
        r.type(field(md, 'Immediate action'), 'Open jars in the prep room only; glass check at changeover', delay=20)
        r.fill(field(md, 'Permanent fix by'), '2026-12-01'); r.snap('form2')
        mclick(r, md.get_by_role('button', name='Save', exact=True)); pg.wait_for_selector('.msg >> text=Saved risk RK-013'); r.wait(0.3)
        r.smooth_top(); r.point(pg.locator('.msg').first, fx=0.2); r.snap('saved')
    r.beat('r5', r5)
    def r6():
        r.click(row_b(pg, 'Residual solvent above the limit').get_by_role('button', name='Review')); pg.wait_for_selector('.md')
        r.point(field(md, 'Likelihood'), fx=0.3); r.wait(0.4)
        ck = md.locator('label.ck', has_text='Controls are in place and working')
        if ck.count(): r.point(ck.first, fx=0.05)
        r.type(field(md, 'Notes'), 'Purge records Jul-Oct reviewed; one failed COA. Purge extended per CC-2026-002.', delay=16); r.snap('review')
    r.beat('r6', r6)
    def r7():
        mclick(r, md.get_by_role('button', name='Record review')); pg.wait_for_selector('.msg >> text=Review recorded'); r.wait(0.3)
        r.smooth_top(); r.point(pg.get_by_role('button', name='Suggested risks')); r.snap('reviewed')
    r.beat('r7', r7)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------------------ Change Control
def s_change(pw):
    ns = setup(); seed_all(ns)   # full seed so the Dashboard seen in passing matches the rest of the video
    b, pg, r = app(pw, ns, 'change'); md = pg.locator('.md')
    r.start()
    def c1():
        r.wait(0.5); go(r, pg, 'Change Control', 'td >> text=CC-2026-003')
        r.point(pg.get_by_text('Waiting for approval').first, fx=0.3, fy=2); r.wait(1.5)
        r.point(pg.locator('tr', has_text='CC-2026-004').locator('td').nth(2), fx=0.3)
    r.beat('c1', c1)
    def c2():
        for n in ('CC-2026-004', 'CC-2026-003', 'CC-2026-002'):
            r.point(pg.locator('tr', has_text=n).get_by_text(re.compile('^(Requested|Approved|Implemented)$', re.I)).first); r.wait(0.5)
        r.point(pg.get_by_text('Next step', exact=True).first); r.wait(0.4)
        r.point(pg.locator('tr', has_text='CC-2026-003').get_by_text('1 action open', exact=False).first, fx=0.3)
    r.beat('c2', c2)
    def c3():
        r.smooth_top(); r.click(pg.get_by_role('button', name='+ Change')); pg.wait_for_selector('.md')
        r.type(field(md, 'Change'), 'Add a mango flavor to the 10-pack gummies', delay=28)
        r.select(field(md, 'Type'), value='product'); r.wait(0.3)
        r.type(field(md, 'What changes'), 'New natural mango flavor and orange color', delay=24)
        r.type(field(md, 'Why'), 'Dispensary demand; replaces the peach SKU', delay=24); r.snap('form1')
    r.beat('c3', c3)
    def c4():
        for k in ('Allergens', 'Labels and packaging', 'Product specs / formulation', 'HACCP plan / flow diagram'):
            r.click(md.locator('label.ck', has_text=re.compile('^' + re.escape(k) + '$')).first, fx=0.06, after=0.25)
        r.type(md.locator('input[placeholder="What the trial must show"]'), '3 batches within potency spec, aw below 0.85', delay=22); r.snap('form2')
    r.beat('c4', c4)
    def c5():
        mclick(r, md.get_by_role('button', name='+ Action'))
        r.type(md.locator('input[placeholder="Action"]').last, 'Approve the flavor supplier', delay=26); r.type(md.locator('input[placeholder="Who"]').last, 'Lee Park')
        mclick(r, md.get_by_role('button', name='+ Action'))
        r.type(md.locator('input[placeholder="Action"]').last, 'New label with flavor and allergens', delay=26); r.type(md.locator('input[placeholder="Who"]').last, 'Marcus Bell'); r.snap('form3')
        mclick(r, md.get_by_role('button', name='Request change')); pg.wait_for_selector('.msg >> text=Requested CC-2026-006'); r.wait(0.3)
        r.smooth_top(); r.point(pg.locator('tr', has_text='CC-2026-006').locator('td').first); r.snap('requested')
    r.beat('c5', c5)
    def c6():
        r.click(pg.locator('tr', has_text='CC-2026-006').get_by_role('button', name='Approve')); pg.wait_for_selector('.md'); r.wait(0.6)
        r.type(md.locator('input[placeholder="Conditions, or why it is acceptable"]'), 'Trial batches must pass before the SKU goes live', delay=22); r.snap('approve')
        mclick(r, md.get_by_role('button', name='Approve', exact=True)); pg.wait_for_timeout(900)
        if pg.locator('.md').count(): close_modals(r, pg)
        r.smooth_top(); r.point(pg.locator('tr', has_text='CC-2026-006').get_by_text(re.compile('^Approved$', re.I)).first); r.snap('approved')
    r.beat('c6', c6)
    def c7():
        r.click(pg.locator('tr', has_text='CC-2026-003').get_by_role('button', name='Work')); pg.wait_for_selector('.md'); r.wait(0.5)
        tr = md.locator('label.ck', has_text='Training given before use')
        r.wait(0.8); r.click(tr.first, fx=0.03); r.wait(0.5)
        r.point(md.locator('label.ck', has_text='HACCP plan reviewed').first, fx=0.3); r.wait(0.6)
        r.point(md.get_by_text('Told on', exact=False).first, fx=0.3, fy=2)
        r.snap('work')
    r.beat('c7', c7)
    def c8():
        r.point(md.get_by_text('Before it can be implemented').first, fx=0.3); r.wait(1.5)
        r.point(md.get_by_role('button', name='Mark implemented')); r.wait(1.2); r.snap('blocked')
        mclick(r, md.get_by_role('button', name='Save progress')); pg.wait_for_timeout(800)
        if pg.locator('.md').count(): close_modals(r, pg)
    r.beat('c8', c8)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------------------ Org Chart
def s_org(pw):
    ns = setup(); seed_all(ns)   # full seed so the Dashboard seen in passing matches the rest of the video
    b, pg, r = app(pw, ns, 'org'); md = pg.locator('.md')
    r.start()
    def o1():
        r.wait(0.5); go(r, pg, 'Org Chart', '.card svg rect'); r.wait(0.3)
        svg = pg.locator('.card svg').first
        r.point(svg.get_by_text('General Manager').first); r.wait(1.5)
        r.point(svg.get_by_text('Quality Manager').first); r.wait(1.5)
        r.point(svg.get_by_text('Vacant').first)
    r.beat('o1', o1)
    def o2():
        r.point(pg.get_by_text('Key CSQ roles').first, fx=0.3, fy=2); r.wait(1.5)
        r.point(pg.get_by_text('Safety, quality and CSQ roles').first, fx=0.3); r.snap('roles')
    r.beat('o2', o2)
    def o3():
        r.click(row_b(pg, 'Maintenance Technician').get_by_role('button', name='Edit')); pg.wait_for_selector('.md'); r.wait(0.4)
        r.type(field(md, 'Person'), 'Dana Brooks', clear=True); r.wait(0.4)
        r.point(field(md, 'Backup'), fx=0.3); r.wait(0.5); r.point(field(md, 'Functions and responsibilities'), fx=0.3); r.snap('edit')
    r.beat('o3', o3)
    def o4():
        mclick(r, md.get_by_role('button', name='Save', exact=True)); pg.wait_for_timeout(900)
        if pg.locator('.md').count(): close_modals(r, pg)
        r.smooth_top(); r.point(pg.locator('.card svg').first.get_by_text('Dana Brooks').first); r.snap('saved')
    r.beat('o4', o4)
    def o5():
        r.point(row_b(pg, 'Quality Manager').get_by_role('button', name='+ Under')); r.wait(2.2)
        r.smooth_top(); r.point(pg.get_by_role('button', name='Print org chart')); r.snap('print')
    r.beat('o5', o5)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------------------ Quality Objectives
def s_obj(pw):
    ns = setup(); seed_all(ns)   # full seed so the Dashboard seen in passing matches the rest of the video
    b, pg, r = app(pw, ns, 'obj'); md = pg.locator('.md')
    r.start()
    def q1():
        r.wait(0.5); go(r, pg, 'Quality Objectives', 'text=SOP-QA-001'); r.wait(0.3)
        r.point(pg.get_by_text('SOP-QA-001').first, fx=0.3); r.wait(2.0)
        r.point(pg.get_by_text('counted from Hendrix').first, fx=0.6)
    r.beat('q1', q1)
    card = pg.locator('.card', has=pg.locator('b', has_text=re.compile('^CAPAs closed on time$'))).first
    def q2():
        r.point(card.locator('svg').first, fx=0.3); r.wait(1.2); r.point(card.locator('svg').first, fx=0.55); r.wait(1.2)
        r.point(pg.get_by_text('Results due').first, fx=0.3, fy=2)
    r.beat('q2', q2)
    def q3():
        r.click(card.get_by_role('button', name=re.compile('^Record'))); pg.wait_for_selector('.md')
        md.locator('text=3 of 4 CAPAs closed on time').wait_for(); r.wait(0.4)
        r.point(md.get_by_text('3 of 4 CAPAs closed on time').first, fx=0.3); r.snap('result')
    r.beat('q3', q3)
    def q4():
        r.type(field(md, 'Action to get back on target'), 'Weekly CAPA due-date review in the Monday meeting', delay=22)
        mclick(r, md.get_by_role('button', name='Record result')); pg.wait_for_selector('.msg >> text=target missed'); r.wait(0.3)
        r.smooth_top(); r.point(pg.locator('.msg').first, fx=0.2); r.snap('recorded')
    r.beat('q4', q4)
    def q5():
        r.click(pg.get_by_role('button', name='+ Objective')); pg.wait_for_selector('.md'); r.wait(0.3)
        r.type(field(md, 'Objective'), 'Line clearance before every batch', delay=26)
        r.select(field(md, 'Category'), value='food_safety')
        r.select(field(md, 'Measured by'), value='line_clear'); r.wait(0.3)
        r.type(field(md, 'Target'), '100')
        r.fill(field(md, 'Reach by'), '2026-12-31'); r.snap('newobj')
        mclick(r, md.get_by_role('button', name='Save', exact=True)); pg.wait_for_timeout(900)
        if pg.locator('.md').count(): r.snap('objerr'); close_modals(r, pg)
        r.smooth_top()
    r.beat('q5', q5)
    def q6():
        c = pg.locator('.card', has=pg.locator('b', has_text='On-time delivery to dispensaries')).first
        r.point(c, fx=0.3, fy=0.15); r.snap('q6')
    r.beat('q6', q6)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------------------ Management Review
NOTES = [('Actions from the last review', 'Second hardware supplier still open: carried over to 12/31.'),
         ('Complaints and customer feedback', 'Quality complaints down; light pre-rolls fixed by CC-2026-004.'),
         ('Internal, external and regulatory audits', 'Internal audit: 1 minor finding open. DCR: no findings.'),
         ('Deviations and corrective actions (CAPA)', 'Critical deviation 10/22 under CAPA-2026-019.'),
         ('Risks and opportunities', 'Residual solvent risk stays high until verified.'),
         ('CSQ conformance', '6 partial clauses to close before the Level 3 audit.'),
         ('Changes that could affect the system', 'Molds and purge change reviewed against HACCP.'),
         ('Resources (people, equipment, facility, budget)', 'Second extraction tech approved.')]


def s_review(pw):
    ns = setup(); seed_all(ns)
    b, pg, r = app(pw, ns, 'review'); md = pg.locator('.md')
    r.start()
    def m1():
        r.wait(0.5); go(r, pg, 'Management Review', 'td >> text=MR-2025-001'); r.wait(0.3)
        for t in ('Last review', 'Next review due', 'Open actions', 'Minutes shared'):
            r.point(pg.get_by_text(t, exact=True).first, fx=0.3, fy=2); r.wait(0.8)
    r.beat('m1', m1)
    def m2():
        r.click(pg.get_by_role('button', name='+ Management review')); pg.wait_for_selector('.md'); md.locator('text=Filled from Hendrix records').first.wait_for(); r.wait(0.4)
        r.point(md.get_by_text('Filled from Hendrix records').first, fx=0.3); r.wait(0.8)
        r.point(field(md, 'Period from'), fx=0.3); r.snap('new')
    r.beat('m2', m2)
    def inp(k): return md.locator('.card', has=pg.locator('b', has_text=re.compile('^' + re.escape(k) + r'( \*)?$'))).first
    def m3():
        r.type(field(md, 'Attendees'), 'Sam Salari (GM), Lee Park (QA), Maria Lopez, Marcus Bell', delay=18)
        c = inp(NOTES[0][0]); r.point(c.locator('textarea').nth(0), fx=0.3); r.wait(0.6)
        r.type(c.locator('textarea').nth(1), NOTES[0][1], delay=18); r.snap('input1')
    r.beat('m3', m3)
    def m4():
        for k, v in NOTES[1:]: r.type(inp(k).locator('textarea').nth(1), v, delay=7)
        r.snap('inputs')
    r.beat('m4', m4)
    def m5():
        r.type(field(md, 'Decisions and conclusions'), 'The system is suitable, adequate and effective.', delay=10)
        mclick(r, md.get_by_role('button', name='+ Action'))
        r.type(md.locator('input[placeholder="Action"]').last, 'Hire a second extraction technician', delay=18); r.type(md.locator('input[placeholder="Who"]').last, 'Sam Salari')
        r.point(field(md, 'Next review'), fx=0.3); r.snap('decisions')
    r.beat('m5', m5)
    def m6():
        mclick(r, md.get_by_role('button', name='Sign as held')); pg.wait_for_selector('.msg >> text=Signed management review MR-2026-001.'); r.wait(0.3)
        if pg.locator('.md').count(): close_modals(r, pg)
        r.smooth_top(); r.point(pg.locator('tr', has_text='MR-2026-001').locator('td').first, fx=0.3); r.snap('signed')
    r.beat('m6', m6)
    def m7():
        r.click(pg.locator('tr', has_text='MR-2026-001').get_by_role('button', name='Follow-up')); pg.wait_for_selector('.md'); r.wait(0.4)
        r.click(md.locator('input[type=checkbox][title=Done]').last)
        r.type(field(md, 'Minutes shared with'), 'All managers; summary in the break room', delay=18)
        r.fill(field(md, 'Shared on'), TODAY); r.snap('follow')
        mclick(r, md.get_by_role('button', name='Save', exact=True)); pg.wait_for_selector('.msg >> text=Saved MR-2026-001.'); r.wait(0.3)
        if pg.locator('.md').count(): close_modals(r, pg)
        r.smooth_top()
    r.beat('m7', m7)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------------------ Verification Schedule
def s_verif(pw):
    ns = setup(); seed_all(ns)
    b, pg, r = app(pw, ns, 'verif'); md = pg.locator('.md')
    r.start()
    def v1():
        r.wait(0.5); go(r, pg, 'Verification Schedule', 'td >> text=VS-013'); r.wait(0.3)
        r.point(pg.get_by_text('Scheduled activities').first, fx=0.3, fy=2); r.wait(1.0)
        r.point(row_b(pg, 'Sanitation records reviewed and signed').locator('b').first, fx=0.4)
    r.beat('v1', v1)
    def v2():
        r.point(pg.get_by_text('from Sanitation log').first, fx=0.4); r.wait(1.5)
        r.point(pg.get_by_text(re.compile('^Overdue', re.I)).first, fx=0.5)
    r.beat('v2', v2)
    def v2b():
        r.click(row_b(pg, 'Risk register review').get_by_role('button', name='Edit')); pg.wait_for_selector('.md'); r.wait(0.4)
        r.point(field(md, 'Who'), fx=0.3); r.wait(0.6); r.point(field(md, 'Every (days)'), fx=0.3); r.wait(0.6)
        r.point(field(md, 'Last date comes from'), fx=0.3); r.snap('edit'); r.wait(1.5)
        close_modals(r, pg)
    r.beat('v2b', v2b)
    def v3():
        row = row_b(pg, 'Labels checked against the batch')
        r.point(row.locator('b').first, fx=0.3); r.wait(0.6)
        r.click(row.get_by_role('button', name='Record')); pg.wait_for_selector('.md'); r.wait(0.3)
        r.type(field(md, 'By'), 'Priya Shah', clear=True)
        r.select(field(md, 'Result'), value='issues'); r.snap('form1')
    r.beat('v3', v3)
    def v4():
        r.type(field(md, 'Findings'), 'CART-2610-008 label lists the old terpene blend', delay=20)
        r.type(field(md, 'Action taken'), 'Template fixed; 120 labels reprinted before release', delay=20); r.snap('form2')
        mclick(r, md.get_by_role('button', name='Record', exact=True)); pg.wait_for_selector('.msg >> text=Recorded: Labels checked against the batch.'); r.wait(0.3)
        r.point(row_b(pg, 'Labels checked against the batch').locator('td').nth(5), fx=0.4); r.snap('recorded')
    r.beat('v4', v4)
    def v5():
        r.click(row_b(pg, 'Labels checked against the batch').get_by_role('button', name='History')); pg.wait_for_selector('.md'); md.locator('text=Action: Template corrected').wait_for(); r.wait(0.4)
        r.point(md.get_by_role('button', name='Deviation').last); r.snap('history')
    r.beat('v5', v5)
    def v6():
        r.wait(0.6); close_modals(r, pg)
        r.point(pg.get_by_text('from Calibrations', exact=False).first, fx=0.4)
    r.beat('v6', v6)
    r.stop(); b.close()


SC = {'intro': lambda pw: card(pw, 'intro'), 'end': lambda pw: card(pw, 'end'), 'haccp': s_haccp, 'risk': s_risk, 'change': s_change, 'org': s_org,
      'obj': s_obj, 'review': s_review, 'verif': s_verif}
if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['build']:
        hv.build(SCENES, V + 'series/03 - HACCP and the management system.mp4')
    else:
        with sync_playwright() as pw:
            for a in args: SC[a](pw)
