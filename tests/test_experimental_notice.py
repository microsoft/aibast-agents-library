"""Every experimental tool surface carries the guide's notice, word for word.

The RAPP guide's Experimental tools section states the notice once
(``#experimental-tools-notice``). The tool pages, ``docs/experimental/tools.json``
and the agents that print or document a notice must say exactly the same
thing, so a reader never sees two versions of what the tools are and are not.
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "docs" / "rapp-guide.html"
EXPERIMENTAL = ROOT / "docs" / "experimental"
MANIFEST = EXPERIMENTAL / "tools.json"
TOOL_PAGES = (
    EXPERIMENTAL / "ai-migration" / "index.html",
    EXPERIMENTAL / "ai-review" / "index.html",
)
AGENT_FILES = (
    EXPERIMENTAL / "ai-migration" / "ai_migration_agent.py",
    EXPERIMENTAL / "ai-review" / "ai_review_walkthrough_agent.py",
)
LICENSE_HREF = re.compile(r"(\.\./)+LICENSE$")
TRADEMARK_HREF = "https://github.com/microsoft/aibast-agents-library#attribution"


def _squash(text: str) -> str:
    return " ".join(text.split())


def _soup(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


def _guide_notice_element():
    element = _soup(GUIDE).find(id="experimental-tools-notice")
    assert element is not None, "the guide lost #experimental-tools-notice"
    return element


GUIDE_NOTICE = _squash(_guide_notice_element().get_text())


def test_the_guide_notice_is_the_full_notice():
    assert GUIDE_NOTICE.startswith(
        "Experimental and not an officially supported Microsoft product or service."
    )
    assert "MIT license" in GUIDE_NOTICE and "Use at your own risk." in GUIDE_NOTICE


@pytest.mark.parametrize("page", TOOL_PAGES, ids=lambda p: p.parent.name)
def test_each_tool_page_shows_the_guide_notice_word_for_word(page):
    notice = _soup(page).find(id="notice")
    assert notice is not None, f"{page} has no #notice element"
    assert _squash(notice.get_text()) == GUIDE_NOTICE


@pytest.mark.parametrize("page", TOOL_PAGES, ids=lambda p: p.parent.name)
def test_each_tool_page_notice_links_the_license_and_the_trademark_notice(page):
    notice = _soup(page).find(id="notice")
    assert notice is not None, f"{page} has no #notice element"
    links = {_squash(a.get_text()): a.get("href", "") for a in notice.find_all("a")}
    guide_links = {
        _squash(a.get_text()) for a in _guide_notice_element().find_all("a")
    }
    assert set(links) == guide_links, page
    assert LICENSE_HREF.search(links["MIT license"]), links
    assert links["repository's trademark notice"] == TRADEMARK_HREF


@pytest.mark.parametrize("page", TOOL_PAGES, ids=lambda p: p.parent.name)
def test_each_tool_page_footer_links_the_trademarks(page):
    soup = _soup(page)
    footer = soup.find("footer") or soup.find(class_="footer")
    assert footer is not None, page
    hrefs = {_squash(a.get_text()): a.get("href") for a in footer.find_all("a")}
    assert hrefs.get("Trademarks") == TRADEMARK_HREF, hrefs


def test_every_tools_json_disclaimer_is_the_guide_notice():
    doc = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert doc["disclaimer"] == GUIDE_NOTICE
    for tool in doc["tools"]:
        assert tool["disclaimer"] == GUIDE_NOTICE, tool["name"]


@pytest.mark.parametrize("agent_file", AGENT_FILES, ids=lambda p: p.stem)
def test_each_agent_documents_the_guide_notice(agent_file):
    spec = importlib.util.spec_from_file_location(agent_file.stem, agent_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert GUIDE_NOTICE in _squash(module.__doc__ or "")
    if hasattr(module, "NOTICE"):
        # The constant the agent prints into its output.
        assert module.NOTICE == GUIDE_NOTICE
