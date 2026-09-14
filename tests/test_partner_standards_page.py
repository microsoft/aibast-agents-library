"""Contract test for the standalone (nav-isolated) research/verification standards page."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STANDARDS_PAGE = REPO_ROOT / "partner-standards.html"
LIBRARY_PAGE = REPO_ROOT / "library.html"


def test_standards_page_exists_and_documents_the_standard():
    assert STANDARDS_PAGE.exists()
    page = STANDARDS_PAGE.read_text(encoding="utf-8")
    for token in (
        "dedicated source",
        "fetched and read",
        "paraphrased",
        "verbatim",
        "not independently verified by AIBAST",
        "Preview",
        "no competitive framing",
        "Attribution and partner review",
    ):
        assert token in page


def test_standards_page_is_isolated_not_linked_from_main_nav():
    # Intentionally not part of the main site navigation — it is shared
    # directly with prospective partners rather than surfaced as a tab.
    page = STANDARDS_PAGE.read_text(encoding="utf-8")
    assert "not linked from the main site" in page

    library = LIBRARY_PAGE.read_text(encoding="utf-8")
    assert "partner-standards.html" not in library
