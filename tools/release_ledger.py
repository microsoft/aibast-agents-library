#!/usr/bin/env python3
"""Draft a docs/RELEASES.md entry for a merged promotion pull request.

Usage: python tools/release_ledger.py <pr-number> [--repo microsoft/aibast-agents-library] [--since-days 14]

Prints a Markdown entry with the pull request, merge commit, the commits it
carried, and every issue opened in the repository after the merge (candidates
for the post-release list). Paste it at the top of docs/RELEASES.md and edit.
Requires the GitHub CLI (`gh`) to be authenticated.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pr", type=int)
    ap.add_argument("--repo", default="microsoft/aibast-agents-library")
    ap.add_argument("--since-days", type=int, default=14, help="issues opened within N days after the merge")
    args = ap.parse_args()

    pr = json.loads(gh("pr", "view", str(args.pr), "-R", args.repo, "--json",
                       "number,title,url,mergedAt,mergeCommit,commits,headRefName,headRepositoryOwner"))
    if not pr.get("mergedAt"):
        print(f"#{args.pr} is not merged", file=sys.stderr)
        return 1
    merged = dt.datetime.fromisoformat(pr["mergedAt"].replace("Z", "+00:00"))
    until = merged + dt.timedelta(days=args.since_days)
    issues = json.loads(gh("issue", "list", "-R", args.repo, "--state", "all", "-L", "100",
                           "--search", f"created:>={merged.date().isoformat()}",
                           "--json", "number,title,url,state,createdAt,labels"))
    post = [i for i in issues
            if merged <= dt.datetime.fromisoformat(i["createdAt"].replace("Z", "+00:00")) <= until]

    head = f"{pr['headRepositoryOwner']['login']}:{pr['headRefName']}"
    print(f"## {merged.date().isoformat()} — {pr['title']}\n")
    print(f"**Shipped:** [#{pr['number']}]({pr['url']}) from `{head}`, merge commit "
          f"`{pr['mergeCommit']['oid'][:8]}`, {len(pr['commits'])} commit(s):")
    for c in pr["commits"]:
        print(f"- `{c['oid'][:8]}` {c['messageHeadline']}")
    print("\n**Gates:** preflight on the pull request; staging ring preflight, Pages deploy, "
          "and one-liner smoke on the promoted head (paste run URLs from tools/promotion_check.sh).\n")
    print("**Post-release:**")
    if post:
        for i in post:
            labels = ", ".join(l["name"] for l in i["labels"]) or "unlabelled"
            print(f"- [#{i['number']}]({i['url']}) {i['title']} ({i['state'].lower()}; {labels})")
    else:
        print(f"- none reported within {args.since_days} days")
    print("\n**Lessons:** (what the next release should do differently)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
