#!/usr/bin/env python3
"""Slim snapshots of the agent catalog for the jsDelivr mirror.

jsDelivr refuses to serve a GitHub repository larger than 50 MB, and this
repository is far larger, so Brainstem chat installs fell back to raw GitHub,
which keeps no download counts. A snapshot is a parentless commit holding only
LICENSE, registry.json and agents/ from a source commit. It is deterministic:
the same source commit always gives the same snapshot commit, wherever it is
built, so the chat can pin it next to RAR_REVISION and anyone can check it.

  python tools/agents_cdn.py snapshot <rev>         print the snapshot commit
  python tools/agents_cdn.py check                  chat pin matches its snapshot
  python tools/agents_cdn.py publish <rev>... [--remote origin]
  python tools/agents_cdn.py verify <rev> --owner OWNER --repo REPO
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAT_PAGE = ROOT / "rapp_brainstem" / "index.html"
SNAPSHOT_PATHS = ("LICENSE", "registry.json", "agents")
SIZE_LIMIT = 40 * 1000 * 1000  # stay well under jsDelivr's 50 MB package limit
TAG_PREFIX = "agents-cdn-"
IDENTITY = ("AIBAST agents CDN", "41898282+github-actions[bot]@users.noreply.github.com")
_REVISION = re.compile(r"^\s*const RAR_REVISION = '([0-9a-f]{40})';$", re.M)
_CDN_COMMIT = re.compile(r"^\s*const RAR_CDN_COMMIT = '([0-9a-f]{40})';$", re.M)


class SnapshotError(RuntimeError):
    pass


def git(*args: str, cwd: Path = ROOT, env: dict | None = None, stdin: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=str(cwd), env=env, input=stdin,
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise SnapshotError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def snapshot_tree(rev: str, cwd: Path = ROOT) -> str:
    entries = git("ls-tree", rev, "--", *SNAPSHOT_PATHS, cwd=cwd)
    names = {line.split("\t", 1)[1] for line in entries.splitlines()}
    missing = [path for path in SNAPSHOT_PATHS if path not in names]
    if missing:
        raise SnapshotError(f"{rev} has no {', '.join(missing)}")
    return git("mktree", cwd=cwd, stdin=entries).strip()


def tree_size(tree: str, cwd: Path = ROOT) -> int:
    total = 0
    for line in git("ls-tree", "-r", "-l", tree, cwd=cwd).splitlines():
        size = line.split()[3]
        total += int(size) if size.isdigit() else 0
    return total


def snapshot_commit(rev: str, cwd: Path = ROOT, size_limit: int = SIZE_LIMIT) -> str:
    """Build (or rebuild) the snapshot commit for rev; same rev, same commit."""
    rev = git("rev-parse", "--verify", f"{rev}^{{commit}}", cwd=cwd).strip()
    tree = snapshot_tree(rev, cwd)
    size = tree_size(tree, cwd)
    if size > size_limit:
        raise SnapshotError(f"snapshot of {rev} is {size} bytes, over the {size_limit} byte limit")
    stamp = git("show", "-s", "--format=%ct", rev, cwd=cwd).strip()
    env = dict(os.environ)
    for role in ("AUTHOR", "COMMITTER"):
        env[f"GIT_{role}_NAME"], env[f"GIT_{role}_EMAIL"] = IDENTITY
        env[f"GIT_{role}_DATE"] = f"{stamp} +0000"
    return git("commit-tree", tree, "-m", f"Agents CDN snapshot of {rev}", cwd=cwd, env=env).strip()


def chat_pins(page: Path = CHAT_PAGE) -> tuple[str, str]:
    text = page.read_text(encoding="utf-8")
    revision, cdn = _REVISION.search(text), _CDN_COMMIT.search(text)
    if not revision or not cdn:
        raise SnapshotError(f"{page} must declare RAR_REVISION and RAR_CDN_COMMIT")
    return revision.group(1), cdn.group(1)


def jsdelivr_url(owner: str, repo: str, commit: str, path: str) -> str:
    quoted = "/".join(urllib.parse.quote(part) for part in path.split("/"))
    return f"https://cdn.jsdelivr.net/gh/{owner}/{repo}@{commit}/{quoted}"


def verify_served(rev: str, owner: str, repo: str, attempts: int = 10, wait: float = 30.0,
                  cwd: Path = ROOT) -> None:
    """Fetch registry.json through jsDelivr and compare it with the source commit."""
    commit = snapshot_commit(rev, cwd)
    expected = git("rev-parse", f"{rev}:registry.json", cwd=cwd).strip()
    url = jsdelivr_url(owner, repo, commit, "registry.json")
    last = ""
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                body = response.read()
            served = hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest()
            if served == expected:
                print(f"served: {url}")
                return
            last = "content differs from the source commit"
        except (urllib.error.URLError, OSError) as error:
            last = str(error)
        if attempt + 1 < attempts:
            time.sleep(wait)
    raise SnapshotError(f"jsDelivr did not serve {url}: {last}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot").add_argument("rev")
    sub.add_parser("check")
    publish = sub.add_parser("publish")
    publish.add_argument("revs", nargs="+")
    publish.add_argument("--remote", default="origin")
    verify = sub.add_parser("verify")
    verify.add_argument("rev")
    verify.add_argument("--owner", required=True)
    verify.add_argument("--repo", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            print(snapshot_commit(args.rev))
        elif args.command == "check":
            revision, cdn = chat_pins()
            built = snapshot_commit(revision)
            if built != cdn:
                raise SnapshotError(
                    f"RAR_CDN_COMMIT is {cdn} but the snapshot of {revision} is {built}; "
                    f"set RAR_CDN_COMMIT = '{built}'"
                )
            print(f"chat pin {revision[:12]} -> snapshot {cdn[:12]}")
        elif args.command == "publish":
            refs = []
            for rev in dict.fromkeys(args.revs):
                full = git("rev-parse", "--verify", f"{rev}^{{commit}}").strip()
                commit = snapshot_commit(full)
                refs.append(f"{commit}:refs/tags/{TAG_PREFIX}{full}")
                print(f"{full} -> {commit}")
            # Tags keep each snapshot reachable; pushing an identical tag again is a no-op.
            git("push", args.remote, *refs)
        else:
            verify_served(args.rev, args.owner, args.repo)
    except SnapshotError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
