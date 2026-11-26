import {expect,it,vi} from 'vitest';
import worker from '../src/index';
const limit={limit:async()=>({success:true})};
const call=async(facilitator:string,network='eip155:84532',path='/v1/snapshot',signature=false)=>{
 const fetchState=vi.fn(async (_url:string, init:RequestInit)=>Response.json({receipt:'receipt',transaction:'tx'}));
 const env={GENERAL_LIMIT:limit,CHALLENGE_LIMIT:limit,STATE:{idFromName:(key:string)=>key,get:()=>({fetch:fetchState})},FACILITATOR_URL:facilitator,X402_NETWORK:network,PAY_TO_ADDRESS:'0x000000000000000000000000000000000000dEaD'};
 const response=await worker.fetch(new Request('https://api.test'+path,{headers:signature?{'PAYMENT-SIGNATURE':'test'}:{}}),env as any);
 return {response,fetchState};
};
it('reports configuration errors on paid routes while leaving free documentation available',async()=>{
 for(const [url,network,reason] of [['https://evil.test','eip155:84532','not allowed'],['https://x402.org/facilitator','eip155:8453','testnet-only']]){
  const {response}=await call(url,network);expect(response.status).toBe(503);expect((await response.json() as any).error).toContain(reason);
 }
 expect((await call('https://evil.test','eip155:84532','/v1/meta')).response.status).toBe(200);
});
it('exposes and forwards the selected facilitator',async()=>{
 for(const url of ['https://facilitator.payai.network','https://x402.org/facilitator','https://v2.facilitator.mogami.tech','https://x402.dexter.cash']) {
 expect((await (await call(url,'eip155:84532','/.well-known/x402')).response.json() as any).facilitator).toBe(url);
 expect(await (await call(url,'eip155:84532','/llms.txt')).response.text()).toContain('facilitator: '+url);
 const {response,fetchState}=await call(url,'eip155:84532','/v1/snapshot',true);expect(response.status).toBe(200);expect(JSON.parse(fetchState.mock.calls[0][1].body as string).facilitatorUrl).toBe(url);
 }
});
