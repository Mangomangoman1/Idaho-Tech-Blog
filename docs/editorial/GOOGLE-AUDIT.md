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
| Build/deployment | Local stdlib Python build/check; empty Vercel buildCommand; no GitHub Actions workflow. Current SHA had Vercel success status. | Vercel now runs build/check, including sitemap generation, internal links, parseable JSON-LD/XML, article dates, RSS coverage and freshness-boundary tests. Confirm result for pushed SHA separately. |

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
