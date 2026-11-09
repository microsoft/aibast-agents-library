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

## Supplier master, supply share, dimension scores, risk, concerns, and strengths

Canonical source constant: `SUPPLIERS`.

Risk level labels: HIGH at or above 7.0, MEDIUM at or above 5.0, LOW below 5.0. The semiconductor review scope is SUP-101 (Taiwan, 40% of MCU supply), SUP-102 (China, 35% of passive components) and SUP-103 (Malaysia, 25% of power ICs).

```json
{
  "SUP-101": {
    "name": "TechnoCore Semiconductor (Taiwan)",
    "short_name": "TechnoCore",
    "assessment_name": "TechnoCore Taiwan",
    "category": "Microcontrollers",
    "region": "Asia-Pacific",
    "country": "Taiwan",
    "scope": "semiconductor",
    "share_pct": 40,
    "supply_label": "MCU supply",
    "impact_label": "MCU supply",
    "annual_spend": 4800000,
    "quality_score": 82,
    "delivery_score": 74,
    "financial_score": 68,
    "geopolitical_score": 42,
    "overall_risk": 8.2,
    "tier": 1,
    "concerns": [
      "Cross-strait geopolitical tensions",
      "Single facility concentration"
    ],
    "recent_event": "Military exercises within 50nm",
    "financial_note": "",
    "quality_note": "",
    "strengths": [],
    "capacity_vs_demand_pct": 0
  },
  "SUP-102": {
    "name": "Shenzhen Electronics Co.",
    "short_name": "Shenzhen Electronics",
    "assessment_name": "Shenzhen Electronics",
    "category": "Passive Components",
    "region": "Asia-Pacific",
    "country": "China",
    "scope": "semiconductor",
    "share_pct": 35,
    "supply_label": "passive components",
    "impact_label": "passives",
    "annual_spend": 3200000,
    "quality_score": 71,
    "delivery_score": 78,
    "financial_score": 55,
    "geopolitical_score": 58,
    "overall_risk": 6.5,
    "tier": 1,
    "concerns": [
      "Trade restrictions",
      "IP protection"
    ],
    "recent_event": "New export control regulations announced",
    "debt_to_equity_change_pct": 35,
    "defect_rate_pct": 2.3,
    "defect_rate_prev_pct": 1.8,
    "financial_note": "Debt-to-equity +35% (stressed)",
    "quality_note": "Defect rate 2.3% (up from 1.8%)",
    "strengths": [],
    "capacity_vs_demand_pct": 0
  },
  "SUP-103": {
    "name": "Malaysia Semicon Pte Ltd",
    "short_name": "Malaysia Semicon",
    "assessment_name": "Malaysia Semicon",
    "category": "Power ICs",
    "region": "Asia-Pacific",
    "country": "Malaysia",
    "scope": "semiconductor",
    "share_pct": 25,
    "supply_label": "power ICs",
    "impact_label": "power ICs",
    "annual_spend": 2100000,
    "quality_score": 91,
    "delivery_score": 88,
    "financial_score": 84,
    "geopolitical_score": 82,
    "overall_risk": 3.8,
    "tier": 1,
    "concerns": [],
    "recent_event": "",
    "financial_note": "",
    "quality_note": "",
    "strengths": [
      "Political stability",
      "diversified base"
    ],
    "capacity_vs_demand_pct": 120
  },
  "SUP-104": {
    "name": "Midwest Casting & Forge",
    "short_name": "Midwest Casting",
    "assessment_name": "Midwest Casting",
    "category": "Aluminum Castings",
    "region": "North America",
    "country": "USA",
    "scope": "industrial",
    "share_pct": 0,
    "supply_label": "aluminum castings",
    "impact_label": "castings",
    "annual_spend": 5600000,
    "quality_score": 88,
    "delivery_score": 65,
    "financial_score": 72,
    "geopolitical_score": 95,
    "overall_risk": 4.9,
    "tier": 1,
    "concerns": [
      "Single foundry equipment reliability"
    ],
    "recent_event": "Force majeure declared after equipment failure",
    "financial_note": "",
    "quality_note": "",
    "strengths": [],
    "capacity_vs_demand_pct": 0
  },
  "SUP-105": {
    "name": "Rheinland Precision GmbH",
    "short_name": "Rheinland Precision",
    "assessment_name": "Rheinland Precision",
    "category": "CNC Machined Parts",
    "region": "Europe",
    "country": "Germany",
    "scope": "industrial",
    "share_pct": 0,
    "supply_label": "machined parts",
    "impact_label": "machined parts",
    "annual_spend": 3800000,
    "quality_score": 95,
    "delivery_score": 91,
    "financial_score": 89,
    "geopolitical_score": 88,
    "overall_risk": 2.4,
    "tier": 2,
    "concerns": [],
    "recent_event": "",
    "financial_note": "",
    "quality_note": "",
    "strengths": [
      "Stable delivery",
      "high quality"
    ],
    "capacity_vs_demand_pct": 0
  }
}
```

## Risk categories monitored

Canonical source constant: `RISK_CATEGORIES`.

```json
[
  "Geopolitical stability",
  "Financial health",
  "Operational capacity",
  "Quality metrics",
  "Logistics reliability"
]
```

## Exact recorded synthetic incidents

Canonical source constant: `RECENT_INCIDENTS`.

```json
[
  {
    "supplier_id": "SUP-101",
    "date": "2026-02-28",
    "severity": "HIGH",
    "description": "Military exercises within 50nm of the facility; 5-day port closure delayed 3 shipments"
  },
  {
    "supplier_id": "SUP-102",
    "date": "2026-03-05",
    "severity": "MEDIUM",
    "description": "Quality excursion: capacitor lot C-4410 at 2.3% defect rate (up from 1.8%; spec 0.5%)"
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

All backup supplier names are fictional. The Korean backup's 26-week lead time is the 6-month qualification shown in the mitigation plan.

```json
{
  "SUP-101": [
    {
      "name": "Hanseong Foundry (Korea)",
      "lead_time_weeks": 26,
      "qual_status": "In Progress",
      "est_cost_premium_pct": 8
    },
    {
      "name": "Lakeside Foundry (USA)",
      "lead_time_weeks": 16,
      "qual_status": "Not Started",
      "est_cost_premium_pct": 15
    }
  ],
  "SUP-102": [
    {
      "name": "Kansai Passive Components (Japan)",
      "lead_time_weeks": 6,
      "qual_status": "In Qualification",
      "est_cost_premium_pct": 5
    },
    {
      "name": "Keystone Passives (USA)",
      "lead_time_weeks": 4,
      "qual_status": "In Qualification",
      "est_cost_premium_pct": 12
    }
  ],
  "SUP-104": [
    {
      "name": "Great Lakes Precision Castings (USA)",
      "lead_time_weeks": 8,
      "qual_status": "In Progress",
      "est_cost_premium_pct": 6
    }
  ]
}
```

## Recommended mitigation plan per supplier

Canonical source constant: `MITIGATION_PLANS`.

Every action is a recommendation for authorized procurement approval; none is executed.

```json
{
  "SUP-101": {
    "stance": "HIGH PRIORITY",
    "heading": "Immediate (30 days)",
    "safety_stock_days": 30,
    "safety_stock_target_days": 45,
    "safety_stock_investment": 840000,
    "actions": [
      "Dual sourcing: Korean supplier qualification started",
      "Alternative qualified: 6 months",
      "Air freight contingency: $2.1M capacity to reserve"
    ]
  },
  "SUP-102": {
    "stance": "MONITOR CLOSELY",
    "heading": "Actions",
    "actions": [
      "Payment terms: Net-30 -> COD (protect exposure)",
      "Quality inspection: 100% incoming (was sampling)",
      "Contract updates: Stronger IP protections",
      "Backup identified: 2 suppliers in qualification"
    ]
  },
  "SUP-103": {
    "stance": "OPPORTUNITY",
    "heading": "Optimization",
    "actions": [
      "Volume increase: +20% (tier discount available)",
      "Strategic partnership discussions",
      "Co-development program for custom ICs"
    ]
  }
}
```

## Mitigation costs

Canonical source constant: `MITIGATION_COSTS`.

Total investment = $840,000 + $125,000 + $48,000 + $85,000 = $1,098,000 ($1.098M).

```json
[
  {
    "action": "Safety stock increase",
    "investment": 840000,
    "recurring": false,
    "benefit": "45 days buffer"
  },
  {
    "action": "Dual sourcing program",
    "investment": 125000,
    "recurring": false,
    "benefit": "Supply security"
  },
  {
    "action": "Enhanced inspection",
    "investment": 48000,
    "recurring": true,
    "benefit": "Quality protection"
  },
  {
    "action": "Alternative qualification",
    "investment": 85000,
    "recurring": false,
    "benefit": "Reduced dependency"
  }
]
```

## Risk exposure model

Canonical source constant: `RISK_EXPOSURE`.

Reduction = (12.4M - 4.3M) / 12.4M = 65%. Break-even probability = 1.098M / 12.4M = 8.85%, shown truncated to one decimal as 8.8%; 15% current probability is above break-even, so the case is favorable.

```json
{
  "current_exposure": 12400000,
  "after_mitigation": 4300000,
  "probability_now_pct": 15,
  "probability_after_pct": 4
}
```

## 12-month implementation roadmap

Canonical source constant: `ROADMAP`.

Phase 4 ends with the risk score target: <4.0 (from TechnoCore's 8.2).

```json
[
  {
    "phase": "Phase 1 (Months 1-3): Immediate Protection",
    "steps": [
      "Week 1: Increase TechnoCore orders (safety stock)",
      "Week 2: COD terms with Shenzhen Electronics",
      "Week 3: 100% inspection protocol starts",
      "Week 4: Korean supplier identification complete"
    ]
  },
  {
    "phase": "Phase 2 (Months 4-6): Qualification",
    "steps": [
      "Month 4: Korean supplier initial samples",
      "Month 5: Testing and validation",
      "Month 6: First production orders (10% volume)"
    ]
  },
  {
    "phase": "Phase 3 (Months 7-9): Optimization",
    "steps": [
      "Malaysia partnership negotiations",
      "Volume consolidation planning",
      "Contract updates completed"
    ]
  },
  {
    "phase": "Phase 4 (Months 10-12): Full Resilience",
    "steps": [
      "Dual sourcing: 60% Taiwan / 40% Korea",
      "Malaysia strategic partnership signed"
    ]
  }
]
```

## Recommended monitoring design

Canonical source constant: `MONITORING_DESIGN`.

A design only; no feed, alert, or automated action is activated by the agent.

```json
{
  "data_sources": [
    "Geopolitical: news wires, government advisories",
    "Financial: credit ratings, stock prices, filings",
    "Operational: supplier portals, IoT, certifications",
    "Logistics: shipping data, port congestion, weather",
    "Legal: sanctions lists, trade restrictions"
  ],
  "alert_thresholds": [
    "Critical: Immediate escalation to VP",
    "Warning: Daily digest to procurement",
    "Info: Weekly risk report"
  ],
  "automated_actions": [
    "Risk score >7.5: Trigger mitigation protocols",
    "Financial deterioration: Payment terms adjustment",
    "Quality issues: Inspection level increase",
    "Capacity concerns: Backup supplier activation"
  ],
  "success_metrics": [
    "Supply continuity: 99.7% (target: 99.5%)",
    "Risk-adjusted cost: -12% vs. reactive approach",
    "Early warning: 18 days average lead time"
  ]
}
```

## Record-use boundary

Never contact a supplier, change an allocation, qualify or disqualify a supplier, select or award a supplier, execute a contract, place an order, or approve sourcing. Authorized procurement owners must use approved procurement and supplier-management tools for any action.

All exact values in this file remain synthetic pilot evidence. Production decisions
require fresh data from approved systems, identity and authorization controls, and
review by the accountable human owner.
