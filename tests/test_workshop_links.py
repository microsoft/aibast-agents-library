import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    ROOT / "solutions/time-entry-billing/quest.html",
    ROOT / "solutions/time-entry-billing/manual-tutorial.html",
    ROOT / "solutions/time-entry-billing/field-guide.html",
    ROOT / "solutions/time-entry-billing/evidence-report.html",
]
RAW_SUFFIXES = {".md", ".json", ".py"}


def test_user_facing_links_never_open_raw_files():
    for page in PAGES:
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        for anchor in soup.select("a[href]"):
            path = urlparse(anchor["href"]).path
            suffix = Path(path).suffix.lower()
            if suffix not in RAW_SUFFIXES:
                continue
            assert anchor.has_attr("download"), (
                page,
                anchor.get_text(" ", strip=True),
                anchor["href"],
            )


def test_one_skill_uses_one_pasted_line_and_one_optional_facilitator_download():
    quest = BeautifulSoup(
        PAGES[0].read_text(encoding="utf-8"),
        "html.parser",
    )
    easy_path = quest.select_one('[data-path="easy"]')
    assert easy_path is not None
    markdown_downloads = [
        anchor
        for anchor in easy_path.select("a[href][download]")
        if Path(urlparse(anchor["href"]).path).suffix.lower() == ".md"
    ]
    assert len(markdown_downloads) == 1
    download = markdown_downloads[0]
    assert download["href"] == "../../skills/aibast-easy-mode/SKILL.md"
    assert download["download"] == "SKILL.md"
    assert download.find_parent("details", class_="facilitator-details") is not None
    text = easy_path.get_text(" ", strip=True)
    assert "Drag the downloaded" not in text
    lines = re.findall(r"Go and read https?://\S+/SKILL\.md and run the .+? workshop for me\.", text)
    assert len(lines) == 1, text[:400]
