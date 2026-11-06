"""Public Microsoft content republished in the library static API (api/v1/public/).

The hand-authored input is tools/public_sources.json. Each source names one
public Microsoft page, the file a value is read from, how to read it, and a
pinned snapshot: the value, the sha256 of the file it came from and when it
was fetched. The library build reads only the snapshot, so it is offline and
byte-identical. Refreshing is a separate, explicit step:

    python tools/library_api_public.py --refresh   # fetch, re-extract, update the snapshot if the file changed
    python tools/library_api_public.py --verify    # fetch and fail if any live file no longer matches its sha256

First source: Copilot Studio credit rates, from Microsoft's Copilot Studio
estimator (ported from PR #298).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_PUBLIC_INDEX = "aibast-public-index/1.0"
SCHEMA_PUBLIC = "aibast-public/1.0"
SOURCES = "tools/public_sources.json"
ROOT = Path(__file__).resolve().parents[1]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "aibast-agents-library/public-api"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def js_object(source: str, symbol: str) -> dict:
    """The literal object assigned to `const <symbol> = {...};`: comments dropped, keys quoted, then strict JSON."""
    match = re.search(r"(?:const|let|var)\s+" + re.escape(symbol) + r"\s*=\s*(\{.*?\n\})\s*;", source, re.S)
    if not match:
        raise ValueError(f"{symbol} not found")
    body = re.sub(r"//[^\n]*", "", match.group(1))
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"([{,]\s*)([A-Za-z_$][\w$]*)\s*:", r'\1"\2":', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body)
    value = json.loads(body)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{symbol} is not a non-empty object")
    return value


EXTRACT = {"js-object": lambda text, spec: js_object(text, spec["symbol"])}


def load_sources(root: Path = ROOT) -> dict:
    return json.loads((root / SOURCES).read_text(encoding="utf-8"))


def public_files(root: Path = ROOT) -> tuple[dict[str, object], dict]:
    sources = load_sources(root)["sources"]
    files: dict[str, object] = {}
    index = []
    for s in sources:
        snap = s["snapshot"]
        files[f"api/v1/public/{s['id']}.json"] = {
            "schema": SCHEMA_PUBLIC,
            "id": s["id"],
            "title": s["title"],
            "data": snap["data"],
            "units": s.get("units"),
            "disclaimer": s["disclaimer"],
            "provenance": {"page": s["page"], "file": s["file"], "file_sha256": snap["file_sha256"],
                           "extract": s["extract"], "fetched_at": snap["fetched_at"],
                           "documented_at": s.get("documented_at", [])},
        }
        index.append({"id": s["id"], "title": s["title"], "doc": f"api/v1/public/{s['id']}.json",
                      "page": s["page"]})
    files["api/v1/public/index.json"] = {
        "schema": SCHEMA_PUBLIC_INDEX,
        "title": "Public Microsoft content, republished with provenance",
        "description": "Each document holds one value read exactly from a public Microsoft page, with the source "
                       "URL and the sha256 of the file it was read from.",
        "sources": index,
    }
    return files, {"public_sources": len(index)}


def refresh(verify_only: bool) -> int:
    data = load_sources()
    stale = 0
    for s in data["sources"]:
        raw = fetch(s["file"])
        digest = hashlib.sha256(raw).hexdigest()
        if digest == s["snapshot"]["file_sha256"]:
            print(f"{s['id']}: unchanged ({digest[:12]})")
            continue
        stale += 1
        print(f"{s['id']}: live file changed ({s['snapshot']['file_sha256'][:12]} -> {digest[:12]})")
        if not verify_only:
            s["snapshot"] = {"data": EXTRACT[s["extract"]["kind"]](raw.decode("utf-8"), s["extract"]),
                             "file_sha256": digest,
                             "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if stale and not verify_only:
        (ROOT / SOURCES).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("snapshot updated; run tools/build_library_api.py")
        return 0
    return 1 if (stale and verify_only) else 0


if __name__ == "__main__":
    if "--refresh" in sys.argv or "--verify" in sys.argv:
        sys.exit(refresh(verify_only="--verify" in sys.argv))
    print(__doc__)
