# Hendrix QMS training · Video 07 · Production Line Map for managers
#   python3 make.py intro | what | read | why | stops | wall | exec | dash | outro | build
# Record one scene at a time (2-core machine). PROBE=1 saves r.snap() screenshots to work/probe/.
# Map data: the real hx_line_map() Postgres function (lmtest copy) via the pgmap bridge in shots_lm.py,
# reseeded right before each scene (times are relative to the database now()); browser clock is real.
import os, sys, re, json
from common import *
from playwright.sync_api import sync_playwright

SERIES = os.path.abspath(HERE + '/..') + '/'
OUT = SERIES + '07 - Production Line Map for managers.mp4'
SCENES = [('intro', 'Introduction'), ('what', 'What the map shows'), ('read', 'Reading lines and colors'), ('why', 'Why a batch stopped'),
          ('stops', 'Stops right now'), ('wall', 'Wall display'), ('exec', 'Access for executives'), ('dash', 'Dashboard card and idle time'), ('outro', 'Wrap-up')]


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
        r.wait(2.4)
    else:
        pg.evaluate('step(0)'); r.wait(1.2)
        r.beat('z1', lambda: pg.evaluate('step(1)'))
        r.beat('z2', lambda: pg.evaluate('step(2)'))
        r.wait(2.0)
    r.snap('end')
    r.stop(tail=0.5); b.close()


# ------------------------------------------------------------------------------------ helpers
def lm_ns():
    reseed_lm()                                  # times are relative to now(): seed right before recording
    ns = setup_lm(); seed_equipment(ns['T'])
    return ns


def open_map(pg):
    """Before r.start(): land on the Line Map (scene starts on the map)."""
    navb(pg, 'Line Map').click(); pg.wait_for_selector('text=Stops right now'); pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(900)


def kpi(pg, k): return pg.locator('.card', has=pg.locator('.k', has_text=re.compile('^' + k + '$'))).first
def det(pg): return pg.locator('.card', has=pg.locator('text=WHY IT IS STOPPED')).first
def sr(pg): return pg.locator('.card', has=pg.locator('h3', has_text='Stops right now')).first


def pick(r, pg, label):
    r.smooth_top()
    r.click(train(pg, label)); pg.wait_for_selector('text=WHY IT IS STOPPED'); r.wait(0.3)
    scroll_to(r, pg, det(pg))


# ------------------------------------------------------------------------------------ What the map shows
def s_what(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'what')
    r.start()
    def w1():
        r.wait(0.6); r.point(pg.locator('.nav').get_by_text('Modules', exact=False).first, 0.3, dur=0.6); r.wait(0.5)
        go(r, pg, 'Line Map', 'text=Stops right now'); r.wait(0.8)
        r.point(pg.get_by_text('Production Line Map', exact=True).first, 0.4); r.snap('open')
    r.beat('w1', w1)
    def w2():
        r.point(pg.locator('select').nth(1), 0.4, dur=0.6); r.wait(0.8)
        r.point(pg.get_by_text(re.compile('^Live')).first, 0.5); r.wait(1.2)
        for k, w in (('In production', 0.8), ('Moving', 0.6), ('Stopped', 1.4), ('At the lab', 1.0), ('Shipped', 1.0), ('On the floor', 1.0)):
            r.point(kpi(pg, k), 0.4, 0.5, dur=0.45); r.wait(w)
        r.snap('kpi')
    r.beat('w2', w2)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Reading lines and colors
def s_read(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'read'); open_map(pg)
    r.start()
    def r1():
        r.wait(0.3)
        for t in ('Pre-Rolls', 'Cartridges', 'Gummies'):
            r.point(pg.get_by_text(t, exact=True).first, 0.4, dur=0.5); r.wait(0.45)
        r.point(pg.get_by_text('Planned', exact=True).nth(1), dur=0.5); r.wait(0.5)
        r.point(pg.get_by_text('Line clearance', exact=True).nth(1), dur=0.4); r.wait(0.6)
        for t in ('Source Oil / Distillate', 'Primed Oil', 'Packaged'):
            r.point(pg.get_by_text(t, exact=True).first, dur=0.4); r.wait(0.4)
        r.snap('lines')
    r.beat('r1', r1)
    def r2():
        for st in ('Lab testing', 'QC release', 'Labels', 'Shipped'):
            r.point(pg.get_by_text(st, exact=True).last, dur=0.45); r.wait(0.45)
        r.snap('trunk')
    r.beat('r2', r2)
    def r3():
        lg = lambda t: pg.get_by_text(t, exact=True).first
        r.point(lg('Moving'), 0.3, dur=0.6); r.wait(0.2)
        r.point(train(pg, 'CT-2026-112'), dur=0.6); r.wait(0.9)
        r.point(train(pg, 'CT-2026-118'), dur=0.6); r.wait(0.9)
        r.point(lg('Waiting'), 0.3, dur=0.6); r.wait(1.1)
        r.point(train(pg, 'PP-2026-019'), dur=0.6); r.wait(0.9)
        r.point(train(pg, 'GM-2026-038'), dur=0.7); r.snap('colors')
    r.beat('r3', r3)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Why a batch stopped
def s_why(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'why'); open_map(pg)
    r.start()
    def y1():
        r.wait(0.3)
        r.point(train(pg, 'PR-2026-207'), dur=0.6); r.wait(0.5); r.point(train(pg, 'CT-2026-119'), dur=0.5); r.wait(0.5)
        r.click(train(pg, 'GM-2026-045')); pg.wait_for_selector('text=WHY IT IS STOPPED'); r.wait(0.3)
        scroll_to(r, pg, det(pg)); r.snap('gm')
    r.beat('y1', y1)
    def y2():
        d = det(pg)
        r.point(d.get_by_text('CCP Cooking temperature', exact=False).first, 0.3); r.wait(1.6)
        for t, w in (('Source record', 1.0), ('Owner', 0.8), ('Stopped for', 0.8), ('What clears it', 0.6)):
            r.point(d.get_by_text(t, exact=True).first, 0.3); r.wait(w)
        r.point(d.get_by_text('A second person verifies', exact=False).first, 0.3); r.snap('why')
    r.beat('y2', y2)
    def y3():
        pick(r, pg, 'CT-2026-119'); d = det(pg)
        r.point(d.get_by_text('Line clearance not cleared', exact=False).first, 0.3); r.wait(1.2)
        r.point(d.get_by_text(re.compile('^No update for')).first, 0.3); r.wait(1.2)
        j = d.get_by_text('JOURNEY').first
        j.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'start'})"); r.wait(0.8)
        r.point(j, 0.2); r.wait(0.5)
        r.point(d.get_by_text('Source Oil / Distillate', exact=True).last, 0.3); r.snap('journey')
    r.beat('y3', y3)
    def y4():
        pick(r, pg, 'PR-2026-207'); d = det(pg)
        r.point(d.get_by_text('EQ-014 Cone filler', exact=False).first, 0.3); r.wait(1.3)
        r.point(d.get_by_text('Owner', exact=True).first, 0.3); r.wait(1.0)
        r.point(d.get_by_text('Record a passing calibration', exact=False).first, 0.3); r.snap('eq')
    r.beat('y4', y4)
    def y5():
        r.click(det(pg).get_by_role('button', name='Open Equipment'), after=0.1)
        pg.wait_for_selector('text=Equipment register'); pg.evaluate('window.scrollTo(0,0)'); r.wait(0.6)
        row = pg.locator('tr', has_text='Cone filler').first
        r.point(row.locator('td').nth(1), 0.3); r.wait(0.8)
        r.point(row.get_by_text(re.compile('overdue', re.I)).last if row.get_by_text(re.compile('overdue', re.I)).count() else row, 0.4); r.snap('equip')
    r.beat('y5', y5)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Stops right now
def s_stops(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'stops'); open_map(pg)
    r.start()
    def s1():
        s = sr(pg)
        r.wait(0.2); scroll_to(r, pg, s, top=90)
        r.point(s.locator('h3').first, 0.3); r.wait(0.8)
        r.point(s.get_by_text('2 days').first, 0.5); r.wait(0.8)
        r.point(s.get_by_text('Hold HOLD-2026-012', exact=False).first, 0.4); r.wait(0.8)
        r.click(s.locator('button', has_text='CT-2026-118').first, 0.3); pg.wait_for_selector('text=Fill weight low on 6 carts'); r.wait(0.4)
        r.point(det(pg).get_by_text('WHY IT IS STOPPED').first, 0.3); r.snap('stop')
    r.beat('s1', s1)
    grp = pg.locator('button[aria-label^="2 batches at Lab testing"]')
    lst = pg.locator('.card', has=pg.locator('text=2 batches at Lab testing')).first
    def s2():
        r.smooth_top()
        r.click(grp); r.wait(0.5)
        scroll_to(r, pg, lst, top=330)
        r.point(lst.get_by_text('CT-2026-115').first, 0.3); r.wait(0.5)
        r.click(lst.get_by_text('GM-2026-041').first, 0.3); pg.wait_for_selector('text=Potency 8% over the label claim'); r.wait(0.4)
        scroll_to(r, pg, det(pg))
        r.point(det(pg).get_by_text('On hold: Potency', exact=False).first, 0.3); r.snap('group')
    r.beat('s2', s2)
    def s3():
        s = sr(pg)
        scroll_to(r, pg, s.locator('button', has_text='CT-2026-115').first, top=360)
        r.point(s.get_by_text('Samples at the lab', exact=False).first, 0.3); r.wait(1.6)
        r.smooth_top()
        r.click(pg.get_by_role('button', name='Stops only')); r.wait(0.8)
        r.point(train(pg, 'CT-2026-112'), dur=0.6); r.wait(0.5); r.point(train(pg, 'CT-2026-119'), dur=0.6); r.snap('stopsonly')
    r.beat('s3', s3)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Wall display
FS_JS = r"""(()=>{if(window.__fsx)return;window.__fsx=1;   // full-screen as the TV shows it (the headless recorder has no real full screen)
  const st=document.createElement('style');st.textContent='.__fs{position:fixed!important;inset:0!important;z-index:9000!important;overflow:auto!important;background:#0a0a0a!important;padding:22px 30px 130px!important;margin:0!important;box-sizing:border-box}';document.head.appendChild(st);
  Object.defineProperty(Document.prototype,'fullscreenElement',{configurable:true,get(){return window.__fsEl||null;}});
  Element.prototype.requestFullscreen=function(){this.classList.add('__fs');window.__fsEl=this;document.dispatchEvent(new Event('fullscreenchange'));return Promise.resolve();};
  Document.prototype.exitFullscreen=function(){const e=window.__fsEl;if(e){e.classList.remove('__fs');window.__fsEl=null;document.dispatchEvent(new Event('fullscreenchange'));}return Promise.resolve();};})()"""


def s_wall(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'wall'); open_map(pg); pg.evaluate(FS_JS)
    r.start()
    def v1():
        r.wait(0.3)
        r.click(pg.get_by_role('button', name='Wall display')); r.wait(1.6); r.snap('wall')
        r.point(pg.get_by_text(re.compile('updated')).first, 0.8); r.wait(1.4)
        r.point(train(pg, 'PR-2026-207'), dur=0.8); r.wait(0.8); r.point(train(pg, 'GM-2026-045'), dur=0.6); r.wait(0.6)
    r.beat('v1', v1)
    r.wait(0.4)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Access for executives
def s_exec(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'exec', uid=EXEC, wait='text=Open line map')
    r.start()
    def e1():
        r.wait(0.4)
        r.point(pg.get_by_text(EXEC_NAME, exact=True).first, 0.5, dur=0.7); r.wait(1.6)
        r.point(navb(pg, 'Line Map'), 0.4); r.wait(1.2)
        r.point(pg.locator('.nav').get_by_text('Dashboard', exact=True).first, 0.4); r.wait(0.4)
        r.point(pg.locator('.card', has_text='Open line map').last, 0.3, 0.3); r.snap('menu')
    r.beat('e1', e1)
    def e2():
        go(r, pg, 'Line Map', 'text=Stops right now'); r.wait(0.6)
        r.click(train(pg, 'PR-2026-207')); pg.wait_for_selector('text=WHY IT IS STOPPED'); r.wait(0.3)
        scroll_to(r, pg, det(pg))
        r.point(det(pg).get_by_text('EQ-014 Cone filler', exact=False).first, 0.3); r.snap('det')
    r.beat('e2', e2)
    def e3():
        d = det(pg)
        r.point(d.get_by_text('Record a passing calibration', exact=False).first, 0.3); r.wait(1.2)
        j = d.get_by_text('Shipped', exact=True).last
        j.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'center'})"); r.wait(0.8)
        r.point(j, 0.3); r.snap('nobuttons')
    r.beat('e3', e3)
    r.stop(); b.close()


# ------------------------------------------------------------------------------------ Dashboard card and idle time
def s_dash(pw):
    ns = lm_ns()
    b, pg, r = app(pw, ns, 'dash')
    r.start()
    c = pg.locator('.card', has_text='Open line map').last
    def d1():
        r.wait(0.3)
        r.point(c, 0.3, 0.2); r.wait(0.5)
        r.point(c.get_by_text('batches stopped', exact=False).first, 0.4); r.wait(1.0)
        r.point(c.get_by_text('On hold', exact=False).first, 0.5); r.wait(0.8)
        r.click(c.get_by_text('Open line map').first, after=0.1); pg.wait_for_selector('text=Stops right now'); pg.evaluate('window.scrollTo(0,0)'); r.wait(0.6)
        r.snap('card')
    r.beat('d1', d1)
    inp = pg.locator('input[aria-label="Hours without an update"]')
    def d2():
        go(r, pg, 'Settings', 'text=Save settings')
        r.click(pg.get_by_role('button', name='Line Map', exact=True).last); r.wait(0.4)
        r.point(pg.get_by_text('Line Map: a batch is stopped after', exact=False).first, 0.3); r.wait(0.8)
        r.point(pg.get_by_text('Default 4 hours', exact=False).first, 0.8); r.wait(0.6)
        r.point(inp, 0.5); r.snap('settings')
    r.beat('d2', d2)
    def d3():
        r.type(inp, '0', clear=True); r.wait(0.2)
        r.click(pg.get_by_role('button', name='Save settings')); pg.wait_for_selector('text=must be between 1 and 72'); r.wait(0.3)
        r.point(pg.get_by_text('must be between 1 and 72', exact=False).first, 0.3); r.wait(1.0); r.snap('refused')
        r.type(inp, '6', clear=True); r.wait(0.2)
        r.click(pg.get_by_role('button', name='Save settings')); r.wait(1.0); r.snap('saved')
    r.beat('d3', d3)
    r.wait(0.6)
    r.stop(); b.close()


SC = {'intro': lambda pw: card(pw, 'title'), 'outro': lambda pw: card(pw, 'end'), 'what': s_what, 'read': s_read, 'why': s_why,
      'stops': s_stops, 'wall': s_wall, 'exec': s_exec, 'dash': s_dash}
if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['build']:
        hv.build(SCENES, OUT)
    else:
        with sync_playwright() as pw:
            for a in args: SC[a](pw)
