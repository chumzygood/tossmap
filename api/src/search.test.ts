import {describe,it,expect} from 'vitest';
import {search,locate,distance,type Facility,type Metro} from './search';
const q=(values:Record<string,string>)=>new URLSearchParams(values);
const metros:Metro[]=[{id:'a',city:'A',state:'NY',location:{lat:40,lng:-74}},{id:'b',city:'B',state:'NY',location:{lat:42,lng:-74}}];
const facilities:Facility[]=[{id:'far',name:'Far',metro:'a',state:'NY',lat:40.1,lng:-74,questions:{paint:{answer:'yes'},fee_charged:{answer:'yes'}}},{id:'near',name:'Near',metro:'a',state:'NY',lat:40.01,lng:-74,questions:{paint:{answer:'yes'},fee_charged:{answer:'no'}}},{id:'unknown',name:'Unknown',metro:'a',state:'NY',lat:null,lng:null,questions:{paint:{answer:'yes'}}}];
const zips={'10001':[40,-74]};
describe('search',()=>{
 it('ranks by distance and excludes missing coordinates',()=>expect(search(q({zip:'10001',material:'paint'}),facilities,metros,zips).results.map(x=>x.id)).toEqual(['near','far']));
 it('applies structured filters',()=>expect(search(q({city:'A',state:'NY',fee_charged:'no'}),facilities,metros,zips).results.map(x=>x.id)).toEqual(['near']));
 it('returns empty results without charging decision',()=>expect(search(q({zip:'10001',material:'tires'}),facilities,metros,zips).count).toBe(0));
 it('validates location, filters and limits',()=>{expect(()=>search(q({zip:'10001'}),facilities,metros,zips)).toThrow();expect(()=>search(q({material:'paint'}),facilities,metros,zips)).toThrow();expect(()=>search(q({zip:'10001',material:'paint',limit:'11'}),facilities,metros,zips)).toThrow();});
 it('finds nearest metro',()=>expect(locate(q({lat:'40',lng:'-74'}),metros,zips).nearest?.id).toBe('a'));
 it('computes distance',()=>expect(distance(40,-74,40,-74)).toBe(0));
});
