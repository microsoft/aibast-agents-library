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
    "display_name": "Deal Progression Agent",
    "description": "Automate sales pipeline management to keep deals moving, increase forecast confidence, and improve team productivity.",
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
    {"id": "OPP-001", "name": "TechCorp Industries",     "account": "TechCorp Industries",     "value": 890_000, "stage": "Proposal",     "days_in_stage": 34, "owner": "Mike Chen",    "last_contact_days": 18, "champion_name": "VP IT - Mark Reynolds",        "champion_status": "Silent",           "blocker": "executive_change", "root_cause": "missing_exec_sponsor"},
    {"id": "OPP-002", "name": "Global Manufacturing",    "account": "Global Manufacturing",    "value": 720_000, "stage": "Negotiation",  "days_in_stage": 28, "owner": "Lisa Torres",  "last_contact_days": 5,  "champion_name": "Dir. Ops - Rachel Green",      "champion_status": "Active frustrated", "blocker": "legal_review", "root_cause": "missing_exec_sponsor"},
    {"id": "OPP-003", "name": "Apex Financial",          "account": "Apex Financial Group",    "value": 580_000, "stage": "Discovery",    "days_in_stage": 25, "owner": "James Park",   "last_contact_days": 12, "champion_name": "CTO - David Liu",              "champion_status": "Disengaged",       "blocker": "competitor_eval", "root_cause": "competitor_eval"},
    {"id": "OPP-004", "name": "Metro Healthcare",        "account": "Metro Health Systems",    "value": 400_000, "stage": "Proposal",     "days_in_stage": 22, "owner": "Mike Chen",    "last_contact_days": 9,  "champion_name": "VP Digital - Sandra Patel",    "champion_status": "Active",           "blocker": "budget_hold", "root_cause": "budget_pending"},
    {"id": "OPP-005", "name": "Pinnacle Logistics",      "account": "Pinnacle Logistics Inc.", "value": 320_000, "stage": "Qualification","days_in_stage": 20, "owner": "James Park",   "last_contact_days": 14, "champion_name": "IT Dir - Tom Bradley",         "champion_status": "Silent",           "blocker": "no_champion", "root_cause": "missing_exec_sponsor"},
    {"id": "OPP-006", "name": "Summit Retail Group",     "account": "Summit Retail Group",     "value": 270_000, "stage": "Discovery",    "days_in_stage": 24, "owner": "Sarah Kim",    "last_contact_days": 11, "champion_name": "COO - Angela Morris",          "champion_status": "Lukewarm",         "blocker": "competitor_eval", "root_cause": "competitor_eval"},
    {"id": "OPP-007", "name": "Vanguard Energy",         "account": "Vanguard Energy Corp",    "value": 230_000, "stage": "Proposal",     "days_in_stage": 21, "owner": "Ryan Davis",   "last_contact_days": 16, "champion_name": "VP Eng - Carlos Reyes",        "champion_status": "Silent",           "blocker": "executive_change", "root_cause": "missing_exec_sponsor"},
    {"id": "OPP-008", "name": "Cascade Media",           "account": "Cascade Media Holdings",  "value": 250_000, "stage": "Negotiation",  "days_in_stage": 18, "owner": "Lisa Torres",  "last_contact_days": 7,  "champion_name": "Dir. Tech - Nina Chow",        "champion_status": "Active",           "blocker": "legal_review", "root_cause": "competitor_eval"},
    {"id": "OPP-009", "name": "Atlas Construction",      "account": "Atlas Construction Co.",  "value": 180_000, "stage": "Qualification","days_in_stage": 19, "owner": "James Park",   "last_contact_days": 20, "champion_name": "None identified",              "champion_status": "None",             "blocker": "no_champion", "root_cause": "missing_exec_sponsor"},
    {"id": "OPP-010", "name": "Horizon Pharma",          "account": "Horizon Pharmaceuticals", "value": 150_000, "stage": "Discovery",    "days_in_stage": 24, "owner": "Sarah Kim",    "last_contact_days": 13, "champion_name": "VP R&D - Greg Foster",         "champion_status": "Disengaged",       "blocker": "budget_hold", "root_cause": "budget_pending"},
    {"id": "OPP-011", "name": "Sterling Insurance",      "account": "Sterling Insurance Co.",  "value": 130_000, "stage": "Proposal",     "days_in_stage": 20, "owner": "Mike Chen",    "last_contact_days": 15, "champion_name": "CIO - Barbara Wells",          "champion_status": "Lukewarm",         "blocker": "competitor_eval", "root_cause": "competitor_eval"},
    {"id": "OPP-012", "name": "Redwood Education",       "account": "Redwood Education Group", "value": 80_000, "stage": "Qualification","days_in_stage": 18, "owner": "Ryan Davis",   "last_contact_days": 10, "champion_name": "Dir. IT - Paul Simmons",       "champion_status": "Active",           "blocker": "budget_hold", "root_cause": "budget_pending"},

    # ── At-risk deals (7) ───────────────────────────────────────
    {"id": "OPP-013", "name": "Pacific Telecom",         "account": "Pacific Telecom Inc.",    "value": 1_080_000, "stage": "Negotiation",  "days_in_stage": 14, "owner": "Lisa Torres",  "last_contact_days": 3,  "champion_name": "SVP Ops - Diana Cruz",         "champion_status": "Active",           "blocker": "procurement_process"},
    {"id": "OPP-014", "name": "Northstar Aerospace",     "account": "Northstar Aerospace",     "value": 750_000, "stage": "Proposal",     "days_in_stage": 17, "owner": "Mike Chen",    "last_contact_days": 4,  "champion_name": "VP IT - Kyle Jensen",          "champion_status": "Active",           "blocker": "technical_validation"},
    {"id": "OPP-015", "name": "Beacon Financial",        "account": "Beacon Financial Corp",   "value": 690_000, "stage": "Discovery",    "days_in_stage": 19, "owner": "James Park",   "last_contact_days": 6,  "champion_name": "CTO - Amy Nakamura",           "champion_status": "Active",           "blocker": "stakeholder_alignment"},
    {"id": "OPP-016", "name": "Crestline Hotels",        "account": "Crestline Hospitality",   "value": 480_000, "stage": "Qualification","days_in_stage": 15, "owner": "Sarah Kim",    "last_contact_days": 5,  "champion_name": "Dir. Digital - Frank Russo",   "champion_status": "Active",           "blocker": "timeline_uncertainty"},
    {"id": "OPP-017", "name": "Ironbridge Steel",        "account": "Ironbridge Steel Corp",   "value": 410_000, "stage": "Proposal",     "days_in_stage": 17, "owner": "Ryan Davis",   "last_contact_days": 4,  "champion_name": "VP Mfg - Helen Park",          "champion_status": "Active",           "blocker": "stakeholder_alignment"},
    {"id": "OPP-018", "name": "Emerald Biotech",         "account": "Emerald Biotech Ltd.",    "value": 370_000, "stage": "Negotiation",  "days_in_stage": 13, "owner": "Lisa Torres",  "last_contact_days": 2,  "champion_name": "CIO - Roger Tran",             "champion_status": "Active",           "blocker": "procurement_process"},
    {"id": "OPP-019", "name": "Sapphire Analytics",      "account": "Sapphire Analytics Inc.", "value": 220_000, "stage": "Discovery",    "days_in_stage": 19, "owner": "James Park",   "last_contact_days": 7,  "champion_name": "VP Data - Megan Lowe",         "champion_status": "Active",           "blocker": "technical_validation"},

    # ── On-track deals (28) ─────────────────────────────────────
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

    {"id": "OPP-044", "name": "Axiom Partners",          "account": "Axiom Partners LLC",      "value": 520_000, "stage": "Proposal",     "days_in_stage": 6,  "owner": "Mike Chen",    "last_contact_days": 2,  "champion_name": "CEO - Janet Rivera",           "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-045", "name": "Delta Dynamics",          "account": "Delta Dynamics Corp",     "value": 310_000, "stage": "Negotiation",  "days_in_stage": 4,  "owner": "Lisa Torres",  "last_contact_days": 1,  "champion_name": "VP Ops - Scott Morgan",        "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-046", "name": "Vector Analytics",        "account": "Vector Analytics Inc.",   "value": 190_000, "stage": "Discovery",    "days_in_stage": 7,  "owner": "Sarah Kim",    "last_contact_days": 3,  "champion_name": "CTO - Lisa Brown",             "champion_status": "Active",           "blocker": "none"},
    {"id": "OPP-047", "name": "Omega Systems",           "account": "Omega Systems Inc.",      "value": 480_000, "stage": "Qualification","days_in_stage": 6,  "owner": "James Park",   "last_contact_days": 2,  "champion_name": "VP IT - Chris Taylor",         "champion_status": "Active",           "blocker": "none"},
]

# Deal-level evidence for the top stalled deals (the demo's deep dive and action plans).
_DEAL_DETAIL = {
    "OPP-001": {
        "deal_age_days": 96,
        "diagnosis": "Champion went silent 18 days ago, new CFO reviewing all purchases",
        "recommendation": "Re-engage via different stakeholder, prepare CFO business case",
        "plan_steps": ["Research CFO", "Call VP IT for intro", "Send CFO ROI analysis", "VP-to-CFO outreach"],
        "assigned": "Sarah Kim (TechCorp exec alignment)",
    },
    "OPP-002": {
        "deal_age_days": 88,
        "diagnosis": "Champion active but legal review blocking contract",
        "recommendation": "Offer pre-approved template, escalate with legal concession",
        "plan_steps": ["Call champion", "Send pre-approved template", "Offer 30-day out clause", "Legal-to-legal call"],
        "assigned": "Legal fast-track (Global)",
    },
}

# Acceleration levers: which open deals each lever can pull forward, and the days it saves.
_ACCELERATION = [
    {"action": "Exec alignment", "days_saved": 12,
     "deals": ["OPP-001", "OPP-015", "OPP-016", "OPP-017", "OPP-005", "OPP-007", "OPP-009"]},
    {"action": "Contract fast-track", "days_saved": 8, "deals": ["OPP-002", "OPP-013"]},
    {"action": "Proof-of-value", "days_saved": 15, "deals": ["OPP-003", "OPP-014", "OPP-019", "OPP-008"]},
]

_SHORT_NAMES = {"OPP-001": "TechCorp", "OPP-002": "Global Mfg", "OPP-003": "Apex Financial",
                "OPP-020": "DataFlow", "OPP-021": "Summit", "OPP-022": "Tech Dynamics"}

# Deal selections a request can name ("details on TechCorp and Global Manufacturing").
_DEAL_SETS = {
    "TechCorp and Global Manufacturing": ["OPP-001", "OPP-002"],
    "TechCorp": ["OPP-001"],
    "Global Manufacturing": ["OPP-002"],
    "Apex Financial": ["OPP-003"],
    "all": ["OPP-001", "OPP-002", "OPP-003", "OPP-004", "OPP-005", "OPP-006",
            "OPP-007", "OPP-008", "OPP-009", "OPP-010", "OPP-011", "OPP-012"],
}

_QUICK_WIN_NOTES = {"OPP-020": "awaiting sig", "OPP-021": "Friday approval", "OPP-022": "in DocuSign"}

# Draft task plan for manager review (18 rep tasks + 3 exec-alignment tasks = 21 actions).
_TASK_PLAN = [
    {"rep": "Mike Chen", "tasks": 6, "deadline": "This week", "focus": "TechCorp re-engagement and exec introductions"},
    {"rep": "Lisa Torres", "tasks": 4, "deadline": "5 days", "focus": "Global Manufacturing contract fast-track"},
    {"rep": "James Park", "tasks": 8, "deadline": "7 days", "focus": "Apex Financial proof-of-value and competitive positioning"},
    {"rep": "Sarah Kim", "tasks": 3, "deadline": "10 days", "focus": "TechCorp exec alignment (CFO business case)"},
]

_TARGETS = {
    "avg_close_days": 45,
    "stall_days_now": 21,
    "stall_days_target": 10,
    "stall_warning_days": 7,
    "q4_commit_add": 2_400_000,
    "health_target_pct": 78,
    "recovery_days": 10,
}

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
            "Tomorrow: Prepare the synthetic contract template for authorized legal and seller review",
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
        b = d.get("root_cause", d["blocker"])
        label = {
            "missing_exec_sponsor": "missing exec sponsor",
            "competitor_eval": "competitor eval",
            "budget_pending": "budget pending",
        }.get(b, b.replace("_", " "))
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


def _deal(deal_id):
    """The pipeline record with this id, or None."""
    for d in _PIPELINE:
        if d["id"] == deal_id:
            return d
    return None


def _acceleration_opportunities():
    """Deals each acceleration lever can pull forward (exec alignment, contract fast-track, proof-of-value)."""
    groups = []
    for lever in _ACCELERATION:
        groups.append([_deal(i) for i in lever["deals"]])
    return groups[0], groups[1], groups[2]


def _short(d):
    """Display name used in summaries ('Global Mfg')."""
    return _SHORT_NAMES.get(d["id"], d["name"].split()[0])


def _select_deals(deals, query):
    """Stalled deals for a named selection (see _DEAL_SETS); the top two by value when empty; none when unknown."""
    ranked = sorted(deals, key=lambda x: -x["value"])
    if not query:
        return ranked[:2]
    wanted = _DEAL_SETS.get(query, [])
    return [d for d in ranked if d["id"] in wanted]


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
            "description": (
                f"{__manifest__['description']} Uses only the bundled synthetic pipeline "
                "dataset and returns read-only analysis or draft plans; it never writes CRM "
                "records, assigns tasks, sends alerts, or changes a forecast. Route requests "
                "to compare timing options, pull-forward opportunities, quick wins, or "
                "acceleration scenarios to `acceleration`; that operation returns "
                "`Pipeline Acceleration Strategy` and `Synthetic Scenario`. Demo path: 'which deals are "
                "stalled ... what actions will move them forward' -> pipeline_health; 'details on TechCorp "
                "and Global Manufacturing' -> stalled_deals with deals; 'create action plans' -> "
                "action_plans; 'accelerate the entire pipeline' -> acceleration; 'assign tasks and set up "
                "tracking' -> assign_tasks; 'summarize everything' -> executive_summary. Call it first; "
                "every operation has demo defaults."
            ),
            "operations": [
                "pipeline_health", "stalled_deals", "action_plans", "acceleration",
                "assign_tasks", "executive_summary",
            ],
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
                        "description": (
                            "Select the requested pipeline deliverable. pipeline_health: the FIRST call for "
                            "'show me which deals are stalled in my pipeline and what actions will move them "
                            "forward' - status table, top stalled deals and root causes. stalled_deals: which deals "
                            "have genuinely stalled and the blocker evidence, or details on named deals ('details "
                            "on TechCorp and Global Manufacturing'; pass deals). "
                            "action_plans: only when asked to create action plans / next steps. acceleration: "
                            "'accelerate the entire pipeline' or how to accelerate; also REQUIRED for "
                            "timing options, pull-forward opportunities, quick wins, acceleration "
                            "strategies, or scenario value without forecast commitment; returns Pipeline "
                            "Acceleration Strategy and Synthetic Scenario. assign_tasks: candidate task "
                            "mapping for manager review. executive_summary: compiled leadership summary."
                        ),
                    },
                    "deals": {
                        "type": "string",
                        "enum": ["TechCorp and Global Manufacturing", "TechCorp", "Global Manufacturing", "Apex Financial", "all"],
                        "description": "stalled_deals / action_plans only: which stalled deals to cover. Use 'TechCorp and Global Manufacturing' when both are named; 'all' for every stalled deal. Omit for the top two.",
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
        op = kwargs.get("operation") or "pipeline_health"
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
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
        if op in ("stalled_deals", "action_plans"):
            output = handler(kwargs.get("deals"))
        else:
            output = handler()
        return (
            output.replace("Source: [", "Synthetic source model: [")
            + "\n\n**Evidence boundary:** Exact names, dates, counts, values, scores, "
            "percentages, and projections are synthetic planning evidence. This read-only "
            "output did not write CRM data, assign tasks, send alerts, approve pricing, "
            "change a forecast, or contact a customer."
        )

    # ── pipeline_health ───────────────────────────────────────
    def _pipeline_health(self):
        on_track, at_risk, stalled = _classify_deals()
        active = _active_pipeline()
        total_value = _total_value(active)
        blockers = _blocker_summary(stalled)
        top = sorted(stalled, key=lambda x: -x["value"])[:3]
        top_text = ", ".join(
            f"{_short(d)} (${d['value'] // 1000}K, {d['days_in_stage']} days)" for d in top
        )
        causes = ", ".join(
            f"{count} {label}" for label, count in sorted(blockers.items(), key=lambda x: -x[1])
        )
        return (
            f"**Pipeline Health Summary**\n\n"
            f"Analyzed **${total_value / 1_000_000:.0f}M** pipeline ({len(active)} deals) - "
            f"**{len(stalled)} deals stalled** (${_total_value(stalled) / 1_000_000:.1f}M at risk)\n\n"
            f"| Status | Deals | Value |\n"
            f"|--------|-------|-------|\n"
            f"| On Track | {len(on_track)} | ${_total_value(on_track) / 1_000_000:.1f}M |\n"
            f"| At Risk | {len(at_risk)} | ${_total_value(at_risk) / 1_000_000:.1f}M |\n"
            f"| Stalled | {len(stalled)} | ${_total_value(stalled) / 1_000_000:.1f}M |\n\n"
            f"**Top Stalled:** {top_text}\n\n"
            f"**Root Causes:** {causes}\n\n"
            f"Source: [Salesforce + Activity Analytics]\n\n"
            f"**Next step:** Want details on the top stalled deals?"
        )

    # ── stalled_deals ─────────────────────────────────────────
    def _stalled_deals(self, deals=None):
        _, _, stalled = _classify_deals()
        selected = _select_deals(stalled, deals)
        if not selected:
            return (
                f"**Stalled Deal Deep-Dive**\n\nNo stalled synthetic deal matches '{deals}'. Stalled deals: "
                + ", ".join(d["name"] for d in sorted(stalled, key=lambda x: -x["value"])) + "."
            )
        sections = []
        for d in selected:
            benchmark = _STAGE_BENCHMARKS.get(d["stage"], 14)
            multiplier = round(d["days_in_stage"] / benchmark, 1)
            detail = _DEAL_DETAIL.get(d["id"], {})
            playbook = _BLOCKER_PLAYBOOK.get(d["blocker"], {})
            diagnosis = detail.get("diagnosis") or playbook.get("diagnosis", d["blocker"].replace("_", " ").title())
            rec = detail.get("recommendation")
            age_row = f"| Deal age | {detail['deal_age_days']} days |\n" if detail.get("deal_age_days") else ""
            sections.append(
                f"**{d['name']} (${d['value'] // 1000}K):** {diagnosis}"
                + (f" -> {rec}" if rec else "") + "\n\n"
                f"| Factor | Status |\n|--------|--------|\n"
                f"| Stage | {d['stage']} |\n"
                f"| Days stalled | {d['days_in_stage']} ({multiplier}x benchmark of {benchmark} days) |\n"
                + age_row
                + f"| Last contact | {d['last_contact_days']} days ago |\n"
                f"| Champion | {d['champion_name']} ({d['champion_status']}) |\n"
                f"| Blocker | {d['blocker'].replace('_', ' ').title()} |\n\n"
                f"**Diagnosis:** {diagnosis}\n"
            )
        aged = [d for d in selected
                if _DEAL_DETAIL.get(d["id"], {}).get("deal_age_days", 0) > _TARGETS["avg_close_days"]]
        if len(aged) == 2:
            close_line = f"Both significantly over your {_TARGETS['avg_close_days']}-day avg close time."
        elif aged:
            close_line = f"{len(aged)} deals significantly over your {_TARGETS['avg_close_days']}-day avg close time."
        else:
            close_line = f"Average deal closes in {_TARGETS['avg_close_days']} days."
        return (
            f"**Stalled Deal Deep-Dive ({len(selected)} of {len(stalled)} stalled deals, "
            f"${_total_value(stalled) / 1_000_000:.1f}M at risk overall)**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n**Velocity Comparison:** {close_line}\n\n"
            f"Source: [CRM + Email Analytics + Meeting Logs]\n\n"
            f"**Next step:** Generate action plans?"
        )

    # ── action_plans ──────────────────────────────────────────
    def _action_plans(self, deals=None):
        _, _, stalled = _classify_deals()
        selected = _select_deals(stalled, deals)
        plans, summary, assigned = [], [], []
        for d in selected:
            detail = _DEAL_DETAIL.get(d["id"], {})
            playbook = _BLOCKER_PLAYBOOK.get(d["blocker"], {})
            steps = detail.get("plan_steps") or [t.split(": ", 1)[-1] for t in playbook.get("week1", [])]
            if not steps:
                continue
            summary.append(f"- **{_short(d)}:** " + " -> ".join(steps))
            if detail.get("assigned"):
                assigned.append(detail["assigned"])
            week2 = "\n".join(f"- {task}" for task in playbook.get("week2", []))
            resource = detail.get("assigned") or playbook.get("resource", "deal owner").title()
            plans.append(
                f"**{d['name']} — ${d['value']:,} ({d['stage']})**\n\n"
                f"**Next steps:**\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(steps, 1)) + "\n\n"
                + (f"**Week 2:**\n{week2}\n\n" if week2 else "")
                + f"**Suggested Resource:** {resource}\n"
                f"**Owner:** {d['owner']}\n"
                f"**Planning Objective:** Evaluate whether the deal can return to active review within "
                f"{_TARGETS['recovery_days']} days\n"
            )
        who = "Both" if len(plans) == 2 else "All"
        return (
            f"**Action Plans — {len(plans)} Stalled Deals (drafts for your review)**\n\n"
            + "\n".join(summary) + "\n\n"
            + (f"**Suggested owners:** {', '.join(assigned)}\n" if assigned else "")
            + f"**Target:** {who} back on track within {_TARGETS['recovery_days']} days\n\n---\n\n"
            + "\n---\n\n".join(plans)
            + f"\nSource: [Sales Playbook + Win Patterns]\n\n"
            f"**Next step:** See the full pipeline acceleration plan?"
        )

    # ── acceleration ──────────────────────────────────────────
    def _acceleration(self):
        groups = _acceleration_opportunities()
        quick = _quick_wins()
        rows = ""
        combined_value = 0
        for lever, group in zip(_ACCELERATION, groups):
            value = _total_value(group)
            combined_value += value
            rows += f"| {lever['action']} | {len(group)} | ${value / 1_000_000:.1f}M | {lever['days_saved']} days |\n"
        quick_sorted = sorted(quick, key=lambda x: -x["value"])
        quick_text = ", ".join(
            f"{_short(d)} ${d['value'] // 1000}K ({_QUICK_WIN_NOTES.get(d['id'], 'final approval pending')})"
            for d in quick_sorted
        )
        quick_total = _total_value(quick)

        _, _, stalled = _classify_deals()
        rep_stalled = _deals_by_owner(stalled)
        rep_rows = ""
        for rep in _REPS:
            rep_deals = rep_stalled.get(rep["name"], [])
            if rep_deals:
                top_blocker = max(
                    sorted(set(d["blocker"] for d in rep_deals)),
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
            f"**${combined_value / 1_000_000:.1f}M** can be accelerated with targeted actions:\n\n"
            f"| Action | Deals Impacted | Value | Days Saved |\n"
            f"|--------|----------------|-------|------------|\n"
            f"{rows}\n"
            f"**Quick Wins This Week:** {quick_text} (total ${quick_total // 1000}K)\n\n"
            f"**Forecast Impact:** +${_TARGETS['q4_commit_add'] / 1_000_000:.1f}M to Q4 commit\n\n"
            f"**Rep-Level Actions:**\n\n"
            f"| Rep | Stalled Deals | Priority Action |\n"
            f"|-----|---------------|----------------|\n"
            f"{rep_rows}\n"
            f"**Synthetic Scenario:** The +${_TARGETS['q4_commit_add'] / 1_000_000:.1f}M Q4 figure is planning "
            f"evidence for your review; it is not a forecast commitment.\n\n"
            f"Source: [Pipeline Analytics + Historical Patterns]\n\n"
            f"**Next step:** Assign tasks to the team?"
        )

    # ── assign_tasks ──────────────────────────────────────────
    def _assign_tasks(self):
        _, _, stalled = _classify_deals()
        total_tasks = sum(t["tasks"] for t in _TASK_PLAN)
        table = "".join(
            f"| {t['rep']} | {t['tasks']} | {t['deadline']} | {t['focus']} |\n" for t in _TASK_PLAN
        )
        return (
            f"**Draft Task Assignment Plan**\n\n"
            f"**{total_tasks}** candidate tasks mapped across **{len(_TASK_PLAN)}** reps, ready for you to assign.\n\n"
            f"| Rep | Tasks | Deadline | Focus |\n"
            f"|-----|-------|----------|-------|\n"
            f"{table}\n"
            f"**Proposed Tracking (ready for you to turn on):**\n"
            f"- Daily alerts in Microsoft Teams for overdue tasks\n"
            f"- Stage change notifications\n"
            f"- {_TARGETS['stall_warning_days']}-day stall warning (vs {_TARGETS['stall_days_now']})\n\n"
            f"**Targets:** Reduce stall time to {_TARGETS['stall_days_target']} days, move "
            f"${_total_value(stalled) / 1_000_000:.1f}M back to active, "
            f"+${_TARGETS['q4_commit_add'] / 1_000_000:.1f}M Q4 commit\n\n"
            f"Source: [Salesforce + Task Management]\n\n"
            f"**Next step:** Generate summary?"
        )

    # ── executive_summary ─────────────────────────────────────
    def _executive_summary(self):
        on_track, at_risk, stalled = _classify_deals()
        active = _active_pipeline()
        quick_val = _total_value(_quick_wins())
        total_tasks = sum(t["tasks"] for t in _TASK_PLAN)
        accel = sum(_total_value(g) for g in _acceleration_opportunities())
        on_track_pct = round(len(on_track) / max(len(active), 1) * 100)
        return (
            f"**Pipeline Acceleration Program — Executive Summary**\n\n"
            f"| Result | Value |\n"
            f"|--------|-------|\n"
            f"| Pipeline analyzed | ${_total_value(active) / 1_000_000:.0f}M ({len(active)} deals) |\n"
            f"| Stalled identified | {len(stalled)} deals (${_total_value(stalled) / 1_000_000:.1f}M) |\n"
            f"| Tasks drafted | {total_tasks} actions |\n"
            f"| Quick wins | ${quick_val // 1000}K this week |\n"
            f"| Acceleration opportunity | ${accel / 1_000_000:.1f}M |\n\n"
            f"**Synthetic Planning Targets:** Stall time {_TARGETS['stall_days_now']} -> "
            f"{_TARGETS['stall_days_target']} days, +${_TARGETS['q4_commit_add'] / 1_000_000:.1f}M Q4 commit, "
            f"pipeline health {on_track_pct}% -> {_TARGETS['health_target_pct']}%\n\n"
            f"Your ${_total_value(stalled) / 1_000_000:.1f}M in stalled deals now have draft action plans and a "
            f"proposed tracking setup with a {_TARGETS['stall_warning_days']}-day early warning, ready for your approval.\n\n"
            f"Source: [All Pipeline Systems]"
        )

if __name__ == "__main__":
    agent = DealProgressionAgent()
    for op in ["pipeline_health", "stalled_deals", "action_plans",
               "acceleration", "assign_tasks", "executive_summary"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
