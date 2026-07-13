// Anong / CerviCo-Pilot — minimal service worker.
// Strategy: network-first for /api (never cache predictions), cache-first for the
// app shell + static assets so the UI loads offline. AI features still need network.
const CACHE = "anong-en-v7";
const SHELL = ["./", "./manifest.webmanifest", "./icon-192.svg", "./icon-512.svg"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  // API: always network (no caching of medical predictions)
  if (url.pathname.startsWith("/api")) return;
  // static + shell: cache-first, fall back to network, then cache the result
  e.respondWith(
    caches.match(e.request).then((hit) =>
      hit ||
      fetch(e.request).then((res) => {
        if (res.ok && url.origin === location.origin) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, copy));
        }
        return res;
      }).catch(() => caches.match("/"))
    )
  );
});
