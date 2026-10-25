"""
Content Launch Clearance Agent for Media & Entertainment.

Read-only launch clearance support for a media company's programming, distribution and rights teams, built on a
synthetic snapshot of five titles requested for the company's owned streaming service: whether each title is
cleared in the requested territory with the exact contract clause cited, the distribution window and any holdback
that blocks an earlier launch date, and whether the request is ready for rights-team approval. Every approval
request is a draft for the rights team to review.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/content-launch-clearance",
    "version": "1.0.0",
    "display_name": "Content Launch Clearance Agent",
    "description": "Help programming, distribution and rights teams confirm where, when and on which platform a title can launch from a synthetic rights snapshot: the launch clearance by territory and platform with the exact contract clause cited, the distribution window and any holdback that blocks an earlier date, and whether the request is ready for rights-team approval. The agent never schedules or publishes a title, changes a contract or submits an approval; the rights team approves every launch through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["media", "streaming", "rights-and-clearances", "content-distribution", "launch-planning"],
    "category": "telecom_media_gaming",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (fixed demo day: five titles requested for the owned streaming service)
# ---------------------------------------------------------------------------

TITLES = {
    "silver-harbor": {
        "name": "Silver Harbor", "territory": "UK", "platform": "Owned streaming service",
        "requested_launch": "Not yet confirmed",
        "contract": "UK Rights Agreement SH-UK-2026", "clause": "3.1", "contract_status": "Approved",
        "clause_text": "Exclusive UK subscription streaming rights are granted for 24 months from the end of the "
                       "theatrical holdback.",
        "clearance": "Cleared from the end of the theatrical holdback (in 24 days)",
    },
    "paper-lantern": {
        "name": "Paper Lantern", "territory": "Canada", "platform": "Owned streaming service",
        "requested_launch": "In 33 days",
        "contract": "Canada Rights Agreement PL-CA-2026", "clause": "2.4", "contract_status": "Approved",
        "clause_text": "Canadian subscription streaming rights commence at the start of the window; no earlier "
                       "digital launch is permitted.",
        "clearance": "Not cleared until the window opens (in 40 days)",
    },
    "meadow-current": {
        "name": "Meadow Current", "territory": "Australia", "platform": "Owned streaming service",
        "requested_launch": "In 21 days",
        "contract": "ANZ Rights Agreement MC-ANZ-2026", "clause": "4.2", "contract_status": "Approved",
        "clause_text": "Non-exclusive subscription streaming rights in Australia commence at the start of the window.",
        "clearance": "Cleared from the window opening (in 14 days)",
    },
    "northern-signal": {
        "name": "Northern Signal", "territory": "UK", "platform": "Owned streaming service",
        "requested_launch": "Not yet confirmed",
        "contract": "UK Rights Agreement NS-UK-2026", "clause": "3.1", "contract_status": "Pending review",
        "clause_text": "UK subscription streaming rights are subject to an unsigned amendment.",
        "clearance": "Clearance unavailable",
    },
    "driftwood-lane": {
        "name": "Driftwood Lane", "territory": "UK", "platform": "Owned streaming service",
        "requested_launch": "Not yet confirmed",
        "contract": "UK Rights Agreement DL-UK-2026", "clause": "6.1", "contract_status": "Pending review",
        "clause_text": "The licensed territory list excludes the UK until a territory amendment is signed.",
        "clearance": "Clearance unavailable",
    },
}

WINDOWS = {
    "silver-harbor": {"window": "Exclusive subscription streaming", "opens": "In 24 days", "runs": "24 months",
                      "holdback": "Theatrical holdback",
                      "restriction": "UK launch must not occur before the theatrical holdback ends in 24 days.",
                      "earliest_launch": "In 24 days"},
    "paper-lantern": {"window": "Subscription streaming", "opens": "In 40 days", "runs": "Not stated in the clause",
                      "holdback": "No earlier digital launch",
                      "restriction": "Canadian launch must not occur before the window opens in 40 days.",
                      "earliest_launch": "In 40 days"},
    "meadow-current": {"window": "Non-exclusive subscription streaming", "opens": "In 14 days",
                       "runs": "Not stated in the clause", "holdback": "None",
                       "restriction": "No scheduling restriction after the window opens in 14 days.",
                       "earliest_launch": "In 14 days"},
    "northern-signal": {"window": "Subscription streaming (subject to amendment)", "opens": "Not set",
                        "runs": "Not set", "holdback": "Unsigned contract amendment",
                        "restriction": "Launch blocked while contract amendment is unsigned.",
                        "earliest_launch": "None until the amendment is signed"},
    "driftwood-lane": {"window": "Subscription streaming (territory pending)", "opens": "Not set",
                       "runs": "Not set", "holdback": "Territory amendment",
                       "restriction": "Launch is blocked pending a territory amendment.",
                       "earliest_launch": "None until the territory amendment is signed"},
}

READINESS = {
    "silver-harbor": {"missing": ["Confirmed requested UK launch date"], "rights_status": "Pending submission",
                      "reviewer": "Helena Brooks", "next_step": "Programming confirms the UK launch date on or "
                      "after the holdback end, then the request goes to the rights team."},
    "paper-lantern": {"missing": [], "rights_status": "Pending rights approval", "reviewer": "Tomas Reyes",
                      "next_step": "Move the requested launch from 33 days out to the window opening in 40 days "
                      "before the rights team approves."},
    "meadow-current": {"missing": [], "rights_status": "Approved", "reviewer": "Tomas Reyes",
                       "next_step": "No rights action needed; programming may schedule from the window opening."},
    "northern-signal": {"missing": ["Approved contract amendment", "Requested launch date"],
                        "rights_status": "On hold", "reviewer": "Helena Brooks",
                        "next_step": "Rights team obtains the signed amendment before any launch date is set."},
    "driftwood-lane": {"missing": ["Signed territory amendment", "Requested launch date"],
                       "rights_status": "On hold", "reviewer": "Helena Brooks",
                       "next_step": "Rights team obtains the signed territory amendment before any launch date is set."},
}

BOUNDARY = ("> Read-only synthetic snapshot. No title was scheduled or published, no contract was changed and no "
            "approval was submitted; every approval request is a draft for the rights team to review.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_title(value):
    """Title key or part of its name; empty -> silver-harbor (the demo title); no match -> None."""
    if not value:
        return "silver-harbor"
    q = str(value).lower().strip()
    for key, t in TITLES.items():
        if q in (key, key.replace("-", " ")) or q in t["name"].lower():
            return key
    return None


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = ["launch_clearance", "distribution_window", "approval_readiness"]


class ContentLaunchClearanceAgent(BasicAgent):
    """Launch clearance agent for owned streaming launches (read-only, synthetic)."""

    def __init__(self):
        self.name = "ContentLaunchClearanceAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call this tool for a title's launch rights: whether it is "
                "cleared in the requested territory and on the owned streaming service, which contract clause says "
                "so, which window and holdback apply, and what is still missing before rights approval. Call it "
                "right away; every operation has demo defaults."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "launch_clearance for whether the title is cleared in its territory and on the owned "
                            "streaming service, with the contract clause cited; distribution_window for the rights "
                            "window, holdbacks and the earliest open launch date; approval_readiness for what is "
                            "missing and whether the request is ready for rights-team approval, with a draft request."
                        ),
                    },
                    "title": {
                        "type": "string",
                        "description": "Title such as Silver Harbor (the default), Paper Lantern or Northern Signal.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "launch_clearance")
        key = _resolve_title(kwargs.get("title"))
        if key is None:
            return (f"# Unknown Title\n\nNo synthetic title matches `{kwargs.get('title')}`; no substitute title "
                    f"was used. Titles: {', '.join(t['name'] for t in TITLES.values())}.\n\n{BOUNDARY}")
        handlers = {
            "launch_clearance": self._launch_clearance,
            "distribution_window": self._distribution_window,
            "approval_readiness": self._approval_readiness,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    def _launch_clearance(self, key) -> str:
        t = TITLES[key]
        lines = [
            f"# Launch Clearance - {t['name']}",
            "",
            f"**Territory:** {t['territory']} | **Platform:** {t['platform']} | **Requested launch:** "
            f"{t['requested_launch']}",
            "",
            f"**Clearance:** {t['clearance']}",
            "",
            "## Contract term cited",
            f"- **Document:** {t['contract']} (contract status: {t['contract_status']})",
            f"- **Clause {t['clause']}:** \"{t['clause_text']}\"",
            "",
            f"**Restriction:** {WINDOWS[key]['restriction']}",
            "",
            BOUNDARY,
        ]
        return "\n".join(lines)

    def _distribution_window(self, key) -> str:
        t = TITLES[key]
        w = WINDOWS[key]
        lines = [
            f"# Distribution Window - {t['name']}",
            "",
            f"**Territory:** {t['territory']} | **Platform:** {t['platform']}",
            "",
            "| Window | Opens | Runs | Holdback | Earliest launch |",
            "|--------|-------|------|----------|-----------------|",
            f"| {w['window']} | {w['opens']} | {w['runs']} | {w['holdback']} | {w['earliest_launch']} |",
            "",
            f"**Restriction:** {w['restriction']}",
            f"**Source:** {t['contract']}, clause {t['clause']}",
            "",
            BOUNDARY,
        ]
        return "\n".join(lines)

    def _approval_readiness(self, key) -> str:
        t = TITLES[key]
        r = READINESS[key]
        ready = not r["missing"] and t["contract_status"] == "Approved"
        lines = [
            f"# Approval Readiness - {t['name']}",
            "",
            f"**Rights approval status:** {r['rights_status']} | **Rights reviewer:** {r['reviewer']} "
            f"(Rights & Clearances Lead)",
            f"**Ready for rights-team approval:** {'Yes' if ready else 'No'}",
            "",
            "## Still missing",
        ]
        lines += [f"- {m}" for m in r["missing"]] or ["- Nothing missing"]
        lines += [
            "",
            "## Draft approval request",
            f"- Title: {t['name']} | Territory: {t['territory']} | Platform: {t['platform']}",
            f"- Clearance: {t['clearance']} ({t['contract']}, clause {t['clause']})",
            f"- Next step: {r['next_step']}",
            "",
            "> Draft only: no approval was submitted. " + BOUNDARY[2:],
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = ContentLaunchClearanceAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
