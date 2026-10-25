// Hendrix QMS - Supabase Edge Function "hendrix-ai"
// Claude for the Hendrix app: reads lab COAs (Testing), writes / revises SOPs (SOPs),
// drafts online training courses from the state Rulebook (Training), organizes an
// uploaded rules PDF into the state Rulebook (Rulebook) and estimates ingredients for
// flavors with no saved formulation (Production Planner).
//
// Security: only a signed-in, approved Hendrix user with at least Edit access to the
// module making the request (Testing, SOPs, Rulebook or Production Planner; Full access for Training) can use it, checked with the user's own
// login through hx_perm. The Anthropic key stays in Supabase secrets and never reaches
// the browser. After changing this file, deploy it again (same name: hendrix-ai).
//
// Deploy (Supabase dashboard, project bqrncllndvzbhmxanitq):
//   1. Edge Functions > Deploy a new function > Via Editor. Name it exactly: hendrix-ai
//   2. Paste this whole file, Deploy. Then Settings: turn "Verify JWT with legacy secret" OFF
//      (this function checks the Hendrix sign-in and access level itself).
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
    // the signed-in user's token must be passed to getUser (an Edge Function has no stored session)
    const token = auth.replace(/^Bearer\s+/i, "").trim();
    if (!token) return json({ error: { message: "Sign in to Hendrix first." } }, 401);
    const { data: u, error: uerr } = await sb.auth.getUser(token);
    if (uerr || !u || !u.user) return json({ error: { message: "Hendrix sign-in was not accepted by the AI function" + (uerr ? " (" + uerr.message + ")" : "") + ". Sign out of Hendrix, sign in again and retry." } }, 401);
    const body = await req.json();
    const mod = body.module === "sops" ? "sops" : body.module === "training" ? "training" : body.module === "rulebook" ? "rulebook" : body.module === "planner" ? "planner" : "testing";
    const need = mod === "training" ? 3 : 2;
    const { data: lvl, error: perr } = await sb.rpc("hx_perm", { p_mod: mod });
    if (perr) return json({ error: { message: "Access check failed: " + perr.message } }, 500);
    if (!lvl || lvl < need) {
      return json({ error: { message: mod === "sops" ? "You need Edit access to SOPs to use the AI SOP tools." : mod === "training" ? "You need Full access to Training to draft courses with AI." : mod === "rulebook" ? "You need Edit access to the Rulebook to organize a rules PDF with AI." : mod === "planner" ? "You need Edit access to the Production Planner to estimate recipes with AI." : "You need Edit access to Testing to read COAs." } }, 403);
    }

    const key = Deno.env.get("ANTHROPIC_API_KEY");
    if (!key) return json({ error: { message: "ANTHROPIC_API_KEY is not set in Supabase Edge Function secrets." } }, 500);

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
    if (r.status === 401 || r.status === 403) {
      return json({ error: { message: "Anthropic refused the ANTHROPIC_API_KEY saved in Supabase (Edge Functions > Secrets). Create a new key at console.anthropic.com > API Keys, paste it there (whole key, no spaces or quotes) and retry." } }, 502);
    }
    if (r.status === 400 && (await r.clone().text()).includes("credit balance")) {
      return json({ error: { message: "The Anthropic account has no credit. Add credit at console.anthropic.com > Billing and retry." } }, 502);
    }
    return new Response(await r.text(), { status: r.status, headers: { ...cors, "Content-Type": "application/json" } });
  } catch (e) {
    return json({ error: { message: String((e as Error)?.message || e) } }, 500);
  }
});
