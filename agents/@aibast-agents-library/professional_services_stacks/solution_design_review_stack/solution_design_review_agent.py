"""
Solution Design Review Agent

Read-only design-document support for an enterprise architecture practice, built on a fixed synthetic initiative
(a customer delivery notifications platform at the fictional Northwind Traders): intake of the design template,
discovery notes and initiative brief; an architecture vision draft; the current-state component baseline; the
non-functional requirements matrix with owners and gaps; the target design with its inventory delta; and a
review-board readiness check with a confidence score and severity-ranked gaps. Every draft is for the architect to
review; the agent never submits to the review board, changes an inventory record, or approves a design.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/solution-design-review",
    "version": "1.0.0",
    "display_name": "Solution Design Review Agent",
    "description": "Help architects draft and self-check a solution design document before the architecture review board: intake of the template, discovery notes and initiative brief, an architecture vision, the current-state baseline, the non-functional requirements matrix with owners and gaps, the target design with its inventory changes, and a readiness check with a confidence score and severity-ranked gaps. The agent is read-only; it never submits to the review board, changes an inventory record, or approves a design.",
    "author": "AIBAST",
    "tags": ["architecture", "solution-design", "design-review", "non-functional-requirements", "professional-services"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic data (fixed initiative snapshot; every person, system and value is fictional)
# ---------------------------------------------------------------------------

INITIATIVE = {
    "id": "INIT-2026-031",
    "org": "Northwind Traders",
    "project": "Delivery Notifications Platform",
    "driver": "Customers ask where their order is; 38% of contact-center calls are delivery-status questions",
    "objective": "Send proactive, consent-aware delivery updates by text and email from one orchestration service",
    "sponsor": "Avery Lindqvist, VP Customer Operations",
    "business_owner": "Mara Okonjo, Director Customer Experience",
    "technical_owner": "Theo Brandt, Lead Solution Architect",
    "review_date": "2026-08-12",
}

INPUTS = [
    {"input": "Solution design template", "detail": "4 sections to fill: Vision, Current State, Requirements, Target Design"},
    {"input": "Discovery session notes", "detail": "2 workshops, 41 captured statements"},
    {"input": "Initiative brief", "detail": f"{INITIATIVE['id']} {INITIATIVE['project']}"},
]

SEQUENCE = [
    "Architecture vision (scope, stakeholders, impacted domains)",
    "Current-state baseline (components in scope)",
    "Non-functional requirements matrix (owners, gaps, variances)",
    "Target design (new, changed and retired components)",
    "Readiness check before the review board",
]

SCOPE_IN = ["Delivery status events from shipment tracking", "Text and email notifications",
            "Customer channel preferences and consent", "Retirement of the legacy text and batch email tools"]
SCOPE_OUT = ["Marketing campaigns", "In-app push notifications (next phase)", "Carrier contract changes"]
CONSTRAINTS = ["Consent must be checked before every send", "Launch before the peak season freeze on 2026-10-15",
               "Reuse the existing integration bus"]
DOMAINS = {"Business": True, "Data": True, "Application": True, "Technology": True}
WORKGROUPS = ["Interfaces and APIs", "Information security", "Data protection"]

COMPONENTS = [
    {"id": "CI-101", "name": "Order Management System", "domain": "Application", "owner": "Order Platform team", "status": "Supported"},
    {"id": "CI-102", "name": "Customer Profile Store", "domain": "Data", "owner": "Customer Data team", "status": "Supported"},
    {"id": "CI-103", "name": "Legacy Text Gateway", "domain": "Technology", "owner": "Messaging team", "status": "End of support 2026-12-31"},
    {"id": "CI-104", "name": "Shipment Tracking Service", "domain": "Application", "owner": "Logistics Apps team", "status": "Supported"},
    {"id": "CI-105", "name": "Batch Email Scheduler", "domain": "Application", "owner": "Messaging team", "status": "End of support 2026-09-30"},
    {"id": "CI-106", "name": "Integration Bus", "domain": "Technology", "owner": "Middleware team", "status": "Supported"},
    {"id": "CI-107", "name": "Consent Records Table", "domain": "Data", "owner": "Privacy and Compliance team", "status": "Supported"},
]

NFRS = [
    {"id": "NFR-01", "area": "Availability", "criterion": "99.9% monthly availability", "owner": "Operations Engineering", "status": "Met in design"},
    {"id": "NFR-02", "area": "Latency", "criterion": "Notification sent within 60 seconds of the event (p95)", "owner": "Messaging team", "status": "Met in design"},
    {"id": "NFR-03", "area": "Privacy", "criterion": "Consent checked before every send", "owner": "Privacy and Compliance team", "status": "Met in design"},
    {"id": "NFR-04", "area": "Retention", "criterion": "Message history kept 13 months, then purged", "owner": "", "status": "Gap"},
    {"id": "NFR-05", "area": "Security", "criterion": "Encryption in transit and at rest", "owner": "Information Security team", "status": "Met in design"},
    {"id": "NFR-06", "area": "Capacity", "criterion": "40 messages per second at peak", "owner": "Messaging team", "status": "Variance candidate",
     "note": "Launch design supports 25 per second; scale-out planned for phase 2"},
    {"id": "NFR-07", "area": "Auditability", "criterion": "Every send logged with the consent decision", "owner": "", "status": "Gap"},
    {"id": "NFR-08", "area": "Accessibility", "criterion": "Message templates meet the accessibility standard", "owner": "Customer Content team", "status": "Met in design"},
]

TARGET = {
    "new": [
        {"id": "CI-201", "name": "Notification Orchestrator", "domain": "Application"},
        {"id": "CI-202", "name": "Preference Center API", "domain": "Application"},
        {"id": "CI-203", "name": "Delivery Event Stream", "domain": "Technology"},
    ],
    "changed": [
        {"id": "CI-104", "name": "Shipment Tracking Service", "change": "Publishes delivery status events"},
        {"id": "CI-107", "name": "Consent Records Table", "change": "Adds per-channel preference fields"},
    ],
    "retired": [
        {"id": "CI-103", "name": "Legacy Text Gateway", "change": "Replaced by the orchestrator's text channel"},
        {"id": "CI-105", "name": "Batch Email Scheduler", "change": "Replaced by the orchestrator's email channel"},
    ],
    "domains": ["Business", "Data", "Application", "Technology"],
    "diagrams": ["Business", "Data", "Application", "Technology"],
}

SEVERITY_ORDER = ["HIGH", "MED", "LOW"]

_GATE = (
    "Synthetic design support only. Every person, system and value is fictional. Nothing was submitted to the "
    "review board, no inventory record was changed, and no design decision was made; the architect owns every section."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _impacted():
    return [d for d in ["Business", "Data", "Application", "Technology"] if DOMAINS[d]]


def _baseline_domains():
    seen = []
    for c in COMPONENTS:
        if c["domain"] not in seen:
            seen.append(c["domain"])
    return seen


def _checks():
    """The review-board checklist, each with pass/fail, severity and the evidence behind it."""
    impacted = _impacted()
    base = _baseline_domains()
    no_base = [d for d in impacted if d not in base]
    no_target = [d for d in impacted if d not in TARGET["domains"]]
    no_owner = [n["id"] for n in NFRS if n["owner"] == ""]
    variances = [n["id"] for n in NFRS if n["status"] == "Variance candidate" and not n.get("response")]
    eos = [c["id"] for c in COMPONENTS if c["status"].startswith("End of support")]
    retired = [r["id"] for r in TARGET["retired"]]
    eos_open = [c for c in eos if c not in retired]
    no_diagram = [d for d in impacted if d not in TARGET["diagrams"]]
    return [
        {"check": "Every impacted domain has a current-state baseline", "ok": not no_base, "sev": "HIGH",
         "evidence": ("Missing: " + ", ".join(no_base)) if no_base else "All domains covered"},
        {"check": "Every impacted domain has a target design", "ok": not no_target, "sev": "HIGH",
         "evidence": ("Missing: " + ", ".join(no_target)) if no_target else "All domains covered"},
        {"check": "Every non-functional requirement has a named owner", "ok": not no_owner, "sev": "HIGH",
         "evidence": ("No owner: " + ", ".join(no_owner)) if no_owner else "All owned"},
        {"check": "Every variance has a documented architect response", "ok": not variances, "sev": "MED",
         "evidence": ("Open: " + ", ".join(variances)) if variances else "None open"},
        {"check": "Scope in and out is stated", "ok": len(SCOPE_IN) > 0 and len(SCOPE_OUT) > 0, "sev": "MED",
         "evidence": f"{len(SCOPE_IN)} in, {len(SCOPE_OUT)} out"},
        {"check": "Constraints are populated", "ok": len(CONSTRAINTS) > 0, "sev": "MED",
         "evidence": f"{len(CONSTRAINTS)} constraints"},
        {"check": "End-of-support components have a disposition", "ok": not eos_open, "sev": "MED",
         "evidence": ("Open: " + ", ".join(eos_open)) if eos_open else "Both retired in the target design"},
        {"check": "Inventory changes are listed", "ok": len(TARGET["new"]) + len(TARGET["changed"]) + len(TARGET["retired"]) > 0,
         "sev": "LOW", "evidence": f"{len(TARGET['new'])} new, {len(TARGET['changed'])} changed, {len(TARGET['retired'])} retired"},
        {"check": "Review workgroups are identified", "ok": len(WORKGROUPS) > 0, "sev": "LOW",
         "evidence": ", ".join(WORKGROUPS)},
        {"check": "Each target domain references a diagram", "ok": not no_diagram, "sev": "LOW",
         "evidence": ("Missing: " + ", ".join(no_diagram)) if no_diagram else "4 of 4 referenced"},
    ]


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

OPERATIONS = [
    "design_intake", "architecture_vision", "current_state", "requirements_matrix", "target_design", "readiness_check",
]


class SolutionDesignReviewAgent(BasicAgent):
    """Solution design document drafting and self-check support (read-only, synthetic)."""

    def __init__(self):
        self.name = "SolutionDesignReviewAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Always call this tool when an architect works on the fictional Northwind Traders delivery "
                "notifications design: handing over the design template, discovery notes and initiative brief "
                "and asking where to start; drafting the vision (scope, stakeholders, impacted architecture "
                "domains); the current state of the systems in scope; which non-functional requirements apply and "
                "who owns them; drafting the target design and its inventory changes; and whether the design is "
                "ready for the review board. Call it right away; the inputs are already loaded and every operation "
                "has demo defaults. It never submits to the review board, changes inventory, or approves a design."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "design_intake when the architect hands over the template, discovery notes and brief "
                            "and asks where to start; architecture_vision for scope, stakeholders, impacted domains, "
                            "constraints and review workgroups; current_state for the current systems or components "
                            "in scope; requirements_matrix for the non-functional requirements, their owners, gaps "
                            "and variances; target_design for the target architecture and what changes in the "
                            "inventory; readiness_check for review-board readiness, the confidence score and gaps."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "design_intake")
        handlers = {
            "design_intake": self._design_intake,
            "architecture_vision": self._architecture_vision,
            "current_state": self._current_state,
            "requirements_matrix": self._requirements_matrix,
            "target_design": self._target_design,
            "readiness_check": self._readiness_check,
        }
        handler = handlers.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`. Operations: {', '.join(OPERATIONS)}."
        return handler()

    def _design_intake(self) -> str:
        i = INITIATIVE
        out = [
            f"# Design Intake - {i['id']} {i['project']}",
            "",
            f"**Organization:** {i['org']} | **Review board date:** {i['review_date']}",
            "",
            "| Input received | Detail |",
            "|----------------|--------|",
        ]
        for x in INPUTS:
            out.append(f"| {x['input']} | {x['detail']} |")
        out += ["", "**Recommended fill sequence:**"]
        n = 0
        for s in SEQUENCE:
            n += 1
            out.append(f"{n}. {s}")
        out += [
            "",
            f"{len(INPUTS)} inputs received; {len(SEQUENCE)} steps from intake to readiness. Start with the vision.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _architecture_vision(self) -> str:
        i = INITIATIVE
        impacted = _impacted()
        out = [
            f"# Architecture Vision - DRAFT ({i['id']})",
            "",
            f"**Business driver:** {i['driver']}.",
            f"**Objective:** {i['objective']}.",
            "",
            "| Stakeholder | Role |",
            "|-------------|------|",
            f"| {i['sponsor']} | Executive sponsor |",
            f"| {i['business_owner']} | Business owner |",
            f"| {i['technical_owner']} | Technical owner |",
            "",
            "**In scope:** " + "; ".join(SCOPE_IN) + ".",
            "**Out of scope:** " + "; ".join(SCOPE_OUT) + ".",
            "",
            f"**Impacted domains ({len(impacted)} of 4):** " + ", ".join(impacted) + ".",
            "**Constraints:** " + "; ".join(CONSTRAINTS) + ".",
            "**Review workgroups:** " + ", ".join(WORKGROUPS) + ".",
            "",
            "Draft for the architect to edit. Next: the current-state baseline.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _current_state(self) -> str:
        eos = [c for c in COMPONENTS if c["status"].startswith("End of support")]
        base = _baseline_domains()
        missing = [d for d in _impacted() if d not in base]
        out = [
            f"# Current-State Baseline - {len(COMPONENTS)} Components in Scope",
            "",
            "| Component | Name | Domain | Owner | Lifecycle |",
            "|-----------|------|--------|-------|-----------|",
        ]
        for c in COMPONENTS:
            out.append(f"| {c['id']} | {c['name']} | {c['domain']} | {c['owner']} | {c['status']} |")
        out += [
            "",
            f"**End of support:** {len(eos)} components - " + ", ".join(f"{c['id']} {c['name']}" for c in eos) + ".",
            "**Domains with a baseline:** " + ", ".join(base) + ".",
        ]
        if missing:
            out.append(f"**Gap:** no current-state baseline for the {', '.join(missing)} domain (process and "
                       "capability view); add it before the review.")
        out += ["", f"> {_GATE}"]
        return "\n".join(out)

    def _requirements_matrix(self) -> str:
        out = [
            f"# Non-Functional Requirements Matrix - {len(NFRS)} Requirements",
            "",
            "| ID | Area | Acceptance criterion | Owner | Status |",
            "|----|------|----------------------|-------|--------|",
        ]
        met = 0
        no_owner = []
        variance = []
        for n in NFRS:
            owner = n["owner"] if n["owner"] else "MISSING OWNER"
            status = n["status"]
            if n.get("note"):
                status = f"{status} - {n['note']}"
            out.append(f"| {n['id']} | {n['area']} | {n['criterion']} | {owner} | {status} |")
            if n["status"] == "Met in design":
                met += 1
            if not n["owner"]:
                no_owner.append(n["id"])
            if n["status"] == "Variance candidate":
                variance.append(n["id"])
        out += [
            "",
            f"**Summary:** {met} met in design, {len(no_owner)} missing owners ({', '.join(no_owner)}), "
            f"{len(variance)} variance candidate ({', '.join(variance)}).",
            "Next: name owners for the gaps and write the architect response for the variance.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _target_design(self) -> str:
        t = TARGET
        out = [
            f"# Target Design - DRAFT ({INITIATIVE['project']})",
            "",
            "One notification orchestrator consumes delivery events from the integration bus, checks consent and "
            "channel preference, and sends by text or email; the two legacy senders are retired.",
            "",
            "| Change | Component | Name | Detail |",
            "|--------|-----------|------|--------|",
        ]
        for c in t["new"]:
            out.append(f"| New | {c['id']} | {c['name']} | {c['domain']} |")
        for c in t["changed"]:
            out.append(f"| Changed | {c['id']} | {c['name']} | {c['change']} |")
        for c in t["retired"]:
            out.append(f"| Retired | {c['id']} | {c['name']} | {c['change']} |")
        total = len(t["new"]) + len(t["changed"]) + len(t["retired"])
        out += [
            "",
            f"**Inventory delta:** {len(t['new'])} new, {len(t['changed'])} changed, {len(t['retired'])} retired "
            f"= {total} inventory updates to register after build (not registered by this agent).",
            "**Target domains drafted:** " + ", ".join(t["domains"]) + "; a diagram reference is included for each.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)

    def _readiness_check(self) -> str:
        checks = _checks()
        passed = len([c for c in checks if c["ok"]])
        conf = int(round(passed * 100 / len(checks)))
        failed = [c for c in checks if not c["ok"]]
        counts = {}
        for s in SEVERITY_ORDER:
            counts[s] = len([c for c in failed if c["sev"] == s])
        if counts["HIGH"] > 0:
            rec = "Revise before the review board"
        elif failed:
            rec = "Approved with conditions"
        else:
            rec = "Ready for the review board"
        out = [
            f"# Review-Board Readiness - {INITIATIVE['id']}",
            "",
            f"**Confidence: {conf}%** ({passed} of {len(checks)} checks pass) | **Gaps:** {counts['HIGH']} HIGH, "
            f"{counts['MED']} MED, {counts['LOW']} LOW | **Recommendation:** {rec}",
            "",
            "| Severity | Gap | Evidence |",
            "|----------|-----|----------|",
        ]
        for s in SEVERITY_ORDER:
            for c in failed:
                if c["sev"] == s:
                    out.append(f"| {s} | {c['check']} | {c['evidence']} |")
        out += [
            "",
            "**To close before the review:** add the Business baseline; name owners for NFR-04 and NFR-07; write the "
            "architect response for NFR-06.",
            f"Closing all {len(failed)} gaps takes the checklist to {len(checks)} of {len(checks)}.",
            "",
            "Status: self-check for the architect. Not submitted to the review board.",
            "",
            f"> {_GATE}",
        ]
        return "\n".join(out)


if __name__ == "__main__":
    agent = SolutionDesignReviewAgent()
    for op in OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
