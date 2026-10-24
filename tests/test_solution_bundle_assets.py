import json
import re
import zipfile
from pathlib import Path

from tools import build_solution_export, solution_bundle_assets


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/solution-bundle-assets.yml"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def fixture_package(root, slug="demo"):
    package = root / "solutions" / slug
    write(package / "README.md", "# Demo\n")
    write(package / "quest.html", "<html><body>quest</body></html>\n")
    write(package / "exports" / f"{slug}-copilot-studio-solution.zip", b"native")
    manifest = package / "export-manifest.json"
    write(manifest, json.dumps({
        "bundle": {"path": f"solutions/{slug}/exports/{slug}-source.zip"},
        "files": [],
    }))
    return manifest


def test_every_solution_declares_one_uniquely_named_bundle_asset():
    rows = solution_bundle_assets.bundle_manifests(ROOT)
    manifests = sorted((ROOT / "solutions").glob("*/export-manifest.json"))
    assert len(rows) == len(manifests) == 69
    for name, manifest in rows:
        assert name == f"{manifest.parent.name}-source.zip"
    assert len({name for name, _ in rows}) == len(rows)


def test_bundle_is_reproducible_and_never_packages_its_declared_path(tmp_path, monkeypatch):
    monkeypatch.setattr(build_solution_export, "ROOT", tmp_path)
    manifest = fixture_package(tmp_path)
    declared = tmp_path / "solutions/demo/exports/demo-source.zip"
    write(declared, b"stale committed bundle")
    first = tmp_path / "out-a" / "demo-source.zip"
    second = tmp_path / "out-b" / "demo-source.zip"

    build_solution_export.build(manifest, first)
    (tmp_path / "solutions/demo/README.md").touch()  # new mtime, same content
    build_solution_export.build(manifest, second)

    assert first.read_bytes() == second.read_bytes()
    assert declared.read_bytes() == b"stale committed bundle"
    with zipfile.ZipFile(first) as archive:
        names = archive.namelist()
        assert "solutions/demo/exports/demo-source.zip" not in names
        assert "solutions/demo/README.md" in names
        assert {info.date_time for info in archive.infolist()} == {
            build_solution_export.FIXED_DATE_TIME
        }


def test_build_all_writes_every_asset_and_checksums(tmp_path, monkeypatch):
    monkeypatch.setattr(build_solution_export, "ROOT", tmp_path)
    fixture_package(tmp_path, "alpha")
    fixture_package(tmp_path, "beta")
    out = tmp_path / "dist"
    sums = solution_bundle_assets.build_all(out, tmp_path)
    assert [name for _digest, name in sums] == ["alpha-source.zip", "beta-source.zip"]
    lines = (out / solution_bundle_assets.SUMS_NAME).read_text().splitlines()
    for line, (digest, name) in zip(lines, sums):
        assert line == f"{digest}  {name}"
        assert solution_bundle_assets.sha256_file(out / name) == digest


def test_bundle_name_must_match_its_solution_folder(tmp_path):
    manifest = fixture_package(tmp_path, "alpha")
    document = json.loads(manifest.read_text())
    document["bundle"]["path"] = "solutions/alpha/exports/other-source.zip"
    write(manifest, json.dumps(document))
    try:
        solution_bundle_assets.bundle_manifests(tmp_path)
    except ValueError as error:
        assert "alpha-source.zip" in str(error)
    else:
        raise AssertionError("mismatched bundle name was accepted")


def test_compare_accepts_recompression_but_not_content_drift(tmp_path):
    def archive(path, payload, method):
        with zipfile.ZipFile(path, "w") as handle:
            info = zipfile.ZipInfo("solutions/demo/README.md", date_time=build_solution_export.FIXED_DATE_TIME)
            info.compress_type = method
            handle.writestr(info, payload)
        return path

    payload = b"same content " * 500
    built = archive(tmp_path / "built.zip", payload, zipfile.ZIP_DEFLATED)
    copy = tmp_path / "copy.zip"
    copy.write_bytes(built.read_bytes())
    recompressed = archive(tmp_path / "recompressed.zip", payload, zipfile.ZIP_STORED)
    drifted = archive(tmp_path / "drifted.zip", payload + b"!", zipfile.ZIP_DEFLATED)
    garbage = tmp_path / "garbage.zip"
    garbage.write_bytes(b"not a zip")

    assert solution_bundle_assets.compare(copy, built) == "identical"
    assert solution_bundle_assets.compare(recompressed, built) == "content-identical"
    assert solution_bundle_assets.compare(drifted, built) == "different"
    assert solution_bundle_assets.compare(garbage, built) == "different"
    assert solution_bundle_assets.main(["same", str(recompressed), str(built)]) == 0
    assert solution_bundle_assets.main(["same", str(drifted), str(built)]) == 1


def test_one_real_bundle_matches_the_repository_files(tmp_path):
    name, manifest = solution_bundle_assets.bundle_manifests(ROOT)[0]
    target = tmp_path / name
    build_solution_export.build(manifest, target)
    with zipfile.ZipFile(target) as archive:
        members = archive.namelist()
        assert not any(member.endswith("-source.zip") for member in members)
        for member in members:
            assert archive.read(member) == build_solution_export.bundle_bytes(ROOT / member), member


def test_workflow_publishes_to_its_own_ring_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert re.search(
        r"github\.event\.repository\.fork == true &&\s+github\.ref == 'refs/heads/staging'",
        text,
    )
    assert re.search(
        r"github\.repository == 'microsoft/aibast-agents-library' &&\s+github\.ref == 'refs/heads/main'",
        text,
    )
    assert "branches: [main, staging]" in text
    for path in (
        "'solutions/**'",
        "'tools/build_solution_export.py'",
        "'tools/solution_bundle_assets.py'",
        "'.github/workflows/solution-bundle-assets.yml'",
    ):
        assert path in text, path
    assert "workflow_dispatch:" in text
    assert "cancel-in-progress: false" in text
    # Publishing targets the repository the workflow runs in, never a fixed one.
    assert "releases/download/$tag" in text
    assert "${GITHUB_REPOSITORY}" in text
    assert "microsoft/aibast-agents-library/releases" not in text


def test_workflow_uploads_only_changed_bundles_and_verifies_them():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert f'tag="{solution_bundle_assets.RELEASE_TAG}"' in text
    assert "--latest=false" in text
    assert "python tools/solution_bundle_assets.py build --out dist/solution-bundles" in text
    assert '"sha256:$sha"' in text
    assert "unchanged $name" in text  # no unconditional re-upload (resets counters)
    assert text.count("gh release upload") == 1
    assert "--clobber" in text
    assert "dist/solution-bundles/SHA256SUMS" in text
    assert "DRIFT $name" in text
    assert 'test "$fail" = 0' in text


def test_workflow_pins_every_action_to_a_commit():
    text = WORKFLOW.read_text(encoding="utf-8")
    uses = re.findall(r"uses:\s*(\S+)", text)
    assert uses
    for action in uses:
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", action), action
