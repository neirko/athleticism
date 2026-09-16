"""Manifest + service worker wiring.

Android needs a web app manifest to open standalone - iOS gets there with
apple-mobile-web-app-capable, which is why the iPhone worked and Android
didn't. The service worker is what makes it open with no signal.

The registration script carries data-pwa so portable exports strip it (a
file:// copy can't register a worker), and a type attribute so the export's
"last untyped script is the app" detection keeps finding the real app script.
It also skips registration inside Capacitor, where assets ship in the APK and
a worker would be pointless.
"""

REGISTER = """<script type="text/javascript" data-pwa>
/* Offline support. Skipped inside the Android shell, which bundles its own copy. */
if ('serviceWorker' in navigator && !window.Capacitor && location.protocol !== 'file:') {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js').catch(function (e) {
      console.warn('Athleticism: service worker did not register', e);
    });
  });
}
</script>
</body>"""


def apply(src):
    def rep(old, new):
        nonlocal src
        assert src.count(old) == 1, "expected 1 of %r, found %d" % (old[:60], src.count(old))
        src = src.replace(old, new)

    rep('<meta name="theme-color" content="#FFF6EC">',
        '<meta name="theme-color" content="#FFFFFF">\n'
        '<link rel="manifest" href="manifest.json">')
    rep("</body>", REGISTER)
    return src


MANIFEST = """{
  "name": "Athleticism",
  "short_name": "Athleticism",
  "description": "A workout tracker that lives on your device. No account, no sync, no subscription.",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#FFF6EC",
  "theme_color": "#FFFFFF",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
"""

SW = """/* Athleticism service worker.

   Strategy: stale-while-revalidate. The app is served from cache immediately -
   it opens instantly even with no signal - while a fresh copy is fetched in the
   background for next time. The practical consequence: after you deploy a new
   version, the first open still shows the old one and the second shows the new.
   That trade is deliberate. Network-first would make every gym session wait on
   a connection that may not be there.

   Bump CACHE_VERSION whenever you deploy. It's what evicts the old files. */

var CACHE_VERSION = 'v1';
var SHELL = 'athleticism-shell-' + CACHE_VERSION;
var FONTS = 'athleticism-fonts-' + CACHE_VERSION;

var SHELL_FILES = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png'
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
        if (k !== SHELL && k !== FONTS) return caches.delete(k);
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

  /* Google Fonts. Cached on first online load so the rounded type survives
     offline; without this the app silently falls back to the system font. */
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(staleWhileRevalidate(req, FONTS));
    return;
  }

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
"""
