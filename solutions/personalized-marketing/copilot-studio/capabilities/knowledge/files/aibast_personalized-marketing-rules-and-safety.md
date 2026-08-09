# Personalized Marketing — Exact Rules, Headings, and Safety

> **COPILOT STUDIO KNOWLEDGE CONTRACT.** Use this file with the companion
> complete synthetic-records file. The deterministic reference responses below
> are the exact tool evidence persisted for every locked case; do not replace
> them with generic summaries or invent missing values.

## Approved personas and language focus

| Persona | Required focus |
|---|---|
| Marketing Director | portfolio priorities, governance, and qualitative business value |
| Campaign Manager | review-ready campaign details, sequencing, and measurement |

## Exact routing and evidence contract

| Case | Route to operation | Persona | Exact arguments | Required transcript evidence |
|---|---|---|---|---|
| `PM-01` | `customer_segmentation` | Marketing Director | `{}` | `Prepared for:** Marketing Director`; `Total Addressable Customers`; `no audience is profiled with sensitive attributes` |
| `PM-02` | `campaign_design` | Campaign Manager | `{"campaign_id":"CAMP-WINBACK"}` | `Prepared for:** Campaign Manager`; `Draft Campaign Design Portfolio`; `Win-Back Journey` |
| `PM-03` | `content_personalization` | Campaign Manager | `{"segment_id":"SEG-NEW"}` | `Draft Content Personalization Matrix`; `New Explorers`; `Draft Hero Copy` |
| `PM-04` | `performance_analysis` | Marketing Director | `{}` | `Marketing Performance Analysis`; `A/B Test Results`; `Synthetic aggregate planning data` |

Routing rules:

- Match the user request to the operation shown above even when the operation name is not stated.
- Use only the exact argument identifiers in the companion records; never fabricate an ID.
- Keep the requested persona heading and the deterministic operation heading exactly as captured.
- When an argument is omitted in a locked case, follow the complete captured reference response below rather than asking for production data.
- If an unknown identifier is supplied, stop and request a valid synthetic identifier; do not approximate.

## Exact no-side-effect boundary

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

Never identify or sensitively profile a person; send or schedule outreach; create, apply, or promise an offer; enroll a member; issue a reward; alter a cart; or complete a purchase.

Every answer is a draft, scenario, informational summary, or recommendation for
authorized human review. Never claim an action was sent, scheduled, approved,
issued, reserved, processed, fulfilled, or completed.

## Locked deterministic reference responses

These blocks are copied exactly from `agent_logs` in the persisted strict-isolation
capture. They establish required headings, names, identifiers, values, statuses,
dates, calculations, caveats, and boundary language for file-only reproduction.

### `PM-01` — `customer_segmentation`

- Persona: **Marketing Director**
- Prompt: As Marketing Director, summarize the aggregate customer groups without demographic traits and identify portfolio review priorities.
- Exact arguments: `{}`

```markdown
[personalized-marketing-agent] **Prepared for:** Marketing Director
**Role focus:** portfolio priorities, governance, and qualitative business value

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Customer Segmentation Overview

**Total Addressable Customers:** 131,820
**Weighted Average LTV:** $6,966.55

| Segment | Size | Avg Spend | Orders/Yr | LTV | Churn Risk | Engagement |
|---------|------|-----------|-----------|-----|------------|------------|
| Loyal Advocates | 42,850 | $1,875.00 | 18.3 | $11,250.00 | 4% | 92/100 |
| At-Risk Churners | 18,420 | $620.00 | 5.1 | $3,720.00 | 38% | 31/100 |
| New Explorers | 27,600 | $340.00 | 3.8 | $2,040.00 | 22% | 58/100 |
| High-Engagement Members | 8,750 | $4,200.00 | 24.6 | $33,600.00 | 6% | 97/100 |
| Dormant Lapsed | 34,200 | $85.00 | 0.8 | $510.00 | 72% | 9/100 |

## Revenue Contribution by Segment

- **Loyal Advocates:** $80,343,750.00
- **At-Risk Churners:** $11,420,400.00
- **New Explorers:** $9,384,000.00
- **High-Engagement Members:** $36,750,000.00
- **Dormant Lapsed:** $2,907,000.00
```

### `PM-02` — `campaign_design`

- Persona: **Campaign Manager**
- Prompt: As Campaign Manager, outline the review-only win-back sequence, assumptions, and approval gates.
- Exact arguments: `{"campaign_id":"CAMP-WINBACK"}`

```markdown
[personalized-marketing-agent] **Prepared for:** Campaign Manager
**Role focus:** review-ready campaign details, sequencing, and measurement

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Draft Campaign Design Portfolio

## Win-Back Journey (`CAMP-WINBACK`)

- **Type:** automated_email
- **Target Segment:** Dormant Lapsed (SEG-DORMANT)
- **Audience Size:** 34,200
- **Duration:** 28 days, 4 stages
- **Offer Concept:** Optional incentive concept, subject to policy and approval
- **Illustrative Revenue Scenario:** $43,605.00

**Draft Sequence (not sent):**
  1. Draft A: Reconnect with recent category interests
  2. Draft B: Explore what is new
  3. Draft C: Optional value reminder
  4. Draft D: Close the sequence respectfully

**Historical Benchmarks:** Open 18% | Click 4% | Convert 1.2%

## Loyalty Tier Upgrade (`CAMP-LOYALTY`)

- **Type:** multi_channel
- **Target Segment:** Loyal Advocates (SEG-LOYAL)
- **Audience Size:** 42,850
- **Duration:** 14 days, 3 stages
- **Offer Concept:** Early-access concept; no benefit is issued
- **Illustrative Revenue Scenario:** $351,232.88

**Draft Sequence (not sent):**
  1. Draft A: Review progress toward the next tier
  2. Draft B: Explain an optional approved benefit
  3. Draft C: Acknowledge a verified tier change

**Historical Benchmarks:** Open 42% | Click 15% | Convert 8.0%

## New Customer Welcome (`CAMP-NEWWELCOME`)

- **Type:** automated_email
- **Target Segment:** New Explorers (SEG-NEW)
- **Audience Size:** 27,600
- **Duration:** 30 days, 5 stages
- **Offer Concept:** Welcome-value concept, subject to policy and approval
- **Illustrative Revenue Scenario:** $135,815.46

**Draft Sequence (not sent):**
  1. Draft A: Welcome and explain available categories
  2. Draft B: Introduce popular products
  3. Draft C: Offer optional curated ideas
  4. Draft D: Invite the shopper to set preferences
  5. Draft E: Explain the rewards program without enrollment

**Historical Benchmarks:** Open 35% | Click 11% | Convert 5.5%

## VIP Exclusive Preview (`CAMP-VIP`)

- **Type:** multi_channel
- **Target Segment:** High-Engagement Members (SEG-HIGHVAL)
- **Audience Size:** 8,750
- **Duration:** 7 days, 2 stages
- **Offer Concept:** Private-preview concept; no access or discount is granted
- **Illustrative Revenue Scenario:** $209,144.25

**Draft Sequence (not sent):**
  1. Draft A: Preview a collection for an eligible aggregate audience
  2. Draft B: Close the preview sequence without urgency pressure

**Historical Benchmarks:** Open 58% | Click 24% | Convert 14.0%
```

### `PM-03` — `content_personalization`

- Persona: **Campaign Manager**
- Prompt: As Campaign Manager, draft neutral content ideas for New Explorers and explain the non-sensitive signals used.
- Exact arguments: `{"segment_id":"SEG-NEW"}`

```markdown
[personalized-marketing-agent] Unknown segment_id `new_explorers`. Valid: SEG-LOYAL, SEG-ATRISK, SEG-NEW, SEG-HIGHVAL, SEG-DORMANT
[personalized-marketing-agent] Unknown segment_id `new_explorers`. Valid: SEG-LOYAL, SEG-ATRISK, SEG-NEW, SEG-HIGHVAL, SEG-DORMANT
[personalized-marketing-agent] **Prepared for:** Campaign Manager
**Role focus:** review-ready campaign details, sequencing, and measurement

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Draft Content Personalization Matrix

## New Explorers (`SEG-NEW`)

**Draft Hero Copy:**
- Headline: "Welcome to the Family"
- CTA: "Start Shopping"

**Draft Product Ideas:**
- Organic Cotton T-Shirt
- Stainless Water Bottle
- UV Protection Sunglasses

**Preferred Channels:** social_media, mobile_app
**Top Categories:** Apparel, Beauty, Accessories

[personalized-marketing-agent] **Prepared for:** Marketing Director
**Role focus:** portfolio priorities, governance, and qualitative business value

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Customer Segmentation Overview

**Total Addressable Customers:** 131,820
**Weighted Average LTV:** $6,966.55

| Segment | Size | Avg Spend | Orders/Yr | LTV | Churn Risk | Engagement |
|---------|------|-----------|-----------|-----|------------|------------|
| New Explorers | 27,600 | $340.00 | 3.8 | $2,040.00 | 22% | 58/100 |

## Revenue Contribution by Segment

- **New Explorers:** $9,384,000.00
```

### `PM-04` — `performance_analysis`

- Persona: **Marketing Director**
- Prompt: As Marketing Director, compare the synthetic tests and call out measurement limitations before any decision.
- Exact arguments: `{}`

```markdown
[personalized-marketing-agent] **Prepared for:** Marketing Director
**Role focus:** portfolio priorities, governance, and qualitative business value

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Marketing Performance Analysis

## A/B Test Results

| Test | Campaign | Winner | Confidence | Sample | Lift |
|------|----------|--------|------------|--------|------|
| ABT-001 | Win-Back Journey | Variant B | 94% | 8,500 | +30.5% |
| ABT-002 | Loyalty Tier Upgrade | Variant A | 91% | 6,200 | +14.4% |
| ABT-003 | VIP Exclusive Preview | Variant B | 88% | 3,400 | +15.3% |

## Campaign ROI Summary

| Campaign | Audience | Proj. Revenue | Conv. Rate | Est. ROAS |
|----------|----------|---------------|------------|-----------|
| Win-Back Journey | 34,200 | $43,605.00 | 1.2% | 3.64x |
| Loyalty Tier Upgrade | 42,850 | $351,232.88 | 8.0% | 23.42x |
| New Customer Welcome | 27,600 | $135,815.46 | 5.5% | 14.06x |
| VIP Exclusive Preview | 8,750 | $209,144.25 | 14.0% | 68.29x |

**Total Projected Campaign Revenue:** $739,797.59
```
