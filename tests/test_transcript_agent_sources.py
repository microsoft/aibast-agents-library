"""Every recorded demo transcript names the agent source it was recorded against by sha256.

The M365 demo page prints that hash under 'Exact Brainstem transcript', so a changed agent must be
re-recorded (tools/capture_demo_transcripts.py) before it ships; otherwise the page cites an agent
that no longer exists.
"""

import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
TRANSCRIPTS = sorted((ROOT / "solutions").glob("*/evals/transcripts.json"))


def test_transcripts_were_found():
    assert len(TRANSCRIPTS) >= 70


@pytest.mark.parametrize("path", TRANSCRIPTS, ids=lambda p: p.parent.parent.name)
def test_recorded_agent_sha_matches_the_shipped_source(path):
    artifact = json.loads(path.read_text(encoding="utf-8"))
    sources = artifact.get("agent_sources") or []
    assert sources, f"{path} names no agent source"
    for source in sources:
        agent = ROOT / source["path"]
        assert agent.is_file(), f"{path} names a missing agent {source['path']}"
        digest = hashlib.sha256(agent.read_bytes()).hexdigest()
        assert digest == source["sha256"], (
            f"{path.relative_to(ROOT)} was recorded against {source['sha256'][:12]} but "
            f"{source['path']} is now {digest[:12]}; re-record with tools/capture_demo_transcripts.py"
        )
