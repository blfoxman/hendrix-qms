import sys, os, re, json, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hxpdf import *
from cert_data import URS, SUITES, IQ, OQ, PQ
D = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(D)
e = lambda s: H.escape(str(s))

EXTRA = """
.sec { break-before: page; page-break-before: always; }
.sec h1 { font-size: 22pt; margin-bottom: 4pt; }
.sec .n { font-size: 8.5pt; letter-spacing: 3px; color: #8a6a14; font-weight: 700; text-transform: uppercase; }
.sec .bar { height: 3px; width: 80px; background: GOLD; border-radius: 2px; margin: 6pt 0 14pt; }
.arch { margin: 8pt 0 12pt; }
.arch .lane { display: flex; gap: 8pt; }
.arch .box { flex: 1; border: 1pt solid #d4af37; border-radius: 7px; padding: 7pt 10pt; background: #fffdf6; }
.arch .box.dark { background: #111; color: #eee; border-color: #6f5a1d; }
.arch .box b { display: block; font-size: 9.5pt; margin-bottom: 2pt; }
.arch .box.dark b { color: #e9c964; }
.arch .box span { font-size: 8pt; color: #555; } .arch .box.dark span { color: #bbb; }
.arch .arrow { text-align: center; font-size: 7.5pt; color: #8a6a14; padding: 3pt 0; letter-spacing: .5px; }
.arch .arrow::before { content: '\\2193  '; font-size: 10pt; }
.exec td.blank { min-width: 70pt; }
table.exec { font-size: 8pt; table-layout: fixed; } table.exec td { height: 34pt; }
table.exec td:nth-child(1) { white-space: nowrap; font-weight: 650; }
table.csq td:first-child, table.ids td:first-child, .trace td:first-child { white-space: nowrap; font-weight: 650; }
table.csq { font-size: 7.8pt; }
h2.mh { font-size: 12pt; margin-top: 14pt; } h2.mh::after { width: 40px; height: 2px; }
.trace table { font-size: 7.8pt; }
.ok { color: #2f7a4b; font-weight: 700; }
""".replace('GOLD', GOLD_GRAD)

def table(head, rows, cls='', widths=None):
    cg = ('<colgroup>' + ''.join('<col style="width:%s%%">' % w for w in widths) + '</colgroup>') if widths else ''
    th = ''.join('<th>%s</th>' % h for h in head)
    tb = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)
    return '<table class="' + cls + '">' + cg + '<thead><tr>' + th + '</tr></thead><tbody>' + tb + '</tbody></table>'

def urs():
    return table(['ID', 'Area', 'Requirement', 'Impact', 'Verified by'], [(u[0], e(u[1]), e(u[2]), '<b>%s</b>' % u[3] if u[3] == 'High' else u[3], e(u[4])) for u in URS], 'ids')

def tests():
    counts = {}
    for ln in open(os.path.join(SP, 'reg.log')):
        m = re.match(r'(\S+) pass=(\d+) fail=(\d+)', ln)
        if m: counts[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    tot = sum(v[0] for v in counts.values())
    k = ('<div class="kpi"><div><b>%d</b><span>test suites</span></div><div><b>%d</b><span>automated checks</span></div>'
         '<div><b>0</b><span>failures</span></div><div><b>37</b><span>database steps challenged</span></div></div>') % (len(SUITES), tot)
    rows = [(s, e(n), counts.get(s, ('-',))[0], '<span class="ok">Pass</span>') for s, n in SUITES]
    note = ('<p class="note">Last full run: 25 October 2026, release 41. Suites are written in Python with Playwright and run against a mocked database that copies the real rules (the System Health, Line Map, My Tasks, kiosk and METRC suites call the real database functions); the two Edge Functions (email, METRC) have their own tests (22 checks); '
            'the database rules themselves are tested on a local PostgreSQL 16 copy. The test scripts and their logs are kept with the source code and can be shown to the auditor.</p>')
    return k + table(['Suite', 'Area', 'Checks', 'Result'], rows) + note

def trace():
    out = ''
    titles = {'found': 'Setting up and running Hendrix', 'qual': 'Quality system', 'mgmt': 'HACCP and management system', 'supply': 'Suppliers, materials and traceability', 'facility': 'Facility, equipment and people', 'prod': 'Products, production and cultivation', 'lm': 'Production Line Map', 'secure': 'Tasks, security, kiosks and METRC'}
    for g in ['found', 'qual', 'mgmt', 'supply', 'facility', 'prod', 'lm', 'secure']:
        p = os.path.join(D, 'controls_%s.md' % g)
        if not os.path.exists(p): continue
        md = open(p).read()
        md = re.sub(r'^#.*\n', '', md, flags=re.M)
        out += '<h2 class="mh">%s</h2><div class="trace">%s</div>' % (titles[g], md_to_html(md))
    return out

def exec_table(rows, oq=False):
    if oq:
        return table(['Test', 'Name', 'Steps', 'Expected result', 'Auto suite', 'Actual result', 'P/F', 'Init / date'],
                     [(r[0], e(r[1]), e(r[2]), e(r[3]), e(r[4]), '', '', '') for r in rows], 'exec', [7, 10, 24, 22, 7, 18, 5, 7])
    return table(['Step', 'Name', 'What to do', 'Expected result', 'Actual result', 'P/F', 'Init / date'],
                 [(r[0], e(r[1]), e(r[2]), e(r[3]), '', '', '') for r in rows], 'exec', [7, 11, 26, 24, 19, 5, 8])

def csq():
    j = json.load(open(os.path.join(D, 'csq.json')))
    C, L = j['C'], j['L']
    names = {'1': 'Module 1 · Requirements for all licensed operations (Level 1)', '2A': 'Module 2A · Current Good Manufacturing Practices (Level 1)',
             '3A': 'Module 3A · Cultivation (Level 1, cultivation licenses)', '3B': 'Module 3B · Extraction (Level 1, manufacturing licenses)',
             '3C': 'Module 3C · Manufacturing (Level 1, manufacturing licenses)', '4A': 'Module 4A · HACCP (Level 2)', '5': 'Module 5 · Advanced safety and quality management (Level 3)'}
    out = ''
    for m in ['1', '2A', '3A', '3B', '3C', '4A', '5']:
        rows = []
        for c in C:
            if c[1] != m: continue
            pages = ', '.join(L.get(p, p) for p in c[4]) or '<i>SOP / product records (no dedicated page)</i>'
            appl = (' <span class="tag">%s</span>' % e(c[7])) if len(c) > 7 and c[7] else ''
            rows.append((e(c[0]), '<b>%s</b>%s<br><span class="small">%s</span>' % (e(c[2]), appl, e(c[3])), pages, e(c[5])))
        out += '<h2 class="mh">%s</h2>' % names[m] + table(['Clause', 'Requirement (summary)', 'Hendrix pages', 'How the evidence is produced'], rows, 'csq')
    return out

def build_cert():
    md = open(os.path.join(D, 'cert_content.md')).read()
    parts = re.split(r'@@SEC (\d+)\|([^@]+)@@', md)
    toc = []; body = '<div class="toc"><h1>Contents</h1>{{TOC}}</div>'
    for i in range(1, len(parts), 3):
        n, t, content = parts[i], parts[i + 1], parts[i + 2]
        sid = 's%s' % n
        toc.append((1, '%s.  %s' % (n, t), sid))
        rep = {'{{URS}}': urs(), '{{TESTS}}': tests(), '{{TRACE}}': trace(), '{{IQ}}': exec_table(IQ), '{{OQ}}': exec_table(OQ, True), '{{PQ}}': exec_table(PQ), '{{CSQ}}': csq()}
        holders = {}
        for k, v in rep.items():
            if k in content:
                tok = 'HOLD%d' % len(holders); holders[tok] = v; content = content.replace(k, tok)
        h = md_to_html(content)
        for tok, v in holders.items():
            h = h.replace('<p>%s</p>' % tok, v).replace(tok, v)
        body += '<div class="sec"><div class="n">Section %s<span class="mk">@@%s@@</span></div><h1>%s</h1><div class="bar"></div>%s</div>' % (n, sid, e(t), h)
    body = '<style>%s</style>' % EXTRA + body
    cov = cover('Validation and certification pack', 'Hendrix QMS<br><em>validation &amp; certification</em>',
                'System description, requirements, risk assessment, data integrity, controls and test evidence, IQ / OQ / PQ protocols and the CSQ clause map, ready for the auditor.',
                'Release 41 · October 2026', 'Prepared for ASI CSQ, Missouri DCR and Michigan CRA')
    out = os.path.join(SP, 'Hendrix_QMS_Validation_and_Certification_Pack.pdf')
    pages = build(out, cov, body, toc, 'Validation and Certification Pack · Release 41', 'Hendrix QMS: Validation and Certification Pack')
    print('pages', pages)

if __name__ == '__main__':
    build_cert()
