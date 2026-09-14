import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BUILD_WORKFLOW = ROOT / ".github/workflows/build-registry.yml"
ASSET_WORKFLOW = ROOT / ".github/workflows/agent-download-assets.yml"
PREFLIGHT_WORKFLOW = ROOT / ".github/workflows/preflight.yml"
BROWSER_PACKAGE = ROOT / "browser-audit/package.json"
ACADEMY_BROWSER_AUDIT = ROOT / "browser-audit/academy-course-audit.mjs"
SKIP_MARKERS = (
    "[skip ci]",
    "[ci skip]",
    "[no ci]",
    "[skip actions]",
    "[actions skip]",
)


def _active_lines(text):
    return "\n".join(
        line
        for line in text.splitlines()
        if not line.lstrip().startswith("#")
    )


def _event_block(text, event):
    match = re.search(
        rf"(?ms)^  {re.escape(event)}:\n(?P<body>.*?)(?=^  [a-z_]+:|"
        r"^permissions:|^concurrency:|^jobs:)",
        text,
    )
    assert match, f"missing {event} trigger"
    return match.group("body")


def _push_paths(text):
    return set(
        re.findall(
            r"^\s+- '([^']+)'\s*$",
            _event_block(text, "push"),
            re.M,
        )
    )


def _step(text, name):
    marker = f"      - name: {name}\n"
    assert marker in text, f"missing step {name!r}"
    remainder = text.split(marker, 1)[1]
    return re.split(
        r"\n      - (?:name:|uses:)",
        remainder,
        maxsplit=1,
    )[0]


def test_build_registry_is_the_only_generated_catalog_writer():
    build = BUILD_WORKFLOW.read_text(encoding="utf-8")
    assets = ASSET_WORKFLOW.read_text(encoding="utf-8")
    active_assets = _active_lines(assets)

    assert "python build_registry.py" in build
    assert "run: python scripts/build_academy.py" in build
    assert "registry-before.json" in build
    assert "registry_path.write_bytes(previous_path.read_bytes())" in build
    assert "python build_registry.py" not in active_assets
    assert "scripts/build_academy.py" not in active_assets
    assert not re.search(
        r"(?m)^\s*git (?:add|commit|push)\b",
        active_assets,
    )


def test_generated_catalogs_are_committed_atomically():
    build = BUILD_WORKFLOW.read_text(encoding="utf-8")
    commit_step = _active_lines(_step(build, "Commit generated catalogs"))

    assert re.findall(r"(?m)^\s*git add\b.*$", commit_step) == [
        "          git add -- registry.json academy.json"
    ]
    assert len(re.findall(r"(?m)^\s*git commit\b", commit_step)) == 1
    assert len(re.findall(r"(?m)^\s*git push\b", commit_step)) == 1
    assert (
        commit_step.index("git add -- registry.json academy.json")
        < commit_step.index(
            'git commit -m "Auto-build generated catalogs"'
        )
        < commit_step.index(
            'git push origin "HEAD:${GITHUB_REF_NAME}"'
        )
    )


def test_catalog_commit_sequences_asset_publication_without_skip_markers():
    build = BUILD_WORKFLOW.read_text(encoding="utf-8")
    assets = ASSET_WORKFLOW.read_text(encoding="utf-8")
    active_build = _active_lines(build).lower()
    active_assets = _active_lines(assets).lower()

    for marker in SKIP_MARKERS:
        assert marker not in active_build
        assert marker not in active_assets

    assert "registry.json" not in _push_paths(build)
    assert "academy.json" not in _push_paths(build)
    assert _push_paths(assets) == {
        "registry.json",
        ".github/workflows/agent-download-assets.yml",
    }
    assert "  workflow_dispatch:" in assets
    assert "  schedule:" in assets
    assert "actions: write" in build
    dispatch_step = _step(build, "Publish committed catalog assets")
    assert "if: steps.catalogs.outputs.changed == 'true'" in dispatch_step
    assert 'workflow_id: "agent-download-assets.yml"' in dispatch_step
    assert build.index("git push origin") < build.index(
        "- name: Publish committed catalog assets"
    )
    assert (
        "branches: [main, easy-mode-copilot-chat-pilot]" in build
    )
    assert (
        "branches: [main, easy-mode-copilot-chat-pilot]" in assets
    )


def test_asset_workflow_consumes_committed_registry_with_integrity_checks():
    assets = ASSET_WORKFLOW.read_text(encoding="utf-8")
    build_step = _active_lines(
        _step(assets, "Build immutable agent assets")
    )

    for token in (
        'Path("registry.json")',
        'agent["_file"]',
        'agent["_sha256"]',
        'agent["_install_filename"]',
        "hashlib.sha256(payload).hexdigest()",
        "shutil.copyfile(source, output / filename)",
    ):
        assert token in build_step
    assert "gh release upload" in assets
    assert 'workflow_id: "metrics.yml"' in assets


def test_browser_certification_includes_the_academy_gate():
    package = json.loads(BROWSER_PACKAGE.read_text(encoding="utf-8"))
    scripts = package["scripts"]

    assert ACADEMY_BROWSER_AUDIT.is_file()
    assert scripts["academy"] == "node academy-course-audit.mjs"
    assert scripts["certify"].split(" && ") == [
        "npm run mutations",
        "npm run audit",
        "npm run academy",
        "npm run attest",
    ]


def test_preflight_runs_the_academy_browser_contract_fail_closed():
    workflow = PREFLIGHT_WORKFLOW.read_text(encoding="utf-8")
    academy_step = _step(workflow, "Academy browser contract")

    assert workflow.index("actions/setup-node@") < workflow.index(
        "- name: Academy browser contract"
    )
    assert "working-directory: browser-audit" in academy_step
    assert "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: '1'" in academy_step
    assert "AIBAST_CHROME_PATH: /usr/bin/google-chrome" in academy_step
    assert (
        "npm install --no-audit --no-fund --ignore-scripts "
        "--no-save --package-lock=false"
    ) in academy_step
    assert "test -f academy-course-audit.mjs" in academy_step
    assert "npm run academy" in academy_step
    assert "continue-on-error" not in academy_step
    assert "|| true" not in academy_step
