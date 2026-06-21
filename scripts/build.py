#!/usr/bin/env python3
"""Build step for The Idaho Stack.

Injects the canonical site header and footer (from /partials) into every page
so navigation and footer are defined ONCE and stay consistent across the site.

Pages opt out simply by not containing a <header> (e.g. redirect stubs).
The script is idempotent: running it twice produces no further changes.

    python3 scripts/build.py          # rewrite pages in place
    python3 scripts/build.py --check  # fail if any page is out of date (CI)
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HEADER = (ROOT / "partials" / "header.html").read_text().strip()
FOOTER = (ROOT / "partials" / "footer.html").read_text().strip()

HEADER_RE = re.compile(r"<header\b.*?</header>", re.S)
FOOTER_RE = re.compile(r"<footer\b.*?</footer>", re.S)


def pages():
    yield from sorted(ROOT.glob("*.html"))
    yield from sorted((ROOT / "articles").glob("*.html"))


def render(html):
    if "<header" not in html:
        return html  # redirect stubs and partial-less pages opt out
    html = HEADER_RE.sub(lambda _: HEADER, html, count=1)
    html = FOOTER_RE.sub(lambda _: FOOTER, html, count=1)
    return html


def main():
    check = "--check" in sys.argv
    stale, changed = [], []
    for p in pages():
        original = p.read_text()
        built = render(original)
        if built == original:
            continue
        if check:
            stale.append(p.relative_to(ROOT))
        else:
            p.write_text(built)
            changed.append(p.relative_to(ROOT))
    if check:
        if stale:
            print("Out of date (run `python3 scripts/build.py`):")
            for s in stale:
                print(f"  {s}")
            sys.exit(1)
        print("All pages up to date.")
    else:
        for c in changed:
            print(f"updated {c}")
        print(f"done: {len(changed)} file(s) updated")


if __name__ == "__main__":
    main()
