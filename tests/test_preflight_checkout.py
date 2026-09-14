import os
import re
import subprocess
from pathlib import Path

import pytest

from tools.audit_metrics_page import TRUSTED_COMMIT
from tools.audit_rapp_guide import TRUSTED_SOURCE_COMMIT


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/preflight.yml"
BASELINE_REFSPEC = "+refs/heads/main:refs/remotes/origin/main"


def git(directory, *arguments):
    result = subprocess.run(
        ["git", "-c", "safe.bareRepository=all", "-C", str(directory), *arguments],
        env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"},
        check=False, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_preflight_bounds_history_without_dropping_the_upgrade_baseline():
    workflow = WORKFLOW.read_text()
    for name in ("static", "e2e"):
        block = re.search(
            rf"(?ms)^  {name}:\n(.*?)(?=^  [a-zA-Z0-9_-]+:\n|\Z)",
            workflow,
        ).group(1)
        assert "fetch-depth: 1" in block
        assert "fetch-depth: 0" not in block
    e2e = workflow.split("  e2e:\n", 1)[1].split("  frontier-installer:\n", 1)[0]
    assert (
        "      - name: Fetch upgrade baseline\n"
        "        if: matrix.scenario == 'upgrade'\n"
        "        shell: bash\n"
        f"        run: git fetch --no-tags --depth=1 origin {BASELINE_REFSPEC}"
    ) in e2e
    assert e2e.index("Fetch upgrade baseline") < e2e.index("Point installers at candidate")
    assert (
        'if [ "${{ matrix.scenario }}" = "upgrade" ]; then\n'
        '            git -C "$BARE" fetch --no-tags --depth=1 "$PWD" \\\n'
        "              refs/remotes/origin/main:refs/heads/production-baseline\n"
        "          fi"
    ) in e2e


def test_static_hydrates_only_authoritative_preservation_baselines(monkeypatch):
    workflow = WORKFLOW.read_text()
    assert "fetch-depth: 1\n          filter: blob:none" in workflow
    step = workflow.split("      - name: AIBAST agent and registry contracts\n", 1)[1]
    code = step.split("          python - <<'PY'\n", 1)[1].split("          PY\n", 1)[0]
    calls = []
    monkeypatch.setattr(
        subprocess, "run", lambda command, **kwargs: calls.append((command, kwargs))
    )
    exec("\n".join(line[10:] for line in code.splitlines()))
    assert calls == [([
        "git", "fetch", "--no-tags", "--depth=1", "--filter=blob:none",
        "origin", TRUSTED_COMMIT, TRUSTED_SOURCE_COMMIT,
    ], {"check": True})]


@pytest.mark.parametrize("upgrade", [False, True])
def test_shallow_candidate_can_serve_the_real_installer_fixture(tmp_path, upgrade):
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "--initial-branch=main")
    git(source, "config", "user.name", "Preflight fixture")
    git(source, "config", "user.email", "preflight@example.invalid")
    runtime = source / "rapp_brainstem"
    runtime.mkdir()
    content = source / "solutions/retained/content.txt"
    content.parent.mkdir(parents=True)
    content.write_text("Hosted content stays in the candidate tree.\n")
    for revision in range(4):
        (runtime / "VERSION").write_text(f"0.1.{revision}\n")
        git(source, "add", ".")
        git(source, "commit", "--quiet", "-m", f"Production fixture {revision}")
    baseline = git(source, "rev-parse", "HEAD")
    git(source, "switch", "--create", "candidate")
    (runtime / "VERSION").write_text("0.2.0\n")
    git(source, "add", ".")
    git(source, "commit", "--quiet", "-m", "Candidate fixture")
    head = git(source, "rev-parse", "HEAD")

    checkout = tmp_path / "checkout"
    git(
        tmp_path, "clone", "--quiet", "--no-tags", "--depth=1",
        "--branch", "candidate", source.as_uri(), str(checkout),
    )
    assert git(checkout, "rev-parse", "--is-shallow-repository") == "true"
    assert git(checkout, "rev-list", "--all", "--count") == "1"
    assert (checkout / content.relative_to(source)).read_bytes() == content.read_bytes()
    if upgrade:
        git(checkout, "fetch", "--no-tags", "--depth=1", "origin", BASELINE_REFSPEC)
        assert git(checkout, "rev-parse", "origin/main") == baseline
        assert git(checkout, "rev-list", "--all", "--count") == "2"

    bare = tmp_path / "fake-origin.git"
    git(tmp_path, "clone", "--quiet", "--bare", str(checkout), str(bare))
    git(bare, "update-ref", "refs/heads/main", head)
    git(bare, "symbolic-ref", "HEAD", "refs/heads/main")
    if upgrade:
        git(
            bare, "fetch", "--no-tags", "--depth=1", str(checkout),
            "refs/remotes/origin/main:refs/heads/production-baseline",
        )
    installed = tmp_path / "installed"
    git(tmp_path, "clone", "--quiet", bare.as_uri(), str(installed))
    assert git(installed, "rev-parse", "HEAD") == head
    assert (installed / "rapp_brainstem/VERSION").read_text() == "0.2.0\n"
    assert (installed / content.relative_to(source)).read_bytes() == content.read_bytes()
    assert git(installed, "rev-list", "--all", "--count") == ("2" if upgrade else "1")
    if upgrade:
        assert git(
            installed, "show", "origin/production-baseline:rapp_brainstem/VERSION"
        ) == "0.1.3"
