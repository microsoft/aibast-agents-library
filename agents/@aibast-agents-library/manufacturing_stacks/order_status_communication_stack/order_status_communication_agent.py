"""
Order Status Communication Agent

Tracks manufacturing orders through production and shipment stages,
generates customer-facing status updates, identifies delays proactively,
and drafts notification messages, recovery plans, multi-channel engagement
plans, quality summaries and performance views. The demo order is E-Cars Corp
PO #F2024-3847 (ORD-7810), 2,500 transmission housings hit by a supplier delay.
All records are fictional and use a fixed reference date (2026-03-17).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/order-status-communication",
    "version": "1.1.0",
    "display_name": "Order Status Communications Agent",
    "description": "Analyze a fixed synthetic order snapshot and prepare review-ready status, delay, recovery, and customer-message drafts. Never send a customer update or change an order, shipment, or production schedule.",
    "author": "AIBAST",
    "tags": ["orders", "communication", "shipment", "customer-service", "manufacturing"],
    "category": "manufacturing",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

REFERENCE_DATE = "2026-03-17"
DEFAULT_ORDER = "ORD-7810"

ORDERS = {
    "ORD-7810": {
        "customer": "E-Cars Corp",
        "po": "F2024-3847",
        "site": "Manufacturing Plant",
        "contact_name": "James Mitchell",
        "contact_role": "Procurement Manager",
        "contact_email": "j.mitchell@ecars.example.com",
        "product": "6R140 Transmission Housing",
        "quantity": 2500,
        "unit_price": 168.00,
        "order_date": "2026-02-01",
        "promised_date": "2026-03-20",
        "status": "delayed",
        "pct_complete": 74,
        "completed": 1850,
        "quality_passed": 1847,
        "in_production": 350,
        "queued": 300,
        "daily_output_before": 250,
        "daily_output_after": 325,
    },
    "ORD-7811": {
        "customer": "Ironridge Equipment Co.",
        "po": "IR-55120",
        "site": "Assembly Works",
        "contact_name": "Rita Vasquez",
        "contact_role": "Buyer",
        "contact_email": "r.vasquez@ironridge.example.com",
        "product": "Track Frame Weldment",
        "quantity": 40,
        "unit_price": 12450.00,
        "order_date": "2026-01-15",
        "promised_date": "2026-04-10",
        "status": "in_production",
        "pct_complete": 45,
    },
    "ORD-7812": {
        "customer": "Voltline Motors",
        "po": "VM-20931",
        "site": "Vehicle Plant",
        "contact_name": "Derek Chung",
        "contact_role": "Logistics Lead",
        "contact_email": "d.chung@voltline.example.com",
        "product": "EV Rocker Panel Stamping",
        "quantity": 8000,
        "unit_price": 42.50,
        "order_date": "2026-02-10",
        "promised_date": "2026-03-15",
        "status": "shipped",
        "pct_complete": 100,
    },
    "ORD-7813": {
        "customer": "Greenfield Agri Machines",
        "po": "GA-77804",
        "site": "Hydraulics Plant",
        "contact_name": "Angela Torres",
        "contact_role": "Procurement Director",
        "contact_email": "a.torres@greenfield.example.com",
        "product": "Hydraulic Cylinder Barrel",
        "quantity": 600,
        "unit_price": 385.00,
        "order_date": "2026-02-18",
        "promised_date": "2026-03-28",
        "status": "delayed",
        "pct_complete": 30,
    },
}

SHIPMENTS = {
    "ORD-7812": {
        "carrier": "XPO Logistics",
        "tracking_number": "XPO-884291047",
        "ship_date": "2026-03-12",
        "est_delivery": "2026-03-15",
        "origin": "Detroit, MI",
        "destination": "Fremont, CA",
        "weight_kg": 4200,
        "status": "in_transit",
    },
}

DELAY_REASONS = {
    "ORD-7810": {
        "supplier": "Midwest Casting (aluminum)",
        "reason": "Supplier delay: aluminum casting equipment failure + force majeure",
        "original_date": "2026-03-20",
        "revised_date": "2026-03-23",
        "initial_delay_days": 7,
        "days_delayed": 3,
        "recovery_actions": [
            ["Alternative supplier", "Secured material", "$12K premium", 12000],
            ["Weekend shifts", "+150 units", "$18K overtime", 18000],
            ["Air freight (first 500 units)", "2-day delivery", "$24K (we absorb)", 24000],
            ["Daily output increase", "+75 units/day", "Existing capacity", 0],
        ],
        "compensation_pct": 2,
        "compensation_extras": ["Priority scheduling on next order", "Dedicated quality liaison"],
        "timeline": [
            ["Day 1-2", "Complete remaining 650 units"],
            ["Day 3", "Final quality inspection"],
            ["Day 4", "Packaging complete"],
            ["Day 5-6", "Expedited shipping"],
        ],
    },
    "ORD-7813": {
        "supplier": "Bar stock mill (alloy steel)",
        "reason": "Raw material shortage -- alloy steel bar stock delayed from supplier",
        "original_date": "2026-03-28",
        "revised_date": "2026-04-08",
        "initial_delay_days": 11,
        "days_delayed": 11,
        "recovery_actions": [
            ["Alternate supplier qualified", "First shipment arriving 2026-03-19", "$6.2K premium", 6200],
            ["Weekend overtime shifts for CNC cell", "+80 units/week", "$8K overtime", 8000],
            ["Partial shipment", "200 units by 2026-03-28", "Existing freight", 0],
        ],
        "compensation_pct": 0,
        "compensation_extras": ["Account manager call to agree the partial shipment"],
        "timeline": [
            ["Week 1", "Alternate supplier material received"],
            ["Week 2", "Partial shipment of 200 units"],
            ["Week 3", "Remaining 400 units complete and shipped"],
        ],
    },
}

CUSTOMER_CONTACTS = {
    "E-Cars Corp": {
        "account_manager": "Sarah Lin",
        "escalation_contact": "Tom Bradley, Plant Manager",
        "cc": ["Tom Bradley (Plant Manager)", "Sarah Chen (Quality)", "Logistics team"],
        "preferred_channel": "email",
        "channels": ["Email", "EDI 856 ASN", "Supplier portal", "Phone call"],
        "follow_up_call": "Today 2 PM EST",
        "customer_tier": "Strategic",
        "sla_response_hours": 4,
    },
    "Ironridge Equipment Co.": {
        "account_manager": "Robert Kim",
        "escalation_contact": "VP Supply Chain",
        "cc": ["VP Supply Chain"],
        "preferred_channel": "EDI",
        "channels": ["EDI 856 ASN", "Email"],
        "follow_up_call": "Weekly status call",
        "customer_tier": "Strategic",
        "sla_response_hours": 8,
    },
    "Voltline Motors": {
        "account_manager": "Sarah Lin",
        "escalation_contact": "Logistics Director",
        "cc": ["Logistics Director"],
        "preferred_channel": "portal",
        "channels": ["Supplier portal", "Email"],
        "follow_up_call": "On request",
        "customer_tier": "Priority",
        "sla_response_hours": 2,
    },
    "Greenfield Agri Machines": {
        "account_manager": "Robert Kim",
        "escalation_contact": "Procurement Director",
        "cc": ["Procurement Director"],
        "preferred_channel": "email",
        "channels": ["Email", "Phone call"],
        "follow_up_call": "Tomorrow 10 AM CST",
        "customer_tier": "Priority",
        "sla_response_hours": 4,
    },
}

QUALITY_PLANS = {
    "ORD-7810": {
        "incoming_material": ["100% dimensional inspection", "Metallurgical testing (batch samples)", "Hardness verification",
                              "Chemical composition analysis", "Certification: material test reports provided"],
        "production": ["In-process inspection: every 50 units", "Statistical process control (SPC) active",
                       "Coordinate measuring machine (CMM): 10% sample", "Visual inspection: 100%"],
        "final_validation": ["Functional testing: 100%", "Dimensional report: full first article", "Surface finish verification",
                             "Packaging integrity check", "Quality documentation: Certificate of Conformance included"],
        "customer_requirements": ["PPAP Level 3 maintained", "Q1 supplier rating protected", "Advanced quality planning review: complete"],
        "yield_target_pct": 99.5,
    },
}

ACCOUNT_METRICS = {
    "E-Cars Corp": {
        "orders_12m": 47,
        "on_time_delivery_pct": 96.2,
        "quality_ppm": 185,
        "supplier_rating": "Q1 (top tier)",
        "annual_revenue": 14200000,
        "avg_delay_communication": "<4 hours",
        "recovery_success_pct": 94,
        "retention_after_delays_pct": 97,
        "lessons_learned": ["Supplier diversification accelerated", "Safety stock policy updated",
                            "Communication template refined", "Recovery playbook enhanced"],
    },
}

_OPERATIONS = [
    "order_lookup",
    "shipment_tracking",
    "delay_notification",
    "customer_update",
    "engagement_plan",
    "quality_validation",
    "performance_dashboard",
]

_NO_SIDE_EFFECT = (
    "> Fixed synthetic drafts; approval required. No email, EDI message, portal update, Teams message, "
    "or other customer communication was sent, and no order, shipment, or production schedule was changed."
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_order(query):
    """Order ID, PO number or customer name; the demo order when empty; None when nothing matches."""
    if not query:
        return DEFAULT_ORDER
    q = str(query).lower().replace("#", "").replace("po ", "").strip()
    for oid, o in ORDERS.items():
        if oid.lower() in q or o["po"].lower() in q or q in o["customer"].lower() or o["customer"].lower() in q:
            return oid
    return None


def _order_value(order_id):
    """Total dollar value of an order."""
    o = ORDERS[order_id]
    return round(o["quantity"] * o["unit_price"], 2)


def _is_at_risk(order_id):
    """Determine if an order is delayed or at risk of missing its date."""
    return ORDERS[order_id]["status"] == "delayed" or order_id in DELAY_REASONS


def _days_from_reference(iso):
    """Calendar days from the fixed reference date to an ISO date."""
    import datetime
    y, m, d = iso.split("-")
    r = REFERENCE_DATE.split("-")
    return (datetime.date(int(y), int(m), int(d)) - datetime.date(int(r[0]), int(r[1]), int(r[2]))).days


def _days_until_promise(order_id):
    """Days to the promised date, or to the revised date for a delayed order; blank once shipped."""
    if ORDERS[order_id]["status"] == "shipped":
        return "-"
    if order_id in DELAY_REASONS:
        return _days_from_reference(DELAY_REASONS[order_id]["revised_date"])
    return _days_from_reference(ORDERS[order_id]["promised_date"])


def _compensation(order_id):
    d = DELAY_REASONS[order_id]
    return round(_order_value(order_id) * d["compensation_pct"] / 100)


def _po(order_id):
    return f"PO #{ORDERS[order_id]['po']}"


def _build_customer_update(order_id):
    """Draft a markdown customer notification."""
    o = ORDERS[order_id]
    cc = CUSTOMER_CONTACTS.get(o["customer"], {})
    lines = []
    lines.append(f"**To:** {o['contact_name']} ({o.get('contact_role', 'Customer contact')})")
    if cc.get("cc"):
        lines.append(f"**CC:** {', '.join(cc['cc'])}")
    if order_id in DELAY_REASONS:
        d = DELAY_REASONS[order_id]
        lines.append(f"**Subject:** {_po(order_id)} Status Update - Revised Delivery Date")
        lines.append(f"\nDear {o['contact_name'].split(' ')[0]},\n")
        lines.append(f"I'm writing to update you on {_po(order_id)} ({o['quantity']:,} {o['product']} units).")
        if o.get("completed"):
            lines.append("\n**Current Status:**")
            lines.append(f"- Completed: {o['completed']:,} units ({o['pct_complete']}%)")
            lines.append(f"- Quality passed: {o['quality_passed']:,} units ({o['quality_passed'] * 100 / o['completed']:.1f}% yield)")
            lines.append(f"- In production: {o['in_production']:,} units")
            lines.append(f"- Queued: {o['queued']:,} units")
        orig = _days_from_reference(d["original_date"])
        rev = _days_from_reference(d["revised_date"])
        lines.append("\n**Delivery Update:**")
        lines.append(f"- Original: {orig} days from now ({d['original_date']})")
        lines.append(f"- Revised: {rev} days from now ({d['revised_date']}; {d['days_delayed']}-day delay)")
        lines.append("\n**Recovery Actions:**")
        for action, impact, _, _ in d["recovery_actions"]:
            if action.startswith("Daily output") and o.get("daily_output_before"):
                continue
            lines.append(f"- {action}: {impact}")
        if o.get("daily_output_before"):
            lines.append(f"- Daily output increased: {o['daily_output_before']} -> {o['daily_output_after']} units")
    elif o["status"] == "shipped":
        sh = SHIPMENTS.get(order_id, {})
        lines.append(f"**Subject:** {_po(order_id)} Shipped")
        lines.append(f"\nDear {o['contact_name'].split(' ')[0]},\n")
        lines.append("Your order has shipped and is on its way.")
        lines.append(f"\n- **Carrier:** {sh.get('carrier', 'TBD')}")
        lines.append(f"- **Tracking:** {sh.get('tracking_number', 'TBD')}")
        lines.append(f"- **Est. delivery:** {sh.get('est_delivery', 'TBD')}")
    else:
        lines.append(f"**Subject:** {_po(order_id)} Status Update")
        lines.append(f"\nDear {o['contact_name'].split(' ')[0]},\n")
        lines.append("Your order is progressing on schedule.")
        lines.append(f"\n- **Completion:** {o['pct_complete']}%")
        lines.append(f"- **Promised delivery:** {o['promised_date']}")
    lines.append("\nPlease do not hesitate to reach out with any questions.")
    lines.append("\nBest regards,")
    lines.append(f"{cc.get('account_manager', 'Account Team')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class OrderStatusCommunicationAgent(BasicAgent):
    """Tracks orders and generates proactive customer communications."""

    def __init__(self):
        self.name = "OrderStatusCommunicationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always call this tool to send (draft) order updates to a "
                "customer, draft the customer communication, show recovery plan details, show customer "
                "touchpoints or multi-channel engagement, show quality assurance and validation, or show the "
                "performance dashboard. The demo order is E-Cars Corp PO #F2024-3847 (ORD-7810), "
                "transmission housings delayed by a supplier; it is used when no order is named. Call this "
                "tool again for every follow-up in the session (for example 'show customer touchpoints', "
                "'show quality assurance and validation', 'show performance dashboard'); each one returns "
                "different records, so never answer a follow-up from earlier turns or from memory."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "order_lookup: order details and situation for a PO (e.g. 'send order updates to "
                            "E-Cars Corp for PO #F2024-3847'), plus the open-order book and delay risk. "
                            "customer_update: draft the customer communication / email for approval; never send. "
                            "delay_notification: recovery plan details (root cause, actions, costs, compensation, "
                            "timeline). engagement_plan: customer touchpoints across email, EDI, portal, follow-up "
                            "call and CRM note, prepared not sent. quality_validation: quality assurance and "
                            "validation summary. performance_dashboard: order and customer performance metrics "
                            "and lessons learned. shipment_tracking: the fixed synthetic shipment record."
                        ),
                    },
                    "order_id": {
                        "type": "string",
                        "description": (
                            "Order ID, PO number or customer: E-Cars Corp or PO #F2024-3847 is ORD-7810 (the "
                            "default); Ironridge is ORD-7811; Voltline is ORD-7812; Greenfield is ORD-7813."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "order_lookup")
        dispatch = {
            "order_lookup": self._order_lookup,
            "shipment_tracking": self._shipment_tracking,
            "delay_notification": self._delay_notification,
            "customer_update": self._customer_update,
            "engagement_plan": self._engagement_plan,
            "quality_validation": self._quality_validation,
            "performance_dashboard": self._performance_dashboard,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        order_id = _resolve_order(kwargs.get("order_id"))
        if order_id is None:
            return (f"> Fixed synthetic snapshot.\n\n**Not found:** no synthetic order matches "
                    f"`{kwargs.get('order_id')}`; no substitute record was used. Orders: {', '.join(ORDERS)}.")
        return handler(order_id)

    # -- video turn 1 ------------------------------------------------------
    def _order_lookup(self, order_id) -> str:
        o = ORDERS[order_id]
        lines = [f"## Order Status: {o['customer']} {_po(order_id)} ({order_id})\n",
                 "> Fixed synthetic snapshot; no live ERP, MES, carrier, or CRM system was queried.\n"]
        lines.append("**Order Details:**\n")
        lines.append(f"- Customer: {o['customer']} - {o['site']}")
        lines.append(f"- Product: {o['product']}")
        lines.append(f"- Quantity: {o['quantity']:,} units")
        lines.append(f"- Original delivery: {_days_from_reference(o['promised_date'])} days from now ({o['promised_date']})")
        lines.append(f"- Current status: {o['pct_complete']}% complete")
        if order_id in DELAY_REASONS:
            d = DELAY_REASONS[order_id]
            lines.append("\n**Situation:**\n")
            lines.append(f"- {d['reason']}")
            if d["initial_delay_days"] != d["days_delayed"]:
                lines.append(f"- Impact: {d['days_delayed']}-day delay (reduced from initial {d['initial_delay_days']} days)")
            else:
                lines.append(f"- Impact: {d['days_delayed']}-day delay")
            lines.append("- Recovery plan: Active")
        lines.append("\n**Open order book:**\n")
        lines.append("| Order | Customer | Product | Qty | Value | Status | Complete | Promise Date | Days Left |")
        lines.append("|-------|----------|---------|-----|-------|--------|----------|--------------|-----------|")
        for oid, x in ORDERS.items():
            risk_flag = " **DELAYED**" if _is_at_risk(oid) else ""
            lines.append(
                f"| {oid} | {x['customer']} | {x['product']} | {x['quantity']:,} | "
                f"${_order_value(oid):,.2f} | {x['status']}{risk_flag} | {x['pct_complete']}% | {x['promised_date']} | {_days_until_promise(oid)} |"
            )
        total_val = sum(_order_value(oid) for oid in ORDERS)
        at_risk_val = sum(_order_value(oid) for oid in ORDERS if _is_at_risk(oid))
        lines.append(f"\n**Total order book value:** ${total_val:,.2f}")
        lines.append(f"**At-risk order value:** ${at_risk_val:,.2f}")
        lines.append("\nSource: [D365 Production + Order Management] (synthetic)")
        lines.append("\n**Next step:** draft the customer communication?")
        return "\n".join(lines)

    # -- shipments ----------------------------------------------------------
    def _shipment_tracking(self, order_id) -> str:
        lines = ["## Shipment Tracking\n", "> Synthetic shipment record; confirm status in the approved carrier system.\n"]
        lines.append("| Order | Carrier | Tracking | Ship Date | Est Delivery | Route | Weight | Status |")
        lines.append("|-------|---------|----------|-----------|-------------|-------|--------|--------|")
        for oid, sh in SHIPMENTS.items():
            route = f"{sh['origin']} -> {sh['destination']}"
            lines.append(
                f"| {oid} | {sh['carrier']} | {sh['tracking_number']} | {sh['ship_date']} | "
                f"{sh['est_delivery']} | {route} | {sh['weight_kg']:,} kg | {sh['status']} |"
            )
        lines.append("\n### Shipped Orders Detail\n")
        for oid in SHIPMENTS:
            o = ORDERS[oid]
            lines.append(f"- **{oid}** ({o['customer']}): {o['product']} -- "
                         f"{o['quantity']:,} units, ${_order_value(oid):,.2f}")
        lines.append("\nCarrier status still needs validation in the approved carrier system.")
        return "\n".join(lines)

    # -- video turn 3 --------------------------------------------------------
    def _delay_notification(self, order_id) -> str:
        o = ORDERS[order_id]
        lines = [f"## Delay Mitigation & Recovery: {o['customer']} {_po(order_id)} ({order_id})\n",
                 "> Fixed synthetic draft for authorized review. No production schedule, shipment, or customer record was changed.\n"]
        if order_id not in DELAY_REASONS:
            lines.append(f"No delay is recorded for {order_id}; delayed orders: {', '.join(DELAY_REASONS)}.")
            return "\n".join(lines)
        d = DELAY_REASONS[order_id]
        cc = CUSTOMER_CONTACTS.get(o["customer"], {})
        lines.append("**Root Cause:**\n")
        lines.append(f"- Supplier: {d['supplier']}")
        lines.append(f"- Issue: {d['reason']}")
        lines.append(f"- Initial impact: {d['initial_delay_days']}-day delay")
        lines.append("\n**Recorded synthetic recovery options (our response):**\n")
        lines.append("| Action | Impact | Cost |\n|---|---|---|")
        total = 0
        for action, impact, cost_text, cost in d["recovery_actions"]:
            total += cost
            lines.append(f"| {action} | {impact} | {cost_text} |")
        lines.append(f"\n**Result:** {d['initial_delay_days']}-day delay -> {d['days_delayed']}-day delay "
                     f"(recovery cost ${total:,})")
        lines.append("\n**Compensation offer (proposed):**\n")
        if d["compensation_pct"]:
            lines.append(f"- {d['compensation_pct']}% discount (${_compensation(order_id):,} credit on ${_order_value(order_id):,.0f})")
        for extra in d["compensation_extras"]:
            lines.append(f"- {extra}")
        lines.append("\n**Updated Timeline:**\n")
        for when, step in d["timeline"]:
            lines.append(f"- {when}: {step}")
        lines.append(f"\n**Owner:** {cc.get('account_manager', 'Account Team')}; SLA response window "
                     f"{cc.get('sla_response_hours', 'N/A')} hours; preferred channel {cc.get('preferred_channel', 'email')}.")
        lines.append("\nSource: [Recovery Planning + Logistics] (synthetic)")
        lines.append("\n**Next step:** show the customer touchpoints?")
        return "\n".join(lines)

    # -- video turn 2 --------------------------------------------------------
    def _customer_update(self, order_id) -> str:
        o = ORDERS[order_id]
        contact = CUSTOMER_CONTACTS.get(o["customer"], {})
        lines = ["## Customer Update Drafts\n", _NO_SIDE_EFFECT + "\n"]
        lines.append(f"### Customer Communication Draft: {o['customer']} {_po(order_id)}\n")
        lines.append(
            f"**Synthetic communication profile:** {contact.get('customer_tier', 'Standard')} tier; "
            f"preferred channel {contact.get('preferred_channel', 'email')}; "
            f"authorized owner {contact.get('account_manager', 'Account Team')}.\n"
        )
        lines.append(_build_customer_update(order_id))
        lines.append("\nReady for you to review and send from Outlook; customer updates require an approved "
                     "communication tool and an authorized sender.")
        lines.append("\nSource: [Email Template + Production Data] (synthetic)")
        lines.append("\n**Next step:** see the detailed recovery plan?")
        return "\n".join(lines)

    # -- video turn 4 --------------------------------------------------------
    def _engagement_plan(self, order_id) -> str:
        o = ORDERS[order_id]
        cc = CUSTOMER_CONTACTS.get(o["customer"], {})
        lines = [f"## Multi-Channel Customer Engagement: {o['customer']} {_po(order_id)}\n", _NO_SIDE_EFFECT + "\n"]
        lines.append(f"Tailored to the {cc.get('customer_tier', 'Standard')} tier: {', '.join(cc.get('channels', []))}.\n")
        lines.append("| Channel | Prepared action | Status |\n|---|---|---|")
        for channel in cc.get("channels", []):
            if channel == "Email":
                lines.append(f"| Email (primary) | To {o['contact_name']} ({o.get('contact_role', '')}); CC {', '.join(cc.get('cc', []))}; read receipt requested | Ready to send |")
            elif channel == "EDI 856 ASN":
                lines.append("| EDI 856 ASN | Updated ship dates from the revised timeline; acknowledgment expected within 2 hours | Ready to transmit |")
            elif channel == "Supplier portal":
                lines.append(f"| {o['customer']} supplier portal | Status and revised date | Ready to sync |")
            elif channel == "Phone call":
                lines.append(f"| Follow-up call | {cc.get('follow_up_call', 'TBD')} with Account Manager + Production Manager; agenda: recovery plan review | Invite ready to send |")
        lines.append(f"\n**Touchpoints prepared:** {len(cc.get('channels', []))}")
        lines.append("\n**Proactive monitoring (to switch on):** daily production updates, quality milestone alerts, "
                     "shipping tracker with real-time status.")
        if order_id in DELAY_REASONS and DELAY_REASONS[order_id]["compensation_pct"]:
            lines.append(f"\n**Relationship management:** {DELAY_REASONS[order_id]['compensation_pct']}% discount "
                         f"(${_compensation(order_id):,}) ready to apply on approval; account note for priority service drafted.")
        lines.append("\nSource: [Outlook + EDI + Supplier Portal + CRM] (synthetic)")
        lines.append("\n**Next step:** review quality assurance and validation?")
        return "\n".join(lines)

    # -- video turn 5 --------------------------------------------------------
    def _quality_validation(self, order_id) -> str:
        o = ORDERS[order_id]
        plan = QUALITY_PLANS.get(order_id)
        lines = [f"## Quality Assurance & Validation: {o['customer']} {_po(order_id)}\n",
                 "> Fixed synthetic quality record; confirm in the quality management system before sharing.\n"]
        if not plan:
            lines.append(f"No enhanced quality plan is recorded for {order_id}.")
            return "\n".join(lines)
        lines.append("**Incoming material (alternative supplier):**\n")
        for item in plan["incoming_material"]:
            lines.append(f"- {item}")
        lines.append("\n**Production quality:**\n")
        for item in plan["production"]:
            lines.append(f"- {item}")
        yld = o["quality_passed"] * 100 / o["completed"]
        lines.append(f"- Current yield: {yld:.1f}% ({o['quality_passed']:,} of {o['completed']:,}; spec {plan['yield_target_pct']}%)")
        lines.append("\n**Final validation:**\n")
        for item in plan["final_validation"]:
            lines.append(f"- {item}")
        lines.append(f"\n**{o['customer']}-specific requirements:**\n")
        for item in plan["customer_requirements"]:
            lines.append(f"- {item}")
        lines.append("\nSource: [Quality Management System] (synthetic)")
        lines.append("\n**Next step:** see the performance dashboard?")
        return "\n".join(lines)

    # -- video turn 6 --------------------------------------------------------
    def _performance_dashboard(self, order_id) -> str:
        o = ORDERS[order_id]
        m = ACCOUNT_METRICS.get(o["customer"])
        cc = CUSTOMER_CONTACTS.get(o["customer"], {})
        lines = [f"## Order & Customer Performance: {o['customer']}\n",
                 "> Fixed synthetic metrics for internal review.\n"]
        lines.append(f"**This order ({_po(order_id)}):**\n")
        lines.append(f"- On-time delivery: {'Recovering (revised date)' if order_id in DELAY_REASONS else 'On track'}")
        if o.get("completed"):
            lines.append(f"- Quality: {o['quality_passed'] * 100 / o['completed']:.1f}% (target {QUALITY_PLANS[order_id]['yield_target_pct']}%)")
        lines.append(f"- Communication: proactive ({len(cc.get('channels', []))} touchpoints prepared)")
        lines.append("- Customer satisfaction: pending (survey to send after delivery)")
        if not m:
            lines.append(f"\nNo 12-month account metrics are recorded for {o['customer']}.")
            return "\n".join(lines)
        lines.append(f"\n**{o['customer']} account (last 12 months):**\n")
        lines.append("| Metric | Value |\n|---|---|")
        lines.append(f"| Total orders | {m['orders_12m']} |")
        lines.append(f"| On-time delivery | {m['on_time_delivery_pct']}% |")
        lines.append(f"| Quality PPM | {m['quality_ppm']} (excellent) |")
        lines.append(f"| Supplier rating | {m['supplier_rating']} |")
        lines.append(f"| Annual revenue | ${m['annual_revenue'] / 1000000:.1f}M |")
        lines.append("\n**Delay management effectiveness:**\n")
        lines.append(f"- Average delay communication: {m['avg_delay_communication']}")
        lines.append(f"- Recovery plan implementation: {m['recovery_success_pct']}% success")
        lines.append(f"- Customer retention after delays: {m['retention_after_delays_pct']}%")
        lines.append("\n**Lessons learned:**\n")
        for item in m["lessons_learned"]:
            lines.append(f"- {item}")
        lines.append("\nSource: [Power BI + CRM + Quality Systems] (synthetic)")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = OrderStatusCommunicationAgent()
    for op in ["order_lookup", "customer_update", "delay_notification", "engagement_plan",
               "quality_validation", "performance_dashboard"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
