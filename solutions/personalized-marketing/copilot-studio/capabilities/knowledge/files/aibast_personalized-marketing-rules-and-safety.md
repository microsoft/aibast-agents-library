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
| `PM-02` | `campaign_design` | Campaign Manager | `{}` | `Prepared for:** Campaign Manager`; `Draft Campaign Design Portfolio`; `Total Campaign Projection` |
| `PM-03` | `content_personalization` | Campaign Manager | `{"segment_id":"SEG-VIP"}` | `Draft Content Personalization Matrix`; `VIP Shoppers`; `A/B Test Setup` |
| `PM-04` | `performance_analysis` | Marketing Director | `{}` | `Marketing Performance Analysis`; `A/B Test Results`; `Synthetic aggregate planning data` |
| `PM-05` | `campaign_workflow` | Campaign Manager | `{}` | `Draft VIP Launch Schedule`; `Hour 48`; `Nothing is scheduled or sent` |
| `PM-06` | `revenue_projection` | Marketing Director | `{}` | `VIP Revenue Projection Model`; `Conservative (Baseline)`; `ROI Range` |
| `PM-07` | `executive_brief` | Marketing Director | `{}` | `Executive Campaign Brief`; `Program Economics`; `has not been sent` |

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

I've analyzed your 240K active customers and identified 5 high-value segments for targeted holiday campaigns.

**Total Addressable Customers:** 240,000

| Segment | Size | Avg Order | Open Rate | Conversion |
|---------|------|-----------|-----------|------------|
| VIP Shoppers | 12,400 | $340 | 68% | 12.4% |
| Frequent Buyers | 38,200 | $185 | 52% | 9.6% |
| Seasonal Shoppers | 67,800 | $210 | 44% | 7.2% |
| Lapsed Customers | 84,300 | $165 | 28% | 3.1% |
| New Subscribers | 37,300 | $0 | 71% | 15.8% |

**Holiday Revenue Potential:**
- Total addressable: $8.4M across all segments
- Highest ROI: VIP Shoppers (12.4% conversion)
- Fastest growth: New Subscribers (15.8% conversion)

**Recommended Strategy:** Multi-wave campaign targeting VIPs first, then expanding to other segments.

Source: [CRM Analytics + Purchase History + Email Platform]

Next: want to see personalized campaign recommendations?
```

### `PM-02` — `campaign_design`

- Persona: **Campaign Manager**
- Prompt: As Campaign Manager, show me the personalized multi-wave campaign recommendations for the holiday promotion and the approval gates.
- Exact arguments: `{}`

```markdown
[personalized-marketing-agent] **Prepared for:** Campaign Manager
**Role focus:** review-ready campaign details, sequencing, and measurement

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Draft Campaign Design Portfolio

I've created 5 personalized campaign drafts optimized for each segment's behavior patterns.

**Campaign Recommendations:**

## Wave 1: VIP Shoppers (Launch Day)

- **Theme (proposed offer, not issued):** "Early Access - 30% Off Everything"
- **Personalization:** Past purchase categories featured
- **Audience:** 12,400 (12.4% conversion, $340 avg order)
- **Expected revenue:** $1.42M

## Wave 2: Frequent Buyers (Day 2)

- **Theme (proposed offer, not issued):** "Your Favorites Are On Sale"
- **Personalization:** AI-recommended products based on browsing
- **Audience:** 38,200 (9.6% conversion, $185 avg order)
- **Expected revenue:** $2.17M

## Wave 3: Seasonal Shoppers (Day 5)

- **Theme (proposed offer, not issued):** "Holiday Gifts - Free Shipping"
- **Personalization:** Gift guides by top category
- **Audience:** 67,800 (7.2% conversion, $210 avg order)
- **Expected revenue:** $1.98M

## Wave 4: New Subscribers (Day 7)

- **Theme (proposed offer, not issued):** "Welcome Gift - 40% Off First Purchase"
- **Personalization:** Signup-preference categories
- **Audience:** 37,300 (15.8% conversion, $0 avg order)
- **Expected revenue:** $1.24M

## Wave 5: Lapsed Customers (Day 10)

- **Theme (proposed offer, not issued):** "We Saved You a Gift - Free Shipping"
- **Personalization:** Last purchased category
- **Audience:** 84,300 (3.1% conversion, $165 avg order)
- **Expected revenue:** $1.31M

**Total Campaign Projection:** $8.12M revenue from $47K campaign investment

Source: [Predictive Analytics + Historical Performance]

Next: generate the VIP campaign creative?
```

### `PM-03` — `content_personalization`

- Persona: **Campaign Manager**
- Prompt: As Campaign Manager, generate the VIP campaign with personalized content and A/B test variants.
- Exact arguments: `{"segment_id":"SEG-VIP"}`

```markdown
[personalized-marketing-agent] **Prepared for:** Campaign Manager
**Role focus:** review-ready campaign details, sequencing, and measurement

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Draft Content Personalization Matrix

VIP campaign creative drafted with 3 A/B test variants optimized for engagement.

**Campaign:** "Early Access VIP - 30% Off Everything"

## Variant A: Product Focus

- Hero image: Best-selling items from the customer's purchase history
- Subject line: "{FirstName}, Your Favorites Are 30% Off (VIP Early Access)"
- CTA: "Shop My Picks"

## Variant B: Urgency Focus

- Hero image: Countdown timer + exclusive badge
- Subject line: "24-Hour VIP Access Starts Now - 30% Off"
- CTA: "Activate My VIP Access"

## Variant C: Rewards Focus

- Hero image: Double points badge + tier benefits
- Subject line: "Earn 3X Points + 30% Off (VIP Exclusive)"
- CTA: "Claim VIP Rewards"

Preview of Variant A for a sample VIP: "Sarah, Your Favorites Are 30% Off (VIP Early Access)"

**A/B Test Setup:**
- Split: 33% / 33% / 34%
- Duration: 12 hours
- Winner auto-selected by open rate + revenue

## VIP Shoppers (`SEG-VIP`)

**Draft Hero Copy:**
- Headline: "VIP Early Access - 30% Off Everything"
- CTA: "Shop My Picks"

**Draft Product Ideas:**
- Limited Edition Blazer
- Designer Handbag
- Artisan Watch

**Top Categories:** Premium Apparel, Footwear, Accessories

Source: [Creative Engine + Testing Framework]

Next: schedule the campaign launch?
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
| ABT-001 | Last year's VIP early access | Variant B | 94% | 11,800 | +15.3% |
| ABT-002 | Last year's frequent-buyer sale | Variant A | 91% | 36,000 | +14.4% |
| ABT-003 | Generic vs personalized holiday email | Variant B | 88% | 24,000 | +15.8% |

## Benchmarks Used for the Holiday Plan

| Segment | Open Rate | Conversion | Avg Order |
|---------|-----------|------------|-----------|
| VIP Shoppers | 68% | 12.4% | $340 |
| Frequent Buyers | 52% | 9.6% | $185 |
| Seasonal Shoppers | 44% | 7.2% | $210 |
| Lapsed Customers | 28% | 3.1% | $165 |
| New Subscribers | 71% | 15.8% | $0 |

**Personalization benchmark:** 15.8% higher conversion than generic campaigns (synthetic benchmark).

Measurement limitation: past tests are synthetic samples; confirm significance before any decision.
```

### `PM-05` — `campaign_workflow`

- Persona: **Campaign Manager**
- Prompt: As Campaign Manager, plan the VIP wave launch for tomorrow morning and show me the automation workflow for approval.
- Exact arguments: `{}`

```markdown
[personalized-marketing-agent] **Prepared for:** Campaign Manager
**Role focus:** review-ready campaign details, sequencing, and measurement

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Draft VIP Launch Schedule and Automation Workflow

VIP wave draft scheduled for tomorrow 8:00 AM with the full automation workflow, ready for you to approve. Nothing is scheduled or sent until you approve it in the marketing platform.

**Scheduled Campaign (draft):**
- Launch: Tomorrow 8:00 AM PST
- Audience: 12,400 VIP customers
- A/B Test: 3 variants (33/33/34 split)
- Winner Selection: Auto-select at 8:00 PM (12 hours)
- Follow-up: 48-hour reminder if no purchase

**Automation Workflow:**

| Hour | Step |
|------|------|
| Hour 0 | Initial send with variant testing |
| Hour 12 | Winner declared, send winning variant to remaining audience |
| Hour 24 | Browse abandonment email (personalized products) |
| Hour 48 | Cart abandonment email (10% additional discount) |
| Hour 72 | Final call email (last chance messaging) |

**Performance Tracking:**
- Real-time dashboard monitoring open/click/revenue
- Milestone alerts to the campaign channel
- Optimization recommendations based on early performance

Source: [Marketing Automation + Campaign Scheduler]

Next: want to see the revenue projection breakdown?
```

### `PM-06` — `revenue_projection`

- Persona: **Marketing Director**
- Prompt: As Marketing Director, break down the revenue projection scenarios for the VIP wave.
- Exact arguments: `{}`

```markdown
[personalized-marketing-agent] **Prepared for:** Marketing Director
**Role focus:** portfolio priorities, governance, and qualitative business value

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# VIP Revenue Projection Model

Revenue projections show $1.42M baseline with $2.11M upside if we beat benchmarks (VIP wave, 12,400 customers).

## Conservative (Baseline)

- Open rate: 68% (8,432 opens)
- Click rate: 24% (2,024 clicks)
- Conversion: 12.4% (251 launch-email orders)
- Avg order: $340
- Revenue (season model): $1.42M

## Expected (Hit Benchmarks)

- Open rate: 72% (8,928 opens)
- Click rate: 28% (2,500 clicks)
- Conversion: 14.2% (355 launch-email orders)
- Avg order: $380 (upsell success)
- Revenue (season model): $1.78M

## Optimistic (Beat Benchmarks)

- Open rate: 78% (9,672 opens)
- Click rate: 32% (3,095 clicks)
- Conversion: 16.8% (520 launch-email orders)
- Avg order: $420 (premium mix)
- Revenue (season model): $2.11M

**Campaign Investment:** $47K (creative + platform + labor)
**ROI Range:** 30:1 (baseline) to 45:1 (optimistic)

Scenarios are planning estimates, not forecasts or committed results.

Source: [Predictive Models + Historical Data]

Next: generate the executive campaign brief?
```

### `PM-07` — `executive_brief`

- Persona: **Marketing Director**
- Prompt: As Marketing Director, create the executive brief summarizing our holiday campaign strategy.
- Exact arguments: `{}`

```markdown
[personalized-marketing-agent] **Prepared for:** Marketing Director
**Role focus:** portfolio priorities, governance, and qualitative business value

> Synthetic aggregate planning data. Drafts and recommendations only; no audience is profiled with sensitive attributes, and no message, offer, campaign, reward, or purchase is created or sent.

# Executive Campaign Brief

Executive brief prepared. Here's the complete holiday promotion strategy:

**Campaign Strategy Summary:**
- Segment analysis - 240K customers > 5 targeted segments, $8.4M revenue potential
- Multi-wave plan - 5 waves over 10 days, prioritizing VIPs (12.4% conversion)
- Creative development - 3 A/B test variants with personalization
- Automation built - 72-hour nurture workflow with browse/cart abandonment
- Revenue modeling - $1.42M baseline to $2.11M optimistic ($1.78M expected)
- Launch ready for approval - Tomorrow 8:00 AM, 12,400 VIP customers

**Program Economics:**
- Total investment: $47K
- Expected total revenue: $8.12M (all waves)
- Program ROI: 173:1
- VIP wave alone: 30-45:1 ROI

**Competitive Advantage:** Personalization creates 15.8% higher conversion vs generic campaigns (synthetic benchmark).

The brief is a draft you can share with stakeholders (for example in Microsoft Teams); it has not been sent.

Source: [All Connected Systems]
```
