"""
Emission Tracking Agent for Energy sector.

Monitors greenhouse gas emissions across facilities, tracks regulatory
compliance, develops reduction plans, and analyzes carbon offset opportunities.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/emission-tracking",
    "version": "1.1.0",
    "display_name": "Emissions Tracking Agent",
    "description": "Analyze a synthetic facility emissions inventory for scope dashboards, threshold screening, reduction scenarios, and carbon-offset due diligence. Use for sustainability and emissions-planning questions. The agent never verifies an emissions claim, declares legal compliance, purchases credits, or files disclosures; qualified reviewers must approve source-backed conclusions through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["emissions", "carbon", "compliance", "ghg", "sustainability", "energy"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

FACILITIES = {
    "NE-01": {
        "name": "Boston Hub",
        "location": "Boston, MA",
        "region": "Northeast",
        "type": "gas_distribution_hub",
        "quarter_mt_co2e": {"scope_1": 4200, "scope_2": 1900, "scope_3": 600},
        "ch4_mt_co2e": 1180,
        "ch4_prior_year_mt_co2e": 1000,
        "alert_cause": "aging infrastructure",
        "next_quarter_allowance_mt": 4300,
        "projected_next_quarter_scope_1_mt": 4640,
    },
    "NE-02": {
        "name": "Hartford Generating Station",
        "location": "Hartford, CT",
        "region": "Northeast",
        "type": "natural_gas_plant",
        "quarter_mt_co2e": {"scope_1": 5100, "scope_2": 1600, "scope_3": 520},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 5500,
        "projected_next_quarter_scope_1_mt": 5100,
    },
    "NE-03": {
        "name": "Providence Peaker Plant",
        "location": "Providence, RI",
        "region": "Northeast",
        "type": "peaker_plant",
        "quarter_mt_co2e": {"scope_1": 3600, "scope_2": 900, "scope_3": 300},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 4000,
        "projected_next_quarter_scope_1_mt": 3600,
    },
    "NE-04": {
        "name": "Portland Fuel Terminal",
        "location": "Portland, ME",
        "region": "Northeast",
        "type": "fuel_terminal",
        "quarter_mt_co2e": {"scope_1": 2300, "scope_2": 1100, "scope_3": 410},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 2700,
        "projected_next_quarter_scope_1_mt": 2300,
    },
    "NE-05": {
        "name": "Albany Substation Campus",
        "location": "Albany, NY",
        "region": "Northeast",
        "type": "substation_campus",
        "quarter_mt_co2e": {"scope_1": 1900, "scope_2": 2400, "scope_3": 380},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 2300,
        "projected_next_quarter_scope_1_mt": 1900,
    },
    "NE-06": {
        "name": "Burlington Operations Center",
        "location": "Burlington, VT",
        "region": "Northeast",
        "type": "operations_center",
        "quarter_mt_co2e": {"scope_1": 800, "scope_2": 600, "scope_3": 200},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 1200,
        "projected_next_quarter_scope_1_mt": 800,
    },
    "NE-07": {
        "name": "Manchester Service Center",
        "location": "Manchester, NH",
        "region": "Northeast",
        "type": "service_center",
        "quarter_mt_co2e": {"scope_1": 1150, "scope_2": 1000, "scope_3": 290},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 1550,
        "projected_next_quarter_scope_1_mt": 1150,
    },
    "NE-08": {
        "name": "Worcester Compressor Station",
        "location": "Worcester, MA",
        "region": "Northeast",
        "type": "compressor_station",
        "quarter_mt_co2e": {"scope_1": 3400, "scope_2": 700, "scope_3": 330},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 3800,
        "projected_next_quarter_scope_1_mt": 3400,
    },
    "NE-09": {
        "name": "Springfield Fleet Depot",
        "location": "Springfield, MA",
        "region": "Northeast",
        "type": "fleet_depot",
        "quarter_mt_co2e": {"scope_1": 1250, "scope_2": 1200, "scope_3": 360},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 1650,
        "projected_next_quarter_scope_1_mt": 1250,
    },
    "NE-10": {
        "name": "New Haven Plant",
        "location": "New Haven, CT",
        "region": "Northeast",
        "type": "natural_gas_plant",
        "quarter_mt_co2e": {"scope_1": 2700, "scope_2": 1300, "scope_3": 450},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 3100,
        "projected_next_quarter_scope_1_mt": 2700,
    },
    "NE-11": {
        "name": "Syracuse Operations Center",
        "location": "Syracuse, NY",
        "region": "Northeast",
        "type": "operations_center",
        "quarter_mt_co2e": {"scope_1": 950, "scope_2": 1280, "scope_3": 270},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 1350,
        "projected_next_quarter_scope_1_mt": 950,
    },
    "NE-12": {
        "name": "Nashua Fleet Yard",
        "location": "Nashua, NH",
        "region": "Northeast",
        "type": "fleet_depot",
        "quarter_mt_co2e": {"scope_1": 800, "scope_2": 700, "scope_3": 400},
        "ch4_mt_co2e": 0,
        "ch4_prior_year_mt_co2e": 0,
        "alert_cause": "",
        "next_quarter_allowance_mt": 1200,
        "projected_next_quarter_scope_1_mt": 800,
    },
}

# Same quarter last year, portfolio totals (MT CO2e) for the YoY change.
PRIOR_YEAR_QUARTER = {"scope_1": 26017, "scope_2": 16701, "scope_3": 4362}

SCOPE_LABELS = {"scope_1": "Scope 1 (Direct)", "scope_2": "Scope 2 (Electricity)", "scope_3": "Scope 3 (Supply Chain)"}

# EPA regional screening threshold for the Northeast portfolio (quarterly MT CO2e).
REGIONAL_SCREENING = {"region": "Northeast", "quarterly_threshold_mt": 51450, "audit_in_days": 14}

CARBON_CREDIT_PRICE_PER_MT = 39.2

# Reduction opportunities, phased into the 18-month roadmap.
REDUCTION_ACTIONS = [
    {"phase": 1, "window": "Next 90 days", "start": "Next month", "action": "Boston Hub LDAR",
     "detail": "Accelerate leak detection and repair at Boston Hub", "facility": "NE-01",
     "cost": 85000, "reduction_mt": 3240, "annual_savings": 102000, "note": "compliance secured"},
    {"phase": 2, "window": "Months 4-9", "start": "Month 4", "action": "CHP + LED",
     "detail": "Combined heat and power at Hartford plus LED retrofits", "facility": "NE-02",
     "cost": 810000, "reduction_mt": 6260, "annual_savings": 607500, "note": "combined"},
    {"phase": 3, "window": "Months 10-15", "start": "Month 10", "action": "Fleet electrification",
     "detail": "Electrify Springfield and Nashua fleet vehicles", "facility": "NE-09",
     "cost": 520000, "reduction_mt": 3230, "annual_savings": 195000, "note": ""},
    {"phase": 4, "window": "Month 16+", "start": "Month 16", "action": "Renewable PPA",
     "detail": "50 MW solar power purchase agreement", "facility": "",
     "cost": 0, "reduction_mt": 0, "annual_savings": 0, "note": "Revenue neutral | 50MW solar"},
]

ROADMAP_BENCHMARK = "top 8% industry performance (synthetic benchmark)"
ROADMAP_MONTHS = 18

CARBON_OFFSETS = {
    "OFF-001": {"project": "Appalachian Reforestation", "type": "forestry", "credits_available": 45000, "price_per_tonne": 18.50, "vintage": 2025, "verified_by": "Verra VCS"},
    "OFF-002": {"project": "Texas Wind REC Bundle", "type": "renewable_energy", "credits_available": 120000, "price_per_tonne": 12.75, "vintage": 2026, "verified_by": "Green-e"},
    "OFF-003": {"project": "Montana Methane Capture", "type": "methane_capture", "credits_available": 28000, "price_per_tonne": 24.00, "vintage": 2025, "verified_by": "ACR"},
    "OFF-004": {"project": "Iowa Agricultural Soil Carbon", "type": "soil_carbon", "credits_available": 35000, "price_per_tonne": 22.00, "vintage": 2026, "verified_by": "Gold Standard"},
}

REGULATIONS = {
    "EPA_GHGRP": {"name": "EPA GHG Reporting Program", "threshold_co2": 25000, "deadline": "2026-03-31"},
    "CA_CAPANDTRADE": {"name": "California Cap-and-Trade", "threshold_co2": 25000, "deadline": "2026-04-01"},
    "EPA_NSPS": {"name": "EPA New Source Performance Standards", "threshold_co2": 0, "deadline": "2026-06-30"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selected_facilities(facility_id=None):
    """All facilities, or those whose ID equals / name contains the query (may be empty)."""
    if facility_id:
        query = facility_id.lower().strip()
        if query == "all" or REGIONAL_SCREENING["region"].lower() in query:
            return FACILITIES
        return {
            fid: facility
            for fid, facility in FACILITIES.items()
            if query == fid.lower() or query in facility["name"].lower()
        }
    return FACILITIES


def _not_found(facility_id):
    return (f"No synthetic facility matches `{facility_id}`. Facilities: "
            + ", ".join(f["name"] for f in FACILITIES.values()) + ".")


def _scope_totals(facilities):
    totals = {"scope_1": 0, "scope_2": 0, "scope_3": 0}
    for f in facilities.values():
        for k in totals:
            totals[k] += f["quarter_mt_co2e"][k]
    return totals


def _share(part, whole):
    """Share of total, truncated to one decimal so the shares never add to more than 100%."""
    return int(part * 1000 / whole) / 10


def _yoy(current, prior):
    return round((current - prior) * 100 / prior, 1)


def _facility_alerts(facilities):
    """Facilities whose methane rose year over year or whose projection exceeds next quarter's allowance."""
    alerts = []
    for fid, f in facilities.items():
        over = f["projected_next_quarter_scope_1_mt"] - f["next_quarter_allowance_mt"]
        ch4 = 0
        if f["ch4_prior_year_mt_co2e"]:
            ch4 = int((f["ch4_mt_co2e"] - f["ch4_prior_year_mt_co2e"]) * 100 / f["ch4_prior_year_mt_co2e"] + 0.5)
        if over > 0 or ch4 > 0:
            alerts.append({"id": fid, "name": f["name"], "ch4_yoy_pct": ch4, "over_allowance_mt": over,
                           "cause": f["alert_cause"]})
    return alerts


def _payback_months(action):
    if not action["annual_savings"]:
        return 0
    return int(action["cost"] * 12 / action["annual_savings"] + 0.5)


def _money(amount):
    """85000 -> '$85K'; 1200000 -> '$1.2M'."""
    if amount >= 1000000:
        return f"${amount / 1000000:.1f}M"
    return f"${amount // 1000}K"


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "emissions_dashboard",
    "compliance_status",
    "reduction_plan",
    "carbon_offset_analysis",
    "implementation_roadmap",
]


class EmissionTrackingAgent(BasicAgent):
    """GHG emission monitoring and compliance tracking agent."""

    def __init__(self):
        self.name = "EmissionTrackingAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"]
                + " Always use this tool for the Northeast carbon emissions analysis: 'I need a carbon emissions "
                "analysis for our Northeast facilities' uses emissions_dashboard; 'top reduction opportunities' "
                "uses reduction_plan; 'create the implementation roadmap' uses implementation_roadmap. The 12 "
                "Northeast facilities are the default; call the tool without asking for details."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "Choose emissions_dashboard for the quarterly emissions analysis (scope totals, share, "
                            "YoY, screening buffer, facility alerts), compliance_status for non-legal threshold "
                            "screening and allowance projections, reduction_plan for the top reduction opportunities "
                            "with cost analysis, carbon_offset_analysis for credit due diligence, or "
                            "implementation_roadmap for the phased 18-month implementation roadmap."
                        ),
                    },
                    "facility_id": {
                        "type": "string",
                        "description": "Optional synthetic facility ID or facility-name substring, such as NE-01 or Boston (omit, or say Northeast, for all 12 facilities). Unknown values return a not-found message.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "emissions_dashboard")
        facility_id = kwargs.get("facility_id")
        facilities = _selected_facilities(facility_id)
        if not facilities:
            return _not_found(facility_id)
        if op == "emissions_dashboard":
            return self._emissions_dashboard(facilities)
        elif op == "compliance_status":
            return self._compliance_status(facilities)
        elif op == "reduction_plan":
            return self._reduction_plan(facilities)
        elif op == "carbon_offset_analysis":
            return self._carbon_offset_analysis(facilities)
        elif op == "implementation_roadmap":
            return self._implementation_roadmap()
        return f"**Error:** Unknown operation `{op}`."

    def _emissions_dashboard(self, facilities) -> str:
        totals = _scope_totals(facilities)
        total = totals["scope_1"] + totals["scope_2"] + totals["scope_3"]
        whole = len(facilities) == len(FACILITIES)
        alerts = _facility_alerts(facilities)
        lines = ["# Emissions Dashboard", ""]
        if whole:
            buffer = round((REGIONAL_SCREENING["quarterly_threshold_mt"] - total) * 100
                           / REGIONAL_SCREENING["quarterly_threshold_mt"])
            focus = f", but {alerts[0]['name']} needs attention" if alerts else ""
            lines += [f"I've analyzed emissions across your {len(facilities)} {REGIONAL_SCREENING['region']} facilities. "
                      f"You're within the screening threshold with an {buffer}% buffer{focus}.", ""]
        lines += [f"**Quarterly Emissions ({total:,} MT CO2e)**", "",
                  "| Scope | Emissions | % Total | YoY Change |",
                  "|-------|-----------|---------|------------|"]
        for k, label in SCOPE_LABELS.items():
            yoy = f"{_yoy(totals[k], PRIOR_YEAR_QUARTER[k]):+}%" if whole else "n/a"
            lines.append(f"| {label} | {totals[k]:,} MT | {_share(totals[k], total)}% | {yoy} |")
        if whole:
            lines += ["", f"**Compliance:** EPA {REGIONAL_SCREENING['region']} regional requirements met "
                          f"({total:,} of {REGIONAL_SCREENING['quarterly_threshold_mt']:,} MT screening threshold; "
                          "screening, not a legal determination)."]
        for a in alerts:
            lines.append(f"\n**Alert:** {a['name']} methane emissions up {a['ch4_yoy_pct']}% due to {a['cause']}. "
                         f"Current trajectory exceeds next-quarter allowances by {a['over_allowance_mt']} MT.")
            for act in REDUCTION_ACTIONS:
                if act["facility"] == a["id"]:
                    avoided = int(act["reduction_mt"] * CARBON_CREDIT_PRICE_PER_MT / 1000 + 0.5) * 1000
                    lines.append(f"**Action:** {act['detail']} - {_money(act['cost'])} cost avoids "
                                 f"{_money(avoided)} in carbon credits.")
        lines += ["", "| Facility | Location | Scope 1 | Scope 2 | Scope 3 | Total |",
                  "|----------|----------|---------|---------|---------|-------|"]
        for f in facilities.values():
            e = f["quarter_mt_co2e"]
            lines.append(f"| {f['name']} | {f['location']} | {e['scope_1']:,} | {e['scope_2']:,} | {e['scope_3']:,} "
                         f"| {e['scope_1'] + e['scope_2'] + e['scope_3']:,} |")
        lines += ["", "Source: [Azure IoT Hub + MS Cloud for Sustainability] (synthetic)", "",
                  "> Synthetic inventory, not verified emissions evidence. Validate boundaries, factors, units, and source records before making a claim.",
                  "", "Next: want to see the top reduction opportunities?"]
        return "\n".join(lines)

    def _compliance_status(self, facilities) -> str:
        totals = _scope_totals(facilities)
        total = totals["scope_1"] + totals["scope_2"] + totals["scope_3"]
        lines = ["# Compliance Status", ""]
        if len(facilities) == len(FACILITIES):
            threshold = REGIONAL_SCREENING["quarterly_threshold_mt"]
            buffer = round((threshold - total) * 100 / threshold)
            state = "BELOW SCREENING THRESHOLD" if total <= threshold else "ABOVE SCREENING THRESHOLD"
            lines += [f"**{REGIONAL_SCREENING['region']} portfolio:** {total:,} of {threshold:,} MT CO2e - {state} "
                      f"({buffer}% buffer). EPA audit in {REGIONAL_SCREENING['audit_in_days']} days.", ""]
        lines += ["| Facility | Scope 1 (quarter) | Next-Quarter Projection | Allowance | Status |",
                  "|----------|-------------------|-------------------------|-----------|--------|"]
        for f in facilities.values():
            over = f["projected_next_quarter_scope_1_mt"] - f["next_quarter_allowance_mt"]
            status = f"AT RISK (+{over} MT)" if over > 0 else "BELOW SCREENING THRESHOLD"
            lines.append(f"| {f['name']} | {f['quarter_mt_co2e']['scope_1']:,} | "
                         f"{f['projected_next_quarter_scope_1_mt']:,} | {f['next_quarter_allowance_mt']:,} | {status} |")
        lines += ["", "> Screening result only; it is not a legal compliance determination or an emissions claim."]
        return "\n".join(lines)

    def _reduction_plan(self, facilities) -> str:
        total = 0
        for k, v in _scope_totals(FACILITIES).items():
            total += v
        lines = ["# Emission Reduction Plans", "",
                 "Top reduction opportunities for the Northeast portfolio, ranked by payback:", "",
                 "| Opportunity | Cost | Reduction (MT) | Annual Savings | Payback | Carbon Credits Avoided |",
                 "|-------------|------|----------------|----------------|---------|------------------------|"]
        cut = 0
        for a in REDUCTION_ACTIONS:
            if a["cost"] == 0:
                lines.append(f"| {a['action']} ({a['detail']}) | Revenue neutral | - | - | - | - |")
                continue
            cut += a["reduction_mt"]
            avoided = int(a["reduction_mt"] * CARBON_CREDIT_PRICE_PER_MT / 1000 + 0.5) * 1000
            lines.append(f"| {a['action']} ({a['detail']}) | {_money(a['cost'])} | {a['reduction_mt']:,} | "
                         f"{_money(a['annual_savings'])} | {_payback_months(a)} months | {_money(avoided)} |")
        lines += ["", f"**Combined reduction:** {cut:,} MT of {total:,} MT per quarter "
                      f"({int(cut * 100 / total + 0.5)}%), at a carbon credit price of ${CARBON_CREDIT_PRICE_PER_MT}/MT.",
                  "", "> Scenario estimates require engineering, finance, environmental, and executive review before action.",
                  "", "Next: want me to create the implementation roadmap?"]
        return "\n".join(lines)

    def _carbon_offset_analysis(self, facilities) -> str:
        gap = 0
        for f in facilities.values():
            over = f["projected_next_quarter_scope_1_mt"] - f["next_quarter_allowance_mt"]
            if over > 0:
                gap += over
        lines = ["# Carbon Offset Analysis", "",
                 f"**Emission Gap to Cover:** {gap:,} MT (projected next-quarter overage)", "",
                 "| Project | Type | Credits Available | Price/t | Cost to Cover Gap | Verified By |",
                 "|---------|------|-------------------|---------|-------------------|-------------|"]
        for o in CARBON_OFFSETS.values():
            cover = min(gap, o["credits_available"])
            lines.append(f"| {o['project']} | {o['type']} | {o['credits_available']:,} | ${o['price_per_tonne']:.2f} "
                         f"| ${int(cover * o['price_per_tonne'] + 0.5):,} | {o['verified_by']} |")
        lines += ["", "Reducing at the source (Boston Hub LDAR) closes the gap without buying credits.", "",
                  "> Due-diligence shortlist only. No credit purchase, retirement, disclosure, or offset claim has been made."]
        return "\n".join(lines)

    def _implementation_roadmap(self) -> str:
        total = 0
        for v in _scope_totals(FACILITIES).values():
            total += v
        cut = 0
        lines = ["# Implementation Roadmap", ""]
        for a in REDUCTION_ACTIONS:
            cut += a["reduction_mt"]
        lines += [f"I've created an {ROADMAP_MONTHS}-month phased roadmap sequenced for quick wins and risk mitigation.", "",
                  "## Implementation Timeline", ""]
        for a in REDUCTION_ACTIONS:
            lines.append(f"**Phase {a['phase']} ({a['window']}) - {a['action']}**")
            if a["cost"] == 0:
                lines.append(f"- {a['note']}")
            else:
                lines.append(f"- Start: {a['start']} | Cost: {_money(a['cost'])}" + (f" {a['note']}" if a["note"] == "combined" else ""))
                impact = f"- Impact: {a['reduction_mt']:,} MT reduction"
                if a["note"] and a["note"] != "combined":
                    impact += f", {a['note']}"
                lines.append(impact)
                lines.append(f"- Payback: {_payback_months(a)} months")
            lines.append("")
        lines += [f"**Projected Outcome:** {int(cut * 100 / total + 0.5)}% emissions reduction "
                  f"({cut:,} of {total:,} MT per quarter), {ROADMAP_BENCHMARK}.", "",
                  "Source: [Project Planning + Financial Modeling] (synthetic)", "",
                  "> Draft roadmap. Scenario estimates require engineering, finance, environmental, and executive review before action; nothing is purchased or committed.",
                  "", "Next: want to prepare your EPA audit package?"]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = EmissionTrackingAgent()
    for op in ["emissions_dashboard", "implementation_roadmap", "reduction_plan", "compliance_status",
               "carbon_offset_analysis"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
