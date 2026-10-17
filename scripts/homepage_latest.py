"""Render the homepage's bounded newest-first article list from publication data."""
from datetime import datetime, timezone
from html import escape
import re
from news_sitemap import ROOT, Metadata, nodes

MARKER = re.compile(r'(<!-- latest-articles:start -->).*?(<!-- latest-articles:end -->)', re.S)


def dated_articles():
    for path in sorted((ROOT / 'articles').glob('*.html')):
        metadata = Metadata()
        metadata.feed(path.read_text())
        for article in nodes(metadata.jsonld):
            types = article.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if any(kind in types for kind in ['Article', 'NewsArticle', 'BlogPosting']):
                yield path.relative_to(ROOT).as_posix(), article


def latest_articles(articles, now, limit=5):
    dated = []
    for path, article in articles:
        if not article.get('datePublished'):
            continue
        stamp = datetime.fromisoformat(article['datePublished'].replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError(f'{path}: publication timestamp needs a timezone')
        if stamp <= now:
            dated.append((stamp, path, article))
    return sorted(dated, key=lambda row: (row[0], row[1]), reverse=True)[:limit]


def render(html, articles=None, now=None):
    if len(MARKER.findall(html)) != 1:
        raise ValueError('Homepage needs exactly one latest-articles marker pair')
    now = now or datetime.now(timezone.utc)
    rows = []
    for stamp, path, article in latest_articles(dated_articles() if articles is None else articles, now):
        display = f'{stamp.strftime("%B")} {stamp.day}, {stamp.year}'
        rows.append(f'<a href="/{escape(path, quote=True)}"><span>{escape(article["headline"])}</span>'
                    f'<small><time datetime="{escape(article["datePublished"], quote=True)}">{display}</time>'
                    f' · {escape(article.get("description", ""))}</small></a>')
    return MARKER.sub(lambda match: match[1] + '\n' + '\n'.join(rows) + '\n' + match[2], html)
