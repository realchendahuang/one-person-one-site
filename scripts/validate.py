#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sites.json"
REQUIRED = ["name", "url", "owner", "description", "languages", "region", "tags"]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def valid_http_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def main() -> None:
    try:
        sites = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Cannot parse {DATA}: {exc}")

    if not isinstance(sites, list):
        fail("data/sites.json must contain a JSON array")

    seen = set()
    for i, site in enumerate(sites, start=1):
        if not isinstance(site, dict):
            fail(f"Entry #{i} must be an object")

        missing = [key for key in REQUIRED if key not in site]
        if missing:
            fail(f"Entry #{i} missing fields: {', '.join(missing)}")

        for field in ["name", "owner", "description", "region"]:
            if not isinstance(site[field], str) or not site[field].strip():
                fail(f"Entry #{i} field '{field}' must be a non-empty string")

        if len(site["description"]) > 240:
            fail(f"Entry #{i} description exceeds 240 characters")

        if not valid_http_url(site["url"]):
            fail(f"Entry #{i} has invalid URL: {site['url']}")

        canonical = site["url"].rstrip("/").lower()
        if canonical in seen:
            fail(f"Duplicate URL found: {site['url']}")
        seen.add(canonical)

        if not isinstance(site["languages"], list) or not site["languages"]:
            fail(f"Entry #{i} languages must be a non-empty array")

        if not isinstance(site["tags"], list) or not (1 <= len(site["tags"]) <= 8):
            fail(f"Entry #{i} tags must contain 1 to 8 items")

        if len(site["tags"]) != len(set(site["tags"])):
            fail(f"Entry #{i} tags contain duplicates")

        if "feed" in site and site["feed"] and not valid_http_url(site["feed"]):
            fail(f"Entry #{i} has invalid feed URL: {site['feed']}")

        allowed = set(REQUIRED + ["feed"])
        extra = sorted(set(site) - allowed)
        if extra:
            fail(f"Entry #{i} contains unsupported fields: {', '.join(extra)}")

    print(f"OK: validated {len(sites)} site(s)")


if __name__ == "__main__":
    main()
