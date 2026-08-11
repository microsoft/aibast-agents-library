"""
The library page and the metrics dashboard both read fields the registry
builder adds. These tests pin that contract so a builder change cannot quietly
empty either page.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts import build_metrics

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "registry.json"
METRICS_PAGE = REPO_ROOT / "metrics.html"


def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def workshop_catalog():
    return build_metrics.build_workshop_catalog(load_registry())


def achievement_claim_body(
    achievements=("started",),
    workshop="account-intelligence",
    agent="@aibast-agents-library/account-intelligence",
    source="achievements.html",
    extra="",
):
    achievement_list = ", ".join(achievements)
    return (
        "<!-- aibast-achievement-progress:v1 -->\n"
        "## Workshop achievement progress\n\n"
        "- Schema: `aibast-achievement-progress/1.0`\n"
        f"- Workshop: `{workshop}`\n"
        f"- Agent: `{agent}`\n"
        f"- Achievements: `{achievement_list}`\n"
        f"- Source quest URL: {source}\n"
        f"{extra}"
    )


def test_registry_exposes_stacks():
    reg = load_registry()
    assert reg["stats"]["total_stacks"] > 0
    assert reg["stats"]["total_multi_agent_stacks"] > 0
    assert reg["stats"]["total_solution_containers"] > 0
    assert reg["stacks"], "registry.json must carry a stacks block for library.html"
    for stack in reg["stacks"]:
        for field in (
            "stack", "vertical", "display_name", "path", "agents",
            "agent_count", "stack_type",
        ):
            assert field in stack, f"stack {stack.get('stack')} missing {field}"
        assert stack["agent_count"] == len(stack["agents"])
        expected_type = "multi_agent" if stack["agent_count"] > 1 else "solution_container"
        assert stack["stack_type"] == expected_type


def test_every_agent_has_library_fields():
    reg = load_registry()
    names = {a["name"] for a in reg["agents"]}
    for a in reg["agents"]:
        assert a.get("_sha256"), f"{a['name']} missing _sha256"
        assert a.get("_catalog_kind"), f"{a['name']} missing _catalog_kind"
        assert isinstance(a.get("_readiness"), list), f"{a['name']} missing _readiness"
        # templates/ holds connector templates and the agent generator - library
        # infrastructure, not industry solutions, so they sit outside a stack.
        if "/templates/" in a["_file"]:
            continue
        assert a.get("_stack"), f"{a['name']} is not inside a *_stack folder"
        assert a.get("_stack_vertical"), f"{a['name']} missing _stack_vertical"
    # Every stack member must resolve to a real agent, or the stack install
    # command on the library page emits a 404 curl.
    for stack in reg["stacks"]:
        for member in stack["agents"]:
            assert member in names, f"stack {stack['stack']} references unknown agent {member}"


def test_advertised_solutions_expose_showroom_fields():
    reg = load_registry()
    advertised = [a for a in reg["agents"] if a.get("_solution")]
    assert advertised
    assert reg["stats"]["advertised_solutions"] == len(advertised)
    assert reg["stats"]["demo_proven_agents"] > 0
    assert reg["stats"]["solution_onepagers"] > 0
    assert reg["stats"]["solution_demo_videos"] > 0
    for agent in advertised:
        solution = agent["_solution"]
        for field in (
            "advertised_name", "executive_summary", "industries", "personas",
            "featured_tools", "capabilities", "outcomes", "customer_scenario",
            "onepager", "demo_video", "promise_coverage", "aliases",
        ):
            assert field in solution, f"{agent['name']} solution missing {field}"


def test_metrics_build_offline_without_prior_marks_remote_unavailable(tmp_path):
    out = tmp_path / "metrics.json"
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_metrics.py"),
         "--offline", "--out", str(out)],
        capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, result.stderr[:800]
    doc = json.loads(out.read_text())
    assert doc["schema"] == "aibast-metrics/1.0"
    assert doc["repo"]["stars"] is None
    assert doc["repo"]["carried_forward"] is False
    assert doc["totals"]["agents"] == len(load_registry()["agents"])
    assert all(doc["totals"][field] is None for field in build_metrics.REMOTE_TOTAL_FIELDS)
    assert doc["cdn"]["total_hits"] is None
    assert doc["releases"]["total_downloads"] is None
    assert doc["traffic"]["live"] is False
    assert doc["traffic"]["as_of"] is None
    assert doc["totals"]["agent_upvotes"] is None
    assert doc["totals"]["skill_downloads"] is None
    assert len(doc["file_metrics"]["rows"]) == len(
        build_metrics.tracked_repository_files()
    )
    assert doc["file_metrics"]["source_status"] == "unavailable"
    assert all(row["downloads"] is None for row in doc["file_metrics"]["rows"])
    assert isinstance(doc["agent_metrics"], list)
    assert len(doc["agent_metrics"]) == len(load_registry()["agents"])
    assert all(row["upvotes"] is None for row in doc["agent_metrics"])
    assert isinstance(doc["daily"], list)
    assert isinstance(doc["sources"], list)
    workshops = doc["workshops"]
    assert workshops["totals"]["workshops"] == 51
    assert len(workshops["rows"]) == 51
    assert workshops["coverage"]["status"] == "unavailable"
    assert all(
        row[field] is None
        for row in workshops["rows"]
        for field in (
            "usage_events",
            "views_14d",
            "view_uniques_14d",
            "file_downloads",
            "bundle_downloads",
            "feedback_reports",
            "agent_upvotes",
        )
    )
    assert doc["leaderboards"]["stacks"], "stack leaderboard must not be empty"
    assert doc["leaderboards"]["verticals"], "vertical breakdown must not be empty"
    achievements = doc["achievements"]
    assert achievements["status"] == "unavailable"
    assert achievements["as_of"] is None
    assert achievements["carried_forward"] is False
    assert achievements["profiles"] == []
    assert len(achievements["workshops"]) == 51
    assert len(achievements["achievements"]) == 6
    assert all(value is None for value in achievements["totals"].values())
    assert all(
        row[field] is None
        for row in achievements["workshops"]
        for field in (
            "starts",
            "workshop_completions",
            "hard_completions",
            "achievements",
            "participants",
            "points",
            "completion_rate",
            "hard_completion_rate",
            "achievement_completion_rate",
        )
    )
    certification = doc["workshop_certification"]
    assert certification["status"] == "unavailable"
    assert certification["facilitators"] == []
    assert certification["candidates"] == []
    assert len(certification["workshops"]) == 51
    assert all(value is None for value in certification["totals"].values())
    ecosystem = doc["ecosystem"]
    assert ecosystem["status"] == "unavailable"
    assert ecosystem["sources"]["rar"]["status"] == "excluded"
    assert (
        ecosystem["totals"]["combined_agent_distribution_fetch_events"]
        is None
    )
    assert doc["totals"]["global_agent_distribution_fetch_events"] is None


def test_offline_mode_makes_zero_network_calls(monkeypatch, tmp_path):
    def fail_network(*_args, **_kwargs):
        raise AssertionError("offline mode attempted a network call")

    monkeypatch.setattr(build_metrics, "fetch_repo", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_releases", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_traffic", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_jsdelivr", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_workshop_feedback", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_achievement_progress", fail_network)
    monkeypatch.setattr(
        build_metrics,
        "fetch_workshop_certification",
        fail_network,
    )
    monkeypatch.setattr(build_metrics, "fetch_rar_source", fail_network)
    monkeypatch.setattr(
        sys,
        "argv",
        ["build_metrics.py", "--offline", "--out", str(tmp_path / "metrics.json")],
    )

    assert build_metrics.main() == 0


def test_merge_history_records_source_specific_tracking_windows(tmp_path):
    history_path = tmp_path / "metrics_history.json"
    traffic = {
        "clones": {"daily": []},
        "views": {
            "daily": [
                {"date": "2026-08-01", "count": 3, "uniques": 2}
            ]
        },
    }
    jsdelivr = {
        "package_available": True,
        "daily": [],
    }

    build_metrics.merge_history(
        traffic,
        jsdelivr,
        history_path,
        run_at="2026-08-01T12:00:00Z",
    )
    build_metrics.merge_history(
        traffic,
        jsdelivr,
        history_path,
        run_at="2026-08-09T12:00:00Z",
    )

    history = json.loads(history_path.read_text())
    assert history["tracking"] == {
        "clones_since": "2026-08-01",
        "clones_last": "2026-08-09",
        "views_since": "2026-08-01",
        "views_last": "2026-08-09",
        "cdn_since": "2026-08-01",
        "cdn_last": "2026-08-09",
    }
    assert history["views"]["2026-08-01"] == {
        "count": 3,
        "uniques": 2,
    }


def test_rar_federation_separates_fetches_acquisitions_and_usage():
    registry = {
        "schema": build_metrics.RAR_REGISTRY_SCHEMA,
        "agents": [
            {
                "name": "@aibast-agents-library/account_intelligence",
                "display_name": "Account Intelligence",
                "_file": "agents/@aibast/account_intelligence_agent.py",
                "_install_filename": "account_intelligence.py",
                "_sha256": "a" * 64,
            },
            {
                "name": "@rapp/learn_new",
                "display_name": "Learn New",
                "_file": "agents/@rapp/learn_new_agent.py",
                "_install_filename": "learn_new.py",
                "_sha256": "b" * 64,
            },
            {
                "name": "@rapp/no_observed_download",
                "display_name": "No Observed Download",
                "_file": "agents/@rapp/no_observed_download_agent.py",
                "_install_filename": "no_observed_download.py",
                "_sha256": "c" * 64,
            },
        ],
    }
    metrics = {
        "schema": build_metrics.RAR_METRICS_SCHEMA,
        "generated_at": "2026-08-09T12:00:00Z",
        "totals": {
            "agent_file_downloads": 5,
            "downloads": 100,
            "clones": 90,
            "page_views": 50,
        },
        "cdn": {
            "files": [
                {
                    "agent": "@aibast-agents-library/account_intelligence",
                    "hits": 3,
                    "kind": "agent",
                },
                {
                    "agent": "@rapp/learn_new",
                    "hits": 2,
                    "kind": "agent",
                },
            ]
        },
        "traffic": {"as_of": "2026-08-09T12:00:00Z"},
    }
    ratings = {
        "schema": build_metrics.RAR_DISCUSSION_SCHEMA,
        "agents": {
            "@aibast-agents-library/account_intelligence": {
                "downloads": 1,
                "upvotes": 2,
                "comments": 1,
                "signals": {
                    "worked": 1,
                    "did_not_work": 0,
                    "stuck": 0,
                    "regular_use": 1,
                    "shipped": 0,
                    "want_to_try": 1,
                    "saved_time": 1,
                },
                "url": "https://github.com/kody-w/RAR/discussions/1",
            },
            "@rapp/learn_new": {
                "downloads": 2,
                "upvotes": 1,
                "comments": 3,
                "signals": {
                    "worked": 2,
                    "did_not_work": 1,
                    "stuck": 0,
                    "regular_use": 1,
                    "shipped": 1,
                    "want_to_try": 2,
                    "saved_time": 1,
                },
                "url": "https://github.com/kody-w/RAR/discussions/2",
            },
        },
    }
    releases = [
        {
            "assets": [
                {
                    "name": "account_intelligence.py",
                    "download_count": 4,
                },
                {"name": "learn_new.py", "download_count": 1},
                {"name": "unmapped.zip", "download_count": 2},
            ]
        }
    ]

    rar = build_metrics.build_rar_source(
        registry,
        metrics,
        ratings,
        releases,
        generated_at="2026-08-09T12:00:00Z",
    )

    assert rar["status"] == "partial"
    assert rar["totals"]["agent_cdn_fetches"] == 5
    assert rar["totals"]["agent_release_fetches"] == 5
    assert rar["totals"]["unmapped_release_fetches"] == 2
    assert rar["totals"]["agent_acquisitions"] == 3
    assert rar["totals"]["positive_reactions"] == 3
    assert rar["totals"]["usage_signals"]["worked"] == 3
    assert rar["totals"]["usage_signals"]["shipped"] == 1
    no_observation = next(
        row
        for row in rar["agents"]
        if row["rar_name"] == "@rapp/no_observed_download"
    )
    assert no_observation["rar_cdn_fetches"] is None
    assert no_observation["rar_release_fetches"] == 0
    assert no_observation["rar_acquisitions"] is None

    local_agents = {
        "@aibast-agents-library/account-intelligence": {
            "display_name": "Account Intelligence",
            "downloads": 10,
        },
        "@aibast-agents-library/local-only": {
            "display_name": "Local Only",
            "downloads": 1,
        },
    }
    ecosystem = build_metrics.build_ecosystem_metrics(
        local_agents,
        11,
        rar,
        generated_at="2026-08-09T12:00:00Z",
    )
    assert ecosystem["totals"][
        "combined_agent_distribution_fetch_events"
    ] == 21
    assert ecosystem["totals"]["rar_agent_acquisitions"] == 3
    assert ecosystem["totals"]["overlap_agents"] == 1
    assert ecosystem["totals"]["distribution_entries"] == 5
    account = next(
        row
        for row in ecosystem["agents"]
        if row["logical_name"]
        == "@aibast-agents-library/account-intelligence"
    )
    assert account["channels"] == ["aibast", "rar"]
    assert account["combined_distribution_fetch_events"] == 17


def test_current_aibast_only_snapshot_reconciles_and_is_privacy_safe():
    snapshot = json.loads(
        (REPO_ROOT / "state" / "metrics.json").read_text(encoding="utf-8")
    )
    ecosystem = snapshot["ecosystem"]
    totals = ecosystem["totals"]
    rar = ecosystem["sources"]["rar"]
    rows = ecosystem["agents"]

    assert ecosystem["schema"] == "aibast-ecosystem-metrics/1.0"
    assert rar == {
        "status": "excluded",
        "reason": (
            "RAR federation is intentionally excluded from AIBAST library "
            "counts."
        ),
    }
    assert len(rows) == totals["logical_agents"]
    assert totals["combined_agent_distribution_fetch_events"] == totals[
        "aibast_direct_agent_fetches"
    ]
    assert snapshot["totals"][
        "global_agent_distribution_fetch_events"
    ] == totals["combined_agent_distribution_fetch_events"]
    assert not any(key.startswith("rar_") for key in snapshot["totals"])
    assert not any(key.startswith("rar_") for key in totals)
    assert all(row["channels"] == ["aibast"] for row in rows)
    assert all(
        not any(key.startswith("rar_") for key in row)
        for row in rows
    )
    serialized = json.dumps(ecosystem)
    for forbidden in ('"login"', '"email"', '"token"', '"body"'):
        assert forbidden not in serialized


def test_achievement_claim_parser_requires_exact_canonical_fields_and_mapping():
    catalog = workshop_catalog()
    assert "authenticated issue authorship" in build_metrics.ACHIEVEMENT_CAVEAT
    assert "canonical claim format only" in build_metrics.ACHIEVEMENT_CAVEAT
    assert "self-reported" in build_metrics.ACHIEVEMENT_CAVEAT
    assert "not independently proven" in build_metrics.ACHIEVEMENT_CAVEAT
    assert build_metrics.ACHIEVEMENT_POINTS == {
        "started": 5,
        "local-proof": 15,
        "draft-builder": 20,
        "preview-proven": 25,
        "workshop-completed": 35,
        "hard-mode-completed": 50,
    }
    valid = achievement_claim_body(
        achievements=build_metrics.ACHIEVEMENT_ORDER,
    )

    assert build_metrics.parse_achievement_claim(valid, catalog) == {
        "workshop": "account-intelligence",
        "agent": "@aibast-agents-library/account-intelligence",
        "achievements": list(build_metrics.ACHIEVEMENT_ORDER),
        "source": "achievements.html",
    }
    invalid = (
        "\n" + valid,
        valid + "This optional prose is not part of the canonical shape.\n",
        valid.replace("aibast-achievement-progress/1.0", "wrong/1.0"),
        valid.replace(
            "- Workshop: `account-intelligence`",
            "- Workshop: `grid-outage-response`",
        ),
        valid.replace(
            "- Agent: `@aibast-agents-library/account-intelligence`",
            "- Agent: `@aibast-agents-library/deal-progression`",
        ),
        valid.replace("- Source quest URL: achievements.html\n", ""),
        valid + "- Achievements: `started`\n",
        valid + "- Source: duplicate-source\n",
        valid.replace(
            "- Achievements:",
            "> - Achievements:",
        ),
        valid.replace(
            "- Achievements: `started, local-proof, draft-builder, preview-proven, workshop-completed, hard-mode-completed`",
            '- Achievements: "started"',
        ),
        achievement_claim_body(achievements=("started", "started")),
        achievement_claim_body(achievements=("started", "unknown-achievement")),
        achievement_claim_body(achievements=("local-proof", "started")),
        achievement_claim_body(achievements=("local-proof",)),
        achievement_claim_body(achievements=("started", "workshop-completed")),
        achievement_claim_body(achievements=("hard-mode-completed",)),
        valid.replace(
            "<!-- aibast-achievement-progress:v1 -->",
            "<!-- aibast-achievements-achievement:v1 -->",
        ),
        valid + "- Event: `completed`\n",
        valid + "- Points: 999999\n",
        valid + "- Point: 999999\n",
        valid + "- Score: 999999\n",
        valid + "- points: 999999\n",
        valid + "- SCORE: 999999\n",
        valid + "> - Points: 999999\n",
    )
    assert all(
        build_metrics.parse_achievement_claim(body, catalog) is None
        for body in invalid
    )


def test_achievement_hard_completion_remains_separate_and_does_not_infer_badges():
    result = build_metrics.group_achievement_progress(
        [
            {
                "user": {"login": "HardUser"},
                "body": achievement_claim_body(
                    achievements=("started", "hard-mode-completed"),
                ),
            }
        ],
        workshop_catalog(),
    )

    profile = result["profiles"][0]
    assert profile["points"] == 55
    assert profile["achievement_count"] == 2
    assert profile["starts"] == 1
    assert profile["workshop_completions"] == 0
    assert profile["hard_completions"] == 1
    assert profile["completed_workshops"] == []
    assert profile["achievement_ids"] == [
        "account-intelligence:started",
        "account-intelligence:hard-mode-completed",
    ]
    assert result["totals"]["achievement_completion_rate"] == 33.3


def test_fetch_achievement_progress_uses_only_the_new_marker(monkeypatch):
    current = {
        "state": "closed",
        "user": {"login": "CurrentUser"},
        "body": achievement_claim_body(
            achievements=("started", "local-proof"),
        ),
    }
    obsolete = {
        "state": "open",
        "user": {"login": "OldUser"},
        "body": achievement_claim_body().replace(
            "<!-- aibast-achievement-progress:v1 -->",
            "<!-- aibast-achievements-achievement:v1 -->",
        ),
    }
    monkeypatch.setattr(
        build_metrics,
        "fetch_issue_pages",
        lambda _token: {
            "available": True,
            "complete": True,
            "pages": 1,
            "issues": [obsolete, current],
        },
    )

    result = build_metrics.fetch_achievement_progress(
        "token",
        workshop_catalog(),
        as_of="2026-08-09T12:00:00Z",
    )

    assert result["status"] == "available"
    assert result["coverage"]["issues_scanned"] == 1
    assert result["totals"]["participants"] == 1
    assert result["totals"]["points"] == 20
    assert result["profiles"][0]["login"] == "CurrentUser"


def test_achievement_progress_union_scores_every_explicit_badge_once_and_is_idempotent():
    catalog = workshop_catalog()
    issues = [
        {
            "number": 1,
            "state": "open",
            "user": {"login": "Alice"},
            "body": achievement_claim_body(
                extra="This free text must not persist.\n"
            ),
        },
        {
            "number": 2,
            "state": "closed",
            "user": {"login": "alice"},
            "body": achievement_claim_body(),
        },
        {
            "number": 3,
            "state": "edited",
            "user": {"login": "ALICE"},
            "body": achievement_claim_body(
                achievements=("started", "local-proof", "draft-builder"),
            ),
        },
        {
            "id": 9004,
            "state": "closed",
            "user": {"login": "alice"},
            "body": achievement_claim_body(
                achievements=(
                    "started",
                    "local-proof",
                    "draft-builder",
                    "preview-proven",
                    "workshop-completed",
                ),
                source="https://example.invalid/private-source",
            ),
        },
        {
            "id": 9005,
            "state": "closed",
            "user": {"login": "Bob"},
            "body": achievement_claim_body(
                achievements=build_metrics.ACHIEVEMENT_ORDER,
            ),
        },
        {
            "number": 6,
            "state": "open",
            "user": {"login": "carol"},
            "body": achievement_claim_body(
                workshop="deal-progression",
                agent="@aibast-agents-library/deal-progression",
            ),
        },
    ]

    result = build_metrics.group_achievement_progress(
        issues,
        catalog,
        as_of="2026-08-09T12:00:00Z",
    )
    replay = build_metrics.group_achievement_progress(
        list(reversed(issues)),
        catalog,
        as_of="2026-08-09T12:00:00Z",
    )

    assert result == replay
    assert result["totals"] == {
        "participants": 3,
        "points": 255,
        "achievements": 12,
        "starts": 3,
        "workshop_completions": 2,
        "hard_completions": 1,
        "completion_rate": 66.7,
        "hard_completion_rate": 33.3,
        "achievement_completion_rate": 66.7,
    }
    assert [profile["login"].casefold() for profile in result["profiles"]] == [
        "bob",
        "alice",
        "carol",
    ]
    alice = result["profiles"][1]
    assert alice == {
        "login": "ALICE",
        "points": 100,
        "achievement_count": 5,
        "starts": 1,
        "workshop_completions": 1,
        "hard_completions": 0,
        "badges": [
            {
                "workshop": "account-intelligence",
                "achievement": achievement_id,
                "points": build_metrics.ACHIEVEMENT_POINTS[achievement_id],
            }
            for achievement_id in build_metrics.ACHIEVEMENT_ORDER[:-1]
        ],
        "achievement_ids": [
            f"account-intelligence:{achievement_id}"
            for achievement_id in build_metrics.ACHIEVEMENT_ORDER[:-1]
        ],
        "completed_workshops": ["account-intelligence"],
    }
    bob = result["profiles"][0]
    assert bob["starts"] == 1
    assert bob["workshop_completions"] == 1
    assert bob["hard_completions"] == 1
    assert bob["points"] == 150
    assert result["coverage"]["diagnostics"]["accepted_issues"] == 5
    assert result["coverage"]["diagnostics"]["accepted_achievements"] == 12
    assert result["coverage"]["diagnostics"]["duplicate_achievements"] == 4
    assert result["coverage"]["diagnostics"]["invalid_issues"] == 1
    account = next(
        row
        for row in result["workshops"]
        if row["slug"] == "account-intelligence"
    )
    assert account["starts"] == 2
    assert account["workshop_completions"] == 2
    assert account["hard_completions"] == 1
    assert account["points"] == 250
    assert account["achievements"] == 11
    assert account["completion_rate"] == 100.0
    assert account["hard_completion_rate"] == 50.0
    assert account["achievement_completion_rate"] == 91.7
    assert account["achievement_counts"]["started"] == 2
    assert account["achievement_counts"]["hard-mode-completed"] == 1
    started = result["achievements"][0]
    assert started["id"] == "started"
    assert started["claims"] == 3
    assert started["attainment_rate"] == 100.0
    serialized = json.dumps(result)
    for forbidden in (
        "This free text must not persist",
        "private-source",
        '"number"',
        '"body"',
        "9004",
        "9005",
    ):
        assert forbidden not in serialized


def test_achievement_rejects_prs_unknown_users_and_invalid_claims_without_leaking_identity():
    catalog = workshop_catalog()
    issues = [
        {
            "number": 1,
            "user": {"login": "Valid-user"},
            "body": achievement_claim_body(),
            "pull_request": {"url": "https://example.invalid/pr/1"},
        },
        {"number": 2, "user": None, "body": achievement_claim_body()},
        {
            "number": 3,
            "user": {"login": "invalid_user"},
            "body": achievement_claim_body(),
        },
        {
            "number": 4,
            "user": {"login": "Mallory"},
            "body": achievement_claim_body(
                workshop="unknown-workshop",
                agent="@aibast-agents-library/account-intelligence",
            ),
        },
        {
            "number": 5,
            "user": {"login": "Oscar"},
            "body": achievement_claim_body() + "- Source: duplicate\n",
        },
    ]

    result = build_metrics.group_achievement_progress(issues, catalog)

    assert result["profiles"] == []
    assert result["totals"]["participants"] == 0
    assert result["coverage"]["diagnostics"] == {
        "accepted_issues": 0,
        "accepted_achievements": 0,
        "duplicate_achievements": 0,
        "invalid_issues": 2,
        "invalid_users": 2,
        "pull_requests": 1,
    }
    serialized = json.dumps(result)
    assert "Mallory" not in serialized
    assert "Oscar" not in serialized


def test_offline_carries_achievement_profiles_and_no_prior_leaves_nulls(tmp_path):
    catalog = workshop_catalog()
    prior_at = "2026-08-08T10:00:00Z"
    prior_achievements = build_metrics.group_achievement_progress(
        [
            {
                "state": "closed",
                "user": {"login": "OptedIn"},
                "body": achievement_claim_body(
                    achievements=build_metrics.ACHIEVEMENT_ORDER,
                ),
            }
        ],
        catalog,
        as_of=prior_at,
    )
    prior_achievements["caveat"] = "Legacy caveat without verification scope."
    out = tmp_path / "metrics.json"
    out.write_text(
        json.dumps({
            "schema": "aibast-metrics/1.0",
            "generated_at": prior_at,
            "achievements": prior_achievements,
        }),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_metrics.py"),
            "--offline",
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO_ROOT),
    )

    assert result.returncode == 0, result.stderr
    achievements = json.loads(out.read_text(encoding="utf-8"))["achievements"]
    assert achievements["carried_forward"] is True
    assert achievements["as_of"] == prior_at
    assert achievements["coverage"]["carried_forward"] is True
    assert achievements["totals"] == prior_achievements["totals"]
    assert achievements["profiles"] == prior_achievements["profiles"]
    assert achievements["caveat"] == build_metrics.ACHIEVEMENT_CAVEAT


def test_obsolete_event_snapshot_is_not_carried_forward():
    catalog = workshop_catalog()
    prior = {
        "generated_at": "2026-08-08T10:00:00Z",
        "achievements": {
            "schema": "aibast-achievements/1.0",
            "status": "available",
            "profiles": [{"login": "OldEventProfile", "score": 100}],
            "workshops": [{"slug": row["slug"]} for row in catalog],
        },
    }

    achievements = build_metrics.carry_forward_achievements(prior, catalog)

    assert achievements["schema"] == "aibast-achievements/2.0"
    assert achievements["status"] == "unavailable"
    assert achievements["profiles"] == []
    assert all(value is None for value in achievements["totals"].values())


def test_achievement_points_never_enter_usage_upvotes_or_download_totals():
    catalog = workshop_catalog()
    achievements = build_metrics.group_achievement_progress(
        [
            {
                "user": {"login": "Participant"},
                "body": achievement_claim_body(
                    achievements=build_metrics.ACHIEVEMENT_ORDER,
                ),
            }
        ],
        catalog,
    )
    workshop_metrics = build_metrics.build_workshop_metrics(
        catalog,
        path_rows=[],
        download_counts={
            row["slug"]: {"file_downloads": 0, "bundle_downloads": 0}
            for row in catalog
        },
        feedback_counts={
            row["slug"]: {
                "feedback_reports": 0,
                "feedback_open": 0,
                "feedback_closed": 0,
            }
            for row in catalog
        },
        agent_upvotes={row["catalog_key"]: 0 for row in catalog},
    )

    assert achievements["totals"]["points"] == 150
    assert workshop_metrics["totals"]["usage_events"] == 0
    assert workshop_metrics["totals"]["agent_upvotes"] == 0
    assert "points" not in workshop_metrics["totals"]


def test_offline_carries_remote_blocks_and_recomputes_local_scope(tmp_path):
    out = tmp_path / "metrics.json"
    prior_at = "2026-08-01T12:00:00Z"
    prior_totals = {field: 9 for field in build_metrics.REMOTE_TOTAL_FIELDS}
    prior_totals["tracking_since"] = "2026-07-01"
    prior_totals["agent_upvotes"] = 3
    prior = {
        "schema": "aibast-metrics/1.0",
        "generated_at": prior_at,
        "repo": {"stars": 7, "forks": 2, "as_of": prior_at},
        "totals": prior_totals,
        "daily": [{"date": "2026-08-01", "clones": 1, "views": 2, "cdn": 3}],
        "traffic": {
            "paths": [],
            "referrers": [],
            "clones_14d": 4,
            "views_14d": 5,
            "live": True,
            "as_of": prior_at,
        },
        "cdn": {
            "total_hits": 6,
            "bandwidth": 10,
            "rank": 2,
            "agent_hits": 3,
            "installer_hits": 1,
            "files": [],
            "as_of": prior_at,
        },
        "releases": {
            "total_downloads": 8,
            "count": 1,
            "releases": [],
            "as_of": prior_at,
        },
        "agent_metrics": [
            {
                "name": "@aibast-agents-library/account-intelligence",
                "downloads": 2,
                "upvotes": 3,
                "upvote_discussion_url": (
                    "https://github.com/microsoft/"
                    "aibast-agents-library/discussions/10"
                ),
            }
        ],
        "agent_upvote_coverage": {
            "status": "available",
            "as_of": prior_at,
        },
        "file_metrics": {
            "schema": "aibast-file-metrics/1.0",
            "source_status": "censored",
            "as_of": prior_at,
            "rows": [
                {
                    "path": "agents/@aibast-agents-library/b2b_sales_stacks/"
                    "account_intelligence_stack/account_intelligence_agent.py",
                    "kind": "agent",
                    "downloads": 2,
                    "status": "observed",
                },
                {
                    "path": "solutions/account-intelligence/quest.html",
                    "kind": "workshop",
                    "downloads": 2,
                    "status": "observed",
                },
            ],
        },
        "workshops": {
            "as_of": prior_at,
            "coverage": {
                "status": "partial",
                "views": {"status": "live popular-path response"},
                "downloads": {"status": "complete paginated jsDelivr file response"},
                "feedback": {"status": "workshop-feedback label"},
            },
            "rows": [
                {
                    "catalog_key": "@aibast-agents-library/account-intelligence",
                    "slug": "account-intelligence",
                    "views_14d": 5,
                    "view_uniques_14d": 3,
                    "view_observed": True,
                    "file_downloads": 4,
                    "bundle_downloads": 2,
                    "feedback_reports": 1,
                    "feedback_open": 1,
                    "feedback_closed": 0,
                }
            ],
        },
    }
    out.write_text(json.dumps(prior), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_metrics.py"),
            "--offline",
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO_ROOT),
    )

    assert result.returncode == 0, result.stderr
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["repo"]["stars"] == 7
    assert doc["repo"]["as_of"] == prior_at
    assert doc["repo"]["carried_forward"] is True
    assert doc["traffic"]["as_of"] == prior_at
    assert doc["traffic"]["carried_forward"] is True
    assert doc["cdn"]["total_hits"] == 6
    assert doc["cdn"]["carried_forward"] is True
    assert doc["releases"]["total_downloads"] == 8
    assert doc["releases"]["carried_forward"] is True
    assert doc["daily"] == prior["daily"]
    for field, value in prior_totals.items():
        if field not in {
            "agent_file_downloads",
            "installer_downloads",
            "skill_downloads",
            "agent_upvotes",
            "agent_acquisitions",
        }:
            assert doc["totals"][field] == value
    assert doc["totals"]["agent_file_downloads"] == 2
    assert doc["totals"]["installer_downloads"] is None
    assert doc["totals"]["skill_downloads"] is None
    assert doc["totals"]["agent_upvotes"] == 3
    assert doc["totals"]["agent_acquisitions"] is None
    assert doc["file_metrics"]["carried_forward"] is True
    assert doc["file_metrics"]["as_of"] == prior_at
    assert len(doc["file_metrics"]["rows"]) == len(
        build_metrics.tracked_repository_files()
    )
    assert doc["workshops"]["as_of"] == prior_at
    assert doc["workshops"]["carried_forward"] is True
    assert doc["agent_upvote_coverage"]["carried_forward"] is True
    assert doc["totals"]["agent_upvotes"] == 3
    account_agent = next(
        row for row in doc["agent_metrics"]
        if row["name"] == "@aibast-agents-library/account-intelligence"
    )
    assert account_agent["upvotes"] == 3
    assert len(doc["workshops"]["rows"]) == 51
    account = next(
        row for row in doc["workshops"]["rows"]
        if row["slug"] == "account-intelligence"
    )
    assert account["usage_events"] == 10
    assert account["agent_name"] == "@aibast-agents-library/account-intelligence"
    assert account["agent_upvotes"] == 3
    assert account["file_downloads"] == 4
    assert account["bundle_downloads"] is None
    assert account["feedback_open"] == 1
    assert account["feedback_closed"] == 0


def test_repo_metrics_publish_repository_stars_only(monkeypatch):
    monkeypatch.setattr(
        build_metrics,
        "fetch_public",
        lambda _url, _token=None: {
            "stargazers_count": 42,
            "forks_count": 7,
            "subscribers_count": 3,
            "open_issues_count": 2,
        },
    )

    repo = build_metrics.fetch_repo(None)

    assert repo["stars"] == 42
    assert "upvotes" not in repo


def test_metrics_target_can_be_parameterized_without_changing_defaults(tmp_path):
    out = tmp_path / "fork-metrics.json"
    out.write_text(
        json.dumps(
            {
                "repo": {
                    "owner": "stale-owner",
                    "name": "stale-repo",
                    "url": "https://github.com/stale-owner/stale-repo",
                    "site": "https://stale-owner.github.io/stale-repo/",
                },
                "totals": {"agent_upvotes": 9},
                "agent_metrics": [
                    {
                        "name": "@aibast-agents-library/account-intelligence",
                        "upvotes": 9,
                        "upvote_discussion_url": (
                            "https://github.com/kody-w/"
                            "aibast-agents-library-proof/discussions/not-a-number"
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "METRICS_OWNER": "kody-w",
        "METRICS_REPO": "aibast-agents-library-proof",
    }
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_metrics.py"),
            "--offline",
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO_ROOT),
        env=env,
    )

    assert result.returncode == 0, result.stderr
    repo = json.loads(out.read_text(encoding="utf-8"))["repo"]
    assert repo["owner"] == "kody-w"
    assert repo["name"] == "aibast-agents-library-proof"
    assert repo["url"] == "https://github.com/kody-w/aibast-agents-library-proof"
    assert repo["site"] == "https://kody-w.github.io/aibast-agents-library-proof/"
    doc = json.loads(out.read_text(encoding="utf-8"))
    account = next(
        row
        for row in doc["agent_metrics"]
        if row["name"] == "@aibast-agents-library/account-intelligence"
    )
    assert account["upvotes"] is None
    assert account["upvote_discussion_url"] is None
    assert doc["totals"]["agent_upvotes"] is None
    assert build_metrics.OWNER == "microsoft"
    assert build_metrics.REPO == "aibast-agents-library"


def test_workshop_catalog_has_exact_advertised_quest_rows():
    rows = workshop_catalog()
    slugs = {row["slug"] for row in rows}
    catalog_keys = set(
        json.loads(
            (REPO_ROOT / "solutions" / "catalog.json").read_text(encoding="utf-8")
        )["solutions"]
    )

    assert len(rows) == 51
    assert len(slugs) == 51
    assert {row["catalog_key"] for row in rows} == catalog_keys
    assert "grid-outage-response" not in slugs
    assert all(row["quest_url"] == f"solutions/{row['slug']}/quest.html" for row in rows)
    assert all(row["display_name"] for row in rows)
    production = next(
        row for row in rows
        if row["catalog_key"].endswith("/production-line-optimization")
    )
    assert production["slug"] == "product-line-optimization"
    assert {
        rule["path"] for rule in production["path_rules"]
    } >= {
        "solutions/product-line-optimization/",
        "agents/@aibast-agents-library/manufacturing_stacks/"
        "production_line_optimization_stack/",
        "agents/@aibast-agents-library/manufacturing_stacks/"
        "production_line_optimization_stack/production_line_optimization_agent.py",
    }


def test_file_scope_covers_every_tracked_file_and_classifies_all_skills():
    registry = load_registry()
    catalog = workshop_catalog()
    scope = build_metrics.build_file_scope(registry, catalog)
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        check=True,
    )
    tracked = {
        value.decode("utf-8")
        for value in result.stdout.split(b"\0")
        if value and not build_metrics._excluded_repository_path(value.decode("utf-8"))
    }

    assert {row["path"] for row in scope} == tracked
    assert len(scope) == len(tracked)
    skill_paths = {path for path in tracked if Path(path).name.casefold() == "skill.md"}
    classified_skills = {
        row["path"] for row in scope if row["kind"] == "skill"
    }
    assert skill_paths
    assert classified_skills == skill_paths
    assert "skill.md" in classified_skills
    assert any(
        path.startswith("solutions/") and "/manual/skills/" in path
        for path in classified_skills
    )
    assert build_metrics.classify_repository_file(
        "agents/example.py", "@aibast-agents-library/example"
    ) == "agent"
    assert build_metrics.classify_repository_file("skill.md") == "skill"
    assert build_metrics.classify_repository_file(
        "solutions/example/quest.html"
    ) == "workshop"
    assert build_metrics.classify_repository_file(
        "exports/example-source.zip"
    ) == "source_bundle"
    assert build_metrics.classify_repository_file(
        "solutions/example/exports/example-source.zip"
    ) == "source_bundle"
    assert build_metrics.classify_repository_file("install.sh") == "installer"
    assert build_metrics.classify_repository_file("README.md") == "documentation"
    assert build_metrics.classify_repository_file("registry.json") == "catalog"
    assert build_metrics.classify_repository_file("tools/example.py") == "code"
    assert build_metrics.classify_repository_file("images/example.png") == "asset"


def test_tracked_file_fallback_excludes_work_caches_and_temp(monkeypatch, tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    (tmp_path / "work").mkdir()
    (tmp_path / "work" / "scratch.md").write_text("scratch", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.pyc").write_bytes(b"cache")
    (tmp_path / "generated.tmp").write_text("temp", encoding="utf-8")
    monkeypatch.setattr(
        build_metrics.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("git unavailable")),
    )

    assert build_metrics.tracked_repository_files(tmp_path) == ["docs/guide.md"]


def test_file_metrics_complete_zero_vs_censored_null_and_kind_totals():
    scope = [
        {
            "path": "skill.md",
            "kind": "skill",
            "agent_name": None,
            "workshop_slug": None,
        },
        {
            "path": "README.md",
            "kind": "documentation",
            "agent_name": None,
            "workshop_slug": None,
        },
    ]
    observed = [{"name": "/skill.md", "hits": {"total": 4}}]

    complete = build_metrics.build_file_metrics(
        scope,
        observed,
        available=True,
        complete=True,
        as_of="2026-08-09T00:00:00Z",
    )
    complete_rows = {row["path"]: row for row in complete["rows"]}
    assert complete_rows["skill.md"]["downloads"] == 4
    assert complete_rows["README.md"]["downloads"] == 0
    assert complete_rows["README.md"]["status"] == "observed_zero"
    assert complete["totals"]["downloads"] == 4
    assert complete["totals"]["by_kind"]["skill"]["downloads"] == 4
    assert complete["totals"]["by_kind"]["documentation"]["downloads"] == 0

    censored = build_metrics.build_file_metrics(
        scope,
        observed,
        available=True,
        complete=False,
        as_of="2026-08-09T00:00:00Z",
    )
    censored_rows = {row["path"]: row for row in censored["rows"]}
    assert censored_rows["skill.md"]["downloads"] == 4
    assert censored_rows["README.md"]["downloads"] is None
    assert censored_rows["README.md"]["status"] == "not_observed"
    assert censored["source_status"] == "censored"


def test_file_ledger_rollups_reconcile_agents_workshops_and_bundles():
    scope = [
        {
            "path": "agents/example_agent.py",
            "kind": "agent",
            "agent_name": "@aibast-agents-library/example",
            "workshop_slug": "example",
        },
        {
            "path": "solutions/example/manual/skills/demo/SKILL.md",
            "kind": "skill",
            "agent_name": None,
            "workshop_slug": "example",
        },
        {
            "path": "exports/example-source.zip",
            "kind": "source_bundle",
            "agent_name": None,
            "workshop_slug": "example",
        },
    ]
    metrics = build_metrics.build_file_metrics(
        scope,
        [
            {"name": "/agents/example_agent.py", "hits": {"total": 3}},
            {
                "name": "/solutions/example/manual/skills/demo/SKILL.md",
                "hits": {"total": 5},
            },
            {"name": "/exports/example-source.zip", "hits": {"total": 7}},
        ],
        available=True,
        complete=True,
        as_of="2026-08-09T00:00:00Z",
    )
    rollup = build_metrics.workshop_downloads_from_file_metrics(
        metrics, {"example"}
    )

    assert rollup["example"] == {
        "file_downloads": 8,
        "bundle_downloads": 7,
    }
    assert metrics["totals"]["downloads"] == 15
    assert metrics["totals"]["downloads"] == sum(
        values["downloads"]
        for values in metrics["totals"]["by_kind"].values()
        if values["downloads"] is not None
    )


def test_workshop_popular_paths_normalize_dedupe_and_reject_lookalikes():
    catalog = workshop_catalog()
    result = build_metrics.group_workshop_paths(
        [
            {
                "path": "https://github.com/microsoft/aibast-agents-library/blob/main/solutions/account-intelligence/quest.html?tab=readme#top",
                "count": 8,
                "uniques": 5,
            },
            {
                "path": "/microsoft/aibast-agents-library/blob/main/solutions/account-intelligence/quest.html",
                "count": 8,
                "uniques": 5,
            },
            {
                "path": "/microsoft/aibast-agents-library/blob/main/solutions/account-intelligence/quest.html",
                "count": 10,
                "uniques": 6,
            },
            {
                "path": "/microsoft/aibast-agents-library/tree/main/agents/@aibast-agents-library/manufacturing_stacks/production_line_optimization_stack/readme.md",
                "count": 3,
                "uniques": 2,
            },
            {
                "path": "https://github.com/other/repo/blob/main/solutions/account-intelligence/quest.html",
                "count": 100,
                "uniques": 90,
            },
            {
                "path": "/solutions/account-intelligence/%2e%2e/deal-progression/quest.html",
                "count": 50,
                "uniques": 40,
            },
            {
                "path": "/solutions/account-intelligence-lookalike/quest.html",
                "count": 70,
                "uniques": 60,
            },
        ],
        catalog,
        return_diagnostics=True,
    )
    grouped = result["counts"]

    assert grouped["account-intelligence"] == {
        "views_14d": 10,
        "view_uniques_14d": 6,
        "view_observed": True,
    }
    assert grouped["product-line-optimization"]["views_14d"] == 3
    assert grouped["deal-progression"] == {
        "views_14d": None,
        "view_uniques_14d": None,
        "view_observed": False,
    }
    assert "grid-outage-response" not in grouped
    assert result["diagnostics"]["duplicate_rows"] == 1
    assert result["diagnostics"]["conflicting_duplicates"] == [
        "solutions/account-intelligence/quest.html"
    ]
    assert result["diagnostics"]["rejected_rows"] == 2


def test_workshop_downloads_validate_dedupe_and_partition():
    result = build_metrics.group_workshop_downloads(
        [
            {
                "name": "/solutions/account-intelligence/quest.html",
                "hits": {"total": 12},
            },
            {
                "name": "/solutions/account-intelligence/quest.html",
                "hits": {"total": 12},
            },
            {
                "name": "/solutions/account-intelligence/quest.html",
                "hits": {"total": 10},
            },
            {
                "name": "/solutions/account-intelligence/assets/diagram.svg",
                "hits": {"total": 4},
            },
            {
                "name": "/exports/account-intelligence-source.zip",
                "hits": {"total": 6},
            },
            {
                "name": "/exports/grid-outage-response-source.zip",
                "hits": {"total": 90},
            },
            {
                "name": "/solutions/account-intelligence/assets/bad.svg",
                "hits": {"total": -1},
            },
            {
                "name": "/solutions/account-intelligence/assets/string.svg",
                "hits": {"total": "7"},
            },
        ],
        {"account-intelligence", "deal-progression"},
        return_diagnostics=True,
    )
    grouped = result["counts"]

    assert grouped["account-intelligence"] == {
        "file_downloads": 16,
        "bundle_downloads": 6,
    }
    assert grouped["deal-progression"] == {
        "file_downloads": 0,
        "bundle_downloads": 0,
    }
    assert result["diagnostics"]["duplicate_rows"] == 1
    assert result["diagnostics"]["conflicting_duplicates"] == [
        "solutions/account-intelligence/quest.html"
    ]
    assert result["diagnostics"]["invalid_rows"] == 2
    assert sum(grouped["account-intelligence"].values()) == 22


def test_jsdelivr_file_pagination_continues_and_detects_unsupported_pages(monkeypatch):
    calls = []
    pages = iter([
        [{"name": "/a", "hits": {"total": 1}}, {"name": "/b", "hits": {"total": 2}}],
        [{"name": "/c", "hits": {"total": 3}}],
    ])
    monkeypatch.setattr(
        build_metrics,
        "fetch_json",
        lambda url, token=None: calls.append(url) or next(pages),
    )

    result = build_metrics.fetch_jsdelivr_file_pages(page_size=2)

    assert result["complete"] is True
    assert result["pages"] == 2
    assert len(result["files"]) == 3
    assert "page=1" in calls[0] and "page=2" in calls[1]

    repeated = [{"name": "/a", "hits": {"total": 1}}]
    monkeypatch.setattr(
        build_metrics,
        "fetch_json",
        lambda _url, token=None: repeated,
    )
    unsupported = build_metrics.fetch_jsdelivr_file_pages(page_size=1)
    assert unsupported["complete"] is False
    assert unsupported["pagination"] == "page parameter unsupported"
    assert len(unsupported["files"]) == 1


def test_workshop_feedback_requires_strict_schema_and_deduplicates(monkeypatch):
    body = """<!-- aibast-workshop-feedback:v1 -->
## Workshop signal
- Schema: `aibast-workshop-feedback/1.0`
- Solution: `@aibast-agents-library/account-intelligence`
"""
    assert build_metrics.parse_feedback_solution(
        body, {"account-intelligence"}
    ) == "account-intelligence"
    assert build_metrics.parse_feedback_solution(
        "\n" + body,
        {"account-intelligence"},
    ) is None
    assert build_metrics.parse_feedback_solution(
        body + "- Solution: `@aibast-agents-library/account-intelligence`\n",
        {"account-intelligence"},
    ) is None

    responses = iter([
        [],
        [
            {"number": 1, "state": "open", "body": body},
            {"number": 1, "state": "open", "body": body},
            {
                "number": 2,
                "state": "closed",
                "body": body,
            },
            {
                "number": 3,
                "state": "open",
                "body": body,
                "pull_request": {"url": "https://example.invalid/pr/1"},
            },
            {
                "number": 4,
                "state": "open",
                "body": "<!-- aibast-workshop-feedback:v1 -->\n"
                "- Schema: `wrong`\n"
                "- Solution: `@aibast-agents-library/account-intelligence`",
            },
            {
                "number": 5,
                "state": "open",
                "body": "- Schema: `aibast-workshop-feedback/1.0`\n"
                "- Solution: `@aibast-agents-library/account-intelligence`",
            },
            {
                "number": 6,
                "state": "open",
                "body": "<!-- aibast-workshop-feedback:v1 -->\n"
                "- Schema: `aibast-workshop-feedback/1.0`\n"
                "- Solution: `@aibast-agents-library/not-canonical`",
            },
        ],
        [],
    ])
    monkeypatch.setattr(
        build_metrics,
        "fetch_public",
        lambda _url, _token=None: next(responses),
    )

    result = build_metrics.fetch_workshop_feedback(
        None, {"account-intelligence", "deal-progression"}
    )

    assert result["status"] == "available"
    assert result["mode"] == "workshop-feedback label + body marker union"
    assert result["issues_scanned"] == 5
    assert result["counts"]["account-intelligence"] == {
        "feedback_reports": 2,
        "feedback_open": 1,
        "feedback_closed": 1,
    }
    assert result["counts"]["deal-progression"] == {
        "feedback_reports": 0,
        "feedback_open": 0,
        "feedback_closed": 0,
    }
    assert result["diagnostics"] == {
        "duplicate_issues": 0,
        "invalid_issues": 2,
        "pull_requests": 1,
    }
    assert "issues" not in result
    assert all("body" not in value for value in result["counts"].values())


def test_workshop_feedback_unions_labelled_and_unlabelled_marker_issues(
    monkeypatch,
):
    body = """<!-- aibast-workshop-feedback:v1 -->
- Schema: `aibast-workshop-feedback/1.0`
- Solution: `@aibast-agents-library/account-intelligence`
"""
    responses = iter([
        [{"id": 10, "number": 10, "state": "open", "body": body}],
        [
            {"id": 10, "number": 10, "state": "open", "body": body},
            {"id": 11, "number": 11, "state": "closed", "body": body},
        ],
    ])
    monkeypatch.setattr(
        build_metrics,
        "fetch_issue_pages",
        lambda _token, label=None: {
            "issues": next(responses),
            "available": True,
            "complete": True,
            "pages": 1,
        },
    )

    result = build_metrics.fetch_workshop_feedback(
        None,
        {"account-intelligence"},
    )

    assert result["issues_scanned"] == 2
    assert result["counts"]["account-intelligence"] == {
        "feedback_reports": 2,
        "feedback_open": 1,
        "feedback_closed": 1,
    }


def test_request_json_sends_the_provided_bearer_token(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return b"{}"

    def fake_urlopen(request, timeout):
        assert timeout == build_metrics.TIMEOUT
        assert request.get_header("Authorization") == "Bearer sentinel-token"
        return Response()

    monkeypatch.setattr(build_metrics.urllib.request, "urlopen", fake_urlopen)

    data, error = build_metrics.request_json(
        "https://example.invalid/metrics",
        "sentinel-token",
    )

    assert data == {}
    assert error is None


def test_issue_pagination_fetches_state_all_pages(monkeypatch):
    calls = []
    pages = iter([
        [{"number": 1}, {"number": 2}],
        [{"number": 3}],
    ])
    monkeypatch.setattr(
        build_metrics,
        "fetch_public",
        lambda url, token=None: calls.append(url) or next(pages),
    )

    result = build_metrics.fetch_issue_pages(None, page_size=2)

    assert result["complete"] is True
    assert [issue["number"] for issue in result["issues"]] == [1, 2, 3]
    assert all("state=all" in url for url in calls)
    assert "page=1" in calls[0] and "page=2" in calls[1]


def test_agent_discussions_validate_schema_and_keep_signals_separate():
    agents = {
        "@aibast-agents-library/account-intelligence",
        "@aibast-agents-library/deal-progression",
    }

    def body(agent, signal="upvote", schema=build_metrics.AGENT_DISCUSSION_SCHEMA):
        return (
            "<!-- aibast-agent-discussion:v1 -->\n"
            f"- Schema: `{schema}`\n"
            f"- Signal: `{signal}`\n"
            f"- Agent: `{agent}`\n"
            f"- File: `agents/{agent.rsplit('/', 1)[-1]}.py`\n"
        )

    valid_body = body("@aibast-agents-library/account-intelligence")
    assert build_metrics.parse_agent_discussion(valid_body) == {
        "signal": "upvote",
        "agent": "@aibast-agents-library/account-intelligence",
        "file": "agents/account-intelligence.py",
    }
    assert build_metrics.parse_agent_discussion(
        "<!-- aibast-agent-discussion:v1 -->\n"
        "- Schema: aibast-agent-discussion/1.0\n"
        "- Signal: acquisition\n"
        "- Agent: @aibast-agents-library/account-intelligence\n",
    ) is None
    assert build_metrics.parse_agent_discussion("\n" + valid_body) is None
    assert build_metrics.parse_agent_discussion(
        valid_body + "- Signal: `acquisition`\n",
    ) is None

    discussions = [
        {
            "number": 1,
            "body": body("@aibast-agents-library/account-intelligence"),
            "upvoteCount": 3,
            "url": "https://github.com/microsoft/aibast-agents-library/discussions/1",
        },
        {
            "number": 2,
            "body": body(
                "@aibast-agents-library/account-intelligence",
                signal="acquisition",
            ),
            "upvoteCount": 2,
            "url": "https://github.com/microsoft/aibast-agents-library/discussions/2",
        },
        {
            "number": 3,
            "body": body("@aibast-agents-library/account-intelligence"),
            "upvoteCount": 50,
            "url": "https://github.com/microsoft/aibast-agents-library/discussions/3",
        },
        {
            "number": 4,
            "body": body("@aibast-agents-library/deal-progression"),
            "upvoteCount": 1,
            "url": "https://github.com/microsoft/aibast-agents-library/discussions/4",
        },
        {
            "number": 5,
            "body": body("@aibast-agents-library/not-registered"),
            "upvoteCount": 8,
            "url": "https://github.com/microsoft/aibast-agents-library/discussions/5",
        },
        {
            "number": 6,
            "body": body(
                "@aibast-agents-library/account-intelligence",
                schema="wrong",
            ),
            "upvoteCount": 4,
            "url": "https://github.com/microsoft/aibast-agents-library/discussions/6",
        },
        {
            "number": 7,
            "body": body(
                "@aibast-agents-library/deal-progression",
                signal="acquisition",
            ),
            "upvoteCount": 9,
            "url": "https://github.com/attacker/repo/discussions/7",
        },
    ]

    grouped = build_metrics.group_agent_discussions(
        discussions, agents, complete=True
    )

    assert grouped["status"] == "partial"
    assert grouped["signals"]["upvote"]["counts"] == {
        "@aibast-agents-library/account-intelligence": 3,
        "@aibast-agents-library/deal-progression": 1,
    }
    assert grouped["signals"]["acquisition"]["counts"] == {
        "@aibast-agents-library/account-intelligence": 2,
        "@aibast-agents-library/deal-progression": None,
    }
    assert grouped["signals"]["upvote"]["total"] == 4
    assert grouped["signals"]["acquisition"]["total"] is None
    assert grouped["diagnostics"] == {
        "duplicate_discussions": 1,
        "invalid_discussions": 2,
        "stale_agent_discussions": 1,
        "upvote_discussions": 2,
        "acquisition_discussions": 1,
    }
    assert "discussions" not in grouped
    assert "body" not in json.dumps(grouped)


def test_agent_discussion_fetch_complete_zero_and_partial_null(monkeypatch):
    names = {
        "@aibast-agents-library/account-intelligence",
        "@aibast-agents-library/deal-progression",
    }
    discussions = []
    number = 0
    for agent in sorted(names):
        for signal in build_metrics.AGENT_DISCUSSION_SIGNALS:
            number += 1
            discussions.append(
                {
                    "number": number,
                    "body": (
                        "<!-- aibast-agent-discussion:v1 -->\n"
                        "- Schema: `aibast-agent-discussion/1.0`\n"
                        f"- Signal: `{signal}`\n"
                        f"- Agent: `{agent}`\n"
                        f"- File: `agents/{number}.py`\n"
                    ),
                    "upvoteCount": 0,
                    "url": (
                        "https://github.com/microsoft/"
                        "aibast-agents-library/discussions/"
                        f"{number}"
                    ),
                }
            )
    monkeypatch.setattr(
        build_metrics,
        "fetch_discussion_pages",
        lambda _token: {
            "discussions": discussions,
            "available": True,
            "complete": True,
            "pages": 1,
            "error": None,
        },
    )
    complete = build_metrics.fetch_agent_discussion_signals("token", names)
    assert complete["status"] == "available"
    assert complete["signals"]["upvote"]["total"] == 0
    assert complete["signals"]["acquisition"]["total"] == 0
    assert set(
        complete["signals"]["upvote"]["counts"].values()
    ) == {0}

    monkeypatch.setattr(
        build_metrics,
        "fetch_discussion_pages",
        lambda _token: {
            "discussions": [],
            "available": True,
            "complete": False,
            "pages": 1,
            "error": "truncated",
        },
    )
    partial = build_metrics.fetch_agent_discussion_signals("token", names)
    assert partial["status"] == "partial"
    assert partial["signals"]["upvote"]["total"] is None
    assert set(
        partial["signals"]["upvote"]["counts"].values()
    ) == {None}


def test_agent_metrics_array_total_and_most_upvoted_leaderboard():
    registry = load_registry()
    agents, _by_file = build_metrics.build_agent_index(registry)
    for agent in agents.values():
        agent["upvotes"] = 0
        agent["acquisitions"] = 0
    agents["@aibast-agents-library/account-intelligence"].update(
        upvotes=2, downloads=5
    )
    agents["@aibast-agents-library/deal-progression"].update(
        upvotes=2, downloads=7
    )
    agents["@aibast-agents-library/proposal-generation"].update(
        upvotes=3, acquisitions=4, downloads=1
    )
    agents["@aibast-agents-library/deal-progression"]["acquisitions"] = 2

    metrics = build_metrics.build_agent_metrics(agents)
    leaderboards = build_metrics.build_leaderboards(agents, registry)
    leaderboard = leaderboards["most_upvoted"]

    assert isinstance(metrics, list)
    assert len(metrics) == len(registry["agents"])
    assert all(
        {
            "name",
            "downloads",
            "upvotes",
            "acquisitions",
            "catalog_kind",
        }
        <= set(row)
        for row in metrics
    )
    assert sum(row["upvotes"] for row in metrics) == 7
    assert [row["name"] for row in leaderboard[:3]] == [
        "@aibast-agents-library/proposal-generation",
        "@aibast-agents-library/deal-progression",
        "@aibast-agents-library/account-intelligence",
    ]
    assert [
        row["name"] for row in leaderboards["most_acquired"][:2]
    ] == [
        "@aibast-agents-library/proposal-generation",
        "@aibast-agents-library/deal-progression",
    ]
    excluded = "@aibast-agents-library/grid-outage-response"
    for board in (
        "most_downloaded",
        "most_upvoted",
        "most_acquired",
        "largest",
        "newest",
    ):
        assert excluded not in {
            row["name"] for row in leaderboards[board]
        }
    assert "grid_outage_response" not in {
        row["name"] for row in leaderboards["stacks"]
    }
    advertised = {
        row["catalog_key"]
        for row in build_metrics.build_workshop_catalog(registry)
    }
    expected_energy = sum(
        row["category"] == "energy"
        and (
            row.get("catalog_kind") != "solution"
            or row["name"] in advertised
        )
        for row in agents.values()
    )
    energy = next(
        row for row in leaderboards["categories"] if row["name"] == "energy"
    )
    assert energy["agents"] == expected_energy


def test_workshop_totals_reconcile_and_rows_sort_by_usage():
    catalog = [
        {
            "catalog_key": "@aibast-agents-library/account-intelligence",
            "slug": "account-intelligence",
            "display_name": "Account Intelligence Agent",
            "quest_url": "solutions/account-intelligence/quest.html",
            "path_rules": [
                {"kind": "prefix", "path": "solutions/account-intelligence/"}
            ],
        },
        {
            "catalog_key": "@aibast-agents-library/deal-progression",
            "slug": "deal-progression",
            "display_name": "Deal Progression Agent",
            "quest_url": "solutions/deal-progression/quest.html",
            "path_rules": [
                {"kind": "prefix", "path": "solutions/deal-progression/"}
            ],
        },
    ]
    metrics = build_metrics.build_workshop_metrics(
        catalog,
        path_rows=[
            {
                "path": "/solutions/account-intelligence/quest.html",
                "count": 5,
                "uniques": 3,
            },
            {
                "path": "/solutions/deal-progression/quest.html",
                "count": 1,
                "uniques": 1,
            },
        ],
        download_counts={
            "account-intelligence": {"file_downloads": 2, "bundle_downloads": 1},
            "deal-progression": {"file_downloads": 10, "bundle_downloads": 0},
        },
        feedback_counts={
            "account-intelligence": {
                "feedback_reports": 1,
                "feedback_open": 1,
                "feedback_closed": 0,
            },
            "deal-progression": {
                "feedback_reports": 2,
                "feedback_open": 0,
                "feedback_closed": 2,
            },
        },
        agent_upvotes={
            "@aibast-agents-library/account-intelligence": 7,
            "@aibast-agents-library/deal-progression": 5,
        },
    )

    assert [row["slug"] for row in metrics["rows"]] == [
        "deal-progression",
        "account-intelligence",
    ]
    totals = metrics["totals"]
    assert totals == {
        "workshops": 2,
        "usage_events": 22,
        "views_14d": 6,
        "view_uniques_14d": 4,
        "file_downloads": 12,
        "bundle_downloads": 1,
        "feedback_reports": 3,
        "feedback_open": 1,
        "feedback_closed": 2,
        "agent_upvotes": 12,
    }
    assert metrics["source_totals"] == {
        "views_14d": 6,
        "file_downloads": 12,
        "bundle_downloads": 1,
        "feedback_reports": 3,
    }
    assert totals["usage_events"] == sum(
        totals[field]
        for field in (
            "views_14d",
            "file_downloads",
            "bundle_downloads",
            "feedback_reports",
        )
    )
    assert all(
        row["usage_events"] == (
            row["views_14d"]
            + row["file_downloads"]
            + row["bundle_downloads"]
            + row["feedback_reports"]
        )
        for row in metrics["rows"]
    )
    assert {
        row["agent_name"]: row["agent_upvotes"]
        for row in metrics["rows"]
    } == {
        "@aibast-agents-library/account-intelligence": 7,
        "@aibast-agents-library/deal-progression": 5,
    }
    assert metrics["totals"]["usage_events"] == 22


def test_metrics_page_binds_workshop_adoption_schema():
    html = METRICS_PAGE.read_text(encoding="utf-8")

    for element_id in (
        "achievements-points",
        "achievements-heading",
        "achievements-summary",
        "achievements-coverage",
        "achievements-profile-hint",
        "achievements-leaderboard",
        "achievements-workshop-hint",
        "achievements-workshop-table",
        "achievements-rollup-heading",
        "achievements-rollup-hint",
        "achievements-rollup-table",
    ):
        assert f'id="{element_id}"' in html
    assert "function renderAchievementPoints(" in html
    assert "renderAchievementPoints();" in html
    for field in (
        "M.achievements || {}",
        "achievementMetrics.totals || {}",
        "achievementMetrics.profiles",
        "achievementMetrics.workshops",
        "achievementMetrics.achievements",
        "totals.participants",
        "totals.points",
        "totals.achievements",
        "totals.starts",
        "totals.workshop_completions",
        "totals.hard_completions",
        "totals.completion_rate",
        "totals.achievement_completion_rate",
        "profile.login",
        "profile.points",
        "profile.achievement_count",
        "profile.starts",
        "profile.workshop_completions",
        "profile.hard_completions",
        "profile.achievement_ids",
        "row.starts",
        "row.achievements",
        "row.workshop_completions",
        "row.hard_completions",
        "row.achievement_completion_rate",
        "row.points",
        "row.attainment_rate",
    ):
        assert field in html
    for phrase in (
        "Verified workshop achievements",
        "Verified participants",
        "Verified badges",
        "Verified starts",
        "Workshop completions",
        "Manual completions",
        "Completion rate",
        "Public achievement leaderboard",
        "Workshop achievement completion",
        "Achievement rollup",
        "Local self-paced achievements are different",
        "explicitly opted into public display",
        "never repository stars, agent upvotes, downloads, or workshop usage events",
        "at most 150 points per workshop",
        "never duplicates points",
        "Missing prerequisite badges are not inferred",
        "Verification scope.",
        "GitHub verification confirms authenticated issue authorship and canonical claim format only",
        "achievement completion remains self-reported and is not independently proven",
    ):
        assert phrase in html
    assert "aibast-achievements-achievement" not in html
    assert html.count('href="achievements.html"') >= 2
    assert (
        'aria-label="Verified public achievement profile leaderboard"'
        in html
    )
    assert (
        'aria-label="Verified per-workshop achievement completion"'
        in html
    )

    for element_id in (
        "workshop-summary",
        "workshop-hint",
        "workshop-coverage",
        "workshop-tabs",
        "workshop-table",
    ):
        assert f'id="{element_id}"' in html
    for function in ("renderWorkshops", "renderWorkshopControls"):
        assert f"function {function}(" in html
    for field in (
        "M.workshops",
        "workshopTotals.usage_events",
        "row.usage_events",
        "row.views_14d",
        "row.view_uniques_14d",
        "row.file_downloads",
        "row.bundle_downloads",
        "row.feedback_reports",
        "row.feedback_open",
        "row.feedback_closed",
        "row.agent_name",
        "row.agent_upvotes",
        "row.quest_url",
    ):
        assert field in html
    for label in (
        "Usage",
        "Agent upvotes",
        "Views",
        "File downloads",
        "Bundle downloads",
        "Feedback",
    ):
        assert f"label: '{label}'" in html
    assert html.count('href="docs/metrics-admin-setup.html"') >= 2
    assert "Admin setup checklist" in html
    assert "METRICS_TOKEN" in html
    assert "Administration: read" in html
    assert "organization SSO" in html
    assert "appendAdminSetupNotice(workshopCoverage)" in html
    assert "appendAdminSetupNotice(callout)" in html
    assert "M.workshops || {}" in html
    assert "Array.isArray(workshops.rows)" in html
    assert "censored, not a verified zero" in html
    assert "mixed measurement windows" in html
    live_top_up = html.split("async function liveTopUp()", 1)[1].split(
        "function render()", 1
    )[0]
    assert "M.workshops" not in live_top_up
    assert "M.repo.upvotes" not in html
    assert "r.upvotes" not in html
    assert "Community upvotes" not in html
    assert "Upvote on GitHub" not in html
    assert "Repository stars" in html
    assert "AIBAST distribution, engagement, and learning impact" in html
    assert "label: 'Most upvoted'" in html
    assert "label: 'Most acquired'" in html
    assert "t.agent_upvotes" in html
    assert "t.agent_acquisitions" in html
    assert "Array.isArray(M.agent_metrics) ? M.agent_metrics : []" in html
    assert "const advertisedWorkshopAgents = new Set(" in html
    assert "row.catalog_kind !== 'solution'" in html
    assert "GitHub permits one active upvote per account" in html
    assert "RAR is intentionally excluded from these counts" in html
    assert 'id="global-agent-ecosystem"' not in html
    assert "function renderEcosystem(" not in html
    assert "renderEcosystem();" not in html
    for element_id in (
        "file-ledger-search",
        "file-ledger-kind",
        "file-ledger-sort",
        "file-ledger-summary",
        "file-ledger-table",
        "file-ledger-prev",
        "file-ledger-next",
        "file-ledger-page",
    ):
        assert f'id="{element_id}"' in html
    for function in ("renderFileLedger", "renderFileLedgerControls", "fileKindLabel"):
        assert f"function {function}(" in html
    assert "M.file_metrics || {}" in html
    assert "Array.isArray(metrics.rows)" in html
    assert "FILE_LEDGER_PAGE_SIZE = 50" in html
    assert "t.skill_downloads" in html
    assert "Skill downloads" in html
    assert "Skill (SKILL.md)" in html
    assert "const DEFAULT_OWNER = 'microsoft'" in html
    assert "DEFAULT_REPO = 'aibast-agents-library'" in html
    assert "function setSnapshotRepository(" in html
    assert "setSnapshotRepository(M.repo)" in html
    assert "(repo || {}).owner" in html
    assert "(repo || {}).name" in html
    achievement_renderer = html.split("function renderAchievementPoints()", 1)[1].split(
        "const WORKSHOP_SORTS", 1
    )[0]
    for forbidden in (
        "M.totals.downloads +=",
        "row.usage_events +",
        "row.agent_upvotes +",
        "M.repo.stars +",
    ):
        assert forbidden not in achievement_renderer
