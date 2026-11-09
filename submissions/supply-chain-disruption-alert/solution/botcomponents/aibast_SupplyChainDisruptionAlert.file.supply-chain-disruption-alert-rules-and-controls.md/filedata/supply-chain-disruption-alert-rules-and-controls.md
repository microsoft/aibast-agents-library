# Supply Chain Disruption Alert Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. `disruption_dashboard` emits `# Supply Chain Disruption Dashboard`; active revenue at risk is the sum of active event impacts and affected routes are unique across active events.
2. Risk labels are HIGH at 0.70 or above, MEDIUM from 0.40 through 0.69, and LOW below 0.40.
3. `risk_assessment` may filter by exact route ID and emits the deterministic overall and factor scores without predicting supplier default.
4. `mitigation_plan` may filter by exact disruption ID. Total mitigation investment counts each active disruption type once, then lists the exact immediate, short-term, and long-term playbook actions.
5. `supplier_alternatives` may filter by exact category. Fastest due-diligence candidate is the supplier with minimum lead_time_days; it is not an activation or award.
6. No supplier is contacted, qualified, selected, contracted, or activated. No purchase order, shipment, route, customer commitment, or inventory position is changed.
<!-- walkthrough-rules -->
7. `root_cause_analysis` emits `# Root Cause Analysis: Northwest Stores`; SKUs affected is the sum of `AFFECTED_CATEGORIES` (143) and the store count is `NORTHWEST_STORES` (12).
8. `emergency_options` lists `EMERGENCY_OPTIONS`; ROI is recovery divided by cost, rounded (47,000 / 15,600 = 3:1). The recommendation adds the `EXPANSION` stores for their cost ($8,900).
9. `transfer_plan`, `incident_report` and `incident_summary` total cost = Option A cost + expansion cost ($24,500), recovery = Option A recovery + expansion recovery ($78,000), net = recovery − cost ($53,500).
10. `transfer_plan` and `incident_summary` are ready-to-release drafts: no truck is dispatched and no Teams notice, SMS or report is sent. `recovery_plan` shows a synthetic tracking snapshot, not a live feed.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### SUPPLY_CHAIN_DISRUPTION_ALERT-01 — Customer Fulfillment Lead — `disruption_dashboard`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-01",
  "persona": "Customer Fulfillment Lead",
  "operation": "disruption_dashboard",
  "prompt": "Which active disruption has the largest modeled impact and what is affected?",
  "canonical_kwargs": {
    "operation": "disruption_dashboard"
  },
  "must_include": [
    "DISR-002",
    "$3,800,000.00",
    "SKU-1010"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Supply Chain Disruption Dashboard

**Active Disruptions:** 3
**Routes Affected:** 3 of 5
**Total Revenue at Risk:** $6,670,000.00

## Active Disruption Events

| ID | Title | Type | Severity | Delay | Revenue Impact | Resolution ETA |
|----|-------|------|----------|-------|----------------|----------------|
| DISR-001 | Port Congestion — Los Angeles/Long Beach | port congestion | HIGH | +8d | $2,150,000.00 | 2026-03-28 |
| DISR-002 | Typhoon Disruption — South China Sea | weather event | CRITICAL | +12d | $3,800,000.00 | 2026-03-20 |
| DISR-003 | EU Customs Regulation Change | regulatory | MEDIUM | +5d | $720,000.00 | 2026-04-15 |

## Route Status Overview

| Route | Origin | Destination | Mode | Status | Reliability |
|-------|--------|-------------|------|--------|-------------|
| Asia-Pacific Primary | Shenzhen, China | Los Angeles, CA | ocean freight | DISRUPTED | 82% |
| European Apparel Route | Porto, Portugal | Newark, NJ | ocean freight | AT RISK | 91% |
| West Coast to Midwest | Los Angeles, CA | Chicago, IL | intermodal rail | NORMAL | 95% |
| Central America Footwear | Leon, Mexico | Dallas, TX | trucking | NORMAL | 93% |
| Southeast Asia Textiles | Ho Chi Minh City, Vietnam | Savannah, GA | ocean freight | DISRUPTED | 78% |

### DISR-001: Port Congestion — Los Angeles/Long Beach

Severe vessel queue at LA/LB ports due to labor slowdown and equipment shortages. Average vessel wait time is 6 days.

**Affected SKUs:** SKU-1002, SKU-1004, SKU-1006, SKU-1008
**Affected Routes:** RT-APAC-01

### DISR-002: Typhoon Disruption — South China Sea

Typhoon Mirinae forcing rerouting of vessels through northern Pacific corridor. Multiple sailings cancelled or delayed.

**Affected SKUs:** SKU-1002, SKU-1003, SKU-1004, SKU-1006, SKU-1008, SKU-1010
**Affected Routes:** RT-APAC-01, RT-SEASIA-01

### DISR-003: EU Customs Regulation Change

New EU sustainability documentation requirements adding processing time at origin. Additional compliance certificates needed for textiles.

**Affected SKUs:** SKU-1001, SKU-1003
**Affected Routes:** RT-EURO-01

> Synthetic monitoring snapshot. Validate live supplier, logistics, order, and customer data before action.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-02 — Supply Chain Planner — `risk_assessment`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-02",
  "persona": "Supply Chain Planner",
  "operation": "risk_assessment",
  "prompt": "Why is RT-APAC-01 high risk?",
  "canonical_kwargs": {
    "operation": "risk_assessment",
    "route_id": "RT-APAC-01"
  },
  "must_include": [
    "Asia-Pacific Primary",
    "HIGH",
    "Weather"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Supply Chain Risk Assessment

## Risk Score Matrix

| Route | Overall | Geopolitical | Weather | Infrastructure | Labor | Regulatory | Financial |
|-------|---------|--------------|---------|----------------|-------|------------|-----------|
| Asia-Pacific Primary | **0.78** (HIGH) | 0.65 | 0.82 | 0.70 | 0.75 | 0.40 | 0.35 |

## Risk Level Distribution

- **HIGH risk routes:** 1
- **MEDIUM risk routes:** 0
- **LOW risk routes:** 0

## Highest Risk Factors

- **Weather:** avg 0.82, peak 0.82
- **Labor:** avg 0.75, peak 0.75
- **Infrastructure:** avg 0.70, peak 0.70
- **Geopolitical:** avg 0.65, peak 0.65
- **Regulatory:** avg 0.40, peak 0.40
- **Financial:** avg 0.35, peak 0.35

> Decision-support score only; it is not a supplier default prediction or authorization to change supply.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-03 — Operations Leader — `mitigation_plan`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-03",
  "persona": "Operations Leader",
  "operation": "mitigation_plan",
  "prompt": "Draft a DISR-002 mitigation scenario without rerouting or moving inventory.",
  "canonical_kwargs": {
    "operation": "mitigation_plan",
    "disruption_id": "DISR-002"
  },
  "must_include": [
    "DISR-002",
    "Draft Disruption Mitigation Scenario",
    "no purchase order"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Draft Disruption Mitigation Scenario

**Estimated Total Mitigation Investment:** $520,000.00

## DISR-002: Typhoon Disruption — South China Sea
**Playbook:** Weather Event Mitigation
**Expected Risk Reduction:** 55%
**Mitigation Cost:** $520,000.00

### Proposed immediate actions (0-48 hours)
1. Consider: Activate emergency inventory reserves at regional warehouses
1. Consider: Reroute in-transit vessels through safe corridors
1. Consider: Expedite air freight for high-priority SKUs with less than 7 days supply

### Short-Term Actions (1-2 weeks)
1. Shift demand to in-stock alternative products via merchandising
1. Enable backorder with guaranteed delivery dates for affected items
1. Communicate proactively with B2B customers on revised timelines

### Long-Term Actions (1-3 months)
1. Integrate real-time weather monitoring into planning systems
1. Build seasonal safety stock buffers for typhoon/hurricane seasons
1. Qualify backup suppliers in geographically diverse regions

> Approval gate: no purchase order, supplier, shipment, route, or inventory position has been changed.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-04 — Procurement Manager — `supplier_alternatives`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-04",
  "persona": "Procurement Manager",
  "operation": "supplier_alternatives",
  "prompt": "Show Electronics alternatives without activating a supplier.",
  "canonical_kwargs": {
    "operation": "supplier_alternatives",
    "category": "Electronics"
  },
  "must_include": [
    "TechSource Taiwan",
    "due diligence",
    "human approval"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Alternative Supplier Directory

## Electronics
**Fastest candidate for due diligence:** KoreanTech Partners — 19d

| Supplier | Location | Lead Time | Quality | Capacity/Mo | Price Premium | MOQ |
|----------|----------|-----------|---------|-------------|---------------|-----|
| TechSource Taiwan | Taipei, Taiwan | 21d | 4.5/5.0 | 15,000 | +8.0% | 500 |
| KoreanTech Partners | Incheon, South Korea | 19d | 4.7/5.0 | 10,000 | +12.0% | 300 |

**Certifications:**
- TechSource Taiwan: ISO 9001, ISO 14001
- KoreanTech Partners: ISO 9001, IATF 16949

**Total Qualified Alternatives:** 8 suppliers across 5 categories

> Synthetic candidates only. Qualification, contracting, sourcing, and inventory movement require human approval and authenticated systems.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-05 — Regional Retail Manager — `root_cause_analysis`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-05",
  "persona": "Regional Retail Manager",
  "operation": "root_cause_analysis",
  "prompt": "I'm seeing unusual inventory movement at our Northwest stores. Can you help me understand what's happening?",
  "canonical_kwargs": {
    "operation": "root_cause_analysis"
  },
  "must_include": [
    "Portland DC",
    "143 products",
    "$84,300/week"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Root Cause Analysis: Northwest Stores

I've detected a supply chain disruption at Portland DC causing cascading stockouts across 12 Northwest stores (incident DISR-PDX-01).

| Issue | Impact | Status |
|---|---|---|
| Portland DC delay | 3-day backup | Active |
| Seattle Flagship | 47% stockout | Critical |
| SKUs affected | 143 products | High |
| Lost revenue | $84,300/week | Escalating |

**Affected Categories:**
- Electronics: 42 SKUs out
- Apparel: 38 SKUs out
- Home goods: 31 SKUs out
- Sporting: 32 SKUs out

**Customer Impact:** 37 complaints (up 280% vs baseline), social media mentions spiking

**Stores affected (stockout %):** Seattle Flagship 47%; Portland South 31%; Tacoma Mall 29%; Bellevue Square 27%; Olympia Center 24%; Spokane Valley 22%; Portland Pearl 18%; Eugene Valley 16%; Salem Center 15%; Everett Commons 14%; Vancouver Plaza 12%; Boise Towne 11%

Source: [D365 Supply Chain + Store POS]

Next step: should I show the emergency response options?

> Synthetic incident snapshot. Draft for the operations owner: no truck, transfer, order, notification, SMS or report has been dispatched or sent.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-06 — Regional Operations Director — `emergency_options`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-06",
  "persona": "Regional Operations Director",
  "operation": "emergency_options",
  "prompt": "What are our emergency options and costs?",
  "canonical_kwargs": {
    "operation": "emergency_options"
  },
  "must_include": [
    "Denver DC Emergency Transfer",
    "$15,600",
    "3:1"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Emergency Response Options

I've identified two response scenarios - emergency transfer from Denver DC offers the best ROI.

## Option A: Denver DC Emergency Transfer
- Timeline: 36 hours to Seattle
- Top 80 priority SKUs delivered
- Cost: $15,600 (truck + handling)
- Revenue recovery: $47,000 (5-day window)
- ROI: 3:1

## Option B: Partial Fill + Wait
- Timeline: 2 days for Portland recovery
- Only 40% of SKUs restored
- Cost: $0 (no added freight)
- Revenue loss: $127,000 additional

**Recommended:** Option A + expand to 5 additional high-impact stores for $8,900 more (Portland South, Tacoma Mall, Bellevue Square, Olympia Center, Spokane Valley).

Source: [Freight Networks + Sales Forecasting]

Next step: approve the Denver transfer?

> Synthetic incident snapshot. Draft for the operations owner: no truck, transfer, order, notification, SMS or report has been dispatched or sent.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-07 — Store Operations Manager — `transfer_plan`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-07",
  "persona": "Store Operations Manager",
  "operation": "transfer_plan",
  "prompt": "Approved. Execute both Seattle and the 5 additional stores.",
  "canonical_kwargs": {
    "operation": "transfer_plan"
  },
  "must_include": [
    "ready to release",
    "$24,500",
    "$78,000"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Emergency Transfer Execution Plan (ready to release)

Emergency transfer from Denver DC is ready for you to release; confirm truck loading with Lisa Park, Denver DC operations manager. Nothing has been dispatched yet.

## Seattle Flagship
- Departure: Tonight 6 PM
- Arrival: Friday 10 AM
- 80 SKUs (electronics priority)
- Cost $15,600, recovery $47,000

## 5 Additional Stores
- Portland South, Tacoma Mall, Bellevue Square, Olympia Center, Spokane Valley
- Arrival: Saturday morning
- 60 SKUs each (highest velocity items)
- Cost $8,900, recovery $31,000

## Logistics Coordination (drafts ready for you to send)
- Teams notice to the 6 store managers: drafted, not sent
- Receiving staff schedule for Friday and Saturday: drafted, not sent
- Restocking plans for store tablets: drafted, not sent
- Customer SMS notification for back-in-stock items: drafted, not sent

**Investment:** $24,500 total | **Recovery:** $78,000 projected

Source: [Freight Management + Store Operations]

Next step: once released, want the live tracking view?

> Synthetic incident snapshot. Draft for the operations owner: no truck, transfer, order, notification, SMS or report has been dispatched or sent.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-08 — Distribution Center Manager — `recovery_plan`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-08",
  "persona": "Distribution Center Manager",
  "operation": "recovery_plan",
  "prompt": "Activate tracking and show me the Portland DC recovery plan.",
  "canonical_kwargs": {
    "operation": "recovery_plan"
  },
  "must_include": [
    "Conveyor repair",
    "340 pending orders",
    "Friday noon"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Shipment Tracking and Portland DC Recovery Plan

Portland DC root cause identified as equipment failure (main conveyor) - recovery plan accelerated.

**Shipment Status (synthetic tracking snapshot after release):** Denver truck departed 6:04 PM | ETA Seattle: Friday 9:47 AM | On schedule

## Portland DC Recovery

| Action | Status | Complete By |
|---|---|---|
| Conveyor repair | In progress | Thursday 8 PM |
| Backlog processing | Staged | Friday 6 AM |
| Normal ops resume | Planned | Friday noon |

## Backlog Clearance
- 340 pending orders queued
- Priority: Seattle + affected stores first
- Full clearance: Saturday end of day

**Prevention:** Backup conveyor system recommended ($145K investment, 48-hour install)

Source: [IoT Sensors + DC Operations + Maintenance]

Next step: generate the executive incident report?

> Synthetic incident snapshot. Draft for the operations owner: no truck, transfer, order, notification, SMS or report has been dispatched or sent.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-09 — Finance Business Partner — `incident_report`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-09",
  "persona": "Finance Business Partner",
  "operation": "incident_report",
  "prompt": "Create the executive report with financial impact.",
  "canonical_kwargs": {
    "operation": "incident_report"
  },
  "must_include": [
    "Executive Incident Report",
    "$53,500",
    "47 minutes"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Executive Incident Report (draft)

Executive incident report ready showing $78K revenue recovery from $24.5K investment.

**Incident Summary:** Portland DC equipment failure (main conveyor), 3-day backup, 12 stores affected.

## Financial Impact

| Metric | Value |
|---|---|
| Revenue at risk | $84,300 |
| Emergency response cost | $24,500 |
| Revenue recovered | $78,000 |
| Net value protected | $53,500 |

## Response Performance
- Detection to action: 47 minutes
- Alternative DC activation: 36 hours
- Stores back to 95% inventory: 3 days
- Customer satisfaction maintained: 4.2/5.0

## Lessons Learned
- Backup conveyor needed ($145K)
- Multi-DC sourcing rules updated
- Monitoring alerts tuned (reduce response time by 18 minutes)

**3-Year Prevention Value:** $340K avoided losses vs $145K investment

Source: [Financial Analysis + Operations Data]

Next step: share with the executive team? The report is a draft ready for you to share.

> Synthetic incident snapshot. Draft for the operations owner: no truck, transfer, order, notification, SMS or report has been dispatched or sent.
```

### SUPPLY_CHAIN_DISRUPTION_ALERT-10 — Supply Chain Director — `incident_summary`

```json
{
  "case_id": "SUPPLY_CHAIN_DISRUPTION_ALERT-10",
  "persona": "Supply Chain Director",
  "operation": "incident_summary",
  "prompt": "Distribute the report and summarize what we accomplished.",
  "canonical_kwargs": {
    "operation": "incident_summary"
  },
  "must_include": [
    "Crisis Response Summary",
    "not sent",
    "all 47 stores"
  ],
  "expected_agent": "supply-chain-disruption-alert-agent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Crisis Response Summary

The report package is ready for you to distribute to leadership (not sent). Here's what we accomplished:

- Detected disruption - Portland DC 3-day delay, 12 stores affected, $84K at risk
- Analyzed options - Denver transfer 3:1 ROI vs wait-and-lose scenario
- Prepared emergency plan - 6 stores, 36-hour delivery, $24.5K investment
- Coordinated operations - store managers, receiving crews, customer comms (drafts)
- Monitored recovery - shipment tracking, Portland DC repair timeline
- Prevention planning - $145K backup system, $340K 3-year value

**Value Delivered:** $53,500 net recovery from rapid response

**Active Now:** monitoring on all 47 stores, Portland DC back online Friday noon, emergency protocols updated

Your supply chain now has 47-minute detection-to-action capability.

Distribution list (draft): regional leadership, operations, finance, store managers.

Source: [All Connected Systems]

> Synthetic incident snapshot. Draft for the operations owner: no truck, transfer, order, notification, SMS or report has been dispatched or sent.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
