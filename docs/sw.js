/* Athleticism service worker.

   Strategy: stale-while-revalidate. The app is served from cache immediately -
   it opens instantly even with no signal - while a fresh copy is fetched in the
   background for next time. The practical consequence: after you deploy a new
   version, the first open still shows the old one and the second shows the new.
   That trade is deliberate. Network-first would make every gym session wait on
   a connection that may not be there.

   Bump CACHE_VERSION whenever you deploy. It's what evicts the old files. */

var CACHE_VERSION = 'v2';
var SHELL = 'athleticism-shell-' + CACHE_VERSION;

/* Fonts are precached, not left to the first online load: a page only asks for
   the subsets its text needs, so an exercise name in a new script would
   otherwise hit a font that was never fetched. */
var SHELL_FILES = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './fonts/baloo2-latin.woff2',
  './fonts/baloo2-latin-ext.woff2',
  './fonts/baloo2-vietnamese.woff2',
  './fonts/baloo2-devanagari.woff2',
  './fonts/nunito-latin.woff2',
  './fonts/nunito-latin-ext.woff2',
  './fonts/nunito-vietnamese.woff2',
  './fonts/nunito-cyrillic.woff2',
  './fonts/nunito-cyrillic-ext.woff2'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(SHELL).then(function (c) {
      return c.addAll(SHELL_FILES);
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k !== SHELL) return caches.delete(k);
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
});

function staleWhileRevalidate(req, cacheName) {
  return caches.open(cacheName).then(function (cache) {
    return cache.match(req).then(function (hit) {
      var net = fetch(req).then(function (res) {
        if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
        return res;
      }).catch(function () {
        return hit;                      /* offline: whatever we already have */
      });
      return hit || net;
    });
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url = new URL(req.url);
  if (url.origin !== location.origin) return;

  /* Navigations always resolve to the app shell, so a deep link or a refresh
     works with no connection. */
  if (req.mode === 'navigate') {
    e.respondWith(
      staleWhileRevalidate(req, SHELL).catch(function () {
        return caches.match('./index.html', { cacheName: SHELL });
      })
    );
    return;
  }

  e.respondWith(staleWhileRevalidate(req, SHELL));
});
