import sys, os, re, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hxpdf import *
D = os.path.dirname(os.path.abspath(__file__))
SP = os.path.dirname(D)
e = lambda s: H.escape(str(s))

CHAPS = [
 ('front', 'Getting started', 'How Hendrix is organized, your access, the rules for good records, routines, and where to find what you need.'),
 ('found', 'Setting up and running Hendrix', 'States and licenses, the state rulebook, the CSQ standard, people and access, the audit trail, settings and importing your lists.'),
 ('qual', 'Quality system', 'Deviations and CAPA, complaints, internal audits, SOPs and training: the core of CSQ Module 1 and the quality culture behind it.'),
 ('mgmt', 'HACCP and the management system', 'HACCP plans and CCP monitoring (CSQ Level 2) and the Level 3 management tools: risk, change control, org chart, objectives, management review and verification.'),
 ('supply', 'Suppliers, materials and traceability', 'From approved supplier to accepted lot, holds and releases, shipments, traces and recalls.'),
 ('facility', 'Facility, equipment and people on site', 'Daily logs, visitors, equipment, chemicals, facility tests, line clearance and rework, the time clock and badges.'),
 ('prod', 'Products, production and cultivation', 'The live Line Map, products and formulations, planning, batch records, testing, compliance stickers and cultivation records.'),
 ('secure', 'Tasks, security, kiosks and METRC', 'My Tasks and email alerts, two-step sign-in and electronic signatures, kiosks that keep working without internet, METRC Check and System Health (releases 37 to 41).'),
]

EXTRA = """
.sit td:first-child { width: 42%; }
.sit td:last-child { white-space: nowrap; color: #6f540c; font-weight: 650; text-align: right; width: 38pt; }
.sit h3 { margin-top: 12pt; }
.gloss td:first-child { font-weight: 700; white-space: nowrap; width: 22%; }
"""

def split_modules(md):
    """returns (intro_md, [(title, body_md)]) splitting on '## '"""
    md = re.sub(r'^# .*\n', '', md, count=1, flags=re.M)
    parts = re.split(r'^## (.+)$', md, flags=re.M)
    intro = parts[0]
    mods = [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    return intro, mods

def situations(body):
    m = re.search(r'### When to use it\s*\n(.*?)(?:\n\s*\n(?!\|)|\Z)', body, re.S)
    if not m: return []
    rows = []
    for ln in m.group(1).split('\n'):
        if not ln.startswith('|') or re.match(r'\|\s*-', ln): continue
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c) >= 2 and c[0].lower() not in ('situation',): rows.append((c[0], c[1]))
    return rows

def inline(md):
    h = markdown.markdown(md)
    return re.sub(r'^<p>|</p>$', '', h.strip())

def build_manual():
    body = '<style>%s</style><div class="toc"><h1>Contents</h1>{{TOC}}</div>' % EXTRA
    toc = []; sit_all = []; mid = 0
    chapter_html = []
    for ci, (g, title, desc) in enumerate(CHAPS):
        path = os.path.join(D, 'front.md' if g == 'front' else 'ch_%s.md' % g)
        if not os.path.exists(path): print('missing', path); continue
        md = open(path).read()
        intro, mods = split_modules(md)
        cid = 'c%d' % ci
        toc.append((1, '%d.  %s' % (ci + 1, title), cid))
        chips = ''.join('<span>%s</span>' % e(t) for t, _ in mods) if g != 'front' else ''
        h = ('<div class="chap"><div class="hx">%s</div><div class="num">Chapter %d<span class="mk">@@%s@@</span></div><h1>%s</h1><div class="bar"></div><p>%s</p><div class="mods">%s</div></div>'
             % (logo(300), ci + 1, cid, e(title), e(desc), chips))
        if intro.strip(): h += md_to_html(intro)
        for k, (mt, mb) in enumerate(mods):
            mid += 1; m_id = 'm%d' % mid
            toc.append((2, mt, m_id))
            for s, w in situations(mb): sit_all.append((title, mt, s, w, m_id))
            cls = 'mod' if (g != 'front' and k > 0) else ''
            # front: keep flowing, but start some sections on new page
            if g == 'front' and mt.startswith(('Routines', 'How Hendrix is organized')): cls = 'mod'
            h += '<div class="%s"><h2>%s<span class="mk">@@%s@@</span></h2>%s</div>' % (cls, e(mt), m_id, md_to_html(mb))
        chapter_html.append((g, h))
    # situation index goes right after Getting started
    sit = '<div class="mod sit"><h2>What do I fill in when…<span class="mk">@@sit@@</span></h2><p>Find the situation, then go to the page shown. The list is grouped by chapter.</p>'
    cur = None
    for ch, mt, s, w, m_id in sit_all:
        if ch != cur:
            if cur is not None: sit += '</tbody></table>'
            sit += '<h3>%s</h3><table><thead><tr><th>Situation</th><th>What you do in Hendrix</th><th>Page</th></tr></thead><tbody>' % e(ch)
            cur = ch
        sit += '<tr><td>%s</td><td>%s</td><td>{{P:%s}}</td></tr>' % (inline(s), inline(w), m_id)
    if cur is not None: sit += '</tbody></table>'
    sit += '</div>'
    for g, h in chapter_html:
        body += h
        if g == 'front':
            body += sit
            k = next(i for i, x in enumerate(toc) if x[2] == 'c1')
            toc.insert(k, (2, 'What do I fill in when…', 'sit'))
    gl = os.path.join(D, 'glossary.md')
    if os.path.exists(gl):
        toc.append((1, 'Glossary', 'gloss'))
        body += '<div class="mod gloss"><h1>Glossary<span class="mk">@@gloss@@</span></h1>%s</div>' % md_to_html(open(gl).read())
    # page refs inside the situation index: two-step: build once to learn pages, then fill
    cov = cover('User manual', 'The <em>Hendrix QMS</em><br>user manual',
                'Every page, every form and every field: what to fill in, when, and why. For production, QA, compliance and management.',
                'Release 41 · October 2026', 'Missouri · Michigan', os.path.join(D, 'shots', 'prod_linemap_overview.png'))
    out = os.path.join(SP, 'Hendrix_QMS_User_Manual.pdf')
    body1 = re.sub(r'\{\{P:(m\d+)\}\}', '00', body)
    pages = build(out, cov, body1, toc, 'User Manual · Release 41', 'Hendrix QMS: User Manual')
    body2 = re.sub(r'\{\{P:(m\d+)\}\}', lambda m: pages.get(m.group(1), ''), body)
    pages2 = build(out, cov, body2, toc, 'User Manual · Release 41', 'Hendrix QMS: User Manual')
    print('modules', mid, 'situations', len(sit_all), 'pages same:', pages == pages2)

if __name__ == '__main__':
    build_manual()
