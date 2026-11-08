#!/usr/bin/env python3
"""Builds datacenter-tracker.html from data/datacenters/*.json.

Weekly update: refresh projects.json, rules.json and power.json from the newest
public records (bump each changed row's "as_of"), update CHECKED below, then
run this script and `npm run build`.

The script also writes data/datacenters/idaho-data-center-projects.csv, the
download offered on the page.
"""
import csv
import html
import json
import math
import pathlib
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "datacenters"
OUT = ROOT / "datacenter-tracker.html"
CSV_OUT = DATA / "idaho-data-center-projects.csv"
SITE = "https://www.idahostack.com"

CHECKED = date(2026, 11, 8)

projects = json.loads((DATA / "projects.json").read_text())
rules = json.loads((DATA / "rules.json").read_text())
power = json.loads((DATA / "power.json").read_text())

# Status vocabulary. Order is the order the filter chips and legend use.
STATUS = {
    "operating": ("Operating", "s-op"),
    "construction": ("Under construction", "s-build"),
    "approved": ("Approved", "s-ok"),
    "proposed": ("Proposed", "s-prop"),
    "paused": ("On hold", "s-hold"),
    "contested": ("Denied, contested", "s-deny"),
    "denied": ("Denied", "s-deny"),
}

# Idaho's outline (public-domain US Census-derived state boundary, simplified).
IDAHO = [[-116.048, 49.0], [-116.048, 47.976], [-115.724, 47.697], [-115.719, 47.423], [-115.527, 47.302], [-115.325, 47.259], [-115.303, 47.187], [-114.93, 46.919], [-114.886, 46.809], [-114.624, 46.705], [-114.613, 46.64], [-114.322, 46.645], [-114.465, 46.273], [-114.492, 46.037], [-114.388, 45.884], [-114.569, 45.774], [-114.498, 45.67], [-114.547, 45.561], [-114.333, 45.457], [-114.087, 45.594], [-113.988, 45.703], [-113.807, 45.605], [-113.835, 45.522], [-113.736, 45.331], [-113.572, 45.128], [-113.451, 45.057], [-113.457, 44.865], [-113.342, 44.783], [-113.134, 44.772], [-113.002, 44.449], [-112.887, 44.394], [-112.783, 44.487], [-112.471, 44.482], [-112.241, 44.569], [-112.104, 44.52], [-111.869, 44.564], [-111.819, 44.509], [-111.617, 44.547], [-111.387, 44.756], [-111.228, 44.58], [-111.047, 44.476], [-111.047, 42.001], [-112.164, 41.995], [-114.043, 41.995], [-117.028, 42.001], [-117.028, 43.83], [-116.896, 44.159], [-116.979, 44.241], [-117.17, 44.257], [-117.241, 44.394], [-117.039, 44.75], [-116.935, 44.783], [-116.831, 44.931], [-116.847, 45.024], [-116.732, 45.144], [-116.672, 45.32], [-116.464, 45.615], [-116.546, 45.752], [-116.781, 45.824], [-116.918, 45.993], [-116.924, 46.169], [-117.055, 46.344], [-117.039, 46.426], [-117.044, 47.762], [-117.033, 49.0]]
# Reference towns for orientation (approximate city-centre coordinates) and label side.
TOWNS = [("Coeur d’Alene", -116.78, 47.68, "r"), ("Lewiston", -117.02, 46.42, "b"), ("Idaho Falls", -112.03, 43.49, "r"),
         ("Twin Falls", -114.46, 42.56, "l")]
# Treasure Valley zoom: projects inside this box are drawn in an inset.
TV = (-116.70, -115.55, 43.00, 43.72)  # lon min, lon max, lat min, lat max
TV_TOWNS = [("Boise", -116.20, 43.615, "r"), ("Nampa", -116.56, 43.54, "b"), ("Kuna", -116.42, 43.49, "l"),
            ("Mountain Home", -115.69, 43.13, "l")]
K = 100
COS = math.cos(math.radians(45.5))
PAD = 14


def xy(lon, lat):
    return ((lon + 117.30) * COS * K + PAD, (49.05 - lat) * K + PAD)


def esc(s):
    return html.escape(str(s), quote=True)


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return f"{d:%b} {d.day}, {d.year}"


def money(v):
    v = float(v)
    if v >= 1e9:
        return f"${v / 1e9:,.1f}B".replace(".0B", "B")
    if v >= 1e6:
        return f"${v / 1e6:,.0f}M"
    return f"${v:,.0f}"


def src_links(srcs):
    return "".join(
        f'<li><a href="{esc(s["url"])}">{esc(s["label"])}</a><span>{esc(s["date"])}</span></li>' for s in srcs
    )


def cite(url, label="source"):
    return f'<a class="cite" href="{esc(url)}">{esc(label)}</a>'


# ---------- numbers ----------
n_projects = len(projects)
by_status = {k: [p for p in projects if p["status"] == k] for k in STATUS}
active = [p for p in projects if p["status"] not in ("denied",)]
mw_rows = [p for p in projects if p.get("mw")]
mw_total = sum(p["mw"] for p in mw_rows)
usd_rows = [p for p in projects if p.get("investment_usd")]
usd_total = sum(p["investment_usd"] for p in usd_rows)
n_rules = len(rules)
deadline = next((e for e in power["events"] if e.get("deadline")), None)

# ---------- map ----------
outline = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in (xy(*p) for p in IDAHO)) + " Z"
w = (-111.0 + 117.30) * COS * K + PAD * 2
h = (49.05 - 41.95) * K + PAD * 2

# Inset geometry: top-right corner of the canvas, which Idaho's shape leaves empty.
K2 = 300
IX, IY = 214.0, 14.0
IW = (TV[1] - TV[0]) * COS * K2
IH = (TV[3] - TV[2]) * K2


def ixy(lon, lat):
    return (IX + (lon - TV[0]) * COS * K2, IY + (TV[3] - lat) * K2)


def in_tv(p):
    return TV[0] <= p["lon"] <= TV[1] and TV[2] <= p["lat"] <= TV[3]


def town_label(n, x, y, side, cls="dc-town", gap=6):
    # gap keeps a label clear of any pin drawn on top of the town's dot
    tx, ty, anchor = {"r": (x + gap, y + 4, "start"), "l": (x - gap, y + 4, "end"),
                      "b": (x, y + 9 + gap, "middle"), "t": (x, y - gap, "middle")}[side]
    return (f'<g class="{cls}"><circle cx="{x:.1f}" cy="{y:.1f}" r="2.6"/>'
            f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}">{esc(n)}</text></g>')


def pin(i, p, x, y, r):
    label, cls = STATUS[p["status"]]
    return (f'<a href="#p-{esc(p["id"])}" class="dc-pin {cls}" data-status="{esc(p["status"])}" aria-label="{i}. {esc(p["name"])}, {esc(p["place"])}: {esc(label)}">'
            f'<circle class="dc-halo" cx="{x:.1f}" cy="{y:.1f}" r="{r + 5}"/><circle class="dc-disc" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
            f'<text x="{x:.1f}" y="{y + 4.5:.1f}">{i}</text></a>')


towns = "".join(town_label(n, *xy(lo, la), side) for n, lo, la, side in TOWNS)
# Treasure Valley box on the main map, joined to the inset.
bx0, by0 = xy(TV[0], TV[3])
bx1, by1 = xy(TV[1], TV[2])
tv_box = (f'<rect class="dc-tvbox" x="{bx0:.1f}" y="{by0:.1f}" width="{bx1 - bx0:.1f}" height="{by1 - by0:.1f}" rx="4"/>'
          f'<path class="dc-tvlink" d="M{bx1:.1f},{by0:.1f} C{bx1 + 60:.1f},{by0 - 120:.1f} {IX - 40:.1f},{IY + IH + 60:.1f} {IX:.1f},{IY + IH:.1f}"/>')
pins, inset_pins, dots = [], [], []
for i, p in enumerate(projects, 1):
    if in_tv(p):
        x, y = xy(p["lon"], p["lat"])
        dots.append(f'<circle class="dc-mini {STATUS[p["status"]][1]}" cx="{x:.1f}" cy="{y:.1f}" r="3.2"/>')
        x0, y0 = ixy(p["lon"], p["lat"])
        dx, dy = p.get("nudge", [0, 0])
        lead = f'<line class="dc-lead {STATUS[p["status"]][1]}" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0 + dx:.1f}" y2="{y0 + dy:.1f}"/>' if (dx or dy) else ""
        inset_pins.append(lead + pin(i, p, x0 + dx, y0 + dy, 12))
    else:
        x, y = xy(p["lon"], p["lat"])
        dx, dy = p.get("nudge", [0, 0])
        pins.append(pin(i, p, x + dx, y + dy, 13))
inset_towns = "".join(town_label(n, *ixy(lo, la), side, "dc-town dc-town-s", 19) for n, lo, la, side in TV_TOWNS)
inset = (f'<g class="dc-inset"><rect class="dc-inset-bg" x="{IX:.1f}" y="{IY:.1f}" width="{IW:.1f}" height="{IH:.1f}" rx="12"/>'
         f'<text class="dc-inset-t" x="{IX + 14:.1f}" y="{IY + IH - 14:.1f}">TREASURE VALLEY</text>'
         f'{inset_towns}{"".join(inset_pins)}</g>')
map_svg = f"""<svg class="dc-map" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-labelledby="dc-map-t">
<title id="dc-map-t">Map of Idaho showing {n_projects} data center projects by status, with a close-up of the Treasure Valley</title>
<defs><pattern id="dc-grid" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="rgba(31,38,35,.06)"/></pattern></defs>
<path class="dc-state" d="{outline}"/><path d="{outline}" fill="url(#dc-grid)"/>
{towns}{tv_box}{''.join(dots)}{''.join(pins)}{inset}</svg>"""

legend = "".join(
    f'<li><span class="dc-dot {cls}"></span>{esc(label)}<b>{len(by_status[k])}</b></li>'
    for k, (label, cls) in STATUS.items() if by_status[k]
)
chips = '<button type="button" class="dc-chip is-on" data-f="all" aria-pressed="true">All <b>' + str(n_projects) + "</b></button>" + "".join(
    f'<button type="button" class="dc-chip" data-f="{k}" aria-pressed="false">{esc(label)} <b>{len(by_status[k])}</b></button>'
    for k, (label, cls) in STATUS.items() if by_status[k]
)

# ---------- project cards ----------


def fact(label, value):
    return f"<div><dt>{esc(label)}</dt><dd>{value}</dd></div>" if value else ""


cards = []
for i, p in enumerate(projects, 1):
    label, cls = STATUS[p["status"]]
    size_bits = []
    if p.get("mw"):
        size_bits.append(f'{p["mw"]:,} MW')
    if p.get("size_note"):
        size_bits.append(esc(p["size_note"]))
    size = " · ".join(size_bits) or '<span class="dc-unk">Not disclosed</span>'
    invest = money(p["investment_usd"]) if p.get("investment_usd") else '<span class="dc-unk">Not disclosed</span>'
    if p.get("investment_note"):
        invest += f' <span class="dc-sub">{esc(p["investment_note"])}</span>'
    rows = "".join(
        f'<div class="dc-row"><dt>{esc(k)}</dt><dd>{v}</dd></div>'
        for k, v in (("Status", p["status_note"]), ("Tax break", p["tax"]), ("Power", p["power"]),
                     ("Water", p["water"]), ("Local rules", p["local"]))
        if v
    )
    unconf = f'<p class="dc-flag">Unconfirmed: {p["unconfirmed"]}</p>' if p.get("unconfirmed") else ""
    cards.append(f"""
<article class="dc-card" id="p-{esc(p['id'])}" data-status="{esc(p['status'])}">
  <header class="dc-card-head"><span class="dc-num {cls}">{i}</span><div><p class="dc-place">{esc(p['place'])} · {esc(p['county'])} County</p><h3>{esc(p['name'])}</h3></div></header>
  <p class="dc-status"><span class="dc-pill {cls}">{esc(label)}</span><span class="dc-asof">Last change {fmt_date(p['as_of'])}</span></p>
  <dl class="dc-facts">{fact('Developer', esc(p['developer']))}{fact('Size', size)}{fact('Investment', invest)}</dl>
  <dl class="dc-rows">{rows}</dl>{unconf}
  <details class="dc-src"><summary>Sources ({len(p['sources'])})</summary><ul class="bt-list">{src_links(p['sources'])}</ul></details>
</article>""")

# ---------- power timeline ----------
timeline = "".join(
    f'<li class="dc-ev{" dc-ev-due" if e.get("deadline") else ""}{" dc-ev-past" if date.fromisoformat(e["date"]) <= CHECKED and not e.get("deadline") else ""}">'
    f'<time datetime="{e["date"]}">{fmt_date(e["date"])}</time><p class="dc-ev-t">{esc(e["title"])}</p><p class="dc-ev-n">{e["note"]} {cite(e["url"])}</p></li>'
    for e in sorted(power["events"], key=lambda e: e["date"])
)

# ---------- local rules ----------
rule_rows = "".join(
    f'<tr><th scope="row">{esc(r["place"])}</th><td><span class="dc-pill {r["cls"]}">{esc(r["kind"])}</span></td>'
    f'<td>{r["summary"]}</td><td class="num">{fmt_date(r["date"])}</td><td>{cite(r["url"])}</td></tr>'
    for r in sorted(rules, key=lambda r: r["date"], reverse=True)
)
rules_table = f"""<div class="table-wrap"><table class="baseline-table bt-table dc-rules">
<caption>City and county actions on data centers, newest first</caption>
<thead><tr><th scope="col">Where</th><th scope="col">Action</th><th scope="col">What it does</th><th scope="col" class="num">Date</th><th scope="col">Record</th></tr></thead>
<tbody>{rule_rows}</tbody></table></div>"""

# ---------- sources & downloads ----------
all_src = {}
for p in projects:
    for s in p["sources"]:
        all_src.setdefault(s["url"], s)
for e in power["events"]:
    all_src.setdefault(e["url"], {"label": e["title"], "url": e["url"], "date": fmt_date(e["date"])})
for r in rules:
    all_src.setdefault(r["url"], {"label": f'{r["place"]}: {r["kind"]}', "url": r["url"], "date": fmt_date(r["date"])})

with CSV_OUT.open("w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["id", "name", "place", "county", "developer", "status", "status_as_of", "mw", "investment_usd",
                 "size_note", "tax_break", "power", "water", "local_rules", "unconfirmed", "sources"])
    for p in projects:
        strip = lambda s: html.unescape(__import__("re").sub(r"<[^>]+>", "", s or ""))
        wr.writerow([p["id"], p["name"], p["place"], p["county"], p["developer"], STATUS[p["status"]][0], p["as_of"],
                     p.get("mw") or "", p.get("investment_usd") or "", p.get("size_note", ""), strip(p["tax"]),
                     strip(p["power"]), strip(p["water"]), strip(p["local"]), strip(p.get("unconfirmed", "")),
                     " | ".join(s["url"] for s in p["sources"])])

title = "Idaho Data Center Tracker: Every Project, Power Deal and Local Rule | The Idaho Stack"
og_title = "Idaho Data Center Tracker"
desc = (f"Every data center proposed or built in Idaho: {n_projects} projects, who is building them, how much power they want, "
        f"the sales tax break, and the city and county rules. Sourced and updated weekly.")
canonical = f"{SITE}/datacenter-tracker.html"
jsonld = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "Idaho Data Center Tracker",
    "description": desc,
    "url": canonical,
    "dateModified": CHECKED.isoformat(),
    "keywords": ["Idaho data centers", "Idaho Power large load", "IPC-E-26-07", "Idaho Code 63-3622VV", "data center moratorium"],
    "spatialCoverage": {"@type": "Place", "name": "Idaho"},
    "isAccessibleForFree": True,
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "creator": {"@type": "Organization", "name": "The Idaho Stack", "url": SITE + "/"},
    "isBasedOn": list(all_src)[:40],
    "distribution": [{"@type": "DataDownload", "name": "Idaho data center projects", "encodingFormat": "text/csv",
                      "contentUrl": f"{SITE}/data/datacenters/{CSV_OUT.name}"}],
}

stat_mw = (f'<div class="bt-stat"><span class="bt-num">{power["pipeline_mw"]:,} MW</span><p>{power["pipeline_stat"]} '
           f'{cite(power["pipeline_url"])}</p></div>')
groups = [("operating", "operating"), ("construction", "under construction"), ("approved", "approved"), ("proposed", "proposed"),
          ("paused", "on hold"), ("contested", "denied and in court"), ("denied", "denied")]
bits = [f"{len(by_status[k])} {w}" for k, w in groups if by_status[k]]
breakdown = ", ".join(bits[:-1]) + " and " + bits[-1] if len(bits) > 1 else bits[0]
stats = f"""<div class="bt-stats">
  <div class="bt-stat"><span class="bt-num">{n_projects}</span><p>data center projects on the public record in Idaho: {breakdown}.</p></div>
  <div class="bt-stat"><span class="bt-num">{money(usd_total)}</span><p>in announced investment across the {len(usd_rows)} projects that named a figure. Announcements are not spending.</p></div>
  {stat_mw}
  <div class="bt-stat bt-stat-alert"><span class="bt-num" data-countdown="{deadline['date'] if deadline else ''}">{fmt_date(deadline['date']).rsplit(',', 1)[0] if deadline else ''}</span><p>{deadline['stat'] if deadline else ''} {cite(deadline['url']) if deadline else ''}</p></div>
</div>"""

upcoming = "".join(
    f'<li><time datetime="{u["date"]}"><b>{date.fromisoformat(u["date"]):%b}</b>{date.fromisoformat(u["date"]).day}</time>'
    f'<a href="{esc(u["url"])}">{esc(u["what"])}</a></li>'
    for u in power["upcoming"] if date.fromisoformat(u["date"]) >= CHECKED
)
header = (ROOT / "partials" / "header.html").read_text().strip()
footer = (ROOT / "partials" / "footer.html").read_text().strip()

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="ai-access" content="allow"><meta name="ai-training" content="allow"><meta name="ai-content-type" content="dataset"><link rel="canonical" href="{canonical}"><link rel="alternate" type="application/rss+xml" title="The Idaho Stack" href="{SITE}/feed.xml"><link rel="icon" href="/favicon.ico"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180"><link rel="manifest" href="/manifest.json"><link rel="stylesheet" href="/assets/styles.css"><meta property="og:title" content="{og_title}"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:image" content="{SITE}/og-image.png"><script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>
.bt-hero{{padding:58px 0 18px}}
.bt-hero h1{{font-family:var(--serif);font-size:clamp(2.6rem,7vw,5.6rem);line-height:.92;letter-spacing:-.045em;margin:10px 0 16px;max-width:14ch}}
.dc-hero-grid{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,.65fr);gap:40px;align-items:end}}
.dc-next{{border:1px solid var(--line);border-radius:24px;background:rgba(255,250,240,.86);padding:20px 22px 10px;box-shadow:var(--shadow)}}
.dc-next ol{{list-style:none;margin:10px 0 0;padding:0}}
.dc-next li{{display:grid;grid-template-columns:52px 1fr;gap:12px;align-items:center;padding:11px 0;border-top:1px solid var(--line)}}
.dc-next time{{display:grid;place-items:center;width:52px;height:52px;border-radius:14px;background:var(--ink);color:var(--cream);font-family:var(--serif);font-size:1.35rem;line-height:1}}
.dc-next time b{{font:800 .62rem var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--amber-soft);margin-bottom:-6px}}
.dc-next li:first-child time{{background:var(--rust)}}
.dc-next a{{text-decoration:none;font-size:.95rem;line-height:1.35;color:var(--basalt)}}.dc-next a:hover{{text-decoration:underline}}
.bt-meta{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}}
.bt-meta span{{border:1px solid var(--line);border-radius:999px;padding:6px 12px;background:rgba(255,250,240,.8);font-size:.88rem;color:var(--basalt)}}
.bt-meta .bt-live{{border-color:rgba(111,128,109,.5);background:var(--sage-soft)}}
.bt-meta .bt-live:before{{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--sage);margin-right:8px;vertical-align:1px}}
.bt-stats{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}
.bt-stat{{border:1px solid var(--line);border-radius:22px;background:rgba(255,250,240,.78);padding:20px;box-shadow:0 12px 34px rgba(31,38,35,.06)}}
.bt-stat p{{margin:8px 0 0;color:var(--basalt);font-size:.96rem}}
.bt-num{{display:block;font-family:var(--serif);font-size:clamp(2.1rem,4.2vw,3.2rem);line-height:1;letter-spacing:-.03em;color:var(--ink)}}
.bt-stat-alert{{background:linear-gradient(160deg,rgba(234,208,197,.75),rgba(255,250,240,.85));border-color:rgba(169,88,49,.35)}}
.bt-stat-alert .bt-num{{color:var(--rust)}}
.cite{{font-size:.8rem;font-weight:800;color:var(--rust);text-underline-offset:3px;white-space:nowrap}}
.bt-h2{{font-family:var(--serif);font-size:clamp(1.9rem,4vw,3rem);line-height:1;margin:6px 0 12px}}
.bt-intro{{max-width:760px;color:var(--basalt)}}
.bt-table caption{{text-align:left;padding:14px 16px 4px;font-weight:800;color:var(--basalt)}}
.bt-table .num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.bt-table tbody th{{font-family:var(--sans);font-size:1rem;background:none;font-weight:700}}
.bt-two{{display:grid;grid-template-columns:1.1fr .9fr;gap:22px;align-items:start}}
.bt-q{{counter-reset:q;list-style:none;padding:0;margin:0;display:grid;gap:10px}}
.bt-q li{{counter-increment:q;position:relative;padding:14px 16px 14px 52px;border:1px solid var(--line);border-radius:16px;background:rgba(255,250,240,.74)}}
.bt-q li:before{{content:counter(q);position:absolute;left:14px;top:12px;width:26px;height:26px;border-radius:50%;background:var(--basalt);color:var(--cream);display:grid;place-items:center;font-size:.85rem;font-weight:800}}
.bt-list{{list-style:none;padding:0;margin:0;display:grid;gap:8px}}
.bt-list li{{display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--line);padding-top:8px}}
.bt-list span{{color:var(--muted);font-size:.88rem;text-align:right;white-space:nowrap}}
.bt-note{{border-left:4px solid var(--amber);background:rgba(234,215,184,.45);padding:14px 16px;border-radius:0 14px 14px 0;color:var(--basalt)}}
/* status colours */
.s-op{{--c:#2f5d50;--cs:#d3e3dc}}.s-build{{--c:#6f806d;--cs:var(--sage-soft)}}.s-ok{{--c:#3f6f8f;--cs:#d6e3ea}}
.s-prop{{--c:#c58b32;--cs:var(--amber-soft)}}.s-hold{{--c:#7c7468;--cs:#e6e0d4}}.s-deny{{--c:#a95831;--cs:var(--rust-soft)}}
/* map */
.dc-atlas{{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:28px;align-items:start}}
.dc-mapwrap{{position:sticky;top:120px;border:1px solid var(--line);border-radius:26px;background:linear-gradient(170deg,rgba(255,250,240,.92),rgba(234,215,184,.35));padding:18px 18px 12px;box-shadow:var(--shadow)}}
.dc-map{{display:block;width:100%;height:auto;max-height:74vh}}
.dc-state{{fill:rgba(255,250,240,.9);stroke:var(--basalt);stroke-width:1.6;stroke-linejoin:round}}
.dc-town circle{{fill:var(--muted)}}.dc-town text{{font:600 13px var(--sans);fill:var(--muted)}}.dc-town-s text{{font-size:11.5px}}
.dc-tvbox{{fill:rgba(197,139,50,.12);stroke:var(--amber);stroke-width:1.4;stroke-dasharray:3 3}}
.dc-tvlink{{fill:none;stroke:var(--amber);stroke-width:1.2;stroke-dasharray:3 3}}
.dc-mini{{fill:var(--c)}}
.dc-inset-bg{{fill:var(--cream);stroke:var(--line-dark);stroke-width:1.2;filter:drop-shadow(0 8px 18px rgba(31,38,35,.12))}}
.dc-inset-t{{font:800 10px var(--sans);letter-spacing:.12em;fill:var(--muted)}}
.dc-pin{{cursor:pointer;transition:opacity .2s}}.dc-pin .dc-disc{{fill:var(--c);stroke:var(--cream);stroke-width:2.5;transition:transform .2s;transform-box:fill-box;transform-origin:center}}
.dc-lead{{stroke:var(--c);stroke-width:1.4}}
.dc-pin .dc-halo{{fill:var(--c);opacity:.18;stroke:none}}
.dc-pin text{{font:800 13px var(--sans);fill:#fff;text-anchor:middle;pointer-events:none}}
.dc-pin:hover .dc-disc,.dc-pin:focus .dc-disc{{transform:scale(1.18)}}
.dc-pin.is-dim{{opacity:.18}}
.dc-legend{{list-style:none;display:flex;flex-wrap:wrap;gap:6px 14px;margin:8px 0 0;padding:10px 0 0;border-top:1px solid var(--line);font-size:.86rem;color:var(--basalt)}}
.dc-legend li{{display:flex;align-items:center;gap:6px}}.dc-legend b{{color:var(--muted);font-weight:700}}
.dc-dot{{width:11px;height:11px;border-radius:50%;background:var(--c);display:inline-block}}
.dc-filter{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 16px}}
.dc-chip{{font:inherit;font-size:.9rem;border:1px solid var(--line-dark);background:rgba(255,250,240,.8);color:var(--basalt);border-radius:999px;padding:7px 14px;cursor:pointer}}
.dc-chip b{{font-weight:800;color:var(--muted);margin-left:2px}}
.dc-chip.is-on{{background:var(--ink);color:var(--cream);border-color:var(--ink)}}.dc-chip.is-on b{{color:var(--amber-soft)}}
.dc-cards{{display:grid;gap:14px}}
.dc-card{{border:1px solid var(--line);border-radius:22px;background:rgba(255,250,240,.86);padding:20px 22px;box-shadow:0 12px 34px rgba(31,38,35,.05);scroll-margin-top:130px;transition:box-shadow .3s,border-color .3s}}
.dc-card:target{{border-color:var(--c,var(--rust));box-shadow:0 0 0 3px rgba(197,139,50,.35),0 12px 34px rgba(31,38,35,.08)}}
.dc-card[hidden]{{display:none}}
.dc-card-head{{display:flex;gap:14px;align-items:flex-start}}
.dc-card h3{{font-family:var(--serif);font-size:1.5rem;line-height:1.1;margin:2px 0 0}}
.dc-num{{flex:0 0 auto;width:34px;height:34px;border-radius:50%;background:var(--c);color:#fff;display:grid;place-items:center;font-weight:800;font-size:.95rem;margin-top:2px}}
.dc-place{{margin:0;font-size:.82rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.dc-status{{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:14px 0 12px}}
.dc-pill{{display:inline-block;border-radius:999px;padding:3px 11px;font-size:.8rem;font-weight:800;background:var(--cs);color:var(--c);border:1px solid color-mix(in srgb,var(--c) 35%,transparent);white-space:nowrap}}
.dc-asof{{font-size:.85rem;color:var(--muted)}}
.dc-facts{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0 0 12px;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}}
.dc-facts dt{{font-size:.74rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}}
.dc-facts dd{{margin:2px 0 0;font-weight:650;line-height:1.35}}
.dc-sub{{display:block;font-weight:400;font-size:.84rem;color:var(--muted)}}
.dc-unk{{color:var(--muted);font-style:italic;font-weight:400}}
.dc-rows{{margin:0;display:grid;gap:8px}}
.dc-row{{display:grid;grid-template-columns:104px 1fr;gap:12px;font-size:.95rem}}
.dc-row dt{{font-weight:800;color:var(--basalt)}}.dc-row dd{{margin:0;color:var(--basalt)}}
.dc-flag{{margin:12px 0 0;font-size:.88rem;color:var(--rust);background:rgba(234,208,197,.4);border-radius:10px;padding:8px 12px}}
.dc-src{{margin-top:12px}}.dc-src summary{{cursor:pointer;font-size:.86rem;font-weight:800;color:var(--rust)}}.dc-src ul{{margin-top:10px;font-size:.9rem}}
/* power timeline */
.dc-tl{{list-style:none;margin:20px 0 0;padding:0;position:relative;display:grid;gap:0}}
.dc-tl:before{{content:"";position:absolute;left:9px;top:8px;bottom:8px;width:2px;background:var(--line-dark)}}
.dc-ev{{position:relative;padding:0 0 22px 40px}}
.dc-ev:before{{content:"";position:absolute;left:2px;top:5px;width:16px;height:16px;border-radius:50%;background:var(--paper-2);border:3px solid var(--line-dark)}}
.dc-ev-past:before{{background:var(--sage);border-color:var(--sage)}}
.dc-ev-due:before{{background:var(--rust);border-color:var(--rust);box-shadow:0 0 0 6px rgba(169,88,49,.18)}}
.dc-ev time{{font-size:.8rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}
.dc-ev-due time{{color:var(--rust)}}
.dc-ev-t{{margin:2px 0 4px;font-family:var(--serif);font-size:1.25rem;line-height:1.2}}
.dc-ev-n{{margin:0;color:var(--basalt);font-size:.95rem;max-width:640px}}
.dc-callout{{border:1px solid var(--line);border-radius:22px;padding:22px;background:var(--ink);color:var(--cream)}}
.dc-callout h3{{font-family:var(--serif);font-size:1.6rem;line-height:1.1;margin:0 0 10px}}
.dc-callout p{{color:rgba(255,250,240,.82)}}.dc-callout a{{color:var(--amber-soft)}}
.dc-callout .button{{background:var(--cream);color:var(--ink);border-color:var(--cream);margin-top:6px}}
.dc-rules td{{font-size:.95rem}}
@media(max-width:1000px){{.dc-hero-grid{{grid-template-columns:1fr;gap:24px}}.dc-next{{max-width:560px}}.bt-stats{{grid-template-columns:1fr 1fr}}.bt-two,.dc-atlas{{grid-template-columns:1fr}}.dc-mapwrap{{position:relative;top:0;max-width:520px}}}}
@media(max-width:560px){{.bt-stats{{grid-template-columns:1fr}}.bt-list li{{flex-direction:column;gap:2px}}.bt-list span{{text-align:left}}.dc-facts{{grid-template-columns:1fr 1fr}}.dc-row{{grid-template-columns:1fr;gap:0}}.dc-card{{padding:18px}}}}
@media(prefers-reduced-motion:reduce){{.dc-pin .dc-disc,.dc-card{{transition:none}}}}
</style></head><body><a class="skip" href="#main">Skip to content</a>{header}<main id="main">
<section class="bt-hero"><div class="wrap dc-hero-grid"><div>
<p class="kicker">Tracker · Public tech money</p>
<h1>Idaho’s data center rush, tracked.</h1>
<p class="lede">Developers want to put some of the largest electricity customers in the state’s history in Kuna, Pocatello, the desert south of Boise and beyond. This page follows every project on the public record: who is building, how much power it wants, what tax break it can claim, and what local governments have done about it. It is rebuilt from public records every week.</p>
<div class="bt-meta"><span class="bt-live">Data checked {fmt_date(CHECKED.isoformat())}</span><span>{n_projects} projects · {n_rules} local actions</span><span>Next update: weekly, or when a record changes</span></div>
</div>
<aside class="dc-next" aria-labelledby="dc-next-h"><p class="kicker" id="dc-next-h">Coming up</p><ol>{upcoming}</ol></aside>
</div></section>

<section class="section" style="padding-top:18px"><div class="wrap">{stats}</div></section>

<section class="section"><div class="wrap">
<p class="kicker">Every project</p>
<h2 class="bt-h2">Where they want to build.</h2>
<p class="bt-intro">Tap a number on the map to jump to that project, or filter by where each one stands. Each card shows the date of its latest public change and links to the records behind it. Anything we could not confirm in a primary or reputable source is flagged.</p>
<div class="dc-atlas" style="margin-top:22px">
<figure class="dc-mapwrap" style="margin:0">{map_svg}<ul class="dc-legend">{legend}</ul></figure>
<div><div class="dc-filter" role="group" aria-label="Filter projects by status">{chips}</div><div class="dc-cards">{''.join(cards)}</div></div>
</div>
</div></section>

<section class="section"><div class="wrap bt-two">
<div>
<p class="kicker">Who pays for the power</p>
<h2 class="bt-h2">{esc(power['headline'])}</h2>
<p class="bt-intro">{power['intro']}</p>
<ol class="dc-tl">{timeline}</ol>
</div>
<div style="display:grid;gap:16px">
<aside class="dc-callout"><p class="kicker" style="color:var(--amber-soft)">Have your say</p><h3>{esc(power['callout_title'])}</h3><p>{power['callout']}</p><a class="button" href="{esc(power['callout_url'])}">Open the PUC case</a></aside>
<aside class="bt-note"><p style="margin-top:0"><b>The tax break.</b> Since 2020, Idaho Code 63-3622VV has let data centers that promise $250 million in investment and 30 jobs skip sales tax on servers, equipment and buildings. The state has never published what it costs, and no law requires anyone to report who claims it.</p><p style="margin-bottom:0"><a href="/articles/idaho-data-center-sales-tax-break-unpriced.html">Read: Six years in, Idaho has never priced it →</a><br><a href="/articles/data-center-power-idaho-ratepayers.html">Read: Who pays for the power? →</a></p></aside>
</div>
</div></section>

<section class="section"><div class="wrap">
<p class="kicker">Local rules</p>
<h2 class="bt-h2">Towns and counties are writing the rules as they go.</h2>
<p class="bt-intro">Idaho has no statewide siting rules for data centers, so zoning decisions fall to cities and counties. These are the actions we have found so far.</p>
{rules_table}
</div></section>

<section class="section"><div class="wrap bt-two">
<div>
<p class="kicker">What we don’t know yet</p>
<h2 class="bt-h2">Open questions.</h2>
<ol class="bt-q">{''.join(f'<li>{q}</li>' for q in power['questions'])}</ol>
</div>
<div>
<p class="kicker">Notes on the numbers</p>
<div class="bt-note">{power['notes']}<p style="margin-bottom:0">Know of a project we’ve missed, or a record that changed? <a href="/submit.html">Send a tip</a> or write <a href="mailto:hello@idahostack.com?subject=Data%20center%20tracker">hello@idahostack.com</a>.</p></div>
</div>
</div></section>

<section class="section"><div class="wrap bt-two">
<div>
<p class="kicker">Method</p>
<h2 class="bt-h2">How this is built.</h2>
<p>We list a project once a developer, utility, regulator or local government has put it on the public record, and keep it after a denial so the history stays visible. Sizes and dollar figures are what the developer or a public body announced, not what has been spent. Every row links to its records and shows the date of its latest change. The tracker was compiled with AI from public documents and news reports and reviewed by the editor before publication. No interviews, site visits or company contacts were part of this version.</p>
</div>
<div>
<p class="kicker">Download the data</p>
<ul class="bt-list"><li><a href="/data/datacenters/{CSV_OUT.name}" download>Idaho data center projects</a><span>CSV</span></li></ul>
<details class="dc-src" style="margin-top:18px"><summary>All sources ({len(all_src)})</summary><ul class="bt-list">{src_links(all_src.values())}</ul></details>
</div>
</div></section>
</main>{footer}
<script>(function(){{
var chips=document.querySelectorAll('.dc-chip'),cards=document.querySelectorAll('.dc-card'),pins=document.querySelectorAll('.dc-pin');
chips.forEach(function(c){{c.addEventListener('click',function(){{var f=c.getAttribute('data-f');
chips.forEach(function(o){{var on=o===c;o.classList.toggle('is-on',on);o.setAttribute('aria-pressed',on?'true':'false');}});
cards.forEach(function(k){{k.hidden=!(f==='all'||k.getAttribute('data-status')===f);}});
pins.forEach(function(p){{p.classList.toggle('is-dim',!(f==='all'||p.getAttribute('data-status')===f));}});}});}});
pins.forEach(function(p){{p.addEventListener('click',function(){{var t=document.querySelector(p.getAttribute('href'));if(t&&t.hidden){{chips[0].click();}}}});}});
var d=document.querySelector('[data-countdown]');if(d&&d.getAttribute('data-countdown')){{var end=new Date(d.getAttribute('data-countdown')+'T23:59:00-07:00'),n=Math.ceil((end-new Date())/864e5);
if(n>1){{d.textContent=n+' days';}}else if(n===1){{d.textContent='1 day';}}else if(n<=0){{d.textContent='Closed';}}}}
}})();</script></body></html>
"""

OUT.write_text(page)
print(f"wrote {OUT.relative_to(ROOT)}: {n_projects} projects, {n_rules} local actions, {len(all_src)} sources")
