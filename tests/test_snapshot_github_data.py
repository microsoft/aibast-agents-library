import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("snapshot", ROOT / "scripts" / "snapshot_github_data.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)

FILES = {"repo.json": {"full_name": "o/r"}, "releases.json": [], "release-commits.json": {"repository": "o/r", "commits": {}}}


def test_unchanged_data_keeps_the_previous_timestamp(tmp_path):
    first = snapshot.write(tmp_path, "o/r", FILES, now=datetime(2026, 10, 1, tzinfo=timezone.utc))
    second = snapshot.write(tmp_path, "o/r", FILES, now=datetime(2026, 10, 2, tzinfo=timezone.utc))
    assert first["generated_at"] == second["generated_at"] == "2026-10-01T00:00:00Z"


def test_changed_data_moves_the_timestamp(tmp_path):
    snapshot.write(tmp_path, "o/r", FILES, now=datetime(2026, 10, 1, tzinfo=timezone.utc))
    changed = dict(FILES, **{"repo.json": {"full_name": "o/r", "stargazers_count": 9}})
    index = snapshot.write(tmp_path, "o/r", changed, now=datetime(2026, 10, 2, tzinfo=timezone.utc))
    assert index["generated_at"] == "2026-10-02T00:00:00Z"


def test_the_daily_metrics_job_commits_the_snapshot_for_the_branch_served_site():
    workflow = (ROOT / ".github" / "workflows" / "metrics.yml").read_text(encoding="utf-8")
    assert "python scripts/snapshot_github_data.py --out . --repository" in workflow
    assert "git add api/v1/github" in workflow
    assert workflow.index("snapshot_github_data.py") < workflow.index("name: Commit snapshot")


def test_the_committed_snapshot_is_for_this_repository():
    index = json.loads((ROOT / "api" / "v1" / "github" / "index.json").read_text(encoding="utf-8"))
    commits = json.loads((ROOT / "api" / "v1" / "github" / "release-commits.json").read_text(encoding="utf-8"))
    assert index["schema"] == "aibast-github-snapshot/1.0"
    assert index["repository"] == commits["repository"] == "microsoft/aibast-agents-library"
