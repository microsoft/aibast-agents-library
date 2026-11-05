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

## Account health values

Account health comes from the fixed CRM fields in the records file; nothing is recalculated:

- Health score: 78/100
- Feature adoption: 67%
- CSAT: 4.2/5
- Touchpoints in the last 30 days: 30
- Renewal risk: 5%
- Win probability (CRM opportunity): 68%
- Close target: 21 days

Money is shown in short form: `$2,800,000,000` -> `$2.8B`, `$1,200,000` -> `$1.2M`, `$2,400,000` -> `$2.4M`.

### Account Overview evidence contract

The Acme response must be able to state:

- **Account Overview: Acme Corporation** (intelligence briefing)
- Revenue: $2.8B
- Current spend: $1.2M/year
- Opportunity: $2.4M expansion
- Health Score: 78/100
- Industry: Manufacturing (12,400 employees, HQ Chicago, IL)
- **Account Health Score: 78/100**
- Key Signals: New CTO hired 6 weeks ago (opportunity); CEO mentioned digital transformation; 67% feature adoption, 4.2/5 CSAT
- All three fixed recent-activity headlines and ages
- Next step offered: want to see the stakeholder map?

## Stakeholder output contract

Emit all eight stakeholder records with Name, Role, Influence, Influence Score and Status, in record order.

The headline is computed:

- `8 stakeholders mapped.` (count of records)
- `Champion strong` when a Champion with Positive sentiment exists (James Miller)
- `need CFO alignment.` when the Economic Buyer is not Positive (Lisa Park, Neutral)

Relationship Gaps are the stakeholders' recorded gap notes, in record order:

- CTO controls tech budget (no relationship)
- CFO wants business case

Action: `Get CTO intro through James before meeting` (the stakeholder whose status is `Need intro`, introduced
through the Champion).

The response must include **Stakeholder Map**, **Relationship Gaps** and the **Influence** column. Next step offered:
want competitive positioning?

## Competitive output contract

Headline: `Two competitors active. You lead on fit, they're aggressive on price.` (a competitor priced at a discount
makes the price clause appear.)

The exact comparison is:

| Factor | You | CompetitorA | CompetitorB |
| --- | --- | --- | --- |
| Product fit | 94% | 78% | 82% |
| Implementation | 8 weeks | 14 weeks | 10 weeks |
| Pricing | Market | 15% discount | 10% premium |

Your Advantages: ERP integration (3-week head start), champion relationship, manufacturing references.

Risk: `CompetitorA's discount may appeal to CFO`

Include the two exact competitor activity records. The response must include **Competitive Intelligence** and
**Competitor Activity**. Next step offered: prepare counter-positioning?

## Value messaging output contract

Return **Draft Meeting Talking Points (human review required)** — tailored talking points by stakeholder, in this
order (Decision Maker, Economic Buyer, Champion):

- **CTO Sarah:** API-first ERP integration, 3 CTO references available
- **CFO Lisa:** $4.2M savings over 3 years, 8-week vs 14-week implementation, 90-day risk-free pilot
- **Champion James:** Positions ops team as transformation leaders

The savings value is calculated as `$2,400,000 opportunity value * 1.75 = $4,200,000` (shown as $4.2M). The
competitor implementation figure is the longest competitor implementation (CompetitorA, 14 weeks).

### Objection Handling

- Price: `TCO is 23% lower with implementation/support`
- Risk: `47 similar deployments, 94% success rate` (synthetic reference set; validate approved references before use)

These are synthetic draft statements, not validated customer claims. The response must include **Draft Meeting
Talking Points** and **Objection Handling**. Next step offered: want the deal risk assessment?

## Risk output contract

Headline: **Deal Risk Assessment: Acme Corporation** — 4 risks identified, 2 need action before tomorrow (High
severity counts as needing action).

| Risk | Severity | Mitigation |
| --- | --- | --- |
| No CTO relationship | High | Champion intro today |
| Competitor pricing | High | TCO analysis ready |
| Budget timing | Medium | Q1 confirmed |
| CFO business case | Medium | ROI calculator drafted |

**Immediate Actions (before the meeting):**

1. Call James for CTO intro
2. Send CFO ROI calculator

These are the seller's to-dos; the agent does not call, send or schedule anything.

Required evidence:

- **Win probability:** 68% | **Close target:** 21 days
- **Opportunity Value:** $2.4M
- Next step offered: generate the briefing document?

## Executive briefing output contract

The briefing must include:

- **Account Intelligence Briefing: Acme Corporation** — briefing complete.
- Deal value: $2.4M
- Win probability: 68%
- Stakeholders: 8 mapped
- Risks: 4 (2 critical)
- **Pre-Meeting Checklist**: Call James for CTO intro; Send CFO ROI calculator; Review competitor counter-strategy
- Closing line: You're prepared with full account intelligence, stakeholder insights, and competitive positioning.

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
