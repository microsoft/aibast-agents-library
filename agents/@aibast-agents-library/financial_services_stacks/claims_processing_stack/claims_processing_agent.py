"""
Claims Processing Agent — Financial Services Stack

Supports insurance claims lifecycle with intake, adjudication review,
fraud flagging, and settlement recommendations.
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
    "description": "Insurance claims processing with intake, adjudication review, fraud detection, and settlement recommendations.",
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

CLAIMS = {
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
        "status": "approved",
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
    "CLM-2025-7001": ["Initial inspection completed 01/20 — damage consistent with pipe burst", "Plumber confirms corrosion in copper fitting", "Estimate from licensed contractor received"],
    "CLM-2025-7002": ["Police report confirms other party at fault", "Body shop estimate within market range", "Medical records show minor soft tissue injury"],
    "CLM-2025-7003": ["Fire marshal report pending", "Financial statements show declining revenue for 3 quarters", "Inventory list lacks purchase receipts for high-value items", "SIU referral initiated"],
    "CLM-2025-7004": ["Police report filed but no suspects identified", "Itemized list of stolen items requested", "Receipts or appraisals needed for jewelry and collectibles"],
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _settlement_amount(claim):
    """Calculate recommended settlement amount."""
    policy = POLICY_DETAILS.get(claim["policy_number"], {})
    deductible = policy.get("deductible", 0)
    coverage = policy.get("coverage_limit", 0)
    claimed = claim["claimed_amount"]
    if claim["fraud_score"] >= 60:
        return 0
    net = min(claimed, coverage) - deductible
    if claim["fraud_score"] >= 30:
        net = round(net * 0.75, 2)
    return max(0, round(net, 2))


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
        self.name = "@aibast-agents-library/claims-processing"
        self.metadata = {
            "name": self.name,
            "display_name": "Claims Processing Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "claim_intake",
                            "adjudication_review",
                            "fraud_flag",
                            "settlement_recommendation",
                        ],
                    },
                    "claim_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "claim_intake")
        dispatch = {
            "claim_intake": self._claim_intake,
            "adjudication_review": self._adjudication_review,
            "fraud_flag": self._fraud_flag,
            "settlement_recommendation": self._settlement_recommendation,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _claim_intake(self, **kwargs) -> str:
        summary = _claims_summary()
        lines = ["# Claims Intake Dashboard\n"]
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

    def _adjudication_review(self, **kwargs) -> str:
        claim_id = kwargs.get("claim_id", "CLM-2025-7001")
        claim = CLAIMS.get(claim_id, list(CLAIMS.values())[0])
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
        if notes:
            lines.append("\n## Adjuster Notes\n")
            for note in notes:
                lines.append(f"- {note}")
        return "\n".join(lines)

    def _fraud_flag(self, **kwargs) -> str:
        lines = ["# Fraud Detection Report\n"]
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
        lines = ["# Settlement Recommendations\n"]
        lines.append("| Claim ID | Claimant | Claimed | Deductible | Fraud Score | Recommended |")
        lines.append("|---|---|---|---|---|---|")
        for cid, c in CLAIMS.items():
            policy = POLICY_DETAILS.get(c["policy_number"], {})
            settlement = _settlement_amount(c)
            lines.append(
                f"| {cid} | {c['claimant']} | ${c['claimed_amount']:,.0f} "
                f"| ${policy.get('deductible', 0):,.0f} | {c['fraud_score']} | ${settlement:,.0f} |"
            )
        total_claimed = sum(c["claimed_amount"] for c in CLAIMS.values())
        total_recommended = sum(_settlement_amount(c) for c in CLAIMS.values())
        lines.append(f"\n**Total Claimed:** ${total_claimed:,.0f}")
        lines.append(f"**Total Recommended Settlement:** ${total_recommended:,.0f}")
        savings = total_claimed - total_recommended
        lines.append(f"**Savings from Adjustments:** ${savings:,.0f}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ClaimsProcessingAgent()
    print(agent.perform(operation="claim_intake"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="adjudication_review", claim_id="CLM-2025-7003"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="fraud_flag"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="settlement_recommendation"))
