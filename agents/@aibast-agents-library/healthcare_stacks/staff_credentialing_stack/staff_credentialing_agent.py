"""
Staff Credentialing Agent for Healthcare.

Manages healthcare staff credential tracking, expiration alerts,
verification audits, and onboarding checklists for licenses, certifications,
DEA registrations, and continuing education requirements.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/staff-credentialing",
    "version": "1.0.0",
    "display_name": "Staff Credentialing Agent",
    "description": "Manages staff credential tracking, expiration alerts, verification audits, and onboarding checklists for healthcare organizations.",
    "author": "AIBAST",
    "tags": ["credentialing", "licenses", "certifications", "dea", "compliance", "healthcare"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

STAFF_CREDENTIALS = {
    "STAFF-001": {
        "name": "Dr. Anita Patel",
        "role": "Physician - Internal Medicine",
        "npi": "1234567890",
        "hire_date": "2019-06-15",
        "credentials": [
            {"type": "Medical License", "issuer": "Illinois DFPR", "number": "036-123456", "issued": "2023-07-01", "expires": "2026-06-30", "status": "active", "verified": True},
            {"type": "DEA Registration", "issuer": "DEA", "number": "AP1234567", "issued": "2024-01-15", "expires": "2027-01-14", "status": "active", "verified": True},
            {"type": "Board Certification - Internal Medicine", "issuer": "ABIM", "number": "ABIM-884210", "issued": "2020-09-01", "expires": "2030-08-31", "status": "active", "verified": True},
            {"type": "BLS Certification", "issuer": "AHA", "number": "BLS-29401", "issued": "2025-03-10", "expires": "2027-03-10", "status": "active", "verified": True},
            {"type": "ACLS Certification", "issuer": "AHA", "number": "ACLS-18822", "issued": "2024-11-05", "expires": "2026-11-05", "status": "active", "verified": True},
        ],
        "cme_required_hrs": 50,
        "cme_completed_hrs": 38,
        "malpractice_insurance": {"carrier": "ProAssurance", "policy": "PA-2025-44821", "expires": "2026-12-31", "coverage_mm": 1.0},
    },
    "STAFF-002": {
        "name": "Dr. James Wright",
        "role": "Physician - Family Medicine",
        "npi": "9876543210",
        "hire_date": "2021-01-10",
        "credentials": [
            {"type": "Medical License", "issuer": "Illinois DFPR", "number": "036-654321", "issued": "2024-07-01", "expires": "2027-06-30", "status": "active", "verified": True},
            {"type": "DEA Registration", "issuer": "DEA", "number": "JW9876543", "issued": "2023-05-20", "expires": "2026-05-19", "status": "active", "verified": True},
            {"type": "Board Certification - Family Medicine", "issuer": "ABFM", "number": "ABFM-552104", "issued": "2021-12-01", "expires": "2031-11-30", "status": "active", "verified": True},
            {"type": "BLS Certification", "issuer": "AHA", "number": "BLS-30218", "issued": "2024-08-22", "expires": "2026-08-22", "status": "active", "verified": True},
        ],
        "cme_required_hrs": 50,
        "cme_completed_hrs": 52,
        "malpractice_insurance": {"carrier": "Coverys", "policy": "COV-2025-91024", "expires": "2026-12-31", "coverage_mm": 1.0},
    },
    "STAFF-003": {
        "name": "Lisa Chen, RN",
        "role": "Registered Nurse",
        "npi": "5551234567",
        "hire_date": "2022-08-01",
        "credentials": [
            {"type": "RN License", "issuer": "Illinois DFPR", "number": "041-789012", "issued": "2024-05-31", "expires": "2026-05-31", "status": "active", "verified": True},
            {"type": "BLS Certification", "issuer": "AHA", "number": "BLS-41092", "issued": "2025-01-15", "expires": "2027-01-15", "status": "active", "verified": True},
            {"type": "ACLS Certification", "issuer": "AHA", "number": "ACLS-22104", "issued": "2024-06-10", "expires": "2026-06-10", "status": "active", "verified": True},
            {"type": "PALS Certification", "issuer": "AHA", "number": "PALS-15580", "issued": "2023-09-20", "expires": "2025-09-20", "status": "expired", "verified": False},
        ],
        "cme_required_hrs": 20,
        "cme_completed_hrs": 14,
        "malpractice_insurance": {"carrier": "NSO", "policy": "NSO-2025-67210", "expires": "2026-06-30", "coverage_mm": 0.5},
    },
    "STAFF-004": {
        "name": "Mark Johnson, PA-C",
        "role": "Physician Assistant",
        "npi": "4449876543",
        "hire_date": "2023-03-15",
        "credentials": [
            {"type": "PA License", "issuer": "Illinois DFPR", "number": "085-345678", "issued": "2023-03-01", "expires": "2026-02-28", "status": "expired", "verified": False},
            {"type": "NCCPA Certification", "issuer": "NCCPA", "number": "NCCPA-778410", "issued": "2023-01-01", "expires": "2033-12-31", "status": "active", "verified": True},
            {"type": "DEA Registration", "issuer": "DEA", "number": "MJ3456789", "issued": "2023-04-01", "expires": "2026-03-31", "status": "active", "verified": True},
            {"type": "BLS Certification", "issuer": "AHA", "number": "BLS-52201", "issued": "2025-06-20", "expires": "2027-06-20", "status": "active", "verified": True},
        ],
        "cme_required_hrs": 100,
        "cme_completed_hrs": 68,
        "malpractice_insurance": {"carrier": "HPSO", "policy": "HPSO-2025-33104", "expires": "2026-09-30", "coverage_mm": 0.5},
    },
}

ONBOARDING_CHECKLIST_TEMPLATE = [
    {"item": "Background check completed", "category": "compliance"},
    {"item": "License verification (primary source)", "category": "credentialing"},
    {"item": "DEA verification (if applicable)", "category": "credentialing"},
    {"item": "Board certification verification", "category": "credentialing"},
    {"item": "Malpractice insurance verification", "category": "compliance"},
    {"item": "NPI validation", "category": "credentialing"},
    {"item": "Payer enrollment initiated", "category": "billing"},
    {"item": "EHR access provisioned", "category": "it"},
    {"item": "HIPAA training completed", "category": "compliance"},
    {"item": "Orientation completed", "category": "hr"},
    {"item": "Privileges approved by medical staff committee", "category": "credentialing"},
    {"item": "Malpractice tail coverage confirmed", "category": "compliance"},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _credential_status():
    statuses = []
    for sid, staff in STAFF_CREDENTIALS.items():
        active = sum(1 for c in staff["credentials"] if c["status"] == "active")
        expired = sum(1 for c in staff["credentials"] if c["status"] == "expired")
        total = len(staff["credentials"])
        cme_pct = round(staff["cme_completed_hrs"] / staff["cme_required_hrs"] * 100, 1) if staff["cme_required_hrs"] else 0
        statuses.append({
            "id": sid, "name": staff["name"], "role": staff["role"],
            "total_credentials": total, "active": active, "expired": expired,
            "cme_pct": cme_pct, "cme_completed": staff["cme_completed_hrs"],
            "cme_required": staff["cme_required_hrs"],
            "malpractice_expires": staff["malpractice_insurance"]["expires"],
        })
    return {"staff": statuses}


def _expiration_alerts():
    alerts = []
    for sid, staff in STAFF_CREDENTIALS.items():
        for cred in staff["credentials"]:
            if cred["status"] == "expired":
                alerts.append({
                    "staff_id": sid, "name": staff["name"],
                    "credential": cred["type"], "expired": cred["expires"],
                    "severity": "critical", "action": "Immediate renewal required",
                })
            elif cred["expires"] <= "2026-06-30":
                alerts.append({
                    "staff_id": sid, "name": staff["name"],
                    "credential": cred["type"], "expired": cred["expires"],
                    "severity": "warning", "action": "Renewal due within 90 days",
                })
        mal = staff["malpractice_insurance"]
        if mal["expires"] <= "2026-06-30":
            alerts.append({
                "staff_id": sid, "name": staff["name"],
                "credential": "Malpractice Insurance", "expired": mal["expires"],
                "severity": "warning", "action": "Policy renewal needed",
            })
    alerts.sort(key=lambda x: (0 if x["severity"] == "critical" else 1, x["expired"]))
    return {"alerts": alerts, "total": len(alerts),
            "critical": sum(1 for a in alerts if a["severity"] == "critical")}


def _verification_audit():
    audit_items = []
    for sid, staff in STAFF_CREDENTIALS.items():
        for cred in staff["credentials"]:
            audit_items.append({
                "staff_id": sid, "name": staff["name"],
                "credential": cred["type"], "number": cred["number"],
                "issuer": cred["issuer"], "verified": cred["verified"],
                "status": cred["status"],
            })
    verified = sum(1 for a in audit_items if a["verified"])
    total = len(audit_items)
    return {"items": audit_items, "total": total, "verified": verified,
            "verification_rate": round(verified / total * 100, 1) if total else 0}


def _onboarding_checklist():
    return {"checklist": ONBOARDING_CHECKLIST_TEMPLATE,
            "total_items": len(ONBOARDING_CHECKLIST_TEMPLATE),
            "categories": list(set(item["category"] for item in ONBOARDING_CHECKLIST_TEMPLATE))}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class StaffCredentialingAgent(BasicAgent):
    """Staff credential tracking and compliance management agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/staff-credentialing"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "credential_status",
                            "expiration_alerts",
                            "verification_audit",
                            "onboarding_checklist",
                        ],
                        "description": "The credentialing operation to perform.",
                    },
                    "staff_id": {
                        "type": "string",
                        "description": "Optional staff ID to filter results.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "credential_status")
        if op == "credential_status":
            return self._credential_status()
        elif op == "expiration_alerts":
            return self._expiration_alerts()
        elif op == "verification_audit":
            return self._verification_audit()
        elif op == "onboarding_checklist":
            return self._onboarding_checklist()
        return f"**Error:** Unknown operation `{op}`."

    def _credential_status(self) -> str:
        data = _credential_status()
        lines = [
            "# Staff Credential Status",
            "",
            "| Staff Member | Role | Credentials | Active | Expired | CME Progress | Malpractice Exp. |",
            "|-------------|------|------------|--------|---------|-------------|-----------------|",
        ]
        for s in data["staff"]:
            lines.append(
                f"| {s['name']} | {s['role']} | {s['total_credentials']} "
                f"| {s['active']} | {s['expired']} | {s['cme_completed']}/{s['cme_required']} ({s['cme_pct']}%) "
                f"| {s['malpractice_expires']} |"
            )
        return "\n".join(lines)

    def _expiration_alerts(self) -> str:
        data = _expiration_alerts()
        if data["total"] == 0:
            return "# Expiration Alerts\n\nNo credentials expiring within the alert window."
        lines = [
            "# Credential Expiration Alerts",
            "",
            f"**Total Alerts:** {data['total']} | **Critical:** {data['critical']}",
            "",
            "| Severity | Staff Member | Credential | Expires | Action Required |",
            "|----------|-------------|------------|---------|----------------|",
        ]
        for a in data["alerts"]:
            lines.append(
                f"| {a['severity'].upper()} | {a['name']} | {a['credential']} "
                f"| {a['expired']} | {a['action']} |"
            )
        return "\n".join(lines)

    def _verification_audit(self) -> str:
        data = _verification_audit()
        lines = [
            "# Verification Audit Report",
            "",
            f"**Total Credentials:** {data['total']} | **Verified:** {data['verified']} "
            f"| **Verification Rate:** {data['verification_rate']}%",
            "",
            "| Staff Member | Credential | Number | Issuer | Verified | Status |",
            "|-------------|------------|--------|--------|----------|--------|",
        ]
        for item in data["items"]:
            v = "YES" if item["verified"] else "NO"
            lines.append(
                f"| {item['name']} | {item['credential']} | {item['number']} "
                f"| {item['issuer']} | {v} | {item['status'].upper()} |"
            )
        return "\n".join(lines)

    def _onboarding_checklist(self) -> str:
        data = _onboarding_checklist()
        lines = [
            "# New Staff Onboarding Checklist",
            "",
            f"**Total Items:** {data['total_items']}",
            f"**Categories:** {', '.join(sorted(data['categories']))}",
            "",
            "| # | Item | Category |",
            "|---|------|----------|",
        ]
        for i, item in enumerate(data["checklist"], 1):
            lines.append(f"| {i} | {item['item']} | {item['category'].upper()} |")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    agent = StaffCredentialingAgent()
    for op in ["credential_status", "expiration_alerts", "verification_audit", "onboarding_checklist"]:
        print(f"\n{'='*60}")
        print(f"Operation: {op}")
        print("=" * 60)
        print(agent.perform(operation=op))
