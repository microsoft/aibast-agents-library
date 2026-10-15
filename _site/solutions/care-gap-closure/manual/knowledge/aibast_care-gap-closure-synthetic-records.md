# Care Gap Closure Agent — complete synthetic records

> **Fictional aggregate demonstration data only.** These records reproduce the deterministic `CareGapClosureAgent`. They do not establish individual eligibility, exclusions, compliance, risk, or outreach permission.

## Synthetic quality measures

| ID | Name | Source population | Source-recorded closed | Records requiring evidence review | Source-recorded closed rate | Evidence as of | Exact limitation |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| SYN-BCS | Synthetic Breast Screening Measure | 400 | 292 | 108 | 73.0% | 2026-07-31 | Eligibility and exclusions are unvalidated synthetic source fields. |
| SYN-COL | Synthetic Colorectal Screening Measure | 520 | 338 | 182 | 65.0% | 2026-07-31 | Clinical exclusions and external claims may be incomplete. |
| SYN-CDC | Synthetic Diabetes Monitoring Measure | 310 | 257 | 53 | 82.9% | 2026-07-31 | Recent labs and measure-year attribution require reviewer validation. |

Calculation rules:

- `Records requiring evidence review = source population - source-recorded closed`.
- `Source-recorded closed rate = round(source-recorded closed / source population × 100, 1)`.
- The largest evidence-review queue is **SYN-COL — 182 records**.

## Synthetic operational cohorts

| Source key | Display heading | Synthetic count | Exact evidence barrier | Exact draft handling route |
| --- | --- | ---: | --- | --- |
| multiple_source_gaps | Multiple Source Gaps | 42 | mixed evidence completeness | staff review queue |
| single_source_gap | Single Source Gap | 117 | recent evidence may be missing | portal draft |
| contact_data_review | Contact Data Review | 19 | contact preference not confirmed | privacy review queue |

Ordering is operational triage only, not clinical risk scoring.

## Canonical unsent outreach draft

For each selected synthetic measure, the deterministic draft is:

- `Draft: We are reviewing our records and invite you to contact the care team if you have questions.`
- `Do not state that care is overdue or that the recipient is eligible until a reviewer validates the record.`
- `Approval route: quality reviewer → clinician when needed → authorized outreach operator.`

No message is sent.

## Fixed source facts used by the locked cases

- CG-01 must identify `SYN-COL — 182 records` as the largest queue and include `Records requiring evidence review` for all three measures.
- CG-02 must include `Multiple Source Gaps` and `Ordering is operational triage only, not clinical risk scoring.`
- CG-03 uses SYN-BCS and must include `No message is sent` plus the prohibition on stating overdue care or eligibility.
- CG-04 must reproduce the three rates, evidence date 2026-07-31, and exact reviewer limitations.

## Medicare Advantage HEDIS demo panel (video scenario)

Fictional panel used by `hedis_status`, `top_gaps`, `risk_stratification`, `outreach_strategy`,
`campaign_projection`, and `monitoring_plan`. All figures are synthetic and aggregate; no patient is identified.

- Panel: Medicare Advantage, 2,847 patients; 1,142 with gaps (40.1%, computed as the sum of the five measures);
  HEDIS score 72.3% vs target 75%; Star rating impact -0.5 stars; revenue at risk $428,900 (sum of the five
  measures); 23 days to the reporting deadline.
- Top 5 measures (patients / revenue risk / reachable): Diabetes A1C test 387 / $189,450 / 76%; Breast cancer screen
  243 / $94,170 / 89%; Colorectal screen 198 / $76,890 / 62%; Statin therapy 176 / $43,120 / 91%; Blood pressure
  control 138 / $25,270 / 84%. Best opportunity: Diabetes A1C test.
- Diabetes cohort (387): A1C >9.0 (Critical) 8.7 months Immediate; A1C 7-9 (Moderate) 7.2 months High; Never tested,
  new diagnosis, High. Barriers: Transportation 34% (132 patients); No-show history 28% (108); Language (Spanish) 18%
  (70); Insurance lapsed 12% (46); average 4.2 chronic conditions per patient.
- Outreach strategy draft: mobile clinic slots + ride vouchers; SMS reminders 48h/24h/2h; Spanish-speaking MA staff +
  translated materials; direct RN outreach within 48 hours for high-risk A1C. Scope: 294 SMS (76% valid mobile of
  387), 387 voicemails, 312 portal messages, 94 RN callbacks. Nothing is sent until an authorized operator launches it.
- Projection: response SMS 42%, portal 28%, voice 35%, RN 78%; 47 mobile clinic slots to reserve, 132 ride vouchers to
  issue, next-day Tue/Thu slots to open; close rate 68% = 263 of 387 patients; revenue saved $128,700 of $189,450
  (263 x $189,450 / 387, to the nearest $100).
- Monitoring (recommended, not activated): daily 8 AM summary via Teams; real-time close rate tracking; weekly trend vs
  last HEDIS cycle; barrier analysis by patient cohort. Alerts: close rate drops below 60%; 3 failed contact
  attempts; critical patient non-response >48h; campaign budget variance >15%.

### Exact source constants (JSON)

`PANEL`

```json
{
  "population": "Medicare Advantage",
  "patients": 2847,
  "hedis_score": 72.3,
  "hedis_target": 75.0,
  "star_impact": -0.5,
  "days_to_deadline": 23
}
```

`HEDIS_MEASURES`

```json
[
  {
    "measure": "Diabetes A1C test",
    "patients": 387,
    "revenue_risk": 189450,
    "reachable_pct": 76
  },
  {
    "measure": "Breast cancer screen",
    "patients": 243,
    "revenue_risk": 94170,
    "reachable_pct": 89
  },
  {
    "measure": "Colorectal screen",
    "patients": 198,
    "revenue_risk": 76890,
    "reachable_pct": 62
  },
  {
    "measure": "Statin therapy",
    "patients": 176,
    "revenue_risk": 43120,
    "reachable_pct": 91
  },
  {
    "measure": "Blood pressure control",
    "patients": 138,
    "revenue_risk": 25270,
    "reachable_pct": 84
  }
]
```

`A1C_TIERS`

```json
[
  {
    "tier": "A1C >9.0 (Critical)",
    "avg_gap": "8.7 months",
    "priority": "Immediate"
  },
  {
    "tier": "A1C 7-9 (Moderate)",
    "avg_gap": "7.2 months",
    "priority": "High"
  },
  {
    "tier": "Never tested",
    "avg_gap": "New diagnosis",
    "priority": "High"
  }
]
```

`A1C_BARRIERS`

```json
[
  {
    "barrier": "Transportation",
    "patients": 132
  },
  {
    "barrier": "No-show history",
    "patients": 108
  },
  {
    "barrier": "Language (Spanish)",
    "patients": 70
  },
  {
    "barrier": "Insurance lapsed",
    "patients": 46
  }
]
```

`INTERVENTIONS`

```json
[
  {
    "barrier": "Transportation barriers",
    "intervention": "Mobile clinic slots + ride vouchers"
  },
  {
    "barrier": "No-show history",
    "intervention": "SMS reminders (48h, 24h, 2h intervals)"
  },
  {
    "barrier": "Language barriers",
    "intervention": "Spanish-speaking MA staff + translated materials"
  },
  {
    "barrier": "High-risk A1C",
    "intervention": "Direct RN outreach within 48 hours"
  }
]
```

`CHANNEL_PLAN`

```json
{
  "valid_mobile_pct": 76,
  "voicemail": 387,
  "portal": 312,
  "rn_callbacks": 94,
  "response": {
    "SMS": 42,
    "Patient portal": 28,
    "Voice calls": 35,
    "RN outreach": 78
  },
  "mobile_clinic_slots": 47,
  "ride_vouchers": 132,
  "close_rate_pct": 68
}
```

`MONITORING`

```json
{
  "features": [
    "Daily 8 AM summary via Teams",
    "Real-time close rate tracking",
    "Weekly trend vs last HEDIS cycle",
    "Barrier analysis by patient cohort"
  ],
  "alerts": [
    "Close rate drops below 60%",
    "3 failed contact attempts",
    "Critical patient non-response >48h",
    "Campaign budget variance >15%"
  ]
}
```

