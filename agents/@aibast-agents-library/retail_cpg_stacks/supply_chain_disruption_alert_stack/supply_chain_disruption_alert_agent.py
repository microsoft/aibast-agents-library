"""
Supply Chain Disruption Alert Agent — Retail & CPG Stack

Monitors supply chain routes for disruptions, assesses risk levels,
generates mitigation plans, and identifies alternative suppliers.

Demo scenario (synthetic): a conveyor failure at the Portland DC causes
cascading stockouts across 12 Northwest stores. The agent runs the root-cause
analysis, compares emergency options, drafts the Denver DC transfer plan,
tracks the DC recovery, and prepares the executive incident report and the
crisis summary. Every execution step is a draft for the operations owner.
"""

import sys
import os

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"),
)
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/supply-chain-disruption-alert",
    "version": "1.1.0",
    "display_name": "Supply Chain Disruption Alert Agent",
    "description": (
        "Analyze a synthetic supply-chain snapshot for disruptions, route risk, mitigation scenarios, and alternative-supplier due diligence. Use for planning and continuity questions. The agent never changes a purchase order, activates a supplier, reroutes a shipment, or moves inventory; procurement and operations owners must approve actions through future authenticated tools."
    ),
    "author": "AIBAST",
    "tags": [
        "supply-chain",
        "disruption",
        "risk-management",
        "logistics",
        "retail",
    ],
    "category": "retail_cpg",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic Data — Supply Chain Network
# ---------------------------------------------------------------------------

SUPPLY_ROUTES = {
    "RT-APAC-01": {
        "name": "Asia-Pacific Primary",
        "origin": "Shenzhen, China",
        "destination": "Los Angeles, CA",
        "transport_mode": "ocean_freight",
        "transit_days": 18,
        "carriers": ["COSCO Shipping", "Evergreen Marine"],
        "annual_volume_teu": 4800,
        "annual_value_usd": 28500000.00,
        "categories": ["Electronics", "Accessories"],
        "current_status": "disrupted",
        "reliability_score": 0.82,
    },
    "RT-EURO-01": {
        "name": "European Apparel Route",
        "origin": "Porto, Portugal",
        "destination": "Newark, NJ",
        "transport_mode": "ocean_freight",
        "transit_days": 12,
        "carriers": ["Maersk Line", "MSC"],
        "annual_volume_teu": 2200,
        "annual_value_usd": 15800000.00,
        "categories": ["Apparel"],
        "current_status": "at_risk",
        "reliability_score": 0.91,
    },
    "RT-DOMESTIC-01": {
        "name": "West Coast to Midwest",
        "origin": "Los Angeles, CA",
        "destination": "Chicago, IL",
        "transport_mode": "intermodal_rail",
        "transit_days": 4,
        "carriers": ["Union Pacific", "BNSF Railway"],
        "annual_volume_teu": 6500,
        "annual_value_usd": 42000000.00,
        "categories": ["Electronics", "Accessories", "Apparel", "Footwear"],
        "current_status": "normal",
        "reliability_score": 0.95,
    },
    "RT-LATAM-01": {
        "name": "Central America Footwear",
        "origin": "Leon, Mexico",
        "destination": "Dallas, TX",
        "transport_mode": "trucking",
        "transit_days": 3,
        "carriers": ["J.B. Hunt", "Werner Enterprises"],
        "annual_volume_teu": 1800,
        "annual_value_usd": 12400000.00,
        "categories": ["Footwear"],
        "current_status": "normal",
        "reliability_score": 0.93,
    },
    "RT-SEASIA-01": {
        "name": "Southeast Asia Textiles",
        "origin": "Ho Chi Minh City, Vietnam",
        "destination": "Savannah, GA",
        "transport_mode": "ocean_freight",
        "transit_days": 22,
        "carriers": ["Yang Ming", "ONE Line"],
        "annual_volume_teu": 3100,
        "annual_value_usd": 19200000.00,
        "categories": ["Apparel", "Home"],
        "current_status": "disrupted",
        "reliability_score": 0.78,
    },
}

DISRUPTION_EVENTS = {
    "DISR-001": {
        "title": "Port Congestion — Los Angeles/Long Beach",
        "type": "port_congestion",
        "severity": "high",
        "affected_routes": ["RT-APAC-01"],
        "start_date": "2026-03-05",
        "estimated_resolution": "2026-03-28",
        "delay_days": 8,
        "affected_skus": ["SKU-1002", "SKU-1004", "SKU-1006", "SKU-1008"],
        "estimated_revenue_impact": 2150000.00,
        "description": (
            "Severe vessel queue at LA/LB ports due to labor slowdown and "
            "equipment shortages. Average vessel wait time is 6 days."
        ),
        "status": "active",
    },
    "DISR-002": {
        "title": "Typhoon Disruption — South China Sea",
        "type": "weather_event",
        "severity": "critical",
        "affected_routes": ["RT-APAC-01", "RT-SEASIA-01"],
        "start_date": "2026-03-10",
        "estimated_resolution": "2026-03-20",
        "delay_days": 12,
        "affected_skus": ["SKU-1002", "SKU-1003", "SKU-1004", "SKU-1006", "SKU-1008", "SKU-1010"],
        "estimated_revenue_impact": 3800000.00,
        "description": (
            "Typhoon Mirinae forcing rerouting of vessels through northern "
            "Pacific corridor. Multiple sailings cancelled or delayed."
        ),
        "status": "active",
    },
    "DISR-003": {
        "title": "EU Customs Regulation Change",
        "type": "regulatory",
        "severity": "medium",
        "affected_routes": ["RT-EURO-01"],
        "start_date": "2026-03-01",
        "estimated_resolution": "2026-04-15",
        "delay_days": 5,
        "affected_skus": ["SKU-1001", "SKU-1003"],
        "estimated_revenue_impact": 720000.00,
        "description": (
            "New EU sustainability documentation requirements adding processing "
            "time at origin. Additional compliance certificates needed for textiles."
        ),
        "status": "active",
    },
}

RISK_SCORES = {
    "RT-APAC-01": {
        "overall_risk": 0.78,
        "geopolitical": 0.65,
        "weather": 0.82,
        "infrastructure": 0.70,
        "labor": 0.75,
        "regulatory": 0.40,
        "financial": 0.35,
    },
    "RT-EURO-01": {
        "overall_risk": 0.45,
        "geopolitical": 0.30,
        "weather": 0.20,
        "infrastructure": 0.25,
        "labor": 0.35,
        "regulatory": 0.72,
        "financial": 0.28,
    },
    "RT-DOMESTIC-01": {
        "overall_risk": 0.22,
        "geopolitical": 0.05,
        "weather": 0.30,
        "infrastructure": 0.20,
        "labor": 0.25,
        "regulatory": 0.10,
        "financial": 0.15,
    },
    "RT-LATAM-01": {
        "overall_risk": 0.35,
        "geopolitical": 0.25,
        "weather": 0.15,
        "infrastructure": 0.40,
        "labor": 0.30,
        "regulatory": 0.45,
        "financial": 0.32,
    },
    "RT-SEASIA-01": {
        "overall_risk": 0.72,
        "geopolitical": 0.50,
        "weather": 0.85,
        "infrastructure": 0.55,
        "labor": 0.40,
        "regulatory": 0.48,
        "financial": 0.30,
    },
}

MITIGATION_PLAYBOOKS = {
    "port_congestion": {
        "label": "Port Congestion Mitigation",
        "immediate_actions": [
            "Divert eligible shipments to alternate ports (Oakland, Seattle-Tacoma)",
            "Activate premium drayage contracts for priority container retrieval",
            "Convert ocean shipments under 2 TEU to air freight for critical SKUs",
        ],
        "short_term_actions": [
            "Increase safety stock at distribution centers by 20%",
            "Negotiate priority berthing with carrier partners",
            "Activate cross-dock bypass for pre-cleared containers",
        ],
        "long_term_actions": [
            "Diversify port-of-entry strategy across West and East Coast",
            "Invest in inland port relationships for rail-direct receiving",
            "Develop dual-source contracts for top-volume categories",
        ],
        "estimated_mitigation_cost": 340000.00,
        "risk_reduction_pct": 45,
    },
    "weather_event": {
        "label": "Weather Event Mitigation",
        "immediate_actions": [
            "Activate emergency inventory reserves at regional warehouses",
            "Reroute in-transit vessels through safe corridors",
            "Expedite air freight for high-priority SKUs with less than 7 days supply",
        ],
        "short_term_actions": [
            "Shift demand to in-stock alternative products via merchandising",
            "Enable backorder with guaranteed delivery dates for affected items",
            "Communicate proactively with B2B customers on revised timelines",
        ],
        "long_term_actions": [
            "Integrate real-time weather monitoring into planning systems",
            "Build seasonal safety stock buffers for typhoon/hurricane seasons",
            "Qualify backup suppliers in geographically diverse regions",
        ],
        "estimated_mitigation_cost": 520000.00,
        "risk_reduction_pct": 55,
    },
    "regulatory": {
        "label": "Regulatory Change Mitigation",
        "immediate_actions": [
            "Engage customs broker to prepare updated documentation templates",
            "Pre-certify next 3 shipments with new compliance requirements",
            "Brief all origin-side partners on updated export procedures",
        ],
        "short_term_actions": [
            "Conduct compliance audit of all active POs on affected routes",
            "Update vendor manual with new regulatory requirements",
            "Schedule training session for procurement team",
        ],
        "long_term_actions": [
            "Subscribe to regulatory change monitoring service",
            "Build compliance buffer time into standard lead times",
            "Develop relationships with in-country compliance consultants",
        ],
        "estimated_mitigation_cost": 85000.00,
        "risk_reduction_pct": 70,
    },
}

ALTERNATIVE_SUPPLIERS = {
    "Electronics": [
        {
            "name": "TechSource Taiwan",
            "location": "Taipei, Taiwan",
            "lead_time_days": 21,
            "quality_rating": 4.5,
            "capacity_units_monthly": 15000,
            "price_premium_pct": 8.0,
            "certifications": ["ISO 9001", "ISO 14001"],
            "min_order_qty": 500,
        },
        {
            "name": "KoreanTech Partners",
            "location": "Incheon, South Korea",
            "lead_time_days": 19,
            "quality_rating": 4.7,
            "capacity_units_monthly": 10000,
            "price_premium_pct": 12.0,
            "certifications": ["ISO 9001", "IATF 16949"],
            "min_order_qty": 300,
        },
    ],
    "Apparel": [
        {
            "name": "TurkTex Industries",
            "location": "Istanbul, Turkey",
            "lead_time_days": 16,
            "quality_rating": 4.3,
            "capacity_units_monthly": 25000,
            "price_premium_pct": 5.0,
            "certifications": ["GOTS", "OEKO-TEX"],
            "min_order_qty": 1000,
        },
        {
            "name": "BanglaStitch Ltd",
            "location": "Dhaka, Bangladesh",
            "lead_time_days": 25,
            "quality_rating": 4.0,
            "capacity_units_monthly": 40000,
            "price_premium_pct": -3.0,
            "certifications": ["WRAP", "BSCI"],
            "min_order_qty": 2000,
        },
    ],
    "Footwear": [
        {
            "name": "IndoSole Manufacturing",
            "location": "Tangerang, Indonesia",
            "lead_time_days": 28,
            "quality_rating": 4.2,
            "capacity_units_monthly": 18000,
            "price_premium_pct": 2.0,
            "certifications": ["ISO 9001", "SA8000"],
            "min_order_qty": 800,
        },
    ],
    "Accessories": [
        {
            "name": "IndiaGlobal Accessories",
            "location": "Mumbai, India",
            "lead_time_days": 24,
            "quality_rating": 4.1,
            "capacity_units_monthly": 30000,
            "price_premium_pct": -5.0,
            "certifications": ["ISO 9001"],
            "min_order_qty": 1500,
        },
        {
            "name": "MediterraneanCraft Co",
            "location": "Florence, Italy",
            "lead_time_days": 14,
            "quality_rating": 4.8,
            "capacity_units_monthly": 5000,
            "price_premium_pct": 25.0,
            "certifications": ["ISO 9001", "Made in Italy"],
            "min_order_qty": 200,
        },
    ],
    "Home": [
        {
            "name": "ThaiHome Products",
            "location": "Bangkok, Thailand",
            "lead_time_days": 20,
            "quality_rating": 4.3,
            "capacity_units_monthly": 12000,
            "price_premium_pct": 4.0,
            "certifications": ["ISO 9001", "FSC"],
            "min_order_qty": 600,
        },
    ],
}


# ---------------------------------------------------------------------------
# Synthetic Data — Portland DC disruption (the demo walkthrough)
# ---------------------------------------------------------------------------

DC_INCIDENT = {
    "id": "DISR-PDX-01",
    "dc": "Portland DC",
    "region": "Northwest",
    "root_cause": "Equipment failure (main conveyor)",
    "backup_days": 3,
    "stores_in_network": 47,
    "lost_revenue_per_week": 84300,
    "complaints": 37,
    "complaint_increase_pct": 280,
    "social": "social media mentions spiking",
}

NORTHWEST_STORES = [
    {"store": "Seattle Flagship", "stockout_pct": 47},
    {"store": "Portland South", "stockout_pct": 31},
    {"store": "Tacoma Mall", "stockout_pct": 29},
    {"store": "Bellevue Square", "stockout_pct": 27},
    {"store": "Olympia Center", "stockout_pct": 24},
    {"store": "Spokane Valley", "stockout_pct": 22},
    {"store": "Portland Pearl", "stockout_pct": 18},
    {"store": "Eugene Valley", "stockout_pct": 16},
    {"store": "Salem Center", "stockout_pct": 15},
    {"store": "Everett Commons", "stockout_pct": 14},
    {"store": "Vancouver Plaza", "stockout_pct": 12},
    {"store": "Boise Towne", "stockout_pct": 11},
]

AFFECTED_CATEGORIES = {"Electronics": 42, "Apparel": 38, "Home goods": 31, "Sporting": 32}

EMERGENCY_OPTIONS = [
    {
        "option": "A",
        "name": "Denver DC Emergency Transfer",
        "timeline": "36 hours to Seattle",
        "coverage": "Top 80 priority SKUs delivered",
        "cost": 15600,
        "cost_note": "truck + handling",
        "recovery": 47000,
        "window": "5-day window",
        "additional_loss": 0,
    },
    {
        "option": "B",
        "name": "Partial Fill + Wait",
        "timeline": "2 days for Portland recovery",
        "coverage": "Only 40% of SKUs restored",
        "cost": 0,
        "cost_note": "no added freight",
        "recovery": 0,
        "window": "none",
        "additional_loss": 127000,
    },
]

EXPANSION = {
    "stores": ["Portland South", "Tacoma Mall", "Bellevue Square", "Olympia Center", "Spokane Valley"],
    "cost": 8900,
    "recovery": 31000,
    "skus_per_store": 60,
    "arrival": "Saturday morning",
    "focus": "highest velocity items",
}

TRANSFER_PLAN = {
    "source_dc": "Denver DC",
    "dc_contact": "Lisa Park, Denver DC operations manager",
    "primary_store": "Seattle Flagship",
    "primary_skus": 80,
    "primary_focus": "electronics priority",
    "departure": "Tonight 6 PM",
    "arrival": "Friday 10 AM",
    "coordination": [
        "Teams notice to the 6 store managers",
        "Receiving staff schedule for Friday and Saturday",
        "Restocking plans for store tablets",
        "Customer SMS notification for back-in-stock items",
    ],
}

SHIPMENT_STATUS = {
    "truck": "Denver truck",
    "departed": "6:04 PM",
    "eta": "Friday 9:47 AM",
    "status": "On schedule",
}

DC_RECOVERY = [
    {"action": "Conveyor repair", "status": "In progress", "complete_by": "Thursday 8 PM"},
    {"action": "Backlog processing", "status": "Staged", "complete_by": "Friday 6 AM"},
    {"action": "Normal ops resume", "status": "Planned", "complete_by": "Friday noon"},
]

BACKLOG = {"pending_orders": 340, "priority": "Seattle + affected stores first", "full_clearance": "Saturday end of day"}

PREVENTION = {"item": "Backup conveyor system", "investment": 145000, "install_hours": 48, "three_year_avoided_losses": 340000}

RESPONSE_PERFORMANCE = {
    "detection_to_action_minutes": 47,
    "alternative_dc_hours": 36,
    "days_to_95pct_inventory": 3,
    "csat": 4.2,
    "alert_tuning_minutes_saved": 18,
}

LESSONS_LEARNED = [
    "Backup conveyor needed ($145K)",
    "Multi-DC sourcing rules updated",
    "Monitoring alerts tuned (reduce response time by 18 minutes)",
]

DEMO_GATE = (
    "> Synthetic incident snapshot. Draft for the operations owner: no truck, "
    "transfer, order, notification, SMS or report has been dispatched or sent."
)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _total_revenue_at_risk():
    return sum(d["estimated_revenue_impact"] for d in DISRUPTION_EVENTS.values() if d["status"] == "active")


def _affected_route_count():
    affected = set()
    for d in DISRUPTION_EVENTS.values():
        if d["status"] == "active":
            affected.update(d["affected_routes"])
    return len(affected)


def _risk_level_label(score):
    if score >= 0.70:
        return "HIGH"
    if score >= 0.40:
        return "MEDIUM"
    return "LOW"


def _total_mitigation_cost():
    seen_types = set()
    total = 0.0
    for d in DISRUPTION_EVENTS.values():
        if d["status"] == "active" and d["type"] not in seen_types:
            pb = MITIGATION_PLAYBOOKS.get(d["type"], {})
            total += pb.get("estimated_mitigation_cost", 0)
            seen_types.add(d["type"])
    return total


def _money(value):
    return f"${value:,.0f}"


def _k(value):
    return f"${value / 1000:g}K"


def _incident_totals():
    a = EMERGENCY_OPTIONS[0]
    cost = a["cost"] + EXPANSION["cost"]
    recovery = a["recovery"] + EXPANSION["recovery"]
    return cost, recovery, recovery - cost


def _ratio(numerator, denominator):
    return f"{round(numerator / denominator)}:1" if denominator else "n/a"


def _best_alternative(category):
    alts = ALTERNATIVE_SUPPLIERS.get(category, [])
    if not alts:
        return None
    return min(alts, key=lambda a: a["lead_time_days"])


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

class SupplyChainDisruptionAlertAgent(BasicAgent):
    """Agent for supply chain disruption monitoring and mitigation."""

    def __init__(self):
        self.name = "supply-chain-disruption-alert-agent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"]
                + " Always use this tool for disruption questions. The demo incident is a Portland DC "
                "conveyor failure causing stockouts at 12 Northwest stores; its operations have demo "
                "defaults, so call it right away without asking for IDs. Approvals such as 'execute' or "
                "'distribute' return a ready-to-release draft; the tool never dispatches or sends."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "disruption_dashboard",
                            "risk_assessment",
                            "mitigation_plan",
                            "supplier_alternatives",
                            "root_cause_analysis",
                            "emergency_options",
                            "transfer_plan",
                            "recovery_plan",
                            "incident_report",
                            "incident_summary",
                        ],
                        "description": (
                            "root_cause_analysis for unusual inventory movement or stockouts at the Northwest "
                            "stores (what is happening); emergency_options for emergency options and costs; "
                            "transfer_plan for 'approved, execute Seattle and the 5 additional stores'; "
                            "recovery_plan for tracking and the Portland DC recovery plan; incident_report for "
                            "the executive report with financial impact; incident_summary for 'distribute the "
                            "report and summarize what we accomplished'; disruption_dashboard for inbound ocean "
                            "and port events; risk_assessment for route risk scoring; mitigation_plan for a "
                            "DISR-00x mitigation scenario; supplier_alternatives for backup suppliers."
                        ),
                    },
                    "route_id": {"type": "string", "description": "Optional synthetic route ID such as RT-APAC-01."},
                    "disruption_id": {"type": "string", "description": "Optional synthetic disruption ID such as DISR-002."},
                    "category": {"type": "string", "description": "Optional product category such as Electronics."},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def _disruption_dashboard(self, **kwargs):
        rev_at_risk = _total_revenue_at_risk()
        routes_affected = _affected_route_count()
        lines = [
            "# Supply Chain Disruption Dashboard",
            "",
            f"**Active Disruptions:** {len([d for d in DISRUPTION_EVENTS.values() if d['status'] == 'active'])}",
            f"**Routes Affected:** {routes_affected} of {len(SUPPLY_ROUTES)}",
            f"**Total Revenue at Risk:** ${rev_at_risk:,.2f}",
            "",
            "## Active Disruption Events",
            "",
            "| ID | Title | Type | Severity | Delay | Revenue Impact | Resolution ETA |",
            "|----|-------|------|----------|-------|----------------|----------------|",
        ]
        for did, d in DISRUPTION_EVENTS.items():
            if d["status"] == "active":
                lines.append(
                    f"| {did} | {d['title']} | {d['type'].replace('_', ' ')} "
                    f"| {d['severity'].upper()} | +{d['delay_days']}d "
                    f"| ${d['estimated_revenue_impact']:,.2f} | {d['estimated_resolution']} |"
                )
        lines.append("")
        lines.append("## Route Status Overview")
        lines.append("")
        lines.append("| Route | Origin | Destination | Mode | Status | Reliability |")
        lines.append("|-------|--------|-------------|------|--------|-------------|")
        for rid, route in SUPPLY_ROUTES.items():
            status_display = route["current_status"].upper().replace("_", " ")
            lines.append(
                f"| {route['name']} | {route['origin']} | {route['destination']} "
                f"| {route['transport_mode'].replace('_', ' ')} "
                f"| {status_display} | {route['reliability_score']*100:.0f}% |"
            )
        lines.append("")
        for did, d in DISRUPTION_EVENTS.items():
            if d["status"] == "active":
                lines.append(f"### {did}: {d['title']}")
                lines.append("")
                lines.append(f"{d['description']}")
                lines.append("")
                lines.append(f"**Affected SKUs:** {', '.join(d['affected_skus'])}")
                lines.append(f"**Affected Routes:** {', '.join(d['affected_routes'])}")
                lines.append("")
        lines.append("> Synthetic monitoring snapshot. Validate live supplier, logistics, order, and customer data before action.")
        return "\n".join(lines)

    def _risk_assessment(self, **kwargs):
        route_id = kwargs.get("route_id")
        if route_id:
            if route_id not in RISK_SCORES:
                return f"Route `{route_id}` not found. Valid route IDs: {', '.join(RISK_SCORES)}"
            routes = {route_id: RISK_SCORES[route_id]}
        else:
            routes = RISK_SCORES
        lines = [
            "# Supply Chain Risk Assessment",
            "",
            "## Risk Score Matrix",
            "",
            "| Route | Overall | Geopolitical | Weather | Infrastructure | Labor | Regulatory | Financial |",
            "|-------|---------|--------------|---------|----------------|-------|------------|-----------|",
        ]
        for rid, scores in routes.items():
            route_name = SUPPLY_ROUTES.get(rid, {}).get("name", rid)
            level = _risk_level_label(scores["overall_risk"])
            lines.append(
                f"| {route_name} | **{scores['overall_risk']:.2f}** ({level}) "
                f"| {scores['geopolitical']:.2f} | {scores['weather']:.2f} "
                f"| {scores['infrastructure']:.2f} | {scores['labor']:.2f} "
                f"| {scores['regulatory']:.2f} | {scores['financial']:.2f} |"
            )
        lines.append("")
        lines.append("## Risk Level Distribution")
        lines.append("")
        high = sum(1 for s in routes.values() if s["overall_risk"] >= 0.70)
        med = sum(1 for s in routes.values() if 0.40 <= s["overall_risk"] < 0.70)
        low = sum(1 for s in routes.values() if s["overall_risk"] < 0.40)
        lines.append(f"- **HIGH risk routes:** {high}")
        lines.append(f"- **MEDIUM risk routes:** {med}")
        lines.append(f"- **LOW risk routes:** {low}")
        lines.append("")
        lines.append("## Highest Risk Factors")
        lines.append("")
        all_factors = {}
        for scores in routes.values():
            for factor in ["geopolitical", "weather", "infrastructure", "labor", "regulatory", "financial"]:
                all_factors.setdefault(factor, []).append(scores[factor])
        for factor, values in sorted(all_factors.items(), key=lambda x: -max(x[1])):
            avg_score = sum(values) / len(values)
            peak = max(values)
            lines.append(f"- **{factor.title()}:** avg {avg_score:.2f}, peak {peak:.2f}")
        lines.append("")
        lines.append("> Decision-support score only; it is not a supplier default prediction or authorization to change supply.")
        return "\n".join(lines)

    def _mitigation_plan(self, **kwargs):
        disruption_id = kwargs.get("disruption_id")
        if disruption_id:
            events = {disruption_id: DISRUPTION_EVENTS[disruption_id]} if disruption_id in DISRUPTION_EVENTS else {}
        else:
            events = {k: v for k, v in DISRUPTION_EVENTS.items() if v["status"] == "active"}
        seen_types, total_cost = [], 0.0
        for event in events.values():
            if event["type"] not in seen_types and event["type"] in MITIGATION_PLAYBOOKS:
                seen_types.append(event["type"])
                total_cost += MITIGATION_PLAYBOOKS[event["type"]]["estimated_mitigation_cost"]
        if disruption_id and not events:
            return f"Disruption `{disruption_id}` not found. Valid: {', '.join(DISRUPTION_EVENTS)}"
        lines = [
            "# Draft Disruption Mitigation Scenario",
            "",
            f"**Estimated Total Mitigation Investment:** ${total_cost:,.2f}",
            "",
        ]
        for did, event in events.items():
            playbook = MITIGATION_PLAYBOOKS.get(event["type"], {})
            if not playbook:
                continue
            lines.append(f"## {did}: {event['title']}")
            lines.append(f"**Playbook:** {playbook['label']}")
            lines.append(f"**Expected Risk Reduction:** {playbook['risk_reduction_pct']}%")
            lines.append(f"**Mitigation Cost:** ${playbook['estimated_mitigation_cost']:,.2f}")
            lines.append("")
            lines.append("### Proposed immediate actions (0-48 hours)")
            for action in playbook["immediate_actions"]:
                lines.append(f"1. Consider: {action}")
            lines.append("")
            lines.append("### Short-Term Actions (1-2 weeks)")
            for action in playbook["short_term_actions"]:
                lines.append(f"1. {action}")
            lines.append("")
            lines.append("### Long-Term Actions (1-3 months)")
            for action in playbook["long_term_actions"]:
                lines.append(f"1. {action}")
            lines.append("")
        lines.append("> Approval gate: no purchase order, supplier, shipment, route, or inventory position has been changed.")
        return "\n".join(lines)

    def _supplier_alternatives(self, **kwargs):
        category = kwargs.get("category")
        if category:
            if category not in ALTERNATIVE_SUPPLIERS:
                return f"Category `{category}` not found. Valid: {', '.join(ALTERNATIVE_SUPPLIERS)}"
            cats = {category: ALTERNATIVE_SUPPLIERS[category]}
        else:
            cats = ALTERNATIVE_SUPPLIERS
        lines = ["# Alternative Supplier Directory", ""]
        for cat_name, suppliers in cats.items():
            best = _best_alternative(cat_name)
            lines.append(f"## {cat_name}")
            if best:
                lines.append(f"**Fastest candidate for due diligence:** {best['name']} — {best['lead_time_days']}d")
            lines.append("")
            lines.append("| Supplier | Location | Lead Time | Quality | Capacity/Mo | Price Premium | MOQ |")
            lines.append("|----------|----------|-----------|---------|-------------|---------------|-----|")
            for sup in suppliers:
                premium_str = f"+{sup['price_premium_pct']:.1f}%" if sup["price_premium_pct"] >= 0 else f"{sup['price_premium_pct']:.1f}%"
                lines.append(
                    f"| {sup['name']} | {sup['location']} | {sup['lead_time_days']}d "
                    f"| {sup['quality_rating']}/5.0 | {sup['capacity_units_monthly']:,} "
                    f"| {premium_str} | {sup['min_order_qty']:,} |"
                )
            lines.append("")
            lines.append("**Certifications:**")
            for sup in suppliers:
                lines.append(f"- {sup['name']}: {', '.join(sup['certifications'])}")
            lines.append("")
        total_suppliers = sum(len(s) for s in ALTERNATIVE_SUPPLIERS.values())
        lines.append(f"**Total Qualified Alternatives:** {total_suppliers} suppliers across {len(ALTERNATIVE_SUPPLIERS)} categories")
        lines.append("")
        lines.append("> Synthetic candidates only. Qualification, contracting, sourcing, and inventory movement require human approval and authenticated systems.")
        return "\n".join(lines)

    # ---- Portland DC walkthrough ---------------------------------------------

    def _root_cause_analysis(self, **kwargs):
        inc = DC_INCIDENT
        skus = sum(AFFECTED_CATEGORIES.values())
        hero = NORTHWEST_STORES[0]
        lines = [
            "# Root Cause Analysis: Northwest Stores",
            "",
            f"I've detected a supply chain disruption at {inc['dc']} causing cascading stockouts across "
            f"{len(NORTHWEST_STORES)} {inc['region']} stores (incident {inc['id']}).",
            "",
            "| Issue | Impact | Status |",
            "|---|---|---|",
            f"| {inc['dc']} delay | {inc['backup_days']}-day backup | Active |",
            f"| {hero['store']} | {hero['stockout_pct']}% stockout | Critical |",
            f"| SKUs affected | {skus} products | High |",
            f"| Lost revenue | {_money(inc['lost_revenue_per_week'])}/week | Escalating |",
            "",
            "**Affected Categories:**",
        ]
        for cat, n in AFFECTED_CATEGORIES.items():
            lines.append(f"- {cat}: {n} SKUs out")
        lines += [
            "",
            f"**Customer Impact:** {inc['complaints']} complaints (up {inc['complaint_increase_pct']}% vs baseline), {inc['social']}",
            "",
            "**Stores affected (stockout %):** " + "; ".join(f"{s['store']} {s['stockout_pct']}%" for s in NORTHWEST_STORES),
            "",
            "Source: [D365 Supply Chain + Store POS]",
            "",
            "Next step: should I show the emergency response options?",
            "",
            DEMO_GATE,
        ]
        return "\n".join(lines)

    def _emergency_options(self, **kwargs):
        a, b = EMERGENCY_OPTIONS[0], EMERGENCY_OPTIONS[1]
        lines = [
            "# Emergency Response Options",
            "",
            f"I've identified two response scenarios - emergency transfer from Denver DC offers the best ROI.",
            "",
        ]
        for o in EMERGENCY_OPTIONS:
            lines.append(f"## Option {o['option']}: {o['name']}")
            lines.append(f"- Timeline: {o['timeline']}")
            lines.append(f"- {o['coverage']}")
            lines.append(f"- Cost: {_money(o['cost'])} ({o['cost_note']})")
            if o["recovery"]:
                lines.append(f"- Revenue recovery: {_money(o['recovery'])} ({o['window']})")
                lines.append(f"- ROI: {_ratio(o['recovery'], o['cost'])}")
            if o["additional_loss"]:
                lines.append(f"- Revenue loss: {_money(o['additional_loss'])} additional")
            lines.append("")
        lines += [
            f"**Recommended:** Option {a['option']} + expand to {len(EXPANSION['stores'])} additional high-impact "
            f"stores for {_money(EXPANSION['cost'])} more ({', '.join(EXPANSION['stores'])}).",
            "",
            "Source: [Freight Networks + Sales Forecasting]",
            "",
            "Next step: approve the Denver transfer?",
            "",
            DEMO_GATE,
        ]
        return "\n".join(lines)

    def _transfer_plan(self, **kwargs):
        t, e, a = TRANSFER_PLAN, EXPANSION, EMERGENCY_OPTIONS[0]
        cost, recovery, _ = _incident_totals()
        lines = [
            "# Emergency Transfer Execution Plan (ready to release)",
            "",
            f"Emergency transfer from {t['source_dc']} is ready for you to release; confirm truck loading with "
            f"{t['dc_contact']}. Nothing has been dispatched yet.",
            "",
            f"## {t['primary_store']}",
            f"- Departure: {t['departure']}",
            f"- Arrival: {t['arrival']}",
            f"- {t['primary_skus']} SKUs ({t['primary_focus']})",
            f"- Cost {_money(a['cost'])}, recovery {_money(a['recovery'])}",
            "",
            f"## {len(e['stores'])} Additional Stores",
            f"- {', '.join(e['stores'])}",
            f"- Arrival: {e['arrival']}",
            f"- {e['skus_per_store']} SKUs each ({e['focus']})",
            f"- Cost {_money(e['cost'])}, recovery {_money(e['recovery'])}",
            "",
            "## Logistics Coordination (drafts ready for you to send)",
        ]
        for c in t["coordination"]:
            lines.append(f"- {c}: drafted, not sent")
        lines += [
            "",
            f"**Investment:** {_money(cost)} total | **Recovery:** {_money(recovery)} projected",
            "",
            "Source: [Freight Management + Store Operations]",
            "",
            "Next step: once released, want the live tracking view?",
            "",
            DEMO_GATE,
        ]
        return "\n".join(lines)

    def _recovery_plan(self, **kwargs):
        sh, b, pv = SHIPMENT_STATUS, BACKLOG, PREVENTION
        lines = [
            "# Shipment Tracking and Portland DC Recovery Plan",
            "",
            f"{DC_INCIDENT['dc']} root cause identified as {DC_INCIDENT['root_cause'].lower()} - recovery plan accelerated.",
            "",
            f"**Shipment Status (synthetic tracking snapshot after release):** {sh['truck']} departed {sh['departed']} | "
            f"ETA Seattle: {sh['eta']} | {sh['status']}",
            "",
            "## Portland DC Recovery",
            "",
            "| Action | Status | Complete By |",
            "|---|---|---|",
        ]
        for r in DC_RECOVERY:
            lines.append(f"| {r['action']} | {r['status']} | {r['complete_by']} |")
        lines += [
            "",
            "## Backlog Clearance",
            f"- {b['pending_orders']} pending orders queued",
            f"- Priority: {b['priority']}",
            f"- Full clearance: {b['full_clearance']}",
            "",
            f"**Prevention:** {pv['item']} recommended ({_k(pv['investment'])} investment, {pv['install_hours']}-hour install)",
            "",
            "Source: [IoT Sensors + DC Operations + Maintenance]",
            "",
            "Next step: generate the executive incident report?",
            "",
            DEMO_GATE,
        ]
        return "\n".join(lines)

    def _incident_report(self, **kwargs):
        cost, recovery, net = _incident_totals()
        rp, pv = RESPONSE_PERFORMANCE, PREVENTION
        lines = [
            "# Executive Incident Report (draft)",
            "",
            f"Executive incident report ready showing {_k(recovery)} revenue recovery from {_k(cost)} investment.",
            "",
            f"**Incident Summary:** {DC_INCIDENT['dc']} {DC_INCIDENT['root_cause'].lower()}, "
            f"{DC_INCIDENT['backup_days']}-day backup, {len(NORTHWEST_STORES)} stores affected.",
            "",
            "## Financial Impact",
            "",
            "| Metric | Value |",
            "|---|---|",
            f"| Revenue at risk | {_money(DC_INCIDENT['lost_revenue_per_week'])} |",
            f"| Emergency response cost | {_money(cost)} |",
            f"| Revenue recovered | {_money(recovery)} |",
            f"| Net value protected | {_money(net)} |",
            "",
            "## Response Performance",
            f"- Detection to action: {rp['detection_to_action_minutes']} minutes",
            f"- Alternative DC activation: {rp['alternative_dc_hours']} hours",
            f"- Stores back to 95% inventory: {rp['days_to_95pct_inventory']} days",
            f"- Customer satisfaction maintained: {rp['csat']}/5.0",
            "",
            "## Lessons Learned",
        ]
        for l in LESSONS_LEARNED:
            lines.append(f"- {l}")
        lines += [
            "",
            f"**3-Year Prevention Value:** {_k(pv['three_year_avoided_losses'])} avoided losses vs {_k(pv['investment'])} investment",
            "",
            "Source: [Financial Analysis + Operations Data]",
            "",
            "Next step: share with the executive team? The report is a draft ready for you to share.",
            "",
            DEMO_GATE,
        ]
        return "\n".join(lines)

    def _incident_summary(self, **kwargs):
        cost, recovery, net = _incident_totals()
        a, rp, pv = EMERGENCY_OPTIONS[0], RESPONSE_PERFORMANCE, PREVENTION
        stores = 1 + len(EXPANSION["stores"])
        lines = [
            "# Crisis Response Summary",
            "",
            "The report package is ready for you to distribute to leadership (not sent). Here's what we accomplished:",
            "",
            f"- Detected disruption - {DC_INCIDENT['dc']} {DC_INCIDENT['backup_days']}-day delay, {len(NORTHWEST_STORES)} stores affected, "
            f"{_k(round(DC_INCIDENT['lost_revenue_per_week'], -3))} at risk",
            f"- Analyzed options - Denver transfer {_ratio(a['recovery'], a['cost'])} ROI vs wait-and-lose scenario",
            f"- Prepared emergency plan - {stores} stores, {rp['alternative_dc_hours']}-hour delivery, {_k(cost)} investment",
            "- Coordinated operations - store managers, receiving crews, customer comms (drafts)",
            "- Monitored recovery - shipment tracking, Portland DC repair timeline",
            f"- Prevention planning - {_k(pv['investment'])} backup system, {_k(pv['three_year_avoided_losses'])} 3-year value",
            "",
            f"**Value Delivered:** {_money(net)} net recovery from rapid response",
            "",
            f"**Active Now:** monitoring on all {DC_INCIDENT['stores_in_network']} stores, Portland DC back online "
            f"{DC_RECOVERY[-1]['complete_by']}, emergency protocols updated",
            "",
            f"Your supply chain now has {rp['detection_to_action_minutes']}-minute detection-to-action capability.",
            "",
            "Distribution list (draft): regional leadership, operations, finance, store managers.",
            "",
            "Source: [All Connected Systems]",
            "",
            DEMO_GATE,
        ]
        return "\n".join(lines)

    def perform(self, **kwargs):
        operation = kwargs.get("operation", "disruption_dashboard")
        dispatch = {
            "disruption_dashboard": self._disruption_dashboard,
            "risk_assessment": self._risk_assessment,
            "mitigation_plan": self._mitigation_plan,
            "supplier_alternatives": self._supplier_alternatives,
            "root_cause_analysis": self._root_cause_analysis,
            "emergency_options": self._emergency_options,
            "transfer_plan": self._transfer_plan,
            "recovery_plan": self._recovery_plan,
            "incident_report": self._incident_report,
            "incident_summary": self._incident_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)


# ---------------------------------------------------------------------------
# Main — exercise all operations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = SupplyChainDisruptionAlertAgent()
    for op in ["root_cause_analysis", "emergency_options", "transfer_plan", "recovery_plan", "incident_report", "incident_summary"]:
        print("=" * 80)
        print(agent.perform(operation=op))
    print("=" * 80)
