// Tests the hendrix-notify Edge Function in Node (no Deno needed): the Supabase client and Resend are faked.
// Run: node --experimental-strip-types tests/edge/test_notify.mjs
import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import url from 'node:url';
const HERE = path.dirname(url.fileURLToPath(import.meta.url));
let src = fs.readFileSync(path.join(HERE, '..', '..', 'hendrix-notify.ts'), 'utf8');
src = src.replace(/^import \{ createClient \} from "jsr:@supabase\/supabase-js@2";$/m, 'const { createClient } = globalThis.__stub;');
const tmp = path.join(os.tmpdir(), 'hx_notify_' + process.pid + '.mts'); fs.writeFileSync(tmp, src);
let fails = 0, passes = 0;
const check = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); c ? passes++ : fails++; };
const ENV = { SUPABASE_URL: 'https://x.supabase.co', SUPABASE_SERVICE_ROLE_KEY: 'svc', SUPABASE_ANON_KEY: 'anon', RESEND_API_KEY: 're_key', HX_MAIL_FROM: 'Hendrix QMS <qms@blackfox.test>', HX_CRON_SECRET: 'sekret' };
let handler; const sent = []; const rpcs = []; let resendFail = new Set();
globalThis.Deno = { env: { get: (k) => ENV[k] }, serve: (h) => { handler = h; } };
const TASKS = [{ kind: 'capa', group: 'mine', page: 'qms', title: 'CAPA C-1: Fix <filler>', detail: 'Priority major', due: '2026-10-20', overdue: true, ref: 'c1' },
               { kind: 'hold', group: 'approve', page: 'holds', title: 'Decide hold H-1: Gummies', detail: 'Foreign matter', due: null, overdue: false, ref: 'h1' }];
const DATA = {
  hx_task_digest: [{ user_id: 'u1', name: 'Sam', email: 'sam@x.test', licenses: [{ license_id: 'lic-mo', license: 'Black Fox', license_number: 'MAN000109', state: 'Missouri', tasks: TASKS }] },
                   { user_id: 'u2', name: 'Lee', email: 'lee@x.test', licenses: [{ license_id: 'lic-mo', license: 'Black Fox', tasks: [TASKS[0]] }] }],
  hx_notify_pending: [{ id: 7, kind: 'hold', title: 'Hold placed: H-2 Gummies', detail: 'Foreign matter', license: 'Black Fox', state: 'Missouri', created_at: '2026-10-25T14:00:00Z', recipients: [{ name: 'Sam', email: 'sam@x.test' }, { name: 'Kim', email: 'kim@x.test' }] },
                      { id: 8, kind: 'test_failed', title: 'Test FAILED: B-9', detail: '', license: 'Black Fox', created_at: '2026-10-25T14:00:00Z', recipients: [{ name: 'Bo', email: 'bo@x.test' }] }],
  hx_my_tasks: TASKS,
};
globalThis.__stub = { createClient: (u, key, opt) => ({
  rpc: async (fn, args) => { rpcs.push({ fn, args, key }); return { data: fn === 'hx_notify_sent' ? 1 : DATA[fn], error: null }; },
  auth: { getUser: async (t) => t === 'good' ? { data: { user: { id: 'u1', email: 'sam@x.test' } }, error: null } : { data: null, error: { message: 'bad jwt' } } },
  from: () => ({ select: () => ({ eq: () => ({ maybeSingle: async () => ({ data: { name: 'Sam' } }) }) }) }),
}) };
globalThis.fetch = async (u, o) => { const b = JSON.parse(o.body); sent.push({ u, auth: o.headers.Authorization, ...b });
  if (resendFail.has(b.to[0])) return new Response(JSON.stringify({ message: 'domain not verified' }), { status: 403 });
  return new Response('{"id":"e1"}', { status: 200 }); };
const mod = await import(url.pathToFileURL(tmp).href);
const call = async (body, headers = {}) => { const r = await handler(new Request('https://x/functions/v1/hendrix-notify', { method: 'POST', headers: { 'Content-Type': 'application/json', ...headers }, body: JSON.stringify(body) })); return { status: r.status, j: await r.json() }; };
const reset = () => { sent.length = 0; rpcs.length = 0; resendFail = new Set(); };

// templates
const d = mod.digestEmail('Sam', DATA.hx_task_digest[0].licenses, 'https://app/');
check(d.subject === 'Hendrix: 2 tasks waiting (1 overdue)' && d.items === 2, 'digest subject counts tasks and overdue');
check(d.html.includes('Waiting for you (1)') && d.html.includes('Waiting for your decision (1)') && d.html.includes('Overdue Oct 20, 2026'), 'digest groups tasks and shows overdue dates');
check(d.html.includes('Fix &lt;filler&gt;') && !d.html.includes('<filler>'), 'digest escapes record text');
check(d.text.includes('OVERDUE Oct 20, 2026') && d.text.includes('https://app/'), 'digest has a plain-text version');
const a = mod.alertEmail(DATA.hx_notify_pending[0], 'https://app/');
check(a.subject === 'Hendrix ALERT: Hold placed: H-2 Gummies (Black Fox)' && a.html.includes('10:00 AM ET'), 'alert subject and Eastern time');

// security
reset(); let r = await call({ mode: 'digest' });
check(r.status === 401 && sent.length === 0, 'scheduled modes refused without the secret');
r = await call({ mode: 'digest' }, { 'x-hendrix-cron': 'wrong' });
check(r.status === 401 && sent.length === 0, 'scheduled modes refused with a wrong secret');
r = await call({ mode: 'test', lic: 'lic-mo' }, { Authorization: 'Bearer nope' });
check(r.status === 401, 'test email refused without a valid sign-in');

// digest
reset(); r = await call({ mode: 'digest' }, { 'x-hendrix-cron': 'sekret' });
check(r.status === 200 && r.j.people === 2 && sent.length === 2 && sent[0].to[0] === 'sam@x.test' && sent[0].from === ENV.HX_MAIL_FROM && sent[0].auth === 'Bearer re_key', 'digest: one email per person through Resend');
const lg = rpcs.find((x) => x.fn === 'hx_notify_sent');
check(lg && lg.key === 'svc' && lg.args.p_log.length === 2 && lg.args.p_log.every((x) => x.kind === 'digest' && x.status === 'sent'), 'digest: logged with the service role');

// alerts
reset(); resendFail = new Set(['bo@x.test']); r = await call({ mode: 'alerts' }, { 'x-hendrix-cron': 'sekret' });
const s2 = rpcs.find((x) => x.fn === 'hx_notify_sent');
check(r.status === 200 && sent.length === 3 && JSON.stringify(s2.args.p_ids) === '[7]', 'alerts: sent to each recipient; an alert nobody received stays queued');
check(s2.args.p_log.filter((x) => x.status === 'failed').length === 1 && s2.args.p_log.find((x) => x.status === 'failed').error.includes('domain not verified'), 'alerts: Resend errors are logged');

// test email
reset(); r = await call({ mode: 'test', lic: 'lic-mo', license: 'Black Fox' }, { Authorization: 'Bearer good' });
check(r.status === 200 && r.j.sent_to === 'sam@x.test' && sent[0].subject.startsWith('Hendrix: 2 tasks') && rpcs.some((x) => x.fn === 'hx_my_tasks' && x.args.p_lic === 'lic-mo' && x.key === 'anon'), 'test email: my own tasks, read with my own sign-in, sent to me');

// not set up
reset(); delete ENV.RESEND_API_KEY; r = await call({ mode: 'test', lic: 'lic-mo' }, { Authorization: 'Bearer good' });
check(r.status === 502 && /RESEND_API_KEY/.test(r.j.error.message) && sent.length === 0, 'clear message when email is not set up');
fs.unlinkSync(tmp);
console.log('\nnotify checks: ' + passes + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
