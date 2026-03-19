"""
Client Health Score Agent

Monitors professional-services client portfolios using engagement metrics,
NPS scores, project margins, utilization rates, and escalation history.
Surfaces at-risk accounts and generates retention action plans.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/client-health-score",
    "version": "1.0.0",
    "display_name": "Client Health Score Agent",
    "description": "Computes client health scores from NPS, margins, utilization, and escalation data to identify at-risk accounts and drive retention strategies.",
    "author": "AIBAST",
    "tags": ["client-health", "NPS", "retention", "professional-services", "churn"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CLIENTS = {
    "CL-301": {
        "name": "TechCorp Industries",
        "annual_value": 2400000,
        "nps": -15,
        "project_margin_pct": 18.2,
        "utilization_pct": 64,
        "billing_trend": "declining",
        "escalations_90d": 4,
        "exec_meetings_90d": 0,
        "satisfaction_scores": [8.2, 7.4, 6.1, 5.1],
        "health_score": 42,
        "risk_label": "CRITICAL",
    },
    "CL-302": {
        "name": "Global Finance Corp",
        "annual_value": 1500000,
        "nps": -20,
        "project_margin_pct": 22.5,
        "utilization_pct": 45,
        "billing_trend": "flat",
        "escalations_90d": 2,
        "exec_meetings_90d": 1,
        "satisfaction_scores": [7.8, 7.2, 6.5, 6.0],
        "health_score": 58,
        "risk_label": "AT_RISK",
    },
    "CL-303": {
        "name": "Healthcare Solutions Inc",
        "annual_value": 1200000,
        "nps": 5,
        "project_margin_pct": 26.0,
        "utilization_pct": 72,
        "billing_trend": "flat",
        "escalations_90d": 3,
        "exec_meetings_90d": 1,
        "satisfaction_scores": [8.0, 7.8, 7.0, 6.8],
        "health_score": 61,
        "risk_label": "AT_RISK",
    },
    "CL-304": {
        "name": "Apex Manufacturing",
        "annual_value": 3200000,
        "nps": 45,
        "project_margin_pct": 31.4,
        "utilization_pct": 88,
        "billing_trend": "growing",
        "escalations_90d": 0,
        "exec_meetings_90d": 3,
        "satisfaction_scores": [8.5, 8.8, 9.0, 9.1],
        "health_score": 91,
        "risk_label": "HEALTHY",
    },
    "CL-305": {
        "name": "National Logistics Group",
        "annual_value": 2800000,
        "nps": 38,
        "project_margin_pct": 28.7,
        "utilization_pct": 82,
        "billing_trend": "growing",
        "escalations_90d": 1,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.9, 8.2, 8.5, 8.6],
        "health_score": 84,
        "risk_label": "HEALTHY",
    },
    "CL-306": {
        "name": "Silverline Retail",
        "annual_value": 1900000,
        "nps": 22,
        "project_margin_pct": 24.1,
        "utilization_pct": 76,
        "billing_trend": "flat",
        "escalations_90d": 1,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.5, 7.6, 7.8, 7.9],
        "health_score": 75,
        "risk_label": "HEALTHY",
    },
    "CL-307": {
        "name": "Pinnacle Energy",
        "annual_value": 3600000,
        "nps": 52,
        "project_margin_pct": 33.0,
        "utilization_pct": 91,
        "billing_trend": "growing",
        "escalations_90d": 0,
        "exec_meetings_90d": 4,
        "satisfaction_scores": [8.8, 9.0, 9.2, 9.3],
        "health_score": 94,
        "risk_label": "HEALTHY",
    },
    "CL-308": {
        "name": "Metro Transit Authority",
        "annual_value": 2100000,
        "nps": 30,
        "project_margin_pct": 27.3,
        "utilization_pct": 79,
        "billing_trend": "growing",
        "escalations_90d": 0,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.6, 7.9, 8.1, 8.3],
        "health_score": 81,
        "risk_label": "HEALTHY",
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _portfolio_value():
    """Total annual portfolio value."""
    return sum(c["annual_value"] for c in CLIENTS.values())


def _at_risk_value():
    """Sum of annual value for CRITICAL and AT_RISK clients."""
    return sum(c["annual_value"] for c in CLIENTS.values() if c["risk_label"] in ("CRITICAL", "AT_RISK"))


def _avg_health():
    """Average health score across all clients."""
    scores = [c["health_score"] for c in CLIENTS.values()]
    return round(sum(scores) / len(scores), 1)


def _satisfaction_trend(client):
    """Return trend direction based on last 4 quarterly scores."""
    scores = client["satisfaction_scores"]
    if len(scores) < 2:
        return "insufficient_data"
    if scores[-1] > scores[0] + 0.3:
        return "improving"
    elif scores[-1] < scores[0] - 0.3:
        return "declining"
    return "stable"


def _churn_probability(client):
    """Simplified churn probability from health score."""
    hs = client["health_score"]
    if hs <= 45:
        return 0.78
    elif hs <= 60:
        return 0.45
    elif hs <= 70:
        return 0.20
    elif hs <= 80:
        return 0.10
    return 0.03


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class ClientHealthScoreAgent(BasicAgent):
    """Monitors client health and identifies at-risk accounts."""

    def __init__(self):
        self.name = "ClientHealthScoreAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "health_dashboard",
                "engagement_analysis",
                "satisfaction_trend",
                "at_risk_clients",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "health_dashboard")
        dispatch = {
            "health_dashboard": self._health_dashboard,
            "engagement_analysis": self._engagement_analysis,
            "satisfaction_trend": self._satisfaction_trend,
            "at_risk_clients": self._at_risk_clients,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _health_dashboard(self, **kwargs) -> str:
        lines = ["## Client Health Dashboard\n"]
        pv = _portfolio_value()
        arv = _at_risk_value()
        lines.append(f"**Portfolio value:** ${pv:,.0f}")
        lines.append(f"**At-risk value:** ${arv:,.0f} ({round(arv/pv*100,1)}%)")
        lines.append(f"**Avg health score:** {_avg_health()}/100\n")

        lines.append("| Client | Annual Value | Health | NPS | Margin | Util % | Risk |")
        lines.append("|--------|-------------|--------|-----|--------|--------|------|")
        ranked = sorted(CLIENTS.values(), key=lambda c: c["health_score"])
        for c in ranked:
            lines.append(
                f"| {c['name']} | ${c['annual_value']:,.0f} | {c['health_score']}/100 | "
                f"{c['nps']:+d} | {c['project_margin_pct']}% | {c['utilization_pct']}% | **{c['risk_label']}** |"
            )

        critical = sum(1 for c in CLIENTS.values() if c["risk_label"] == "CRITICAL")
        at_risk = sum(1 for c in CLIENTS.values() if c["risk_label"] == "AT_RISK")
        healthy = sum(1 for c in CLIENTS.values() if c["risk_label"] == "HEALTHY")
        lines.append(f"\n**Distribution:** {critical} critical, {at_risk} at-risk, {healthy} healthy")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _engagement_analysis(self, **kwargs) -> str:
        lines = ["## Engagement Analysis\n"]
        lines.append("| Client | Exec Meetings (90d) | Escalations (90d) | Billing Trend | Utilization |")
        lines.append("|--------|--------------------:|------------------:|---------------|-------------|")
        for cid, c in CLIENTS.items():
            flag = " **LOW**" if c["exec_meetings_90d"] == 0 and c["risk_label"] != "HEALTHY" else ""
            lines.append(
                f"| {c['name']} | {c['exec_meetings_90d']}{flag} | {c['escalations_90d']} | "
                f"{c['billing_trend']} | {c['utilization_pct']}% |"
            )

        lines.append("\n### Engagement Red Flags\n")
        for cid, c in CLIENTS.items():
            flags = []
            if c["exec_meetings_90d"] == 0:
                flags.append("No executive contact in 90 days")
            if c["escalations_90d"] >= 3:
                flags.append(f"{c['escalations_90d']} escalations in 90 days")
            if c["utilization_pct"] < 60:
                flags.append(f"Low utilization ({c['utilization_pct']}%) -- may not see value")
            if c["billing_trend"] == "declining":
                flags.append("Declining billing trend")
            if flags:
                lines.append(f"**{c['name']}:**")
                for f in flags:
                    lines.append(f"- {f}")
                lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _satisfaction_trend(self, **kwargs) -> str:
        lines = ["## Client Satisfaction Trends\n"]
        lines.append("| Client | Q1 | Q2 | Q3 | Q4 | Trend | NPS |")
        lines.append("|--------|-----|-----|-----|-----|-------|-----|")
        for cid, c in CLIENTS.items():
            scores = c["satisfaction_scores"]
            trend = _satisfaction_trend(c)
            trend_icon = {"improving": "UP", "declining": "DOWN", "stable": "FLAT"}.get(trend, "-")
            cols = " | ".join(f"{s:.1f}" for s in scores)
            lines.append(f"| {c['name']} | {cols} | **{trend_icon}** | {c['nps']:+d} |")

        declining = [c for c in CLIENTS.values() if _satisfaction_trend(c) == "declining"]
        if declining:
            lines.append("\n### Declining Accounts Requiring Attention\n")
            for c in declining:
                drop = round(c["satisfaction_scores"][0] - c["satisfaction_scores"][-1], 1)
                lines.append(f"- **{c['name']}**: dropped {drop} points over 4 quarters (NPS: {c['nps']:+d})")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _at_risk_clients(self, **kwargs) -> str:
        lines = ["## At-Risk Client Report\n"]
        at_risk = {cid: c for cid, c in CLIENTS.items() if c["risk_label"] in ("CRITICAL", "AT_RISK")}
        if not at_risk:
            lines.append("No clients currently at risk.")
            return "\n".join(lines)

        total_risk_val = sum(c["annual_value"] for c in at_risk.values())
        lines.append(f"**Clients at risk:** {len(at_risk)}")
        lines.append(f"**Total value at risk:** ${total_risk_val:,.0f}\n")

        for cid, c in sorted(at_risk.items(), key=lambda x: x[1]["health_score"]):
            churn = _churn_probability(c)
            lines.append(f"### {c['name']} -- Health: {c['health_score']}/100 ({c['risk_label']})")
            lines.append(f"- **Annual value:** ${c['annual_value']:,.0f}")
            lines.append(f"- **Churn probability:** {churn*100:.0f}%")
            lines.append(f"- **NPS:** {c['nps']:+d}")
            lines.append(f"- **Satisfaction trend:** {_satisfaction_trend(c)}")
            lines.append(f"- **Escalations (90d):** {c['escalations_90d']}")
            lines.append(f"- **Exec meetings (90d):** {c['exec_meetings_90d']}")

            lines.append("\n**Recommended retention actions:**")
            if c["exec_meetings_90d"] == 0:
                lines.append("- Schedule executive sponsor meeting within 7 days")
            if c["escalations_90d"] >= 3:
                lines.append("- Deploy SWAT team to resolve open issues")
            if c["utilization_pct"] < 60:
                lines.append("- Review scope alignment; client may not be extracting full value")
            if c["nps"] < 0:
                lines.append("- Conduct root-cause analysis on negative NPS drivers")
            lines.append(f"- Prepare value-delivered summary (ROI documentation)")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ClientHealthScoreAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
