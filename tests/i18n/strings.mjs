// Hendrix i18n: the English screen text of index.html and the server messages, checked against i18n/es.json.
//   node tests/i18n/strings.mjs check            -> "i18n checks: N passed, M failed" (missing Spanish = failed)
//   node tests/i18n/strings.mjs missing out.json -> writes the English strings that have no Spanish yet
// Needs acorn + acorn-walk (run_all.sh installs them into tests/i18n/node_modules when missing).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const acorn = require('acorn'), walk = require('acorn-walk');
const ROOT = path.join(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');

export function uiStrings() {
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  const css = [...html.matchAll(/<style>([\s\S]*?)<\/style>/g)].map(m => m[1]).join('\n');
  const classes = new Set([...css.matchAll(/\.([A-Za-z_][\w-]*)/g)].map(m => m[1]));
  const seen = new Set();
  for (const src of scripts) {
    let ast; try { ast = acorn.parse(src, { ecmaVersion: 2022, sourceType: 'script' }); } catch (e) { continue; }
    walk.full(ast, n => { if (n.type === 'Literal' && typeof n.value === 'string') seen.add(n.value); });
  }
  const out = new Set();
  for (const v of seen) {
    const t = v.trim();
    if (!/[A-Za-z]{2}/.test(t) || v.includes('\n') || v.length > 400) continue;            // long content (courses, SOP templates) is data
    if (/^[a-z0-9_\-.:\/#\[\]=*>+~ ,()]+$/.test(t) && !/ [a-z]{3,} [a-z]{3,} /.test(' ' + t + ' ') && !(/^\s|\s$/.test(v) && /[a-z]{3}/.test(t))) continue; // keys, selectors (a piece with a space at either end is screen text)
    if (t.split(/\s+/).every(w => classes.has(w))) continue;                                  // class names
    if (/^[\w-]+\s*:\s*[^;]+;/.test(t) || /;\s*[\w-]+\s*:/.test(t)) continue;                // inline css
    if (/^(https?:|data:|mailto:|blob:)/.test(t)) continue;
    if (/^\s*(select|insert|update|create|alter|drop|with)\s/i.test(t)) continue;
    if (/^(hx|st|lic|sop|v_)[a-z_]*$/.test(t) || /^[A-Z0-9_]+$/.test(t) || /^[a-z]+[A-Z]\w*$/.test(t)) continue;
    if (/^(image|application|text|font)\//.test(t) || /^\.?[\w-]+\.(png|jpg|pdf|csv|xlsx|json|html|js|sql|svg)$/i.test(t)) continue;
    if (v.includes('&select') || t.startsWith('&') || t.startsWith('?')) continue;
    if (/<\/?[a-z][^>]*>/.test(v) || v.includes('&middot;') || v.includes('&nbsp;')) continue; // printed records stay English
    if (/^(You are|Return ONLY|Reply with|Respond with|Output ONLY)/.test(t) || (/\bJSON\b/.test(v) && v.length > 80)) continue; // AI prompts
    out.add(v);
  }
  // count words built in code: ' open deviation' + (n === 1 ? '' : 's') -> also ' open deviations'
  for (const src of scripts) for (const m of src.matchAll(/'([^'\n]{2,80})'\s*\+\s*\(\s*[\w.\[\]()]+\s*===?\s*1\s*\?\s*'([^']*)'\s*:\s*'([^']*)'\s*\)/g)) {
    if (!/[A-Za-z]{3}/.test(m[1])) continue;
    out.add(m[1] + m[2]); out.add(m[1] + m[3]);
  }
  return out;
}
export function serverStrings() {
  const out = new Set();
  for (const f of fs.readdirSync(ROOT).filter(f => /^hendrix_step\d+\.sql$/.test(f))) {
    for (const m of fs.readFileSync(path.join(ROOT, f), 'utf8').matchAll(/raise exception\s+'((?:[^']|'')*)'/gi)) {
      const s = m[1].replace(/''/g, "'");
      for (const p of s.includes('%') ? s.split('%') : [s]) if (/[A-Za-z]{3}/.test(p)) out.add(p);
    }
  }
  for (const f of ['hendrix-ai.ts', 'hendrix-notify.ts', 'hendrix-metrc.ts']) {
    const p = path.join(ROOT, f); if (!fs.existsSync(p)) continue;
    for (const m of fs.readFileSync(p, 'utf8').matchAll(/message:\s*"((?:[^"\\]|\\.)*)"/g)) if (/[A-Za-z]{3}/.test(m[1])) out.add(JSON.parse('"' + m[1] + '"'));
  }
  return out;
}

const [cmd, outFile] = process.argv.slice(2);
if (cmd) {
  const es = JSON.parse(fs.readFileSync(path.join(ROOT, 'i18n', 'es.json'), 'utf8'));
  const all = new Set([...uiStrings(), ...serverStrings()]);
  const missing = [...all].filter(s => typeof es[s] !== 'string' || !es[s]).sort();
  if (cmd === 'missing') { fs.writeFileSync(outFile, JSON.stringify(missing, null, 0)); console.log('missing', missing.length); }
  else {
    let pass = 0, fail = 0;
    const chk = (c, m) => { if (c) pass++; else fail++; console.log((c ? 'PASS ' : 'FAIL ') + m); };
    chk(missing.length === 0, missing.length ? `${missing.length} screen texts have no Spanish in i18n/es.json, e.g. ${JSON.stringify(missing.slice(0, 5))} (node tests/i18n/strings.mjs missing x.json lists them)` : `every screen text (${all.size}) has Spanish`);
    const bad = Object.entries(es).filter(([k, v]) => typeof v !== 'string' || (k.match(/^\s*/)[0] !== v.match(/^\s*/)[0]) || (k.match(/\s*$/)[0] !== v.match(/\s*$/)[0]));
    chk(bad.length === 0, bad.length ? `${bad.length} Spanish entries change the spaces around the text, e.g. ${JSON.stringify(bad.slice(0, 3))}` : 'Spanish keeps the spaces around every piece of text');
    console.log(`i18n checks: ${pass} passed, ${fail} failed`);
  }
}
