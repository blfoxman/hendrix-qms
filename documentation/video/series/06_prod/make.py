# Hendrix QMS training · Video 06 · Products, production and cultivation (group prod)
#   python3 make.py intro | linemap | products | planner | batches | testing | stickers | cult | outro | build
# Record one scene at a time (2-core machine). PROBE=1 saves r.snap() screenshots to work/probe/.
import os, sys, re, json
from common import *
from playwright.sync_api import sync_playwright

SERIES = os.path.abspath(HERE + '/..') + '/'
OUT = SERIES + '06 - Products, production and cultivation.mp4'
SCENES = [('intro', 'Introduction'), ('linemap', 'Line Map'), ('products', 'Products'), ('planner', 'Production Planner'),
          ('batches', 'Batch Tracker'), ('testing', 'Testing'), ('stickers', 'Compliance Stickers'), ('cult', 'Cultivation'), ('outro', 'Wrap-up')]
EX = 'localStorage.setItem("hx_ptype","cartridges");localStorage.setItem("hx_btype","pre_rolls");localStorage.setItem("hx_pptype","pre_rolls");localStorage.setItem("hx_cultab","batches");'


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
        r.beat('z1', lambda: pg.evaluate('step(1)'))
        r.beat('z2', lambda: pg.evaluate('step(2)'))
        r.wait(2.0)
    r.snap('end')
    r.stop(tail=0.5); b.close()


# ------------------------------------------------------------------------------------ Line Map
def train(pg, label): return pg.locator('button[aria-label^="%s,"]' % label)


def scroll_to(r, pg, loc, top=86):
    y = loc.evaluate('e=>e.getBoundingClientRect().top+window.scrollY') - top
    pg.evaluate("y=>window.scrollTo({top:y,behavior:'smooth'})", y); r.wait(0.9)


def s_linemap(pw):
    reseed_lm()                                  # times are relative to now(): seed right before recording
    ns = setup_lm()
    b, pg, r = app(pw, ns, 'linemap', fixed=None)
    r.start()
    kpi = lambda k: pg.locator('.card', has=pg.locator('.k', has_text=re.compile('^' + k + '$'))).first

    def l1():
        r.wait(0.6); go(r, pg, 'Line Map', 'text=Stops right now'); r.wait(0.8)
        for k in ('In production', 'Moving', 'Stopped', 'At the lab', 'Shipped', 'On the floor'):
            r.point(kpi(k), 0.4, 0.45, dur=0.45); r.wait(0.45)
        r.snap('kpi')
    r.beat('l1', l1)

    def l2():
        for t in ('Pre-Rolls', 'Cartridges', 'Gummies'):
            r.point(pg.get_by_text(t, exact=True).first, 0.4, dur=0.5); r.wait(0.4)
        r.point(pg.get_by_text('Planned', exact=True).nth(1), dur=0.5); r.wait(0.3)
        r.point(pg.get_by_text('Line clearance', exact=True).nth(1), dur=0.4); r.wait(0.3)
        r.point(pg.get_by_text('Source Oil / Distillate', exact=True).first, dur=0.4); r.wait(0.3)
        r.point(pg.get_by_text('Primed Oil', exact=True).first, dur=0.4); r.wait(0.3)
        r.point(pg.get_by_text('Packaged', exact=True).first, dur=0.4); r.wait(0.4)
        for st in ('Lab testing', 'QC release', 'Labels', 'Shipped'):
            r.point(pg.get_by_text(st, exact=True).last, dur=0.4); r.wait(0.3)
        r.snap('lines')
    r.beat('l2', l2)

    def l3():
        r.point(train(pg, 'CT-2026-112'), dur=0.6); r.wait(0.9)
        r.point(train(pg, 'CT-2026-118'), dur=0.5); r.wait(0.9)
        r.point(pg.get_by_text('Waiting', exact=True).first, dur=0.6); r.wait(0.8)
        r.point(train(pg, 'PP-2026-019'), dur=0.6); r.wait(0.9)
        r.point(train(pg, 'GM-2026-038'), dur=0.7); r.snap('colors')
    r.beat('l3', l3)

    det = pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
    def l4():
        r.click(train(pg, 'CT-2026-118')); pg.wait_for_selector('text=WHY IT IS STOPPED'); r.wait(0.3)
        scroll_to(r, pg, det)
        r.point(det.get_by_text('WHY IT IS STOPPED').first, 0.2); r.wait(1.6)
        for t in ('Source record', 'Owner', 'Stopped for', 'What clears it'):
            r.point(det.get_by_text(t, exact=True).first, 0.3); r.wait(1.0)
        r.snap('why')
    r.beat('l4', l4)

    def l5():
        r.point(det.get_by_text('JOURNEY').first, 0.2); r.wait(0.8)
        r.point(det.get_by_text('Source Oil / Distillate').first, 0.3); r.wait(0.6)
        opn = det.get_by_role('button', name=re.compile('^Open '))
        r.point(opn.first, 0.5); r.wait(0.8)
        r.point(opn.last, 0.5); r.snap('journey')
    r.beat('l5', l5)

    sr = pg.locator('.card', has=pg.locator('h3', has_text='Stops right now')).first
    def l6():
        r.point(sr.locator('h3').first, 0.3); r.wait(0.8)
        r.point(sr.get_by_text('2 days').first, 0.5); r.wait(0.6)
        item = sr.locator('button', has_text='GM-2026-045').first
        r.click(item, 0.3); pg.wait_for_selector('text=CCP Cooking temperature'); r.wait(0.4)
        scroll_to(r, pg, det)
        r.point(det.get_by_text('What clears it', exact=True).first, 0.3); r.snap('stop2')
    r.beat('l6', l6)

    def l7():
        r.smooth_top()
        r.click(pg.get_by_role('button', name='Stops only')); r.wait(0.8)
        r.point(train(pg, 'CT-2026-112'), dur=0.6); r.wait(0.6); r.point(train(pg, 'PR-2026-207'), dur=0.6); r.snap('stopsonly')
    r.beat('l7', l7)

    grp = pg.locator('button[aria-label^="2 batches at Lab testing"]')
    lst = pg.locator('.card', has=pg.locator('text=2 batches at Lab testing')).first
    def l8():
        r.click(grp); r.wait(0.5)
        scroll_to(r, pg, lst, top=300)
        r.point(lst.get_by_text('GM-2026-041').first, 0.3); r.wait(0.7)
        r.click(lst.get_by_text('CT-2026-115').first, 0.3); r.wait(0.6)
        r.snap('group')
    r.beat('l8', l8)

    def l9():
        foot = sr.get_by_text('A batch stops on its own', exact=False).first
        r.point(foot, 0.3); r.wait(0.6); r.snap('checks')
    r.beat('l9', l9)

    FS_JS = r"""(()=>{if(window.__fsx)return;window.__fsx=1;   // full-screen as the TV shows it (the headless recorder has no real full screen)
      const st=document.createElement('style');st.textContent='.__fs{position:fixed!important;inset:0!important;z-index:9000!important;overflow:auto!important;background:#0a0a0a!important;padding:22px 30px 130px!important;margin:0!important;box-sizing:border-box}';document.head.appendChild(st);
      Object.defineProperty(Document.prototype,'fullscreenElement',{configurable:true,get(){return window.__fsEl||null;}});
      Element.prototype.requestFullscreen=function(){this.classList.add('__fs');window.__fsEl=this;document.dispatchEvent(new Event('fullscreenchange'));return Promise.resolve();};
      Document.prototype.exitFullscreen=function(){const e=window.__fsEl;if(e){e.classList.remove('__fs');window.__fsEl=null;document.dispatchEvent(new Event('fullscreenchange'));}return Promise.resolve();};})()"""
    def l10():
        pg.evaluate(FS_JS)
        r.smooth_top()
        r.click(pg.get_by_role('button', name='All batches'), after=0.4)
        r.click(pg.get_by_role('button', name='Wall display')); r.wait(2.2); r.snap('wall')
        r.click(pg.get_by_role('button', name='Wall display')); r.wait(0.6)
        if pg.evaluate('!!document.fullscreenElement'): pg.evaluate('document.exitFullscreen()'); r.wait(0.5)
    r.beat('l10', l10)

    def l11():
        go(r, pg, 'Settings', 'text=Save settings')
        r.click(pg.get_by_role('button', name='Line Map', exact=True).last); r.wait(0.4)
        inp = pg.locator('input[aria-label="Hours without an update"]')
        r.point(pg.get_by_text('LINE MAP: A BATCH IS STOPPED AFTER', exact=False).first, 0.3); r.wait(0.6)
        r.type(inp, '6', clear=True); r.wait(0.3)
        r.click(pg.get_by_role('button', name='Save settings')); r.wait(0.8); r.snap('settings')
    r.beat('l11', l11)
    r.stop(); b.close()


def rec_card(pg, num):
    """The innermost card of a record (outer wrappers also contain the text)."""
    return pg.locator('.card', has=pg.get_by_text(num, exact=True)).last


# ------------------------------------------------------------------------------------ Products
def s_products(pw):
    ns = setup_prod()
    b, pg, r = app(pw, ns, 'products', extra=EX); md = pg.locator('.md')
    r.start()
    def p1():
        r.wait(0.5); go(r, pg, 'Products', '.card >> text=Muha Meds 2G AIO'); r.wait(0.3)
        for t in ('SKUs and Flavors', 'Formulation Bank', 'Ingredient Prices'):
            r.point(pg.locator('.tabs button', has_text=t).first, dur=0.5); r.wait(0.5)
        r.snap('open')
    r.beat('p1', p1)
    def p2():
        r.point(pg.locator('.tabs button', has_text='Cartridges').first); r.wait(0.6)
        c = rec_card(pg, 'Muha Meds 2G AIO')
        r.point(c.get_by_text('Every license in Missouri').first, 0.3); r.wait(0.5)
        r.point(c.get_by_text('Oil per cartridge', exact=False).first, 0.3); r.wait(0.5)
        r.point(c.get_by_text(re.compile('flavors$', re.I)).first, 0.3); r.wait(0.5)
        pod = rec_card(pg, 'Live Resin 0.5G Pod')
        r.point(pod.get_by_text(re.compile('^Needs formulation$', re.I)).first); r.snap('pod')
    r.beat('p2', p2)
    def p3():
        r.smooth_top()
        r.click(pg.locator('.tabs button', has_text='Gummies').first); pg.wait_for_selector('.card >> text=Black Fox Gummies 100mg 10pk'); r.wait(0.3)
        r.click(pg.get_by_role('button', name='+ New SKU')); pg.wait_for_selector('.md'); r.wait(0.3)
        r.type(F(md, 'SKU name'), 'Black Fox Gummies 200mg 20pk', delay=30)
        r.type(F(md, 'Grams per gummy'), '4.6'); r.type(F(md, 'Gummies per package'), '20')
        r.type(F(md, 'Flavors - one per line'), 'Watermelon\nSour Apple\nMango', delay=34); r.snap('wiz1')
    r.beat('p3', p3)
    def p4():
        mclick(r, md.get_by_role('button', name='Next: formulation')); r.wait(0.4)
        r.type(F(md, 'Standard batch size'), '1000')
        lib = lambda i=0: md.locator('select', has=pg.locator('option', has_text='+ Add from price library')).nth(i)
        r.select(lib(), label='Distillate ($1.85/g)'); r.type(md.locator('.li').nth(0).locator('input').nth(1), '230')
        r.select(lib(), label='Gummy base ($0.02/g)'); r.type(md.locator('.li').nth(1).locator('input').nth(1), '91770')
        r.select(lib(1), label='Child-resistant jar ($0.25/each)'); r.type(md.locator('.li').nth(2).locator('input').nth(1), '1000')
        r.point(md.get_by_text('Batch total', exact=False).first, 0.4); r.snap('wiz2')
    r.beat('p4', p4)
    def p5():
        r.wait(1.5)
        mclick(r, md.get_by_role('button', name='Save SKU and formulation')); pg.wait_for_selector('.card >> text=Black Fox Gummies 200mg 20pk'); r.wait(0.5)
        c = rec_card(pg, 'Black Fox Gummies 200mg 20pk')
        r.point(c.get_by_text(re.compile('^Active$', re.I)).first); r.wait(0.6)
        r.point(c.get_by_text('Base recipe', exact=True).first, 0.3); r.snap('saved')
    r.beat('p5', p5)
    def p6():
        r.smooth_top(); r.click(pg.locator('.tabs button', has_text='Formulation Bank').first); r.wait(0.6)
        r.point(pg.get_by_text(re.compile('^Pre-Rolls', re.I)).last, 0.3); r.wait(0.6)
        c = pg.locator('.card', has=pg.get_by_text('Mates THCA — Berry Blast', exact=True)).last
        r.point(c, 0.3, 0.15); r.wait(0.5)
        r.point(c.get_by_text(re.compile('^BATCH', re.I)).first); r.wait(0.4); r.point(c.get_by_text(re.compile(r'^\$')).first); r.wait(0.4)
        r.point(c.get_by_role('button', name='Edit')); r.wait(0.5); r.point(c.get_by_role('button', name='Duplicate')); r.snap('bank')
    r.beat('p6', p6)
    def p7():
        r.smooth_top(); r.click(pg.locator('.tabs button', has_text='SKUs and Flavors').first); r.wait(0.5)
        r.point(rec_card(pg, 'Black Fox Gummies 100mg 10pk').get_by_role('button', name='Switch off')); r.snap('tip')
    r.beat('p7', p7)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Production Planner
def s_planner(pw):
    ns = setup_prod(); T = ns['T']
    b, pg, r = app(pw, ns, 'planner', extra=EX); md = pg.locator('.md')
    r.start()
    def n1():
        r.wait(0.5); go(r, pg, 'Production Planner', 'text=Calculate ingredients'); r.wait(0.3)
        r.select(F(pg, 'Product type'), value='pre_rolls')
        r.select(F(pg, 'SKU'), value='k-mates'); r.snap('a')
    r.beat('n1', n1)
    def n2():
        r.click(pg.get_by_role('link', name='Select all')); pg.wait_for_selector('text=Exact amounts from saved formulations')
        u = F(pg, 'Units per flavor'); r.type(u, '1000', clear=True)
        r.fill(F(pg, 'Planned for'), '2026-10-29')
        r.type(F(pg, 'Additional instructions (optional)'), '5% waste buffer'); r.snap('b')
    r.beat('n2', n2)
    def n3():
        r.click(pg.get_by_role('button', name='Calculate ingredients')); pg.wait_for_selector('text=Grand total'); r.wait(0.4)
        gt = pg.locator('.card.gold', has_text='Grand total').first
        r.point(gt, fx=0.3, fy=0.12); r.wait(0.6)
        for t in ('on hand', 'short', 'not in inventory'):
            loc = gt.get_by_text(t, exact=False)
            if loc.count(): r.point(loc.first, dur=0.5); r.wait(0.5)
        r.snap('c')
    r.beat('n3', n3)
    def n4():
        card2 = pg.locator('.card', has_text='Berry Blast').filter(has_not_text='Grand total').last
        r.point(card2, 0.3, 0.1); r.wait(0.6)
        for t in ('Formulation', 'Base recipe'):
            loc = pg.get_by_text(t, exact=True)
            if loc.count(): r.point(loc.first, dur=0.5); r.wait(0.6)
        loc = pg.get_by_text('Production tracking', exact=False)
        if loc.count(): r.point(loc.first, 0.3)
        r.snap('d')
    r.beat('n4', n4)
    def n5():
        sv = pg.get_by_role('button', name='Save plan'); r.click(sv); pg.wait_for_selector('text=← All plans'); r.wait(0.4)
        r.smooth_top()
        num = pg.get_by_text('PP-2026-017', exact=False).first
        r.point(num, 0.3); r.wait(0.8)
        ws = pg.get_by_role('button', name=re.compile('^Worksheets PDF'))
        if ws.count(): r.point(ws.first)
        r.snap('e')
    r.beat('n5', n5)
    def n6():
        r.click(pg.get_by_role('button', name='Start batch').first); pg.wait_for_selector('.md'); r.wait(0.6)
        r.point(F(md, 'SKU'), 0.3); r.wait(0.6); r.point(F(md, 'Flavor'), 0.3); r.wait(0.4)
        r.type(F(md, 'Batch / Lot Number'), 'PR-2026-045', delay=45); r.snap('f')
    r.beat('n6', n6)
    def n7():
        mclick(r, md.get_by_role('button', name='Cancel')); r.wait(0.3)
        go(r, pg, 'Production Planner', 'text=Production Planner')
        r.click(pg.locator('.tabs button', has_text='Plans').first); pg.wait_for_selector('td >> text=PP-2026-017'); r.wait(0.4)
        r.point(pg.locator('tr', has_text='PP-2026-017').locator('td').first, 0.3); r.wait(0.6)
        r.point(pg.locator('tr', has_text='PP-2026-017').get_by_text(re.compile('In production', re.I)).first); r.wait(0.6)
        r.point(pg.locator('tr', has_text='PP-2026-013').get_by_text(re.compile('Cancelled', re.I)).first); r.snap('g')
    r.beat('n7', n7)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Batch Tracker
def s_batches(pw):
    ns = setup_prod(); T = ns['T']
    b43 = next(x for x in T['hx_batches'] if x['id'] == 'b-pr43')      # final tag filled in: ready for testing
    b43['data'].update({'kiefed_infused_preroll_metrc': ns['tag'](1305), 'kiefed_infused_joints_used': '916', 'total_jar_packaged': '183', 'final_packaged_tag': ns['tag'](1343), 'rd1_result': 'Passed'})
    b43['data'] = ns['recalc']('pre_rolls', b43['data'], next(k for k in T['hx_skus'] if k['id'] == 'k-mates')['spec'])
    b, pg, r = app(pw, ns, 'batches', extra=EX); md = pg.locator('.md')
    r.start()
    def b1():
        r.wait(0.5); go(r, pg, 'Batch Tracker', '.card >> text=PR-2026-041'); r.wait(0.3)
        tabs = pg.locator('.tabs').first
        r.point(tabs.locator('button').first, dur=0.5); r.wait(0.4); r.point(tabs.locator('button').last, dur=0.8); r.snap('open')
    r.beat('b1', b1)
    def b2():
        c = rec_card(pg, 'PR-2026-044')
        r.point(c.get_by_text(re.compile('^QC Hold$', re.I)).first); r.wait(0.5)
        r.point(c.get_by_text(re.compile('^METRC')).first); r.wait(0.5)
        r.point(c.get_by_text(re.compile('JOINTS: UNDER WEIGHT', re.I)).first); r.wait(0.6)
        r.point(rec_card(pg, 'PR-2026-042').get_by_text(re.compile('TEST: SUBMITTED', re.I)).first); r.wait(0.5)
        r.point(rec_card(pg, 'PR-2026-042').get_by_text(re.compile('LINE CLEARED', re.I)).first); r.snap('cards')
    r.beat('b2', b2)
    def b3():
        r.smooth_top(); r.click(pg.get_by_role('button', name='+ New Batch')); pg.wait_for_selector('.md'); r.wait(0.3)
        r.type(F(md, 'Batch / Lot Number'), 'PR-2026-045', delay=45)
        r.select(F(md, 'SKU'), label='Mates THCA 5 x 0.6g')
        r.select(F(md, 'Flavor'), label='Berry Blast'); r.snap('hdr')
    r.beat('b3', b3)
    def b4():
        r.point(md.get_by_text(re.compile('^Formulation', re.I)).first, 0.3); r.wait(1.0)
        r.type(F(md, 'Flower METRC #'), ns['tag'](4501), delay=22)
        r.type(F(md, 'Flower Used'), '550'); r.type(F(md, 'THCA Used'), '100'); r.type(F(md, 'Terpene Used'), '25')
        r.type(F(md, 'Infused Flower Total WT'), '674')
        r.click(md.locator('label.ck', has_text='Recorded on METRC?').nth(0), fx=0.04); r.snap('metrc')
    r.beat('b4', b4)
    def b5():
        r.type(F(md, 'Infused Flower Used'), '550')
        r.type(F(md, 'Total Joint Filled'), '1180'); r.wait(0.3)
        uw = md.get_by_text('More joints than expected', exact=False).first
        r.point(uw); r.wait(1.8); r.snap('under')
        r.type(F(md, 'Total Joint Filled'), '998', clear=True); r.wait(0.4)
        r.point(md.get_by_text('Weight per joint is on target', exact=False).first, 0.5); r.snap('pass')
    r.beat('b5', b5)
    def b6():
        r.sign(md.locator('canvas').first); r.wait(0.3)
        mclick(r, md.get_by_role('button', name='Submit & Sign')); pg.wait_for_selector('.card >> text=PR-2026-045'); r.wait(0.4)
        if pg.locator('.md').count(): closeall(r, pg)
        r.smooth_top(); r.point(rec_card(pg, 'PR-2026-045'), 0.2, 0.25); r.snap('saved')
    r.beat('b6', b6)
    def b7():
        r.click(rec_card(pg, 'PR-2026-042').get_by_role('button', name='Edit', exact=True)); pg.wait_for_selector('.md >> text=Reason for change'); r.wait(0.3)
        r.type(F(md, 'Total Joint Filled'), '1004', clear=True)
        r.type(F(md, 'Reason for change'), 'Recount at end of shift (QA Sara H.)', delay=24); r.snap('edit')
    r.beat('b7', b7)
    def b7b():
        mclick(r, md.get_by_role('button', name='Save changes')); pg.wait_for_selector('.md', state='detached'); r.wait(0.3)
        r.click(rec_card(pg, 'PR-2026-042').get_by_role('button', name='View', exact=True)); pg.wait_for_selector('.md .hxrec'); r.wait(0.5)
        md.evaluate("m=>m.scrollTo({top:m.scrollHeight,behavior:'smooth'})"); r.wait(1.2)
        h = md.get_by_text(re.compile('Change history', re.I)).first
        r.point(h, 0.3); r.wait(0.6)
        r.point(md.get_by_text('Recount at end of shift', exact=False).last, 0.3); r.snap('history')
    r.beat('b7b', b7b)
    def b8():
        closeall(r, pg)
        c = rec_card(pg, 'PR-2026-043')
        r.click(c.get_by_role('button', name='Submit for testing')); r.wait(0.6); r.snap('confirm')
        if pg.locator('.md').count():
            mclick(r, md.get_by_role('button', name=re.compile('Submit')).last)
        r.wait(0.8)
        if pg.locator('.md').count(): closeall(r, pg)
        r.point(rec_card(pg, 'PR-2026-043').get_by_text(re.compile('TEST: SUBMITTED', re.I)).first); r.snap('submitted')
    r.beat('b8', b8)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Testing
def s_testing(pw):
    ns = setup_prod(); T = ns['T']
    b, pg, r = app(pw, ns, 'testing', extra=EX); md = pg.locator('.md')
    r.start()
    def t1():
        r.wait(0.5); go(r, pg, 'Testing', '.card >> text=PR-2026-041'); r.wait(0.3)
        for t in ('All', 'Submitted', 'Passed', 'Failed', 'Retest'):
            r.point(pg.locator('.tabs button', has_text=re.compile('^' + t)).first, dur=0.4); r.wait(0.35)
        r.snap('open')
    r.beat('t1', t1)
    def t2():
        c = rec_card(pg, 'PR-2026-042')
        r.point(c.get_by_text('Sample', exact=False).first, 0.6); r.wait(0.5)
        r.click(c.locator('label', has_text='Upload COA'))
        c.locator('input[type=file]').set_input_files(SCR + 'fake_coa.pdf')
        pg.wait_for_selector('.msg >> text=COA read'); r.wait(0.3); r.snap('read')
    r.beat('t2', t2)
    def t3():
        c = rec_card(pg, 'PR-2026-042')
        r.point(pg.locator('.msg', has_text='COA read').first, 0.2); r.wait(0.6)
        r.point(c.get_by_text(re.compile('^Passed$', re.I)).first); r.wait(0.6)
        r.point(c.get_by_text(re.compile('^THC ')).first, 0.3); r.wait(0.6)
        r.point(pg.get_by_text(re.compile('^COA tag:')).first, 0.4); r.snap('passed')
    r.beat('t3', t3)
    def t4():
        r.point(pg.get_by_text(re.compile('COA OVERALL', re.I)).first); r.wait(0.6)
        r.point(pg.get_by_text('Total THC', exact=True).first); r.wait(0.4)
        r.wheel(420); r.wait(0.4)
        r.point(pg.get_by_text(re.compile('^MICROBIALS$', re.I)).first, 0.3); r.wait(0.5)
        r.point(pg.get_by_text('Total yeast and mold', exact=True).first, 0.3); r.wait(0.4)
        r.point(rec_card(pg, 'PR-2026-042').get_by_role('button', name='Hide analysis')); r.snap('analysis')
        r.click(rec_card(pg, 'PR-2026-042').get_by_role('button', name='Hide analysis'))
    r.beat('t4', t4)
    def t5():
        r.smooth_top()
        r.click(rec_card(pg, 'CART-2026-118').get_by_role('button', name='Update')); pg.wait_for_selector('.md'); r.wait(0.3)
        r.select(F(md, 'Status'), value='Retest'); r.wait(0.3)
        r.type(F(md, 'Reason for changing'), 'Lab reported a calibration error on the potency run; resample requested.', delay=16)
        mclick(r, md.get_by_role('button', name='Save', exact=True)); pg.wait_for_selector('.md', state='detached'); r.wait(0.3)
        r.point(rec_card(pg, 'CART-2026-118').get_by_text(re.compile('^Retest$', re.I)).first); r.snap('retest')
    r.beat('t5', t5)
    def t6():
        c = rec_card(pg, 'GUM-2026-031')
        r.point(c.get_by_text(re.compile('^Failed$', re.I)).first); r.wait(0.6)
        r.point(c.get_by_role('button', name='Deviation')); r.snap('failed')
    r.beat('t6', t6)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Compliance Stickers
def pdf_preview(pg, frame):
    """The headless recorder has no PDF viewer: show the label PDF the app made (blob in the iframe) as an image
    in the iframe's place, the way a desktop browser displays it."""
    import base64, subprocess, tempfile
    pg.wait_for_function("e=>e.src&&e.src.startsWith('blob:')", arg=frame.element_handle(), timeout=15000)
    b64 = frame.evaluate("async e=>{const b=new Uint8Array(await (await fetch(e.src)).arrayBuffer());let s='';for(let i=0;i<b.length;i+=8192)s+=String.fromCharCode.apply(null,b.subarray(i,i+8192));return btoa(s);}")
    d = tempfile.mkdtemp(dir=HERE + '/work'); open(d + '/p.pdf', 'wb').write(base64.b64decode(b64))
    subprocess.run(['pdftoppm', '-r', '150', '-f', '1', '-l', '1', '-png', d + '/p.pdf', d + '/p'], check=True)
    from PIL import Image, ImageOps
    f = sorted(__import__('glob').glob(d + '/p*.png'))[0]; im = Image.open(f).convert('RGB')
    bb = ImageOps.invert(im).getbbox()                     # trim the blank paper around the labels
    if bb: im = im.crop((max(0, bb[0] - 24), max(0, bb[1] - 24), min(im.width, bb[2] + 24), min(im.height, bb[3] + 24)))
    im.save(d + '/c.png'); png = base64.b64encode(open(d + '/c.png', 'rb').read()).decode()
    frame.evaluate("""(e,src)=>{const o=e.parentElement.querySelector('.hxpv');if(o)o.remove();
      const was=e.style.display;e.style.display='';const h=e.getBoundingClientRect().height;e.style.display=was;const d=document.createElement('div');d.className='hxpv';
      d.style.cssText='height:'+h+'px;overflow:hidden;border:1px solid var(--line);border-radius:8px;background:#525659;padding:14px;box-sizing:border-box';
      d.innerHTML='<img src="data:image/png;base64,'+src+'" style="width:100%;display:block;box-shadow:0 2px 8px rgba(0,0,0,.5)">';
      e.style.display='none';e.after(d);}""", png)


def retype(r, loc, text):
    r.click(loc, after=0.15); loc.select_text(); r.wait(0.25); r.type(loc, text, click=False)


def s_stickers(pw):
    ns = setup_prod()
    b, pg, r = app(pw, ns, 'stickers', extra=EX); md = pg.locator('.md')
    r.start()
    def s1():
        r.wait(0.5); go(r, pg, 'Compliance Stickers', '.card >> text=Black Fox Gummies — Watermelon'); r.wait(0.3)
        r.point(rec_card(pg, 'Mates THCA — Berry Blast'), 0.3, 0.2); r.wait(0.6)
        r.point(rec_card(pg, 'Black Fox Gummies — Watermelon'), 0.3, 0.2); r.snap('open')
    r.beat('s1', s1)
    def s2():
        r.click(rec_card(pg, 'Black Fox Gummies — Watermelon').get_by_role('button', name='Edit')); pg.wait_for_selector('.md >> text=Allergen declaration'); r.wait(0.4)
        pdf_preview(pg, md.locator('iframe').first)
        for t in ('Product approval number', 'Servings / doses per package', 'Weight', 'Active and other ingredients', 'Allergen declaration', 'Warning'):
            r.point(F(md, t), 0.25, dur=0.5); r.wait(0.45)
        r.snap('edit')
    r.beat('s2', s2)
    def s3():
        pv = md.get_by_text('Preview with sample results', exact=False).first
        pv.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'start'})"); r.wait(1.0)
        r.point(pv, 0.3); r.wait(0.5); r.point(pv, 0.5, 4); r.snap('preview')
    r.beat('s3', s3)
    def s4():
        mclick(r, md.get_by_role('button', name='Cancel')); r.wait(0.3)
        c = rec_card(pg, 'Black Fox 1G Cartridge')
        r.point(c.get_by_text(re.compile('No ingredients', re.I)).first); r.snap('noing')
    r.beat('s4', s4)
    def s5():
        go(r, pg, 'Testing', '.card >> text=PR-2026-041'); r.wait(0.2)
        r.click(rec_card(pg, 'PR-2026-041').get_by_role('button', name='Compliance Sticker')); pg.wait_for_selector('.md iframe'); r.wait(0.3)
        pdf_preview(pg, md.locator('iframe').first); r.wait(0.3)
        r.point(F(md, 'Template'), 0.3); r.snap('print')
    r.beat('s5', s5)
    def s6():
        fr = md.locator('iframe').first; src0 = fr.get_attribute('src')
        retype(r, F(md, 'Labels to print'), '40')
        retype(r, F(md, 'Start at position'), '3')
        pg.wait_for_function("([e,s])=>e.src&&e.src!==s", arg=[fr.element_handle(), src0], timeout=15000); pdf_preview(pg, fr)
        r.point(md.get_by_role('button', name='Alignment test sheet')); r.wait(0.6)
        r.point(F(md, 'Shift right'), 0.4); r.wait(0.4); r.point(F(md, 'Shift down'), 0.4); r.snap('align')
    r.beat('s6', s6)
    def s7():
        fr = md.locator('.hxpv').first
        fr.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'center'})"); r.wait(0.9)
        r.point(fr, 0.3, 0.3); r.wait(0.8)
        md.evaluate("m=>m.scrollTo({top:0,behavior:'smooth'})"); r.wait(0.7)
        dl = md.get_by_role('button', name='Download PDF')
        with pg.expect_download() as di: r.click(dl)
        di.value.path(); r.wait(0.8)
        log = md.get_by_text(re.compile('Print log for this tag', re.I)).first
        r.point(log, 0.3); r.snap('logged')
    r.beat('s7', s7)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Cultivation
def s_cult(pw):
    ns = setup_prod(); T = ns['T']
    b, pg, r = app(pw, ns, 'cult', extra=EX); md = pg.locator('.md')
    r.start()
    def c1():
        r.wait(0.5)
        r.select(pg.locator('select').nth(1), value='lic-cul'); r.wait(0.6)
        go(r, pg, 'Cultivation', 'td >> text=PB-2026-021'); r.wait(0.3); r.snap('open')
    r.beat('c1', c1)
    def c2():
        for t in ('Active plant batches', 'Harvest on hold', 'Harvests (30 days)', 'Applications (7 days)'):
            r.point(pg.get_by_text(t, exact=False).first, 0.4, dur=0.5); r.wait(0.4)
        row = pg.locator('tr', has_text='PB-2026-021')
        r.point(row.locator('td').nth(1), 0.3); r.wait(0.4)
        r.point(row.get_by_text(re.compile('Flowering', re.I)).first); r.wait(0.4)
        r.point(row.get_by_text(re.compile('Not before', re.I)).first); r.snap('list')
    r.beat('c2', c2)
    def c3():
        r.click(pg.get_by_role('button', name='+ Plant batch')); pg.wait_for_selector('.md'); r.wait(0.3)
        r.type(F(md, 'Cultivar / strain'), 'Blue Dream')
        r.type(F(md, 'Plants'), '36')
        r.select(F(md, 'Lot (Receiving)'), value='lt-cl2')
        r.select(F(md, 'Grow media lot'), value='lt-md')
        r.select(F(md, 'Starts in area'), value='ga3'); r.snap('new')
    r.beat('c3', c3)
    def c4():
        mclick(r, md.get_by_role('button', name='Save', exact=True)); pg.wait_for_selector('td >> text=PB-2026-025'); r.wait(0.4)
        if pg.locator('.md').count(): closeall(r, pg)
        row = pg.locator('tr', has_text='PB-2026-025')
        r.point(row.locator('td').first, 0.3); r.wait(0.5); r.point(row.get_by_text(re.compile('Propagation', re.I)).first); r.snap('saved')
    r.beat('c4', c4)
    def c5():
        r.click(pg.locator('tr', has_text='PB-2026-021').get_by_role('button', name='Open')); pg.wait_for_selector('.md >> text=Pre-harvest interval running'); r.wait(0.4)
        for t in ('Nutrients', 'Crop protection', 'Scouting', 'Stage / move', 'Harvest'):
            r.point(md.get_by_role('button', name=t, exact=True).first, dur=0.4); r.wait(0.3)
        r.snap('batch')
    r.beat('c5', c5)
    m2 = pg.locator('.md').last
    def c6():
        r.click(md.get_by_role('button', name='Crop protection', exact=True).first); pg.wait_for_selector('.md >> text=Approved pesticide'); r.wait(0.3)
        r.type(F(m2, 'Applicator'), 'Amir Yrigoyen', clear=True)
        r.select(F(m2, 'Approved pesticide (Chemicals)'), value='ch-p')
        r.type(F(m2, 'Rate (label)'), '1 oz/gal'); r.type(F(m2, 'Method'), 'Foliar spray')
        r.type(F(m2, 'Re-entry (hours)'), '4'); r.type(F(m2, 'Pre-harvest (days)'), '14')
        r.type(F(m2, 'Target pest / disease'), 'Spider mites, follow-up spray', delay=26); r.snap('crop')
    r.beat('c6', c6)
    def c7():
        mclick(r, m2.get_by_role('button', name='Record', exact=True)); pg.wait_for_selector('.md >> text=no harvest before 2026-11-07'); r.wait(0.4)
        r.point(pg.locator('.md').first.get_by_text('no harvest before 2026-11-07', exact=False).first, 0.4); r.snap('phi')
    r.beat('c7', c7)
    def c7b():
        r.click(pg.locator('.md').first.get_by_role('button', name='Harvest', exact=True)); pg.wait_for_selector('.md >> text=Wet weight'); r.wait(0.3)
        hm = pg.locator('.md').last
        r.type(F(hm, 'Wet weight (g)'), '13800'); r.type(F(hm, 'Harvest batch tag (METRC)'), '1A40A0300004F5D00000021', delay=20)
        mclick(r, hm.get_by_role('button', name='Record', exact=True)); pg.wait_for_selector('text=Too early to harvest'); r.wait(0.3)
        r.point(pg.get_by_text('Too early to harvest', exact=False).first, 0.3); r.snap('early')
    r.beat('c7b', c7b)
    def c8():
        closeall(r, pg); r.smooth_top()
        r.click(pg.locator('.tabs button', has_text='Applications').first); r.wait(0.6)
        r.point(pg.locator('tr', has_text='Spider mites, follow-up spray').first if pg.locator('tr', has_text='Spider mites, follow-up spray').count() else pg.locator('tbody tr').first, 0.3); r.wait(0.5)
        r.point(pg.get_by_role('button', name=re.compile('Print application records'))); r.snap('apps')
    r.beat('c8', c8)
    r.stop(); b.close()


SC = {'intro': lambda pw: card(pw, 'title'), 'outro': lambda pw: card(pw, 'end'), 'linemap': s_linemap, 'products': s_products, 'planner': s_planner,
      'batches': s_batches, 'testing': s_testing, 'stickers': s_stickers, 'cult': s_cult}
if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['build']:
        hv.build(SCENES, OUT)
    else:
        with sync_playwright() as pw:
            for a in args: SC[a](pw)
