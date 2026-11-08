"""Public Microsoft content in api/v1/public/ matches its pinned, provenanced snapshot."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import library_api_public as public  # noqa: E402


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_every_source_is_public_microsoft_with_provenance():
    for s in public.load_sources()["sources"]:
        for url in [s["page"], s["file"], *s.get("documented_at", [])]:
            assert url.startswith(("https://microsoft.github.io/", "https://learn.microsoft.com/")), url
        assert len(s["snapshot"]["file_sha256"]) == 64 and s["snapshot"]["data"]
        doc = load(ROOT / "api" / "v1" / "public" / f"{s['id']}.json")
        assert doc["schema"] == "aibast-public/1.0"
        assert doc["data"] == s["snapshot"]["data"]
        assert doc["provenance"]["file_sha256"] == s["snapshot"]["file_sha256"]
        assert doc["disclaimer"]


def test_credit_rates_values():
    rates = load(ROOT / "api" / "v1" / "public" / "copilot-credit-rates.json")["data"]
    assert rates["toolInvocation"] == 5 and rates["agentFlowPerAction"] == 0.13
    assert rates["tenantGraphGrounding"] == 12 and rates["otherKnowledge"] == 2


def test_js_object_extractor():
    text = "const CREDIT_RATES = {\n    a: 1,  // note\n    /* x */ b: 0.5,\n};\n"
    assert public.js_object(text, "CREDIT_RATES") == {"a": 1, "b": 0.5}


def test_index_llms_and_registry():
    idx = load(ROOT / "api" / "v1" / "public" / "index.json")
    assert idx["sources"][0]["doc"] == "api/v1/public/copilot-credit-rates.json"
    assert load(ROOT / "api" / "v1" / "index.json")["endpoints"]["public"] == "api/v1/public/index.json"
    assert "api/v1/public/copilot-credit-rates.json" in (ROOT / "llms.txt").read_text(encoding="utf-8")
    names = {e["path"] for e in load(ROOT / "api" / "registry.json")["entries"]}
    assert {"api/v1/public/index.json", "api/v1/public/copilot-credit-rates.json"} <= names


def test_rebuild_is_byte_identical():
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "build_library_api.py"), "--check"],
                         cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
