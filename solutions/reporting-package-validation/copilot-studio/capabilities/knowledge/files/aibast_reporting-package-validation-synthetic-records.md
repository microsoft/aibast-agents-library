# Reporting Package Validation — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Proseware Holdings and every name, identifier, date, amount and
> score below are invented for demonstration. Never match them to a real organization or
> person, and never treat them as live data.

## Complete synthetic records

The records below are the complete data the agent uses (one fictional June close package with six files, four divisions, three scenarios, a driver bridge and thresholds).

```json
{
 "PACKAGE": {
  "id": "PKG-2026-06",
  "org": "Proseware Holdings",
  "period": "June 2026",
  "metric": "Operating income",
  "unit": "$K",
  "release_target": "Workday 5"
 },
 "FILES": [
  {
   "id": "FILE-01",
   "name": "Industrial division submission",
   "source": "General ledger extract",
   "received": "Jul 2 09:14",
   "checksum": "a41f09"
  },
  {
   "id": "FILE-02",
   "name": "Consumer division submission",
   "source": "General ledger extract",
   "received": "Jul 2 10:02",
   "checksum": "7c2be1"
  },
  {
   "id": "FILE-03",
   "name": "Services division submission",
   "source": "Planning system export",
   "received": "Jul 2 11:40",
   "checksum": "e90d35"
  },
  {
   "id": "FILE-04",
   "name": "Outdoor division submission",
   "source": "Planning system export",
   "received": "Jul 2 13:05",
   "checksum": "52aa7f"
  },
  {
   "id": "FILE-05",
   "name": "Consolidated summary",
   "source": "Consolidation workbook",
   "received": "Jul 2 15:22",
   "checksum": "b8e613"
  },
  {
   "id": "FILE-06",
   "name": "Driver bridge workbook",
   "source": "FP&A model",
   "received": "Jul 2 16:10",
   "checksum": "0f4c92"
  }
 ],
 "DIVISIONS": [
  "Industrial",
  "Consumer",
  "Services",
  "Outdoor"
 ],
 "SCENARIOS": [
  "Actual",
  "Budget",
  "Forecast"
 ],
 "CELLS": {
  "Industrial": {
   "Actual": 4820,
   "Budget": 4500,
   "Forecast": 4900
  },
  "Consumer": {
   "Actual": 3140,
   "Budget": 3400,
   "Forecast": 3200
  },
  "Services": {
   "Actual": 1960,
   "Budget": 1900,
   "Forecast": 0
  },
  "Outdoor": {
   "Actual": 880,
   "Budget": 1000,
   "Forecast": null
  }
 },
 "PRIOR_FORECAST": {
  "Services": 1950
 },
 "SCENARIO_LABELS": [
  {
   "raw": "Bud",
   "normalized": "Budget",
   "file": "FILE-03"
  },
  {
   "raw": "FCST",
   "normalized": "Forecast",
   "file": "FILE-04"
  }
 ],
 "CONSOLIDATED_ACTUAL": 10850,
 "BRIDGE": [
  {
   "driver": "Volume",
   "amount": 410
  },
  {
   "driver": "Price",
   "amount": 180
  },
  {
   "driver": "Mix",
   "amount": -230
  },
  {
   "driver": "Input cost",
   "amount": -320
  },
  {
   "driver": "Foreign exchange",
   "amount": -80
  }
 ],
 "BRIDGE_TOLERANCE": 25,
 "VARIANCE_ABS": 250,
 "VARIANCE_PCT": 5,
 "OWNERS": {
  "Industrial": "Industrial division controller",
  "Consumer": "Consumer division controller",
  "Services": "Services FP&A analyst",
  "Outdoor": "Outdoor division controller",
  "Consolidation": "Consolidation lead",
  "Bridge": "FP&A manager"
 }
}
```

## Locked-case evidence contract

Each locked case is one natural-language prompt routed to one operation. The answer must
contain every listed evidence value exactly as recorded.

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| RPV-01 | FP&A Manager | The June reporting package just landed. What did we receive and where did each file come from? | `package_intake` | PKG-2026-06; 6 files received; 11 of 12 |
| RPV-02 | Financial Controller | Run the integrity checks before anyone looks at the numbers. | `integrity_checks` | 2 blocking; Outdoor Forecast; A missing cell is not a zero |
| RPV-03 | FP&A Manager | How did each division do against budget, and which variances need an explanation? | `variance_analysis` | +$320K; -7.6%; offset each other |
| RPV-04 | FP&A Manager | Does the driver bridge reconcile from budget to actual? | `driver_reconciliation` | $10,760K; Unexplained residual; Does not reconcile |
| RPV-05 | Financial Controller | Route the exceptions to the right owners. | `exception_queue` | EX-01; Consolidation lead; none has been sent |
| RPV-06 | Finance Director | Draft the executive summary for the leadership pack. | `executive_summary` | on budget overall; Industrial +$320K; not released |

## Complete operation outputs

The deterministic output of every operation on the fixed snapshot follows. Answers must
keep these identifiers, figures and tables.

### RPV-01 — Package intake and lineage (`package_intake`)

# Package Intake - PKG-2026-06 (June 2026)

**Organization:** Proseware Holdings | **Metric:** Operating income ($K) | **Release target:** Workday 5

| File | Content | Source | Received | Checksum |
|------|---------|--------|----------|----------|
| FILE-01 | Industrial division submission | General ledger extract | Jul 2 09:14 | a41f09 |
| FILE-02 | Consumer division submission | General ledger extract | Jul 2 10:02 | 7c2be1 |
| FILE-03 | Services division submission | Planning system export | Jul 2 11:40 | e90d35 |
| FILE-04 | Outdoor division submission | Planning system export | Jul 2 13:05 | 52aa7f |
| FILE-05 | Consolidated summary | Consolidation workbook | Jul 2 15:22 | b8e613 |
| FILE-06 | Driver bridge workbook | FP&A model | Jul 2 16:10 | 0f4c92 |

**6 files received**, lineage frozen for each. Division cells: 11 of 12 expected (4 divisions x 3 scenarios).

Next: run the integrity checks before anyone reads the numbers.

> Synthetic finance review support only. Every figure is fictional. No journal was posted, no submission was changed, the package was not released, and no commentary was sent.

### RPV-02 — Integrity checks (`integrity_checks`)

# Integrity Checks - PKG-2026-06

**4 pass, 2 blocking, 2 advisory** of 8 checks.

| Check | Result | Evidence |
|-------|--------|----------|
| Source lineage stamped on every file | Pass | 6 of 6 files |
| Expected cells received | Blocking | 11 of 12; missing: Outdoor Forecast |
| Reported zeros confirmed | Advisory | Services Forecast reported as 0 (prior $1,950K) |
| Division sum ties to consolidated | Blocking | $10,800K vs $10,850K (difference $50K) |
| Scenario labels normalized | Pass | Bud -> Budget, FCST -> Forecast |
| Driver bridge reconciles | Advisory | Residual $40K vs tolerance $25K |
| Prior-period actuals unchanged | Pass | May 2026 actuals match the closed period |
| Formula links intact | Pass | No broken links in FILE-05 or FILE-06 |

A missing cell is not a zero: Outdoor Forecast was never submitted, while Services Forecast was reported as 0 and needs confirmation.
The package cannot be released while blocking checks are open.

> Synthetic finance review support only. Every figure is fictional. No journal was posted, no submission was changed, the package was not released, and no commentary was sent.

### RPV-03 — Variance against budget (`variance_analysis`)

# Actual vs Budget - Operating income, June 2026

| Division | Actual | Budget | Variance | Variance % | Explanation |
|----------|--------|--------|----------|------------|-------------|
| Industrial | $4,820K | $4,500K | +$320K | +7.1% | Required |
| Consumer | $3,140K | $3,400K | -$260K | -7.6% | Required |
| Services | $1,960K | $1,900K | +$60K | +3.2% | Not required |
| Outdoor | $880K | $1,000K | -$120K | -12.0% | Not required |
| **Total** | **$10,800K** | **$10,800K** | **+$0K** | | |

**Rule:** explanation required when a variance is at least $250K and 5% of budget.
**Read:** the total is on budget, but 2 divisions need explanations (Industrial, Consumer); their swings offset each other in the consolidated view.

> Synthetic finance review support only. Every figure is fictional. No journal was posted, no submission was changed, the package was not released, and no commentary was sent.

### RPV-04 — Driver bridge reconciliation (`driver_reconciliation`)

# Driver Bridge - Budget to Actual, June 2026

| Step | Amount |
|------|--------|
| Budget operating income | $10,800K |
| Volume | +$410K |
| Price | +$180K |
| Mix | -$230K |
| Input cost | -$320K |
| Foreign exchange | -$80K |
| Bridge-implied actual | $10,760K |
| Reported actual (division sum) | $10,800K |
| **Unexplained residual** | **+$40K** |

**Does not reconcile:** the residual of $40K exceeds the $25K tolerance. Route to the FP&A manager to find the missing driver.

> Synthetic finance review support only. Every figure is fictional. No journal was posted, no submission was changed, the package was not released, and no commentary was sent.

### RPV-05 — Exception routing (`exception_queue`)

# Exception Queue - PKG-2026-06

| ID | Type | Exception | Owner | Due |
|----|------|-----------|-------|-----|
| EX-01 | Blocking | Outdoor Forecast not submitted | Outdoor division controller | Workday 3 |
| EX-02 | Blocking | Consolidated total off by $50K | Consolidation lead | Workday 3 |
| EX-03 | Advisory | Services Forecast reported as 0 (prior $1,950K); confirm intended | Services FP&A analyst | Workday 4 |
| EX-04 | Advisory | Bridge residual $40K unexplained | FP&A manager | Workday 4 |
| EX-05 | Explanation | Industrial +$320K (+7.1%) vs budget | Industrial division controller | Workday 4 |
| EX-06 | Explanation | Consumer -$260K (-7.6%) vs budget | Consumer division controller | Workday 4 |

**6 exceptions:** 2 blocking, 2 advisory, 2 explanations. Release stays on hold until the 2 blocking items clear.
Owner requests are drafted for review; none has been sent.

> Synthetic finance review support only. Every figure is fictional. No journal was posted, no submission was changed, the package was not released, and no commentary was sent.

### RPV-06 — Executive summary draft (`executive_summary`)

# Executive Summary - DRAFT (June 2026)

**Headline:** operating income of $10,800K against a $10,800K budget (+$0K); on budget overall.
**Under the surface:** Industrial +$320K; Consumer -$260K; Services +$60K; Outdoor -$120K. Industrial volume and price gains offset Consumer mix and input-cost pressure.
**Watch items:** Outdoor forecast not yet submitted; bridge residual $40K under review.

Status: Draft - not released. 2 blocking exceptions must clear and the FP&A manager must sign off before this commentary enters the leadership pack.

> Synthetic finance review support only. Every figure is fictional. No journal was posted, no submission was changed, the package was not released, and no commentary was sent.
