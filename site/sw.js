// hendrixqms.com is now the Hendrix intro page; each company's Hendrix (and its kiosk worker) lives at
// hendrixqms.com/<company>/. This retires the kiosk worker that was registered at the root before the move.
// Its cached copy is left alone: the company kiosk workers keep their own.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => { e.waitUntil(self.registration.unregister()); });
