"""
Loan Origination Assistant Agent — Financial Services Stack

Supports mortgage application intake, program comparison, credit and property
analysis, document verification, underwriting findings, condition tracking and a
loan processing summary for lending operations. The default file is the
Martinez purchase application (LA-2025-4001) from the demo.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/loan-origination-assistant",
    "version": "1.1.0",
    "display_name": "Loan Origination Assistant",
    "description": "Streamline mortgage origination with intelligent automation, enabling faster, more accurate loan decisions.",
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

DEFAULT_APPLICATION = "LA-2025-4001"

LOAN_APPLICATIONS = {
    "LA-2025-4001": {
        "applicant": "Michael & Sarah Martinez",
        "alias": "martinez",
        "loan_type": "conventional_30yr",
        "purpose": "purchase",
        "property_address": "1234 Oak Lane",
        "property_value": 485000,
        "loan_amount": 388000,
        "credit_score": 742,
        "credit_scores": [742, 738],
        "annual_income": 170400,
        "monthly_debt": 1158,
        "taxes_insurance_monthly": 1405,
        "living_expenses_monthly": 3040,
        "employment_years": 8,
        "employment": [["Michael", 8], ["Sarah", 5]],
        "down_payment_pct": 20.0,
        "assets_verified": 145000,
        "earnest_money_deposited": 37000,
        "closing_costs": 10000,
        "late_payments": 0,
        "utilization_pct": 18,
        "avm_low": 490000,
        "avm_high": 510000,
        "property_type": "Single-family, good condition",
        "documents": [
            ["Income", 9, 10, "missing 1 paystub"],
            ["Assets", 5, 5, "complete"],
            ["Credit", 4, 4, "complete"],
            ["Property", 4, 5, "appraisal ordered, 5 days"],
        ],
        "program_fit": [
            ["conventional_30yr", 98],
            ["conventional_15yr", 95],
            ["fha_30yr", 100],
        ],
        "recommended_program": "conventional_30yr",
        "standard_close_days": 45,
        "projected_close_days": 15,
        "status": "underwriting",
        "loan_officer": "Diana Cruz",
    },
    "LA-2025-4002": {
        "applicant": "Kevin Nguyen",
        "alias": "nguyen",
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
        "alias": "westfield",
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
        "alias": "blake",
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
        "status": "ready_for_human_decision",
        "loan_officer": "Mark Peterson",
    },
}

APPROVAL_CRITERIA = {
    "conventional_30yr": {"min_credit": 620, "max_dti": 43, "min_down_pct": 5, "max_ltv": 95, "min_reserve_months": 6},
    "conventional_15yr": {"min_credit": 620, "max_dti": 43, "min_down_pct": 5, "max_ltv": 95, "min_reserve_months": 6},
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
    "conventional_30yr": {"rate": 6.875, "apr": 7.012, "points": 0.5, "years": 30},
    "conventional_15yr": {"rate": 6.375, "apr": 6.498, "points": 0.5, "years": 15},
    "fha_30yr": {"rate": 7.125, "apr": 7.250, "points": 0.0, "years": 30, "mip_upfront": 1.75, "mip_annual": 0.55},
    "va_30yr": {"rate": 6.250, "apr": 6.485, "points": 0.0, "years": 30, "funding_fee": 2.15},
    "commercial_5yr": {"rate": 7.500, "apr": 7.750, "points": 1.0, "years": 5},
}

PROGRAM_NAMES = {
    "conventional_30yr": "Conventional 30-yr",
    "conventional_15yr": "Conventional 15-yr",
    "fha_30yr": "FHA 30-yr",
    "va_30yr": "VA 30-yr",
    "commercial_5yr": "Commercial 5-yr",
}

CONDITIONS = {
    "LA-2025-4001": [
        {"condition": "Recent paystub", "status": "Outstanding", "due": "2 days", "action": "Borrower upload", "outstanding": True},
        {"condition": "Appraisal", "status": "Ordered", "due": "3 days", "action": "Inspector scheduled", "outstanding": True},
        {"condition": "Insurance quote", "status": "Submitted", "due": "Under review", "action": "Meets requirements", "outstanding": False},
        {"condition": "Title work", "status": "Ordered", "due": "5 days", "action": "In progress", "outstanding": False},
    ],
    "LA-2025-4002": [
        {"condition": "Employment verification", "status": "Open", "due": "Assign in LOS", "action": "Processor follow-up", "outstanding": True},
        {"condition": "FHA case number", "status": "Open", "due": "Assign in LOS", "action": "Processor follow-up", "outstanding": True},
        {"condition": "Final appraisal", "status": "Open", "due": "Assign in LOS", "action": "Order appraisal", "outstanding": True},
    ],
    "LA-2025-4003": [
        {"condition": "Environmental Phase I", "status": "Open", "due": "Assign in LOS", "action": "Order report", "outstanding": True},
        {"condition": "Current rent roll", "status": "Open", "due": "Assign in LOS", "action": "Borrower upload", "outstanding": True},
    ],
    "LA-2025-4004": [
        {"condition": "Certificate of Eligibility validation", "status": "Open", "due": "Assign in LOS", "action": "Processor follow-up", "outstanding": True},
        {"condition": "Final insurance evidence", "status": "Open", "due": "Assign in LOS", "action": "Borrower upload", "outstanding": True},
    ],
}

SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — LENDER REVIEW REQUIRED.** Fictional applications, rates, and "
    "eligibility rules only. This is not lending, legal, or financial advice and does not approve, deny, "
    "price, lock, close, fund, or modify a loan.\n\n"
)

_OPERATIONS = [
    "application_review",
    "credit_analysis",
    "document_verification",
    "decision_recommendation",
    "condition_tracking",
    "application_intake",
    "program_comparison",
    "processing_summary",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_application(query):
    """Application ID, borrower name or last name; default file when empty; None when nothing matches."""
    if not query:
        return DEFAULT_APPLICATION
    q = str(query).lower().strip()
    for app_id, app in LOAN_APPLICATIONS.items():
        if app_id.lower() in q or app["alias"] in q or q in app["applicant"].lower():
            return app_id
    return None


def _payment(amount, loan_type):
    """Monthly principal and interest for a rate-sheet program."""
    rate_info = RATE_SHEET.get(loan_type, {})
    monthly_rate = rate_info.get("rate", 7.0) / 100 / 12
    n_payments = rate_info.get("years", 30) * 12
    if monthly_rate > 0:
        return amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)
    return amount / n_payments


def _housing_payment(app):
    """Proposed housing payment: P&I plus taxes and insurance (PITI) when known."""
    return _payment(app["loan_amount"], app["loan_type"]) + app.get("taxes_insurance_monthly", 0)


def _calculate_dti(app):
    """Back-end debt-to-income ratio (housing payment plus other debts)."""
    monthly_income = app["annual_income"] / 12
    if monthly_income == 0:
        return 0
    total_debt = app["monthly_debt"] + _housing_payment(app)
    return round((total_debt / monthly_income) * 100, 1)


def _front_dti(app):
    """Front-end ratio (housing payment only)."""
    monthly_income = app["annual_income"] / 12
    if monthly_income == 0:
        return 0
    return round((_housing_payment(app) / monthly_income) * 100, 1)


def _calculate_ltv(app):
    """Calculate loan-to-value ratio."""
    if app["property_value"] == 0:
        return 0
    return round((app["loan_amount"] / app["property_value"]) * 100, 1)


def _reserves(app):
    """Reserves after close and months covered (housing + debts + living expenses)."""
    if "assets_verified" not in app:
        return 0, 0
    down = app["property_value"] - app["loan_amount"]
    cash_to_close = down + app["closing_costs"] - app["earnest_money_deposited"]
    reserves = app["assets_verified"] - cash_to_close
    monthly = _housing_payment(app) + app["monthly_debt"] + app["living_expenses_monthly"]
    return reserves, round(reserves / monthly, 1)


def _documents(app):
    """Per-category completion rows and the overall completion percent."""
    rows = []
    received, required = 0, 0
    for name, got, need, note in app.get("documents", []):
        received += got
        required += need
        rows.append([name, round(got * 100 / need), note])
    overall = round(received * 100 / required) if required else 0
    return rows, overall


def _outstanding(app_id):
    return [c for c in CONDITIONS.get(app_id, []) if c["outstanding"]]


def _is_commercial(app):
    return "commercial" in app["loan_type"]


def _eligibility_check(app):
    """Check application against approval criteria."""
    criteria = APPROVAL_CRITERIA.get(app["loan_type"], {})
    issues = []
    if criteria.get("min_credit") and app["credit_score"] < criteria["min_credit"]:
        issues.append(f"Credit score {app['credit_score']} below minimum {criteria['min_credit']}")
    if not _is_commercial(app):
        dti = _calculate_dti(app)
        if criteria.get("max_dti") and dti > criteria["max_dti"]:
            issues.append(f"DTI {dti}% exceeds maximum {criteria['max_dti']}%")
    ltv = _calculate_ltv(app)
    if criteria.get("max_ltv") and ltv > criteria["max_ltv"]:
        issues.append(f"LTV {ltv}% exceeds maximum {criteria['max_ltv']}%")
    if criteria.get("min_dscr") and app.get("dscr", 0) < criteria["min_dscr"]:
        issues.append(f"DSCR {app.get('dscr', 0)} below minimum {criteria['min_dscr']}")
    return issues


def _money_k(value):
    return f"${value / 1000:,.0f}K"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class LoanOriginationAssistantAgent(BasicAgent):
    """Loan origination assistant agent."""

    def __init__(self):
        self.name = "LoanOriginationAssistantAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Loan Origination Assistant Agent",
            "description": (
                "Always call this tool for loan-officer, processor, underwriter, or closing-coordinator "
                "requests: processing a mortgage application with an eligibility assessment and "
                "documentation status, which loan programs a borrower is eligible for, credit and property "
                "analysis, conditions that need to be cleared, a complete loan processing summary, the "
                "mortgage pipeline, which application remains in document review, a named borrower's "
                "ratios, a VA document checklist, or whether any loan was approved. The demo file is the "
                "Martinez application (LA-2025-4001) and is used when no file is named. Do not answer those "
                "workflows from general knowledge. Uses fictional records only and never approves, denies, "
                "prices, locks, closes, funds, or modifies a loan. Fair-lending controls and authorized "
                "human underwriting review are required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose application_intake to process a mortgage application and give an "
                            "eligibility assessment with documentation status. Choose program_comparison for "
                            "which loan programs the borrower is eligible for, rates, payments and the "
                            "recommended program. Choose credit_analysis for the credit and property analysis "
                            "or a named borrower's DTI, LTV, credit, DSCR, ratios, or eligibility exceptions. "
                            "Choose condition_tracking for conditions that need to be cleared, open conditions, "
                            "the commercial refinance, timelines, or whether a closing date was promised. "
                            "Choose processing_summary for the complete loan processing summary. Choose "
                            "application_review for the mortgage pipeline, intake volume, statuses, or which "
                            "application is in document review. Choose document_verification for a named "
                            "file's required documents, including VA or FHA checklists. Choose "
                            "decision_recommendation for which files meet limited criteria or whether the "
                            "assistant approved a loan."
                        ),
                        "enum": list(_OPERATIONS),
                    },
                    "application_id": {
                        "type": "string",
                        "description": (
                            "Synthetic loan mapping: Michael and Sarah Martinez, Martinez or 'this mortgage "
                            "application' is LA-2025-4001 (the default); Kevin Nguyen or Kevin is "
                            "LA-2025-4002; Westfield Properties or the commercial refinance is LA-2025-4003; "
                            "Sandra Blake, Sandra, or the VA file is LA-2025-4004. Omit for the Martinez demo "
                            "file and for pipeline-wide and decision-wide reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "application_intake")
        dispatch = {
            "application_review": self._application_review,
            "credit_analysis": self._credit_analysis,
            "document_verification": self._document_verification,
            "decision_recommendation": self._decision_recommendation,
            "condition_tracking": self._condition_tracking,
            "application_intake": self._application_intake,
            "program_comparison": self._program_comparison,
            "processing_summary": self._processing_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        record_id = kwargs.get("application_id")
        app_id = _resolve_application(record_id)
        if app_id is None:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        return SYNTHETIC_NOTICE + handler(app_id)

    # -- application_review: pipeline ---------------------------------------
    def _application_review(self, app_id) -> str:
        lines = ["# Loan Application Pipeline\n"]
        lines.append("| App ID | Applicant | Type | Amount | LTV | Status | LO |")
        lines.append("|---|---|---|---|---|---|---|")
        for aid, app in LOAN_APPLICATIONS.items():
            ltv = _calculate_ltv(app)
            lines.append(
                f"| {aid} | {app['applicant']} | {PROGRAM_NAMES[app['loan_type']]} "
                f"| ${app['loan_amount']:,.0f} | {ltv}% | {app['status'].replace('_', ' ').title()} | {app['loan_officer']} |"
            )
        total_pipeline = sum(a["loan_amount"] for a in LOAN_APPLICATIONS.values())
        lines.append(f"\n**Pipeline Volume:** ${total_pipeline:,.0f}")
        lines.append(f"**Applications:** {len(LOAN_APPLICATIONS)}")
        lines.append("\n## Rate Sheet\n")
        lines.append("| Product | Rate | APR | Points |")
        lines.append("|---|---|---|---|")
        for product, rate in RATE_SHEET.items():
            lines.append(f"| {PROGRAM_NAMES[product]} | {rate['rate']}% | {rate['apr']}% | {rate['points']} |")
        return "\n".join(lines)

    # -- application_intake: video turn 1 ------------------------------------
    def _application_intake(self, app_id) -> str:
        app = LOAN_APPLICATIONS[app_id]
        rows, overall = _documents(app)
        scores = app.get("credit_scores") or [app["credit_score"]]
        score_text = " / ".join(str(s) for s in scores) if scores[0] else "N/A (commercial)"
        if scores[0] >= 740:
            score_text += " (excellent)"
        down = app["property_value"] - app["loan_amount"]
        employment = app.get("employment") or [[app["applicant"], app["employment_years"]]]
        tenure = ", ".join(f"{name} {years} yrs" for name, years in employment)
        issues = _eligibility_check(app)
        lines = [f"# Application Processed: {app['applicant']} ({app_id})\n"]
        if rows:
            lines.append(f"**{overall}% documentation complete.**\n")
        lines.append("| Field | Details |\n|---|---|")
        lines.append(f"| Borrowers | {app['applicant']} |")
        lines.append(f"| Property | {app['property_address']}, {_money_k(app['property_value'])} {app['purpose']} |")
        lines.append(f"| Loan amount | {_money_k(app['loan_amount'])} ({round(down * 100 / app['property_value'])}% down) |")
        lines.append(f"| Credit scores | {score_text} |")
        lines.append(f"| Program | {PROGRAM_NAMES[app['loan_type']]} |")
        if rows:
            lines.append("\n**Document Status:**\n")
            lines.append("| Category | Complete | Note |\n|---|---|---|")
            for name, pct, note in rows:
                lines.append(f"| {name} | {pct}% | {note} |")
            lines.append(f"| **Overall** | **{overall}%** | |")
        else:
            lines.append("\nDocument status: use document_verification for this file's checklist.")
        strength = f"Stable employment ({tenure})"
        if scores[0] >= 740:
            strength = "Excellent credit, s" + strength[1:]
        if "assets_verified" in app:
            strength += f", assets {_money_k(app['assets_verified'])} verified"
        flags = "No red flags in the stated criteria." if not issues else "Exceptions: " + "; ".join(issues) + "."
        lines.append(f"\n**Application Strength:** {strength}. {flags}")
        lines.append("\n**Next step:** run eligibility and program matching (program comparison).")
        lines.append("\nEligibility assessment is guidance for underwriter review; no lending decision has been made.")
        lines.append("\nSource: [LOS + Document Portal + Credit] Agents: ApplicationIntakeAgent, DocumentProcessingAgent")
        return "\n".join(lines)

    # -- program_comparison: video turn 2 ------------------------------------
    def _program_comparison(self, app_id) -> str:
        app = LOAN_APPLICATIONS[app_id]
        if not app.get("program_fit"):
            return (
                f"# Program Comparison: {app_id}\n\n**Not available:** no program comparison is on file for "
                f"{app['applicant']}; only the {PROGRAM_NAMES[app['loan_type']]} program was assessed. "
                "Use credit_analysis for its criteria."
            )
        recommended = app["recommended_program"]
        _, months = _reserves(app)
        criteria = APPROVAL_CRITERIA[recommended]
        front = _front_dti(app)
        ltv = _calculate_ltv(app)
        lines = [f"# Eligibility Analyzed: {app['applicant']} ({app_id})\n"]
        lines.append(f"Qualifies for {len(app['program_fit'])} programs; {PROGRAM_NAMES[recommended]} recommended.\n")
        lines.append("| Program | Rate | Monthly P&I | Eligibility fit |\n|---|---|---|---|")
        for program, fit in app["program_fit"]:
            pay = _payment(app["loan_amount"], program)
            tag = " (recommended)" if program == recommended else ""
            lines.append(f"| {PROGRAM_NAMES[program]} | {RATE_SHEET[program]['rate']}% | ${pay:,.0f} | {fit}%{tag} |")
        pmi = "No PMI (20% down)" if ltv <= 80 else "PMI required (LTV above 80%)"
        lines.append(f"\n**Recommended: {PROGRAM_NAMES[recommended]}**\n")
        lines.append("- Best rate/payment balance")
        lines.append(f"- {pmi}")
        lines.append(f"- DTI: {front:.0f}% (well below {criteria['max_dti']}% max)")
        lines.append(f"- Reserves: {months} months (exceeds {criteria['min_reserve_months']}-month requirement)")
        minor = ", ".join(c["condition"].lower() for c in _outstanding(app_id))
        lines.append(f"\n**Minor Conditions:** {minor}")
        lines.append(
            f"**Fast-Track Eligible:** strong profile qualifies for expedited underwriting "
            f"({app['projected_close_days']}-day close possible, projected, not promised)."
        )
        lines.append(
            "\nEligibility fit is an underwriting-guideline match score for underwriter review, not an approval "
            "prediction; rates are synthetic and nothing is priced or locked."
        )
        lines.append("\nSource: [Underwriting Guidelines + AUS] Agents: EligibilityAssessmentAgent, DocumentProcessingAgent")
        lines.append("\n**Next step:** run comprehensive credit and property analysis.")
        return "\n".join(lines)

    # -- credit_analysis: video turn 3 ---------------------------------------
    def _credit_analysis(self, app_id) -> str:
        app = LOAN_APPLICATIONS[app_id]
        dti = _calculate_dti(app)
        ltv = _calculate_ltv(app)
        issues = _eligibility_check(app)
        lines = [f"# Credit Analysis: {app_id}\n"]
        lines.append(f"- **Applicant:** {app['applicant']}")
        lines.append(f"- **Loan Type:** {PROGRAM_NAMES[app['loan_type']]}")
        if app.get("credit_scores"):
            reserves, months = _reserves(app)
            scores = " / ".join(str(s) for s in app["credit_scores"])
            lines.append("\n## Credit Summary\n")
            lines.append(f"- Scores: {scores} (excellent)")
            lines.append(f"- Payment history: {app['late_payments']} late payments")
            lines.append(f"- Utilization: {app['utilization_pct']}%")
            lines.append(f"- DTI: Front {_front_dti(app):.0f}% / Back {dti:.0f}%")
            lines.append("\n## Financial Strength\n")
            lines.append(f"- Monthly income: ${app['annual_income'] / 12:,.0f} (verified)")
            lines.append(
                f"- Proposed payment: ${_housing_payment(app):,.0f} PITI "
                f"(P&I ${_payment(app['loan_amount'], app['loan_type']):,.0f} + taxes/insurance ${app['taxes_insurance_monthly']:,})"
            )
            lines.append(f"- Reserves: {_money_k(reserves)} after close ({months} months)")
            lines.append("\n## Property Valuation\n")
            lines.append(f"- Purchase price: {_money_k(app['property_value'])}")
            lines.append(f"- AVM estimate: {_money_k(app['avm_low'])}-{_money_k(app['avm_high'])}")
            lines.append(f"- LTV: {ltv:.0f}%")
            lines.append(f"- Property type: {app['property_type']}")
            risk = "Low" if not issues and ltv <= 80 else "Elevated"
            lines.append(
                f"\n**Risk Assessment:** {risk} risk. Strong borrowers, conservative LTV, excellent credit, ample reserves."
            )
            lines.append("\nSource: [Credit Bureaus + AVM + Financial Calc] Agents: CreditAnalysisAgent, PropertyValuationAgent\n")
        else:
            lines.append(f"- **Credit Score:** {app['credit_score'] or 'N/A (Commercial)'}")
            lines.append(f"- **Annual Income:** ${app['annual_income']:,.0f}")
            lines.append(f"- **Monthly Debt:** ${app['monthly_debt']:,.0f}")
            if _is_commercial(app):
                lines.append("- **DTI Ratio:** not used for commercial files (DSCR applies)")
            else:
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
        if criteria.get("max_dti") and not _is_commercial(app):
            met = "Pass" if dti <= criteria["max_dti"] else "Fail"
            lines.append(f"| DTI | {dti}% | <= {criteria['max_dti']}% | {met} |")
        if criteria.get("min_dscr"):
            met = "Pass" if app.get("dscr", 0) >= criteria["min_dscr"] else "Fail"
            lines.append(f"| DSCR | {app.get('dscr', 0)} | >= {criteria['min_dscr']} | {met} |")
        met = "Pass" if ltv <= criteria.get("max_ltv", 100) else "Fail"
        lines.append(f"| LTV | {ltv}% | <= {criteria.get('max_ltv', 100)}% | {met} |")
        if issues:
            lines.append("\n## Issues\n")
            for issue in issues:
                lines.append(f"- {issue}")
        else:
            lines.append("\n**All criteria met.**")
        return "\n".join(lines)

    # -- document_verification -----------------------------------------------
    def _document_verification(self, app_id) -> str:
        app = LOAN_APPLICATIONS[app_id]
        lines = [f"# Document Verification: {app_id}\n"]
        lines.append(f"**Applicant:** {app['applicant']}")
        lines.append(f"**Loan Type:** {PROGRAM_NAMES[app['loan_type']]}\n")
        rows, overall = _documents(app)
        if rows:
            lines.append("## Document Status\n")
            lines.append("| Category | Complete | Note |\n|---|---|---|")
            for name, pct, note in rows:
                lines.append(f"| {name} | {pct}% | {note} |")
            lines.append(f"\n**Overall:** {overall}% documentation complete\n")
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

    # -- decision_recommendation ---------------------------------------------
    def _decision_recommendation(self, app_id) -> str:
        lines = ["# Loan Eligibility Findings for Underwriter Review\n"]
        for aid, app in LOAN_APPLICATIONS.items():
            ltv = _calculate_ltv(app)
            issues = _eligibility_check(app)
            watch = []
            if ltv > 95 and "va" not in app["loan_type"]:
                watch.append(f"LTV {ltv}% leaves little equity; confirm mortgage insurance")
            if not _is_commercial(app) and _calculate_dti(app) > 43:
                watch.append(f"DTI {_calculate_dti(app)}% above the 43% guideline; document compensating factors")
            if not issues and not watch:
                decision = "Stated criteria met — human underwriting review"
                rationale = "No exception found in the limited synthetic criteria"
            elif len(issues) <= 1:
                decision = "Condition or exception review required"
                rationale = "; ".join(issues + watch)
            else:
                decision = "Senior underwriter review required"
                rationale = "; ".join(issues + watch)
            ratio = "DSCR " + str(app["dscr"]) if _is_commercial(app) else f"DTI {_calculate_dti(app)}%"
            lines.append(f"## {aid}: {app['applicant']}\n")
            lines.append(f"- **Loan:** ${app['loan_amount']:,.0f} ({PROGRAM_NAMES[app['loan_type']]})")
            lines.append(f"- **Credit / ratio / LTV:** {app['credit_score'] or 'N/A'} / {ratio} / {ltv}%")
            lines.append(f"- **Review Finding:** {decision}")
            lines.append(f"- **Rationale:** {rationale}\n")
        lines.append(
            "No lending decision has been made. Validate source documents, program rules, fair-lending "
            "controls, disclosures, and delegated authority before any customer communication or action."
        )
        return "\n".join(lines)

    # -- condition_tracking: video turn 4 ------------------------------------
    def _condition_tracking(self, app_id) -> str:
        app = LOAN_APPLICATIONS[app_id]
        conditions = CONDITIONS.get(app_id, [])
        outstanding = _outstanding(app_id)
        lines = [f"# Conditions: {app_id} {app['applicant']}\n"]
        lines.append(f"**{len(outstanding)} outstanding items.**\n")
        lines.append("| Condition | Status | Due | Action |\n|---|---|---|---|")
        for c in conditions:
            lines.append(f"| {c['condition']} | {c['status']} | {c['due']} | {c['action']} |")
        if app.get("documents"):
            rows, _ = _documents(app)
            done = {name: pct for name, pct, _ in rows}
            lines.append("\n**Clear-to-Close Checklist:**\n")
            lines.append(f"- Income verified: {'Yes' if done['Income'] == 100 else 'Yes (pending final paystub)'}")
            lines.append(f"- Assets verified: {'Yes' if done['Assets'] == 100 else 'Pending'}")
            lines.append(f"- Credit approved for underwriting: {'Yes' if done['Credit'] == 100 else 'Pending'}")
            lines.append("- Appraisal: Pending (on schedule)")
            lines.append("- Title: Pending (on schedule)")
            lines.append("- Insurance: Under review")
            lines.append(
                f"\n**Timeline:** on track for a {app['projected_close_days']}-day close if the paystub is "
                "received within 48 hours and the appraisal is on time (projection only)."
            )
            lines.append(
                "\n**Draft team update (Dynamics 365 / Teams), ready for you to post:** "
                f"{app['applicant']} {app_id}: {len(outstanding)} outstanding conditions "
                f"({', '.join(c['condition'].lower() for c in outstanding)}); "
                f"projected {app['projected_close_days']}-day close."
            )
        else:
            lines.append("\nOwner and due date: assign in the approved loan-origination system.")
        lines.append("\nNo condition was cleared, no update was posted, and no closing date is promised.")
        lines.append("\nSource: [LOS + Document Management] Agents: ConditionTrackingAgent")
        return "\n".join(lines)

    # -- processing_summary: video turn 5 ------------------------------------
    def _processing_summary(self, app_id) -> str:
        app = LOAN_APPLICATIONS[app_id]
        if not app.get("program_fit"):
            return (
                f"# Loan Processing Summary: {app_id}\n\n**Not available:** {app['applicant']} has no completed "
                "intake session on file; use application_intake and condition_tracking for this file."
            )
        _, overall = _documents(app)
        program = app["recommended_program"]
        fit = 0
        for name, score in app["program_fit"]:
            if name == program:
                fit = score
        outstanding = _outstanding(app_id)
        std, proj = app["standard_close_days"], app["projected_close_days"]
        faster = round((std - proj) * 100 / std)
        pi = _payment(app["loan_amount"], program)
        lines = [f"# Loan Processing Summary: {app['applicant']} ({app_id})\n"]
        lines.append(f"Session complete. {proj}-day close projected.\n")
        lines.append("| Accomplishment | Result |\n|---|---|")
        lines.append(f"| Application processed | {overall}% documentation complete |")
        lines.append(f"| Program selected | {PROGRAM_NAMES[program]}, {RATE_SHEET[program]['rate']}% |")
        lines.append(f"| Eligibility confirmed | {fit}% eligibility fit (underwriter review pending) |")
        lines.append(f"| Conditions | {len(outstanding)} outstanding, on track |")
        lines.append(f"| Timeline | {proj}-day close ({faster}% faster than the {std}-day standard) |")
        lines.append("\n**Loan Details:**\n")
        lines.append(f"- Amount: {_money_k(app['loan_amount'])} at {RATE_SHEET[program]['rate']}%")
        lines.append(f"- Payment: ${pi:,.0f} P&I (${_housing_payment(app):,.0f} PITI)")
        lines.append(f"- DTI: {_front_dti(app):.0f}% (excellent)")
        lines.append("- Risk: Low")
        lines.append("\n**Remaining steps:** " + "; ".join(f"{c['condition']} ({c['due']})" for c in outstanding) + ".")
        lines.append(
            "\n**Efficiency Gains:** document processing by AI extraction (minutes vs hours); program comparison "
            "and condition tracking in one session."
        )
        lines.append(
            "\nThe timeline is a projection; no lending decision has been made and no closing date is promised."
        )
        lines.append("\nSource: [LOS + Underwriting + Condition Tracking] Agents: LoanOriginationAssistantAgent")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = LoanOriginationAssistantAgent()
    for op in ["application_intake", "program_comparison", "credit_analysis", "condition_tracking", "processing_summary"]:
        print("=" * 80)
        print(agent.perform(operation=op))
        print()
