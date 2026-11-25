export const domains: Record<string, {name:string; version:string}> = {
 'eip155:84532': {name:'USDC',version:'2'},
 'eip155:8453': {name:'USD Coin',version:'2'},
};

export const DEFAULT_FACILITATOR = 'https://facilitator.payai.network';
export const TESTNET_FACILITATOR = 'https://x402.org/facilitator';
export function facilitatorConfig(value: string | undefined, network: string): {url: string; error?: string} {
 const url = value || DEFAULT_FACILITATOR;
 if (url !== DEFAULT_FACILITATOR && url !== TESTNET_FACILITATOR) return {url, error:'Payments unavailable: FACILITATOR_URL is not allowed'};
 if (url === TESTNET_FACILITATOR && network === 'eip155:8453') return {url, error:'Payments unavailable: x402.org facilitator is testnet-only'};
 return {url};
}
