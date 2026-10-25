"""
Procurement Agent

Manages purchase requests, vendor comparisons, approval routing, and
spend analysis for organizational procurement workflows.

Where a real deployment would connect to ERP and procurement platforms,
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
    "name": "@aibast-agents-library/procurement-agent",
    "version": "1.1.0",
    "display_name": "Procurement Agent",
    "description": "Automate purchase order management and vendor selection to enable faster and more cost-effective purchasing.",
    "author": "AIBAST",
    "tags": ["procurement", "purchasing", "vendor", "approval", "spend-analysis"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_PURCHASE_REQUESTS = {
    "PR-5001": {"id": "PR-5001", "title": "Cloud Infrastructure Upgrade", "requester": "Sarah Chen", "department": "IT", "category": "Technology", "amount": 125000, "priority": "High", "status": "Pending Approval", "vendor_preferred": "AWS", "justification": "Current infrastructure at 92% capacity, scaling needed for Q1 growth", "budget_code": "IT-INFRA-2025"},
    "PR-5002": {"id": "PR-5002", "title": "Office Furniture - New Floor Build-Out", "requester": "Tom Rivera", "department": "Facilities", "category": "Office Supplies", "amount": 48500, "priority": "Medium", "status": "Vendor Selection", "vendor_preferred": "Steelcase", "justification": "5th floor build-out for 30 new employees starting Q2", "budget_code": "FAC-CAPEX-2025"},
    "PR-5003": {"id": "PR-5003", "title": "Annual Software License Renewal - Salesforce", "requester": "Mike Torres", "department": "Sales", "category": "Software", "amount": 215000, "priority": "High", "status": "Approved", "vendor_preferred": "Salesforce", "justification": "Annual enterprise license renewal, 200 seats", "budget_code": "SALES-SW-2025"},
    "PR-5004": {"id": "PR-5004", "title": "Employee Training Program - Leadership Development", "requester": "Lisa Park", "department": "HR", "category": "Professional Services", "amount": 35000, "priority": "Low", "status": "Draft", "vendor_preferred": "FranklinCovey", "justification": "Q2 leadership development program for 25 managers", "budget_code": "HR-TRAIN-2025"},
    "PR-5005": {"id": "PR-5005", "title": "Engineering Team Laptops (50)", "requester": "Priya Nair", "department": "Engineering", "category": "IT Equipment", "amount": 81893, "priority": "High", "status": "Draft PO - Pending Approval", "vendor_preferred": "TechPro Solutions", "justification": "50 new engineers start Monday; equipment needed within 5 business days", "budget_code": "IT-EQUIP-Q4-2024"},
}

_VENDOR_CATALOG = {
    "VND-001": {"name": "AWS", "category": "Cloud Infrastructure", "contract_status": "Active", "tier": "Strategic", "rating": 4.7, "annual_spend": 890000, "payment_terms": "Net 30", "contact": "Enterprise Account Manager"},
    "VND-002": {"name": "Salesforce", "category": "CRM Software", "contract_status": "Active", "tier": "Strategic", "rating": 4.5, "annual_spend": 430000, "payment_terms": "Annual Prepay", "contact": "Customer Success Manager"},
    "VND-003": {"name": "Steelcase", "category": "Office Furniture", "contract_status": "Active", "tier": "Preferred", "rating": 4.3, "annual_spend": 125000, "payment_terms": "Net 45", "contact": "Account Representative"},
    "VND-004": {"name": "Herman Miller", "category": "Office Furniture", "contract_status": "Active", "tier": "Approved", "rating": 4.6, "annual_spend": 85000, "payment_terms": "Net 30", "contact": "Regional Sales"},
    "VND-005": {"name": "Azure", "category": "Cloud Infrastructure", "contract_status": "Active", "tier": "Strategic", "rating": 4.6, "annual_spend": 650000, "payment_terms": "Net 30", "contact": "Technical Account Manager"},
    "VND-006": {"name": "FranklinCovey", "category": "Training Services", "contract_status": "Active", "tier": "Approved", "rating": 4.2, "annual_spend": 45000, "payment_terms": "Net 30", "contact": "Program Director"},
    "VND-007": {"name": "TechPro Solutions", "category": "IT Equipment", "contract_status": "Master agreement valid through next year", "tier": "Preferred", "rating": 4.8, "annual_spend": 166750, "payment_terms": "Net 30", "contact": "Account Manager", "delivery": "3-5 days", "on_time_pct": 98, "defect_pct": 0, "volume_discount": "5% off for 50+ units"},
    "VND-008": {"name": "Global IT Supply", "category": "IT Equipment", "contract_status": "Active", "tier": "Approved", "rating": 4.4, "annual_spend": 63250, "payment_terms": "Net 30", "contact": "Inside Sales", "delivery": "5-7 days", "on_time_pct": 93, "defect_pct": 1, "volume_discount": "3% off for 100+ units"},
    "VND-009": {"name": "CompuDirect", "category": "IT Equipment", "contract_status": "Active", "tier": "Approved", "rating": 4.1, "annual_spend": 57500, "payment_terms": "Net 45", "contact": "Regional Sales", "delivery": "7-10 days", "on_time_pct": 89, "defect_pct": 2, "volume_discount": "None"},
}

# Keywords that select a vendor category (simple substring match).
_CATEGORY_KEYWORDS = {
    "IT Equipment": "it equipment laptops laptop computers hardware it hardware",
    "Cloud Infrastructure": "cloud infrastructure cloud vendors",
    "Office Furniture": "office furniture furniture",
}

# Demo purchase order for PR-5005 (draft only; created by an authorized buyer in the ERP).
_PO_DRAFTS = {
    "PR-5005": {
        "po_number": "PO-2024-ENG-0892", "vendor": "TechPro Solutions",
        "lines": [
            {"item": "Dell Latitude 7440 (i7, 32GB, 1TB) - engineering configuration", "qty": 50, "unit": 1250},
            {"item": "3-Year Warranty", "qty": 50, "unit": 189},
            {"item": "Docking Stations", "qty": 50, "unit": 150},
        ],
        "discount_pct": 5, "tax_pct": 8.5,
        "finance_director": "Sarah Thompson", "cfo": "Michael Roberts",
        "queue_time": "4 hours 23 minutes", "fd_avg_response": "6 hours", "escalation_after": "24 hours",
        "it_inventory_units": 12, "rental_days": 45,
        "needed_by": "team starts Monday",
    },
}

# Q4 2024 IT department budget (the budget the laptop PO lands in).
_IT_BUDGET = {
    "period": "Q4 2024", "budget": 450000,
    "spent_by_category": [("Laptops/Desktops", 198400), ("Software Licenses", 42300),
                          ("Networking", 28900), ("Accessories", 17900)],
    "duplicate_licenses": [("Design suite seats assigned twice", 18, 400), ("Overlapping project-tool licenses", 13, 400)],
}

_RFQ_DRAFTS = {
    "RFQ-2024-FRN-0145": {
        "for": "the new engineering team (50 people)",
        "items": [("Standing Desks (60\" adjustable)", 35000, 45000), ("Ergonomic Chairs (lumbar support)", 25000, 30000),
                  ("Dual Monitor Arms", 7500, 10000)],
        "vendors": ["WorkSpace Plus", "Office Innovations", "Commercial Interiors"],
        "criteria": [("Price", 40), ("Delivery", 25), ("Warranty", 20), ("Sustainability", 15)],
        "response_hours": 48,
    },
}

_APPROVAL_THRESHOLDS = [
    {"max_amount": 5000, "approver": "Direct Manager", "sla_hours": 4},
    {"max_amount": 25000, "approver": "Dept Manager", "sla_hours": 8},
    {"max_amount": 75000, "approver": "Finance Director", "sla_hours": 24},
    {"max_amount": 500000, "approver": "CFO", "sla_hours": 48},
    {"max_amount": 999999999, "approver": "CEO + Board", "sla_hours": 120},
]

_SPEND_CATEGORIES = {
    "Technology": {"budget": 2500000, "spent_ytd": 1875000, "committed": 340000, "available": 285000, "trend": "+12% YoY"},
    "Software": {"budget": 800000, "spent_ytd": 645000, "committed": 215000, "available": -60000, "trend": "+18% YoY"},
    "Office Supplies": {"budget": 350000, "spent_ytd": 210000, "committed": 48500, "available": 91500, "trend": "-5% YoY"},
    "Professional Services": {"budget": 500000, "spent_ytd": 325000, "committed": 35000, "available": 140000, "trend": "+8% YoY"},
    "Travel": {"budget": 200000, "spent_ytd": 142000, "committed": 18000, "available": 40000, "trend": "-15% YoY"},
}

_PROCUREMENT_GATE = (
    "Analysis only. No purchase order is created, no supplier is selected or "
    "contacted, and no funds are committed without authorized procurement approval."
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_approval_level(amount):
    for threshold in _APPROVAL_THRESHOLDS:
        if amount <= threshold["max_amount"]:
            return threshold
    return _APPROVAL_THRESHOLDS[-1]


def _approval_chain(amount):
    """Department-level and higher approvers up to and including the one the amount requires."""
    chain = []
    for t in _APPROVAL_THRESHOLDS[1:]:
        chain.append(t)
        if amount <= t["max_amount"]:
            break
    return chain


def _half_up(value):
    return int(value + 0.5)


def _po_totals(req_id):
    po = _PO_DRAFTS[req_id]
    subtotal = sum(l["qty"] * l["unit"] for l in po["lines"])
    discount = _half_up(subtotal * po["discount_pct"] / 100)
    tax = _half_up((subtotal - discount) * po["tax_pct"] / 100)
    return subtotal, discount, tax, subtotal - discount + tax


def _match_category(query):
    """Category name for a query like 'IT equipment' or 'laptops'; None for all vendors."""
    if not query:
        return None
    q = str(query).lower().strip()
    for cat, words in _CATEGORY_KEYWORDS.items():
        if q in words or cat.lower() in q:
            return cat
    return None


def _find_competing_vendors(category):
    return [v for v in _VENDOR_CATALOG.values() if category.lower() in v["category"].lower()]


def _total_spend_summary():
    total_budget = sum(c["budget"] for c in _SPEND_CATEGORIES.values())
    total_spent = sum(c["spent_ytd"] for c in _SPEND_CATEGORIES.values())
    total_committed = sum(c["committed"] for c in _SPEND_CATEGORIES.values())
    return total_budget, total_spent, total_committed


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ProcurementAgent(BasicAgent):
    """
    Procurement management agent.

    Operations:
        purchase_request   - create and view purchase requests
        vendor_comparison  - compare vendors for a category
        approval_routing   - determine approval path for a request
        spend_analysis     - analyze spend by category and budget
    """

    def __init__(self):
        self.name = "ProcurementAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always use this tool for a "
                "purchase-request brief, cloud-upgrade request, approved vendors for a "
                "category (e.g. IT equipment for laptops), drafting a purchase order, "
                "expediting an approval, budget impact of an order, an RFQ draft, "
                "vendor comparison, approval path, or purchasing-budget pressure question. "
                "The demo order is PR-5005: 50 laptops for the new engineering team. If the "
                "user asks to walk through the cloud-upgrade request and identify "
                "whose review it needs, use purchase_request with the default "
                "synthetic PR-5001. Provide synthetic procurement decision support "
                "only; never create a purchase order, select or contact a supplier, "
                "send a notification, or commit funds: purchase orders, reminders and "
                "RFQs come back as drafts for an authorized buyer to submit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "purchase_request", "vendor_comparison",
                            "approval_routing", "spend_analysis",
                            "draft_purchase_order", "expedite_approval",
                            "budget_impact", "draft_rfq",
                        ],
                        "description": (
                            "Choose vendor_comparison for approved vendors (pass category "
                            "'IT Equipment' for laptops) or a neutral approved-vendor view; "
                            "draft_purchase_order to create the purchase order for the 50 Dell "
                            "Latitude 7440 laptops; expedite_approval to expedite the approval "
                            "with urgency notifications; budget_impact for how this order affects "
                            "the Q4 budget; draft_rfq for an RFQ for office furniture for the same "
                            "team; purchase_request for a request brief, cloud upgrade, amount, or "
                            "required reviewer; approval_routing for the recommended approval path "
                            "or SLA; and spend_analysis for company-wide budget pressure, category "
                            "spend, or overspend."
                        ),
                    },
                    "request_id": {
                        "type": "string",
                        "description": (
                            "Synthetic purchase request ID. Use PR-5001 for the "
                            "cloud infrastructure or cloud-upgrade request and PR-5005 "
                            "for the engineering laptops (the default for purchase "
                            "orders, expediting and budget impact)."
                        ),
                    },
                    "category": {
                        "type": "string",
                        "enum": ["IT Equipment", "Cloud Infrastructure", "Office Furniture"],
                        "description": (
                            "Vendor category for vendor_comparison: 'IT Equipment' for laptops "
                            "or computers, 'Cloud Infrastructure' for cloud vendors, 'Office "
                            "Furniture' for furniture. Omit for all vendors."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "purchase_request")
        dispatch = {
            "purchase_request": self._purchase_request,
            "vendor_comparison": self._vendor_comparison,
            "approval_routing": self._approval_routing,
            "spend_analysis": self._spend_analysis,
            "draft_purchase_order": self._draft_purchase_order,
            "expedite_approval": self._expedite_approval,
            "budget_impact": self._budget_impact,
            "draft_rfq": self._draft_rfq,
        }
        if op in ("draft_purchase_order", "expedite_approval", "budget_impact"):
            req = kwargs.get("request_id") or "PR-5005"
            if req not in _PO_DRAFTS:
                return (f"No purchase order draft is packaged for {req}; drafts exist for "
                        f"{', '.join(_PO_DRAFTS)} (engineering laptops). {_PROCUREMENT_GATE}")
            kwargs = dict(kwargs, request_id=req)
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── purchase_request ───────────────────────────────────────
    def _purchase_request(self, params):
        req_id = params.get("request_id", "PR-5001")
        if req_id in _PURCHASE_REQUESTS:
            pr = _PURCHASE_REQUESTS[req_id]
            approval = _get_approval_level(pr["amount"])
            return (
                f"**Purchase Request Review: {pr['id']}**\n\n"
                f"| Field | Detail |\n|---|---|\n"
                f"| Title | {pr['title']} |\n"
                f"| Requester | {pr['requester']} ({pr['department']}) |\n"
                f"| Category | {pr['category']} |\n"
                f"| Amount | ${pr['amount']:,} |\n"
                f"| Priority | {pr['priority']} |\n"
                f"| Status | {pr['status']} |\n"
                f"| Preferred Vendor | {pr['vendor_preferred']} |\n"
                f"| Budget Code | {pr['budget_code']} |\n"
                f"| Required Approver | {approval['approver']} |\n\n"
                f"**Justification:** {pr['justification']}\n\n"
                f"**Approval gate:** {_PROCUREMENT_GATE}\n\n"
                f"Source: [Synthetic Procurement Snapshot]\nAgents: ProcurementAgent"
            )
        rows = ""
        for pr in _PURCHASE_REQUESTS.values():
            rows += f"| {pr['id']} | {pr['title'][:35]} | ${pr['amount']:,} | {pr['status']} | {pr['priority']} |\n"
        return (
            f"**Purchase Requests**\n\n"
            f"| ID | Title | Amount | Status | Priority |\n|---|---|---|---|---|\n"
            f"{rows}\n\n"
            f"**Approval gate:** {_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Procurement Snapshot]\nAgents: ProcurementAgent"
        )

    # ── vendor_comparison ──────────────────────────────────────
    def _vendor_comparison(self, params):
        cat = _match_category(params.get("category"))
        if cat == "IT Equipment":
            return self._it_vendors()
        rows = ""
        for vid, v in _VENDOR_CATALOG.items():
            rows += f"| {vid} | {v['name']} | {v['category']} | {v['tier']} | {v['rating']}/5 | ${v['annual_spend']:,} | {v['payment_terms']} |\n"
        return (
            f"**Vendor Comparison**\n\n"
            f"| ID | Vendor | Category | Tier | Rating | Annual Spend | Terms |\n|---|---|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Vendor Tiers:**\n"
            f"- Strategic: Long-term partners, best pricing, dedicated support\n"
            f"- Preferred: Competitive pricing, standard support, pre-approved\n"
            f"- Approved: Vetted and available, standard terms\n\n"
            f"Ratings and terms are comparison evidence, not a supplier award. "
            f"{_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Vendor Management Snapshot]\nAgents: ProcurementAgent"
        )

    # ── approval_routing ───────────────────────────────────────
    def _approval_routing(self, params):
        req_id = params.get("request_id", "PR-5001")
        pr = _PURCHASE_REQUESTS.get(req_id, list(_PURCHASE_REQUESTS.values())[0])
        approval = _get_approval_level(pr["amount"])
        threshold_rows = ""
        for t in _APPROVAL_THRESHOLDS:
            limit = f"Up to ${t['max_amount']:,}" if t["max_amount"] < 999999999 else "Above $500,000"
            marker = " <-- This request" if t == approval else ""
            threshold_rows += f"| {limit} | {t['approver']} | {t['sla_hours']}h |{marker}\n"
        return (
            f"**Approval Routing: {pr['id']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Request | {pr['title']} |\n"
            f"| Amount | ${pr['amount']:,} |\n"
            f"| Required Approver | {approval['approver']} |\n"
            f"| Approval SLA | {approval['sla_hours']} hours |\n"
            f"| Current Status | {pr['status']} |\n\n"
            f"**Approval Thresholds:**\n\n"
            f"| Amount Limit | Approver | SLA |\n|---|---|---|\n"
            f"{threshold_rows}\n\n"
            f"Routing is a recommendation and does not record an approval. "
            f"{_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Approval Rules]\nAgents: ProcurementAgent"
        )

    # ── spend_analysis ─────────────────────────────────────────
    def _spend_analysis(self, params):
        total_budget, total_spent, total_committed = _total_spend_summary()
        total_available = total_budget - total_spent - total_committed
        alert_lines = []
        for cat, data in _SPEND_CATEGORIES.items():
            utilization = (data["spent_ytd"] + data["committed"]) / data["budget"] * 100
            if data["available"] < 0:
                alert_lines.append(f"- {cat} category over budget by ${-data['available']:,} - requires reallocation")
            elif utilization > 85:
                alert_lines.append(f"- {cat} committed spend approaching budget limit ({utilization:.0f}% used)")
        dup = sum(n * price for _label, n, price in _IT_BUDGET["duplicate_licenses"])
        alert_lines.append(f"- ${dup:,} in duplicate software licenses identified in the IT budget - potential savings")
        alerts = "\n".join(alert_lines)
        cat_rows = ""
        for cat, data in _SPEND_CATEGORIES.items():
            utilization = (data["spent_ytd"] + data["committed"]) / data["budget"] * 100
            status = "Over Budget" if data["available"] < 0 else ("At Risk" if utilization > 85 else "On Track")
            cat_rows += f"| {cat} | ${data['budget']:,} | ${data['spent_ytd']:,} | ${data['committed']:,} | ${data['available']:,} | {status} | {data['trend']} |\n"
        return (
            f"**Spend Analysis**\n\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Total Budget | ${total_budget:,} |\n"
            f"| Spent YTD | ${total_spent:,} ({total_spent/total_budget*100:.0f}%) |\n"
            f"| Committed | ${total_committed:,} |\n"
            f"| Available | ${total_available:,} |\n\n"
            f"**By Category:**\n\n"
            f"| Category | Budget | Spent YTD | Committed | Available | Status | Trend |\n|---|---|---|---|---|---|---|\n"
            f"{cat_rows}\n"
            f"**Alerts:**\n{alerts}\n\n"
            f"{_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic ERP + Finance Snapshot]\nAgents: ProcurementAgent"
        )


    # ── vendor_comparison: IT equipment view ───────────────────
    def _it_vendors(self):
        vendors = [v for v in _VENDOR_CATALOG.values() if v["category"] == "IT Equipment"]
        best = vendors[0]
        rows = "\n".join(f"| {v['name']} | {v['delivery']} | {v['on_time_pct']}% | {v['defect_pct']}% | "
                         f"{v['volume_discount']} | {v['contract_status']} |" for v in vendors)
        spent = sum(a for _c, a in _IT_BUDGET["spent_by_category"])
        return (
            f"Approved IT-equipment vendors with current performance data. {best['name']} offers the "
            f"best value with a volume discount.\n\n"
            f"**Approved Vendor Analysis**\n\n"
            f"| Vendor | Delivery | On-time | Defect rate | Volume discount | Contract |\n|---|---|---|---|---|---|\n"
            f"{rows}\n\n"
            f"**{best['name']} Performance:** on-time delivery {best['on_time_pct']}% (last quarter); "
            f"defect rate {best['defect_pct']}%; volume discount {best['volume_discount']}; contract status: "
            f"{best['contract_status']}.\n\n"
            f"**Your IT Budget:** ${spent:,} spent YTD of ${_IT_BUDGET['budget']:,} "
            f"({spent * 100 / _IT_BUDGET['budget']:.1f}%)\n\n"
            f"Ratings and terms are comparison evidence, not a supplier award. {_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Procurement + Vendor Management Snapshot]\nAgents: ProcurementAgent\n\n"
            f"Should I draft a purchase order with {best['name']}?"
        )

    # ── draft_purchase_order ───────────────────────────────────
    def _draft_purchase_order(self, params):
        req = params["request_id"]
        po = _PO_DRAFTS[req]
        subtotal, discount, tax, total = _po_totals(req)
        lines = "\n".join(f"| {l['item']} | {l['qty']} | ${l['unit']:,} | ${l['qty'] * l['unit']:,} |"
                          for l in po["lines"])
        chain = _approval_chain(total)
        status = []
        for i, t in enumerate(chain):
            if i == 0:
                status.append(f"- {t['approver']}: Auto-approved (within department budget)")
            elif i == len(chain) - 1:
                status.append(f"- {t['approver']} ({po['cfo']}): Required (order >${chain[i - 1]['max_amount']:,})")
            else:
                status.append(f"- {t['approver']} ({po['finance_director']}): Pending")
        return (
            f"Purchase order drafted with {po['vendor']}, ready for you to submit for approval. "
            f"Volume discount applied - saving ${discount:,}.\n\n"
            f"**{po['po_number']} (draft)** for {req}\n\n"
            f"| Item | Qty | Unit Price | Total |\n|---|---|---|---|\n{lines}\n\n"
            f"**Financial Summary:**\n"
            f"- Subtotal: ${subtotal:,}\n"
            f"- Volume Discount ({po['discount_pct']}%): -${discount:,}\n"
            f"- Tax ({po['tax_pct']}%): ${tax:,}\n"
            f"- Total: ${total:,}\n\n"
            f"**Approval Workflow (once submitted):**\n" + "\n".join(status) + "\n\n"
            f"Draft only. {_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Finance + Approval Rules]\nAgents: ProcurementAgent\n\n"
            f"Want me to prepare urgency notifications to expedite the approval?"
        )

    # ── expedite_approval ──────────────────────────────────────
    def _expedite_approval(self, params):
        req = params["request_id"]
        po = _PO_DRAFTS[req]
        _s, _d, _t, total = _po_totals(req)
        return (
            f"Urgency notifications drafted for both approvers, ready for you to send in Teams.\n\n"
            f"**Approval Status ({po['po_number']}, ${total:,}):**\n"
            f"- Current queue time: {po['queue_time']}\n"
            f"- Finance Director avg response: {po['fd_avg_response']}\n"
            f"- Escalation available: after {po['escalation_after']}\n\n"
            f"**Draft Teams notifications:**\n"
            f"1. To {po['finance_director']} (Finance Director) - Priority: HIGH - Channel: Finance Approvals - "
            f"\"URGENT: Engineering laptop PO needs approval - {po['needed_by']}.\"\n"
            f"2. To {po['cfo']} (CFO) - pre-notification for the >$75,000 threshold - "
            f"\"New hire equipment - time sensitive.\"\n\n"
            f"**Alternative Options If Delayed:**\n"
            f"- {po['it_inventory_units']} similar laptops available in IT inventory\n"
            f"- {po['rental_days']}-day rental option while awaiting delivery\n"
            f"- Splitting the order to stay under the CFO threshold is not offered: it would circumvent the approval control.\n\n"
            f"No notification was sent. {_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Approval Workflow]\nAgents: ProcurementAgent\n\n"
            f"Want to see how this affects your Q4 budget?"
        )

    # ── budget_impact ──────────────────────────────────────────
    def _budget_impact(self, params):
        req = params["request_id"]
        _s, _d, _t, total = _po_totals(req)
        b = _IT_BUDGET
        spent = sum(a for _c, a in b["spent_by_category"])
        remaining = b["budget"] - spent - total
        committed = (spent + total) * 100 / b["budget"]
        risk = "high" if committed >= 90 else ("medium" if committed >= 75 else "low")
        cats = "\n".join(f"- {c}: ${a:,} ({a * 100 / spent:.0f}%)" for c, a in b["spent_by_category"])
        it_vendors = [v for v in _VENDOR_CATALOG.values() if v["category"] == "IT Equipment"]
        conc = "\n".join(f"- {v['name']}: {v['annual_spend'] * 100 / spent:.0f}% of spend" for v in it_vendors)
        dup = sum(n * price for _l, n, price in b["duplicate_licenses"])
        dup_detail = "; ".join(f"{l} ({n} x ${price})" for l, n, price in b["duplicate_licenses"])
        return (
            f"{b['period']} IT budget analysis shows you'll be at {committed:.0f}% committed after this "
            f"purchase - {risk} risk level.\n\n"
            f"**{b['period']} IT Budget Status (${b['budget']:,})**\n\n"
            f"| Category | Amount | % of Budget |\n|---|---|---|\n"
            f"| Spent to Date | ${spent:,} | {spent * 100 / b['budget']:.1f}% |\n"
            f"| This PO ({req}) | ${total:,} | {total * 100 / b['budget']:.1f}% |\n"
            f"| Remaining | ${remaining:,} | {remaining * 100 / b['budget']:.1f}% |\n\n"
            f"**Spending by Category:**\n{cats}\n\n"
            f"**Vendor Concentration:**\n{conc}\n\n"
            f"**Alert:** ${dup:,} in duplicate software licenses identified - potential savings ({dup_detail}).\n\n"
            f"{_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic Finance + Budget Analytics]\nAgents: ProcurementAgent\n\n"
            f"Need an RFQ for office furniture for the same team?"
        )

    # ── draft_rfq ──────────────────────────────────────────────
    def _draft_rfq(self, params):
        rfq_id = "RFQ-2024-FRN-0145"
        r = _RFQ_DRAFTS[rfq_id]
        items = "\n".join(f"| {i} | ${lo:,}-${hi:,} |" for i, lo, hi in r["items"])
        low = sum(lo for _i, lo, _h in r["items"])
        high = sum(hi for _i, _l, hi in r["items"])
        crit = " | ".join(f"{c}: {w}%" for c, w in r["criteria"])
        return (
            f"RFQ drafted for your top 3 furniture vendors with a {r['response_hours']}-hour response "
            f"deadline, ready for you to send.\n\n"
            f"**{rfq_id} (draft)** for {r['for']}\n\n"
            f"| Item | Est. Budget |\n|---|---|\n{items}\n| **Total** | **${low:,}-${high:,}** |\n\n"
            f"**Vendors to invite:** {', '.join(r['vendors'])}\n\n"
            f"**Evaluation Criteria:** {crit} (total {sum(w for _c, w in r['criteria'])}%)\n\n"
            f"**Timeline:** responses due {r['response_hours']} hours after you send it; decision by end of week.\n\n"
            f"No RFQ was distributed. {_PROCUREMENT_GATE}\n\n"
            f"Source: [Synthetic RFQ Templates + Vendor Portal]\nAgents: ProcurementAgent\n\n"
            f"Want a summary of everything we prepared?"
        )


if __name__ == "__main__":
    agent = ProcurementAgent()
    print(agent.perform(operation="vendor_comparison", category="IT equipment"))
    for op in ["draft_purchase_order", "expedite_approval", "budget_impact", "draft_rfq"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
