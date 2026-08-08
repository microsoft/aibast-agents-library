# Deal Progression Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `pipeline_health` | Which opportunities need attention in the synthetic pipeline, and what evidence should I review before changing the forecast? | `Pipeline Health Summary`; `Evidence boundary` |
| `stalled_deals` | Which synthetic deals have genuinely stalled, and what blocker evidence explains the loss of momentum? | `Stalled Deal Deep-Dive`; `Diagnosis`; `Evidence boundary` |
| `action_plans` | Draft reviewable intervention plans for the stalled synthetic deals, but do not assign work or contact anyone. | `Action Plans`; `Planning Objective`; `Evidence boundary` |
| `acceleration` | Which synthetic timing options could move pipeline review forward without turning scenario value into a forecast commitment? | `Pipeline Acceleration Strategy`; `Synthetic Scenario`; `Evidence boundary` |
| `assign_tasks` | Map candidate follow-up work to the synthetic rep capacity for my review; do not create tasks or alerts. | `Draft Task Assignment Plan`; `candidate tasks`; `Evidence boundary` |
| `executive_summary` | Give me a leadership-ready summary of the synthetic pipeline findings and the decisions that still require human review. | `Executive Summary`; `Synthetic Planning Targets`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

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
        b = d["blocker"]
        label = {
            "executive_change": "Missing executive sponsor",
            "legal_review": "Legal / contract review",
            "competitor_eval": "Competitor evaluation ongoing",
            "budget_hold": "Budget approval pending",
            "no_champion": "No internal champion",
        }.get(b, b)
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

### `_acceleration_opportunities`

```python
def _acceleration_opportunities():
    """Identify deals that can be pulled forward by intervention type."""
    active = _active_pipeline()
    exec_align = [d for d in active if d["stage"] in ("Proposal", "Negotiation")
                  and d["blocker"] in ("executive_change", "no_champion", "stakeholder_alignment", "none")
                  and d["days_in_stage"] >= 5]
    contract_fast = [d for d in active if d["blocker"] in ("legal_review", "procurement_process")
                     or d["stage"] == "Contract"]
    pov_offer = [d for d in active if d["blocker"] in ("competitor_eval", "technical_validation", "timeline_uncertainty")
                 or (d["stage"] == "Discovery" and d["days_in_stage"] >= 8)]
    return exec_align, contract_fast, pov_offer
```

### `_rep_capacity`

```python
def _rep_capacity():
    """Calculate rep capacity and stalled deal load."""
    _, _, stalled = _classify_deals()
    owner_stalled = _deals_by_owner(stalled)
    result = []
    for rep in _REPS:
        rep_stalled = owner_stalled.get(rep["name"], [])
        result.append({
            "name": rep["name"],
            "title": rep["title"],
            "active_deals": rep["active_deals"],
            "capacity": rep["capacity"],
            "available_slots": rep["capacity"] - rep["active_deals"],
            "stalled_count": len(rep_stalled),
            "stalled_value": _total_value(rep_stalled),
            "specialty": rep["specialty"],
        })
    return result
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### DP-01 — `pipeline_health`

- Persona: Sales Director
- Locked prompt: Which opportunities need attention in the synthetic pipeline, and what evidence should I review before changing the forecast?
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Pipeline Health Summary**

Analyzed **$16.2M** pipeline across **43** active opportunities.

| Status | Deals | Value | Avg Days in Stage |
|--------|-------|-------|-------------------|
| On Track | 24 | $8.3M | within benchmark |
| At Risk | 8 | $3.6M | +2 days over |
| Stalled | 11 | $4.2M | avg 23 days |

**Critical Stalled Deals (top 4 by value):**

1. **TechCorp Industries** — $890,000 — 34 days in Proposal
2. **Global Manufacturing** — $720,000 — 28 days in Negotiation
3. **Apex Financial** — $580,000 — 25 days in Discovery
4. **Metro Healthcare** — $440,000 — 22 days in Proposal

**Root Cause Analysis:**
- 3 deals: Competitor evaluation ongoing
- 2 deals: Missing executive sponsor
- 2 deals: Legal / contract review
- 2 deals: Budget approval pending
- 2 deals: No internal champion

Synthetic source model: [Salesforce + Activity Analytics]
Agents: PipelineAnalyticsAgent, StalledDealDetectionAgent

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-02 — `stalled_deals`

- Persona: Account Executive
- Locked prompt: Which synthetic deals have genuinely stalled, and what blocker evidence explains the loss of momentum?
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Stalled Deal Deep-Dive (11 deals, $4.2M at risk)**

**TechCorp Industries — $890,000**

| Factor | Status |
|--------|--------|
| Stage | Proposal |
| Days stalled | 34 (2.1x benchmark of 16 days) |
| Last contact | 18 days ago |
| Champion | VP IT - Mark Reynolds (Silent) |
| Blocker | Executive Change |

**Diagnosis:** Champion disengaged, economic buyer changed

---

**Global Manufacturing — $720,000**

| Factor | Status |
|--------|--------|
| Stage | Negotiation |
| Days stalled | 28 (2.3x benchmark of 12 days) |
| Last contact | 5 days ago |
| Champion | Dir. Ops - Rachel Green (Active frustrated) |
| Blocker | Legal Review |

**Diagnosis:** Process bottleneck, not relationship issue

---

**Apex Financial — $580,000**

| Factor | Status |
|--------|--------|
| Stage | Discovery |
| Days stalled | 25 (1.4x benchmark of 18 days) |
| Last contact | 12 days ago |
| Champion | CTO - David Liu (Disengaged) |
| Blocker | Competitor Eval |

**Diagnosis:** Active competitive evaluation in progress

---

**Metro Healthcare — $440,000**

| Factor | Status |
|--------|--------|
| Stage | Proposal |
| Days stalled | 22 (1.4x benchmark of 16 days) |
| Last contact | 9 days ago |
| Champion | VP Digital - Sandra Patel (Active) |
| Blocker | Budget Hold |

**Diagnosis:** Budget approval stalled or deprioritized

---

**Pinnacle Logistics — $360,000**

| Factor | Status |
|--------|--------|
| Stage | Qualification |
| Days stalled | 20 (1.4x benchmark of 14 days) |
| Last contact | 14 days ago |
| Champion | IT Dir - Tom Bradley (Silent) |
| Blocker | No Champion |

**Diagnosis:** No internal champion identified or engaged

---

**Summit Retail Group — $310,000**

| Factor | Status |
|--------|--------|
| Stage | Discovery |
| Days stalled | 24 (1.3x benchmark of 18 days) |
| Last contact | 11 days ago |
| Champion | COO - Angela Morris (Lukewarm) |
| Blocker | Competitor Eval |

**Diagnosis:** Active competitive evaluation in progress

---

**Vanguard Energy — $270,000**

| Factor | Status |
|--------|--------|
| Stage | Proposal |
| Days stalled | 21 (1.3x benchmark of 16 days) |
| Last contact | 16 days ago |
| Champion | VP Eng - Carlos Reyes (Silent) |
| Blocker | Executive Change |

**Diagnosis:** Champion disengaged, economic buyer changed

---

**Cascade Media — $220,000**

| Factor | Status |
|--------|--------|
| Stage | Negotiation |
| Days stalled | 18 (1.5x benchmark of 12 days) |
| Last contact | 7 days ago |
| Champion | Dir. Tech - Nina Chow (Active) |
| Blocker | Legal Review |

**Diagnosis:** Process bottleneck, not relationship issue

---

**Atlas Construction — $180,000**

| Factor | Status |
|--------|--------|
| Stage | Qualification |
| Days stalled | 19 (1.4x benchmark of 14 days) |
| Last contact | 20 days ago |
| Champion | None identified (None) |
| Blocker | No Champion |

**Diagnosis:** No internal champion identified or engaged

---

**Sterling Insurance — $130,000**

| Factor | Status |
|--------|--------|
| Stage | Proposal |
| Days stalled | 20 (1.2x benchmark of 16 days) |
| Last contact | 15 days ago |
| Champion | CIO - Barbara Wells (Lukewarm) |
| Blocker | Competitor Eval |

**Diagnosis:** Active competitive evaluation in progress

---

**Redwood Education — $110,000**

| Factor | Status |
|--------|--------|
| Stage | Qualification |
| Days stalled | 18 (1.3x benchmark of 14 days) |
| Last contact | 10 days ago |
| Champion | Dir. IT - Paul Simmons (Active) |
| Blocker | Budget Hold |

**Diagnosis:** Budget approval stalled or deprioritized

**Velocity Comparison:** Average deal closes in 45 days — stalled deals average 23 days in current stage alone.

Synthetic source model: [CRM + Email Analytics + Meeting Logs]
Agents: DealDiagnosticsAgent, StalledDealDetectionAgent

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-03 — `action_plans`

- Persona: Account Executive
- Locked prompt: Draft reviewable intervention plans for the stalled synthetic deals, but do not assign work or contact anyone.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Action Plans — 11 Stalled Deals**

Total tasks generated: **73**

**TechCorp Industries — $890,000 (Proposal)**

**Week 1:**
- Day 1: Research new executive background (LinkedIn, news)
- Day 2: Call existing champion — acknowledge gap, request intro
- Day 3: Send executive-tailored ROI analysis
- Day 5: Executive sponsor outreach (your VP to their exec)

**Week 2:**
- Schedule executive meeting with business case
- Re-present proposal with finance lens
- Establish new champion relationship

**Suggested Resource:** Exec Alignment Specialist
**Owner:** Mike Chen
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Global Manufacturing — $720,000 (Negotiation)**

**Week 1:**
- Today: Call champion — acknowledge legal delay
- Tomorrow: Prepare the synthetic contract template for authorized legal and seller review
- Day 3: Offer 30-day out clause to reduce perceived risk
- Day 5: Legal-to-legal call to resolve remaining items

**Week 2:**
- Follow up on outstanding redline items
- Escalate any remaining blockers to VP Legal

**Suggested Resource:** Legal Team Fast-Track Review
**Owner:** Lisa Torres
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Apex Financial — $580,000 (Discovery)**

**Week 1:**
- Day 1: Request competitive landscape details from champion
- Day 2: Prepare head-to-head comparison deck
- Day 3: Schedule technical deep-dive vs competitor capabilities
- Day 5: Deliver customer reference calls in same vertical

**Week 2:**
- Provide proof-of-value pilot offer
- Executive peer reference call
- Submit best-and-final with differentiated terms

**Suggested Resource:** Competitive Intelligence Team
**Owner:** James Park
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Metro Healthcare — $440,000 (Proposal)**

**Week 1:**
- Day 1: Confirm budget timeline with champion
- Day 2: Build CFO-ready business case with 3-year TCO
- Day 3: Offer phased implementation to reduce upfront cost
- Day 5: Provide flexible payment terms proposal

**Week 2:**
- Schedule CFO meeting with ROI walkthrough
- Share peer company case study with hard ROI numbers

**Suggested Resource:** Value Engineering Team
**Owner:** Mike Chen
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Pinnacle Logistics — $360,000 (Qualification)**

**Week 1:**
- Day 1: Map org chart and identify 3 potential champions
- Day 2: Multi-thread outreach via LinkedIn and email
- Day 3: Offer executive briefing or lunch-and-learn
- Day 5: Ask existing contacts for warm introductions

**Week 2:**
- Host on-site workshop to build relationships
- Provide industry insights to create value before selling
- Identify and cultivate power sponsor

**Suggested Resource:** Senior Ae For Relationship Building
**Owner:** James Park
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Summit Retail Group — $310,000 (Discovery)**

**Week 1:**
- Day 1: Request competitive landscape details from champion
- Day 2: Prepare head-to-head comparison deck
- Day 3: Schedule technical deep-dive vs competitor capabilities
- Day 5: Deliver customer reference calls in same vertical

**Week 2:**
- Provide proof-of-value pilot offer
- Executive peer reference call
- Submit best-and-final with differentiated terms

**Suggested Resource:** Competitive Intelligence Team
**Owner:** Sarah Kim
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Vanguard Energy — $270,000 (Proposal)**

**Week 1:**
- Day 1: Research new executive background (LinkedIn, news)
- Day 2: Call existing champion — acknowledge gap, request intro
- Day 3: Send executive-tailored ROI analysis
- Day 5: Executive sponsor outreach (your VP to their exec)

**Week 2:**
- Schedule executive meeting with business case
- Re-present proposal with finance lens
- Establish new champion relationship

**Suggested Resource:** Exec Alignment Specialist
**Owner:** Ryan Davis
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Cascade Media — $220,000 (Negotiation)**

**Week 1:**
- Today: Call champion — acknowledge legal delay
- Tomorrow: Prepare the synthetic contract template for authorized legal and seller review
- Day 3: Offer 30-day out clause to reduce perceived risk
- Day 5: Legal-to-legal call to resolve remaining items

**Week 2:**
- Follow up on outstanding redline items
- Escalate any remaining blockers to VP Legal

**Suggested Resource:** Legal Team Fast-Track Review
**Owner:** Lisa Torres
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Atlas Construction — $180,000 (Qualification)**

**Week 1:**
- Day 1: Map org chart and identify 3 potential champions
- Day 2: Multi-thread outreach via LinkedIn and email
- Day 3: Offer executive briefing or lunch-and-learn
- Day 5: Ask existing contacts for warm introductions

**Week 2:**
- Host on-site workshop to build relationships
- Provide industry insights to create value before selling
- Identify and cultivate power sponsor

**Suggested Resource:** Senior Ae For Relationship Building
**Owner:** James Park
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Sterling Insurance — $130,000 (Proposal)**

**Week 1:**
- Day 1: Request competitive landscape details from champion
- Day 2: Prepare head-to-head comparison deck
- Day 3: Schedule technical deep-dive vs competitor capabilities
- Day 5: Deliver customer reference calls in same vertical

**Week 2:**
- Provide proof-of-value pilot offer
- Executive peer reference call
- Submit best-and-final with differentiated terms

**Suggested Resource:** Competitive Intelligence Team
**Owner:** Mike Chen
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

---

**Redwood Education — $110,000 (Qualification)**

**Week 1:**
- Day 1: Confirm budget timeline with champion
- Day 2: Build CFO-ready business case with 3-year TCO
- Day 3: Offer phased implementation to reduce upfront cost
- Day 5: Provide flexible payment terms proposal

**Week 2:**
- Schedule CFO meeting with ROI walkthrough
- Share peer company case study with hard ROI numbers

**Suggested Resource:** Value Engineering Team
**Owner:** Ryan Davis
**Planning Objective:** Evaluate whether the deal can return to active review within 10 days

Synthetic source model: [Sales Playbook + Win Patterns]
Agents: NextBestActionAgent

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-04 — `acceleration`

- Persona: Sales Director
- Locked prompt: Which synthetic timing options could move pipeline review forward without turning scenario value into a forecast commitment?
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Pipeline Acceleration Strategy**

Identified **$12.5M** that can be pulled forward with targeted interventions.

**Acceleration Opportunities:**

| Action | Deals Impacted | Value | Days Saved |
|--------|----------------|-------|------------|
| Executive alignment | 12 | $5.1M | 12 days avg |
| Contract fast-track | 7 | $2.9M | 8 days avg |
| Proof-of-value offer | 12 | $4.5M | 15 days avg |

**Quick Wins (Close This Week):**
- **DataFlow Corp:** $340,000 — verbal commit, awaiting signature
- **Summit Industries:** $280,000 — final approval pending
- **Tech Dynamics:** $190,000 — verbal commit, awaiting signature

Quick-win total: **$0.8M**

**Rep-Level Actions:**

| Rep | Stalled Deals | Priority Action |
|-----|---------------|----------------|
| Mike Chen | 3 | Executive introductions |
| Lisa Torres | 2 | Contract negotiations |
| James Park | 3 | Re-engagement campaign |
| Sarah Kim | 1 | Competitive positioning |
| Ryan Davis | 2 | Executive introductions |

**Synthetic Scenario:** The planning model illustrates **$2.4M** of possible Q4 timing movement; it is not a forecast commitment.

Synthetic source model: [Pipeline Analytics + Historical Patterns]
Agents: PipelineAccelerationAgent

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-05 — `assign_tasks`

- Persona: Sales Director
- Locked prompt: Map candidate follow-up work to the synthetic rep capacity for my review; do not create tasks or alerts.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Draft Task Assignment Plan**

**73** candidate tasks mapped across **5** reps for manager review.

| Rep | Tasks | Deadline | Deals |
|-----|-------|----------|-------|
| Mike Chen | 20 tasks | Next 6 days | 3 stalled |
| Lisa Torres | 12 tasks | This week | 2 stalled |
| James Park | 21 tasks | Next 6 days | 3 stalled |
| Sarah Kim | 7 tasks | This week | 1 stalled |
| Ryan Davis | 13 tasks | This week | 2 stalled |

**Proposed Monitoring (not configured):**
- Draft daily alert rule for overdue tasks
- Draft deal-stage change notification rule
- Draft weekly pipeline velocity report
- Draft stall warning at 7 days (vs current 21)

**Suggested Accountability Cadence:**
- Daily: Review candidate task reminders
- Wednesday: Consider a pipeline review meeting (30 min)
- Friday: Review a draft deal progression scorecard

**Synthetic Planning Measures:**
- Target: Reduce avg stall time from 21 to 10 days
- Goal: Move $4.2M stalled back to active
- Forecast: Add $2.4M to Q4 commit

Synthetic source model: [Salesforce + Task Management]
Agents: TaskAssignmentAgent

**Evidence boundary:** Exact names, dates, counts, values, scores, percentages, and projections are synthetic planning evidence. This read-only output did not write CRM data, assign tasks, send alerts, approve pricing, change a forecast, or contact a customer.

### DP-06 — `executive_summary`

- Persona: Sales Director
- Locked prompt: Give me a leadership-ready summary of the synthetic pipeline findings and the decisions that still require human review.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Pipeline Acceleration Program — Executive Summary**

| Analysis | Result |
|----------|--------|
| Pipeline analyzed | $16.2M across 43 deals |
| Stalled identified | 11 deals, $4.2M at risk |
| Root causes | competitor evaluation ongoing, missing executive sponsor, legal / contract review |
| Actions drafted | 73 candidate tasks for review |
| Acceleration target | $7.9M can be pulled forward |

**Immediate Impact:**
- $810K in quick wins closing this week
- TechCorp Industries ($890,000) draft action plan prepared
- Global Manufacturing ($720,000) draft action plan prepared
- All 11 stalled deals have candidate intervention plans

**Process Improvements:**
- Early warning at 7 days (was 21)
- Candidate daily task-tracking rule
- Suggested weekly velocity review
- Draft rep accountability scorecard

**Synthetic Planning Targets:**
- Reduce stall time: 21 days to 10 days
- Q4 forecast improvement: +$2.4M commit
- Pipeline health: 74% on-track (from 56%)

Synthetic source model: [All Pipeline Systems]
Agents: PipelineReportAgent (orchestrating all agents)

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
