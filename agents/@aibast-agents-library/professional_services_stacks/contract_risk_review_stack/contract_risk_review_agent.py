"""
Contract Risk Review Agent

Scans professional-services contracts for risky clauses, checks compliance
with internal policies, and generates renegotiation briefs highlighting
liability exposure, IP concerns, and unfavorable terms.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/contract-risk-review",
    "version": "1.0.0",
    "display_name": "Contract Risk Review Agent",
    "description": "Scans contracts for risky clauses, evaluates compliance with internal policies, and produces renegotiation briefs with prioritized amendments.",
    "author": "AIBAST",
    "tags": ["contract", "risk", "legal", "compliance", "professional-services"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CONTRACTS = {
    "CTR-5001": {
        "client": "NovaTech Systems",
        "type": "Master Services Agreement",
        "value": 25000000,
        "term_months": 36,
        "governing_law": "Delaware",
        "renewal_date": "2028-06-30",
        "risk_score": 6.5,
        "pages": 47,
        "status": "under_review",
    },
    "CTR-5002": {
        "client": "Meridian Healthcare",
        "type": "Statement of Work",
        "value": 4200000,
        "term_months": 18,
        "governing_law": "New York",
        "renewal_date": "2027-09-15",
        "risk_score": 3.8,
        "pages": 22,
        "status": "active",
    },
    "CTR-5003": {
        "client": "Atlas Financial Group",
        "type": "Master Services Agreement",
        "value": 12000000,
        "term_months": 24,
        "governing_law": "California",
        "renewal_date": "2027-12-01",
        "risk_score": 5.2,
        "pages": 38,
        "status": "active",
    },
    "CTR-5004": {
        "client": "Orion Defense Systems",
        "type": "IDIQ Task Order",
        "value": 8500000,
        "term_months": 60,
        "governing_law": "Federal (FAR)",
        "renewal_date": "2030-03-31",
        "risk_score": 4.1,
        "pages": 64,
        "status": "active",
    },
}

CLAUSES = {
    "CTR-5001": [
        {"section": "7.1", "title": "Liability Cap", "risk": "HIGH",
         "issue": "Cap limited to fees paid in preceding 12 months ($2-8M range); no carve-outs for IP or data breach",
         "recommendation": "Increase to annual contract value ($8.3M minimum) with carve-outs"},
        {"section": "8.2", "title": "IP Ownership", "risk": "HIGH",
         "issue": "All work product assigned to client including improvements and derivatives; no pre-existing IP protection",
         "recommendation": "Carve out pre-existing IP; add license-back for client-specific derivatives"},
        {"section": "9.4", "title": "Payment Terms", "risk": "MEDIUM",
         "issue": "Net 60 days vs company standard Net 30; creates $1.4M cash-flow delay",
         "recommendation": "Negotiate to Net 30 or Net 45 with early-pay discount"},
        {"section": "12.1", "title": "Termination", "risk": "HIGH",
         "issue": "Client may terminate immediately for any breach with no cure period",
         "recommendation": "Add 30-day cure period for non-material breaches"},
        {"section": "14.3", "title": "SLA Penalties", "risk": "MEDIUM",
         "issue": "Penalties uncapped; could exceed monthly fees in extreme scenarios",
         "recommendation": "Cap penalties at 10% of monthly fees"},
        {"section": "15.2", "title": "Change Orders", "risk": "MEDIUM",
         "issue": "Verbal change approvals accepted; creates scope-creep exposure",
         "recommendation": "Require written change orders signed by authorized representatives"},
    ],
    "CTR-5003": [
        {"section": "5.1", "title": "Indemnification", "risk": "HIGH",
         "issue": "One-sided indemnification; we indemnify client but no reciprocal obligation",
         "recommendation": "Add mutual indemnification clause"},
        {"section": "6.3", "title": "Data Handling", "risk": "MEDIUM",
         "issue": "No data destruction timeline after engagement ends; liability lingers",
         "recommendation": "Add 90-day data destruction clause with certification"},
        {"section": "11.2", "title": "Non-Compete", "risk": "MEDIUM",
         "issue": "12-month non-compete for similar engagements in financial services sector",
         "recommendation": "Narrow scope to specific sub-sector or reduce to 6 months"},
    ],
}

COMPLIANCE_REQUIREMENTS = {
    "liability_cap_minimum": 5000000,
    "payment_terms_max_days": 45,
    "ip_preexisting_protection": True,
    "mutual_indemnification": True,
    "cure_period_days": 30,
    "data_destruction_clause": True,
    "change_order_written": True,
    "sla_penalty_cap_pct": 15,
}

RENEWAL_CALENDAR = [
    {"contract_id": "CTR-5002", "renewal_date": "2027-09-15", "days_out": 547, "action": "Begin renewal discussions Q1 2027"},
    {"contract_id": "CTR-5003", "renewal_date": "2027-12-01", "days_out": 624, "action": "Address risk clauses before renewal"},
    {"contract_id": "CTR-5001", "renewal_date": "2028-06-30", "days_out": 835, "action": "Renegotiate critical terms at Year-2 review"},
    {"contract_id": "CTR-5004", "renewal_date": "2030-03-31", "days_out": 1474, "action": "Option-year review in 2028"},
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _high_risk_count(contract_id):
    """Count HIGH-risk clauses for a contract."""
    return sum(1 for c in CLAUSES.get(contract_id, []) if c["risk"] == "HIGH")


def _compliance_gaps(contract_id):
    """Check contract clauses against compliance requirements."""
    gaps = []
    clauses = CLAUSES.get(contract_id, [])
    clause_titles = {c["title"].lower() for c in clauses}
    ctr = CONTRACTS[contract_id]

    # Check specific known issues
    for cl in clauses:
        if cl["risk"] in ("HIGH", "MEDIUM"):
            gaps.append({"clause": cl["title"], "section": cl["section"], "severity": cl["risk"],
                         "requirement": cl["recommendation"]})
    return gaps


def _total_exposure():
    """Sum the value of contracts with risk score above 5."""
    return sum(c["value"] for c in CONTRACTS.values() if c["risk_score"] >= 5.0)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class ContractRiskReviewAgent(BasicAgent):
    """Scans contracts for risk and generates compliance reports."""

    def __init__(self):
        self.name = "ContractRiskReviewAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "operations": [
                "risk_scan",
                "clause_analysis",
                "compliance_check",
                "renegotiation_brief",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "risk_scan")
        dispatch = {
            "risk_scan": self._risk_scan,
            "clause_analysis": self._clause_analysis,
            "compliance_check": self._compliance_check,
            "renegotiation_brief": self._renegotiation_brief,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _risk_scan(self, **kwargs) -> str:
        lines = ["## Contract Risk Scan\n"]
        exposure = _total_exposure()
        total_val = sum(c["value"] for c in CONTRACTS.values())
        lines.append(f"**Active contracts:** {len(CONTRACTS)}")
        lines.append(f"**Total contract value:** ${total_val:,.0f}")
        lines.append(f"**Value at elevated risk (score >= 5.0):** ${exposure:,.0f}\n")

        lines.append("| Contract | Client | Type | Value | Term | Risk Score | HIGH Issues |")
        lines.append("|----------|--------|------|-------|------|------------|-------------|")
        ranked = sorted(CONTRACTS.items(), key=lambda x: x[1]["risk_score"], reverse=True)
        for cid, c in ranked:
            hrc = _high_risk_count(cid)
            lines.append(
                f"| {cid} | {c['client']} | {c['type']} | ${c['value']:,.0f} | "
                f"{c['term_months']}mo | {c['risk_score']}/10 | {hrc} |"
            )

        lines.append("\n### Upcoming Renewals\n")
        lines.append("| Contract | Client | Renewal Date | Days Out | Action |")
        lines.append("|----------|--------|-------------|----------|--------|")
        for r in RENEWAL_CALENDAR:
            client = CONTRACTS[r["contract_id"]]["client"]
            lines.append(f"| {r['contract_id']} | {client} | {r['renewal_date']} | {r['days_out']} | {r['action']} |")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _clause_analysis(self, **kwargs) -> str:
        lines = ["## Clause-Level Risk Analysis\n"]
        for cid in CLAUSES:
            c = CONTRACTS[cid]
            lines.append(f"### {cid} -- {c['client']} (${c['value']:,.0f})\n")
            lines.append("| Section | Clause | Risk | Issue | Recommendation |")
            lines.append("|---------|--------|------|-------|----------------|")
            for cl in CLAUSES[cid]:
                lines.append(
                    f"| {cl['section']} | {cl['title']} | **{cl['risk']}** | "
                    f"{cl['issue'][:60]}... | {cl['recommendation'][:50]}... |"
                )
            high = sum(1 for cl in CLAUSES[cid] if cl["risk"] == "HIGH")
            med = sum(1 for cl in CLAUSES[cid] if cl["risk"] == "MEDIUM")
            lines.append(f"\n**Summary:** {high} HIGH, {med} MEDIUM risk clauses\n")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _compliance_check(self, **kwargs) -> str:
        lines = ["## Compliance Check Results\n"]
        lines.append("### Internal Policy Requirements\n")
        lines.append("| Requirement | Policy Standard |")
        lines.append("|-------------|----------------|")
        for key, val in COMPLIANCE_REQUIREMENTS.items():
            label = key.replace("_", " ").title()
            lines.append(f"| {label} | {val} |")

        lines.append("\n### Contract Compliance Status\n")
        for cid, c in CONTRACTS.items():
            gaps = _compliance_gaps(cid)
            status = "PASS" if not gaps else f"FAIL ({len(gaps)} gaps)"
            lines.append(f"#### {cid} -- {c['client']} -- **{status}**\n")
            if gaps:
                lines.append("| Clause | Section | Severity | Required Action |")
                lines.append("|--------|---------|----------|-----------------|")
                for g in gaps:
                    lines.append(f"| {g['clause']} | {g['section']} | {g['severity']} | {g['requirement']} |")
                lines.append("")
            else:
                lines.append("All compliance requirements met.\n")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _renegotiation_brief(self, **kwargs) -> str:
        lines = ["## Renegotiation Brief\n"]
        # Focus on highest-risk contracts
        high_risk = [(cid, c) for cid, c in CONTRACTS.items() if c["risk_score"] >= 5.0]
        high_risk.sort(key=lambda x: x[1]["risk_score"], reverse=True)

        for cid, c in high_risk:
            clauses = CLAUSES.get(cid, [])
            lines.append(f"### {cid} -- {c['client']}")
            lines.append(f"- **Value:** ${c['value']:,.0f} over {c['term_months']} months")
            lines.append(f"- **Risk score:** {c['risk_score']}/10")
            lines.append(f"- **Governing law:** {c['governing_law']}")
            lines.append(f"- **Renewal:** {c['renewal_date']}\n")

            non_negotiable = [cl for cl in clauses if cl["risk"] == "HIGH"]
            negotiable = [cl for cl in clauses if cl["risk"] == "MEDIUM"]

            if non_negotiable:
                lines.append("**Non-Negotiable Amendments (must resolve):**")
                for i, cl in enumerate(non_negotiable, 1):
                    lines.append(f"{i}. **{cl['title']}** (Section {cl['section']}): {cl['recommendation']}")
            if negotiable:
                lines.append("\n**Preferred Amendments:**")
                for i, cl in enumerate(negotiable, 1):
                    lines.append(f"{i}. **{cl['title']}** (Section {cl['section']}): {cl['recommendation']}")

            lines.append("\n**Negotiation strategy:**")
            lines.append(f"- Lead with non-negotiable items; concede on lower-priority terms if needed")
            lines.append(f"- Fallback: accept current value on MEDIUM items if all HIGH items resolved")
            lines.append(f"- Escalation path: General Counsel review if impasse on liability cap")
            lines.append("")

        total_risk_val = sum(c["value"] for _, c in high_risk)
        lines.append(f"**Total contract value requiring renegotiation:** ${total_risk_val:,.0f}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ContractRiskReviewAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
