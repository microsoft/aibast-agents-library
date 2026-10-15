# Sales Qualification Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `score_leads` | Which bundled synthetic leads should my team review first, and why did they score that way? | `Lead Qualification Summary`; `Top 3 Hot Leads`; `Hot (80+)`; `Evidence boundary` |
| `bant_analysis` | Show the BANT evidence and missing qualification details for the strongest synthetic leads. | `BANT Analysis`; `Strongest Engagement Signals`; `$200K`; `Evidence boundary` |
| `create_outreach` | Draft outreach ideas for the synthetic hot leads, but do not send or schedule any communication. | `Personalized Outreach`; `Draft Sequence Cadence`; `Connecting 12 data sources in weeks`; `Evidence boundary` |
| `assign_leads` | Recommend synthetic lead routing for manager review without assigning CRM owners. | `Recommended Lead Routing`; `Handoff Package`; `$470K`; `Evidence boundary` |
| `setup_tracking` | Draft an SLA and escalation plan for the synthetic leads without activating alerts or automations. | `Draft SLA Tracking Plan`; `Targets`; `$800K pipeline`; `Evidence boundary` |
| `qualification_report` | Summarize the synthetic qualified pipeline and clearly label every conversion and value assumption. | `Qualification Report`; `$1.25M`; `Action plan`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

### `_icp_score`

```python
def _icp_score(lead):
    """Compute ICP fit score (0-100) from weighted criteria."""
    # Size score
    emp = lead["employees"]
    if _ICP["ideal_employees_min"] <= emp <= _ICP["ideal_employees_max"]:
        size_score = 100
    elif emp < _ICP["ideal_employees_min"]:
        size_score = max(10, int((emp / _ICP["ideal_employees_min"]) * 100))
    else:
        size_score = max(40, 100 - int((emp - _ICP["ideal_employees_max"]) / 200))

    # Industry score
    industry_score = 100 if lead["industry"] in _ICP["ideal_industries"] else 30

    # Tech fit score
    overlap = len(set(lead["tech_stack"]) & set(_ICP["ideal_tech"]))
    tech_score = min(100, int((overlap / max(len(_ICP["ideal_tech"]), 1)) * 150))

    # Budget score
    budget_score = int(_ICP["budget_tiers"].get(lead["budget"], 0.2) * 100)

    # Authority score
    authority_score = int(_ICP["authority_tiers"].get(lead["authority_level"], 0.3) * 100)

    total = (
        size_score * _ICP["size_weight"]
        + industry_score * _ICP["industry_weight"]
        + tech_score * _ICP["tech_fit_weight"]
        + budget_score * _ICP["budget_weight"]
        + authority_score * _ICP["authority_weight"]
    )
    return min(100, max(0, int(total)))
```

### `_bant_scores`

```python
def _bant_scores(lead):
    """Score each BANT dimension independently (0-100)."""
    budget_map = {"confirmed": 95, "planned": 70, "exploring": 40, "tbd": 15}
    b = budget_map.get(lead["budget"], 15)

    authority_map = {"C-Level": 95, "VP": 80, "Director": 60, "Manager": 40, "Individual": 20}
    a = authority_map.get(lead["authority_level"], 20)

    n = min(100, 50 + len(lead["need"]) // 3 + len(lead["engagement_signals"]) * 8)

    timeline_val = lead["timeline"].upper()
    if "60" in timeline_val or "Q1" in timeline_val:
        t = 90
    elif "90" in timeline_val:
        t = 70
    elif "Q2" in timeline_val:
        t = 55
    else:
        t = 25

    composite = int(b * 0.30 + a * 0.25 + n * 0.25 + t * 0.20)
    return {"budget": b, "authority": a, "need": n, "timeline": t, "composite": composite}
```

### `_tier_lead`

```python
def _tier_lead(icp_score, bant_composite, intent_score):
    """Assign tier from the weighted ICP, BANT and intent scores: Hot 80+, Warm 60-79, Nurture below 60."""
    w = _SCORE_WEIGHTS
    combined = int(round(icp_score * w["icp"] + bant_composite * w["bant"] + intent_score * w["intent"]))
    if combined >= _TIER_THRESHOLDS["Hot"]:
        return "Hot", combined
    if combined >= _TIER_THRESHOLDS["Warm"]:
        return "Warm", combined
    return "Nurture", combined
```

### `_match_ae`

```python
def _match_ae(lead):
    """Route by expertise: healthcare, manufacturing and financial services specialists; technology and SaaS
    accounts of 300+ employees to Enterprise, smaller SaaS to Mid-Market."""
    industry = lead["industry"]
    if industry == "Healthcare":
        specialty = "Healthcare"
    elif industry == "Manufacturing":
        specialty = "Manufacturing"
    elif industry == "Financial Services":
        specialty = "Financial Services"
    elif lead["employees"] >= 300:
        specialty = "Enterprise"
    else:
        specialty = "Mid-Market SaaS"
    for ae in _AE_TEAM:
        if ae["specialty"] == specialty:
            return ae
    return _AE_TEAM[0]
```

### `_money_k`

```python
def _money_k(value):
    if value >= 1000000:
        return f"${value / 1000000:.2f}M"
    return f"${value // 1000}K"
```

### `_budget_label`

```python
def _budget_label(lead):
    if lead["budget"] == "tbd":
        return f"TBD (est. {_money_k(lead['budget_usd'])})"
    return _money_k(lead["budget_usd"])
```

### `_short_title`

```python
def _short_title(lead):
    return lead["title"].replace("Engineering", "Eng").replace("Director of IT", "Director")
```

### `_generate_outreach`

```python
def _generate_outreach(lead, tier):
    """Personalized outreach elements from the playbook (hot) or lead context."""
    first_name = lead["contact_name"].split()[0]
    play = _HOT_PLAYBOOK.get(lead["id"])
    if play:
        return {"subject": f"{first_name}, {play['angle'].lower()}", "hook": play["angle"], "cta": f"{play['cta']} CTA"}
    need_short = lead["need"][:60]
    if tier == "Warm":
        return {"subject": f"{lead['company']}: {need_short[:40]}",
                "hook": f"Teams like yours at {lead['company']} are solving {need_short.lower()}.",
                "cta": "Quick call to explore fit"}
    return {"subject": f"Resource: solving {need_short[:35].lower()} at scale",
            "hook": f"Our latest guide on {lead['industry'].lower()} data challenges.",
            "cta": "Reply for a walkthrough"}
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### SQ-01 — `score_leads`

- Persona: Sales Manager
- Locked prompt: Which bundled synthetic leads should my team review first, and why did they score that way?
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Lead Qualification Summary — 45 Leads Scored**

Analyzed 45 leads with ICP scoring and BANT criteria plus intent data (score = 35% ICP fit + 25% BANT + 40% intent).

| Tier | Leads | Recommended Action |
|---|---|---|
| Hot (80+) | 8 | AE handoff |
| Warm (60-79) | 15 | SDR call |
| Nurture (<60) | 22 | Email sequence |

**Top 3 Hot Leads:**
- **TechFlow Industries** (94) - VP Eng, active eval
- **Meridian Corp** (91) - CTO, budget approved
- **Apex Solutions** (88) - Competitor displacement

**Enrichment (firmographic, technographic, intent):**

| Company | Employees | Industry | Tech Stack | Intent |
|---|---|---|---|---|
| TechFlow Industries | 520 | Technology | AWS, Snowflake, Kubernetes | 98 |
| Meridian Corp | 1,200 | Healthcare | Azure, Salesforce, Databricks | 88 |
| Apex Solutions | 780 | SaaS | AWS, Kubernetes, Salesforce | 98 |

Next: BANT analysis on the hot leads.

Synthetic source model: [CRM + ZoomInfo + 6sense Intent Data]
Agents: LeadEnrichmentAgent, ICPMatchingAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-02 — `bant_analysis`

- Persona: Business Development Rep.
- Locked prompt: Show the BANT evidence and missing qualification details for the strongest synthetic leads.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**BANT Analysis — Top 5 Hot Leads**

| Lead | Budget | Authority | Need | Timeline | BANT Score |
|---|---|---|---|---|---|
| TechFlow Industries | $200K | VP Eng | Consolidate 12 data sources into unified pipe | Q1 | 89 |
| Meridian Corp | $150K | CTO | Replace legacy EHR integration layer | 60 days | 89 |
| Apex Solutions | $180K | Director | Displace incumbent vendor, contract ending Q1 | Q1 | 76 |
| DataCorp Analytics | $90K | IT Manager | Improve data pipeline efficiency by 40% | Q2 | 69 |
| Summit Technologies | TBD (est. $40K) | VP Operations | Scale production monitoring across 8 plants | 60 days | 62 |

**Strongest Engagement Signals:**
- **TechFlow Industries**: Demo booth visited twice
- **Meridian Corp**: CTO asked technical questions
- **Apex Solutions**: Competitor contract ending

**Risk Flags:**
- DataCorp Analytics: Needs a decision maker (IT Manager)
- Summit Technologies: Budget TBD

Synthetic source model: [CRM + Booth Interactions + Intent Data]
Agents: BANTScoringAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-03 — `create_outreach`

- Persona: Business Development Rep.
- Locked prompt: Draft outreach ideas for the synthetic hot leads, but do not send or schedule any communication.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Personalized Outreach — 8 Hot Leads**

Personalized outreach drafted for all 8 hot leads.

| Lead | Contact | Personalized Hook | CTA |
|---|---|---|---|
| TechFlow Industries | Sarah Nguyen, VP Engineering | "Connecting 12 data sources in weeks" | 15-min deep dive CTA |
| Meridian Corp | James Walker, CTO | "60-day migration playbook attached" | Stack discussion CTA |
| Apex Solutions | Diana Reyes, Director of IT | "40% of [Competitor] customers switched" | Comparison call CTA |
| DataCorp Analytics | Emily Tran, IT Manager | "40% faster pipelines on your trial data" | Trial review call CTA |
| Summit Technologies | Robert Kim, VP Operations | "Monitoring 8 plants from one pipeline" | Plant-rollout walkthrough CTA |
| Greenfield Health | Maria Santos, Chief Digital Officer | "One patient record across 14 facilities" | Architecture session CTA |
| Orion Manufacturing | Thomas Park, CTO | "Predictive maintenance from IoT data in 90 days" | Pilot scoping call CTA |
| FusionTech Labs | Derek Johnson, CTO | "Hadoop to cloud-native migration assessment" | Assessment kickoff CTA |

**Draft Sequence Cadence (not activated):** Personalized email today > LinkedIn connection + note day 2 > Value content email day 3 > Phone call day 4
- Today: Personalized email
- Day 2: LinkedIn connection + note
- Day 3: Value content email
- Day 4: Phone call

Next: assign the leads to AEs.

Synthetic source model: [Content Library + Booth Notes + LinkedIn]
Agents: PersonalizedOutreachAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-04 — `assign_leads`

- Persona: Sales Manager
- Locked prompt: Recommend synthetic lead routing for manager review without assigning CRM owners.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Recommended Lead Routing — 8 Hot Leads to 4 AEs**

Leads routed by territory and expertise:

| AE | Leads | Pipeline | Specialty | Capacity |
|---|---|---|---|---|
| Mike Rodriguez | 3 | $470K | Enterprise | 62% |
| Sarah Kim | 2 | $210K | Healthcare | 55% |
| James Chen | 2 | $100K | Manufacturing | 70% |
| Lisa Park | 1 | $20K | Mid-Market SaaS | 48% |

**Assignment Detail:**
- Mike Rodriguez: TechFlow Industries ($200K), Apex Solutions ($180K), DataCorp Analytics ($90K)
- Sarah Kim: Meridian Corp ($150K), Greenfield Health ($60K)
- James Chen: Summit Technologies ($40K), Orion Manufacturing ($60K)
- Lisa Park: FusionTech Labs ($20K)

All AEs under 80% capacity. Handoff packages include BANT summary, booth notes, and email drafts.

Next: set up SLA tracking.

Synthetic source model: [Territory Rules + Capacity Dashboard]
Agents: LeadRoutingAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-05 — `setup_tracking`

- Persona: Sales Manager
- Locked prompt: Draft an SLA and escalation plan for the synthetic leads without activating alerts or automations.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Draft SLA Tracking Plan — 45 Synthetic Leads (ready to activate)**

| Tier | Leads | Response SLA | Escalation |
|---|---|---|---|
| Hot | 8 | 4 hours | Manager alert |
| Warm | 15 | 24 hours | Team alert |
| Nurture | 22 | 48 hours | Auto-sequence |

**Automations to switch on (not activated):** Teams alerts at 2 hr remaining, manager notification if an SLA is missed, CRM stage update suggested when a meeting is booked.

**Targets:** 100% hot contact rate, 40% meeting conversion, $800K pipeline

Next: generate the summary.

Synthetic source model: [SLA Engine + Notification System]
Agents: SLAMonitoringAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-06 — `qualification_report`

- Persona: Account Executive
- Locked prompt: Summarize the synthetic qualified pipeline and clearly label every conversion and value assumption.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Qualification Report — Lead qualification complete**

| Result | Value |
|---|---|
| Leads analyzed | 45 |
| Hot leads | 8 ($800K) |
| Outreach drafted | All 8 hot leads |
| AEs recommended | 4 reps |
| SLA tracking | Plan ready to activate |

**Total pipeline:** $1.25M (Hot $800K + Warm $450K)

**Action plan:** 8 hot leads get AE outreach within 4 hours, 15 warm get SDR calls, 22 nurture enter email sequences.

**Draft Review Queue:** approve the hot-lead outreach drafts and AE routing, then activate the SLA plan.

Synthetic source model: [All Qualification Systems]
Agents: QualificationReportAgent (orchestrating all agents)

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

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
