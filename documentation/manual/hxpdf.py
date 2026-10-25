"""Hendrix PDF builder: markdown/HTML -> print HTML -> Chromium PDF, cover merged, TOC with real page numbers."""
import re, os, html as H, markdown, base64, io
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

DIR = os.path.dirname(os.path.abspath(__file__))
CHROME = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'

LOGO = ('<svg viewBox="0 0 40 40" width="{s}" height="{s}"><defs><linearGradient id="lg{i}" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#f1d57a"/><stop offset=".5" stop-color="#d4af37"/><stop offset="1" stop-color="#a8841c"/></linearGradient></defs>'
        '<polygon points="20,2 36,11 36,29 20,38 4,29 4,11" fill="none" stroke="url(#lg{i})" stroke-width="2.4"/>'
        '<path d="M13 12v16M27 12v16M13 20h14" stroke="url(#lg{i})" stroke-width="3" stroke-linecap="round" fill="none"/></svg>')
_li = [0]
def logo(size=40):
    _li[0] += 1
    return LOGO.format(s=size, i=_li[0])

GOLD_GRAD = 'linear-gradient(100deg,#8a6a14 0%,#d4af37 22%,#f6e08f 42%,#d4af37 58%,#a8841c 80%,#e9c964 100%)'

BASE_CSS = r"""
@page { size: Letter; margin: 0.7in 0.75in 0.8in 0.75in; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: 'Inter', 'DejaVu Sans', sans-serif; font-size: 9.6pt; line-height: 1.52; color: #1b1b1b; margin: 0; }
pre { white-space: pre-wrap; font-size: 8pt; }
p { margin: 0 0 7pt; orphans: 3; widows: 3; }
a { color: #7a5c0c; text-decoration: none; }
strong { font-weight: 650; color: #111; }
code { font-family: 'DejaVu Sans Mono', monospace; font-size: 8.4pt; background: #f4efe0; padding: 0 3px; border-radius: 3px; }
h1, h2, h3, h4 { font-family: 'Inter Display', 'Inter', sans-serif; color: #111; break-after: avoid; page-break-after: avoid; }
h1 { font-size: 26pt; font-weight: 750; letter-spacing: -0.4px; margin: 0 0 10pt; line-height: 1.12; }
h2 { font-size: 17pt; font-weight: 720; margin: 0 0 6pt; padding-top: 2pt; line-height: 1.2; }
h2::after { content: ''; display: block; height: 3px; width: 64px; margin-top: 7pt; background: GOLD; border-radius: 2px; }
h3 { font-size: 11.5pt; font-weight: 700; margin: 15pt 0 5pt; color: #6f540c; }
h4 { font-size: 10pt; font-weight: 700; margin: 11pt 0 4pt; }
ul, ol { margin: 0 0 8pt; padding-left: 17pt; }
li { margin: 0 0 2.5pt; }
li > p { margin: 0; }
table { width: 100%; border-collapse: collapse; margin: 4pt 0 10pt; font-size: 8.5pt; line-height: 1.38; break-inside: auto; }
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
th { background: #141414; color: #e9c964; font-weight: 650; text-align: left; padding: 5pt 6pt; font-size: 7.6pt; letter-spacing: .5px; text-transform: uppercase; border: 0; }
td { padding: 4.5pt 6pt; border-bottom: 0.6pt solid #e4ddc8; vertical-align: top; }
tbody tr:nth-child(even) td { background: #faf7ee; }
blockquote { margin: 6pt 0 10pt; padding: 7pt 10pt 7pt 12pt; background: #fbf5e2; border-left: 3.5pt solid #d4af37; border-radius: 0 5px 5px 0; break-inside: avoid; }
blockquote p { margin: 0 0 3pt; } blockquote p:last-child { margin: 0; }
figure { margin: 8pt 0 12pt; break-inside: avoid; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 4.6in; border-radius: 6px; border: 0.8pt solid #2a2a2a; box-shadow: 0 1px 0 #d4af37; }
figure.form img { max-height: 5.4in; }
figcaption { font-size: 7.8pt; color: #6b6b6b; margin-top: 4pt; font-style: italic; }
hr { border: 0; height: 1px; background: #e4ddc8; margin: 12pt 0; }
.pb { break-before: page; page-break-before: always; }
.mk { font-size: 1px; line-height: 0; color: #fff; letter-spacing: 0; }
.chap .mk { color: #0b0b0b; }
/* chapter opener */
.chap { break-before: page; page-break-before: always; background: #0b0b0b; color: #f3ead2; border-radius: 10px; padding: 34pt 30pt 30pt; margin-bottom: 18pt; position: relative; overflow: hidden; }
.chap .num { font-size: 9pt; letter-spacing: 3px; text-transform: uppercase; font-weight: 650; color: #e3bf55; }
.chap h1 { color: #fff; margin: 8pt 0 8pt; font-size: 28pt; }
.chap .bar { height: 3px; width: 90px; background: GOLD; border-radius: 2px; margin: 4pt 0 12pt; }
.chap p { color: #cfc6ae; margin: 0; font-size: 10pt; }
.chap .mods { margin-top: 12pt; display: flex; flex-wrap: wrap; gap: 5pt; }
.chap .mods span { border: 0.8pt solid #6f5a1d; color: #e9c964; border-radius: 20px; padding: 2pt 8pt; font-size: 8pt; }
.chap .hx { position: absolute; right: -30pt; top: -20pt; opacity: .13; }
.mod { break-before: page; page-break-before: always; }
.mod:first-of-type { break-before: auto; }
.meta { background: #f6f3ea; border-radius: 6px; padding: 7pt 10pt; margin: 6pt 0 10pt; font-size: 8.8pt; }
.meta p { margin: 0 0 2pt; }
/* toc */
.toc h1 { margin-bottom: 14pt; }
.toc .row { display: flex; align-items: baseline; gap: 6pt; padding: 3pt 0; font-size: 9.6pt; }
.toc .row.l1 { font-weight: 700; font-size: 10.5pt; margin-top: 9pt; color: #111; }
.toc .row.l2 { padding-left: 14pt; color: #333; }
.toc .row .dots { flex: 1; border-bottom: 1px dotted #b9ab80; transform: translateY(-3pt); }
.toc .row .pg { font-variant-numeric: tabular-nums; color: #6f540c; font-weight: 600; min-width: 18pt; text-align: right; }
.cols2 { columns: 2; column-gap: 22pt; }
.cols2 .row { break-inside: avoid; }
.note { font-size: 8.4pt; color: #666; }
.kpi { display: flex; gap: 8pt; margin: 8pt 0 12pt; }
.kpi div { flex: 1; background: #0e0e0e; color: #eee; border-radius: 7px; padding: 9pt 10pt; border-top: 2px solid #d4af37; }
.kpi b { display: block; font-size: 18pt; color: #e9c964; font-weight: 700; }
.kpi span { font-size: 7.6pt; color: #bbb; text-transform: uppercase; letter-spacing: .8px; }
.sign { width: 100%; margin-top: 8pt; }
.sign td { height: 30pt; border-bottom: 0.8pt solid #888; }
.small { font-size: 8pt; }
.tag { display: inline-block; font-size: 7pt; padding: 0.5pt 5pt; border-radius: 9px; border: 0.6pt solid #b99a3c; color: #6f540c; font-weight: 650; letter-spacing: .3px; }
.tag.ok { border-color: #3c8a5a; color: #2f7a4b; } .tag.na { border-color: #999; color: #777; }
""".replace('GOLD', GOLD_GRAD)

COVER_CSS = r"""
@page { size: Letter; margin: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: 'Inter', sans-serif; }
.cover { width: 8.5in; height: 11in; background: radial-gradient(ellipse at 75% 18%, #2a2210 0%, #0d0c09 45%, #050505 100%); color: #f3ead2; position: relative; overflow: hidden; }
.cover .brand { position: absolute; left: 0.8in; top: 0.8in; display: flex; align-items: center; gap: 12pt; }
.cover .bn { font-family: 'Inter Display', 'Inter'; font-weight: 800; letter-spacing: 7px; font-size: 15pt; color: #e3bf55; }
.cover .bs { font-size: 7pt; letter-spacing: 4px; color: #b8a97c; }
.cover .t { position: absolute; left: 0.8in; right: 0.8in; top: 3.3in; }
.cover .kicker { font-size: 9pt; letter-spacing: 4px; text-transform: uppercase; color: #d4af37; font-weight: 650; }
.cover h1 { font-family: 'Inter Display', 'Inter'; font-size: 44pt; line-height: 1.04; margin: 12pt 0 14pt; font-weight: 780; letter-spacing: -1px; color: #fff; }
.cover h1 em { font-style: normal; color: #e3bf55; }
.cover .sub { font-size: 12.5pt; color: #cbbf9f; max-width: 5.6in; line-height: 1.5; }
.cover .bar { height: 4px; width: 120px; background: GOLD; border-radius: 2px; margin-top: 22pt; }
.cover .hex { position: absolute; right: -1.6in; bottom: -1.4in; opacity: .11; }
.cover .foot { position: absolute; left: 0.8in; right: 0.8in; bottom: 0.7in; display: flex; justify-content: space-between; font-size: 8pt; color: #9c916f; letter-spacing: .6px; border-top: 0.6pt solid #3a321c; padding-top: 9pt; }
.cover .shot { position: absolute; right: 0.8in; left: 0.8in; bottom: 1.35in; height: 3.3in; border-radius: 10px; overflow: hidden; border: 1px solid #4a3d18; box-shadow: 0 0 0 4px rgba(212,175,55,.06); }
.cover .shot img { width: 100%; display: block; }
.cover .shot::after { content: ''; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(5,5,5,0) 55%, rgba(5,5,5,.9) 100%); }
""".replace('GOLD', GOLD_GRAD)


def img_uri(path):
    p = path if os.path.isabs(path) else os.path.join(DIR, path)
    if p.endswith('.png') and os.path.exists(p):
        from PIL import Image
        j = os.path.join(DIR, 'shots_jpg', os.path.basename(p)[:-4] + '.jpg')
        if not os.path.exists(j) or os.path.getmtime(j) < os.path.getmtime(p):
            os.makedirs(os.path.dirname(j), exist_ok=True)
            im = Image.open(p).convert('RGB')
            if im.width > 1400: im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
            im.save(j, quality=82, optimize=True, progressive=True)
        p = j
    return 'file://' + p


def md_to_html(md):
    """Markdown -> HTML; images become figures with captions; 'Hendrix checks' quotes stay callouts."""
    L = md.split('\n'); R = []
    isli = lambda x: bool(re.match(r'\s*([-*+]|\d+\.)\s', x))
    for ln in L:
        if isli(ln) and R and R[-1].strip() and not isli(R[-1]) and not R[-1].lstrip().startswith('|'): R.append('')
        R.append(ln)
    md = '\n'.join(R)
    out = markdown.markdown(md, extensions=['tables', 'sane_lists', 'attr_list', 'fenced_code'])
    def fig(m):
        alt, src = H.unescape(m.group(1)), m.group(2)
        cls = 'form' if re.search(r'(form|modal|_new|_edit|dialog)', src) else ''
        return '<figure class="%s"><img src="%s" alt="%s"><figcaption>%s</figcaption></figure>' % (cls, img_uri(src), H.escape(alt), H.escape(alt))
    out = re.sub(r'<p>\s*<img alt="([^"]*)" src="([^"]+)"\s*/?>\s*</p>', fig, out)
    out = re.sub(r'<img alt="([^"]*)" src="([^"]+)"\s*/?>', lambda m: '<img src="%s" alt="%s">' % (img_uri(m.group(2)), m.group(1)), out)
    return out


def page_html(body, css_extra=''):
    return ('<!doctype html><html><head><meta charset="utf-8"><style>%s%s</style></head><body>%s</body></html>'
            % (BASE_CSS, css_extra, body))


def footer(label):
    return ('<div style="width:100%;font-family:Inter,sans-serif;font-size:7px;color:#8a8170;padding:0 0.75in;display:flex;justify-content:space-between;align-items:center">'
            '<span style="letter-spacing:1.2px"><b style="color:#8a6a14">HENDRIX</b> &nbsp;' + H.escape(label) + '</span>'
            '<span><span class="pageNumber"></span></span></div>')


def render(pg, html_text, out, foot_label=None, cover=False):
    tmp = os.path.join(DIR, '_render.html')
    open(tmp, 'w').write(html_text)
    pg.goto('file://' + tmp)
    pg.wait_for_load_state('networkidle')
    pg.evaluate('document.fonts.ready')
    opts = dict(path=out, format='Letter', print_background=True, prefer_css_page_size=True, outline=True, tagged=True)
    if cover or not foot_label:
        opts['display_header_footer'] = False
    else:
        opts.update(display_header_footer=True, header_template='<div></div>', footer_template=footer(foot_label))
    pg.pdf(**opts)


def build(out, cover_html, body_parts, toc_entries, foot_label, title, author='Hendrix QMS'):
    """body_parts: html string containing markers <span class="mk">@@ID@@</span> for each toc entry id.
    toc_entries: list of (level, text, id). TOC placeholder '{{TOC}}' inside body gets replaced."""
    def toc_html(pages):
        rows = ''.join('<div class="row l%d"><span>%s</span><span class="dots"></span><span class="pg">%s</span></div>'
                       % (lv, H.escape(t), pages.get(i.lower(), '00')) for lv, t, i in toc_entries)
        return rows
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page()
        body1 = body_parts.replace('{{TOC}}', toc_html({}))
        p1 = os.path.join(DIR, '_pass1.pdf')
        render(pg, page_html(body1), p1, foot_label)
        # find markers
        pages = {}
        import subprocess
        txt = subprocess.run(['pdftotext', p1, '-'], capture_output=True, text=True).stdout
        for n, t in enumerate(txt.split('\f')):
            for m in re.finditer(r'@@([A-Za-z0-9_\-]+)@@', t):
                pages.setdefault(m.group(1).lower(), str(n + 1))
        missing = [i for _, _, i in toc_entries if i.lower() not in pages]
        if missing: print('TOC markers missing:', missing[:10])
        body2 = body_parts.replace('{{TOC}}', toc_html(pages))
        body2 = re.sub(r'<span class="mk">@@[A-Za-z0-9_\-]+@@</span>', '', body2)
        p2 = os.path.join(DIR, '_pass2.pdf')
        render(pg, page_html(body2), p2, foot_label)
        txt2 = subprocess.run(['pdftotext', p2, '-'], capture_output=True, text=True).stdout.split('\f')
        norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
        bad = []
        for lv, t, i in toc_entries:
            pn = pages.get(i.lower())
            if not pn: continue
            key = norm(re.sub(r'^\d+\.\s+', '', t))[:24]
            if key and key not in norm(txt2[int(pn) - 1]): bad.append((t, pn))
        print('TOC check: %d entries, %d not found on their page' % (len(toc_entries), len(bad)), bad[:5])
        pc = os.path.join(DIR, '_cover.pdf')
        tmp = os.path.join(DIR, '_cover.html')
        open(tmp, 'w').write('<!doctype html><html><head><meta charset="utf-8"><style>%s</style></head><body>%s</body></html>' % (COVER_CSS, cover_html))
        pg.goto('file://' + tmp); pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready')
        pg.pdf(path=pc, width='8.5in', height='11in', print_background=True, prefer_css_page_size=True)
        b.close()
    w = PdfWriter()
    for f in (pc, p2):
        for p in PdfReader(f).pages: w.add_page(p)
    # outline from p2 is lost on merge; rebuild bookmarks from toc entries
    parent = None
    for lv, t, i in toc_entries:
        if i.lower() in pages:
            pn = int(pages[i.lower()])  # body page index (1-based) -> merged index = pn (cover is 0)
            if lv == 1: parent = w.add_outline_item(t, pn)
            else: w.add_outline_item(t, pn, parent=parent)
    w.add_metadata({'/Title': title, '/Author': author})
    w.page_mode = '/UseOutlines'
    with open(out, 'wb') as f: w.write(f)
    return pages


def cover(kicker, title_html, sub, foot_l, foot_r, shot=None):
    s = ('<div class="shot"><img src="%s"></div>' % img_uri(shot)) if shot else ''
    return ('<div class="cover"><div class="hex">%s</div><div class="brand">%s<div><div class="bn">HENDRIX</div><div class="bs">QUALITY MANAGEMENT</div></div></div>'
            '<div class="t"><div class="kicker">%s</div><h1>%s</h1><div class="sub">%s</div><div class="bar"></div></div>%s'
            '<div class="foot"><span>%s</span><span>%s</span></div></div>') % (logo(560), logo(44), kicker, title_html, sub, s, foot_l, foot_r)
