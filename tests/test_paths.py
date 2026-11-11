"""Path source, static fallback and append-only build contracts."""

import copy
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

import pytest
from bs4 import BeautifulSoup

from tools.library_api_paths import destination_urls, page_outputs, paths_document
from scripts.build_pages_site import classify_source_path, INCLUDE
from tools.build_solution_export import bundle_bytes

ROOT = Path(__file__).resolve().parents[1]


def paths():
    return json.loads((ROOT / "api/v1/paths.json").read_text())


def test_every_question_has_a_consumer_and_every_route_has_real_steps():
    doc = paths()
    assert len(doc["questions"]) <= 3
    for question in doc["questions"]:
        assert question["used_by"]
        assert not any(answer["label"] == "Other" for answer in question.get("answers", []))
    for route in doc["routes"]:
        assert 2 <= len(route["steps"]) <= (3 if route["needs"] else 4)
        if route["area"]:
            assert route["solutions"]
    for url in destination_urls(doc):
        assert (ROOT / urlsplit(url).path).is_file()


def test_no_script_list_and_every_destination_strip_are_generated():
    doc = paths()
    output = page_outputs(ROOT, doc)
    for name, content in output.items():
        assert (ROOT / name).read_bytes() == content, name
    soup = BeautifulSoup(output["paths.html"], "html.parser")
    assert {a["href"] for a in soup.select("#fallback li a")} == set(destination_urls(doc))
    for url in destination_urls(doc):
        name = urlsplit(url).path
        assert BeautifulSoup(output[name], "html.parser").select_one("script[data-path-strip]")


def test_missing_destination_is_a_build_error():
    solutions = {path.stem: json.loads(path.read_text())
                 for path in (ROOT / "api/v1/solutions").glob("*.json")}
    broken = copy.deepcopy(solutions)
    first = next(iter(broken.values()))
    first["learn"]["workshop"] = "solutions/missing-synthetic-workshop.html"
    with pytest.raises(ValueError, match="Missing path destination"):
        paths_document(ROOT, broken)


def test_browser_state_is_url_only_and_request_wiring_is_unchanged():
    for name in ("path-chooser.js", "path-route.js"):
        script = (ROOT / "solutions/_shared" / name).read_text()
        assert "localStorage" not in script and "sessionStorage" not in script
        assert "innerHTML" not in script
        assert "api.github.com" not in script and "no-store" not in script
    request = (ROOT / "request-info.html").read_text()
    assert 'src="https://forms.cloud.microsoft/Pages/ResponsePage.aspx?' in request


def test_chooser_assets_ship_on_pages():
    for name in ("paths.html", "paths/paths.source.json", "api/v1/paths.json",
                 "solutions/_shared/path-chooser.js", "solutions/_shared/path-route.js",
                 "docs/path-requirements.html"):
        assert classify_source_path(PurePosixPath(name)) == INCLUDE


def test_downloaded_solution_pages_do_not_depend_on_site_navigation():
    page = ROOT / "solutions/account-intelligence/quest.html"
    assert b"data-path-strip" in page.read_bytes()
    assert b"data-path-strip" not in bundle_bytes(page)
