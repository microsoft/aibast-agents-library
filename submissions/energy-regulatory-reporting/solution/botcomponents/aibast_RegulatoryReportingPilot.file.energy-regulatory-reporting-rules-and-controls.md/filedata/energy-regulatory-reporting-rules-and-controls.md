# Regulatory Reporting Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Report filtering uses an exact synthetic report ID when supplied; an unknown ID returns no invented report.
2. `report_status` emits `# Regulatory Report Status`, sorts by deadline, and includes report, authority, facility, owner, completion, quality, and status.
3. `data_validation` excludes `not_started` records. Quality below 80 adds `Data quality score below threshold`; completeness below 100 on a non-submitted report adds `Data collection incomplete`.
4. Validation pass rate is passed reports divided by evaluated reports, multiplied by 100 and rounded to one decimal place.
5. `submission_tracker` emits `# Submission Tracker`, sorts by deadline, and includes the exact assignee so overdue PHMSA evidence names Pipeline Operations.
6. `audit_readiness` groups exact AUDIT_FINDINGS by report and counts open and high-severity-open findings.
7. No report is signed, certified, transmitted, or claimed filed. Readiness evidence is not legal advice and cannot predict an audit outcome.
8. `emissions_summary` emits `# Emissions Summary - Last Quarter (Q1 2026)`: the 14-facility pollutant table (total, annual limit, % of limit), CEMS data availability 99.7%, and the CO2 change vs the same quarter last year ((8.24M - 8.89M) / 8.89M = -7.3%).
9. `prepare_submission` emits `# Draft EPA Submission Package`: draft `EPA_Q1_Emissions_Report.xml`, the synthetic CAMD schema check, the SharePoint target location pending authorized upload, the three compliance risks (FERC Form 1 deadline days computed from the fixed demo date 2026-03-19), and automation value (85 - 6) hours x $105 = $8,295.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### ENERGY_REGULATORY_REPORTING-01 — Regulatory Reporting Lead — `report_status`

```json
{
  "case_id": "ENERGY_REGULATORY_REPORTING-01",
  "persona": "Regulatory Reporting Lead",
  "operation": "report_status",
  "prompt": "Which filing is overdue and who owns it?",
  "canonical_kwargs": {
    "operation": "report_status",
    "report_id": "RPT-9006"
  },
  "must_include": [
    "PHMSA Annual Pipeline Safety Report",
    "OVERDUE",
    "Pipeline Operations"
  ],
  "expected_agent": "RegulatoryReportingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[RegulatoryReportingAgent] # Submission Tracker

| Report | Authority | Owner | Deadline | Status | Last Updated |
|--------|-----------|-------|----------|--------|-------------|
| PHMSA Annual Pipeline Safety Report | PHMSA | Pipeline Operations | 2026-03-15 | OVERDUE | 2026-03-14 |
| EPA GHG Reporting Program (Subpart C) | EPA | Environmental Compliance Team | 2026-03-31 | IN_PROGRESS | 2026-03-10 |
| TCEQ Annual Emissions Inventory | State - Texas | Environmental Compliance Team | 2026-03-31 | SUBMITTED | 2026-03-05 |
| FERC Form 1 Annual Report | FERC | Regulatory Affairs | 2026-04-18 | IN_PROGRESS | 2026-03-12 |
| Colorado Air Quality Control Division Report | State - Colorado | Environmental Compliance Team | 2026-04-30 | NOT_STARTED | N/A |
| EPA CAMD Quarterly Emissions Report (Part 75) Q1 | EPA | Environmental Compliance Team | 2026-04-30 | IN_PROGRESS | 2026-03-19 |
| EPA Toxics Release Inventory (TRI) | EPA | Health & Safety Team | 2026-07-01 | IN_PROGRESS | 2026-02-28 |

> Read-only tracking. No regulator filing, certification, signature, or transmission has occurred.
```

### ENERGY_REGULATORY_REPORTING-02 — Data Analyst — `data_validation`

```json
{
  "case_id": "ENERGY_REGULATORY_REPORTING-02",
  "persona": "Data Analyst",
  "operation": "data_validation",
  "prompt": "Which report data is incomplete or below quality threshold?",
  "canonical_kwargs": {
    "operation": "data_validation"
  },
  "must_include": [
    "Data collection incomplete",
    "Data quality score below threshold",
    "authorized report owner"
  ],
  "expected_agent": "RegulatoryReportingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[RegulatoryReportingAgent] # Data Validation Results

**Validation Pass Rate:** 33.3%

| Report | Quality Score | Completeness | Issues | Passed |
|--------|-------------|-------------|--------|--------|
| EPA GHG Reporting Program (Subpart C) | 87/100 | 78% | Data collection incomplete (78%) | NO |
| FERC Form 1 Annual Report | 92/100 | 65% | Data collection incomplete (65%) | NO |
| TCEQ Annual Emissions Inventory | 95/100 | 100% | None | YES |
| EPA Toxics Release Inventory (TRI) | 74/100 | 42% | Data quality score below threshold (74/100); Data collection incomplete (42%) | NO |
| PHMSA Annual Pipeline Safety Report | 81/100 | 90% | Data collection incomplete (90%) | NO |
| EPA CAMD Quarterly Emissions Report (Part 75) Q1 | 99.7/100 | 100% | None | YES |

> Validation screening only. An authorized report owner must resolve and attest source evidence.
```

### ENERGY_REGULATORY_REPORTING-03 — Compliance Manager — `submission_tracker`

```json
{
  "case_id": "ENERGY_REGULATORY_REPORTING-03",
  "persona": "Compliance Manager",
  "operation": "submission_tracker",
  "prompt": "Show filing state and confirm you did not transmit anything.",
  "canonical_kwargs": {
    "operation": "submission_tracker",
    "report_id": "RPT-9006"
  },
  "must_include": [
    "PHMSA Annual Pipeline Safety Report",
    "OVERDUE",
    "No regulator filing"
  ],
  "expected_agent": "RegulatoryReportingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[RegulatoryReportingAgent] # Submission Tracker

| Report | Authority | Owner | Deadline | Status | Last Updated |
|--------|-----------|-------|----------|--------|-------------|
| PHMSA Annual Pipeline Safety Report | PHMSA | Pipeline Operations | 2026-03-15 | OVERDUE | 2026-03-14 |
| EPA GHG Reporting Program (Subpart C) | EPA | Environmental Compliance Team | 2026-03-31 | IN_PROGRESS | 2026-03-10 |
| TCEQ Annual Emissions Inventory | State - Texas | Environmental Compliance Team | 2026-03-31 | SUBMITTED | 2026-03-05 |
| FERC Form 1 Annual Report | FERC | Regulatory Affairs | 2026-04-18 | IN_PROGRESS | 2026-03-12 |
| Colorado Air Quality Control Division Report | State - Colorado | Environmental Compliance Team | 2026-04-30 | NOT_STARTED | N/A |
| EPA CAMD Quarterly Emissions Report (Part 75) Q1 | EPA | Environmental Compliance Team | 2026-04-30 | IN_PROGRESS | 2026-03-19 |
| EPA Toxics Release Inventory (TRI) | EPA | Health & Safety Team | 2026-07-01 | IN_PROGRESS | 2026-02-28 |

> Read-only tracking. No regulator filing, certification, signature, or transmission has occurred.
```

### ENERGY_REGULATORY_REPORTING-04 — Internal Auditor — `audit_readiness`

```json
{
  "case_id": "ENERGY_REGULATORY_REPORTING-04",
  "persona": "Internal Auditor",
  "operation": "audit_readiness",
  "prompt": "What high-severity reporting evidence is still open?",
  "canonical_kwargs": {
    "operation": "audit_readiness",
    "report_id": "RPT-9006"
  },
  "must_include": [
    "Pipeline mileage discrepancy",
    "HIGH",
    "cannot predict an audit outcome"
  ],
  "expected_agent": "RegulatoryReportingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[RegulatoryReportingAgent] # Audit Readiness Assessment

**Total Findings:** 4 | **Open:** 3 | **High Severity Open:** 1

## EPA GHG Reporting Program (Subpart C)

| Finding | Severity | Status | Due Date |
|---------|----------|--------|----------|
| Missing CEMS calibration records for Q3 | MEDIUM | OPEN | 2026-03-25 |

## FERC Form 1 Annual Report

| Finding | Severity | Status | Due Date |
|---------|----------|--------|----------|
| Depreciation schedule mismatch with PowerPlan | HIGH | REMEDIATED | 2026-03-15 |

## EPA Toxics Release Inventory (TRI)

| Finding | Severity | Status | Due Date |
|---------|----------|--------|----------|
| Threshold calculation methodology not documented | LOW | OPEN | 2026-05-01 |

## PHMSA Annual Pipeline Safety Report

| Finding | Severity | Status | Due Date |
|---------|----------|--------|----------|
| Pipeline mileage discrepancy between GIS and PIMS | HIGH | OPEN | 2026-03-20 |

> Readiness triage is not legal advice and cannot predict an audit outcome.
```

### ENERGY_REGULATORY_REPORTING-05 — Environmental Manager — `emissions_summary`

```json
{
  "case_id": "ENERGY_REGULATORY_REPORTING-05",
  "persona": "Environmental Manager",
  "operation": "emissions_summary",
  "prompt": "I need to prepare our quarterly EPA emissions report. Can you pull the data?",
  "canonical_kwargs": {
    "operation": "emissions_summary"
  },
  "must_include": [
    "14 facilities",
    "8.24M tons",
    "down 7.3%"
  ],
  "expected_agent": "RegulatoryReportingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[RegulatoryReportingAgent] # Emissions Summary - Last Quarter (Q1 2026)

I've compiled your quarterly emissions data across all 14 facilities. All plants are compliant with permit limits and data quality is strong at 99.7% uptime (CEMS data availability).

| Pollutant | Total | Annual Limit | % of Limit |
|-----------|-------|--------------|------------|
| CO2 | 8.24M tons | 35.2M tons | 23.4% |
| NOx | 4,187 tons | 18,500 tons | 22.6% |
| SO2 | 2,943 tons | 12,800 tons | 23.0% |
| Mercury | 142 lbs | 620 lbs | 22.9% |

**Key Highlight:** CO2 emissions down 7.3% vs same quarter last year while maintaining generation capacity.

Source: [Azure Compliance Manager + CEMS] (synthetic)

> Synthetic emissions snapshot for report preparation; not a certified submission.

Next: should I generate the EPA CAMD submission file?
```

### ENERGY_REGULATORY_REPORTING-06 — Regulatory Affairs Director — `prepare_submission`

```json
{
  "case_id": "ENERGY_REGULATORY_REPORTING-06",
  "persona": "Regulatory Affairs Director",
  "operation": "prepare_submission",
  "prompt": "Generate the EPA submission file for the quarter and show me any compliance risks.",
  "canonical_kwargs": {
    "operation": "prepare_submission"
  },
  "must_include": [
    "EPA_Q1_Emissions_Report.xml",
    "6 sections incomplete",
    "No regulator filing"
  ],
  "expected_agent": "RegulatoryReportingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[RegulatoryReportingAgent] # Draft EPA Submission Package

The EPA submission file is ready for your upload, and I've identified 3 compliance risks that need attention in the next 30 days.

**Submission Ready (draft):**
- EPA_Q1_Emissions_Report.xml generated (draft for EPA CAMD Quarterly Emissions Report (Part 75) Q1)
- Validated against EPA CAMD schema: passed (synthetic validation)
- Location: SharePoint > Regulatory Filings (pending your authorized upload)

**Compliance Risks Identified:**
- FERC Form 1 - 6 sections incomplete, 30 days until deadline
- OSHA 300A Posting - 3 facilities missing annual summaries
- State Air Permits - 2 renewals needed next quarter

**Automation Value:** This report took 6 hours vs 85 hours manually, saving $8,295 in labor costs (79 hours x $105/hour, synthetic estimate).

Source: [Azure Compliance + SharePoint] (synthetic)

> Draft package only. No regulator filing, certification, signature, upload, or transmission has occurred.

Next: would you like me to assess what's needed to complete the FERC filing?
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
