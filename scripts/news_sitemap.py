#!/usr/bin/env python3
"""Build the optional Google News sitemap from genuine article publication dates.

Run during each daily editorial session, even when no new piece meets standards.
A static deployment cannot expire itself: an unattended gap requires a rebuild.
"""
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.idahostack.com"
SM = "http://www.sitemaps.org/schemas/sitemap/0.9"
NEWS = "http://www.google.com/schemas/sitemap-news/0.9"


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.jsonld = []
        self.block = None

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self.block = []

    def handle_data(self, data):
        if self.block is not None:
            self.block.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.block is not None:
            self.jsonld.append(json.loads("".join(self.block)))
            self.block = None


def nodes(value):
    if isinstance(value, list):
        for item in value:
            yield from nodes(item)
    elif isinstance(value, dict):
        yield value
        yield from nodes(value.get("@graph", []))


def recent_articles(articles, now):
    for path, article in articles:
        published = article.get("datePublished")
        if not published:
            continue
        stamp = datetime.fromisoformat(published.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError(f"{path}: publication timestamp needs a timezone")
        if now - timedelta(days=2) < stamp <= now:
            yield path, article


def render(now=None):
    now = now or datetime.now(timezone.utc)
    articles = []
    for path in sorted((ROOT / "articles").glob("*.html")):
        metadata = Metadata()
        metadata.feed(path.read_text())
        for node in nodes(metadata.jsonld):
            types = node.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if "NewsArticle" in types:
                articles.append((path.relative_to(ROOT).as_posix(), node))
    ET.register_namespace("", SM)
    ET.register_namespace("news", NEWS)
    root = ET.Element(f"{{{SM}}}urlset")
    for path, article in recent_articles(articles, now):
        url = ET.SubElement(root, f"{{{SM}}}url")
        ET.SubElement(url, f"{{{SM}}}loc").text = f"{SITE}/{path}"
        news = ET.SubElement(url, f"{{{NEWS}}}news")
        pub = ET.SubElement(news, f"{{{NEWS}}}publication")
        ET.SubElement(pub, f"{{{NEWS}}}name").text = "The Idaho Stack"
        ET.SubElement(pub, f"{{{NEWS}}}language").text = "en"
        ET.SubElement(news, f"{{{NEWS}}}publication_date").text = article["datePublished"]
        ET.SubElement(news, f"{{{NEWS}}}title").text = article["headline"]
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode") + "\n"


if __name__ == "__main__":
    (ROOT / "news-sitemap.xml").write_text(render())
