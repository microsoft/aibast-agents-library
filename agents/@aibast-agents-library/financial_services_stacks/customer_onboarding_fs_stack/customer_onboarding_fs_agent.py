"""
Financial Services Customer Onboarding Agent — Financial Services Stack

Manages KYC verification, account setup, document checklists, and
onboarding status tracking for financial institution customer onboarding.

The demo scenario is the corporate onboarding of Nexus Industries Inc.
(APP-6005) for commercial banking: initiation, company verification,
beneficial ownership, documents, product provisioning plan, timeline,
risk review and a status summary. All records are synthetic.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/fs-customer-onboarding",
    "version": "1.1.0",
    "display_name": "Customer Onboarding Agent",
    "description": "Orchestrate client onboarding journeys with unified workflows to accelerate revenue and mitigate compliance risk.",
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

DEMO_APPLICATION = "APP-6005"

CUSTOMER_APPLICATIONS = {
    "APP-6001": {
        "applicant": "Elena Brooks",
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
        "status": "setup_review_ready",
        "risk_rating": "low",
        "relationship_manager": "Michael Torres",
        "estimated_assets": 15000,
    },
    "APP-6005": {
        "applicant": "Nexus Industries Inc.",
        "application_type": "business",
        "account_requested": "commercial_banking_suite",
        "products_requested": ["Treasury management", "Credit line", "Foreign exchange (FX)"],
        "submitted": "2025-03-10",
        "status": "kyc_in_progress",
        "risk_rating": "low",
        "priority": "HIGH - Strategic relationship",
        "annual_revenue_potential": 8000000,
        "crm_case": "ONB-2025-4782",
        "relationship_manager": "Jessica Nguyen",
        "estimated_assets": 12000000,
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
    "APP-6005": {
        "corporate_registration": "complete",
        "articles_of_incorporation": "complete",
        "financial_statements": "complete",
        "ofac_screening": "clear",
        "enhanced_due_diligence": "in_progress",
    },
}

ACCOUNT_TYPES = {
    "basic_savings": {"min_deposit": 25, "monthly_fee": 0, "apy": 0.50, "features": ["Online banking", "Mobile deposit", "ATM access"]},
    "premium_checking": {"min_deposit": 1000, "monthly_fee": 12, "apy": 0.15, "features": ["No ATM fees", "Overdraft protection", "Bill pay", "Cashback rewards"]},
    "commercial_checking": {"min_deposit": 5000, "monthly_fee": 25, "apy": 0.10, "features": ["Treasury management", "ACH origination", "Wire transfers", "Merchant services"]},
    "wealth_management": {"min_deposit": 250000, "monthly_fee": 0, "apy": 1.25, "features": ["Dedicated advisor", "Investment management", "Trust services", "Concierge banking"]},
    "commercial_banking_suite": {"min_deposit": 25000, "monthly_fee": 150, "apy": 0.20, "features": ["Commercial DDA", "Treasury management (ACH, wires, positive pay)", "Credit line", "FX spot and forward contracts"]},
}

CORPORATE_PROFILES = {
    "APP-6005": {
        "legal_entity": "Nexus Industries Inc.",
        "incorporation": "Delaware C-Corp",
        "ein": "88-1234567",
        "industry": "Advanced Manufacturing (NAICS 332710)",
        "sector": "advanced manufacturing",
        "annual_revenue": 125000000,
        "years_in_business": 17,
        "corporate_registration": "Verified via Secretary of State database",
        "financial_statements": "3 years reviewed - strong financials",
        "credit_rating": "BBB+ (S&P equivalent)",
        "ofac_screening": "CLEAR - no matches",
        "enhanced_due_diligence": "In progress (high-value client)",
    },
}

BENEFICIAL_OWNERS = {
    "APP-6005": [
        {"name": "Sarah Morrison", "ownership_pct": 45, "status": "verified", "note": "Government-issued ID verified"},
        {"name": "David Park", "ownership_pct": 30, "status": "verified", "note": "Government-issued ID verified"},
        {"name": "Marcus Chen", "ownership_pct": 25, "status": "pending", "note": "Passport verification processing, expected within 2 hours"},
    ],
}

DOCUMENT_STATUS = {
    "APP-6005": [
        {"document": "Corporate resolution", "status": "received", "note": "Received and verified"},
        {"document": "Articles of Incorporation", "status": "received", "note": "Authenticated"},
        {"document": "Financial statements", "status": "received", "note": "3 years reviewed (2022-2024)"},
        {"document": "Certificate of Good Standing", "status": "received", "note": "Received from Delaware"},
        {"document": "Operating agreement", "status": "received", "note": "Received and reviewed"},
        {"document": "Insurance certificates", "status": "received", "note": "D&O and liability verified"},
        {"document": "EIN verification letter", "status": "received", "note": "Matches EIN 88-1234567"},
        {"document": "Government ID for authorized signers", "status": "received", "note": "3 signers on file"},
        {"document": "Business license", "status": "received", "note": "Current"},
        {"document": "Beneficial ownership certification form", "status": "pending", "note": "Awaiting Marcus Chen"},
        {"document": "W-9 tax form", "status": "pending", "note": "Pending signature"},
        {"document": "Board authorization", "status": "pending", "note": "Pending for online banking access"},
    ],
}

PROVISIONING_PLANS = {
    "APP-6005": [
        {"item": "Operating account", "detail": "Commercial DDA ****7823 reserved", "status": "ready"},
        {"item": "Treasury management", "detail": "ACH, wires, positive pay configured", "status": "ready"},
        {"item": "Credit line", "detail": "$5M pre-approved; credit committee review Day 2 (tomorrow) 2 PM; expected approval (strong financials)", "status": "pending"},
        {"item": "FX services", "detail": "Spot and forward contracts, $10M monthly aggregate limit", "status": "ready"},
        {"item": "Online and mobile banking", "detail": "3 admin users configured; corporate mobile app access", "status": "ready"},
    ],
}

ONBOARDING_TIMELINES = {
    "APP-6005": {
        "steps": [
            ("Day 1 (Today)", "Complete beneficial ownership verification"),
            ("Day 2 (Tomorrow)", "Credit committee review at 2 PM"),
            ("Day 3", "Signature cards and service agreements"),
            ("Day 4", "Final compliance sign-offs and testing"),
            ("Day 5", "Full account activation - go live"),
            ("Week 2", "Relationship manager introduction call"),
        ],
        "business_days": 5,
        "industry_days_low": 15,
        "industry_days_high": 21,
        "success_probability_pct": 95,
    },
}

RISK_NOTES = {
    "APP-6005": {
        "summary": "No significant red flags detected",
        "screening": "All screening results clean (OFAC, PEP, EU sanctions)",
        "financials": "Strong financial position with positive cash flow (credit rating BBB+)",
        "industry_risk": "Moderate-low for advanced manufacturing",
        "minor_note": "International suppliers in Asia may require occasional OFAC screening on wire transfers; standard for the industry and handled by routine wire screening",
    },
}

SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — HUMAN REVIEW REQUIRED.** Fictional records only. "
    "This output is operational decision support, not legal, compliance, or financial advice. "
    "It does not verify a real identity, approve an application, provision an account, or complete a transaction.\n\n"
)


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


def _pct(done, total):
    return round(done * 100 / total) if total else 0


def _cip_pct(app_id):
    owners = BENEFICIAL_OWNERS.get(app_id, [])
    return _pct(sum(1 for o in owners if o["status"] == "verified"), len(owners))


def _doc_pct(app_id):
    docs = DOCUMENT_STATUS.get(app_id, [])
    return _pct(sum(1 for d in docs if d["status"] == "received"), len(docs))


def _prov_pct(app_id):
    items = PROVISIONING_PLANS.get(app_id, [])
    return _pct(sum(1 for i in items if i["status"] == "ready"), len(items))


def _faster_pct(app_id):
    t = ONBOARDING_TIMELINES[app_id]
    return _pct(t["industry_days_low"] - t["business_days"], t["industry_days_low"])


def _onboarding_pipeline():
    """Summarize onboarding pipeline metrics."""
    by_status = {}
    for app in CUSTOMER_APPLICATIONS.values():
        by_status[app["status"]] = by_status.get(app["status"], 0) + 1
    total_assets = sum(app["estimated_assets"] for app in CUSTOMER_APPLICATIONS.values())
    return {"count": len(CUSTOMER_APPLICATIONS), "by_status": by_status, "total_assets": total_assets}


def _money_m(value):
    m = value / 1000000
    return f"${m:g}M"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "kyc_verification",
    "account_setup",
    "document_checklist",
    "onboarding_status",
    "initiate_onboarding",
    "beneficial_ownership",
    "onboarding_timeline",
    "risk_assessment",
    "status_summary",
]


class FSCustomerOnboardingAgent(BasicAgent):
    """Financial services customer onboarding agent."""

    def __init__(self):
        self.name = "FSCustomerOnboardingAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "FS Customer Onboarding Agent",
            "description": (
                "Always call this tool for onboarding-specialist, relationship-manager, or compliance "
                "requests about onboarding a new corporate client (the demo client is Nexus Industries, "
                "APP-6005, commercial banking with treasury, credit line and FX), company profile and "
                "legitimacy, enhanced due diligence, KYC or PEP checks, beneficial ownership and FinCEN, "
                "documentation collected, product setup and provisioning, activation timeline, risks or red "
                "flags, a status summary, which file is ready for account setup review, a business "
                "onboarding document list for Blackwood, or where the onboarding queue is stuck. Do not "
                "answer those workflows from general knowledge. Uses fictional records only; it never "
                "verifies identity, approves an applicant, opens or provisions an account, sends a message, "
                "or provides legal, compliance, or financial advice. Every result requires authorized human review."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose initiate_onboarding to start onboarding a new corporate client (Nexus "
                            "Industries); kyc_verification for the company profile, legitimacy, screening and "
                            "verification evidence; beneficial_ownership for beneficial owners, FinCEN and CIP; "
                            "document_checklist for documentation collected so far, a named applicant's required "
                            "documents, a business onboarding list, or Blackwood; account_setup for product setup, "
                            "whether accounts can be provisioned, a review-ready service configuration plan, or "
                            "which setup-ready file and product are being prepared; onboarding_timeline for when "
                            "the client can start using the account; risk_assessment for risks or red flags; "
                            "status_summary for a status summary or update; onboarding_status for queue status, "
                            "bottlenecks, owners, and the whole pipeline."
                        ),
                        "enum": list(_OPERATIONS),
                    },
                    "application_id": {
                        "type": "string",
                        "description": (
                            "Synthetic application mapping: Nexus Industries or the corporate commercial-banking "
                            "client is APP-6005 (the default); Elena Brooks is APP-6001; Blackwood Capital "
                            "Partners, Blackwood, or the business onboarding file is APP-6002; Ahmed Al-Rashid or "
                            "the enhanced-due-diligence case is APP-6003; Maria Fontaine or the setup-ready "
                            "basic-savings file is APP-6004. Omit for Nexus Industries or for whole-pipeline reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("application_id")
        if record_id and record_id not in CUSTOMER_APPLICATIONS:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        operation = kwargs.get("operation", "initiate_onboarding")
        dispatch = {
            "kyc_verification": self._kyc_verification,
            "account_setup": self._account_setup,
            "document_checklist": self._document_checklist,
            "onboarding_status": self._onboarding_status,
            "initiate_onboarding": self._initiate_onboarding,
            "beneficial_ownership": self._beneficial_ownership,
            "onboarding_timeline": self._onboarding_timeline,
            "risk_assessment": self._risk_assessment,
            "status_summary": self._status_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        app_id = record_id or DEMO_APPLICATION
        if operation in ("initiate_onboarding", "beneficial_ownership", "onboarding_timeline",
                         "risk_assessment", "status_summary") and app_id != DEMO_APPLICATION:
            return SYNTHETIC_NOTICE + (
                f"**Not packaged:** this workflow has synthetic records for {DEMO_APPLICATION} "
                f"(Nexus Industries Inc.) only; `{app_id}` has KYC, document and pipeline records. "
                f"No substitute record was used.")
        return SYNTHETIC_NOTICE + handler(app_id=app_id)

    # ------------------------------------------------------------------
    def _initiate_onboarding(self, app_id, **_):
        app = CUSTOMER_APPLICATIONS[app_id]
        return "\n".join([
            f"Initiating corporate onboarding for {app['applicant']} with the full commercial banking suite: "
            f"KYC verification, corporate registration data, OFAC and sanctions screening, and product "
            f"provisioning are prepared as parallel workstreams for authorized reviewers.\n",
            "# Onboarding Initiated\n",
            "| Detail | Value |",
            "|---|---|",
            f"| Status | KYC Verification In Progress |",
            f"| Client Name | {app['applicant']} |",
            f"| Onboarding Type | Corporate - Commercial Banking |",
            f"| Products Requested | {', '.join(app['products_requested'])} |",
            f"| Estimated Annual Revenue | {_money_m(app['annual_revenue_potential'])} potential |",
            f"| Priority Level | {app['priority']} |",
            f"| CRM Case | {app['crm_case']} |",
            f"| Relationship Manager | {app['relationship_manager']} |",
            "",
            "## Parallel workstreams",
            "- KYC and company verification (corporate registration, financial statements)",
            "- OFAC and sanctions screening (entity and owners)",
            "- Beneficial ownership (FinCEN) verification",
            "- Product provisioning plan: treasury management, credit line, FX",
            "",
            "Next: ask for the company profile to review the legitimacy evidence.",
        ])

    def _kyc_verification(self, app_id, **_):
        app = CUSTOMER_APPLICATIONS[app_id]
        verification = VERIFICATION_STATUS.get(app_id, {})
        pct = _kyc_completion_pct(app_id)
        lines = []
        prof = CORPORATE_PROFILES.get(app_id)
        if prof:
            lines.append(
                f"{prof['legal_entity']} is a {prof['incorporation']}, EIN {prof['ein']}, in the "
                f"{prof['sector']} sector with {_money_m(prof['annual_revenue'])} annual revenue.\n")
        lines.append(f"# KYC Verification: {app_id}\n")
        lines.append(f"- **Applicant:** {app['applicant']}")
        lines.append(f"- **Type:** {app['application_type'].title()}")
        lines.append(f"- **Risk Rating:** {app['risk_rating'].title()}")
        lines.append(f"- **KYC Progress:** {pct}%\n")
        if prof:
            lines.append("## Corporate Verification\n")
            lines.append("**Status:** Legitimate entity per synthetic records\n")
            lines.append("| Field | Record |")
            lines.append("|---|---|")
            lines.append(f"| Legal Entity | {prof['legal_entity']} |")
            lines.append(f"| Incorporation | {prof['incorporation']} |")
            lines.append(f"| EIN | {prof['ein']} |")
            lines.append(f"| Industry | {prof['industry']} |")
            lines.append(f"| Annual Revenue | ${prof['annual_revenue']:,} ({_money_m(prof['annual_revenue'])}) |")
            lines.append(f"| Years in Business | {prof['years_in_business']} years |")
            lines.append(f"| Corporate Registration | {prof['corporate_registration']} |")
            lines.append(f"| Financial Statements | {prof['financial_statements']} |")
            lines.append(f"| Credit Rating | {prof['credit_rating']} |")
            lines.append(f"| OFAC Screening | {prof['ofac_screening']} |")
            lines.append(f"| Enhanced Due Diligence | {prof['enhanced_due_diligence']} |\n")
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
        if prof:
            lines.append("\nNext: review beneficial ownership (FinCEN).")
        return "\n".join(lines)

    def _beneficial_ownership(self, app_id, **_):
        owners = BENEFICIAL_OWNERS[app_id]
        verified = sum(1 for o in owners if o["status"] == "verified")
        pending = [o for o in owners if o["status"] != "verified"]
        lines = [
            f"The company has {len(owners)} beneficial owners with 25%+ ownership. {verified} are verified "
            f"in the synthetic record; {', '.join(o['name'] for o in pending)} is pending.\n",
            "# Beneficial Ownership (FinCEN)\n",
            f"**Status:** {verified} of {len(owners)} Verified - {len(pending)} Pending\n",
            "| Owner | Ownership | Status | Note |",
            "|---|---|---|---|",
        ]
        for i, o in enumerate(owners, 1):
            lines.append(f"| Owner {i} - {o['name']} | {o['ownership_pct']}% | {o['status'].title()} | {o['note']} |")
        lines += [
            "",
            "- ID verification method: Government-issued ID + facial recognition",
            f"- PEP screening: All {len(owners)} cleared - no PEP matches",
            f"- Sanctions screening: All {len(owners)} cleared - no OFAC/EU matches",
            "- Expected completion: Within 2 hours (passport processing)",
            "- FinCEN compliance: On track for full compliance once the pending owner is verified",
            f"- CIP status: Customer Identification Program {_cip_pct(app_id)}% complete",
            "",
            "A KYC/AML reviewer confirms each owner before the file is cleared.",
        ]
        return "\n".join(lines)

    def _account_setup(self, app_id, **_):
        lines = []
        plan = PROVISIONING_PLANS.get(app_id)
        if plan:
            lines.append(f"# Product Provisioning Plan: {app_id} {CUSTOMER_APPLICATIONS[app_id]['applicant']}\n")
            lines.append(f"**Status:** {_prov_pct(app_id)}% prepared for authorized provisioning\n")
            lines.append("| Product | Prepared configuration | Status |")
            lines.append("|---|---|---|")
            for item in plan:
                lines.append(f"| {item['item']} | {item['detail']} | {item['status'].title()} |")
            lines.append(
                "\nEverything except the credit line is ready for an authorized provisioning operator "
                "to activate in the core banking system; the credit line waits for the credit committee.\n")
        lines.append("# Account Setup Preparation Reference\n")
        lines.append("| Account Type | Min Deposit | Monthly Fee | APY | Features |")
        lines.append("|---|---|---|---|---|")
        for acct_type, details in ACCOUNT_TYPES.items():
            features = ", ".join(details["features"][:3])
            lines.append(
                f"| {acct_type.replace('_', ' ').title()} | ${details['min_deposit']:,.0f} "
                f"| ${details['monthly_fee']:,.0f} | {details['apy']}% | {features} |"
            )
        lines.append("\n## Applications Ready for Authorized Setup Review\n")
        review_ready = {k: v for k, v in CUSTOMER_APPLICATIONS.items() if v["status"] == "setup_review_ready"}
        if review_ready:
            for aid, app in review_ready.items():
                acct = ACCOUNT_TYPES.get(app["account_requested"], {})
                lines.append(f"### {aid}: {app['applicant']}\n")
                lines.append(f"- **Account:** {app['account_requested'].replace('_', ' ').title()}")
                lines.append(f"- **Min Deposit:** ${acct.get('min_deposit', 0):,.0f}")
                lines.append(f"- **Features:** {', '.join(acct.get('features', []))}\n")
        else:
            lines.append("No applications pending account setup.")
        lines.append(
            "\nNo account has been opened or provisioned. An authorized onboarding reviewer must "
            "validate KYC evidence, product eligibility, disclosures, and customer consent before action."
        )
        return "\n".join(lines)

    def _document_checklist(self, app_id, **_):
        app = CUSTOMER_APPLICATIONS[app_id]
        app_type = app["application_type"]
        lines = [f"# Document Checklist: {app_id}\n"]
        lines.append(f"**Applicant:** {app['applicant']}")
        lines.append(f"**Type:** {app_type.title()}\n")
        status = DOCUMENT_STATUS.get(app_id)
        if status:
            received = [d for d in status if d["status"] == "received"]
            pending = [d for d in status if d["status"] != "received"]
            lines.append(f"**Status:** {_doc_pct(app_id)}% Complete ({len(received)} of {len(status)} received)\n")
            lines.append("## Received\n")
            for d in received:
                lines.append(f"- [x] {d['document']}: {d['note']}")
            lines.append("\n## Pending\n")
            for d in pending:
                lines.append(f"- [ ] {d['document']}: {d['note']}")
            lines.append("\nDocument repository: secure compliance folder (synthetic record).")
        else:
            docs = KYC_DOCUMENTS.get(app_type, [])
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

    def _onboarding_timeline(self, app_id, **_):
        t = ONBOARDING_TIMELINES[app_id]
        lines = [
            f"Timeline to full activation is {t['business_days']} business days.\n",
            "# Onboarding Timeline\n",
            f"**Status:** {t['business_days']}-Day Fast Track\n",
            "| When | Step |",
            "|---|---|",
        ]
        for when, step in t["steps"]:
            lines.append(f"| {when} | {step} |")
        lines += [
            "",
            f"- Industry average: {t['industry_days_low']}-{t['industry_days_high']} days "
            f"(this plan is {_faster_pct(app_id)}% faster)",
            "- Client communication: daily status updates, sent by the relationship manager",
            f"- Success probability: {t['success_probability_pct']}% (strong financials + near-complete docs)",
            "",
            "The relationship manager schedules the week-2 introduction call; no meeting has been booked.",
        ]
        return "\n".join(lines)

    def _risk_assessment(self, app_id, **_):
        r = RISK_NOTES[app_id]
        app = CUSTOMER_APPLICATIONS[app_id]
        return "\n".join([
            f"{r['summary']}.\n",
            f"# Risk Review: {app['applicant']}\n",
            "| Area | Finding |",
            "|---|---|",
            f"| Screening | {r['screening']} |",
            f"| Financial position | {r['financials']} |",
            f"| Industry risk | {r['industry_risk']} |",
            f"| Overall risk rating | {app['risk_rating'].title()} |",
            "",
            f"**Minor note:** {r['minor_note']}.",
            "",
            "A KYC/AML compliance reviewer confirms the risk rating before activation.",
        ])

    def _status_summary(self, app_id, **_):
        app = CUSTOMER_APPLICATIONS[app_id]
        t = ONBOARDING_TIMELINES[app_id]
        owners = BENEFICIAL_OWNERS[app_id]
        pending_docs = [d["document"] for d in DOCUMENT_STATUS[app_id] if d["status"] != "received"]
        return "\n".join([
            f"# Status Summary: {app['applicant']} ({app['crm_case']})\n",
            "Ready for you to share with stakeholders:\n",
            "| Workstream | Status |",
            "|---|---|",
            f"| KYC and company verification | {_kyc_completion_pct(app_id)}% (enhanced due diligence in progress) |",
            f"| Beneficial ownership (FinCEN) | {sum(1 for o in owners if o['status'] == 'verified')} of {len(owners)} verified; CIP {_cip_pct(app_id)}% |",
            f"| Documentation | {_doc_pct(app_id)}% complete; pending: {', '.join(pending_docs)} |",
            f"| Product provisioning plan | {_prov_pct(app_id)}% prepared; credit line awaits credit committee Day 2 (tomorrow) 2 PM |",
            f"| Timeline | {t['business_days']}-day fast track; full activation Day 5 |",
            f"| Risk | {RISK_NOTES[app_id]['summary']}; overall {app['risk_rating']} |",
            "",
            "**Activation alert:** this agent cannot watch the file or notify you later. Set a reminder for "
            "Day 5 (full activation) or ask me for the status again. No message was sent.",
        ])

    def _onboarding_status(self, **_):
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
    for op in ["initiate_onboarding", "kyc_verification", "beneficial_ownership", "document_checklist",
               "account_setup", "onboarding_timeline", "risk_assessment", "status_summary"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
