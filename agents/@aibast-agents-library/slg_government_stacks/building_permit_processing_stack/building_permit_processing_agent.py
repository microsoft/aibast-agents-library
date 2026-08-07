"""
Building Permit Processing Agent — SLG Government Stack

Manages building permit workflows including status tracking, review
checklists, inspector assignments, and fee calculations for local
government permitting offices.
"""

import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

TODAY = date.today()


def _d(offset_days):
    """Dates are computed from the run date so the backlog is never stale."""
    return (TODAY + timedelta(days=offset_days)).isoformat()

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/building-permit-processing",
    "version": "1.0.0",
    "display_name": "Building Permit Processing Agent",
    "description": "Automate building permit review processes to enable faster service, lower operational costs, and higher citizen satisfaction.",
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
        "submitted": _d(-48),
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
        "submitted": _d(-12),
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
        "submitted": _d(-26),
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
        "submitted": _d(-63),
        "valuation": 6800000,
        "zoning_district": "PF (Public Facilities)",
        "status": "corrections_required",
        "assigned_reviewer": "Tom Delgado",
        "review_cycle": 3,
    },
    "BP-2025-0105": {
        "applicant": "Greenfield Development LLC",
        "property_address": "4520 Oak Ridge Blvd",
        "parcel_id": "045-221-009",
        "permit_type": "new_construction",
        "description": "3-story mixed-use building - 12 residential units, ground floor retail",
        "submitted": _d(-3),
        "valuation": 4200000,
        "zoning_district": "MU-2 (Mixed Use)",
        "status": "intake",
        "assigned_reviewer": None,
        "review_cycle": 0,
        "documents": ["site_plan", "structural_calcs"],
    },
    "BP-2025-0106": {
        "applicant": "Ridgeline Restaurants Inc.",
        "property_address": "77 Harbor Way",
        "parcel_id": "012-088-024",
        "permit_type": "commercial_alteration",
        "description": "Tenant improvement - restaurant fit-out with commercial kitchen",
        "submitted": _d(-1),
        "valuation": 540000,
        "zoning_district": "MU-2 (Mixed Use)",
        "status": "intake",
        "assigned_reviewer": None,
        "review_cycle": 0,
        "documents": ["site_plan", "structural_calcs", "mep_drawings", "title_report"],
    },
}

# Statutory review clocks. Exceeding these is what generates the status-check
# calls the one-pager describes.
SLA_TARGETS_DAYS = {
    "new_construction": 30,
    "residential_addition": 15,
    "commercial_alteration": 21,
    "institutional": 45,
}

# Which desks a permit type has to clear, in order.
REVIEW_ROUTING = {
    "new_construction": ["Planning", "Zoning", "Structural", "Fire/Life Safety", "Public Works"],
    "residential_addition": ["Zoning", "Structural"],
    "commercial_alteration": ["Zoning", "Building", "Fire/Life Safety"],
    "institutional": ["Planning", "Zoning", "Structural", "Fire/Life Safety", "Public Works", "Health"],
}

# Intake completeness: what a submission must carry before the clock starts.
REQUIRED_DOCUMENTS = {
    "new_construction": ["site_plan", "structural_calcs", "mep_drawings", "title_report"],
    "residential_addition": ["site_plan", "structural_calcs"],
    "commercial_alteration": ["site_plan", "mep_drawings"],
    "institutional": ["site_plan", "structural_calcs", "mep_drawings", "title_report", "traffic_study"],
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
        {"type": "Electrical Rough-In", "inspector": "Dave Martinez", "date": _d(10), "status": "scheduled"},
        {"type": "Structural Mounting", "inspector": "Lisa Park", "date": _d(12), "status": "scheduled"},
        {"type": "Final Electrical", "inspector": "Dave Martinez", "date": _d(-5), "status": "pending"},
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


def _age_days(permit):
    """Calendar days since submission."""
    return (TODAY - date.fromisoformat(permit["submitted"])).days


def _sla_days(permit):
    return SLA_TARGETS_DAYS.get(permit["permit_type"], 30)


def _sla_state(permit):
    """(state, days_over) against the statutory review clock."""
    over = _age_days(permit) - _sla_days(permit)
    if permit["status"] == "approved":
        return "closed", over
    if over > 0:
        return "overdue", over
    if over > -5:
        return "at risk", over
    return "on track", over


def _complaint_risk(permit):
    """Who calls the front desk next.

    The one-pager's pain is 'applicants repeatedly called for status updates'.
    Risk rises with time over SLA and with each correction cycle, because every
    cycle is another round trip the applicant was not told about.
    """
    state, over = _sla_state(permit)
    if state == "closed":
        return 0
    score = max(0, over) * 2 + permit.get("review_cycle", 0) * 15
    if permit["status"] == "corrections_required":
        score += 20
    return min(100, score)


def _missing_documents(permit):
    required = REQUIRED_DOCUMENTS.get(permit["permit_type"], [])
    have = permit.get("documents", [])
    return [d for d in required if d not in have]


def _duplicate_of(permit_id, permit):
    """Same parcel + same applicant already in flight is a duplicate submission."""
    for other_id, other in PERMIT_APPLICATIONS.items():
        if other_id == permit_id:
            continue
        if (other["parcel_id"] == permit["parcel_id"]
                and other["applicant"] == permit["applicant"]
                and other["status"] not in ("approved",)):
            return other_id
    return None


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
        self.name = "BuildingPermitProcessingAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Building Permit Processing Agent",
            # __manifest__["description"] is the advertised one-liner from the
            # SharePoint listing; it is what the catalog page shows. The TOOL
            # description is what the model routes on, so it has to name the
            # surfaces a permitting office actually asks about in their own
            # words — front counter, status calls, the board, a job by street
            # name — or the model answers generically instead of calling this.
            "description": (
                "The city's building permit system of record. Use this for ANY question about "
                "building permits, permit applications, plan review, zoning review, inspections, "
                "inspectors, permit fees, or development services — including questions that never "
                "say the word 'permit', such as what is at the front counter or intake, what is in "
                "the queue or backlog, which applications are late or over the statutory clock, "
                "which applicant or resident is likely to complain or call for a status update, "
                "what to send applicants to stop status calls, who reviews an incoming application "
                "and when it is due back, duplicate or incomplete submissions, and which "
                "inspections are on the board for a job referred to by street name, applicant, or "
                "project type (for example 'the solar job' or 'the restaurant fit-out on Harbor "
                "Way'). Covers intake classification and validation, automatic routing to review "
                "teams, applicant communication, and inspector assignment."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Which permitting workflow to run. "
                            "permit_backlog: department-wide delays on applications ALREADY in "
                            "review — what is late, which resident will complain. Needs no "
                            "permit id. Do NOT use for anything newly arrived or at the counter. "
                            "intake_triage: THE FRONT COUNTER and the intake queue — use this "
                            "whenever the question is about what is arriving, what to accept or "
                            "reject today, or a newly submitted application. Covers whether to "
                            "accept it, duplicates, missing documents, WHICH REVIEW TEAMS it "
                            "routes to and when it is due back. Use this for any newly arrived "
                            "application named by street, applicant or project type. "
                            "applicant_updates: what to send applicants so they stop calling. "
                            "permit_status: one named permit's current state. "
                            "review_checklist: the plan-review checklist for a permit type. "
                            "inspector_assignment: which inspections are booked and who covers "
                            "them. "
                            "fee_calculation: permit fees for a valuation."
                        ),
                        "enum": [
                            "permit_backlog",
                            "intake_triage",
                            "applicant_updates",
                            "permit_status",
                            "review_checklist",
                            "inspector_assignment",
                            "fee_calculation",
                        ],
                    },
                    "permit_id": {"type": "string",
                                  "description": "Optional. Only needed for a single-permit view."},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "permit_backlog")
        dispatch = {
            "permit_backlog": self._permit_backlog,
            "intake_triage": self._intake_triage,
            "applicant_updates": self._applicant_updates,
            "permit_status": self._permit_status,
            "review_checklist": self._review_checklist,
            "inspector_assignment": self._inspector_assignment,
            "fee_calculation": self._fee_calculation,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _permit_backlog(self, **kwargs) -> str:
        """Department-wide aging view. Answers 'what is sitting too long'."""
        rows = [(pid, p) for pid, p in PERMIT_APPLICATIONS.items() if p["status"] != "approved"]
        rows.sort(key=lambda r: -_complaint_risk(r[1]))
        overdue = [r for r in rows if _sla_state(r[1])[0] == "overdue"]

        L = [f"# Permit Backlog — {TODAY.isoformat()}\n"]
        L.append(f"**{len(rows)} open applications · {len(overdue)} past the statutory clock**\n")
        L.append("| Permit | Applicant | Type | Age | SLA | State | Complaint risk |")
        L.append("|---|---|---|---|---|---|---|")
        for pid, p in rows:
            state, over = _sla_state(p)
            L.append(f"| {pid} | {p['applicant']} | {p['permit_type'].replace('_',' ')} | "
                     f"{_age_days(p)}d | {_sla_days(p)}d | {state.upper()}"
                     f"{f' (+{over}d)' if over > 0 else ''} | {_complaint_risk(p)}/100 |")

        if rows:
            pid, p = rows[0]
            state, over = _sla_state(p)
            L.append(f"\n## Who calls first\n")
            L.append(f"**{p['applicant']}** on {pid} — {p['property_address']}. "
                     f"{_age_days(p)} days in process against a {_sla_days(p)}-day clock"
                     f"{f', {over} days over' if over > 0 else ''}, "
                     f"{p['review_cycle']} correction cycle(s), currently "
                     f"{p['status'].replace('_',' ')}.")
            L.append(f"- Reviewer: {p['assigned_reviewer'] or 'unassigned'}")
            L.append(f"- Get ahead of it: send the cycle-{p['review_cycle']} correction list today "
                     f"and give a committed re-review date.")
        return "\n".join(L)

    def _intake_triage(self, **kwargs) -> str:
        """Classify and validate at intake, then route — one-pager bullets 1 and 2."""
        pid = kwargs.get("permit_id")
        queue = ([(pid.upper(), PERMIT_APPLICATIONS[pid.upper()])]
                 if pid and pid.upper() in PERMIT_APPLICATIONS
                 else [(k, v) for k, v in PERMIT_APPLICATIONS.items() if v["status"] == "intake"])
        if not queue:
            return "# Intake Triage\n\nNothing waiting at intake."

        L = [f"# Intake Triage — {len(queue)} application(s)\n"]
        for pid, p in queue:
            missing = _missing_documents(p)
            dup = _duplicate_of(pid, p)
            route = REVIEW_ROUTING.get(p["permit_type"], [])
            verdict = "REJECT — duplicate" if dup else ("HOLD — incomplete" if missing else "ACCEPT")
            L.append(f"## {pid} — {p['applicant']}\n")
            L.append(f"- **Classification:** {p['permit_type'].replace('_',' ')} · "
                     f"{p['zoning_district']} · ${p['valuation']:,} valuation")
            L.append(f"- **Verdict:** {verdict}")
            if dup:
                L.append(f"- **Duplicate of {dup}** — same parcel {p['parcel_id']} and applicant, "
                         f"already in {PERMIT_APPLICATIONS[dup]['status'].replace('_',' ')}. "
                         f"Close this one and point the applicant at {dup}.")
            if missing:
                L.append(f"- **Missing at intake:** {', '.join('`'+m+'`' for m in missing)} — "
                         f"the review clock does not start until these land.")
            if not dup and not missing:
                L.append(f"- **Routed to:** {' → '.join(route)}")
                L.append(f"- **Clock starts today**, {_sla_days(p)}-day statutory target "
                         f"(due {_d(_sla_days(p))}).")
            L.append("")
        return "\n".join(L)

    def _applicant_updates(self, **kwargs) -> str:
        """Proactive status notifications — the 'stop the status-check calls' bullet."""
        rows = [(pid, p) for pid, p in PERMIT_APPLICATIONS.items() if p["status"] != "approved"]
        rows.sort(key=lambda r: -_complaint_risk(r[1]))
        L = [f"# Applicant Updates Ready to Send — {len(rows)}\n"]
        for pid, p in rows:
            state, over = _sla_state(p)
            if p["status"] == "corrections_required":
                msg = (f"your application is in correction cycle {p['review_cycle']}; "
                       f"the outstanding items are with {p['assigned_reviewer']}")
            elif p["status"] == "intake":
                miss = _missing_documents(p)
                msg = (f"we need {', '.join(miss)} before the review clock can start"
                       if miss else "your application is complete and enters review today")
            elif p["status"] == "inspection_scheduled":
                nxt = INSPECTION_SCHEDULE.get(pid, [])
                msg = (f"your next inspection is {nxt[0]['type']} on {nxt[0]['date']} "
                       f"with {nxt[0]['inspector']}" if nxt else "inspections are being scheduled")
            else:
                msg = f"your application is in {p['status'].replace('_',' ')}"
            L.append(f"**{pid} → {p['applicant']}**")
            L.append(f"- {msg}.")
            L.append(f"- Day {_age_days(p)} of a {_sla_days(p)}-day target — "
                     f"{state}{f', {over} days over' if over > 0 else ''}.")
            L.append("")
        L.append(f"Sending these removes the reason for {len(rows)} status-check call(s).")
        return "\n".join(L)

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
