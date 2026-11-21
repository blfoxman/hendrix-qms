"""Hendrix user manual for the web: the same chapters as the PDF, as one page in the Training Center.

    python3 documentation/manual/build_web.py [out_dir]      (default: site/training/manual)

Writes index.html, toc.js (chapters and the access each module needs, for the Training Center)
and img/*.jpg. Copy the PDF (build_manual.py) next to it as Hendrix_QMS_User_Manual.pdf.
"""
import sys, os, re, json, html as H
import markdown
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from build_manual import CHAPS, RELEASE, split_modules, situations, load_understand, with_understand

ROOT = os.path.abspath(os.path.join(D, '..', '..'))
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, 'site', 'training', 'manual')
IMG = os.path.join(OUT, 'img')
PDF = 'Hendrix_QMS_User_Manual.pdf'
e = lambda s: H.escape(str(s))

# the Hendrix area (access module) each manual section is for; '' = everyone, 'admin' = system admins
ACCESS = {
 'Dashboard': '', 'States and Licenses': 'admin', 'Rulebook': 'rulebook', 'Standards (CSQ)': 'standards', 'Team and Access': 'admin', 'Roles': 'admin',
 'Audit Trail': 'audit', 'Settings': 'settings', 'Import (Excel / Sheets)': 'admin',
 'QMS': 'qms', 'Complaints': 'complaints', 'Internal Audits': 'intaudits', 'SOPs': 'sops', 'Training': 'training',
 'HACCP': 'haccp', 'Risk Register': 'risks', 'Change Control': 'changes', 'Org Chart': 'orgchart', 'Quality Objectives': 'objectives',
 'Management Review': 'mgmtreview', 'Verification Schedule': 'verification',
 'Suppliers': 'suppliers', 'Receiving': 'receiving', 'Hold and Release': 'holds', 'Shipping': 'shipping', 'Traceability and Recall': 'recall',
 'Facility Logs': 'logs', 'Visitor Log': 'logs_visitor', 'Rooms': '', 'Facility Map': 'facmap', 'Equipment': 'equipment', 'Chemicals and SDS': 'chemicals',
 'Facility Tests': 'envtests', 'Line Clearance and Rework': 'lineclear', 'Time Clock and Badges': 'timeclock',
 'Line Map': 'linemap', 'Products': 'products', 'Production Planner': 'planner', 'Batch Tracker': 'batch', 'Manufacturing Process': 'batch',
 'Testing': 'testing', 'Compliance Stickers': 'stickers', 'Cultivation': 'cultivation',
 'Security settings and automatic sign-out': 'settings', 'METRC Check': 'metrc', 'System Health': 'admin'}

def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')

def web_img(src):
    """shots/x.png -> img/x.jpg (1400 px wide), returns (url, w, h)"""
    p = os.path.join(D, src)
    name = os.path.splitext(os.path.basename(src))[0] + '.jpg'
    j = os.path.join(IMG, name)
    if not os.path.exists(p):
        if os.path.exists(j):
            with Image.open(j) as im: return 'img/' + name, im.width, im.height
        print('missing image', src); return None
    if not os.path.exists(j) or os.path.getmtime(j) < os.path.getmtime(p):
        im = Image.open(p).convert('RGB')
        if im.width > 1400: im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(j, quality=80, optimize=True, progressive=True)
    with Image.open(j) as im: return 'img/' + name, im.width, im.height

def md_html(md):
    L = md.split('\n'); R = []
    isli = lambda x: bool(re.match(r'\s*([-*+]|\d+\.)\s', x))
    for ln in L:
        if isli(ln) and R and R[-1].strip() and not isli(R[-1]) and not R[-1].lstrip().startswith('|'): R.append('')
        R.append(ln)
    out = markdown.markdown('\n'.join(R), extensions=['tables', 'sane_lists', 'attr_list', 'fenced_code', 'md_in_html'])
    def fig(m):
        alt, src = H.unescape(m.group(1)), m.group(2)
        r = web_img(src)
        if not r: return ''
        url, w, h = r
        tall = ' tall' if h > w * 1.1 else ''
        return '<figure class="%s"><a href="%s" target="_blank" rel="noopener"><img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async"></a><figcaption>%s</figcaption></figure>' % (tall.strip(), url, url, e(alt), w, h, e(alt))
    out = re.sub(r'<p>\s*<img alt="([^"]*)" src="([^"]+)"\s*/?>\s*</p>', fig, out)
    out = re.sub(r'<blockquote>\s*<p><strong>Hendrix checks', '<blockquote class="checks"><p><strong>Hendrix checks', out)
    out = out.replace('<table>', '<div class="tw"><table>').replace('</table>', '</table></div>')
    return out

def build():
    os.makedirs(IMG, exist_ok=True)
    U = load_understand()
    toc, body, sits, mods_js = [], [], [], []
    for ci, (g, title, desc) in enumerate(CHAPS):
        path = os.path.join(D, 'front.md' if g == 'front' else 'ch_%s.md' % g)
        intro, mods = split_modules(open(path).read())
        cid = 'ch-' + g
        items = []
        body.append('<header class="chap" id="%s"><p class="num">Chapter %d</p><h2>%s</h2><p>%s</p></header>' % (cid, ci + 1, e(title), e(desc)))
        if intro.strip(): body.append('<div class="sec-intro">%s</div>' % md_html(intro))
        for mt, mb in mods:
            sid = slug(mt)
            acc = ACCESS.get(mt, '') if g not in ('front', 'flow') else ''
            items.append((mt, sid))
            mods_js.append({'t': mt, 'id': sid, 'ch': ci + 1, 'a': acc})
            for s, w in situations(mb): sits.append((title, mt, sid, s, w))
            body.append('<section class="mod" id="%s" data-ch="%s"><h3 class="mt"><a href="#%s">%s</a></h3>%s</section>' % (sid, cid, sid, e(mt), md_html(with_understand(mt, mb, U))))
        toc.append((title, cid, ci + 1, items))
        if g == 'front':
            toc.append(('What do I fill in when…', 'situations', None, []))
            body.append('@@SIT@@')
    # situation index
    sh = '<header class="chap" id="situations"><p class="num">Find it fast</p><h2>What do I fill in when…</h2><p>Find the situation, then go to the page shown. Type in the search box at the top to narrow the list.</p></header><section class="mod sit" id="sit-list">'
    cur = None
    for ch, mt, sid, s, w in sits:
        if ch != cur:
            if cur is not None: sh += '</tbody></table></div>'
            sh += '<h4>%s</h4><div class="tw"><table><thead><tr><th>Situation</th><th>What you do in Hendrix</th><th>Page</th></tr></thead><tbody>' % e(ch)
            cur = ch
        sh += '<tr><td>%s</td><td>%s</td><td><a href="#%s">%s</a></td></tr>' % (re.sub(r'^<p>|</p>$', '', markdown.markdown(s)), re.sub(r'^<p>|</p>$', '', markdown.markdown(w)), sid, e(mt))
    sh += '</tbody></table></div></section>'
    body = [sh if b == '@@SIT@@' else b for b in body]
    # glossary
    gl = open(os.path.join(D, 'glossary.md')).read()
    toc.append(('Glossary', 'glossary', None, []))
    body.append('<header class="chap" id="glossary"><p class="num">Words</p><h2>Glossary</h2><p>The terms used in Hendrix and in this manual, in plain words.</p></header><section class="mod gloss" id="glossary-list">%s</section>' % md_html(gl))
    nav = ''
    for title, cid, n, items in toc:
        nav += '<li><a class="c" href="#%s">%s%s</a>' % (cid, ('<span>%d</span>' % n) if n else '', e(title))
        if items: nav += '<ul>' + ''.join('<li><a href="#%s">%s</a></li>' % (sid, e(mt)) for mt, sid in items) + '</ul>'
        nav += '</li>'
    pdf_size = ''
    pp = os.path.join(OUT, PDF)
    if os.path.exists(pp): pdf_size = ' (%d MB)' % round(os.path.getsize(pp) / 1e6)
    html = TEMPLATE.replace('@@NAV@@', nav).replace('@@BODY@@', '\n'.join(body)).replace('@@RELEASE@@', e(RELEASE)).replace('@@PDF@@', PDF).replace('@@PDFSIZE@@', pdf_size)
    open(os.path.join(OUT, 'index.html'), 'w').write(html)
    toc_js = {'release': RELEASE, 'pdf': 'manual/' + PDF, 'modules': mods_js}
    open(os.path.join(OUT, 'toc.js'), 'w').write('window.HX_MANUAL=' + json.dumps(toc_js, ensure_ascii=False, separators=(',', ':')) + ';\n')
    used = set(re.findall(r'img/([^"]+\.jpg)', html))
    for f in os.listdir(IMG):
        if f not in used: os.remove(os.path.join(IMG, f))
    print('web manual:', len(mods_js), 'sections,', len(sits), 'situations,', len(used), 'images ->', OUT)

TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hendrix QMS user manual</title>
<meta name="description" content="The Hendrix QMS user manual: what every page is for, why we do it, and how to fill in every field.">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../../apple-touch-icon.png">
<meta name="theme-color" content="#000000">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&display=swap" rel="stylesheet">
<style>
:root{--black:#000;--panel:#12110e;--panel2:#181610;--gold:#d4af37;--gold-hi:#f1d57a;--gold-lo:#a8841c;--bone:#ece6d6;--stone:#8c877a;--rule:#2a2822;--stop:#e5705a;--go:#5fbf8a;
  --gold-grad:linear-gradient(135deg,var(--gold-hi) 0%,var(--gold) 45%,var(--gold-lo) 100%);--top:68px}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-padding-top:calc(var(--top) + 16px)}
body{margin:0;background:var(--black);color:var(--bone);font-family:Archivo,"Helvetica Neue",Arial,sans-serif;font-size:17px;line-height:1.65;font-variation-settings:"wdth" 100}
a{color:var(--gold-hi)}
:focus-visible{outline:2px solid var(--gold-hi);outline-offset:3px;border-radius:2px}
[hidden]{display:none!important}
.bar{position:sticky;top:0;z-index:20;height:var(--top);display:flex;align-items:center;gap:14px;padding:0 22px;background:rgba(0,0,0,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--rule)}
.mark{display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;flex:0 0 auto}
.mark b{font-weight:800;font-size:15px;letter-spacing:.24em;font-variation-settings:"wdth" 125;background:var(--gold-grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.mark span{color:var(--stone);font-size:14px;font-weight:600}
.search{flex:1;max-width:520px;margin-left:auto;display:flex;align-items:center;border:1px solid #3a372f;border-radius:999px;background:#0b0a08;padding:0 14px}
.search:focus-within{border-color:var(--gold)}
.search input{flex:1;min-width:0;border:0;background:transparent;color:var(--bone);font:inherit;font-size:15px;padding:10px 6px;outline:none}
.search svg{flex:0 0 auto}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:0 16px;border-radius:999px;font:inherit;font-size:14px;font-weight:650;text-decoration:none;cursor:pointer;border:1px solid var(--gold);background:transparent;color:var(--gold-hi);white-space:nowrap}
.btn.solid{background:var(--gold-grad);color:#1a1405;border-color:transparent}
.toc-btn{display:none}
.layout{display:grid;grid-template-columns:300px minmax(0,1fr);max-width:1400px;margin:0 auto}
nav.toc{position:sticky;top:var(--top);height:calc(100vh - var(--top));overflow:auto;padding:22px 14px 40px 22px;border-right:1px solid var(--rule);font-size:14.5px;line-height:1.35}
nav.toc ul{list-style:none;margin:0;padding:0}
nav.toc > ul > li{margin-bottom:10px}
nav.toc a{display:block;color:#bdb6a4;text-decoration:none;padding:4px 8px;border-radius:7px}
nav.toc a:hover{color:var(--bone);background:#14130f}
nav.toc a.c{color:var(--bone);font-weight:700}
nav.toc a.c span{display:inline-block;min-width:22px;color:var(--gold);font-weight:800}
nav.toc ul ul a{padding-left:38px;font-size:14px}
nav.toc a.on{color:#1a1405;background:var(--gold-grad);font-weight:650}
main{min-width:0;padding:34px 48px 120px}
.doc{max-width:860px}
.hero h1{margin:0;font-weight:800;font-size:clamp(34px,5vw,58px);line-height:1.02;font-variation-settings:"wdth" 116}
.hero p{color:#cfc8b6;max-width:40em;margin:14px 0 0}
.hero .acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
.mine{margin-top:26px;padding:18px 20px;border:1px solid var(--rule);border-radius:14px;background:var(--panel)}
.mine h2{margin:0 0 4px;font-size:19px}
.mine p{margin:0 0 12px;color:var(--stone);font-size:14.5px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chips a{border:1px solid #3a372f;border-radius:999px;padding:5px 12px;font-size:14px;text-decoration:none;color:var(--bone)}
.chips a:hover{border-color:var(--gold)}
.chap{margin:72px 0 10px;padding-top:26px;border-top:1px solid var(--rule)}
.chap .num{margin:0;color:var(--gold);font-weight:750;font-size:14px;letter-spacing:.06em}
.chap h2{margin:4px 0 8px;font-weight:800;font-size:clamp(30px,3.6vw,42px);line-height:1.08;font-variation-settings:"wdth" 112}
.chap p{margin:0;color:#cfc8b6;max-width:44em}
.mod{margin-top:46px}
h3.mt{margin:0 0 12px;font-size:clamp(24px,2.6vw,30px);font-weight:800;line-height:1.15;font-variation-settings:"wdth" 108}
h3.mt a{color:var(--bone);text-decoration:none}
h3.mt a:hover{color:var(--gold-hi)}
.mod h3:not(.mt),.sec-intro h2{margin:30px 0 10px;font-size:20px;font-weight:750;color:var(--gold-hi);font-variation-settings:"wdth" 104}
.mod h4{margin:24px 0 8px;font-size:17px}
p{margin:0 0 12px}
ul,ol{margin:0 0 14px;padding-left:24px}
li{margin:0 0 5px}
strong{color:#fff;font-weight:650}
code{font-family:ui-monospace,Menlo,monospace;font-size:14px;background:#1c1a14;padding:1px 5px;border-radius:5px}
.tw{overflow-x:auto;margin:6px 0 18px;border:1px solid var(--rule);border-radius:12px}
table{width:100%;border-collapse:collapse;font-size:15px;line-height:1.45}
th{text-align:left;background:#14130f;color:var(--gold-hi);font-weight:650;font-size:13.5px;padding:10px 12px;border-bottom:1px solid var(--rule)}
td{padding:9px 12px;border-bottom:1px solid #1e1c17;vertical-align:top}
tr:last-child td{border-bottom:0}
blockquote{margin:12px 0 18px;padding:12px 16px;border-left:3px solid var(--gold);background:#100f0b;border-radius:0 10px 10px 0}
blockquote p:last-child,blockquote ul:last-child{margin-bottom:0}
blockquote.checks{border-left-color:var(--stone)}
.why{margin:16px 0 22px;padding:18px 22px 8px;background:linear-gradient(180deg,#17140b 0%,#0f0e0a 100%);border:1px solid #3d3317;border-radius:14px}
.mod .why h3{margin:0 0 10px;color:var(--gold-hi);font-size:18px}
figure{margin:14px 0 22px}
figure img{display:block;width:100%;height:auto;border:1px solid var(--rule);border-radius:10px;background:#0b0a08}
figure.tall img{width:auto;max-width:100%;max-height:640px}
figcaption{margin-top:6px;font-size:13.5px;color:var(--stone)}
.sit h4{color:var(--gold-hi)}
mark{background:rgba(241,213,122,.28);color:inherit;border-radius:3px}
.status{margin:0 0 14px;color:var(--stone);font-size:14.5px}
footer{margin-top:80px;padding-top:20px;border-top:1px solid var(--rule);color:var(--stone);font-size:14px}
.totop{position:fixed;right:18px;bottom:18px;z-index:15}
@media (max-width:980px){
  .layout{grid-template-columns:minmax(0,1fr)}
  nav.toc{position:fixed;left:0;top:var(--top);bottom:0;width:min(340px,88vw);height:auto;background:#050505;z-index:30;transform:translateX(-102%);transition:transform .2s;border-right:1px solid var(--rule)}
  body.toc-open nav.toc{transform:none}
  .toc-btn{display:inline-flex}
  main{padding:24px 20px 100px}
  .mark span{display:none}
  .pdf-btn .lg{display:none}
}
@media (max-width:560px){
  .bar{gap:8px;padding:0 12px}
  .mark b{display:none}
  .btn{padding:0 12px}
  .search{padding:0 10px}
  .tc-link,.pdf-btn{display:none}
  .search{min-width:0}
}
@media print{.bar,nav.toc,.totop,.mine{display:none!important}.layout{display:block}body{background:#fff;color:#000}}
</style>
</head>
<body>
<div class="bar">
  <button class="btn toc-btn" id="toc-btn" type="button" aria-controls="toc" aria-expanded="false">Contents</button>
  <a class="mark" href="../" aria-label="Hendrix Training Center">
    <svg width="28" height="28" viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="hx" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f1d57a"/><stop offset=".5" stop-color="#d4af37"/><stop offset="1" stop-color="#a8841c"/></linearGradient></defs><polygon points="20,2 36,11 36,29 20,38 4,29 4,11" fill="none" stroke="url(#hx)" stroke-width="2.4" stroke-linejoin="round"/><path d="M13 12v16M27 12v16M13 20h14" stroke="url(#hx)" stroke-width="3" stroke-linecap="round" fill="none"/></svg>
    <b>HENDRIX</b><span>User manual</span>
  </a>
  <label class="search"><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="7" fill="none" stroke="#8c877a" stroke-width="2"/><path d="M15.5 15.5L21 21" stroke="#8c877a" stroke-width="2" stroke-linecap="round"/></svg><input id="q" type="search" placeholder="Search the manual" aria-label="Search the manual" autocomplete="off"></label>
  <a class="btn solid pdf-btn" href="@@PDF@@" download><span class="lg">Download&nbsp;</span>PDF</a>
  <a class="btn tc-link" href="../">Training Center</a>
</div>
<div class="layout">
  <nav class="toc" id="toc" aria-label="Contents"><ul>@@NAV@@</ul></nav>
  <main>
    <div class="doc">
      <div class="hero">
        <h1>Hendrix QMS user manual</h1>
        <p>What every page in Hendrix is for, why we do it, and how to fill in every field. Each section starts with <strong>Understand it first</strong>: the idea behind the page in plain words. @@RELEASE@@.</p>
        <div class="acts"><a class="btn" href="#ch-flow">Start with how it all fits together</a><a class="btn" href="#situations">What do I fill in when…</a><a class="btn" href="@@PDF@@" download>Download the PDF@@PDFSIZE@@</a></div>
        <div class="mine" id="mine" hidden><h2 id="mine-h">Your pages</h2><p id="mine-p"></p><div class="chips" id="mine-chips"></div></div>
      </div>
      <p class="status" id="status" role="status" hidden></p>
      @@BODY@@
      <footer>Hendrix QMS user manual, @@RELEASE@@. Examples and screenshots use a made-up company (Northfield Labs) and made-up people; your own screens show your company's names.</footer>
    </div>
  </main>
</div>
<a class="btn totop" href="#" id="totop" hidden>Top</a>
<script src="toc.js"></script>
<script>
(function(){
  var $ = function(id){ return document.getElementById(id); };
  var M = (window.HX_MANUAL || {}).modules || [];
  // ----- contents drawer (phones) -----
  function toc(open){ document.body.classList.toggle('toc-open', open); $('toc-btn').setAttribute('aria-expanded', open ? 'true' : 'false'); }
  $('toc-btn').addEventListener('click', function(){ toc(!document.body.classList.contains('toc-open')); });
  $('toc').addEventListener('click', function(ev){ if (ev.target.closest('a')) toc(false); });
  // ----- where am I -----
  var links = {}; Array.prototype.forEach.call(document.querySelectorAll('nav.toc a'), function(a){ links[a.getAttribute('href').slice(1)] = a; });
  var current = null;
  function mark(id){ if (current === id || !links[id]) return; if (current && links[current]) links[current].classList.remove('on'); current = id; links[id].classList.add('on');
    var r = links[id].getBoundingClientRect(), n = $('toc').getBoundingClientRect(); if (r.top < n.top + 40 || r.bottom > n.bottom - 40) links[id].scrollIntoView({ block: 'center' }); }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function(es){ es.forEach(function(x){ if (x.isIntersecting) mark(x.target.id); }); }, { rootMargin: '-80px 0px -70% 0px' });
    Array.prototype.forEach.call(document.querySelectorAll('section.mod[id], header.chap[id]'), function(s){ io.observe(s); });
  }
  window.addEventListener('scroll', function(){ $('totop').hidden = window.scrollY < 1200; }, { passive: true });
  // ----- search: show only the sections that have every word -----
  var secs = Array.prototype.slice.call(document.querySelectorAll('section.mod, .sec-intro, header.chap'));
  var text = secs.map(function(s){ return s.textContent.toLowerCase(); });
  var rows = Array.prototype.slice.call(document.querySelectorAll('#sit-list tbody tr, #glossary-list tbody tr'));
  var timer = null;
  $('q').addEventListener('input', function(){ clearTimeout(timer); timer = setTimeout(run, 150); });
  $('q').addEventListener('keydown', function(ev){ if (ev.key === 'Escape') { this.value = ''; run(); } });
  function run(){
    var q = $('q').value.trim().toLowerCase(), words = q.split(/\s+/).filter(function(w){ return w.length > 1; });
    unmark();
    if (!words.length) { secs.forEach(function(s){ s.hidden = false; }); rows.forEach(function(r){ r.hidden = false; }); $('status').hidden = true; document.querySelector('.hero').hidden = false; return; }
    document.querySelector('.hero').hidden = true;
    var n = 0, first = null;
    secs.forEach(function(s, i){
      var hit = words.every(function(w){ return text[i].indexOf(w) >= 0; });
      if (s.matches('header.chap')) { s.hidden = true; return; }
      s.hidden = !hit; if (hit && s.matches('section.mod')) { n++; if (!first) first = s; }
    });
    rows.forEach(function(r){ r.hidden = !words.every(function(w){ return r.textContent.toLowerCase().indexOf(w) >= 0; }); });
    $('status').hidden = false;
    $('status').textContent = n ? n + (n === 1 ? ' section mentions ' : ' sections mention ') + '"' + q + '". Clear the search to see the whole manual.' : 'Nothing in the manual mentions "' + q + '". Try another word.';
    var best = M.filter(function(m){ return words.every(function(w){ return m.t.toLowerCase().indexOf(w) >= 0; }); });
    if (best.length) { $('status').appendChild(document.createTextNode(' Best match: '));
      best.slice(0, 3).forEach(function(m, i){ if (i) $('status').appendChild(document.createTextNode(', ')); var a = document.createElement('a'); a.href = '#' + m.id; a.textContent = m.t;
        a.addEventListener('click', function(){ $('q').value = ''; run(); }); $('status').appendChild(a); }); }
    highlight(words);
    window.scrollTo(0, 0);
  }
  function unmark(){ Array.prototype.forEach.call(document.querySelectorAll('main mark'), function(m){ var p = m.parentNode; p.replaceChild(document.createTextNode(m.textContent), m); p.normalize(); }); }
  function highlight(words){
    var rx = new RegExp('(' + words.map(function(w){ return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')', 'gi'), count = 0;
    secs.forEach(function(s){ if (s.hidden || count > 400) return;
      var w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT, null), nodes = [], t;
      while ((t = w.nextNode())) if (rx.test(t.nodeValue)) nodes.push(t), rx.lastIndex = 0;
      nodes.forEach(function(node){ if (count > 400) return; var f = document.createDocumentFragment(), parts = node.nodeValue.split(rx);
        parts.forEach(function(p, i){ if (i % 2) { var m = document.createElement('mark'); m.textContent = p; f.appendChild(m); count++; } else if (p) f.appendChild(document.createTextNode(p)); });
        node.parentNode.replaceChild(f, node); });
    });
  }
  if (location.hash.length > 1 && /^#q=/.test(location.hash)) { $('q').value = decodeURIComponent(location.hash.slice(3)); run(); }
  // ----- signed in at the Training Center: the pages for this person's access -----
  try {
    var P = JSON.parse(sessionStorage.getItem('hxtc_profile') || 'null');
    if (P && P.access) {
      var mine = M.filter(function(m){ if (!m.a) return false; if (m.a === 'admin') return !!P.admin; return P.admin || (P.access[m.a] || 0) >= 1; });
      if (mine.length) {
        $('mine').hidden = false;
        $('mine-h').textContent = (P.name ? P.name.split(' ')[0] + ', your pages' : 'Your pages');
        $('mine-p').textContent = 'The parts of Hendrix you can open' + (P.title ? ' as ' + P.title : '') + '. Read "How it all fits together" first, then these.';
        mine.forEach(function(m){ var a = document.createElement('a'); a.href = '#' + m.id; a.textContent = m.t; $('mine-chips').appendChild(a); });
      }
    }
  } catch (e) {}
})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    build()
