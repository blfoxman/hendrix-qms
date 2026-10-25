// Hendrix QMS - Supabase Edge Function "hendrix-notify"
// Sends Hendrix email through Resend:
//   * mode "digest": the daily task list of every person (My Tasks), one email per person,
//     all licenses they can open; people who switched it off in My account get none.
//   * mode "alerts": urgent alerts (hold placed, test failed, critical deviation or complaint,
//     real recall or withdrawal started) to the people with Full access to that area.
//   * mode "test":  a signed-in person sends their own task list to themselves (My Tasks).
// "digest" and "alerts" are started by the database schedule (pg_cron, see hendrix_step39.sql)
// with the secret header x-hendrix-cron. Every email is written to hx_notify_log.
//
// Deploy (Supabase dashboard, project bqrncllndvzbhmxanitq):
//   1. Edge Functions > Deploy a new function > Via Editor. Name it exactly: hendrix-notify
//   2. Paste this whole file, Deploy. Settings: turn "Verify JWT" OFF (it checks its own secret
//      and the Hendrix sign-in itself).
//   3. Edge Functions > Secrets: RESEND_API_KEY, HX_MAIL_FROM (e.g. Hendrix QMS <qms@blackfox.com>),
//      HX_CRON_SECRET (a long random text, the same one used in the schedule),
//      optional HX_APP_URL (default https://blfoxman.github.io/hendrix-qms/).

import { createClient } from "jsr:@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-hendrix-cron",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

type Task = { kind: string; group: string; page: string; title: string; detail: string; due: string | null; overdue: boolean; ref: string };
type Lic = { license_id: string; license: string; license_number?: string; state?: string; tasks: Task[] };
type LogRow = { kind: string; email: string; subject: string; items: number; status: string; error?: string; ref?: string };

const esc = (s: unknown) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]!));
const fmtDue = (d: string | null) => {
  if (!d) return "";
  const t = new Date(d + "T12:00:00Z");
  return t.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
};
const GOLD = "#d4af37", INK = "#0b0b0b";

export function digestEmail(name: string, lics: Lic[], appUrl: string) {
  const all = lics.flatMap((l) => l.tasks);
  const overdue = all.filter((t) => t.overdue).length;
  const subject = "Hendrix: " + all.length + " task" + (all.length === 1 ? "" : "s") + " waiting" + (overdue ? " (" + overdue + " overdue)" : "");
  const row = (t: Task) =>
    '<tr><td style="padding:8px 10px;border-bottom:1px solid #eee;font:14px Arial,sans-serif;color:#111">' + esc(t.title) +
    (t.detail ? '<div style="color:#666;font-size:12px;margin-top:2px">' + esc(t.detail) + "</div>" : "") + "</td>" +
    '<td style="padding:8px 10px;border-bottom:1px solid #eee;font:13px Arial,sans-serif;white-space:nowrap;text-align:right;color:' + (t.overdue ? "#b3261e;font-weight:bold" : "#444") + '">' +
    (t.due ? (t.overdue ? "Overdue " : "Due ") + esc(fmtDue(t.due)) : "") + "</td></tr>";
  const section = (title: string, list: Task[]) => list.length
    ? '<tr><td colspan="2" style="padding:14px 10px 6px;font:bold 12px Arial,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#8a6d12">' + esc(title) + " (" + list.length + ")</td></tr>" + list.map(row).join("")
    : "";
  const body = lics.map((l) =>
    '<h3 style="font:bold 16px Arial,sans-serif;margin:22px 0 4px;color:#111">' + esc(l.license) + (l.license_number ? ' <span style="color:#888;font-weight:normal">· ' + esc(l.license_number) + "</span>" : "") +
    (l.state ? ' <span style="color:#888;font-weight:normal">· ' + esc(l.state) + "</span>" : "") + "</h3>" +
    '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse">' +
    section("Waiting for you", l.tasks.filter((t) => t.group === "mine")) + section("Waiting for your decision", l.tasks.filter((t) => t.group !== "mine")) + "</table>").join("");
  const html = '<div style="background:#f4f4f4;padding:24px 0"><div style="max-width:640px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">' +
    '<div style="background:' + INK + ';padding:18px 24px;font:bold 20px Georgia,serif;color:' + GOLD + ';letter-spacing:.04em">HENDRIX QMS</div>' +
    '<div style="padding:8px 24px 24px">' +
    '<p style="font:15px Arial,sans-serif;color:#111">Good morning ' + esc(name) + ", here is what is waiting for you" + (overdue ? ' — <b style="color:#b3261e">' + overdue + " overdue</b>" : "") + ".</p>" + body +
    '<p style="margin:26px 0 6px"><a href="' + esc(appUrl) + '" style="background:' + INK + ";color:" + GOLD + ';text-decoration:none;font:bold 14px Arial,sans-serif;padding:11px 20px;border-radius:6px;display:inline-block">Open Hendrix — My Tasks</a></p>' +
    '<p style="font:12px Arial,sans-serif;color:#888;margin-top:18px">You get this list on work days. To stop it: Hendrix &gt; My account &gt; Daily task email.</p></div></div></div>';
  const text = "Hendrix QMS - tasks waiting for " + name + "\n" + lics.map((l) => "\n" + l.license + "\n" + l.tasks.map((t) =>
    "- " + t.title + (t.due ? " (" + (t.overdue ? "OVERDUE " : "due ") + fmtDue(t.due) + ")" : "")).join("\n")).join("\n") + "\n\nOpen Hendrix: " + appUrl + "\n";
  return { subject, html, text, items: all.length };
}

export function alertEmail(a: { title: string; detail: string; license: string; license_number?: string; state?: string; created_at: string }, appUrl: string) {
  const subject = "Hendrix ALERT: " + a.title + " (" + a.license + ")";
  const when = new Date(a.created_at).toLocaleString("en-US", { timeZone: "America/New_York", dateStyle: "medium", timeStyle: "short" }) + " ET";
  const html = '<div style="background:#f4f4f4;padding:24px 0"><div style="max-width:640px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">' +
    '<div style="background:' + INK + ';padding:18px 24px;font:bold 20px Georgia,serif;color:' + GOLD + '">HENDRIX QMS · ALERT</div>' +
    '<div style="padding:20px 24px"><div style="border-left:4px solid #b3261e;padding:6px 14px;font:bold 17px Arial,sans-serif;color:#111">' + esc(a.title) + "</div>" +
    (a.detail ? '<p style="font:14px Arial,sans-serif;color:#333;white-space:pre-wrap">' + esc(a.detail) + "</p>" : "") +
    '<p style="font:13px Arial,sans-serif;color:#666">' + esc(a.license) + (a.license_number ? " · " + esc(a.license_number) : "") + (a.state ? " · " + esc(a.state) : "") + " · " + esc(when) + "</p>" +
    '<p><a href="' + esc(appUrl) + '" style="background:' + INK + ";color:" + GOLD + ';text-decoration:none;font:bold 14px Arial,sans-serif;padding:11px 20px;border-radius:6px;display:inline-block">Open Hendrix</a></p>' +
    '<p style="font:12px Arial,sans-serif;color:#888">You get this alert because you have Full access to this area.</p></div></div></div>';
  const text = "HENDRIX ALERT\n" + a.title + "\n" + (a.detail ? a.detail + "\n" : "") + a.license + " · " + when + "\nOpen Hendrix: " + appUrl + "\n";
  return { subject, html, text };
}

async function send(to: string, mail: { subject: string; html: string; text: string }): Promise<string | null> {
  const key = Deno.env.get("RESEND_API_KEY"), from = Deno.env.get("HX_MAIL_FROM");
  if (!key || !from) return "Email is not set up: add RESEND_API_KEY and HX_MAIL_FROM in Supabase > Edge Functions > Secrets.";
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST", headers: { Authorization: "Bearer " + key, "Content-Type": "application/json" },
    body: JSON.stringify({ from, to: [to], subject: mail.subject, html: mail.html, text: mail.text }),
  });
  if (r.ok) return null;
  const t = await r.text();
  let m = t; try { const j = JSON.parse(t); m = j.message || j.error || t; } catch (_) { /* text */ }
  return "Resend refused the email (" + r.status + "): " + String(m).slice(0, 300);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: { message: "POST only" } }, 405);
  try {
    const url = Deno.env.get("SUPABASE_URL")!, appUrl = Deno.env.get("HX_APP_URL") || "https://blfoxman.github.io/hendrix-qms/";
    const admin = createClient(url, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
    const body = await req.json().catch(() => ({}));
    const mode = String(body.mode || "");
    const log: LogRow[] = [];

    if (mode === "test") {
      const auth = req.headers.get("Authorization") || "", token = auth.replace(/^Bearer\s+/i, "").trim();
      if (!token) return json({ error: { message: "Sign in to Hendrix first." } }, 401);
      const user = createClient(url, Deno.env.get("SUPABASE_ANON_KEY")!, { global: { headers: { Authorization: auth } } });
      const { data: u, error: uerr } = await user.auth.getUser(token);
      if (uerr || !u?.user?.email) return json({ error: { message: "Hendrix sign-in was not accepted. Sign out, sign in again and retry." } }, 401);
      const { data: tasks, error: terr } = await user.rpc("hx_my_tasks", { p_lic: String(body.lic || "") });
      if (terr) return json({ error: { message: "Could not read your tasks: " + terr.message } }, 500);
      const { data: prof } = await user.from("hx_profiles").select("name").eq("id", u.user.id).maybeSingle();
      const mail = digestEmail(prof?.name || u.user.email, [{ license_id: String(body.lic || ""), license: String(body.license || "Your license"), tasks: (tasks || []) as Task[] }], appUrl);
      const err = await send(u.user.email, mail);
      log.push({ kind: "test", email: u.user.email, subject: mail.subject, items: mail.items, status: err ? "failed" : "sent", error: err || "" });
      await admin.rpc("hx_notify_sent", { p_ids: [], p_log: log });
      return err ? json({ error: { message: err } }, 502) : json({ ok: true, sent_to: u.user.email, items: mail.items });
    }

    // scheduled modes: the secret header from the database schedule
    const secret = Deno.env.get("HX_CRON_SECRET");
    if (!secret || req.headers.get("x-hendrix-cron") !== secret) return json({ error: { message: "Not allowed." } }, 401);

    if (mode === "digest") {
      const { data, error } = await admin.rpc("hx_task_digest");
      if (error) return json({ error: { message: error.message } }, 500);
      for (const p of (data || []) as { name: string; email: string; licenses: Lic[] }[]) {
        const mail = digestEmail(p.name, p.licenses, appUrl);
        const err = await send(p.email, mail);
        log.push({ kind: "digest", email: p.email, subject: mail.subject, items: mail.items, status: err ? "failed" : "sent", error: err || "" });
      }
      await admin.rpc("hx_notify_sent", { p_ids: [], p_log: log });
      return json({ ok: true, people: log.length, failed: log.filter((x) => x.status !== "sent").length });
    }

    if (mode === "alerts") {
      const { data, error } = await admin.rpc("hx_notify_pending");
      if (error) return json({ error: { message: error.message } }, 500);
      const ids: number[] = [];
      for (const a of (data || []) as { id: number; title: string; detail: string; license: string; license_number?: string; state?: string; created_at: string; recipients: { email: string }[] }[]) {
        const mail = alertEmail(a, appUrl);
        let ok = a.recipients.length === 0;   // nobody to tell: mark done
        for (const r of a.recipients) {
          const err = await send(r.email, mail);
          if (!err) ok = true;
          log.push({ kind: "alert", email: r.email, subject: mail.subject, items: 1, status: err ? "failed" : "sent", error: err || "", ref: String(a.id) });
        }
        if (ok) ids.push(a.id);   // failed alerts stay queued and are tried again next time
      }
      await admin.rpc("hx_notify_sent", { p_ids: ids, p_log: log });
      return json({ ok: true, alerts: ids.length, emails: log.filter((x) => x.status === "sent").length, failed: log.filter((x) => x.status !== "sent").length });
    }
    return json({ error: { message: "Unknown mode." } }, 400);
  } catch (e) {
    return json({ error: { message: String((e as Error).message || e) } }, 500);
  }
});
