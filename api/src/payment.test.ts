import {expect,it} from 'vitest';
import {domains} from './payment';
it('uses the on-chain USDC domain for each supported Base network',()=>{
 expect(domains['eip155:84532']).toEqual({name:'USDC',version:'2'});
 expect(domains['eip155:8453']).toEqual({name:'USD Coin',version:'2'});
});

import {DEFAULT_FACILITATOR, TESTNET_FACILITATOR, MOGAMI_FACILITATOR, DEXTER_FACILITATOR, facilitatorConfig} from './payment';
it('allows only the configured facilitator URLs and defaults to PayAI',()=>{
 for(const value of [undefined,'',DEFAULT_FACILITATOR]) expect(facilitatorConfig(value,'eip155:84532')).toEqual({url:DEFAULT_FACILITATOR});
 for(const url of [DEFAULT_FACILITATOR, TESTNET_FACILITATOR, MOGAMI_FACILITATOR, DEXTER_FACILITATOR]) {
  expect(facilitatorConfig(url+'/', 'eip155:84532')).toEqual({url});
  expect(facilitatorConfig(url, 'eip155:84532')).toEqual({url});
 }
 for(const url of [DEFAULT_FACILITATOR, MOGAMI_FACILITATOR, DEXTER_FACILITATOR]) expect(facilitatorConfig(url,'eip155:8453')).toEqual({url});
 for(const value of ['http://facilitator.payai.network','https://facilitator.payai.network.evil.test','https://x402.org/facilitator//','https://x402.org/facilitator?x=1']) expect(facilitatorConfig(value,'eip155:84532').error).toMatch(/not allowed/);
 expect(facilitatorConfig(TESTNET_FACILITATOR,'eip155:8453').error).toMatch(/testnet-only/);
 expect(facilitatorConfig(DEFAULT_FACILITATOR,'eip155:8453').error).toBeUndefined();
});
