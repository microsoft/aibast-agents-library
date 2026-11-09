# Emissions Tracking Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/emission_tracking_stack/emission_tracking_agent.py`
- Captured source SHA-256: `2b162ab6f3e844e31c646402037e7d88890ce3bb02ac66bba1579282d6ebcf26`
- Locked case file: `tests/demo_cases/emission-tracking.json`
- Locked case SHA-256: `550c7776f0f635e010dba1f432cb0026e0133c14438c1b31d46174547d18e027`
- Strict isolation: `true`

## Demo scenario (Northeast facilities, EPA audit in two weeks)

- 12 Northeast facilities, quarterly 47,340 MT CO2e: Scope 1 (Direct) 28,150 MT, 59.4%, +8.2% YoY; Scope 2 (Electricity) 14,680 MT, 31.0%, -12.1%; Scope 3 (Supply Chain) 4,510 MT, 9.5%, +3.4%.
- Within the EPA regional screening threshold (51,450 MT) with an 8% buffer.
- Alert: Boston Hub methane up 18% due to aging infrastructure; trajectory exceeds next-quarter allowances by 340 MT. Action: accelerate leak detection - $85K cost avoids $127K in carbon credits.
- Roadmap (18 months): Phase 1 (Next 90 days) Boston Hub LDAR, $85K, 3,240 MT, payback 10 months; Phase 2 (Months 4-9) CHP + LED, $810K combined, 6,260 MT, 16 months; Phase 3 (Months 10-15) Fleet electrification, $520K, 3,230 MT, 32 months; Phase 4 (Month 16+) Renewable PPA, revenue neutral, 50MW solar. Projected outcome: 27% emissions reduction, top 8% industry performance (synthetic benchmark).

## Record index

- `FACILITIES`
- `PRIOR_YEAR_QUARTER`
- `SCOPE_LABELS`
- `REGIONAL_SCREENING`
- `REDUCTION_ACTIONS`
- `CARBON_OFFSETS`
- `REGULATIONS`

## FACILITIES

```json
{
  "NE-01": {
    "name": "Boston Hub",
    "location": "Boston, MA",
    "region": "Northeast",
    "type": "gas_distribution_hub",
    "quarter_mt_co2e": {
      "scope_1": 4200,
      "scope_2": 1900,
      "scope_3": 600
    },
    "ch4_mt_co2e": 1180,
    "ch4_prior_year_mt_co2e": 1000,
    "alert_cause": "aging infrastructure",
    "next_quarter_allowance_mt": 4300,
    "projected_next_quarter_scope_1_mt": 4640
  },
  "NE-02": {
    "name": "Hartford Generating Station",
    "location": "Hartford, CT",
    "region": "Northeast",
    "type": "natural_gas_plant",
    "quarter_mt_co2e": {
      "scope_1": 5100,
      "scope_2": 1600,
      "scope_3": 520
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 5500,
    "projected_next_quarter_scope_1_mt": 5100
  },
  "NE-03": {
    "name": "Providence Peaker Plant",
    "location": "Providence, RI",
    "region": "Northeast",
    "type": "peaker_plant",
    "quarter_mt_co2e": {
      "scope_1": 3600,
      "scope_2": 900,
      "scope_3": 300
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 4000,
    "projected_next_quarter_scope_1_mt": 3600
  },
  "NE-04": {
    "name": "Portland Fuel Terminal",
    "location": "Portland, ME",
    "region": "Northeast",
    "type": "fuel_terminal",
    "quarter_mt_co2e": {
      "scope_1": 2300,
      "scope_2": 1100,
      "scope_3": 410
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 2700,
    "projected_next_quarter_scope_1_mt": 2300
  },
  "NE-05": {
    "name": "Albany Substation Campus",
    "location": "Albany, NY",
    "region": "Northeast",
    "type": "substation_campus",
    "quarter_mt_co2e": {
      "scope_1": 1900,
      "scope_2": 2400,
      "scope_3": 380
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 2300,
    "projected_next_quarter_scope_1_mt": 1900
  },
  "NE-06": {
    "name": "Burlington Operations Center",
    "location": "Burlington, VT",
    "region": "Northeast",
    "type": "operations_center",
    "quarter_mt_co2e": {
      "scope_1": 800,
      "scope_2": 600,
      "scope_3": 200
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 1200,
    "projected_next_quarter_scope_1_mt": 800
  },
  "NE-07": {
    "name": "Manchester Service Center",
    "location": "Manchester, NH",
    "region": "Northeast",
    "type": "service_center",
    "quarter_mt_co2e": {
      "scope_1": 1150,
      "scope_2": 1000,
      "scope_3": 290
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 1550,
    "projected_next_quarter_scope_1_mt": 1150
  },
  "NE-08": {
    "name": "Worcester Compressor Station",
    "location": "Worcester, MA",
    "region": "Northeast",
    "type": "compressor_station",
    "quarter_mt_co2e": {
      "scope_1": 3400,
      "scope_2": 700,
      "scope_3": 330
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 3800,
    "projected_next_quarter_scope_1_mt": 3400
  },
  "NE-09": {
    "name": "Springfield Fleet Depot",
    "location": "Springfield, MA",
    "region": "Northeast",
    "type": "fleet_depot",
    "quarter_mt_co2e": {
      "scope_1": 1250,
      "scope_2": 1200,
      "scope_3": 360
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 1650,
    "projected_next_quarter_scope_1_mt": 1250
  },
  "NE-10": {
    "name": "New Haven Plant",
    "location": "New Haven, CT",
    "region": "Northeast",
    "type": "natural_gas_plant",
    "quarter_mt_co2e": {
      "scope_1": 2700,
      "scope_2": 1300,
      "scope_3": 450
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 3100,
    "projected_next_quarter_scope_1_mt": 2700
  },
  "NE-11": {
    "name": "Syracuse Operations Center",
    "location": "Syracuse, NY",
    "region": "Northeast",
    "type": "operations_center",
    "quarter_mt_co2e": {
      "scope_1": 950,
      "scope_2": 1280,
      "scope_3": 270
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 1350,
    "projected_next_quarter_scope_1_mt": 950
  },
  "NE-12": {
    "name": "Nashua Fleet Yard",
    "location": "Nashua, NH",
    "region": "Northeast",
    "type": "fleet_depot",
    "quarter_mt_co2e": {
      "scope_1": 800,
      "scope_2": 700,
      "scope_3": 400
    },
    "ch4_mt_co2e": 0,
    "ch4_prior_year_mt_co2e": 0,
    "alert_cause": "",
    "next_quarter_allowance_mt": 1200,
    "projected_next_quarter_scope_1_mt": 800
  }
}
```

## PRIOR_YEAR_QUARTER

```json
{
  "scope_1": 26017,
  "scope_2": 16701,
  "scope_3": 4362
}
```

## SCOPE_LABELS

```json
{
  "scope_1": "Scope 1 (Direct)",
  "scope_2": "Scope 2 (Electricity)",
  "scope_3": "Scope 3 (Supply Chain)"
}
```

## REGIONAL_SCREENING

```json
{
  "region": "Northeast",
  "quarterly_threshold_mt": 51450,
  "audit_in_days": 14
}
```

## REDUCTION_ACTIONS

```json
[
  {
    "phase": 1,
    "window": "Next 90 days",
    "start": "Next month",
    "action": "Boston Hub LDAR",
    "detail": "Accelerate leak detection and repair at Boston Hub",
    "facility": "NE-01",
    "cost": 85000,
    "reduction_mt": 3240,
    "annual_savings": 102000,
    "note": "compliance secured"
  },
  {
    "phase": 2,
    "window": "Months 4-9",
    "start": "Month 4",
    "action": "CHP + LED",
    "detail": "Combined heat and power at Hartford plus LED retrofits",
    "facility": "NE-02",
    "cost": 810000,
    "reduction_mt": 6260,
    "annual_savings": 607500,
    "note": "combined"
  },
  {
    "phase": 3,
    "window": "Months 10-15",
    "start": "Month 10",
    "action": "Fleet electrification",
    "detail": "Electrify Springfield and Nashua fleet vehicles",
    "facility": "NE-09",
    "cost": 520000,
    "reduction_mt": 3230,
    "annual_savings": 195000,
    "note": ""
  },
  {
    "phase": 4,
    "window": "Month 16+",
    "start": "Month 16",
    "action": "Renewable PPA",
    "detail": "50 MW solar power purchase agreement",
    "facility": "",
    "cost": 0,
    "reduction_mt": 0,
    "annual_savings": 0,
    "note": "Revenue neutral | 50MW solar"
  }
]
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
