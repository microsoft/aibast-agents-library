#!/usr/bin/env python3
"""
Registry Builder — Auto-generates registry.json from __manifest__ dicts in agent .py files.

Run manually:   python build_registry.py
Or via CI:      Triggered on every push by .github/workflows/build-registry.yml

Scans agents/@publisher/slug.py for __manifest__ dicts and builds:
- registry.json (full index for programmatic access)
- Validates all manifests against schema
- Reports errors for malformed agents

Each entry also carries the stack it belongs to (_stack / _stack_vertical), the
SHA-256 of the exact file indexed, and the date it first landed in git. The
library browse page (library.html) and the metrics snapshot
(scripts/build_metrics.py) both read those fields.
"""

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

AGENTS_DIR = Path("agents")
REGISTRY_FILE = Path("registry.json")
SOLUTIONS_FILE = Path("solutions.json")
REQUIRED_MANIFEST_FIELDS = [
    "schema", "name", "version", "display_name",
    "description", "author", "tags", "category"
]


def load_solutions() -> dict:
    """agent name -> the approved SharePoint listing for that solution.

    solutions.json is the AIBAST SharePoint "Agents Library" catalog: the set
    that was actually advertised to the field, each with a one-pager and a demo
    video. It is authored upstream and is NOT derived from this repo — the repo
    aligns to it. Every agent that implements an advertised solution inherits
    that listing's name, summary, industries, personas and featured tools, so
    the catalog page shows the field what it was sold.
    """
    if not SOLUTIONS_FILE.exists():
        return {}
    try:
        doc = json.loads(SOLUTIONS_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        print(f"  [WARN] cannot read {SOLUTIONS_FILE}: {e}")
        return {}
    out = {}
    for s in doc.get("solutions", []):
        if s.get("repo_agent"):
            out.setdefault(s["repo_agent"], s)
    return out


def stack_of(py_path: Path) -> tuple:
    """(stack, vertical) for agents/@pub/<vertical>_stacks/<name>_stack/x.py.

    Templates and anything outside a *_stacks/*_stack/ folder return (None, None)
    — they are library primitives, not a shipped industry stack.
    """
    parts = py_path.parts
    for i, part in enumerate(parts):
        if part.endswith("_stacks") and i + 1 < len(parts):
            folder = parts[i + 1]
            if folder.endswith("_stack"):
                return folder[: -len("_stack")], part[: -len("_stacks")]
    return None, None


def git_added_dates() -> dict:
    """path -> ISO date the file was first added, from git history.

    CI checks out shallow, so history is often absent. That is not an error:
    the caller carries the previous registry's dates forward instead.
    """
    dates = {}
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--reverse", "--date=iso-strict",
             "--format=%cd", "--name-only", "--", str(AGENTS_DIR)],
            capture_output=True, text=True, timeout=120, check=True,
        ).stdout
    except Exception:
        return dates

    current = None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if line[:4].isdigit() and "T" in line:
            current = line
        elif current and line.endswith(".py"):
            dates.setdefault(line, current)
    return dates


def extract_manifest(py_path: Path) -> dict:
    """Extract __manifest__ dict from a Python file using AST parsing."""
    try:
        source = py_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  [WARN] Syntax error in {py_path}: {e}")
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__manifest__":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, TypeError) as e:
                        print(f"  [WARN] Cannot parse __manifest__ in {py_path}: {e}")
                        return None
    return None


def validate_manifest(py_path: Path, manifest: dict) -> list:
    """Validate a manifest and return list of errors."""
    errors = []

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    name = manifest.get("name", "")
    if not name.startswith("@") or "/" not in name:
        errors.append(f"Invalid name format '{name}' — must be @publisher/slug")

    version = manifest.get("version", "")
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        errors.append(f"Invalid version '{version}' — must be semver (e.g., 1.0.0)")

    if not isinstance(manifest.get("tags", []), list):
        errors.append("tags must be a list")

    return errors


def build_registry():
    """Scan all agent .py files and build registry.json."""
    agents = []
    publishers = set()
    categories = set()
    errors = []

    added_dates = git_added_dates()
    solutions = load_solutions()
    previous = {}
    if REGISTRY_FILE.exists():
        try:
            for a in json.loads(REGISTRY_FILE.read_text(encoding="utf-8")).get("agents", []):
                previous[a.get("name")] = a
        except (ValueError, OSError):
            pass

    for py_path in sorted(AGENTS_DIR.rglob("*.py")):
        manifest = extract_manifest(py_path)
        if manifest is None:
            continue

        validation_errors = validate_manifest(py_path, manifest)
        if validation_errors:
            for err in validation_errors:
                errors.append(f"{py_path}: {err}")
            continue

        name = manifest["name"]
        publisher = name.split("/")[0]
        publishers.add(publisher)
        categories.add(manifest.get("category", "uncategorized"))

        # Add file metadata
        content = py_path.read_text(encoding="utf-8")
        raw = content.encode("utf-8")
        stack, vertical = stack_of(py_path)
        manifest["_file"] = py_path.as_posix()
        manifest["_size_kb"] = round(len(raw) / 1024, 1)
        manifest["_lines"] = len(content.split('\n'))
        manifest["_sha256"] = hashlib.sha256(raw).hexdigest()
        manifest["_stack"] = stack
        manifest["_stack_vertical"] = vertical
        # git history first, last good registry second — a shallow CI checkout
        # must not blank the date the catalog already published.
        added = added_dates.get(py_path.as_posix()) or previous.get(name, {}).get("_added_at")
        if added:
            manifest["_added_at"] = added

        # The advertised listing, when this agent implements an approved solution.
        sol = solutions.get(name)
        if sol:
            manifest["_solution"] = {
                "advertised_name": sol.get("advertised_name"),
                "slot": sol.get("slot"),
                "executive_summary": sol.get("executive_summary"),
                "industries": sol.get("industries", []),
                "personas": sol.get("personas", []),
                "featured_tools": sol.get("featured_tools", []),
                "capabilities": sol.get("capabilities", []),
                "outcomes": sol.get("outcomes", []),
                "customer_scenario": sol.get("customer_scenario", []),
                "has_onepager": bool(sol.get("onepager")),
                "has_demo_video": bool(sol.get("demo_video")),
            }

        agents.append(manifest)

    stacks = {}
    tiers = {}
    for a in agents:
        tiers[a.get("quality_tier", "community")] = tiers.get(a.get("quality_tier", "community"), 0) + 1
        if not a.get("_stack"):
            continue
        key = f"{a['_stack_vertical']}/{a['_stack']}"
        entry = stacks.setdefault(key, {
            "stack": a["_stack"],
            "vertical": a["_stack_vertical"],
            "display_name": a["_stack"].replace("_", " ").title(),
            "path": str(Path(a["_file"]).parent.as_posix()),
            "agents": [],
        })
        entry["agents"].append(a["name"])

    stack_rows = sorted(stacks.values(), key=lambda s: (s["vertical"], s["stack"]))
    for s in stack_rows:
        s["agent_count"] = len(s["agents"])

    registry = {
        "schema": "rapp-registry/1.0",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_agents": len(agents),
            "publishers": len(publishers),
            "categories": len(categories),
            "total_stacks": len(stack_rows),
            "total_verticals": len({s["vertical"] for s in stack_rows}),
            "total_lines": sum(a["_lines"] for a in agents),
            "total_kb": round(sum(a["_size_kb"] for a in agents), 1),
            "publisher_list": sorted(publishers),
            "category_list": sorted(categories),
            "tier_counts": dict(sorted(tiers.items(), key=lambda kv: -kv[1])),
        },
        "stacks": stack_rows,
        "agents": agents
    }

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    print(f"[OK] Registry built: {len(agents)} agents from {len(publishers)} publishers")
    print(f"  Categories: {', '.join(sorted(categories))}")
    print(f"  Publishers: {', '.join(sorted(publishers))}")

    if errors:
        print(f"\n[WARN] {len(errors)} validation errors:")
        for err in errors:
            print(f"  - {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(build_registry())
