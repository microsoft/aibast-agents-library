"""
Test that build_registry.py runs successfully.
"""

import subprocess
import sys
from pathlib import Path

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
