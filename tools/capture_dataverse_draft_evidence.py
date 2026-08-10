#!/usr/bin/env python3
"""Capture live Dataverse evidence that advertised pilot agents are unpublished."""

from __future__ import annotations

import hashlib
import json
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT_NAME = "kodyv8"
ENVIRONMENT_ID = "ee67a404-325c-e726-a18a-886fe708ca0b"
ENVIRONMENT_URL = "https://org7dfbd855.crm.dynamics.com"
API_VERSION = "v9.2"
SELECT_FIELDS = [
    "name",
    "botid",
    "componentstate",
    "statecode",
    "statuscode",
    "modifiedon",
    "publishedon",
    "synchronizationstatus",
    "versionnumber",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        f"{json.dumps(payload, indent=2, ensure_ascii=True)}\n",
        encoding="utf-8",
    )


def access_token() -> str:
    result = subprocess.run(
        [
            "az",
            "account",
            "get-access-token",
            "--resource",
            ENVIRONMENT_URL,
            "--query",
            "accessToken",
            "-o",
            "tsv",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    token = result.stdout.strip()
    if not token:
        raise RuntimeError("Azure CLI returned an empty Dataverse access token.")
    return token


def advertised_slugs() -> list[str]:
    catalog = read_json(ROOT / "solutions" / "catalog.json")["solutions"]
    registry = read_json(ROOT / "registry.json")["agents"]
    registry_by_name = {
        row["name"]: row
        for row in registry
        if row.get("_solution")
    }
    return sorted({
        registry_by_name[name]["_solution"]["package"]["slug"]
        for name in catalog
    })


def fetch_bot(token: str, bot_id: str) -> dict:
    query = urllib.parse.urlencode(
        {"$select": ",".join(SELECT_FIELDS)},
        safe="$,",
    )
    url = (
        f"{ENVIRONMENT_URL}/api/data/{API_VERSION}/bots({bot_id})?{query}"
    )
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    token = access_token()
    captured_at = datetime.now(timezone.utc).isoformat()
    failures = []
    captured = 0
    for slug in advertised_slugs():
        package = ROOT / "solutions" / slug
        deployment = read_json(package / "deployment.json")
        copilot = deployment.get("copilot_studio", {})
        export_agent = (
            copilot.get("export_agent")
            or copilot.get("validated_pilot")
            or {}
        )
        bot_id = export_agent.get("bot_id")
        display_name = export_agent.get("display_name")
        schema_name = export_agent.get("schema_name")
        if not all(
            isinstance(value, str) and value
            for value in (bot_id, display_name, schema_name)
        ):
            failures.append(f"{slug}: validated pilot identity is incomplete")
            continue

        response = fetch_bot(token, bot_id)
        synchronization = response.get("synchronizationstatus")
        try:
            synchronization = (
                json.loads(synchronization)
                if isinstance(synchronization, str)
                else synchronization
            )
        except json.JSONDecodeError:
            synchronization = None
        record = {
            field: response.get(field)
            for field in SELECT_FIELDS
            if field != "synchronizationstatus"
        }
        record["synchronizationstatus"] = synchronization
        record["odata_etag"] = response.get("@odata.etag")
        canonical_record = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        last_publish = (
            synchronization.get("lastFinishedPublishOperation")
            if isinstance(synchronization, dict)
            else None
        )
        assertions = {
            "bot_id_matches": record["botid"] == bot_id,
            "display_name_matches": record["name"] == display_name,
            "publishedon_is_null": record["publishedon"] is None,
            "last_finished_publish_operation_is_null": last_publish is None,
        }
        evidence = {
            "schema": "aibast-dataverse-draft-evidence/1.0",
            "captured_at": captured_at,
            "source": {
                "kind": "Dataverse Web API",
                "environment_name": ENVIRONMENT_NAME,
                "environment_id": ENVIRONMENT_ID,
                "environment_url": ENVIRONMENT_URL,
                "api_version": API_VERSION,
                "select": SELECT_FIELDS,
            },
            "identity": {
                "slug": slug,
                "solution": deployment.get("name"),
                "display_name": display_name,
                "schema_name": schema_name,
                "bot_id": bot_id,
            },
            "record": record,
            "record_sha256": hashlib.sha256(canonical_record).hexdigest(),
            "assertions": assertions,
        }
        write_json(
            package / "evals" / "dataverse-draft-evidence.json",
            evidence,
        )
        captured += 1
        if not all(assertions.values()):
            failures.append(
                f"{slug}: live agent is not proven unpublished ({assertions})"
            )

    print(
        json.dumps(
            {
                "total": len(advertised_slugs()),
                "captured": captured,
                "failed": len(failures),
                "failures": failures,
            },
            separators=(",", ":"),
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
