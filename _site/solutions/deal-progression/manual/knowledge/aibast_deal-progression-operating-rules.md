# Deal Progression Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `pipeline_health` | Which opportunities need attention in the synthetic pipeline, and what evidence should I review before changing the forecast? | `Pipeline Health Summary`; `Evidence boundary` |
| `stalled_deals` | What blocker evidence explains the loss of momentum on our two largest stalled synthetic deals? | `Stalled Deal Deep-Dive`; `Diagnosis`; `Evidence boundary` |
| `action_plans` | Draft reviewable intervention plans for our two largest stalled synthetic deals, but do not assign work or contact anyone. | `Action Plans`; `Planning Objective`; `Evidence boundary` |
| `acceleration` | Which synthetic timing options could move pipeline review forward without turning scenario value into a forecast commitment? | `Pipeline Acceleration Strategy`; `Synthetic Scenario`; `Evidence boundary` |
| `assign_tasks` | Map candidate follow-up work to the synthetic rep capacity for my review; do not create tasks or alerts. | `Draft Task Assignment Plan`; `candidate tasks`; `Evidence boundary` |
| `executive_summary` | Give me a leadership-ready summary of the synthetic pipeline findings and the decisions that still require human review. | `Executive Summary`; `Synthetic Planning Targets`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed. `stalled_deals` and `action_plans` accept an optional `deals` selection (`TechCorp and Global Manufacturing`, `TechCorp`, `Global Manufacturing`, `Apex Financial` or `all`); without it they cover the top two stalled deals.

Demo conversation path: "Show me which deals are stalled in my pipeline and what actions will move them forward" -> `pipeline_health`; "Yes, give me the details on TechCorp and Global Manufacturing" -> `stalled_deals`; "Yes, create action plans with specific next steps" -> `action_plans`; "Yes, show me how to accelerate the entire pipeline" -> `acceleration`; "Yes, assign tasks and set up tracking" -> `assign_tasks`; "Yes, summarize everything we accomplished" -> `executive_summary`.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

### `_active_pipeline`

```python
def _active_pipeline():
    """Return only open, active-stage deals."""
    return [d for d in _PIPELINE if d["stage"] in _ACTIVE_STAGES]
```

### `_classify_deals`

```python
def _classify_deals():
    """Classify every active deal as on_track, at_risk, or stalled."""
    on_track, at_risk, stalled = [], [], []
    for d in _active_pipeline():
        benchmark = _STAGE_BENCHMARKS.get(d["stage"], 14)
        ratio = d["days_in_stage"] / benchmark
        if ratio >= 1.25:
            stalled.append(d)
        elif ratio >= 1.0 or d["last_contact_days"] >= 10:
            at_risk.append(d)
        else:
            on_track.append(d)
    return on_track, at_risk, stalled
```

### `_total_value`

```python
def _total_value(deals):
    """Sum opportunity values."""
    return sum(d["value"] for d in deals)
```

### `_avg_days_stalled`

```python
def _avg_days_stalled(deals):
    """Average days in stage beyond benchmark for a list of deals."""
    if not deals:
        return 0
    excess = []
    for d in deals:
        benchmark = _STAGE_BENCHMARKS.get(d["stage"], 14)
        excess.append(d["days_in_stage"] - benchmark)
    return round(sum(excess) / len(excess))
```

### `_blocker_summary`

```python
def _blocker_summary(stalled):
    """Group stalled deals by blocker type and count."""
    counts = {}
    for d in stalled:
        b = d.get("root_cause", d["blocker"])
        label = {
            "missing_exec_sponsor": "missing exec sponsor",
            "competitor_eval": "competitor eval",
            "budget_pending": "budget pending",
        }.get(b, b.replace("_", " "))
        counts[label] = counts.get(label, 0) + 1
    return counts
```

### `_deals_by_owner`

```python
def _deals_by_owner(deals):
    """Group deals by rep name."""
    grouped = {}
    for d in deals:
        grouped.setdefault(d["owner"], []).append(d)
    return grouped
```

### `_quick_wins`

```python
def _quick_wins():
    """Deals in Contract stage with recent contact — near close."""
    return [d for d in _active_pipeline()
            if d["stage"] == "Contract" and d["last_contact_days"] <= 3]
```

### `_deal`

```python
def _deal(deal_id):
    """The pipeline record with this id, or None."""
    for d in _PIPELINE:
        if d["id"] == deal_id:
            return d
    return None
```

### `_acceleration_opportunities`

```python
def _acceleration_opportunities():
    """Deals each acceleration lever can pull forward (exec alignment, contract fast-track, proof-of-value)."""
    groups = []
    for lever in _ACCELERATION:
        groups.append([_deal(i) for i in lever["deals"]])
    return groups[0], groups[1], groups[2]
```

### `_short`

```python
def _short(d):
    """Display name used in summaries ('Global Mfg')."""
    return _SHORT_NAMES.get(d["id"], d["name"].split()[0])
```

### `_select_deals`

```python
def _select_deals(deals, query):
    """Stalled deals for a named selection (see _DEAL_SETS); the top two by value when empty; none when unknown."""
    ranked = sorted(deals, key=lambda x: -x["value"])
    if not query:
        return ranked[:2]
    wanted = _DEAL_SETS.get(query, [])
    return [d for d in ranked if d["id"] in wanted]
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### DP-01 — `pipeline_health`

- Persona: Sales Director
- Locked prompt: Which opportunities need attention in the synthetic pipeline, and what evidence should I review before changing the forecast?
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Pipeline Health Summary**

Analyzed **$18M** pipeline (47 deals) - **12 deals stalled** ($4.2M at risk)

| Status | Deals | Value |
|--------|-------|-------|
| On Track | 28 | $9.8M |
| At Risk | 7 | $4.0M |
| Stalled | 12 | $4.2M |

**Top Stalled:** TechCorp ($890K, 34 days), Global Mfg ($720K, 28 days), Apex Financial ($580K, 25 days)

**Root Causes:** 5 missing exec sponsor, 4 competitor eval, 3 budget pending

Synthetic source model: [Salesforce + Activity Analytics]

**Next step:** Want details on the top stalled deals?

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-02 — `stalled_deals`

- Persona: Account Executive
- Locked prompt: What blocker evidence explains the loss of momentum on our two largest stalled synthetic deals?
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Stalled Deal Deep-Dive (2 of 12 stalled deals, $4.2M at risk overall)**

**TechCorp Industries ($890K):** Champion went silent 18 days ago, new CFO reviewing all purchases -> Re-engage via different stakeholder, prepare CFO business case

| Factor | Status |
|--------|--------|
| Stage | Proposal |
| Days stalled | 34 (2.1x benchmark of 16 days) |
| Deal age | 96 days |
| Last contact | 18 days ago |
| Champion | VP IT - Mark Reynolds (Silent) |
| Blocker | Executive Change |

**Diagnosis:** Champion went silent 18 days ago, new CFO reviewing all purchases

---

**Global Manufacturing ($720K):** Champion active but legal review blocking contract -> Offer pre-approved template, escalate with legal concession

| Factor | Status |
|--------|--------|
| Stage | Negotiation |
| Days stalled | 28 (2.3x benchmark of 12 days) |
| Deal age | 88 days |
| Last contact | 5 days ago |
| Champion | Dir. Ops - Rachel Green (Active frustrated) |
| Blocker | Legal Review |

**Diagnosis:** Champion active but legal review blocking contract

**Velocity Comparison:** Both significantly over your 45-day avg close time.

Synthetic source model: [CRM + Email Analytics + Meeting Logs]

**Next step:** Generate action plans?

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-03 — `action_plans`

- Persona: Account Executive
- Locked prompt: Draft reviewable intervention plans for our two largest stalled synthetic deals, but do not assign work or contact anyone.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Action Plans — 2 Stalled Deals (drafts for your review)**

- **TechCorp:** Research CFO -> Call VP IT for intro -> Send CFO ROI analysis -> VP-to-CFO outreach
- **Global Mfg:** Call champion -> Send pre-approved template -> Offer 30-day out clause -> Legal-to-legal call

**Suggested owners:** Sarah Kim (TechCorp exec alignment), Legal fast-track (Global)
**Target:** Both back on track within 10 days

---

**TechCorp Industries — $890,000 (Proposal)**

**Next steps:**
1. Research CFO
2. Call VP IT for intro
3. Send CFO ROI analysis
4. VP-to-CFO outreach

**Week 2:**
- Schedule executive meeting with business case
- Re-present proposal with finance lens
- Establish new champion relationship

**Suggested Resource:** Sarah Kim (TechCorp exec alignment)
**Owner:** Mike Chen
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Global Manufacturing — $720,000 (Negotiation)**

**Next steps:**
1. Call champion
2. Send pre-approved template
3. Offer 30-day out clause
4. Legal-to-legal call

**Week 2:**
- Follow up on outstanding redline items
- Escalate any remaining blockers to VP Legal

**Suggested Resource:** Legal fast-track (Global)
**Owner:** Lisa Torres
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

Synthetic source model: [Sales Playbook + Win Patterns]

**Next step:** See the full pipeline acceleration plan?

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-04 — `acceleration`

- Persona: Sales Director
- Locked prompt: Which synthetic timing options could move pipeline review forward without turning scenario value into a forecast commitment?
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Pipeline Acceleration Strategy**

**$6.8M** can be accelerated with targeted actions:

| Action | Deals Impacted | Value | Days Saved |
|--------|----------------|-------|------------|
| Exec alignment | 7 | $3.2M | 12 days |
| Contract fast-track | 2 | $1.8M | 8 days |
| Proof-of-value | 4 | $1.8M | 15 days |

**Quick Wins This Week:** DataFlow $340K (awaiting sig), Summit $280K (Friday approval), Tech Dynamics $190K (in DocuSign) (total $810K)

**Forecast Impact:** +$2.4M to Q4 commit

**Rep-Level Actions:**

| Rep | Stalled Deals | Priority Action |
|-----|---------------|----------------|
| Mike Chen | 3 | ROI business cases |
| Lisa Torres | 2 | Contract negotiations |
| James Park | 3 | Re-engagement campaign |
| Sarah Kim | 2 | ROI business cases |
| Ryan Davis | 2 | ROI business cases |

**Synthetic Scenario:** The +$2.4M Q4 figure is planning evidence for your review; it is not a forecast commitment.

Synthetic source model: [Pipeline Analytics + Historical Patterns]

**Next step:** Assign tasks to the team?

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-05 — `assign_tasks`

- Persona: Sales Director
- Locked prompt: Map candidate follow-up work to the synthetic rep capacity for my review; do not create tasks or alerts.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Draft Task Assignment Plan**

**21** candidate tasks mapped across **4** reps, ready for you to assign.

| Rep | Tasks | Deadline | Focus |
|-----|-------|----------|-------|
| Mike Chen | 6 | This week | TechCorp re-engagement and exec introductions |
| Lisa Torres | 4 | 5 days | Global Manufacturing contract fast-track |
| James Park | 8 | 7 days | Apex Financial proof-of-value and competitive positioning |
| Sarah Kim | 3 | 10 days | TechCorp exec alignment (CFO business case) |

**Proposed Tracking (ready for you to turn on):**
- Daily alerts in Microsoft Teams for overdue tasks
- Stage change notifications
- 7-day stall warning (vs 21)

**Targets:** Reduce stall time to 10 days, move $4.2M back to active, +$2.4M Q4 commit

Synthetic source model: [Salesforce + Task Management]

**Next step:** Generate summary?

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-06 — `executive_summary`

- Persona: Sales Director
- Locked prompt: Give me a leadership-ready summary of the synthetic pipeline findings and the decisions that still require human review.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Pipeline Acceleration Program — Executive Summary**

| Result | Value |
|--------|-------|
| Pipeline analyzed | $18M (47 deals) |
| Stalled identified | 12 deals ($4.2M) |
| Tasks drafted | 21 actions |
| Quick wins | $810K this week |
| Acceleration opportunity | $6.8M |

**Synthetic Planning Targets:** Stall time 21 -> 10 days, +$2.4M Q4 commit, pipeline health 60% -> 78%

Your $4.2M in stalled deals now have draft action plans and a proposed tracking setup with a 7-day early warning, ready for your approval.

Synthetic source model: [All Pipeline Systems]

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

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
