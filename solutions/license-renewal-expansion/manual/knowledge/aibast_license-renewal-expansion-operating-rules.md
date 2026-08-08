# License Renewal and Expansion Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `renewal_pipeline` | Review the bundled synthetic renewal pipeline, risk bands, and preparation checklist without changing CRM or forecast records. | `Renewal Pipeline`; `Draft Renewal Preparation Checklist`; `Evidence boundary` |
| `expansion_opportunities` | Identify synthetic demand signals and draft packaging options that still require authorized pricing review. | `Expansion Opportunities`; `Draft Packaging Options`; `Evidence boundary` |
| `churn_risk` | Which synthetic accounts show churn or competitor risk, and what switching-cost assumptions require validation? | `Churn Risk Assessment`; `Synthetic Switching-Cost Review`; `Evidence boundary` |
| `revenue_impact` | Compare the bundled synthetic renewal, expansion, and churn scenarios without making revenue commitments. | `Synthetic Revenue Scenario`; `Illustrative midpoint assumption`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

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
    at_risk_arr = sum(p["arr"] for p in pipeline if p["risk"] == "high")
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
            seat_rev = EXPANSION_PRICING["additional_seats"]["unit_price"] * 50
            potential += seat_rev
            items.append({"type": "additional_seats", "value": seat_rev})
        for signal in lic["expansion_signals"]:
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
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

# Renewal Pipeline

**Total Renewal ARR:** $966,000
**At-Risk ARR:** $126,000

| Customer | ARR | Renewal Date | Health | Risk | CSM |
|----------|-----|-------------|--------|------|-----|
| Skyline Hospitality Group | $360,000 | 2026-04-15 | 94 | LOW | James Okafor |
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
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

# Expansion Opportunities

**Total Expansion Potential:** $114,000

## Pinnacle Insurance Corp (Current ARR: $288,000)
**Expansion Potential:** $42,000

**Signals:**
- API usage +45% QoQ
- Requested SSO for 3 subsidiaries

| Expansion Item | Value |
|---------------|-------|
| Additional Seats | $6,000 |
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
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

# Churn Risk Assessment

**Total ARR at Risk:** $318,000

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
- Data Migration: $45,000
- Reimplementation: $60,000
- User Retraining: $18,000
- Parallel Run: $24,000
- Illustrative total switching-cost assumption: $147,000
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


**Synthetic source model:** Bundled subscription, usage, support, and planning records.

**Evidence boundary:** Exact names, dates, seats, scores, prices, ARR, percentages, and projections are synthetic planning evidence. This read-only output did not approve a concession, change pricing, create or send a proposal, write a CRM record, or contact a customer.

### LRE-04 — `revenue_impact`

- Persona: Sales Leadership
- Locked prompt: Compare the bundled synthetic renewal, expansion, and churn scenarios without making revenue commitments.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

# Synthetic Revenue Scenario

**Base Renewal ARR:** $966,000
**Expansion Potential:** $114,000
**Churn Risk ARR:** $318,000

## Scenarios

| Scenario | Projected ARR |
|----------|--------------|
| Best Case (full expansion, no churn) | $1,080,000 |
| Illustrative midpoint assumption (40% expansion, 30% churn) | $916,200 |
| Worst Case (no expansion, full churn) | $648,000 |

## Recommendations
- Prioritize executive engagement for high-churn-risk accounts.
- Prepare expansion options for authorized review where demand signals are present.
- Review whether CSM capacity should be adjusted for higher-risk synthetic accounts.

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
