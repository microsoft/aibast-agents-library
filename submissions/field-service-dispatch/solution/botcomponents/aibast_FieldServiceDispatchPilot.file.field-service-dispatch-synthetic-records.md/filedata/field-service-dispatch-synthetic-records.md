# Field Service Dispatch Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/field_service_dispatch_stack/field_service_dispatch_agent.py`
- Captured source SHA-256: `49452ef7f2a119bb099f29c595124ea33414a3bd50623ef1812f02dd0fd1a846`
- Locked case file: `tests/demo_cases/field-service-dispatch.json`
- Locked case SHA-256: `89bb00b273e151a78826533f6f455549f6727c1e8f6d6bd282426a271ce798f6`
- Strict isolation: `true`

## Record index

- `CREWS`
- `CERT_LABELS`
- `JOBS`
- `SCHEDULE_BASELINE`
- `OUTAGE`
- `LIVE_STATUS`
- `INCIDENT_REVIEW`
- `WORK_ORDERS`
- `MONTHLY_OPS`

## CREWS

```json
{
  "A-1": {
    "name": "Crew A-1 Marcus Chen",
    "lead": "Marcus Chen",
    "years": 12,
    "level": "Level 3",
    "truck": "#47",
    "certs": [
      "high_voltage",
      "underground_cable",
      "commercial_electrical"
    ],
    "status": "scheduled",
    "location": "North service yard",
    "route_miles": 42
  },
  "B-2": {
    "name": "Crew B-2 Priya Nair",
    "lead": "Priya Nair",
    "years": 9,
    "level": "Level 3",
    "truck": "#22",
    "certs": [
      "high_voltage",
      "meter_service"
    ],
    "status": "scheduled",
    "location": "East service yard",
    "route_miles": 38
  },
  "C-3": {
    "name": "Crew C-3 Diego Alvarez",
    "lead": "Diego Alvarez",
    "years": 7,
    "level": "Level 2",
    "truck": "#31",
    "certs": [
      "underground_cable",
      "high_voltage"
    ],
    "status": "scheduled",
    "location": "South service yard",
    "route_miles": 35
  },
  "D-4": {
    "name": "Crew D-4 Hannah Brooks",
    "lead": "Hannah Brooks",
    "years": 5,
    "level": "Level 2",
    "truck": "#18",
    "certs": [
      "meter_service",
      "commercial_electrical"
    ],
    "status": "scheduled",
    "location": "West service yard",
    "route_miles": 28
  },
  "E-7": {
    "name": "Crew E-7 Tom Okafor",
    "lead": "Tom Okafor",
    "years": 14,
    "level": "Level 3",
    "truck": "#7",
    "certs": [
      "high_voltage",
      "substation",
      "emergency_response"
    ],
    "status": "standby",
    "location": "Downtown staging area",
    "route_miles": 0
  },
  "F-8": {
    "name": "Crew F-8 Lena Park",
    "lead": "Lena Park",
    "years": 10,
    "level": "Level 3",
    "truck": "#8",
    "certs": [
      "high_voltage",
      "transformer_assessment"
    ],
    "status": "standby",
    "location": "2.4 mi from downtown",
    "route_miles": 0
  }
}
```

## CERT_LABELS

```json
{
  "high_voltage": "High-voltage certification",
  "underground_cable": "Underground cable certified",
  "commercial_electrical": "Commercial electrical license",
  "meter_service": "Meter service qualified",
  "substation": "Substation switching",
  "emergency_response": "Emergency response",
  "transformer_assessment": "Transformer assessment"
}
```

## JOBS

```json
[
  {
    "id": "J-101",
    "crew": "A-1",
    "stop": 1,
    "time": "7:00 AM",
    "location": "Oak Ridge Blvd",
    "job": "Transformer inspect",
    "hours": 1.5,
    "cert": "high_voltage",
    "fit": 100
  },
  {
    "id": "J-102",
    "crew": "A-1",
    "stop": 2,
    "time": "9:15 AM",
    "location": "Riverside Dr",
    "job": "Underground cable",
    "hours": 2.0,
    "cert": "underground_cable",
    "fit": 100
  },
  {
    "id": "J-103",
    "crew": "A-1",
    "stop": 3,
    "time": "12:00 PM",
    "location": "Commerce Pkwy",
    "job": "Meter upgrade",
    "hours": 1.5,
    "cert": "commercial_electrical",
    "fit": 100
  },
  {
    "id": "J-104",
    "crew": "A-1",
    "stop": 4,
    "time": "2:30 PM",
    "location": "Industrial Way",
    "job": "Switchgear maint",
    "hours": 1.0,
    "cert": "high_voltage",
    "fit": 100
  },
  {
    "id": "J-105",
    "crew": "B-2",
    "stop": 1,
    "time": "7:30 AM",
    "location": "Maple Ave",
    "job": "Pole transformer swap",
    "hours": 2.5,
    "cert": "high_voltage",
    "fit": 100
  },
  {
    "id": "J-106",
    "crew": "B-2",
    "stop": 2,
    "time": "10:30 AM",
    "location": "Harbor St",
    "job": "Smart meter install",
    "hours": 1.5,
    "cert": "meter_service",
    "fit": 95
  },
  {
    "id": "J-107",
    "crew": "B-2",
    "stop": 3,
    "time": "1:00 PM",
    "location": "Lakeview Dr",
    "job": "Service drop repair",
    "hours": 2.0,
    "cert": "high_voltage",
    "fit": 90
  },
  {
    "id": "J-108",
    "crew": "C-3",
    "stop": 1,
    "time": "7:30 AM",
    "location": "Elm St vault",
    "job": "Cable splice",
    "hours": 2.5,
    "cert": "underground_cable",
    "fit": 100
  },
  {
    "id": "J-109",
    "crew": "C-3",
    "stop": 2,
    "time": "10:45 AM",
    "location": "Park Plaza",
    "job": "Network protector test",
    "hours": 2.0,
    "cert": "high_voltage",
    "fit": 100
  },
  {
    "id": "J-110",
    "crew": "C-3",
    "stop": 3,
    "time": "1:30 PM",
    "location": "Union Sq",
    "job": "Vault inspection",
    "hours": 1.5,
    "cert": "underground_cable",
    "fit": 100
  },
  {
    "id": "J-111",
    "crew": "D-4",
    "stop": 1,
    "time": "8:00 AM",
    "location": "Westgate Mall",
    "job": "Commercial meter bank",
    "hours": 3.0,
    "cert": "commercial_electrical",
    "fit": 90
  },
  {
    "id": "J-112",
    "crew": "D-4",
    "stop": 2,
    "time": "12:30 PM",
    "location": "Cedar Ct",
    "job": "Meter upgrade",
    "hours": 1.5,
    "cert": "meter_service",
    "fit": 90
  }
]
```

## SCHEDULE_BASELINE

```json
{
  "baseline_jobs": 8,
  "baseline_miles": 330,
  "baseline_travel_hours": 37.1,
  "optimized_travel_hours": 24.5,
  "fuel_cost_per_mile": 1.0,
  "crew_hour_cost": 131.2,
  "first_time_fix_projected": 96
}
```

## OUTAGE

```json
{
  "area": "Downtown",
  "customers": 1247,
  "hospitals": 2,
  "initial_finding": "Primary feeder failure at Substation 7B",
  "target_restoration_hours": 2.5,
  "hospital_status": "Backup generators active (safe)",
  "dispatch": [
    {
      "crew": "E-7",
      "from": "Staging area",
      "eta_min": 8,
      "assignment": "Primary response"
    },
    {
      "crew": "F-8",
      "from": "2.4 mi away",
      "eta_min": 11,
      "assignment": "Assessment"
    },
    {
      "crew": "A-1",
      "from": "Redirected from Industrial Way",
      "eta_min": 18,
      "assignment": "Backup power"
    }
  ],
  "postponed_job": "J-104",
  "segments": [
    {
      "segment": "Hospitals",
      "impact_per_hour": 12400,
      "priority": "Critical",
      "restore_min": 48
    },
    {
      "segment": "Commercial",
      "impact_per_hour": 8700,
      "priority": "High",
      "restore_min": 63
    },
    {
      "segment": "Retail",
      "impact_per_hour": 4200,
      "priority": "Medium",
      "restore_min": 93
    },
    {
      "segment": "Residential",
      "impact_per_hour": 840,
      "priority": "Standard",
      "restore_min": 93
    }
  ]
}
```

## LIVE_STATUS

```json
{
  "minutes_since_outage": 16,
  "crews": [
    {
      "crew": "E-7",
      "status": "On site, cause confirmed",
      "details": [
        "Wildlife contact on Phase B insulator",
        "Rerouting through backup feeder",
        "ETA restoration: 45 minutes"
      ]
    },
    {
      "crew": "F-8",
      "status": "Downtown assessment complete",
      "details": [
        "3 transformers checked, all intact",
        "Safe to re-energize"
      ]
    }
  ]
}
```

## INCIDENT_REVIEW

```json
{
  "restored_min": 87,
  "metrics": [
    {
      "metric": "Response time",
      "target": 15,
      "actual": 8,
      "unit": "min"
    },
    {
      "metric": "Restoration",
      "target": 120,
      "actual": 87,
      "unit": "min"
    },
    {
      "metric": "First-time fix",
      "target": 95,
      "actual": 100,
      "unit": "%"
    }
  ],
  "value_protected": 37870,
  "response_cost": 4280,
  "prevention": [
    {
      "horizon": "Immediate (30 days)",
      "action": "Wildlife mitigation at Substation 7B",
      "cost": "$8,400",
      "benefit": "78% risk reduction"
    },
    {
      "horizon": "Immediate (30 days)",
      "action": "Vegetation management expansion",
      "cost": "$12,200/yr",
      "benefit": "prevents 3-4 outages"
    },
    {
      "horizon": "Long-term (6-12 months)",
      "action": "IoT sensors on 6 critical feeders",
      "cost": "$28,500",
      "benefit": "15-30 min early warning"
    },
    {
      "horizon": "Long-term (6-12 months)",
      "action": "Smart grid automation",
      "cost": "$340K",
      "benefit": "payback in 4.6 months"
    }
  ]
}
```

## WORK_ORDERS

```json
[
  {
    "id": "WO-2847",
    "action": "Wildlife mitigation",
    "owner": "Crew E-7",
    "due": "next week"
  },
  {
    "id": "WO-2848",
    "action": "Vegetation management",
    "owner": "Contractor",
    "due": "15 days"
  },
  {
    "id": "WO-2849",
    "action": "IoT sensor deployment",
    "owner": "Engineering",
    "due": "30 days"
  }
]
```

## MONTHLY_OPS

```json
{
  "emergency_response_min": [
    8,
    14
  ],
  "first_time_fix_pct": [
    96,
    89
  ],
  "csat_pct": 91.8,
  "fuel_cost": [
    18400,
    24700
  ],
  "overtime_savings": 22960,
  "emergencies": [
    {
      "event": "Downtown feeder outage (Substation 7B)",
      "revenue_protected": 37870
    },
    {
      "event": "Eastside substation breaker trip",
      "revenue_protected": 98400
    },
    {
      "event": "Industrial park cable fault",
      "revenue_protected": 81330
    },
    {
      "event": "Storm damage, north circuits",
      "revenue_protected": 52600
    }
  ]
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
