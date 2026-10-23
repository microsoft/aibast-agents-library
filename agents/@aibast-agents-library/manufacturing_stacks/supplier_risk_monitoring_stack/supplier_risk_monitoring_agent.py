"""
Supplier Risk Monitoring Agent

Monitors supplier health across geopolitical, financial, operational, quality,
and logistics dimensions. Produces the semiconductor exposure view, a detailed
risk assessment, mitigation plans, the financial case, a 12-month roadmap, a
monitoring design, disruption alerts, and alternative-sourcing comparisons.
Everything is a recommendation for authorized procurement review.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/supplier-risk-monitoring",
    "version": "1.0.0",
    "display_name": "Supply Risk Monitoring Agent",
    "description": "Analyze a fixed synthetic supplier-risk snapshot and recommend review-ready mitigation options. Never contact suppliers, change sourcing, place orders, or approve procurement action.",
    "author": "AIBAST",
    "tags": ["supplier", "risk", "procurement", "supply-chain", "manufacturing"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

# scope "semiconductor" = the critical semiconductor suppliers (the default review); share_pct = share of that
# component category's supply; supply_label / impact_label = how the share is described.
SUPPLIERS = {
    "SUP-101": {
        "name": "TechnoCore Semiconductor (Taiwan)",
        "short_name": "TechnoCore",
        "assessment_name": "TechnoCore Taiwan",
        "category": "Microcontrollers",
        "region": "Asia-Pacific",
        "country": "Taiwan",
        "scope": "semiconductor",
        "share_pct": 40,
        "supply_label": "MCU supply",
        "impact_label": "MCU supply",
        "annual_spend": 4800000,
        "quality_score": 82,
        "delivery_score": 74,
        "financial_score": 68,
        "geopolitical_score": 42,
        "overall_risk": 8.2,
        "tier": 1,
        "concerns": ["Cross-strait geopolitical tensions", "Single facility concentration"],
        "recent_event": "Military exercises within 50nm",
        "financial_note": "",
        "quality_note": "",
        "strengths": [],
        "capacity_vs_demand_pct": 0,
    },
    "SUP-102": {
        "name": "Shenzhen Electronics Co.",
        "short_name": "Shenzhen Electronics",
        "assessment_name": "Shenzhen Electronics",
        "category": "Passive Components",
        "region": "Asia-Pacific",
        "country": "China",
        "scope": "semiconductor",
        "share_pct": 35,
        "supply_label": "passive components",
        "impact_label": "passives",
        "annual_spend": 3200000,
        "quality_score": 71,
        "delivery_score": 78,
        "financial_score": 55,
        "geopolitical_score": 58,
        "overall_risk": 6.5,
        "tier": 1,
        "concerns": ["Trade restrictions", "IP protection"],
        "recent_event": "New export control regulations announced",
        "debt_to_equity_change_pct": 35,
        "defect_rate_pct": 2.3,
        "defect_rate_prev_pct": 1.8,
        "financial_note": "Debt-to-equity +35% (stressed)",
        "quality_note": "Defect rate 2.3% (up from 1.8%)",
        "strengths": [],
        "capacity_vs_demand_pct": 0,
    },
    "SUP-103": {
        "name": "Malaysia Semicon Pte Ltd",
        "short_name": "Malaysia Semicon",
        "assessment_name": "Malaysia Semicon",
        "category": "Power ICs",
        "region": "Asia-Pacific",
        "country": "Malaysia",
        "scope": "semiconductor",
        "share_pct": 25,
        "supply_label": "power ICs",
        "impact_label": "power ICs",
        "annual_spend": 2100000,
        "quality_score": 91,
        "delivery_score": 88,
        "financial_score": 84,
        "geopolitical_score": 82,
        "overall_risk": 3.8,
        "tier": 1,
        "concerns": [],
        "recent_event": "",
        "financial_note": "",
        "quality_note": "",
        "strengths": ["Political stability", "diversified base"],
        "capacity_vs_demand_pct": 120,
    },
    "SUP-104": {
        "name": "Midwest Casting & Forge",
        "short_name": "Midwest Casting",
        "assessment_name": "Midwest Casting",
        "category": "Aluminum Castings",
        "region": "North America",
        "country": "USA",
        "scope": "industrial",
        "share_pct": 0,
        "supply_label": "aluminum castings",
        "impact_label": "castings",
        "annual_spend": 5600000,
        "quality_score": 88,
        "delivery_score": 65,
        "financial_score": 72,
        "geopolitical_score": 95,
        "overall_risk": 4.9,
        "tier": 1,
        "concerns": ["Single foundry equipment reliability"],
        "recent_event": "Force majeure declared after equipment failure",
        "financial_note": "",
        "quality_note": "",
        "strengths": [],
        "capacity_vs_demand_pct": 0,
    },
    "SUP-105": {
        "name": "Rheinland Precision GmbH",
        "short_name": "Rheinland Precision",
        "assessment_name": "Rheinland Precision",
        "category": "CNC Machined Parts",
        "region": "Europe",
        "country": "Germany",
        "scope": "industrial",
        "share_pct": 0,
        "supply_label": "machined parts",
        "impact_label": "machined parts",
        "annual_spend": 3800000,
        "quality_score": 95,
        "delivery_score": 91,
        "financial_score": 89,
        "geopolitical_score": 88,
        "overall_risk": 2.4,
        "tier": 2,
        "concerns": [],
        "recent_event": "",
        "financial_note": "",
        "quality_note": "",
        "strengths": ["Stable delivery", "high quality"],
        "capacity_vs_demand_pct": 0,
    },
}

RISK_CATEGORIES = [
    "Geopolitical stability",
    "Financial health",
    "Operational capacity",
    "Quality metrics",
    "Logistics reliability",
]

RECENT_INCIDENTS = [
    {"supplier_id": "SUP-101", "date": "2026-02-28", "severity": "HIGH",
     "description": "Military exercises within 50nm of the facility; 5-day port closure delayed 3 shipments"},
    {"supplier_id": "SUP-102", "date": "2026-03-05", "severity": "MEDIUM",
     "description": "Quality excursion: capacitor lot C-4410 at 2.3% defect rate (up from 1.8%; spec 0.5%)"},
    {"supplier_id": "SUP-104", "date": "2026-03-10", "severity": "HIGH",
     "description": "Equipment failure at foundry; force majeure declared, 7-day production halt"},
    {"supplier_id": "SUP-102", "date": "2026-03-12", "severity": "LOW",
     "description": "New export control regulations announced; compliance review underway"},
]

BACKUP_SUPPLIERS = {
    "SUP-101": [
        {"name": "Hanseong Foundry (Korea)", "lead_time_weeks": 26, "qual_status": "In Progress", "est_cost_premium_pct": 8},
        {"name": "Lakeside Foundry (USA)", "lead_time_weeks": 16, "qual_status": "Not Started", "est_cost_premium_pct": 15},
    ],
    "SUP-102": [
        {"name": "Kansai Passive Components (Japan)", "lead_time_weeks": 6, "qual_status": "In Qualification", "est_cost_premium_pct": 5},
        {"name": "Keystone Passives (USA)", "lead_time_weeks": 4, "qual_status": "In Qualification", "est_cost_premium_pct": 12},
    ],
    "SUP-104": [
        {"name": "Great Lakes Precision Castings (USA)", "lead_time_weeks": 8, "qual_status": "In Progress", "est_cost_premium_pct": 6},
    ],
}

# Recommended mitigation plan per supplier (for procurement approval; nothing is executed by the agent).
MITIGATION_PLANS = {
    "SUP-101": {
        "stance": "HIGH PRIORITY",
        "heading": "Immediate (30 days)",
        "safety_stock_days": 30,
        "safety_stock_target_days": 45,
        "safety_stock_investment": 840000,
        "actions": [
            "Dual sourcing: Korean supplier qualification started",
            "Alternative qualified: 6 months",
            "Air freight contingency: $2.1M capacity to reserve",
        ],
    },
    "SUP-102": {
        "stance": "MONITOR CLOSELY",
        "heading": "Actions",
        "actions": [
            "Payment terms: Net-30 -> COD (protect exposure)",
            "Quality inspection: 100% incoming (was sampling)",
            "Contract updates: Stronger IP protections",
            "Backup identified: 2 suppliers in qualification",
        ],
    },
    "SUP-103": {
        "stance": "OPPORTUNITY",
        "heading": "Optimization",
        "actions": [
            "Volume increase: +20% (tier discount available)",
            "Strategic partnership discussions",
            "Co-development program for custom ICs",
        ],
    },
}

MITIGATION_COSTS = [
    {"action": "Safety stock increase", "investment": 840000, "recurring": False, "benefit": "45 days buffer"},
    {"action": "Dual sourcing program", "investment": 125000, "recurring": False, "benefit": "Supply security"},
    {"action": "Enhanced inspection", "investment": 48000, "recurring": True, "benefit": "Quality protection"},
    {"action": "Alternative qualification", "investment": 85000, "recurring": False, "benefit": "Reduced dependency"},
]

RISK_EXPOSURE = {
    "current_exposure": 12400000,
    "after_mitigation": 4300000,
    "probability_now_pct": 15,
    "probability_after_pct": 4,
}

ROADMAP = [
    {"phase": "Phase 1 (Months 1-3): Immediate Protection", "steps": [
        "Week 1: Increase TechnoCore orders (safety stock)",
        "Week 2: COD terms with Shenzhen Electronics",
        "Week 3: 100% inspection protocol starts",
        "Week 4: Korean supplier identification complete",
    ]},
    {"phase": "Phase 2 (Months 4-6): Qualification", "steps": [
        "Month 4: Korean supplier initial samples",
        "Month 5: Testing and validation",
        "Month 6: First production orders (10% volume)",
    ]},
    {"phase": "Phase 3 (Months 7-9): Optimization", "steps": [
        "Malaysia partnership negotiations",
        "Volume consolidation planning",
        "Contract updates completed",
    ]},
    {"phase": "Phase 4 (Months 10-12): Full Resilience", "steps": [
        "Dual sourcing: 60% Taiwan / 40% Korea",
        "Malaysia strategic partnership signed",
    ]},
]
ROADMAP_RISK_TARGET = 4.0

MONITORING_DESIGN = {
    "data_sources": [
        "Geopolitical: news wires, government advisories",
        "Financial: credit ratings, stock prices, filings",
        "Operational: supplier portals, IoT, certifications",
        "Logistics: shipping data, port congestion, weather",
        "Legal: sanctions lists, trade restrictions",
    ],
    "alert_thresholds": [
        "Critical: Immediate escalation to VP",
        "Warning: Daily digest to procurement",
        "Info: Weekly risk report",
    ],
    "automated_actions": [
        "Risk score >7.5: Trigger mitigation protocols",
        "Financial deterioration: Payment terms adjustment",
        "Quality issues: Inspection level increase",
        "Capacity concerns: Backup supplier activation",
    ],
    "success_metrics": [
        "Supply continuity: 99.7% (target: 99.5%)",
        "Risk-adjusted cost: -12% vs. reactive approach",
        "Early warning: 18 days average lead time",
    ],
}

_BOUNDARY = ("Synthetic recommendation only. No supplier was contacted, qualified, selected, or awarded "
             "business; no order, payment term, contract, or alert was changed or activated.")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _composite_score(supplier):
    """Weighted composite health score (0-100, higher = healthier)."""
    return round(
        supplier["quality_score"] * 0.30
        + supplier["delivery_score"] * 0.25
        + supplier["financial_score"] * 0.25
        + supplier["geopolitical_score"] * 0.20,
        1,
    )


def _risk_tier_label(overall_risk):
    """Convert numeric risk (0-10) to a label: >=7 HIGH, >=5 MEDIUM, else LOW."""
    if overall_risk >= 7.0:
        return "HIGH"
    if overall_risk >= 5.0:
        return "MEDIUM"
    return "LOW"


def _scope_suppliers(scope="semiconductor"):
    return [(sid, s) for sid, s in SUPPLIERS.items() if s["scope"] == scope]


def _money(value):
    """840000 -> '$840K', 1098000 -> '$1.098M', 12400000 -> '$12.4M'."""
    if value >= 1000000:
        if value % 100000 == 0:
            return f"${value / 1000000:.1f}M"
        return f"${value / 1000000:.3f}M"
    return f"${value // 1000}K"


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "risk_dashboard",
    "supplier_scorecard",
    "disruption_alerts",
    "alternative_sourcing",
    "mitigation_plan",
    "financial_impact",
    "implementation_roadmap",
    "monitoring_plan",
]


class SupplierRiskMonitoringAgent(BasicAgent):
    """Monitors supplier risk and generates mitigation plans."""

    def __init__(self):
        self.name = "SupplierRiskMonitoringAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always use this tool for the critical semiconductor suppliers "
                "in Taiwan, China and Malaysia (TechnoCore, Shenzhen Electronics, Malaysia Semicon). A supply "
                "chain leader walks the operations in order: monitor supplier risk -> risk_dashboard; detailed "
                "risk assessment -> supplier_scorecard; mitigation strategies -> mitigation_plan; financial "
                "impact -> financial_impact; implementation roadmap -> implementation_roadmap; ongoing "
                "monitoring approach -> monitoring_plan. Every one of these asks, including the monitoring "
                "approach, must call this tool: its data sources, alert thresholds, automated-action rules and "
                "success metrics come only from monitoring_plan, never from general knowledge."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "risk_dashboard: monitor risks for the critical semiconductor suppliers (supply "
                            "exposure by country and the risk categories monitored). "
                            "supplier_scorecard: the detailed risk assessment (HIGH/MEDIUM/LOW per supplier "
                            "with concerns, financial, quality and dimension evidence). "
                            "disruption_alerts: recorded incidents and potential exposure. "
                            "alternative_sourcing: compare backup suppliers for procurement review. "
                            "mitigation_plan: mitigation strategies per supplier. "
                            "financial_impact: mitigation costs, exposure reduction and ROI / break-even. "
                            "implementation_roadmap: the 12-month implementation roadmap. "
                            "monitoring_plan: the ongoing / real-time monitoring approach. "
                            "Never contact a supplier or change sourcing."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "risk_dashboard")
        dispatch = {
            "risk_dashboard": self._risk_dashboard,
            "supplier_scorecard": self._supplier_scorecard,
            "disruption_alerts": self._disruption_alerts,
            "alternative_sourcing": self._alternative_sourcing,
            "mitigation_plan": self._mitigation_plan,
            "financial_impact": self._financial_impact,
            "implementation_roadmap": self._implementation_roadmap,
            "monitoring_plan": self._monitoring_plan,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _risk_dashboard(self, **kwargs) -> str:
        scope = _scope_suppliers("semiconductor")
        countries = ", ".join(s["country"] for _, s in scope)
        lines = [
            "## Supplier Risk Dashboard — Semiconductor Supply Chain\n",
            "> Fixed synthetic snapshot; no live financial, logistics, ERP, or supplier feed was queried.\n",
            f"Risk profiles for your semiconductor supply chain across {countries}: geopolitical, financial, "
            "operational, quality, and logistics risk.\n",
            "**Supply Chain Exposure:**",
        ]
        for _, s in scope:
            lines.append(f"- {s['country']}: {s['share_pct']}% of {s['supply_label']} ({s['short_name']})")
        lines.append("\n**Risk Categories Monitored:**")
        for c in RISK_CATEGORIES:
            lines.append(f"- {c}")
        total = sum(s["annual_spend"] for _, s in scope)
        at_risk = sum(s["annual_spend"] for _, s in scope if s["overall_risk"] >= 5.0)
        lines.append(f"\n**Annual semiconductor spend:** ${total:,.0f}")
        lines.append(f"**Spend at elevated risk (score >= 5.0):** ${at_risk:,.0f} ({round(at_risk / total * 100, 1)}%)\n")
        lines.append("| Supplier | Country | Share | Spend | Risk Score | Risk Level |")
        lines.append("|----------|---------|-------|-------|------------|------------|")
        for _, s in sorted(scope, key=lambda item: item[1]["overall_risk"], reverse=True):
            lines.append(
                f"| {s['name']} | {s['country']} | {s['share_pct']}% of {s['impact_label']} | "
                f"${s['annual_spend']:,.0f} | {s['overall_risk']}/10 | **{_risk_tier_label(s['overall_risk'])} RISK** |"
            )
        others = [s for _, s in _scope_suppliers("industrial")]
        lines.append("\nOther monitored suppliers (outside this semiconductor review): "
                     + "; ".join(f"{s['name']} {s['overall_risk']}/10" for s in others) + ".")
        lines.append("\nSource: [Risk Intelligence + news wires + D365] (synthetic)")
        lines.append("\nShall I show the detailed risk assessment?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _supplier_scorecard(self, **kwargs) -> str:
        lines = ["## Supply Risk Assessment\n",
                 "> Synthetic evidence for procurement review; scores are not customer or third-party ratings.\n"]
        for sid, s in _scope_suppliers("semiconductor"):
            level = _risk_tier_label(s["overall_risk"])
            lines.append(f"### {level} RISK: {s['assessment_name']} ({sid})")
            lines.append(f"- **Risk score:** {s['overall_risk']}/10")
            lines.append(f"- **Impact:** {s['share_pct']}% of {s['impact_label']}")
            if level == "HIGH" and s["concerns"]:
                lines.append(f"- **Primary concern:** {s['concerns'][0]}")
                if len(s["concerns"]) > 1:
                    lines.append(f"- **Secondary:** {s['concerns'][1]}")
                if s["recent_event"]:
                    lines.append(f"- **Recent events:** {s['recent_event']}")
            elif s["concerns"]:
                lines.append(f"- **Concerns:** {', '.join(s['concerns'])}")
            if s["financial_note"]:
                lines.append(f"- **Financial:** {s['financial_note']}")
            if s["quality_note"]:
                lines.append(f"- **Quality:** {s['quality_note']}")
            if s["strengths"]:
                lines.append(f"- **Strengths:** {', '.join(s['strengths'])}")
            if s["capacity_vs_demand_pct"]:
                lines.append(f"- **Capacity:** {s['capacity_vs_demand_pct']}% of our demand available")
            lines.append(
                f"- **Dimension scores (0-100):** Quality {s['quality_score']} | Delivery {s['delivery_score']} | "
                f"Financial {s['financial_score']} | Geopolitical {s['geopolitical_score']} "
                f"(composite health {_composite_score(s)}/100)"
            )
            lines.append("")
        lines.append("Source: [Risk Intelligence + Financial Data] (synthetic)")
        lines.append("\nWant to see mitigation strategies?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _disruption_alerts(self, **kwargs) -> str:
        lines = ["## Active Disruption Alerts\n", "> Recorded synthetic incidents only; validate against approved sources before action.\n"]
        if not RECENT_INCIDENTS:
            lines.append("No active disruption alerts.")
            return "\n".join(lines)

        sorted_incidents = sorted(RECENT_INCIDENTS, key=lambda i: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(i["severity"], 3))
        lines.append("| Severity | Date | Supplier | Description |")
        lines.append("|----------|------|----------|-------------|")
        for inc in sorted_incidents:
            sname = SUPPLIERS.get(inc["supplier_id"], {}).get("name", inc["supplier_id"])
            lines.append(
                f"| **{inc['severity']}** | {inc['date']} | "
                f"{sname} ({inc['supplier_id']}) | {inc['description']} |"
            )

        lines.append("\n### Impact Assessment\n")
        for inc in sorted_incidents:
            if inc["severity"] != "HIGH":
                continue
            s = SUPPLIERS.get(inc["supplier_id"], {})
            lines.append(f"**{s.get('name', inc['supplier_id'])}**")
            lines.append(f"- Annual spend exposed: ${s.get('annual_spend', 0):,.0f}")
            lines.append(f"- Category: {s.get('category', 'N/A')}")
            has_backup = inc["supplier_id"] in BACKUP_SUPPLIERS
            lines.append(f"- Backup suppliers available: {'Yes' if has_backup else 'No'}")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _alternative_sourcing(self, **kwargs) -> str:
        lines = ["## Alternative Sourcing Options\n", f"> {_BOUNDARY}\n"]
        if not BACKUP_SUPPLIERS:
            lines.append("No alternative suppliers have been identified.")
            return "\n".join(lines)

        total_premium = 0
        scope_spend = 0
        for sid, backups in BACKUP_SUPPLIERS.items():
            s = SUPPLIERS.get(sid, {})
            scope_spend += s.get("annual_spend", 0)
            lines.append(f"### Alternatives for {s.get('name', sid)} ({s.get('category', 'N/A')})")
            lines.append(f"- **Current spend:** ${s.get('annual_spend', 0):,.0f}")
            lines.append(f"- **Current risk:** {s.get('overall_risk', 'N/A')}/10\n")
            lines.append("| Alternative Supplier | Lead Time | Qual Status | Cost Premium |")
            lines.append("|---------------------|-----------|-------------|--------------|")
            for b in backups:
                lines.append(
                    f"| {b['name']} | {b['lead_time_weeks']} weeks | {b['qual_status']} | +{b['est_cost_premium_pct']}% |"
                )
            qualified = [b for b in backups if b["qual_status"] == "Qualified"]
            if qualified:
                best = min(qualified, key=lambda b: b["est_cost_premium_pct"])
                lines.append(f"\n**Review option:** Ask authorized procurement owners to evaluate {best['name']} "
                             f"(synthetic status: qualified; +{best['est_cost_premium_pct']}% premium; {best['lead_time_weeks']}-week lead)")
            else:
                fastest = min(backups, key=lambda b: b["lead_time_weeks"])
                lines.append(f"\n**Review option:** Ask authorized procurement owners whether to assess {fastest['name']} "
                             f"({fastest['lead_time_weeks']}-week lead; synthetic status: {fastest['qual_status']})")
            lines.append("")
            best_prem = min(b["est_cost_premium_pct"] for b in backups)
            total_premium += s.get("annual_spend", 0) * best_prem / 100

        lines.append(f"**Estimated annual cost of full diversification:** ${total_premium:,.0f}")
        lines.append(f"**Spend represented by the modeled review scope:** ${scope_spend:,.0f}")
        lines.append("\nThis agent does not contact suppliers, change allocations, place orders, or approve qualification.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _mitigation_plan(self, **kwargs) -> str:
        lines = ["## Risk Mitigation Plan\n",
                 "> Synthetic recommendations for authorized procurement approval; nothing below has been executed.\n"]
        for sid, plan in MITIGATION_PLANS.items():
            s = SUPPLIERS[sid]
            lines.append(f"### {s['short_name']} ({s['country']}) - {plan['stance']}")
            lines.append(f"**{plan['heading']}:**")
            if "safety_stock_days" in plan:
                lines.append(
                    f"- Increase safety stock: {plan['safety_stock_days']} -> {plan['safety_stock_target_days']} days "
                    f"({_money(plan['safety_stock_investment'])} investment)"
                )
            for action in plan["actions"]:
                lines.append(f"- {action}")
            lines.append("")
        lines.append("Source: [Supply Chain + Procurement] (synthetic)")
        lines.append(f"\n{_BOUNDARY}")
        lines.append("\nShall I show the financial impact?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _financial_impact(self, **kwargs) -> str:
        e = RISK_EXPOSURE
        total = sum(c["investment"] for c in MITIGATION_COSTS)
        reduction = round((e["current_exposure"] - e["after_mitigation"]) / e["current_exposure"] * 100)
        break_even = int(total / e["current_exposure"] * 1000) / 10
        verdict = "favorable" if e["probability_now_pct"] > break_even else "unfavorable"
        lines = ["## Risk Mitigation Investment Analysis\n",
                 "> Synthetic planning model; values are estimates for review, not committed budget.\n",
                 "**Mitigation Costs:**\n",
                 "| Action | Investment | Benefit |",
                 "|--------|------------|---------|"]
        for c in MITIGATION_COSTS:
            amount = _money(c["investment"]) + ("/year" if c["recurring"] else "")
            lines.append(f"| {c['action']} | {amount} | {c['benefit']} |")
        lines.append(f"| **Total Investment** | **{_money(total)}** | Risk reduction |")
        lines.append("\n**Risk Exposure Reduction:**")
        lines.append(f"- Current supply risk: {_money(e['current_exposure'])} (potential disruption)")
        lines.append(f"- After mitigation: {_money(e['after_mitigation'])} ({reduction}% reduction)")
        lines.append(f"- Expected probability: {e['probability_now_pct']}% -> {e['probability_after_pct']}%")
        lines.append("\n**ROI Scenario:**")
        lines.append(f"- Avoided disruption value: {_money(e['current_exposure'])}")
        lines.append(f"- Implementation cost: {_money(total)}")
        lines.append(f"- Break-even: {break_even}% disruption probability")
        lines.append(f"- Current probability: {e['probability_now_pct']}% ({verdict})")
        lines.append("\nSource: [Finance + Risk Model] (synthetic)")
        lines.append("\nWant to see the 12-month implementation roadmap?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _implementation_roadmap(self, **kwargs) -> str:
        lines = ["## 12-Month Implementation Roadmap\n",
                 "> Synthetic recommended plan for procurement approval; no order, contract, or term change is made.\n"]
        for phase in ROADMAP:
            lines.append(f"**{phase['phase']}**")
            for step in phase["steps"]:
                lines.append(f"- {step}")
            if phase["phase"].startswith("Phase 4"):
                lines.append(f"- Risk score target: <{ROADMAP_RISK_TARGET} (from {SUPPLIERS['SUP-101']['overall_risk']})")
            lines.append("")
        lines.append("Source: [Project Management + Procurement] (synthetic)")
        lines.append("\nWant to see ongoing monitoring?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _monitoring_plan(self, **kwargs) -> str:
        m = MONITORING_DESIGN
        lines = ["## Real-Time Risk Monitoring System\n",
                 "> Synthetic recommended monitoring design; no feed, alert, or automated action is activated by this agent.\n",
                 "**Data Sources (24/7 Scanning):**"]
        lines += [f"- {x}" for x in m["data_sources"]]
        lines.append("\n**Alert Thresholds:**")
        lines += [f"- {x}" for x in m["alert_thresholds"]]
        lines.append("\n**Automated Actions (recommended rules, each requires approval to activate):**")
        lines += [f"- {x}" for x in m["automated_actions"]]
        lines.append("\n**Success Metrics (synthetic pilot benchmarks):**")
        lines += [f"- {x}" for x in m["success_metrics"]]
        lines.append("\nSource: [Azure AI + Power Platform + Risk Intelligence] (synthetic)")
        lines.append("\nYour supply chain now has a ready-to-approve design for enterprise-grade risk monitoring and mitigation.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = SupplierRiskMonitoringAgent()
    for op in ["risk_dashboard", "supplier_scorecard", "mitigation_plan", "financial_impact",
               "implementation_roadmap", "monitoring_plan", "disruption_alerts", "alternative_sourcing"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
