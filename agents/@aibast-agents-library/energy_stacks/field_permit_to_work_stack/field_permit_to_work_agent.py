"""
Field Permit to Work Agent

Supports a utility permit coordinator through the permit-to-work lifecycle for
field crews: the day's permit queue, a drafted risk assessment, an isolation
check that compares the isolation plan with the live switching state, the
sign-off route and timing, crew briefing acknowledgements, close-out clearance
and a monthly safety roll-up.

Where a real deployment would read a work-management system, a network control
system and a crew briefing app, this agent uses a fixed synthetic snapshot so it
runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/field-permit-to-work",
    "version": "1.0.0",
    "display_name": "Field Permit to Work Agent",
    "description": "Keep every field permit safe and on time: draft the risk assessment, check the isolation plan against the live switching state, track sign-offs and crew briefings, and verify close-out, so no crew starts work on an unconfirmed isolation.",
    "author": "AIBAST",
    "tags": ["energy", "utilities", "permit-to-work", "field-safety", "isolation", "work-management"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot: Tuesday 10 March 2026, 06:30)
# ═══════════════════════════════════════════════════════════════

_SNAPSHOT = "Tue 10 Mar 2026 06:30"
_NOW_MIN = 6 * 60 + 30
_ORG = "Northwind Energy Networks"
_COORDINATOR = "Dana Brooks, permit coordinator"

_HAZARDS = {
    "transformer": [
        ("Electric shock or arc flash", "De-energize, lock out and tag, prove dead, arc-rated clothing"),
        ("Hot oil contact", "Cooling period, oil-handling gloves, drip tray"),
        ("Manual handling of heavy components", "Mechanical lift, two-person carry"),
    ],
    "underground_cable": [
        ("Striking a live cable while digging", "Cable-route plans, cable locator scan, hand dig near the route"),
        ("Confined space in the joint pit", "Gas monitor, top person, rescue plan"),
        ("Heavy cable handling", "Cable rollers, two-person lift"),
    ],
    "overhead_line": [
        ("Working at height", "Elevated work platform, fall arrest, exclusion zone"),
        ("Adjacent live conductors", "Safe approach distance, insulated tools, portable earths"),
        ("Wind on the elevated platform", "Wind check before lift, stop-work limit"),
    ],
}
_PPE = {
    "transformer": "Arc-rated coveralls, insulated gloves, face shield",
    "underground_cable": "Coveralls, cut-resistant gloves, gas monitor",
    "overhead_line": "Fall-arrest harness, insulated gloves, high-visibility clothing",
}
_WEATHER_UPLIFT = {"calm": 0, "windy": 10, "wet": 15, "icy": 25}
_BASE_RISK = 45
_SENIOR_REDUCTION = 10

_STAGES = [
    ("Supervisor review", "Shift supervisor", 60),
    ("Authorized person review", "Lee Carter, authorized person", 120),
    ("Site manager endorsement", "Site manager", 90),
    ("Permit office issue", "Permit office", 30),
]

_PERMITS = {
    "ptw-4471": {
        "id": "PTW-4471", "site": "Cedar Hill Substation", "asset": "Transformer T2", "asset_class": "transformer",
        "work": "Tap-changer maintenance", "start_min": 11 * 60, "hours": 6, "crew": "CR-12",
        "weather": "wet", "senior": False, "stage": 1,
        "required": [("ISO-T2-A", "Primary disconnector", "Open"), ("ISO-T2-B", "Earth switch", "Closed"),
                     ("ISO-T2-C", "Lockout padlock", "Applied"), ("ISO-T2-D", "Voltage proving point", "Tested")],
        "planned": ["ISO-T2-A", "ISO-T2-B", "ISO-T2-C", "ISO-T2-D"],
        "devices": [("CB-CH-01", "Circuit breaker", "Open", "Applied"), ("CB-CH-02", "Circuit breaker", "Open", "Not applied"),
                    ("DS-CH-01", "Disconnector", "Open", "Applied"), ("ES-CH-01", "Earth switch", "Closed", "Applied")],
        "crew_members": [("Morgan Hayes", "Crew lead", True), ("Ravi Kumar", "Electrician", True),
                         ("Elena Novak", "Electrician", True), ("Chris Dale", "Apprentice", False)],
        "closeout": {"people_start": 4, "people_end": 4, "tools_out": 18, "tools_in": 17, "area_safe": True,
                     "work_complete": True, "entered": "16:40 by Morgan Hayes"},
    },
    "ptw-4472": {
        "id": "PTW-4472", "site": "Riverside Feeder 7", "asset": "Cable joint J14", "asset_class": "underground_cable",
        "work": "Cable joint repair", "start_min": 10 * 60, "hours": 5, "crew": "CR-07",
        "weather": "calm", "senior": True, "stage": 0,
        "required": [("ISO-F7-A", "Feeder breaker", "Open"), ("ISO-F7-B", "Earth switch", "Closed"),
                     ("ISO-F7-C", "Lockout padlock", "Applied"), ("ISO-F7-D", "Voltage proving point", "Tested")],
        "planned": ["ISO-F7-A", "ISO-F7-C", "ISO-F7-D"],
        "devices": [("CB-RV-07", "Circuit breaker", "Open", "Applied"), ("ES-RV-07", "Earth switch", "Closed", "Applied")],
        "crew_members": [("Jordan Wells", "Crew lead", False), ("Aisha Bello", "Cable jointer", False),
                         ("Tom Reyes", "Cable jointer", False)],
        "closeout": {"people_start": 3, "people_end": 3, "tools_out": 12, "tools_in": 12, "area_safe": True,
                     "work_complete": False, "entered": "Not yet entered"},
    },
    "ptw-4473": {
        "id": "PTW-4473", "site": "Hilltop Line 3", "asset": "Span 3-14 to 3-15", "asset_class": "overhead_line",
        "work": "Insulator replacement", "start_min": 13 * 60, "hours": 4, "crew": "CR-21",
        "weather": "windy", "senior": True, "stage": 0,
        "required": [("ISO-L3-A", "Line recloser", "Open"), ("ISO-L3-B", "Portable earths", "Applied"),
                     ("ISO-L3-C", "Lockout padlock", "Applied")],
        "planned": ["ISO-L3-A", "ISO-L3-B", "ISO-L3-C"],
        "devices": [("RC-HT-03", "Recloser", "Open", "Applied"), ("DS-HT-03", "Disconnector", "Open", "Applied")],
        "crew_members": [("Priya Raman", "Crew lead", True), ("Leo Grant", "Line worker", True),
                         ("Nina Holt", "Line worker", True)],
        "closeout": {"people_start": 3, "people_end": 3, "tools_out": 15, "tools_in": 15, "area_safe": True,
                     "work_complete": True, "entered": "17:10 by Priya Raman"},
    },
}
_ORDER = ["ptw-4471", "ptw-4472", "ptw-4473"]

_KPIS = {
    "window": "30 days to Tue 10 Mar 2026", "issued": 212, "closed_on_time": 196, "near_misses": 5,
    "avg_cycle_hours": 18.4, "lockout_gaps_caught": 7, "plans_returned": 4,
    "top_hazards": ["Electric shock or arc flash", "Working at height", "Striking a live cable while digging",
                    "Confined space"],
}

_GATE = (
    "Synthetic permit support only. This agent prepares drafts and checks; it does not issue, approve or "
    "close a permit, operate or lock any device, instruct a crew, or authorize work. Authorized people make "
    "every safety decision."
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_permit(query):
    """Permit ID (case-insensitive); default PTW-4471; None when no permit has that ID (never another permit)."""
    if not query:
        return "ptw-4471"
    q = str(query).lower().strip()
    return q if q in _PERMITS else None


def _hhmm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _risk(p):
    score = _BASE_RISK + _WEATHER_UPLIFT[p["weather"]] - (_SENIOR_REDUCTION if p["senior"] else 0)
    band = "High" if score >= 55 else "Medium" if score >= 25 else "Low"
    return score, band


def _plan_missing(p):
    return [r for r in p["required"] if r[0] not in p["planned"]]


def _live_issues(p):
    issues = []
    for dev, kind, state, lock in p["devices"]:
        if kind == "Earth switch":
            ok_state = state == "Closed"
        else:
            ok_state = state == "Open"
        if not ok_state:
            issues.append(f"{dev} {kind.lower()} is {state.lower()}")
        if lock != "Applied":
            issues.append(f"{dev} lockout not applied")
    return issues


def _footer(source):
    return f"{_GATE}\n\nSource: [{source}]\nAgents: FieldPermitToWorkAgent"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "permit_queue", "risk_assessment", "isolation_check", "authorization_route",
    "crew_briefing", "clearance_check", "safety_kpis",
]


class FieldPermitToWorkAgent(BasicAgent):
    """
    Permit-to-work assistant for utility field crews.

    Operations:
        permit_queue         - today's permits with stage, start time, risk band and blockers
        risk_assessment      - drafted hazards, controls, PPE and residual risk for one permit
        isolation_check      - isolation plan vs required points, and live switching state
        authorization_route  - remaining sign-offs, accountable people and earliest issue time
        crew_briefing        - briefing topics and crew acknowledgements
        clearance_check      - close-out reconciliation of people, tools, area and work status
        safety_kpis          - 30-day permit safety roll-up
    """

    def __init__(self):
        self.name = "FieldPermitToWorkAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Use this tool for field permit-to-work questions at a fictional energy network operator. It lists "
                "the permits waiting today (permit_queue), drafts the risk assessment for a job (risk_assessment), "
                "checks whether the isolation is actually in place, comparing the isolation plan with the live "
                "switching state (isolation_check), shows where a permit is in the sign-off chain and whether it "
                "will be ready for the planned start (authorization_route), shows whether the crew has acknowledged "
                "the briefing (crew_briefing), checks whether a finished job can be closed (clearance_check), and "
                "summarizes permit safety for the month (safety_kpis). Pass permit_id as the permit number: "
                "PTW-4471 is the Cedar Hill Substation transformer job (the default), PTW-4472 the Riverside Feeder 7 "
                "cable joint, PTW-4473 the Hilltop Line 3 insulator job. Outputs are drafts and checks only: no permit is issued or closed, no device "
                "is operated and no crew is instructed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "permit_queue for permits waiting today; risk_assessment to draft hazards and controls; "
                            "isolation_check for whether isolation is in place; authorization_route for sign-off "
                            "status and readiness for the start time; crew_briefing for crew acknowledgements; "
                            "clearance_check when the crew has finished and the permit should close; safety_kpis "
                            "for monthly permit safety performance."
                        ),
                    },
                    "permit_id": {
                        "type": "string",
                        "enum": ["PTW-4471", "PTW-4472", "PTW-4473"],
                        "description": "Permit ID: PTW-4471 Cedar Hill Substation (default), PTW-4472 Riverside Feeder 7, PTW-4473 Hilltop Line 3.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "permit_queue")
        dispatch = {
            "permit_queue": self._permit_queue,
            "risk_assessment": self._risk_assessment,
            "isolation_check": self._isolation_check,
            "authorization_route": self._authorization_route,
            "crew_briefing": self._crew_briefing,
            "clearance_check": self._clearance_check,
            "safety_kpis": self._safety_kpis,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        if op in ("permit_queue", "safety_kpis"):
            return handler()
        key = _resolve_permit(kwargs.get("permit_id", ""))
        if key is None:
            known = ", ".join(f"{_PERMITS[k]['id']} ({_PERMITS[k]['site']})" for k in _ORDER)
            return (f"No synthetic permit matches '{kwargs.get('permit_id')}'. Permits in the snapshot: {known}.\n\n"
                    f"{_footer('Synthetic Permit Snapshot')}")
        return handler(key)

    # ── permit_queue ──────────────────────────────────────────
    def _permit_queue(self):
        rows = []
        for key in _ORDER:
            p = _PERMITS[key]
            _score, band = _risk(p)
            blocker = "Isolation plan incomplete" if _plan_missing(p) else (
                "Live isolation not confirmed" if _live_issues(p) else "None")
            rows.append(f"| {p['id']} | {p['site']} | {p['work']} | {_hhmm(p['start_min'])} | "
                        f"{_STAGES[p['stage']][0]} | {band} | {blocker} |")
        return (
            f"**Permit Queue: {_ORG}** (snapshot {_SNAPSHOT})\n\n"
            f"| Permit | Site | Work | Start | Current stage | Risk | Blocker |\n|---|---|---|---|---|---|---|\n"
            + "\n".join(rows) + "\n\n"
            f"**Today:** {len(_ORDER)} permits, 2 with a blocker before work can start.\n"
            f"**Recommended next:** PTW-4471 at Cedar Hill is the highest-risk job; draft its risk assessment "
            f"and check its isolation first.\n\n"
            f"{_footer('Synthetic Permit Snapshot')}"
        )

    # ── risk_assessment ───────────────────────────────────────
    def _risk_assessment(self, key):
        p = _PERMITS[key]
        score, band = _risk(p)
        haz = "\n".join(f"| {h} | {c} |" for h, c in _HAZARDS[p["asset_class"]])
        reduction = _SENIOR_REDUCTION if p["senior"] else 0
        return (
            f"**Risk Assessment Draft: {p['id']} {p['site']} {p['asset']}**\n\n"
            f"| Hazard | Controls |\n|---|---|\n{haz}\n\n"
            f"**PPE:** {_PPE[p['asset_class']]}\n\n"
            f"| Residual risk | Value |\n|---|---|\n"
            f"| Base risk | {_BASE_RISK} |\n"
            f"| Weather ({p['weather']}) | +{_WEATHER_UPLIFT[p['weather']]} |\n"
            f"| Senior authorized crew | -{reduction} |\n"
            f"| **Residual risk score** | **{score} of 100 ({band})** |\n\n"
            f"**Method steps:** toolbox talk and sign-in; confirm isolation and prove dead; barriers and signs; "
            f"work to method statement; tidy site and clear the permit.\n\n"
            f"Risk bands: Low below 25, Medium 25-54, High 55 or more. Draft for the authorized person to review "
            f"and sign.\n\n"
            f"{_footer('Synthetic Hazard Library + Permit Snapshot')}"
        )

    # ── isolation_check ───────────────────────────────────────
    def _isolation_check(self, key):
        p = _PERMITS[key]
        missing = _plan_missing(p)
        plan_rows = "\n".join(
            f"| {pid} | {kind} | {state} | {'In plan' if pid in p['planned'] else 'MISSING from plan'} |"
            for pid, kind, state in p["required"]
        )
        dev_rows = "\n".join(f"| {d} | {k} | {s} | {l} |" for d, k, s, l in p["devices"])
        issues = _live_issues(p)
        plan_result = "PASS" if not missing else "FAIL"
        covered = len(p["required"]) - len(missing)
        if missing:
            verdict = (f"**Result: Do not start work.** The isolation plan is missing "
                       f"{', '.join(m[0] + ' ' + m[1].lower() for m in missing)}; return it to the planner.")
        elif issues:
            verdict = (f"**Result: Isolation NOT confirmed. Do not start work.** {'; '.join(issues)}. "
                       f"Ask the control room to correct it and re-check before the crew briefing.")
        else:
            verdict = "**Result: Isolation confirmed** against the plan and the live switching state."
        return (
            f"**Isolation Check: {p['id']} {p['site']}** (live state as of {_SNAPSHOT})\n\n"
            f"**Plan vs required points: {plan_result} ({covered} of {len(p['required'])})**\n\n"
            f"| Point | Type | Required state | Plan |\n|---|---|---|---|\n{plan_rows}\n\n"
            f"**Live switching state:**\n\n"
            f"| Device | Type | State | Lockout |\n|---|---|---|---|\n{dev_rows}\n\n"
            f"{verdict}\n\n"
            f"No device was operated or locked.\n\n"
            f"{_footer('Synthetic Isolation Plan + Control Room Snapshot')}"
        )

    # ── authorization_route ───────────────────────────────────
    def _authorization_route(self, key):
        p = _PERMITS[key]
        if _plan_missing(p):
            return (
                f"**Sign-off Route: {p['id']} (Blocked)**\n\n"
                f"The permit cannot enter sign-off: the isolation plan is incomplete. It returns to the planner, "
                f"and the requested {_hhmm(p['start_min'])} start is at risk.\n\n"
                f"{_footer('Synthetic Permit Workflow')}"
            )
        remaining = _STAGES[p["stage"]:]
        rows, t = [], _NOW_MIN
        for name, who, mins in remaining:
            t += mins
            rows.append(f"| {name} | {who} | {mins} min | {_hhmm(t)} |")
        margin = p["start_min"] - t
        score, band = _risk(p)
        priority = "P1" if band == "High" else "P2" if band == "Medium" else "P3"
        status = (f"On track: ready {margin} minutes before the {_hhmm(p['start_min'])} start"
                  if margin >= 0 else f"At risk: {-margin} minutes after the {_hhmm(p['start_min'])} start")
        return (
            f"**Sign-off Route: {p['id']} {p['site']}** (from {_SNAPSHOT})\n\n"
            f"| Stage | Accountable | Target time | Due by |\n|---|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"**Next sign-off:** {remaining[0][1]} ({remaining[0][0]}), priority {priority} ({band} risk).\n"
            f"**Earliest issue:** {_hhmm(t)}. {status}.\n"
            f"**Condition:** the permit can only be issued once the live isolation is confirmed.\n\n"
            f"Routing note prepared for the permit office; no sign-off was given or requested.\n\n"
            f"{_footer('Synthetic Permit Workflow')}"
        )

    # ── crew_briefing ─────────────────────────────────────────
    def _crew_briefing(self, key):
        p = _PERMITS[key]
        rows = "\n".join(f"| {n} | {r} | {'Acknowledged' if a else 'Not yet'} |" for n, r, a in p["crew_members"])
        acked = sum(1 for _n, _r, a in p["crew_members"] if a)
        total = len(p["crew_members"])
        pending = [n for n, _r, a in p["crew_members"] if not a]
        hazards = ", ".join(h for h, _c in _HAZARDS[p["asset_class"]])
        result = ("Complete: every crew member has acknowledged." if acked == total else
                  f"Incomplete: {acked} of {total} acknowledged. Work cannot start until {', '.join(pending)} "
                  f"acknowledge{'s' if len(pending) == 1 else ''}.")
        return (
            f"**Crew Briefing: {p['id']} crew {p['crew']}**\n\n"
            f"**Briefing topics:** isolation points and lockouts, PPE check, emergency contacts and muster point, "
            f"site hazards ({hazards}).\n\n"
            f"| Crew member | Role | Acknowledgement |\n|---|---|---|\n{rows}\n\n"
            f"**Status:** {result}\n\n"
            f"Briefing sheet prepared for the crew lead; no one was messaged.\n\n"
            f"{_footer('Synthetic Crew Briefing Records')}"
        )

    # ── clearance_check ───────────────────────────────────────
    def _clearance_check(self, key):
        p = _PERMITS[key]
        c = p["closeout"]
        issues = []
        if c["people_end"] != c["people_start"]:
            issues.append(f"People on site: {c['people_start']} at start, {c['people_end']} at close")
        if c["tools_in"] != c["tools_out"]:
            issues.append(f"Tools: {c['tools_out']} issued, {c['tools_in']} returned "
                          f"({c['tools_out'] - c['tools_in']} unaccounted for)")
        if not c["area_safe"]:
            issues.append("Work area not confirmed safe")
        if not c["work_complete"]:
            issues.append("Work not marked complete")
        status = "Ready to clear" if not issues else "Held for review"
        issue_text = "\n".join(f"- {i}" for i in issues) if issues else "- None"
        return (
            f"**Permit Clearance Check: {p['id']} {p['site']}**\n\n"
            f"| Check | Start | Close |\n|---|---|---|\n"
            f"| People on site | {c['people_start']} | {c['people_end']} |\n"
            f"| Tools | {c['tools_out']} issued | {c['tools_in']} returned |\n"
            f"| Area safe | | {'Yes' if c['area_safe'] else 'No'} |\n"
            f"| Work complete | | {'Yes' if c['work_complete'] else 'No'} |\n\n"
            f"**Close-out entered:** {c['entered']}\n"
            f"**Clearance status:** {status}\n\n**Issues:**\n{issue_text}\n\n"
            + ("**Next step:** the crew lead resolves each issue (for a tool shortfall, finds the missing tool) "
               "before the authorized person clears the permit and the control room restores supply.\n\n" if issues else
               "**Next step:** the authorized person reviews and clears the permit.\n\n")
            + f"The permit was not closed.\n\n"
            f"{_footer('Synthetic Close-out Records')}"
        )

    # ── safety_kpis ───────────────────────────────────────────
    def _safety_kpis(self):
        k = _KPIS
        rate = k["closed_on_time"] * 100 // k["issued"]
        hazards = "\n".join(f"{i}. {h}" for i, h in enumerate(k["top_hazards"], 1))
        return (
            f"**Permit Safety Roll-up: {_ORG}** ({k['window']})\n\n"
            f"| Measure | Value |\n|---|---|\n"
            f"| Permits issued | {k['issued']} |\n"
            f"| Closed on time | {k['closed_on_time']} ({rate}%) |\n"
            f"| Near misses reported | {k['near_misses']} |\n"
            f"| Average permit cycle | {k['avg_cycle_hours']} hours |\n"
            f"| Lockout gaps caught before work | {k['lockout_gaps_caught']} |\n"
            f"| Isolation plans returned to planner | {k['plans_returned']} |\n\n"
            f"**Top hazards this month:**\n{hazards}\n\n"
            f"**Focus:** lockout gaps are the most frequent pre-start finding; keep the live isolation check "
            f"before every crew briefing.\n\n"
            f"{_footer('Synthetic Permit Analytics Snapshot')}"
        )


if __name__ == "__main__":
    agent = FieldPermitToWorkAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op, permit_id="PTW-4471"))
        print()
