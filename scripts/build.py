import json,html,re,os,shutil
BASE="https://example.com"  # TODO: set to final domain
D=json.load(open("data/facilities.json")); OUT="site"
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
e=html.escape
slug=lambda s:re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
CSS="""*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,sans-serif;color:#1d2a24;background:#f7f8f6}
header,footer{background:#1f4d3a;color:#fff;padding:14px 20px}header a,footer a{color:#fff}main{max-width:900px;margin:0 auto;padding:20px}
a{color:#1f6b4d}.card{background:#fff;border:1px solid #dfe5e0;border-radius:8px;padding:16px;margin:14px 0}
.card h3{margin:0 0 6px}.meta{font-size:13px;color:#5b6b63}.ad{border:1px dashed #b9c4bd;color:#8a978f;text-align:center;padding:24px;margin:18px 0;font-size:12px}
ul.grid{columns:3 200px;padding-left:18px}.note{background:#fff7e0;border-left:4px solid #e0b030;padding:10px 14px}"""
open(f"{OUT}/style.css","w").write(CSS)
GC="<!-- GoatCounter: replace CODE then uncomment\n<script data-goatcounter=\"https://CODE.goatcounter.com/count\" async src=\"//gc.zgo.at/count.js\"></script> -->"
AD=lambda n:f'<div class="ad" data-ad-slot="{n}">Ad slot ({n})</div>'
urls=[]
def page(path,title,desc,body,ld=""):
    urls.append(path); p=f"{OUT}{path}"+("index.html" if path.endswith("/") else "")
    os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,"w").write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}"><link rel="stylesheet" href="/style.css">{ld}
{GC}</head><body><header><a href="/"><strong>Where to Toss It</strong></a> · hazardous waste, paint, e-waste &amp; tire drop-offs</header><main>{body}</main>
<footer>Data from official government sources, checked 2026-11-02. Always confirm with the source before driving. · <a href="/privacy.html">Privacy</a></footer></body></html>""")
states={}
for m in D: states.setdefault((m["state"],m["st"]),[]).append(m)
def fac(f):
    return f"""<div class="card"><h3>{e(f['name'])}</h3><div>{e(f['address'])}</div>
<p><b>Accepts:</b> {e(f['accepts'])}<br><b>Hours:</b> {e(f['hours'])}{'<br><b>Fees:</b> '+e(f['fees']) if f['fees'] else ''}{'<br><b>Notes:</b> '+e(f['notes']) if f['notes'] else ''}</p>
<div class="meta">Source: <a href="{e(f['source'])}" rel="nofollow noopener">{e(f['source'])}</a> · Last checked {f['checked']}</div></div>"""
def ldj(f):
    return {"@type":"LocalBusiness","name":f["name"],"address":{"@type":"PostalAddress","streetAddress":f["address"]},"openingHours":f["hours"],"url":f["source"]}
for (sn,st),ms in sorted(states.items()):
    sp=f"/{slug(st)}/"
    for m in ms:
        cp=f"{sp}{slug(m['city'])}/"
        note=f'<p class="note">{e(m["note"])}</p>' if m["note"] else ""
        body=f'<p><a href="/">Home</a> › <a href="{sp}">{e(sn)}</a></p><h1>Hazardous waste drop-off in {e(m["city"])}, {st}</h1>{note}'+AD("city-top")+"".join(fac(f) for f in m["facilities"])+(("<p>No permanent drop-off site found in official sources.</p>") if not m["facilities"] else "")+AD("city-bottom")
        ld='<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@graph":[ldj(f) for f in m["facilities"]]})+"</script>" if m["facilities"] else ""
        page(cp,f"Where to dump paint, chemicals & e-waste in {m['city']}, {st}",f"{len(m['facilities'])} verified drop-off sites in {m['city']} with hours, accepted items and official sources.",body,ld)
    page(sp,f"Hazardous waste drop-off in {sn}",f"Verified household hazardous waste drop-off sites in {sn}.",f'<p><a href="/">Home</a></p><h1>{e(sn)}</h1>'+AD("state-top")+"<ul>"+"".join(f'<li><a href="{sp}{slug(m["city"])}/">{e(m["city"])}</a> ({len(m["facilities"])} sites)</li>' for m in ms)+"</ul>")
n=sum(len(m["facilities"]) for m in D)
page("/","Where to Toss It – hazardous waste & e-waste drop-off by city","Find official drop-off sites for paint, chemicals, batteries, electronics and tires in 50 US metros.",
 f"<h1>Where do I take paint, chemicals, batteries &amp; electronics?</h1><p>{n} verified government drop-off sites across {len(D)} US metros. Every listing links to its official source.</p>"+AD("home-top")+
 "<h2>By city</h2><ul class=grid>"+"".join(f'<li><a href="/{slug(m["st"])}/{slug(m["city"])}/">{e(m["city"])}, {m["st"]}</a></li>' for m in sorted(D,key=lambda x:x["city"]))+"</ul><h2>By state</h2><ul class=grid>"+"".join(f'<li><a href="/{slug(st)}/">{e(sn)}</a></li>' for sn,st in sorted(states))+"</ul>")
page("/privacy.html","Privacy","Privacy policy","<h1>Privacy</h1><p>We collect no personal data and set no cookies. We may use GoatCounter, a privacy-friendly analytics service that does not track individuals. If ads are added, ad partners may use cookies; this page will be updated before that happens.</p><p>Listings come from public government sources and may change; confirm with the source before visiting.</p>")
open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{BASE}{u}</loc><lastmod>2026-11-02</lastmod></url>" for u in urls)+"</urlset>\n")
print(len(urls),"pages;",len(states),"states;",n,"facilities")
