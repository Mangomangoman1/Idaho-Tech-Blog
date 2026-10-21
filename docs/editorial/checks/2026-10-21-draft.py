from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import re,json
from PIL import Image
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[3];slug='idaho-911-shared-technology-local-operations';relative=f'drafts/{slug}.html'
s=(root/relative).read_text()
class Draft(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.canonical=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content','')
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  for k in ['href','src']:
   if k in a:self.links.append(a[k])
d=Draft();d.feed(s)
assert 'noindex' in d.meta['robots']
assert not d.canonical
data=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S).group(1))
assert data['@type']=='Article' and data['creativeWorkStatus']=='Draft' and data['author']['@type']=='Organization'
assert not {'datePublished','dateModified','mainEntityOfPage'} & data.keys()
assert not {'article:published_time','article:modified_time','og:url'} & d.meta.keys()
assert '<time' not in s and 'Local editorial draft; not published' in s
assert 'Published:' not in s
for link in d.links:
 u=urlsplit(link)
 if u.scheme or not u.path:continue
 target=root/unquote(u.path).lstrip('/') if u.path.startswith('/') else (root/relative).parent/unquote(u.path)
 if target.is_dir():target/='index.html'
 assert target.exists(),link
for f in ['index.html','news.html','feed.xml','sitemap.xml','news-sitemap.xml']:
 assert slug not in (root/f).read_text(),f
for r,size in [('16x9',(1600,900)),('4x3',(1200,900)),('1x1',(1200,1200))]:
 assert Image.open(root/f'assets/articles/{slug}-{r}.png').size==size
assert re.search(r'<header\b.*?</header>',s,re.S).group(0)==(root/'partials/header.html').read_text().strip()
assert re.search(r'<footer\b.*?</footer>',s,re.S).group(0)==(root/'partials/footer.html').read_text().strip()
cases=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for width,height in [(320,740),(390,844),(1440,1000)]:
  page=browser.new_page(viewport={'width':width,'height':height});errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  for name,path in [('draft','/'+relative),('home','/'),('news','/news.html')]:
   response=page.goto('http://127.0.0.1:5173'+path,wait_until='networkidle')
   assert response.status==200
   overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
   broken=page.locator('img').evaluate_all('(imgs)=>imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)')
   assert not overflow and not broken and not errors,(name,width,overflow,broken,errors)
   if name=='draft':
    assert page.locator('h1').count()==1
    assert 'Draft:' in page.title()
    assert page.locator('time').count()==0
    page.screenshot(path=f'/tmp/oct21-draft-full-{width}.png',full_page=True)
    page.screenshot(path=f'/tmp/oct21-draft-top-{width}.png')
   else:
    assert page.locator(f'a[href*="{slug}"]').count()==0
   if width<700:
    b=page.locator('.nav-toggle');b.click();assert b.get_attribute('aria-expanded')=='true' and page.locator('#primary-nav').is_visible()
    b.click();assert b.get_attribute('aria-expanded')=='false'
   cases.append({'page':name,'width':width,'height':height,'http':response.status,'overflow':overflow,'broken_images':broken,'page_errors':errors.copy(),'mobile_menu':'passed' if width<700 else 'not_applicable'})
  page.close()
 browser.close()
record={'date':'2026-10-21','scope':'Local only. No GitHub or deployment/public checks attempted under owner hold.','draft_checks':{'noindex':True,'status':'Draft','publication_dates_absent':True,'canonical_absent':True,'discovery_exclusion':True,'local_links':True,'shared_partials':True,'three_image_ratios':True},'cases':cases}
(root/'docs/editorial/validation-2026-10-21.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS: undated/noindex draft, metadata, local links/images/partials/discovery isolation and 9 responsive cases')
