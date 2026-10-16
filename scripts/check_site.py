"""Offline publishing checks. These do not certify facts or Google eligibility."""
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys
import xml.etree.ElementTree as ET
from news_sitemap import Metadata, nodes, SITE, SM, NEWS

ROOT = Path(__file__).resolve().parents[1]
fail = []

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals, self.links, self.meta = [], [], {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta':
            self.meta[attrs.get('name', attrs.get('property'))] = attrs.get('content')
        for key in ['href', 'src']:
            if key in attrs:
                self.links.append(attrs[key])

article_dates = {}
for path in [*ROOT.glob('*.html'), *(ROOT / 'articles').glob('*.html')]:
    name = path.relative_to(ROOT).as_posix()
    html = path.read_text()
    page = Page()
    page.feed(html)
    if '<title>' not in html or not page.meta.get('description'):
        fail.append(f'{name}: missing title/description')
    if len(page.canonicals) != 1 or not page.canonicals[0].startswith(SITE + '/'):
        fail.append(f'{name}: expected one canonical on {SITE}')
    if len(re.findall(r'<h1\b', html)) != 1:
        fail.append(f'{name}: expected one h1')
    if page.meta.get('ai-access') is None:
        fail.append(f'{name}: missing ai-access meta')
    for link in page.links:
        url = urlsplit(link)
        if url.scheme and url.netloc not in ['www.idahostack.com', 'idahostack.com']:
            continue
        if url.scheme in ['mailto', 'tel', 'data', 'javascript'] or not url.path:
            continue
        target = (ROOT / unquote(url.path).lstrip('/')) if url.path.startswith('/') else (path.parent / unquote(url.path))
        if target.is_dir():
            target /= 'index.html'
        if not target.is_file():
            fail.append(f'{name}: broken local link {link}')
    try:
        metadata = Metadata()
        metadata.feed(html)
        for node in nodes(metadata.jsonld):
            if node.get('datePublished') and node.get('@type') in ['Article', 'NewsArticle', 'BlogPosting']:
                published = datetime.fromisoformat(node['datePublished'].replace('Z', '+00:00'))
                modified = datetime.fromisoformat(node.get('dateModified', node['datePublished']).replace('Z', '+00:00'))
                if published.tzinfo is None or modified.tzinfo is None or modified < published or published > datetime.now(timezone.utc):
                    fail.append(f'{name}: invalid publication/modification timestamp')
                article_dates[SITE + '/' + name] = node['datePublished']
    except (ValueError, TypeError) as exc:
        fail.append(f'{name}: invalid JSON-LD or date: {exc}')

for required in ['robots.txt', 'sitemap.xml', 'news-sitemap.xml', 'feed.xml', 'llms.txt', 'assets/styles.css']:
    if not (ROOT / required).is_file():
        fail.append(f'missing {required}')

try:
    ns = {'s': SM, 'n': NEWS}
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    locations = [u.findtext('s:loc', namespaces=ns) for u in sitemap.getroot()]
    if len(set(locations)) != len(locations):
        fail.append('sitemap.xml: duplicate URLs')
    feed = ET.parse(ROOT / 'feed.xml')
    items = feed.getroot().findall('channel/item')
    guids = [item.findtext('guid') for item in items]
    if len(set(guids)) != len(guids):
        fail.append('feed.xml: duplicate GUIDs')
    feed_links = {item.findtext('link') for item in items}
    for path in (ROOT / 'articles').glob('*.html'):
        url = SITE + '/' + path.relative_to(ROOT).as_posix()
        if url not in locations or url not in feed_links:
            fail.append(f'{path.name}: missing from sitemap or RSS')
    for url in ET.parse(ROOT / 'news-sitemap.xml').getroot():
        loc = url.findtext('s:loc', namespaces=ns)
        stamp = url.findtext('n:news/n:publication_date', namespaces=ns)
        if article_dates.get(loc) != stamp:
            fail.append(f'news-sitemap.xml: publication mismatch: {loc}')
except (ET.ParseError, OSError) as exc:
    fail.append(f'discovery XML: {exc}')

print('PASS: pages, local links, JSON-LD, article dates, sitemap and RSS' if not fail else '\n'.join(fail))
sys.exit(bool(fail))
