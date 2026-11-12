"""The installer page uses one wide column width, set in one place."""
from pathlib import Path
import re

PAGE = Path(__file__).resolve().parents[1] / "docs" / "installer.html"


def test_one_width_setting_and_it_is_wide():
    html = PAGE.read_text(encoding="utf-8")
    found = re.findall(r"--installer-width:\s*min\((\d+)px", html)
    assert len(found) == 1, "set --installer-width exactly once"
    assert int(found[0]) >= 1000, "the installer column must stay wide"


def test_no_narrow_fixed_columns_come_back():
    html = PAGE.read_text(encoding="utf-8")
    narrow = [int(n) for n in re.findall(r"(?<!\()max-width:\s*(\d+)px", html) if 400 <= int(n) < 1000]
    assert not narrow, f"fixed narrow columns found: {narrow}; use var(--installer-width)"
