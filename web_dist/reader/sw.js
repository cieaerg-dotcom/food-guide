const CACHE_NAME = 'novel-pwa-shell-v3';
const ASSETS = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS).catch(() => {}))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((k) => { if (k !== CACHE_NAME) return caches.delete(k); })
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.pathname.startsWith('/api/')) return;

  // 導航與靜態殼採用 Cache-First (確保電腦關機或無網路時 0.1 秒秒開)
  event.respondWith(
    caches.match(req).then((cached) => {
      const fetchPromise = fetch(req).then((netRes) => {
        if (netRes && netRes.status === 200) {
          const clone = netRes.clone();
          caches.open(CACHE_NAME).then((c) => c.put(req, clone));
        }
        return netRes;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});