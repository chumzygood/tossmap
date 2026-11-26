import {afterEach, expect, it, vi} from 'vitest';
import {encodePaymentSignatureHeader} from '@x402/core/http';
import {State} from '../src/state';

const requirements = {scheme:'exact',network:'eip155:84532',asset:'asset',amount:'10000',payTo:'address',maxTimeoutSeconds:300,extra:{name:'USDC',version:'2'}};

afterEach(()=>vi.unstubAllGlobals());
it.each([
 'https://facilitator.payai.network',
 'https://x402.org/facilitator',
 'https://v2.facilitator.mogami.tech',
 'https://x402.dexter.cash',
])('sends verify and settle to the exact URLs for %s',async base=>{
 const fetchMock=vi.fn(async (url:string)=>Response.json(url.endsWith('/verify')
  ? {isValid:true}
  : {success:true,transaction:'0xtx',network:'eip155:84532',payer:'0xpayer'}));
 vi.stubGlobal('fetch',fetchMock);
 const storage=new Map();
 const ctx={storage:{get:async(k:string)=>storage.get(k),put:async(k:string,v:unknown)=>storage.set(k,v)},blockConcurrencyWhile:async(fn:()=>Promise<unknown>)=>fn()};
 const state=new State(ctx as any,{} as any);
 const signature=encodePaymentSignatureHeader({x402Version:2,accepted:requirements,payload:{}} as any);
 const response=await state.fetch(new Request('https://state/',{method:'POST',body:JSON.stringify({action:'payment',signature,requirements,resource:'https://api.test/search',facilitatorUrl:base})}));
 expect(response.status).toBe(200);
 expect(fetchMock.mock.calls.map(call=>call[0])).toEqual([base+'/verify',base+'/settle']);
});
