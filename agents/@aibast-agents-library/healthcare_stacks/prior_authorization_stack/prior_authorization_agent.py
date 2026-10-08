"""Read-only, synthetic prior-authorization evidence support."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/prior-authorization",
    "version": "1.2.0",
    "display_name": "Prior Authorization Agent",
    "description": (
        "Assembles synthetic payer and clinical evidence for human utilization review: the patient "
        "request, payer-criteria match, a ready-to-submit packet, documentation strengths and appeal "
        "strategy, a proposed tracking plan, the authorization portfolio and denial reviews; it never "
        "predicts, grants, denies, submits, or changes an authorization and never sends a notification."
    ),
    "author": "AIBAST",
    "tags": ["prior-auth", "evidence-packet", "payer-criteria", "healthcare", "human-review"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

SAFETY = (
    "Synthetic demonstration data only. This output is a read-only evidence draft, not an "
    "authorization, eligibility, medical-necessity, diagnosis, or treatment decision. A qualified "
    "utilization reviewer must verify payer policy and clinical evidence before any submission."
)

REQUESTS = {
    "SYN-AUTH-001": {
        "service": "synthetic knee imaging request",
        "payer": "Synthetic Health Plan",
        "source_status": "additional evidence requested",
        "source_date": "2026-07-30",
        "policy_id": "SYN-POL-IMG-01",
        "evidence": {
            "encounter note": "present",
            "prior imaging report": "present",
            "conservative-care duration": "not found in synthetic source",
        },
    },
    "SYN-AUTH-002": {
        "service": "synthetic outpatient procedure request",
        "payer": "Synthetic Community Plan",
        "source_status": "payer response recorded",
        "source_date": "2026-07-31",
        "policy_id": "SYN-POL-PROC-02",
        "evidence": {
            "encounter note": "present",
            "specialist note": "present",
            "current payer policy confirmation": "requires human review",
        },
    },
}

POLICIES = {
    "SYN-POL-IMG-01": {
        "title": "Synthetic Imaging Evidence Checklist",
        "requirements": ["relevant encounter note", "prior imaging evidence", "documented duration fields"],
        "effective_date": "2026-07-01",
    },
    "SYN-POL-PROC-02": {
        "title": "Synthetic Procedure Evidence Checklist",
        "requirements": ["relevant encounter note", "specialist documentation", "current policy version"],
        "effective_date": "2026-07-01",
    },
}

# Demo authorization portfolio (video scenario). All patients, IDs and numbers are fictional.
PATIENT_REQUESTS = {
    "PA-2024-892741": {"patient": "Robert Chen", "listed_as": "Chen, Robert", "procedure": "Lumbar MRI", "payer": "Insurance", "status": "Ready to submit"},
    "PA-2024-892655": {"patient": "Ana Martinez", "listed_as": "Martinez, Ana", "procedure": "Knee arthroscopy", "payer": "Insurance", "status": "Approved"},
    "PA-2024-892698": {"patient": "David Thompson", "listed_as": "Thompson, David", "procedure": "Cervical MRI", "payer": "Insurance", "status": "Pending"},
    "PA-2024-892712": {"patient": "Sarah Williams", "listed_as": "Williams, Sarah", "procedure": "PT (20 visits)", "payer": "Insurance", "status": "Under review"},
    "PA-2024-891977": {"patient": "Michael Johnson", "listed_as": "Johnson, Michael", "procedure": "Sleep study", "payer": "Medicare", "status": "Denied (appealing)"},
}

OPEN_STATUSES = ["Ready to submit", "Pending", "Under review"]

PORTFOLIO_METRICS = {"avg_approval_days": 2.4, "approval_rate_month_pct": 91, "historical_similar_approval_pct": 94}

CHEN_REQUEST = {
    "auth_id": "PA-2024-892741",
    "patient": "Robert Chen",
    "dob": "05/22/1965",
    "mrn": "MR-489327",
    "insurance": "Insurance PPO #XY4829103",
    "cpt": "72148 - Lumbar MRI w/o contrast",
    "provider": "Dr. James Thompson (Orthopedics)",
    "diagnosis": "M54.5 - Chronic low back pain",
    "indication": "Failed 6 weeks conservative therapy",
    "payer_reference": "Case #4729183",
    "prepared_at": "Today at 3:47 PM",
    "review_type": "Standard (non-urgent)",
    "expected_decision": "Within 2 business days",
    "reviewer": "Automated criteria screening",
}

PAYER_REQUIREMENTS_72148 = [
    ["Clinical notes", "Last 3 office visits attached", "Met"],
    ["Conservative therapy", "PT x6 weeks, NSAIDs documented", "Met"],
    ["Symptom duration", "8 weeks, no improvement", "Met"],
    ["Red flag screening", "Negative (no fever/trauma/cancer)", "Met"],
    ["Provider NPI", "Dr. Thompson #1234567890", "Met"],
    ["Prior imaging", "None on file (first lumbar study)", "Met"],
]

DOCUMENTATION_STRENGTHS = [
    "Conservative therapy well-documented (PT, NSAIDs)",
    "Symptom duration >6 weeks",
    "Clinical notes support medical necessity criteria",
    "No inappropriate imaging red flags",
    "Complete documentation package",
]

APPEAL_STRATEGY = [
    "Peer-to-peer review with radiologist",
    "Additional functional impact documentation",
    "Imaging guidelines citation",
]

PROPOSED_NOTIFICATIONS = [
    "Patient: SMS with tracking link",
    "Dr. Thompson: Inbox message",
    "Radiology: Pending alert for scheduling",
]

TRACKING_PLAN = [
    "Status checks: every 4 hours via portal",
    "Patient notification: SMS when approved (includes auth #)",
    "Radiology alert: scheduling team notified to book slot",
    "Provider update: Dr. Thompson via secure message",
    "Escalation: auto-trigger if no decision in 48 hours",
    "Appeal workflow: ready if denied",
]

JOHNSON_DENIAL = {
    "auth_id": "PA-2024-891977",
    "reason": "Insufficient clinical documentation of daytime symptoms",
    "missing": [
        "Epworth Sleepiness Scale not in records",
        "Work/driving impairment not documented",
        "Failed CPAP trial not clearly stated",
    ],
    "appeal_actions": [
        "Peer-to-peer review scheduled - tomorrow 2 PM",
        "Additional symptom questionnaire completed",
        "Employer letter documenting work issues",
        "Prior CPAP compliance data retrieved",
    ],
    "timeline": "Decision expected within 5 business days",
}

DEMO_OPERATIONS = [
    "patient_auth_request", "payer_requirements_check", "submission_packet", "approval_outlook",
    "tracking_plan", "portfolio_status", "denial_review",
]

ALIASES = {
    "auth_request": "request_evidence",
    "clinical_criteria_check": "criteria_evidence",
    "status_tracking": "status_summary",
    "appeal_preparation": "appeal_evidence_packet",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _resolve_patient(query):
    """Patient name or PA-2024 ID (e.g. 'Robert Chen', 'Johnson'); default Robert Chen; None when nothing matches."""
    if not query:
        return "PA-2024-892741"
    q = query.lower().strip()
    for key in PATIENT_REQUESTS:
        if key.lower() in q or q in PATIENT_REQUESTS[key]["patient"].lower():
            return key
    return None


def _no_patient(query):
    names = ", ".join(r["patient"] + " (" + pid + ")" for pid, r in PATIENT_REQUESTS.items())
    return f"# Prior Authorization\n\n> {SAFETY}\n\nNo synthetic request matched `{query}`. Known requests: {names}."


def _selected_request(auth_id):
    if not auth_id:
        return REQUESTS.items()
    if auth_id not in REQUESTS:
        return []
    return [(auth_id, REQUESTS[auth_id])]


class PriorAuthorizationAgent(BasicAgent):
    """Assemble evidence without making an authorization outcome."""

    def __init__(self):
        self.name = "PriorAuthorizationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["request_evidence", "criteria_evidence", "status_summary", "appeal_evidence_packet"] + DEMO_OPERATIONS,
                        "description": (
                            "Read-only utilization-review evidence operation. The demo patient is Robert "
                            "Chen (lumbar MRI, PA-2024-892741); call right away, no ID is needed. "
                            "patient_auth_request: a patient needs prior auth / 'can you submit this' - "
                            "verify the request details. payer_requirements_check: check payer or "
                            "insurance requirements. submission_packet: 'submit it now' / confirmation "
                            "details - returns the ready-to-submit packet (never submits). "
                            "approval_outlook: likelihood of approval and appeal strategy if denied. "
                            "tracking_plan: configure automatic tracking / notify everyone when approved. "
                            "portfolio_status: all pending prior auths and their status. denial_review: "
                            "the denied Medicare case / why a request was denied and the appeal. "
                            "request_evidence, criteria_evidence, status_summary and appeal_evidence_packet "
                            "cover the SYN-AUTH evidence-inventory requests."
                        ),
                    },
                    "patient": {
                        "type": "string",
                        "description": "Optional patient name or PA-2024 request ID for the demo operations (default Robert Chen; denial_review always shows the denied Michael Johnson case).",
                    },
                    "auth_id": {
                        "type": "string",
                        "enum": sorted(REQUESTS),
                        "description": "Optional synthetic request identifier.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = ALIASES.get(kwargs.get("operation", ""), kwargs.get("operation", ""))
        routes = {
            "request_evidence": self._request_evidence,
            "criteria_evidence": self._criteria_evidence,
            "status_summary": self._status_summary,
            "appeal_evidence_packet": self._appeal_evidence_packet,
        }
        demo = {
            "patient_auth_request": self._patient_auth_request,
            "payer_requirements_check": self._payer_requirements_check,
            "submission_packet": self._submission_packet,
            "approval_outlook": self._approval_outlook,
            "tracking_plan": self._tracking_plan,
            "portfolio_status": self._portfolio_status,
            "denial_review": self._denial_review,
        }
        if operation in demo:
            pid = _resolve_patient(kwargs.get("patient"))
            if pid is None:
                return _no_patient(kwargs.get("patient"))
            return demo[operation](pid)
        if operation not in routes:
            return f"**Error:** Unknown operation `{operation}`. No action was taken."
        return routes[operation](kwargs.get("auth_id"))

    def _chen_only(self, pid, title):
        r = PATIENT_REQUESTS[pid]
        return (f"# {title}\n\n> {SAFETY}\n\nThe detailed packet in this synthetic set is for Robert Chen "
                f"(PA-2024-892741). {r['patient']} ({pid}): {r['procedure']}, {r['payer']}, {r['status']}.")

    def _patient_auth_request(self, pid):
        if pid != CHEN_REQUEST["auth_id"]:
            return self._chen_only(pid, "Prior Authorization Request")
        c = CHEN_REQUEST
        lines = _notice("Prior Authorization Request")
        lines.append("Patient demographics, insurance coverage and clinical documentation verified against the "
                     "synthetic EHR record. Ready to prepare for submission.")
        lines.append("")
        lines.append("| Detail | Value |")
        lines.append("|---|---|")
        lines.append(f"| Patient | {c['patient']}, DOB {c['dob']} |")
        lines.append(f"| MRN | {c['mrn']} |")
        lines.append(f"| Insurance | {c['insurance']} |")
        lines.append(f"| CPT code | {c['cpt']} |")
        lines.append(f"| Provider | {c['provider']} |")
        lines.append(f"| Diagnosis | {c['diagnosis']} (source-coded; no diagnosis added) |")
        lines.append(f"| Clinical indication | {c['indication']} |")
        lines.append("")
        lines.append("**Status:** All patient data verified from the synthetic EHR record.")
        lines.append("**Next:** check payer requirements?")
        return "\n".join(lines)

    def _payer_requirements_check(self, pid):
        if pid != CHEN_REQUEST["auth_id"]:
            return self._chen_only(pid, "Insurance Requirements")
        met = 0
        for r in PAYER_REQUIREMENTS_72148:
            if r[2] == "Met":
                met += 1
        total = len(PAYER_REQUIREMENTS_72148)
        lines = _notice("Insurance Requirements")
        lines.append(f"Payer requirements for CPT 72148 matched against {CHEN_REQUEST['patient']}'s documentation.")
        lines.append("")
        lines.append("| Requirement | Evidence found | Status |")
        lines.append("|---|---|---|")
        for r in PAYER_REQUIREMENTS_72148:
            lines.append(f"| {r[0]} | {r[1]} | {r[2]} |")
        lines.append("")
        lines.append("**Assessment:**")
        if met == total:
            lines.append(f"- All required criteria met ({met} of {total} have matching evidence)")
            lines.append("- No missing documentation")
        else:
            lines.append(f"- {met} of {total} criteria have matching evidence")
        lines.append("- Estimated payer turnaround: 24-48 hours (standard review)")
        lines.append("- A utilization reviewer confirms the match; this is not a medical-necessity decision.")
        lines.append("**Next:** prepare the authorization for submission?")
        return "\n".join(lines)

    def _submission_packet(self, pid):
        if pid != CHEN_REQUEST["auth_id"]:
            return self._chen_only(pid, "Submission Packet")
        c = CHEN_REQUEST
        lines = _notice("Submission Packet — Ready for You to Submit")
        lines.append("The authorization request is complete and ready for the coordinator to submit in the payer portal.")
        lines.append("")
        lines.append("| Detail | Value |")
        lines.append("|---|---|")
        lines.append(f"| Auth request # | {c['auth_id']} |")
        lines.append(f"| Prepared | {c['prepared_at']} |")
        lines.append(f"| Payer reference | {c['payer_reference']} |")
        lines.append(f"| Review type | {c['review_type']} |")
        lines.append(f"| Expected decision | {c['expected_decision']} |")
        lines.append(f"| Reviewer | {c['reviewer']} |")
        lines.append("")
        lines.append("**Notifications drafted (sent only when you submit):**")
        for n in PROPOSED_NOTIFICATIONS:
            lines.append(f"- {n}")
        lines.append("")
        lines.append("Not submitted: no payer submission was made and no notification was sent.")
        lines.append("**Next:** review documentation strength and appeal readiness?")
        return "\n".join(lines)

    def _approval_outlook(self, pid):
        if pid != CHEN_REQUEST["auth_id"]:
            return self._chen_only(pid, "Approval Outlook")
        m = PORTFOLIO_METRICS
        lines = _notice("Approval Outlook and Appeal Strategy")
        lines.append(f"**Historical approval rate:** {m['historical_similar_approval_pct']}% for similar cases "
                     "(synthetic historical statistic; no prediction is made for this request).")
        lines.append("")
        lines.append("**Documentation strengths:**")
        for s_ in DOCUMENTATION_STRENGTHS:
            lines.append(f"- {s_}")
        lines.append("")
        lines.append("**If denied - appeal strategy:**")
        for a in APPEAL_STRATEGY:
            lines.append(f"- {a}")
        lines.append("")
        lines.append("**Proposed escalation:** alert within 2 hours of the payer decision.")
        lines.append("**Next:** set up tracking and notifications?")
        return "\n".join(lines)

    def _tracking_plan(self, pid):
        r = PATIENT_REQUESTS[pid]
        lines = _notice("Tracking and Notification Plan (Proposed)")
        lines.append(f"Proposed monitoring for {pid} ({r['patient']}, {r['procedure']}), ready for you to switch on:")
        lines.append("")
        for t in TRACKING_PLAN:
            lines.append(f"- {t}")
        lines.append("")
        lines.append("**Tracking dashboard:** Teams channel post drafted (not posted); real-time status updates "
                     f"once enabled; expected decision {CHEN_REQUEST['expected_decision'].lower()}.")
        lines.append("Nothing is scheduled or sent until you enable it.")
        lines.append("**Next:** see all pending prior auths?")
        return "\n".join(lines)

    def _portfolio_status(self, pid):
        m = PORTFOLIO_METRICS
        open_count = 0
        for r in PATIENT_REQUESTS.values():
            if r["status"] in OPEN_STATUSES:
                open_count += 1
        lines = _notice("Active Prior Authorizations")
        lines.append("| Auth # | Patient | Procedure | Payer | Status |")
        lines.append("|---|---|---|---|---|")
        for k, r in PATIENT_REQUESTS.items():
            lines.append(f"| {k} | {r['listed_as']} | {r['procedure']} | {r['payer']} | {r['status']} |")
        lines.append("")
        lines.append("**Portfolio metrics:**")
        lines.append(f"- Pending: {open_count} authorizations")
        lines.append(f"- Avg approval time: {m['avg_approval_days']} days")
        lines.append(f"- Approval rate: {m['approval_rate_month_pct']}% this month")
        lines.append("Statuses are source-recorded for human review, not agent determinations.")
        lines.append("**Next:** check the denied Medicare case?")
        return "\n".join(lines)

    def _denial_review(self, pid):
        # Only one request in this synthetic set is denied; the review always shows it.
        d = JOHNSON_DENIAL
        pid = d["auth_id"]
        r = PATIENT_REQUESTS[pid]
        lines = _notice(f"Denial Details - {r['listed_as']} - {r['procedure']}")
        lines.append(f"**Request:** {pid}, {r['patient']}, {r['procedure']}, {r['payer']} - {r['status']}")
        lines.append(f"**Reason:** {d['reason']}")
        lines.append("")
        lines.append("**Missing elements:**")
        for x in d["missing"]:
            lines.append(f"- {x}")
        lines.append("")
        lines.append("**Appeal actions recorded:**")
        for x in d["appeal_actions"]:
            lines.append(f"- {x}")
        lines.append("")
        lines.append(f"**Timeline:** {d['timeline']}")
        lines.append("A qualified reviewer owns the appeal; this summary makes no authorization decision.")
        lines.append("**Next:** return to the Chen authorization?")
        return "\n".join(lines)

    def _request_evidence(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Request Evidence\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Prior-Authorization Evidence Inventory")
        for rid, request in rows:
            lines.extend([
                f"## {rid}: {request['service']}",
                f"- Payer in synthetic source: {request['payer']}",
                f"- Source-recorded workflow state: {request['source_status']} ({request['source_date']})",
                f"- Referenced policy: {request['policy_id']}",
                "",
            ])
            for item, state in request["evidence"].items():
                lines.append(f"- {item}: {state}")
            lines.append("")
        return "\n".join(lines)

    def _criteria_evidence(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Criteria Evidence\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Criteria-to-Evidence Crosswalk")
        for rid, request in rows:
            policy = POLICIES[request["policy_id"]]
            lines.extend([
                f"## {rid} — {policy['title']}",
                f"- Synthetic policy effective date: {policy['effective_date']}",
                "- Checklist only; presence does not establish medical necessity or authorization.",
            ])
            for requirement in policy["requirements"]:
                lines.append(f"- Reviewer check: {requirement}")
            lines.append("")
        return "\n".join(lines)

    def _status_summary(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Status Summary\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Source-Recorded Status Summary")
        for rid, request in rows:
            lines.extend([
                f"- {rid}: {request['source_status']} as recorded on {request['source_date']}",
                "  - This is a source transcription, not an agent determination.",
            ])
        return "\n".join(lines)

    def _appeal_evidence_packet(self, auth_id=None):
        rows = list(_selected_request(auth_id))
        if not rows:
            return f"# Appeal Evidence Packet\n\n> {SAFETY}\n\nNo synthetic request matched `{auth_id}`."
        lines = _notice("Reconsideration Evidence Draft")
        lines.append("A reviewer must confirm that reconsideration or appeal is appropriate and permitted.")
        lines.append("")
        for rid, request in rows:
            lines.extend([
                f"## {rid}",
                f"- Source workflow state: {request['source_status']}",
                f"- Policy reference to verify: {request['policy_id']}",
                "- Include only authorized, minimum-necessary evidence.",
                "- Human utilization reviewer owns rationale, completeness, and submission.",
                "",
            ])
        return "\n".join(lines)


if __name__ == "__main__":
    agent = PriorAuthorizationAgent()
    for op in DEMO_OPERATIONS:
        print(agent.perform(operation=op))
        print()
