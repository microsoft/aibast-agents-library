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
    "description": "Insurance underwriting support with risk evaluation, pricing recommendations, guideline compliance, and exception review.",
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
        "status": "approved",
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
            {"year": 2021, "allegation": "surgical_complication", "amount": 450000, "status": "settled"},
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
    return "Decline"


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


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class UnderwritingSupportAgent(BasicAgent):
    """Insurance underwriting support agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/underwriting-support"
        self.metadata = {
            "name": self.name,
            "display_name": "Underwriting Support Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "risk_evaluation",
                            "pricing_recommendation",
                            "guideline_check",
                            "exception_review",
                        ],
                    },
                    "application_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "risk_evaluation")
        dispatch = {
            "risk_evaluation": self._risk_evaluation,
            "pricing_recommendation": self._pricing_recommendation,
            "guideline_check": self._guideline_check,
            "exception_review": self._exception_review,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

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
        lines.append("- **Decline** (76+): Outside risk appetite")
        return "\n".join(lines)

    def _pricing_recommendation(self, **kwargs) -> str:
        app_id = kwargs.get("application_id", "UW-2025-101")
        app = APPLICATIONS.get(app_id, list(APPLICATIONS.values())[0])
        tier = _risk_tier(app["risk_score"])
        lines = [f"# Pricing Recommendation: {app_id}\n"]
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
            status = "Compliant" if not violations else "Exceptions Noted"
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
            lines.append("\n### Exception Decision Options\n")
            lines.append("1. **Approve with conditions** — Accept risk with additional terms")
            lines.append("2. **Approve with surcharge** — Accept at higher premium")
            lines.append("3. **Decline** — Risk outside appetite")
            lines.append("4. **Request additional information** — Need more underwriting data\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = UnderwritingSupportAgent()
    print(agent.perform(operation="risk_evaluation"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="pricing_recommendation", application_id="UW-2025-103"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="guideline_check"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="exception_review"))
