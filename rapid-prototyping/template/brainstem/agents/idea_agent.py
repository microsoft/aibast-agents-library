"""Example agent for the rapid prototyping pattern: does its AI work through its own Brainstem.

Rename it, change the prompt and perform(). Keep: return JSON, never raise to the caller.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # template/ (so `app` is importable)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from agents.basic_agent import BasicAgent  # provided by the Brainstem at runtime
except ImportError:  # imported outside a Brainstem (tests)
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            self.name, self.metadata = name, metadata

PROMPT = """Give three practical, specific ideas for: {topic}.
Return ONLY a JSON array: [{{"title": "...", "why": "one sentence"}}]."""


class IdeaAgent(BasicAgent):
    def __init__(self):
        self.name = "Idea"
        self.metadata = {
            "name": self.name,
            "description": "Gives three practical ideas for a topic. Returns JSON.",
            "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        from app.llm import complete, extract_json
        try:
            ideas = extract_json(complete(PROMPT.format(topic=kwargs.get("topic", "")), timeout=120), list)
            return json.dumps({"ok": True, "ideas": ideas})
        except Exception as e:  # the app shows a plain message, never a traceback
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})
