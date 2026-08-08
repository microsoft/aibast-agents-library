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
    """Fuzzy-match an RFP or account name to synthetic data."""
    if not query:
        return "meridian"
    q = query.lower().strip()
    for key in _RFPS:
        if key in q or q in _RFPS[key]["account"].lower():
            return key
    return None
```

### `_match_capabilities`

```python
def _match_capabilities(rfp):
    """Score how well our capabilities match each RFP requirement. Returns list of dicts + overall %."""
    cap_map = {
        "EHR integration": {"score": 95, "evidence": "Native Epic & Cerner connectors, certified"},
        "HIPAA compliance": {"score": 100, "evidence": "SOC 2 Type II + HIPAA certified"},
        "24/7 support": {"score": 98, "evidence": "24/7/365 with 15-min response SLA"},
        "15-min response": {"score": 98, "evidence": "Industry-leading 15-min SLA"},
        "Implementation under": {"score": 90, "evidence": f"{_OUR_CAPABILITIES['impl_weeks']}-week methodology with accelerators"},
        "staff training": {"score": 92, "evidence": "Role-based curriculum with certification"},
        "Data migration": {"score": 88, "evidence": "Automated migration toolkit, 50+ connectors"},
        "Multi-cloud": {"score": 91, "evidence": "AWS + Azure + GCP orchestration layer"},
        "Zero-downtime": {"score": 93, "evidence": "Blue-green deployment with automated rollback"},
        "SOC 2": {"score": 100, "evidence": "SOC 2 Type II audit current"},
        "managed services": {"score": 90, "evidence": "Dedicated SRE team, 99.99% uptime track record"},
        "Knowledge transfer": {"score": 85, "evidence": "Structured runbook and shadowing program"},
        "Real-time transaction": {"score": 87, "evidence": "Sub-30ms processing demonstrated at Atlantic CU"},
        "PCI-DSS": {"score": 100, "evidence": "PCI-DSS Level 1 certified"},
        "99.999%": {"score": 88, "evidence": "99.99% historical, architecture supports five-nines"},
        "Phased rollout": {"score": 92, "evidence": "Proven branch-by-branch methodology"},
        "certification": {"score": 90, "evidence": "LMS-integrated certification tracks"},
    }
    matches = []
    for req in rfp["requirements"]:
        best_score = 75  # default baseline
        best_evidence = "Addressed through standard platform capabilities"
        for kw, cap in cap_map.items():
            if kw.lower() in req["text"].lower():
                if cap["score"] > best_score:
                    best_score = cap["score"]
                    best_evidence = cap["evidence"]
        matches.append({
            "req_id": req["id"], "requirement": req["text"],
            "category": req["category"], "weight": req["weight"],
            "fit_score": best_score, "evidence": best_evidence,
        })
    weighted_total = sum(m["fit_score"] * m["weight"] for m in matches)
    weight_sum = sum(m["weight"] for m in matches)
    overall = round(weighted_total / weight_sum, 1) if weight_sum else 0
    return matches, overall
```

### `_compute_pricing`

```python
def _compute_pricing(rfp):
    """Build solution pricing with discounts, savings, and margin analysis."""
    industry = rfp["industry"]
    components = _SOLUTION_CONFIGS.get(industry, _SOLUTION_CONFIGS["Technology"])
    budget = rfp["budget_ceiling"]

    line_items = []
    total_list = 0
    total_proposed = 0
    total_cost = 0

    for comp_key in components:
        prod = _PRODUCT_CATALOG[comp_key]
        cat = prod["category"]
        rules = _DISCOUNT_RULES[cat]
        discount = rules["base"]
        if prod["list_price"] >= rules["volume_threshold"]:
            discount += rules["volume_bonus"]
        discount = min(discount, rules["max"])

        list_price = prod["list_price"]
        proposed = int(list_price * (1 - discount))
        cost = int(list_price * (1 - prod["margin_floor"]))
        margin_pct = round((proposed - cost) / proposed * 100, 1) if proposed else 0

        line_items.append({
            "component": prod["name"], "category": cat,
            "list_price": list_price, "discount_pct": round(discount * 100, 1),
            "proposed_price": proposed, "savings": list_price - proposed,
            "cost": cost, "margin_pct": margin_pct,
        })
        total_list += list_price
        total_proposed += proposed
        total_cost += cost

    # Adjust if proposed exceeds budget
    if total_proposed > budget:
        scale = budget / total_proposed
        for item in line_items:
            item["proposed_price"] = int(item["proposed_price"] * scale)
            item["savings"] = item["list_price"] - item["proposed_price"]
            item["margin_pct"] = round((item["proposed_price"] - item["cost"]) / max(item["proposed_price"], 1) * 100, 1)
        total_proposed = sum(i["proposed_price"] for i in line_items)

    overall_discount = round((1 - total_proposed / total_list) * 100, 1) if total_list else 0
    overall_margin = round((total_proposed - total_cost) / max(total_proposed, 1) * 100, 1)
    within_budget = total_proposed <= budget

    return {
        "line_items": line_items,
        "total_list": total_list, "total_proposed": total_proposed,
        "total_savings": total_list - total_proposed,
        "overall_discount_pct": overall_discount,
        "overall_margin_pct": overall_margin,
        "budget_ceiling": budget, "within_budget": within_budget,
        "budget_headroom": budget - total_proposed,
    }
```

### `_score_references`

```python
def _score_references(industry):
    """Select and score references by industry relevance."""
    scored = []
    for ref in _REFERENCES:
        relevance = 100 if ref["industry"] == industry else 30
        if ref["contact_ready"]:
            relevance += 10
        scored.append({**ref, "relevance_score": min(relevance, 100)})
    scored.sort(key=lambda r: r["relevance_score"], reverse=True)
    return scored[:4]
```

### `_build_differentiator_matrix`

```python
def _build_differentiator_matrix(competitor_keys):
    """Build comparison matrix of us vs named competitors."""
    rows = []
    factors = [
        ("Implementation", lambda c: f"{c['impl_weeks']} weeks", f"{_OUR_CAPABILITIES['impl_weeks']} weeks"),
        ("HIPAA certified", lambda c: "Yes" if c["hipaa_certified"] else "Pending", "Yes"),
        ("EHR integration", lambda c: c["ehr_integration"], _OUR_CAPABILITIES["ehr_integration"]),
        ("Support SLA", lambda c: f"{c['support_sla_min']} min", f"{_OUR_CAPABILITIES['support_sla_min']} min"),
        ("Pricing", lambda c: c["pricing_position"], _OUR_CAPABILITIES["pricing_position"]),
    ]
    for label, comp_fn, ours in factors:
        row = {"factor": label, "us": ours}
        for ck in competitor_keys:
            comp = _COMPETITOR_CAPABILITIES.get(ck)
            row[ck] = comp_fn(comp) if comp else "N/A"
        rows.append(row)
    return rows
```

### `_compute_win_probability`

```python
def _compute_win_probability(rfp, capability_score, pricing):
    """Compute win probability from fit, pricing, references, and competition factors."""
    # Capability fit factor (0-30 points)
    fit_pts = min(30, capability_score * 0.3)

    # Pricing factor (0-25 points)
    pricing_pts = 20 if pricing["within_budget"] else 10
    if pricing["budget_headroom"] > 30_000:
        pricing_pts += 5

    # Reference strength (0-20 points)
    industry_refs = [r for r in _REFERENCES if r["industry"] == rfp["industry"]]
    ref_pts = min(20, len(industry_refs) * 7)

    # Competition factor (0-25 points) -- fewer competitors = better odds
    num_competitors = len(rfp["competitors_shortlisted"])
    comp_pts = max(5, 25 - num_competitors * 7)
    # Bonus if we beat all on implementation speed
    all_slower = all(
        _COMPETITOR_CAPABILITIES.get(c, {}).get("impl_weeks", 99) > _OUR_CAPABILITIES["impl_weeks"]
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

## Locked operation evidence

Each exact output below is generated by the deterministic source with the corresponding locked-case arguments and appears verbatim within that case's strict-isolation transcript agent log. Use it as the response contract for Copilot Studio.

### PG-01 — `analyze_rfp`

- Persona: Bid Manager
- Locked prompt: Analyze the synthetic Meridian Healthcare RFP and show the traceable requirement checklist.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**RFP Analysis: Meridian Healthcare -- Digital Transformation Platform**

| Detail | Information |
|---|---|
| RFP ID | RFP-2024-0147 |
| Account | Meridian Healthcare |
| Deal value | $1,200,000 |
| Budget ceiling | $1,250,000 |
| Decision timeline | 14 days |
| Key stakeholder | CIO Amanda Foster |
| Competitors shortlisted | CompetitorA, CompetitorB |

**Requirements Analysis (Overall Fit: 94.5%):**

| ID | Requirement | Category | Weight | Fit Score | Evidence |
|---|---|---|---|---|---|
| R1 | EHR integration capabilities | Technical | 25% | 95% | Native Epic & Cerner connectors, certified |
| R2 | HIPAA compliance certification | Compliance | 20% | 100% | SOC 2 Type II + HIPAA certified |
| R3 | 24/7 support SLA with <15-min response | Support | 15% | 98% | 24/7/365 with 15-min response SLA |
| R4 | Implementation under 16 weeks | Delivery | 20% | 90% | 12-week methodology with accelerators |
| R5 | Comprehensive staff training program | Training | 10% | 92% | Role-based curriculum with certification |
| R6 | Data migration from legacy systems | Technical | 10% | 88% | Automated migration toolkit, 50+ connectors |

**Existing Assets Found:**
- Healthcare case study (Memorial Health System)
- HIPAA compliance documentation
- Implementation methodology deck
- Training curriculum template

Synthetic source model: [CRM + RFP Document + Content Library]
Agents: RFPAnalysisAgent, ContentLibraryAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-02 — `executive_summary`

- Persona: Account Executive
- Locked prompt: Draft an executive summary for the synthetic Meridian Healthcare opportunity that reflects the buyer priorities and remains subject to review.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Executive Summary: Transforming Meridian Healthcare's Future**

Meridian Healthcare has an opportunity to digital transformation platform with a solution that matches 94.5% of stated requirements.

**Why Us:**

| Your Need | Our Solution | Fit |
|---|---|---|
| EHR integration capabilities | Native Epic & Cerner connectors, certified | 95% |
| HIPAA compliance certification | SOC 2 Type II + HIPAA certified | 100% |
| 24/7 support SLA with <15-min response | 24/7/365 with 15-min response SLA | 98% |
| Implementation under 16 weeks | 12-week methodology with accelerators | 90% |

**Capability Match:** 94.5% overall fit score
**Pricing:** $1,201,599 total (within budget, $48,401 under ceiling)
**Margin:** 33.4% gross margin maintained

**Proven Healthcare Success:**
Memorial Health System achieved 34% efficiency gain, $2.4M annual savings.

**Personalization Applied:**
- Tailored to CIO Amanda Foster's priorities
- Healthcare-specific references and compliance language
- Matched exact RFP terminology and requirement IDs

Synthetic source model: [Content Library + Stakeholder Intel]
Agents: ExecutiveSummaryAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-03 — `solution_pricing`

- Persona: Sales Leader
- Locked prompt: Compare the synthetic solution and pricing assumptions for Meridian Healthcare without approving a price, discount, or concession.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Solution & Pricing: Meridian Healthcare**

**Implementation Approach (12 weeks):**

**Phase 1: Foundation (Weeks 1-4)**
- Infrastructure assessment, Connector deployment, Security configuration, Core team training

**Phase 2: Rollout (Weeks 5-10)**
- Phased facility deployment, Workflow integration, Staff certification, Go-live support

**Phase 3: Optimization (Weeks 11-12)**
- Performance tuning, Advanced training, Success metrics validation, Handoff to support

**Pricing Structure:**

| Component | List Price | Discount | Proposed | Savings | Margin |
|---|---|---|---|---|---|
| Platform Core License | $420,000 | 8.0% | $386,400 | $33,600 | 32.6% |
| Integration Suite | $180,000 | 8.0% | $165,600 | $14,400 | 34.8% |
| Analytics & Reporting | $80,000 | 8.0% | $73,600 | $6,400 | 40.2% |
| Implementation Services | $380,000 | 10.0% | $342,000 | $38,000 | 27.8% |
| Training Program | $120,000 | 10.0% | $108,000 | $12,000 | 44.4% |
| 3-Year Premium Support | $180,000 | 30.0% | $125,999 | $54,001 | 35.7% |
| **Total** | **$1,360,000** | **11.6%** | **$1,201,599** | **$158,401** | **33.4%** |

**Budget Analysis:**
- Budget ceiling: $1,250,000
- Proposed total: $1,201,599
- Status: **WITHIN** (headroom: $48,401)
- Overall discount: 11.6%
- Gross margin: 33.4% (floor: 35%)

Synthetic source model: [Pricing Engine + Competitive Data]
Agents: SolutionArchitectAgent, PricingOptimizationAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-04 — `references_positioning`

- Persona: Bid Manager
- Locked prompt: Prepare synthetic reference and competitive positioning options for Meridian Healthcare, with availability checks before use.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**References & Competitive Positioning: Meridian Healthcare**

**Customer References (Healthcare-weighted):**

| Customer | Size | Results | Relevance | Contact Ready |
|---|---|---|---|---|
| Memorial Health System | 8 facilities | 34% efficiency gain, $2.4M annual savings | 100% | Yes |
| Pacific Medical Group | 15 facilities | $2.4M savings/year, 99.9% uptime | 100% | Yes |
| Summit Healthcare Network | 6 facilities | 12-week go-live, 28% cost reduction | 100% | Yes |
| Atlas Cloud Services | 800 employees | Zero-downtime migration, 40% infra cost reduction | 40% | Yes |

**Win Theme: Speed + Compliance + Support**

**Competitive Differentiator Matrix:**

| Factor | Us | CompetitorA | CompetitorB |
|---|---|---|---|
| Implementation | 12 weeks | 20 weeks | 16 weeks |
| HIPAA certified | Yes | Yes | Pending |
| EHR integration | Native | Third-party | Native |
| Support SLA | 15 min | 240 min | 60 min |
| Pricing | Market rate | Market rate | +5% above market |

**Objection Pre-Handlers:**
- "Pre-built healthcare accelerators cut implementation by 40%"
- "Native EHR integration eliminates middleware costs"
- "15-minute support SLA is fastest in industry"

Synthetic source model: [Reference Database + Competitive Intel]
Agents: CompetitiveDifferentiationAgent, ContentLibraryAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-05 — `compile_proposal`

- Persona: Bid Manager
- Locked prompt: Outline the synthetic Meridian Healthcare proposal package and every human review required before delivery.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Proposal Package: Meridian Healthcare -- Digital Transformation Platform**

**Main Document (42 pages):**
1. Executive Summary (personalized) (3 pages)
2. Company Overview + Healthcare Expertise (4 pages)
3. Solution Architecture + Roadmap (6 pages)
4. Implementation Methodology (12-week plan) (5 pages)
5. Pricing + Investment Summary (4 pages)
6. Customer References + Case Studies (4) (8 pages)
7. Team Bios (Industry specialists) (3 pages)
8. Terms + Conditions (3 pages)

**Supporting Materials:**
- HIPAA documentation (attached)
- Memorial Health System case study (2 pages)
- Implementation timeline visual (1 page)

**Planned Draft Package:**
- Proposed PDF proposal structure (branded template)
- Proposed executive presentation structure (12 slides)
- Proposed pricing worksheet (detailed breakdown)
- Proposed reference review sheet (4 synthetic examples)

**Required Human Review Before Delivery:**
- Legal review: Not performed
- Pricing approval: Required from an authorized approver
- Branding review: Required
- Requirement coverage: Synthetic fit model reports 94.5%
- Editorial review: Required

Synthetic source model: [Document Assembly + Compliance Check]
Agents: ProposalAssemblyAgent

**Evidence boundary:** Exact names, dates, requirements, prices, discounts, margins, fit scores, and projections are synthetic planning evidence. This read-only output did not approve pricing, create a final document, submit a response, contact a reference, or communicate with a customer.

### PG-06 — `delivery_summary`

- Persona: Sales Leader
- Locked prompt: Summarize the synthetic Meridian Healthcare draft readiness and the decisions authorized reviewers must make next.
- Transcript model: `claude-haiku-4.5`
- Exact deterministic output:

**Delivery Summary: Meridian Healthcare -- Digital Transformation Platform**

| Element | Status |
|---|---|
| Capability match | 94.5% fit to 6 requirements |
| Executive summary | Personalized to CIO Amanda Foster |
| Solution | 12-week implementation plan |
| Pricing | $1,201,599 (11.6% discount, 33.4% margin) |
| References | 4 synthetic Healthcare-specific examples requiring availability review |
| Compliance | SOC 2 Type II, HIPAA, ISO 27001 included |

**Synthetic Win-Probability Indicator: 89%**

| Factor | Score | Max |
|---|---|---|
| Capability fit | 28.3 | 30 |
| Pricing strength | 25 | 25 |
| Reference strength | 20 | 20 |
| Competitive position | 16 | 25 |
| **Total** | **89** | **100** |

**Session Accomplishments:**
- RFP requirements mapped to capabilities (94.5% fit)
- Executive summary personalized to CIO Amanda Foster
- Competitive positioning vs 2 shortlisted vendors
- Pricing optimized ($158,401 discount, 33.4% margin protected)
- Draft proposal package outline prepared for review

**Human-Governed Next-Step Options:**
- Review the draft against the 14 day synthetic window
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
