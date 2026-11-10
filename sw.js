// Keep the app shell offline while ensuring installation metadata is never pinned to an old cached copy.
const CACHE='sg-events-shell-v7';
const SHELL=['./','./index.html','./manifest.webmanifest','./icons/app-icon.svg','./icons/sg-national-events-icon-192.png','./icons/sg-national-events-icon-512.png'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('sg-events-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',event=>{
 const req=event.request;
 if(req.method!=='GET')return;
 const url=new URL(req.url);
 if(url.origin!==self.location.origin||!url.pathname.startsWith('/sg-national-events-monitor/'))return;
 if(url.pathname.includes('/data/')){event.respondWith(fetch(req,{cache:'no-store'}).catch(()=>caches.match(req)));return;}
 // Browser must see fresh manifest and service-worker metadata after a deployment.
 if(url.pathname.endsWith('/manifest.webmanifest')){
  event.respondWith(fetch(req,{cache:'no-store'}).then(response=>{if(response.ok){const copy=response.clone();event.waitUntil(caches.open(CACHE).then(cache=>cache.put(req,copy)));}return response;}).catch(()=>caches.match(req)));
  return;
 }
 if(req.mode==='navigate'){event.respondWith(fetch(req).catch(()=>caches.match('./index.html')));return;}
 event.respondWith(caches.match(req).then(cached=>cached||fetch(req)));
});
