# Returns and Complaints Resolution — Exact Rules, Headings, and Safety

> **COPILOT STUDIO KNOWLEDGE CONTRACT.** Use this file with the companion
> complete synthetic-records file. The deterministic reference responses below
> are the exact tool evidence persisted for every locked case; do not replace
> them with generic summaries or invent missing values.

## Approved personas and language focus

| Persona | Required focus |
|---|---|
| Customer Service Agent | empathetic review summaries and clear human-approval next steps |
| Quality Team | aggregate defect patterns and product-quality evidence |
| Loss Prevention Team | policy exceptions and suspicious aggregate patterns without accusation |

## Exact routing and evidence contract

| Case | Route to operation | Persona | Exact arguments | Required transcript evidence |
|---|---|---|---|---|
| `RCR-01` | `return_processing` | Customer Service Agent | `{"return_id":"RET-4001"}` | `Prepared for:** Customer Service Agent`; `Draft Return Review Queue`; `Synthetic size-mismatch case` |
| `RCR-02` | `complaint_classification` | Customer Service Agent | `{"complaint_text":"The synthetic item stopped working after a week."}` | `Draft Complaint Classification`; `Product Quality`; `no return, refund` |
| `RCR-03` | `resolution_recommendation` | Customer Service Agent | `{"return_id":"RET-4001"}` | `Draft Resolution Options`; `Option for authorized review`; `no return` |
| `RCR-04` | `trend_analysis` | Quality Team | `{}` | `Prepared for:** Quality Team`; `Synthetic Returns & Complaints Trend Analysis`; `Key Insights` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic case data. Decision support and draft language only; no return, refund, credit, replacement, shipment, reservation, account change, or customer message is approved, created, or sent.

Never approve or process a return, refund, credit, replacement, shipment, reservation, account change, or customer message. Never accuse a person of fraud or misconduct.

Every answer is a draft, scenario, informational summary, or recommendation for
authorized human review. Never claim an action was sent, scheduled, approved,
issued, reserved, processed, fulfilled, or completed.

## Locked deterministic reference responses

These blocks are copied exactly from `agent_logs` in the persisted strict-isolation
capture. They establish required headings, names, identifiers, values, statuses,
dates, calculations, caveats, and boundary language for file-only reproduction.

### `RCR-01` — `return_processing`

- Persona: **Customer Service Agent**
- Prompt: As Customer Service Agent, summarize the anonymous return review evidence and approval boundary.
- Exact arguments: `{"return_id":"RET-4001"}`

```markdown
[returns-complaints-resolution-agent] **Prepared for:** Customer Service Agent
**Role focus:** empathetic review summaries and clear human-approval next steps

> Synthetic case data. Decision support and draft language only; no return, refund, credit, replacement, shipment, reservation, account change, or customer message is approved, created, or sent.

# Draft Return Review Queue

| Return ID | Synthetic Case | Product | Reason | Condition | Days | Status |
|-----------|----------|---------|--------|-----------|------|--------|
| RET-4001 | Synthetic size-mismatch case | Classic Denim Jacket | wrong size | unworn tags attached | 18 | pending review |
| RET-4002 | Synthetic device-defect case | Smart Fitness Tracker | defective | non functional | 50 | policy match candidate |
| RET-4003 | Synthetic description-mismatch case | Premium Running Shoes | not as described | lightly used | 10 | pending review |
| RET-4004 | Synthetic changed-mind case | Wireless Earbuds Pro | changed mind | opened unused | 11 | pending review |
| RET-4005 | Synthetic warranty-escalation case | Leather Crossbody Bag | defective | damaged | 91 | escalated |
| RET-4006 | Synthetic wrong-item case | UV Protection Sunglasses | wrong item | unopened | 10 | policy match candidate |

### RET-4001 — Classic Denim Jacket

- **Order:** ORD-88712
- **Case:** Synthetic size-mismatch case
- **Purchase Date:** 2026-02-14 | **Request Date:** 2026-03-02
- **Channel:** online
- **Price:** $89.99
- **Notes:** Ordered size M, needs size L. Willing to exchange.

### RET-4002 — Smart Fitness Tracker

- **Order:** ORD-89234
- **Case:** Synthetic device-defect case
- **Purchase Date:** 2026-01-20 | **Request Date:** 2026-03-10
- **Channel:** in_store
- **Price:** $129.99
- **Notes:** Heart rate sensor stopped working after 3 weeks. Under warranty.

### RET-4003 — Premium Running Shoes

- **Order:** ORD-87455
- **Case:** Synthetic description-mismatch case
- **Purchase Date:** 2026-02-28 | **Request Date:** 2026-03-08
- **Channel:** online
- **Price:** $149.99
- **Notes:** Color shown online was navy but received was dark grey.

### RET-4004 — Wireless Earbuds Pro

- **Order:** ORD-90100
- **Case:** Synthetic changed-mind case
- **Purchase Date:** 2026-03-01 | **Request Date:** 2026-03-12
- **Channel:** online
- **Price:** $59.99
- **Notes:** Found a better deal elsewhere. Wants full refund.

### RET-4005 — Leather Crossbody Bag

- **Order:** ORD-86321
- **Case:** Synthetic warranty-escalation case
- **Purchase Date:** 2025-12-18 | **Request Date:** 2026-03-14
- **Channel:** in_store
- **Price:** $79.99
- **Notes:** Strap broke after normal use. Outside 60-day window but claims manufacturing defect.

### RET-4006 — UV Protection Sunglasses

- **Order:** ORD-91005
- **Case:** Synthetic wrong-item case
- **Purchase Date:** 2026-03-05 | **Request Date:** 2026-03-15
- **Channel:** online
- **Price:** $44.99
- **Notes:** Received aviator style instead of ordered wayfarer style.

**Pending Reviews:** 3 | **Queue Value:** $554.94
```

### `RCR-02` — `complaint_classification`

- Persona: **Customer Service Agent**
- Prompt: As Customer Service Agent, classify this product concern without echoing personal information or sending a response.
- Exact arguments: `{"complaint_text":"The synthetic item stopped working after a week."}`

```markdown
[returns-complaints-resolution-agent] **Prepared for:** Customer Service Agent
**Role focus:** empathetic review summaries and clear human-approval next steps

> Synthetic case data. Decision support and draft language only; no return, refund, credit, replacement, shipment, reservation, account change, or customer message is approved, created, or sent.

# Draft Complaint Classification

**Classified As:** Service Experience (`service_experience`)
**Severity Weight:** 0.6
**Avg Resolution Time:** 48h
**Escalation Rate:** 22%

## Complaint Category Reference

| Category | Monthly Volume | Severity | Avg Resolution | Escalation Rate |
|----------|---------------|----------|----------------|-----------------|
| Product Quality | 142 | 0.85 | 36h | 15% |
| Order Fulfillment | 98 | 0.70 | 24h | 8% |
| Pricing & Billing | 67 | 0.65 | 18h | 5% |
| Service Experience | 53 | 0.60 | 48h | 22% |

**Total Monthly Complaints:** 360
```

### `RCR-03` — `resolution_recommendation`

- Persona: **Customer Service Agent**
- Prompt: As Customer Service Agent, draft a policy-grounded option and keep all actions behind authorization.
- Exact arguments: `{"return_id":"RET-4001"}`

```markdown
[returns-complaints-resolution-agent] **Prepared for:** Customer Service Agent
**Role focus:** empathetic review summaries and clear human-approval next steps

> Synthetic case data. Decision support and draft language only; no return, refund, credit, replacement, shipment, reservation, account change, or customer message is approved, created, or sent.

# Draft Resolution Options

## RET-4001 — Synthetic size-mismatch case

- **Product:** Classic Denim Jacket ($89.99)
- **Reason:** wrong size
- **Option for authorized review:** Product Exchange
- **Cost Impact:** medium | **CSAT Impact:** very_high

**Review Steps:**
  1. Review the requested replacement and verify availability separately
  2. Draft exchange eligibility for authorized approval
  3. List logistics considerations without creating shipments
  4. Draft tracking-language requirements without sending a message
  5. State that no exchange or reservation is performed

## RET-4003 — Synthetic description-mismatch case

- **Product:** Premium Running Shoes ($149.99)
- **Reason:** not as described
- **Option for authorized review:** Partial Refund
- **Cost Impact:** medium | **CSAT Impact:** moderate

**Review Steps:**
  1. Review item-condition evidence and model a policy range
  2. Identify any disclosed fee rule for authorized review
  3. Draft a partial-refund option without processing funds
  4. Draft timeline language without notifying a customer

## RET-4004 — Synthetic changed-mind case

- **Product:** Wireless Earbuds Pro ($59.99)
- **Reason:** changed mind
- **Option for authorized review:** Store Credit
- **Cost Impact:** low | **CSAT Impact:** moderate

**Review Steps:**
  1. Review whether the condition appears to meet the synthetic policy
  2. Draft a store-credit option without issuing value or a bonus
  3. Require authorized review before any loyalty-account change
  4. Draft disclosure language without sending a message

## Available Resolution Playbooks

- **Full Refund** (`full_refund`): Window 90d, Cost: high, CSAT: high
- **Product Exchange** (`exchange`): Window 60d, Cost: medium, CSAT: very_high
- **Store Credit** (`store_credit`): Window 45d, Cost: low, CSAT: moderate
- **Warranty Replacement** (`warranty_replacement`): Window 365d, Cost: medium, CSAT: high
- **Partial Refund** (`partial_refund`): Window 30d, Cost: medium, CSAT: moderate
```

### `RCR-04` — `trend_analysis`

- Persona: **Quality Team**
- Prompt: As Quality Team, summarize aggregate defect and return patterns without accusing any person.
- Exact arguments: `{}`

```markdown
[returns-complaints-resolution-agent] **Prepared for:** Quality Team
**Role focus:** aggregate defect patterns and product-quality evidence

> Synthetic case data. Decision support and draft language only; no return, refund, credit, replacement, shipment, reservation, account change, or customer message is approved, created, or sent.

# Synthetic Returns & Complaints Trend Analysis

**Overall Trend:** STABLE

## Monthly Returns Overview

| Month | Total Returns | Return Rate | Avg Resolution | CSAT | Refund Total |
|-------|--------------|-------------|----------------|------|--------------|
| 2025-10 | 312 | 4.1% | 28.5h | 4.1/5.0 | $18,720.00 |
| 2025-11 | 345 | 4.5% | 30.2h | 4.0/5.0 | $21,450.00 |
| 2025-12 | 498 | 6.2% | 38.7h | 3.6/5.0 | $34,200.00 |
| 2026-01 | 387 | 5.0% | 32.1h | 3.9/5.0 | $24,800.00 |
| 2026-02 | 328 | 4.3% | 27.8h | 4.2/5.0 | $19,650.00 |
| 2026-03 | 360 | 4.7% | 29.4h | 4.1/5.0 | $22,100.00 |

## Return Reasons Breakdown (Last 6 Months)

- **Wrong Size:** 715 total, 119.2 avg/month
- **Defective:** 466 total, 77.7 avg/month
- **Changed Mind:** 511 total, 85.2 avg/month
- **Not As Described:** 320 total, 53.3 avg/month
- **Wrong Item:** 218 total, 36.3 avg/month

**Total Refunded (6 months):** $140,920.00

## Key Insights

- Holiday season (Dec) drove a 44% spike in returns, primarily changed-mind returns
- Wrong-size returns consistently highest — consider enhanced size guide implementation
- Resolution time improved 8% over the period despite volume increases
- CSAT recovered to 4.1 after post-holiday dip to 3.6
```
