# M&A Target Sourcing — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Fabrikam Information Services and every name, identifier, date, amount and
> score below are invented for demonstration. Never match them to a real organization or
> person, and never treat them as live data.

## Complete synthetic records

The records below are the complete data the agent uses (eight fictional companies, one acquisition thesis, scoring weights, evidence sources and the memo draft).

```json
{
 "SNAPSHOT_DATE": "2026-06-30",
 "STALE_BEFORE": "2025-06-30",
 "THESIS": {
  "id": "TH-2026-014",
  "acquirer": "Fabrikam Information Services",
  "objective": "Add compliance and regulatory workflow software in Europe",
  "sector": "Compliance and regulatory workflow software",
  "region": "Europe",
  "min_revenue": 20,
  "max_revenue": 120,
  "positive_ebitda": true
 },
 "WEIGHTS": {
  "strategy": 40,
  "financial": 30,
  "market": 15,
  "execution": 15
 },
 "ALT_WEIGHTINGS": [
  {
   "name": "Base thesis",
   "strategy": 40,
   "financial": 30,
   "market": 15,
   "execution": 15
  },
  {
   "name": "Financial-first",
   "strategy": 25,
   "financial": 45,
   "market": 15,
   "execution": 15
  },
  {
   "name": "Equal weights",
   "strategy": 25,
   "financial": 25,
   "market": 25,
   "execution": 25
  }
 ],
 "CRITERIA_LABELS": {
  "strategy": "Strategy fit",
  "financial": "Financial quality",
  "market": "Market signal",
  "execution": "Execution fit"
 },
 "TARGETS": {
  "T-01": {
   "name": "Lumenrock Compliance Systems",
   "focus": "Regulatory change and policy workflow",
   "region": "Europe",
   "revenue": 64,
   "ebitda": 14.1,
   "growth": 18,
   "recurring": 88,
   "scores": {
    "strategy": 92,
    "financial": 84,
    "market": 78,
    "execution": 80
   },
   "risks": [
    "Top five clients are 31% of revenue",
    "Founder-led sales motion"
   ],
   "questions": [
    "How concentrated is renewal exposure in the next 18 months?",
    "Which product modules are sold standalone versus bundled?",
    "What would it take to move sales beyond the founders?"
   ],
   "evidence": [
    {
     "id": "T-01-S1",
     "type": "Financials",
     "title": "FY2025 audited summary (synthetic)",
     "date": "2026-03-31"
    },
    {
     "id": "T-01-S2",
     "type": "Product",
     "title": "Analyst product review (synthetic)",
     "date": "2026-05-12"
    },
    {
     "id": "T-01-S3",
     "type": "Customer",
     "title": "Customer reference notes (synthetic)",
     "date": "2025-11-04"
    }
   ]
  },
  "T-02": {
   "name": "Veridane Analytics",
   "focus": "Risk analytics for compliance teams",
   "region": "Europe",
   "revenue": 38,
   "ebitda": 6.5,
   "growth": 24,
   "recurring": 81,
   "scores": {
    "strategy": 74,
    "financial": 80,
    "market": 86,
    "execution": 70
   },
   "risks": [
    "Partner-dependent distribution"
   ],
   "questions": [
    "What share of new bookings comes through partners?",
    "How portable is the analytics engine to our data platform?",
    "Which retention terms apply to the partner contracts?"
   ],
   "evidence": [
    {
     "id": "T-02-S1",
     "type": "Financials",
     "title": "Management accounts (synthetic)",
     "date": "2025-12-31"
    },
    {
     "id": "T-02-S2",
     "type": "Customer",
     "title": "Customer survey extract (synthetic)",
     "date": "2026-04-02"
    }
   ]
  },
  "T-03": {
   "name": "Halverd Audit Cloud",
   "focus": "Audit and controls workflow",
   "region": "Europe",
   "revenue": 92,
   "ebitda": 17.5,
   "growth": 11,
   "recurring": 76,
   "scores": {
    "strategy": 88,
    "financial": 72,
    "market": 70,
    "execution": 62
   },
   "risks": [
    "Platform migration underway",
    "Two-country operating model"
   ],
   "questions": [
    "When does the platform migration finish, and at what cost?",
    "How are the two country entities integrated today?",
    "What is net revenue retention after the migration?"
   ],
   "evidence": [
    {
     "id": "T-03-S1",
     "type": "Financials",
     "title": "FY2024 filed accounts (synthetic)",
     "date": "2025-03-31"
    },
    {
     "id": "T-03-S2",
     "type": "Product",
     "title": "Product roadmap brief (synthetic)",
     "date": "2026-01-15"
    },
    {
     "id": "T-03-S3",
     "type": "Customer",
     "title": "Customer reference notes (synthetic)",
     "date": "2026-05-20"
    }
   ]
  },
  "T-04": {
   "name": "Brightquay Reg Data",
   "focus": "Regulatory data feeds",
   "region": "North America",
   "revenue": 55,
   "ebitda": 9.9,
   "growth": 14,
   "recurring": 90,
   "scores": {
    "strategy": 80,
    "financial": 82,
    "market": 74,
    "execution": 72
   },
   "risks": [
    "Outside the thesis region"
   ],
   "questions": [],
   "evidence": []
  },
  "T-05": {
   "name": "Oskarvale Workflow",
   "focus": "Compliance case management",
   "region": "Europe",
   "revenue": 21,
   "ebitda": -1.8,
   "growth": 32,
   "recurring": 79,
   "scores": {
    "strategy": 78,
    "financial": 40,
    "market": 80,
    "execution": 66
   },
   "risks": [
    "Loss-making"
   ],
   "questions": [],
   "evidence": []
  },
  "T-06": {
   "name": "Cindral Risk Labs",
   "focus": "Enterprise risk platform",
   "region": "Europe",
   "revenue": 140,
   "ebitda": 25.2,
   "growth": 9,
   "recurring": 83,
   "scores": {
    "strategy": 70,
    "financial": 78,
    "market": 68,
    "execution": 58
   },
   "risks": [
    "Above the revenue band"
   ],
   "questions": [],
   "evidence": []
  },
  "T-07": {
   "name": "Tessaline Controls",
   "focus": "Compliance controls testing",
   "region": "Europe",
   "revenue": 47,
   "ebitda": 7.1,
   "growth": 15,
   "recurring": 84,
   "scores": {
    "strategy": 84,
    "financial": 76,
    "market": 72,
    "execution": 84
   },
   "risks": [
    "Single product line"
   ],
   "questions": [
    "How much of the pipeline depends on the single product line?",
    "Which adjacent modules are on the near-term roadmap?",
    "What does the integration effort look like for our platform?"
   ],
   "evidence": [
    {
     "id": "T-07-S1",
     "type": "Financials",
     "title": "Management accounts (synthetic)",
     "date": "2026-02-28"
    },
    {
     "id": "T-07-S2",
     "type": "Product",
     "title": "Product review (synthetic)",
     "date": "2025-04-18"
    }
   ]
  },
  "T-08": {
   "name": "Marrowgate Reporting",
   "focus": "Regulatory reporting templates",
   "region": "Europe",
   "revenue": 29,
   "ebitda": 4.4,
   "growth": 9,
   "recurring": 70,
   "scores": {
    "strategy": 60,
    "financial": 58,
    "market": 56,
    "execution": 78
   },
   "risks": [
    "Low growth"
   ],
   "questions": [
    "What is driving the slower growth?",
    "How many templates are customer-specific?",
    "Which renewals are at risk this year?"
   ],
   "evidence": [
    {
     "id": "T-08-S1",
     "type": "Financials",
     "title": "Management accounts (synthetic)",
     "date": "2026-01-31"
    }
   ]
  }
 },
 "REQUIRED_EVIDENCE": [
  "Financials",
  "Product",
  "Customer"
 ],
 "SHORTLIST_SIZE": 3
}
```

## Locked-case evidence contract

Each locked case is one natural-language prompt routed to one operation. The answer must
contain every listed evidence value exactly as recorded.

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| MATS-01 | Corporate Development Associate | We want to buy a profitable compliance-workflow software company in Europe within our revenue band. Turn that into a screen we can run. | `build_thesis` | TH-2026-014; 5 of 8 pass; Cindral Risk Labs |
| MATS-02 | Corporate Development Associate | Run the screen and rank the companies that pass. | `screen_targets` | Lumenrock Compliance Systems; 85.7; 79.8 |
| MATS-03 | Corporate Development Associate | Give me the dossier on the top-ranked target, with its sources and diligence questions. | `target_dossier` | T-01-S1; 22.0% margin; Diligence questions |
| MATS-04 | Head of Corporate Development | Does the ranking hold if we weight financial quality more heavily? | `challenge_ranking` | Financial-first; 84.5; top 3 holds under all 3 weightings |
| MATS-05 | Research Analyst | Where is our evidence thin or out of date? | `evidence_gaps` | RR-01; 6 evidence gaps across 4 targets; none has been sent |
| MATS-06 | Head of Corporate Development | Draft the screening memo for the investment committee. | `ic_memo_draft` | ICM-2026-07-01; $149M; Not sent; no target contacted |

## Complete operation outputs

The deterministic output of every operation on the fixed snapshot follows. Answers must
keep these identifiers, figures and tables.

### MATS-01 — Thesis to screening criteria (`build_thesis`)

# Screening Criteria - TH-2026-014

**Acquirer:** Fabrikam Information Services | **Objective:** Add compliance and regulatory workflow software in Europe

| Criterion | Setting |
|-----------|---------|
| Sector focus | Compliance and regulatory workflow software |
| Region | Europe |
| Revenue band | $20M-$120M |
| Profitability | Positive EBITDA required |
| Score weights | Strategy fit 40%, financial quality 30%, market signal 15%, execution fit 15% |

**Universe:** 8 synthetic companies; **5 of 8 pass** the filters.

| Excluded | Company | Reason |
|----------|---------|--------|
| T-04 | Brightquay Reg Data | Region North America is outside Europe |
| T-05 | Oskarvale Workflow | EBITDA $-1.8M is not positive |
| T-06 | Cindral Risk Labs | Revenue $140M is outside the $20M-$120M band |

Next: run the screen and rank the targets that pass.

> Synthetic screening support only. All companies, financials and sources are fictional. No target was contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made.

### MATS-02 — Ranked target longlist (`screen_targets`)

# Ranked Longlist - TH-2026-014

5 targets pass the screen (snapshot 2026-06-30). Weighted score = strategy fit 40% + financial quality 30% + market signal 15% + execution fit 15%.

| Rank | Target | Company | Revenue | EBITDA | Growth | Score |
|------|--------|---------|---------|--------|--------|-------|
| 1 | T-01 | Lumenrock Compliance Systems | $64M | $14.1M | 18% | 85.7 |
| 2 | T-07 | Tessaline Controls | $47M | $7.1M | 15% | 79.8 |
| 3 | T-02 | Veridane Analytics | $38M | $6.5M | 24% | 77.0 |
| 4 | T-03 | Halverd Audit Cloud | $92M | $17.5M | 11% | 76.6 |
| 5 | T-08 | Marrowgate Reporting | $29M | $4.4M | 9% | 61.5 |

**Shortlist (top 3):** T-01 Lumenrock Compliance Systems, T-07 Tessaline Controls, T-02 Veridane Analytics.
**Leader:** T-01 Lumenrock Compliance Systems at 85.7.

Next: open the dossier on the top-ranked target.

> Synthetic screening support only. All companies, financials and sources are fictional. No target was contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made.

### MATS-03 — Cited target dossier (`target_dossier`)

# Target Dossier - T-01 Lumenrock Compliance Systems

**Focus:** Regulatory change and policy workflow | **Region:** Europe | **Rank:** 1 of 5 | **Weighted score:** 85.7

| Synthetic financials | Value |
|----------------------|-------|
| Revenue | $64M |
| EBITDA | $14.1M (22.0% margin) |
| Revenue growth | 18% |
| Recurring revenue | 88% |

| Criterion | Score | Weight |
|-----------|-------|--------|
| Strategy fit | 92 | 40% |
| Financial quality | 84 | 30% |
| Market signal | 78 | 15% |
| Execution fit | 80 | 15% |

**Risk flags:** Top five clients are 31% of revenue; Founder-led sales motion.

**Sources:**
- [T-01-S1] Financials: FY2025 audited summary (synthetic), 2026-03-31
- [T-01-S2] Product: Analyst product review (synthetic), 2026-05-12
- [T-01-S3] Customer: Customer reference notes (synthetic), 2025-11-04

**Diligence questions:**
1. How concentrated is renewal exposure in the next 18 months?
2. Which product modules are sold standalone versus bundled?
3. What would it take to move sales beyond the founders?

> Synthetic screening support only. All companies, financials and sources are fictional. No target was contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made.

### MATS-04 — Weighting challenge (`challenge_ranking`)

# Ranking Challenge - Three Weightings

| Target | Base thesis | Financial-first | Equal weights |
|--------|------|------|------|
| T-01 Lumenrock Compliance Systems | 85.7 | 84.5 | 83.5 |
| T-07 Tessaline Controls | 79.8 | 78.6 | 79.0 |
| T-02 Veridane Analytics | 77.0 | 77.9 | 77.5 |
| T-03 Halverd Audit Cloud | 76.6 | 74.2 | 73.0 |
| T-08 Marrowgate Reporting | 61.5 | 61.2 | 63.0 |

**Verdict:** The top 3 holds under all 3 weightings.
**Watch:** the gap between rank 2 (T-07) and rank 3 (T-02) narrows from 2.8 to 0.7 points under Financial-first, so treat them as close.

Next: check where the evidence behind the shortlist is thin or out of date.

> Synthetic screening support only. All companies, financials and sources are fictional. No target was contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made.

### MATS-05 — Evidence-gap review (`evidence_gaps`)

# Evidence Coverage - Snapshot 2026-06-30

Required per target: Financials, Product, Customer. Sources dated before 2025-06-30 are stale.

| Request | Target | Evidence | Issue | Detail | Shortlist |
|---------|--------|----------|-------|--------|-----------|
| RR-01 | T-07 | Product | Stale | T-07-S2 dated 2025-04-18 | Yes |
| RR-02 | T-07 | Customer | Missing | No source on file | Yes |
| RR-03 | T-02 | Product | Missing | No source on file | Yes |
| RR-04 | T-03 | Financials | Stale | T-03-S1 dated 2025-03-31 | No |
| RR-05 | T-08 | Product | Missing | No source on file | No |
| RR-06 | T-08 | Customer | Missing | No source on file | No |

**6 evidence gaps across 4 targets; 3 sit on the shortlist.** T-01 Lumenrock Compliance Systems has complete, current evidence.

The research requests above are drafts for the research team; none has been sent.

> Synthetic screening support only. All companies, financials and sources are fictional. No target was contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made.

### MATS-06 — Investment committee memo draft (`ic_memo_draft`)

# Investment Committee Screening Memo - DRAFT ICM-2026-07-01

**Thesis:** TH-2026-014 Add compliance and regulatory workflow software in Europe | **Universe:** 8 | **Passed screen:** 5 | **Shortlist:** 3

| Rank | Target | Company | Score | Revenue | Key risk |
|------|--------|---------|-------|---------|----------|
| 1 | T-01 | Lumenrock Compliance Systems | 85.7 | $64M | Top five clients are 31% of revenue |
| 2 | T-07 | Tessaline Controls | 79.8 | $47M | Single product line |
| 3 | T-02 | Veridane Analytics | 77.0 | $38M | Partner-dependent distribution |

**Combined shortlist revenue:** $149M. **Ranking check:** top 3 stable under 3 weightings.
**Conditions before outreach:** close 3 open evidence gaps on the shortlist; the corporate development lead approves any first contact.
**Ask of the committee:** approve the shortlist for confidential management outreach planning.

Status: Draft for the corporate development lead. Not sent; no target contacted.

> Synthetic screening support only. All companies, financials and sources are fictional. No target was contacted, no CRM or deal record was changed, nothing was shared, and no investment decision was made.
