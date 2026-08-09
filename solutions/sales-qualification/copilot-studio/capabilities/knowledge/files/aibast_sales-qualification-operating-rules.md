# Sales Qualification Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `score_leads` | Which bundled synthetic leads should my team review first, and why did they score that way? | `Lead Qualification Summary`; `Top Hot Leads`; `Evidence boundary` |
| `bant_analysis` | Show the BANT evidence and missing qualification details for the strongest synthetic leads. | `BANT Analysis`; `Strongest Engagement Signals`; `Evidence boundary` |
| `create_outreach` | Draft outreach ideas for the synthetic hot leads, but do not send or schedule any communication. | `Personalized Outreach`; `Draft Sequence Cadence`; `Evidence boundary` |
| `assign_leads` | Recommend synthetic lead routing for manager review without assigning CRM owners. | `Recommended Lead Routing`; `Handoff Package`; `Evidence boundary` |
| `setup_tracking` | Draft an SLA and escalation plan for the synthetic leads without activating alerts or automations. | `Draft SLA Tracking Plan`; `Proposed Monitoring`; `Evidence boundary` |
| `qualification_report` | Summarize the synthetic qualified pipeline and clearly label every conversion and value assumption. | `Qualification Report`; `Synthetic Conversion Assumptions`; `Evidence boundary` |

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
def _tier_lead(icp_score, bant_composite):
    """Assign tier from combined ICP and BANT scores."""
    combined = int(icp_score * 0.55 + bant_composite * 0.45)
    if combined >= 88:
        return "Hot", combined
    elif combined >= 73:
        return "Warm", combined
    elif combined >= 55:
        return "Nurture", combined
    else:
        return "Disqualified", combined
```

### `_match_ae`

```python
def _match_ae(lead, team):
    """Route lead to best AE by specialty keyword match and capacity."""
    industry = lead["industry"].lower()
    best_ae = None
    best_score = -1
    for ae in team:
        spec = ae["specialty"].lower()
        score = 0
        if industry in spec:
            score += 50
        if "enterprise" in spec and lead["employees"] >= 1000:
            score += 20
        elif "mid-market" in spec and lead["employees"] < 1000:
            score += 20
        if "finserv" in spec and "financial" in industry:
            score += 30
        if "tech" in spec and industry in ("technology", "saas"):
            score += 25
        if "health" in spec and "healthcare" in industry:
            score += 30
        if "manufactur" in spec and "manufacturing" in industry:
            score += 30
        capacity_bonus = max(0, (100 - ae["current_capacity_pct"]) // 5)
        score += capacity_bonus
        if score > best_score:
            best_score = score
            best_ae = ae
    return best_ae
```

### `_generate_outreach`

```python
def _generate_outreach(lead, tier, icp_score):
    """Build personalized outreach elements from lead context."""
    company = lead["company"]
    first_name = lead["contact_name"].split()[0]
    need_short = lead["need"][:60]

    if tier == "Hot":
        subject = f"Following up on our {lead['source'].lower()} conversation, {first_name}"
        hook = f'You mentioned "{need_short}" — we have a proven path to solve this in {lead["timeline"]}.'
        cta = "15-minute deep dive this week?"
    elif tier == "Warm":
        subject = f"{company} + DataSync: {need_short[:40]}"
        hook = f"Teams like yours at {company} are solving {need_short.lower()} with our platform."
        cta = "Quick call to explore fit?"
    else:
        subject = f"Resource: solving {need_short[:35].lower()} at scale"
        hook = f"Thought you would find our latest guide on {lead['industry'].lower()} data challenges useful."
        cta = "Reply if you would like a walkthrough."

    return {"subject": subject, "hook": hook, "cta": cta}
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### SQ-01 — `score_leads`

- Persona: Sales Manager
- Locked prompt: Which bundled synthetic leads should my team review first, and why did they score that way?
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Lead Qualification Summary — 45 Leads Scored**

| Tier | Leads | Avg Score | Recommended Action |
|---|---|---|---|
| Hot | 13 | 93/100 | Immediate AE handoff |
| Warm | 11 | 80/100 | SDR qualification call |
| Nurture | 13 | 65/100 | Automated email sequence |
| Disqualified | 8 | 46/100 | Marketing nurture list |

**Top Hot Leads:**
1. **NovaTech Solutions** — Score: 96 — Amanda Torres, CTO, Replace custom ETL with managed platform
2. **Pacific Mutual Insurance** — Score: 96 — Gregory Adams, CIO, Claims processing automation with AI/ML
3. **Nexus Health Network** — Score: 96 — Christina Park, CMIO, Population health analytics across 30 hospitals
4. **Summit Health Partners** — Score: 96 — Lisa Nakamura, Chief Analytics Officer, Enterprise analytics platform for value-based care
5. **Crestline Financial** — Score: 96 — Patricia Adams, Chief Data Officer, Enterprise data mesh architecture implementation

Synthetic source model: [CRM + ZoomInfo + 6sense Intent Data]
Agents: LeadEnrichmentAgent, ICPMatchingAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-02 — `bant_analysis`

- Persona: Business Development Rep.
- Locked prompt: Show the BANT evidence and missing qualification details for the strongest synthetic leads.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**BANT Analysis — Top 8 Hot Leads**

| Lead | Budget | Authority | Need | Timeline | BANT Score |
|---|---|---|---|---|---|
| NovaTech Solutions | Confirmed (95) | C-Level (95) | 87 | 60 days (90) | 92 |
| Pacific Mutual Insurance | Confirmed (95) | C-Level (95) | 87 | Q1 (90) | 92 |
| Nexus Health Network | Confirmed (95) | C-Level (95) | 89 | Q1 (90) | 92 |
| Summit Health Partners | Confirmed (95) | C-Level (95) | 90 | Q1 (90) | 92 |
| Crestline Financial | Confirmed (95) | C-Level (95) | 90 | Q1 (90) | 92 |
| Greenfield Health | Confirmed (95) | C-Level (95) | 90 | Q1 (90) | 92 |
| Orion Manufacturing | Confirmed (95) | C-Level (95) | 89 | Q1 (90) | 92 |
| FusionTech Labs | Confirmed (95) | C-Level (95) | 88 | 60 days (90) | 92 |

**Strongest Engagement Signals:**
- **NovaTech Solutions**: Referral from board member, Requested architecture review, Downloaded migration guide
- **Pacific Mutual Insurance**: 1-on-1 executive meeting, Requested proposal, Site visit scheduled
- **Nexus Health Network**: Executive referral, Requested ROI model, Reviewed case studies

**Risk Flags:**

Synthetic source model: [CRM + Booth Interactions + Intent Data]
Agents: BANTScoringAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-03 — `create_outreach`

- Persona: Business Development Rep.
- Locked prompt: Draft outreach ideas for the synthetic hot leads, but do not send or schedule any communication.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Personalized Outreach — 5 Hot Leads**

**NovaTech Solutions Outreach:**

**Subject:** Following up on our referral conversation, Amanda

**Hook:** "You mentioned "Replace custom ETL with managed platform" — we have a proven path to solve this in 60 days."

**CTA:** 15-minute deep dive this week?

---

**Pacific Mutual Insurance Outreach:**

**Subject:** Following up on our executive event conversation, Gregory

**Hook:** "You mentioned "Claims processing automation with AI/ML" — we have a proven path to solve this in Q1."

**CTA:** 15-minute deep dive this week?

---

**Nexus Health Network Outreach:**

**Subject:** Following up on our referral conversation, Christina

**Hook:** "You mentioned "Population health analytics across 30 hospitals" — we have a proven path to solve this in Q1."

**CTA:** 15-minute deep dive this week?

---

**Summit Health Partners Outreach:**

**Subject:** Following up on our executive event conversation, Lisa

**Hook:** "You mentioned "Enterprise analytics platform for value-based care" — we have a proven path to solve this in Q1."

**CTA:** 15-minute deep dive this week?

---

**Crestline Financial Outreach:**

**Subject:** Following up on our referral conversation, Patricia

**Hook:** "You mentioned "Enterprise data mesh architecture implementation" — we have a proven path to solve this in Q1."

**CTA:** 15-minute deep dive this week?

---

**Draft Sequence Cadence (not activated):**
- Day 0: Personalized email (above)
- Day 1: LinkedIn connection + note
- Day 2: Phone attempt #1
- Day 3: Value content email
- Day 5: Phone attempt #2

Synthetic source model: [Content Library + Booth Notes + LinkedIn]
Agents: PersonalizedOutreachAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-04 — `assign_leads`

- Persona: Sales Manager
- Locked prompt: Recommend synthetic lead routing for manager review without assigning CRM owners.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Recommended Lead Routing — 24 Leads Evaluated**

| AE | Leads | Est. Pipeline | Specialty Match | Capacity |
|---|---|---|---|---|
| Mike Rodriguez | 5 | $384,000 | Enterprise Tech | 62% |
| Sarah Kim | 9 | $8,414,000 | Healthcare / FinServ | 55% |
| James Chen | 2 | $1,460,000 | Manufacturing / Industrial | 70% |
| Lisa Park | 2 | $168,000 | Mid-Market SaaS | 48% |
| David Okafor | 6 | $8,350,000 | Enterprise FinServ | 58% |

**Assignment Detail:**
- NovaTech Solutions ($110,000) -> Mike Rodriguez (Enterprise Tech)
- TechFlow Industries ($85,000) -> Mike Rodriguez (Enterprise Tech)
- Ironclad Security ($75,000) -> Mike Rodriguez (Enterprise Tech)
- Nexus Health Network ($3,200,000) -> Sarah Kim (Healthcare / FinServ)
- Summit Health Partners ($1,600,000) -> Sarah Kim (Healthcare / FinServ)
- Greenfield Health ($620,000) -> Sarah Kim (Healthcare / FinServ)
- Orion Manufacturing ($780,000) -> James Chen (Manufacturing / Industrial)
- Titan Aerospace ($680,000) -> James Chen (Manufacturing / Industrial)
- FusionTech Labs ($48,000) -> Lisa Park (Mid-Market SaaS)
- Apex Solutions ($120,000) -> Lisa Park (Mid-Market SaaS)
- Pacific Mutual Insurance ($2,100,000) -> David Okafor (Enterprise FinServ)
- Crestline Financial ($2,800,000) -> David Okafor (Enterprise FinServ)
- CoreBridge Insurance ($1,500,000) -> David Okafor (Enterprise FinServ)

**Handoff Package per Lead:**
- Lead score + BANT summary
- Booth interaction / source notes
- Personalized email draft
- Recommended talk track

Synthetic source model: [Territory Rules + Capacity Dashboard]
Agents: LeadRoutingAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-05 — `setup_tracking`

- Persona: Sales Manager
- Locked prompt: Draft an SLA and escalation plan for the synthetic leads without activating alerts or automations.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Draft SLA Tracking Plan — 45 Synthetic Leads**

| Lead Tier | Response SLA | Escalation | Sequence |
|---|---|---|---|
| Hot (13 leads) | 4h | Manager alert + Slack DM | Immediate call + personalized email |
| Warm (11 leads) | 24h | Team channel alert | Personalized email day 0, call day 1 |
| Nurture (13 leads) | 48h | Weekly digest flag | 3-email drip over 10 days |
| Disqualified (8 leads) | N/A | None — routed to marketing | Marketing nurture list |

**Proposed Monitoring (not activated):**
- Draft dashboard design for all 45 synthetic leads
- Draft SLA-risk alert rule (50% time elapsed)
- Draft daily summary schedule for 9:00 AM
- Draft weekly qualification tracking by tier

**Escalation Rules:**
- Hot lead no contact in 4h: Manager DM + email
- Warm lead no contact in 24h: Team channel alert
- Any lead no response after full sequence: Re-route to alternate AE
- Meeting booked: Recommend a CRM stage review by an authorized owner

Synthetic source model: [SLA Engine + Notification System]
Agents: SLAMonitoringAgent

**Evidence boundary:** Exact names, lead counts, company attributes, scores, values, percentages, and timing are synthetic planning evidence. Outreach and routing are drafts for human review. No lead was assigned, no sequence or alert was activated, and no CRM or customer communication occurred.

### SQ-06 — `qualification_report`

- Persona: Account Executive
- Locked prompt: Summarize the synthetic qualified pipeline and clearly label every conversion and value assumption.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Qualification Report — Full Pipeline Summary**

| Metric | Value |
|---|---|
| Total leads scored | 45 |
| Hot leads | 13 |
| Warm leads | 11 |
| Nurture leads | 13 |
| Disqualified | 8 |
| Hot pipeline value | $15,303,000 |
| Warm pipeline value | $3,473,000 |
| **Total qualified pipeline** | **$18,776,000** |

**Leads by Industry:**

| Industry | Count | Hot | Warm |
|---|---|---|---|
| Healthcare | 10 | 5 | 4 |
| Financial Services | 8 | 4 | 2 |
| Manufacturing | 7 | 1 | 1 |
| SaaS | 6 | 1 | 1 |
| Technology | 5 | 2 | 3 |
| Logistics | 3 | 0 | 0 |
| Energy | 3 | 0 | 0 |
| Education | 1 | 0 | 0 |
| Professional Services | 1 | 0 | 0 |
| Retail | 1 | 0 | 0 |

**Synthetic Conversion Assumptions (not predictions):**
- Hot-to-meeting assumption: 40% (5 modeled meetings)
- Meeting-to-opportunity assumption: 60% (3 modeled opportunities)
- Warm-to-meeting assumption: 20% (2 modeled meetings)
- Illustrative hot-lead scenario value: $3,672,720

**Draft Review Queue:**
1. 13 hot leads — Review for authorized AE follow-up
2. 11 warm leads — Review for authorized SDR follow-up
3. 13 nurture leads — Review a draft email sequence
4. 8 disqualified — Review for marketing nurture eligibility

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
