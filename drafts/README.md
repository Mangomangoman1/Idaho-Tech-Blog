# Local editorial drafts

The owner’s October 21 GitHub account restriction puts remote synchronization and
publication on hold. See [AGENTS.md](../AGENTS.md) and the current
[handoff](../docs/editorial/HANDOFF.md). Do not fetch, pull, push, poll checks,
update PRs or deploy until the owner explicitly reports restoration. No bypass.

## October 21: 911 maintenance

- [HTML preview](idaho-911-shared-technology-local-operations.html)
- [Source/claim ledger](../docs/research/2026-10-21-idaho-911-maintenance.md)
- [Validation record](../docs/editorial/validation-2026-10-21.json)
- Intended final path: `articles/idaho-911-shared-technology-local-operations.html`

Serve the repository root with `python3 -m http.server 5173`; open
`http://127.0.0.1:5173/drafts/idaho-911-shared-technology-local-operations.html`.
The preview uses existing CSS and current shared partials. Production build/check
scripts scan root and articles pages; the draft was also audited separately.

The preview is deliberately absent from public discovery files. It has visible
draft labeling, `robots=noindex,nofollow`, Article `creativeWorkStatus=Draft`, no
canonical, no publication/modification timestamp and no public article URL claim.
No deployment of this directory has been attempted.

After explicit restoration, recheck sources, resolve newer remote work safely and
review the story again. Do not assume the October 5 agenda's items were approved.
The posted FY2026 grant deadline is historical, not an open opportunity. Review
newer minutes and funding guidance; hold or revise if the framing is stale.

At actual publication, move the draft to the intended article path, remove the
editorial-preview sidebar/hold language and noindex, add the production canonical
and OG URL, assign the genuine first-publication timestamp with timezone, and
use NewsArticle/production metadata. Preserve honest Organization authorship and
visible AI/source-method disclosure. Add homepage/news/relevant desk, RSS and
regular sitemap entries; let the build generate latest/news metadata. Re-run local
checks and visuals, then verify normal push, exact remote SHA, deployment and fresh
public article/discovery/image responses before a live claim. No indexing guarantee.

If a draft remains unpublished across days, its preparation date is not a
publication date. Do not silently backdate it or refresh an actually published
article merely to promote it. Establish the October20 article's first-publication
state before deciding how its prepared date metadata should be handled.
