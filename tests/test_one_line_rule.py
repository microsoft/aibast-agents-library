"""The one-line rule (2026-11-06): a person briefs their AI with ONE pasted line of the shape
"Go and read <public skill URL> and do X". The skill holds every step. Nobody downloads, drags or
attaches an instruction file, and nobody pastes a wall of instructions.

Guards the front doors a newcomer lands on, plus the generated workshop pages.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONE_LINE = re.compile(r"Go and read https?://\S+\.md and \S")
# phrasings that move work from the machine to the person
FORBIDDEN = [
    re.compile(r"download(?:ed|ing)?\b[^.<]{0,80}\bSKILL\.md", re.I),
    re.compile(r"\bdrag\b[^.<]{0,60}\b(downloaded file|SKILL\.md)", re.I),
    re.compile(r"Download (Brainstem|Copilot-only) SKILL\.md", re.I),
    # only instruction files are forbidden as downloads; knowledge files, email drafts and other data may be downloaded
    re.compile(r"<a[^>]+href=\"(?![^\"]*\bmanual/)[^\"]*skill\.md\"[^>]*\bdownload\b", re.I),
]
FRONT_DOORS = [
    ROOT / "docs/start/index.html",
    ROOT / "docs/start/prompt.txt",
    ROOT / "docs/start/business-prompting.md",
    ROOT / "docs/installer.html",
]


def _hits(text: str) -> list[str]:
    return [m.group(0)[:80] for pat in FORBIDDEN for m in pat.finditer(text)]


def test_front_doors_hand_the_ai_one_line_and_nothing_to_download():
    for page in FRONT_DOORS:
        text = page.read_text(encoding="utf-8")
        assert ONE_LINE.search(text), f"{page.relative_to(ROOT)} has no 'Go and read … and do X' line"
        assert _hits(text) == [], (page.relative_to(ROOT), _hits(text))


def test_pasted_prompts_are_one_line():
    """A pasteable box is never a wall of instructions: at most 240 characters, no numbered steps."""
    for page, box_id in ((ROOT / "docs/start/index.html", "prompt"), (ROOT / "docs/start/index.html", "bp"), (ROOT / "docs/installer.html", "vscode-prompt")):
        text = page.read_text(encoding="utf-8")
        m = re.search(r'id=["\']?%s["\']?[^>]*>(.*?)</' % re.escape(box_id), text, re.S)
        assert m, (page.relative_to(ROOT), box_id)
        line = re.sub(r"\s+", " ", m.group(1)).strip()
        assert len(line) <= 240 and "\n1." not in m.group(1), (page.relative_to(ROOT), box_id, len(line))


def test_generated_workshops_use_one_line_with_one_optional_facilitator_download():
    pages = sorted(ROOT.glob("solutions/*/quest.html")) + sorted(ROOT.glob("solutions/*/field-guide.html"))
    assert pages, "no generated workshop pages found"
    optional_download = re.compile(
        r'<a class="button" href="../../skills/aibast-easy-mode/SKILL.md" '
        r'download="SKILL.md">Download SKILL.md</a>'
    )
    for page in pages:
        text = page.read_text(encoding="utf-8")
        matches = optional_download.findall(text)
        assert len(matches) == (1 if page.name == "quest.html" else 0), page
        if matches:
            assert matches[0] in text.split('<details class="facilitator-details">', 1)[1]
        assert _hits(optional_download.sub("", text)) == [], page
    for p in sorted(ROOT.glob("solutions/*/quest.html")):
        assert ONE_LINE.search(p.read_text(encoding="utf-8")), f"{p.relative_to(ROOT)} has no one-line brief"
