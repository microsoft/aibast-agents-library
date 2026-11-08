"""
Next Best Action Agent

Recommends prioritized next-best actions for each deal based on stage,
risk factors, engagement history, and rep profiles. Generates sequenced
action plans, forecasts expected impact, and optimizes rep assignments
to maximize pipeline velocity.

Where a real deployment would call Salesforce, Outreach, Gong, etc., this
agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ===================================================================
# RAPP AGENT MANIFEST
# ===================================================================
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/next-best-action",
    "version": "1.0.0",
    "display_name": "Next Best Action",
    "description": "Recommends prioritized actions, sequences tasks, forecasts impact, and optimizes rep assignments.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "next-best-action", "deal-progression", "recommendations"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ===================================================================
# SYNTHETIC DATA LAYER
# ===================================================================

_ACTION_TEMPLATES = {
    "executive_outreach": {
        "name": "Executive Sponsor Outreach",
        "effort_hours": 2.0, "impact_score": 85,
        "description": "VP-to-VP outreach to establish executive alignment",
        "applicable_stages": ["Proposal", "Negotiation"],
        "applicable_blockers": ["executive_change", "no_champion", "stakeholder_alignment"],
    },
    "champion_reengagement": {
        "name": "Champion Re-engagement",
        "effort_hours": 1.5, "impact_score": 78,
        "description": "Personalized outreach to silent or disengaged champion",
        "applicable_stages": ["Discovery", "Proposal", "Negotiation"],
        "applicable_blockers": ["executive_change", "competitor_eval"],
    },
    "roi_business_case": {
        "name": "ROI Business Case Delivery",
        "effort_hours": 4.0, "impact_score": 82,
        "description": "CFO-ready business case with 3-year TCO analysis",
        "applicable_stages": ["Proposal", "Negotiation"],
        "applicable_blockers": ["budget_hold"],
    },
    "competitive_differentiation": {
        "name": "Competitive Differentiation Session",
        "effort_hours": 3.0, "impact_score": 75,
        "description": "Head-to-head comparison with proof points and references",
        "applicable_stages": ["Discovery", "Proposal"],
        "applicable_blockers": ["competitor_eval", "technical_validation"],
    },
    "legal_fast_track": {
        "name": "Legal Fast-Track Package",
        "effort_hours": 1.0, "impact_score": 70,
        "description": "Pre-approved contract template with flexible terms",
        "applicable_stages": ["Negotiation", "Contract"],
        "applicable_blockers": ["legal_review", "procurement_process"],
    },
    "reference_call": {
        "name": "Customer Reference Call",
        "effort_hours": 1.5, "impact_score": 72,
        "description": "Arrange reference call with similar customer in same vertical",
        "applicable_stages": ["Discovery", "Proposal"],
        "applicable_blockers": ["competitor_eval", "technical_validation", "timeline_uncertainty"],
    },
    "technical_deep_dive": {
        "name": "Technical Deep-Dive Workshop",
        "effort_hours": 3.0, "impact_score": 68,
        "description": "Hands-on technical session with prospect engineering team",
        "applicable_stages": ["Discovery", "Proposal"],
        "applicable_blockers": ["technical_validation"],
    },
    "multi_thread_outreach": {
        "name": "Multi-Thread Outreach Campaign",
        "effort_hours": 2.5, "impact_score": 65,
        "description": "Engage 3+ contacts across departments simultaneously",
        "applicable_stages": ["Qualification", "Discovery"],
        "applicable_blockers": ["no_champion", "stakeholder_alignment"],
    },
    "contract_negotiation": {
        "name": "Contract Terms Negotiation",
        "effort_hours": 2.0, "impact_score": 80,
        "description": "Address outstanding contract terms with procurement/legal",
        "applicable_stages": ["Negotiation", "Contract"],
        "applicable_blockers": ["legal_review", "procurement_process"],
    },
    "value_workshop": {
        "name": "Value Realization Workshop",
        "effort_hours": 3.5, "impact_score": 74,
        "description": "On-site workshop demonstrating business value and implementation plan",
        "applicable_stages": ["Proposal", "Negotiation"],
        "applicable_blockers": ["budget_hold", "timeline_uncertainty"],
    },
}

_DEAL_CONTEXT = {
    "TechCorp Industries": {
        "deal_id": "OPP-001", "value": 890000, "stage": "Proposal", "owner": "Mike Chen",
        "blocker": "executive_change", "days_in_stage": 34, "last_contact_days": 18,
        "champion_status": "Silent", "risk_score": 72, "health_score": 42,
    },
    "Global Manufacturing": {
        "deal_id": "OPP-002", "value": 720000, "stage": "Negotiation", "owner": "Lisa Torres",
        "blocker": "legal_review", "days_in_stage": 28, "last_contact_days": 5,
        "champion_status": "Active frustrated", "risk_score": 44, "health_score": 63,
    },
    "Apex Financial": {
        "deal_id": "OPP-003", "value": 580000, "stage": "Discovery", "owner": "James Park",
        "blocker": "competitor_eval", "days_in_stage": 25, "last_contact_days": 12,
        "champion_status": "Disengaged", "risk_score": 70, "health_score": 32,
    },
    "Metro Healthcare": {
        "deal_id": "OPP-004", "value": 440000, "stage": "Proposal", "owner": "Mike Chen",
        "blocker": "budget_hold", "days_in_stage": 22, "last_contact_days": 9,
        "champion_status": "Active", "risk_score": 42, "health_score": 67,
    },
    "Pacific Telecom": {
        "deal_id": "OPP-013", "value": 780000, "stage": "Negotiation", "owner": "Lisa Torres",
        "blocker": "procurement_process", "days_in_stage": 14, "last_contact_days": 3,
        "champion_status": "Active", "risk_score": 16, "health_score": 85,
    },
    "Pinnacle Logistics": {
        "deal_id": "OPP-005", "value": 360000, "stage": "Qualification", "owner": "James Park",
        "blocker": "no_champion", "days_in_stage": 20, "last_contact_days": 14,
        "champion_status": "Silent", "risk_score": 68, "health_score": 28,
    },
}

_REP_PROFILES = {
    "Mike Chen": {"title": "Sr. Account Executive", "specialty": "executive alignment",
                  "active_deals": 11, "capacity": 14, "avg_close_rate": 0.34,
                  "strengths": ["C-level relationships", "Complex deal navigation"]},
    "Lisa Torres": {"title": "Account Executive", "specialty": "contract negotiation",
                    "active_deals": 9, "capacity": 12, "avg_close_rate": 0.38,
                    "strengths": ["Procurement expertise", "Legal coordination"]},
    "James Park": {"title": "Sr. Account Executive", "specialty": "technical sales",
                   "active_deals": 12, "capacity": 14, "avg_close_rate": 0.31,
                   "strengths": ["Technical depth", "Solution architecture"]},
    "Sarah Kim": {"title": "Account Executive", "specialty": "executive alignment",
                  "active_deals": 8, "capacity": 12, "avg_close_rate": 0.36,
                  "strengths": ["Relationship building", "Stakeholder management"]},
    "Ryan Davis": {"title": "Account Executive", "specialty": "mid-market",
                   "active_deals": 7, "capacity": 12, "avg_close_rate": 0.42,
                   "strengths": ["Fast deal cycles", "SMB/mid-market focus"]},
}

_HISTORICAL_OUTCOMES = {
    "executive_outreach": {"success_rate": 0.72, "avg_days_to_impact": 5, "stage_advance_rate": 0.45},
    "champion_reengagement": {"success_rate": 0.65, "avg_days_to_impact": 3, "stage_advance_rate": 0.35},
    "roi_business_case": {"success_rate": 0.68, "avg_days_to_impact": 7, "stage_advance_rate": 0.40},
    "competitive_differentiation": {"success_rate": 0.62, "avg_days_to_impact": 5, "stage_advance_rate": 0.30},
    "legal_fast_track": {"success_rate": 0.80, "avg_days_to_impact": 4, "stage_advance_rate": 0.55},
    "reference_call": {"success_rate": 0.70, "avg_days_to_impact": 3, "stage_advance_rate": 0.28},
    "technical_deep_dive": {"success_rate": 0.66, "avg_days_to_impact": 5, "stage_advance_rate": 0.32},
    "multi_thread_outreach": {"success_rate": 0.55, "avg_days_to_impact": 7, "stage_advance_rate": 0.20},
    "contract_negotiation": {"success_rate": 0.78, "avg_days_to_impact": 5, "stage_advance_rate": 0.50},
    "value_workshop": {"success_rate": 0.64, "avg_days_to_impact": 8, "stage_advance_rate": 0.38},
}


# ===================================================================
# HELPERS
# ===================================================================

def _recommend_for_deal(deal_name):
    """Generate ranked action recommendations for a deal."""
    ctx = _DEAL_CONTEXT.get(deal_name, {})
    stage = ctx.get("stage", "")
    blocker = ctx.get("blocker", "")
    recommendations = []
    for action_id, template in _ACTION_TEMPLATES.items():
        if stage in template["applicable_stages"] and blocker in template["applicable_blockers"]:
            outcome = _HISTORICAL_OUTCOMES.get(action_id, {})
            priority_score = (
                template["impact_score"] * 0.4 +
                outcome.get("success_rate", 0.5) * 100 * 0.3 +
                (100 - outcome.get("avg_days_to_impact", 5) * 10) * 0.3
            )
            recommendations.append({
                "action_id": action_id,
                "name": template["name"],
                "description": template["description"],
                "effort_hours": template["effort_hours"],
                "priority_score": round(priority_score, 1),
                "success_rate": outcome.get("success_rate", 0.5),
                "days_to_impact": outcome.get("avg_days_to_impact", 5),
            })
    return sorted(recommendations, key=lambda r: -r["priority_score"])


def _expected_impact(deal_name, action_id):
    """Forecast expected impact of an action on a deal."""
    ctx = _DEAL_CONTEXT.get(deal_name, {})
    outcome = _HISTORICAL_OUTCOMES.get(action_id, {})
    value = ctx.get("value", 0)
    success_rate = outcome.get("success_rate", 0.5)
    stage_advance = outcome.get("stage_advance_rate", 0.3)
    expected_value_impact = round(value * success_rate * stage_advance)
    return expected_value_impact


# ===================================================================
# AGENT CLASS
# ===================================================================

class NextBestActionAgent(BasicAgent):
    """
    Recommends prioritized next-best actions for pipeline deals.

    Operations:
        recommend_actions  - prioritized action recommendations per deal
        action_sequence    - sequenced multi-step action plans
        impact_forecast    - expected impact of recommended actions
        rep_assignments    - optimal rep assignment for actions
    """

    def __init__(self):
        self.name = "NextBestActionAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["recommend_actions", "action_sequence", "impact_forecast", "rep_assignments"],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "recommend_actions")
        dispatch = {
            "recommend_actions": self._recommend_actions,
            "action_sequence": self._action_sequence,
            "impact_forecast": self._impact_forecast,
            "rep_assignments": self._rep_assignments,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation '{op}'. Valid: {', '.join(dispatch.keys())}"
        return handler()

    # -- recommend_actions ---------------------------------------------
    def _recommend_actions(self) -> str:
        sections = []
        total_actions = 0
        for deal_name in sorted(_DEAL_CONTEXT.keys(), key=lambda d: -_DEAL_CONTEXT[d]["value"]):
            ctx = _DEAL_CONTEXT[deal_name]
            recs = _recommend_for_deal(deal_name)
            total_actions += len(recs)

            rows = ""
            for i, r in enumerate(recs[:4], 1):
                rows += (f"| {i} | {r['name']} | {r['priority_score']} | "
                         f"{r['effort_hours']}h | {r['success_rate']:.0%} | {r['days_to_impact']}d |\n")

            urgency = "IMMEDIATE" if ctx["risk_score"] >= 60 else ("THIS WEEK" if ctx["risk_score"] >= 40 else "STANDARD")
            sections.append(
                f"**{deal_name} -- ${ctx['value']:,} ({ctx['stage']})**\n"
                f"Risk: {ctx['risk_score']}/100 | Health: {ctx['health_score']}/100 | Urgency: {urgency}\n\n"
                f"| # | Action | Priority | Effort | Success Rate | Time to Impact |\n"
                f"|---|--------|----------|--------|-------------|---------------|\n"
                f"{rows}"
            )

        return (
            f"**Next Best Action Recommendations -- {len(_DEAL_CONTEXT)} Deals**\n\n"
            f"Total actions recommended: **{total_actions}**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\nSource: [Deal Context + Historical Outcomes + Action Library]\n"
            f"Agents: ActionRecommendationEngine"
        )

    # -- action_sequence -----------------------------------------------
    def _action_sequence(self) -> str:
        sections = []
        for deal_name in sorted(_DEAL_CONTEXT.keys(), key=lambda d: -_DEAL_CONTEXT[d]["value"]):
            ctx = _DEAL_CONTEXT[deal_name]
            recs = _recommend_for_deal(deal_name)
            if not recs:
                continue

            day = 1
            sequence = []
            for r in recs[:4]:
                end_day = day + r["days_to_impact"] - 1
                sequence.append(f"- **Days {day}-{end_day}:** {r['name']} -- {r['description']}")
                day = end_day + 1

            total_days = day - 1
            sections.append(
                f"**{deal_name} -- ${ctx['value']:,}**\n"
                f"Total sequence: {total_days} days | Owner: {ctx['owner']}\n\n"
                + "\n".join(sequence)
                + f"\n- **Day {total_days + 1}:** Review progress and reassess\n"
            )

        return (
            f"**Action Sequences -- Multi-Step Plans**\n\n"
            f"Sequenced for optimal execution and minimal rep context-switching.\n\n"
            + "\n\n---\n\n".join(sections)
            + f"\n\nSource: [Action Sequencing Model + Rep Calendars]\n"
            f"Agents: SequencePlannerAgent"
        )

    # -- impact_forecast -----------------------------------------------
    def _impact_forecast(self) -> str:
        rows = ""
        total_expected = 0
        total_pipeline = 0

        for deal_name in sorted(_DEAL_CONTEXT.keys(), key=lambda d: -_DEAL_CONTEXT[d]["value"]):
            ctx = _DEAL_CONTEXT[deal_name]
            recs = _recommend_for_deal(deal_name)
            total_pipeline += ctx["value"]

            if recs:
                top_action = recs[0]
                impact = _expected_impact(deal_name, top_action["action_id"])
                total_expected += impact
                outcome = _HISTORICAL_OUTCOMES.get(top_action["action_id"], {})
                advance_pct = round(outcome.get("stage_advance_rate", 0.3) * 100)
                rows += (f"| {deal_name} | ${ctx['value']:,} | {top_action['name']} | "
                         f"${impact:,} | {advance_pct}% | {top_action['days_to_impact']}d |\n")

        roi_pct = round(total_expected / max(total_pipeline, 1) * 100, 1)

        return (
            f"**Impact Forecast -- Expected Outcomes**\n\n"
            f"Total pipeline: ${total_pipeline:,} | Expected value impact: ${total_expected:,}\n"
            f"Action ROI: {roi_pct}% of pipeline value influenced\n\n"
            f"| Deal | Value | Top Action | Expected Impact | Stage Advance | Timeline |\n"
            f"|------|-------|-----------|----------------|--------------|----------|\n"
            f"{rows}\n"
            f"**Assumptions:**\n"
            f"- Impact based on historical success rates for similar actions\n"
            f"- Stage advance probability assumes timely execution\n"
            f"- Expected value = Deal value x Success rate x Stage advance rate\n\n"
            f"Source: [Historical Outcomes + Predictive Model]\n"
            f"Agents: ForecastEngine"
        )

    # -- rep_assignments -----------------------------------------------
    def _rep_assignments(self) -> str:
        assignments = []
        for deal_name in sorted(_DEAL_CONTEXT.keys(), key=lambda d: -_DEAL_CONTEXT[d]["value"]):
            ctx = _DEAL_CONTEXT[deal_name]
            recs = _recommend_for_deal(deal_name)
            if not recs:
                continue

            top_action = recs[0]
            owner = ctx["owner"]
            owner_profile = _REP_PROFILES.get(owner, {})
            available = owner_profile.get("capacity", 12) - owner_profile.get("active_deals", 10)

            # Check if a specialist would be better
            best_rep = owner
            best_reason = "Current owner, maintains continuity"
            for rep_name, profile in _REP_PROFILES.items():
                rep_available = profile["capacity"] - profile["active_deals"]
                if rep_available > available and any(
                    s.lower() in top_action["description"].lower() for s in profile["strengths"]
                ):
                    best_rep = rep_name
                    best_reason = f"Specialist in {profile['specialty']}, {rep_available} slots available"
                    break

            assignments.append(
                f"| {deal_name} | ${ctx['value']:,} | {top_action['name']} | "
                f"{best_rep} | {best_reason} |\n"
            )

        rows = "".join(assignments)

        # Rep workload summary
        workload_rows = ""
        for rep_name, profile in _REP_PROFILES.items():
            assigned = sum(1 for d in _DEAL_CONTEXT.values() if d["owner"] == rep_name)
            available = profile["capacity"] - profile["active_deals"]
            workload_rows += f"| {rep_name} | {profile['title']} | {assigned} | {available} | {profile['specialty']} |\n"

        return (
            f"**Optimized Rep Assignments**\n\n"
            f"| Deal | Value | Action | Assigned To | Rationale |\n"
            f"|------|-------|--------|------------|----------|\n"
            f"{rows}\n"
            f"**Team Workload:**\n\n"
            f"| Rep | Title | Active Deals | Available Slots | Specialty |\n"
            f"|-----|-------|-------------|----------------|----------|\n"
            f"{workload_rows}\n"
            f"**Optimization Notes:**\n"
            f"- Assignments balance workload with deal-specific expertise\n"
            f"- Cross-assignments recommended when specialist skills needed\n"
            f"- Review assignments weekly in pipeline meeting\n\n"
            f"Source: [Rep Profiles + Workload Data + Skill Matrix]\n"
            f"Agents: AssignmentOptimizer"
        )


if __name__ == "__main__":
    agent = NextBestActionAgent()
    for op in ["recommend_actions", "action_sequence", "impact_forecast", "rep_assignments"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
