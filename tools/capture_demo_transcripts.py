#!/usr/bin/env python3
"""
Capture canonical demo transcripts from one solution loaded in isolation.

All discoverable *_agent.py files except basic_agent.py are moved aside while
the selected solution runs. The original Brainstem agent set is restored in a
finally block even when a request or assertion fails.
"""

import argparse
import fcntl
import hashlib
import json
import shutil
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
LIBRARY = REPO / "agents" / "@aibast-agents-library"
DEFAULT_BRAINSTEM_AGENTS = (
    Path.home() / ".brainstem" / "src" / "rapp_brainstem" / "agents"
)
HEALTH = "http://localhost:7071/health"
CHAT = "http://localhost:7071/chat"
CAPTURE_LOCK = Path.home() / ".brainstem" / ".aibast-capture.lock"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def request_json(url, body=None, timeout=240):
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_agent(stem):
    matches = list(LIBRARY.rglob(f"{stem}.py"))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {stem}.py, found {len(matches)}")
    return matches[0]


def assert_case(case, response, logs):
    failures = []
    expected = case.get("expects_agent")
    if expected and expected.lower() not in logs.lower():
        failures.append(f"expected agent {expected} did not fire")
    for value in case.get("must_include", []):
        if value.lower() not in logs.lower():
            failures.append(f"agent output missing {value!r}")
    for value in case.get("must_not_include", []):
        if value.lower() in response.lower():
            failures.append(f"assistant response contains stall phrase {value!r}")
    if len(response.split()) < case.get("min_words", 0):
        failures.append(
            f"response has {len(response.split())} words; "
            f"expected at least {case['min_words']}"
        )
    if failures:
        raise AssertionError("; ".join(failures))


def _capture_unlocked(case_path, output_path, agents_dir):
    case_doc = read_json(case_path)
    health_before = request_json(HEALTH, timeout=10)
    if health_before.get("status") != "ok":
        raise RuntimeError("Brainstem health is not ok")

    selected_sources = [find_agent(stem) for stem in case_doc["agent_files"]]
    agents_dir.mkdir(parents=True, exist_ok=True)
    original_files = [
        path for path in agents_dir.glob("*_agent.py")
        if path.name != "basic_agent.py"
    ]

    with tempfile.TemporaryDirectory(prefix="aibast-agent-isolation-") as temp:
        backup = Path(temp)
        installed = []
        try:
            for path in original_files:
                shutil.move(str(path), backup / path.name)
            for source in selected_sources:
                target = agents_dir / source.name
                shutil.copy2(source, target)
                installed.append(target)

            time.sleep(1)
            discoverable = {
                path.name for path in agents_dir.glob("*_agent.py")
                if path.name != "basic_agent.py"
            }
            expected_files = {source.name for source in selected_sources}
            if discoverable != expected_files:
                raise AssertionError(
                    "strict isolation failed on disk; "
                    f"expected {sorted(expected_files)}, found {sorted(discoverable)}"
                )

            isolated_health = request_json(HEALTH, timeout=10)
            expected_tools = {
                case["expects_agent"] for case in case_doc["cases"]
                if case.get("expects_agent")
            }

            transcripts = []
            for index, case in enumerate(case_doc["cases"]):
                result = request_json(
                    CHAT,
                    {
                        "user_input": case["prompt"],
                        "conversation_history": [],
                        "session_id": f"canonical-{case['id'].lower()}-{index}",
                    },
                )
                response = result.get("response", "")
                logs = result.get("agent_logs", "") or ""
                assert_case(case, response, logs)
                transcripts.append({
                    "case_id": case["id"],
                    "persona": case.get("persona"),
                    "onepager_promise": case.get("onepager_bullet"),
                    "prompt": case["prompt"],
                    "assistant_response": response,
                    "agent_logs": logs,
                    "expected_agent": case.get("expects_agent"),
                    "must_include": case.get("must_include", []),
                    "model": result.get("model"),
                    "requested_model": result.get("requested_model"),
                    "passed": True,
                })

            health_after = request_json(HEALTH, timeout=10)
            loaded = set(health_after.get("agents", []))
            missing = expected_tools - loaded
            if missing:
                raise AssertionError(
                    f"post-chat health missing tools: {sorted(missing)}"
                )

            artifact = {
                "schema": "aibast-canonical-transcripts/1.0",
                "captured_at": datetime.now(timezone.utc).isoformat(),
                "solution": case_doc["agent"],
                "onepager": case_doc.get("onepager"),
                "brainstem_version": health_after.get("version"),
                "loaded_tools_after_capture": sorted(loaded),
                "agent_sources": [
                    {
                        "path": source.relative_to(REPO).as_posix(),
                        "sha256": sha256(source),
                    }
                    for source in selected_sources
                ],
                "case_file": case_path.relative_to(REPO).as_posix(),
                "case_file_sha256": sha256(case_path),
                "strict_isolation": True,
                "transcripts": transcripts,
            }
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(artifact, indent=2) + "\n",
                encoding="utf-8",
            )
            return artifact
        finally:
            for path in installed:
                path.unlink(missing_ok=True)
            for path in backup.glob("*_agent.py"):
                shutil.move(str(path), agents_dir / path.name)
            time.sleep(1)


def capture(case_path, output_path, agents_dir):
    """Run one isolation capture while holding the cross-process swap lock."""
    CAPTURE_LOCK.parent.mkdir(parents=True, exist_ok=True)
    with CAPTURE_LOCK.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            return _capture_unlocked(case_path, output_path, agents_dir)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case_file", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=DEFAULT_BRAINSTEM_AGENTS,
    )
    args = parser.parse_args()

    artifact = capture(
        args.case_file.resolve(),
        args.output.resolve(),
        args.agents_dir.expanduser().resolve(),
    )
    print(
        f"[OK] Captured {len(artifact['transcripts'])} isolated transcripts "
        f"for {artifact['solution']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
