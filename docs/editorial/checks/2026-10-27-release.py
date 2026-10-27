from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,subprocess,xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3]
base='5950147e35919117086f01e89931568527513ed1'
release=json.loads((root/'docs/editorial/release-2026-10-27.json').read_text())
rows=release['releases'];stamp=release['prepared_at']
assert datetime.fromisoformat(stamp)<=datetime.now(timezone.utc)
held=['idaho-911-shared-technology-local-operations','western-idaho-airborne-survey-rock-signals']
class Page(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.canonicals=[];self.links=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
  if t=='link' and a.get('rel')=='canonical':self.canonicals.append(a.get('href'))
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
def parse(path):
 s=(root/path).read_text();p=Page();p.feed(s)
 data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S).group(1))
 for link in p.links:
  u=urlsplit(link)
  if u.scheme or not u.path:continue
  target=root/unquote(u.path).lstrip('/') if u.path.startswith('/') else (root/path).parent/unquote(u.path)
  if target.is_dir():target/='index.html'
  assert target.exists(),(path,link)
 for tag in ['header','footer']:assert re.search(fr'<{tag}\b.*?</{tag}>',s,re.S).group(0)==(root/f'partials/{tag}.html').read_text().strip()
 return s,p,data
for row in rows:
 slug=row['slug'];s,p,data=parse(f'articles/{slug}.html')
 assert data['@type']=='NewsArticle' and data['datePublished']==stamp and data['dateModified']==stamp
 assert data['author']['@type']=='Organization' and data['author']['url'].endswith('#ai-assisted-publishing')
 assert p.canonicals==[row['url']] and p.meta['og:url']==row['url'] and 'noindex' not in p.meta['robots']
 assert p.meta['article:published_time']==stamp and f'datetime="{stamp}"' in s
 assert 'This draft' not in s and 'Release checks remain on hold' not in s
 assert 'creativeWorkStatus' not in data and 'No publication date assigned' not in s and '<title>Draft:' not in s
 for ratio,size in [('16x9',(1600,900)),('4x3',(1200,900)),('1x1',(1200,1200))]:assert Image.open(root/f'assets/articles/{slug}-{ratio}.png').size==size
 archived,ap,ad=parse(f'drafts/{slug}.html')
 original=subprocess.check_output(['git','show',f'{base}:drafts/{slug}.html'],cwd=root,text=True)
 assert archived.replace(row['archive_banner']+'\n','',1)==original
 assert 'noindex' in ap.meta['robots'] and not ap.canonicals and ad['creativeWorkStatus']=='Draft'
for slug in held:
 s,p,data=parse(f'drafts/{slug}.html');assert 'noindex' in p.meta['robots'] and not p.canonicals
 assert data['creativeWorkStatus']=='Draft' and not {'datePublished','dateModified','mainEntityOfPage'}&data.keys()
 for path in root.glob('*.html'):assert slug not in path.read_text()
 for name in ['feed.xml','sitemap.xml','news-sitemap.xml']:assert slug not in (root/name).read_text()
 paths=[f'drafts/{slug}.html']+[f'assets/articles/{slug}-{r}.png' for r in ['16x9','4x3','1x1']]
 subprocess.run(['git','diff','--exit-code',base,'--',*paths],cwd=root,check=True,stdout=subprocess.PIPE)
s,p,data=parse('articles/itd-north-idaho-certified-payroll-upload.html')
assert 'datePublished' not in data and 'article:published_time' not in p.meta
assert data['dateModified']==stamp and 'first public-serving date has not been independently established' in s and 'Those dates have passed' in s
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','n':'http://www.google.com/schemas/sitemap-news/0.9'}
news=ET.parse(root/'news-sitemap.xml').getroot();assert {u.findtext('s:loc',namespaces=ns) for u in news}=={r['url'] for r in rows}
assert all(u.findtext('n:news/n:publication_date',namespaces=ns)==stamp for u in news)
items=ET.parse(root/'feed.xml').getroot().findall('channel/item');byurl={x.findtext('link'):x for x in items}
old=ET.fromstring(subprocess.check_output(['git','show',f'{base}:feed.xml'],cwd=root)).findall('channel/item')
for item in old:
 current=byurl[item.findtext('link')];assert current.findtext('guid')==item.findtext('guid')
 if item.findtext('link').endswith('itd-north-idaho-certified-payroll-upload.html'):assert current.find('pubDate') is None
 else:assert current.findtext('pubDate')==item.findtext('pubDate')
for row in rows:
 for name in ['index.html','news.html','feed.xml','sitemap.xml','news-sitemap.xml']:assert row['slug'] in (root/name).read_text()
cases=[]
pages=[('software','/articles/inl-software-browser-access-licensing.html'),('court','/articles/idaho-court-ai-document-control.html'),('itd','/articles/itd-north-idaho-certified-payroll-upload.html'),('911-held','/drafts/'+held[0]+'.html'),('survey-held','/drafts/'+held[1]+'.html'),('software-archive','/drafts/inl-software-browser-access-licensing.html'),('court-archive','/drafts/idaho-court-ai-document-control.html'),('home','/'),('news','/news.html'),('ai-desk','/ai-automation.html'),('business-guide','/business-technology-baseline.html')]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(1440,1000)]:
  page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for name,path in pages:
   response=page.goto('http://127.0.0.1:5173'+path,wait_until='networkidle');assert response.status==200
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
   broken=page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)')
   assert not overflow and not broken and not errors,(name,width,overflow,broken,errors)
   assert page.locator('h1').count()==1
   if name in ['software','court','itd']:
    page.screenshot(path=f'/tmp/release27-{name}-top-{width}.png')
   if width<700:
    b=page.locator('.nav-toggle');b.click();assert b.get_attribute('aria-expanded')=='true' and page.locator('#primary-nav').is_visible()
    b.click();assert b.get_attribute('aria-expanded')=='false'
   cases.append({'page':name,'width':width,'height':height,'http':response.status,'overflow':overflow,'broken_images':broken,'page_errors':errors.copy()})
  page.close()
 browser.close()
record={'date_utc':'2026-10-27','release_stamp':stamp,'scope':'Local release and two remaining held drafts; remote/deployment/public evidence separate.','checks':{'two_production_metadata_discovery':True,'two_held_drafts_preserved':True,'two_archived_previews_preserved_except_banner':True,'old_rss_guids_dates_preserved_except_unverified_itd_date':True,'itd_provenance_clarified_without_new_first_date':True},'cases':cases}
(root/'docs/editorial/validation-2026-10-27-release.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS: two release articles, held/archive safeguards, honest ITD dates and 33 responsive cases')
