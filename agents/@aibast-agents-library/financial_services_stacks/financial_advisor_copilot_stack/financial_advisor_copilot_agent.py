"""
Financial Advisor Copilot Agent — Financial Services Stack

Assists financial advisors with client reviews, portfolio summaries,
investment recommendations, and compliance checks.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/financial-advisor-copilot",
    "version": "1.0.0",
    "display_name": "Financial Advisor Copilot Agent",
    "description": "Financial advisor support with client reviews, portfolio summaries, recommendation engine, and compliance checks.",
    "author": "AIBAST",
    "tags": ["advisor", "portfolio", "investment", "compliance", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CLIENT_PORTFOLIOS = {
    "CLI-3001": {
        "name": "Robert & Susan Whitfield",
        "advisor": "James Morrison, CFP",
        "risk_profile": "moderate",
        "age": 58,
        "retirement_target": 67,
        "total_assets": 1850000,
        "holdings": {
            "US Equities": {"value": 555000, "allocation": 30.0, "target": 35.0},
            "International Equities": {"value": 185000, "allocation": 10.0, "target": 15.0},
            "Fixed Income": {"value": 647500, "allocation": 35.0, "target": 30.0},
            "Real Estate (REITs)": {"value": 185000, "allocation": 10.0, "target": 10.0},
            "Alternatives": {"value": 92500, "allocation": 5.0, "target": 5.0},
            "Cash & Equivalents": {"value": 185000, "allocation": 10.0, "target": 5.0},
        },
        "annual_income": 285000,
        "annual_contributions": 45000,
        "last_review": "2024-12-15",
    },
    "CLI-3002": {
        "name": "Angela Martinez",
        "advisor": "James Morrison, CFP",
        "risk_profile": "aggressive",
        "age": 34,
        "retirement_target": 60,
        "total_assets": 420000,
        "holdings": {
            "US Equities": {"value": 210000, "allocation": 50.0, "target": 45.0},
            "International Equities": {"value": 84000, "allocation": 20.0, "target": 20.0},
            "Fixed Income": {"value": 42000, "allocation": 10.0, "target": 10.0},
            "Emerging Markets": {"value": 50400, "allocation": 12.0, "target": 15.0},
            "Alternatives": {"value": 21000, "allocation": 5.0, "target": 5.0},
            "Cash & Equivalents": {"value": 12600, "allocation": 3.0, "target": 5.0},
        },
        "annual_income": 145000,
        "annual_contributions": 24000,
        "last_review": "2025-01-20",
    },
    "CLI-3003": {
        "name": "William Chen Trust",
        "advisor": "Patricia Lane, CFA",
        "risk_profile": "conservative",
        "age": 72,
        "retirement_target": 0,
        "total_assets": 4200000,
        "holdings": {
            "US Equities": {"value": 630000, "allocation": 15.0, "target": 15.0},
            "International Equities": {"value": 210000, "allocation": 5.0, "target": 5.0},
            "Fixed Income": {"value": 1890000, "allocation": 45.0, "target": 45.0},
            "Municipal Bonds": {"value": 840000, "allocation": 20.0, "target": 20.0},
            "Real Estate (REITs)": {"value": 210000, "allocation": 5.0, "target": 5.0},
            "Cash & Equivalents": {"value": 420000, "allocation": 10.0, "target": 10.0},
        },
        "annual_income": 0,
        "annual_contributions": 0,
        "last_review": "2025-02-10",
    },
}

INVESTMENT_RECOMMENDATIONS = {
    "moderate": [
        {"action": "Rebalance to target allocation", "rationale": "Drift from target exceeds 3% in multiple asset classes"},
        {"action": "Reduce cash overweight", "rationale": "Excess cash drag on returns; deploy to equities"},
        {"action": "Increase international exposure", "rationale": "Underweight vs target; diversification benefit"},
    ],
    "aggressive": [
        {"action": "Increase emerging markets allocation", "rationale": "Below target; favorable long-term growth outlook"},
        {"action": "Consider small-cap tilt", "rationale": "Long time horizon supports higher-volatility allocations"},
        {"action": "Build cash reserve to target 5%", "rationale": "Slightly underweight cash for opportunistic rebalancing"},
    ],
    "conservative": [
        {"action": "Maintain current allocation", "rationale": "Portfolio aligned with targets; no rebalancing needed"},
        {"action": "Review bond duration", "rationale": "Consider shortening duration if rate hikes expected"},
        {"action": "Tax-loss harvesting review", "rationale": "Identify unrealized losses for year-end tax planning"},
    ],
}

COMPLIANCE_RULES = {
    "reg_bi": {"name": "Regulation Best Interest", "description": "Ensure recommendations are in client's best interest", "applies_to": "all"},
    "form_crs": {"name": "Form CRS Delivery", "description": "Relationship summary delivered at account opening and annually", "applies_to": "all"},
    "suitability": {"name": "Suitability Obligation", "description": "Investment recommendations suitable for client profile", "applies_to": "all"},
    "concentration_limit": {"name": "Concentration Limit", "description": "No single position exceeds 10% of portfolio", "applies_to": "all"},
    "senior_investor": {"name": "Senior Investor Protection", "description": "Enhanced protections for clients age 65+", "applies_to": "seniors"},
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _allocation_drift(holdings):
    """Calculate max allocation drift from target."""
    max_drift = 0
    for asset, data in holdings.items():
        drift = abs(data["allocation"] - data["target"])
        if drift > max_drift:
            max_drift = drift
    return round(max_drift, 1)


def _years_to_retirement(client):
    """Calculate years remaining to retirement."""
    if client["retirement_target"] == 0:
        return 0
    return max(0, client["retirement_target"] - client["age"])


def _compliance_flags(client):
    """Check for compliance issues."""
    flags = []
    for asset, data in client["holdings"].items():
        if data["allocation"] > 50:
            flags.append(f"Concentration risk: {asset} at {data['allocation']}%")
    if client["age"] >= 65:
        flags.append("Senior investor protections apply")
    drift = _allocation_drift(client["holdings"])
    if drift > 5:
        flags.append(f"Allocation drift of {drift}% exceeds threshold")
    return flags


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class FinancialAdvisorCopilotAgent(BasicAgent):
    """Financial advisor copilot agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/financial-advisor-copilot"
        self.metadata = {
            "name": self.name,
            "display_name": "Financial Advisor Copilot Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "client_review",
                            "portfolio_summary",
                            "recommendation_engine",
                            "compliance_check",
                        ],
                    },
                    "client_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "client_review")
        dispatch = {
            "client_review": self._client_review,
            "portfolio_summary": self._portfolio_summary,
            "recommendation_engine": self._recommendation_engine,
            "compliance_check": self._compliance_check,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _client_review(self, **kwargs) -> str:
        lines = ["# Client Review Summary\n"]
        lines.append("| Client | Advisor | Risk | Assets | Age | Retirement In | Last Review |")
        lines.append("|---|---|---|---|---|---|---|")
        for cid, c in CLIENT_PORTFOLIOS.items():
            yrs = _years_to_retirement(c)
            ret_str = f"{yrs} yrs" if yrs > 0 else "Retired"
            lines.append(
                f"| {c['name']} ({cid}) | {c['advisor']} | {c['risk_profile'].title()} "
                f"| ${c['total_assets']:,.0f} | {c['age']} | {ret_str} | {c['last_review']} |"
            )
        total_aum = sum(c["total_assets"] for c in CLIENT_PORTFOLIOS.values())
        lines.append(f"\n**Total AUM:** ${total_aum:,.0f}")
        lines.append(f"**Clients:** {len(CLIENT_PORTFOLIOS)}")
        return "\n".join(lines)

    def _portfolio_summary(self, **kwargs) -> str:
        client_id = kwargs.get("client_id", "CLI-3001")
        client = CLIENT_PORTFOLIOS.get(client_id, list(CLIENT_PORTFOLIOS.values())[0])
        drift = _allocation_drift(client["holdings"])
        lines = [f"# Portfolio Summary: {client['name']}\n"]
        lines.append(f"- **Risk Profile:** {client['risk_profile'].title()}")
        lines.append(f"- **Total Assets:** ${client['total_assets']:,.0f}")
        lines.append(f"- **Annual Contributions:** ${client['annual_contributions']:,.0f}")
        lines.append(f"- **Max Allocation Drift:** {drift}%\n")
        lines.append("## Holdings\n")
        lines.append("| Asset Class | Value | Current % | Target % | Drift |")
        lines.append("|---|---|---|---|---|")
        for asset, data in client["holdings"].items():
            d = round(data["allocation"] - data["target"], 1)
            sign = "+" if d > 0 else ""
            lines.append(
                f"| {asset} | ${data['value']:,.0f} | {data['allocation']}% "
                f"| {data['target']}% | {sign}{d}% |"
            )
        return "\n".join(lines)

    def _recommendation_engine(self, **kwargs) -> str:
        client_id = kwargs.get("client_id", "CLI-3001")
        client = CLIENT_PORTFOLIOS.get(client_id, list(CLIENT_PORTFOLIOS.values())[0])
        recs = INVESTMENT_RECOMMENDATIONS.get(client["risk_profile"], [])
        lines = [f"# Investment Recommendations: {client['name']}\n"]
        lines.append(f"**Risk Profile:** {client['risk_profile'].title()}")
        lines.append(f"**Years to Retirement:** {_years_to_retirement(client) or 'Retired'}\n")
        lines.append("## Recommendations\n")
        for i, rec in enumerate(recs, 1):
            lines.append(f"### {i}. {rec['action']}\n")
            lines.append(f"**Rationale:** {rec['rationale']}\n")
        lines.append("## Rebalancing Trades\n")
        lines.append("| Asset Class | Current | Target | Action | Est. Amount |")
        lines.append("|---|---|---|---|---|")
        for asset, data in client["holdings"].items():
            diff_pct = data["target"] - data["allocation"]
            if abs(diff_pct) >= 1.0:
                amount = abs(diff_pct / 100 * client["total_assets"])
                action = "Buy" if diff_pct > 0 else "Sell"
                lines.append(f"| {asset} | {data['allocation']}% | {data['target']}% | {action} | ${amount:,.0f} |")
        return "\n".join(lines)

    def _compliance_check(self, **kwargs) -> str:
        lines = ["# Compliance Check Report\n"]
        lines.append("## Regulatory Requirements\n")
        lines.append("| Rule | Description | Applies To |")
        lines.append("|---|---|---|")
        for rule_id, rule in COMPLIANCE_RULES.items():
            lines.append(f"| {rule['name']} | {rule['description']} | {rule['applies_to'].title()} |")
        lines.append("\n## Client Compliance Status\n")
        for cid, c in CLIENT_PORTFOLIOS.items():
            flags = _compliance_flags(c)
            status = "Issues Found" if flags else "Compliant"
            lines.append(f"### {c['name']} ({cid}) — {status}\n")
            if flags:
                for f in flags:
                    lines.append(f"- **Flag:** {f}")
            else:
                lines.append("- No compliance issues detected")
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = FinancialAdvisorCopilotAgent()
    print(agent.perform(operation="client_review"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="portfolio_summary", client_id="CLI-3001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="recommendation_engine", client_id="CLI-3002"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="compliance_check"))
