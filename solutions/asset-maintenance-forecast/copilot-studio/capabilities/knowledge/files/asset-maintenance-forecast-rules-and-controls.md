# Asset Maintenance Forecast Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. The default scope is the whole synthetic wind farm: 45 GE 2.5MW turbines with three flagged units (Unit 12, Unit 23, Unit 37). An asset_id such as `Unit 12` or `12` filters to that turbine; an unknown name returns no invented record.
2. `maintenance_forecast` emits `# Maintenance Forecast`, a critical alert for the highest risk score, additional risks in descending score, and (fleet scope) the recommendation to bundle all three units in the March 18-22 low-wind window.
3. `asset_health` labels CRITICAL at a risk score of 8.0 or above, WARNING from 5.0, and WATCH below 5.0.
4. A stand-alone planned repair = labor + parts + one crane ($6,000) + one crew travel ($850). Unit 12 is $65,100, Unit 23 $13,350, Unit 37 $10,850; separate jobs total $89,300.
5. The bundled job uses one crane and one crew trip and a 15% bulk parts discount on $36,000 of parts: $70,200; savings $19,100 = crane $12,000 + travel $1,700 + parts $5,400.
6. Avoided failure = Unit 12 emergency cost $227,000 - planned $65,100 = $161,900; total value $181,000; ROI = 181,000 / 70,200 = 258%. Fleet availability (45 - 3) / 45 = 93.3% -> (45 - 1) / 45 = 97.8% (Unit 41 stays in a scheduled blade inspection).
7. Modeled dates and costs are planning evidence only. No work order, schedule, crew assignment, operating authorization, or field instruction is created.

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
  "prompt": "I need immediate analysis on our wind farm turbines",
  "canonical_kwargs": {
    "operation": "maintenance_forecast"
  },
  "must_include": [
    "Unit 12",
    "8.7/10",
    "March 18-22"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Maintenance Forecast

Analyzing your 45 GE 2.5MW turbines through Azure IoT Hub (synthetic telemetry snapshot).

## Critical Alert - Unit 12
- **Risk Score:** 8.7/10 (Failure Imminent)
- **Issue:** Main bearing end-of-life wear
- **Timeline:** 18-30 days to failure
- **Impact:** $227K emergency cost vs $65K planned repair

## Additional Risks
- Unit 23 (6.2/10) - Gearbox oil contamination, 45 days
- Unit 37 (3.8/10) - Generator slip ring wear, 90 days

**Recommendation:** Bundle all 3 units during the March 18-22 low-wind window
- Save $19K on mobilization
- Avoid $227K catastrophic failure
- Total investment: $70K

**Next step:** See the detailed bundled maintenance plan?

> Synthetic planning evidence only. Confirm against live telemetry and engineering review before maintenance or field action.
```

### ASSET_MAINTENANCE_FORECAST-02 — Reliability Engineer — `asset_health`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-02",
  "persona": "Reliability Engineer",
  "operation": "asset_health",
  "prompt": "Show me the weakest turbine condition and whether this is an operating authorization.",
  "canonical_kwargs": {
    "operation": "asset_health"
  },
  "must_include": [
    "Unit 12",
    "CRITICAL",
    "not a safety determination"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Asset Health Dashboard

**Fleet:** 45 GE 2.5MW turbines; 3 flagged by the synthetic risk model.

| Turbine | Risk Score | Status | Failure Mode | Days to Failure |
|---------|-----------|--------|--------------|-----------------|
| Unit 12 | 8.7/10 | CRITICAL | Main bearing end-of-life wear | 18-30 |
| Unit 23 | 6.2/10 | WARNING | Gearbox oil contamination | 45 |
| Unit 37 | 3.8/10 | WATCH | Generator slip ring wear | 90 |

Status rule: CRITICAL at 8.0 or above, WARNING from 5.0, WATCH below 5.0.

> Advisory condition screening only; it is not a safety determination or authorization to operate.
```

### ASSET_MAINTENANCE_FORECAST-03 — Finance Business Partner — `budget_projection`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-03",
  "persona": "Finance Business Partner",
  "operation": "budget_projection",
  "prompt": "What maintenance funding should I reserve for the at-risk turbines?",
  "canonical_kwargs": {
    "operation": "budget_projection"
  },
  "must_include": [
    "$70,200",
    "$227,000",
    "Synthetic planning estimate"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] # Maintenance Budget Projection

| Turbine | Planned Repair (stand-alone) | Emergency Cost if It Fails |
|---------|------------------------------|----------------------------|
| Unit 12 | $65,100 | $227,000 |
| Unit 23 | $13,350 | $98,000 |
| Unit 37 | $10,850 | $41,000 |

**Reserve (bundled plan):** $70,200 versus $89,300 as separate jobs.
**Emergency exposure avoided on Unit 12:** $161,900.

> Synthetic planning estimate; finance and asset owners must validate and approve any commitment.
```

### ASSET_MAINTENANCE_FORECAST-04 — Maintenance Planner — `work_order_plan`

```json
{
  "case_id": "ASSET_MAINTENANCE_FORECAST-04",
  "persona": "Maintenance Planner",
  "operation": "work_order_plan",
  "prompt": "Draft the bundled maintenance plan for the at-risk turbines, but do not create any work orders.",
  "canonical_kwargs": {
    "operation": "work_order_plan"
  },
  "must_include": [
    "Bundled Maintenance Plan",
    "258%",
    "No work order"
  ],
  "expected_agent": "AssetMaintenanceForecastAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[AssetMaintenanceForecastAgent] Bundling saves $19K and maximizes efficiency.

# Bundled Maintenance Plan

**Window:** March 18-22 (5 days, low-wind forecast)
**Work:** Unit 12 bearing (3d) + Unit 23 oil (2d) + Unit 37 slip ring (1d)

| Turbine | Work | Crew | Dates |
|---------|------|------|-------|
| Unit 12 | Main bearing end-of-life wear repair (3d) | Crew A | March 18-20 |
| Unit 23 | Gearbox oil contamination repair (2d) | Crew A | March 21-22 |
| Unit 37 | Generator slip ring wear repair (1d) | Crew B | March 22 |

## Cost Comparison

| Approach | Total Cost | Savings |
|----------|-----------|---------|
| Separate Jobs | $89,300 | - |
| Bundled Job | $70,200 | -$19,100 |

## Savings Sources
- Single crane rental vs 3 separate: -$12K
- Shared crew travel: -$1.7K
- Bulk parts discount (15%): -$5.4K

## ROI Summary
- Investment: $70,200
- Avoided failure: $161,900
- Bundling savings: $19,100
- Total value: $181,000
- ROI: 258%

**Outcome:** Fleet availability 93.3% -> 97.8%

Ready for the asset owner to approve and schedule in Dynamics.

> Synthetic planning evidence only. Draft approval queue only: no work order, schedule, crew assignment, or field instruction has been created in Dynamics or any other system.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
