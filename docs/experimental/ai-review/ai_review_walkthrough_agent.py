"""
AI Review Walkthrough Agent (rapplication)

An educational, step-by-step walkthrough of a generic responsible AI review
for your own AI agent or app. It teaches one stage at a time: why the stage
matters, the questions to answer, and a worked example from an invented
sample agent. Your answers are saved only in this Brainstem's local storage,
and an export writes a Markdown review packet plus a one-page summary to a
local folder. The agent itself makes no network calls, but what you type in
chat is sent to the AI model your Brainstem uses, as with any chat.

Built from Microsoft's public responsible AI guidance. Educational only.
Every stage links the public pages it draws on ("Learn more"); the full source
list, with the date checked, is in SOURCES below and in every export. It is a
generic review any team could run; it does not describe or reproduce any
organization's internal process.

Educational. Not legal advice, and not a substitute for your organization's
own review.

Experimental and not an officially supported Microsoft product or service.
Provided as is under the repository's MIT license, with no support or
warranty. Use at your own risk. Trademark use follows the repository's
trademark notice.

Stdlib only. Single file. Drop it into a Brainstem's agents/ folder.
"""

import json
import os
import re
import uuid
from datetime import datetime, timezone

try:
    from agents.basic_agent import BasicAgent
except Exception:  # pragma: no cover - layout differs between hosts
    try:
        from basic_agent import BasicAgent
    except Exception:
        class BasicAgent:  # minimal stand-in so the file runs on its own
            def __init__(self, name=None, metadata=None):
                self.name = name or getattr(self, "name", "BasicAgent")
                self.metadata = metadata or getattr(self, "metadata", {})

            def perform(self, **kwargs):
                return "Not implemented."


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/ai-review-walkthrough",
    "version": "1.0.0",
    "display_name": "AI Review Walkthrough",
    "description": (
        "Walks you, one stage at a time, through an educational responsible AI "
        "review of your own AI agent or app, and exports a review packet."
    ),
    "author": "AIBAST",
    "tags": ["experimental", "responsible-ai", "review", "education", "rapplication"],
    "category": "experimental_tools",
    "quality_tier": "experimental",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
    "example_call": "Start a responsible AI review walkthrough for my agent.",
}

NOTICE = (
    "Experimental and not an officially supported Microsoft product or service. "
    "Provided as is under the repository's MIT license, with no support or "
    "warranty. Use at your own risk. Trademark use follows the repository's "
    "trademark notice."
)
FRAMING = "Built from Microsoft's public responsible AI guidance. Educational only."
DISCLAIMER = (
    "Educational. Not legal advice, and not a substitute for your "
    "organization's own review."
)

SAMPLE_AGENT = (
    "Fern & Field Returns Helper, an invented assistant for a fictional garden "
    "supply shop. It answers store staff questions about the returns policy, "
    "using only the shop's policy handbook."
)

DECISIONS = ("go", "go with conditions", "not yet")

STORE_DIR = "ai_review"
STATE_FILE = STORE_DIR + "/reviews.json"
EXPORT_DIR = STORE_DIR + "/exports"

SOURCES_CHECKED = "2026-10-29"

# Public, sign-in-free sources this walkthrough is built from. Paraphrased in
# short plain words; nothing is copied at length.
SOURCES = {
    "principles": (
        "Microsoft Responsible AI principles and approach",
        "https://www.microsoft.com/en-us/ai/principles-and-approach",
    ),
    "standard": (
        "Microsoft Responsible AI Standard v2, general requirements (public version)",
        "https://msblogs.thesourcemediaassets.com/sites/5/2022/06/Microsoft-Responsible-AI-Standard-v2-General-Requirements-3.pdf",
    ),
    "ia_template": (
        "Microsoft Responsible AI Impact Assessment Template (public)",
        "https://msblogs.thesourcemediaassets.com/sites/5/2022/06/Microsoft-RAI-Impact-Assessment-Template.pdf",
    ),
    "ia_guide": (
        "Microsoft Responsible AI Impact Assessment Guide (public)",
        "https://msblogs.thesourcemediaassets.com/sites/5/2022/06/Microsoft-RAI-Impact-Assessment-Guide.pdf",
    ),
    "hax": (
        "Guidelines for Human-AI Interaction (Microsoft HAX Toolkit)",
        "https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/",
    ),
    "practices": (
        "Overview of responsible AI practices for hosted models: identify, measure, mitigate, operate (Microsoft Learn)",
        "https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/overview",
    ),
    "tnote": (
        "Transparency Note for hosted models (Microsoft Learn)",
        "https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/transparency-note",
    ),
    "redteam": (
        "Planning red teaming for large language models and their applications (Microsoft Learn)",
        "https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/red-teaming",
    ),
    "threats": (
        "Threat modeling AI/ML systems and dependencies (Microsoft Learn)",
        "https://learn.microsoft.com/en-us/security/engineering/threat-modeling-aiml",
    ),
    "report": (
        "Microsoft Responsible AI Transparency Report",
        "https://www.microsoft.com/en-us/corporate-responsibility/responsible-ai-transparency-report",
    ),
}

# Each question: id, the question, a minimum number of listed items, and the
# plain gap message shown by `check` when it is missing or too thin.
STAGES = [
    {
        "id": "describe",
        "title": "Describe the system",
        "lesson": (
            "A reviewer can only judge what they understand. Explain in plain "
            "language what you are building, who it is for, how it works and "
            "where it will run. Every later stage builds on this."
        ),
        "questions": [
            ("name", "What is the system called, and what does it do, in plain language?", 1,
             "you have not named the system or said what it does"),
            ("users", "Who uses it, and in what setting?", 1,
             "you have not said who uses the system"),
            ("how", "How does it work: inputs, the kind of AI model, data sources, and outputs?", 1,
             "you have not described how the system works (inputs, model, data, outputs)"),
            ("actions", "Can it take actions on its own (send, change, buy, delete), or does it only answer?", 1,
             "you have not said whether the system can take actions on its own"),
            ("deployment", "Where and how will it be deployed (regions, languages, channels, release stage and dates)?", 1,
             "you have not said where and how the system will be deployed"),
        ],
        "example": {
            "name": "Returns Helper answers staff questions about the returns policy.",
            "users": "Shop floor staff, on a tablet at the service desk.",
            "how": "Staff type a question; a language model answers only from the policy handbook and cites the section.",
            "actions": "It only answers. It cannot issue refunds or change records.",
            "deployment": "Two shops, English only, a four-week pilot, then all shops.",
        },
        "sources": ["ia_template", "ia_guide"],
    },
    {
        "id": "uses",
        "title": "Intended and out-of-scope uses",
        "lesson": (
            "An intended use is what your team designs and tests the system for. "
            "Much harm comes from using a system for something it was never built "
            "or tested for, so write down the uses you rule out and the known limits."
        ),
        "questions": [
            ("intended", "List the intended uses (one per line).", 2,
             "you listed fewer than two intended uses"),
            ("fit", "For each intended use, how does the system actually solve the problem, and how will you know?", 1,
             "you have not said how the system is fit for its intended uses"),
            ("out_of_scope", "List uses it was not designed or tested for, or that should be avoided (one per line).", 2,
             "you listed no out-of-scope uses, or only one"),
            ("limits", "What are its known limits: where will it not perform well?", 1,
             "you have not listed the system's known limits"),
            ("decline", "What should it do when asked something out of scope?", 1,
             "you have not said how the system responds to out-of-scope requests"),
        ],
        "example": {
            "intended": "Explain the returns window\nExplain which items need a receipt",
            "fit": "Staff get the policy answer in seconds; we compare answers against the handbook in testing.",
            "out_of_scope": "Legal or consumer-rights advice\nDeciding a specific customer's refund\nQuestions unrelated to returns",
            "limits": "Unusual cases the handbook does not cover; questions in other languages.",
            "decline": "Say it can only help with the returns policy and point staff to a manager.",
        },
        "sources": ["ia_template", "standard", "tnote"],
    },
    {
        "id": "stakeholders",
        "title": "Stakeholders and affected people",
        "lesson": (
            "The people affected by a system are not always the people using it. "
            "Name everyone it touches, with the likely benefits and harms for each, "
            "and the people who will oversee and run it."
        ),
        "questions": [
            ("direct", "Who uses the system directly?", 1,
             "you have not named the direct users"),
            ("indirect", "Who is affected without using it (customers, the public, other teams)?", 1,
             "you have not named anyone affected indirectly"),
            ("benefits_harms", "For each stakeholder, what are the likely benefits and harms (one per line)?", 2,
             "you have not listed benefits and harms for at least two stakeholders"),
            ("higher_risk", "Could any group be at higher risk (for example people with disabilities, minors, non-native speakers)?", 1,
             "you have not considered groups at higher risk"),
            ("operators", "Who will run, oversee and troubleshoot it after release?", 1,
             "you have not named who oversees and runs the system"),
        ],
        "example": {
            "direct": "Service desk staff.",
            "indirect": "Customers returning items, whose outcome depends on the answer staff receive.",
            "benefits_harms": "Staff: faster answers; harm if an answer is wrong\nCustomers: quicker service; harm if a valid return is refused",
            "higher_risk": "Staff reading in a second language; customers who cannot easily come back.",
            "operators": "The store manager, with the shop's IT contact.",
        },
        "sources": ["ia_template", "standard"],
    },
    {
        "id": "data",
        "title": "Data and privacy",
        "lesson": (
            "A system is shaped by the data it reads and keeps. Know what data goes "
            "in, whether it suits the intended uses and the people involved, where "
            "it is stored and who can see it."
        ),
        "questions": [
            ("data_used", "What data does the system read, use or learn from?", 1,
             "you have not listed the data the system uses"),
            ("suitability", "Is that data suitable and representative for the intended uses and the people affected?", 1,
             "you have not said whether the data suits the intended uses"),
            ("personal", "Does it handle personal or sensitive data? If so, which?", 1,
             "you have not said whether personal or sensitive data is involved"),
            ("retention", "What is stored, where, for how long, and who can access it?", 1,
             "you have not described storage, retention or access"),
        ],
        "example": {
            "data_used": "The shop's returns policy handbook only. No training on shop data.",
            "suitability": "The handbook is current and covers all item types; test questions come from real staff.",
            "personal": "None by design; staff are told not to type customer details.",
            "retention": "Chat history is kept 30 days on the shop's own system; only the store manager can view it.",
        },
        "sources": ["standard", "ia_template", "tnote"],
    },
    {
        "id": "harms",
        "title": "Harms mapping across the principle areas",
        "lesson": (
            "Harms are easier to find through six lenses: fairness, reliability and "
            "safety, privacy and security, inclusiveness, transparency and "
            "accountability. List what could go wrong, including misuse and "
            "predictable failures, then rank by how severe and how likely."
        ),
        "questions": [
            ("fairness", "Fairness: could quality of service, access to opportunities, or how people are described differ between groups?", 1,
             "you have not considered fairness"),
            ("reliability", "Reliability and safety: what are the predictable failures, and what happens when it is wrong?", 1,
             "you have not considered reliability and safety"),
            ("privacy", "Privacy and security: could it expose information or be misused?", 1,
             "you have not considered privacy and security"),
            ("inclusiveness", "Inclusiveness: who might find it hard to use (accessibility, language)?", 1,
             "you have not considered inclusiveness"),
            ("transparency", "Transparency: will people know it is AI, what it can do and how well?", 1,
             "you have not considered transparency"),
            ("accountability", "Accountability: who owns the outcome when it goes wrong?", 1,
             "you have not considered accountability"),
            ("top_harms", "List your top harms, each with severity and likelihood (low, medium, high), one per line.", 2,
             "you listed fewer than two ranked harms"),
        ],
        "example": {
            "fairness": "Low risk: one policy for everyone; we check answers are equally good for all item types.",
            "reliability": "It could state a rule that is not in the handbook and a valid return gets refused.",
            "privacy": "Staff might type customer details; we remind them not to and keep logs private.",
            "inclusiveness": "Plain-language answers and screen-reader support on the tablet.",
            "transparency": "The screen says it is an AI assistant and that it can be wrong.",
            "accountability": "The store manager owns returns decisions, not the assistant.",
            "top_harms": "Made-up rule leads to a wrong refusal (medium severity, low likelihood)\nCustomer details typed into chat (medium, medium)",
        },
        "sources": ["principles", "standard", "ia_template", "practices"],
    },
    {
        "id": "threats",
        "title": "Threat model, in concept",
        "lesson": (
            "A threat model asks, before release, how the system could be misused "
            "or attacked and what protects it. You do not need to be a security "
            "expert to name what is valuable, where untrusted input crosses into "
            "the system, what it depends on, and what could go wrong."
        ),
        "questions": [
            ("assets", "What is valuable or sensitive in or around the system (data, outputs, the model, its permissions)?", 1,
             "you have not listed what needs protecting"),
            ("entry_points", "Where does untrusted input cross in (user messages, files, web content, other tools), and what outside parts does it depend on?", 1,
             "you have not listed untrusted inputs and dependencies"),
            ("what_could_go_wrong", "What could go wrong: misuse, data leaking out, tampered data, being steered off task, unintended actions?", 2,
             "you listed fewer than two ways things could go wrong"),
            ("controls", "What protects against each of those (limits on permissions, input checks, access control, approvals)?", 1,
             "you have not listed the controls that protect the system"),
        ],
        "example": {
            "assets": "The handbook (internal) and chat logs. The assistant has read-only access.",
            "entry_points": "Staff messages; handbook updates; the hosted model it calls.",
            "what_could_go_wrong": "Someone tries to get answers outside returns\nA bad handbook edit spreads a wrong rule",
            "controls": "Answers only from the handbook; edits need a second approver; logs are private; no write access.",
        },
        "sources": ["threats", "report"],
    },
    {
        "id": "evaluation",
        "title": "Evaluation plan and defect rates",
        "lesson": (
            "You cannot claim a system is good enough without measuring it. Decide "
            "the acceptable error rate first, then test quality, groundedness, "
            "harmful content and misuse, by hand first and then with repeatable "
            "test sets, before and after mitigations."
        ),
        "questions": [
            ("quality", "How will you test answer quality (test set, size, who judges)?", 1,
             "you have no plan for testing answer quality"),
            ("groundedness", "How will you check answers stay true to the source data?", 1,
             "you have no plan for checking groundedness"),
            ("harmful_misuse", "How will you test that it declines harmful requests and requests outside the intended use?", 1,
             "you have no plan for harmful-content and misuse testing"),
            ("red_team", "Who will probe it for harms (a varied group, including everyday-user views), and how are findings recorded (date, version tested, a repeatable example)?", 1,
             "you have not said who probes the system for harms or how findings are recorded"),
            ("defect_rates", "What defect rate will you accept for each test, and what did you measure?", 1,
             "you have not set target or measured defect rates"),
        ],
        "example": {
            "quality": "120 real staff questions; two supervisors check each answer.",
            "groundedness": "Every answer must cite a handbook section; reviewers check the citation supports it.",
            "harmful_misuse": "60 requests outside the intended use; we check it declines and points to a manager.",
            "red_team": "Four staff and a manager try it freely, then against a harm list; findings go in a shared sheet with the date, the version tested and a repeatable example.",
            "defect_rates": "Target under 2% wrong answers and 0 harmful answers. Measured 1.7% (2 of 120) and 0 of 60.",
        },
        "sources": ["practices", "redteam", "standard"],
    },
    {
        "id": "mitigations",
        "title": "Mitigations",
        "lesson": (
            "Each important harm needs something that reduces it. Think in layers: "
            "the model, safety filters, the app's own instructions and design, and "
            "how you position and document it. Test that each mitigation works."
        ),
        "questions": [
            ("per_harm", "For each top harm, what reduces it (one per line: harm, then mitigation)?", 2,
             "you listed fewer than two harm-to-mitigation pairs"),
            ("layers", "Which layers do you use: model choice, safety filters, app instructions and grounding, user experience, documentation?", 1,
             "you have not said which mitigation layers you use"),
            ("fallback", "When a failure cannot be prevented by design, what is the fallback?", 1,
             "you have not described a fallback for failures you cannot prevent"),
            ("tested", "How do you know each mitigation works, and what risk remains?", 1,
             "you have not said how mitigations were tested or what risk remains"),
        ],
        "example": {
            "per_harm": "Made-up rule: must cite the handbook or say it does not know\nCustomer details: on-screen reminder and log redaction",
            "layers": "Content filters on; instructions limit it to returns; citations shown; short answers.",
            "fallback": "If it cannot find the rule, it says so and sends staff to a manager.",
            "tested": "Re-ran the evaluation after each change. Remaining risk: occasional unclear answers.",
        },
        "sources": ["practices", "standard", "ia_template"],
    },
    {
        "id": "oversight",
        "title": "Human oversight and escalation",
        "lesson": (
            "People should stay in charge of decisions that matter. The people "
            "overseeing the system need to understand what it is for, how to read "
            "its output, when to override or stop it, and how to avoid relying on "
            "it too much."
        ),
        "questions": [
            ("human_in_loop", "Where does a person review, approve, correct or override what it does?", 1,
             "you have not said where a person reviews or overrides the system"),
            ("overreliance", "How do you help people avoid trusting its output too much?", 1,
             "you have not addressed over-reliance on the system"),
            ("escalation", "How does a user report a problem or reach a person?", 1,
             "you have not described how users escalate"),
            ("shutdown", "Who can pause or turn it off, and how fast?", 1,
             "you have not said who can pause the system"),
        ],
        "example": {
            "human_in_loop": "Staff make every refund decision; the assistant only explains policy.",
            "overreliance": "Each answer shows the handbook section so staff can check it.",
            "escalation": "A 'Report a problem' button, and 'ask a manager' in every decline.",
            "shutdown": "The store manager can switch it off from the admin page in under a minute.",
        },
        "sources": ["standard", "hax"],
    },
    {
        "id": "transparency",
        "title": "Transparency note",
        "lesson": (
            "People use a system well when they know what it is, what it can do and "
            "how well. A short transparency note, written for users, covers its "
            "purpose, intended uses, limits, how it performed, and where to get help."
        ),
        "questions": [
            ("what_it_is", "In plain words for users: what is it and what is it for?", 1,
             "your transparency note does not say what the system is for"),
            ("limits", "What are its known limits, and how well did it perform in testing?", 1,
             "your transparency note does not cover limits and performance"),
            ("ai_disclosure", "How do people learn they are dealing with AI?", 1,
             "you have not said how people learn it is AI"),
            ("help", "Where do users get help or give feedback?", 1,
             "your transparency note does not say where to get help"),
        ],
        "example": {
            "what_it_is": "An AI assistant that explains the shop's returns policy.",
            "limits": "It only knows the handbook, can be wrong (about 2 in 100 answers in testing), and does not decide refunds.",
            "ai_disclosure": "A label on the screen and in the first message.",
            "help": "Ask a manager or use 'Report a problem'.",
        },
        "sources": ["tnote", "standard", "hax"],
    },
    {
        "id": "decision",
        "title": "Release decision and sign-off",
        "lesson": (
            "A release should be a deliberate decision by named people, made on the "
            "evidence. Record the decision, any conditions, which reviews were done "
            "and who signed off, and plan to revisit it."
        ),
        "questions": [
            ("decision", "Decision: go, go with conditions, or not yet?", 1,
             "you have not recorded a decision (go, go with conditions, or not yet)"),
            ("reviews_done", "Which checks were completed (for example privacy, security, accessibility)?", 1,
             "you have not listed which checks were completed"),
            ("conditions", "Any conditions or open items, such as a phased rollout (or 'none')?", 1,
             "you have not recorded conditions or open items"),
            ("signoff", "Who signs off (role), and on what date? When is the review updated?", 1,
             "you have not recorded who signs off and when"),
        ],
        "example": {
            "decision": "go with conditions",
            "reviews_done": "Privacy check, security check, accessibility check on the tablet.",
            "conditions": "Pilot in two shops for four weeks; re-run evaluation after any handbook change.",
            "signoff": "Operations lead and store manager, on the pilot start date. Updated yearly or for any new use.",
        },
        "sources": ["ia_template", "practices", "report"],
    },
    {
        "id": "monitoring",
        "title": "Monitoring and incident response",
        "lesson": (
            "A review is not finished at release. Watch how the system behaves in "
            "real use, give users and the public a way to report problems, and "
            "agree in advance how you will respond, roll back and learn."
        ),
        "questions": [
            ("signals", "What will you watch after release (metrics, feedback, samples), and how often?", 1,
             "you have not said what you will monitor"),
            ("feedback", "How can users and others report failures or concerns?", 1,
             "you have not described feedback channels"),
            ("incident_plan", "When an incident is found: who is told, what is paused or rolled back, how fast, how it is fixed?", 1,
             "you have no incident response plan"),
            ("new_uses", "What happens when new uses appear or the system changes?", 1,
             "you have not said how new uses or changes are handled"),
        ],
        "example": {
            "signals": "Weekly sample of 20 chats, decline rate, and report count.",
            "feedback": "'Report a problem' button for staff; a customer comment form at the desk.",
            "incident_plan": "Store manager told the same day; assistant paused within minutes if a rule was wrong; handbook fixed and evaluation re-run.",
            "new_uses": "Any new use is added to this review and tested before it is allowed.",
        },
        "sources": ["standard", "practices", "report"],
    },
]

STAGE_IDS = [s["id"] for s in STAGES]


# ── storage ──────────────────────────────────────────────────────────────
class _FileStore:
    """Fallback local store when the Brainstem storage shim is not present."""

    def __init__(self, root):
        self.root = os.path.abspath(root)

    def _path(self, rel):
        target = os.path.abspath(os.path.join(self.root, rel))
        if os.path.commonpath([self.root, target]) != self.root:
            raise ValueError("path escapes storage root")
        return target

    def read_json(self, file_path):
        path = self._path(file_path)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_json(self, data, file_path):
        self.write_file(file_path, json.dumps(data, indent=2))

    def write_file(self, file_path, content):
        path = self._path(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def abspath(self, file_path):
        return self._path(file_path)


def _default_store():
    override = os.environ.get("AI_REVIEW_DATA_DIR")
    if override:
        return _FileStore(override)
    try:
        from utils.azure_file_storage import AzureFileStorageManager
        return AzureFileStorageManager()
    except Exception:
        return _FileStore(os.path.join(os.path.expanduser("~"), ".brainstem", "ai_review_data"))


def _abspath(store, rel):
    for attr in ("abspath", "_scoped_path"):
        fn = getattr(store, attr, None)
        if callable(fn):
            try:
                return fn(rel)
            except Exception:
                pass
    return rel


# ── helpers ──────────────────────────────────────────────────────────────
def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _items(text):
    """Count listed items: one per line, or separated by semicolons."""
    parts = re.split(r"[\n;]+", str(text or ""))
    return [p.strip(" -*\t") for p in parts if p.strip(" -*\t")]


def _stage_gaps(stage, answers):
    gaps = []
    for qid, _q, min_items, gap in stage["questions"]:
        value = str(answers.get(qid, "") or "").strip()
        if len(_items(value)) < min_items:
            gaps.append(gap)
        elif stage["id"] == "decision" and qid == "decision":
            if value.lower().strip(" .") not in DECISIONS:
                gaps.append("the decision should be one of: go, go with conditions, not yet")
    return gaps


class AIReviewWalkthroughAgent(BasicAgent):
    def __init__(self, store=None):
        self.name = "AIReviewWalkthrough"
        self.metadata = {
            "name": self.name,
            "description": (
                "Educational step-by-step responsible AI review of the user's own "
                "AI agent or app. Use when the user wants to review, assess or "
                "check their AI system before release. Actions: start (new "
                "review), next / back (move one stage), answer (save answers for "
                "the current stage), check (list gaps), status (progress), export "
                "(write a Markdown review packet and one-page summary locally), "
                "sources (the public guidance it is built from). "
                "Show the returned text to the user as-is."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["start", "next", "back", "answer", "check", "status", "export", "sources"],
                        "description": "What to do.",
                    },
                    "system_name": {
                        "type": "string",
                        "description": "start only: a short name for the system under review (optional).",
                    },
                    "answers": {
                        "type": "object",
                        "description": (
                            "answer only: map of question id to the user's answer for the "
                            "current stage, for example {\"intended\": \"...\", \"out_of_scope\": \"...\"}. "
                            "Use the question ids shown in the stage."
                        ),
                        "additionalProperties": {"type": "string"},
                    },
                    "text": {
                        "type": "string",
                        "description": "answer only: free text saved to the first unanswered question of the current stage.",
                    },
                },
                "required": ["action"],
            },
        }
        self._store = store
        super().__init__(name=self.name, metadata=self.metadata)

    # storage ---------------------------------------------------------------
    @property
    def store(self):
        if self._store is None:
            self._store = _default_store()
        return self._store

    def _load(self):
        try:
            data = self.store.read_json(STATE_FILE) or {}
        except Exception:
            data = {}
        data.setdefault("current", None)
        data.setdefault("reviews", {})
        return data

    def _save(self, data):
        self.store.write_json(data, STATE_FILE)

    def _current(self, data):
        rid = data.get("current")
        return data["reviews"].get(rid) if rid else None

    # rendering -------------------------------------------------------------
    def _render_stage(self, review):
        idx = review["stage"]
        stage = STAGES[idx]
        saved = review["answers"].get(stage["id"], {})
        lines = [
            f"**Stage {idx + 1} of {len(STAGES)}: {stage['title']}**",
            "",
            f"Why it matters: {stage['lesson']}",
            "",
            "Questions (answer with the id):",
        ]
        for qid, q, _m, _g in stage["questions"]:
            mark = "done" if str(saved.get(qid, "")).strip() else "open"
            lines.append(f"- `{qid}` ({mark}): {q}")
        lines += ["", "Worked example (invented sample: Fern & Field Returns Helper):"]
        for qid, _q, _m, _g in stage["questions"]:
            lines.append(f"- {qid}: {stage['example'][qid]}")
        lines += ["", "Learn more:"]
        lines += [f"- {SOURCES[k][1]}" for k in stage["sources"]]
        lines += ["", f"_{DISCLAIMER}_"]
        return "\n".join(lines)

    # actions ---------------------------------------------------------------
    def perform(self, **kwargs):
        action = str(kwargs.get("action") or "status").strip().lower()
        handler = {
            "start": self._start,
            "next": self._next,
            "back": self._back,
            "answer": self._answer,
            "check": self._check,
            "status": self._status,
            "export": self._export,
            "sources": self._sources,
        }.get(action)
        if handler is None:
            return "Unknown action. Use start, next, back, answer, check, status, export or sources."
        try:
            return handler(**kwargs)
        except ValueError as exc:
            return f"Could not complete that: {exc}"

    def _sources(self, **_):
        lines = [f"{FRAMING} Public sources, checked {SOURCES_CHECKED}:"]
        lines += [f"- {title}: {url}" for title, url in SOURCES.values()]
        return "\n".join(lines)

    def _need_review(self, data):
        review = self._current(data)
        if review is None:
            raise ValueError("no review in progress. Use action start first.")
        return review

    def _start(self, **kwargs):
        data = self._load()
        name = str(kwargs.get("system_name") or "my agent").strip()[:80] or "my agent"
        rid = uuid.uuid4().hex[:12]
        data["reviews"][rid] = {
            "id": rid,
            "system_name": name,
            "created": _now(),
            "updated": _now(),
            "stage": 0,
            "answers": {},
        }
        data["current"] = rid
        self._save(data)
        review = data["reviews"][rid]
        head = (
            f"Started review `{rid}` ({len(STAGES)} stages). Your answers are saved only in "
            "your Brainstem's local storage, but what you type is sent to the AI model your "
            "Brainstem uses, as with any chat.\n"
            f"{FRAMING}\n"
            "Say 'next' or 'back' to move, give answers by question id, 'check' for gaps, "
            "'status' for progress, 'export' for the packet.\n\n"
        )
        return head + self._render_stage(review)

    def _move(self, step):
        data = self._load()
        review = self._need_review(data)
        new = review["stage"] + step
        if new < 0:
            return "You are already on stage 1.\n\n" + self._render_stage(review)
        if new >= len(STAGES):
            return (
                f"That was the last stage ({len(STAGES)} of {len(STAGES)}). "
                "Use 'check' to see gaps or 'export' to write the packet."
            )
        review["stage"] = new
        review["updated"] = _now()
        self._save(data)
        return self._render_stage(review)

    def _next(self, **_):
        return self._move(1)

    def _back(self, **_):
        return self._move(-1)

    def _answer(self, **kwargs):
        data = self._load()
        review = self._need_review(data)
        stage = STAGES[review["stage"]]
        valid = [q[0] for q in stage["questions"]]
        saved = review["answers"].setdefault(stage["id"], {})
        answers = kwargs.get("answers") or {}
        if isinstance(answers, str):
            try:
                answers = json.loads(answers)
            except ValueError:
                answers = {}
        if not isinstance(answers, dict):
            answers = {}
        recorded, unknown = [], []
        for key, value in answers.items():
            key = str(key).strip()
            if key in valid:
                saved[key] = str(value if value is not None else "").strip()
                recorded.append(key)
            else:
                unknown.append(key)
        text = str(kwargs.get("text") or "").strip()
        if text:
            target = next((q for q in valid if not str(saved.get(q, "")).strip()), None)
            if target is None:
                unknown.append("text (all questions on this stage already answered)")
            else:
                saved[target] = text
                recorded.append(target)
        review["updated"] = _now()
        self._save(data)
        gaps = _stage_gaps(stage, saved)
        msg = [f"Saved {len(recorded)} answer(s) for stage {review['stage'] + 1}: {stage['title']}."]
        if recorded:
            msg.append("Recorded: " + ", ".join(f"`{r}`" for r in recorded) + ".")
        if unknown:
            msg.append("Not recognised: " + ", ".join(unknown[:5]) + f". Valid ids: {', '.join(valid)}.")
        msg.append(f"{len(gaps)} gap(s) left on this stage." if gaps else "This stage looks complete. Say 'next'.")
        return "\n".join(msg)

    def _check(self, **_):
        data = self._load()
        review = self._need_review(data)
        stage = STAGES[review["stage"]]
        gaps = _stage_gaps(stage, review["answers"].get(stage["id"], {}))
        total = sum(len(_stage_gaps(s, review["answers"].get(s["id"], {}))) for s in STAGES)
        lines = [f"Check, stage {review['stage'] + 1} of {len(STAGES)}: {stage['title']}"]
        if gaps:
            lines += [f"- {g[0].upper() + g[1:]}." for g in gaps]
        else:
            lines.append("- No gaps on this stage.")
        lines.append(f"Whole review: {total} gap(s) across {len(STAGES)} stages.")
        lines.append(f"_{DISCLAIMER}_")
        return "\n".join(lines)

    def _status(self, **_):
        data = self._load()
        review = self._need_review(data)
        done = 0
        lines = [f"Review `{review['id']}`: {review['system_name']}"]
        for i, s in enumerate(STAGES):
            gaps = _stage_gaps(s, review["answers"].get(s["id"], {}))
            mark = "complete" if not gaps else f"{len(gaps)} gap(s)"
            done += 0 if gaps else 1
            here = "  <- you are here" if i == review["stage"] else ""
            lines.append(f"{i + 1}. {s['title']}: {mark}{here}")
        lines.insert(1, f"{done} of {len(STAGES)} stages complete.")
        return "\n".join(lines)

    def _export(self, **_):
        data = self._load()
        review = self._need_review(data)
        packet, summary = self.build_packet(review)
        base = f"{EXPORT_DIR}/{review['id']}"
        self.store.write_file(f"{base}/review-packet.md", packet)
        self.store.write_file(f"{base}/summary.md", summary)
        folder = os.path.dirname(_abspath(self.store, f"{base}/review-packet.md"))
        total = sum(len(_stage_gaps(s, review["answers"].get(s["id"], {}))) for s in STAGES)
        return (
            f"Exported the review packet and a one-page summary to:\n{folder}\n"
            "Files: review-packet.md, summary.md. "
            f"{total} open gap(s) are listed in the packet. The files were written to this folder only."
        )

    # packet ----------------------------------------------------------------
    @staticmethod
    def build_packet(review):
        answers = review.get("answers", {})
        out = [
            f"# Responsible AI review packet: {review.get('system_name', 'my agent')}",
            "",
            f"Review id: {review.get('id')}  ",
            f"Created: {review.get('created')}  ",
            f"Exported: {_now()}",
            "",
            f"> {FRAMING} {DISCLAIMER}",
            ">",
            f"> {NOTICE}",
            "",
        ]
        total = 0
        for i, s in enumerate(STAGES):
            a = answers.get(s["id"], {})
            gaps = _stage_gaps(s, a)
            total += len(gaps)
            out += [f"## {i + 1}. {s['title']}", "", f"_Why it matters:_ {s['lesson']}", ""]
            for qid, q, _m, _g in s["questions"]:
                val = str(a.get(qid, "") or "").strip() or "_Not answered._"
                out += [f"**{q}**", "", val, ""]
            if gaps:
                out += ["Open gaps:"] + [f"- {g}" for g in gaps] + [""]
            learn = "; ".join(f"[{SOURCES[k][0]}]({SOURCES[k][1]})" for k in s["sources"])
            out += [f"Learn more: {learn}", ""]
        out += ["---", f"Total open gaps: {total}", "", f"## Sources (checked {SOURCES_CHECKED})", ""]
        out += [f"- {title}: {url}" for title, url in SOURCES.values()]
        out += [""]
        packet = "\n".join(out)

        def first(stage_id, qid, limit=300):
            val = "; ".join(_items(answers.get(stage_id, {}).get(qid, "")))
            if not val:
                return "_Not answered._"
            return val if len(val) <= limit else val[:limit].rstrip() + "..."

        done = sum(1 for s in STAGES if not _stage_gaps(s, answers.get(s["id"], {})))
        summary = "\n".join([
            f"# One-page summary: {review.get('system_name', 'my agent')}",
            "",
            f"> {FRAMING} {DISCLAIMER}",
            "",
            f"- **What it is:** {first('describe', 'name')}",
            f"- **Who uses it:** {first('describe', 'users')}",
            f"- **Intended uses:** {first('uses', 'intended')}",
            f"- **Out of scope:** {first('uses', 'out_of_scope')}",
            f"- **Top harms:** {first('harms', 'top_harms')}",
            f"- **Measured defect rates:** {first('evaluation', 'defect_rates')}",
            f"- **Human oversight:** {first('oversight', 'human_in_loop')}",
            f"- **Decision:** {first('decision', 'decision', 60)}",
            f"- **Conditions:** {first('decision', 'conditions')}",
            f"- **Sign-off:** {first('decision', 'signoff')}",
            f"- **Monitoring:** {first('monitoring', 'signals')}",
            "",
            f"Stages complete: {done} of {len(STAGES)}. Open gaps: {total}.",
            "",
            f"_{NOTICE}_",
            "",
        ])
        return packet, summary
