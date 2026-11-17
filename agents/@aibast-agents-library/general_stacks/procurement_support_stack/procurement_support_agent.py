"""
Discount Finder Agent

Finds every available discount for a company's upcoming purchase orders
(IT equipment, software licenses, office supplies): quarter-end vendor deals,
annual-commitment license savings, bulk-tier consolidation, a draft purchase
order, and a dated action timeline.

Where a real deployment would connect to ERP, vendor contracts, promotion
feeds and license management, this agent uses a synthetic data layer so it
runs anywhere without credentials.
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
    "version": "1.2.0",
    "display_name": "Discount Finder Agent",
    "description": "Identify and optimize savings opportunities across vendors, contracts, and purchasing cycles to reduce costs and increase procurement efficiency.",
    "author": "AIBAST",
    "tags": ["procurement", "discounts", "contracts", "licenses", "purchase-orders"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

# Planned purchases for the quarter and the best available discount per category.
_DISCOUNT_OPPORTUNITIES = [
    {"id": "DISC-101", "category": "IT Equipment", "planned_spend": 85000, "discount_pct": 20,
     "discount": "20% quarter-end", "basis": "Quarter-end vendor promotions (Dell, HP, Lenovo)"},
    {"id": "DISC-102", "category": "Software Licenses", "planned_spend": 78000, "discount_pct": 35,
     "discount": "35% annual commit", "basis": "Annual commitment instead of monthly / per-seat billing"},
    {"id": "DISC-103", "category": "Office Supplies", "planned_spend": 47000, "discount_pct": 15,
     "discount": "15% bulk tier", "basis": "Consolidate 6 separate orders into 2 (Office Depot bulk tier)"},
]

_TIME_SENSITIVE_ALERTS = [
    "Dell quarter-end pricing expires Friday",
    "Microsoft license increase effective next month",
    "Office Depot bulk tier requires $5K minimum",
]

_IT_PROMOTIONS = [
    {"vendor": "Dell", "products": "Laptops, monitors", "discount_pct": 20, "expires": "Friday", "savings": 9050},
    {"vendor": "HP", "products": "Printers, accessories", "discount_pct": 18, "expires": "Friday", "savings": 2400},
    {"vendor": "Lenovo", "products": "Desktops", "discount_pct": 15, "expires": "Sunday", "savings": 2650},
]

_DELL_LINES = [
    {"item": "Dell Latitude 7440 laptops", "qty": 25, "unit_price": 1250},
    {"item": "monitors (27\" 4K)", "qty": 40, "unit_price": 350},
]

_PURCHASE_ORDER = {
    "po_number": "PO-2024-Q1-0234", "vendor": "Dell", "discount_pct": 20,
    "free_dock_min_units": 50, "free_shipping_over": 25000,
    "cutoff": "Thursday 5 PM",
}

_LICENSES = [
    {"product": "Microsoft 365", "current": "Monthly", "recommended": "Annual", "annual_savings": 12400},
    {"product": "Adobe Creative", "current": "Per-seat", "recommended": "Enterprise", "annual_savings": 8200},
    {"product": "Salesforce", "current": "Standard", "recommended": "Annual", "annual_savings": 4800},
    {"product": "Zoom", "current": "Monthly", "recommended": "Annual", "annual_savings": 1900},
]

_PRICE_INCREASE = {"vendor": "Microsoft", "pct": 12, "license_spend": 78000, "effective": "next month"}

_DUPLICATE_LICENSES = [
    {"finding": "Zoom and Microsoft Teams meetings both licensed for the same 40 users", "seats": 40},
    {"finding": "Standalone Adobe Acrobat seats for users already on Adobe Creative", "seats": 12},
]

_OFFICE_LEVERS = [
    {"current": "6 separate orders", "optimized": "2 consolidated orders", "savings": 3550},
    {"current": "Random timing", "optimized": "Aligned with promotions", "savings": 1200},
    {"current": "Multiple vendors", "optimized": "Primary vendor (Office Depot)", "savings": 890},
]

_BULK_TIER = {"monthly_avg": 7800, "months": 3, "tier": "Gold", "tier_pct": 15, "standard_pct": 8}

_DISCOUNT_GATE = (
    "Synthetic savings analysis only. No supplier is selected or contacted, no "
    "order or renewal is placed, and no commercial commitment is made."
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _planned_total():
    total = 0
    for item in _DISCOUNT_OPPORTUNITIES:
        total += item["planned_spend"]
    return total


def _office_savings():
    total = 0
    for lever in _OFFICE_LEVERS:
        total += lever["savings"]
    return total


def _category_savings(item):
    """Projected savings shown in the scan: office supplies use the first consolidation lever (the bulk-tier order
    consolidation); IT and software apply the category discount to planned spend."""
    if item["id"] == "DISC-103":
        return _OFFICE_LEVERS[0]["savings"]
    return item["planned_spend"] * item["discount_pct"] // 100


def _dell_po():
    lines, before, after = [], 0, 0
    for line in _DELL_LINES:
        list_total = line["qty"] * line["unit_price"]
        net = list_total * (100 - _PURCHASE_ORDER["discount_pct"]) // 100
        before += list_total
        after += net
        lines.append({"item": line["item"], "qty": line["qty"], "list_total": list_total, "net": net})
    return lines, before, after


def _license_total():
    total = 0
    for lic in _LICENSES:
        total += lic["annual_savings"]
    return total


def _price_increase_avoided():
    return _PRICE_INCREASE["license_spend"] * _PRICE_INCREASE["pct"] // 100


def _it_locked_savings():
    total = 0
    for promo in _IT_PROMOTIONS:
        total += promo["savings"]
    return total


def _money(value):
    return f"${value:,}"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "savings_scan", "time_sensitive_deals", "consolidation_analysis", "purchase_timing",
    "draft_purchase_order", "license_optimization",
]


class ProcurementSupportAgent(BasicAgent):
    """
    Discount-finder decision-support agent.

    Operations:
        savings_scan           - all available discounts for the upcoming purchase orders
        time_sensitive_deals   - expiring IT equipment deals and what to lock in now
        consolidation_analysis - office-supply bulk strategy and the Q1 total savings projection
        purchase_timing        - implementation plan / action timeline with savings at risk
        draft_purchase_order   - draft Dell PO plus the software license savings
        license_optimization   - license conversions, price-increase avoidance and duplicate licenses
    """

    def __init__(self):
        self.name = "ProcurementSupportAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} This is the Discount Finder Agent. "
                "Always use this tool to find discounts for upcoming purchase orders "
                "(office supplies, IT equipment, software licenses). Demo flow: identify "
                "all available discounts -> savings_scan; IT equipment deals to lock in "
                "-> time_sensitive_deals; prepare the PO and show software license "
                "savings -> draft_purchase_order; bulk order strategy and total savings "
                "projection -> consolidation_analysis; implementation plan / action "
                "timeline -> purchase_timing. Every operation has demo defaults, so call "
                "it without asking for details. Analyze fictional records only; the PO "
                "is a draft pending the user's approval. Never select or contact a "
                "supplier, place an order, renew a contract, or make a commercial "
                "commitment."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "savings_scan: identify all available discounts for upcoming "
                            "purchases. time_sensitive_deals: expiring IT equipment deals "
                            "and what to lock in immediately. draft_purchase_order: prepare "
                            "the Dell PO and show the software license savings. "
                            "consolidation_analysis: office-supply bulk order strategy and "
                            "the total (Q1) savings projection. purchase_timing: "
                            "implementation plan, deadlines and action timeline. "
                            "license_optimization: software license conversions, the "
                            "Microsoft price increase and duplicate licenses."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "savings_scan")
        dispatch = {
            "savings_scan": self._savings_scan,
            "time_sensitive_deals": self._time_sensitive_deals,
            "consolidation_analysis": self._consolidation_analysis,
            "purchase_timing": self._purchase_timing,
            "draft_purchase_order": self._draft_purchase_order,
            "license_optimization": self._license_optimization,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        return handler(kwargs)

    # ── savings_scan (video turn 1) ────────────────────────────
    def _savings_scan(self, params):
        rows, total = "", 0
        for item in _DISCOUNT_OPPORTUNITIES:
            saving = _category_savings(item)
            total += saving
            rows += (f"| {item['id']} | {item['category']} | {_money(item['planned_spend'])} | "
                     f"{item['discount']} | {_money(saving)} |\n")
        pct = round(total * 100 / _planned_total())
        alerts = "".join(f"- {a}\n" for a in _TIME_SENSITIVE_ALERTS)
        return (
            f"I've analyzed your planned purchases against all vendor agreements, seasonal "
            f"promotions, and volume tiers. Total savings potential: {_money(total)} "
            f"({pct}% of {_money(_planned_total())} spend).\n\n"
            "**Savings Opportunity Scan - Discount Opportunities Identified**\n\n"
            "| ID | Category | Planned Spend | Available Discount | Savings |\n"
            "|---|---|---|---|---|\n"
            f"{rows}\n"
            f"**Time-Sensitive Alerts:**\n{alerts}\n"
            "Savings are projected, not realized savings. Validate demand, terms, quality, "
            "and authority before action.\n\n"
            f"**Approval gate:** {_DISCOUNT_GATE}\n\n"
            "Source: [Vendor Contracts + Promotion Database]\n"
            "Agents: ProcurementSupportAgent\n\n"
            "Want me to detail the IT equipment deals expiring this week?"
        )

    # ── time_sensitive_deals (video turn 2) ────────────────────
    def _time_sensitive_deals(self, params):
        rows = "".join(f"| {p['vendor']} | {p['products']} | {p['discount_pct']}% off | {p['expires']} |\n"
                       for p in _IT_PROMOTIONS)
        lines, _before, _after = _dell_po()
        dell = "".join(f"- {l['qty']} {l['item']}: {_money(l['list_total'])} -> {_money(l['net'])}\n" for l in lines)
        return (
            "Three IT vendors have quarter-end promotions expiring this week. Recommended action: "
            "lock in the Dell and HP deals today.\n\n"
            "**Expiring IT Promotions**\n\n"
            "| Vendor | Products | Discount | Expires |\n|---|---|---|---|\n"
            f"{rows}\n"
            "**Dell Deal Analysis (Highest Value):**\n"
            f"{dell}"
            f"- Dock stations included free ({_PURCHASE_ORDER['free_dock_min_units']}+ unit orders)\n\n"
            f"**Action Required:** PO must be submitted by {_PURCHASE_ORDER['cutoff']} to guarantee "
            "pricing. Confirm current terms through the approved procurement process.\n\n"
            f"**Approval gate:** {_DISCOUNT_GATE}\n\n"
            "Source: [Dell Premier + HP Direct + Lenovo Portal]\n"
            "Agents: ProcurementSupportAgent\n\n"
            "Should I prepare the PO and show the software license savings?"
        )

    # ── draft_purchase_order (video turn 3) ────────────────────
    def _draft_purchase_order(self, params):
        lines, before, after = _dell_po()
        po = _PURCHASE_ORDER
        rows = "".join(f"| {l['item']} | {l['qty']} | {_money(l['list_total'])} | {_money(l['net'])} |\n" for l in lines)
        lic_rows = "".join(f"| {x['product']} | {x['current']} | {x['recommended']} | {_money(x['annual_savings'])} |\n"
                           for x in _LICENSES)
        ms = _LICENSES[0]["annual_savings"]
        shipping = "Free shipping (order >$25K)" if after > po["free_shipping_over"] else "Standard shipping"
        return (
            f"Dell PO drafted for {_money(after)} (saving {_money(before - after)}). Software analysis "
            "shows a major opportunity with annual commitments.\n\n"
            f"**Draft {po['vendor']} {po['po_number']} - Not Submitted**\n\n"
            "| Line | Qty | List | Net (20% off) |\n|---|---|---|---|\n"
            f"{rows}"
            f"| Docking stations | {po['free_dock_min_units']}+ units | included | $0 |\n"
            f"| **Total** | | **{_money(before)}** | **{_money(after)}** |\n\n"
            f"- Quarter-end discount: {po['discount_pct']}%\n"
            f"- {shipping}\n"
            "- Status: ready for you to approve and submit (pending your approval; not sent to Dell)\n\n"
            "**Software License Optimization**\n\n"
            "| Product | Current | Recommended | Annual Savings |\n|---|---|---|---|\n"
            f"{lic_rows}\n"
            f"**Key Insight:** {_PRICE_INCREASE['vendor']} is increasing prices "
            f"{_PRICE_INCREASE['pct']}% {_PRICE_INCREASE['effective']}. Locking in annual now saves "
            f"{_money(ms)} PLUS avoids the price increase ({_money(_price_increase_avoided())} additional).\n"
            f"**Total Software Opportunity:** {_money(_license_total())} annual savings\n\n"
            f"**Approval gate:** {_DISCOUNT_GATE}\n\n"
            "Source: [License Management + Vendor Pricing]\n"
            "Agents: ProcurementSupportAgent\n\n"
            "Want me to model the bulk order strategy for office supplies?"
        )

    # ── consolidation_analysis (video turn 4) ──────────────────
    def _consolidation_analysis(self, params):
        rows = ""
        for i, lever in enumerate(_OFFICE_LEVERS):
            sign = "" if i == 0 else "+"
            rows += f"| {lever['current']} | {lever['optimized']} | {sign}{_money(lever['savings'])} |\n"
        bt = _BULK_TIER
        quarterly = bt["monthly_avg"] * bt["months"]
        summary = [
            ("IT Equipment", _it_locked_savings(), "Quarter-end deals (Dell, HP, Lenovo)"),
            ("Software", _license_total(), "Annual commitments"),
            ("Office Supplies", _office_savings(), "Bulk consolidation"),
            ("Price Increase Avoidance", _price_increase_avoided(), "Early lock-in"),
        ]
        total = 0
        srows = ""
        for name, value, method in summary:
            total += value
            srows += f"| {name} | {_money(value)} | {method} |\n"
        pct = round(total * 100 / _planned_total())
        return (
            f"Office supply consolidation unlocks the {bt['tier_pct']}% bulk tier. Combined with timing "
            f"optimization, total Q1 savings reaches {_money(total)}.\n\n"
            "**Office Supply Bulk Strategy**\n\n"
            "| Current Approach | Optimized Approach | Savings |\n|---|---|---|\n"
            f"{rows}\n"
            "**Bulk Tier Qualification:**\n"
            f"- Current monthly: {_money(bt['monthly_avg'])} average\n"
            f"- Consolidated quarterly: {_money(quarterly)}\n"
            f"- Tier unlocked: {bt['tier']} ({bt['tier_pct']}% discount vs {bt['standard_pct']}% standard)\n\n"
            "**Q1 Total Savings Summary**\n\n"
            "| Category | Savings | Method |\n|---|---|---|\n"
            f"{srows}"
            f"| **TOTAL** | **{_money(total)}** | {pct}% of spend |\n\n"
            "Consolidation may introduce resilience or supplier-diversity tradeoffs; the analysis "
            "does not recommend a supplier award.\n\n"
            f"**Approval gate:** {_DISCOUNT_GATE}\n\n"
            "Source: [Purchase History + Vendor Tiers]\n"
            "Agents: ProcurementSupportAgent\n\n"
            "Want me to create the implementation plan with deadlines?"
        )

    # ── purchase_timing (video turn 5) ─────────────────────────
    def _purchase_timing(self, params):
        _lines, before, after = _dell_po()
        ms_at_risk = _LICENSES[0]["annual_savings"] + _price_increase_avoided()
        hp = _IT_PROMOTIONS[1]
        return (
            "**Purchase Timing Review - Action Timeline (draft plan)**\n\n"
            "Implementation plan with critical deadlines; every action is yours to approve.\n\n"
            "**This Week (Critical):**\n"
            f"- Today: Approve Dell {_PURCHASE_ORDER['po_number']} ({_money(before - after)} savings at risk)\n"
            f"- Thursday: Submit Microsoft annual commitment ({_money(ms_at_risk)} at risk)\n"
            f"- Friday: Lock HP printer deal ({_money(hp['savings'])} savings)\n\n"
            "**Next Week:**\n"
            "- Monday: Consolidate office supply orders\n"
            "- Tuesday: Review Adobe Enterprise proposal\n"
            "- Wednesday: Finalize Salesforce annual terms\n\n"
            "**End of Month:**\n"
            "- Submit consolidated Q1 supply order\n"
            "- Complete all license conversions\n\n"
            "**Recommended tracking (ready for you to turn on):**\n"
            "- Calendar reminders for all deadlines\n"
            "- Approval workflow notifications\n"
            "- Price monitoring alerts\n\n"
            f"**Approval gate:** {_DISCOUNT_GATE}\n\n"
            "Source: [Project Management + Calendar]\n"
            "Agents: ProcurementSupportAgent\n\n"
            "Want a summary and executive report for leadership?"
        )

    # ── license_optimization (one-pager: duplicate licenses) ───
    def _license_optimization(self, params):
        rows = "".join(f"| {x['product']} | {x['current']} | {x['recommended']} | {_money(x['annual_savings'])} |\n"
                       for x in _LICENSES)
        dups = "".join(f"- {d['finding']} ({d['seats']} seats)\n" for d in _DUPLICATE_LICENSES)
        return (
            "**Software License Optimization**\n\n"
            "| Product | Current | Recommended | Annual Savings |\n|---|---|---|---|\n"
            f"{rows}"
            f"| **Total** | | | **{_money(_license_total())}** |\n\n"
            f"**Price increase:** {_PRICE_INCREASE['vendor']} +{_PRICE_INCREASE['pct']}% "
            f"{_PRICE_INCREASE['effective']} on {_money(_PRICE_INCREASE['license_spend'])} of planned "
            f"license spend = {_money(_price_increase_avoided())} avoided by locking in now.\n\n"
            f"**Duplicate licenses flagged for review:**\n{dups}\n"
            f"**Approval gate:** {_DISCOUNT_GATE}\n\n"
            "Source: [License Management + Vendor Pricing]\n"
            "Agents: ProcurementSupportAgent"
        )


if __name__ == "__main__":
    agent = ProcurementSupportAgent()
    for op in ["savings_scan", "time_sensitive_deals", "draft_purchase_order",
               "consolidation_analysis", "purchase_timing"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
