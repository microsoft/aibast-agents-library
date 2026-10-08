"""
Proposal Generation Agent

Analyzes RFPs, generates executive summaries, builds solution pricing,
selects references, assembles proposal packages, and computes win probability.
Uses synthetic data for CRM, product catalog, reference database, and
competitive intelligence so the agent runs anywhere without credentials.

Demo scenario (the default): Meridian Healthcare's $1.2M digital transformation
RFP, CIO Amanda Foster, two shortlisted vendors, a 12-week plan priced at
$1.18M (13% savings, 42% margin against a 40% target), three healthcare
references and a 38-page draft package.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/proposal-generation",
    "version": "1.0.0",
    "display_name": "Proposal Generation Agent",
    "description": "Automate proposal creation to accelerate deal cycles, improve win rates, and deliver consistent, high-quality responses.",
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
            {"id": "R1", "text": "EHR integration", "category": "Technical", "weight": 0.25},
            {"id": "R2", "text": "HIPAA compliance", "category": "Compliance", "weight": 0.25},
            {"id": "R3", "text": "24/7 support", "category": "Support", "weight": 0.15},
            {"id": "R4", "text": "16-week implementation", "category": "Delivery", "weight": 0.20},
            {"id": "R5", "text": "Training", "category": "Training", "weight": 0.15},
        ],
        "summary_rows": [
            ["EHR Integration", "Epic & Cerner certified"],
            ["HIPAA Compliance", "SOC 2 + HIPAA certified"],
            ["Deployment", "12 weeks (beats your 16)"],
            ["Support", "24/7, 15-min SLA"],
        ],
        "existing_assets": ["Healthcare case study", "HIPAA docs", "Implementation deck"],
        "certificates": ["HIPAA", "SOC 2"],
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
        "summary_rows": [
            ["Multi-cloud", "AWS + Azure orchestration layer"],
            ["Zero downtime", "Blue-green migration with rollback"],
            ["Compliance", "SOC 2 Type II audit current"],
            ["Support", "24/7 managed services, 15-min SLA"],
        ],
        "existing_assets": ["Cloud migration playbook", "SOC 2 Type II audit report", "Multi-cloud architecture reference"],
        "certificates": ["SOC 2"],
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
        "summary_rows": [
            ["Real-time processing", "Sub-30ms transaction processing"],
            ["Compliance", "PCI-DSS Level 1 certified"],
            ["Uptime", "Architecture supports five-nines"],
            ["Rollout", "Branch-by-branch methodology"],
        ],
        "existing_assets": ["Financial services case study (Atlantic Credit Union)", "PCI-DSS compliance package", "Branch rollout methodology"],
        "certificates": ["PCI-DSS Level 1", "SOC 2"],
    },
}

# Pricing groups shown in the proposal: Software, Implementation, Training + Support.
# cost = synthetic delivery cost used for the margin check.
_PRODUCT_CATALOG = {
    "platform_core": {"name": "Platform Core License", "list_price": 421_000, "group": "Software", "cost": 190_000},
    "integration_suite": {"name": "Integration Suite", "list_price": 180_000, "group": "Software", "cost": 85_000},
    "analytics_module": {"name": "Analytics & Reporting", "list_price": 80_000, "group": "Software", "cost": 35_000},
    "implementation": {"name": "Implementation Services", "list_price": 382_000, "group": "Implementation", "cost": 238_000},
    "training": {"name": "Training Program", "list_price": 113_000, "group": "Training + Support", "cost": 61_400},
    "support_3yr": {"name": "3-Year Premium Support", "list_price": 180_000, "group": "Training + Support", "cost": 75_000},
}

_SOLUTION_CONFIGS = {
    "Healthcare": ["platform_core", "integration_suite", "analytics_module", "implementation", "training", "support_3yr"],
    "Technology": ["platform_core", "integration_suite", "implementation", "training", "support_3yr"],
    "Financial Services": ["platform_core", "integration_suite", "analytics_module", "implementation", "training", "support_3yr"],
}

_GROUP_DISCOUNTS = [
    {"group": "Software", "discount_pct": 9},
    {"group": "Implementation", "discount_pct": 11},
    {"group": "Training + Support", "discount_pct": 25},
]

_MARGIN_TARGET_PCT = 40

_REFERENCES = [
    {"customer": "Memorial Health", "industry": "Healthcare", "size": "8 facilities",
     "headline": "34% efficiency gain", "results": "34% efficiency gain, $2.4M savings", "impl_weeks": 11, "contact_ready": True},
    {"customer": "Pacific Medical", "industry": "Healthcare", "size": "15 facilities",
     "headline": "$2.4M/year savings", "results": "$2.4M/year savings, 99.9% uptime", "impl_weeks": 14, "contact_ready": True},
    {"customer": "Summit Healthcare", "industry": "Healthcare", "size": "6 facilities",
     "headline": "12-week go-live", "results": "12-week go-live, 28% cost reduction", "impl_weeks": 12, "contact_ready": True},
    {"customer": "Atlas Cloud Services", "industry": "Technology", "size": "800 employees",
     "headline": "Zero-downtime migration", "results": "Zero-downtime migration, 40% infra cost reduction", "impl_weeks": 10, "contact_ready": True},
    {"customer": "Nexus Software Corp", "industry": "Technology", "size": "2,400 employees",
     "headline": "3x deployment velocity", "results": "3x deployment velocity, 99.95% uptime", "impl_weeks": 8, "contact_ready": False},
    {"customer": "Atlantic Credit Union", "industry": "Financial Services", "size": "120 branches",
     "headline": "Sub-30ms latency", "results": "Sub-30ms latency, zero audit findings", "impl_weeks": 16, "contact_ready": True},
    {"customer": "Sentinel Insurance", "industry": "Financial Services", "size": "$4B AUM",
     "headline": "PCI-DSS compliant in 90 days", "results": "PCI-DSS compliant in 90 days, 22% ops savings", "impl_weeks": 14, "contact_ready": True},
    {"customer": "Vanguard Logistics", "industry": "Manufacturing", "size": "3,200 employees",
     "headline": "18% throughput improvement", "results": "18% throughput improvement", "impl_weeks": 12, "contact_ready": False},
]

_COMPETITOR_CAPABILITIES = {
    "CompetitorA": {
        "impl_weeks": 20, "hipaa_certified": True, "ehr_integration": "Third-party",
        "support_sla_min": 240, "pricing_position": "Market rate",
        "strengths": ["Large install base", "Brand recognition"],
        "weaknesses": ["Slow implementation", "Middleware dependency"],
    },
    "CompetitorB": {
        "impl_weeks": 16, "hipaa_certified": False, "ehr_integration": "Third-party",
        "support_sla_min": 60, "pricing_position": "+5% above market",
        "strengths": ["Modern UI", "Aggressive pricing on licenses"],
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
        "Native Epic integration eliminates middleware costs",
        "15-minute support SLA is fastest in industry",
        "API-first architecture for seamless ecosystem integration",
    ],
}

_CAPABILITY_FIT = [
    {"keyword": "ehr", "score": 95, "evidence": "Native Epic & Cerner connectors, certified"},
    {"keyword": "hipaa", "score": 100, "evidence": "SOC 2 Type II + HIPAA certified"},
    {"keyword": "24/7", "score": 98, "evidence": "24/7/365 with 15-min response SLA"},
    {"keyword": "implementation", "score": 92, "evidence": "12-week methodology with accelerators"},
    {"keyword": "training", "score": 92, "evidence": "Role-based curriculum with certification"},
    {"keyword": "multi-cloud", "score": 91, "evidence": "AWS + Azure + GCP orchestration layer"},
    {"keyword": "zero-downtime", "score": 93, "evidence": "Blue-green deployment with automated rollback"},
    {"keyword": "soc 2", "score": 100, "evidence": "SOC 2 Type II audit current"},
    {"keyword": "knowledge transfer", "score": 85, "evidence": "Structured runbook and shadowing program"},
    {"keyword": "real-time", "score": 87, "evidence": "Sub-30ms processing demonstrated at Atlantic CU"},
    {"keyword": "pci-dss", "score": 100, "evidence": "PCI-DSS Level 1 certified"},
    {"keyword": "99.999%", "score": 88, "evidence": "99.99% historical, architecture supports five-nines"},
    {"keyword": "phased rollout", "score": 92, "evidence": "Proven branch-by-branch methodology"},
]

_IMPL_PHASES = [
    {"phase": 1, "name": "Foundation", "duration_weeks": 4,
     "activities": ["Infrastructure assessment", "Connector deployment", "Security configuration", "Core team training"]},
    {"phase": 2, "name": "Rollout", "duration_weeks": 6,
     "activities": ["Phased facility deployment", "Workflow integration", "Staff certification", "Go-live support"]},
    {"phase": 3, "name": "Optimization", "duration_weeks": 2,
     "activities": ["Performance tuning", "Advanced training", "Success metrics validation", "Handoff to support"]},
]

_PROPOSAL_SECTIONS = [
    {"section": "Executive Summary (personalized)", "pages": 3},
    {"section": "Company Overview + Industry Expertise", "pages": 4},
    {"section": "Solution Architecture + Roadmap", "pages": 8},
    {"section": "12-week Implementation Plan", "pages": 5},
    {"section": "Pricing + Investment Summary", "pages": 4},
    {"section": "Customer References + Case Studies", "pages": 6},
    {"section": "Team Bios (Industry specialists)", "pages": 3},
    {"section": "Terms + Conditions", "pages": 5},
]

_DELIVERY_PACKAGE = ["PDF proposal", "12-slide exec presentation", "pricing spreadsheet"]


# ═══════════════════════════════════════════════════════════════
# HELPERS -- real computation, synthetic inputs
# ═══════════════════════════════════════════════════════════════

def _resolve_rfp(query):
    """Match an RFP or account name to synthetic data (default Meridian Healthcare)."""
    if not query:
        return "meridian"
    q = query.lower().strip()
    for key in _RFPS:
        if key in q or q in _RFPS[key]["account"].lower():
            return key
    return None


def _money_short(amount):
    """$1,180,000 -> '$1.18M'; $620,000 -> '$620K'."""
    if amount >= 1_000_000 and amount % 100_000 == 0:
        return f"${amount / 1_000_000:.1f}M"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    return f"${amount // 1000}K"


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


def _score_references(industry):
    """Same-industry references in catalog order; the top three overall when none match."""
    same = [r for r in _REFERENCES if r["industry"] == industry]
    return same[:3] if same else _REFERENCES[:3]


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


def _timeline_text(days):
    """14 -> '2 weeks'; 30 -> '30 days'."""
    return f"{days // 7} weeks" if days % 7 == 0 else f"{days} days"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class ProposalGenerationAgent(BasicAgent):
    """
    Generates complete sales proposals from RFP analysis through delivery.

    Operations:
        analyze_rfp          - Deal context, RFP requirements and existing assets
        executive_summary    - Need -> solution summary for the key stakeholder with proof and investment
        solution_pricing     - 12-week plan + Software / Implementation / Training + Support pricing and margin
        references_positioning - Same-industry references, edge vs competition, win theme
        compile_proposal     - Draft proposal package (page count, contents, delivery files, review checklist)
        delivery_summary     - Final readiness summary with computed win probability
    """

    def __init__(self):
        self.name = "ProposalGenerationAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always use this tool when a seller is building a "
                "proposal: 'create a proposal for Meridian Healthcare' uses analyze_rfp; "
                "'create the executive summary' uses executive_summary; 'build out the solution "
                "section and pricing' uses solution_pricing; 'add the strongest references and "
                "competitive positioning' uses references_positioning; 'compile the final proposal "
                "and prepare for delivery' uses compile_proposal. The default account is Meridian "
                "Healthcare. Uses bundled synthetic RFP evidence and produces read-only draft content "
                "only; no proposal is delivered, no price is approved, and no customer communication "
                "is sent. Route requests to outline, assemble, compile, structure, or checklist a "
                "proposal package to `compile_proposal`; that operation returns `Proposal Package` "
                "and `Required Human Review Before Delivery`."
            ),
            "operations": [
                "analyze_rfp", "executive_summary", "solution_pricing",
                "references_positioning", "compile_proposal", "delivery_summary",
            ],
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
                        "description": (
                            "Select the requested proposal deliverable. analyze_rfp: 'I need to create a "
                            "proposal for ...' - deal value, decision timeline, stakeholder, competition, "
                            "requirements and existing assets. executive_summary: buyer-aligned draft "
                            "summary with proof and investment. solution_pricing: 'build out the solution "
                            "section and pricing' - 12-week plan, pricing, savings and margin. "
                            "references_positioning: strongest references, edge vs competition, win theme. "
                            "compile_proposal: REQUIRED for compiling the final proposal, preparing for "
                            "delivery, outlining, assembling, or checklisting the proposal package; returns "
                            "Proposal Package and Required Human Review Before Delivery. "
                            "delivery_summary: concise readiness summary, win probability and next-step options."
                        ),
                    },
                    "rfp_name": {
                        "type": "string",
                        "enum": ["Meridian Healthcare", "Contoso Technologies", "Pinnacle Financial Group"],
                        "description": "RFP or account name (default 'Meridian Healthcare')",
                    },
                    "data_source": {
                        "type": "string",
                        "enum": ["synthetic"],
                        "description": "Deterministic source route. Only bundled synthetic evidence is supported.",
                    },
                },
                "required": ["operation"],
                "additionalProperties": False,
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "analyze_rfp")
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
        key = _resolve_rfp(kwargs.get("rfp_name", ""))
        if key is None:
            return (
                "**Error:** Unknown `rfp_name`. Valid synthetic accounts: "
                "Meridian Healthcare, Contoso Technologies, Pinnacle Financial Group."
            )
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
        output = handler(key)
        return (
            output.replace("Source: [", "Synthetic source model: [")
            + "\n\n**Evidence boundary:** Exact names, dates, requirements, prices, "
            "discounts, margins, fit scores, and projections are synthetic planning evidence. "
            "This read-only output did not approve pricing, create a final document, submit "
            "a response, contact a reference, or communicate with a customer."
        )

    # ── analyze_rfp ────────────────────────────────────────────
    def _analyze_rfp(self, key):
        rfp = _RFPS[key]
        matches, overall = _match_capabilities(rfp)
        req_table = "| ID | Requirement | Category | Weight | Fit Score | Evidence |\n|---|---|---|---|---|---|\n"
        for m in matches:
            req_table += (
                f"| {m['req_id']} | {m['requirement']} | {m['category']} "
                f"| {int(m['weight'] * 100)}% | {m['fit_score']}% | {m['evidence']} |\n"
            )
        requirements = ", ".join(r["text"] for r in rfp["requirements"])
        return (
            f"**RFP Analysis: {rfp['account']} -- {rfp['project']}**\n\n"
            f"Context pulled for {rfp['account']} proposal:\n\n"
            f"| Detail | Info |\n|---|---|\n"
            f"| Deal value | {_money_short(rfp['deal_value'])} |\n"
            f"| Decision | {_timeline_text(rfp['decision_timeline_days'])} |\n"
            f"| Stakeholder | {rfp['key_stakeholder']} |\n"
            f"| Competition | {len(rfp['competitors_shortlisted'])} vendors shortlisted |\n"
            f"| RFP ID | {rfp['id']} |\n"
            f"| Budget ceiling | ${rfp['budget_ceiling']:,} |\n\n"
            f"**RFP Requirements:** {requirements}\n\n"
            f"**Requirements Analysis (Overall Fit: {overall}%):**\n\n{req_table}\n"
            f"**Existing Assets Found:** {', '.join(rfp['existing_assets'])}\n\n"
            f"Next: generate the executive summary?\n\n"
            f"Source: [CRM + RFP Document + Content Library]\n"
            f"Agents: RFPAnalysisAgent, ContentLibraryAgent"
        )

    # ── executive_summary ──────────────────────────────────────
    def _executive_summary(self, key):
        rfp = _RFPS[key]
        matches, overall = _match_capabilities(rfp)
        pricing = _compute_pricing(rfp)
        refs = _score_references(rfp["industry"])
        needs_table = "| Your Need | Our Solution |\n|---|---|\n"
        for need, solution in rfp["summary_rows"]:
            needs_table += f"| {need} | {solution} |\n"
        return (
            f"**Executive Summary: {rfp['account']} -- personalized to {rfp['key_stakeholder']}**\n\n"
            f"{rfp['account']} has an opportunity to modernize with a {rfp['project'].lower()} "
            f"that matches {overall}% of the stated requirements.\n\n"
            f"{needs_table}\n"
            f"**Proof:** {refs[0]['customer']} achieved {refs[0]['results']}\n"
            f"**Investment:** {_money_short(pricing['total_proposed'])} (3 years support + training included)\n\n"
            f"**Personalization Applied:**\n"
            f"- Tailored to {rfp['key_stakeholder']}'s priorities\n"
            f"- {rfp['industry']}-specific references and compliance language\n"
            f"- Matched exact RFP terminology and requirement IDs\n\n"
            f"Next: proceed to solution and pricing?\n\n"
            f"Source: [Content Library + Stakeholder Intel]\n"
            f"Agents: ExecutiveSummaryAgent"
        )

    # ── solution_pricing ───────────────────────────────────────
    def _solution_pricing(self, key):
        rfp = _RFPS[key]
        pricing = _compute_pricing(rfp)
        plan, phase_lines, week = [], "", 1
        for p in _IMPL_PHASES:
            end = week + p["duration_weeks"] - 1
            plan.append(f"{p['name']} (wks {week}-{end})")
            phase_lines += f"- **{p['name']} (wks {week}-{end}):** {', '.join(p['activities'])}\n"
            week = end + 1
        price_table = "| Component | List Price | Proposed | Savings |\n|---|---|---|---|\n"
        for g in pricing["groups"]:
            price_table += (
                f"| {g['group']} | ${g['list_price']:,} | {_money_short(g['proposed'])} | {g['savings_pct']}% |\n"
            )
        price_table += (
            f"| **Total** | **${pricing['total_list']:,}** | **{_money_short(pricing['total_proposed'])}** "
            f"| **{pricing['overall_discount_pct']}%** |\n"
        )
        margin_ok = "maintained" if pricing["overall_margin_pct"] >= pricing["margin_target_pct"] else "below target"
        return (
            f"**Solution & Pricing: {rfp['account']}**\n\n"
            f"**{_OUR_CAPABILITIES['impl_weeks']}-Week Plan:** {' > '.join(plan)}\n\n"
            f"{phase_lines}\n"
            f"{price_table}\n"
            f"**Margin:** {pricing['overall_margin_pct']}% {margin_ok} (target {pricing['margin_target_pct']}%+)\n\n"
            f"**Budget Analysis:**\n"
            f"- Budget ceiling: ${pricing['budget_ceiling']:,}\n"
            f"- Proposed total: ${pricing['total_proposed']:,} "
            f"({'within budget' if pricing['within_budget'] else 'exceeds budget'}, "
            f"${abs(pricing['budget_headroom']):,} headroom)\n"
            f"- Customer savings: ${pricing['total_savings']:,} ({pricing['overall_discount_pct']}%)\n"
            f"- Pricing is a draft for an authorized pricing approver.\n\n"
            f"Next: add references and differentiators?\n\n"
            f"Source: [Pricing Engine + Competitive Data]\n"
            f"Agents: SolutionArchitectAgent, PricingOptimizationAgent"
        )

    # ── references_positioning ─────────────────────────────────
    def _references_positioning(self, key):
        rfp = _RFPS[key]
        refs = _score_references(rfp["industry"])
        edge = _competitive_edge(rfp)
        ref_table = "| Reference | Results | Size | Contact Ready |\n|---|---|---|---|\n"
        for r in refs:
            ready = "Yes" if r["contact_ready"] else "On request"
            ref_table += f"| {r['customer']} | {r['headline']} | {r['size']} | {ready} |\n"
        objections = "\n".join(f"- \"{d}\"" for d in _OUR_CAPABILITIES["differentiators"][:3])
        return (
            f"**References & Competitive Positioning: {rfp['account']}**\n\n"
            f"{ref_table}\n"
            f"**Your Edge vs Competition:**\n"
            f"- Implementation: {edge['implementation']}\n"
            f"- Epic integration: {edge['integration']}\n"
            f"- Support SLA: {edge['support']}\n\n"
            f"**Win Theme: {edge['theme']}**\n\n"
            f"**Objection Pre-Handlers:**\n{objections}\n\n"
            f"Confirm each reference's availability before offering a call.\n\n"
            f"Next: generate the final proposal?\n\n"
            f"Source: [Reference Database + Competitive Intel]\n"
            f"Agents: CompetitiveDifferentiationAgent, ContentLibraryAgent"
        )

    # ── compile_proposal ───────────────────────────────────────
    def _compile_proposal(self, key):
        rfp = _RFPS[key]
        pricing = _compute_pricing(rfp)
        matches, overall = _match_capabilities(rfp)
        refs = _score_references(rfp["industry"])
        page_count = sum(s["pages"] for s in _PROPOSAL_SECTIONS)
        section_list = "\n".join(
            f"{i}. {s['section']} ({s['pages']} pages)" for i, s in enumerate(_PROPOSAL_SECTIONS, 1)
        )
        certificates = " + ".join(rfp["certificates"])
        return (
            f"**Proposal Package: {rfp['account']} -- {rfp['project']}**\n\n"
            f"Final proposal compiled as a draft ({page_count} pages), ready for your review.\n\n"
            f"**Package Contents:**\n"
            f"- Executive Summary + Solution Architecture\n"
            f"- {_OUR_CAPABILITIES['impl_weeks']}-week Implementation Plan\n"
            f"- Pricing ({_money_short(pricing['total_proposed'])}) + References ({len(refs)})\n"
            f"- {certificates} certificates attached\n\n"
            f"**Sections:**\n{section_list}\n\n"
            f"**Delivery Package (drafts):** {', '.join(_DELIVERY_PACKAGE)}\n\n"
            f"**Checklist:** Legal - ready for review; Pricing - ready for approval; Branding - applied, ready for review\n\n"
            f"**Required Human Review Before Delivery:**\n"
            f"- Legal review by your legal team\n"
            f"- Pricing approval from an authorized approver\n"
            f"- Branding and editorial check\n"
            f"- Requirement coverage: synthetic fit model reports {overall}%\n\n"
            f"Nothing has been sent: you share the package with {rfp['key_stakeholder']} "
            f"(for example through Microsoft Teams) after review.\n\n"
            f"Next: review the final summary?\n\n"
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
            f"| Pricing | {_money_short(pricing['total_proposed'])} ({pricing['overall_discount_pct']}% savings, "
            f"{pricing['overall_margin_pct']}% margin vs {pricing['margin_target_pct']}% target) |\n"
            f"| References | {len(refs)} synthetic {rfp['industry']} examples requiring availability review |\n"
            f"| Compliance | {' + '.join(rfp['certificates'])} certificates attached |\n\n"
            f"**Synthetic Win-Probability Indicator: {win_pct}%**\n\n{factor_table}\n"
            f"**Session Accomplishments:**\n"
            f"- RFP requirements mapped to capabilities ({overall}% fit)\n"
            f"- Executive summary personalized to {rfp['key_stakeholder']}\n"
            f"- Competitive positioning vs {len(rfp['competitors_shortlisted'])} shortlisted vendors\n"
            f"- Pricing optimized (${pricing['total_savings']:,} customer savings, {pricing['overall_margin_pct']}% margin protected)\n"
            f"- Draft proposal package prepared for review\n\n"
            f"**Human-Governed Next-Step Options:**\n"
            f"- Review the draft against the {_timeline_text(rfp['decision_timeline_days'])} decision window\n"
            f"- Decide whether an authorized seller should request a confirmation meeting\n"
            f"- Validate reference availability before offering any calls\n"
            f"- Decide whether executive sponsorship is appropriate\n\n"
            f"Source: [All Proposal Systems]\n"
            f"Agents: ProposalAssemblyAgent (orchestrating all agents)"
        )


if __name__ == "__main__":
    agent = ProposalGenerationAgent()
    # The demo video's turns, in order, then the readiness summary.
    for op in ["analyze_rfp", "executive_summary", "solution_pricing",
               "references_positioning", "compile_proposal", "delivery_summary"]:
        print("=" * 70)
        print(agent.perform(operation=op, rfp_name="Meridian Healthcare"))
        print()
