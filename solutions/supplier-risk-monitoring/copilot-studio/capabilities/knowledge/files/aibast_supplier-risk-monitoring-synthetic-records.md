# Supply Risk Monitoring Agent — Complete Synthetic Source Records

> **SYNTHETIC PILOT DATA.** This file is a complete Markdown rendering of the
> deterministic source constants used by the local agent and canonical transcript
> capture. Every identifier, person-like name, organization, measurement, score,
> quantity, amount, date, schedule, status, and relationship is fictional. No live
> customer or third-party system was queried.

## Source fidelity contract

- Deterministic source: `agents/@aibast-agents-library/manufacturing_stacks/supplier_risk_monitoring_stack/supplier_risk_monitoring_agent.py`
- Canonical transcript: `solutions/supplier-risk-monitoring/evals/transcripts.json`
- Locked cases: `tests/demo_cases/supplier-risk-monitoring.json`
- Values below are copied exactly from source constants. Do not recalculate, enrich,
  browse for, or substitute them when reproducing the pilot.

## Supplier master, spend, dimension scores, risk, and tier

Canonical source constant: `SUPPLIERS`.

```json
{
  "SUP-101": {
    "name": "TechnoCore Semiconductor (Taiwan)",
    "category": "Microcontrollers",
    "region": "Asia-Pacific",
    "country": "Taiwan",
    "annual_spend": 4800000,
    "quality_score": 82,
    "delivery_score": 74,
    "financial_score": 68,
    "geopolitical_score": 42,
    "overall_risk": 8.2,
    "tier": 1
  },
  "SUP-102": {
    "name": "Shenzhen Electronics Co.",
    "category": "Passive Components",
    "region": "Asia-Pacific",
    "country": "China",
    "annual_spend": 3200000,
    "quality_score": 71,
    "delivery_score": 78,
    "financial_score": 55,
    "geopolitical_score": 58,
    "overall_risk": 6.5,
    "tier": 1
  },
  "SUP-103": {
    "name": "Malaysia Semicon Pte Ltd",
    "category": "Power ICs",
    "region": "Asia-Pacific",
    "country": "Malaysia",
    "annual_spend": 2100000,
    "quality_score": 91,
    "delivery_score": 88,
    "financial_score": 84,
    "geopolitical_score": 82,
    "overall_risk": 3.8,
    "tier": 1
  },
  "SUP-104": {
    "name": "Midwest Casting & Forge",
    "category": "Aluminum Castings",
    "region": "North America",
    "country": "USA",
    "annual_spend": 5600000,
    "quality_score": 88,
    "delivery_score": 65,
    "financial_score": 72,
    "geopolitical_score": 95,
    "overall_risk": 4.9,
    "tier": 1
  },
  "SUP-105": {
    "name": "Rheinmetall Precision GmbH",
    "category": "CNC Machined Parts",
    "region": "Europe",
    "country": "Germany",
    "annual_spend": 3800000,
    "quality_score": 95,
    "delivery_score": 91,
    "financial_score": 89,
    "geopolitical_score": 88,
    "overall_risk": 2.4,
    "tier": 2
  }
}
```

## Exact recorded synthetic incidents

Canonical source constant: `RECENT_INCIDENTS`.

```json
[
  {
    "supplier_id": "SUP-101",
    "date": "2026-02-28",
    "severity": "HIGH",
    "description": "Cross-strait military exercises caused 5-day port closure; delayed 3 shipments"
  },
  {
    "supplier_id": "SUP-102",
    "date": "2026-03-05",
    "severity": "MEDIUM",
    "description": "Quality excursion: capacitor lot C-4410 failed incoming inspection (2.3% defect rate vs 0.5% spec)"
  },
  {
    "supplier_id": "SUP-104",
    "date": "2026-03-10",
    "severity": "HIGH",
    "description": "Equipment failure at foundry; force majeure declared, 7-day production halt"
  },
  {
    "supplier_id": "SUP-102",
    "date": "2026-03-12",
    "severity": "LOW",
    "description": "New export control regulations announced; compliance review underway"
  }
]
```

## Backup supplier names, lead times, qualification states, and premiums

Canonical source constant: `BACKUP_SUPPLIERS`.

```json
{
  "SUP-101": [
    {
      "name": "Samsung Foundry (Korea)",
      "lead_time_weeks": 12,
      "qual_status": "In Progress",
      "est_cost_premium_pct": 8
    },
    {
      "name": "GlobalFoundries (USA)",
      "lead_time_weeks": 16,
      "qual_status": "Not Started",
      "est_cost_premium_pct": 15
    }
  ],
  "SUP-102": [
    {
      "name": "Murata Electronics (Japan)",
      "lead_time_weeks": 6,
      "qual_status": "Qualified",
      "est_cost_premium_pct": 5
    },
    {
      "name": "Vishay Intertechnology (USA)",
      "lead_time_weeks": 4,
      "qual_status": "Qualified",
      "est_cost_premium_pct": 12
    }
  ],
  "SUP-104": [
    {
      "name": "Alcoa Precision Castings (USA)",
      "lead_time_weeks": 8,
      "qual_status": "In Progress",
      "est_cost_premium_pct": 6
    }
  ]
}
```

## Record-use boundary

Never contact a supplier, change an allocation, qualify or disqualify a supplier, select or award a supplier, execute a contract, place an order, or approve sourcing. Authorized procurement owners must use approved procurement and supplier-management tools for any action.

All exact values in this file remain synthetic pilot evidence. Production decisions
require fresh data from approved systems, identity and authorization controls, and
review by the accountable human owner.
