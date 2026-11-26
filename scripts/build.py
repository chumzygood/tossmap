import json,html,re,os,datetime,shutil
from urllib.parse import quote, urlparse
BASE="https://tossmap.com"
D=json.load(open("data/facilities.json")); OUT="docs"
# Facility page paths (used so city FAQ answers link straight to each facility page).
for _m in D:
    for _f in _m["facilities"]:
        _f["_fp"]="/"+_m["st"].lower()+"/"+__import__("re").sub(r"[^a-z0-9]+","-",_m["city"].lower()).strip("-")+"/"+_f["slug"]+"/"
TODAY=datetime.date.today().isoformat()
# Sitemap lastmod for pages without dated listings: bump only when their content actually changes.
STATIC_LASTMOD="2026-11-10"
os.makedirs(OUT,exist_ok=True)  # Never remove existing published pages during a build.
from facility_questions import QUESTIONS, UNKNOWN
e=html.escape
slug=lambda s:re.sub(r"[^a-z0-9]+","-",s.lower()).strip("-")
CSS="""*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,sans-serif;color:#1d2a24;background:#f7f8f6}
header,footer{background:#1f4d3a;color:#fff;padding:14px 20px}header a,footer a{color:#fff}main{max-width:900px;margin:0 auto;padding:20px}
a{color:#1f6b4d}.card{background:#fff;border:1px solid #dfe5e0;border-radius:8px;padding:16px;margin:14px 0}
.card h3{margin:0 0 6px}.meta{font-size:13px;color:#5b6b63}.crumbs{font-size:14px}
ul.grid{columns:3 200px;padding-left:18px}.note{background:#fff7e0;border-left:4px solid #e0b030;padding:10px 14px}.lead{margin:0 0 14px}.tags a{display:inline-block;margin:0 8px 6px 0}
.signup{background:#fff;border:1px solid #dfe5e0;border-radius:8px;padding:16px;margin:14px 0}
.signup h2{margin:0 0 6px;font-size:1.15em}.signup p{margin:0 0 10px}
.signup-form{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-end;margin:10px 0}
.signup-form label{flex:1 1 100%;font-size:14px}
.signup-form input[type=email]{flex:1 1 220px;font:inherit;padding:8px 10px;border:1px solid #c5d0ca;border-radius:6px}
.signup-form button{font:inherit;padding:8px 14px;border:0;border-radius:6px;background:#1f4d3a;color:#fff;cursor:pointer}
.signup .meta{margin:0}
.questions{width:100%;border-collapse:collapse;background:#fff}.questions th,.questions td{padding:12px;border:1px solid #dfe5e0;text-align:left;vertical-align:top;overflow-wrap:anywhere}.questions th{width:30%}dd{margin:0 0 12px}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #ad5700;outline-offset:3px}@media(max-width:600px){.questions,.questions tbody,.questions tr,.questions th,.questions td{display:block;width:100%}.questions thead{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}.questions th{padding-bottom:4px;border-bottom:0}.questions td{padding-top:4px;border-top:0;margin-bottom:8px}} .answers h2{font-size:1.15em;margin:1.15em 0 6px}.answers p{margin:0 0 12px}a,.meta,p,li,dd,h1,h2,h3,.card,.answers{overflow-wrap:anywhere}a,.meta{word-break:break-word}img,iframe,video,pre,table{max-width:100%}pre{white-space:pre-wrap;overflow-x:auto}.facts{padding-left:18px}.facts li{margin:0 0 8px}.freshness{margin:0 0 14px}"""
open(f"{OUT}/style.css","w").write(CSS)
GC='<meta name="google-site-verification" content="jAhRn0yYvjC37jRpBEzda-xllydn360g3kgkVonTDKA" /><script data-goatcounter="https://tossmap.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
ICONS='<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">'
KIT_ACTION="https://app.kit.com/forms/10171028/subscriptions"
KIT_HOSTED="https://tossmap.kit.com/f14ed9078b"
def signup_form():
    return (f'<form class="signup-form" action="{KIT_ACTION}" method="post">'
            '<label for="newsletter-email">Email address</label>'
            '<input type="email" id="newsletter-email" name="email_address" required autocomplete="email" placeholder="you@example.com">'
            '<button type="submit">Sign me up</button></form>')
def signup_box():
    return ('<div class="signup" id="newsletter"><h2>Get local drop-off updates</h2>'
            '<p>Hazardous-waste days, new locations and a short weekly tip. Free, and you can unsubscribe anytime.</p>'
            +signup_form()+
            '<p class="meta">You will get a confirmation email first. We do not sell your email. <a href="/newsletter/">About the newsletter</a></p></div>')
# Material pages: keyword patterns matched against each listing's "accepts" text
MAT=[("paint","Paint","paint"),("e-waste","Electronics (e-waste)",r"e-waste|electronic|computer|tv|cell phone|monitor"),
     ("tires","Tires",r"\btires?\b"),("batteries","Batteries",r"batter"),("motor-oil","Motor oil",r"motor oil|automotive fluid|car fluid|used oil"),
     ("household-chemicals","Household chemicals",r"chemical|pesticide|solvent|cleaner")]
def mats(f):
    t=f["accepts"].lower()
    neg=re.findall(r"\((?:[^)]*?)(?:no|not)\s[^)]*\)|no [a-z ,]+",t)
    tt=re.sub(r"not accepted:[^.;]*","",t)
    for n in neg: tt=tt.replace(n,"")
    if "questions" in f:
        keys={"e-waste":"e_waste","motor-oil":"motor_oil","household-chemicals":"household_chemicals"}
        return [m for m in MAT if f["questions"][keys.get(m[0],m[0])]["answer"]=="yes"]
    return [m for m in MAT if re.search(m[2],tt)]
urls=[]
def ldscript(o): return '<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False).replace("<", "\\u003c")+"</script>"
def crumbs(items):
    vis='<p class="crumbs">'+" › ".join(f'<a href="{u}">{e(n)}</a>' for n,u in items)+"</p>"
    ld={"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":BASE+u} for i,(n,u) in enumerate(items)]}
    return vis,ld
# Hand-written titles/metas for pages that get Search Console impressions (Nov 24 review). Every claim is checked against the listing data;
# keep titles near 60 chars and metas near 155. Pages not listed here use the generated templates.
SEO_OVERRIDE={
 "/or/portland/":("Portland, OR battery, paint & hazardous waste disposal | TossMap",
   "Battery, paint and household hazardous waste disposal in Portland, OR: Metro Central (NW 61st Ave) and Metro South (Oregon City). Hours, limits, fees, sources."),
 "/tx/dallas/":("Dallas tire, e-waste, paint & battery drop-off sites | TossMap",
   "Dallas, TX drop-offs: tires and electronics at McCommas Bluff and 3 transfer stations; paint and batteries at the Dallas County Home Chemical Center."),
 "/ca/san-francisco/":("San Francisco paint, battery & HHW disposal (Recology) | TossMap",
   "Recology SF Household Hazardous Waste Facility, 501 Tunnel Ave: paint, batteries, motor oil and chemicals, Thu–Sat 8am–4pm. SF residents only; ID required."),
 "/ne/omaha/":("Under the Sink Omaha: hazardous waste & paint drop-off | TossMap",
   "Omaha's household hazardous waste drop-off is Under the Sink, 4001 S 120th St: paint, batteries, motor oil and chemicals for Douglas and Sarpy County homes."),
 "/ne/omaha/under-the-sink/":("Under The Sink Omaha: hours, accepted items & fees | TossMap",
   "Under The Sink, 4001 S 120th St, Omaha: household chemical drop-off for Douglas & Sarpy County homes. Paint, batteries, motor oil; Wed–Fri, Sat by appointment."),
 "/oh/cincinnati/cincinnati-recycling-reuse-hub/":("Cincinnati Recycling & Reuse Hub: e-waste & tires | TossMap",
   "Cincinnati Recycling & Reuse Hub, 911 Evans St: drop off electronics, TVs, car and bike tires, batteries and bulbs. Tue, Thu and Sat hours, item fees, closures."),
 "/tx/fort-worth/environmental-collection-center/":("Fort Worth Environmental Collection Center hours | TossMap",
   "Fort Worth Environmental Collection Center, 6400 Bridge St: paint, batteries, auto fluids, cleaners and pool chemicals. Thu–Fri 11am–7pm, Sat 9am–3pm."),
 "/ca/los-angeles/ucla-s-a-f-e-collection-center/":("UCLA S.A.F.E. Center: free HHW & e-waste drop-off, LA | TossMap",
   "UCLA S.A.F.E. Collection Center, 550 Charles E Young Dr: free drop-off for paint, motor oil, e-waste, batteries and sharps. Fri, Sat, first Sun 9am–3pm."),
 "/nc/raleigh/south-wake-multi-material-recycling-facility/":("South Wake Recycling Facility, Apex: e-waste & oil | TossMap",
   "South Wake Multi-Material Recycling Facility, 6130 Old Smithfield Rd, Apex, NC: electronics, large appliances, motor oil and antifreeze. Mon–Sat 8am–4pm."),
 "/ca/sacramento/":("Sacramento tire, e-waste & hazardous waste drop-offs | TossMap",
   "Sacramento-area drop-offs: free resident tires (4/day) and e-waste at Kiefer Landfill; paint, batteries and chemicals at NARS, Fruitridge Rd and Elk Grove."),
 "/ca/san-jose/santa-clara-county-hhw-san-jose/":("Santa Clara County HHW San Jose: appointments & items | TossMap",
   "Santa Clara County HHW drop-off, 1608 Las Plumas Ave, San Jose: free, by appointment Thu–Sat with proof of residency. Paint, batteries, chemicals, auto fluids."),
}
# City pages whose main facility has a well-known name people search for: H1 and first FAQ name it (data comes from that listing).
CITY_NAMED={("NE","Omaha"):"Under The Sink"}
def fix_mailto(path):
    return "mailto:toolshed@mail.grokbot.com?subject="+quote(f"TossMap fix: {path}", safe="")
def page(path,title,desc,body,graph=(),checked=None):
    title,desc=SEO_OVERRIDE.get(path,(title,desc))
    urls.append((path,checked or STATIC_LASTMOD)); p=f"{OUT}{path}"+("index.html" if path.endswith("/") else "")
    os.makedirs(os.path.dirname(p),exist_ok=True)
    ld=ldscript({"@context":"https://schema.org","@graph":list(graph)}) if graph else ""
    foot=f"Data from official government and operator sources{', checked '+checked if checked else ''}. Always confirm with the source before driving."
    open(p,"w").write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:type" content="website"><meta property="og:site_name" content="TossMap"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}">
{ICONS}<link rel="stylesheet" href="/style.css">{ld}
{GC}</head><body><header><a href="/"><strong>TossMap</strong></a> · where to toss hazardous waste, paint, e-waste &amp; tires · <a href="/newsletter/">Newsletter</a></header><main>{body}</main>
<footer>{foot} · <a href="/newsletter/">Newsletter</a> · <a href="/privacy.html">Privacy</a> · <a href="/embed/">Embed widget</a> · <a href="/for-cities/">For cities</a> · <a href="/partners/">Partners</a> · <a href="{fix_mailto(path)}">Suggest a fix or leave a review</a> · <a href="mailto:toolshed@mail.grokbot.com">Support</a></footer></body></html>""")
states={}
for m in D: states.setdefault((m["state"],m["st"]),[]).append(m)
cpath=lambda m:f"/{slug(m['st'])}/{slug(m['city'])}/"
fpath=lambda f,m:cpath(m)+f["slug"]+"/"

MAT_H1={"household-chemicals":"hazardous waste","tires":"tires","e-waste":"e-waste","paint":"paint","motor-oil":"motor oil","batteries":"batteries"}  # city H1 priority order
MAT_SHORT={"e-waste":"electronics","household-chemicals":"household chemicals","motor-oil":"motor oil","paint":"paint","tires":"tires","batteries":"batteries"}
ORG_ID=BASE+"/#organization"
DAY_ABBR=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
DAY_SCHEMA={"Mon":"Monday","Tue":"Tuesday","Wed":"Wednesday","Thu":"Thursday","Fri":"Friday","Sat":"Saturday","Sun":"Sunday"}
GENERIC_BIZ=("Can businesses use these drop-off sites?","Do not assume so. Many household hazardous-waste programs restrict drop-offs to residents and exclude commercial waste. Read the eligibility notes for the individual facility, then confirm with the linked government or operator source. A place listed near your business may still require a commercial disposal service or a separate appointment.")
GENERIC_HOURS=("Are the hours and fees guaranteed?","No. TossMap shows source links and last-checked dates so you can see where a listing came from and when it was reviewed. Hours, fees and accepted materials can change after that check. Confirm with the linked facility or government page before loading your vehicle and making the trip.")
GENERIC_PAINT=("Where can I drop off old paint?","Start with your city's paint listings and read the linked operator's rules. Accepted paint types, container limits, residency requirements and fees vary by location. Confirm the current hours and whether an appointment is needed before driving. Do not assume a site that takes oil-based paint also takes latex paint.")

def is_event(f):
    h=f.get("hours") or ""
    if re.search(r"Event:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+(Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct)\s+(\d{1,2}),\s*(20\d{2})", h):
        return True
    return bool(re.match(r"Collection days:", h, re.I))

# A one-day event whose own date is before today's build date has passed: no Event markup, and pages say so plainly.
_EVMON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def event_day(f):
    mm=re.search(r"Event:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s*(20\d{2})", f.get("hours") or "")
    return f"{int(mm.group(3)):04d}-{_EVMON.index(mm.group(1))+1:02d}-{int(mm.group(2)):02d}" if mm else None
def is_past_event(f):
    d=event_day(f)
    return bool(d and d<TODAY)
def past_event_note(f):
    if not is_past_event(f): return ""
    d=datetime.date.fromisoformat(event_day(f)).strftime("%B %-d, %Y")
    return f"This collection event ({d}) has already taken place. It is kept here for reference; check the official source for the next date before you go."

def parse_address(addr):
    core=addr.strip(); parent=None
    pm=re.match(r"^(.*?)(\s*\([^)]+\))\s*$", core)
    if pm and re.search(r"[A-Z]{2}(?:\s+\d{5})?\s*$", pm.group(1)):
        core=pm.group(1).strip(); parent=pm.group(2).strip()
    m=re.match(r"^(?P<street>.+),\s*(?P<locality>[^,]+),\s*(?P<region>[A-Z]{2})(?:\s+(?P<postal>\d{5}(?:-\d{4})?))?$", core)
    if m:
        street=m.group("street").strip()
        if parent: street=f"{street} {parent}"
        pa={"@type":"PostalAddress","streetAddress":street,"addressLocality":m.group("locality").strip(),"addressRegion":m.group("region"),"addressCountry":"US"}
        if m.group("postal"): pa["postalCode"]=m.group("postal")
        return pa
    pa={"@type":"PostalAddress","streetAddress":addr,"addressCountry":"US"}
    m2=re.search(r",\s*([A-Z]{2})(?:\s+(\d{5}(?:-\d{4})?))?\s*$", core)
    if m2:
        pa["addressRegion"]=m2.group(1)
        if m2.group(2): pa["postalCode"]=m2.group(2)
    return pa

def parse_time(tok, inherit=None):
    t=tok.strip().lower().replace(" ","")
    if t in ("noon","12pm"): return "12:00"
    if t in ("midnight","12am"): return "00:00"
    m=re.match(r"^(\d{1,2})(?::(\d{2}))?(am|pm)?$", t)
    if not m: return None
    ap=m.group(3) or inherit
    if not ap: return None
    hh=int(m.group(1)); mm=int(m.group(2) or 0)
    if hh==12: hh=0 if ap=="am" else 12
    elif ap=="pm": hh+=12
    if not (0<=hh<=23 and 0<=mm<=59): return None
    return f"{hh:02d}:{mm:02d}"

def parse_days(tok):
    tok=tok.strip().replace("–","-").replace("—","-")
    low=tok.lower()
    if low=="daily": return list(DAY_ABBR)
    week={
        "monday":"Mon","mondays":"Mon","tuesday":"Tue","tuesdays":"Tue","wednesday":"Wed","wednesdays":"Wed",
        "thursday":"Thu","thursdays":"Thu","friday":"Fri","fridays":"Fri","saturday":"Sat","saturdays":"Sat",
        "sunday":"Sun","sundays":"Sun"
    }
    if tok in DAY_ABBR: return [tok]
    if low in week: return [week[low]]
    m=re.match(r"^([A-Z][a-z]{2})-([A-Z][a-z]{2})$", tok)
    if m and m.group(1) in DAY_ABBR and m.group(2) in DAY_ABBR:
        a,b=DAY_ABBR.index(m.group(1)), DAY_ABBR.index(m.group(2))
        if a<=b: return DAY_ABBR[a:b+1]
        return DAY_ABBR[a:]+DAY_ABBR[:b+1]
    parts=[p.strip() for p in tok.split(",")]
    if parts and all(p in DAY_ABBR for p in parts):
        return parts
    return None

def opening_hours_spec(hours):
    if not hours or is_event({"hours":hours}):
        return None
    h=hours.strip()
    if re.search(r"\b(1st|2nd|3rd|4th|first|second|third|fourth|appointment|scheduled|select|seasonal|next:|hours not published)\b", h, re.I):
        return None
    h=re.sub(r"\s*\([^)]*closed[^)]*\)","",h,flags=re.I)
    h=re.sub(r";\s*closed\b.*$","",h,flags=re.I)
    h=h.strip().rstrip(";").strip()
    if not h: return None
    specs=[]
    for seg in re.split(r";\s*", h):
        seg=seg.strip()
        if not seg: continue
        m=re.match(r"^(.+?)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?|noon)\s*[–-]\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)|noon)$", seg, re.I)
        if not m: return None
        days=parse_days(m.group(1))
        close_ap=re.search(r"(am|pm)$", m.group(3).strip().lower().replace(" ",""))
        inherit=close_ap.group(1) if close_ap else None
        op,cl=parse_time(m.group(2), inherit), parse_time(m.group(3))
        if not days or not op or not cl: return None
        for d in days:
            specs.append({"@type":"OpeningHoursSpecification","dayOfWeek":"https://schema.org/"+DAY_SCHEMA[d],"opens":op,"closes":cl})
    return specs or None

def drop_empty(o):
    if isinstance(o, dict):
        return {k:drop_empty(v) for k,v in o.items() if v is not None and v!="" and v!=[] and v!={}}
    if isinstance(o, list):
        return [drop_empty(x) for x in o]
    return o

def appointment_status(f):
    hours=(f.get("hours") or ""); notes=(f.get("notes") or ""); t=(hours+" "+notes).lower()
    if re.search(r"\bno appointment\b", t) and not re.search(r"\bby appointment\b|\bappointment required\b|\bappointment only\b|\bappointment \+", t):
        return "no"
    if re.search(r"\bappointment required\b|\bappointment only\b|\bappointment \+", t):
        return "yes"
    if re.match(r"by appointment\b", hours.strip(), re.I):
        return "yes"
    if re.search(r",\s*by appointment\s*$", hours, re.I):
        return "yes"
    if re.search(r"\bby appointment\b", t):
        return "sometimes"
    return "no"

def checked_phrase(fs):
    dates=sorted({f["checked"] for f in fs if f.get("checked")})
    if not dates: return ""
    if dates[0]==dates[-1]: return f"Last checked {dates[0]}."
    return f"Last checked {dates[0]} to {dates[-1]}."

def field_or_check(val):
    v=(val or "").strip()
    return v if v else "check source"

def format_updated(iso):
    return datetime.date.fromisoformat(iso).strftime("%B %-d, %Y")

def checked_month_label(fs):
    dates=sorted({f["checked"] for f in fs if f.get("checked")})
    if not dates: return ""
    months=sorted({datetime.date.fromisoformat(d).strftime("%b %Y") for d in dates})
    if len(months)==1:
        return f"Checked {months[0]}"
    a=datetime.date.fromisoformat(dates[0]); b=datetime.date.fromisoformat(dates[-1])
    if a.year==b.year:
        return f"Checked {a.strftime('%b %-d')}–{b.strftime('%b %-d, %Y')}"
    return f"Checked {a.strftime('%b %-d, %Y')}–{b.strftime('%b %-d, %Y')}"

def freshness_plain(fs):
    dates=[f["checked"] for f in fs if f.get("checked")]
    if not dates: return ""
    text=f"Updated {format_updated(max(dates))}."
    label=checked_month_label(fs)
    if label: text+=f" {label}."
    text+=" Confirm with the official source before you go."
    return text

def freshness_html(fs):
    text=freshness_plain(fs)
    return f'<p class="meta freshness">{e(text)}</p>' if text else ""

def unique_sources(fs):
    seen=[]
    for f in fs:
        u=f.get("source")
        if u and u not in seen: seen.append(u)
    return seen

def source_html(fs):
    seen=unique_sources(fs)
    if not seen: return ""
    label="Source" if len(seen)==1 else "Sources"
    return label+": "+"; ".join(f'<a href="{e(u)}" rel="nofollow noopener">{e(u)}</a>' for u in seen)+"."

def source_plain(fs):
    seen=unique_sources(fs)
    if not seen: return ""
    label="Source" if len(seen)==1 else "Sources"
    return label+": "+"; ".join(seen)+"."

def group_facilities(fs):
    groups=[]
    for f in fs:
        key=(f["accepts"],f["hours"],f.get("notes") or "",f.get("fees") or "",f["source"])
        for g in groups:
            if g["key"]==key:
                g["items"].append(f); break
        else:
            groups.append({"key":key,"items":[f]})
    return groups

def names_phrase(fs, html=False):
    names=[f["name"] for f in fs]
    if len(fs)>1:
        for sep in (" – ", " — ", " - "):
            if all(sep in n for n in names):
                prefs=[n.rsplit(sep,1)[0] for n in names]
                sufs=[n.rsplit(sep,1)[1] for n in names]
                if len(set(prefs))==1:
                    if html:
                        bits=[f'<a href="{f.get("_fp") or "#"+slug(f["name"])}">{e(s)}</a>' for f,s in zip(fs,sufs)]
                    else:
                        bits=list(sufs)
                    mid=f"{bits[0]} and {bits[1]}" if len(bits)==2 else (", ".join(bits[:-1])+", and "+bits[-1])
                    pref=e(prefs[0]) if html else prefs[0]
                    return f"{len(fs)} {pref} sites ({mid})"
    if html:
        bits=[f'<a href="{f.get("_fp") or "#"+slug(f["name"])}">{e(f["name"])}</a>' for f in fs]
    else:
        bits=list(names)
    if len(bits)==1: return bits[0]
    if len(bits)==2: return f"{bits[0]} and {bits[1]}"
    return ", ".join(bits[:-1])+", and "+bits[-1]

def join_sents(*parts):
    text=" ".join(p.strip() for p in parts if p and p.strip())
    text=re.sub(r"\s+\.", ".", text)
    text=re.sub(r"\.{2,}", ".", text)
    text=re.sub(r" \s+", " ", text)
    return text.strip()

def city_overview_qa(m):
    city,st,fs=m["city"],m["st"],m["facilities"]
    note=(m.get("note") or "").strip()
    q=f"Where can I drop off hazardous waste in {city}?"
    named=next((f for f in fs if f["name"]==CITY_NAMED.get((st,city))),None)
    if named: q=f"Where can I drop off hazardous waste in {city} (Under the Sink)?" if named["name"]=="Under The Sink" else f"Where can I drop off hazardous waste in {city} ({named['name']})?"
    if not fs:
        parts=[f"TossMap does not list a permanent drop-off site in {city}, {st}."]
        if note: parts.append(note)
        parts.append("Confirm any current options on the official source before you go.")
        plain=join_sents(*parts)
        return q, e(plain), plain
    events=[f for f in fs if is_event(f)]
    standing=[f for f in fs if not is_event(f)]
    have=[n.split(" (")[0].lower() for s,n,_ in MAT if any(x[0]==s for f in fs for x in mats(f))]
    if len(have)>1: mat_list=", ".join(have[:-1])+" and "+have[-1]
    elif have: mat_list=have[0]
    else: mat_list="the materials named in the listings"
    parts=[]
    if named: parts.append(f'{city}\'s household hazardous waste drop-off is {named["name"]} at {named["address"]}. Hours recorded: {named["hours"]}.')
    if standing and not events:
        n=len(standing)
        parts.append(f"TossMap lists {n} official drop-off site{'s' if n!=1 else ''} in {city}, {st}.")
        parts.append(f"Listed materials include {mat_list}.")
    elif events and not standing:
        parts.append(f"TossMap does not list a permanent drop-off site in {city}, {st}.")
        for f in events:
            parts.append(f'The official source lists {f["name"]} at {f["address"]}. Hours recorded: {f["hours"]}.'+(" That date has passed; check the source for the next one." if is_past_event(f) else ""))
        parts.append("This is a scheduled collection event, not a year-round drop-off site.")
    else:
        parts.append(f"TossMap lists {len(standing)} official standing drop-off site{'s' if len(standing)!=1 else ''} and {len(events)} scheduled collection event{'s' if len(events)!=1 else ''} in {city}, {st}.")
        parts.append(f"Listed materials include {mat_list}.")
    if note: parts.append(note)
    notes=[(f.get("notes") or "").strip() for f in fs]
    if all(notes) and len(set(notes))==1:
        parts.append(notes[0].rstrip(".")+".")
    else:
        stts=[appointment_status(f) for f in fs]
        if stts and all(s=="yes" for s in stts):
            parts.append("Listings record that an appointment is required.")
        elif any(s in ("yes","sometimes") for s in stts):
            parts.append("Some listings require an appointment; see each listing.")
    parts.append(checked_phrase(fs))
    parts.append("Confirm current hours, eligibility and acceptance with the official source before you go.")
    plain=join_sents(*parts)
    return q, e(plain)+" "+source_html(fs), plain+" "+source_plain(fs)

def material_qa(m, s, fs, html=True):
    if not fs: return None
    city,st=m["city"],m["st"]
    low=MAT_SHORT[s]
    q=f"Where can I drop off {low} in {city}?"
    events=[f for f in fs if is_event(f)]
    standing=[f for f in fs if not is_event(f)]
    groups=group_facilities(fs)
    shared_notes=None
    note_set={(g["items"][0].get("notes") or "").strip() for g in groups}
    if len(note_set)==1: shared_notes=note_set.pop() or None
    def group_sentence(g, as_html):
        items=g["items"]; f=items[0]
        who=names_phrase(items, html=as_html)
        if len(items)==1:
            sent=f"{who} at {e(f['address']) if as_html else f['address']} is listed as accepting {low}."
        else:
            sent=f"{who} are listed as accepting {low}."
        acc=f["accepts"]
        if re.search(r"\bno |\bnot |\blimit|\d+\s*(gal|qt|lb|tires?)\b|\boil-based|\blatex", acc, re.I):
            sent+=f" The listing records acceptance as: {e(acc) if as_html else acc}."
        if is_event(f):
            hrs=e(f["hours"]) if as_html else f["hours"]
            sent+=f" Recorded hours: {hrs}. This is a scheduled event, not a permanent drop-off site."+(" That date has passed; check the source for the next one." if is_past_event(f) else "")
        stt=appointment_status(f)
        notes_already=(f.get("notes") or "")
        if stt=="yes" and "appoint" not in notes_already.lower():
            sent+=" The listing records that an appointment is required."
        if stt=="sometimes" and "appoint" not in notes_already.lower():
            sent+=" The listing records that some visits require an appointment."
        if not shared_notes and notes_already.strip():
            sent+=" "+(e(notes_already) if as_html else notes_already).rstrip(".")+"."
        return sent
    def build(as_html):
        ps=[]
        if events and not standing:
            ps.append(f"TossMap does not list a permanent drop-off for {low} in {city}, {st}.")
        for g in groups:
            ps.append(group_sentence(g, as_html))
        if shared_notes:
            ps.append((e(shared_notes) if as_html else shared_notes).rstrip(".")+".")
        ps.append(checked_phrase(fs))
        ps.append("Confirm current acceptance, hours and eligibility with the official source before you go.")
        body=join_sents(*ps)
        return body+" "+(source_html(fs) if as_html else source_plain(fs))
    return q, build(True), build(False)

def event_vs_permanent_qa(m):
    fs=m["facilities"]
    events=[f for f in fs if is_event(f)]
    standing=[f for f in fs if not is_event(f)]
    if not events: return None
    q="Household collection event or permanent drop-off?"
    if events and not standing:
        plain=join_sents(
            f"In {m['city']}, the listed option is a scheduled collection event, not a permanent drop-off site.",
            "Event dates expire, and hours or acceptance can change. Confirm the current schedule on the official source before you go.",
            checked_phrase(events))
        return q, e(plain)+" "+source_html(events), plain+" "+source_plain(events)
    def body(as_html):
        stn=names_phrase(standing, html=as_html)
        ev=names_phrase(events, html=as_html)
        site="a standing drop-off site" if len(standing)==1 else "standing drop-off sites"
        evw="a scheduled collection event" if len(events)==1 else "scheduled collection events"
        vs,ve=("is","is") if (len(standing)==1,len(events)==1)==(True,True) else (("is" if len(standing)==1 else "are"), ("is" if len(events)==1 else "are"))
        return join_sents(
            f"In {m['city']}, {stn} {vs} listed as {site}, and {ev} {ve} listed as {evw}.",
            "Do not treat an event date as year-round hours. Confirm both options on the official source before you go.",
            checked_phrase(fs),
            source_html(fs) if as_html else source_plain(fs))
    return q, body(True), body(False)

def generic_material_faq(s):
    if s=="paint": return GENERIC_PAINT
    low=MAT_SHORT[s]
    q=f"Where can I drop off {low}?"
    a=(f"Start with your city's {low} listings and read the linked operator's rules. "
       "Limits, residency requirements and fees vary by location. "
       "Confirm the current hours and whether an appointment is needed before driving.")
    return q,a

def faq_block(qas):
    if not qas: return "", None
    parts=[]
    for q,h,_ in qas:
        wrap="div" if re.search(r"<(ul|ol|table|section|div)\b", h) else "p"
        parts.append(f"<h2>{e(q)}</h2><{wrap}>{h}</{wrap}>")
    html_out='<section class="answers">'+"".join(parts)+"</section>"
    faq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":p}} for q,_,p in qas]}
    return html_out, faq

def city_hours_fees_qa(m):
    fs=m["facilities"]
    if not fs: return None
    q=f"What hours, fees and accepted items are listed in {m['city']}?"
    intro="These hours, fees and accepted items come from each listing's official source. "+freshness_plain(fs)
    def item_plain(f):
        return (f'{f["name"]}: hours {field_or_check(f.get("hours"))}; '
                f'fees {field_or_check(f.get("fees"))}; '
                f'accepts {field_or_check(f.get("accepts"))}.')
    items="".join(
        f'<li><a href="{fpath(f,m)}">{e(item_plain(f))}</a></li>'
        for f in fs)
    html=e(intro)+f'<ul class="facts">{items}</ul>'
    plain=intro+" "+" ".join(item_plain(f) for f in fs)
    return q, html, plain

def facility_place(f, m):
    place={"@type":"Place","@id":f"{BASE}{cpath(m)}#{slug(f['name'])}","name":f["name"],
           "address":parse_address(f["address"]),"description":"Accepts: "+f["accepts"],"url":BASE+fpath(f,m),"sameAs":f["source"]}
    props=[{"@type":"PropertyValue","name":"Accepted materials","value":f["accepts"]}]
    if f.get("checked"): props.append({"@type":"PropertyValue","name":"Last checked","value":f["checked"]})
    if (f.get("notes") or "").strip(): props.append({"@type":"PropertyValue","name":"Eligibility notes","value":f["notes"]})
    if f.get("fees"): props.append({"@type":"PropertyValue","name":"Fees","value":f["fees"]})
    if f.get("operator") and f["operator"]!=UNKNOWN:
        props.append({"@type":"PropertyValue","name":"Operator","value":f["operator"]})
    place["additionalProperty"]=props
    # Telephone only when the source-backed notes contain exactly one distinct US phone number (already visible on the page).
    phones={re.sub(r"\D","",x) for x in re.findall(r"\(?\b\d{3}\)?[ .-]\d{3}-\d{4}\b",f.get("notes") or "")}
    if len(phones)==1:
        d=phones.pop(); place["telephone"]=f"+1-{d[:3]}-{d[3:6]}-{d[6:]}"
    # Free-entry flag only when the reviewed fee answer is an evidence-backed "no" (never inferred from blank or conditional fees).
    fee=(f.get("questions") or {}).get("fee_charged") or {}
    if fee.get("answer")=="no" and fee.get("evidence"): place["isAccessibleForFree"]=True
    spec=opening_hours_spec(f["hours"])
    if spec: place["openingHoursSpecification"]=spec
    elif f.get("hours"):
        place["description"]=place["description"]+". Hours: "+f["hours"]
    return drop_empty(place)

def city_qas(m, have):
    qas=[city_overview_qa(m)]
    hf=city_hours_fees_qa(m)
    if hf: qas.append(hf)
    for s,n in have:
        fs=[f for f in m["facilities"] if any(x[0]==s for x in mats(f))]
        qa=material_qa(m,s,fs)
        if qa: qas.append(qa)
    ev=event_vs_permanent_qa(m)
    if ev: qas.append(ev)
    if m["facilities"]:
        qas.append((GENERIC_HOURS[0], e(GENERIC_HOURS[1]), GENERIC_HOURS[1]))
        qas.append((GENERIC_BIZ[0], e(GENERIC_BIZ[1]), GENERIC_BIZ[1]))
    return qas

def material_seo(s, n, nsites, nmetros):
    """Title, H1 and meta description for a material hub. Counts come from facilities.json at build time."""
    low=n.split(" (")[0].lower()
    title=f"Where to recycle or dispose of {low}: {nsites} drop-off sites by city | TossMap"
    h1=f"Where to drop off {low} near you"
    desc=f"{plural(nsites,'official '+low+' drop-off location')} in {nmetros} US metro areas, with addresses, hours, limits and source links."
    if s=="tires":
        title=f"Tire disposal near me: {nsites} official drop-off sites in {nmetros} metros | TossMap"
        h1="Tire disposal near you: official drop-off sites by city"
        desc=f"Tire disposal near you: {nsites} official drop-off sites in {nmetros} US metros, with addresses, hours, tire limits, fees and a source link for every listing."
    elif s=="e-waste":
        title=f"Electronics recycling near me: {nsites} official e-waste drop-off sites | TossMap"
        h1="Electronics (e-waste) recycling near you: official drop-off sites by city"
        desc=f"Electronics and e-waste recycling near you: {nsites} official drop-off sites in {nmetros} US metros, with accepted items, hours, fees and a source link for every listing."
    elif s=="batteries":
        title=f"Battery disposal & recycling near me: {nsites} sites | TossMap"
        h1="Battery recycling and disposal near you"
        # Battery types differ by site (some take only vehicle/lead-acid batteries); each listing states what it takes.
        desc=f"Battery disposal near you: {nsites} official drop-off sites in {nmetros} US metros, from Portland to NYC. Battery types each site takes, hours and source links."
    elif s=="household-chemicals":
        title=f"Household hazardous waste disposal near me: {nsites} sites by city | TossMap"
        h1="Household hazardous waste disposal near you"
        # Do not claim every listing takes cleaners and pesticides; those appear on some, not all, household-chemicals sites.
        desc=f"Household hazardous waste (HHW) disposal near you: {nsites} official drop-off sites in {nmetros} US metros, with hours, limits and source links."
    elif s=="paint":
        title=f"Paint disposal near me: {nsites} official drop-off sites | TossMap"
        h1="Paint disposal near you: where to drop off old paint"
        # Many sites take only oil-based paint (no latex); each listing states which.
        desc=f"Where to dispose of paint near you: {nsites} official drop-off sites in {nmetros} US metros. Some take only oil-based paint; each listing says what it accepts."
    elif s=="motor-oil":
        title=f"Used motor oil disposal near me: {nsites} official drop-off sites | TossMap"
        h1="Used motor oil recycling and disposal near you"
        desc=f"Used motor oil recycling near you: {nsites} official drop-off sites in {nmetros} US metros, with quantity limits, hours, fees and a source link for every listing."
    return title,h1,desc

def material_page_qas(s, n, nsites, nmetros):
    low=n.split(" (")[0].lower()
    lead_q={"tires":"Where is tire disposal near me?","e-waste":"Where can I recycle electronics near me?","batteries":"Where can I recycle batteries near me?","paint":"Where can I dispose of paint near me?","motor-oil":"Where can I recycle used motor oil near me?","household-chemicals":"Where can I dispose of household hazardous waste near me?"}.get(s,f"Where can I drop off {low} near you?")
    lead=(f"TossMap lists {nsites} official drop-off site{'s' if nsites!=1 else ''} in {nmetros} US metro area{'s' if nmetros!=1 else ''} that list {low} as accepted. "
          "Rules, limits and residency requirements vary. Each city section below links to the listing and its official source, with a last-checked date. "
          "Confirm with that source before you go.")
    gq,ga=generic_material_faq(s)
    qas=[(lead_q, e(lead), lead)]
    if gq!=lead_q:
        qas.append((gq, e(ga), ga))
    qas.append((GENERIC_BIZ[0], e(GENERIC_BIZ[1]), GENERIC_BIZ[1]))
    qas.append((GENERIC_HOURS[0], e(GENERIC_HOURS[1]), GENERIC_HOURS[1]))
    return qas

def write_llms(matidx):
    n=sum(len(m["facilities"]) for m in D)
    nstates=len(states)
    lines=["# TossMap","",
           f"> Every TossMap listing is verified against an official government or facility-operator source. Each of the {n} sites includes that source link and a last-checked date. The data is unique because it is a source-backed, dated record — not an unverified aggregate. TossMap does not operate the listed facilities.","",
           f"TossMap lists {n} drop-off sites across {len(D)} US metro areas in {nstates} states. Listings include accepted materials, addresses, hours, fees and eligibility notes when the official source provides them. Rules and hours can change. Confirm with the linked operator before driving; a listing does not guarantee acceptance, availability or free service. Do not treat household waste listings as permission to bring commercial waste.","",
           f"A complete plain-text dump of every listing is in [llms-full.txt]({BASE}/llms-full.txt).",
           "API for agents: https://api.tossmap.com/llms.txt — paid per call in USDC via x402; free coverage checks and 3 free searches/day.",
           "MCP server for agents: https://api.tossmap.com/mcp (Streamable HTTP; tools: search_facilities, get_facility, coverage).","",
           "## Find a drop-off",
           f"- [Cities and materials]({BASE}/): directory index"]
    for s,nm,_ in MAT:
        ms=matidx[s]
        nsites=sum(len([f for f in m["facilities"] if any(x[0]==s for x in mats(f))]) for m in ms)
        lines.append(f"- [{nm}]({BASE}/{s}/): {nsites} official listings in {len(ms)} metro areas")
    lines += ["","## Cities"]
    for m in sorted(D, key=lambda x:x["city"]):
        lines.append(f"- [{m['city']}, {m['st']}]({BASE}{cpath(m)})")
    lines += ["", "## Facilities"]
    for m in sorted(D,key=lambda x:(x["city"],x["st"])):
        for f in m["facilities"]:
            lines.append(f"- [{f['name']} — {m['city']}, {m['st']}]({BASE}{fpath(f,m)})")
    lines += ["","## Optional",f"- [Privacy]({BASE}/privacy.html)",f"- [Newsletter]({BASE}/newsletter/): local drop-off updates",f"- [Full listings (plain text)]({BASE}/llms-full.txt)",""]
    open(f"{OUT}/llms.txt","w").write("\n".join(lines))

def write_llms_full():
    n=sum(len(m["facilities"]) for m in D)
    nstates=len(states)
    lines=["# TossMap — full facility listings","",
           f"Every listing below is verified against an official government or facility-operator source and includes that source URL and a last-checked date. TossMap lists {n} drop-off sites across {len(D)} US metro areas in {nstates} states. TossMap does not operate these facilities. Rules and hours can change; confirm with the official source before driving.","",
           f"A shorter index is in {BASE}/llms.txt.","",]
    by_state={}
    for m in D:
        by_state.setdefault((m["state"],m["st"]),[]).append(m)
    for (state,st),metros in sorted(by_state.items(), key=lambda x:x[0][0]):
        lines.append(f"## {state}")
        lines.append("")
        for m in sorted(metros, key=lambda x:x["city"]):
            lines.append(f"### {m['city']}, {st}")
            lines.append("")
            for f in m["facilities"]:
                fees=(f.get("fees") or "").strip() or "not listed"
                lines += [
                    f"Name: {f['name']}",
                    f"City/state: {m['city']}, {st}",
                    f"Address: {f['address']}",
                    f"Materials accepted: {f['accepts']}",
                    f"Hours: {f['hours']}",
                    f"Fees: {fees}",
                    f"Official source: {f['source']}",
                    f"Last checked: {f['checked']}",
                    f"TossMap page: {BASE}{fpath(f,m)}",
                    "",
                ]
    open(f"{OUT}/llms-full.txt","w").write("\n".join(lines))

AI_BOTS=("GPTBot","ChatGPT-User","OAI-SearchBot","ClaudeBot","Claude-SearchBot","Claude-User","PerplexityBot","Google-Extended")

def write_robots():
    lines=["# robots.txt — tossmap.com.",
           "# Every group repeats Allow because robots groups do not inherit.",
           "# AI answer-engines are welcome: listings are first-party, source-backed drop-off data.",
           "","User-agent: *","Allow: /","",
           "# AI answer-engines are explicitly welcome."]
    for bot in AI_BOTS:
        lines += [f"User-agent: {bot}","Allow: /",""]
    lines += [f"Sitemap: {BASE}/sitemap.xml",""]
    open(f"{OUT}/robots.txt","w").write("\n".join(lines))

def load_indexnow_key():
    for path in ("/workspace/tossmap/indexnow-key.txt","data/indexnow-key.txt"):
        if os.path.isfile(path):
            key=open(path).read().strip()
            if re.fullmatch(r"[A-Fa-f0-9]{32}", key):
                return key
    raise SystemExit("IndexNow key file missing; expected data/indexnow-key.txt")

def write_indexnow_key():
    key=load_indexnow_key()
    open(f"{OUT}/{key}.txt","w").write(key+"\n")
    try:
        os.makedirs("/workspace/tossmap", exist_ok=True)
        dest="/workspace/tossmap/indexnow-key.txt"
        if not os.path.isfile(dest) or open(dest).read().strip()!=key:
            open(dest,"w").write(key+"\n")
    except OSError:
        pass

def ldj(f, m):
    place=facility_place(f, m)
    hm=re.search(r"Event:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+(Nov|Dec|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct)\s+(\d{1,2}),\s*(20\d{2})", f.get("hours",""))
    if hm:
        mon={"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}[hm.group(1)]
        return drop_empty({"@type":"Event","name":f["name"],"startDate":f"{hm.group(3)}-{mon}-{int(hm.group(2)):02d}",
            "eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","eventStatus":"https://schema.org/EventScheduled",
            "location":place,"description":"Accepts: "+f["accepts"],"url":f["source"],
            "organizer":{"@type":"Organization","name":"Official source","url":f["source"]}})
    return place

def fac(f,m):
    tags=" ".join(f'<a href="/{s}/">{e(n)}</a>' for s,n,_ in mats(f))
    return f"""<div class="card" id="{slug(f['name'])}"><h3><a href="{fpath(f,m)}">{e(f['name'])}</a></h3><div>{e(f['address'])}</div>
<p><b>Accepts:</b> {e(f['accepts'])}<br><b>Hours:</b> {e(f['hours'])}{'<br><b>Fees:</b> '+e(f['fees']) if f['fees'] else ''}{'<br><b>Notes:</b> '+e(f['notes']) if f['notes'] else ''}</p>
{'<p class="note">'+e(f['source_notice'])+'</p>' if f.get('source_notice') else ''}{'<p class="note"><strong>Past event:</strong> '+e(past_event_note(f))+'</p>' if is_past_event(f) else ''}{'<p class="tags">'+tags+'</p>' if tags else ''}<div class="meta">Source: <a href="{e(f['source'])}" rel="nofollow noopener">{e(f['source'])}</a> · Last checked {f['checked']}</div></div>"""

CITY_ALIASES={
    "New York":("nyc","new york city"),
    "San Francisco":("sf",),
    "Los Angeles":("la county","l.a.","los angeles county"),
    "Washington":("d.c.","district of columbia","washington, dc"),
    "Honolulu":("oahu","city and county of honolulu"),
}
def residency_ok_for_city(f,m):
    """True when it is safe to say '{city} residents can drop off...'. Skip that claim if the listing limits use to a different place."""
    blob=" ".join((
        f.get("notes") or "",
        ((f.get("questions") or {}).get("residents_only") or {}).get("evidence") or "",
        f.get("fees") or "",
    )).lower()
    names=[m["city"].lower(), *CITY_ALIASES.get(m["city"],())]
    # "Fairfax County residents" / "county residents" — do not attribute that access to the metro city.
    for phrase in re.findall(r"((?:[a-z]+ ){0,3}(?:county|parish|city) residents|[a-z]+ residents)", blob):
        if not any(n and n in phrase for n in names):
            return False
    ro=((f.get("questions") or {}).get("residents_only") or {}).get("answer")
    if ro!="yes":
        return True
    if any(n and n in blob for n in names+[m["st"].lower(), (m.get("state") or "").lower()]):
        return True
    if not re.search(r"resident|county|city of|only", blob):
        return True
    return False

def facility_place_label(f,m):
    """City and state from the listing address, not the metro directory city."""
    pa=parse_address(f.get("address") or "")
    loc=(pa.get("addressLocality") or "").strip()
    region=(pa.get("addressRegion") or "").strip() or m["st"]
    if loc:
        return f"{loc}, {region}"
    mm=re.search(r",\s*([^,]+),\s*([A-Z]{2})(?:\s+\d{5}(?:-\d{4})?)?\s*$", (f.get("address") or "").strip())
    if mm:
        return f"{mm.group(1).strip()}, {mm.group(2)}"
    return f"{m['city']}, {m['st']}"

def hours_is_short(hours):
    """True when hours are a short, single-line phrase (no sentence breaks)."""
    h=(hours or "").strip().rstrip(" .")
    if not h or len(h)>70:
        return False
    tmp=re.sub(r"(?i)\b[ap]\.m\.","",h)
    return not re.search(r"\.", tmp)

def fee_clause(fees):
    """Attach only a short fee phrase. Omit long or multi-clause fee prose; never invent a value."""
    raw=(fees or "").strip()
    if not raw:
        return ""
    text=raw.rstrip(" .")
    if re.fullmatch(r"free", text, re.I):
        return ", and it's free"
    m=re.match(r"(?i)^free(\s+(?:for|with)\s+.{1,40})$", text)
    if m and not re.search(r"[;.$]", text) and len(text)<=60:
        return f", and it's free{m.group(1)}"
    tmp=re.sub(r"(?i)\b[ap]\.m\.","",text)
    if len(text)<=60 and not re.search(r"[;.]", tmp):
        return f"; fees: {text}"
    return ""

def source_domain(url):
    host=urlparse(url).netloc.lower()
    if host.startswith("www."):
        host=host[4:]
    return host

def source_sentence(url):
    url=(url or "").strip()
    if not url:
        return ""
    label=source_domain(url) or url
    return f' Source: <a href="{e(url)}" rel="noopener">{e(label)}</a>.'

def _lead_word_count(sentence, url):
    vis=sentence
    if url:
        vis+=f" Source: {source_domain(url) or url}."
    return len(vis.split())

def _sentence_with_hours_fees(lead, hours_core, fee):
    if hours_core=="see":
        return lead+fee+". See hours below." if fee else lead+". See hours below."
    if hours_core:
        return lead+f", {hours_core}"+fee+"."
    return lead+fee+"."

def attach_hours_fees(lead, hours, fees, source_url=""):
    """Add short hours/fees only. Long hours become 'See hours below.'; long fees are omitted. Keep the line to about 35 words."""
    hours_core=(hours or "").strip().rstrip(" .")
    fee=fee_clause(fees)
    candidates=[]
    if hours_core and hours_is_short(hours_core):
        candidates.append(_sentence_with_hours_fees(lead, hours_core, fee))
        if fee:
            candidates.append(_sentence_with_hours_fees(lead, hours_core, ""))
    if hours_core:
        candidates.append(_sentence_with_hours_fees(lead, "see", fee))
        candidates.append(_sentence_with_hours_fees(lead, "see", ""))
    else:
        candidates.append(_sentence_with_hours_fees(lead, "", fee))
        candidates.append(lead+".")
    for sentence in candidates:
        if _lead_word_count(sentence, source_url)<=35:
            return sentence
    return lead+"."

def facility_direct_answer(f,m):
    """One short sentence from verified fields only. Skip unknown fields rather than invent them."""
    materials=[MAT_SHORT[s] for s,_,_ in mats(f)]
    place=facility_place_label(f,m)
    if materials:
        if residency_ok_for_city(f,m):
            lead=f"{m['city']} residents can drop off {and_list(materials)} at {f['name']}"
        else:
            lead=f"{f['name']} in {place} accepts {and_list(materials)}"
    else:
        lead=f"{f['name']} is a listed drop-off site in {place}"
    src=f.get("source") or ""
    html_lead=e(attach_hours_fees(lead, f.get("hours") or "", f.get("fees") or "", src))
    html_lead+=source_sentence(src)
    return f'<p class="lead">{html_lead}</p>'

def city_direct_answer(m,have):
    fs=m["facilities"]
    if not fs:
        return ""
    materials=[MAT_SHORT[s] for s,_ in have]
    named=CITY_NAMED.get((m["st"],m["city"]))
    site=next((f for f in fs if f["name"]==named), fs[0])
    if materials:
        if all(residency_ok_for_city(f,m) for f in fs):
            lead=f"{m['city']} residents can drop off {and_list(materials)}"
            if len(fs)==1:
                lead+=f" at {site['name']}"
            else:
                lead+=f" at {len(fs)} official sites, including {site['name']}"
        else:
            n=len(fs)
            sites=f"{n} official site" + ("" if n==1 else "s")
            lead=f"{m['city']}, {m['st']} has {sites} listed for {and_list(materials)}, including {site['name']}"
    else:
        if len(fs)==1:
            lead=f"{site['name']} is listed for {m['city']}, {m['st']}"
        else:
            lead=f"{m['city']}, {m['st']} has {len(fs)} official drop-off sites listed, including {site['name']}"
    # Hours and fees belong to one site; only attach them on single-site city pages to keep the sentence short.
    if len(fs)==1:
        sentence=attach_hours_fees(lead, site.get("hours") or "", site.get("fees") or "", site.get("source") or "")
    else:
        sentence=lead+"."
    return f'<p class="lead">{e(sentence)+source_sentence(site.get("source") or "")}</p>'


def facility_overview(f,m):
    """Sourced overview that weaves this listing's address, hours and accepted items into the copy. No invented facts."""
    name=f["name"]; addr=(f.get("address") or "").strip(); hours=(f.get("hours") or "").strip()
    accepts=(f.get("accepts") or "").strip(); fees=(f.get("fees") or "").strip()
    parts=[]
    if addr: parts.append(f"{name} is at {addr}.")
    else: parts.append(f"{name} is a listed drop-off site in {m['city']}, {m['st']}.")
    if hours: parts.append(f"Hours: {hours}.")
    if accepts:
        a=accepts.rstrip(".")
        if a and a[0].isupper() and not a[:2].isupper():
            a=a[0].lower()+a[1:]
        parts.append("It accepts "+a+".")
    if fees: parts.append("Fees: "+fees.rstrip(".")+".")
    parts.append("This is an independent source-backed listing, not the operator’s website.")
    return "<p>"+e(" ".join(parts))+"</p>"

def facility_page(f,m):
    fp=fpath(f,m)
    vis,bl=crumbs([("Home","/"),(m["state"],f"/{slug(m['st'])}/"),(m["city"],cpath(m)),(f["name"],fp)])
    rows=[]; entities=[]
    for key,label in QUESTIONS:
        answer=f["questions"][key]
        text=answer["answer"].capitalize()
        if answer["evidence"]: text+=" — "+answer["evidence"]
        rows.append(f'<tr><th scope="row">{e(label)}</th><td>{e(text)}</td></tr>')
        entities.append({"@type":"Question","name":label,"acceptedAnswer":{"@type":"Answer","text":text}})
    materials=" · ".join(f'<a href="/{ms}/">{e(n)}</a>' for ms,n,_ in mats(f))
    others=[o for o in m["facilities"] if o is not f]
    body=(vis+f'<h1>{e(f["name"])}</h1>'+facility_direct_answer(f,m)+facility_overview(f,m)
          +(f'<p class="note">{e(f["source_notice"])}</p>' if f.get("source_notice") else "")
          +(f'<p class="note"><strong>Past event:</strong> {e(past_event_note(f))}</p>' if is_past_event(f) else "")
          +'<section class="card"><h2>Before you go</h2><dl>'
          +''.join(f'<dt><strong>{e(label)}</strong></dt><dd>{e(value or UNKNOWN)}</dd>' for label,value in [
              ("Operator",f["operator"]),("Full address",f["address"]),("Accepted materials",f["accepts"]),
              ("Hours / collection schedule",f["hours"]),("Fees",f["fees"]),("Eligibility, ID and other notes",f["notes"])])
          +f'</dl><p><a href="{e(f["source"])}" rel="noopener">Official source and current rules</a> · Updated {e(format_updated(f["checked"]))}. Last checked {e(f["checked"])}. · <a href="{fix_mailto(fp)}">Is this info wrong? Suggest a fix</a></p></section>'
          +f'<h2>Common questions</h2><p class="meta">Question set reviewed {e(f.get("questions_reviewed",f["checked"]))}.</p><p>Yes and no apply only to the material types, users and conditions in the accompanying evidence. A fee answer of no means the listed service is free under those conditions; it does not waive eligibility rules. “Not stated by source” means no explicit answer is recorded in our source-backed listing, not that the source has no further information. Check the official source before driving.</p>'
          +'<table class="questions"><caption>Facility requirements and material acceptance</caption><thead><tr><th scope="col">Question</th><th scope="col">Answer and source-backed detail</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
          +(f'<h2>Browse accepted materials</h2><p>{materials}</p>' if materials else '')
          # City-scoped internal links: each material hub has a per-city section (#city-st) listing every site there that takes it.
          +(f'<p>More in {e(m["city"])}: '+" · ".join(f'<a href="/{ms}/#{slug(m["city"])}-{slug(m["st"])}">{e({"tires":"tire","batteries":"battery"}.get(ms,n.split(" (")[0].lower()))} drop-off in {e(m["city"])}</a>' for ms,n,_ in mats(f))+'</p>' if materials else '')
          +f'<p><a href="{cpath(m)}">All drop-off options in {e(m["city"])}</a> · <a href="/{slug(m['st'])}/">More drop-off sites in {e(m["state"])}</a></p>'
          +('<h2>Other facilities in this city directory</h2><ul>'+''.join(f'<li><a href="{fpath(o,m)}">{e(o["name"])}</a> — {e(o["address"])}</li>' for o in others)+'</ul>' if others else '<p>No other facilities are currently listed in this city directory. Follow the city link above for local guidance.</p>')
          +'<p class="note">Use the exact acceptance notes above: paint types, battery types, item limits and event dates matter. Do not mix chemicals or assume a material is accepted because a similar item is listed. Confirm availability with the operator.</p>')
    place=facility_place(f,m)
    webpage={"@type":"WebPage","@id":BASE+fp+"#page","url":BASE+fp,"name":f["name"],"mainEntity":{"@id":place["@id"]},"publisher":{"@id":ORG_ID},"citation":f["source"],"dateModified":f["checked"],"inLanguage":"en-US","isPartOf":{"@id":BASE+"/#website"}}
    # Many facility names are generic ("Waste Reduction Center"), so the city goes in the title.
    ttl=f'{f["name"]}, {m["city"]} {m["st"]}: hours & rules | TossMap'
    if m["city"].lower() in f["name"].lower(): ttl=f'{f["name"]} ({m["st"]}): hours, materials & rules | TossMap'
    # SEO length guard (Nov 26 2026): long names push titles past ~60 characters, so step down to shorter forms only when needed.
    short=re.sub(r"\s*\([^)]*\)","",f["name"]).strip()
    if sum(re.sub(r"\s*\([^)]*\)","",o["name"]).strip()==short for o in m["facilities"])>1: short=f["name"]  # keep titles unique
    for cand in ([f'{f["name"]} ({m["st"]}) | TossMap',f'{short} ({m["st"]}) | TossMap',f'{short}, {m["st"]}'] if m["city"].lower() in f["name"].lower()
                 else [f'{f["name"]}, {m["city"]} {m["st"]} | TossMap',f'{short}, {m["city"]} {m["st"]} | TossMap',f'{short}, {m["city"]} {m["st"]}']):
        if len(ttl)<=60: break
        ttl=cand
    mnames=[n.split(" (")[0].lower() for _,n,_ in mats(f)]
    takes=f' Takes {and_list(mnames)}.' if mnames else ''
    where=f'{"in" if m["city"].lower() in f["address"].lower() else "in the"} {m["city"]}, {m["st"]}{"" if m["city"].lower() in f["address"].lower() else " area"}'
    desc=f'{f["name"]} {where}: address, hours, fees, eligibility and official source.{takes} Last checked {f["checked"]}.'
    # Same guard for the meta description (~160 characters): drop the qualifier in parentheses, then the long phrase, never the facts.
    for cand in [f'{short} {where}: address, hours, fees, eligibility and official source.{takes} Last checked {f["checked"]}.',
                 f'{short} {where}: hours, fees, rules and official source.{takes} Checked {f["checked"]}.',
                 f'{short} {where}: hours, fees, rules and official source.{takes}',
                 f'{short} {where}: hours, fees, accepted materials and official source. Checked {f["checked"]}.']:
        if len(desc)<=160: break
        desc=cand
    page(fp,ttl,
         desc,
         body,[bl,webpage,place,{"@type":"FAQPage","mainEntity":entities}]+([event_ld(f,m,place)] if event_ld(f,m,place) else []),f["checked"])

# One-day collection events ("Event: Sat Dec 12, 2026, 8am–2pm") get schema.org Event markup, using only the listing's own date/time text.
STATE_TZ={"DC":"America/New_York","MA":"America/New_York","MD":"America/New_York","PA":"America/New_York","OH":"America/New_York","NY":"America/New_York","VA":"America/New_York","GA":"America/New_York","FL":"America/New_York","NC":"America/New_York","MI":"America/New_York","KY":"America/New_York","TX":"America/Chicago","IL":"America/Chicago","LA":"America/Chicago","TN":"America/Chicago","MO":"America/Chicago","MN":"America/Chicago","WI":"America/Chicago","OK":"America/Chicago","NE":"America/Chicago","CO":"America/Denver","UT":"America/Denver","NM":"America/Denver","AZ":"America/Phoenix","CA":"America/Los_Angeles","WA":"America/Los_Angeles","OR":"America/Los_Angeles","NV":"America/Los_Angeles","HI":"Pacific/Honolulu"}
MONTHS={m:i+1 for i,m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}
def event_ld(f,m,place):
    mm=re.search(r"Event:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s*(20\d{2})(?:,\s*([0-9:]+(?:am|pm)?)\s*[–-]\s*([0-9:]+(?:am|pm)|noon))?",f.get("hours") or "")
    if not mm or is_past_event(f): return None
    from datetime import datetime
    from zoneinfo import ZoneInfo
    y,mo,d=int(mm.group(3)),MONTHS[mm.group(1)],int(mm.group(2))
    def stamp(tok,inherit=None):
        if not tok: return None
        t=parse_time(tok,inherit)
        if not t or m["st"] not in STATE_TZ: return None
        hh,mi=map(int,t.split(":"))
        return datetime(y,mo,d,hh,mi,tzinfo=ZoneInfo(STATE_TZ[m["st"]])).isoformat()
    endtok=mm.group(5); inh=re.search(r"(am|pm)$",endtok or "")
    start=stamp(mm.group(4),inh.group(1) if inh else None) or f"{y:04d}-{mo:02d}-{d:02d}"
    end=stamp(endtok)
    ev={"@type":"Event","name":f'{f["name"]} ({mm.group(1)} {d}, {y})',"startDate":start,"eventStatus":"https://schema.org/EventScheduled",
        "eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","location":{"@id":place["@id"]},"url":f["source"],
        "description":"Accepts: "+f["accepts"]+(". "+f["notes"] if f.get("notes") else "")}
    if end: ev["endDate"]=end
    if (f.get("fees") or "").strip().lower().startswith("free"): ev["isAccessibleForFree"]=True
    if f.get("operator") and f["operator"]!=UNKNOWN: ev["organizer"]={"@type":"Organization","name":f["operator"],"url":f["source"]}
    return ev

def and_list(xs): return ", ".join(xs[:-1])+" and "+xs[-1] if len(xs)>1 else "".join(xs)
def fac_link_text(f):
    names=[MAT_SHORT[s] for s,_,_ in mats(f)]
    return e(f["name"])+(f" — {e(and_list(names))}" if names else "")
# Weekend quick list on larger city pages, derived only from each listing's own hours text ("closed Sun" segments ignored).
WKND=re.compile(r"(?i)\b(Sat|Sun)(urday|day)?s?\b|\bdaily\b|\b(7|seven) days\b")
def weekend_block(m):
    fs=[f for f in m["facilities"] if WKND.search(re.sub(r"(?i)closed[^;)]*","",f.get("hours","")))]
    if len(m["facilities"])<6 or not fs: return ""
    return (f'<h2>Weekend drop-off options in {e(m["city"])}</h2><p>{plural(len(fs),"listed site")} in this directory show Saturday or Sunday hours. Check the hours on each listing and the official source before you go.</p><ul>'
            +"".join(f'<li><a href="{fpath(f,m)}">{e(f["name"])}</a>: {e(f["hours"])}</li>' for f in fs)+"</ul>")
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
        ans_html,faq=faq_block(city_qas(m, have))
        # H1 names only materials this city's listings actually accept (same source-backed index as the title), not a fixed phrase.
        hs={s for s,_ in have}; hl=[w for k,w in MAT_H1.items() if k in hs][:3]
        h1=f'Where to dump {and_list(hl) if hl else "household hazardous waste"} in {m["city"]}, {st}'
        named=CITY_NAMED.get((m["st"],m["city"]))
        if named and any(f["name"]==named for f in fs): h1=f'{named}: where to dump {and_list(hl) if hl else "household hazardous waste"} in {m["city"]}, {st}'
        body=(vis+f'<h1>{e(h1)}</h1>'+city_direct_answer(m, have)+freshness_html(fs)+note+ans_html
              +"".join(fac(f,m) for f in fs)+("<p>No permanent drop-off site listed yet. See the note above for event-based or alternate official options, and check back after the next source review.</p>" if not fs else "")
              +weekend_block(m)
              +(('<h2>By material</h2>'+"".join(f'<h3><a href="/{s}/">{e(n)} drop-off</a></h3><ul>'+"".join(f'<li><a href="{fpath(f,m)}">{e(f["name"])}</a></li>' for f in m["facilities"] if any(x[0]==s for x in mats(f)))+"</ul>" for s,n in have)) if have else "")
              +f'<p class="meta">Run a local site? <a href="/embed/">Embed this list for free</a>.</p>'+(f'<h2>Other cities in {e(sn)}</h2><ul>'+"".join(f'<li><a href="{cpath(o)}">{e(o["city"])}</a></li>' for o in nearby)+"</ul>" if nearby else "")
              +signup_box())
        short={"Electronics (e-waste)":"e-waste","Household chemicals":"chemicals"}
        tl=[short.get(n,n).lower() for _,n in have if n!="Household chemicals"][:3]
        title=f"Where to dump {', '.join(tl[:-1])+' & '+tl[-1] if len(tl)>1 else (tl[0] if tl else 'hazardous waste')} in {m['city']}, {st} | TossMap"
        what=", ".join(n.split(" (")[0].lower() for _,n in have[:4]) or "household hazardous waste"
        desc=(f"{plural(len(fs),'official drop-off site')} in {m['city']}, {st} for {what}: addresses, hours, fees and source links, last checked {chk}." if fs
              else f"How {m['city']}, {st} handles household hazardous waste, from official sources.")
        collection={"@type":"CollectionPage","@id":BASE+cp+"#page","url":BASE+cp,"name":h1,"publisher":{"@id":ORG_ID},"isPartOf":{"@id":BASE+"/#website"},"inLanguage":"en-US"}
        if chk: collection["dateModified"]=chk
        cites=unique_sources(fs)
        if cites: collection["citation"]=[{"@type":"WebPage","url":u} for u in cites]
        # City pages: ItemList of the facility pages they link to (same names and URLs as the visible cards).
        sites=[]
        if fs:
            collection["mainEntity"]={"@id":BASE+cp+"#sites"}
            sites=[{"@type":"ItemList","@id":BASE+cp+"#sites","name":f'Official drop-off sites in {m["city"]}, {st}',"numberOfItems":len(fs),
                    "itemListElement":[{"@type":"ListItem","position":k+1,"name":f["name"],"url":BASE+fpath(f,m)} for k,f in enumerate(fs)]}]
        graph=[bl,collection]+sites+[ldj(f,m) for f in fs]+([faq] if faq else [])
        page(cp,title,desc,body,graph,chk)
    vis,bl=crumbs([("Home","/"),(sn,sp)])
    nst=sum(len(m["facilities"]) for m in ms)
    def state_city_block(m):
        mh=[(s,n) for s,n,_ in MAT if m in matidx[s]]
        head=f'<h2><a href="{cpath(m)}">{e(m["city"])}</a> ({plural(len(m["facilities"]),"site")})</h2>'
        mats_line=('<p class="tags">'+" ".join(f'<a href="/{s}/">{e(n.split(" (")[0].lower())}</a>' for s,n in mh)+"</p>") if mh else ""
        items="".join(f'<li><a href="{fpath(f,m)}">{fac_link_text(f)}</a></li>' for f in m["facilities"])
        return head+mats_line+(f"<ul>{items}</ul>" if items else "")
    st_fs=[f for m in ms for f in m["facilities"]]
    st_chk=max([f["checked"] for f in st_fs],default=None)
    st_collection={"@type":"CollectionPage","@id":BASE+sp+"#page","url":BASE+sp,"name":f"Hazardous waste drop-off in {sn}","publisher":{"@id":ORG_ID},"isPartOf":{"@id":BASE+"/#website"},"mainEntity":{"@id":BASE+sp+"#cities"},"inLanguage":"en-US"}
    if st_chk: st_collection["dateModified"]=st_chk
    st_matl=[n.split(" (")[0].lower() for s,n,_ in MAT if any(m in matidx[s] for m in ms)]
    st_mats=and_list(st_matl) or "household hazardous waste"
    st_desc=f"{plural(nst,'official drop-off site')} in {sn} ({', '.join(m['city'] for m in ms)}) for {st_mats}, with source links."
    # SEO length guard (Nov 26 2026): states with many metros name the first three and count the rest.
    if len(st_desc)>160 and len(ms)>3: st_desc=f"{plural(nst,'official drop-off site')} in {sn} ({', '.join(m['city'] for m in ms[:3])} and {len(ms)-3} more) for {st_mats}, with source links."
    if len(st_desc)>160 and len(st_matl)>3: st_desc=f"{plural(nst,'official drop-off site')} in {sn} ({', '.join(m['city'] for m in ms[:3])}{f' and {len(ms)-3} more' if len(ms)>3 else ''}) for {', '.join(st_matl[:3])} and more, with source links."
    page(sp,f"Hazardous waste, paint & e-waste drop-off in {sn} | TossMap",
         st_desc,
         vis+f'<h1>Hazardous waste drop-off in {e(sn)}</h1>'+freshness_html(st_fs)+f'<p>{plural(nst,"official drop-off site")} across {plural(len(ms),"metro area")} in {e(sn)}. Each city page lists addresses, hours, fees, eligibility rules and a link to the official source, with the date we last checked it.</p>'+"".join(state_city_block(m) for m in ms),
         # State hubs: CollectionPage + ItemList of the city pages they link to (same names and URLs as the visible list).
         [bl,st_collection,
          {"@type":"ItemList","@id":BASE+sp+"#cities","name":f"{sn} metro areas with official drop-off sites","numberOfItems":len(ms),"itemListElement":[{"@type":"ListItem","position":k+1,"name":f'{m["city"]}, {m["st"]}',"url":BASE+cpath(m)} for k,m in enumerate(ms)]}],
         st_chk)
for s,n,_ in MAT:
    ms=sorted(matidx[s],key=lambda x:x["city"]); low=n.split(" (")[0].lower()
    vis,bl=crumbs([("Home","/"),(n,f"/{s}/")])
    hits=[(m,[f for f in m["facilities"] if any(x[0]==s for x in mats(f))]) for m in ms]
    nsites=sum(len(fs) for _,fs in hits); nmetros=len(ms)
    title,h1,desc=material_seo(s,n,nsites,nmetros)
    ans_html,faq=faq_block(material_page_qas(s,n,nsites,nmetros))
    body=(vis+f"<h1>{e(h1)}</h1>"+freshness_html([f for _,fs in hits for f in fs])+f"<p>{plural(nsites,'official drop-off site')} in {plural(nmetros,'metro area')} list {e(low)} as accepted. Rules, limits and residency requirements vary, so check each listing's source link before you go.</p>"
      +ans_html
      +"<ul class=grid>"+"".join(f'<li><a href="#{slug(m["city"])}-{slug(m["st"])}">{e(m["city"])}, {m["st"]}</a></li>' for m in ms)+"</ul>"
      +"".join(f'<h2 id="{slug(m["city"])}-{slug(m["st"])}">{e(low.capitalize())} drop-off in <a href="{cpath(m)}">{e(m["city"])}, {m["st"]}</a></h2><ul>'
               +"".join(f'<li><a href="{fpath(f,m)}">{e(f["name"])}</a> — {e(f["address"])}<span class="meta"> · checked {f["checked"]}</span></li>' for f in fs)+"</ul>" for m,fs in hits)
      +"<p>Other materials: "+" · ".join(f'<a href="/{o}/">{e(on)}</a>' for o,on,_ in MAT if o!=s)+"</p>"
      +signup_box())
    il={"@type":"ItemList","name":f"{n} drop-off sites by city","numberOfItems":nsites,"itemListElement":[{"@type":"ListItem","position":k+1,"name":f'{f["name"]} ({m["city"]}, {m["st"]})',"url":f'{BASE}{fpath(f,m)}'} for k,(m,f) in enumerate((m,f) for m,fs in hits for f in fs)]}
    mat_fs=[f for _,fs in hits for f in fs]
    mat_chk=max([f["checked"] for f in mat_fs],default=None)
    collection={"@type":"CollectionPage","@id":BASE+f"/{s}/#page","url":BASE+f"/{s}/","name":h1,"publisher":{"@id":ORG_ID},"inLanguage":"en-US"}
    if mat_chk: collection["dateModified"]=mat_chk
    graph=[bl,collection,il]+([faq] if faq else [])
    page(f"/{s}/",title,desc,body,graph,mat_chk)
n=sum(len(m["facilities"]) for m in D)
# Home page crawl paths: (1) upcoming dated collection days parsed only from each listing's own hours text, dropped once past;
# (2) the most recently added/re-checked listings so new facility pages get a link from the home page.
EVDATE=re.compile(r"(?:Event:\s*|Collection days:\s*|next:\s*)(?:(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:[–-]\d{1,2})?,\s*(20\d{2})")
def next_date(f):
    mm=EVDATE.search(f.get("hours") or "")
    return f"{int(mm.group(3)):04d}-{MONTHS[mm.group(1)]:02d}-{int(mm.group(2)):02d}" if mm else None
upcoming=sorted(((d,m,f) for m in D for f in m["facilities"] for d in [next_date(f)] if d and d>=TODAY),key=lambda x:(x[0],x[1]["city"],x[2]["name"]))
recent=sorted(((f["checked"],m,f) for m in D for f in m["facilities"]),key=lambda x:(x[0],x[1]["city"],x[2]["name"]),reverse=True)[:12]
home_events=(f"<h2>Upcoming collection days</h2><p class=\"meta\">As of {TODAY}.</p><ul>"+"".join(f'<li><a href="{fpath(f,m)}">{e(f["name"])}</a> ({e(m["city"])}, {m["st"]}) — {datetime.date.fromisoformat(d).strftime("%a %b %-d, %Y")}</li>' for d,m,f in upcoming)+"</ul><p class=\"meta\">Dates come from each official source; confirm before you go.</p>") if upcoming else ""
home_recent=("<h2>Recently added or re-checked</h2><ul>"+"".join(f'<li><a href="{fpath(f,m)}">{e(f["name"])}</a> — {e(m["city"])}, {m["st"]}<span class="meta"> · checked {f["checked"]}</span></li>' for c,m,f in recent)+"</ul>")
home=(f"<h1>Where do I take paint, chemicals, batteries, electronics &amp; tires?</h1><p>{n} drop-off sites from official government and operator sources across {len(D)} US metros. Every listing links to its source and shows when we last checked it.</p>"
 "<h2>By material</h2><p class=tags>"+" ".join(f'<a href="/{s}/">{e(nm)}</a>' for s,nm,_ in MAT)+"</p>"
 "<h2>By city</h2><ul class=grid>"+"".join(f'<li><a href="{cpath(m)}">{e(m["city"])}, {m["st"]}</a></li>' for m in sorted(D,key=lambda x:x["city"]))+"</ul><h2>By state</h2><ul class=grid>"+"".join(f'<li><a href="/{slug(st)}/">{e(sn)}</a></li>' for sn,st in sorted(states))+"</ul>"+home_events+home_recent+signup_box())
page("/","TossMap: where to dump paint, hazardous waste, e-waste & tires by city","Find official drop-off sites for paint, chemicals, batteries, electronics and tires in 50+ US metros, addresses, hours, fees and source links, checked regularly.",home,
     [{"@type":"Organization","@id":ORG_ID,"name":"TossMap","url":BASE+"/"},{"@type":"WebSite","@id":BASE+"/#website","name":"TossMap","url":BASE+"/","publisher":{"@id":ORG_ID}}],max(f["checked"] for m in D for f in m["facilities"]))
page("/privacy.html","Privacy | TossMap","TossMap privacy policy: no cookies on our pages; newsletter sign-ups are handled by Kit and we do not sell your email.","<h1>Privacy</h1><p>TossMap sets no cookies. We use GoatCounter, a privacy-friendly analytics service that does not track individuals.</p><p>If you sign up for the <a href=\"/newsletter/\">TossMap newsletter</a>, your email is collected by Kit, our email provider, so we can send drop-off updates. We do not sell your email. Kit will send a confirmation email first, and you can unsubscribe anytime.</p><p>If ads are added, ad partners may use cookies; this page will be updated before that happens.</p><p>Listings come from public government sources and may change; confirm with the source before visiting.</p>")
open(f"{OUT}/404.html","w").write(open(f"{OUT}/index.html").read().replace("<h1>","<h1>Page not found.</h1><h2>",1).replace("</h1><p>","</h2><p>",1).replace(f'<link rel="canonical" href="{BASE}/">','<meta name="robots" content="noindex">'))
# EMBED: compact, noindex widget per city for other sites (free iframe snippet)
EMB_CSS="body{margin:0;font:14px/1.45 system-ui,sans-serif;color:#1d2a24;background:#fff}.w{padding:12px}.w h2{font-size:16px;margin:0 0 8px}.f{border-top:1px solid #e3e8e4;padding:8px 0}.f b{display:block}.m{font-size:12px;color:#5b6b63}a{color:#1f6b4d}.by{font-size:12px;margin-top:8px}"
def snippet(m): return f'<iframe src="{BASE}/embed{cpath(m)}" title="Hazardous waste drop-off sites in {e(m["city"])} (TossMap)" width="100%" height="460" style="border:1px solid #dfe5e0;border-radius:8px" loading="lazy"></iframe>'
for m in D:
    p=f"{OUT}/embed{cpath(m)}index.html"; os.makedirs(os.path.dirname(p),exist_ok=True)
    fs="".join(f'<div class="f"><b>{e(f["name"])}</b>{e(f["address"])}<br>Accepts: {e(f["accepts"])}<br>Hours: {e(f["hours"])}<div class="m"><a href="{e(f["source"])}" target="_blank" rel="nofollow noopener">Official source</a> · checked {f["checked"]}</div></div>' for f in m["facilities"]) or f'<p>{e(m["note"]) or "No permanent drop-off site found in official sources."}</p>'
    open(p,"w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="canonical" href="{BASE}{cpath(m)}"><title>Drop-off sites in {e(m["city"])} | TossMap</title><style>{EMB_CSS}</style>{ICONS}{GC}</head><body><div class="w"><h2>Where to drop off hazardous waste in {e(m["city"])}, {m["st"]}</h2>{fs}<div class="by">Full list and updates at <a href="{BASE}{cpath(m)}" target="_blank">TossMap</a></div></div></body></html>')
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

nl_vis,nl_bl=crumbs([("Home","/"),("Newsletter","/newsletter/")])
nl_body=(nl_vis+"<h1>Get local drop-off updates, hazardous-waste days and new locations</h1>"
 "<p>The TossMap newsletter is free. About once a week we send new official listings, upcoming household hazardous-waste collection days, and one short disposal tip. You can unsubscribe anytime.</p>"
 "<div class=\"signup\">"+signup_form()+
 "<p class=\"meta\">When you sign up, Kit (our email provider) will send a confirmation email first. We will not add you until you confirm that address. We do not sell your email.</p></div>"
 "<p>If the form does not work, you can also use the <a href=\""+KIT_HOSTED+"\">hosted sign-up page</a>.</p>"
 "<h2>Privacy</h2><p>This form does not set cookies or add any trackers beyond the GoatCounter analytics already used on TossMap. Your email is stored by Kit so we can send the newsletter. See our <a href=\"/privacy.html\">privacy policy</a>.</p>")
page("/newsletter/","Get local drop-off updates | TossMap","Free TossMap newsletter: local drop-off updates, hazardous-waste days and new locations. About weekly, unsubscribe anytime. Confirmation email first; we do not sell your email.",nl_body,[nl_bl])

# This is a queue, not an automatic indexing submission. Request in small daily batches.
priority=["Richmond","Philadelphia","Dallas","San Antonio","Atlanta","Boston","Cleveland","Louisville","New York","Los Angeles","Houston","Phoenix","Chicago"]
facility_queue=[]
for m in sorted(D,key=lambda x:(priority.index(x["city"]) if x["city"] in priority else len(priority),-len(x["facilities"]),x["city"])):
    for f in m["facilities"]:
        facility_page(f,m)
        facility_queue.append(BASE+fpath(f,m))
open("data/facility-indexing-queue.txt","w").write("\n".join(facility_queue)+"\n")

write_llms(matidx)
write_llms_full()
write_robots()
write_indexnow_key()
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>" for u,d in urls)+"</urlset>\n")
print(len(urls),"pages;",len(states),"states;",n,"facilities")
open(f"{OUT}/CNAME","w").write("tossmap.com\n"); open(f"{OUT}/.nojekyll","w").write("")
for _name in ("favicon.ico","favicon-32.png","apple-touch-icon.png"):
    shutil.copyfile(f"assets/{_name}", f"{OUT}/{_name}")
