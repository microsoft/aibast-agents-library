# Procurement Agent — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Every requester, supplier, amount, budget, status,
> term, and approval rule below is invented. Use it exactly and never browse,
> refresh, supplement, or create a transaction.

## Purchase requests

| ID | Title | Requester | Department | Category | Amount | Priority | Status | Preferred vendor | Justification | Budget code |
|---|---|---|---|---|---|---|---|---|---|---|
| PR-5001 | Cloud Infrastructure Upgrade | Sarah Chen | IT | Technology | $125,000 | High | Pending Approval | AWS | Current infrastructure at 92% capacity, scaling needed for Q1 growth | IT-INFRA-2025 |
| PR-5002 | Office Furniture - New Floor Build-Out | Tom Rivera | Facilities | Office Supplies | $48,500 | Medium | Vendor Selection | Steelcase | 5th floor build-out for 30 new employees starting Q2 | FAC-CAPEX-2025 |
| PR-5003 | Annual Software License Renewal - Salesforce | Mike Torres | Sales | Software | $215,000 | High | Approved | Salesforce | Annual enterprise license renewal, 200 seats | SALES-SW-2025 |
| PR-5004 | Employee Training Program - Leadership Development | Lisa Park | HR | Professional Services | $35,000 | Low | Draft | FranklinCovey | Q2 leadership development program for 25 managers | HR-TRAIN-2025 |
| PR-5005 | Engineering Team Laptops (50) | Priya Nair | Engineering | IT Equipment | $81,893 | High | Draft PO - Pending Approval | TechPro Solutions | 50 new engineers start Monday; equipment needed within 5 business days | IT-EQUIP-Q4-2024 |

## Vendor catalog

| ID | Vendor | Category | Contract status | Tier | Rating | Annual spend | Payment terms | Contact role |
|---|---|---|---|---|---|---|---|---|
| VND-001 | AWS | Cloud Infrastructure | Active | Strategic | 4.7 | $890,000 | Net 30 | Enterprise Account Manager |
| VND-002 | Salesforce | CRM Software | Active | Strategic | 4.5 | $430,000 | Annual Prepay | Customer Success Manager |
| VND-003 | Steelcase | Office Furniture | Active | Preferred | 4.3 | $125,000 | Net 45 | Account Representative |
| VND-004 | Herman Miller | Office Furniture | Active | Approved | 4.6 | $85,000 | Net 30 | Regional Sales |
| VND-005 | Azure | Cloud Infrastructure | Active | Strategic | 4.6 | $650,000 | Net 30 | Technical Account Manager |
| VND-006 | FranklinCovey | Training Services | Active | Approved | 4.2 | $45,000 | Net 30 | Program Director |
| VND-007 | TechPro Solutions | IT Equipment | Master agreement valid through next year | Preferred | 4.8 | $166,750 | Net 30 | Account Manager |
| VND-008 | Global IT Supply | IT Equipment | Active | Approved | 4.4 | $63,250 | Net 30 | Inside Sales |
| VND-009 | CompuDirect | IT Equipment | Active | Approved | 4.1 | $57,500 | Net 45 | Regional Sales |

IT-equipment vendor performance: TechPro Solutions delivery 3-5 days, on-time 98% (last quarter), defect rate
0%, volume discount 5% off for 50+ units; Global IT Supply 5-7 days, 93%, 1%, 3% off for 100+ units;
CompuDirect 7-10 days, 89%, 2%, no volume discount. TechPro Solutions offers the best value (a recommendation,
not a supplier award).

## Approval thresholds

| Amount up to and including | Required approver | Approval SLA |
|---|---|---|
| $5,000 | Direct Manager | 4 hours |
| $25,000 | Dept Manager | 8 hours |
| $75,000 | Finance Director | 24 hours |
| $500,000 | CFO | 48 hours |
| Unlimited (above $500,000) | CEO + Board | 120 hours |

## Spend categories

| Category | Budget | Spent YTD | Committed | Available | Utilization | Status | Trend |
|---|---|---|---|---|---|---|---|
| Technology | $2,500,000 | $1,875,000 | $340,000 | $285,000 | 88.6% | At Risk | +12% YoY |
| Software | $800,000 | $645,000 | $215,000 | $-60,000 | 107.5% | Over Budget | +18% YoY |
| Office Supplies | $350,000 | $210,000 | $48,500 | $91,500 | 73.9% | On Track | -5% YoY |
| Professional Services | $500,000 | $325,000 | $35,000 | $140,000 | 72.0% | On Track | +8% YoY |
| Travel | $200,000 | $142,000 | $18,000 | $40,000 | 80.0% | On Track | -15% YoY |

## Portfolio totals

| Metric | Exact value |
|---|---|
| Total budget | $4,350,000 |
| Spent YTD | $3,197,000 (73%) |
| Committed | $656,500 |
| Available | $496,500 |

## Engineering laptop order (PR-5005, the demo scenario)

Asked as "I need to order 50 laptops for the new engineering team. Can you show me our approved vendors for IT
equipment?", then "Yes, create the purchase order for 50 Dell Latitude 7440 laptops with engineering
configuration", "Yes, expedite the approval with urgency notifications", "Yes, show me how this affects our Q4
budget", and "Yes, create an RFQ for office furniture for the same team".

### Purchase order draft PO-2024-ENG-0892 (TechPro Solutions)

| Item | Qty | Unit price | Total |
|---|---|---|---|
| Dell Latitude 7440 (i7, 32GB, 1TB) - engineering configuration | 50 | $1,250 | $62,500 |
| 3-Year Warranty | 50 | $189 | $9,450 |
| Docking Stations | 50 | $150 | $7,500 |

Subtotal $79,450; volume discount (5%) -$3,973; tax (8.5% of $75,477) $6,416; total $81,893 (amounts round half
up). Approval workflow once submitted: Dept Manager auto-approved (within department budget); Finance Director
(Sarah Thompson) pending; CFO (Michael Roberts) required (order >$75,000). Draft only: No purchase order is
created until an authorized buyer submits it.

### Expedite approval (draft notifications)

Approval status: current queue time 4 hours 23 minutes; Finance Director avg response 6 hours; escalation
available after 24 hours. Draft Teams notifications: to Sarah Thompson (Finance Director), priority HIGH,
channel Finance Approvals, "URGENT: Engineering laptop PO needs approval - team starts Monday."; to Michael
Roberts (CFO), pre-notification for the >$75,000 threshold, "New hire equipment - time sensitive."
Alternatives if delayed: 12 similar laptops available in IT inventory; 45-day rental option. Splitting the order
to stay under the CFO threshold is not offered (it would circumvent the approval control). No notification was
sent.

### Q4 2024 IT budget ($450,000) and this order

| Line | Amount | % of budget |
|---|---|---|
| Spent to Date | $287,500 | 63.9% |
| This PO (PR-5005) | $81,893 | 18.2% |
| Remaining | $80,607 | 17.9% |

82% committed after this purchase - medium risk level (75-90%). Spending by category: Laptops/Desktops $198,400
(69%); Software Licenses $42,300 (15%); Networking $28,900 (10%); Accessories $17,900 (6%). Vendor
concentration (share of IT spend): TechPro Solutions 58%; Global IT Supply 22%; CompuDirect 20%. Alert: $12,400
in duplicate software licenses (design suite seats assigned twice, 18 x $400; overlapping project-tool
licenses, 13 x $400).

### RFQ draft RFQ-2024-FRN-0145 (office furniture for the same team)

| Item | Est. budget |
|---|---|
| Standing Desks (60" adjustable) | $35,000-$45,000 |
| Ergonomic Chairs (lumbar support) | $25,000-$30,000 |
| Dual Monitor Arms | $7,500-$10,000 |

Total $67,500-$85,000. Vendors to invite: WorkSpace Plus, Office Innovations, Commercial Interiors. Evaluation
criteria: Price: 40% | Delivery: 25% | Warranty: 20% | Sustainability: 15%. Responses due 48 hours after the
buyer sends it; decision by end of week. No RFQ was distributed.

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| PROC-01 | Procurement Manager | purchase_request | Walk me through the cloud-upgrade request and tell me whose review it needs before anything moves. | PR-5001; $125,000; CFO |
| PROC-02 | Category Buyer | vendor_comparison | Give me a neutral comparison of the approved cloud vendors; do not pick a winner. | AWS; Azure; not a supplier award |
| PROC-03 | Department Approver | approval_routing | This infrastructure request landed in my queue. What is the recommended approval path? | CFO; 48 hours; does not record an approval |
| PROC-04 | Finance Director | spend_analysis | Where is the purchasing budget under pressure, and what should we review before approving more spend? | Software; $60,000; No purchase order is created |
| PROC-05 | Procurement Manager | draft_purchase_order | Create the purchase order for the 50 Dell Latitude 7440 laptops for the new engineering team. | PO-2024-ENG-0892; $81,893; No purchase order is created |
| PROC-06 | Procurement Manager | expedite_approval | The engineering laptop order is stuck in approval. Can you expedite it with urgency notifications? | Sarah Thompson; 4 hours 23 minutes; No notification was sent |
| PROC-07 | Finance Director | budget_impact | How does the engineering laptop order affect our Q4 IT budget? | $80,607; 82% committed; $12,400 |
| PROC-08 | Category Buyer | draft_rfq | We also need an RFQ for office furniture for the same engineering team. | RFQ-2024-FRN-0145; Sustainability: 15%; No RFQ was distributed |

## Required response headings and phrases

- Request: `Purchase Request Review: PR-5001`, `Justification`, and `Approval gate`.
- Vendor review: `Vendor Comparison`, `Vendor Tiers`, and `not a supplier award`.
- Approval: `Approval Routing: PR-5001`, `Approval Thresholds`, `48 hours`,
  and `does not record an approval`.
- Spend: `Spend Analysis`, `By Category`, `Alerts`, `Software category over
  budget by $60,000`, and `No purchase order is created`.
