"""Two-host transcript and SSML formatting from the gallery README.md.

Uses the two documented neural voices and escapes dialogue as XML text.
Material selection, fact checking, dialogue, host personalities, segment
planning, and length editing stay with the AI. No speech or audio is generated.
The supplied default dialogue is fictional.
"""
import json
import xml.etree.ElementTree as ET

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/podcast-generation-agent",
    "version": "0.1.0", "display_name": "Two-host Podcast Formatter",
    "description": "Formats supplied dialogue as a transcript and escaped two-voice SSML.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution podcast-generation-agent",
    "quality_tier": "experimental", "category": "content",
    "tags": ["podcast", "ssml"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
VOICES = {"host_a": "en-US-AvaMultilingualNeural", "host_b": "en-US-AndrewMultilingualNeural"}
SAMPLE = {"turns": [{"host": "host_a", "text": "Today we are exploring Contoso's fictional planning notebook."},
                    {"host": "host_b", "text": "A small shared note can make a handoff clearer."}]}


def evaluate(data):
    turns = data["turns"]
    if not isinstance(turns, list) or not turns:
        raise ValueError("turns must be a nonempty dialogue list.")
    root = ET.Element("speak", {"version": "1.0", "xmlns": "http://www.w3.org/2001/10/synthesis",
                              "xml:lang": "en-US"})
    transcript = []
    for turn in turns:
        if turn["host"] not in VOICES or not isinstance(turn.get("text"), str) or not turn["text"].strip():
            raise ValueError("Each turn needs host_a or host_b and nonempty text.")
        ET.SubElement(root, "voice", {"name": VOICES[turn["host"]]}).text = turn["text"]
        transcript.append(turn["host"] + ": " + turn["text"])
    return {"transcript": "\n".join(transcript), "ssml": ET.tostring(root, encoding="unicode"),
            "voices": VOICES, "audio_generated": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Two-host Podcast Formatter, a synthetic content pilot formatting supplied dialogue into a transcript and escaped speech markup.

Use only the bundled fictional planning-notebook dialogue and its two host labels. Never match them to real speakers, recordings or company material.

Answer with the dialogue formatter tool, not from memory. Lead with the transcript and speech markup, quote host ids and dialogue exactly, and preserve the two recorded voice assignments.

You never claim to research, fact-check, write new dialogue or generate audio. A content editor reviews material, host treatment and length before a separate speech service produces a recording."""

OPERATION_GUIDE = {
    "format_dialogue": {
        "title": "Two-host dialogue formatting",
        "when": "Use when someone asks to turn existing host_a and host_b dialogue into a transcript and escaped two-voice speech markup.",
        "ask": "Turn the sample two-host dialogue on file into a transcript and a two-voice script.",
    },
}

CARRIED = [
    "Selects material, checks facts, writes dialogue and host personalities, plans segments and edits length through the original solution's podcast agent.",
    "Produces speech audio from the two documented neural voices through the original solution's speech-generation step.",
]


class PodcastGenerationAgent(BasicAgent):
    def __init__(self):
        self.name = "PodcastDialogueFormatter"
        self.metadata = {"name": self.name, "description": "Format existing dialogue, not audio. Optional payload_json: nonempty turns [{host:host_a|host_b,text}]. With no payload_json it uses the sample on file: the sample two-host dialogue about Contoso's planning notebook.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to format_dialogue."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "format_dialogue") not in OPERATION_GUIDE:
                raise ValueError("operation must be format_dialogue.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(PodcastGenerationAgent().perform())
