const base=process.env.BASE_URL||'http://localhost:8787';
for(const path of ['/v1/meta','/v1/metros','/v1/coverage?zip=10001','/v1/search?lat=0&lng=0&material=paint','/openapi.json','/llms.txt','/.well-known/x402']) {const r=await fetch(base+path);console.log(path,r.status);if(!r.ok)process.exitCode=1;}
