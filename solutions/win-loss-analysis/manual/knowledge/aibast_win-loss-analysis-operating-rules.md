# Win Loss Analysis Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `win_loss_overview` | Compare the bundled synthetic Q3 and Q2 win and loss patterns and show where the decline is concentrated. | `Q3 Win/Loss Overview`; `Loss Analysis by Competitor`; `Evidence boundary` |
| `root_cause_analysis` | Identify the evidence-backed synthetic loss drivers and buyer feedback themes that enablement should review. | `Root Cause Analysis`; `Deep Dive`; `Evidence boundary` |
| `counter_strategies` | Draft counter-strategy and talk-track options from the synthetic loss evidence for enablement review. | `Counter-Strategies`; `Updated Talk Track`; `Evidence boundary` |
| `revenue_impact` | Model synthetic intervention scenarios without presenting them as realized or committed revenue. | `Synthetic Revenue Scenario Model`; `Illustrative scenario value`; `Evidence boundary` |
| `board_presentation` | Draft a board-level synthetic win and loss narrative with all investment and performance values labeled as scenarios. | `Board Presentation`; `Decision for authorized leaders`; `Evidence boundary` |
| `action_summary` | Summarize the synthetic findings and candidate next steps without activating programs or approvals. | `Complete Summary`; `Draft Next-Step Options`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

### `_quarter_stats`

```python
def _quarter_stats(opps):
    """Compute aggregate stats for a list of opportunities."""
    total = len(opps)
    won = [o for o in opps if o["outcome"] == "won"]
    lost = [o for o in opps if o["outcome"] == "lost"]
    win_rate = round(len(won) / max(total, 1) * 100, 1)
    avg_won_value = int(sum(o["value"] for o in won) / max(len(won), 1))
    total_won_value = sum(o["value"] for o in won)
    total_lost_value = sum(o["value"] for o in lost)

    # Segment breakdown
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
        "total_won_value": total_won_value,
        "total_lost_value": total_lost_value,
        "segments": segments,
    }
```

### `_competitor_breakdown`

```python
def _competitor_breakdown(opps):
    """Break down losses by competitor with counts and values."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    competitors = {}
    no_decision_count = 0
    no_decision_value = 0
    for o in lost:
        comp = o["competitor_lost_to"]
        if comp is None:
            no_decision_count += 1
            no_decision_value += o["value"]
        else:
            if comp not in competitors:
                competitors[comp] = {"count": 0, "value": 0, "reasons": {}}
            competitors[comp]["count"] += 1
            competitors[comp]["value"] += o["value"]
            reason = o["loss_reason"] or "unknown"
            competitors[comp]["reasons"][reason] = competitors[comp]["reasons"].get(reason, 0) + 1

    competitors["No Decision"] = {"count": no_decision_count, "value": no_decision_value, "reasons": {"no_decision": no_decision_count}}
    total_lost = len(lost)
    for comp in competitors:
        competitors[comp]["pct_of_losses"] = round(competitors[comp]["count"] / max(total_lost, 1) * 100, 1)
    return competitors
```

### `_loss_reason_analysis`

```python
def _loss_reason_analysis(opps, competitor=None):
    """Analyze loss reasons, optionally filtered to a specific competitor."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    if competitor:
        lost = [o for o in lost if o["competitor_lost_to"] == competitor]

    reasons = {}
    for o in lost:
        r = o["loss_reason"] or "unknown"
        if r not in reasons:
            reasons[r] = {"count": 0, "value": 0}
        reasons[r]["count"] += 1
        reasons[r]["value"] += o["value"]

    total_lost = len(lost)
    for r in reasons:
        reasons[r]["frequency_pct"] = round(reasons[r]["count"] / max(total_lost, 1) * 100, 1)

    # Impact scoring: high if frequency > 25%, medium 10-25%, low < 10%
    for r in reasons:
        pct = reasons[r]["frequency_pct"]
        if pct >= 25:
            reasons[r]["impact"] = "High"
        elif pct >= 10:
            reasons[r]["impact"] = "Medium"
        else:
            reasons[r]["impact"] = "Low"

        # Addressable assessment
        addressable_map = {
            "security_certs": "Yes (6 months)",
            "enterprise_references": "Yes (3 months)",
            "pricing": "Yes (immediate)",
            "feature_gaps": "Roadmap item",
            "no_decision": "Partially (nurture)",
            "relationship": "Yes (engagement plan)",
        }
        reasons[r]["addressable"] = addressable_map.get(r, "Unknown")

    return reasons
```

### `_revenue_recovery_model`

```python
def _revenue_recovery_model(opps):
    """Model recoverable revenue per intervention based on loss data."""
    lost = [o for o in opps if o["outcome"] == "lost"]
    projections = {}
    total_recoverable = 0

    reason_to_intervention = {
        "security_certs": ["security_positioning", "fedramp_certification"],
        "enterprise_references": ["reference_program"],
        "pricing": ["pricing_flexibility"],
        "feature_gaps": [],
        "no_decision": [],
        "relationship": ["reference_program"],
    }

    for intv_key, intv in _INTERVENTIONS.items():
        # Find deals that map to this intervention
        applicable_reasons = [r for r, ivs in reason_to_intervention.items() if intv_key in ivs]
        applicable_deals = [o for o in lost if o.get("loss_reason") in applicable_reasons]

        total_pipeline = sum(o["value"] for o in applicable_deals)
        recoverable_value = int(total_pipeline * intv["recovery_rate"])
        deal_count_low = max(1, int(len(applicable_deals) * intv["recovery_rate"] * 0.7))
        deal_count_high = max(deal_count_low, int(len(applicable_deals) * intv["recovery_rate"] * 1.1))

        projections[intv_key] = {
            "label": intv["label"],
            "applicable_deals": len(applicable_deals),
            "total_pipeline": total_pipeline,
            "recoverable_value": recoverable_value,
            "deals_recoverable": f"{deal_count_low}-{deal_count_high}",
            "cost": intv["cost"],
            "timeline": intv["timeline"],
            "roi": round(recoverable_value / max(intv["cost"], 1), 1),
        }
        total_recoverable += recoverable_value

    total_cost = sum(intv["cost"] for intv in _INTERVENTIONS.values())
    return projections, total_recoverable, total_cost
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### WL-01 — `win_loss_overview`

- Persona: Sales Operations Manager
- Locked prompt: Compare the bundled synthetic Q3 and Q2 win and loss patterns and show where the decline is concentrated.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Q3 Win/Loss Overview** (127 closed opportunities analyzed)

| Metric | Q3 | Q2 | Change |
|---|---|---|---|
| Total opportunities | 127 | 118 | +8% |
| Win rate | 38.6% | 44.9% | -6.3 pts |
| Enterprise win rate | 20.0% | 40.0% | -20.0 pts |
| Avg deal size (won) | $172,102 | $189,490 | -9% |

**Win Rate by Segment:**

| Segment | Q3 | Q2 | Change |
|---|---|---|---|
| Enterprise | 20.0% | 40.0% | -20.0 pts |
| Mid-Market | 31.6% | 31.0% | +0.6 pts |
| Smb | 76.7% | 76.7% | +0.0 pts |

**Loss Analysis by Competitor:**

| Competitor | Losses | % of Total | Trend |
|---|---|---|---|
| CompetitorX | 29 | 37.2% | Up 14.1% |
| CompetitorY | 23 | 29.5% | Down 7% |
| No Decision | 17 | 21.8% | Down 4% |
| CompetitorZ | 9 | 11.5% | Down 2% |

**Initial Pattern:** CompetitorX wins are concentrated in enterprise ($500K+) deals with security-conscious buyers.

Synthetic source model: [CRM + Win/Loss Interviews + Competitive Intel]
Agents: WinLossDataAgent, PatternRecognitionAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-02 — `root_cause_analysis`

- Persona: Enablement Manager
- Locked prompt: Identify the evidence-backed synthetic loss drivers and buyer feedback themes that enablement should review.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Root Cause Analysis - Losses to CompetitorX:**

| Reason | Frequency | Impact | Addressable? |
|---|---|---|---|
| Security certifications | 41.4% | High | Yes (6 months) |
| Enterprise references | 24.1% | Medium | Yes (3 months) |
| Pricing/packaging | 17.2% | Medium | Yes (immediate) |
| Feature gaps | 10.3% | Medium | Roadmap item |
| Relationship/trust | 6.9% | Low | Yes (engagement plan) |

**Deep Dive - Security (12 deals, $7,450,000 pipeline):**
- CompetitorX has FedRAMP certification (we do not)
- They lead with SOC 2 Type II + ISO 27001 in every proposal
- Enterprise buyers require these for procurement approval
- Quote: "We loved the product but couldn't get past security review"

**Deep Dive - References (7 deals, $3,205,000 pipeline):**
- CompetitorX has 12 Fortune 500 logos available for reference
- We have 3 enterprise references currently available
- Buyers want peer validation at their scale before committing
- Quote: "We need peer validation from companies our size before we commit"

**Win/Loss Interview Insight:** 8 of 10 lost buyers said they preferred our UX but couldn't justify the security/reference risk.

Synthetic source model: [Win/Loss Surveys + Gong Calls + Competitive Intel]
Agents: RootCauseAnalysisAgent, PatternRecognitionAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-03 — `counter_strategies`

- Persona: Enablement Manager
- Locked prompt: Draft counter-strategy and talk-track options from the synthetic loss evidence for enablement review.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Counter-Strategies for Win Rate Recovery:**

**Immediate Actions (This Quarter):**

**1. Security Positioning Refresh**
- Lead with SOC 2 Type II (currently underutilized in sales materials)
- Create Security Architecture one-pager for enterprise buyers
- Offer security team direct access during evaluation period
- Bridge messaging: FedRAMP in progress, SOC 2 + ISO active now

**2. Enterprise Reference Program**
- Activate 3 enterprise customers for reference calls
- Produce 2 video testimonials from Fortune 1000 logos
- Offer reference incentives (extended support, discounts)
- Build enterprise customer advisory board

**3. Pricing & Packaging Adjustment**
- Enterprise tier: bundle security features at no extra cost
- Offer 90-day pilot with success-based conversion
- Match competitor payment terms flexibility
- Introduce volume discount for multi-year commits

**Longer-Term (Next 2 Quarters):**

- FedRAMP Certification (6 months timeline, $85,000 investment)
  - Engage FedRAMP 3PAO for readiness assessment
  - Assign dedicated compliance engineering team
  - Target FedRAMP Moderate authorization
- ISO 27001 Certification (4 months timeline, $25,000 investment)
  - Engage certification body for gap assessment
  - Implement required ISMS controls
  - Complete Stage 1 and Stage 2 audits

**Updated Talk Track:**
"We're the secure choice for enterprises who want modern UX. Here's our SOC 2 Type II, and our FedRAMP is in progress. Let us connect you with 3 enterprise references in your industry."

Synthetic source model: [Competitive Playbook + Product Roadmap]
Agents: CompetitiveStrategyAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-04 — `revenue_impact`

- Persona: Sales Leader
- Locked prompt: Model synthetic intervention scenarios without presenting them as realized or committed revenue.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Synthetic Revenue Scenario Model:**

| Intervention | Deals Recoverable | Pipeline Value | Timeline |
|---|---|---|---|
| FedRAMP Certification | 4-7 deals | $4,097,500 | 6 months |
| Security Positioning Refresh | 2-4 deals | $2,607,500 | Immediate |
| Enterprise Reference Program | 4-7 deals | $2,098,000 | 30 days |
| Pricing & Packaging Adjustment | 4-6 deals | $1,388,400 | Immediate |
| ISO 27001 Certification | 1-1 deals | $0 | 4 months |

**Q4 Forecast Impact:**
- Current trajectory: $8,433,000 (38.6% win rate)
- With interventions: $14,751,668 (45.1% win rate)
- **Illustrative incremental scenario value: $6,318,668**

**Win Rate Recovery Path:**

| Quarter | Projected Win Rate | Key Driver |
|---|---|---|
| Q4 | 45.1% | Positioning + pricing |
| Q1 | 49.1% | References + certifications |
| Q2 | 53.1% | Full program maturity |

**ROI Calculation:**
- Investment: $180,000 (certifications, content, incentives)
- Illustrative scenario value: $10,191,400
- Modeled value-to-cost ratio: 56.6:1

Synthetic source model: [Revenue Analytics + Forecast Models]
Agents: RevenueImpactAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-05 — `board_presentation`

- Persona: Sales Leader
- Locked prompt: Draft a board-level synthetic win and loss narrative with all investment and performance values labeled as scenarios.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Board Presentation: Q3 Win/Loss Analysis**

**Slide 1: The Challenge**
- Win rate declined to 38.6% (from 44.9%)
- Enterprise segment hit hardest (-20.0 pts)
- CompetitorX captured 37.2% of our losses
- Root cause: Security positioning and references gap

**Slide 2: Why We're Losing**

| Factor | Impact | Evidence |
|---|---|---|
| Security certs | 41.4% of losses | Buyer feedback, lost deal analysis |
| Enterprise refs | 24.1% of losses | Buyer feedback, lost deal analysis |
| Pricing | 17.2% of losses | Buyer feedback, lost deal analysis |

**Slide 3: The Plan**
- Immediate: Security messaging refresh, pricing flexibility
- 30 days: Enterprise reference program launch
- 6 months: FedRAMP + ISO 27001 certification

**Slide 4: Synthetic Scenario Outputs**
- Q4 win rate target: 45.1% (+6.5 pts)
- Pipeline recovery: $10,191,400
- Investment required: $180,000
- ROI: 56.6:1

**Decision for authorized leaders:** Evaluate the synthetic $180,000 investment scenario and require normal approvals before any action.

Synthetic source model: [All Analysis Systems]
Agents: ExecutivePresentationAgent

**Evidence boundary:** Exact deal values, counts, interview statements, rates, costs, ROI, and recovery figures are synthetic scenario evidence, not measured business results or commitments. This read-only output did not change a forecast, approve spend, publish enablement, or contact a buyer.

### WL-06 — `action_summary`

- Persona: Sales Operations Manager
- Locked prompt: Summarize the synthetic findings and candidate next steps without activating programs or approvals.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Win/Loss Analysis - Complete Summary**

| Insight | Finding |
|---|---|
| Q3 win rate | 38.6% (-6.3 pts from Q2) |
| Primary competitor | CompetitorX (37.2% of losses) |
| Biggest gap | Security certifications (41.4%) |
| Second gap | Enterprise references (24.1%) |
| Recoverable pipeline | $10,191,400 |

**Session Accomplishments:**
- Analyzed 127 Q3 opportunities
- Identified 4 root causes for losses
- Developed counter-strategies for each driver
- Modeled a $10,191,400 synthetic recovery scenario
- Created board presentation framework

**Draft Next-Step Options:**
1. Review security positioning materials
2. Evaluate a pricing-flexibility policy with authorized approvers
3. Validate reference availability before any buyer contact
4. Review draft talk tracks with enablement leaders

**Candidate 30-Day Milestones:**
- Draft reference-story plan reviewed
- Decide whether to begin a FedRAMP readiness assessment
- Draft win-rate tracking dashboard reviewed

**Synthetic Scenario:** The model illustrates movement from 38.6% to 45.1% within 2 quarters and $10,191,400 of scenario value; it is not a conversion, revenue, ROI, or forecast commitment.

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
