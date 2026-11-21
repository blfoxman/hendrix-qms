"""In-depth Hendrix training videos, built from the user manual.

One narrated video per manual section (module): what it is, why we do it, when to use it, how to do the
main tasks and what Hendrix checks, read over the manual's screenshots with the button being talked
about highlighted. The words come from documentation/manual (understand.md and the chapters), so when
the manual is updated, the videos are rebuilt from it:

    python3 documentation/video/deep/deep.py                 # every section
    python3 documentation/video/deep/deep.py qms batch-tracker   # only these (slugs)
    python3 documentation/video/deep/deep.py --script qms   # print the narration, build nothing

Needs: piper-tts (pip), the voice file (HX_VOICE, default en-us-lessac-medium.onnx), tesseract, ffmpeg.
Writes site/training/media/deep/<slug>.mp4 and .jpg, and site/training/deep.js (the catalog).
"""
import os, sys, re, json, hashlib, wave, functools, subprocess, html as H
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAN = os.path.join(ROOT, 'documentation', 'manual')
sys.path.insert(0, MAN)
from build_manual import CHAPS, split_modules, load_understand
from build_web import ACCESS, slug

OUT = os.path.join(ROOT, 'site', 'training', 'media', 'deep')
CAT = os.path.join(ROOT, 'site', 'training', 'deep.js')
WORK = os.environ.get('HX_DEEP_WORK', '/tmp/hx_deep')
VOICE = os.environ.get('HX_VOICE', '/home/claude/cx/tts/lessac/en-us-lessac-medium.onnx')
W, H_, FPS = 1920, 1080, 30
FONTS = '/usr/share/fonts/opentype/inter/'
ANTON = '/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf'
GOLD, GOLDHI, INK, MUTED, BG = (212, 175, 55), (241, 213, 122), (244, 239, 227), (176, 168, 150), (10, 9, 7)
os.makedirs(OUT, exist_ok=True); os.makedirs(WORK + '/tts', exist_ok=True); os.makedirs(WORK + '/ocr', exist_ok=True)

@functools.lru_cache(None)
def font(name, size): return ImageFont.truetype(ANTON if name == 'anton' else FONTS + name, size)

# ---------------------------------------------------------------- words: manual -> narration
SAY = [(r'hendrixqms\.com', 'hendrix Q M S dot com'), (r'\bQMS\b', 'Q M S'), (r'\bSDS\b', 'S D S'), (r'\bCOAs\b', 'C O Ayes'), (r'\bCOA\b', 'C O A'),
       (r'\bMETRC\b', 'Metric'), (r'\bCAPAs\b', 'kay-pahs'), (r'\bCAPA\b', 'kay-pah'), (r'\bHACCP\b', 'hassip'), (r'\bCCPs\b', 'C C Ps'), (r'\bCCP\b', 'C C P'),
       (r'\bCSQ\b', 'C S Q'), (r'\bcGMP\b', 'C G M P'), (r'\bGMP\b', 'G M P'), (r'\bPPE\b', 'P P E'), (r'\bQR\b', 'Q R'), (r'\bCSV\b', 'C S V'), (r'\bPDF\b', 'P D F'),
       (r'\bQA\b', 'Q A'), (r'\bSOPs\b', 'S O Ps'), (r'\bSOP\b', 'S O P'), (r'\bSKUs\b', 'skews'), (r'\bSKU\b', 'skew'), (r'\bAI\b', 'A I'), (r'\bPIC\b', 'P I C'),
       (r'\bPHI\b', 'P H I'), (r'\bREI\b', 'R E I'), (r'\bIPM\b', 'I P M'), (r'\bIQ\b', 'I Q'), (r'\bOQ\b', 'O Q'), (r'\bPQ\b', 'P Q'), (r'\bEPA\b', 'E P A'),
       (r'\bRH\b', 'relative humidity'), (r'\bLOQ\b', 'L O Q'), (r'\bND\b', 'N D'), (r'\bR&D\b', 'R and D'), (r'\bHR\b', 'H R'), (r'\bKPIs\b', 'K P Is'), (r'\bKPI\b', 'K P I'),
       (r'\bCFR\b', 'C F R'), (r'\bALCOA\b', 'alcoa'), (r'\bTV\b', 'T V'), (r'\bID\b', 'I D'), (r'\bBHO\b', 'B H O'), (r'\bCUL\b', 'C U L'), (r'\bRCA\b', 'R C A'),
       (r'\bkWh\b', 'kilowatt hours'), (r'°F', ' degrees'), (r'(\d)\s?mL\b', r'\1 milliliters'), (r'(\d)\s?kg\b', r'\1 kilograms'), (r'(\d)\s?g\b', r'\1 grams'),
       (r'(\d)\s?mg\b', r'\1 milligrams'), (r'±', 'plus or minus '), (r'(\d)%', r'\1 percent'), (r'×', ' times '), (r'→', ' then '), (r'\be\.g\.', 'for example'),
       (r'\bN/A\b', 'not applicable'), (r'<', 'less than '), (r'&', ' and ')]
def say(t):
    t = re.sub(r'(^|\s)\+\s', r'\1', t)
    for a, b in SAY: t = re.sub(a, b, t)
    t = re.sub(r'\s+/\s+', ' or ', t)
    return t

def plain(md):
    """markdown -> plain text for captions and speech"""
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', md)
    t = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'\1', t); t = re.sub(r'\*([^*]+)\*', r'\1', t); t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('\\*', '*').replace('…', '...').replace('“', '"').replace('”', '"').replace('a ✓ or ✗', 'a tick or a cross').replace('✓ or ✗', 'a tick or a cross')
    t = re.sub(r'[✓✗🤖🔄👍📄⬇✍]\s*', '', t)
    t = re.sub(r'\s*\((?:for example|e\.g\.)?\s*[A-Z]{2,6}-(?:\d{4}-)?\d{2,4}(?:,[^)]*)?\)', '', t)   # (for example DEV-2026-009)
    t = re.sub(r',?\s*for example [A-Z]{2,6}-(?:\d{4}-)?\d{2,4},?', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def bolds(md): return [plain(b) for b in re.findall(r'\*\*([^*]+)\*\*', md)]

def split_sentences(t):
    parts = re.split(r'(?<=[.!?:])\s+(?=[A-Z"(])', t.strip())
    return [p.strip() for p in parts if len(p.strip()) > 1]

class Seg:
    """one spoken sentence: its text (md), the picture and what to highlight"""
    def __init__(self, md, img=None, kind='screen', label=''):
        self.md = md; self.img = img; self.kind = kind; self.label = label
        self.text = plain(md); self.hl = bolds(md)

@functools.lru_cache(None)
def module_images():
    """each module's first screenshot, to show while the overview chapter talks about that page"""
    out = {}
    for g, ct, _ in CHAPS:
        if g in ('front', 'flow'): continue
        for mt, mb in split_modules(open(os.path.join(MAN, 'ch_%s.md' % g)).read())[1]:
            im = re.findall(r'!\[[^\]]*\]\((shots/[^)]+)\)', mb)
            if im: out[mt] = im[0]
    return out

def table_rows(tbl):
    rows = [ln for ln in tbl.strip().split('\n') if ln.startswith('|') and not re.match(r'\|\s*-', ln)]
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    return cells[0], cells[1:]

HEAD_SAY = {'What happens': '', 'What it means': '', 'Meaning': '', 'In plain words': '', 'What it is': '', 'Who': 'Who', 'Where in Hendrix': 'In Hendrix',
            'The record it leaves': 'Record', 'Why it matters': 'Why it matters', 'Example': 'For example', 'Use': 'Use', 'Every day': 'Every day',
            'When it happens': 'When it happens', 'Read first': 'Read first', 'Who checks it': 'Checked by', 'What it asks for (examples)': 'It asks for',
            'In Hendrix': 'In Hendrix', 'What it means for you': 'For you', 'How Hendrix helps': 'How Hendrix helps'}
def overview_script(title, chapter, body):
    """the overview chapter: mostly tables, read row by row over the page each row is about"""
    segs = [Seg(title + '.', None, 'title', chapter)]; MI = module_images(); last_img = None
    for part in re.split(r'(\n(?:\|[^\n]*\n?)+)', body):
        if part.strip().startswith('|'):
            head, rows = table_rows(part)
            if head == ['Do', "Don't"]:
                for r in rows: segs.append(Seg('Do: ' + r[0] + '. Don\'t: ' + r[1][0].lower() + r[1][1:] + '.', last_img, 'flow', 'Do and don\'t'))
                continue
            for r in rows:
                names = re.findall(r'\*\*([^*]+)\*\*', ' '.join(r))
                img = next((MI[n] for n in names if n in MI), None) or last_img
                last_img = img
                lead = plain(r[0]).rstrip('.')
                bits = [lead + '.']
                for h, c in zip(head[1:], r[1:]):
                    c = plain(c).rstrip('.')
                    if not c: continue
                    k = HEAD_SAY.get(h, h)
                    bits.append((k + ': ' if k else '') + c + '.')
                seg = Seg(' '.join(bits), img, 'flow', lead); seg.text = ' '.join(bits); segs.append(seg)
        else:
            for para in [p for p in part.strip().split('\n\n') if p.strip()]:
                if para.startswith('!['): continue
                t = re.sub(r'^>\s*', '', para.replace('\n> ', ' ').replace('\n', ' '))
                for sn in split_sentences(t): segs.append(Seg(sn, last_img, 'why', 'The big picture'))
    segs.append(Seg('Each page is explained in its own video, and in the user manual.', None, 'end', ''))
    for x in segs: x.hl = []
    return segs

def script(title, chapter, body, U):
    """the narration of one module, as a list of Seg"""
    if chapter == 'How it all fits together': return overview_script(title, chapter, body)
    segs = []
    imgs_all = re.findall(r'!\[[^\]]*\]\((shots/[^)]+)\)', body)
    first_img = imgs_all[0] if imgs_all else None
    segs.append(Seg(title + '.', None, 'title', chapter))
    blocks = re.split(r'^### (.+)$', body, flags=re.M)
    intro = blocks[0]
    paras = [p for p in intro.strip().split('\n\n') if p.strip() and not p.startswith(('**Where', '**Who', '**CSQ', '!['))]
    if paras: segs += [Seg(s, first_img, 'screen') for s in split_sentences(paras[0].replace('\n', ' '))[:3]]
    # understand it first
    u = U.get(title)
    if u:
        for p in [p for p in u.split('\n\n') if p.strip()]:
            m = re.match(r'\*\*([^*]+)\*\*\s*(.*)', p, re.S)
            label = m.group(1).rstrip('.') if m else ''
            rest = (m.group(2) if m else p).strip()
            items = [x[2:].strip() for x in rest.split('\n') if x.startswith('- ')]
            lead = '\n'.join(x for x in rest.split('\n') if not x.startswith('- ')).strip()
            sents = split_sentences(lead.replace('\n', ' '))
            if label == 'Example': sents = ['For example: ' + sents[0][0].lower() + sents[0][1:]] + sents[1:] if sents else []
            if label == "If it's skipped": sents = ['If it\'s skipped: ' + sents[0][0].lower() + sents[0][1:]] + sents[1:] if sents else []
            for s in sents: segs.append(Seg(s, first_img, 'why', label))
            for it in items: segs.append(Seg(it.rstrip(';.') + '.', first_img, 'why', label))
    # the rest, section by section
    tips = []; said_fields = False
    for i in range(1, len(blocks), 2):
        h, b = blocks[i].strip(), blocks[i + 1]
        im = (re.findall(r'!\[[^\]]*\]\((shots/[^)]+)\)', b) or [None])[0]
        if h == 'Understand it first': continue
        if h.startswith('Tips'):
            tips = [x[2:] for x in b.split('\n') if x.startswith('- ')][:3]; continue
        if h == 'When to use it':
            rows = [ln for ln in b.split('\n') if ln.startswith('|') and not re.match(r'\|\s*-', ln)][1:]
            picked = []
            for ln in rows[:3]:
                c = [x.strip() for x in ln.strip().strip('|').split('|')]
                if len(c) >= 2: picked.append('When ' + c[0][0].lower() + c[0][1:].rstrip('.') + ': ' + c[1].rstrip('.') + '.')
            if picked: segs.append(Seg(h + '.', first_img, 'heading', h))
            segs += [Seg(s, first_img, 'screen', 'When to use it') for s in picked]
            continue
        if re.match(r'(The fields of|Fields on|Sections and)', h): continue
        lines = b.strip().split('\n')
        # the prose before the first list, table or picture
        prose = []
        for para in b.strip().split('\n\n'):
            if not para.strip(): continue
            if re.match(r'\s*(\||-\s|>|!|\d+\.\s|\*\*Fields|\*\*Sections)', para): break
            prose.append(re.split(r'\n(?=-\s|\d+\.\s)', para)[0])
            if re.search(r'\n(-\s|\d+\.\s)', para): break
        steps = [re.sub(r'^\d+\.\s*', '', ln.strip()) for ln in lines if re.match(r'^\d+\.\s', ln.strip())]
        bullets = [ln.strip()[2:] for ln in lines if ln.startswith('- ')]
        checks = [ln.lstrip('> ').lstrip('- ').strip() for ln in lines if ln.startswith('> - ')]
        if not checks:
            cm = re.search(r'^> \*\*Hendrix checks:\*\*\s*(.+)$', b, re.M)
            if cm: checks = split_sentences(cm.group(1))[:2]
        why = re.search(r'^> \*\*(Why[^*]*)\*\*\s*(.+)$', b, re.M)
        segs.append(Seg(h + '.', im or first_img, 'heading', h))
        for p in prose[:1]: segs += [Seg(s, im or first_img, 'screen', h) for s in split_sentences(p.replace('\n', ' '))[:3]]
        for k, s in enumerate(steps[:6]): segs.append(Seg(s if s.endswith('.') else s + '.', im or first_img, 'step', h))
        if not steps: segs += [Seg(x if x.endswith('.') else x + '.', im or first_img, 'screen', h) for x in bullets[:3]]
        if why: segs.append(Seg(why.group(1).rstrip(':') + ': ' + why.group(2), im or first_img, 'why', why.group(1).rstrip(':')))
        if checks: segs.append(Seg('Hendrix checks: ' + plain(checks[0]), im or first_img, 'check', 'Hendrix checks'))
        if '| Field |' in b and not said_fields: segs.append(Seg('The user manual lists every field of this form and what to enter.', im or first_img, 'screen', h)); said_fields = True
    if tips:
        segs.append(Seg('Tips.', first_img, 'heading', 'Tips'))
        segs += [Seg(t if t.endswith('.') else t + '.', first_img, 'screen', 'Tips') for t in tips[:2]]
    # keep it to about five minutes: drop the checks, then shorten the step lists
    def n(): return len(segs)
    if n() > 60: segs = [x for x in segs if x.kind != 'check']
    if n() > 60:
        out, run = [], 0
        for x in segs:
            run = run + 1 if x.kind == 'step' else 0
            if run <= 3: out.append(x)
        segs = out
    segs.append(Seg('Every field is explained in the user manual, in the Training Center.', None, 'end', ''))
    for s in segs:
        s.text = re.sub(r'\s+', ' ', s.text).strip()
        if s.kind in ('why', 'title', 'end', 'heading', 'check'): s.hl = []
    return [s for s in segs if s.text and len(s.text) > 2]

# ---------------------------------------------------------------- voice
_V = [None]
def tts(text):
    h = hashlib.md5(('d1|' + text).encode()).hexdigest()[:16]; p = WORK + '/tts/' + h + '.wav'
    if not os.path.exists(p):
        if _V[0] is None:
            from piper import PiperVoice
            _V[0] = PiperVoice.load(VOICE)
        from piper import SynthesisConfig
        with wave.open(p + '.tmp', 'wb') as w: _V[0].synthesize_wav(say(text), w, syn_config=SynthesisConfig(length_scale=1.03))
        os.replace(p + '.tmp', p)
    w = wave.open(p); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0; w.close()
    return x, sr

# ---------------------------------------------------------------- pictures
def shot_file(src):
    p = os.path.join(MAN, src)
    if os.path.exists(p): return p
    return os.path.join(ROOT, 'site', 'training', 'manual', 'img', os.path.splitext(os.path.basename(src))[0] + '.jpg')   # screenshots are not kept in git
@functools.lru_cache(None)
def shot(src): return Image.open(shot_file(src)).convert('RGB')

@functools.lru_cache(None)
def ocr_words(src):
    """tesseract word boxes of a screenshot (cached)"""
    p = shot_file(src); key = hashlib.md5((p + str(os.path.getmtime(p))).encode()).hexdigest()[:12]
    j = WORK + '/ocr/' + key + '.json'
    if not os.path.exists(j):
        r = subprocess.run(['tesseract', p, '-', 'tsv'], capture_output=True, text=True)
        out = []
        for ln in r.stdout.split('\n')[1:]:
            c = ln.split('\t')
            if len(c) == 12 and c[11].strip() and c[10] not in ('-1',) and float(c[10]) > 40:
                out.append((c[11].strip(), int(c[6]), int(c[7]), int(c[6]) + int(c[8]), int(c[7]) + int(c[9]), int(c[2]), int(c[3]), int(c[4])))
        json.dump(out, open(j, 'w'))
    return [tuple(x) for x in json.load(open(j))]

def norm(w): return re.sub(r'[^a-z0-9]', '', w.lower())
def find_phrase(src, phrase):
    """box of a phrase (a button or label) on the screenshot, or None"""
    toks = [norm(t) for t in phrase.split() if norm(t)]
    if not toks or len(toks) > 6: return None
    exact = len(toks) == 1   # one word: only the same word with the same capitals (a button label, not a word in a sentence)
    ws = ocr_words(src); best = None
    for i in range(len(ws)):
        if norm(ws[i][0]) != toks[0]: continue
        if exact and re.sub(r'[^A-Za-z0-9]', '', ws[i][0]) != re.sub(r'[^A-Za-z0-9]', '', phrase): continue
        j, k, box = i, 0, list(ws[i][1:5])
        while k < len(toks) and j < len(ws) and norm(ws[j][0]) == toks[k] and ws[j][5:8] == ws[i][5:8]:
            box = [min(box[0], ws[j][1]), min(box[1], ws[j][2]), max(box[2], ws[j][3]), max(box[3], ws[j][4])]; j += 1; k += 1
        if k == len(toks):
            iw = shot(src).width
            score = (1 if box[0] < iw * 0.16 else 0, box[1])   # not the left menu first, then the highest on the page
            if best is None or score < best[0]: best = (score, box)
    return best[1] if best else None

@functools.lru_cache(None)
def glow():
    im = Image.new('RGB', (W, H_), BG); d = ImageDraw.Draw(im)
    g = Image.new('L', (W // 4, H_ // 4), 0); dg = ImageDraw.Draw(g); dg.ellipse((W // 8 - 260, H_ // 8 - 200, W // 8 + 260, H_ // 8 + 160), fill=70)
    g = g.filter(ImageFilter.GaussianBlur(60)).resize((W, H_), Image.BILINEAR)
    return Image.composite(Image.new('RGB', (W, H_), (60, 48, 16)), im, g)

def logo(d, cx, cy, s):
    pts = [(20, 2), (36, 11), (36, 29), (20, 38), (4, 29), (4, 11)]
    P = [(cx + (x - 20) * s / 40, cy + (y - 20) * s / 40) for x, y in pts]
    d.line(P + [P[0]], fill=GOLD, width=max(3, int(s / 16)), joint='curve')
    k = s / 40
    for a, b in (((13, 12), (13, 28)), ((27, 12), (27, 28)), ((13, 20), (27, 20))):
        d.line((cx + (a[0] - 20) * k, cy + (a[1] - 20) * k, cx + (b[0] - 20) * k, cy + (b[1] - 20) * k), fill=GOLDHI, width=max(4, int(s / 12)))

def wrap(text, f, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if f.getlength(t) > width and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def card_frame(title, chapter, sub=''):
    im = glow().copy(); d = ImageDraw.Draw(im)
    logo(d, W / 2, 300, 130)
    d.text((W / 2, 430), chapter.upper(), font=font('Inter-SemiBold.otf', 30), fill=GOLD, anchor='mm')
    f = font('anton', 112 if len(title) < 24 else 92)
    for i, ln in enumerate(wrap(title.upper(), f, 1600)): d.text((W / 2, 540 + i * 120), ln, font=f, fill=INK, anchor='mm')
    if sub: d.text((W / 2, 860), sub, font=font('Inter-Medium.otf', 34), fill=MUTED, anchor='mm')
    d.text((W / 2, 1000), 'HENDRIX TRAINING CENTER  ·  IN DEPTH', font=font('Inter-Medium.otf', 24), fill=(150, 138, 100), anchor='mm')
    return im

def end_frame():
    im = glow().copy(); d = ImageDraw.Draw(im)
    logo(d, W / 2, 380, 150)
    d.text((W / 2, 560), 'Every field is in the user manual', font=font('Inter-Bold.otf', 58), fill=INK, anchor='mm')
    d.text((W / 2, 640), 'hendrixqms.com/training', font=font('Inter-SemiBold.otf', 44), fill=GOLDHI, anchor='mm')
    return im

def screen_frame(src, box):
    """the screenshot in a 16:9 window (full width, scrolled to the highlight), with the highlight"""
    im = shot(src); iw, ih = im.size
    if iw / ih < 1.25:   # phone or tall form: a card on the background
        bg = glow().copy(); s = min(940 / ih, 1500 / iw); sw, sh = int(iw * s), int(ih * s)
        sm = im.resize((sw, sh), Image.LANCZOS); x0, y0 = (W - sw) // 2, 40 + (940 - sh) // 2
        bg.paste(sm, (x0, y0)); d = ImageDraw.Draw(bg); d.rounded_rectangle((x0 - 2, y0 - 2, x0 + sw + 2, y0 + sh + 2), 12, outline=(70, 62, 40), width=2)
        rect = [x0 + box[0] * s, y0 + box[1] * s, x0 + box[2] * s, y0 + box[3] * s] if box else None
        return spot(bg, rect)
    vh = iw * 9 / 16
    if vh >= ih: top, vh2 = 0, ih
    else:
        vh2 = vh
        top = min(max(0, (box[1] + box[3]) / 2 - vh * 0.45), ih - vh) if box else 0
    crop = im.crop((0, int(top), iw, int(top + vh2))).resize((W, int(round(vh2 * W / iw))), Image.LANCZOS)
    fr = Image.new('RGB', (W, H_), BG); fr.paste(crop, (0, (H_ - crop.height) // 2))
    if box:
        s = W / iw; oy = (H_ - crop.height) // 2
        rect = [box[0] * s, (box[1] - top) * s + oy, box[2] * s, (box[3] - top) * s + oy]
    else: rect = None
    return spot(fr, rect)

def spot(fr, rect):
    if not rect: return fr
    pad = 12; r = [rect[0] - pad, rect[1] - pad, rect[2] + pad, rect[3] + pad]
    m = Image.new('L', (W // 2, H_ // 2), 150); d = ImageDraw.Draw(m); d.rounded_rectangle([v / 2 for v in r], 8, fill=0)
    m = m.filter(ImageFilter.GaussianBlur(5)).resize((W, H_), Image.BILINEAR)
    f = Image.composite(Image.new('RGB', (W, H_), (0, 0, 0)), fr, m)
    d = ImageDraw.Draw(f); d.rounded_rectangle(r, 12, outline=GOLDHI, width=4)
    return f

def concept_frame(src, label, text, kicker='UNDERSTAND IT FIRST'):
    """Understand it first: the idea in large type over the dimmed screen"""
    bg = screen_frame(src, None) if src else glow().copy()
    bg = bg.resize((W // 4, H_ // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H_), Image.BILINEAR)
    bg = Image.blend(bg, Image.new('RGB', (W, H_), (6, 5, 3)), 0.78)
    d = ImageDraw.Draw(bg)
    d.text((160, 250), kicker.upper(), font=font('Inter-SemiBold.otf', 30), fill=GOLD, anchor='ls')
    fl = font('Inter-Bold.otf', 64 if len(label) < 40 else 50)
    d.text((160, 330), label, font=fl, fill=GOLDHI, anchor='ls')
    d.line((160, 368, 300, 368), fill=GOLD, width=4)
    f = font('Inter-Medium.otf', 56); lines = wrap(text, f, 1560)
    if len(lines) > 6: f = font('Inter-Medium.otf', 46); lines = wrap(text, f, 1600)
    for i, ln in enumerate(lines): d.text((160, 470 + i * (f.size + 22)), ln, font=f, fill=INK, anchor='ls')
    return bg

def chip(fr, label):
    if not label: return fr
    d = ImageDraw.Draw(fr); f = font('Inter-SemiBold.otf', 28); w = f.getlength(label) + 44
    d.rounded_rectangle((40, 34, 40 + w, 34 + 52), 26, fill=(16, 14, 10), outline=GOLD, width=2)
    d.text((40 + w / 2, 60), label, font=f, fill=GOLDHI, anchor='mm')
    return fr

def caption(fr, text):
    if not text: return fr
    f = font('Inter-SemiBold.otf', 40); lines = wrap(text, f, 1560); lh = 54
    w = int(max(f.getlength(l) for l in lines)) + 64; h = lh * len(lines) + 34
    L = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L); d.rounded_rectangle((0, 0, w - 1, h - 1), 16, fill=(0, 0, 0, 215))
    for i, l in enumerate(lines): d.text((w / 2, 17 + lh * i + lh / 2 + 2), l, font=f, fill=INK + (255,), anchor='mm')
    o = fr.convert('RGBA'); o.alpha_composite(L, (int(W / 2 - w / 2), H_ - 44 - h))
    return o.convert('RGB')

def chunks(text, maxc=120):
    """caption pieces of a sentence"""
    if len(text) <= maxc: return [text]
    parts = re.split(r'(?<=[,;:])\s+', text); out, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) + 1 > maxc: out.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    if cur: out.append(cur)
    res = []
    for o in out:
        while len(o) > maxc + 30:
            k = o.rfind(' ', 0, maxc); res.append(o[:k]); o = o[k + 1:]
        res.append(o)
    return res

# ---------------------------------------------------------------- build one video
LABELS = {'why': 'Understand it first', 'check': 'Hendrix checks', 'step': '', 'heading': '', 'screen': ''}
def build(mod, U, only_script=False):
    segs = script(mod['t'], mod['chapter'], mod['body'], U)
    if only_script:
        for s in segs: print('[%s|%s|%s] %s%s' % (s.kind, s.label, os.path.basename(s.img or '-'), s.text, ('  {hl: %s}' % s.hl if s.hl else '')))
        return None
    d = WORK + '/' + mod['id']; os.makedirs(d, exist_ok=True)
    sr = 22050; audio = []; items = []; t = 0.0
    gap = {'title': 1.2, 'heading': 0.45, 'end': 1.0}
    for s in segs:
        x, sr = tts(s.text)
        lead = 0.35 if s.kind in ('heading',) else 0.12
        dur = len(x) / sr; g = gap.get(s.kind, 0.32)
        audio += [np.zeros(int(lead * sr), np.float32), x, np.zeros(int(g * sr), np.float32)]
        # picture
        if s.kind == 'title':
            base = card_frame(mod['t'], mod['chapter'], 'What it is, why we do it, and how')
            items.append((base, lead + dur + g)); t += lead + dur + g; continue
        if s.kind == 'why':
            items.append((concept_frame(s.img, s.label or 'What it is', s.text), lead + dur + g)); t += lead + dur + g; continue
        if s.kind == 'flow':
            shown = s.text[len(s.label) + 1:].strip() if s.text.startswith(s.label + '.') else s.text
            items.append((concept_frame(s.img, s.label, shown, mod['t']), lead + dur + g)); t += lead + dur + g; continue
        if s.kind == 'end' or not s.img:
            items.append((end_frame(), lead + dur + g + 0.8)); t += lead + dur + g + 0.8; continue
        box = None
        for b in (s.hl if s.label != 'When to use it' else []):
            box = find_phrase(s.img, b)
            if box: break
        fr = screen_frame(s.img, box)
        lab = s.label if s.kind in ('why', 'check') else (s.label if s.kind in ('heading', 'step') else '')
        fr = chip(fr, lab)
        pieces = chunks(s.text); tot = sum(len(p) for p in pieces)
        for k, p in enumerate(pieces):
            pd = (dur * len(p) / tot) + (lead if k == 0 else 0) + (g if k == len(pieces) - 1 else 0)
            items.append((caption(fr, p), pd)); t += pd
    # audio
    a = np.concatenate(audio + [np.zeros(int(0.8 * sr), np.float32)])
    a = a / (np.max(np.abs(a)) + 1e-9) * 0.89
    wav = d + '/voice.wav'
    with wave.open(wav, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())
    # pictures -> concat list with exact frame-aligned durations
    lst = []; acc = 0.0; frames_done = 0
    for i, (im, dur) in enumerate(items):
        p = d + '/f%04d.png' % i; im.save(p, compress_level=1)
        acc += dur; f_end = int(round(acc * FPS)); nf = max(1, f_end - frames_done); frames_done += nf
        lst.append("file '%s'\nduration %.5f" % (p, nf / FPS))
    lst.append("file '%s'" % (d + '/f%04d.png' % (len(items) - 1)))
    open(d + '/list.txt', 'w').write('\n'.join(lst) + '\n')
    tmp = os.path.join(OUT, mod['id'] + '.tmp.mp4'); out = os.path.join(OUT, mod['id'] + '.mp4')
    cmd = ['nice', 'ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', d + '/list.txt', '-i', wav,
           '-vf', 'fps=%d,format=yuv420p' % FPS, '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'stillimage', '-crf', '32', '-threads', '2',
           '-c:a', 'aac', '-b:a', '48k', '-ac', '1', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-shortest', '-movflags', '+faststart', tmp]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise SystemExit('ffmpeg failed: ' + r.stderr[-600:])
    os.replace(tmp, out)
    # poster: the first screen of the video, with the title
    items[0][0].resize((960, 540), Image.LANCZOS).save(os.path.join(OUT, mod['id'] + '.jpg'), quality=80)
    for f in os.listdir(d):
        if f.endswith('.png'): os.remove(os.path.join(d, f))
    secs = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip())
    print('built %s: %.0f s, %d sentences, %.1f MB' % (mod['id'], secs, len(segs), os.path.getsize(out) / 1e6), flush=True)
    return secs

def modules():
    out = []
    for ci, (g, ctitle, desc) in enumerate(CHAPS):
        if g == 'front': continue
        md = open(os.path.join(MAN, 'ch_%s.md' % g)).read()
        intro, mods = split_modules(md)
        for mt, mb in mods:
            out.append({'id': slug(mt), 't': mt, 'chapter': ctitle, 'ch': ci + 1, 'body': mb, 'a': ACCESS.get(mt, '') if g != 'flow' else ''})
    return out

def summary(mod, U):
    u = U.get(mod['t'], '')
    m = re.search(r'\*\*What it is\.\*\*\s*(.+?)(?:\n|$)', u)
    s = plain(m.group(1)) if m else plain(mod['body'].strip().split('\n\n')[0])
    s = split_sentences(s)[0] if split_sentences(s) else s
    return s if len(s) < 170 else s[:165].rsplit(' ', 1)[0] + '…'

def write_catalog(mods, U):
    cat = []
    for m in mods:
        f = os.path.join(OUT, m['id'] + '.mp4')
        if not os.path.exists(f): continue
        secs = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip())
        cat.append({'id': 'deep-' + m['id'], 'title': m['t'], 'chapter': m['chapter'], 'ch': m['ch'], 'summary': summary(m, U), 'a': m['a'],
                    'file': 'media/deep/' + m['id'] + '.mp4', 'poster': 'media/deep/' + m['id'] + '.jpg', 'seconds': round(secs, 1), 'manual': 'manual/#' + m['id']})
    open(CAT, 'w').write('window.HX_DEEP=' + json.dumps(cat, ensure_ascii=False, indent=0) + ';\n')
    print('catalog: %d videos, %.0f minutes' % (len(cat), sum(c['seconds'] for c in cat) / 60))

if __name__ == '__main__':
    U = load_understand(); M = modules()
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pick = [m for m in M if not args or m['id'] in args]
    if '--script' in sys.argv:
        for m in pick: print('=====', m['t']); build(m, U, True)
        sys.exit(0)
    for m in pick: build(m, U)
    write_catalog(M, U)
