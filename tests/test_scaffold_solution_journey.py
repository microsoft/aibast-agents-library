import json
import re
import subprocess
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tools.scaffold_solution_journey import (
    DARK_THEME_VARIABLES,
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
        / "easy_mode_agent.py",
        "class AIBASTEasyModeAgent:\n    pass\n",
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
    write(
        package / "easy" / "demo_workshop_agent.py",
        "class DemoWorkshop:\n    pass\n",
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
        {"file": "01-assisted-draft.jpg", "label": "1 · Review Draft", "duration_ms": 1200}
    ]
    write(
        package / "screenshots" / "assisted" / "browserfilm.json",
        json.dumps({"frames": assisted_frames}),
    )
    write(package / "screenshots" / "assisted" / "01-assisted-draft.jpg", b"jpeg")
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

    assert "Easy mode — with Brainstem (default)" in guide
    assert "Easy mode — without Brainstem (comparison)" in guide
    assert "three short messages" in guide
    assert "Hard mode — literal browser construction" in guide
    assert "Production replacement seams" in guide
    assert "Failure recovery" in guide
    assert "Evidence gates" in guide
    assert "synthetic" in guide.lower()
    assert "customer KPI" in guide

    for generated in (quest, tutorial):
        assert THEME_SCRIPT in generated
        assert THEME_VARIABLES in generated
        assert DARK_THEME_VARIABLES in generated
        assert "Clawpilot" in generated
        assert "localStorage" in generated
    assert "With Brainstem — default" in quest
    assert "GitHub Copilot only" in quest
    assert "Personless harness" in quest
    assert "View workshop agent" in quest
    assert "Skeptic comparison" in quest
    assert "Fast path — complete Easy mode in one message" in quest
    assert quest.count("data-copy-target=") == 9
    assert "Start the Brainstem and go and get the Easy Mode agent" in quest
    assert "Give me Demo Journey using the Easy Mode agent and test it for me." in quest
    assert "Deploy it into Copilot Studio for me." in quest
    assert "What the workshop returns" in quest
    assert "Facilitator evidence and portable download" in quest
    assert "Raw resources" not in quest
    assert "literal browser construction" in quest
    assert "Draft and is not published" in quest
    assert "manual-tutorial.html" in quest
    assert "copilot-assisted-walkthrough.gif" in quest
    assert "manual-build-walkthrough.gif" in quest
    assert "Start the Brainstem and go and get the Easy Mode agent" in personless
    assert "Give me Demo Journey using the Easy Mode agent and test it for me." in personless
    assert "Deploy it into Copilot Studio for me." in personless
    assert "demo_workshop_agent.py" in personless
    assert "Brainstem + Copilot pull the harness" in personless
    assert "GitHub Copilot Chat running in Agent mode in VS Code" in easy_prompts
    assert "Copilot-only Easy mode comparison" in easy_prompts
    assert "natural-language commands" in easy_prompts
    assert "Show the synthetic review." in easy_prompts
    assert "Do not ask me to open a terminal" in easy_prompts
    assert "Stop before publish" in easy_prompts

    assert "0 of 6 complete" in tutorial
    assert tutorial.count("<strong>Action</strong>") == len(frames)
    assert tutorial.count("<strong>Expected result</strong>") == len(frames)
    assert tutorial.count("Raw download:") == len(frames)
    assert "No PAC CLI, YAML import, or plugin architect" in tutorial
    assert "Do not choose Publish" in tutorial
    for filename, label in frames:
        assert tutorial.count(filename) == 1
        assert label.split("·", 1)[1].strip() in tutorial

    resources = {item["id"]: item for item in manifest["files"]}
    for required in [
        "portable-agent",
        "deployment-recipe",
        "field-guide",
        "easy-personless-guide",
        "easy-mode-agent",
        "easy-personless-agent",
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
    assert (package / "screenshots" / "manual" / "README.md").exists()
    assert (package / "screenshots" / "assisted" / "README.md").exists()
    assert (package / "exports" / "README.md").exists()

    assert_html_and_javascript_valid(package / "quest.html", tmp_path)
    assert_html_and_javascript_valid(package / "manual-tutorial.html", tmp_path)


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
    assert "solutions/demo-journey/EASY-MODE-PERSONLESS.md" in names
    assert "agents/@aibast-agents-library/templates/easy_mode_agent.py" in names
    assert "solutions/demo-journey/easy/demo_workshop_agent.py" in names
    assert "solutions/demo-journey/EASY-MODE-COPILOT-CHAT.md" in names
    assert "solutions/demo-journey/quest.html" in names
    assert "solutions/demo-journey/manual-tutorial.html" in names
    assert "agents/demo_agent.py" in names
