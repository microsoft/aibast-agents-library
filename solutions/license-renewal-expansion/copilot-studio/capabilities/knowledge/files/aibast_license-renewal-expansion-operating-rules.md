# License Renewal and Expansion Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `renewal_pipeline` | Review the bundled synthetic renewal pipeline, risk bands, and preparation checklist without changing CRM or forecast records. | `Renewal Pipeline`; `Draft Renewal Preparation Checklist`; `Evidence boundary` |
| `expansion_opportunities` | Identify synthetic demand signals and draft packaging options that still require authorized pricing review. | `Expansion Opportunities`; `Draft Packaging Options`; `Evidence boundary` |
| `churn_risk` | Which synthetic accounts show churn or competitor risk, and what switching-cost assumptions require validation? | `Churn Risk Assessment`; `Synthetic Switching-Cost Review`; `Evidence boundary` |
| `revenue_impact` | Compare the bundled synthetic renewal, expansion, and churn scenarios without making revenue commitments. | `Synthetic Revenue Scenario`; `Illustrative midpoint assumption`; `Evidence boundary` |
| `account_health` | GlobalBank license expires in 45 days. Currently 2,000 seats at $1M ARR. Usage shows they need 500 more seats. Competitor offering 30% discount. | `Account Analysis: GlobalBank`; `99.4%`; `Evidence boundary` |
| `competitive_defense` | Yes, show me the competitive defense strategy. | `Competitive Defense Strategy`; `~$500K`; `Evidence boundary` |
| `renewal_proposal` | Yes, build the renewal and expansion proposal. | `$787.5K/year`; `5.3x`; `Evidence boundary` |
| `executive_brief` | Yes, create the executive presentation with talking points. | `Draft Executive Presentation`; `Key Talking Points`; `Evidence boundary` |
| `negotiation_plan` | Yes, show me negotiation strategy and what approvals I need. | `Negotiation Boundaries`; `Approvals to Request`; `Evidence boundary` |
| `deal_summary` | Yes, send the proposal and summarize our renewal strategy. | `$2.36M`; `not sent`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

### `_days_until`

```python
def _days_until(date_text):
    import datetime
    start = datetime.date.fromisoformat(DEMO_AS_OF)
    return (datetime.date.fromisoformat(date_text) - start).days
```

### `_usage_pct`

```python
def _usage_pct(lic):
    """Seat usage to one decimal, rounded half up (1,987 of 2,000 -> 99.4)."""
    return ((lic["seats_used"] * 1000 + lic["seats"] // 2) // lic["seats"]) / 10
```

### `_money_k`

```python
def _money_k(value):
    return f"${value / 1000:,.1f}K".replace(".0K", "K")
```

### `_proposal`

```python
def _proposal(license_id="LIC-3000"):
    lic = LICENSE_AGREEMENTS[license_id]
    det = ACCOUNT_DETAILS[license_id]
    t = RENEWAL_TERMS
    list_price = lic["arr"] / lic["seats"]
    seat_price = round(list_price * (100 - t["matched_discount_pct"]) / 100)
    base = lic["seats"] * seat_price
    expansion = det["waitlist_users"] * seat_price
    seats = lic["seats"] + det["waitlist_users"]
    annual = base + expansion
    multi_year = round(annual * (100 - t["multi_year_discount_pct"]) / 100)
    list_value = seats * list_price
    return {
        "list_price": list_price, "seat_price": seat_price, "base": base, "expansion": expansion,
        "seats": seats, "annual": annual, "multi_year": multi_year, "tcv": multi_year * t["term_years"],
        "effective_discount_pct": round((list_value - multi_year) * 100 / list_value),
        "arr_change_pct": round((multi_year - lic["arr"]) * 100 / lic["arr"]),
        "seat_change_pct": round((seats - lic["seats"]) * 100 / lic["seats"]),
        "roi": round(det["documented_savings"] / multi_year, 1), "list_value": list_value,
    }
```

### `_license_items`

```python
def _license_items(license_id=None):
    if license_id:
        return [(license_id, LICENSE_AGREEMENTS[license_id])]
    return list(LICENSE_AGREEMENTS.items())
```

### `_renewal_pipeline`

```python
def _renewal_pipeline(license_id=None):
    pipeline = []
    for lid, lic in _license_items(license_id):
        risk = "low" if lic["health_score"] >= 70 else ("medium" if lic["health_score"] >= 50 else "high")
        pipeline.append({
            "id": lid, "customer": lic["customer"], "arr": lic["arr"],
            "renewal_date": lic["renewal_date"], "health_score": lic["health_score"],
            "risk": risk, "csm": lic["csm"],
        })
    pipeline.sort(key=lambda x: x["renewal_date"])
    total_arr = sum(p["arr"] for p in pipeline)
    at_risk_arr = sum(LICENSE_AGREEMENTS[p["id"]]["arr"] for p in pipeline if LICENSE_AGREEMENTS[p["id"]]["churn_signals"])
    return {"pipeline": pipeline, "total_arr": total_arr, "at_risk_arr": at_risk_arr}
```

### `_expansion_opportunities`

```python
def _expansion_opportunities(license_id=None):
    opps = []
    for lid, lic in _license_items(license_id):
        if not lic["expansion_signals"]:
            continue
        potential = 0
        items = []
        seat_util = round(lic["seats_used"] / lic["seats"] * 100, 1)
        if seat_util > 90:
            if lid in ACCOUNT_DETAILS:
                seat_rev = ACCOUNT_DETAILS[lid]["waitlist_users"] * _proposal(lid)["seat_price"]
            else:
                seat_rev = EXPANSION_PRICING["additional_seats"]["unit_price"] * 50
            potential += seat_rev
            items.append({"type": "additional_seats", "value": seat_rev})
        for signal in lic["expansion_signals"]:
            if "api" in signal.lower():
                potential += EXPANSION_PRICING["api_premium"]["price"]
                items.append({"type": "api_premium", "value": EXPANSION_PRICING["api_premium"]["price"]})
            if "analytics" in signal.lower():
                potential += EXPANSION_PRICING["analytics_addon"]["price"]
                items.append({"type": "analytics_addon", "value": EXPANSION_PRICING["analytics_addon"]["price"]})
            if "sso" in signal.lower():
                val = EXPANSION_PRICING["sso_subsidiary"]["price"] * 3
                potential += val
                items.append({"type": "sso_subsidiary", "value": val})
            if "integration" in signal.lower():
                potential += EXPANSION_PRICING["custom_integration"]["price"]
                items.append({"type": "custom_integration", "value": EXPANSION_PRICING["custom_integration"]["price"]})
        opps.append({
            "id": lid, "customer": lic["customer"], "current_arr": lic["arr"],
            "expansion_potential": potential, "items": items, "signals": lic["expansion_signals"],
        })
    opps.sort(key=lambda x: x["expansion_potential"], reverse=True)
    return {"opportunities": opps, "total_potential": sum(o["expansion_potential"] for o in opps)}
```

### `_churn_risk`

```python
def _churn_risk(license_id=None):
    risks = []
    for lid, lic in _license_items(license_id):
        if not lic["churn_signals"]:
            continue
        seat_util = round(lic["seats_used"] / lic["seats"] * 100, 1)
        risks.append({
            "id": lid, "customer": lic["customer"], "arr": lic["arr"],
            "health_score": lic["health_score"], "nps": lic["nps_score"],
            "seat_utilization": seat_util, "usage_trend": lic["usage_trend"],
            "signals": lic["churn_signals"], "tickets_90d": lic["support_tickets_90d"],
        })
    risks.sort(key=lambda x: x["health_score"])
    return {"at_risk": risks, "total_arr_at_risk": sum(r["arr"] for r in risks)}
```

### `_revenue_impact`

```python
def _revenue_impact(license_id=None):
    renewal = _renewal_pipeline(license_id)
    expansion = _expansion_opportunities(license_id)
    churn = _churn_risk(license_id)
    base_renewal = renewal["total_arr"]
    expansion_val = expansion["total_potential"]
    churn_val = churn["total_arr_at_risk"]
    best_case = base_renewal + expansion_val
    worst_case = base_renewal - churn_val
    expected = base_renewal + round(expansion_val * 0.4) - round(churn_val * 0.3)
    return {
        "base_renewal_arr": base_renewal, "expansion_potential": expansion_val,
        "churn_risk_arr": churn_val, "best_case": best_case,
        "worst_case": worst_case, "expected": expected,
    }
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### LRE-01 — `renewal_pipeline`

- Persona: Sales Leadership
- Locked prompt: Review the bundled synthetic renewal pipeline, risk bands, and preparation checklist without changing CRM or forecast records.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Renewal Pipeline

**Total Renewal ARR:** $1,966,000
**At-Risk ARR (accounts with churn signals):** $1,318,000

| Customer | ARR | Renewal Date | Health | Risk | CSM |
|----------|-----|-------------|--------|------|-----|
| Skyline Hospitality Group | $360,000 | 2026-04-15 | 94 | LOW | James Okafor |
| GlobalBank | $1,000,000 | 2026-04-30 | 87 | LOW | Dana Reeves |
| Pinnacle Insurance Corp | $288,000 | 2026-04-30 | 88 | LOW | Dana Reeves |
| ClearView Analytics | $72,000 | 2026-05-15 | 29 | HIGH | James Okafor |
| Redwood Supply Chain | $192,000 | 2026-06-01 | 62 | MEDIUM | Dana Reeves |
| Granite Construction Co | $54,000 | 2026-07-01 | 35 | HIGH | Dana Reeves |

## Draft Renewal Preparation Checklist
- Validate usage, support, stakeholder, and competitive evidence.
- Review value evidence and renewal options with authorized commercial owners.
- Draft customer-facing materials only after pricing, legal, and account review.

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-02 — `expansion_opportunities`

- Persona: Account Executive
- Locked prompt: Identify synthetic demand signals and draft packaging options that still require authorized pricing review.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Expansion Opportunities

**Total Expansion Potential:** $307,000

## GlobalBank (Current ARR: $1,000,000)
**Expansion Potential:** $175,000

**Signals:**
- Waitlist demand: 500 users
- 12 of 15 modules actively used

| Expansion Item | Value |
|---------------|-------|
| Additional Seats | $175,000 |

**Draft Packaging Options (authorized review required):**
- Preserve the current plan and add only the evidence-backed capability.
- Compare a staged expansion with a broader package before negotiation.
- Apply no concession unless an authorized pricing workflow approves it.

## Pinnacle Insurance Corp (Current ARR: $288,000)
**Expansion Potential:** $60,000

**Signals:**
- API usage +45% QoQ
- Requested SSO for 3 subsidiaries

| Expansion Item | Value |
|---------------|-------|
| Additional Seats | $6,000 |
| Api Premium | $18,000 |
| Sso Subsidiary | $36,000 |

**Draft Packaging Options (authorized review required):**
- Preserve the current plan and add only the evidence-backed capability.
- Compare a staged expansion with a broader package before negotiation.
- Apply no concession unless an authorized pricing workflow approves it.

## Skyline Hospitality Group (Current ARR: $360,000)
**Expansion Potential:** $42,000

**Signals:**
- Opening 12 new locations
- Requested bulk seat pricing
- Custom integration POC

| Expansion Item | Value |
|---------------|-------|
| Additional Seats | $6,000 |
| Custom Integration | $36,000 |

**Draft Packaging Options (authorized review required):**
- Preserve the current plan and add only the evidence-backed capability.
- Compare a staged expansion with a broader package before negotiation.
- Apply no concession unless an authorized pricing workflow approves it.

## Redwood Supply Chain (Current ARR: $192,000)
**Expansion Potential:** $30,000

**Signals:**
- Inquired about analytics add-on

| Expansion Item | Value |
|---------------|-------|
| Additional Seats | $6,000 |
| Analytics Addon | $24,000 |

**Draft Packaging Options (authorized review required):**
- Preserve the current plan and add only the evidence-backed capability.
- Compare a staged expansion with a broader package before negotiation.
- Apply no concession unless an authorized pricing workflow approves it.


**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-03 — `churn_risk`

- Persona: Customer Success Manager
- Locked prompt: Which synthetic accounts show churn or competitor risk, and what switching-cost assumptions require validation?
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Churn Risk Assessment

**Total ARR at Risk:** $1,318,000

## ClearView Analytics (ARR: $72,000)
- Health Score: 29
- NPS: 34
- Seat Utilization: 60.0%
- Usage Trend: declining
- Support Tickets (90d): 18

**Churn Signals:**
- Usage down 32%
- Executive sponsor departed
- Competitor eval detected

**Synthetic Switching-Cost Review:**
- Data Migration: $180,000
- User Retraining: $120,000
- Integration Rebuild: $200,000
- Illustrative total switching-cost assumption: $500,000
- Validate every component with the customer and authorized commercial owners before use.

## Granite Construction Co (ARR: $54,000)
- Health Score: 35
- NPS: 41
- Seat Utilization: 60.0%
- Usage Trend: declining
- Support Tickets (90d): 11

**Churn Signals:**
- Primary admin inactive 45 days
- Missed last 2 QBRs

## Redwood Supply Chain (ARR: $192,000)
- Health Score: 62
- NPS: 65
- Seat Utilization: 98.8%
- Usage Trend: stable
- Support Tickets (90d): 7

**Churn Signals:**
- Budget freeze mentioned in QBR

## GlobalBank (ARR: $1,000,000)
- Health Score: 87
- NPS: 72
- Seat Utilization: 99.4%
- Usage Trend: increasing
- Support Tickets (90d): 3

**Churn Signals:**
- Competitor offer: FinTech Solutions at a 30% discount

**Synthetic Switching-Cost Review:**
- Data Migration: $180,000
- User Retraining: $120,000
- Integration Rebuild: $200,000
- Illustrative total switching-cost assumption: $500,000
- Validate every component with the customer and authorized commercial owners before use.


**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-04 — `revenue_impact`

- Persona: Sales Leadership
- Locked prompt: Compare the bundled synthetic renewal, expansion, and churn scenarios without making revenue commitments.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Synthetic Revenue Scenario

**Base Renewal ARR:** $1,966,000
**Expansion Potential:** $307,000
**Churn Risk ARR:** $1,318,000

## Scenarios

| Scenario | Projected ARR |
|----------|--------------|
| Best Case (full expansion, no churn) | $2,273,000 |
| Illustrative midpoint assumption (40% expansion, 30% churn) | $1,693,400 |
| Worst Case (no expansion, full churn) | $648,000 |

## Recommendations
- Prioritize executive engagement for high-churn-risk accounts.
- Prepare expansion options for authorized review where demand signals are present.
- Review whether CSM capacity should be adjusted for higher-risk synthetic accounts.

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-05 — `account_health`

- Persona: Account Executive
- Locked prompt: GlobalBank license expires in 45 days. Currently 2,000 seats at $1M ARR. Usage shows they need 500 more seats. Competitor offering 30% discount.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Account Analysis: GlobalBank

License renews in 45 days (2026-04-30). Strong usage gives leverage despite the competitor discount.

| Metric | Value | Signal |
|---|---|---|
| Current ARR | $1.0M (2,000 seats) | Baseline |
| Active usage | 99.4% (1,987 users) | Excellent |
| Waitlist demand | 500 users | Expansion |
| Health score | 87/100 | Strong |
| Competitor threat | FinTech Solutions | 30% discount |

**Value Realized by GlobalBank:**
- $4.2M documented cost savings
- 12 of 15 modules actively used
- API calls: 2.3M/month (growing 15% MoM)
- NPS from their team: 72

Next step: want to see the competitive defense strategy?

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-06 — `competitive_defense`

- Persona: Customer Success Manager
- Locked prompt: Yes, show me the competitive defense strategy.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Competitive Defense Strategy

FinTech Solutions is offering 30% off their enterprise tier. Counter-strategy based on the switching-cost analysis:

## Competitor Offer Analysis

| Factor | FinTech Solutions | Our Position |
|---|---|---|
| Price | 30% lower | Match + value-add |
| Migration cost | $0 (their offer) | $500K actual cost |
| Feature parity | 78% | 100% |
| Integration work | 4-6 months | Already done |

## Their Hidden Costs (draft to share with GlobalBank after review)
- Data Migration: 6-week project = $180K
- User Retraining: 2,000 users, plus productivity loss = $120K
- Integration Rebuild: 8 custom connections = $200K
- Total switching cost: ~$500K

## Our Counter-Strategy (draft options for authorized pricing review)
- Match their 30% discount on renewal
- Add premium support ($60K value) at no charge
- Lock a 3-year term for stability
- Include an executive roadmap session

Next step: should I build the renewal and expansion proposal with pricing?

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-07 — `renewal_proposal`

- Persona: Account Executive
- Locked prompt: Yes, build the renewal and expansion proposal.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Draft Renewal + Expansion Proposal: GlobalBank

Proposal draft that answers the competitor threat while capturing the 500-seat expansion.

| Component | Quantity | Unit Price | Annual Value |
|---|---|---|---|
| Base renewal | 2,000 seats | $350/seat | $700K |
| Expansion | 500 seats | $350/seat | $175K |
| Premium support | Included | $0 | $60K value |
| Total ARR | 2,500 seats | | $875K |

## Proposal Positioning
- 30% discount applied to the $500/seat list price (matches competitor)
- 3-year term: additional 10% = $787.5K/year
- List value $1,250K -> $787.5K (37% effective discount)
- But: 25% more seats, premium support included

## ROI for GlobalBank
- Their cost savings: $4.2M annually
- Their cost: $787.5K per year
- ROI: 5.3x return on investment

Draft for deal-desk and pricing approval; not sent to the customer.

Next step: want me to prepare the executive presentation and talking points?

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-08 — `executive_brief`

- Persona: Account Executive
- Locked prompt: Yes, create the executive presentation with talking points.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Draft Executive Presentation

Executive presentation outline ready with 8 slides focused on value realization and strategic partnership.

## Presentation Structure
1. Title - GlobalBank strategic partnership renewal
2. Partnership Value - $4.2M savings delivered
3. Usage Success - 99.4% adoption, 12 modules active
4. Growth Support - 500 new seats for waitlisted teams
5. Competitive Comparison - TCO analysis showing $500K switching cost
6. Proposal Summary - 2,500 seats, 3-year commitment
7. Roadmap Preview - features launching in the next 12 months
8. Next Steps - executive decision 30 days before expiry

## Key Talking Points
- "You've realized $4.2M in savings - 5x your investment"
- "Switching costs $500K+ before any productivity loss"
- "We're matching their price AND adding premium support"
- "A 3-year term locks in today's pricing against inflation"

**Objection Handlers:** 12 prepared responses drafted for sales enablement review.

Next step: ready to see the negotiation strategy and the approvals you need?

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-09 — `negotiation_plan`

- Persona: Sales Leadership
- Locked prompt: Yes, show me negotiation strategy and what approvals I need.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Negotiation Plan and Required Approvals

Negotiation path mapped; internal approvals are listed as requests to route, not granted approvals.

## Negotiation Boundaries

| Lever | Floor | Target | Approval Needed |
|---|---|---|---|
| Discount | 30% | 25% | Pre-approved policy for a 3-year term |
| Term | 1 year | 3 years | None (standard) |
| Payment | Net 60 | Annual upfront | Finance |
| Premium support | Included | Included | VP Sales |
| Implementation | $0 | $0 for new modules | VP Sales |

## Internal Approvals to Request (pre-staged drafts)
- Finance: request confirmation of the 30% discount for a 3-year term
- Legal: contract template ready for review; redlines pending
- VP Sales: implementation waiver to request
- CFO: required only if the discount exceeds 35%

## Negotiation Strategy
- Lead with value ($4.2M savings)
- Anchor on a 25% discount, concede to 30%
- Trade discount for a longer term or upfront payment

Next step: should I prepare the executive meeting request and the proposal for you to send?

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-10 — `deal_summary`

- Persona: Sales Leadership
- Locked prompt: Yes, send the proposal and summarize our renewal strategy.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

# Renewal Strategy Summary

The proposal and meeting request for GlobalBank's VP of Technology are ready for you to send (not sent). Complete renewal strategy:

## Session Summary
- Account analysis - 99.4% usage, 87 health score, $4.2M value delivered
- Competitive defense - $500K switching cost identified, 30% match strategy
- Expansion capture - 500 additional seats from waitlist demand
- Pricing proposal - $787.5K/year for 2,500 seats (3-year term)
- Executive presentation - 8 slides with objection handlers
- Approvals - routed as requests; contract template ready for review

## Deal Metrics

| Metric | Original | Proposed |
|---|---|---|
| ARR | $1.0M | $787.5K (-21%) |
| Seats | 2,000 | 2,500 (+25%) |
| Term | 1 year | 3 years |
| TCV | | $2.36M |

## Next Steps
- Executive meeting: request for next week
- Decision timeline: 30 days before expiration
- Win probability (modeled): 78% (up from 52%)

The renewal defense is positioned to retain $2.36M TCV against the competitive threat.

**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

## Evidence-first response contract

1. Label the result as a fixed synthetic snapshot.
2. Cite exact source identifiers and fields before computed conclusions.
3. Preserve every required heading and distinguish recorded evidence from calculations and scenarios.
4. Present messages, assignments, mitigations, recommendations, pricing, approvals, and next steps only as drafts or options for authorized human review.
5. End with an evidence boundary confirming that no external system or customer-facing action occurred.

## Failure and safety behavior

- Never browse or use external CRM, email, meeting, social, news, product, usage, competitive, subscription, pricing, or customer systems.
- Never invent a missing identifier, value, signal, benchmark, relationship, result, or source.
- Never send outreach, assign an owner, update CRM, create a task or alert, activate monitoring, schedule a meeting, change a forecast, approve pricing, issue a proposal, alter a subscription, or contact a customer.
- Do not present synthetic conversion, win-rate, savings, margin, pipeline, ARR, renewal, expansion, or revenue scenarios as observed, realized, approved, forecast, or committed results.
- Require authorized human review before any external or commercial use.
