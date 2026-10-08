# Utility Billing and Assistance Agent — Complete Synthetic Records

> COMPLETE SYNTHETIC PILOT DATA. Every organization, person, identifier, date, measurement, cost, score, status, and schedule below is fictional. Use only these records; do not supplement them with external facts.

## Provenance

- Deterministic source: `agents/@aibast-agents-library/slg_government_stacks/utility_billing_assistance_stack/utility_billing_assistance_agent.py`
- Captured source SHA-256: `ed02f2e42c47c1e04bf331e0941be5f59f9887fc9e268a520597d8819f33f33f`
- Locked case file: `tests/demo_cases/utility-billing-assistance.json`
- Locked case SHA-256: `a526a9c10ee4d2a04e1c22d076703a022664c1705af5e04731831ed97bbf699d`
- Strict isolation: `true`

## Demo case

RES-782MD, 782 Maple Drive (single-family residence, current, 8 years): $184.50 for 22,000 gallons versus a typical $48.20 for 4,500 gallons (389% above the 12-month baseline). 17,500 gallons ran Mar 10-13 at about 182 gallons per hour; Municipal Code 18.42 credit $97.80, new bill $86.70; income $32,400 = 68% of AMI (LIWAP $150 + LIHEAP $200 = $350); 6-month plan at $14.45 from April 15; free repairs ($85) proposed for Tuesday, April 2, 1:00-3:00 PM; total relief $447.80 plus $85 repairs. The demo video's own figures ($8.40 / $3.25 rates, $347.80 total relief) do not reconcile; these records use the consistent values above.


- Daily smart-meter reads for RES-782MD's billing period (hourly reads summed). Normal baseline: 150 gallons per day; a leak window is any day above 3x baseline.
- Credit = (current bill - typical bill) - excess gallons x water-only rate. RES-782MD: $136.30 - $38.50 = $97.80; new bill $86.70 (53% reduction).
- Assistance screens use 80% of the area median income ($47,650). RES-782MD: $32,400 = 68% of AMI.
- Accounts are flagged for a 30-day follow-up after the package (repair proof due).

## Record index

- `UTILITY_ACCOUNTS`
- `USAGE_HISTORY`
- `DAILY_USAGE`
- `RATE_STRUCTURES`
- `ASSISTANCE_PROGRAMS`
- `LEAK_ADJUSTMENT_POLICY`
- `AREA_MEDIAN_INCOME`
- `APPLICATION_TERMS`
- `REPAIR_PROGRAM`
- `FPL_REFERENCE_2025`

## UTILITY_ACCOUNTS

```json
{
  "RES-782MD": {
    "customer": "782 Maple Drive household",
    "address": "782 Maple Drive",
    "property": "single-family residence",
    "account_type": "residential",
    "services": [
      "water",
      "sewer",
      "stormwater"
    ],
    "status": "current",
    "balance_current": 184.5,
    "balance_past_due": 0.0,
    "autopay": false,
    "last_payment": {
      "date": "2024-02-20",
      "amount": 48.2
    },
    "meter": "Smart meter - hourly data available",
    "tenure_years": 8,
    "billing_period": "Feb 24 - Mar 28",
    "current_gallons": 22000,
    "typical_gallons": 4500,
    "typical_bill": 48.2,
    "prior_leak_adjustments": 0,
    "resident_age": 42,
    "household_income_estimate": 32400,
    "income_source": "estimated from property tax records"
  },
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

## DAILY_USAGE

```json
{
  "RES-782MD": [
    {
      "date": "Feb 24",
      "gallons": 150
    },
    {
      "date": "Feb 25",
      "gallons": 150
    },
    {
      "date": "Feb 26",
      "gallons": 150
    },
    {
      "date": "Feb 27",
      "gallons": 150
    },
    {
      "date": "Feb 28",
      "gallons": 150
    },
    {
      "date": "Feb 29",
      "gallons": 150
    },
    {
      "date": "Mar 1",
      "gallons": 150
    },
    {
      "date": "Mar 2",
      "gallons": 150
    },
    {
      "date": "Mar 3",
      "gallons": 150
    },
    {
      "date": "Mar 4",
      "gallons": 150
    },
    {
      "date": "Mar 5",
      "gallons": 150
    },
    {
      "date": "Mar 6",
      "gallons": 150
    },
    {
      "date": "Mar 7",
      "gallons": 150
    },
    {
      "date": "Mar 8",
      "gallons": 150
    },
    {
      "date": "Mar 9",
      "gallons": 150
    },
    {
      "date": "Mar 10",
      "gallons": 4375
    },
    {
      "date": "Mar 11",
      "gallons": 4375
    },
    {
      "date": "Mar 12",
      "gallons": 4375
    },
    {
      "date": "Mar 13",
      "gallons": 4375
    },
    {
      "date": "Mar 14",
      "gallons": 150
    },
    {
      "date": "Mar 15",
      "gallons": 150
    },
    {
      "date": "Mar 16",
      "gallons": 150
    },
    {
      "date": "Mar 17",
      "gallons": 150
    },
    {
      "date": "Mar 18",
      "gallons": 150
    },
    {
      "date": "Mar 19",
      "gallons": 150
    },
    {
      "date": "Mar 20",
      "gallons": 150
    },
    {
      "date": "Mar 21",
      "gallons": 150
    },
    {
      "date": "Mar 22",
      "gallons": 150
    },
    {
      "date": "Mar 23",
      "gallons": 150
    },
    {
      "date": "Mar 24",
      "gallons": 150
    },
    {
      "date": "Mar 25",
      "gallons": 150
    },
    {
      "date": "Mar 26",
      "gallons": 150
    },
    {
      "date": "Mar 27",
      "gallons": 150
    },
    {
      "date": "Mar 28",
      "gallons": 150
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
  "LIWAP": {
    "name": "Low-Income Water Assistance Program (LIWAP)",
    "eligibility": "Household income at or below 80% of area median income",
    "benefit": "Up to $150/year utility credit",
    "benefit_amount": 150,
    "documents_required": [
      "Proof of income - recent pay stubs or last year's tax return",
      "Copy of lease or property deed showing residency"
    ],
    "status": "accepting_applications"
  },
  "LIHEAP": {
    "name": "LIHEAP Emergency Utility Fund",
    "eligibility": "Household income at or below 80% of area median income",
    "benefit": "One-time $200 grant",
    "benefit_amount": 200,
    "documents_required": [
      "Proof of income",
      "Current utility bill"
    ],
    "status": "accepting_applications"
  },
  "senior_discount": {
    "name": "Senior Citizen Rate Discount",
    "eligibility": "Age 65+ and income at or below 80% of area median income",
    "benefit": "25% rate discount",
    "benefit_amount": 0,
    "documents_required": [
      "Proof of age",
      "Proof of income"
    ],
    "status": "accepting_applications"
  },
  "payment_plan": {
    "name": "Extended Payment Arrangement",
    "eligibility": "Any residential customer with a balance due",
    "benefit": "Up to 12 interest-free installments",
    "benefit_amount": 0,
    "documents_required": [
      "Signed payment agreement"
    ],
    "status": "always_available",
    "max_installments": 12,
    "default_installments": 6,
    "interest_pct": 0,
    "first_due": "April 15"
  }
}
```

## LEAK_ADJUSTMENT_POLICY

```json
{
  "code": "Municipal Code 18.42",
  "name": "One-time leak adjustment per household",
  "basis": "Excess volume above the 12-month typical usage is re-billed at the water-only rate and sewer charges on the excess are waived, because the leaked water did not enter the sewer system.",
  "water_only_rate_per_1000": 2.2,
  "repair_proof_days": 30,
  "repair_proof": "receipt or invoice",
  "one_time_only": true,
  "requirements": [
    "Documented repair (receipt or invoice) within 30 days",
    "No prior leak adjustment on the account",
    "Billing specialist approval"
  ]
}
```

## AREA_MEDIAN_INCOME

```json
47650
```

## APPLICATION_TERMS

```json
{
  "response_deadline_days": 14,
  "submission": "Online assistance portal",
  "delivery": "Email and postal mail"
}
```

## REPAIR_PROGRAM

```json
{
  "name": "Water Conservation Assistance Program",
  "eligibility": "Income-qualified residents (based on LIWAP income qualification)",
  "free_repairs": [
    "Toilet flapper",
    "faucet aerators",
    "leak detection"
  ],
  "additional_items": [
    "Low-flow showerhead",
    "leak detection dye tablets"
  ],
  "provider": "City Maintenance - licensed plumber",
  "proposed_slot": "Tuesday, April 2 (1:00-3:00 PM window)",
  "program_value": 85,
  "estimated_savings_gal_per_month": 6000
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
