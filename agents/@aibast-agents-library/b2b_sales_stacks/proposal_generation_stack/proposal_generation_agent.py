"""
Proposal Generation Agent

Analyzes RFPs, generates executive summaries, builds solution pricing,
selects references, assembles proposal packages, and computes win probability.
Uses synthetic data for CRM, product catalog, reference database, and
competitive intelligence so the agent runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/proposal-generation",
    "version": "1.0.0",
    "display_name": "Proposal Generation",
    "description": "AI-powered proposal generation with RFP analysis, personalized content, pricing optimization, and competitive positioning.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "proposal", "rfp", "pricing", "competitive-positioning"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# Stands in for CRM, Product Catalog, Reference DB, Competitive Intel
# ═══════════════════════════════════════════════════════════════

_RFPS = {
    "meridian": {
        "id": "RFP-2024-0147", "account": "Meridian Healthcare", "industry": "Healthcare",
        "deal_value": 1_200_000, "budget_ceiling": 1_250_000,
        "project": "Digital Transformation Platform",
        "decision_timeline_days": 14, "key_stakeholder": "CIO Amanda Foster",
        "competitors_shortlisted": ["CompetitorA", "CompetitorB"],
        "requirements": [
            {"id": "R1", "text": "EHR integration capabilities", "category": "Technical", "weight": 0.25},
            {"id": "R2", "text": "HIPAA compliance certification", "category": "Compliance", "weight": 0.20},
            {"id": "R3", "text": "24/7 support SLA with <15-min response", "category": "Support", "weight": 0.15},
            {"id": "R4", "text": "Implementation under 16 weeks", "category": "Delivery", "weight": 0.20},
            {"id": "R5", "text": "Comprehensive staff training program", "category": "Training", "weight": 0.10},
            {"id": "R6", "text": "Data migration from legacy systems", "category": "Technical", "weight": 0.10},
        ],
        "existing_assets": [
            "Healthcare case study (Memorial Health System)",
            "HIPAA compliance documentation",
            "Implementation methodology deck",
            "Training curriculum template",
        ],
    },
    "contoso": {
        "id": "RFP-2024-0152", "account": "Contoso Technologies", "industry": "Technology",
        "deal_value": 800_000, "budget_ceiling": 850_000,
        "project": "Cloud Migration & Modernization",
        "decision_timeline_days": 21, "key_stakeholder": "VP Engineering Alex Kim",
        "competitors_shortlisted": ["CompetitorA"],
        "requirements": [
            {"id": "R1", "text": "Multi-cloud orchestration (AWS + Azure)", "category": "Technical", "weight": 0.30},
            {"id": "R2", "text": "Zero-downtime migration methodology", "category": "Delivery", "weight": 0.25},
            {"id": "R3", "text": "SOC 2 Type II compliance", "category": "Compliance", "weight": 0.15},
            {"id": "R4", "text": "24/7 managed services post-migration", "category": "Support", "weight": 0.20},
            {"id": "R5", "text": "Knowledge transfer and runbooks", "category": "Training", "weight": 0.10},
        ],
        "existing_assets": [
            "Cloud migration playbook",
            "SOC 2 Type II audit report",
            "Multi-cloud architecture reference",
        ],
    },
    "pinnacle": {
        "id": "RFP-2024-0159", "account": "Pinnacle Financial Group", "industry": "Financial Services",
        "deal_value": 1_500_000, "budget_ceiling": 1_600_000,
        "project": "Core Banking Platform Upgrade",
        "decision_timeline_days": 30, "key_stakeholder": "CTO Marcus Webb",
        "competitors_shortlisted": ["CompetitorA", "CompetitorB", "CompetitorC"],
        "requirements": [
            {"id": "R1", "text": "Real-time transaction processing (<50ms)", "category": "Technical", "weight": 0.25},
            {"id": "R2", "text": "PCI-DSS Level 1 and SOX compliance", "category": "Compliance", "weight": 0.25},
            {"id": "R3", "text": "99.999% uptime SLA", "category": "Support", "weight": 0.20},
            {"id": "R4", "text": "Phased rollout across 120 branches", "category": "Delivery", "weight": 0.20},
            {"id": "R5", "text": "End-user and admin training certification", "category": "Training", "weight": 0.10},
        ],
        "existing_assets": [
            "Financial services case study (Atlantic Credit Union)",
            "PCI-DSS compliance package",
            "Branch rollout methodology",
        ],
    },
}

_PRODUCT_CATALOG = {
    "platform_core": {"name": "Platform Core License", "list_price": 420_000, "category": "Software", "margin_floor": 0.38},
    "integration_suite": {"name": "Integration Suite", "list_price": 180_000, "category": "Software", "margin_floor": 0.40},
    "analytics_module": {"name": "Analytics & Reporting", "list_price": 80_000, "category": "Software", "margin_floor": 0.45},
    "implementation": {"name": "Implementation Services", "list_price": 380_000, "category": "Services", "margin_floor": 0.35},
    "training": {"name": "Training Program", "list_price": 120_000, "category": "Services", "margin_floor": 0.50},
    "support_3yr": {"name": "3-Year Premium Support", "list_price": 180_000, "category": "Support", "margin_floor": 0.55},
}

_SOLUTION_CONFIGS = {
    "Healthcare": ["platform_core", "integration_suite", "analytics_module", "implementation", "training", "support_3yr"],
    "Technology": ["platform_core", "integration_suite", "implementation", "training", "support_3yr"],
    "Financial Services": ["platform_core", "integration_suite", "analytics_module", "implementation", "training", "support_3yr"],
}

_DISCOUNT_RULES = {
    "Software": {"base": 0.08, "volume_threshold": 600_000, "volume_bonus": 0.03, "max": 0.15},
    "Services": {"base": 0.10, "volume_threshold": 400_000, "volume_bonus": 0.04, "max": 0.18},
    "Support": {"base": 0.25, "volume_threshold": 150_000, "volume_bonus": 0.05, "max": 0.35},
}

_REFERENCES = [
    {"customer": "Memorial Health System", "industry": "Healthcare", "size": "8 facilities",
     "results": "34% efficiency gain, $2.4M annual savings", "impl_weeks": 11, "contact_ready": True},
    {"customer": "Pacific Medical Group", "industry": "Healthcare", "size": "15 facilities",
     "results": "$2.4M savings/year, 99.9% uptime", "impl_weeks": 14, "contact_ready": True},
    {"customer": "Summit Healthcare Network", "industry": "Healthcare", "size": "6 facilities",
     "results": "12-week go-live, 28% cost reduction", "impl_weeks": 12, "contact_ready": True},
    {"customer": "Atlas Cloud Services", "industry": "Technology", "size": "800 employees",
     "results": "Zero-downtime migration, 40% infra cost reduction", "impl_weeks": 10, "contact_ready": True},
    {"customer": "Nexus Software Corp", "industry": "Technology", "size": "2,400 employees",
     "results": "3x deployment velocity, 99.95% uptime", "impl_weeks": 8, "contact_ready": False},
    {"customer": "Atlantic Credit Union", "industry": "Financial Services", "size": "120 branches",
     "results": "Sub-30ms latency, zero audit findings", "impl_weeks": 16, "contact_ready": True},
    {"customer": "Sentinel Insurance", "industry": "Financial Services", "size": "$4B AUM",
     "results": "PCI-DSS compliant in 90 days, 22% ops savings", "impl_weeks": 14, "contact_ready": True},
    {"customer": "Vanguard Logistics", "industry": "Manufacturing", "size": "3,200 employees",
     "results": "18% throughput improvement", "impl_weeks": 12, "contact_ready": False},
]

_COMPETITOR_CAPABILITIES = {
    "CompetitorA": {
        "impl_weeks": 20, "hipaa_certified": True, "ehr_integration": "Third-party",
        "support_sla_min": 240, "pricing_position": "Market rate",
        "strengths": ["Large install base", "Brand recognition"],
        "weaknesses": ["Slow implementation", "Middleware dependency"],
    },
    "CompetitorB": {
        "impl_weeks": 16, "hipaa_certified": False, "ehr_integration": "Native",
        "support_sla_min": 60, "pricing_position": "+5% above market",
        "strengths": ["Native integrations", "Modern UI"],
        "weaknesses": ["HIPAA pending", "Limited references"],
    },
    "CompetitorC": {
        "impl_weeks": 24, "hipaa_certified": True, "ehr_integration": "Third-party",
        "support_sla_min": 120, "pricing_position": "-10% below market",
        "strengths": ["Low price", "Long track record"],
        "weaknesses": ["Legacy architecture", "High customization cost"],
    },
}

_OUR_CAPABILITIES = {
    "impl_weeks": 12, "hipaa_certified": True, "ehr_integration": "Native",
    "support_sla_min": 15, "pricing_position": "Market rate",
    "certifications": ["SOC 2 Type II", "HIPAA", "ISO 27001", "PCI-DSS Level 1"],
    "differentiators": [
        "Pre-built healthcare accelerators cut implementation by 40%",
        "Native EHR integration eliminates middleware costs",
        "15-minute support SLA is fastest in industry",
        "API-first architecture for seamless ecosystem integration",
    ],
}

_IMPL_PHASES = [
    {"phase": 1, "name": "Foundation", "duration_weeks": 4,
     "activities": ["Infrastructure assessment", "Connector deployment", "Security configuration", "Core team training"]},
    {"phase": 2, "name": "Rollout", "duration_weeks": 6,
     "activities": ["Phased facility deployment", "Workflow integration", "Staff certification", "Go-live support"]},
    {"phase": 3, "name": "Optimization", "duration_weeks": 2,
     "activities": ["Performance tuning", "Advanced training", "Success metrics validation", "Handoff to support"]},
]


# ═══════════════════════════════════════════════════════════════
# HELPERS -- real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _resolve_rfp(query):
    """Fuzzy-match an RFP or account name to synthetic data."""
    if not query:
        return "meridian"
    q = query.lower().strip()
    for key in _RFPS:
        if key in q or q in _RFPS[key]["account"].lower():
            return key
    return "meridian"


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


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ProposalGenerationAgent(BasicAgent):
    """
    Generates complete sales proposals from RFP analysis through delivery.

    Operations:
        analyze_rfp          - Extract and score requirements from RFP
        executive_summary    - Personalized exec summary with capability match
        solution_pricing     - Phased implementation plan + optimized pricing
        references_positioning - Best references + competitive differentiator matrix
        compile_proposal     - Assemble full proposal package with page counts
        delivery_summary     - Final summary with computed win probability
    """

    def __init__(self):
        self.name = "ProposalGenerationAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "analyze_rfp", "executive_summary",
                            "solution_pricing", "references_positioning",
                            "compile_proposal", "delivery_summary",
                        ],
                        "description": "The proposal operation to perform",
                    },
                    "rfp_name": {
                        "type": "string",
                        "description": "RFP or account name (e.g. 'Meridian Healthcare')",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "analyze_rfp")
        key = _resolve_rfp(kwargs.get("rfp_name", ""))
        dispatch = {
            "analyze_rfp": self._analyze_rfp,
            "executive_summary": self._executive_summary,
            "solution_pricing": self._solution_pricing,
            "references_positioning": self._references_positioning,
            "compile_proposal": self._compile_proposal,
            "delivery_summary": self._delivery_summary,
        }
        handler = dispatch.get(op)
        if not handler:
            return json.dumps({"status": "error", "message": f"Unknown operation: {op}"})
        return handler(key)

    # ── analyze_rfp ────────────────────────────────────────────
    def _analyze_rfp(self, key):
        rfp = _RFPS[key]
        matches, overall = _match_capabilities(rfp)

        req_table = "| ID | Requirement | Category | Weight | Fit Score | Evidence |\n|---|---|---|---|---|---|\n"
        for m in matches:
            req_table += (
                f"| {m['req_id']} | {m['requirement']} | {m['category']} "
                f"| {int(m['weight']*100)}% | {m['fit_score']}% | {m['evidence']} |\n"
            )

        assets = "\n".join(f"- {a}" for a in rfp["existing_assets"])

        return (
            f"**RFP Analysis: {rfp['account']} -- {rfp['project']}**\n\n"
            f"| Detail | Information |\n|---|---|\n"
            f"| RFP ID | {rfp['id']} |\n"
            f"| Account | {rfp['account']} |\n"
            f"| Deal value | ${rfp['deal_value']:,} |\n"
            f"| Budget ceiling | ${rfp['budget_ceiling']:,} |\n"
            f"| Decision timeline | {rfp['decision_timeline_days']} days |\n"
            f"| Key stakeholder | {rfp['key_stakeholder']} |\n"
            f"| Competitors shortlisted | {', '.join(rfp['competitors_shortlisted'])} |\n\n"
            f"**Requirements Analysis (Overall Fit: {overall}%):**\n\n{req_table}\n"
            f"**Existing Assets Found:**\n{assets}\n\n"
            f"Source: [CRM + RFP Document + Content Library]\n"
            f"Agents: RFPAnalysisAgent, ContentLibraryAgent"
        )

    # ── executive_summary ──────────────────────────────────────
    def _executive_summary(self, key):
        rfp = _RFPS[key]
        matches, overall = _match_capabilities(rfp)
        pricing = _compute_pricing(rfp)

        needs_table = "| Your Need | Our Solution | Fit |\n|---|---|---|\n"
        for m in matches[:4]:
            needs_table += f"| {m['requirement'][:40]} | {m['evidence'][:50]} | {m['fit_score']}% |\n"

        refs = _score_references(rfp["industry"])
        top_ref = refs[0] if refs else None
        ref_line = f"\n**Proven {rfp['industry']} Success:**\n{top_ref['customer']} achieved {top_ref['results']}.\n" if top_ref else ""

        budget_status = "within budget" if pricing["within_budget"] else "requires negotiation"
        headroom = pricing["budget_headroom"]

        return (
            f"**Executive Summary: Transforming {rfp['account']}'s Future**\n\n"
            f"{rfp['account']} has an opportunity to {rfp['project'].lower()} with a solution "
            f"that matches {overall}% of stated requirements.\n\n"
            f"**Why Us:**\n\n{needs_table}\n"
            f"**Capability Match:** {overall}% overall fit score\n"
            f"**Pricing:** ${pricing['total_proposed']:,} total ({budget_status}, "
            f"${abs(headroom):,} {'under' if headroom >= 0 else 'over'} ceiling)\n"
            f"**Margin:** {pricing['overall_margin_pct']}% gross margin maintained\n"
            f"{ref_line}\n"
            f"**Personalization Applied:**\n"
            f"- Tailored to {rfp['key_stakeholder']}'s priorities\n"
            f"- {rfp['industry']}-specific references and compliance language\n"
            f"- Matched exact RFP terminology and requirement IDs\n\n"
            f"Source: [Content Library + Stakeholder Intel]\n"
            f"Agents: ExecutiveSummaryAgent"
        )

    # ── solution_pricing ───────────────────────────────────────
    def _solution_pricing(self, key):
        rfp = _RFPS[key]
        pricing = _compute_pricing(rfp)

        # Implementation phases
        phase_lines = ""
        for p in _IMPL_PHASES:
            week_start = sum(pp["duration_weeks"] for pp in _IMPL_PHASES[:p["phase"]-1]) + 1
            week_end = week_start + p["duration_weeks"] - 1
            activities = ", ".join(p["activities"])
            phase_lines += f"\n**Phase {p['phase']}: {p['name']} (Weeks {week_start}-{week_end})**\n- {activities}\n"

        # Pricing table
        price_table = "| Component | List Price | Discount | Proposed | Savings | Margin |\n|---|---|---|---|---|---|\n"
        for item in pricing["line_items"]:
            price_table += (
                f"| {item['component']} | ${item['list_price']:,} | {item['discount_pct']}% "
                f"| ${item['proposed_price']:,} | ${item['savings']:,} | {item['margin_pct']}% |\n"
            )
        price_table += (
            f"| **Total** | **${pricing['total_list']:,}** | **{pricing['overall_discount_pct']}%** "
            f"| **${pricing['total_proposed']:,}** | **${pricing['total_savings']:,}** "
            f"| **{pricing['overall_margin_pct']}%** |\n"
        )

        budget_flag = "WITHIN" if pricing["within_budget"] else "EXCEEDS"

        return (
            f"**Solution & Pricing: {rfp['account']}**\n\n"
            f"**Implementation Approach ({_OUR_CAPABILITIES['impl_weeks']} weeks):**\n"
            f"{phase_lines}\n"
            f"**Pricing Structure:**\n\n{price_table}\n"
            f"**Budget Analysis:**\n"
            f"- Budget ceiling: ${pricing['budget_ceiling']:,}\n"
            f"- Proposed total: ${pricing['total_proposed']:,}\n"
            f"- Status: **{budget_flag}** (headroom: ${pricing['budget_headroom']:,})\n"
            f"- Overall discount: {pricing['overall_discount_pct']}%\n"
            f"- Gross margin: {pricing['overall_margin_pct']}% (floor: 35%)\n\n"
            f"Source: [Pricing Engine + Competitive Data]\n"
            f"Agents: SolutionArchitectAgent, PricingOptimizationAgent"
        )

    # ── references_positioning ─────────────────────────────────
    def _references_positioning(self, key):
        rfp = _RFPS[key]
        refs = _score_references(rfp["industry"])
        comp_keys = rfp["competitors_shortlisted"]
        matrix = _build_differentiator_matrix(comp_keys)

        # References table
        ref_table = "| Customer | Size | Results | Relevance | Contact Ready |\n|---|---|---|---|---|\n"
        for r in refs:
            ready = "Yes" if r["contact_ready"] else "On request"
            ref_table += f"| {r['customer']} | {r['size']} | {r['results']} | {r['relevance_score']}% | {ready} |\n"

        # Differentiator matrix
        comp_headers = " | ".join(comp_keys)
        matrix_header = f"| Factor | Us | {comp_headers} |\n|---|---|" + "---|" * len(comp_keys) + "\n"
        matrix_rows = ""
        for row in matrix:
            comp_vals = " | ".join(str(row.get(ck, "N/A")) for ck in comp_keys)
            matrix_rows += f"| {row['factor']} | {row['us']} | {comp_vals} |\n"

        # Objection pre-handlers from differentiators
        objections = "\n".join(f"- \"{d}\"" for d in _OUR_CAPABILITIES["differentiators"][:3])

        # Win theme
        our_impl = _OUR_CAPABILITIES["impl_weeks"]
        fastest = all(
            _COMPETITOR_CAPABILITIES.get(c, {}).get("impl_weeks", 99) > our_impl
            for c in comp_keys
        )
        theme = "Speed + Compliance + Support" if fastest else "Compliance + Integration + Support"

        return (
            f"**References & Competitive Positioning: {rfp['account']}**\n\n"
            f"**Customer References ({rfp['industry']}-weighted):**\n\n{ref_table}\n"
            f"**Win Theme: {theme}**\n\n"
            f"**Competitive Differentiator Matrix:**\n\n{matrix_header}{matrix_rows}\n"
            f"**Objection Pre-Handlers:**\n{objections}\n\n"
            f"Source: [Reference Database + Competitive Intel]\n"
            f"Agents: CompetitiveDifferentiationAgent, ContentLibraryAgent"
        )

    # ── compile_proposal ───────────────────────────────────────
    def _compile_proposal(self, key):
        rfp = _RFPS[key]
        pricing = _compute_pricing(rfp)
        matches, overall = _match_capabilities(rfp)
        refs = _score_references(rfp["industry"])

        num_reqs = len(rfp["requirements"])
        num_refs = len(refs)
        num_comps = len(rfp["competitors_shortlisted"])
        # Estimate page count from content sections
        page_count = 12 + num_reqs * 2 + num_refs * 2 + num_comps * 3 + 4

        sections = [
            ("Executive Summary (personalized)", 3),
            (f"Company Overview + {rfp['industry']} Expertise", 4),
            ("Solution Architecture + Roadmap", 6),
            (f"Implementation Methodology ({_OUR_CAPABILITIES['impl_weeks']}-week plan)", 5),
            ("Pricing + Investment Summary", 4),
            (f"Customer References + Case Studies ({num_refs})", num_refs * 2),
            ("Team Bios (Industry specialists)", 3),
            ("Terms + Conditions", 3),
        ]

        section_list = "\n".join(f"{i}. {name} ({pages} pages)" for i, (name, pages) in enumerate(sections, 1))

        certs_found = [c for c in _OUR_CAPABILITIES["certifications"]
                       if any(c.lower() in req["text"].lower() for req in rfp["requirements"])]
        cert_attachments = "\n".join(f"- {c} documentation (attached)" for c in certs_found) if certs_found else "- Standard compliance package"

        return (
            f"**Proposal Package: {rfp['account']} -- {rfp['project']}**\n\n"
            f"**Main Document ({page_count} pages):**\n{section_list}\n\n"
            f"**Supporting Materials:**\n{cert_attachments}\n"
            f"- {refs[0]['customer']} case study (2 pages)\n"
            f"- Implementation timeline visual (1 page)\n\n"
            f"**Delivery Package:**\n"
            f"- PDF proposal (branded template)\n"
            f"- Executive presentation (12 slides)\n"
            f"- Pricing spreadsheet (detailed breakdown)\n"
            f"- Reference contact sheet ({num_refs} contacts)\n\n"
            f"**Pre-Delivery Checklist:**\n"
            f"- Legal review: Approved\n"
            f"- Pricing approval: Confirmed (margin {pricing['overall_margin_pct']}% > 35% floor)\n"
            f"- Branding: Compliant\n"
            f"- Requirement coverage: {overall}% fit verified\n"
            f"- Spell check: Complete\n\n"
            f"Source: [Document Assembly + Compliance Check]\n"
            f"Agents: ProposalAssemblyAgent"
        )

    # ── delivery_summary ───────────────────────────────────────
    def _delivery_summary(self, key):
        rfp = _RFPS[key]
        matches, overall = _match_capabilities(rfp)
        pricing = _compute_pricing(rfp)
        refs = _score_references(rfp["industry"])
        win_pct, factors = _compute_win_probability(rfp, overall, pricing)

        factor_table = "| Factor | Score | Max |\n|---|---|---|\n"
        factor_table += f"| Capability fit | {factors['capability_fit']} | 30 |\n"
        factor_table += f"| Pricing strength | {factors['pricing_strength']} | 25 |\n"
        factor_table += f"| Reference strength | {factors['reference_strength']} | 20 |\n"
        factor_table += f"| Competitive position | {factors['competitive_position']} | 25 |\n"
        factor_table += f"| **Total** | **{win_pct}** | **100** |\n"

        return (
            f"**Delivery Summary: {rfp['account']} -- {rfp['project']}**\n\n"
            f"| Element | Status |\n|---|---|\n"
            f"| Capability match | {overall}% fit to {len(rfp['requirements'])} requirements |\n"
            f"| Executive summary | Personalized to {rfp['key_stakeholder']} |\n"
            f"| Solution | {_OUR_CAPABILITIES['impl_weeks']}-week implementation plan |\n"
            f"| Pricing | ${pricing['total_proposed']:,} ({pricing['overall_discount_pct']}% discount, {pricing['overall_margin_pct']}% margin) |\n"
            f"| References | {len(refs)} {rfp['industry']}-specific, contact-ready |\n"
            f"| Compliance | {', '.join(_OUR_CAPABILITIES['certifications'][:3])} included |\n\n"
            f"**Win Probability: {win_pct}%**\n\n{factor_table}\n"
            f"**Session Accomplishments:**\n"
            f"- RFP requirements mapped to capabilities ({overall}% fit)\n"
            f"- Executive summary personalized to {rfp['key_stakeholder']}\n"
            f"- Competitive positioning vs {len(rfp['competitors_shortlisted'])} shortlisted vendors\n"
            f"- Pricing optimized (${pricing['total_savings']:,} discount, {pricing['overall_margin_pct']}% margin protected)\n"
            f"- Full proposal package assembled\n\n"
            f"**Delivery Recommendation:**\n"
            f"- Submit within {rfp['decision_timeline_days']} day window\n"
            f"- Request confirmation meeting within 48 hours\n"
            f"- Offer reference calls proactively\n"
            f"- CC executive sponsor for alignment\n\n"
            f"Source: [All Proposal Systems]\n"
            f"Agents: ProposalAssemblyAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = ProposalGenerationAgent()
    for op in ["analyze_rfp", "executive_summary", "solution_pricing",
               "references_positioning", "compile_proposal", "delivery_summary"]:
        print("=" * 70)
        print(agent.perform(operation=op, rfp_name="Meridian Healthcare"))
        print()
