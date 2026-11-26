export const domains: Record<string, {name:string; version:string}> = {
 'eip155:84532': {name:'USDC',version:'2'},
 'eip155:8453': {name:'USD Coin',version:'2'},
};

export const DEFAULT_FACILITATOR = 'https://facilitator.payai.network';
export const TESTNET_FACILITATOR = 'https://x402.org/facilitator';
export const MOGAMI_FACILITATOR = 'https://v2.facilitator.mogami.tech';
export const DEXTER_FACILITATOR = 'https://x402.dexter.cash';
export function facilitatorConfig(value: string | undefined, network: string): {url: string; error?: string} {
 const url = (value || DEFAULT_FACILITATOR).replace(/\/$/, '');
 if (![DEFAULT_FACILITATOR, TESTNET_FACILITATOR, MOGAMI_FACILITATOR, DEXTER_FACILITATOR].includes(url)) return {url, error:'Payments unavailable: FACILITATOR_URL is not allowed'};
 if (url === TESTNET_FACILITATOR && network === 'eip155:8453') return {url, error:'Payments unavailable: x402.org facilitator is testnet-only'};
 return {url};
}
