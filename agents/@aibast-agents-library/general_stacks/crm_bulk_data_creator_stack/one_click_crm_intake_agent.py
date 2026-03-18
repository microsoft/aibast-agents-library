"""
One-Click CRM Intake Agent

Streamlined CRM data intake with form generation, validation, duplicate
detection, and import preview capabilities.

Where a real deployment would connect to CRM APIs, this agent uses a
synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/one-click-crm-intake",
    "version": "1.0.0",
    "display_name": "One-Click CRM Intake",
    "description": "Streamlined CRM data intake with form generation, validation, duplicate detection, and import preview.",
    "author": "AIBAST",
    "tags": ["crm", "intake", "data-validation", "duplicate-detection", "import"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_INTAKE_TEMPLATES = {
    "new_lead": {
        "name": "New Lead Intake", "entity": "lead",
        "fields": [
            {"name": "first_name", "label": "First Name", "type": "text", "required": True, "max_length": 50},
            {"name": "last_name", "label": "Last Name", "type": "text", "required": True, "max_length": 50},
            {"name": "email", "label": "Email", "type": "email", "required": True, "max_length": 100},
            {"name": "company", "label": "Company", "type": "text", "required": True, "max_length": 160},
            {"name": "phone", "label": "Phone", "type": "phone", "required": False, "max_length": 20},
            {"name": "source", "label": "Lead Source", "type": "picklist", "required": True, "options": ["Website", "Referral", "Trade Show", "Cold Call", "LinkedIn"]},
            {"name": "interest", "label": "Product Interest", "type": "picklist", "required": False, "options": ["Platform", "Analytics", "Integration", "Support"]},
            {"name": "notes", "label": "Notes", "type": "textarea", "required": False, "max_length": 2000},
        ],
        "auto_assign_rule": "Round-robin by territory",
    },
    "new_account": {
        "name": "New Account Intake", "entity": "account",
        "fields": [
            {"name": "company_name", "label": "Company Name", "type": "text", "required": True, "max_length": 160},
            {"name": "industry", "label": "Industry", "type": "picklist", "required": True, "options": ["Technology", "Healthcare", "Finance", "Manufacturing", "Retail"]},
            {"name": "revenue", "label": "Annual Revenue", "type": "currency", "required": False},
            {"name": "employees", "label": "Number of Employees", "type": "number", "required": False},
            {"name": "website", "label": "Website", "type": "url", "required": False, "max_length": 200},
            {"name": "city", "label": "City", "type": "text", "required": True, "max_length": 80},
            {"name": "state", "label": "State/Province", "type": "text", "required": True, "max_length": 50},
        ],
        "auto_assign_rule": "Territory-based assignment",
    },
    "support_case": {
        "name": "Support Case Intake", "entity": "incident",
        "fields": [
            {"name": "contact_email", "label": "Contact Email", "type": "email", "required": True, "max_length": 100},
            {"name": "subject", "label": "Subject", "type": "text", "required": True, "max_length": 200},
            {"name": "description", "label": "Description", "type": "textarea", "required": True, "max_length": 5000},
            {"name": "priority", "label": "Priority", "type": "picklist", "required": True, "options": ["Critical", "High", "Medium", "Low"]},
            {"name": "category", "label": "Category", "type": "picklist", "required": True, "options": ["Technical", "Billing", "Feature Request", "General"]},
        ],
        "auto_assign_rule": "Priority-based queue routing",
    },
}

_VALIDATION_RULES = {
    "email": {"pattern": "contains @ and valid domain", "error": "Invalid email format"},
    "phone": {"pattern": "10-15 digits with optional country code", "error": "Invalid phone number"},
    "url": {"pattern": "starts with http:// or https://", "error": "Invalid URL format"},
    "currency": {"pattern": "numeric, non-negative", "error": "Invalid currency value"},
    "required": {"pattern": "non-empty value", "error": "Required field cannot be empty"},
    "max_length": {"pattern": "within character limit", "error": "Value exceeds maximum length"},
}

_DUPLICATE_RULES = {
    "lead": {
        "rules": [
            {"name": "Email Match", "fields": ["email"], "match_type": "exact", "confidence": "High"},
            {"name": "Name + Company", "fields": ["first_name", "last_name", "company"], "match_type": "fuzzy", "confidence": "Medium"},
            {"name": "Phone Match", "fields": ["phone"], "match_type": "exact", "confidence": "High"},
        ],
        "action_on_duplicate": "Flag for review",
    },
    "account": {
        "rules": [
            {"name": "Company Name", "fields": ["company_name"], "match_type": "fuzzy", "confidence": "Medium"},
            {"name": "Website Domain", "fields": ["website"], "match_type": "domain_match", "confidence": "High"},
            {"name": "Name + City", "fields": ["company_name", "city"], "match_type": "fuzzy", "confidence": "Low"},
        ],
        "action_on_duplicate": "Merge suggestion",
    },
    "incident": {
        "rules": [
            {"name": "Subject + Contact", "fields": ["subject", "contact_email"], "match_type": "fuzzy", "confidence": "Medium"},
        ],
        "action_on_duplicate": "Link to existing case",
    },
}

_SAMPLE_INTAKE_BATCH = [
    {"first_name": "Elena", "last_name": "Kowalski", "email": "elena.k@techstart.io", "company": "TechStart Inc", "source": "LinkedIn", "status": "Valid"},
    {"first_name": "Marcus", "last_name": "Thompson", "email": "marcus.t@healthpro.com", "company": "HealthPro Solutions", "source": "Trade Show", "status": "Valid"},
    {"first_name": "Rachel", "last_name": "Chen", "email": "rachel.chen@existing-customer.com", "company": "Existing Customer LLC", "source": "Referral", "status": "Duplicate Detected"},
    {"first_name": "David", "last_name": "", "email": "david@newcorp.com", "company": "NewCorp", "source": "Website", "status": "Validation Error: Last name required"},
    {"first_name": "Sarah", "last_name": "Williams", "email": "sarah.w@summit.com", "company": "Summit Partners", "source": "Cold Call", "status": "Valid"},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _validate_batch(records):
    valid = sum(1 for r in records if r["status"] == "Valid")
    duplicates = sum(1 for r in records if "Duplicate" in r["status"])
    errors = sum(1 for r in records if "Error" in r["status"])
    return valid, duplicates, errors


def _get_template_fields_summary(template):
    required = sum(1 for f in template["fields"] if f["required"])
    optional = len(template["fields"]) - required
    return required, optional


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class OneClickCRMIntakeAgent(BasicAgent):
    """
    One-click CRM intake agent.

    Operations:
        intake_form      - generate intake form for a specific entity
        data_validation  - validate intake data against rules
        duplicate_check  - check for duplicate records
        import_preview   - preview import results before committing
    """

    def __init__(self):
        self.name = "OneClickCRMIntakeAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "intake_form", "data_validation",
                            "duplicate_check", "import_preview",
                        ],
                        "description": "The intake operation to perform",
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Template name (e.g. 'new_lead', 'new_account', 'support_case')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "intake_form")
        template_name = kwargs.get("template_name", "new_lead")
        dispatch = {
            "intake_form": self._intake_form,
            "data_validation": self._data_validation,
            "duplicate_check": self._duplicate_check,
            "import_preview": self._import_preview,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(template_name)

    # ── intake_form ────────────────────────────────────────────
    def _intake_form(self, template_name):
        template = _INTAKE_TEMPLATES.get(template_name)
        if not template:
            keys = ", ".join(_INTAKE_TEMPLATES.keys())
            return f"Template '{template_name}' not found. Available: {keys}"
        req, opt = _get_template_fields_summary(template)
        field_rows = ""
        for f in template["fields"]:
            req_str = "Yes" if f["required"] else "No"
            type_info = f["type"]
            if "options" in f:
                type_info += f" ({', '.join(f['options'][:3])}...)"
            field_rows += f"| {f['label']} | {f['name']} | {type_info} | {req_str} |\n"
        return (
            f"**{template['name']}**\n"
            f"Target Entity: {template['entity']} | Assignment: {template['auto_assign_rule']}\n\n"
            f"| Label | Field Name | Type | Required |\n|---|---|---|---|\n"
            f"{field_rows}\n"
            f"**Summary:** {req} required fields, {opt} optional fields\n\n"
            f"Source: [CRM Intake Engine]\nAgents: OneClickCRMIntakeAgent"
        )

    # ── data_validation ────────────────────────────────────────
    def _data_validation(self, template_name):
        rule_rows = ""
        for rule_name, rule in _VALIDATION_RULES.items():
            rule_rows += f"| {rule_name} | {rule['pattern']} | {rule['error']} |\n"
        valid, dups, errors = _validate_batch(_SAMPLE_INTAKE_BATCH)
        batch_rows = ""
        for r in _SAMPLE_INTAKE_BATCH:
            status_icon = "Pass" if r["status"] == "Valid" else "Fail"
            batch_rows += f"| {r['first_name']} {r['last_name']} | {r['email']} | {status_icon} | {r['status']} |\n"
        return (
            f"**Data Validation Report**\n\n"
            f"**Validation Rules:**\n\n"
            f"| Rule | Pattern | Error Message |\n|---|---|---|\n"
            f"{rule_rows}\n"
            f"**Batch Validation Results ({len(_SAMPLE_INTAKE_BATCH)} records):**\n\n"
            f"| Name | Email | Result | Details |\n|---|---|---|---|\n"
            f"{batch_rows}\n"
            f"**Summary:** {valid} valid, {dups} duplicates, {errors} errors\n\n"
            f"Source: [Validation Engine]\nAgents: OneClickCRMIntakeAgent"
        )

    # ── duplicate_check ────────────────────────────────────────
    def _duplicate_check(self, template_name):
        template = _INTAKE_TEMPLATES.get(template_name)
        entity = template["entity"] if template else "lead"
        dup_config = _DUPLICATE_RULES.get(entity, _DUPLICATE_RULES["lead"])
        rule_rows = ""
        for rule in dup_config["rules"]:
            fields = ", ".join(rule["fields"])
            rule_rows += f"| {rule['name']} | {fields} | {rule['match_type']} | {rule['confidence']} |\n"
        return (
            f"**Duplicate Detection: {entity.title()}**\n\n"
            f"**Detection Rules:**\n\n"
            f"| Rule | Fields | Match Type | Confidence |\n|---|---|---|---|\n"
            f"{rule_rows}\n"
            f"**Action on Duplicate:** {dup_config['action_on_duplicate']}\n\n"
            f"**Scan Results (sample batch):**\n"
            f"- Records scanned: {len(_SAMPLE_INTAKE_BATCH)}\n"
            f"- Potential duplicates: 1\n"
            f"- Match: rachel.chen@existing-customer.com (Email Match, High confidence)\n"
            f"- Recommended action: Review and merge with existing record\n\n"
            f"Source: [Duplicate Detection Engine]\nAgents: OneClickCRMIntakeAgent"
        )

    # ── import_preview ─────────────────────────────────────────
    def _import_preview(self, template_name):
        valid, dups, errors = _validate_batch(_SAMPLE_INTAKE_BATCH)
        total = len(_SAMPLE_INTAKE_BATCH)
        preview_rows = ""
        for r in _SAMPLE_INTAKE_BATCH:
            action = "Create" if r["status"] == "Valid" else ("Review" if "Duplicate" in r["status"] else "Skip")
            preview_rows += f"| {r['first_name']} {r['last_name']} | {r['company']} | {action} | {r['status']} |\n"
        return (
            f"**Import Preview**\n\n"
            f"| Metric | Count |\n|---|---|\n"
            f"| Total Records | {total} |\n"
            f"| Ready to Import | {valid} |\n"
            f"| Duplicates (Review) | {dups} |\n"
            f"| Validation Errors (Skip) | {errors} |\n\n"
            f"**Record Actions:**\n\n"
            f"| Name | Company | Action | Status |\n|---|---|---|---|\n"
            f"{preview_rows}\n"
            f"**Estimated Import Time:** 2 seconds\n"
            f"**Auto-Assignment:** Round-robin by territory\n\n"
            f"Confirm to proceed with importing {valid} records.\n\n"
            f"Source: [CRM Import Engine]\nAgents: OneClickCRMIntakeAgent"
        )


if __name__ == "__main__":
    agent = OneClickCRMIntakeAgent()
    for op in ["intake_form", "data_validation", "duplicate_check", "import_preview"]:
        print("=" * 60)
        print(agent.perform(operation=op, template_name="new_lead"))
        print()
