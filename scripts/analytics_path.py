#!/usr/bin/env python3
"""Point the analytics loader at this project's unique Web Analytics path.

Runs on Vercel after the build and checks. When Web Analytics is enabled,
Vercel provides VERCEL_OBSERVABILITY_BASEPATH, a project-specific path on our
own domain that ad blockers are far less likely to block than the default
/_vercel/insights. Without it (local builds, analytics off) the loader keeps
the default path. Only the build machine's copy of assets/stack.js changes.
"""
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOADER = ROOT / "assets" / "stack.js"


def main():
    base = os.environ.get("VERCEL_OBSERVABILITY_BASEPATH", "").strip().strip("/")
    if not base or not re.fullmatch(r"[A-Za-z0-9._~/-]+", base):
        print("analytics: no unique path set, using /_vercel/insights")
        return
    path = f"/{base}/insights"
    js = LOADER.read_text()
    new = re.sub(r'var ANALYTICS_BASE = "[^"]*";', f'var ANALYTICS_BASE = "{path}";', js, count=1)
    LOADER.write_text(new)
    print(f"analytics: loader points at {path}")


if __name__ == "__main__":
    main()
