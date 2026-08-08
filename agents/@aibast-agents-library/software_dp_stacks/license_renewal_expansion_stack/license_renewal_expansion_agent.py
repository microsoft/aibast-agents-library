"""
License Renewal and Expansion Agent for Software/Digital Products.

Manages SaaS license renewal pipelines, identifies expansion opportunities,
assesses churn risk, and projects revenue impact across the customer portfolio.
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

LICENSE_AGREEMENTS = {
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
    "data_migration": 45000,
    "reimplementation": 60000,
    "user_retraining": 18000,
    "parallel_run": 24000,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
    at_risk_arr = sum(p["arr"] for p in pipeline if p["risk"] == "high")
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
            seat_rev = EXPANSION_PRICING["additional_seats"]["unit_price"] * 50
            potential += seat_rev
            items.append({"type": "additional_seats", "value": seat_rev})
        for signal in lic["expansion_signals"]:
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
                f"{__manifest__['description']} Uses bundled synthetic subscription records "
                "and returns read-only renewal, risk, expansion, and scenario planning only. "
                "It does not approve concessions, create proposals, or contact customers. "
                "Route requests that compare renewal, expansion, and churn scenarios or ask "
                "for modeled portfolio value to `revenue_impact`; that operation returns "
                "`Synthetic Revenue Scenario` and `Illustrative midpoint assumption`."
            ),
            "operations": [
                "renewal_pipeline", "expansion_opportunities", "churn_risk", "revenue_impact",
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
                        ],
                        "description": (
                            "Select the requested renewal deliverable. renewal_pipeline: renewal dates, "
                            "health, risk bands, and preparation checklist. expansion_opportunities: "
                            "demand signals and draft packaging options. churn_risk: churn evidence, "
                            "competitive threats, and switching-cost assumptions. revenue_impact: REQUIRED "
                            "for comparing renewal, expansion, and churn scenarios or modeled portfolio "
                            "value; returns Synthetic Revenue Scenario and Illustrative midpoint assumption."
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
            return f"**Error:** Unknown `license_id` `{license_id}`. Valid: {', '.join(LICENSE_AGREEMENTS)}."
        dispatch = {
            "renewal_pipeline": self._renewal_pipeline,
            "expansion_opportunities": self._expansion_opportunities,
            "churn_risk": self._churn_risk,
            "revenue_impact": self._revenue_impact,
        }
        handler = dispatch.get(op)
        if handler is None:
            return f"**Error:** Unknown operation `{op}`. Valid: {', '.join(dispatch)}."
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
            f"**At-Risk ARR:** ${data['at_risk_arr']:,}",
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


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = LicenseRenewalExpansionAgent()
    for op in ["renewal_pipeline", "expansion_opportunities", "churn_risk", "revenue_impact"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
