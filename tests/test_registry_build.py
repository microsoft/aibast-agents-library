"""
Test that build_registry.py runs successfully.
"""

import subprocess
import sys
from pathlib import Path

from build_registry import resolve_added_date

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_registry_build_exits_zero():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "build_registry.py")],
        capture_output=True, text=True, timeout=60,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"build_registry.py failed (exit {result.returncode})\n"
        f"stdout: {result.stdout[:500]}\n"
        f"stderr: {result.stderr[:500]}"
    )


def test_registry_preserves_published_added_date_with_shallow_history():
    path = Path("agents/@aibast/example.py")
    name = "@aibast/example"

    assert resolve_added_date(
        path,
        name,
        {path.as_posix(): "2026-08-14T12:00:00Z"},
        {name: {"_added_at": "2025-01-02T03:04:05Z"}},
    ) == "2025-01-02T03:04:05Z"


def test_registry_uses_git_date_for_new_agents():
    path = Path("agents/@aibast/new.py")

    assert resolve_added_date(
        path,
        "@aibast/new",
        {path.as_posix(): "2026-08-14T12:00:00Z"},
        {},
    ) == "2026-08-14T12:00:00Z"
