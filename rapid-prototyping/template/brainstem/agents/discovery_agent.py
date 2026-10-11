"""RAPP Step 2 (Audit: Transcript Analysis) as an agent: discovery call transcript -> DISCOVERY.md.

The transcript stays in discovery/ (git-ignored). The output names no people: roles only. A human
confirms DISCOVERY.md (gate 1) before anything is built from it.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from agents.basic_agent import BasicAgent
except ImportError:
    class BasicAgent:
        def __init__(self, name=None, metadata=None):
            self.name, self.metadata = name, metadata

PROMPT = """You are preparing the RAPP Step 2 audit (Transcript Analysis) for a discovery call.
Read the transcript and return ONLY a JSON object:
{{"problem": "one sentence, in the customer's words where possible",
  "users": ["roles, never names"],
  "today": ["how they do it today, step by step"],
  "data": ["what information the solution needs (kinds of data, never real values)"],
  "success": ["how they'd know it worked, measurable where they said so"],
  "mvp": {{"name": "short name", "first_slice": "the smallest thing worth showing them",
          "screens": ["what the person sees"], "agents": [{{"name": "...", "job": "one job"}}]}},
  "out_of_scope": ["things mentioned that the MVP will not do"],
  "open_questions": ["what must be confirmed with the customer"],
  "sensitive": ["anything sensitive mentioned (personal data, systems, money) to keep out of the prototype"]}}
Use roles, not names. Don't invent requirements: if they didn't say it, put it in open_questions.

TRANSCRIPT:
{transcript}
"""


def to_markdown(d: dict) -> str:
    def items(xs):
        return "\n".join(f"- {x}" for x in xs) or "- (none)"
    m = d.get("mvp", {})
    agents = "\n".join(f"- **{a.get('name')}**: {a.get('job')}" for a in m.get("agents", [])) or "- (none)"
    return f"""# Discovery (RAPP Step 2: Transcript Analysis)

> **Gate 1:** a person confirms this page before anything is built. Edit it freely; the AI builds from it.

## The problem
{d.get('problem', '')}

## Who uses it
{items(d.get('users', []))}

## How it works today
{items(d.get('today', []))}

## What it needs to know
{items(d.get('data', []))}

## How we'll know it worked
{items(d.get('success', []))}

## The MVP "poke": {m.get('name', '')}
**First slice:** {m.get('first_slice', '')}

Screens:
{items(m.get('screens', []))}

Agents:
{agents}

## Not in the MVP
{items(d.get('out_of_scope', []))}

## Questions for the customer
{items(d.get('open_questions', []))}

## Keep out of the prototype
{items(d.get('sensitive', []))}
"""


class DiscoveryAgent(BasicAgent):
    def __init__(self):
        self.name = "Discovery"
        self.metadata = {
            "name": self.name,
            "description": "RAPP Step 2: analyses a discovery call transcript in discovery/ and writes DISCOVERY.md. Returns JSON.",
            "parameters": {"type": "object", "properties": {
                "transcript": {"type": "string", "description": "File name inside discovery/"}}, "required": ["transcript"]},
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        from app.llm import complete, extract_json
        try:
            src = (ROOT / "discovery" / Path(kwargs.get("transcript", "")).name)
            if not src.is_file():
                return json.dumps({"ok": False, "error": f"No transcript named {src.name} in discovery/"})
            d = extract_json(complete(PROMPT.format(transcript=src.read_text(errors="replace")[:60000]), timeout=300), dict)
            (ROOT / "DISCOVERY.md").write_text(to_markdown(d))
            (ROOT / "discovery" / "discovery.json").write_text(json.dumps(d, indent=1))
            return json.dumps({"ok": True, "written": "DISCOVERY.md", "mvp": d.get("mvp", {}).get("name"),
                               "open_questions": len(d.get("open_questions", []))})
        except Exception as e:
            return json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"})
