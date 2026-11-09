# Supply Chain Disruption Alert Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/retail_cpg_stacks/supply_chain_disruption_alert_stack/supply_chain_disruption_alert_agent.py`
- Captured source SHA-256: `6f7e8aac2c1b221a240c9bd9c65301f3207f382c038fcd1de21eb709935ffbdd`
- Locked case file: `tests/demo_cases/supply-chain-disruption-alert.json`
- Locked case SHA-256: `7848d9ec4ffb7e0cfb177e711f169ae07d7874b072dafa9e8ed7128afe0d41ea`
- Strict isolation: `true`

## Record index

- `SUPPLY_ROUTES`
- `DISRUPTION_EVENTS`
- `RISK_SCORES`
- `MITIGATION_PLAYBOOKS`
- `ALTERNATIVE_SUPPLIERS`
- `DC_INCIDENT`
- `NORTHWEST_STORES`
- `AFFECTED_CATEGORIES`
- `EMERGENCY_OPTIONS`
- `EXPANSION`
- `TRANSFER_PLAN`
- `SHIPMENT_STATUS`
- `DC_RECOVERY`
- `BACKLOG`
- `PREVENTION`
- `RESPONSE_PERFORMANCE`
- `LESSONS_LEARNED`

## SUPPLY_ROUTES

```json
{
  "RT-APAC-01": {
    "name": "Asia-Pacific Primary",
    "origin": "Shenzhen, China",
    "destination": "Los Angeles, CA",
    "transport_mode": "ocean_freight",
    "transit_days": 18,
    "carriers": [
      "COSCO Shipping",
      "Evergreen Marine"
    ],
    "annual_volume_teu": 4800,
    "annual_value_usd": 28500000.0,
    "categories": [
      "Electronics",
      "Accessories"
    ],
    "current_status": "disrupted",
    "reliability_score": 0.82
  },
  "RT-EURO-01": {
    "name": "European Apparel Route",
    "origin": "Porto, Portugal",
    "destination": "Newark, NJ",
    "transport_mode": "ocean_freight",
    "transit_days": 12,
    "carriers": [
      "Maersk Line",
      "MSC"
    ],
    "annual_volume_teu": 2200,
    "annual_value_usd": 15800000.0,
    "categories": [
      "Apparel"
    ],
    "current_status": "at_risk",
    "reliability_score": 0.91
  },
  "RT-DOMESTIC-01": {
    "name": "West Coast to Midwest",
    "origin": "Los Angeles, CA",
    "destination": "Chicago, IL",
    "transport_mode": "intermodal_rail",
    "transit_days": 4,
    "carriers": [
      "Union Pacific",
      "BNSF Railway"
    ],
    "annual_volume_teu": 6500,
    "annual_value_usd": 42000000.0,
    "categories": [
      "Electronics",
      "Accessories",
      "Apparel",
      "Footwear"
    ],
    "current_status": "normal",
    "reliability_score": 0.95
  },
  "RT-LATAM-01": {
    "name": "Central America Footwear",
    "origin": "Leon, Mexico",
    "destination": "Dallas, TX",
    "transport_mode": "trucking",
    "transit_days": 3,
    "carriers": [
      "J.B. Hunt",
      "Werner Enterprises"
    ],
    "annual_volume_teu": 1800,
    "annual_value_usd": 12400000.0,
    "categories": [
      "Footwear"
    ],
    "current_status": "normal",
    "reliability_score": 0.93
  },
  "RT-SEASIA-01": {
    "name": "Southeast Asia Textiles",
    "origin": "Ho Chi Minh City, Vietnam",
    "destination": "Savannah, GA",
    "transport_mode": "ocean_freight",
    "transit_days": 22,
    "carriers": [
      "Yang Ming",
      "ONE Line"
    ],
    "annual_volume_teu": 3100,
    "annual_value_usd": 19200000.0,
    "categories": [
      "Apparel",
      "Home"
    ],
    "current_status": "disrupted",
    "reliability_score": 0.78
  }
}
```

## DISRUPTION_EVENTS

```json
{
  "DISR-001": {
    "title": "Port Congestion — Los Angeles/Long Beach",
    "type": "port_congestion",
    "severity": "high",
    "affected_routes": [
      "RT-APAC-01"
    ],
    "start_date": "2026-03-05",
    "estimated_resolution": "2026-03-28",
    "delay_days": 8,
    "affected_skus": [
      "SKU-1002",
      "SKU-1004",
      "SKU-1006",
      "SKU-1008"
    ],
    "estimated_revenue_impact": 2150000.0,
    "description": "Severe vessel queue at LA/LB ports due to labor slowdown and equipment shortages. Average vessel wait time is 6 days.",
    "status": "active"
  },
  "DISR-002": {
    "title": "Typhoon Disruption — South China Sea",
    "type": "weather_event",
    "severity": "critical",
    "affected_routes": [
      "RT-APAC-01",
      "RT-SEASIA-01"
    ],
    "start_date": "2026-03-10",
    "estimated_resolution": "2026-03-20",
    "delay_days": 12,
    "affected_skus": [
      "SKU-1002",
      "SKU-1003",
      "SKU-1004",
      "SKU-1006",
      "SKU-1008",
      "SKU-1010"
    ],
    "estimated_revenue_impact": 3800000.0,
    "description": "Typhoon Mirinae forcing rerouting of vessels through northern Pacific corridor. Multiple sailings cancelled or delayed.",
    "status": "active"
  },
  "DISR-003": {
    "title": "EU Customs Regulation Change",
    "type": "regulatory",
    "severity": "medium",
    "affected_routes": [
      "RT-EURO-01"
    ],
    "start_date": "2026-03-01",
    "estimated_resolution": "2026-04-15",
    "delay_days": 5,
    "affected_skus": [
      "SKU-1001",
      "SKU-1003"
    ],
    "estimated_revenue_impact": 720000.0,
    "description": "New EU sustainability documentation requirements adding processing time at origin. Additional compliance certificates needed for textiles.",
    "status": "active"
  }
}
```

## RISK_SCORES

```json
{
  "RT-APAC-01": {
    "overall_risk": 0.78,
    "geopolitical": 0.65,
    "weather": 0.82,
    "infrastructure": 0.7,
    "labor": 0.75,
    "regulatory": 0.4,
    "financial": 0.35
  },
  "RT-EURO-01": {
    "overall_risk": 0.45,
    "geopolitical": 0.3,
    "weather": 0.2,
    "infrastructure": 0.25,
    "labor": 0.35,
    "regulatory": 0.72,
    "financial": 0.28
  },
  "RT-DOMESTIC-01": {
    "overall_risk": 0.22,
    "geopolitical": 0.05,
    "weather": 0.3,
    "infrastructure": 0.2,
    "labor": 0.25,
    "regulatory": 0.1,
    "financial": 0.15
  },
  "RT-LATAM-01": {
    "overall_risk": 0.35,
    "geopolitical": 0.25,
    "weather": 0.15,
    "infrastructure": 0.4,
    "labor": 0.3,
    "regulatory": 0.45,
    "financial": 0.32
  },
  "RT-SEASIA-01": {
    "overall_risk": 0.72,
    "geopolitical": 0.5,
    "weather": 0.85,
    "infrastructure": 0.55,
    "labor": 0.4,
    "regulatory": 0.48,
    "financial": 0.3
  }
}
```

## MITIGATION_PLAYBOOKS

```json
{
  "port_congestion": {
    "label": "Port Congestion Mitigation",
    "immediate_actions": [
      "Divert eligible shipments to alternate ports (Oakland, Seattle-Tacoma)",
      "Activate premium drayage contracts for priority container retrieval",
      "Convert ocean shipments under 2 TEU to air freight for critical SKUs"
    ],
    "short_term_actions": [
      "Increase safety stock at distribution centers by 20%",
      "Negotiate priority berthing with carrier partners",
      "Activate cross-dock bypass for pre-cleared containers"
    ],
    "long_term_actions": [
      "Diversify port-of-entry strategy across West and East Coast",
      "Invest in inland port relationships for rail-direct receiving",
      "Develop dual-source contracts for top-volume categories"
    ],
    "estimated_mitigation_cost": 340000.0,
    "risk_reduction_pct": 45
  },
  "weather_event": {
    "label": "Weather Event Mitigation",
    "immediate_actions": [
      "Activate emergency inventory reserves at regional warehouses",
      "Reroute in-transit vessels through safe corridors",
      "Expedite air freight for high-priority SKUs with less than 7 days supply"
    ],
    "short_term_actions": [
      "Shift demand to in-stock alternative products via merchandising",
      "Enable backorder with guaranteed delivery dates for affected items",
      "Communicate proactively with B2B customers on revised timelines"
    ],
    "long_term_actions": [
      "Integrate real-time weather monitoring into planning systems",
      "Build seasonal safety stock buffers for typhoon/hurricane seasons",
      "Qualify backup suppliers in geographically diverse regions"
    ],
    "estimated_mitigation_cost": 520000.0,
    "risk_reduction_pct": 55
  },
  "regulatory": {
    "label": "Regulatory Change Mitigation",
    "immediate_actions": [
      "Engage customs broker to prepare updated documentation templates",
      "Pre-certify next 3 shipments with new compliance requirements",
      "Brief all origin-side partners on updated export procedures"
    ],
    "short_term_actions": [
      "Conduct compliance audit of all active POs on affected routes",
      "Update vendor manual with new regulatory requirements",
      "Schedule training session for procurement team"
    ],
    "long_term_actions": [
      "Subscribe to regulatory change monitoring service",
      "Build compliance buffer time into standard lead times",
      "Develop relationships with in-country compliance consultants"
    ],
    "estimated_mitigation_cost": 85000.0,
    "risk_reduction_pct": 70
  }
}
```

## ALTERNATIVE_SUPPLIERS

```json
{
  "Electronics": [
    {
      "name": "TechSource Taiwan",
      "location": "Taipei, Taiwan",
      "lead_time_days": 21,
      "quality_rating": 4.5,
      "capacity_units_monthly": 15000,
      "price_premium_pct": 8.0,
      "certifications": [
        "ISO 9001",
        "ISO 14001"
      ],
      "min_order_qty": 500
    },
    {
      "name": "KoreanTech Partners",
      "location": "Incheon, South Korea",
      "lead_time_days": 19,
      "quality_rating": 4.7,
      "capacity_units_monthly": 10000,
      "price_premium_pct": 12.0,
      "certifications": [
        "ISO 9001",
        "IATF 16949"
      ],
      "min_order_qty": 300
    }
  ],
  "Apparel": [
    {
      "name": "TurkTex Industries",
      "location": "Istanbul, Turkey",
      "lead_time_days": 16,
      "quality_rating": 4.3,
      "capacity_units_monthly": 25000,
      "price_premium_pct": 5.0,
      "certifications": [
        "GOTS",
        "OEKO-TEX"
      ],
      "min_order_qty": 1000
    },
    {
      "name": "BanglaStitch Ltd",
      "location": "Dhaka, Bangladesh",
      "lead_time_days": 25,
      "quality_rating": 4.0,
      "capacity_units_monthly": 40000,
      "price_premium_pct": -3.0,
      "certifications": [
        "WRAP",
        "BSCI"
      ],
      "min_order_qty": 2000
    }
  ],
  "Footwear": [
    {
      "name": "IndoSole Manufacturing",
      "location": "Tangerang, Indonesia",
      "lead_time_days": 28,
      "quality_rating": 4.2,
      "capacity_units_monthly": 18000,
      "price_premium_pct": 2.0,
      "certifications": [
        "ISO 9001",
        "SA8000"
      ],
      "min_order_qty": 800
    }
  ],
  "Accessories": [
    {
      "name": "IndiaGlobal Accessories",
      "location": "Mumbai, India",
      "lead_time_days": 24,
      "quality_rating": 4.1,
      "capacity_units_monthly": 30000,
      "price_premium_pct": -5.0,
      "certifications": [
        "ISO 9001"
      ],
      "min_order_qty": 1500
    },
    {
      "name": "MediterraneanCraft Co",
      "location": "Florence, Italy",
      "lead_time_days": 14,
      "quality_rating": 4.8,
      "capacity_units_monthly": 5000,
      "price_premium_pct": 25.0,
      "certifications": [
        "ISO 9001",
        "Made in Italy"
      ],
      "min_order_qty": 200
    }
  ],
  "Home": [
    {
      "name": "ThaiHome Products",
      "location": "Bangkok, Thailand",
      "lead_time_days": 20,
      "quality_rating": 4.3,
      "capacity_units_monthly": 12000,
      "price_premium_pct": 4.0,
      "certifications": [
        "ISO 9001",
        "FSC"
      ],
      "min_order_qty": 600
    }
  ]
}
```

## DC_INCIDENT

```json
{
  "id": "DISR-PDX-01",
  "dc": "Portland DC",
  "region": "Northwest",
  "root_cause": "Equipment failure (main conveyor)",
  "backup_days": 3,
  "stores_in_network": 47,
  "lost_revenue_per_week": 84300,
  "complaints": 37,
  "complaint_increase_pct": 280,
  "social": "social media mentions spiking"
}
```

## NORTHWEST_STORES

```json
[
  {
    "store": "Seattle Flagship",
    "stockout_pct": 47
  },
  {
    "store": "Portland South",
    "stockout_pct": 31
  },
  {
    "store": "Tacoma Mall",
    "stockout_pct": 29
  },
  {
    "store": "Bellevue Square",
    "stockout_pct": 27
  },
  {
    "store": "Olympia Center",
    "stockout_pct": 24
  },
  {
    "store": "Spokane Valley",
    "stockout_pct": 22
  },
  {
    "store": "Portland Pearl",
    "stockout_pct": 18
  },
  {
    "store": "Eugene Valley",
    "stockout_pct": 16
  },
  {
    "store": "Salem Center",
    "stockout_pct": 15
  },
  {
    "store": "Everett Commons",
    "stockout_pct": 14
  },
  {
    "store": "Vancouver Plaza",
    "stockout_pct": 12
  },
  {
    "store": "Boise Towne",
    "stockout_pct": 11
  }
]
```

## AFFECTED_CATEGORIES

```json
{
  "Electronics": 42,
  "Apparel": 38,
  "Home goods": 31,
  "Sporting": 32
}
```

## EMERGENCY_OPTIONS

```json
[
  {
    "option": "A",
    "name": "Denver DC Emergency Transfer",
    "timeline": "36 hours to Seattle",
    "coverage": "Top 80 priority SKUs delivered",
    "cost": 15600,
    "cost_note": "truck + handling",
    "recovery": 47000,
    "window": "5-day window",
    "additional_loss": 0
  },
  {
    "option": "B",
    "name": "Partial Fill + Wait",
    "timeline": "2 days for Portland recovery",
    "coverage": "Only 40% of SKUs restored",
    "cost": 0,
    "cost_note": "no added freight",
    "recovery": 0,
    "window": "none",
    "additional_loss": 127000
  }
]
```

## EXPANSION

```json
{
  "stores": [
    "Portland South",
    "Tacoma Mall",
    "Bellevue Square",
    "Olympia Center",
    "Spokane Valley"
  ],
  "cost": 8900,
  "recovery": 31000,
  "skus_per_store": 60,
  "arrival": "Saturday morning",
  "focus": "highest velocity items"
}
```

## TRANSFER_PLAN

```json
{
  "source_dc": "Denver DC",
  "dc_contact": "Lisa Park, Denver DC operations manager",
  "primary_store": "Seattle Flagship",
  "primary_skus": 80,
  "primary_focus": "electronics priority",
  "departure": "Tonight 6 PM",
  "arrival": "Friday 10 AM",
  "coordination": [
    "Teams notice to the 6 store managers",
    "Receiving staff schedule for Friday and Saturday",
    "Restocking plans for store tablets",
    "Customer SMS notification for back-in-stock items"
  ]
}
```

## SHIPMENT_STATUS

```json
{
  "truck": "Denver truck",
  "departed": "6:04 PM",
  "eta": "Friday 9:47 AM",
  "status": "On schedule"
}
```

## DC_RECOVERY

```json
[
  {
    "action": "Conveyor repair",
    "status": "In progress",
    "complete_by": "Thursday 8 PM"
  },
  {
    "action": "Backlog processing",
    "status": "Staged",
    "complete_by": "Friday 6 AM"
  },
  {
    "action": "Normal ops resume",
    "status": "Planned",
    "complete_by": "Friday noon"
  }
]
```

## BACKLOG

```json
{
  "pending_orders": 340,
  "priority": "Seattle + affected stores first",
  "full_clearance": "Saturday end of day"
}
```

## PREVENTION

```json
{
  "item": "Backup conveyor system",
  "investment": 145000,
  "install_hours": 48,
  "three_year_avoided_losses": 340000
}
```

## RESPONSE_PERFORMANCE

```json
{
  "detection_to_action_minutes": 47,
  "alternative_dc_hours": 36,
  "days_to_95pct_inventory": 3,
  "csat": 4.2,
  "alert_tuning_minutes_saved": 18
}
```

## LESSONS_LEARNED

```json
[
  "Backup conveyor needed ($145K)",
  "Multi-DC sourcing rules updated",
  "Monitoring alerts tuned (reduce response time by 18 minutes)"
]
```

## Demo walkthrough (video scenario)

A conveyor failure at the Portland DC (`DISR-PDX-01`) causes cascading stockouts across 12 Northwest stores of a
47-store retailer. Every walkthrough operation has demo defaults; no identifier is needed.

| Turn | User prompt | Operation | Key values |
|---|---|---|---|
| 1 | I'm seeing unusual inventory movement at our Northwest stores. Can you help me understand what's happening? | `root_cause_analysis` | Portland DC delay 3-day backup (Active); Seattle Flagship 47% stockout (Critical); SKUs affected 143 products (High); Lost revenue $84,300/week (Escalating); Electronics 42, Apparel 38, Home goods 31, Sporting 32; 37 complaints (up 280% vs baseline) |
| 2 | What are our emergency options and costs? | `emergency_options` | Option A Denver DC Emergency Transfer: 36 hours to Seattle, top 80 priority SKUs, $15,600, $47,000 recovery (5-day window), ROI 3:1; Option B Partial Fill + Wait: 2 days, 40% of SKUs, $0, $127,000 additional loss; recommended A + 5 additional stores for $8,900 |
| 3 | Approved. Execute both Seattle and the 5 additional stores. | `transfer_plan` | Plan ready to release (nothing dispatched); Denver DC contact Lisa Park; Seattle Flagship departs tonight 6 PM, arrives Friday 10 AM, 80 SKUs; Portland South, Tacoma Mall, Bellevue Square, Olympia Center, Spokane Valley arrive Saturday morning, 60 SKUs each; coordination drafts not sent; investment $24,500, recovery $78,000 |
| 4 | Activate tracking and show me the Portland DC recovery plan. | `recovery_plan` | Tracking snapshot: departed 6:04 PM, ETA Friday 9:47 AM, on schedule; Conveyor repair (In progress, Thursday 8 PM); Backlog processing (Staged, Friday 6 AM); Normal ops resume (Planned, Friday noon); 340 pending orders, full clearance Saturday end of day; backup conveyor $145K, 48-hour install |
| 5 | Create the executive report with financial impact. | `incident_report` | Revenue at risk $84,300; response cost $24,500; recovered $78,000; net $53,500; 47 minutes detection to action; 36 hours; 3 days to 95% inventory; CSAT 4.2/5.0; $340K 3-year avoided losses vs $145K |
| 6 | Distribute the report and summarize what we accomplished. | `incident_summary` | Crisis Response Summary, package ready to distribute (not sent); 6 stores; $24.5K; $53,500 net; monitoring on all 47 stores; Portland DC back online Friday noon |
## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
