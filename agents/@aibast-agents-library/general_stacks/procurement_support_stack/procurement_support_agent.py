"""
Procurement Support Agent

Provides procurement support operations including requisition status tracking,
contract lookups, supplier performance scoring, and budget checking.

Where a real deployment would connect to ERP and contract management systems,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/procurement-support",
    "version": "1.0.0",
    "display_name": "Procurement Support",
    "description": "Procurement support for requisition tracking, contract lookups, supplier performance, and budget checks.",
    "author": "AIBAST",
    "tags": ["procurement", "requisition", "contracts", "supplier", "budget"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_REQUISITIONS = {
    "REQ-7001": {"id": "REQ-7001", "title": "Q1 Marketing Collateral Print Run", "requester": "Angela Martinez", "department": "Marketing", "amount": 18500, "status": "Approved", "created": "2025-10-28", "po_number": "PO-44201", "supplier": "PrintPro Services", "delivery_date": "2025-12-05", "received_pct": 0},
    "REQ-7002": {"id": "REQ-7002", "title": "Server Room UPS Replacement", "requester": "Frank O'Brien", "department": "IT", "amount": 42000, "status": "In Transit", "created": "2025-10-15", "po_number": "PO-44189", "supplier": "APC by Schneider Electric", "delivery_date": "2025-11-20", "received_pct": 0},
    "REQ-7003": {"id": "REQ-7003", "title": "Annual Compliance Audit Services", "requester": "Carla Dubois", "department": "Finance", "amount": 65000, "status": "Under Review", "created": "2025-11-10", "po_number": None, "supplier": "Deloitte", "delivery_date": None, "received_pct": 0},
    "REQ-7004": {"id": "REQ-7004", "title": "Ergonomic Office Chairs (50 units)", "requester": "Derek Washington", "department": "HR", "amount": 27500, "status": "Delivered", "created": "2025-09-20", "po_number": "PO-44102", "supplier": "Herman Miller", "delivery_date": "2025-10-25", "received_pct": 100},
    "REQ-7005": {"id": "REQ-7005", "title": "Cloud Security Assessment Tool", "requester": "Frank O'Brien", "department": "IT", "amount": 35000, "status": "Pending Approval", "created": "2025-11-12", "po_number": None, "supplier": "CrowdStrike", "delivery_date": None, "received_pct": 0},
}

_CONTRACTS = {
    "CTR-3001": {"id": "CTR-3001", "supplier": "AWS", "title": "Enterprise Cloud Services Agreement", "start": "2024-01-01", "end": "2026-12-31", "total_value": 2670000, "annual_value": 890000, "status": "Active", "auto_renew": True, "notice_period_days": 90, "category": "Technology"},
    "CTR-3002": {"id": "CTR-3002", "supplier": "Salesforce", "title": "CRM Enterprise License Agreement", "start": "2024-04-01", "end": "2025-03-31", "total_value": 430000, "annual_value": 430000, "status": "Renewal Due", "auto_renew": False, "notice_period_days": 60, "category": "Software"},
    "CTR-3003": {"id": "CTR-3003", "supplier": "Deloitte", "title": "Professional Services MSA", "start": "2023-06-01", "end": "2025-05-31", "total_value": 195000, "annual_value": 97500, "status": "Active", "auto_renew": True, "notice_period_days": 30, "category": "Professional Services"},
    "CTR-3004": {"id": "CTR-3004", "supplier": "Herman Miller", "title": "Furniture Supply Agreement", "start": "2024-07-01", "end": "2025-06-30", "total_value": 125000, "annual_value": 125000, "status": "Active", "auto_renew": True, "notice_period_days": 30, "category": "Office Supplies"},
    "CTR-3005": {"id": "CTR-3005", "supplier": "CrowdStrike", "title": "Endpoint Security Subscription", "start": "2025-01-01", "end": "2025-12-31", "total_value": 78000, "annual_value": 78000, "status": "Active", "auto_renew": True, "notice_period_days": 60, "category": "Security"},
}

_SUPPLIER_SCORES = {
    "AWS": {"overall": 94, "quality": 96, "delivery": 92, "responsiveness": 93, "pricing": 88, "innovation": 97, "risk_level": "Low", "total_orders": 47, "on_time_pct": 98.2},
    "Salesforce": {"overall": 87, "quality": 90, "delivery": 88, "responsiveness": 82, "pricing": 78, "innovation": 92, "risk_level": "Low", "total_orders": 12, "on_time_pct": 95.0},
    "Deloitte": {"overall": 91, "quality": 94, "delivery": 89, "responsiveness": 90, "pricing": 82, "innovation": 88, "risk_level": "Low", "total_orders": 8, "on_time_pct": 96.5},
    "Herman Miller": {"overall": 89, "quality": 95, "delivery": 85, "responsiveness": 88, "pricing": 80, "innovation": 85, "risk_level": "Low", "total_orders": 15, "on_time_pct": 92.0},
    "CrowdStrike": {"overall": 92, "quality": 95, "delivery": 94, "responsiveness": 91, "pricing": 83, "innovation": 96, "risk_level": "Low", "total_orders": 6, "on_time_pct": 100.0},
    "PrintPro Services": {"overall": 78, "quality": 80, "delivery": 72, "responsiveness": 75, "pricing": 85, "innovation": 65, "risk_level": "Medium", "total_orders": 22, "on_time_pct": 82.0},
}

_BUDGET_ALLOCATIONS = {
    "IT": {"annual_budget": 1800000, "spent": 1245000, "committed": 77000, "remaining": 478000, "q4_forecast": 320000},
    "Marketing": {"annual_budget": 650000, "spent": 482000, "committed": 18500, "remaining": 149500, "q4_forecast": 125000},
    "Finance": {"annual_budget": 400000, "spent": 275000, "committed": 65000, "remaining": 60000, "q4_forecast": 80000},
    "HR": {"annual_budget": 350000, "spent": 245000, "committed": 27500, "remaining": 77500, "q4_forecast": 55000},
    "Sales": {"annual_budget": 500000, "spent": 380000, "committed": 0, "remaining": 120000, "q4_forecast": 90000},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_requisition(query):
    if not query:
        return "REQ-7001"
    q = query.upper().strip()
    for key in _REQUISITIONS:
        if key in q:
            return key
    return "REQ-7001"


def _contracts_expiring_soon(days=90):
    expiring = []
    for cid, c in _CONTRACTS.items():
        if c["status"] in ("Active", "Renewal Due"):
            expiring.append(c)
    return expiring


def _budget_health():
    total_budget = sum(d["annual_budget"] for d in _BUDGET_ALLOCATIONS.values())
    total_spent = sum(d["spent"] for d in _BUDGET_ALLOCATIONS.values())
    total_committed = sum(d["committed"] for d in _BUDGET_ALLOCATIONS.values())
    return total_budget, total_spent, total_committed


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ProcurementSupportAgent(BasicAgent):
    """
    Procurement support agent.

    Operations:
        requisition_status   - track requisition status and delivery
        contract_lookup      - look up contracts and renewal dates
        supplier_performance - view supplier performance scores
        budget_check         - check budget availability by department
    """

    def __init__(self):
        self.name = "ProcurementSupportAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "requisition_status", "contract_lookup",
                            "supplier_performance", "budget_check",
                        ],
                        "description": "The procurement support operation to perform",
                    },
                    "requisition_id": {
                        "type": "string",
                        "description": "Requisition ID (e.g. 'REQ-7001')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "requisition_status")
        dispatch = {
            "requisition_status": self._requisition_status,
            "contract_lookup": self._contract_lookup,
            "supplier_performance": self._supplier_performance,
            "budget_check": self._budget_check,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── requisition_status ─────────────────────────────────────
    def _requisition_status(self, params):
        rows = ""
        for req in _REQUISITIONS.values():
            po = req["po_number"] or "Pending"
            rows += f"| {req['id']} | {req['title'][:35]} | ${req['amount']:,} | {req['status']} | {po} | {req['supplier']} |\n"
        return (
            f"**Requisition Status Dashboard**\n\n"
            f"| ID | Title | Amount | Status | PO# | Supplier |\n|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Status Summary:**\n"
            f"- Delivered: {sum(1 for r in _REQUISITIONS.values() if r['status'] == 'Delivered')}\n"
            f"- In Transit: {sum(1 for r in _REQUISITIONS.values() if r['status'] == 'In Transit')}\n"
            f"- Approved: {sum(1 for r in _REQUISITIONS.values() if r['status'] == 'Approved')}\n"
            f"- Pending: {sum(1 for r in _REQUISITIONS.values() if 'Pending' in r['status'] or 'Review' in r['status'])}\n\n"
            f"Source: [Procurement System + ERP]\nAgents: ProcurementSupportAgent"
        )

    # ── contract_lookup ────────────────────────────────────────
    def _contract_lookup(self, params):
        rows = ""
        for c in _CONTRACTS.values():
            auto = "Yes" if c["auto_renew"] else "No"
            rows += f"| {c['id']} | {c['supplier']} | {c['title'][:30]} | ${c['annual_value']:,} | {c['end']} | {c['status']} | {auto} |\n"
        renewal_count = sum(1 for c in _CONTRACTS.values() if c["status"] == "Renewal Due")
        total_value = sum(c["annual_value"] for c in _CONTRACTS.values())
        return (
            f"**Contract Portfolio**\n\n"
            f"| ID | Supplier | Title | Annual Value | End Date | Status | Auto-Renew |\n|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Summary:**\n"
            f"- Active contracts: {len(_CONTRACTS)}\n"
            f"- Total annual value: ${total_value:,}\n"
            f"- Renewals due: {renewal_count}\n\n"
            f"Source: [Contract Management System]\nAgents: ProcurementSupportAgent"
        )

    # ── supplier_performance ───────────────────────────────────
    def _supplier_performance(self, params):
        rows = ""
        for name, s in sorted(_SUPPLIER_SCORES.items(), key=lambda x: x[1]["overall"], reverse=True):
            rows += f"| {name} | {s['overall']} | {s['quality']} | {s['delivery']} | {s['responsiveness']} | {s['pricing']} | {s['risk_level']} | {s['on_time_pct']}% |\n"
        return (
            f"**Supplier Performance Scorecard**\n\n"
            f"| Supplier | Overall | Quality | Delivery | Response | Pricing | Risk | On-Time |\n|---|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Scoring Methodology:** Weighted composite (Quality 30%, Delivery 25%, Responsiveness 20%, Pricing 15%, Innovation 10%)\n\n"
            f"**Alerts:**\n"
            f"- PrintPro Services: Below 80 overall - consider alternative suppliers\n"
            f"- All strategic suppliers (AWS, Salesforce) maintaining 87+ scores\n\n"
            f"Source: [Supplier Management System]\nAgents: ProcurementSupportAgent"
        )

    # ── budget_check ───────────────────────────────────────────
    def _budget_check(self, params):
        total_budget, total_spent, total_committed = _budget_health()
        total_remaining = total_budget - total_spent - total_committed
        rows = ""
        for dept, b in _BUDGET_ALLOCATIONS.items():
            util = (b["spent"] + b["committed"]) / b["annual_budget"] * 100
            status = "Over" if b["remaining"] < 0 else ("At Risk" if util > 85 else "On Track")
            rows += f"| {dept} | ${b['annual_budget']:,} | ${b['spent']:,} | ${b['committed']:,} | ${b['remaining']:,} | {util:.0f}% | {status} |\n"
        return (
            f"**Budget Check**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Total Budget | ${total_budget:,} |\n"
            f"| Spent YTD | ${total_spent:,} ({total_spent/total_budget*100:.0f}%) |\n"
            f"| Committed | ${total_committed:,} |\n"
            f"| Remaining | ${total_remaining:,} |\n\n"
            f"**By Department:**\n\n"
            f"| Department | Budget | Spent | Committed | Remaining | Utilization | Status |\n|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Alerts:**\n"
            f"- Finance department at risk: Q4 forecast ($80K) exceeds remaining ($60K)\n"
            f"- IT has sufficient budget for planned Q4 purchases\n\n"
            f"Source: [ERP + Finance System]\nAgents: ProcurementSupportAgent"
        )


if __name__ == "__main__":
    agent = ProcurementSupportAgent()
    for op in ["requisition_status", "contract_lookup", "supplier_performance", "budget_check"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
