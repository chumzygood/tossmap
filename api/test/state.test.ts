import {beforeEach,describe,expect,it,vi} from 'vitest';
const mock=vi.hoisted(()=>({verify:vi.fn(),settle:vi.fn()}));
vi.mock('@x402/core/server',()=>({HTTPFacilitatorClient:class {verify=mock.verify;settle=mock.settle;}}));
vi.mock('@x402/core/http',()=>({decodePaymentSignatureHeader:(s:string)=>JSON.parse(s),encodePaymentResponseHeader:()=> 'receipt'}));
import {State} from '../src/state';
let state:any;const requirements={scheme:'exact',network:'eip155:84532',asset:'asset',amount:'10000',payTo:'address',maxTimeoutSeconds:300,extra:{name:'USDC',version:'2'}};
const request=(body:unknown)=>new Request('https://state/',{method:'POST',body:JSON.stringify(body)});
beforeEach(()=>{const storage=new Map();const ctx={storage:{get:async(k:string)=>storage.get(k),put:async(k:string,v:unknown)=>storage.set(k,v)},blockConcurrencyWhile:async(fn:()=>Promise<unknown>)=>fn()};state=new State(ctx as any,{} as any);mock.verify.mockReset().mockResolvedValue({isValid:true});mock.settle.mockReset().mockResolvedValue({success:true,transaction:'0xtx',network:'eip155:84532'});});
describe('durable state',()=>{
 it('allows three searches with results and stops at zero remaining',async()=>{const out=[];for(let i=0;i<4;i++)out.push(await (await state.fetch(request({action:'allowance'}))).json());expect(out).toEqual([{allowed:true,remaining:2},{allowed:true,remaining:1},{allowed:true,remaining:0},{allowed:false,remaining:0}]);});
 it('settles a signature once and returns the same receipt on retry',async()=>{const signature=JSON.stringify({x402Version:2,accepted:requirements,payload:{}});const body={action:'payment',signature,requirements,resource:'https://api.test/search'};const first=await state.fetch(request(body));const second=await state.fetch(request(body));expect(await first.json()).toEqual(await second.json());expect(mock.verify).toHaveBeenCalledTimes(1);expect(mock.settle).toHaveBeenCalledTimes(1);const other=await state.fetch(request({...body,resource:'https://api.test/other'}));expect(other.status).toBe(409);});
 it('fails closed when settlement outcome is unknown',async()=>{mock.settle.mockRejectedValueOnce(Error('timeout'));const signature=JSON.stringify({x402Version:2,accepted:requirements,payload:{}});const body={action:'payment',signature,requirements,resource:'https://api.test/search'};expect((await state.fetch(request(body))).status).toBe(503);expect((await state.fetch(request(body))).status).toBe(409);expect(mock.settle).toHaveBeenCalledTimes(1);});
});
