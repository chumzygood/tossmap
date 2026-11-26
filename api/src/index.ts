import { declareDiscoveryExtension } from '@x402/extensions/bazaar';
import { encodePaymentRequiredHeader } from '@x402/core/http';
import facilities from './data/facilities.json';
import metros from './data/metros.json';
import zips from './data/zips.json';
import version from './data/version.json';
import { locate, search, type Facility, type Metro } from './search';
import {openapi, searchParameters} from './openapi';
import {domains, facilitatorConfig} from './payment';
import {callerKey} from './caller';
import {registry, card, tools, protocolVersion} from './mcp';
export { State } from './state';
interface Env {STATE:DurableObjectNamespace; GENERAL_LIMIT:RateLimit; CHALLENGE_LIMIT:RateLimit; X402_NETWORK?:string; PAY_TO_ADDRESS?:string; FACILITATOR_URL?:string; INDEX402_VERIFY_HASH?:string}
const disclaimer='Confirm with the operator before driving; a listing does not guarantee acceptance.';
const assets:Record<string,string>={'eip155:84532':'0x036CbD53842c5426634e7929541eC2318f3dCF7e','eip155:8453':'0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'};
const fs=facilities as Facility[], ms=metros as Metro[], zs=zips as Record<string,number[]>;
const rates={search:{amount:'10000',price:'$0.01'},facility:{amount:'5000',price:'$0.005'},snapshot:{amount:'5000000',price:'$5.00'}};
const sha=async(s:string)=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))).map(x=>x.toString(16).padStart(2,'0')).join('');
const json=(body:unknown,status=200,headers:HeadersInit={})=>Response.json(body,{status,headers});
const call=async(env:Env,key:string,body:unknown)=>env.STATE.get(env.STATE.idFromName(key)).fetch('https://state/',{method:'POST',body:JSON.stringify(body)});
const docs=(network:string,asset:string|undefined,payTo:string,facilitator:string)=>`# TossMap API for agents

TossMap lists places to recycle or dispose of household materials in covered US metros. Confirm with the operator before driving; a listing does not guarantee acceptance.

## Endpoints
- GET /v1/meta: dataset metadata and prices, free.
- GET /v1/metros: covered metros, free.
- GET /v1/coverage?zip=10001: nearest metro, distance and covered (within 100 miles), free. Supply zip, lat and lng, or city and state (covered metro names).
- GET /v1/search?zip=10001&material=paint: location as above plus at least one material or filter. Materials: tires, paint, e_waste, batteries, motor_oil, household_chemicals (hyphens also accepted). Filters businesses_accepted, fee_charged, residents_only accept yes or no. radius_mi defaults to 25, maximum 100; limit defaults to 10, maximum 10. Results are sorted by distance.
- GET /v1/facilities/{id}: full facility record, $0.005 USDC.
- GET /v1/snapshot: full dataset, $5.00 USDC. x402 client libraries (@x402/core 2.23+) default to a $1 spend limit; raise your client spend limit to at least $5 to buy the snapshot.
- GET /openapi.json: API specification; GET /.well-known/x402: payment discovery.

Searches with zero results are free. Three searches with results per IPv4 address or IPv6 /64 prefix per UTC day are free; later searches with results cost $0.01 USDC. X-Free-Searches-Remaining reports the balance on free search responses and challenges. Count is before limit.

## MCP server
Streamable HTTP endpoint: https://api.tossmap.com/mcp. Tools: search_facilities, get_facility, coverage. Coverage and empty searches are free; three result-bearing searches or facility lookups per caller per day are free. Further calls use the paid REST API.

    {"mcpServers":{"tossmap":{"url":"https://api.tossmap.com/mcp"}}}

## Payment (x402 v2 exact)
Current network: ${network}; USDC asset: ${asset||'unsupported'}; payTo: ${payTo||'not configured'}; facilitator: ${facilitator}. These values reflect the current Worker configuration. Amounts are USDC base units (6 decimals).
1. GET a paid resource. A 402 has JSON describing the price and a base64 PAYMENT-REQUIRED header; search challenges include match count without results.
2. Inspect network, asset, amount and payTo. Use an x402 v2 client to sign the accepted requirements.
3. Retry the same URL with PAYMENT-SIGNATURE. On success PAYMENT-RESPONSE contains the base64 settlement receipt. Retrying the same signature and URL within 15 minutes returns the cached receipt.

Example with @x402/fetch, @x402/evm and viem (supply your own account securely):

    import { wrapFetchWithPaymentFromConfig } from '@x402/fetch';
    import { ExactEvmScheme } from '@x402/evm/exact/client';
    const paidFetch = wrapFetchWithPaymentFromConfig(fetch, { schemes: [{ network: 'eip155:*', client: new ExactEvmScheme(account) }] });
    const response = await paidFetch('https://api.tossmap.com/v1/facilities/dsny-special-waste-drop-off-bronx');
    console.log(await response.json());

## Examples (trimmed)
    GET /v1/coverage?zip=10001
    {"nearest_metro":{"city":"New York","state":"NY","distance_mi":1.2},"covered":true,"disclaimer":"..."}
    GET /v1/search?zip=10001&material=paint
    {"count":1,"results":[{"id":"...","name":"...","location":{"distance_mi":2.1}}],"disclaimer":"..."}
    GET /v1/facilities/dsny-special-waste-drop-off-bronx
    {"facility":{"id":"dsny-special-waste-drop-off-bronx","name":"...","questions":{}},"disclaimer":"..."}

## Errors
400: correct the location, filters or signature. 402: inspect PAYMENT-REQUIRED and pay, or inspect reason if verification failed. 404: check endpoint or facility ID. 409: signature already used or settlement uncertain; contact the operator. 429: wait for Retry-After seconds. 502: facilitator rejected settlement; inspect reason and contact the operator. 503: configuration or facilitator unavailable, or settlement outcome unknown; contact the operator if settlement is uncertain.

Geocoding: US Census Bureau and © OpenStreetMap contributors (Nominatim). Coordinates are approximate; some facilities have no coordinates and do not appear in radius searches.
`;
async function handle(req:Request,env:Env,ip:string,info:{kind:string;price:string;tx?:string}):Promise<Response>{
 const url=new URL(req.url),path=url.pathname,network=env.X402_NETWORK||'eip155:84532',payTo=env.PAY_TO_ADDRESS||'',asset=assets[network],facilitator=facilitatorConfig(env.FACILITATOR_URL,network);
 if(req.method==='OPTIONS')return new Response(null,{status:204});
 if(path==='/mcp') {if(req.method!=='POST')return new Response(null,{status:405,headers:{Allow:'POST'}}); return mcp(req,env,ip,info);}
 if(req.method!=='GET')return json({error:'Method not allowed'},405);
 if(path==='/server.json')return json(registry);
 if(path==='/.well-known/mcp/server-card.json'||path==='/.well-known/mcp.json')return json(card);
 if(path==='/.well-known/402index-verify.txt')return env.INDEX402_VERIFY_HASH ? new Response(env.INDEX402_VERIFY_HASH,{headers:{'content-type':'text/plain; charset=utf-8'}}):new Response(null,{status:404});
 if(path==='/'||path==='/llms.txt')return new Response(docs(network,asset,payTo,facilitator.url),{headers:{'content-type':'text/markdown; charset=utf-8'}});
 if(path==='/openapi.json')return json(openapi);
 if(path==='/.well-known/x402')return json({version:1,x402Version:2,network,asset,payTo:payTo||null,facilitator:facilitator.url,mcp:'https://api.tossmap.com/mcp',resources:['https://api.tossmap.com/v1/search/paid?zip=10001&material=paint','https://api.tossmap.com/v1/facilities/dsny-special-waste-drop-off-bronx','https://api.tossmap.com/v1/snapshot'],paidResources:[{path:'/v1/search',price:'$0.01',condition:'results after three free searches per IPv4 address or IPv6 /64 prefix per UTC day'},{path:'/v1/facilities/{id}',price:'$0.005'},{path:'/v1/snapshot',price:'$5.00'}],disclaimer});
 const dataset={...version,facilities_total:fs.length,geocoding_attribution:'US Census Bureau and © OpenStreetMap contributors (Nominatim).'};
 if(path==='/v1/meta')return json({dataset,metros:ms.length,prices:rates,network,asset,disclaimer});
 if(path==='/v1/metros')return json({dataset,metros:ms.map(m=>({...m,facilities:fs.filter(f=>f.metro===m.id).length})),disclaimer});
 if(path==='/v1/coverage'){try{const l=locate(url.searchParams,ms,zs,fs);return json({nearest_metro:l.nearest,covered:!!l.nearest&&l.nearest.distance_mi<=100,disclaimer});}catch(e){return json({error:(e as Error).message,disclaimer},400);}}
 let result:unknown, rate:typeof rates.search, count:number|undefined;
 if(path==='/v1/search'||path==='/v1/search/paid'){
  try{const s=search(url.searchParams,fs,ms,zs);count=s.count;result={query:Object.fromEntries(url.searchParams),dataset,...s,disclaimer};}catch(e){return json({error:(e as Error).message,disclaimer},400);}
  if(!count){info.kind='free';const left:any=await (await call(env,'ip:'+await sha(ip),{action:'remaining'})).json();return json(result,200,{'X-Free-Searches-Remaining':String(left.remaining)});}
  if(path==='/v1/search'&&!req.headers.has('PAYMENT-SIGNATURE')) {const res=await call(env,'ip:'+await sha(ip),{action:'allowance'}); const a:any=await res.json();if(a.allowed){info.kind='free';return json(result,200,{'X-Free-Searches-Remaining':String(a.remaining)});}}
  rate=rates.search;
 } else if(path.startsWith('/v1/facilities/')) {const f=fs.find(x=>x.id===decodeURIComponent(path.slice('/v1/facilities/'.length)));if(!f)return json({error:'Facility not found',disclaimer},404);result={dataset,facility:f,disclaimer};rate=rates.facility;}
 else if(path==='/v1/snapshot'){result={dataset,facilities:fs,disclaimer};rate=rates.snapshot;}
 else return json({error:'Not found'},404);
 info.price=rate.price;
 if(facilitator.error)return json({error:facilitator.error},503);
 if(!asset||!/^0x[0-9a-fA-F]{40}$/.test(payTo)||/^0x0{40}$/i.test(payTo))return json({error:'Payments unavailable: invalid or missing PAY_TO_ADDRESS or X402_NETWORK'},503);
 const requirements={scheme:'exact',network:network as `eip155:${string}`,asset,amount:rate.amount,payTo,maxTimeoutSeconds:300,extra:domains[network]};
 const resource={url:url.toString(),description:`TossMap ${path} (${rate.price} USDC)`,mimeType:'application/json'};
 const signature=req.headers.get('PAYMENT-SIGNATURE');
 if(!signature){if(!(await env.CHALLENGE_LIMIT.limit({key:ip})).success)return json({error:'Too many payment challenges'},429,{'Retry-After':'60'});info.kind='402';const extensions=declareDiscoveryExtension({input:path.startsWith('/v1/search')?{zip:'10001',material:'paint'}:{},inputSchema:path.startsWith('/v1/search')?{type:'object',description:'Use a location and a material or filter',properties:Object.fromEntries(searchParameters.map(p=>[p.name,p.schema]))}:{type:'object',properties:{}},...(path.startsWith('/v1/facilities/')?{pathParams:{id:decodeURIComponent(path.slice('/v1/facilities/'.length))},pathParamsSchema:{type:'object',properties:{id:{type:'string',description:'Facility ID in the URL path'}},required:['id']}}:{}),output:{example:{disclaimer},schema:{type:'object',description:resource.description,properties:{disclaimer:{type:'string'}}}}}); (extensions.bazaar.info.input as unknown as {method:string}).method='GET'; const required={x402Version:2,resource,accepts:[requirements],extensions};return json({...required,error:'Payment required',description:resource.description,price:rate.price,currency:'USDC',matches:count,how_to_pay:path==='/v1/snapshot'?'Use an x402 v2 client; retry with PAYMENT-SIGNATURE. @x402/core 2.23+ clients default to a $1 spend limit; raise your client spend limit to at least $5 for this snapshot.':'Use an x402 v2 client; retry with PAYMENT-SIGNATURE.',disclaimer},402,{'PAYMENT-REQUIRED':encodePaymentRequiredHeader(required),'Cache-Control':'no-store','X-Free-Searches-Remaining':'0'});}
 const ready=JSON.stringify(result); // finish preparing content before charging
 const state=await call(env,'signature:'+await sha(signature),{action:'payment',signature,requirements,resource:url.toString(),facilitatorUrl:facilitator.url});const outcome:any=await state.json();if(!state.ok)return json(outcome,state.status);
 info.kind='paid';info.tx=outcome.transaction;return new Response(ready,{headers:{'content-type':'application/json','PAYMENT-RESPONSE':outcome.receipt,'Cache-Control':'private, no-store'}});
}
async function mcp(req:Request,env:Env,ip:string,info:{kind:string;price:string;tx?:string}):Promise<Response>{
 let body:any; try{body=await req.json();}catch{return json({jsonrpc:'2.0',id:null,error:{code:-32700,message:'Parse error'}});}
 const one=async (msg:any):Promise<any>=>{
  if(!msg||typeof msg!=='object'||Array.isArray(msg)||msg.jsonrpc!=='2.0'||typeof msg.method!=='string'||('id' in msg && msg.id!==null && typeof msg.id!=='string' && typeof msg.id!=='number'))return {jsonrpc:'2.0',id:null,error:{code:-32600,message:'Invalid Request'}};
  if(!Object.prototype.hasOwnProperty.call(msg,'id'))return null;
  const reply=(result:unknown)=>({jsonrpc:'2.0',id:msg.id,result}); const error=(code:number,message:string)=>({jsonrpc:'2.0',id:msg.id,error:{code,message}});
  if(msg.method==='initialize')return reply({protocolVersion:['2025-11-25','2025-06-18','2025-03-26'].includes(msg.params?.protocolVersion)?msg.params.protocolVersion:protocolVersion,capabilities:{tools:{listChanged:false}},serverInfo:card.serverInfo,instructions:'TossMap finds US disposal sites. Three result-bearing searches or facility lookups per day are free; see https://api.tossmap.com/llms.txt for paid API access.'});
  if(msg.method==='ping')return reply({}); if(msg.method==='tools/list')return reply({tools}); if(msg.method!=='tools/call')return error(-32601,'Method not found');
  const name=msg.params?.name, args=msg.params?.arguments??{}; const def=tools.find(t=>t.name===name);
  if(!def)return error(-32602,'Unknown tool');
  if(!args||typeof args!=='object'||Array.isArray(args)||Object.keys(args).some(k=>!(k in def.inputSchema.properties)))return error(-32602,'Invalid tool arguments');
  if(name==='get_facility'?(typeof args.id!=='string'||!args.id):(!args.zip&&!args.city)|| (args.zip!==undefined&&(typeof args.zip!=='string'||!/^\d{5}$/.test(args.zip))) || (args.city!==undefined&&(typeof args.city!=='string'||!args.city.trim())) || (args.state!==undefined&&(typeof args.state!=='string'||!/^[a-z]{2}$/i.test(args.state))) || (name==='search_facilities'&&(!['tires','paint','e_waste','batteries','motor_oil','household_chemicals'].includes(args.material)||(args.limit!==undefined&&(!Number.isInteger(args.limit)||args.limit<1||args.limit>10)))))return error(-32602,'Invalid tool arguments');
  const params=new URLSearchParams(); for(const [k,v] of Object.entries(args))if(k!=='id')params.set(k,String(v));
  const paidUrl=name==='get_facility'?'https://api.tossmap.com/v1/facilities/'+encodeURIComponent(args.id):'https://api.tossmap.com/v1/search?'+params;
  const endpoint=name==='coverage'?'https://api.tossmap.com/v1/coverage?'+params:paidUrl;
  if(name==='get_facility') {const f=fs.find(f=>f.id===args.id); if(f){const a:any=await (await call(env,'ip:'+await sha(ip),{action:'allowance'})).json(); if(a.allowed){info.kind='free';const data={dataset:{...version,facilities_total:fs.length,geocoding_attribution:'US Census Bureau and © OpenStreetMap contributors (Nominatim).'},facility:f,disclaimer};return reply({content:[{type:'text',text:JSON.stringify(data)}],structuredContent:data});}}}
  const res=await handle(new Request(endpoint),env,ip,info), data:any=await res.json();
  if(res.status===402){const {x402Version,resource,accepts,extensions}=data; const paymentRequired={x402Version,resource,accepts,extensions}; return reply({isError:true,content:[{type:'text',text:`Payment required: ${data.price} USDC. Pay with x402 at ${paidUrl}`}],structuredContent:{paymentRequired,paidUrl,docs:'https://api.tossmap.com/llms.txt'}});}
  return reply({...(res.ok?{}:{isError:true}),content:[{type:'text',text:JSON.stringify(data)}],structuredContent:data});
 };
 if(Array.isArray(body)){if(!body.length)return json({jsonrpc:'2.0',id:null,error:{code:-32600,message:'Invalid Request'}});const replies=[]; for(const item of body){const result=await one(item);if(result)replies.push(result);}return replies.length?json(replies):new Response(null,{status:202});}
 const response=await one(body);return response?json(response):new Response(null,{status:202});
}
export default {async fetch(req:Request,env:Env):Promise<Response>{const ip=callerKey(req.headers.get('CF-Connecting-IP')||'unknown'),url=new URL(req.url),info:{kind:string;price:string;tx?:string}={kind:'free',price:'0'};let res:Response;
 try{if(!(await env.GENERAL_LIMIT.limit({key:ip})).success)res=json({error:'Rate limit exceeded'},429,{'Retry-After':'60'});else res=await handle(req,env,ip,info);}catch{res=json({error:'Service unavailable'},503);}
 const headers=new Headers(res.headers);headers.set('Access-Control-Allow-Origin','*');headers.set('Access-Control-Allow-Methods','GET, POST, DELETE, OPTIONS');headers.set('Access-Control-Allow-Headers','PAYMENT-SIGNATURE, Content-Type, Authorization, Mcp-Session-Id, MCP-Protocol-Version');headers.set('Access-Control-Expose-Headers','PAYMENT-REQUIRED, PAYMENT-RESPONSE, X-Free-Searches-Remaining, Retry-After, Mcp-Session-Id');
 console.log(JSON.stringify({route:url.pathname,status:res.status,kind:info.kind,price:info.price,network:env.X402_NETWORK||'eip155:84532',transaction:info.tx,ip_hash:await sha(ip)}));return new Response(res.body,{status:res.status,headers});}};
