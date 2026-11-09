import json,html,re,os,shutil,datetime
BASE="https://tossmap.com"
D=json.load(open("data/facilities.json")); OUT="docs"
TODAY=datetime.date.today().isoformat()
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
e=html.escape
slug=lambda s:re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
CSS="""*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,sans-serif;color:#1d2a24;background:#f7f8f6}
header,footer{background:#1f4d3a;color:#fff;padding:14px 20px}header a,footer a{color:#fff}main{max-width:900px;margin:0 auto;padding:20px}
a{color:#1f6b4d}.card{background:#fff;border:1px solid #dfe5e0;border-radius:8px;padding:16px;margin:14px 0}
.card h3{margin:0 0 6px}.meta{font-size:13px;color:#5b6b63}.crumbs{font-size:14px}
ul.grid{columns:3 200px;padding-left:18px}.note{background:#fff7e0;border-left:4px solid #e0b030;padding:10px 14px}.tags a{display:inline-block;margin:0 8px 6px 0}"""
open(f"{OUT}/style.css","w").write(CSS)
GC='<meta name="google-site-verification" content="jAhRn0yYvjC37jRpBEzda-xllydn360g3kgkVonTDKA" /><script data-goatcounter="https://tossmap.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
# Material pages: keyword patterns matched against each listing's "accepts" text
MAT=[("paint","Paint","paint"),("e-waste","Electronics (e-waste)",r"e-waste|electronic|computer|tv|cell phone|monitor"),
     ("tires","Tires",r"\btires?\b"),("batteries","Batteries",r"batter"),("motor-oil","Motor oil",r"motor oil|automotive fluid|car fluid|used oil"),
     ("household-chemicals","Household chemicals",r"chemical|pesticide|solvent|cleaner")]
def mats(f):
    t=f["accepts"].lower()
    neg=re.findall(r"\((?:[^)]*?)(?:no|not)\s[^)]*\)|no [a-z ,]+",t)
    tt=t
    for n in neg: tt=tt.replace(n,"")
    return [m for m in MAT if re.search(m[2],tt)]
urls=[]
def ldscript(o): return '<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False)+"</script>"
def crumbs(items):
    vis='<p class="crumbs">'+" › ".join(f'<a href="{u}">{e(n)}</a>' for n,u in items)+"</p>"
    ld={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u} for i,(n,u) in enumerate(items)]}
    return vis,ld
def page(path,title,desc,body,graph=(),checked=None):
    urls.append((path,checked or TODAY)); p=f"{OUT}{path}"+("index.html" if path.endswith("/") else "")
    os.makedirs(os.path.dirname(p),exist_ok=True)
    ld=ldscript({"@context":"https://schema.org","@graph":list(graph)}) if graph else ""
    foot=f"Data from official government and operator sources{', checked '+checked if checked else ''}. Always confirm with the source before driving."
    open(p,"w").write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:type" content="website"><meta property="og:site_name" content="TossMap">
<link rel="stylesheet" href="/style.css">{ld}
{GC}</head><body><header><a href="/"><strong>TossMap</strong></a> · where to toss hazardous waste, paint, e-waste &amp; tires</header><main>{body}</main>
<footer>{foot} · <a href="/privacy.html">Privacy</a> · <a href="/embed/">Embed widget</a> · <a href="/for-cities/">For cities</a> · <a href="/partners/">Partners</a> · <a href="mailto:toolshed@mail.grokbot.com">Support</a></footer></body></html>""")
states={}
for m in D: states.setdefault((m["state"],m["st"]),[]).append(m)
cpath=lambda m:f"/{slug(m['st'])}/{slug(m['city'])}/"
def fac(f):
    tags=" ".join(f'<a href="/{s}/">{e(n)}</a>' for s,n,_ in mats(f))
    return f"""<div class="card"><h3>{e(f['name'])}</h3><div>{e(f['address'])}</div>
<p><b>Accepts:</b> {e(f['accepts'])}<br><b>Hours:</b> {e(f['hours'])}{'<br><b>Fees:</b> '+e(f['fees']) if f['fees'] else ''}{'<br><b>Notes:</b> '+e(f['notes']) if f['notes'] else ''}</p>
{'<p class="tags">'+tags+'</p>' if tags else ''}<div class="meta">Source: <a href="{e(f['source'])}" rel="nofollow noopener">{e(f['source'])}</a> · Last checked {f['checked']}</div></div>"""
def ldj(f):
    place={"@type":"Place","name":f["name"],"address":{"@type":"PostalAddress","streetAddress":f["address"]},"description":"Accepts: "+f["accepts"],"url":f["source"]}
    # Emit Event schema when hours clearly describe a dated drop-off event
    hm=re.search(r"Event:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+(Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct)\s+(\d{1,2}),\s*(20\d{2})", f.get("hours",""))
    if hm:
        mon={"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}[hm.group(1)]
        day=int(hm.group(2)); year=hm.group(3)
        return {"@type":"Event","name":f["name"],"startDate":f"{year}-{mon}-{day:02d}","eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","eventStatus":"https://schema.org/EventScheduled","location":place,"description":"Accepts: "+f["accepts"],"url":f["source"],"organizer":{"@type":"Organization","name":"Official source","url":f["source"]}}
    return place
def plural(n,w): return f"{n} {w}{'' if n==1 else 's'}"
matidx={s:[] for s,_,_ in MAT}
for m in D:
    for f in m["facilities"]:
        for s,_,_ in mats(f):
            if m not in matidx[s]: matidx[s].append(m)
for (sn,st),ms in sorted(states.items()):
    sp=f"/{slug(st)}/"
    for m in ms:
        cp=cpath(m); fs=m["facilities"]
        chk=max([f["checked"] for f in fs],default=None)
        note=f'<p class="note">{e(m["note"])}</p>' if m["note"] else ""
        vis,bl=crumbs([("Home","/"),(sn,sp),(m["city"],cp)])
        have=[(s,n) for s,n,_ in MAT if m in matidx[s]]
        nearby=[o for o in ms if o is not m]
        body=(vis+f'<h1>Where to dump hazardous waste, paint &amp; e-waste in {e(m["city"])}, {st}</h1>'+note
              +"".join(fac(f) for f in fs)+("<p>No permanent drop-off site listed yet. See the note above for event-based or alternate official options, and check back after the next source review.</p>" if not fs else "")
              +(f'<h2>By material</h2><p class="tags">'+" ".join(f'<a href="/{s}/">{e(n)} drop-off</a>' for s,n in have)+"</p>" if have else "")
              +f'<p class="meta">Run a local site? <a href="/embed/">Embed this list for free</a>.</p>'+(f'<h2>Other cities in {e(sn)}</h2><ul>'+"".join(f'<li><a href="{cpath(o)}">{e(o["city"])}</a></li>' for o in nearby)+"</ul>" if nearby else ""))
        short={"Electronics (e-waste)":"e-waste","Household chemicals":"chemicals"}
        tl=[short.get(n,n).lower() for _,n in have if n!="Household chemicals"][:3]
        title=f"Where to dump {', '.join(tl[:-1])+' & '+tl[-1] if len(tl)>1 else (tl[0] if tl else 'hazardous waste')} in {m['city']}, {st} | TossMap"
        what=", ".join(n.split(" (")[0].lower() for _,n in have[:4]) or "household hazardous waste"
        desc=(f"{plural(len(fs),'official drop-off site')} in {m['city']}, {st} for {what}: addresses, hours, fees and source links, last checked {chk}." if fs
              else f"How {m['city']}, {st} handles household hazardous waste, from official sources.")
        page(cp,title,desc,body,[bl]+[ldj(f) for f in fs],chk)
    vis,bl=crumbs([("Home","/"),(sn,sp)])
    page(sp,f"Hazardous waste, paint & e-waste drop-off in {sn} | TossMap",f"Official household hazardous waste, paint, e-waste and tire drop-off sites in {sn}, by city.",
         vis+f'<h1>Hazardous waste drop-off in {e(sn)}</h1><ul>'+"".join(f'<li><a href="{cpath(m)}">{e(m["city"])}</a> ({plural(len(m["facilities"]),"site")})</li>' for m in ms)+"</ul>",[bl])
for s,n,_ in MAT:
    ms=sorted(matidx[s],key=lambda x:x["city"]); low=n.split(" (")[0].lower()
    vis,bl=crumbs([("Home","/"),(n,f"/{s}/")])
    body=vis+f"<h1>Where to drop off {e(low)} near you</h1><p>These {plural(len(ms),'metro area')} have at least one official drop-off site that lists {e(low)} as accepted. Rules, limits and residency requirements vary, so check each listing's source link.</p><ul class=grid>"+"".join(f'<li><a href="{cpath(m)}">{e(m["city"])}, {m["st"]}</a></li>' for m in ms)+"</ul><p>Other materials: "+" · ".join(f'<a href="/{o}/">{e(on)}</a>' for o,on,_ in MAT if o!=s)+"</p>"
    page(f"/{s}/",f"Where to recycle or dispose of {low}: drop-off sites by city | TossMap",f"Official {low} drop-off locations in {len(ms)} US metro areas, with hours, limits and source links.",body,[bl])
n=sum(len(m["facilities"]) for m in D)
home=(f"<h1>Where do I take paint, chemicals, batteries, electronics &amp; tires?</h1><p>{n} drop-off sites from official government and operator sources across {len(D)} US metros. Every listing links to its source and shows when we last checked it.</p>"
 "<h2>By material</h2><p class=tags>"+" ".join(f'<a href="/{s}/">{e(nm)}</a>' for s,nm,_ in MAT)+"</p>"
 "<h2>By city</h2><ul class=grid>"+"".join(f'<li><a href="{cpath(m)}">{e(m["city"])}, {m["st"]}</a></li>' for m in sorted(D,key=lambda x:x["city"]))+"</ul><h2>By state</h2><ul class=grid>"+"".join(f'<li><a href="/{slug(st)}/">{e(sn)}</a></li>' for sn,st in sorted(states))+"</ul>")
page("/","TossMap: where to dump paint, hazardous waste, e-waste & tires by city","Find official drop-off sites for paint, chemicals, batteries, electronics and tires in 50+ US metros—addresses, hours, fees and source links, checked regularly.",home,
     [{"@type":"WebSite","name":"TossMap","url":BASE+"/"},{"@type":"Organization","name":"TossMap","url":BASE+"/"}])
page("/privacy.html","Privacy | TossMap","TossMap privacy policy: no cookies, no personal data.","<h1>Privacy</h1><p>We collect no personal data and set no cookies. We use GoatCounter, a privacy-friendly analytics service that does not track individuals. If ads are added, ad partners may use cookies; this page will be updated before that happens.</p><p>Listings come from public government sources and may change; confirm with the source before visiting.</p>")
open(f"{OUT}/404.html","w").write(open(f"{OUT}/index.html").read().replace("<h1>","<h1>Page not found.</h1><h2>",1).replace("</h1><p>","</h2><p>",1).replace(f'<link rel="canonical" href="{BASE}/">','<meta name="robots" content="noindex">'))
# EMBED: compact, noindex widget per city for other sites (free iframe snippet)
EMB_CSS="body{margin:0;font:14px/1.45 system-ui,sans-serif;color:#1d2a24;background:#fff}.w{padding:12px}.w h2{font-size:16px;margin:0 0 8px}.f{border-top:1px solid #e3e8e4;padding:8px 0}.f b{display:block}.m{font-size:12px;color:#5b6b63}a{color:#1f6b4d}.by{font-size:12px;margin-top:8px}"
def snippet(m): return f'<iframe src="{BASE}/embed{cpath(m)}" title="Hazardous waste drop-off sites in {e(m["city"])} (TossMap)" width="100%" height="460" style="border:1px solid #dfe5e0;border-radius:8px" loading="lazy"></iframe>'
for m in D:
    p=f"{OUT}/embed{cpath(m)}index.html"; os.makedirs(os.path.dirname(p),exist_ok=True)
    fs="".join(f'<div class="f"><b>{e(f["name"])}</b>{e(f["address"])}<br>Accepts: {e(f["accepts"])}<br>Hours: {e(f["hours"])}<div class="m"><a href="{e(f["source"])}" target="_blank" rel="nofollow noopener">Official source</a> · checked {f["checked"]}</div></div>' for f in m["facilities"]) or f'<p>{e(m["note"]) or "No permanent drop-off site found in official sources."}</p>'
    open(p,"w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="canonical" href="{BASE}{cpath(m)}"><title>Drop-off sites in {e(m["city"])} | TossMap</title><style>{EMB_CSS}</style>{GC}</head><body><div class="w"><h2>Where to drop off hazardous waste in {e(m["city"])}, {m["st"]}</h2>{fs}<div class="by">Full list and updates at <a href="{BASE}{cpath(m)}" target="_blank">TossMap</a></div></div></body></html>')
ex=sorted(D,key=lambda x:-len(x["facilities"]))[0]
emb_body=(crumbs([("Home","/"),("Embed","/embed/")])[0]+"<h1>Free drop-off map widget for your website</h1><p>City pages, libraries, neighborhood groups and local news sites can embed TossMap's list of official drop-off sites for any metro. It's free, needs no account, sets no cookies, and updates whenever we re-check the listings.</p>"
 f"<h2>How to add it</h2><p>Copy this snippet into your page and change the city path if you like:</p><pre style='white-space:pre-wrap;background:#fff;border:1px solid #dfe5e0;padding:10px'>{e(snippet(ex))}</pre>"
 f"<h2>Preview ({e(ex['city'])})</h2>{snippet(ex)}<h2>Snippet for every city</h2><ul class=grid>"+"".join(f'<li><a href="/embed{cpath(m)}">{e(m["city"])}, {m["st"]}</a></li>' for m in sorted(D,key=lambda x:x["city"]))+"</ul>")
page("/embed/","Free hazardous waste drop-off widget for your website | TossMap","Embed a free, cookie-free list of official paint, chemical, e-waste and tire drop-off sites for your city on any website.",emb_body,[crumbs([("Home","/"),("Embed","/embed/")])[1]])

SUPPORT="toolshed@mail.grokbot.com"
city_vis,city_bl=crumbs([("Home","/"),("For cities","/for-cities/")])
city_body=(city_vis+"<h1>TossMap for cities and waste districts</h1>"
 "<p>Give residents one accurate place to find tire, paint, e-waste, and household-chemical drop-offs—without building another directory. Official listings stay free and sourced. Support: <a href=\"mailto:"+SUPPORT+"\">"+SUPPORT+"</a>.</p>"
 "<div class=card><h3>What you get</h3><ul>"
 "<li><b>Branded city embed</b> — your city name (seal optional), hosted and updated when official sources change.</li>"
 "<li><b>Verified listings only</b> — every site has a source link and a last-checked date.</li>"
 "<li><b>Event callouts</b> — upcoming HHW or free-landfill days when your city publishes them.</li>"
 "<li><b>Simple analytics</b> — quarterly note on embed traffic (cookie-free on our side).</li></ul></div>"
 "<div class=card><h3>Suggested annual pricing</h3><ul>"
 "<li><b>Starter</b> — city embed + listing updates: $500–$1,200</li>"
 "<li><b>Standard</b> — Starter + event callouts + quarterly traffic note: $1,500–$3,000</li>"
 "<li><b>District</b> — multi-city / county coverage: custom</li></ul>"
 "<p>Pilot: 90 days free for one city page if you publish the embed on an official .gov page and share one sentence of feedback.</p></div>"
 "<div class=card><h3>Next step</h3><p>Email <a href=\"mailto:"+SUPPORT+"\">"+SUPPORT+"</a> with your city and preferred package. We send a one-line embed snippet and a short terms sheet. Free embed docs: <a href=\"/embed/\">/embed/</a>.</p></div>")
page("/for-cities/","TossMap for cities | branded drop-off embed","Offer for municipalities: embed TossMap’s verified hazardous-waste drop-off list on your .gov site.",city_body,[city_bl])
partner_vis,partner_bl=crumbs([("Home","/"),("Partners","/partners/")])
partner_body=(partner_vis+"<h1>TossMap partner placements</h1>"
 "<p>For tire shops, e-waste recyclers, and paint / HHW handlers. Partner spots are clearly labeled and never replace official city listings. Support: <a href=\"mailto:"+SUPPORT+"\">"+SUPPORT+"</a>.</p>"
 "<div class=card><h3>What you get</h3><ul>"
 "<li><b>Labeled partner card</b> — name, address, materials, hours, and link, marked Partner.</li>"
 "<li><b>City + material pages</b> — your metro page and matching material hubs where relevant.</li>"
 "<li><b>Source &amp; check date</b> — we verify acceptance rules; stale partners come down.</li>"
 "<li><b>Optional pickup leads</b> — haul-away inquiries routed to you (separate per-lead fee).</li></ul></div>"
 "<div class=card><h3>Suggested pricing</h3><ul>"
 "<li><b>City partner</b> — one metro, one materials set: $99–$249 / month</li>"
 "<li><b>Metro + materials</b> — city page plus 1–2 material hubs: $199–$399 / month</li>"
 "<li><b>Pickup leads</b> — qualified inquiry: $15–$40 / lead</li></ul>"
 "<p>First month free with proof of materials accepted and a website or photo we can cite. Cancel anytime; we remove the card within a week.</p></div>"
 "<div class=card><h3>Trust rules</h3><ul>"
 "<li>Official government and operator listings stay free and are not buried.</li>"
 "<li>No fake reviews and no “#1 dump site” claims.</li>"
 "<li>Tell us when acceptance rules change.</li></ul></div>"
 "<div class=card><h3>Next step</h3><p>Email <a href=\"mailto:"+SUPPORT+"\">"+SUPPORT+"</a> with your city, materials, website, and preferred package. We send a draft partner card for approval before it goes live.</p></div>")
page("/partners/","TossMap partners | tire & e-waste placements","Labeled partner placements on TossMap for tire shops and e-waste recyclers. Official listings stay free.",partner_body,[partner_bl])

open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>" for u,d in urls)+"</urlset>\n")
print(len(urls),"pages;",len(states),"states;",n,"facilities")
open(f"{OUT}/CNAME","w").write("tossmap.com\n"); open(f"{OUT}/.nojekyll","w").write("")
