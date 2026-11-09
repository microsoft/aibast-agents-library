# Asset Maintenance Forecast Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/asset_maintenance_forecast_stack/asset_maintenance_forecast_agent.py`
- Captured source SHA-256: `08edd95089a4da0c81b3ec203a72424b30aeb3b80ff5110611f4102343787c09`
- Locked case file: `tests/demo_cases/asset-maintenance-forecast.json`
- Locked case SHA-256: `7108dd74335db510810c4d60dca170506029c0327a3c3ff0754e45e926544965`
- Strict isolation: `true`

## Record index

- `FLEET`
- `ASSETS`
- `MOBILIZATION`
- `BUNDLE_WINDOW`

## FLEET

```json
{
  "site": "wind farm",
  "turbines": 45,
  "model": "GE 2.5MW",
  "telemetry": "Azure IoT Hub",
  "other_units_offline": 1,
  "other_offline_note": "Unit 41 in a scheduled blade inspection"
}
```

## ASSETS

```json
{
  "Unit 12": {
    "risk_score": 8.7,
    "risk_label": "Failure Imminent",
    "failure_mode": "Main bearing end-of-life wear",
    "repair": "bearing",
    "days_to_failure": "18-30",
    "emergency_cost": 227000,
    "labor_cost": 30250,
    "parts_cost": 28000,
    "duration_days": 3,
    "crew": "Crew A",
    "dates": "March 18-20"
  },
  "Unit 23": {
    "risk_score": 6.2,
    "risk_label": "Elevated",
    "failure_mode": "Gearbox oil contamination",
    "repair": "oil",
    "days_to_failure": "45",
    "emergency_cost": 98000,
    "labor_cost": 1500,
    "parts_cost": 5000,
    "duration_days": 2,
    "crew": "Crew A",
    "dates": "March 21-22"
  },
  "Unit 37": {
    "risk_score": 3.8,
    "risk_label": "Watch",
    "failure_mode": "Generator slip ring wear",
    "repair": "slip ring",
    "days_to_failure": "90",
    "emergency_cost": 41000,
    "labor_cost": 1000,
    "parts_cost": 3000,
    "duration_days": 1,
    "crew": "Crew B",
    "dates": "March 22"
  }
}
```

## MOBILIZATION

```json
{
  "crane_per_job": 6000,
  "crew_travel_per_job": 850,
  "bulk_parts_discount_pct": 15
}
```

## BUNDLE_WINDOW

```json
{
  "dates": "March 18-22",
  "days": 5,
  "forecast": "low-wind forecast"
}
```

## Derived planning figures (computed from the records above)

| Turbine | Risk score | Status | Failure mode | Days to failure | Labor | Parts | Stand-alone planned repair | Emergency cost |
|---|---|---|---|---|---|---|---|---|
| Unit 12 | 8.7/10 (Failure Imminent) | CRITICAL | Main bearing end-of-life wear | 18-30 | $30,250 | $28,000 | $65,100 | $227,000 |
| Unit 23 | 6.2/10 | WARNING | Gearbox oil contamination | 45 | $1,500 | $5,000 | $13,350 | $98,000 |
| Unit 37 | 3.8/10 | WATCH | Generator slip ring wear | 90 | $1,000 | $3,000 | $10,850 | $41,000 |

- Stand-alone planned repair = labor + parts + crane $6,000 + crew travel $850.
- Separate Jobs: $89,300. Bundled Job (one crane, one crew trip, 15% bulk parts discount on $36,000 of parts): $70,200.
- Savings $19,100 = single crane rental vs 3 separate $12,000 + shared crew travel $1,700 + bulk parts discount $5,400.
- Bundle window: March 18-22 (5 days, low-wind forecast). Crew A: Unit 12 bearing March 18-20, Unit 23 oil March 21-22;
  Crew B: Unit 37 slip ring March 22.
- ROI Summary: investment $70,200; avoided failure $161,900 (= $227,000 - $65,100); bundling savings $19,100; total value
  $181,000; ROI 258%.
- Fleet availability: 45 GE 2.5MW turbines; (45 - 3) / 45 = 93.3% today -> (45 - 1) / 45 = 97.8% after the plan (Unit 41
  remains in a scheduled blade inspection).
- Opening analysis wording: "Analyzing your 45 GE 2.5MW turbines through Azure IoT Hub." Critical Alert - Unit 12: $227K
  emergency cost vs $65K planned repair; recommendation: bundle all 3 units during the March 18-22 low-wind window, save
  $19K on mobilization, avoid $227K catastrophic failure, total investment $70K.

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
