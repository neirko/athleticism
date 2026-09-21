/* Athleticism service worker.

   Strategy: stale-while-revalidate. The app is served from cache immediately -
   it opens instantly even with no signal - while a fresh copy is fetched in the
   background for next time. The practical consequence: after you deploy a new
   version, the first open still shows the old one and the second shows the new.
   That trade is deliberate. Network-first would make every gym session wait on
   a connection that may not be there.

   Bump CACHE_VERSION whenever you deploy. It's what evicts the old files. */

var CACHE_VERSION = 'v20';
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

/* Cached one at a time. addAll() is all-or-nothing, so a single missing icon
   would leave the app with no offline copy at all. */
self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(SHELL).then(function (cache) {
      return Promise.all(SHELL_FILES.map(function (f) {
        return cache.add(f).catch(function () {
          console.warn('Athleticism SW: could not precache', f);
        });
      }));
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

function offlinePage() {
  return new Response(
    '<!DOCTYPE html><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<body style="font-family:system-ui;padding:40px;text-align:center;background:#FFF6EC;color:#2A2233">' +
    '<h1>Offline</h1><p>Open Athleticism once with a connection and it will work offline from then on.</p>',
    { headers: { 'Content-Type': 'text/html' } }
  );
}

/* Every path through this returns a real Response. Resolving with undefined is
   what produced "Safari can't open the page" - respondWith(undefined) is a
   network error, and iOS renders it as though the site were unreachable. */
function serve(e, cacheName, isNavigation) {
  var req = e.request;
  return caches.open(cacheName).then(function (cache) {
    return cache.match(req, { ignoreSearch: true }).then(function (hit) {
      var net = fetch(req).then(function (res) {
        if (res && (res.ok || res.type === 'opaque')) cache.put(req, res.clone());
        return res;
      }).catch(function () {
        return null;
      });

      if (hit) {
        e.waitUntil(net);               /* refresh in the background */
        return hit;
      }
      return net.then(function (res) {
        if (res) return res;
        if (!isNavigation) return Response.error();
        /* A navigation we've never cached under this exact URL - a query
           string, a trailing slash, whatever iOS decided to add. Any copy of
           the app shell answers it correctly. */
        return cache.match('./index.html').then(function (shell) {
          if (shell) return shell;
          return cache.match('./').then(function (root) {
            return root || offlinePage();
          });
        });
      });
    });
  }).catch(function () {
    return isNavigation ? offlinePage() : Response.error();
  });
}

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url;
  try { url = new URL(req.url); } catch (err) { return; }

  if (url.origin !== location.origin) return;

  if (req.mode === 'navigate') {
    e.respondWith(serve(e, SHELL, true));
    return;
  }

  e.respondWith(serve(e, SHELL, false));
});
