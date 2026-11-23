"""The installer parity comparer: allowed differences pass, anything else fails."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import installer_parity as ip  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

GRAIL_RUN1 = """  RAPP Brainstem
Checking prerequisites...
  [OK] Python 3.12.10
Installing RAPP Brainstem...
  Cloning repository...
  [OK] Source code ready
  Creating virtual environment...
Collecting flask>=2.0.0
  [OK] RAPP Brainstem v0.6.16 installed!
  Your code: AAAA-1111
[brainstem] Agent loaded: ContextMemory
"""

OURS_RUN1 = """  RAPP Brainstem
Checking prerequisites...
  [OK] Python 3.12.10
Installing RAPP Brainstem...
  Downloading only the Brainstem runtime; solution ZIPs stay in the web library.
Cloning into 'C:\\Users\\someone\\.brainstem\\src-fresh-1'...
remote: Counting objects:  10% (265/2645)
  [OK] Source code ready
  [..] Creating Python virtual environment...
  [OK] RAPP Brainstem v0.6.17 installed!
  Your code: BBBB-2222
[brainstem] Agent loaded: ContextMemory
[brainstem] Agent loaded: LearnNew
"""


def _capture(tmp_path, name, run1, *, agents, version, tree, beside=()):
    d = tmp_path / name
    d.mkdir()
    for label in ("run1", "run2"):
        (d / f"{label}.log").write_text(run1, encoding="utf-8")
        (d / f"{label}.tree.txt").write_text("\n".join(tree) + "\n", encoding="utf-8")
        (d / f"{label}.meta.json").write_text(json.dumps({
            "state": "serving", "seconds": 1, "src_kib": 4000, "beside_runtime": list(beside),
            "health": {"status": "unauthenticated", "version": version, "agents": agents},
        }), encoding="utf-8")
    return d


BASE_TREE = ["src/rapp_brainstem/brainstem.py", "src/rapp_brainstem/agents/basic_agent.py",
             "src/rapp_brainstem/.env", "src/README.md"]
OUR_TREE = ["src/rapp_brainstem/brainstem.py", "src/rapp_brainstem/agents/basic_agent.py",
            "src/rapp_brainstem/agents/rar_rapp_learn_new_agent.py", "src/rapp_brainstem/tui.py",
            "src/rapp_brainstem/.copilot_pending"]


def _pair(tmp_path, **ours):
    grail = _capture(tmp_path, "grail", GRAIL_RUN1, agents=["ContextMemory"], version="0.6.16", tree=BASE_TREE)
    kwargs = dict(agents=["ContextMemory", "LearnNew"], version="0.6.17", tree=OUR_TREE)
    run1 = ours.pop("run1", OURS_RUN1)
    kwargs.update(ours)
    return grail, _capture(tmp_path, "ours", run1, **kwargs)


def test_allowed_differences_pass(tmp_path):
    result = ip.compare_dirs(*_pair(tmp_path))
    assert result["problems"] == []
    assert {"light-download", "progress-notes", "extra-agent", "mouse-terminal", "downstream-version"} <= set(result["allowed_used"])


def test_an_unlisted_step_fails(tmp_path):
    result = ip.compare_dirs(*_pair(tmp_path, run1=OURS_RUN1 + "  Sending usage statistics...\n"))
    assert any("only ours shows: Sending usage statistics" in p for p in result["problems"])


def test_a_step_the_grail_has_and_ours_dropped_fails(tmp_path):
    result = ip.compare_dirs(*_pair(tmp_path, run1=OURS_RUN1.replace("Checking prerequisites...\n", "")))
    assert any("only the Grail shows: Checking prerequisites" in p for p in result["problems"])


def test_files_beside_the_runtime_fail(tmp_path):
    result = ip.compare_dirs(*_pair(tmp_path, beside=["registry.json", ".DS_Store"]))
    assert any("beside the runtime folder" in p for p in result["problems"])


def test_an_unlisted_agent_or_runtime_file_fails(tmp_path):
    result = ip.compare_dirs(*_pair(tmp_path, agents=["ContextMemory", "LearnNew", "Surprise"],
                                    tree=OUR_TREE + ["src/rapp_brainstem/extra.py"]))
    assert any("not listed" in p for p in result["problems"])
    assert any("runtime file only in ours: extra.py" in p for p in result["problems"])


def test_a_missing_grail_agent_fails(tmp_path):
    result = ip.compare_dirs(*_pair(tmp_path, agents=["LearnNew"]))
    assert any("missing agents" in p for p in result["problems"])


def test_every_allowed_difference_is_in_the_drift_ledger():
    text = (ROOT / "rapp" / "KERNEL-DRIFT.md").read_text(encoding="utf-8")
    assert [e["id"] for e in ip.ALLOWED if f"`{e['id']}`" not in text] == []


def test_step_lines_drop_noise_and_run_specific_values():
    lines = ip.steps(OURS_RUN1)
    assert "RAPP Brainstem v# installed!" in lines
    assert not any("Your code" in l or "Counting objects" in l for l in lines)


def test_a_dash_one_console_drops_is_not_a_difference():
    assert ip.steps("  Powered by GitHub Copilot \u2014 no API keys needed") == ip.steps("  Powered by GitHub Copilot - no API keys needed")
