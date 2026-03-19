"""
Customer Onboarding Agent for Software/Digital Products.

Tracks customer onboarding progress, milestone completion, feature adoption
metrics, and risk flags for SaaS customer success teams managing enterprise
onboarding pipelines.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/software-customer-onboarding",
    "version": "1.0.0",
    "display_name": "Customer Onboarding Agent",
    "description": "Tracks SaaS customer onboarding status, milestone completion, feature adoption metrics, and risk flags.",
    "author": "AIBAST",
    "tags": ["onboarding", "customer-success", "saas", "adoption", "milestones"],
    "category": "software_digital_products",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "CUST-1001": {
        "name": "Meridian Healthcare Systems",
        "plan": "Enterprise",
        "arr": 186000,
        "onboarding_start": "2026-01-15",
        "target_go_live": "2026-03-31",
        "csm": "Priya Sharma",
        "health_score": 72,
        "milestones": {
            "kickoff_complete": {"status": "complete", "date": "2026-01-18"},
            "sso_configured": {"status": "complete", "date": "2026-01-25"},
            "data_migration": {"status": "complete", "date": "2026-02-10"},
            "integration_setup": {"status": "in_progress", "date": None},
            "user_training": {"status": "not_started", "date": None},
            "go_live": {"status": "not_started", "date": None},
        },
        "feature_adoption": {
            "dashboard": 88,
            "reporting": 62,
            "api_access": 45,
            "automation_rules": 12,
            "custom_fields": 33,
        },
        "training_completion_pct": 41,
        "active_users": 28,
        "licensed_users": 75,
    },
    "CUST-1002": {
        "name": "Apex Financial Group",
        "plan": "Enterprise",
        "arr": 240000,
        "onboarding_start": "2026-02-01",
        "target_go_live": "2026-04-15",
        "csm": "Marcus Chen",
        "health_score": 89,
        "milestones": {
            "kickoff_complete": {"status": "complete", "date": "2026-02-03"},
            "sso_configured": {"status": "complete", "date": "2026-02-08"},
            "data_migration": {"status": "complete", "date": "2026-02-20"},
            "integration_setup": {"status": "complete", "date": "2026-03-05"},
            "user_training": {"status": "in_progress", "date": None},
            "go_live": {"status": "not_started", "date": None},
        },
        "feature_adoption": {
            "dashboard": 95,
            "reporting": 81,
            "api_access": 72,
            "automation_rules": 55,
            "custom_fields": 68,
        },
        "training_completion_pct": 73,
        "active_users": 92,
        "licensed_users": 120,
    },
    "CUST-1003": {
        "name": "Vanguard Logistics",
        "plan": "Professional",
        "arr": 84000,
        "onboarding_start": "2025-12-10",
        "target_go_live": "2026-02-28",
        "csm": "Priya Sharma",
        "health_score": 38,
        "milestones": {
            "kickoff_complete": {"status": "complete", "date": "2025-12-13"},
            "sso_configured": {"status": "complete", "date": "2025-12-20"},
            "data_migration": {"status": "blocked", "date": None},
            "integration_setup": {"status": "not_started", "date": None},
            "user_training": {"status": "not_started", "date": None},
            "go_live": {"status": "not_started", "date": None},
        },
        "feature_adoption": {
            "dashboard": 55,
            "reporting": 20,
            "api_access": 0,
            "automation_rules": 0,
            "custom_fields": 10,
        },
        "training_completion_pct": 15,
        "active_users": 8,
        "licensed_users": 40,
    },
    "CUST-1004": {
        "name": "BrightPath Education",
        "plan": "Professional",
        "arr": 96000,
        "onboarding_start": "2026-02-20",
        "target_go_live": "2026-04-30",
        "csm": "Marcus Chen",
        "health_score": 81,
        "milestones": {
            "kickoff_complete": {"status": "complete", "date": "2026-02-22"},
            "sso_configured": {"status": "complete", "date": "2026-03-01"},
            "data_migration": {"status": "in_progress", "date": None},
            "integration_setup": {"status": "not_started", "date": None},
            "user_training": {"status": "not_started", "date": None},
            "go_live": {"status": "not_started", "date": None},
        },
        "feature_adoption": {
            "dashboard": 78,
            "reporting": 45,
            "api_access": 22,
            "automation_rules": 5,
            "custom_fields": 30,
        },
        "training_completion_pct": 28,
        "active_users": 15,
        "licensed_users": 35,
    },
    "CUST-1005": {
        "name": "Orion Manufacturing",
        "plan": "Enterprise",
        "arr": 312000,
        "onboarding_start": "2026-03-01",
        "target_go_live": "2026-05-15",
        "csm": "Priya Sharma",
        "health_score": 91,
        "milestones": {
            "kickoff_complete": {"status": "complete", "date": "2026-03-03"},
            "sso_configured": {"status": "in_progress", "date": None},
            "data_migration": {"status": "not_started", "date": None},
            "integration_setup": {"status": "not_started", "date": None},
            "user_training": {"status": "not_started", "date": None},
            "go_live": {"status": "not_started", "date": None},
        },
        "feature_adoption": {
            "dashboard": 40,
            "reporting": 15,
            "api_access": 10,
            "automation_rules": 0,
            "custom_fields": 5,
        },
        "training_completion_pct": 8,
        "active_users": 12,
        "licensed_users": 200,
    },
}

RISK_THRESHOLDS = {
    "health_score_critical": 40,
    "health_score_warning": 60,
    "training_min_pct": 50,
    "adoption_min_pct": 30,
    "user_activation_min_pct": 40,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _onboarding_status_summary():
    total = len(CUSTOMERS)
    on_track = sum(1 for c in CUSTOMERS.values() if c["health_score"] >= 70)
    at_risk = sum(1 for c in CUSTOMERS.values() if 40 <= c["health_score"] < 70)
    critical = sum(1 for c in CUSTOMERS.values() if c["health_score"] < 40)
    total_arr = sum(c["arr"] for c in CUSTOMERS.values())
    return {
        "total_customers": total,
        "on_track": on_track,
        "at_risk": at_risk,
        "critical": critical,
        "total_arr": total_arr,
        "customers": {cid: {"name": c["name"], "health_score": c["health_score"],
                            "plan": c["plan"], "target_go_live": c["target_go_live"]}
                      for cid, c in CUSTOMERS.items()},
    }


def _milestone_tracking():
    results = {}
    for cid, c in CUSTOMERS.items():
        ms = c["milestones"]
        done = sum(1 for m in ms.values() if m["status"] == "complete")
        total = len(ms)
        blocked = [k for k, v in ms.items() if v["status"] == "blocked"]
        next_ms = next((k for k, v in ms.items() if v["status"] in ("in_progress", "not_started")), None)
        results[cid] = {
            "name": c["name"], "completed": done, "total": total,
            "pct": round(done / total * 100, 1), "blocked": blocked,
            "next_milestone": next_ms,
        }
    return results


def _adoption_metrics():
    results = {}
    for cid, c in CUSTOMERS.items():
        fa = c["feature_adoption"]
        avg = round(sum(fa.values()) / len(fa), 1)
        act_pct = round(c["active_users"] / c["licensed_users"] * 100, 1) if c["licensed_users"] else 0
        results[cid] = {
            "name": c["name"], "avg_adoption_pct": avg,
            "feature_adoption": fa, "training_pct": c["training_completion_pct"],
            "activation_pct": act_pct, "active_users": c["active_users"],
            "licensed_users": c["licensed_users"],
        }
    return results


def _risk_flags():
    flags = []
    for cid, c in CUSTOMERS.items():
        cflags = []
        if c["health_score"] < RISK_THRESHOLDS["health_score_critical"]:
            cflags.append("CRITICAL: Health score below threshold")
        elif c["health_score"] < RISK_THRESHOLDS["health_score_warning"]:
            cflags.append("WARNING: Health score declining")
        if c["training_completion_pct"] < RISK_THRESHOLDS["training_min_pct"]:
            cflags.append("Low training completion")
        act = round(c["active_users"] / c["licensed_users"] * 100, 1) if c["licensed_users"] else 0
        if act < RISK_THRESHOLDS["user_activation_min_pct"]:
            cflags.append("Low user activation")
        blocked = [k for k, v in c["milestones"].items() if v["status"] == "blocked"]
        if blocked:
            cflags.append(f"Blocked milestones: {', '.join(blocked)}")
        if cflags:
            flags.append({"id": cid, "name": c["name"], "arr": c["arr"],
                          "health_score": c["health_score"], "flags": cflags})
    flags.sort(key=lambda x: x["health_score"])
    return flags


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class CustomerOnboardingAgent(BasicAgent):
    """Customer onboarding tracking and risk assessment agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/software-customer-onboarding"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "onboarding_status",
                            "milestone_tracking",
                            "adoption_metrics",
                            "risk_flags",
                        ],
                        "description": "The onboarding operation to perform.",
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Optional customer ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "onboarding_status")
        if op == "onboarding_status":
            return self._onboarding_status()
        elif op == "milestone_tracking":
            return self._milestone_tracking()
        elif op == "adoption_metrics":
            return self._adoption_metrics()
        elif op == "risk_flags":
            return self._risk_flags()
        return f"**Error:** Unknown operation `{op}`."

    def _onboarding_status(self) -> str:
        data = _onboarding_status_summary()
        lines = [
            "# Customer Onboarding Pipeline",
            "",
            f"**Total Customers:** {data['total_customers']} | "
            f"**Pipeline ARR:** ${data['total_arr']:,}",
            "",
            f"- On Track: {data['on_track']}",
            f"- At Risk: {data['at_risk']}",
            f"- Critical: {data['critical']}",
            "",
            "| Customer | Plan | Health | Target Go-Live |",
            "|----------|------|--------|----------------|",
        ]
        for cid, info in data["customers"].items():
            lines.append(
                f"| {info['name']} | {info['plan']} | {info['health_score']} | {info['target_go_live']} |"
            )
        return "\n".join(lines)

    def _milestone_tracking(self) -> str:
        data = _milestone_tracking()
        lines = [
            "# Milestone Tracking",
            "",
            "| Customer | Completed | Progress | Blocked | Next Milestone |",
            "|----------|-----------|----------|---------|----------------|",
        ]
        for cid, m in data.items():
            blocked_str = ", ".join(m["blocked"]) if m["blocked"] else "None"
            lines.append(
                f"| {m['name']} | {m['completed']}/{m['total']} | {m['pct']}% "
                f"| {blocked_str} | {m['next_milestone'] or 'N/A'} |"
            )
        return "\n".join(lines)

    def _adoption_metrics(self) -> str:
        data = _adoption_metrics()
        lines = ["# Feature Adoption Metrics", ""]
        for cid, m in data.items():
            lines.append(f"## {m['name']}")
            lines.append(f"- Avg Adoption: {m['avg_adoption_pct']}%")
            lines.append(f"- Training: {m['training_pct']}%")
            lines.append(f"- User Activation: {m['activation_pct']}% ({m['active_users']}/{m['licensed_users']})")
            lines.append("")
            lines.append("| Feature | Adoption % |")
            lines.append("|---------|-----------|")
            for feat, pct in m["feature_adoption"].items():
                lines.append(f"| {feat.replace('_', ' ').title()} | {pct}% |")
            lines.append("")
        return "\n".join(lines)

    def _risk_flags(self) -> str:
        data = _risk_flags()
        if not data:
            return "# Risk Flags\n\nNo customers currently flagged."
        lines = ["# Customer Risk Flags", ""]
        for entry in data:
            lines.append(f"## {entry['name']} (ARR: ${entry['arr']:,})")
            lines.append(f"Health Score: {entry['health_score']}")
            for flag in entry["flags"]:
                lines.append(f"- {flag}")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = CustomerOnboardingAgent()
    for op in ["onboarding_status", "milestone_tracking", "adoption_metrics", "risk_flags"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
