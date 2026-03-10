// Name of the cache storage.
// If we update files later, we can bump this version.
const CACHE_NAME = "anyanwu-cache-v1";

// Files we want to store locally in the browser
// so the app loads faster and works offline.
const urlsToCache = [
  "/",
  "/index.html",
  "/style.css",
  "/script.js",
  "/manifest.json"
];


// INSTALL EVENT
// This runs when the service worker is first installed.
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Caching app files");
      return cache.addAll(urlsToCache);
    })
  );
});


// FETCH EVENT
// Every network request goes through here.
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {

      // If the file exists in cache, return it
      if (response) {
        return response;
      }

      // Otherwise fetch it from the internet
      return fetch(event.request);
    })
  );
});