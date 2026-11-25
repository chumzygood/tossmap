import { DurableObject } from 'cloudflare:workers';
import { HTTPFacilitatorClient } from '@x402/core/server';
import { decodePaymentSignatureHeader, encodePaymentResponseHeader } from '@x402/core/http';
export class State extends DurableObject {
 async fetch(request:Request):Promise<Response> {
  const body:any=await request.json();
  if(body.action==='remaining'){const n=(await this.ctx.storage.get<number>('day:'+new Date().toISOString().slice(0,10)))||0;return Response.json({remaining:Math.max(0,3-n)});}
  if(body.action==='allowance') return this.ctx.blockConcurrencyWhile(async()=>{const day=new Date().toISOString().slice(0,10);const key='day:'+day;const n=(await this.ctx.storage.get<number>(key))||0;if(n<3)await this.ctx.storage.put(key,n+1);return Response.json({allowed:n<3,remaining:Math.max(0,3-n-1)});});
  if(body.action==='payment') return this.ctx.blockConcurrencyWhile(async()=>{
   const previous:any=await this.ctx.storage.get('payment');
   if(previous){if(previous.resource!==body.resource)return Response.json({error:'Signature already used for a different request'}, {status:409});if(previous.status==='failed')return Response.json(previous.result,{status:502});if(previous.status==='done'&&Date.now()-previous.time<900000)return Response.json(previous.result);return Response.json({error:'Payment already submitted or settlement outcome unknown'}, {status:409});}
   let payload;try{payload=decodePaymentSignatureHeader(body.signature);}catch{return Response.json({error:'Invalid payment signature'}, {status:400});}
   const r=body.requirements;
   if(payload.x402Version!==2||!payload.accepted||['scheme','network','asset','amount','payTo','maxTimeoutSeconds'].some(k=>(payload.accepted as any)[k]!==r[k])||payload.accepted.extra?.name!==r.extra.name||payload.accepted.extra?.version!==r.extra.version) return Response.json({error:'Payment requirements do not match'}, {status:400});
   const client=new HTTPFacilitatorClient({url:body.facilitatorUrl});
   try {const verify=await client.verify(payload,r);if(!verify.isValid)return Response.json({error:'Payment verification failed',...(typeof verify.invalidReason==='string'?{reason:verify.invalidReason}:{})}, {status:402});}
   catch{return Response.json({error:'Payment verification unavailable'}, {status:503});}
   await this.ctx.storage.put('payment',{status:'pending',resource:body.resource,time:Date.now()});
   try {const settled=await client.settle(payload,r);if(!settled.success){const reason=typeof settled.errorReason==='string'?settled.errorReason:undefined;const result={error:'Payment settlement failed',...(reason!==undefined?{reason}:{})};await this.ctx.storage.put('payment',{status:'failed',resource:body.resource,time:Date.now(),result});console.error(JSON.stringify({event:'payment_settlement_failed',errorReason:reason}));return Response.json(result,{status:502});} const result={receipt:encodePaymentResponseHeader(settled),transaction:settled.transaction};await this.ctx.storage.put('payment',{status:'done',resource:body.resource,time:Date.now(),result});return Response.json(result);}
   catch{return Response.json({error:'Payment settlement outcome unknown; contact the operator'}, {status:503});}
  });
  return Response.json({error:'Unknown action'},{status:400});
 }
}
