/* Plan DCG : fonctionne aussi hors ligne */
const V = "plan-dcg-v2";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-180.png", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png", "./logo.svg"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const u = new URL(e.request.url);
  if (u.hostname === "api.github.com" || u.hostname === "raw.githubusercontent.com") return;
  if (u.origin === self.location.origin){
    // le réseau d'abord (pour les mises à jour), la copie en secours
    e.respondWith(fetch(e.request).then(r => {
      if (r.ok){ const cl = r.clone(); caches.open(V).then(c => c.put(e.request, cl)); }
      return r;
    }).catch(() => caches.match(e.request, {ignoreSearch:true}).then(r => r || caches.match("./index.html"))));
    return;
  }
  if (u.hostname === "fonts.googleapis.com" || u.hostname === "fonts.gstatic.com"){
    // polices Sora et Inter : gardées pour le hors-ligne
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => {
      if (res.ok || res.type === "opaque"){ const cl = res.clone(); caches.open(V).then(c => c.put(e.request, cl)); }
      return res;
    })));
  }
});
