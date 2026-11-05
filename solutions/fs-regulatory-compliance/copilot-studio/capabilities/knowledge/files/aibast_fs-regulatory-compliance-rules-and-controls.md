# Financial Regulatory Compliance Pilot — Rules and Controls

> SYNTHETIC PILOT RULES. These rules demonstrate a production pattern; they do
> not replace legal interpretation, a firm's compliance policy, or an
> authorized regulatory submission process.

## Transaction-reporting checks

Check each transaction report for venue ID against the instrument's admitted
venues, counterparty LEI presence and validity, and timestamp format (ISO 8601
UTC). Venue, LEI and timestamp issues are auto-fixable from source records; an
expired counterparty LEI needs the client's updated LEI and goes to manual
review. Reporting compliance = reports filed on time / trades executed.

## Best-execution control

Compare the quarter's client trades with the benchmarks: within best bid/offer
(95%), optimal venue selection (90%), average slippage (below 3 bps) and
execution speed (below 100 ms). Rank venues by execution quality. Present an
RTS 28 report only as a draft for review before client distribution.

## Algorithm-documentation control

A complete documentation pack contains pre-trade testing, stress scenarios, a
kill-switch test and an audit trail. A strategy with a missing item cannot be
deployed until documentation is filed; go-live requires Quant sign-off and
authorized review.

## Certification control

The look-ahead window is 30 days: 15 days or less is Urgent, 30 days or less is
Soon, later is Current; a past expiry is lapsed and the trader must stop
trading pending authorized review. Enrollments and reminders are prepared for
the desk supervisor; never claim a real enrollment or notification.

## Remediation and submission control

The pilot may stage correction reports for auto-fixable trades and a new
submission once a missing value (such as an updated LEI) is supplied. It is a
synthetic dry run: it must not claim that a record was changed or a filing was
transmitted. Production transmission requires an authenticated ARM connector
and explicit approval from an authorized compliance reviewer.

## Response policy

- Lead with the specific figure, record or person requiring action.
- Identify at-risk areas and control gaps only; never state that an audit will
  pass or fail and never present the result as legal or regulatory advice.
- Penalty-exposure figures are modeled estimates, not promises.
- State when the result is a draft, a dry run, or requires human approval.
