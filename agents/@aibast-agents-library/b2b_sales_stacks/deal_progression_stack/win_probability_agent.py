"""
Win Probability Agent

Calculates win probabilities for active deals using multi-factor scoring,
analyzes contributing factors with weighted importance, tracks probability
trends over time, and provides deal-to-deal comparisons to surface
patterns and actionable insights for improving close rates.

Where a real deployment would call Salesforce, Gong, Clari, etc., this
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
    "name": "@aibast-agents-library/win-probability",
    "version": "1.0.0",
    "display_name": "Win Probability",
    "description": "Calculates win probabilities, analyzes contributing factors, tracks trends, and compares deals.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "win-probability", "deal-progression", "forecasting"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ===================================================================
# SYNTHETIC DATA LAYER
# ===================================================================

_DEAL_ATTRIBUTES = {
    "TechCorp Industries": {
        "deal_id": "OPP-001", "value": 890000, "stage": "Proposal", "owner": "Mike Chen",
        "factors": {
            "stage_progression": {"value": 0.55, "weight": 0.20, "detail": "3 of 5 stages completed"},
            "champion_strength": {"value": 0.20, "weight": 0.18, "detail": "Champion silent 18 days"},
            "stakeholder_coverage": {"value": 0.40, "weight": 0.12, "detail": "2 of 5 stakeholders engaged"},
            "activity_momentum": {"value": 0.25, "weight": 0.12, "detail": "Activity declined 75% in last 14 days"},
            "competitive_position": {"value": 0.40, "weight": 0.10, "detail": "2 competitors in evaluation"},
            "deal_velocity": {"value": 0.30, "weight": 0.10, "detail": "2.1x benchmark in current stage"},
            "budget_confidence": {"value": 0.65, "weight": 0.08, "detail": "Budget approved in Q3 planning"},
            "executive_access": {"value": 0.15, "weight": 0.10, "detail": "No exec meeting in 45 days"},
        },
    },
    "Global Manufacturing": {
        "deal_id": "OPP-002", "value": 720000, "stage": "Negotiation", "owner": "Lisa Torres",
        "factors": {
            "stage_progression": {"value": 0.80, "weight": 0.20, "detail": "4 of 5 stages completed"},
            "champion_strength": {"value": 0.70, "weight": 0.18, "detail": "Champion active but frustrated"},
            "stakeholder_coverage": {"value": 0.60, "weight": 0.12, "detail": "3 of 4 stakeholders engaged"},
            "activity_momentum": {"value": 0.55, "weight": 0.12, "detail": "Consistent engagement, slight decline"},
            "competitive_position": {"value": 0.70, "weight": 0.10, "detail": "Leading, competitor offering discount"},
            "deal_velocity": {"value": 0.35, "weight": 0.10, "detail": "2.3x benchmark in Negotiation"},
            "budget_confidence": {"value": 0.75, "weight": 0.08, "detail": "Budget confirmed, procurement slow"},
            "executive_access": {"value": 0.45, "weight": 0.10, "detail": "Exec engaged but 20 days since contact"},
        },
    },
    "Apex Financial": {
        "deal_id": "OPP-003", "value": 580000, "stage": "Discovery", "owner": "James Park",
        "factors": {
            "stage_progression": {"value": 0.30, "weight": 0.20, "detail": "2 of 5 stages completed"},
            "champion_strength": {"value": 0.15, "weight": 0.18, "detail": "CTO disengaged, no response"},
            "stakeholder_coverage": {"value": 0.20, "weight": 0.12, "detail": "1 of 6 stakeholders engaged"},
            "activity_momentum": {"value": 0.15, "weight": 0.12, "detail": "Activity declined 80% in last 14 days"},
            "competitive_position": {"value": 0.25, "weight": 0.10, "detail": "3 competitors, RFP coming"},
            "deal_velocity": {"value": 0.45, "weight": 0.10, "detail": "1.4x benchmark in Discovery"},
            "budget_confidence": {"value": 0.30, "weight": 0.08, "detail": "Budget not yet allocated"},
            "executive_access": {"value": 0.10, "weight": 0.10, "detail": "No executive contact established"},
        },
    },
    "Metro Healthcare": {
        "deal_id": "OPP-004", "value": 440000, "stage": "Proposal", "owner": "Mike Chen",
        "factors": {
            "stage_progression": {"value": 0.55, "weight": 0.20, "detail": "3 of 5 stages completed"},
            "champion_strength": {"value": 0.85, "weight": 0.18, "detail": "VP Digital actively championing"},
            "stakeholder_coverage": {"value": 0.65, "weight": 0.12, "detail": "3 of 4 stakeholders engaged"},
            "activity_momentum": {"value": 0.60, "weight": 0.12, "detail": "Steady engagement maintained"},
            "competitive_position": {"value": 0.80, "weight": 0.10, "detail": "Competitor struggling with compliance"},
            "deal_velocity": {"value": 0.50, "weight": 0.10, "detail": "1.4x benchmark, moderate delay"},
            "budget_confidence": {"value": 0.40, "weight": 0.08, "detail": "Budget on hold, board approval needed"},
            "executive_access": {"value": 0.70, "weight": 0.10, "detail": "CMO engaged as executive sponsor"},
        },
    },
    "Pacific Telecom": {
        "deal_id": "OPP-013", "value": 780000, "stage": "Negotiation", "owner": "Lisa Torres",
        "factors": {
            "stage_progression": {"value": 0.80, "weight": 0.20, "detail": "4 of 5 stages completed"},
            "champion_strength": {"value": 0.95, "weight": 0.18, "detail": "SVP Ops strong advocate, weekly calls"},
            "stakeholder_coverage": {"value": 0.85, "weight": 0.12, "detail": "4 of 5 stakeholders engaged"},
            "activity_momentum": {"value": 0.90, "weight": 0.12, "detail": "High and increasing activity"},
            "competitive_position": {"value": 0.90, "weight": 0.10, "detail": "Competitor eliminated in eval"},
            "deal_velocity": {"value": 0.75, "weight": 0.10, "detail": "1.2x benchmark, near target"},
            "budget_confidence": {"value": 0.90, "weight": 0.08, "detail": "Budget approved, PO in queue"},
            "executive_access": {"value": 0.85, "weight": 0.10, "detail": "CTO and SVP both engaged"},
        },
    },
    "Pinnacle Logistics": {
        "deal_id": "OPP-005", "value": 360000, "stage": "Qualification", "owner": "James Park",
        "factors": {
            "stage_progression": {"value": 0.15, "weight": 0.20, "detail": "1 of 5 stages, early"},
            "champion_strength": {"value": 0.10, "weight": 0.18, "detail": "No champion identified"},
            "stakeholder_coverage": {"value": 0.15, "weight": 0.12, "detail": "1 contact, single-threaded"},
            "activity_momentum": {"value": 0.20, "weight": 0.12, "detail": "Minimal activity, declining"},
            "competitive_position": {"value": 0.50, "weight": 0.10, "detail": "No known competitors yet"},
            "deal_velocity": {"value": 0.40, "weight": 0.10, "detail": "1.4x benchmark in Qualification"},
            "budget_confidence": {"value": 0.20, "weight": 0.08, "detail": "No budget discussion held"},
            "executive_access": {"value": 0.05, "weight": 0.10, "detail": "No executive contact at all"},
        },
    },
}

_HISTORICAL_WIN_FACTORS = {
    "champion_strength": {"avg_won": 0.82, "avg_lost": 0.28, "discriminative_power": 0.92},
    "executive_access": {"avg_won": 0.76, "avg_lost": 0.22, "discriminative_power": 0.88},
    "stakeholder_coverage": {"avg_won": 0.74, "avg_lost": 0.31, "discriminative_power": 0.82},
    "activity_momentum": {"avg_won": 0.78, "avg_lost": 0.35, "discriminative_power": 0.78},
    "stage_progression": {"avg_won": 0.85, "avg_lost": 0.42, "discriminative_power": 0.75},
    "competitive_position": {"avg_won": 0.72, "avg_lost": 0.38, "discriminative_power": 0.70},
    "deal_velocity": {"avg_won": 0.70, "avg_lost": 0.40, "discriminative_power": 0.65},
    "budget_confidence": {"avg_won": 0.80, "avg_lost": 0.45, "discriminative_power": 0.62},
}

_SCORING_WEIGHTS = {
    "stage_progression": 0.20,
    "champion_strength": 0.18,
    "stakeholder_coverage": 0.12,
    "activity_momentum": 0.12,
    "competitive_position": 0.10,
    "deal_velocity": 0.10,
    "budget_confidence": 0.08,
    "executive_access": 0.10,
}

_PROBABILITY_HISTORY = {
    "TechCorp Industries": [0.52, 0.48, 0.42, 0.38, 0.35, 0.32],
    "Global Manufacturing": [0.40, 0.45, 0.50, 0.52, 0.55, 0.56],
    "Apex Financial": [0.35, 0.30, 0.25, 0.22, 0.20, 0.18],
    "Metro Healthcare": [0.38, 0.42, 0.45, 0.48, 0.50, 0.52],
    "Pacific Telecom": [0.50, 0.58, 0.65, 0.72, 0.78, 0.82],
    "Pinnacle Logistics": [0.20, 0.18, 0.15, 0.14, 0.12, 0.11],
}


# ===================================================================
# HELPERS
# ===================================================================

def _calculate_win_prob(deal_name):
    """Calculate weighted win probability."""
    deal = _DEAL_ATTRIBUTES.get(deal_name, {})
    factors = deal.get("factors", {})
    probability = 0
    for fname, fdata in factors.items():
        probability += fdata["value"] * fdata["weight"]
    return round(probability * 100, 1)


def _top_factors(deal_name, top_n=3):
    """Return top contributing factors (positive) for a deal."""
    deal = _DEAL_ATTRIBUTES.get(deal_name, {})
    factors = deal.get("factors", {})
    contributions = []
    for fname, fdata in factors.items():
        contribution = fdata["value"] * fdata["weight"]
        contributions.append({"name": fname, "value": fdata["value"], "weight": fdata["weight"],
                              "contribution": contribution, "detail": fdata["detail"]})
    return sorted(contributions, key=lambda x: -x["contribution"])[:top_n]


def _bottom_factors(deal_name, top_n=3):
    """Return weakest factors dragging down probability."""
    deal = _DEAL_ATTRIBUTES.get(deal_name, {})
    factors = deal.get("factors", {})
    weaknesses = []
    for fname, fdata in factors.items():
        gap = (1.0 - fdata["value"]) * fdata["weight"]
        weaknesses.append({"name": fname, "value": fdata["value"], "weight": fdata["weight"],
                           "gap": gap, "detail": fdata["detail"]})
    return sorted(weaknesses, key=lambda x: -x["gap"])[:top_n]


def _prob_trend(deal_name):
    """Analyze probability trend."""
    history = _PROBABILITY_HISTORY.get(deal_name, [])
    if len(history) < 2:
        return "stable", 0
    delta = history[-1] - history[-2]
    overall = history[-1] - history[0]
    if overall > 0.05:
        return "improving", round(overall * 100, 1)
    if overall < -0.05:
        return "declining", round(overall * 100, 1)
    return "stable", round(overall * 100, 1)


# ===================================================================
# AGENT CLASS
# ===================================================================

class WinProbabilityAgent(BasicAgent):
    """
    Calculates and analyzes win probabilities for pipeline deals.

    Operations:
        calculate_probability - compute win probability per deal
        factor_analysis       - weighted factor contributions
        probability_trend     - 6-period probability trend
        deal_comparison       - side-by-side deal comparison
    """

    def __init__(self):
        self.name = "WinProbabilityAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["calculate_probability", "factor_analysis", "probability_trend", "deal_comparison"],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "calculate_probability")
        dispatch = {
            "calculate_probability": self._calculate_probability,
            "factor_analysis": self._factor_analysis,
            "probability_trend": self._probability_trend,
            "deal_comparison": self._deal_comparison,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation '{op}'. Valid: {', '.join(dispatch.keys())}"
        return handler()

    # -- calculate_probability -----------------------------------------
    def _calculate_probability(self) -> str:
        rows = ""
        probs = []
        total_value = 0
        weighted_value = 0

        for deal_name in sorted(_DEAL_ATTRIBUTES.keys(), key=lambda d: -_DEAL_ATTRIBUTES[d]["value"]):
            deal = _DEAL_ATTRIBUTES[deal_name]
            prob = _calculate_win_prob(deal_name)
            probs.append(prob)
            total_value += deal["value"]
            weighted_value += deal["value"] * prob / 100
            direction, _ = _prob_trend(deal_name)
            trend_str = {"improving": "UP", "declining": "DOWN", "stable": "FLAT"}.get(direction, "FLAT")

            top = _top_factors(deal_name, 1)
            bottom = _bottom_factors(deal_name, 1)
            top_str = top[0]["name"].replace("_", " ").title() if top else "-"
            bottom_str = bottom[0]["name"].replace("_", " ").title() if bottom else "-"

            rows += (f"| {deal_name} | ${deal['value']:,} | {deal['stage']} | "
                     f"**{prob}%** | {trend_str} | {top_str} | {bottom_str} |\n")

        avg_prob = round(sum(probs) / max(len(probs), 1), 1)

        return (
            f"**Win Probability Scorecard**\n\n"
            f"Portfolio avg: **{avg_prob}%** | Total pipeline: ${total_value:,} | "
            f"Weighted value: ${weighted_value:,.0f}\n\n"
            f"| Deal | Value | Stage | Win Prob | Trend | Top Factor | Biggest Gap |\n"
            f"|------|-------|-------|---------|-------|-----------|------------|\n"
            f"{rows}\n"
            f"**Scoring Model:** 8 factors weighted by predictive power from historical win/loss data.\n\n"
            f"Source: [CRM + Activity Data + Win/Loss Database]\n"
            f"Agents: ProbabilityScoringEngine"
        )

    # -- factor_analysis -----------------------------------------------
    def _factor_analysis(self) -> str:
        sections = []
        for deal_name in sorted(_DEAL_ATTRIBUTES.keys(), key=lambda d: -_DEAL_ATTRIBUTES[d]["value"]):
            deal = _DEAL_ATTRIBUTES[deal_name]
            prob = _calculate_win_prob(deal_name)

            factor_rows = ""
            for fname, fdata in sorted(deal["factors"].items(), key=lambda x: -x[1]["value"] * x[1]["weight"]):
                contribution = round(fdata["value"] * fdata["weight"] * 100, 1)
                max_possible = round(fdata["weight"] * 100, 1)
                label = fname.replace("_", " ").title()
                factor_rows += (f"| {label} | {fdata['value']:.0%} | {fdata['weight']:.0%} | "
                                f"{contribution}% | {max_possible}% | {fdata['detail']} |\n")

            sections.append(
                f"**{deal_name} -- ${deal['value']:,} (Win Prob: {prob}%)**\n\n"
                f"| Factor | Score | Weight | Contribution | Max Possible | Detail |\n"
                f"|--------|-------|--------|-------------|-------------|--------|\n"
                f"{factor_rows}"
            )

        hist_rows = ""
        for fname in sorted(_HISTORICAL_WIN_FACTORS.keys(),
                            key=lambda f: -_HISTORICAL_WIN_FACTORS[f]["discriminative_power"]):
            hf = _HISTORICAL_WIN_FACTORS[fname]
            label = fname.replace("_", " ").title()
            hist_rows += (f"| {label} | {hf['avg_won']:.0%} | {hf['avg_lost']:.0%} | "
                          f"{hf['discriminative_power']:.0%} |\n")

        return (
            f"**Factor Analysis -- Win Probability Drivers**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\n**Historical Factor Importance:**\n\n"
            f"| Factor | Avg (Won) | Avg (Lost) | Discriminative Power |\n"
            f"|--------|----------|----------|--------------------|\n"
            f"{hist_rows}\n"
            f"Source: [Win/Loss Analysis + Factor Model]\n"
            f"Agents: FactorAnalysisEngine"
        )

    # -- probability_trend ---------------------------------------------
    def _probability_trend(self) -> str:
        sections = []
        for deal_name in sorted(_DEAL_ATTRIBUTES.keys(), key=lambda d: -_DEAL_ATTRIBUTES[d]["value"]):
            history = _PROBABILITY_HISTORY.get(deal_name, [])
            if not history:
                continue
            direction, delta = _prob_trend(deal_name)
            status = {"improving": "IMPROVING", "declining": "DECLINING", "stable": "STABLE"}.get(direction, "STABLE")

            period_labels = ["W-5", "W-4", "W-3", "W-2", "W-1", "Current"]
            trend_line = " | ".join(f"{period_labels[i]}: {h:.0%}" for i, h in enumerate(history))
            peak = max(history)
            trough = min(history)

            sections.append(
                f"**{deal_name} -- ${_DEAL_ATTRIBUTES[deal_name]['value']:,}**\n"
                f"Status: {status} | Current: {history[-1]:.0%} | 6-week delta: {delta:+.1f}%\n"
                f"Trend: {trend_line}\n"
                f"Range: {trough:.0%} - {peak:.0%}\n"
            )

        improving = sum(1 for d in _PROBABILITY_HISTORY if _prob_trend(d)[0] == "improving")
        declining = sum(1 for d in _PROBABILITY_HISTORY if _prob_trend(d)[0] == "declining")

        return (
            f"**Win Probability Trends -- 6-Week Analysis**\n\n"
            f"Improving: {improving} | Declining: {declining} | "
            f"Stable: {len(_PROBABILITY_HISTORY) - improving - declining}\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\n**Insight:** Deals with 3+ consecutive weeks of decline require immediate "
            f"intervention to reverse trajectory.\n\n"
            f"Source: [Historical Probability Scores]\n"
            f"Agents: TrendAnalysisEngine"
        )

    # -- deal_comparison -----------------------------------------------
    def _deal_comparison(self) -> str:
        deals_sorted = sorted(_DEAL_ATTRIBUTES.keys(), key=lambda d: -_calculate_win_prob(d))

        factor_names = list(_SCORING_WEIGHTS.keys())
        header = "| Factor | " + " | ".join(d.split()[0] for d in deals_sorted) + " |\n"
        separator = "|--------|" + "|".join("------" for _ in deals_sorted) + "|\n"

        rows = ""
        for fname in factor_names:
            label = fname.replace("_", " ").title()
            values = []
            for deal_name in deals_sorted:
                val = _DEAL_ATTRIBUTES[deal_name]["factors"].get(fname, {}).get("value", 0)
                values.append(f"{val:.0%}")
            rows += f"| {label} | " + " | ".join(values) + " |\n"

        prob_values = [f"**{_calculate_win_prob(d)}%**" for d in deals_sorted]
        rows += f"| **Win Probability** | " + " | ".join(prob_values) + " |\n"

        best = deals_sorted[0]
        worst = deals_sorted[-1]
        best_prob = _calculate_win_prob(best)
        worst_prob = _calculate_win_prob(worst)

        return (
            f"**Deal Comparison Matrix**\n\n"
            f"Best: **{best}** ({best_prob}%) | Needs attention: **{worst}** ({worst_prob}%)\n\n"
            f"{header}{separator}{rows}\n"
            f"**Comparison Insights:**\n"
            f"- {best} leads on champion strength and stakeholder coverage\n"
            f"- {worst} critically low on champion, executive access, and momentum\n"
            f"- Deals above 50% win probability share strong champion + executive access\n"
            f"- Activity momentum is the leading indicator of probability direction\n\n"
            f"**Pattern:** Deals that win have avg champion score of 82% vs 28% for losses. "
            f"Champion strength is the single strongest predictor.\n\n"
            f"Source: [Comparative Analytics + Win/Loss Patterns]\n"
            f"Agents: ComparisonEngine"
        )


if __name__ == "__main__":
    agent = WinProbabilityAgent()
    for op in ["calculate_probability", "factor_analysis", "probability_trend", "deal_comparison"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
