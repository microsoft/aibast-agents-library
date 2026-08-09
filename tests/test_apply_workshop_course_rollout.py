import json
from pathlib import Path

import pytest

from tools.apply_workshop_course_rollout import (
    AdvertisedSolution,
    RESHOOT_REASON,
    RolloutError,
    apply_package,
    build_visual_contract,
    load_rollout_inputs,
    resolve_advertised_solutions,
    select_targets,
    write_visual_contract,
)


ROOT = Path(__file__).resolve().parent.parent


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def rollout_fixture(tmp_path, *, assisted=True):
    slug = "demo-rollout"
    package = tmp_path / "solutions" / slug
    write_json(
        tmp_path / "tests" / "demo_cases" / f"{slug}.json",
        {
            "cases": [
                {"id": "DR-01"},
                {"id": "DR-02"},
                {"id": "DR-03"},
            ]
        },
    )
    if assisted:
        write_json(
            package / "screenshots" / "assisted" / "browserfilm.json",
            {
                "frames": [
                    {
                        "file": "01-unlabelled.jpg",
                        "label": "Pass the first captured case",
                    },
                    {
                        "file": "02-dr-01.jpg",
                        "label": "Pass DR-01: explicit label wins",
                    },
                    {
                        "file": "03-review.jpg",
                        "label": "Review the Copilot-assisted Draft configuration",
                    },
                    {
                        "file": "04-unlabelled.jpg",
                        "label": "Pass the remaining captured case",
                    },
                    {
                        "file": "05-confirm.jpg",
                        "label": "Confirm the validated agent remains Draft",
                    },
                ]
            },
        )
    write_json(
        package / "screenshots" / "manual" / "browserfilm.json",
        {
            "frames": [
                {"file": "same-source.jpg", "label": "Create the manual agent"},
                {"file": "same-source.jpg", "label": "Pass DR-01 in Preview"},
                {"file": "03-confirm.jpg", "label": "Confirm Draft"},
            ]
        },
    )
    (package / "evals").mkdir(parents=True)
    return AdvertisedSolution(
        name="@aibast-agents-library/demo-rollout",
        slug=slug,
    )


def test_catalog_scope_is_exact_and_excludes_registry_only_grid():
    advertised = resolve_advertised_solutions(ROOT)

    assert len(advertised) == 51
    assert "grid-outage-response" not in advertised
    assert "time-entry-billing" in advertised
    assert "product-line-optimization" in advertised
    assert "production-line-optimization" not in advertised


def test_all_scope_skips_the_reviewed_billing_reference():
    advertised = resolve_advertised_solutions(ROOT)

    targets, skipped = select_targets(advertised, slug=None, all_packages=True)

    assert len(targets) == 50
    assert "time-entry-billing" not in {item.slug for item in targets}
    assert skipped == [
        {
            "slug": "time-entry-billing",
            "reason": (
                "Preserved as the individually reviewed visual-contract "
                "reference package."
            ),
        }
    ]


def test_assisted_mapping_reserves_explicit_cases_and_detects_draft(tmp_path):
    solution = rollout_fixture(tmp_path)
    inputs = load_rollout_inputs(tmp_path, solution.slug)

    captures = [
        item
        for item in build_visual_contract(solution, inputs)["captures"]
        if item["mode"] == "easy"
    ]

    assert [item.get("case_id") for item in captures] == [
        "DR-02",
        "DR-01",
        None,
        "DR-03",
        None,
    ]
    assert captures[0]["source"].endswith("/01-unlabelled.jpg")
    assert captures[2]["id"].startswith("easy-draft")
    assert captures[4]["id"].startswith("easy-draft")


def test_manual_steps_keep_duplicate_sources_as_distinct_captures(tmp_path):
    solution = rollout_fixture(tmp_path)
    inputs = load_rollout_inputs(tmp_path, solution.slug)

    captures = [
        item
        for item in build_visual_contract(solution, inputs)["captures"]
        if item["mode"] == "hard"
    ]

    assert [item["step"] for item in captures] == [1, 2, 3]
    assert captures[0]["source"] == captures[1]["source"]
    assert captures[0]["id"] == "hard-step-01"
    assert captures[1]["id"] == "hard-step-02"
    assert captures[1]["case_id"] == "DR-01"


def test_contract_has_no_annotations_and_reconciles_reshoot_summary(tmp_path):
    solution = rollout_fixture(tmp_path)
    document = build_visual_contract(
        solution,
        load_rollout_inputs(tmp_path, solution.slug),
    )

    captures = document["captures"]
    assert document["summary"] == {
        "total_existing_captures": len(captures),
        "reusable": 0,
        "reshoot_required": len(captures),
        "new_learn_step_captures_recommended": 0,
    }
    assert all(item["status"] == "reshoot_required" for item in captures)
    assert all(item["reason"] == RESHOOT_REASON for item in captures)
    assert all("annotated" not in item for item in captures)


def test_missing_assisted_browserfilm_does_not_invent_easy_frames(tmp_path):
    solution = rollout_fixture(tmp_path, assisted=False)

    document = build_visual_contract(
        solution,
        load_rollout_inputs(tmp_path, solution.slug),
    )

    assert {item["mode"] for item in document["captures"]} == {"hard"}
    assert document["summary"]["total_existing_captures"] == 3


def test_existing_visual_contract_is_protected_unless_forced(tmp_path):
    solution = rollout_fixture(tmp_path)
    inputs = load_rollout_inputs(tmp_path, solution.slug)
    path = (
        tmp_path
        / "solutions"
        / solution.slug
        / "evals"
        / "visual-checkpoints.json"
    )
    original = '{\n  "reviewed": true\n}\n'
    path.write_text(original, encoding="utf-8")

    state, document = write_visual_contract(
        tmp_path,
        solution,
        inputs,
        force=False,
    )

    assert state == "preserved"
    assert document is None
    assert path.read_text(encoding="utf-8") == original

    state, document = write_visual_contract(
        tmp_path,
        solution,
        inputs,
        force=True,
    )
    assert state == "replaced"
    assert document["schema"] == "aibast-visual-checkpoints/1.0"
    assert json.loads(path.read_text(encoding="utf-8")) == document


def test_apply_package_uses_scaffolder_without_allow_pending(tmp_path):
    solution = rollout_fixture(tmp_path)
    calls = []

    def preflight(root, slug, **kwargs):
        calls.append(("preflight", root, slug, kwargs))

    def scaffold(slug, **kwargs):
        calls.append(("scaffold", slug, kwargs))

    result = apply_package(
        tmp_path,
        solution,
        raw_base="https://example.test/raw/",
        build_export=True,
        force_visual_contract=False,
        preflight_func=preflight,
        scaffold_func=scaffold,
    )

    assert result["visual_contract"] == "created"
    assert calls == [
        (
            "preflight",
            tmp_path,
            solution.slug,
            {
                "allow_pending": False,
                "raw_base": "https://example.test/raw/",
            },
        ),
        (
            "scaffold",
            solution.slug,
            {
                "root": tmp_path,
                "allow_pending": False,
                "raw_base": "https://example.test/raw/",
                "build_bundle": True,
            },
        ),
    ]


def test_required_manual_foundation_is_enforced(tmp_path):
    slug = "missing-manual"
    (tmp_path / "solutions" / slug).mkdir(parents=True)
    write_json(
        tmp_path / "tests" / "demo_cases" / f"{slug}.json",
        {"cases": [{"id": "MM-01"}]},
    )

    with pytest.raises(RolloutError, match="manual browserfilm"):
        load_rollout_inputs(tmp_path, slug)
