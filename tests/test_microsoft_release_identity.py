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
        # Superseded by the 2026-10-08 re-shoot; kept as dated history.
        path = ROOT / "solutions" / slug / "evals" / "history" / "2026-10-08-pre-reshoot" / filename
        inventory = json.loads(path.read_text(encoding="utf-8"))
        for item in inventory["inputs"]:
            assert item["public_url"] == (
                "https://raw.githubusercontent.com/microsoft/aibast-agents-library/"
                f"{inventory['source_commit']}/{item['path']}"
            )


# Files that may still name personal repositories, each for a stated reason. Everything else in the repository must
# reach only Microsoft-hosted sources, so the library runs with no dependency on a personal repository.
PERSONAL_URL_ALLOWED = {
    # Kernel files arrive unchanged from the Grail through kernel-sync pull requests and are never edited here.
    "rapp_brainstem/": "kernel, synced from the Grail",
    "rapp/KERNEL-DRIFT.md": "kernel provenance",
    "rapp/GRAIL-SPECIES.json": "kernel provenance",
    # True provenance and licence notices name their real upstream source.
    "docs/vault/": "RAPP/1 vault provenance and licence notice",
    "tools/rapp1/SOURCE.json": "RAPP/1 corpus provenance",
    "community_rapp/project/SOURCE.json": "CommunityRAPP provenance",
    "beta/docs/twins/COMPLIANCE.md": "names the canon the twins design is checked against",
    # Build tools read public upstreams at build time only; nothing they write fetches from them.
    "tools/mirror_rapp_store.py": "upstream catalog for the hosted store copy",
    "tools/build_rapp1_vault.py": "the forbidden-text list itself",
    "scripts/": "metrics builders read public traffic and catalog data",
    # Dated records and collected telemetry.
    "docs/RELEASES.md": "release ledger links to the staging runs that gated each release",
    "docs/MS-RAPP-HOSTING-AUDIT.md": "the audit that lists what moved",
    "reports/": "collected traffic data",
    "state/": "collected metrics snapshots",
    # Tests use these strings as fixtures or as the very patterns they block.
    "tests/": "fixtures and guard patterns",
    "beta/tests/": "fixtures",
}


def test_runtime_files_do_not_depend_on_personal_repositories():
    import subprocess

    pattern = "|".join(p.replace(".", r"\.") for p in FORBIDDEN_PROMOTION_TEXT)
    found = subprocess.run(
        ["git", "grep", "-IliE", pattern], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout.split()
    assert found, "the scan should see the allowed files; an empty result means git grep did not run"
    failures = [
        path for path in found
        if not any(path == allowed or (allowed.endswith("/") and path.startswith(allowed))
                   for allowed in PERSONAL_URL_ALLOWED)
    ]
    assert failures == [], (
        "These files link to a personal repository. Point them at microsoft/aibast-agents-library, or add the file "
        "to PERSONAL_URL_ALLOWED with the reason it must keep the link:\n" + "\n".join(failures)
    )
