# Maintenance Scheduling Pilot — Review Rules

> Uploadable pilot guidance. This content supports human planning and does not authorize maintenance execution.

## Analysis

- Rank condition signals using the deterministic snapshot and explain the evidence.
- Present technicians only as candidates and maintenance windows only as proposals.
- Separate parts readiness, backup-capacity review, and production-impact review.

## Action boundary

- Never control equipment, alter a production schedule, reserve a part, create a work order, assign a technician, or dispatch maintenance.
- Authorized maintenance and production owners must verify telemetry and approve action through connected CMMS, MES, and safety systems.

## Routing

- `schedule_overview` (MS-01): "Give me the equipment and technician-capacity picture I should review before the weekly maintenance meeting."
- `predictive_alerts` (MS-02): "Machine #7 on Line 3 is showing wear indicators and we have a big order next week. What does the condition data say?"
- `work_order_plan` (MS-03): "Show me the lowest-impact maintenance window for machine #7 with coverage, crew, parts and backup, but do not create or dispatch work orders."
- `downtime_analysis` (MS-04): "What does preventive maintenance on machine #7 cost compared with a breakdown, and what is the ROI?"
- `work_order_draft` (MS-05): "Line up the crew and parts for the machine #7 overhaul so I can approve it."
- `maintenance_calendar` (MS-06): "What does the maintenance calendar look like for the next 30 days?"
- `optimization_plan` (MS-07): "What long-term changes would cut our maintenance cost and unplanned downtime?"
- Video phrasing: "Schedule maintenance for Line 3 ... machine #7 is showing wear indicators" -> `predictive_alerts`; "show me the schedule" -> `work_order_plan`; "cost analysis" -> `downtime_analysis`; "schedule everything" -> `work_order_draft`; "full maintenance calendar" -> `maintenance_calendar`; "long-term optimization" -> `optimization_plan`.

## Exact reference outputs

### MS-01 `schedule_overview`

```markdown
## Maintenance Schedule Overview

> Synthetic planning snapshot; no equipment was queried or controlled.

### Equipment Status

| ID | Equipment | Line | Type | Status | Alert |
|----|-----------|------|------|--------|-------|
| IM-05 | Machine #5 | Line 3 | IM-2000 injection molder | running | Normal |
| IM-06 | Machine #6 | Line 3 | IM-2000 injection molder | running | Normal |
| IM-07 | Machine #7 | Line 3 | IM-2000 injection molder | warning | Yellow Alert - Preventive maintenance required |
| IM-08 | Machine #8 | Line 3 | IM-2000 injection molder | running | Normal |
| IM-09 | Machine #9 | Line 2 | IM-2000 injection molder | standby | Normal |
| IM-03 | Machine #3 | Line 1 | IM-2000 injection molder | running | Normal |
| IM-12 | Machine #12 | Line 2 | IM-2000 injection molder | watch | Monitor |
| CV-01 | Line 1 conveyor | Line 1 | Conveyor | running | Normal |
| CH-02 | Chiller #2 | Utilities | Chiller | running | Normal |

### Technician Availability

| Technician | Team | Role | Certification | Saturday |
|------------|------|------|---------------|----------|
| Marcus Chen | Team B | Lead | IM-2000 specialist | Available |
| Sarah Park | Team B | Tech | Level 3 certified | Available |
| Marcus Rivera | Team A | Tech | Level 2 certified | Not available |
| Lin Zhao | Team C | Tech | Level 2 certified | Not available |
```

### MS-02 `predictive_alerts`

```markdown
## Predictive Maintenance Alerts

> Synthetic advisory signals only; verify against approved condition-monitoring systems before action.

Optimizing the maintenance schedule to protect next week's production while addressing Machine #7's condition (wear indicators, production capacity, crew availability).

### Machine #7 Status (IM-07, Line 3)

- **Yellow Alert - Preventive maintenance required**
- Screw wear at 78%, barrel temp variance +3°C
- Estimated time to failure: 120 operating hours
- Required maintenance: 4-hour overhaul
- Parts needed: In stock

### Production Context

- Next week order: 50,000 units (automotive brackets)
- Current capacity without #7: 52,000 units
- Delivery: Thursday shipment (on track)

### Other Signals

- Machine #12: Monitor (vibration 30 days to threshold)

Source: [IoT Sensors + D365 Production + EAM]

Next: shall I create the optimized schedule?
```

### MS-03 `work_order_plan`

```markdown
## Proposed Work Order Plan

> Fixed synthetic plan for planner review. No work order is created or dispatched, no technician is assigned, and no part is reserved.

### Optimized Maintenance Schedule

**Maintenance Window:** Saturday 6 AM - 10 AM

**Why This Works:**
- Zero production impact - using machines #5, #6, #8
- Backup ready: Machine #9 from Line 2 on standby
- Weekend labor: Team B certified for IM-2000 series
- Parts staged: screw assembly + heating bands

**Immediate Action:** Run Machine #7 for the current batch only (safe for 48 hours), then take it offline.

### Production Continuity

| Metric | Value |
|--------|-------|
| Capacity without #7 | 52,000 units |
| Required capacity | 50,000 units |
| Safety margin | 104% |
| Quality risk | Low |

Other windows considered: Wednesday 2 PM - 6 PM (2,900 units lost); Friday 10 PM - Saturday 2 AM (1,400 units lost)

Source: [D365 Production + EAM]

Next: want to see the cost analysis?
```

### MS-04 `downtime_analysis`

```markdown
## Downtime & Cost Analysis

> All probabilities, hours, and costs are synthetic planning estimates.

### Cost-Benefit Analysis

**Preventive Maintenance Investment:**
- Labor: $1,800 (4 hrs, Team B weekend rate)
- Parts: $1,400 (screw assembly + heating bands)
- Total: $3,200

**Avoided Breakdown Costs:**
- Emergency repair: $12,500
- Production delay: 2 days = $6,000
- Total exposure: $18,500

**ROI: 478%** by avoiding unplanned downtime (($18,500 - $3,200) / $3,200)

**Modeled avoided-cost opportunity:** $15,300

**Additional Benefits:**
- Weekend overtime avoided ($4,200 saved)
- Quality maintained (no rushed repairs)
- Customer confidence (on-time delivery)
- Machine lifespan extended 18-24 months

Source: [EAM Cost Data + Historical]

Next: ready to schedule the crew and parts?
```

### MS-05 `work_order_draft`

```markdown
## Maintenance Schedule Ready for Approval

> Synthetic draft only. No work order is created or dispatched, no technician is booked, no notification is sent, and no part is reserved until you approve it in the maintenance system.

**Draft Work Order:** WO-2024-3847 (Screw and barrel overhaul, Machine #7, Saturday 6 AM - 10 AM)

**Proposed Crew:**
- Lead: Marcus Chen (12 yrs, IM-2000 specialist)
- Tech: Sarah Park (Level 3 certified)
- Notification: Teams message drafted for the crew (not sent)
- Availability: Both available Saturday

**Parts to Reserve (on approval):**
- Screw assembly #IM-2000-SC47: Bin 12-A
- Heating bands (set of 4): Bin 18-C
- Transfer proposed: Friday 4 PM to staging

**Production Coordination (drafts):**
- Operations notice: Machine #7 offline Sat 6-10 AM
- Backup plan: Machine #9 prepped (Line 2)
- Quality check: Sunday 7 AM

Source: [EAM + D365 + Teams]

Next: want to see the full maintenance calendar?
```

### MS-06 `maintenance_calendar`

```markdown
## Predictive Maintenance Calendar - Next 30 Days

> Synthetic planning calendar; nothing is booked.

### Upcoming Maintenance

| Date | Equipment | Type | Impact |
|------|-----------|------|--------|
| Sat (2 days) | Machine #7 | Overhaul | Zero |
| Week 2 | Line 1 conveyor | Lubrication | 2 hrs |
| Week 3 | Chiller #2 | Filter swap | Minimal |
| Week 4 | Machine #3 | Calibration | 4 hrs |

### Predictive Alerts

- Machine #12: Monitor vibration (30 days to threshold)
- Hydraulic system: All nominal
- Electrical panels: No issues

### Maintenance Efficiency

- Planned vs. reactive: 87% planned (target: 80%)
- MTBF improvement: +34% year-over-year
- Cost per unit: $0.08 (industry avg: $0.14)

Source: [EAM + IoT + Power BI]

Next: want to see long-term optimization recommendations?
```

### MS-07 `optimization_plan`

```markdown
## Strategic Maintenance Optimization

> Synthetic recommendations for leadership review; no purchase or change is made.

### Quick Wins (Next Quarter)

- Extend oil change intervals using synthetic oil (save $8,400/year)
- Consolidate Line 2 & 3 maintenance windows (save 12 hrs/month)
- Predictive sensors on aging equipment (ROI: 240%)

### Investment Opportunities

- CMMS mobile app: $12K -> save 180 hrs/year
- Spare parts optimization: free $47K working capital
- Reliability-centered maintenance training: 3 staff, $18K

### Impact Projection

- Unplanned downtime: 4.2% -> 2.1% (halved)
- Maintenance cost: -$124K annually
- Production availability: 94% -> 97%
- Equipment lifespan: +2.5 years average

**Next Steps:** Run pilot on Line 3, scale to all lines by Q3

Source: [Historical Data + Industry Benchmarks]
```

