# Maintenance Scheduling Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. Every asset, sensor reading, order, technician, part, cost, and date is fictional. No equipment, CMMS, MES, or IoT platform was queried or controlled.

## Demo scenario: Line 3 injection molding (default machine: Machine #7, `IM-07`)

- Machine #7 (IM-2000 series, Line 3): Yellow Alert - Preventive maintenance required. Screw wear at 78%, barrel temp variance +3°C, estimated time to failure 120 operating hours, 4-hour overhaul, parts in stock; safe to run the current batch for 48 hours.
- Production: next week's order PO-5521 is 50,000 units (automotive brackets) for a Thursday shipment (on track). Line 3 capacity without #7 = machines #5, #6, #8 = 17,500 + 17,500 + 17,000 = 52,000 units, a 104% safety margin; quality risk Low.
- Window: Saturday 6 AM - 10 AM has zero lost units (Wednesday 2-6 PM loses 2,900; Friday 10 PM - Saturday 2 AM loses 1,400). Backup: Machine #9 from Line 2 on standby. Team B (certified for IM-2000) works the weekend.
- Cost-benefit: labor $1,800 (4 hrs x 2 technicians x $225 Team B weekend rate) + parts $1,400 (screw assembly $1,100 + heating bands $300) = $3,200. Exposure: emergency repair $12,500 + 2-day delay x $3,000 = $6,000 -> $18,500. ROI = (18,500 - 3,200) / 3,200 = 478%. Weekend overtime avoided $4,200; lifespan extended 18-24 months.
- Draft work order WO-2024-3847: Lead Marcus Chen (12 yrs, IM-2000 specialist), Tech Sarah Park (Level 3 certified), both available Saturday; parts Screw assembly #IM-2000-SC47 Bin 12-A, Heating bands (set of 4) Bin 18-C, transfer proposed Friday 4 PM to staging; Machine #7 offline Sat 6-10 AM; Machine #9 prepped; quality check Sunday 7 AM. A Teams message is drafted, not sent. No work order is created or dispatched until approved.
- 30-day calendar: Sat (2 days) Machine #7 overhaul (zero impact); Week 2 Line 1 conveyor lubrication (2 hrs); Week 3 Chiller #2 filter swap (minimal); Week 4 Machine #3 calibration (4 hrs). Alert: Machine #12 monitor vibration (30 days to threshold); hydraulic system all nominal; electrical panels no issues.
- Efficiency: 26 planned vs 4 reactive work orders = 87% planned (target 80%); MTBF 310 -> 415 hours = +34% year-over-year; $96,000 / 1,200,000 units = $0.08 per unit (industry avg $0.14).
- Optimization: quick wins (synthetic oil intervals $8,400/year; consolidate Line 2 & 3 windows 12 hrs/month; predictive sensors ROI 240%); investments (CMMS mobile app $12K -> 180 hrs/year; spare parts optimization frees $47K; RCM training 3 staff $18K); impact: unplanned downtime 4.2% -> 2.1% (halved), maintenance cost -$124K annually, availability 94% -> 97%, lifespan +2.5 years; next steps: Run pilot on Line 3, scale to all lines by Q3.

## Locked cases

| Case | Persona | Operation | Prompt | Required evidence |
|---|---|---|---|---|
| `MS-01` | Maintenance Manager | `schedule_overview` | Give me the equipment and technician-capacity picture I should review before the weekly maintenance meeting. | IM-07; Technician Availability; Marcus Chen |
| `MS-02` | Production Supervisor | `predictive_alerts` | Machine #7 on Line 3 is showing wear indicators and we have a big order next week. What does the condition data say? | Screw wear at 78%; 120 operating hours; 50,000 units |
| `MS-03` | Maintenance Manager | `work_order_plan` | Show me the lowest-impact maintenance window for machine #7 with coverage, crew, parts and backup, but do not create or dispatch work orders. | Saturday 6 AM - 10 AM; 104%; No work order is created or dispatched |
| `MS-04` | Operations Leader | `downtime_analysis` | What does preventive maintenance on machine #7 cost compared with a breakdown, and what is the ROI? | $3,200; $18,500; 478% |
| `MS-05` | Maintenance Manager | `work_order_draft` | Line up the crew and parts for the machine #7 overhaul so I can approve it. | WO-2024-3847; Bin 12-A; No work order is created or dispatched |
| `MS-06` | Operations Leader | `maintenance_calendar` | What does the maintenance calendar look like for the next 30 days? | Machine #12; 87% planned; Calibration |
| `MS-07` | Operations Leader | `optimization_plan` | What long-term changes would cut our maintenance cost and unplanned downtime? | Quick Wins; $124K; Run pilot on Line 3 |

## Complete record sets

### `EQUIPMENT`

```json
{
  "IM-05": {
    "name": "Machine #5",
    "line": "Line 3",
    "type": "IM-2000 injection molder",
    "status": "running",
    "weekly_capacity_units": 17500
  },
  "IM-06": {
    "name": "Machine #6",
    "line": "Line 3",
    "type": "IM-2000 injection molder",
    "status": "running",
    "weekly_capacity_units": 17500
  },
  "IM-07": {
    "name": "Machine #7",
    "line": "Line 3",
    "type": "IM-2000 injection molder",
    "status": "warning",
    "weekly_capacity_units": 17000
  },
  "IM-08": {
    "name": "Machine #8",
    "line": "Line 3",
    "type": "IM-2000 injection molder",
    "status": "running",
    "weekly_capacity_units": 17000
  },
  "IM-09": {
    "name": "Machine #9",
    "line": "Line 2",
    "type": "IM-2000 injection molder",
    "status": "standby",
    "weekly_capacity_units": 17000
  },
  "IM-03": {
    "name": "Machine #3",
    "line": "Line 1",
    "type": "IM-2000 injection molder",
    "status": "running",
    "weekly_capacity_units": 16000
  },
  "IM-12": {
    "name": "Machine #12",
    "line": "Line 2",
    "type": "IM-2000 injection molder",
    "status": "watch",
    "weekly_capacity_units": 16000
  },
  "CV-01": {
    "name": "Line 1 conveyor",
    "line": "Line 1",
    "type": "Conveyor",
    "status": "running",
    "weekly_capacity_units": 0
  },
  "CH-02": {
    "name": "Chiller #2",
    "line": "Utilities",
    "type": "Chiller",
    "status": "running",
    "weekly_capacity_units": 0
  }
}
```

### `SENSOR_READINGS`

```json
{
  "IM-07": {
    "screw_wear_pct": 78,
    "barrel_temp_variance_c": 3,
    "time_to_failure_hours": 120,
    "vibration_days_to_threshold": 0
  },
  "IM-12": {
    "screw_wear_pct": 41,
    "barrel_temp_variance_c": 1,
    "time_to_failure_hours": 0,
    "vibration_days_to_threshold": 30
  },
  "IM-05": {
    "screw_wear_pct": 35,
    "barrel_temp_variance_c": 0,
    "time_to_failure_hours": 0,
    "vibration_days_to_threshold": 0
  },
  "IM-06": {
    "screw_wear_pct": 42,
    "barrel_temp_variance_c": 1,
    "time_to_failure_hours": 0,
    "vibration_days_to_threshold": 0
  },
  "IM-08": {
    "screw_wear_pct": 29,
    "barrel_temp_variance_c": 0,
    "time_to_failure_hours": 0,
    "vibration_days_to_threshold": 0
  }
}
```

### `ALERT_RULES`

```json
{
  "screw_wear_yellow_pct": 75,
  "screw_wear_red_pct": 90
}
```

### `REPAIR_PLANS`

```json
{
  "IM-07": {
    "work": "Screw and barrel overhaul",
    "overhaul_hours": 4,
    "parts_status": "In stock",
    "safe_run_hours": 48,
    "parts": [
      {
        "part": "Screw assembly #IM-2000-SC47",
        "short": "screw assembly",
        "bin": "12-A",
        "cost": 1100
      },
      {
        "part": "Heating bands (set of 4)",
        "short": "heating bands",
        "bin": "18-C",
        "cost": 300
      }
    ],
    "parts_transfer": "Friday 4 PM to staging",
    "quality_check": "Sunday 7 AM"
  }
}
```

### `PRODUCTION_ORDERS`

```json
[
  {
    "order": "PO-5521",
    "product": "automotive brackets",
    "units": 50000,
    "week": "Next week",
    "line": "Line 3",
    "ship": "Thursday shipment",
    "status": "on track"
  }
]
```

### `MAINTENANCE_WINDOWS`

```json
[
  {
    "window": "Wednesday 2 PM - 6 PM",
    "day": "Wednesday",
    "day_short": "Wed",
    "start_hour": 14,
    "units_lost": 2900,
    "crew": "Team A"
  },
  {
    "window": "Friday 10 PM - Saturday 2 AM",
    "day": "Friday",
    "day_short": "Fri",
    "start_hour": 22,
    "units_lost": 1400,
    "crew": "Team C"
  },
  {
    "window": "Saturday 6 AM - 10 AM",
    "day": "Saturday",
    "day_short": "Sat",
    "start_hour": 6,
    "units_lost": 0,
    "crew": "Team B"
  }
]
```

### `TECHNICIANS`

```json
{
  "TECH-301": {
    "name": "Marcus Chen",
    "team": "Team B",
    "role": "Lead",
    "years": 12,
    "certifications": [
      "IM-2000"
    ],
    "level": "IM-2000 specialist",
    "available_saturday": true
  },
  "TECH-302": {
    "name": "Sarah Park",
    "team": "Team B",
    "role": "Tech",
    "years": 6,
    "certifications": [
      "IM-2000"
    ],
    "level": "Level 3 certified",
    "available_saturday": true
  },
  "TECH-201": {
    "name": "Marcus Rivera",
    "team": "Team A",
    "role": "Tech",
    "years": 9,
    "certifications": [
      "Conveyor",
      "Chiller"
    ],
    "level": "Level 2 certified",
    "available_saturday": false
  },
  "TECH-204": {
    "name": "Lin Zhao",
    "team": "Team C",
    "role": "Tech",
    "years": 7,
    "certifications": [
      "IM-2000",
      "Chiller"
    ],
    "level": "Level 2 certified",
    "available_saturday": false
  }
}
```

### `COST_MODEL`

```json
{
  "weekend_rate_per_tech_hour": 225,
  "crew_size": 2,
  "emergency_repair": 12500,
  "delay_days": 2,
  "delay_cost_per_day": 3000,
  "weekend_overtime_avoided": 4200,
  "lifespan_extension": "18-24 months"
}
```

### `CALENDAR_30_DAYS`

```json
[
  {
    "date": "Sat (2 days)",
    "equipment": "Machine #7",
    "type": "Overhaul",
    "impact": "Zero"
  },
  {
    "date": "Week 2",
    "equipment": "Line 1 conveyor",
    "type": "Lubrication",
    "impact": "2 hrs"
  },
  {
    "date": "Week 3",
    "equipment": "Chiller #2",
    "type": "Filter swap",
    "impact": "Minimal"
  },
  {
    "date": "Week 4",
    "equipment": "Machine #3",
    "type": "Calibration",
    "impact": "4 hrs"
  }
]
```

### `SYSTEM_CHECKS`

```json
[
  {
    "system": "Hydraulic system",
    "status": "All nominal"
  },
  {
    "system": "Electrical panels",
    "status": "No issues"
  }
]
```

### `EFFICIENCY`

```json
{
  "planned_work_orders": 26,
  "reactive_work_orders": 4,
  "planned_target_pct": 80,
  "mtbf_hours_last_year": 310,
  "mtbf_hours_this_year": 415,
  "annual_maintenance_cost": 96000,
  "annual_units": 1200000,
  "industry_cost_per_unit": 0.14
}
```

### `OPTIMIZATION`

```json
{
  "quick_wins": [
    "Extend oil change intervals using synthetic oil (save $8,400/year)",
    "Consolidate Line 2 & 3 maintenance windows (save 12 hrs/month)",
    "Predictive sensors on aging equipment (ROI: 240%)"
  ],
  "investments": [
    "CMMS mobile app: $12K -> save 180 hrs/year",
    "Spare parts optimization: free $47K working capital",
    "Reliability-centered maintenance training: 3 staff, $18K"
  ],
  "downtime_now_pct": 4.2,
  "downtime_target_pct": 2.1,
  "cost_reduction": 124000,
  "availability_now_pct": 94,
  "availability_target_pct": 97,
  "lifespan_gain_years": 2.5,
  "next_steps": "Run pilot on Line 3, scale to all lines by Q3"
}
```

## Resource evidence

- Technicians are proposed crew; nobody is booked or notified.
- Parts are listed with bins for reservation on approval; nothing is reserved.
- Backup readiness is a planning note; no equipment is started, stopped, switched, or rescheduled.

All exact readings, probabilities, hours, dates, and costs remain synthetic pilot evidence.
