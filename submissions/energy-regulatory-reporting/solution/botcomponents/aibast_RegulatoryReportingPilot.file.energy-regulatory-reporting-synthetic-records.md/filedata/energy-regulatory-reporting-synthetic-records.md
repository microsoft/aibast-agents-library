# Regulatory Reporting Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/energy_stacks/regulatory_reporting_stack/regulatory_reporting_agent.py`
- Captured source SHA-256: `c0045a249275152acee2683de879c34a478c52544868e0a592a7f7536c05a3e5`
- Locked case file: `tests/demo_cases/energy-regulatory-reporting.json`
- Locked case SHA-256: `a20d8391f70792e3de6634dfbff353052df9f0cf79d750b0347e23bf0f377116`
- Strict isolation: `true`

## Demo scenario (quarterly EPA emissions report)

- Last quarter, 14 facilities, all within permit limits; CEMS data availability 99.7%.
- CO2 8.24M tons (annual limit 35.2M), NOx 4,187 tons (18,500), SO2 2,943 tons (12,800), Mercury 142 lbs (620); CO2 down 7.3% vs the same quarter last year.
- Draft submission: EPA_Q1_Emissions_Report.xml, validated against the EPA CAMD schema (synthetic), target SharePoint > Regulatory Filings pending authorized upload.
- Compliance risks in the next 30 days: FERC Form 1 - 6 sections incomplete, 30 days until deadline; OSHA 300A Posting - 3 facilities missing annual summaries; State Air Permits - 2 renewals needed next quarter.
- Automation value: 6 hours vs 85 hours manually = 79 hours x $105 = $8,295 (synthetic estimate).

## Record index

- `REGULATORY_REPORTS`
- `DATA_VALIDATION_RULES`
- `AUDIT_FINDINGS`
- `EMISSIONS_QUARTER`
- `SUBMISSION_PACKAGE`
- `COMPLIANCE_RISKS`

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
  },
  "RPT-9007": {
    "name": "EPA CAMD Quarterly Emissions Report (Part 75) Q1",
    "authority": "EPA",
    "facility": "All 14 facilities",
    "reporting_period": "Q1 2026",
    "deadline": "2026-04-30",
    "status": "in_progress",
    "data_quality_score": 99.7,
    "completeness_pct": 100,
    "assignee": "Environmental Compliance Team",
    "last_updated": "2026-03-19"
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

## EMISSIONS_QUARTER

```json
{
  "quarter": "Q1",
  "period": "Last Quarter (Q1 2026)",
  "facilities": 14,
  "facilities_within_limits": 14,
  "cems_data_availability_pct": 99.7,
  "pollutants": [
    {
      "pollutant": "CO2",
      "total": 8240000,
      "annual_limit": 35200000,
      "unit": "tons",
      "prior_year_quarter": 8890000
    },
    {
      "pollutant": "NOx",
      "total": 4187,
      "annual_limit": 18500,
      "unit": "tons",
      "prior_year_quarter": 4402
    },
    {
      "pollutant": "SO2",
      "total": 2943,
      "annual_limit": 12800,
      "unit": "tons",
      "prior_year_quarter": 3105
    },
    {
      "pollutant": "Mercury",
      "total": 142,
      "annual_limit": 620,
      "unit": "lbs",
      "prior_year_quarter": 151
    }
  ]
}
```

## SUBMISSION_PACKAGE

```json
{
  "report_id": "RPT-9007",
  "file_name": "EPA_Q1_Emissions_Report.xml",
  "schema": "EPA CAMD schema",
  "schema_check": "passed (synthetic validation)",
  "location": "SharePoint > Regulatory Filings",
  "manual_hours": 85,
  "agent_hours": 6,
  "labor_rate_per_hour": 105
}
```

## COMPLIANCE_RISKS

```json
[
  {
    "item": "FERC Form 1",
    "report": "RPT-9002",
    "detail": "6 sections incomplete",
    "sections_incomplete": 6
  },
  {
    "item": "OSHA 300A Posting",
    "report": null,
    "detail": "3 facilities missing annual summaries",
    "facilities_missing": 3
  },
  {
    "item": "State Air Permits",
    "report": null,
    "detail": "2 renewals needed next quarter",
    "renewals_next_quarter": 2
  }
]
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
