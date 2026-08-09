#!/usr/bin/env python3
"""Create and maintain one rating and one acquisition Discussion per agent."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

try:
    from scripts import build_metrics
except ImportError:
    import build_metrics  # type: ignore


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"
OUT = ROOT / "state" / "agent_discussions.json"
DEFAULT_CATEGORY = "Announcements"
STATE_SCHEMA = "aibast-agent-discussions/1.0"

REPOSITORY_QUERY = """
query($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    id
    hasDiscussionsEnabled
    defaultBranchRef { name target { oid } }
    discussionCategories(first: 100) {
      nodes { id name slug }
    }
  }
}
"""

CREATE_MUTATION = """
mutation(
  $repositoryId: ID!
  $categoryId: ID!
  $title: String!
  $body: String!
) {
  createDiscussion(input: {
    repositoryId: $repositoryId
    categoryId: $categoryId
    title: $title
    body: $body
  }) {
    discussion {
      id
      number
      title
      body
      url
      upvoteCount
      viewerHasUpvoted
      category { id name slug }
    }
  }
}
"""

UPDATE_MUTATION = """
mutation($discussionId: ID!, $title: String!, $body: String!) {
  updateDiscussion(input: {
    discussionId: $discussionId
    title: $title
    body: $body
  }) {
    discussion {
      id
      number
      title
      body
      url
      upvoteCount
      viewerHasUpvoted
      category { id name slug }
    }
  }
}
"""

REMOVE_UPVOTE_MUTATION = """
mutation($subjectId: ID!) {
  removeUpvote(input: {subjectId: $subjectId}) {
    subject {
      ... on Discussion {
        id
        upvoteCount
        viewerHasUpvoted
      }
    }
  }
}
"""


class SyncError(RuntimeError):
    pass


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def install_command(
    agent: dict,
    owner: str,
    repo: str,
    revision: str,
) -> str:
    file_path = str(agent.get("_file") or "")
    filename = Path(file_path).name
    target = (
        filename
        if filename.endswith("_agent.py")
        else filename.removesuffix(".py") + "_agent.py"
    )
    sha256 = str(agent.get("_sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise SyncError(f"Invalid SHA-256 for {agent.get('name')}")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise SyncError(f"Invalid immutable revision for {agent.get('name')}")
    source = (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{revision}/"
        f"{quote(file_path, safe='/@._-')}"
    )
    return (
        'tmp="$(mktemp)" && trap \'rm -f "$tmp"\' EXIT && '
        f"curl -fsSL {shlex.quote(source)} -o \"$tmp\" && "
        "test \"$(python3 -c "
        "'import hashlib,sys; print(hashlib.sha256("
        "open(sys.argv[1],\"rb\").read()).hexdigest())' "
        f"\"$tmp\")\" = {shlex.quote(sha256)} && "
        f"install -m 0644 \"$tmp\" "
        f"\"$HOME/.brainstem/src/rapp_brainstem/agents/{target}\""
    )


def discussion_title(agent: dict, signal: str) -> str:
    name = str(agent["name"])
    return name if signal == "upvote" else f"[Acquisition] {name}"


def discussion_body(
    agent: dict,
    signal: str,
    owner: str,
    repo: str,
    revision: str,
) -> str:
    name = str(agent["name"])
    display_name = str(agent.get("display_name") or name)
    description = str(agent.get("description") or "").strip()
    file_path = str(agent.get("_file") or "")
    sha256 = str(agent.get("_sha256") or "unavailable")
    source_url = (
        f"https://github.com/{owner}/{repo}/blob/{revision}/"
        f"{quote(file_path, safe='/@._-')}"
    )
    machine_header = "\n".join(
        (
            build_metrics.AGENT_DISCUSSION_MARKER,
            f"- Schema: `{build_metrics.AGENT_DISCUSSION_SCHEMA}`",
            f"- Signal: `{signal}`",
            f"- Agent: `{name}`",
            f"- File: `{file_path}`",
            f"- SHA-256: `{sha256}`",
            f"- Revision: `{revision}`",
        )
    )
    if signal == "upvote":
        instructions = (
            "## Community preference\n\n"
            "Use GitHub's native **upvote** control on this Discussion to "
            "recommend this agent. GitHub allows one active upvote per signed-in "
            "account, so the public aggregate is traceable without publishing a "
            "voter list.\n\n"
            "Questions, reviews, and implementation notes belong in the replies."
        )
    else:
        command = install_command(agent, owner, repo, revision)
        instructions = (
            "## Signed-in acquisition\n\n"
            "If you downloaded, copied, or installed this agent file, use "
            "GitHub's native **upvote** control once to record one signed-in "
            "acquisition. This is an opt-in acquisition ledger, not a raw HTTP "
            "download counter; CDN and release file transfers remain separate "
            "metrics.\n\n"
            "```bash\n"
            f"{command}\n"
            "```"
        )
    return (
        f"{machine_header}\n\n"
        f"# {display_name}\n\n"
        f"{description}\n\n"
        f"{instructions}\n\n"
        f"**Canonical source:** {source_url}\n"
    )


def _prior_discussion_number(
    prior: dict,
    agent: dict,
    signal: str,
    owner: str,
    repo: str,
) -> int | None:
    if (
        prior.get("schema") != STATE_SCHEMA
        or prior.get("repo") != f"{owner}/{repo}"
    ):
        return None
    rows = prior.get("agents") if isinstance(prior, dict) else None
    if not isinstance(rows, dict):
        return None
    exact = rows.get(agent["name"])
    if isinstance(exact, dict):
        block = exact.get(signal)
        number = (
            block.get("number")
            if isinstance(block, dict)
            else None
        )
        if isinstance(number, int):
            return number
    file_path = agent.get("_file")
    for row in rows.values():
        if not isinstance(row, dict) or row.get("file") != file_path:
            continue
        block = row.get(signal)
        number = block.get("number") if isinstance(block, dict) else None
        if isinstance(number, int):
            return number
    return None


def plan_discussion_sync(
    registry: dict,
    discussions: list[dict],
    prior: dict,
    *,
    owner: str,
    repo: str,
    revisions: dict[str, str],
) -> dict:
    agents = [
        row
        for row in registry.get("agents", [])
        if isinstance(row, dict)
        and isinstance(row.get("name"), str)
        and row["name"].startswith("@aibast-agents-library/")
        and row.get("_file")
    ]
    by_number = {
        row.get("number"): row
        for row in discussions
        if isinstance(row, dict) and isinstance(row.get("number"), int)
    }
    exact = {}
    by_file = {}
    by_title = {}
    for discussion in discussions:
        if not isinstance(discussion, dict):
            continue
        title = discussion.get("title")
        if isinstance(title, str):
            by_title.setdefault(title, []).append(discussion)
        parsed = build_metrics.parse_agent_discussion(
            discussion.get("body", "")
        )
        if not parsed:
            continue
        exact.setdefault(
            (parsed["signal"], parsed["agent"]),
            [],
        ).append(discussion)
        by_file.setdefault(
            (parsed["signal"], parsed["file"]),
            [],
        ).append(discussion)

    operations = []
    claimed_ids = set()
    duplicate_candidates = 0
    for agent in sorted(agents, key=lambda row: row["name"]):
        for signal in build_metrics.AGENT_DISCUSSION_SIGNALS:
            candidates = []
            candidates.extend(exact.get((signal, agent["name"]), []))
            candidates.extend(
                by_file.get((signal, agent.get("_file")), [])
            )
            prior_number = _prior_discussion_number(
                prior, agent, signal, owner, repo
            )
            if prior_number in by_number:
                prior_candidate = by_number[prior_number]
                parsed_prior = build_metrics.parse_agent_discussion(
                    prior_candidate.get("body", "")
                )
                if (
                    parsed_prior
                    and parsed_prior["signal"] == signal
                    and (
                        parsed_prior["agent"] == agent["name"]
                        or parsed_prior["file"] == agent.get("_file")
                    )
                ):
                    candidates.append(prior_candidate)
            title = discussion_title(agent, signal)
            candidates.extend(by_title.get(title, []))
            if signal == "upvote":
                candidates.extend(by_title.get(agent["name"], []))

            unique = []
            seen_ids = set()
            for candidate in candidates:
                identity = candidate.get("id") or candidate.get("number")
                if identity in seen_ids or identity in claimed_ids:
                    continue
                seen_ids.add(identity)
                unique.append(candidate)
            duplicate_candidates += max(0, len(unique) - 1)
            existing = unique[0] if unique else None
            revision = revisions.get(str(agent.get("_file") or ""))
            if not revision:
                raise SyncError(
                    f"No immutable revision for {agent.get('_file')}"
                )
            desired_body = discussion_body(
                agent, signal, owner, repo, revision
            )
            desired_title = discussion_title(agent, signal)
            action = "create"
            if existing:
                claimed_ids.add(existing.get("id") or existing.get("number"))
                action = (
                    "unchanged"
                    if (
                        existing.get("title") == desired_title
                        and existing.get("body") == desired_body
                    )
                    else "update"
                )
            operations.append(
                {
                    "action": action,
                    "signal": signal,
                    "agent": agent["name"],
                    "file": agent["_file"],
                    "sha256": agent.get("_sha256"),
                    "revision": revision,
                    "title": desired_title,
                    "body": desired_body,
                    "existing": existing,
                }
            )
    return {
        "operations": operations,
        "agents": len(agents),
        "duplicate_candidates": duplicate_candidates,
        "author_upvotes_to_remove": sum(
            bool(
                (operation.get("existing") or {}).get(
                    "viewerHasUpvoted"
                )
            )
            for operation in operations
        ),
    }


def resolve_agent_revisions(registry: dict) -> dict[str, str]:
    revisions = {}
    for agent in registry.get("agents", []):
        if not isinstance(agent, dict):
            continue
        file_path = str(agent.get("_file") or "")
        sha256 = str(agent.get("_sha256") or "")
        if (
            not agent.get("name", "").startswith(
                "@aibast-agents-library/"
            )
            or not file_path
        ):
            continue
        try:
            revision = subprocess.run(
                [
                    "git",
                    "log",
                    "-1",
                    "--format=%H",
                    "--",
                    file_path,
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            source = subprocess.run(
                ["git", "show", f"{revision}:{file_path}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
        except subprocess.CalledProcessError as error:
            raise SyncError(
                f"Could not resolve committed source for {file_path}"
            ) from error
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            raise SyncError(f"Invalid git revision for {file_path}")
        if hashlib.sha256(source).hexdigest() != sha256:
            raise SyncError(
                f"Registry SHA-256 does not match {revision}:{file_path}"
            )
        revisions[file_path] = revision
    return revisions


def fetch_repository(
    owner: str,
    repo: str,
    token: str,
) -> dict:
    data, error = build_metrics.request_graphql(
        REPOSITORY_QUERY,
        {"owner": owner, "repo": repo},
        token,
    )
    if error:
        raise SyncError(error.get("message") or "Repository query failed")
    repository = data.get("repository") if data else None
    if not isinstance(repository, dict):
        raise SyncError(f"Repository {owner}/{repo} was not found")
    if not repository.get("hasDiscussionsEnabled"):
        raise SyncError(f"GitHub Discussions are disabled for {owner}/{repo}")
    return repository


def apply_operation(
    operation: dict,
    *,
    repository_id: str,
    category_id: str,
    token: str,
) -> dict:
    if operation["action"] == "unchanged":
        discussion = dict(operation["existing"])
    else:
        if operation["action"] == "create":
            query = CREATE_MUTATION
            variables = {
                "repositoryId": repository_id,
                "categoryId": category_id,
                "title": operation["title"],
                "body": operation["body"],
            }
            response_key = "createDiscussion"
        else:
            query = UPDATE_MUTATION
            variables = {
                "discussionId": operation["existing"]["id"],
                "title": operation["title"],
                "body": operation["body"],
            }
            response_key = "updateDiscussion"
        data = _request_mutation(
            query,
            variables,
            token,
            (
                f"{operation['action']} {operation['signal']} Discussion "
                f"for {operation['agent']}"
            ),
        )
        payload = data.get(response_key) if data else None
        discussion = (
            payload.get("discussion")
            if isinstance(payload, dict)
            else None
        )
        if not isinstance(discussion, dict):
            raise SyncError(
                f"{operation['action']} did not return a Discussion for "
                f"{operation['agent']}"
            )

    discussion["_author_upvote_removed"] = False
    if discussion.get("viewerHasUpvoted"):
        data = _request_mutation(
            REMOVE_UPVOTE_MUTATION,
            {"subjectId": discussion["id"]},
            token,
            (
                f"remove sync-author upvote from {operation['signal']} "
                f"Discussion for {operation['agent']}"
            ),
        )
        payload = data.get("removeUpvote") if data else None
        subject = (
            payload.get("subject")
            if isinstance(payload, dict)
            else None
        )
        if not isinstance(subject, dict):
            raise SyncError(
                f"removeUpvote did not return a Discussion for "
                f"{operation['agent']}"
            )
        discussion.update(subject)
        discussion["_author_upvote_removed"] = True
    return discussion


def _request_mutation(
    query: str,
    variables: dict,
    token: str,
    description: str,
) -> dict:
    for attempt in range(6):
        data, error = build_metrics.request_graphql(
            query, variables, token
        )
        message = str((error or {}).get("message") or "")
        if not error:
            return data or {}
        throttled = (
            "too quickly" in message.casefold()
            or "secondary rate limit" in message.casefold()
            or "abuse" in message.casefold()
        )
        if not throttled or attempt == 5:
            raise SyncError(f"{description}: {message}")
        time.sleep(min(60, 2 ** (attempt + 1)))
    raise SyncError(f"{description}: retry limit reached")


def build_state(
    owner: str,
    repo: str,
    category: str,
    plan: dict,
    results: list[dict],
) -> dict:
    agents = {}
    for operation, discussion in zip(plan["operations"], results):
        row = agents.setdefault(
            operation["agent"],
            {
                "file": operation["file"],
                "sha256": operation.get("sha256"),
                "revision": operation.get("revision"),
            },
        )
        row[operation["signal"]] = {
            "number": discussion.get("number"),
            "url": discussion.get("url"),
            "title": discussion.get("title"),
            "upvotes": discussion.get("upvoteCount"),
        }
    return {
        "schema": STATE_SCHEMA,
        "generated_at": build_metrics.now_iso(),
        "repo": f"{owner}/{repo}",
        "category": category,
        "signals": list(build_metrics.AGENT_DISCUSSION_SIGNALS),
        "agents": agents,
        "summary": {
            "agents": plan["agents"],
            "discussions": len(results),
            "created": sum(
                row["action"] == "create" for row in plan["operations"]
            ),
            "updated": sum(
                row["action"] == "update" for row in plan["operations"]
            ),
            "unchanged": sum(
                row["action"] == "unchanged"
                for row in plan["operations"]
            ),
            "duplicate_candidates": plan["duplicate_candidates"],
            "author_upvotes_removed": sum(
                bool(row.get("_author_upvote_removed"))
                for row in results
            ),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize canonical rating and signed-in acquisition "
            "Discussions for every registry agent."
        )
    )
    parser.add_argument(
        "--owner",
        default=os.environ.get("METRICS_OWNER", "microsoft"),
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get(
            "METRICS_REPO", "aibast-agents-library"
        ),
    )
    parser.add_argument(
        "--category",
        default=os.environ.get(
            "AGENT_DISCUSSION_CATEGORY", DEFAULT_CATEGORY
        ),
    )
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    token = (
        os.environ.get("DISCUSSIONS_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
    )
    if not token:
        raise SyncError(
            "DISCUSSIONS_TOKEN or GITHUB_TOKEN is required"
        )
    registry = load_json(args.registry, {})
    if not registry.get("agents"):
        raise SyncError(f"Registry is missing or empty: {args.registry}")

    repository = fetch_repository(args.owner, args.repo, token)
    categories = (
        repository.get("discussionCategories") or {}
    ).get("nodes") or []
    category = next(
        (
            row
            for row in categories
            if str(row.get("name", "")).casefold()
            == args.category.casefold()
        ),
        None,
    )
    if not category:
        raise SyncError(
            f"Discussion category {args.category!r} does not exist"
        )

    previous_owner = build_metrics.OWNER
    previous_repo = build_metrics.REPO
    build_metrics.OWNER = args.owner
    build_metrics.REPO = args.repo
    try:
        pages = build_metrics.fetch_discussion_pages(token)
    finally:
        build_metrics.OWNER = previous_owner
        build_metrics.REPO = previous_repo
    if not pages["available"] or not pages["complete"]:
        raise SyncError(
            pages.get("error")
            or "Could not read every existing Discussion"
        )

    prior = load_json(args.out, {})
    revisions = resolve_agent_revisions(registry)
    plan = plan_discussion_sync(
        registry,
        pages["discussions"],
        prior,
        owner=args.owner,
        repo=args.repo,
        revisions=revisions,
    )
    summary = {
        action: sum(
            row["action"] == action for row in plan["operations"]
        )
        for action in ("create", "update", "unchanged")
    }
    if args.dry_run:
        print(
            json.dumps(
                {
                    **summary,
                    "author_upvotes_to_remove": plan[
                        "author_upvotes_to_remove"
                    ],
                    "agents": plan["agents"],
                }
            )
        )
        return 0

    results = []
    for operation in plan["operations"]:
        result = apply_operation(
            operation,
            repository_id=repository["id"],
            category_id=category["id"],
            token=token,
        )
        results.append(result)
        if (
            operation["action"] != "unchanged"
            or result.get("_author_upvote_removed")
        ):
            time.sleep(0.75)
    state = build_state(
        args.owner,
        args.repo,
        category["name"],
        plan,
        results,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(state, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Synced {len(results)} Discussions for {plan['agents']} agents: "
        f"{summary['create']} created, {summary['update']} updated, "
        f"{summary['unchanged']} unchanged."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SyncError as exc:
        print(f"sync_agent_discussions: {exc}", file=sys.stderr)
        raise SystemExit(1)
