"""
Action Prioritization Agent

Prioritizes sales actions by effort-impact analysis, generates daily
time-blocked plans, produces weekly reviews, and optimizes resource
allocation across enterprise B2B deals. Helps reps focus on the highest-
value activities.

Where a real deployment would call CRM and calendar APIs, this agent
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
    "name": "@aibast-agents-library/action-prioritization",
    "version": "1.0.0",
    "display_name": "Action Prioritization",
    "description": "Prioritizes sales actions, generates daily plans, and optimizes resource allocation across deals.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "action-prioritization", "planning", "resource-allocation"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_REP_PROFILE = {
    "name": "Michael Torres",
    "role": "Enterprise Account Executive",
    "quota": 8_000_000,
    "ytd_closed": 3_200_000,
    "pipeline_value": 7_800_000,
    "active_deals": 6,
    "available_hours_per_day": 8,
    "available_hours_per_week": 40,
}

_ACTION_ITEMS = [
    {
        "id": "act-001", "account": "Acme Corporation", "action": "Get champion intro to CTO Sarah Chen",
        "category": "Stakeholder", "impact_score": 95, "effort_hours": 1.0,
        "deadline": "2025-03-15", "deal_value": 2_400_000, "stage": "Proposal",
        "dependencies": ["Champion James Miller available"], "status": "pending",
    },
    {
        "id": "act-002", "account": "Acme Corporation", "action": "Send customized ROI calculator to CFO",
        "category": "Value Prop", "impact_score": 88, "effort_hours": 2.5,
        "deadline": "2025-03-15", "deal_value": 2_400_000, "stage": "Proposal",
        "dependencies": ["Finance team input on TCO model"], "status": "pending",
    },
    {
        "id": "act-003", "account": "Acme Corporation", "action": "Prepare competitor counter-strategy",
        "category": "Competitive", "impact_score": 82, "effort_hours": 1.5,
        "deadline": "2025-03-15", "deal_value": 2_400_000, "stage": "Proposal",
        "dependencies": [], "status": "pending",
    },
    {
        "id": "act-004", "account": "Contoso Ltd", "action": "Schedule renewal discussion with CTO",
        "category": "Retention", "impact_score": 90, "effort_hours": 0.5,
        "deadline": "2025-03-17", "deal_value": 1_100_000, "stage": "Negotiation",
        "dependencies": [], "status": "pending",
    },
    {
        "id": "act-005", "account": "Contoso Ltd", "action": "Deliver expansion proposal",
        "category": "Value Prop", "impact_score": 78, "effort_hours": 3.0,
        "deadline": "2025-03-20", "deal_value": 1_100_000, "stage": "Negotiation",
        "dependencies": ["Product team review"], "status": "in_progress",
    },
    {
        "id": "act-006", "account": "Fabrikam Industries", "action": "Conduct discovery workshop with VP IT",
        "category": "Discovery", "impact_score": 72, "effort_hours": 2.0,
        "deadline": "2025-03-21", "deal_value": 890_000, "stage": "Discovery",
        "dependencies": ["VP IT calendar confirmation"], "status": "pending",
    },
    {
        "id": "act-007", "account": "Fabrikam Industries", "action": "Share production downtime case study",
        "category": "Content", "impact_score": 55, "effort_hours": 0.5,
        "deadline": "2025-03-18", "deal_value": 890_000, "stage": "Discovery",
        "dependencies": [], "status": "pending",
    },
    {
        "id": "act-008", "account": "Northwind Traders", "action": "Initial discovery call with CTO",
        "category": "Discovery", "impact_score": 60, "effort_hours": 1.0,
        "deadline": "2025-03-22", "deal_value": 540_000, "stage": "Qualification",
        "dependencies": [], "status": "pending",
    },
    {
        "id": "act-009", "account": "Acme Corporation", "action": "Update deal forecast in CRM",
        "category": "Admin", "impact_score": 30, "effort_hours": 0.5,
        "deadline": "2025-03-16", "deal_value": 2_400_000, "stage": "Proposal",
        "dependencies": [], "status": "pending",
    },
    {
        "id": "act-010", "account": "General", "action": "Attend weekly pipeline review meeting",
        "category": "Admin", "impact_score": 40, "effort_hours": 1.0,
        "deadline": "2025-03-17", "deal_value": 0, "stage": "N/A",
        "dependencies": [], "status": "pending",
    },
]

_WEEKLY_METRICS = {
    "week_of": "2025-03-10",
    "actions_completed": 12, "actions_total": 18,
    "completion_rate": 0.67,
    "hours_selling": 22, "hours_admin": 8, "hours_meetings": 10,
    "deals_advanced": 3, "deals_stalled": 1,
    "emails_sent": 28, "meetings_held": 8, "calls_made": 15,
    "pipeline_movement": 450_000,
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _priority_score(action):
    """Compute priority from impact, deal value, and deadline proximity."""
    impact = action["impact_score"]
    value_weight = min(30, action["deal_value"] / 100_000)
    # deadline proximity bonus
    deadline_bonus = 0
    if action["deadline"]:
        days_left = 3  # synthetic approximation for urgency
        deadline_bonus = max(0, 20 - days_left * 3)
    return min(100, int(impact * 0.5 + value_weight + deadline_bonus))


def _effort_impact_quadrant(action):
    """Classify into effort-impact quadrant."""
    impact = action["impact_score"]
    effort = action["effort_hours"]
    if impact >= 70 and effort <= 1.5:
        return "Quick Wins"
    if impact >= 70:
        return "Major Projects"
    if effort <= 1.5:
        return "Fill-Ins"
    return "Reconsider"


def _sort_by_priority(actions):
    """Sort actions by computed priority score descending."""
    return sorted(actions, key=lambda a: _priority_score(a), reverse=True)


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ActionPrioritizationAgent(BasicAgent):
    """
    Prioritizes and schedules sales actions for maximum impact.

    Operations:
        prioritize_actions  - ranked list of all actions by priority
        daily_plan          - time-blocked daily schedule
        weekly_review       - weekly performance review
        resource_allocation - resource utilization analysis
    """

    def __init__(self):
        self.name = "ActionPrioritizationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "prioritize_actions", "daily_plan",
                            "weekly_review", "resource_allocation",
                        ],
                        "description": "The prioritization operation",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "prioritize_actions")
        dispatch = {
            "prioritize_actions": self._prioritize_actions,
            "daily_plan": self._daily_plan,
            "weekly_review": self._weekly_review,
            "resource_allocation": self._resource_allocation,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler()

    # ── prioritize_actions ────────────────────────────────────
    def _prioritize_actions(self):
        sorted_actions = _sort_by_priority(_ACTION_ITEMS)

        rows = ""
        for rank, a in enumerate(sorted_actions, 1):
            score = _priority_score(a)
            quadrant = _effort_impact_quadrant(a)
            rows += (
                f"| {rank} | {a['action'][:45]} | {a['account']} | "
                f"{score}/100 | {a['effort_hours']}h | {quadrant} | {a['deadline']} |\n"
            )

        quick_wins = [a for a in sorted_actions if _effort_impact_quadrant(a) == "Quick Wins"]
        total_effort = sum(a["effort_hours"] for a in sorted_actions if a["status"] == "pending")

        return (
            f"**Action Priority List: {_REP_PROFILE['name']}**\n\n"
            f"Total pending actions: {sum(1 for a in _ACTION_ITEMS if a['status'] == 'pending')}\n"
            f"Total effort required: {total_effort:.1f} hours\n"
            f"Quick wins available: {len(quick_wins)}\n\n"
            f"| Rank | Action | Account | Priority | Effort | Quadrant | Deadline |\n|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Quick Wins (do first):**\n"
            + "".join(f"- {a['action']} ({a['account']}, {a['effort_hours']}h)\n" for a in quick_wins)
            + f"\nSource: [CRM Actions + Deal Intelligence + Calendar]\n"
            f"Agents: ActionPrioritizationAgent"
        )

    # ── daily_plan ────────────────────────────────────────────
    def _daily_plan(self):
        sorted_actions = _sort_by_priority(_ACTION_ITEMS)
        pending = [a for a in sorted_actions if a["status"] == "pending"]

        schedule = [
            {"time": "8:00 AM", "duration": "30 min", "action": "Review pipeline and prioritize", "type": "Planning"},
            {"time": "8:30 AM", "duration": "60 min", "action": pending[0]["action"] if len(pending) > 0 else "Open block", "type": pending[0]["category"] if len(pending) > 0 else "Free"},
            {"time": "9:30 AM", "duration": "30 min", "action": pending[1]["action"] if len(pending) > 1 else "Open block", "type": pending[1]["category"] if len(pending) > 1 else "Free"},
            {"time": "10:00 AM", "duration": "60 min", "action": pending[2]["action"] if len(pending) > 2 else "Open block", "type": pending[2]["category"] if len(pending) > 2 else "Free"},
            {"time": "11:00 AM", "duration": "30 min", "action": "Email follow-ups and LinkedIn engagement", "type": "Outreach"},
            {"time": "11:30 AM", "duration": "60 min", "action": pending[3]["action"] if len(pending) > 3 else "Open block", "type": pending[3]["category"] if len(pending) > 3 else "Free"},
            {"time": "12:30 PM", "duration": "60 min", "action": "Lunch break", "type": "Break"},
            {"time": "1:30 PM", "duration": "90 min", "action": pending[4]["action"] if len(pending) > 4 else "Open block", "type": pending[4]["category"] if len(pending) > 4 else "Free"},
            {"time": "3:00 PM", "duration": "60 min", "action": pending[5]["action"] if len(pending) > 5 else "Open block", "type": pending[5]["category"] if len(pending) > 5 else "Free"},
            {"time": "4:00 PM", "duration": "60 min", "action": "CRM updates and end-of-day review", "type": "Admin"},
        ]

        sched_rows = ""
        for s in schedule:
            sched_rows += f"| {s['time']} | {s['duration']} | {s['action'][:50]} | {s['type']} |\n"

        selling_hours = sum(1 for s in schedule if s["type"] not in ("Planning", "Admin", "Break", "Free")) * 0.75
        admin_hours = sum(1 for s in schedule if s["type"] in ("Planning", "Admin")) * 0.5

        return (
            f"**Daily Plan: {_REP_PROFILE['name']}**\n\n"
            f"| Time | Duration | Activity | Type |\n|---|---|---|---|\n"
            f"{sched_rows}\n"
            f"**Day Summary:**\n"
            f"- Selling activities: ~{selling_hours:.1f} hours\n"
            f"- Admin/planning: ~{admin_hours:.1f} hours\n"
            f"- Top priority: {pending[0]['action'] if pending else 'N/A'}\n"
            f"- Deals touched: {len(set(a['account'] for a in pending[:6]))}\n\n"
            f"Source: [CRM + Calendar + Action Engine]\n"
            f"Agents: ActionPrioritizationAgent"
        )

    # ── weekly_review ─────────────────────────────────────────
    def _weekly_review(self):
        m = _WEEKLY_METRICS
        quota_pct = _REP_PROFILE["ytd_closed"] / _REP_PROFILE["quota"] * 100
        pipeline_coverage = _REP_PROFILE["pipeline_value"] / (_REP_PROFILE["quota"] - _REP_PROFILE["ytd_closed"])

        selling_pct = m["hours_selling"] / (m["hours_selling"] + m["hours_admin"] + m["hours_meetings"]) * 100

        # Account-level summary
        acct_actions = {}
        for a in _ACTION_ITEMS:
            acct = a["account"]
            if acct not in acct_actions:
                acct_actions[acct] = {"total": 0, "pending": 0, "deal_value": a["deal_value"]}
            acct_actions[acct]["total"] += 1
            if a["status"] == "pending":
                acct_actions[acct]["pending"] += 1

        acct_rows = ""
        for acct, data in sorted(acct_actions.items(), key=lambda x: x[1]["deal_value"], reverse=True):
            acct_rows += f"| {acct} | ${data['deal_value']:,} | {data['total']} | {data['pending']} |\n"

        return (
            f"**Weekly Review: {_REP_PROFILE['name']}**\n"
            f"Week of {m['week_of']}\n\n"
            f"**Performance Summary:**\n\n"
            f"| Metric | Value | Target |\n|---|---|---|\n"
            f"| Actions Completed | {m['actions_completed']}/{m['actions_total']} | 90%+ |\n"
            f"| Completion Rate | {m['completion_rate']:.0%} | 85%+ |\n"
            f"| Selling Hours | {m['hours_selling']}h ({selling_pct:.0f}%) | 60%+ |\n"
            f"| Emails Sent | {m['emails_sent']} | 30+ |\n"
            f"| Meetings Held | {m['meetings_held']} | 10+ |\n"
            f"| Calls Made | {m['calls_made']} | 20+ |\n"
            f"| Deals Advanced | {m['deals_advanced']} | 3+ |\n"
            f"| Deals Stalled | {m['deals_stalled']} | 0 |\n"
            f"| Pipeline Movement | ${m['pipeline_movement']:,} | $500K+ |\n\n"
            f"**Quota Progress:**\n"
            f"- YTD Closed: ${_REP_PROFILE['ytd_closed']:,} ({quota_pct:.0f}% of ${_REP_PROFILE['quota']:,})\n"
            f"- Pipeline: ${_REP_PROFILE['pipeline_value']:,} ({pipeline_coverage:.1f}x coverage)\n\n"
            f"**Account Activity:**\n\n"
            f"| Account | Deal Value | Total Actions | Pending |\n|---|---|---|---|\n"
            f"{acct_rows}\n"
            f"**Recommendations:**\n"
            f"- Increase selling time ratio (currently {selling_pct:.0f}%, target 60%+)\n"
            f"- Address stalled deal: schedule re-engagement within 48 hours\n"
            f"- Prioritize Acme Corporation actions (highest deal value)\n\n"
            f"Source: [CRM Activity + Calendar + Pipeline Analytics]\n"
            f"Agents: ActionPrioritizationAgent"
        )

    # ── resource_allocation ───────────────────────────────────
    def _resource_allocation(self):
        # Time allocation by account (based on deal value weighting)
        accounts_data = {}
        for a in _ACTION_ITEMS:
            acct = a["account"]
            if acct not in accounts_data:
                accounts_data[acct] = {"effort": 0, "deal_value": a["deal_value"], "actions": 0}
            if a["status"] == "pending":
                accounts_data[acct]["effort"] += a["effort_hours"]
                accounts_data[acct]["actions"] += 1

        total_effort = sum(d["effort"] for d in accounts_data.values())
        total_value = sum(d["deal_value"] for d in accounts_data.values() if d["deal_value"] > 0)

        alloc_rows = ""
        for acct, data in sorted(accounts_data.items(), key=lambda x: x[1]["deal_value"], reverse=True):
            effort_pct = data["effort"] / max(total_effort, 1) * 100
            value_pct = data["deal_value"] / max(total_value, 1) * 100 if data["deal_value"] > 0 else 0
            alignment = "Aligned" if abs(effort_pct - value_pct) < 15 else "Under-invested" if effort_pct < value_pct else "Over-invested"
            alloc_rows += (
                f"| {acct} | ${data['deal_value']:,} | {value_pct:.0f}% | "
                f"{data['effort']:.1f}h | {effort_pct:.0f}% | {data['actions']} | {alignment} |\n"
            )

        # Category breakdown
        category_hours = {}
        for a in _ACTION_ITEMS:
            cat = a["category"]
            if cat not in category_hours:
                category_hours[cat] = 0
            if a["status"] == "pending":
                category_hours[cat] += a["effort_hours"]

        cat_rows = ""
        for cat, hours in sorted(category_hours.items(), key=lambda x: x[1], reverse=True):
            pct = hours / max(total_effort, 1) * 100
            cat_rows += f"| {cat} | {hours:.1f}h | {pct:.0f}% |\n"

        weekly_capacity = _REP_PROFILE["available_hours_per_week"]
        utilization = total_effort / weekly_capacity * 100

        return (
            f"**Resource Allocation: {_REP_PROFILE['name']}**\n\n"
            f"**Capacity Overview:**\n"
            f"- Weekly capacity: {weekly_capacity}h\n"
            f"- Pending effort: {total_effort:.1f}h\n"
            f"- Utilization: {utilization:.0f}%\n"
            f"- Status: {'Over-committed' if utilization > 100 else 'Available capacity' if utilization < 80 else 'Well-utilized'}\n\n"
            f"**Allocation by Account:**\n\n"
            f"| Account | Deal Value | Value % | Effort | Effort % | Actions | Alignment |\n|---|---|---|---|---|---|---|\n"
            f"{alloc_rows}\n"
            f"**Allocation by Category:**\n\n"
            f"| Category | Hours | % of Total |\n|---|---|---|\n"
            f"{cat_rows}\n"
            f"**Optimization Recommendations:**\n"
            f"- Allocate effort proportional to deal value\n"
            f"- Automate admin tasks to increase selling time\n"
            f"- Delegate low-impact activities where possible\n\n"
            f"Source: [CRM + Calendar + Capacity Planning]\n"
            f"Agents: ActionPrioritizationAgent"
        )


if __name__ == "__main__":
    agent = ActionPrioritizationAgent()
    for op in ["prioritize_actions", "daily_plan", "weekly_review", "resource_allocation"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
