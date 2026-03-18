"""
Dynamics 365 Connector Agent

Provides entity querying, record creation, bulk import, and schema inspection
for Microsoft Dynamics 365 CRM environments.

Where a real deployment would connect to the D365 Web API, this agent uses
a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/dynamics-365-connector",
    "version": "1.0.0",
    "display_name": "Dynamics 365 Connector",
    "description": "Dynamics 365 connector for entity queries, record creation, bulk import, and schema inspection.",
    "author": "AIBAST",
    "tags": ["dynamics-365", "crm", "d365", "entity", "bulk-import", "schema"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_ENTITY_SCHEMAS = {
    "account": {
        "logical_name": "account", "display_name": "Account",
        "primary_key": "accountid", "primary_name": "name",
        "attributes": [
            {"name": "accountid", "type": "Uniqueidentifier", "required": True},
            {"name": "name", "type": "String", "max_length": 160, "required": True},
            {"name": "accountnumber", "type": "String", "max_length": 20, "required": False},
            {"name": "industrycode", "type": "Picklist", "required": False},
            {"name": "revenue", "type": "Money", "required": False},
            {"name": "numberofemployees", "type": "Integer", "required": False},
            {"name": "telephone1", "type": "String", "max_length": 50, "required": False},
            {"name": "emailaddress1", "type": "String", "max_length": 100, "required": False},
            {"name": "websiteurl", "type": "String", "max_length": 200, "required": False},
            {"name": "address1_city", "type": "String", "max_length": 80, "required": False},
            {"name": "address1_stateorprovince", "type": "String", "max_length": 50, "required": False},
            {"name": "ownerid", "type": "Lookup", "target": "systemuser", "required": True},
        ],
        "record_count": 1247,
    },
    "contact": {
        "logical_name": "contact", "display_name": "Contact",
        "primary_key": "contactid", "primary_name": "fullname",
        "attributes": [
            {"name": "contactid", "type": "Uniqueidentifier", "required": True},
            {"name": "firstname", "type": "String", "max_length": 50, "required": False},
            {"name": "lastname", "type": "String", "max_length": 50, "required": True},
            {"name": "emailaddress1", "type": "String", "max_length": 100, "required": False},
            {"name": "telephone1", "type": "String", "max_length": 50, "required": False},
            {"name": "jobtitle", "type": "String", "max_length": 100, "required": False},
            {"name": "parentcustomerid", "type": "Lookup", "target": "account", "required": False},
            {"name": "ownerid", "type": "Lookup", "target": "systemuser", "required": True},
        ],
        "record_count": 4532,
    },
    "opportunity": {
        "logical_name": "opportunity", "display_name": "Opportunity",
        "primary_key": "opportunityid", "primary_name": "name",
        "attributes": [
            {"name": "opportunityid", "type": "Uniqueidentifier", "required": True},
            {"name": "name", "type": "String", "max_length": 300, "required": True},
            {"name": "estimatedvalue", "type": "Money", "required": False},
            {"name": "estimatedclosedate", "type": "DateTime", "required": False},
            {"name": "stepname", "type": "String", "max_length": 200, "required": False},
            {"name": "parentaccountid", "type": "Lookup", "target": "account", "required": False},
            {"name": "parentcontactid", "type": "Lookup", "target": "contact", "required": False},
            {"name": "closeprobability", "type": "Integer", "required": False},
            {"name": "ownerid", "type": "Lookup", "target": "systemuser", "required": True},
        ],
        "record_count": 892,
    },
}

_SAMPLE_RECORDS = {
    "account": [
        {"accountid": "a1b2c3d4-0001", "name": "Contoso Ltd", "accountnumber": "ACC-10001", "industrycode": "Technology", "revenue": 45000000, "numberofemployees": 320, "address1_city": "Seattle", "address1_stateorprovince": "WA"},
        {"accountid": "a1b2c3d4-0002", "name": "Fabrikam Inc", "accountnumber": "ACC-10002", "industrycode": "Manufacturing", "revenue": 89000000, "numberofemployees": 650, "address1_city": "Portland", "address1_stateorprovince": "OR"},
        {"accountid": "a1b2c3d4-0003", "name": "Adventure Works", "accountnumber": "ACC-10003", "industrycode": "Retail", "revenue": 12000000, "numberofemployees": 95, "address1_city": "Denver", "address1_stateorprovince": "CO"},
    ],
    "contact": [
        {"contactid": "c1d2e3f4-0001", "firstname": "Alex", "lastname": "Rivera", "emailaddress1": "alex.rivera@contoso.com", "jobtitle": "CTO", "parentcustomerid": "a1b2c3d4-0001"},
        {"contactid": "c1d2e3f4-0002", "firstname": "Kim", "lastname": "Park", "emailaddress1": "kim.park@fabrikam.com", "jobtitle": "VP Operations", "parentcustomerid": "a1b2c3d4-0002"},
        {"contactid": "c1d2e3f4-0003", "firstname": "Jordan", "lastname": "Hayes", "emailaddress1": "jordan.hayes@adventureworks.com", "jobtitle": "Purchasing Manager", "parentcustomerid": "a1b2c3d4-0003"},
    ],
    "opportunity": [
        {"opportunityid": "o1p2q3r4-0001", "name": "Contoso - Cloud Migration", "estimatedvalue": 125000, "stepname": "Proposal", "closeprobability": 60, "parentaccountid": "a1b2c3d4-0001", "estimatedclosedate": "2025-12-15"},
        {"opportunityid": "o1p2q3r4-0002", "name": "Fabrikam - IoT Platform", "estimatedvalue": 89000, "stepname": "Qualification", "closeprobability": 30, "parentaccountid": "a1b2c3d4-0002", "estimatedclosedate": "2026-02-28"},
    ],
}

_IMPORT_TEMPLATES = {
    "account_import": {
        "entity": "account", "format": "CSV",
        "required_columns": ["name", "accountnumber"],
        "optional_columns": ["industrycode", "revenue", "numberofemployees", "telephone1", "emailaddress1", "websiteurl", "address1_city", "address1_stateorprovince"],
        "max_batch_size": 1000, "estimated_time_per_1000": "45 seconds",
        "duplicate_detection_fields": ["name", "accountnumber"],
    },
    "contact_import": {
        "entity": "contact", "format": "CSV",
        "required_columns": ["lastname"],
        "optional_columns": ["firstname", "emailaddress1", "telephone1", "jobtitle", "parentcustomerid"],
        "max_batch_size": 2000, "estimated_time_per_1000": "30 seconds",
        "duplicate_detection_fields": ["emailaddress1", "firstname+lastname"],
    },
    "opportunity_import": {
        "entity": "opportunity", "format": "CSV",
        "required_columns": ["name"],
        "optional_columns": ["estimatedvalue", "estimatedclosedate", "stepname", "parentaccountid", "closeprobability"],
        "max_batch_size": 500, "estimated_time_per_1000": "60 seconds",
        "duplicate_detection_fields": ["name", "parentaccountid"],
    },
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _format_schema_attributes(entity_name):
    schema = _ENTITY_SCHEMAS.get(entity_name, {})
    attrs = schema.get("attributes", [])
    rows = ""
    for a in attrs:
        req = "Yes" if a.get("required") else "No"
        extra = ""
        if "max_length" in a:
            extra = f"max: {a['max_length']}"
        elif "target" in a:
            extra = f"-> {a['target']}"
        rows += f"| {a['name']} | {a['type']} | {req} | {extra} |\n"
    return rows


def _format_records(entity_name):
    records = _SAMPLE_RECORDS.get(entity_name, [])
    if not records:
        return "No records found."
    keys = list(records[0].keys())[:6]
    header = " | ".join(keys)
    sep = " | ".join(["---"] * len(keys))
    rows = ""
    for r in records:
        vals = [str(r.get(k, ""))[:25] for k in keys]
        rows += "| " + " | ".join(vals) + " |\n"
    return f"| {header} |\n|{sep}|\n{rows}"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class Dynamics365ConnectorAgent(BasicAgent):
    """
    Dynamics 365 connector agent.

    Operations:
        entity_query    - query entity records with filters
        record_create   - create new records in an entity
        bulk_import     - bulk import records from templates
        schema_inspect  - inspect entity schema and metadata
    """

    def __init__(self):
        self.name = "Dynamics365ConnectorAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "entity_query", "record_create",
                            "bulk_import", "schema_inspect",
                        ],
                        "description": "The D365 operation to perform",
                    },
                    "entity_name": {
                        "type": "string",
                        "description": "D365 entity logical name (e.g. 'account', 'contact', 'opportunity')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "schema_inspect")
        entity = kwargs.get("entity_name", "account")
        dispatch = {
            "entity_query": self._entity_query,
            "record_create": self._record_create,
            "bulk_import": self._bulk_import,
            "schema_inspect": self._schema_inspect,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(entity)

    # ── entity_query ───────────────────────────────────────────
    def _entity_query(self, entity):
        schema = _ENTITY_SCHEMAS.get(entity)
        if not schema:
            return f"Entity '{entity}' not found. Available: {', '.join(_ENTITY_SCHEMAS.keys())}"
        record_table = _format_records(entity)
        count = schema["record_count"]
        return (
            f"**D365 Entity Query: {schema['display_name']}**\n\n"
            f"Total Records: {count:,}\n\n"
            f"**Sample Records:**\n\n{record_table}\n"
            f"**Query Info:**\n"
            f"- Entity: {schema['logical_name']}\n"
            f"- Primary Key: {schema['primary_key']}\n"
            f"- Primary Name: {schema['primary_name']}\n"
            f"- Records returned: {len(_SAMPLE_RECORDS.get(entity, []))} of {count:,}\n\n"
            f"Source: [Dynamics 365 Web API]\nAgents: Dynamics365ConnectorAgent"
        )

    # ── record_create ──────────────────────────────────────────
    def _record_create(self, entity):
        schema = _ENTITY_SCHEMAS.get(entity)
        if not schema:
            return f"Entity '{entity}' not found. Available: {', '.join(_ENTITY_SCHEMAS.keys())}"
        required_attrs = [a for a in schema["attributes"] if a.get("required")]
        req_rows = ""
        for a in required_attrs:
            req_rows += f"| {a['name']} | {a['type']} | Required |\n"
        sample = _SAMPLE_RECORDS.get(entity, [{}])[0]
        sample_lines = "\n".join(f"  \"{k}\": \"{v}\"" for k, v in list(sample.items())[:5])
        return (
            f"**D365 Record Create: {schema['display_name']}**\n\n"
            f"**Required Fields:**\n\n"
            f"| Attribute | Type | Status |\n|---|---|---|\n"
            f"{req_rows}\n"
            f"**Sample Payload:**\n```json\n{{\n{sample_lines}\n}}\n```\n\n"
            f"**Result:** Record created successfully\n"
            f"- Entity: {schema['logical_name']}\n"
            f"- New Record Count: {schema['record_count'] + 1:,}\n\n"
            f"Source: [Dynamics 365 Web API]\nAgents: Dynamics365ConnectorAgent"
        )

    # ── bulk_import ────────────────────────────────────────────
    def _bulk_import(self, entity):
        template_key = f"{entity}_import"
        template = _IMPORT_TEMPLATES.get(template_key)
        if not template:
            return f"No import template for '{entity}'. Available: {', '.join(k.replace('_import','') for k in _IMPORT_TEMPLATES.keys())}"
        req_cols = ", ".join(template["required_columns"])
        opt_cols = ", ".join(template["optional_columns"][:5])
        dup_fields = ", ".join(template["duplicate_detection_fields"])
        return (
            f"**D365 Bulk Import: {entity.title()}**\n\n"
            f"| Setting | Value |\n|---|---|\n"
            f"| Format | {template['format']} |\n"
            f"| Max Batch Size | {template['max_batch_size']:,} records |\n"
            f"| Est. Time per 1000 | {template['estimated_time_per_1000']} |\n"
            f"| Duplicate Detection | {dup_fields} |\n\n"
            f"**Required Columns:** {req_cols}\n\n"
            f"**Optional Columns:** {opt_cols}, ...\n\n"
            f"**Import Preview:**\n"
            f"- Records to import: 500 (simulated)\n"
            f"- Duplicates detected: 12\n"
            f"- Records to create: 488\n"
            f"- Estimated time: 23 seconds\n\n"
            f"Source: [Dynamics 365 Import Service]\nAgents: Dynamics365ConnectorAgent"
        )

    # ── schema_inspect ─────────────────────────────────────────
    def _schema_inspect(self, entity):
        schema = _ENTITY_SCHEMAS.get(entity)
        if not schema:
            overview_rows = ""
            for name, s in _ENTITY_SCHEMAS.items():
                overview_rows += f"| {name} | {s['display_name']} | {len(s['attributes'])} | {s['record_count']:,} |\n"
            return (
                f"**D365 Schema Overview**\n\n"
                f"| Entity | Display Name | Attributes | Records |\n|---|---|---|---|\n"
                f"{overview_rows}\n"
                f"Specify `entity_name` to inspect a specific entity.\n\n"
                f"Source: [Dynamics 365 Metadata API]\nAgents: Dynamics365ConnectorAgent"
            )
        attr_rows = _format_schema_attributes(entity)
        return (
            f"**D365 Schema: {schema['display_name']}**\n\n"
            f"| Property | Value |\n|---|---|\n"
            f"| Logical Name | {schema['logical_name']} |\n"
            f"| Primary Key | {schema['primary_key']} |\n"
            f"| Primary Name | {schema['primary_name']} |\n"
            f"| Record Count | {schema['record_count']:,} |\n"
            f"| Attributes | {len(schema['attributes'])} |\n\n"
            f"**Attributes:**\n\n"
            f"| Name | Type | Required | Details |\n|---|---|---|---|\n"
            f"{attr_rows}\n\n"
            f"Source: [Dynamics 365 Metadata API]\nAgents: Dynamics365ConnectorAgent"
        )


if __name__ == "__main__":
    agent = Dynamics365ConnectorAgent()
    for op in ["entity_query", "record_create", "bulk_import", "schema_inspect"]:
        print("=" * 60)
        print(agent.perform(operation=op, entity_name="account"))
        print()
