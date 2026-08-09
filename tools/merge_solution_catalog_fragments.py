#!/usr/bin/env python3
"""Merge disjoint hand-authored solution catalog fragments."""

import argparse
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "solutions" / "catalog.json"
REQUIRED_ENTRY_FIELDS = {
    "display_name",
    "sales_headline",
    "card_pitch",
    "why_try",
    "customer_challenge",
    "microsoft_ai_story",
    "business_value",
    "search_terms",
    "journey_stage",
    "blueprint_role",
    "sample_prompts",
    "architecture",
}
REQUIRED_ARCHITECTURE_FIELDS = {
    "business_flow",
    "capabilities",
    "easy_mode",
    "local_install_prompt",
    "copilot_studio_prompt",
    "required_connections",
    "manual_commands",
    "acceptance_checks",
    "hard_mode",
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def entries(document):
    if "solutions" in document:
        return document["solutions"]
    return document


def validate_entry(name, entry):
    missing = REQUIRED_ENTRY_FIELDS - set(entry)
    if missing:
        raise ValueError(f"{name}: missing catalog fields {sorted(missing)}")
    architecture = entry["architecture"]
    missing_architecture = REQUIRED_ARCHITECTURE_FIELDS - set(architecture)
    if missing_architecture:
        raise ValueError(
            f"{name}: missing architecture fields {sorted(missing_architecture)}"
        )
    if len(entry["business_value"]) != 3:
        raise ValueError(f"{name}: business_value must contain exactly 3 items")
    if not entry["sample_prompts"]:
        raise ValueError(f"{name}: sample_prompts must not be empty")
    for prompt in entry["sample_prompts"]:
        if not {"label", "prompt", "demo_url"} <= set(prompt):
            raise ValueError(f"{name}: incomplete sample prompt")
    if "Do not ask me to open a terminal" not in architecture["local_install_prompt"]:
        raise ValueError(f"{name}: local install prompt is not no-terminal")
    if "Stop before publish" not in architecture["copilot_studio_prompt"]:
        raise ValueError(f"{name}: Copilot Studio prompt lacks publish gate")


def normalize_entry(entry):
    normalized = copy.deepcopy(entry)
    architecture = normalized.get("architecture", {})
    local_prompt = architecture.get("local_install_prompt", "")
    if "Do not ask me to open a terminal" not in local_prompt:
        architecture["local_install_prompt"] = (
            local_prompt.rstrip()
            + " Do not ask me to open a terminal, run a command, clone a "
            "repository, or install the runtime myself."
        )
    studio_prompt = architecture.get("copilot_studio_prompt", "")
    if "Microsoft Copilot Studio plugin" not in studio_prompt:
        studio_prompt = (
            "Use the Microsoft Copilot Studio plugin. " + studio_prompt.lstrip()
        )
    if "Stop before publish" not in studio_prompt:
        studio_prompt = studio_prompt.rstrip() + " Stop before publish."
    architecture["copilot_studio_prompt"] = studio_prompt
    return normalized


def merge(base, fragments):
    merged = dict(base)
    for path, fragment in fragments:
        for name, value in fragment.items():
            value = normalize_entry(value)
            validate_entry(name, value)
            if name in merged and merged[name] != value:
                raise ValueError(f"{path}: conflicting catalog entry {name}")
            merged[name] = value
    return merged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fragments", nargs="+", type=Path)
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    args = parser.parse_args()

    catalog_path = args.catalog.resolve()
    document = read(catalog_path)
    fragments = [
        (path, entries(read(path.resolve())))
        for path in args.fragments
    ]
    normalized_base = {
        name: normalize_entry(value)
        for name, value in document.get("solutions", {}).items()
    }
    document["solutions"] = merge(normalized_base, fragments)
    catalog_path.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[OK] Catalog now contains {len(document['solutions'])} curated solutions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
