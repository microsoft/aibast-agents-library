"""
Deal Progression Agent

Tracks deal progression across the full pipeline, identifies stalled
opportunities using stage-velocity benchmarks, generates blocker-specific
action plans, and surfaces acceleration opportunities. Produces executive-
ready pipeline health reports with assigned tasks and accountability cadences.

Where a real deployment would call Salesforce, Gong, Clari, etc., this agent
uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/deal-progression",
    "version": "1.0.0",
    "display_name": "Deal Progression",
    "description": "Pipeline health analysis, stalled-deal detection, action plan generation, and pipeline acceleration.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "deal-progression", "pipeline", "forecasting"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# Stands in for Salesforce, Gong, Clari, etc.
# ═══════════════════════════════════════════════════════════════

# Stage benchmarks — average days a healthy deal spends in each stage
_STAGE_BENCHMARKS = {
    "Qualification":  14,
    "Discovery":      18,
    "Proposal":       16,
    "Negotiation":    12,
    "Contract":       10,
}

# Sales team with capacity data
_REPS = [
    {"name": "Mike Chen",    "title": "Sr. Account Executive",  "active_deals": 11, "capacity": 14, "specialty": "executive alignment"},
    {"name": "Lisa Torres",  "title": "Account Executive",      "active_deals": 9,  "capacity": 12, "specialty": "contract negotiation"},
    {"name": "James Park",   "title": "Sr. Account Executive",  "active_deals": 12, "capacity": 14, "specialty": "technical sales"},
    {"name": "Sarah Kim",    "title": "Account Executive",      "active_deals": 8,  "capacity": 12, "specialty": "executive alignment"},
    {"name": "Ryan Davis",   "title": "Account Executive",      "active_deals": 7,  "capacity": 12, "specialty": "mid-market"},
]

# Full pipeline — 47 opportunities
_PIPELINE = [
    # ── Stalled deals (12) ──────────────────────────────────────
    {"id": "OPP-001", "name": "TechCorp Industries",     "account": "TechCorp Industries",     "value": 890_000, "stage": "Proposal",     "days_in_stage": 34, "owner": "Mike Chen",    "last_contact_days": 18, "champion_name": "VP IT - Mark Reynolds",        "champion_status": "Silent",           "blocker": "executive_change"},
    {"id": "OPP-002", "name": "Global Manufacturing",    "account": "Global Manufacturing",    "value": 720_000, "stage": "Negotiation",  "days_in_stage": 28, "owner": "Lisa Torres",  "last_contact_days": 5,  "champion_name": "Dir. Ops - Rachel Green",      "champion_status": "Active frustrated", "blocker": "legal_review"},
    {"id": "OPP-003", "name": "Apex Financial",          "account": "Apex Financial Group",    "value": 580_000, "stage": "Discovery",    "days_in_stage": 25, "owner": "James Park",   "last_contact_days": 12, "champion_name": "CTO - David Liu",              "champion_status": "Disengaged",       "blocker": "competitor_eval"},
    {"id": "OPP-004", "name": "Metro Healthcare",        "account": "Metro Health Systems",    "value": 440_000, "stage": "Proposal",     "days_in_stage": 22, "owner": "Mike Chen",    "last_contact_days": 9,  "champion_name": "VP Digital - Sandra Patel",    "champion_status": "Active",           "blocker": "budget_hold"},
    {"id": "OPP-005", "name": "Pinnacle Logistics",      "account": "Pinnacle Logistics Inc.", "value": 360_000, "stage": "Qualification","days_in_stage": 20, "owner": "James Park",   "last_contact_days": 14, "champion_name": "IT Dir - Tom Bradley",         "champion_status": "Silent",           "blocker": "no_champion"},
    {"id": "OPP-006", "name": "Summit Retail Group",     "account": "Summit Retail Group",     "value": 310_000, "stage": "Discovery",    "days_in_stage": 24, "owner": "Sarah Kim",    "last_contact_days": 11, "champion_name": "COO - Angela Morris",          "champion_status": "Lukewarm",         "blocker": "competitor_eval"},
    {"id": "OPP-007", "name": "Vanguard Energy",         "account": "Vanguard Energy Corp",    "value": 270_000, "stage": "Proposal",     "days_in_stage": 21, "owner": "Ryan Davis",   "last_contact_days": 16, "champion_name": "VP Eng - Carlos Reyes",        "champion_status": "Silent",           "blocker": "executive_change"},
    {"id": "OPP-008", "name": "Cascade Media",           "account": "Cascade Media Holdings",  "value": 220_000, "stage": "Negotiation",  "days_in_stage": 18, "owner": "Lisa Torres",  "last_contact_days": 7,  "champion_name": "Dir. Tech - Nina Chow",        "champion_status": "Active",           "blocker": "legal_review"},
    {"id": "OPP-009", "name": "Atlas Construction",      "account": "Atlas Construction Co.",  "value": 180_000, "stage": "Qualification","days_in_stage": 19, "owner": "James Park",   "last_contact_days": 20, "champion_name": "None identified",              "champion_status": "None",             "blocker": "no_champion"},
    {"id": "OPP-010", "name": "Horizon Pharma",          "account": "Horizon Pharmaceuticals", "value": 150_000, "stage": "Discovery",    "days_in_stage": 22, "owner": "Sarah Kim",    "last_contact_days": 13, "champion_name": "VP R&D - Greg Foster",         "champion_status": "Disengaged",       "blocker": "budget_hold"},
    {"id": "OPP-011", "name": "Sterling Insurance",      "account": "Sterling Insurance Co.",  "value": 130_000, "stage": "Proposal",     "days_in_stage": 20, "owner": "Mike Chen",    "last_contact_days": 15, "champion_name": "CIO - Barbara Wells",          "champion_status": "Lukewarm",         "blocker": "competitor_eval"},
    {"id": "OPP-012", "name": "Redwood Education",       "account": "Redwood Education Group", "value": 110_000, "stage": "Qualification","days_in_stage": 18, "owner": "Ryan Davis",   "last_contact_days": 10, "champion_name": "Dir. IT - Paul Simmons",       "champion_status": "Active",           "blocker": "budget_hold"},

    # ── At-risk deals (7) ───────────────────────────────────────
    {"id": "OPP-013", "name": "Pacific Telecom",         "account": "Pacific Telecom Inc.",    "value": 780_000, "stage": "Negotiation",  "days_in_stage": 14, "owner": "Lisa Torres",  "last_contact_days": 3,  "champion_name": "SVP Ops - Diana Cruz",         "champion_status": "Active",           "blocker": "procurement_process"},
    {"id": "OPP-014", "name": "Northstar Aerospace",     "account": "Northstar Aerospace",     "value": 650_000, "stage": "Proposal",     "days_in_stage": 17, "owner": "Mike Chen",    "last_contact_days": 4,  "champion_name": "VP IT - Kyle Jensen",          "champion_status": "Active",           "blocker": "technical_validation"},
    {"id": "OPP-015", "name": "Beacon Financial",        "account": "Beacon Financial Corp",   "value": 520_000, "stage": "Discovery",    "days_in_stage": 19, "owner": "James Park",   "last_contact_days": 6,  "champion_name": "CTO - Amy Nakamura",           "champion_status": "Active",           "blocker": "stakeholder_alignment"},
    {"id": "OPP-016", "name": "Crestline Hotels",        "account": "Crestline Hospitality",   "value": 480_000, "stage": "Qualification","days_in_stage": 15, "owner": "Sarah Kim",    "last_contact_days": 5,  "champion_name": "Dir. Digital - Frank Russo",   "champion_status": "Active",           "blocker": "timeline_uncertainty"},
    {"id": "OPP-017", "name": "Ironbridge Steel",        "account": "Ironbridge Steel Corp",   "value": 410_000, "stage": "Proposal",     "days_in_stage": 17, "owner": "Ryan Davis",   "last_contact_days": 4,  "champion_name": "VP Mfg - Helen Park",          "champion_status": "Active",           "blocker": "stakeholder_alignment"},
    {"id": "OPP-018", "name": "Emerald Biotech",         "account": "Emerald Biotech Ltd.",    "value": 370_000, "stage": "Negotiation",  "days_in_stage": 13, "owner": "Lisa Torres",  "last_contact_days": 2,  "champion_name": "CIO - Roger Tran",             "champion_status": "Active",           "blocker": "procurement_process"},
    {"id": "OPP-019", "name": "Sapphire Analytics",      "account": "Sapphire Analytics Inc.", "value": 290_000, "stage": "Discovery",    "days_in_stage": 19, "owner": "James Park",   "last_contact_days": 7,  "champion_name": "VP Data - Megan Lowe",         "champion_status": "Active",           "blocker": "technical_validation"},

    # ── On-track deals (24) ─────────────────────────────────────
    {"id": "OPP-020", "name": "DataFlow Corp",           "account": "DataFlow Corp",           "value": 340_000, "stage": "Contract",     "days_in_stage": 3,  "owner": "Lisa Torres",  "last_contact_days": 1,  "champion_name": "VP Eng - Steve Hall",          "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-021", "name": "Summit Industries",       "account": "Summit Industries Inc.",  "value": 280_000, "stage": "Contract",     "days_in_stage": 5,  "owner": "Mike Chen",    "last_contact_days": 1,  "champion_name": "CTO - Laura Adams",            "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-022", "name": "Tech Dynamics",           "account": "Tech Dynamics LLC",       "value": 190_000, "stage": "Contract",     "days_in_stage": 2,  "owner": "Sarah Kim",    "last_contact_days": 0,  "champion_name": "IT Dir - Ben Wright",          "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-023", "name": "Orion Software",          "account": "Orion Software Inc.",     "value": 420_000, "stage": "Negotiation",  "days_in_stage": 5,  "owner": "James Park",   "last_contact_days": 1,  "champion_name": "VP Prod - Jill Carter",        "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-024", "name": "Vertex Solutions",        "account": "Vertex Solutions Corp",   "value": 380_000, "stage": "Proposal",     "days_in_stage": 8,  "owner": "Ryan Davis",   "last_contact_days": 2,  "champion_name": "CIO - Dan Mitchell",           "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-025", "name": "Phoenix Consulting",      "account": "Phoenix Consulting Grp",  "value": 310_000, "stage": "Discovery",    "days_in_stage": 10, "owner": "Mike Chen",    "last_contact_days": 3,  "champion_name": "CEO - Tina Brooks",            "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-026", "name": "Cirrus Cloud Services",   "account": "Cirrus Cloud Services",   "value": 540_000, "stage": "Proposal",     "days_in_stage": 7,  "owner": "Lisa Torres",  "last_contact_days": 2,  "champion_name": "VP Infra - Raj Patel",         "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-027", "name": "Quantum Analytics",       "account": "Quantum Analytics LLC",   "value": 290_000, "stage": "Discovery",    "days_in_stage": 9,  "owner": "Sarah Kim",    "last_contact_days": 4,  "champion_name": "CTO - Eric Saunders",          "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-028", "name": "Bluewave Telecom",        "account": "Bluewave Telecom Inc.",   "value": 460_000, "stage": "Negotiation",  "days_in_stage": 6,  "owner": "James Park",   "last_contact_days": 1,  "champion_name": "SVP Tech - Maria Gonzalez",    "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-029", "name": "Granite Capital",         "account": "Granite Capital Mgmt",    "value": 350_000, "stage": "Qualification","days_in_stage": 7,  "owner": "Mike Chen",    "last_contact_days": 3,  "champion_name": "Dir. IT - Jake Morton",        "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-030", "name": "Silverline Media",        "account": "Silverline Media Group",  "value": 230_000, "stage": "Proposal",     "days_in_stage": 6,  "owner": "Ryan Davis",   "last_contact_days": 2,  "champion_name": "VP Tech - Olivia Hart",        "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-031", "name": "Trident Manufacturing",   "account": "Trident Mfg Corp",        "value": 510_000, "stage": "Negotiation",  "days_in_stage": 4,  "owner": "Lisa Torres",  "last_contact_days": 1,  "champion_name": "COO - William Chen",           "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-032", "name": "Falcon Logistics",        "account": "Falcon Logistics Inc.",   "value": 270_000, "stage": "Discovery",    "days_in_stage": 11, "owner": "Sarah Kim",    "last_contact_days": 3,  "champion_name": "VP Ops - Christine Lee",       "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-033", "name": "Prism Technologies",      "account": "Prism Technologies LLC",  "value": 390_000, "stage": "Proposal",     "days_in_stage": 9,  "owner": "James Park",   "last_contact_days": 2,  "champion_name": "CTO - Derek Nash",             "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-034", "name": "Keystone Health",         "account": "Keystone Health Corp",    "value": 320_000, "stage": "Qualification","days_in_stage": 8,  "owner": "Mike Chen",    "last_contact_days": 4,  "champion_name": "VP Digital - Susan Park",      "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-035", "name": "Neptune Shipping",        "account": "Neptune Shipping Co.",    "value": 180_000, "stage": "Discovery",    "days_in_stage": 6,  "owner": "Ryan Davis",   "last_contact_days": 2,  "champion_name": "CIO - Alan Foster",            "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-036", "name": "Ember Software",          "account": "Ember Software Inc.",     "value": 450_000, "stage": "Proposal",     "days_in_stage": 5,  "owner": "Lisa Torres",  "last_contact_days": 1,  "champion_name": "VP Eng - Kevin Zhao",          "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-037", "name": "Ridgeline Capital",       "account": "Ridgeline Capital Grp",   "value": 260_000, "stage": "Negotiation",  "days_in_stage": 3,  "owner": "Sarah Kim",    "last_contact_days": 1,  "champion_name": "Dir. Tech - Nancy White",      "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-038", "name": "Aurora Aerospace",        "account": "Aurora Aerospace Ltd.",   "value": 530_000, "stage": "Discovery",    "days_in_stage": 8,  "owner": "James Park",   "last_contact_days": 3,  "champion_name": "SVP Eng - Robert Kim",         "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-039", "name": "Cobalt Chemicals",        "account": "Cobalt Chemical Corp",    "value": 200_000, "stage": "Qualification","days_in_stage": 5,  "owner": "Mike Chen",    "last_contact_days": 2,  "champion_name": "VP IT - Dorothy Mills",        "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-040", "name": "Zenith Insurance",        "account": "Zenith Insurance Group",  "value": 340_000, "stage": "Proposal",     "days_in_stage": 4,  "owner": "Ryan Davis",   "last_contact_days": 1,  "champion_name": "CTO - Philip Grant",           "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-041", "name": "Legacy Healthcare",       "account": "Legacy Health Systems",   "value": 280_000, "stage": "Negotiation",  "days_in_stage": 7,  "owner": "Lisa Torres",  "last_contact_days": 2,  "champion_name": "Dir. Digital - Kelly Young",   "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-042", "name": "Pinnacle Software",       "account": "Pinnacle Software Inc.",  "value": 410_000, "stage": "Discovery",    "days_in_stage": 7,  "owner": "Sarah Kim",    "last_contact_days": 3,  "champion_name": "VP Prod - Brian Hughes",       "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-043", "name": "Titan Energy",            "account": "Titan Energy Corp",       "value": 370_000, "stage": "Proposal",     "days_in_stage": 10, "owner": "James Park",   "last_contact_days": 2,  "champion_name": "CIO - Martha Clark",           "champion_status": "Active",           "blocker": "none"},

    # ── Closed Won (3) — for velocity reference ────────────────
    {"id": "OPP-044", "name": "Axiom Partners",          "account": "Axiom Partners LLC",      "value": 520_000, "stage": "Closed Won",   "days_in_stage": 0,  "owner": "Mike Chen",    "last_contact_days": 0,  "champion_name": "CEO - Janet Rivera",           "champion_status": "Won",              "blocker": "none"},
    {"id": "OPP-045", "name": "Delta Dynamics",          "account": "Delta Dynamics Corp",     "value": 310_000, "stage": "Closed Won",   "days_in_stage": 0,  "owner": "Lisa Torres",  "last_contact_days": 0,  "champion_name": "VP Ops - Scott Morgan",        "champion_status": "Won",              "blocker": "none"},
    {"id": "OPP-046", "name": "Vector Analytics",        "account": "Vector Analytics Inc.",   "value": 190_000, "stage": "Closed Won",   "days_in_stage": 0,  "owner": "Sarah Kim",    "last_contact_days": 0,  "champion_name": "CTO - Lisa Brown",             "champion_status": "Won",              "blocker": "none"},

    # ── Closed Lost (1) — for context ──────────────────────────
    {"id": "OPP-047", "name": "Omega Systems",           "account": "Omega Systems Inc.",      "value": 430_000, "stage": "Closed Lost",  "days_in_stage": 0,  "owner": "James Park",   "last_contact_days": 0,  "champion_name": "VP IT - Chris Taylor",         "champion_status": "Lost",             "blocker": "competitor_won"},
]

# Blocker-to-action mapping for action plan generation
_BLOCKER_PLAYBOOK = {
    "executive_change": {
        "diagnosis": "Champion disengaged, economic buyer changed",
        "week1": [
            "Day 1: Research new executive background (LinkedIn, news)",
            "Day 2: Call existing champion — acknowledge gap, request intro",
            "Day 3: Send executive-tailored ROI analysis",
            "Day 5: Executive sponsor outreach (your VP to their exec)",
        ],
        "week2": [
            "Schedule executive meeting with business case",
            "Re-present proposal with finance lens",
            "Establish new champion relationship",
        ],
        "resource": "exec alignment specialist",
    },
    "legal_review": {
        "diagnosis": "Process bottleneck, not relationship issue",
        "week1": [
            "Today: Call champion — acknowledge legal delay",
            "Tomorrow: Send pre-approved contract template (removes 80% of redlines)",
            "Day 3: Offer 30-day out clause to reduce perceived risk",
            "Day 5: Legal-to-legal call to resolve remaining items",
        ],
        "week2": [
            "Follow up on outstanding redline items",
            "Escalate any remaining blockers to VP Legal",
        ],
        "resource": "legal team fast-track review",
    },
    "competitor_eval": {
        "diagnosis": "Active competitive evaluation in progress",
        "week1": [
            "Day 1: Request competitive landscape details from champion",
            "Day 2: Prepare head-to-head comparison deck",
            "Day 3: Schedule technical deep-dive vs competitor capabilities",
            "Day 5: Deliver customer reference calls in same vertical",
        ],
        "week2": [
            "Provide proof-of-value pilot offer",
            "Executive peer reference call",
            "Submit best-and-final with differentiated terms",
        ],
        "resource": "competitive intelligence team",
    },
    "budget_hold": {
        "diagnosis": "Budget approval stalled or deprioritized",
        "week1": [
            "Day 1: Confirm budget timeline with champion",
            "Day 2: Build CFO-ready business case with 3-year TCO",
            "Day 3: Offer phased implementation to reduce upfront cost",
            "Day 5: Provide flexible payment terms proposal",
        ],
        "week2": [
            "Schedule CFO meeting with ROI walkthrough",
            "Share peer company case study with hard ROI numbers",
        ],
        "resource": "value engineering team",
    },
    "no_champion": {
        "diagnosis": "No internal champion identified or engaged",
        "week1": [
            "Day 1: Map org chart and identify 3 potential champions",
            "Day 2: Multi-thread outreach via LinkedIn and email",
            "Day 3: Offer executive briefing or lunch-and-learn",
            "Day 5: Ask existing contacts for warm introductions",
        ],
        "week2": [
            "Host on-site workshop to build relationships",
            "Provide industry insights to create value before selling",
            "Identify and cultivate power sponsor",
        ],
        "resource": "senior AE for relationship building",
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPERS — real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

_ACTIVE_STAGES = {"Qualification", "Discovery", "Proposal", "Negotiation", "Contract"}


def _active_pipeline():
    """Return only open, active-stage deals."""
    return [d for d in _PIPELINE if d["stage"] in _ACTIVE_STAGES]


def _classify_deals():
    """Classify every active deal as on_track, at_risk, or stalled."""
    on_track, at_risk, stalled = [], [], []
    for d in _active_pipeline():
        benchmark = _STAGE_BENCHMARKS.get(d["stage"], 14)
        ratio = d["days_in_stage"] / benchmark
        if ratio >= 1.25:
            stalled.append(d)
        elif ratio >= 1.0 or d["last_contact_days"] >= 10:
            at_risk.append(d)
        else:
            on_track.append(d)
    return on_track, at_risk, stalled


def _total_value(deals):
    """Sum opportunity values."""
    return sum(d["value"] for d in deals)


def _avg_days_stalled(deals):
    """Average days in stage beyond benchmark for a list of deals."""
    if not deals:
        return 0
    excess = []
    for d in deals:
        benchmark = _STAGE_BENCHMARKS.get(d["stage"], 14)
        excess.append(d["days_in_stage"] - benchmark)
    return round(sum(excess) / len(excess))


def _blocker_summary(stalled):
    """Group stalled deals by blocker type and count."""
    counts = {}
    for d in stalled:
        b = d["blocker"]
        label = {
            "executive_change": "Missing executive sponsor",
            "legal_review": "Legal / contract review",
            "competitor_eval": "Competitor evaluation ongoing",
            "budget_hold": "Budget approval pending",
            "no_champion": "No internal champion",
        }.get(b, b)
        counts[label] = counts.get(label, 0) + 1
    return counts


def _deals_by_owner(deals):
    """Group deals by rep name."""
    grouped = {}
    for d in deals:
        grouped.setdefault(d["owner"], []).append(d)
    return grouped


def _quick_wins():
    """Deals in Contract stage with recent contact — near close."""
    return [d for d in _active_pipeline()
            if d["stage"] == "Contract" and d["last_contact_days"] <= 3]


def _acceleration_opportunities():
    """Identify deals that can be pulled forward by intervention type."""
    active = _active_pipeline()
    exec_align = [d for d in active if d["stage"] in ("Proposal", "Negotiation")
                  and d["blocker"] in ("executive_change", "no_champion", "stakeholder_alignment", "none")
                  and d["days_in_stage"] >= 5]
    contract_fast = [d for d in active if d["blocker"] in ("legal_review", "procurement_process")
                     or d["stage"] == "Contract"]
    pov_offer = [d for d in active if d["blocker"] in ("competitor_eval", "technical_validation", "timeline_uncertainty")
                 or (d["stage"] == "Discovery" and d["days_in_stage"] >= 8)]
    return exec_align, contract_fast, pov_offer


def _rep_capacity():
    """Calculate rep capacity and stalled deal load."""
    _, _, stalled = _classify_deals()
    owner_stalled = _deals_by_owner(stalled)
    result = []
    for rep in _REPS:
        rep_stalled = owner_stalled.get(rep["name"], [])
        result.append({
            "name": rep["name"],
            "title": rep["title"],
            "active_deals": rep["active_deals"],
            "capacity": rep["capacity"],
            "available_slots": rep["capacity"] - rep["active_deals"],
            "stalled_count": len(rep_stalled),
            "stalled_value": _total_value(rep_stalled),
            "specialty": rep["specialty"],
        })
    return result


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class DealProgressionAgent(BasicAgent):
    """
    Tracks deal progression and accelerates pipeline velocity.

    Operations:
        pipeline_health    - full pipeline health with on-track / at-risk / stalled breakdown
        stalled_deals      - deep-dive into stalled deals with blocker analysis
        action_plans       - week-by-week action plans per stalled deal
        acceleration       - deals that can be pulled forward with targeted actions
        assign_tasks       - assign tasks to reps based on capacity
        executive_summary  - session summary with all findings and actions
    """

    def __init__(self):
        self.name = "DealProgressionAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "pipeline_health", "stalled_deals",
                            "action_plans", "acceleration",
                            "assign_tasks", "executive_summary",
                        ],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "pipeline_health")
        dispatch = {
            "pipeline_health": self._pipeline_health,
            "stalled_deals": self._stalled_deals,
            "action_plans": self._action_plans,
            "acceleration": self._acceleration,
            "assign_tasks": self._assign_tasks,
            "executive_summary": self._executive_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return json.dumps({"status": "error", "message": f"Unknown operation: {op}"})
        return handler()

    # ── pipeline_health ───────────────────────────────────────
    def _pipeline_health(self):
        on_track, at_risk, stalled = _classify_deals()
        active = _active_pipeline()
        total_value = _total_value(active)
        blockers = _blocker_summary(stalled)

        at_risk_avg = _avg_days_stalled(at_risk) if at_risk else 0
        stalled_avg = round(sum(d["days_in_stage"] for d in stalled) / max(len(stalled), 1))

        blocker_lines = "\n".join(f"- {count} deals: {label}" for label, count in
                                   sorted(blockers.items(), key=lambda x: -x[1]))

        return (
            f"**Pipeline Health Summary**\n\n"
            f"Analyzed **${total_value / 1_000_000:.1f}M** pipeline across **{len(active)}** active opportunities.\n\n"
            f"| Status | Deals | Value | Avg Days in Stage |\n"
            f"|--------|-------|-------|-------------------|\n"
            f"| On Track | {len(on_track)} | ${_total_value(on_track) / 1_000_000:.1f}M | within benchmark |\n"
            f"| At Risk | {len(at_risk)} | ${_total_value(at_risk) / 1_000_000:.1f}M | +{at_risk_avg} days over |\n"
            f"| Stalled | {len(stalled)} | ${_total_value(stalled) / 1_000_000:.1f}M | avg {stalled_avg} days |\n\n"
            f"**Critical Stalled Deals (top 4 by value):**\n\n"
            + "".join(
                f"{i}. **{d['name']}** — ${d['value']:,} — {d['days_in_stage']} days in {d['stage']}\n"
                for i, d in enumerate(sorted(stalled, key=lambda x: -x["value"])[:4], 1)
            )
            + f"\n**Root Cause Analysis:**\n{blocker_lines}\n\n"
            f"Source: [Salesforce + Activity Analytics]\n"
            f"Agents: PipelineAnalyticsAgent, StalledDealDetectionAgent"
        )

    # ── stalled_deals ─────────────────────────────────────────
    def _stalled_deals(self):
        _, _, stalled = _classify_deals()
        stalled_sorted = sorted(stalled, key=lambda x: -x["value"])

        sections = []
        for d in stalled_sorted:
            benchmark = _STAGE_BENCHMARKS.get(d["stage"], 14)
            multiplier = round(d["days_in_stage"] / benchmark, 1)
            playbook = _BLOCKER_PLAYBOOK.get(d["blocker"], {})
            diagnosis = playbook.get("diagnosis", d["blocker"].replace("_", " ").title())

            sections.append(
                f"**{d['name']} — ${d['value']:,}**\n\n"
                f"| Factor | Status |\n|--------|--------|\n"
                f"| Stage | {d['stage']} |\n"
                f"| Days stalled | {d['days_in_stage']} ({multiplier}x benchmark of {benchmark} days) |\n"
                f"| Last contact | {d['last_contact_days']} days ago |\n"
                f"| Champion | {d['champion_name']} ({d['champion_status']}) |\n"
                f"| Blocker | {d['blocker'].replace('_', ' ').title()} |\n\n"
                f"**Diagnosis:** {diagnosis}\n"
            )

        avg_velocity = 45  # benchmark close cycle
        return (
            f"**Stalled Deal Deep-Dive ({len(stalled)} deals, ${_total_value(stalled) / 1_000_000:.1f}M at risk)**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n**Velocity Comparison:** Average deal closes in {avg_velocity} days — "
            f"stalled deals average {round(sum(d['days_in_stage'] for d in stalled) / len(stalled))} days in current stage alone.\n\n"
            f"Source: [CRM + Email Analytics + Meeting Logs]\n"
            f"Agents: DealDiagnosticsAgent, StalledDealDetectionAgent"
        )

    # ── action_plans ──────────────────────────────────────────
    def _action_plans(self):
        _, _, stalled = _classify_deals()
        stalled_sorted = sorted(stalled, key=lambda x: -x["value"])

        plans = []
        for d in stalled_sorted:
            playbook = _BLOCKER_PLAYBOOK.get(d["blocker"])
            if not playbook:
                continue

            week1 = "\n".join(f"- {task}" for task in playbook["week1"])
            week2 = "\n".join(f"- {task}" for task in playbook["week2"])

            plans.append(
                f"**{d['name']} — ${d['value']:,} ({d['stage']})**\n\n"
                f"**Week 1:**\n{week1}\n\n"
                f"**Week 2:**\n{week2}\n\n"
                f"**Assigned Resource:** {playbook['resource'].title()}\n"
                f"**Owner:** {d['owner']}\n"
                f"**Expected Outcome:** Deal back on track within 10 days\n"
            )

        total_tasks = sum(
            len(_BLOCKER_PLAYBOOK.get(d["blocker"], {}).get("week1", []))
            + len(_BLOCKER_PLAYBOOK.get(d["blocker"], {}).get("week2", []))
            for d in stalled_sorted if d["blocker"] in _BLOCKER_PLAYBOOK
        )

        return (
            f"**Action Plans — {len(plans)} Stalled Deals**\n\n"
            f"Total tasks generated: **{total_tasks}**\n\n"
            + "\n---\n\n".join(plans)
            + f"\nSource: [Sales Playbook + Win Patterns]\n"
            f"Agents: NextBestActionAgent"
        )

    # ── acceleration ──────────────────────────────────────────
    def _acceleration(self):
        exec_align, contract_fast, pov_offer = _acceleration_opportunities()
        quick = _quick_wins()

        rows = (
            f"| Executive alignment | {len(exec_align)} | "
            f"${_total_value(exec_align) / 1_000_000:.1f}M | 12 days avg |\n"
            f"| Contract fast-track | {len(contract_fast)} | "
            f"${_total_value(contract_fast) / 1_000_000:.1f}M | 8 days avg |\n"
            f"| Proof-of-value offer | {len(pov_offer)} | "
            f"${_total_value(pov_offer) / 1_000_000:.1f}M | 15 days avg |\n"
        )

        quick_lines = "".join(
            f"- **{d['name']}:** ${d['value']:,} — "
            f"{'verbal commit, awaiting signature' if d['days_in_stage'] <= 3 else 'final approval pending'}\n"
            for d in sorted(quick, key=lambda x: -x["value"])
        )

        quick_total = _total_value(quick)
        combined_value = _total_value(exec_align) + _total_value(contract_fast) + _total_value(pov_offer)

        # Rep-level stalled summary
        _, _, stalled = _classify_deals()
        rep_stalled = _deals_by_owner(stalled)
        rep_rows = ""
        for rep in _REPS:
            rep_deals = rep_stalled.get(rep["name"], [])
            if rep_deals:
                top_blocker = max(
                    set(d["blocker"] for d in rep_deals),
                    key=lambda b: sum(1 for d in rep_deals if d["blocker"] == b),
                )
                action = {
                    "executive_change": "Executive introductions",
                    "legal_review": "Contract negotiations",
                    "competitor_eval": "Competitive positioning",
                    "budget_hold": "ROI business cases",
                    "no_champion": "Re-engagement campaign",
                }.get(top_blocker, "Deal acceleration")
                rep_rows += f"| {rep['name']} | {len(rep_deals)} | {action} |\n"

        return (
            f"**Pipeline Acceleration Strategy**\n\n"
            f"Identified **${combined_value / 1_000_000:.1f}M** that can be pulled forward "
            f"with targeted interventions.\n\n"
            f"**Acceleration Opportunities:**\n\n"
            f"| Action | Deals Impacted | Value | Days Saved |\n"
            f"|--------|----------------|-------|------------|\n"
            f"{rows}\n"
            f"**Quick Wins (Close This Week):**\n{quick_lines}\n"
            f"Quick-win total: **${quick_total / 1_000_000:.1f}M**\n\n"
            f"**Rep-Level Actions:**\n\n"
            f"| Rep | Stalled Deals | Priority Action |\n"
            f"|-----|---------------|----------------|\n"
            f"{rep_rows}\n"
            f"**Forecast Impact:** Accelerating these deals adds "
            f"**$2.4M** to Q4 commit.\n\n"
            f"Source: [Pipeline Analytics + Historical Patterns]\n"
            f"Agents: PipelineAccelerationAgent"
        )

    # ── assign_tasks ──────────────────────────────────────────
    def _assign_tasks(self):
        _, _, stalled = _classify_deals()
        rep_stalled = _deals_by_owner(stalled)
        caps = _rep_capacity()

        # Calculate tasks per rep based on their stalled deals and playbook
        assignments = []
        total_tasks = 0
        for rc in caps:
            rep_deals = rep_stalled.get(rc["name"], [])
            task_count = 0
            for d in rep_deals:
                pb = _BLOCKER_PLAYBOOK.get(d["blocker"], {})
                task_count += len(pb.get("week1", [])) + len(pb.get("week2", []))
            # Support reps get tasks from cross-assignment
            if task_count == 0 and rc["specialty"] == "executive alignment" and rc["available_slots"] > 2:
                task_count = 3  # exec support tasks
            total_tasks += task_count
            if task_count > 0:
                deadline = "This week" if rc["stalled_count"] <= 2 else f"Next {min(rc['stalled_count'] * 2, 7)} days"
                role_note = f"{rc['stalled_count']} stalled" if rc["stalled_count"] > 0 else "Exec support"
                assignments.append({
                    "name": rc["name"],
                    "tasks": task_count,
                    "deadline": deadline,
                    "deals": role_note,
                })

        table = "".join(
            f"| {a['name']} | {a['tasks']} tasks | {a['deadline']} | {a['deals']} |\n"
            for a in assignments
        )

        return (
            f"**Task Assignments Completed**\n\n"
            f"**{total_tasks}** tasks assigned across **{len(assignments)}** reps.\n\n"
            f"| Rep | Tasks | Deadline | Deals |\n"
            f"|-----|-------|----------|-------|\n"
            f"{table}\n"
            f"**Automated Monitoring:**\n"
            f"- Daily Slack alerts for overdue tasks\n"
            f"- Deal stage change notifications\n"
            f"- Weekly pipeline velocity report\n"
            f"- Stall warning at 7 days (vs current 21)\n\n"
            f"**Accountability Cadence:**\n"
            f"- Daily: Automated task reminders\n"
            f"- Wednesday: Pipeline review meeting (30 min)\n"
            f"- Friday: Deal progression scorecard\n\n"
            f"**Success Metrics:**\n"
            f"- Target: Reduce avg stall time from 21 to 10 days\n"
            f"- Goal: Move ${_total_value(stalled) / 1_000_000:.1f}M stalled back to active\n"
            f"- Forecast: Add $2.4M to Q4 commit\n\n"
            f"Source: [Salesforce + Task Management]\n"
            f"Agents: TaskAssignmentAgent"
        )

    # ── executive_summary ─────────────────────────────────────
    def _executive_summary(self):
        on_track, at_risk, stalled = _classify_deals()
        active = _active_pipeline()
        total_val = _total_value(active)
        stalled_val = _total_value(stalled)
        quick = _quick_wins()
        quick_val = _total_value(quick)
        blockers = _blocker_summary(stalled)

        # Count total tasks
        total_tasks = 0
        for d in stalled:
            pb = _BLOCKER_PLAYBOOK.get(d["blocker"], {})
            total_tasks += len(pb.get("week1", [])) + len(pb.get("week2", []))

        blocker_labels = ", ".join(
            label.lower() for label, _ in sorted(blockers.items(), key=lambda x: -x[1])[:3]
        )

        top_stalled = sorted(stalled, key=lambda x: -x["value"])[:2]
        immediate_lines = ""
        if quick:
            immediate_lines += f"- ${quick_val / 1_000:,.0f}K in quick wins closing this week\n"
        for d in top_stalled:
            immediate_lines += f"- {d['name']} (${d['value']:,}) action plan activated\n"
        immediate_lines += f"- All {len(stalled)} stalled deals have intervention plans\n"

        on_track_pct = round(len(on_track) / max(len(active), 1) * 100)
        target_pct = min(on_track_pct + 18, 95)

        return (
            f"**Pipeline Acceleration Program — Executive Summary**\n\n"
            f"| Analysis | Result |\n"
            f"|----------|--------|\n"
            f"| Pipeline analyzed | ${total_val / 1_000_000:.1f}M across {len(active)} deals |\n"
            f"| Stalled identified | {len(stalled)} deals, ${stalled_val / 1_000_000:.1f}M at risk |\n"
            f"| Root causes | {blocker_labels} |\n"
            f"| Actions created | {total_tasks} specific tasks assigned |\n"
            f"| Acceleration target | ${(_total_value(stalled) + _total_value(at_risk)) / 1_000_000:.1f}M can be pulled forward |\n\n"
            f"**Immediate Impact:**\n{immediate_lines}\n"
            f"**Process Improvements:**\n"
            f"- Early warning at 7 days (was 21)\n"
            f"- Daily automated task tracking\n"
            f"- Weekly velocity reviews scheduled\n"
            f"- Rep accountability scorecard active\n\n"
            f"**Expected Outcomes:**\n"
            f"- Reduce stall time: 21 days to 10 days\n"
            f"- Q4 forecast improvement: +$2.4M commit\n"
            f"- Pipeline health: {target_pct}% on-track (from {on_track_pct}%)\n\n"
            f"Source: [All Pipeline Systems]\n"
            f"Agents: PipelineReportAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = DealProgressionAgent()
    for op in ["pipeline_health", "stalled_deals", "action_plans",
               "acceleration", "assign_tasks", "executive_summary"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
