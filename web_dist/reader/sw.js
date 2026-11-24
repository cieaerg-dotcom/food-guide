const CACHE_NAME = 'novel-pwa-shell-v5';
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

  // Network-First：有網路優先取得最新版，離線或無法連線時立即回傳本機快取
  event.respondWith(
    fetch(req).then((netRes) => {
      if (netRes && netRes.status === 200) {
        const clone = netRes.clone();
        caches.open(CACHE_NAME).then((c) => c.put(req, clone));
      }
      return netRes;
    }).catch(() => caches.match(req))
  );
});