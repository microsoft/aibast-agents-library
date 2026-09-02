import re
from pathlib import Path

from scripts import build_metrics


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/installer-assets.yml"
RELEASE_URL = "https://github.com/microsoft/aibast-agents-library/releases/download/installers/"


def test_release_installer_downloads_counts_only_mapped_assets():
    releases = {
        "available": True,
        "releases": [
            {"tag": "installers", "assets": [
                {"name": "install.ps1", "downloads": 4},
                {"name": "community_rapp-install.sh", "downloads": 5},
                {"name": "community_rapp-install.ps1", "downloads": None},
            ]},
            {"tag": "agent-downloads", "assets": [
                {"name": "example__abc123_agent.py", "downloads": 9},
            ]},
        ],
    }
    assert build_metrics.release_installer_downloads(releases) == 9
    assert build_metrics.release_installer_downloads({"available": False}) == 0
    assert build_metrics.release_installer_downloads(None) == 0


def test_every_release_installer_asset_maps_to_a_tracked_installer_path():
    for asset, path in build_metrics.RELEASE_INSTALLER_ASSETS.items():
        assert path in build_metrics.INSTALLER_FILES, asset
        assert (ROOT / path.lstrip("/")).is_file(), path


def test_workflow_publishes_exactly_the_mapped_assets():
    text = WORKFLOW.read_text(encoding="utf-8")
    published = set(re.findall(r"dist/installers/([A-Za-z0-9_.-]+)\s*$", text, re.M))
    assert published == set(build_metrics.RELEASE_INSTALLER_ASSETS)
    assert 'tag="installers"' in text
    assert "--clobber" in text


def test_public_one_liners_point_at_the_release_assets():
    for page in ("README.md", "index.html"):
        text = (ROOT / page).read_text(encoding="utf-8")
        assert not re.search(
            r"raw\.githubusercontent\.com/microsoft/aibast-agents-library/main/(community_rapp/)?install\.(sh|ps1)",
            text,
        ), page
        assert RELEASE_URL in text, page
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for asset in build_metrics.RELEASE_INSTALLER_ASSETS:
        assert RELEASE_URL + asset in readme, asset


def test_with_release_installer_downloads_preserves_unobserved_none():
    none_releases = {"available": True, "releases": []}
    some = {"available": True, "releases": [{"tag": "installers", "assets": [
        {"name": "install.ps1", "downloads": 3}]}]}
    assert build_metrics.with_release_installer_downloads(None, none_releases) is None
    assert build_metrics.with_release_installer_downloads(None, some) == 3
    assert build_metrics.with_release_installer_downloads(2, some) == 5
    assert build_metrics.with_release_installer_downloads(0, none_releases) == 0
