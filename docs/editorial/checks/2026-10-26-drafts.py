from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import json,re,subprocess
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3]
baseline='45e96d89c2af9fc80fc3690e44f869dccaf72c28'
slugs=['western-idaho-airborne-survey-rock-signals','inl-software-browser-access-licensing','idaho-court-ai-document-control','idaho-911-shared-technology-local-operations']
class Draft(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.canonical=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
discovery=list(root.glob('*.html'))+[root/f for f in ['feed.xml','sitemap.xml','news-sitemap.xml']]
for slug in slugs:
 relative=f'drafts/{slug}.html';s=(root/relative).read_text();d=Draft();d.feed(s)
 data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S).group(1))
 assert 'noindex' in d.meta['robots'] and not d.canonical
 assert data['@type']=='Article' and data['creativeWorkStatus']=='Draft' and data['author']['@type']=='Organization'
 assert data['author']['url'].endswith('/about.html#ai-assisted-publishing')
 assert not {'datePublished','dateModified','mainEntityOfPage'} & data.keys()
 assert not {'article:published_time','article:modified_time','og:url'} & d.meta.keys()
 assert '<time' not in s and 'Local editorial draft; not published' in s and 'Published:' not in s
 assert re.search(r'<h1>(.*?)</h1>',s,re.S).group(1)==data['headline']
 for link in d.links:
  u=urlsplit(link)
  if u.scheme or not u.path:continue
  target=root/unquote(u.path).lstrip('/') if u.path.startswith('/') else (root/relative).parent/unquote(u.path)
  if target.is_dir():target/='index.html'
  assert target.exists(),link
 for f in discovery:assert slug not in f.read_text(),(slug,f)
 for ratio,size in [('16x9',(1600,900)),('4x3',(1200,900)),('1x1',(1200,1200))]:
  assert Image.open(root/f'assets/articles/{slug}-{ratio}.png').size==size
 for tag in ['header','footer']:
  assert re.search(fr'<{tag}\b.*?</{tag}>',s,re.S).group(0)==(root/f'partials/{tag}.html').read_text().strip()
assert len(ET.fromstring((root/'news-sitemap.xml').read_text()))==0
# Compare only files tracked in the starting commit; allow the new draft's assets.
trees=['assets','articles','partials','scripts','robots.txt','vercel.json','feed.xml','sitemap.xml','news-sitemap.xml','docs/research','docs/editorial/checks']
trees += [p.name for p in root.glob('*.html')]
preserved=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline,'--',*trees],cwd=root,text=True).splitlines()
preserved += [f'drafts/{slug}.html' for slug in slugs[1:]]
subprocess.run(['git','diff','--exit-code',baseline,'--',*preserved],cwd=root,check=True,stdout=subprocess.PIPE)
cases=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(1440,1000)]:
  page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  paths=[('survey-draft',f'/drafts/{slugs[0]}.html'),('software-draft',f'/drafts/{slugs[1]}.html'),('court-draft',f'/drafts/{slugs[2]}.html'),('911-draft',f'/drafts/{slugs[3]}.html'),('home','/'),('news','/news.html')]
  for name,path in paths:
   response=page.goto('http://127.0.0.1:5173'+path,wait_until='networkidle');assert response.status==200
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
   broken=page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)')
   assert not overflow and not broken and not errors,(name,width,overflow,broken,errors)
   if name.endswith('draft'):
    assert page.locator('h1').count()==1 and page.locator('time').count()==0 and 'Draft:' in page.title()
    if name=='survey-draft':
     page.screenshot(path=f'/tmp/oct26-full-{width}.png',full_page=True)
     page.screenshot(path=f'/tmp/oct26-top-{width}.png')
   else:
    for slug in slugs:assert page.locator(f'a[href*="{slug}"]').count()==0
   if width<700:
    b=page.locator('.nav-toggle');b.click();assert b.get_attribute('aria-expanded')=='true' and page.locator('#primary-nav').is_visible()
    b.click();assert b.get_attribute('aria-expanded')=='false'
   cases.append({'page':name,'width':width,'height':height,'http':response.status,'overflow':overflow,'broken_images':broken,'page_errors':errors.copy(),'mobile_menu':'passed' if width<700 else 'not_applicable'})
  page.close()
 browser.close()
record={'date':'2026-10-26','scope':'Local only; no remote GitHub/CI/deployment/public serving checks under owner hold.','draft_checks':{'all_four_undated_noindex':True,'all_root_discovery_exclusion':True,'local_links_images_jsonld_partials':True,'local_news_sitemap_empty':True,'preserved_three_prior_drafts_and_tracked_production_files_against_local_45e96d8':True},'cases':cases}
(root/'docs/editorial/validation-2026-10-26.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS: four draft safeguards, three prior drafts/production preserved and 18 responsive browser cases')
