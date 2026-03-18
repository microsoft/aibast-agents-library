"""
Prior Authorization Agent for Healthcare.

Manages prior authorization requests, checks clinical criteria against
payer rules, tracks authorization status, and prepares appeal documentation
for denied or pending authorizations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/prior-authorization",
    "version": "1.0.0",
    "display_name": "Prior Authorization Agent",
    "description": "Manages prior authorization requests, clinical criteria checks, status tracking, and appeal preparation for healthcare payers.",
    "author": "AIBAST",
    "tags": ["prior-auth", "authorization", "payer", "clinical-criteria", "appeals", "healthcare"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

AUTH_REQUESTS = {
    "AUTH-4001": {
        "patient": "Margaret Sullivan",
        "patient_id": "PT-10045",
        "procedure": "Left Knee MRI without Contrast",
        "cpt_code": "73721",
        "diagnosis": "M17.12 - Primary osteoarthritis, left knee",
        "requesting_provider": "Dr. Anita Patel",
        "payer": "Blue Cross Blue Shield of Illinois",
        "plan": "PPO Gold",
        "submitted_date": "2026-03-13",
        "status": "approved",
        "decision_date": "2026-03-14",
        "auth_number": "BCBS-AUTH-884210",
        "valid_through": "2026-06-14",
        "notes": "Auto-approved based on clinical criteria match.",
    },
    "AUTH-4002": {
        "patient": "Robert Kim",
        "patient_id": "PT-10078",
        "procedure": "Cardiac Stress Test (Nuclear)",
        "cpt_code": "78452",
        "diagnosis": "R07.9 - Chest pain, unspecified",
        "requesting_provider": "Dr. James Wright",
        "payer": "Aetna",
        "plan": "HMO Select",
        "submitted_date": "2026-03-15",
        "status": "pending_review",
        "decision_date": None,
        "auth_number": None,
        "valid_through": None,
        "notes": "Requires peer-to-peer review. Additional documentation requested.",
    },
    "AUTH-4003": {
        "patient": "Maria Gonzalez",
        "patient_id": "PT-20003",
        "procedure": "Total Hip Arthroplasty",
        "cpt_code": "27130",
        "diagnosis": "M16.11 - Primary osteoarthritis, right hip",
        "requesting_provider": "Dr. Michael Torres",
        "payer": "Medicare Part B",
        "plan": "Original Medicare",
        "submitted_date": "2026-03-10",
        "status": "approved",
        "decision_date": "2026-03-11",
        "auth_number": "MCR-AUTH-THA-99201",
        "valid_through": "2026-09-11",
        "notes": "Medicare LCD criteria met. Pre-op clearance required.",
    },
    "AUTH-4004": {
        "patient": "David Nguyen",
        "patient_id": "PT-20002",
        "procedure": "Lumbar Spine MRI with Contrast",
        "cpt_code": "72149",
        "diagnosis": "M54.5 - Low back pain",
        "requesting_provider": "Dr. James Wright",
        "payer": "Aetna",
        "plan": "HMO Select",
        "submitted_date": "2026-03-08",
        "status": "denied",
        "decision_date": "2026-03-12",
        "auth_number": None,
        "valid_through": None,
        "notes": "Denied: Conservative therapy requirement not met. Minimum 6 weeks PT required.",
    },
}

CLINICAL_CRITERIA = {
    "73721": {
        "procedure": "Knee MRI",
        "payer_rules": {
            "BCBS": {"requires": ["Physical exam documented", "X-ray completed", "Conservative therapy >= 4 weeks"], "auto_approve": True},
            "Aetna": {"requires": ["Physical exam documented", "X-ray completed", "Conservative therapy >= 6 weeks", "Specialist referral"], "auto_approve": False},
            "Medicare": {"requires": ["Physical exam documented", "Imaging appropriate per LCD"], "auto_approve": True},
        },
        "avg_turnaround_days": 1.5,
        "approval_rate_pct": 92,
    },
    "78452": {
        "procedure": "Nuclear Cardiac Stress Test",
        "payer_rules": {
            "BCBS": {"requires": ["Cardiac risk factors documented", "EKG performed", "Symptoms documented"], "auto_approve": False},
            "Aetna": {"requires": ["Cardiac risk factors documented", "EKG performed", "Peer-to-peer if age < 55"], "auto_approve": False},
            "Medicare": {"requires": ["Symptoms documented", "EKG performed"], "auto_approve": True},
        },
        "avg_turnaround_days": 3.2,
        "approval_rate_pct": 78,
    },
    "27130": {
        "procedure": "Total Hip Arthroplasty",
        "payer_rules": {
            "BCBS": {"requires": ["Failed conservative therapy >= 3 months", "Imaging confirming severe OA", "Functional impairment documented"], "auto_approve": False},
            "Aetna": {"requires": ["Failed conservative therapy >= 3 months", "Imaging", "Functional assessment", "BMI < 40"], "auto_approve": False},
            "Medicare": {"requires": ["LCD criteria met", "Pre-op clearance", "Imaging"], "auto_approve": True},
        },
        "avg_turnaround_days": 5.0,
        "approval_rate_pct": 85,
    },
    "72149": {
        "procedure": "Lumbar MRI with Contrast",
        "payer_rules": {
            "BCBS": {"requires": ["Conservative therapy >= 4 weeks", "Red flags absent", "Physical exam documented"], "auto_approve": True},
            "Aetna": {"requires": ["Conservative therapy >= 6 weeks", "Physical therapy documented", "Red flags absent"], "auto_approve": False},
            "Medicare": {"requires": ["Symptoms documented", "Exam documented"], "auto_approve": True},
        },
        "avg_turnaround_days": 2.0,
        "approval_rate_pct": 74,
    },
}

PAYER_APPROVAL_RATES = {
    "Blue Cross Blue Shield of Illinois": {"overall_pct": 88, "avg_days": 1.8, "appeal_success_pct": 62},
    "Aetna": {"overall_pct": 72, "avg_days": 4.1, "appeal_success_pct": 48},
    "Medicare Part B": {"overall_pct": 94, "avg_days": 1.2, "appeal_success_pct": 71},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _auth_request_status():
    requests = []
    for aid, auth in AUTH_REQUESTS.items():
        requests.append({
            "id": aid, "patient": auth["patient"], "procedure": auth["procedure"],
            "cpt": auth["cpt_code"], "payer": auth["payer"], "status": auth["status"],
            "submitted": auth["submitted_date"], "decision": auth["decision_date"] or "Pending",
            "auth_number": auth["auth_number"] or "N/A",
        })
    status_counts = {}
    for r in requests:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
    return {"requests": requests, "status_counts": status_counts}


def _clinical_criteria_check():
    checks = []
    for aid, auth in AUTH_REQUESTS.items():
        cpt = auth["cpt_code"]
        criteria = CLINICAL_CRITERIA.get(cpt, {})
        payer_key = None
        for key in ["BCBS", "Aetna", "Medicare"]:
            if key.lower() in auth["payer"].lower():
                payer_key = key
                break
        rules = criteria.get("payer_rules", {}).get(payer_key, {})
        checks.append({
            "auth_id": aid, "patient": auth["patient"],
            "procedure": auth["procedure"], "cpt": cpt,
            "payer": auth["payer"],
            "requirements": rules.get("requires", []),
            "auto_approve": rules.get("auto_approve", False),
            "approval_rate": criteria.get("approval_rate_pct", 0),
            "avg_turnaround": criteria.get("avg_turnaround_days", 0),
        })
    return {"checks": checks}


def _status_tracking():
    tracking = []
    for aid, auth in AUTH_REQUESTS.items():
        payer_stats = PAYER_APPROVAL_RATES.get(auth["payer"], {})
        tracking.append({
            "id": aid, "patient": auth["patient"], "procedure": auth["procedure"],
            "status": auth["status"], "payer": auth["payer"],
            "submitted": auth["submitted_date"],
            "decision": auth["decision_date"] or "Awaiting",
            "valid_through": auth["valid_through"] or "N/A",
            "payer_avg_days": payer_stats.get("avg_days", 0),
            "notes": auth["notes"],
        })
    return {"tracking": tracking}


def _appeal_preparation():
    denied = [auth for auth in AUTH_REQUESTS.values() if auth["status"] == "denied"]
    appeals = []
    for auth in denied:
        payer_stats = PAYER_APPROVAL_RATES.get(auth["payer"], {})
        criteria = CLINICAL_CRITERIA.get(auth["cpt_code"], {})
        payer_key = None
        for key in ["BCBS", "Aetna", "Medicare"]:
            if key.lower() in auth["payer"].lower():
                payer_key = key
                break
        rules = criteria.get("payer_rules", {}).get(payer_key, {})
        appeals.append({
            "patient": auth["patient"], "procedure": auth["procedure"],
            "payer": auth["payer"], "denial_reason": auth["notes"],
            "criteria_not_met": rules.get("requires", []),
            "appeal_success_rate": payer_stats.get("appeal_success_pct", 0),
            "recommended_actions": [
                "Document conservative therapy completed to date",
                "Obtain physical therapy records",
                "Schedule peer-to-peer review with medical director",
                "Submit supplemental clinical documentation",
            ],
        })
    return {"appeals": appeals, "total_denied": len(denied)}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class PriorAuthorizationAgent(BasicAgent):
    """Prior authorization management and clinical criteria checking agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/prior-authorization"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "auth_request",
                            "clinical_criteria_check",
                            "status_tracking",
                            "appeal_preparation",
                        ],
                        "description": "The prior authorization operation to perform.",
                    },
                    "auth_id": {
                        "type": "string",
                        "description": "Optional authorization ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "auth_request")
        if op == "auth_request":
            return self._auth_request()
        elif op == "clinical_criteria_check":
            return self._clinical_criteria_check()
        elif op == "status_tracking":
            return self._status_tracking()
        elif op == "appeal_preparation":
            return self._appeal_preparation()
        return f"**Error:** Unknown operation `{op}`."

    def _auth_request(self) -> str:
        data = _auth_request_status()
        lines = [
            "# Prior Authorization Requests",
            "",
            "**Status Summary:** " + " | ".join(f"{s}: {c}" for s, c in data["status_counts"].items()),
            "",
            "| ID | Patient | Procedure | CPT | Payer | Status | Submitted | Decision | Auth # |",
            "|----|---------|-----------|-----|-------|--------|-----------|----------|--------|",
        ]
        for r in data["requests"]:
            lines.append(
                f"| {r['id']} | {r['patient']} | {r['procedure']} | {r['cpt']} "
                f"| {r['payer']} | {r['status'].upper()} | {r['submitted']} "
                f"| {r['decision']} | {r['auth_number']} |"
            )
        return "\n".join(lines)

    def _clinical_criteria_check(self) -> str:
        data = _clinical_criteria_check()
        lines = ["# Clinical Criteria Check", ""]
        for c in data["checks"]:
            auto = "Yes" if c["auto_approve"] else "No"
            lines.append(f"## {c['auth_id']}: {c['procedure']} ({c['patient']})")
            lines.append(f"**Payer:** {c['payer']} | **Auto-Approve:** {auto}")
            lines.append(f"**Historical Approval Rate:** {c['approval_rate']}% | **Avg Turnaround:** {c['avg_turnaround']} days")
            lines.append("")
            lines.append("**Requirements:**")
            for req in c["requirements"]:
                lines.append(f"- {req}")
            lines.append("")
        return "\n".join(lines)

    def _status_tracking(self) -> str:
        data = _status_tracking()
        lines = ["# Authorization Status Tracking", ""]
        for t in data["tracking"]:
            lines.append(f"## {t['id']}: {t['procedure']}")
            lines.append(f"- Patient: {t['patient']}")
            lines.append(f"- Payer: {t['payer']} (avg decision: {t['payer_avg_days']} days)")
            lines.append(f"- Status: {t['status'].upper()}")
            lines.append(f"- Submitted: {t['submitted']} | Decision: {t['decision']} | Valid Through: {t['valid_through']}")
            lines.append(f"- Notes: {t['notes']}")
            lines.append("")
        return "\n".join(lines)

    def _appeal_preparation(self) -> str:
        data = _appeal_preparation()
        if data["total_denied"] == 0:
            return "# Appeal Preparation\n\nNo denied authorizations requiring appeals."
        lines = [
            "# Appeal Preparation",
            "",
            f"**Total Denied Authorizations:** {data['total_denied']}",
            "",
        ]
        for a in data["appeals"]:
            lines.append(f"## {a['procedure']} - {a['patient']}")
            lines.append(f"**Payer:** {a['payer']}")
            lines.append(f"**Denial Reason:** {a['denial_reason']}")
            lines.append(f"**Appeal Success Rate:** {a['appeal_success_rate']}%")
            lines.append("")
            lines.append("**Criteria Not Met:**")
            for c in a["criteria_not_met"]:
                lines.append(f"- {c}")
            lines.append("")
            lines.append("**Recommended Actions:**")
            for action in a["recommended_actions"]:
                lines.append(f"1. {action}")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = PriorAuthorizationAgent()
    for op in ["auth_request", "clinical_criteria_check", "status_tracking", "appeal_preparation"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
