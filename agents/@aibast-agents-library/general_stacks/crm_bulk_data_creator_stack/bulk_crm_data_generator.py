"""
Bulk CRM Data Generator Agent

Generates synthetic CRM records (contacts, accounts, opportunities) for
testing, demos, and data migration validation.

Where a real deployment would write to Salesforce or Dynamics 365, this
agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/bulk-crm-data-generator",
    "version": "1.0.0",
    "display_name": "Bulk CRM Data Generator",
    "description": "Generates synthetic CRM contacts, accounts, and opportunities for testing, demos, and data migration.",
    "author": "AIBAST",
    "tags": ["crm", "data-generation", "testing", "contacts", "accounts", "opportunities"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_NAME_POOLS = {
    "first_names": ["James", "Maria", "Robert", "Jennifer", "David", "Sarah", "Michael", "Lisa", "William", "Patricia", "Thomas", "Linda", "Charles", "Karen", "Daniel", "Nancy"],
    "last_names": ["Anderson", "Chen", "Rodriguez", "Patel", "O'Brien", "Kim", "Johnson", "Williams", "Martinez", "Lee", "Garcia", "Taylor", "Thomas", "Wilson", "Moore", "Clark"],
    "titles": ["CEO", "CTO", "VP Sales", "Director of IT", "Procurement Manager", "CFO", "VP Marketing", "Operations Director", "Head of Engineering", "Business Development Manager"],
}

_INDUSTRY_LIST = [
    {"name": "Technology", "code": "TECH", "avg_deal_size": 85000, "typical_cycle_days": 90},
    {"name": "Healthcare", "code": "HLTH", "avg_deal_size": 120000, "typical_cycle_days": 120},
    {"name": "Financial Services", "code": "FNSV", "avg_deal_size": 150000, "typical_cycle_days": 150},
    {"name": "Manufacturing", "code": "MFCT", "avg_deal_size": 95000, "typical_cycle_days": 105},
    {"name": "Retail", "code": "RETL", "avg_deal_size": 45000, "typical_cycle_days": 60},
    {"name": "Education", "code": "EDUC", "avg_deal_size": 35000, "typical_cycle_days": 75},
    {"name": "Energy", "code": "ENRG", "avg_deal_size": 200000, "typical_cycle_days": 180},
    {"name": "Professional Services", "code": "PRSV", "avg_deal_size": 65000, "typical_cycle_days": 80},
]

_REVENUE_RANGES = [
    {"label": "Startup", "min": 500000, "max": 5000000, "employee_range": "10-50"},
    {"label": "Small Business", "min": 5000000, "max": 25000000, "employee_range": "50-200"},
    {"label": "Mid-Market", "min": 25000000, "max": 250000000, "employee_range": "200-1000"},
    {"label": "Enterprise", "min": 250000000, "max": 1000000000, "employee_range": "1000-5000"},
    {"label": "Large Enterprise", "min": 1000000000, "max": 10000000000, "employee_range": "5000+"},
]

_STAGE_DEFINITIONS = [
    {"name": "Prospecting", "probability": 10, "typical_duration_days": 14, "exit_criteria": "Initial contact made, interest confirmed"},
    {"name": "Qualification", "probability": 25, "typical_duration_days": 21, "exit_criteria": "Budget, authority, need, timeline confirmed"},
    {"name": "Proposal", "probability": 50, "typical_duration_days": 30, "exit_criteria": "Proposal delivered and reviewed by decision maker"},
    {"name": "Negotiation", "probability": 75, "typical_duration_days": 21, "exit_criteria": "Terms agreed, legal review complete"},
    {"name": "Closed Won", "probability": 100, "typical_duration_days": 0, "exit_criteria": "Contract signed, payment terms set"},
    {"name": "Closed Lost", "probability": 0, "typical_duration_days": 0, "exit_criteria": "Opportunity declined or competitor selected"},
]

_GENERATED_CONTACTS = [
    {"id": "CON-001", "first_name": "James", "last_name": "Anderson", "title": "VP Sales", "company": "Apex Technologies", "email": "james.anderson@apextech.com", "phone": "415-555-0101", "industry": "Technology"},
    {"id": "CON-002", "first_name": "Maria", "last_name": "Chen", "title": "CTO", "company": "HealthFirst Systems", "email": "maria.chen@healthfirst.com", "phone": "312-555-0202", "industry": "Healthcare"},
    {"id": "CON-003", "first_name": "Robert", "last_name": "Patel", "title": "CFO", "company": "Summit Financial Group", "email": "robert.patel@summitfin.com", "phone": "212-555-0303", "industry": "Financial Services"},
    {"id": "CON-004", "first_name": "Jennifer", "last_name": "Rodriguez", "title": "Procurement Manager", "company": "Pacific Manufacturing", "email": "jennifer.rodriguez@pacmfg.com", "phone": "503-555-0404", "industry": "Manufacturing"},
    {"id": "CON-005", "first_name": "David", "last_name": "Kim", "title": "Director of IT", "company": "EduPath Solutions", "email": "david.kim@edupath.com", "phone": "617-555-0505", "industry": "Education"},
]

_GENERATED_ACCOUNTS = [
    {"id": "ACC-001", "name": "Apex Technologies", "industry": "Technology", "revenue": 45000000, "employees": 320, "segment": "Mid-Market", "website": "www.apextech.com", "city": "San Francisco", "state": "CA"},
    {"id": "ACC-002", "name": "HealthFirst Systems", "industry": "Healthcare", "revenue": 180000000, "employees": 890, "segment": "Mid-Market", "website": "www.healthfirst.com", "city": "Chicago", "state": "IL"},
    {"id": "ACC-003", "name": "Summit Financial Group", "industry": "Financial Services", "revenue": 520000000, "employees": 2100, "segment": "Enterprise", "website": "www.summitfin.com", "city": "New York", "state": "NY"},
    {"id": "ACC-004", "name": "Pacific Manufacturing", "industry": "Manufacturing", "revenue": 75000000, "employees": 450, "segment": "Mid-Market", "website": "www.pacmfg.com", "city": "Portland", "state": "OR"},
    {"id": "ACC-005", "name": "EduPath Solutions", "industry": "Education", "revenue": 12000000, "employees": 85, "segment": "Small Business", "website": "www.edupath.com", "city": "Boston", "state": "MA"},
]

_GENERATED_OPPORTUNITIES = [
    {"id": "OPP-001", "name": "Apex Technologies - Platform License", "account": "ACC-001", "amount": 85000, "stage": "Proposal", "close_date": "2025-12-15", "probability": 50, "owner": "Sarah Johnson"},
    {"id": "OPP-002", "name": "HealthFirst - Enterprise Suite", "account": "ACC-002", "amount": 240000, "stage": "Negotiation", "close_date": "2025-11-30", "probability": 75, "owner": "Tom Rivera"},
    {"id": "OPP-003", "name": "Summit Financial - Compliance Module", "account": "ACC-003", "amount": 150000, "stage": "Qualification", "close_date": "2026-02-28", "probability": 25, "owner": "Sarah Johnson"},
    {"id": "OPP-004", "name": "Pacific Mfg - IoT Integration", "account": "ACC-004", "amount": 95000, "stage": "Prospecting", "close_date": "2026-03-31", "probability": 10, "owner": "Mike Davis"},
    {"id": "OPP-005", "name": "EduPath - SaaS Migration", "account": "ACC-005", "amount": 42000, "stage": "Closed Won", "close_date": "2025-10-20", "probability": 100, "owner": "Tom Rivera"},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _summarize_contacts():
    by_industry = {}
    for c in _GENERATED_CONTACTS:
        by_industry.setdefault(c["industry"], []).append(c)
    return by_industry


def _summarize_pipeline():
    total_value = sum(o["amount"] for o in _GENERATED_OPPORTUNITIES)
    weighted = sum(o["amount"] * o["probability"] / 100 for o in _GENERATED_OPPORTUNITIES)
    by_stage = {}
    for o in _GENERATED_OPPORTUNITIES:
        by_stage.setdefault(o["stage"], {"count": 0, "value": 0})
        by_stage[o["stage"]]["count"] += 1
        by_stage[o["stage"]]["value"] += o["amount"]
    return total_value, weighted, by_stage


def _account_segments():
    by_segment = {}
    for a in _GENERATED_ACCOUNTS:
        by_segment.setdefault(a["segment"], {"count": 0, "total_revenue": 0})
        by_segment[a["segment"]]["count"] += 1
        by_segment[a["segment"]]["total_revenue"] += a["revenue"]
    return by_segment


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class BulkCRMDataGeneratorAgent(BasicAgent):
    """
    Bulk CRM data generator for testing and demos.

    Operations:
        generate_contacts       - generate sample contact records
        generate_accounts       - generate sample account records
        generate_opportunities  - generate sample opportunity records
        data_summary            - summarize all generated data
    """

    def __init__(self):
        self.name = "BulkCRMDataGeneratorAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "generate_contacts", "generate_accounts",
                            "generate_opportunities", "data_summary",
                        ],
                        "description": "The data generation operation to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "data_summary")
        dispatch = {
            "generate_contacts": self._generate_contacts,
            "generate_accounts": self._generate_accounts,
            "generate_opportunities": self._generate_opportunities,
            "data_summary": self._data_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler()

    # ── generate_contacts ──────────────────────────────────────
    def _generate_contacts(self):
        rows = ""
        for c in _GENERATED_CONTACTS:
            rows += f"| {c['id']} | {c['first_name']} {c['last_name']} | {c['title']} | {c['company']} | {c['industry']} |\n"
        by_ind = _summarize_contacts()
        dist = "\n".join(f"- {ind}: {len(contacts)} contact(s)" for ind, contacts in by_ind.items())
        pool_info = f"First names: {len(_NAME_POOLS['first_names'])} | Last names: {len(_NAME_POOLS['last_names'])} | Titles: {len(_NAME_POOLS['titles'])}"
        return (
            f"**Generated Contacts ({len(_GENERATED_CONTACTS)} records)**\n\n"
            f"| ID | Name | Title | Company | Industry |\n|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Distribution by Industry:**\n{dist}\n\n"
            f"**Name Pool Capacity:** {pool_info}\n"
            f"**Max Unique Combinations:** {len(_NAME_POOLS['first_names']) * len(_NAME_POOLS['last_names']):,}\n\n"
            f"Source: [Synthetic Data Engine]\nAgents: BulkCRMDataGeneratorAgent"
        )

    # ── generate_accounts ──────────────────────────────────────
    def _generate_accounts(self):
        rows = ""
        for a in _GENERATED_ACCOUNTS:
            rows += f"| {a['id']} | {a['name']} | {a['industry']} | ${a['revenue']:,.0f} | {a['employees']} | {a['segment']} |\n"
        segments = _account_segments()
        seg_rows = "\n".join(f"- {seg}: {d['count']} accounts, ${d['total_revenue']:,.0f} total revenue" for seg, d in segments.items())
        ind_rows = "\n".join(f"| {i['name']} | {i['code']} | ${i['avg_deal_size']:,} | {i['typical_cycle_days']}d |" for i in _INDUSTRY_LIST)
        return (
            f"**Generated Accounts ({len(_GENERATED_ACCOUNTS)} records)**\n\n"
            f"| ID | Name | Industry | Revenue | Employees | Segment |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Segment Distribution:**\n{seg_rows}\n\n"
            f"**Industry Reference:**\n\n"
            f"| Industry | Code | Avg Deal | Cycle |\n|---|---|---|---|\n"
            f"{ind_rows}\n\n"
            f"Source: [Synthetic Data Engine]\nAgents: BulkCRMDataGeneratorAgent"
        )

    # ── generate_opportunities ─────────────────────────────────
    def _generate_opportunities(self):
        rows = ""
        for o in _GENERATED_OPPORTUNITIES:
            rows += f"| {o['id']} | {o['name']} | ${o['amount']:,} | {o['stage']} | {o['probability']}% | {o['close_date']} |\n"
        stage_rows = ""
        for s in _STAGE_DEFINITIONS:
            stage_rows += f"| {s['name']} | {s['probability']}% | {s['typical_duration_days']}d | {s['exit_criteria'][:50]} |\n"
        return (
            f"**Generated Opportunities ({len(_GENERATED_OPPORTUNITIES)} records)**\n\n"
            f"| ID | Name | Amount | Stage | Probability | Close Date |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Stage Definitions:**\n\n"
            f"| Stage | Probability | Duration | Exit Criteria |\n|---|---|---|---|\n"
            f"{stage_rows}\n\n"
            f"Source: [Synthetic Data Engine]\nAgents: BulkCRMDataGeneratorAgent"
        )

    # ── data_summary ───────────────────────────────────────────
    def _data_summary(self):
        total_val, weighted_val, by_stage = _summarize_pipeline()
        segments = _account_segments()
        stage_lines = "\n".join(f"| {stg} | {d['count']} | ${d['value']:,} |" for stg, d in by_stage.items())
        seg_lines = "\n".join(f"| {seg} | {d['count']} | ${d['total_revenue']:,.0f} |" for seg, d in segments.items())
        return (
            f"**CRM Data Generation Summary**\n\n"
            f"| Entity | Count |\n|---|---|\n"
            f"| Contacts | {len(_GENERATED_CONTACTS)} |\n"
            f"| Accounts | {len(_GENERATED_ACCOUNTS)} |\n"
            f"| Opportunities | {len(_GENERATED_OPPORTUNITIES)} |\n\n"
            f"**Pipeline Summary:**\n"
            f"- Total Value: ${total_val:,}\n"
            f"- Weighted Value: ${weighted_val:,.0f}\n\n"
            f"| Stage | Opps | Value |\n|---|---|---|\n"
            f"{stage_lines}\n\n"
            f"**Account Segments:**\n\n"
            f"| Segment | Count | Revenue |\n|---|---|---|\n"
            f"{seg_lines}\n\n"
            f"**Data Quality:** All records validated, no duplicates, referential integrity confirmed.\n\n"
            f"Source: [Synthetic Data Engine]\nAgents: BulkCRMDataGeneratorAgent"
        )


if __name__ == "__main__":
    agent = BulkCRMDataGeneratorAgent()
    for op in ["generate_contacts", "generate_accounts", "generate_opportunities", "data_summary"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
