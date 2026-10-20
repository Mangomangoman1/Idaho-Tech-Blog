# Idaho Stack editorial operations

Established October 16, 2026. Read [HANDOFF.md](HANDOFF.md) at every session start.
The founder's existing [roadmap](../the-idaho-review-roadmap.md) remains the mission
source. This operating plan supplies daily execution and evidence discipline.

## Mission and coverage

Help Idaho readers make better technology decisions by explaining the companies,
physical systems, constraints, skills and public choices shaping the state.
Follow who pays, who maintains, who gets trained, who waits, and the next decision.
Cover chips, power/nuclear, broadband, water/agriculture, repair, practical business
technology, and workforce. Statewide means more than Boise: seek evidence from
Eastern Idaho, North Idaho, Magic Valley, Wood River Valley and rural communities.

A story needs a named Idaho system/place, something changed, local stakes, usable
primary evidence, and a next decision or action. Technology announcements are leads,
not proof of delivery. Keep analysis distinct from sourced facts and uncertainty.
No generic trend padding, vendor promotion or copied news rewrites.

## Authorization and bylines

Routine sourced articles and normal commits/pushes are authorized. Stop before
serious allegations or reputationally sensitive claims about identifiable subjects,
third-party outreach/interviews, payments, new accounts, subscriptions,
credential/security/domain changes, or tracking. Do independent work while a
restricted action is pending. Do not invent a reporter, credential, interview,
quotation, visit, quote review or human sign-off.

Use The Idaho Stack as an Organization author for autonomous AI-assisted work and
visibly disclose AI research/writing and whether any interviews/visits occurred.
Do not assign Samuel Torres a new byline without his actual authorship. Preserve
legacy bylines and publication dates. The About page already identifies Samuel,
Hailey Device Repair and Actrix; disclose a relevant relationship in any future
piece touching his businesses rather than implying editorial independence from it.

## Daily production loop

1. Read handoff, inventory, source ledger, backlog and corrections. Confirm the date
   in Idaho, not just the session timezone. Fetch the verified origin, inspect
   status/divergence and fast-forward only. Never discard edits or force push.
2. Check primary sources and select one useful changed story. Rotate geography and
   beat without forcing a quota. Re-check prior ideas for expiration or repetition.
3. Save a claim ledger before drafting: URL, document and event dates, access date,
   exact page/table, what it supports, current status and gaps. Check newer records.
   Attribute interested-party statements. Distinguish allocation, award, contract,
   expenditure, construction, production and operating service.
4. Draft original synthesis with a practical reader payoff. Cite sources near the
   claims, add source dates and a method/limits note. Explain estimates and counts;
   never equate BSLs, households, subscriptions or people without evidence.
5. Use the existing static HTML design. Add a real publication timestamp with
   timezone, matching visible date, honest byline, canonical, NewsArticle or Article
   metadata, headline, description, author URL and relevant images. Use an original
   explanatory graphic or properly licensed image, credit it and provide alt text.
   No logo as article imagery; no illustration passed off as a documentary photo.
6. Update homepage lead, news index, relevant desk, RSS and normal sitemap. Add
   follow-up links to old coverage without silently changing what it originally
   said. Set dateModified only for substantive changes; record material corrections.
7. Run `npm run build` then `npm run check`. The build injects shared header/footer
   and generates the homepage latest list from original dated article metadata,
   newest first. It regenerates news-sitemap.xml using only NewsArticles published within 48
   hours, excluding future dates. RSS remains hand-maintained; checks require each
   /articles page in RSS and the normal sitemap. Unknown archival publication times
   must remain unknown; RSS pubDate can be omitted.
8. Review the whole new article, source links, numbers and caveats. Check local
   mobile/desktop rendering, navigation, image loads, overflow, broken links and
   browser errors. Review `git diff --check` and staged scope.
9. Commit and push to the observed production branch only when fast-forward safe.
   Verify the remote SHA, Vercel status, public article, homepage, RSS, canonical,
   robots and sitemaps. Separate pushed, built, deployed and publicly verified.
   A successful push or cached browser extract alone does not establish publication.
10. Update handoff with outcome, source ledger, URL, SHA, checks, unresolved facts
    and next reporting trigger. On a quality hold, explain why, preserve the pitch
    and run discovery maintenance anyway.

## Daily continuity and maintenance

The parent configured a daily recurrence beginning October 17, 2026. Do not create
another. The recurring job still needs the saved environment and GitHub access;
its existence is not proof that future articles were researched or published.

The news sitemap is a static snapshot. Running the daily build/publish loop prunes
expired entries; if sessions stop or no rebuild is pushed for more than two days,
news metadata can age on the live server. The hold-day task must commit discovery
pruning when needed. An empty news sitemap is intentional when nothing is fresh.
There is no new background cron, account, paid service or tracking in this change.

Every week review corrections, backlog freshness, source links and regional balance.
Every month revisit a living desk or guide using actual new evidence. Prioritize
accuracy and useful follow-ups over expanding an unmaintained directory.

## Repository and deployment

- Origin: https://github.com/Mangomangoman1/Idaho-Tech-Blog.git
- Default/production branch observed: main. Saved workspace branch initially work.
- Static HTML/CSS with Python standard-library build/check scripts; no npm packages.
- Vercel project linked by GitHub status: wpbfls-5183s-projects/idaho-tech-blog.
- Canonical host in repository: https://www.idahostack.com/ (verify real redirects).
- `vercel.json` now runs `npm run build && npm run check` and serves root output.
  Two existing permanent redirects: contribute -> submit and intelligence -> about.
- Local server: `python3 -m http.server 5173`; build first. No CMS or newsletter
  backend was found. Contact/newsletter actions are mailto links, not subscriptions.
- No repository AGENTS/skills or workflows existed at takeover. Workspace .agents
  and .codex directories were empty. This root AGENTS.md is the continuity entry.

## Next two weeks

The October 16 broadband and October 17 CWI pieces are live per parent verification.
October 17 reporting covers CWI course sequencing and employer hiring before Micron Day;
Oct20 source recheck still listed Nampa public hours4–7:30pm; seek course guidance
before November2 registration. Event notices remain historical after the date.
October 18 reporting explains MARVEL's dry physics milestone and distinct thermal/
end-use tests. Follow dated completion data and public schedule clarification,
without claiming full operation or commercial supply. A newer transformer shake-
test lead should advance with released results and primary supply-chain evidence.
October 19 reporting rotates to Treasure/Payette Valley groundwater measurements,
spatial/depth gaps and model funding. Follow actual survey data and coverage before
claiming a new trend; next scheduled repeats are spring/fall 2027.
October20 reporting covers North Idaho’s ITD payroll-tool change, document uploads,
formats and certification. Follow actual phased district updates, public contract
costs or measured outcomes; do not restate supplier savings promises as findings.
Advance the energy docket only on an actual new filing/order, not its update date.
Build remaining backlog items into claim ledgers before committing to dates. No
interview quota is authorized; outreach needs approval.
