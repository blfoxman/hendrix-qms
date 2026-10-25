# Video 04 - Suppliers, materials and traceability. Usage: python3 make.py [scene ...] [build]
from common import *
from playwright.sync_api import sync_playwright

OUTDIR = os.path.abspath(HERE + '/..')
FINAL = OUTDIR + '/04 - Suppliers, materials and traceability.mp4'
SCENES = [('intro', 'Introduction'), ('suppliers', 'Suppliers'), ('receiving', 'Receiving'), ('holds', 'Hold and Release'),
          ('shipping', 'Shipping'), ('trace', 'Traceability and Recall'), ('end', 'Wrap-up')]
CARD = open(HERE + '/card.html').read()
PDF = lambda name: {'name': name, 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4\n%%EOF'}


def ripple(r):
    r.page.evaluate('([x,y])=>window.__ripple&&window.__ripple(x,y)', [r.mx, r.my]); r.wait(0.3)


def md_last(pg): return pg.locator('.md').last


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
        r.wait(0.8)
    else:
        pg.evaluate('step(0)'); r.wait(0.8)
        r.beat('w1')
        r.beat('w2', lambda: (pg.evaluate('step(1)'), r.wait(4.5), pg.evaluate('step(2)')))
        r.wait(1.2)
    r.snap('end'); r.stop(tail=0.5); b.close()


# ------------------------------------------------------------------ Suppliers
def scene_suppliers(pw):
    ns = setup(); T = ns['T']
    b = hv.launch(pw)
    ctx, pg, r = open_app(b, ns, 'suppliers')
    r.start()

    def s1():
        r.click(nav(pg, 'Suppliers')); pg.wait_for_selector('.card >> text=Futurola USA'); r.wait(0.5)
        for k in ('Approved', 'Pending', 'Reviews overdue', 'Credentials expiring'):
            r.point(pg.locator('.card .k', has_text=re.compile('^' + k)).first, 0.4, dur=0.45); r.wait(0.35)
        r.snap('list')
    r.beat('s1', s1)

    def s1b():
        r.point(pg.locator('.card', has_text='Futurola USA').first, 0.02, 0.5); r.wait(0.6)
        r.point(pg.locator('.card', has_text='Rapid Label & Print').first, 0.02, 0.5); r.wait(0.6)
        r.point(pg.locator('.card', has_text='Prairie Packaging Group').first, 0.02, 0.5); r.wait(0.6)
        r.point(pg.locator('.card', has_text='Valley Vape Supply').first, 0.02, 0.5); r.snap('edges')
    r.beat('s1b', s1b)

    def s2():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='+ Add supplier')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.type(field(md, 'Supplier name'), 'Heartland Glass & Jars', delay=30)
        r.select(field(md, 'Category / type'), value='Packaging')
        r.select(field(md, 'Risk'), value='medium')
        r.type(field(md, 'Products / services supplied'), 'Child-resistant glass jars, 3.5 g and 7 g', delay=18)
        r.snap('form1')
    r.beat('s2', s2)

    def s3():
        md = pg.locator('.md')
        r.type(field(md, 'Specifications the supplier must meet'), 'Food-grade glass; child-resistant lid; COA with every lot', delay=14)
        r.type(field(md, 'Contact name'), 'Erin Brooks', delay=24)
        r.type(field(md, 'Contact email'), 'erin@heartlandglass.example', delay=14)
        r.click(md.get_by_role('button', name='+ Add credential'))
        cr = md.locator('div.grid', has=pg.locator('input[placeholder=Number]')).last
        r.select(cr.locator('select'), value='Food-grade / GMP certificate')
        r.type(cr.locator('input[placeholder=Number]'), 'FG-10442', delay=40)
        r.fill(cr.locator('input[type=date]'), '2027-06-30')
        r.point(cr.get_by_text('File').first); ripple(r)
        cr.locator('input[type=file]').set_input_files(PDF('food-grade-certificate.pdf')); pg.wait_for_selector('.md >> text=\U0001f4ce'); r.wait(0.3)
        r.snap('form2')
    r.beat('s3', s3)

    def s4():
        md = pg.locator('.md')
        r.click(md.get_by_role('button', name='Add supplier', exact=True)); pg.wait_for_selector('.md >> text=Credentials'); r.wait(0.5)
        r.point(md_last(pg).get_by_text(re.compile('^Pending', re.I)).first, 0.3); r.snap('new')
    r.beat('s4', s4)

    def s5():
        md = md_last(pg)
        r.click(md.get_by_role('button', name='Approve', exact=True)); pg.wait_for_selector('.md >> text=Approval based on'); r.wait(0.3)
        ap = md_last(pg)
        r.point(ap.locator('textarea').first, 0.3); r.wait(0.4)
        r.click(ap.get_by_role('button', name='Approve supplier')); pg.wait_for_selector('text=Write what the approval is based on.'); r.wait(0.2)
        r.point(ap.get_by_text('Write what the approval is based on.').first, 0.3); r.snap('blank')
    r.beat('s5', s5)

    def s6():
        ap = md_last(pg)
        r.type(ap.locator('textarea').first, 'Questionnaire, food-grade certificate and COA reviewed; trial lot passed inspection', delay=12)
        r.point(field(ap, 'Next review'), 0.3); r.wait(0.4)
        r.click(ap.get_by_role('button', name='Approve supplier')); pg.wait_for_selector('text=Approval based on', state='detached'); r.wait(0.6)
        r.snap('approved')
        mdx = md_last(pg)
        if mdx.count():
            r.point(mdx.get_by_text('Sam Salari').first, 0.3)
    r.beat('s6', s6)

    def s7():
        close_modals(r, pg)
        c = pg.locator('.card', has_text='Ozark Pest Solutions').first
        r.point(c.get_by_text('Review overdue').first, 0.4); r.wait(0.6)
        r.click(c, fx=0.3, fy=0.3); pg.wait_for_selector('.md >> text=Credentials'); r.wait(0.3)
        r.click(md_last(pg).get_by_role('button', name='Record review')); pg.wait_for_selector('.md >> text=Review date'); r.snap('review')
    r.beat('s7', s7)

    def s8():
        md = md_last(pg)
        r.select(field(md, 'Rating'), value='Satisfactory')
        r.select(field(md, 'Result'), value='Keep approved')
        r.type(field(md, 'Notes'), '12 monthly reports on file; applicator license current', delay=14)
        r.click(md.get_by_role('button', name='Save review')); pg.wait_for_selector('text=Review date', state='detached'); r.wait(0.5)
        d = md_last(pg)
        r.point(d.get_by_text('12 monthly reports on file').first, 0.3); r.wait(0.5)
        r.point(d.get_by_text('2027-10-24').first, 0.3); r.snap('reviewed')
    r.beat('s8', s8)

    def s9():
        close_modals(r, pg); r.smooth_top()
        r.point(pg.get_by_role('button', name='Approved supplier list'), 0.5); r.snap('tip')
    r.beat('s9', s9)
    r.stop(); b.close()

# ------------------------------------------------------------------ Receiving (+ Inventory)
def scene_receiving(pw):
    ns = setup(); T = ns['T']
    b = hv.launch(pw)
    ctx, pg, r = open_app(b, ns, 'receiving')
    r.start()

    def r1():
        r.click(nav(pg, 'Receiving')); pg.wait_for_selector('tr >> text=RCV-2026-018'); r.wait(0.5)
        for k in ('In quarantine', 'Missing COA'):
            r.point(pg.locator('.card .k', has_text=re.compile('^' + k)).first, 0.4, dur=0.45); r.wait(0.5)
        row = pg.locator('tr', has_text='RCV-2026-017')
        hdr = pg.locator('thead th')
        for i in range(hdr.count()):
            if hdr.nth(i).inner_text().strip().lower() in ('coa', 'inspection', 'status'):
                r.point(row.locator('td').nth(i), 0.4, dur=0.4); r.wait(0.4)
        r.snap('list')
    r.beat('r1', r1)

    def r2():
        r.click(pg.get_by_role('button', name='+ Receive lot')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.select(field(md, 'Supplier'), value='s-mdp'); r.wait(0.5)
        r.point(md.get_by_text(re.compile('Full-panel COA from ISO 17025 lab')).first, 0.3); r.snap('sup')
    r.beat('r2', r2)

    def r3():
        md = pg.locator('.md')
        r.type(field(md, 'Item received'), 'THC distillate', delay=30)
        r.select(field(md, 'Category'), value='Distillate / extract')
        r.type(field(md, 'Quantity'), '500', delay=60)
        r.select(field(md, 'Unit'), value='g')
        r.type(field(md, 'Supplier lot #'), 'MDP-DST-1019', delay=30)
        r.fill(field(md, 'Expiry / best before'), '2027-10-15')
        r.type(field(md, 'Storage location'), 'Quarantine fridge Q2', delay=22)
        r.snap('form1')
    r.beat('r3', r3)

    def r4():
        md = pg.locator('.md')
        for ck in md.locator('label.ck').all():
            r.click(ck, fx=0.03 if (ck.bounding_box() or {'width': 0})['width'] > 100 else 0.5, after=0.1)
        md.locator('input[type=file]').first.set_input_files(PDF('COA MDP-DST-1019.pdf'))
        pg.wait_for_selector('.md >> text=COA MDP-DST-1019.pdf'); r.point(md.get_by_text('COA MDP-DST-1019.pdf').first, 0.3); r.snap('form2')
    r.beat('r4', r4)

    def r5():
        md = pg.locator('.md')
        r.click(md.get_by_role('button', name='Receive into quarantine')); pg.wait_for_selector('text=RCV-2026-019'); r.wait(0.6)
        if pg.locator('.md').count():
            r.point(md_last(pg).get_by_text('RCV-2026-019').first, 0.3)
        else:
            r.point(pg.locator('tr', has_text='RCV-2026-019').locator('td').first, 0.4)
        r.snap('saved')
    r.beat('r5', r5)

    def r6():
        if not pg.locator('.md').count():
            r.click(pg.locator('tr', has_text='RCV-2026-019').first, fx=0.3); pg.wait_for_selector('.md >> text=Receiving inspection')
        r.click(md_last(pg).get_by_role('button', name='Accept', exact=True)); pg.wait_for_selector('.md >> text=Accept lot'); m2 = md_last(pg); r.wait(0.2)
        r.type(m2.locator('textarea').first, 'COA matches spec; seal intact, received cold.', delay=18)
        r.click(m2.get_by_role('button', name='Accept lot')); pg.wait_for_selector('.md >> text=Accept lot', state='detached'); r.wait(0.6); r.snap('accepted')
    r.beat('r6', r6)

    def r7():
        close_modals(r, pg)
        r.click(pg.locator('tr', has_text='RCV-2026-018').first, fx=0.3); pg.wait_for_selector('.md >> text=Receiving inspection'); r.wait(0.4)
        r.click(md_last(pg).get_by_role('button', name='Accept', exact=True)); pg.wait_for_selector('.md >> text=Accept lot'); r.wait(0.3)
        m2 = md_last(pg)
        r.point(m2.get_by_text(re.compile('^No COA or certificate')).first, 0.3); r.wait(0.8)
        r.point(m2.get_by_text(re.compile('^Not every receiving check')).first, 0.3); r.wait(0.8)
        r.point(m2.get_by_role('button', name='Accept lot'), 0.5); r.snap('nocoa')
    r.beat('r7', r7)

    def r8():
        close_modals(r, pg); r.smooth_top()
        r.click(pg.locator('.tabs button', has_text='Inventory')); pg.wait_for_selector('td >> text=98mm pre-roll cones'); r.wait(0.4)
        r.point(pg.get_by_text('Use first').first, 0.5); r.wait(0.6)
        r.point(pg.locator('tr', has_text='RCV-2026-009').locator('td').first, 0.4); r.snap('inv')
    r.beat('r8', r8)

    def r9():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='+ Record use')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.select(field(md, 'Lot'), value='l14'); pg.wait_for_selector('.md >> text=FIFO'); r.wait(0.3)
        r.point(md.get_by_text(re.compile('FIFO')).first, 0.3); r.wait(1.2)
        r.select(field(md, 'Lot'), value='l09'); r.snap('fifo')
    r.beat('r9', r9)

    def r10():
        md = pg.locator('.md')
        r.select(field(md, 'Used in batch'), value='b-pr2')
        r.type(field(md, 'Quantity'), '300', delay=60)
        r.type(field(md, 'Notes'), 'Line 2, first shift', delay=24)
        r.click(md.get_by_role('button', name='Record use')); pg.wait_for_selector('.md', state='detached'); r.wait(0.5)
        r.point(pg.locator('tr', has_text='PR-2026-1024').first.locator('td').first, 0.4); r.snap('used')
    r.beat('r10', r10)
    r.stop(); b.close()

# ------------------------------------------------------------------ Hold and Release
def scene_holds(pw):
    ns = setup(); T = ns['T']
    b = hv.launch(pw)
    ctx, pg, r = open_app(b, ns, 'holds')
    r.start()

    def h1():
        r.click(nav(pg, 'Hold and Release')); pg.wait_for_selector('.card >> text=HOLD-2026-007'); r.wait(0.5)
        r.point(pg.locator('.card .k', has_text=re.compile('^Open holds')).first, 0.4); r.wait(0.5)
        c = pg.locator('.card', has_text='HOLD-2026-006').last
        r.point(c, 0.3, 0.3); r.wait(0.5)
        r.point(c.get_by_text(re.compile(r'\d+ days?')).first, 0.4); r.snap('list')
    r.beat('h1', h1)

    def h2():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='+ Put on hold')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.select(field(md, 'What is held'), value='batch')
        r.select(field(md, 'Source'), value='Complaint')
        r.select(field(md, 'Batch'), value='b-gm'); r.snap('form1')
    r.beat('h2', h2)

    def h3():
        md = pg.locator('.md')
        r.type(field(md, 'Quantity held'), '1,150 units', delay=30)
        r.type(field(md, 'Held at (location)'), 'Vault cage V3', delay=24, clear=True)
        r.type(field(md, 'Reason'), 'Complaint: gummies sticking together in the jar. Hold pending retained-sample check.', delay=12)
        r.snap('form2')
        r.click(md.get_by_role('button', name='Put on hold'))
        pg.wait_for_selector('text=HOLD-2026-008'); r.wait(0.3)
    r.beat('h3', h3)

    def h4():
        close_modals(r, pg)
        c = pg.locator('.card', has_text='HOLD-2026-008').last
        r.point(c.get_by_text('HOLD-2026-008').first, 0.4); r.wait(0.6)
        r.point(c.get_by_text(re.compile('GM-2026-1003')).first, 0.4); r.snap('held')
    r.beat('h4', h4)

    def h5():
        r.click(pg.locator('.card', has_text='HOLD-2026-006').last, fx=0.3, fy=0.3); pg.wait_for_selector('.md')
        r.click(md_last(pg).get_by_role('button', name='Decide')); pg.wait_for_selector('.md >> text=Save decision'); m = md_last(pg)
        r.select(field(m, 'Decision'), value='released')
        r.type(field(m, 'Reason / evidence for the decision'), 'Lab suspects a sampling error', delay=10)
        r.click(m.get_by_role('button', name='Save decision')); pg.wait_for_selector('text=It cannot be released.'); r.wait(0.2)
        r.point(m.get_by_text(re.compile('failed test and no passing retest after it')).first, 0.3); r.snap('blocked'); r.wait(1.4)
    r.beat('h5', h5)

    def h6():
        close_modals(r, pg)
        r.click(pg.locator('.card', has_text='HOLD-2026-008').last, fx=0.3, fy=0.3); pg.wait_for_selector('.md')
        r.click(md_last(pg).get_by_role('button', name='Decide')); pg.wait_for_selector('.md >> text=Save decision'); m = md_last(pg)
        r.select(field(m, 'Decision'), value='released')
        r.type(field(m, 'Reason / evidence for the decision'), 'Retained samples checked: no defects found. Complaint not confirmed.', delay=12)
        r.click(m.get_by_role('button', name='Save decision')); pg.wait_for_selector('.md >> text=Save decision', state='detached'); r.wait(0.5); r.snap('released')
    r.beat('h6', h6)

    def h7():
        close_modals(r, pg)
        c = pg.locator('.card', has_text='HOLD-2026-008').last
        r.point(c, 0.3, 0.3); r.wait(0.6)
        r.point(c.get_by_text('Sam Salari').last, 0.4); r.wait(0.8)
        r.point(pg.locator('.card', has_text='HOLD-2026-007').last, 0.3, 0.3); r.snap('done')
    r.beat('h7', h7)
    r.stop(); b.close()


# ------------------------------------------------------------------ Shipping
def scene_shipping(pw):
    ns = setup(); T = ns['T']
    b = hv.launch(pw)
    ctx, pg, r = open_app(b, ns, 'shipping')
    r.start()

    def p1():
        r.click(nav(pg, 'Shipping')); pg.wait_for_selector('tr >> text=SHP-2026-033'); r.wait(0.5)
        row = pg.locator('tr', has_text='SHP-2026-032')
        r.point(row.locator('td').nth(2), 0.3); r.wait(0.5)
        r.point(row.locator('td').nth(3), 0.3); r.wait(0.5)
        r.point(pg.locator('tr', has_text='SHP-2026-033').get_by_text('Missing').first, 0.5); r.snap('list')
    r.beat('p1', p1)

    def p2():
        r.click(pg.get_by_role('button', name='+ New shipment')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.type(field(md, 'Customer'), 'Riverbend Cannabis Co.', delay=22)
        r.type(field(md, 'Customer license #'), 'DIS000291', delay=30)
        r.type(field(md, 'Destination address'), '15 River Rd, Cape Girardeau, MO', delay=14)
        r.type(field(md, 'State manifest #'), '0004472019', delay=30)
        r.type(field(md, 'Transporter'), 'Black Fox fleet', delay=22)
        r.type(field(md, 'Driver'), 'Chris Lane', delay=24)
        r.type(field(md, 'Vehicle'), 'Van MO-4KT-221', delay=22); r.snap('form1')
    r.beat('p2', p2)

    def p3():
        md = pg.locator('.md'); sels = md.locator('select').filter(has=pg.locator('option', has_text='(batch)'))
        r.select(sels.first, value='b-pr')
        r.type(md.locator('input[placeholder="Package tag"]').first, '1A4000000000000000021004', delay=14)
        r.type(md.locator('input[placeholder=Qty]').first, '400', delay=50)
        r.point(md.get_by_text('Test passed').first, 0.3); r.snap('row1')
    r.beat('p3', p3)

    def p4():
        md = pg.locator('.md'); sels = md.locator('select').filter(has=pg.locator('option', has_text='(batch)'))
        r.click(md.get_by_role('button', name='+ Add batch / package'))
        r.select(sels.nth(1), value='b-ct2'); pg.wait_for_selector('.md >> text=cannot ship'); r.wait(0.2)
        r.point(md.get_by_text(re.compile('cannot ship')).first, 0.3); r.wait(1.4); r.snap('row2')
        r.click(md.get_by_role('button', name='×').nth(1)); r.wait(0.3)
    r.beat('p4', p4)

    def p5():
        md = pg.locator('.md')
        r.point(md.get_by_text(re.compile('^Pre-load inspection')).first, 0.2); r.wait(0.3)
        cks = [c for c in md.locator('label.ck').all()]
        for c in cks:
            r.click(c, fx=0.03 if (c.bounding_box() or {'width': 0})['width'] > 100 else 0.5, after=0.1)
        r.snap('checks')
        r.click(md.get_by_role('button', name='Record shipment')); pg.wait_for_selector('tr >> text=SHP-2026-034'); r.wait(0.4)
        close_modals(r, pg)
        r.point(pg.locator('tr', has_text='SHP-2026-034').locator('td').first, 0.4); r.snap('saved')
    r.beat('p5', p5)

    def p6():
        r.click(pg.locator('tr', has_text='SHP-2026-033').first, fx=0.3); pg.wait_for_selector('.md >> text=Pre-load inspection'); r.wait(0.4)
        r.click(md_last(pg).get_by_role('button', name='Add manifest #')); m = md_last(pg)
        r.type(m.locator('textarea').first, '0004472001', delay=40)
        r.click(m.get_by_role('button', name='Save')); pg.wait_for_selector('text=Manifest saved.'); r.wait(0.3)
        if not pg.locator('.md').count():
            r.click(pg.locator('tr', has_text='SHP-2026-033').first, fx=0.3); pg.wait_for_selector('.md >> text=Pre-load inspection'); r.wait(0.3)
        d = md_last(pg)
        r.point(d.get_by_role('button', name='Mark delivered'), 0.5); r.wait(0.6)
        r.point(d.get_by_role('button', name='Record return'), 0.5); r.snap('detail')
    r.beat('p6', p6)
    r.stop(); b.close()

# ------------------------------------------------------------------ Traceability and Recall
def scene_trace(pw):
    ns = setup(); T = ns['T']
    b = hv.launch(pw)
    ctx = hv.new_context(b, ns, fixed=None, session=hv.session_script())
    ctx.clock.install(time=hv.FIXED_DAY); CLK['t0'] = time.time(); CLK['flow'] = True
    pg = ctx.new_page(); pg.goto(ns['BASE']); pg.wait_for_selector('.nav'); pg.add_style_tag(content=CAP_CSS); pg.wait_for_timeout(700)
    r = hv.Rec(ctx, pg, 'trace')
    r.start()

    def c1():
        r.click(nav(pg, 'Traceability and Recall')); pg.wait_for_selector('text=Type a received lot number'); r.wait(0.4)
        r.type(pg.locator('input[placeholder^="Search a lot"]'), 'CT-2026-0930', delay=60)
        r.wait(0.4); r.click(pg.locator('.card', has_text='CT-2026-0930').first, fx=0.2); pg.wait_for_selector('text=One step back'); r.wait(0.4)
        r.snap('trace')
    r.beat('c1', c1)

    def c2():
        r.point(pg.get_by_text('One step back').first, 0.3); r.wait(0.5)
        col = pg.locator('div', has=pg.get_by_text('One step back', exact=True)).last
        r.point(pg.get_by_text('Midwest Distillate Partners').first, 0.3); r.wait(0.6)
        r.point(pg.get_by_text('Northline Hardware Co.').first, 0.3); r.wait(0.6)
        r.point(pg.get_by_text('One step forward').first, 0.3); r.wait(0.6)
        r.point(pg.get_by_text('Riverbend Cannabis Co.').first, 0.3); r.wait(0.6)
        r.point(pg.get_by_text('Ozark Leaf Dispensary').first, 0.3); r.snap('cols')
    r.beat('c2', c2)

    def c3():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='Start mock recall from this')); md = pg.locator('.md'); md.wait_for(); r.wait(0.3)
        r.type(field(md, 'Reason'), 'Q4 mock recall: cartridge batch', delay=24)
        r.snap('start')
        r.click(md.get_by_role('button', name='Start the clock')); pg.wait_for_selector('text=Elapsed (limit 2:00:00)'); r.wait(0.6)
        r.point(pg.get_by_text('Elapsed (limit 2:00:00)').first, 0.5); r.snap('run')
    r.beat('c3', c3)

    def c4():
        m = md_last(pg)
        r.point(m.get_by_text(re.compile(r'^Steps \(')).first, 0.2)
        cks = m.locator('label.ck', has_text=re.compile('Recall team assembled|Affected product identified|Traced one step back|Traced one step forward'))
        for i in range(cks.count()):
            r.click(cks.nth(i), fx=0.02, after=0.4)
        r.click(m.get_by_role('button', name='Save progress')); r.wait(0.8)
        if not pg.locator('.md').count():
            r.click(pg.locator('.tabs button', has_text='Mock recalls and recalls')); pg.wait_for_selector('tr >> text=MOCK-2026-002'); r.wait(0.3)
            r.click(pg.locator('tr', has_text='MOCK-2026-002').first, fx=0.2); pg.wait_for_selector('text=Elapsed (limit 2:00:00)'); r.wait(0.3)
        m = md_last(pg)
        r.point(m.get_by_text(re.compile(r'^\+\d')).first, 0.5); r.wait(0.4)
        r.point(m.get_by_text(re.compile(r'^\+\d')).nth(3), 0.5)
        r.snap('steps')
    r.beat('c4', c4)

    def c5():
        if not pg.locator('.md').count():
            r.click(pg.locator('.tabs button', has_text='Mock recalls and recalls'))
            r.click(pg.locator('tr', has_text='MOCK-2026-002').first, fx=0.2); pg.wait_for_selector('text=Elapsed (limit 2:00:00)')
        m = md_last(pg)
        cs = m.locator('label.ck', has_text='Sam Salari')
        r.click(cs.first, fx=0.02, after=0.3)
        r.click(m.locator('label.ck', has_text='Dana Whitfield').first, fx=0.02, after=0.3)
        r.type(field(m, 'Made / received'), '2400', delay=60)
        r.type(field(m, 'On hand'), '1100', delay=60)
        r.point(m.get_by_text(re.compile('^Accounted for')).first, 0.3); r.snap('qty')
    r.beat('c5', c5)

    def c6():
        m = md_last(pg)
        r.click(m.get_by_role('button', name='Stop the clock and close')); pg.wait_for_selector('text=Write the findings before closing.'); r.wait(0.3)
        r.point(m.get_by_text('Write the findings before closing.').first, 0.3); r.snap('nofind')
    r.beat('c6', c6)

    def c7():
        m = md_last(pg)
        r.click(m.get_by_role('button', name='Save progress')); r.wait(0.6)
        close_modals(r, pg); r.smooth_top()
        pg.wait_for_selector('.tabs button >> text=Recall team and contacts')
        r.click(pg.locator('.tabs button', has_text='Recall team and contacts')); pg.wait_for_selector('text=Dana Whitfield'); r.wait(0.4)
        r.point(pg.get_by_text('Dana Whitfield').first, 0.3); r.wait(0.6)
        r.point(pg.get_by_text('Ozark Leaf Dispensary').first, 0.3); r.wait(0.4)
        r.snap('contacts')
    r.beat('c7', c7)
    r.stop(); b.close()


FUN = {'intro': lambda pw: scene_card(pw, 'title'), 'end': lambda pw: scene_card(pw, 'end'), 'suppliers': scene_suppliers, 'receiving': scene_receiving, 'holds': scene_holds, 'shipping': scene_shipping, 'trace': scene_trace}

if __name__ == '__main__':
    args = sys.argv[1:]
    if 'nosynth' not in args: hv.synth()
    todo = [a for a in args if a in FUN] if [a for a in args if a in FUN] else ([] if args else list(FUN))
    if todo:
        with sync_playwright() as pw:
            for n in todo: FUN[n](pw)
    if not args or 'build' in args:
        hv.build(SCENES, FINAL)
