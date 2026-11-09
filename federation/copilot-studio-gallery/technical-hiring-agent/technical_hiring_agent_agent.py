"""Output-shape and email gates from README.md, Capabilities and Key behaviors.

Checks five primary questions with three follow-ups and answers each, or a
three-to-six-stage interview loop. Email plans require full-draft approval and
never include file attachments. No candidate is scored or screened.
Technical assessment, question writing, role interpretation, and explanations
stay with the AI; final hiring decisions stay with people.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/technical-hiring-agent",
    "version": "0.1.0", "display_name": "Technical Hiring Output Checks",
    "description": "Checks interview output structure and approved attachment-free email plans.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution technical-hiring-agent",
    "quality_tier": "experimental", "category": "hr",
    "tags": ["interview", "approval"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SAMPLE = {"operation": "loop", "stages": [
    {"focus": "System design", "criteria": "Explain tradeoffs", "interviewer_profile": "Senior engineer"},
    {"focus": "Implementation", "criteria": "Correctness and clarity", "interviewer_profile": "Engineering peer"},
    {"focus": "Collaboration", "criteria": "Evidence of teamwork", "interviewer_profile": "Hiring manager"}]}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def evaluate(data):
    operation = data["operation"]
    if operation == "questions":
        questions = data["questions"]
        if not isinstance(questions, list):
            raise ValueError("questions must be a list.")
        problems = [] if len(questions) == 5 else ["Exactly five primary questions are required."]
        for index, question in enumerate(questions, 1):
            if not nonempty(question.get("question")) or not nonempty(question.get("answer")):
                problems.append(f"Question {index} needs a question and answer.")
            followups = question.get("followups")
            if not isinstance(followups, list) or len(followups) != 3 or any(
                    not isinstance(item, dict) or not nonempty(item.get("question")) or not nonempty(item.get("answer")) for item in followups):
                problems.append(f"Question {index} needs three answered follow-ups.")
        return {"valid_structure": not problems, "problems": problems,
                "note": "Difficulty progression and technical quality still require expert review."}
    if operation == "loop":
        stages = data["stages"]
        if not isinstance(stages, list):
            raise ValueError("stages must be a list.")
        problems = [] if 3 <= len(stages) <= 6 else ["Interview loop must contain three to six stages."]
        for index, stage in enumerate(stages, 1):
            if not isinstance(stage, dict) or any(not nonempty(stage.get(field)) for field in ("focus", "criteria", "interviewer_profile")):
                problems.append(f"Stage {index} needs focus, criteria, and interviewer_profile.")
        return {"valid_structure": not problems, "problems": problems, "hiring_decision": None}
    if operation == "email":
        if type(data.get("full_draft_approved")) is not bool:
            raise ValueError("full_draft_approved must be an explicit Boolean.")
        if data.get("attachments"):
            raise ValueError("This agent's emails never attach files.")
        allowed = data["full_draft_approved"] and nonempty(data.get("html_body")) and nonempty(data.get("recipient"))
        return {"may_send": allowed, "attachments": [], "sent": False}
    raise ValueError("operation must be questions, loop, or email.")


# ---- Transfer layer ----
INSTRUCTIONS = """You are Technical Hiring Output Checks, a synthetic hiring-support pilot checking interview material structure and approved email plans.

Use only the bundled fictional three-stage interview loop and the empty question and unapproved email checks. Never match them to a real candidate, interviewer or hiring record.

Answer with the hiring output tool, not from memory. Lead with structural problems or sending eligibility, quote operation names and record ids exactly, and distinguish output completeness from technical quality or candidate assessment.

You never score or screen candidates, make hiring decisions, attach files or send email. A technical reviewer checks question quality and the hiring team approves the full draft before any separate communication."""

OPERATION_GUIDE = {
    "questions": {
        "title": "Interview question structure",
        "when": "Use when someone asks whether an interview set has exactly five primary questions with answers and three answered follow-ups each; the no-payload sample reports the missing questions.",
    },
    "loop": {
        "title": "Interview loop structure",
        "when": "Use when someone asks whether a three-to-six-stage interview loop supplies a focus, criteria and interviewer profile for each stage.",
    },
    "email": {
        "title": "Interview email approval check",
        "when": "Use when someone asks whether a complete interview email draft is approved and attachment-free before a separate send action.",
    },
}

CARRIED = [
    "Interprets roles, writes questions and answers, assesses technical quality and explains interview plans through the original solution's hiring agent.",
    "Sends the approved full email draft without attachments through the original solution's email action, leaving hiring decisions to people.",
]


class TechnicalHiringAgent(BasicAgent):
    def __init__(self):
        self.name = "TechnicalHiringOutputCheck"
        self.metadata = {"name": self.name, "description": "Check interview structure, not candidates. Optional payload_json: operation questions with questions [{question,answer,followups:[{question,answer}]}]; loop with stages [{focus,criteria,interviewer_profile}]; email with full_draft_approved Boolean, html_body, recipient, empty attachments.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; overrides the payload operation. Default loop."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            if "operation" in kwargs:
                operation = kwargs["operation"]
                if operation not in OPERATION_GUIDE:
                    raise ValueError("operation must be questions, loop, or email.")
                if "payload_json" not in kwargs and operation == "questions":
                    data = {"questions": []}
                elif "payload_json" not in kwargs and operation == "email":
                    data = {"full_draft_approved": False, "attachments": []}
                data = {**data, "operation": operation}
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(TechnicalHiringAgent().perform())
