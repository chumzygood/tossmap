"""Offline regression checks; run after seed_data.py and build.py (stdlib only)."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from facility_questions import QUESTIONS, UNKNOWN

BASE='https://tossmap.com'
D=json.loads(Path('data/facilities.json').read_text())
slug=lambda s: re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def city_path(m): return f'/{slug(m["st"])}/{slug(m["city"])}/'
def facility_path(m,f): return city_path(m)+f['slug']+'/'
def norm(s): return ' '.join(s.split())
class Doc(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.jsonld=[]; self.visible=[]; self.script=None; self.buf=[]
        self.canonical=[]; self.h1=0; self.rows=0; self.ids=[]
        self.feed(text); self.close()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script': self.script=a.get('type','other'); self.buf=[]
        if tag=='a' and 'href' in a: self.links.append(a['href'])
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a['href'])
        if tag=='h1': self.h1+=1
        if tag=='tr': self.rows+=1
        if 'id' in a: self.ids.append(a['id'])
    def handle_endtag(self,tag):
        if tag=='script':
            if self.script=='application/ld+json': self.jsonld.append(json.loads(''.join(self.buf)))
            self.script=None
    def handle_data(self,data):
        if self.script is not None: self.buf.append(data)
        else: self.visible.append(data)

def read(path): return Doc(Path('docs'+path+'index.html').read_text())
class FacilityTests(unittest.TestCase):
    def test_seed_and_stable_unique_paths(self):
        paths=[]
        for m in D:
            for f in m['facilities']:
                paths.append(facility_path(m,f))
                self.assertEqual(set(f['questions']),{k for k,_ in QUESTIONS})
                self.assertRegex(f['slug'],r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
                for k,a in f['questions'].items():
                    self.assertIn(a['answer'],('yes','no',UNKNOWN))
                    if a['answer']!=UNKNOWN: self.assertTrue(a['evidence'],(f['name'],k))
        self.assertEqual(len(paths),213)
        self.assertEqual(len(set(paths)),len(paths))
    def test_all_facility_pages_and_visible_schema(self):
        sitemap={u.text for u in ET.parse('docs/sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
        queue=Path('data/facility-indexing-queue.txt').read_text().splitlines()
        llms=Path('docs/llms.txt').read_text()
        for m in D:
            city=read(city_path(m))
            for f in m['facilities']:
                p=facility_path(m,f); doc=read(p); text=norm(' '.join(doc.visible))
                self.assertEqual(doc.canonical,[BASE+p]); self.assertEqual(doc.h1,1)
                self.assertEqual(doc.rows,13); self.assertIn(p,city.links)
                self.assertIn(city_path(m),doc.links); self.assertIn(f['source'],doc.links)
                self.assertIn(f['address'],text); self.assertIn(f['operator'],text)
                self.assertIn(BASE+p,sitemap); self.assertIn(BASE+p,queue); self.assertIn(BASE+p,llms)
                self.assertEqual(len(doc.ids),len(set(doc.ids)))
                graph=doc.jsonld[0]['@graph']; place=next(x for x in graph if x['@type']=='Place')
                self.assertEqual(place['@id'],BASE+city_path(m)+'#'+slug(f['name']))
                self.assertEqual(place['url'],BASE+p)
                self.assertEqual(place['address']['@type'],'PostalAddress')
                faq=next(x for x in graph if x['@type']=='FAQPage')
                self.assertEqual(len(faq['mainEntity']),12)
                for qa in faq['mainEntity']:
                    self.assertIn(norm(qa['name']),text)
                    self.assertIn(norm(qa['acceptedAnswer']['text']),text)
                for other in m['facilities']:
                    if other is not f: self.assertIn(facility_path(m,other),doc.links)
                for ms,key in [('paint','paint'),('tires','tires'),('e-waste','e_waste'),('batteries','batteries'),('motor-oil','motor_oil'),('household-chemicals','household_chemicals')]:
                    if f['questions'][key]['answer']=='yes':
                        anchor=f'/{ms}/#{slug(m["city"])}-{slug(m["st"])}'
                        self.assertIn(anchor,doc.links); self.assertIn(anchor.split('#')[1],read(f'/{ms}/').ids)
        self.assertEqual(len(queue),213); self.assertEqual(len(set(queue)),213)
        self.assertTrue(queue[0].startswith(BASE+'/va/richmond/'))
        self.assertEqual(len(sitemap),310)
    def test_state_pages_itemlist_matches_city_links(self):
        states={}
        for m in D: states.setdefault(m['st'],[]).append(m)
        for st,ms in states.items():
            doc=read(f'/{slug(st)}/'); graph=doc.jsonld[0]['@graph']
            il=next(x for x in graph if x['@type']=='ItemList')
            self.assertEqual(il['numberOfItems'],len(ms))
            self.assertEqual([x['url'] for x in il['itemListElement']],[BASE+city_path(m) for m in ms])
            for m in ms:
                self.assertIn(city_path(m),doc.links)
                for f in m['facilities']:
                    self.assertIn(facility_path(m,f),doc.links)
            self.assertTrue(any(x['@type']=='CollectionPage' for x in graph))
    def test_city_pages_itemlist_matches_facility_cards(self):
        for m in D:
            if not m['facilities']: continue
            doc=read(city_path(m)); graph=doc.jsonld[0]['@graph']
            cp=next(x for x in graph if x['@type']=='CollectionPage')
            il=next(x for x in graph if x['@type']=='ItemList')
            self.assertEqual(cp['mainEntity']['@id'],il['@id'])
            self.assertEqual(il['numberOfItems'],len(m['facilities']))
            self.assertEqual([x['url'] for x in il['itemListElement']],[BASE+facility_path(m,f) for f in m['facilities']])
            for f in m['facilities']: self.assertIn(facility_path(m,f),doc.links)
    def test_material_links_match_explicit_answers(self):
        for path,key in [('paint','paint'),('tires','tires'),('e-waste','e_waste'),('batteries','batteries'),('motor-oil','motor_oil'),('household-chemicals','household_chemicals')]:
            mat=read('/'+path+'/')
            for m in D:
                for f in m['facilities']:
                    p=facility_path(m,f)
                    if f['questions'][key]['answer']=='yes':
                        self.assertIn(p,mat.links); self.assertIn('/'+path+'/',read(p).links)
                    else: self.assertNotIn(p,mat.links)
    def test_every_html_internal_link_and_jsonld(self):
        for path in Path('docs').rglob('*.html'):
            doc=Doc(path.read_text())
            for href in doc.links:
                u=urlsplit(href)
                if u.scheme or u.netloc: continue
                if not u.path.startswith('/'): continue
                target=Path('docs'+unquote(u.path))
                if u.path.endswith('/'): target=target/'index.html'
                self.assertTrue(target.exists(),f'{path}: broken link {href}')
    def test_material_hub_seo_uses_live_counts(self):
        def count(key):
            n=sum(1 for m in D for f in m['facilities'] if f['questions'][key]['answer']=='yes')
            metros=sum(1 for m in D if any(f['questions'][key]['answer']=='yes' for f in m['facilities']))
            return n,metros
        tn,tm=count('tires'); hn,hm=count('household_chemicals')
        tires=Path('docs/tires/index.html').read_text()
        hhw=Path('docs/household-chemicals/index.html').read_text()
        home=Path('docs/index.html').read_text()
        self.assertIn(f'<title>Tire disposal near me: {tn} official drop-off sites in {tm} metros | TossMap</title>',tires)
        self.assertIn('<h1>Tire disposal near you: official drop-off sites by city</h1>',tires)
        self.assertIn(f'content="Tire disposal near you: {tn} official drop-off sites in {tm} US metros, with addresses, hours, tire limits, fees and a source link for every listing."',tires)
        self.assertIn('<h2>Where is tire disposal near me?</h2>',tires)
        self.assertIn(f'TossMap lists {tn} official drop-off sites in {tm} US metro areas that list tires as accepted.',tires)
        self.assertIn(f'<title>Household hazardous waste disposal near me: {hn} sites by city | TossMap</title>',hhw)
        self.assertIn('<h1>Household hazardous waste disposal near you</h1>',hhw)
        self.assertIn(f'content="Household hazardous waste (HHW) disposal near you: {hn} official drop-off sites in {hm} US metros, with hours, limits and source links."',hhw)
        self.assertIn('metros, addresses, hours, fees and source links, checked regularly.',home)
        self.assertNotIn('metros—addresses',home)
    def test_home_links_upcoming_and_recent_listings(self):
        import datetime
        home=read('/'); text=norm(''.join(home.visible)); today=datetime.date.today().isoformat()
        latest=max(f['checked'] for m in D for f in m['facilities'])
        for m in D:
            for f in m['facilities']:
                mm=re.search(r'(?:Event:\s*|Collection days:\s*|next:\s*)(?:(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+)?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(?:[–-]\d{1,2})?,\s*(20\d{2})',f['hours'])
                if mm:
                    d=datetime.date(int(mm.group(3)),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].index(mm.group(1))+1,int(mm.group(2))).isoformat()
                    if d>=today: self.assertIn(facility_path(m,f),home.links,f['name'])
        self.assertIn('Upcoming collection days',text); self.assertIn('Recently added or re-checked',text)
        self.assertTrue(any(facility_path(m,f) in home.links for m in D for f in m['facilities'] if f['checked']==latest))
    def test_past_one_day_events_have_no_event_schema_and_say_so(self):
        import datetime
        today=datetime.date.today().isoformat(); months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        for m in D:
            for f in m['facilities']:
                mm=re.search(r'Event:\s*(?:Sat|Sun|Mon|Tue|Wed|Thu|Fri)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),\s*(20\d{2})',f['hours'])
                if not mm: continue
                d=datetime.date(int(mm.group(3)),months.index(mm.group(1))+1,int(mm.group(2))).isoformat()
                html_text=Path('docs'+facility_path(m,f)+'index.html').read_text()
                if d<today:
                    self.assertNotIn('"@type": "Event"',html_text,f['name']); self.assertIn('Past event:',html_text,f['name'])
                else:
                    self.assertIn('"@type": "Event"',html_text,f['name']); self.assertNotIn('Past event:',html_text,f['name'])
    def test_suggest_fix_mailto_includes_page_path(self):
        from urllib.parse import quote
        samples=['/','/oh/','/oh/cleveland/']
        m=next(x for x in D if x['city']=='Cleveland')
        fac=facility_path(m,m['facilities'][0])
        samples.append(fac)
        for path in samples:
            href='mailto:toolshed@mail.grokbot.com?subject='+quote(f'TossMap fix: {path}', safe='')
            doc=read(path)
            self.assertIn(href, doc.links, path)
            html=Path('docs'+path+'index.html').read_text()
            self.assertIn('Suggest a fix or leave a review', html)
        html=Path('docs'+fac+'index.html').read_text()
        self.assertIn('Is this info wrong? Suggest a fix', html)
        self.assertGreaterEqual(read(fac).links.count('mailto:toolshed@mail.grokbot.com?subject='+quote(f'TossMap fix: {fac}', safe='')), 2)
    def test_robots_allows_ai_crawlers_and_keeps_sitemap(self):
        text=Path('docs/robots.txt').read_text()
        self.assertIn('User-agent: *\nAllow: /', text)
        for bot in ('GPTBot','ChatGPT-User','OAI-SearchBot','ClaudeBot','Claude-SearchBot','Claude-User','PerplexityBot','Google-Extended'):
            self.assertIn(f'User-agent: {bot}\nAllow: /', text)
        self.assertIn('Sitemap: https://tossmap.com/sitemap.xml', text)

    def test_llms_intro_and_full_listings(self):
        llms=Path('docs/llms.txt').read_text()
        full=Path('docs/llms-full.txt').read_text()
        n=sum(len(m['facilities']) for m in D)
        self.assertIn(f'{n} drop-off sites', llms)
        self.assertIn(f'across {len(D)} US metro areas', llms)
        self.assertIn('https://tossmap.com/llms-full.txt', llms)
        self.assertRegex(llms.split('##',1)[0], r'verified against an official government or facility-operator source')
        self.assertIn('last-checked date', llms.split('##',1)[0])
        for m in D:
            for f in m['facilities']:
                self.assertIn(f['name'], full)
                self.assertIn(f['source'], full)
                self.assertIn(BASE+facility_path(m,f), full)
                self.assertIn(f"Last checked: {f['checked']}", full)

    def test_indexnow_key_file_is_published(self):
        key=Path('data/indexnow-key.txt').read_text().strip()
        self.assertRegex(key, r'^[A-Fa-f0-9]{32}$')
        self.assertEqual(Path('docs/'+key+'.txt').read_text().strip(), key)

    def test_direct_answer_lines_use_verified_fields(self):
        for m in D:
            city=Path('docs'+city_path(m)+'index.html').read_text()
            self.assertIn('<p class="lead">', city, city_path(m))
            if m['facilities']:
                self.assertIn(m['facilities'][0]['name'], city)
                self.assertIn(m['facilities'][0]['source'], city)
            for f in m['facilities']:
                p=facility_path(m,f)
                html=Path('docs'+p+'index.html').read_text()
                self.assertIn('<p class="lead">', html, p)
                self.assertIn(f['name'], html)
                self.assertIn(f['source'], html)
                # Lead sits immediately after H1 and uses only known fields.
                lead=re.search(r'<h1>.*?</h1><p class="lead">(.*?)</p>', html, re.S).group(1)
                visible=unescape(re.sub(r'<[^>]+>','',lead))
                hours=(f.get('hours') or '').strip().rstrip(' .')
                if hours:
                    self.assertIn(hours, visible, p)
                else:
                    self.assertNotIn('hours not listed', visible.lower())
                fees=(f.get('fees') or '').strip()
                if not fees:
                    self.assertNotRegex(visible, r', not listed\.?$', p)
                    self.assertNotIn(', Free.', visible, p)
                else:
                    fee_text=fees.rstrip(' .')
                    simple=re.match(r'(?i)^free(\s+(?:for|with)\s+.{1,40})$', fee_text)
                    if re.fullmatch(r'free', fee_text, re.I):
                        self.assertIn("and it's free", visible, p)
                        self.assertNotIn(', Free', visible, p)
                    elif simple and not re.search(r'[;:$]', fee_text):
                        self.assertIn("and it's free"+simple.group(1), visible, p)
                        self.assertNotIn(', Free', visible, p)
                    else:
                        self.assertIn(fee_text, visible, p)
                        self.assertNotRegex(visible, r', Free\.', p)
                self.assertNotIn('None', visible)
                self.assertNotIn(UNKNOWN, visible)
                self.assertNotIn('[', visible, p)
                self.assertNotIn('[', lead, p)
                a=re.search(r'Source: <a href="([^"]+)"[^>]*>([^<]+)</a>', lead)
                self.assertIsNotNone(a, p)
                self.assertEqual(unescape(a.group(1)), f['source'], p)
                host=urlsplit(f['source']).netloc.lower()
                if host.startswith('www.'):
                    host=host[4:]
                self.assertEqual(unescape(a.group(2)), host, p)
                # Do not place a site in the metro core city when the address is elsewhere.
                loc=re.search(r',\s*([^,]+),\s*([A-Z]{2})(?:\s+\d{5}(?:-\d{4})?)?\s*$', (f.get('address') or '').strip())
                if loc:
                    city_from_addr=loc.group(1).strip()
                    if city_from_addr.lower()!=m['city'].lower() and m['city'].lower() not in city_from_addr.lower():
                        self.assertNotIn(f"in {m['city']}, {m['st']}", visible, p)

    def test_known_rejection_and_conditional_cases(self):
        facilities={f['name']:f for m in D for f in m['facilities']}
        self.assertEqual(facilities['Keʻehi Transfer Station']['questions']['tires']['answer'],'no')
        self.assertEqual(facilities['Cuyahoga County Solid Waste District HQ (electronics drop-off bins)']['questions']['batteries']['answer'],'no')
        self.assertEqual(facilities['Residential Drop-Off Center – North']['questions']['e_waste']['answer'],UNKNOWN)
        self.assertEqual(facilities['Metro Central Hazardous Waste']['questions']['businesses_accepted']['answer'],'yes')
        self.assertIn('fire damage',facilities['North Wake HHW Facility']['source_notice'])
        self.assertEqual(facilities['ERG Environmental Services (Wayne County HHW)']['questions']['appointment_required']['answer'],'yes')
        self.assertEqual(facilities['New Kent County Main Refuse Site (Route 618)']['questions']['tires']['answer'],'no')
        self.assertEqual(facilities['Sheldon Road HHW Collection Center']['questions']['e_waste']['answer'],'no')
        self.assertEqual(facilities['Prince George County Convenience Center']['questions']['paint']['answer'],'no')

if __name__=='__main__': unittest.main(verbosity=2)
