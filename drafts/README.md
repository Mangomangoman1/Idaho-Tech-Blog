# Local editorial drafts

The owner’s October 21 GitHub account restriction puts remote synchronization and
publication on hold. See [AGENTS.md](../AGENTS.md) and the current
[handoff](../docs/editorial/HANDOFF.md). Do not fetch, pull, push, poll checks,
update PRs or deploy until the owner explicitly reports restoration. No bypass.

## October 24–25: reporting quality hold

No fourth draft. The [Ammon transit dossier](../docs/research/2026-10-24-ammon-gift-service-boundary.md)
preserves a distinct lead, primary evidence and unresolved verification gates.
All three previews below retain their original source, images, authorship and
undated unpublished status. Latest all-draft/local preservation audit:
`python3 docs/editorial/checks/2026-10-25-drafts.py` with the root server on5173.
The [October 25 validation](../docs/editorial/validation-2026-10-25.json) records
actual checks; no remote serving or source-status refresh of those drafts implied.

## October 23: INL software access and licensing

- [HTML preview](inl-software-browser-access-licensing.html)
- [Source/claim ledger](../docs/research/2026-10-23-inl-software-access-licensing.md)
- [Validation record](../docs/editorial/validation-2026-10-23.json)
- Intended final path: `articles/inl-software-browser-access-licensing.html`

Recheck the October22 notice/September24 selection context, ELEMENT/E-Lucid
goals and current product/contract status before release. FieldSim is an existing
example, not an identified selection in either new project. No current license,
pricing, support, delivered hosted app or savings were tested. Do not create an
account, accept a license or contact anyone as part of release without authorization.

Reproduce all three local draft audits with root server on5173 and:
`python3 docs/editorial/checks/2026-10-23-drafts.py`.
Uses existing environment tools. Checks preserve prior draft source/images/ledgers/
checkers against local94c7b67. No new production dependency or remote operation.

## October 22: court AI and document control

- [HTML preview](idaho-court-ai-document-control.html)
- [Source/claim ledger](../docs/research/2026-10-22-idaho-court-ai-document-control.md)
- [Validation record](../docs/editorial/validation-2026-10-22.json)
- Intended final path: `articles/idaho-court-ai-document-control.html`

The October19 announcement releases an August2026 report. Its possible operational
chatbot is not a verified deployed service. Recheck new court orders/policies and
tool decisions before release; distinguish adopted principles from draft appendices
and proposals. No case advice or allegations about individuals. Use the common
publication procedure below after the owner explicitly reports restoration.

Reproduce both drafts’ local audit with a root server on5173 and:
`python3 docs/editorial/checks/2026-10-22-drafts.py`.
Existing Pillow, Playwright and system Chromium are used; not a new production
dependency or CI requirement. The audit also verifies the911 source/assets remain
unchanged from local commit99fd6cf.

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
