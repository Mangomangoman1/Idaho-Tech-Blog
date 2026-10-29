from pathlib import Path
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,subprocess,xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3]
base='743fbd012fd6a2f465efb21c3cf7fe4edbdf2dd7'
release=json.loads((root/'docs/editorial/release-2026-10-29-rural-health.json').read_text())
slug=release['slug'];stamp=release['publication_stamp'];url=release['url']
class Page(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.canonicals=[];self.links=[];self.alts=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
  if t=='link' and a.get('rel')=='canonical':self.canonicals.append(a.get('href'))
  if t=='img':self.alts.append(a.get('alt'))
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
s=(root/f'articles/{slug}.html').read_text();p=Page();p.feed(s)
data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S).group(1))
assert data['@type']=='NewsArticle' and data['datePublished']==stamp and data['dateModified']==stamp
assert datetime.fromisoformat(stamp)<=datetime.now(timezone.utc)
assert p.canonicals==[url] and p.meta['og:url']==url and 'noindex' not in p.meta['robots']
assert data['author']['@type']=='Organization' and data['author']['url'].endswith('#ai-assisted-publishing')
assert re.search(r'<h1>(.*?)</h1>',s,re.S).group(1)==data['headline']
assert 'This draft' not in s and 'Release checks remain on hold' not in s
assert f'datetime="{stamp}"' in s and p.meta['article:published_time']==stamp
assert all(a is not None for a in p.alts)
for link in p.links:
 u=urlsplit(link)
 if u.scheme or not u.path:continue
 target=root/unquote(u.path).lstrip('/') if u.path.startswith('/') else (root/'articles')/unquote(u.path)
 if target.is_dir():target/='index.html'
 assert target.exists(),link
for tag in ['header','footer']:assert re.search(fr'<{tag}\b.*?</{tag}>',s,re.S).group(0)==(root/f'partials/{tag}.html').read_text().strip()
for r,size in [('16x9',(1600,900)),('4x3',(1200,900)),('1x1',(1200,1200))]:assert Image.open(root/f'assets/articles/{slug}-{r}.png').size==size
for name in ['index.html','news.html','ai-automation.html','feed.xml','sitemap.xml','news-sitemap.xml']:assert slug in (root/name).read_text()
oldfiles=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'--','articles','assets','drafts/idaho-911-shared-technology-local-operations.html','drafts/western-idaho-airborne-survey-rock-signals.html','docs/research/2026-10-24-ammon-gift-service-boundary.md'],cwd=root,text=True).splitlines()
subprocess.run(['git','diff','--exit-code',base,'--',*oldfiles],cwd=root,check=True,stdout=subprocess.PIPE)
items=ET.parse(root/'feed.xml').getroot().findall('channel/item');byurl={i.findtext('link'):i for i in items}
old=ET.fromstring(subprocess.check_output(['git','show',f'{base}:feed.xml'],cwd=root)).findall('channel/item')
for item in old:
 current=byurl[item.findtext('link')];assert current.findtext('guid')==item.findtext('guid') and current.findtext('pubDate')==item.findtext('pubDate')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','n':'http://www.google.com/schemas/sitemap-news/0.9'}
news=ET.parse(root/'news-sitemap.xml').getroot();assert len(news)==2
assert any(u.findtext('s:loc',namespaces=ns)==url and u.findtext('n:news/n:publication_date',namespaces=ns)==stamp for u in news)
held=['idaho-911-shared-technology-local-operations','western-idaho-airborne-survey-rock-signals']
for name in ['index.html','news.html','feed.xml','sitemap.xml','news-sitemap.xml']:
 for h in held:assert h not in (root/name).read_text()
cases=[]
with sync_playwright() as playwright:
 browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(1440,1000)]:
  page=browser.new_page(viewport={'width':width,'height':height});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for name,path in [('health',f'/articles/{slug}.html'),('home','/'),('news','/news.html'),('desk','/ai-automation.html')]:
   response=page.goto('http://127.0.0.1:5173'+path,wait_until='networkidle');assert response.status==200
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
   broken=page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)')
   assert not overflow and not broken and not errors,(name,width,overflow,broken,errors)
   assert page.locator('h1').count()==1
   if name=='health':
    assert page.locator('h2').count()>=5 and page.locator('.story-figure img').count()==1
    page.screenshot(path=f'/tmp/rural-health-top-{width}.png')
    page.screenshot(path=f'/tmp/rural-health-full-{width}.png',full_page=True)
    page.locator('.story-figure').screenshot(path=f'/tmp/rural-health-figure-{width}.png')
   if width<700:
    b=page.locator('.nav-toggle');b.click();assert b.get_attribute('aria-expanded')=='true' and page.locator('#primary-nav').is_visible();b.click();assert b.get_attribute('aria-expanded')=='false'
   cases.append({'page':name,'width':width,'height':height,'http':response.status,'overflow':overflow,'broken_images':broken,'page_errors':errors.copy()})
  page.close()
 browser.close()
record={'date':'2026-10-29','scope':'New rural-health technology article and changed home/news/desk only; prior fraud article independently public-verified by parent.','publication_stamp':stamp,'checks':{'article_metadata_links_images_partials':True,'rss_previous_dates_guids_preserved':True,'all_prior_articles_assets_held_drafts_unchanged':True,'held_drafts_excluded':True,'news_sitemap_two_recent_articles':True},'cases':cases}
(root/'docs/editorial/validation-2026-10-29-rural-health.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS: new article/discovery, prior-work preservation and 12 responsive cases')
