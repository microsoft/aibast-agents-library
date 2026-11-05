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
8. The default scope is the 12 Northeast facilities (facility_id omitted, `Northeast`, or `all`); an unmatched facility returns `No synthetic facility matches`. Scope shares are truncated to one decimal; YoY change compares each scope total with `PRIOR_YEAR_QUARTER` and rounds to one decimal; the screening buffer is (51,450 - total) / 51,450 = 8%.
9. A facility alert fires when methane rose year over year or the next-quarter projection exceeds its allowance (Boston Hub: +18% CH4, 4,640 projected vs 4,300 allowance = +340 MT). Carbon credits avoided = reduction MT x $39.2, rounded to $1K; payback months = cost x 12 / annual savings.
10. `implementation_roadmap` lists the four phases of `REDUCTION_ACTIONS` and the projected outcome = total phase reductions / quarterly total (12,730 / 47,340 = 27%).

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
  "prompt": "I need a carbon emissions analysis for our Northeast facilities. EPA audit is in two weeks.",
  "canonical_kwargs": {
    "operation": "emissions_dashboard"
  },
  "must_include": [
    "47,340",
    "Boston Hub",
    "not verified emissions evidence"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Emissions Dashboard

I've analyzed emissions across your 12 Northeast facilities. You're within the screening threshold with an 8% buffer, but Boston Hub needs attention.

**Quarterly Emissions (47,340 MT CO2e)**

| Scope | Emissions | % Total | YoY Change |
|-------|-----------|---------|------------|
| Scope 1 (Direct) | 28,150 MT | 59.4% | +8.2% |
| Scope 2 (Electricity) | 14,680 MT | 31.0% | -12.1% |
| Scope 3 (Supply Chain) | 4,510 MT | 9.5% | +3.4% |

**Compliance:** EPA Northeast regional requirements met (47,340 of 51,450 MT screening threshold; screening, not a legal determination).

**Alert:** Boston Hub methane emissions up 18% due to aging infrastructure. Current trajectory exceeds next-quarter allowances by 340 MT.
**Action:** Accelerate leak detection and repair at Boston Hub - $85K cost avoids $127K in carbon credits.

| Facility | Location | Scope 1 | Scope 2 | Scope 3 | Total |
|----------|----------|---------|---------|---------|-------|
| Boston Hub | Boston, MA | 4,200 | 1,900 | 600 | 6,700 |
| Hartford Generating Station | Hartford, CT | 5,100 | 1,600 | 520 | 7,220 |
| Providence Peaker Plant | Providence, RI | 3,600 | 900 | 300 | 4,800 |
| Portland Fuel Terminal | Portland, ME | 2,300 | 1,100 | 410 | 3,810 |
| Albany Substation Campus | Albany, NY | 1,900 | 2,400 | 380 | 4,680 |
| Burlington Operations Center | Burlington, VT | 800 | 600 | 200 | 1,600 |
| Manchester Service Center | Manchester, NH | 1,150 | 1,000 | 290 | 2,440 |
| Worcester Compressor Station | Worcester, MA | 3,400 | 700 | 330 | 4,430 |
| Springfield Fleet Depot | Springfield, MA | 1,250 | 1,200 | 360 | 2,810 |
| New Haven Plant | New Haven, CT | 2,700 | 1,300 | 450 | 4,450 |
| Syracuse Operations Center | Syracuse, NY | 950 | 1,280 | 270 | 2,500 |
| Nashua Fleet Yard | Nashua, NH | 800 | 700 | 400 | 1,900 |

Source: [Azure IoT Hub + MS Cloud for Sustainability] (synthetic)

> Synthetic inventory, not verified emissions evidence. Validate boundaries, factors, units, and source records before making a claim.

Next: want to see the top reduction opportunities?
```

### EMISSION_TRACKING-02 — Environmental Compliance Manager — `compliance_status`

```json
{
  "case_id": "EMISSION_TRACKING-02",
  "persona": "Environmental Compliance Manager",
  "operation": "compliance_status",
  "prompt": "Screen the Northeast portfolio against its threshold without making a legal compliance claim.",
  "canonical_kwargs": {
    "operation": "compliance_status"
  },
  "must_include": [
    "BELOW SCREENING THRESHOLD",
    "AT RISK (+340 MT)",
    "not a legal compliance determination"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Compliance Status

**Northeast portfolio:** 47,340 of 51,450 MT CO2e - BELOW SCREENING THRESHOLD (8% buffer). EPA audit in 14 days.

| Facility | Scope 1 (quarter) | Next-Quarter Projection | Allowance | Status |
|----------|-------------------|-------------------------|-----------|--------|
| Boston Hub | 4,200 | 4,640 | 4,300 | AT RISK (+340 MT) |
| Hartford Generating Station | 5,100 | 5,100 | 5,500 | BELOW SCREENING THRESHOLD |
| Providence Peaker Plant | 3,600 | 3,600 | 4,000 | BELOW SCREENING THRESHOLD |
| Portland Fuel Terminal | 2,300 | 2,300 | 2,700 | BELOW SCREENING THRESHOLD |
| Albany Substation Campus | 1,900 | 1,900 | 2,300 | BELOW SCREENING THRESHOLD |
| Burlington Operations Center | 800 | 800 | 1,200 | BELOW SCREENING THRESHOLD |
| Manchester Service Center | 1,150 | 1,150 | 1,550 | BELOW SCREENING THRESHOLD |
| Worcester Compressor Station | 3,400 | 3,400 | 3,800 | BELOW SCREENING THRESHOLD |
| Springfield Fleet Depot | 1,250 | 1,250 | 1,650 | BELOW SCREENING THRESHOLD |
| New Haven Plant | 2,700 | 2,700 | 3,100 | BELOW SCREENING THRESHOLD |
| Syracuse Operations Center | 950 | 950 | 1,350 | BELOW SCREENING THRESHOLD |
| Nashua Fleet Yard | 800 | 800 | 1,200 | BELOW SCREENING THRESHOLD |

> Screening result only; it is not a legal compliance determination or an emissions claim.
```

### EMISSION_TRACKING-03 — Decarbonization Program Lead — `reduction_plan`

```json
{
  "case_id": "EMISSION_TRACKING-03",
  "persona": "Decarbonization Program Lead",
  "operation": "reduction_plan",
  "prompt": "What are the top reduction opportunities for the Northeast facilities, and who must review them?",
  "canonical_kwargs": {
    "operation": "reduction_plan"
  },
  "must_include": [
    "Boston Hub LDAR",
    "10 months",
    "engineering, finance, environmental, and executive review"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Emission Reduction Plans

Top reduction opportunities for the Northeast portfolio, ranked by payback:

| Opportunity | Cost | Reduction (MT) | Annual Savings | Payback | Carbon Credits Avoided |
|-------------|------|----------------|----------------|---------|------------------------|
| Boston Hub LDAR (Accelerate leak detection and repair at Boston Hub) | $85K | 3,240 | $102K | 10 months | $127K |
| CHP + LED (Combined heat and power at Hartford plus LED retrofits) | $810K | 6,260 | $607K | 16 months | $245K |
| Fleet electrification (Electrify Springfield and Nashua fleet vehicles) | $520K | 3,230 | $195K | 32 months | $127K |
| Renewable PPA (50 MW solar power purchase agreement) | Revenue neutral | - | - | - | - |

**Combined reduction:** 12,730 MT of 47,340 MT per quarter (27%), at a carbon credit price of $39.2/MT.

> Scenario estimates require engineering, finance, environmental, and executive review before action.

Next: want me to create the implementation roadmap?
```

### EMISSION_TRACKING-04 — Sustainability Lead — `carbon_offset_analysis`

```json
{
  "case_id": "EMISSION_TRACKING-04",
  "persona": "Sustainability Lead",
  "operation": "carbon_offset_analysis",
  "prompt": "Show offset candidates for the projected Boston Hub overage, but do not buy or claim credits.",
  "canonical_kwargs": {
    "operation": "carbon_offset_analysis"
  },
  "must_include": [
    "Appalachian Reforestation",
    "No credit purchase",
    "offset claim"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Carbon Offset Analysis

**Emission Gap to Cover:** 340 MT (projected next-quarter overage)

| Project | Type | Credits Available | Price/t | Cost to Cover Gap | Verified By |
|---------|------|-------------------|---------|-------------------|-------------|
| Appalachian Reforestation | forestry | 45,000 | $18.50 | $6,290 | Verra VCS |
| Texas Wind REC Bundle | renewable_energy | 120,000 | $12.75 | $4,335 | Green-e |
| Montana Methane Capture | methane_capture | 28,000 | $24.00 | $8,160 | ACR |
| Iowa Agricultural Soil Carbon | soil_carbon | 35,000 | $22.00 | $7,480 | Gold Standard |

Reducing at the source (Boston Hub LDAR) closes the gap without buying credits.

> Due-diligence shortlist only. No credit purchase, retirement, disclosure, or offset claim has been made.
```

### EMISSION_TRACKING-05 — Environmental Manager — `implementation_roadmap`

```json
{
  "case_id": "EMISSION_TRACKING-05",
  "persona": "Environmental Manager",
  "operation": "implementation_roadmap",
  "prompt": "Create the implementation roadmap for our emissions reductions.",
  "canonical_kwargs": {
    "operation": "implementation_roadmap"
  },
  "must_include": [
    "Phase 1 (Next 90 days)",
    "$810K",
    "27% emissions reduction"
  ],
  "expected_agent": "EmissionTrackingAgent",
  "captured_model": "claude-sonnet-5"
}
```

#### Exact canonical deterministic tool output

```text
[EmissionTrackingAgent] # Implementation Roadmap

I've created an 18-month phased roadmap sequenced for quick wins and risk mitigation.

## Implementation Timeline

**Phase 1 (Next 90 days) - Boston Hub LDAR**
- Start: Next month | Cost: $85K
- Impact: 3,240 MT reduction, compliance secured
- Payback: 10 months

**Phase 2 (Months 4-9) - CHP + LED**
- Start: Month 4 | Cost: $810K combined
- Impact: 6,260 MT reduction
- Payback: 16 months

**Phase 3 (Months 10-15) - Fleet electrification**
- Start: Month 10 | Cost: $520K
- Impact: 3,230 MT reduction
- Payback: 32 months

**Phase 4 (Month 16+) - Renewable PPA**
- Revenue neutral | 50MW solar

**Projected Outcome:** 27% emissions reduction (12,730 of 47,340 MT per quarter), top 8% industry performance (synthetic benchmark).

Source: [Project Planning + Financial Modeling] (synthetic)

> Draft roadmap. Scenario estimates require engineering, finance, environmental, and executive review before action; nothing is purchased or committed.

Next: want to prepare your EPA audit package?
```

## Response completion checklist

- The selected operation matches the persona question.
- Every required identifier and value appears exactly as recorded.
- The relevant synthetic-data limitation is explicit.
- The authorized reviewer and no-write boundary are explicit.
- No unsupported live-system action or customer outcome is claimed.
