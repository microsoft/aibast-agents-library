import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from tests.test_library_agent_upvotes import run_library_node


ROOT = Path(__file__).resolve().parents[1]
COMMUNITY = json.loads((ROOT / "community_tools.json").read_text(encoding="utf-8"))
REGISTRY = {"agents": [{"name": "example"}], "stacks": [], "partners": [{"id": "owner"}]}
HARNESS = """
const nodes = new Map();
document.getElementById = id => {
  if (!nodes.has(id)) nodes.set(id, {textContent: "", innerHTML: "", disabled: false});
  return nodes.get(id);
};
location.href = "https://kody-w.github.io/aibast-agents-library/index.html?view=partners";
const downloads = [];
const blobs = [];
const revoked = [];
document.body = {appendChild() {}};
document.createElement = () => ({
  click() { downloads.push({href: this.href, name: this.download}); },
  remove() {}
});
URL.createObjectURL = blob => { blobs.push(blob); return "blob:catalog"; };
URL.revokeObjectURL = url => revoked.push(url);
const errors = [];
console.error = (...args) => errors.push(args.map(String).join(" "));
"""


def probe(setup, action):
    return run_library_node(
        HARNESS
        + f"\nconst community = {json.dumps(COMMUNITY)};"
        + f"\nconst registry = {json.dumps(REGISTRY)};"
        + "\n"
        + setup
        + "\n(async () => {\n"
        + action
        + "\n})().catch(error => { process.stderr.write(String(error)); process.exitCode = 1; });"
    )


def run_community_tools_node(setup, action):
    """Same node harness as `probe`, but running community-tools.html's own
    script instead of index.html's — renderCommunityTools() lives there now."""
    assert shutil.which("node"), "Node.js is required to validate community-tools scripts"
    text = (ROOT / "community-tools.html").read_text(encoding="utf-8")
    scripts = re.findall(r"<script\b[^>]*>(.*?)</script>", text, re.DOTALL)
    assert scripts
    script = scripts[-1]
    script = re.sub(r"\nrenderCommunityTools\(\);\s*$", "\n", script)
    base = """
globalThis.document = {};
globalThis.window = {};
globalThis.location = {
  hash: "",
  search: "",
  pathname: "/community-tools.html",
  hostname: "kody-w.github.io"
};
globalThis.localStorage = { getItem() { return null; } };
globalThis.navigator = {};
"""
    payload = (
        base
        + HARNESS
        + f"\nconst community = {json.dumps(COMMUNITY)};"
        + "\n"
        + setup
        + "\n"
        + script
        + "\n(async () => {\n"
        + action
        + "\n})().catch(error => { process.stderr.write(String(error)); process.exitCode = 1; });"
    )
    result = subprocess.run(
        ["node"], input=payload, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_catalog_preserves_community_credits_and_honest_snapshot_controls():
    page = BeautifulSoup((ROOT / "index.html").read_text(encoding="utf-8"), "html.parser")
    community_page = BeautifulSoup(
        (ROOT / "community-tools.html").read_text(encoding="utf-8"), "html.parser"
    )
    assert community_page.select_one("#community-grid")
    assert community_page.select_one("#community-note")
    assert page.select_one('a[href="community-tools.html"]')
    assert page.select_one('[data-action="export-workspace"]')["type"] == "button"
    assert page.select_one("#export-status")["role"] == "status"
    text = page.select_one(".export-workspace").get_text(" ", strip=True)
    assert "not an executable agent or an importable Brainstem workspace" in text
    assert COMMUNITY["count"] == len(COMMUNITY["tools"])


def test_community_cards_render_all_sources_and_escape_content():
    result = run_community_tools_node(
        """
community.tools[0].name = '<img src=x onerror="alert(1)">';
globalThis.fetch = async () => ({ok: true, json: async () => community});
""",
        """
await renderCommunityTools();
console.log(JSON.stringify({
  html: $("community-grid").innerHTML,
  note: $("community-note").textContent,
  errors
}));
""",
    )
    assert result["html"].count('class="community-card"') == COMMUNITY["count"]
    assert "<img" not in result["html"]
    assert "&lt;img" in result["html"]
    assert result["note"] == COMMUNITY["note"]
    assert result["errors"] == []
    for tool in COMMUNITY["tools"]:
        assert tool["url"] in result["html"]


def test_export_downloads_the_complete_snapshot_with_staging_install_links():
    result = probe(
        """
globalThis.fetch = async path => ({
  ok: true, json: async () => path === "registry.json" ? registry : community
});
""",
        """
await exportRappWorkspace();
await new Promise(resolve => setTimeout(resolve, 1));
console.log(JSON.stringify({
  bundle: JSON.parse(await blobs[0].text()),
  downloads, revoked, errors,
  disabled: $("export-workspace-btn").disabled,
  status: $("export-status").textContent
}));
""",
    )
    bundle = result["bundle"]
    assert bundle["schema"] == "aibast-rapp-workspace-export/1.0"
    assert bundle["purpose"] == "catalog_snapshot"
    assert bundle["library"] == REGISTRY
    assert bundle["community_tools"] == COMMUNITY
    assert bundle["source"] == "https://kody-w.github.io/aibast-agents-library/"
    assert "kody-w.github.io/aibast-agents-library/install.sh" in bundle["install"]["brainstem"]
    assert "kody-w.github.io/aibast-agents-library/install.ps1" in bundle["install"]["brainstem_windows"]
    assert bundle["install"]["guide"].endswith("/docs/installer.html")
    assert "not loaded from AGENTS_PATH" in bundle["usage"]
    assert len(result["downloads"]) == 1
    assert re.fullmatch(r"rapp-catalog-\d{4}-\d{2}-\d{2}\.json", result["downloads"][0]["name"])
    assert result["revoked"] == ["blob:catalog"]
    assert result["errors"] == []
    assert result["disabled"] is False
    assert "reference data" in result["status"]


@pytest.mark.parametrize("failure", ["http", "network", "invalid-json", "invalid-registry", "invalid-tools", "unsafe-url"])
def test_failed_export_never_downloads_a_partial_or_invalid_snapshot(failure):
    result = probe(
        f"""
const failure = {json.dumps(failure)};
globalThis.fetch = async path => {{
  if (failure === "network") throw new Error("Connection lost");
  if (failure === "http") return {{ok: false, status: 503}};
  if (failure === "invalid-tools") community.count = -1;
  if (failure === "unsafe-url") community.tools[0].url = "javascript:alert(1)";
  return {{
    ok: true,
    json: async () => {{
      if (failure === "invalid-json") throw new SyntaxError("Invalid JSON");
      return path === "registry.json"
        ? (failure === "invalid-registry" ? {{}} : registry) : community;
    }}
  }};
}};
""",
        """
await exportRappWorkspace();
console.log(JSON.stringify({
  downloads, errors,
  disabled: $("export-workspace-btn").disabled,
  status: $("export-status").textContent
}));
""",
    )
    assert result["downloads"] == []
    assert result["errors"]
    assert result["disabled"] is False
    assert result["status"].startswith("Export failed.")


def test_community_fetch_failure_is_visible_without_crashing_the_catalog():
    result = run_community_tools_node(
        'globalThis.fetch = async () => ({ok: false, status: 503});',
        """
await renderCommunityTools();
console.log(JSON.stringify({html: $("community-grid").innerHTML, errors}));
""",
    )
    assert 'role="alert"' in result["html"]
    assert "unavailable" in result["html"]
    assert "HTTP 503" in result["errors"][0]
