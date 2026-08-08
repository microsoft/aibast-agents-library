# Emissions Tracking Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/emission_tracking_stack/emission_tracking_agent.py`
- Captured source SHA-256: `995b5f93335d3b49c8579ed22cab7882b711958be0b7a5bd75e68103f1a0ed8e`
- Locked case file: `tests/demo_cases/emission-tracking.json`
- Locked case SHA-256: `8a88d29e81eac3487d304354386fd8ab71ba75d7aa3d04ff613d3100de2dd95a`
- Strict isolation: `true`

## Record index

- `FACILITIES`
- `CARBON_OFFSETS`
- `REGULATIONS`

## FACILITIES

```json
{
  "FAC-E01": {
    "name": "Riverside Generating Station",
    "location": "Sacramento, CA",
    "type": "natural_gas_plant",
    "capacity_mw": 340,
    "emissions": {
      "scope_1": {
        "co2_tonnes": 482000,
        "ch4_tonnes": 1240,
        "n2o_tonnes": 85
      },
      "scope_2": {
        "co2_tonnes": 12400,
        "ch4_tonnes": 0,
        "n2o_tonnes": 0
      },
      "scope_3": {
        "co2_tonnes": 38500,
        "ch4_tonnes": 280,
        "n2o_tonnes": 15
      }
    },
    "regulatory_threshold_co2": 500000,
    "reduction_target_pct": 15,
    "baseline_year": 2022,
    "baseline_co2": 545000
  },
  "FAC-E02": {
    "name": "Sweetwater Wind Farm",
    "location": "Nolan County, TX",
    "type": "wind_farm",
    "capacity_mw": 180,
    "emissions": {
      "scope_1": {
        "co2_tonnes": 0,
        "ch4_tonnes": 0,
        "n2o_tonnes": 0
      },
      "scope_2": {
        "co2_tonnes": 3200,
        "ch4_tonnes": 0,
        "n2o_tonnes": 0
      },
      "scope_3": {
        "co2_tonnes": 8400,
        "ch4_tonnes": 12,
        "n2o_tonnes": 2
      }
    },
    "regulatory_threshold_co2": 25000,
    "reduction_target_pct": 5,
    "baseline_year": 2022,
    "baseline_co2": 14200
  },
  "FAC-E03": {
    "name": "Ridgeline Coal Station",
    "location": "Moffat County, CO",
    "type": "coal_plant",
    "capacity_mw": 520,
    "emissions": {
      "scope_1": {
        "co2_tonnes": 1420000,
        "ch4_tonnes": 3800,
        "n2o_tonnes": 420
      },
      "scope_2": {
        "co2_tonnes": 18200,
        "ch4_tonnes": 0,
        "n2o_tonnes": 0
      },
      "scope_3": {
        "co2_tonnes": 95000,
        "ch4_tonnes": 1200,
        "n2o_tonnes": 85
      }
    },
    "regulatory_threshold_co2": 1500000,
    "reduction_target_pct": 30,
    "baseline_year": 2022,
    "baseline_co2": 1780000
  },
  "FAC-E04": {
    "name": "Bayshore Refinery",
    "location": "Beaumont, TX",
    "type": "refinery",
    "capacity_mw": 0,
    "emissions": {
      "scope_1": {
        "co2_tonnes": 890000,
        "ch4_tonnes": 5600,
        "n2o_tonnes": 210
      },
      "scope_2": {
        "co2_tonnes": 42000,
        "ch4_tonnes": 0,
        "n2o_tonnes": 0
      },
      "scope_3": {
        "co2_tonnes": 2100000,
        "ch4_tonnes": 8400,
        "n2o_tonnes": 320
      }
    },
    "regulatory_threshold_co2": 1000000,
    "reduction_target_pct": 20,
    "baseline_year": 2022,
    "baseline_co2": 1050000
  }
}
```

## CARBON_OFFSETS

```json
{
  "OFF-001": {
    "project": "Appalachian Reforestation",
    "type": "forestry",
    "credits_available": 45000,
    "price_per_tonne": 18.5,
    "vintage": 2025,
    "verified_by": "Verra VCS"
  },
  "OFF-002": {
    "project": "Texas Wind REC Bundle",
    "type": "renewable_energy",
    "credits_available": 120000,
    "price_per_tonne": 12.75,
    "vintage": 2026,
    "verified_by": "Green-e"
  },
  "OFF-003": {
    "project": "Montana Methane Capture",
    "type": "methane_capture",
    "credits_available": 28000,
    "price_per_tonne": 24.0,
    "vintage": 2025,
    "verified_by": "ACR"
  },
  "OFF-004": {
    "project": "Iowa Agricultural Soil Carbon",
    "type": "soil_carbon",
    "credits_available": 35000,
    "price_per_tonne": 22.0,
    "vintage": 2026,
    "verified_by": "Gold Standard"
  }
}
```

## REGULATIONS

```json
{
  "EPA_GHGRP": {
    "name": "EPA GHG Reporting Program",
    "threshold_co2": 25000,
    "deadline": "2026-03-31"
  },
  "CA_CAPANDTRADE": {
    "name": "California Cap-and-Trade",
    "threshold_co2": 25000,
    "deadline": "2026-04-01"
  },
  "EPA_NSPS": {
    "name": "EPA New Source Performance Standards",
    "threshold_co2": 0,
    "deadline": "2026-06-30"
  }
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
