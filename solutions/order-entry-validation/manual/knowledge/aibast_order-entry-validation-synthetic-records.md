# Order Entry Validation Agent — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Proseware Instruments, its products, the five customers and contacts, the buying group, and every PO, quote, price, term, address and rule are fictional. Never match them to a real organization, person or live system.

## Complete synthetic records

Each section below is the exact output of one operation over the fixed snapshot (demo defaults). Together they contain every record, figure and rule the pilot may cite.

### Pending PO queue (`order_queue`)

**Pending PO Queue: Proseware Instruments Sales Operations (2026-10-05)**

| PO | Customer | Received | Quote | PO Value | Watch For |
|---|---|---|---|---|---|
| PO-4471 | Woodgrove Water Authority | 2026-10-01 | Q-2210 | $28,000 | Sensor head price differs from the quote |
| PO-4472 | Coho Refining | 2026-10-02 | Q-2214 | $56,520 | Hydrogen sulfide heads ordered without the safety kit |
| PO-4473 | Tailwind Mining Co | 2026-10-02 | Q-2219 | $66,550 | Payment terms and a region-restricted sensor |
| PO-4474 | Lucerne Labs | 2026-10-03 | Q-2223 | $18,870 | None expected |
| PO-4475 | Relecloud Utilities | 2026-10-04 | Q-2226 | $51,960 | Buying group pricing on the quote |

**Queue:** 5 purchase orders worth $221,900, each matched to an accepted quote.
**Next step:** start with PO-4471 (oldest): read it and check it against quote Q-2210.

### Purchase order extraction (`extract_po`)

**Purchase Order Extract: PO-4471**

| Field | Value |
|---|---|
| Customer | Woodgrove Water Authority |
| PO Number | PO-4471 |
| Date Received | 2026-10-01 |
| Ship-To | 1200 Reservoir Rd, Dock 3 |
| Ship-To Contact | Hannah Cole |
| Payment Terms | Net 30 |
| Freight Terms | FOB Origin |
| Referenced Quote | Q-2210 |

| Line | Part | Description | Qty | Unit Price | Extended |
|---|---|---|---|---|---|
| 1 | PX-300 | PX-300 portable gas analyzer | 4 | $6,450 | $25,800 |
| 2 | SH-CO | Carbon monoxide sensor head | 4 | $410 | $1,640 |
| 3 | KIT-CAL | Calibration kit | 2 | $280 | $560 |

**PO total:** $28,000 across 3 lines. Every field above was read from the PO; nothing was inferred.
**Next step:** validate it against quote Q-2210.

### Quote validation (`quote_validation`)

**Quote Validation: PO-4471 vs Q-2210**

| Check | PO | Quote | Result |
|---|---|---|---|
| Customer account | Woodgrove Water Authority | Woodgrove Water Authority | Match |
| Ship-to contact | Hannah Cole | Hannah Cole | Match |
| Ship-to address | 1200 Reservoir Rd, Dock 3 | 1200 Reservoir Rd, Dock 3 | Match |
| Payment terms | Net 30 | Net 30 | Match |
| Freight terms | FOB Origin | FOB Origin | Match |
| Price PX-300 | $6,450 | $6,450 | Match |
| Price SH-CO | $410 | $395 | Mismatch (+3.8%) |
| Price KIT-CAL | $280 | $280 | Match |

**Result:** 1 exception: Price SH-CO is $410 on the PO vs $395 on the quote (+3.8%). Price tolerance is 1% per line.
**Next step:** confirm price SH-CO with the account owner before entry.

### Configuration check (`configuration_check`)

**Configuration Check: PO-4472 (Coho Refining)**

| Rule | Result | Detail |
|---|---|---|
| Compatible pairing | Pass | SH-H2S with PX-500 |
| Mandatory kit | Fail | SH-H2S needs KIT-SAFE (0 of 6 ordered) |

**Result:** 1 of 2 configuration rules pass. Never enter this order with the wrong configuration: add KIT-SAFE to the order (it is on quote Q-2214) and confirm with the customer.

### Order classification (`order_classification`)

**Order Classification: PO-4471 (Woodgrove Water Authority)**

| Attribute | Value | Basis |
|---|---|---|
| Region | Domestic | Ship-to address |
| Order Type | STD-DOM | Region rule |
| Order Class | New | Quote opportunity |
| Sales Channel | Public sector | Customer account |

**Next step:** use these values on the draft sales order header.

### Draft sales order (`draft_sales_order`)

**Draft Sales Order: PO-4471 - Not Submitted**

| Header | Value |
|---|---|
| Customer | Woodgrove Water Authority |
| Customer PO | PO-4471 |
| Quote | Q-2210 |
| Order Type | STD-DOM |
| Order Class | New |
| Sales Channel | Public sector |
| Payment Terms | Net 30 (quote) |
| Freight Terms | FOB Origin (quote) |
| Ship-To | 1200 Reservoir Rd, Dock 3 |
| Status | Draft - Not Submitted, on hold for exceptions |

| Line | Part | Qty | Unit Price (quote) | Extended |
|---|---|---|---|---|
| 1 | PX-300 | 4 | $6,450 | $25,800 |
| 2 | SH-CO | 4 | $395 | $1,580 |
| 3 | KIT-CAL | 2 | $280 | $560 |

**Order total at quote prices:** $27,940 (PO states $28,000).
**Exceptions to resolve before entry:**
- Price SH-CO: PO $410 vs quote $395

A sales operations specialist reviews and enters this order; nothing was submitted to the ERP.

### Queue readiness review (`queue_review`)

**Queue Review: 2026-10-05**

| PO | Customer | Status | Exceptions |
|---|---|---|---|
| PO-4471 | Woodgrove Water Authority | Needs fix | Price SH-CO: PO $410 vs quote $395 |
| PO-4472 | Coho Refining | Needs fix | Mandatory kit: SH-H2S needs KIT-SAFE (0 of 6 ordered) |
| PO-4473 | Tailwind Mining Co | Needs fix | Payment terms: PO Net 60 vs quote Net 30; Region release: SH-NH3 is not released for International orders |
| PO-4474 | Lucerne Labs | Ready to enter | - |
| PO-4475 | Relecloud Utilities | Needs fix | Buying group: assign Trey Purchasing Network from the quote |

**Result:** 1 of 5 purchase orders are ready to enter; 4 need a fix first. Each exception names the field or rule behind it.
**Next step:** enter the ready orders and send the exceptions to their account owners as drafts.

### `extract_po` with po = PO-4472

**Purchase Order Extract: PO-4472**

| Field | Value |
|---|---|
| Customer | Coho Refining |
| PO Number | PO-4472 |
| Date Received | 2026-10-02 |
| Ship-To | 88 Harbor Industrial Pkwy |
| Ship-To Contact | Luis Moreno |
| Payment Terms | Net 45 |
| Freight Terms | FOB Destination |
| Referenced Quote | Q-2214 |

| Line | Part | Description | Qty | Unit Price | Extended |
|---|---|---|---|---|---|
| 1 | PX-500 | PX-500 multi-gas analyzer | 6 | $8,900 | $53,400 |
| 2 | SH-H2S | Hydrogen sulfide sensor head | 6 | $520 | $3,120 |

**PO total:** $56,520 across 2 lines. Every field above was read from the PO; nothing was inferred.
**Next step:** validate it against quote Q-2214.

### `quote_validation` with po = PO-4472

**Quote Validation: PO-4472 vs Q-2214**

| Check | PO | Quote | Result |
|---|---|---|---|
| Customer account | Coho Refining | Coho Refining | Match |
| Ship-to contact | Luis Moreno | Luis Moreno | Match |
| Ship-to address | 88 Harbor Industrial Pkwy | 88 Harbor Industrial Pkwy | Match |
| Payment terms | Net 45 | Net 45 | Match |
| Freight terms | FOB Destination | FOB Destination | Match |
| Price PX-500 | $8,900 | $8,900 | Match |
| Price SH-H2S | $520 | $520 | Match |

**Result:** All fields match the quote. Price tolerance is 1% per line.
**Next step:** check the product configuration.

### `configuration_check` with po = PO-4472

**Configuration Check: PO-4472 (Coho Refining)**

| Rule | Result | Detail |
|---|---|---|
| Compatible pairing | Pass | SH-H2S with PX-500 |
| Mandatory kit | Fail | SH-H2S needs KIT-SAFE (0 of 6 ordered) |

**Result:** 1 of 2 configuration rules pass. Never enter this order with the wrong configuration: add KIT-SAFE to the order (it is on quote Q-2214) and confirm with the customer.

### `draft_sales_order` with po = PO-4472

**Draft Sales Order: PO-4472 - Not Submitted**

| Header | Value |
|---|---|
| Customer | Coho Refining |
| Customer PO | PO-4472 |
| Quote | Q-2214 |
| Order Type | STD-DOM |
| Order Class | New |
| Sales Channel | Direct industrial |
| Payment Terms | Net 45 (quote) |
| Freight Terms | FOB Destination (quote) |
| Ship-To | 88 Harbor Industrial Pkwy |
| Status | Draft - Not Submitted, on hold for exceptions |

| Line | Part | Qty | Unit Price (quote) | Extended |
|---|---|---|---|---|
| 1 | PX-500 | 6 | $8,900 | $53,400 |
| 2 | SH-H2S | 6 | $520 | $3,120 |

**Order total at quote prices:** $56,520 (PO states $56,520).
**Exceptions to resolve before entry:**
- Mandatory kit: SH-H2S needs KIT-SAFE (0 of 6 ordered)

A sales operations specialist reviews and enters this order; nothing was submitted to the ERP.

### `extract_po` with po = PO-4473

**Purchase Order Extract: PO-4473**

| Field | Value |
|---|---|
| Customer | Tailwind Mining Co |
| PO Number | PO-4473 |
| Date Received | 2026-10-02 |
| Ship-To | Gate 7, Ridgeway Mine Site |
| Ship-To Contact | Ana Silva |
| Payment Terms | Net 60 |
| Freight Terms | FOB Origin |
| Referenced Quote | Q-2219 |

| Line | Part | Description | Qty | Unit Price | Extended |
|---|---|---|---|---|---|
| 1 | PX-300 | PX-300 portable gas analyzer | 10 | $6,200 | $62,000 |
| 2 | SH-NH3 | Ammonia sensor head | 10 | $455 | $4,550 |

**PO total:** $66,550 across 2 lines. Every field above was read from the PO; nothing was inferred.
**Next step:** validate it against quote Q-2219.

### `quote_validation` with po = PO-4473

**Quote Validation: PO-4473 vs Q-2219**

| Check | PO | Quote | Result |
|---|---|---|---|
| Customer account | Tailwind Mining Co | Tailwind Mining Co | Match |
| Ship-to contact | Ana Silva | Ana Silva | Match |
| Ship-to address | Gate 7, Ridgeway Mine Site | Gate 7, Ridgeway Mine Site | Match |
| Payment terms | Net 60 | Net 30 | Mismatch |
| Freight terms | FOB Origin | FOB Origin | Match |
| Price PX-300 | $6,200 | $6,200 | Match |
| Price SH-NH3 | $455 | $455 | Match |

**Result:** 1 exception: Payment terms is Net 60 on the PO vs Net 30 on the quote. Price tolerance is 1% per line.
**Next step:** confirm payment terms with the account owner before entry.

### `configuration_check` with po = PO-4473

**Configuration Check: PO-4473 (Tailwind Mining Co)**

| Rule | Result | Detail |
|---|---|---|
| Compatible pairing | Pass | SH-NH3 with PX-300 |
| Region release | Fail | SH-NH3 is not released for International orders |

**Result:** 1 of 2 configuration rules pass. Never enter this order with the wrong configuration: ask the account owner for a released alternative before entry.

### `draft_sales_order` with po = PO-4473

**Draft Sales Order: PO-4473 - Not Submitted**

| Header | Value |
|---|---|
| Customer | Tailwind Mining Co |
| Customer PO | PO-4473 |
| Quote | Q-2219 |
| Order Type | STD-INTL |
| Order Class | Replacement |
| Sales Channel | Distributor |
| Payment Terms | Net 30 (quote) |
| Freight Terms | FOB Origin (quote) |
| Ship-To | Gate 7, Ridgeway Mine Site |
| Status | Draft - Not Submitted, on hold for exceptions |

| Line | Part | Qty | Unit Price (quote) | Extended |
|---|---|---|---|---|
| 1 | PX-300 | 10 | $6,200 | $62,000 |
| 2 | SH-NH3 | 10 | $455 | $4,550 |

**Order total at quote prices:** $66,550 (PO states $66,550).
**Exceptions to resolve before entry:**
- Payment terms: PO Net 60 vs quote Net 30
- Region release: SH-NH3 is not released for International orders

A sales operations specialist reviews and enters this order; nothing was submitted to the ERP.

### `extract_po` with po = PO-4474

**Purchase Order Extract: PO-4474**

| Field | Value |
|---|---|
| Customer | Lucerne Labs |
| PO Number | PO-4474 |
| Date Received | 2026-10-03 |
| Ship-To | 45 Science Park Dr, Bldg B |
| Ship-To Contact | Omar Haddad |
| Payment Terms | Net 30 |
| Freight Terms | FOB Origin |
| Referenced Quote | Q-2223 |

| Line | Part | Description | Qty | Unit Price | Extended |
|---|---|---|---|---|---|
| 1 | PX-500 | PX-500 multi-gas analyzer | 2 | $8,900 | $17,800 |
| 2 | SH-CO | Carbon monoxide sensor head | 2 | $395 | $790 |
| 3 | KIT-CAL | Calibration kit | 1 | $280 | $280 |

**PO total:** $18,870 across 3 lines. Every field above was read from the PO; nothing was inferred.
**Next step:** validate it against quote Q-2223.

### `quote_validation` with po = PO-4474

**Quote Validation: PO-4474 vs Q-2223**

| Check | PO | Quote | Result |
|---|---|---|---|
| Customer account | Lucerne Labs | Lucerne Labs | Match |
| Ship-to contact | Omar Haddad | Omar Haddad | Match |
| Ship-to address | 45 Science Park Dr, Bldg B | 45 Science Park Dr, Bldg B | Match |
| Payment terms | Net 30 | Net 30 | Match |
| Freight terms | FOB Origin | FOB Origin | Match |
| Price PX-500 | $8,900 | $8,900 | Match |
| Price SH-CO | $395 | $395 | Match |
| Price KIT-CAL | $280 | $280 | Match |

**Result:** All fields match the quote. Price tolerance is 1% per line.
**Next step:** check the product configuration.

### `configuration_check` with po = PO-4474

**Configuration Check: PO-4474 (Lucerne Labs)**

| Rule | Result | Detail |
|---|---|---|
| Compatible pairing | Pass | SH-CO with PX-500 |

**Result:** 1 of 1 configuration rules pass. Configuration is valid.

### `draft_sales_order` with po = PO-4474

**Draft Sales Order: PO-4474 - Not Submitted**

| Header | Value |
|---|---|
| Customer | Lucerne Labs |
| Customer PO | PO-4474 |
| Quote | Q-2223 |
| Order Type | STD-DOM |
| Order Class | Upgrade |
| Sales Channel | Direct industrial |
| Payment Terms | Net 30 (quote) |
| Freight Terms | FOB Origin (quote) |
| Ship-To | 45 Science Park Dr, Bldg B |
| Status | Draft - Not Submitted, ready to enter |

| Line | Part | Qty | Unit Price (quote) | Extended |
|---|---|---|---|---|
| 1 | PX-500 | 2 | $8,900 | $17,800 |
| 2 | SH-CO | 2 | $395 | $790 |
| 3 | KIT-CAL | 1 | $280 | $280 |

**Order total at quote prices:** $18,870 (PO states $18,870).
**Exceptions to resolve before entry:**
- None

A sales operations specialist reviews and enters this order; nothing was submitted to the ERP.

### `extract_po` with po = PO-4475

**Purchase Order Extract: PO-4475**

| Field | Value |
|---|---|
| Customer | Relecloud Utilities |
| PO Number | PO-4475 |
| Date Received | 2026-10-04 |
| Ship-To | 300 Grid Ave, Receiving |
| Ship-To Contact | Mei Tanaka |
| Payment Terms | Net 30 |
| Freight Terms | FOB Origin |
| Referenced Quote | Q-2226 |

| Line | Part | Description | Qty | Unit Price | Extended |
|---|---|---|---|---|---|
| 1 | PX-300 | PX-300 portable gas analyzer | 8 | $6,100 | $48,800 |
| 2 | SH-CO | Carbon monoxide sensor head | 8 | $395 | $3,160 |

**PO total:** $51,960 across 2 lines. Every field above was read from the PO; nothing was inferred.
**Next step:** validate it against quote Q-2226.

### `quote_validation` with po = PO-4475

**Quote Validation: PO-4475 vs Q-2226**

| Check | PO | Quote | Result |
|---|---|---|---|
| Customer account | Relecloud Utilities | Relecloud Utilities | Match |
| Ship-to contact | Mei Tanaka | Mei Tanaka | Match |
| Ship-to address | 300 Grid Ave, Receiving | 300 Grid Ave, Receiving | Match |
| Payment terms | Net 30 | Net 30 | Match |
| Freight terms | FOB Origin | FOB Origin | Match |
| Price PX-300 | $6,100 | $6,100 | Match |
| Price SH-CO | $395 | $395 | Match |
| Buying group | Not stated | Trey Purchasing Network | Assign from quote |

**Result:** 1 exception: Buying group is Not stated on the PO vs Trey Purchasing Network on the quote. Price tolerance is 1% per line.
**Next step:** confirm buying group with the account owner before entry.

### `configuration_check` with po = PO-4475

**Configuration Check: PO-4475 (Relecloud Utilities)**

| Rule | Result | Detail |
|---|---|---|
| Compatible pairing | Pass | SH-CO with PX-300 |

**Result:** 1 of 1 configuration rules pass. Configuration is valid.

### `draft_sales_order` with po = PO-4475

**Draft Sales Order: PO-4475 - Not Submitted**

| Header | Value |
|---|---|
| Customer | Relecloud Utilities |
| Customer PO | PO-4475 |
| Quote | Q-2226 |
| Order Type | STD-DOM |
| Order Class | New |
| Sales Channel | Public sector |
| Payment Terms | Net 30 (quote) |
| Freight Terms | FOB Origin (quote) |
| Ship-To | 300 Grid Ave, Receiving |
| Status | Draft - Not Submitted, on hold for exceptions |

| Line | Part | Qty | Unit Price (quote) | Extended |
|---|---|---|---|---|
| 1 | PX-300 | 8 | $6,100 | $48,800 |
| 2 | SH-CO | 8 | $395 | $3,160 |

**Order total at quote prices:** $51,960 (PO states $51,960).
**Exceptions to resolve before entry:**
- Buying group: assign Trey Purchasing Network from the quote

A sales operations specialist reviews and enters this order; nothing was submitted to the ERP.

## Record resolution rules

- The queue is fixed at five POs: PO-4471 Woodgrove Water Authority, PO-4472 Coho Refining, PO-4473 Tailwind Mining Co, PO-4474 Lucerne Labs, PO-4475 Relecloud Utilities.
- `po` accepts a PO number (with or without the PO- prefix) or part of the customer name, default PO-4471. A value that matches nothing returns "No synthetic purchase order matches".
- Price tolerance is 1% per line against the accepted quote; the draft sales order always uses quote prices and quote terms.
- Configuration rules: PX-300 takes SH-CO or SH-NH3; PX-500 takes SH-CO, SH-H2S or SH-NH3; every SH-H2S needs one KIT-SAFE; SH-NH3 is not released for International orders.

## Locked-case evidence contract

Each locked case below routes to one skill; a correct answer always contains every listed evidence string.

| Case | Persona | Prompt | Skill | Must include |
|---|---|---|---|---|
| OE-01 | Sales Operations Specialist | What's in my PO queue this morning? | `order-queue` | `5 purchase orders`; `$221,900`; `Woodgrove Water Authority` |
| OE-02 | Sales Operations Specialist | Read PO-4471 and pull out the order details. | `extract-po` | `1200 Reservoir Rd, Dock 3`; `Hannah Cole`; `PO total` |
| OE-03 | Sales Operations Specialist | Does PO-4471 match the quote? | `quote-validation` | `$410 on the PO vs $395 on the quote`; `Price tolerance is 1%`; `Mismatch` |
| OE-04 | Product Configuration Analyst | Check the product configuration on the Coho Refining order. | `configuration-check` | `SH-H2S needs KIT-SAFE`; `1 of 2 configuration rules pass`; `Never enter this order with the wrong configuration` |
| OE-05 | Sales Operations Specialist | What order type, class and sales channel should PO-4471 go in as? | `order-classification` | `STD-DOM`; `Public sector`; `Order Class` |
| OE-06 | Sales Operations Specialist | Prepare the sales order for PO-4471 so I can enter it. | `draft-sales-order` | `Not Submitted`; `$27,940`; `nothing was submitted to the ERP` |
| OE-07 | Sales Operations Manager | Across the whole queue, which orders are ready to enter and which need a fix? | `queue-review` | `1 of 5 purchase orders are ready`; `Lucerne Labs`; `Needs fix` |
