"""
Building Permit Processing Agent — SLG Government Stack

Manages building permit workflows including status tracking, review
checklists, inspector assignments, and fee calculations for local
government permitting offices.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/building-permit-processing",
    "version": "1.0.0",
    "display_name": "Building Permit Processing Agent",
    "description": "Local government building permit processing with status tracking, review checklists, inspector assignment, and fee calculation.",
    "author": "AIBAST",
    "tags": ["permits", "building", "zoning", "inspection", "local-government", "fees"],
    "category": "slg_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PERMIT_APPLICATIONS = {
    "BP-2025-0101": {
        "applicant": "Greenfield Development LLC",
        "property_address": "4520 Oak Ridge Blvd",
        "parcel_id": "045-221-009",
        "permit_type": "new_construction",
        "description": "3-story mixed-use building — 12 residential units, ground floor retail",
        "submitted": "2025-01-15",
        "valuation": 4200000,
        "zoning_district": "MU-2 (Mixed Use)",
        "status": "plan_review",
        "assigned_reviewer": "Karen Whitfield",
        "review_cycle": 2,
    },
    "BP-2025-0102": {
        "applicant": "Johnson Family Trust",
        "property_address": "812 Maple Street",
        "parcel_id": "023-114-003",
        "permit_type": "residential_addition",
        "description": "650 sq ft second-story addition to single-family residence",
        "submitted": "2025-02-03",
        "valuation": 185000,
        "zoning_district": "R-1 (Single Family Residential)",
        "status": "approved",
        "assigned_reviewer": "Tom Delgado",
        "review_cycle": 1,
    },
    "BP-2025-0103": {
        "applicant": "Sunrise Solar Inc.",
        "property_address": "1100 Industrial Pkwy",
        "parcel_id": "067-340-015",
        "permit_type": "commercial_alteration",
        "description": "Rooftop solar installation — 240 panel array on warehouse",
        "submitted": "2025-02-20",
        "valuation": 320000,
        "zoning_district": "I-1 (Light Industrial)",
        "status": "inspection_scheduled",
        "assigned_reviewer": "Karen Whitfield",
        "review_cycle": 1,
    },
    "BP-2025-0104": {
        "applicant": "Metro School District",
        "property_address": "2200 Education Way",
        "parcel_id": "034-502-001",
        "permit_type": "institutional",
        "description": "New gymnasium and cafeteria wing — 18,000 sq ft",
        "submitted": "2025-01-28",
        "valuation": 6800000,
        "zoning_district": "PF (Public Facilities)",
        "status": "corrections_required",
        "assigned_reviewer": "Tom Delgado",
        "review_cycle": 3,
    },
}

ZONING_REQUIREMENTS = {
    "R-1 (Single Family Residential)": {
        "max_height": "35 ft / 2.5 stories",
        "setbacks": {"front": 25, "side": 5, "rear": 20},
        "lot_coverage": 40,
        "parking": "2 spaces per unit",
    },
    "MU-2 (Mixed Use)": {
        "max_height": "55 ft / 4 stories",
        "setbacks": {"front": 0, "side": 0, "rear": 10},
        "lot_coverage": 80,
        "parking": "1 space per unit + 1 per 500 sq ft commercial",
    },
    "I-1 (Light Industrial)": {
        "max_height": "45 ft / 3 stories",
        "setbacks": {"front": 20, "side": 10, "rear": 15},
        "lot_coverage": 60,
        "parking": "1 per 1,000 sq ft",
    },
    "PF (Public Facilities)": {
        "max_height": "50 ft / 3 stories",
        "setbacks": {"front": 30, "side": 15, "rear": 20},
        "lot_coverage": 50,
        "parking": "Per use determination",
    },
}

INSPECTION_SCHEDULE = {
    "BP-2025-0103": [
        {"type": "Electrical Rough-In", "inspector": "Dave Martinez", "date": "2025-03-20", "status": "scheduled"},
        {"type": "Structural Mounting", "inspector": "Lisa Park", "date": "2025-03-22", "status": "scheduled"},
        {"type": "Final Electrical", "inspector": "Dave Martinez", "date": "2025-04-05", "status": "pending"},
    ],
}

FEE_TABLES = {
    "plan_review": {"base": 250, "per_thousand_valuation": 4.50},
    "building_permit": {"base": 150, "per_thousand_valuation": 8.75},
    "electrical": {"base": 75, "per_thousand_valuation": 1.25},
    "plumbing": {"base": 75, "per_thousand_valuation": 1.25},
    "mechanical": {"base": 75, "per_thousand_valuation": 1.00},
    "fire_review": {"base": 200, "per_thousand_valuation": 2.00},
    "technology_surcharge": {"base": 25, "per_thousand_valuation": 0.50},
}

INSPECTORS = {
    "Dave Martinez": {"specialty": "Electrical", "available_slots": 3, "zone": "East"},
    "Lisa Park": {"specialty": "Structural", "available_slots": 2, "zone": "East"},
    "Carlos Reyes": {"specialty": "Plumbing/Mechanical", "available_slots": 4, "zone": "West"},
    "Ann Kowalski": {"specialty": "Fire/Life Safety", "available_slots": 2, "zone": "All"},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _calculate_fees(valuation):
    """Calculate permit fees based on project valuation."""
    fees = {}
    total = 0
    for fee_name, schedule in FEE_TABLES.items():
        amount = schedule["base"] + (valuation / 1000) * schedule["per_thousand_valuation"]
        amount = round(amount, 2)
        fees[fee_name] = amount
        total += amount
    return fees, round(total, 2)


def _review_checklist(permit_type):
    """Return review checklist items based on permit type."""
    common = [
        "Verify application completeness",
        "Confirm property ownership / authorization",
        "Zoning compliance verification",
        "Setback and height compliance",
        "Parking requirement verification",
    ]
    type_specific = {
        "new_construction": [
            "Structural engineering review",
            "Fire and life safety review",
            "Accessibility (ADA) compliance",
            "Stormwater management plan",
            "Utility connection approvals",
            "Environmental review (CEQA/NEPA if applicable)",
        ],
        "residential_addition": [
            "Structural adequacy of existing foundation",
            "Egress requirements met",
            "Energy code compliance (Title 24)",
        ],
        "commercial_alteration": [
            "Electrical load calculation review",
            "Fire alarm system impact assessment",
            "Structural load verification",
        ],
        "institutional": [
            "Structural engineering review",
            "Fire and life safety review",
            "ADA accessibility compliance",
            "School facility standards (DSA if applicable)",
            "Seismic compliance verification",
            "Hazardous materials assessment",
        ],
    }
    return common + type_specific.get(permit_type, [])


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class BuildingPermitProcessingAgent(BasicAgent):
    """Building permit processing agent for local government."""

    def __init__(self):
        self.name = "@aibast-agents-library/building-permit-processing"
        self.metadata = {
            "name": self.name,
            "display_name": "Building Permit Processing Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "permit_status",
                            "review_checklist",
                            "inspector_assignment",
                            "fee_calculation",
                        ],
                    },
                    "permit_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "permit_status")
        dispatch = {
            "permit_status": self._permit_status,
            "review_checklist": self._review_checklist,
            "inspector_assignment": self._inspector_assignment,
            "fee_calculation": self._fee_calculation,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _permit_status(self, **kwargs) -> str:
        permit_id = kwargs.get("permit_id")
        if permit_id and permit_id in PERMIT_APPLICATIONS:
            p = PERMIT_APPLICATIONS[permit_id]
            zoning = ZONING_REQUIREMENTS.get(p["zoning_district"], {})
            lines = [f"# Permit Status: {permit_id}\n"]
            lines.append(f"- **Applicant:** {p['applicant']}")
            lines.append(f"- **Address:** {p['property_address']}")
            lines.append(f"- **Parcel:** {p['parcel_id']}")
            lines.append(f"- **Type:** {p['permit_type'].replace('_', ' ').title()}")
            lines.append(f"- **Description:** {p['description']}")
            lines.append(f"- **Submitted:** {p['submitted']}")
            lines.append(f"- **Valuation:** ${p['valuation']:,.0f}")
            lines.append(f"- **Zoning:** {p['zoning_district']}")
            lines.append(f"- **Status:** {p['status'].replace('_', ' ').title()}")
            lines.append(f"- **Reviewer:** {p['assigned_reviewer']}")
            lines.append(f"- **Review Cycle:** {p['review_cycle']}")
            if zoning:
                lines.append(f"\n## Zoning Requirements — {p['zoning_district']}\n")
                lines.append(f"- Max Height: {zoning['max_height']}")
                lines.append(f"- Lot Coverage: {zoning['lot_coverage']}%")
                lines.append(f"- Parking: {zoning['parking']}")
                sb = zoning["setbacks"]
                lines.append(f"- Setbacks: Front {sb['front']}ft, Side {sb['side']}ft, Rear {sb['rear']}ft")
            return "\n".join(lines)

        lines = ["# Permit Applications Dashboard\n"]
        lines.append("| Permit ID | Applicant | Type | Valuation | Status | Reviewer |")
        lines.append("|---|---|---|---|---|---|")
        for pid, p in PERMIT_APPLICATIONS.items():
            lines.append(
                f"| {pid} | {p['applicant']} | {p['permit_type'].replace('_', ' ').title()} "
                f"| ${p['valuation']:,.0f} | {p['status'].replace('_', ' ').title()} | {p['assigned_reviewer']} |"
            )
        total_val = sum(p["valuation"] for p in PERMIT_APPLICATIONS.values())
        lines.append(f"\n**Total Applications:** {len(PERMIT_APPLICATIONS)}")
        lines.append(f"**Total Valuation:** ${total_val:,.0f}")
        return "\n".join(lines)

    def _review_checklist(self, **kwargs) -> str:
        permit_id = kwargs.get("permit_id", "BP-2025-0101")
        p = PERMIT_APPLICATIONS.get(permit_id, list(PERMIT_APPLICATIONS.values())[0])
        checklist = _review_checklist(p["permit_type"])
        lines = [f"# Review Checklist: {permit_id}\n"]
        lines.append(f"**Project:** {p['description']}")
        lines.append(f"**Type:** {p['permit_type'].replace('_', ' ').title()}")
        lines.append(f"**Reviewer:** {p['assigned_reviewer']}\n")
        for i, item in enumerate(checklist, 1):
            lines.append(f"- [ ] {i}. {item}")
        lines.append(f"\n**Total Items:** {len(checklist)}")
        return "\n".join(lines)

    def _inspector_assignment(self, **kwargs) -> str:
        lines = ["# Inspector Assignment\n"]
        lines.append("## Available Inspectors\n")
        lines.append("| Inspector | Specialty | Available Slots | Zone |")
        lines.append("|---|---|---|---|")
        for name, info in INSPECTORS.items():
            lines.append(f"| {name} | {info['specialty']} | {info['available_slots']} | {info['zone']} |")
        lines.append("\n## Scheduled Inspections\n")
        for pid, inspections in INSPECTION_SCHEDULE.items():
            p = PERMIT_APPLICATIONS.get(pid, {})
            lines.append(f"### {pid} — {p.get('property_address', 'Unknown')}\n")
            lines.append("| Type | Inspector | Date | Status |")
            lines.append("|---|---|---|---|")
            for insp in inspections:
                lines.append(f"| {insp['type']} | {insp['inspector']} | {insp['date']} | {insp['status'].title()} |")
            lines.append("")
        return "\n".join(lines)

    def _fee_calculation(self, **kwargs) -> str:
        permit_id = kwargs.get("permit_id")
        lines = ["# Permit Fee Calculation\n"]
        permits_to_calc = {}
        if permit_id and permit_id in PERMIT_APPLICATIONS:
            permits_to_calc = {permit_id: PERMIT_APPLICATIONS[permit_id]}
        else:
            permits_to_calc = PERMIT_APPLICATIONS
        for pid, p in permits_to_calc.items():
            fees, total = _calculate_fees(p["valuation"])
            lines.append(f"## {pid}: {p['applicant']}\n")
            lines.append(f"**Project Valuation:** ${p['valuation']:,.0f}\n")
            lines.append("| Fee Category | Amount |")
            lines.append("|---|---|")
            for fee_name, amount in fees.items():
                display = fee_name.replace("_", " ").title()
                lines.append(f"| {display} | ${amount:,.2f} |")
            lines.append(f"| **Total** | **${total:,.2f}** |")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = BuildingPermitProcessingAgent()
    print(agent.perform(operation="permit_status"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="permit_status", permit_id="BP-2025-0101"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="review_checklist", permit_id="BP-2025-0104"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="inspector_assignment"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="fee_calculation", permit_id="BP-2025-0101"))
