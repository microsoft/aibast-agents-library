"""The capture tool must not silently move a caller's Brainstem endpoint."""
import importlib.util
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "capture_demo_transcripts_under_test", ROOT / "tools" / "capture_demo_transcripts.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_main(module, argv):
    seen = {}

    def fake_capture(*_args, **_kwargs):
        seen["health"], seen["chat"] = module.HEALTH, module.CHAT
        return {}

    with mock.patch.object(module, "capture", fake_capture), \
         mock.patch.object(sys, "argv", ["capture"] + argv), \
         mock.patch.object(module, "write_artifact", lambda *a, **k: None, create=True):
        try:
            module.main()
        except Exception:
            pass
    return seen


def test_caller_patched_endpoint_is_kept_without_the_flag():
    module = _load()
    module.HEALTH = "http://localhost:7179/health"
    module.CHAT = "http://localhost:7179/chat"
    seen = _run_main(module, ["cases.json", "out.json"])
    assert seen == {"health": "http://localhost:7179/health", "chat": "http://localhost:7179/chat"}


def test_explicit_flag_moves_the_endpoint():
    module = _load()
    seen = _run_main(module, ["cases.json", "out.json", "--base-url", "http://localhost:7187/"])
    assert seen == {"health": "http://localhost:7187/health", "chat": "http://localhost:7187/chat"}


def test_default_is_the_main_brainstem():
    module = _load()
    seen = _run_main(module, ["cases.json", "out.json"])
    assert seen["chat"] == "http://localhost:7071/chat"
