# Field Service Dispatch Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. `crew_id` accepts a crew ID or part of the crew/lead name (e.g. `A-1`, `Marcus Chen`); empty means Crew A-1; an unknown value returns "Unknown Crew" and no substitute crew.
2. `dispatch_dashboard` emits `# Field Service Dispatch Dashboard - Tomorrow`: all 12 jobs in JOBS order and every crew's status.
3. `route_optimization` emits `# Optimized Schedule - Tomorrow`. Per crew: jobs = its JOBS rows, miles = `route_miles`, skill match = mean job `fit` rounded. Miles saved = baseline_miles - sum(route_miles) = 330 - 143 = 187; hours saved = 37.1 - 24.5 = 12.6; travel-time cut = 12.6 / 37.1 = 34%; savings = 187 x $1.00 + 12.6 x $131.20 = $1,840/day; jobs lift = (12 - 8) / 8 = +50%.
4. `technician_assignment` emits the crew's timed stops (`# Crew A-1 Route - 4 Stops, Zero Backtracking` by default) with the certification each stop needs and the crew certifications matched to stop numbers; a standby crew has no route.
5. `emergency_response` emits `# Emergency Response Draft - Ready for Dispatcher Approval`: OUTAGE customers, hospitals and finding, the three crew dispatch rows with ETAs, revenue at risk = sum of segment impact per hour ($26,140/hour), the postponed A-1 job (J-104) and remaining jobs = 12 - 1 = 11.
6. `incident_status` emits `# Live Status - 16 Minutes Since Outage`: LIVE_STATUS crew findings, the segment table with its total, and the restoration timeline (hospitals 48, commercial 63, full = max restore_min = 93 min).
7. `post_incident_review` emits the review: Beat when actual <= target minutes or actual >= target percent; ROI = (value protected - response cost) / response cost = (37,870 - 4,280) / 4,280 = 785%; prevention actions grouped by horizon.
8. `work_orders_report` emits the draft work orders WO-2847..WO-2849 and the monthly table; cost savings = fuel savings (24,700 - 18,400 = 6,300) + overtime savings 22,960 = $29,260/month; revenue protected = sum of the 4 emergencies = $270,200.
9. No crew is dispatched, rerouted, assigned or notified, no customer message or SMS is sent, no schedule is synced and no work order is created; every such item is a draft for a human dispatcher.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### FIELD_SERVICE_DISPATCH-01 — Field Operations Manager — `dispatch_dashboard`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-01",
  "persona": "Field Operations Manager",
  "operation": "dispatch_dashboard",
  "prompt": "What does tomorrow's job list look like by crew, and which crews are on standby?",
  "canonical_kwargs": {
    "operation": "dispatch_dashboard"
  },
  "must_include": [
    "J-101",
    "Marcus Chen",
    "No job"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Field Service Dispatch Dashboard - Tomorrow

**Jobs:** 12 | **Scheduled crews:** 4 | **Standby crews:** 2

| Job | Crew | Time | Location | Work | Hours |
|-----|------|------|----------|------|-------|
| J-101 | A-1 | 7:00 AM | Oak Ridge Blvd | Transformer inspect | 1.5 |
| J-102 | A-1 | 9:15 AM | Riverside Dr | Underground cable | 2.0 |
| J-103 | A-1 | 12:00 PM | Commerce Pkwy | Meter upgrade | 1.5 |
| J-104 | A-1 | 2:30 PM | Industrial Way | Switchgear maint | 1.0 |
| J-105 | B-2 | 7:30 AM | Maple Ave | Pole transformer swap | 2.5 |
| J-106 | B-2 | 10:30 AM | Harbor St | Smart meter install | 1.5 |
| J-107 | B-2 | 1:00 PM | Lakeview Dr | Service drop repair | 2.0 |
| J-108 | C-3 | 7:30 AM | Elm St vault | Cable splice | 2.5 |
| J-109 | C-3 | 10:45 AM | Park Plaza | Network protector test | 2.0 |
| J-110 | C-3 | 1:30 PM | Union Sq | Vault inspection | 1.5 |
| J-111 | D-4 | 8:00 AM | Westgate Mall | Commercial meter bank | 3.0 |
| J-112 | D-4 | 12:30 PM | Cedar Ct | Meter upgrade | 1.5 |

| Crew | Lead | Status | Location |
|------|------|--------|----------|
| A-1 | Marcus Chen | scheduled | North service yard |
| B-2 | Priya Nair | scheduled | East service yard |
| C-3 | Diego Alvarez | scheduled | South service yard |
| D-4 | Hannah Brooks | scheduled | West service yard |
| E-7 | Tom Okafor | standby | Downtown staging area |
| F-8 | Lena Park | standby | 2.4 mi from downtown |

> Read-only synthetic dashboard. No job, crew, route, customer message, or inventory record was changed.
```

### FIELD_SERVICE_DISPATCH-02 — Service Director — `route_optimization`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-02",
  "persona": "Service Director",
  "operation": "route_optimization",
  "prompt": "I need help optimizing our field technician schedules for tomorrow. We have 15 service calls.",
  "canonical_kwargs": {
    "operation": "route_optimization"
  },
  "must_include": [
    "34%",
    "187 miles",
    "$1,840/day"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Optimized Schedule - Tomorrow

Geographic clustering across the metro area cuts travel time by 34%, saving 187 miles and 12.6 billable hours.

| Crew | Jobs | Miles | Skill Match |
|------|------|-------|-------------|
| A-1 | 4 | 42 mi | 100% |
| B-2 | 3 | 38 mi | 95% |
| C-3 | 3 | 35 mi | 100% |
| D-4 | 2 | 28 mi | 90% |

**Impact:**
- Efficiency: +50% jobs (12 vs 8 baseline)
- First-time fix: 96% projected
- Cost savings: $1,840/day in fuel and overtime
- Travel: 330 -> 143 miles; 37.1 -> 24.5 travel hours

Routes are ready to sync to Field Service and the customer SMS confirmations are drafted; both go out after dispatcher approval.

Next: see Crew A-1's detailed route.

> Draft schedule only. A dispatcher must validate travel, safety, labor, and SLA constraints before rerouting.
```

### FIELD_SERVICE_DISPATCH-03 — Dispatch Coordinator — `technician_assignment`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-03",
  "persona": "Dispatch Coordinator",
  "operation": "technician_assignment",
  "prompt": "Yes, show me Crew A-1's detailed route",
  "canonical_kwargs": {
    "operation": "technician_assignment",
    "crew_id": "A-1"
  },
  "must_include": [
    "Marcus Chen",
    "Truck",
    "Underground cable certified"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Crew A-1 Route - 4 Stops, Zero Backtracking

**Lead:** Marcus Chen (12 yrs, Level 3) | **Truck:** #47 fully stocked | **Route:** 42 miles

| Time | Location | Job | Duration | Skill Needed |
|------|----------|-----|----------|--------------|
| 7:00 AM | Oak Ridge Blvd | Transformer inspect | 1.5 hrs | High-voltage certification |
| 9:15 AM | Riverside Dr | Underground cable | 2.0 hrs | Underground cable certified |
| 12:00 PM | Commerce Pkwy | Meter upgrade | 1.5 hrs | Commercial electrical license |
| 2:30 PM | Industrial Way | Switchgear maint | 1.0 hr | High-voltage certification |

**Skills Matched:**
- High-voltage certification (stops 1, 4)
- Underground cable certified (stop 2)
- Commercial electrical license (stop 3)

Parts are pre-staged on the truck; 30-min arrival alerts are drafted for each customer.

> Recommendation only. No technician has been assigned, notified, or dispatched.
```

### FIELD_SERVICE_DISPATCH-04 — Emergency Duty Manager — `emergency_response`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-04",
  "persona": "Emergency Duty Manager",
  "operation": "emergency_response",
  "prompt": "URGENT: Major power outage downtown - 1,200 customers affected. Dispatch emergency crews now!",
  "canonical_kwargs": {
    "operation": "emergency_response"
  },
  "must_include": [
    "1,247",
    "$26,140/hour",
    "No crew was dispatched"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Emergency Response Draft - Ready for Dispatcher Approval

**Downtown outage:** 1,247 customers including 2 hospitals. Primary feeder failure at Substation 7B.

| Crew | Location | ETA | Assignment |
|------|----------|-----|------------|
| E-7 | Staging area | 8 min | Primary response |
| F-8 | 2.4 mi away | 11 min | Assessment |
| A-1 | Redirected from Industrial Way | 18 min | Backup power |

**Customer Impact:**
- Hospitals: Backup generators active (safe)
- Revenue at risk: $26,140/hour
- Target restoration: 2.5 hours max

**Adjusted Schedule:**
- A-1's Industrial Way switchgear maint job postponed (customer notice drafted)
- Remaining 11 jobs unaffected

> Dispatcher approval and established emergency procedures are mandatory. No crew was dispatched and no customer notification was sent.
```

### FIELD_SERVICE_DISPATCH-05 — Control Room Operator — `incident_status`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-05",
  "persona": "Control Room Operator",
  "operation": "incident_status",
  "prompt": "Yes, give me live updates and customer impact",
  "canonical_kwargs": {
    "operation": "incident_status"
  },
  "must_include": [
    "Phase B insulator",
    "$12,400",
    "93 min"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Live Status - 16 Minutes Since Outage

**Crew E-7 - On site, cause confirmed**
- Wildlife contact on Phase B insulator
- Rerouting through backup feeder
- ETA restoration: 45 minutes

**Crew F-8 - Downtown assessment complete**
- 3 transformers checked, all intact
- Safe to re-energize

**Customer Breakdown:**

| Segment | Impact/Hr | Priority |
|---------|-----------|----------|
| Hospitals | $12,400 | Critical |
| Commercial | $8,700 | High |
| Retail | $4,200 | Medium |
| Residential | $840 | Standard |
| **Total** | **$26,140** | |

**Timeline:**
- Hospitals: 48 min
- Commercial: 63 min
- Full restoration: 93 min

> Synthetic status snapshot (not live telemetry). Customer updates are drafts for dispatcher approval.
```

### FIELD_SERVICE_DISPATCH-06 — Reliability Engineer — `post_incident_review`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-06",
  "persona": "Reliability Engineer",
  "operation": "post_incident_review",
  "prompt": "The outage is resolved. Show me the post-incident review and how we prevent the next one.",
  "canonical_kwargs": {
    "operation": "post_incident_review"
  },
  "must_include": [
    "87 Minutes",
    "785% ROI",
    "Substation 7B"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Outage Resolved - All Customers Restored in 87 Minutes

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Response time | <15 min | 8 min | Beat |
| Restoration | <120 min | 87 min | Beat |
| First-time fix | 95% | 100% | Beat |

**Value Protected:** $37,870 revenue vs $4,280 response cost = 785% ROI

**Prevention Actions:**
- Immediate (30 days):
  - Wildlife mitigation at Substation 7B ($8,400, 78% risk reduction)
  - Vegetation management expansion ($12,200/yr, prevents 3-4 outages)
- Long-term (6-12 months):
  - IoT sensors on 6 critical feeders ($28,500, 15-30 min early warning)
  - Smart grid automation ($340K, payback in 4.6 months)

Next: generate work orders for the prevention actions.

> Review summary only. No work order, budget, or field action was created or approved.
[FieldServiceDispatchAgent] # Prevention Work Orders (Drafts) and Monthly Operations Report

**Work orders ready for you to create:**

| Work Order | Action | Owner | Due |
|------------|--------|-------|-----|
| WO-2847 | Wildlife mitigation | Crew E-7 | next week |
| WO-2848 | Vegetation management | Contractor | 15 days |
| WO-2849 | IoT sensor deployment | Engineering | 30 days |

**Monthly Operations Summary:**

| Metric | This Month | Last Month |
|--------|------------|------------|
| Emergency response | 8 min avg | 14 min |
| First-time fix | 96% | 89% |
| Customer satisfaction | 91.8% | - |
| Fuel costs | $18,400 | $24,700 |

**Cost Savings:** $29,260/month through route optimization (fuel $6,300 + overtime $22,960)
**Revenue Protected:** $270,200 (4 emergency responses)

> Work orders are drafts: none was created or assigned. Report figures are synthetic.
```

### FIELD_SERVICE_DISPATCH-07 — Operations Analyst — `work_orders_report`

```json
{
  "case_id": "FIELD_SERVICE_DISPATCH-07",
  "persona": "Operations Analyst",
  "operation": "work_orders_report",
  "prompt": "Yes, create the work orders and show me the monthly operations report",
  "canonical_kwargs": {
    "operation": "work_orders_report"
  },
  "must_include": [
    "WO-2847",
    "$29,260/month",
    "none was created"
  ],
  "expected_agent": "FieldServiceDispatchAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[FieldServiceDispatchAgent] # Prevention Work Orders (Drafts) and Monthly Operations Report

**Work orders ready for you to create:**

| Work Order | Action | Owner | Due |
|------------|--------|-------|-----|
| WO-2847 | Wildlife mitigation | Crew E-7 | next week |
| WO-2848 | Vegetation management | Contractor | 15 days |
| WO-2849 | IoT sensor deployment | Engineering | 30 days |

**Monthly Operations Summary:**

| Metric | This Month | Last Month |
|--------|------------|------------|
| Emergency response | 8 min avg | 14 min |
| First-time fix | 96% | 89% |
| Customer satisfaction | 91.8% | - |
| Fuel costs | $18,400 | $24,700 |

**Cost Savings:** $29,260/month through route optimization (fuel $6,300 + overtime $22,960)
**Revenue Protected:** $270,200 (4 emergency responses)

> Work orders are drafts: none was created or assigned. Report figures are synthetic.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
