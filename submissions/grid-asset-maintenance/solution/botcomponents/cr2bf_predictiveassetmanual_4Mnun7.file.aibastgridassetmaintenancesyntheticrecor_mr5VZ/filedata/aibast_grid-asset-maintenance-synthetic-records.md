# Predictive Asset Maintenance Intelligence — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Larkfield Electric Networks and every substation, asset, health score, failure probability, part, crew, person, work order, measurement and capital figure in this snapshot are invented. Never match them to a real organization, person, asset, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source. Health is 0-100 (100 = as new); p30, p90 and p180 are failure probabilities in percent over 30, 90 and 180 days. Materials are (part, needed, in stores, lead time in days). History entries are (days ago, event). start_in_days is the planned start counted from the snapshot day; completed_days_ago counts back from it. In the recorded responses, calendar dates are shown relative to the snapshot day and financial years as FY+1, FY+2 and FY+3 counted from the current financial year.

### Utility and policy

```json
{
 "name": "Larkfield Electric Networks",
 "policy": {
  "work_order_p90": 20,
  "plan_p180": 25,
  "long_lead_days": 30
 },
 "defaults": {
  "asset": "TX-0417",
  "work_order": "WO-55102"
 }
}
```

### Assets (condition-monitoring snapshot)

```json
[
 {
  "id": "TX-0417",
  "class": "Power transformer",
  "name": "Primary transformer T2, 33/11 kV 20 MVA",
  "site": "Millbrook Primary Substation",
  "age_years": 47,
  "customers": 8400,
  "health": 31,
  "rul_years": 1.5,
  "p30": 9,
  "p90": 27,
  "p180": 46,
  "anomaly": "Dissolved acetylene 9 ppm against a 1 ppm baseline; top-oil temperature 8 C above the load-corrected baseline",
  "action": "Offline inspection and on-load tap changer overhaul",
  "history": [
   {
    "days_ago": 410,
    "event": "On-load tap changer contacts inspected; moderate wear noted"
   },
   {
    "days_ago": 190,
    "event": "Oil sample: acetylene first detected at 3 ppm"
   },
   {
    "days_ago": 21,
    "event": "Oil sample: acetylene 9 ppm; reliability engineer flagged for review"
   }
  ],
  "materials": [
   {
    "part": "Tap changer contact kit",
    "needed": 1,
    "in_stores": 0,
    "lead_days": 35
   },
   {
    "part": "Transformer oil, 200 L drum",
    "needed": 4,
    "in_stores": 12,
    "lead_days": 3
   },
   {
    "part": "Gasket set, T2 tank",
    "needed": 1,
    "in_stores": 2,
    "lead_days": 5
   }
  ],
  "crew": "Substation Crew B (two HV fitters and a test engineer)",
  "start_in_days": 42,
  "outage": "Transfer the 11 kV load to transformer T1 (peak 14.2 MVA against a 20 MVA rating) for three days",
  "replacement_cost": 2400000
 },
 {
  "id": "SG-1123",
  "class": "Switchgear",
  "name": "11 kV switchboard panel 4",
  "site": "Ashby Road Substation",
  "age_years": 39,
  "customers": 3100,
  "health": 38,
  "rul_years": 2.0,
  "p30": 7,
  "p90": 22,
  "p180": 39,
  "anomaly": "Partial discharge 410 pC against a 60 pC baseline, rising for six weeks",
  "action": "Partial discharge investigation and panel refurbishment",
  "history": [
   {
    "days_ago": 730,
    "event": "Routine maintenance; no defects"
   },
   {
    "days_ago": 44,
    "event": "Partial discharge alarm at 180 pC"
   },
   {
    "days_ago": 6,
    "event": "Partial discharge 410 pC confirmed by handheld survey"
   }
  ],
  "materials": [
   {
    "part": "Cable termination kit, 11 kV",
    "needed": 3,
    "in_stores": 4,
    "lead_days": 7
   },
   {
    "part": "Busbar insulating boots",
    "needed": 6,
    "in_stores": 0,
    "lead_days": 21
   }
  ],
  "crew": "Substation Crew A (two HV fitters)",
  "start_in_days": 28,
  "outage": "Open the bus section and back-feed panel 4 customers from feeder 9 for one day",
  "replacement_cost": 640000
 },
 {
  "id": "CB-2208",
  "class": "Underground cable",
  "name": "11 kV feeder 7, 1.2 km paper-insulated section",
  "site": "Harbour Street",
  "age_years": 54,
  "customers": 1900,
  "health": 44,
  "rul_years": 3.0,
  "p30": 4,
  "p90": 15,
  "p180": 31,
  "anomaly": "Partial discharge at joint 2 of 3, 260 pC against a 40 pC baseline",
  "action": "Replace joint 2 and plan the section replacement",
  "history": [
   {
    "days_ago": 1100,
    "event": "Fault at joint 1; joint replaced"
   },
   {
    "days_ago": 95,
    "event": "Online partial discharge monitor fitted"
   }
  ],
  "materials": [
   {
    "part": "11 kV transition joint kit",
    "needed": 1,
    "in_stores": 2,
    "lead_days": 14
   }
  ],
  "crew": "Cable Jointing Team 2",
  "start_in_days": 120,
  "outage": "Feeder 7 back-fed from feeder 11 during the joint change",
  "replacement_cost": 1100000
 },
 {
  "id": "OH-3310",
  "class": "Overhead line",
  "name": "33 kV line Fenwick to Millbrook, spans 112 to 118",
  "site": "Fenwick corridor",
  "age_years": 31,
  "customers": 5200,
  "health": 52,
  "rul_years": 6.0,
  "p30": 5,
  "p90": 12,
  "p180": 20,
  "anomaly": "Thermal survey: two compression clamps 22 C above conductor temperature",
  "action": "Replace two compression clamps",
  "history": [
   {
    "days_ago": 365,
    "event": "Annual thermal survey; no hotspots"
   },
   {
    "days_ago": 12,
    "event": "Thermal survey found two hot clamps"
   }
  ],
  "materials": [
   {
    "part": "Compression clamp, 33 kV",
    "needed": 2,
    "in_stores": 10,
    "lead_days": 3
   }
  ],
  "crew": "Overhead Line Crew 3",
  "start_in_days": 60,
  "outage": "None; live-line clamp replacement",
  "replacement_cost": 380000
 },
 {
  "id": "TX-0388",
  "class": "Power transformer",
  "name": "Primary transformer T1, 33/11 kV 15 MVA",
  "site": "Calder Lane Substation",
  "age_years": 36,
  "customers": 6100,
  "health": 61,
  "rul_years": 9.0,
  "p30": 2,
  "p90": 8,
  "p180": 17,
  "anomaly": "Oil level 6% below normal; slow weep at the radiator flange",
  "action": "Repair the radiator flange and top up the oil",
  "history": [
   {
    "days_ago": 300,
    "event": "Oil sample normal"
   }
  ],
  "materials": [
   {
    "part": "Radiator flange gasket",
    "needed": 2,
    "in_stores": 6,
    "lead_days": 5
   }
  ],
  "crew": "Substation Crew B",
  "start_in_days": 90,
  "outage": "None",
  "replacement_cost": 1900000
 },
 {
  "id": "SG-1140",
  "class": "Switchgear",
  "name": "11 kV ring main unit RMU-22",
  "site": "Orchard Way",
  "age_years": 24,
  "customers": 700,
  "health": 72,
  "rul_years": 12.0,
  "p30": 1,
  "p90": 4,
  "p180": 9,
  "anomaly": "None; SF6 gas pressure stable",
  "action": "Routine inspection",
  "history": [
   {
    "days_ago": 400,
    "event": "Routine inspection"
   }
  ],
  "materials": [],
  "crew": "Substation Crew A",
  "start_in_days": 180,
  "outage": "None",
  "replacement_cost": 45000
 },
 {
  "id": "CB-2215",
  "class": "Underground cable",
  "name": "11 kV feeder 12, XLPE section",
  "site": "Quarry Road",
  "age_years": 18,
  "customers": 1400,
  "health": 76,
  "rul_years": 20.0,
  "p30": 1,
  "p90": 3,
  "p180": 7,
  "anomaly": "None",
  "action": "Monitor",
  "history": [],
  "materials": [],
  "crew": "Cable Jointing Team 1",
  "start_in_days": 180,
  "outage": "None",
  "replacement_cost": 600000
 },
 {
  "id": "OH-3302",
  "class": "Overhead line",
  "name": "11 kV line Calder Lane spur",
  "site": "Calder valley",
  "age_years": 14,
  "customers": 900,
  "health": 80,
  "rul_years": 25.0,
  "p30": 1,
  "p90": 3,
  "p180": 6,
  "anomaly": "None",
  "action": "Monitor",
  "history": [],
  "materials": [],
  "crew": "Overhead Line Crew 1",
  "start_in_days": 180,
  "outage": "None",
  "replacement_cost": 150000
 }
]
```

### Completed jobs (field records)

```json
[
 {
  "work_order": "WO-55102",
  "asset": "SG-1131",
  "asset_name": "11 kV switchboard panel 2, Ashby Road Substation",
  "completed_days_ago": 2,
  "crew_lead": "Rowan Pettigrew",
  "work_done": "Replaced three vacuum interrupters and cleaned the cable box",
  "parts": [
   {
    "part": "Vacuum interrupter, 11 kV",
    "qty": 3,
    "unit_cost": 6200
   }
  ],
  "required": [
   "Contact resistance",
   "Insulation resistance",
   "Partial discharge after energization"
  ],
  "measurements": {
   "Contact resistance": "38 micro-ohm (limit 60)",
   "Insulation resistance": "12 G-ohm (minimum 1)",
   "Partial discharge after energization": "35 pC (baseline 60)"
  },
  "condition_before": 4,
  "condition_after": 2,
  "fixed_asset": "FA-SG-1131"
 },
 {
  "work_order": "WO-55097",
  "asset": "CB-2190",
  "asset_name": "11 kV feeder 3 cable, joint 4, Mill Lane",
  "completed_days_ago": 1,
  "crew_lead": "Dara Whitcombe",
  "work_done": "Replaced joint 4 with a transition joint",
  "parts": [
   {
    "part": "11 kV transition joint kit",
    "qty": 1,
    "unit_cost": 2900
   }
  ],
  "required": [
   "Insulation resistance",
   "Sheath test",
   "Partial discharge after energization"
  ],
  "measurements": {
   "Sheath test": "Pass at 10 kV",
   "Partial discharge after energization": "28 pC (baseline 40)"
  },
  "condition_before": 4,
  "condition_after": 2,
  "fixed_asset": "FA-CB-2190"
 }
]
```

### Fleet by asset class

```json
[
 {
  "class": "Power transformers",
  "count": "64 units",
  "avg_health": 66,
  "poor": "5 units",
  "at_risk_180": "3 units"
 },
 {
  "class": "Switchgear",
  "count": "410 panels",
  "avg_health": 71,
  "poor": "22 panels",
  "at_risk_180": "9 panels"
 },
 {
  "class": "Underground cables",
  "count": "1,280 km",
  "avg_health": 63,
  "poor": "41 km",
  "at_risk_180": "12 km"
 },
 {
  "class": "Overhead lines",
  "count": "2,350 km",
  "avg_health": 74,
  "poor": "18 km",
  "at_risk_180": "6 km"
 }
]
```

### Replacement pipeline (year_offset counts financial years from this one)

```json
[
 {
  "asset": "TX-0417",
  "plan": "Replace T2 once the tap changer overhaul (about two more years of life) runs out",
  "year_offset": 2,
  "capital": 2400000
 },
 {
  "asset": "SG-1123",
  "plan": "Replace the Ashby Road 11 kV switchboard (8 panels)",
  "year_offset": 1,
  "capital": 640000
 },
 {
  "asset": "CB-2208",
  "plan": "Replace the 1.2 km paper-insulated section of feeder 7",
  "year_offset": 1,
  "capital": 1100000
 },
 {
  "asset": "Program",
  "plan": "Cable replacement program: the worst 9 km of the 41 km in poor condition",
  "year_offset": 3,
  "capital": 7200000
 }
]
```

## Exact responses for every locked case

### GAM-01 — Risk ranking

Prompt: "Which of our grid assets are most likely to fail in the next 90 days, and what's driving it?"

Operation: `risk_ranking`; arguments: `{"operation": "risk_ranking"}`

**Grid Asset Risk Ranking - Larkfield Electric Networks**

**As of:** the snapshot day's condition-monitoring snapshot | **Assets monitored:** 8 | **Work orders recommended:** 2 | **To plan within 180 days:** 1

**Act first:** TX-0417 Primary transformer T2, 33/11 kV 20 MVA at Millbrook Primary Substation: 27% chance of failure in 90 days, 8,400 customers on it. Dissolved acetylene 9 ppm against a 1 ppm baseline; top-oil temperature 8 C above the load-corrected baseline.

| Rank | Asset | Class | Site | Health | Fail 30 d | Fail 90 d | Fail 180 d | Remaining life | Recommended action |
|------|-------|-------|------|--------|-----------|-----------|------------|----------------|--------------------|
| 1 | TX-0417 | Power transformer | Millbrook Primary Substation | 31 | 9% | 27% | 46% | 1.5 yr | Raise work order now: Offline inspection and on-load tap changer overhaul |
| 2 | SG-1123 | Switchgear | Ashby Road Substation | 38 | 7% | 22% | 39% | 2 yr | Raise work order now: Partial discharge investigation and panel refurbishment |
| 3 | CB-2208 | Underground cable | Harbour Street | 44 | 4% | 15% | 31% | 3 yr | Plan within 180 days: Replace joint 2 and plan the section replacement |
| 4 | OH-3310 | Overhead line | Fenwick corridor | 52 | 5% | 12% | 20% | 6 yr | Monitor; at next visit: Replace two compression clamps |
| 5 | TX-0388 | Power transformer | Calder Lane Substation | 61 | 2% | 8% | 17% | 9 yr | Monitor; at next visit: Repair the radiator flange and top up the oil |
| 6 | SG-1140 | Switchgear | Orchard Way | 72 | 1% | 4% | 9% | 12 yr | Monitor; at next visit: Routine inspection |
| 7 | CB-2215 | Underground cable | Quarry Road | 76 | 1% | 3% | 7% | 20 yr | Monitor |
| 8 | OH-3302 | Overhead line | Calder valley | 80 | 1% | 3% | 6% | 25 yr | Monitor |

**What is driving the top risks**
- TX-0417: Dissolved acetylene 9 ppm against a 1 ppm baseline; top-oil temperature 8 C above the load-corrected baseline.
- SG-1123: Partial discharge 410 pC against a 60 pC baseline, rising for six weeks.
- CB-2208: Partial discharge at joint 2 of 3, 260 pC against a 40 pC baseline.

Work orders are recommended at 20% or more 90-day failure probability; planning starts at 25% over 180 days.

> Read-only synthetic snapshot of a fictional utility. No work order was raised, no part was ordered, no crew was assigned and no register was changed; an authorized engineer approves every step.

Source: [Synthetic Grid Asset Condition Snapshot]
Agents: GridAssetMaintenanceAgent

### GAM-02 — Work order draft

Prompt: "Get a preventive work order ready for the Millbrook transformer, with the parts and crew we need. Don't raise it yet."

Operation: `work_order_draft`; arguments: `{"operation": "work_order_draft", "asset": "Millbrook transformer"}`

**Preventive Work Order Draft - TX-0417**

**Asset:** Primary transformer T2, 33/11 kV 20 MVA, Millbrook Primary Substation (Power transformer, 47 years old)
**Risk:** health 31; failure probability 9% in 30 days, 27% in 90 days, 46% in 180 days; 8,400 customers

**Work:** Offline inspection and on-load tap changer overhaul
**Why now:** Dissolved acetylene 9 ppm against a 1 ppm baseline; top-oil temperature 8 C above the load-corrected baseline.
**Planned start:** day 42 from the snapshot | **Priority:** High | **Crew:** Substation Crew B (two HV fitters and a test engineer)
**Outage plan:** Transfer the 11 kV load to transformer T1 (peak 14.2 MVA against a 20 MVA rating) for three days

**Asset history**
- (dated by history days_ago): On-load tap changer contacts inspected; moderate wear noted
- (dated by history days_ago): Oil sample: acetylene first detected at 3 ppm
- (dated by history days_ago): Oil sample: acetylene 9 ppm; reliability engineer flagged for review

**Materials and parts pre-plan**

| Part | Needed | In stores | Lead time | Action |
|------|--------|-----------|-----------|--------|
| Tap changer contact kit | 1 | 0 | 35 days | Long-lead: Order by day 7 from the snapshot |
| Transformer oil, 200 L drum | 4 | 12 | 3 days | Reserve from stores |
| Gasket set, T2 tank | 1 | 2 | 5 days | Reserve from stores |

**Long-lead parts to order first:** Tap changer contact kit.

**Status:** Draft - a maintenance planner approves it in Field Service, which raises the work order, reserves the stores items and sends purchase requisitions for the parts to order. Nothing has been raised, ordered or assigned.

> Read-only synthetic snapshot of a fictional utility. No work order was raised, no part was ordered, no crew was assigned and no register was changed; an authorized engineer approves every step.

Source: [Synthetic Grid Asset Condition Snapshot]
Agents: GridAssetMaintenanceAgent

### GAM-03 — Register update check

Prompt: "The Mill Lane cable joint job closed yesterday. Is the field record complete enough to update the asset register?"

Operation: `register_update`; arguments: `{"operation": "register_update", "work_order": "Mill Lane joint"}`

**Asset Register Update Check - WO-55097**

**Asset:** CB-2190 11 kV feeder 3 cable, joint 4, Mill Lane
**Completed:** recently (see completed_days_ago) by Dara Whitcombe | **Work done:** Replaced joint 4 with a transition joint

**Field record**

| Required measurement | Recorded |
|----------------------|----------|
| Insulation resistance | MISSING |
| Sheath test | Pass at 10 kV |
| Partial discharge after energization | 28 pC (baseline 40) |

**Not ready for the register.** Missing: Insulation resistance. Ask Dara Whitcombe to add it on the job form; the register update stays on hold until the record is complete.

> Read-only synthetic snapshot of a fictional utility. No work order was raised, no part was ordered, no crew was assigned and no register was changed; an authorized engineer approves every step.

Source: [Synthetic Grid Asset Condition Snapshot]
Agents: GridAssetMaintenanceAgent

### GAM-04 — Replacement plan

Prompt: "For the investment committee, how healthy is the fleet and what replacements and capital do we need over the next few years?"

Operation: `replacement_plan`; arguments: `{"operation": "replacement_plan"}`

**Fleet Health and Replacement Plan - Larkfield Electric Networks**

**Capital needed in the plan:** $11,340,000 over the next 3 financial years.

| Asset class | Fleet | Average health | Poor condition | At risk in 180 days |
|-------------|-------|----------------|----------------|---------------------|
| Power transformers | 64 units | 66 | 5 units | 3 units |
| Switchgear | 410 panels | 71 | 22 panels | 9 panels |
| Underground cables | 1,280 km | 63 | 41 km | 12 km |
| Overhead lines | 2,350 km | 74 | 18 km | 6 km |

**Replacement pipeline**

| Year | Asset | Plan | Capital |
|------|-------|------|---------|
| FY+1 | SG-1123 | Replace the Ashby Road 11 kV switchboard (8 panels) | $640,000 |
| FY+1 | CB-2208 | Replace the 1.2 km paper-insulated section of feeder 7 | $1,100,000 |
| FY+2 | TX-0417 | Replace T2 once the tap changer overhaul (about two more years of life) runs out | $2,400,000 |
| FY+3 | Program | Cable replacement program: the worst 9 km of the 41 km in poor condition | $7,200,000 |

**Capital by year:** FY+1 $1,740,000; FY+2 $2,400,000; FY+3 $7,200,000

> Recommendation only: the investment committee approves the replacement program. Read-only synthetic snapshot of a fictional utility. No work order was raised, no part was ordered, no crew was assigned and no register was changed; an authorized engineer approves every step.

Source: [Synthetic Grid Asset Condition Snapshot]
Agents: GridAssetMaintenanceAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| GAM-01 | Reliability Engineer | Which of our grid assets are most likely to fail in the next 90 days, and what's driving it? | `risk_ranking` | Grid Asset Risk Ranking; TX-0417; SG-1123 |
| GAM-02 | Maintenance Planner | Get a preventive work order ready for the Millbrook transformer, with the parts and crew we need. Don't raise it yet. | `work_order_draft` | Preventive Work Order Draft; Tap changer contact kit; Substation Crew B |
| GAM-03 | Reliability Engineer | The Mill Lane cable joint job closed yesterday. Is the field record complete enough to update the asset register? | `register_update` | Asset Register Update Check; WO-55097; Insulation resistance |
| GAM-04 | Director of Asset Management | For the investment committee, how healthy is the fleet and what replacements and capital do we need over the next few years? | `replacement_plan` | Fleet Health and Replacement Plan; TX-0417; $11,340,000 |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
