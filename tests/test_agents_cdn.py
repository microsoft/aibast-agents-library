import re
import subprocess
from pathlib import Path

import pytest

from tools import agents_cdn


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/agents-cdn.yml"


def _git(repo, *args, env=None):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, env=env).stdout


@pytest.fixture
def source_repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "agents/@aibast-agents-library").mkdir(parents=True)
    (repo / "solutions/demo").mkdir(parents=True)
    (repo / "LICENSE").write_text("MIT\n")
    (repo / "registry.json").write_text('{"agents": []}\n')
    (repo / "agents/@aibast-agents-library/demo_agent.py").write_text("print('demo')\n")
    (repo / "solutions/demo/walkthrough.gif").write_bytes(b"GIF89a" + b"\0" * 2048)
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "source")
    return repo


def test_snapshot_holds_only_the_catalog(source_repo):
    commit = agents_cdn.snapshot_commit("HEAD", cwd=source_repo)
    top = sorted(line.split("\t")[1] for line in _git(source_repo, "ls-tree", commit).splitlines())
    assert top == ["LICENSE", "agents", "registry.json"]
    files = _git(source_repo, "ls-tree", "-r", "--name-only", commit).split()
    assert "agents/@aibast-agents-library/demo_agent.py" in files
    assert not any(name.startswith("solutions/") for name in files)
    assert _git(source_repo, "rev-list", "--parents", "-n", "1", commit).split() == [commit]


def test_snapshot_is_deterministic(source_repo, monkeypatch):
    first = agents_cdn.snapshot_commit("HEAD", cwd=source_repo)
    monkeypatch.setenv("GIT_COMMITTER_DATE", "2030-01-01T00:00:00Z")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "someone else")
    assert agents_cdn.snapshot_commit("HEAD", cwd=source_repo) == first


def test_snapshot_refuses_a_catalog_jsdelivr_would_refuse(source_repo):
    with pytest.raises(agents_cdn.SnapshotError, match="over the"):
        agents_cdn.snapshot_commit("HEAD", cwd=source_repo, size_limit=10)


def test_snapshot_requires_every_catalog_path(source_repo):
    _git(source_repo, "rm", "-q", "registry.json")
    _git(source_repo, "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "drop")
    with pytest.raises(agents_cdn.SnapshotError, match="registry.json"):
        agents_cdn.snapshot_commit("HEAD", cwd=source_repo)


def test_chat_pins_its_revision_and_snapshot():
    revision, cdn = agents_cdn.chat_pins()
    assert re.fullmatch(r"[0-9a-f]{40}", revision)
    assert re.fullmatch(r"[0-9a-f]{40}", cdn)
    assert revision != cdn
    page = agents_cdn.CHAT_PAGE.read_text(encoding="utf-8")
    assert "cdn.jsdelivr.net/gh/microsoft/aibast-agents-library@${RAR_CDN_COMMIT}" in page


def test_chat_snapshot_pin_matches_its_revision_when_history_is_present():
    revision, cdn = agents_cdn.chat_pins()
    present = subprocess.run(["git", "cat-file", "-e", f"{revision}^{{commit}}"], cwd=ROOT, capture_output=True)
    if present.returncode != 0:
        pytest.skip("pinned registry commit is not in this checkout")
    assert agents_cdn.snapshot_commit(revision) == cdn


def test_jsdelivr_paths_encode_scope_folders():
    url = agents_cdn.jsdelivr_url("o", "r", "c" * 40, "agents/@aibast-agents-library/x_agent.py")
    assert url == f"https://cdn.jsdelivr.net/gh/o/r@{'c' * 40}/agents/%40aibast-agents-library/x_agent.py"


def test_workflow_publishes_checks_and_verifies_the_pinned_snapshot():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "branches: [main]" in text
    assert "contents: write" in text
    assert "tools/agents_cdn.py check" in text
    assert "tools/agents_cdn.py publish" in text
    assert "tools/agents_cdn.py verify" in text
    for uses in re.findall(r"uses: (\S+)", text):
        assert re.search(r"@[0-9a-f]{40}$", uses), f"{uses} must be pinned to a commit"
