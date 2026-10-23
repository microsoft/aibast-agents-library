"""
Campaign Delivery Optimizer Agent for Media Ad Sales.

Read-only campaign delivery support for a media company's ad sales and ad operations teams, built on a synthetic
snapshot of four active advertiser campaigns in the current week: each campaign's delivered reach against its
weekly plan with the delivery gap explained, the placements with extra reach available this week, and the drafted
recommendation waiting for the sales lead's approval. Every recommendation is a draft; nothing is booked or shared
with an advertiser.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/campaign-delivery-optimizer",
    "version": "1.0.0",
    "display_name": "Campaign Delivery Optimizer Agent",
    "description": "Help ad sales and ad operations teams keep advertiser campaigns on plan from a synthetic weekly delivery snapshot: each campaign's delivered reach against plan with the gap explained, the placements with extra reach available this week, and the drafted recommendation for the sales lead to approve. The agent never books inventory, changes a campaign or placement, or shares anything with an advertiser; the sales lead approves every recommendation through future authenticated tools.",
    "author": "AIBAST",
    "tags": ["media", "advertising", "ad-sales", "ad-operations", "campaign-delivery"],
    "category": "telecom_media_gaming",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data (fixed demo week: four active advertiser campaigns)
# ---------------------------------------------------------------------------

CAMPAIGNS = {
    "harborlight": {
        "name": "Harborlight Streaming Campaign", "id": "CMP-2041", "sales_lead": "Maya Chen",
        "planned_weekly_reach": "235,000", "delivered_reach": "192,700", "variance": "18% below plan",
        "at_risk": "Yes", "delivery_status": "At risk", "missing": "No",
        "reason": "Delivered reach is 18% below planned weekly reach as of this week's delivery read.",
    },
    "northfield": {
        "name": "Northfield Culture Campaign", "id": "CMP-2038", "sales_lead": "Jon Bell",
        "planned_weekly_reach": "120,000", "delivered_reach": "124,800", "variance": "4% above plan",
        "at_risk": "No", "delivery_status": "On track", "missing": "No",
        "reason": "Delivered reach is tracking 4% above planned weekly reach as of this week's delivery read.",
    },
    "cedar-view": {
        "name": "Cedar View Campaign", "id": "CMP-2045", "sales_lead": "Priya Nair",
        "planned_weekly_reach": "80,000", "delivered_reach": "Incomplete", "variance": "Cannot be compared",
        "at_risk": "Yes", "delivery_status": "Pending review", "missing": "Yes - current-week delivery data",
        "reason": "Delivery data for the current week is incomplete; planned weekly reach cannot be fully compared.",
    },
    "ridgeway-audio": {
        "name": "Ridgeway Audio Campaign", "id": "CMP-2033", "sales_lead": "Elena Ruiz",
        "planned_weekly_reach": "150,000", "delivered_reach": "147,000", "variance": "2% below plan",
        "at_risk": "No", "delivery_status": "On track", "missing": "No",
        "reason": "Delivered reach is within 2% of planned weekly reach as of this week's delivery read.",
    },
}

PLACEMENTS = [
    {"id": "INV-501", "campaign": "harborlight", "placement": "Streaming Home Screen Takeover",
     "extra_reach": "42,000", "status": "Available"},
    {"id": "INV-502", "campaign": "harborlight", "placement": "Weekend Premium Video Pre-roll",
     "extra_reach": "0", "status": "Sold out"},
    {"id": "INV-511", "campaign": "northfield", "placement": "Culture Newsletter Sponsorship",
     "extra_reach": "15,500", "status": "Available"},
    {"id": "INV-520", "campaign": "cedar-view", "placement": "Local News Mid-roll",
     "extra_reach": "8,200", "status": "Pending confirmation"},
    {"id": "INV-531", "campaign": "ridgeway-audio", "placement": "Podcast Network Host-read",
     "extra_reach": "27,000", "status": "Available"},
]

RECOMMENDATIONS = {
    "harborlight": {"draft": "Propose Streaming Home Screen Takeover for an estimated 42,000 additional reach this "
                             "week to address the 18% weekly reach gap.",
                    "approval_status": "Pending sales lead approval", "missing": "Nothing missing"},
    "northfield": {"draft": "No additional reach recommendation is needed because delivery is on track.",
                   "approval_status": "Approved", "missing": "Nothing missing"},
    "cedar-view": {"draft": "Recommendation cannot be finalized until current-week delivery data is provided.",
                   "approval_status": "Blocked - missing delivery data", "missing": "Current-week delivery data"},
    "ridgeway-audio": {"draft": "Keep the current placement mix because delivery is within the planned weekly range.",
                       "approval_status": "Pending sales lead approval", "missing": "Nothing missing"},
}

BOUNDARY = ("> Read-only synthetic snapshot. No inventory was booked, no campaign or placement was changed and "
            "nothing was shared with an advertiser; every recommendation is a draft for the sales lead to approve.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_campaign(value):
    """Campaign key, id or part of its name; empty -> harborlight (the demo campaign); no match -> None."""
    if not value:
        return "harborlight"
    q = str(value).lower().strip().replace(" campaign", "")
    for key, c in CAMPAIGNS.items():
        if q in (key, key.replace("-", " "), c["id"].lower()) or q in c["name"].lower():
            return key
    return None


def _placements(key):
    return [p for p in PLACEMENTS if p["campaign"] == key]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = ["campaign_risk", "available_reach", "approval_recommendation"]


class CampaignDeliveryOptimizerAgent(BasicAgent):
    """Weekly campaign delivery agent for media ad sales (read-only, synthetic)."""

    def __init__(self):
        self.name = "CampaignDeliveryOptimizerAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                __manifest__["description"] + " Always call this tool for an advertiser campaign's delivery: "
                "whether it is at risk this week and why, which placements have extra reach to close the gap, and "
                "the recommendation drafted for the sales lead. Call it right away; every operation has demo "
                "defaults."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "campaign_risk for delivered reach against the weekly plan and the reason a campaign is "
                            "or is not at risk; available_reach for placements with extra reach this week and their "
                            "inventory status; approval_recommendation for the drafted recommendation, its approval "
                            "status, the sales lead and anything missing."
                        ),
                    },
                    "campaign": {
                        "type": "string",
                        "description": "Campaign such as Harborlight Streaming Campaign (the default) or Cedar View.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "campaign_risk")
        key = _resolve_campaign(kwargs.get("campaign"))
        if key is None:
            return (f"# Unknown Campaign\n\nNo synthetic campaign matches `{kwargs.get('campaign')}`; no substitute "
                    f"campaign was used. Campaigns: {', '.join(c['name'] for c in CAMPAIGNS.values())}."
                    f"\n\n{BOUNDARY}")
        handlers = {
            "campaign_risk": self._campaign_risk,
            "available_reach": self._available_reach,
            "approval_recommendation": self._approval_recommendation,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(key)

    def _campaign_risk(self, key) -> str:
        c = CAMPAIGNS[key]
        at_risk = sum(1 for x in CAMPAIGNS.values() if x["at_risk"] == "Yes")
        lines = [
            f"# Campaign Risk - {c['name']}",
            "",
            f"**Campaign:** {c['id']} | **Sales lead:** {c['sales_lead']} | **Delivery status:** "
            f"{c['delivery_status']} | **At risk this week:** {c['at_risk']}",
            "",
            "| Planned weekly reach | Delivered reach | Variance |",
            "|----------------------|-----------------|----------|",
            f"| {c['planned_weekly_reach']} | {c['delivered_reach']} | {c['variance']} |",
            "",
            f"**Why:** {c['reason']}",
            f"**Anything missing:** {c['missing']}",
            f"**Across all {len(CAMPAIGNS)} active campaigns:** {at_risk} at risk this week.",
            "",
            BOUNDARY,
        ]
        return "\n".join(lines)

    def _available_reach(self, key) -> str:
        c = CAMPAIGNS[key]
        rows = _placements(key)
        lines = [f"# Available Reach - {c['name']}", "",
                 f"**Delivery gap:** {c['variance']} | **Delivery status:** {c['delivery_status']}", ""]
        if rows:
            lines += ["| Inventory | Placement | Extra reach this week | Inventory status |",
                      "|-----------|-----------|-----------------------|------------------|"]
            lines += [f"| {p['id']} | {p['placement']} | {p['extra_reach']} | {p['status']} |" for p in rows]
        else:
            lines.append("**No placements** with extra reach are recorded for this campaign this week.")
        lines += ["", BOUNDARY]
        return "\n".join(lines)

    def _approval_recommendation(self, key) -> str:
        c = CAMPAIGNS[key]
        r = RECOMMENDATIONS[key]
        lines = [
            f"# Approval Recommendation - {c['name']}",
            "",
            f"**Sales lead:** {c['sales_lead']} | **Approval status:** {r['approval_status']}",
            f"**Anything missing:** {r['missing']}",
            "",
            "## Draft recommendation",
            f"- {r['draft']}",
            f"- Basis: {c['reason']}",
            "",
            "> Draft only: nothing was booked or shared with the advertiser. " + BOUNDARY[2:],
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = CampaignDeliveryOptimizerAgent()
    for op in OPERATIONS:
        print(f"\n{'=' * 60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
