"""The RAPP learning endpoints under api/v1/rapp/ match their sources."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api" / "v1" / "rapp"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_index_lists_everything():
    index = load(API / "index.json")
    assert index["schema"] == "aibast-rapp-index/1.0"
    assert [s["step"] for s in index["steps"]] == list(range(1, 15))
    for entry in index["steps"] + index["concepts"]:
        assert (ROOT / entry["doc"]).is_file(), entry["doc"]
    assert (ROOT / index["glossary"]).is_file() and (ROOT / index["tools"]).is_file()


def test_steps_have_do_get_and_chain():
    for n in range(1, 15):
        doc = load(API / "steps" / f"{n}.json")
        assert doc["schema"] == "aibast-rapp-step/1.0" and doc["step"] == n
        assert doc["title"].startswith(f"Step {n}:")
        assert doc["do"] and doc["get"] and doc["explain"]["markdown"] and doc["done_when"]
        assert doc["prev"] == (f"api/v1/rapp/steps/{n - 1}.json" if n > 1 else None)
        assert doc["next"] == (f"api/v1/rapp/steps/{n + 1}.json" if n < 14 else None)


def test_every_source_sha_matches():
    docs = list(API.rglob("*.json"))
    assert len(docs) > 40
    for path in docs:
        doc = load(path)
        if path.name == "index.json":
            continue
        assert doc["sources"], path
        for src in doc["sources"]:
            data = (ROOT / src["path"]).read_bytes()
            assert hashlib.sha256(data).hexdigest() == src["sha256"], (path, src["path"])


def test_glossary_and_tools():
    glossary = load(API / "glossary.json")
    assert glossary["count"] == len(glossary["terms"]) > 20
    tools = load(API / "tools.json")
    assert "not an officially supported Microsoft product" in tools["disclaimer"]
    assert tools["count"] == len(tools["tools"]) > 0


def test_index_and_llms_point_at_rapp():
    root = load(ROOT / "api" / "v1" / "index.json")
    assert root["endpoints"]["rapp"] == "api/v1/rapp/index.json"
    assert "Learn RAPP step by step" in (ROOT / "llms.txt").read_text(encoding="utf-8")
    names = {e["path"] for e in load(ROOT / "api" / "registry.json")["entries"]}
    assert "api/v1/rapp/steps/3.json" in names


def test_rebuild_is_byte_identical():
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "build_library_api.py"), "--check"],
                         cwd=ROOT, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
