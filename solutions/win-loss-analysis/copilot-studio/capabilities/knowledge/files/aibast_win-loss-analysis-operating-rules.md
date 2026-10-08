# Win Loss Analysis Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `win_loss_overview` | Compare the bundled synthetic Q3 and Q2 win and loss patterns and show where the decline is concentrated. | `Q3 Win/Loss Overview`; `Loss by Competitor`; `CompetitorX 47%`; `Evidence boundary` |
| `root_cause_analysis` | Identify the evidence-backed synthetic loss drivers and buyer feedback themes that enablement should review. | `Root Cause Analysis`; `Buyer Key Insight`; `38%`; `Evidence boundary` |
| `counter_strategies` | Draft counter-strategy and talk-track options from the synthetic loss evidence for enablement review. | `Counter-Strategies`; `Talk Track`; `FedRAMP in progress`; `Evidence boundary` |
| `revenue_impact` | Model synthetic intervention scenarios without presenting them as realized or committed revenue. | `Synthetic Revenue Scenario Model`; `$4.2M`; `23:1`; `Evidence boundary` |
| `board_presentation` | Draft a board-level synthetic win and loss narrative with all investment and performance values labeled as scenarios. | `Board Presentation`; `Decision for authorized leaders`; `32% Q4 win rate`; `Evidence boundary` |
| `action_summary` | Summarize the synthetic findings and candidate next steps without activating programs or approvals. | `Complete Summary`; `Draft Next-Step Options`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

### `_whole`

```python
def _whole(value):
    """Round half away from zero (16.5 -> 17), unlike Python's banker's rounding."""
    return int(value + 0.5) if value >= 0 else -int(-value + 0.5)
```

### `_pct`

```python
def _pct(value):
    """Whole-percent display, e.g. 28.3 -> '28%'."""
    return f"{_whole(value)}%"
```

### `_millions`

```python
def _millions(value):
    return f"${value / 1000000:.1f}M"
```

### `_quarter_stats`

```python
def _quarter_stats(opps):
    """Compute aggregate stats for a list of opportunities."""
    total = len(opps)
    won = [o for o in opps if o["outcome"] == "won"]
    lost = [o for o in opps if o["outcome"] == "lost"]
    win_rate = round(len(won) / max(total, 1) * 100, 1)
    avg_won_value = int(sum(o["value"] for o in won) / max(len(won), 1))
    segments = {}
    for seg in ("enterprise", "mid-market", "smb"):
        seg_opps = [o for o in opps if o["segment"] == seg]
        seg_won = [o for o in seg_opps if o["outcome"] == "won"]
        segments[seg] = {
            "total": len(seg_opps),
            "won": len(seg_won),
            "lost": len(seg_opps) - len(seg_won),
            "win_rate": round(len(seg_won) / max(len(seg_opps), 1) * 100, 1),
        }
    return {
        "total": total, "won": len(won), "lost": len(lost),
        "win_rate": win_rate, "avg_won_value": avg_won_value,
        "total_won_value": sum(o["value"] for o in won),
        "total_lost_value": sum(o["value"] for o in lost),
        "segments": segments,
    }
```

### `_competitor_breakdown`

```python
def _competitor_breakdown(opps):
    """Break down losses by competitor with counts, values and share of losses."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    competitors = {}
    for o in lost:
        comp = o["competitor_lost_to"] or "No Decision"
        if comp not in competitors:
            competitors[comp] = {"count": 0, "value": 0}
        competitors[comp]["count"] += 1
        competitors[comp]["value"] += o["value"]
    for comp in competitors:
        competitors[comp]["pct_of_losses"] = round(competitors[comp]["count"] / max(len(lost), 1) * 100, 1)
    return competitors
```

### `_loss_reason_analysis`

```python
def _loss_reason_analysis(opps, competitor=None):
    """Loss reasons by buyer mentions (primary + secondary reason cited in the win/loss interview)."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    if competitor:
        lost = [o for o in lost if o["competitor_lost_to"] == competitor]
    reasons = {}
    for o in lost:
        cited = [o["loss_reason"]] + ([o["secondary_reason"]] if o.get("secondary_reason") else [])
        for r in cited:
            if r not in reasons:
                reasons[r] = {"mentions": 0, "deals": 0, "value": 0}
            reasons[r]["mentions"] += 1
        reasons[o["loss_reason"]]["deals"] += 1
        reasons[o["loss_reason"]]["value"] += o["value"]
    total = sum(r["mentions"] for r in reasons.values())
    for r in reasons:
        pct = round(reasons[r]["mentions"] / max(total, 1) * 100, 1)
        reasons[r]["frequency_pct"] = pct
        reasons[r]["impact"] = "High" if pct >= 25 else "Medium" if pct >= 10 else "Low"
        reasons[r]["addressable"] = _ADDRESSABLE.get(r, "Unknown")
    return reasons
```

### `_revenue_recovery_model`

```python
def _revenue_recovery_model(opps, competitor="CompetitorX"):
    """Recoverable pipeline per intervention over the competitor's losses; one intervention per primary reason."""
    lost = [o for o in opps if o["outcome"] == "lost" and o["competitor_lost_to"] == competitor]
    projections = {}
    for reason, key in _REASON_TO_INTERVENTION.items():
        intv = _INTERVENTIONS[key]
        deals = [o for o in lost if o["loss_reason"] == reason]
        pipeline = sum(o["value"] for o in deals)
        value = int(round(pipeline * intv["recovery_rate"] / 100000.0)) * 100000
        projections[key] = {
            "label": intv["label"],
            "applicable_deals": len(deals),
            "total_pipeline": pipeline,
            "recoverable_value": value,
            "deals_recoverable": int(round(len(deals) * intv["recovery_rate"])),
            "timeline": intv["timeline"],
        }
    total_recoverable = sum(p["recoverable_value"] for p in projections.values())
    total_cost = sum(intv["cost"] for intv in _INTERVENTIONS.values())
    return projections, total_recoverable, total_cost
```

### `_forecast`

```python
def _forecast(opps):
    """Q4 scenario: flat Q3 bookings plus the realizable share of the recovery; win rates from recovered deals."""
    q3 = _quarter_stats(opps)
    projections, total_recoverable, total_cost = _revenue_recovery_model(opps, _FORECAST["focus_competitor"])
    lift = int(round(total_recoverable * _FORECAST["q4_realization"] / 100000.0)) * 100000
    immediate = sum(p["deals_recoverable"] for p in projections.values() if p["timeline"] == "Immediate")
    all_deals = sum(p["deals_recoverable"] for p in projections.values())
    return {
        "current": q3["total_won_value"],
        "lift": lift,
        "with": q3["total_won_value"] + lift,
        "current_wr": q3["win_rate"],
        "q4_wr": round((q3["won"] + immediate) / q3["total"] * 100, 1),
        "q1_wr": round((q3["won"] + all_deals) / q3["total"] * 100, 1),
        "recoverable": total_recoverable,
        "cost": total_cost,
        "roi": int(total_recoverable / max(total_cost, 1)),
        "projections": projections,
    }
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### WL-01 — `win_loss_overview`

- Persona: Sales Operations Manager
- Locked prompt: Compare the bundled synthetic Q3 and Q2 win and loss patterns and show where the decline is concentrated.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Q3 Win/Loss Overview** - analyzed 127 Q3 opportunities: win rate dropped 7 pts, enterprise hit hardest.

| Metric | Q3 | Q2 | Change |
|---|---|---|---|
| Win rate | 28% | 35% | -7 pts |
| Enterprise win rate | 22% | 38% | -16 pts |
| Closed opportunities | 127 | 120 | +7 |

**Win Rate by Segment:**

| Segment | Q3 | Q2 | Change |
|---|---|---|---|
| Enterprise | 22% | 38% | -16 pts |
| Mid-Market | 23% | 27% | -5 pts |
| SMB | 60% | 52% | +8 pts |

**Loss by Competitor:** CompetitorX 47% (up 12%), CompetitorY 25%, No Decision 17%

| Competitor | Losses | % of Total | Trend |
|---|---|---|---|
| CompetitorX | 43 | 47% | Up 12% |
| CompetitorY | 23 | 25% | Down 3% |
| No Decision | 15 | 17% | Down 4% |
| CompetitorZ | 10 | 11% | Down 6% |

**Pattern:** CompetitorX is winning enterprise deals with security-conscious buyers.

Next: see the root cause analysis.

Synthetic source model: [CRM + Win/Loss Interviews + Competitive Intel]
Agents: WinLossDataAgent, PatternRecognitionAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-02 — `root_cause_analysis`

- Persona: Enablement Manager
- Locked prompt: Identify the evidence-backed synthetic loss drivers and buyer feedback themes that enablement should review.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Root Cause Analysis - Losses to CompetitorX:** 4 loss drivers identified - security is the biggest gap.

| Reason | Frequency | Impact | Addressable |
|---|---|---|---|
| Security certs | 38% | High | 6 months |
| Enterprise refs | 26% | High | 3 months |
| Pricing | 21% | Medium | Immediate |
| Features | 15% | Medium | Roadmap |

Frequency = share of buyer-cited loss reasons in 43 lost deals (47 reasons cited).

**Buyer Key Insight:** "We loved the product but couldn't get past security review" (8 of 10 lost buyers)

**Gap:** They have FedRAMP + 12 Fortune 500 logos; we have SOC 2 + 3 refs.

- Security: 16 deals, $7,200,000 pipeline
- References: 11 deals, $3,360,000 pipeline

Next: counter-strategies.

Synthetic source model: [Win/Loss Surveys + Gong Calls + Competitive Intel]
Agents: RootCauseAnalysisAgent, PatternRecognitionAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-03 — `counter_strategies`

- Persona: Enablement Manager
- Locked prompt: Draft counter-strategy and talk-track options from the synthetic loss evidence for enablement review.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Counter-Strategies by Driver (vs CompetitorX):**

**Immediate (This Quarter):**

- **Security positioning** (Immediate): Lead with SOC 2 Type II (currently underutilized in sales materials); Bridge message: "FedRAMP in progress" with the readiness timeline; Create a Security Architecture one-pager for enterprise buyers; Offer the buyer's security team direct access during evaluation
- **Reference program** (30 days): Activate 3 enterprise customers for reference calls; Produce video testimonials from enterprise logos; Offer reference incentives (extended support, discounts)
- **Pricing flexibility** (Immediate): Enterprise tier: bundle security features at no extra cost; Offer a 90-day pilot option with success-based conversion; Match competitor payment-terms flexibility

**Longer-Term:**

- Roadmap commitments (Next quarter, within the existing roadmap budget)
- FedRAMP certification (6 months, $85,000 investment)
- ISO 27001 (4 months, $25,000 investment)

**Talk Track:** "Secure choice with modern UX. SOC 2 active, FedRAMP in progress. Let us connect you with 3 enterprise references."

Next: see the revenue impact.

Synthetic source model: [Competitive Playbook + Product Roadmap]
Agents: CompetitiveStrategyAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-04 — `revenue_impact`

- Persona: Sales Leader
- Locked prompt: Model synthetic intervention scenarios without presenting them as realized or committed revenue.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Synthetic Revenue Scenario Model:** $4.2M recoverable pipeline with interventions.

| Action | Value | Timeline | Deals Recoverable |
|---|---|---|---|
| Security positioning | $1.8M | Immediate | 4 of 16 deals |
| Reference program | $1.2M | 30 days | 4 of 11 deals |
| Pricing flexibility | $0.8M | Immediate | 1 of 9 deals |
| Roadmap commitments | $0.4M | Next quarter | 1 of 7 deals |

**Q4 Impact:** $8.2M -> $10.8M (+$2.6M); win rate 28% -> 32% in Q4 and 36% by Q1 as the reference program lands.

**Investment:** $180K | **ROI:** 23:1

Q4 assumes flat Q3 bookings plus 62% of the recoverable pipeline; FedRAMP and ISO 27001 are enablers with cost only, so no deal is counted twice.

Next: build the board executive summary.

Synthetic source model: [Revenue Analytics + Forecast Models]
Agents: RevenueImpactAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-05 — `board_presentation`

- Persona: Sales Leader
- Locked prompt: Draft a board-level synthetic win and loss narrative with all investment and performance values labeled as scenarios.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Board Presentation: Q3 Win/Loss - Executive Summary**

| Slide | Content |
|---|---|
| Challenge | Win rate 28% (down 7), CompetitorX taking 47% of losses |
| Root Causes | Security certs (38%), Enterprise refs (26%), Pricing (21%) |
| Plan | Security messaging now -> References in 30 days -> FedRAMP in 6 months |
| Ask | $180K for certification + reference program |
| Expected | 32% Q4 win rate, $4.2M pipeline recovery, 23:1 ROI |

**Decision for authorized leaders:** evaluate the synthetic $180,000 investment scenario and require normal approvals before any action. The summary is ready for you to share in Teams.

Synthetic source model: [All Analysis Systems]
Agents: ExecutivePresentationAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-06 — `action_summary`

- Persona: Sales Operations Manager
- Locked prompt: Summarize the synthetic findings and candidate next steps without activating programs or approvals.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Win/Loss Analysis - Complete Summary**

| Insight | Finding |
|---|---|
| Q3 win rate | 28% (-7 pts from Q2) |
| Primary competitor | CompetitorX (47% of losses) |
| Biggest gap | Security certs (38%) |
| Second gap | Enterprise refs (26%) |
| Recoverable pipeline | $4.2M |

**Session Accomplishments:**
- Analyzed 127 Q3 opportunities
- Identified 4 loss drivers
- Developed counter-strategies for each driver
- Modeled a $4.2M synthetic recovery scenario
- Created the board executive summary

**Draft Next-Step Options:**
1. Review security positioning materials
2. Evaluate a pricing-flexibility policy with authorized approvers
3. Validate reference availability before any buyer contact
4. Review draft talk tracks with enablement leaders

**Synthetic Scenario:** the model illustrates movement from 28% to 32% in Q4 and 36% by Q1; it is not a conversion, revenue, ROI, or forecast commitment.

Synthetic source model: [All Win/Loss Systems]
Agents: ExecutivePresentationAgent (orchestrating all agents)

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

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
