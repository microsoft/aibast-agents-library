"""Meeting overlap and back-to-back checks from README.md, Capabilities.

Only explicit, offset-aware event intervals are compared. Cancelled meetings
do not block time, touching intervals are back-to-back rather than overlaps.
Notes synthesis, agenda drafting, contextual mail search, and alternative-time
recommendations stay with the AI. Calendar changes require external review.
All sample events are fictional and no wall clock is read.
"""
import json
from datetime import datetime, timezone

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/calendar-manager-agent",
    "version": "0.1.0", "display_name": "Calendar Manager",
    "description": "Detects overlaps and back-to-back events from supplied calendar data.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution calendar-manager-agent",
    "quality_tier": "experimental", "category": "productivity",
    "tags": ["calendar", "conflicts"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"events": [
    {"id": "C1", "subject": "Contoso planning", "start": "2026-11-02T09:00:00-05:00", "end": "2026-11-02T10:00:00-05:00"},
    {"id": "C2", "subject": "Northwind review", "start": "2026-11-02T09:30:00-05:00", "end": "2026-11-02T10:30:00-05:00"},
    {"id": "C3", "subject": "Fabrikam handoff", "start": "2026-11-02T10:30:00-05:00", "end": "2026-11-02T11:00:00-05:00"}]}


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Event times must include explicit UTC offsets.")
    return result.astimezone(timezone.utc)


def evaluate(data):
    events = data["events"]
    if not isinstance(events, list):
        raise ValueError("events must be a list.")
    intervals, seen = [], set()
    for event in events:
        if event["id"] in seen:
            raise ValueError("Event IDs must be unique.")
        seen.add(event["id"])
        cancelled = event.get("cancelled", False)
        if type(cancelled) is not bool:
            raise ValueError("cancelled must be Boolean.")
        start, end = timestamp(event["start"]), timestamp(event["end"])
        if end <= start:
            raise ValueError("Each event must end after it starts.")
        if not cancelled:
            intervals.append((start, end, event["id"]))
    intervals.sort()
    findings = []
    for index, (start, end, identifier) in enumerate(intervals):
        for other_start, other_end, other_id in intervals[index + 1:]:
            if other_start > end:
                break
            findings.append({"first": identifier, "second": other_id,
                             "kind": "back-to-back" if other_start == end else "overlap"})
    return {"findings": findings, "active_events": len(intervals), "calendar_changed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Calendar Manager, a synthetic scheduling pilot checking explicit meeting intervals for overlaps and back-to-back events.

Use only the bundled fictional events C1, C2 and C3 with their recorded time offsets. Never match them to a real calendar, attendee or meeting.

Answer with the calendar conflict tool, not from memory. Lead with the findings and active event count, quote event ids exactly, ignore cancelled events and distinguish touching intervals from overlaps.

You never read a live mailbox, book, cancel or move a meeting. The calendar owner reviews conflicts and any suggested alternative before making changes."""

OPERATION_GUIDE = {
    "conflict_check": {
        "title": "Calendar conflict check",
        "when": "Use when someone asks which supplied meetings overlap or run back-to-back, excluding cancelled events.",
        "ask": "Which of the sample meetings on my calendar, C1, C2 and C3, overlap or run back to back?",
    },
}

CARRIED = [
    "Synthesizes meeting notes, drafts agendas, searches contextual mail and recommends alternative times through the original solution's calendar agent.",
    "Reads and changes calendar events through the original solution's calendar connections after owner review.",
]


class CalendarManagerAgent(BasicAgent):
    def __init__(self):
        self.name = "CalendarConflictCheck"
        self.metadata = {"name": self.name, "description": "Check event intervals. Optional payload_json: events list with unique id, start/end ISO timestamps with offsets, and optional cancelled Boolean. With no payload_json it uses the sample on file: the sample meetings C1, C2 and C3.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to conflict_check."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "conflict_check") not in OPERATION_GUIDE:
                raise ValueError("operation must be conflict_check.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(CalendarManagerAgent().perform())
