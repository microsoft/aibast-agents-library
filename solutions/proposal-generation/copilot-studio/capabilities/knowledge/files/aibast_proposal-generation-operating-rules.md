# Proposal Generation Agent — Deterministic Rules and Locked-Case Evidence

> **FIXED SYNTHETIC SNAPSHOT ONLY.** Use the companion complete source-record file and the exact rules below. Do not browse, enrich, infer missing facts, or substitute live data.

## Deterministic routing

| Operation | Locked request | Required response anchors |
| --- | --- | --- |
| `analyze_rfp` | Analyze the synthetic Meridian Healthcare RFP and show the traceable requirement checklist. | `RFP Analysis`; `Requirements Analysis`; `Evidence boundary` |
| `executive_summary` | Draft an executive summary for the synthetic Meridian Healthcare opportunity that reflects the buyer priorities and remains subject to review. | `Executive Summary`; `Personalization Applied`; `Evidence boundary` |
| `solution_pricing` | Compare the synthetic solution and pricing assumptions for Meridian Healthcare without approving a price, discount, or concession. | `Solution & Pricing`; `Budget Analysis`; `Evidence boundary` |
| `references_positioning` | Prepare synthetic reference and competitive positioning options for Meridian Healthcare, with availability checks before use. | `References & Competitive Positioning`; `Win Theme`; `Evidence boundary` |
| `compile_proposal` | Outline the synthetic Meridian Healthcare proposal package and every human review required before delivery. | `Proposal Package`; `Required Human Review Before Delivery`; `Evidence boundary` |
| `delivery_summary` | Summarize the synthetic Meridian Healthcare draft readiness and the decisions authorized reviewers must make next. | `Delivery Summary`; `Human-Governed Next-Step Options`; `Evidence boundary` |

Only the operations above are supported. Pass `data_source=synthetic` and use only allow-listed identifiers from the companion records. Unknown sources, operations, and identifiers must fail closed.

## Exact computation rules

The following source functions are the authoritative deterministic calculations. They operate only on the bundled records. Preserve their thresholds, ordering, rounding, labels, and formulas exactly.

### `_resolve_rfp`

```python
def _resolve_rfp(query):
    """Match an RFP or account name to synthetic data (default Meridian Healthcare)."""
    if not query:
        return "meridian"
    q = query.lower().strip()
    for key in _RFPS:
        if key in q or q in _RFPS[key]["account"].lower():
            return key
    return None
```

### `_money_short`

```python
def _money_short(amount):
    """$1,180,000 -> '$1.18M'; $620,000 -> '$620K'."""
    if amount >= 1_000_000 and amount % 100_000 == 0:
        return f"${amount / 1_000_000:.1f}M"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    return f"${amount // 1000}K"
```

### `_match_capabilities`

```python
def _match_capabilities(rfp):
    """Score how well our capabilities match each RFP requirement. Returns list of dicts + overall %."""
    matches = []
    for req in rfp["requirements"]:
        score, evidence = 75, "Addressed through standard platform capabilities"
        for cap in _CAPABILITY_FIT:
            if cap["keyword"] in req["text"].lower() and cap["score"] > score:
                score, evidence = cap["score"], cap["evidence"]
        matches.append({
            "req_id": req["id"], "requirement": req["text"],
            "category": req["category"], "weight": req["weight"],
            "fit_score": score, "evidence": evidence,
        })
    weighted_total = sum(m["fit_score"] * m["weight"] for m in matches)
    weight_sum = sum(m["weight"] for m in matches)
    overall = round(weighted_total / weight_sum, 1) if weight_sum else 0
    return matches, overall
```

### `_compute_pricing`

```python
def _compute_pricing(rfp):
    """Group the solution into Software / Implementation / Training + Support with savings and margin."""
    components = _SOLUTION_CONFIGS.get(rfp["industry"], _SOLUTION_CONFIGS["Technology"])
    groups = []
    for rule in _GROUP_DISCOUNTS:
        members = [_PRODUCT_CATALOG[c] for c in components if _PRODUCT_CATALOG[c]["group"] == rule["group"]]
        list_price = sum(m["list_price"] for m in members)
        cost = sum(m["cost"] for m in members)
        proposed = int(list_price * (100 - rule["discount_pct"]) / 100 / 1000 + 0.5) * 1000
        groups.append({
            "group": rule["group"], "components": [m["name"] for m in members],
            "list_price": list_price, "proposed": proposed, "cost": cost,
            "savings_pct": rule["discount_pct"],
        })
    total_list = sum(g["list_price"] for g in groups)
    total_proposed = sum(g["proposed"] for g in groups)
    total_cost = sum(g["cost"] for g in groups)
    return {
        "groups": groups, "total_list": total_list, "total_proposed": total_proposed,
        "total_savings": total_list - total_proposed,
        "overall_discount_pct": round((total_list - total_proposed) * 100 / total_list),
        "overall_margin_pct": round((total_proposed - total_cost) * 100 / total_proposed),
        "margin_target_pct": _MARGIN_TARGET_PCT,
        "budget_ceiling": rfp["budget_ceiling"],
        "within_budget": total_proposed <= rfp["budget_ceiling"],
        "budget_headroom": rfp["budget_ceiling"] - total_proposed,
    }
```

### `_score_references`

```python
def _score_references(industry):
    """Same-industry references in catalog order; the top three overall when none match."""
    same = [r for r in _REFERENCES if r["industry"] == industry]
    return same[:3] if same else _REFERENCES[:3]
```

### `_competitive_edge`

```python
def _competitive_edge(rfp):
    """Our edge vs the shortlisted competitors: implementation weeks, integration, support SLA."""
    comps = [_COMPETITOR_CAPABILITIES[c] for c in rfp["competitors_shortlisted"]]
    weeks = sorted(c["impl_weeks"] for c in comps)
    slas = sorted(c["support_sla_min"] for c in comps)
    weeks_range = f"{weeks[0]}-{weeks[-1]}" if weeks[0] != weeks[-1] else f"{weeks[0]}"
    sla_range = f"{slas[0] // 60}-{slas[-1] // 60} hours" if slas[0] != slas[-1] else f"{slas[0] // 60} hours"
    third_party = all(c["ehr_integration"] == "Third-party" for c in comps)
    integration = "Native (not third-party)" if third_party else "Native"
    fastest = all(c["impl_weeks"] > _OUR_CAPABILITIES["impl_weeks"] for c in comps)
    theme = "Speed + Compliance + Support" if fastest else "Compliance + Integration + Support"
    return {
        "implementation": f"{_OUR_CAPABILITIES['impl_weeks']} wks (vs {weeks_range})",
        "integration": integration,
        "support": f"{_OUR_CAPABILITIES['support_sla_min']} min (vs {sla_range})",
        "theme": theme,
    }
```

### `_compute_win_probability`

```python
def _compute_win_probability(rfp, capability_score, pricing):
    """Compute win probability from fit, pricing, references, and competition factors."""
    fit_pts = min(30, capability_score * 0.3)
    pricing_pts = 20 if pricing["within_budget"] else 10
    if pricing["budget_headroom"] > 30_000:
        pricing_pts += 5
    industry_refs = [r for r in _REFERENCES if r["industry"] == rfp["industry"]]
    ref_pts = min(20, len(industry_refs) * 7)
    num_competitors = len(rfp["competitors_shortlisted"])
    comp_pts = max(5, 25 - num_competitors * 7)
    all_slower = all(
        _COMPETITOR_CAPABILITIES[c]["impl_weeks"] > _OUR_CAPABILITIES["impl_weeks"]
        for c in rfp["competitors_shortlisted"]
    )
    if all_slower:
        comp_pts += 5
    raw = fit_pts + pricing_pts + ref_pts + comp_pts
    win_pct = min(95, max(15, int(raw)))
    return win_pct, {
        "capability_fit": round(fit_pts, 1), "pricing_strength": pricing_pts,
        "reference_strength": ref_pts, "competitive_position": min(comp_pts, 25),
    }
```

### `_timeline_text`

```python
def _timeline_text(days):
    """14 -> '2 weeks'; 30 -> '30 days'."""
    return f"{days // 7} weeks" if days % 7 == 0 else f"{days} days"
```

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### PG-01 — `analyze_rfp`

- Persona: Bid Manager
- Locked prompt: Analyze the synthetic Meridian Healthcare RFP and show the traceable requirement checklist.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**RFP Analysis: Meridian Healthcare -- Digital Transformation Platform**

Context pulled for Meridian Healthcare proposal:

| Detail | Info |
|---|---|
| Deal value | $1.2M |
| Decision | 2 weeks |
| Stakeholder | CIO Amanda Foster |
| Competition | 2 vendors shortlisted |
| RFP ID | RFP-2024-0147 |
| Budget ceiling | $1,250,000 |

**RFP Requirements:** EHR integration, HIPAA compliance, 24/7 support, 16-week implementation, Training

**Requirements Analysis (Overall Fit: 95.7%):**

| ID | Requirement | Category | Weight | Fit Score | Evidence |
|---|---|---|---|---|---|
| R1 | EHR integration | Technical | 25% | 95% | Native Epic & Cerner connectors, certified |
| R2 | HIPAA compliance | Compliance | 25% | 100% | SOC 2 Type II + HIPAA certified |
| R3 | 24/7 support | Support | 15% | 98% | 24/7/365 with 15-min response SLA |
| R4 | 16-week implementation | Delivery | 20% | 92% | 12-week methodology with accelerators |
| R5 | Training | Training | 15% | 92% | Role-based curriculum with certification |

**Existing Assets Found:** Healthcare case study, HIPAA docs, Implementation deck

Next: generate the executive summary?

Synthetic source model: [CRM + RFP Document + Content Library]
Agents: RFPAnalysisAgent, ContentLibraryAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-02 — `executive_summary`

- Persona: Account Executive
- Locked prompt: Draft an executive summary for the synthetic Meridian Healthcare opportunity that reflects the buyer priorities and remains subject to review.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Executive Summary: Meridian Healthcare -- personalized to CIO Amanda Foster**

Meridian Healthcare has an opportunity to modernize with a digital transformation platform that matches 95.7% of the stated requirements.

| Your Need | Our Solution |
|---|---|
| EHR Integration | Epic & Cerner certified |
| HIPAA Compliance | SOC 2 + HIPAA certified |
| Deployment | 12 weeks (beats your 16) |
| Support | 24/7, 15-min SLA |

**Proof:** Memorial Health achieved 34% efficiency gain, $2.4M savings
**Investment:** $1.18M (3 years support + training included)

**Personalization Applied:**
- Tailored to CIO Amanda Foster's priorities
- Healthcare-specific references and compliance language
- Matched exact RFP terminology and requirement IDs

Next: proceed to solution and pricing?

Synthetic source model: [Content Library + Stakeholder Intel]
Agents: ExecutiveSummaryAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-03 — `solution_pricing`

- Persona: Sales Leader
- Locked prompt: Compare the synthetic solution and pricing assumptions for Meridian Healthcare without approving a price, discount, or concession.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Solution & Pricing: Meridian Healthcare**

**12-Week Plan:** Foundation (wks 1-4) > Rollout (wks 5-10) > Optimization (wks 11-12)

- **Foundation (wks 1-4):** Infrastructure assessment, Connector deployment, Security configuration, Core team training
- **Rollout (wks 5-10):** Phased facility deployment, Workflow integration, Staff certification, Go-live support
- **Optimization (wks 11-12):** Performance tuning, Advanced training, Success metrics validation, Handoff to support

| Component | List Price | Proposed | Savings |
|---|---|---|---|
| Software | $681,000 | $620K | 9% |
| Implementation | $382,000 | $340K | 11% |
| Training + Support | $293,000 | $220K | 25% |
| **Total** | **$1,356,000** | **$1.18M** | **13%** |

**Margin:** 42% maintained (target 40%+)

**Budget Analysis:**
- Budget ceiling: $1,250,000
- Proposed total: $1,180,000 (within budget, $70,000 headroom)
- Customer savings: $176,000 (13%)
- Pricing is a draft for an authorized pricing approver.

Next: add references and differentiators?

Synthetic source model: [Pricing Engine + Competitive Data]
Agents: SolutionArchitectAgent, PricingOptimizationAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-04 — `references_positioning`

- Persona: Bid Manager
- Locked prompt: Prepare synthetic reference and competitive positioning options for Meridian Healthcare, with availability checks before use.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**References & Competitive Positioning: Meridian Healthcare**

| Reference | Results | Size | Contact Ready |
|---|---|---|---|
| Memorial Health | 34% efficiency gain | 8 facilities | Yes |
| Pacific Medical | $2.4M/year savings | 15 facilities | Yes |
| Summit Healthcare | 12-week go-live | 6 facilities | Yes |

**Your Edge vs Competition:**
- Implementation: 12 wks (vs 16-20)
- Epic integration: Native (not third-party)
- Support SLA: 15 min (vs 1-4 hours)

**Win Theme: Speed + Compliance + Support**

**Objection Pre-Handlers:**
- "Pre-built healthcare accelerators cut implementation by 40%"
- "Native Epic integration eliminates middleware costs"
- "15-minute support SLA is fastest in industry"

Confirm each reference's availability before offering a call.

Next: generate the final proposal?

Synthetic source model: [Reference Database + Competitive Intel]
Agents: CompetitiveDifferentiationAgent, ContentLibraryAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-05 — `compile_proposal`

- Persona: Bid Manager
- Locked prompt: Outline the synthetic Meridian Healthcare proposal package and every human review required before delivery.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Proposal Package: Meridian Healthcare -- Digital Transformation Platform**

Final proposal compiled as a draft (38 pages), ready for your review.

**Package Contents:**
- Executive Summary + Solution Architecture
- 12-week Implementation Plan
- Pricing ($1.18M) + References (3)
- HIPAA + SOC 2 certificates attached

**Sections:**
1. Executive Summary (personalized) (3 pages)
2. Company Overview + Industry Expertise (4 pages)
3. Solution Architecture + Roadmap (8 pages)
4. 12-week Implementation Plan (5 pages)
5. Pricing + Investment Summary (4 pages)
6. Customer References + Case Studies (6 pages)
7. Team Bios (Industry specialists) (3 pages)
8. Terms + Conditions (5 pages)

**Delivery Package (drafts):** PDF proposal, 12-slide exec presentation, pricing spreadsheet

**Checklist:** Legal - ready for review; Pricing - ready for approval; Branding - applied, ready for review

**Required Human Review Before Delivery:**
- Legal review by your legal team
- Pricing approval from an authorized approver
- Branding and editorial check
- Requirement coverage: synthetic fit model reports 95.7%

Nothing has been sent: you share the package with CIO Amanda Foster (for example through Microsoft Teams) after review.

Next: review the final summary?

Synthetic source model: [Document Assembly + Compliance Check]
Agents: ProposalAssemblyAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-06 — `delivery_summary`

- Persona: Sales Leader
- Locked prompt: Summarize the synthetic Meridian Healthcare draft readiness and the decisions authorized reviewers must make next.
- Transcript model: `claude-sonnet-5`
- Exact deterministic output:

**Delivery Summary: Meridian Healthcare -- Digital Transformation Platform**

| Element | Status |
|---|---|
| Capability match | 95.7% fit to 5 requirements |
| Executive summary | Personalized to CIO Amanda Foster |
| Solution | 12-week implementation plan |
| Pricing | $1.18M (13% savings, 42% margin vs 40% target) |
| References | 3 synthetic Healthcare examples requiring availability review |
| Compliance | HIPAA + SOC 2 certificates attached |

**Synthetic Win-Probability Indicator: 89%**

| Factor | Score | Max |
|---|---|---|
| Capability fit | 28.7 | 30 |
| Pricing strength | 25 | 25 |
| Reference strength | 20 | 20 |
| Competitive position | 16 | 25 |
| **Total** | **89** | **100** |

**Session Accomplishments:**
- RFP requirements mapped to capabilities (95.7% fit)
- Executive summary personalized to CIO Amanda Foster
- Competitive positioning vs 2 shortlisted vendors
- Pricing optimized ($176,000 customer savings, 42% margin protected)
- Draft proposal package prepared for review

**Human-Governed Next-Step Options:**
- Review the draft against the 2 weeks decision window
- Decide whether an authorized seller should request a confirmation meeting
- Validate reference availability before offering any calls
- Decide whether executive sponsorship is appropriate

Synthetic source model: [All Proposal Systems]
Agents: ProposalAssemblyAgent (orchestrating all agents)

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

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
