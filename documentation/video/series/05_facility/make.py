# Hendrix QMS training · Video 05 · Facility, equipment and people on site (group facility)
#   python3 make.py synth | intro | logs | visitors | equipment | chemicals | tests | lineclear | timeclock | outro | build
# Record one scene at a time (2-core machine). PROBE=1 saves r.snap() screenshots to work/probe/.
import os, sys, re, json, datetime as dt
from common import *
from playwright.sync_api import sync_playwright

SERIES = os.path.abspath(HERE + '/..') + '/'
OUT = SERIES + '05 - Facility, equipment and people on site.mp4'
SCENES = [('intro', 'Introduction'), ('logs', 'Facility Logs'), ('visitors', 'Visitor Log'), ('equipment', 'Equipment'),
          ('chemicals', 'Chemicals and SDS'), ('tests', 'Facility Tests'), ('lineclear', 'Line Clearance and Rework'),
          ('timeclock', 'Time Clock and Badges'), ('outro', 'Wrap-up')]


KIOSK_CSS = '.auth{padding-bottom:230px !important}'


def go(r, pg, name, wait):
    r.click(navb(pg, name)); pg.wait_for_selector(wait); r.wait(0.3)
    if pg.evaluate('window.scrollY') > 0: r.smooth_top()


def closeall(r, pg):
    for _ in range(6):
        if not pg.locator('.mo').count(): return
        pg.locator('.mo').last.click(position={'x': 4, 'y': 4}); r.wait(0.25)


def to_app(r, pg, name, wait):
    """Back from a kiosk page to the signed-in app on a module page."""
    pg.goto(pg.url.split('?')[0]); pg.wait_for_selector('.nav'); pg.wait_for_selector('text=Quality standard'); pg.add_style_tag(content=CAP_CSS)
    if not pg.locator(wait).count():
        r.click(navb(pg, name)); pg.wait_for_selector(wait)
    if pg.evaluate('window.scrollY') > 0: r.smooth_top()


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
        r.wait(1.8)
    r.snap('end')
    r.stop(tail=0.5); b.close()


# ------------------------------------------------------------------------------------ Facility Logs
def scene_logs(pw):
    ns = setup(); T = ns['T']
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'logs'); r.start()

    def f1():
        r.wait(1.2); go(r, pg, 'Facility Logs', 'h2 >> text=Sanitation Log'); pg.wait_for_selector('td >> text=Aisha Khan'); r.wait(0.4)
        r.point(pg.locator('.tabs').first, 0.5); r.snap('open')
    r.beat('f1', f1)

    def f2():
        r.point(pg.locator('.tabs button', has_text='Sanitation').first); r.wait(0.6)
        r.point(pg.locator('.tabs button', has_text='Environmental Monitoring').first); r.wait(1.0)
        row = pg.locator('tr', has_text='Re-clean').first if pg.locator('tr', has_text='Re-clean').count() else pg.locator('tbody tr').nth(3)
        r.point(pg.locator('tbody tr').first.locator('td').nth(3), 0.5); r.wait(1.0)
        r.point(pg.locator('tbody tr', has_text='QR').first.get_by_text('QR', exact=True), 0.5); r.wait(1.0)
        r.point(pg.get_by_text(re.compile('Fail / Open', re.I)).first, 0.5); r.snap('rows')
    r.beat('f2', f2)
    md = pg.locator('.md')

    def f3():
        r.click(pg.locator('.tabs button', has_text='Temp / Humidity')); pg.wait_for_selector('h2 >> text=Temp / Humidity Log'); pg.wait_for_selector('td >> text=Gummy Curing Room'); r.wait(0.3)
        r.click(pg.get_by_role('button', name='+ New entry')); pg.wait_for_selector('.md')
        r.select(F(md, 'Location / Room'), label='Storage Vault')
        r.type(F(md, 'Temperature'), '70.5')
        r.type(F(md, 'Relative Humidity'), '66'); r.snap('form1')
    r.beat('f3', f3)

    def f4():
        r.point(F(md, 'Within Acceptable Range?'), 0.3); r.wait(1.4)
        r.point(F(md, 'Corrective Action'), 0.3); r.snap('form2')
    r.beat('f4', f4)

    def f5():
        r.type(F(md, 'Corrective Action'), 'Vault dehumidifier switched on, door seal checked. Re-read in 1 hour.', delay=16)
        r.sign(md.locator('canvas').last); r.snap('form3')
    r.beat('f5', f5)

    def f6():
        r.click(md.get_by_role('button', name='Submit entry')); r.wait(0.8)
        if pg.locator('.md').count(): r.snap('stuck'); closeall(r, pg)
        row = pg.locator('tbody tr').first
        r.point(row.locator('td').nth(3), 0.5); r.wait(1.0)
        r.point(row.get_by_role('button', name='Deviation'), 0.5); r.snap('saved')
    r.beat('f6', f6)

    def f7():
        r.smooth_top()
        r.point(pg.get_by_role('button', name='Print QR sign'), 0.5); r.wait(1.2)
        r.point(pg.get_by_role('button', name='Copy link'), 0.5); r.snap('qr')
    r.beat('f7', f7)

    def f8():
        pg.goto(ns['BASE'] + '?kiosk=log&type=temperature&state=st-mo&lic=lic-mo'); pg.wait_for_selector('text=Temp / Humidity Log'); pg.add_style_tag(content=KIOSK_CSS); r.wait(0.4)
        r.move(720, 260); r.snap('kiosk0')
    r.beat('f8', f8)

    def f9():
        bx = pg.locator('.box')
        r.type(F(bx, 'Recorded By'), 'Devon Brooks')
        r.select(F(bx, 'Location / Room'), label='Packaging Room')
        r.type(F(bx, 'Temperature'), '71.2')
        r.type(F(bx, 'Relative Humidity'), '49'); r.snap('kiosk1')
    r.beat('f9', f9)

    def f10():
        r.sign(pg.locator('canvas').last); r.wait(0.3)
        r.click(pg.get_by_role('button', name='Submit entry')); pg.wait_for_selector('text=Thank you'); r.wait(0.4)
        r.point(pg.get_by_text('Thank you').first); r.snap('kiosk2')
    r.beat('f10', f10)

    def f11():
        to_app(r, pg, 'Facility Logs', 'h2 >> text=Temp / Humidity Log')
        pg.wait_for_selector('td >> text=Devon Brooks'); r.wait(0.4)
        row = pg.locator('tbody tr').first
        r.point(row, 0.15); r.wait(0.8)
        r.point(row.get_by_text('QR', exact=True).first); r.snap('back')
    r.beat('f11', f11)
    r.stop(); b.close()
    print([(x['item'], x['result'], x['source'], x['created_at']) for x in T['hx_facility_log'][-2:]])


# ------------------------------------------------------------------------------------ Visitor Log
def scene_visitors(pw):
    ns = setup(); T = ns['T']
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'visitors'); r.start()

    def v1():
        r.wait(1.2); go(r, pg, 'Visitor Log', 'td >> text=Rachel Ortiz'); r.wait(0.4)
        r.point(pg.locator('tr', has_text='Rachel Ortiz').first, 0.2); r.snap('open')
    r.beat('v1', v1)

    def v2():
        r.point(pg.locator('tr', has_text='Rachel Ortiz').first.get_by_text('GMP accepted').first, 0.5); r.wait(1.0)
        r.point(pg.locator('tr', has_text='Kevin Doyle').first.get_by_text(re.compile('Ill')).first, 0.5); r.wait(1.4)
        r.point(pg.locator('tr', has_text='Rachel Ortiz').first.get_by_text('On site').first, 0.5); r.snap('cols')
    r.beat('v2', v2)

    def v3():
        r.point(pg.get_by_role('button', name='Print QR sign'), 0.5); r.wait(1.0)
        pg.goto(ns['BASE'] + '?kiosk=visitor&state=st-mo&lic=lic-mo'); pg.wait_for_selector('text=Facility GMP rules for visitors'); pg.add_style_tag(content=KIOSK_CSS); r.wait(0.4)
        r.move(720, 300); r.snap('kiosk0')
    r.beat('v3', v3)

    def v4():
        r.type(F(pg, 'Full name'), 'Daniel Reyes')
        r.type(F(pg, 'Company'), 'Show-Me Packaging', delay=30)
        r.select(F(pg, 'Purpose of visit'), value='Vendor / delivery')
        r.type(F(pg, 'Who are you visiting'), 'Devon Brooks', delay=30); r.snap('kiosk1')
    r.beat('v4', v4)

    def v5():
        r.sign(pg.locator('canvas').last); r.wait(0.3)
        r.click(pg.get_by_role('button', name='No', exact=True))
        box = pg.locator('div', has=pg.locator('div.k', has_text='Facility GMP rules for visitors')).last
        box.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'center'})"); r.wait(0.8)
        r.point(pg.get_by_text('Facility GMP rules for visitors').first, 0.3, scroll=False); r.wait(1.2)
        r.click(pg.locator('label', has_text='I have read the GMP rules').locator('input')); r.snap('kiosk2')
    r.beat('v5', v5)

    def v6():
        r.click(pg.get_by_role('button', name='Sign in', exact=True).last); pg.wait_for_selector('text=You are signed in'); r.wait(0.4)
        r.point(pg.get_by_text('You are signed in', exact=False).first, 0.5); r.snap('kiosk3')
    r.beat('v6', v6)

    def v7():
        r.click(pg.get_by_role('button', name='Done', exact=True)); r.wait(0.3)
        r.click(pg.get_by_role('button', name='Sign out', exact=True).first); pg.wait_for_selector('text=In at'); r.wait(0.5)
        r.point(pg.get_by_text('Daniel Reyes').first, 0.5); r.snap('kiosk4')
    r.beat('v7', v7)

    def v8():
        to_app(r, pg, 'Visitor Log', 'td >> text=Rachel Ortiz'); pg.wait_for_selector('td >> text=Daniel Reyes'); r.wait(0.4)
        r.point(pg.locator('tr', has_text='Daniel Reyes').first, 0.2); r.wait(1.0)
        row = pg.locator('tr', has_text='Rachel Ortiz').first
        r.click(row.get_by_role('button', name='Sign out')); r.wait(0.8)
        r.point(pg.locator('tr', has_text='Rachel Ortiz').first.locator('td').nth(6), 0.5); r.snap('signedout')
    r.beat('v8', v8)

    def v9():
        r.point(pg.get_by_role('button', name='+ Manual entry'), 0.5); r.wait(1.2)
        r.point(pg.get_by_role('button', name='Export CSV'), 0.5); r.snap('tip')
    r.beat('v9', v9)
    r.stop(); b.close()
    print([(x['visitor_name'], x.get('time_in'), x.get('time_out')) for x in T['hx_visitor_log']])


# ------------------------------------------------------------------------------------ Equipment
def scene_equipment(pw):
    ns = setup(); T = ns['T']
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'equipment'); r.start()
    md = pg.locator('.md')

    def e1():
        r.wait(1.2); go(r, pg, 'Equipment', 'b >> text=Gummy depositor'); r.wait(0.4)
        r.point(pg.locator('.grid').first, 0.5); r.snap('open')
    r.beat('e1', e1)

    def e2():
        r.point(pg.locator('tr', has_text='Gummy depositor').first.get_by_text('Overdue').first, 0.5); r.wait(1.2)
        r.point(pg.locator('tr', has_text='SCALE-02').first.get_by_text('Overdue').first, 0.5); r.wait(1.2)
        r.point(pg.locator('tr', has_text='Closed-loop BHO').first.get_by_text(re.compile('Out of service', re.I)).first, 0.5); r.snap('reg')
    r.beat('e2', e2)

    def e3():
        r.click(pg.get_by_role('button', name='+ Equipment')); pg.wait_for_selector('.md')
        r.type(F(md, 'Name *'), 'Pre-roll cone filler', delay=30)
        r.select(F(md, 'Category'), value='Production')
        r.type(F(md, 'Location / room'), 'Pre-roll room', delay=30)
        r.type(F(md, 'Make'), 'ConeTech', delay=30); r.type(F(md, 'Model'), 'CF-121', delay=30)
        r.fill(F(md, 'Installed on'), '2026-10-19')
        r.click(md.locator('label.ck', has_text='Touches product').locator('input')); r.snap('form1')
    r.beat('e3', e3)

    def e4():
        r.type(F(md, 'Every (days)'), '30')
        r.type(F(md, 'Tasks (manufacturer requirements)'), 'Clean cone trays, check motor mounts, replace tamping pins.', delay=16); r.snap('form2')
    r.beat('e4', e4)

    def e5():
        r.click(md.get_by_role('button', name='Save', exact=True)); r.wait(1.0)
        if pg.locator('.md').count(): r.snap('stuck'); closeall(r, pg)
        r.point(pg.locator('tr', has_text='Pre-roll cone filler').first, 0.15); r.snap('saved')
    r.beat('e5', e5)

    def e6():
        r.click(pg.locator('tr', has_text='SCALE-01').first.get_by_role('button', name='Open')); pg.wait_for_selector('.md')
        r.click(pg.locator('.md').get_by_role('button', name='Record calibration')); m = pg.locator('.md').last
        r.type(F(m, 'Calibrated by'), 'Midwest Scale Co', delay=30)
        r.point(F(m, 'Reference standard'), 0.3); r.snap('cal1')
    r.beat('e6', e6)

    def e7():
        m = pg.locator('.md').last
        m.locator('label', has_text='+ Certificate').locator('input[type=file]').set_input_files({'name': 'SCALE-01 certificate 2026-10-23.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 cert'})
        r.point(m.locator('label', has_text='+ Certificate'), 0.5); pg.wait_for_selector('.md >> text=SCALE-01 certificate 2026-10-23.pdf'); r.wait(0.4)
        r.type(F(m, 'Details'), 'As found 500.02 g, as left 500.00 g.', delay=20); r.snap('cal2')
    r.beat('e7', e7)

    def e8():
        m = pg.locator('.md').last
        r.click(m.get_by_role('button', name=re.compile('^(Save|Record)'))); r.wait(1.0); r.snap('cal3')
        closeall(r, pg)
        r.point(pg.locator('tr', has_text='SCALE-01').first, 0.5); r.snap('cal4')
    r.beat('e8', e8)

    def e9():
        r.click(pg.locator('tr', has_text='Closed-loop BHO').first.get_by_role('button', name='Open')); pg.wait_for_selector('.md')
        r.click(pg.locator('.md').get_by_role('button', name='Back in service')); r.wait(0.4)
        m = pg.locator('.md').last
        for t in ('Tools, parts, lubricants', 'Cleaned and sanitized before use', 'Checked working as intended'):
            r.click(m.locator('label.ck', has_text=t).locator('input'))
        r.snap('bis')
    r.beat('e9', e9)

    def e10():
        closeall(r, pg); r.wait(0.3)
        r.point(pg.get_by_role('button', name='Print register'), 0.5); r.snap('tip')
    r.beat('e10', e10)
    r.stop(); b.close()
    print(T['hx_equipment'][-1]); print(T['hx_equipment_events'][-1])


# ------------------------------------------------------------------------------------ Chemicals and SDS
def scene_chemicals(pw):
    ns = setup(); T = ns['T']
    for x in T['hx_chemicals']:
        if x['id'] == 'ch6': x.update({'ppe': '', 'hazards': ''})
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'chemicals'); r.start()
    md = pg.locator('.md')

    def c1():
        r.wait(1.2); go(r, pg, 'Chemicals and SDS', 'b >> text=Quat sanitizer 200'); r.wait(0.4)
        r.point(pg.locator('.grid').first, 0.5); r.snap('open')
    r.beat('c1', c1)

    def c2():
        row = pg.locator('tr', has_text='Quat sanitizer 200').first
        r.point(row, 0.15); r.wait(0.8); r.point(row.locator('td').nth(3), 0.5); r.wait(0.8); r.point(row.locator('td').nth(4), 0.5); r.wait(0.8)
        r.point(row.locator('td').nth(5), 0.5); r.wait(1.0)
        r.point(pg.locator('tr', has_text='Neem oil concentrate').first, 0.15); r.snap('list')
    r.beat('c2', c2)

    def c3():
        r.point(pg.get_by_role('button', name='+ Chemical'), 0.5); r.wait(0.8)
        r.click(pg.locator('tr', has_text='Neem oil concentrate').get_by_role('button', name='Review')); pg.wait_for_selector('.md')
        r.type(F(md, 'EPA registration'), '70051-2', delay=40)
        r.point(md.get_by_text('Neem_SDS.pdf').first, 0.5); r.snap('form1')
    r.beat('c3', c3)

    def c4():
        r.type(F(md, 'Hazards'), 'Eye irritant; toxic to aquatic life', delay=22)
        r.type(F(md, 'PPE (SDS section 8) *'), 'Nitrile gloves, safety glasses', delay=22, clear=True)
        r.type(F(md, 'First aid'), 'Rinse eyes 15 minutes', delay=22)
        r.point(F(md, 'Storage area'), 0.3); r.snap('form2')
    r.beat('c4', c4)

    def c5():
        r.click(md.get_by_role('button', name='Save and approve')); r.wait(1.0)
        if pg.locator('.md').count(): r.snap('stuck'); closeall(r, pg)
        r.point(pg.locator('tr', has_text='Neem oil concentrate').first.locator('td').nth(6), 0.5); r.snap('saved')
    r.beat('c5', c5)

    def c6():
        r.point(pg.locator('tr', has_text='Heavy-duty degreaser').first, 0.15); r.wait(1.2)
        r.point(pg.locator('tr', has_text='Heavy-duty degreaser').first.get_by_role('button', name='Review'), 0.5); r.snap('checks')
    r.beat('c6', c6)

    def c7():
        r.smooth_top()
        r.point(pg.get_by_role('button', name='Print approved list'), 0.5); r.wait(1.2)
        r.point(pg.get_by_role('button', name='Print storage area lists'), 0.5); r.snap('tip')
    r.beat('c7', c7)
    r.stop(); b.close()
    print(next(x for x in T['hx_chemicals'] if x['id'] == 'ch6'))


# ------------------------------------------------------------------------------------ Facility Tests
def scene_tests(pw):
    ns = setup(); T = ns['T']
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'tests'); r.start()
    md = pg.locator('.md')

    def t1():
        r.wait(1.2); go(r, pg, 'Facility Tests', 'b >> text=Production room air'); r.wait(0.4)
        r.point(pg.locator('tr', has_text='Incoming water').first, 0.15); r.snap('open')
    r.beat('t1', t1)

    def t2():
        r.point(pg.locator('thead').first, 0.5); r.wait(1.0)
        air = pg.locator('tr', has_text='Production room air').first
        r.point(air, 0.15); r.wait(0.6); r.point(air.get_by_text(re.compile('Overdue', re.I)).first, 0.5); r.snap('status')
    r.beat('t2', t2)

    def t3():
        r.click(pg.locator('tr', has_text='Production room air').first.get_by_role('button', name='Record result')); pg.wait_for_selector('.md')
        r.fill(F(md, 'Sampled on'), '2026-10-20')
        r.type(F(md, 'Sampled by'), 'Maria Gonzalez', delay=30)
        r.type(F(md, 'Report #'), 'PA-26-3381', delay=40)
        r.point(F(md, 'Lab'), 0.3); r.snap('form1')
    r.beat('t3', t3)

    def t4():
        ck = md.locator('label.ck', has_text='ISO/IEC 17025').locator('input')
        if not ck.is_checked(): r.click(ck)
        else: r.point(ck)
        r.type(F(md, 'Results (values)'), 'Yeast and mold 35 CFU/m3; total aerobic count 180 CFU/m3', delay=14)
        md.locator('label', has_text='+ Report').locator('input[type=file]').set_input_files({'name': 'Pace_PA-26-3381_air.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 air'})
        r.point(md.locator('label', has_text='+ Report'), 0.5); pg.wait_for_selector('.md >> text=Pace_PA-26-3381_air.pdf'); r.snap('form2')
    r.beat('t4', t4)

    def t5():
        r.click(md.get_by_role('button', name='Record result')); r.wait(1.0)
        if pg.locator('.md').count(): r.snap('stuck'); closeall(r, pg)
        r.point(pg.locator('tr', has_text='Production room air').first.locator('td').nth(3), 0.5); r.wait(0.8)
        r.point(pg.locator('tr', has_text='Production room air').first.locator('td').nth(4), 0.5); r.snap('saved')
    r.beat('t5', t5)

    def t6():
        r.click(pg.locator('tr', has_text='Food-contact surface swabs').first.get_by_role('button', name='History')); pg.wait_for_selector('.md >> text=Corrective action')
        m = pg.locator('.md').last
        r.point(m.get_by_text('ATP 450 RLU', exact=False).first, 0.3); r.wait(1.2)
        r.point(m.get_by_role('button', name='Deviation').first, 0.5); r.snap('history')
    r.beat('t6', t6)

    def t7():
        closeall(r, pg); r.wait(0.3)
        r.point(pg.get_by_role('button', name='+ Test point'), 0.5); r.wait(1.0)
        r.point(pg.get_by_role('button', name='Print program'), 0.5); r.snap('tip')
    r.beat('t7', t7)
    r.stop(); b.close()
    print(T['hx_env_tests'][0])


# ------------------------------------------------------------------------------------ Line Clearance and Rework
def scene_lineclear(pw):
    ns = setup(); T = ns['T']
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'lineclear'); r.start()
    md = pg.locator('.md')

    def l1():
        r.wait(1.2); go(r, pg, 'Line Clearance and Rework', 'text=LC-2026-018'); r.wait(0.4)
        r.point(pg.locator('.card', has_text=re.compile('Batches cleared', re.I)).first, 0.3); r.snap('open')
    r.beat('l1', l1)

    def l2():
        r.point(pg.locator('tr', has_text='LC-2026-016').first, 0.2); r.wait(1.0)
        r.point(pg.locator('tr', has_text='LC-2026-016').first.get_by_role('button', name='Deviation'), 0.5); r.snap('list')
    r.beat('l2', l2)

    def l3():
        r.click(pg.get_by_role('button', name='+ Line clearance')); pg.wait_for_selector('.md')
        pg.wait_for_selector('.md option >> text=BHO-261023-01', state='attached')
        r.select(F(md, 'Batch'), label='BHO Extraction BHO-261023-01')
        r.type(F(md, 'Room / line'), 'C1D1 room', delay=40)
        r.click(md.locator('label.ck', has_text='EQ-008 Hydrocarbon gas detector').locator('input'))
        r.click(md.locator('label.ck', has_text='EQ-003 SCALE-02').locator('input')); r.wait(0.3)
        r.point(md.locator('label.ck', has_text='EQ-003 SCALE-02'), 0.5); r.snap('form1')
    r.beat('l3', l3)

    def l4():
        rows = md.locator('div.card div.row')
        for i in range(rows.count()):
            r.click(rows.nth(i).get_by_role('button', name='Pass'), after=0.12)
        r.snap('form2')
    r.beat('l4', l4)

    def l5():
        r.point(md.get_by_role('button', name='Line cleared'), 0.5); r.wait(1.2)
        r.point(md.get_by_text('Cannot be cleared', exact=False).first, 0.2); r.snap('blocked')
    r.beat('l5', l5)

    def l6():
        r.click(md.locator('label.ck', has_text='EQ-003 SCALE-02').locator('input'))
        r.click(md.locator('label.ck', has_text='EQ-002 SCALE-01').locator('input'))
        r.type(F(md, 'Verified by'), 'Maria Gonzalez', delay=30)
        r.click(md.get_by_role('button', name='Line cleared')); r.wait(1.0)
        if pg.locator('.md').count(): r.snap('stuck'); closeall(r, pg)
        r.point(pg.locator('tr', has_text='LC-2026-019').first, 0.2); r.snap('saved')
    r.beat('l6', l6)

    def l7():
        r.click(pg.locator('.tabs button', has_text='Rework')); pg.wait_for_selector('text=RW-2026-006'); r.wait(0.4)
        for n in ('RW-2026-006', 'RW-2026-005', 'RW-2026-004', 'RW-2026-003', 'RW-2026-002'):
            r.point(pg.locator('tr', has_text=n).first, 0.12); r.wait(0.35)
        r.snap('rework')
    r.beat('l7', l7)

    def l8():
        r.click(pg.locator('tr', has_text='RW-2026-005').get_by_role('button', name='Approve')); pg.wait_for_selector('.md')
        r.click(md.locator('label.ck', has_text='Like-to-like').locator('input'))
        r.type(F(md, 'Note'), 'Re-blend into the next Blue Dream batch, max 5%', delay=18)
        r.fill(F(md, 'Rework expires on *'), '2027-04-20'); r.snap('approve')
    r.beat('l8', l8)

    def l9():
        r.click(md.get_by_role('button', name='Approve', exact=True)); r.wait(1.0)
        if pg.locator('.md').count(): r.snap('stuck2'); closeall(r, pg)
        r.point(pg.locator('tr', has_text='RW-2026-005').first, 0.5); r.snap('approved')
    r.beat('l9', l9)

    def l10():
        r.point(pg.locator('tr', has_text='RW-2026-005').first.get_by_role('button', name='Use in batch'), 0.5); r.snap('tip')
    r.beat('l10', l10)
    r.stop(); b.close()
    print(T['hx_line_clearances'][0]['number'], next(x for x in T['hx_rework'] if x['id'] == 'rw5')['status'])


# ------------------------------------------------------------------------------------ Time Clock and Badges
def scene_timeclock(pw):
    ns = setup(); T = ns['T']
    b, ctx, pg = open_app(pw, ns)
    r = hv.Rec(ctx, pg, 'timeclock'); r.start()

    def k1():
        r.wait(1.2); go(r, pg, 'Time Clock and Badges', 'td >> text=Lee Park'); r.wait(0.4)
        r.point(pg.locator('.grid').first, 0.5); r.snap('open')
    r.beat('k1', k1)

    def k2():
        r.point(pg.locator('tr', has_text='Lee Park').first, 0.1); r.wait(1.0)
        r.point(pg.locator('tr', has_text='Lee Park').first.locator('td').nth(3), 0.5); r.wait(1.2)
        r.point(pg.locator('tr', has_text='Tom Becker').first.locator('td').nth(1), 0.5); r.wait(1.2)
        r.point(pg.get_by_text('Double scan by mistake', exact=False).first, 0.3); r.snap('sheet')
    r.beat('k2', k2)

    def k3():
        r.smooth_top()
        r.click(pg.locator('.tabs').get_by_role('button', name='On site now')); pg.wait_for_selector('text=In since'); r.wait(0.5)
        r.point(pg.get_by_text('On break since', exact=False).first, 0.3); r.wait(1.0)
        r.point(pg.get_by_role('button', name='Print roll call'), 0.5); r.snap('onsite')
    r.beat('k3', k3)

    def k4():
        r.click(pg.locator('.tabs').get_by_role('button', name='Badges')); pg.wait_for_selector('text=Choose a person'); r.wait(0.4)
        r.click(pg.locator('div', has_text=re.compile('^Tom Becker')).last); pg.wait_for_selector('h3 >> text=Tom Becker'); r.wait(0.4)
        r.type(F(pg, 'Title on the badge'), 'Production Technician', delay=30)
        import base64
        jpg = base64.b64decode(ns['avatar']((90, 80, 60), (210, 170, 135), (60, 40, 25)).split(',', 1)[1])
        r.point(pg.locator('label', has_text='Upload photo'), 0.5); r.wait(0.2)
        pg.locator('label', has_text='Upload photo').locator('input[type=file]').set_input_files({'name': 'tom.jpg', 'mimeType': 'image/jpeg', 'buffer': jpg}); r.wait(0.8); r.snap('badge1')
    r.beat('k4', k4)

    def k5():
        r.click(pg.get_by_role('button', name='Issue badge')); r.wait(1.0)
        r.point(pg.get_by_text(re.compile('Badge issued')).first, 0.3); r.wait(1.0)
        r.point(pg.get_by_role('button', name='Print', exact=True), 0.5); r.snap('badge2')
    r.beat('k5', k5)

    def k6():
        r.smooth_top()
        r.click(pg.locator('.tabs').get_by_role('button', name='Kiosk')); r.wait(0.5)
        r.point(pg.get_by_text('Open kiosk').first, 0.5); r.snap('kiosktab')
    r.beat('k6', k6)

    def k7():
        pg.goto(ns['BASE'] + '?kiosk=clock&state=st-mo&lic=lic-mo'); pg.wait_for_selector('text=Scan your badge'); r.wait(0.6)
        r.move(720, 380); r.snap('kiosk0')
    r.beat('k7', k7)

    def k8():
        r.wait(2.0); pg.keyboard.type(ns['BADGES']['u-maria']['code'], delay=25); pg.keyboard.press('Enter')
        pg.wait_for_selector('text=Maria Gonzalez'); r.wait(0.5); r.snap('kiosk1')
    r.beat('k8', k8)

    def k9():
        r.wait(0.5); r.snap('checks')
    r.beat('k9', k9)
    r.stop(); b.close()
    print(T['hx_time_clock'][-1])


SCENEFN = {'logs': scene_logs, 'visitors': scene_visitors, 'equipment': scene_equipment, 'chemicals': scene_chemicals, 'tests': scene_tests,
           'lineclear': scene_lineclear, 'timeclock': scene_timeclock}

if __name__ == '__main__':
    what = sys.argv[1:] or ['synth']
    for w in what:
        if w == 'synth': hv.synth()
        elif w == 'build': hv.build(SCENES, OUT, os.path.splitext(OUT)[0] + '.srt')
        else:
            with sync_playwright() as pw:
                if w in ('intro', 'outro'): card(pw, 'title' if w == 'intro' else 'end')
                else: SCENEFN[w](pw)
            if LOG and os.environ.get('PROBE'):
                for x in LOG: print('  ', x)
