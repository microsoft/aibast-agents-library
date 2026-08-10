from scripts import build_metrics, sync_agent_discussions

REVISION = "b" * 40


def agent(name="@aibast-agents-library/example", file_path="agents/example.py"):
    return {
        "name": name,
        "display_name": "Example Agent",
        "description": "A deterministic example.",
        "_file": file_path,
        "_sha256": "a" * 64,
    }


def remote_discussion(
    row,
    signal,
    *,
    number,
    owner="example",
    repo="library",
    revision=REVISION,
    viewer_has_upvoted=False,
):
    return {
        "id": f"discussion-{number}",
        "number": number,
        "title": sync_agent_discussions.discussion_title(row, signal),
        "body": sync_agent_discussions.discussion_body(
            row, signal, owner, repo, revision
        ),
        "url": f"https://github.com/{owner}/{repo}/discussions/{number}",
        "upvoteCount": number,
        "viewerHasUpvoted": viewer_has_upvoted,
        "category": {
            "id": "category",
            "name": "Announcements",
            "slug": "announcements",
        },
    }


def test_discussion_contract_has_two_distinct_traceable_ledgers():
    row = agent()
    rating = sync_agent_discussions.discussion_body(
        row, "upvote", "example", "library", REVISION
    )
    acquisition = sync_agent_discussions.discussion_body(
        row, "acquisition", "example", "library", REVISION
    )

    assert rating.startswith(build_metrics.AGENT_DISCUSSION_MARKER)
    assert "- Schema: `aibast-agent-discussion/1.0`" in rating
    assert "- Signal: `upvote`" in rating
    assert "- Signal: `acquisition`" in acquisition
    assert "- Agent: `@aibast-agents-library/example`" in rating
    assert "- File: `agents/example.py`" in rating
    assert "one active upvote per signed-in account" in rating
    assert "opt-in acquisition ledger, not a raw HTTP download counter" in (
        acquisition
    )
    assert "curl -fsSL" in acquisition
    assert REVISION in acquisition
    assert "python3 -c" in acquisition
    assert row["_sha256"] in acquisition
    assert "/main/" not in acquisition
    assert sync_agent_discussions.discussion_title(
        row, "upvote"
    ) == "@aibast-agents-library/example"
    assert sync_agent_discussions.discussion_title(
        row, "acquisition"
    ) == "[Acquisition] @aibast-agents-library/example"


def test_sync_reuses_legacy_rating_and_creates_parallel_acquisition():
    row = agent()
    legacy = {
        "id": "legacy-rating",
        "number": 7,
        "title": row["name"],
        "body": (
            "This is the official rating thread for "
            f"{row['name']} in the AIBAST Agents Library."
        ),
        "url": "https://github.com/example/library/discussions/7",
        "upvoteCount": 4,
    }
    plan = sync_agent_discussions.plan_discussion_sync(
        {"agents": [row]},
        [legacy],
        {},
        owner="example",
        repo="library",
        revisions={row["_file"]: REVISION},
    )

    assert plan["agents"] == 1
    assert [
        (item["signal"], item["action"])
        for item in plan["operations"]
    ] == [
        ("upvote", "update"),
        ("acquisition", "create"),
    ]
    assert plan["operations"][0]["existing"]["number"] == 7


def test_sync_preserves_discussion_across_agent_rename_by_file_identity():
    old = agent(
        "@aibast-agents-library/old-name",
        "agents/stable_agent.py",
    )
    new = agent(
        "@aibast-agents-library/new-name",
        "agents/stable_agent.py",
    )
    existing = remote_discussion(old, "upvote", number=12)
    prior = {
        "schema": sync_agent_discussions.STATE_SCHEMA,
        "repo": "example/library",
        "agents": {
            old["name"]: {
                "file": old["_file"],
                "upvote": {"number": 12},
            }
        }
    }

    plan = sync_agent_discussions.plan_discussion_sync(
        {"agents": [new]},
        [existing],
        prior,
        owner="example",
        repo="library",
        revisions={new["_file"]: REVISION},
    )
    rating = next(
        row for row in plan["operations"] if row["signal"] == "upvote"
    )

    assert rating["action"] == "update"
    assert rating["existing"]["number"] == 12
    assert "- Agent: `@aibast-agents-library/new-name`" in rating["body"]


def test_idempotent_sync_leaves_complete_pair_unchanged():
    row = agent()
    discussions = [
        remote_discussion(row, "upvote", number=1),
        remote_discussion(row, "acquisition", number=2),
    ]
    plan = sync_agent_discussions.plan_discussion_sync(
        {"agents": [row]},
        discussions,
        {},
        owner="example",
        repo="library",
        revisions={row["_file"]: REVISION},
    )

    assert {item["action"] for item in plan["operations"]} == {
        "unchanged"
    }
    state = sync_agent_discussions.build_state(
        "example",
        "library",
        "Announcements",
        plan,
        discussions,
    )
    assert state["schema"] == "aibast-agent-discussions/1.0"
    assert state["summary"] == {
        "agents": 1,
        "discussions": 2,
        "created": 0,
        "updated": 0,
        "unchanged": 2,
        "duplicate_candidates": 0,
        "author_upvotes_removed": 0,
    }
    assert state["agents"][row["name"]]["upvote"]["number"] == 1
    assert state["agents"][row["name"]]["acquisition"]["number"] == 2
    assert state["agents"][row["name"]]["revision"] == REVISION


def test_prior_state_from_another_repository_is_ignored():
    row = agent()
    unrelated = remote_discussion(
        agent(
            "@aibast-agents-library/unrelated",
            "agents/unrelated.py",
        ),
        "upvote",
        number=7,
    )
    prior = {
        "schema": sync_agent_discussions.STATE_SCHEMA,
        "repo": "other/library",
        "agents": {
            row["name"]: {
                "file": row["_file"],
                "upvote": {"number": 7},
            }
        },
    }

    plan = sync_agent_discussions.plan_discussion_sync(
        {"agents": [row]},
        [unrelated],
        prior,
        owner="example",
        repo="library",
        revisions={row["_file"]: REVISION},
    )

    rating = next(
        item for item in plan["operations"] if item["signal"] == "upvote"
    )
    assert rating["action"] == "create"
    assert rating["existing"] is None


def test_prior_number_must_match_canonical_agent_or_file():
    row = agent()
    unrelated = remote_discussion(
        agent(
            "@aibast-agents-library/unrelated",
            "agents/unrelated.py",
        ),
        "upvote",
        number=7,
    )
    prior = {
        "schema": sync_agent_discussions.STATE_SCHEMA,
        "repo": "example/library",
        "agents": {
            row["name"]: {
                "file": row["_file"],
                "upvote": {"number": 7},
            }
        },
    }

    plan = sync_agent_discussions.plan_discussion_sync(
        {"agents": [row]},
        [unrelated],
        prior,
        owner="example",
        repo="library",
        revisions={row["_file"]: REVISION},
    )

    rating = next(
        item for item in plan["operations"] if item["signal"] == "upvote"
    )
    assert rating["action"] == "create"
    assert rating["existing"] is None


def test_apply_operation_removes_sync_author_upvote(monkeypatch):
    row = agent()
    existing = remote_discussion(
        row,
        "acquisition",
        number=2,
        viewer_has_upvoted=True,
    )
    operation = {
        "action": "unchanged",
        "signal": "acquisition",
        "agent": row["name"],
        "existing": existing,
    }
    calls = []

    def request_graphql(query, variables, token):
        calls.append((query, variables, token))
        return (
            {
                "removeUpvote": {
                    "subject": {
                        "id": existing["id"],
                        "upvoteCount": 0,
                        "viewerHasUpvoted": False,
                    }
                }
            },
            None,
        )

    monkeypatch.setattr(
        build_metrics, "request_graphql", request_graphql
    )

    result = sync_agent_discussions.apply_operation(
        operation,
        repository_id="repository",
        category_id="category",
        token="token",
    )

    assert len(calls) == 1
    assert "removeUpvote" in calls[0][0]
    assert calls[0][1] == {"subjectId": existing["id"]}
    assert result["upvoteCount"] == 0
    assert result["viewerHasUpvoted"] is False
    assert result["_author_upvote_removed"] is True
