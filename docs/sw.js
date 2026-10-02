// Offline cache: the whole text is small, so cache everything on install; network-first for data so new meanings arrive.
const V = 'ss-9ffab8eb44';
const CORE = ['./', 'index.html', 'manifest.json', 'data/text.json', 'data/notes/index.json', 'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png', 'data/notes/argala.json', 'data/notes/ch10.json', 'data/notes/ch12.json', 'data/notes/ch13.json', 'data/notes/ch3.json', 'data/notes/ch4.json', 'data/notes/ch6.json', 'data/notes/ch7.json', 'data/notes/ch8.json', 'data/notes/ch9.json', 'data/notes/kilakam.json', 'data/notes/ch1.json', 'data/notes/ch11.json', 'data/notes/ch2.json', 'data/notes/ch5.json', 'data/notes/kavacham.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  const fonts = /fonts\.(googleapis|gstatic)\.com$/.test(u.hostname);
  if (u.origin !== location.origin && !fonts) return;
  e.respondWith(caches.open(V).then(async c => {
    const hit = await c.match(e.request);
    const net = fetch(e.request).then(r => { if (r.ok || r.type === 'opaque') c.put(e.request, r.clone()); return r; }).catch(() => hit);
    return u.pathname.includes('/data/') ? net.then(r => r || hit) : (hit || net);
  }));
});
