"""
Pipeline Velocity Agent

Measures and analyzes pipeline velocity metrics across all stages,
identifies bottlenecks slowing deal progression, benchmarks performance
against historical data, and generates acceleration plans to improve
time-to-close across the sales pipeline.

Where a real deployment would call Salesforce, Clari, InsightSquared, etc.,
this agent uses a synthetic data layer so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ===================================================================
# RAPP AGENT MANIFEST
# ===================================================================
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/pipeline-velocity",
    "version": "1.0.0",
    "display_name": "Pipeline Velocity",
    "description": "Velocity dashboard, stage analysis, bottleneck detection, and acceleration planning for the sales pipeline.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "pipeline-velocity", "deal-progression", "analytics"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ===================================================================
# SYNTHETIC DATA LAYER
# ===================================================================

_STAGE_TIMESTAMPS = {
    "TechCorp Industries": {
        "deal_id": "OPP-001", "value": 890000, "owner": "Mike Chen",
        "stages": {"Qualification": 12, "Discovery": 16, "Proposal": 34},
        "current_stage": "Proposal", "total_age": 62, "probability": 0.35,
    },
    "Global Manufacturing": {
        "deal_id": "OPP-002", "value": 720000, "owner": "Lisa Torres",
        "stages": {"Qualification": 10, "Discovery": 15, "Proposal": 14, "Negotiation": 28},
        "current_stage": "Negotiation", "total_age": 67, "probability": 0.55,
    },
    "Apex Financial": {
        "deal_id": "OPP-003", "value": 580000, "owner": "James Park",
        "stages": {"Qualification": 11, "Discovery": 25},
        "current_stage": "Discovery", "total_age": 36, "probability": 0.20,
    },
    "Metro Healthcare": {
        "deal_id": "OPP-004", "value": 440000, "owner": "Mike Chen",
        "stages": {"Qualification": 9, "Discovery": 14, "Proposal": 22},
        "current_stage": "Proposal", "total_age": 45, "probability": 0.45,
    },
    "Pacific Telecom": {
        "deal_id": "OPP-013", "value": 780000, "owner": "Lisa Torres",
        "stages": {"Qualification": 8, "Discovery": 12, "Proposal": 11, "Negotiation": 14},
        "current_stage": "Negotiation", "total_age": 45, "probability": 0.75,
    },
    "Pinnacle Logistics": {
        "deal_id": "OPP-005", "value": 360000, "owner": "James Park",
        "stages": {"Qualification": 20},
        "current_stage": "Qualification", "total_age": 20, "probability": 0.10,
    },
    "Northstar Aerospace": {
        "deal_id": "OPP-014", "value": 650000, "owner": "Mike Chen",
        "stages": {"Qualification": 10, "Discovery": 13, "Proposal": 17},
        "current_stage": "Proposal", "total_age": 40, "probability": 0.50,
    },
    "DataFlow Corp": {
        "deal_id": "OPP-020", "value": 340000, "owner": "Lisa Torres",
        "stages": {"Qualification": 7, "Discovery": 10, "Proposal": 9, "Negotiation": 8, "Contract": 3},
        "current_stage": "Contract", "total_age": 37, "probability": 0.90,
    },
}

_CONVERSION_RATES = {
    "Qualification_to_Discovery": {"rate": 0.72, "avg_days": 12, "benchmark_days": 14},
    "Discovery_to_Proposal": {"rate": 0.58, "avg_days": 16, "benchmark_days": 18},
    "Proposal_to_Negotiation": {"rate": 0.65, "avg_days": 15, "benchmark_days": 16},
    "Negotiation_to_Contract": {"rate": 0.78, "avg_days": 11, "benchmark_days": 12},
    "Contract_to_Closed_Won": {"rate": 0.88, "avg_days": 7, "benchmark_days": 10},
}

_STAGE_BENCHMARKS = {
    "Qualification": {"target_days": 14, "median_days": 11, "p75_days": 16, "p90_days": 22},
    "Discovery": {"target_days": 18, "median_days": 14, "p75_days": 20, "p90_days": 28},
    "Proposal": {"target_days": 16, "median_days": 12, "p75_days": 18, "p90_days": 26},
    "Negotiation": {"target_days": 12, "median_days": 9, "p75_days": 14, "p90_days": 20},
    "Contract": {"target_days": 10, "median_days": 6, "p75_days": 10, "p90_days": 15},
}

_QUARTERLY_VELOCITY = {
    "Q1_2025": {"avg_cycle": 58, "pipeline_value": 8200000, "deals_closed": 14, "velocity_index": 1980000},
    "Q2_2025": {"avg_cycle": 54, "pipeline_value": 9100000, "deals_closed": 16, "velocity_index": 2700000},
    "Q3_2025": {"avg_cycle": 51, "pipeline_value": 10400000, "deals_closed": 18, "velocity_index": 3670000},
    "Q4_2025": {"avg_cycle": 48, "pipeline_value": 11200000, "deals_closed": 21, "velocity_index": 4900000},
}


# ===================================================================
# HELPERS
# ===================================================================

def _pipeline_velocity_formula(num_deals, avg_value, win_rate, avg_cycle):
    """Standard pipeline velocity = (# deals x avg value x win rate) / avg cycle days."""
    if avg_cycle == 0:
        return 0
    return round(num_deals * avg_value * win_rate / avg_cycle)


def _current_bottlenecks():
    """Identify stages where deals are exceeding benchmarks."""
    bottlenecks = {}
    for deal_name, deal in _STAGE_TIMESTAMPS.items():
        stage = deal["current_stage"]
        days = deal["stages"].get(stage, 0)
        benchmark = _STAGE_BENCHMARKS.get(stage, {})
        target = benchmark.get("target_days", 14)
        if days > target:
            if stage not in bottlenecks:
                bottlenecks[stage] = {"deals": [], "total_value": 0, "avg_excess": 0}
            excess = days - target
            bottlenecks[stage]["deals"].append({"name": deal_name, "value": deal["value"], "days": days, "excess": excess})
            bottlenecks[stage]["total_value"] += deal["value"]

    for stage, data in bottlenecks.items():
        data["avg_excess"] = round(sum(d["excess"] for d in data["deals"]) / len(data["deals"]))
    return bottlenecks


# ===================================================================
# AGENT CLASS
# ===================================================================

class PipelineVelocityAgent(BasicAgent):
    """
    Measures and optimizes pipeline velocity.

    Operations:
        velocity_dashboard   - overall velocity metrics and KPIs
        stage_analysis       - per-stage conversion and timing analysis
        bottleneck_detection - identify stages causing slowdowns
        acceleration_plan    - recommendations to improve velocity
    """

    def __init__(self):
        self.name = "PipelineVelocityAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["velocity_dashboard", "stage_analysis", "bottleneck_detection", "acceleration_plan"],
                        "description": "The analysis to perform",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "velocity_dashboard")
        dispatch = {
            "velocity_dashboard": self._velocity_dashboard,
            "stage_analysis": self._stage_analysis,
            "bottleneck_detection": self._bottleneck_detection,
            "acceleration_plan": self._acceleration_plan,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation '{op}'. Valid: {', '.join(dispatch.keys())}"
        return handler()

    # -- velocity_dashboard --------------------------------------------
    def _velocity_dashboard(self) -> str:
        deals = _STAGE_TIMESTAMPS
        num_deals = len(deals)
        total_value = sum(d["value"] for d in deals.values())
        avg_value = round(total_value / max(num_deals, 1))
        avg_cycle = round(sum(d["total_age"] for d in deals.values()) / max(num_deals, 1))
        avg_prob = round(sum(d["probability"] for d in deals.values()) / max(num_deals, 1), 2)
        velocity = _pipeline_velocity_formula(num_deals, avg_value, avg_prob, avg_cycle)

        # Stage distribution
        stage_counts = {}
        for d in deals.values():
            s = d["current_stage"]
            if s not in stage_counts:
                stage_counts[s] = {"count": 0, "value": 0}
            stage_counts[s]["count"] += 1
            stage_counts[s]["value"] += d["value"]

        stage_rows = ""
        for stage in ["Qualification", "Discovery", "Proposal", "Negotiation", "Contract"]:
            sc = stage_counts.get(stage, {"count": 0, "value": 0})
            stage_rows += f"| {stage} | {sc['count']} | ${sc['value']:,} |\n"

        # Quarterly trend
        q_rows = ""
        for q, data in _QUARTERLY_VELOCITY.items():
            q_rows += f"| {q.replace('_', ' ')} | ${data['velocity_index']:,}/day | {data['avg_cycle']}d | {data['deals_closed']} |\n"

        return (
            f"**Pipeline Velocity Dashboard**\n\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Active Deals | {num_deals} |\n"
            f"| Total Pipeline | ${total_value:,} |\n"
            f"| Avg Deal Value | ${avg_value:,} |\n"
            f"| Avg Win Rate | {avg_prob:.0%} |\n"
            f"| Avg Cycle Length | {avg_cycle} days |\n"
            f"| **Pipeline Velocity** | **${velocity:,}/day** |\n\n"
            f"**Stage Distribution:**\n\n"
            f"| Stage | Deals | Value |\n"
            f"|-------|-------|-------|\n"
            f"{stage_rows}\n"
            f"**Quarterly Velocity Trend:**\n\n"
            f"| Quarter | Velocity | Avg Cycle | Deals Closed |\n"
            f"|---------|----------|-----------|-------------|\n"
            f"{q_rows}\n"
            f"Source: [CRM Pipeline Data + Historical Analytics]\n"
            f"Agents: VelocityEngine, PipelineTracker"
        )

    # -- stage_analysis ------------------------------------------------
    def _stage_analysis(self) -> str:
        rows = ""
        for transition, data in _CONVERSION_RATES.items():
            stages = transition.replace("_to_", " -> ").replace("_", " ")
            delta = data["avg_days"] - data["benchmark_days"]
            delta_str = f"{delta:+d}d" if delta != 0 else "on target"
            rows += (f"| {stages} | {data['rate']:.0%} | {data['avg_days']}d | "
                     f"{data['benchmark_days']}d | {delta_str} |\n")

        # Per-deal current stage timing
        deal_rows = ""
        for deal_name in sorted(_STAGE_TIMESTAMPS.keys(), key=lambda d: -_STAGE_TIMESTAMPS[d]["value"]):
            deal = _STAGE_TIMESTAMPS[deal_name]
            stage = deal["current_stage"]
            days = deal["stages"].get(stage, 0)
            benchmark = _STAGE_BENCHMARKS.get(stage, {}).get("target_days", 14)
            ratio = round(days / max(benchmark, 1), 1)
            status = "ON TRACK" if ratio <= 1.0 else ("SLOW" if ratio <= 1.5 else "STALLED")
            deal_rows += f"| {deal_name} | ${deal['value']:,} | {stage} | {days}d | {benchmark}d | {ratio}x | {status} |\n"

        return (
            f"**Stage-by-Stage Analysis**\n\n"
            f"**Conversion Rates:**\n\n"
            f"| Transition | Rate | Avg Days | Benchmark | Delta |\n"
            f"|-----------|------|---------|-----------|-------|\n"
            f"{rows}\n"
            f"**Current Deal Timing:**\n\n"
            f"| Deal | Value | Stage | Days | Benchmark | Ratio | Status |\n"
            f"|------|-------|-------|------|-----------|-------|--------|\n"
            f"{deal_rows}\n"
            f"Source: [Stage Transition Data + Benchmarks]\n"
            f"Agents: StageAnalysisEngine"
        )

    # -- bottleneck_detection ------------------------------------------
    def _bottleneck_detection(self) -> str:
        bottlenecks = _current_bottlenecks()

        if not bottlenecks:
            return "**Bottleneck Detection**\n\nNo bottlenecks detected. All deals within benchmark timelines."

        sections = []
        for stage in ["Qualification", "Discovery", "Proposal", "Negotiation", "Contract"]:
            bn = bottlenecks.get(stage)
            if not bn:
                continue
            deal_lines = ""
            for d in sorted(bn["deals"], key=lambda x: -x["value"]):
                deal_lines += f"  - {d['name']}: ${d['value']:,} -- {d['days']}d (+{d['excess']}d over)\n"

            benchmark = _STAGE_BENCHMARKS[stage]
            sections.append(
                f"**{stage} Stage Bottleneck**\n"
                f"Deals affected: {len(bn['deals'])} | Value at risk: ${bn['total_value']:,}\n"
                f"Avg excess: {bn['avg_excess']} days | Benchmark: {benchmark['target_days']}d\n"
                f"P75: {benchmark['p75_days']}d | P90: {benchmark['p90_days']}d\n\n"
                f"Affected deals:\n{deal_lines}"
            )

        total_bottleneck_value = sum(bn["total_value"] for bn in bottlenecks.values())
        return (
            f"**Bottleneck Detection Report**\n\n"
            f"Bottlenecks found in **{len(bottlenecks)}** stages | "
            f"Total value impacted: **${total_bottleneck_value:,}**\n\n"
            + "\n---\n\n".join(sections)
            + f"\n\n**Root Cause Patterns:**\n"
            f"- Proposal stage: Executive access and competitive evaluation delays\n"
            f"- Negotiation stage: Legal review and procurement process bottlenecks\n"
            f"- Qualification stage: Insufficient early engagement and champion gaps\n\n"
            f"Source: [Pipeline Analytics + Stage Duration Data]\n"
            f"Agents: BottleneckDetectionEngine"
        )

    # -- acceleration_plan ---------------------------------------------
    def _acceleration_plan(self) -> str:
        bottlenecks = _current_bottlenecks()

        stage_actions = {
            "Qualification": [
                "Implement automated BANT qualification scoring",
                "Add discovery call within 48h of lead assignment",
                "Set 14-day SLA with escalation for stalled qualification",
            ],
            "Discovery": [
                "Mandate multi-threading by day 10 of Discovery",
                "Require champion identification before stage exit",
                "Offer POC or demo within first week of Discovery",
            ],
            "Proposal": [
                "Pre-stage executive sponsor meeting before proposal delivery",
                "Include competitive differentiation in every proposal",
                "Set 16-day proposal stage SLA with weekly reviews",
            ],
            "Negotiation": [
                "Send pre-approved contract templates day 1 of Negotiation",
                "Schedule legal-to-legal call within 3 business days",
                "Offer flexible payment terms to reduce procurement friction",
            ],
            "Contract": [
                "Assign deal desk support for all contracts over $200K",
                "Implement e-signature with 48-hour reminder cadence",
                "Pre-schedule onboarding kickoff to create urgency",
            ],
        }

        sections = []
        for stage in ["Qualification", "Discovery", "Proposal", "Negotiation", "Contract"]:
            bn = bottlenecks.get(stage)
            actions = stage_actions.get(stage, [])
            impact = f"${bn['total_value']:,} at risk, {bn['avg_excess']}d avg excess" if bn else "Preventive measures"
            action_lines = "\n".join(f"  {i}. {a}" for i, a in enumerate(actions, 1))
            sections.append(
                f"**{stage}** -- {impact}\n{action_lines}"
            )

        # Overall targets
        current_avg = round(sum(d["total_age"] for d in _STAGE_TIMESTAMPS.values()) / max(len(_STAGE_TIMESTAMPS), 1))
        target_avg = round(current_avg * 0.78)

        return (
            f"**Pipeline Acceleration Plan**\n\n"
            f"Current avg cycle: **{current_avg} days** | Target: **{target_avg} days** (-22%)\n\n"
            + "\n\n".join(sections)
            + f"\n\n**Implementation Timeline:**\n"
            f"- Week 1: Deploy SLA tracking and automated alerts\n"
            f"- Week 2: Train team on stage exit criteria and acceleration tactics\n"
            f"- Week 3: Launch weekly velocity reviews in pipeline meetings\n"
            f"- Week 4: First velocity improvement measurement\n\n"
            f"**Expected Outcomes:**\n"
            f"- Reduce avg cycle from {current_avg} to {target_avg} days\n"
            f"- Increase pipeline velocity by 28%\n"
            f"- Eliminate 60% of stage bottlenecks within 30 days\n\n"
            f"Source: [Best Practices + Velocity Benchmarks]\n"
            f"Agents: AccelerationPlannerAgent"
        )


if __name__ == "__main__":
    agent = PipelineVelocityAgent()
    for op in ["velocity_dashboard", "stage_analysis", "bottleneck_detection", "acceleration_plan"]:
        print("=" * 70)
        print(agent.perform(operation=op))
        print()
