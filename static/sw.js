const CACHE='luys-pwa-assets-v2';

const ASSETS=[
  '/static/manifest.webmanifest',
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/apple-touch-icon.png'
];

self.addEventListener('install', event=>{
  event.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', event=>{
  event.waitUntil(
    caches.keys().then(keys=>
      Promise.all(
        keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event=>{
  const u=new URL(event.request.url);

  if(event.request.method!=='GET') return;

  const staticOnly=
    u.pathname==='/static/manifest.webmanifest' ||
    u.pathname==='/static/icon-192.png' ||
    u.pathname==='/static/icon-512.png' ||
    u.pathname==='/static/apple-touch-icon.png';

  if(staticOnly){
    event.respondWith(
      caches.match(event.request)
        .then(r=>r||fetch(event.request))
    );
  }
});
