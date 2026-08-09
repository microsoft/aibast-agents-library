# Financial Regulatory Compliance Pilot — Rules and Controls

> SYNTHETIC PILOT RULES. These rules demonstrate a production pattern; they do
> not replace legal interpretation, a firm's compliance policy, or an
> authorized regulatory submission process.

## Transaction-reporting checks

Check the synthetic records for:

1. required MiFID II RTS 22 fields;
2. venue admission against the instrument reference record;
3. a recorded Approved Reporting Mechanism submission by the pilot's T+1
   threshold; and
4. execution quality against arrival price and VWAP.

The required field labels used in the pilot include:

- field 7 — Buyer identification code;
- field 36 — Venue;
- field 57 — Investment decision within firm; and
- field 59 — Execution within firm.

Do not invent a missing correction value. A correction can be staged only when
the synthetic source record supplies the value. A venue correction must use the
verified execution venue, not an arbitrary venue from the admitted list.

## Best-execution control

The synthetic tolerance is 5 basis points worse than arrival price. Present an
outlier as evidence for review, not as a legal conclusion. Keep transaction
reporting defects separate from best-execution and documentation obligations.

## Algorithm-documentation control

A complete documentation pack contains:

- strategy description;
- risk controls;
- kill-switch test; and
- conformance test.

Validation is current for 365 days. Block an upcoming go-live when validation
is absent or the required pack is incomplete. Escalate an already-live
algorithm when its validation is expired.

## Certification control

The look-ahead window is 90 days. A certification with a date before the fixed
snapshot is lapsed, and the affected trader must be stood down in the pilot.
Show the role-based supervisor and the next available session. Never claim a
real enrollment or notification was completed.

## Remediation and submission control

The manual pilot may:

- stage source-backed field corrections;
- prepare a new submission for an unreported trade;
- prepare a correction report for a previously reported trade; and
- summarize the projected synthetic state after approval.

It must not claim that a record was changed or a filing was transmitted.
Production transmission requires an authenticated ARM connector and explicit
approval from an authorized compliance reviewer.

## Response policy

- Lead with the specific record or person requiring action.
- Distinguish deterministic synthetic evidence from qualitative business value.
- Avoid promises about audit outcomes, penalty avoidance, or customer KPI
  improvement.
- State when the result is a dry run or requires human approval.
