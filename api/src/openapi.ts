const location = [
 {name:'zip',in:'query',schema:{type:'string',pattern:'^[0-9]{5}$',example:'10001'}},
 {name:'lat',in:'query',schema:{type:'number',minimum:-90,maximum:90}},
 {name:'lng',in:'query',schema:{type:'number',minimum:-180,maximum:180}},
 {name:'city',in:'query',schema:{type:'string'}},
 {name:'state',in:'query',schema:{type:'string'}}
].map(p=>({...p,required:false,description:'Use ZIP, lat and lng, or a covered city and state.'}));
export const searchParameters = [...location,
 {name:'radius_mi',in:'query',schema:{type:'number',exclusiveMinimum:0,maximum:100,default:25}},
 {name:'limit',in:'query',schema:{type:'integer',minimum:1,maximum:10,default:10}},
 {name:'material',in:'query',description:'Hyphens may replace underscores',schema:{type:'string',enum:['paint','tires','e_waste','batteries','motor_oil','household_chemicals','e-waste','motor-oil','household-chemicals'],example:'paint'}},
 ...['businesses_accepted','fee_charged','residents_only'].map(name=>({name,in:'query',schema:{type:'string',enum:['yes','no']}}))];
const freeResponses={'200':{description:'Successful response'},'400':{description:'Invalid request'},'429':{description:'Rate limit exceeded; see Retry-After'}};
const paidResponses=(description:string)=>({...freeResponses,'200':{description:'JSON response. Confirm with the operator before driving; a listing does not guarantee acceptance.',headers:{'PAYMENT-RESPONSE':{description:'Base64-encoded x402 settlement receipt for paid requests',schema:{type:'string'}}}},'402':{description,headers:{'PAYMENT-REQUIRED':{description:'Base64-encoded x402 v2 payment requirements',schema:{type:'string'}}}},'404':{description:'Facility not found'},'409':{description:'Signature already used or settlement outcome uncertain'},'502':{description:'Facilitator rejected settlement; inspect reason'},'503':{description:'Payment configuration or facilitator unavailable'}});
const payment=(amount:string)=>({protocols:[{x402:{}}],price:{mode:'fixed',currency:'USD',amount}});
export const openapi={openapi:'3.1.0',info:{title:'TossMap API',version:'1.0.0',description:'Coverage is free. Three searches with results per IPv4 address or IPv6 /64 prefix per UTC day and all empty searches are free. Other paid calls use x402 v2 exact USDC. MCP tools are available at https://api.tossmap.com/mcp.','x-guidance':'Check free coverage first, then search. Search costs $0.01 after three free result-bearing searches per day; empty searches are free. Facility details cost $0.005 and snapshots $5.00. Confirm with the operator before driving; a listing does not guarantee acceptance.',contact:{url:'https://tossmap.com'}},'x-mcp':{url:'https://api.tossmap.com/mcp',transport:'streamable-http'},servers:[{url:'https://api.tossmap.com'}],paths:{
 '/':{get:{operationId:'getGuide',summary:'API guide',security:[],responses:freeResponses}},
 '/llms.txt':{get:{operationId:'getAgentGuide',summary:'Agent guide',security:[],responses:freeResponses}},
 '/openapi.json':{get:{operationId:'getOpenApi',summary:'OpenAPI specification',security:[],responses:freeResponses}},
 '/.well-known/x402':{get:{operationId:'getPaymentDiscovery',summary:'Payment discovery',security:[],responses:freeResponses}},
 '/v1/meta':{get:{operationId:'getMetadata',summary:'Dataset metadata',security:[],responses:freeResponses}},
 '/v1/metros':{get:{operationId:'listMetros',summary:'Covered metros',security:[],responses:freeResponses}},
 '/v1/coverage':{get:{operationId:'getCoverage',summary:'Nearest covered metro',security:[],parameters:location,responses:freeResponses}},
 '/v1/search':{get:{operationId:'searchFacilities',summary:'Search facilities',description:'Requires a location and a material or filter. The first 3 searches per day with results and all empty searches are free; later searches with results cost $0.01 USDC via x402 v2 per IPv4 address or IPv6 /64 prefix per UTC day.',parameters:searchParameters,'x-payment-info':payment('0.01'),responses:paidResponses('$0.01 USDC payment required after free allowance')}},
 '/v1/search/paid':{get:{operationId:'searchFacilitiesPaid',summary:'Paid search for directories',description:'Search with results costs $0.01; empty searches are free.',parameters:searchParameters,'x-payment-info':payment('0.01'),responses:paidResponses('$0.01 USDC payment required')}},
 '/v1/facilities/{id}':{get:{operationId:'getFacility',summary:'Facility detail',description:'$0.005 USDC via x402 v2.',parameters:[{name:'id',in:'path',required:true,schema:{type:'string',example:'dsny-special-waste-drop-off-bronx'}}],'x-payment-info':payment('0.005'),responses:paidResponses('$0.005 USDC payment required')}},
 '/v1/snapshot':{get:{operationId:'getSnapshot',summary:'Full dataset',description:'$5 USDC via x402 v2. @x402/core 2.23+ client libraries default to a $1 spend limit; raise your client spend limit to at least $5 to buy the snapshot.','x-payment-info':payment('5.00'),responses:paidResponses('$5 USDC payment required. Raise the client spend limit to at least $5.')}}}};
