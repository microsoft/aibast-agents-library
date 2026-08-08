# Order Status Communications Agent — Complete Synthetic Source Records

> **SYNTHETIC PILOT DATA.** This file is a complete Markdown rendering of the
> deterministic source constants used by the local agent and canonical transcript
> capture. Every identifier, person-like name, organization, measurement, score,
> quantity, amount, date, schedule, status, and relationship is fictional. No live
> customer or third-party system was queried.

## Source fidelity contract

- Deterministic source: `agents/@aibast-agents-library/manufacturing_stacks/order_status_communication_stack/order_status_communication_agent.py`
- Canonical transcript: `solutions/order-status-communication/evals/transcripts.json`
- Locked cases: `tests/demo_cases/order-status-communication.json`
- Values below are copied exactly from source constants. Do not recalculate, enrich,
  browse for, or substitute them when reproducing the pilot.

## Order, customer, contact, product, quantity, pricing, dates, status, and completion records

Canonical source constant: `ORDERS`.

```json
{
  "ORD-7810": {
    "customer": "Ford Motor Company",
    "contact_name": "James Mitchell",
    "contact_email": "j.mitchell@ford.example.com",
    "product": "6R140 Transmission Housing",
    "quantity": 2500,
    "unit_price": 168.0,
    "order_date": "2026-02-01",
    "promised_date": "2026-03-20",
    "status": "in_production",
    "pct_complete": 74
  },
  "ORD-7811": {
    "customer": "Caterpillar Inc.",
    "contact_name": "Rita Vasquez",
    "contact_email": "r.vasquez@cat.example.com",
    "product": "D11 Track Frame Weldment",
    "quantity": 40,
    "unit_price": 12450.0,
    "order_date": "2026-01-15",
    "promised_date": "2026-04-10",
    "status": "in_production",
    "pct_complete": 45
  },
  "ORD-7812": {
    "customer": "Tesla Inc.",
    "contact_name": "Derek Chung",
    "contact_email": "d.chung@tesla.example.com",
    "product": "Model Y Rocker Panel Stamping",
    "quantity": 8000,
    "unit_price": 42.5,
    "order_date": "2026-02-10",
    "promised_date": "2026-03-15",
    "status": "shipped",
    "pct_complete": 100
  },
  "ORD-7813": {
    "customer": "John Deere",
    "contact_name": "Angela Torres",
    "contact_email": "a.torres@deere.example.com",
    "product": "Hydraulic Cylinder Barrel",
    "quantity": 600,
    "unit_price": 385.0,
    "order_date": "2026-02-18",
    "promised_date": "2026-03-28",
    "status": "delayed",
    "pct_complete": 30
  }
}
```

## Carrier, tracking, route, dates, weight, and shipment status

Canonical source constant: `SHIPMENTS`.

```json
{
  "ORD-7812": {
    "carrier": "XPO Logistics",
    "tracking_number": "XPO-884291047",
    "ship_date": "2026-03-12",
    "est_delivery": "2026-03-15",
    "origin": "Detroit, MI",
    "destination": "Fremont, CA",
    "weight_kg": 4200,
    "status": "in_transit"
  }
}
```

## Delay reason, dates, duration, recovery options, and cost impact

Canonical source constant: `DELAY_REASONS`.

```json
{
  "ORD-7813": {
    "reason": "Raw material shortage -- alloy steel bar stock delayed from supplier",
    "original_date": "2026-03-28",
    "revised_date": "2026-04-08",
    "days_delayed": 11,
    "recovery_actions": [
      "Alternate supplier qualified; first shipment arriving 2026-03-19",
      "Weekend overtime shifts approved for CNC cell",
      "Partial shipment of 200 units by 2026-03-28"
    ],
    "cost_impact": 14200.0
  }
}
```

## Account ownership, escalation, preferred channel, tier, and response window

Canonical source constant: `CUSTOMER_CONTACTS`.

```json
{
  "Ford Motor Company": {
    "account_manager": "Sarah Lin",
    "escalation_contact": "Tom Bradley, Plant Manager",
    "preferred_channel": "email",
    "customer_tier": "Strategic",
    "sla_response_hours": 4
  },
  "Caterpillar Inc.": {
    "account_manager": "Robert Kim",
    "escalation_contact": "VP Supply Chain",
    "preferred_channel": "EDI",
    "customer_tier": "Strategic",
    "sla_response_hours": 8
  },
  "Tesla Inc.": {
    "account_manager": "Sarah Lin",
    "escalation_contact": "Logistics Director",
    "preferred_channel": "portal",
    "customer_tier": "Priority",
    "sla_response_hours": 2
  },
  "John Deere": {
    "account_manager": "Robert Kim",
    "escalation_contact": "Procurement Director",
    "preferred_channel": "email",
    "customer_tier": "Priority",
    "sla_response_hours": 4
  }
}
```

## Record-use boundary

Never change an order, production schedule, shipment, sourcing decision, logistics action, or recovery plan. Never send email, EDI, portal, Teams, or any other customer communication. An approved communication tool and authorized sender are required.

All exact values in this file remain synthetic pilot evidence. Production decisions
require fresh data from approved systems, identity and authorization controls, and
review by the accountable human owner.
