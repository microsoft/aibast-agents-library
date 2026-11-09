# Discount Finder — Exact Rules and Guardrails

## Fixed-snapshot authority

Use only `aibast_procurement-support-synthetic-records.md` and the six Discount Finder skills. Do not browse supplier
sites, pricing feeds, contracts, email, ERP, or market data. Never invent a supplier, offer, term, deadline, quantity,
price, license, discount, or saving.

## Natural-language routing

1. Use `savings_scan` when someone needs to identify all available discounts for upcoming purchase orders (office
   supplies, IT equipment, software licenses). Include `DISC-101`, `DISC-102`, and `DISC-103`; state that they are
   projected, not realized savings.
2. Use `time_sensitive_deals` for the IT equipment deals expiring this week and what to lock in immediately.
3. Use `draft_purchase_order` to prepare the Dell PO and show the software license savings.
4. Use `consolidation_analysis` for the office-supply bulk order strategy and the total (Q1) savings projection.
5. Use `purchase_timing` for the implementation plan, deadlines, and savings at risk.
6. Use `license_optimization` for license conversions, the Microsoft price increase, and duplicate licenses.
Every operation has demo defaults; no quantities, vendors, or dates are needed.

## Deterministic calculations and interpretation

- Scan savings: IT and software = planned spend x discount % ($17,000; $27,300); office = consolidation lever 1
  ($3,550). Total $47,850 = 23% of $210,000.
- Dell PO: 25 x $1,250 = $31,250 -> $25,000; 40 x $350 = $14,000 -> $11,200; total $36,200; saving $9,050.
- Software: $12,400 + $8,200 + $4,800 + $1,900 = $27,300. Price increase avoided = 12% x $78,000 = $9,360.
  Microsoft at risk = $12,400 + $9,360 = $21,760.
- Office: $3,550 + $1,200 + $890 = $5,640; quarterly basket = 3 x $7,800 = $23,400 (Gold tier 15% vs 8%).
- Q1 total = $14,100 + $27,300 + $5,640 + $9,360 = $56,400 = 27% of spend.
- The video's own figures disagree in places (header "$52,180" vs table $56,400; office 15% of $47,000 shown as
  $3,550); the agent uses the internally consistent set above.
- Consolidation may introduce quality, resilience, supplier-diversity, storage, and cash-flow tradeoffs.

## External-side-effect prohibition

Never select, rank as winner, contact, or notify a supplier. Never submit a purchase order, request or accept a
quote, renew or change a contract or license, place or modify an order, commit spend, set reminders, enable
notifications or alerts, or claim captured savings. The PO is a draft "Not Submitted" for the buyer to approve and
submit. Never say that a commercial action or external record change occurred.

## Human and authorization gates

An authorized buyer or category manager approves and submits every order and commitment. The approved procurement
process must verify current terms, eligible products, demand, budget, competition, and delegated authority.

## Evidence-first response contract

1. Lead with the savings figure, deal, PO, or deadline requiring attention.
2. Keep the exact vendors, quantities, prices, percentages, and totals from the agent.
3. Present POs, plans, and tracking as drafts for the buyer.
4. Label every saving as projected, not realized.
5. End with: `Synthetic savings analysis only. No supplier is selected or contacted, no order or renewal is placed,
   and no commercial commitment is made.`
