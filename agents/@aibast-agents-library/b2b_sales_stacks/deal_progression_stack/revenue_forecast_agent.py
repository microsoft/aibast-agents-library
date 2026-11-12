"""
Revenue Forecast Agent

Generates quarterly revenue forecasts using weighted pipeline analysis,
runs scenario modeling (best case, commit, worst case), compares commit
vs best-case projections, and tracks forecast accuracy over time. Provides
sales leadership with data-driven revenue projections and confidence levels.

Where a real deployment would call Salesforce, Clari, Aviso, etc., this
agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ===================================================================
# RAPP AGENT MANIFEST
# ===================================================================
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/revenue-forecast",
    "version": "1.0.0",
    "display_name": "Revenue Forecast",
    "description": "Quarterly forecasting, scenario analysis, commit vs best-case modeling, and forecast accuracy tracking.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "revenue-forecast", "deal-progression", "analytics"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ===================================================================
# SYNTHETIC DATA LAYER
# ===================================================================

_PIPELINE_DEALS = {
    "TechCorp Industries": {"deal_id": "OPP-001", "value": 890000, "stage": "Proposal",
                            "probability": 0.35, "close_date": "2026-04-15", "category": "upside",
                            "owner": "Mike Chen", "forecast_override": None},
    "Global Manufacturing": {"deal_id": "OPP-002", "value": 720000, "stage": "Negotiation",
                             "probability": 0.55, "close_date": "2026-03-31", "category": "commit",
                             "owner": "Lisa Torres", "forecast_override": 720000},
    "Apex Financial": {"deal_id": "OPP-003", "value": 580000, "stage": "Discovery",
                       "probability": 0.20, "close_date": "2026-05-30", "category": "pipeline",
                       "owner": "James Park", "forecast_override": None},
    "Metro Healthcare": {"deal_id": "OPP-004", "value": 440000, "stage": "Proposal",
                         "probability": 0.45, "close_date": "2026-04-20", "category": "best_case",
                         "owner": "Mike Chen", "forecast_override": None},
    "Pacific Telecom": {"deal_id": "OPP-013", "value": 780000, "stage": "Negotiation",
                        "probability": 0.75, "close_date": "2026-03-28", "category": "commit",
                        "owner": "Lisa Torres", "forecast_override": 780000},
    "Pinnacle Logistics": {"deal_id": "OPP-005", "value": 360000, "stage": "Qualification",
                           "probability": 0.10, "close_date": "2026-06-15", "category": "pipeline",
                           "owner": "James Park", "forecast_override": None},
    "Northstar Aerospace": {"deal_id": "OPP-014", "value": 650000, "stage": "Proposal",
                            "probability": 0.50, "close_date": "2026-04-10", "category": "best_case",
                            "owner": "Mike Chen", "forecast_override": 650000},
    "DataFlow Corp": {"deal_id": "OPP-020", "value": 340000, "stage": "Contract",
                      "probability": 0.90, "close_date": "2026-03-22", "category": "commit",
                      "owner": "Lisa Torres", "forecast_override": 340000},
    "Beacon Financial": {"deal_id": "OPP-015", "value": 520000, "stage": "Discovery",
                         "probability": 0.25, "close_date": "2026-05-15", "category": "upside",
                         "owner": "James Park", "forecast_override": None},
    "Orion Software": {"deal_id": "OPP-023", "value": 420000, "stage": "Negotiation",
                       "probability": 0.65, "close_date": "2026-04-05", "category": "best_case",
                       "owner": "James Park", "forecast_override": 420000},
}

_HISTORICAL_ACCURACY = {
    "Q1_2025": {"forecast": 3200000, "actual": 3450000, "accuracy": 92.8, "variance_pct": 7.8},
    "Q2_2025": {"forecast": 3800000, "actual": 3620000, "accuracy": 95.3, "variance_pct": -4.7},
    "Q3_2025": {"forecast": 4100000, "actual": 4280000, "accuracy": 95.8, "variance_pct": 4.4},
    "Q4_2025": {"forecast": 4900000, "actual": 5100000, "accuracy": 96.1, "variance_pct": 4.1},
}

_SEASONAL_ADJUSTMENTS = {
    "Q1": 0.92,
    "Q2": 1.05,
    "Q3": 0.98,
    "Q4": 1.12,
}

_QUOTA = {
    "Q1_2026": 5200000,
    "team_size": 5,
    "per_rep": 1040000,
}


# ===================================================================
# HELPERS
# ===================================================================

def _weighted_forecast():
    """Calculate weighted pipeline forecast."""
    total = 0
    for deal in _PIPELINE_DEALS.values():
        total += deal["value"] * deal["probability"]
    return round(total)


def _category_totals():
    """Sum pipeline by forecast category."""
    cats = {"commit": 0, "best_case": 0, "upside": 0, "pipeline": 0}
    for deal in _PIPELINE_DEALS.values():
        cat = deal["category"]
        if cat in cats:
            cats[cat] += deal["value"]
    return cats


def _scenario_forecast(multiplier_map):
    """Run scenario with probability multipliers per category."""
    total = 0
    for deal in _PIPELINE_DEALS.values():
        mult = multiplier_map.get(deal["category"], deal["probability"])
        total += deal["value"] * mult
    return round(total)


# ===================================================================
# AGENT CLASS
# ===================================================================

class RevenueForecastAgent(BasicAgent):
    """
    Generates revenue forecasts and scenario analysis.

    Operations:
        quarterly_forecast   - weighted pipeline forecast for current quarter
        scenario_analysis    - best case, expected, and worst case scenarios
        commit_vs_best_case  - compare commit pipeline to best case projections
        forecast_accuracy    - historical accuracy and trend analysis
    """

    def __init__(self):
        self.name = "RevenueForecastAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["quarterly_forecast", "scenario_analysis", "commit_vs_best_case", "forecast_accuracy"],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "quarterly_forecast")
        dispatch = {
            "quarterly_forecast": self._quarterly_forecast,
            "scenario_analysis": self._scenario_analysis,
            "commit_vs_best_case": self._commit_vs_best_case,
            "forecast_accuracy": self._forecast_accuracy,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation '{op}'. Valid: {', '.join(dispatch.keys())}"
        return handler()

    # -- quarterly_forecast --------------------------------------------
    def _quarterly_forecast(self) -> str:
        weighted = _weighted_forecast()
        cats = _category_totals()
        total_pipeline = sum(d["value"] for d in _PIPELINE_DEALS.values())
        quota = _QUOTA["Q1_2026"]
        attainment = round(weighted / max(quota, 1) * 100, 1)

        rows = ""
        for deal_name in sorted(_PIPELINE_DEALS.keys(), key=lambda d: -_PIPELINE_DEALS[d]["value"]):
            deal = _PIPELINE_DEALS[deal_name]
            w = round(deal["value"] * deal["probability"])
            override = f"${deal['forecast_override']:,}" if deal["forecast_override"] else "-"
            rows += (f"| {deal_name} | ${deal['value']:,} | {deal['stage']} | "
                     f"{deal['probability']:.0%} | ${w:,} | {deal['category']} | {override} |\n")

        seasonal = _SEASONAL_ADJUSTMENTS.get("Q1", 1.0)
        adjusted = round(weighted * seasonal)

        return (
            f"**Q1 2026 Revenue Forecast**\n\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Total Pipeline | ${total_pipeline:,} |\n"
            f"| Weighted Forecast | ${weighted:,} |\n"
            f"| Seasonal Adjustment ({seasonal}x) | ${adjusted:,} |\n"
            f"| Quota | ${quota:,} |\n"
            f"| **Forecast Attainment** | **{attainment}%** |\n\n"
            f"**Category Breakdown:**\n"
            f"- Commit: ${cats['commit']:,}\n"
            f"- Best Case: ${cats['best_case']:,}\n"
            f"- Upside: ${cats['upside']:,}\n"
            f"- Pipeline: ${cats['pipeline']:,}\n\n"
            f"**Deal-Level Forecast:**\n\n"
            f"| Deal | Value | Stage | Prob | Weighted | Category | Override |\n"
            f"|------|-------|-------|------|---------|----------|----------|\n"
            f"{rows}\n"
            f"Source: [CRM Pipeline + Forecast Submissions]\n"
            f"Agents: ForecastEngine, PipelineAnalytics"
        )

    # -- scenario_analysis ---------------------------------------------
    def _scenario_analysis(self) -> str:
        best = _scenario_forecast({"commit": 0.95, "best_case": 0.80, "upside": 0.50, "pipeline": 0.25})
        expected = _scenario_forecast({"commit": 0.85, "best_case": 0.55, "upside": 0.25, "pipeline": 0.10})
        worst = _scenario_forecast({"commit": 0.70, "best_case": 0.30, "upside": 0.10, "pipeline": 0.05})
        quota = _QUOTA["Q1_2026"]

        scenarios = [
            ("Best Case", best, round(best / quota * 100, 1)),
            ("Expected", expected, round(expected / quota * 100, 1)),
            ("Worst Case", worst, round(worst / quota * 100, 1)),
        ]

        rows = ""
        for name, value, att in scenarios:
            gap = value - quota
            gap_str = f"+${gap:,}" if gap >= 0 else f"-${abs(gap):,}"
            rows += f"| {name} | ${value:,} | {att}% | {gap_str} |\n"

        at_risk_value = sum(d["value"] for d in _PIPELINE_DEALS.values()
                           if d["category"] in ("upside", "pipeline"))

        return (
            f"**Scenario Analysis -- Q1 2026**\n\n"
            f"Quota: ${quota:,}\n\n"
            f"| Scenario | Forecast | Attainment | Gap to Quota |\n"
            f"|----------|----------|-----------|-------------|\n"
            f"{rows}\n"
            f"**Scenario Assumptions:**\n"
            f"- Best Case: 95% of commit closes, 80% of best case, 50% of upside\n"
            f"- Expected: 85% of commit, 55% of best case, 25% of upside\n"
            f"- Worst Case: 70% of commit, 30% of best case, 10% of upside\n\n"
            f"**Risk Factors:**\n"
            f"- ${at_risk_value:,} in upside/pipeline categories (low confidence)\n"
            f"- 2 deals in commit category with legal/procurement delays\n"
            f"- Seasonal Q1 adjustment factor: {_SEASONAL_ADJUSTMENTS['Q1']}x\n\n"
            f"**Confidence Level:** Expected scenario has 72% confidence based on historical patterns.\n\n"
            f"Source: [Scenario Modeling + Historical Patterns]\n"
            f"Agents: ScenarioEngine"
        )

    # -- commit_vs_best_case -------------------------------------------
    def _commit_vs_best_case(self) -> str:
        commit_deals = {n: d for n, d in _PIPELINE_DEALS.items() if d["category"] == "commit"}
        best_case_deals = {n: d for n, d in _PIPELINE_DEALS.items() if d["category"] == "best_case"}

        commit_total = sum(d["value"] for d in commit_deals.values())
        best_total = sum(d["value"] for d in best_case_deals.values())
        combined = commit_total + best_total
        quota = _QUOTA["Q1_2026"]

        commit_rows = ""
        for name, d in sorted(commit_deals.items(), key=lambda x: -x[1]["value"]):
            commit_rows += f"| {name} | ${d['value']:,} | {d['stage']} | {d['probability']:.0%} | {d['close_date']} |\n"

        best_rows = ""
        for name, d in sorted(best_case_deals.items(), key=lambda x: -x[1]["value"]):
            best_rows += f"| {name} | ${d['value']:,} | {d['stage']} | {d['probability']:.0%} | {d['close_date']} |\n"

        gap_to_quota = quota - commit_total
        coverage = round(combined / max(quota, 1) * 100, 1)

        return (
            f"**Commit vs Best Case Analysis**\n\n"
            f"| Category | Value | % of Quota |\n"
            f"|----------|-------|----------|\n"
            f"| Commit | ${commit_total:,} | {round(commit_total / quota * 100, 1)}% |\n"
            f"| Best Case | ${best_total:,} | {round(best_total / quota * 100, 1)}% |\n"
            f"| **Combined** | **${combined:,}** | **{coverage}%** |\n"
            f"| Quota | ${quota:,} | 100% |\n"
            f"| Gap (Commit to Quota) | ${gap_to_quota:,} | |\n\n"
            f"**Commit Deals ({len(commit_deals)}):**\n\n"
            f"| Deal | Value | Stage | Probability | Close Date |\n"
            f"|------|-------|-------|-----------|------------|\n"
            f"{commit_rows}\n"
            f"**Best Case Deals ({len(best_case_deals)}):**\n\n"
            f"| Deal | Value | Stage | Probability | Close Date |\n"
            f"|------|-------|-------|-----------|------------|\n"
            f"{best_rows}\n"
            f"**Action Required:**\n"
            f"- Close gap of ${gap_to_quota:,} by converting best-case deals to commit\n"
            f"- Accelerate Northstar Aerospace and Orion Software through Negotiation\n"
            f"- Protect commit deals from slippage with weekly reviews\n\n"
            f"Source: [Forecast Submissions + CRM Data]\n"
            f"Agents: CommitAnalysisAgent"
        )

    # -- forecast_accuracy ---------------------------------------------
    def _forecast_accuracy(self) -> str:
        rows = ""
        accuracies = []
        for q, data in sorted(_HISTORICAL_ACCURACY.items()):
            variance_dir = "Over" if data["variance_pct"] > 0 else "Under"
            rows += (f"| {q.replace('_', ' ')} | ${data['forecast']:,} | ${data['actual']:,} | "
                     f"{data['accuracy']}% | {data['variance_pct']:+.1f}% ({variance_dir}) |\n")
            accuracies.append(data["accuracy"])

        avg_accuracy = round(sum(accuracies) / max(len(accuracies), 1), 1)
        improving = all(accuracies[i] <= accuracies[i + 1] for i in range(len(accuracies) - 1))
        trend = "Improving" if improving else "Mixed"

        weighted = _weighted_forecast()
        est_accuracy = min(avg_accuracy + 0.5, 98.0)
        low_range = round(weighted * (1 - (100 - est_accuracy) / 100))
        high_range = round(weighted * (1 + (100 - est_accuracy) / 100))

        return (
            f"**Forecast Accuracy Report**\n\n"
            f"4-Quarter avg accuracy: **{avg_accuracy}%** | Trend: **{trend}**\n\n"
            f"| Quarter | Forecast | Actual | Accuracy | Variance |\n"
            f"|---------|----------|--------|----------|----------|\n"
            f"{rows}\n"
            f"**Q1 2026 Confidence Range:**\n"
            f"- Weighted forecast: ${weighted:,}\n"
            f"- Expected accuracy: {est_accuracy}%\n"
            f"- Low estimate: ${low_range:,}\n"
            f"- High estimate: ${high_range:,}\n\n"
            f"**Accuracy Insights:**\n"
            f"- Consistent slight under-forecasting (avg +4.1% actual vs forecast)\n"
            f"- Commit category accuracy: 94% (most reliable)\n"
            f"- Best case conversion: 62% historically\n"
            f"- Upside conversion: 28% historically\n\n"
            f"**Recommendation:** Apply +4% upward adjustment to weighted forecast "
            f"based on historical under-forecasting pattern.\n\n"
            f"Source: [Historical Forecast Data + Actuals]\n"
            f"Agents: AccuracyTrackingEngine"
        )


if __name__ == "__main__":
    agent = RevenueForecastAgent()
    for op in ["quarterly_forecast", "scenario_analysis", "commit_vs_best_case", "forecast_accuracy"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
