"""Item notification view from README.md, How it works.

Formats only supplied current-item fields and its direct link. The recipient
comes only from a separately supplied connected-user profile, never item data.
Channel results remain independent. Retrieval, relevance judgment, natural
language summaries, and actual delivery stay with the AI and authorized tools.
No live delivery is claimed. All example records and addresses are fictional.
"""
import html
import json
import re

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/sharepoint-list-update-notifier",
    "version": "0.1.0", "display_name": "List Change Notification View",
    "description": "Formats a supplied item for the connected user and reports channel outcomes.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution sharepoint-list-update-notifier",
    "quality_tier": "experimental", "category": "productivity",
    "tags": ["sharepoint", "notification"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"item": {"Title": "Contoso stock check", "field_2": "In progress", "field_3": "Warehouse"},
          "item_link": "https://contoso.example/lists/stock/1",
          "connected_user": {"mail": "operator@contoso.example"},
          "channel_results": {"Teams": "not-applicable", "email": "not-applicable"}}


def evaluate(data):
    profile, item = data["connected_user"], data["item"]
    recipient = profile.get("mail") or profile.get("userPrincipalName")
    if not isinstance(recipient, str) or not recipient.strip():
        raise ValueError("Connected-user profile needs mail or userPrincipalName.")
    if not isinstance(item, dict):
        raise ValueError("item must contain the current retrieved fields.")
    link = data["item_link"]
    if not isinstance(link, str) or not re.fullmatch(r"https?://[^/\s?#]+(?:[/?#][^\s]*)?", link):
        raise ValueError("item_link must be an absolute web link supplied by the source.")
    outcomes = data["channel_results"]
    if not isinstance(outcomes, dict) or set(outcomes) != {"Teams", "email"} or any(
            result not in ("sent", "failed", "not-applicable") for result in outcomes.values()):
        raise ValueError("Supply independent Teams and email results: sent, failed, or not-applicable.")
    fields = {name: item[name] for name in ("Title", "field_2", "field_3") if name in item}
    body = "<dl>" + "".join("<dt>" + html.escape(name) + "</dt><dd>" + html.escape(str(value)) + "</dd>" for name, value in fields.items()) + "</dl>"
    body += '<p><a href="' + html.escape(link, quote=True) + '">Open item</a></p>'
    return {"title": item.get("Title"), "recipient": recipient, "html": body,
            "channel_results": outcomes, "outcome_source": "Caller-supplied; no delivery attempted by this cartridge.",
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are List Change Notification View, a synthetic productivity pilot formatting a supplied current item for the connected user.

Use only the bundled fictional stock-check item, direct link, user profile and independent channel outcomes. Never match them to a real list item, employee or delivery record.

Answer with the notification view tool, not from memory. Lead with the item and recipient, quote recorded fields and ids exactly, take the address only from the connected-user profile and label delivery outcomes as caller-supplied.

You never retrieve a live item, choose recipients from item content or send a notification. The connected user reviews the current fields, direct link and separate channel results before relying on delivery claims."""

OPERATION_GUIDE = {
    "notification_view": {
        "title": "List item notification view",
        "when": "Use when someone asks for a current-item notification preview addressed only to the connected user, with independent channel outcomes.",
        "ask": "Preview the update notice for the Contoso stock check list item, addressed to me.",
    },
}

CARRIED = [
    "Retrieves the changed SharePoint item and connected-user profile through the original solution's list notification connections.",
    "Judges relevance, summarizes the item and delivers independent Teams and email notifications through the original solution's agent and delivery actions.",
]


class SharepointListUpdateNotifierAgent(BasicAgent):
    def __init__(self):
        self.name = "ListNotificationView"
        self.metadata = {"name": self.name, "description": "Format a retrieved item. Optional payload_json: item, item_link, connected_user {mail or userPrincipalName}, channel_results {Teams,email} each sent/failed/not-applicable. With no payload_json it uses the sample on file: the Contoso stock check list item.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to notification_view."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "notification_view") not in OPERATION_GUIDE:
                raise ValueError("operation must be notification_view.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(SharepointListUpdateNotifierAgent().perform())
