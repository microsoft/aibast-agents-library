"""Tests for the repository-wide achievement audit."""

from tools import audit_achievement_points


def test_repository_passes_fail_closed_achievement_points_audit():
    result = audit_achievement_points.audit()

    assert result["status"] == "pass", "\n".join(result["failures"])
    assert result["workshops"] == 51


def test_point_contract_catches_local_server_drift(monkeypatch):
    failures = audit_achievement_points.Failures()
    changed = dict(audit_achievement_points.scaffold_solution_journey.ACHIEVEMENT_POINTS)
    changed["started"] = 500
    monkeypatch.setattr(
        audit_achievement_points.scaffold_solution_journey,
        "ACHIEVEMENT_POINTS",
        changed,
    )

    audit_achievement_points.audit_point_contract(failures)

    assert any("point mismatch" in failure for failure in failures.items)


def test_parser_gate_rejects_body_supplied_points():
    failures = audit_achievement_points.Failures()
    catalog = audit_achievement_points.workshop_catalog(
        audit_achievement_points.ROOT,
        failures,
    )

    audit_achievement_points.audit_parser(catalog, failures)

    assert not failures.items
