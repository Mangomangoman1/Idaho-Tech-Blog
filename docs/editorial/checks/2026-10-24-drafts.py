from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import json,re,sys,subprocess
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[3]
slugs=['inl-software-browser-access-licensing','idaho-court-ai-document-control','idaho-911-shared-technology-local-operations']
class Draft(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.canonical=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
for slug in slugs:
 relative=f'drafts/{slug}.html';s=(root/relative).read_text();d=Draft();d.feed(s)
 data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S).group(1))
 assert 'noindex' in d.meta['robots'] and not d.canonical
 assert data['@type']=='Article' and data['creativeWorkStatus']=='Draft' and data['author']['@type']=='Organization'
 assert not {'datePublished','dateModified','mainEntityOfPage'} & data.keys()
 assert not {'article:published_time','article:modified_time','og:url'} & d.meta.keys()
 assert '<time' not in s and 'Local editorial draft; not published' in s and 'Published:' not in s
 for link in d.links:
  u=urlsplit(link)
  if u.scheme or not u.path:continue
  target=root/unquote(u.path).lstrip('/') if u.path.startswith('/') else (root/relative).parent/unquote(u.path)
  if target.is_dir():target/='index.html'
  assert target.exists(),link
 for f in ['index.html','news.html','feed.xml','sitemap.xml','news-sitemap.xml']:assert slug not in (root/f).read_text(),(slug,f)
 for r,size in [('16x9',(1600,900)),('4x3',(1200,900)),('1x1',(1200,1200))]:assert Image.open(root/f'assets/articles/{slug}-{r}.png').size==size
 for tag in ['header','footer']:assert re.search(fr'<{tag}\b.*?</{tag}>',s,re.S).group(0)==(root/f'partials/{tag}.html').read_text().strip()
preserved=[f'drafts/{slug}.html' for slug in slugs]+[f'assets/articles/{slug}-{r}.png' for slug in slugs for r in ['16x9','4x3','1x1']]+['docs/research/2026-10-21-idaho-911-maintenance.md','docs/research/2026-10-22-idaho-court-ai-document-control.md','docs/editorial/checks/2026-10-21-draft.py','docs/editorial/checks/2026-10-22-drafts.py','docs/editorial/checks/2026-10-23-drafts.py','docs/research/2026-10-23-inl-software-access-licensing.md','articles','assets/articles','feed.xml','sitemap.xml','index.html','news.html']
preserved += [p.name for p in root.glob('*.html')] + ['assets','partials','scripts','robots.txt','vercel.json']
assert len(ET.fromstring((root/'news-sitemap.xml').read_text()))==0
subprocess.run(['git','diff','--exit-code','22fb648f6449b7bc698b44cdc516f4a6def8840f','--',*preserved],cwd=root,check=True,stdout=subprocess.PIPE)
cases=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(1440,1000)]:
  page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for name,path in [('software-draft',f'/drafts/{slugs[0]}.html'),('court-draft',f'/drafts/{slugs[1]}.html'),('911-draft',f'/drafts/{slugs[2]}.html'),('home','/'),('news','/news.html')]:
   response=page.goto('http://127.0.0.1:5173'+path,wait_until='networkidle');assert response.status==200
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
   broken=page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)')
   assert not overflow and not broken and not errors,(name,width,overflow,broken,errors)
   if name.endswith('draft'):
    assert page.locator('h1').count()==1 and page.locator('time').count()==0 and 'Draft:' in page.title()
    if name=='software-draft':
     page.screenshot(path=f'/tmp/oct24-full-{width}.png',full_page=True)
     page.screenshot(path=f'/tmp/oct24-top-{width}.png')
   else:
    for slug in slugs:assert page.locator(f'a[href*="{slug}"]').count()==0
   if width<700:
    b=page.locator('.nav-toggle');b.click();assert b.get_attribute('aria-expanded')=='true' and page.locator('#primary-nav').is_visible()
    b.click();assert b.get_attribute('aria-expanded')=='false'
   cases.append({'page':name,'width':width,'height':height,'http':response.status,'overflow':overflow,'broken_images':broken,'page_errors':errors.copy(),'mobile_menu':'passed' if width<700 else 'not_applicable'})
  page.close()
 browser.close()
record={'date':'2026-10-24','scope':'Local only; no remote GitHub/CI/deployment/public serving checks under owner hold.','draft_checks':{'all_three_undated_noindex':True,'discovery_exclusion':True,'local_links_images_jsonld_partials':True,'local_news_sitemap_empty':True,'preserved_all_three_and_production_articles_against_local_22fb648':True},'cases':cases}
(root/'docs/editorial/validation-2026-10-24.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS: three draft safeguards, preserved all three drafts/production articles and 15 responsive browser cases')
