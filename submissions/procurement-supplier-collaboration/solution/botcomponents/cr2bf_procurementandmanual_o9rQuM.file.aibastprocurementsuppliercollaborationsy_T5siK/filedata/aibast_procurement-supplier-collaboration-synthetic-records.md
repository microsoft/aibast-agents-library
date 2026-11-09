# Procurement and Supplier Collaboration — Complete Synthetic Records

> FIXED FICTIONAL SNAPSHOT. Northcombe Power Distribution and every requisition, framework, supplier, RFQ, bid, purchase order, shipping notice, invoice and amount in this snapshot are invented. Never match them to a real organization, person, or live record.

## Complete synthetic records

Every value the agent uses, exactly as bundled in the portable agent source. need_in_days, closes_in_days, committed_in_days, ship_in_days and arrive_in_days count forward from the snapshot day; issued_days_ago counts back. In the recorded responses, calendar dates are shown relative to the snapshot day.

### Company and policy

```json
{
 "name": "Northcombe Power Distribution",
 "policy": {
  "direct_award_limit": 250000,
  "open_tender_threshold": 500000,
  "otif_floor": 90,
  "price_tolerance_pct": 2,
  "weights": {
   "price": 50,
   "lead_time": 20,
   "quality": 20,
   "sustainability": 10
  }
 },
 "defaults": {
  "requisition": "REQ-7712",
  "rfq": "RFQ-3301"
 }
}
```

### Requisitions

```json
[
 {
  "id": "REQ-7712",
  "item": "Distribution transformer, 500 kVA 11/0.433 kV",
  "qty": 24,
  "unit_estimate": 28000,
  "source": "Stock replenishment model: Central Stores below reorder point (6 on hand, 30-unit reorder level)",
  "framework": "FW-DT-22",
  "category": "Distribution transformers",
  "critical": true,
  "need_in_days": 126
 },
 {
  "id": "REQ-7710",
  "item": "33 kV XLPE cable, 3 x 300 mm2",
  "qty": "6 km",
  "unit_estimate": null,
  "value": 1380000,
  "source": "Capital project: Fenwick 33 kV reinforcement",
  "framework": null,
  "category": "HV cable",
  "critical": true,
  "need_in_days": 160
 },
 {
  "id": "REQ-7715",
  "item": "Pole-top fuse kit, 11 kV",
  "qty": 400,
  "unit_estimate": 95,
  "source": "Maintenance plan: overhead line refurbishment, quarter 1",
  "framework": "FW-OH-19",
  "category": "Overhead line fittings",
  "critical": false,
  "need_in_days": 45
 }
]
```

### Framework suppliers

```json
[
 {
  "name": "Brightwater Transformers",
  "framework": "FW-DT-22",
  "otif": 97,
  "open_ncr": "None"
 },
 {
  "name": "Halden Transformer Works",
  "framework": "FW-DT-22",
  "otif": 94,
  "open_ncr": "None"
 },
 {
  "name": "Kelso Electrical Supply",
  "framework": "FW-DT-22",
  "otif": 92,
  "open_ncr": "1 minor"
 },
 {
  "name": "Marlow Power Products",
  "framework": "FW-DT-22",
  "otif": 84,
  "open_ncr": "1 major (oil leaks)"
 },
 {
  "name": "Ferris Line Fittings",
  "framework": "FW-OH-19",
  "otif": 98,
  "open_ncr": "None"
 }
]
```

### RFQs, published pack and clarifications

```json
[
 {
  "id": "RFQ-3301",
  "requisition": "REQ-7712",
  "route": "Mini-competition under framework FW-DT-22",
  "closes_in_days": 6,
  "invited": [
   "Brightwater Transformers",
   "Halden Transformer Works",
   "Kelso Electrical Supply"
  ],
  "clarifications": [
   {
    "id": "CL-1",
    "question": "Is a sealed tank design acceptable?",
    "answer": "Yes, if it meets ES-DT-04; published to all bidders."
   }
  ],
  "pack": [
   {
    "topic": "Delivery lots",
    "answer": "Delivery is 24 units in three lots of 8 to Central Stores. Lot dates are set at award from each bidder's quoted lead time. A different lot plan may be offered only as a variant bid under section 5.3, alongside a compliant bid."
   },
   {
    "topic": "Specification",
    "answer": "500 kVA, 11/0.433 kV, vector group Dyn11, losses as set in specification ES-DT-04 (no tolerance on load losses)."
   },
   {
    "topic": "Quality documents",
    "answer": "Bids must include an ISO 9001 certificate and type test certificates for the offered design. A bid missing a type test certificate scores half marks on quality."
   },
   {
    "topic": "Evaluation",
    "answer": "Price 50%, lead time 20%, quality 20%, sustainability 10%."
   },
   {
    "topic": "Closing date",
    "answer": "The RFQ closes at 12:00 on the closing day shown in the portal. Extensions apply to all bidders and are published as a clarification."
   }
  ]
 }
]
```

### Bids

```json
[
 {
  "rfq": "RFQ-3301",
  "supplier": "Brightwater Transformers",
  "price": 648000,
  "lead_weeks": 9,
  "quality_complete": true,
  "sustainability": 9,
  "sustainability_note": "Environmental product declaration; 30% recycled core steel"
 },
 {
  "rfq": "RFQ-3301",
  "supplier": "Halden Transformer Works",
  "price": 630000,
  "lead_weeks": 10,
  "quality_complete": true,
  "sustainability": 6,
  "sustainability_note": "Environmental product declaration"
 },
 {
  "rfq": "RFQ-3301",
  "supplier": "Kelso Electrical Supply",
  "price": 612000,
  "lead_weeks": 13,
  "quality_complete": false,
  "sustainability": 2,
  "sustainability_note": "None offered",
  "quality_gap": "Type test certificate missing for the offered design"
 }
]
```

### Purchase orders and shipping notices

```json
[
 {
  "po": "PO-88017",
  "supplier": "Corran Cables",
  "item": "11 kV cable drums, 500 m",
  "qty": 6,
  "acknowledged": true,
  "committed_in_days": 4,
  "asn": {
   "qty": 4,
   "ship_in_days": 3,
   "arrive_in_days": 4
  },
  "remaining_note": "ASN shows the last 2 drums arriving in 13 days",
  "remaining_arrive_in_days": 13,
  "impact": "Feeder 7 section replacement at Harbour Street is planned to start in 10 days and needs all 6 drums on site"
 },
 {
  "po": "PO-88044",
  "supplier": "Ardmore Switchgear",
  "item": "11 kV switchboard panels",
  "qty": 8,
  "acknowledged": false,
  "issued_days_ago": 5,
  "committed_in_days": 70,
  "asn": null,
  "impact": "Ashby Road switchboard replacement"
 },
 {
  "po": "PO-88031",
  "supplier": "Ferris Line Fittings",
  "item": "Pole-top fuse kits, 11 kV",
  "qty": 400,
  "acknowledged": true,
  "committed_in_days": 12,
  "asn": {
   "qty": 400,
   "ship_in_days": 9,
   "arrive_in_days": 11
  },
  "impact": "Overhead line refurbishment"
 }
]
```

### Invoices awaiting match

```json
[
 {
  "invoice": "INV-55120",
  "supplier": "Corran Cables",
  "po": "PO-88010",
  "item": "11 kV cable drums, 500 m",
  "po_qty": 4,
  "po_price": 41500,
  "gr_qty": 4,
  "inv_qty": 4,
  "inv_price": 41500
 },
 {
  "invoice": "INV-55133",
  "supplier": "Halden Transformer Works",
  "po": "PO-88022",
  "item": "Distribution transformer, 315 kVA",
  "po_qty": 10,
  "po_price": 26800,
  "gr_qty": 9,
  "inv_qty": 10,
  "inv_price": 26800,
  "gr_note": "1 unit rejected at receipt: damaged radiator"
 },
 {
  "invoice": "INV-55141",
  "supplier": "Ferris Line Fittings",
  "po": "PO-88003",
  "item": "Line clamps, 33 kV",
  "po_qty": 200,
  "po_price": 61,
  "gr_qty": 200,
  "inv_qty": 200,
  "inv_price": 64
 }
]
```

## Exact responses for every locked case

### PSC-01 — Sourcing plan

Prompt: "What requisitions are waiting, how should we buy each one, and who should we invite for the transformer order?"

Operation: `sourcing_plan`; arguments: `{"operation": "sourcing_plan"}`

**Sourcing Plan - Northcombe Power Distribution**

**Open requisitions:** 3 | **Shortlist shown for:** REQ-7712

| Requisition | Item | Quantity | Estimated value | Demand source | Need by | Recommended route |
|-------------|------|----------|-----------------|---------------|---------|-------------------|
| REQ-7712 | Distribution transformer, 500 kVA 11/0.433 kV | 24 | $672,000 | Stock replenishment model: Central Stores below reorder point (6 on hand, 30-unit reorder level) | day +126 | Mini-competition under framework FW-DT-22 |
| REQ-7710 | 33 kV XLPE cable, 3 x 300 mm2 | 6 km | $1,380,000 | Capital project: Fenwick 33 kV reinforcement | day +160 | Open tender |
| REQ-7715 | Pole-top fuse kit, 11 kV | 400 | $38,000 | Maintenance plan: overhead line refurbishment, quarter 1 | day +45 | Direct award under framework FW-OH-19 |

**REQ-7712: Mini-competition under framework FW-DT-22**
Why: framework order above the $250,000 direct-award limit. Critical network material.

**Eligible supplier shortlist (framework FW-DT-22):**

| Supplier | On-time in full | Open nonconformance | Eligible |
|----------|-----------------|---------------------|----------|
| Brightwater Transformers | 97% | None | Yes |
| Halden Transformer Works | 94% | None | Yes |
| Kelso Electrical Supply | 92% | 1 minor | Yes |
| Marlow Power Products | 84% | 1 major (oil leaks) | No: on-time in full below 90%; open major nonconformance |

**Status:** Recommendation - the category manager confirms the route and shortlist before the RFQ is issued in the supplier portal. Nothing has been issued.

> Read-only synthetic snapshot of a fictional utility. Nothing was awarded, ordered, sent to a supplier or approved for payment; an authorized person approves every step.

Source: [Synthetic Source-to-Pay Snapshot]
Agents: ProcurementSupplierCollaborationAgent

### PSC-02 — Supplier question

Prompt: "A bidder on the transformer RFQ asks if they can deliver all 24 units in two lots instead of three. What should I tell them?"

Operation: `supplier_query`; arguments: `{"operation": "supplier_query", "question": "Can we deliver all 24 units in two lots instead of three?"}`

**Supplier Question - RFQ-3301**

**RFQ:** RFQ-3301 (Mini-competition under framework FW-DT-22), closes day +6 (in 6 days)
**Question:** "Can we deliver all 24 units in two lots instead of three?"

**Draft answer from the published RFQ pack**
- **Delivery lots:** Delivery is 24 units in three lots of 8 to Central Stores. Lot dates are set at award from each bidder's quoted lead time. A different lot plan may be offered only as a variant bid under section 5.3, alongside a compliant bid.

Because the answer is already in the published pack, it can go to this supplier without changing the terms for other bidders.

**Clarifications already published to all bidders:** CL-1 Is a sealed tank design acceptable? Yes, if it meets ES-DT-04; published to all bidders.

**Status:** Draft - the buyer approves and sends the reply in the supplier portal. Nothing has been sent.

> Read-only synthetic snapshot of a fictional utility. Nothing was awarded, ordered, sent to a supplier or approved for payment; an authorized person approves every step.

Source: [Synthetic Source-to-Pay Snapshot]
Agents: ProcurementSupplierCollaborationAgent

### PSC-03 — Bid evaluation

Prompt: "The transformer bids are in. How do they score, and who should the award panel pick?"

Operation: `bid_evaluation`; arguments: `{"operation": "bid_evaluation"}`

**Bid Evaluation - RFQ-3301**

**Weights:** price 50, lead time 20, quality 20, sustainability 10 | **Bids:** 3

| Rank | Supplier | Price | Lead time | Quality | Sustainability | Score |
|------|----------|-------|-----------|---------|----------------|-------|
| 1 | Brightwater Transformers | $648,000 (47.2) | 9 weeks (20.0) | Complete (20.0) | 9/10 (9.0) | **96.2** |
| 2 | Halden Transformer Works | $630,000 (48.6) | 10 weeks (18.0) | Complete (20.0) | 6/10 (6.0) | **92.6** |
| 3 | Kelso Electrical Supply | $612,000 (50.0) | 13 weeks (13.8) | Incomplete (10.0) | 2/10 (2.0) | **75.8** |

**Evaluation narrative**
- **Brightwater Transformers** ranks first at 96.2, 3.7 points ahead of Halden Transformer Works: 9-week lead time, complete quality documents, and environmental product declaration; 30% recycled core steel.
- **Kelso Electrical Supply** is the lowest price at $612,000 ($36,000 below the first-ranked bid) but scores lower: type test certificate missing for the offered design and a 13-week lead time.
- Recommended award: Brightwater Transformers at $648,000, subject to the award panel.

**Status:** Recommendation - the award panel decides and records the award. No supplier has been told the outcome.

> Read-only synthetic snapshot of a fictional utility. Nothing was awarded, ordered, sent to a supplier or approved for payment; an authorized person approves every step.

Source: [Synthetic Source-to-Pay Snapshot]
Agents: ProcurementSupplierCollaborationAgent

### PSC-04 — Delivery tracking

Prompt: "Which of our open orders have delivery problems I need to chase today?"

Operation: `delivery_tracking`; arguments: `{"operation": "delivery_tracking"}`

**Delivery Tracking - Northcombe Power Distribution**

**Open purchase orders:** 3 | **Needing action:** 2 | **On track:** 1

**Needing action**
- **PO-88017** Corran Cables, 11 kV cable drums, 500 m x6: ASN covers 4 of 6 arriving day +4; ASN shows the last 2 drums arriving in 13 days (day +13), 9 days after the committed day +4. Impact: Feeder 7 section replacement at Harbour Street is planned to start in 10 days and needs all 6 drums on site.
- **PO-88044** Ardmore Switchgear, 11 kV switchboard panels x8: Not acknowledged 5 days after issue; the committed date day +70 is unconfirmed. Draft a reminder to Ardmore Switchgear.

**On track**
- PO-88031 Ferris Line Fittings, Pole-top fuse kits, 11 kV x400: ASN matches, arriving day +11 against day +12.

**Status:** Alerts only - the buyer contacts suppliers and the project team re-plans. No message was sent and no order was changed.

> Read-only synthetic snapshot of a fictional utility. Nothing was awarded, ordered, sent to a supplier or approved for payment; an authorized person approves every step.

Source: [Synthetic Source-to-Pay Snapshot]
Agents: ProcurementSupplierCollaborationAgent

### PSC-05 — Three-way match

Prompt: "Which supplier invoices can go for payment approval today, and which ones need to be held?"

Operation: `invoice_match`; arguments: `{"operation": "invoice_match"}`

**Three-Way Match - Northcombe Power Distribution**

**Invoices awaiting match:** 3 | **Price tolerance:** 2%

| Invoice | Supplier | PO | PO qty | Received | Invoiced | PO unit price | Invoiced unit price | Invoice total | Result |
|---------|----------|----|--------|----------|----------|---------------|---------------------|---------------|--------|
| INV-55120 | Corran Cables | PO-88010 | 4 | 4 | 4 | $41,500 | $41,500 | $166,000 | Matched: ready for payment approval |
| INV-55133 | Halden Transformer Works | PO-88022 | 10 | 9 | 10 | $26,800 | $26,800 | $268,000 | Hold |
| INV-55141 | Ferris Line Fittings | PO-88003 | 200 | 200 | 200 | $61 | $64 | $12,800 | Hold |

**Holds**
- **INV-55133** Halden Transformer Works: invoiced 10 but received 9 (1 unit rejected at receipt: damaged radiator). Amount in question $26,800. Draft: ask the supplier for a credit note or corrected invoice.
- **INV-55141** Ferris Line Fittings: price +4.9% against the PO, outside the 2% tolerance. Amount in question $600. Draft: ask the supplier for a credit note or corrected invoice.

**Status:** Draft - accounts payable approves matched invoices for payment in the finance module and resolves holds with the supplier. Nothing has been paid or sent.

> Read-only synthetic snapshot of a fictional utility. Nothing was awarded, ordered, sent to a supplier or approved for payment; an authorized person approves every step.

Source: [Synthetic Source-to-Pay Snapshot]
Agents: ProcurementSupplierCollaborationAgent

## Locked-case evidence contract

| Case | Persona | Prompt | Operation | Must include |
|---|---|---|---|---|
| PSC-01 | Category Manager | What requisitions are waiting, how should we buy each one, and who should we invite for the transformer order? | `sourcing_plan` | Sourcing Plan; REQ-7712; Marlow Power Products |
| PSC-02 | Buyer | A bidder on the transformer RFQ asks if they can deliver all 24 units in two lots instead of three. What should I tell them? | `supplier_query` | Supplier Question; RFQ-3301; variant bid |
| PSC-03 | Category Manager | The transformer bids are in. How do they score, and who should the award panel pick? | `bid_evaluation` | Bid Evaluation; Brightwater Transformers; Kelso Electrical Supply |
| PSC-04 | Expediter | Which of our open orders have delivery problems I need to chase today? | `delivery_tracking` | Delivery Tracking; PO-88017; PO-88044 |
| PSC-05 | Accounts Payable Lead | Which supplier invoices can go for payment approval today, and which ones need to be held? | `invoice_match` | Three-Way Match; INV-55133; INV-55141 |

The response for each case must contain every must-include value and must not contain: I do not have access; I cannot help.
