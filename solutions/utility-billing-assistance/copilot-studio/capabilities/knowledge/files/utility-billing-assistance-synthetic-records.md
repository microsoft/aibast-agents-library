# Utility Billing and Assistance Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/slg_government_stacks/utility_billing_assistance_stack/utility_billing_assistance_agent.py`
- Captured source SHA-256: `ff1bddd2b0d822e2237ee0a50909f7fa38d3ee0c60c40e8a4cbc623bfbfef02a`
- Locked case file: `tests/demo_cases/utility-billing-assistance.json`
- Locked case SHA-256: `06362ed47c2cf30f4835499edb21cf9f218f1e939dc084fc6e02b7e856b8ccc7`
- Strict isolation: `true`

## Record index

- `UTILITY_ACCOUNTS`
- `USAGE_HISTORY`
- `RATE_STRUCTURES`
- `ASSISTANCE_PROGRAMS`
- `LEAK_ADJUSTMENT_POLICY`
- `FPL_REFERENCE_2025`

## UTILITY_ACCOUNTS

```json
{
  "ACCT-90001": {
    "customer": "Patricia Hernandez",
    "address": "1245 Cedar Lane",
    "account_type": "residential",
    "services": [
      "water",
      "sewer",
      "stormwater"
    ],
    "status": "active",
    "balance_current": 127.45,
    "balance_past_due": 0.0,
    "autopay": true,
    "last_payment": {
      "date": "2025-02-15",
      "amount": 118.9
    }
  },
  "ACCT-90002": {
    "customer": "Green Valley Shopping Center",
    "address": "5600 Commerce Blvd",
    "account_type": "commercial",
    "services": [
      "water",
      "sewer",
      "stormwater",
      "fire_line"
    ],
    "status": "active",
    "balance_current": 2845.6,
    "balance_past_due": 1420.3,
    "autopay": false,
    "last_payment": {
      "date": "2025-01-20",
      "amount": 2650.0
    }
  },
  "ACCT-90003": {
    "customer": "Robert & Linda Thompson",
    "address": "887 Willow Creek Dr",
    "account_type": "residential",
    "services": [
      "water",
      "sewer",
      "stormwater",
      "trash"
    ],
    "status": "delinquent",
    "balance_current": 245.8,
    "balance_past_due": 489.2,
    "autopay": false,
    "last_payment": {
      "date": "2024-11-18",
      "amount": 135.0
    }
  },
  "ACCT-90004": {
    "customer": "Sunnyvale Elementary School",
    "address": "300 Education Way",
    "account_type": "institutional",
    "services": [
      "water",
      "sewer",
      "stormwater",
      "irrigation"
    ],
    "status": "active",
    "balance_current": 1890.25,
    "balance_past_due": 0.0,
    "autopay": true,
    "last_payment": {
      "date": "2025-02-28",
      "amount": 1756.0
    }
  }
}
```

## USAGE_HISTORY

```json
{
  "ACCT-90001": [
    {
      "period": "2024-09",
      "water_gallons": 4200,
      "sewer_gallons": 3780,
      "amount": 98.5
    },
    {
      "period": "2024-10",
      "water_gallons": 3800,
      "sewer_gallons": 3420,
      "amount": 92.1
    },
    {
      "period": "2024-11",
      "water_gallons": 3100,
      "sewer_gallons": 2790,
      "amount": 84.3
    },
    {
      "period": "2024-12",
      "water_gallons": 2900,
      "sewer_gallons": 2610,
      "amount": 81.2
    },
    {
      "period": "2025-01",
      "water_gallons": 3000,
      "sewer_gallons": 2700,
      "amount": 82.9
    },
    {
      "period": "2025-02",
      "water_gallons": 3200,
      "sewer_gallons": 2880,
      "amount": 86.45
    }
  ],
  "ACCT-90003": [
    {
      "period": "2024-09",
      "water_gallons": 8500,
      "sewer_gallons": 7650,
      "amount": 145.2
    },
    {
      "period": "2024-10",
      "water_gallons": 9200,
      "sewer_gallons": 8280,
      "amount": 152.8
    },
    {
      "period": "2024-11",
      "water_gallons": 12400,
      "sewer_gallons": 11160,
      "amount": 198.5
    },
    {
      "period": "2024-12",
      "water_gallons": 14800,
      "sewer_gallons": 13320,
      "amount": 232.1
    },
    {
      "period": "2025-01",
      "water_gallons": 13200,
      "sewer_gallons": 11880,
      "amount": 215.4
    },
    {
      "period": "2025-02",
      "water_gallons": 11500,
      "sewer_gallons": 10350,
      "amount": 189.8
    }
  ]
}
```

## RATE_STRUCTURES

```json
{
  "water_residential": {
    "base_charge": 18.5,
    "tiers": [
      {
        "range": "0-3,000 gal",
        "rate_per_1000": 4.25
      },
      {
        "range": "3,001-6,000 gal",
        "rate_per_1000": 6.5
      },
      {
        "range": "6,001-10,000 gal",
        "rate_per_1000": 9.75
      },
      {
        "range": "Over 10,000 gal",
        "rate_per_1000": 14.0
      }
    ]
  },
  "water_commercial": {
    "base_charge": 45.0,
    "tiers": [
      {
        "range": "0-10,000 gal",
        "rate_per_1000": 5.8
      },
      {
        "range": "10,001-50,000 gal",
        "rate_per_1000": 5.25
      },
      {
        "range": "Over 50,000 gal",
        "rate_per_1000": 4.9
      }
    ]
  },
  "sewer": {
    "base_charge": 12.75,
    "rate_per_1000": 5.1
  },
  "stormwater": {
    "residential": 8.5,
    "commercial_per_eru": 8.5
  },
  "trash": {
    "residential": 22.0
  }
}
```

## ASSISTANCE_PROGRAMS

```json
{
  "LIHWAP": {
    "name": "Low-Income Household Water Assistance Program",
    "income_limit_pct_fpl": 150,
    "max_benefit": 1500,
    "eligibility": "Household income at or below 150% FPL",
    "documents_required": [
      "Proof of income",
      "Utility bill",
      "ID",
      "Household size verification"
    ],
    "status": "accepting_applications"
  },
  "senior_discount": {
    "name": "Senior Citizen Rate Discount",
    "income_limit_pct_fpl": 200,
    "max_benefit": 0,
    "eligibility": "Age 65+ and income at or below 200% FPL",
    "documents_required": [
      "Proof of age",
      "Proof of income",
      "Utility account number"
    ],
    "status": "accepting_applications",
    "discount_pct": 25
  },
  "arrearage_forgiveness": {
    "name": "COVID-19 Arrearage Forgiveness Program",
    "income_limit_pct_fpl": 200,
    "max_benefit": 3000,
    "eligibility": "Past-due balance accrued during March 2020 - December 2023",
    "documents_required": [
      "Utility account statement",
      "Income verification"
    ],
    "status": "limited_funds"
  },
  "payment_plan": {
    "name": "Extended Payment Arrangement",
    "income_limit_pct_fpl": 0,
    "max_benefit": 0,
    "eligibility": "Any customer with past-due balance over $100",
    "documents_required": [
      "Signed payment agreement"
    ],
    "status": "always_available",
    "max_installments": 12
  }
}
```

## LEAK_ADJUSTMENT_POLICY

```json
{
  "lookback_months": 2,
  "credit_rate_pct": 50,
  "requirements": [
    "Documented repair invoice or utility inspection",
    "No unresolved leak adjustment in the prior 24 months",
    "Billing specialist approval"
  ]
}
```

## FPL_REFERENCE_2025

> This exact table is embedded in the deterministic operation implementation.

```json
{
  "1": 15650,
  "2": 21150,
  "3": 26650,
  "4": 32150,
  "5": 37650
}
```

## Record-use boundary

- Values are fixed synthetic evidence, not live telemetry or customer records.
- An absent identifier must remain absent; never substitute a different record.
- A recommendation or draft is not proof that an external action occurred.
