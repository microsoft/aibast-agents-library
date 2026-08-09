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


def test_only_lane_skills_are_markdown_learner_actions():
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
    assert {
        anchor.get_text(" ", strip=True)
        for anchor in markdown_downloads
    } == {
        "Download Brainstem SKILL.md",
        "Download Copilot-only SKILL.md",
    }
