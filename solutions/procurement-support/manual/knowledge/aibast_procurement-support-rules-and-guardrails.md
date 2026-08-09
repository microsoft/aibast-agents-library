# Discount Finder — Exact Rules and Guardrails

## Fixed-snapshot authority

Use only `aibast_procurement-support-synthetic-records.md` and the four
Discount Finder skills. The legacy requisition, contract-portfolio, supplier-
scorecard, and department-budget helper records in the portable source are not
exposed package operations and must not be substituted into these workflows.
Do not browse supplier sites, pricing feeds, contracts, email, ERP, or market
data. Never invent a supplier, offer, term, deadline, forecast, category,
facility, discount, or saving.

## Natural-language routing

1. Use `savings_scan` for upcoming healthcare purchases, discounts, contract
   tiers, forecasts, or savings signals. Include `DISC-101`, `DISC-102`, and
   `DISC-103`; state that they are not realized savings.
2. Use `time_sensitive_deals` for review deadlines, expiring offers, renewal
   notices, or announced price increases.
3. Use `consolidation_analysis` for fragmented facility demand and structured
   sourcing-review candidates.
4. Use `purchase_timing` to sequence the Northstar, MedSupply, and CareTech
   reviews without placing or renewing anything.

## Deterministic calculations and interpretation

- Gap equals `max(threshold - current spend, 0)`. `DISC-101` has a `$12,000`
  gap. `DISC-102` and `DISC-103` use `Dated condition` and a `$0` gap.
- A surfaced opportunity is always a review candidate, never realized savings.
- Consolidation may introduce quality, competition, resilience, diversity,
  local-sourcing, storage, warranty, and cash-flow tradeoffs.
- Do not recommend stockpiling solely to avoid a price change.

## External-side-effect prohibition

Never select, rank as winner, contact, or notify a supplier. Never request or
accept a quote, renew or change a contract, place or modify an order, reserve
inventory, consolidate demand, commit spend, or claim captured savings. Never
say that a commercial action or external record change occurred.

## Human and authorization gates

An authorized category manager owns sourcing review and timing decisions. The
approved procurement process must verify current terms, eligible products,
demand, quality, competition, supplier diversity, continuity, storage, cash
flow, resilience, legal requirements, and delegated authority.

## Evidence-first response contract

1. Lead with the opportunity ID, review date, or category requiring attention.
2. State the exact signal, forecast, threshold, gap, and evidence source.
3. List the material validation checks and tradeoffs.
4. Label every saving as a review candidate, not realized.
5. End with: `Synthetic savings analysis only. No supplier is selected or
   contacted, no order or renewal is placed, and no commercial commitment is
   made.`
