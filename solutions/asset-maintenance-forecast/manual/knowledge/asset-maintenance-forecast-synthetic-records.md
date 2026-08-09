# Asset Maintenance Forecast Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/asset_maintenance_forecast_stack/asset_maintenance_forecast_agent.py`
- Captured source SHA-256: `6e0e25ffee2c9ddb54c1457acf87b7cc9ebcdaf357397fa2d533e01dc565fd31`
- Locked case file: `tests/demo_cases/asset-maintenance-forecast.json`
- Locked case SHA-256: `eadc4fc1b187ca684b2022c1d8115eae2a1839748ac9f1d6935654697bc5a354`
- Strict isolation: `true`

## Record index

- `ASSETS`
- `BUDGET_RATES`

## ASSETS

```json
{
  "AST-T001": {
    "name": "Wind Turbine Alpha-7",
    "type": "wind_turbine",
    "location": "Sweetwater Wind Farm, TX",
    "installed_year": 2016,
    "age_years": 10,
    "capacity_mw": 3.2,
    "condition_score": 68,
    "last_major_service": "2025-06-15",
    "operating_hours": 72480,
    "failure_rate_annual_pct": 4.2,
    "maintenance_history": [
      {
        "date": "2025-06-15",
        "type": "major",
        "cost": 48000,
        "description": "Gearbox bearing replacement"
      },
      {
        "date": "2025-11-20",
        "type": "minor",
        "cost": 8200,
        "description": "Blade pitch calibration"
      },
      {
        "date": "2026-01-10",
        "type": "inspection",
        "cost": 3500,
        "description": "Annual structural inspection"
      }
    ],
    "predicted_next_failure": "2026-08-15",
    "replacement_cost": 2400000
  },
  "AST-X002": {
    "name": "Substation Transformer B-12",
    "type": "transformer",
    "location": "Ridgeline Substation, CO",
    "installed_year": 2008,
    "age_years": 18,
    "capacity_mw": 120.0,
    "condition_score": 42,
    "last_major_service": "2024-09-22",
    "operating_hours": 148920,
    "failure_rate_annual_pct": 8.7,
    "maintenance_history": [
      {
        "date": "2024-09-22",
        "type": "major",
        "cost": 125000,
        "description": "Oil filtration and bushing replacement"
      },
      {
        "date": "2025-04-11",
        "type": "minor",
        "cost": 18500,
        "description": "Cooling fan motor replacement"
      },
      {
        "date": "2025-12-05",
        "type": "inspection",
        "cost": 6200,
        "description": "DGA oil analysis - elevated acetylene"
      }
    ],
    "predicted_next_failure": "2026-05-01",
    "replacement_cost": 4800000
  },
  "AST-P003": {
    "name": "Gas Pipeline Segment NE-14",
    "type": "pipeline",
    "location": "Northeast Corridor, PA",
    "installed_year": 2012,
    "age_years": 14,
    "capacity_mw": 0,
    "condition_score": 75,
    "last_major_service": "2025-08-30",
    "operating_hours": 0,
    "failure_rate_annual_pct": 1.8,
    "maintenance_history": [
      {
        "date": "2025-08-30",
        "type": "major",
        "cost": 210000,
        "description": "Corrosion remediation and recoating"
      },
      {
        "date": "2025-11-15",
        "type": "inspection",
        "cost": 15000,
        "description": "Inline inspection pig run"
      },
      {
        "date": "2026-02-20",
        "type": "minor",
        "cost": 9800,
        "description": "Valve actuator servicing"
      }
    ],
    "predicted_next_failure": "2027-03-01",
    "replacement_cost": 12000000
  },
  "AST-T004": {
    "name": "Gas Turbine GT-3A",
    "type": "gas_turbine",
    "location": "Riverside Generating Station, CA",
    "installed_year": 2019,
    "age_years": 7,
    "capacity_mw": 85.0,
    "condition_score": 88,
    "last_major_service": "2025-10-12",
    "operating_hours": 38200,
    "failure_rate_annual_pct": 1.2,
    "maintenance_history": [
      {
        "date": "2025-10-12",
        "type": "major",
        "cost": 340000,
        "description": "Hot gas path inspection"
      },
      {
        "date": "2026-01-28",
        "type": "minor",
        "cost": 22000,
        "description": "Fuel nozzle cleaning"
      }
    ],
    "predicted_next_failure": "2027-10-01",
    "replacement_cost": 18000000
  }
}
```

## BUDGET_RATES

```json
{
  "major": {
    "wind_turbine": 52000,
    "transformer": 135000,
    "pipeline": 225000,
    "gas_turbine": 360000
  },
  "minor": {
    "wind_turbine": 9000,
    "transformer": 20000,
    "pipeline": 12000,
    "gas_turbine": 25000
  },
  "inspection": {
    "wind_turbine": 4000,
    "transformer": 7000,
    "pipeline": 16000,
    "gas_turbine": 15000
  }
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
