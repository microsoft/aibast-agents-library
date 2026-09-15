"""The Agent Library is the front page; the installer and the why page hang off it."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent


def soup(relative):
    return BeautifulSoup((ROOT / relative).read_text(encoding="utf-8"), "html.parser")


def test_index_is_the_agent_library():
    page = soup("index.html")
    assert page.title.get_text(strip=True) == "AI BAST Agent Library"
    nav = page.select_one("nav.nav")
    links = [(a.get_text(strip=True), a.get("href")) for a in nav.select("a")]
    assert ("Agent Library", "index.html") in links
    assert ("Industry Workshops", "index.html?view=solutions#workshops") in links
    assert ("Install Brainstem", "docs/installer.html") in links
    assert page.select_one('meta[property="og:url"]')["content"] == "https://microsoft.github.io/aibast-agents-library/"
    text = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'href="library.html"' not in text
    assert "?return=../../index.html" in text


def test_library_html_redirects_and_keeps_deep_links():
    text = (ROOT / "library.html").read_text(encoding="utf-8")
    assert '<meta http-equiv="refresh" content="0; url=index.html">' in text
    assert '<meta name="robots" content="noindex">' in text
    assert 'href="academy.html"' in text and 'href="index.html"' in text
    script = re.search(r"<script>(.*?)</script>", text, re.DOTALL).group(1)
    if not shutil.which("node"):
        pytest.skip("Node.js required")
    probe = (
        "const calls=[];const location={search:'?view=solutions',hash:'#workshops',replace:(u)=>calls.push(u)};"
        + script + "\nconsole.log(JSON.stringify(calls));"
    )
    result = subprocess.run(["node"], input=probe, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == '["index.html?view=solutions#workshops"]'


def test_why_page_explains_the_positioning_and_links_the_paths():
    page = soup("why.html")
    text = " ".join((ROOT / "why.html").read_text(encoding="utf-8").split())
    assert "local frontier learning and rapid prototyping tool" in text
    for phrase in (
        "Not a replacement for GitHub Copilot",
        "Not a competitor to Copilot Studio or Microsoft 365 Copilot",
        "Not a production runtime",
        "The graduation path",
    ):
        assert phrase in text, phrase
    hrefs = {a.get("href") for a in page.select("a")}
    for target in ("docs/installer.html", "index.html", "academy.html", "docs/rapp-guide.html"):
        assert target in hrefs, target


def test_primary_pages_link_the_library_at_the_root():
    # metrics.html keeps its historical library.html link: its preservation gate pins it, and the redirect keeps it working.
    for relative in ("academy.html", "achievements.html", "solution.html"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert 'href="library.html"' not in text, relative
        assert 'href="index.html"' in text, relative


REQUEST_FORM = "https://forms.cloud.microsoft/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR7RNABRLLw9Eq-9okV_7Z-hUOEY3QjQ3V1RJUk43OEs4WEkzTDZQUVdNMC4u"


def test_request_info_page_embeds_the_form_and_is_linked_from_the_library():
    page = BeautifulSoup((ROOT / "request-info.html").read_text(encoding="utf-8"), "html.parser")
    iframe = page.find("iframe")
    assert iframe is not None and iframe.get("src") == REQUEST_FORM + "&embed=true"
    assert any(a.get("href") == REQUEST_FORM for a in page.select("a")), "a plain link to the form must exist as a fallback"
    assert 'href="index.html"' in page.decode()
    # The primary toolbar stays at four links (test_library_agent_upvotes pins it), so the library links the
    # request page from its footer and every solution page links it next to the one-pager and video badges.
    for relative in ("index.html", "solution.html"):
        assert 'href="request-info.html"' in (ROOT / relative).read_text(encoding="utf-8"), relative
