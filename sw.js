// Hendrix QMS - service worker for the kiosks (time clock, facility logs, visitors).
// Registered only by a kiosk page. It keeps a copy of the app page and its libraries so a
// kiosk tablet can open Hendrix again without internet. The app page is always fetched fresh
// when the internet is there (network first); libraries from the CDN are kept (cache first).
// Hendrix data (Supabase) is never cached here: offline entries wait in the kiosk's own outbox.
const CACHE = 'hendrix-kiosk-v1';
const CDN = /(^|\.)cdnjs\.cloudflare\.com$|(^|\.)cdn\.jsdelivr\.net$|(^|\.)unpkg\.com$|(^|\.)fonts\.googleapis\.com$|(^|\.)fonts\.gstatic\.com$/;

self.addEventListener('install', (e) => { self.skipWaiting(); });
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k.startsWith('hendrix-kiosk-') && k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const u = new URL(req.url);
  if (u.origin === self.location.origin) {
    // the app page (index.html with any ?kiosk=... link): network first, the kept copy when offline
    if (req.mode === 'navigate' || u.pathname.endsWith('/') || u.pathname.endsWith('.html')) {
      e.respondWith(fetch(req).then((r) => {
        if (r.ok) { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(new Request(u.origin + u.pathname), cp)); }
        return r;
      }).catch(() => caches.match(new Request(u.origin + u.pathname)).then((m) => m || caches.match(u.origin + u.pathname.replace(/[^/]*$/, '')))));
    }
    return;
  }
  if (CDN.test(u.hostname)) {
    e.respondWith(caches.match(req).then((m) => m || fetch(req).then((r) => {
      if (r.ok || r.type === 'opaque') { const cp = r.clone(); caches.open(CACHE).then((c) => c.put(req, cp)); }
      return r;
    })));
  }
});
