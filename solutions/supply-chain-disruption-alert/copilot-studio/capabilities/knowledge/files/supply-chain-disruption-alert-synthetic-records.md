# Supply Chain Disruption Alert Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/retail_cpg_stacks/supply_chain_disruption_alert_stack/supply_chain_disruption_alert_agent.py`
- Captured source SHA-256: `ad921fdd2417b9bc9bacfa2bdf70998c150c615968f7ad0c32ae0b91e47531d1`
- Locked case file: `tests/demo_cases/supply-chain-disruption-alert.json`
- Locked case SHA-256: `5a8ef6d1b299867f259db1eaddf650a1d751fb2b512e696875ea95c237ca7595`
- Strict isolation: `true`

## Record index

- `SUPPLY_ROUTES`
- `DISRUPTION_EVENTS`
- `RISK_SCORES`
- `MITIGATION_PLAYBOOKS`
- `ALTERNATIVE_SUPPLIERS`

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

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
