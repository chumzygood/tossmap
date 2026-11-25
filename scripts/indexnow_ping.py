#!/usr/bin/env python3
"""POST changed or all sitemap URLs to IndexNow for tossmap.com (stdlib only)."""
import argparse, json, os, re, sys, urllib.error, urllib.request, xml.etree.ElementTree as ET

HOST = "tossmap.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_CANDIDATES = [
    "/workspace/tossmap/indexnow-key.txt",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "indexnow-key.txt"),
    "data/indexnow-key.txt",
]

def load_key(path=None):
    paths = [path] if path else KEY_CANDIDATES
    for p in paths:
        if p and os.path.isfile(p):
            key = open(p).read().strip()
            if re.fullmatch(r"[A-Fa-f0-9]{32}", key):
                return key
    raise SystemExit("IndexNow key file not found (expected data/indexnow-key.txt)")

def sitemap_urls(path):
    tree = ET.parse(path)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [u.text.strip() for u in tree.getroot().findall("sm:url/sm:loc", ns) if u.text]
    if not urls:
        raise SystemExit(f"No URLs found in {path}")
    return urls

def main():
    ap = argparse.ArgumentParser(description="Ping IndexNow for TossMap")
    ap.add_argument("--all", action="store_true", help="Ping every URL in the sitemap")
    ap.add_argument("--changed", nargs="+", metavar="URL", help="Ping these URLs only")
    ap.add_argument("--sitemap", default="docs/sitemap.xml")
    ap.add_argument("--key-file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    key = load_key(args.key_file)
    if args.changed:
        urls = args.changed
    elif args.all:
        urls = sitemap_urls(args.sitemap)
    else:
        raise SystemExit("Pass --all or --changed URL [URL ...]")
    payload = {
        "host": HOST,
        "key": key,
        "keyLocation": f"https://{HOST}/{key}.txt",
        "urlList": urls,
    }
    if args.dry_run:
        print(f"Would POST {len(urls)} URLs to {ENDPOINT}")
        print(f"keyLocation: https://{HOST}/{key}.txt")
        return 0
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"IndexNow HTTP {resp.status} ({len(urls)} URLs)")
            extra = resp.read().decode("utf-8", "replace")
            if extra.strip():
                print(extra)
            return 0
    except urllib.error.HTTPError as exc:
        print(f"IndexNow HTTP {exc.code} ({len(urls)} URLs)")
        print(exc.read().decode("utf-8", "replace"))
        return 1
    except urllib.error.URLError as exc:
        print(f"IndexNow request failed: {exc}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
