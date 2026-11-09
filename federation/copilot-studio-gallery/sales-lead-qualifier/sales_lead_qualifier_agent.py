"""BANT qualification and logging gates from README.md, Qualification rules.

Hot requires Budget Strong and Authority Strong, plus Need or Timing Strong.
Otherwise any Strong means Warm; none means Cold. Non-sales means Filtered.
Only genuine enquiries log; only Hot leads with a created record notify.
Free-text signal extraction, buying-intent judgment, contact extraction, and
notification prose stay with the AI. No duplicate policy is invented and no
record or email is created. All bundled sample contact data is fictional.
"""
import json

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/sales-lead-qualifier",
    "version": "0.1.0", "display_name": "Sales Lead Qualification Rules",
    "description": "Applies documented BANT tiers and Hot-only notification gates.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution sales-lead-qualifier",
    "quality_tier": "experimental", "category": "sales",
    "tags": ["bant", "leads"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
SIGNALS = ("Budget", "Authority", "Need", "Timing")
SAMPLE = {"company": "Contoso", "is_sales": True, "buying_intent": True,
          "signals": {"Budget": "Strong", "Authority": "Strong", "Need": "Strong", "Timing": "Weak"},
          "record_created": False}


def evaluate(data):
    for field in ("is_sales", "record_created"):
        if type(data.get(field)) is not bool:
            raise ValueError(field + " must be an explicit Boolean.")
    if not data["is_sales"]:
        tier = "Filtered"
    else:
        if type(data.get("buying_intent")) is not bool:
            raise ValueError("buying_intent must be an explicit Boolean for sales messages.")
        signals = data["signals"]
        if not isinstance(signals, dict) or any(signals.get(name) not in ("Strong", "Weak", "Absent") for name in SIGNALS):
            raise ValueError("Each BANT signal must be Strong, Weak, or Absent.")
        if not data["buying_intent"]:
            tier = "Cold"
        elif signals["Budget"] == signals["Authority"] == "Strong" and "Strong" in (signals["Need"], signals["Timing"]):
            tier = "Hot"
        elif any(signals[name] == "Strong" for name in SIGNALS):
            tier = "Warm"
        else:
            tier = "Cold"
    return {"tier": tier, "ShouldLog": tier != "Filtered", "ShouldNotify": tier == "Hot",
            "may_notify_now": tier == "Hot" and data["record_created"],
            "original_table": tier + "Leads" if tier != "Filtered" else None,
            "duplicate_lookup": False, "written": False, "sent": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Sales Lead Qualification, a synthetic sales pilot applying recorded budget, authority, need and timing signals to qualification rules.

Use only the bundled fictional company, buying-intent flags, four signals and record-created state. Never match them to a real prospect, contact or sales record.

Answer with the qualification tool, not from memory. Lead with the tier and logging and notification gates, quote signal names and record ids exactly, and permit a Hot notification only after record creation.

You never infer buying intent from live mail, invent a duplicate policy, create a lead or send a notification. A sales reviewer checks the extracted signals, contact details and record state before acting."""

OPERATION_GUIDE = {
    "qualify_lead": {
        "title": "Lead qualification rules",
        "when": "Use when someone asks which tier follows from already-extracted qualification signals and whether logging or a Hot-lead notification is permitted.",
    },
}

CARRIED = [
    "Extracts contact details and qualification signals, judges buying intent and drafts notification prose through the original solution's lead AI steps.",
    "Creates records in the tier-specific lead tables and notifies for Hot leads through the original solution's logging and notification workflow.",
]


class SalesLeadQualifierAgent(BasicAgent):
    def __init__(self):
        self.name = "SalesLeadQualification"
        self.metadata = {"name": self.name, "description": "Apply already-extracted BANT rules. Optional payload_json: is_sales, buying_intent, record_created Booleans; signals object with Budget,Authority,Need,Timing set to Strong/Weak/Absent.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to qualify_lead."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "qualify_lead") not in OPERATION_GUIDE:
                raise ValueError("operation must be qualify_lead.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(SalesLeadQualifierAgent().perform())
