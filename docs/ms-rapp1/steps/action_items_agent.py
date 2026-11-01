"""ActionItems: an ms-rapp/1 Step that is also a plain rapp/1 agent.

Drop this file into a Brainstem's agents/ folder and it loads like any other agent. RAPP Runtime serves the same
file at POST /api/lens/action-items (ROUTE below), and the generated openapi.json lets a Microsoft Foundry agent call
it as an OpenAPI tool. One file, three hosts, no changes.

The task is deterministic on purpose, so the compatibility tests can run it without a model: it reads meeting notes
and returns the lines that assign work.
"""

import json
import re

try:
    from agents.basic_agent import BasicAgent
except ImportError:  # outside a Brainstem, beside basic_agent.py
    from basic_agent import BasicAgent

# ms-rapp/1 Step fields. A rapp/1 host ignores them; RAPP Runtime and the OpenAPI build read them.
ROUTE = "action-items"
RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"owner": {"type": "string"}, "task": {"type": "string"}},
                "required": ["owner", "task"],
            },
        },
    },
    "required": ["items"],
}

# "Action: Dana: send the sheet" names an owner; "TODO: book the follow-up" does not.
_ITEM = re.compile(r"^\s*(?:[-*]\s*)?(?:action|todo|ai)\s*:\s*(?:@?(?P<owner>[A-Za-z][\w .'-]{0,40}?)\s*:\s*)?(?P<task>.+)$",
                   re.IGNORECASE)


class ActionItemsAgent(BasicAgent):
    def __init__(self):
        self.name = "ActionItems"
        self.metadata = {
            "name": self.name,
            "description": "Lists the action items in meeting notes: each line that starts with 'Action:', "
                           "'TODO:' or 'AI:', with its owner when one is named.",
            "parameters": {
                "type": "object",
                "properties": {"notes": {"type": "string", "description": "The meeting notes, as plain text."}},
                "required": ["notes"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        items = []
        for line in str(kwargs.get("notes", "")).splitlines():
            match = _ITEM.match(line)
            if match:
                items.append({"owner": (match.group("owner") or "Unassigned").strip(),
                              "task": match.group("task").strip()})
        return json.dumps({"items": items})
