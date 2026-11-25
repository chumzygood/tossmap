#!/usr/bin/env python3
"""Export TossMap API data; geocoding cache is persistent and reusable."""
import collections, csv, hashlib, io, json, math, pathlib, re, statistics, time, urllib.parse, urllib.request, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT/'api/data'; OUT = ROOT/'api/src/data'
DATA.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
cachepath = DATA/'geocode-cache.json'
cache = json.loads(cachepath.read_text()) if cachepath.exists() else {}
UA = 'TossMap-API/1.0 (tossmap.com)'
last_nominatim = 0.0

def get(url, params):
    req = urllib.request.Request(url+'?'+urllib.parse.urlencode(params), headers={'User-Agent':UA})
    with urllib.request.urlopen(req, timeout=18) as r: return json.load(r)

def lookup(key, address, fallback=True):
    global last_nominatim
    if key in cache: return cache[key]
    result = None
    try:
        hits = get('https://geocoding.geo.census.gov/geocoder/locations/onelineaddress', {'address':address,'benchmark':'Public_AR_Current','format':'json'})['result']['addressMatches']
        if hits:
            h=hits[0]; result={'lat':h['coordinates']['y'],'lng':h['coordinates']['x'],'zip':h['addressComponents'].get('zip'), 'source':'US Census','quality':'address match'}
    except Exception as e: print('Census error:', key, str(e), flush=True)
    if not result and fallback:
        try:
            time.sleep(max(0, 1.05-(time.monotonic()-last_nominatim))); last_nominatim=time.monotonic()
            hits=get('https://nominatim.openstreetmap.org/search',{'q':address,'countrycodes':'us','format':'jsonv2','addressdetails':1,'limit':1})
            if hits:
                h=hits[0]; result={'lat':float(h['lat']),'lng':float(h['lon']),'zip':h.get('address',{}).get('postcode','')[:5], 'source':'Nominatim','quality':h.get('type','unknown')}
        except Exception as e: print('Nominatim error:', key, str(e), flush=True)
    cache[key]=result
    cachepath.write_text(json.dumps(cache,indent=2,sort_keys=True)+'\n')
    return result

def dist(a,b):
    p1,p2=map(math.radians,(a['lat'],b['lat'])); dp=p2-p1; dl=math.radians(b['lng']-a['lng']); return 3958.8*2*math.asin(min(1,math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2)))
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def main():
    zipfile_path=DATA/'2020_Gaz_zcta_national.zip'
    if not zipfile_path.exists():
        urllib.request.urlretrieve('https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2020_Gazetteer/2020_Gaz_zcta_national.zip',zipfile_path)
    with zipfile.ZipFile(zipfile_path) as z:
        with z.open(z.namelist()[0]) as f:
            rows=csv.DictReader(io.TextIOWrapper(f),delimiter='\t'); zips={}
            for row in rows:
                row={k.strip():v.strip() for k,v in row.items()}; zips[row['GEOID']]=[round(float(row['INTPTLAT']),5),round(float(row['INTPTLONG']),5)]
    (OUT/'zips.json').write_text(json.dumps(zips,separators=(',',':'))+'\n')
    metros=json.loads((ROOT/'data/facilities.json').read_text()); counts=collections.Counter(f['slug'] for m in metros for f in m['facilities']); output=[]; metroout=[]; unresolved=[]; filled=0
    for m in metros:
        mk=slug(m['city'])+'-'+m['st'].lower(); center=lookup('metro:'+mk,m['city']+', '+m['st'])
        if not center:
            known=[zips[x] for f in m['facilities'] if (q:=re.search(r'\b\d{5}\b',f['address'])) and (x:=q.group()) in zips]
            if known: center={'lat':statistics.median(x[0] for x in known),'lng':statistics.median(x[1] for x in known),'source':'ZCTA median','quality':'approximate'}
        metroout.append({'id':mk,'city':m['city'],'state':m['st'],'location':center})
        for f in m['facilities']:
            key='facility:'+mk+':'+f['slug']; g=lookup(key,f['address'])
            if g and center and dist(g,center)>80:
                print('OUTLIER', key, round(dist(g,center)), flush=True)
                g=None
            original=re.search(r'\b\d{5}\b',f['address']); zipcode=original.group() if original else (g or {}).get('zip')
            if not original and zipcode and re.fullmatch(r'\d{5}',zipcode): filled+=1
            if not g: unresolved.append(key)
            q=f.get('questions',{}); output.append({'id':(mk+'-'+f['slug'] if counts[f['slug']]>1 else f['slug']),'slug':f['slug'],'name':f['name'],'address':f['address'],'metro':mk,'state':m['st'],'lat':g['lat'] if g else None,'lng':g['lng'] if g else None,'zip':zipcode or None,'geocode':g,'materials':{k:v.get('answer')=='yes' for k,v in q.items()},'questions':q,'hours':f.get('hours'),'accepts_text':f.get('accepts'),'fees':f.get('fees'),'notes':f.get('notes'),'source_url':f.get('source'),'last_checked':f.get('checked'),'page_url':f"https://tossmap.com/{m['st'].lower()}/{slug(m['city'])}/{f['slug']}/"})
    raw=json.dumps(output,ensure_ascii=False,separators=(',',':')).encode(); (OUT/'facilities.json').write_bytes(raw+b'\n'); (OUT/'metros.json').write_text(json.dumps(metroout,separators=(',',':'))+'\n'); (OUT/'version.json').write_text(json.dumps({'version':max(f['last_checked'] for f in output if f['last_checked']),'sha256':hashlib.sha256(raw+b'\n').hexdigest()},indent=2)+'\n')
    print(f'Geocoded {len(output)-len(unresolved)}/{len(output)}; ZIP filled {filled}; unresolved: {unresolved}',flush=True)
if __name__=='__main__': main()
