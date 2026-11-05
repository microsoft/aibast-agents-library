"""Every published page carries one identical Microsoft Clarity tag."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import apply_clarity_tag as cli  # noqa: E402

from tools import clarity_tag as clarity  # noqa: E402

BLOCK_RE = re.compile(
    re.escape(clarity.START_MARK) + r"(.*?)" + re.escape(clarity.END_MARK), re.DOTALL
)


def blocks(path):
    return BLOCK_RE.findall(path.read_text(encoding="utf-8"))


def test_config_names_a_valid_or_empty_project_id():
    config = json.loads((ROOT / "clarity.json").read_text(encoding="utf-8"))
    assert config["provider"] == "Microsoft Clarity"
    assert config["site"] == "https://microsoft.github.io/aibast-agents-library"
    project_id = config["project_id"]
    assert project_id == "" or clarity.PROJECT_ID_RE.match(project_id)


def test_every_public_page_carries_the_current_tag_once():
    pages = clarity.public_pages(ROOT)
    assert len(pages) > 200
    expected = clarity.render_tag(clarity.load_config()["project_id"])
    expected_body = BLOCK_RE.search(expected).group(1)
    for page in pages:
        found = blocks(page)
        assert found == [expected_body], page.relative_to(ROOT)
        html = page.read_text(encoding="utf-8")
        head_end = html.lower().index("</head>")
        assert html.index(clarity.START_MARK) < head_end, page.relative_to(ROOT)


def test_landing_catalog_metrics_and_solution_pages_are_covered():
    for relative in (
        "index.html",
        "library.html",
        "metrics.html",
        "docs/rapp-guide.html",
        "reports/impact-report.html",
        "solutions/ask-hr/quest.html",
    ):
        assert len(blocks(ROOT / relative)) == 1, relative


def test_installed_software_and_local_tools_are_never_tagged():
    for relative in (
        "rapp_brainstem/index.html",
        "rapp_ai/index.html",
        "beta/index.html",
        "beta/ui/index.html",
    ):
        path = ROOT / relative
        if path.exists():
            assert blocks(path) == [], relative
    for path in ROOT.glob("tools/*.html"):
        assert blocks(path) == [], path.relative_to(ROOT)


def test_check_mode_passes_on_the_committed_tree():
    assert cli.main(["--check"]) == 0


def test_stamp_is_idempotent_and_replaces_stale_ids():
    old = clarity.render_tag("oldid12345")
    new = clarity.render_tag("newid12345")
    page = "<html><head><title>x</title>\n</head><body></body></html>"
    once = clarity.stamp(page, old)
    assert once.count(clarity.START_MARK) == 1
    assert clarity.stamp(once, old) == once
    swapped = clarity.stamp(once, new)
    assert swapped.count(clarity.START_MARK) == 1
    assert "oldid12345" not in swapped and 'data-clarity-project="newid12345"' in swapped
    with pytest.raises(ValueError):
        clarity.stamp("<html><body></body></html>", new)


def test_check_mode_flags_a_stale_page(tmp_path):
    (tmp_path / "clarity.json").write_text(json.dumps({"project_id": "abc1234567"}))
    (tmp_path / "index.html").write_text("<html><head></head><body></body></html>")
    assert cli.main(["--check", "--root", str(tmp_path)]) == 1
    assert cli.main(["--root", str(tmp_path)]) == 0
    assert cli.main(["--check", "--root", str(tmp_path)]) == 0
    assert 'data-clarity-project="abc1234567"' in (tmp_path / "index.html").read_text()


def test_rejects_a_malformed_project_id(tmp_path):
    (tmp_path / "clarity.json").write_text(json.dumps({"project_id": "not a real id!"}))
    (tmp_path / "index.html").write_text("<html><head></head><body></body></html>")
    assert cli.main(["--check", "--root", str(tmp_path)]) == 1


def loader_script():
    body = BLOCK_RE.search(clarity.render_tag("abc1234567")).group(1)
    return re.search(r"<script[^>]*>(.*?)</script>", body, re.DOTALL).group(1)


FAKE_DOM = r"""
function run(hostname, nav, stored, opts) {
  opts = opts || {};
  const store = {};
  if (stored) store[%(key)s] = stored;
  const inserted = [];
  const created = [];
  function element(tag) {
    const e = { tagName: tag, style: {}, children: [], attrs: {}, removed: false,
      appendChild(c) { this.children.push(c); return c; },
      setAttribute(k, v) { this.attrs[k] = v; },
      remove() { this.removed = true; } };
    created.push(e);
    return e;
  }
  const body = element("body");
  const first = { parentNode: { insertBefore: (el) => inserted.push(el.src) } };
  const document = {
    location: { hostname },
    body: opts.noBody ? null : body,
    listeners: {},
    createElement: element,
    getElementById: (id) => created.find((e) => e.id === id && !e.removed) || null,
    getElementsByTagName: () => [first],
    addEventListener(name, fn) { this.listeners[name] = fn; },
  };
  const window = { navigator: nav, doNotTrack: opts.winDnt,
    localStorage: { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = v; } } };
  (function (window, document) { %(script)s })(window, document);
  const bar = created.find((e) => e.id === %(key)s);
  const buttons = bar ? bar.children.filter((c) => c.tagName === "button") : [];
  return {
    inserted, store, barShown: !!bar && !bar.removed, deferred: !!document.listeners.DOMContentLoaded,
    bodyChildren: body.children.length, buttons: buttons.map((b) => b.textContent),
    click(label) { buttons.find((b) => b.textContent === label).onclick(); return this; },
    get clarityQueue() { return window.clarity && window.clarity.q ? window.clarity.q.map((a) => a[0]) : null; },
    get consentArgs() { return window.clarity && window.clarity.q ? window.clarity.q.map((a) => a[1]) : null; },
    get barRemoved() { return !!bar && bar.removed; },
    fire() { document.listeners.DOMContentLoaded(); return this; },
  };
}
"""


def run_loader(cases):
    harness = FAKE_DOM % {
        "key": json.dumps(clarity.CONSENT_STORAGE_KEY),
        "script": loader_script(),
    }
    harness += "const out = {};\n" + cases + "\nconsole.log(JSON.stringify(out));\n"
    result = subprocess.run(["node"], input=harness, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


TAG_URL = "https://www.clarity.ms/tag/abc1234567"


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_loader_waits_for_consent_and_remembers_the_choice():
    out = run_loader("""
const fresh = run("microsoft.github.io", {}, null);
out.fresh = { inserted: fresh.inserted, barShown: fresh.barShown, buttons: fresh.buttons, bodyChildren: fresh.bodyChildren };
const accepted = run("microsoft.github.io", {}, null).click("Accept");
out.accepted = { inserted: accepted.inserted, store: accepted.store, barRemoved: accepted.barRemoved, queue: accepted.clarityQueue, consent: accepted.consentArgs };
const declined = run("microsoft.github.io", {}, null).click("Decline");
out.declined = { inserted: declined.inserted, store: declined.store, barRemoved: declined.barRemoved };
const returning = run("kody-w.github.io", {}, "granted");
out.returning = { inserted: returning.inserted, barShown: returning.barShown };
const refused = run("microsoft.github.io", {}, "denied");
out.refused = { inserted: refused.inserted, barShown: refused.barShown };
const early = run("microsoft.github.io", {}, null, { noBody: true });
out.early = { deferred: early.deferred, barShown: early.barShown };
""")
    assert out["fresh"] == {"inserted": [], "barShown": True, "buttons": ["Accept", "Decline"], "bodyChildren": 1}
    assert out["accepted"] == {
        "inserted": [TAG_URL],
        "store": {clarity.CONSENT_STORAGE_KEY: "granted"},
        "barRemoved": True,
        "queue": ["consentv2"],
        "consent": [{"ad_Storage": "denied", "analytics_Storage": "granted"}],
    }
    assert out["declined"] == {"inserted": [], "store": {clarity.CONSENT_STORAGE_KEY: "denied"}, "barRemoved": True}
    assert out["returning"] == {"inserted": [TAG_URL], "barShown": False}
    assert out["refused"] == {"inserted": [], "barShown": False}
    assert out["early"] == {"deferred": True, "barShown": False}


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js required")
def test_loader_stays_silent_off_github_pages_and_under_privacy_signals():
    out = run_loader("""
for (const [name, host, nav, dnt] of [
  ["local", "localhost", {}, undefined],
  ["file", "", {}, undefined],
  ["gpc", "microsoft.github.io", { globalPrivacyControl: true }, undefined],
  ["dnt", "microsoft.github.io", { doNotTrack: "1" }, undefined],
  ["winDnt", "microsoft.github.io", {}, "1"],
]) {
  const r = run(host, nav, "granted", { winDnt: dnt });
  out[name] = { inserted: r.inserted, barShown: r.barShown };
}
""")
    for key, value in out.items():
        assert value == {"inserted": [], "barShown": False}, key


def test_banner_links_the_microsoft_privacy_statement():
    tag = clarity.render_tag("abc1234567")
    assert clarity.PRIVACY_STATEMENT_URL in tag
    assert "Microsoft Privacy Statement" in tag
    assert 'rel = "noopener"' in tag


def test_strip_tag_removes_the_block_and_nothing_else():
    page = "<html><head><title>x</title>\n</head><body>hi</body></html>"
    stamped = clarity.stamp(page, clarity.render_tag("abc1234567"))
    assert clarity.strip_tag(stamped) == page
    assert clarity.strip_tag_bytes(stamped.encode()) == page.encode()
    assert clarity.strip_tag(page) == page


def test_solution_bundles_ship_pages_without_the_tag(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "build_solution_export", ROOT / "tools" / "build_solution_export.py"
    )
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    builder.ROOT = tmp_path
    package = tmp_path / "solutions" / "demo"
    (package / "exports").mkdir(parents=True)
    page = "<html><head><title>x</title>\n</head><body>demo</body></html>"
    (package / "quest.html").write_text(clarity.stamp(page, clarity.render_tag("abc1234567")), encoding="utf-8")
    (package / "source.py").write_text("print('hi')\n", encoding="utf-8")
    manifest = package / "export-manifest.json"
    manifest.write_text(json.dumps({"bundle": {"path": "solutions/demo/exports/demo-source.zip"}, "files": []}))
    bundle, _ = builder.build(manifest)
    from zipfile import ZipFile

    with ZipFile(bundle) as archive:
        assert archive.read("solutions/demo/quest.html").decode() == page
        assert archive.read("solutions/demo/source.py") == b"print('hi')\n"
    stamped = (package / "quest.html").read_bytes()
    assert builder.CLARITY_BLOCK_RE.sub(b"", stamped) == clarity.strip_tag_bytes(stamped) == page.encode()


def test_rollout_audit_ignores_the_tag_but_still_catches_real_drift(tmp_path):
    pytest.importorskip("bs4")
    from tests.test_workshop_course_rollout import audit_fixture, create_fixture

    package = create_fixture(tmp_path)
    quest = package / "quest.html"
    quest.write_text(
        clarity.stamp(quest.read_text(encoding="utf-8"), clarity.render_tag("abc1234567")),
        encoding="utf-8",
    )
    result = audit_fixture(tmp_path)
    assert not [f for f in result["failures"] if "stale bytes" in f], result["failures"]

    (package / "source.py").write_text("print('changed')\n", encoding="utf-8")
    result = audit_fixture(tmp_path)
    assert any("stale bytes" in f and "source.py" in f for f in result["failures"])


def test_academy_gate_ignores_only_the_sanctioned_clarity_block():
    audit_academy = pytest.importorskip("tools.audit_academy")  # Academy ships on staging first

    tag = clarity.render_tag("abc1234567")
    page = clarity.stamp("<html><head></head><body></body></html>", tag)
    assert audit_academy.ANALYTICS_RE.search(tag)  # the raw block would trip it
    assert audit_academy.ANALYTICS_RE.search(clarity.strip_tag(page)) is None
    assert audit_academy.ANALYTICS_RE.search(clarity.strip_tag(page + "<script>gtag('js')</script>"))


def test_banner_uses_system_colors_not_literals():
    script = loader_script()
    assert re.search(r"#[0-9a-fA-F]{3,8}\b|(?:rgb|rgba|hsl|hsla)\s*\(", script) is None
    for keyword in ("Canvas", "CanvasText", "AccentColor", "LinkText"):
        assert keyword in script
