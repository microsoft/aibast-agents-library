# Time Entry and Billing — Complete Synthetic Ledger

> SYNTHETIC PILOT DATA. All people, clients, projects, entries, dates, rates,
> budgets, invoices, and statuses are fictional. Fixed close snapshot: March
> 2026.

## Complete time-entry records

| Entry | Consultant | Project | Date | Hours | Rate | Category | Exact description | Approved |
|---|---|---|---|---:|---:|---|---|---|
| TE-9001 | Elena Vasquez | TechCorp Transformation | 2026-03-10 | 8.0 | $275 | billable | Cloud architecture design workshop | yes |
| TE-9002 | Elena Vasquez | TechCorp Transformation | 2026-03-11 | 9.5 | $275 | billable | Azure landing zone implementation | yes |
| TE-9003 | Michael Chen | Apex Analytics Platform | 2026-03-10 | 7.5 | $260 | billable | Data pipeline development | yes |
| TE-9004 | Michael Chen | Apex Analytics Platform | 2026-03-11 | 8.0 | $260 | billable | empty / Missing description | no |
| TE-9005 | Priya Sharma | Pinnacle Energy ERP | 2026-03-10 | 10.0 | $310 | billable | Program status review and steering committee | yes |
| TE-9006 | Priya Sharma | Pinnacle Energy ERP | 2026-03-11 | 8.0 | $310 | billable | Sprint planning and backlog grooming | yes |
| TE-9007 | Lisa Tanaka | Atlas Security Audit | 2026-03-10 | 6.0 | $290 | billable | Identity and access management review | yes |
| TE-9008 | Lisa Tanaka | Atlas Security Audit | 2026-03-11 | 8.5 | $290 | billable | Penetration test coordination | yes |
| TE-9009 | Amanda Foster | Metro Transit Portal | 2026-03-10 | 8.0 | $165 | billable | User research session facilitation | yes |
| TE-9010 | Amanda Foster | Metro Transit Portal | 2026-03-11 | 4.0 | $165 | non_billable | Internal design review | yes |
| TE-9011 | Elena Vasquez | TechCorp Transformation | 2026-03-12 | 11.0 | $412 | billable | Weekend migration cutover | no |
| TE-9012 | David Okafor | Internal Training | 2026-03-10 | 8.0 | $0 | non_billable | Power BI certification prep | yes |

## Configured billing rates

| Consultant | Standard | Overtime | Maximum daily hours |
|---|---:|---:|---:|
| Elena Vasquez | $275 | $412 | 10 |
| Michael Chen | $260 | $390 | 10 |
| Priya Sharma | $310 | $465 | 10 |
| Lisa Tanaka | $290 | $435 | 10 |
| Amanda Foster | $165 | $248 | 10 |

## Complete project budget records

| Project | Client | Contract type | Total budget | Billed to date | Remaining | Budget used |
|---|---|---|---:|---:|---:|---:|
| TechCorp Transformation | TechCorp Industries | T&M | $850,000 | $682,400 | $167,600 | 80.3% |
| Apex Analytics Platform | Apex Manufacturing | T&M | $520,000 | $398,000 | $122,000 | 76.5% |
| Pinnacle Energy ERP | Pinnacle Energy | Fixed Fee | $1,200,000 | $744,000 | $456,000 | 62.0% |
| Atlas Security Audit | Atlas Financial Group | T&M | $185,000 | $156,600 | $28,400 | 84.6% |
| Metro Transit Portal | Metro Transit Authority | T&M | $340,000 | $218,000 | $122,000 | 64.1% |

Pinnacle Energy ERP is Fixed Fee. Its time supports delivery evidence but does
not determine invoice value; contractual milestone evidence is required.

## Complete invoice history

| Invoice | Client | Amount | Date | Status | Days outstanding |
|---|---|---:|---|---|---:|
| INV-2026-201 | TechCorp Industries | $142,500.00 | 2026-02-28 | paid | 0 |
| INV-2026-202 | Apex Manufacturing | $98,800.00 | 2026-02-28 | paid | 0 |
| INV-2026-203 | Pinnacle Energy | $186,000.00 | 2026-02-28 | outstanding | 17 |
| INV-2026-204 | Atlas Financial Group | $52,200.00 | 2026-02-28 | outstanding | 17 |
| INV-2026-205 | Metro Transit Authority | $46,200.00 | 2026-02-28 | overdue | 45 |

## Canonical close totals

- Total hours logged: 96.5
- Billable hours: 84.5 (87.6%)
- Non-billable hours: 12.0
- Total billable value: $24,479.50
- Unbilled entries: 2
- Unbilled value: $6,612.00
- Total outstanding invoices: $284,400.00
- Last-cycle total billed: $525,700.00
- Total collected: $241,300.00
- Collection rate: 45.9%
