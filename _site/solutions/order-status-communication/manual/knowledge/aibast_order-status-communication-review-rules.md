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
| OS-03 | Operations Leader | `delay_notification` | Prepare the internal delay and recovery review for the E-Cars Corp transmission housing order without changing any schedule. | `Midwest Casting`; `Recorded synthetic recovery options` |
| OS-04 | Account Manager | `customer_update` | Draft the customer updates for approval, but do not send an email, portal update, EDI message, or Teams message. | `Customer Update Drafts`; `No email, EDI message` |
| OS-05 | Production Manager | `engagement_plan` | Show the customer touchpoints planned for the E-Cars Corp delay across email, EDI, portal and the follow-up call. | `EDI 856 ASN`; `Today 2 PM EST`; `Ready to send` |
| OS-06 | Production Manager | `quality_validation` | What quality assurance and validation is in place for the E-Cars Corp housings from the alternative supplier? | `PPAP Level 3`; `99.8%`; `Metallurgical testing` |
| OS-07 | Operations Leader | `performance_dashboard` | Show the performance dashboard for the E-Cars Corp account and this order. | `96.2%`; `$14.2M`; `Lessons learned` |

## Deterministic calculation and interpretation rules

- Order value is quantity multiplied by unit price (E-Cars Corp: 2,500 x $168 = $420,000).
- At-risk status is derived from the fixed delayed status or presence in the delay record.
- Days use calendar arithmetic from the fixed reference date 2026-03-17: promised 2026-03-20 is 3 days, revised 2026-03-23 is 6 days; a delayed order shows days to its revised date, a shipped order shows "-".
- Compensation = compensation percent x order value (2% x $420,000 = $8,400). Recovery cost = sum of action costs ($54,000).
- Yield = quality passed / completed (1,847 / 1,850 = 99.8%). Remaining units = in production + queued (650).
- Customer drafts, EDI updates, portal syncs, calls, discounts and CRM notes are prepared for an authorized person; none is sent or applied by the agent.

## Exact deterministic operation outputs

### `order_lookup` — Order status and situation

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Order Status: E-Cars Corp PO #F2024-3847 (ORD-7810)

> Fixed synthetic snapshot; no live ERP, MES, carrier, or CRM system was queried.

**Order Details:**

- Customer: E-Cars Corp - Manufacturing Plant
- Product: 6R140 Transmission Housing
- Quantity: 2,500 units
- Original delivery: 3 days from now (2026-03-20)
- Current status: 74% complete

**Situation:**

- Supplier delay: aluminum casting equipment failure + force majeure
- Impact: 3-day delay (reduced from initial 7 days)
- Recovery plan: Active

**Open order book:**

| Order | Customer | Product | Qty | Value | Status | Complete | Promise Date | Days Left |
|-------|----------|---------|-----|-------|--------|----------|--------------|-----------|
| ORD-7810 | E-Cars Corp | 6R140 Transmission Housing | 2,500 | $420,000.00 | delayed **DELAYED** | 74% | 2026-03-20 | 6 |
| ORD-7811 | Ironridge Equipment Co. | Track Frame Weldment | 40 | $498,000.00 | in_production | 45% | 2026-04-10 | 24 |
| ORD-7812 | Voltline Motors | EV Rocker Panel Stamping | 8,000 | $340,000.00 | shipped | 100% | 2026-03-15 | - |
| ORD-7813 | Greenfield Agri Machines | Hydraulic Cylinder Barrel | 600 | $231,000.00 | delayed **DELAYED** | 30% | 2026-03-28 | 22 |

**Total order book value:** $1,489,000.00
**At-risk order value:** $651,000.00

Source: [D365 Production + Order Management] (synthetic)

**Next step:** draft the customer communication?
```

### `shipment_tracking` — Shipment tracking

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Shipment Tracking

> Synthetic shipment record; confirm status in the approved carrier system.

| Order | Carrier | Tracking | Ship Date | Est Delivery | Route | Weight | Status |
|-------|---------|----------|-----------|-------------|-------|--------|--------|
| ORD-7812 | XPO Logistics | XPO-884291047 | 2026-03-12 | 2026-03-15 | Detroit, MI -> Fremont, CA | 4,200 kg | in_transit |

### Shipped Orders Detail

- **ORD-7812** (Voltline Motors): EV Rocker Panel Stamping -- 8,000 units, $340,000.00

Carrier status still needs validation in the approved carrier system.
```

### `delay_notification` — Recovery plan details

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Delay Mitigation & Recovery: E-Cars Corp PO #F2024-3847 (ORD-7810)

> Fixed synthetic draft for authorized review. No production schedule, shipment, or customer record was changed.

**Root Cause:**

- Supplier: Midwest Casting (aluminum)
- Issue: Supplier delay: aluminum casting equipment failure + force majeure
- Initial impact: 7-day delay

**Recorded synthetic recovery options (our response):**

| Action | Impact | Cost |
|---|---|---|
| Alternative supplier | Secured material | $12K premium |
| Weekend shifts | +150 units | $18K overtime |
| Air freight (first 500 units) | 2-day delivery | $24K (we absorb) |
| Daily output increase | +75 units/day | Existing capacity |

**Result:** 7-day delay -> 3-day delay (recovery cost $54,000)

**Compensation offer (proposed):**

- 2% discount ($8,400 credit on $420,000)
- Priority scheduling on next order
- Dedicated quality liaison

**Updated Timeline:**

- Day 1-2: Complete remaining 650 units
- Day 3: Final quality inspection
- Day 4: Packaging complete
- Day 5-6: Expedited shipping

**Owner:** Sarah Lin; SLA response window 4 hours; preferred channel email.

Source: [Recovery Planning + Logistics] (synthetic)

**Next step:** show the customer touchpoints?
```

### `customer_update` — Customer communication draft

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Customer Update Drafts

> Fixed synthetic drafts; approval required. No email, EDI message, portal update, Teams message, or other customer communication was sent, and no order, shipment, or production schedule was changed.

### Customer Communication Draft: E-Cars Corp PO #F2024-3847

**Synthetic communication profile:** Strategic tier; preferred channel email; authorized owner Sarah Lin.

**To:** James Mitchell (Procurement Manager)
**CC:** Tom Bradley (Plant Manager), Sarah Chen (Quality), Logistics team
**Subject:** PO #F2024-3847 Status Update - Revised Delivery Date

Dear James,

I'm writing to update you on PO #F2024-3847 (2,500 6R140 Transmission Housing units).

**Current Status:**
- Completed: 1,850 units (74%)
- Quality passed: 1,847 units (99.8% yield)
- In production: 350 units
- Queued: 300 units

**Delivery Update:**
- Original: 3 days from now (2026-03-20)
- Revised: 6 days from now (2026-03-23; 3-day delay)

**Recovery Actions:**
- Alternative supplier: Secured material
- Weekend shifts: +150 units
- Air freight (first 500 units): 2-day delivery
- Daily output increased: 250 -> 325 units

Please do not hesitate to reach out with any questions.

Best regards,
Sarah Lin

Ready for you to review and send from Outlook; customer updates require an approved communication tool and an authorized sender.

Source: [Email Template + Production Data] (synthetic)

**Next step:** see the detailed recovery plan?
```

### `engagement_plan` — Multi-channel engagement

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Multi-Channel Customer Engagement: E-Cars Corp PO #F2024-3847

> Fixed synthetic drafts; approval required. No email, EDI message, portal update, Teams message, or other customer communication was sent, and no order, shipment, or production schedule was changed.

Tailored to the Strategic tier: Email, EDI 856 ASN, Supplier portal, Phone call.

| Channel | Prepared action | Status |
|---|---|---|
| Email (primary) | To James Mitchell (Procurement Manager); CC Tom Bradley (Plant Manager), Sarah Chen (Quality), Logistics team; read receipt requested | Ready to send |
| EDI 856 ASN | Updated ship dates from the revised timeline; acknowledgment expected within 2 hours | Ready to transmit |
| E-Cars Corp supplier portal | Status and revised date | Ready to sync |
| Follow-up call | Today 2 PM EST with Account Manager + Production Manager; agenda: recovery plan review | Invite ready to send |

**Touchpoints prepared:** 4

**Proactive monitoring (to switch on):** daily production updates, quality milestone alerts, shipping tracker with real-time status.

**Relationship management:** 2% discount ($8,400) ready to apply on approval; account note for priority service drafted.

Source: [Outlook + EDI + Supplier Portal + CRM] (synthetic)

**Next step:** review quality assurance and validation?
```

### `quality_validation` — Quality assurance and validation

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Quality Assurance & Validation: E-Cars Corp PO #F2024-3847

> Fixed synthetic quality record; confirm in the quality management system before sharing.

**Incoming material (alternative supplier):**

- 100% dimensional inspection
- Metallurgical testing (batch samples)
- Hardness verification
- Chemical composition analysis
- Certification: material test reports provided

**Production quality:**

- In-process inspection: every 50 units
- Statistical process control (SPC) active
- Coordinate measuring machine (CMM): 10% sample
- Visual inspection: 100%
- Current yield: 99.8% (1,847 of 1,850; spec 99.5%)

**Final validation:**

- Functional testing: 100%
- Dimensional report: full first article
- Surface finish verification
- Packaging integrity check
- Quality documentation: Certificate of Conformance included

**E-Cars Corp-specific requirements:**

- PPAP Level 3 maintained
- Q1 supplier rating protected
- Advanced quality planning review: complete

Source: [Quality Management System] (synthetic)

**Next step:** see the performance dashboard?
```

### `performance_dashboard` — Performance dashboard

When answering from uploaded files alone, preserve the identifiers, headings,
measurements, amounts, dates, statuses, and authorization language in this
canonical source output (default order):

```markdown
## Order & Customer Performance: E-Cars Corp

> Fixed synthetic metrics for internal review.

**This order (PO #F2024-3847):**

- On-time delivery: Recovering (revised date)
- Quality: 99.8% (target 99.5%)
- Communication: proactive (4 touchpoints prepared)
- Customer satisfaction: pending (survey to send after delivery)

**E-Cars Corp account (last 12 months):**

| Metric | Value |
|---|---|
| Total orders | 47 |
| On-time delivery | 96.2% |
| Quality PPM | 185 (excellent) |
| Supplier rating | Q1 (top tier) |
| Annual revenue | $14.2M |

**Delay management effectiveness:**

- Average delay communication: <4 hours
- Recovery plan implementation: 94% success
- Customer retention after delays: 97%

**Lessons learned:**

- Supplier diversification accelerated
- Safety stock policy updated
- Communication template refined
- Recovery playbook enhanced

Source: [Power BI + CRM + Quality Systems] (synthetic)
```

## Authorization and no-side-effect boundary

Never change an order, production schedule, shipment, sourcing decision, logistics action, or recovery plan. Never send email, EDI, portal, Teams, or any other customer communication. An approved communication tool and authorized sender are required.

Always distinguish: **source record**, **derived synthetic analysis**,
**recommendation**, **required human approval**, and **external action not performed**.
If a requested fact is absent from the complete records, say it is not present in
the fixed synthetic snapshot rather than inventing it.
