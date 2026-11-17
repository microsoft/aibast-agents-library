"""
Account Risk Assessment Agent

Evaluates deal risk, churn probability, financial health, and generates
executive risk summaries for enterprise B2B accounts. Combines CRM signals,
financial indicators, and engagement data to produce actionable risk
mitigation recommendations.

Where a real deployment would call risk scoring APIs and financial data
providers, this agent uses a synthetic data layer so it runs anywhere
without credentials.
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
    "name": "@aibast-agents-library/account-risk-assessment",
    "version": "1.0.0",
    "display_name": "Account Risk Assessment",
    "description": "Assesses deal risk, churn probability, and financial health with mitigation recommendations.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "risk-assessment", "churn-prediction", "deal-risk"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_ACCOUNTS = {
    "acme": {
        "id": "acc-001", "name": "Acme Corporation", "industry": "Manufacturing",
        "revenue": 2_800_000_000, "employees": 12_400,
        "current_spend": 1_200_000, "opportunity_value": 2_400_000,
        "contract_renewal": "8 months", "deal_stage": "Proposal",
        "days_in_stage": 34, "expected_close_days": 21,
    },
    "contoso": {
        "id": "acc-002", "name": "Contoso Ltd", "industry": "Technology",
        "revenue": 980_000_000, "employees": 4_200,
        "current_spend": 680_000, "opportunity_value": 1_100_000,
        "contract_renewal": "3 months", "deal_stage": "Negotiation",
        "days_in_stage": 12, "expected_close_days": 30,
    },
    "fabrikam": {
        "id": "acc-003", "name": "Fabrikam Industries", "industry": "Manufacturing",
        "revenue": 1_500_000_000, "employees": 8_700,
        "current_spend": 450_000, "opportunity_value": 890_000,
        "contract_renewal": "14 months", "deal_stage": "Discovery",
        "days_in_stage": 18, "expected_close_days": 90,
    },
    "northwind": {
        "id": "acc-004", "name": "Northwind Traders", "industry": "Retail",
        "revenue": 620_000_000, "employees": 3_100,
        "current_spend": 220_000, "opportunity_value": 540_000,
        "contract_renewal": None, "deal_stage": "Qualification",
        "days_in_stage": 7, "expected_close_days": 120,
    },
}

_RISK_FACTORS = {
    "acme": [
        {"factor": "No CTO relationship", "category": "Stakeholder", "severity": "High", "weight": 0.25, "score": 82},
        {"factor": "Competitor pricing pressure (-15%)", "category": "Competitive", "severity": "High", "weight": 0.20, "score": 75},
        {"factor": "CFO requires ROI validation", "category": "Financial", "severity": "Medium", "weight": 0.15, "score": 60},
        {"factor": "Days in stage above average", "category": "Velocity", "severity": "Medium", "weight": 0.15, "score": 55},
        {"factor": "New CTO unknown sentiment", "category": "Stakeholder", "severity": "Medium", "weight": 0.10, "score": 50},
        {"factor": "Competitor RFP issued", "category": "Competitive", "severity": "Low", "weight": 0.10, "score": 40},
        {"factor": "Champion strongly engaged", "category": "Stakeholder", "severity": "Low", "weight": 0.05, "score": 15},
    ],
    "contoso": [
        {"factor": "Contract renewal in 3 months", "category": "Timeline", "severity": "High", "weight": 0.30, "score": 78},
        {"factor": "CFO budget cautious", "category": "Financial", "severity": "Medium", "weight": 0.20, "score": 55},
        {"factor": "Incumbent competitor on analytics", "category": "Competitive", "severity": "Medium", "weight": 0.20, "score": 52},
        {"factor": "Strong CTO advocacy", "category": "Stakeholder", "severity": "Low", "weight": 0.15, "score": 18},
        {"factor": "Series D funding (budget available)", "category": "Financial", "severity": "Low", "weight": 0.15, "score": 12},
    ],
    "fabrikam": [
        {"factor": "Early stage discovery", "category": "Velocity", "severity": "Medium", "weight": 0.25, "score": 45},
        {"factor": "New VP IT decision maker", "category": "Stakeholder", "severity": "Medium", "weight": 0.25, "score": 50},
        {"factor": "Low-cost competitor proposal", "category": "Competitive", "severity": "Medium", "weight": 0.20, "score": 55},
        {"factor": "COO champion engaged", "category": "Stakeholder", "severity": "Low", "weight": 0.15, "score": 20},
        {"factor": "Long renewal runway (14 months)", "category": "Timeline", "severity": "Low", "weight": 0.15, "score": 15},
    ],
    "northwind": [
        {"factor": "No existing relationship", "category": "Stakeholder", "severity": "High", "weight": 0.30, "score": 85},
        {"factor": "No products owned", "category": "Adoption", "severity": "High", "weight": 0.25, "score": 80},
        {"factor": "Only 1 discovery call", "category": "Velocity", "severity": "Medium", "weight": 0.20, "score": 60},
        {"factor": "CTO sentiment unknown", "category": "Stakeholder", "severity": "Medium", "weight": 0.15, "score": 55},
        {"factor": "E-commerce launch (budget available)", "category": "Financial", "severity": "Low", "weight": 0.10, "score": 20},
    ],
}

_CHURN_INDICATORS = {
    "acme": {
        "product_usage_trend": "stable", "support_tickets_30d": 3,
        "nps_score": 42, "login_frequency": "daily",
        "feature_adoption_pct": 67, "executive_sponsor_engaged": False,
        "last_qbr_days_ago": 45, "open_support_escalations": 0,
        "historical_churn_rate_industry": 0.12,
    },
    "contoso": {
        "product_usage_trend": "increasing", "support_tickets_30d": 1,
        "nps_score": 58, "login_frequency": "daily",
        "feature_adoption_pct": 52, "executive_sponsor_engaged": True,
        "last_qbr_days_ago": 20, "open_support_escalations": 0,
        "historical_churn_rate_industry": 0.18,
    },
    "fabrikam": {
        "product_usage_trend": "declining", "support_tickets_30d": 7,
        "nps_score": 28, "login_frequency": "weekly",
        "feature_adoption_pct": 34, "executive_sponsor_engaged": False,
        "last_qbr_days_ago": 90, "open_support_escalations": 2,
        "historical_churn_rate_industry": 0.12,
    },
    "northwind": {
        "product_usage_trend": "none", "support_tickets_30d": 0,
        "nps_score": None, "login_frequency": "none",
        "feature_adoption_pct": 0, "executive_sponsor_engaged": False,
        "last_qbr_days_ago": None, "open_support_escalations": 0,
        "historical_churn_rate_industry": 0.15,
    },
}

_FINANCIAL_HEALTH = {
    "acme": {
        "credit_rating": "A", "revenue_growth_yoy": 0.08,
        "debt_to_equity": 0.42, "operating_margin": 0.14,
        "cash_reserves_months": 18, "recent_layoffs": False,
        "budget_cycle": "Q1 (January)", "fiscal_year_end": "December",
        "it_budget_pct_revenue": 0.038,
    },
    "contoso": {
        "credit_rating": "BBB+", "revenue_growth_yoy": 0.22,
        "debt_to_equity": 0.65, "operating_margin": 0.09,
        "cash_reserves_months": 24, "recent_layoffs": False,
        "budget_cycle": "Q1 (January)", "fiscal_year_end": "December",
        "it_budget_pct_revenue": 0.062,
    },
    "fabrikam": {
        "credit_rating": "A-", "revenue_growth_yoy": 0.18,
        "debt_to_equity": 0.35, "operating_margin": 0.16,
        "cash_reserves_months": 14, "recent_layoffs": False,
        "budget_cycle": "Q4 (October)", "fiscal_year_end": "September",
        "it_budget_pct_revenue": 0.029,
    },
    "northwind": {
        "credit_rating": "BB+", "revenue_growth_yoy": 0.05,
        "debt_to_equity": 0.78, "operating_margin": 0.06,
        "cash_reserves_months": 9, "recent_layoffs": True,
        "budget_cycle": "Q1 (January)", "fiscal_year_end": "December",
        "it_budget_pct_revenue": 0.041,
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_account(query):
    if not query:
        return "acme"
    q = query.lower().strip()
    for key in _ACCOUNTS:
        if key in q or q in _ACCOUNTS[key]["name"].lower():
            return key
    return "acme"


def _composite_risk_score(key):
    """Weighted risk score from all factors."""
    factors = _RISK_FACTORS.get(key, [])
    if not factors:
        return 50
    return int(sum(f["score"] * f["weight"] for f in factors))


def _win_probability(key):
    """Derive win probability from risk score."""
    risk = _composite_risk_score(key)
    return max(10, min(95, 100 - risk))


def _churn_probability(key):
    """Compute churn probability from indicators."""
    ind = _CHURN_INDICATORS.get(key, {})
    if not ind or ind["product_usage_trend"] == "none":
        return None

    base = ind["historical_churn_rate_industry"]
    usage_mod = {"increasing": -0.05, "stable": 0.0, "declining": 0.10, "none": 0.20}
    score = base + usage_mod.get(ind["product_usage_trend"], 0)

    if ind["nps_score"] and ind["nps_score"] < 30:
        score += 0.08
    if ind["open_support_escalations"] > 0:
        score += 0.05 * ind["open_support_escalations"]
    if ind["last_qbr_days_ago"] and ind["last_qbr_days_ago"] > 60:
        score += 0.04
    if ind["executive_sponsor_engaged"]:
        score -= 0.06
    if ind["feature_adoption_pct"] >= 60:
        score -= 0.04

    return max(0.02, min(0.85, round(score, 2)))


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class RiskAssessmentAgent(BasicAgent):
    """
    Evaluates deal and account risk across multiple dimensions.

    Operations:
        assess_deal_risk  - comprehensive deal risk analysis
        churn_prediction  - churn probability with contributing factors
        financial_risk    - financial health assessment
        executive_summary - consolidated risk executive summary
    """

    def __init__(self):
        self.name = "RiskAssessmentAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "assess_deal_risk", "churn_prediction",
                            "financial_risk", "executive_summary",
                        ],
                        "description": "The risk assessment to perform",
                    },
                    "account_name": {
                        "type": "string",
                        "description": "Account name (e.g. 'Acme Corporation')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "assess_deal_risk")
        key = _resolve_account(kwargs.get("account_name", ""))
        dispatch = {
            "assess_deal_risk": self._assess_deal_risk,
            "churn_prediction": self._churn_prediction,
            "financial_risk": self._financial_risk,
            "executive_summary": self._executive_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    # ── assess_deal_risk ──────────────────────────────────────
    def _assess_deal_risk(self, key):
        acct = _ACCOUNTS[key]
        factors = _RISK_FACTORS.get(key, [])
        risk_score = _composite_risk_score(key)
        win_prob = _win_probability(key)

        factor_rows = ""
        for f in factors:
            factor_rows += f"| {f['factor']} | {f['category']} | {f['severity']} | {f['score']}/100 |\n"

        high_risks = [f for f in factors if f["severity"] == "High"]
        mitigations = ""
        if high_risks:
            mitigations = "\n**Immediate Mitigations Required:**\n"
            for i, r in enumerate(high_risks, 1):
                if r["category"] == "Stakeholder":
                    mitigations += f"{i}. Schedule champion intro to close stakeholder gap\n"
                elif r["category"] == "Competitive":
                    mitigations += f"{i}. Prepare TCO analysis countering competitor pricing\n"
                elif r["category"] == "Financial":
                    mitigations += f"{i}. Deliver customized ROI calculator to economic buyer\n"
                elif r["category"] == "Adoption":
                    mitigations += f"{i}. Offer pilot program to demonstrate value\n"
                else:
                    mitigations += f"{i}. Address: {r['factor']}\n"

        return (
            f"**Deal Risk Assessment: {acct['name']}**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Deal Stage | {acct['deal_stage']} |\n"
            f"| Days in Stage | {acct['days_in_stage']} |\n"
            f"| Opportunity Value | ${acct['opportunity_value']:,} |\n"
            f"| Composite Risk Score | {risk_score}/100 |\n"
            f"| Win Probability | {win_prob}% |\n"
            f"| Expected Close | {acct['expected_close_days']} days |\n\n"
            f"**Risk Factors:**\n\n"
            f"| Factor | Category | Severity | Score |\n|---|---|---|---|\n"
            f"{factor_rows}"
            f"{mitigations}\n"
            f"Source: [Deal Analytics + Risk Models + CRM]\n"
            f"Agents: RiskAssessmentAgent"
        )

    # ── churn_prediction ──────────────────────────────────────
    def _churn_prediction(self, key):
        acct = _ACCOUNTS[key]
        ind = _CHURN_INDICATORS.get(key, {})
        churn_prob = _churn_probability(key)

        if churn_prob is None:
            return (
                f"**Churn Prediction: {acct['name']}**\n\n"
                f"No product usage data available — this is a prospect account.\n"
                f"Churn prediction requires active product usage.\n\n"
                f"Source: [Product Analytics]\nAgents: RiskAssessmentAgent"
            )

        risk_level = "Critical" if churn_prob >= 0.30 else "Elevated" if churn_prob >= 0.15 else "Low"

        indicator_rows = (
            f"| Usage Trend | {ind['product_usage_trend'].title()} |\n"
            f"| Support Tickets (30d) | {ind['support_tickets_30d']} |\n"
            f"| NPS Score | {ind['nps_score']} |\n"
            f"| Login Frequency | {ind['login_frequency'].title()} |\n"
            f"| Feature Adoption | {ind['feature_adoption_pct']}% |\n"
            f"| Executive Sponsor Engaged | {'Yes' if ind['executive_sponsor_engaged'] else 'No'} |\n"
            f"| Last QBR | {ind['last_qbr_days_ago']} days ago |\n"
            f"| Open Escalations | {ind['open_support_escalations']} |\n"
            f"| Industry Churn Rate | {ind['historical_churn_rate_industry']:.0%} |\n"
        )

        actions = ""
        if churn_prob >= 0.20:
            actions = (
                "\n**Retention Actions:**\n"
                "1. Schedule executive business review within 2 weeks\n"
                "2. Assign dedicated CSM for high-touch engagement\n"
                "3. Deliver product adoption workshop\n"
                "4. Address open support escalations immediately\n"
            )
        elif churn_prob >= 0.10:
            actions = (
                "\n**Proactive Measures:**\n"
                "1. Schedule quarterly business review\n"
                "2. Share product roadmap preview\n"
                "3. Introduce executive sponsor program\n"
            )

        return (
            f"**Churn Prediction: {acct['name']}**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Churn Probability | {churn_prob:.0%} |\n"
            f"| Risk Level | {risk_level} |\n"
            f"| Current Spend | ${acct['current_spend']:,}/yr |\n"
            f"| Revenue at Risk | ${int(acct['current_spend'] * churn_prob):,} |\n"
            f"| Contract Renewal | {acct['contract_renewal'] or 'N/A'} |\n\n"
            f"**Contributing Indicators:**\n\n"
            f"| Indicator | Value |\n|---|---|\n"
            f"{indicator_rows}"
            f"{actions}\n"
            f"Source: [Product Analytics + Support + NPS]\n"
            f"Agents: RiskAssessmentAgent"
        )

    # ── financial_risk ────────────────────────────────────────
    def _financial_risk(self, key):
        acct = _ACCOUNTS[key]
        fin = _FINANCIAL_HEALTH.get(key, {})

        if fin["credit_rating"].startswith("A"):
            fin_risk = "Low"
        elif fin["credit_rating"].startswith("B") and "+" in fin["credit_rating"]:
            fin_risk = "Moderate"
        else:
            fin_risk = "Elevated"

        it_budget = int(acct["revenue"] * fin["it_budget_pct_revenue"])
        deal_pct_it_budget = acct["opportunity_value"] / max(it_budget, 1) * 100

        implications = ""
        if fin_risk == "Low":
            implications = (
                "- Strong financial position supports deal progression\n"
                "- Low debt and positive growth indicate budget availability\n"
            )
        elif fin_risk == "Moderate":
            implications = (
                "- Moderate financial caution recommended\n"
                "- Consider phased implementation to manage budget impact\n"
            )
        else:
            implications = (
                "- Elevated risk: validate budget approval path\n"
                "- Recommend smaller pilot to reduce buyer risk\n"
                "- Recent layoffs may signal budget tightening\n"
            )

        return (
            f"**Financial Risk Assessment: {acct['name']}**\n\n"
            f"**Company Financials:**\n\n"
            f"| Indicator | Value |\n|---|---|\n"
            f"| Credit Rating | {fin['credit_rating']} |\n"
            f"| Revenue Growth (YoY) | {fin['revenue_growth_yoy']:.0%} |\n"
            f"| Debt-to-Equity | {fin['debt_to_equity']:.2f} |\n"
            f"| Operating Margin | {fin['operating_margin']:.0%} |\n"
            f"| Cash Reserves | {fin['cash_reserves_months']} months |\n"
            f"| Recent Layoffs | {'Yes' if fin['recent_layoffs'] else 'No'} |\n\n"
            f"**Budget Analysis:**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Est. IT Budget | ${it_budget:,}/yr ({fin['it_budget_pct_revenue']:.1%} of revenue) |\n"
            f"| Deal Value | ${acct['opportunity_value']:,} |\n"
            f"| Deal as % IT Budget | {deal_pct_it_budget:.1f}% |\n"
            f"| Budget Cycle | {fin['budget_cycle']} |\n"
            f"| Fiscal Year End | {fin['fiscal_year_end']} |\n\n"
            f"**Financial Risk Level: {fin_risk}**\n\n"
            f"**Implications:**\n"
            f"{implications}\n"
            f"Source: [D&B + Financial Intelligence + CRM]\n"
            f"Agents: RiskAssessmentAgent"
        )

    # ── executive_summary ─────────────────────────────────────
    def _executive_summary(self, key):
        acct = _ACCOUNTS[key]
        risk_score = _composite_risk_score(key)
        win_prob = _win_probability(key)
        churn_prob = _churn_probability(key)
        fin = _FINANCIAL_HEALTH.get(key, {})
        factors = _RISK_FACTORS.get(key, [])

        high_count = sum(1 for f in factors if f["severity"] == "High")
        med_count = sum(1 for f in factors if f["severity"] == "Medium")

        churn_display = f"{churn_prob:.0%}" if churn_prob is not None else "N/A (prospect)"
        churn_status = "Monitoring" if churn_prob and churn_prob < 0.15 else "Action needed" if churn_prob else "N/A"

        if risk_score >= 65:
            overall = "High Risk"
            recommendation = "Escalate to management, accelerate mitigation actions"
        elif risk_score >= 40:
            overall = "Moderate Risk"
            recommendation = "Address high-severity factors within 2 weeks"
        else:
            overall = "Low Risk"
            recommendation = "Maintain current engagement cadence"

        risk_lines = "".join(
            f"- [{f['severity']}] {f['factor']}\n"
            for f in factors if f["severity"] in ("High", "Medium")
        )

        return (
            f"**Risk Executive Summary: {acct['name']}**\n\n"
            f"**Overall Assessment: {overall}**\n\n"
            f"| Dimension | Score | Status |\n|---|---|---|\n"
            f"| Deal Risk | {risk_score}/100 | {high_count} high, {med_count} medium factors |\n"
            f"| Win Probability | {win_prob}% | {'Above' if win_prob >= 50 else 'Below'} 50% threshold |\n"
            f"| Churn Probability | {churn_display} | {churn_status} |\n"
            f"| Financial Health | {fin.get('credit_rating', 'N/A')} | {fin.get('revenue_growth_yoy', 0):.0%} YoY growth |\n\n"
            f"**Key Risks:**\n"
            f"{risk_lines}\n"
            f"**Recommendation:** {recommendation}\n\n"
            f"**Value at Stake:**\n"
            f"- Opportunity: ${acct['opportunity_value']:,}\n"
            f"- Current ARR: ${acct['current_spend']:,}\n"
            f"- Total at risk: ${acct['opportunity_value'] + acct['current_spend']:,}\n\n"
            f"Source: [Deal Analytics + Financial Intelligence + Product Analytics]\n"
            f"Agents: RiskAssessmentAgent"
        )


if __name__ == "__main__":
    agent = RiskAssessmentAgent()
    for op in ["assess_deal_risk", "churn_prediction", "financial_risk", "executive_summary"]:
        print("=" * 60)
        print(agent.perform(operation=op, account_name="Acme Corporation"))
        print()
