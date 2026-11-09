"""Packet and team-intro gates from README.md, How the workflow runs.

Checks Packet sent, required hire fields, Everyone plus a supplied matching
audience, manager-first roster capped at ten, 0.75 bio confidence, and the
independent Yes/No auto-send setting. Audience interpretation, profile matching,
confidence judgment, and bios stay with the AI. No email, draft, or stamp is
created. Bundled people, links, and company data are fictional.
"""
import json
import math

try:
    from basic_agent import BasicAgent
except ImportError:
    from agents.basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0", "name": "@aibast-agents-library/hr-new-hire-welcome-packet",
    "version": "0.1.0", "display_name": "HR Welcome Packet Checks",
    "description": "Plans packet eligibility and independent team-intro delivery gates.",
    "author": "AIBAST, built on the Copilot Studio Gallery solution hr-new-hire-welcome-packet",
    "quality_tier": "experimental", "category": "hr",
    "tags": ["onboarding", "gates"], "requires_env": [], "dependencies": ["@rapp/basic-agent"],
}
REQUIRED = ("Preferred name", "Work email", "Job title", "Start date", "Manager email")
SAMPLE = {
    "hire": {"Preferred name": "Sample hire", "Work email": "hire@contoso.example",
             "Job title": "Engineer", "Start date": "2026-11-02", "Manager email": "manager@contoso.example", "Packet sent": ""},
    "links": [{"Audience": "Everyone", "Link name": "Benefits", "URL": "https://contoso.example/benefits", "Description": "Sample benefits page"},
              {"Audience": "Engineering", "Link name": "Engineering guide", "URL": "https://contoso.example/engineering", "Description": "Sample team guide"}],
    "matched_audience": "Engineering", "auto_send_team_intro": "No",
    "manager": {"name": "Sample manager", "email": "manager@contoso.example", "job_title": "Team manager"},
    "direct_reports": [{"name": "Sample teammate", "email": "teammate@contoso.example", "job_title": "Engineer", "confidence": 0.6}]}


def evaluate(data):
    hire, links = data["hire"], data["links"]
    missing = [field for field in REQUIRED if not str(hire.get(field) or "").strip()]
    audience = data.get("matched_audience")
    audiences = {row["Audience"] for row in links}
    if audience is not None and (audience not in audiences or audience == "Everyone"):
        raise ValueError("matched_audience must be a single non-Everyone list value, or null for no match.")
    if hire.get("Packet sent"):
        packet = {"action": "skip", "reason": "Packet sent already has a value.", "links": []}
    elif missing:
        packet = {"action": "notify HR", "missing_fields": missing, "links": [], "stamp": False}
    else:
        selected = [row for row in links if row["Audience"] == "Everyone" or row["Audience"] == audience]
        packet = {"action": "prepare packet", "links": selected, "notify_hr_unmatched_title": audience is None,
                  "manager_follow_up_needed": audience is None, "stamp": False}
    setting = data["auto_send_team_intro"]
    if setting not in ("Yes", "No"):
        raise ValueError("auto_send_team_intro must be Yes or No.")
    roster, seen = [], set()
    hire_email = str(hire.get("Work email", "")).casefold()
    for person in [data["manager"]] + data.get("direct_reports", []):
        email = person.get("email", "").strip().casefold()
        if not person.get("job_title", "").strip() or not email or email == hire_email or email in seen:
            continue
        seen.add(email)
        confidence = person.get("confidence", 0)
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError("Profile confidence must be a finite number from 0 to 1.")
        sourced = confidence >= 0.75 and bool(person.get("source")) and bool(person.get("bio"))
        roster.append({"name": person["name"], "email": person["email"], "job_title": person["job_title"],
                       "bio": person["bio"] if sourced else f"Meet {person['name']}, {person['job_title']}.",
                       "source": person["source"] if sourced else None, "uses_sourced_bio": bool(sourced)})
        if len(roster) == 10:
            break
    return {"packet": packet, "team_intro": {"delivery_plan": "send" if setting == "Yes" else "draft",
                                             "roster": roster, "independent_of_packet": True,
                                             "disclaimer": "Bios are AI-generated from public information and may be inaccurate."},
            "external_work_performed": False}


# ---- Transfer layer ----
INSTRUCTIONS = """You are Welcome Packet Checks, a synthetic people-operations pilot checking welcome packet eligibility and an independent team introduction plan.

Use only the bundled fictional hire, manager, teammate, audience links and delivery settings. Never match them to a real employee, public profile or personnel record.

Answer with the welcome gates tool, not from memory. Lead with the packet action and introduction delivery plan, quote recorded fields and ids exactly, and keep the manager first, the roster capped at ten and unsupported biographies out.

You never look up real people, send mail, create a draft or stamp a personnel record. A people-operations reviewer checks audience matching, profile confidence and the separate introduction setting before delivery."""

OPERATION_GUIDE = {
    "welcome_gates": {
        "title": "Welcome packet and introduction gates",
        "when": "Use when someone asks whether a welcome packet is eligible, which audience links apply, or how the independent team introduction roster and delivery setting are checked.",
    },
}

CARRIED = [
    "Interprets audiences, matches public profiles, judges confidence and writes biographies through the original solution's welcome-packet AI steps.",
    "Reads hire and link lists, creates or sends messages and stamps Packet sent through the original solution's welcome workflow.",
]


class HrNewHireWelcomePacketAgent(BasicAgent):
    def __init__(self):
        self.name = "HrWelcomePacketChecks"
        self.metadata = {"name": self.name, "description": "Plan welcome gates. Optional payload_json: hire (source column names), links, matched_audience string or null, auto_send_team_intro Yes/No, manager, direct_reports. People use name,email,job_title and optional confidence,bio,source.",
                         "parameters": {"type": "object", "properties": {
                             "operation": {"type": "string", "enum": list(OPERATION_GUIDE), "description": "Optional; defaults to welcome_gates."},
                             "payload_json": {"type": "string"}}, "required": []}}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        try:
            if kwargs.get("operation", "welcome_gates") not in OPERATION_GUIDE:
                raise ValueError("operation must be welcome_gates.")
            data = json.loads(kwargs["payload_json"]) if "payload_json" in kwargs else SAMPLE
            if not isinstance(data, dict):
                raise ValueError("payload_json must contain an object.")
            return json.dumps(evaluate(data), indent=2, sort_keys=True, allow_nan=False)
        except (ValueError, TypeError, KeyError) as error:
            return "Invalid input: " + str(error)


if __name__ == "__main__":
    print(HrNewHireWelcomePacketAgent().perform())
