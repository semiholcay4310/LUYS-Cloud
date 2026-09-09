const CACHE='luys-pwa-assets-v4';

const ASSETS=[
  '/manifest.webmanifest',
  '/icon-192.png',
  '/icon-512.png',
  '/apple-touch-icon.png'
];

const SPLASH_HTML=`<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#071724">
<title>LÜYS</title>
<style>
*{box-sizing:border-box}
html,body{
  margin:0;width:100%;height:100%;
  background:#061522;color:#eef8ff;
  font-family:Arial,sans-serif
}
body{
  display:grid;
  place-items:center;
  overflow:hidden
}
body:before{
  content:"";
  position:fixed;
  inset:0;
  background:
    radial-gradient(circle at 50% 28%,rgba(22,145,224,.18),transparent 32%),
    linear-gradient(180deg,#030c13 0%,#071a29 55%,#04101a 100%)
}
.wrap{
  position:relative;
  z-index:1;
  text-align:center;
  padding:28px;
  width:min(92vw,430px)
}
.logo{
  width:148px;
  height:148px;
  object-fit:contain;
  border-radius:32px;
  filter:drop-shadow(0 16px 34px rgba(0,130,220,.28));
  margin-bottom:18px
}
h1{
  font-size:42px;
  letter-spacing:5px;
  margin:0;
  font-weight:900
}
.sub{
  margin-top:8px;
  color:#9dc3dc;
  font-size:13px;
  letter-spacing:1.4px;
  font-weight:700
}
.line{
  width:150px;
  height:3px;
  margin:25px auto 14px;
  background:#12354d;
  border-radius:99px;
  overflow:hidden
}
.line i{
  display:block;
  width:42%;
  height:100%;
  background:linear-gradient(90deg,#168ed8,#73d1ff);
  border-radius:99px;
  animation:load 1.15s ease-in-out infinite
}
.status{
  font-size:12px;
  color:#7899ae;
  letter-spacing:.4px
}
@keyframes load{
  0%{transform:translateX(-110%)}
  100%{transform:translateX(350%)}
}
</style>
</head>
<body>
<div class="wrap">
  <img class="logo" src="/icon-512.png" alt="LÜYS">
  <h1>LÜYS</h1>
  <div class="sub">LUUKMAS ÜRETİM YÖNETİM SİSTEMİ</div>
  <div class="line"><i></i></div>
  <div class="status">Sistem hazırlanıyor…</div>
</div>

<script>
(async function wake(){
  while(true){
    try{
      const r=await fetch(
        '/health?wake='+Date.now(),
        {cache:'no-store',credentials:'same-origin'}
      );

      if(r.ok){
        location.replace('/?luys_ready='+Date.now());
        return;
      }
    }catch(e){}

    await new Promise(r=>setTimeout(r,1800));
  }
})();
<\/script>
</body>
</html>`;

self.addEventListener('install',event=>{
  event.waitUntil(
    caches.open(CACHE).then(c=>c.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys().then(keys=>
      Promise.all(
        keys
          .filter(k=>k!==CACHE)
          .map(k=>caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET') return;

  const u=new URL(event.request.url);

  if(event.request.mode==='navigate'){
    if(u.searchParams.has('luys_ready')){
      event.respondWith(fetch(event.request));
    }else{
      event.respondWith(
        new Response(SPLASH_HTML,{
          headers:{
            'Content-Type':'text/html; charset=utf-8',
            'Cache-Control':'no-store'
          }
        })
      );
    }
    return;
  }

  if(ASSETS.includes(u.pathname)){
    event.respondWith(
      caches.match(event.request)
        .then(r=>r||fetch(event.request))
    );
  }
});
