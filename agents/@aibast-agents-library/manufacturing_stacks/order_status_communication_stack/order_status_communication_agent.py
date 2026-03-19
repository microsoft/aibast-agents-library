"""
Order Status Communication Agent

Tracks manufacturing orders through production and shipment stages,
generates customer-facing status updates, identifies delays proactively,
and drafts notification messages with recovery timelines.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/order-status-communication",
    "version": "1.0.0",
    "display_name": "Order Status Communication Agent",
    "description": "Tracks manufacturing orders through fulfillment, generates proactive delay notifications, and drafts customer status updates with shipment details.",
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

ORDERS = {
    "ORD-7810": {
        "customer": "Ford Motor Company",
        "contact_name": "James Mitchell",
        "contact_email": "j.mitchell@ford.example.com",
        "product": "6R140 Transmission Housing",
        "quantity": 2500,
        "unit_price": 168.00,
        "order_date": "2026-02-01",
        "promised_date": "2026-03-20",
        "status": "in_production",
        "pct_complete": 74,
    },
    "ORD-7811": {
        "customer": "Caterpillar Inc.",
        "contact_name": "Rita Vasquez",
        "contact_email": "r.vasquez@cat.example.com",
        "product": "D11 Track Frame Weldment",
        "quantity": 40,
        "unit_price": 12450.00,
        "order_date": "2026-01-15",
        "promised_date": "2026-04-10",
        "status": "in_production",
        "pct_complete": 45,
    },
    "ORD-7812": {
        "customer": "Tesla Inc.",
        "contact_name": "Derek Chung",
        "contact_email": "d.chung@tesla.example.com",
        "product": "Model Y Rocker Panel Stamping",
        "quantity": 8000,
        "unit_price": 42.50,
        "order_date": "2026-02-10",
        "promised_date": "2026-03-15",
        "status": "shipped",
        "pct_complete": 100,
    },
    "ORD-7813": {
        "customer": "John Deere",
        "contact_name": "Angela Torres",
        "contact_email": "a.torres@deere.example.com",
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
    "ORD-7813": {
        "reason": "Raw material shortage -- alloy steel bar stock delayed from supplier",
        "original_date": "2026-03-28",
        "revised_date": "2026-04-08",
        "days_delayed": 11,
        "recovery_actions": [
            "Alternate supplier qualified; first shipment arriving 2026-03-19",
            "Weekend overtime shifts approved for CNC cell",
            "Partial shipment of 200 units by 2026-03-28",
        ],
        "cost_impact": 14200.00,
    },
}

CUSTOMER_CONTACTS = {
    "Ford Motor Company": {
        "account_manager": "Sarah Lin",
        "escalation_contact": "Tom Bradley, Plant Manager",
        "preferred_channel": "email",
        "sla_response_hours": 4,
    },
    "Caterpillar Inc.": {
        "account_manager": "Robert Kim",
        "escalation_contact": "VP Supply Chain",
        "preferred_channel": "EDI",
        "sla_response_hours": 8,
    },
    "Tesla Inc.": {
        "account_manager": "Sarah Lin",
        "escalation_contact": "Logistics Director",
        "preferred_channel": "portal",
        "sla_response_hours": 2,
    },
    "John Deere": {
        "account_manager": "Robert Kim",
        "escalation_contact": "Procurement Director",
        "preferred_channel": "email",
        "sla_response_hours": 4,
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _order_value(order_id):
    """Total dollar value of an order."""
    o = ORDERS[order_id]
    return round(o["quantity"] * o["unit_price"], 2)


def _is_at_risk(order_id):
    """Determine if an order is delayed or at risk of missing its date."""
    return ORDERS[order_id]["status"] == "delayed" or order_id in DELAY_REASONS


def _days_until_promise(order_id):
    """Rough days remaining until promised delivery (fixed calculation)."""
    # Using a fixed reference of 2026-03-17 for deterministic output
    promise = ORDERS[order_id]["promised_date"]
    year, month, day = map(int, promise.split("-"))
    ref_year, ref_month, ref_day = 2026, 3, 17
    return (year - ref_year) * 365 + (month - ref_month) * 30 + (day - ref_day)


def _build_customer_update(order_id):
    """Draft a markdown customer notification."""
    o = ORDERS[order_id]
    lines = []
    lines.append(f"**Subject:** Order {order_id} Status Update -- {o['product']}")
    lines.append(f"\nDear {o['contact_name']},\n")

    if order_id in DELAY_REASONS:
        d = DELAY_REASONS[order_id]
        lines.append(f"We are writing to inform you of a revised delivery date for your order.")
        lines.append(f"\n- **Original date:** {d['original_date']}")
        lines.append(f"- **Revised date:** {d['revised_date']}")
        lines.append(f"- **Reason:** {d['reason']}")
        lines.append("\n**Recovery actions underway:**")
        for action in d["recovery_actions"]:
            lines.append(f"- {action}")
    elif o["status"] == "shipped":
        sh = SHIPMENTS.get(order_id, {})
        lines.append(f"Your order has shipped and is on its way.")
        lines.append(f"\n- **Carrier:** {sh.get('carrier', 'TBD')}")
        lines.append(f"- **Tracking:** {sh.get('tracking_number', 'TBD')}")
        lines.append(f"- **Est. delivery:** {sh.get('est_delivery', 'TBD')}")
    else:
        lines.append(f"Your order is progressing on schedule.")
        lines.append(f"\n- **Completion:** {o['pct_complete']}%")
        lines.append(f"- **Promised delivery:** {o['promised_date']}")

    lines.append("\nPlease do not hesitate to reach out with any questions.")
    lines.append(f"\nBest regards,")
    am = CUSTOMER_CONTACTS.get(o["customer"], {}).get("account_manager", "Account Team")
    lines.append(f"{am}")
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
            "description": __manifest__["description"],
            "operations": [
                "order_lookup",
                "shipment_tracking",
                "delay_notification",
                "customer_update",
            ],
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "order_lookup")
        dispatch = {
            "order_lookup": self._order_lookup,
            "shipment_tracking": self._shipment_tracking,
            "delay_notification": self._delay_notification,
            "customer_update": self._customer_update,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _order_lookup(self, **kwargs) -> str:
        lines = ["## Order Status Dashboard\n"]
        lines.append("| Order | Customer | Product | Qty | Value | Status | Complete | Promise Date | Days Left |")
        lines.append("|-------|----------|---------|-----|-------|--------|----------|--------------|-----------|")
        for oid, o in ORDERS.items():
            val = _order_value(oid)
            dl = _days_until_promise(oid)
            risk_flag = " **DELAYED**" if _is_at_risk(oid) else ""
            lines.append(
                f"| {oid} | {o['customer']} | {o['product'][:28]} | {o['quantity']:,} | "
                f"${val:,.2f} | {o['status']}{risk_flag} | {o['pct_complete']}% | {o['promised_date']} | {dl} |"
            )
        total_val = sum(_order_value(oid) for oid in ORDERS)
        at_risk_val = sum(_order_value(oid) for oid in ORDERS if _is_at_risk(oid))
        lines.append(f"\n**Total order book value:** ${total_val:,.2f}")
        lines.append(f"**At-risk order value:** ${at_risk_val:,.2f}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _shipment_tracking(self, **kwargs) -> str:
        lines = ["## Shipment Tracking\n"]
        if not SHIPMENTS:
            lines.append("No active shipments at this time.")
            return "\n".join(lines)

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
            o = ORDERS.get(oid, {})
            lines.append(f"- **{oid}** ({o.get('customer', 'N/A')}): {o.get('product', 'N/A')} -- "
                         f"{o.get('quantity', 0):,} units, ${_order_value(oid):,.2f}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _delay_notification(self, **kwargs) -> str:
        lines = ["## Delay Notifications\n"]
        if not DELAY_REASONS:
            lines.append("No delays currently reported.")
            return "\n".join(lines)

        for oid, d in DELAY_REASONS.items():
            o = ORDERS[oid]
            cc = CUSTOMER_CONTACTS.get(o["customer"], {})
            lines.append(f"### {oid} -- {o['customer']}")
            lines.append(f"- **Product:** {o['product']}")
            lines.append(f"- **Quantity:** {o['quantity']:,} units (${_order_value(oid):,.2f})")
            lines.append(f"- **Delay:** {d['days_delayed']} days ({d['original_date']} -> {d['revised_date']})")
            lines.append(f"- **Reason:** {d['reason']}")
            lines.append(f"- **Cost impact:** ${d['cost_impact']:,.2f}")
            lines.append(f"- **Account manager:** {cc.get('account_manager', 'N/A')}")
            lines.append(f"- **SLA response window:** {cc.get('sla_response_hours', 'N/A')} hours")
            lines.append(f"- **Preferred channel:** {cc.get('preferred_channel', 'email')}")
            lines.append("\n**Recovery actions:**")
            for action in d["recovery_actions"]:
                lines.append(f"- {action}")
            lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _customer_update(self, **kwargs) -> str:
        lines = ["## Customer Update Drafts\n"]
        lines.append("The following update messages have been prepared for all active orders:\n")
        for oid in ORDERS:
            lines.append(f"---\n### {oid} -- {ORDERS[oid]['customer']}\n")
            lines.append(_build_customer_update(oid))
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = OrderStatusCommunicationAgent()
    for op in agent.metadata["operations"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
