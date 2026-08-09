# Supply Chain Disruption Alert Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. `disruption_dashboard` emits `# Supply Chain Disruption Dashboard`; active revenue at risk is the sum of active event impacts and affected routes are unique across active events.
2. Risk labels are HIGH at 0.70 or above, MEDIUM from 0.40 through 0.69, and LOW below 0.40.
3. `risk_assessment` may filter by exact route ID and emits the deterministic overall and factor scores without predicting supplier default.
4. `mitigation_plan` may filter by exact disruption ID. Total mitigation investment counts each active disruption type once, then lists the exact immediate, short-term, and long-term playbook actions.
5. `supplier_alternatives` may filter by exact category. Fastest due-diligence candidate is the supplier with minimum lead_time_days; it is not an activation or award.
6. No supplier is contacted, qualified, selected, contracted, or activated. No purchase order, shipment, route, customer commitment, or inventory position is changed.

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
  "captured_model": "claude-haiku-4.5"
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
  "captured_model": "claude-haiku-4.5"
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

- **HIGH risk routes:** 2
- **MEDIUM risk routes:** 1
- **LOW risk routes:** 2

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
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[supply-chain-disruption-alert-agent] # Draft Disruption Mitigation Scenario

**Estimated Total Mitigation Investment:** $945,000.00

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
  "captured_model": "claude-haiku-4.5"
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

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
