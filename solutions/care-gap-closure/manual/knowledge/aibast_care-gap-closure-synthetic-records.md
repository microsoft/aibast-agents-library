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
