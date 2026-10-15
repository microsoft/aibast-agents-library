# Financial Advisor Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/financial_advisor_copilot_stack/financial_advisor_copilot_agent.py`
- Source SHA-256: `79bee42d7de48881912c677a0bb842299343c9cfa0af19ba63f8d7727ff06e13`
- Expected tool: `FinancialAdvisorCopilotAgent`
- Snapshot behavior: fixed to the packaged source revision; no live connection or current-data claim.

## Complete deterministic source records

The following objects reproduce every packaged identifier, name, value, amount, date, status, rule, threshold, mapping, and relationship used by the agent. Keys and values are exact.

### `CLIENT_PORTFOLIOS`

```json
{
  "CLI-3001": {
    "advisor": "James Morrison, CFP",
    "age": 58,
    "annual_contributions": 45000,
    "annual_income": 285000,
    "holdings": {
      "Alternatives": {
        "allocation": 5.0,
        "target": 5.0,
        "value": 92500
      },
      "Cash & Equivalents": {
        "allocation": 10.0,
        "target": 5.0,
        "value": 185000
      },
      "Fixed Income": {
        "allocation": 35.0,
        "target": 30.0,
        "value": 647500
      },
      "International Equities": {
        "allocation": 10.0,
        "target": 15.0,
        "value": 185000
      },
      "Real Estate (REITs)": {
        "allocation": 10.0,
        "target": 10.0,
        "value": 185000
      },
      "US Equities": {
        "allocation": 30.0,
        "target": 35.0,
        "value": 555000
      }
    },
    "last_review": "2024-12-15",
    "name": "Robert & Susan Whitfield",
    "retirement_target": 67,
    "risk_profile": "moderate",
    "total_assets": 1850000
  },
  "CLI-3002": {
    "advisor": "James Morrison, CFP",
    "age": 34,
    "annual_contributions": 24000,
    "annual_income": 145000,
    "holdings": {
      "Alternatives": {
        "allocation": 5.0,
        "target": 5.0,
        "value": 21000
      },
      "Cash & Equivalents": {
        "allocation": 3.0,
        "target": 5.0,
        "value": 12600
      },
      "Emerging Markets": {
        "allocation": 12.0,
        "target": 15.0,
        "value": 50400
      },
      "Fixed Income": {
        "allocation": 10.0,
        "target": 10.0,
        "value": 42000
      },
      "International Equities": {
        "allocation": 20.0,
        "target": 20.0,
        "value": 84000
      },
      "US Equities": {
        "allocation": 50.0,
        "target": 45.0,
        "value": 210000
      }
    },
    "last_review": "2025-01-20",
    "name": "Angela Martinez",
    "retirement_target": 60,
    "risk_profile": "aggressive",
    "total_assets": 420000
  },
  "CLI-3003": {
    "advisor": "Patricia Lane, CFA",
    "age": 72,
    "annual_contributions": 0,
    "annual_income": 0,
    "holdings": {
      "Cash & Equivalents": {
        "allocation": 10.0,
        "target": 10.0,
        "value": 420000
      },
      "Fixed Income": {
        "allocation": 45.0,
        "target": 45.0,
        "value": 1890000
      },
      "International Equities": {
        "allocation": 5.0,
        "target": 5.0,
        "value": 210000
      },
      "Municipal Bonds": {
        "allocation": 20.0,
        "target": 20.0,
        "value": 840000
      },
      "Real Estate (REITs)": {
        "allocation": 5.0,
        "target": 5.0,
        "value": 210000
      },
      "US Equities": {
        "allocation": 15.0,
        "target": 15.0,
        "value": 630000
      }
    },
    "last_review": "2025-02-10",
    "name": "William Chen Trust",
    "retirement_target": 0,
    "risk_profile": "conservative",
    "total_assets": 4200000
  }
}
```

### `INVESTMENT_RECOMMENDATIONS`

```json
{
  "aggressive": [
    {
      "action": "Increase emerging markets allocation",
      "rationale": "Below target; favorable long-term growth outlook"
    },
    {
      "action": "Consider small-cap tilt",
      "rationale": "Long time horizon supports higher-volatility allocations"
    },
    {
      "action": "Build cash reserve to target 5%",
      "rationale": "Slightly underweight cash for opportunistic rebalancing"
    }
  ],
  "conservative": [
    {
      "action": "Maintain current allocation",
      "rationale": "Portfolio aligned with targets; no rebalancing needed"
    },
    {
      "action": "Review bond duration",
      "rationale": "Consider shortening duration if rate hikes expected"
    },
    {
      "action": "Tax-loss harvesting review",
      "rationale": "Identify unrealized losses for year-end tax planning"
    }
  ],
  "moderate": [
    {
      "action": "Rebalance to target allocation",
      "rationale": "Drift from target exceeds 3% in multiple asset classes"
    },
    {
      "action": "Reduce cash overweight",
      "rationale": "Excess cash drag on returns; deploy to equities"
    },
    {
      "action": "Increase international exposure",
      "rationale": "Underweight vs target; diversification benefit"
    }
  ]
}
```

### `COMPLIANCE_RULES`

```json
{
  "concentration_limit": {
    "applies_to": "all",
    "description": "No single position exceeds 10% of portfolio",
    "name": "Concentration Limit"
  },
  "form_crs": {
    "applies_to": "all",
    "description": "Relationship summary delivered at account opening and annually",
    "name": "Form CRS Delivery"
  },
  "reg_bi": {
    "applies_to": "all",
    "description": "Ensure recommendations are in client's best interest",
    "name": "Regulation Best Interest"
  },
  "senior_investor": {
    "applies_to": "seniors",
    "description": "Enhanced protections for clients age 65+",
    "name": "Senior Investor Protection"
  },
  "suitability": {
    "applies_to": "all",
    "description": "Investment recommendations suitable for client profile",
    "name": "Suitability Obligation"
  }
}
```

### `CLIENT_DIRECTORY`

```json
{
  "CLI-3001": {
    "name": "Robert & Susan Whitfield",
    "segment": "Advisory client"
  },
  "CLI-3002": {
    "name": "Angela Martinez",
    "segment": "Advisory client"
  },
  "CLI-3003": {
    "name": "William Chen Trust",
    "segment": "Advisory client"
  },
  "CLI-3004": {
    "name": "Jennifer Martinez and Emma Martinez",
    "segment": "Branch retail customer"
  }
}
```

### `RETAIL_CUSTOMERS`

```json
{
  "CLI-3004": {
    "advisor": "Sarah King, Education Planning Specialist",
    "age": 35,
    "beneficiary": {
      "age": 5,
      "dob": "March 15, 2019",
      "name": "Emma Martinez",
      "relationship": "daughter",
      "ssn_last4": "4321"
    },
    "comfort_allocation": {
      "equities": 35,
      "fixed_income": 65
    },
    "draft_reference": "VS1-8609E7B8",
    "goal": "Emma's college savings (college start 2037)",
    "high_interest_debt": "none reported",
    "household_income": 125000,
    "initial_deposit": 1000,
    "investment_experience": "Basic",
    "liquid_savings": 50000,
    "monthly_contribution": 300,
    "mortgage": 300000,
    "name": "Jennifer Martinez",
    "portfolio_choice": "Age-Based Conservative",
    "state": "California"
  }
}
```

### `EDUCATION_PLANS`

```json
{
  "California": {
    "expense_ratio": "~0.25%",
    "federal": "Growth is tax-deferred and withdrawals for qualified education expenses are federally tax-free",
    "opening_fee": "No account opening fee",
    "plan": "California ScholarShare 529",
    "portfolios": [
      [
        "Age-Based Aggressive",
        "starts ~90% equities, reduces over time"
      ],
      [
        "Age-Based Conservative",
        "starts ~75% equities, reduces quickly"
      ],
      [
        "Static Portfolios",
        "you choose and maintain the allocation"
      ],
      [
        "Single-Fund Options",
        "for custom building"
      ]
    ],
    "state_deduction": "California does not offer a state income tax deduction for 529 contributions"
  }
}
```

### `COLLEGE_COSTS`

```json
[
  {
    "projected_2037": 52685,
    "today": 25707,
    "type": "In-State Public"
  },
  {
    "projected_2037": 90160,
    "today": 44014,
    "type": "Out-of-State Public"
  },
  {
    "projected_2037": 117845,
    "today": 57570,
    "type": "Private Nonprofit"
  }
]
```

### `PLANNING_ASSUMPTIONS`

```json
{
  "annual_return": 0.05,
  "college_start_year": 2037,
  "demo_date": "Thursday, September 5, 2024",
  "tuition_inflation": "5% annual",
  "years_to_college": 13
}
```

### `ENROLLMENT_DOCUMENTS`

```json
[
  [
    "Account owner ID",
    "Driver's license or passport"
  ],
  [
    "Beneficiary's SSN",
    "You've provided Emma's last four; keep the full SSN handy"
  ],
  [
    "Proof of beneficiary's birth",
    "Certified birth certificate"
  ],
  [
    "Proof of address",
    "Utility bill, bank statement, or other acceptable document"
  ]
]
```

### `RISK_BANDS`

```json
[
  [
    0,
    34,
    "Very Conservative"
  ],
  [
    35,
    54,
    "Conservative"
  ],
  [
    55,
    74,
    "Moderate"
  ],
  [
    75,
    100,
    "Aggressive"
  ]
]
```

### `ADVISOR_SLOTS`

```json
{
  "channel": "Microsoft Teams",
  "date": "Tuesday, September 10, 2024",
  "duration": "30 minutes",
  "reminders": "24 hours, 1 hour, and 15 minutes before the meeting",
  "time": "3:30 PM PT",
  "type": "Investment Review"
}
```

### `SERVICE_REQUESTS`

```json
{
  "CLI-3001": {
    "request": "retirement review",
    "route": "Financial Advisor",
    "verification": "pending authorized check"
  },
  "CLI-3002": {
    "request": "portfolio review",
    "route": "Financial Advisor",
    "verification": "pending authorized check"
  },
  "CLI-3003": {
    "request": "trust distribution question",
    "route": "Senior Advisor",
    "verification": "pending authorized check"
  },
  "CLI-3004": {
    "request": "529 education savings account",
    "route": "Education Planning Specialist (Sarah King)",
    "verification": "pending authorized check"
  }
}
```

## Locked-case deterministic outputs

These are direct `perform()` results for the locked operation and arguments. Preserve the headings, identifiers, values, and boundary language.

### FAC-01 — Branch Banker

- Prompt: Who is waiting, what do they need, and where should I route them after identity checks?
- Operation: `service_intake`
- Arguments: `{}`
- Required factual anchors: `CLI-3001`, `No identity`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Branch Service Intake and Routing Preparation

| Client | Request | Identity Check | Proposed Route |
|---|---|---|---|
| Jennifer Martinez (CLI-3004) | 529 Education Savings Account | Pending Authorized Check | Education Planning Specialist (Sarah King) |
| Robert & Susan Whitfield (CLI-3001) | Retirement Review | Pending Authorized Check | Financial Advisor |
| Angela Martinez (CLI-3002) | Portfolio Review | Pending Authorized Check | Financial Advisor |
| William Chen Trust (CLI-3003) | Trust Distribution Question | Pending Authorized Check | Senior Advisor |

No identity has been verified and no service has been assigned. Follow approved customer-identification and routing procedures before proceeding.
```

### FAC-02 — Advisory Director

- Prompt: Summarize the advisor book and show which client is already retired.
- Operation: `client_review`
- Arguments: `{}`
- Required factual anchors: `CLI-3003`, `Retired`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Client Review Summary

| Client | Advisor | Risk | Assets | Age | Retirement In | Last Review |
|---|---|---|---|---|---|---|
| Robert & Susan Whitfield (CLI-3001) | James Morrison, CFP | Moderate | $1,850,000 | 58 | 9 yrs | 2024-12-15 |
| Angela Martinez (CLI-3002) | James Morrison, CFP | Aggressive | $420,000 | 34 | 26 yrs | 2025-01-20 |
| William Chen Trust (CLI-3003) | Patricia Lane, CFA | Conservative | $4,200,000 | 72 | Retired | 2025-02-10 |

**Total AUM:** $6,470,000
**Clients:** 3
```

### FAC-03 — Financial Advisor

- Prompt: Show the Whitfield allocation drift before our review meeting.
- Operation: `portfolio_summary`
- Arguments: `{"client_id": "CLI-3001"}`
- Required factual anchors: `Robert & Susan Whitfield`, `Cash & Equivalents`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Portfolio Summary: Robert & Susan Whitfield

- **Risk Profile:** Moderate
- **Total Assets:** $1,850,000
- **Annual Contributions:** $45,000
- **Max Allocation Drift:** 5.0%

## Holdings

| Asset Class | Value | Current % | Target % | Drift |
|---|---|---|---|---|
| US Equities | $555,000 | 30.0% | 35.0% | -5.0% |
| International Equities | $185,000 | 10.0% | 15.0% | -5.0% |
| Fixed Income | $647,500 | 35.0% | 30.0% | +5.0% |
| Real Estate (REITs) | $185,000 | 10.0% | 10.0% | 0.0% |
| Alternatives | $92,500 | 5.0% | 5.0% | 0.0% |
| Cash & Equivalents | $185,000 | 10.0% | 5.0% | +5.0% |
```

### FAC-04 — Financial Advisor

- Prompt: Prepare discussion candidates for Angela without giving advice or creating an order.
- Operation: `recommendation_engine`
- Arguments: `{"client_id": "CLI-3002"}`
- Required factual anchors: `Angela Martinez`, `not recommendations`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Advisor-Review Considerations: Angela Martinez

**Risk Profile:** Aggressive
**Years to Retirement:** 26

## Discussion Candidates

### 1. Increase emerging markets allocation

**Rationale:** Below target; favorable long-term growth outlook

### 2. Consider small-cap tilt

**Rationale:** Long time horizon supports higher-volatility allocations

### 3. Build cash reserve to target 5%

**Rationale:** Slightly underweight cash for opportunistic rebalancing

## Illustrative Allocation Differences

| Asset Class | Current | Target | Review Direction | Illustrative Amount |
|---|---|---|---|---|
| US Equities | 50.0% | 45.0% | Reduce candidate | $21,000 |
| Emerging Markets | 12.0% | 15.0% | Increase candidate | $12,600 |
| Cash & Equivalents | 3.0% | 5.0% | Increase candidate | $8,400 |

These are discussion candidates, not recommendations or orders. Validate objectives, risk tolerance, suitability, tax consequences, disclosures, and client consent.
```

### FAC-05 — Compliance Officer

- Prompt: Which client requires senior-investor controls, and what other checkpoints apply?
- Operation: `compliance_check`
- Arguments: `{}`
- Required factual anchors: `CLI-3003`, `Senior investor`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Compliance Check Report

## Regulatory Requirements

| Rule | Description | Applies To |
|---|---|---|
| Regulation Best Interest | Ensure recommendations are in client's best interest | All |
| Form CRS Delivery | Relationship summary delivered at account opening and annually | All |
| Suitability Obligation | Investment recommendations suitable for client profile | All |
| Concentration Limit | No single position exceeds 10% of portfolio | All |
| Senior Investor Protection | Enhanced protections for clients age 65+ | Seniors |

## Client Compliance Status

### Robert & Susan Whitfield (CLI-3001) — No Automated Flags

- No automated flags detected; complete normal compliance review

### Angela Martinez (CLI-3002) — No Automated Flags

- No automated flags detected; complete normal compliance review

### William Chen Trust (CLI-3003) — Review Flags Found

- **Flag:** Senior investor protections apply

```

### FAC-06 — Branch Banker

- Prompt: Draft the Whitfield handoff with request, identity status, risk context, and compliance flags.
- Operation: `advisor_handoff`
- Arguments: `{"client_id": "CLI-3001"}`
- Required factual anchors: `Robert & Susan Whitfield`, `no case transfer`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Draft Banker-to-Advisor Handoff: Robert & Susan Whitfield

- **Requested service:** retirement review
- **Identity status:** pending authorized check
- **Proposed route:** Financial Advisor
- **Risk profile on synthetic record:** Moderate
- **Portfolio drift:** 5.0%

## Compliance Context

- No automated flag; complete normal policy checks

Draft only. Confirm identity, consent, source records, and routing in approved systems; no case transfer or customer communication has occurred.
```

### FAC-07 — Branch Customer

- Prompt: I'd like to understand what 529 plan options are available. My daughter Emma is 5 years old, and we're in California. We can contribute about $300 per month.
- Operation: `plan_research`
- Arguments: `{"client_id": "CLI-3004"}`
- Required factual anchors: `California ScholarShare 529`, `~$65,730`, `~31%`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# 529 Plan Options: Jennifer Martinez — Emma Martinez (age 5), California

## Top Recommendation for Review — California ScholarShare 529

- No account opening fee and a low expense ratio (~0.25%)
- Age-based portfolios automatically shift from growth (equities) to conservative as college approaches
- Broad menu: low-cost index funds, socially responsible options, actively managed portfolios

## State-Specific Benefits

- California does not offer a state income tax deduction for 529 contributions
- Federal: Growth is tax-deferred and withdrawals for qualified education expenses are federally tax-free

## Your Contribution Scenario

| Item | Value |
|---|---|
| Monthly contribution | $300 |
| Time until college | 13 years (156 months) |
| Estimated return (conservative growth) | 5% annually |
| Projected value at age 18 | ~$65,730 |
| Projected in-state 4-year cost (2037) | ~$210,740 |
| Coverage | ~31% |

Assumes steady monthly contributions and no lump-sum deposits.

## Portfolio Choices

1. **Age-Based Aggressive** — starts ~90% equities, reduces over time
2. **Age-Based Conservative** — starts ~75% equities, reduces quickly (fits a conservative approach)
3. **Static Portfolios** — you choose and maintain the allocation
4. **Single-Fund Options** — for custom building

**Next step:** model higher contribution levels or a different risk track to raise the ~31% coverage; a licensed advisor confirms suitability before enrollment.
```

### FAC-08 — Branch Customer

- Prompt: Can you walk me through what's needed to complete the 529 enrollment? I want to make sure I have all the required documents.
- Operation: `enrollment_checklist`
- Arguments: `{"client_id": "CLI-3004"}`
- Required factual anchors: `Proof of address`, `$1,000 initial deposit`, `20-30 minutes`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# 529 Enrollment Checklist: Jennifer Martinez for Emma Martinez

| Step | Item | Status |
|---|---|---|
| 1 | Risk profile | Complete |
| 2 | Investment choice: Age-Based Conservative | Complete |
| 3 | Gather required documents (below) | Needed |
| 4 | Funding setup: $1,000 initial deposit method + account for $300/month automatic contribution | Needed |
| 5 | Submit & acknowledge: complete the form, acknowledge risk profile and disclosures, sign electronically or in-branch | Needed |

## Step 3 — Required Documents

1. **Account owner ID** — Driver's license or passport
2. **Beneficiary's SSN** — You've provided Emma's last four; keep the full SSN handy
3. **Proof of beneficiary's birth** — Certified birth certificate
4. **Proof of address** — Utility bill, bank statement, or other acceptable document

**Estimated time:** 20-30 minutes once documents are ready.
**Your status:** risk profile complete, investment choice made — finalize forms and present documents.
```

### FAC-09 — Branch Customer

- Prompt: Great, let's open a 529 account. Emma was born on March 15, 2019, and her SSN ends in 4321. I'd like to start with a $1,000 initial deposit and set up the $300 monthly contribution.
- Operation: `account_onboarding`
- Arguments: `{"client_id": "CLI-3004"}`
- Required factual anchors: `VS1-8609E7B8`, `Not Submitted`, `no account was opened`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# 529 Account Application — Prefilled Draft, Not Submitted

| Field | Value |
|---|---|
| Draft reference | VS1-8609E7B8 |
| Owner | Jennifer Martinez |
| Beneficiary | Emma Martinez (age 5, born March 15, 2019, SSN ending 4321) |
| Time to college start | 13 years |
| Plan | California ScholarShare 529 (Conservative, Age-Based Allocation) |
| Initial deposit | $1,000 — ready to fund at submission |
| Monthly contribution | $300 — schedule prefilled |

## Pre-checks

| Check | Result |
|---|---|
| Required application fields | Complete |
| Beneficiary DOB and SSN last four match the customer record | Match (March 15, 2019, 4321) |
| Beneficiary eligibility (under 18, US resident) | Eligible on record |
| KYC / identity verification | Ready for banker verification with the documents listed |

The application is ready for you and the banker to submit. Not submitted: no account was opened and no deposit was processed. **Next:** schedule the investment review with Sarah King to fine-tune the portfolio mix.
```

### FAC-10 — Branch Customer

- Prompt: Can you show me what college might cost when Emma turns 18? I want to understand if $300 per month will be enough.
- Operation: `college_cost_projection`
- Arguments: `{"client_id": "CLI-3004"}`
- Required factual anchors: `~$210,740`, `~$145,010`, `$950/month`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Projected College Costs in 2037 — Emma Martinez at 18

Based on historical averages and 5% annual tuition inflation; tuition, fees, room & board.

| School Type | Today's Avg. Annual Cost | 2037 Projected Annual | 4-Year Total |
|---|---|---|---|
| In-State Public | $25,707 | ~$52,685 | ~$210,740 |
| Out-of-State Public | $44,014 | ~$90,160 | ~$360,640 |
| Private Nonprofit | $57,570 | ~$117,845 | ~$471,380 |

## Your $300/Month Plan — Projection

| Item | Value |
|---|---|
| Initial deposit | $1,000 |
| Monthly contribution | $300 |
| Time to college | 13 years |
| Assumed growth (Age-Based Conservative portfolio) | 5% annually |
| Value at 18 from monthly contributions | ~$65,730 |
| Covers | ~31% of the in-state 4-year cost |
| Shortfall | ~$145,010 |

The $1,000 initial deposit is extra buffer on top (about $1,910 by 2037); it is not counted in the coverage above.

**Is $300/month enough?** Not for the full in-state cost: fully funding ~$210,740 by 2037 takes about $950/month. The shortfall could be covered by increasing contributions, scholarships, or loans; an advisor can model the options.
```

### FAC-11 — Branch Customer

- Prompt: I'm 35 years old, our household income is $125,000, and we have about $50,000 in liquid savings. I've done some basic investing before but nothing extensive. We also have a mortgage of about $300,000.
- Operation: `risk_assessment`
- Arguments: `{"client_id": "CLI-3004"}`
- Required factual anchors: `Conservative (Score: 45/100)`, `35% equities`, `advisor review`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Risk Assessment: Jennifer Martinez

**Profile:** Conservative (Score: 45/100)  
**Investment experience:** Basic  
**Income & liquidity:** $125,000 household income, $50,000 in liquid savings  
**Debt:** $300,000 mortgage (no red flags unless high-interest)  
**Suitability status:** Consistent with an age-based 529 — for licensed-advisor confirmation

| Questionnaire factor | Points |
|---|---|
| Time horizon (age 35) | 15 |
| Household income $125,000 | 10 |
| Liquid savings $50,000 (40% of income) | 10 |
| Debt: $300,000 mortgage, high-interest debt none reported | 5 |
| Investment experience: Basic | 5 |
| **Total** | **45** |

## Allocation Guidance

- Your personal comfort level: 35% equities / 65% fixed income (lower volatility)
- Age-based 529 track for Emma Martinez (age 5): ~75% equities now, shifting to bonds by college
- Why the difference? The education timeline is fixed and age-based plans front-load growth to offset rising tuition, then de-risk automatically.

## 529 Funding Check

- Fully funding the in-state 4-year cost (~$210,740 by 2037) takes about $950/month
- Your planned $300/month covers ~31%; the $50,000 in savings stays available as an emergency fund

**Key note:** if any debt beyond the mortgage is high-interest, reduce it before increasing contributions.

This is a questionnaire summary for advisor review, not investment advice.
```

### FAC-12 — Branch Customer

- Prompt: I'd like to schedule a follow-up meeting with a financial advisor to review the investment options in more detail. Can we set something up, preferably Tuesday afternoon? I prefer a Teams call.
- Operation: `schedule_followup`
- Arguments: `{"client_id": "CLI-3004"}`
- Required factual anchors: `Tuesday, September 10, 2024`, `Sarah King`, `no invite was sent`

```text
> **SYNTHETIC DEMO DATA — LICENSED ADVISOR REVIEW REQUIRED.** Fictional clients and holdings only. This is not investment, tax, legal, or financial advice; no identity was verified, no account was opened, and no order, transaction, transfer, or customer communication occurred.

# Proposed Investment Review — Draft Invite, Not Sent

| Detail | Value |
|---|---|
| Date / time | Tuesday, September 10, 2024 — 3:30 PM PT (30 minutes) |
| Type | Investment Review |
| Participants | Jennifer Martinez & Sarah King, Education Planning Specialist |
| Location | Microsoft Teams (join link created when the invite is sent) |
| Reminders | 24 hours, 1 hour, and 15 minutes before the meeting |

## Context Passed to the Advisor (draft handoff)

- **Customer:** Jennifer Martinez (CLI-3004), age 35, California
- **Requested service:** 529 education savings account
- **Identity status:** pending authorized check
- **Goal:** Emma's college savings (college start 2037); beneficiary Emma Martinez (age 5)
- **Plan chosen:** California ScholarShare 529 (Age-Based Conservative); $1,000 initial + $300/month
- **Projection:** ~$65,730 at 18 covers ~31% of the ~$210,740 in-state 4-year cost; shortfall ~$145,010
- **Risk questionnaire:** Conservative (45/100), experience Basic
- **Draft application reference:** VS1-8609E7B8 (not submitted)
- **Open questions:** contribution increase scenarios; portfolio mix (comfort 35/65 vs ~75% equities in the age-based track)

The Outlook / Teams invite is ready for you to send; no invite was sent and no case transfer or customer communication has occurred. **Next:** prepare a portfolio comparison report before the call.
```

## Evidence boundary

This snapshot does not authorize identity verification; investment, tax, legal, retirement, or financial advice; suitability or compliance determinations; account actions; live case transfer; outreach; money movement; order creation, routing, or execution. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
