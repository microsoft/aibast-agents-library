import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RAW = "https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/"
CANONICAL_FOLDER = "https://github.com/microsoft/aibast-agents-library/tree/main/"
FORBIDDEN_PROMOTION_TEXT = (
    "github.com/kody-w/",
    "raw.githubusercontent.com/kody-w/",
    "kody-w.github.io",
    "kodyw.com",
)


def test_microsoft_facing_pages_do_not_publish_personal_fork_identity():
    pages = list(ROOT.glob("*.html"))
    for directory in ("docs", "reports", "solutions"):
        pages.extend((ROOT / directory).rglob("*.html"))
    pages.extend((ROOT / "beta").glob("*.html"))
    pages.append(ROOT / "README.md")
    assert pages
    failures = []
    for page in sorted(set(pages)):
        text = page.read_text(encoding="utf-8").lower()
        for forbidden in FORBIDDEN_PROMOTION_TEXT:
            if forbidden in text:
                failures.append(f"{page.relative_to(ROOT)}: {forbidden}")
    assert failures == [], "\n".join(failures)


def test_explicit_workshop_delivery_recipes_target_microsoft():
    checked = []
    for path in sorted((ROOT / "solutions").glob("*/deployment.json")):
        deployment = json.loads(path.read_text(encoding="utf-8"))
        bundle = deployment.get("source_bundle") or {}
        if not bundle:
            continue
        checked.append(path)
        if "raw_base" in bundle:
            assert bundle["raw_base"] == CANONICAL_RAW, path
        if "github_folder" in bundle:
            assert bundle["github_folder"] == (
                f"{CANONICAL_FOLDER}solutions/{path.parent.name}"
            ), path
    assert checked


def test_immutable_delivery_aliases_keep_content_addressed_microsoft_urls():
    for slug, filename in (
        ("procurement-agent", "manual-inputs-r3.json"),
        ("prior-authorization", "manual-inputs-r4.json"),
    ):
        path = ROOT / "solutions" / slug / "evals" / filename
        inventory = json.loads(path.read_text(encoding="utf-8"))
        for item in inventory["inputs"]:
            assert item["public_url"] == (
                "https://raw.githubusercontent.com/microsoft/aibast-agents-library/"
                f"{inventory['source_commit']}/{item['path']}"
            )
