#!/usr/bin/env python3
"""Builds broadband-tracker.html from the CSV files in data/bead/.

Weekly update: refresh the CSVs and the STATUS block below from the newest
state records, then run this script and `npm run build`.
"""
import csv
import html
import json
import pathlib
from collections import OrderedDict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "bead"
OUT = ROOT / "broadband-tracker.html"
SITE = "https://www.idahostack.com"

# Facts taken from the state's own documents. Each one is cited on the page.
STATUS = {
    "checked": "October 30, 2026",
    "checked_iso": "2026-10-30",
    "program_total": "$583.2 million",
    "final_proposal_approved": "December 19, 2025",
    "notice_of_award": "January 26, 2026",
    "projects_awarded": 94,
    "signed_projects": 45,
    "board_packet": "October 1, 2026",
    "returned_pool": 26232,
    "printed_withdrawal_total": "$164,352,678.01",
    "printed_withdrawal_bsl": "25,393",
}

SOURCES = OrderedDict([
    ("final", ("Idaho BEAD Final Proposal page, Idaho Office of Broadband", "https://linkup.idaho.gov/idaho-bead-final-proposal/", "Read Oct. 30, 2026")),
    ("overview", ("BEAD Awards Overview and Map (updated Feb. 2–3, 2026)", "https://linkup.idaho.gov/wp-content/uploads/2026/02/BEAD-Awards-Overview_Map-2.3.26.pdf", "Provider award table")),
    ("board", ("Idaho Broadband Advisory Board packet, Oct. 1, 2026", "https://commerce.idaho.gov/wp-content/uploads/2026/09/10_1_2026-Board-Book.pdf", "BEAD executive summary, packet pages 2–9")),
    ("faq", ("Subgrantee FAQ, version 6 (Aug. 18, 2026)", "https://linkup.idaho.gov/wp-content/uploads/2026/08/Subgrantee-RFI-FAQ_V6_08.18.26.pdf", "Construction and payment gates")),
])

ALIASES = {
    "Newmax LLC": "Newmax LLC dba Intermax Networks",
    "Wi-Fiber": "Wi-Fiber Inc",
}
SHORT = {
    "Albion Telephone Company, Inc. dba ATC Communications": "ATC Communications (Albion Telephone)",
    "Coeur d'Alene Tribe DBA Red Spectrum": "Red Spectrum (Coeur d’Alene Tribe)",
    "Concept Communications, LLC": "Concept Communications",
    "Custer Telephone Cooperative Inc": "Custer Telephone Cooperative",
    "Direct Communications Rockland Inc.": "Direct Communications Rockland",
    "Farmers Mutual Telephone Co.": "Farmers Mutual Telephone",
    "FyberCom LLC": "FyberCom",
    "Midvale Telephone Company dba MTE Communications": "MTE Communications (Midvale Telephone)",
    "Mud Lake Telephone Cooperative Assoc Inc.": "Mud Lake Telephone Cooperative",
    "Newmax LLC dba Intermax Networks": "Intermax Networks (Newmax)",
    "Northwest Fiber LLC dba Ziply": "Ziply Fiber (Northwest Fiber)",
    "Rally Networks (Formerly Oregon Telephone Corp)": "Rally Networks",
    "RTI (Rural Telecom Inc.)": "Rural Telecom (RTI)",
    "White Cloud Communications, Inc": "White Cloud Communications",
    "Wi-Fiber Inc": "Wi-Fiber",
    "Anthem Broadband": "Anthem Broadband",
    "Anthem Broadband LLC": "Anthem Broadband",
    "E.L. Automation, Inc. Dba E.L. Internet Northwest": "E.L. Internet Northwest",
    "E.L. Automation, Inc": "E.L. Internet Northwest",
    "IBT Group USA": "IBT Group USA",
    "SpaceX": "SpaceX (Starlink)",
    "ETS Management LLC": "ETS Management",
    "Fremont Telcom Co. DBA Blackfoot Communications": "Blackfoot Communications (Fremont Telcom)",
    "Inland Cellular LLC": "Inland Cellular",
    "Nez Perce Tribe": "Nez Perce Tribe",
}
TECH = {
    "FTTP": "Fiber",
    "Licensed Fixed Wireless": "Fixed wireless",
    "Low Earth Orbit Satellite": "Satellite",
    "Mixed Technology": "Mixed",
}


def read(name):
    with open(DATA / name, newline="") as f:
        return list(csv.DictReader(f))


def money(v, digits=1):
    v = float(v)
    if v >= 1e6:
        return f"${v / 1e6:,.{digits}f}M"
    if v >= 1e3:
        return f"${v / 1e3:,.0f}K"
    return f"${v:,.0f}"


def esc(s):
    return html.escape(str(s), quote=True)


def cite(key):
    return f'<a class="cite" href="{SOURCES[key][1]}">source</a>'


awards = read("idaho-bead-awards-2026-02.csv")
withdrawals = read("idaho-bead-withdrawals-2026-10.csv")
rebid = read("idaho-bead-rebid-2026-08.csv")

total_award = sum(float(r["bead_award_usd"]) for r in awards)
total_bsl = sum(int(r["locations_bsl"]) for r in awards)
providers = OrderedDict()
for r in awards:
    p = providers.setdefault(r["provider"], {"award": 0.0, "bsl": 0, "areas": 0, "tech": []})
    p["award"] += float(r["bead_award_usd"])
    p["bsl"] += int(r["locations_bsl"])
    p["areas"] += int(r["project_areas"])
    p["tech"].append(TECH[r["technology"]])

out = OrderedDict()
for r in withdrawals:
    name = ALIASES.get(r["provider"], r["provider"])
    w = out.setdefault(name, {"award": 0.0, "bsl": 0, "areas": 0})
    w["award"] += float(r["bead_award_returned_usd"])
    w["bsl"] += int(r["locations_bsl"])
    w["areas"] += 1
wd_award = sum(w["award"] for w in out.values())
wd_bsl = sum(w["bsl"] for w in out.values())
for name, w in out.items():
    assert name in providers, name
    w["share"] = w["award"] / providers[name]["award"]

bids = OrderedDict()
for r in rebid:
    raw = r["provider"].replace(" [pending NTIA match waiver]", "")
    b = bids.setdefault(raw, {"bsl": 0, "req": 0.0, "match": 0.0, "areas": 0, "pending": "pending" in r["provider"]})
    b["bsl"] += int(r["locations_bsl"])
    b["req"] += float(r["bead_request_usd"])
    b["match"] += float(r["provider_match_usd"])
    b["areas"] += 1
bid_bsl = sum(b["bsl"] for b in bids.values())
bid_req = sum(b["req"] for b in bids.values())

held_award = total_award - wd_award
held_bsl = total_bsl - wd_bsl
held_share = held_award / total_award
wd_share = wd_award / total_award
n_providers = len(providers)
n_out = len(out)
all_out = all(abs(w["share"] - 1) < 1e-9 for w in out.values())
assert all_out, "page copy assumes every withdrawing provider returned its whole award"
award_short = {SHORT.get(k, k) for k in providers}

# ---------- page parts ----------

stats = f"""
<div class="bt-stats">
  <div class="bt-stat"><span class="bt-num">{money(total_award)}</span><p>awarded in February 2026 to {n_providers} providers to reach {total_bsl:,} homes, businesses and other locations. {cite('overview')}</p></div>
  <div class="bt-stat bt-stat-alert"><span class="bt-num">{money(wd_award)}</span><p>handed back. {n_out} providers withdrew every Idaho award they held, {wd_share:.0%} of the money and {wd_bsl:,} locations. {cite('board')}</p></div>
  <div class="bt-stat"><span class="bt-num">{STATUS['signed_projects']}</span><p>projects with a signed grant agreement as of {STATUS['board_packet']}. Signing comes before environmental review and construction. {cite('board')}</p></div>
  <div class="bt-stat"><span class="bt-num">{bid_bsl:,}</span><p>returned locations offered to other providers in an August re-bid, asking {money(bid_req)}. Still awaiting federal approval. {cite('board')}</p></div>
</div>"""

stages = [
    ("done", "Awarded", f"{STATUS['projects_awarded']} projects", "Federal approval Dec. 19, 2025; notice of award Jan. 26, 2026."),
    ("done", "Agreement signed", f"{STATUS['signed_projects']} projects", "As of the Oct. 1 board packet, which also says 43 in one passage."),
    ("unknown", "Environmental clearance", "Not reported", "Required before any digging. The packet gives no count."),
    ("unknown", "Construction", "Not reported", "Cannot begin until environmental review is complete."),
    ("unknown", "Service live", "None reported", "The state’s packet reports no BEAD-funded connection in service."),
]
pipeline = '<ol class="bt-pipe">' + "".join(
    f'<li class="bt-step bt-{state}"><span class="bt-dot" aria-hidden="true"></span><p class="bt-step-name">{esc(name)}</p>'
    f'<p class="bt-step-count">{esc(count)}</p><p class="bt-step-note">{esc(note)}</p></li>'
    for state, name, count, note in stages
) + "</ol>"

bar = f"""
<figure class="bt-bar-fig">
  <div class="bt-bar" role="img" aria-label="Of {money(total_award)} awarded, {money(held_award)} ({held_share:.0%}) is still held by the original providers and {money(wd_award)} ({wd_share:.0%}) was returned.">
    <span class="bt-seg bt-held" style="width:{held_share * 100:.2f}%"><b>{money(held_award)}</b> still held by {n_providers - n_out} original providers</span>
    <span class="bt-seg bt-out" style="width:{wd_share * 100:.2f}%"><b>{money(wd_award)}</b> returned</span>
  </div>
  <div class="bt-bar bt-bar-sub" role="img" aria-label="August re-bid requests total {money(bid_req)}, pending federal approval.">
    <span class="bt-seg bt-rebid" style="width:{bid_req / total_award * 100:.2f}%"><b>{money(bid_req)}</b> re-bid, pending</span>
  </div>
  <figcaption>Bars share one scale: the {money(total_award)} in awards announced in February 2026. Amounts are grant awards, not money spent. These documents do not account for the gap between the awards and Idaho’s full {STATUS['program_total']} allocation. {cite('final')}</figcaption>
</figure>"""

out_rows = "".join(
    f"<tr><th scope=\"row\">{esc(SHORT.get(n, n))}</th><td>{esc(' + '.join(sorted(set(providers[n]['tech']))))}</td>"
    f"<td class=\"num\">{money(w['award'], 2)}</td><td class=\"num\">{w['bsl']:,}</td><td class=\"num\">{w['share']:.0%}</td></tr>"
    for n, w in sorted(out.items(), key=lambda kv: -kv[1]["award"])
)
out_table = f"""
<div class="table-wrap"><table class="baseline-table bt-table">
<caption>Providers that withdrew, from the state’s Oct. 1 board packet</caption>
<thead><tr><th scope="col">Provider</th><th scope="col">Technology</th><th scope="col" class="num">Money returned</th><th scope="col" class="num">Locations</th><th scope="col" class="num">Share of its award</th></tr></thead>
<tbody>{out_rows}</tbody>
<tfoot><tr><th scope="row">Total</th><td></td><td class="num">{money(wd_award, 2)}</td><td class="num">{wd_bsl:,}</td><td></td></tr></tfoot>
</table></div>"""


def bid_note(raw, b):
    if b["pending"]:
        return "New to Idaho’s BEAD awards; waiting on a federal waiver of its match"
    if SHORT.get(raw, raw) in award_short:
        return "Already held February awards"
    return ""


bid_rows = "".join(
    f"<tr><th scope=\"row\">{esc(SHORT.get(n, n.split(' (')[0].rstrip(',')))}</th><td class=\"num\">{b['areas']}</td><td class=\"num\">{b['bsl']:,}</td>"
    f"<td class=\"num\">{money(b['req'], 2)}</td><td class=\"num\">${b['req'] / b['bsl']:,.0f}</td><td>{esc(bid_note(n, b))}</td></tr>"
    for n, b in sorted(bids.items(), key=lambda kv: -kv[1]["req"])
)
bid_table = f"""
<div class="table-wrap"><table class="baseline-table bt-table">
<caption>New projects proposed in the August 14–24 re-bid</caption>
<thead><tr><th scope="col">Provider</th><th scope="col" class="num">Projects</th><th scope="col" class="num">Locations</th><th scope="col" class="num">BEAD request</th><th scope="col" class="num">Per location</th><th scope="col">Note</th></tr></thead>
<tbody>{bid_rows}</tbody>
<tfoot><tr><th scope="row">Total</th><td class="num">{sum(b['areas'] for b in bids.values())}</td><td class="num">{bid_bsl:,}</td><td class="num">{money(bid_req, 2)}</td><td></td><td></td></tr></tfoot>
</table></div>"""

prov_rows = "".join(
    f"<tr class=\"{'bt-gone' if n in out else ''}\"><th scope=\"row\">{esc(SHORT.get(n, n))}</th><td>{esc(' + '.join(dict.fromkeys(p['tech'])))}</td>"
    f"<td class=\"num\">{p['areas']}</td><td class=\"num\">{money(p['award'], 2)}</td><td class=\"num\">{p['bsl']:,}</td>"
    f"<td class=\"num\">${p['award'] / p['bsl']:,.0f}</td>"
    f"<td>{'<span class=\"bt-chip bt-chip-out\">Withdrew</span>' if n in out else '<span class=\"bt-chip\">Holding award</span>'}</td></tr>"
    for n, p in sorted(providers.items(), key=lambda kv: -kv[1]["award"])
)
prov_table = f"""
<div class="table-wrap"><table class="baseline-table bt-table">
<caption>All {n_providers} February 2026 award holders and where each stands</caption>
<thead><tr><th scope="col">Provider</th><th scope="col">Technology</th><th scope="col" class="num">Project areas</th><th scope="col" class="num">BEAD award</th><th scope="col" class="num">Locations</th><th scope="col" class="num">Per location</th><th scope="col">Status</th></tr></thead>
<tbody>{prov_rows}</tbody>
<tfoot><tr><th scope="row">Total</th><td></td><td class="num">{sum(p['areas'] for p in providers.values())}</td><td class="num">{money(total_award, 2)}</td><td class="num">{total_bsl:,}</td><td class="num">${total_award / total_bsl:,.0f}</td><td></td></tr></tfoot>
</table></div>"""

sources_html = "".join(
    f'<li><a href="{u}">{esc(t)}</a><span>{esc(note)}</span></li>' for t, u, note in SOURCES.values()
)

title = "Idaho BEAD Broadband Tracker | The Idaho Stack"
desc = (f"Where Idaho’s federal broadband grant stands: {money(total_award)} awarded to {n_providers} providers, "
        f"{money(wd_award)} returned by {n_out} that withdrew, and how many projects have reached each stage. Updated weekly from state records.")
canonical = f"{SITE}/broadband-tracker.html"
csvs = [
    ("Idaho BEAD awards by provider and technology, February 2026", "idaho-bead-awards-2026-02.csv"),
    ("Idaho BEAD awards returned by withdrawing providers, October 2026", "idaho-bead-withdrawals-2026-10.csv"),
    ("Idaho BEAD re-bid new project proposals, August 2026", "idaho-bead-rebid-2026-08.csv"),
]
jsonld = {
    "@context": "https://schema.org",
    "@type": "Dataset",
    "name": "Idaho BEAD Broadband Tracker",
    "description": desc,
    "url": canonical,
    "dateModified": STATUS["checked_iso"],
    "spatialCoverage": {"@type": "Place", "name": "Idaho"},
    "isAccessibleForFree": True,
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "creator": {"@type": "Organization", "name": "The Idaho Stack", "url": SITE + "/"},
    "isBasedOn": [u for _, u, _ in SOURCES.values()],
    "distribution": [
        {"@type": "DataDownload", "name": n, "encodingFormat": "text/csv", "contentUrl": f"{SITE}/data/bead/{f}"}
        for n, f in csvs
    ],
}
downloads = "".join(f'<li><a href="/data/bead/{f}" download>{esc(n)}</a><span>CSV</span></li>' for n, f in csvs)

header = (ROOT / "partials" / "header.html").read_text().strip()
footer = (ROOT / "partials" / "footer.html").read_text().strip()

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="ai-access" content="allow"><meta name="ai-training" content="allow"><meta name="ai-content-type" content="dataset"><link rel="canonical" href="{canonical}"><link rel="alternate" type="application/rss+xml" title="The Idaho Stack" href="{SITE}/feed.xml"><link rel="icon" href="/favicon.ico"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180"><link rel="manifest" href="/manifest.json"><link rel="stylesheet" href="/assets/styles.css"><meta property="og:title" content="Idaho BEAD Broadband Tracker"><meta property="og:description" content="{esc(desc)}"><meta property="og:type" content="website"><meta property="og:image" content="{SITE}/og-image.png"><script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>
.bt-hero{{padding:58px 0 18px}}
.bt-hero h1{{font-family:var(--serif);font-size:clamp(2.6rem,7vw,5.6rem);line-height:.92;letter-spacing:-.045em;margin:10px 0 16px;max-width:15ch}}
.bt-meta{{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}}
.bt-meta span{{border:1px solid var(--line);border-radius:999px;padding:6px 12px;background:rgba(255,250,240,.8);font-size:.88rem;color:var(--basalt)}}
.bt-meta .bt-live{{border-color:rgba(111,128,109,.5);background:var(--sage-soft)}}
.bt-meta .bt-live:before{{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--sage);margin-right:8px;vertical-align:1px}}
.bt-stats{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}}
.bt-stat{{border:1px solid var(--line);border-radius:22px;background:rgba(255,250,240,.78);padding:20px;box-shadow:0 12px 34px rgba(31,38,35,.06)}}
.bt-stat p{{margin:8px 0 0;color:var(--basalt);font-size:.96rem}}
.bt-num{{display:block;font-family:var(--serif);font-size:clamp(2.2rem,4.4vw,3.3rem);line-height:1;letter-spacing:-.03em;color:var(--ink)}}
.bt-stat-alert{{background:linear-gradient(160deg,rgba(234,208,197,.75),rgba(255,250,240,.85));border-color:rgba(169,88,49,.35)}}
.bt-stat-alert .bt-num{{color:var(--rust)}}
.cite{{font-size:.8rem;font-weight:800;color:var(--rust);text-underline-offset:3px;white-space:nowrap}}
.bt-h2{{font-family:var(--serif);font-size:clamp(1.9rem,4vw,3rem);line-height:1;margin:6px 0 12px}}
.bt-intro{{max-width:760px;color:var(--basalt)}}
.bt-pipe{{list-style:none;margin:22px 0 0;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:0;position:relative}}
.bt-step{{position:relative;padding:34px 16px 0 0}}
.bt-step:before{{content:"";position:absolute;top:11px;left:0;right:0;height:3px;background:var(--line)}}
.bt-done:before{{background:var(--sage)}}
.bt-dot{{position:absolute;top:2px;left:0;width:22px;height:22px;border-radius:50%;border:3px solid var(--line-dark);background:var(--paper-2)}}
.bt-done .bt-dot{{background:var(--sage);border-color:var(--sage)}}
.bt-unknown .bt-dot{{border-style:dashed}}
.bt-step-name{{margin:0;font-weight:800}}
.bt-step-count{{margin:2px 0 6px;font-family:var(--serif);font-size:1.5rem;line-height:1.1}}
.bt-unknown .bt-step-count{{color:var(--muted);font-style:italic}}
.bt-step-note{{margin:0;font-size:.9rem;color:var(--muted)}}
.bt-bar-fig{{margin:22px 0 0}}
.bt-bar{{display:flex;width:100%;min-height:58px;border-radius:16px;overflow:hidden;border:1px solid var(--line-dark);background:rgba(255,250,240,.6)}}
.bt-bar-sub{{margin-top:10px;min-height:44px;border-style:dashed}}
.bt-seg{{display:flex;align-items:center;padding:8px 14px;font-size:.92rem;line-height:1.2;min-width:0}}
.bt-seg b{{font-family:var(--serif);font-size:1.15rem;margin-right:6px;white-space:nowrap}}
.bt-held{{background:var(--sage-soft);color:var(--ink)}}
.bt-out{{background:var(--rust);color:var(--cream)}}
.bt-rebid{{background:var(--amber-soft);color:var(--ink);white-space:nowrap}}
.bt-bar-fig figcaption{{margin-top:10px;font-size:.9rem;color:var(--muted);max-width:820px}}
.bt-table caption{{text-align:left;padding:14px 16px 4px;font-weight:800;color:var(--basalt)}}
.bt-table .num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.bt-table tbody th{{font-family:var(--sans);font-size:1rem;background:none;font-weight:700}}
.bt-table tfoot th,.bt-table tfoot td{{font-weight:800;border-top:2px solid var(--line-dark);border-bottom:0}}
.bt-gone th,.bt-gone td{{color:var(--muted)}}
.bt-gone th{{text-decoration:line-through;text-decoration-color:rgba(169,88,49,.6)}}
.bt-chip{{display:inline-block;border:1px solid rgba(111,128,109,.45);background:var(--sage-soft);border-radius:999px;padding:3px 10px;font-size:.82rem;font-weight:700;color:var(--ink);white-space:nowrap}}
.bt-chip-out{{background:var(--rust-soft);border-color:rgba(169,88,49,.45);color:var(--rust)}}
.bt-two{{display:grid;grid-template-columns:1.1fr .9fr;gap:22px;align-items:start}}
.bt-q{{counter-reset:q;list-style:none;padding:0;margin:0;display:grid;gap:10px}}
.bt-q li{{counter-increment:q;position:relative;padding:14px 16px 14px 52px;border:1px solid var(--line);border-radius:16px;background:rgba(255,250,240,.74)}}
.bt-q li:before{{content:counter(q);position:absolute;left:14px;top:12px;width:26px;height:26px;border-radius:50%;background:var(--basalt);color:var(--cream);display:grid;place-items:center;font-size:.85rem;font-weight:800}}
.bt-list{{list-style:none;padding:0;margin:0;display:grid;gap:8px}}
.bt-list li{{display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--line);padding-top:8px}}
.bt-list span{{color:var(--muted);font-size:.88rem;text-align:right}}
.bt-note{{border-left:4px solid var(--amber);background:rgba(234,215,184,.45);padding:14px 16px;border-radius:0 14px 14px 0;color:var(--basalt)}}
@media(max-width:1000px){{.bt-stats{{grid-template-columns:1fr 1fr}}.bt-two{{grid-template-columns:1fr}}}}
@media(max-width:850px){{.bt-pipe{{grid-template-columns:1fr;gap:0}}.bt-step{{padding:0 0 18px 40px}}.bt-step:before{{top:0;bottom:0;left:10px;right:auto;width:3px;height:auto}}.bt-dot{{top:0}}.bt-bar{{flex-direction:column}}.bt-seg{{width:auto!important}}.bt-bar-sub .bt-seg{{width:auto!important}}}}
@media(max-width:560px){{.bt-stats{{grid-template-columns:1fr}}.bt-list li{{flex-direction:column;gap:2px}}.bt-list span{{text-align:left}}}}
</style></head><body><a class="skip" href="#main">Skip to content</a>{header}<main id="main">
<section class="bt-hero"><div class="wrap">
<p class="kicker">Tracker · Public broadband money</p>
<h1>Idaho’s broadband money, tracked.</h1>
<p class="lede">Idaho has {STATUS['program_total']} in federal BEAD funding to bring good internet to places that lack it. This page follows who holds that money, who gave it back, and how far the projects have actually gotten. It is rebuilt from state records every week.</p>
<div class="bt-meta"><span class="bt-live">Data checked {STATUS['checked']}</span><span>Latest state status report: {STATUS['board_packet']}</span><span>Next update: weekly, or when the state publishes new records</span></div>
</div></section>

<section class="section" style="padding-top:18px"><div class="wrap">{stats}</div></section>

<section class="section"><div class="wrap">
<p class="kicker">Where the projects are</p>
<h2 class="bt-h2">Signed is not built.</h2>
<p class="bt-intro">Each project has to clear these stages in order. The state reports progress through signing. It has not published counts for the stages that put fiber in the ground, so those stay empty here until it does. {cite('board')} {cite('faq')}</p>
{pipeline}
</div></section>

<section class="section"><div class="wrap">
<p class="kicker">Where the money is</p>
<h2 class="bt-h2">More than a third of the awards came back.</h2>
<p class="bt-intro">Four providers did not trim their plans. Each returned every Idaho award it had won, which we confirmed by matching the state’s withdrawal rows against its February award table, provider by provider.</p>
{bar}
</div></section>

<section class="section"><div class="wrap">
<p class="kicker">Who withdrew</p>
<h2 class="bt-h2">{n_out} providers, {wd_bsl:,} locations.</h2>
<p class="bt-intro">The board packet lists the withdrawals but gives no reasons. A location is a home, business or other building the state counts as needing service; it is not a count of people.</p>
{out_table}
</div></section>

<section class="section"><div class="wrap">
<p class="kicker">What replaced them</p>
<h2 class="bt-h2">The August re-bid.</h2>
<p class="bt-intro">From August 14 to 24 the state invited bids on the returned locations. It says bids covered the full returned pool of {STATUS['returned_pool']:,} locations through new projects and changes to existing ones. The table below is the new-project portion only, so it does not add up to the full pool. None of it is final until the federal government approves it, and the state plans one more round after that, with no date yet. {cite('board')}</p>
{bid_table}
</div></section>

<section class="section"><div class="wrap">
<p class="kicker">Every award holder</p>
<h2 class="bt-h2">All {n_providers} providers.</h2>
<p class="bt-intro">February award totals by provider, combining fiber, wireless, satellite and mixed projects. Awards are grant commitments, not money paid out; providers are paid against milestones. {cite('overview')}</p>
{prov_table}
</div></section>

<section class="section"><div class="wrap bt-two">
<div>
<p class="kicker">What we don’t know yet</p>
<h2 class="bt-h2">Open questions.</h2>
<ol class="bt-q">
<li>Which counties and towns were in the withdrawn project areas, and who now covers them. The state’s location spreadsheets hold this; county-level tracking is our next addition.</li>
<li>How many of the {STATUS['signed_projects']} signed projects have cleared environmental review, and when the first construction starts.</li>
<li>Why the four providers withdrew. The state’s packet does not say.</li>
<li>What the required low-cost internet plan will cost subscribers in each area.</li>
<li>Which locations, if any, are still unclaimed after the re-bid. The state calls its current estimates preliminary.</li>
</ol>
</div>
<div>
<p class="kicker">Notes on the numbers</p>
<div class="bt-note"><p style="margin-top:0">The packet prints the withdrawal total as {STATUS['printed_withdrawal_total']} and {STATUS['printed_withdrawal_bsl']} locations. Its own rows add to {money(wd_award, 2)} (${wd_award:,.2f}) and {wd_bsl:,} locations, the same figures as the four providers’ February awards. We use the row totals.</p><p>The packet says {STATUS['signed_projects']} projects have signed agreements in two places and 43 in another. The February overview’s table counts 727 project areas while a note on the same page says 588.</p><p style="margin-bottom:0">Corrections or records we’ve missed: <a href="mailto:hello@idahostack.com?subject=Broadband%20tracker">hello@idahostack.com</a></p></div>
</div>
</div></section>

<section class="section"><div class="wrap bt-two">
<div>
<p class="kicker">Method</p>
<h2 class="bt-h2">How this is built.</h2>
<p>Every figure comes from Idaho Office of Broadband and Idaho Commerce documents listed here. We transcribed the provider tables, then checked each one by adding every row and comparing it with the document’s own totals. The tracker was compiled with AI and reviewed by the editor before publication. No interviews, site visits or provider contacts were part of this version.</p>
<p>More context: <a href="/articles/idaho-bead-provider-withdrawals-rebid.html">the October withdrawal story</a> and <a href="/articles/idaho-broadband-bead-delivery-deadline.html">why delivery is the hard part</a>.</p>
</div>
<div>
<p class="kicker">Sources</p>
<ul class="bt-list">{sources_html}</ul>
<p class="kicker" style="margin-top:22px">Download the data</p>
<ul class="bt-list">{downloads}</ul>
</div>
</div></section>
</main>{footer}</body></html>
"""

OUT.write_text(page)
print(f"wrote {OUT.relative_to(ROOT)}: {money(total_award)} awarded, {money(wd_award)} returned by {n_out}, {bid_bsl:,} re-bid locations")
