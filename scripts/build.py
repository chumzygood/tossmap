import json,html,re,os,datetime
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
ul.grid{columns:3 200px;padding-left:18px}.note{background:#fff7e0;border-left:4px solid #e0b030;padding:10px 14px}.tags a{display:inline-block;margin:0 8px 6px 0}
.signup{background:#fff;border:1px solid #dfe5e0;border-radius:8px;padding:16px;margin:14px 0}
.signup h2{margin:0 0 6px;font-size:1.15em}.signup p{margin:0 0 10px}
.signup-form{display:flex;flex-wrap:wrap;gap:8px;align-items:flex-end;margin:10px 0}
.signup-form label{flex:1 1 100%;font-size:14px}
.signup-form input[type=email]{flex:1 1 220px;font:inherit;padding:8px 10px;border:1px solid #c5d0ca;border-radius:6px}
.signup-form button{font:inherit;padding:8px 14px;border:0;border-radius:6px;background:#1f4d3a;color:#fff;cursor:pointer}
.signup .meta{margin:0}
.questions{width:100%;border-collapse:collapse;background:#fff}.questions th,.questions td{padding:12px;border:1px solid #dfe5e0;text-align:left;vertical-align:top;overflow-wrap:anywhere}.questions th{width:30%}dd{margin:0 0 12px}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #ad5700;outline-offset:3px}@media(max-width:600px){.questions,.questions tbody,.questions tr,.questions th,.questions td{display:block;width:100%}.questions thead{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}.questions th{padding-bottom:4px;border-bottom:0}.questions td{padding-top:4px;border-top:0;margin-bottom:8px}} .answers h2{font-size:1.15em;margin:1.15em 0 6px}.answers p{margin:0 0 12px}"""
open(f"{OUT}/style.css","w").write(CSS)
GC='<meta name="google-site-verification" content="jAhRn0yYvjC37jRpBEzda-xllydn360g3kgkVonTDKA" /><script data-goatcounter="https://tossmap.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
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
def page(path,title,desc,body,graph=(),checked=None):
    urls.append((path,checked or STATIC_LASTMOD)); p=f"{OUT}{path}"+("index.html" if path.endswith("/") else "")
    os.makedirs(os.path.dirname(p),exist_ok=True)
    ld=ldscript({"@context":"https://schema.org","@graph":list(graph)}) if graph else ""
    foot=f"Data from official government and operator sources{', checked '+checked if checked else ''}. Always confirm with the source before driving."
    open(p,"w").write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:type" content="website"><meta property="og:site_name" content="TossMap">
<link rel="stylesheet" href="/style.css">{ld}
{GC}</head><body><header><a href="/"><strong>TossMap</strong></a> · where to toss hazardous waste, paint, e-waste &amp; tires · <a href="/newsletter/">Newsletter</a></header><main>{body}</main>
<footer>{foot} · <a href="/newsletter/">Newsletter</a> · <a href="/privacy.html">Privacy</a> · <a href="/embed/">Embed widget</a> · <a href="/for-cities/">For cities</a> · <a href="/partners/">Partners</a> · <a href="mailto:toolshed@mail.grokbot.com">Support</a></footer></body></html>""")
states={}
for m in D: states.setdefault((m["state"],m["st"]),[]).append(m)
cpath=lambda m:f"/{slug(m['st'])}/{slug(m['city'])}/"
fpath=lambda f,m:cpath(m)+f["slug"]+"/"

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
    if standing and not events:
        n=len(standing)
        parts.append(f"TossMap lists {n} official drop-off site{'s' if n!=1 else ''} in {city}, {st}.")
        parts.append(f"Listed materials include {mat_list}.")
    elif events and not standing:
        parts.append(f"TossMap does not list a permanent drop-off site in {city}, {st}.")
        for f in events:
            parts.append(f'The official source lists {f["name"]} at {f["address"]}. Hours recorded: {f["hours"]}.')
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
            sent+=f" Recorded hours: {hrs}. This is a scheduled event, not a permanent drop-off site."
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
    html_out='<section class="answers">'+" ".join(f"<h2>{e(q)}</h2><p>{h}</p>" for q,h,_ in qas)+"</section>"
    faq={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":p}} for q,_,p in qas]}
    return html_out, faq

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
    spec=opening_hours_spec(f["hours"])
    if spec: place["openingHoursSpecification"]=spec
    elif f.get("hours"):
        place["description"]=place["description"]+". Hours: "+f["hours"]
    return drop_empty(place)

def city_qas(m, have):
    qas=[city_overview_qa(m)]
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

def material_page_qas(s, n, nsites, nmetros):
    low=n.split(" (")[0].lower()
    lead_q=f"Where can I drop off {low} near you?"
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
    lines=["# TossMap","",
           "> TossMap is an independent directory of waste and recycling drop-off options in US cities, using government and facility-operator sources. It does not operate the listed facilities.","",
           f"Listings include accepted materials, addresses, hours, fees, eligibility notes, source links and last-checked dates where available. {n} drop-off sites are listed across {len(D)} US metros. Rules and hours can change. Confirm with the linked operator before driving; a listing does not guarantee acceptance, availability or free service. Do not treat household waste listings as permission to bring commercial waste.","",
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
    lines += ["","## Optional",f"- [Privacy]({BASE}/privacy.html)",f"- [Newsletter]({BASE}/newsletter/): local drop-off updates",""]
    open(f"{OUT}/llms.txt","w").write("\n".join(lines))

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
{'<p class="note">'+e(f['source_notice'])+'</p>' if f.get('source_notice') else ''}{'<p class="tags">'+tags+'</p>' if tags else ''}<div class="meta">Source: <a href="{e(f['source'])}" rel="nofollow noopener">{e(f['source'])}</a> · Last checked {f['checked']}</div></div>"""
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
    body=(vis+f'<h1>{e(f["name"])}</h1><p>Waste and recycling drop-off information for {e(m["city"])}, {e(m["st"])}. This is an independent source-backed listing, not the operator’s website.</p>'
          +(f'<p class="note">{e(f["source_notice"])}</p>' if f.get("source_notice") else "")
          +'<section class="card"><h2>Before you go</h2><dl>'
          +''.join(f'<dt><strong>{e(label)}</strong></dt><dd>{e(value or UNKNOWN)}</dd>' for label,value in [
              ("Operator",f["operator"]),("Full address",f["address"]),("Accepted materials",f["accepts"]),
              ("Hours / collection schedule",f["hours"]),("Fees",f["fees"]),("Eligibility, ID and other notes",f["notes"])])
          +f'</dl><p><a href="{e(f["source"])}" rel="noopener">Official source and current rules</a> · Last checked {e(f["checked"])}</p></section>'
          +f'<h2>Common questions</h2><p class="meta">Question set reviewed {e(f.get("questions_reviewed",f["checked"]))}.</p><p>Yes and no apply only to the material types, users and conditions in the accompanying evidence. A fee answer of no means the listed service is free under those conditions; it does not waive eligibility rules. “Not stated by source” means no explicit answer is recorded in our source-backed listing, not that the source has no further information. Check the official source before driving.</p>'
          +'<table class="questions"><caption>Facility requirements and material acceptance</caption><thead><tr><th scope="col">Question</th><th scope="col">Answer and source-backed detail</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table>'
          +(f'<h2>Browse accepted materials</h2><p>{materials}</p>' if materials else '')
          +f'<p><a href="{cpath(m)}">All drop-off options in {e(m["city"])}</a></p>'
          +('<h2>Other facilities in this city directory</h2><ul>'+''.join(f'<li><a href="{fpath(o,m)}">{e(o["name"])}</a> — {e(o["address"])}</li>' for o in others)+'</ul>' if others else '<p>No other facilities are currently listed in this city directory. Follow the city link above for local guidance.</p>')
          +'<p class="note">Use the exact acceptance notes above: paint types, battery types, item limits and event dates matter. Do not mix chemicals or assume a material is accepted because a similar item is listed. Confirm availability with the operator.</p>')
    place=facility_place(f,m)
    webpage={"@type":"WebPage","@id":BASE+fp+"#page","url":BASE+fp,"name":f["name"],"mainEntity":{"@id":place["@id"]},"publisher":{"@id":ORG_ID},"citation":f["source"],"dateModified":f["checked"],"isPartOf":{"@id":BASE+"/#website"}}
    # Many facility names are generic ("Waste Reduction Center"), so the city goes in the title.
    ttl=f'{f["name"]}, {m["city"]} {m["st"]}: hours & rules | TossMap'
    if m["city"].lower() in f["name"].lower(): ttl=f'{f["name"]} ({m["st"]}): hours, materials & rules | TossMap'
    mnames=[n.split(" (")[0].lower() for _,n,_ in mats(f)]
    takes=f' Takes {and_list(mnames)}.' if mnames else ''
    page(fp,ttl,
         f'{f["name"]} {"in" if m["city"].lower() in f["address"].lower() else "in the"} {m["city"]}, {m["st"]}{"" if m["city"].lower() in f["address"].lower() else " area"}: address, hours, fees, eligibility and official source.{takes} Last checked {f["checked"]}.',
         body,[bl,webpage,place,{"@type":"FAQPage","mainEntity":entities}],f["checked"])

def and_list(xs): return ", ".join(xs[:-1])+" and "+xs[-1] if len(xs)>1 else "".join(xs)
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
        h1=f'Where to dump hazardous waste, paint & e-waste in {m["city"]}, {st}'
        body=(vis+f'<h1>Where to dump hazardous waste, paint &amp; e-waste in {e(m["city"])}, {st}</h1>'+note+ans_html
              +"".join(fac(f,m) for f in fs)+("<p>No permanent drop-off site listed yet. See the note above for event-based or alternate official options, and check back after the next source review.</p>" if not fs else "")
              +(f'<h2>By material</h2><p class="tags">'+" ".join(f'<a href="/{s}/">{e(n)} drop-off</a>' for s,n in have)+"</p>" if have else "")
              +f'<p class="meta">Run a local site? <a href="/embed/">Embed this list for free</a>.</p>'+(f'<h2>Other cities in {e(sn)}</h2><ul>'+"".join(f'<li><a href="{cpath(o)}">{e(o["city"])}</a></li>' for o in nearby)+"</ul>" if nearby else "")
              +signup_box())
        short={"Electronics (e-waste)":"e-waste","Household chemicals":"chemicals"}
        tl=[short.get(n,n).lower() for _,n in have if n!="Household chemicals"][:3]
        title=f"Where to dump {', '.join(tl[:-1])+' & '+tl[-1] if len(tl)>1 else (tl[0] if tl else 'hazardous waste')} in {m['city']}, {st} | TossMap"
        what=", ".join(n.split(" (")[0].lower() for _,n in have[:4]) or "household hazardous waste"
        desc=(f"{plural(len(fs),'official drop-off site')} in {m['city']}, {st} for {what}: addresses, hours, fees and source links, last checked {chk}." if fs
              else f"How {m['city']}, {st} handles household hazardous waste, from official sources.")
        collection={"@type":"CollectionPage","@id":BASE+cp+"#page","url":BASE+cp,"name":h1,"publisher":{"@id":ORG_ID}}
        cites=unique_sources(fs)
        if cites: collection["citation"]=[{"@type":"WebPage","url":u} for u in cites]
        graph=[bl,collection]+[ldj(f,m) for f in fs]+([faq] if faq else [])
        page(cp,title,desc,body,graph,chk)
    vis,bl=crumbs([("Home","/"),(sn,sp)])
    nst=sum(len(m["facilities"]) for m in ms)
    def state_li(m):
        mh=[(s,n) for s,n,_ in MAT if m in matidx[s]]
        return (f'<li><a href="{cpath(m)}">{e(m["city"])}</a> ({plural(len(m["facilities"]),"site")})'
                +(' — '+", ".join(f'<a href="/{s}/">{e(n.split(" (")[0].lower())}</a>' for s,n in mh) if mh else "")+"</li>")
    page(sp,f"Hazardous waste, paint & e-waste drop-off in {sn} | TossMap",
         f"{plural(nst,'official drop-off site')} in {sn} ({', '.join(m['city'] for m in ms)}) for {and_list([n.split(" (")[0].lower() for s,n,_ in MAT if any(m in matidx[s] for m in ms)]) or "household hazardous waste"}, with source links.",
         vis+f'<h1>Hazardous waste drop-off in {e(sn)}</h1><p>{plural(nst,"official drop-off site")} across {plural(len(ms),"metro area")} in {e(sn)}. Each city page lists addresses, hours, fees, eligibility rules and a link to the official source, with the date we last checked it.</p><ul>'+"".join(state_li(m) for m in ms)+"</ul>",[bl],
         max([f["checked"] for m in ms for f in m["facilities"]],default=None))
for s,n,_ in MAT:
    ms=sorted(matidx[s],key=lambda x:x["city"]); low=n.split(" (")[0].lower()
    vis,bl=crumbs([("Home","/"),(n,f"/{s}/")])
    hits=[(m,[f for f in m["facilities"] if any(x[0]==s for x in mats(f))]) for m in ms]
    nsites=sum(len(fs) for _,fs in hits)
    ans_html,faq=faq_block(material_page_qas(s,n,nsites,len(ms)))
    body=(vis+f"<h1>Where to drop off {e(low)} near you</h1><p>{plural(nsites,'official drop-off site')} in {plural(len(ms),'metro area')} list {e(low)} as accepted. Rules, limits and residency requirements vary, so check each listing's source link before you go.</p>"
      +ans_html
      +"<ul class=grid>"+"".join(f'<li><a href="#{slug(m["city"])}-{slug(m["st"])}">{e(m["city"])}, {m["st"]}</a></li>' for m in ms)+"</ul>"
      +"".join(f'<h2 id="{slug(m["city"])}-{slug(m["st"])}">{e(low.capitalize())} drop-off in <a href="{cpath(m)}">{e(m["city"])}, {m["st"]}</a></h2><ul>'
               +"".join(f'<li><a href="{fpath(f,m)}">{e(f["name"])}</a> — {e(f["address"])}<span class="meta"> · checked {f["checked"]}</span></li>' for f in fs)+"</ul>" for m,fs in hits)
      +"<p>Other materials: "+" · ".join(f'<a href="/{o}/">{e(on)}</a>' for o,on,_ in MAT if o!=s)+"</p>"
      +signup_box())
    il={"@type":"ItemList","name":f"{n} drop-off sites by city","numberOfItems":nsites,"itemListElement":[{"@type":"ListItem","position":k+1,"name":f'{f["name"]} ({m["city"]}, {m["st"]})',"url":f'{BASE}{fpath(f,m)}'} for k,(m,f) in enumerate((m,f) for m,fs in hits for f in fs)]}
    collection={"@type":"CollectionPage","@id":BASE+f"/{s}/#page","url":BASE+f"/{s}/","name":f"Where to drop off {low} near you","publisher":{"@id":ORG_ID}}
    graph=[bl,collection,il]+([faq] if faq else [])
    page(f"/{s}/",f"Where to recycle or dispose of {low}: {nsites} drop-off sites by city | TossMap",f"{plural(nsites,'official '+low+' drop-off location')} in {len(ms)} US metro areas, with addresses, hours, limits and source links.",body,graph,
         max([f["checked"] for _,fs in hits for f in fs],default=None))
n=sum(len(m["facilities"]) for m in D)
home=(f"<h1>Where do I take paint, chemicals, batteries, electronics &amp; tires?</h1><p>{n} drop-off sites from official government and operator sources across {len(D)} US metros. Every listing links to its source and shows when we last checked it.</p>"
 "<h2>By material</h2><p class=tags>"+" ".join(f'<a href="/{s}/">{e(nm)}</a>' for s,nm,_ in MAT)+"</p>"
 "<h2>By city</h2><ul class=grid>"+"".join(f'<li><a href="{cpath(m)}">{e(m["city"])}, {m["st"]}</a></li>' for m in sorted(D,key=lambda x:x["city"]))+"</ul><h2>By state</h2><ul class=grid>"+"".join(f'<li><a href="/{slug(st)}/">{e(sn)}</a></li>' for sn,st in sorted(states))+"</ul>"+signup_box())
page("/","TossMap: where to dump paint, hazardous waste, e-waste & tires by city","Find official drop-off sites for paint, chemicals, batteries, electronics and tires in 50+ US metros—addresses, hours, fees and source links, checked regularly.",home,
     [{"@type":"Organization","@id":ORG_ID,"name":"TossMap","url":BASE+"/"},{"@type":"WebSite","@id":BASE+"/#website","name":"TossMap","url":BASE+"/","publisher":{"@id":ORG_ID}}],max(f["checked"] for m in D for f in m["facilities"]))
page("/privacy.html","Privacy | TossMap","TossMap privacy policy: no cookies on our pages; newsletter sign-ups are handled by Kit and we do not sell your email.","<h1>Privacy</h1><p>TossMap sets no cookies. We use GoatCounter, a privacy-friendly analytics service that does not track individuals.</p><p>If you sign up for the <a href=\"/newsletter/\">TossMap newsletter</a>, your email is collected by Kit, our email provider, so we can send drop-off updates. We do not sell your email. Kit will send a confirmation email first, and you can unsubscribe anytime.</p><p>If ads are added, ad partners may use cookies; this page will be updated before that happens.</p><p>Listings come from public government sources and may change; confirm with the source before visiting.</p>")
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
open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>" for u,d in urls)+"</urlset>\n")
print(len(urls),"pages;",len(states),"states;",n,"facilities")
open(f"{OUT}/CNAME","w").write("tossmap.com\n"); open(f"{OUT}/.nojekyll","w").write("")
