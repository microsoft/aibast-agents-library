import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = re.compile(
    r"Hard mode|hard mode|Hard-mode|HARD MODE|>\s*Hard\s*<|"
    r"Hard tab|Hard completions|Hard steps|Hard captures|"
    r"Literal browser hard-mode|reusable hard-mode|expected hard-mode"
)


def public_mode_files():
    yield ROOT / "library.html"
    yield ROOT / "achievements.html"
    yield ROOT / "metrics.html"
    yield ROOT / "scripts" / "build_metrics.py"
    yield ROOT / "tools" / "scaffold_solution_journey.py"
    for pattern in ("*.html", "*.md", "*.json"):
        yield from (ROOT / "solutions").rglob(pattern)


def test_public_workshop_terminology_uses_manual_mode():
    findings = []
    for path in public_mode_files():
        text = path.read_text(encoding="utf-8")
        match = FORBIDDEN.search(text)
        if match:
            findings.append(f"{path.relative_to(ROOT)}: {match.group(0)}")
    assert not findings, findings


def test_manual_mode_keeps_backward_compatible_internal_keys():
    scaffold = (ROOT / "tools" / "scaffold_solution_journey.py").read_text(
        encoding="utf-8"
    )
    quest = (
        ROOT / "solutions" / "account-intelligence" / "quest.html"
    ).read_text(encoding="utf-8")

    assert "Manual mode complete" in scaffold
    assert '>Manual</button>' in quest
    assert 'data-mode="hard"' in quest
    assert 'data-path="hard"' in quest
    assert '"hard-mode-complete"' in quest
