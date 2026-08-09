#!/usr/bin/env python3
"""Run a locked case corpus against a published Copilot Studio CLI agent."""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHAT = (
    Path.home()
    / ".copilot"
    / "installed-plugins"
    / "_direct"
    / "microsoft--copilot-studio-plugin"
    / "scripts"
    / "chat-with-agent.bundle.js"
)


def run_case(chat_script, agent_dir, client_id, case):
    command = [
        "node",
        str(chat_script),
        "--agent-dir",
        str(agent_dir),
        "--client-id",
        client_id,
        case["prompt"],
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"{case['id']} runtime failed ({result.returncode}): "
            f"{result.stderr[-1200:]}"
        )
    payload = json.loads(result.stdout)
    if payload.get("status") != "ok":
        raise RuntimeError(f"{case['id']} returned {payload}")

    text = payload.get("text", "")
    failures = []
    for value in case.get("must_include", []):
        if value.lower() not in text.lower():
            failures.append(f"missing {value!r}")
    for value in case.get("must_not_include", []):
        if value.lower() in text.lower():
            failures.append(f"contains stall phrase {value!r}")
    if len(text.split()) < case.get("min_words", 0):
        failures.append(
            f"{len(text.split())} words < {case['min_words']}"
        )
    if failures:
        raise AssertionError(f"{case['id']}: {'; '.join(failures)}")

    return {
        "case_id": case["id"],
        "persona": case.get("persona"),
        "onepager_promise": case.get("onepager_bullet"),
        "prompt": case["prompt"],
        "assistant_response": text,
        "conversation_id": payload.get("conversation_id"),
        "expected_agent": case.get("expects_agent"),
        "must_include": case.get("must_include", []),
        "runtime_steps": payload.get("steps", []),
        "passed": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case_file", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--agent-dir", type=Path, required=True)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--chat-script", type=Path, default=DEFAULT_CHAT)
    args = parser.parse_args()

    case_doc = json.loads(args.case_file.read_text(encoding="utf-8"))
    transcripts = [
        run_case(
            args.chat_script.expanduser().resolve(),
            args.agent_dir.expanduser().resolve(),
            args.client_id,
            case,
        )
        for case in case_doc["cases"]
    ]
    artifact = {
        "schema": "aibast-copilot-studio-transcripts/1.0",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "solution": case_doc["agent"],
        "onepager": case_doc.get("onepager"),
        "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
        "agent_schema_name": "aibast_BuildingPermitPilot",
        "strict_case_parity": True,
        "transcripts": transcripts,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"[OK] Captured {len(transcripts)} Copilot Studio transcripts "
        f"for {case_doc['agent']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
