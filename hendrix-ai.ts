// Hendrix QMS - Supabase Edge Function "hendrix-ai"
// Reads lab COAs (and later other documents) with Claude for the Hendrix app.
//
// Security: only a signed-in, approved Hendrix user with at least Edit access to
// Testing can use it (checked with the user's own login through hx_perm). The
// Anthropic key stays in Supabase secrets and never reaches the browser.
//
// Deploy (Supabase dashboard, project bqrncllndvzbhmxanitq):
//   1. Edge Functions > Deploy a new function > Via Editor. Name it exactly: hendrix-ai
//   2. Paste this whole file, Deploy. Leave "Verify JWT" ON.
//   3. Edge Functions > Secrets: add ANTHROPIC_API_KEY = your Anthropic API key.
//      Optional: HX_AI_MODEL to choose another model.

import { createClient } from "jsr:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: { message: "POST only" } }, 405);
  try {
    const auth = req.headers.get("Authorization") || "";
    const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!, {
      global: { headers: { Authorization: auth } },
    });
    const { data: u } = await sb.auth.getUser();
    if (!u || !u.user) return json({ error: { message: "Sign in to Hendrix first." } }, 401);
    const { data: lvl, error: perr } = await sb.rpc("hx_perm", { p_mod: "testing" });
    if (perr) return json({ error: { message: "Access check failed: " + perr.message } }, 500);
    if (!lvl || lvl < 2) return json({ error: { message: "You need Edit access to Testing to read COAs." } }, 403);

    const key = Deno.env.get("ANTHROPIC_API_KEY");
    if (!key) return json({ error: { message: "ANTHROPIC_API_KEY is not set in Supabase Edge Function secrets." } }, 500);

    const body = await req.json();
    if (!Array.isArray(body.messages)) return json({ error: { message: "messages missing" } }, 400);
    const payload = {
      model: Deno.env.get("HX_AI_MODEL") || "claude-sonnet-4-6",
      max_tokens: Math.min(Number(body.max_tokens) || 4000, 8000),
      system: typeof body.system === "string" ? body.system : undefined,
      messages: body.messages,
    };
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    return new Response(await r.text(), { status: r.status, headers: { ...cors, "Content-Type": "application/json" } });
  } catch (e) {
    return json({ error: { message: String((e as Error)?.message || e) } }, 500);
  }
});
