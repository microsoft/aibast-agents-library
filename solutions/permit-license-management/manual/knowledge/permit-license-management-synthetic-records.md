# Permit Management Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/permit_license_management_stack/permit_license_management_agent.py`
- Captured source SHA-256: `6d42f1ce868288628c1355841200790d26ff9756fc854c451bfb138d1b8aa66e`
- Locked case file: `tests/demo_cases/permit-license-management.json`
- Locked case SHA-256: `3a085cd75bceace09f03371a77e0f267b351670b6853a7e07722ac3e6f015b8a`
- Strict isolation: `true`

## Record index

- `PERMITS`
- `APPLICATIONS`
- `REGULATORY_REQUIREMENTS`

## PERMITS

```json
{
  "PRM-6001": {
    "name": "Title V Air Operating Permit",
    "facility": "Riverside Generating Station",
    "issuing_authority": "CA Air Resources Board",
    "permit_number": "AOP-CA-2024-1847",
    "issued_date": "2024-06-15",
    "expiration_date": "2029-06-15",
    "status": "active",
    "type": "air_quality",
    "renewal_lead_days": 365,
    "conditions": 24,
    "last_inspection": "2025-09-22"
  },
  "PRM-6002": {
    "name": "NPDES Stormwater Discharge Permit",
    "facility": "Riverside Generating Station",
    "issuing_authority": "CA State Water Board",
    "permit_number": "NPDES-CA-0052841",
    "issued_date": "2023-03-01",
    "expiration_date": "2026-03-01",
    "status": "expired",
    "type": "water_discharge",
    "renewal_lead_days": 180,
    "conditions": 18,
    "last_inspection": "2025-07-14"
  },
  "PRM-6003": {
    "name": "RCRA Hazardous Waste Generator",
    "facility": "Bayshore Refinery",
    "issuing_authority": "EPA Region 6",
    "permit_number": "TXD-0489-2215",
    "issued_date": "2022-01-10",
    "expiration_date": "2027-01-10",
    "status": "active",
    "type": "waste_management",
    "renewal_lead_days": 270,
    "conditions": 32,
    "last_inspection": "2025-11-05"
  },
  "PRM-6004": {
    "name": "Pipeline Operating License",
    "facility": "Northeast Corridor Pipeline",
    "issuing_authority": "PHMSA",
    "permit_number": "PHMSA-NE-7742",
    "issued_date": "2021-08-20",
    "expiration_date": "2026-08-20",
    "status": "active",
    "type": "pipeline_operation",
    "renewal_lead_days": 365,
    "conditions": 28,
    "last_inspection": "2025-10-30"
  },
  "PRM-6005": {
    "name": "Coal Combustion Residuals Permit",
    "facility": "Ridgeline Coal Station",
    "issuing_authority": "CO Dept of Public Health",
    "permit_number": "CCR-CO-2023-0091",
    "issued_date": "2023-04-01",
    "expiration_date": "2026-04-01",
    "status": "active",
    "type": "waste_management",
    "renewal_lead_days": 180,
    "conditions": 21,
    "last_inspection": "2025-08-18"
  },
  "PRM-6006": {
    "name": "Spill Prevention Control Plan",
    "facility": "Bayshore Refinery",
    "issuing_authority": "EPA Region 6",
    "permit_number": "SPCC-TX-2024-3340",
    "issued_date": "2024-02-15",
    "expiration_date": "2029-02-15",
    "status": "active",
    "type": "spill_prevention",
    "renewal_lead_days": 365,
    "conditions": 15,
    "last_inspection": "2025-06-02"
  }
}
```

## APPLICATIONS

```json
{
  "APP-7001": {
    "permit_name": "NPDES Stormwater Discharge Permit Renewal",
    "facility": "Riverside Generating Station",
    "submitted_date": "2025-09-01",
    "authority": "CA State Water Board",
    "status": "under_review",
    "expected_decision": "2026-04-15",
    "comments_received": 3
  },
  "APP-7002": {
    "permit_name": "New Source Review - Gas Turbine Expansion",
    "facility": "Riverside Generating Station",
    "submitted_date": "2026-01-20",
    "authority": "CA Air Resources Board",
    "status": "public_comment",
    "expected_decision": "2026-06-30",
    "comments_received": 12
  },
  "APP-7003": {
    "permit_name": "Pipeline Integrity Management Plan Update",
    "facility": "Northeast Corridor Pipeline",
    "submitted_date": "2026-02-10",
    "authority": "PHMSA",
    "status": "submitted",
    "expected_decision": "2026-05-15",
    "comments_received": 0
  }
}
```

## REGULATORY_REQUIREMENTS

```json
{
  "air_quality": [
    "Continuous emissions monitoring",
    "Annual stack testing",
    "Quarterly compliance reports"
  ],
  "water_discharge": [
    "Monthly effluent sampling",
    "Annual DMR submission",
    "Stormwater pollution prevention plan"
  ],
  "waste_management": [
    "Biennial hazardous waste report",
    "Manifest tracking",
    "Land disposal restrictions compliance"
  ],
  "pipeline_operation": [
    "Integrity management program",
    "Operator qualification records",
    "Emergency response plan"
  ],
  "spill_prevention": [
    "Annual SPCC plan review",
    "Integrity testing of containers",
    "Discharge prevention briefings"
  ]
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
