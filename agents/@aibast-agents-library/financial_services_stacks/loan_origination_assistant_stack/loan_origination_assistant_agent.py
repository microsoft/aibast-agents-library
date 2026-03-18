"""
Loan Origination Assistant Agent — Financial Services Stack

Supports loan application review, credit analysis, document verification,
and decision recommendations for lending operations.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/loan-origination-assistant",
    "version": "1.0.0",
    "display_name": "Loan Origination Assistant Agent",
    "description": "Loan origination support with application review, credit analysis, document verification, and decision recommendations.",
    "author": "AIBAST",
    "tags": ["loan", "origination", "credit", "underwriting", "mortgage", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

LOAN_APPLICATIONS = {
    "LA-2025-4001": {
        "applicant": "Thomas & Rebecca Harper",
        "loan_type": "conventional_30yr",
        "purpose": "purchase",
        "property_address": "742 Evergreen Terrace, Springfield",
        "property_value": 485000,
        "loan_amount": 388000,
        "credit_score": 762,
        "annual_income": 142000,
        "monthly_debt": 1850,
        "employment_years": 8,
        "down_payment_pct": 20.0,
        "status": "underwriting",
        "loan_officer": "Diana Cruz",
    },
    "LA-2025-4002": {
        "applicant": "Kevin Nguyen",
        "loan_type": "fha_30yr",
        "purpose": "purchase",
        "property_address": "1200 Oak Park Ave, Unit 4B",
        "property_value": 275000,
        "loan_amount": 265375,
        "credit_score": 648,
        "annual_income": 68000,
        "monthly_debt": 890,
        "employment_years": 3,
        "down_payment_pct": 3.5,
        "status": "document_review",
        "loan_officer": "Mark Peterson",
    },
    "LA-2025-4003": {
        "applicant": "Westfield Properties LLC",
        "loan_type": "commercial_5yr",
        "purpose": "refinance",
        "property_address": "8800 Industrial Blvd",
        "property_value": 2400000,
        "loan_amount": 1680000,
        "credit_score": 0,
        "annual_income": 580000,
        "monthly_debt": 22000,
        "employment_years": 0,
        "down_payment_pct": 30.0,
        "status": "credit_review",
        "loan_officer": "Diana Cruz",
        "dscr": 1.42,
    },
    "LA-2025-4004": {
        "applicant": "Sandra Blake",
        "loan_type": "va_30yr",
        "purpose": "purchase",
        "property_address": "555 Freedom Way",
        "property_value": 340000,
        "loan_amount": 340000,
        "credit_score": 710,
        "annual_income": 95000,
        "monthly_debt": 650,
        "employment_years": 12,
        "down_payment_pct": 0.0,
        "status": "approved",
        "loan_officer": "Mark Peterson",
    },
}

APPROVAL_CRITERIA = {
    "conventional_30yr": {"min_credit": 620, "max_dti": 45, "min_down_pct": 5, "max_ltv": 95},
    "fha_30yr": {"min_credit": 580, "max_dti": 50, "min_down_pct": 3.5, "max_ltv": 96.5},
    "va_30yr": {"min_credit": 580, "max_dti": 60, "min_down_pct": 0, "max_ltv": 100},
    "commercial_5yr": {"min_credit": 0, "max_dti": 0, "min_down_pct": 20, "max_ltv": 80, "min_dscr": 1.25},
}

DOCUMENT_REQUIREMENTS = {
    "income": ["W-2 forms (last 2 years)", "Pay stubs (last 30 days)", "Tax returns (last 2 years)", "Employment verification letter"],
    "assets": ["Bank statements (last 2 months)", "Investment account statements", "Gift letter (if applicable)"],
    "property": ["Purchase agreement", "Appraisal report", "Title search", "Homeowners insurance quote"],
    "identity": ["Government-issued photo ID", "Social Security verification"],
    "fha_specific": ["FHA case number assignment", "HUD-1 settlement statement"],
    "va_specific": ["Certificate of Eligibility (COE)", "DD-214 or active duty proof"],
    "commercial_specific": ["Business tax returns (3 years)", "Profit & loss statement", "Rent roll", "Environmental Phase I"],
}

RATE_SHEET = {
    "conventional_30yr": {"rate": 6.875, "apr": 7.012, "points": 0.5},
    "fha_30yr": {"rate": 6.500, "apr": 7.250, "points": 0.0, "mip_upfront": 1.75, "mip_annual": 0.55},
    "va_30yr": {"rate": 6.250, "apr": 6.485, "points": 0.0, "funding_fee": 2.15},
    "commercial_5yr": {"rate": 7.500, "apr": 7.750, "points": 1.0},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _calculate_dti(app):
    """Calculate debt-to-income ratio."""
    monthly_income = app["annual_income"] / 12
    if monthly_income == 0:
        return 0
    rate_info = RATE_SHEET.get(app["loan_type"], {})
    monthly_rate = rate_info.get("rate", 7.0) / 100 / 12
    n_payments = 360
    if "5yr" in app["loan_type"]:
        n_payments = 60
    if monthly_rate > 0:
        payment = app["loan_amount"] * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
    else:
        payment = app["loan_amount"] / n_payments
    total_debt = app["monthly_debt"] + payment
    return round((total_debt / monthly_income) * 100, 1)


def _calculate_ltv(app):
    """Calculate loan-to-value ratio."""
    if app["property_value"] == 0:
        return 0
    return round((app["loan_amount"] / app["property_value"]) * 100, 1)


def _eligibility_check(app):
    """Check application against approval criteria."""
    criteria = APPROVAL_CRITERIA.get(app["loan_type"], {})
    issues = []
    if criteria.get("min_credit") and app["credit_score"] < criteria["min_credit"]:
        issues.append(f"Credit score {app['credit_score']} below minimum {criteria['min_credit']}")
    dti = _calculate_dti(app)
    if criteria.get("max_dti") and dti > criteria["max_dti"]:
        issues.append(f"DTI {dti}% exceeds maximum {criteria['max_dti']}%")
    ltv = _calculate_ltv(app)
    if criteria.get("max_ltv") and ltv > criteria["max_ltv"]:
        issues.append(f"LTV {ltv}% exceeds maximum {criteria['max_ltv']}%")
    if criteria.get("min_dscr") and app.get("dscr", 0) < criteria["min_dscr"]:
        issues.append(f"DSCR {app.get('dscr', 0)} below minimum {criteria['min_dscr']}")
    return issues


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class LoanOriginationAssistantAgent(BasicAgent):
    """Loan origination assistant agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/loan-origination-assistant"
        self.metadata = {
            "name": self.name,
            "display_name": "Loan Origination Assistant Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "application_review",
                            "credit_analysis",
                            "document_verification",
                            "decision_recommendation",
                        ],
                    },
                    "application_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "application_review")
        dispatch = {
            "application_review": self._application_review,
            "credit_analysis": self._credit_analysis,
            "document_verification": self._document_verification,
            "decision_recommendation": self._decision_recommendation,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _application_review(self, **kwargs) -> str:
        lines = ["# Loan Application Pipeline\n"]
        lines.append("| App ID | Applicant | Type | Amount | LTV | Status | LO |")
        lines.append("|---|---|---|---|---|---|---|")
        for aid, app in LOAN_APPLICATIONS.items():
            ltv = _calculate_ltv(app)
            lines.append(
                f"| {aid} | {app['applicant']} | {app['loan_type'].replace('_', ' ').title()} "
                f"| ${app['loan_amount']:,.0f} | {ltv}% | {app['status'].replace('_', ' ').title()} | {app['loan_officer']} |"
            )
        total_pipeline = sum(a["loan_amount"] for a in LOAN_APPLICATIONS.values())
        lines.append(f"\n**Pipeline Volume:** ${total_pipeline:,.0f}")
        lines.append(f"**Applications:** {len(LOAN_APPLICATIONS)}")
        lines.append("\n## Rate Sheet\n")
        lines.append("| Product | Rate | APR | Points |")
        lines.append("|---|---|---|---|")
        for product, rate in RATE_SHEET.items():
            lines.append(f"| {product.replace('_', ' ').title()} | {rate['rate']}% | {rate['apr']}% | {rate['points']} |")
        return "\n".join(lines)

    def _credit_analysis(self, **kwargs) -> str:
        app_id = kwargs.get("application_id", "LA-2025-4001")
        app = LOAN_APPLICATIONS.get(app_id, list(LOAN_APPLICATIONS.values())[0])
        dti = _calculate_dti(app)
        ltv = _calculate_ltv(app)
        issues = _eligibility_check(app)
        lines = [f"# Credit Analysis: {app_id}\n"]
        lines.append(f"- **Applicant:** {app['applicant']}")
        lines.append(f"- **Loan Type:** {app['loan_type'].replace('_', ' ').title()}")
        lines.append(f"- **Credit Score:** {app['credit_score'] or 'N/A (Commercial)'}")
        lines.append(f"- **Annual Income:** ${app['annual_income']:,.0f}")
        lines.append(f"- **Monthly Debt:** ${app['monthly_debt']:,.0f}")
        lines.append(f"- **DTI Ratio:** {dti}%")
        lines.append(f"- **LTV Ratio:** {ltv}%")
        lines.append(f"- **Down Payment:** {app['down_payment_pct']}%")
        if app.get("dscr"):
            lines.append(f"- **DSCR:** {app['dscr']}")
        lines.append(f"- **Employment:** {app['employment_years']} years\n")
        criteria = APPROVAL_CRITERIA.get(app["loan_type"], {})
        lines.append("## Criteria Comparison\n")
        lines.append("| Metric | Actual | Required | Status |")
        lines.append("|---|---|---|---|")
        if criteria.get("min_credit"):
            met = "Pass" if app["credit_score"] >= criteria["min_credit"] else "Fail"
            lines.append(f"| Credit Score | {app['credit_score']} | >= {criteria['min_credit']} | {met} |")
        if criteria.get("max_dti"):
            met = "Pass" if dti <= criteria["max_dti"] else "Fail"
            lines.append(f"| DTI | {dti}% | <= {criteria['max_dti']}% | {met} |")
        met = "Pass" if ltv <= criteria.get("max_ltv", 100) else "Fail"
        lines.append(f"| LTV | {ltv}% | <= {criteria.get('max_ltv', 100)}% | {met} |")
        if issues:
            lines.append("\n## Issues\n")
            for issue in issues:
                lines.append(f"- {issue}")
        else:
            lines.append("\n**All criteria met.**")
        return "\n".join(lines)

    def _document_verification(self, **kwargs) -> str:
        app_id = kwargs.get("application_id", "LA-2025-4001")
        app = LOAN_APPLICATIONS.get(app_id, list(LOAN_APPLICATIONS.values())[0])
        lines = [f"# Document Verification: {app_id}\n"]
        lines.append(f"**Applicant:** {app['applicant']}")
        lines.append(f"**Loan Type:** {app['loan_type'].replace('_', ' ').title()}\n")
        categories = ["income", "assets", "property", "identity"]
        if "fha" in app["loan_type"]:
            categories.append("fha_specific")
        elif "va" in app["loan_type"]:
            categories.append("va_specific")
        elif "commercial" in app["loan_type"]:
            categories.append("commercial_specific")
        for cat in categories:
            docs = DOCUMENT_REQUIREMENTS.get(cat, [])
            lines.append(f"## {cat.replace('_', ' ').title()}\n")
            for doc in docs:
                lines.append(f"- [ ] {doc}")
            lines.append("")
        return "\n".join(lines)

    def _decision_recommendation(self, **kwargs) -> str:
        lines = ["# Loan Decision Recommendations\n"]
        for aid, app in LOAN_APPLICATIONS.items():
            dti = _calculate_dti(app)
            ltv = _calculate_ltv(app)
            issues = _eligibility_check(app)
            if not issues:
                decision = "Approve"
                rationale = "All underwriting criteria met"
            elif len(issues) == 1 and dti <= 50:
                decision = "Conditional Approve"
                rationale = f"Minor condition: {issues[0]}"
            else:
                decision = "Refer to Senior UW"
                rationale = "; ".join(issues)
            lines.append(f"## {aid}: {app['applicant']}\n")
            lines.append(f"- **Loan:** ${app['loan_amount']:,.0f} ({app['loan_type'].replace('_', ' ').title()})")
            lines.append(f"- **Credit/DTI/LTV:** {app['credit_score'] or 'N/A'} / {dti}% / {ltv}%")
            lines.append(f"- **Recommendation:** {decision}")
            lines.append(f"- **Rationale:** {rationale}\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = LoanOriginationAssistantAgent()
    print(agent.perform(operation="application_review"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="credit_analysis", application_id="LA-2025-4002"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="document_verification", application_id="LA-2025-4004"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="decision_recommendation"))
