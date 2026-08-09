# Order Status Communications Agent — Exact Review Rules and Locked Outputs

> **SYNTHETIC PILOT RULES.** Use this file with the complete synthetic source
> records. It contains the exact deterministic operation outputs captured by the
> source agent. These outputs are evidence and recommendations, not completed
> operational side effects or customer outcomes.

## Locked case routing

| Case | Persona | Operation | Exact prompt | Required deterministic evidence |
|---|---|---|---|---|
| OS-01 | Customer Service Representative | `order_lookup` | Which orders are on track or delayed, and where should customer service focus its review? | `ORD-7813`; `DELAYED` |
| OS-02 | Account Manager | `shipment_tracking` | What shipment evidence is recorded for the shipped order, and what still needs carrier validation? | `ORD-7812`; `XPO-884291047` |
| OS-03 | Operations Leader | `delay_notification` | Prepare the internal delay and recovery review for the at-risk customer order without changing any schedule. | `ORD-7813`; `Recorded synthetic recovery options` |
| OS-04 | Account Manager | `customer_update` | Draft the customer updates for approval, but do not send an email, portal update, EDI message, or Teams message. | `Customer Update Drafts`; `No email, EDI message` |

## Deterministic calculation and interpretation rules

- Order value is quantity multiplied by unit price.
- At-risk status is derived from the fixed delayed status or presence in the delay record.
- Days left uses the source fixed reference date of 2026-03-17 and the implemented deterministic date arithmetic.
- Customer drafts must use the exact synthetic contact, tier, preferred channel, account owner, order, shipment, and delay records.
- Carrier and production facts must be validated in approved ERP, MES, carrier, and CRM systems before customer use.

## Exact deterministic operation outputs

### `order_lookup` — Order status dashboard

Use for exact order, customer, product, quantity, value, status, completion, promise date, days left, and at-risk value.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Order Status Dashboard

> Fixed synthetic snapshot; no live ERP, MES, carrier, or CRM system was queried.

| Order | Customer | Product | Qty | Value | Status | Complete | Promise Date | Days Left |
|-------|----------|---------|-----|-------|--------|----------|--------------|-----------|
| ORD-7810 | Ford Motor Company | 6R140 Transmission Housing | 2,500 | $420,000.00 | in_production | 74% | 2026-03-20 | 3 |
| ORD-7811 | Caterpillar Inc. | D11 Track Frame Weldment | 40 | $498,000.00 | in_production | 45% | 2026-04-10 | 23 |
| ORD-7812 | Tesla Inc. | Model Y Rocker Panel Stampin | 8,000 | $340,000.00 | shipped | 100% | 2026-03-15 | -2 |
| ORD-7813 | John Deere | Hydraulic Cylinder Barrel | 600 | $231,000.00 | delayed **DELAYED** | 30% | 2026-03-28 | 11 |

**Total order book value:** $1,489,000.00
**At-risk order value:** $231,000.00
```

### `shipment_tracking` — Shipment tracking

Use for exact order, carrier, tracking number, ship date, estimated delivery, route, weight, and recorded status.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Shipment Tracking

> Synthetic shipment record; confirm status in the approved carrier system.

| Order | Carrier | Tracking | Ship Date | Est Delivery | Route | Weight | Status |
|-------|---------|----------|-----------|-------------|-------|--------|--------|
| ORD-7812 | XPO Logistics | XPO-884291047 | 2026-03-12 | 2026-03-15 | Detroit, MI -> Fremont, CA | 4,200 kg | in_transit |

### Shipped Orders Detail

- **ORD-7812** (Tesla Inc.): Model Y Rocker Panel Stamping -- 8,000 units, $340,000.00
```

### `delay_notification` — Internal delay review

Use for exact delayed order, product, quantity, value, delay dates, reason, cost, owner, response window, channel, and recorded recovery options.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Internal Delay Review

> Fixed synthetic draft for authorized review. No production schedule, shipment, or customer record was changed.

### ORD-7813 -- John Deere
- **Product:** Hydraulic Cylinder Barrel
- **Quantity:** 600 units ($231,000.00)
- **Delay:** 11 days (2026-03-28 -> 2026-04-08)
- **Reason:** Raw material shortage -- alloy steel bar stock delayed from supplier
- **Cost impact:** $14,200.00
- **Account manager:** Robert Kim
- **SLA response window:** 4 hours
- **Preferred channel:** email

**Recorded synthetic recovery options:**
- Alternate supplier qualified; first shipment arriving 2026-03-19
- Weekend overtime shifts approved for CNC cell
- Partial shipment of 200 units by 2026-03-28

```

### `customer_update` — Customer update drafts

Use for exact customer, contact, tier, preferred channel, authorized owner, subject, order status, shipment evidence, delay evidence, recovery wording, and signature.

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output:

```markdown
## Customer Update Drafts

> Fixed synthetic drafts; approval required. No email, EDI message, portal update, Teams message, or other customer communication was sent.

The following draft messages have been prepared for all active orders:

---
### ORD-7810 -- Ford Motor Company

**Synthetic communication profile:** Strategic tier; preferred channel email; authorized owner Sarah Lin.

**Subject:** Order ORD-7810 Status Update -- 6R140 Transmission Housing

Dear James Mitchell,

Your order is progressing on schedule.

- **Completion:** 74%
- **Promised delivery:** 2026-03-20

Please do not hesitate to reach out with any questions.

Best regards,
Sarah Lin

---
### ORD-7811 -- Caterpillar Inc.

**Synthetic communication profile:** Strategic tier; preferred channel EDI; authorized owner Robert Kim.

**Subject:** Order ORD-7811 Status Update -- D11 Track Frame Weldment

Dear Rita Vasquez,

Your order is progressing on schedule.

- **Completion:** 45%
- **Promised delivery:** 2026-04-10

Please do not hesitate to reach out with any questions.

Best regards,
Robert Kim

---
### ORD-7812 -- Tesla Inc.

**Synthetic communication profile:** Priority tier; preferred channel portal; authorized owner Sarah Lin.

**Subject:** Order ORD-7812 Status Update -- Model Y Rocker Panel Stamping

Dear Derek Chung,

Your order has shipped and is on its way.

- **Carrier:** XPO Logistics
- **Tracking:** XPO-884291047
- **Est. delivery:** 2026-03-15

Please do not hesitate to reach out with any questions.

Best regards,
Sarah Lin

---
### ORD-7813 -- John Deere

**Synthetic communication profile:** Priority tier; preferred channel email; authorized owner Robert Kim.

**Subject:** Order ORD-7813 Status Update -- Hydraulic Cylinder Barrel

Dear Angela Torres,

We are writing to inform you of a revised delivery date for your order.

- **Original date:** 2026-03-28
- **Revised date:** 2026-04-08
- **Reason:** Raw material shortage -- alloy steel bar stock delayed from supplier

**Recovery actions underway:**
- Alternate supplier qualified; first shipment arriving 2026-03-19
- Weekend overtime shifts approved for CNC cell
- Partial shipment of 200 units by 2026-03-28

Please do not hesitate to reach out with any questions.

Best regards,
Robert Kim


Customer updates require an approved communication tool and an authorized sender.
```

## Authorization and no-side-effect boundary

Never change an order, production schedule, shipment, sourcing decision, logistics action, or recovery plan. Never send email, EDI, portal, Teams, or any other customer communication. An approved communication tool and authorized sender are required.

Always distinguish: **source record**, **derived synthetic analysis**,
**recommendation**, **required human approval**, and **external action not performed**.
If a requested fact is absent from the complete records, say it is not present in
the fixed synthetic snapshot rather than inventing it.
