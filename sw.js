const CACHE = 'kazakh-alphabet-v1';
const ASSETS = [
  './',
  './index.html',
  './cyrillic.html',
  './latin.html',
  './arabic-to-cyrillic.html',
  './learn-kazakh.html',
  './converter.html',
  './manifest.json',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(clients.claim());
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).catch(() => r))
  );
});
