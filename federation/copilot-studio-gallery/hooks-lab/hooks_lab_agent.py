"""Exact prompt rewrite from README.md, What you can try.

The three exact lowercase demo strings become [redacted]; all other text is
preserved. Weather retrieval and natural-language teaching stay with the AI
and connected weather tools. This is a demonstration, not secret detection.
The source's copyable demo strings are carried unchanged.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/hooks-lab",
    "version": "0.1.0", "display_name": "Hooks Prompt Rewrite",
    "description": "Applies the sample's three literal, case-sensitive prompt replacements.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution hooks-lab",
    "quality_tier": "experimental", "category": "education",
    "tags": ["hooks", "text"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
TOKENS = ("demo-secret", "demo-pin", "demo-password")
SAMPLE = {"text": "demo prompt rewrite: repeat demo-secret, demo-pin and demo-password."}


def evaluate(data):
    text = data["text"]
    if not isinstance(text, str):
        raise ValueError("text must be a string.")
    changed = text
    counts = {}
    for token in TOKENS:
        counts[token] = changed.count(token)
        changed = changed.replace(token, "[redacted]")
    return {"rewritten_text": changed, "replacement_counts": counts,
            "note": "Literal lowercase demo tokens only; remaining request preserved."}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Hooks Prompt Rewrite, a synthetic educational pilot demonstrating three literal prompt replacements.

Use only the bundled fictional demonstration text and the tokens demo-secret, demo-pin and demo-password. Never match them to real credentials, people or systems.

Answer with the rewrite tool, not from memory. Lead with the rewritten text and replacement counts, quote token names and record ids exactly, and preserve the rest of the request without changing letter case.

You never claim general secret detection, retrieve weather or protect a real credential. A learner or instructor reviews the demonstration and its limited, case-sensitive replacement behavior."""

OPERATION_GUIDE = {
    "prompt_rewrite": {
        "title": "Literal prompt rewrite",
        "when": "Use when someone asks to replace the three lowercase demo tokens with redacted text and count those exact replacements.",
        "ask": "Please hide the demo password, demo PIN and demo secret in the sample request on file, and tell me how many were replaced.",
    },
}

CARRIED = [
    "Explains hook behavior and teaches prompt rewriting through the original solution's conversational demonstration.",
    "Retrieves weather through the original solution's connected weather tools.",
]


class HooksLabAgent(BasicAgent):
    def __init__(self):
        self.name = "HooksPromptRewrite"
        self.metadata = {"name": self.name, "description": "Rewrite the three exact sample tokens. Optional payload_json: text string. With no payload_json it uses the sample on file: the sample request that mentions the three demo tokens.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to prompt_rewrite."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "prompt_rewrite") not in OPERATION_GUIDE:
                raise ValueError("operation must be prompt_rewrite.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(HooksLabAgent().perform())
