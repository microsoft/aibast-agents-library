import json
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


def test_accumulate_installer_assets_survives_counter_resets():
    store = {}
    build_metrics.accumulate_installer_assets(store, {"install.ps1": 5})
    build_metrics.accumulate_installer_assets(store, {"install.ps1": 7})
    assert store["install.ps1"] == {"last": 7, "all_time": 7}
    # asset replaced on a real installer change: counter restarts at 2
    build_metrics.accumulate_installer_assets(store, {"install.ps1": 2})
    assert store["install.ps1"] == {"last": 2, "all_time": 9}
    build_metrics.accumulate_installer_assets(store, {"install.ps1": 2})
    assert store["install.ps1"]["all_time"] == 9
    assert build_metrics.installer_release_all_time({"installer_assets": store}) == 9
    assert build_metrics.installer_release_all_time({}) == 0


def test_with_release_installer_downloads_prefers_accumulated_history():
    live = {"available": True, "releases": [{"tag": "installers", "assets": [
        {"name": "install.ps1", "downloads": 1}]}]}
    hist = {"installer_assets": {"install.ps1": {"last": 1, "all_time": 40}}}
    assert build_metrics.with_release_installer_downloads(2, live, hist) == 42
    assert build_metrics.with_release_installer_downloads(2, live, {}) == 3
    assert build_metrics.with_release_installer_downloads(None, live, hist) == 40


def test_merge_history_accumulates_installer_assets(tmp_path):
    history = tmp_path / "metrics_history.json"
    for counters in ({"install.ps1": 3}, {"install.ps1": 4}, {"install.ps1": 1}):
        totals, _daily, _last = build_metrics.merge_history(
            {}, {}, history, run_at="2026-09-02T00:00:00Z", installer_assets=counters
        )
    assert totals["installer_release_downloads_all_time"] == 5
    saved = json.loads(history.read_text())
    assert saved["installer_assets"]["install.ps1"] == {"last": 1, "all_time": 5}


def test_workflow_publishes_exactly_the_mapped_assets():
    text = WORKFLOW.read_text(encoding="utf-8")
    published = set(re.findall(r"dist/installers/([A-Za-z0-9_.-]+)\s*$", text, re.M))
    assert published == set(build_metrics.RELEASE_INSTALLER_ASSETS)
    assert 'tag="installers"' in text
    assert "--clobber" in text
    assert "unchanged $name" in text  # no unconditional re-upload (resets counters)


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
