"""Valid-ballot scoring from MeetingCoordinator workflow, Evaluate votes.

Five ranks map to 5,4,3,2,1 points; Required voters weigh 3, Optional 1,
unlisted voters 0. No required voter may rank an acceptable slot 4th or 5th.
Ties use required top-two support, then earliest time.
Invalid-ballot repair, fallback when no slot is acceptable, task interpretation,
availability search, and meeting creation stay with the AI coordinator.
This returns a provisional recommendation, not a booked meeting.
"""
import json
from datetime import datetime, timezone

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/meeting-coordinator",
    "version": "0.1.0", "display_name": "Meeting Vote Calculator",
    "description": "Scores valid five-slot ballots using documented attendee weights.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution meeting-coordinator",
    "quality_tier": "experimental", "category": "productivity",
    "tags": ["meeting", "voting"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"slots": ["2026-11-02T09:00:00+00:00", "2026-11-02T10:00:00+00:00",
                    "2026-11-03T09:00:00+00:00", "2026-11-03T10:00:00+00:00", "2026-11-04T09:00:00+00:00"],
          "required": ["lead@contoso.example"], "optional": ["observer@contoso.example"],
          "votes": [{"email": "lead@contoso.example", "ranks": [1, 2, 3, 4, 5]},
                    {"email": "observer@contoso.example", "ranks": [5, 1, 2, 3, 4]}]}


def evaluate(data):
    slots = data["slots"]
    if not isinstance(slots, list) or len(slots) != 5:
        raise ValueError("Exactly five slots are required.")
    times = [datetime.fromisoformat(slot.replace("Z", "+00:00")) for slot in slots]
    if any(value.tzinfo is None for value in times) or len(set(times)) != 5:
        raise ValueError("Slots must be distinct timestamps with UTC offsets.")
    required = {email.strip().casefold() for email in data["required"]}
    optional = {email.strip().casefold() for email in data["optional"]}
    if required & optional:
        raise ValueError("Required and optional attendee lists must not overlap.")
    scores, support, acceptable = [0] * 5, [0] * 5, [True] * 5
    seen, ignored = set(), []
    for vote in data["votes"]:
        email = vote["email"].strip().casefold()
        if email in seen:
            raise ValueError("Multiple ballots for one voter require coordinator review.")
        seen.add(email)
        weight = 3 if email in required else 1 if email in optional else 0
        if not weight:
            ignored.append(email)
            continue
        ranks = vote["ranks"]
        if not isinstance(ranks, list) or len(ranks) != 5 or any(type(rank) is not int for rank in ranks) or sorted(ranks) != [1, 2, 3, 4, 5]:
            raise ValueError("Invalid ballot; the AI coordinator must resolve repeated or missing ranks before calculation.")
        for index, rank in enumerate(ranks):
            scores[index] += (6 - rank) * weight
            if weight == 3:
                support[index] += rank <= 2
                acceptable[index] = acceptable[index] and rank <= 3
    missing = sorted((required | optional) - seen)
    candidates = [i for i in range(5) if acceptable[i]]
    winner = min(candidates, key=lambda i: (-scores[i], -support[i], times[i].astimezone(timezone.utc))) if candidates and not missing and seen - set(ignored) else None
    return {"scores": scores, "required_top_two_support": support, "acceptable": acceptable,
            "selected_slot": slots[winner] if winner is not None else None,
            "missing_votes": missing, "ignored_voters": ignored, "booked": False,
            "next_step": "Review provisional selection" if winner is not None else "Coordinator review or another voting round"}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Meeting Vote Calculator, a synthetic scheduling pilot scoring five-slot ballots using required and optional attendee weights.

Use only the bundled fictional five meeting slots, attendee lists and ranked ballots. Never match them to a real attendee, calendar or vote.

Answer with the vote tool, not from memory. Lead with the provisional selection or need for another round, quote slot timestamps and voter ids exactly, and retain missing votes, required-attendee acceptability and the documented tie breakers.

You never repair ambiguous ballots silently, find live availability or book a meeting. A meeting coordinator reviews invalid ballots, missing votes and any provisional selection before scheduling."""

OPERATION_GUIDE = {
    "score_votes": {
        "title": "Meeting ballot scoring",
        "when": "Use when someone asks how five-slot ranked ballots score, which slots required voters accept, or which provisional slot wins the documented tie breakers.",
    },
}

CARRIED = [
    "Interprets scheduling tasks, finds availability, repairs invalid ballots and handles no-acceptable-slot fallbacks through the original solution's coordinator.",
    "Collects ballots and creates the reviewed meeting through the original solution's MeetingCoordinator workflow.",
]


class MeetingCoordinatorAgent(BasicAgent):
    def __init__(self):
        self.name = "MeetingVoteCalculator"
        self.metadata = {"name": self.name, "description": "Score five valid ranked slots. Optional payload_json: slots (5 offset-aware ISO times), required and optional email lists, votes [{email,ranks:[1..5 permutation]}].",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to score_votes."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "score_votes") not in OPERATION_GUIDE:
                raise ValueError("operation must be score_votes.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(MeetingCoordinatorAgent().perform())
