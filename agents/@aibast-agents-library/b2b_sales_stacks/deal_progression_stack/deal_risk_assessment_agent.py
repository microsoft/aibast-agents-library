"""
Deal Risk Assessment Agent

Assesses risk across active pipeline deals using multi-factor scoring,
generates risk matrices for portfolio-level visibility, creates mitigation
plans with actionable steps, and tracks risk trends over time. Helps sales
leadership proactively manage deal risk before it leads to slippage.

Where a real deployment would call Salesforce, Clari, Gong, etc., this
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
    "name": "@aibast-agents-library/deal-risk-assessment",
    "version": "1.0.0",
    "display_name": "Deal Risk Assessment",
    "description": "Multi-factor risk scoring, risk matrices, mitigation planning, and risk trend tracking for pipeline deals.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "risk-assessment", "deal-progression", "pipeline"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ===================================================================
# SYNTHETIC DATA LAYER
# ===================================================================

_RISK_FACTORS = {
    "TechCorp Industries": {
        "deal_id": "OPP-001", "value": 890000, "stage": "Proposal", "owner": "Mike Chen",
        "factors": {
            "champion_risk": {"score": 85, "detail": "Champion silent for 18 days, new VP joined org"},
            "budget_risk": {"score": 40, "detail": "Budget approved in Q3 planning, still allocated"},
            "timeline_risk": {"score": 65, "detail": "34 days in Proposal, 2.1x benchmark"},
            "competitive_risk": {"score": 70, "detail": "Nextera Platform in active evaluation"},
            "technical_risk": {"score": 30, "detail": "POC completed successfully, positive feedback"},
            "decision_risk": {"score": 75, "detail": "Executive change, new decision maker not engaged"},
        },
    },
    "Global Manufacturing": {
        "deal_id": "OPP-002", "value": 720000, "stage": "Negotiation", "owner": "Lisa Torres",
        "factors": {
            "champion_risk": {"score": 25, "detail": "Champion active and frustrated with legal delays"},
            "budget_risk": {"score": 35, "detail": "Budget confirmed, procurement process slow"},
            "timeline_risk": {"score": 70, "detail": "28 days in Negotiation, 2.3x benchmark"},
            "competitive_risk": {"score": 45, "detail": "Vendara offering 25% discount, we lead on features"},
            "technical_risk": {"score": 15, "detail": "Technical validation complete, no concerns"},
            "decision_risk": {"score": 50, "detail": "Legal review creating bottleneck, not relationship issue"},
        },
    },
    "Apex Financial": {
        "deal_id": "OPP-003", "value": 580000, "stage": "Discovery", "owner": "James Park",
        "factors": {
            "champion_risk": {"score": 90, "detail": "CTO disengaged, no response in 12 days"},
            "budget_risk": {"score": 60, "detail": "Budget not yet allocated, fiscal year change pending"},
            "timeline_risk": {"score": 55, "detail": "25 days in Discovery, 1.4x benchmark"},
            "competitive_risk": {"score": 80, "detail": "Three competitors in evaluation, RFP coming"},
            "technical_risk": {"score": 45, "detail": "Security compliance concerns in financial services"},
            "decision_risk": {"score": 70, "detail": "No executive sponsor, buying committee not mapped"},
        },
    },
    "Metro Healthcare": {
        "deal_id": "OPP-004", "value": 440000, "stage": "Proposal", "owner": "Mike Chen",
        "factors": {
            "champion_risk": {"score": 20, "detail": "VP Digital actively championing internally"},
            "budget_risk": {"score": 65, "detail": "Budget on hold pending board approval next month"},
            "timeline_risk": {"score": 50, "detail": "22 days in Proposal, 1.4x benchmark"},
            "competitive_risk": {"score": 30, "detail": "Nextera struggling with HIPAA requirements"},
            "technical_risk": {"score": 35, "detail": "HIPAA compliance validated, minor integration work"},
            "decision_risk": {"score": 40, "detail": "Decision maker identified and engaged"},
        },
    },
    "Pacific Telecom": {
        "deal_id": "OPP-013", "value": 780000, "stage": "Negotiation", "owner": "Lisa Torres",
        "factors": {
            "champion_risk": {"score": 10, "detail": "SVP Ops strong advocate, weekly check-ins"},
            "budget_risk": {"score": 20, "detail": "Budget approved, PO in procurement queue"},
            "timeline_risk": {"score": 35, "detail": "14 days in Negotiation, 1.2x benchmark"},
            "competitive_risk": {"score": 15, "detail": "CloudFirst eliminated in technical evaluation"},
            "technical_risk": {"score": 10, "detail": "Full technical sign-off obtained"},
            "decision_risk": {"score": 25, "detail": "Procurement process standard, no blockers"},
        },
    },
    "Pinnacle Logistics": {
        "deal_id": "OPP-005", "value": 360000, "stage": "Qualification", "owner": "James Park",
        "factors": {
            "champion_risk": {"score": 80, "detail": "IT Director silent, no internal advocate found"},
            "budget_risk": {"score": 70, "detail": "No budget discussion, unclear funding source"},
            "timeline_risk": {"score": 60, "detail": "20 days in Qualification, 1.4x benchmark"},
            "competitive_risk": {"score": 40, "detail": "No known competitors, but early stage"},
            "technical_risk": {"score": 50, "detail": "Requirements not fully scoped"},
            "decision_risk": {"score": 85, "detail": "No champion, no exec sponsor, single contact only"},
        },
    },
}

_RISK_HISTORY = {
    "TechCorp Industries": [52, 55, 60, 64, 68, 72],
    "Global Manufacturing": [30, 32, 35, 38, 42, 44],
    "Apex Financial": [40, 48, 55, 60, 65, 70],
    "Metro Healthcare": [35, 33, 36, 38, 40, 42],
    "Pacific Telecom": [28, 25, 22, 20, 18, 16],
    "Pinnacle Logistics": [50, 55, 58, 62, 65, 68],
}

_MITIGATION_PLAYBOOKS = {
    "champion_risk": {
        "high": [
            "Immediately identify 3 alternative champion candidates in org chart",
            "Multi-thread outreach via LinkedIn, email, and mutual connections",
            "Offer executive briefing or value workshop to create new relationships",
            "Escalate to your VP for peer-level executive outreach",
        ],
        "medium": [
            "Schedule regular weekly touchpoints with current champion",
            "Identify backup champion as insurance",
            "Share exclusive industry insights to maintain engagement",
        ],
    },
    "budget_risk": {
        "high": [
            "Build CFO-ready business case with 3-year TCO and ROI",
            "Offer phased implementation to reduce upfront commitment",
            "Provide flexible payment terms or subscription model",
            "Connect champion with finance team for internal advocacy",
        ],
        "medium": [
            "Confirm budget cycle timing and approval process",
            "Share peer company ROI case studies",
            "Offer bridge pricing or pilot to maintain momentum",
        ],
    },
    "competitive_risk": {
        "high": [
            "Prepare head-to-head comparison with proof points",
            "Arrange customer reference calls in same vertical",
            "Offer differentiated proof-of-value engagement",
            "Accelerate timeline to reduce evaluation window",
        ],
        "medium": [
            "Monitor competitive activity through champion",
            "Reinforce key differentiators in all communications",
            "Share competitive battle card with internal stakeholders",
        ],
    },
    "decision_risk": {
        "high": [
            "Map complete buying committee and decision process",
            "Secure executive sponsor meeting within 5 business days",
            "Provide decision framework to champion for internal use",
            "Identify and address individual stakeholder concerns",
        ],
        "medium": [
            "Validate decision criteria and timeline with champion",
            "Ensure all decision makers have received value messaging",
            "Schedule group demo or workshop for buying committee",
        ],
    },
    "timeline_risk": {
        "high": [
            "Reset mutual action plan with new target dates",
            "Identify and address specific bottleneck causing delays",
            "Offer implementation accelerators or quick-start packages",
            "Escalate internally for resource prioritization",
        ],
        "medium": [
            "Review and update mutual action plan timeline",
            "Schedule weekly progress checkpoints",
            "Pre-stage next-step resources to remove friction",
        ],
    },
    "technical_risk": {
        "high": [
            "Schedule technical deep-dive with solutions architect",
            "Provide security and compliance documentation proactively",
            "Offer extended POC or pilot to address concerns",
            "Connect prospect technical team with engineering leadership",
        ],
        "medium": [
            "Share technical documentation and architecture overview",
            "Address open technical questions in writing",
            "Offer technical office hours for prospect IT team",
        ],
    },
}


# ===================================================================
# HELPERS
# ===================================================================

def _composite_risk(deal_name):
    """Calculate weighted composite risk score."""
    factors = _RISK_FACTORS.get(deal_name, {}).get("factors", {})
    weights = {
        "champion_risk": 0.25, "budget_risk": 0.15, "timeline_risk": 0.15,
        "competitive_risk": 0.20, "technical_risk": 0.10, "decision_risk": 0.15,
    }
    total = sum(factors.get(f, {}).get("score", 0) * w for f, w in weights.items())
    return round(total)


def _severity_label(score):
    """Classify risk severity."""
    if score >= 70:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 30:
        return "MODERATE"
    return "LOW"


# ===================================================================
# AGENT CLASS
# ===================================================================

class DealRiskAssessmentAgent(BasicAgent):
    """
    Assesses and manages deal risk across the pipeline.

    Operations:
        assess_risks     - multi-factor risk assessment per deal
        risk_matrix      - portfolio-level risk matrix
        mitigation_plan  - actionable mitigation steps per deal
        risk_trend       - risk score trends over time
    """

    def __init__(self):
        self.name = "DealRiskAssessmentAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["assess_risks", "risk_matrix", "mitigation_plan", "risk_trend"],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "assess_risks")
        dispatch = {
            "assess_risks": self._assess_risks,
            "risk_matrix": self._risk_matrix,
            "mitigation_plan": self._mitigation_plan,
            "risk_trend": self._risk_trend,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation '{op}'. Valid: {', '.join(dispatch.keys())}"
        return handler()

    # -- assess_risks --------------------------------------------------
    def _assess_risks(self) -> str:
        sections = []
        for deal_name in sorted(_RISK_FACTORS.keys(), key=lambda d: -_composite_risk(d)):
            deal = _RISK_FACTORS[deal_name]
            composite = _composite_risk(deal_name)
            severity = _severity_label(composite)

            factor_rows = ""
            for fname, fdata in sorted(deal["factors"].items(), key=lambda x: -x[1]["score"]):
                label = fname.replace("_", " ").title()
                fsev = _severity_label(fdata["score"])
                factor_rows += f"| {label} | {fdata['score']}/100 | {fsev} | {fdata['detail']} |\n"

            sections.append(
                f"**{deal_name} -- ${deal['value']:,} ({deal['stage']})**\n"
                f"Composite Risk: **{composite}/100 [{severity}]** | Owner: {deal['owner']}\n\n"
                f"| Factor | Score | Level | Detail |\n"
                f"|--------|-------|-------|--------|\n"
                f"{factor_rows}"
            )

        total_value = sum(d["value"] for d in _RISK_FACTORS.values())
        critical_value = sum(d["value"] for dn, d in _RISK_FACTORS.items() if _composite_risk(dn) >= 70)

        return (
            f"**Deal Risk Assessment -- {len(_RISK_FACTORS)} Deals**\n\n"
            f"Total pipeline: ${total_value:,} | Critical risk exposure: ${critical_value:,}\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\nSource: [CRM + Activity Analytics + Gong Signals]\n"
            f"Agents: RiskScoringEngine, DealAnalyticsAgent"
        )

    # -- risk_matrix ---------------------------------------------------
    def _risk_matrix(self) -> str:
        deals_by_quadrant = {"high_value_high_risk": [], "high_value_low_risk": [],
                             "low_value_high_risk": [], "low_value_low_risk": []}
        value_threshold = 500000
        risk_threshold = 50

        for deal_name, deal in _RISK_FACTORS.items():
            composite = _composite_risk(deal_name)
            high_val = deal["value"] >= value_threshold
            high_risk = composite >= risk_threshold

            if high_val and high_risk:
                deals_by_quadrant["high_value_high_risk"].append((deal_name, deal, composite))
            elif high_val:
                deals_by_quadrant["high_value_low_risk"].append((deal_name, deal, composite))
            elif high_risk:
                deals_by_quadrant["low_value_high_risk"].append((deal_name, deal, composite))
            else:
                deals_by_quadrant["low_value_low_risk"].append((deal_name, deal, composite))

        def format_quadrant(items):
            if not items:
                return "  None\n"
            return "".join(f"  - {n}: ${d['value']:,} (risk: {r}/100)\n" for n, d, r in items)

        return (
            f"**Risk Matrix -- Pipeline Portfolio View**\n\n"
            f"Value threshold: ${value_threshold:,} | Risk threshold: {risk_threshold}/100\n\n"
            f"**Quadrant 1: High Value + High Risk (IMMEDIATE ACTION)**\n"
            f"{format_quadrant(deals_by_quadrant['high_value_high_risk'])}\n"
            f"**Quadrant 2: High Value + Low Risk (PROTECT & ACCELERATE)**\n"
            f"{format_quadrant(deals_by_quadrant['high_value_low_risk'])}\n"
            f"**Quadrant 3: Low Value + High Risk (EVALUATE ROI OF EFFORT)**\n"
            f"{format_quadrant(deals_by_quadrant['low_value_high_risk'])}\n"
            f"**Quadrant 4: Low Value + Low Risk (MONITOR)**\n"
            f"{format_quadrant(deals_by_quadrant['low_value_low_risk'])}\n"
            f"**Recommendation:** Focus 70% of leadership attention on Quadrant 1 deals. "
            f"Quadrant 2 deals need acceleration, not intervention.\n\n"
            f"Source: [Risk Scoring + Pipeline Data]\n"
            f"Agents: PortfolioRiskAgent"
        )

    # -- mitigation_plan -----------------------------------------------
    def _mitigation_plan(self) -> str:
        sections = []
        for deal_name in sorted(_RISK_FACTORS.keys(), key=lambda d: -_composite_risk(d)):
            deal = _RISK_FACTORS[deal_name]
            composite = _composite_risk(deal_name)
            if composite < 40:
                continue

            top_risks = sorted(deal["factors"].items(), key=lambda x: -x[1]["score"])[:3]
            risk_plans = []
            for fname, fdata in top_risks:
                level = "high" if fdata["score"] >= 60 else "medium"
                playbook = _MITIGATION_PLAYBOOKS.get(fname, {}).get(level, [])
                if playbook:
                    steps = "\n".join(f"    {i}. {s}" for i, s in enumerate(playbook, 1))
                    label = fname.replace("_", " ").title()
                    risk_plans.append(f"  **{label}** (Score: {fdata['score']}):\n{steps}")

            sections.append(
                f"**{deal_name} -- ${deal['value']:,} (Risk: {composite}/100)**\n"
                f"Owner: {deal['owner']} | Stage: {deal['stage']}\n\n"
                + "\n\n".join(risk_plans)
            )

        return (
            f"**Mitigation Plans -- High-Risk Deals**\n\n"
            f"Plans generated for deals with composite risk >= 40.\n\n"
            + "\n\n---\n\n".join(sections)
            + f"\n\n**Execution Timeline:** All critical mitigations should begin within 48 hours. "
            f"Review progress in weekly pipeline meeting.\n\n"
            f"Source: [Risk Playbook + Best Practices]\n"
            f"Agents: MitigationPlannerAgent"
        )

    # -- risk_trend ----------------------------------------------------
    def _risk_trend(self) -> str:
        sections = []
        for deal_name in sorted(_RISK_FACTORS.keys(), key=lambda d: -_RISK_FACTORS[d]["value"]):
            history = _RISK_HISTORY.get(deal_name, [])
            if not history:
                continue
            current = history[-1]
            start = history[0]
            delta = current - start
            direction = "WORSENING" if delta > 5 else ("IMPROVING" if delta < -5 else "STABLE")

            trend_line = " -> ".join(f"{s}" for s in history)

            sections.append(
                f"**{deal_name} -- ${_RISK_FACTORS[deal_name]['value']:,}**\n"
                f"Direction: {direction} | Current: {current}/100 | 6-week change: {delta:+d}\n"
                f"Trend: {trend_line}\n"
            )

        worsening = sum(1 for h in _RISK_HISTORY.values() if h and h[-1] - h[0] > 5)
        improving = sum(1 for h in _RISK_HISTORY.values() if h and h[-1] - h[0] < -5)

        return (
            f"**Risk Trend Analysis -- 6-Week View**\n\n"
            f"Worsening: {worsening} | Improving: {improving} | "
            f"Stable: {len(_RISK_HISTORY) - worsening - improving}\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\n**Alert:** Deals with worsening risk trends require immediate pipeline review.\n\n"
            f"Source: [Historical Risk Scores]\n"
            f"Agents: RiskTrendEngine"
        )


if __name__ == "__main__":
    agent = DealRiskAssessmentAgent()
    for op in ["assess_risks", "risk_matrix", "mitigation_plan", "risk_trend"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
