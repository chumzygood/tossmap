import {expect,it} from 'vitest';
import {domains} from './payment';
it('uses the on-chain USDC domain for each supported Base network',()=>{
 expect(domains['eip155:84532']).toEqual({name:'USDC',version:'2'});
 expect(domains['eip155:8453']).toEqual({name:'USD Coin',version:'2'});
});
