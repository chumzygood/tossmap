import {readFile} from 'node:fs/promises';
import {privateKeyToAccount} from 'viem/accounts';
import {wrapFetchWithPaymentFromConfig,decodePaymentResponseHeader} from '@x402/fetch';
import {ExactEvmScheme} from '@x402/evm/exact/client';
try {
 if(!process.env.BASE_URL||!process.env.BUYER_KEY_FILE) throw Error('missing configuration');
 const key=(await readFile(process.env.BUYER_KEY_FILE,'utf8')).trim();
 const account=privateKeyToAccount(key);
 const paid=wrapFetchWithPaymentFromConfig(fetch,{schemes:[{network:'eip155:*',client:new ExactEvmScheme(account)}]});
 const response=await paid(new URL(process.env.PAY_PATH||'/v1/snapshot',process.env.BASE_URL));
 console.log('status:',response.status);
 const header=response.headers.get('PAYMENT-RESPONSE');
 if(header){const {transaction,payer,network}=decodePaymentResponseHeader(header);console.log(JSON.stringify({transaction,payer,network}));}
 if(!response.ok)process.exitCode=1;
} catch {console.error('Payment test failed; check BASE_URL, BUYER_KEY_FILE, balance, and facilitator availability.');process.exitCode=1;}
