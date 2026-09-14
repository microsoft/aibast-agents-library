import hashlib
import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HISTORY = "evals/history/2026-09-10-upstream"
UPSTREAM = "0783cc219124b4a6dff1c41f0c5eb5c285ae9436"
STAGING = "c2e2be939273e912aa63a8237f48776ba33ff73a"
MERGE_BASE = "2cc050754d237d7c13a9f66feff8da2b9deb2230"
SNAPSHOTS = {
    "fs-customer-onboarding": {
        "upstream": "8e4956cfe119b75fe0c2c7ccfb950deb9998f6608b985578f68298e1f85e143e",
        "current": "e20ea433f5bf578856bd5afa9fab255fec8d42ccf6d4b270f3145554a30c263f",
        "corrected_ids": {f"hard-step-{step:02}" for step in range(5, 13)},
    },
    "portfolio-rebalancing": {
        "upstream": "4e196cf7f3cdb12eeb3a115c731b5cdc7b022ee14a9f14cbd9ea4d4e7cdefc10",
        "current": "80b60d5abfdaab6a738c51a67bb763625884b93cc381cc36a88e82fe344017a0",
        "corrected_ids": {"easy-prb-04"},
    },
    "procurement-agent": {
        "upstream": "a7204c3005af4c333785051f13d7d3fcdc4fcc814686df95e2e91f2ae419ee35",
        "current": "b6b59db7b7ab98ba227db39a7aff525c58d05c4e6c89d4f5fc4d466cd80a0f81",
        "corrected_ids": {"easy-proc-03", "hard-step-16", "hard-step-17"},
    },
}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify_file(record):
    data = (ROOT / record["path"]).read_bytes()
    assert len(data) == record["bytes"]
    assert digest(data) == record["sha256"]
    return data


@pytest.mark.parametrize("slug", SNAPSHOTS)
def test_upstream_annotations_cannot_change_current_acceptance(slug):
    package = ROOT / "solutions" / slug
    visual = read(package / "evals/visual-checkpoints.json")
    reference = visual.pop("historical_annotation_reference")
    assert reference["status"] == "historical_only"
    assert reference["annotation_date"] == "2026-09-10"
    assert reference["index"] == f"{HISTORY}/index.json"
    index = read(package / reference["index"])
    assert index["status"] == "historical_only"
    assert index["new_native_acceptance"] == {
        "accepted_components": 0, "accepted_cases": 0, "reviewed_images": 0,
    }
    assert index["source_commits"] == {
        "base": MERGE_BASE, "staging": STAGING, "upstream": UPSTREAM,
    }
    projection = digest(json.dumps(visual, sort_keys=True).encode())
    assert projection == index["current_visual_projection"]["sha256"]
    assert projection == SNAPSHOTS[slug]["current"]
    for capture in visual["captures"]:
        if capture["status"] == "reshoot_required":
            assert capture["reason"]
            assert "annotated" not in capture
            assert "visible_anchors" not in capture
        else:
            assert slug == "portfolio-rebalancing"
            assert capture["mode"] == "hard"
            assert capture["build_revision"] == "repaired-r5"
            assert "/manual/repaired-r5/" in capture["annotated"]
    if slug != "portfolio-rebalancing":
        assert visual["summary"]["reusable"] == 0
        assert visual["summary"]["reshoot_required"] == len(visual["captures"])


@pytest.mark.parametrize("slug", SNAPSHOTS)
def test_both_annotation_versions_have_complete_hash_verified_path_resolution(slug):
    package = ROOT / "solutions" / slug
    index = read(package / HISTORY / "index.json")
    data = verify_file(index["upstream_visual_metadata"])
    assert digest(data) == SNAPSHOTS[slug]["upstream"]
    incoming = read(ROOT / index["upstream_visual_metadata"]["path"])
    captures = {item["id"]: item for item in incoming["captures"]}
    archived = {item["original_path"]: item for item in index["archived_annotations"]}
    assert {item["capture_id"] for item in archived.values()} == SNAPSHOTS[slug]["corrected_ids"]
    assert len(archived) == len(SNAPSHOTS[slug]["corrected_ids"])
    for original, record in archived.items():
        capture = captures[record["capture_id"]]
        assert capture["annotated"] == original
        assert capture["boxes"] == record["upstream_boxes"]
        assert capture["note"] == record["upstream_note"]
        assert "2026-09-10" in record["upstream_note"]
        assert f"/{HISTORY}/screenshots/" in record["path"]
        corrected = verify_file(record)
        retained = (ROOT / original).read_bytes()
        assert corrected != retained
        assert digest(retained) == record["retained_original_sha256"]
        assert digest(retained) == index["retained_original_media_sha256"][original]
        assert corrected[:8] == b"\x89PNG\r\n\x1a\n"
    references = {
        capture[field]
        for capture in incoming["captures"]
        for field in ("source", "annotated")
        if field in capture
    }
    unchanged = index["unchanged_upstream_media_sha256"]
    assert references == set(archived) | set(unchanged)
    assert references == set(index["retained_original_media_sha256"])
    assert not set(archived) & set(unchanged)
    for original, expected in unchanged.items():
        assert digest((ROOT / original).read_bytes()) == expected


def test_corrected_geometry_is_archived_not_rebound_to_original_images():
    expected = {
        ("fs-customer-onboarding", "hard-step-12"): [(1024, 357, 374, 156)],
        ("portfolio-rebalancing", "easy-prb-04"): [(281, 366, 945, 305)],
        ("procurement-agent", "hard-step-16"): [(286, 210, 940, 74)],
        ("procurement-agent", "hard-step-17"): [(286, 123, 940, 84), (286, 220, 940, 110)],
    }
    for (slug, capture_id), boxes in expected.items():
        index = read(ROOT / "solutions" / slug / HISTORY / "index.json")
        record = next(row for row in index["archived_annotations"] if row["capture_id"] == capture_id)
        actual = {
            tuple(box[key] for key in ("x", "y", "width", "height"))
            for box in record["upstream_boxes"]
        }
        assert set(boxes) <= actual
    current = read(ROOT / "solutions/procurement-agent/evals/visual-checkpoints.json")
    row = next(row for row in current["captures"] if row["id"] == "hard-step-16")
    assert row["historical_boxes"][0]["y"] == 207
    assert row["historical_boxes"][0]["height"] == 84
    current = read(ROOT / "solutions/fs-customer-onboarding/evals/visual-checkpoints.json")
    row = next(row for row in current["captures"] if row["id"] == "hard-step-12")
    assert row["historical_boxes"][-1]["y"] == 323
    assert row["historical_boxes"][-1]["height"] == 190


def test_procurement_candidate_keeps_seven_inputs_and_all_august_bytes_without_acceptance():
    package = ROOT / "solutions/procurement-agent"
    inventory = read(package / "evals/manual-inputs-r3.json")
    assert inventory["build_revision"] == "grounding-r3"
    assert len(inventory["inputs"]) == 7
    for record in inventory["inputs"]:
        verify_file(record)
    verify_file(inventory["locked_cases"])
    evidence = read(package / "evals/manual-build-evidence.json")
    regression = evidence["native_regression"]
    assert evidence["status"] == "reshoot_required"
    assert regression["status"] == "blocked"
    assert regression["accepted_components"] == regression["cases_run"] == regression["passed"] == 0
    assert regression["older_passes_carried_forward"] is False
    assert regression["total"] == len(evidence["canonical_preview"]) == 4
    assert all(case["passed"] is None and case["status"] == "reshoot_required"
               for case in evidence["canonical_preview"])
    history = read(package / "evals/history/2026-08/index.json")
    assert len(history["files"]) == 8
    for record in history["files"]:
        verify_file({**record, "path": record["archived_path"]})
    assert len(history["media_sha256"]) == 41
    for original, expected in history["media_sha256"].items():
        assert digest((ROOT / original).read_bytes()) == expected
    for mode in ("manual", "assisted"):
        film = read(package / "screenshots" / mode / "browserfilm.json")
        assert all(frame["captured"] is False for frame in film["frames"])


def test_portfolio_skill_name_fix_is_already_satisfied_by_exact_frozen_r5_payload():
    package = ROOT / "solutions/portfolio-rebalancing"
    index = read(package / HISTORY / "index.json")
    resolution = index["instruction_resolution"]
    assert resolution["native_payload_changed"] is False
    assert resolution["new_acceptance_claimed"] is False
    frozen = verify_file(resolution["frozen_current_instructions"])
    assert len(frozen) == 5154
    assert digest(frozen) == "b9e120836fe330ca5c79f9ffe0336e448671eecec3f70550c8a58164226e6070"
    incoming = verify_file(resolution["upstream_instructions"]).decode()
    names = re.findall(r"uses skill `([^`]+)`", incoming)
    actual = {
        re.search(r"^name: (.+)$", path.read_text(), re.MULTILINE)[1]
        for path in (package / "manual/skills").glob("*/SKILL.md")
    }
    assert len(names) == 6 and set(names) == actual
    assert names == resolution["matching_skill_names"]
    assert all(f": {name}." in frozen.decode() for name in names)
    assert "locked-preview-anchors" not in frozen.decode()
    inventory = read(package / "evals/manual-inputs-r5.json")
    assert len(inventory["inputs"]) == 9
    for record in inventory["inputs"]:
        verify_file(record)
    visual = read(package / "evals/visual-checkpoints.json")
    assert visual["summary"]["current_native_cases_passed"] == 6
    assert visual["summary"]["reusable"] == 14
    assert visual["summary"]["reviewed_manual_images"] == 13
    assert visual["strict_coverage"]["open_student_steps"] == [1, *range(7, 14)]
    assert visual["release_review"]["certified"] is False


def test_care_gap_retains_repaired_controls_and_adds_only_the_real_skill_routing_guard():
    package = ROOT / "solutions/care-gap-closure"
    review = read(package / HISTORY / "index.json")
    files = {name: verify_file(record) for name, record in review["source_files"].items()}
    assert digest(files["staging"]) == "d37f68ac11251886bd825e1842724614b9f0d33a36f4e9cc3d333243bd59af8a"
    assert digest(files["upstream"]) == "f5b06e97bee7cc70b5203a6c953abcbb2446c95ed4e4b7d412215310f054e6a0"
    marker = b"<!-- locked-preview-anchors:start -->"
    assert files["resolved"].split(marker)[0] == files["staging"].split(marker)[0]
    assert files["resolved"].split(marker)[1] == files["upstream"].split(marker)[1]
    policy = files["resolved"].decode()
    assert "SYN-COL has 182 records, SYN-BCS has 108, and SYN-CDC has 53" in policy
    assert "after one retry in the same turn, say so honestly and stop" in policy
    assert "a response with no real citation is not acceptable output" in policy
    assert "These phrases are acceptance evidence" not in policy
    assert set(re.findall(r"uses skill `([^`]+)`", policy)) == {
        re.search(r"^name: (.+)$", path.read_text(), re.MULTILINE)[1]
        for path in (package / "manual/skills").glob("*/SKILL.md")
    }
    cases = read(ROOT / "tests/demo_cases/care-gap-closure.json")["cases"]
    assert cases[0]["must_include"] == [
        "SYN-COL — 182 records", "Records requiring evidence review",
    ]
    assert cases[3]["must_include"] == ["SYN-BCS", "source-recorded closed"]
    evidence = read(package / "evals/manual-build-evidence.json")
    assert evidence["status"] == "reshoot_required"
    assert evidence["manual_components"]["global_instructions"]["confirmed"] is False
    assert evidence["canonical_preview"][0]["passed"] is None
    assert review["status"] == "source_only_native_pending"
    assert review["native_payload_changed"] is True
    assert review["accepted_current_native_cases"] == 0
    assert review["older_passes_carried_forward"] is False
    assert review["native_operations_performed"] is False


@pytest.mark.parametrize(("slug", "current_hash", "upstream_hash"), [
    (
        "procurement-agent",
        "f3ef5a14a3ae52acfdb0fb40a7d7849560ddbb4f2262ce460f23f1ca22f768d2",
        "6c78e4dfd539a86c10f83804c9879a73b983b3294ffae5cca86d9eafbcfde002",
    ),
    (
        "fs-customer-onboarding",
        "40550c9b62c7649028bdd9e3fd6fd3619434d563d1cf39320605014fa328ee26",
        "27e5a8884655ff6feb1fea73863bd2dd5083e2e5dc6d67b78c6379469506744c",
    ),
])
def test_incoming_policy_improvements_cannot_replace_pinned_source_identities(
    slug, current_hash, upstream_hash,
):
    package = ROOT / "solutions" / slug
    index = read(package / HISTORY / "index.json")
    resolution = index["instruction_resolution"]
    current = verify_file(resolution["preserved_current_instructions"])
    incoming = verify_file(resolution["upstream_instructions"])
    assert digest(current) == current_hash
    assert digest(incoming) == upstream_hash
    assert incoming != current
    assert resolution["preserved_current_instructions"]["restored_from"] == STAGING
    assert resolution["upstream_instructions"]["source_commit"] == UPSTREAM
    assert resolution["current_payload_changed"] is False
    assert resolution["incoming_policy_is_current"] is False
    assert resolution["passes_transferred_to_incoming_policy"] is False
    assert resolution["payload_identity_transferred_to_incoming_policy"] is False
    assert resolution["new_acceptance_claimed"] is False
    names = re.findall(r"uses skill `([^`]+)`", incoming.decode())
    actual = {
        re.search(r"^name: (.+)$", path.read_text(), re.MULTILINE)[1]
        for path in (package / "manual/skills").glob("*/SKILL.md")
    }
    assert len(names) == 4 and set(names) == actual
    assert names == resolution["upstream_skill_routing_names"]
    assert "after one retry in the same turn" in incoming.decode()
    assert "a response with no real citation is not acceptable output" in incoming.decode()
    identity = resolution["current_source_identity"]
    assert identity["instruction_sha256"] == current_hash
    if slug == "procurement-agent":
        inventory = read(package / "evals/manual-inputs-r3.json")
        assert identity["source_commit"] == inventory["source_commit"]
        assert identity["build_revision"] == inventory["build_revision"] == "grounding-r3"
        assert identity["input_count"] == len(inventory["inputs"]) == 7
        assert identity["accepted_native_components"] == identity["accepted_native_cases"] == 0
        for record in inventory["inputs"]:
            verify_file(record)
    else:
        review = read(package / "evals/manual-pilot-review.json")
        assert identity["tested_source_commit"] == review["tested_source_commit"]
        assert identity["reviewed_on"] == review["reviewed_on"] == "2026-09-12"
        assert identity["status"] == review["status"] == "blocked"
        assert identity["certified"] is review["certified"] is False
        for record in review["promoted_manual_sources"]:
            assert digest((ROOT / record["path"]).read_bytes()) == record["packaged_sha256"]
        policy = next(
            row for row in review["promoted_manual_sources"]
            if row["path"].endswith("/GLOBAL-INSTRUCTIONS.md")
        )
        assert policy["native_payload_sha256"] == policy["packaged_sha256"] == current_hash
