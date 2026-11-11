"""Offline regression checks; run after seed_data.py and build.py (stdlib only)."""
import json
import re
import unittest
import xml.etree.ElementTree as ET
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
        self.assertEqual(len(paths),121)
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
        self.assertEqual(len(queue),121); self.assertEqual(len(set(queue)),121)
        self.assertTrue(queue[0].startswith(BASE+'/va/richmond/'))
        self.assertEqual(len(sitemap),218)
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
    def test_known_rejection_and_conditional_cases(self):
        facilities={f['name']:f for m in D for f in m['facilities']}
        self.assertEqual(facilities['Keʻehi Transfer Station']['questions']['tires']['answer'],'no')
        self.assertEqual(facilities['Cuyahoga County Solid Waste District HQ (electronics drop-off bins)']['questions']['batteries']['answer'],'no')
        self.assertEqual(facilities['Residential Drop-Off Center – North']['questions']['e_waste']['answer'],UNKNOWN)
        self.assertEqual(facilities['Metro Central Hazardous Waste']['questions']['businesses_accepted']['answer'],'yes')
        self.assertIn('fire damage',facilities['North Wake HHW Facility']['source_notice'])
        self.assertEqual(facilities['ERG Environmental Services (Wayne County HHW)']['questions']['appointment_required']['answer'],'yes')

if __name__=='__main__': unittest.main(verbosity=2)
