"""The library's static API (rapp-static-api/1.1): one input, one idempotent build, append-only versions."""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"
SHARED = ROOT / "solutions" / "_shared"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_rebuild_is_byte_identical():
    result = subprocess.run(
        [sys.executable, "tools/build_library_api.py", "--check"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_registry_names_every_document_and_its_frozen_version():
    registry = read_json(API / "registry.json")
    assert registry["schema"].startswith("aibast-library-api/")
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", registry["generated"])
    assert registry["pages"].endswith("/") and registry["raw"].endswith("/")
    for entry in registry["entries"]:
        doc = ROOT / entry["path"]
        assert sha256(doc) == entry["sha256"], entry["path"]
        version = ROOT / entry["version"]
        assert version.read_bytes() == doc.read_bytes(), entry["version"]
        assert version.stem == entry["sha8"] == entry["sha256"][:12]


def test_every_schema_is_named_and_versioned():
    for path in (API / "v1").rglob("*.json"):
        if path.name == "badge.json":  # shields.io endpoint shape: schemaVersion
            assert read_json(path)["schemaVersion"] == 1
            continue
        assert re.fullmatch(r"[a-z0-9-]+/\d+\.\d+", read_json(path)["schema"]), path


def test_solution_documents_point_at_real_files_with_matching_hashes():
    checked = 0
    for path in (API / "v1" / "solutions").glob("*.json"):
        get = read_json(path)["get"]
        for key in ("package", "deploy_agent", "instructions"):
            item = get.get(key)
            if not item:
                continue
            local = ROOT / item["path"]
            assert local.is_file(), (path.name, key)
            assert sha256(local) == item["sha256"], (path.name, key)
            checked += 1
        assert "{pages}" in get["prompt"] and get["prompt"].endswith("and do it.")
    assert checked >= 3 * 72


def test_scenarios_keep_the_preview_answer_shape_and_sample_data_notice():
    for path in (API / "v1" / "scenarios").glob("*.json"):
        doc = read_json(path)
        assert doc["answer"]["schema"] == "rapp-preview-answer/1"
        assert doc["answer"]["question"] == doc["question"]
        assert "not connected to your organization's data" in doc["notice"]


def test_llms_txt_is_the_front_door():
    text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "api/v1/index.json" in text
    assert "https://microsoft.github.io/aibast-agents-library/" in text


def test_the_demo_reads_only_the_static_api():
    for name in ("m365-copilot-demo.html", "aibast-demo-sdk.js", "surfaces/surface.js"):
        text = (SHARED / name).read_text(encoding="utf-8")
        assert "no-store" not in text, name
        assert "api.github.com" not in text, name
        assert not re.search(r"fetch\(\s*['\"`]https?://", text), name


def test_surfaces_carry_no_account_or_tenant_details():
    guid = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
    for page in (SHARED / "surfaces").glob("*/index.html"):
        text = page.read_text(encoding="utf-8")
        assert not guid.search(text), page
        assert "copilot.cloud.microsoft/chat/conversation" not in text, page
        assert "data:image/jpeg" not in text, page  # no profile photos
        assert "<script" not in text.replace('<script src="../surface.js" defer></script>', ""), page


def test_narration_clips_are_content_addressed_24khz_mono_wav():
    import wave
    found = 0
    for path in (API / "v1" / "scenarios").glob("*.json"):
        block = read_json(path)["narration"]
        if not block:
            continue
        assert block["mode"] == "synthesized" and block["captions"] is True
        for seg in block["segments"]:
            media = seg["media"]
            local = ROOT / media["url"]
            assert sha256(local) == media["contentHash"] == local.stem
            assert local.stat().st_size == media["sizeBytes"]
            with wave.open(str(local)) as w:
                assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
                assert abs(round(w.getnframes() * 1000 / 24000) - media["durationMs"]) <= 1
            assert seg["captions"]["segments"][-1]["endMs"] == media["durationMs"]
            found += 1
    assert found == 8
