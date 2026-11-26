import registry from '../server.json';
export {registry};
export const protocolVersion='2025-11-25';
const location={zip:{type:'string',pattern:'^[0-9]{5}$'},city:{type:'string',minLength:1},state:{type:'string',pattern:'^[A-Za-z]{2}$'}};
const annotations={readOnlyHint:true,openWorldHint:false};
const outputSchema={type:'object',additionalProperties:true};
export const tools=[
 {name:'search_facilities',description:'Find facilities by ZIP or covered city and material.',inputSchema:{type:'object',properties:{...location,material:{type:'string',enum:['tires','paint','e_waste','batteries','motor_oil','household_chemicals']},limit:{type:'integer',minimum:1,maximum:10}},required:['material'],anyOf:[{required:['zip']},{required:['city']}],additionalProperties:false},outputSchema,annotations},
 {name:'get_facility',description:'Get a facility by ID.',inputSchema:{type:'object',properties:{id:{type:'string',minLength:1}},required:['id'],additionalProperties:false},outputSchema,annotations},
 {name:'coverage',description:'Check coverage by ZIP or covered city.',inputSchema:{type:'object',properties:location,anyOf:[{required:['zip']},{required:['city']}],additionalProperties:false},outputSchema,annotations}
];
export const card={$schema:'https://static.modelcontextprotocol.io/schemas/mcp-server-card/v1.json',version:'1.0',protocolVersion,serverInfo:{name:'tossmap',title:'TossMap',version:'1.0.0'},description:registry.description,documentationUrl:'https://api.tossmap.com/llms.txt',transport:{type:'streamable-http',endpoint:'https://api.tossmap.com/mcp'},capabilities:{tools:{}},authentication:{required:false},tools,resources:[],prompts:[]};
