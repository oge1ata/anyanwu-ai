// ── Version this every time you deploy new CSS/JS ─────────────────────────────
// This is the key to preventing stale cache. When you change files, bump this:
// v1 → v2 → v3 etc. The activate step below will wipe any cache not matching
// this name, so users always get fresh files on next load.
const CACHE_NAME = "anyanwu-cache-v4";

const FILES_TO_CACHE = [
  "/",
  "/index.html",
  "/style.css",
  "/script.js",
  "/manifest.json"
];


// ── INSTALL ───────────────────────────────────────────────────────────────────
// Fires when a new service worker is detected. Cache all static files.
// skipWaiting() means it takes over immediately without waiting for old tabs to close.

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(FILES_TO_CACHE))
  );
});


// ── ACTIVATE ──────────────────────────────────────────────────────────────────
// Fires after install. THIS is where the old cache gets deleted.
// Any cache whose name doesn't match CACHE_NAME is wiped — this is what was
// missing before. Without this, old stale files sit in the browser forever.

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME) // find all caches that aren't current
          .map((name) => caches.delete(name))     // delete them
      )
    ).then(() => clients.claim()) // take control of all open tabs immediately
  );
});


// ── FETCH ─────────────────────────────────────────────────────────────────────
// Network-first strategy: always try to get a fresh file from the server.
// Only fall back to cache if the network fails (e.g. offline).
// This means updates are always picked up as long as the user has a connection —
// the cache is just a safety net, not the primary source.

self.addEventListener("fetch", (event) => {
  // Don't intercept POST requests (chat API calls) — only cache static assets
  if (event.request.method !== "GET") return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Got a fresh response — update the cache with it for offline use
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
        return response;
      })
      .catch(() => caches.match(event.request)) // offline fallback
  );
});
