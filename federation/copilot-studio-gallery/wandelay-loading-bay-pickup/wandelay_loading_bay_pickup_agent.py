"""Retained-snapshot queue arithmetic from loading_dock_reasoning.py.

The original calculate_queue_status uses 30 seconds per truck and whole
completed trucks. This slice uses explicit offset-aware observation, current,
and arrival timestamps, never the wall clock or a fresh dock snapshot.
Weather suitability, dock selection, priority verification, and explanations
stay with the AI planning step. The initial queue is its already-adjusted queue.
The source README's ORD-10502 sample reference is retained unchanged.
"""
import json
from datetime import datetime, timedelta, timezone

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/wandelay-loading-bay-pickup",
    "version": "0.1.0", "display_name": "Loading Queue Follow-up",
    "description": "Recalculates queue progress from a retained observation without changing the dock.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution wandelay-loading-bay-pickup",
    "quality_tier": "experimental", "category": "logistics",
    "tags": ["queue", "eta"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
QUEUE_SECONDS_PER_TRUCK = 30
SAMPLE = {"shipment": "ORD-10502", "dock": "Fictional Contoso dock 1", "initial_trucks_ahead": 8,
          "queue_observed_at": "2026-11-02T10:00:00-05:00", "now": "2026-11-02T10:01:00-05:00",
          "arrival": "2026-11-02T10:20:00-05:00"}


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Every timestamp needs an explicit UTC offset.")
    return result


def evaluate(data):
    initial = data["initial_trucks_ahead"]
    if type(initial) is not int or initial < 0:
        raise ValueError("initial_trucks_ahead must be a nonnegative whole number.")
    observed, current, arrival = (timestamp(data[field]) for field in ("queue_observed_at", "now", "arrival"))
    elapsed = max(0, int((current.astimezone(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds()))
    completed = min(initial, elapsed // QUEUE_SECONDS_PER_TRUCK)
    remaining = initial - completed
    wait = remaining * QUEUE_SECONDS_PER_TRUCK
    eta = max(0, int((arrival.astimezone(timezone.utc) - current.astimezone(timezone.utc)).total_seconds()))
    ready = current + timedelta(seconds=wait)
    return {"shipment": data["shipment"], "dock": data["dock"], "queue_observed_at": data["queue_observed_at"],
            "queue_seconds_per_truck": QUEUE_SECONDS_PER_TRUCK, "completed_trucks": completed,
            "trucks_ahead": remaining, "expected_wait_seconds": wait,
            "estimated_dock_ready_time": ready.isoformat(), "remaining_eta_seconds": eta,
            "eta_margin_seconds": eta - wait, "ready_before_arrival": eta >= wait,
            "queue_status": "ready" if remaining == 0 else "in_progress",
            "snapshot_refreshed": False, "assignment_changed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Loading Queue Follow-up, a synthetic logistics pilot recalculating queue progress from a retained dock observation.

Use only the bundled fictional shipment ORD-10502, dock, queue count and explicit observation, current and arrival timestamps. Never match them to a real shipment, driver or loading assignment.

Answer with the queue tool, not from memory. Lead with trucks ahead, expected wait and arrival margin, quote shipment ids and timestamps exactly, and keep the original dock and observation instead of claiming a refreshed snapshot.

You never read live weather, choose a dock, verify priority or change an assignment. A logistics planner reviews the initial adjusted queue, weather suitability and priority before using the follow-up estimate."""

OPERATION_GUIDE = {
    "queue_followup": {
        "title": "Retained queue follow-up",
        "when": "Use when someone asks how a retained loading queue has progressed at thirty seconds per truck and whether the same dock should be ready before arrival.",
        "ask": "How has the loading queue for shipment ORD-10502 moved, and will dock 1 be ready before the truck arrives?",
    },
}

CARRIED = [
    "Checks weather suitability, selects the dock, verifies priority and explains the loading plan through the original solution's planning AI step.",
    "Retrieves the initial dock snapshot and shipment context before the original solution's loading_dock_reasoning.py queue follow-up.",
]


class WandelayLoadingBayPickupAgent(BasicAgent):
    def __init__(self):
        self.name = "LoadingQueueFollowup"
        self.metadata = {"name": self.name, "description": "Check a retained loading queue. Optional payload_json: shipment, dock, initial_trucks_ahead, queue_observed_at, now, arrival (offset-aware ISO times). Initial queue already includes verified priority outcome. With no payload_json it uses the sample on file: shipment ORD-10502 at Contoso dock 1.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to queue_followup."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "queue_followup") not in OPERATION_GUIDE:
                raise ValueError("operation must be queue_followup.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(WandelayLoadingBayPickupAgent().perform())
