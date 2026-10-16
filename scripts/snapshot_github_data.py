#!/usr/bin/env python3
"""Snapshot the GitHub data the Pages site reads, so visitors never call api.github.com.

Runs in the Pages workflow with the workflow's GITHUB_TOKEN, after build_pages_site.py, and writes into
the Pages artifact (nothing is committed):

  api/v1/github/repo.json             repos/{repo}, trimmed, same field names as the GitHub API
  api/v1/github/releases.json         Frontier releases (tag prefix brainstem-beta-v), full API objects
  api/v1/github/release-commits.json  {"repository", "commits": {tag: {"sha"}}}
  api/v1/github/index.json            schema, generated_at, sources, and the sha256 of each file

GitHub's unauthenticated API allows 60 requests per hour per network address, and a room of visitors on
one corporate network shares that budget. These files are served from the Pages CDN instead. If GitHub
cannot be reached, the step writes nothing and the pages fall back to asking GitHub themselves.

Usage: python scripts/snapshot_github_data.py --out _site --repository owner/repo
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

API = "https://api.github.com"
SCHEMA = "aibast-github-snapshot/1.0"
TAG_PREFIX = "brainstem-beta-v"
REPO_FIELDS = (
    "id", "name", "full_name", "html_url", "description", "default_branch",
    "stargazers_count", "watchers_count", "forks_count", "open_issues_count",
    "subscribers_count", "created_at", "updated_at", "pushed_at",
)


def get(path, token):
    request = urllib.request.Request(
        f"{API}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "aibast-pages-snapshot",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def snapshot(repository, token, fetch=get):
    repo = fetch(f"repos/{repository}", token)
    releases = [
        item for item in fetch(f"repos/{repository}/releases?per_page=100", token)
        if isinstance(item, dict) and item.get("draft") is not True
        and str(item.get("tag_name", "")).startswith(TAG_PREFIX)
    ]
    commits = {}
    for item in releases:
        tag = item["tag_name"]
        commits[tag] = {"sha": fetch(f"repos/{repository}/commits/{quote(tag, safe='')}", token)["sha"]}
    return {
        "repo.json": {"owner": {"login": repo.get("owner", {}).get("login")}, **{k: repo.get(k) for k in REPO_FIELDS}},
        "releases.json": releases,
        "release-commits.json": {"repository": repository, "commits": commits},
    }


def write(out, repository, files, now=None):
    folder = Path(out) / "api" / "v1" / "github"
    folder.mkdir(parents=True, exist_ok=True)
    previous = {}
    if (folder / "index.json").exists():
        try:
            previous = json.loads((folder / "index.json").read_text(encoding="utf-8"))
        except ValueError:
            previous = {}
    index = {
        "schema": SCHEMA,
        "generated_at": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repository": repository,
        "source": f"{API}/repos/{repository}",
        "files": {},
    }
    for name, value in files.items():
        data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
        (folder / name).write_bytes(data)
        index["files"][name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    # Stable write: when no file changed, keep the previous timestamp so a committed snapshot only changes with the data.
    if previous.get("files") == index["files"] and previous.get("repository") == repository:
        index["generated_at"] = previous.get("generated_at", index["generated_at"])
    (folder / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True)
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    try:
        files = snapshot(args.repository, os.environ.get("GITHUB_TOKEN", ""))
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as error:
        print(f"::warning::GitHub snapshot skipped ({error}); pages will ask GitHub directly.", file=sys.stderr)
        return 0
    index = write(args.out, args.repository, files)
    print(f"wrote api/v1/github/ ({len(files['releases.json'])} releases) at {index['generated_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
