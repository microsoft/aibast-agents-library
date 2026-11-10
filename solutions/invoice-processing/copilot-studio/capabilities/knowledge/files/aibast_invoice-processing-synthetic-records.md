# Invoice Processing: Synthetic Records (Accounts Payable)

> FIXED FICTIONAL SNAPSHOT, added by the AIBAST Agents Library. Northwind Traders, Contoso Services, Fabrikam Supplies, Tailspin Toys and every invoice number, date, amount and ledger row below are invented. Never match them to a real organization, person, or live record. Label any answer drawn from this file as synthetic.

## What this snapshot is

A small accounts payable team receives invoices as email attachments. The invoice fields have already been read from each attachment. The ledger rules below decide what is logged.

## Existing ledger rows

| Ledger row | Invoice | Vendor | Amount due |
|---|---|---|---|
| INV-ROW-0001 | FAB-1043 | Fabrikam Supplies | 1,250.00 USD |
| INV-ROW-0002 | TT-88-207 | Tailspin Toys | 389.50 USD |

## This week's attachments (fields as read)

| Attachment | Invoice | Vendor | Invoice date | Amount due | Currency |
|---|---|---|---|---|---|
| complete.pdf | NW-2026-118 | Northwind Traders | 11/03/2026 | $4,820.00 | USD |
| partial.pdf | CS-5521 | Contoso Services | (not read) | 975 | (not read) |
| duplicate.pdf | FAB-1043 | Fabrikam Supplies | 2026-10-28 | 1,250.00 | USD |
| cover-letter.pdf | (none) | (none) | (none) | (none) | (none) |

## Ledger rules

1. **Extraction status.** An attachment is **Complete** when all five fields were read (invoice number, vendor, invoice date, amount due, currency), **Partial** when some were read, and **Failed** when none were.
2. **Dates** are written as year-month-day. 11/03/2026 is read as month/day/year, so it becomes 2026-11-03.
3. **Duplicates.** An invoice whose number already has a ledger row is marked as a duplicate of that row. It is still logged, with the duplicate marked, so a person can review it.
4. **Log or skip.** Complete and Partial attachments are logged. Failed attachments, such as a cover letter, are skipped.

## Expected decisions for this snapshot

| Attachment | Invoice | Status | Duplicate of | Logged? |
|---|---|---|---|---|
| complete.pdf | NW-2026-118 | Complete | none | yes |
| cover-letter.pdf | none | Failed | none | no, skipped |
| duplicate.pdf | FAB-1043 | Complete | INV-ROW-0001 | yes, marked as a duplicate |
| partial.pdf | CS-5521 | Partial | none | yes |

Three of the four attachments are logged. Nothing is written to any real ledger; a person reviews every row first.
