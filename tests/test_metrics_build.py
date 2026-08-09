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


def test_offline_mode_makes_zero_network_calls(monkeypatch, tmp_path):
    def fail_network(*_args, **_kwargs):
        raise AssertionError("offline mode attempted a network call")

    monkeypatch.setattr(build_metrics, "fetch_repo", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_releases", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_traffic", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_jsdelivr", fail_network)
    monkeypatch.setattr(build_metrics, "fetch_workshop_feedback", fail_network)
    monkeypatch.setattr(
        sys,
        "argv",
        ["build_metrics.py", "--offline", "--out", str(tmp_path / "metrics.json")],
    )

    assert build_metrics.main() == 0


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
        }:
            assert doc["totals"][field] == value
    assert doc["totals"]["agent_file_downloads"] == 2
    assert doc["totals"]["installer_downloads"] is None
    assert doc["totals"]["skill_downloads"] is None
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


def test_agent_upvotes_validate_schema_dedupe_account_agent_and_count_closed():
    agents = {
        "@aibast-agents-library/account-intelligence",
        "@aibast-agents-library/deal-progression",
    }

    def body(agent, schema=build_metrics.AGENT_UPVOTE_SCHEMA):
        return (
            "<!-- aibast-agent-upvote:v1 -->\n"
            f"- Schema: `{schema}`\n"
            f"- Agent: `{agent}`\n"
        )

    valid_body = body("@aibast-agents-library/account-intelligence")
    assert build_metrics.parse_agent_upvote(valid_body, agents) == (
        "@aibast-agents-library/account-intelligence"
    )
    assert build_metrics.parse_agent_upvote(
        "<!-- aibast-agent-upvote:v1 -->\n"
        "- Schema: aibast-agent-upvote/1.0\n"
        "- Agent: @aibast-agents-library/account-intelligence\n",
        agents,
    ) == "@aibast-agents-library/account-intelligence"
    assert build_metrics.parse_agent_upvote("\n" + valid_body, agents) is None
    assert build_metrics.parse_agent_upvote(
        valid_body + "- Agent: `@aibast-agents-library/deal-progression`\n",
        agents,
    ) is None

    issues = [
        {
            "number": 1,
            "state": "open",
            "user": {"login": "Alice"},
            "body": body("@aibast-agents-library/account-intelligence"),
        },
        {
            "number": 2,
            "state": "closed",
            "user": {"login": "alice"},
            "body": body("@aibast-agents-library/account-intelligence"),
        },
        {
            "number": 3,
            "state": "closed",
            "user": {"login": "Bob"},
            "body": body("@aibast-agents-library/account-intelligence"),
        },
        {
            "number": 4,
            "state": "closed",
            "user": {"login": "Bob"},
            "body": body("@aibast-agents-library/deal-progression"),
        },
        {
            "number": 5,
            "state": "open",
            "user": {"login": "Charlie"},
            "body": body("@aibast-agents-library/account-intelligence"),
            "pull_request": {"url": "https://example.invalid/pr/5"},
        },
        {
            "number": 6,
            "state": "open",
            "user": {"login": "Dana"},
            "body": body("@aibast-agents-library/not-registered"),
        },
        {
            "number": 7,
            "state": "open",
            "user": {"login": "Eve"},
            "body": body(
                "@aibast-agents-library/account-intelligence",
                schema="wrong",
            ),
        },
    ]

    grouped = build_metrics.group_agent_upvotes(issues, agents, complete=True)

    assert grouped["counts"] == {
        "@aibast-agents-library/account-intelligence": 2,
        "@aibast-agents-library/deal-progression": 1,
    }
    assert grouped["total"] == 3
    assert grouped["diagnostics"] == {
        "duplicate_votes": 1,
        "invalid_issues": 2,
        "pull_requests": 1,
        "open_votes": 1,
        "closed_votes": 2,
    }
    assert "issues" not in grouped
    assert "Alice" not in json.dumps(grouped)
    assert "body" not in grouped


def test_agent_upvote_fetch_complete_zero_and_partial_null(monkeypatch):
    names = {
        "@aibast-agents-library/account-intelligence",
        "@aibast-agents-library/deal-progression",
    }
    monkeypatch.setattr(
        build_metrics,
        "fetch_issue_pages",
        lambda _token: {
            "issues": [],
            "available": True,
            "complete": True,
            "pages": 1,
        },
    )
    complete = build_metrics.fetch_agent_upvotes(None, names)
    assert complete["total"] == 0
    assert set(complete["counts"].values()) == {0}

    monkeypatch.setattr(
        build_metrics,
        "fetch_issue_pages",
        lambda _token: {
            "issues": [],
            "available": True,
            "complete": False,
            "pages": 1,
        },
    )
    partial = build_metrics.fetch_agent_upvotes(None, names)
    assert partial["total"] is None
    assert set(partial["counts"].values()) == {None}


def test_agent_metrics_array_total_and_most_upvoted_leaderboard():
    registry = load_registry()
    agents, _by_file = build_metrics.build_agent_index(registry)
    for agent in agents.values():
        agent["upvotes"] = 0
    agents["@aibast-agents-library/account-intelligence"].update(
        upvotes=2, downloads=5
    )
    agents["@aibast-agents-library/deal-progression"].update(
        upvotes=2, downloads=7
    )
    agents["@aibast-agents-library/proposal-generation"].update(
        upvotes=3, downloads=1
    )

    metrics = build_metrics.build_agent_metrics(agents)
    leaderboard = build_metrics.build_leaderboards(agents, registry)["most_upvoted"]

    assert isinstance(metrics, list)
    assert len(metrics) == len(registry["agents"])
    assert all({"name", "downloads", "upvotes"} <= set(row) for row in metrics)
    assert sum(row["upvotes"] for row in metrics) == 7
    assert [row["name"] for row in leaderboard[:3]] == [
        "@aibast-agents-library/proposal-generation",
        "@aibast-agents-library/deal-progression",
        "@aibast-agents-library/account-intelligence",
    ]


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
    assert "Downloads, agent upvotes, and workshop usage" in html
    assert "label: 'Most upvoted'" in html
    assert "t.agent_upvotes" in html
    assert "Array.isArray(M.agent_metrics) ? M.agent_metrics : []" in html
    assert "Opening the form is not a vote" in html
    assert "One GitHub account counts once per agent" in html
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
