"""
First-Time Fix Agent for Telecommunications.

Read-only first-call resolution support for a broadband provider's contact center and field service team, built
on a synthetic snapshot of five customer services in one service area: the service status with the guided
connection fix to use during the call, local network work that could be affecting the service, previous visit
outcomes with technician notes, and the recommended technician with the job preparation when a visit is needed.
Every booking is a draft for a human agent to confirm.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/first-time-fix",
    "version": "1.0.0",
    "display_name": "First-Time Fix Agent",
    "description": "Help contact center and field service agents resolve a customer's connection issue on the first call from a synthetic broadband snapshot: the service status with the guided connection fix, local network work that could be affecting the service, previous visit outcomes with technician notes, and the recommended technician with the job preparation when a visit is needed. The agent never books, changes or cancels a visit, changes a service, contacts a customer or dispatches a technician; a human agent confirms every booking through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["telecommunications", "broadband", "contact-center", "field-service", "first-call-resolution"],
    "category": "telecom_media_gaming",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (fixed demo day: one service area, five customer services)
# ---------------------------------------------------------------------------

SERVICES = {
    "alder-grove": {
        "name": "Alder Grove Service", "plan": "Fibre 500", "area": "North service area", "cabinet": "Cabinet N-14",
        "status": "Active - intermittent connection", "drops_7_days": 6, "open_case": "CS-48211",
        "guided_fix": [
            "Restart the optical network terminal (ONT).",
            "Wait 2 minutes for it to reconnect.",
            "Confirm the broadband light is solid green.",
        ],
        "visit_rule": "Book a technician if the broadband light stays red after the restart.",
        "flag": "Repeated drops after restart",
    },
    "cedar-reach": {
        "name": "Cedar Reach Service", "plan": "Fibre 300", "area": "East service area", "cabinet": "Cabinet E-03",
        "status": "Active - no fault detected", "drops_7_days": 1, "open_case": "CS-48207",
        "guided_fix": [
            "Check that the router power cable is secure.",
            "Restart the router.",
            "Test one wired device.",
        ],
        "visit_rule": "No visit unless service is still unavailable after the planned maintenance.",
        "flag": "Maintenance window may affect connection",
    },
    "willow-park": {
        "name": "Willow Park Service", "plan": "Fibre 900", "area": "West service area", "cabinet": "Cabinet W-21",
        "status": "Active - connection restored", "drops_7_days": 0, "open_case": "CS-48190",
        "guided_fix": [
            "Confirm the router is powered on.",
            "Run a connection test before taking further action.",
        ],
        "visit_rule": "No visit; no action is required if the connection test passes.",
        "flag": "None",
    },
    "harbour-view": {
        "name": "Harbour View Service", "plan": "Fibre 500", "area": "South service area", "cabinet": "Cabinet S-08",
        "status": "Active - intermittent connection", "drops_7_days": 4, "open_case": "CS-48215",
        "guided_fix": [
            "Check the router indicator lights.",
            "Reseat the broadband cable.",
            "Restart the router once.",
        ],
        "visit_rule": "Book a technician if the broadband indicator stays off.",
        "flag": "Broadband indicator reported off",
    },
    "meadow-lane": {
        "name": "Meadow Lane Service", "plan": "Fibre 300", "area": "North service area", "cabinet": "Cabinet N-09",
        "status": "Active - unavailable", "drops_7_days": 9, "open_case": "CS-48219",
        "guided_fix": [
            "Verify the optical network terminal has power.",
            "Restart it.",
            "Check the broadband light.",
        ],
        "visit_rule": "No premises visit while the emergency cable repair is in progress.",
        "flag": "Local repair expected to complete today",
    },
}

LOCAL_WORK = [
    {"id": "NW-3301", "area": "East service area", "cabinet": "Cabinet E-03", "type": "Planned cabinet maintenance",
     "window": "Today 13:00-16:00", "status": "Scheduled", "affects": ["cedar-reach"]},
    {"id": "NW-3307", "area": "North service area", "cabinet": "Cabinet N-09", "type": "Emergency cable repair",
     "window": "Started 07:40, expected complete 15:30 today", "status": "In progress", "affects": ["meadow-lane"]},
]

VISITS = [
    {"id": "FV-7710", "service": "alder-grove", "when": "22 days ago", "outcome": "Connection restored",
     "note": "Reseated fibre connector; investigate intermittent drops if they recur.", "technician": "Priya Nair"},
    {"id": "FV-7655", "service": "cedar-reach", "when": "40 days ago", "outcome": "No fault found",
     "note": "Service was stable on arrival; customer advised about planned cabinet maintenance.",
     "technician": "Daniel Okafor"},
    {"id": "FV-7702", "service": "willow-park", "when": "24 days ago", "outcome": "Router replaced",
     "note": "New router installed and connection test passed.", "technician": "Marta Lewis"},
    {"id": "FV-7719", "service": "meadow-lane", "when": "20 days ago", "outcome": "External network fault identified",
     "note": "Local cable repair required; no premises work completed.", "technician": "Owen Shah"},
]

TECHNICIANS = {
    "Priya Nair": {"skills": ["Fibre connectors", "ONT replacement"], "area": "North service area",
                   "next_slot": "Tomorrow 09:00-11:00"},
    "Daniel Okafor": {"skills": ["Cabinet work", "Router setup"], "area": "East service area",
                      "next_slot": "Tomorrow 13:00-15:00"},
    "Marta Lewis": {"skills": ["Router diagnostics", "In-home Wi-Fi"], "area": "West service area",
                    "next_slot": "Tomorrow 10:00-12:00"},
    "Owen Shah": {"skills": ["External cable", "ONT replacement"], "area": "North service area",
                  "next_slot": "Tomorrow 14:00-16:00"},
    "Sam Whitley": {"skills": ["Router diagnostics", "Fibre connectors"], "area": "South service area",
                    "next_slot": "Tomorrow 08:00-10:00"},
}

BOOKINGS = {
    "alder-grove": {"technician": "Priya Nair", "status": "Ready to book",
                    "preparation": ["Add the repeated-drop history (6 drops in 7 days).",
                                    "Include the previous fibre-connector visit note (FV-7710).",
                                    "Test the optical network terminal and fibre connector on arrival."]},
    "cedar-reach": {"technician": "Daniel Okafor", "status": "Not required",
                    "preparation": ["Hold the visit until planned cabinet maintenance NW-3301 completes.",
                                    "Include the maintenance reference if service remains unavailable."]},
    "willow-park": {"technician": "Marta Lewis", "status": "No booking needed",
                    "preparation": ["Bring the router diagnostics kit only if a later test fails.",
                                    "Confirm connection test results before any travel."]},
    "harbour-view": {"technician": "Sam Whitley", "status": "Ready to book if the indicator stays off",
                     "preparation": ["Note that the broadband indicator was reported off.",
                                     "Bring a replacement broadband cable and router diagnostics kit."]},
    "meadow-lane": {"technician": "Owen Shah", "status": "Pending local repair",
                    "preparation": ["Do not book a premises visit while emergency cable repair NW-3307 is open.",
                                    "Review repair completion first."]},
}

BOUNDARY = ("> Read-only synthetic snapshot. No visit, service, customer contact, case or technician schedule was "
            "changed; every booking is a draft for the agent to confirm.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_service(value):
    """Service key or part of its name; empty -> alder-grove (the demo service); no match -> None."""
    if not value:
        return "alder-grove"
    q = str(value).lower().strip().replace(" service", "")
    for key, svc in SERVICES.items():
        if q in (key, key.replace("-", " ")) or q in svc["name"].lower():
            return key
    return None


def _local_work(key):
    return [w for w in LOCAL_WORK if key in w["affects"]]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = ["guided_fix", "local_work_check", "visit_history", "technician_booking"]


class FirstTimeFixAgent(BasicAgent):
    """First-call resolution agent for broadband connection issues (read-only, synthetic)."""

    def __init__(self):
        self.name = "FirstTimeFixAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call this tool for a customer's connection issue: the guided "
                "fix to use now, whether local network work is affecting the service, what previous visits found, "
                "and which technician to book with what job preparation. Call it right away; every operation has "
                "demo defaults."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "guided_fix for the service status and the step-by-step fix to use during the call; "
                            "local_work_check for planned or emergency network work affecting the service; "
                            "visit_history for previous visit outcomes and technician notes; technician_booking for "
                            "the recommended technician, the job preparation and the booking status."
                        ),
                    },
                    "service": {
                        "type": "string",
                        "description": "Customer service such as Alder Grove Service (the default) or Meadow Lane.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "guided_fix")
        key = _resolve_service(kwargs.get("service"))
        if key is None:
            return (f"# Unknown Service\n\nNo synthetic service matches `{kwargs.get('service')}`; no substitute "
                    f"service was used. Services: {', '.join(s['name'] for s in SERVICES.values())}.\n\n{BOUNDARY}")
        handlers = {
            "guided_fix": self._guided_fix,
            "local_work_check": self._local_work_check,
            "visit_history": self._visit_history,
            "technician_booking": self._technician_booking,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    def _guided_fix(self, key) -> str:
        s = SERVICES[key]
        work = _local_work(key)
        lines = [
            f"# Guided Connection Fix - {s['name']}",
            "",
            f"**Plan:** {s['plan']} | **Status:** {s['status']} | **Drops in 7 days:** {s['drops_7_days']} "
            f"| **Open case:** {s['open_case']}",
            "",
            "## Steps to use now",
        ]
        lines += [f"{i}. {step}" for i, step in enumerate(s["guided_fix"], 1)]
        lines += [
            "",
            f"**When to book a visit:** {s['visit_rule']}",
            f"**Local work:** {', '.join(w['type'] + ' (' + w['id'] + ')' for w in work) or 'No confirmed local work'}",
            f"**Flag:** {s['flag']}",
            "",
            BOUNDARY,
        ]
        return "\n".join(lines)

    def _local_work_check(self, key) -> str:
        s = SERVICES[key]
        work = _local_work(key)
        lines = [f"# Local Work Check - {s['name']}", "",
                 f"**Area:** {s['area']} | **Cabinet:** {s['cabinet']}", ""]
        if work:
            lines += ["| Work | Type | Window | Status |", "|------|------|--------|--------|"]
            lines += [f"| {w['id']} | {w['type']} | {w['window']} | {w['status']} |" for w in work]
            lines += ["", f"**Flag for the agent:** {s['flag']}"]
        else:
            lines += [f"**No confirmed local work** on {s['cabinet']} or in the {s['area']}; "
                      f"checked {len(LOCAL_WORK)} open network work records.",
                      f"**Flag for the agent:** {s['flag']}"]
        lines += ["", BOUNDARY]
        return "\n".join(lines)

    def _visit_history(self, key) -> str:
        s = SERVICES[key]
        visits = [v for v in VISITS if v["service"] == key]
        lines = [f"# Previous Visits - {s['name']}", ""]
        if visits:
            lines += ["| Visit | When | Outcome | Technician | Note |", "|-------|------|---------|------------|------|"]
            lines += [f"| {v['id']} | {v['when']} | {v['outcome']} | {v['technician']} | {v['note']} |"
                      for v in visits]
        else:
            lines.append("**No previous visits** are recorded for this service.")
        lines += ["", BOUNDARY]
        return "\n".join(lines)

    def _technician_booking(self, key) -> str:
        s = SERVICES[key]
        b = BOOKINGS[key]
        t = TECHNICIANS[b["technician"]]
        lines = [
            f"# Technician Booking - {s['name']}",
            "",
            f"**Recommended technician:** {b['technician']} ({', '.join(t['skills'])}; {t['area']})",
            f"**Next slot:** {t['next_slot']} | **Booking status:** {b['status']}",
            "",
            "## Job preparation",
        ]
        lines += [f"- {p}" for p in b["preparation"]]
        lines += ["", "> Draft only: no visit was booked. " + BOUNDARY[2:]]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = FirstTimeFixAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
