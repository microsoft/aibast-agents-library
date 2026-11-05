"""The AIBAST front page: a curated index whose links are checked, not trusted.

The point of the page is that someone can drop a link into ``front-page.json``
and it shows up. That only stays useful if a bad path fails the build instead of
the reader, which is what these tests are for.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.design_tokens import START_MARK, strip_block  # noqa: E402

DATA_PATH = ROOT / "front-page.json"
PAGE_PATH = ROOT / "front-page.html"
DATA = json.loads(DATA_PATH.read_text(encoding="utf-8"))
PAGE = PAGE_PATH.read_text(encoding="utf-8")

VALID_KINDS = {"page", "doc", "tool", "repo", "external"}


def links():
    for section in DATA["sections"]:
        for link in section["links"]:
            yield section["id"], link


def test_the_index_has_the_shape_the_page_renders():
    assert DATA["title"] and DATA["tagline"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", DATA["updated"]), DATA["updated"]
    assert DATA["sections"], "no sections"
    seen_ids: set[str] = set()
    for section in DATA["sections"]:
        assert re.fullmatch(r"[a-z0-9-]+", section["id"]), section["id"]
        assert section["id"] not in seen_ids, f"duplicate section id {section['id']}"
        seen_ids.add(section["id"])
        assert section["title"] and section["blurb"]
        assert section["links"], f"{section['id']} has no links"


def test_every_link_is_labelled_explained_and_typed():
    for section_id, link in links():
        where = f"{section_id}/{link.get('label')}"
        assert link["label"].strip(), where
        assert link["href"].strip(), where
        assert link["kind"] in VALID_KINDS, f"{where}: unknown kind {link['kind']}"
        why = link["why"].strip()
        assert why, f"{where}: every asset needs a reason to remember it"
        assert why[0].isupper() and why.endswith("."), f"{where}: {why!r}"


def test_no_duplicate_destinations():
    seen: dict[str, str] = {}
    for section_id, link in links():
        href = link["href"]
        assert href not in seen, f"{href} is listed twice ({seen[href]} and {section_id})"
        seen[href] = section_id


def test_every_internal_link_resolves_to_a_file_that_exists():
    missing: list[str] = []
    for section_id, link in links():
        href = link["href"]
        if urlparse(href).scheme:
            continue
        path = href.split("?", 1)[0].split("#", 1)[0]
        if not path:
            continue
        if not (ROOT / path).is_file():
            missing.append(f"{section_id}: {href}")
    assert not missing, missing


def test_external_links_are_hosts_the_site_already_publishes():
    # Keeps the front page inside what this repository already vouches for.
    allowed = {
        "github.com",
        "microsoft.github.io",
        "copilotstudio.microsoft.com",
        "make.powerapps.com",
        "portal.azure.com",
        "opensource.microsoft.com",
        "learn.microsoft.com",
        "aka.ms",
        "go.microsoft.com",
        "m365.cloud.microsoft",
        "www.microsoft.com",
    }
    unexpected = []
    for section_id, link in links():
        parsed = urlparse(link["href"])
        if not parsed.scheme:
            continue
        assert parsed.scheme == "https", f"{section_id}: {link['href']} is not https"
        if parsed.hostname not in allowed:
            unexpected.append(f"{section_id}: {parsed.hostname}")
    assert not unexpected, unexpected


def test_the_page_renders_the_index_and_nothing_else():
    assert 'fetch("front-page.json"' in PAGE
    # Section content must come from the JSON, not be duplicated into the markup.
    body = strip_block(PAGE)
    for section in DATA["sections"]:
        assert section["blurb"] not in body, (
            f"{section['id']}: blurb is hardcoded in the page as well as the index"
        )


def test_the_page_is_on_the_shared_design_system():
    assert START_MARK in PAGE, "front-page.html is missing the shared design tokens"
    own_css = re.search(r"</style>\s*</head>|<style>(.*?)</style>", strip_block(PAGE), re.DOTALL)
    assert own_css, "no page stylesheet found"
    css = strip_block(PAGE)
    css = css[css.index("<style>") : css.index("</style>")]
    literals = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)", css)
    assert not literals, f"front-page.html hardcodes colours instead of using tokens: {literals}"
    assert "var(--cp-bg)" in css and "var(--cp-text)" in css


def test_the_page_keeps_the_four_link_toolbar_and_is_reachable():
    nav = PAGE[PAGE.index('<nav aria-label="Primary navigation">') : PAGE.index("</nav>")]
    assert nav.count("<a ") == 4, "the primary toolbar is four links everywhere"
    for target in ("index.html", "academy.html", "docs/installer.html"):
        assert f'href="{target}"' in nav, target
    # A front page nothing links to is not a front page.
    library = (ROOT / "index.html").read_text(encoding="utf-8")
    assert 'href="front-page.html"' in library, "index.html does not link the front page"
