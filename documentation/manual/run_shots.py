# Re-take the manual screenshots for one chapter group against the current app:
#   python3 documentation/manual/run_shots.py qual
# Uses tests/browser/mock_c.py (the mock Supabase) and scrub.py (fictional names on every shot).
import sys, os, re
D = os.path.dirname(os.path.abspath(__file__))
G = sys.argv[1]
OLD = '/tmp/claude-0/-home-claude/6a741574-ee1e-59de-bdb0-5e888d18b162/scratchpad/'
W = os.path.join(D, '_work') + '/'
os.makedirs(W + 'manual', exist_ok=True)
SHOTDIR = os.path.join(D, 'shots')
os.makedirs(SHOTDIR, exist_ok=True)
if not os.path.exists(W + 'manual/shots'): os.symlink(SHOTDIR, W + 'manual/shots')
MOCK = os.path.abspath(os.path.join(D, '..', '..', 'tests', 'browser', 'mock_c.py'))
if not os.path.exists(W + 'mock_c.py'): os.symlink(MOCK, W + 'mock_c.py')
sys.path.insert(0, D)
# The screenshot scripts were written for Release 41 (late October 2026) and their sample data is dated around then.
# Freeze "today" there, in Python and in the browser, so "last 30 days", "this month" and "overdue" read the same.
import datetime as _d
FROZEN = _d.datetime(2026, 10, 25, 20, 0, 0, tzinfo=_d.timezone.utc)
class _FD(_d.date):
    @classmethod
    def today(cls): return cls(FROZEN.year, FROZEN.month, FROZEN.day)
class _FDT(_d.datetime):
    @classmethod
    def now(cls, tz=None):
        t = FROZEN if tz else FROZEN.replace(tzinfo=None) - _d.timedelta(hours=5)
        return cls(t.year, t.month, t.day, t.hour, t.minute, t.second, tzinfo=t.tzinfo) if tz is None else cls.fromtimestamp(FROZEN.timestamp(), tz)
    @classmethod
    def utcnow(cls): return cls(FROZEN.year, FROZEN.month, FROZEN.day, FROZEN.hour)
    @classmethod
    def today(cls): return cls.now()
_d.date = _FD; _d.datetime = _FDT
import playwright.sync_api as _s
_nc = _s.Browser.new_context
def _new_context(self, *a, **k):
    c = _nc(self, *a, **k)
    try: c.clock.install(time=FROZEN.timestamp())
    except Exception as e: print('clock not frozen:', e)
    return c
_s.Browser.new_context = _new_context
import scrub; scrub.install()
src = open(os.path.join(D, 'shots_%s.py' % G)).read().replace(OLD, W).replace("OUT + 'manual/", repr(W + 'manual/')[:-1] + "' + '")
src = re.sub(r"executable_path=('/opt/pw-browsers/[^']*'|BROWSER)", 'executable_path=CHROME', src)
import glob
CHROME = os.environ.get('HX_CHROME') or (sorted(glob.glob('/opt/pw-browsers/chromium_headless_shell-*/chrome-linux*/headless_shell')) or [None])[-1]
# --fiction: also rewrite the sample data (script and mock) to the made-up company, for pictures the page scrub can't reach (PDFs drawn from data)
if '--fiction' in sys.argv:
    def fic(t):
        for a, b in scrub.REPL:
            if 'app' in a and 'test' in a: continue   # keep the mock's URL
            t = re.sub(a, b, t)
        return t
    src = fic(src)
    mock_src = fic(open(MOCK).read())
    if os.path.islink(W + 'mock_c.py') or os.path.exists(W + 'mock_c.py'): os.remove(W + 'mock_c.py')
    open(W + 'mock_c.py', 'w').write(mock_src)
else:
    if os.path.exists(W + 'mock_c.py') and not os.path.islink(W + 'mock_c.py'): os.remove(W + 'mock_c.py')
    if not os.path.exists(W + 'mock_c.py'): os.symlink(MOCK, W + 'mock_c.py')
g = {'__file__': MOCK, '__name__': '__main__', 'CHROME': CHROME}
src = src.replace("with sync_playwright() as pw:", "with sync_playwright() as pw:\n    __import__('builtins').HX_PW = pw", 1)
try:
    exec(compile(src, 'shots_%s.py' % G, 'exec'), g)
except Exception:
    import traceback; traceback.print_exc()
    for k in ('pg', 'page', 'p'):
        try: g[k].screenshot(path='/tmp/dbg_%s.png' % G); print('debug shot /tmp/dbg_%s.png' % G); break
        except Exception: pass
    sys.exit(1)
