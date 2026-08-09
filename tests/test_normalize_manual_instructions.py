import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "normalize_manual_instructions.py"


def load_module():
    spec = importlib.util.spec_from_file_location("normalize_manual_instructions", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_section_preserves_case_operations_and_anchors():
    module = load_module()
    section = module.render_section(
        [
            {
                "id": "EX-01",
                "operation": "evidence_review",
                "must_include": ["Record A", "Evidence boundary"],
            }
        ]
    )
    assert "`EX-01` / `evidence_review`" in section
    assert "`Record A`, `Evidence boundary`" in section
    assert "Do not narrate internal retrieval" in section


def test_normalize_is_idempotent(tmp_path):
    module = load_module()
    instructions = (
        tmp_path
        / "solutions"
        / "example"
        / "manual"
        / "GLOBAL-INSTRUCTIONS.md"
    )
    instructions.parent.mkdir(parents=True)
    instructions.write_text("# Role\n\nSynthetic only.\n", encoding="utf-8")
    cases = tmp_path / "tests" / "demo_cases" / "example.json"
    cases.parent.mkdir(parents=True)
    cases.write_text(
        json.dumps(
            {
                "cases": [
                    {
                        "id": "EX-01",
                        "operation": "review",
                        "must_include": ["Record A"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    catalog = tmp_path / "solutions" / "catalog.json"
    catalog.write_text(
        json.dumps({"solutions": {"@aibast-agents-library/example": {}}}),
        encoding="utf-8",
    )

    assert module.normalize(tmp_path) == ["example"]
    first = instructions.read_text(encoding="utf-8")
    assert module.normalize(tmp_path) == []
    assert instructions.read_text(encoding="utf-8") == first
