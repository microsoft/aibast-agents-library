"""
Live Event Launch Planner Agent for Gaming.

Read-only launch planning support for a game studio's live operations, community and marketing teams, built on a
synthetic snapshot of four seasonal in-game events: the launch timeline from communications approval to launch
day, the cross-team readiness checklist with owners and status, the approved player announcement with its
publishing permission, and a launch summary of late, missing and blocked work. Every announcement and reminder is
a draft; nothing is published or sent.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/live-event-launch-planner",
    "version": "1.0.0",
    "display_name": "Live Event Launch Planner Agent",
    "description": "Help live operations, community and marketing teams launch a seasonal in-game event from one plan built on a synthetic snapshot: the launch timeline with every milestone to launch day, the readiness checklist across teams with owners and status, the player announcement with its approval and publishing permission, and a summary of late, missing and blocked work. The agent never publishes an announcement, changes a task, sends a reminder or changes the event; the event owners approve every step through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["gaming", "live-operations", "community", "event-launch", "readiness"],
    "category": "telecom_media_gaming",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (fixed demo day: four seasonal events in planning)
# ---------------------------------------------------------------------------

EVENTS = {
    "frostveil-festival": {
        "name": "Frostveil Festival", "plan": "PLN-FVF Launch", "launch_pack": "SP-FVF-LaunchPack-Approved",
        "launch_day": "In 12 days", "missing": "No",
        "milestones": [("In 2 days", "Launch communications approval"), ("In 7 days", "Readiness review"),
                       ("In 9 days", "Player announcement scheduling"), ("In 12 days", "Launch day")],
        "latest_update": "Yesterday: Live operations confirmed server-event configuration is on track.",
    },
    "emberline-expedition": {
        "name": "Emberline Expedition", "plan": "PLN-EE Launch", "launch_pack": "SP-EE-LaunchPack-Approved",
        "launch_day": "In 8 days", "missing": "No",
        "milestones": [("Tomorrow", "Final event rewards sign-off"), ("In 6 days", "Readiness review"),
                       ("In 8 days", "Launch day")],
        "latest_update": "2 days ago: Marketing confirmed key art delivery.",
    },
    "moonlit-market": {
        "name": "Moonlit Market", "plan": "PLN-MM Launch", "launch_pack": "SP-MM-LaunchPack-Draft",
        "launch_day": "In 11 days", "missing": "Yes - approved player announcement brief",
        "milestones": [("In 3 days", "Community moderation coverage confirmation"), ("In 8 days", "Readiness review"),
                       ("In 11 days", "Launch day")],
        "latest_update": "Yesterday: Community team still needs the approved announcement brief.",
    },
    "cindercrest-trials": {
        "name": "Cindercrest Trials", "plan": "PLN-CT Launch", "launch_pack": "SP-CT-LaunchPack-Approved",
        "launch_day": "In 14 days", "missing": "No",
        "milestones": [("In 4 days", "Localization handoff"), ("In 9 days", "Readiness review"),
                       ("In 14 days", "Launch day")],
        "latest_update": "Today: All launch dependencies have owners.",
    },
}

TASKS = [
    {"id": "TSK-101", "event": "frostveil-festival", "task": "Confirm server-event configuration",
     "team": "Live operations", "owner": "Elena Voss", "status": "Complete", "reminder": "No", "source": "Planner"},
    {"id": "TSK-102", "event": "frostveil-festival", "task": "Confirm community moderation coverage",
     "team": "Community", "owner": "Priya Nair", "status": "Blocked", "reminder": "Yes", "source": "Planner"},
    {"id": "TSK-103", "event": "frostveil-festival", "task": "Submit final store assets",
     "team": "Marketing", "owner": "Mateo Silva", "status": "Late", "reminder": "Yes", "source": "Planner"},
    {"id": "TSK-104", "event": "frostveil-festival", "task": "Review launch communications",
     "team": "Community", "owner": "Jon Bell", "status": "In progress", "reminder": "No", "source": "Teams"},
    {"id": "TSK-201", "event": "emberline-expedition", "task": "Approve event reward table",
     "team": "Live operations", "owner": "Hana Cho", "status": "In progress", "reminder": "Yes", "source": "Planner"},
    {"id": "TSK-301", "event": "moonlit-market", "task": "Provide approved player announcement brief",
     "team": "Marketing", "owner": "Quinn Harper", "status": "Missing", "reminder": "Yes", "source": "SharePoint"},
    {"id": "TSK-401", "event": "cindercrest-trials", "task": "Complete localization handoff",
     "team": "Live operations", "owner": "Ravi Mehta", "status": "In progress", "reminder": "No",
     "source": "Planner"},
    {"id": "TSK-402", "event": "cindercrest-trials", "task": "Approve player announcement brief",
     "team": "Marketing", "owner": "Quinn Harper", "status": "In progress", "reminder": "Yes", "source": "SharePoint"},
]

ANNOUNCEMENTS = {
    "frostveil-festival": {"messaging": "Join the Frostveil Festival from launch day for limited-time quests, "
                                        "rewards, and community challenges.",
                           "approval": "Approved", "permission": "Not granted - marketing lead sign-off required",
                           "brief": "SP-FVF-AnnouncementBrief-Approved", "missing": "Publishing sign-off"},
    "emberline-expedition": {"messaging": "Emberline Expedition arrives on launch day with new expedition rewards "
                                          "and timed objectives.",
                             "approval": "Approved", "permission": "Granted",
                             "brief": "SP-EE-AnnouncementBrief-Approved", "missing": "Nothing missing"},
    "moonlit-market": {"messaging": "Moonlit Market returns with rotating vendor rewards.",
                       "approval": "Pending review", "permission": "Not granted",
                       "brief": "SP-MM-AnnouncementBrief-Draft", "missing": "Approved player announcement brief"},
    "cindercrest-trials": {"messaging": "Cindercrest Trials opens on launch day with competitive trials and "
                                        "seasonal rewards.",
                           "approval": "Missing approval", "permission": "Not granted",
                           "brief": "SP-CT-AnnouncementBrief-Review", "missing": "Messaging approval"},
}

OPEN_STATUSES = ("Late", "Missing", "Blocked")

BOUNDARY = ("> Read-only synthetic snapshot. No announcement was published, no task or event was changed and no "
            "reminder was sent; every announcement and reminder is a draft for the event owners to approve.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_event(value):
    """Event key or part of its name; empty -> frostveil-festival (the demo event); no match -> None."""
    if not value:
        return "frostveil-festival"
    q = str(value).lower().strip()
    for key, e in EVENTS.items():
        if q in (key, key.replace("-", " ")) or q in e["name"].lower():
            return key
    return None


def _tasks(key):
    return [t for t in TASKS if t["event"] == key]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = ["launch_timeline", "readiness_checklist", "announcement_check", "launch_summary"]


class LiveEventLaunchPlannerAgent(BasicAgent):
    """Seasonal in-game event launch planning agent (read-only, synthetic)."""

    def __init__(self):
        self.name = "LiveEventLaunchPlannerAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call this tool for a seasonal event launch: the milestones "
                "to launch day, which team tasks are open and who owns them, whether the player announcement is "
                "approved and may be published, and what is late, missing or blocked. Call it right away; every "
                "operation has demo defaults."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "launch_timeline for the milestones from communications approval to launch day and the "
                            "first milestone; readiness_checklist for every team task with owner, status and source; "
                            "announcement_check for the player messaging, its approval and publishing permission; "
                            "launch_summary for late, missing and blocked work with draft owner reminders."
                        ),
                    },
                    "event": {
                        "type": "string",
                        "description": "Seasonal event such as Frostveil Festival (the default) or Moonlit Market.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "launch_timeline")
        key = _resolve_event(kwargs.get("event"))
        if key is None:
            return (f"# Unknown Event\n\nNo synthetic seasonal event matches `{kwargs.get('event')}`; no substitute "
                    f"event was used. Events: {', '.join(e['name'] for e in EVENTS.values())}.\n\n{BOUNDARY}")
        handlers = {
            "launch_timeline": self._launch_timeline,
            "readiness_checklist": self._readiness_checklist,
            "announcement_check": self._announcement_check,
            "launch_summary": self._launch_summary,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    def _launch_timeline(self, key) -> str:
        e = EVENTS[key]
        first_when, first_what = e["milestones"][0]
        lines = [
            f"# Launch Timeline - {e['name']}",
            "",
            f"**Launch day:** {e['launch_day']} | **Plan:** {e['plan']} | **Launch pack:** {e['launch_pack']}",
            f"**First milestone:** {first_what} - {first_when.lower()}",
            "",
            "| When | Milestone |",
            "|------|-----------|",
        ]
        lines += [f"| {when} | {what} |" for when, what in e["milestones"]]
        lines += [
            "",
            f"**Latest team update:** {e['latest_update']}",
            f"**Anything missing:** {e['missing']}",
            "",
            BOUNDARY,
        ]
        return "\n".join(lines)

    def _readiness_checklist(self, key) -> str:
        e = EVENTS[key]
        tasks = _tasks(key)
        done = sum(1 for t in tasks if t["status"] == "Complete")
        lines = [f"# Readiness Checklist - {e['name']}", "",
                 f"**Launch day:** {e['launch_day']} | **Tasks complete:** {done} of {len(tasks)}", "",
                 "| Task | Team | Owner | Status | Reminder needed | Source |",
                 "|------|------|-------|--------|-----------------|--------|"]
        lines += [f"| {t['id']} {t['task']} | {t['team']} | {t['owner']} | {t['status']} | {t['reminder']} | "
                  f"{t['source']} |" for t in tasks]
        lines += ["", BOUNDARY]
        return "\n".join(lines)

    def _announcement_check(self, key) -> str:
        e = EVENTS[key]
        a = ANNOUNCEMENTS[key]
        can_publish = a["approval"] == "Approved" and a["permission"] == "Granted"
        lines = [
            f"# Announcement Check - {e['name']}",
            "",
            f"**Messaging approval:** {a['approval']} | **Publish permission:** {a['permission']}",
            f"**Ready to publish:** {'Yes, once launch day scheduling is confirmed' if can_publish else 'No - hold'}",
            f"**Announcement brief:** {a['brief']} | **Anything missing:** {a['missing']}",
            "",
            "## Draft player announcement",
            f"> {a['messaging']}",
            "",
            "> Draft only: the announcement was not published. " + BOUNDARY[2:],
        ]
        return "\n".join(lines)

    def _launch_summary(self, key) -> str:
        e = EVENTS[key]
        tasks = _tasks(key)
        open_items = [t for t in tasks if t["status"] in OPEN_STATUSES]
        counts = {s: sum(1 for t in tasks if t["status"] == s) for s in OPEN_STATUSES}
        lines = [
            f"# Launch Summary - {e['name']}",
            "",
            f"**Launch day:** {e['launch_day']} | **Late:** {counts['Late']} | **Missing:** {counts['Missing']} "
            f"| **Blocked:** {counts['Blocked']}",
            f"**Announcement:** {ANNOUNCEMENTS[key]['approval']}; publish permission "
            f"{ANNOUNCEMENTS[key]['permission'].lower()}",
            "",
        ]
        if open_items:
            lines += ["## Needs attention", "| Task | Owner | Status |", "|------|-------|--------|"]
            lines += [f"| {t['task']} | {t['owner']} ({t['team']}) | {t['status']} |" for t in open_items]
            lines += ["", "## Draft reminders"]
            lines += [f"- To {t['owner']}: \"{t['task']}\" is {t['status'].lower()} for {e['name']}; launch day is "
                      f"{e['launch_day'].lower()}." for t in open_items if t["reminder"] == "Yes"]
        else:
            lines.append("**No late, missing or blocked work** is recorded for this event.")
        lines += ["", "> Draft only: no reminder was sent. " + BOUNDARY[2:]]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = LiveEventLaunchPlannerAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
