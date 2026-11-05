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

## Order, customer, contact, product, quantity, pricing, dates, status, production breakdown, and completion records

Canonical source constant: `ORDERS`.

```json
{
  "ORD-7810": {
    "customer": "E-Cars Corp",
    "po": "F2024-3847",
    "site": "Manufacturing Plant",
    "contact_name": "James Mitchell",
    "contact_role": "Procurement Manager",
    "contact_email": "j.mitchell@ecars.example.com",
    "product": "6R140 Transmission Housing",
    "quantity": 2500,
    "unit_price": 168.0,
    "order_date": "2026-02-01",
    "promised_date": "2026-03-20",
    "status": "delayed",
    "pct_complete": 74,
    "completed": 1850,
    "quality_passed": 1847,
    "in_production": 350,
    "queued": 300,
    "daily_output_before": 250,
    "daily_output_after": 325
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
    "unit_price": 12450.0,
    "order_date": "2026-01-15",
    "promised_date": "2026-04-10",
    "status": "in_production",
    "pct_complete": 45
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
    "unit_price": 42.5,
    "order_date": "2026-02-10",
    "promised_date": "2026-03-15",
    "status": "shipped",
    "pct_complete": 100
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

## Delay root cause, dates, duration, recovery actions with costs, compensation, and timeline

Canonical source constant: `DELAY_REASONS`.

```json
{
  "ORD-7810": {
    "supplier": "Midwest Casting (aluminum)",
    "reason": "Supplier delay: aluminum casting equipment failure + force majeure",
    "original_date": "2026-03-20",
    "revised_date": "2026-03-23",
    "initial_delay_days": 7,
    "days_delayed": 3,
    "recovery_actions": [
      [
        "Alternative supplier",
        "Secured material",
        "$12K premium",
        12000
      ],
      [
        "Weekend shifts",
        "+150 units",
        "$18K overtime",
        18000
      ],
      [
        "Air freight (first 500 units)",
        "2-day delivery",
        "$24K (we absorb)",
        24000
      ],
      [
        "Daily output increase",
        "+75 units/day",
        "Existing capacity",
        0
      ]
    ],
    "compensation_pct": 2,
    "compensation_extras": [
      "Priority scheduling on next order",
      "Dedicated quality liaison"
    ],
    "timeline": [
      [
        "Day 1-2",
        "Complete remaining 650 units"
      ],
      [
        "Day 3",
        "Final quality inspection"
      ],
      [
        "Day 4",
        "Packaging complete"
      ],
      [
        "Day 5-6",
        "Expedited shipping"
      ]
    ]
  },
  "ORD-7813": {
    "supplier": "Bar stock mill (alloy steel)",
    "reason": "Raw material shortage -- alloy steel bar stock delayed from supplier",
    "original_date": "2026-03-28",
    "revised_date": "2026-04-08",
    "initial_delay_days": 11,
    "days_delayed": 11,
    "recovery_actions": [
      [
        "Alternate supplier qualified",
        "First shipment arriving 2026-03-19",
        "$6.2K premium",
        6200
      ],
      [
        "Weekend overtime shifts for CNC cell",
        "+80 units/week",
        "$8K overtime",
        8000
      ],
      [
        "Partial shipment",
        "200 units by 2026-03-28",
        "Existing freight",
        0
      ]
    ],
    "compensation_pct": 0,
    "compensation_extras": [
      "Account manager call to agree the partial shipment"
    ],
    "timeline": [
      [
        "Week 1",
        "Alternate supplier material received"
      ],
      [
        "Week 2",
        "Partial shipment of 200 units"
      ],
      [
        "Week 3",
        "Remaining 400 units complete and shipped"
      ]
    ]
  }
}
```

## Account ownership, escalation, CC list, channels, follow-up call, tier, and response window

Canonical source constant: `CUSTOMER_CONTACTS`.

```json
{
  "E-Cars Corp": {
    "account_manager": "Sarah Lin",
    "escalation_contact": "Tom Bradley, Plant Manager",
    "cc": [
      "Tom Bradley (Plant Manager)",
      "Sarah Chen (Quality)",
      "Logistics team"
    ],
    "preferred_channel": "email",
    "channels": [
      "Email",
      "EDI 856 ASN",
      "Supplier portal",
      "Phone call"
    ],
    "follow_up_call": "Today 2 PM EST",
    "customer_tier": "Strategic",
    "sla_response_hours": 4
  },
  "Ironridge Equipment Co.": {
    "account_manager": "Robert Kim",
    "escalation_contact": "VP Supply Chain",
    "cc": [
      "VP Supply Chain"
    ],
    "preferred_channel": "EDI",
    "channels": [
      "EDI 856 ASN",
      "Email"
    ],
    "follow_up_call": "Weekly status call",
    "customer_tier": "Strategic",
    "sla_response_hours": 8
  },
  "Voltline Motors": {
    "account_manager": "Sarah Lin",
    "escalation_contact": "Logistics Director",
    "cc": [
      "Logistics Director"
    ],
    "preferred_channel": "portal",
    "channels": [
      "Supplier portal",
      "Email"
    ],
    "follow_up_call": "On request",
    "customer_tier": "Priority",
    "sla_response_hours": 2
  },
  "Greenfield Agri Machines": {
    "account_manager": "Robert Kim",
    "escalation_contact": "Procurement Director",
    "cc": [
      "Procurement Director"
    ],
    "preferred_channel": "email",
    "channels": [
      "Email",
      "Phone call"
    ],
    "follow_up_call": "Tomorrow 10 AM CST",
    "customer_tier": "Priority",
    "sla_response_hours": 4
  }
}
```

## Quality assurance and validation plan

Canonical source constant: `QUALITY_PLANS`.

```json
{
  "ORD-7810": {
    "incoming_material": [
      "100% dimensional inspection",
      "Metallurgical testing (batch samples)",
      "Hardness verification",
      "Chemical composition analysis",
      "Certification: material test reports provided"
    ],
    "production": [
      "In-process inspection: every 50 units",
      "Statistical process control (SPC) active",
      "Coordinate measuring machine (CMM): 10% sample",
      "Visual inspection: 100%"
    ],
    "final_validation": [
      "Functional testing: 100%",
      "Dimensional report: full first article",
      "Surface finish verification",
      "Packaging integrity check",
      "Quality documentation: Certificate of Conformance included"
    ],
    "customer_requirements": [
      "PPAP Level 3 maintained",
      "Q1 supplier rating protected",
      "Advanced quality planning review: complete"
    ],
    "yield_target_pct": 99.5
  }
}
```

## Customer account performance, delay management, and lessons learned

Canonical source constant: `ACCOUNT_METRICS`.

```json
{
  "E-Cars Corp": {
    "orders_12m": 47,
    "on_time_delivery_pct": 96.2,
    "quality_ppm": 185,
    "supplier_rating": "Q1 (top tier)",
    "annual_revenue": 14200000,
    "avg_delay_communication": "<4 hours",
    "recovery_success_pct": 94,
    "retention_after_delays_pct": 97,
    "lessons_learned": [
      "Supplier diversification accelerated",
      "Safety stock policy updated",
      "Communication template refined",
      "Recovery playbook enhanced"
    ]
  }
}
```

Fixed reference date: `2026-03-17`; default order: `ORD-7810` (E-Cars Corp PO #F2024-3847).

## Record-use boundary

Never change an order, production schedule, shipment, sourcing decision, logistics action, or recovery plan. Never send email, EDI, portal, Teams, or any other customer communication. An approved communication tool and authorized sender are required.

All exact values in this file remain synthetic pilot evidence. Production decisions
require fresh data from approved systems, identity and authorization controls, and
review by the accountable human owner.
