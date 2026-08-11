#!/usr/bin/env python3
"""Validate per-solution L2 architecture drafts and publish one catalog."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry.json"
DOMAIN_LIMITS = {
    "knowledge": (2, 5),
    "intelligence_processing": (3, 6),
    "clients_user_interface": (2, 5),
    "management_reporting": (2, 5),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "state" / "architecture_level2.json",
    )
    return parser.parse_args()


def expected_agents() -> dict[str, str]:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {
        agent["name"]: agent["_solution"]["advertised_name"]
        for agent in registry.get("agents", [])
        if (agent.get("_solution") or {}).get("architecture")
    }


def validate_items(
    label: str,
    items,
    minimum: int,
    maximum: int,
) -> list[dict]:
    if not isinstance(items, list) or not minimum <= len(items) <= maximum:
        raise ValueError(
            f"{label} must contain {minimum}-{maximum} items; got "
            f"{len(items) if isinstance(items, list) else type(items).__name__}"
        )
    result = []
    names = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != {"name", "detail"}:
            raise ValueError(f"{label}[{index}] must contain name and detail")
        name = str(item["name"]).strip()
        detail = str(item["detail"]).strip()
        if not name or len(name) > 60:
            raise ValueError(f"{label}[{index}].name must be 1-60 characters")
        if not detail or len(detail) > 140:
            raise ValueError(f"{label}[{index}].detail must be 1-140 characters")
        if "<" in name + detail or ">" in name + detail:
            raise ValueError(f"{label}[{index}] must not contain HTML")
        folded = name.casefold()
        if folded in names:
            raise ValueError(f"{label} repeats item name {name!r}")
        names.add(folded)
        result.append({"name": name, "detail": detail})
    return result


def validate_document(path: Path, expected: dict[str, str]) -> dict:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ValueError(f"{path}: invalid JSON: {error}") from error
    required = {
        "schema",
        "slug",
        "agent",
        "display_name",
        "domains",
        "tools",
        "supporting_features",
    }
    if set(document) != required:
        raise ValueError(f"{path}: keys must be exactly {sorted(required)}")
    if document["schema"] != "aibast-architecture-l2/1.0":
        raise ValueError(f"{path}: unsupported schema")
    agent = str(document["agent"])
    if agent not in expected:
        raise ValueError(f"{path}: {agent!r} is not an architecture solution")
    if path.stem != document["slug"]:
        raise ValueError(f"{path}: filename must match slug")
    if document["display_name"] != expected[agent]:
        raise ValueError(
            f"{path}: display_name must be {expected[agent]!r}, "
            f"not {document['display_name']!r}"
        )
    domains = document["domains"]
    if not isinstance(domains, dict) or set(domains) != set(DOMAIN_LIMITS):
        raise ValueError(
            f"{path}: domains must be exactly {sorted(DOMAIN_LIMITS)}"
        )
    validated_domains = {
        name: validate_items(
            f"{path.name}.domains.{name}",
            domains[name],
            *limits,
        )
        for name, limits in DOMAIN_LIMITS.items()
    }
    return {
        "schema": document["schema"],
        "slug": document["slug"],
        "agent": agent,
        "display_name": document["display_name"],
        "domains": validated_domains,
        "tools": validate_items(f"{path.name}.tools", document["tools"], 3, 8),
        "supporting_features": validate_items(
            f"{path.name}.supporting_features",
            document["supporting_features"],
            4,
            7,
        ),
    }


def main() -> None:
    args = parse_args()
    expected = expected_agents()
    files = sorted(args.input.glob("*.json"))
    documents = [validate_document(path, expected) for path in files]
    by_agent = {document["agent"]: document for document in documents}
    if len(by_agent) != len(documents):
        raise ValueError("duplicate agent documents were supplied")
    missing = sorted(set(expected) - set(by_agent))
    extra = sorted(set(by_agent) - set(expected))
    if missing or extra:
        raise ValueError(f"coverage mismatch: missing={missing}, extra={extra}")

    fingerprints = {
        agent: tuple(
            item["name"]
            for domain in document["domains"].values()
            for item in domain
        )
        for agent, document in by_agent.items()
    }
    repeated = {}
    for agent, fingerprint in fingerprints.items():
        repeated.setdefault(fingerprint, []).append(agent)
    duplicates = [agents for agents in repeated.values() if len(agents) > 1]
    if duplicates:
        raise ValueError(f"solution-specific domain content is duplicated: {duplicates}")

    output = {
        "schema": "aibast-architecture-l2-catalog/1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(by_agent),
        "solutions": dict(sorted(by_agent.items())),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(by_agent)} Level 2 architectures to {args.out}")


if __name__ == "__main__":
    main()
