# Warranty and Registration — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Fabrikam Tool Supply (Riverside branch, dealer account DLR-4100), Northwind Equipment, Priya Raman, Contoso Fleet Services and Adatum Auto Body are fictional. Every serial, date, coverage term, claim and price is invented. Never match them to a real organization,
> person, product or market, and never treat them as live data.

## Complete synthetic records

## Snapshot

| Field | Value |
|---|---|
| Snapshot date | 2026-03-02 (fixed; the current date is not a source) |
| Dealer | Fabrikam Tool Supply (Riverside branch) |
| Dealer account | DLR-4100 |
| Manufacturer | Northwind Equipment |
| Service manager | Priya Raman |
| Warranty decisions | Northwind warranty desk |
| Registration window | 30 days from sale |
| Extension window | coverage ending within 90 days |
| Extension discount | 15% off list |

## Coverage types

| Type | Label | Parts | Labor | On-site |
|---|---|---|---|---|
| full | Full parts and labor | Yes | Yes | Yes |
| parts_only | Parts only | Yes | No | No |
| limited | Limited (wear items excluded) | Yes | No | No |

## Registered units (6)

| Serial | Product | Family | Purchased | Registered | Warranty ends | Days remaining on 2026-03-02 | Coverage | Status | Extension list price |
|---|---|---|---|---|---|---|---|---|---|
| HP-40-1182 | Hydraulic Press HP-40 | Shop presses | 2024-04-10 | 2024-04-12 | 2027-04-10 | 404 | full | Active | $420.00 |
| WS-25-4471 | Welding Station WS-250 | Welding | 2025-01-22 | 2025-01-24 | 2027-01-22 | 326 | full | Active | $260.00 |
| BG-08-2290 | Bench Grinder BG-8 | Grinding | 2024-03-28 | 2024-04-02 | 2026-03-28 | 26 | parts_only | Expiring soon | $85.00 |
| PW-30-0615 | Parts Washer PW-30 | Cleaning | 2024-05-05 | 2024-05-07 | 2026-05-05 | 64 | full | Expiring soon | $140.00 |
| TC-90-3307 | Tire Changer TC-900 | Tire service | 2023-02-14 | 2023-02-15 | 2026-02-14 | ended 16 days ago | full | Expired | not offered |
| CR-12-0950 | Coolant Recovery Unit CR-12 | Fluid service | 2025-06-30 | 2025-07-01 | 2027-06-30 | 485 | limited | Active | $110.00 |

Totals: 6 registered units; 3 Active; 2 Expiring within 90 days; 1 Expired; 2 sold, awaiting registration.

## Claim history

| Serial | Claim | Date | Issue | Status |
|---|---|---|---|---|
| WS-25-4471 | CLM-25-0318 | 2025-08-14 | Torch cable replaced | Resolved |
| TC-90-3307 | CLM-24-0127 | 2024-06-03 | Bead breaker cylinder resealed | Resolved |
| TC-90-3307 | CLM-25-0044 | 2025-02-11 | Turntable motor replaced | Resolved |

## Sold units awaiting registration (2)

| Serial | Product | Sold | End customer | Registration due | Days left | Term | Warranty would end | Coverage |
|---|---|---|---|---|---|---|---|---|
| WS-25-4520 | Welding Station WS-250 | 2026-02-20 | Contoso Fleet Services (shop account C-2207) | 2026-03-22 | 20 | 24 months | 2028-02-20 | full |
| HP-40-1207 | Hydraulic Press HP-40 | 2026-02-26 | Adatum Auto Body (shop account C-2241) | 2026-03-28 | 26 | 36 months | 2029-02-26 | full |

## Derived results

- Claim pre-check WS-25-4471: Eligible for claim review; parts and labor covered; 1 prior claim; 326 days remaining.
- Claim pre-check BG-08-2290: Eligible for parts only; labor billable.
- Claim pre-check TC-90-3307: Not eligible - warranty ended (2026-02-14, 16 days ago); paid repair quote; exceptions go to the Northwind warranty desk.
- Serial check WS-25-4520: format Valid, in catalog, not registered, Ready to register, due 2026-03-22.
- Serial check of a registered serial: Duplicate - do not register again.
- Registration draft WS-25-4520: Draft ID REG-DRAFT-WS-25-4520, Not Submitted, warranty would end 2028-02-20.
- Extension offers: BG-08-2290 $85.00 -> $72.25; PW-30-0615 $140.00 -> $119.00; offer total $191.25 across 2 units; TC-90-3307 not offered (coverage ended).

## Locked-case evidence contract

Each locked case below calls exactly one operation. The agent output must contain every listed evidence string.

| Case | Persona | Operation | Prompt | Must include |
|---|---|---|---|---|
| WAR-01 | Dealer Service Manager | coverage_overview | How does our dealership's warranty coverage look right now? | Registered units; Expiring within 90 days; Sold, awaiting registration |
| WAR-02 | Dealer Service Manager | claim_precheck | A customer brought in welding station WS-25-4471 with a failed wire feeder. Is the repair covered? | Eligible for claim review; Labor covered; No claim was filed |
| WAR-03 | Warranty Administrator | unit_record | Pull the full warranty record for tire changer TC-90-3307. | Expired (ended 16 days ago); CLM-25-0044; Claim history |
| WAR-04 | Dealer Sales Staff | validate_serial | We just sold welding station WS-25-4520. Check the serial before we register it. | Ready to register; Already registered; 2026-03-22 |
| WAR-05 | Dealer Sales Staff | registration_draft | Prepare the registration for WS-25-4520, but don't submit anything. | Not Submitted; 2028-02-20; Nothing was submitted |
| WAR-06 | Dealer Sales Staff | extension_offers | Which units should we offer extended coverage to this month? | $191.25; BG-08-2290; No offer was sent |

## Reference outputs (exact agent output for each locked case)

### WAR-01 — Coverage overview (`{"operation": "coverage_overview"}`)

````markdown
**Warranty Coverage Overview: Fabrikam Tool Supply (Riverside branch)**

Dealer account DLR-4100 | Manufacturer Northwind Equipment | As of 2026-03-02

| Measure | Count |
|---|---|
| Registered units | 6 |
| Active | 3 |
| Expiring within 90 days | 2 |
| Expired | 1 |
| Sold, awaiting registration | 2 |

| Serial | Product | Coverage | Ends | Remaining | Status |
|---|---|---|---|---|---|
| HP-40-1182 | Hydraulic Press HP-40 | Full parts and labor | 2027-04-10 | 404 days | Active |
| WS-25-4471 | Welding Station WS-250 | Full parts and labor | 2027-01-22 | 326 days | Active |
| BG-08-2290 | Bench Grinder BG-8 | Parts only | 2026-03-28 | 26 days | Expiring soon |
| PW-30-0615 | Parts Washer PW-30 | Full parts and labor | 2026-05-05 | 64 days | Expiring soon |
| TC-90-3307 | Tire Changer TC-900 | Full parts and labor | 2026-02-14 | ended 16 days ago | Expired |
| CR-12-0950 | Coolant Recovery Unit CR-12 | Limited (wear items excluded) | 2027-06-30 | 485 days | Active |

**Awaiting registration (30-day window):**

| Serial | Product | Sale | Registration |
|---|---|---|---|
| WS-25-4520 | Welding Station WS-250 | sold 2026-02-20 | due 2026-03-22 (20 days) |
| HP-40-1207 | Hydraulic Press HP-40 | sold 2026-02-26 | due 2026-03-28 (26 days) |

**Next step:** register the 2 sold units before their windows close and review extended-coverage offers for the 2 expiring units.

Synthetic dealer snapshot only. This agent does not file a claim, submit a registration, sell an extension, contact a customer or change a warranty record; it prepares drafts and pre-checks for an authorized person to act on.

Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]
Agents: WarrantyRegistrationAgent
````

### WAR-02 — Claim pre-check (`{"operation": "claim_precheck", "serial_number": "WS-25-4471"}`)

````markdown
**Claim Pre-Check: WS-25-4471 (Welding Station WS-250)**

| Check | Result |
|---|---|
| Registration | Confirmed 2025-01-24 |
| Warranty active | Yes (ends 2027-01-22) |
| Days remaining | 326 |
| Coverage | Full parts and labor |
| Parts covered | Yes |
| Labor covered | Yes |
| Prior claims | 1 |

**Pre-check result: Eligible for claim review**

**Next step:** Parts and labor are covered. Prepare the claim with the failure description, photos and hours for the Northwind warranty desk to approve.

No claim was filed. The Northwind warranty desk makes the coverage decision.

Synthetic dealer snapshot only. This agent does not file a claim, submit a registration, sell an extension, contact a customer or change a warranty record; it prepares drafts and pre-checks for an authorized person to act on.

Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]
Agents: WarrantyRegistrationAgent
````

### WAR-03 — Unit warranty record (`{"operation": "unit_record", "serial_number": "TC-90-3307"}`)

````markdown
**Warranty Record: TC-90-3307 (Tire Changer TC-900)**

| Field | Value |
|---|---|
| Product family | Tire service |
| Purchased | 2023-02-14 |
| Registered | 2023-02-15 |
| Warranty ends | 2026-02-14 |
| Status | Expired (ended 16 days ago) |
| Coverage | Full parts and labor |
| Parts / Labor / On-site | Yes / Yes / Yes |

**Claim history (2):**

| Claim | Date | Issue | Status |
|---|---|---|---|
| CLM-24-0127 | 2024-06-03 | Bead breaker cylinder resealed | Resolved |
| CLM-25-0044 | 2025-02-11 | Turntable motor replaced | Resolved |

**Next step:** Warranty ended 16 days ago. Repairs are customer-paid; quote the repair and, if the customer asks, route an exception request to the Northwind warranty desk.

Synthetic dealer snapshot only. This agent does not file a claim, submit a registration, sell an extension, contact a customer or change a warranty record; it prepares drafts and pre-checks for an authorized person to act on.

Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]
Agents: WarrantyRegistrationAgent
````

### WAR-04 — Serial check (`{"operation": "validate_serial", "serial_number": "WS-25-4520"}`)

````markdown
**Serial Check: WS-25-4520**

| Check | Result |
|---|---|
| Format | Valid |
| In catalog | Yes - Welding Station WS-250 |
| Already registered | No |
| Sold | 2026-02-20 to Contoso Fleet Services (shop account C-2207) |
| Registration window | Due 2026-03-22 (20 days left) |

**Result: Ready to register.** Ask me to prepare the registration draft.

Synthetic dealer snapshot only. This agent does not file a claim, submit a registration, sell an extension, contact a customer or change a warranty record; it prepares drafts and pre-checks for an authorized person to act on.

Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]
Agents: WarrantyRegistrationAgent
````

### WAR-05 — Registration draft (`{"operation": "registration_draft", "serial_number": "WS-25-4520"}`)

````markdown
**Product Registration Draft - Not Submitted**

| Field | Value |
|---|---|
| Draft ID | REG-DRAFT-WS-25-4520 |
| Serial | WS-25-4520 |
| Product | Welding Station WS-250 |
| Dealer | Fabrikam Tool Supply (Riverside branch) (DLR-4100) |
| End customer | Contoso Fleet Services (shop account C-2207) |
| Sale date (warranty start) | 2026-02-20 |
| Warranty term | 24 months |
| Warranty would end | 2028-02-20 |
| Coverage | Full parts and labor |
| Registration due | 2026-03-22 (20 days left) |
| Status | Draft for dealer review |

**Before submitting:** confirm the sale date on the invoice and the end customer's contact with Priya Raman, then submit it in the manufacturer's registration portal. Nothing was submitted and no warranty was activated.

Synthetic dealer snapshot only. This agent does not file a claim, submit a registration, sell an extension, contact a customer or change a warranty record; it prepares drafts and pre-checks for an authorized person to act on.

Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]
Agents: WarrantyRegistrationAgent
````

### WAR-06 — Extended-coverage offers (`{"operation": "extension_offers"}`)

````markdown
**Extended-Coverage Offers: 2 units ending within 90 days**

| Serial | Product | Coverage ends | Remaining | List price | Offer (15% off list) |
|---|---|---|---|---|---|
| BG-08-2290 | Bench Grinder BG-8 | 2026-03-28 | 26 days | $85.00 | $72.25 |
| PW-30-0615 | Parts Washer PW-30 | 2026-05-05 | 64 days | $140.00 | $119.00 |

**Offer total:** $191.25 across 2 units.
**Not offered:** TC-90-3307 - coverage already ended; extensions must start before the warranty ends.

**Next step:** review the offer drafts and send them to the customers yourself. No offer was sent and nothing was sold.

Synthetic dealer snapshot only. This agent does not file a claim, submit a registration, sell an extension, contact a customer or change a warranty record; it prepares drafts and pre-checks for an authorized person to act on.

Source: [Synthetic Warranty + Registration Snapshot, as of 2026-03-02]
Agents: WarrantyRegistrationAgent
````
