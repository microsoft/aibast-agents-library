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
        "last_contact": "2025-02-20",
        "next_review": "2025-04-15",
        "life_events": ["Daughter starting college Fall 2025"],
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
        "last_contact": "2025-03-01",
        "next_review": "2025-06-01",
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
        "last_contact": "2025-01-15",
        "next_review": "2025-04-01",
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
        "last_contact": "2025-02-10",
        "next_review": "2025-05-15",
        "life_events": ["Considering real estate exit strategy"],
        "held_away_assets": 900000,
    },
}

PERFORMANCE_BENCHMARKS = {
    "balanced_growth": {"benchmark": "60/40 Balanced", "1yr": 12.5, "3yr": 8.2, "5yr": 9.1},
    "aggressive_growth": {"benchmark": "80/20 Growth", "1yr": 18.2, "3yr": 10.5, "5yr": 11.8},
    "capital_preservation": {"benchmark": "20/80 Conservative", "1yr": 5.8, "3yr": 3.9, "5yr": 4.5},
    "alternative_focused": {"benchmark": "HFRI Fund Weighted", "1yr": 8.4, "3yr": 6.1, "5yr": 7.2},
}

OPPORTUNITY_SIGNALS = [
    {"client": "WM-001", "type": "education_funding", "description": "529 plan contribution deadline approaching; daughter's college enrollment Fall 2025", "priority": "high", "action": "Schedule meeting to review education funding plan"},
    {"client": "WM-002", "type": "liquidity_event", "description": "Practice sale in 2-3 years; begin pre-sale tax and asset protection planning", "priority": "high", "action": "Engage tax advisor for sale structuring"},
    {"client": "WM-003", "type": "estate_planning", "description": "Estate plan last updated 2019; tax law changes require revision", "priority": "medium", "action": "Coordinate with estate attorney for plan update"},
    {"client": "WM-003", "type": "rmd_optimization", "description": "Client age 74; review Qualified Charitable Distribution strategy", "priority": "medium", "action": "Model QCD scenarios vs standard RMD"},
    {"client": "WM-004", "type": "reallocation", "description": "Portfolio underperforming benchmark; alternative allocation review needed", "priority": "medium", "action": "Prepare alternative manager review presentation"},
]


SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional clients, holdings, market "
    "snapshots, and planning signals only. This is not investment, tax, legal, estate-planning, or "
    "financial advice; no outreach or transaction has occurred.\n\n"
)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _total_aum():
    """Calculate total AUM across all clients."""
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
                "portfolio-strategist requests about the fixed market snapshot, which household has the "
                "largest held-away opportunity, high-priority planning signals, a client below benchmark, "
                "or a meeting brief for the Kensington household. Do not answer those workflows from "
                "general knowledge. Uses fictional records and fixed synthetic snapshots only. Never "
                "presents current market data or personal financial, tax, legal, "
                "or estate-planning advice, sends outreach, or performs a transaction. Licensed-advisor "
                "and customer review are required."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "Choose market_brief for the fixed market snapshot, morning huddle, index "
                            "context, or whether data is current. Choose client_insights for unified managed "
                            "and held-away wealth, the household with the largest held-away opportunity, life "
                            "events, or next reviews. Choose opportunity_alerts for high-priority planning "
                            "signals or advisor-review opportunities. Choose performance_attribution for a "
                            "client below benchmark, alpha, strategy benchmarks, or an attribution label. "
                            "Choose meeting_brief for the Kensington household or draft preparation material "
                            "without advice or outreach."
                        ),
                        "enum": [
                            "market_brief",
                            "client_insights",
                            "opportunity_alerts",
                            "performance_attribution",
                            "meeting_brief",
                        ],
                    },
                    "client_id": {
                        "type": "string",
                        "description": (
                            "Synthetic client mapping: Harrison Family Trust is WM-001; Dr. Anita Rao is "
                            "WM-002; George and Martha Kensington, the Kensington household, or the largest "
                            "held-away opportunity is WM-003; Tidewater Ventures is WM-004. Omit for "
                            "market, opportunity, attribution, and book-wide reports."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("client_id")
        if record_id and record_id not in CLIENT_PORTFOLIOS:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        operation = kwargs.get("operation", "market_brief")
        dispatch = {
            "market_brief": self._market_brief,
            "client_insights": self._client_insights,
            "opportunity_alerts": self._opportunity_alerts,
            "performance_attribution": self._performance_attribution,
            "meeting_brief": self._meeting_brief,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(**kwargs)

    def _market_brief(self, **kwargs) -> str:
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
        lines.append(f"\n**Total Practice AUM:** ${_total_aum():,.0f}")
        return "\n".join(lines)

    def _client_insights(self, **kwargs) -> str:
        lines = ["# Client Insights Report\n"]
        lines.append(f"**Total AUM:** ${_total_aum():,.0f}")
        lines.append(f"**Average Alpha:** {_avg_alpha()}%\n")
        lines.append("| Client | Managed AUM | Held Away | Strategy | YTD | Alpha | Health | Next Review |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for cid, c in CLIENT_PORTFOLIOS.items():
            health = _client_health(c)
            lines.append(
                f"| {c['name']} ({cid}) | ${c['aum']:,.0f} | ${c['held_away_assets']:,.0f} | {c['strategy'].replace('_', ' ').title()} "
                f"| {c['ytd_return']:+.1f}% | {c['alpha']:+.1f}% | {health} | {c['next_review']} |"
            )
        lines.append("\n## Life Events & Planning Needs\n")
        for cid, c in CLIENT_PORTFOLIOS.items():
            if c["life_events"]:
                lines.append(f"### {c['name']} ({cid})\n")
                for event in c["life_events"]:
                    lines.append(f"- {event}")
                lines.append("")
        return "\n".join(lines)

    def _opportunity_alerts(self, **kwargs) -> str:
        lines = ["# Opportunity Alerts\n"]
        high = [s for s in OPPORTUNITY_SIGNALS if s["priority"] == "high"]
        medium = [s for s in OPPORTUNITY_SIGNALS if s["priority"] == "medium"]
        if high:
            lines.append("## High Priority\n")
            for s in high:
                client = CLIENT_PORTFOLIOS.get(s["client"], {})
                lines.append(f"### {client.get('name', s['client'])} — {s['type'].replace('_', ' ').title()}\n")
                lines.append(f"- **Description:** {s['description']}")
                lines.append(f"- **Recommended Action:** {s['action']}\n")
        if medium:
            lines.append("## Medium Priority\n")
            for s in medium:
                client = CLIENT_PORTFOLIOS.get(s["client"], {})
                lines.append(f"### {client.get('name', s['client'])} — {s['type'].replace('_', ' ').title()}\n")
                lines.append(f"- **Description:** {s['description']}")
                lines.append(f"- **Recommended Action:** {s['action']}\n")
        lines.append(f"**Total Alerts:** {len(OPPORTUNITY_SIGNALS)}")
        return "\n".join(lines)

    def _performance_attribution(self, **kwargs) -> str:
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

    def _meeting_brief(self, **kwargs) -> str:
        client_id = kwargs.get("client_id", "WM-003")
        client = CLIENT_PORTFOLIOS.get(client_id, list(CLIENT_PORTFOLIOS.values())[0])
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = WealthInsightsGeneratorAgent()
    print(agent.perform(operation="market_brief"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="client_insights"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="opportunity_alerts"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="performance_attribution"))
