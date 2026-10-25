import sys, os, re, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hxpdf import *
from playwright.sync_api import sync_playwright
D = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(D)
S = lambda f: img_uri(os.path.join(D, 'shots', f))

CSS = r"""
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: 'Inter', sans-serif; color: #e9e3d2; background: #070707; }
.pg { width: 8.5in; height: 11in; position: relative; overflow: hidden; background: #080808; padding: 0.7in 0.7in 0.6in; break-after: page; page-break-after: always; }
.pg:last-child { break-after: auto; }
.pg.glow { background: radial-gradient(ellipse at 85% 0%, #251d0b 0%, #0b0a08 45%, #060606 100%); }
.pg.light { background: #f7f3e8; color: #1b1b1b; }
.kick { font-size: 8.5pt; letter-spacing: 3.5px; text-transform: uppercase; font-weight: 700; color: #e3bf55; }
h1 { font-family: 'Inter Display','Inter'; font-size: 34pt; line-height: 1.05; margin: 10pt 0 12pt; color: #fff; font-weight: 780; letter-spacing: -0.8px; }
.light h1 { color: #111; }
h1 em, h2 em { font-style: normal; color: #e3bf55; }
h2 { font-family: 'Inter Display','Inter'; font-size: 15pt; margin: 0 0 5pt; color: #fff; font-weight: 720; }
.light h2 { color: #111; }
p { font-size: 10.5pt; line-height: 1.55; color: #c9c0a8; margin: 0 0 9pt; }
.light p { color: #444; }
.lead { font-size: 12.5pt; color: #ddd3b8; max-width: 6.2in; }
.bar { height: 3px; width: 90px; background: GOLD; border-radius: 2px; margin: 4pt 0 18pt; }
.shot { border-radius: 9px; overflow: hidden; border: 1px solid #3d331a; box-shadow: 0 14px 40px rgba(0,0,0,.55), 0 0 0 4px rgba(212,175,55,.05); background: #000; }
.shot img { width: 100%; display: block; }
.shot.h { height: 3.4in; } .shot.h img { object-fit: cover; object-position: top left; height: 100%; }
.cap { font-size: 8pt; color: #8f8670; margin-top: 6pt; letter-spacing: .2px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16pt; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12pt; }
.feat { border-top: 1.5px solid #6f5a1d; padding-top: 9pt; }
.feat h3 { font-size: 10.5pt; color: #e9c964; margin: 0 0 4pt; font-weight: 700; }
.light .feat h3 { color: #6f540c; }
.feat p { font-size: 9pt; margin: 0; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10pt; margin: 18pt 0; }
.stat { background: #111; border: 1px solid #2c2614; border-top: 2px solid #d4af37; border-radius: 8px; padding: 12pt; }
.stat b { display: block; font-family: 'Inter Display','Inter'; font-size: 26pt; font-weight: 750; color: #e3bf55; line-height: 1.1; }
.stat span { font-size: 7.8pt; color: #a99f84; text-transform: uppercase; letter-spacing: 1px; }
ul.ticks { list-style: none; padding: 0; margin: 0 0 10pt; }
ul.ticks li { font-size: 9.6pt; color: #d6cdb4; padding: 3pt 0 3pt 16pt; position: relative; line-height: 1.45; }
.light ul.ticks li { color: #333; }
ul.ticks li::before { content: ''; position: absolute; left: 0; top: 8pt; width: 7pt; height: 7pt; border: 1.5px solid #d4af37; transform: rotate(45deg); }
.foot { position: absolute; left: 0.7in; right: 0.7in; bottom: 0.38in; display: flex; justify-content: space-between; font-size: 7pt; color: #6d6552; letter-spacing: 1.5px; text-transform: uppercase; }
.light .foot { color: #9a917a; }
.brand { display: flex; align-items: center; gap: 9pt; }
.bn { font-family: 'Inter Display','Inter'; font-weight: 800; letter-spacing: 6px; font-size: 12pt; color: #e3bf55; }
.bs { font-size: 6pt; letter-spacing: 3.5px; color: #a99f84; }
.hexbg { position: absolute; right: -1.7in; top: -1.2in; opacity: .08; }
.mods { display: flex; flex-wrap: wrap; gap: 5pt; margin-top: 8pt; }
.mods span { border: 0.8pt solid #6f5a1d; color: #e9c964; border-radius: 20px; padding: 2.5pt 9pt; font-size: 8pt; }
.flow { display: flex; align-items: stretch; gap: 0; margin: 12pt 0 16pt; }
.flow div { flex: 1; background: #121212; border: 1px solid #2f2816; padding: 9pt 8pt; font-size: 8.4pt; color: #d6cdb4; text-align: center; position: relative; }
.flow div b { display: block; color: #e9c964; font-size: 9pt; margin-bottom: 2pt; }
.flow div + div { border-left: 0; }
.flow div:first-child { border-radius: 8px 0 0 8px; } .flow div:last-child { border-radius: 0 8px 8px 0; }
.steps { counter-reset: s; }
.steps .st { display: flex; gap: 12pt; margin-bottom: 12pt; align-items: flex-start; }
.steps .st::before { counter-increment: s; content: counter(s); flex: 0 0 26pt; height: 26pt; border-radius: 50%; border: 1.5px solid #d4af37; color: #e9c964; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11pt; }
.steps .st h3 { margin: 2pt 0 2pt; font-size: 11pt; color: #fff; }
.steps .st p { margin: 0; font-size: 9.2pt; }
.quote { border-left: 3px solid #d4af37; padding: 6pt 0 6pt 14pt; font-size: 13pt; color: #efe6cc; font-family: 'Inter Display','Inter'; line-height: 1.4; margin: 14pt 0; }
.sm { position: absolute; }
""".replace('GOLD', GOLD_GRAD)

def foot(n, label='Hendrix QMS · Introduction'):
    return '<div class="foot"><span>%s</span><span>%02d</span></div>' % (label, n)

def shot(f, cap=None, h=None):
    st = (' style="height:%sin"' % h) if h else ''
    ist = ' style="height:100%;object-fit:cover;object-position:top left"' if h else ''
    return '<div><div class="shot"%s><img src="%s"%s></div>%s</div>' % (st, S(f), ist, ('<div class="cap">%s</div>' % cap) if cap else '')

def brand():
    return '<div class="brand">%s<div><div class="bn">HENDRIX</div><div class="bs">QUALITY MANAGEMENT</div></div></div>' % logo(30)

def render(pages, out):
    html_ = '<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (CSS, ''.join(pages))
    tmp = os.path.join(D, '_intro.html'); open(tmp, 'w').write(html_)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME); pg = b.new_page()
        pg.goto('file://' + tmp); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
        pg.pdf(path=out, width='8.5in', height='11in', print_background=True, prefer_css_page_size=True)
        b.close()


def pages():
    P = []
    # 1 cover
    P.append('''<div class="pg glow"><div class="hexbg">%s</div>%s
<div style="margin-top:1.15in"><div class="kick">Introducing</div>
<h1 style="font-size:50pt">Hendrix <em>QMS</em></h1>
<p class="lead">The quality system that runs every cannabis license you operate, and proves it to any inspector, any day.</p><div class="bar"></div></div>
<div style="position:absolute;left:0.7in;right:0.7in;bottom:0.85in">%s</div>
<div class="foot"><span>Missouri · Michigan</span><span>CSQ Levels 1–3 · Release 36 · October 2026</span></div></div>''' % (logo(620), brand(), shot('b_prod_linemap_overview.png')))
    # 2 why
    P.append('''<div class="pg"><div class="kick">Why Hendrix</div><h1>One system.<br>Every license.<br><em>Always audit-ready.</em></h1><div class="bar"></div>
<p class="lead">Paper logs, scattered spreadsheets and a binder for every audit don't scale across licenses and states. Hendrix puts every quality record of every license into one place. Each record is signed, dated and locked the moment it is saved. Each one is linked to the CSQ clause it proves.</p>
<div class="stats"><div class="stat"><b>130</b><span>CSQ clauses tracked</span></div><div class="stat"><b>129</b><span>with live evidence</span></div><div class="stat"><b>39</b><span>pages, one system</span></div><div class="stat"><b>679</b><span>automated checks</span></div></div>
<div class="grid3" style="margin-top:6pt">
<div class="feat"><h3>Built per license</h3><p>Pick a state and a license at the top; every page shows and saves that license only. Missouri and Michigan rules, products and training stay apart.</p></div>
<div class="feat"><h3>Rules that can't be skipped</h3><p>Approvals, reasons, locks and "can't be released" checks are enforced by the database itself, not just the screen.</p></div>
<div class="feat"><h3>See production live</h3><p>The Line Map shows every batch at its station, from plan to shipment, and tells you exactly why a batch has stopped.</p></div></div>
<div style="margin-top:22pt">%s</div>%s</div>''' % (shot('b_mgmt_risk_register.png', 'Risk Register: every hazard scored on a live heat map, with owners, actions and review dates.', h=2.6), foot(2)))
    # 3 CSQ
    P.append('''<div class="pg glow"><div class="kick">CSQ, clause by clause</div><h1>Certification evidence<br><em>that builds itself.</em></h1><div class="bar"></div>
<p class="lead">Hendrix holds all 130 clauses of the CSQ Manufacturing, Extraction and Cultivation standards. Each clause is tied to the pages that prove it. When your team records a log, a batch or a review, that clause's evidence updates.</p>
%s
<div class="grid2" style="margin-top:16pt"><div><ul class="ticks"><li>Scopes per license: manufacturing licenses follow Extraction and Manufacturing; cultivation licenses follow Cultivation</li><li>Conformance per clause, with owner, status, evidence and files</li><li>Warnings for overdue logs, open findings and clauses never assessed</li></ul></div>
<div><ul class="ticks"><li>Read-only inspector view: no edit buttons, everything traceable</li><li>Annual internal audit program that covers every clause</li><li>Each state's rulebook alongside, loaded from the official PDF</li></ul></div></div>%s</div>''' % (shot('b_found_standards_page.png', 'Standards (CSQ): operational alerts, scopes and conformance for the selected license.', h=3.7), foot(3)))
    # 4 quality system
    P.append('''<div class="pg"><div class="kick">Quality system</div><h1>Every problem found,<br><em>fixed and proven fixed.</em></h1><div class="bar"></div>
<div class="grid2" style="grid-template-columns:1.25fr 1fr;align-items:start"><div>%s</div>
<div><div class="feat"><h3>Deviations and CAPA</h3><p>Numbered, owned and dated. A deviation closes only with a correction, and a root cause when one is needed. A CAPA closes only when it is verified effective.</p></div>
<div class="feat" style="margin-top:10pt"><h3>Complaints and adverse events</h3><p>Logged, investigated, answered and trended by category, source and month.</p></div>
<div class="feat" style="margin-top:10pt"><h3>SOPs</h3><p>Written by hand or drafted by AI. Approved with Full access, versioned, and read and signed by every person who needs them.</p></div></div></div>
<div style="margin-top:16pt">%s</div><div class="feat" style="margin-top:12pt"><h3>Training that counts everywhere</h3><p>A training matrix by role, graded online courses and state law courses. One pass counts at every license where the course is shared.</p></div>%s</div>''' % (shot('b_qual_qms_trends.png', 'QMS trends: deviations by month, category, source and department.', h=2.7), shot('b_qual_training_matrix.png', 'Training matrix: who is current, due, expired or missing, at a glance.', h=2.5), foot(4)))
    # 5 HACCP and management
    P.append('''<div class="pg glow"><div class="kick">HACCP and management · CSQ Levels 2 and 3</div><h1>Run the plant<br><em>the way auditors expect.</em></h1><div class="bar"></div>
%s
<div class="grid2" style="margin-top:16pt">%s%s</div>
<div class="grid3" style="margin-top:14pt"><div class="feat"><h3>HACCP</h3><p>Team, product descriptions, flow diagrams, hazard analysis and CCPs. An out-of-limit reading must have its corrective action, and a second person verifies it.</p></div>
<div class="feat"><h3>Risk and change</h3><p>Scored risks with reviews. Changes are approved, then blocked until training, trials and notifications are done.</p></div>
<div class="feat"><h3>Review and verify</h3><p>Objectives with live KPIs, a yearly management review with its inputs pulled in for you, and one schedule of every verification.</p></div></div>%s</div>''' % (shot('b_mgmt_haccp_plans.png', 'HACCP: active plans, CCP monitoring, verification and the certified team.', h=2.5), shot('b_mgmt_objectives_board.png', 'Quality Objectives with live KPIs', h=1.9), shot('b_mgmt_org_chart.png', 'Org chart with backups and key roles', h=1.9), foot(5)))
    # 6 supply chain
    P.append('''<div class="pg"><div class="kick">From supplier to customer</div><h1>Trace any lot<br><em>in seconds.</em></h1><div class="bar"></div>
<div class="flow"><div><b>Supplier</b>approved</div><div><b>Receiving</b>quarantine</div><div><b>Accepted</b>by QA</div><div><b>Batch</b>lots used</div><div><b>Testing</b>COA</div><div><b>Release</b>no holds</div><div><b>Shipping</b>pre-load check</div></div>
%s
<div class="grid2" style="margin-top:16pt"><div><ul class="ticks"><li>Lots come only from approved suppliers and wait in quarantine until QA accepts them</li><li>Held, expired or rejected lots can't be used; a held or failed batch can't ship</li><li>FIFO and quantity left on every accepted lot</li></ul></div>
<div><ul class="ticks"><li>One step back and one step forward trace from any lot, batch or package tag</li><li>Timed mock recalls against the 2-hour target, with the recall team and contact list</li><li>Every shipment linked to its customer, manifest and transporter</li></ul></div></div>%s</div>''' % (shot('b_supply_recall_trace.png', 'Traceability: one lot, traced back to its suppliers and forward to every customer.', h=4.0), foot(6)))
    # 7 production
    P.append('''<div class="pg glow"><div class="kick">Production</div><h1>Plan it, make it,<br><em>test it, label it.</em></h1><div class="bar"></div>
%s
<div class="grid2" style="margin-top:16pt">%s%s</div>
<div class="grid3" style="margin-top:14pt"><div class="feat"><h3>Production Planner</h3><p>Exact amounts for every flavor from your formulations, checked against accepted inventory, with worksheets as a PDF.</p></div>
<div class="feat"><h3>Batch Tracker and Testing</h3><p>Batch records for all eight product types with METRC tags. AI reads the COA, and a person checks it before it is saved.</p></div>
<div class="feat"><h3>Stickers and cultivation</h3><p>Approved label templates and a print log. At cultivation licenses: grow areas, plant batches, crop protection with a pre-harvest hold, harvest and cure.</p></div></div>%s</div>''' % (shot('b_prod_planner_results.png', 'Production Planner: ingredients per flavor, grand total and inventory check.', h=2.7), shot('b_prod_batches_list.png', 'Batch Tracker', h=1.8), shot('b_prod_testing_analysis.png', 'Testing with the COA read by AI', h=1.8), foot(7)))
    # 8 on the floor
    P.append('''<div class="pg"><div class="kick">On the floor</div><h1>Tablets at the door.<br><em>Records in real time.</em></h1><div class="bar"></div>
<p class="lead">Kiosk pages work without a login for one license. Staff scan a QR code to fill in a log, visitors sign in with the GMP agreement and an illness check, and everyone clocks in with their badge.</p>
<div style="display:grid;grid-template-columns:0.8fr 0.8fr 1.6fr;gap:12pt;align-items:start;margin-top:10pt">%s%s%s</div>
<div class="grid2" style="margin-top:16pt;align-items:start">%s<div><div class="feat"><h3>Facility Logs</h3><p>Black Fox and Michigan logs: sanitation, temperature and humidity, pest, security, scale calibration, equipment maintenance, waste and environmental monitoring. Overdue logs are flagged automatically.</p></div>
<div class="feat" style="margin-top:10pt"><h3>Time Clock and Badges</h3><p>Printed CR80 badges with a barcode and QR code. Three breaks with limits, late minutes, a live "on site now" list, and corrections only with a reason.</p></div></div></div>%s</div>''' % (shot('b_facility_logs_kiosk.png', 'Facility log kiosk', h=3.0), shot('b_facility_visitor_kiosk_signin.png', 'Visitor sign-in', h=3.0), shot('facility_timeclock_kiosk.png', 'Time clock kiosk', h=3.0), shot('b_facility_timeclock_badges.png', 'Badges, ready to print', h=2.3), foot(8)))
    # 9 trust
    P.append('''<div class="pg glow"><div class="kick">Built for trust</div><h1>Records you can<br><em>stand behind.</em></h1><div class="bar"></div>
%s
<div class="grid2" style="margin-top:18pt"><div><ul class="ticks"><li><b style="color:#fff">Attributable:</b> personal accounts approved by an admin; every save is stamped with the name and the server time</li><li><b style="color:#fff">Never deleted:</b> wrong entries are voided with a reason and stay visible</li><li><b style="color:#fff">Reason for every change:</b> old value, new value, who, when and why, in an audit trail nobody can edit</li><li><b style="color:#fff">Right person, right action:</b> View, Edit or Full per module, checked by the database</li></ul></div>
<div><ul class="ticks"><li><b style="color:#fff">AI as a helper:</b> it drafts and reads; people check, approve and sign</li><li><b style="color:#fff">Tested:</b> 35 automated test suites and 679 checks run on every release</li><li><b style="color:#fff">Validation pack:</b> requirements, risk assessment, IQ / OQ / PQ and the CSQ clause map, ready for the auditor</li><li><b style="color:#fff">Printouts:</b> your logo, legal name and footer on every record</li></ul></div></div>%s</div>''' % (shot('b_found_audit_page.png', 'Audit Trail: every change with who, when, old and new values and the reason.', h=3.7), foot(9)))
    # 10 getting started
    P.append('''<div class="pg"><div class="kick">Getting started</div><h1>Live in<br><em>five steps.</em></h1><div class="bar"></div>
<div class="steps" style="max-width:6.4in">
<div class="st"><div><h3>Set up your states and licenses</h3><p>Add Missouri and Michigan, then each license, with its operation (manufacturing or cultivation).</p></div></div>
<div class="st"><div><h3>Add your people and roles</h3><p>Approve each account and give it a role: Production Tech, QA Manager, GM and more, or custom access.</p></div></div>
<div class="st"><div><h3>Bring in what you already have</h3><p>Import suppliers, equipment, chemicals, products, complaints, risks and your org chart from Excel or Google Sheets.</p></div></div>
<div class="st"><div><h3>Adopt the standard</h3><p>Load the CSQ standard, adopt it for each license and upload your state's rulebook.</p></div></div>
<div class="st"><div><h3>Put tablets on the floor</h3><p>Print badges, place the log, visitor and time clock kiosks, and start recording.</p></div></div></div>
<div class="quote">"Every record signed, dated, locked and linked to the clause it proves."</div>
<div style="position:absolute;left:0.7in;right:0.7in;bottom:0.9in;display:flex;justify-content:space-between;align-items:flex-end">%s<div style="text-align:right;font-size:8.5pt;color:#8f8670;line-height:1.6">Hendrix QMS · Release 36<br>User Manual and Validation and Certification Pack available</div></div>%s</div>''' % (brand(), foot(10)))
    return P

if __name__ == '__main__':
    out = os.path.join(SP, 'Hendrix_QMS_Introduction.pdf')
    render(pages(), out)
    print('ok', out)
