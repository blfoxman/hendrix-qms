// Hendrix QMS - Supabase Edge Function "hendrix-metrc"
// METRC Check: reads the license's active packages from the METRC API and saves them as a
// METRC snapshot in Hendrix (hx_metrc_save), so Hendrix can list every difference with its
// own records (hx_metrc_reconcile). Read only: it never changes anything in METRC.
//
// Security: only a signed-in Hendrix user with Edit access to METRC Check at that license
// (checked by the database with the user's own sign-in). The METRC keys stay in Supabase
// secrets and never reach the browser.
//
// Deploy (Supabase dashboard, project bqrncllndvzbhmxanitq):
//   1. Edge Functions > Deploy a new function > Via Editor. Name it exactly: hendrix-metrc
//   2. Paste this whole file, Deploy. Settings: turn "Verify JWT" OFF.
//   3. Edge Functions > Secrets:
//        METRC_VENDOR_KEY            your METRC integrator (software vendor) API key
//                                    (or METRC_VENDOR_KEY_MO / METRC_VENDOR_KEY_MI when they differ by state)
//        METRC_USER_KEYS             the user API key of each license, as JSON:
//                                    {"MAN000109":"user-key-1","AU-P-000123":"user-key-2"}
//      Optional: METRC_BASES = {"Missouri":"https://api-mo.metrc.com","Michigan":"https://api-mi.metrc.com"}

import { createClient } from "jsr:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });
const BASES: Record<string, string> = { missouri: "https://api-mo.metrc.com", michigan: "https://api-mi.metrc.com" };
const STATE_CODE: Record<string, string> = { missouri: "MO", michigan: "MI" };

// METRC package (v1 or v2) -> the row hx_metrc_save expects
export function metrcRow(p: Record<string, unknown>) {
  const item = (p.Item ?? {}) as Record<string, unknown>;
  const s = (v: unknown) => (v === null || v === undefined ? "" : String(v));
  return {
    tag: s(p.Label ?? p.PackageLabel ?? p.Tag),
    item: s(item.Name ?? p.ItemName ?? p.ProductName),
    category: s(item.ProductCategoryName ?? p.ProductCategoryName ?? p.ItemProductCategoryName),
    quantity: s(p.Quantity),
    unit: s(p.UnitOfMeasureName ?? p.UnitOfMeasureAbbreviation ?? item.UnitOfMeasureName),
    lab_state: s(p.LabTestingState ?? p.LabTestingStateName),
    on_hold: p.IsOnHold === true || p.IsOnHold === "true",
    packaged_date: s(p.PackagedDate).slice(0, 10),
    batch_no: s(p.ProductionBatchNumber ?? p.SourceProductionBatchNumbers),
    location: s(p.LocationName ?? p.Location),
  };
}

export async function fetchActive(base: string, auth: string, licNo: string, fetcher: typeof fetch = fetch) {
  const out: Record<string, unknown>[] = [];
  const h = { Authorization: "Basic " + auth, Accept: "application/json" };
  // v2 (paged)
  for (let page = 1; page <= 500; page++) {
    const r = await fetcher(base + "/packages/v2/active?licenseNumber=" + encodeURIComponent(licNo) + "&pageNumber=" + page + "&pageSize=20", { headers: h });
    if (r.status === 404 && page === 1) break; // older METRC: v1 below
    if (r.status === 401 || r.status === 403) throw new Error("METRC refused the keys for license " + licNo + " (" + r.status + "). Check METRC_VENDOR_KEY and the user key in METRC_USER_KEYS, and that the user key has access to this license.");
    if (!r.ok) throw new Error("METRC answered " + r.status + ": " + (await r.text()).slice(0, 200));
    const j = await r.json();
    const data = Array.isArray(j) ? j : (j.Data ?? []);
    out.push(...data);
    const total = Array.isArray(j) ? 1 : Number(j.TotalPages ?? 1);
    if (Array.isArray(j) || page >= total || data.length === 0) return out;
  }
  if (out.length) return out;
  const r = await fetcher(base + "/packages/v1/active?licenseNumber=" + encodeURIComponent(licNo), { headers: h });
  if (r.status === 401 || r.status === 403) throw new Error("METRC refused the keys for license " + licNo + " (" + r.status + "). Check METRC_VENDOR_KEY and the user key in METRC_USER_KEYS.");
  if (!r.ok) throw new Error("METRC answered " + r.status + ": " + (await r.text()).slice(0, 200));
  return (await r.json()) as Record<string, unknown>[];
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: { message: "POST only" } }, 405);
  try {
    const auth = req.headers.get("Authorization") || "", token = auth.replace(/^Bearer\s+/i, "").trim();
    if (!token) return json({ error: { message: "Sign in to Hendrix first." } }, 401);
    const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!, { global: { headers: { Authorization: auth } } });
    const { data: u, error: uerr } = await sb.auth.getUser(token);
    if (uerr || !u?.user) return json({ error: { message: "Hendrix sign-in was not accepted. Sign out, sign in again and retry." } }, 401);
    const body = await req.json().catch(() => ({}));
    const lic = String(body.lic || "");
    const { data: lvl } = await sb.rpc("hx_perm", { p_mod: "metrc" });
    if (!lvl || lvl < 2) return json({ error: { message: "You need Edit access to METRC Check." } }, 403);
    const { data: L, error: lerr } = await sb.from("hx_licenses").select("id,license_number,state_id,hx_states(name)").eq("id", lic).maybeSingle();
    if (lerr || !L) return json({ error: { message: "License not found or not yours." } }, 404);
    const stateName = String((L as any).hx_states?.name || "").toLowerCase();
    const licNo = String(L.license_number || "").trim();
    let bases = BASES;
    try { const b = Deno.env.get("METRC_BASES"); if (b) bases = { ...BASES, ...Object.fromEntries(Object.entries(JSON.parse(b)).map(([k, v]) => [k.toLowerCase(), String(v)])) }; } catch (_) { /* default */ }
    const base = bases[stateName];
    if (!base) return json({ error: { message: "No METRC address for the state " + stateName + ": add it to METRC_BASES." } }, 400);
    const code = STATE_CODE[stateName] || "";
    const vendor = Deno.env.get("METRC_VENDOR_KEY_" + code) || Deno.env.get("METRC_VENDOR_KEY");
    let userKeys: Record<string, string> = {};
    try { userKeys = JSON.parse(Deno.env.get("METRC_USER_KEYS") || "{}"); } catch (_) { return json({ error: { message: "METRC_USER_KEYS is not valid JSON." } }, 500); }
    const userKey = userKeys[licNo];
    if (!vendor || !userKey) return json({ error: { message: "METRC keys are not set for license " + licNo + ": add METRC_VENDOR_KEY and this license in METRC_USER_KEYS (Supabase > Edge Functions > Secrets). Until then, upload the METRC export (CSV)." } }, 400);
    const pk = await fetchActive(base, btoa(vendor + ":" + userKey), licNo);
    const rows = pk.map(metrcRow).filter((r) => r.tag);
    if (!rows.length) return json({ error: { message: "METRC has no active packages for license " + licNo + "." } }, 404);
    const { data: snap, error: serr } = await sb.rpc("hx_metrc_save", { p_lic: lic, p_source: "api", p_file: "METRC API " + licNo, p_rows: rows });
    if (serr) return json({ error: { message: serr.message } }, 500);
    return json({ ok: true, snapshot: snap, packages: rows.length });
  } catch (e) {
    return json({ error: { message: String((e as Error).message || e) } }, 502);
  }
});
