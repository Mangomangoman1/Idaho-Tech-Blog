"""Render the homepage's generated parts from publication data.

- latest-articles: the bounded newest-first list (the rail beside the lead).
- lead-story: the newest homepage article, or the one carrying
  <meta name="stack:lead" content="pin">. When the lead block is present the
  rail leaves the lead out so a story never shows twice.
- desk: the two tracker tiles and the dated docket, read from the tracker data.

Only the latest-articles marker pair is required; the others render when present.
"""
from datetime import datetime, timezone, date
from html import escape
import ast
import json
import re
from news_sitemap import ROOT, Metadata, nodes

HOMEPAGE_OFF = '<meta name="stack:homepage" content="off">'
LEAD_PIN = '<meta name="stack:lead" content="pin">'
MARKER = re.compile(r'(<!-- latest-articles:start -->).*?(<!-- latest-articles:end -->)', re.S)
LEAD_MARKER = re.compile(r'(<!-- lead-story:start -->).*?(<!-- lead-story:end -->)', re.S)
DESK_MARKER = re.compile(r'(<!-- desk:start -->).*?(<!-- desk:end -->)', re.S)
SITE = 'https://www.idahostack.com'


def dated_articles():
    for path in sorted((ROOT / 'articles').glob('*.html')):
        html = path.read_text()
        if HOMEPAGE_OFF in html:
            continue  # quiet desk notes stay on News and RSS but off the homepage list
        metadata = Metadata()
        metadata.feed(html)
        for article in nodes(metadata.jsonld):
            types = article.get('@type', [])
            if isinstance(types, str):
                types = [types]
            if any(kind in types for kind in ['Article', 'NewsArticle', 'BlogPosting']):
                article = dict(article)
                article['_pinned'] = LEAD_PIN in html
                kicker = re.search(r'<p class="kicker">\s*(Desk note|Flagship)', html)
                article['_kind'] = kicker[1] if kicker else 'Report'
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


def display_date(stamp):
    return f'{stamp.strftime("%B")} {stamp.day}, {stamp.year}'


def tag(article):
    kind = article.get('_kind', 'Report')
    section = article.get('articleSection')
    return f'{kind} · {section}' if section else kind


def local_image(article):
    """The article's own 16:9 image as a site path, or None (never the generic share card)."""
    images = article.get('image') or []
    if isinstance(images, (str, dict)):
        images = [images]
    for image in images:
        url = image.get('url') if isinstance(image, dict) else image
        if not isinstance(url, str) or '16x9' not in url:
            continue
        path = url.replace(SITE, '')
        if path.startswith('/') and (ROOT / path.lstrip('/')).is_file():
            return path
    return None


def rail_row(stamp, path, article):
    return (f'<a href="/{escape(path, quote=True)}"><b class="tag">{escape(tag(article))}</b>'
            f'<span>{escape(article["headline"])}</span>'
            f'<small><time datetime="{escape(article["datePublished"], quote=True)}">{display_date(stamp)}</time>'
            f'<i class="dek"> · {escape(article.get("description", ""))}</i></small></a>')


def lead_block(stamp, path, article):
    href = f'/{escape(path, quote=True)}'
    image = local_image(article)
    figure = (f'<figure class="lead-figure"><img src="{escape(image, quote=True)}" alt="" width="1600" height="900" '
              f'fetchpriority="high"></figure>') if image else ''
    return (f'<article class="lead"><a class="lead-link" href="{href}">{figure}'
            f'<p class="kicker">{escape(tag(article))}</p>'
            f'<h2>{escape(article["headline"])}</h2>'
            f'<p>{escape(article.get("description", ""))}</p></a>'
            f'<p class="byline">The Idaho Stack · <time datetime="{escape(article["datePublished"], quote=True)}">'
            f'{display_date(stamp)}</time></p></article>')


def pick_lead(rows):
    pinned = [row for row in rows if row[2].get('_pinned')]
    return (pinned or rows or [None])[0]


def bead_status():
    source = (ROOT / 'scripts' / 'build_bead_tracker.py').read_text()
    match = re.search(r'^STATUS = (\{.*?^\})', source, re.S | re.M)
    return ast.literal_eval(match[1]) if match else {}


def datacenter_checked():
    source = (ROOT / 'scripts' / 'build_datacenter_tracker.py').read_text()
    match = re.search(r'^CHECKED = date\((\d+), (\d+), (\d+)\)', source, re.M)
    return date(*map(int, match.groups())) if match else None


def short_date(day):
    return f'{day.strftime("%B")} {day.day}'


def desk_block():
    data = ROOT / 'data' / 'datacenters'
    projects = json.loads((data / 'projects.json').read_text())
    power = json.loads((data / 'power.json').read_text())
    checked = datacenter_checked()
    bead = bead_status()
    tiles = []
    dc_checked = f'Checked {short_date(checked)}' if checked else 'Updated weekly'
    tiles.append(
        '<a class="tracker-tile" href="/datacenter-tracker.html"><p class="kicker">Live tracker</p>'
        '<h3>Idaho Data Center Tracker</h3>'
        '<p>Every data center proposed or built in Idaho: who is building, the power it wants, the tax break and the local rules.</p>'
        f'<div class="figures"><div><span class="figure-num">{len(projects)}</span><span class="figure-label">projects on the map</span></div>'
        f'<div><span class="figure-num">{power["pipeline_mw"]:,}</span><span class="figure-label">MW of large-load requests in Idaho Power’s queue</span></div></div>'
        f'<div class="tile-foot"><span class="checked">{escape(dc_checked)}</span><span class="go">Open tracker</span></div></a>')
    if bead:
        total = bead.get('program_total', '').replace(' million', 'M')
        tiles.append(
            '<a class="tracker-tile" href="/broadband-tracker.html"><p class="kicker">Live tracker</p>'
            '<h3>Idaho Broadband Tracker</h3>'
            '<p>Where Idaho’s federal BEAD broadband money stands: who holds it, who gave it back, and how far the projects have gotten.</p>'
            f'<div class="figures"><div><span class="figure-num">{escape(total)}</span><span class="figure-label">in Idaho’s BEAD program</span></div>'
            f'<div><span class="figure-num">{bead.get("signed_projects")}<small>/{bead.get("projects_awarded")}</small></span>'
            '<span class="figure-label">awarded projects with signed agreements</span></div></div>'
            f'<div class="tile-foot"><span class="checked">Checked {escape(bead.get("checked", "").rsplit(",", 1)[0])}</span>'
            '<span class="go">Open tracker</span></div></a>')
    items = []
    for item in sorted(power.get('upcoming', []), key=lambda row: row['date']):
        day = date.fromisoformat(item['date'])
        items.append(
            f'<li data-date="{day.isoformat()}"><time datetime="{day.isoformat()}"><b>{day.strftime("%b")}</b>'
            f'<span>{day.day}</span></time><div><a href="{escape(item["url"], quote=True)}">{escape(item["what"])}</a>'
            f'<span class="until">{day.strftime("%A")}, {short_date(day)}, {day.year}</span></div></li>')
    docket = ('<aside class="docket" aria-labelledby="docket-title"><p class="kicker">The docket</p>'
              '<h3 id="docket-title">Dates on the public record</h3>'
              f'<ol>{"".join(items)}</ol>'
              '<p class="docket-empty" hidden>No dated deadlines ahead right now.</p>'
              '<p class="docket-foot">From the <a href="/datacenter-tracker.html">data center tracker</a>.</p></aside>')
    return '<div class="desk-grid">' + ''.join(tiles) + docket + '</div>'


def render(html, articles=None, now=None):
    if len(MARKER.findall(html)) != 1:
        raise ValueError('Homepage needs exactly one latest-articles marker pair')
    now = now or datetime.now(timezone.utc)
    rows = latest_articles(dated_articles() if articles is None else articles, now, limit=7)
    if LEAD_MARKER.search(html):
        lead = pick_lead(rows)
        if lead:
            html = LEAD_MARKER.sub(lambda match: match[1] + lead_block(*lead) + match[2], html, count=1)
            rows = [row for row in rows if row is not lead]
        rows = rows[:6]
    else:
        rows = rows[:5]
    if DESK_MARKER.search(html):
        html = DESK_MARKER.sub(lambda match: match[1] + desk_block() + match[2], html, count=1)
    listing = '\n'.join(rail_row(*row) for row in rows)
    return MARKER.sub(lambda match: match[1] + '\n' + listing + '\n' + match[2], html)
