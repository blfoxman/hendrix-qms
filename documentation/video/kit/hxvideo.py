"""hxvideo - make narrated training videos of the Hendrix QMS app running against the mock database.

One module: seed data (exec a manual/shots_<group>.py setup), record scenes with a visible cursor and
narration beats (CDP screencast), Kokoro TTS, captions (.srt + burned-in .ass), loudness normalization and
MP4 chapter markers. See KIT.md for a walkthrough.

A project is a directory (PROJECT). Layout it uses:
  PROJECT/narration.py     NARR = [(key, text), ...]; optional SAY = [(written, spoken), ...]
  PROJECT/tts/             beats/<key>.wav, meta.json, cache/   (made by synth())
  PROJECT/work/            frames_<scene>/, rec_<scene>.json, <scene>.mp4 ...  (made by Rec / build())
"""
import json, os, re, time, math, base64, shutil, subprocess, urllib.parse, hashlib, itertools, importlib.util
import datetime as _dt

SCR = '/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/'
MAN = SCR + 'manual/'
BROWSER = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'
KOKORO_MODEL = os.environ.get('HXV_KOKORO', SCR + 'video/tts/kokoro-v1.0.onnx')
KOKORO_VOICES = os.environ.get('HXV_VOICES', SCR + 'video/tts/voices-v1.0.bin')
ADMIN = '11111111-1111-1111-1111-111111111111'
SR = 24000
CDT = _dt.timezone(_dt.timedelta(hours=-5))
FIXED_DAY = _dt.datetime(2026, 10, 24, 10, 40, 0, tzinfo=CDT)   # browser clock for consistent dates
PROJECT = os.environ.get('HXV_PROJECT', os.getcwd())

# Pronunciation respellings used for the Hendrix tutorial (speech only; captions keep the written form)
DEFAULT_SAY = [('CAPAs', 'kay-pahs'), ('CAPA', 'kay-pa'), ('COA', 'C O A'), ('SKU', 'S K U'), ('CSV', 'C S V'),
               ('HACCP', 'hassip'), ('read only', 'read-only')]


def set_project(path):
    global PROJECT
    PROJECT = os.path.abspath(path); os.makedirs(PROJECT + '/work', exist_ok=True); os.makedirs(PROJECT + '/tts', exist_ok=True)
    return PROJECT


def P(*a): return os.path.join(PROJECT, *a)


# ----------------------------------------------------------------------------------------- seed data
def load_setup(group=None, path=None, snapshot=None):
    """Exec the setup part (everything before `with sync_playwright() as pw:`) of manual/shots_<group>.py
    (or any shots script via path=) in a fresh namespace. Returns the namespace: ns['T'] tables, ns['handle']
    route handler, ns['BASE'] app URL. The app HTML served is `snapshot` (copy index.html first!)."""
    assert snapshot, 'pass snapshot= (a copy of /home/claude/hendrix/index.html)'
    src = open(path or (MAN + 'shots_%s.py' % group)).read().split('with sync_playwright() as pw:')[0]
    src = src.replace("OUT + 'manual/bf_logo.png'", repr(P('work', 'bf_logo.png')))   # never write into manual/
    src = src.replace('/home/claude/hendrix/index.html', snapshot)
    ns = {'__name__': 'setup_%s' % (group or 'custom')}
    exec(compile(src, path or 'shots_%s.py' % group, 'exec'), ns)
    ns['HTML'] = open(snapshot).read()   # mock_c serves the namespace's global HTML
    return ns


def day_now(base_hour=15):
    """'now' for records the mock stamps (UTC, mid-morning in Missouri), real minutes/seconds."""
    t = time.gmtime(); return '2026-10-24T%02d:%02d:%02d.000Z' % (base_hour, t.tm_min, t.tm_sec)


# ----------------------------------------------------------------------------------------- browser
CURSOR_JS = r"""
(()=>{ if(window.__hxc) return; window.__hxc=1;
 function ripple(x,y){const r=document.createElement('div');r.style.cssText='position:fixed;left:'+(x-20)+'px;top:'+(y-20)+'px;width:40px;height:40px;border-radius:50%;border:3px solid #d4af37;background:rgba(212,175,55,.28);pointer-events:none;z-index:2147483646;transform:scale(.3);opacity:1;transition:transform .5s ease-out,opacity .5s ease-out';document.documentElement.appendChild(r);requestAnimationFrame(()=>requestAnimationFrame(()=>{r.style.transform='scale(1.7)';r.style.opacity='0'}));setTimeout(()=>r.remove(),700);}
 window.__ripple=ripple;
 const mk=()=>{ if(!document.documentElement) return setTimeout(mk,5);
  const c=document.createElement('div'); c.id='__cur';
  c.innerHTML='<svg width="30" height="30" viewBox="0 0 30 30"><path d="M4 3 L4 23.5 L9.4 18.3 L13.3 27 L17 25.4 L13.2 16.9 L20.6 16.6 Z" fill="#141414" stroke="#d4af37" stroke-width="1.9" stroke-linejoin="round"/></svg>';
  c.style.cssText='position:fixed;left:0;top:0;width:30px;height:30px;pointer-events:none;z-index:2147483647;transform:translate(-200px,-200px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.7))';
  document.documentElement.appendChild(c);
  let p=null; try{p=JSON.parse(sessionStorage.getItem('__curpos')||'null')}catch(_){}
  if(p) c.style.transform='translate('+(p[0]-4)+'px,'+(p[1]-3)+'px)';
  addEventListener('mousemove',e=>{c.style.transform='translate('+(e.clientX-4)+'px,'+(e.clientY-3)+'px)';try{sessionStorage.setItem('__curpos',JSON.stringify([e.clientX,e.clientY]))}catch(_){}},true);
  addEventListener('mousedown',e=>ripple(e.clientX,e.clientY),true);
 }; mk();
})();
"""


def session_script(uid=ADMIN, state='st-mo', lic='lic-mo', extra=''):
    """Init script that logs the user in (localStorage session) once per tab."""
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': uid}}
    return 'if(!sessionStorage.getItem("seeded")){sessionStorage.setItem("seeded","1");localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","%s");localStorage.setItem("hx_lic","%s");%s}' % (
        json.dumps(json.dumps(sess)), state, lic, extra)


def token_route(uid=ADMIN):
    """(pattern, handler) for a real-looking sign-in: POST /auth/v1/token returns a session."""
    def tok(route, request):
        if request.method == 'POST':
            return route.fulfill(status=200, content_type='application/json', body=json.dumps(
                {'access_token': 't', 'refresh_token': 'r', 'expires_in': 3600, 'expires_at': 9999999999, 'token_type': 'bearer', 'user': {'id': uid}}))
        return route.fallback()
    return ('**/auth/v1/token**', tok)


def launch(pw):
    return pw.chromium.launch(executable_path=BROWSER)


def new_context(browser, ns=None, *, fixed=FIXED_DAY, tz='America/Chicago', session=None, routes=()):
    """1440x810 CSS px at device scale 4/3 = 1920x1080 frames. ns: a load_setup() namespace (mock DB)."""
    ctx = browser.new_context(viewport={'width': 1440, 'height': 810}, device_scale_factor=4 / 3, timezone_id=tz, accept_downloads=True)
    if fixed is not None: ctx.clock.set_fixed_time(fixed)
    if ns is not None: ctx.route('**/*', ns['handle'])
    for pat, fn in routes: ctx.route(pat, fn)     # later routes win; use route.fallback() to pass on
    ctx.add_init_script(CURSOR_JS)
    if session: ctx.add_init_script(session)
    return ctx


def field(scope, label):
    """The input/select/textarea of a Hendrix form field by its label text (label.f / div.f > span)."""
    pg = scope if hasattr(scope, 'goto') else scope.page
    return scope.locator('label.f, div.f', has=pg.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first


# ----------------------------------------------------------------------------------------- recorder
class Rec:
    """Records one scene: CDP screencast frames + narration beats on the same clock.
    Use the helpers (click/type/select/point/wheel) so the cursor moves visibly and events keep flowing."""

    def __init__(self, ctx, page, name, meta=None):
        self.ctx, self.page, self.name = ctx, page, name
        self.dir = P('work', 'frames_' + name) + '/'
        shutil.rmtree(self.dir, ignore_errors=True); os.makedirs(self.dir)
        self.frames, self.beats, self.errors, self.lag = [], [], [], []
        self.meta = meta if meta is not None else load_meta()
        self.mx, self.my = 1100, 600
        self.cdp = None; self.t0 = None
        page.on('pageerror', lambda e: self.errors.append('JS: ' + str(e)))
        page.on('dialog', lambda d: d.accept())

    def _frame(self, p):
        path = self.dir + '%06d.jpg' % len(self.frames)
        with open(path, 'wb') as f: f.write(base64.b64decode(p['data']))
        self.frames.append((p['metadata']['timestamp'], path)); self.lag.append(time.time() - p['metadata']['timestamp'])
        try: self.cdp.send('Page.screencastFrameAck', {'sessionId': p['sessionId']})
        except Exception as e: self.errors.append('ack ' + str(e))

    def start(self):
        self.cdp = self.ctx.new_cdp_session(self.page)
        self.cdp.on('Page.screencastFrame', self._frame)
        self.cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 90, 'maxWidth': 1920, 'maxHeight': 1080, 'everyNthFrame': 1})
        self.page.mouse.move(self.mx, self.my); self.page.wait_for_timeout(600)
        self.t0 = time.time()

    def now(self): return time.time() - self.t0

    def stop(self, tail=1.0):
        self.page.wait_for_timeout(int(tail * 1000)); end = self.now()
        try: self.cdp.send('Page.stopScreencast')
        except Exception: pass
        self.page.wait_for_timeout(200)
        out = {'name': self.name, 'end': end, 'frames': [(ts - self.t0, p) for ts, p in self.frames], 'beats': self.beats, 'errors': self.errors}
        json.dump(out, open(P('work', 'rec_%s.json' % self.name), 'w'))
        print('scene %s: %.1fs, %d frames, errors %s' % (self.name, end, len(self.frames), self.errors))
        return out

    def beat(self, key, fn=None, pad=0.45):
        """Narration beat: audio `key` starts now, fn() runs, then wait until the audio (+pad) has played."""
        dur = self.meta[key]['dur'] if key in self.meta else 0.8
        t = self.now(); self.beats.append({'key': key, 't': t})
        if fn: fn()
        rem = t + dur + pad - self.now()
        if rem > 0: self.page.wait_for_timeout(int(rem * 1000))

    def wait(self, s): self.page.wait_for_timeout(int(s * 1000))   # never time.sleep: frames must keep flowing

    def snap(self, label):
        if os.environ.get('PROBE'):
            os.makedirs(P('work', 'probe'), exist_ok=True); self.page.screenshot(path=P('work', 'probe', '%s_%s.png' % (self.name, label)))

    def move(self, x, y, dur=None):
        x0, y0 = self.mx, self.my
        if dur is None: dur = min(1.0, max(0.35, math.hypot(x - x0, y - y0) / 1300))
        n = max(6, int(dur / 0.018))
        for i in range(1, n + 1):
            t = i / n; e = t * t * (3 - 2 * t)
            self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e); self.page.wait_for_timeout(14)
        self.mx, self.my = x, y

    def visible(self, loc, top=70, bottom=690):
        """Smooth-scroll loc into view, keeping it above the caption area (bottom ~120 px)."""
        loc.wait_for(state='visible', timeout=15000)
        bb = loc.bounding_box()
        if bb is None or bb['y'] < top or bb['y'] + min(bb['height'], 300) > bottom:
            loc.evaluate("e=>e.scrollIntoView({behavior:'smooth',block:'center'})")
            last = None
            for _ in range(40):
                self.page.wait_for_timeout(50); bb = loc.bounding_box()
                if last and bb and abs(bb['y'] - last['y']) < 0.5: break
                last = bb
        return loc.bounding_box()

    def point(self, loc, fx=0.5, fy=0.5, dur=None, scroll=True):
        bb = self.visible(loc) if scroll else loc.bounding_box()
        x = bb['x'] + (min(bb['width'] * fx, 260) if (fx == 0.5 and bb['width'] > 520) else bb['width'] * fx)
        self.move(x, bb['y'] + bb['height'] * fy, dur); return bb

    def click(self, loc, fx=0.5, fy=0.5, after=0.35):
        self.point(loc, fx, fy); self.page.wait_for_timeout(120)
        self.page.mouse.down(); self.page.wait_for_timeout(70); self.page.mouse.up()
        self.page.wait_for_timeout(int(after * 1000))

    def type(self, loc, text, delay=38, click=True, clear=False):
        if click: self.click(loc, fx=0.12 if (loc.bounding_box() or {'width': 0})['width'] > 200 else 0.5, after=0.15)
        if clear:
            self.page.keyboard.press('Control+a'); self.page.wait_for_timeout(250); self.page.keyboard.press('Backspace'); self.page.wait_for_timeout(200)
        for ch in text:
            self.page.keyboard.type(ch); self.page.wait_for_timeout(delay)
        self.page.wait_for_timeout(150)

    def select(self, loc, **kw):
        """Native <select> popups are not captured: move there, ripple, then select_option(**kw)."""
        self.point(loc, 0.3 if (loc.bounding_box() or {'width': 0})['width'] > 200 else 0.5); self.page.wait_for_timeout(120)
        self.page.evaluate('([x,y])=>window.__ripple&&window.__ripple(x,y)', [self.mx, self.my]); self.page.wait_for_timeout(250)
        loc.select_option(**kw); self.page.wait_for_timeout(350)

    def fill(self, loc, value):   # date/time inputs
        self.click(loc, fx=0.25, after=0.15); loc.fill(value); self.page.wait_for_timeout(250)

    def wheel(self, dy, steps=None):
        steps = steps or max(6, int(abs(dy) / 40))
        for _ in range(steps): self.page.mouse.wheel(0, dy / steps); self.page.wait_for_timeout(22)
        self.page.wait_for_timeout(250)

    def smooth_top(self):
        self.page.evaluate("window.scrollTo({top:0,behavior:'smooth'})"); self.page.wait_for_timeout(700)

    def sign(self, canvas):
        bb = self.visible(canvas); x0, y0 = bb['x'] + bb['width'] * 0.18, bb['y'] + bb['height'] * 0.6
        self.move(x0, y0); self.page.mouse.down()
        for i in range(1, 40):
            x = x0 + i * (bb['width'] * 0.6 / 40); y = y0 - bb['height'] * 0.22 * math.sin(i / 3.0) * (1 if i < 30 else 0.4)
            self.page.mouse.move(x, y); self.page.wait_for_timeout(16)
        self.page.mouse.up(); self.mx, self.my = x, y; self.page.wait_for_timeout(200)


# ----------------------------------------------------------------------------------------- narration (TTS)
def load_narration():
    spec = importlib.util.spec_from_file_location('narration', P('narration.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.NARR, getattr(m, 'SAY', DEFAULT_SAY)


def load_meta():
    try: return json.load(open(P('tts', 'meta.json')))
    except Exception: return {}


def sentences(t):
    return [s for s in re.split(r'(?<=[.!?])\s+(?=[A-Z\'"])', t.strip()) if s]


def synth(voice='af_heart', speed=1.0, gap=0.32, threads=2):
    """Generate tts/beats/<key>.wav and tts/meta.json for every NARR entry (sentence by sentence, cached)."""
    import numpy as np, soundfile as sf
    narr, say = load_narration()
    cache = P('tts', 'cache') + '/'; os.makedirs(cache, exist_ok=True); os.makedirs(P('tts', 'beats'), exist_ok=True)
    os.environ.setdefault('OMP_NUM_THREADS', str(threads))
    k = [None]
    def tts(text):
        for a, b in say: text = text.replace(a, b)
        p = cache + hashlib.sha1(('%s|%s|%s' % (voice, speed, text)).encode()).hexdigest()[:16] + '.wav'
        if not os.path.exists(p):
            if k[0] is None:
                from kokoro_onnx import Kokoro
                k[0] = Kokoro(KOKORO_MODEL, KOKORO_VOICES)
            s, sr = k[0].create(text, voice=voice, speed=speed, lang='en-us')
            idx = np.where(np.abs(s) > 0.006)[0]
            if len(idx): s = s[max(0, idx[0] - 600): idx[-1] + 2400]
            sf.write(p, s, sr)
        return sf.read(p)[0]
    meta = {}
    for key, text in narr:
        parts, audio, t = [], [], 0.0
        for s in sentences(text):
            a = tts(s); d = len(a) / SR
            parts.append({'text': s, 'start': round(t, 3), 'dur': round(d, 3)}); audio += [a, np.zeros(int(gap * SR))]; t += d + gap
        wav = np.concatenate(audio[:-1]); sf.write(P('tts', 'beats', key + '.wav'), wav, SR)
        meta[key] = {'dur': round(len(wav) / SR, 3), 'parts': parts, 'text': text}
    json.dump(meta, open(P('tts', 'meta.json'), 'w'), indent=1)
    print('narration: %d beats, %.1fs' % (len(meta), sum(m['dur'] for m in meta.values())))
    return meta


# ----------------------------------------------------------------------------------------- captions
QUOTE = r"(?<![A-Za-z])'[^']+'(?![A-Za-z])"


def chunks(text, maxlen=84):
    """Split a sentence into caption chunks of <= 2 lines (~42 chars), preferring breaks after punctuation."""
    if len(text) <= maxlen: return [text]
    words = text.split(' '); n = math.ceil(len(text) / (maxlen - 4))
    spans = [m.span() for m in re.finditer(QUOTE, text)]
    def bcost(i):
        prev, nxt = words[i - 1], words[i]; c = 0
        if re.search(r'[,:;]$', prev): c -= 30
        if any(a < len(' '.join(words[:i])) < b for a, b in spans): c += 80
        if re.match(r'^\d', nxt) or re.match(r'^\d', prev) or prev.lower() in ('a', 'an', 'the', 'to', 'of', 'and', 'from', 'with', 'for'): c += 25
        return c
    best = None
    for cut in itertools.combinations(range(1, len(words)), n - 1):
        parts = [' '.join(words[x:y]) for x, y in zip((0,) + cut, cut + (len(words),))]
        if max(len(p) for p in parts) > maxlen: continue
        cost = (max(map(len, parts)) - min(map(len, parts))) * 0.6 + sum(bcost(i) for i in cut)
        if best is None or cost < best[0]: best = (cost, parts)
    return best[1] if best else [text]


def two_lines(text, width=42):
    if len(text) <= width: return [text]
    words = text.split(' '); best = None; spans = [m.span() for m in re.finditer(QUOTE, text)]
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        score = max(len(a), len(b)) + (0 if len(a) <= width + 4 and len(b) <= width + 4 else 100) + (30 if any(x < len(a) < y for x, y in spans) else 0)
        if best is None or score < best[0]: best = (score, a, b)
    return [best[1], best[2]]


def _ts_srt(t):
    ms = int(round(t * 1000)); return '%02d:%02d:%02d,%03d' % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)


def _ts_ass(t):
    cs = int(round(t * 100)); return '%d:%02d:%02d.%02d' % (cs // 360000, cs // 6000 % 60, cs // 100 % 60, cs % 100)


ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Medium,44,&H00FFFFFF,&H00FFFFFF,&H48000000,&H48000000,0,0,0,0,100,100,0,0,4,14,0,2,200,200,46,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


# ----------------------------------------------------------------------------------------- build
def _run(cmd):
    p = subprocess.run(['nice', '-n', '10'] + cmd, capture_output=True, text=True)
    if p.returncode: print(p.stderr[-3000:]); raise SystemExit('ffmpeg failed: ' + ' '.join(cmd[:6]))


def _probe_dur(f):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)


def scene_captions(name, meta=None):
    meta = meta or load_meta(); R = json.load(open(P('work', 'rec_%s.json' % name))); caps = []
    for bt in R['beats']:
        for part in meta[bt['key']]['parts']:
            cs = chunks(part['text']); tot = sum(len(c) for c in cs); t0 = bt['t'] + part['start']
            for c in cs:
                d = part['dur'] * len(c) / tot; caps.append([t0, t0 + d, c]); t0 += d
    return caps


def build_scene(name, fade=0.35, force=False, threads=2):
    """frames -> constant 30 fps H.264 (each frame held until the next timestamp) + narration track."""
    import numpy as np, soundfile as sf
    rec = P('work', 'rec_%s.json' % name); out = P('work', '%s.mp4' % name); R = json.load(open(rec)); meta = load_meta()
    key = hashlib.sha1(json.dumps([R['end'], len(R['frames']), R['beats'], [meta[b['key']]['dur'] for b in R['beats']], fade]).encode()).hexdigest()
    if not force and os.path.exists(out) and os.path.exists(out + '.key') and open(out + '.key').read() == key:
        return _probe_dur(out)                     # unchanged recording + narration: reuse the encoded scene
    end = R['end']; fr = R['frames']
    pre = [f for f in fr if f[0] <= 0]; post = [f for f in fr if f[0] > 0]
    seq = ([(0.0, pre[-1][1])] if pre else [(0.0, post[0][1])]) + post
    lines = ["file '%s'\nduration %.4f" % (p, max((seq[i + 1][0] if i + 1 < len(seq) else end) - t, 0.001)) for i, (t, p) in enumerate(seq)]
    lines.append("file '%s'" % seq[-1][1])
    open(P('work', '%s_list.txt' % name), 'w').write('\n'.join(lines) + '\n')
    n = int((end + 0.05) * SR); aud = np.zeros(n)
    for bt in R['beats']:
        w, _ = sf.read(P('tts', 'beats', bt['key'] + '.wav')); s = int(bt['t'] * SR); e = min(n, s + len(w)); aud[s:e] += w[:e - s]
    sf.write(P('work', '%s.wav' % name), aud.astype(np.float32), SR)
    vf = 'fps=30,scale=1920:1080:flags=lanczos,format=yuv420p,fade=t=in:st=0:d=%.2f,fade=t=out:st=%.3f:d=%.2f' % (fade, max(0, end - fade), fade)
    _run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', P('work', '%s_list.txt' % name), '-i', P('work', '%s.wav' % name), '-vf', vf, '-t', '%.3f' % end,
          '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-threads', str(threads), '-r', '30', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', out])
    open(out + '.key', 'w').write(key)
    d = _probe_dur(out); print('built %s: %.2fs (%d frames, errors %s)' % (name, d, len(fr), R['errors'])); return d


def build(scenes, out_mp4, out_srt=None, loudnorm=True, chapters=True, threads=2):
    """scenes: [(scene_name, chapter_title), ...] in order. Writes out_mp4 (+ .srt) with burned-in captions,
    loudness normalized to -16 LUFS and one chapter per scene. Returns the timeline [(name, title, start, dur)]."""
    out_srt = out_srt or os.path.splitext(out_mp4)[0] + '.srt'
    meta = load_meta(); off = 0.0; caps = []; tl = []
    for name, title in scenes:
        d = build_scene(name, threads=threads)
        caps += [(a + off, b + off, t) for a, b, t in scene_captions(name, meta)]
        tl.append((name, title, off, d)); off += d
    caps.sort()
    for i in range(len(caps) - 1):
        if caps[i][1] > caps[i + 1][0] - 0.04: caps[i] = (caps[i][0], caps[i + 1][0] - 0.04, caps[i][2])
    srt, ass = [], [ASS_HEAD]
    for i, (a, b, t) in enumerate(caps):
        ls = two_lines(t)
        srt.append('%d\n%s --> %s\n%s\n' % (i + 1, _ts_srt(a), _ts_srt(b), '\n'.join(ls)))
        ass.append('Dialogue: 0,%s,%s,Cap,,0,0,0,,%s\n' % (_ts_ass(a), _ts_ass(b), '\\N'.join(ls)))
    open(out_srt, 'w').write('\n'.join(srt)); open(P('work', 'captions.ass'), 'w').write(''.join(ass))
    open(P('work', 'concat.txt'), 'w').write(''.join("file '%s'\n" % P('work', n + '.mp4') for n, _, _, _ in tl))
    _run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', P('work', 'concat.txt'), '-c', 'copy', P('work', 'joined.mp4')])
    af = ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000'] if loudnorm else ['-c:a', 'copy']
    _run(['ffmpeg', '-y', '-i', P('work', 'joined.mp4'), '-vf', "ass=%s:fontsdir=/usr/share/fonts/opentype/inter" % P('work', 'captions.ass'),
          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-threads', str(threads), '-pix_fmt', 'yuv420p', '-profile:v', 'high'] + af + [P('work', 'burned.mp4')])
    if chapters:
        md = [';FFMETADATA1']
        for name, title, start, d in tl:
            md += ['[CHAPTER]', 'TIMEBASE=1/1000', 'START=%d' % int(start * 1000), 'END=%d' % int((start + d) * 1000), 'title=%s' % title.replace('=', '\\=').replace(';', '\\;')]
        open(P('work', 'chapters.ffmetadata'), 'w').write('\n'.join(md) + '\n')
        _run(['ffmpeg', '-y', '-i', P('work', 'burned.mp4'), '-i', P('work', 'chapters.ffmetadata'), '-map', '0', '-map_metadata', '1', '-map_chapters', '1', '-codec', 'copy', '-movflags', '+faststart', out_mp4])
    else:
        shutil.copy(P('work', 'burned.mp4'), out_mp4)
    json.dump(tl, open(P('work', 'timeline.json'), 'w'))
    for name, title, s, d in tl: print('%5s  %d:%05.2f  %-40s (%.1fs)' % (name, s // 60, s % 60, title, d))
    print('total %.1fs, %d captions -> %s' % (off, len(caps), out_mp4))
    return tl
