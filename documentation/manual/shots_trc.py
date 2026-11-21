# Screenshot of the Training Center library for the manual (Training chapter): python3 documentation/manual/shots_trc.py
# Signs in a made-up technician against a mock; the page scrub turns the company name into the made-up one.
import os, sys, subprocess, tempfile, json, urllib.parse
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(D, '..', '..'))
sys.path.insert(0, D); import scrub; scrub.install()
from playwright.sync_api import sync_playwright
out = tempfile.mkdtemp(prefix='hxtc_')
subprocess.run([os.path.join(ROOT, 'tools', 'build_site.sh'), out], check=True, capture_output=True)
cat = json.loads(open(os.path.join(out, 'training', 'catalog.js')).read().split('window.HX_VIDEOS=', 1)[1].rstrip().rstrip(';'))
ALL = {a[0]: 0 for v in cat for a in v['access']}
P = {'approved': True, 'name': 'Lee Park', 'title': 'Production Technician', 'admin': False, 'mfa_needed': False,
     'access': {**ALL, 'linemap': 1, 'logs': 2, 'batch': 2, 'lineclear': 2, 'qms': 1, 'sops': 1, 'training': 1, 'receiving': 1}}
SBU = 'https://bqrncllndvzbhmxanitq.supabase.co'
def jr(route, j, st=200): return route.fulfill(status=st, content_type='application/json', body=json.dumps(j))
def handle(route, request):
    u = request.url
    if not u.startswith(SBU): return route.continue_() if u.startswith('file://') else route.abort()
    path = urllib.parse.urlparse(u).path
    if path.endswith('/auth/v1/token'): return jr(route, {'access_token': 'tok', 'refresh_token': 'r', 'expires_in': 3600, 'user': {'id': 'u-tok'}})
    if path.endswith('/auth/v1/user'): return jr(route, {'id': 'u-tok', 'factors': []})
    if path.endswith('/rpc/hx_my_training_profile'): return jr(route, P)
    return route.abort()
with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={'width': 1300, 'height': 900}, device_scale_factor=1.5); ctx.route('**/*', handle)
    pg = ctx.new_page(); pg.goto('file://' + out + '/training/index.html?company=summitsolutions'); pg.wait_for_selector('#signin')
    pg.locator('#email').fill('lee.park@northfieldlabs.com'); pg.locator('#pw').fill('x-password-1'); pg.locator('#go').click()
    pg.wait_for_selector('#lib:not([hidden])'); pg.wait_for_timeout(1200)
    pg.set_viewport_size({'width': 1300, 'height': pg.evaluate('document.body.scrollHeight') + 10}); pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(D, 'shots', 'qual_training_center.png'))
    print('shot qual_training_center.png'); b.close()
