# Financial Regulatory Compliance Pilot — Synthetic Records

> SYNTHETIC PILOT DATA. Every organization, identifier, transaction, figure, and
> person-like record below is fictional and describes one fixed synthetic
> quarter. Do not treat this content as customer data, regulatory advice, or
> evidence of a filing.

## Reporting entity

- Name: Northgate Asset Management LLP
- LEI: `549300XKQZ2P4NLK7T18`
- Regulator: FCA; submission route: FCA transaction reporting via the firm's ARM

## Desk quarter (last quarter)

| Figure | Value |
|---|---|
| Trades executed | 12,000 |
| Transaction reports filed on time | 11,976 |
| Reports needing amendment | 24 |
| Reporting compliance | 99.8% (11,976 / 12,000) |
| Client trades in best-execution scope | 8,432 |
| Traders on the desk | 12 |
| Market making uptime | 98.5% (obligation 95.0%) |
| Batch amendment processing | about 8 minutes |
| Penalty exposure avoided (modeled) | £847K |

## Transaction-report exceptions (24)

| Issue type | Trades | Auto-fix | Priority |
|---|---|---|---|
| Venue ID mismatch | 11 | Yes | High |
| Counterparty LEI | 8 | Yes | High |
| Timestamp format | 4 | Yes | Medium |
| Manual review needed | 1 | No | Critical |

23 trades are auto-fixable (11 + 8 + 4) and can be staged as correction reports in one batch.

| Trade | Issue | Detail | Client | Resolution |
|---|---|---|---|---|
| APX-2024-8847 | Manual review needed | Counterparty LEI expired during settlement | Standard National Bank | Updated LEI required from client |
| APX-2024-8812 | Venue ID mismatch | Reported XPAR; instrument admitted on XLON | Meridian Pension Trustees | Correct venue to XLON |
| APX-2024-8829 | Counterparty LEI | Buyer LEI field empty | Halden Life Assurance | Populate LEI from client master |
| APX-2024-8853 | Timestamp format | Trading time not in UTC microseconds | Cavendish Multi-Asset Fund | Reformat to ISO 8601 UTC |

APX-2024-8847 is the critical manual-review trade: the counterparty LEI expired during settlement; Standard National Bank must supply an updated LEI, after which it goes as a new submission.

## Algorithm strategies

| # | Strategy | Status | Pre-trade testing | Stress scenarios | Kill switch test | Audit trail |
|---|---|---|---|---|---|---|
| 1 | ALGO-VWAP-EU — VWAP Europe | live | Complete | Complete | Complete | Complete |
| 2 | ALGO-IS-EU — Implementation Shortfall | live | Complete | Complete | Complete | Complete |
| 3 | ALGO-POV-EU — Percentage of Volume | live | Complete | Complete | Complete | Complete |
| 4 | ALGO-DARK-EU — Dark Aggregator | live | Complete | Complete | Complete | Complete |
| 5 | ALGO-MOM-05 — Momentum algo | pre-deployment | Missing | Missing | Complete | Complete |

Algo testing docs: 4 of 5 complete (80%). Strategy #5 (momentum algo, ALGO-MOM-05) is pre-deployment; missing items are due end of week. Required actions: Complete 12-month backtest with volatility scenarios; Document circuit breaker triggers (currently at 5% daily loss); Obtain Quant team sign-off; File with compliance register. Risk if incomplete: cannot deploy; potential £2.1M revenue impact.

## Best execution (8,432 client trades)

| Metric | Result | Benchmark | Status |
|---|---|---|---|
| Within best bid/offer | 97% | 95% | Exceeds |
| Optimal venue selection | 94% | 90% | Exceeds |
| Average slippage | 2.3 bps | <3 bps | Better |
| Execution speed | 42 ms | <100 ms | Met |

| Rank | Venue | Trades | Quality |
|---|---|---|---|
| 1 | LSE (London) | 4,247 | 98.2% |
| 2 | BATS Europe | 2,156 | 96.8% |
| 3 | Chi-X | 1,589 | 95.1% |
| 4 | Turquoise | 440 | 93.4% |

Venue trades total 8,432. RTS 28 quarterly report: drafted with the top venue analysis, ready for review before client distribution (not published).

## Trader certifications (12-trader desk)

| Trader | Certification | Expires in | Status | Prepared action |
|---|---|---|---|---|
| James Morrison | MiFID II Algo | 15 days | Urgent | Enrollment in next week's recertification prepared |
| Sarah Chen | Best Execution | 22 days | Soon | Reminder drafted, session proposed |
| Michael Torres | Transaction Reporting | 28 days | Soon | Reminder drafted, session proposed |
| Lisa Wong | Market Abuse | 6 months | Current | None needed |

No trader is lapsed. 3 traders need renewal within 30 days (by end of month). All 12 traders are current on AML training. Team compliance rate 92% (11 of 12 fully current; target 100%); assessment average 94%; next mandatory refresh in 45 days; penalty risk £50K+ per uncertified trader operating.

## Executive scorecard

| Area | Score | Risk level |
|---|---|---|
| Transaction Reporting | 99.8% | Low |
| Best Execution | 97% | Low |
| Algo Compliance | 80% | Medium |
| Trader Certifications | 92% | Medium |

Risk level is Low at 95% or above, otherwise Medium. Remaining actions: 1 trade pending LEI update; algo docs due end of week.

## Locked cases and deterministic evidence

| Case | Persona | Operation | Prompt | Required evidence |
|---|---|---|---|---|
| RC-01 | Chief Compliance Officer | compliance_dashboard | Are we going to fail our next MiFID audit? What's actually broken on the desk right now? | 99.8%; Strategy #5 |
| RC-02 | Trading Desk Supervisor | certification_tracker | Which of my traders can't legally trade today, and who do I have to call? | James Morrison; No trader is lapsed |
| RC-03 | Compliance Manager | trade_surveillance | We executed a few hundred trades this week. Which ones will the regulator reject, and why exactly? | APX-2024-8847; Venue ID mismatch |
| RC-04 | Head of Quant Execution | documentation_review | Is anything about to go live that shouldn't? | Strategy #5; Pre-trade testing |
| RC-05 | Chief Risk Officer | remediation_submission | My head of trading says the reporting is fine. Prove him wrong with specifics I can take to the board. | APX-2024-8847; Standard National Bank |
| RC-06 | Compliance Manager | best_execution_analysis | How did best execution hold up last quarter, venue by venue? | LSE (London); 98.2%; RTS 28 |
| RC-07 | Chief Compliance Officer | executive_summary | Generate the executive report and summarize what we accomplished in this review. | Compliance Scorecard; £847K; 80% |
