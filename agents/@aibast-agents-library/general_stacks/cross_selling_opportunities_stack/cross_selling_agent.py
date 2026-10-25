"""
Cross-Selling Agent

Identifies cross-selling opportunities across a SaaS company's top 100
enterprise accounts: portfolio segmentation, the top five accounts, tailored
engagement strategies, a quarterly conversion forecast, and a draft rep
assignment plan.

Where a real deployment would connect to CRM, product-usage and peer-benchmark
data, this agent uses a synthetic data layer so it runs anywhere without
credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/cross-selling",
    "version": "1.0.0",
    "display_name": "Cross Selling Opportunities Agent",
    "description": "Identify and prioritize expansion opportunities to drive revenue growth and strengthen customer relationships.",
    "author": "AIBAST",
    "tags": ["cross-sell", "upsell", "revenue", "product-affinity", "recommendations"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

# Portfolio of the top 100 enterprise accounts (synthetic aggregate).
_PORTFOLIO = {
    "accounts": 100,
    "segments": [
        {"segment": "High Priority", "accounts": 12, "potential_arr": 1400000},
        {"segment": "Medium Priority", "accounts": 20, "potential_arr": 1200000},
        {"segment": "Nurture", "accounts": 68, "potential_arr": 600000},
    ],
    "quick_wins": [
        "32 accounts showing active buying signals",
        "8 accounts exceeded usage limits this quarter",
        "5 accounts requested features in products they don't own",
    ],
    "top_signal": {"crm_without_analytics": 12, "peer_pct_with_both": 94},
}

# The five highest-value accounts. ARR potential = sum of the recommended products.
_CUSTOMER_OWNERSHIP = {
    "CUST-001": {
        "name": "Acme Corp", "current_products": ["CRM", "Marketing"],
        "recommended": [{"product": "Analytics Suite", "arr": 120000}],
        "current_spend": 85000, "health_score": 91,
        "usage": "Heavy data exports (no analytics)",
        "usage_fact": "exporting 50K records monthly",
        "champion": "VP Marketing (Sarah Chen)", "relationship": "strong relationship",
        "trigger": "Requested custom reports last week",
        "next_step": "Schedule analytics demo",
        "budget_window": "End of quarter budget available",
        "approach": "Value-led demo showcasing ROI",
        "talking_points": [
            "You're exporting 50K records monthly - Analytics automates this",
            "Similar customers saw 340% ROI in 6 months",
            "Your competitor TechGiant uses our full suite",
        ],
        "owner": "Lisa Chen",
    },
    "CUST-002": {
        "name": "TechCo Industries", "current_products": ["Basic Plan"],
        "recommended": [{"product": "Enterprise", "arr": 85000}, {"product": "Security", "arr": 30000}],
        "current_spend": 48000, "health_score": 86,
        "usage": "Exceeded plan limits 3 consecutive months (12 limit hits)",
        "usage_fact": "hit limits 12 times",
        "champion": "Director of IT", "relationship": "engaged",
        "trigger": "Exceeded limits 3 consecutive months",
        "next_step": "Usage review and Enterprise upgrade proposal",
        "budget_window": "Compliance audit budget this quarter",
        "approach": "Usage-based upgrade conversation",
        "talking_points": [
            "You've hit limits 12 times - Enterprise removes caps",
            "Security add-on addresses your compliance audit needs",
        ],
        "owner": "James Wilson",
    },
    "CUST-003": {
        "name": "GlobalRetail Inc", "current_products": ["CRM"],
        "recommended": [{"product": "Full Platform", "arr": 108000}],
        "current_spend": 60000, "health_score": 84,
        "usage": "CRM used by all regional sales teams; marketing runs on spreadsheets",
        "usage_fact": "CRM adoption across all regions",
        "champion": "VP Sales Operations", "relationship": "strong relationship",
        "trigger": "Asked about marketing automation in last QBR",
        "next_step": "Full Platform walkthrough",
        "budget_window": "Annual planning next month",
        "approach": "Platform consolidation conversation",
        "talking_points": [
            "Your CRM is used across every region - the Full Platform connects marketing to it",
            "One platform replaces the spreadsheet campaign process",
        ],
        "owner": "Mike Torres",
    },
    "CUST-004": {
        "name": "Meridian Finance", "current_products": ["Analytics"],
        "recommended": [{"product": "CRM", "arr": 76000}, {"product": "Integrations", "arr": 28000}],
        "current_spend": 52000, "health_score": 82,
        "usage": "Analytics dashboards fed by manual CRM uploads",
        "usage_fact": "uploading CRM data manually every week",
        "champion": "Head of Revenue Operations", "relationship": "engaged",
        "trigger": "Requested a CRM connector in a support ticket",
        "next_step": "Integration discovery call",
        "budget_window": "New fiscal year budget",
        "approach": "Integration-led conversation",
        "talking_points": [
            "You upload CRM data manually every week - native CRM + Integrations removes that step",
            "Analytics customers who add CRM get one revenue view",
        ],
        "owner": "James Wilson",
    },
    "CUST-005": {
        "name": "Apex Manufacturing", "current_products": ["Marketing"],
        "recommended": [{"product": "CRM", "arr": 62000}, {"product": "Analytics", "arr": 38000}],
        "current_spend": 40000, "health_score": 80,
        "usage": "Campaign leads tracked outside the platform",
        "usage_fact": "tracking campaign leads in spreadsheets",
        "champion": "Marketing Director", "relationship": "engaged",
        "trigger": "Feature request for lead scoring",
        "next_step": "Lead-to-revenue demo",
        "budget_window": "Mid-year budget review",
        "approach": "Lead-to-revenue demo",
        "talking_points": [
            "Your campaign leads leave the platform - CRM keeps them connected",
            "Analytics shows which campaigns turn into revenue",
        ],
        "owner": "Sarah Kim",
    },
}

_AFFINITY_RULES = [
    {"if_owns": "CRM", "recommend": "Analytics Suite", "affinity_score": 0.94, "success_rate": 0.50, "avg_time_to_close_days": 30},
    {"if_owns": "Basic Plan", "recommend": "Enterprise", "affinity_score": 0.88, "success_rate": 0.45, "avg_time_to_close_days": 21},
    {"if_owns": "Enterprise", "recommend": "Security", "affinity_score": 0.81, "success_rate": 0.48, "avg_time_to_close_days": 30},
    {"if_owns": "Analytics", "recommend": "CRM", "affinity_score": 0.79, "success_rate": 0.38, "avg_time_to_close_days": 45},
    {"if_owns": "Marketing", "recommend": "CRM", "affinity_score": 0.76, "success_rate": 0.38, "avg_time_to_close_days": 40},
    {"if_owns": "CRM", "recommend": "Integrations", "affinity_score": 0.72, "success_rate": 0.45, "avg_time_to_close_days": 28},
]

_CROSS_SELL_SUCCESS_RATES = {
    "Quick wins": {"avg_success_rate": 0.45, "avg_deal_cycle_days": 21, "basis": "historical"},
    "Medium priority": {"avg_success_rate": 0.38, "avg_deal_cycle_days": 45, "basis": "historical"},
    "High-value": {"avg_success_rate": 0.50, "avg_deal_cycle_days": 60, "basis": "strong signals"},
}

_FORECAST = {
    "months": [
        {"month": "Month 1", "opportunities": "32 quick wins", "closes": "12-15 deals", "arr": 540000, "close_rate": "Quick wins: 45% close rate (historical)"},
        {"month": "Month 2", "opportunities": "20 medium", "closes": "8-10 deals", "arr": 720000, "close_rate": "Medium priority: 38% close rate"},
        {"month": "Month 3", "opportunities": "12 high-value", "closes": "5-6 deals", "arr": 840000, "close_rate": "High-value: 50% close rate (strong signals)"},
    ],
    "current_pipeline": 1800000,
    "coverage_before": "1.2x",
    "coverage_after": "2.8x",
    "se_support_accounts": 12,
    "exec_sponsor_accounts": 8,
}

_REPS = [
    {"rep": "James Wilson", "accounts": 8, "arr": 680000, "specialty": "Enterprise/Security"},
    {"rep": "Lisa Chen", "accounts": 7, "arr": 520000, "specialty": "Analytics/Data"},
    {"rep": "Mike Torres", "accounts": 9, "arr": 490000, "specialty": "Marketing/CRM"},
    {"rep": "Sarah Kim", "accounts": 8, "arr": 410000, "specialty": "Manufacturing"},
]

_OUTREACH_SEQUENCE = [
    "Day 1: Personalized email with usage insights",
    "Day 3: LinkedIn touchpoint",
    "Day 5: Calendar invite for value demo",
]

_OPERATIONS = [
    "opportunity_scan", "product_affinity", "recommendation_engine", "revenue_impact",
    "portfolio_scan", "top_opportunities", "account_assignments",
]


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve_customer(query):
    """Account ID or (part of) an account name; None when nothing matches."""
    if not query:
        return "CUST-001"
    q = str(query).lower().strip()
    for key, cust in _CUSTOMER_OWNERSHIP.items():
        if key.lower() in q or q in cust["name"].lower() or cust["name"].lower() in q:
            return key
    return None


def _money_k(value):
    """$120K / $1.4M style."""
    if value >= 1000000:
        return f"${value / 1000000:.1f}M"
    return f"${round(value / 1000)}K"


def _potential(cust):
    total = 0
    for rec in cust["recommended"]:
        total += rec["arr"]
    return total


def _recommended_label(cust):
    return " + ".join(rec["product"] for rec in cust["recommended"])


def _portfolio_total():
    total = 0
    for seg in _PORTFOLIO["segments"]:
        total += seg["potential_arr"]
    return total


def _forecast_total():
    total = 0
    for row in _FORECAST["months"]:
        total += row["arr"]
    return total


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class CrossSellingAgent(BasicAgent):
    """
    Cross-selling opportunity identification agent.

    Operations:
        opportunity_scan      - one account's products, usage, buying signals and budget timing
        product_affinity      - product affinity rules and close-rate assumptions
        recommendation_engine - tailored engagement strategies, talking points and outreach sequence (drafts)
        revenue_impact        - revenue impact and quarterly conversion timeline
        portfolio_scan        - segment the top 100 enterprise accounts and surface quick wins
        top_opportunities     - top 5 highest-value opportunities with a #1 deep dive
        account_assignments   - draft rep assignments and this week's action plan
    """

    def __init__(self):
        self.name = "CrossSellingAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                f"{__manifest__['description']} Always use this tool for cross-selling, "
                "upsell and expansion questions about the top 100 enterprise accounts "
                "(Acme Corp, TechCo Industries, GlobalRetail Inc, Meridian Finance, Apex "
                "Manufacturing). Demo flow: analyze the top 100 accounts -> portfolio_scan; "
                "top 5 highest-value opportunities -> top_opportunities; engagement "
                "strategies / talking points / outreach for each -> recommendation_engine; "
                "revenue impact and conversion timeline -> revenue_impact; assign accounts "
                "and create the action plan -> account_assignments. Every operation has "
                "demo defaults, so call it without asking for an account. Uses bundled "
                "synthetic records and returns read-only analysis or drafts. It never sends "
                "outreach, changes CRM data, or claims realized revenue."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "portfolio_scan: 'analyze our top 100 enterprise accounts', "
                            "segments, quick wins, cross-selling opportunities across accounts. "
                            "top_opportunities: 'top 5 highest-value opportunities' and the #1 "
                            "account deep dive. recommendation_engine: engagement strategies, "
                            "talking points and outreach sequences for each account (drafts, "
                            "not sent). revenue_impact: revenue impact forecast and conversion "
                            "timeline by month. account_assignments: assign accounts to reps "
                            "and create the action plan. opportunity_scan: one named account's "
                            "products, usage and buying signals. product_affinity: product-"
                            "affinity rules, benchmark and close-rate assumptions."
                        ),
                    },
                    "customer_id": {
                        "type": "string",
                        "description": (
                            "Optional account ID or name for opportunity_scan or "
                            "recommendation_engine (e.g. 'CUST-001' or 'Acme Corp'). Leave "
                            "empty for the whole top-account list."
                        ),
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
        op = kwargs.get("operation", "portfolio_scan")
        source = kwargs.get("data_source", "synthetic")
        if source != "synthetic":
            return "**Error:** `data_source` must be `synthetic`."
        raw = kwargs.get("customer_id", "")
        cust_id = _resolve_customer(raw)
        if cust_id is None:
            return f"**Error:** Unknown `customer_id`. Valid: {', '.join(_CUSTOMER_OWNERSHIP)}."
        dispatch = {
            "opportunity_scan": self._opportunity_scan,
            "product_affinity": self._product_affinity,
            "recommendation_engine": self._recommendation_engine,
            "revenue_impact": self._revenue_impact,
            "portfolio_scan": self._portfolio_scan,
            "top_opportunities": self._top_opportunities,
            "account_assignments": self._account_assignments,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"Unknown operation: {op}"
        if op == "recommendation_engine":
            output = handler(cust_id if raw else None)
        else:
            output = handler(cust_id)
        return (
            output.replace("Source: [", "Synthetic source model: [")
            + "\n\n**Evidence boundary:** Exact account names, products, ARR, scores, "
            "percentages, timing, and forecast figures are synthetic planning evidence. "
            "Close rates and forecasts are scenario assumptions, not conversion or revenue "
            "claims. No outreach was sent and no CRM, pricing, approval, or customer record changed."
        )

    # ── portfolio_scan (video turn 1) ──────────────────────────
    def _portfolio_scan(self, cust_id):
        rows = ""
        for seg in _PORTFOLIO["segments"]:
            avg = seg["potential_arr"] / seg["accounts"]
            rows += f"| {seg['segment']} | {seg['accounts']} | ${seg['potential_arr'] / 1000000:.1f}M | {_money_k(avg)} |\n"
        wins = "".join(f"- {w}\n" for w in _PORTFOLIO["quick_wins"])
        sig = _PORTFOLIO["top_signal"]
        return (
            f"I've analyzed all {_PORTFOLIO['accounts']} enterprise accounts against usage patterns, "
            f"peer comparisons, and buying signals. Total expansion opportunity: "
            f"{_money_k(_portfolio_total())} ARR.\n\n"
            f"**Cross-Sell Opportunity Summary**\n\n"
            f"| Segment | Accounts | Potential ARR | Avg Deal |\n|---|---|---|---|\n{rows}\n"
            f"**Quick Wins (Ready for Outreach):**\n{wins}\n"
            f"**Top Signal:** {sig['crm_without_analytics']} accounts using CRM but not Analytics - "
            f"peer data shows {sig['peer_pct_with_both']}% of similar companies have both.\n\n"
            f"Source: [CRM + Usage Analytics + Peer Benchmarks]\n"
            f"Agents: CrossSellingAgent\n\n"
            f"Want to see the top 5 highest-value opportunities?"
        )

    # ── top_opportunities (video turn 2) ───────────────────────
    def _top_opportunities(self, cust_id):
        rows, total = "", 0
        for cust in _CUSTOMER_OWNERSHIP.values():
            pot = _potential(cust)
            total += pot
            rows += (f"| {cust['name']} | {', '.join(cust['current_products'])} | "
                     f"{_recommended_label(cust)} | {_money_k(pot)} |\n")
        top = _CUSTOMER_OWNERSHIP["CUST-001"]
        return (
            f"Top 5 opportunities represent {_money_k(total)} in potential ARR. All have strong "
            f"buying signals and account health.\n\n"
            f"**Top Cross-Sell Opportunities**\n\n"
            f"| Account | Current Products | Recommended | ARR Potential |\n|---|---|---|---|\n{rows}\n"
            f"**#1 {top['name']} - Deep Dive:**\n"
            f"- Current spend: {_money_k(top['current_spend'])}/year\n"
            f"- Usage: {top['usage']}\n"
            f"- Champion: VP Marketing ({top['relationship']})\n"
            f"- Trigger: {top['trigger']}\n"
            f"- Next step: {top['next_step']}\n\n"
            f"Source: [CRM + Product Usage + Support Tickets]\n"
            f"Agents: CrossSellingAgent\n\n"
            f"Should I create engagement strategies for each?"
        )

    # ── recommendation_engine (video turn 3) ───────────────────
    def _strategy_block(self, cust):
        points = "".join(f"  {i}. \"{p}\"\n" for i, p in enumerate(cust["talking_points"], 1))
        return (
            f"**{cust['name']} Strategy:**\n"
            f"- Approach: {cust['approach']}\n"
            f"- Recommended: {_recommended_label(cust)} ({_money_k(_potential(cust))} ARR potential)\n"
            f"- Champion: {cust['champion']}\n"
            f"- Trigger: {cust['trigger']}\n"
            f"- Timing: {cust['budget_window']}\n"
            f"- Talking Points:\n{points}\n"
        )

    def _recommendation_engine(self, cust_id):
        if cust_id:
            accounts = [_CUSTOMER_OWNERSHIP[cust_id]]
            title = f"Prioritized Recommendations: {accounts[0]['name']}"
        else:
            accounts = list(_CUSTOMER_OWNERSHIP.values())
            title = "Prioritized Recommendations: Top 5 Accounts"
        blocks = "".join(self._strategy_block(c) for c in accounts)
        seq = "".join(f"- {s}\n" for s in _OUTREACH_SEQUENCE)
        return (
            f"**{title}**\n\n"
            f"Personalized engagement strategies created for each account with specific talking "
            f"points and timing recommendations.\n\n"
            f"{blocks}"
            f"**Draft Engagement Plan (not sent) - Outreach Sequence:**\n{seq}\n"
            f"Talking points are synthetic examples: verify the ROI benchmark and any competitor "
            f"reference before use, and confirm contact consent before outreach.\n\n"
            f"Source: [Sales Playbook + Customer Intelligence]\n"
            f"Agents: CrossSellingAgent\n\n"
            f"Want to see the revenue impact forecast?"
        )

    # ── revenue_impact (video turn 4) ──────────────────────────
    def _revenue_impact(self, cust_id):
        rows = ""
        for row in _FORECAST["months"]:
            rows += f"| {row['month']} | {row['opportunities']} | {row['closes']} | {_money_k(row['arr'])} |\n"
        rates = "".join(f"- {row['close_rate']}\n" for row in _FORECAST["months"])
        current = _FORECAST["current_pipeline"]
        after = current + _portfolio_total()
        growth = round((after - current) * 100 / current)
        return (
            f"**Synthetic Cross-Sell Value Scenario**\n\n"
            f"Revenue model shows {_money_k(_forecast_total())} realizable ARR this quarter with a "
            f"staged conversion timeline.\n\n"
            f"**Quarterly Revenue Forecast**\n\n"
            f"| Month | Opportunities | Expected Closes | ARR Impact |\n|---|---|---|---|\n{rows}\n"
            f"**Conversion Assumptions:**\n{rates}\n"
            f"**Portfolio Totals - Pipeline Impact:**\n"
            f"- Current expansion pipeline: {_money_k(current)}\n"
            f"- After this analysis: {_money_k(after)} (+{growth}%)\n"
            f"- Quota coverage: {_FORECAST['coverage_after']} (vs {_FORECAST['coverage_before']} before)\n\n"
            f"**Resource Needs:**\n"
            f"- {_FORECAST['se_support_accounts']} accounts need SE support for demos\n"
            f"- {_FORECAST['exec_sponsor_accounts']} accounts need executive sponsor intro\n\n"
            f"Source: [Revenue Analytics + Historical Conversion]\n"
            f"Agents: CrossSellingAgent\n\n"
            f"Want me to assign accounts and create the action plan?"
        )

    # ── account_assignments (video turn 5) ─────────────────────
    def _account_assignments(self, cust_id):
        rows, n, arr = "", 0, 0
        for r in _REPS:
            n += r["accounts"]
            arr += r["arr"]
            rows += f"| {r['rep']} | {r['accounts']} | {_money_k(r['arr'])} | {r['specialty']} |\n"
        top = "".join(f"- {c['name']} -> {c['owner']}\n" for c in _CUSTOMER_OWNERSHIP.values())
        return (
            f"**Draft Account Assignments**\n\n"
            f"Accounts matched to reps by expertise and existing relationships; the action plan "
            f"below is a draft for your review.\n\n"
            f"| Rep | Accounts | Total ARR | Specialty Match |\n|---|---|---|---|\n{rows}"
            f"| **Total** | **{n}** | **{_money_k(arr)}** | |\n\n"
            f"**Top 5 owners:**\n{top}\n"
            f"**This Week's Actions (drafts ready for you to send):**\n"
            f"- Today: 32 quick-win outreach emails (templates ready, not sent)\n"
            f"- Tomorrow: Schedule 12 SE demos\n"
            f"- Friday: Executive intro requests to leadership\n\n"
            f"**Recommended Triggers (not enabled):**\n"
            f"- Alerts when accounts log in\n"
            f"- Email notifications on feature requests\n"
            f"- Weekly pipeline review dashboard\n\n"
            f"**Team Briefing:** proposed for tomorrow 9 AM with account dossiers; the plan is ready "
            f"for you to share in Microsoft Teams.\n\n"
            f"Source: [CRM + Team Capacity + Calendar]\n"
            f"Agents: CrossSellingAgent\n\n"
            f"Want a summary of everything we accomplished?"
        )

    # ── opportunity_scan (one account) ─────────────────────────
    def _opportunity_scan(self, cust_id):
        cust = _CUSTOMER_OWNERSHIP[cust_id]
        recs = "".join(f"| {r['product']} | {_money_k(r['arr'])} |\n" for r in cust["recommended"])
        return (
            f"**Cross-Sell Opportunity Scan: {cust['name']}**\n\n"
            f"| Field | Detail |\n|---|---|\n"
            f"| Account ID | {cust_id} |\n"
            f"| Current Products | {', '.join(cust['current_products'])} |\n"
            f"| Current Spend | {_money_k(cust['current_spend'])}/year |\n"
            f"| Health Score | {cust['health_score']}/100 |\n"
            f"| Champion | {cust['champion']} |\n"
            f"| Owner | {cust['owner']} |\n\n"
            f"**Synthetic Usage Signals:**\n- {cust['usage']}\n\n"
            f"**Synthetic Buying Signals:**\n- {cust['trigger']}\n"
            f"- Budget timing assumption: {cust['budget_window']}\n\n"
            f"**Recommended Products:**\n\n| Product | ARR Potential |\n|---|---|\n{recs}"
            f"| **Total** | **{_money_k(_potential(cust))}** |\n\n"
            f"**Next step:** {cust['next_step']}\n\n"
            f"Source: [CRM + Product Usage + Support Tickets]\nAgents: CrossSellingAgent"
        )

    # ── product_affinity ───────────────────────────────────────
    def _product_affinity(self, cust_id):
        rule_rows = ""
        for r in _AFFINITY_RULES:
            rule_rows += (f"| {r['if_owns']} | {r['recommend']} | {r['affinity_score']:.0%} | "
                          f"{r['success_rate']:.0%} | {r['avg_time_to_close_days']}d |\n")
        seg_rows = ""
        for seg, data in _CROSS_SELL_SUCCESS_RATES.items():
            seg_rows += f"| {seg} | {data['avg_success_rate']:.0%} | {data['avg_deal_cycle_days']}d | {data['basis']} |\n"
        sig = _PORTFOLIO["top_signal"]
        return (
            f"**Product Affinity Matrix**\n\n"
            f"| If Customer Owns | Recommend | Affinity | Synthetic Response Assumption | Synthetic Cycle |\n|---|---|---|---|---|\n"
            f"{rule_rows}\n"
            f"**Peer benchmark:** {sig['peer_pct_with_both']}% of similar companies own both CRM and Analytics.\n\n"
            f"**Segment Benchmarks:**\n\n"
            f"| Segment | Response Assumption | Cycle Assumption | Basis |\n|---|---|---|---|\n"
            f"{seg_rows}\n"
            f"Source: [Affinity Engine + Historical Data]\nAgents: CrossSellingAgent"
        )


if __name__ == "__main__":
    agent = CrossSellingAgent()
    for op in ["portfolio_scan", "top_opportunities", "recommendation_engine",
               "revenue_impact", "account_assignments"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
