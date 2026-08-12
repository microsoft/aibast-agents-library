import json
from pathlib import Path

from PIL import Image

from tools import normalize_workshop_visual_evidence as normalize


SLUG = "fixture-workshop"


def write_image(path: Path, color: tuple[int, int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGBA", (20, 20), color).save(path)


def image_paths(slug: str, mode: str, name: str) -> tuple[str, str]:
    directory = "assisted" if mode == "easy" else "manual"
    source = f"solutions/{slug}/screenshots/{directory}/{name}.png"
    annotated = (
        f"solutions/{slug}/screenshots/{directory}/annotated/{name}.png"
    )
    return source, annotated


def valid_capture(
    root: Path,
    *,
    capture_id: str,
    mode: str,
    name: str,
    color_index: int,
    case_id: str | None = None,
    step: int | None = None,
    status: str = "reusable",
) -> dict:
    source, annotated = image_paths(SLUG, mode, name)
    write_image(
        root / source,
        (color_index, color_index * 2 % 256, color_index * 3 % 256, 255),
    )
    write_image(
        root / annotated,
        (
            color_index,
            color_index * 2 % 256,
            (color_index * 3 + 1) % 256,
            255,
        ),
    )
    capture = {
        "id": capture_id,
        "mode": mode,
        "source": source,
        "annotated": annotated,
        "status": status,
        "visible_anchors": [capture_id],
        "boxes": [{"x": 1, "y": 1, "width": 10, "height": 10}],
    }
    if case_id:
        capture["case_id"] = case_id
    if step:
        capture["step"] = step
    return capture


def create_package(
    root: Path,
    captures: list[dict],
    *,
    assisted_frames: list[dict],
    manual_frames: list[dict],
    release_review: bool = False,
) -> Path:
    package = root / "solutions" / SLUG
    for directory, frames in (
        ("assisted", assisted_frames),
        ("manual", manual_frames),
    ):
        path = package / "screenshots" / directory / "browserfilm.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema": "rapp-browserfilm/1.0",
                    "width": 20,
                    "height": 20,
                    "frames": frames,
                }
            ),
            encoding="utf-8",
        )
    cases = root / "tests" / "demo_cases" / f"{SLUG}.json"
    cases.parent.mkdir(parents=True, exist_ok=True)
    cases.write_text(
        json.dumps({"cases": [{"case_id": "CASE-01"}]}), encoding="utf-8"
    )
    document = {
        "schema": "aibast-visual-checkpoints/1.0",
        "summary": {"incorrect": True},
        "captures": captures,
    }
    if release_review:
        document["release_review"] = {
            "status": "approved",
            "reviewer": f"workshop-builder:{SLUG}",
            "reviewed_at": "2026-08-09T20:00:00Z",
            "method": "Independent review",
            "notes": "All source-side requirements passed.",
        }
    path = package / "evals" / "visual-checkpoints.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_reshoot_capture_is_never_promoted(tmp_path):
    capture = valid_capture(
        tmp_path,
        capture_id="easy-case-01",
        mode="easy",
        name="01-case",
        color_index=10,
        case_id="CASE-01",
        status="reshoot_required",
    )
    capture["reason"] = "The required state was not visually established."
    path = create_package(
        tmp_path,
        [capture],
        assisted_frames=[{"file": "01-case.png", "label": "Pass CASE-01"}],
        manual_frames=[],
    )

    normalize.normalize_workshop(SLUG, root=tmp_path)

    result = read(path)["captures"][0]
    assert result["status"] == "reshoot_required"
    assert "annotated" not in result


def test_corrects_objective_browserfilm_binding_and_summary(tmp_path):
    capture = valid_capture(
        tmp_path,
        capture_id="wrong-binding",
        mode="hard",
        name="01-preview",
        color_index=20,
        case_id="WRONG-99",
        step=99,
    )
    capture["mode"] = "easy"
    path = create_package(
        tmp_path,
        [capture],
        assisted_frames=[],
        manual_frames=[
            {"file": "01-preview.png", "label": "Pass CASE-01 in Preview"}
        ],
    )

    normalize.normalize_workshop(SLUG, root=tmp_path)

    document = read(path)
    result = document["captures"][0]
    assert result["mode"] == "hard"
    assert result["step"] == 1
    assert result["case_id"] == "CASE-01"
    assert document["summary"] == {
        "total_existing_captures": 1,
        "reusable": 1,
        "reshoot_required": 0,
    }


def test_demotes_invalid_annotation_without_synthesizing_fix(tmp_path):
    capture = valid_capture(
        tmp_path,
        capture_id="easy-case-01",
        mode="easy",
        name="01-case",
        color_index=30,
        case_id="CASE-01",
    )
    (tmp_path / capture["annotated"]).write_bytes(
        (tmp_path / capture["source"]).read_bytes()
    )
    path = create_package(
        tmp_path,
        [capture],
        assisted_frames=[{"file": "01-case.png", "label": "Pass CASE-01"}],
        manual_frames=[],
    )

    normalize.normalize_workshop(SLUG, root=tmp_path)

    result = read(path)["captures"][0]
    assert result["status"] == "reshoot_required"
    assert "pixel-identical" in result["reason"]
    assert "annotated" not in result
    assert "visible_anchors" not in result
    assert "boxes" not in result


def test_duplicate_content_keeps_deterministic_best_capture(tmp_path):
    easy = valid_capture(
        tmp_path,
        capture_id="easy-case-01",
        mode="easy",
        name="01-case",
        color_index=40,
        case_id="CASE-01",
    )
    hard = valid_capture(
        tmp_path,
        capture_id="hard-step-01",
        mode="hard",
        name="01-preview",
        color_index=50,
        case_id="CASE-01",
        step=1,
    )
    (tmp_path / hard["source"]).write_bytes(
        (tmp_path / easy["source"]).read_bytes()
    )
    path = create_package(
        tmp_path,
        [hard, easy],
        assisted_frames=[{"file": "01-case.png", "label": "Pass CASE-01"}],
        manual_frames=[
            {"file": "01-preview.png", "label": "Pass CASE-01 in Preview"}
        ],
    )

    normalize.normalize_workshop(SLUG, root=tmp_path)

    captures = {item["id"]: item for item in read(path)["captures"]}
    assert captures["easy-case-01"]["status"] == "reusable"
    assert captures["hard-step-01"]["status"] == "reshoot_required"
    assert "retained capture easy-case-01" in captures["hard-step-01"]["reason"]


def test_removes_release_review_when_coverage_falls(tmp_path):
    captures = [
        valid_capture(
            tmp_path,
            capture_id="easy-case-01",
            mode="easy",
            name="01-case",
            color_index=60,
            case_id="CASE-01",
        ),
        valid_capture(
            tmp_path,
            capture_id="easy-confirm-draft",
            mode="easy",
            name="02-draft",
            color_index=61,
        ),
    ]
    assisted_frames = [
        {"file": "01-case.png", "label": "Pass CASE-01"},
        {"file": "02-draft.png", "label": "Confirm Draft"},
    ]
    manual_frames = []
    for step in range(1, 6):
        captures.append(
            valid_capture(
                tmp_path,
                capture_id=f"hard-step-{step:02d}",
                mode="hard",
                name=f"{step:02d}-step",
                color_index=61 + step,
                step=step,
            )
        )
        manual_frames.append(
            {"file": f"{step:02d}-step.png", "label": f"Manual step {step}"}
        )
    for index in range(3):
        case_id = f"EXTRA-{index + 1:02d}"
        captures.append(
            valid_capture(
                tmp_path,
                capture_id=f"easy-extra-{index + 1:02d}",
                mode="easy",
                name=f"{index + 3:02d}-extra",
                color_index=70 + index,
                case_id=case_id,
            )
        )
        assisted_frames.append(
            {
                "file": f"{index + 3:02d}-extra.png",
                "label": f"Pass {case_id}",
            }
        )
    locked = captures[0]
    (tmp_path / locked["annotated"]).write_bytes(
        (tmp_path / locked["source"]).read_bytes()
    )
    path = create_package(
        tmp_path,
        captures,
        assisted_frames=assisted_frames,
        manual_frames=manual_frames,
        release_review=True,
    )

    normalize.normalize_workshop(SLUG, root=tmp_path)

    document = read(path)
    assert document["summary"]["reusable"] == 9
    assert "release_review" not in document
