# Emissions Tracking Agent — Deterministic Rules, Controls, and Locked Evidence

> Use this file with the complete synthetic records. It contains the exact computation rules, output contracts, locked prompts, and canonical strict-isolation tool outputs needed to reproduce the pilot without access to the Python source.

## Deterministic operation rules

1. Facility filtering accepts an exact synthetic facility ID or a case-insensitive facility-name substring. `Ridgeline` resolves to FAC-E03.
2. `emissions_dashboard` emits `# Emissions Dashboard`; facility total is Scope 1 + Scope 2 + Scope 3 CO2 tonnes. Ridgeline totals 1,420,000 + 18,200 + 95,000 = 1,533,200 tonnes CO2e.
3. Threshold percentage is Scope 1 divided by the configured facility threshold, multiplied by 100 and rounded to one decimal place.
4. `compliance_status` is screening only: Scope 1 at or below threshold is `BELOW SCREENING THRESHOLD`; above is `ABOVE SCREENING THRESHOLD`. It never declares legal compliance.
5. Actual reduction is `(1 - current Scope 1 / baseline CO2) * 100`, rounded to one decimal place. On-track means actual reduction is at least the configured target.
6. `reduction_plan` target is baseline multiplied by one minus target percentage; remaining reduction is current Scope 1 minus target, floored at zero. Actions and costs come only from the deterministic source.
7. `carbon_offset_analysis` totals the remaining reduction gap and the exact available credits and costs. It is due diligence only: no purchase, retirement, disclosure, or offset claim occurs.

## Shared authorization controls

1. Use only the uploaded synthetic records and operation skills.
2. Lead with the exact source-backed identifier, value, status, and output heading.
3. Preserve uncertainty and distinguish screening, recommendation, estimate, or draft from an authorized decision.
4. Never invent a missing record, value, approval, notification, filing, assignment, transaction, or side effect.
5. Production reads require approved least-privilege connections. Any future write requires role authorization, current-state validation, explicit human confirmation, error handling, and immutable audit logging.
6. Public value statements remain qualitative; exact numbers are synthetic evidence only.

## Locked persona cases and canonical tool evidence

### EMISSION_TRACKING-01 — Emissions Data Analyst — `emissions_dashboard`

```json
{
  "case_id": "EMISSION_TRACKING-01",
  "persona": "Emissions Data Analyst",
  "operation": "emissions_dashboard",
  "prompt": "Consolidate the Ridgeline scope totals and state the evidence limitation.",
  "canonical_kwargs": {
    "operation": "emissions_dashboard",
    "facility_id": "FAC-E03"
  },
  "must_include": [
    "Ridgeline Coal Station",
    "1,533,200",
    "not verified emissions evidence"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Emissions Dashboard

**Total Portfolio Emissions:** 1,533,200 tonnes CO2e

| Facility | Type | Scope 1 | Scope 2 | Scope 3 | Total | % of Threshold |
|----------|------|---------|---------|---------|-------|---------------|
| Ridgeline Coal Station | coal_plant | 1,420,000 | 18,200 | 95,000 | 1,533,200 | 94.7% |

> Synthetic inventory, not verified emissions evidence. Validate boundaries, factors, units, and source records before making a claim.
```

### EMISSION_TRACKING-02 — Environmental Compliance Manager — `compliance_status`

```json
{
  "case_id": "EMISSION_TRACKING-02",
  "persona": "Environmental Compliance Manager",
  "operation": "compliance_status",
  "prompt": "Screen FAC-E03 against its threshold without making a legal compliance claim.",
  "canonical_kwargs": {
    "operation": "compliance_status",
    "facility_id": "FAC-E03"
  },
  "must_include": [
    "BELOW SCREENING THRESHOLD",
    "not a legal compliance determination"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Compliance Status

| Facility | Scope 1 CO2 | Threshold | Compliant | Gap | Target Reduction | Actual |
|----------|-------------|-----------|-----------|-----|-----------------|--------|
| Ridgeline Coal Station | 1,420,000 | 1,500,000 | BELOW SCREENING THRESHOLD | 0 | 30% | 20.2% (Behind) |

> Screening result only; it is not a legal compliance determination or an emissions claim.
```

### EMISSION_TRACKING-03 — Decarbonization Program Lead — `reduction_plan`

```json
{
  "case_id": "EMISSION_TRACKING-03",
  "persona": "Decarbonization Program Lead",
  "operation": "reduction_plan",
  "prompt": "What reduction scenarios exist for Ridgeline and who must review them?",
  "canonical_kwargs": {
    "operation": "reduction_plan",
    "facility_id": "FAC-E03"
  },
  "must_include": [
    "Fuel switching to natural gas",
    "engineering, finance, environmental, and executive review"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Emission Reduction Plans

## Ridgeline Coal Station
Current: 1,420,000 tonnes | Target: 1,246,000 tonnes | Gap: 174,000 tonnes

| Action | Reduction (tonnes) | Cost ($M) |
|--------|-------------------|----------|
| Fuel switching to natural gas | 400,000 | $85.0M |
| Carbon capture retrofit | 300,000 | $120.0M |
| Efficiency upgrades | 50,000 | $12.0M |

> Scenario estimates require engineering, finance, environmental, and executive review before action.
```

### EMISSION_TRACKING-04 — Sustainability Lead — `carbon_offset_analysis`

```json
{
  "case_id": "EMISSION_TRACKING-04",
  "persona": "Sustainability Lead",
  "operation": "carbon_offset_analysis",
  "prompt": "Show offset candidates for the Ridgeline gap, but do not buy or claim credits.",
  "canonical_kwargs": {
    "operation": "carbon_offset_analysis",
    "facility_id": "FAC-E03"
  },
  "must_include": [
    "Appalachian Reforestation",
    "No credit purchase",
    "offset claim"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-haiku-4.5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Carbon Offset Analysis

**Emission Gap to Cover:** 174,000 tonnes
**Total Credits Available:** 228,000 tonnes
**Total Offset Cost:** $3,804,500

| Project | Type | Credits | Price/t | Total Cost | Verified By |
|---------|------|---------|---------|-----------|-------------|
| Appalachian Reforestation | forestry | 45,000 | $18.50 | $832,500 | Verra VCS |
| Texas Wind REC Bundle | renewable_energy | 120,000 | $12.75 | $1,530,000 | Green-e |
| Montana Methane Capture | methane_capture | 28,000 | $24.00 | $672,000 | ACR |
| Iowa Agricultural Soil Carbon | soil_carbon | 35,000 | $22.00 | $770,000 | Gold Standard |

> Due-diligence shortlist only. No credit purchase, retirement, disclosure, or offset claim has been made.
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
