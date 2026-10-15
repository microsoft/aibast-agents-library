# Discount Finder — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. The vendors, offers, terms, quantities, prices, deadlines, licenses, and spend values
> below are invented. They are sourcing-review evidence only and are not live pricing or realized savings.
> Deadlines are relative weekdays of the demo week (Thursday, Friday, Sunday, next month), never calendar dates.

## Planned purchases and available discounts (savings scan)

| ID | Category | Planned spend | Available discount | Projected savings | Basis |
|---|---|---|---|---|---|
| DISC-101 | IT Equipment | $85,000 | 20% quarter-end | $17,000 | 20% of planned spend; quarter-end vendor promotions (Dell, HP, Lenovo) |
| DISC-102 | Software Licenses | $78,000 | 35% annual commit | $27,300 | 35% of planned spend; annual commitment instead of monthly / per-seat billing |
| DISC-103 | Office Supplies | $47,000 | 15% bulk tier | $3,550 | Consolidation lever 1 (6 separate orders -> 2 consolidated orders, Office Depot bulk tier) |

- Total planned spend: $210,000. Total savings potential: $47,850 (23% of spend). These are projected, not realized savings.
- Time-sensitive alerts: Dell quarter-end pricing expires Friday; Microsoft license increase effective next month;
  Office Depot bulk tier requires $5K minimum.

## Expiring IT promotions

| Vendor | Products | Discount | Expires | Savings if locked in |
|---|---|---|---|---|
| Dell | Laptops, monitors | 20% off | Friday | $9,050 (the draft PO below) |
| HP | Printers, accessories | 18% off | Friday | $2,400 |
| Lenovo | Desktops | 15% off | Sunday | $2,650 |

Locked IT savings for Q1 = $9,050 + $2,400 + $2,650 = $14,100. Recommended action: lock in the Dell and HP deals today.

## Dell deal analysis and draft purchase order PO-2024-Q1-0234

| Line | Qty | Unit list price | List total | Net at 20% off |
|---|---|---|---|---|
| Dell Latitude 7440 laptops | 25 | $1,250 | $31,250 | $25,000 |
| monitors (27" 4K) | 40 | $350 | $14,000 | $11,200 |
| Docking stations | 50+ units | included free | - | $0 |
| Total | | | $45,250 | $36,200 |

- Saving: $9,050 ($6,250 + $2,800). Quarter-end discount 20%. Free shipping (order >$25K). Docks free on 50+ unit orders.
- PO must be submitted by Thursday 5 PM to guarantee pricing. The PO is a draft — Not Submitted — ready for the
  buyer to approve and submit; nothing is sent to Dell.

## Software license optimization

| Product | Current | Recommended | Annual savings |
|---|---|---|---|
| Microsoft 365 | Monthly | Annual | $12,400 |
| Adobe Creative | Per-seat | Enterprise | $8,200 |
| Salesforce | Standard | Annual | $4,800 |
| Zoom | Monthly | Annual | $1,900 |
| Total | | | $27,300 |

- Microsoft is increasing prices 12% next month: 12% of the $78,000 planned license spend = $9,360 avoided by locking
  in annual now (on top of the $12,400).
- Duplicate licenses flagged for review: Zoom and Microsoft Teams meetings both licensed for the same 40 users (40
  seats); standalone Adobe Acrobat seats for users already on Adobe Creative (12 seats).

## Office supply bulk strategy

| Current approach | Optimized approach | Savings |
|---|---|---|
| 6 separate orders | 2 consolidated orders | $3,550 |
| Random timing | Aligned with promotions | +$1,200 |
| Multiple vendors | Primary vendor (Office Depot) | +$890 |

- Office supply savings = $3,550 + $1,200 + $890 = $5,640.
- Bulk tier qualification: current monthly $7,800 average; consolidated quarterly $23,400 (3 x $7,800); tier unlocked
  Gold (15% discount vs 8% standard).

## Q1 total savings summary

| Category | Savings | Method |
|---|---|---|
| IT Equipment | $14,100 | Quarter-end deals (Dell, HP, Lenovo) |
| Software | $27,300 | Annual commitments |
| Office Supplies | $5,640 | Bulk consolidation |
| Price Increase Avoidance | $9,360 | Early lock-in |
| TOTAL | $56,400 | 27% of spend |

## Action timeline (draft implementation plan)

- This week (critical): Today approve Dell PO-2024-Q1-0234 ($9,050 savings at risk); Thursday submit the Microsoft
  annual commitment ($21,760 at risk = $12,400 + $9,360); Friday lock the HP printer deal ($2,400 savings).
- Next week: Monday consolidate office supply orders; Tuesday review the Adobe Enterprise proposal; Wednesday finalize
  Salesforce annual terms.
- End of month: submit the consolidated Q1 supply order; complete all license conversions.
- Recommended tracking (ready for the buyer to turn on, not enabled by the agent): calendar reminders for all
  deadlines, approval workflow notifications, price monitoring alerts.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| DISC-01 | Procurement Manager | savings_scan | I need to identify all available discounts for our upcoming purchase orders: office supplies, IT equipment, and software licenses. | DISC-101; DISC-102; not realized savings |
| DISC-02 | Category Buyer | time_sensitive_deals | Which IT equipment deals expire this week, and what should we lock in immediately? | Dell; Thursday 5 PM; approved procurement process |
| DISC-03 | Finance Director | consolidation_analysis | Model the office-supply bulk order strategy and the total savings projection for the quarter. | Office Supply Bulk Strategy; $56,400; does not recommend a supplier award |
| DISC-04 | Category Buyer | purchase_timing | Create the implementation plan with the deadlines and the savings at risk, without placing anything. | PO-2024-Q1-0234; $21,760; No supplier is selected |
| DISC-05 | Procurement Manager | draft_purchase_order | Prepare the Dell laptop and monitor PO for my approval and show the software license savings. | PO-2024-Q1-0234; $36,200; Not Submitted |
| DISC-06 | IT Asset Manager | license_optimization | Which software licenses should move to annual or enterprise terms, and do we pay for any duplicate licenses? | $27,300; $9,360; Duplicate licenses |

## Required response headings and phrases

- Savings: `Savings Opportunity Scan`, IDs `DISC-101` and `DISC-102`, `$47,850`, and `not realized savings`.
- IT deals: `Expiring IT Promotions`, `Dell Deal Analysis`, `Thursday 5 PM`, and `approved procurement process`.
- Draft PO: `PO-2024-Q1-0234`, `$36,200`, `Not Submitted`, and `Software License Optimization`.
- Bulk strategy: `Office Supply Bulk Strategy`, `Q1 Total Savings Summary`, `$56,400`, and `does not recommend a supplier award`.
- Timeline: `Purchase Timing Review`, `PO-2024-Q1-0234`, `$21,760`, and `No supplier is selected`.
- Licenses: `Software License Optimization`, `$27,300`, `$9,360`, and `Duplicate licenses`.
