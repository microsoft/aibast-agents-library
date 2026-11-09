"""Remembered-idea view for the gallery's Oddly brainstorming canvas.

The README describes brainstorming, jotting down ideas, and remembering good
ones. This is the smallest offline slice: show and search supplied remembered
ideas, in supplied order. Creative conversation, deciding what to remember,
native authentication, and persistent memory stay with the AI and managed app.
Nothing is stored here. All bundled ideas are fictional.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/oddly",
    "version": "0.1.0", "display_name": "Remembered Ideas View",
    "description": "Shows and searches supplied remembered ideas without pretending to chat.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution oddly",
    "quality_tier": "experimental", "category": "creativity",
    "tags": ["ideas", "view"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"ideas": [{"id": "I1", "text": "Contoso could reserve a quiet hour for planning."},
                    {"id": "I2", "text": "Northwind could keep a shared handoff notebook."}], "search": ""}


def evaluate(data):
    ideas, search = data["ideas"], data.get("search", "")
    if not isinstance(ideas, list) or not isinstance(search, str):
        raise ValueError("ideas must be a list and search must be text.")
    seen = set()
    for idea in ideas:
        if not isinstance(idea, dict) or not isinstance(idea.get("text"), str) or not idea["text"].strip() or not isinstance(idea.get("id"), str) or not idea["id"] or idea["id"] in seen:
            raise ValueError("Ideas need distinct nonempty string IDs and nonempty text.")
        seen.add(idea["id"])
    rows = [idea for idea in ideas if search.casefold() in idea["text"].casefold()]
    return {"remembered_ideas": rows, "shown": len(rows), "total": len(ideas),
            "scope": "Supplied memory view only; no brainstorming or persistent writes.", "stored": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Remembered Ideas View, a synthetic creativity pilot showing and searching a small remembered-ideas collection.

Use only the bundled fictional ideas I1 and I2 about a quiet planning hour and a shared handoff notebook. Never match them to a real person's thoughts, organization or memory.

Answer with the ideas view tool, not from memory. Lead with matching ideas and the shown count, quote idea ids and text exactly, and preserve the supplied order.

You never claim to brainstorm, authenticate a person or save a memory from this view. The idea owner reviews what is worth retaining and confirms any persistent change in the separate app."""

OPERATION_GUIDE = {
    "ideas_view": {
        "title": "Remembered ideas view",
        "when": "Use when someone wants to see remembered ideas or search their text while preserving the recorded order.",
    },
}

CARRIED = [
    "Brainstorms conversationally and helps decide what to remember through the original solution's Oddly canvas.",
    "Authenticates the user and persists remembered ideas through the original solution's managed app.",
]


class OddlyAgent(BasicAgent):
    def __init__(self):
        self.name = "RememberedIdeasView"
        self.metadata = {"name": self.name, "description": "Show remembered ideas. Optional payload_json: ideas [{id,text}], optional search text. No ideas are saved.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to ideas_view."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "ideas_view") not in OPERATION_GUIDE:
                raise ValueError("operation must be ideas_view.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(OddlyAgent().perform())
