#!/usr/bin/env python3
"""
Registry Builder — Auto-generates registry.json from __manifest__ dicts in agent .py files.

Run manually:   python build_registry.py
Or via CI:      Triggered on every push by .github/workflows/build-registry.yml

Scans agents/@publisher/slug.py for __manifest__ dicts and builds:
- registry.json (full index for programmatic access)
- Validates all manifests against schema
- Reports errors for malformed agents
"""

import ast
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

AGENTS_DIR = Path("agents")
REGISTRY_FILE = Path("registry.json")
REQUIRED_MANIFEST_FIELDS = [
    "schema", "name", "version", "display_name",
    "description", "author", "tags", "category"
]


def extract_manifest(py_path: Path) -> dict:
    """Extract __manifest__ dict from a Python file using AST parsing."""
    try:
        source = py_path.read_text()
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  ⚠ Syntax error in {py_path}: {e}")
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__manifest__":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, TypeError) as e:
                        print(f"  ⚠ Cannot parse __manifest__ in {py_path}: {e}")
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
        content = py_path.read_text()
        manifest["_file"] = str(py_path)
        manifest["_size_kb"] = round(py_path.stat().st_size / 1024, 1)
        manifest["_lines"] = len(content.split('\n'))

        agents.append(manifest)

    registry = {
        "schema": "rapp-registry/1.0",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_agents": len(agents),
            "publishers": len(publishers),
            "categories": len(categories),
            "publisher_list": sorted(publishers),
            "category_list": sorted(categories)
        },
        "agents": agents
    }

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    print(f"✓ Registry built: {len(agents)} agents from {len(publishers)} publishers")
    print(f"  Categories: {', '.join(sorted(categories))}")
    print(f"  Publishers: {', '.join(sorted(publishers))}")

    if errors:
        print(f"\n⚠ {len(errors)} validation errors:")
        for err in errors:
            print(f"  - {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(build_registry())
