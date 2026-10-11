"""AIBAST agent templates as a prototype's starting point, verified before anything runs.

Templates come only from the published AIBAST library (one fixed origin), and a file is accepted
only if its sha256 matches the registry entry from that same published snapshot. Anything else is
refused. Standard library only.

  python3 templates.py list [query]
  python3 templates.py fetch @aibast-agents-library/claims-processing <agents-dir>
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = "https://microsoft.github.io/aibast-agents-library/"  # the only source
NAME = re.compile(r"^@aibast-agents-library/[a-z0-9-]{1,80}$")
SAFE_FILE = re.compile(r"^agents/@aibast-agents-library/[A-Za-z0-9_/.-]+_agent\.py$")
MAX_BYTES = 300_000


class TemplateError(RuntimeError):
    pass


def _get(path: str, limit: int) -> bytes:
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        data = r.read(limit + 1)
    if len(data) > limit:
        raise TemplateError(f"{path} is larger than expected")
    return data


def registry() -> dict:
    return json.loads(_get("registry.json", 5_000_000))


def listing(query: str = "") -> list[dict]:
    q = query.lower()
    out = []
    for a in registry().get("agents", []):
        text = " ".join([a.get("name", ""), a.get("display_name", ""), a.get("description", ""), a.get("category", "")]).lower()
        if not q or q in text:
            out.append({k: a.get(k) for k in ("name", "display_name", "description", "category", "quality_tier")})
    return out


def fetch(name: str, agents_dir: Path) -> dict:
    """Download one template into agents_dir after verifying it against the published registry."""
    if not name.startswith("@"):
        name = "@aibast-agents-library/" + name
    if not NAME.match(name):
        raise TemplateError("Not an AIBAST template name.")
    entry = next((a for a in registry().get("agents", []) if a.get("name") == name), None)
    if not entry:
        raise TemplateError(f"{name} is not in the published AIBAST registry.")
    rel, want = entry.get("_file", ""), entry.get("_sha256", "")
    if not SAFE_FILE.match(rel) or ".." in rel or not re.fullmatch(r"[0-9a-f]{64}", want or ""):
        raise TemplateError("The registry entry doesn't describe a single agent file with a hash.")
    data = _get(rel, MAX_BYTES)
    got = hashlib.sha256(data).hexdigest()
    if got != want:
        raise TemplateError(f"Hash mismatch for {name}: refusing to install it.")
    dest = Path(agents_dir) / Path(rel).name
    dest.write_bytes(data)
    return {"name": name, "display_name": entry.get("display_name"), "file": dest.name, "sha256": got,
            "source": BASE + rel}


if __name__ == "__main__":
    try:
        if sys.argv[1] == "list":
            for a in listing(" ".join(sys.argv[2:])):
                print(f"{a['name'].split('/')[-1]:40} {a['display_name']}")
        elif sys.argv[1] == "fetch":
            print(json.dumps(fetch(sys.argv[2], Path(sys.argv[3]))))
        else:
            raise SystemExit(__doc__)
    except TemplateError as e:
        raise SystemExit(f"✗ {e}")
