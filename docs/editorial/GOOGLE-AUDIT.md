# Google publishing audit — October 16, 2026

Repository baseline 4648abe. This is a technical/editorial audit, not a statement
that Google has indexed, approved or included the site. No guarantee of Google
News, Top stories, rich results or ranking. No new account, verification DNS,
credential, analytics or tracking change was made.

## Official guidance reviewed

- [Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article): supported types are Article, NewsArticle and BlogPosting. Recommended fields apply where truthful; author may be a Person or Organization. Relevant article imagery should not be a logo. Structured data does not guarantee a search feature.
- [News sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap): include only articles published within the last two days; original publication dates, publication name/language and title. An intentionally empty file can be appropriate.
- [Publication dates](https://developers.google.com/search/docs/appearance/publication-dates): visible and structured dates should agree; use actual publication/substantive-update dates and no future dates.
- [Google News policies](https://support.google.com/news/publisher-center/answer/6204050): clear dates/bylines, author/publisher/company and contact information, with sponsorship transparency.
- [News across Google](https://support.google.com/news/publisher-center/answer/9607025): discovery and consideration are automated; eligible content need not rank. Search Console reports, when accessible, are evidence of appearance.

## Findings, changes and limits

| Area | Baseline | Action / remaining work |
| --- | --- | --- |
| Article metadata | Three newer NewsArticles with Samuel Torres/date fields; two launch articles without Article markup; briefing has incomplete Article. Sector guides use TechArticle. | New story has NewsArticle, matching headline/canonical, real timestamp, Organization author and profile/disclosure URL, publisher, language, free access and relevant image variants. Do not invent old author/date values to complete schemas. Legacy TechArticle is not a Google-supported Article type; reclassify only when the content merits it. |
| Images | Generic og-image logo used as article image in power and May broadband JSON-LD; no story-body images. | New original process graphic, 1600×900, 1200×900, 1200×1200, alt text and explanatory credit. Remaining archival image cleanup is queued; a publisher logo belongs under publisher.logo, not as evidence of a reported scene. |
| Dates and bylines | Human bylines on three newer pieces; two launch articles lack one. Some old RSS noon times lack verified provenance. | Preserve historic credit/time; new autonomous story visibly discloses AI and does not imply Samuel's authorship/review. Legacy Micron RSS addition omits unknown pubDate. Do not silently promote “Sources to verify” into certified reporting. |
| Canonicals/indexability | Pages use www HTTPS canonicals; robots allows crawling and names both sitemaps; no article noindex found locally. | Local canonical/link/JSON-LD checks pass. Live redirect chain, HTTP status, headers and Google-selected canonical need public network/Search Console verification. A canonical is a signal, not proof of indexing. |
| Normal sitemap | 24 URLs, May lastmod values. | New article added; dates updated only for touched substantive pages. Preserve unreviewed archive dates. Sitemap parses; articles covered. |
| News sitemap | May 27 story still marked as news in October. | Build now regenerates from genuine NewsArticle publication dates within 48 hours and excludes future entries. It prunes old metadata, retaining old URLs in normal sitemap/RSS. Static file still needs daily editorial rebuild, including hold days. If unattended beyond two days, live snapshot can age; no server cron added. |
| RSS | Valid feed omitted Micron analysis. | New story and archive Micron item added; all article files are checked for sitemap/RSS inclusion and duplicate GUIDs. Browser autodiscovery retained. RSS itself does not constitute Google submission. |
| Transparency | About identifies Samuel/Hailey/businesses; editorial standards, source lists and contact links exist. | Added public AI process disclosures. No invented staff or credentials. Mailbox delivery untested. Any future coverage of affiliated businesses needs specific conflict disclosure. |
| Index presentation | Home lead claimed latest but showed May 20 while news had May 27. | Home and news now lead with October 16 follow-up and desk/archive forward links. Removed technical search-promotion prose from news intro. |
| Build/deployment | Local stdlib Python build/check; empty Vercel buildCommand; no GitHub Actions workflow. Current SHA had Vercel success status. | Vercel now runs build/check, including sitemap generation, internal links, parseable JSON-LD/XML, article dates, RSS coverage and freshness-boundary tests. Release b5a4bc5 has a successful Vercel status; fresh public behavior remains unverified. |

## Remaining verification

Direct workspace HTTPS requests to IdahoStack.com and GitHub API returned proxy
403; direct no-proxy requests could not resolve DNS. Authenticated GitHub connector
reads work. Web retrieval can read cached public article bodies but cannot establish
fresh production headers or deploy propagation. This is a workspace access limit,
not evidence that the public site is down.

After deploy, obtain fresh public responses for apex -> www redirects, article,
images, robots, RSS and both sitemaps; check HTML canonical/JSON-LD and no noindex
headers. Use Google's Rich Results Test for markup and URL Inspection/Search Console
for live fetch, selected canonical, crawl/index state and sitemap submission if an
existing authorized property is available. None of those authenticated Google
checks was performed here, and no indexing claim should be made.

## October 17 daily check

Reopened official Article, publication-date and news-sitemap guidance. New CWI
article uses a genuine October 17 timestamp, matching visible date and canonical,
Organization author, visible AI method, related public sources and original
representative imagery in three ratios. RSS and normal sitemap updated; news
sitemap rebuilt. Homepage latest list now generates from original article dates
and excludes future metadata; old archive dates remain intact. No Search Console,
URL Inspection or Rich Results Test was run, and no indexing/inclusion claim is made.

Parent independently verified the October 16 article and public feeds after the
previous workspace proxy block; that release is already reported live. See the
current handoff for October 17 validation and deployment evidence.

October 17 content release 5430552 has a successful Vercel status. Fresh article/feed
HTTPS checks from this workspace returned proxy CONNECT 403; current public
behavior remains unverified here. Cached May homepage extraction is not a valid
indicator of today’s deployment. Exact evidence is in the current handoff.

## October 18 daily publishing check

Official Article and news-sitemap guidance reopened. New MARVEL report uses an
honest Organization author/AI method, current publication timestamp and matching
visible date/canonical/JSON-LD, plus original representative graphics in3 ratios.
Homepage latest list is generated; RSS/news index/energy desk and normal sitemap
updated. Build expires October 16 metadata from news sitemap without changing its
article date or removing its RSS/normal sitemap/archive record.

Parent confirmed October 17 release 0068e05 is live with public metadata, home, feed,
sitemaps and image checked at 15:58 UTC. Prior workspace-network notes do not negate
that confirmation. Today's exact remote/deployment/public result goes in handoff.
No authenticated Search Console, URL Inspection or Rich Results Test is claimed.

October 18 content release 552a7b4 has a successful Vercel status and matching
remote SHA. Fresh article/news-sitemap HTTPS requests remain blocked by the
workspace proxy (CONNECT 403). Current public behavior requires independent
verification; exact actions and outcome are in the current handoff.


## October 19 follow-through

Re-read current official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article),
[byline dates](https://developers.google.com/search/docs/appearance/publication-dates),
[news sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap)
and [News transparency policy](https://support.google.com/news/publisher-center/answer/6204050).
No guidance-based infrastructure change was needed. New water article uses honest
Organization authorship linked to AI policy, genuine visible/structured Oct19 date,
canonical, representative original images in three recommended ratios, inline
primary sources, method and source limits. Publisher/about/contact remain linked.

Local audits passed JSON-LD, titles, canonical/local links, date coherence, RSS and
regular/news sitemaps. Robots permits crawling and advertises both sitemaps. RSS
GUIDs preserved; newest first. News metadata uses original48-hour timestamp, not
modification time; Oct17 CWI still qualifies at morning build until09:52:21MDT.
No historical date refresh, fictitious reporter, tracking or credential changes.
Build + five regression tests + twelve responsive browser cases passed. Public
origin behavior, Rich Results Test, Search Console/URL Inspection and actual Google
indexing are separate from these checks; exact release outcome is in HANDOFF.md.


October19 release evidence: content066d153 reached remote main and GitHub Vercel
success. Fresh domain article/home/RSS/sitemap/news-sitemap/image requests at15:16:51UTC
were proxy CONNECT403-blocked; web article/news-sitemap opens were inaccessible.
No confirmed fresh public response or indexing claim. Exact targets/status and
parent verification instructions are in the current handoff. This network block
is not an automatic approval rejection or evidence the application is down.


## October 20 follow-through

Reviewed current official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article),
[publication dates](https://developers.google.com/search/docs/appearance/publication-dates),
[news sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap)
and [News transparency policy](https://support.google.com/news/publisher-center/answer/6204050).
New North Idaho article uses NewsArticle, genuine timezone-aware visible/structured
date, organizational author linked to AI disclosure, canonical and original relevant
images in three recommended ratios. Sources, supplier claims and limits are visible;
publisher/about/contact remain linked. No fabricated human author/credential.

Build/site audit/five regression tests and15responsive browser cases passed.
Robots/canonicals/discovery links retained. RSS new first with stable old GUIDs;
news snapshot now only Oct19/20 after pruning expired Oct18. Normal sitemap retains
archive. Guide related-report links did not refresh historical article dates.

Remote/deployment/public serving require separate evidence, recorded in HANDOFF.
Do not infer this repo has the unrelated deployment issue reported elsewhere, or
infer public serving/indexing from a status alone. No settings/protection bypass,
empty commit, Search Console/URL Inspection/Rich Results Test or inclusion guarantee.


October20 release check: content6a6b794 matched remote main. Fresh combined statuses
were empty at15:36/15:37UTC; check-runs total0. Current deployment is unconfirmed.
All six direct public URL requests were proxy CONNECT403-blocked; web extraction
showed an October19 homepage and could not access the new article, which is not
conclusive fresh origin evidence. No live/indexing claim. Exact targets, unavailable
Vercel access and owner project/log/public-fetch action are in HANDOFF.md. No
configuration change, empty trigger commit or bypass attempted.


## October21 local draft under owner hold

Reviewed current official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article),
[publication dates](https://developers.google.com/search/docs/appearance/publication-dates)
and [news sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap).
Article properties should reflect what applies; datePublished describes first
publication. The new 911 preview therefore claims none: Article/Draft/noindex,
visible status, honest Organization author and three original image ratios, no
canonical or OG URL/dates, and no production discovery entry. Production metadata
must be added with actual publication after the restriction is lifted.

Build/check + five regression tests passed. Bespoke draft metadata/link/image/
partial/discovery audit + nine responsive cases passed. Local daily rebuild removed
expired Oct19 news metadata; Oct20 remains. No claim live snapshot changed.
Owner explicitly prohibits remote sync/checks/push/deployment until restoration;
all intentionally unrun today. No alternate access, bypass, indexing claim or
Search Console/Rich Results Test. Current handoff supersedes earlier release nudges.


## October22 local draft and expiry maintenance

Rechecked official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article)
and [news sitemap rules](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap).
New court AI preview remains Article/Draft/noindex, honestly authored and undated,
with no canonical/OG URL or production discovery entries. Real publication dates
and production metadata are deferred to actual release, not the preparation date.
Both drafts pass custom isolation/link/metadata/partial/image audits and12responsive
cases. Existing911 files remain unchanged. Standard build/check + five regression
tests passed. Local news snapshot is now intentionally empty after Oct20 expiry;
no old publication timestamps changed or archive URLs removed.

Owner hold prevents remote/CI/deployment/live checks. None attempted; no indexing,
News inclusion or rich-result guarantee. Historical release statuses do not verify
either draft. Handoff supplies safe restoration/revalidation/publication steps.


## October23 local software draft

Rechecked official [Article properties](https://developers.google.com/search/docs/appearance/structured-data/article)
and [publication dates](https://developers.google.com/search/docs/appearance/publication-dates).
New preview is Article/Draft/noindex, honestly authored and undated, with three
original image ratios and no canonical/OG URL/publication timestamps or discovery
promotion. Real production metadata is deferred to actual publication. Prior two
drafts preserved unchanged. All three draft safeguards plus15responsive cases pass;
standard build/check + five regression tests pass. Local news sitemap remains
intentionally empty; no old dates refreshed or archive URLs removed.

Owner hold remains; no remote/CI/deployment/live/Google index verification attempted.
No current deployment or Google News/rich-result guarantee. Recovery must start
with explicit restoration and source/status rechecks in HANDOFF.md.


## October24 quality hold and preservation check

Reopened official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article),
[publication dates](https://developers.google.com/search/docs/appearance/publication-dates)
and [news sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap).
No fourth draft created: the transit lead needs stronger evidence. Three existing
previews remain unchanged, honestly authored, undated/noindex and outside discovery.
No canonical/publication date assigned to a research dossier. The daily build leaves
local news metadata intentionally empty; no archive dates or URLs were refreshed.

Standard build/check and five regression tests passed, as did all three draft
safeguards/preservation checks and15responsive browser cases. Representative mobile/
desktop views reviewed. See the current handoff and validation record for scope.
Owner hold prevents remote/CI/deployment/public serving checks; none attempted.
No Rich Results Test, Search Console, indexing or News-inclusion result claimed.


## October 25 research hold and local checks

Reopened official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article),
[publication dates](https://developers.google.com/search/docs/appearance/publication-dates)
and [news sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap).
No fourth article: Ammon reporting gates remain open. Three existing previews
remain unchanged, undated, honestly authored, noindex and outside discovery.
Daily build left the local news snapshot intentionally empty; old publication
metadata and archive URLs remain unchanged. No production metadata/code change.

Build/check and five regression tests passed; all-draft isolation/preservation
checks and 15 responsive browser cases passed. Representative mobile/desktop views
reviewed. See the current handoff and October 25 validation for actual scope.
Owner hold remains: no remote/CI/deployment/public-origin verification attempted.
No Rich Results Test, Search Console, indexing or Google News result claimed.


## October 26 undated geophysics draft

Reopened official [Article guidance](https://developers.google.com/search/docs/appearance/structured-data/article),
[publication dates](https://developers.google.com/search/docs/appearance/publication-dates)
and [news sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap).
New preview remains Article/Draft/noindex, with honest Organization author, visible
AI method, no publication/canonical/OG URL claim and original relevant images in
three ratios. Its preparation date is not a publication date. Three earlier drafts
remain unchanged; all four are excluded from production discovery. Daily build
leaves local news metadata empty without refreshing archive dates or URLs.

Standard build/check and five regression tests passed; all four draft safeguards,
prior-work preservation and 18 responsive browser cases passed. New artwork and
representative mobile/desktop views reviewed. Exact scope in current handoff and
validation record. Owner hold prevents remote/CI/deployment/public-origin checks;
none attempted. No Rich Results Test, Search Console, indexing or News guarantee.


## October 27 UTC restored release preparation

Owner restoration permits normal release checks. Court and INL pieces have genuine
current Idaho timestamps, Organization authorship/AI disclosure, NewsArticle,
canonical/OG and original relevant images. Discovery integrated and news sitemap
contains only those two. Two held drafts stay undated/noindex; two original previews
remain as labeled archives. October 20's unverified first-publication metadata and
RSS date removed with a visible provenance clarification; no replacement first date
invented. Its actual substantive modification is labeled separately.

Official Article/date/news-sitemap guidance reopened. Build/site checks, five
regression tests and 33 responsive cases pass. Remote, deployment and public evidence
are separate and recorded in current handoff after push. No Rich Results Test,
Search Console, indexing or News inclusion claim follows from local schema checks.


October 27 release evidence: exact content `4288672737cd188f1cca7c4baff61ee8d350a52b` reached main and received
Vercel success. All ten fresh origin checks were proxy CONNECT 403 blocked, and
web article retrieval was unavailable. Local schema/discovery validation and a
successful deployment status do not certify fresh public headers, selected
canonical, serving or indexing. Current handoff/public-check JSON record the
precise targets, limits and independent verification action. No live claim.


## October 27 daily SH-21 piece and completed recovery

Parent independently verified the earlier recovered release at remote 456c42f:
both public INL/court articles fully rendered in cloud Chrome, accurate metadata/
disclosures and live News navigation. That supersedes the earlier workspace-only
serving limit for those articles; no Google indexing result was asserted.

New SH-21 reporting uses a genuine October 27 Idaho timestamp, Organization author/
AI method, relevant original images, canonical/OG/NewsArticle and discovery links.
Official Article/date/news-sitemap guidance reopened; the news snapshot has three
recent articles with their original dates. Prior GUIDs/dates and the October 20
provenance clarification remain intact. Build/site checks, five regression tests
and 12 responsive cases pass after a new-table mobile-width fix. Prior articles,
artwork and CSS are unchanged. New release verification is recorded separately in
the current handoff. No Rich Results Test, Search Console or inclusion guarantee.


Today's content `fa7665200f22a427f8853809c5b08c070112b7f0` reached main with Vercel success. Normal saved-workspace
Chromium navigation to the new SH-21 article returned ERR_TUNNEL_CONNECTION_FAILED;
web article/news-sitemap retrieval was unavailable. This new-page check remains for
the parent's working cloud Chrome route. Previous INL/court public verification is
complete and is not reopened. Exact new task evidence/target is in the current
handoff and public-check JSON. No new live/indexing claim from this workspace.
