# Financial Advisor Agent — Complete Synthetic Records and Deterministic Outputs

> **AUTHORITATIVE FIXED SYNTHETIC SNAPSHOT.** Every record below is fictional and copied from the deterministic portable agent. Use only this file, the paired controls file, and the packaged skills. Do not browse, refresh from the current date, infer, enrich, substitute, or invent any fact.

## Source identity

- Portable source: `agents/@aibast-agents-library/financial_services_stacks/financial_advisor_copilot_stack/financial_advisor_copilot_agent.py`
- Source SHA-256: `b69a30049be7f2ec22efbae99bc4e5bd4bff20e35c47cf6bbd8b553b606cbf85`
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

## Evidence boundary

This snapshot does not authorize identity verification; investment, tax, legal, retirement, or financial advice; suitability or compliance determinations; account actions; live case transfer; outreach; money movement; order creation, routing, or execution. Missing evidence must be reported as absent. No browser lookup, external connector, message, approval, filing, account action, payment, order, transaction, or record change is available.
