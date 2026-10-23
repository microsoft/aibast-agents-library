"""
Claims Processing Agent — Financial Services Stack

Supports insurance claims lifecycle with intake, adjudication review,
fraud flagging, and settlement recommendations.

Demo scenario (synthetic): today's 2,847-claim queue. The agent tiers the queue
(1,936 auto-adjudicate), flags 89 suspicious claims ($2.4M), produces
recommended auto-adjudication outcomes for the eligible claims, prepares the
complex file CLM-78445, reports before/after processing metrics, and
summarizes the session. Approvals and denials are recommendations awaiting
authorized adjuster sign-off; nothing is paid or released by the agent.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/claims-processing",
    "version": "1.0.0",
    "display_name": "Claims Processing Agent",
    "description": "Automate claims processing workflows to deliver faster, consistent, and more compliant claim outcomes.",
    "author": "AIBAST",
    "tags": ["claims", "insurance", "adjudication", "fraud", "settlement", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

DEMO_AS_OF = "2025-03-10"

CLAIMS = {
    "CLM-78445": {
        "claimant": "Homeowner policyholder (water loss)",
        "policy_number": "HO-912340",
        "policy_type": "homeowners",
        "date_of_loss": "2025-03-03",
        "date_filed": "2025-03-04",
        "loss_type": "water_damage",
        "description": "Homeowner's water damage: supply-line failure flooded the kitchen, basement and finished family room",
        "claimed_amount": 127000,
        "adjuster": "Senior adjuster queue",
        "status": "complex_prepared",
        "fraud_score": 8,
        "supporting_docs": ["photos", "repair_estimate"],
    },
    "CLM-2025-7001": {
        "claimant": "Margaret Sullivan",
        "policy_number": "HO-445892",
        "policy_type": "homeowners",
        "date_of_loss": "2025-01-15",
        "date_filed": "2025-01-18",
        "loss_type": "water_damage",
        "description": "Burst pipe in upstairs bathroom caused water damage to ceiling, walls, and flooring in two rooms",
        "claimed_amount": 28500,
        "adjuster": "Brian Keller",
        "status": "under_review",
        "fraud_score": 12,
        "supporting_docs": ["photos", "plumber_invoice", "repair_estimate"],
    },
    "CLM-2025-7002": {
        "claimant": "David Park",
        "policy_number": "AU-331205",
        "policy_type": "auto",
        "date_of_loss": "2025-02-08",
        "date_filed": "2025-02-09",
        "loss_type": "collision",
        "description": "Rear-end collision at intersection of 5th Ave and Main St, other driver cited",
        "claimed_amount": 14200,
        "adjuster": "Sandra Ortiz",
        "status": "ready_for_adjuster_review",
        "fraud_score": 5,
        "supporting_docs": ["police_report", "photos", "body_shop_estimate", "medical_records"],
    },
    "CLM-2025-7003": {
        "claimant": "Apex Commercial Properties",
        "policy_number": "CP-778341",
        "policy_type": "commercial_property",
        "date_of_loss": "2025-02-22",
        "date_filed": "2025-02-24",
        "loss_type": "fire_damage",
        "description": "Electrical fire in warehouse section B, significant inventory and structural damage",
        "claimed_amount": 485000,
        "adjuster": "Brian Keller",
        "status": "investigation",
        "fraud_score": 68,
        "supporting_docs": ["fire_report", "photos", "inventory_list", "financial_statements"],
    },
    "CLM-2025-7004": {
        "claimant": "Jennifer Liu",
        "policy_number": "HO-557210",
        "policy_type": "homeowners",
        "date_of_loss": "2025-03-01",
        "date_filed": "2025-03-02",
        "loss_type": "theft",
        "description": "Home burglary — electronics, jewelry, and collectibles stolen",
        "claimed_amount": 42000,
        "adjuster": "Sandra Ortiz",
        "status": "pending_documentation",
        "fraud_score": 45,
        "supporting_docs": ["police_report", "photos"],
    },
}

POLICY_DETAILS = {
    "HO-912340": {"coverage_limit": 500000, "deductible": 2500, "premium_annual": 3100, "effective": "2024-10-01", "expiry": "2025-10-01"},
    "HO-445892": {"coverage_limit": 350000, "deductible": 1500, "premium_annual": 2400, "effective": "2024-07-01", "expiry": "2025-07-01"},
    "AU-331205": {"coverage_limit": 100000, "deductible": 500, "premium_annual": 1800, "effective": "2024-11-01", "expiry": "2025-11-01"},
    "CP-778341": {"coverage_limit": 2000000, "deductible": 10000, "premium_annual": 18500, "effective": "2024-09-01", "expiry": "2025-09-01"},
    "HO-557210": {"coverage_limit": 400000, "deductible": 2000, "premium_annual": 2800, "effective": "2025-01-01", "expiry": "2026-01-01"},
}

FRAUD_INDICATORS = {
    "financial_stress": {"weight": 15, "description": "Claimant shows signs of recent financial distress"},
    "claim_timing": {"weight": 12, "description": "Claim filed shortly after policy inception or increase in coverage"},
    "excessive_amount": {"weight": 20, "description": "Claimed amount significantly exceeds typical loss for category"},
    "inconsistent_narrative": {"weight": 18, "description": "Inconsistencies between claimant statement and evidence"},
    "prior_claims_history": {"weight": 10, "description": "Multiple prior claims on same or similar policies"},
    "delayed_reporting": {"weight": 8, "description": "Significant delay between loss event and claim filing"},
    "witness_issues": {"weight": 12, "description": "Lack of independent witnesses or corroborating evidence"},
    "documentation_gaps": {"weight": 15, "description": "Missing or incomplete supporting documentation"},
}

ADJUSTER_NOTES = {
    "CLM-78445": ["Coverage confirmed for water damage (sudden supply-line failure)", "Contractor estimate within 8% of market rate", "No prior water claims on property"],
    "CLM-2025-7001": ["Initial inspection completed 01/20 — damage consistent with pipe burst", "Plumber confirms corrosion in copper fitting", "Estimate from licensed contractor received"],
    "CLM-2025-7002": ["Police report confirms other party at fault", "Body shop estimate within market range", "Medical records show minor soft tissue injury"],
    "CLM-2025-7003": ["Fire marshal report pending", "Financial statements show declining revenue for 3 quarters", "Inventory list lacks purchase receipts for high-value items", "SIU referral initiated"],
    "CLM-2025-7004": ["Police report filed but no suspects identified", "Itemized list of stolen items requested", "Receipts or appraisals needed for jewelry and collectibles"],
}


# Documents each loss type needs before evaluation (label shown when missing)
REQUIRED_DOCS = {
    "water_damage": {"photos": "Photos", "repair_estimate": "Contractor repair estimate",
                     "plumber_invoice": "Final plumber invoice", "mold_inspection_report": "Mold inspection report"},
    "theft": {"police_report": "Police report", "photos": "Photos", "itemized_list": "Itemized list of stolen items",
              "receipts_or_appraisals": "Receipts or appraisals"},
    "collision": {"police_report": "Police report", "photos": "Photos", "body_shop_estimate": "Body shop estimate"},
    "fire_damage": {"fire_report": "Fire marshal report", "photos": "Photos", "inventory_list": "Inventory list",
                    "purchase_receipts": "Purchase receipts for high-value items"},
}

COMPLEX_FILE_FACTS = {
    "CLM-78445": {"market_rate_estimate": 117600, "prior_water_claims": 0, "covered": True},
}

ADJUSTER_WORKFLOW = [
    "Claims queued by specialization",
    "Pre-populated decision forms",
    "One-click approval/denial for the authorized adjuster",
    "Auto-generated correspondence drafts",
]

# Today's queue (the demo walkthrough)
QUEUE_TIERS = [
    {"category": "Auto-adjudicate", "claims": 1936, "action": "Instant processing (recommendation for sign-off)"},
    {"category": "Standard review", "claims": 624, "action": "Adjuster queue"},
    {"category": "Complex/High-value", "claims": 198, "action": "Senior adjuster"},
    {"category": "Fraud investigation", "claims": 89, "action": "SIU referral"},
]

PRIORITY_FLAGS = [
    "34 claims with regulatory deadlines in 48 hours",
    "18 claims from VIP policyholders",
    "12 claims with litigation potential",
    "8 catastrophe-related claims (expedited handling)",
]

ROUTING_RULES = [
    "Simple auto claims under $5,000",
    "Routine medical with matching codes",
    "Property claims with verified estimates",
]

PROCESSING_TIME = {"auto_minutes": 4, "traditional_days": 3, "traditional_hours_per_claim": 3, "ai_batch_minutes": 18,
                   "hourly_cost": 50}

FRAUD_TIERS = [
    {"risk": "High (80%+)", "claims": 12, "value": 890000, "action": "SIU immediate"},
    {"risk": "Medium (50-79%)", "claims": 41, "value": 1100000, "action": "Enhanced review"},
    {"risk": "Low (25-49%)", "claims": 36, "value": 420000, "action": "Flag for adjuster"},
]

FRAUD_SUSPECTS = [
    {"claim": "CLM-78234", "type": "Auto", "indicator": "Staged accident pattern"},
    {"claim": "CLM-78156", "type": "Medical", "indicator": "Provider billing anomaly"},
    {"claim": "CLM-78089", "type": "Property", "indicator": "Recent policy change"},
]

FRAUD_DEEP_ANALYSIS = {
    "claim": "CLM-78234",
    "findings": [
        "Claimant filed 3 claims in 18 months",
        "Accident location matches known staging area",
        "Body shop on fraud watch list",
        "Similar claims from same intersection",
    ],
}

AUTO_ADJUDICATION = {
    "outcomes": [
        {"outcome": "Approve", "claims": 1724, "value": 4200000, "avg_minutes": 3.8},
        {"outcome": "Deny", "claims": 142, "value": 380000, "avg_minutes": 2.1},
        {"outcome": "Needs info", "claims": 70, "value": 290000, "avg_minutes": 4.2},
    ],
    "approval_breakdown": [
        {"type": "Auto physical damage", "claims": 892, "value": 1800000},
        {"type": "Medical routine", "claims": 534, "value": 1600000},
        {"type": "Property minor", "claims": 298, "value": 800000},
    ],
    "denial_reasons": [
        {"reason": "Coverage exclusion", "claims": 68},
        {"reason": "Policy lapsed", "claims": 42},
        {"reason": "Duplicate submission", "claims": 32},
    ],
    "accuracy_pct": 99.2,
    "within_guidelines_pct": 100,
}

PROCESSING_METRICS = [
    {"metric": "Avg cycle time", "before": 12, "after": 5.2, "unit": " days", "prefix": ""},
    {"metric": "Auto-adjudication", "before": 12, "after": 68, "unit": "%", "prefix": ""},
    {"metric": "Cost per claim", "before": 142, "after": 48, "unit": "", "prefix": "$"},
    {"metric": "Customer satisfaction", "before": 3.2, "after": 4.4, "unit": "/5", "prefix": ""},
]

OPTIMIZATIONS = [
    {"improvement": "Expand auto-adjudication rules", "impact": "+8% auto rate", "effort": "Medium"},
    {"improvement": "Mobile photo AI assessment", "impact": "-1 day cycle", "effort": "Low"},
    {"improvement": "Real-time status updates", "impact": "+0.3 CSAT", "effort": "Low"},
    {"improvement": "Provider network integration", "impact": "-2 days medical", "effort": "High"},
]


SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — ADJUSTER REVIEW REQUIRED.** Fictional claims and policy terms only. "
    "This output is not legal, insurance, or financial advice and does not approve, deny, settle, pay, "
    "reserve, or change a claim.\n\n"
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _settlement_amount(claim):
    """Calculate a policy-term review estimate without making a claim decision."""
    policy = POLICY_DETAILS.get(claim["policy_number"], {})
    deductible = policy.get("deductible", 0)
    coverage = policy.get("coverage_limit", 0)
    claimed = claim["claimed_amount"]
    net = min(claimed, coverage) - deductible
    return max(0, round(net, 2))


def _queue_total():
    return sum(t["claims"] for t in QUEUE_TIERS)


def _pct(part, whole):
    return round(part * 100 / whole) if whole else 0


def _money_k(value):
    if value >= 1000000:
        return f"${value / 1000000:.1f}M"
    return f"${value / 1000:g}K"


def _efficiency():
    eligible = QUEUE_TIERS[0]["claims"]
    traditional_hours = eligible * PROCESSING_TIME["traditional_hours_per_claim"]
    saved = int(traditional_hours - PROCESSING_TIME["ai_batch_minutes"] / 60)
    return {"eligible": eligible, "traditional_hours": traditional_hours, "saved": saved,
            "saved_pct": round(saved * 100 / traditional_hours, 2),
            "cost_savings": saved * PROCESSING_TIME["hourly_cost"]}


def _missing_docs(claim):
    required = REQUIRED_DOCS.get(claim["loss_type"], {})
    return [label for key, label in required.items() if key not in claim["supporting_docs"]]


def _in_force(policy):
    return policy.get("effective", "9999") <= DEMO_AS_OF < policy.get("expiry", "0000")


def _claims_summary():
    """Compute aggregate claims metrics."""
    total_claimed = sum(c["claimed_amount"] for c in CLAIMS.values())
    avg_fraud = sum(c["fraud_score"] for c in CLAIMS.values()) / len(CLAIMS)
    by_status = {}
    for c in CLAIMS.values():
        by_status[c["status"]] = by_status.get(c["status"], 0) + 1
    return {"total_claimed": total_claimed, "avg_fraud_score": round(avg_fraud, 1), "by_status": by_status, "count": len(CLAIMS)}


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class ClaimsProcessingAgent(BasicAgent):
    """Insurance claims processing agent."""

    def __init__(self):
        self.name = "ClaimsProcessingAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Claims Processing Agent",
            "description": (
                "Use for claims-adjuster, claims-manager, SIU, or claims-operations requests. Call this "
                "tool when the user asks to process the incoming claims queue and separate immediate "
                "attention from auto-adjudication, for fraud detection results and high-risk claims, to "
                "auto-adjudicate the eligible claims, for the complex claims prepared for adjusters, for "
                "processing metrics and improvements, for a summary of today's work, which incoming claim "
                "needs specialized handling, what is missing "
                "from a named claimant's file before evaluation, which claim crosses an SIU threshold, "
                "whether a fraud score proves fraud, or for policy-term estimates and approval/payment "
                "status boundaries. Always call this tool for those claims-workflow requests rather than "
                "answering from general knowledge, including when the user asks whether any claim was "
                "approved or paid. Uses fictional records only; a fraud flag is not proof, and the tool "
                "never approves, denies, reserves, settles, pays, or changes a claim. Authorized adjuster "
                "review is required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose claim_intake to process the incoming claims queue, immediate attention vs "
                            "auto-adjudication, specialized handling, routing, or workload questions. Choose "
                            "adjudication_review for the complex claims prepared for adjuster review (default "
                            "CLM-78445), a named claim or claimant, missing documents, file completeness, "
                            "policy evidence, adjuster notes, or what is needed before evaluation. Choose "
                            "fraud_flag for fraud detection results, high-risk claims, SIU thresholds, fraud "
                            "indicators, referrals, or whether a score proves fraud. Choose auto_adjudication "
                            "to auto-adjudicate the eligible claims and show the results (recommended outcomes "
                            "awaiting adjuster sign-off). Choose processing_metrics for metrics and where we "
                            "can improve. Choose session_summary to summarize everything accomplished today. Choose "
                            "settlement_recommendation for nonbinding policy-term estimates or questions "
                            "asking whether any claim was approved, denied, settled, or paid; this operation "
                            "returns the source-backed boundary that no approval or payment occurred."
                        ),
                        "enum": [
                            "claim_intake",
                            "adjudication_review",
                            "fraud_flag",
                            "settlement_recommendation",
                            "auto_adjudication",
                            "processing_metrics",
                            "session_summary",
                        ],
                    },
                    "claim_id": {
                        "type": "string",
                        "description": (
                            "Use the synthetic claim identifier when the user names a file or claimant: "
                            "the complex water-damage file is CLM-78445; Margaret Sullivan is CLM-2025-7001; David Park is CLM-2025-7002; "
                            "Apex Commercial Properties is CLM-2025-7003; Jennifer Liu or the theft file "
                            "is CLM-2025-7004. Omit only for whole-queue reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("claim_id")
        if record_id and record_id not in CLAIMS:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        operation = kwargs.get("operation", "claim_intake")
        dispatch = {
            "claim_intake": self._claim_intake,
            "adjudication_review": self._adjudication_review,
            "fraud_flag": self._fraud_flag,
            "settlement_recommendation": self._settlement_recommendation,
            "auto_adjudication": self._auto_adjudication,
            "processing_metrics": self._processing_metrics,
            "session_summary": self._session_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(**kwargs)

    def _claim_intake(self, **kwargs) -> str:
        summary = _claims_summary()
        total = _queue_total()
        auto = QUEUE_TIERS[0]["claims"]
        eff = _efficiency()
        lines = ["# Claims Intake Dashboard\n"]
        lines.append(
            f"I've analyzed today's {total:,} incoming claims. {_pct(auto, total)}% qualify for "
            f"auto-adjudication, saving {eff['saved']:,} adjuster hours.\n"
        )
        lines.append("## Claims Queue Analysis\n")
        lines.append("| Category | Claims | % of Total | Recommended Action |")
        lines.append("|---|---|---|---|")
        for t in QUEUE_TIERS:
            lines.append(f"| {t['category']} | {t['claims']:,} | {_pct(t['claims'], total)}% | {t['action']} |")
        lines.append("\n## Priority Flags Detected\n")
        lines += [f"- {f}" for f in PRIORITY_FLAGS]
        lines.append("\n## Auto-Adjudication Eligible\n")
        lines += [f"- {r}" for r in ROUTING_RULES]
        lines.append(f"- Average processing: {PROCESSING_TIME['auto_minutes']} minutes vs {PROCESSING_TIME['traditional_days']} days")
        lines.append("\nNext step: see the fraud detection results?\n")
        lines.append("## Sample Claim Files\n")
        lines.append(f"**Total Claims:** {summary['count']}")
        lines.append(f"**Total Claimed:** ${summary['total_claimed']:,.0f}")
        lines.append(f"**Avg Fraud Score:** {summary['avg_fraud_score']}\n")
        lines.append("| Claim ID | Claimant | Policy Type | Loss | Amount | Status | Fraud |")
        lines.append("|---|---|---|---|---|---|---|")
        for cid, c in CLAIMS.items():
            lines.append(
                f"| {cid} | {c['claimant']} | {c['policy_type'].replace('_', ' ').title()} "
                f"| {c['loss_type'].replace('_', ' ').title()} | ${c['claimed_amount']:,.0f} "
                f"| {c['status'].replace('_', ' ').title()} | {c['fraud_score']} |"
            )
        lines.append("\n## Status Distribution\n")
        for status, count in summary["by_status"].items():
            lines.append(f"- {status.replace('_', ' ').title()}: {count}")
        return "\n".join(lines)

    def _complex_file(self, claim_id):
        claim = CLAIMS[claim_id]
        policy = POLICY_DETAILS[claim["policy_number"]]
        facts = COMPLEX_FILE_FACTS[claim_id]
        variance = round((claim["claimed_amount"] - facts["market_rate_estimate"]) * 100 / facts["market_rate_estimate"])
        recommend = _settlement_amount(claim)
        complex_count = QUEUE_TIERS[2]["claims"]
        lines = [f"# Complex Claims Prepared for Adjuster Review\n"]
        lines.append(f"{complex_count} complex claims prepared with pre-analysis. Sample prepared claim - {claim_id}:\n")
        lines.append("## Claim Summary\n")
        lines.append(f"- Type: Homeowner's {claim['loss_type'].replace('_', ' ')}")
        lines.append(f"- Claimed: ${claim['claimed_amount']:,.0f}")
        lines.append(f"- Policy limit: ${policy['coverage_limit']:,.0f}")
        lines.append(f"- Deductible: ${policy['deductible']:,.0f}")
        lines.append(f"- Policy in force on {DEMO_AS_OF}: {'Yes' if _in_force(policy) else 'No'}\n")
        lines.append("## Pre-Analysis\n")
        lines.append(f"- Coverage {'confirmed' if facts['covered'] else 'not confirmed'} for {claim['loss_type'].replace('_', ' ')}")
        lines.append(f"- Contractor estimate within {variance}% of market rate (${facts['market_rate_estimate']:,.0f})")
        lines.append(f"- {'No' if facts['prior_water_claims'] == 0 else facts['prior_water_claims']} prior water claims on property")
        lines.append(f"- Recommendation for adjuster sign-off: approve ${recommend:,.0f} (estimate minus deductible)\n")
        lines.append("## Missing Information\n")
        lines += [f"- {d} needed" for d in _missing_docs(claim)]
        lines.append("\n## Adjuster Workflow\n")
        lines += [f"- {w}" for w in ADJUSTER_WORKFLOW]
        lines.append("\nNo claim was approved, denied or paid; the authorized adjuster decides.")
        lines.append("\nNext step: show processing metrics and optimization opportunities?")
        return "\n".join(lines)

    def _adjudication_review(self, **kwargs) -> str:
        claim_id = kwargs.get("claim_id") or "CLM-78445"
        if claim_id in COMPLEX_FILE_FACTS:
            return self._complex_file(claim_id)
        claim = CLAIMS[claim_id]
        policy = POLICY_DETAILS.get(claim["policy_number"], {})
        notes = ADJUSTER_NOTES.get(claim_id, [])
        lines = [f"# Adjudication Review: {claim_id}\n"]
        lines.append(f"- **Claimant:** {claim['claimant']}")
        lines.append(f"- **Policy:** {claim['policy_number']} ({claim['policy_type'].replace('_', ' ').title()})")
        lines.append(f"- **Date of Loss:** {claim['date_of_loss']}")
        lines.append(f"- **Loss Type:** {claim['loss_type'].replace('_', ' ').title()}")
        lines.append(f"- **Description:** {claim['description']}")
        lines.append(f"- **Claimed Amount:** ${claim['claimed_amount']:,.0f}")
        lines.append(f"- **Adjuster:** {claim['adjuster']}")
        lines.append(f"- **Fraud Score:** {claim['fraud_score']}/100\n")
        lines.append("## Policy Details\n")
        lines.append(f"- Coverage Limit: ${policy.get('coverage_limit', 0):,.0f}")
        lines.append(f"- Deductible: ${policy.get('deductible', 0):,.0f}")
        lines.append(f"- Effective: {policy.get('effective', 'N/A')} to {policy.get('expiry', 'N/A')}\n")
        lines.append("## Supporting Documents\n")
        for doc in claim["supporting_docs"]:
            lines.append(f"- [x] {doc.replace('_', ' ').title()}")
        missing = _missing_docs(claim)
        if missing:
            lines.append("\n## Missing Before Evaluation\n")
            for doc in missing:
                lines.append(f"- [ ] {doc}")
        if notes:
            lines.append("\n## Adjuster Notes\n")
            for note in notes:
                lines.append(f"- {note}")
        return "\n".join(lines)

    def _fraud_flag(self, **kwargs) -> str:
        lines = ["# Fraud Detection Report\n"]
        suspicious = sum(t["claims"] for t in FRAUD_TIERS)
        value = sum(t["value"] for t in FRAUD_TIERS)
        high = FRAUD_TIERS[0]
        lines.append(
            f"Fraud analysis identified {suspicious} suspicious claims worth {_money_k(value)}. "
            f"{high['claims']} are high-confidence fraud referrals (a flag is not proof of fraud).\n"
        )
        lines.append("| Risk Level | Claims | Total Value | Action |")
        lines.append("|---|---|---|---|")
        for t in FRAUD_TIERS:
            lines.append(f"| {t['risk']} | {t['claims']} | {_money_k(t['value'])} | {t['action']} |")
        lines.append("\n## Top High-Risk Claims\n")
        lines.append("| Claim # | Type | Fraud Indicators |")
        lines.append("|---|---|---|")
        for f in FRAUD_SUSPECTS:
            lines.append(f"| {f['claim']} | {f['type']} | {f['indicator']} |")
        lines.append(f"\n## {FRAUD_DEEP_ANALYSIS['claim']} Deep Analysis (SIU evidence package draft)\n")
        lines += [f"- {x}" for x in FRAUD_DEEP_ANALYSIS["findings"]]
        lines.append(f"\n**Estimated Fraud Savings:** {_money_k(high['value'])} prevented if high-risk confirmed (estimate).")
        lines.append("\nNext step: proceed with auto-adjudication recommendations for eligible claims?\n")
        lines.append("## Fraud Indicator Reference\n")
        lines.append("| Indicator | Weight | Description |")
        lines.append("|---|---|---|")
        for ind_id, ind in FRAUD_INDICATORS.items():
            lines.append(f"| {ind_id.replace('_', ' ').title()} | {ind['weight']} | {ind['description']} |")
        flagged = {k: v for k, v in CLAIMS.items() if v["fraud_score"] >= 30}
        lines.append(f"\n## Flagged Claims (score >= 30)\n")
        if flagged:
            lines.append("| Claim ID | Claimant | Amount | Fraud Score | Status |")
            lines.append("|---|---|---|---|---|")
            for cid, c in flagged.items():
                lines.append(
                    f"| {cid} | {c['claimant']} | ${c['claimed_amount']:,.0f} "
                    f"| {c['fraud_score']} | {c['status'].replace('_', ' ').title()} |"
                )
        else:
            lines.append("No claims currently flagged.")
        high_risk = {k: v for k, v in CLAIMS.items() if v["fraud_score"] >= 60}
        if high_risk:
            lines.append("\n## SIU Referrals (score >= 60)\n")
            for cid, c in high_risk.items():
                lines.append(f"- **{cid}:** {c['claimant']} — ${c['claimed_amount']:,.0f} (score: {c['fraud_score']})")
        return "\n".join(lines)

    def _settlement_recommendation(self, **kwargs) -> str:
        lines = ["# Policy-Term Settlement Estimates for Adjuster Review\n"]
        lines.append("| Claim ID | Claimant | Claimed | Deductible | Fraud Score | Review Estimate |")
        lines.append("|---|---|---|---|---|---|")
        for cid, c in CLAIMS.items():
            policy = POLICY_DETAILS.get(c["policy_number"], {})
            if c["fraud_score"] >= 60:
                estimate = "Hold pending SIU"
            else:
                estimate = f"${_settlement_amount(c):,.0f}"
            lines.append(
                f"| {cid} | {c['claimant']} | ${c['claimed_amount']:,.0f} "
                f"| ${policy.get('deductible', 0):,.0f} | {c['fraud_score']} | {estimate} |"
            )
        total_claimed = sum(c["claimed_amount"] for c in CLAIMS.values())
        total_recommended = sum(_settlement_amount(c) for c in CLAIMS.values() if c["fraud_score"] < 60)
        lines.append(f"\n**Total Claimed:** ${total_claimed:,.0f}")
        lines.append(f"**Aggregate Review Estimate (excluding SIU holds):** ${total_recommended:,.0f}")
        lines.append(
            "\nFraud scores do not reduce or eliminate coverage. An authorized adjuster must validate "
            "coverage, causation, documentation, exclusions, jurisdictional rules, and SIU findings. "
            "No approval, denial, settlement, reserve, or payment has occurred."
        )
        return "\n".join(lines)


    def _auto_adjudication(self, **kwargs) -> str:
        a = AUTO_ADJUDICATION
        eff = _efficiency()
        lines = ["# Auto-Adjudication Recommendations\n"]
        lines.append(
            f"{eff['eligible']:,} eligible claims evaluated against the guidelines. Outcomes below are "
            "recommendations; release requires authorized adjuster sign-off.\n"
        )
        lines.append("| Recommended Outcome | Claims | Total Value | Avg Time |")
        lines.append("|---|---|---|---|")
        for o in a["outcomes"]:
            lines.append(f"| {o['outcome']} | {o['claims']:,} | {_money_k(o['value'])} | {o['avg_minutes']} min |")
        lines.append("\n## Approval Breakdown\n")
        for b in a["approval_breakdown"]:
            lines.append(f"- {b['type']}: {b['claims']} claims ({_money_k(b['value'])})")
        lines.append("\n## Denial Reasons\n")
        for d in a["denial_reasons"]:
            lines.append(f"- {d['reason']}: {d['claims']} claims")
        lines.append("\n## Efficiency Gains\n")
        lines.append(f"- Traditional processing: {eff['traditional_hours']:,} hours")
        lines.append(f"- AI processing: {PROCESSING_TIME['ai_batch_minutes']} minutes")
        lines.append(f"- Hours saved: {eff['saved']:,} ({eff['saved_pct']}%)")
        lines.append(f"- Cost savings: ${eff['cost_savings']:,} (at ${PROCESSING_TIME['hourly_cost']}/hour)")
        lines.append("\n## Quality Metrics\n")
        lines.append(f"- Auto-decision accuracy: {a['accuracy_pct']}%")
        lines.append(f"- Within payment guidelines: {a['within_guidelines_pct']}%")
        lines.append("\nNo approval, denial, or payment has occurred; adjusters release the recommendations.")
        lines.append("\nNext step: review the complex claims prepared for adjusters?")
        return "\n".join(lines)

    def _processing_metrics(self, **kwargs) -> str:
        cycle = PROCESSING_METRICS[0]
        lines = ["# Claims Processing Metrics\n"]
        lines.append(
            f"Cycle time improved {_pct(cycle['before'] - cycle['after'], cycle['before'])}%. "
            "Additional optimization can reduce cycle time to about 4 days.\n"
        )
        lines.append("| Metric | Before AI | With AI | Change |")
        lines.append("|---|---|---|---|")
        for m in PROCESSING_METRICS:
            change = round((m["after"] - m["before"]) * 100 / m["before"])
            lines.append(
                f"| {m['metric']} | {m['prefix']}{m['before']:g}{m['unit']} | {m['prefix']}{m['after']:g}{m['unit']} "
                f"| {'+' if change > 0 else ''}{change}% |"
            )
        lines.append("\n## Optimization Opportunities\n")
        lines.append("| Improvement | Impact | Effort |")
        lines.append("|---|---|---|")
        for o in OPTIMIZATIONS:
            lines.append(f"| {o['improvement']} | {o['impact']} | {o['effort']} |")
        lines.append("\nNext step: summarize everything accomplished today?")
        return "\n".join(lines)

    def _session_summary(self, **kwargs) -> str:
        total = _queue_total()
        auto = QUEUE_TIERS[0]["claims"]
        fraud_claims = sum(t["claims"] for t in FRAUD_TIERS)
        fraud_value = sum(t["value"] for t in FRAUD_TIERS)
        approved = AUTO_ADJUDICATION["outcomes"][0]
        eff = _efficiency()
        cycle = PROCESSING_METRICS[0]
        lines = ["# Claims Processing Session Summary\n"]
        lines.append("| Accomplishment | Result |")
        lines.append("|---|---|")
        lines.append(f"| Claims processed | {total:,} total |")
        lines.append(f"| Auto-adjudication recommendations | {auto:,} ({_pct(auto, total)}%) in {PROCESSING_TIME['ai_batch_minutes']} minutes |")
        lines.append(f"| Fraud identified | {fraud_claims} claims, {_money_k(fraud_value)} flagged for SIU review |")
        lines.append(f"| Complex prepared | {QUEUE_TIERS[2]['claims']} claims with AI analysis |")
        lines.append(f"| Payments recommended | {_money_k(approved['value'])} awaiting adjuster release |")
        lines.append("\n## Efficiency Gains\n")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Hours saved | {eff['saved']:,} adjuster hours |")
        lines.append(f"| Cost savings | ${eff['cost_savings']:,} today |")
        lines.append(
            f"| Cycle time reduction | {_pct(cycle['before'] - cycle['after'], cycle['before'])}% "
            f"({cycle['before']:g} to {cycle['after']:g} days) |"
        )
        lines.append("\nNo approval, denial, settlement, or payment has occurred; each needs authorized adjuster sign-off.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ClaimsProcessingAgent()
    for op in ["claim_intake", "fraud_flag", "auto_adjudication", "adjudication_review", "processing_metrics",
               "session_summary"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
