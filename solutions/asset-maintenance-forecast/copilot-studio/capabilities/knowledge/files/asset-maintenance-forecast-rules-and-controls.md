# Asset Maintenance Forecast Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Filter by exact synthetic asset ID when supplied; an unknown ID returns no invented record.
2. `maintenance_forecast` emits `# Maintenance Forecast`, sorts assets by `predicted_next_failure` ascending, and reports condition score, annual failure rate, predicted failure, and last major service.
3. `asset_health` assigns CRITICAL below 50, WARNING from 50 through 69, and GOOD at 70 or above; the average is the arithmetic mean of selected condition scores.
4. `budget_projection` calculates major + two minor services + one inspection. Assets below 50 receive a 1.5 multiplier rounded to whole dollars; AST-X002 is therefore $273,000.
5. `work_order_plan` sorts by condition. Below 50 adds major service; below 70 adds inspection; every selected asset receives preventive minor maintenance. Priorities increment in emitted order.
6. Modeled dates and costs are planning evidence only. No work order, schedule, crew assignment, operating authorization, or field instruction is created.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### ASSET_MAINTENANCE_FORECAST-01 — Plant Manager — `maintenance_forecast`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-01",
  "persona": "Plant Manager",
  "operation": "maintenance_forecast",
  "prompt": "Which asset is most likely to interrupt operations next, and what evidence supports that?",
  "canonical_kwargs": {
    "operation": "maintenance_forecast",
    "asset_id": "AST-X002"
  },
  "must_include": [
    "Substation Transformer B-12",
    "2026-05-01"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Maintenance Forecast

| Asset | Type | Condition | Failure Rate | Predicted Failure | Last Service |
|-------|------|-----------|-------------|-------------------|--------------|
| Substation Transformer B-12 | transformer | 42 | 8.7% | 2026-05-01 | 2024-09-22 |
| Wind Turbine Alpha-7 | wind_turbine | 68 | 4.2% | 2026-08-15 | 2025-06-15 |
| Gas Pipeline Segment NE-14 | pipeline | 75 | 1.8% | 2027-03-01 | 2025-08-30 |
| Gas Turbine GT-3A | gas_turbine | 88 | 1.2% | 2027-10-01 | 2025-10-12 |

## Action Items
- Substation Transformer B-12 is the highest-priority engineering review candidate.
- Wind Turbine Alpha-7 is approaching its modeled maintenance window.

> Synthetic planning evidence only. Confirm against live telemetry and engineering review before maintenance or field action.
```

### ASSET_MAINTENANCE_FORECAST-02 — Reliability Engineer — `asset_health`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-02",
  "persona": "Reliability Engineer",
  "operation": "asset_health",
  "prompt": "Show me the weakest asset condition and whether this is an operating authorization.",
  "canonical_kwargs": {
    "operation": "asset_health",
    "asset_id": "AST-X002"
  },
  "must_include": [
    "Substation Transformer B-12",
    "CRITICAL",
    "not a safety determination"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Asset Health Dashboard

**Average Condition Score:** 68.2

| Asset | Type | Condition | Status | Age | Operating Hours | Replacement Cost |
|-------|------|-----------|--------|-----|----------------|-----------------|
| Substation Transformer B-12 | transformer | 42 | CRITICAL | 18yr | 148,920 | $4,800,000 |
| Wind Turbine Alpha-7 | wind_turbine | 68 | WARNING | 10yr | 72,480 | $2,400,000 |
| Gas Pipeline Segment NE-14 | pipeline | 75 | GOOD | 14yr | N/A | $12,000,000 |
| Gas Turbine GT-3A | gas_turbine | 88 | GOOD | 7yr | 38,200 | $18,000,000 |

> Advisory condition screening only; it is not a safety determination or authorization to operate.
```

### ASSET_MAINTENANCE_FORECAST-03 — Finance Business Partner — `budget_projection`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-03",
  "persona": "Finance Business Partner",
  "operation": "budget_projection",
  "prompt": "What maintenance funding should I reserve for the transformer risk?",
  "canonical_kwargs": {
    "operation": "budget_projection",
    "asset_id": "AST-X002"
  },
  "must_include": [
    "Substation Transformer B-12",
    "$273,000",
    "Synthetic planning estimate"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Maintenance Budget Projection

**Total Annual Budget:** $1,037,000

| Asset | Type | Condition | Annual Budget | Replacement Cost |
|-------|------|-----------|--------------|-----------------|
| Gas Turbine GT-3A | gas_turbine | 88 | $425,000 | $18,000,000 |
| Substation Transformer B-12 | transformer | 42 | $273,000 | $4,800,000 |
| Gas Pipeline Segment NE-14 | pipeline | 75 | $265,000 | $12,000,000 |
| Wind Turbine Alpha-7 | wind_turbine | 68 | $74,000 | $2,400,000 |

> Synthetic planning estimate; finance and asset owners must validate and approve any commitment.
```

### ASSET_MAINTENANCE_FORECAST-04 — Maintenance Planner — `work_order_plan`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-04",
  "persona": "Maintenance Planner",
  "operation": "work_order_plan",
  "prompt": "Draft the maintenance queue for AST-X002, but do not create any work orders.",
  "canonical_kwargs": {
    "operation": "work_order_plan",
    "asset_id": "AST-X002"
  },
  "must_include": [
    "Substation Transformer B-12",
    "Draft approval queue",
    "No work order"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Work Order Plan

**Total Planned Cost:** $162,000

| Priority | Asset | Work Type | Description | Est. Cost | Target |
|----------|-------|-----------|-------------|----------|--------|
| 1 | Substation Transformer B-12 | MAJOR | Urgent major service - condition score 42 | $135,000 | 2026-Q2 |
| 2 | Substation Transformer B-12 | INSPECTION | Detailed condition assessment required | $7,000 | 2026-Q2 |
| 3 | Substation Transformer B-12 | MINOR | Scheduled preventive maintenance | $20,000 | 2026-Q3 |

> Draft approval queue only. No work order, schedule, crew assignment, or field instruction has been created.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
