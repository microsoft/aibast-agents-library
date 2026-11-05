"""Community agents: the demo submission form, its checker, the page, and the
rule that community demos stay out of the agent library until one graduates."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from tests.test_catalog_export import probe, run_community_tools_node
from tools import demo_submission as ds

ROOT = Path(__file__).resolve().parents[1]
FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "demo-submission.yml"
WORKFLOW = ROOT / ".github" / "workflows" / "demo-submission.yml"
MANIFEST = json.loads((ROOT / "community_tools.json").read_text(encoding="utf-8"))
DEMOS = [t for t in MANIFEST["tools"] if t.get("kind") == "demo"]

SAMPLE_DEMO = {
    "id": "sample-community-demo",
    "kind": "demo",
    "name": "Sample Community Demo",
    "url": "https://www.youtube.com/watch?v=abc123",
    "author": "Sample Team",
    "description": "One sentence. Two sentences.",
    "industry": "Healthcare",
    "products": ["Copilot Studio"],
    "submission_issue": 1,
    "thumbnail": "https://i.ytimg.com/vi/abc123/mqdefault.jpg",
}
DEMO_LABELS = ("demo: submitted", "demo: ready for review", "demo: needs changes", "demo: approved")


def filled_body(**overrides):
    values = {
        "title": "Tiered Digital Huddle Board",
        "video": "https://www.youtube.com/watch?v=9A8k0z77NFo",
        "description": (
            "A hospital runs its daily tiered huddles on one live board. "
            "Copilot briefs the whole board before the huddle. "
            "One approval escalates an issue up a tier and notifies the right people in Teams."
        ),
        "industry": "Healthcare",
        "team": "Microsoft Healthcare AI Business Process Solutions",
        "onepager": "_No response_",
        "products": ["Copilot Studio", "Dataverse", "Teams", "Power Apps"],
        "confirm": list(ds.REQUIRED_CONFIRMATIONS),
    }
    values.update(overrides)
    products = "\n".join(
        f"- [{'X' if p in values['products'] else ' '}] {p}" for p in ds.PRODUCT_OPTIONS
    )
    confirmations = "\n".join(
        f"- [{'X' if c in values['confirm'] else ' '}] {c}" for c in ds.REQUIRED_CONFIRMATIONS
    )
    return (
        f"### Demo title\n\n{values['title']}\n\n"
        f"### Public video URL\n\n{values['video']}\n\n"
        f"### Short description\n\n{values['description']}\n\n"
        f"### Industry\n\n{values['industry']}\n\n"
        f"### Microsoft products used\n\n{products}\n\n"
        f"### Owning team or channel\n\n{values['team']}\n\n"
        f"### One-pager URL (optional)\n\n{values['onepager']}\n\n"
        f"### Before you submit\n\n{confirmations}\n"
    )


# ------------------------------------------------------------------ the form
def test_form_parses_and_matches_the_checker():
    yaml = pytest.importorskip("yaml")
    form = yaml.safe_load(FORM.read_text(encoding="utf-8"))
    assert form["name"] == "Submit a demo to Community agents"
    assert form["labels"] == ["demo: submitted"]
    fields = {item["id"]: item for item in form["body"] if "id" in item}
    labels = {f["attributes"]["label"] for f in fields.values()}
    assert {ds.TITLE, ds.VIDEO, ds.DESCRIPTION, ds.INDUSTRY, ds.PRODUCTS,
            ds.TEAM, ds.ONEPAGER, ds.CONFIRMATIONS} == labels
    for required in ("title", "video", "description", "industry", "team"):
        assert fields[required]["validations"]["required"] is True
    assert tuple(fields["industry"]["attributes"]["options"]) == ds.INDUSTRIES
    assert tuple(o["label"] for o in fields["products"]["attributes"]["options"]) == ds.PRODUCT_OPTIONS
    confirm = fields["confirmations"]["attributes"]["options"]
    assert tuple(o["label"] for o in confirm) == ds.REQUIRED_CONFIRMATIONS
    assert all(o.get("required") is True for o in confirm)


def test_form_industries_match_the_library_names():
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    block = re.search(r"const CATEGORY_NAMES = \{(.*?)\};", index, re.S).group(1)
    names = set(re.findall(r':\s*"([^"]+)"', block))
    assert set(ds.INDUSTRIES) == names


def test_public_copy_follows_the_tone_rules():
    for path in (FORM, ROOT / "community-agents.html", ROOT / "community-tools.html"):
        text = path.read_text(encoding="utf-8")
        assert "RAPP Factory" not in text, path
        assert not re.search(r"[\U0001F300-\U0001FAFF]", text), path


# ------------------------------------------------------------- the checker
def test_parser_reads_a_filled_form():
    sections = ds.parse_issue_form(filled_body())
    assert sections[ds.TITLE] == "Tiered Digital Huddle Board"
    entry, problems = ds.validate(sections)
    assert problems == []
    assert entry["id"] == "tiered-digital-huddle-board"
    assert entry["kind"] == "demo"
    assert entry["products"] == ["Copilot Studio", "Dataverse", "Power Apps", "Teams"]
    assert entry["author"] == "Microsoft Healthcare AI Business Process Solutions"
    assert "onepager" not in entry


def test_unticked_confirmation_is_rejected():
    body = filled_body(confirm=list(ds.REQUIRED_CONFIRMATIONS[:-1]))
    _, problems = ds.validate(ds.parse_issue_form(body))
    assert any("no Azure services" in p for p in problems)


@pytest.mark.parametrize("url, message", [
    ("http://www.youtube.com/watch?v=x", "https"),
    ("https://example.com/video", "public YouTube link"),
    ("https://user:pw@youtube.com/watch?v=x", "plain public"),
    ("not a url", "https"),
])
def test_bad_video_links_are_rejected(url, message):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(video=url)))
    assert any(message in p for p in problems), problems


def test_allowed_video_hosts():
    assert ds.classify_video_url("https://youtu.be/9A8k0z77NFo") == "youtube"


@pytest.mark.parametrize("url", [
    "https://contoso.sharepoint.com/:v:/s/team/EabcXYZ",
    "https://web.microsoftstream.com/video/abc",
])
def test_stream_links_get_a_clear_youtube_only_answer(url):
    """Stream videos need a sign-in, so the form and checker accept YouTube only."""
    with pytest.raises(ds.SubmissionError, match="need a sign-in"):
        ds.classify_video_url(url)
    form = FORM.read_text(encoding="utf-8")
    assert "public Microsoft Stream link" not in form
    assert "Microsoft Stream videos need a sign-in" in form


@pytest.mark.parametrize("field, text", [
    ("description", "Built in the RAPP Factory. Second sentence."),
    ("description", "This is confidential. Second sentence."),
    ("description", "Runs on Azure Functions. Second sentence."),
    ("team", "Contact jane@example.com"),
    ("team", "@someone"),
])
def test_forbidden_words_and_personal_contacts_are_rejected(field, text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(**{field: text})))
    assert problems


def test_description_length_is_two_to_four_sentences():
    _, problems = ds.validate(ds.parse_issue_form(filled_body(description="Only one.")))
    assert any("2 to 4 sentences" in p for p in problems)


def test_youtube_resolution_uses_oembed_and_keeps_https_thumbnail():
    seen = []

    def fetch(url):
        seen.append(url)
        return {"title": "t", "thumbnail_url": "https://i.ytimg.com/vi/x/hqdefault.jpg"}

    facts = ds.resolve_video("https://www.youtube.com/watch?v=x", "youtube", fetch=fetch)
    assert seen[0].startswith("https://www.youtube.com/oembed?")
    # hqdefault is 4:3 with black bars baked in; mqdefault is 16:9 without them.
    assert facts["thumbnail"] == "https://i.ytimg.com/vi/x/mqdefault.jpg"

    def missing(url):
        raise ValueError("404")

    with pytest.raises(ds.SubmissionError):
        ds.resolve_video("https://www.youtube.com/watch?v=x", "youtube", fetch=missing)


def test_apply_adds_then_replaces_the_demo_and_keeps_tools():
    manifest = json.loads(json.dumps(MANIFEST))
    tool_count = len([t for t in manifest["tools"] if t.get("kind", "tool") == "tool"])
    entry, _ = ds.validate(ds.parse_issue_form(filled_body()))
    entry["id"] = "unit-test-demo"
    ds.apply_entry(manifest, entry, 7, "2026-10-28")
    ds.apply_entry(manifest, dict(entry), 7, "2026-10-29")
    demos = [t for t in manifest["tools"] if t.get("id") == "unit-test-demo"]
    assert len(demos) == 1 and demos[0]["submission_issue"] == 7
    assert "_video_kind" not in demos[0]
    assert manifest["count"] == len(manifest["tools"])
    assert manifest["snapshot_date"] == "2026-10-29"
    assert len([t for t in manifest["tools"] if t.get("kind", "tool") == "tool"]) == tool_count


def test_saved_demo_thumbnails_have_no_letterbox_bars():
    for demo in DEMOS:
        if "i.ytimg.com" in demo.get("thumbnail", ""):
            assert not demo["thumbnail"].endswith("/hqdefault.jpg"), demo["id"]


def _two_team_manifest():
    manifest = json.loads(json.dumps(MANIFEST))
    original = {**SAMPLE_DEMO, "submission_issue": 335, "graduated_to": "tiered-huddle-board"}
    manifest["tools"].append(original)
    manifest["count"] = len(manifest["tools"])
    return manifest, original


def test_a_new_submission_cannot_replace_another_teams_demo():
    manifest, original = _two_team_manifest()
    takeover = {**SAMPLE_DEMO, "author": "Another Team", "url": "https://youtu.be/zzz"}
    takeover.pop("submission_issue")
    with pytest.raises(ds.SubmissionError, match="already used by another demo"):
        ds.apply_entry(manifest, takeover, 999, "2026-10-30")
    demos = [t for t in manifest["tools"] if t.get("id") == SAMPLE_DEMO["id"]]
    assert demos == [original]


def test_the_same_issue_can_update_its_demo_and_keeps_its_graduation():
    manifest, _ = _two_team_manifest()
    update = {**SAMPLE_DEMO, "description": "New words. Still two sentences."}
    ds.apply_entry(manifest, update, 335, "2026-10-30")
    demos = [t for t in manifest["tools"] if t.get("id") == SAMPLE_DEMO["id"]]
    assert len(demos) == 1
    assert demos[0]["description"] == "New words. Still two sentences."
    assert demos[0]["graduated_to"] == "tiered-huddle-board"


def test_the_check_reports_a_title_another_demo_already_uses(tmp_path):
    manifest, _ = _two_team_manifest()
    body = filled_body(title=SAMPLE_DEMO["name"])
    _, problems = ds.run_check(body, offline=True, manifest=manifest, issue=999)
    assert any("already used by another demo" in p for p in problems), problems
    _, problems = ds.run_check(body, offline=True, manifest=manifest, issue=335)
    assert problems == []

    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "body.md").write_text(body, encoding="utf-8")
    result, comment = tmp_path / "r.json", tmp_path / "c.md"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demo_submission.py"), "check", "--offline",
         "--issue", "999", "--manifest", str(path), "--body-file", str(tmp_path / "body.md"),
         "--result", str(result), "--comment", str(comment)],
        check=True, capture_output=True,
    )
    assert json.loads(result.read_text())["ok"] is False
    assert "already used by another demo" in comment.read_text()


def test_the_check_reports_a_title_used_by_a_related_resource():
    manifest = json.loads(json.dumps(MANIFEST))
    resource = next(t for t in manifest["tools"] if t.get("kind", "tool") == "tool")
    _, problems = ds.run_check(
        filled_body(title=resource["name"]), offline=True, manifest=manifest, issue=5
    )
    assert any("related resource" in p for p in problems), problems


def test_a_title_with_no_letters_or_numbers_fails_at_check_time():
    _, problems = ds.validate(ds.parse_issue_form(filled_body(title="\u65e5\u672c\u8a9e\u30c7\u30e2")))
    assert any("English letter or number" in p for p in problems), problems


def test_apply_never_overwrites_a_related_resource():
    manifest = json.loads(json.dumps(MANIFEST))
    entry, _ = ds.validate(ds.parse_issue_form(filled_body()))
    entry["id"] = manifest["tools"][0]["id"]
    with pytest.raises(ds.SubmissionError):
        ds.apply_entry(manifest, entry, 3, "2026-10-28")


def test_check_cli_writes_result_and_comment(tmp_path):
    body = tmp_path / "body.md"
    body.write_text(filled_body(confirm=[]), encoding="utf-8")
    result, comment = tmp_path / "r.json", tmp_path / "c.md"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demo_submission.py"), "check", "--offline",
         "--body-file", str(body), "--result", str(result), "--comment", str(comment)],
        check=True, capture_output=True,
    )
    assert json.loads(result.read_text())["ok"] is False
    assert "needs a few changes" in comment.read_text()


def test_check_cli_finishes_on_a_very_long_word_of_listed_names(tmp_path):
    """Round 8: one word made of 1200 listed names used to raise
    RecursionError, so no comment was written and the submitter got no reply."""
    body = tmp_path / "body.md"
    body.write_text(
        filled_body(description="Tags: " + "gpt" * 1200 + ". The agent drafts."), encoding="utf-8"
    )
    result, comment = tmp_path / "r.json", tmp_path / "c.md"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demo_submission.py"), "check", "--offline",
         "--body-file", str(body), "--result", str(result), "--comment", str(comment)],
        check=True, capture_output=True,
    )
    problems = json.loads(result.read_text())["problems"]
    assert any(p.startswith(ds.OTHER_AI_PRODUCTS_PROBLEM) for p in problems)
    assert "needs a few changes" in comment.read_text()


def _run_comment_step(tmp_path, files: dict[str, str]) -> list[str]:
    """Run the check job's 'Comment and label' step with a stand-in gh."""
    yaml = pytest.importorskip("yaml")
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["check"]["steps"]
    step = next(s for s in steps if s.get("name") == "Comment and label")
    runner = tmp_path / "runner"
    runner.mkdir()
    for name, text in files.items():
        (runner / name).write_text(text, encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh.log"
    gh = bin_dir / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$GH_LOG"\n'
        'if [ "$1 $2" = "issue comment" ]; then cat "$5" >> "$GH_LOG"; fi\n',
        encoding="utf-8",
    )
    gh.chmod(0o755)
    py = bin_dir / "python"
    py.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding="utf-8")
    py.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}",
           "RUNNER_TEMP": str(runner), "NUMBER": "7", "GH_LOG": str(log)}
    subprocess.run(["bash", "-e", "-c", step["run"]], env=env, check=True, capture_output=True)
    return log.read_text(encoding="utf-8").splitlines()


def test_comment_step_runs_and_replies_when_the_check_crashed(tmp_path):
    """Round 8: when the check step crashed, the 'Comment and label' step was
    skipped, so the issue got no reply and no label."""
    yaml = pytest.importorskip("yaml")
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["check"]["steps"]
    check = next(s for s in steps if s.get("name") == "Check the submission")
    step = next(s for s in steps if s.get("name") == "Comment and label")
    assert "!cancelled()" in step.get("if", ""), "the step must run after a failed check"
    assert f"steps.{check['id']}.outcome" in step["if"]
    lines = _run_comment_step(tmp_path, {})
    assert any(line.startswith("issue comment 7") for line in lines)
    assert any("could not finish" in line for line in lines)
    assert any('--add-label demo: needs changes' in line for line in lines)


def test_comment_step_still_posts_the_check_result(tmp_path):
    lines = _run_comment_step(tmp_path, {
        "comment.md": "Thank you. This demo passed.\n",
        "result.json": '{"ok": true, "problems": []}\n',
    })
    assert "Thank you. This demo passed." in lines
    assert any('--add-label demo: ready for review' in line for line in lines)


# ------------------------------------------------------------ the workflow
def test_workflow_is_least_privilege_pinned_and_injection_safe():
    text = WORKFLOW.read_text(encoding="utf-8")
    yaml = pytest.importorskip("yaml")
    flow = yaml.safe_load(text)
    assert flow["permissions"] == {}
    assert flow["jobs"]["check"]["permissions"] == {"contents": "read", "issues": "write"}
    assert set(flow["jobs"]["approve"]["permissions"]) == {"contents", "issues", "pull-requests"}
    for uses in re.findall(r"uses:\s*(\S+)", text):
        assert re.search(r"@[0-9a-f]{40}$", uses), uses
    for job in flow["jobs"].values():
        for step in job["steps"]:
            run = step.get("run", "")
            assert "github.event.issue.body" not in run
            assert "github.event.issue.title" not in run
            assert "${{" not in run, step.get("name")
    assert "collaborators/$SENDER/permission" in text
    assert "Closes #" in text


def test_workflow_creates_its_own_labels_first():
    """GitHub drops form labels a repository does not have, so the workflow
    must create every label it uses, and promotion must name them."""
    yaml = pytest.importorskip("yaml")
    text = WORKFLOW.read_text(encoding="utf-8")
    flow = yaml.safe_load(text)
    used = set(re.findall(r"demo: [a-z ]+[a-z]", text)) | {"demo: submitted"}
    assert used == set(DEMO_LABELS)
    for name, job in flow["jobs"].items():
        first = job["steps"][0].get("run", "")
        for label in DEMO_LABELS:
            assert f'gh label create "{label}"' in first and "--force" in first, (name, label)
    for path in (ROOT / "docs" / "RELEASE-PROCESS.md", ROOT / "tools" / "promotion_check.sh"):
        doc = path.read_text(encoding="utf-8")
        for label in DEMO_LABELS:
            assert label in doc, (path.name, label)


# ----------------------------------------------------------------- the page
def test_page_has_shelf_submit_button_and_related_resources():
    page = BeautifulSoup((ROOT / "community-agents.html").read_text(encoding="utf-8"), "html.parser")
    assert page.title.get_text().startswith("Community agents")
    assert page.select_one("#demo-grid")
    assert page.select_one("#community-grid")
    assert page.find("h2", string="Colleague demos")
    assert page.find("h2", string="Related resources")
    submit = page.select_one("#submit-demo")
    assert submit.get_text(strip=True) == "Submit your demo"
    assert submit["href"].endswith("/issues/new?template=demo-submission.yml")
    assert "kody-w" not in str(page)
    assert 'data-clarity-project' in str(page)
    assert "aibast-design:start" in str(page)


def test_small_print_is_written_for_visitors_not_the_manifest_schema():
    result = run_community_tools_node(
        "globalThis.fetch = async () => ({ok: true, json: async () => community});",
        """
await renderCommunityTools();
console.log(JSON.stringify({note: $("community-note").textContent, errors}));
""",
    )
    assert result["errors"] == []
    note = result["note"]
    assert note != MANIFEST["note"]
    assert "not an endorsement" in note
    for word in ("kind", "Entries", "Backs the", "manifest"):
        assert word not in note, word


def test_old_page_redirects_and_keeps_hash_and_query():
    text = (ROOT / "community-tools.html").read_text(encoding="utf-8")
    assert 'location.replace("community-agents.html" + location.search + location.hash)' in text
    assert 'content="0; url=community-agents.html"' in text
    page = BeautifulSoup(text, "html.parser")
    assert "This page is now Community agents" in page.body.get_text(" ", strip=True)
    assert page.select_one('body a[href="community-agents.html"]')


def test_page_renders_demos_as_cards_and_submit_points_at_this_repo():
    result = run_community_tools_node(
        f"""
community.tools.push({json.dumps({**SAMPLE_DEMO, "graduated_to": "tiered-huddle-board"})});
community.tools.push({json.dumps({**SAMPLE_DEMO, "id": "x2", "name": "<b>x</b>", "thumbnail": "javascript:1"})});
community.count = community.tools.length;
globalThis.fetch = async () => ({{ok: true, json: async () => community}});
const submit = {{href: ""}};
nodes.set("submit-demo", submit);
""",
        """
await renderCommunityTools();
console.log(JSON.stringify({
  demos: $("demo-grid").innerHTML, tools: $("community-grid").innerHTML,
  submit: $("submit-demo").href, errors
}));
""",
    )
    assert result["errors"] == []
    assert result["demos"].count('class="demo-card"') == len(DEMOS) + 2
    assert "Sample Team" in result["demos"]
    assert "Healthcare" in result["demos"]
    assert 'target="_blank"' in result["demos"]
    assert "<iframe" not in result["demos"]
    assert "&lt;b&gt;" in result["demos"]
    assert "javascript:" not in result["demos"]
    assert 'href="solutions/tiered-huddle-board/quest.html">Now in the library' in result["demos"]
    assert SAMPLE_DEMO["url"] not in result["tools"]
    # The harness serves the page from kody-w.github.io, so the form link follows it.
    assert result["submit"] == (
        "https://github.com/kody-w/aibast-agents-library/issues/new?template=demo-submission.yml"
    )


# ---------------------------------------------- isolation from the library
def test_manifest_stays_valid_for_both_kinds():
    assert MANIFEST["schema"] == "aibast-community-tools/1.0"
    assert MANIFEST["count"] == len(MANIFEST["tools"])
    assert "Community agents" in MANIFEST["note"]
    ids = [t["id"] for t in MANIFEST["tools"]]
    assert len(ids) == len(set(ids))
    for entry in MANIFEST["tools"]:
        assert entry.get("kind", "tool") in {"tool", "demo"}
        for key in ("id", "name", "url", "author", "description"):
            assert isinstance(entry[key], str) and entry[key].strip()
        assert entry["url"].startswith("https://")
    for demo in DEMOS:
        assert demo["industry"] in ds.INDUSTRIES
        assert demo["products"] and set(demo["products"]) <= set(ds.PRODUCT_OPTIONS)
        assert isinstance(demo["submission_issue"], int)
        assert ds.forbidden_terms_in(" ".join([demo["name"], demo["description"], demo["author"]])) == []


def test_registry_build_skips_demo_entries(tmp_path, monkeypatch):
    import build_registry

    manifest = json.loads(json.dumps(MANIFEST))
    manifest["tools"].append(SAMPLE_DEMO)
    manifest["count"] = len(manifest["tools"])
    path = tmp_path / "community_tools.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(build_registry, "COMMUNITY_TOOLS_FILE", path)
    errors = []
    rows = build_registry.load_community_tools(errors)
    assert errors == []
    assert all(r.get("kind", "tool") == "tool" for r in rows)
    assert SAMPLE_DEMO["id"] not in {r["id"] for r in rows}


def _library_surfaces():
    paths = [ROOT / "registry.json", ROOT / "solutions.json", ROOT / "academy.json",
             ROOT / "solutions" / "catalog.json"]
    paths += sorted((ROOT / "state").glob("*.json"))
    return [p for p in paths if p.exists()]


def _demo_leaks(demo, paths):
    """Library files that mention the demo's own id or name.

    A graduated demo lives in the library under its template slug
    (graduated_to), so only the demo's own id and name are leaks.
    """
    leaks = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if f'"{demo["id"]}"' in text or demo["name"] in text:
            leaks.append(path.name)
    return leaks


@pytest.mark.parametrize("demo", DEMOS + [SAMPLE_DEMO], ids=lambda d: d["id"])
def test_no_demo_appears_in_library_catalogs_academy_or_metrics(demo):
    registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
    assert demo["id"] not in {t.get("id") for t in registry.get("community_tools", [])}
    assert all(t.get("kind", "tool") == "tool" for t in registry.get("community_tools", []))
    assert _demo_leaks(demo, _library_surfaces()) == []


def test_leak_check_catches_a_graduated_demo_copied_into_the_academy(tmp_path):
    demo = {**SAMPLE_DEMO, "graduated_to": "tiered-huddle-board"}
    academy = tmp_path / "academy.json"
    academy.write_text(json.dumps({"courses": [{"id": demo["id"], "name": demo["name"]}]}))
    assert _demo_leaks(demo, [academy]) == ["academy.json"]
    named = tmp_path / "state.json"
    named.write_text(json.dumps({"title": demo["name"]}))
    assert _demo_leaks(demo, [named]) == ["state.json"]


@pytest.mark.parametrize("demo", [d for d in DEMOS if d.get("graduated_to")] or [None], ids=lambda d: d["id"] if d else "none")
def test_graduated_demo_links_to_a_real_library_solution(demo):
    if demo is None:
        pytest.skip("no graduated demos yet")
    assert (ROOT / "solutions" / demo["graduated_to"] / "quest.html").is_file()


def test_library_page_only_links_community_agents_from_the_footer():
    page = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
    links = page.select('a[href^="community-agents.html"]')
    assert len(links) == 1
    assert links[0].find_parent("footer") is not None
    for demo in DEMOS:
        assert demo["name"] not in str(page)


def test_library_export_bundle_skips_demo_entries():
    result = probe(
        f"""
community.tools.push({json.dumps(SAMPLE_DEMO)});
community.count = community.tools.length;
globalThis.fetch = async path => ({{
  ok: true, json: async () => path === "registry.json" ? registry : community
}});
""",
        """
await exportRappWorkspace();
await new Promise(resolve => setTimeout(resolve, 1));
console.log(JSON.stringify({bundle: JSON.parse(await blobs[0].text()), errors}));
""",
    )
    tools = result["bundle"]["community_tools"]["tools"]
    assert result["errors"] == []
    assert all(t.get("kind", "tool") == "tool" for t in tools)
    assert result["bundle"]["community_tools"]["count"] == len(tools)


# ------------------------------------------- links a browser would reject
@pytest.mark.parametrize("url", [
    "https://example.com:99999/x",
    "https://example.com:abc/x",
    "https://example.com:-1/x",
    "https://exa mple.com/x",
    "https://example.com/a b",
    "https://exa_mple..com/x",
    "https://:443/x",
])
def test_one_pager_links_a_browser_would_reject_are_flagged(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    assert "The one-pager link must be a public https link." in problems, problems


@pytest.mark.parametrize("url", [
    "https://example.com/one-pager.pdf",
    "https://example.com:8443/x",
    "https://docs.example.org/a/b?c=d#e",
])
def test_good_one_pager_links_still_pass(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    assert problems == [], problems


@pytest.mark.parametrize("url", [
    "https://www.youtube.com:99999/watch?v=9A8k0z77NFo",
    "https://www.youtube.com:abc/watch?v=x",
])
def test_video_link_with_a_bad_port_gets_a_friendly_problem(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(video=url)))
    assert "The video link is not a valid URL." in problems, problems


def test_check_cli_answers_a_video_link_with_a_bad_port(tmp_path):
    body = tmp_path / "body.md"
    body.write_text(
        filled_body(video="https://www.youtube.com:99999/watch?v=9A8k0z77NFo"), encoding="utf-8"
    )
    result, comment = tmp_path / "r.json", tmp_path / "c.md"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "demo_submission.py"), "check", "--offline",
         "--body-file", str(body), "--result", str(result), "--comment", str(comment)],
        check=True, capture_output=True,
    )
    assert json.loads(result.read_text())["ok"] is False
    assert "not a valid URL" in comment.read_text()


# --------------------------------------------- other vendors' AI products
@pytest.mark.parametrize("field, text", [
    ("description", "We rebuilt our ChatGPT prototype in Copilot Studio. It drafts replies."),
    ("description", "It replaces a Gemini workflow. It drafts replies."),
    ("description", "Built on GPT-4 first. It drafts replies."),
    ("team", "OpenAI Partner Team"),
    ("title", "Claude reply drafter"),
])
def test_other_vendors_ai_product_names_are_flagged(field, text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(**{field: text})))
    assert _vendor_problem(problems), problems


def test_the_other_vendors_problem_never_repeats_the_names():
    """The comment is public, so it says what to fix without naming anyone."""
    message = ds.OTHER_AI_PRODUCTS_PROBLEM.lower()
    for term in ds.OTHER_AI_PRODUCT_TERMS:
        assert not re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", message), term
    _, problems = ds.validate(ds.parse_issue_form(
        filled_body(description="It replaces a Gemini workflow. It drafts replies.")
    ))
    assert not any("gemini" in p.lower() for p in problems), problems


def test_microsoft_product_names_are_not_flagged():
    _, problems = ds.validate(ds.parse_issue_form(filled_body(
        description="Copilot Studio drafts the reply. Microsoft 365 Copilot summarises it in Teams."
    )))
    assert problems == [], problems


# --------------------------------------- one bad card never takes the page
def test_one_bad_entry_is_skipped_and_the_rest_of_the_page_renders():
    result = run_community_tools_node(
        f"""
community.tools.push({json.dumps({**SAMPLE_DEMO, "id": "bad-port", "onepager": "https://example.com:99999/x"})});
community.tools.push({json.dumps({**SAMPLE_DEMO, "id": "bad-thumb", "thumbnail": "https://example.com:99999/t.jpg"})});
community.tools.push({json.dumps({**SAMPLE_DEMO, "id": "bad-url", "url": "https://www.youtube.com:99999/watch?v=x"})});
community.tools.push({json.dumps({**SAMPLE_DEMO, "id": "good-one"})});
community.count = community.tools.length;
globalThis.fetch = async () => ({{ok: true, json: async () => community}});
""",
        """
await renderCommunityTools();
console.log(JSON.stringify({
  demos: $("demo-grid").innerHTML, tools: $("community-grid").innerHTML, errors
}));
""",
    )
    assert result["errors"] == []
    assert "unavailable" not in result["demos"]
    assert "unavailable" not in result["tools"]
    assert 'data-demo-id="good-one"' in result["demos"]
    # A bad one-pager or thumbnail only drops that link; a bad video link drops the card.
    assert 'data-demo-id="bad-port"' in result["demos"]
    assert "99999" not in result["demos"]
    assert 'data-demo-id="bad-url"' not in result["demos"]
    assert result["demos"].count('class="demo-card"') == len(DEMOS) + 3
    assert result["tools"].count('class="community-card"') == len(
        [t for t in MANIFEST["tools"] if t.get("kind") != "demo"]
    )


# ------------------------------------- the bot's demo PR gets the page test
def test_approve_job_runs_the_page_tests_before_opening_the_pull_request():
    yaml = pytest.importorskip("yaml")
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["approve"]["steps"]
    names = [s.get("name", "") for s in steps]
    test_step = next(i for i, s in enumerate(steps) if "tests/test_community_agents.py" in s.get("run", ""))
    pr_step = names.index("Push a branch and open a pull request")
    assert test_step < pr_step
    assert any(s.get("uses", "").startswith("actions/setup-node@") for s in steps[:test_step])
    report = next(s for s in steps if s.get("name") == "Report a failed page check")
    assert "failure()" in report["if"]
    assert "--remove-label \"demo: approved\"" in report["run"]


# ------------------------------- names that are joined, versioned or full-width
@pytest.mark.parametrize("field, text", [
    ("description", "Built like a GPT4 helper. The agent drafts the summary."),
    ("description", "It started as a Claude3 prototype. The agent drafts the summary."),
    ("description", "Uses AzureOpenAI under the hood. The agent drafts the summary."),
    ("description", "Uses azureopenai under the hood. The agent drafts the summary."),
    ("description", "Replaces Salesforce Agentforce. The agent drafts the summary."),
    ("description", "Replaces Google Vertex AI. The agent drafts the summary."),
    ("description", "Moved off Amazon Bedrock. The agent drafts the summary."),
    ("description", "Moved off IBM watsonx. The agent drafts the summary."),
    ("title", "\uff23\uff48\uff41\uff54\uff27\uff30\uff34 Helper"),
    ("title", "Chat\u200bGPT Helper"),
])
def test_joined_versioned_and_full_width_vendor_names_are_flagged(field, text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(**{field: text})))
    assert _vendor_problem(problems), problems


@pytest.mark.parametrize("text", [
    "Uses AzureOpenAI under the hood. The agent drafts the summary.",
    "Runs on AzureFunctions. The agent drafts the summary.",
    "Runs on \uff21\uff5a\uff55\uff52\uff45 Functions. The agent drafts the summary.",
    "Hosted in Azure2 regions. The agent drafts the summary.",
])
def test_joined_and_full_width_azure_is_flagged(text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(description=text)))
    assert any("azure" in p for p in problems if p.startswith("Remove these words")), problems


def test_a_full_width_title_keeps_all_its_words_in_the_web_address():
    assert ds.slugify("\uff34\uff49\uff45\uff52\uff45\uff44 Huddle Board") == "tiered-huddle-board"


@pytest.mark.parametrize("text", [
    "Copilot Studio drafts the reply. Microsoft 365 Copilot summarises it in Teams.",
    "Power Automate routes the request. Dynamics 365 and SharePoint keep the record.",
    "PowerApps and Dataverse hold the plan. The bedrock of the process is one Teams channel.",
    "The agenda covers standard tasks. It handles grading and abandoned carts.",
])
def test_microsoft_names_and_ordinary_words_still_pass(text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(description=text)))
    assert problems == [], problems


def test_the_problem_text_names_none_of_the_added_platforms():
    message = ds.OTHER_AI_PRODUCTS_PROBLEM
    assert ds.other_ai_products_in(message) is False
    _, problems = ds.validate(ds.parse_issue_form(
        filled_body(description="Replaces Salesforce Agentforce. The agent drafts the summary.")
    ))
    assert not any("agentforce" in p.lower() for p in problems), problems


# ------------------------------------------------------ the one-pager link
@pytest.mark.parametrize("url", [
    "https://chatgpt.com/share/abc",
    "https://example.com/our-gpt4-onepager.pdf",
])
def test_one_pager_link_is_checked_for_other_vendors_names(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    assert _vendor_problem(problems), problems


@pytest.mark.parametrize("url", [
    "https://example.com/files/confidential-onepager.pdf",
    "https://example.com/files/internal%20only/onepager.pdf",
])
def test_one_pager_link_is_checked_for_forbidden_words(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    assert any(p.startswith("Remove these words") for p in problems), problems


@pytest.mark.parametrize("url", [
    "https://microsoft.sharepoint.com/teams/x/Shared%20Documents/onepager.pdf",
    "https://contoso-my.sharepoint.com/:b:/p/someone/EabcXYZ",
    "https://SAMPLE.SharePoint.com/sites/demo/onepager.pdf",
    "https://teams.microsoft.com/l/file/abc",
    "https://loop.cloud.microsoft/p/abc",
    "https://sample.crm.dynamics.com/main.aspx",
])
def test_one_pager_on_a_sign_in_only_host_is_rejected(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    assert ds.ONEPAGER_SIGN_IN_PROBLEM in problems, problems
    assert not any("sharepoint" in p.lower() or "contoso" in p.lower() or "sample" in p.lower()
                   for p in problems), problems


# ------------------------------------------------ one video, not a playlist
@pytest.mark.parametrize("url", [
    "https://www.youtube.com/playlist?list=PLsample0000000000000000000000000",
    "https://www.youtube.com/@SampleChannel",
    "https://www.youtube.com/channel/UCsample000000000000000",
    "https://www.youtube.com/",
    "https://www.youtube.com/watch",
    "https://www.youtube.com/watch?list=PLsample0000000000000000000000000",
    "https://youtu.be/",
    "https://youtu.be/9A8k0z77NFo/extra",
])
def test_video_link_must_point_at_one_video(url):
    with pytest.raises(ds.SubmissionError, match="one video"):
        ds.classify_video_url(url)
    _, problems = ds.validate(ds.parse_issue_form(filled_body(video=url)))
    assert any("one video" in p for p in problems), problems


@pytest.mark.parametrize("url", [
    "https://www.youtube.com/watch?v=9A8k0z77NFo",
    "https://www.youtube.com/watch?v=9A8k0z77NFo&list=PLsample0000000000000000000000000",
    "https://m.youtube.com/watch?v=9A8k0z77NFo&t=30s",
    "https://youtu.be/9A8k0z77NFo",
    "https://youtu.be/9A8k0z77NFo?t=12",
    "https://www.youtube.com/shorts/9A8k0z77NFo",
    "https://www.youtube.com/embed/9A8k0z77NFo",
    "https://www.youtube.com/live/9A8k0z77NFo",
])
def test_single_video_links_still_pass(url):
    assert ds.classify_video_url(url) == "youtube"


# ------------------------------------- a retitled graduate keeps its library link
def test_a_retitled_reapproval_keeps_its_graduation():
    manifest = {"schema": ds.MANIFEST_SCHEMA, "tools": []}
    original = {**SAMPLE_DEMO, "submission_issue": 335, "graduated_to": "tiered-huddle-board"}
    manifest["tools"].append(dict(original))
    retitled = {**SAMPLE_DEMO, "id": "sample-community-demo-v2", "name": "Sample Community Demo v2"}
    retitled.pop("submission_issue")
    ds.apply_entry(manifest, retitled, 335, "2026-10-30")
    demos = [t for t in manifest["tools"] if t.get("kind") == "demo"]
    assert [(d["id"], d.get("graduated_to")) for d in demos] == [
        ("sample-community-demo-v2", "tiered-huddle-board")
    ]
    assert all("_drop" not in t for t in manifest["tools"])


def test_a_new_issue_never_inherits_another_demos_graduation():
    manifest = {"schema": ds.MANIFEST_SCHEMA, "tools": [
        {**SAMPLE_DEMO, "submission_issue": 335, "graduated_to": "tiered-huddle-board"}
    ]}
    other = {**SAMPLE_DEMO, "id": "another-demo", "name": "Another Demo"}
    ds.apply_entry(manifest, other, 400, "2026-10-30")
    by_id = {t["id"]: t for t in manifest["tools"]}
    assert "graduated_to" not in by_id["another-demo"]
    assert by_id["sample-community-demo"]["graduated_to"] == "tiered-huddle-board"


def test_ordinary_sentences_with_platform_words_still_pass():
    _, problems = ds.validate(ds.parse_issue_form(filled_body(
        description="The agent can now assist managers. Amazon queue times are not involved."
    )))
    assert problems == [], problems


def test_the_form_explains_the_one_video_and_no_sign_in_rules():
    form = FORM.read_text(encoding="utf-8")
    assert "one video (not a playlist or channel)" in form
    assert "must open without a sign-in" in form


# ------------------------------------- round 4: playlists, sentence breaks, link ids
def _vendor_problem(problems):
    return next((p for p in problems if p.startswith(ds.OTHER_AI_PRODUCTS_PROBLEM)), None)


@pytest.mark.parametrize("url", [
    "https://www.youtube.com/embed/videoseries?list=PLsample0000000000000000000000000",
    "https://www.youtube.com/embed/VideoSeries?list=PLsample0000000000000000000000000",
    "https://www.youtube.com/embed/videoseries",
    "https://www.youtube.com/shorts/videoseries",
    "https://youtu.be/videoseries?list=PLsample0000000000000000000000000",
    "https://www.youtube.com/watch?v=videoseries&list=PLsample0000000000000000000000000",
])
def test_an_embedded_playlist_is_not_one_video(url):
    with pytest.raises(ds.SubmissionError, match="one video"):
        ds.classify_video_url(url)


@pytest.mark.parametrize("url", [
    "https://www.youtube.com/embed/9A8k0z77NFo?list=PLsample0000000000000000000000000",
    "https://youtu.be/9A8k0z77NFo?list=PLsample0000000000000000000000000",
])
def test_a_real_video_inside_a_playlist_still_passes(url):
    assert ds.classify_video_url(url) == "youtube"


@pytest.mark.parametrize("field, text", [
    ("description", "Sellers list on Amazon. Q4 returns spike and the agent triages them."),
    ("description", "Stores order from Amazon, Q3 forecasts guide stock. The agent helps."),
    ("description", "Stores order from Amazon; Q3 forecasts guide stock. The agent helps."),
    ("description", "Sales on Amazon Q4 were strong. The agent forecasts the next quarter."),
    ("description", "Planners face perplexity over shift rules. The agent explains them."),
    ("description", "The town bard wrote the anthem. The agent books the hall."),
    ("title", "Retail Returns Triage"),
])
def test_ordinary_retail_words_and_english_words_pass(field, text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(**{field: text})))
    assert problems == [], problems


def test_words_in_different_fields_never_join_into_a_name():
    _, problems = ds.validate(ds.parse_issue_form(filled_body(
        title="Store Ops Amazon",
        description="Q forecasts guide stock. The agent helps.",
    )))
    assert _vendor_problem(problems) is None, problems


@pytest.mark.parametrize("field, text", [
    ("description", "It replaces Amazon Q in the store. The agent drafts replies."),
    ("description", "It replaces Amazon-Q. The agent drafts replies."),
    ("description", "It started on Perplexity AI. The agent drafts replies."),
    ("description", "It started on GPT4. The agent drafts replies."),
    ("title", "Mistral Wind Farm Ops"),
    ("team", "Gemini Squad"),
])
def test_listed_vendor_names_are_still_flagged(field, text):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(**{field: text})))
    assert _vendor_problem(problems), problems


@pytest.mark.parametrize("overrides, named, not_named", [
    ({"title": "Gemini Reply Drafter"}, ["the title"], ["the description", "the team", "the one-pager"]),
    ({"description": "It replaces a Gemini workflow. It drafts replies."}, ["the description"],
     ["the title", "the team", "the one-pager"]),
    ({"team": "Gemini Squad"}, ["the team"], ["the title", "the description", "the one-pager"]),
    ({"onepager": "https://example.com/gemini-onepager.pdf"}, ["the one-pager link"],
     ["the title", "the description", "the team"]),
    ({"title": "Gemini Reply Drafter", "team": "Mistral Squad"}, ["the title", "the team"],
     ["the description", "the one-pager"]),
])
def test_the_vendor_problem_says_which_field_without_the_name(overrides, named, not_named):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(**overrides)))
    message = _vendor_problem(problems)
    assert message, problems
    for field in named:
        assert field in message, message
    for field in not_named:
        assert field not in message, message
    assert not ds.other_ai_products_in(message), message
    assert "gemini" not in message.lower() and "mistral" not in message.lower()


@pytest.mark.parametrize("url", [
    "https://contoso.github.io/doc?id=AbNDA9xQ",
    "https://example.com/files/1aGPT3kz.pdf",
    "https://example.com/d/AbNDA9xQ/view",
    "https://example.com/view?file=confidential-gpt4.pdf",
    "https://example.com/onepager.pdf#azure",
])
def test_one_pager_ids_and_query_values_are_not_scanned_for_words(url):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    assert problems == [], problems


@pytest.mark.parametrize("url, kind", [
    ("https://example.com/files/confidential-onepager.pdf", "words"),
    ("https://example.com/files/internal%20only/onepager.pdf", "words"),
    ("https://azure-demo.example.com/onepager.pdf", "words"),
    ("https://example.com/azureopenai-onepager.pdf", "words"),
    ("https://chatgpt.com/share/abc", "vendor"),
    ("https://example.com/our-gpt4-onepager.pdf", "vendor"),
])
def test_one_pager_host_and_path_words_are_still_checked(url, kind):
    _, problems = ds.validate(ds.parse_issue_form(filled_body(onepager=url)))
    if kind == "words":
        assert any(p.startswith("Remove these words") for p in problems), problems
    else:
        assert _vendor_problem(problems), problems
