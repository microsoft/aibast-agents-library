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
    "version": "1.1.0",
    "display_name": "Portfolio Rebalancing Agent",
    "description": "Provide intelligent, automated portfolio rebalancing that streamlines manual reviews and improves wealth management outcomes.",
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


# Demo client (the default record): a pre-retiree whose $2M portfolio drifted after a market correction.
DEMO_CLIENT = "CLIENT-001"

CLIENT_PORTFOLIOS = {
    "CLIENT-001": {
        "name": "Pre-retiree client portfolio",
        "value_before": 2000000,
        "total_value": 1740000,
        "market_drop_pct": 15,
        "age": 55,
        "years_to_retirement": 10,
        "risk_tolerance": "Moderate (currently too aggressive)",
        "federal_bracket": 0.32,
        "current_pct": {"Equities": 80, "Fixed Income": 18, "Cash": 2},
        "target_pct": {"Equities": 65, "Fixed Income": 30, "Cash": 5},
        "harvest_lots": [
            {"holding": "US Growth Equity Fund", "proceeds": 128000, "loss": 21400, "substitute": "US Total Market Index Fund"},
            {"holding": "International Equity Fund", "proceeds": 101000, "loss": 13700, "substitute": "Developed Markets Index Fund"},
        ],
        "other_sell_lots": [
            {"holding": "US Large Cap Value Fund", "proceeds": 32000, "gain": 0},
        ],
        "buys": [
            {"action": "Buy investment-grade and municipal bonds", "amount": 180600, "note": "Tax-exempt munis"},
            {"action": "Buy Treasury securities", "amount": 28200, "note": "State-tax free"},
        ],
        "trading_costs": 847,
        "weeks": [
            ("Week 1: Tax-Loss Harvesting", ["Sell harvest lots (${harvest:,}) and rebalancing lot (${other:,})",
                                              "Document cost basis for tax reporting",
                                              "Buy substitute securities (wash-sale compliant)"]),
            ("Week 2: Fixed Income Build", ["Purchase municipal bonds ($125,000) - tax-exempt",
                                            "Add Treasury ladder ($28,200) - state-tax free",
                                            "Monitor for wash-sale compliance"]),
            ("Week 3: Dollar-Cost Average", ["Remaining bond purchases ($55,600)",
                                             "Rebalance within tax-advantaged accounts",
                                             "No tax impact on IRA reallocations"]),
            ("Week 4: Final Positioning", ["Cash reserve +$52,200 (to 5%)",
                                           "Portfolio monitoring activation",
                                           "Client review meeting to schedule"]),
        ],
        "projection": [("Current", 1740000), ("Year 5", 2480000), ("Year 10", 4010000), ("Year 20", 3840000)],
        "withdrawal_rate": 0.04,
        "monte_carlo": {"success_new_pct": 94, "success_old_pct": 78, "median": 4010000, "p10": 2920000, "p90": 5470000},
        "social_security": 42000,
        "risk_old": {"volatility": 18.2, "max_drawdown": 35, "recovery_years": 4.2, "sharpe": 0.68, "crash_impact": 348000, "delay_risk": "HIGH"},
        "risk_new": {"volatility": 10.4, "max_drawdown": 20, "recovery_years": 2.1, "sharpe": 0.92, "crash_impact": 199000, "delay_risk": "LOW"},
    },
}

SYNTHETIC_NOTICE = (
    "> **SYNTHETIC DEMO DATA — ADVISOR REVIEW REQUIRED.** Fictional portfolios and assumptions only. "
    "This is not investment, tax, legal, or financial advice; no trade or transaction has been placed.\n\n"
)

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
                "action": "reduce" if drift > 0 else "increase",
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


def _client_numbers(cid):
    """Every derived figure for a client portfolio, computed from the record."""
    c = CLIENT_PORTFOLIOS[cid]
    value = c["total_value"]
    cur = {k: round(value * v / 100) for k, v in c["current_pct"].items()}
    tgt = {k: round(value * v / 100) for k, v in c["target_pct"].items()}
    harvest = sum(l["proceeds"] for l in c["harvest_lots"])
    other = sum(l["proceeds"] for l in c["other_sell_lots"])
    losses = sum(l["loss"] for l in c["harvest_lots"])
    gains = sum(l["gain"] for l in c["other_sell_lots"])
    net_loss = losses - gains
    savings = round(net_loss * c["federal_bracket"])
    buys_fi = sum(b["amount"] for b in c["buys"])
    cash_add = tgt["Cash"] - cur["Cash"]
    traded = harvest + other + buys_fi
    ro, rn = c["risk_old"], c["risk_new"]
    return {
        "value": value, "cur": cur, "tgt": tgt, "harvest": harvest, "other": other,
        "sells": harvest + other, "losses": losses, "net_loss": net_loss, "savings": savings,
        "buys_fi": buys_fi, "cash_add": cash_add, "traded": traded,
        "cost_pct": round(c["trading_costs"] * 100 / traded, 2),
        "net_benefit": savings - c["trading_costs"],
        "vol_cut": round((ro["volatility"] - rn["volatility"]) * 100 / ro["volatility"]),
        "sharpe_gain": round(rn["sharpe"] - ro["sharpe"], 2),
        "recovery_faster": round((ro["recovery_years"] - rn["recovery_years"]) * 100 / ro["recovery_years"]),
        "drop_pct": round((value - c["value_before"]) * 100 / c["value_before"]),
    }


def _m(value):
    """$1.74M style label."""
    return f"${value / 1000000:.2f}M".replace("0M", "M") if value % 100000 else f"${value / 1000000:.1f}M"


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
        self.name = "PortfolioRebalancingAgent"
        self.metadata = {
            "name": self.name,
            "display_name": "Portfolio Rebalancing Agent",
            "description": (
                "Always call this tool for portfolio-manager, financial-advisor, paraplanner, tax-review, "
                "retirement-planning, or trading-supervisor requests about a client's drifted portfolio (the "
                "demo client CLIENT-001 has a $2M portfolio now $1.74M after a market correction), a "
                "rebalancing strategy with tax optimization, the implementation timeline, a 10-year "
                "retirement projection, a risk comparison, a client presentation or session summary, "
                "drift guardrails, the largest "
                "allocation gap, rebalancing candidates before trading, tax assumptions, loss candidates, "
                "retirement scenarios, or a controlled implementation checklist. Do not answer those "
                "workflows from general knowledge. Always call the tool when asked to show allocation "
                "changes to review with the client before anyone trades; the output is a synthetic review "
                "candidate, not advice. Also always call when asked to frame retirement scenarios without "
                "inventing a success probability or to prepare a controlled implementation checklist and "
                "state whether an order was sent. Uses fictional portfolios only, provides no investment "
                "or tax advice, and never places trades. A licensed professional and authorized reviewer "
                "must approve any action."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "For the client portfolio sequence: portfolio_analysis to review a client's drifted "
                            "portfolio; rebalance_recommendation for the rebalancing strategy with tax "
                            "optimization; execution_plan for the implementation timeline and execution "
                            "strategy; retirement_scenario for the 10-year retirement projection; "
                            "risk_comparison to compare the risk profiles of the old and new allocation; "
                            "client_summary to prepare the client presentation and summarize what was "
                            "accomplished. Otherwise choose portfolio_analysis for drift; rebalance_recommendation for candidate "
                            "allocation changes before anyone trades, including 'show me the allocation "
                            "changes I should review with the client'; tax_impact for tax assumptions or an "
                            "illustrative tax estimate; tax_loss_harvest for loss positions, wash-sale "
                            "controls, or tax-advice boundaries; retirement_scenario for retirement inputs "
                            "or a success-probability boundary, including requests to frame scenarios without "
                            "inventing a success probability; execution_plan for a controlled implementation "
                            "checklist or requests to state clearly whether any order was sent."
                        ),
                        "enum": [
                            "portfolio_analysis",
                            "rebalance_recommendation",
                            "tax_impact",
                            "tax_loss_harvest",
                            "retirement_scenario",
                            "execution_plan",
                            "risk_comparison",
                            "client_summary",
                        ],
                    },
                    "portfolio_id": {
                        "type": "string",
                        "description": (
                            "Synthetic portfolio mapping: the client with the $2M portfolio and that client's "
                            "rebalancing strategy, timeline, projection, risk comparison and presentation is "
                            "CLIENT-001 (the default when omitted). Use PORT-5001 (Growth Allocation Fund) for "
                            "fund-level review requests: which portfolio is outside its drift guardrails or the "
                            "largest gap, allocation changes to review with the client before anyone trades, tax "
                            "assumptions for the rebalance candidate, loss candidates and tax-advice controls, "
                            "framing retirement scenarios without inventing a success probability, and the "
                            "controlled implementation checklist. Conservative Income Portfolio or income "
                            "portfolio is PORT-5002."
                        ),
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        record_id = kwargs.get("portfolio_id")
        if record_id and record_id not in PORTFOLIOS and record_id not in CLIENT_PORTFOLIOS:
            return SYNTHETIC_NOTICE + f"**Not found:** No synthetic record `{record_id}` exists; no substitute record was used."
        operation = kwargs.get("operation", "portfolio_analysis")
        cid = record_id or DEMO_CLIENT
        client_ops = {
            "portfolio_analysis": self._client_analysis,
            "rebalance_recommendation": self._client_rebalance,
            "tax_impact": self._client_tax,
            "tax_loss_harvest": self._client_tax,
            "retirement_scenario": self._client_projection,
            "execution_plan": self._client_timeline,
            "risk_comparison": self._client_risk,
            "client_summary": self._client_summary,
        }
        if cid in CLIENT_PORTFOLIOS:
            handler = client_ops.get(operation)
            if not handler:
                return f"**Error:** Unknown operation `{operation}`."
            return SYNTHETIC_NOTICE + handler(cid)
        if operation in ("risk_comparison", "client_summary"):
            return SYNTHETIC_NOTICE + (f"**Not packaged:** {operation} has records for {DEMO_CLIENT} only; "
                                       f"`{cid}` has drift, tax and checklist records. No substitute record was used.")
        dispatch = {
            "portfolio_analysis": self._portfolio_analysis,
            "rebalance_recommendation": self._rebalance_recommendation,
            "tax_impact": self._tax_impact,
            "tax_loss_harvest": self._tax_loss_harvest,
            "retirement_scenario": self._retirement_scenario,
            "execution_plan": self._execution_plan,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return SYNTHETIC_NOTICE + handler(**kwargs)

    # ------------------------------------------------------------------
    # Client portfolio (CLIENT-001) views
    # ------------------------------------------------------------------
    def _client_analysis(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        n = _client_numbers(cid)
        rows = []
        for k in ("Equities", "Fixed Income", "Cash"):
            d = c["current_pct"][k] - c["target_pct"][k]
            flag = "RED" if abs(d) >= 5 else "AMBER"
            rows.append(f"| {k} | {c['current_pct'][k]}% | {c['target_pct'][k]}% | {flag} {d:+d}% |")
        return "\n".join([
            f"Your client's portfolio after the {c['market_drop_pct']}% market drop has significant drift and a "
            f"tax-loss harvesting opportunity worth ${n['savings']:,}.\n",
            f"# Portfolio Status (Post-Correction): {cid}\n",
            "| Metric | Current | Target | Drift |",
            "|---|---|---|---|",
            f"| Portfolio Value | {_m(n['value'])} | {_m(c['value_before'])} | {n['drop_pct']}% |",
            *rows,
            "",
            "**Client Profile:**",
            f"- Age: {c['age']}, retiring in {c['years_to_retirement']} years",
            f"- Risk tolerance: {c['risk_tolerance']}",
            f"- Tax bracket: {round(c['federal_bracket'] * 100)}% federal",
            "",
            f"**Key Issue:** Current {c['current_pct']['Equities']}% equity allocation exceeds age-appropriate risk "
            f"for a pre-retiree by {c['current_pct']['Equities'] - c['target_pct']['Equities']} percentage points.",
            "",
            "Should I show the recommended rebalancing strategy with tax optimization?",
        ])

    def _client_rebalance(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        n = _client_numbers(cid)
        ro, rn = c["risk_old"], c["risk_new"]
        t = c["target_pct"]
        rows = [f"| Sell equities (harvest losses) | ${n['harvest']:,} | -${n['losses']:,} realized |",
                f"| Sell equities (rebalancing lot at cost) | ${n['other']:,} | No gain |"]
        rows += [f"| {b['action']} | ${b['amount']:,} | {b['note']} |" for b in c["buys"]]
        rows.append(f"| Increase cash reserve | ${n['cash_add']:,} | Liquidity buffer |")
        subs = "; ".join(f"{l['holding']} -> {l['substitute']}" for l in c["harvest_lots"])
        return "\n".join([
            f"Recommended {t['Equities']}/{t['Fixed Income']}/{t['Cash']} allocation reduces volatility "
            f"{n['vol_cut']}% while harvesting ${n['savings']:,} in tax savings.\n",
            "# Rebalancing Transactions (candidates for advisor review)\n",
            "| Action | Amount | Tax Impact |",
            "|---|---|---|",
            *rows,
            "",
            f"Sells ${n['sells']:,} = fixed-income buys ${n['buys_fi']:,} + cash ${n['cash_add']:,}.",
            "",
            "**Tax-Loss Harvesting Value:**",
            f"- Realized losses: ${n['losses']:,}",
            f"- Tax savings ({round(c['federal_bracket'] * 100)}%): ${n['savings']:,}",
            f"- Wash sale compliant: substitute securities identified ({subs})",
            "",
            "**Risk Reduction:**",
            f"- Portfolio volatility: {ro['volatility']}% -> {rn['volatility']}%",
            f"- Max drawdown exposure: {ro['max_drawdown']}% -> {rn['max_drawdown']}%",
            f"- Sharpe ratio improvement: +{n['sharpe_gain']}",
            "",
            "These are candidates for the licensed advisor; no trade has been placed.",
            "",
            "Want to see the implementation timeline and execution strategy?",
        ])

    def _client_tax(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        n = _client_numbers(cid)
        lots = "\n".join(f"| {l['holding']} | ${l['proceeds']:,} | -${l['loss']:,} | {l['substitute']} |"
                         for l in c["harvest_lots"])
        return "\n".join([
            f"# Tax-Loss Harvesting and Tax Impact: {cid}\n",
            "| Lot | Proceeds | Realized Loss | Substitute (wash-sale control) |",
            "|---|---|---|---|",
            lots,
            "",
            f"- Realized losses ${n['losses']:,} x {round(c['federal_bracket'] * 100)}% federal bracket = "
            f"illustrative tax savings ${n['savings']:,}",
            f"- Rebalancing lot ${n['other']:,} sold at cost: no gain to offset",
            f"- Illustrative Tax Estimate: net capital loss ${n['net_loss']:,}; no tax due on the rebalance",
            "",
            "A qualified tax professional must validate tax lots, holding periods, account type, wash-sale "
            "exposure, and client suitability. No sale has been placed.",
        ])

    def _client_timeline(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        n = _client_numbers(cid)
        lines = [f"A 4-week implementation minimizes market impact while capturing the tax benefits before year-end.\n",
                 f"# Execution Timeline: {cid}\n"]
        for title, steps in c["weeks"]:
            lines.append(f"**{title}**")
            lines += ["- " + st.format(harvest=n["harvest"], other=n["other"]) for st in steps]
            lines.append("")
        lines.append(f"**Trading Costs:** ${c['trading_costs']:,} estimated ({n['cost_pct']}% of ${n['traded']:,} traded)")
        lines.append(f"**Net Benefit:** ${n['net_benefit']:,} after costs (${n['savings']:,} tax savings - ${c['trading_costs']:,})")
        lines.append("\nNo order has been created, routed, or executed; each week's trades need licensed-advisor "
                     "and authorized-trading approval.")
        lines.append("\nShould I show the 10-year retirement projection?")
        return "\n".join(lines)

    def _client_projection(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        mc = c["monte_carlo"]
        t = c["target_pct"]
        rows = []
        for label, value in c["projection"]:
            w = f"${round(value * c['withdrawal_rate']):,} ({round(c['withdrawal_rate'] * 100)}%)" if label in ("Year 10", "Year 20") else ""
            rows.append(f"| {label} | {_m(value)} | {w} |")
        y10 = dict(c["projection"])["Year 10"]
        income = round(y10 * c["withdrawal_rate"])
        return "\n".join([
            f"The new allocation projects {_m(y10)} at retirement with a {mc['success_new_pct']}% simulated "
            f"probability of meeting income goals.\n",
            f"# 10-Year Projection ({t['Equities']}/{t['Fixed Income']}/{t['Cash']} Allocation): {cid}\n",
            "| Year | Portfolio Value | Annual Withdrawal |",
            "|---|---|---|",
            *rows,
            "",
            "**Monte Carlo Analysis (synthetic illustration):**",
            f"- Success probability: {mc['success_new_pct']}% (vs {mc['success_old_pct']}% with old allocation)",
            f"- Median outcome: {_m(mc['median'])}",
            f"- 10th percentile (worst case): {_m(mc['p10'])}",
            f"- 90th percentile (best case): {_m(mc['p90'])}",
            "",
            "**Retirement Income Security:**",
            f"- Annual sustainable withdrawal: ${income:,}",
            f"- Social Security supplement: +${c['social_security']:,}",
            f"- Total retirement income: ${income + c['social_security']:,}/year",
            "",
            "The simulation figures are packaged synthetic illustrations, not a forecast: contribution, "
            "inflation, tax, fee, longevity and capital-market assumptions require advisor and client validation.",
            "",
            "Want to see the risk comparison against the old allocation?",
        ])

    def _client_risk(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        n = _client_numbers(cid)
        ro, rn = c["risk_old"], c["risk_new"]
        co, cn = c["current_pct"], c["target_pct"]
        old = f"Old ({co['Equities']}/{co['Fixed Income']}/{co['Cash']})"
        new = f"New ({cn['Equities']}/{cn['Fixed Income']}/{cn['Cash']})"
        return "\n".join([
            f"The new allocation reduces volatility, and with it sequence-of-returns risk, by {n['vol_cut']}%: "
            f"critical for a pre-retiree.\n",
            f"# Risk Comparison Analysis: {cid}\n",
            f"| Risk Metric | {old} | {new} |",
            "|---|---|---|",
            f"| Annual volatility | {ro['volatility']}% | {rn['volatility']}% |",
            f"| Max drawdown | -{ro['max_drawdown']}% | -{rn['max_drawdown']}% |",
            f"| Recovery time | {ro['recovery_years']} years | {rn['recovery_years']} years |",
            f"| Sharpe ratio | {ro['sharpe']} | {rn['sharpe']} |",
            "",
            "**Sequence Risk Protection:**",
            f"- 2008-style crash impact: -${ro['crash_impact'] // 1000}K -> -${rn['crash_impact'] // 1000}K",
            f"- Recovery to breakeven: {ro['recovery_years']} yrs -> {rn['recovery_years']} yrs ({n['recovery_faster']}% faster)",
            f"- Retirement delay risk: {ro['delay_risk']} -> {rn['delay_risk']}",
            "",
            f"**Why This Matters at Age {c['age']}:** less time to recover from major losses; approaching the "
            "withdrawal phase; income stability over growth optimization.",
            "",
            "Shall I prepare the client presentation with recommendations?",
        ])

    def _client_summary(self, cid):
        c = CLIENT_PORTFOLIOS[cid]
        n = _client_numbers(cid)
        mc = c["monte_carlo"]
        y10 = dict(c["projection"])["Year 10"]
        t = c["target_pct"]
        return "\n".join([
            f"# Session Summary: {cid}\n",
            f"- Portfolio analyzed: {_m(n['value'])} post-correction, {c['current_pct']['Equities']}% equity (too aggressive)",
            f"- Rebalancing designed: {t['Equities']}/{t['Fixed Income']}/{t['Cash']} target allocation, ${n['sells']:,} in sells",
            f"- Tax optimization: ${n['savings']:,} in tax-loss harvesting savings identified",
            "- Implementation planned: 4-week execution minimizing market impact",
            f"- Projection modeled: {_m(y10)} at retirement ({mc['success_new_pct']}% simulated success)",
            f"- Risk reduced: {n['vol_cut']}% lower volatility, {n['recovery_faster']}% faster recovery time",
            "",
            "**Value Delivered:**\n",
            "| Benefit | Amount |",
            "|---|---|",
            f"| Tax savings | ${n['savings']:,} |",
            f"| Risk reduction | {n['vol_cut']}% |",
            f"| Success probability | +{mc['success_new_pct'] - mc['success_old_pct']} pts |",
            f"| Projected retirement value | {_m(y10)} |",
            "",
            "**Client presentation outline (draft for you to build in PowerPoint):** 1) where the portfolio stands "
            "after the correction; 2) the recommended allocation and trades; 3) tax-loss harvesting value; "
            "4) 10-year projection; 5) risk comparison; 6) next steps and approvals.",
            "",
            "Nothing has been saved, shared or scheduled: save the presentation and book the client review "
            "meeting (for example tomorrow at 2 PM) yourself. No order has been created.",
        ])

    # ------------------------------------------------------------------
    # Fund portfolio (PORT-5001 / PORT-5002) views
    # ------------------------------------------------------------------
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
        lines = [f"# Rebalancing Candidates for Advisor Review: {port['name']}\n"]
        lines.append(f"**Portfolio Value:** ${port['total_value']:,.0f}")
        lines.append(f"**Drift Threshold:** {port['drift_threshold']}%\n")
        if not trades:
            lines.append("No rebalancing trades required — all holdings within drift threshold.")
            return "\n".join(lines)
        lines.append("## Candidate Allocation Changes\n")
        lines.append("| Asset | Ticker | Action | Current % | Target % | Drift | Trade Amount |")
        lines.append("|---|---|---|---|---|---|---|")
        total_sell = 0
        total_buy = 0
        for t in trades:
            sign = "+" if t["drift"] > 0 else ""
            lines.append(
                f"| {t['asset']} | {t['ticker']} | {t['action'].title()} candidate "
                f"| {t['current_pct']}% | {t['target_pct']}% | {sign}{t['drift']}% | ${t['trade_value']:,.0f} |"
            )
            if t["action"] == "reduce":
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
        sell_trades = [t for t in trades if t["action"] == "reduce"]
        lines = [f"# Tax Impact Analysis: {port['name']}\n"]
        lines.append("## Tax Rate Reference\n")
        for rate_name, rate in TAX_RATES.items():
            lines.append(f"- {rate_name.replace('_', ' ').title()}: {rate * 100:.1f}%")
        lines.append("\n## Estimated Tax on Reduction Candidates\n")
        if not sell_trades:
            lines.append("No reduction candidates require tax review.")
            return "\n".join(lines)
        lines.append("| Asset | Ticker | Reduction Amount | Cost Basis | Unrealized Gain | Est. Tax |")
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
        lines.append(f"\n**Illustrative Tax Estimate:** ${total_tax:,.0f}")
        lines.append("\n## Questions for a Qualified Tax Professional\n")
        lines.append("- Direct new contributions to underweight asset classes")
        lines.append("- Use tax-loss positions to offset gains")
        lines.append("- Rebalance within tax-advantaged accounts first")
        lines.append("- Consider charitable donation of appreciated shares")
        return "\n".join(lines)

    def _tax_loss_harvest(self, **kwargs) -> str:
        portfolio_id = kwargs.get("portfolio_id", "PORT-5001")
        port = PORTFOLIOS.get(portfolio_id, list(PORTFOLIOS.values())[0])
        losses = []
        for asset, holding in port["holdings"].items():
            unrealized = holding["value"] - holding["cost_basis"]
            if unrealized < 0:
                losses.append((asset, holding["ticker"], unrealized))
        lines = [f"# Tax-Loss-Harvesting Candidates: {port['name']}\n"]
        lines.append("| Asset | Ticker | Illustrative Unrealized Loss | Review Status |")
        lines.append("|---|---|---|---|")
        for asset, ticker, loss in losses:
            lines.append(
                f"| {asset} | {ticker} | ${abs(loss):,.0f} | Candidate only — tax-lot and wash-sale review required |"
            )
        lines.append(
            "\nA qualified tax professional must validate tax lots, holding periods, account type, "
            "wash-sale exposure, and client suitability. No sale has been recommended or placed."
        )
        return "\n".join(lines)

    def _retirement_scenario(self, **kwargs) -> str:
        portfolio_id = kwargs.get("portfolio_id", "PORT-5001")
        port = PORTFOLIOS.get(portfolio_id, list(PORTFOLIOS.values())[0])
        lines = [f"# Retirement Planning Scenario Inputs: {port['name']}\n"]
        lines.append(f"- **Starting portfolio:** ${port['total_value']:,.0f}")
        lines.append("- **Illustrative horizon:** 25 years")
        lines.append("- **Illustrative annual withdrawal:** 4.0% of starting value")
        lines.append("- **Scenarios to model:** lower-return, base, and higher-volatility")
        lines.append(
            "\nNo success probability is asserted because contribution, withdrawal, inflation, tax, "
            "fee, longevity, and capital-market assumptions require advisor and client validation."
        )
        return "\n".join(lines)

    def _execution_plan(self, **kwargs) -> str:
        portfolio_id = kwargs.get("portfolio_id", "PORT-5001")
        port = PORTFOLIOS.get(portfolio_id, list(PORTFOLIOS.values())[0])
        trades = _calculate_drift(port)
        lines = [f"# Human-Controlled Implementation Checklist: {port['name']}\n"]
        lines.append(f"**Rebalance Frequency:** {port['rebalance_frequency'].title()}")
        lines.append(f"**Total Trades:** {len(trades)}\n")
        if not trades:
            lines.append("No trades required at this time.")
            return "\n".join(lines)
        sell_trades = [t for t in trades if t["action"] == "reduce"]
        buy_trades = [t for t in trades if t["action"] == "increase"]
        lines.append("## Step 1: Review Reduction Candidates\n")
        if sell_trades:
            for i, t in enumerate(sell_trades, 1):
                lines.append(f"{i}. Review a ${t['trade_value']:,.0f} reduction candidate for {t['ticker']} ({t['asset']})")
        else:
            lines.append("No sells required.")
        lines.append("\n## Step 2: Validate Cash and Settlement Assumptions\n")
        lines.append("- Confirm available cash and settlement timing in the approved trading system\n")
        lines.append("## Step 3: Review Increase Candidates\n")
        if buy_trades:
            for i, t in enumerate(buy_trades, 1):
                lines.append(f"{i}. Review a ${t['trade_value']:,.0f} increase candidate for {t['ticker']} ({t['asset']})")
        else:
            lines.append("No buys required.")
        lines.append("\n## Step 4: Verification\n")
        lines.append("- Confirm post-trade allocations match targets")
        lines.append("- Update portfolio records")
        lines.append("- Generate client notification")
        lines.append("- Document compliance review")
        lines.append("- Obtain licensed-advisor and authorized-trading approval before any order")
        lines.append("\nNo order has been created, routed, or executed.")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = PortfolioRebalancingAgent()
    for op in ["portfolio_analysis", "rebalance_recommendation", "execution_plan",
               "retirement_scenario", "risk_comparison", "client_summary"]:
        print(agent.perform(operation=op))
        print("\n" + "=" * 80 + "\n")
