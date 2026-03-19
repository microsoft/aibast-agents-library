"""
Portfolio Rebalancing Agent — Financial Services Stack

Analyzes portfolio drift, generates rebalancing recommendations,
assesses tax impact, and creates execution plans.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/portfolio-rebalancing",
    "version": "1.0.0",
    "display_name": "Portfolio Rebalancing Agent",
    "description": "Portfolio rebalancing with drift analysis, trade recommendations, tax impact assessment, and execution planning.",
    "author": "AIBAST",
    "tags": ["portfolio", "rebalancing", "allocation", "tax", "trading", "financial-services"],
    "category": "financial_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

PORTFOLIOS = {
    "PORT-5001": {
        "name": "Growth Allocation Fund",
        "manager": "Victoria Reeves, CFA",
        "strategy": "growth",
        "total_value": 12450000,
        "benchmark": "60/40 Growth Blend",
        "rebalance_frequency": "quarterly",
        "drift_threshold": 3.0,
        "holdings": {
            "US Large Cap": {"ticker": "VTI", "value": 4357500, "current_pct": 35.0, "target_pct": 30.0, "cost_basis": 3800000},
            "US Small Cap": {"ticker": "VB", "value": 872500, "current_pct": 7.0, "target_pct": 10.0, "cost_basis": 750000},
            "Intl Developed": {"ticker": "VEA", "value": 1493750, "current_pct": 12.0, "target_pct": 15.0, "cost_basis": 1600000},
            "Emerging Markets": {"ticker": "VWO", "value": 622500, "current_pct": 5.0, "target_pct": 5.0, "cost_basis": 680000},
            "US Aggregate Bond": {"ticker": "BND", "value": 3112500, "current_pct": 25.0, "target_pct": 25.0, "cost_basis": 3200000},
            "TIPS": {"ticker": "VTIP", "value": 622500, "current_pct": 5.0, "target_pct": 5.0, "cost_basis": 600000},
            "REITs": {"ticker": "VNQ", "value": 622500, "current_pct": 5.0, "target_pct": 5.0, "cost_basis": 550000},
            "Cash": {"ticker": "VMFXX", "value": 746250, "current_pct": 6.0, "target_pct": 5.0, "cost_basis": 746250},
        },
    },
    "PORT-5002": {
        "name": "Conservative Income Portfolio",
        "manager": "Daniel Kim, CFP",
        "strategy": "income",
        "total_value": 8200000,
        "benchmark": "30/70 Income Blend",
        "rebalance_frequency": "semi-annual",
        "drift_threshold": 2.0,
        "holdings": {
            "US Large Cap Dividend": {"ticker": "VYM", "value": 1312000, "current_pct": 16.0, "target_pct": 15.0, "cost_basis": 1100000},
            "Intl Dividend": {"ticker": "VYMI", "value": 656000, "current_pct": 8.0, "target_pct": 10.0, "cost_basis": 700000},
            "US Investment Grade": {"ticker": "VCIT", "value": 2132000, "current_pct": 26.0, "target_pct": 25.0, "cost_basis": 2250000},
            "US Treasury": {"ticker": "VGIT", "value": 1640000, "current_pct": 20.0, "target_pct": 20.0, "cost_basis": 1700000},
            "Municipal Bonds": {"ticker": "VTEB", "value": 1148000, "current_pct": 14.0, "target_pct": 15.0, "cost_basis": 1200000},
            "High Yield": {"ticker": "VWEHX", "value": 492000, "current_pct": 6.0, "target_pct": 5.0, "cost_basis": 460000},
            "Preferred Stock": {"ticker": "PFF", "value": 410000, "current_pct": 5.0, "target_pct": 5.0, "cost_basis": 420000},
            "Cash": {"ticker": "VMFXX", "value": 410000, "current_pct": 5.0, "target_pct": 5.0, "cost_basis": 410000},
        },
    },
}

TAX_RATES = {
    "short_term_capital_gains": 0.37,
    "long_term_capital_gains": 0.20,
    "qualified_dividends": 0.20,
    "ordinary_income": 0.37,
    "net_investment_income_tax": 0.038,
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _calculate_drift(portfolio):
    """Calculate drift for each holding and identify rebalance needs."""
    trades = []
    for asset, data in portfolio["holdings"].items():
        drift = round(data["current_pct"] - data["target_pct"], 2)
        if abs(drift) >= portfolio["drift_threshold"]:
            target_value = portfolio["total_value"] * data["target_pct"] / 100
            trade_value = round(target_value - data["value"], 2)
            trades.append({
                "asset": asset,
                "ticker": data["ticker"],
                "current_pct": data["current_pct"],
                "target_pct": data["target_pct"],
                "drift": drift,
                "action": "sell" if drift > 0 else "buy",
                "trade_value": abs(trade_value),
            })
    return trades


def _estimate_tax(holding, sell_amount):
    """Estimate tax liability on a sale."""
    cost_basis = holding["cost_basis"]
    current_value = holding["value"]
    if current_value == 0:
        return 0
    gain_pct = (current_value - cost_basis) / current_value
    gain = sell_amount * gain_pct
    if gain <= 0:
        return 0
    tax_rate = TAX_RATES["long_term_capital_gains"] + TAX_RATES["net_investment_income_tax"]
    return round(gain * tax_rate, 2)


def _max_drift(portfolio):
    """Find maximum absolute drift in portfolio."""
    drifts = [abs(d["current_pct"] - d["target_pct"]) for d in portfolio["holdings"].values()]
    return max(drifts) if drifts else 0


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class PortfolioRebalancingAgent(BasicAgent):
    """Portfolio rebalancing agent."""

    def __init__(self):
        self.name = "@aibast-agents-library/portfolio-rebalancing"
        self.metadata = {
            "name": self.name,
            "display_name": "Portfolio Rebalancing Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "portfolio_analysis",
                            "rebalance_recommendation",
                            "tax_impact",
                            "execution_plan",
                        ],
                    },
                    "portfolio_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "portfolio_analysis")
        dispatch = {
            "portfolio_analysis": self._portfolio_analysis,
            "rebalance_recommendation": self._rebalance_recommendation,
            "tax_impact": self._tax_impact,
            "execution_plan": self._execution_plan,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    def _portfolio_analysis(self, **kwargs) -> str:
        lines = ["# Portfolio Analysis\n"]
        for pid, port in PORTFOLIOS.items():
            max_d = _max_drift(port)
            needs_rebalance = "Yes" if max_d >= port["drift_threshold"] else "No"
            lines.append(f"## {pid}: {port['name']}\n")
            lines.append(f"- **Manager:** {port['manager']}")
            lines.append(f"- **Strategy:** {port['strategy'].title()}")
            lines.append(f"- **Total Value:** ${port['total_value']:,.0f}")
            lines.append(f"- **Benchmark:** {port['benchmark']}")
            lines.append(f"- **Max Drift:** {max_d:.1f}%")
            lines.append(f"- **Drift Threshold:** {port['drift_threshold']}%")
            lines.append(f"- **Rebalance Needed:** {needs_rebalance}\n")
            lines.append("| Asset | Ticker | Value | Current % | Target % | Drift |")
            lines.append("|---|---|---|---|---|---|")
            for asset, data in port["holdings"].items():
                drift = round(data["current_pct"] - data["target_pct"], 1)
                sign = "+" if drift > 0 else ""
                lines.append(
                    f"| {asset} | {data['ticker']} | ${data['value']:,.0f} "
                    f"| {data['current_pct']}% | {data['target_pct']}% | {sign}{drift}% |"
                )
            lines.append("")
        return "\n".join(lines)

    def _rebalance_recommendation(self, **kwargs) -> str:
        portfolio_id = kwargs.get("portfolio_id", "PORT-5001")
        port = PORTFOLIOS.get(portfolio_id, list(PORTFOLIOS.values())[0])
        trades = _calculate_drift(port)
        lines = [f"# Rebalance Recommendation: {port['name']}\n"]
        lines.append(f"**Portfolio Value:** ${port['total_value']:,.0f}")
        lines.append(f"**Drift Threshold:** {port['drift_threshold']}%\n")
        if not trades:
            lines.append("No rebalancing trades required — all holdings within drift threshold.")
            return "\n".join(lines)
        lines.append("## Recommended Trades\n")
        lines.append("| Asset | Ticker | Action | Current % | Target % | Drift | Trade Amount |")
        lines.append("|---|---|---|---|---|---|---|")
        total_sell = 0
        total_buy = 0
        for t in trades:
            sign = "+" if t["drift"] > 0 else ""
            lines.append(
                f"| {t['asset']} | {t['ticker']} | {t['action'].upper()} "
                f"| {t['current_pct']}% | {t['target_pct']}% | {sign}{t['drift']}% | ${t['trade_value']:,.0f} |"
            )
            if t["action"] == "sell":
                total_sell += t["trade_value"]
            else:
                total_buy += t["trade_value"]
        lines.append(f"\n**Total Sells:** ${total_sell:,.0f}")
        lines.append(f"**Total Buys:** ${total_buy:,.0f}")
        return "\n".join(lines)

    def _tax_impact(self, **kwargs) -> str:
        portfolio_id = kwargs.get("portfolio_id", "PORT-5001")
        port = PORTFOLIOS.get(portfolio_id, list(PORTFOLIOS.values())[0])
        trades = _calculate_drift(port)
        sell_trades = [t for t in trades if t["action"] == "sell"]
        lines = [f"# Tax Impact Analysis: {port['name']}\n"]
        lines.append("## Tax Rate Reference\n")
        for rate_name, rate in TAX_RATES.items():
            lines.append(f"- {rate_name.replace('_', ' ').title()}: {rate * 100:.1f}%")
        lines.append("\n## Estimated Tax on Sell Trades\n")
        if not sell_trades:
            lines.append("No sell trades required.")
            return "\n".join(lines)
        lines.append("| Asset | Ticker | Sell Amount | Cost Basis | Unrealized Gain | Est. Tax |")
        lines.append("|---|---|---|---|---|---|")
        total_tax = 0
        for t in sell_trades:
            holding = port["holdings"][t["asset"]]
            gain_pct = (holding["value"] - holding["cost_basis"]) / holding["value"] if holding["value"] else 0
            unrealized = round(t["trade_value"] * gain_pct, 2)
            tax = _estimate_tax(holding, t["trade_value"])
            total_tax += tax
            lines.append(
                f"| {t['asset']} | {t['ticker']} | ${t['trade_value']:,.0f} "
                f"| ${holding['cost_basis']:,.0f} | ${unrealized:,.0f} | ${tax:,.0f} |"
            )
        lines.append(f"\n**Total Estimated Tax Liability:** ${total_tax:,.0f}")
        lines.append("\n## Tax-Efficient Alternatives\n")
        lines.append("- Direct new contributions to underweight asset classes")
        lines.append("- Use tax-loss positions to offset gains")
        lines.append("- Rebalance within tax-advantaged accounts first")
        lines.append("- Consider charitable donation of appreciated shares")
        return "\n".join(lines)

    def _execution_plan(self, **kwargs) -> str:
        portfolio_id = kwargs.get("portfolio_id", "PORT-5001")
        port = PORTFOLIOS.get(portfolio_id, list(PORTFOLIOS.values())[0])
        trades = _calculate_drift(port)
        lines = [f"# Execution Plan: {port['name']}\n"]
        lines.append(f"**Rebalance Frequency:** {port['rebalance_frequency'].title()}")
        lines.append(f"**Total Trades:** {len(trades)}\n")
        if not trades:
            lines.append("No trades required at this time.")
            return "\n".join(lines)
        sell_trades = [t for t in trades if t["action"] == "sell"]
        buy_trades = [t for t in trades if t["action"] == "buy"]
        lines.append("## Step 1: Execute Sells\n")
        if sell_trades:
            for i, t in enumerate(sell_trades, 1):
                lines.append(f"{i}. SELL ${t['trade_value']:,.0f} of {t['ticker']} ({t['asset']})")
        else:
            lines.append("No sells required.")
        lines.append("\n## Step 2: Settle Cash (T+1)\n")
        lines.append("- Allow sell proceeds to settle before purchasing\n")
        lines.append("## Step 3: Execute Buys\n")
        if buy_trades:
            for i, t in enumerate(buy_trades, 1):
                lines.append(f"{i}. BUY ${t['trade_value']:,.0f} of {t['ticker']} ({t['asset']})")
        else:
            lines.append("No buys required.")
        lines.append("\n## Step 4: Verification\n")
        lines.append("- Confirm post-trade allocations match targets")
        lines.append("- Update portfolio records")
        lines.append("- Generate client notification")
        lines.append("- Document compliance review")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = PortfolioRebalancingAgent()
    print(agent.perform(operation="portfolio_analysis"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="rebalance_recommendation", portfolio_id="PORT-5001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="tax_impact", portfolio_id="PORT-5001"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="execution_plan", portfolio_id="PORT-5001"))
