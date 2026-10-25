// Tests the hendrix-metrc Edge Function in Node (no Deno needed): Supabase and METRC are faked.
// Run: node --experimental-strip-types tests/edge/test_metrc.mjs
import fs from 'node:fs'; import os from 'node:os'; import path from 'node:path'; import url from 'node:url';
const HERE = path.dirname(url.fileURLToPath(import.meta.url));
let src = fs.readFileSync(path.join(HERE, '..', '..', 'hendrix-metrc.ts'), 'utf8');
src = src.replace(/^import \{ createClient \} from "jsr:@supabase\/supabase-js@2";$/m, 'const { createClient } = globalThis.__stub;');
const tmp = path.join(os.tmpdir(), 'hx_metrc_' + process.pid + '.mts'); fs.writeFileSync(tmp, src);
let fails = 0, passes = 0;
const check = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); c ? passes++ : fails++; };
const ENV = { SUPABASE_URL: 'https://x.supabase.co', SUPABASE_ANON_KEY: 'anon', METRC_VENDOR_KEY: 'vend', METRC_USER_KEYS: '{"MAN000109":"usr"}' };
let handler; const calls = []; let LVL = 2; let METRC = 'v2';
globalThis.Deno = { env: { get: (k) => ENV[k] }, serve: (h) => { handler = h; } };
const P = (i, extra = {}) => ({ Id: i, Label: '1A400000000000000000' + i, Item: { Name: 'Cart ' + i, ProductCategoryName: 'Vape Cartridge' }, Quantity: 10 * i, UnitOfMeasureName: 'Each', LabTestingState: i === 2 ? 'TestFailed' : 'TestPassed', IsOnHold: i === 3, PackagedDate: '2026-10-0' + i, ProductionBatchNumber: 'B-' + i, LocationName: 'Vault', ...extra });
globalThis.__stub = { createClient: () => ({
  auth: { getUser: async (t) => t === 'good' ? { data: { user: { id: 'u1' } }, error: null } : { data: null, error: { message: 'bad' } } },
  rpc: async (fn, a) => { calls.push({ fn, a }); return fn === 'hx_perm' ? { data: LVL } : { data: 'ms-1', error: null }; },
  from: () => ({ select: () => ({ eq: (k, v) => ({ maybeSingle: async () => v === 'lic-mo' ? { data: { id: 'lic-mo', license_number: 'MAN000109', state_id: 'st-mo', hx_states: { name: 'Missouri' } } } : v === 'lic-mi' ? { data: { id: 'lic-mi', license_number: 'MI-9', hx_states: { name: 'Michigan' } } } : { data: null } }) }) }),
}) };
const seen = [];
globalThis.fetch = async (u, o) => { seen.push({ u, auth: o.headers.Authorization });
  if (METRC === 'deny') return new Response('no', { status: 401 });
  if (METRC === 'v1') { if (u.includes('/v2/')) return new Response('', { status: 404 }); return new Response(JSON.stringify([P(1), P(2)]), { status: 200 }); }
  const pg = Number(new URL(u).searchParams.get('pageNumber'));
  return new Response(JSON.stringify({ Data: pg === 1 ? [P(1), P(2)] : [P(3)], Total: 3, PageNumber: pg, PageSize: 20, TotalPages: 2 }), { status: 200 }); };
const mod = await import(url.pathToFileURL(tmp).href);
const call = async (body, tok = 'good') => { const r = await handler(new Request('https://x/functions/v1/hendrix-metrc', { method: 'POST', headers: { Authorization: 'Bearer ' + tok, 'Content-Type': 'application/json' }, body: JSON.stringify(body) })); return { status: r.status, j: await r.json() }; };

const row = mod.metrcRow(P(3));
check(row.tag === '1A4000000000000000003' && row.item === 'Cart 3' && row.category === 'Vape Cartridge' && row.quantity === '30' && row.unit === 'Each' && row.on_hold === true && row.packaged_date === '2026-10-03' && row.batch_no === 'B-3', 'METRC package mapped to a Hendrix row');
let r = await call({ lic: 'lic-mo' }, 'bad'); check(r.status === 401, 'refused without a valid sign-in');
LVL = 1; r = await call({ lic: 'lic-mo' }); check(r.status === 403 && /Edit access/.test(r.j.error.message), 'needs Edit access to METRC Check'); LVL = 2;
r = await call({ lic: 'lic-mi' }); check(r.status === 400 && /MI-9/.test(r.j.error.message) && /upload the METRC export/.test(r.j.error.message), 'no keys for a license: clear message, CSV still possible');
calls.length = 0; seen.length = 0; r = await call({ lic: 'lic-mo' });
const save = calls.find((c) => c.fn === 'hx_metrc_save');
check(r.status === 200 && r.j.packages === 3 && save.a.p_source === 'api' && save.a.p_rows.length === 3, 'all pages read and saved as a METRC snapshot');
check(seen[0].u.startsWith('https://api-mo.metrc.com/packages/v2/active?licenseNumber=MAN000109') && seen[0].auth === 'Basic ' + Buffer.from('vend:usr').toString('base64'), 'Missouri METRC address, vendor + user key');
METRC = 'v1'; calls.length = 0; r = await call({ lic: 'lic-mo' });
check(r.status === 200 && r.j.packages === 2, 'older METRC (v1) also works');
METRC = 'deny'; r = await call({ lic: 'lic-mo' });
check(r.status === 502 && /refused the keys/.test(r.j.error.message), 'METRC refusing the keys: the reason is shown');
fs.unlinkSync(tmp);
console.log('\nmetrc checks: ' + passes + ' passed, ' + fails + ' failed');
process.exit(fails ? 1 : 0);
