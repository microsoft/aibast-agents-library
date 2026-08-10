#!/usr/bin/env python3
"""Refresh Copilot Studio solution export metadata from local artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "solutions" / "catalog.json"
REGISTRY_PATH = ROOT / "registry.json"
STATE_PATH = ROOT / "state" / "copilot_studio_solution_exports.json"
ENVIRONMENT = {
    "name": "kodyv8",
    "url": "https://org7dfbd855.crm.dynamics.com/",
}
IMPORT_CAVEATS = [
    "Import as an unmanaged solution for manual review.",
    "Map connection references and environment variables before enabling integrations.",
    "The exported agent remains unpublished unless the target administrator explicitly publishes it.",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        f"{json.dumps(payload, indent=2, ensure_ascii=True)}\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exported_at(
    zip_path: Path,
    current_metadata: dict,
    current_state: dict,
    digest: str,
) -> str:
    for current in (current_metadata, current_state):
        if current.get("sha256") == digest and current.get("exported_at"):
            return str(current["exported_at"])
    return datetime.fromtimestamp(
        zip_path.stat().st_mtime,
        tz=timezone.utc,
    ).isoformat()


def record_for(slug: str, current_state: dict) -> dict:
    solution_root = ROOT / "solutions" / slug
    exports_root = solution_root / "exports"
    deployment = read_json(solution_root / "deployment.json")
    copilot = deployment.get("copilot_studio", {})
    export_agent = (
        copilot.get("export_agent")
        or copilot.get("validated_pilot")
        or {}
    )
    solution_unique_name = (
        export_agent.get("solution_unique_name")
        or export_agent.get("schema_name")
    )
    bot_schema_name = export_agent.get("schema_name")
    display_name = export_agent.get("display_name")
    published = export_agent.get("published")

    zip_relative = f"solutions/{slug}/exports/{slug}-copilot-studio-solution.zip"
    settings_relative = f"solutions/{slug}/exports/{slug}-deployment-settings.json"
    metadata_relative = f"solutions/{slug}/exports/{slug}-solution-export.json"
    zip_path = ROOT / zip_relative
    settings_path = ROOT / settings_relative
    metadata_path = ROOT / metadata_relative

    current_metadata = read_json(metadata_path) if metadata_path.exists() else {}
    settings_error = None
    if settings_path.exists():
        try:
            read_json(settings_path)
        except (OSError, json.JSONDecodeError) as error:
            settings_error = str(error)
    else:
        settings_error = "Deployment settings file is missing."

    if zip_path.exists():
        digest = sha256(zip_path)
        record = {
            "slug": slug,
            "solution_unique_name": solution_unique_name,
            "status": "exported",
            "zip": zip_relative,
            "deployment_settings": settings_relative,
            "metadata": metadata_relative,
            "published": published,
            "managed": False,
            "error": (
                None
                if published is False
                else "Export agent is not proven unpublished."
            ),
            "sha256": digest,
            "bytes": zip_path.stat().st_size,
            "agent_display_name": display_name,
            "agent_id": None,
            "bot_schema_name": bot_schema_name,
            "source_environment": ENVIRONMENT["name"],
            "exported_at": exported_at(
                zip_path,
                current_metadata,
                current_state,
                digest,
            ),
            "import_caveats": IMPORT_CAVEATS,
            "settings_error": settings_error,
        }
    else:
        record = {
            "slug": slug,
            "solution_unique_name": solution_unique_name,
            "status": "missing",
            "zip": zip_relative,
            "deployment_settings": settings_relative,
            "metadata": metadata_relative,
            "published": published,
            "managed": False,
            "error": "Copilot Studio solution ZIP is missing.",
            "sha256": None,
            "bytes": 0,
            "agent_display_name": display_name,
            "agent_id": None,
            "bot_schema_name": bot_schema_name,
            "source_environment": ENVIRONMENT["name"],
            "exported_at": None,
            "import_caveats": IMPORT_CAVEATS,
            "settings_error": settings_error,
        }
    write_json(metadata_path, record)
    return record


def main() -> int:
    catalog = read_json(CATALOG_PATH)
    registry = read_json(REGISTRY_PATH)
    current_inventory = read_json(STATE_PATH) if STATE_PATH.exists() else {}
    current_by_slug = {
        row["slug"]: row
        for row in current_inventory.get("solutions", [])
        if row.get("slug")
    }
    registry_by_name = {
        row.get("name"): row
        for row in registry.get("agents", [])
        if row.get("_solution")
    }
    slugs = sorted({
        registry_by_name[name]["_solution"]["package"]["slug"]
        for name in catalog.get("solutions", {})
    })
    records = [
        record_for(slug, current_by_slug.get(slug, {}))
        for slug in slugs
    ]
    exported = sum(row["status"] == "exported" for row in records)
    with_settings = sum(
        row["status"] == "exported" and row["settings_error"] is None
        for row in records
    )
    unpublished = sum(
        row["status"] == "exported"
        and row["published"] is False
        and row["error"] is None
        for row in records
    )
    timestamps = [
        datetime.fromisoformat(row["exported_at"])
        for row in records
        if row.get("exported_at")
    ]
    inventory = {
        "schema": "aibast-copilot-studio-solution-exports/1.0",
        "generated_at": max(timestamps).isoformat() if timestamps else None,
        "environment": ENVIRONMENT,
        "managed": False,
        "published": False,
        "summary": {
            "total": len(records),
            "exported": exported,
            "missing": len(records) - exported,
            "with_deployment_settings": with_settings,
            "unpublished": unpublished,
        },
        "solutions": records,
    }
    write_json(STATE_PATH, inventory)
    print(
        json.dumps(
            {
                "total": len(records),
                "exported": exported,
                "missing": len(records) - exported,
                "with_deployment_settings": with_settings,
                "unpublished": unpublished,
            },
            separators=(",", ":"),
        )
    )
    return (
        0
        if (
            exported == len(records)
            and with_settings == len(records)
            and unpublished == len(records)
        )
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
