"""
Sales Coach Agent

AI-powered sales coaching with call reviews, skill assessments, personalized
coaching plans, and performance dashboards.

Where a real deployment would integrate with call recording and CRM systems,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/sales-coach",
    "version": "1.0.0",
    "display_name": "Sales Coach",
    "description": "AI-powered sales coaching with call reviews, skill assessments, coaching plans, and performance dashboards.",
    "author": "AIBAST",
    "tags": ["sales", "coaching", "training", "performance", "call-review"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_CALL_TRANSCRIPTS = {
    "CALL-901": {
        "id": "CALL-901", "rep": "Alex Rivera", "prospect": "Jennifer Walsh (TechVantage)",
        "date": "2025-11-12", "duration_min": 32, "type": "Discovery",
        "outcome": "Meeting Scheduled", "deal_value": 185000,
        "scores": {"opening": 85, "discovery_questions": 72, "active_listening": 90, "value_articulation": 68, "next_steps": 95, "objection_handling": 60},
        "highlights": ["Strong rapport building in first 3 minutes", "Identified 3 key pain points", "Secured next meeting with VP"],
        "improvements": ["Ask more open-ended discovery questions", "Missed opportunity to quantify business impact", "Did not address competitor mention"],
        "talk_ratio": {"rep": 58, "prospect": 42},
    },
    "CALL-902": {
        "id": "CALL-902", "rep": "Sarah Kim", "prospect": "David Park (Greenridge Partners)",
        "date": "2025-11-11", "duration_min": 45, "type": "Proposal Review",
        "outcome": "Verbal Agreement", "deal_value": 72000,
        "scores": {"opening": 92, "discovery_questions": 88, "active_listening": 85, "value_articulation": 91, "next_steps": 88, "objection_handling": 82},
        "highlights": ["Excellent value quantification with ROI numbers", "Handled pricing objection confidently", "Clear mutual action plan"],
        "improvements": ["Could have involved more stakeholders", "Missed upsell opportunity for Analytics Pro"],
        "talk_ratio": {"rep": 45, "prospect": 55},
    },
    "CALL-903": {
        "id": "CALL-903", "rep": "Tom Rivera", "prospect": "Maria Santos (BlueHorizon Health)",
        "date": "2025-11-10", "duration_min": 28, "type": "Renewal Discussion",
        "outcome": "Expansion Identified", "deal_value": 240000,
        "scores": {"opening": 78, "discovery_questions": 65, "active_listening": 82, "value_articulation": 75, "next_steps": 70, "objection_handling": 55},
        "highlights": ["Customer mentioned expansion plans", "Good understanding of healthcare compliance needs"],
        "improvements": ["Rushed through opening - no personal connection", "Failed to probe deeper on expansion timeline", "Weak close - no specific next meeting date", "Did not handle budget concern effectively"],
        "talk_ratio": {"rep": 65, "prospect": 35},
    },
}

_SCORING_RUBRICS = {
    "opening": {"weight": 0.10, "criteria": ["Warm greeting and rapport", "Agenda setting", "Time confirmation", "Reference to previous interactions"]},
    "discovery_questions": {"weight": 0.25, "criteria": ["Open-ended questions", "Pain point identification", "Budget qualification", "Timeline discovery", "Decision process mapping"]},
    "active_listening": {"weight": 0.15, "criteria": ["Paraphrasing", "Acknowledgment phrases", "Follow-up on responses", "Note-taking signals"]},
    "value_articulation": {"weight": 0.20, "criteria": ["ROI quantification", "Customer-specific benefits", "Competitive differentiation", "Social proof/references"]},
    "next_steps": {"weight": 0.15, "criteria": ["Clear action items", "Mutual commitment", "Timeline specified", "Calendar invite sent"]},
    "objection_handling": {"weight": 0.15, "criteria": ["Acknowledge concern", "Clarifying questions", "Reframe with value", "Proof points", "Trial close after handling"]},
}

_SKILL_ASSESSMENTS = {
    "Alex Rivera": {"overall": 78, "tenure_months": 18, "quota_attainment": 0.92, "scores": {"opening": 85, "discovery": 72, "listening": 90, "value": 68, "closing": 82, "objections": 60}, "trend": "Improving", "rank": 3},
    "Sarah Kim": {"overall": 88, "tenure_months": 36, "quota_attainment": 1.15, "scores": {"opening": 92, "discovery": 88, "listening": 85, "value": 91, "closing": 88, "objections": 82}, "trend": "Consistent", "rank": 1},
    "Tom Rivera": {"overall": 71, "tenure_months": 12, "quota_attainment": 0.78, "scores": {"opening": 78, "discovery": 65, "listening": 82, "value": 75, "closing": 70, "objections": 55}, "trend": "Needs Improvement", "rank": 5},
}

_COACHING_RECOMMENDATIONS = {
    "objection_handling": [
        {"activity": "Role-play: Price Objection Scenarios", "duration": "30 min", "frequency": "2x/week", "resource": "Objection Handling Playbook Ch. 4"},
        {"activity": "Review 5 recorded calls where objections were handled well", "duration": "45 min", "frequency": "1x/week", "resource": "Call Library - Top Performers"},
        {"activity": "Practice the Feel-Felt-Found framework", "duration": "15 min", "frequency": "Daily", "resource": "Sales Methodology Guide"},
    ],
    "discovery_questions": [
        {"activity": "SPIN Selling question practice", "duration": "20 min", "frequency": "Daily", "resource": "SPIN Selling Workbook"},
        {"activity": "Shadow top performer discovery calls", "duration": "60 min", "frequency": "2x/week", "resource": "Peer Coaching Program"},
        {"activity": "Complete BANT qualification checklist review", "duration": "15 min", "frequency": "After each call", "resource": "Qualification Framework"},
    ],
    "value_articulation": [
        {"activity": "Customer ROI case study review", "duration": "30 min", "frequency": "3x/week", "resource": "Customer Success Stories Library"},
        {"activity": "Practice value proposition delivery", "duration": "15 min", "frequency": "Daily", "resource": "Value Prop Toolkit"},
        {"activity": "Create custom ROI calculations for top 5 prospects", "duration": "45 min", "frequency": "1x/week", "resource": "ROI Calculator Tool"},
    ],
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_rep(query):
    if not query:
        return "Alex Rivera"
    q = query.lower().strip()
    for name in _SKILL_ASSESSMENTS:
        if q in name.lower():
            return name
    return "Alex Rivera"


def _weighted_call_score(scores):
    total = 0
    for skill, rubric in _SCORING_RUBRICS.items():
        total += scores.get(skill, 0) * rubric["weight"]
    return round(total)


def _identify_weakest_skills(rep_name, top_n=2):
    assessment = _SKILL_ASSESSMENTS.get(rep_name, {})
    scores = assessment.get("scores", {})
    sorted_skills = sorted(scores.items(), key=lambda x: x[1])
    return sorted_skills[:top_n]


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class SalesCoachAgent(BasicAgent):
    """
    Sales coaching assistant.

    Operations:
        call_review           - review and score a sales call
        skill_assessment      - assess a rep's skill profile
        coaching_plan         - generate a personalized coaching plan
        performance_dashboard - team performance overview
    """

    def __init__(self):
        self.name = "SalesCoachAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "call_review", "skill_assessment",
                            "coaching_plan", "performance_dashboard",
                        ],
                        "description": "The coaching operation to perform",
                    },
                    "rep_name": {
                        "type": "string",
                        "description": "Sales rep name (e.g. 'Alex Rivera')",
                    },
                    "call_id": {
                        "type": "string",
                        "description": "Call ID to review (e.g. 'CALL-901')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "performance_dashboard")
        dispatch = {
            "call_review": self._call_review,
            "skill_assessment": self._skill_assessment,
            "coaching_plan": self._coaching_plan,
            "performance_dashboard": self._performance_dashboard,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── call_review ────────────────────────────────────────────
    def _call_review(self, params):
        call_id = params.get("call_id", "CALL-901")
        call = _CALL_TRANSCRIPTS.get(call_id, list(_CALL_TRANSCRIPTS.values())[0])
        weighted = _weighted_call_score(call["scores"])
        score_rows = "\n".join(f"| {skill.replace('_', ' ').title()} | {score}/100 | {_SCORING_RUBRICS[skill]['weight']:.0%} |" for skill, score in call["scores"].items())
        highlights = "\n".join(f"- {h}" for h in call["highlights"])
        improvements = "\n".join(f"- {i}" for i in call["improvements"])
        return (
            f"**Call Review: {call['id']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Rep | {call['rep']} |\n"
            f"| Prospect | {call['prospect']} |\n"
            f"| Date | {call['date']} |\n"
            f"| Duration | {call['duration_min']} min |\n"
            f"| Type | {call['type']} |\n"
            f"| Outcome | {call['outcome']} |\n"
            f"| **Overall Score** | **{weighted}/100** |\n\n"
            f"**Skill Scores:**\n\n"
            f"| Skill | Score | Weight |\n|---|---|---|\n"
            f"{score_rows}\n\n"
            f"**Talk Ratio:** Rep {call['talk_ratio']['rep']}% / Prospect {call['talk_ratio']['prospect']}%\n\n"
            f"**Highlights:**\n{highlights}\n\n"
            f"**Areas for Improvement:**\n{improvements}\n\n"
            f"Source: [Call Recording + AI Analysis]\nAgents: SalesCoachAgent"
        )

    # ── skill_assessment ───────────────────────────────────────
    def _skill_assessment(self, params):
        rep_name = _resolve_rep(params.get("rep_name", ""))
        assessment = _SKILL_ASSESSMENTS[rep_name]
        score_rows = "\n".join(f"| {skill.title()} | {score}/100 |" for skill, score in assessment["scores"].items())
        weakest = _identify_weakest_skills(rep_name)
        weak_list = "\n".join(f"- {skill.title()}: {score}/100" for skill, score in weakest)
        return (
            f"**Skill Assessment: {rep_name}**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Overall Score | {assessment['overall']}/100 |\n"
            f"| Tenure | {assessment['tenure_months']} months |\n"
            f"| Quota Attainment | {assessment['quota_attainment']:.0%} |\n"
            f"| Trend | {assessment['trend']} |\n"
            f"| Team Rank | #{assessment['rank']} |\n\n"
            f"**Skill Breakdown:**\n\n| Skill | Score |\n|---|---|\n{score_rows}\n\n"
            f"**Focus Areas (weakest skills):**\n{weak_list}\n\n"
            f"Source: [Coaching Platform + CRM]\nAgents: SalesCoachAgent"
        )

    # ── coaching_plan ──────────────────────────────────────────
    def _coaching_plan(self, params):
        rep_name = _resolve_rep(params.get("rep_name", ""))
        weakest = _identify_weakest_skills(rep_name)
        plan = ""
        for skill, score in weakest:
            recs = _COACHING_RECOMMENDATIONS.get(skill, _COACHING_RECOMMENDATIONS.get("objection_handling", []))
            plan += f"**{skill.replace('_', ' ').title()}** (Current: {score}/100)\n\n"
            for rec in recs:
                plan += f"- {rec['activity']} ({rec['duration']}, {rec['frequency']})\n  Resource: {rec['resource']}\n"
            plan += "\n"
        return (
            f"**Coaching Plan: {rep_name}**\n\n"
            f"**Assessment:** {_SKILL_ASSESSMENTS[rep_name]['overall']}/100 overall\n"
            f"**Goal:** Improve weakest skills by 15+ points in 30 days\n\n"
            f"{plan}"
            f"**Timeline:** 4-week program with weekly check-ins\n"
            f"**Success Metrics:** Skill score improvement, call conversion rate, quota attainment\n\n"
            f"Source: [Coaching Platform]\nAgents: SalesCoachAgent"
        )

    # ── performance_dashboard ──────────────────────────────────
    def _performance_dashboard(self, params):
        rows = ""
        for name, a in sorted(_SKILL_ASSESSMENTS.items(), key=lambda x: x[1]["overall"], reverse=True):
            rows += f"| {name} | {a['overall']}/100 | {a['quota_attainment']:.0%} | {a['trend']} | #{a['rank']} |\n"
        team_avg = sum(a["overall"] for a in _SKILL_ASSESSMENTS.values()) / len(_SKILL_ASSESSMENTS)
        team_quota = sum(a["quota_attainment"] for a in _SKILL_ASSESSMENTS.values()) / len(_SKILL_ASSESSMENTS)
        return (
            f"**Sales Performance Dashboard**\n\n"
            f"**Team Summary:**\n"
            f"- Team Size: {len(_SKILL_ASSESSMENTS)}\n"
            f"- Avg Score: {team_avg:.0f}/100\n"
            f"- Avg Quota Attainment: {team_quota:.0%}\n"
            f"- Calls Reviewed: {len(_CALL_TRANSCRIPTS)}\n\n"
            f"**Individual Performance:**\n\n"
            f"| Rep | Score | Quota | Trend | Rank |\n|---|---|---|---|---|\n"
            f"{rows}\n\n"
            f"Source: [Coaching Platform + CRM + Call Analytics]\nAgents: SalesCoachAgent"
        )


if __name__ == "__main__":
    agent = SalesCoachAgent()
    for op in ["call_review", "skill_assessment", "coaching_plan", "performance_dashboard"]:
        print("=" * 60)
        print(agent.perform(operation=op, rep_name="Alex Rivera", call_id="CALL-901"))
        print()
