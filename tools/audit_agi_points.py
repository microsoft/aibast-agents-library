#!/usr/bin/env python3
"""Fail-closed acceptance gate for local and globally synced AGI Points."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import build_metrics  # noqa: E402
from tools import scaffold_solution_journey  # noqa: E402


SCHEMA = "aibast-agi-points-audit/1.0"
LOCAL_TO_CLAIM = {
    "started": "started",
    "local-proof": "local-proof",
    "draft-builder": "draft-builder",
    "preview-proven": "preview-proven",
    "workshop-complete": "workshop-completed",
    "hard-mode-complete": "hard-mode-completed",
}
PROFILE_KEYS = {
    "login",
    "points",
    "achievement_count",
    "starts",
    "workshop_completions",
    "hard_completions",
    "badges",
    "achievement_ids",
    "completed_workshops",
}


class Failures:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        if message not in self.items:
            self.items.append(message)


def read_text(path: Path, failures: Failures) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.add(f"{path}: unreadable ({exc})")
        return ""


def read_json(path: Path, failures: Failures) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.add(f"{path}: unreadable JSON ({exc})")
        return {}


def workshop_catalog(root: Path, failures: Failures) -> list[dict[str, Any]]:
    registry = read_json(root / "registry.json", failures)
    if not isinstance(registry, dict):
        return []
    try:
        catalog = build_metrics.build_workshop_catalog(registry)
    except Exception as exc:
        failures.add(f"registry workshop scope cannot be resolved ({exc})")
        return []
    slugs = {row.get("slug") for row in catalog}
    if len(catalog) != 51:
        failures.add(f"expected 51 canonical workshops, found {len(catalog)}")
    if "grid-outage-response" in slugs:
        failures.add("Grid Outage must remain outside the canonical workshop scope")
    return catalog


def audit_point_contract(failures: Failures) -> None:
    local_points = scaffold_solution_journey.AGI_POINTS
    server_points = build_metrics.AGI_POINTS
    if tuple(LOCAL_TO_CLAIM.values()) != build_metrics.AGI_ACHIEVEMENT_ORDER:
        failures.add("local-to-claim achievement order does not match the server")
    for local_id, claim_id in LOCAL_TO_CLAIM.items():
        if local_points.get(local_id) != server_points.get(claim_id):
            failures.add(
                f"point mismatch for {local_id}/{claim_id}: "
                f"{local_points.get(local_id)} != {server_points.get(claim_id)}"
            )
    if sum(server_points.values()) != 150:
        failures.add("canonical AGI Points must total 150 per workshop")


def audit_generated_workshops(
    root: Path,
    catalog: list[dict[str, Any]],
    failures: Failures,
) -> None:
    required_quest = (
        scaffold_solution_journey.AGI_PROFILE_KEY,
        "Agent Growth &amp; Impact (AGI) Points",
        "Sync AGI Points to GitHub",
        "<!-- aibast-agi-progress:v1 -->",
        "aibast-agi-progress/1.0",
        "aibastSignalIssueUrl()",
        "globalThis.location?.hostname",
        "earnedAgiSyncIds(achievements)",
        "Opening this form does not sync anything",
        "manual-progress",
        "updateHardProgress",
        "hardProgressToast.textContent = complete",
    )
    required_manual = (
        scaffold_solution_journey.AGI_PROFILE_KEY,
        "manual-progress",
        'badgeIds.push("hard-mode-complete")',
        "hardComplete: complete",
        "aibastSignalIssueUrl()",
    )
    forbidden_network = ("fetch(", "XMLHttpRequest", "sendBeacon", ".submit(")
    for row in catalog:
        slug = row["slug"]
        agent = row["catalog_key"]
        package = root / "solutions" / slug
        quest = read_text(package / "quest.html", failures)
        manual = read_text(package / "manual-tutorial.html", failures)
        label = f"solutions/{slug}"
        for token in required_quest:
            if token not in quest:
                failures.add(f"{label}/quest.html: missing {token}")
        for token in required_manual:
            if token not in manual:
                failures.add(f"{label}/manual-tutorial.html: missing {token}")
        for token in ("postMessage", "ResizeObserver", "data-embedded"):
            if token in quest or token in manual:
                failures.add(f"{label}: obsolete iframe protocol remains ({token})")
        if f'const AGI_WORKSHOP_SLUG = "{slug}";' not in quest:
            failures.add(f"{label}/quest.html: wrong AGI workshop slug")
        if f"const AGI_CANONICAL_AGENT = {json.dumps(agent)};" not in quest:
            failures.add(f"{label}/quest.html: wrong canonical AGI agent")
        for claim_id in build_metrics.AGI_ACHIEVEMENT_ORDER:
            if f'claimId: "{claim_id}"' not in quest:
                failures.add(
                    f"{label}/quest.html: missing canonical claim ID {claim_id}"
                )
        if "aibast-agi-achievement" in quest or "aibast-agi-achievement" in manual:
            failures.add(f"{label}: obsolete AGI achievement schema remains")
        for token in forbidden_network:
            if token in quest or token in manual:
                failures.add(f"{label}: automatic network/write primitive found ({token})")


def audit_public_pages(root: Path, failures: Failures) -> None:
    achievements = read_text(root / "achievements.html", failures)
    metrics = read_text(root / "metrics.html", failures)
    library = read_text(root / "library.html", failures)
    admin = read_text(root / "docs" / "metrics-admin-setup.html", failures)
    workflow = read_text(
        root / ".github" / "workflows" / "workshop-feedback.yml",
        failures,
    )
    metrics_workflow = read_text(
        root / ".github" / "workflows" / "metrics.yml",
        failures,
    )

    for token in (
        "Local unsynced",
        "Verified synced",
        'fetch("state/metrics.json", {',
        'cache: "no-store"',
        "row.badges",
        "does not authenticate the account",
        "No local progress is sent automatically",
    ):
        if token not in achievements:
            failures.add(f"achievements.html: missing {token}")
    if achievements.count("fetch(") != 1:
        failures.add("achievements.html must make exactly one read-only fetch")
    for token in ("XMLHttpRequest", "sendBeacon", "aibast-agi-achievement"):
        if token in achievements:
            failures.add(f"achievements.html: forbidden token {token}")

    for token in (
        'id="agi-points"',
        'id="agi-leaderboard"',
        'id="agi-workshop-table"',
        'id="agi-rollup-table"',
        "M.agi || {}",
        "self-reported",
        "not independently",
    ):
        if token not in metrics:
            failures.add(f"metrics.html: missing {token}")

    if '<a href="achievements.html">AGI Points</a>' not in library:
        failures.add("library.html: AGI Points navigation is missing")
    if "globalThis.location?.hostname" not in library:
        failures.add("library.html: structured signals are not fork-aware")

    metrics_workflow_tokens = {
        "issues: read",
        "contents: write",
        "METRICS_OWNER:",
        "github.repository_owner",
        "METRICS_REPO:",
        "github.event.repository.name",
    }
    for token in (
        "actions: write",
        "issues: write",
        "issues: read",
        "contents: write",
        "METRICS_OWNER:",
        "github.repository_owner",
        "METRICS_REPO:",
        "github.event.repository.name",
        "repository.default_branch",
        "createWorkflowDispatch",
        "types: [opened, edited, closed, reopened]",
    ):
        source = metrics_workflow if token in metrics_workflow_tokens else workflow
        if token not in source:
            failures.add(f"workflow contract: missing {token}")
    for token in (
        "issues: write",
        "actions: write",
        "default branch",
        "marker",
        "self-reported",
    ):
        if token.lower() not in admin.lower():
            failures.add(f"metrics admin checklist: missing {token}")


def audit_parser(
    catalog: list[dict[str, Any]],
    failures: Failures,
) -> None:
    if not catalog:
        return
    workshop = catalog[0]
    achievement_list = ", ".join(build_metrics.AGI_ACHIEVEMENT_ORDER)
    body = (
        f"{build_metrics.AGI_PROGRESS_MARKER}\n"
        "## Agent Growth & Impact progress\n\n"
        f"- Schema: `{build_metrics.AGI_PROGRESS_SCHEMA}`\n"
        f"- Workshop: `{workshop['slug']}`\n"
        f"- Agent: `{workshop['catalog_key']}`\n"
        f"- Achievements: {achievement_list}\n"
        "- Source: https://example.test/quest.html\n"
    )
    claim = build_metrics.parse_agi_claim(body, catalog)
    if not claim or claim.get("achievements") != list(
        build_metrics.AGI_ACHIEVEMENT_ORDER
    ):
        failures.add("strict AGI parser rejected the canonical claim")
        return
    if build_metrics.parse_agi_claim(body + "- Points: 999999\n", catalog):
        failures.add("strict AGI parser accepted body-supplied points")
    grouped = build_metrics.group_agi_progress(
        [{"user": {"login": "AuditUser"}, "body": body}],
        catalog,
    )
    if (
        grouped["totals"]["points"] != 150
        or grouped["totals"]["participants"] != 1
        or grouped["profiles"][0]["points"] != 150
    ):
        failures.add("canonical AGI score does not reconcile to 150")


def audit_snapshot(
    root: Path,
    catalog: list[dict[str, Any]],
    failures: Failures,
) -> None:
    snapshot = read_json(root / "state" / "metrics.json", failures)
    agi = snapshot.get("agi") if isinstance(snapshot, dict) else None
    if not isinstance(agi, dict) or agi.get("schema") != "aibast-agi/2.0":
        failures.add("state/metrics.json: AGI schema is missing or stale")
        return
    expected_slugs = {row["slug"] for row in catalog}
    rows = agi.get("workshops", [])
    if {row.get("slug") for row in rows} != expected_slugs:
        failures.add("state/metrics.json: AGI workshop scope does not match 51")
    profiles = agi.get("profiles", [])
    if any(set(profile) != PROFILE_KEYS for profile in profiles):
        failures.add("state/metrics.json: public AGI profile fields are unsafe")
    serialized = json.dumps(agi)
    for token in ('"body"', '"source"', '"issue_id"', '"email"', '"token"'):
        if token in serialized:
            failures.add(f"state/metrics.json: private/source field persisted ({token})")
    if agi.get("status") == "unavailable":
        if profiles or any(value is not None for value in agi.get("totals", {}).values()):
            failures.add("state/metrics.json: unavailable AGI data fabricates zeros")
        return
    totals = agi.get("totals", {})
    expected = {
        "participants": len(profiles),
        "points": sum(profile["points"] for profile in profiles),
        "achievements": sum(profile["achievement_count"] for profile in profiles),
        "starts": sum(profile["starts"] for profile in profiles),
        "workshop_completions": sum(
            profile["workshop_completions"] for profile in profiles
        ),
        "hard_completions": sum(
            profile["hard_completions"] for profile in profiles
        ),
    }
    if any(totals.get(key) != value for key, value in expected.items()):
        failures.add("state/metrics.json: AGI totals do not reconcile to profiles")
    for profile in profiles:
        badges = profile.get("badges", [])
        if profile.get("points") != sum(badge.get("points", 0) for badge in badges):
            failures.add(
                f"state/metrics.json: AGI profile score mismatch for {profile.get('login')}"
            )


def audit(root: Path = ROOT) -> dict[str, Any]:
    failures = Failures()
    catalog = workshop_catalog(root, failures)
    audit_point_contract(failures)
    audit_generated_workshops(root, catalog, failures)
    audit_public_pages(root, failures)
    audit_parser(catalog, failures)
    audit_snapshot(root, catalog, failures)
    return {
        "schema": SCHEMA,
        "status": "pass" if not failures.items else "fail",
        "workshops": len(catalog),
        "failures": failures.items,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = audit(args.root.resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["status"] == "pass":
        print(f"[PASS] AGI Points contract: {result['workshops']} workshops")
    else:
        print("[FAIL] AGI Points contract", file=sys.stderr)
        for failure in result["failures"]:
            print(f"- {failure}", file=sys.stderr)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
