import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://example.github.io/aibast-agents-library/"


def build(tmp_path):
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_public_api.py"), "--out", str(tmp_path),
         "--site", SITE, "--repository", "example/aibast-agents-library"],
        check=True, capture_output=True, text=True,
    )
    return tmp_path


def test_every_catalog_agent_gets_its_own_document(tmp_path):
    out = build(tmp_path)
    catalog = json.loads((ROOT / "solutions" / "catalog.json").read_text(encoding="utf-8"))["solutions"]
    listing = json.loads((out / "api/v1/agents.json").read_text(encoding="utf-8"))
    assert listing["count"] == len(catalog) == len(listing["agents"])
    for row in listing["agents"]:
        document = json.loads((out / "api/v1/agents" / f"{row['slug']}.json").read_text(encoding="utf-8"))
        assert document["schema"] == "aibast-public-agent/1.0"
        assert document["id"] in catalog
        assert document["links"]["page"].startswith(SITE)
        for prompt in document["prompts"]:
            assert prompt["demo_url"].startswith(SITE + "solutions/_shared/m365-copilot-demo.html?scenario=")
            assert prompt["recorded"] == (prompt["recorded_answer"] is not None)


def test_recorded_answers_are_the_transcripts_word_for_word(tmp_path):
    out = build(tmp_path)
    document = json.loads((out / "api/v1/agents/account-intelligence.json").read_text(encoding="utf-8"))
    transcripts = json.loads((ROOT / "solutions/account-intelligence/evals/transcripts.json").read_text(encoding="utf-8"))
    answers = {t["prompt"]: t["assistant_response"] for t in transcripts["transcripts"]}
    recorded = [p["recorded_answer"] for p in document["prompts"] if p["recorded"]]
    assert recorded
    for answer in recorded:
        assert answers[answer["prompt"]] == answer["answer"]


def test_discovery_files_are_well_formed_and_point_at_the_site(tmp_path):
    out = build(tmp_path)
    openapi = json.loads((out / "openapi.json").read_text(encoding="utf-8"))
    assert openapi["openapi"].startswith("3.1")
    assert openapi["servers"][0]["url"] == SITE.rstrip("/")
    llms = (out / "llms.txt").read_text(encoding="utf-8")
    assert llms.startswith("# AI BAST Agents Library\n")
    assert f"{SITE}api/v1/agents.json" in llms
    assert (out / "robots.txt").read_text(encoding="utf-8").endswith(f"Sitemap: {SITE}sitemap.xml\n")
    urls = [loc.text for url in ET.parse(out / "sitemap.xml").getroot() for loc in url]
    assert urls and all(url.startswith(SITE) for url in urls)
    entries = ET.parse(out / "feed.xml").getroot().findall("{http://www.w3.org/2005/Atom}entry")
    assert entries


def test_the_build_is_deterministic(tmp_path):
    first = build(tmp_path / "a")
    second = build(tmp_path / "b")
    names = sorted(p.relative_to(first).as_posix() for p in first.rglob("*") if p.is_file())
    assert names == sorted(p.relative_to(second).as_posix() for p in second.rglob("*") if p.is_file())
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name
