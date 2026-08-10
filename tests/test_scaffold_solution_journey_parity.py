import json
import re
from pathlib import Path

from tools import scaffold_solution_journey as scaffold


ROOT = Path(__file__).resolve().parents[1]


def advertised_slugs():
    catalog = json.loads(
        (ROOT / "solutions" / "catalog.json").read_text(encoding="utf-8")
    )["solutions"]
    registry = json.loads(
        (ROOT / "registry.json").read_text(encoding="utf-8")
    )["agents"]
    registry_by_name = {
        row["name"]: row
        for row in registry
        if row.get("_solution")
    }
    return sorted({
        registry_by_name[name]["_solution"]["package"]["slug"]
        for name in catalog
    })


def test_all_advertised_workshops_match_the_authoritative_scaffold():
    for slug in advertised_slugs():
        context = scaffold.load_context(
            ROOT,
            slug,
            allow_pending=False,
            raw_base=scaffold.DEFAULT_RAW_BASE,
        )
        resources, outputs = scaffold.generated_outputs(context)

        for path, expected in outputs.items():
            assert path.read_text(encoding="utf-8") == (
                scaffold.normalize_generated_text(expected)
            ), f"{slug}: stale generated file {path.relative_to(ROOT)}"

        readme = (context.package / "README.md").read_text(encoding="utf-8")
        match = re.search(
            re.escape(scaffold.README_START)
            + r".*?"
            + re.escape(scaffold.README_END),
            readme,
            re.DOTALL,
        )
        assert match, f"{slug}: generated README block is missing"
        assert match.group(0) == scaffold.readme_block(context, resources)
