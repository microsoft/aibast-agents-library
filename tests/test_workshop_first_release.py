import hashlib
import json

from PIL import Image

from tests.test_workshop_course_rollout import PNG_1X1, create_fixture, write
from tools import audit_workshop_first_release as audit


SLUG = "time-entry-billing"


def write_distinct_image(path, index):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new(
        "RGBA",
        (1, 1),
        (index % 256, (index * 37) % 256, (index * 83) % 256, 255),
    ).save(path)


def create_release_fixture(root):
    package = create_fixture(root)
    (package / "deployment.json").write_text(
        json.dumps(
            {
                "copilot_studio": {
                    "validated_manual": {
                        "display_name": "Fixture Manual",
                        "status": "Draft",
                        "published": False,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    path = package / "evals" / "visual-checkpoints.json"
    visual = json.loads(path.read_text(encoding="utf-8"))
    visual["release_review"] = {
        "status": "approved",
        "reviewer": f"workshop-builder:{SLUG}",
        "reviewed_at": "2026-08-09T20:00:00Z",
        "method": "Independent learner-page and capture review",
        "notes": "Approved positive anchors and Draft boundary.",
    }

    additions = [
        {
            "id": "easy-confirm-draft",
            "mode": "easy",
            "source": f"solutions/{SLUG}/screenshots/assisted/confirm-draft.png",
            "annotated": (
                f"solutions/{SLUG}/screenshots/assisted/annotated/"
                "confirm-draft.png"
            ),
            "status": "reusable",
            "visible_anchors": [
                "Fixture Manual",
                "Draft",
                "Published false",
            ],
            "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
        }
    ]
    for index in range(2, 6):
        additions.append(
            {
                "id": f"hard-step-{index:02d}",
                "mode": "hard",
                "step": index,
                "source": (
                    f"solutions/{SLUG}/screenshots/manual/{index:02d}-step.png"
                ),
                "annotated": (
                    f"solutions/{SLUG}/screenshots/manual/annotated/"
                    f"{index:02d}-step.png"
                ),
                "status": "reusable",
                "visible_anchors": [f"Hard step {index}"],
                "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
            }
        )
    for index in range(4):
        additions.append(
            {
                "id": f"easy-extra-{index}",
                "mode": "easy",
                "case_id": f"EXTRA-{index}",
                "source": (
                    f"solutions/{SLUG}/screenshots/assisted/extra-{index}.png"
                ),
                "annotated": (
                    f"solutions/{SLUG}/screenshots/assisted/annotated/"
                    f"extra-{index}.png"
                ),
                "status": "reusable",
                "visible_anchors": [f"Extra anchor {index}"],
                "boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
            }
        )
    additions.append(
        {
            "id": "easy-needs-targeted-reshoot",
            "mode": "easy",
            "case_id": "RESHOOT-01",
            "source": f"solutions/{SLUG}/screenshots/assisted/reshoot.png",
            "status": "reshoot_required",
            "reason": "The target Draft identity is cropped from this capture.",
        }
    )
    visual["captures"].extend(additions)
    for capture in additions:
        for key in ("source", "annotated"):
            raw = capture.get(key)
            if raw:
                write(root / raw, PNG_1X1)
    image_index = 1
    for capture in visual["captures"]:
        if capture.get("status") != "reusable":
            continue
        for key in ("source", "annotated"):
            raw = capture.get(key)
            if raw:
                write_distinct_image(root / raw, image_index)
                image_index += 1
    assisted_path = package / "screenshots" / "assisted" / "browserfilm.json"
    assisted = json.loads(assisted_path.read_text(encoding="utf-8"))
    assisted["frames"].extend(
        [
            {"file": "confirm-draft.png", "label": "Confirm Draft state"},
            *[
                {
                    "file": f"extra-{index}.png",
                    "label": f"Pass EXTRA-{index}",
                }
                for index in range(4)
            ],
        ]
    )
    assisted_path.write_text(json.dumps(assisted), encoding="utf-8")
    manual_path = package / "screenshots" / "manual" / "browserfilm.json"
    manual = json.loads(manual_path.read_text(encoding="utf-8"))
    manual["frames"].extend(
        [
            {
                "file": f"{index:02d}-step.png",
                "label": f"Hard step {index}",
            }
            for index in range(2, 6)
        ]
    )
    manual_path.write_text(json.dumps(manual), encoding="utf-8")
    update_summary(visual)
    path.write_text(json.dumps(visual), encoding="utf-8")
    return package


def update_summary(visual):
    visual["summary"] = {
        "total_existing_captures": len(visual["captures"]),
        "reusable": sum(
            item.get("status") == "reusable" for item in visual["captures"]
        ),
        "reshoot_required": sum(
            item.get("status") == "reshoot_required"
            for item in visual["captures"]
        ),
    }


def run_gate(root):
    return audit.audit_workshop(
        root,
        SLUG,
        {"slug": SLUG, "passed": True, "failures": [], "metrics": {}},
    )


def mutate_visual(package, mutation):
    path = package / "evals" / "visual-checkpoints.json"
    visual = json.loads(path.read_text(encoding="utf-8"))
    mutation(visual)
    update_summary(visual)
    path.write_text(json.dumps(visual), encoding="utf-8")


def enable_machine_draft(package):
    path = package / "evals" / "manual-build-evidence.json"
    evidence = {
        "schema": "aibast-manual-build-evidence/1.0",
        "status": "passed",
        "canonical_preview": [{"case_id": "TEB-01", "passed": True}],
        "publication_gate": {
            "required_state": "Draft",
            "published": False,
        },
    }
    path.write_text(json.dumps(evidence), encoding="utf-8")


def enable_dataverse_draft(package):
    deployment_path = package / "deployment.json"
    deployment = json.loads(deployment_path.read_text(encoding="utf-8"))
    deployment["name"] = f"@aibast-agents-library/{SLUG}"
    deployment["copilot_studio"]["export_agent"] = {
        "display_name": "Fixture Pilot",
        "schema_name": "aibast_FixturePilot",
        "bot_id": "11111111-1111-1111-1111-111111111111",
        "environment_name": "kodyv8",
        "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
        "status": "Draft",
        "published": False,
    }
    deployment_path.write_text(json.dumps(deployment), encoding="utf-8")
    record = {
        "name": "Fixture Pilot",
        "botid": "11111111-1111-1111-1111-111111111111",
        "componentstate": 0,
        "statecode": 0,
        "statuscode": 1,
        "modifiedon": "2026-08-10T00:00:00Z",
        "publishedon": None,
        "versionnumber": 123,
        "synchronizationstatus": {
            "lastFinishedPublishOperation": None,
            "contentVersion": 2,
        },
        "odata_etag": 'W/"123"',
    }
    canonical = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    evidence = {
        "schema": "aibast-dataverse-draft-evidence/1.0",
        "captured_at": "2026-08-10T00:00:00+00:00",
        "source": {
            "kind": "Dataverse Web API",
            "environment_name": "kodyv8",
            "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
            "environment_url": "https://org7dfbd855.crm.dynamics.com",
            "api_version": "v9.2",
            "select": [],
        },
        "identity": {
            "slug": SLUG,
            "solution": f"@aibast-agents-library/{SLUG}",
            "display_name": "Fixture Pilot",
            "schema_name": "aibast_FixturePilot",
            "bot_id": "11111111-1111-1111-1111-111111111111",
        },
        "record": record,
        "record_sha256": hashlib.sha256(canonical).hexdigest(),
        "assertions": {
            "bot_id_matches": True,
            "display_name_matches": True,
            "publishedon_is_null": True,
            "last_finished_publish_operation_is_null": True,
        },
    }
    (package / "evals" / "dataverse-draft-evidence.json").write_text(
        json.dumps(evidence),
        encoding="utf-8",
    )


def enable_machine_case(package, case_id):
    root = package.parents[1]
    enable_dataverse_draft(package)
    case_path = root / "tests" / "demo_cases" / f"{SLUG}.json"
    case_data = json.loads(case_path.read_text(encoding="utf-8"))
    locked_case = next(
        case
        for case in case_data["cases"]
        if case.get("case_id", case.get("id")) == case_id
    )
    locked_case.update(
        {
            "prompt": "Run the bound machine case",
            "must_include": ["BOUND-MARKER"],
            "must_not_include": ["FORBIDDEN-MARKER"],
            "expects_agent": "BoundMachineAgent",
        }
    )
    case_path.write_text(json.dumps(case_data), encoding="utf-8")
    case_sha256 = hashlib.sha256(case_path.read_bytes()).hexdigest()

    agent_path = root / "agents" / "bound_machine_agent.py"
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_text("class BoundMachineAgent:\n    pass\n", encoding="utf-8")
    agent_sha256 = hashlib.sha256(agent_path.read_bytes()).hexdigest()

    transcript_path = package / "evals" / "transcripts.json"
    transcript_path.write_text(
        json.dumps(
            {
                "schema": "aibast-canonical-transcripts/1.0",
                "strict_isolation": True,
                "case_file": f"tests/demo_cases/{SLUG}.json",
                "case_file_sha256": case_sha256,
                "loaded_tools_after_capture": ["BoundMachineAgent"],
                "agent_sources": [
                    {
                        "path": "agents/bound_machine_agent.py",
                        "sha256": agent_sha256,
                    }
                ],
                "transcripts": [
                    {
                        "case_id": case_id,
                        "prompt": locked_case["prompt"],
                        "assistant_response": "BOUND-MARKER",
                        "agent_logs": "Bound machine execution output",
                        "expected_agent": "BoundMachineAgent",
                        "must_include": locked_case["must_include"],
                        "passed": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    preview_path = package / "evals" / "copilot-studio-preview-evidence.json"
    preview_path.write_text(
        json.dumps(
            {
                "schema": "aibast-copilot-studio-preview-evidence/1.0",
                "solution": f"@aibast-agents-library/{SLUG}",
                "environment_name": "kodyv8",
                "environment_id": "ee67a404-325c-e726-a18a-886fe708ca0b",
                "display_name": "Fixture Pilot",
                "schema_name": "aibast_FixturePilot",
                "bot_id": "11111111-1111-1111-1111-111111111111",
                "status": "Draft",
                "published": False,
                "cases": [
                    {
                        "case_id": case_id,
                        "must_include": locked_case["must_include"],
                        "must_not_include": locked_case["must_not_include"],
                        "passed": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    path = package / "evals" / "manual-build-evidence.json"
    if path.exists():
        evidence = json.loads(path.read_text(encoding="utf-8"))
    else:
        evidence = {
            "schema": "aibast-manual-build-evidence/1.0",
            "status": "passed",
            "canonical_preview": [],
            "publication_gate": {
                "required_state": "Draft",
                "published": False,
            },
        }
    evidence["status"] = "passed"
    preview = evidence.setdefault("canonical_preview", [])
    preview.append(
        {
            "case_id": case_id,
            "prompt": locked_case["prompt"],
            "must_include": locked_case["must_include"],
            "must_not_include": locked_case["must_not_include"],
            "passed": True,
        }
    )
    path.write_text(json.dumps(evidence), encoding="utf-8")


def assert_fails(result, fragment):
    assert result["passed"] is False
    assert any(fragment in failure for failure in result["failures"]), result


def test_valid_first_release_fixture_passes(tmp_path):
    create_release_fixture(tmp_path)
    result = run_gate(tmp_path)
    assert result["passed"] is True, result["failures"]
    assert result["metrics"]["reusable"] >= 10
    assert result["metrics"]["hard_reusable"] >= 5


def test_rejects_workshop_when_base_course_audit_fails(tmp_path):
    create_release_fixture(tmp_path)
    result = audit.audit_workshop(
        tmp_path,
        SLUG,
        {
            "slug": SLUG,
            "passed": False,
            "failures": ["quest.html failed"],
            "metrics": {},
        },
    )
    assert_fails(result, "base course audit did not pass")


def test_rejects_invalid_release_review(tmp_path):
    package = create_release_fixture(tmp_path)
    mutate_visual(
        package,
        lambda visual: visual["release_review"].update({"status": "pending"}),
    )
    assert_fails(run_gate(tmp_path), "release_review.status")


def test_rejects_missing_locked_case_coverage(tmp_path):
    package = create_release_fixture(tmp_path)
    mutate_visual(
        package,
        lambda visual: visual["captures"][0].update({"case_id": "OTHER"}),
    )
    assert_fails(run_gate(tmp_path), "locked cases lack reusable captures")


def test_accepts_machine_proven_locked_case_without_visual_capture(tmp_path):
    package = create_release_fixture(tmp_path)

    def remove_case(visual):
        visual["captures"] = [
            capture
            for capture in visual["captures"]
            if capture["id"] != "easy-case-01"
        ]

    mutate_visual(package, remove_case)
    enable_machine_case(package, "CASE-01")
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            '<img src="screenshots/assisted/annotated/01-case.png" '
            'alt="Reusable evidence">',
            "",
        ),
        encoding="utf-8",
    )
    result = run_gate(tmp_path)
    assert result["passed"] is True, result["failures"]
    assert result["metrics"]["locked_cases_visually_covered"] == 0
    assert result["metrics"]["locked_cases_machine_covered"] == 1


def test_rejects_machine_case_without_bound_execution_output(tmp_path):
    package = create_release_fixture(tmp_path)

    def remove_case(visual):
        visual["captures"] = [
            capture
            for capture in visual["captures"]
            if capture["id"] != "easy-case-01"
        ]

    mutate_visual(package, remove_case)
    enable_machine_case(package, "CASE-01")
    transcripts = package / "evals" / "transcripts.json"
    payload = json.loads(transcripts.read_text(encoding="utf-8"))
    payload["transcripts"][0]["assistant_response"] = "No bound marker"
    payload["transcripts"][0]["agent_logs"] = ""
    transcripts.write_text(json.dumps(payload), encoding="utf-8")
    assert_fails(run_gate(tmp_path), "locked cases lack reusable captures")


def test_rejects_missing_draft_coverage(tmp_path):
    package = create_release_fixture(tmp_path)

    def remove_draft(visual):
        visual["captures"] = [
            item
            for item in visual["captures"]
            if item["id"] != "easy-confirm-draft"
        ]

    mutate_visual(package, remove_draft)
    assert_fails(
        run_gate(tmp_path),
        "Draft state lacks identity-bound visual or Dataverse proof",
    )


def test_rejects_machine_only_draft_without_visual_capture(tmp_path):
    package = create_release_fixture(tmp_path)
    enable_machine_draft(package)

    def remove_draft(visual):
        visual["captures"] = [
            item
            for item in visual["captures"]
            if item["id"] != "easy-confirm-draft"
        ]

    mutate_visual(package, remove_draft)
    assert_fails(
        run_gate(tmp_path),
        "Draft state lacks identity-bound visual or Dataverse proof",
    )


def test_accepts_bound_dataverse_draft_without_visual_capture(tmp_path):
    package = create_release_fixture(tmp_path)
    enable_dataverse_draft(package)

    def remove_draft(visual):
        visual["captures"] = [
            item
            for item in visual["captures"]
            if item["id"] != "easy-confirm-draft"
        ]

    mutate_visual(package, remove_draft)
    result = run_gate(tmp_path)
    assert result["passed"] is True, result["failures"]
    assert result["metrics"]["draft_reusable"] == 0
    assert result["metrics"]["draft_machine_proven"] is True


def test_case_capture_containing_draft_does_not_satisfy_draft_coverage(
    tmp_path,
):
    package = create_release_fixture(tmp_path)

    def replace_draft_with_case_word(visual):
        visual["captures"] = [
            item
            for item in visual["captures"]
            if item["id"] != "easy-confirm-draft"
        ]
        case_capture = next(
            item
            for item in visual["captures"]
            if item["id"] == "easy-case-01"
        )
        case_capture["visible_anchors"].append("Draft")

    mutate_visual(package, replace_draft_with_case_word)
    assert_fails(
        run_gate(tmp_path),
        "Draft state lacks identity-bound visual or Dataverse proof",
    )


def test_rejects_insufficient_hard_coverage(tmp_path):
    package = create_release_fixture(tmp_path)

    def reduce_hard(visual):
        removed = False
        for capture in visual["captures"]:
            if capture.get("mode") == "hard" and capture.get("status") == "reusable":
                if removed:
                    continue
                capture["status"] = "reshoot_required"
                capture["reason"] = "The expected hard-mode state is cropped."
                capture.pop("annotated", None)
                capture.pop("visible_anchors", None)
                capture.pop("boxes", None)
                removed = True

    mutate_visual(package, reduce_hard)
    assert_fails(run_gate(tmp_path), "reusable hard-mode captures 4 < 5")


def test_rejects_reusable_ratio_below_floor(tmp_path):
    package = create_release_fixture(tmp_path)

    def add_reshoots(visual):
        for index in range(25):
            visual["captures"].append(
                {
                    "id": f"ratio-reshoot-{index}",
                    "mode": "easy",
                    "case_id": f"RATIO-{index}",
                    "source": (
                        f"solutions/{SLUG}/screenshots/assisted/reshoot.png"
                    ),
                    "status": "reshoot_required",
                    "reason": "The expected state is not visible.",
                }
            )

    mutate_visual(package, add_reshoots)
    assert_fails(run_gate(tmp_path), "reusable captures")


def test_rejects_generic_conservative_reason(tmp_path):
    package = create_release_fixture(tmp_path)

    def use_generic_reason(visual):
        capture = next(
            item
            for item in visual["captures"]
            if item["status"] == "reshoot_required"
        )
        capture["reason"] = (
            "These captures were not independently revalidated for a positive "
            "deterministic learner anchor."
        )

    mutate_visual(package, use_generic_reason)
    assert_fails(run_gate(tmp_path), "generic conservative rollout reason")


def test_rejects_duplicate_reusable_source_and_annotation_paths(tmp_path):
    package = create_release_fixture(tmp_path)

    def duplicate_paths(visual):
        first = next(
            item for item in visual["captures"] if item["id"] == "easy-extra-0"
        )
        second = next(
            item for item in visual["captures"] if item["id"] == "easy-extra-1"
        )
        second["source"] = first["source"]
        second["annotated"] = first["annotated"]

    mutate_visual(package, duplicate_paths)
    result = run_gate(tmp_path)
    assert_fails(result, "reusable source paths must be unique")
    assert_fails(result, "reusable annotated paths must be unique")


def test_rejects_copied_source_content_under_distinct_filenames(tmp_path):
    package = create_release_fixture(tmp_path)
    visual = json.loads(
        (package / "evals" / "visual-checkpoints.json").read_text(
            encoding="utf-8"
        )
    )
    first = next(
        item for item in visual["captures"] if item["id"] == "easy-extra-0"
    )
    second = next(
        item for item in visual["captures"] if item["id"] == "easy-extra-1"
    )
    (tmp_path / second["source"]).write_bytes(
        (tmp_path / first["source"]).read_bytes()
    )

    assert_fails(
        run_gate(tmp_path),
        "source image content is duplicated across distinct claims",
    )


def test_rejects_copied_annotation_content_under_distinct_filenames(tmp_path):
    package = create_release_fixture(tmp_path)
    visual = json.loads(
        (package / "evals" / "visual-checkpoints.json").read_text(
            encoding="utf-8"
        )
    )
    first = next(
        item for item in visual["captures"] if item["id"] == "easy-extra-0"
    )
    second = next(
        item for item in visual["captures"] if item["id"] == "easy-extra-1"
    )
    (tmp_path / second["annotated"]).write_bytes(
        (tmp_path / first["annotated"]).read_bytes()
    )

    assert_fails(run_gate(tmp_path), "annotated image content is duplicated")


def test_rejects_annotation_unchanged_from_source(tmp_path):
    package = create_release_fixture(tmp_path)
    visual = json.loads(
        (package / "evals" / "visual-checkpoints.json").read_text(
            encoding="utf-8"
        )
    )
    capture = next(
        item for item in visual["captures"] if item["id"] == "easy-extra-0"
    )
    (tmp_path / capture["annotated"]).write_bytes(
        (tmp_path / capture["source"]).read_bytes()
    )

    assert_fails(run_gate(tmp_path), "annotation is pixel-identical to its source")


def test_rejects_undecodable_reusable_image(tmp_path):
    package = create_release_fixture(tmp_path)
    visual = json.loads(
        (package / "evals" / "visual-checkpoints.json").read_text(
            encoding="utf-8"
        )
    )
    capture = next(
        item for item in visual["captures"] if item["id"] == "easy-extra-0"
    )
    (tmp_path / capture["source"]).write_bytes(b"not an image")

    assert_fails(run_gate(tmp_path), "cannot be decoded as an image")


def test_rejects_easy_case_source_mismatch(tmp_path):
    package = create_release_fixture(tmp_path)

    def swap_case_sources(visual):
        first = next(
            item for item in visual["captures"] if item["id"] == "easy-extra-0"
        )
        second = next(
            item for item in visual["captures"] if item["id"] == "easy-extra-1"
        )
        first["source"], second["source"] = second["source"], first["source"]

    mutate_visual(package, swap_case_sources)
    assert_fails(run_gate(tmp_path), "source does not match claimed easy case")


def test_rejects_hard_step_source_mismatch(tmp_path):
    package = create_release_fixture(tmp_path)

    def swap_step_sources(visual):
        first = next(
            item for item in visual["captures"] if item["id"] == "hard-step-02"
        )
        second = next(
            item for item in visual["captures"] if item["id"] == "hard-step-03"
        )
        first["source"], second["source"] = second["source"], first["source"]

    mutate_visual(package, swap_step_sources)
    assert_fails(run_gate(tmp_path), "source does not match claimed hard step")


def test_rejects_reference_only_learner_image(tmp_path):
    package = create_release_fixture(tmp_path)
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "<img ",
            '<img data-evidence-status="reference-only" ',
            1,
        ),
        encoding="utf-8",
    )
    assert_fails(run_gate(tmp_path), "reference-only image")


def test_allows_approved_reusable_source_download(tmp_path):
    package = create_release_fixture(tmp_path)
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<a href="screenshots/assisted/01-case.png" download>'
            "Download original</a></main>",
        ),
        encoding="utf-8",
    )
    result = run_gate(tmp_path)
    assert result["passed"] is True, result["failures"]
    assert result["metrics"]["learner_screenshot_links"] == 1


def test_rejects_unapproved_screenshot_download_link(tmp_path):
    package = create_release_fixture(tmp_path)
    write(package / "screenshots" / "assisted" / "unapproved.png", PNG_1X1)
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<a href="screenshots/assisted/unapproved.png" download>'
            "Download unapproved</a></main>",
        ),
        encoding="utf-8",
    )
    assert_fails(
        run_gate(tmp_path),
        "learner-linked or displayed screenshots are not approved",
    )


def test_rejects_css_background_screenshot_leakage(tmp_path):
    package = create_release_fixture(tmp_path)
    write(
        package / "screenshots" / "assisted" / "css-unapproved.png",
        PNG_1X1,
    )
    write(
        package / "screenshots" / "assisted" / "inline-unapproved.png",
        PNG_1X1,
    )
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<style>.leak{background:url("screenshots/assisted/'
            'css-unapproved.png")}</style>'
            '<div style="background-image:url(screenshots/assisted/'
            'inline-unapproved.png)">Leak</div></main>',
        ),
        encoding="utf-8",
    )

    result = run_gate(tmp_path)
    assert_fails(
        result,
        "learner-linked or displayed screenshots are not approved",
    )
    assert any("css-unapproved.png" in item for item in result["failures"])
    assert any("inline-unapproved.png" in item for item in result["failures"])


def test_rejects_source_srcset_screenshot_leakage(tmp_path):
    package = create_release_fixture(tmp_path)
    write(
        package / "screenshots" / "assisted" / "srcset-unapproved.png",
        PNG_1X1,
    )
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<picture><source srcset="screenshots/assisted/'
            'srcset-unapproved.png 1x"></picture></main>',
        ),
        encoding="utf-8",
    )

    assert_fails(
        run_gate(tmp_path),
        "learner-linked or displayed screenshots are not approved",
    )


def test_rejects_svg_xlink_screenshot_leakage(tmp_path):
    package = create_release_fixture(tmp_path)
    write(
        package / "screenshots" / "assisted" / "xlink-unapproved.png",
        PNG_1X1,
    )
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<svg><image xlink:href="screenshots/assisted/'
            'xlink-unapproved.png"></image></svg></main>',
        ),
        encoding="utf-8",
    )

    assert_fails(run_gate(tmp_path), "xlink-unapproved.png")


def test_rejects_object_data_screenshot_leakage(tmp_path):
    package = create_release_fixture(tmp_path)
    write(
        package / "screenshots" / "assisted" / "object-unapproved.png",
        PNG_1X1,
    )
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<object data="screenshots/assisted/object-unapproved.png">'
            "</object></main>",
        ),
        encoding="utf-8",
    )

    assert_fails(
        run_gate(tmp_path),
        "learner-linked or displayed screenshots are not approved",
    )


def test_rejects_reshoot_source_download_link(tmp_path):
    package = create_release_fixture(tmp_path)
    quest = package / "quest.html"
    quest.write_text(
        quest.read_text(encoding="utf-8").replace(
            "</main>",
            '<a href="screenshots/assisted/reshoot.png" download>'
            "Download withheld</a></main>",
        ),
        encoding="utf-8",
    )
    assert_fails(
        run_gate(tmp_path),
        "learner pages link or display reshoot-required screenshots",
    )


def test_repository_requires_exactly_51_advertised_slugs(monkeypatch, tmp_path):
    slugs = [f"workshop-{index:02d}" for index in range(50)]
    monkeypatch.setattr(
        audit.course,
        "course_scope",
        lambda root, failures: (slugs, []),
    )
    monkeypatch.setattr(
        audit.course,
        "audit_repository",
        lambda root: {
            "total": 50,
            "solutions": [
                {"slug": slug, "passed": True, "failures": []}
                for slug in slugs
            ]
        },
    )
    monkeypatch.setattr(
        audit,
        "audit_workshop",
        lambda root, slug, base: {
            "slug": slug,
            "passed": True,
            "failures": [],
            "metrics": {
                "locked_cases": 0,
                "locked_cases_covered": 0,
                "captures": 10,
                "reusable": 10,
                "hard_reusable": 5,
                "learner_images": 0,
                "reference_only_images": 0,
            },
        },
    )

    report = audit.audit_repository(tmp_path)

    assert report["totals"]["workshops"] == 50
    assert report["totals"]["failed"] == 50
    assert report["global_failures"] == [
        "advertised workshop count 50 != 51",
        "base course audit did not resolve exactly 51 workshops",
    ]
