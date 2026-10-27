import re, subprocess, copy
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_c.py')).read())
ROSTER = [{'id': ADMIN, 'name': 'Sam', 'role_ids': [], 'license_ids': [], 'is_admin': True}, {'id': 'u-lee', 'name': 'Lee Worker', 'role_ids': ['r1'], 'license_ids': ['lic-mo'], 'is_admin': False}]
AIQ = []
META = {'sop_number': 'SOP-[DEPT]-[3digit]', 'title': 'Pre-Roll Infusion', 'revision': '1.0', 'department': 'Production', 'purpose': 'Infuse pre-rolls safely.', 'scope': 'Pre-roll room.',
        'regulatory_references': ['19 CSR 100-1.x'], 'responsibilities': [{'role': 'Lead', 'responsibility': 'Oversees'}], 'required_materials': ['Gloves'], 'deviation_procedure': 'Stop and tell QA.', 'training_requirements': 'Annual.'}
STEPS = {'steps': [{'step_number': 1, 'title': 'Prep', 'instruction': 'Sanitize the bench.', 'critical': False}, {'step_number': 2, 'title': 'Infuse', 'instruction': 'Apply 0.5 g oil.', 'regulatory_note': 'Record in METRC', 'critical': True}],
         'quality_checks': ['Weight check'], 'documentation_required': ['Batch record']}
def me_name(): return 'Sam'
_h = handle
def handle(route, request):
    u = request.url
    if '/functions/v1/hendrix-ai' in u:
        b = json.loads(request.post_data); AIQ.append(b)
        prompt = b['messages'][0]['content']; prompt = prompt if isinstance(prompt, str) else prompt[-1]['text']
        out = META if 'Respond with ONLY this JSON (no markdown, be concise)' in prompt else STEPS
        return route.fulfill(status=200, content_type='application/json', body=json.dumps({'content': [{'type': 'text', 'text': json.dumps(out)}]}))
    if '/rest/v1/rpc/hx_sop_roster' in u:
        return route.fulfill(status=200, content_type='application/json', body=json.dumps(ROSTER))
    if '/rest/v1/hx_sops' in u and request.method in ('POST', 'PATCH'):
        body = json.loads(request.post_data)
        if request.method == 'POST':
            body.update({'created_at': now(), 'updated_at': now(), 'created_by': 'Sam', 'created_by_id': ADMIN, 'license_ids': body.get('license_ids') or [body['license_id']],
                         'previous_folder': '', 'revision_note': body.get('revision_note', ''), 'approved_by': '', 'approved_at': None, 'effective_date': body.get('effective_date'), 'next_review': body.get('next_review'),
                         'target_mode': body.get('target_mode', 'license'), 'target_role_ids': body.get('target_role_ids', []), 'target_user_ids': body.get('target_user_ids', []), 'attachments': body.get('attachments', []), 'generated_content': body.get('generated_content')})
            if any(x['license_id'] == body['license_id'] and x.get('sop_number') and x['sop_number'].lower() == (body.get('sop_number') or '').lower() for x in T['hx_sops']):
                return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'duplicate key value violates unique constraint "hx_sops_number"'}))
            if body.get('status') == 'published': body.update({'approved_by': 'Sam', 'approved_at': now(), 'effective_date': body.get('effective_date') or '2026-10-23', 'next_review': body.get('next_review') or '2027-10-23'})
            T['hx_sops'].append(body); return route.fulfill(status=201, content_type='application/json', body=json.dumps([body]))
        sid = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)['id'][0].replace('eq.', '')
        r = next(x for x in T['hx_sops'] if x['id'] == sid); old = copy.deepcopy(r)
        content = any(k in body and body[k] != r.get(k) for k in ('title', 'description', 'steps', 'generated_content', 'sop_number', 'attachments'))
        if old['status'] == 'published' and (content or ('version' in body and body['version'] != r['version'])):
            if body.get('version', r['version']) == r['version']: return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'Changing a published SOP is a revision: give it a new version number.'}))
            T['hx_sop_versions'].append({'id': 'v%d' % len(T['hx_sop_versions']), 'sop_id': sid, 'version': old['version'], 'snapshot': old, 'revision_note': body.get('revision_note', ''), 'superseded_by': 'Sam', 'superseded_at': now(), 'license_id': old['license_id']})
            body.update({'revised_by': 'Sam', 'approved_by': 'Sam', 'approved_at': now()})
        if old['status'] == 'draft' and body.get('status') == 'published': body.update({'approved_by': 'Sam', 'approved_at': now(), 'effective_date': r.get('effective_date') or '2026-10-23', 'next_review': r.get('next_review') or '2027-10-23'})
        if body.get('status') == 'archived' and old['status'] != 'archived': body.update({'previous_folder': old['folder'], 'folder': 'Archived'})
        if body.get('status') == 'published' and old['status'] == 'archived': body['folder'] = old['previous_folder'] or 'General'
        r.update(body); return route.fulfill(status=200, content_type='application/json', body=json.dumps([r]))
    if '/rest/v1/hx_sop_acks' in u and request.method == 'POST':
        b = json.loads(request.post_data)
        if any(a['sop_id'] == b['sop_id'] and a['version'] == b['version'] and a['user_id'] == b['user_id'] for a in T['hx_sop_acks']):
            return route.fulfill(status=400, content_type='application/json', body=json.dumps({'message': 'duplicate key value violates unique constraint "hx_sop_acks_one"'}))
        b.update({'at': now(), 'role_names': 'Admin'}); T['hx_sop_acks'].append(b)
        return route.fulfill(status=201, content_type='application/json', body=json.dumps([b]))
    return _h(route, request)
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond: errors.append(msg)
def field(md, label):
    pgx = md if hasattr(md, 'goto') else md.page
    return md.locator('label.f, div.f', has=pgx.locator('span', has_text=re.compile('^' + re.escape(label)))).locator('input,select,textarea').first
def open_sop(pg, name):
    if pg.locator('.md').count():
        pg.locator('.md').get_by_role('button', name='Close').click() if pg.locator('.md').get_by_role('button', name='Close').count() else pg.mouse.click(5, 5)
        pg.wait_for_timeout(150)
    pg.locator('.card', has_text=name).first.click(); pg.wait_for_selector('.md')
def sign(pg):
    cv = pg.locator('.md canvas').last.bounding_box()
    pg.mouse.move(cv['x'] + 30, cv['y'] + 40); pg.mouse.down(); pg.mouse.move(cv['x'] + 200, cv['y'] + 90, steps=8); pg.mouse.up()
T['hx_roles'] += [{'id': 'r1', 'name': 'Team Member', 'description': 'Line', 'perms': {}, 'sort': 0}]
with sync_playwright() as pw:
    b = pw.chromium.launch(**LAUNCH)
    ctx = b.new_context(viewport={'width': 1300, 'height': 950}, accept_downloads=True); ctx.route('**/*', handle)
    sess = {'access_token': 't', 'refresh_token': 'r', 'expires_at': 9999999999, 'user': {'id': ADMIN}}
    ctx.add_init_script('localStorage.setItem("hx_session",%s);localStorage.setItem("hx_state","st-mo");localStorage.setItem("hx_lic","lic-mo");' % json.dumps(json.dumps(sess)))
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errors.append('JS: ' + str(e))); pg.on('dialog', lambda d: d.accept())
    pg.goto(BASE); pg.wait_for_selector('text=Dashboard')
    check(pg.locator('.nav button.soon', has_text='SOPs').count() == 0, 'SOPs is a live module (no Soon tag)')
    pg.get_by_role('button', name='SOPs', exact=True).click(); pg.wait_for_selector('text=No SOPs yet')
    # manual SOP
    pg.get_by_role('button', name='+ Manual SOP').click(); md = pg.locator('.md')
    field(md, 'Title').fill('Cart Filling'); field(md, 'Folder').select_option('Production')
    md.get_by_role('button', name='Suggest').click()
    check(field(md, 'Document number').input_value() == 'SOP-PRD-001', 'suggested document number SOP-PRD-001')
    md.locator('textarea[placeholder="Step 1..."]').fill('Inspect carts.'); md.get_by_role('button', name='+ Add step').click(); md.locator('textarea[placeholder="Step 2..."]').fill('Fill to 1.0 g.')
    md.locator('input[type=file]').set_input_files({'name': 'flow.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 x'}); pg.wait_for_selector('.md >> text=flow.pdf')
    md.get_by_role('button', name='Create SOP').click(); pg.wait_for_selector('.msg >> text=Created: Cart Filling')
    sop = T['hx_sops'][0]
    check(sop['status'] == 'draft' and sop['sop_number'] == 'SOP-PRD-001' and len(sop['steps']) == 2 and len(sop['attachments']) == 1 and sop['license_ids'] == ['lic-mo'], 'draft saved with number, steps, attachment')
    pg.get_by_role('button', name='✓ Approve & publish').click(); pg.wait_for_selector('.msg >> text=Published')
    check(sop['status'] == 'published' and sop['approved_by'] == 'Sam' and sop['next_review'], 'published with approver + review date')
    # sign
    open_sop(pg, 'Cart Filling')
    check(pg.locator('.md >> text=Lee Worker').count() == 1, 'pending list shows people who still must sign')
    pg.get_by_role('button', name='👍 I have read and understood this SOP').click(); sign(pg)
    pg.get_by_role('button', name='✓ Sign & acknowledge').click(); pg.wait_for_selector('.msg >> text=Signed')
    check(len(T['hx_sop_acks']) == 1 and T['hx_sop_acks'][0]['version'] == '1.0' and T['hx_sop_acks'][0]['signature'].startswith('data:image'), 'signature saved for v1.0')
    open_sop(pg, 'Cart Filling')
    check(pg.locator('.md >> text=You signed this version').count() == 1 and pg.locator('.md >> text=1 of 2 people').count() == 1, 'detail: signed + 1 of 2 people')
    # duplicate number refused
    if pg.locator('.md').count(): pg.get_by_role('button', name='Close').click()
    pg.get_by_role('button', name='+ Manual SOP').click(); md = pg.locator('.md'); field(md, 'Title').fill('Dup'); field(md, 'Document number').fill('sop-prd-001')
    md.get_by_role('button', name='Create SOP').click(); pg.wait_for_timeout(400)
    check(md.locator('.msg.err', has_text='already used').count() == 1, 'duplicate document number refused'); md.get_by_role('button', name='Cancel').click()
    # revise manually
    open_sop(pg, 'Cart Filling'); pg.get_by_role('button', name='🔄 Revise SOP').click(); md = pg.locator('.md')
    check(field(md, 'New version').input_value() == '1.1', 'next version suggested 1.1')
    md.get_by_role('button', name='Approve and publish v1.1').click(); pg.wait_for_timeout(200)
    check(md.locator('.msg.err', has_text='reason').count() == 1, 'revision needs a reason')
    field(md, 'Reason for revision').fill('Added weight check'); md.locator('textarea').nth(1).fill('Inspect carts and record the lot.')
    md.get_by_role('button', name='Approve and publish v1.1').click(); pg.wait_for_selector('.msg >> text=Revised')
    check(sop['version'] == '1.1' and len(T['hx_sop_versions']) == 1 and T['hx_sop_versions'][0]['version'] == '1.0' and T['hx_sop_versions'][0]['snapshot']['steps'][0]['text'] == 'Inspect carts.', 'v1.0 kept unchanged in version history')
    try: pg.locator('.card', has_text='Cart Filling').locator('.badge', has_text='Needs my signature').first.wait_for(timeout=5000)
    except Exception: pass
    check(pg.locator('.card', has_text='Cart Filling').locator('.badge', has_text='Needs my signature').count() == 1, 'new version needs signing again')
    open_sop(pg, 'Cart Filling'); pg.get_by_role('button', name='Version history').click()
    pg.wait_for_selector('.md >> text=Replaced because: Added weight check'); check(True, 'version history shows v1.0 and the reason'); pg.mouse.click(5, 5)
    open_sop(pg, 'Cart Filling')
    pg.get_by_role('button', name='👍 I have read and understood this SOP').click(); sign(pg); pg.get_by_role('button', name='✓ Sign & acknowledge').click(); pg.wait_for_selector('.msg >> text=Signed')
    # PDF
    open_sop(pg, 'Cart Filling')
    with pg.expect_download() as di: pg.get_by_role('button', name='📄 Download PDF').click()
    di.value.save_as(OUT + 'sop.pdf'); txt = subprocess.run(['pdftotext', '-layout', OUT + 'sop.pdf', '-'], capture_output=True, text=True).stdout
    check('HENDRIX QMS' in txt and 'SOP-PRD-001' in txt and 'Rev 1.1' in txt and 'Approved By' in txt.replace('APPROVED BY', 'Approved By') and 'Sam' in txt and 'uncontrolled' in txt, 'controlled-document PDF with number, revision, approval, signer')
    if pg.locator('.md').count(): pg.get_by_role('button', name='Close').click()
    # master list
    with ctx.expect_page() as pi: pg.get_by_role('button', name='Master list').click()
    pp = pi.value; pp.wait_for_load_state(); html = pp.content(); pp.close()
    check('SOP master list' in html and 'SOP-PRD-001' in html and '1 / 2' in html, 'master list prints numbers and signature counts')
    # AI generator
    pg.get_by_role('button', name='🤖 AI Generate SOP').click(); md = pg.locator('.md')
    field(md, 'SOP title').fill('Pre-Roll Infusion'); field(md, 'Category / department').select_option('Production — Pre-Roll Department')
    md.get_by_role('button', name='Generate SOP with AI').click(); pg.wait_for_selector('.md >> text=Save as draft')
    check(len(AIQ) == 2 and all(q.get('module') == 'sops' for q in AIQ), 'AI called twice with module=sops')
    check(md.locator('.badge', has_text='Critical').count() == 1, 'review shows critical step')
    md.get_by_role('button', name='Save as draft').click(); pg.wait_for_selector('.msg >> text=Created: Pre-Roll Infusion')
    ai = next(x for x in T['hx_sops'] if x['title'] == 'Pre-Roll Infusion')
    check(ai['status'] == 'draft' and ai['folder'] == 'Production' and ai['generated_content']['scope'] == 'Pre-roll room.' and ai['sop_number'] == '', 'AI SOP saved as draft (placeholder number dropped)')
    # archive + restore
    open_sop(pg, 'Cart Filling'); pg.get_by_role('button', name='Archive', exact=True).click(); pg.wait_for_selector('.msg >> text=Archived')
    check(sop['status'] == 'archived' and sop['folder'] == 'Archived', 'archived')
    open_sop(pg, 'zzz') if False else None
    if pg.locator('.md').count(): pg.locator('.md').get_by_role('button', name='Close').click()
    pg.locator('.tabs button', has_text='Archived').click(); open_sop(pg, 'Cart Filling'); pg.get_by_role('button', name='Restore').click(); pg.wait_for_selector('.msg >> text=Restored')
    check(sop['status'] == 'published' and sop['folder'] == 'Production', 'restored to its folder')
    pg.screenshot(path=OUT + 'sops_page.png')
    # standards evidence
    T['hx_standards'].append({'id': 's1', 'code': 'CSQ-MFG', 'name': 'CSQ Standard for Manufacturing', 'publisher': 'CSQ', 'version': '2.0', 'issued': '', 'scope': '', 'levels': [{'level': 1, 'name': 'Level 1', 'modules': ['1', '2A', '3C'], 'audit': ''}], 'modules': {'1': 'All', '2A': 'cGMP', '3C': 'P', '4A': 'H', '5': 'Q'}, 'audit_notes': [], 'file_path': '', 'file_name': ''})
    T['hx_license_standards'].append({'id': 'a1', 'state_id': 'st-mo', 'license_id': 'lic-mo', 'standard_id': 's1', 'target_level': 1, 'status': 'Following'})
    if pg.locator('.md').count(): pg.get_by_role('button', name='Close').click()
    pg.get_by_role('button', name='Standards (CSQ)').click(); pg.get_by_role('button', name='Update the standard').click(); pg.wait_for_selector('.msg >> text=Updated')
    r = pg.locator('div[style*="border-top"]', has=pg.locator('span', has_text=re.compile(r'^1\.4$'))).first; r.locator('div.row').first.click()
    check(r.locator('text=1 published, numbered and approved SOP').count() == 1 and r.locator('text=50% of required signatures done').count() == 1, '1.4 shows live SOP library evidence')
    pg.get_by_role('button', name='Dashboard').click(); pg.wait_for_selector('.card >> text=Open SOPs')
    check(pg.locator('.card', has_text='Open SOPs').locator('text=All signed').count() == 1, 'dashboard SOP card')
    # View-only member
    T['hx_profiles'][0]['role'] = 'member'; T['hx_profiles'][0]['perms'] = {'sops': 'read'}
    pg.reload(); pg.get_by_role('button', name='SOPs', exact=True).click(); pg.wait_for_selector('.card >> text=Cart Filling')
    check(pg.get_by_role('button', name='+ Manual SOP').count() == 0 and pg.get_by_role('button', name='🤖 AI Generate SOP').count() == 0, 'View: cannot create')
    open_sop(pg, 'Cart Filling')
    check(pg.get_by_role('button', name='🔄 Revise SOP').count() == 0 and pg.get_by_role('button', name='Archive', exact=True).count() == 0 and pg.get_by_role('button', name='📄 Download PDF').count() == 1, 'View: read + PDF only')
    b.close()
print('\nJS/assert errors:', errors if errors else 'none')
