# Español: the EN / ES switch, Spanish screen text (menus, forms, messages built in code), stored data unchanged, back to English
import re
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
ES = json.load(open(os.path.join(HERE, '..', '..', 'i18n', 'es.json'), encoding='utf8'))
errors = []
T['hx_sops'].append({'id': 'sop-zz', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Zebra line wipe-down', 'sop_number': 'SOP-ZZ-001', 'version': '1.0', 'status': 'published',
                     'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'steps': [], 'folder': 'General', 'category': '', 'description': '', 'regulatory_references': [], 'attachments': []})
T['hx_sops'].append({'id': 'sop-es', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'license_ids': ['lic-mo'], 'title': 'Glove change', 'sop_number': 'SOP-ES-001', 'version': '2.0', 'status': 'published',
                     'target_mode': 'license', 'target_role_ids': [], 'target_user_ids': [], 'steps': [], 'folder': 'General', 'category': '', 'description': '', 'regulatory_references': [], 'attachments': [],
                     'generated_content': {'purpose': 'Keep product clean.', 'scope': 'All rooms', 'steps': [{'step_number': 1, 'title': 'Wash', 'instruction': 'Wash hands for 20 seconds.'}, {'step_number': 2, 'title': 'Gloves', 'instruction': 'Put on new gloves.', 'critical': True}]}})
AIQ = []
def es_mark(x):
    if isinstance(x, str): return 'ES:' + x if x else x
    if isinstance(x, list): return [es_mark(i) for i in x]
    if isinstance(x, dict): return {k: es_mark(v) for k, v in x.items()}
    return x
def handle_es(route, request):
    if '/functions/v1/hendrix-ai' in request.url and request.post_data and 'You translate' in request.post_data:
        body = json.loads(request.post_data); AIQ.append(body['module'])
        src = json.loads(body['messages'][0]['content'])
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'content': [{'type': 'text', 'text': json.dumps(es_mark(src))}]}))
    return handle(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def es(s): return ES[s]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1400, 'height': 950}); ctx.route('**/*', handle_es)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('if(!sessionStorage.getItem("es_init")){sessionStorage.setItem("es_init","1");localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");localStorage.setItem("hx_lang","es");}' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('.side')
    side = pg.locator('.side')
    check(side.get_by_role('button', name=es('Batch Tracker'), exact=True).count() == 1 and side.get_by_role('button', name='Batch Tracker', exact=True).count() == 0, 'menu in Spanish (Batch Tracker -> %s)' % es('Batch Tracker'))
    check(pg.evaluate('document.documentElement.lang') == 'es', 'page language set to es')
    check(pg.locator('.top .langsw button', has_text='ES').get_attribute('class').find('ghost') < 0, 'ES is the active choice in the top bar')
    # a form: labels, options and buttons
    side.get_by_role('button', name=es('Facility Logs'), exact=True).first.click()
    pg.locator('.tabs button', has_text=es('GMP Hygiene Walk')).click()
    pg.get_by_role('button', name=es('+ New entry')).click(); md = pg.locator('.md')
    check(md.locator('span', has_text=es('No food, drinks, gum or tobacco in production or storage')).count() >= 1, 'form field labels in Spanish')
    check(md.get_by_role('button', name=es('Submit entry')).count() == 1, 'form buttons in Spanish')
    md.get_by_role('button', name=es('Cancel')).click()
    # stored data stays as written
    side.get_by_role('button', name=es('SOPs'), exact=True).click(); pg.wait_for_selector('text=Zebra line wipe-down')
    check(pg.locator('text=Zebra line wipe-down').count() >= 1, 'an SOP title (stored data) is shown as written')
    pg.screenshot(path=OUT + 'es_sops.png')
    txt = pg.locator('.main').inner_text()
    check('undefined' not in txt, 'no "undefined" on a Spanish screen')
    # sentence built in code: the fixed parts are translated
    gold = pg.locator('.card.gold', has=pg.get_by_role('button', name=es('Add them')))
    check(gold.count() >= 1 and not re.search(r'food safety SOPs are not in Hendrix yet', gold.first.inner_text()), 'a sentence built in code is translated (food safety banner): ' + (gold.first.inner_text()[:80] if gold.count() else '-'))
    # SOP text: a manager makes the Spanish version once; Spanish readers see it while the English is unchanged
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5)
    pg.locator('.card', has_text='Glove change').first.click(); md = pg.locator('.md')
    md.get_by_role('button', name=es('Translate to Spanish (AI)')).click(); md.locator('text=' + es('Spanish version: up to date')).wait_for(timeout=15000)
    s = next(x for x in T['hx_sops'] if x['id'] == 'sop-es')
    check(s.get('es') and s['es']['steps'][1]['text'] == 'ES:Put on new gloves.' and s['version'] == '2.0' and set(AIQ) == {'sops'}, 'Translate to Spanish saves the Spanish version on the SOP (version unchanged, AI as SOPs)')
    check(md.locator('text=ES:Put on new gloves.').count() == 1 and md.locator('text=ES:Keep product clean.').count() == 1, 'the SOP shows in Spanish in Spanish mode')
    s['generated_content']['steps'][1]['instruction'] = 'Put on new nitrile gloves.'
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5); side.get_by_role('button', name=es('Dashboard'), exact=True).click(); side.get_by_role('button', name=es('SOPs'), exact=True).click()
    pg.locator('.card', has_text='Glove change').first.click(); md = pg.locator('.md')
    md.locator('text=' + es('Spanish version: out of date (the English changed)')).wait_for(timeout=10000)
    check(md.locator('text=Put on new nitrile gloves.').count() == 1, 'after the English changes, the English is shown until it is translated again')
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5)
    # Translate all: every SOP without a current Spanish version, one after another
    btn = pg.get_by_role('button', name=re.compile(re.escape(es('🇪🇸 Translate all to Spanish ('))))
    n0 = len([x for x in T['hx_sops'] if x['status'] in ('published', 'draft') and x['license_id'] == 'lic-mo'])
    btn.click(); pg.wait_for_selector('.msg >> text=' + es('Spanish versions saved for '), timeout=30000)
    check(all(x.get('es') for x in T['hx_sops'] if x['status'] in ('published', 'draft') and x['license_id'] == 'lic-mo') and pg.get_by_role('button', name=es('🇪🇸 All in Spanish ✓')).count() == 1, 'Translate all to Spanish translates every SOP (%d) and then shows all done' % n0)
    pg.locator('.card', has_text='Zebra line wipe-down').first.click(); pg.locator('.md >> text=ES:Zebra line wipe-down').first.wait_for(timeout=8000)
    check(True, 'a translated SOP opens in Spanish')
    pg.keyboard.press('Escape'); pg.mouse.click(5, 5)
    r = pg.evaluate("""() => {const c={name:'GMP',lessons:[{title:'Hands',body:'Wash.'}],quiz:[{q:'When?',options:['Before','Never']}]};
      c.es={name:'BPM',lessons:[{title:'Manos',body:'Lavar.'}],quiz:[{q:'¿Cuándo?',options:['Antes','Nunca']}],sig:hxCourseEs.hash(JSON.stringify(hxCourseEs.source(c)))};
      const a=hxCourseEs.view(c)?hxCourseEs.view(c).lessons[0].title:null; c.lessons[0].body='Wash well.'; return [a, hxCourseEs.state(c)];}""")
    check(r == ['Manos', 'old'], 'course: Spanish lessons used while current, out of date after the English changes')
    # back to English
    pg.locator('.top .langsw').get_by_role('button', name='EN').click(); pg.wait_for_selector('.side >> text=Batch Tracker')
    check(pg.locator('.side').get_by_role('button', name='Batch Tracker', exact=True).count() == 1 and pg.evaluate('localStorage.getItem("hx_lang")') == 'en', 'EN switches back to English (and is remembered)')
    # sign-in screen has the switch too
    pg.evaluate('localStorage.removeItem("hx_session");localStorage.setItem("hx_lang","es")'); pg.reload(); pg.wait_for_selector('.auth')
    check(pg.locator('.auth .langsw').count() == 1, 'sign-in screen has the EN / ES switch')
    check(pg.locator('.auth').get_by_role('button', name=es('Sign in'), exact=True).count() >= 1, 'sign-in screen in Spanish')
    pg.screenshot(path=OUT + 'es_signin.png')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
