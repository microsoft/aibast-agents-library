import json
import re
import shutil
import subprocess
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tools.scaffold_solution_journey import (
    DARK_THEME_VARIABLES,
    THEME_PREFERENCE_SCRIPT,
    THEME_SCRIPT,
    THEME_VARIABLES,
    ScaffoldError,
    scaffold,
)


class StructureParser(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack, f"unexpected closing tag </{tag}>"
        assert self.stack.pop() == tag


def write(path, content="fixture\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def build_fixture(root):
    slug = "demo-journey"
    package = root / "solutions" / slug
    source = root / "agents" / "demo_agent.py"
    write(source, "class DemoAgent:\n    pass\n")
    write(
        root
        / "agents"
        / "@aibast-agents-library"
        / "templates"
        / "workshop_agent.py",
        "class AIBASTWorkshopAgent:\n    pass\n",
    )
    write(
        root / "skills" / "aibast-easy-mode-brainstem" / "SKILL.md",
        "---\nname: aibast-easy-mode-brainstem\ndescription: fixture\n---\n",
    )
    write(
        root / "skills" / "aibast-easy-mode-copilot" / "SKILL.md",
        "---\nname: aibast-easy-mode-copilot\ndescription: fixture\n---\n",
    )
    write(
        root / "solutions" / "_shared" / "workshop-settings.html",
        "<!doctype html><title>Workshop settings</title>\n",
    )
    write(
        package / "README.md",
        "# Demo Journey\n\nDomain narrative that the scaffolder must preserve.\n",
    )
    write(
        package / "deployment.json",
        json.dumps(
            {
                "schema": "aibast-deployment-recipe/1.0",
                "name": "@aibast-agents-library/demo-journey",
                "display_name": "Demo Journey Agent",
                "source_url": (
                    "https://raw.githubusercontent.com/microsoft/"
                    "aibast-agents-library/main/agents/demo_agent.py"
                ),
                "copilot_studio": {
                    "validated_pilot": {
                        "display_name": "Demo Journey Pilot",
                        "model": "Sonnet46",
                        "status": "Draft",
                        "published": False,
                    },
                    "required_connections": ["approved records system"],
                },
            }
        ),
    )
    write(
        package / "evals" / "transcripts.json",
        json.dumps(
            {
                "agent_sources": [{"path": "agents/demo_agent.py"}],
                "transcripts": [
                    {
                        "case_id": "DJ-01",
                        "prompt": "Show the synthetic review.",
                        "passed": True,
                    }
                ],
            }
        ),
    )
    write(
        package / "evals" / "onepager-map.json",
        json.dumps({"cases": ["DJ-01"]}),
    )
    write(
        package / "evals" / "copilot-studio-preview-evidence.json",
        json.dumps(
            {
                "status": "Draft",
                "published": False,
                "cases": [
                    {
                        "case_id": "DJ-01",
                        "prompt": "Show the synthetic review.",
                        "passed": True,
                    }
                ],
            }
        ),
    )
    write(
        package / "manual" / "GLOBAL-INSTRUCTIONS.md",
        "# Role\n\nUse only synthetic fixture records.\n",
    )
    write(package / "manual" / "knowledge" / "synthetic-records.md")
    write(package / "manual" / "knowledge" / "review-rules.md")
    write(package / "manual" / "skills" / "review" / "SKILL.md", "---\nname: review\n---\n")
    write(package / "manual" / "skills" / "summary" / "SKILL.md", "---\nname: summary\n---\n")
    write(package / "copilot-studio" / "settings.mcs.yml", "displayName: Demo Journey Pilot\n")
    write(package / "copilot-studio" / "agent.sync.yaml", "components: []\n")
    write(
        package / "copilot-studio" / "capabilities" / "knowledge" / "files" / "synthetic-records.md",
    )
    write(package / "copilot-studio" / "behaviors" / "review.mcs.yml", "kind: TaskDialog\n")

    frames = [
        ("01-create-agent.jpg", "1 · Create a blank agent"),
        ("02-enter-instructions.jpg", "2 · Enter reviewed instructions"),
        ("03-upload-records.jpg", "3 · Upload synthetic records"),
        ("04-add-review-skill.jpg", "4 · Add review skill"),
        ("05-preview-dj01.jpg", "5 · Run DJ-01"),
        ("06-draft-gate.jpg", "6 · Verify Draft and do not publish"),
    ]
    browserfilm = {
        "schema": "rapp-browserfilm/1.0",
        "capture_status": "captured",
        "frames": [
            {"file": filename, "label": label, "duration_ms": 1200}
            for filename, label in frames
        ],
    }
    write(
        package / "screenshots" / "manual" / "browserfilm.json",
        json.dumps(browserfilm),
    )
    for filename, _label in frames:
        write(package / "screenshots" / "manual" / filename, b"real-fixture-frame")
    write(package / "screenshots" / "manual" / "manual-build-walkthrough.gif", b"GIF89a")
    write(package / "screenshots" / "manual" / "manual-build-contact-sheet.jpg", b"jpeg")

    assisted_frames = [
        {
            "file": "01-assisted-draft.jpg",
            "label": "1 · Review Draft",
            "duration_ms": 1200,
        },
        {
            "file": "05-preview-dj01.jpg",
            "label": "5 · Run DJ-01",
            "duration_ms": 1200,
        },
    ]
    write(
        package / "screenshots" / "assisted" / "browserfilm.json",
        json.dumps({"frames": assisted_frames}),
    )
    write(package / "screenshots" / "assisted" / "01-assisted-draft.jpg", b"jpeg")
    write(package / "screenshots" / "assisted" / "05-preview-dj01.jpg", b"jpeg")
    write(package / "screenshots" / "assisted" / "copilot-assisted-walkthrough.gif", b"GIF89a")
    write(package / "screenshots" / "assisted" / "copilot-assisted-contact-sheet.jpg", b"jpeg")

    write(
        package / "evals" / "manual-build-evidence.json",
        json.dumps(
            {
                "schema": "aibast-manual-build-evidence/1.0",
                "status": "passed",
                "manual_agent": {
                    "display_name": "Demo Journey Manual Build",
                    "created": True,
                },
                "target_model": "Claude Sonnet 4.6",
                "manual_components": {
                    "global_instructions": {"expected": True, "confirmed": True},
                    "knowledge_files": {"expected": 2, "confirmed": 2},
                    "skills": {"expected": 2, "confirmed": 2},
                },
                "canonical_preview": [
                    {
                        "case_id": "DJ-01",
                        "must_include": ["Synthetic Record A"],
                        "expected_screenshot": "05-preview-dj01.jpg",
                        "passed": True,
                    }
                ],
                "browserfilm": {
                    "status": "captured",
                    "manifest": (
                        "solutions/demo-journey/screenshots/manual/browserfilm.json"
                    ),
                    "gif": (
                        "solutions/demo-journey/screenshots/manual/"
                        "manual-build-walkthrough.gif"
                    ),
                    "contact_sheet": (
                        "solutions/demo-journey/screenshots/manual/"
                        "manual-build-contact-sheet.jpg"
                    ),
                },
                "publication_gate": {
                    "required_state": "Draft",
                    "published": False,
                    "confirmation_screenshot": "06-draft-gate.jpg",
                },
            }
        ),
    )
    return package, frames


def assert_html_and_javascript_valid(path, scratch):
    text = path.read_text(encoding="utf-8")
    parser = StructureParser()
    parser.feed(text)
    parser.close()
    assert parser.stack == []
    scripts = re.findall(r"<script>(.*?)</script>", text, re.DOTALL)
    assert len(scripts) >= 2
    for index, script in enumerate(scripts):
        script_path = scratch / f"{path.stem}-{index}.js"
        script_path.write_text(script, encoding="utf-8")
        result = subprocess.run(
            ["node", "--check", str(script_path)],
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr


def test_scaffolds_complete_evidence_grounded_journey(tmp_path):
    package, frames = build_fixture(tmp_path)

    scaffold("demo-journey", root=tmp_path)

    guide = (package / "FIELD-GUIDE.md").read_text(encoding="utf-8")
    guide_html = (package / "field-guide.html").read_text(
        encoding="utf-8"
    )
    evidence_html = (package / "evidence-report.html").read_text(
        encoding="utf-8"
    )
    personless = (package / "EASY-MODE-PERSONLESS.md").read_text(
        encoding="utf-8"
    )
    easy_prompts = (package / "EASY-MODE-COPILOT-CHAT.md").read_text(
        encoding="utf-8"
    )
    quest = (package / "quest.html").read_text(encoding="utf-8")
    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    manifest = json.loads((package / "export-manifest.json").read_text(encoding="utf-8"))
    readme = (package / "README.md").read_text(encoding="utf-8")

    assert "Easy mode — GitHub Copilot (default)" in guide
    assert "Easy mode — GitHub Copilot + Brainstem (optional)" in guide
    assert guide.index("GitHub Copilot (default)") < guide.index(
        "GitHub Copilot + Brainstem (optional)"
    )
    assert "two short messages" in guide
    assert "personal, on-device training AI" in guide
    assert "Hard mode — literal browser construction" in guide
    assert "Production replacement seams" in guide
    assert "Failure recovery" in guide
    assert "Evidence gates" in guide
    assert "synthetic" in guide.lower()
    assert "customer KPI" in guide
    assert "## Workshop mission" in guide
    assert "non-technical sales professionals into AI superheroes" in guide

    for generated in (guide_html, evidence_html, quest, tutorial):
        assert THEME_SCRIPT in generated
        assert THEME_PREFERENCE_SCRIPT in generated
        assert THEME_VARIABLES in generated
        assert DARK_THEME_VARIABLES in generated
        assert "AIBAST" in generated
        assert "Clawpilot" not in generated
    for generated in (guide_html, quest, tutorial):
        assert "localStorage" in generated
    assert "GitHub Copilot + Brainstem" in quest
    assert "GitHub Copilot only" in quest
    assert "Personless harness" in quest
    assert "Download generic workshop agent" in quest
    assert "Skeptic comparison" in quest
    assert "aibast:workshop-engine" in quest
    assert 'data-easy-lane-button' not in quest
    assert "Workshop settings" in quest
    assert 'href="field-guide.html"' in quest
    assert 'href="FIELD-GUIDE.md"' not in quest
    assert 'href="evidence-report.html"' in quest
    assert 'href="VISUAL-EVIDENCE-AUDIT.md"' not in quest
    assert quest.count("data-copy-target=") == 7
    assert "Download Brainstem SKILL.md" in quest
    assert "Download Copilot-only SKILL.md" in quest
    assert quest.count('download="SKILL.md"') == 2
    assert "Drag the downloaded file into the chat." in quest
    assert "Give me Demo Journey using Easy Mode and test it for me." in quest
    assert "using Easy Mode without Brainstem" not in quest
    assert "Deploy it into Copilot Studio for me." in quest
    assert "Facilitator evidence and portable download" in quest
    assert "Raw resources" not in quest
    assert "What you will learn" in quest
    assert "<strong>Workshop mission:</strong>" in quest
    assert "non-technical sales professionals into AI superheroes" in quest
    assert "Before you begin" in quest
    assert quest.count('class="learn-step"') == 8
    assert "Prove the solution locally" in quest
    assert "Create the reviewed Draft" in quest
    assert "Confirm the Draft in Copilot Studio Preview" in quest
    assert "Shown at or below natural size" in quest
    assert ".preview-shot { display: block; width: 100%; max-width: 100%" in quest
    assert 'class="preview-case preview-case-wide"' in quest
    assert "Confirm the expected evidence" in quest
    assert "Preview response matched this contract" in quest
    assert "Know what “done” looks like" in quest
    assert "Final expected verdict" in quest
    assert "Troubleshooting" in quest
    assert "Reshoot required" not in quest
    assert "No approved visual checkpoint" not in quest
    assert "Compare and contrast while you build" not in quest
    assert "<iframe" not in quest
    assert 'class="path" data-path="hard"' in quest
    assert quest.count('<article class="step"') == len(frames)
    assert "manually on this page." in quest
    assert "manual-progress" in quest
    assert "Draft · published false" in quest
    assert "manual-tutorial.html" in quest
    assert "Watch assisted film" not in quest
    assert "copilot-assisted-walkthrough.gif" not in quest
    assert "Open standalone Hard-mode guide" in quest
    assert "Attach the Brainstem skill" in personless
    assert "drag `SKILL.md` into the" in personless
    assert "Give me Demo Journey using Easy Mode and test it for me." in personless
    assert "Deploy it into Copilot Studio for me." in personless
    assert "AIBASTWorkshopAgent" in personless
    assert "Brainstem + Copilot pull the harness" in personless
    assert "GitHub Copilot Easy mode" in easy_prompts
    assert "comparison" not in easy_prompts.lower()
    assert "Attach the Copilot-only skill" in easy_prompts
    assert "drag `SKILL.md` into the" in easy_prompts
    assert "Give me Demo Journey using Easy Mode and test it for me." in easy_prompts
    assert "using Easy Mode without Brainstem" not in easy_prompts
    assert "Deploy it into Copilot Studio for me." in easy_prompts
    assert "default Easy path" not in personless

    assert "0 of 6 complete" in tutorial
    assert tutorial.count("<strong>Action</strong>") == len(frames)
    assert tutorial.count("<strong>Expected result</strong>") == len(frames)
    assert tutorial.count("Download source:") == len(frames)
    assert tutorial.count('data-copy-target="hard-copy-') == 2
    assert "Copy instructions" in tutorial
    assert "Copy Preview prompt" in tutorial
    assert "Use only synthetic fixture records." in tutorial
    assert "Show the synthetic review." in tutorial
    assert "No PAC CLI, YAML import, or plugin architect" in tutorial
    assert "postMessage" not in tutorial
    assert "data-embedded" not in tutorial
    assert "Do not choose Publish" in tutorial
    assert "Open Preview in a fresh conversation before running DJ-01" in tutorial
    assert "Shown without browser upscaling" in tutorial
    assert ".shot { display: block; width: auto; max-width: 100%" in tutorial
    for filename, label in frames:
        assert tutorial.count(filename) >= 3
        assert label.split("·", 1)[1].strip() in tutorial

    resources = {item["id"]: item for item in manifest["files"]}
    for required in [
        "portable-agent",
        "deployment-recipe",
        "field-guide",
        "field-guide-source",
        "evidence-report",
        "easy-personless-guide",
        "easy-mode-brainstem-skill",
        "easy-mode-copilot-skill",
        "generic-workshop-agent",
        "easy-copilot-chat-prompts",
        "settings",
        "agent-sync",
        "manual-instructions",
        "brainstem-transcripts",
        "onepager-map",
        "manual-evidence",
        "assisted-browserfilm-manifest",
        "assisted-browserfilm",
        "assisted-contact-sheet",
        "manual-browserfilm-manifest",
        "manual-browserfilm",
        "manual-contact-sheet",
        "quest",
        "manual-tutorial",
    ]:
        assert resources[required]["status"] == "ready"
    assert any(item["id"].startswith("knowledge-") for item in manifest["files"])
    assert any(item["id"].startswith("skill-") for item in manifest["files"])
    assert all(item["raw_url"].endswith(item["path"]) for item in manifest["files"])
    assert manifest["bundle"]["path"] == (
        "solutions/demo-journey/exports/demo-journey-source.zip"
    )

    assert "Domain narrative that the scaffolder must preserve." in readme
    assert "Customer journey package map" in readme
    assert "resources ready; 0 pending" in readme
    assert (package / "screenshots" / "README.md").exists()
    assert (package / "field-guide.html").exists()
    assert (package / "evidence-report.html").exists()
    assert (package / "screenshots" / "manual" / "README.md").exists()
    assert (package / "screenshots" / "assisted" / "README.md").exists()
    assert (package / "exports" / "README.md").exists()

    assert_html_and_javascript_valid(package / "quest.html", tmp_path)
    assert_html_and_javascript_valid(package / "manual-tutorial.html", tmp_path)
    quest = (package / "quest.html").read_text(encoding="utf-8")
    assert 'class="preview-case preview-case-wide"' in quest
    assert ".preview-case-wide { grid-column: 1 / -1; }" in quest
    assert (
        ".preview-shot { display: block; width: 100%; max-width: 100%;"
        in quest
    )
    assert ".shot { display: block; width: 100%; max-width: 100%;" in quest

    ctx = __import__(
        "tools.scaffold_solution_journey",
        fromlist=["load_context", "choose_frame_resources", "expected_result"],
    )
    loaded = ctx.load_context(
        tmp_path,
        "demo-journey",
        allow_pending=False,
        raw_base="https://example.test/raw/",
    )
    resources = ctx.choose_frame_resources(loaded)
    assert resources[3] == package / "manual" / "skills" / "review" / "SKILL.md"
    assert ctx.expected_result(
        loaded,
        "Open a fresh Preview conversation",
        "unmatched.jpg",
    ).startswith("A fresh Preview surface")


def test_scaffolder_uses_reviewed_copilot_studio_knowledge_as_legacy_fallback(
    tmp_path,
):
    package, _frames = build_fixture(tmp_path)
    shutil.rmtree(package / "manual" / "knowledge")

    scaffold(
        "demo-journey",
        root=tmp_path,
        raw_base="https://example.test/raw/",
    )

    manifest = json.loads(
        (package / "export-manifest.json").read_text(encoding="utf-8")
    )
    paths = {item["path"] for item in manifest["files"]}
    assert (
        "solutions/demo-journey/copilot-studio/capabilities/knowledge/files/"
        "synthetic-records.md"
    ) in paths
    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    assert "copilot-studio/capabilities/knowledge/files/synthetic-records.md" in tutorial


def test_refuses_missing_referenced_screenshot_without_allow_pending(tmp_path):
    package, _frames = build_fixture(tmp_path)
    missing = package / "screenshots" / "manual" / "05-preview-dj01.jpg"
    missing.unlink()

    with pytest.raises(ScaffoldError, match="refusing to fabricate"):
        scaffold("demo-journey", root=tmp_path)

    assert not (package / "FIELD-GUIDE.md").exists()
    assert not (package / "export-manifest.json").exists()


def test_allow_pending_labels_missing_evidence_without_fabricating_image(tmp_path):
    package, _frames = build_fixture(tmp_path)
    missing = package / "screenshots" / "manual" / "05-preview-dj01.jpg"
    missing.unlink()

    scaffold("demo-journey", root=tmp_path, allow_pending=True)

    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    manifest = json.loads((package / "export-manifest.json").read_text(encoding="utf-8"))
    frame = next(item for item in manifest["files"] if item["path"].endswith(missing.name))
    assert frame["status"] == "pending_capture"
    assert "Evidence pending. No screenshot is shown" in tutorial
    assert f'src="screenshots/manual/{missing.name}"' not in tutorial
    assert "--allow-pending" in tutorial


def test_reshoot_images_are_withheld_while_reusable_annotations_remain_visible(
    tmp_path,
):
    package, _frames = build_fixture(tmp_path)
    captures = [
        {
            "id": "easy-dj-01",
            "mode": "easy",
            "case_id": "DJ-01",
            "source": (
                "solutions/demo-journey/screenshots/assisted/"
                "05-preview-dj01.jpg"
            ),
            "annotated": (
                "solutions/demo-journey/screenshots/assisted/annotated/"
                "05-preview-dj01.png"
            ),
            "status": "reusable",
            "visible_anchors": ["Synthetic Record A"],
            "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
        },
        {
            "id": "easy-confirm-draft",
            "mode": "easy",
            "source": (
                "solutions/demo-journey/screenshots/assisted/"
                "01-assisted-draft.jpg"
            ),
            "status": "reshoot_required",
            "reason": "The Draft identity is cropped.",
        },
        {
            "id": "hard-step-01",
            "mode": "hard",
            "step": 1,
            "source": (
                "solutions/demo-journey/screenshots/manual/"
                "01-create-agent.jpg"
            ),
            "annotated": (
                "solutions/demo-journey/screenshots/manual/annotated/"
                "01-create-agent.png"
            ),
            "status": "reusable",
            "visible_anchors": ["Blank agent"],
            "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
        },
        {
            "id": "hard-step-02",
            "mode": "hard",
            "step": 2,
            "source": (
                "solutions/demo-journey/screenshots/manual/"
                "02-enter-instructions.jpg"
            ),
            "status": "reshoot_required",
            "reason": "The reviewed instructions are not legible.",
        },
    ]
    write(
        package / "evals" / "visual-checkpoints.json",
        json.dumps(
            {
                "schema": "aibast-visual-checkpoints/1.0",
                "summary": {
                    "total_existing_captures": 4,
                    "reusable": 2,
                    "reshoot_required": 2,
                },
                "captures": captures,
            }
        ),
    )
    write(
        package
        / "screenshots"
        / "assisted"
        / "annotated"
        / "05-preview-dj01.png",
        b"annotated",
    )
    write(
        package
        / "screenshots"
        / "manual"
        / "annotated"
        / "01-create-agent.png",
        b"annotated",
    )

    scaffold("demo-journey", root=tmp_path)

    quest = (package / "quest.html").read_text(encoding="utf-8")
    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    evidence = (package / "evidence-report.html").read_text(encoding="utf-8")
    learner_html = quest + tutorial

    assert 'src="screenshots/assisted/annotated/05-preview-dj01.png"' in quest
    assert 'download="05-preview-dj01.png"' in quest
    assert 'class="preview-case preview-case-wide"' in quest
    assert 'src="screenshots/manual/annotated/01-create-agent.png"' in tutorial
    assert 'download="01-create-agent.png"' in tutorial
    assert 'src="screenshots/assisted/01-assisted-draft.jpg"' not in learner_html
    assert 'src="screenshots/manual/02-enter-instructions.jpg"' not in learner_html
    assert 'href="screenshots/assisted/01-assisted-draft.jpg"' not in learner_html
    assert 'href="screenshots/manual/02-enter-instructions.jpg"' not in learner_html
    assert 'data-evidence-status="reference-only"' not in learner_html
    assert "Withheld checkpoint — reshoot required" in learner_html
    assert "Expected state:" in learner_html
    assert "01-assisted-draft.jpg" in evidence
    assert "02-enter-instructions.jpg" in evidence


def test_reusable_original_downloads_use_checkpoint_sources(tmp_path):
    package, _frames = build_fixture(tmp_path)
    captures = [
        {
            "id": "easy-dj-01",
            "mode": "easy",
            "case_id": "DJ-01",
            "source": (
                "solutions/demo-journey/screenshots/assisted/"
                "reviewed-case-original.png"
            ),
            "annotated": (
                "solutions/demo-journey/screenshots/assisted/annotated/"
                "reviewed-case.png"
            ),
            "status": "reusable",
            "visible_anchors": ["Synthetic Record A"],
            "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
        },
        {
            "id": "easy-confirm-draft",
            "mode": "easy",
            "source": (
                "solutions/demo-journey/screenshots/assisted/"
                "01-assisted-draft.jpg"
            ),
            "annotated": (
                "solutions/demo-journey/screenshots/assisted/annotated/"
                "reviewed-draft.png"
            ),
            "status": "reusable",
            "visible_anchors": ["Draft", "Published false"],
            "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
        },
        {
            "id": "hard-step-01",
            "mode": "hard",
            "step": 1,
            "source": (
                "solutions/demo-journey/screenshots/manual/"
                "reviewed-hard-original.png"
            ),
            "annotated": (
                "solutions/demo-journey/screenshots/manual/annotated/"
                "reviewed-hard.png"
            ),
            "status": "reusable",
            "visible_anchors": ["Blank agent"],
            "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
        },
    ]
    write(
        package / "evals" / "visual-checkpoints.json",
        json.dumps(
            {
                "schema": "aibast-visual-checkpoints/1.0",
                "summary": {
                    "total_existing_captures": 3,
                    "reusable": 3,
                    "reshoot_required": 0,
                },
                "captures": captures,
            }
        ),
    )
    for capture in captures:
        write(tmp_path / capture["source"], b"source")
        write(tmp_path / capture["annotated"], b"annotated")

    scaffold("demo-journey", root=tmp_path)

    quest = (package / "quest.html").read_text(encoding="utf-8")
    tutorial = (package / "manual-tutorial.html").read_text(encoding="utf-8")
    assert 'href="screenshots/assisted/reviewed-case-original.png"' in quest
    assert 'href="screenshots/assisted/01-assisted-draft.jpg"' in quest
    assert 'href="screenshots/manual/reviewed-hard-original.png"' in tutorial
    assert 'href="screenshots/assisted/05-preview-dj01.jpg"' not in quest
    assert 'href="screenshots/manual/01-create-agent.jpg"' not in tutorial


def test_refuses_unpassed_manual_evidence_unless_allow_pending(tmp_path):
    package, _frames = build_fixture(tmp_path)
    evidence_path = package / "evals" / "manual-build-evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    evidence["canonical_preview"][0]["passed"] = False
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

    with pytest.raises(ScaffoldError, match="does not record passed manual Preview"):
        scaffold("demo-journey", root=tmp_path)

    scaffold("demo-journey", root=tmp_path, allow_pending=True)
    guide = (package / "FIELD-GUIDE.md").read_text(encoding="utf-8")
    assert "Pending items are not proof" in guide


def test_readme_update_is_idempotent_and_preserves_domain_content(tmp_path):
    package, _frames = build_fixture(tmp_path)

    scaffold("demo-journey", root=tmp_path)
    first = (package / "README.md").read_text(encoding="utf-8")
    scaffold("demo-journey", root=tmp_path)
    second = (package / "README.md").read_text(encoding="utf-8")

    assert first == second
    assert second.count("scaffold-solution-journey:start") == 1
    assert "Domain narrative that the scaffolder must preserve." in second


def test_optional_export_uses_existing_builder_semantics(tmp_path):
    package, _frames = build_fixture(tmp_path)
    repository_root = Path(__file__).resolve().parent.parent
    write(
        tmp_path / "tools" / "build_solution_export.py",
        (repository_root / "tools" / "build_solution_export.py").read_text(
            encoding="utf-8"
        ),
    )

    scaffold("demo-journey", root=tmp_path, build_bundle=True)

    bundle = package / "exports" / "demo-journey-source.zip"
    assert bundle.exists()
    with zipfile.ZipFile(bundle) as archive:
        names = set(archive.namelist())
    assert "solutions/demo-journey/FIELD-GUIDE.md" in names
    assert "solutions/demo-journey/field-guide.html" in names
    assert "solutions/demo-journey/evidence-report.html" in names
    assert "solutions/demo-journey/EASY-MODE-PERSONLESS.md" in names
    assert "skills/aibast-easy-mode-brainstem/SKILL.md" in names
    assert "skills/aibast-easy-mode-copilot/SKILL.md" in names
    assert "agents/@aibast-agents-library/templates/workshop_agent.py" in names
    assert "solutions/demo-journey/EASY-MODE-COPILOT-CHAT.md" in names
    assert "solutions/demo-journey/quest.html" in names
    assert "solutions/demo-journey/manual-tutorial.html" in names
    assert "agents/demo_agent.py" in names
