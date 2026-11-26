import {expect,it} from 'vitest';
import worker from '../src/index';
import {decodePaymentRequiredHeader} from '@x402/core/http';
const limit={limit:async()=>({success:true})};
const env={GENERAL_LIMIT:limit,CHALLENGE_LIMIT:limit,STATE:{idFromName:(key:string)=>key,get:()=>({fetch:async()=>Response.json({allowed:false,remaining:0})})},PAY_TO_ADDRESS:'0x000000000000000000000000000000000000dEaD'};
const get=(path:string)=>worker.fetch(new Request('https://api.tossmap.com'+path),env as any);
it('classifies operations and describes paid inputs and prices',async()=>{
 const spec:any=await (await get('/openapi.json')).json();
 expect(spec.info['x-guidance']).toContain('coverage');expect(spec.info.contact).toEqual({url:'https://tossmap.com'});
 const paid:Record<string,string>={'/v1/search':'0.01','/v1/facilities/{id}':'0.005','/v1/snapshot':'5.00'};const ids=new Set<string>();
 for(const [path,entry] of Object.entries(spec.paths) as [string,any][]) {
  const op=entry.get;expect(op.operationId).toBeTruthy();expect(ids.has(op.operationId)).toBe(false);ids.add(op.operationId);
  if(path in paid){expect(op.responses['402']).toBeDefined();expect(op['x-payment-info']).toEqual({protocols:[{x402:{}}],price:{mode:'fixed',currency:'USD',amount:paid[path]}});}
  else {expect(op.security).toEqual([]);for(const code of ['402','409','502','503'])expect(op.responses[code]).toBeUndefined();expect(op.responses['200'].headers?.['PAYMENT-RESPONSE']).toBeUndefined();}
 }
 expect(ids.size).toBe(10);
 expect(spec.paths['/v1/search'].get.parameters.map((p:any)=>p.name)).toEqual(expect.arrayContaining(['zip','lat','lng','city','state','radius_mi','material','businesses_accepted','fee_charged','residents_only','limit']));
 expect(spec.paths['/v1/facilities/{id}'].get.parameters[0]).toMatchObject({name:'id',in:'path',required:true});
});
it('publishes compatible resource URLs and matching runtime challenges',async()=>{
 const discovery:any=await (await get('/.well-known/x402')).json();
 expect(discovery.version).toBe(1);expect(discovery.x402Version).toBe(2);expect(discovery.resources).toEqual(['https://api.tossmap.com/v1/search?zip=10001&material=paint','https://api.tossmap.com/v1/facilities/dsny-special-waste-drop-off-bronx','https://api.tossmap.com/v1/snapshot']);
 for(const url of discovery.resources){
  const parsed=new URL(url);const res=await get(parsed.pathname+parsed.search);expect(res.status).toBe(402);
  const body:any=await res.json();const header:any=decodePaymentRequiredHeader(res.headers.get('PAYMENT-REQUIRED')!);
  for(const field of ['x402Version','accepts','resource','extensions'])expect(body[field]).toEqual(header[field]);
  const bazaar=body.extensions.bazaar;expect(bazaar.info.input.method).toBe('GET');const properties=bazaar.schema.properties.input.properties;
  if(url.includes('/search?')){expect(bazaar.info.input.queryParams).toMatchObject({zip:'10001',material:'paint'});expect(Object.keys(properties.queryParams.properties)).toEqual(expect.arrayContaining(['zip','lat','lng','city','state','radius_mi','material','businesses_accepted','fee_charged','residents_only','limit']));}
  if(url.includes('/facilities/'))expect(properties.pathParams.properties.id.type).toBe('string');
 }
});
