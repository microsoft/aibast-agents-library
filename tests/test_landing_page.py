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


def test_landing_page_installer_uses_current_pages_host():
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "const publishedBase" in text
    assert "new URL('.', location.href).href" in text
    assert "cmd: `curl -fsSL ${publishedBase}install.sh | bash`" in text
    assert "cmd: `irm ${publishedBase}install.ps1 | iex`" in text
    assert "id=\"brainstem-win-cmd\"" in text
