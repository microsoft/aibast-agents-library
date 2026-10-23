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
    "version": "1.2.0",
    "display_name": "Contract Risk Review Agent",
    "description": "Automate contract review processes to enable faster, lower-risk, and more successful negotiations.",
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
         "recommendation": "Increase cap to $10M with carve-outs (IP indemnity, data breach, gross negligence); fallback minimum $8.3M (annual contract value)",
         "critical": "Liability exposure: Cap limited to prior 12 months fees ($2-8M)"},
        {"section": "8.2", "title": "IP Ownership", "risk": "HIGH",
         "issue": "All work product assigned to client including improvements and derivatives; no pre-existing IP protection",
         "recommendation": "Carve out pre-existing IP; add license-back for client-specific derivatives",
         "critical": "IP ownership: ALL work product assigned to client"},
        {"section": "9.4", "title": "Payment Terms", "risk": "MEDIUM",
         "issue": "Net 60 days vs company standard Net 30; creates $1.4M cash-flow delay",
         "recommendation": "Change to Net 30 payment terms",
         "critical": "Payment terms: Net 60 vs standard Net 30"},
        {"section": "12.1", "title": "Termination", "risk": "HIGH",
         "issue": "Client may terminate immediately for any breach with no cure period",
         "recommendation": "Add 30-day cure period for termination",
         "critical": "Termination: No cure period, immediate for any breach"},
        {"section": "14.3", "title": "SLA Penalties", "risk": "MEDIUM",
         "issue": "Penalties uncapped; could exceed monthly fees in extreme scenarios",
         "recommendation": "Cap SLA penalties at 10% of monthly fees",
         "critical": "SLA penalties: Uncapped, could exceed monthly fees"},
        {"section": "15.2", "title": "Change Orders", "risk": "MEDIUM",
         "issue": "Verbal change approvals accepted; creates scope-creep exposure",
         "recommendation": "Require written change orders signed by authorized representatives",
         "critical": "Change orders: Verbal approval accepted (risky)"},
        {"section": "7.3", "title": "Indemnification", "risk": "HIGH",
         "issue": "One-sided: we indemnify the client, the client does not indemnify us",
         "recommendation": "Add mutual indemnification"},
        {"section": "16.1", "title": "Dispute Resolution", "risk": "MEDIUM",
         "issue": "Litigation-first with no executive escalation or mediation step; high legal costs",
         "recommendation": "Add escalation before litigation"},
        {"section": "3.2", "title": "Auto-Renewal", "risk": "MEDIUM",
         "issue": "Auto-renews with an unfavorable rate lock preventing price adjustments",
         "recommendation": "Remove auto-renewal"},
        {"section": "5.4", "title": "Resource Replacement", "risk": "MEDIUM",
         "issue": "Client has unilateral right to replace our team members",
         "recommendation": "Limit resource replacement rights"},
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
    "liability_cap_minimum": 8300000,
    "payment_terms_max_days": 30,
    "ip_preexisting_protection": True,
    "mutual_indemnification": True,
    "cure_period_days": 30,
    "data_destruction_clause": True,
    "change_order_written": True,
    "sla_penalty_cap_pct": 10,
}

SYNTHETIC_SNAPSHOT_DATE = "2026-03-17"

RENEWAL_CALENDAR = [
    {"contract_id": "CTR-5002", "renewal_date": "2027-09-15", "days_out": 547, "action": "Begin renewal discussions Q1 2027"},
    {"contract_id": "CTR-5003", "renewal_date": "2027-12-01", "days_out": 624, "action": "Address risk clauses before renewal"},
    {"contract_id": "CTR-5001", "renewal_date": "2028-06-30", "days_out": 835, "action": "Renegotiate critical terms at Year-2 review"},
    {"contract_id": "CTR-5004", "renewal_date": "2030-03-31", "days_out": 1474, "action": "Option-year review in 2028"},
]

# NovaTech MSA (CTR-5001) deep-dive records used by the guided review.
LIABILITY_MODEL = {
    "current_cap": "Fees paid in preceding 12 months",
    "exposure_min": 2000000,     # 12-month fees early in the project
    "exposure_max": 8000000,     # 12-month fees in later stages
    "damages_low": 10000000,     # plausible claim range for this engagement
    "damages_high": 20000000,
    "preferred_floor": 10000000,
    "missing_carve_outs": ["IP indemnity", "data breach", "gross negligence"],
    "insurance_gap": "Current E&O coverage insufficient for $10M+ exposure",
}

IP_SECTION = {
    "section": "8.2",
    "current_language": [
        "ALL work product assigned to client",
        "Includes improvements and derivatives",
        "No distinction for pre-existing IP",
        "No license-back provision",
        "No restrictions on client use",
    ],
    "risk_scenario": [
        "We develop valuable accelerator during engagement",
        "Client owns it completely",
        "Client can use it with our competitors",
        "Client can sell it in the market",
        "We can't reuse our own innovation",
    ],
    "protections": [
        "Carve-out for pre-existing methodologies",
        "License-back for client-specific work",
        "Restriction: Client use only, no resale",
        'Define "work product" narrowly',
    ],
}

# (group, amendment, current text, proposed text, non-negotiable)
AMENDMENTS = [
    ("Liability Protection", "Increase cap to $10M", "Cap = fees paid in preceding 12 months",
     "Cap = $10,000,000 per claim", True),
    ("Liability Protection", "Add mutual indemnification", "Provider indemnifies client only",
     "Each party indemnifies the other", True),
    ("Liability Protection", "Carve-outs: IP, data breach, gross negligence", "No carve-outs",
     "IP indemnity, data breach and gross negligence sit outside the cap", True),
    ("IP Protection", "Protect pre-existing methodologies", "ALL work product assigned to client",
     "Pre-existing IP and methodologies remain with provider", True),
    ("IP Protection", "License-back for client-specific work", "No license-back",
     "Provider receives a license-back to client-specific derivatives", True),
    ("IP Protection", "Restrict client resale rights", "No restrictions on client use",
     "Client use only; no resale or transfer to third parties", True),
    ("IP Protection", 'Define "work product" narrowly', "Work product includes improvements and derivatives",
     "Work product = deliverables named in each SOW", False),
    ("Payment & Termination", "Change to Net 30 payment terms", "Net 60", "Net 30", False),
    ("Payment & Termination", "Add 30-day cure period for termination", "Immediate termination for any breach",
     "30-day written cure period before termination", False),
    ("Payment & Termination", "Cap SLA penalties at 10% of monthly fees", "Uncapped SLA penalties",
     "SLA penalties capped at 10% of monthly fees", False),
    ("Additional Amendments", "Require written change orders", "Verbal approval accepted",
     "Signed written change orders only", False),
    ("Additional Amendments", "Escalation before litigation", "Litigation-first",
     "Executive escalation, then mediation, before litigation", False),
    ("Additional Amendments", "Remove auto-renewal", "Auto-renewal with rate lock",
     "Renewal by mutual written agreement with rate review", False),
    ("Additional Amendments", "Limit resource replacement rights", "Client may replace team members unilaterally",
     "Replacement for documented cause with 15 days notice", False),
]

DELIVERABLES = [
    ("Redlined MSA", "{n} tracked changes (draft text below, ready for Word)"),
    ("Executive memo", "3-page risk summary with rationale (outline below)"),
    ("Fallback positions", "Tiered negotiation strategy"),
    ("Comparable terms", "Industry contract references"),
    ("Insurance review", "$10M E&O coverage to raise with your broker"),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _money_m(value):
    """$25M / $8.3M style label."""
    m = value / 1000000
    return f"${m:.1f}M".replace(".0M", "M")


def _range_m(low, high):
    """$2-18M style range label."""
    return f"${low / 1000000:g}-{high / 1000000:g}M"


def _resolve_contract(query, default="CTR-5001"):
    """Contract id or client name (or part of it); 'all' for the portfolio; None when nothing matches."""
    if not query:
        return default
    q = str(query).lower().strip()
    if q in ("all", "portfolio", "every", "all contracts"):
        return "all"
    for cid, c in CONTRACTS.items():
        if cid.lower() in q or q in cid.lower() or q in c["client"].lower() or c["client"].lower() in q:
            return cid
    return None


def _annual_value(contract_id):
    c = CONTRACTS[contract_id]
    return round(c["value"] * 12 / c["term_months"])


def _monthly_fees(contract_id):
    c = CONTRACTS[contract_id]
    return round(c["value"] / c["term_months"])


def _cash_delay(contract_id):
    """Average billings outstanding under Net 60 (two months of fees)."""
    return _monthly_fees(contract_id) * 2


def _high_risk_count(contract_id):
    """Count HIGH-risk clauses for a contract."""
    return sum(1 for c in CLAUSES.get(contract_id, []) if c["risk"] == "HIGH")


def _compliance_gaps(contract_id):
    """Return documented policy gaps, or None when clause evidence is absent."""
    if contract_id not in CLAUSES:
        return None
    gaps = []
    clauses = CLAUSES.get(contract_id, [])
    for cl in clauses:
        if cl["risk"] in ("HIGH", "MEDIUM"):
            gaps.append({"clause": cl["title"], "section": cl["section"], "severity": cl["risk"],
                         "requirement": cl["recommendation"]})
    return gaps


def _total_exposure():
    """Sum the value of contracts with risk score above 5."""
    return sum(c["value"] for c in CONTRACTS.values() if c["risk_score"] >= 5.0)


def _risk_label(score):
    if score >= 7:
        return "High"
    if score >= 6:
        return "Medium-High"
    if score >= 4:
        return "Medium"
    return "Low"


_REVIEW_NOTE = "> Draft positions for authorized counsel review; no amendment has been sent or accepted."
_UNKNOWN = "No synthetic contract matches '{q}'. Known agreements: {ids}."


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "risk_scan",
    "clause_analysis",
    "compliance_check",
    "renegotiation_brief",
    "contract_overview",
    "liability_analysis",
    "ip_analysis",
    "additional_risks",
    "redline_summary",
]


class ContractRiskReviewAgent(BasicAgent):
    """Scans contracts for risk and generates compliance reports."""

    def __init__(self):
        self.name = "ContractRiskReviewAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "The required tool for any professional-services agreement, contract, clause, "
                "or MSA question. Always invoke it instead of giving generic guidance when a "
                "legal-operations director, attorney, or executive asks to review an agreement "
                "(for example the NovaTech Systems MSA, $25M over 3 years) before signing; which "
                "agreements need counsel first; what drives priority; what liability-cap, IP "
                "ownership, payment-term, termination, SLA, indemnity, data, non-compete, or "
                "change-order language needs attention; where contract evidence is incomplete "
                "against internal policy; or what amendments, negotiation positions, fallbacks, "
                "redlines and escalation points to prepare. The packaged synthetic portfolio is "
                "sufficient and the NovaTech MSA (CTR-5001) is the default agreement, so do not "
                "ask the user to identify or upload an agreement. This tool provides review "
                "support only and never gives legal advice or changes a contract."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "Choose from plain-language intent, not operation words. "
                            "contract_overview: review an agreement someone just sent (e.g. the "
                            "NovaTech MSA before a signing meeting): overview, risk score, critical "
                            "issues. liability_analysis: what is wrong with the liability "
                            "provisions, cap, exposure, indemnity, carve-outs, insurance. "
                            "ip_analysis: IP ownership problems, Section 8.2. additional_risks: "
                            "other or additional risk factors (payment, termination, SLA, change "
                            "orders, disputes, auto-renewal). renegotiation_brief: the full amendment "
                            "list with priorities, recommended amendments, negotiation positions, "
                            "fallbacks, non-negotiables, and counsel escalation points. redline_summary: "
                            "ONLY when the user explicitly asks to generate the redline, executive summary "
                            "or memo (it returns draft text; no file is created). Call exactly one "
                            "operation per question. risk_scan: which agreements "
                            "go to counsel first, priority, ranking, or renewal queue across the "
                            "portfolio. clause_analysis: walk through MSA language, Liability Cap, IP "
                            "Ownership, Payment Terms, or other risky clauses in a table. "
                            "compliance_check: compare evidence with internal policy, find gaps, or "
                            "identify an incomplete file."
                        ),
                    },
                    "contract_id": {
                        "type": "string",
                        "description": (
                            "Contract id or client name (default CTR-5001, NovaTech Systems); "
                            "'all' for every agreement in clause_analysis or renegotiation_brief."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "contract_overview")
        dispatch = {
            "risk_scan": self._risk_scan,
            "clause_analysis": self._clause_analysis,
            "compliance_check": self._compliance_check,
            "renegotiation_brief": self._renegotiation_brief,
            "contract_overview": self._contract_overview,
            "liability_analysis": self._liability_analysis,
            "ip_analysis": self._ip_analysis,
            "additional_risks": self._additional_risks,
            "redline_summary": self._redline_summary,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        cid = _resolve_contract(kwargs.get("contract_id"))
        if cid is None:
            return _UNKNOWN.format(q=kwargs.get("contract_id"), ids=", ".join(
                f"{k} ({v['client']})" for k, v in CONTRACTS.items()))
        if operation in ("contract_overview", "liability_analysis", "ip_analysis",
                         "additional_risks", "redline_summary") and cid != "CTR-5001":
            c = CONTRACTS.get(cid, {})
            return (f"The detailed clause review is packaged for CTR-5001 (NovaTech Systems) only. "
                    f"{cid} ({c.get('client', 'portfolio')}) has portfolio-level records: ask for "
                    f"the risk scan or compliance check.\n\n{_REVIEW_NOTE}")
        return handler(contract_id=cid)

    # ------------------------------------------------------------------
    def _contract_overview(self, contract_id="CTR-5001") -> str:
        c = CONTRACTS[contract_id]
        critical = [cl["critical"] for cl in CLAUSES[contract_id] if cl.get("critical")]
        years = c["term_months"] // 12
        return (
            f"I've analyzed the {c['pages']}-page {c['client']} MSA and identified significant risk "
            f"exposure requiring {len(AMENDMENTS)} amendments before signing. Risk rating: "
            f"{c['risk_score']}/10 ({_risk_label(c['risk_score']).lower()}).\n\n"
            f"## Contract Overview\n\n"
            f"| Element | Details |\n|---|---|\n"
            f"| Agreement type | {c['type']} |\n"
            f"| Total value | {_money_m(c['value'])} over {c['term_months']} months ({years} years) |\n"
            f"| Client | {c['client']} Inc |\n"
            f"| Governing law | {c['governing_law']} |\n"
            f"| Pages analyzed | {c['pages']} |\n"
            f"| Risk score | {c['risk_score']}/10 ({_risk_label(c['risk_score'])}) |\n\n"
            f"**Critical Issues Identified ({len(critical)}):**\n"
            + "\n".join(f"- {x}" for x in critical) + "\n\n"
            f"Source: [Synthetic contract record + Contract Analysis]\n\n"
            f"Review support only; contract decisions require authorized legal counsel.\n\n"
            f"Want details on the liability exposure?"
        )

    # ------------------------------------------------------------------
    def _liability_analysis(self, contract_id="CTR-5001") -> str:
        lm = LIABILITY_MODEL
        annual = _annual_value(contract_id)
        gap_low = lm["damages_low"] - lm["exposure_max"]
        gap_high = lm["damages_high"] - lm["exposure_min"]
        carve = "\n".join(f"- No carve-outs for {x}" for x in lm["missing_carve_outs"])
        return (
            f"The liability cap is dangerously low and one-sided: we could face "
            f"{_money_m(lm['damages_low'])}+ in damages with only {_money_m(lm['exposure_min'])} "
            f"protection, and they don't indemnify us at all.\n\n"
            f"## Liability Problems (Section 7.1)\n\n"
            f"**Current Cap:** \"{lm['current_cap']}\"\n"
            f"- Minimum exposure: {_money_m(lm['exposure_min'])} (early project)\n"
            f"- Maximum exposure: {_money_m(lm['exposure_max'])} (later stages)\n"
            f"- Gap to damages: could be {_range_m(gap_low, gap_high)} shortfall "
            f"(against {_range_m(lm['damages_low'], lm['damages_high'])} potential damages)\n\n"
            f"**Industry Standards:**\n"
            f"- Minimum: Annual contract value ({_money_m(annual)})\n"
            f"- Preferred: Greater of annual value or {_money_m(lm['preferred_floor'])}\n"
            f"- **Our recommendation: {_money_m(max(annual, lm['preferred_floor']))} with carve-outs**\n\n"
            f"**Missing Protections:**\n{carve}\n"
            f"- One-sided (Section 7.3): We indemnify them, they don't indemnify us\n\n"
            f"**Insurance Gap:** {lm['insurance_gap']}\n\n"
            f"Source: [Contract Benchmarking + Insurance Analysis] (synthetic)\n\n"
            f"{_REVIEW_NOTE}\n\n"
            f"What about the IP ownership issues?"
        )

    # ------------------------------------------------------------------
    def _ip_analysis(self, contract_id="CTR-5001") -> str:
        ip = IP_SECTION
        return (
            f"Section {ip['section']} assigns ALL intellectual property to the client with no protection "
            f"for our pre-existing methods or license-back for derivatives: they could sell our "
            f"accelerators to competitors.\n\n"
            f"## IP Ownership Issues\n\n"
            f"**Current Language (Section {ip['section']}):**\n"
            + "\n".join(f"- {x}" for x in ip["current_language"]) + "\n\n"
            f"**Risk Scenario:**\n"
            + "\n".join(f"- {x}" for x in ip["risk_scenario"]) + "\n\n"
            f"**Required Protections:**\n"
            + "\n".join(f"- {x}" for x in ip["protections"]) + "\n\n"
            f"Source: [IP Risk Analysis + Standard Templates] (synthetic)\n\n"
            f"{_REVIEW_NOTE}\n\n"
            f"What other risks did you find?"
        )

    # ------------------------------------------------------------------
    def _additional_risks(self, contract_id="CTR-5001") -> str:
        c = CONTRACTS[contract_id]
        delay = _cash_delay(contract_id)
        rows = [
            ("Payment", "Net 60 days", f"{_money_m(delay)} delayed cash flow"),
            ("Termination", "Immediate, no cure", f"Loss of {_money_m(c['value'])} revenue"),
            ("SLA penalties", "Uncapped", "Could exceed monthly fees"),
            ("Change orders", "Verbal OK", "Scope creep exposure"),
            ("Disputes", "Litigation-first", "High legal costs"),
        ]
        table = "\n".join(f"| {a} | {b} | {d} |" for a, b, d in rows)
        return (
            f"{len(rows)} more significant issues: payment delays, immediate termination rights, "
            f"uncapped penalties, verbal change orders, and unfavorable dispute resolution.\n\n"
            f"## Additional Risks\n\n"
            f"| Risk | Current Terms | Impact |\n|---|---|---|\n{table}\n\n"
            f"- **Cash Flow Impact:** Net 60 delays {_money_m(delay)} on average (two months of "
            f"${_monthly_fees(contract_id):,} monthly fees) vs Net 30 standard\n"
            f"- **Termination Risk:** No 30-day cure period means instant contract loss for a minor breach\n"
            f"- **Auto-Renewal:** Yes, with an unfavorable rate lock preventing price adjustments\n"
            f"- **Resource Control:** Client has unilateral right to replace our team members\n\n"
            f"Source: [Payment Analysis + Risk Modeling] (synthetic)\n\n"
            f"{_REVIEW_NOTE}\n\n"
            f"What amendments are you recommending?"
        )

    # ------------------------------------------------------------------
    def _redline_summary(self, contract_id="CTR-5001") -> str:
        c = CONTRACTS[contract_id]
        lm = LIABILITY_MODEL
        annual = _annual_value(contract_id)
        n = len(AMENDMENTS)
        changes = "\n".join(
            f"| {i} | {name} | {cur} | {new} |"
            for i, (_g, name, cur, new, _nn) in enumerate(AMENDMENTS, 1)
        )
        deliver = "\n".join(f"- **{a}:** {b.format(n=n)}" for a, b in DELIVERABLES)
        return (
            f"Redlined MSA and executive memo drafted for your legal team, ready for you to review "
            f"and upload to your contract workspace. Nothing has been uploaded, sent or flagged.\n\n"
            f"## Deliverables (drafts)\n\n{deliver}\n\n"
            f"### Redline: {n} tracked changes\n\n"
            f"| # | Change | Original | Proposed |\n|---|---|---|---|\n{changes}\n\n"
            f"### Executive memo outline (3 pages)\n"
            f"1. Risk summary: {c['client']} MSA, {_money_m(c['value'])} over {c['term_months']} months, "
            f"risk {c['risk_score']}/10\n"
            f"2. Rationale for the {n} amendments (liability, IP, payment and termination, additional)\n"
            f"3. Negotiation boundaries and fallback positions\n\n"
            f"**Key Talking Points:**\n"
            f"- Risk score: {c['risk_score']}/10 requires amendments\n"
            f"- Liability exposure: {_range_m(lm['damages_low'] - lm['exposure_max'], lm['damages_high'] - lm['exposure_min'])} gap\n"
            f"- IP risk: Complete ownership transfer\n"
            f"- Cash flow impact: {_money_m(_cash_delay(contract_id))} delayed\n"
            f"- Termination: No cure period\n\n"
            f"**Negotiation Strategy:**\n"
            f"- Target: {_money_m(lm['preferred_floor'])} liability cap with carve-outs\n"
            f"- Minimum: {_money_m(annual)} with mutual indemnification\n"
            f"- Alternative: Tiered caps by violation type\n\n"
            f"Source: [Synthetic contract record + Legal Benchmarking]\n\n"
            f"{_REVIEW_NOTE} Synthetic draft for counsel; this is not legal advice."
        )

    # ------------------------------------------------------------------
    def _risk_scan(self, **kwargs) -> str:
        lines = ["## Contract Risk Scan\n"]
        lines.append(f"> Synthetic portfolio snapshot: {SYNTHETIC_SNAPSHOT_DATE}.")
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
        lines.append("\n> Review support only; contract decisions require authorized legal counsel.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _clause_analysis(self, contract_id="CTR-5001") -> str:
        lines = ["## Clause-Level Risk Analysis\n"]
        ids = list(CLAUSES) if contract_id == "all" else [contract_id]
        for cid in ids:
            c = CONTRACTS[cid]
            lines.append(f"### {cid} -- {c['client']} (${c['value']:,.0f})\n")
            if cid not in CLAUSES:
                lines.append("No clause evidence is packaged for this contract.\n")
                continue
            lines.append("| Section | Clause | Risk | Issue | Recommendation |")
            lines.append("|---------|--------|------|-------|----------------|")
            for cl in CLAUSES[cid]:
                lines.append(
                    f"| {cl['section']} | {cl['title']} | **{cl['risk']}** | "
                    f"{cl['issue']} | {cl['recommendation']} |"
                )
            high = sum(1 for cl in CLAUSES[cid] if cl["risk"] == "HIGH")
            med = sum(1 for cl in CLAUSES[cid] if cl["risk"] == "MEDIUM")
            lines.append(f"\n**Summary:** {high} HIGH, {med} MEDIUM risk clauses\n")
        lines.append("> Synthetic clause excerpts; findings are not legal advice or a complete contract opinion.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _compliance_check(self, **kwargs) -> str:
        r = COMPLIANCE_REQUIREMENTS
        lines = ["## Compliance Check Results\n"]
        lines.append("### Internal Policy Requirements\n")
        lines.append("| Requirement | Policy Standard |")
        lines.append("|-------------|----------------|")
        lines.append(f"| Liability Cap Minimum | ${r['liability_cap_minimum']:,} (annual contract value) |")
        lines.append(f"| Payment Terms Max Days | Net {r['payment_terms_max_days']} |")
        lines.append(f"| Ip Preexisting Protection | {'Required' if r['ip_preexisting_protection'] else 'Optional'} |")
        lines.append(f"| Mutual Indemnification | {'Required' if r['mutual_indemnification'] else 'Optional'} |")
        lines.append(f"| Cure Period Days | {r['cure_period_days']} days |")
        lines.append(f"| Data Destruction Clause | {'Required' if r['data_destruction_clause'] else 'Optional'} |")
        lines.append(f"| Change Order Written | {'Required' if r['change_order_written'] else 'Optional'} |")
        lines.append(f"| Sla Penalty Cap Pct | {r['sla_penalty_cap_pct']}% of monthly fees |")

        lines.append("\n### Contract Compliance Status\n")
        for cid, c in CONTRACTS.items():
            gaps = _compliance_gaps(cid)
            if gaps is None:
                lines.append(f"#### {cid} -- {c['client']} -- **REVIEW REQUIRED**\n")
                lines.append("No clause evidence is packaged for this contract; no compliance conclusion can be made.\n")
                continue
            status = "PASS" if not gaps else f"GAPS FOUND ({len(gaps)})"
            lines.append(f"#### {cid} -- {c['client']} -- **{status}**\n")
            if gaps:
                lines.append("| Clause | Section | Severity | Required Action |")
                lines.append("|--------|---------|----------|-----------------|")
                for g in gaps:
                    lines.append(f"| {g['clause']} | {g['section']} | {g['severity']} | {g['requirement']} |")
                lines.append("")
            else:
                lines.append("All compliance requirements met.\n")
        lines.append("> Internal-policy screening only; this is not a legal or regulatory compliance determination.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _renegotiation_brief(self, contract_id="CTR-5001") -> str:
        lines = ["## Renegotiation Brief\n"]
        if contract_id == "all":
            ids = [cid for cid, c in sorted(CONTRACTS.items(), key=lambda x: x[1]["risk_score"], reverse=True)
                   if c["risk_score"] >= 5.0]
        else:
            ids = [contract_id]
        for cid in ids:
            c = CONTRACTS[cid]
            lines.append(f"### {cid} -- {c['client']}")
            lines.append(f"- **Value:** ${c['value']:,.0f} over {c['term_months']} months")
            lines.append(f"- **Risk score:** {c['risk_score']}/10")
            lines.append(f"- **Governing law:** {c['governing_law']}\n")
            if cid == "CTR-5001":
                n = len(AMENDMENTS)
                must = [a for a in AMENDMENTS if a[4]]
                lines.append(f"{n} critical amendments required before signing. Top {len(must)} are "
                             f"non-negotiable for risk protection.\n")
                lines.append("**Non-Negotiable Amendments (must resolve):**")
                for i, a in enumerate(must, 1):
                    lines.append(f"{i}. **{a[0]}:** {a[1]}")
                lines.append("\n**All amendments by priority group:**")
                group = None
                for i, a in enumerate(AMENDMENTS, 1):
                    if a[0] != group:
                        group = a[0]
                        lines.append(f"\n*{group}:*")
                    lines.append(f"{i}. {a[1]}{' (non-negotiable)' if a[4] else ''}")
                lines.append(f"\n**Fallback Position:** Minimum {_money_m(_annual_value(cid))} liability "
                             f"(annual value) with mutual indemnification and critical carve-outs")
                lines.append("**Alternative:** Tiered caps by violation type")
            else:
                clauses = CLAUSES.get(cid, [])
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
                lines.append("- Fallback: accept current value on MEDIUM items if all HIGH items resolved")
            lines.append("- Escalation path: General Counsel review if impasse on liability cap\n")
        lines.append("Source: [Legal Benchmarking + Industry Comparisons] (synthetic)\n")
        lines.append(_REVIEW_NOTE)
        lines.append("\nReady for the redline document?")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ContractRiskReviewAgent()
    for op in ["contract_overview", "liability_analysis", "ip_analysis",
               "additional_risks", "renegotiation_brief", "redline_summary"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
