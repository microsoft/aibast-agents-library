import hashlib
import html
import json
import zipfile
from pathlib import Path

from tests.test_solution_packages import tutorial_steps
from tools import build_solution_export, normalize_manual_instructions


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "solutions/building-permit-processing"
SKILL = "manual/skills/aibast_inspector-assignment_bp06/SKILL.md"
INSPECTOR_CAPTURES = (
    "screenshots/manual/12-add-aibast-inspector-assignment-bp06.jpg",
    "screenshots/manual/annotated/12-add-aibast-inspector-assignment-bp06.png",
)
RETIRED_FRAMES = (
    "16-inspector-skill-validation-error.jpg",
    "17-retry-inspector-skill.jpg",
)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_inspector_skill_remains_valid_and_byte_identical():
    skill = (PACKAGE / SKILL).read_bytes()
    assert hashlib.sha256(skill).hexdigest() == (
        "d0de81ccb5092a9cefe348aa1d2b8041c781f3c99d0b699d02f0f00dfc851ac9"
    )
    frontmatter = skill.decode("utf-8").split("---", 2)[1]
    fields = dict(line.split(": ", 1) for line in frontmatter.strip().splitlines())
    assert fields["name"] == "inspector-board-and-coverage"
    assert fields["description"].strip()


def test_inspector_skill_is_added_as_an_ordinary_upload_without_forcing_retry():
    # The 2026-10 re-shoot uploaded the valid inspector skill on the first try.
    # The tutorial must teach a plain upload, never a manufactured validation
    # error or retry.
    browserfilm = read_json(PACKAGE / "screenshots/manual/browserfilm.json")
    frames = browserfilm["frames"]
    files = [frame["file"] for frame in frames]
    assert len(frames) == 34
    assert files[11] == "12-add-aibast-inspector-assignment-bp06.jpg"
    assert not set(RETIRED_FRAMES) & set(files)
    for filename in ("manual-tutorial.html", "quest.html"):
        page = (PACKAGE / filename).read_text(encoding="utf-8")
        steps = tutorial_steps(page)
        assert len(steps) == len(frames)
        step = steps[11]
        assert step["title"] == "Add skill: aibast_inspector-assignment_bp06"
        assert step["downloads"] == [SKILL]
        assert step["images"] == [
            "screenshots/manual/annotated/12-add-aibast-inspector-assignment-bp06.png"
        ]
        assert "Diagnose a SKILL.md validation failure" not in page
        assert "Correct and add inspector coverage" not in page
        assert "validation error" not in page
        assert "manufacture an error" not in page


def test_current_evidence_replaces_the_old_failure_and_retry():
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    captures = {item["id"]: item for item in visual["captures"]}
    assert visual["summary"] == {
        "total_existing_captures": len(captures),
        "reusable": len(captures),
        "reshoot_required": 0,
    }
    assert "historical_release_review" not in visual
    assert "source_contract_review" not in visual
    inspector = captures["hard-step-12"]
    assert inspector["status"] == "reusable"
    assert inspector["visible_anchors"] == ["inspector-board-and-coverage"]
    report = (PACKAGE / "evidence-report.html").read_text(encoding="utf-8")
    gaps = report.split("<h2>Reference-only visual gaps</h2>", 1)[1].split("</section>", 1)[0]
    assert "<tbody></tbody>" in gaps
    # With every Manual checkpoint reusable, the film may be offered.
    tutorial = (PACKAGE / "manual-tutorial.html").read_text(encoding="utf-8")
    assert "Watch the manual film" in tutorial

    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    cases = read_json(ROOT / "tests/demo_cases/building-permit-processing.json")["cases"]
    assert "skill_validation" not in evidence
    assert evidence["status"] == "passed"
    assert evidence["manual_components"]["skills"] == {"expected": 12, "confirmed": 12}
    assert [case["case_id"] for case in evidence["canonical_preview"]] == [
        case["id"] for case in cases
    ]
    assert all(case["passed"] is True for case in evidence["canonical_preview"])
    assert evidence["publication_gate"]["published"] is False
    assert evidence["publication_gate"]["required_state"] == "Draft"
    for frame in RETIRED_FRAMES:
        assert not (PACKAGE / "screenshots/manual" / frame).exists()
    film_readme = (PACKAGE / "screenshots/manual/README.md").read_text(encoding="utf-8")
    assert "34 real browser frames" in film_readme
    assert "publication approval" in film_readme


def test_normalization_keeps_the_canonical_policy_and_generated_copies_in_parity():
    instructions = (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    assert "## Locked backlog response contract" in instructions
    assert normalize_manual_instructions.START not in instructions
    assert "building-permit-processing" not in normalize_manual_instructions.normalize(
        ROOT, check=True
    )
    for filename in ("manual-tutorial.html", "quest.html"):
        assert html.escape(instructions) in (PACKAGE / filename).read_text(encoding="utf-8")


def test_downloadable_bundle_contains_the_current_contract_and_captures():
    deployment = read_json(PACKAGE / "deployment.json")
    assert deployment["source_bundle"]["raw_base"] == (
        "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
    )
    bundle = PACKAGE / "exports/building-permit-processing-source.zip"
    paths = [
        "screenshots/manual/browserfilm.json",
        "screenshots/manual/README.md",
        "manual-tutorial.html",
        "quest.html",
        "evidence-report.html",
        "evals/manual-build-evidence.json",
        "evals/visual-checkpoints.json",
        "export-manifest.json",
        "manual/GLOBAL-INSTRUCTIONS.md",
        SKILL,
        *INSPECTOR_CAPTURES,
    ]
    with zipfile.ZipFile(bundle) as archive:
        for relative in paths:
            path = PACKAGE / relative
            assert archive.read(path.relative_to(ROOT).as_posix()) == (
                build_solution_export.bundle_bytes(path)
            ), relative
