# Account Intelligence Agent — Deterministic Rules and Acme Output Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the uploaded Acme record file and these rules. Do not browse, enrich, infer missing facts, or substitute another account.

## Deterministic routing

| Operation | Use when the user asks for | Required response anchors |
| --- | --- | --- |
| `account_overview` | Firmographics, health, adoption, spend, opportunity, or recent activity | `Account Overview`; `Account Health Score` |
| `stakeholder_map` | Buying committee, influence, champions, introductions, or relationship gaps | `Stakeholder Map`; `Relationship Gaps` |
| `competitive_intel` | Competitor activity, comparisons, differentiation, or positioning | `Competitive Intelligence`; `Competitor Activity` |
| `value_messaging` | Persona-specific talking points, conversation hooks, meeting messaging, or objection handling | `Draft Meeting Talking Points`; `Objection Handling` |
| `risk_assessment` | Deal risks, severity, mitigation options, or win-probability indicator | `Deal Risk Assessment`; `Immediate Actions` |
| `executive_briefing` | Compiled account briefing, opportunity summary, or pre-meeting checklist | `Account Intelligence Briefing`; `Pre-Meeting Checklist` |

`value_messaging` and `executive_briefing` are not interchangeable. Talking-point and objection requests must use `value_messaging`.

## Health calculation

Use the source formulas exactly:

- `total_meetings = sum(stakeholder meetings)` = 30
- `positive_ratio = positive stakeholders / all stakeholders` = 3 / 8
- `product_depth = products owned / 3` = 2 / 3
- `engagement = min(100, int(total_meetings * 3.5))` = 100
- `adoption = int(product_depth * 100)` = 66
- `sentiment_score = int(positive_ratio * 100)` = 37
- `renewal_risk_pct = max(5, 50 - total_meetings * 2 - int(positive_ratio * 30))` = 5
- `overall = int(engagement * 0.3 + adoption * 0.2 + sentiment_score * 0.3 + (100 - renewal_risk_pct) * 0.2)` = 73
- `touchpoints_30d = total_meetings` = 30
- `csat = round(3.0 + positive_ratio * 2, 1)` = 3.8

### Account Overview evidence contract

The Acme response must be able to state:

- **Account Overview: Acme Corporation**
- Industry: Manufacturing
- Revenue: $2,800,000,000
- Employees: 12,400 globally
- HQ: Chicago, IL
- Current spend: $1,200,000/year
- Opportunity: $2,400,000 expansion
- **Account Health Score: 73/100**
- Engagement: 100% (30 touchpoints last 30 days)
- Product adoption: 66% feature utilization
- Support sentiment: 3.8/5 CSAT
- Renewal risk: 5%
- All three fixed recent-activity headlines and ages

## Stakeholder calculation and output contract

Emit all eight stakeholder records exactly as recorded. Engagement is rendered as `<meetings> meetings` when meetings are greater than zero; otherwise render `Schedule intro`.

The source relationship-gap rule selects a stakeholder only when:

- meetings equal 0; and
- influence is `Decision Maker`, `Economic Buyer`, or `Executive Sponsor`.

For Acme this yields:

- Sarah Chen (CTO): New hire from AWS, 6 weeks ago. Controls tech budget.
- Tom Bradley (CEO): Mentioned digital transformation in earnings call.

The positive champion rule yields:

- James Miller — Promoted to VP last quarter. Advocated for 3 vendor decisions.

The response must include **Stakeholder Map** and **Relationship Gaps**.

## Competitive output contract

The exact comparison is:

| Factor | You | CompetitorA | CompetitorB |
| --- | --- | --- | --- |
| Relationship depth | Strong | Medium | Weak |
| Product fit | 94% | 78% | 82% |
| Pricing | Market rate | -15% below market | +10% above market |
| Implementation | 8 weeks | 14 weeks | 10 weeks |

Include the two exact competitor activity records, all three synthetic advantages, and the risk alert:

`CompetitorA's discount may appeal to economic buyer.`

The response must include **Competitive Intelligence** and **Competitor Activity**.

## Value messaging output contract

Return **Draft Meeting Talking Points (human review required)** for these exact synthetic stakeholders:

### Sarah Chen — CTO — Tech Vision

- `Platform aligns with digital transformation roadmap`
- `API-first architecture integrates with existing systems`
- `3 Manufacturing CTO references available for peer conversation`

### James Miller — VP Operations — Internal Positioning

- `Positions your team as transformation leaders`
- `Executive visibility on project success metrics`
- `Co-innovation partnership opportunity`

### Lisa Park — CFO — ROI

The savings value is calculated as:

`$2,400,000 opportunity value * 1.75 = $4,200,000`

Use these exact points:

- `$4,200,000 projected savings over 3 years`
- `8-week implementation vs competitor's longer timeline`
- `Risk-free pilot: 90-day proof of value before full commitment`

### Objection Handling

- Price concern: `Total cost of ownership is 23% lower when factoring implementation and support`
- Risk concern: `The synthetic reference set includes comparable examples; validate approved references and outcomes before use`

These are synthetic draft statements, not validated customer claims. The response must include **Draft Meeting Talking Points** and **Objection Handling**.

## Risk calculation and output contract

The source emits these exact synthetic risks:

| Risk | Severity | Mitigation label | Owner label |
| --- | --- | --- | --- |
| No relationship with CTO (Sarah Chen) | High | Champion intro this week | You |
| CompetitorA pricing pressure (-15% below market) | High | TCO analysis showing lower total cost | You |
| CFO needs ROI validation | Medium | Send customized ROI calculator | Finance |

`Send customized ROI calculator` is preserved as an exact source label only. It is a draft option and does not authorize sending anything.

The synthetic win-probability indicator is calculated as:

`min(95, max(20, 50 + 1 positive champion * 15 - 2 high blockers * 10 + 8 stakeholders * 2)) = 61`

Required evidence:

- **Deal Risk Assessment: Acme Corporation**
- **Synthetic Win-Probability Indicator: 61%**
- **Opportunity Value: $2,400,000**
- **Immediate Actions** containing the two high-severity mitigation labels

## Executive briefing output contract

The briefing must include:

- **Account Intelligence Briefing: Acme Corporation**
- Deal value: $2,400,000 (expansion from $1,200,000 current)
- Synthetic win-probability indicator: 61%
- Account health: 73/100
- Account health finding: 100% engagement, 66% adoption, 5% churn risk
- Stakeholders: 8 mapped, 3 need intro, 1 champion
- The briefing's three zero-meeting introductions are Sarah Chen, Maria Lopez, and Tom Bradley; this count is intentionally broader than the two-person `Relationship Gaps` rule.
- Competition: 2 active, you lead on fit/speed
- Risks: 3 identified, 2 critical
- **Pre-Meeting Checklist**
- Champion intro this week
- TCO analysis showing lower total cost

## Evidence-first response contract

1. Label the result as a synthetic Acme snapshot.
2. Cite the exact record fields used.
3. Separate recorded evidence from computed indicators.
4. Present messaging, risks, and next steps as drafts for review.
5. End with an evidence boundary stating that no CRM record, task, message, meeting, proposal, forecast, pricing, approval, or customer communication was created or changed.

## Failure and safety behavior

- Accept only the six listed operations and the allow-listed synthetic accounts.
- Never browse or use external CRM, news, social, meeting, email, competitive, or reference sources.
- Never invent a missing record or treat a synthetic claim as customer truth.
- Never send outreach, update CRM, create a task, schedule a meeting, change a forecast, approve pricing, deliver a proposal, or contact a customer.
- Require authorized account-owner review before any external use.
