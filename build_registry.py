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
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

AGENTS_DIR = Path("agents")
REGISTRY_FILE = Path("registry.json")
SOLUTIONS_FILE = Path("solutions.json")
FIRST_PARTY_FILE = Path("first_party.json")
ONEPAGER_CONTENT_FILE = Path("state/onepager_content.json")
SOLUTION_COPY_FILE = Path("solutions/catalog.json")
DEMO_CASES_DIR = Path("tests/demo_cases")
REQUIRED_MANIFEST_FIELDS = [
    "schema", "name", "version", "display_name",
    "description", "author", "tags", "category"
]
REQUIRED_FIRST_PARTY_FIELDS = [
    "id", "name", "product", "vertical", "deck_status",
    "description", "use_cases", "doc_status", "overview_url", "source_slide"
]
FIRST_PARTY_SCHEMA = "aibast-first-party/1.0"
FIRST_PARTY_DECK_STATUSES = {"GA", "Preview"}
FIRST_PARTY_LIFECYCLES = {"Preview"}
FIRST_PARTY_DOC_STATUSES = {"dedicated"}


def load_first_party(errors: list) -> list:
    """Microsoft first-party agents the field should evaluate before building custom.

    first_party.json is authored, not derived: these agents ship inside
    Dynamics 365, Microsoft 365 Copilot, and Agent 365, so they have no .py
    file and no __manifest__ to scan. They stay out of the `agents` array
    (which counts code this repo owns) and land in their own `first_party`
    array so total_agents, catalog kinds, and the metrics snapshot stay honest.

    Only current public Microsoft Learn links that document the exact
    capability are published. Lifecycle is optional and appears only when the
    current Learn page explicitly states it; source-deck lifecycle is retained
    separately as deck_status and is never promoted to current lifecycle.
    """
    if not FIRST_PARTY_FILE.exists():
        return []
    try:
        doc = json.loads(FIRST_PARTY_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        errors.append(f"{FIRST_PARTY_FILE}: cannot read ({e})")
        return []

    if doc.get("schema") != FIRST_PARTY_SCHEMA:
        errors.append(
            f"{FIRST_PARTY_FILE}: schema must be {FIRST_PARTY_SCHEMA}"
        )
    entries = doc.get("agents", [])
    if not isinstance(entries, list):
        errors.append(f"{FIRST_PARTY_FILE}: agents must be a list")
        return []
    if doc.get("count") != len(entries):
        errors.append(
            f"{FIRST_PARTY_FILE}: count {doc.get('count')} does not match "
            f"{len(entries)} agents"
        )

    rows = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append(f"{FIRST_PARTY_FILE}: every agent must be an object")
            continue
        label = entry.get("id") or entry.get("name") or "<unnamed>"
        missing = [f for f in REQUIRED_FIRST_PARTY_FIELDS if not entry.get(f)]
        if missing:
            errors.append(f"{FIRST_PARTY_FILE}:{label}: missing {', '.join(missing)}")
            continue
        if entry["id"] in seen:
            errors.append(f"{FIRST_PARTY_FILE}:{label}: duplicate id")
            continue
        seen.add(entry["id"])
        if entry["deck_status"] not in FIRST_PARTY_DECK_STATUSES:
            errors.append(
                f"{FIRST_PARTY_FILE}:{label}: deck_status must be one of "
                f"{sorted(FIRST_PARTY_DECK_STATUSES)}"
            )
            continue
        lifecycle = entry.get("lifecycle")
        if lifecycle is not None:
            if lifecycle not in FIRST_PARTY_LIFECYCLES:
                errors.append(
                    f"{FIRST_PARTY_FILE}:{label}: lifecycle must be one of "
                    f"{sorted(FIRST_PARTY_LIFECYCLES)}"
                )
                continue
            if not entry.get("lifecycle_source_url"):
                errors.append(
                    f"{FIRST_PARTY_FILE}:{label}: lifecycle requires "
                    "lifecycle_source_url"
                )
                continue
        if entry["doc_status"] not in FIRST_PARTY_DOC_STATUSES:
            errors.append(
                f"{FIRST_PARTY_FILE}:{label}: doc_status must be one of "
                f"{sorted(FIRST_PARTY_DOC_STATUSES)}"
            )
            continue
        urls = [
            entry.get("overview_url"),
            entry.get("configure_url"),
            entry.get("lifecycle_source_url"),
        ]
        if any(
            url is not None
            and not url.startswith("https://learn.microsoft.com/")
            for url in urls
        ):
            errors.append(
                f"{FIRST_PARTY_FILE}:{label}: published URLs must use "
                "https://learn.microsoft.com/"
            )
            continue
        use_cases = entry["use_cases"]
        if (
            not isinstance(use_cases, list)
            or len(use_cases) < 3
            or any(not isinstance(value, str) or not value.strip() for value in use_cases)
        ):
            errors.append(
                f"{FIRST_PARTY_FILE}:{label}: use_cases must contain at least "
                "three non-empty strings"
            )
            continue

        row = dict(entry)
        row["_catalog_kind"] = "first_party"
        row["_documented"] = True
        row["_availability_label"] = lifecycle or "Available"
        rows.append(row)

    rows.sort(key=lambda r: (r["vertical"], r["name"]))
    return rows


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
    grouped = {}
    for s in doc.get("solutions", []):
        if s.get("repo_agent"):
            grouped.setdefault(s["repo_agent"], []).append(s)

    out = {}
    for name, rows in grouped.items():
        primary = next((row for row in rows if row.get("is_primary")), rows[0])
        selected = dict(primary)
        selected["_aliases"] = [
            row.get("advertised_display") or row.get("advertised_name")
            for row in rows
            if row is not primary
        ]
        out[name] = selected
    return out


def load_demo_cases() -> dict:
    """agent package name -> locked conversational demo metadata."""
    out = {}
    if not DEMO_CASES_DIR.exists():
        return out
    for path in sorted(DEMO_CASES_DIR.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as e:
            print(f"  [WARN] cannot read {path}: {e}")
            continue
        name = doc.get("agent")
        if not name:
            continue
        cases = doc.get("cases", [])
        out[name] = {
            "slug": path.stem,
            "case_count": len(cases),
            "personas": sorted({
                case.get("persona") for case in cases if case.get("persona")
            }),
            "prompts": [
                case["prompt"] for case in cases
                if case.get("prompt")
            ][:3],
        }
    return out


def load_onepager_content() -> dict:
    """one-pager filename -> content extracted from the approved PowerPoint."""
    if not ONEPAGER_CONTENT_FILE.exists():
        return {}
    try:
        doc = json.loads(ONEPAGER_CONTENT_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        print(f"  [WARN] cannot read {ONEPAGER_CONTENT_FILE}: {e}")
        return {}
    return doc.get("onepagers", {})


def load_solution_copy() -> dict:
    """agent package name -> curated, field-ready copy grounded in its slide."""
    if not SOLUTION_COPY_FILE.exists():
        return {}
    try:
        doc = json.loads(SOLUTION_COPY_FILE.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        print(f"  [WARN] cannot read {SOLUTION_COPY_FILE}: {e}")
        return {}
    return doc.get("solutions", {})


def words(value: str) -> set:
    return {
        word.rstrip("s")
        for word in re.findall(r"[a-z0-9]+", (value or "").lower())
        if word not in {"agent", "suite", "energy", "operations", "library"}
    }


def select_module(agent_name: str, solution: dict, slide: dict):
    """Choose the matching module when one PowerPoint represents a suite."""
    modules = slide.get("modules", [])
    if not modules:
        return None
    candidates = " ".join([
        agent_name.split("/")[-1],
        solution.get("advertised_name") or "",
        solution.get("canonical_name") or "",
    ])
    candidate_words = words(candidates)
    ranked = sorted(
        modules,
        key=lambda module: len(candidate_words & words(module.get("name", ""))),
        reverse=True,
    )
    return ranked[0] if ranked and candidate_words & words(ranked[0].get("name", "")) else None


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
                vertical = part[: -len("_stacks")]
                if vertical == "software_dp":
                    vertical = "software_digital_products"
                return folder[: -len("_stack")], vertical
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


def resolve_added_date(
    py_path: Path,
    name: str,
    added_dates: dict,
    previous: dict,
):
    """Preserve published dates when a shallow checkout has incomplete history."""
    return (
        previous.get(name, {}).get("_added_at")
        or added_dates.get(py_path.as_posix())
    )


def build_registry():
    """Scan all agent .py files and build registry.json."""
    agents = []
    publishers = set()
    categories = set()
    errors = []

    added_dates = git_added_dates()
    solutions = load_solutions()
    first_party = load_first_party(errors)
    onepager_content = load_onepager_content()
    solution_copy = load_solution_copy()
    demo_cases = load_demo_cases()
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
        install_slug = re.sub(
            r"[^a-z0-9]+",
            "_",
            manifest["name"].split("/", 1)[-1].lower(),
        ).strip("_")
        manifest["_install_prefix"] = f"{install_slug}__"
        manifest["_install_filename"] = (
            f"{manifest['_install_prefix']}"
            f"{manifest['_sha256'][:12]}_agent.py"
        )
        manifest["_stack"] = stack
        manifest["_stack_vertical"] = vertical
        manifest["_synthetic_data"] = bool(
            "synthetic" in content.lower() or "demo data" in content.lower()
        )
        added = resolve_added_date(py_path, name, added_dates, previous)
        if added:
            manifest["_added_at"] = added

        # The advertised listing, when this agent implements an approved solution.
        sol = solutions.get(name)
        if sol:
            slide = onepager_content.get(sol.get("onepager"), {})
            curated = solution_copy.get(name, {})
            module = select_module(name, sol, slide) if slide else None
            actions = slide.get("agent_actions", {}).get("items", [])
            outcomes = slide.get("business_outcomes", {}).get("items", [])
            challenges = slide.get("customer_challenge", {}).get("items", [])
            featured_tools = slide.get("featured_tools") or sol.get("featured_tools", [])
            manifest["_solution"] = {
                # The one-pager slide title is what the field saw on screen;
                # the list row name is internal SharePoint taxonomy. Both are
                # published so a seller can find the solution either way.
                "advertised_name": (
                    curated.get("display_name")
                    or (module or {}).get("name")
                    or sol.get("advertised_display")
                    or sol.get("advertised_name")
                ),
                "sharepoint_list_name": sol.get("sharepoint_list_name") or sol.get("advertised_name"),
                "slot": sol.get("slot"),
                "executive_summary": sol.get("executive_summary"),
                "industries": sol.get("industries", []),
                "personas": sol.get("personas", []),
                "featured_tools": featured_tools,
                "agent_requirements": slide.get("agent_requirements", []),
                "capabilities": actions or sol.get("capabilities", []),
                "outcomes": outcomes or sol.get("outcomes", []),
                "customer_scenario": challenges or sol.get("customer_scenario", []),
                "slide_title": slide.get("title"),
                "slide_summary": slide.get("executive_summary"),
                "scenario_name": slide.get("scenario_name"),
                "challenge_intro": slide.get("customer_challenge", {}).get("intro"),
                "actions_intro": slide.get("agent_actions", {}).get("intro"),
                "outcomes_intro": slide.get("business_outcomes", {}).get("intro"),
                "opportunity_statements": slide.get("opportunity_statements", []),
                "module_name": (module or {}).get("name"),
                "module_description": (module or {}).get("description"),
                "source_verified": bool(slide),
                "sales_headline": curated.get("sales_headline"),
                "card_pitch": curated.get("card_pitch"),
                "why_try": curated.get("why_try"),
                "customer_challenge_copy": curated.get("customer_challenge"),
                "microsoft_ai_story": curated.get("microsoft_ai_story"),
                "business_value": curated.get("business_value", []),
                "search_terms": curated.get("search_terms", []),
                "journey_stage": curated.get("journey_stage"),
                "blueprint_role": curated.get("blueprint_role"),
                "sample_prompts": curated.get("sample_prompts", []),
                "architecture": curated.get("architecture"),
                "curated_copy": bool(curated),
                "onepager": sol.get("onepager"),
                "demo_video": sol.get("demo_video"),
                "has_onepager": bool(sol.get("onepager")),
                "has_demo_video": bool(sol.get("demo_video")),
                "promise_coverage": sol.get("promise_coverage"),
                "is_primary": bool(sol.get("is_primary")),
                "aliases": sol.get("_aliases", []),
            }

        demo = demo_cases.get(name)
        if demo:
            manifest["_demo"] = demo
            package_dir = Path("solutions") / demo["slug"]
            if manifest.get("_solution") and package_dir.is_dir():
                package = {"slug": demo["slug"]}
                for key, filename in (
                    ("quest_url", "quest.html"),
                    ("manual_tutorial_url", "manual-tutorial.html"),
                    ("export_manifest_url", "export-manifest.json"),
                ):
                    path = package_dir / filename
                    if path.exists():
                        package[key] = path.as_posix()
                manifest["_solution"]["package"] = package

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
        s["stack_type"] = "multi_agent" if s["agent_count"] > 1 else "solution_container"

    for agent in agents:
        if agent.get("_solution"):
            agent["_catalog_kind"] = "solution"
        elif "/templates/" in agent["_file"]:
            agent["_catalog_kind"] = "template"
        elif agent.get("_stack"):
            agent["_catalog_kind"] = "component"
        else:
            agent["_catalog_kind"] = "agent"

        readiness = []
        if agent.get("_demo", {}).get("case_count"):
            readiness.extend(["Demo proven", "Conversation tested"])
        if agent.get("requires_env"):
            readiness.append("Connector ready")
        if agent.get("_synthetic_data"):
            readiness.append("Synthetic data")
        if agent.get("_demo", {}).get("case_count") and agent.get("quality_tier") == "verified":
            readiness.append("Production pattern")
        agent["_readiness"] = readiness

    registry = {
        "schema": "rapp-registry/1.0",
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_agents": len(agents),
            "publishers": len(publishers),
            "categories": len(categories),
            "total_stacks": len(stack_rows),
            "total_multi_agent_stacks": sum(
                s["stack_type"] == "multi_agent" for s in stack_rows
            ),
            "total_solution_containers": sum(
                s["stack_type"] == "solution_container" for s in stack_rows
            ),
            "total_verticals": len({s["vertical"] for s in stack_rows}),
            "advertised_solutions": sum(bool(a.get("_solution")) for a in agents),
            "demo_proven_agents": sum(
                bool(a.get("_demo", {}).get("case_count")) for a in agents
            ),
            "source_verified_solutions": sum(
                bool(a.get("_solution", {}).get("source_verified")) for a in agents
            ),
            "curated_copy_solutions": sum(
                bool(a.get("_solution", {}).get("curated_copy")) for a in agents
            ),
            "solution_onepagers": sum(
                bool(a.get("_solution", {}).get("has_onepager")) for a in agents
            ),
            "solution_demo_videos": sum(
                bool(a.get("_solution", {}).get("has_demo_video")) for a in agents
            ),
            "total_lines": sum(a["_lines"] for a in agents),
            "total_kb": round(sum(a["_size_kb"] for a in agents), 1),
            "total_first_party": len(first_party),
            "first_party_available": sum(
                not a.get("lifecycle") for a in first_party
            ),
            "first_party_preview": sum(
                a.get("lifecycle") == "Preview" for a in first_party
            ),
            "first_party_documented": sum(
                a["_documented"] for a in first_party
            ),
            "first_party_products": sorted({a["product"] for a in first_party}),
            "publisher_list": sorted(publishers),
            "category_list": sorted(categories),
            "tier_counts": dict(sorted(tiers.items(), key=lambda kv: -kv[1])),
        },
        "stacks": stack_rows,
        "agents": agents,
        "first_party": first_party
    }

    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)

    print(f"[OK] Registry built: {len(agents)} agents from {len(publishers)} publishers")
    print(f"  Categories: {', '.join(sorted(categories))}")
    print(f"  Publishers: {', '.join(sorted(publishers))}")
    if first_party:
        preview = sum(a.get("lifecycle") == "Preview" for a in first_party)
        print(
            f"  First-party agents: {len(first_party)} "
            f"({preview} explicitly documented Preview)"
        )

    if errors:
        print(f"\n[WARN] {len(errors)} validation errors:")
        for err in errors:
            print(f"  - {err}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(build_registry())
