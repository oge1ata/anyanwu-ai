const CACHE_NAME = "anyanwu-cache-v3";

const urlsToCache = [
  "/",
  "/index.html",
  "/style.css",
  "/script.js",
  "/manifest.json"
];


// INSTALL
self.addEventListener("install", (event) => {

  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Caching app files");
      return cache.addAll(urlsToCache);
    })
  );
});


// ACTIVATE
self.addEventListener("activate", (event) => {

  event.waitUntil(clients.claim());

});


// FETCH
self.addEventListener("fetch", (event) => {

  event.respondWith(
    fetch(event.request)
      .then((response) => {

        const responseClone = response.clone();

        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });

        return response;

      })
      .catch(() => caches.match(event.request))
  );

});