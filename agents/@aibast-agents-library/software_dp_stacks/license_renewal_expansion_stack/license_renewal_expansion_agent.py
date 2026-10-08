"""
License Renewal and Expansion Agent for Software/Digital Products.

Manages SaaS license renewal pipelines, identifies expansion opportunities,
assesses churn risk, and projects revenue impact across the customer portfolio.

Demo scenario (synthetic): the strategic account GlobalBank (LIC-3000) renews in
45 days with 2,000 seats at $1.0M ARR, 500 users waitlisted, and a competitor
offering a 30% discount. Account-level operations default to GlobalBank:
account health, competitive defense, renewal + expansion proposal, executive
brief, negotiation plan with required approvers, and the deal summary. Every
proposal, approval and message is a draft; nothing is approved or sent.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/license-renewal-expansion",
    "version": "1.0.0",
    "display_name": "License Renewal and Expansion Agent",
    "description": "Streamline subscription renewal management and expansion planning, turning risk into growth opportunities while increasing win probability.",
    "author": "AIBAST",
    "tags": ["license", "renewal", "expansion", "churn", "revenue", "saas"],
    "category": "software_digital_products",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

DEMO_AS_OF = "2026-03-16"

LICENSE_AGREEMENTS = {
    "LIC-3000": {
        "customer": "GlobalBank",
        "plan": "Enterprise",
        "arr": 1000000,
        "seats": 2000,
        "seats_used": 1987,
        "renewal_date": "2026-04-30",
        "contract_start": "2025-04-30",
        "usage_trend": "increasing",
        "nps_score": 72,
        "support_tickets_90d": 3,
        "expansion_signals": ["Waitlist demand: 500 users", "12 of 15 modules actively used"],
        "churn_signals": ["Competitor offer: FinTech Solutions at a 30% discount"],
        "csm": "Dana Reeves",
        "health_score": 87,
    },
    "LIC-3001": {
        "customer": "Pinnacle Insurance Corp",
        "plan": "Enterprise",
        "arr": 288000,
        "seats": 150,
        "seats_used": 142,
        "renewal_date": "2026-04-30",
        "contract_start": "2025-04-30",
        "usage_trend": "increasing",
        "nps_score": 72,
        "support_tickets_90d": 4,
        "expansion_signals": ["API usage +45% QoQ", "Requested SSO for 3 subsidiaries"],
        "churn_signals": [],
        "csm": "Dana Reeves",
        "health_score": 88,
    },
    "LIC-3002": {
        "customer": "ClearView Analytics",
        "plan": "Professional",
        "arr": 72000,
        "seats": 30,
        "seats_used": 18,
        "renewal_date": "2026-05-15",
        "contract_start": "2025-05-15",
        "usage_trend": "declining",
        "nps_score": 34,
        "support_tickets_90d": 18,
        "expansion_signals": [],
        "churn_signals": ["Usage down 32%", "Executive sponsor departed", "Competitor eval detected"],
        "csm": "James Okafor",
        "health_score": 29,
    },
    "LIC-3003": {
        "customer": "Redwood Supply Chain",
        "plan": "Enterprise",
        "arr": 192000,
        "seats": 80,
        "seats_used": 79,
        "renewal_date": "2026-06-01",
        "contract_start": "2025-06-01",
        "usage_trend": "stable",
        "nps_score": 65,
        "support_tickets_90d": 7,
        "expansion_signals": ["Inquired about analytics add-on"],
        "churn_signals": ["Budget freeze mentioned in QBR"],
        "csm": "Dana Reeves",
        "health_score": 62,
    },
    "LIC-3004": {
        "customer": "Skyline Hospitality Group",
        "plan": "Enterprise",
        "arr": 360000,
        "seats": 250,
        "seats_used": 248,
        "renewal_date": "2026-04-15",
        "contract_start": "2025-04-15",
        "usage_trend": "increasing",
        "nps_score": 85,
        "support_tickets_90d": 2,
        "expansion_signals": ["Opening 12 new locations", "Requested bulk seat pricing", "Custom integration POC"],
        "churn_signals": [],
        "csm": "James Okafor",
        "health_score": 94,
    },
    "LIC-3005": {
        "customer": "Granite Construction Co",
        "plan": "Professional",
        "arr": 54000,
        "seats": 20,
        "seats_used": 12,
        "renewal_date": "2026-07-01",
        "contract_start": "2025-07-01",
        "usage_trend": "declining",
        "nps_score": 41,
        "support_tickets_90d": 11,
        "expansion_signals": [],
        "churn_signals": ["Primary admin inactive 45 days", "Missed last 2 QBRs"],
        "csm": "Dana Reeves",
        "health_score": 35,
    },
}

EXPANSION_PRICING = {
    "additional_seats": {"unit_price": 120, "min_qty": 10},
    "analytics_addon": {"price": 24000, "description": "Advanced analytics module"},
    "api_premium": {"price": 18000, "description": "Premium API tier with higher rate limits"},
    "sso_subsidiary": {"price": 12000, "description": "SSO extension per subsidiary"},
    "custom_integration": {"price": 36000, "description": "Custom integration package"},
}

SWITCHING_COST_ASSUMPTIONS = {
    "data_migration": 180000,
    "user_retraining": 120000,
    "integration_rebuild": 200000,
}

# Strategic-account detail for the demo account (GlobalBank)
ACCOUNT_DETAILS = {
    "LIC-3000": {
        "waitlist_users": 500,
        "modules_used": 12,
        "modules_total": 15,
        "api_calls_month": "2.3M",
        "api_growth_mom_pct": 15,
        "documented_savings": 4200000,
        "competitor": {
            "vendor": "FinTech Solutions",
            "discount_pct": 30,
            "migration_offer": 0,
            "feature_parity_pct": 78,
            "integration_time": "4-6 months",
        },
        "switching_detail": {
            "data_migration": "6-week project",
            "user_retraining": "2,000 users, plus productivity loss",
            "integration_rebuild": "8 custom connections",
        },
        "decision_maker": "VP of Technology",
    },
}

RENEWAL_TERMS = {
    "matched_discount_pct": 30,
    "multi_year_discount_pct": 10,
    "term_years": 3,
    "premium_support_value": 60000,
    "counter_strategy": [
        "Match their 30% discount on renewal",
        "Add premium support ($60K value) at no charge",
        "Lock a 3-year term for stability",
        "Include an executive roadmap session",
    ],
}

EXECUTIVE_BRIEF = {
    "slides": [
        "Title - GlobalBank strategic partnership renewal",
        "Partnership Value - $4.2M savings delivered",
        "Usage Success - 99.4% adoption, 12 modules active",
        "Growth Support - 500 new seats for waitlisted teams",
        "Competitive Comparison - TCO analysis showing $500K switching cost",
        "Proposal Summary - 2,500 seats, 3-year commitment",
        "Roadmap Preview - features launching in the next 12 months",
        "Next Steps - executive decision 30 days before expiry",
    ],
    "talking_points": [
        "You've realized $4.2M in savings - 5x your investment",
        "Switching costs $500K+ before any productivity loss",
        "We're matching their price AND adding premium support",
        "A 3-year term locks in today's pricing against inflation",
    ],
    "objection_handlers": 12,
}

CONCESSION_POLICY = [
    {"lever": "Discount", "floor": "30%", "target": "25%", "approver": "Pre-approved policy for a 3-year term"},
    {"lever": "Term", "floor": "1 year", "target": "3 years", "approver": "None (standard)"},
    {"lever": "Payment", "floor": "Net 60", "target": "Annual upfront", "approver": "Finance"},
    {"lever": "Premium support", "floor": "Included", "target": "Included", "approver": "VP Sales"},
    {"lever": "Implementation", "floor": "$0", "target": "$0 for new modules", "approver": "VP Sales"},
]

APPROVAL_ROUTING = [
    "Finance: request confirmation of the 30% discount for a 3-year term",
    "Legal: contract template ready for review; redlines pending",
    "VP Sales: implementation waiver to request",
    "CFO: required only if the discount exceeds 35%",
]

NEGOTIATION_STRATEGY = [
    "Lead with value ($4.2M savings)",
    "Anchor on a 25% discount, concede to 30%",
    "Trade discount for a longer term or upfront payment",
]

DEAL_OUTLOOK = {
    "win_probability_before_pct": 52,
    "win_probability_after_pct": 78,
    "next_steps": [
        "Executive meeting: request for next week",
        "Decision timeline: 30 days before expiration",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _days_until(date_text):
    import datetime
    start = datetime.date.fromisoformat(DEMO_AS_OF)
    return (datetime.date.fromisoformat(date_text) - start).days


def _usage_pct(lic):
    """Seat usage to one decimal, rounded half up (1,987 of 2,000 -> 99.4)."""
    return ((lic["seats_used"] * 1000 + lic["seats"] // 2) // lic["seats"]) / 10


def _money_k(value):
    return f"${value / 1000:,.1f}K".replace(".0K", "K")


def _proposal(license_id="LIC-3000"):
    lic = LICENSE_AGREEMENTS[license_id]
    det = ACCOUNT_DETAILS[license_id]
    t = RENEWAL_TERMS
    list_price = lic["arr"] / lic["seats"]
    seat_price = round(list_price * (100 - t["matched_discount_pct"]) / 100)
    base = lic["seats"] * seat_price
    expansion = det["waitlist_users"] * seat_price
    seats = lic["seats"] + det["waitlist_users"]
    annual = base + expansion
    multi_year = round(annual * (100 - t["multi_year_discount_pct"]) / 100)
    list_value = seats * list_price
    return {
        "list_price": list_price, "seat_price": seat_price, "base": base, "expansion": expansion,
        "seats": seats, "annual": annual, "multi_year": multi_year, "tcv": multi_year * t["term_years"],
        "effective_discount_pct": round((list_value - multi_year) * 100 / list_value),
        "arr_change_pct": round((multi_year - lic["arr"]) * 100 / lic["arr"]),
        "seat_change_pct": round((seats - lic["seats"]) * 100 / lic["seats"]),
        "roi": round(det["documented_savings"] / multi_year, 1), "list_value": list_value,
    }


def _license_items(license_id=None):
    if license_id:
        return [(license_id, LICENSE_AGREEMENTS[license_id])]
    return list(LICENSE_AGREEMENTS.items())


def _renewal_pipeline(license_id=None):
    pipeline = []
    for lid, lic in _license_items(license_id):
        risk = "low" if lic["health_score"] >= 70 else ("medium" if lic["health_score"] >= 50 else "high")
        pipeline.append({
            "id": lid, "customer": lic["customer"], "arr": lic["arr"],
            "renewal_date": lic["renewal_date"], "health_score": lic["health_score"],
            "risk": risk, "csm": lic["csm"],
        })
    pipeline.sort(key=lambda x: x["renewal_date"])
    total_arr = sum(p["arr"] for p in pipeline)
    at_risk_arr = sum(LICENSE_AGREEMENTS[p["id"]]["arr"] for p in pipeline if LICENSE_AGREEMENTS[p["id"]]["churn_signals"])
    return {"pipeline": pipeline, "total_arr": total_arr, "at_risk_arr": at_risk_arr}


def _expansion_opportunities(license_id=None):
    opps = []
    for lid, lic in _license_items(license_id):
        if not lic["expansion_signals"]:
            continue
        potential = 0
        items = []
        seat_util = round(lic["seats_used"] / lic["seats"] * 100, 1)
        if seat_util > 90:
            if lid in ACCOUNT_DETAILS:
                seat_rev = ACCOUNT_DETAILS[lid]["waitlist_users"] * _proposal(lid)["seat_price"]
            else:
                seat_rev = EXPANSION_PRICING["additional_seats"]["unit_price"] * 50
            potential += seat_rev
            items.append({"type": "additional_seats", "value": seat_rev})
        for signal in lic["expansion_signals"]:
            if "api" in signal.lower():
                potential += EXPANSION_PRICING["api_premium"]["price"]
                items.append({"type": "api_premium", "value": EXPANSION_PRICING["api_premium"]["price"]})
            if "analytics" in signal.lower():
                potential += EXPANSION_PRICING["analytics_addon"]["price"]
                items.append({"type": "analytics_addon", "value": EXPANSION_PRICING["analytics_addon"]["price"]})
            if "sso" in signal.lower():
                val = EXPANSION_PRICING["sso_subsidiary"]["price"] * 3
                potential += val
                items.append({"type": "sso_subsidiary", "value": val})
            if "integration" in signal.lower():
                potential += EXPANSION_PRICING["custom_integration"]["price"]
                items.append({"type": "custom_integration", "value": EXPANSION_PRICING["custom_integration"]["price"]})
        opps.append({
            "id": lid, "customer": lic["customer"], "current_arr": lic["arr"],
            "expansion_potential": potential, "items": items, "signals": lic["expansion_signals"],
        })
    opps.sort(key=lambda x: x["expansion_potential"], reverse=True)
    return {"opportunities": opps, "total_potential": sum(o["expansion_potential"] for o in opps)}


def _churn_risk(license_id=None):
    risks = []
    for lid, lic in _license_items(license_id):
        if not lic["churn_signals"]:
            continue
        seat_util = round(lic["seats_used"] / lic["seats"] * 100, 1)
        risks.append({
            "id": lid, "customer": lic["customer"], "arr": lic["arr"],
            "health_score": lic["health_score"], "nps": lic["nps_score"],
            "seat_utilization": seat_util, "usage_trend": lic["usage_trend"],
            "signals": lic["churn_signals"], "tickets_90d": lic["support_tickets_90d"],
        })
    risks.sort(key=lambda x: x["health_score"])
    return {"at_risk": risks, "total_arr_at_risk": sum(r["arr"] for r in risks)}


def _revenue_impact(license_id=None):
    renewal = _renewal_pipeline(license_id)
    expansion = _expansion_opportunities(license_id)
    churn = _churn_risk(license_id)
    base_renewal = renewal["total_arr"]
    expansion_val = expansion["total_potential"]
    churn_val = churn["total_arr_at_risk"]
    best_case = base_renewal + expansion_val
    worst_case = base_renewal - churn_val
    expected = base_renewal + round(expansion_val * 0.4) - round(churn_val * 0.3)
    return {
        "base_renewal_arr": base_renewal, "expansion_potential": expansion_val,
        "churn_risk_arr": churn_val, "best_case": best_case,
        "worst_case": worst_case, "expected": expected,
    }


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class LicenseRenewalExpansionAgent(BasicAgent):
    """License renewal pipeline and expansion opportunity agent."""

    def __init__(self):
        self.name = "LicenseRenewalExpansionAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always use this tool for license renewals; the demo "
                "account is GlobalBank (LIC-3000) and every operation has demo defaults, so call it "
                "right away without asking for IDs. Uses bundled synthetic subscription records "
                "and returns read-only renewal, risk, expansion, and scenario planning only. "
                "It does not approve concessions, create proposals, or contact customers. "
                "Route requests that compare renewal, expansion, and churn scenarios or ask "
                "for modeled portfolio value to `revenue_impact`; that operation returns "
                "`Synthetic Revenue Scenario` and `Illustrative midpoint assumption`."
            ),
            "operations": [
                "renewal_pipeline", "expansion_opportunities", "churn_risk", "revenue_impact",
                "account_health", "competitive_defense", "renewal_proposal", "executive_brief",
                "negotiation_plan", "deal_summary",
            ],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "renewal_pipeline",
                            "expansion_opportunities",
                            "churn_risk",
                            "revenue_impact",
                            "account_health",
                            "competitive_defense",
                            "renewal_proposal",
                            "executive_brief",
                            "negotiation_plan",
                            "deal_summary",
                        ],
                        "description": (
                            "Select the requested renewal deliverable. renewal_pipeline: renewal dates, "
                            "health, risk bands, and preparation checklist. expansion_opportunities: "
                            "demand signals and draft packaging options. churn_risk: churn evidence, "
                            "competitive threats, and switching-cost assumptions. revenue_impact: REQUIRED "
                            "for comparing renewal, expansion, and churn scenarios or modeled portfolio "
                            "value; returns Synthetic Revenue Scenario and Illustrative midpoint assumption. "
                            "For one strategic account (default GlobalBank, LIC-3000): account_health when the "
                            "user describes the account (license expiring, seats, ARR, waitlist, competitor "
                            "discount); competitive_defense for the competitive defense strategy or switching "
                            "costs; renewal_proposal for the renewal and expansion proposal with pricing; "
                            "executive_brief for the executive presentation and talking points; "
                            "negotiation_plan for negotiation strategy and the approvals needed; deal_summary "
                            "for 'send the proposal and summarize our renewal strategy' (returns a "
                            "ready-to-send draft, never sends)."
                        ),
                    },
                    "license_id": {
                        "type": "string",
                        "enum": list(LICENSE_AGREEMENTS),
                        "description": "Optional license ID to filter results.",
                    },
                    "data_source": {
                        "type": "string",
                        "enum": ["synthetic"],
                        "description": "Deterministic source route. Only bundled synthetic evidence is supported.",
                    },
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "renewal_pipeline")
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
        license_id = kwargs.get("license_id")
        if license_id is not None and license_id not in LICENSE_AGREEMENTS:
            for lid, lic in LICENSE_AGREEMENTS.items():
                if str(license_id).lower() in lic["customer"].lower():
                    license_id = lid
        if license_id is not None and license_id not in LICENSE_AGREEMENTS:
            return f"**Error:** Unknown `license_id` `{license_id}`. Valid: {', '.join(LICENSE_AGREEMENTS)}."
        dispatch = {
            "renewal_pipeline": self._renewal_pipeline,
            "expansion_opportunities": self._expansion_opportunities,
            "churn_risk": self._churn_risk,
            "revenue_impact": self._revenue_impact,
            "account_health": self._account_health,
            "competitive_defense": self._competitive_defense,
            "renewal_proposal": self._renewal_proposal,
            "executive_brief": self._executive_brief,
            "negotiation_plan": self._negotiation_plan,
            "deal_summary": self._deal_summary,
        }
        handler = dispatch.get(op)
        if handler is None:
            return f"**Error:** Unknown operation `{op}`. Valid: {', '.join(dispatch)}."
        if op in ("account_health", "competitive_defense", "renewal_proposal", "executive_brief",
                  "negotiation_plan", "deal_summary"):
            license_id = license_id or "LIC-3000"
            if license_id not in ACCOUNT_DETAILS:
                return (f"**Error:** No strategic-account detail for `{license_id}` in the synthetic records. "
                        f"Strategic accounts: {', '.join(ACCOUNT_DETAILS)} (GlobalBank). Synthetic data only.")
        output = handler(license_id)
        return (
            output
            + "\n\n**Synthetic source model:** Bundled subscription, usage, support, and "
            "planning records.\n\n**Evidence boundary:** Exact names, dates, seats, scores, "
            "prices, ARR, percentages, and projections are synthetic planning evidence. This "
            "read-only output did not approve a concession, change pricing, create or send a "
            "proposal, write a CRM record, or contact a customer."
        )

    def _renewal_pipeline(self, license_id=None) -> str:
        data = _renewal_pipeline(license_id)
        lines = [
            "# Renewal Pipeline",
            "",
            f"**Total Renewal ARR:** ${data['total_arr']:,}",
            f"**At-Risk ARR (accounts with churn signals):** ${data['at_risk_arr']:,}",
            "",
            "| Customer | ARR | Renewal Date | Health | Risk | CSM |",
            "|----------|-----|-------------|--------|------|-----|",
        ]
        for p in data["pipeline"]:
            lines.append(
                f"| {p['customer']} | ${p['arr']:,} | {p['renewal_date']} "
                f"| {p['health_score']} | {p['risk'].upper()} | {p['csm']} |"
            )
        lines.extend(
            [
                "",
                "## Draft Renewal Preparation Checklist",
                "- Validate usage, support, stakeholder, and competitive evidence.",
                "- Review value evidence and renewal options with authorized commercial owners.",
                "- Draft customer-facing materials only after pricing, legal, and account review.",
            ]
        )
        return "\n".join(lines)

    def _expansion_opportunities(self, license_id=None) -> str:
        data = _expansion_opportunities(license_id)
        lines = [
            "# Expansion Opportunities",
            "",
            f"**Total Expansion Potential:** ${data['total_potential']:,}",
            "",
        ]
        for opp in data["opportunities"]:
            lines.append(f"## {opp['customer']} (Current ARR: ${opp['current_arr']:,})")
            lines.append(f"**Expansion Potential:** ${opp['expansion_potential']:,}")
            lines.append("")
            lines.append("**Signals:**")
            for s in opp["signals"]:
                lines.append(f"- {s}")
            lines.append("")
            lines.append("| Expansion Item | Value |")
            lines.append("|---------------|-------|")
            for item in opp["items"]:
                lines.append(f"| {item['type'].replace('_', ' ').title()} | ${item['value']:,} |")
            lines.extend(
                [
                    "",
                    "**Draft Packaging Options (authorized review required):**",
                    "- Preserve the current plan and add only the evidence-backed capability.",
                    "- Compare a staged expansion with a broader package before negotiation.",
                    "- Apply no concession unless an authorized pricing workflow approves it.",
                ]
            )
            lines.append("")
        return "\n".join(lines)

    def _churn_risk(self, license_id=None) -> str:
        data = _churn_risk(license_id)
        lines = [
            "# Churn Risk Assessment",
            "",
            f"**Total ARR at Risk:** ${data['total_arr_at_risk']:,}",
            "",
        ]
        for r in data["at_risk"]:
            lines.append(f"## {r['customer']} (ARR: ${r['arr']:,})")
            lines.append(f"- Health Score: {r['health_score']}")
            lines.append(f"- NPS: {r['nps']}")
            lines.append(f"- Seat Utilization: {r['seat_utilization']}%")
            lines.append(f"- Usage Trend: {r['usage_trend']}")
            lines.append(f"- Support Tickets (90d): {r['tickets_90d']}")
            lines.append("")
            lines.append("**Churn Signals:**")
            for s in r["signals"]:
                lines.append(f"- {s}")
            competitor_signal = any("competitor" in s.lower() for s in r["signals"])
            if competitor_signal:
                total_switching_cost = sum(SWITCHING_COST_ASSUMPTIONS.values())
                lines.extend(
                    [
                        "",
                        "**Synthetic Switching-Cost Review:**",
                        *[
                            f"- {label.replace('_', ' ').title()}: ${value:,}"
                            for label, value in SWITCHING_COST_ASSUMPTIONS.items()
                        ],
                        f"- Illustrative total switching-cost assumption: ${total_switching_cost:,}",
                        "- Validate every component with the customer and authorized commercial owners before use.",
                    ]
                )
            lines.append("")
        return "\n".join(lines)

    def _revenue_impact(self, license_id=None) -> str:
        data = _revenue_impact(license_id)
        lines = [
            "# Synthetic Revenue Scenario",
            "",
            f"**Base Renewal ARR:** ${data['base_renewal_arr']:,}",
            f"**Expansion Potential:** ${data['expansion_potential']:,}",
            f"**Churn Risk ARR:** ${data['churn_risk_arr']:,}",
            "",
            "## Scenarios",
            "",
            "| Scenario | Projected ARR |",
            "|----------|--------------|",
            f"| Best Case (full expansion, no churn) | ${data['best_case']:,} |",
            f"| Illustrative midpoint assumption (40% expansion, 30% churn) | ${data['expected']:,} |",
            f"| Worst Case (no expansion, full churn) | ${data['worst_case']:,} |",
            "",
            "## Recommendations",
            "- Prioritize executive engagement for high-churn-risk accounts.",
            "- Prepare expansion options for authorized review where demand signals are present.",
            "- Review whether CSM capacity should be adjusted for higher-risk synthetic accounts.",
        ]
        return "\n".join(lines)


    # ---- Strategic account (GlobalBank) walkthrough ---------------------------

    def _account_health(self, license_id="LIC-3000") -> str:
        lic, det = LICENSE_AGREEMENTS[license_id], ACCOUNT_DETAILS[license_id]
        comp = det["competitor"]
        usage = _usage_pct(lic)
        lines = [
            f"# Account Analysis: {lic['customer']}",
            "",
            f"License renews in {_days_until(lic['renewal_date'])} days ({lic['renewal_date']}). Strong usage gives "
            "leverage despite the competitor discount.",
            "",
            "| Metric | Value | Signal |",
            "|---|---|---|",
            f"| Current ARR | ${lic['arr'] / 1000000:.1f}M ({lic['seats']:,} seats) | Baseline |",
            f"| Active usage | {usage}% ({lic['seats_used']:,} users) | Excellent |",
            f"| Waitlist demand | {det['waitlist_users']} users | Expansion |",
            f"| Health score | {lic['health_score']}/100 | Strong |",
            f"| Competitor threat | {comp['vendor']} | {comp['discount_pct']}% discount |",
            "",
            f"**Value Realized by {lic['customer']}:**",
            f"- ${det['documented_savings'] / 1000000:.1f}M documented cost savings",
            f"- {det['modules_used']} of {det['modules_total']} modules actively used",
            f"- API calls: {det['api_calls_month']}/month (growing {det['api_growth_mom_pct']}% MoM)",
            f"- NPS from their team: {lic['nps_score']}",
            "",
            "Next step: want to see the competitive defense strategy?",
        ]
        return "\n".join(lines)

    def _competitive_defense(self, license_id="LIC-3000") -> str:
        lic, det = LICENSE_AGREEMENTS[license_id], ACCOUNT_DETAILS[license_id]
        comp, sd = det["competitor"], det["switching_detail"]
        total = sum(SWITCHING_COST_ASSUMPTIONS.values())
        lines = [
            "# Competitive Defense Strategy",
            "",
            f"{comp['vendor']} is offering {comp['discount_pct']}% off their enterprise tier. Counter-strategy "
            "based on the switching-cost analysis:",
            "",
            "## Competitor Offer Analysis",
            "",
            f"| Factor | {comp['vendor']} | Our Position |",
            "|---|---|---|",
            f"| Price | {comp['discount_pct']}% lower | Match + value-add |",
            f"| Migration cost | ${comp['migration_offer']:,} (their offer) | {_money_k(total)} actual cost |",
            f"| Feature parity | {comp['feature_parity_pct']}% | 100% |",
            f"| Integration work | {comp['integration_time']} | Already done |",
            "",
            f"## Their Hidden Costs (draft to share with {lic['customer']} after review)",
        ]
        for key, value in SWITCHING_COST_ASSUMPTIONS.items():
            lines.append(f"- {key.replace('_', ' ').title()}: {sd[key]} = {_money_k(value)}")
        lines += [
            f"- Total switching cost: ~{_money_k(total)}",
            "",
            "## Our Counter-Strategy (draft options for authorized pricing review)",
        ]
        lines += [f"- {c}" for c in RENEWAL_TERMS["counter_strategy"]]
        lines += ["", "Next step: should I build the renewal and expansion proposal with pricing?"]
        return "\n".join(lines)

    def _renewal_proposal(self, license_id="LIC-3000") -> str:
        lic, det, t = LICENSE_AGREEMENTS[license_id], ACCOUNT_DETAILS[license_id], RENEWAL_TERMS
        p = _proposal(license_id)
        lines = [
            f"# Draft Renewal + Expansion Proposal: {lic['customer']}",
            "",
            f"Proposal draft that answers the competitor threat while capturing the {det['waitlist_users']}-seat expansion.",
            "",
            "| Component | Quantity | Unit Price | Annual Value |",
            "|---|---|---|---|",
            f"| Base renewal | {lic['seats']:,} seats | ${p['seat_price']}/seat | {_money_k(p['base'])} |",
            f"| Expansion | {det['waitlist_users']} seats | ${p['seat_price']}/seat | {_money_k(p['expansion'])} |",
            f"| Premium support | Included | $0 | {_money_k(t['premium_support_value'])} value |",
            f"| Total ARR | {p['seats']:,} seats | | {_money_k(p['annual'])} |",
            "",
            "## Proposal Positioning",
            f"- {t['matched_discount_pct']}% discount applied to the ${p['list_price']:.0f}/seat list price (matches competitor)",
            f"- {t['term_years']}-year term: additional {t['multi_year_discount_pct']}% = {_money_k(p['multi_year'])}/year",
            f"- List value {_money_k(p['list_value'])} -> {_money_k(p['multi_year'])} ({p['effective_discount_pct']}% effective discount)",
            "- But: 25% more seats, premium support included",
            "",
            f"## ROI for {lic['customer']}",
            f"- Their cost savings: ${det['documented_savings'] / 1000000:.1f}M annually",
            f"- Their cost: {_money_k(p['multi_year'])} per year",
            f"- ROI: {p['roi']}x return on investment",
            "",
            "Draft for deal-desk and pricing approval; not sent to the customer.",
            "",
            "Next step: want me to prepare the executive presentation and talking points?",
        ]
        return "\n".join(lines)

    def _executive_brief(self, license_id="LIC-3000") -> str:
        b = EXECUTIVE_BRIEF
        lines = [
            "# Draft Executive Presentation",
            "",
            f"Executive presentation outline ready with {len(b['slides'])} slides focused on value realization and "
            "strategic partnership.",
            "",
            "## Presentation Structure",
        ]
        lines += [f"{i}. {slide}" for i, slide in enumerate(b["slides"], 1)]
        lines += ["", "## Key Talking Points"]
        lines += [f'- "{tp}"' for tp in b["talking_points"]]
        lines += [
            "",
            f"**Objection Handlers:** {b['objection_handlers']} prepared responses drafted for sales enablement review.",
            "",
            "Next step: ready to see the negotiation strategy and the approvals you need?",
        ]
        return "\n".join(lines)

    def _negotiation_plan(self, license_id="LIC-3000") -> str:
        lines = [
            "# Negotiation Plan and Required Approvals",
            "",
            "Negotiation path mapped; internal approvals are listed as requests to route, not granted approvals.",
            "",
            "## Negotiation Boundaries",
            "",
            "| Lever | Floor | Target | Approval Needed |",
            "|---|---|---|---|",
        ]
        for c in CONCESSION_POLICY:
            lines.append(f"| {c['lever']} | {c['floor']} | {c['target']} | {c['approver']} |")
        lines += ["", "## Internal Approvals to Request (pre-staged drafts)"]
        lines += [f"- {a}" for a in APPROVAL_ROUTING]
        lines += ["", "## Negotiation Strategy"]
        lines += [f"- {n}" for n in NEGOTIATION_STRATEGY]
        lines += ["", "Next step: should I prepare the executive meeting request and the proposal for you to send?"]
        return "\n".join(lines)

    def _deal_summary(self, license_id="LIC-3000") -> str:
        lic, det = LICENSE_AGREEMENTS[license_id], ACCOUNT_DETAILS[license_id]
        p, o, t = _proposal(license_id), DEAL_OUTLOOK, RENEWAL_TERMS
        total = sum(SWITCHING_COST_ASSUMPTIONS.values())
        lines = [
            "# Renewal Strategy Summary",
            "",
            f"The proposal and meeting request for {lic['customer']}'s {det['decision_maker']} are ready for you to "
            "send (not sent). Complete renewal strategy:",
            "",
            "## Session Summary",
            f"- Account analysis - {_usage_pct(lic)}% usage, {lic['health_score']} health "
            f"score, ${det['documented_savings'] / 1000000:.1f}M value delivered",
            f"- Competitive defense - {_money_k(total)} switching cost identified, {t['matched_discount_pct']}% match strategy",
            f"- Expansion capture - {det['waitlist_users']} additional seats from waitlist demand",
            f"- Pricing proposal - {_money_k(p['multi_year'])}/year for {p['seats']:,} seats ({t['term_years']}-year term)",
            f"- Executive presentation - {len(EXECUTIVE_BRIEF['slides'])} slides with objection handlers",
            "- Approvals - routed as requests; contract template ready for review",
            "",
            "## Deal Metrics",
            "",
            "| Metric | Original | Proposed |",
            "|---|---|---|",
            f"| ARR | ${lic['arr'] / 1000000:.1f}M | {_money_k(p['multi_year'])} ({p['arr_change_pct']}%) |",
            f"| Seats | {lic['seats']:,} | {p['seats']:,} (+{p['seat_change_pct']}%) |",
            f"| Term | 1 year | {t['term_years']} years |",
            f"| TCV | | ${p['tcv'] / 1000000:.2f}M |",
            "",
            "## Next Steps",
        ]
        lines += [f"- {n}" for n in o["next_steps"]]
        lines += [
            f"- Win probability (modeled): {o['win_probability_after_pct']}% (up from {o['win_probability_before_pct']}%)",
            "",
            f"The renewal defense is positioned to retain ${p['tcv'] / 1000000:.2f}M TCV against the competitive threat.",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = LicenseRenewalExpansionAgent()
    for op in ["account_health", "competitive_defense", "renewal_proposal", "executive_brief",
               "negotiation_plan", "deal_summary"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
