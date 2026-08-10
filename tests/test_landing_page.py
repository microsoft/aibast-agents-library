from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent


def test_landing_page_keeps_two_primary_actions():
    soup = BeautifulSoup(
        (ROOT / "index.html").read_text(encoding="utf-8"),
        "html.parser",
    )
    actions = soup.select(".hero-actions a")
    assert [(link.get_text(" ", strip=True), link.get("href")) for link in actions] == [
        ("Open Production Guide", "docs/rapp-guide.html"),
        ("Browse Agent Library", "library.html"),
    ]
