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

## Vendor catalog

| ID | Vendor | Category | Contract status | Tier | Rating | Annual spend | Payment terms | Contact role |
|---|---|---|---|---|---|---|---|---|
| VND-001 | AWS | Cloud Infrastructure | Active | Strategic | 4.7 | $890,000 | Net 30 | Enterprise Account Manager |
| VND-002 | Salesforce | CRM Software | Active | Strategic | 4.5 | $430,000 | Annual Prepay | Customer Success Manager |
| VND-003 | Steelcase | Office Furniture | Active | Preferred | 4.3 | $125,000 | Net 45 | Account Representative |
| VND-004 | Herman Miller | Office Furniture | Active | Approved | 4.6 | $85,000 | Net 30 | Regional Sales |
| VND-005 | Azure | Cloud Infrastructure | Active | Strategic | 4.6 | $650,000 | Net 30 | Technical Account Manager |
| VND-006 | FranklinCovey | Training Services | Active | Approved | 4.2 | $45,000 | Net 30 | Program Director |

## Approval thresholds

| Amount up to and including | Required approver | Approval SLA |
|---|---|---|
| $5,000 | Direct Manager | 4 hours |
| $25,000 | Department Head | 8 hours |
| $100,000 | VP Finance | 24 hours |
| $500,000 | CFO | 48 hours |
| Unlimited | CEO + Board | 120 hours |

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

## Locked-case evidence contract

| Case | Persona | Operation | Locked prompt | Required evidence |
|---|---|---|---|---|
| PROC-01 | Procurement Manager | purchase_request | Walk me through the cloud-upgrade request and tell me whose review it needs before anything moves. | PR-5001; $125,000; CFO |
| PROC-02 | Category Buyer | vendor_comparison | Give me a neutral comparison of the approved cloud vendors; do not pick a winner. | AWS; Azure; not a supplier award |
| PROC-03 | Department Approver | approval_routing | This infrastructure request landed in my queue. What is the recommended approval path? | CFO; 48 hours; does not record an approval |
| PROC-04 | Finance Director | spend_analysis | Where is the purchasing budget under pressure, and what should we review before approving more spend? | Software; $60,000; No purchase order is created |

## Required response headings and phrases

- Request: `Purchase Request Review: PR-5001`, `Justification`, and `Approval gate`.
- Vendor review: `Vendor Comparison`, `Vendor Tiers`, and `not a supplier award`.
- Approval: `Approval Routing: PR-5001`, `Approval Thresholds`, `48 hours`,
  and `does not record an approval`.
- Spend: `Spend Analysis`, `By Category`, `Alerts`, `Software category over
  budget by $60,000`, and `No purchase order is created`.
