# Regulatory Reporting Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/regulatory_reporting_stack/regulatory_reporting_agent.py`
- Captured source SHA-256: `bf1440fe023ff90686473a33078c0e9da58016b3cd95c39ec1c0cf64b95c49f7`
- Locked case file: `tests/demo_cases/energy-regulatory-reporting.json`
- Locked case SHA-256: `2246e0ebfbc0d3e35486c545f73c602c67eb55597b67c73cd047dfc5e83498e5`
- Strict isolation: `true`

## Record index

- `REGULATORY_REPORTS`
- `DATA_VALIDATION_RULES`
- `AUDIT_FINDINGS`

## REGULATORY_REPORTS

```json
{
  "RPT-9001": {
    "name": "EPA GHG Reporting Program (Subpart C)",
    "authority": "EPA",
    "facility": "Riverside Generating Station",
    "reporting_period": "CY 2025",
    "deadline": "2026-03-31",
    "status": "in_progress",
    "data_quality_score": 87,
    "completeness_pct": 78,
    "assignee": "Environmental Compliance Team",
    "last_updated": "2026-03-10"
  },
  "RPT-9002": {
    "name": "FERC Form 1 Annual Report",
    "authority": "FERC",
    "facility": "Corporate (All Facilities)",
    "reporting_period": "CY 2025",
    "deadline": "2026-04-18",
    "status": "in_progress",
    "data_quality_score": 92,
    "completeness_pct": 65,
    "assignee": "Regulatory Affairs",
    "last_updated": "2026-03-12"
  },
  "RPT-9003": {
    "name": "TCEQ Annual Emissions Inventory",
    "authority": "State - Texas",
    "facility": "Bayshore Refinery",
    "reporting_period": "CY 2025",
    "deadline": "2026-03-31",
    "status": "submitted",
    "data_quality_score": 95,
    "completeness_pct": 100,
    "assignee": "Environmental Compliance Team",
    "last_updated": "2026-03-05"
  },
  "RPT-9004": {
    "name": "Colorado Air Quality Control Division Report",
    "authority": "State - Colorado",
    "facility": "Ridgeline Coal Station",
    "reporting_period": "CY 2025",
    "deadline": "2026-04-30",
    "status": "not_started",
    "data_quality_score": 0,
    "completeness_pct": 0,
    "assignee": "Environmental Compliance Team",
    "last_updated": null
  },
  "RPT-9005": {
    "name": "EPA Toxics Release Inventory (TRI)",
    "authority": "EPA",
    "facility": "Bayshore Refinery",
    "reporting_period": "CY 2025",
    "deadline": "2026-07-01",
    "status": "in_progress",
    "data_quality_score": 74,
    "completeness_pct": 42,
    "assignee": "Health & Safety Team",
    "last_updated": "2026-02-28"
  },
  "RPT-9006": {
    "name": "PHMSA Annual Pipeline Safety Report",
    "authority": "PHMSA",
    "facility": "Northeast Corridor Pipeline",
    "reporting_period": "CY 2025",
    "deadline": "2026-03-15",
    "status": "overdue",
    "data_quality_score": 81,
    "completeness_pct": 90,
    "assignee": "Pipeline Operations",
    "last_updated": "2026-03-14"
  }
}
```

## DATA_VALIDATION_RULES

```json
{
  "emissions_data": {
    "rules": [
      "Non-negative values",
      "Year-over-year variance < 25%",
      "Mass balance check",
      "Unit conversion validation"
    ],
    "source_systems": [
      "CEMS",
      "Fuel metering",
      "Production logs"
    ]
  },
  "financial_data": {
    "rules": [
      "Reconciliation to GL",
      "Rate base validation",
      "Depreciation schedule check",
      "Intercompany elimination"
    ],
    "source_systems": [
      "SAP",
      "PowerPlan",
      "Hyperion"
    ]
  },
  "safety_data": {
    "rules": [
      "Incident classification verification",
      "Mileage data reconciliation",
      "Leak survey completeness"
    ],
    "source_systems": [
      "PIMS",
      "GIS",
      "Inspection database"
    ]
  }
}
```

## AUDIT_FINDINGS

```json
{
  "AUD-001": {
    "report": "RPT-9001",
    "finding": "Missing CEMS calibration records for Q3",
    "severity": "medium",
    "status": "open",
    "due_date": "2026-03-25"
  },
  "AUD-002": {
    "report": "RPT-9002",
    "finding": "Depreciation schedule mismatch with PowerPlan",
    "severity": "high",
    "status": "remediated",
    "due_date": "2026-03-15"
  },
  "AUD-003": {
    "report": "RPT-9005",
    "finding": "Threshold calculation methodology not documented",
    "severity": "low",
    "status": "open",
    "due_date": "2026-05-01"
  },
  "AUD-004": {
    "report": "RPT-9006",
    "finding": "Pipeline mileage discrepancy between GIS and PIMS",
    "severity": "high",
    "status": "open",
    "due_date": "2026-03-20"
  }
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
