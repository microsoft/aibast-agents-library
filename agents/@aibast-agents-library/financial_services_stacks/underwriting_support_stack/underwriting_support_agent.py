"""
Underwriting Support Agent — Financial Services Stack

Supports insurance underwriting with risk evaluation, pricing
recommendations, guideline checks, and exception reviews.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/underwriting-support",
    "version": "1.0.0",
    "display_name": "Underwriting Support Agent",
    "description": "Automate commercial underwriting analysis to accelerate evaluations, improve pricing accuracy, and maintain full compliance.",
    "author": "AIBAST",
    "tags": ["underwriting", "insurance", "risk", "pricing", "guidelines", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

APPLICATIONS = {
    "UW-2025-101": {
        "applicant": "Riverside Manufacturing Inc.",
        "line_of_business": "commercial_property",
        "coverage_requested": 5000000,
        "premium_indicated": 42500,
        "property_type": "manufacturing_facility",
        "construction": "fire_resistive",
        "year_built": 1998,
        "square_footage": 85000,
        "protection_class": 3,
        "loss_history": [
            {"year": 2022, "type": "fire", "amount": 125000, "status": "closed"},
            {"year": 2023, "type": "water_damage", "amount": 18500, "status": "closed"},
        ],
        "risk_score": 62,
        "status": "under_review",
        "underwriter": "Patricia Graham",
    },
    "UW-2025-102": {
        "applicant": "Sarah Mitchell",
        "line_of_business": "personal_auto",
        "coverage_requested": 500000,
        "premium_indicated": 2400,
        "vehicle": "2024 Toyota RAV4",
        "driver_age": 34,
        "driving_record": {"violations": 0, "accidents": 0, "years_licensed": 16},
        "credit_score": 745,
        "loss_history": [],
        "risk_score": 22,
        "status": "ready_for_underwriter_review",
        "underwriter": "James Chen",
    },
    "UW-2025-103": {
        "applicant": "Downtown Medical Associates",
        "line_of_business": "professional_liability",
        "coverage_requested": 3000000,
        "premium_indicated": 67000,
        "specialty": "orthopedic_surgery",
        "practitioners": 6,
        "years_in_practice": 12,
        "claims_history": [
            {"year": 2021, "allegation": "surgical_complication", "amount": 450000, "status": "closed_record"},
            {"year": 2023, "allegation": "misdiagnosis", "amount": 0, "status": "dismissed"},
        ],
        "risk_score": 75,
        "status": "exception_review",
        "underwriter": "Patricia Graham",
    },
    "UW-2025-104": {
        "applicant": "Harbor View Restaurant Group",
        "line_of_business": "general_liability",
        "coverage_requested": 2000000,
        "premium_indicated": 18500,
        "business_type": "restaurant_chain",
        "locations": 4,
        "annual_revenue": 8500000,
        "employees": 120,
        "loss_history": [
            {"year": 2024, "type": "slip_and_fall", "amount": 35000, "status": "open"},
        ],
        "risk_score": 48,
        "status": "pending_info",
        "underwriter": "James Chen",
    },
}

UNDERWRITING_GUIDELINES = {
    "commercial_property": {
        "max_coverage": 25000000,
        "min_protection_class": 8,
        "max_building_age": 50,
        "max_loss_ratio": 60,
        "required_inspections": ["fire_protection", "electrical", "roof_condition"],
        "prohibited_risks": ["cannabis_operations", "fireworks_storage"],
    },
    "personal_auto": {
        "max_coverage": 1000000,
        "min_driver_age": 16,
        "max_violations_3yr": 3,
        "max_accidents_3yr": 2,
        "min_credit_score": 550,
        "required_documents": ["MVR", "prior_insurance_dec"],
    },
    "professional_liability": {
        "max_coverage": 10000000,
        "high_risk_specialties": ["neurosurgery", "orthopedic_surgery", "obstetrics"],
        "max_claims_5yr": 3,
        "min_years_practice": 3,
        "required_documents": ["CV", "board_certifications", "claims_history"],
    },
    "general_liability": {
        "max_coverage": 5000000,
        "max_loss_ratio": 65,
        "min_years_business": 2,
        "required_documents": ["financial_statements", "safety_program", "certificates_of_insurance"],
    },
}

PRICING_MODELS = {
    "commercial_property": {"base_rate_per_100": 0.85, "construction_factor": {"fire_resistive": 0.80, "masonry": 1.0, "frame": 1.35}, "protection_class_factor": {1: 0.75, 2: 0.80, 3: 0.90, 4: 1.0, 5: 1.10}},
    "personal_auto": {"base_premium": 1200, "age_factor": {16: 2.5, 25: 1.3, 30: 1.0, 50: 0.95, 65: 1.05}, "credit_factor": {800: 0.85, 700: 1.0, 600: 1.25, 500: 1.60}},
    "professional_liability": {"base_rate_per_practitioner": 8500, "specialty_factor": {"family_medicine": 0.60, "orthopedic_surgery": 2.10, "neurosurgery": 2.80, "obstetrics": 2.40}},
    "general_liability": {"base_rate_per_1000_revenue": 2.15, "industry_factor": {"restaurant_chain": 1.35, "office": 0.70, "retail": 1.10, "construction": 1.80}},
}

# The commercial package submission walked through in the product demo (fictional).
SUBMISSIONS = {
    "UW-2025-100": {
        "applicant": "Midwest Manufacturing Inc.",
        "industry": "Metal fabrication",
        "naics": "332312",
        "revenue": 24000000,
        "employees": 145,
        "state": "OH",
        "coverages_requested": ["GL", "Property", "Products"],
        "completeness_pct": 95,
        "missing": ["current financials", "property value confirmation"],
        "risk_flags": ["40% equipment >15 years", "single location concentration", "heavy machinery"],
        "preliminary_risk_score": 68,
        "risk_label": "Moderate",
        "dimensions": [
            {"factor": "Industry hazard", "score": 72, "note": "Metal fab = moderate"},
            {"factor": "Financial stability", "score": 78, "note": "Healthy ratios"},
            {"factor": "Loss experience", "score": 82, "note": "Better than class"},
            {"factor": "Operations", "score": 70, "note": "Equipment age concern"},
        ],
        "losses_5yr": [
            {"year": "Year -3", "type": "Products liability", "amount": 180000,
             "note": "defective bracket, QC gap addressed"},
            {"year": "Years -5 to -1", "type": "Other GL and property claims", "amount": 57000,
             "note": "minor, closed"},
        ],
        "loss_ratio": 0.42,
        "class_loss_ratio": 0.58,
        "premium_lines": [
            {"coverage": "General Liability", "limit": "$1M/$2M", "premium": 32400},
            {"coverage": "Property", "limit": "$8.2M", "premium": 28700},
            {"coverage": "Products Liability", "limit": "$1M/$2M", "premium": 18600},
            {"coverage": "Business Income", "limit": "$2M", "premium": 8400},
        ],
        "rate_adjustments": [
            {"name": "Loss experience credit", "pct": -8},
            {"name": "Equipment age", "pct": 5},
        ],
        "market_low": 82000,
        "market_high": 96000,
        "expected_loss_ratio_pct": 52,
        "target_profit_pct": 12,
        "combined_ratio_pct": 94,
        "gl_structure": "$1M occurrence, $2M aggregate, $5K deductible",
        "property_values": [
            {"item": "building", "value": 4200000},
            {"item": "contents", "value": 3400000},
            {"item": "equipment (scheduled)", "value": 600000},
        ],
        "endorsements": [
            {"endorsement": "Equipment breakdown", "reason": "Aging machinery"},
            {"endorsement": "Contingent business income", "reason": "Single location"},
            {"endorsement": "Blanket additional insured", "reason": "Contracts"},
        ],
        "subjectivities": ["Current financials", "equipment maintenance records", "QC procedures"],
        "strengths": ["Favorable loss history", "strong financials", "safety program"],
    },
}

AUTHORITY_MATRIX = {
    "underwriter_limit": 10000000,
    "rate_adequacy": "Above minimum",
    "reinsurance": "Within capacity",
    "filed_states": ["OH", "IN", "MI"],
    "quote_validity_days": 30,
}

DEFAULT_SUBMISSION = "UW-2025-100"


SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — UNDERWRITER REVIEW REQUIRED.** Fictional submissions and rating "
    "assumptions only. This is not legal, insurance, or financial advice and does not bind, quote, "
    "approve, decline, or modify coverage.\n\n"
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _risk_tier(score):
    """Map risk score to tier."""
    if score <= 30:
        return "Preferred"
    elif score <= 55:
        return "Standard"
    elif score <= 75:
        return "Substandard"
    return "Outside Stated Appetite"


def _guideline_check(app):
    """Check application against underwriting guidelines."""
    lob = app["line_of_business"]
    guidelines = UNDERWRITING_GUIDELINES.get(lob, {})
    violations = []
    if app["coverage_requested"] > guidelines.get("max_coverage", float("inf")):
        violations.append(f"Coverage ${app['coverage_requested']:,.0f} exceeds max ${guidelines['max_coverage']:,.0f}")
    if lob == "professional_liability":
        specialty = app.get("specialty", "")
        if specialty in guidelines.get("high_risk_specialties", []):
            violations.append(f"High-risk specialty: {specialty.replace('_', ' ').title()}")
        claims_count = len(app.get("claims_history", []))
        if claims_count > guidelines.get("max_claims_5yr", 99):
            violations.append(f"Claims count {claims_count} exceeds 5-year max of {guidelines['max_claims_5yr']}")
    if lob == "personal_auto":
        record = app.get("driving_record", {})
        if record.get("violations", 0) > guidelines.get("max_violations_3yr", 99):
            violations.append("Violation count exceeds guideline")
    return violations


def _sub(record_id):
    return SUBMISSIONS.get(record_id or DEFAULT_SUBMISSION, SUBMISSIONS[DEFAULT_SUBMISSION])


def _total_premium(sub):
    total = 0
    for line in sub["premium_lines"]:
        total += line["premium"]
    return total


def _net_adjustment_pct(sub):
    """Multiplicative net of the rate adjustments, one decimal (e.g. -8% and +5% -> -3.4%)."""
    factor = 1.0
    for adj in sub["rate_adjustments"]:
        factor = factor * (100 + adj["pct"]) / 100
    return round((factor - 1) * 100, 1)


def _incurred(sub):
    total = 0
    for loss in sub["losses_5yr"]:
        total += loss["amount"]
    return total


def _property_total(sub):
    total = 0
    for item in sub["property_values"]:
        total += item["value"]
    return total


def _money_short(value):
    if value >= 1000000:
        return f"${value / 1000000:g}M"
    return f"${round(value / 1000)}K"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class UnderwritingSupportAgent(BasicAgent):
    """Insurance underwriting support agent."""

    def __init__(self):
        self.name = "UnderwritingSupportAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Underwriting Support Agent",
            "description": (
                "Always call this tool for underwriter, pricing-analyst, risk-analyst, or senior-underwriter "
                "requests. Commercial submission demo flow (Midwest Manufacturing Inc., UW-2025-100, the "
                "default; no ID needed): evaluate this commercial insurance application -> "
                "submission_review; full risk assessment and loss history -> risk_assessment; what premium "
                "should we quote -> pricing_recommendation; what coverage structure -> coverage_structure; "
                "check compliance and finalize -> compliance_check; complete underwriting summary -> "
                "underwriting_summary. Queue requests "
                "requests about which submission needs the most experienced underwriter, rating factors "
                "and loss evidence, guideline exceptions or missing evidence, or preparing an exception "
                "file and checking whether a coverage decision occurred. Do not answer those workflows "
                "from general knowledge. For 'Which submission needs the most experienced underwriter, and "
                "why?', call risk_evaluation with no application_id; the synthetic queue returns "
                "UW-2025-103 as Substandard. For 'Which applications are outside a stated guideline or "
                "missing required evidence?', call guideline_check with no application_id; it returns "
                "UW-2025-103 and High-Risk Specialty. For an exception file and whether a coverage decision "
                "was made, call exception_review; it returns UW-2025-103 and the No approval boundary. Uses "
                "fictional records only and never binds, quotes, approves, "
                "declines, or changes coverage. All conclusions are nonbinding decision support for an "
                "authorized underwriter and require explicit human review."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "For the Midwest Manufacturing commercial submission (default): "
                            "submission_review to evaluate the application; risk_assessment for the "
                            "full four-factor risk assessment and loss history; pricing_recommendation "
                            "for the premium to quote; coverage_structure for limits, deductibles and "
                            "endorsements; compliance_check to check compliance / authority and "
                            "finalize; underwriting_summary for the complete underwriting summary. "
                            "Choose risk_evaluation for the submission queue, highest-risk case, which "
                            "submission needs an experienced underwriter, risk scores, or tiers; omit "
                            "application_id for that queue-wide request so UW-2025-103 and its Substandard "
                            "tier are returned. Choose "
                            "pricing_recommendation for the premium to quote (Midwest by default) or, with "
                            "an application_id, rating factors, indicated premium and loss evidence (e.g. "
                            "Riverside) without issuing a quote. Choose guideline_check for applications "
                            "outside a stated guideline, required documents, inspections, or missing "
                            "evidence; omit application_id so the queue includes UW-2025-103 and High-Risk "
                            "Specialty. Choose exception_review for the exception file, senior review paths, "
                            "or whether any coverage decision was made; the output states No approval."
                        ),
                        "enum": [
                            "risk_evaluation",
                            "pricing_recommendation",
                            "guideline_check",
                            "exception_review",
                            "submission_review",
                            "risk_assessment",
                            "coverage_structure",
                            "compliance_check",
                            "underwriting_summary",
                        ],
                    },
                    "application_id": {
                        "type": "string",
                        "description": (
                            "Synthetic application mapping: Midwest Manufacturing is UW-2025-100 (default "
                            "for the commercial submission flow); Riverside Manufacturing is UW-2025-101; "
                            "Sarah Mitchell is UW-2025-102; Downtown Medical Associates, the orthopedic "
                            "submission, highest-risk submission, or exception file is UW-2025-103; Harbor "
                            "View Restaurant Group is UW-2025-104. Omit for queue-wide and guideline-wide reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("application_id")
        if record_id and record_id not in APPLICATIONS and record_id not in SUBMISSIONS:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        operation = kwargs.get("operation", "risk_evaluation")
        dispatch = {
            "risk_evaluation": self._risk_evaluation,
            "pricing_recommendation": self._pricing_recommendation,
            "guideline_check": self._guideline_check,
            "exception_review": self._exception_review,
            "submission_review": self._submission_review,
            "risk_assessment": self._risk_assessment,
            "coverage_structure": self._coverage_structure,
            "compliance_check": self._compliance_check,
            "underwriting_summary": self._underwriting_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(**kwargs)

    # ── commercial submission flow (video turns 1-6) ───────────
    def _submission_review(self, **kwargs) -> str:
        app_id = kwargs.get("application_id") if kwargs.get("application_id") in SUBMISSIONS else DEFAULT_SUBMISSION
        sub = _sub(app_id)
        return "\n".join([
            f"# Submission Review: {sub['applicant']} ({app_id})\n",
            f"Analyzed the {sub['applicant']} application - {sub['risk_label'].lower()} risk with attention areas.\n",
            "| Field | Details |",
            "|---|---|",
            f"| Applicant | {sub['applicant']} |",
            f"| Industry | {sub['industry']} (NAICS {sub['naics']}) |",
            f"| Revenue | {_money_short(sub['revenue'])}, {sub['employees']} employees |",
            f"| Coverage | {', '.join(sub['coverages_requested'])} |",
            f"| State | {sub['state']} |",
            "",
            f"**Completeness:** {sub['completeness_pct']}% complete, need {' and '.join(sub['missing'])}",
            f"**Risk Flags:** {', '.join(sub['risk_flags'])}",
            f"**Preliminary Risk Score:** {sub['preliminary_risk_score']}/100 ({sub['risk_label']})",
            "",
            "Source: [Application Portal (synthetic)]",
            "",
            "See detailed risk and loss history?",
        ])

    def _risk_assessment(self, **kwargs) -> str:
        app_id = kwargs.get("application_id") if kwargs.get("application_id") in SUBMISSIONS else DEFAULT_SUBMISSION
        sub = _sub(app_id)
        lines = [
            f"# Risk Assessment: {sub['applicant']} ({app_id})\n",
            "Risk assessment complete - favorable loss history with one notable claim.\n",
            "| Risk Factor | Score | Notes |",
            "|---|---|---|",
        ]
        for d in sub["dimensions"]:
            lines.append(f"| {d['factor']} | {d['score']}/100 | {d['note']} |")
        notable = sub["losses_5yr"][0]
        lines.extend([
            "",
            f"**5-Year Loss History:** Total incurred {_money_short(_incurred(sub))} (below the class average)",
            f"**Notable Claim:** {notable['year']} {notable['type'].lower()} {_money_short(notable['amount'])} ({notable['note']})",
            f"**Benchmark:** Loss ratio {sub['loss_ratio']:.2f} vs class {sub['class_loss_ratio']:.2f} (better than average)",
            f"**Preliminary Risk Score:** {sub['preliminary_risk_score']}/100 ({sub['risk_label']})",
            "",
            "Source: [Claims Database (synthetic)]",
            "",
            "Generate pricing?",
        ])
        return "\n".join(lines)

    def _package_premium(self, app_id) -> str:
        sub = _sub(app_id)
        total = _total_premium(sub)
        lines = [
            f"# Premium Recommendation: {sub['applicant']} ({app_id})\n",
            f"Premium recommendation: ${total:,} annual package - competitive positioning "
            "(an indication for underwriter judgment; no quote is issued).\n",
            "| Coverage | Limit | Premium |",
            "|---|---|---|",
        ]
        for line in sub["premium_lines"]:
            lines.append(f"| {line['coverage']} | {line['limit']} | ${line['premium']:,} |")
        lines.append(f"| **Total package** | | **${total:,}** |")
        adj = ", ".join(f"{a['name'].lower() if i else a['name']} {a['pct']:+d}%" for i, a in enumerate(sub["rate_adjustments"]))
        lines.extend([
            "",
            f"**Rate Adjustments:** {adj}, net {_net_adjustment_pct(sub):+g}% (multiplicative)",
            f"**Market Position:** ${total:,} vs market low {_money_short(sub['market_low'])}, high "
            f"{_money_short(sub['market_high'])} (competitive mid-range)",
            f"**Margin:** Expected loss ratio {sub['expected_loss_ratio_pct']}%, target profit "
            f"{sub['target_profit_pct']}%, combined ratio {sub['combined_ratio_pct']}%",
            "",
            "Source: [Rating Engine (synthetic)]",
            "",
            "Review coverage structure?",
        ])
        return "\n".join(lines)

    def _coverage_structure(self, **kwargs) -> str:
        app_id = kwargs.get("application_id") if kwargs.get("application_id") in SUBMISSIONS else DEFAULT_SUBMISSION
        sub = _sub(app_id)
        parts = ", ".join(f"{p['item']} {_money_short(p['value'])}" for p in sub["property_values"])
        lines = [
            f"# Recommended Coverage Structure: {sub['applicant']} ({app_id})\n",
            "Coverage structure designed for the manufacturing risk profile (recommendation for the underwriter).\n",
            f"**General Liability:** {sub['gl_structure']}",
            f"**Property Coverage:** {_money_short(_property_total(sub))} total ({parts})",
            "",
            "**Recommended Endorsements:**",
            "",
            "| Endorsement | Reason |",
            "|---|---|",
        ]
        for e in sub["endorsements"]:
            lines.append(f"| {e['endorsement']} | {e['reason']} |")
        lines.extend([
            "",
            f"**Subjectivities:** {', '.join(sub['subjectivities'])}",
            "",
            "Source: [Product Library (synthetic)]",
            "",
            "Run compliance check?",
        ])
        return "\n".join(lines)

    def _compliance_check(self, **kwargs) -> str:
        app_id = kwargs.get("application_id") if kwargs.get("application_id") in SUBMISSIONS else DEFAULT_SUBMISSION
        sub = _sub(app_id)
        auth = AUTHORITY_MATRIX
        tiv = _property_total(sub)
        within = tiv <= auth["underwriter_limit"]
        filed = sub["state"] in auth["filed_states"]
        lines = [
            f"# Compliance and Authority Check: {sub['applicant']} ({app_id})\n",
            f"Compliance validated - {'within' if within else 'outside'} authority, ready for your quote decision.\n",
            "| Check | Status |",
            "|---|---|",
            f"| Underwriting authority | {'Within' if within else 'Exceeds'} {_money_short(auth['underwriter_limit'])} limit |",
            f"| Rate adequacy | {auth['rate_adequacy']} |",
            f"| Reinsurance treaty | {auth['reinsurance']} |",
            f"| State filing | {sub['state']} rates {'filed' if filed else 'not filed'} |",
            "",
            "**Approval:** " + ("Within your binding authority, no referral required; the bind decision is yours."
                                if within else "Referral to a senior underwriter required."),
            f"**Subjectivities Before Binding:** {', '.join(sub['subjectivities'])}",
            f"**Quote Validity:** {auth['quote_validity_days']} days",
            "",
            "Source: [Authority Matrix (synthetic)]",
            "",
            "Generate underwriting summary?",
        ]
        return "\n".join(lines)

    def _underwriting_summary(self, **kwargs) -> str:
        app_id = kwargs.get("application_id") if kwargs.get("application_id") in SUBMISSIONS else DEFAULT_SUBMISSION
        sub = _sub(app_id)
        total = _total_premium(sub)
        within = _property_total(sub) <= AUTHORITY_MATRIX["underwriter_limit"]
        return "\n".join([
            f"# Underwriting Summary: {sub['applicant']} ({app_id})\n",
            f"Recommendation for the underwriter: approve with conditions, ${total:,} premium.\n",
            "| Decision Detail | Value |",
            "|---|---|",
            "| Recommendation | Approve with conditions (underwriter decision) |",
            f"| Risk score | {sub['preliminary_risk_score']}/100 ({sub['risk_label']}) |",
            f"| Premium | ${total:,} |",
            f"| Authority | {'Within limits' if within else 'Referral required'} |",
            "",
            f"**Strengths:** {', '.join(sub['strengths'])}",
            f"**Conditions for Binding:** {', '.join(sub['subjectivities'])}",
            "**Quote Package:** drafted for you to issue - letter, coverage summary, subjectivities listed",
            "",
            "Source: [All Underwriting Systems (synthetic)]",
        ])

    def _risk_evaluation(self, **kwargs) -> str:
        lines = ["# Underwriting Risk Evaluation\n"]
        lines.append("| App ID | Applicant | LOB | Coverage | Risk Score | Tier | Status |")
        lines.append("|---|---|---|---|---|---|---|")
        for aid, app in APPLICATIONS.items():
            tier = _risk_tier(app["risk_score"])
            lines.append(
                f"| {aid} | {app['applicant']} | {app['line_of_business'].replace('_', ' ').title()} "
                f"| ${app['coverage_requested']:,.0f} | {app['risk_score']} | {tier} | {app['status'].replace('_', ' ').title()} |"
            )
        lines.append("\n## Risk Tier Definitions\n")
        lines.append("- **Preferred** (0-30): Best rates, minimal restrictions")
        lines.append("- **Standard** (31-55): Standard rates and terms")
        lines.append("- **Substandard** (56-75): Rate surcharge or coverage restrictions")
        lines.append("- **Outside Stated Appetite** (76+): Requires authorized underwriting review")
        return "\n".join(lines)

    def _pricing_recommendation(self, **kwargs) -> str:
        app_id = kwargs.get("application_id") or DEFAULT_SUBMISSION
        if app_id in SUBMISSIONS:
            return self._package_premium(app_id)
        app = APPLICATIONS.get(app_id, list(APPLICATIONS.values())[0])
        tier = _risk_tier(app["risk_score"])
        lines = [f"# Illustrative Pricing-Factor Review: {app_id}\n"]
        lines.append(f"- **Applicant:** {app['applicant']}")
        lines.append(f"- **LOB:** {app['line_of_business'].replace('_', ' ').title()}")
        lines.append(f"- **Coverage:** ${app['coverage_requested']:,.0f}")
        lines.append(f"- **Indicated Premium:** ${app['premium_indicated']:,.0f}")
        lines.append(f"- **Risk Score:** {app['risk_score']} ({tier})\n")
        model = PRICING_MODELS.get(app["line_of_business"], {})
        lines.append("## Pricing Model Factors\n")
        for factor, values in model.items():
            if isinstance(values, dict):
                lines.append(f"### {factor.replace('_', ' ').title()}\n")
                for k, v in values.items():
                    lines.append(f"- {k}: {v}")
            else:
                lines.append(f"- **{factor.replace('_', ' ').title()}:** {values}")
        lines.append(f"\n## Loss History\n")
        losses = app.get("loss_history", app.get("claims_history", []))
        if losses:
            lines.append("| Year | Type/Allegation | Amount | Status |")
            lines.append("|---|---|---|---|")
            for loss in losses:
                loss_type = loss.get("type", loss.get("allegation", "N/A"))
                lines.append(f"| {loss['year']} | {loss_type.replace('_', ' ').title()} | ${loss['amount']:,.0f} | {loss['status'].title()} |")
        else:
            lines.append("No loss history.")
        return "\n".join(lines)

    def _guideline_check(self, **kwargs) -> str:
        lines = ["# Underwriting Guideline Check\n"]
        for aid, app in APPLICATIONS.items():
            violations = _guideline_check(app)
            lob = app["line_of_business"]
            guidelines = UNDERWRITING_GUIDELINES.get(lob, {})
            status = "No Stated Exception" if not violations else "Exceptions Noted"
            lines.append(f"## {aid}: {app['applicant']} — {status}\n")
            lines.append(f"- **LOB:** {lob.replace('_', ' ').title()}")
            lines.append(f"- **Max Coverage:** ${guidelines.get('max_coverage', 0):,.0f}")
            if guidelines.get("required_documents"):
                lines.append(f"- **Required Documents:** {', '.join(guidelines['required_documents'])}")
            if guidelines.get("required_inspections"):
                lines.append(f"- **Required Inspections:** {', '.join(guidelines['required_inspections'])}")
            if violations:
                lines.append("\n**Violations:**\n")
                for v in violations:
                    lines.append(f"- {v}")
            lines.append("")
        return "\n".join(lines)

    def _exception_review(self, **kwargs) -> str:
        exceptions = {k: v for k, v in APPLICATIONS.items() if v["status"] == "exception_review"}
        lines = ["# Exception Review Queue\n"]
        if not exceptions:
            lines.append("No applications currently in exception review.")
            return "\n".join(lines)
        for aid, app in exceptions.items():
            tier = _risk_tier(app["risk_score"])
            violations = _guideline_check(app)
            lines.append(f"## {aid}: {app['applicant']}\n")
            lines.append(f"- **LOB:** {app['line_of_business'].replace('_', ' ').title()}")
            lines.append(f"- **Coverage:** ${app['coverage_requested']:,.0f}")
            lines.append(f"- **Premium:** ${app['premium_indicated']:,.0f}")
            lines.append(f"- **Risk Score:** {app['risk_score']} ({tier})")
            lines.append(f"- **Underwriter:** {app['underwriter']}\n")
            if violations:
                lines.append("### Guideline Exceptions\n")
                for v in violations:
                    lines.append(f"- {v}")
            lines.append("\n### Human Review Paths\n")
            lines.append("1. Validate missing evidence and authority limits")
            lines.append("2. Obtain actuarial or senior-underwriter review of rating assumptions")
            lines.append("3. Document whether the risk falls within stated appetite")
            lines.append("4. Request additional information before any coverage decision\n")
            lines.append("No approval, decline, quote, or binder has been issued.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = UnderwritingSupportAgent()
    for op in ["submission_review", "risk_assessment", "pricing_recommendation", "coverage_structure",
               "compliance_check", "underwriting_summary"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="risk_evaluation"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="pricing_recommendation", application_id="UW-2025-103"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="guideline_check"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="exception_review"))
