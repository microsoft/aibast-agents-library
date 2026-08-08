# Discount Finder — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The suppliers, offers, terms, forecasts, dates,
> facilities, and spend values below are invented. They are sourcing-review
> evidence only and are not live pricing or realized savings.

## Discount and pricing opportunities

| ID | Supplier | Category | Exact signal | Current spend | Threshold | Gap | Review by / expires | Evidence source |
|---|---|---|---|---|---|---|---|---|
| DISC-101 | MedSupply Cooperative | Clinical consumables | 4% volume tier above $150,000 aggregated quarterly spend | $138,000 | $150,000 | $12,000 | 2026-09-30 | Synthetic master agreement section 7.2 |
| DISC-102 | Northstar Imaging | Imaging service renewals | 3% early-renewal credit when reviewed 60 days before renewal | $240,000 | Dated condition | $0 | 2026-08-31 | Synthetic renewal notice RN-204 |
| DISC-103 | CareTech Devices | Patient monitoring devices | Price increase of 5% announced after current quote window | $185,000 | Dated condition | $0 | 2026-10-15 | Synthetic pricing bulletin PB-88 |

## Demand-consolidation candidates

| Category | Facilities | Current suppliers | Combined spend | Review candidate |
|---|---|---|---|---|
| Clinical consumables | 4 | 3 | $214,000 | Aggregate forecast before requesting approved bids |
| Office and breakroom supplies | 5 | 4 | $92,000 | Standardize the basket before comparing contract tiers |

## Exact purchase-timing sequence

1. **Northstar Imaging / `DISC-102`:** review the renewal evidence before
   `2026-08-31`; do not renew automatically.
2. **MedSupply Cooperative / `DISC-101`:** validate whether approved demand can
   reach the synthetic volume tier before `2026-09-30`.
3. **CareTech Devices / `DISC-103`:** compare the announced price change before
   `2026-10-15` with demand, competitive bids, storage, warranty, and cash-flow
   constraints.
4. Prepare a sourcing-review brief with verified terms and alternatives for an
   authorized category manager. Do not contact a supplier or place anything.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| DISC-01 | Procurement Manager | savings_scan | Scan the upcoming healthcare purchases and show me which savings signals are worth validating. | DISC-101; DISC-102; not realized savings |
| DISC-02 | Category Buyer | time_sensitive_deals | Which pricing notices expire first, and what evidence should I verify before I act? | 2026-08-31; 2026-09-30; approved procurement process |
| DISC-03 | Finance Director | consolidation_analysis | Are our facilities buying the same categories separately enough to justify a sourcing review? | Clinical consumables; 4; does not recommend a supplier award |
| DISC-04 | Category Buyer | purchase_timing | Sequence the renewal, volume-tier, and price-change reviews without placing anything. | Northstar Imaging; MedSupply Cooperative; No supplier is selected |

## Required response headings and phrases

- Savings: `Savings Opportunity Scan`, IDs `DISC-101` and `DISC-102`, and
  `not realized savings`.
- Dated signals: `Time-Sensitive Pricing Review`, `2026-08-31`, `2026-09-30`,
  and `approved procurement process`.
- Consolidation: `Demand Consolidation Candidates`, `Clinical consumables`,
  `4` facilities, and `does not recommend a supplier award`.
- Timing: `Purchase Timing Review`, `Northstar Imaging`, `MedSupply
  Cooperative`, and `No supplier is selected`.
