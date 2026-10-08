# Account Intelligence Agent — Fixed Synthetic Acme Snapshot

> **SYNTHETIC DEMO DATA.** This file is the complete fixed evidence snapshot for the six locked Acme Corporation cases. It contains no live customer, CRM, news, social, meeting, or competitive data. Do not browse, enrich, substitute, or invent records.

## Source and scope

- Portable source: `account_intelligence_agent.py`
- Account key: `acme` (the demo account and the default when no account is named)
- Account ID: `acc-001`
- Account name: `Acme Corporation`
- Supported evidence source: this uploaded snapshot only

If a requested fact is not recorded below, state that it is absent from the fixed synthetic snapshot.
Name matching: an account key, the full account name or part of it selects an account; a name that matches
no account returns "Unknown `account_name`" and never falls back to another account.

## Account record

| Field | Exact synthetic value |
| --- | --- |
| Industry | Manufacturing |
| Revenue | $2,800,000,000 (shown as $2.8B) |
| Employees | 12,400 |
| Headquarters | Chicago, IL |
| Current spend | $1,200,000 per year (shown as $1.2M/year) |
| Opportunity value | $2,400,000 expansion (shown as $2.4M expansion) |
| Products owned | Platform Core; Analytics Module |
| Contract renewal | 8 months |
| CRM health score | 78/100 |
| Feature adoption | 67% |
| CSAT | 4.2/5 |
| Touchpoints in the last 30 days | 30 |
| Renewal risk | 5% |
| Win probability (CRM opportunity) | 68% |
| Close target | 21 days |

## Key signals

- New CTO hired 6 weeks ago (opportunity)
- CEO mentioned digital transformation
- 67% feature adoption, 4.2/5 CSAT

## Recent activity

| Headline | Age |
| --- | --- |
| CEO mentioned digital transformation in Q3 earnings call | 12 days ago |
| New CTO Sarah Chen hired 6 weeks ago | 42 days ago |
| Competitor RFP issued for operations platform | 30 days ago |

These are fixed fictional headlines. They are not current news and must not be refreshed through browsing.

## Acme stakeholder map (8 stakeholders mapped)

| Name | Role | Influence | Influence score | Status | Meetings | Relationship gap | Exact synthetic notes |
| --- | --- | --- | ---: | --- | ---: | --- | --- |
| Sarah Chen | CTO (New) | Decision Maker | 95 | Need intro | 0 | CTO controls tech budget (no relationship) | New CTO, hired 6 weeks ago. Controls tech budget. |
| James Miller | VP Operations | Champion | 85 | Champion | 14 | — | Promoted to VP last quarter. Advocated for 3 vendor decisions. |
| Lisa Park | CFO | Economic Buyer | 90 | Needs ROI | 2 | CFO wants business case | Requested business case and ROI validation. |
| David Wong | IT Director | Influencer | 70 | Positive | 8 | — | Technical evaluator. Likes our API-first approach. |
| Rachel Torres | Procurement | Gatekeeper | 50 | Neutral | 1 | — | Standard procurement process, 4-6 week cycle. |
| Kevin Park | VP Engineering | Influencer | 60 | Positive | 5 | — | Attended 2 product demos. |
| Maria Lopez | Director of Strategy | Influencer | 40 | No contact | 0 | — | No contact yet. |
| Tom Bradley | CEO | Executive Sponsor | 80 | Aware | 0 | — | Mentioned digital transformation in earnings call. |

### Deterministic stakeholder anchors

- Stakeholders mapped: 8. Headline: `8 stakeholders mapped. Champion strong, need CFO alignment.`
- Positive champion: James Miller
- Relationship Gaps: CTO controls tech budget (no relationship), CFO wants business case
- Action: Get CTO intro through James before meeting

## Competitor records (two competitors active)

| Competitor | Relationship | Product fit | Pricing | Implementation | Exact synthetic activity |
| --- | --- | ---: | --- | --- | --- |
| CompetitorA | Medium | 78% | 15% discount | 14 weeks | On-site demo last week, aggressive discount offered |
| CompetitorB | Weak | 82% | 10% premium | 10 weeks | Early conversations only, no formal proposal |

## Our synthetic comparison profile

| Factor | Exact synthetic value |
| --- | --- |
| Relationship | Strong |
| Product fit | 94% |
| Pricing | Market |
| Implementation | 8 weeks |
| TCO versus competitor | 23% lower with implementation/support |
| Reference deployments | 47 similar deployments, 94% success rate (synthetic reference set) |

### Exact synthetic advantages

1. ERP integration (3-week head start)
2. champion relationship
3. manufacturing references

### Deterministic competitive anchor

`Two competitors active. You lead on fit, they're aggressive on price.` Risk: `CompetitorA's discount may appeal to CFO`.

## Deal risks (4 risks identified, 2 need action before tomorrow)

| Risk | Severity | Mitigation | Seller action before the meeting |
| --- | --- | --- | --- |
| No CTO relationship | High | Champion intro today | Call James for CTO intro |
| Competitor pricing | High | TCO analysis ready | Send CFO ROI calculator |
| Budget timing | Medium | Q1 confirmed | — |
| CFO business case | Medium | ROI calculator drafted | — |

The demo video's table shows the first three rows; the fourth (CFO business case) completes the stated count of four.
"Send CFO ROI calculator" is the seller's own to-do; the agent sends nothing.

## Pre-meeting checklist

- Call James for CTO intro
- Send CFO ROI calculator
- Review competitor counter-strategy

## Locked-case evidence contract

| Case | Operation | Locked prompt | Required evidence |
| --- | --- | --- | --- |
| AI-01 | account_overview | Prepare a synthetic Acme Corporation account overview and show the evidence that deserves seller attention. | Account Overview; Account Health Score; Evidence boundary |
| AI-02 | stakeholder_map | Map the synthetic Acme buying committee and show the relationship gaps without creating outreach tasks. | Stakeholder Map; Relationship Gaps; Evidence boundary |
| AI-03 | competitive_intel | Compare the synthetic competitor signals and positioning considerations for Acme Corporation. | Competitive Intelligence; Competitor Activity; Evidence boundary |
| AI-04 | value_messaging | Draft persona-specific talking points for the synthetic Acme meeting; do not send messages. | Draft Meeting Talking Points; Objection Handling; Evidence boundary |
| AI-05 | risk_assessment | Assess the synthetic Acme deal risks and mitigation options without changing a forecast or CRM record. | Deal Risk Assessment; Immediate Actions; Evidence boundary |
| AI-06 | executive_briefing | Prepare a concise synthetic Acme pre-meeting briefing and review checklist. | Account Intelligence Briefing; Pre-Meeting Checklist; Evidence boundary |

## Data-use boundary

Every name, company, event, meeting, value, percentage, score, sentiment, competitor statement, and relationship is synthetic. No CRM record, task, meeting, message, proposal, forecast, price, approval, or customer communication may be created or changed from this evidence.
