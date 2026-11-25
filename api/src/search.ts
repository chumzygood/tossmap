export type Facility = {id:string; name:string; metro:string; state:string; lat:number|null; lng:number|null; questions:Record<string,{answer:string}>; [key:string]:unknown};
export type Metro = {id:string; city:string; state:string; location:{lat:number;lng:number}|null};
export function distance(a:number,b:number,c:number,d:number) {const r=Math.PI/180, p=(c-a)*r, q=(d-b)*r;return 2*3958.8*Math.asin(Math.min(1,Math.sqrt(Math.sin(p/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin(q/2)**2)));}
export function locate(p:URLSearchParams, metros:Metro[], zips:Record<string,number[]>) {
  let lat:number, lng:number;
  if(p.has('zip')) {let z=p.get('zip')!; if(!/^\d{5}$/.test(z)||!zips[z]) throw Error('Unknown or invalid ZIP'); [lat,lng]=zips[z];}
  else if(p.has('lat')&&p.has('lng')) {lat=Number(p.get('lat'));lng=Number(p.get('lng'));if(!p.get('lat')||!p.get('lng')||!Number.isFinite(lat)||!Number.isFinite(lng)||Math.abs(lat)>90||Math.abs(lng)>180) throw Error('Invalid latitude or longitude');}
  else if(p.has('city')&&p.has('state')) {const m=metros.find(m=>m.city.toLowerCase()===p.get('city')!.trim().toLowerCase()&&m.state.toLowerCase()===p.get('state')!.trim().toLowerCase()); if(!m?.location) throw Error('Unknown covered city and state'); ({lat,lng}=m.location);}
  else throw Error('Provide zip, lat and lng, or city and state');
  const nearest=metros.filter(m=>m.location).map(m=>({...m,distance_mi:Math.round(distance(lat,lng,m.location!.lat,m.location!.lng)*10)/10})).sort((a,b)=>a.distance_mi-b.distance_mi)[0]||null;
  return {lat,lng,nearest};
}
export function search(p:URLSearchParams, facilities:Facility[], metros:Metro[], zips:Record<string,number[]>) {
 const location=locate(p,metros,zips), material=p.get('material')?.replace(/-/g,'_');
 const mats=['tires','paint','e_waste','batteries','motor_oil','household_chemicals'], filters=['businesses_accepted','fee_charged','residents_only'];
 if(material&&!mats.includes(material))throw Error('Unknown material');
 if(!material&&!filters.some(k=>p.has(k)))throw Error('Provide a material or filter');
 for(const k of filters)if(p.has(k)&&!['yes','no'].includes(p.get(k)!))throw Error(`${k} must be yes or no`);
 const radius=p.has('radius_mi')?Number(p.get('radius_mi')):25, limit=p.has('limit')?Number(p.get('limit')):10;
 if(!Number.isFinite(radius)||radius<=0||radius>100||!Number.isInteger(limit)||limit<1||limit>10)throw Error('radius_mi must be > 0 and <= 100; limit must be 1–10');
 const all=facilities.filter(f=>f.lat!==null&&f.lng!==null&&(!material||f.questions[material]?.answer==='yes')&&filters.every(k=>!p.has(k)||f.questions[k]?.answer===p.get(k))).map(f=>({...f,location:{lat:f.lat,lng:f.lng,distance_mi:Math.round(distance(location.lat,location.lng,f.lat!,f.lng!)*10)/10}})).filter(f=>f.location.distance_mi<=radius).sort((a,b)=>a.location.distance_mi-b.location.distance_mi||a.id.localeCompare(b.id));
 return {count:all.length,results:all.slice(0,limit),nearest_metro:location.nearest};
}
