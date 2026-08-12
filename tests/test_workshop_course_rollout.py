import importlib.util
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "audit_workshop_course_rollout.py"


def load_module():
    spec = importlib.util.spec_from_file_location("workshop_course_rollout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module()
SLUG = "time-entry-billing"
RAW_BASE = "https://raw.example.invalid/course/"
PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\x0aIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def report_button(location: str) -> str:
    return (
        f'<button class="report-button" data-report-location="{location}" '
        'data-report-expected="Expected" data-report-evidence="">'
        "Report an issue</button>"
    )


def valid_pages() -> dict[str, str]:
    feedback = (
        "<!-- aibast-workshop-feedback:v1 -->"
        "<script>const feedbackSchema = 'aibast-workshop-feedback/1.0';</script>"
    )
    engine = """
    <script>
    const engine = localStorage.getItem("aibast:workshop-engine") === "brainstem"
      ? "brainstem" : "copilot";
    document.documentElement.setAttribute("data-workshop-engine", engine);
    </script>
    """
    reports = "".join(report_button(f"base-{index}") for index in range(7))
    quest = f"""<!doctype html>
<html><head><title>Fixture workshop</title>{engine}<style>body{{color:#222}}</style></head>
<body>
<header>AIBAST guided workshop
<a href="../_shared/workshop-settings.html?return=quest.html">Workshop settings</a>
<a href="field-guide.html">Field guide</a>
<a href="evidence-report.html">Evidence report</a></header>
<main><section class="learn-step" id="workshop-step-1">
<h3>Install RAPP Brainstem Frontier</h3>
<a href="../../beta/">Open Frontier installer</a>
<a href="../../beta/install.cmd" download>Download Windows install.cmd</a>
<a href="../../beta/README.md" download>Download installation guide</a>
{report_button("beta-install")}
</section>
<section data-easy-lane="brainstem">Brainstem lane</section>
<section data-easy-lane="copilot">GitHub Copilot only lane</section>
{reports}
<article class="preview-case">
<button data-copy-target="preview-prompt-case-01">Copy Preview prompt</button>
{report_button("preview-case-01")}
<pre id="preview-prompt-case-01">Run the locked case.</pre>
<img src="screenshots/assisted/annotated/01-case.png" alt="Reusable evidence">
</article>
<section data-path="hard">
<a href="manual-tutorial.html">Standalone manual tutorial</a>
<article class="step"><header>{report_button("native-hard-step-1")}</header>
<img src="screenshots/manual/annotated/01-step.png" alt="Reusable evidence">
<footer><a href="source.py" download>Download source: Agent</a></footer>
</article>
</section>
</main>{feedback}</body></html>"""
    manual = f"""<!doctype html>
<html><head><title>Manual tutorial</title>
<style>body{{color:#222}}</style></head>
<body>AIBAST manual workshop
<article class="step"><header>{report_button("hard-step-1")}</header>
<img src="screenshots/manual/annotated/01-step.png" alt="Reusable evidence">
<footer><a href="source.py" download>Download source: Agent</a></footer>
</article>
{feedback}
<script>
const key = "aibast:time-entry-billing:manual-progress";
const badgeIds = [];
badgeIds.push("hard-mode-complete");
const hardProgress = {{hardComplete: complete}};
</script></body></html>"""
    field = f"""<!doctype html>
<html><head><title>Field guide</title>{engine}<script>
document.documentElement.setAttribute("data-theme", "light");
</script><style>body{{color:#222}}</style></head>
<body>AIBAST field guide
<a href="../_shared/workshop-settings.html">Workshop settings</a>
<a href="quest.html">Back to workshop</a>
<h2>Locked Preview corpus</h2>
<h2>Production replacement seams</h2>
<h2>Evidence gates</h2>
<a href="source.py" download>Download source</a>
</body></html>"""
    evidence = """<!doctype html>
<html><head><title>Evidence report</title>
<script>document.documentElement.setAttribute("data-theme", "light");</script>
<style>body{color:#222}</style></head>
<body>AIBAST evidence report
<div class="summary-grid"><strong>2</strong> Reusable positive checkpoints
<strong>0</strong> Images hidden from learner proof</div>
<h2>Deterministic case contract</h2><section id="locked-cases">CASE-01</section>
<h2>Displayed visual checkpoints</h2>
<h2>Reference-only visual gaps</h2>
<h2>Downloads for audit</h2>
<a href="evals/visual-checkpoints.json" download>Visual contract</a>
<a href="export-manifest.json" download>Manifest</a>
<a href="exports/fixture-solution-source.zip" download>Bundle</a>
<a href="VISUAL-EVIDENCE-AUDIT.md" download>Detailed audit</a>
</body></html>"""
    return {
        "quest.html": quest,
        "manual-tutorial.html": manual,
        "field-guide.html": field,
        "evidence-report.html": evidence,
    }


def build_zip(root: Path, omit: str | None = None) -> None:
    package = root / "solutions" / SLUG
    bundle = package / "exports" / f"{SLUG}-source.zip"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    names = [
        f"solutions/{SLUG}/quest.html",
        f"solutions/{SLUG}/manual-tutorial.html",
        f"solutions/{SLUG}/field-guide.html",
        f"solutions/{SLUG}/evidence-report.html",
        f"solutions/{SLUG}/evals/visual-checkpoints.json",
        f"solutions/{SLUG}/export-manifest.json",
        f"solutions/{SLUG}/source.py",
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    ]
    with ZipFile(bundle, "w", ZIP_DEFLATED) as archive:
        for name in names:
            if name == omit:
                continue
            archive.write(root / name, name)


def create_fixture(root: Path) -> Path:
    package = root / "solutions" / SLUG
    registry = {
        "agents": [
            {
                "name": f"@aibast-agents-library/{SLUG}",
                "_demo": {"slug": SLUG},
                "_solution": {"advertised_name": "Fixture Solution"},
            }
        ]
    }
    write(root / "registry.json", json.dumps(registry))
    write(
        root / "solutions/catalog.json",
        json.dumps(
            {
                "schema": "aibast-solution-copy/1.0",
                "solutions": {
                    f"@aibast-agents-library/{SLUG}": {
                        "display_name": "Fixture Solution"
                    }
                },
            }
        ),
    )
    write(
        root / "tests" / "demo_cases" / f"{SLUG}.json",
        json.dumps({"cases": [{"id": "CASE-01", "prompt": "Run it"}]}),
    )
    write(root / "skills/aibast-easy-mode-copilot/SKILL.md", "Copilot lane")
    write(root / "skills/aibast-easy-mode-brainstem/SKILL.md", "Persistent lane")
    write(root / "solutions/_shared/workshop-settings.html", "settings")
    write(package / "source.py", "print('fixture')\n")
    write(package / "VISUAL-EVIDENCE-AUDIT.md", "# Audit\n")
    for name, page in valid_pages().items():
        write(package / name, page)

    image_paths = (
        "screenshots/assisted/01-case.png",
        "screenshots/assisted/annotated/01-case.png",
        "screenshots/manual/01-step.png",
        "screenshots/manual/annotated/01-step.png",
    )
    for path in image_paths:
        write(package / path, PNG_1X1)
    assisted_film = {
        "schema": "rapp-browserfilm/1.0",
        "width": 1,
        "height": 1,
        "frames": [{"file": "01-case.png", "label": "Pass CASE-01"}],
    }
    manual_film = {
        "schema": "rapp-browserfilm/1.0",
        "width": 1,
        "height": 1,
        "frames": [{"file": "01-step.png", "label": "Create the fixture"}],
    }
    write(
        package / "screenshots/assisted/browserfilm.json",
        json.dumps(assisted_film),
    )
    write(
        package / "screenshots/manual/browserfilm.json",
        json.dumps(manual_film),
    )
    visual = {
        "schema": "aibast-visual-checkpoints/1.0",
        "summary": {
            "total_existing_captures": 2,
            "reusable": 2,
            "reshoot_required": 0,
        },
        "captures": [
            {
                "id": "easy-case-01",
                "mode": "easy",
                "case_id": "CASE-01",
                "source": f"solutions/{SLUG}/screenshots/assisted/01-case.png",
                "annotated": (
                    f"solutions/{SLUG}/screenshots/assisted/annotated/01-case.png"
                ),
                "status": "reusable",
                "visible_anchors": ["CASE-01 passed"],
                "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
            },
            {
                "id": "hard-step-01",
                "mode": "hard",
                "step": 1,
                "source": f"solutions/{SLUG}/screenshots/manual/01-step.png",
                "annotated": (
                    f"solutions/{SLUG}/screenshots/manual/annotated/01-step.png"
                ),
                "status": "reusable",
                "visible_anchors": ["Fixture step"],
                "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
            },
        ],
    }
    write(package / "evals/visual-checkpoints.json", json.dumps(visual))
    manifest_paths = [
        f"solutions/{SLUG}/{name}" for name in valid_pages()
    ] + [
        f"solutions/{SLUG}/evals/visual-checkpoints.json",
        f"solutions/{SLUG}/source.py",
        "skills/aibast-easy-mode-brainstem/SKILL.md",
        "skills/aibast-easy-mode-copilot/SKILL.md",
    ]
    manifest = {
        "schema": "aibast-solution-export/1.0",
        "raw_base": RAW_BASE,
        "bundle": {
            "path": f"solutions/{SLUG}/exports/{SLUG}-source.zip",
            "raw_url": RAW_BASE
            + f"solutions/{SLUG}/exports/{SLUG}-source.zip",
        },
        "files": [
            {
                "id": f"file-{index}",
                "path": path,
                "raw_url": RAW_BASE + path,
                "status": "ready",
            }
            for index, path in enumerate(manifest_paths)
        ],
    }
    write(package / "export-manifest.json", json.dumps(manifest))
    build_zip(root)
    return package


def audit_fixture(root: Path):
    report = AUDIT.audit_repository(root)
    assert report["total"] == 1
    return report["solutions"][0]


def assert_failure(result, fragment: str) -> None:
    assert result["passed"] is False
    assert any(fragment in failure for failure in result["failures"]), result[
        "failures"
    ]


def test_valid_fixture_passes(tmp_path):
    create_fixture(tmp_path)
    result = audit_fixture(tmp_path)
    assert result["passed"] is True, result["failures"]


def test_hard_draft_frame_is_classified_by_its_tutorial_step(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "screenshots" / "manual" / "browserfilm.json"
    film = json.loads(path.read_text(encoding="utf-8"))
    film["frames"][0]["label"] = "Confirm Draft and stop before publish"
    path.write_text(json.dumps(film), encoding="utf-8")

    result = audit_fixture(tmp_path)

    assert result["passed"] is True, result["failures"]


def test_browserfilm_declared_dimensions_do_not_override_measured_pixels(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "screenshots" / "manual" / "browserfilm.json"
    film = json.loads(path.read_text(encoding="utf-8"))
    film["width"] = 1280
    film["height"] = 780
    path.write_text(json.dumps(film), encoding="utf-8")

    result = audit_fixture(tmp_path)

    assert result["passed"] is True, result["failures"]


def test_optional_detailed_visual_audit_download_is_not_required(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "evidence-report.html"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            '<a href="VISUAL-EVIDENCE-AUDIT.md" download>Detailed audit</a>',
            "",
        ),
        encoding="utf-8",
    )
    build_zip(tmp_path)

    result = audit_fixture(tmp_path)

    assert result["passed"] is True, result["failures"]


def test_rejects_manual_film_when_hard_capture_requires_reshoot(tmp_path):
    package = create_fixture(tmp_path)
    visual_path = package / "evals" / "visual-checkpoints.json"
    visual = json.loads(visual_path.read_text(encoding="utf-8"))
    hard = next(
        item for item in visual["captures"] if item["mode"] == "hard"
    )
    hard.pop("annotated")
    hard.pop("visible_anchors")
    hard.pop("boxes")
    hard["status"] = "reshoot_required"
    hard["reason"] = "The target state is not visible."
    visual["summary"]["reusable"] = 1
    visual["summary"]["reshoot_required"] = 1
    visual_path.write_text(json.dumps(visual), encoding="utf-8")
    manual = package / "manual-tutorial.html"
    manual.write_text(
        manual.read_text(encoding="utf-8").replace(
            "<body>AIBAST manual workshop",
            '<body><a href="screenshots/manual/manual-build-walkthrough.gif">'
            "Watch the manual film</a>AIBAST manual workshop",
        ),
        encoding="utf-8",
    )
    build_zip(tmp_path)

    assert_failure(
        audit_fixture(tmp_path),
        "exposes the manual film while one or more Manual captures require reshoot",
    )


def test_single_slug_scope_passes_without_scanning_other_packages(tmp_path):
    create_fixture(tmp_path)
    report = AUDIT.audit_repository(tmp_path, only_slug=SLUG)
    assert report["total"] == 1
    assert report["passed"] == 1
    assert [item["slug"] for item in report["solutions"]] == [SLUG]


def test_catalog_scope_excludes_registry_only_non_advertised_solution(tmp_path):
    create_fixture(tmp_path)
    registry_path = tmp_path / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["agents"].append(
        {
            "name": "@aibast-agents-library/grid-outage-response",
            "_demo": {"slug": "grid-outage-response"},
            "_solution": {"advertised_name": "Grid Outage Response"},
        }
    )
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    write(
        tmp_path / "tests/demo_cases/grid-outage-response.json",
        json.dumps(
            {
                "status": (
                    "GENERATED - not SharePoint-advertised. "
                    "Proves the generator; must be advertised before it ships."
                ),
                "distribution": {
                    "sharepoint_advertised": False,
                    "ship_gate": "advertise-before-ship",
                },
            }
        ),
    )
    report = AUDIT.audit_repository(tmp_path)
    assert report["total"] == 1
    assert [item["slug"] for item in report["solutions"]] == [SLUG]
    assert report["excluded_non_advertised"] == [
        {
            "slug": "grid-outage-response",
            "status": "excluded_non_advertised",
            "reason": (
                "GENERATED - not SharePoint-advertised. "
                "Proves the generator; must be advertised before it ships."
            ),
        }
    ]


def test_catches_stale_clawpilot_branding(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "quest.html"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "AIBAST guided workshop", "AIBAST Clawpilot guided workshop"
        ),
        encoding="utf-8",
    )
    assert_failure(audit_fixture(tmp_path), "stale Clawpilot branding")


def test_catches_missing_report_marker(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "quest.html"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "<!-- aibast-workshop-feedback:v1 -->", ""
        ),
        encoding="utf-8",
    )
    assert_failure(audit_fixture(tmp_path), "missing contextual feedback marker")


def test_catches_raw_link_without_download(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "manual-tutorial.html"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            'href="source.py" download', 'href="source.py"'
        ),
        encoding="utf-8",
    )
    assert_failure(audit_fixture(tmp_path), "raw .py link lacks download")


def test_catches_missing_visual_classification(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "evals/visual-checkpoints.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["captures"].pop()
    data["summary"] = {
        "total_existing_captures": 1,
        "reusable": 1,
        "reshoot_required": 0,
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    assert_failure(
        audit_fixture(tmp_path), "missing visual classification for hard step 1"
    )


def test_catches_invalid_reusable_annotation(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "evals/visual-checkpoints.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["captures"][0]["boxes"][0]["x"] = 2
    path.write_text(json.dumps(data), encoding="utf-8")
    assert_failure(audit_fixture(tmp_path), "outside 1x1 source bounds")


def test_catches_displayed_reshoot_image(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "evals/visual-checkpoints.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["captures"][0]["status"] = "reshoot_required"
    data["captures"][0]["reason"] = "The required anchor is not visible."
    data["summary"]["reusable"] = 1
    data["summary"]["reshoot_required"] = 1
    path.write_text(json.dumps(data), encoding="utf-8")
    assert_failure(audit_fixture(tmp_path), "displays reshoot-required image")


def test_catches_zip_missing_required_file(tmp_path):
    create_fixture(tmp_path)
    build_zip(
        tmp_path,
        omit=f"solutions/{SLUG}/field-guide.html",
    )
    assert_failure(
        audit_fixture(tmp_path),
        f"source ZIP missing required file solutions/{SLUG}/field-guide.html",
    )


def test_catches_zip_missing_non_hard_coded_ready_manifest_file(tmp_path):
    create_fixture(tmp_path)
    entry = f"solutions/{SLUG}/source.py"
    build_zip(tmp_path, omit=entry)
    assert_failure(
        audit_fixture(tmp_path),
        f"source ZIP missing ready manifest file {entry}",
    )


def test_catches_zip_stale_ready_manifest_bytes(tmp_path):
    package = create_fixture(tmp_path)
    (package / "source.py").write_text("print('changed')\n", encoding="utf-8")
    assert_failure(
        audit_fixture(tmp_path),
        f"source ZIP has stale bytes for ready manifest file "
        f"solutions/{SLUG}/source.py",
    )


def test_catches_malformed_inline_javascript(tmp_path):
    package = create_fixture(tmp_path)
    path = package / "quest.html"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "const feedbackSchema", "const = feedbackSchema"
        ),
        encoding="utf-8",
    )
    assert_failure(audit_fixture(tmp_path), "malformed inline JavaScript")


def test_time_entry_billing_reference_passes_with_withheld_reshoots():
    assert shutil.which("node"), "node is required by the acceptance gate"
    checker = AUDIT.ScriptChecker()
    global_failures = AUDIT.audit_global(ROOT, checker)
    result = AUDIT.audit_solution(
        ROOT,
        "time-entry-billing",
        checker=checker,
        global_failures=global_failures,
    )
    assert result["passed"] is True
    assert result["failures"] == []
    assert result["metrics"]["visual_reusable"] == 13
    assert result["metrics"]["visual_reshoot_required"] == 13
    assert result["metrics"]["visual_reference_only_displayed"] == 0


def test_repository_course_scope_uses_catalog_truth():
    failures = AUDIT.Failures()
    slugs, exclusions = AUDIT.course_scope(ROOT, failures)
    assert failures.items == []
    assert len(slugs) == 51
    assert "time-entry-billing" in slugs
    assert "grid-outage-response" not in slugs
    assert [(item["slug"], item["status"]) for item in exclusions] == [
        ("grid-outage-response", "excluded_non_advertised")
    ]
    grid_case = json.loads(
        (
            ROOT
            / "tests"
            / "demo_cases"
            / "grid-outage-response.json"
        ).read_text(encoding="utf-8")
    )
    assert grid_case["distribution"] == {
        "sharepoint_advertised": False,
        "ship_gate": "advertise-before-ship",
    }
