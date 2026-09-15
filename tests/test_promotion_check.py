import json
import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "promotion_check.sh"


@pytest.fixture
def promotion_probe(tmp_path):
    binaries = tmp_path / "bin"
    binaries.mkdir()
    git_log = tmp_path / "git-called"
    gh_log = tmp_path / "gh-calls.jsonl"
    git = binaries / "git"
    git.write_text(
        "#!/bin/sh\n"
        'printf "called\\n" >> "$TEST_GIT_LOG"\n'
        'if [ "$*" != "remote get-url origin" ]; then exit 2; fi\n'
        'printf "%s\\n" "$TEST_ORIGIN"\n',
        encoding="utf-8",
    )
    gh = binaries / "gh"
    gh.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
with Path(os.environ["TEST_GH_LOG"]).open("a", encoding="utf-8") as output:
    output.write(json.dumps(args) + "\\n")
if args[0] == "api" and "/commits/" in args[1]:
    print("a" * 40)
elif args[0] == "api" and "/compare/" in args[1]:
    print(json.dumps({"ahead_by": 12, "behind_by": int(os.environ["TEST_BEHIND"])}))
elif args[:2] == ["run", "list"]:
    print("completed success https://example.test/run")
else:
    sys.exit("Unexpected GitHub command")
""",
        encoding="utf-8",
    )
    for executable in (git, gh):
        executable.chmod(0o755)

    def run(origin, *, fork=None, behind=0):
        env = os.environ.copy()
        for key in ("FORK", "UPSTREAM", "RING_BRANCH", "PROD_BRANCH"):
            env.pop(key, None)
        env.update(
            PATH=f"{binaries}{os.pathsep}{env['PATH']}",
            TEST_ORIGIN=origin,
            TEST_GIT_LOG=str(git_log),
            TEST_GH_LOG=str(gh_log),
            TEST_BEHIND=str(behind),
        )
        if fork is not None:
            env["FORK"] = fork
        result = subprocess.run(
            ["bash", str(SCRIPT)], cwd=ROOT, env=env,
            text=True, capture_output=True, check=False,
        )
        calls = (
            [json.loads(line) for line in gh_log.read_text().splitlines()]
            if gh_log.exists()
            else []
        )
        return result, calls, git_log.exists()

    return run


@pytest.mark.parametrize(
    "origin",
    [
        "https://github.com/example-fork/aibast-agents-library.git",
        "git@github.com:example-fork/aibast-agents-library.git",
        "ssh://git@github.com/example-fork/aibast-agents-library.git",
    ],
)
def test_default_fork_comes_from_origin(promotion_probe, origin):
    result, calls, git_called = promotion_probe(origin)
    assert result.returncode == 0, result.stderr
    assert git_called
    assert calls[0][1] == "repos/example-fork/aibast-agents-library/commits/staging"
    assert "--head example-fork:staging" in result.stdout
    assert "upstream/main..origin/staging" in result.stdout


def test_explicit_fork_does_not_depend_on_origin(promotion_probe):
    result, calls, git_called = promotion_probe(
        "unsupported-origin", fork="release-fork/aibast-agents-library"
    )
    assert result.returncode == 0, result.stderr
    assert not git_called
    assert calls[0][1] == "repos/release-fork/aibast-agents-library/commits/staging"


def test_unknown_origin_is_rejected_without_printing_it(promotion_probe):
    origin = "https://private-example@example.invalid/team/repo"
    result, calls, _git_called = promotion_probe(origin)
    assert result.returncode == 2
    assert "set FORK=OWNER/REPOSITORY" in result.stderr
    assert origin not in result.stdout + result.stderr
    assert calls == []


def test_invalid_explicit_fork_is_rejected_before_network_calls(promotion_probe):
    result, calls, git_called = promotion_probe(
        "unused", fork="https://example.invalid/team/repo"
    )
    assert result.returncode == 2
    assert "FORK must be a GitHub OWNER/REPOSITORY" in result.stderr
    assert not git_called
    assert calls == []


def test_upstream_divergence_still_blocks_promotion(promotion_probe):
    result, _calls, _git_called = promotion_probe(
        "git@github.com:example-fork/aibast-agents-library.git", behind=3
    )
    assert result.returncode == 1
    assert "behind microsoft/aibast-agents-library:main by 3" in result.stdout
    assert "do not promote yet" in result.stdout
