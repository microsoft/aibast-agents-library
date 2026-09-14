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
HISTORICAL_HASHES = {
    "screenshots/manual/16-inspector-skill-validation-error.jpg": (
        "cd250909369f1269a970c42973ffa92b79288f34f942dc1a601836edbd3c9c1b"
    ),
    "screenshots/manual/17-retry-inspector-skill.jpg": (
        "0513b1b2c74264a286fb635e2fe9ca2299a1f19a65bd46436597a58838e299dc"
    ),
    "screenshots/annotated/hard-step-16.png": (
        "0f7ca55fc340c76a33b46d07779a41b6990d14cc0646bf887c51aef85b29bcaa"
    ),
    "screenshots/annotated/hard-step-17.png": (
        "e742131a394f7a2bd103b5750d739dcc882021142594c1ad10dc94e6ddeb1e39"
    ),
}


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


def test_validation_steps_accept_success_or_an_authentic_error_without_forcing_retry():
    browserfilm = read_json(PACKAGE / "screenshots/manual/browserfilm.json")
    frames = browserfilm["frames"]
    assert len(frames) == 24
    validation = frames[15]["tutorial"]
    confirmation = frames[16]["tutorial"]
    assert "If validation succeeds" in validation["action"]
    assert "If Copilot Studio reports an authentic validation error" in validation["action"]
    assert "Never corrupt a valid skill or manufacture an error" in validation["action"]
    assert "Only if step 16 recorded an authentic validation error" in confirmation["action"]
    assert "If step 16 succeeded, do not edit or re-upload the skill" in confirmation["action"]
    assert "Do not claim a retry" in confirmation["expected_result"]
    assert "unresolved error" in confirmation["expected_result"]

    for filename in ("manual-tutorial.html", "quest.html"):
        page = (PACKAGE / filename).read_text(encoding="utf-8")
        steps = tutorial_steps(page)
        assert len(steps) == 24
        for number, contract in ((16, validation), (17, confirmation)):
            step = steps[number - 1]
            assert step["title"] == contract["title"]
            assert " ".join(contract["action"].split()) in step["text"]
            assert " ".join(contract["expected_result"].split()) in step["text"]
            assert step["downloads"] == [SKILL]
            assert step["images"] == []
            assert "Live verification checkpoint" in step["text"]
        assert "Diagnose a SKILL.md validation failure" not in page
        assert "Correct and add inspector coverage" not in page
        assert "Watch the manual film" not in page


def test_old_failure_and_retry_evidence_is_historical_not_a_current_pass():
    visual = read_json(PACKAGE / "evals/visual-checkpoints.json")
    captures = {item["id"]: item for item in visual["captures"]}
    assert visual["summary"] == {
        "total_existing_captures": 31,
        "reusable": 22,
        "reshoot_required": 9,
    }
    assert "release_review" not in visual
    assert visual["historical_release_review"]["status"] == "approved"
    assert visual["source_contract_review"]["status"] == "reshoot_required"
    report = (PACKAGE / "evidence-report.html").read_text(encoding="utf-8")
    displayed, gaps = report.split("<h2>Reference-only visual gaps</h2>", 1)
    for number in (16, 17):
        identifier = f"hard-step-{number}"
        checkpoint = captures[identifier]
        assert checkpoint["status"] == "reshoot_required"
        assert checkpoint["historical"] is True
        assert "Historical" in checkpoint["reason"]
        assert identifier not in displayed
        assert identifier in gaps
        assert html.escape(checkpoint["reason"]) in gaps

    evidence = read_json(PACKAGE / "evals/manual-build-evidence.json")
    validation = evidence["skill_validation"]
    assert validation["steps"] == [16, 17]
    assert validation["step_16_outcomes"] == [
        "accepted_upload", "authentic_validation_error"
    ]
    assert validation["current_evidence_status"] == "reshoot_required"
    assert validation["current_outcome"] is None
    assert evidence["canonical_preview"]["passed"] is True
    assert evidence["publication"]["published"] is False

    for relative, digest in HISTORICAL_HASHES.items():
        assert hashlib.sha256((PACKAGE / relative).read_bytes()).hexdigest() == digest
    film_readme = (PACKAGE / "screenshots/manual/README.md").read_text(encoding="utf-8")
    assert "Historical" in film_readme
    assert "Never corrupt a valid skill or manufacture an error" in film_readme


def test_normalization_keeps_the_canonical_policy_and_generated_copies_in_parity():
    instructions = (PACKAGE / "manual/GLOBAL-INSTRUCTIONS.md").read_text(encoding="utf-8")
    assert "## Locked backlog response contract" in instructions
    assert normalize_manual_instructions.START not in instructions
    assert "building-permit-processing" not in normalize_manual_instructions.normalize(
        ROOT, check=True
    )
    for filename in ("manual-tutorial.html", "quest.html"):
        assert html.escape(instructions) in (PACKAGE / filename).read_text(encoding="utf-8")


def test_downloadable_bundle_contains_the_current_contract_and_unchanged_captures():
    deployment = read_json(PACKAGE / "deployment.json")
    assert deployment["source_bundle"]["raw_base"] == (
        "https://raw.githubusercontent.com/kody-w/aibast-agents-library/staging/"
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
        *HISTORICAL_HASHES,
    ]
    with zipfile.ZipFile(bundle) as archive:
        for relative in paths:
            path = PACKAGE / relative
            assert archive.read(path.relative_to(ROOT).as_posix()) == (
                build_solution_export.bundle_bytes(path)
            ), relative
