#!/usr/bin/env python3
"""Point the analytics loader at this project's own Web Analytics paths.

Runs on Vercel after the build and checks. With Web Analytics enabled, Vercel
provides VERCEL_OBSERVABILITY_CLIENT_CONFIG, the browser config that the
official @vercel/analytics package reads (its "analytics" part holds the
project's script and intake paths on our own domain, which ad blockers are far
less likely to block than the default /_vercel/insights). This copies the same
logic as the package's loadProps() into assets/stack.js. Without the config
(local builds, analytics off) the loader keeps the default path.
Only the build machine's copy of assets/stack.js changes.
"""
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOADER = ROOT / "assets" / "stack.js"
SAFE = re.compile(r"^(https://[A-Za-z0-9.-]+)?/?[A-Za-z0-9._~/-]*$")
DATA_KEYS = ["endpoint", "viewEndpoint", "eventEndpoint", "sessionEndpoint", "dsn"]


def absolute(url):
    return url if url.startswith(("https://", "/")) else "/" + url


def settings():
    raw = os.environ.get("VERCEL_OBSERVABILITY_CLIENT_CONFIG", "")
    try:
        props = (json.loads(raw) or {}).get("analytics") or {}
    except ValueError:
        props = {}
    base = os.environ.get("VERCEL_OBSERVABILITY_BASEPATH") or props.get("basePath")
    src, data = None, {}
    if props.get("scriptSrc"):
        src = absolute(props["scriptSrc"])
    elif base:
        src = absolute(f"{base.rstrip('/')}/insights/script.js")
    for key in DATA_KEYS:
        if props.get(key):
            data[key] = absolute(props[key]) if key != "dsn" and key != "endpoint" else props[key]
    if "endpoint" not in data and base:
        data["endpoint"] = absolute(f"{base.rstrip('/')}/insights")
    return src, data


def main():
    src, data = settings()
    if not src or not SAFE.match(src) or any(k != "dsn" and not SAFE.match(v) for k, v in data.items()):
        print("analytics: no project path in config, using /_vercel/insights")
        return
    js = LOADER.read_text()
    js = re.sub(r'var SRC = "[^"]*";', f"var SRC = {json.dumps(src)};", js, count=1)
    js = re.sub(r"var DATA = \{[^}]*\};", f"var DATA = {json.dumps(data)};", js, count=1)
    LOADER.write_text(js)
    print(f"analytics: loader points at {src} with {sorted(data)}")


if __name__ == "__main__":
    main()
