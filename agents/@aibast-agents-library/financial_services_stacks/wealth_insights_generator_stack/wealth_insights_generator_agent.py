"""
Wealth Insights Generator Agent — Financial Services Stack

Generates market briefs, client insights, opportunity alerts, and
performance attribution reports for wealth management teams.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/wealth-insights-generator",
    "version": "1.0.0",
    "display_name": "Wealth Insights Generator Agent",
    "description": "Deliver AI-powered portfolio intelligence to uncover hidden asset opportunities, strengthen client relationships, and drive advisory growth at scale.",
    "author": "AIBAST",
    "tags": ["wealth", "insights", "market", "performance", "analytics", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

MARKET_DATA = {
    "S&P 500": {"current": 5285.42, "ytd_return": 4.8, "pe_ratio": 22.1, "dividend_yield": 1.35},
    "NASDAQ Composite": {"current": 16742.15, "ytd_return": 6.2, "pe_ratio": 28.5, "dividend_yield": 0.72},
    "Dow Jones Industrial": {"current": 39180.50, "ytd_return": 3.1, "pe_ratio": 19.8, "dividend_yield": 1.82},
    "MSCI EAFE": {"current": 2385.70, "ytd_return": 5.5, "pe_ratio": 15.2, "dividend_yield": 2.95},
    "Bloomberg US Agg Bond": {"current": 98.45, "ytd_return": 1.2, "pe_ratio": 0, "dividend_yield": 4.45},
    "10-Year Treasury": {"current": 4.28, "ytd_return": 0, "pe_ratio": 0, "dividend_yield": 4.28},
    "Gold (per oz)": {"current": 2185.30, "ytd_return": 8.1, "pe_ratio": 0, "dividend_yield": 0},
}

CLIENT_PORTFOLIOS = {
    "WM-001": {
        "name": "Harrison Family Trust",
        "aum": 8500000,
        "strategy": "balanced_growth",
        "ytd_return": 5.2,
        "benchmark_return": 4.1,
        "alpha": 1.1,
        "risk_profile": "moderate",
        "next_review": "Q2 review",
        "life_events": ["Daughter starting college next fall"],
        "held_away_assets": 620000,
    },
    "WM-002": {
        "name": "Dr. Anita Rao",
        "aum": 3200000,
        "strategy": "aggressive_growth",
        "ytd_return": 7.8,
        "benchmark_return": 6.2,
        "alpha": 1.6,
        "risk_profile": "aggressive",
        "next_review": "Q3 review",
        "life_events": ["Planning practice sale in 2-3 years"],
        "held_away_assets": 1100000,
    },
    "WM-003": {
        "name": "George & Martha Kensington",
        "aum": 12400000,
        "strategy": "capital_preservation",
        "ytd_return": 2.1,
        "benchmark_return": 1.8,
        "alpha": 0.3,
        "risk_profile": "conservative",
        "next_review": "Q2 review",
        "life_events": ["Estate plan revision needed", "RMD optimization"],
        "held_away_assets": 1850000,
    },
    "WM-004": {
        "name": "Tidewater Ventures LLC",
        "aum": 5700000,
        "strategy": "alternative_focused",
        "ytd_return": 3.9,
        "benchmark_return": 4.1,
        "alpha": -0.2,
        "risk_profile": "moderate_aggressive",
        "next_review": "Q3 review",
        "life_events": ["Considering real estate exit strategy"],
        "held_away_assets": 900000,
    },
    "WM-005": {
        "name": "Morrison Family",
        "alias": "morrison",
        "contact": "David Morrison",
        "aum": 12000000,
        "strategy": "balanced_growth",
        "ytd_return": 4.6,
        "benchmark_return": 4.1,
        "alpha": 0.5,
        "risk_profile": "moderate",
        "next_review": "Retirement readiness review (proposed)",
        "life_events": ["5-year retirement timeline", "Concern about tech layoffs", "$800K RSUs vesting next quarter"],
        "held_away_assets": 16000000,
        "held_away_breakdown": [
            ["Company stock", 8000000, "Diversification"],
            ["Real estate", 6000000, "1031 exchange"],
            ["Cash", 2000000, "Yield enhancement"],
        ],
        "concentration": {"asset": "Company stock", "sector": "tech", "value": 8000000, "rsu_vesting_next_quarter": 800000},
        "conversation_trigger": "David mentioned 5-year retirement timeline, showed concern about tech layoffs",
    },
    "WM-006": {
        "name": "Chen Family",
        "alias": "chen",
        "aum": 6400000,
        "strategy": "balanced_growth",
        "ytd_return": 4.4,
        "benchmark_return": 4.1,
        "alpha": 0.3,
        "risk_profile": "moderate",
        "next_review": "Call this week",
        "life_events": ["Business sale closing this year"],
        "held_away_assets": 3800000,
    },
    "WM-007": {
        "name": "Thompson Family",
        "alias": "thompson",
        "aum": 9100000,
        "strategy": "capital_preservation",
        "ytd_return": 2.4,
        "benchmark_return": 1.8,
        "alpha": 0.6,
        "risk_profile": "conservative",
        "next_review": "Introduction next week",
        "life_events": ["Next generation joining the family office"],
        "held_away_assets": 5200000,
    },
}

PERFORMANCE_BENCHMARKS = {
    "balanced_growth": {"benchmark": "60/40 Balanced", "1yr": 12.5, "3yr": 8.2, "5yr": 9.1},
    "aggressive_growth": {"benchmark": "80/20 Growth", "1yr": 18.2, "3yr": 10.5, "5yr": 11.8},
    "capital_preservation": {"benchmark": "20/80 Conservative", "1yr": 5.8, "3yr": 3.9, "5yr": 4.5},
    "alternative_focused": {"benchmark": "HFRI Fund Weighted", "1yr": 8.4, "3yr": 6.1, "5yr": 7.2},
}

OPPORTUNITY_SIGNALS = [
    {"client": "WM-005", "type": "concentration_and_retirement", "description": "Single tech stock is 29% of family wealth with $800K RSUs vesting next quarter; 5-year retirement timeline", "priority": "high", "impact_usd": 48000, "readiness": "High", "action": "Personal call this week to propose a retirement readiness review"},
    {"client": "WM-001", "type": "education_funding", "description": "529 plan contribution deadline approaching; daughter's college enrollment next fall", "priority": "high", "impact_usd": 6000, "readiness": "High", "action": "Schedule meeting to review education funding plan"},
    {"client": "WM-002", "type": "liquidity_event", "description": "Practice sale in 2-3 years; begin pre-sale tax and asset protection planning", "priority": "high", "impact_usd": 22000, "readiness": "Medium", "action": "Engage tax advisor for sale structuring"},
    {"client": "WM-006", "type": "liquidity_event", "description": "Business sale closing this year; proceeds likely held away", "priority": "medium", "impact_usd": 23000, "readiness": "High", "action": "Call this week to discuss proceeds planning"},
    {"client": "WM-007", "type": "wallet_share", "description": "Next generation joining the family office; $5.2M held away", "priority": "medium", "impact_usd": 31000, "readiness": "Medium", "action": "Introduction meeting next week"},
    {"client": "WM-003", "type": "estate_planning", "description": "Estate plan last updated 2019; tax law changes require revision", "priority": "medium", "impact_usd": 12000, "readiness": "Medium", "action": "Coordinate with estate attorney for plan update"},
    {"client": "WM-003", "type": "rmd_optimization", "description": "Client age 74; review Qualified Charitable Distribution strategy", "priority": "medium", "impact_usd": 4000, "readiness": "Medium", "action": "Model QCD scenarios vs standard RMD"},
    {"client": "WM-004", "type": "reallocation", "description": "Portfolio underperforming benchmark; alternative allocation review needed", "priority": "medium", "impact_usd": 9000, "readiness": "Low", "action": "Prepare alternative manager review presentation"},
]

BOOK_SUMMARY = {
    "families": 85,
    "segment": "UHNW",
    "aum_managed": 2400000000,
    "held_away_est": 4100000000,
    "target_wallet_share_pct": 55,
    "assets_in_play": 840000000,
    "top_opportunity": "WM-005",
}

OPPORTUNITY_CATEGORIES = [
    ["Wallet share growth", 34, 4200000],
    ["Planning gaps", 28, 1800000],
    ["Life events", 12, 2100000],
]

PLANNING_GAPS = {
    "WM-005": {
        "areas": [
            ["Investment", "Strong (concentration to diversify)", "High"],
            ["Estate planning", "Outdated (8 yrs)", "High"],
            ["Tax planning", "Reactive", "High"],
        ],
        "estate_gaps": ["Will from 2016 (pre-TCJA)", "No living trust", "Beneficiaries unchecked"],
        "tax_opportunities": [
            ["Stock diversification", 240000, "over 5 years"],
            ["RSU coordination", 45000, "per year"],
            ["Charitable giving", 80000, "one time"],
        ],
        "transfer_usd": 8000000,
        "advisory_fee_pct": 0.6,
    },
}

ENGAGEMENT_PLANS = {
    "WM-005": {
        "phase_1": ["Personal call (reconnect on retirement)", "Share article (stock concentration risk)", "Propose meeting (\"Retirement readiness review\")"],
        "phase_2_topics": [["Retirement vision", "Timeline confirmation"], ["Legacy goals", "Family intentions"], ["Company outlook", "Confidence level"]],
        "key_messages": ["5 years to do this right", "Manage taxes while reducing risk", "Estate plan needs checkup"],
        "touches": ["Client dinner next month", "Intro to estate attorney partner"],
    },
}

OUTREACH_MATERIALS = {
    "WM-005": {
        "subject": "Catching Up + Retirement Readiness Thoughts",
        "body": "David, I've been thinking about your 5-year retirement horizon. With market changes and your significant company stock position, let's map out a retirement readiness review - allocation alignment, tax-smart RSU strategies, and estate plan review. No pressure, just strategic conversation. Available in the next two weeks?",
        "agenda": [["0-10 min", "Personal catch-up"], ["10-25 min", "Retirement vision"], ["25-40 min", "Current situation review"], ["40-55 min", "Opportunities presentation"], ["55-60 min", "Next steps agreement"]],
    },
}

IMMEDIATE_ACTIONS = [
    ["Send Morrison email", "today"],
    ["Chen call", "this week"],
    ["Thompson intro", "next week"],
]

SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market "
    "snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or "
    "financial advice; no outreach or transaction has occurred.\n\n"
)

DEFAULT_CLIENT = "WM-005"

_OPERATIONS = [
    "market_brief",
    "client_insights",
    "opportunity_alerts",
    "performance_attribution",
    "meeting_brief",
    "book_insights",
    "planning_gaps",
    "engagement_strategy",
    "insights_summary",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _resolve_client(query):
    """Client ID, household name or family alias; None when nothing matches."""
    q = str(query).lower().strip()
    for cid, c in CLIENT_PORTFOLIOS.items():
        if cid.lower() in q or q in c["name"].lower() or (c.get("alias") and c["alias"] in q):
            return cid
    return None


def _total_aum():
    """Calculate total AUM across the named client records."""
    return sum(c["aum"] for c in CLIENT_PORTFOLIOS.values())


def _avg_alpha():
    """Calculate average alpha across client portfolios."""
    alphas = [c["alpha"] for c in CLIENT_PORTFOLIOS.values()]
    return round(sum(alphas) / len(alphas), 2) if alphas else 0


def _client_health(client):
    """Assess client relationship health."""
    if client["alpha"] >= 1.0 and client["ytd_return"] > client["benchmark_return"]:
        return "Strong"
    elif client["alpha"] >= 0:
        return "Satisfactory"
    return "Attention Needed"


def _money(value):
    """$2.4B / $28M / $240K style amounts."""
    if value >= 1000000000:
        return f"${value / 1000000000:.1f}B"
    if value >= 1000000:
        text = f"{value / 1000000:.1f}"
        if text.endswith(".0"):
            text = text[:-2]
        return f"${text}M"
    return f"${value // 1000}K"


def _wallet_share():
    b = BOOK_SUMMARY
    return round(b["aum_managed"] * 100 / (b["aum_managed"] + b["held_away_est"]))


def _pipeline_total():
    return sum(c[2] for c in OPPORTUNITY_CATEGORIES)


def _largest_held_away():
    best = None
    for cid, c in CLIENT_PORTFOLIOS.items():
        if best is None or c["held_away_assets"] > CLIENT_PORTFOLIOS[best]["held_away_assets"]:
            best = cid
    return best


def _fee(gaps):
    return round(gaps["transfer_usd"] * gaps["advisory_fee_pct"] / 100)


def _tax_savings_5yr(gaps):
    total = 0
    for _, amount, basis in gaps["tax_opportunities"]:
        total += amount * 5 if basis == "per year" else amount
    return total


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class WealthInsightsGeneratorAgent(BasicAgent):
    """Wealth management insights generator agent."""

    def __init__(self):
        self.name = "WealthInsightsGeneratorAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Wealth Insights Generator Agent",
            "description": (
                "Always call this tool for wealth-advisor, relationship-manager, advisory-director, or "
                "portfolio-strategist requests: wealth insights for my top clients and opportunities to deepen "
                "relationships, details on the Morrison Family opportunity, planning gaps, how to approach a "
                "relationship expansion, an outreach email and meeting agenda, the complete wealth insights "
                "summary, which household has the largest held-away opportunity, high-priority planning signals, "
                "a client below benchmark, the fixed market snapshot, or a meeting brief for the Kensington "
                "household. The demo hero client is the Morrison Family (WM-005); client-level operations use it "
                "when no client is named. Do not answer those workflows from general knowledge. Uses fictional "
                "records and fixed synthetic snapshots only. Never presents current market data or personal "
                "financial, tax, legal, or estate-planning advice, sends outreach, or performs a transaction. "
                "Licensed-advisor and customer review are required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose book_insights for wealth insights for my top clients, the book, wallet share "
                            "or opportunities to deepen relationships. Choose client_insights for details on one "
                            "client's opportunity (e.g. the Morrison Family), unified managed and held-away wealth, "
                            "or the household with the largest held-away opportunity. Choose planning_gaps for what "
                            "planning gaps a client has. Choose engagement_strategy for how to approach a "
                            "relationship expansion. Choose meeting_brief for an outreach email, meeting agenda, or "
                            "the Kensington review brief (drafts only). Choose insights_summary for the complete "
                            "wealth insights summary. Choose opportunity_alerts for high-priority planning signals "
                            "ranked by impact and readiness. Choose performance_attribution for a client below "
                            "benchmark or attribution labels. Choose market_brief only for the fixed market "
                            "snapshot or morning huddle."
                        ),
                        "enum": list(_OPERATIONS),
                    },
                    "client_id": {
                        "type": "string",
                        "description": (
                            "Synthetic client mapping: Morrison Family or David Morrison is WM-005 (the default "
                            "hero client and the largest held-away opportunity); Harrison Family Trust is WM-001; "
                            "Dr. Anita Rao is WM-002; George and Martha Kensington or the Kensington household is "
                            "WM-003; Tidewater Ventures is WM-004; Chen Family is WM-006; Thompson Family is WM-007. "
                            "Omit for book-wide, market, opportunity and attribution reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "book_insights")
        dispatch = {
            "market_brief": self._market_brief,
            "client_insights": self._client_insights,
            "opportunity_alerts": self._opportunity_alerts,
            "performance_attribution": self._performance_attribution,
            "meeting_brief": self._meeting_brief,
            "book_insights": self._book_insights,
            "planning_gaps": self._planning_gaps,
            "engagement_strategy": self._engagement_strategy,
            "insights_summary": self._insights_summary,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        record_id = kwargs.get("client_id")
        client_id = None
        if record_id:
            client_id = _resolve_client(record_id)
            if client_id is None:
                return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        return SYNTHETIC_NOTICE + handler(client_id)

    def _market_brief(self, client_id) -> str:
        lines = ["# Fixed Synthetic Market Snapshot\n"]
        lines.append("## Index Performance\n")
        lines.append("| Index | Current | YTD Return | P/E | Yield |")
        lines.append("|---|---|---|---|---|")
        for idx, data in MARKET_DATA.items():
            pe = f"{data['pe_ratio']:.1f}" if data["pe_ratio"] else "N/A"
            yld = f"{data['dividend_yield']:.2f}%" if data["dividend_yield"] else "N/A"
            lines.append(f"| {idx} | {data['current']:,.2f} | {data['ytd_return']:+.1f}% | {pe} | {yld} |")
        lines.append("\n## Key Observations\n")
        lines.append("- Equity markets continue positive YTD momentum; NASDAQ leading at +6.2%")
        lines.append("- International developed markets (EAFE) outperforming on weaker dollar")
        lines.append("- Fixed income subdued with 10-Year Treasury at 4.28%")
        lines.append("- Gold rally continues (+8.1% YTD) on geopolitical uncertainty")
        lines.append(f"\n**Named-client AUM in this snapshot:** ${_total_aum():,.0f}")
        return "\n".join(lines)

    # -- book_insights: video turn 1 ----------------------------------------
    def _book_insights(self, client_id) -> str:
        b = BOOK_SUMMARY
        top = CLIENT_PORTFOLIOS[b["top_opportunity"]]
        lines = [f"# Wealth Insights: {b['families']} {b['segment']} Families\n"]
        lines.append(
            f"Analyzed {b['families']} {b['segment']} clients - {_money(b['assets_in_play'])} in held-away assets "
            f"in play across wallet share and planning gaps; {_money(_pipeline_total())}/year revenue potential.\n"
        )
        lines.append("| Metric | Value |\n|---|---|")
        lines.append(f"| Total clients | {b['families']} families |")
        lines.append(f"| AUM managed | {_money(b['aum_managed'])} |")
        lines.append(f"| Held-away (est.) | {_money(b['held_away_est'])} |")
        lines.append(f"| Wallet share | {_wallet_share()}% (target {b['target_wallet_share_pct']}%) |")
        lines.append("\n**Opportunities:**\n")
        lines.append("| Category | Clients | Revenue Potential |\n|---|---|---|")
        for name, clients, revenue in OPPORTUNITY_CATEGORIES:
            lines.append(f"| {name} | {clients} | {_money(revenue)}/year |")
        stock = top["concentration"]["value"]
        lines.append(f"\n**Top Opportunity:** {top['name']} - {_money(stock)} outside stock concentration")
        lines.append("\nSource: [Portfolio + Wealth Estimates] Agents: WealthAnalyticsAgent, OpportunityIdentificationAgent")
        lines.append(f"\n**Next step:** dive into the {top['name']}?")
        return "\n".join(lines)

    # -- client_insights: video turn 2 --------------------------------------
    def _client_insights(self, client_id) -> str:
        if client_id is None:
            return self._book_table()
        c = CLIENT_PORTFOLIOS[client_id]
        total = c["aum"] + c["held_away_assets"]
        lines = [f"# Client Deep Dive: {c['name']} ({client_id})\n"]
        lines.append("| Detail | Information |\n|---|---|")
        lines.append(f"| Total wealth | {_money(total)} |")
        lines.append(f"| With us | {_money(c['aum'])} ({round(c['aum'] * 100 / total)}%) |")
        lines.append(f"| Held away | {_money(c['held_away_assets'])} ({round(c['held_away_assets'] * 100 / total)}%) |")
        if c.get("held_away_breakdown"):
            lines.append("\n**Held-Away Assets:**\n")
            lines.append("| Asset | Value | Opportunity |\n|---|---|---|")
            for asset, value, opp in c["held_away_breakdown"]:
                lines.append(f"| {asset} | {_money(value)} | {opp} |")
        if c.get("concentration"):
            k = c["concentration"]
            lines.append(
                f"\n**Concentration Risk:** Single stock = {round(k['value'] * 100 / total)}% of wealth "
                f"({_money(k['value'])}), {k['sector']} sector, {_money(k['rsu_vesting_next_quarter'])} RSUs vesting next quarter"
            )
        if c.get("conversation_trigger"):
            lines.append(f"\n**Conversation Trigger:** {c['conversation_trigger']}")
        else:
            lines.append("\n**Life events to validate:** " + "; ".join(c["life_events"]))
        lines.append("\nSource: [CRM + Account Aggregation] Agents: ClientInsightsAgent, OpportunityIdentificationAgent")
        lines.append("\n**Next step:** see planning gaps?")
        return "\n".join(lines)

    def _book_table(self) -> str:
        largest = _largest_held_away()
        lines = ["# Client Insights Report\n"]
        lines.append(f"**Named-client AUM:** ${_total_aum():,.0f}")
        lines.append(f"**Average Alpha:** {_avg_alpha()}%")
        lines.append(f"**Largest held-away opportunity:** {CLIENT_PORTFOLIOS[largest]['name']} ({largest})\n")
        lines.append("| Client | Managed AUM | Held Away | Strategy | YTD | Alpha | Health | Next Review |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for cid, c in CLIENT_PORTFOLIOS.items():
            lines.append(
                f"| {c['name']} ({cid}) | ${c['aum']:,.0f} | ${c['held_away_assets']:,.0f} | {c['strategy'].replace('_', ' ').title()} "
                f"| {c['ytd_return']:+.1f}% | {c['alpha']:+.1f}% | {_client_health(c)} | {c['next_review']} |"
            )
        lines.append("\n## Life Events & Planning Needs\n")
        for cid, c in CLIENT_PORTFOLIOS.items():
            lines.append(f"- **{c['name']} ({cid}):** " + "; ".join(c["life_events"]))
        return "\n".join(lines)

    # -- planning_gaps: video turn 3 ----------------------------------------
    def _planning_gaps(self, client_id) -> str:
        client_id = client_id or DEFAULT_CLIENT
        c = CLIENT_PORTFOLIOS[client_id]
        gaps = PLANNING_GAPS.get(client_id)
        if not gaps:
            return (
                f"# Planning Gaps: {c['name']} ({client_id})\n\n**Not available:** no planning review is on file "
                "for this client; signals to validate: " + "; ".join(c["life_events"]) + "."
            )
        fee = _fee(gaps)
        savings = _tax_savings_5yr(gaps)
        multiple = savings // fee
        label = "10x+" if multiple >= 10 else f"{multiple}x"
        lines = [f"# Planning Gaps: {c['name']} ({client_id})\n"]
        lines.append(f"{len(gaps['areas'])} areas need attention.\n")
        lines.append("| Area | Status | Priority |\n|---|---|---|")
        for area, status, priority in gaps["areas"]:
            lines.append(f"| {area} | {status} | {priority} |")
        lines.append("\n**Estate Gaps:** " + ", ".join(gaps["estate_gaps"]))
        tax = []
        for name, amount, basis in gaps["tax_opportunities"]:
            tax.append(f"{name} {_money(amount)}{'+' if basis == 'over 5 years' else ''} ({basis})")
        lines.append("\n**Tax Opportunities:** " + "; ".join(tax))
        lines.append(
            f"\n**Service Expansion:** +{_money(fee)} annual fees on a {_money(gaps['transfer_usd'])} transfer; "
            f"about {_money(savings)} of 5-year tax opportunities, {label} the annual fee."
        )
        lines.append("\nEstimates for advisor review; validate with the client's tax and estate professionals.")
        lines.append("\nSource: [Planning System] Agents: PlanningGapAgent, ClientInsightsAgent")
        lines.append("\n**Next step:** develop the engagement strategy?")
        return "\n".join(lines)

    # -- engagement_strategy: video turn 4 ----------------------------------
    def _engagement_strategy(self, client_id) -> str:
        client_id = client_id or DEFAULT_CLIENT
        c = CLIENT_PORTFOLIOS[client_id]
        plan = ENGAGEMENT_PLANS.get(client_id)
        if not plan:
            return (
                f"# Engagement Strategy: {c['name']} ({client_id})\n\n**Not available:** no engagement plan is on "
                "file for this client; start from its opportunity alerts."
            )
        lines = [f"# Engagement Strategy: {c['name']} Relationship Expansion\n"]
        lines.append("**Phase 1: Immediate (This Week)**\n")
        for step in plan["phase_1"]:
            lines.append(f"- {step}")
        lines.append("\n**Phase 2: Discovery Meeting (2 Weeks)**\n")
        lines.append("| Topic | Focus |\n|---|---|")
        for topic, focus in plan["phase_2_topics"]:
            lines.append(f"| {topic} | {focus} |")
        lines.append("\n**Key Messages:** " + ", ".join(f"\"{m}\"" for m in plan["key_messages"]))
        lines.append("\n**Touches:** " + ", ".join(plan["touches"]))
        lines.append("\nSource: [CRM + Engagement] Agents: RelationshipStrategyAgent")
        lines.append("\n**Next step:** draft the outreach?")
        return "\n".join(lines)

    # -- meeting_brief: video turn 5 (outreach) / Kensington brief -----------
    def _meeting_brief(self, client_id) -> str:
        client_id = client_id or DEFAULT_CLIENT
        client = CLIENT_PORTFOLIOS[client_id]
        material = OUTREACH_MATERIALS.get(client_id)
        if material:
            gaps = PLANNING_GAPS[client_id]
            lines = [f"# Outreach and Meeting Materials: {client['contact']} ({client['name']})\n"]
            lines.append(f"**Email Subject:** {material['subject']}\n")
            lines.append(f"**Draft:** \"{material['body']}\"\n")
            lines.append("**Meeting Agenda (60 minutes):**\n")
            lines.append("| Time | Topic |\n|---|---|")
            for slot, topic in material["agenda"]:
                lines.append(f"| {slot} | {topic} |")
            lines.append(
                f"\n**Talking Points:** concentration risk {_money(client['concentration']['value'])}, "
                f"tax savings {_money(gaps['tax_opportunities'][0][1])}+, estate docs 8 years old"
            )
            lines.append(
                "\nDraft email ready for you to review and send from Outlook; nothing has been sent. This is "
                "preparation material, not a recommendation; validate suitability and approved disclosures."
            )
            lines.append("\nSource: [CRM + Content Library] Agents: OutreachAgent, RelationshipStrategyAgent")
            lines.append("\n**Next step:** complete wealth insights summary?")
            return "\n".join(lines)
        signals = [s for s in OPPORTUNITY_SIGNALS if s["client"] == client_id]
        lines = [f"# Draft Advisor Meeting Brief: {client['name']}\n"]
        lines.append(f"- **Managed AUM:** ${client['aum']:,.0f}")
        lines.append(f"- **Held-away assets in synthetic snapshot:** ${client['held_away_assets']:,.0f}")
        lines.append(f"- **Risk profile:** {client['risk_profile'].replace('_', ' ').title()}")
        lines.append(f"- **Next review:** {client['next_review']}")
        lines.append("\n## Validate With the Client\n")
        for event in client["life_events"]:
            lines.append(f"- {event}")
        lines.append("\n## Discussion Prompts\n")
        for signal in signals:
            lines.append(f"- {signal['description']}")
        lines.append(
            "\nThis is preparation material, not a recommendation or customer communication. "
            "The advisor must validate facts, suitability, consent, and approved disclosures."
        )
        return "\n".join(lines)

    # -- insights_summary: video turn 6 -------------------------------------
    def _insights_summary(self, client_id) -> str:
        b = BOOK_SUMMARY
        hero_id = client_id or b["top_opportunity"]
        hero = CLIENT_PORTFOLIOS[hero_id]
        lines = [f"# Wealth Insights Summary: {_money(_pipeline_total())} Revenue Opportunity\n"]
        lines.append("| Analysis | Result |\n|---|---|")
        lines.append(f"| Clients analyzed | {b['families']} {b['segment']} families |")
        lines.append(f"| Total AUM | {_money(b['aum_managed'])} |")
        lines.append(f"| Wallet share | {_wallet_share()}% -> {b['target_wallet_share_pct']}% target |")
        lines.append("\n**Pipeline:**\n")
        lines.append("| Category | Revenue |\n|---|---|")
        for name, _, revenue in OPPORTUNITY_CATEGORIES:
            lines.append(f"| {name} | {_money(revenue)}/year |")
        lines.append(f"| **Total** | **{_money(_pipeline_total())}/year** |")
        gaps = PLANNING_GAPS.get(hero_id)
        if gaps:
            lines.append(
                f"\n**{hero['name'].split(' ')[0]}:** {_money(gaps['transfer_usd'])} transfer, {_money(_fee(gaps))}/year fees, "
                f"{_money(gaps['tax_opportunities'][0][1])}+ tax savings"
            )
        lines.append("\n**Immediate Actions:** " + ", ".join(f"{a} ({when})" for a, when in IMMEDIATE_ACTIONS))
        lines.append("\nRevenue figures are synthetic estimates for advisor planning; no outreach has been sent.")
        lines.append("\nSource: [Portfolio + CRM + Planning] Agents: WealthAnalyticsAgent, RelationshipStrategyAgent")
        return "\n".join(lines)

    def _opportunity_alerts(self, client_id) -> str:
        lines = ["# Opportunity Alerts (ranked by relationship readiness, then impact)\n"]
        for level in ["high", "medium"]:
            group = []
            for readiness in ["High", "Medium", "Low"]:
                for s in OPPORTUNITY_SIGNALS:
                    if s["priority"] == level and s["readiness"] == readiness:
                        group.append(s)
            if not group:
                continue
            lines.append(f"## {level.title()} Priority\n")
            lines.append("| Client | Signal | Est. annual impact | Readiness | Recommended action |")
            lines.append("|---|---|---|---|---|")
            for s in group:
                client = CLIENT_PORTFOLIOS[s["client"]]
                lines.append(
                    f"| {client['name']} | {s['description']} | ${s['impact_usd']:,} | {s['readiness']} | {s['action']} |"
                )
            lines.append("")
        lines.append(f"**Total Alerts:** {len(OPPORTUNITY_SIGNALS)}")
        return "\n".join(lines)

    def _performance_attribution(self, client_id) -> str:
        lines = ["# Performance Attribution\n"]
        lines.append("## Strategy Benchmarks\n")
        lines.append("| Strategy | Benchmark | 1-Year | 3-Year | 5-Year |")
        lines.append("|---|---|---|---|---|")
        for strat, bench in PERFORMANCE_BENCHMARKS.items():
            lines.append(
                f"| {strat.replace('_', ' ').title()} | {bench['benchmark']} "
                f"| {bench['1yr']}% | {bench['3yr']}% | {bench['5yr']}% |"
            )
        lines.append("\n## Client Performance vs Benchmark\n")
        lines.append("| Client | Strategy | YTD | Benchmark | Alpha | Attribution |")
        lines.append("|---|---|---|---|---|---|")
        for cid, c in CLIENT_PORTFOLIOS.items():
            if c["alpha"] >= 1.0:
                attribution = "Selection + Allocation"
            elif c["alpha"] >= 0:
                attribution = "Allocation"
            else:
                attribution = "Underperformance"
            lines.append(
                f"| {c['name']} | {c['strategy'].replace('_', ' ').title()} "
                f"| {c['ytd_return']:+.1f}% | {c['benchmark_return']:+.1f}% "
                f"| {c['alpha']:+.1f}% | {attribution} |"
            )
        total_alpha_weighted = sum(c["alpha"] * c["aum"] for c in CLIENT_PORTFOLIOS.values()) / _total_aum()
        lines.append(f"\n**AUM-Weighted Alpha:** {total_alpha_weighted:+.2f}%")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = WealthInsightsGeneratorAgent()
    for op, cid in [("book_insights", None), ("client_insights", "Morrison Family"), ("planning_gaps", None),
                    ("engagement_strategy", None), ("meeting_brief", None), ("insights_summary", None)]:
        print("=" * 80)
        print(agent.perform(operation=op, client_id=cid) if cid else agent.perform(operation=op))
        print()
