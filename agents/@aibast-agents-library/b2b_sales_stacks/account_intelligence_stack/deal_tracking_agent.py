"""
Deal Tracking Agent

Tracks pipeline snapshots, deal stage movement, stage velocity metrics,
and forecast accuracy for enterprise B2B sales. Provides real-time
visibility into deal health and progression patterns.

Where a real deployment would call CRM and forecasting APIs, this agent
uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/deal-tracking",
    "version": "1.0.0",
    "display_name": "Deal Tracking",
    "description": "Tracks pipeline, deal movement, stage velocity, and forecast accuracy for enterprise sales.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "deal-tracking", "pipeline", "forecasting"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_DEALS = {
    "deal-001": {
        "name": "Acme Corporation - Platform Expansion",
        "account": "Acme Corporation", "owner": "Michael Torres",
        "amount": 2_400_000, "stage": "Proposal",
        "win_probability": 68, "close_date": "2025-04-05",
        "created": "2024-11-15", "days_open": 120,
        "stage_history": [
            {"stage": "Qualification", "entered": "2024-11-15", "exited": "2024-12-10", "days": 25},
            {"stage": "Discovery", "entered": "2024-12-10", "exited": "2025-01-15", "days": 36},
            {"stage": "Solution Design", "entered": "2025-01-15", "exited": "2025-02-08", "days": 24},
            {"stage": "Proposal", "entered": "2025-02-08", "exited": None, "days": 34},
        ],
        "next_steps": "Executive meeting scheduled, pending CTO intro",
        "risk_flags": ["Competitor pricing pressure", "No CTO relationship"],
    },
    "deal-002": {
        "name": "Contoso Ltd - Renewal + Expansion",
        "account": "Contoso Ltd", "owner": "Michael Torres",
        "amount": 1_100_000, "stage": "Negotiation",
        "win_probability": 82, "close_date": "2025-03-31",
        "created": "2024-10-01", "days_open": 165,
        "stage_history": [
            {"stage": "Qualification", "entered": "2024-10-01", "exited": "2024-10-20", "days": 19},
            {"stage": "Discovery", "entered": "2024-10-20", "exited": "2024-11-28", "days": 39},
            {"stage": "Solution Design", "entered": "2024-11-28", "exited": "2025-01-10", "days": 43},
            {"stage": "Proposal", "entered": "2025-01-10", "exited": "2025-03-02", "days": 51},
            {"stage": "Negotiation", "entered": "2025-03-02", "exited": None, "days": 12},
        ],
        "next_steps": "Legal review of contract terms, pricing finalization",
        "risk_flags": ["CFO budget cautious"],
    },
    "deal-003": {
        "name": "Fabrikam Industries - Analytics Suite",
        "account": "Fabrikam Industries", "owner": "Michael Torres",
        "amount": 890_000, "stage": "Discovery",
        "win_probability": 45, "close_date": "2025-06-30",
        "created": "2025-01-20", "days_open": 53,
        "stage_history": [
            {"stage": "Qualification", "entered": "2025-01-20", "exited": "2025-02-05", "days": 16},
            {"stage": "Discovery", "entered": "2025-02-05", "exited": None, "days": 37},
        ],
        "next_steps": "Workshop with VP IT, stakeholder mapping",
        "risk_flags": ["New VP IT decision maker", "Low-cost competitor"],
    },
    "deal-004": {
        "name": "Northwind Traders - E-commerce Platform",
        "account": "Northwind Traders", "owner": "Michael Torres",
        "amount": 540_000, "stage": "Qualification",
        "win_probability": 25, "close_date": "2025-07-31",
        "created": "2025-03-05", "days_open": 9,
        "stage_history": [
            {"stage": "Qualification", "entered": "2025-03-05", "exited": None, "days": 9},
        ],
        "next_steps": "Schedule discovery call, research account",
        "risk_flags": ["No existing relationship", "Greenfield account"],
    },
    "deal-005": {
        "name": "Acme Corporation - Support Tier Upgrade",
        "account": "Acme Corporation", "owner": "Sarah Kim",
        "amount": 180_000, "stage": "Closed Won",
        "win_probability": 100, "close_date": "2025-02-28",
        "created": "2025-01-05", "days_open": 54,
        "stage_history": [
            {"stage": "Qualification", "entered": "2025-01-05", "exited": "2025-01-12", "days": 7},
            {"stage": "Proposal", "entered": "2025-01-12", "exited": "2025-02-15", "days": 34},
            {"stage": "Negotiation", "entered": "2025-02-15", "exited": "2025-02-28", "days": 13},
            {"stage": "Closed Won", "entered": "2025-02-28", "exited": None, "days": 0},
        ],
        "next_steps": "Implementation kickoff",
        "risk_flags": [],
    },
}

_STAGE_BENCHMARKS = {
    "Qualification": {"avg_days": 18, "conversion_rate": 0.72, "target_days": 14},
    "Discovery": {"avg_days": 32, "conversion_rate": 0.65, "target_days": 28},
    "Solution Design": {"avg_days": 28, "conversion_rate": 0.78, "target_days": 21},
    "Proposal": {"avg_days": 25, "conversion_rate": 0.70, "target_days": 21},
    "Negotiation": {"avg_days": 18, "conversion_rate": 0.85, "target_days": 14},
}

_FORECAST_HISTORY = {
    "2025-Q1": {
        "forecast_date": "2025-01-15", "target": 2_500_000,
        "committed": 1_800_000, "best_case": 2_900_000, "pipeline": 4_200_000,
        "actual_to_date": 2_100_000, "accuracy_committed": 0.86, "accuracy_best_case": 0.72,
    },
    "2025-Q2": {
        "forecast_date": "2025-03-10", "target": 3_000_000,
        "committed": 1_100_000, "best_case": 3_500_000, "pipeline": 5_830_000,
        "actual_to_date": 0, "accuracy_committed": None, "accuracy_best_case": None,
    },
}

_PIPELINE_SNAPSHOTS = {
    "2025-03-01": {"total": 5_110_000, "qualification": 540_000, "discovery": 890_000, "solution_design": 0, "proposal": 2_580_000, "negotiation": 1_100_000},
    "2025-03-07": {"total": 5_110_000, "qualification": 540_000, "discovery": 890_000, "solution_design": 0, "proposal": 2_580_000, "negotiation": 1_100_000},
    "2025-03-14": {"total": 4_930_000, "qualification": 540_000, "discovery": 890_000, "solution_design": 0, "proposal": 2_400_000, "negotiation": 1_100_000},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _weighted_pipeline(deals):
    """Calculate probability-weighted pipeline value."""
    return sum(d["amount"] * d["win_probability"] / 100 for d in deals if d["stage"] not in ("Closed Won", "Closed Lost"))


def _stage_velocity(deal):
    """Get current stage days vs benchmark."""
    current = deal["stage_history"][-1] if deal["stage_history"] else None
    if not current or current["stage"] not in _STAGE_BENCHMARKS:
        return None, None, None
    bench = _STAGE_BENCHMARKS[current["stage"]]
    days = current["days"]
    status = "On track" if days <= bench["target_days"] else "Slow" if days <= bench["avg_days"] * 1.5 else "Stalled"
    return days, bench["avg_days"], status


def _pipeline_change(snap1_key, snap2_key):
    """Calculate pipeline change between two snapshots."""
    s1 = _PIPELINE_SNAPSHOTS.get(snap1_key, {})
    s2 = _PIPELINE_SNAPSHOTS.get(snap2_key, {})
    if not s1 or not s2:
        return 0
    return s2.get("total", 0) - s1.get("total", 0)


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class DealTrackingAgent(BasicAgent):
    """
    Tracks deal pipeline and progression metrics.

    Operations:
        pipeline_snapshot  - current pipeline state
        deal_movement      - deal stage transitions and trends
        stage_velocity     - stage duration vs benchmarks
        forecast_accuracy  - forecast vs actual comparison
    """

    def __init__(self):
        self.name = "DealTrackingAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "pipeline_snapshot", "deal_movement",
                            "stage_velocity", "forecast_accuracy",
                        ],
                        "description": "The tracking operation to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "pipeline_snapshot")
        dispatch = {
            "pipeline_snapshot": self._pipeline_snapshot,
            "deal_movement": self._deal_movement,
            "stage_velocity": self._stage_velocity,
            "forecast_accuracy": self._forecast_accuracy,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler()

    # ── pipeline_snapshot ─────────────────────────────────────
    def _pipeline_snapshot(self):
        active_deals = [d for d in _DEALS.values() if d["stage"] not in ("Closed Won", "Closed Lost")]
        total_value = sum(d["amount"] for d in active_deals)
        weighted = _weighted_pipeline(active_deals)
        deal_count = len(active_deals)

        deal_rows = ""
        for d in sorted(active_deals, key=lambda x: x["amount"], reverse=True):
            deal_rows += (
                f"| {d['name'][:40]} | {d['stage']} | ${d['amount']:,} | "
                f"{d['win_probability']}% | {d['close_date']} | {d['owner']} |\n"
            )

        # Stage summary
        stage_totals = {}
        for d in active_deals:
            s = d["stage"]
            if s not in stage_totals:
                stage_totals[s] = {"count": 0, "value": 0}
            stage_totals[s]["count"] += 1
            stage_totals[s]["value"] += d["amount"]

        stage_rows = ""
        for stage in ["Qualification", "Discovery", "Solution Design", "Proposal", "Negotiation"]:
            data = stage_totals.get(stage, {"count": 0, "value": 0})
            if data["count"] > 0:
                stage_rows += f"| {stage} | {data['count']} | ${data['value']:,} |\n"

        change = _pipeline_change("2025-03-01", "2025-03-14")
        change_str = f"+${change:,}" if change >= 0 else f"-${abs(change):,}"

        return (
            f"**Pipeline Snapshot**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Total Pipeline | ${total_value:,} |\n"
            f"| Weighted Pipeline | ${int(weighted):,} |\n"
            f"| Active Deals | {deal_count} |\n"
            f"| 14-Day Change | {change_str} |\n\n"
            f"**Deals:**\n\n"
            f"| Deal | Stage | Amount | Probability | Close Date | Owner |\n|---|---|---|---|---|---|\n"
            f"{deal_rows}\n"
            f"**By Stage:**\n\n"
            f"| Stage | Deals | Value |\n|---|---|---|\n"
            f"{stage_rows}\n"
            f"Source: [CRM Pipeline + Deal Intelligence]\n"
            f"Agents: DealTrackingAgent"
        )

    # ── deal_movement ─────────────────────────────────────────
    def _deal_movement(self):
        output = f"**Deal Movement Analysis**\n\n"

        for deal_id, d in _DEALS.items():
            if d["stage"] in ("Closed Won", "Closed Lost"):
                continue

            history_rows = ""
            for h in d["stage_history"]:
                status = "Current" if h["exited"] is None else f"Completed ({h['days']}d)"
                bench = _STAGE_BENCHMARKS.get(h["stage"], {})
                vs_bench = ""
                if bench and h["exited"] is not None:
                    vs_bench = f" ({'on target' if h['days'] <= bench['target_days'] else 'over target'})"
                history_rows += f"| {h['stage']} | {h['entered']} | {h.get('exited', 'Current')} | {h['days']}d{vs_bench} | {status} |\n"

            risks = ", ".join(d["risk_flags"]) if d["risk_flags"] else "None"

            output += (
                f"---\n**{d['name']}** (${d['amount']:,})\n\n"
                f"| Stage | Entered | Exited | Duration | Status |\n|---|---|---|---|---|\n"
                f"{history_rows}\n"
                f"- Days open: {d['days_open']} | Win probability: {d['win_probability']}%\n"
                f"- Next steps: {d['next_steps']}\n"
                f"- Risk flags: {risks}\n\n"
            )

        output += (
            f"Source: [CRM Stage History + Deal Analytics]\n"
            f"Agents: DealTrackingAgent"
        )
        return output

    # ── stage_velocity ────────────────────────────────────────
    def _stage_velocity(self):
        bench_rows = ""
        for stage, bench in _STAGE_BENCHMARKS.items():
            bench_rows += (
                f"| {stage} | {bench['avg_days']}d | {bench['target_days']}d | "
                f"{bench['conversion_rate']:.0%} |\n"
            )

        deal_velocity_rows = ""
        for d in _DEALS.values():
            if d["stage"] in ("Closed Won", "Closed Lost"):
                continue
            days, avg, status = _stage_velocity(d)
            if days is not None:
                deal_velocity_rows += (
                    f"| {d['name'][:35]} | {d['stage']} | {days}d | "
                    f"{avg}d | {status} |\n"
                )

        # Deals at risk of stalling
        at_risk = []
        for d in _DEALS.values():
            days, avg, status = _stage_velocity(d)
            if status == "Slow" or status == "Stalled":
                at_risk.append(f"- {d['name']}: {days}d in {d['stage']} ({status})")

        at_risk_section = ""
        if at_risk:
            at_risk_section = "\n**Deals at Risk of Stalling:**\n" + "\n".join(at_risk) + "\n"

        return (
            f"**Stage Velocity Report**\n\n"
            f"**Benchmarks:**\n\n"
            f"| Stage | Avg Days | Target | Conversion |\n|---|---|---|---|\n"
            f"{bench_rows}\n"
            f"**Current Deal Velocity:**\n\n"
            f"| Deal | Stage | Days | Benchmark | Status |\n|---|---|---|---|---|\n"
            f"{deal_velocity_rows}"
            f"{at_risk_section}\n"
            f"**Recommendations:**\n"
            f"- Review deals exceeding target days in stage\n"
            f"- Schedule next-step meetings for slow-moving deals\n"
            f"- Verify buying committee engagement on stalled deals\n\n"
            f"Source: [CRM + Stage Analytics + Historical Benchmarks]\n"
            f"Agents: DealTrackingAgent"
        )

    # ── forecast_accuracy ─────────────────────────────────────
    def _forecast_accuracy(self):
        output = f"**Forecast Accuracy Report**\n\n"

        for quarter, f in _FORECAST_HISTORY.items():
            acc_committed = f"{f['accuracy_committed']:.0%}" if f["accuracy_committed"] is not None else "Pending"
            acc_best = f"{f['accuracy_best_case']:.0%}" if f["accuracy_best_case"] is not None else "Pending"

            output += (
                f"**{quarter}:**\n\n"
                f"| Metric | Value |\n|---|---|\n"
                f"| Forecast Date | {f['forecast_date']} |\n"
                f"| Target | ${f['target']:,} |\n"
                f"| Committed | ${f['committed']:,} |\n"
                f"| Best Case | ${f['best_case']:,} |\n"
                f"| Pipeline | ${f['pipeline']:,} |\n"
                f"| Actual to Date | ${f['actual_to_date']:,} |\n"
                f"| Committed Accuracy | {acc_committed} |\n"
                f"| Best Case Accuracy | {acc_best} |\n\n"
            )

        # Active deals forecast contribution
        active = [d for d in _DEALS.values() if d["stage"] not in ("Closed Won", "Closed Lost")]
        weighted = _weighted_pipeline(active)

        commit_deals = [d for d in active if d["win_probability"] >= 75]
        upside_deals = [d for d in active if 40 <= d["win_probability"] < 75]

        commit_value = sum(d["amount"] for d in commit_deals)
        upside_value = sum(d["amount"] for d in upside_deals)

        output += (
            f"**Current Quarter Forecast Build:**\n\n"
            f"| Category | Deals | Value | Weighted |\n|---|---|---|---|\n"
            f"| Commit (75%+) | {len(commit_deals)} | ${commit_value:,} | ${int(sum(d['amount'] * d['win_probability'] / 100 for d in commit_deals)):,} |\n"
            f"| Upside (40-74%) | {len(upside_deals)} | ${upside_value:,} | ${int(sum(d['amount'] * d['win_probability'] / 100 for d in upside_deals)):,} |\n"
            f"| Total Active | {len(active)} | ${sum(d['amount'] for d in active):,} | ${int(weighted):,} |\n\n"
            f"Source: [CRM Forecast + Deal History + Revenue Analytics]\n"
            f"Agents: DealTrackingAgent"
        )
        return output


if __name__ == "__main__":
    agent = DealTrackingAgent()
    for op in ["pipeline_snapshot", "deal_movement", "stage_velocity", "forecast_accuracy"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
