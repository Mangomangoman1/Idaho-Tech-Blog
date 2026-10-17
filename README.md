# The Idaho Stack

Idaho technology, business, and infrastructure publication plus future B2B regional intelligence hub.

## Run locally

```bash
python3 -m http.server 5173
```

Open `http://localhost:5173`.

## Current launch package

- Current working brand: The Idaho Stack
- Home page with publication/hub positioning
- Three launch articles
- About, Contribute, Interviews, Editorial Policy, Field Notes, Submit, Companies pages
- robots.txt, sitemap.xml, llms.txt

## Editorial operations

Start each daily session with [the handoff](docs/editorial/HANDOFF.md) and [operating rules](docs/editorial/OPERATIONS.md). [Inventory/backlog](docs/editorial/INVENTORY.md) and the [Google publishing audit](docs/editorial/GOOGLE-AUDIT.md) record evidence and limits.

Run `npm run build` and `npm run check` before release. The build generates the newest-first homepage article list and prunes the news sitemap; run it even on quality-hold days. Vercel runs these checks on deployment.
