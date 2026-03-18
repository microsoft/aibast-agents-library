"""
Financial Services Customer Onboarding Agent — Financial Services Stack

Manages KYC verification, account setup, document checklists, and
onboarding status tracking for financial institution customer onboarding.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fs-customer-onboarding",
    "version": "1.0.0",
    "display_name": "FS Customer Onboarding Agent",
    "description": "Financial services customer onboarding with KYC verification, account setup, document checklists, and status tracking.",
    "author": "AIBAST",
    "tags": ["KYC", "onboarding", "account-setup", "compliance", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CUSTOMER_APPLICATIONS = {
    "APP-6001": {
        "applicant": "Sarah Chen",
        "application_type": "individual",
        "account_requested": "premium_checking",
        "submitted": "2025-02-20",
        "status": "kyc_in_progress",
        "risk_rating": "low",
        "relationship_manager": "Michael Torres",
        "estimated_assets": 250000,
    },
    "APP-6002": {
        "applicant": "Blackwood Capital Partners LLC",
        "application_type": "business",
        "account_requested": "commercial_checking",
        "submitted": "2025-02-25",
        "status": "document_review",
        "risk_rating": "medium",
        "relationship_manager": "Jessica Nguyen",
        "estimated_assets": 2400000,
    },
    "APP-6003": {
        "applicant": "Ahmed Al-Rashid",
        "application_type": "individual",
        "account_requested": "wealth_management",
        "submitted": "2025-03-01",
        "status": "enhanced_due_diligence",
        "risk_rating": "high",
        "relationship_manager": "Jessica Nguyen",
        "estimated_assets": 5800000,
    },
    "APP-6004": {
        "applicant": "Maria Fontaine",
        "application_type": "individual",
        "account_requested": "basic_savings",
        "submitted": "2025-03-05",
        "status": "approved",
        "risk_rating": "low",
        "relationship_manager": "Michael Torres",
        "estimated_assets": 15000,
    },
}

KYC_DOCUMENTS = {
    "individual": [
        {"document": "Government-issued photo ID", "required": True},
        {"document": "Social Security Number verification", "required": True},
        {"document": "Proof of address (utility bill or bank statement)", "required": True},
        {"document": "W-9 Tax Form", "required": True},
        {"document": "Source of funds documentation", "required": False},
    ],
    "business": [
        {"document": "Articles of Incorporation / Formation", "required": True},
        {"document": "EIN verification letter", "required": True},
        {"document": "Certificate of Good Standing", "required": True},
        {"document": "Operating Agreement / Bylaws", "required": True},
        {"document": "Beneficial ownership declaration (FinCEN BOI)", "required": True},
        {"document": "Government ID for all authorized signers", "required": True},
        {"document": "Business license", "required": False},
        {"document": "Financial statements (last 2 years)", "required": False},
    ],
}

VERIFICATION_STATUS = {
    "APP-6001": {
        "id_verification": "complete",
        "ssn_verification": "complete",
        "address_verification": "pending",
        "ofac_screening": "clear",
        "pep_screening": "clear",
        "adverse_media": "clear",
    },
    "APP-6002": {
        "id_verification": "complete",
        "ein_verification": "complete",
        "beneficial_ownership": "in_progress",
        "ofac_screening": "clear",
        "pep_screening": "clear",
        "adverse_media": "clear",
    },
    "APP-6003": {
        "id_verification": "complete",
        "ssn_verification": "complete",
        "address_verification": "complete",
        "ofac_screening": "clear",
        "pep_screening": "flagged",
        "adverse_media": "review_needed",
        "source_of_wealth": "pending",
    },
    "APP-6004": {
        "id_verification": "complete",
        "ssn_verification": "complete",
        "address_verification": "complete",
        "ofac_screening": "clear",
        "pep_screening": "clear",
        "adverse_media": "clear",
    },
}

ACCOUNT_TYPES = {
    "basic_savings": {"min_deposit": 25, "monthly_fee": 0, "apy": 0.50, "features": ["Online banking", "Mobile deposit", "ATM access"]},
    "premium_checking": {"min_deposit": 1000, "monthly_fee": 12, "apy": 0.15, "features": ["No ATM fees", "Overdraft protection", "Bill pay", "Cashback rewards"]},
    "commercial_checking": {"min_deposit": 5000, "monthly_fee": 25, "apy": 0.10, "features": ["Treasury management", "ACH origination", "Wire transfers", "Merchant services"]},
    "wealth_management": {"min_deposit": 250000, "monthly_fee": 0, "apy": 1.25, "features": ["Dedicated advisor", "Investment management", "Trust services", "Concierge banking"]},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _kyc_completion_pct(app_id):
    """Calculate KYC verification completion percentage."""
    status = VERIFICATION_STATUS.get(app_id, {})
    if not status:
        return 0.0
    total = len(status)
    complete = sum(1 for v in status.values() if v == "complete" or v == "clear")
    return round((complete / total) * 100, 1)


def _onboarding_pipeline():
    """Summarize onboarding pipeline metrics."""
    by_status = {}
    for app in CUSTOMER_APPLICATIONS.values():
        by_status[app["status"]] = by_status.get(app["status"], 0) + 1
    total_assets = sum(app["estimated_assets"] for app in CUSTOMER_APPLICATIONS.values())
    return {"count": len(CUSTOMER_APPLICATIONS), "by_status": by_status, "total_assets": total_assets}


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class FSCustomerOnboardingAgent(BasicAgent):
    """Financial services customer onboarding agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/fs-customer-onboarding"
        self.metadata = {
            "name": self.name,
            "display_name": "FS Customer Onboarding Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "kyc_verification",
                            "account_setup",
                            "document_checklist",
                            "onboarding_status",
                        ],
                    },
                    "application_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "onboarding_status")
        dispatch = {
            "kyc_verification": self._kyc_verification,
            "account_setup": self._account_setup,
            "document_checklist": self._document_checklist,
            "onboarding_status": self._onboarding_status,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _kyc_verification(self, **kwargs) -> str:
        app_id = kwargs.get("application_id")
        if app_id and app_id in CUSTOMER_APPLICATIONS:
            app = CUSTOMER_APPLICATIONS[app_id]
            verification = VERIFICATION_STATUS.get(app_id, {})
            pct = _kyc_completion_pct(app_id)
            lines = [f"# KYC Verification: {app_id}\n"]
            lines.append(f"- **Applicant:** {app['applicant']}")
            lines.append(f"- **Type:** {app['application_type'].title()}")
            lines.append(f"- **Risk Rating:** {app['risk_rating'].title()}")
            lines.append(f"- **KYC Progress:** {pct}%\n")
            lines.append("## Verification Checks\n")
            lines.append("| Check | Status |")
            lines.append("|---|---|")
            for check, status in verification.items():
                display = check.replace("_", " ").title()
                lines.append(f"| {display} | {status.replace('_', ' ').title()} |")
            if app["risk_rating"] == "high":
                lines.append("\n## Enhanced Due Diligence Required\n")
                lines.append("- Source of wealth verification")
                lines.append("- PEP relationship documentation")
                lines.append("- Enhanced transaction monitoring parameters")
            return "\n".join(lines)

        lines = ["# KYC Verification Summary\n"]
        lines.append("| App ID | Applicant | Risk | KYC Progress | Status |")
        lines.append("|---|---|---|---|---|")
        for aid, app in CUSTOMER_APPLICATIONS.items():
            pct = _kyc_completion_pct(aid)
            lines.append(
                f"| {aid} | {app['applicant']} | {app['risk_rating'].title()} "
                f"| {pct}% | {app['status'].replace('_', ' ').title()} |"
            )
        return "\n".join(lines)

    def _account_setup(self, **kwargs) -> str:
        lines = ["# Account Setup Reference\n"]
        lines.append("| Account Type | Min Deposit | Monthly Fee | APY | Features |")
        lines.append("|---|---|---|---|---|")
        for acct_type, details in ACCOUNT_TYPES.items():
            features = ", ".join(details["features"][:3])
            lines.append(
                f"| {acct_type.replace('_', ' ').title()} | ${details['min_deposit']:,.0f} "
                f"| ${details['monthly_fee']:,.0f} | {details['apy']}% | {features} |"
            )
        lines.append("\n## Pending Account Setups\n")
        approved = {k: v for k, v in CUSTOMER_APPLICATIONS.items() if v["status"] == "approved"}
        if approved:
            for aid, app in approved.items():
                acct = ACCOUNT_TYPES.get(app["account_requested"], {})
                lines.append(f"### {aid}: {app['applicant']}\n")
                lines.append(f"- **Account:** {app['account_requested'].replace('_', ' ').title()}")
                lines.append(f"- **Min Deposit:** ${acct.get('min_deposit', 0):,.0f}")
                lines.append(f"- **Features:** {', '.join(acct.get('features', []))}\n")
        else:
            lines.append("No applications pending account setup.")
        return "\n".join(lines)

    def _document_checklist(self, **kwargs) -> str:
        app_id = kwargs.get("application_id", "APP-6001")
        app = CUSTOMER_APPLICATIONS.get(app_id, list(CUSTOMER_APPLICATIONS.values())[0])
        app_type = app["application_type"]
        docs = KYC_DOCUMENTS.get(app_type, [])
        lines = [f"# Document Checklist: {app_id}\n"]
        lines.append(f"**Applicant:** {app['applicant']}")
        lines.append(f"**Type:** {app_type.title()}\n")
        lines.append("## Required Documents\n")
        for doc in docs:
            req = " (Required)" if doc["required"] else " (Optional)"
            lines.append(f"- [ ] {doc['document']}{req}")
        lines.append("\n## Compliance Notes\n")
        lines.append("- All documents must be current (within 90 days)")
        lines.append("- Copies must be certified or notarized for business accounts")
        lines.append("- BSA/AML requirements apply to all account openings")
        lines.append("- CIP (Customer Identification Program) verification mandatory")
        return "\n".join(lines)

    def _onboarding_status(self, **kwargs) -> str:
        pipeline = _onboarding_pipeline()
        lines = ["# Customer Onboarding Pipeline\n"]
        lines.append(f"**Applications:** {pipeline['count']}")
        lines.append(f"**Total Estimated Assets:** ${pipeline['total_assets']:,.0f}\n")
        lines.append("## Pipeline Status\n")
        for status, count in pipeline["by_status"].items():
            lines.append(f"- {status.replace('_', ' ').title()}: {count}")
        lines.append("\n## Application Details\n")
        lines.append("| App ID | Applicant | Account | Risk | Est. Assets | Status | RM |")
        lines.append("|---|---|---|---|---|---|---|")
        for aid, app in CUSTOMER_APPLICATIONS.items():
            lines.append(
                f"| {aid} | {app['applicant']} | {app['account_requested'].replace('_', ' ').title()} "
                f"| {app['risk_rating'].title()} | ${app['estimated_assets']:,.0f} "
                f"| {app['status'].replace('_', ' ').title()} | {app['relationship_manager']} |"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FSCustomerOnboardingAgent()
    print(agent.perform(operation="onboarding_status"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="kyc_verification", application_id="APP-6003"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="account_setup"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="document_checklist", application_id="APP-6002"))
