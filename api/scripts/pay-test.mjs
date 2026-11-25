import {readFile} from 'node:fs/promises';
import {privateKeyToAccount} from 'viem/accounts';
import {wrapFetchWithPaymentFromConfig,decodePaymentResponseHeader} from '@x402/fetch';

let key='';
try {
 if(!process.env.BASE_URL||!process.env.BUYER_KEY_FILE) throw Error('missing configuration');
 const max=process.env.MAX_USD||'0.05';
 if(!/^\d+(\.\d{1,6})?$/.test(max)) throw Error('invalid MAX_USD');
 const [whole,fraction='']=max.split('.');
 const maxUnits=BigInt(whole)*1000000n+BigInt(fraction.padEnd(6,'0'));
 const url=new URL(process.env.PAY_PATH||'/v1/facilities/dsny-special-waste-drop-off-bronx',process.env.BASE_URL);
 const initial=await fetch(url);
 if(initial.status!==402) {
  console.log('status:',initial.status);
  if(!initial.ok) console.log('body:',(await initial.text()).slice(0,500));
  if(!initial.ok) process.exitCode=1;
 } else {
  const encoded=initial.headers.get('PAYMENT-REQUIRED');
  if(!encoded) throw Error('missing payment requirements');
  const required=JSON.parse(Buffer.from(encoded,'base64').toString('utf8'));
  if(!Array.isArray(required.accepts)||required.accepts.length!==1) throw Error('unexpected payment options');
  const {network,asset,amount,payTo,scheme}=required.accepts[0];
  console.log('PAYMENT-REQUIRED:',JSON.stringify({network,asset,amount,payTo}));
  const assets={'eip155:84532':'0x036cbd53842c5426634e7929541ec2318f3dcf7e','eip155:8453':'0x833589fcd6edb6e08f4c7c32d4f71b54bda02913'};
  if(scheme!=='exact'||!assets[network]||typeof asset!=='string'||asset.toLowerCase()!==assets[network]||!/^\d+$/.test(amount)||BigInt(amount)>maxUnits) throw Error('unsupported or excessive payment');
  if(network==='eip155:8453'&&process.env.ALLOW_MAINNET!=='1') throw Error('mainnet payment requires ALLOW_MAINNET=1');
  key=(await readFile(process.env.BUYER_KEY_FILE,'utf8')).trim();
  const account=privateKeyToAccount(key);
  // The client sees the already inspected challenge; no second challenge can change the price.
  let first=true;
  const guardedFetch=async(input,init)=>{if(first){first=false;return initial.clone();} return fetch(input,init);};
  const paid=wrapFetchWithPaymentFromConfig(guardedFetch,{schemes:[{network:'eip155:*',client:new ExactEvmScheme(account)}]});
  const response=await paid(url);
  console.log('status:',response.status);
  const header=response.headers.get('PAYMENT-RESPONSE');
  if(header){const {transaction,payer,network}=decodePaymentResponseHeader(header);console.log(JSON.stringify({transaction,payer,network}));}
  if(!response.ok){console.log('body:',(await response.text()).split(key).join('[redacted]').slice(0,500));process.exitCode=1;}
 }
} catch(e) {console.error('Payment test failed:', ['mainnet payment requires ALLOW_MAINNET=1','unsupported or excessive payment','invalid MAX_USD','missing payment requirements','unexpected payment options'].includes(e.message)?e.message:'check configuration, balance, and facilitator availability.');process.exitCode=1;}
