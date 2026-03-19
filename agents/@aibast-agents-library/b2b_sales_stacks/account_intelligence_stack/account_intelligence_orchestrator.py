"""
Account Intelligence Orchestrator

Coordinates multi-agent pipelines for enterprise account intelligence.
Manages stage sequencing, agent dispatch, timing estimates, and pipeline
status reporting across the account intelligence stack.

Where a real deployment would invoke sub-agents via an orchestration bus,
this agent uses a synthetic data layer so it runs anywhere without
credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/account-intelligence-orchestrator",
    "version": "1.0.0",
    "display_name": "Account Intelligence Orchestrator",
    "description": "Coordinates multi-agent pipelines for 360-degree account intelligence briefings.",
    "author": "AIBAST",
    "tags": ["b2b", "sales", "orchestration", "pipeline", "account-intelligence"],
    "category": "b2b_sales",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER
# ═══════════════════════════════════════════════════════════════

_PIPELINES = {
    "full_briefing": {
        "id": "pipe-001",
        "name": "Full Account Briefing",
        "stages": [
            {
                "stage": 1, "name": "Data Collection",
                "agents": ["AccountProfileAgent", "AccountHealthScoreAgent"],
                "avg_duration_sec": 4.2, "parallel": True,
            },
            {
                "stage": 2, "name": "Stakeholder Analysis",
                "agents": ["StakeholderMappingAgent", "EngagementTrackerAgent"],
                "avg_duration_sec": 6.8, "parallel": True,
            },
            {
                "stage": 3, "name": "Market Intelligence",
                "agents": ["CompetitiveIntelligenceAgent", "NewsMonitorAgent"],
                "avg_duration_sec": 5.1, "parallel": True,
            },
            {
                "stage": 4, "name": "Risk & Messaging",
                "agents": ["DealRiskAssessmentAgent", "ValueMessagingAgent"],
                "avg_duration_sec": 3.9, "parallel": True,
            },
            {
                "stage": 5, "name": "Briefing Assembly",
                "agents": ["BriefingDocumentAgent"],
                "avg_duration_sec": 2.3, "parallel": False,
            },
        ],
    },
    "quick_snapshot": {
        "id": "pipe-002",
        "name": "Quick Account Snapshot",
        "stages": [
            {
                "stage": 1, "name": "Core Data",
                "agents": ["AccountProfileAgent"],
                "avg_duration_sec": 3.1, "parallel": False,
            },
            {
                "stage": 2, "name": "Health Check",
                "agents": ["AccountHealthScoreAgent"],
                "avg_duration_sec": 2.4, "parallel": False,
            },
        ],
    },
    "competitive_deep_dive": {
        "id": "pipe-003",
        "name": "Competitive Deep Dive",
        "stages": [
            {
                "stage": 1, "name": "Competitor Scan",
                "agents": ["CompetitiveIntelligenceAgent", "NewsMonitorAgent"],
                "avg_duration_sec": 5.5, "parallel": True,
            },
            {
                "stage": 2, "name": "Win/Loss Analysis",
                "agents": ["WinLossAnalyzerAgent"],
                "avg_duration_sec": 4.7, "parallel": False,
            },
            {
                "stage": 3, "name": "Battlecard Generation",
                "agents": ["BattlecardGeneratorAgent"],
                "avg_duration_sec": 3.2, "parallel": False,
            },
        ],
    },
}

_ORCHESTRATION_RUNS = {
    "run-2001": {
        "pipeline": "full_briefing", "account": "Acme Corporation",
        "requested_by": "Michael Torres", "status": "completed",
        "started_at": "2025-03-14T09:12:00Z", "completed_at": "2025-03-14T09:12:22Z",
        "stages_completed": 5, "stages_total": 5,
        "agents_invoked": 9, "agents_succeeded": 9, "agents_failed": 0,
        "total_duration_sec": 22.3, "output_tokens": 4820,
    },
    "run-2002": {
        "pipeline": "quick_snapshot", "account": "Contoso Ltd",
        "requested_by": "Sarah Kim", "status": "completed",
        "started_at": "2025-03-14T10:05:00Z", "completed_at": "2025-03-14T10:05:06Z",
        "stages_completed": 2, "stages_total": 2,
        "agents_invoked": 2, "agents_succeeded": 2, "agents_failed": 0,
        "total_duration_sec": 5.5, "output_tokens": 1240,
    },
    "run-2003": {
        "pipeline": "full_briefing", "account": "Fabrikam Industries",
        "requested_by": "Michael Torres", "status": "running",
        "started_at": "2025-03-14T14:30:00Z", "completed_at": None,
        "stages_completed": 3, "stages_total": 5,
        "agents_invoked": 6, "agents_succeeded": 5, "agents_failed": 1,
        "total_duration_sec": 16.1, "output_tokens": 3100,
    },
    "run-2004": {
        "pipeline": "competitive_deep_dive", "account": "Northwind Traders",
        "requested_by": "Casey Brown", "status": "queued",
        "started_at": None, "completed_at": None,
        "stages_completed": 0, "stages_total": 3,
        "agents_invoked": 0, "agents_succeeded": 0, "agents_failed": 0,
        "total_duration_sec": 0, "output_tokens": 0,
    },
}

_AGENT_HEALTH = {
    "AccountProfileAgent": {"status": "healthy", "avg_latency_ms": 1120, "success_rate": 99.2, "last_invocation": "2025-03-14T14:30:02Z"},
    "AccountHealthScoreAgent": {"status": "healthy", "avg_latency_ms": 890, "success_rate": 98.7, "last_invocation": "2025-03-14T14:30:02Z"},
    "StakeholderMappingAgent": {"status": "healthy", "avg_latency_ms": 2340, "success_rate": 97.5, "last_invocation": "2025-03-14T14:30:09Z"},
    "EngagementTrackerAgent": {"status": "healthy", "avg_latency_ms": 1560, "success_rate": 99.1, "last_invocation": "2025-03-14T14:30:09Z"},
    "CompetitiveIntelligenceAgent": {"status": "degraded", "avg_latency_ms": 3450, "success_rate": 94.3, "last_invocation": "2025-03-14T14:30:15Z"},
    "NewsMonitorAgent": {"status": "healthy", "avg_latency_ms": 1890, "success_rate": 98.0, "last_invocation": "2025-03-14T14:30:15Z"},
    "DealRiskAssessmentAgent": {"status": "healthy", "avg_latency_ms": 1340, "success_rate": 99.4, "last_invocation": "2025-03-14T14:30:19Z"},
    "ValueMessagingAgent": {"status": "healthy", "avg_latency_ms": 1120, "success_rate": 99.6, "last_invocation": "2025-03-14T14:30:19Z"},
    "BriefingDocumentAgent": {"status": "healthy", "avg_latency_ms": 2100, "success_rate": 99.8, "last_invocation": "2025-03-14T09:12:22Z"},
    "WinLossAnalyzerAgent": {"status": "healthy", "avg_latency_ms": 2780, "success_rate": 97.9, "last_invocation": "2025-03-13T16:45:00Z"},
    "BattlecardGeneratorAgent": {"status": "healthy", "avg_latency_ms": 1950, "success_rate": 98.5, "last_invocation": "2025-03-13T16:49:00Z"},
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _estimate_duration(pipeline_key):
    """Compute estimated pipeline duration from stage timings."""
    pipe = _PIPELINES.get(pipeline_key)
    if not pipe:
        return 0.0
    return sum(s["avg_duration_sec"] for s in pipe["stages"])


def _total_agents_in_pipeline(pipeline_key):
    """Count unique agents across all stages."""
    pipe = _PIPELINES.get(pipeline_key)
    if not pipe:
        return 0
    agents = set()
    for stage in pipe["stages"]:
        agents.update(stage["agents"])
    return len(agents)


def _pipeline_health(pipeline_key):
    """Assess overall pipeline health from agent health data."""
    pipe = _PIPELINES.get(pipeline_key)
    if not pipe:
        return "unknown"
    agents = set()
    for stage in pipe["stages"]:
        agents.update(stage["agents"])
    statuses = [_AGENT_HEALTH.get(a, {}).get("status", "unknown") for a in agents]
    if all(s == "healthy" for s in statuses):
        return "healthy"
    if any(s == "down" for s in statuses):
        return "degraded"
    return "warning"


def _avg_success_rate(pipeline_key):
    """Average success rate across pipeline agents."""
    pipe = _PIPELINES.get(pipeline_key)
    if not pipe:
        return 0.0
    agents = set()
    for stage in pipe["stages"]:
        agents.update(stage["agents"])
    rates = [_AGENT_HEALTH.get(a, {}).get("success_rate", 0) for a in agents]
    return round(sum(rates) / max(len(rates), 1), 1)


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

class AccountIntelligenceOrchestrator(BasicAgent):
    """
    Coordinates multi-agent pipelines for account intelligence.

    Operations:
        orchestrate_briefing - plan and describe a pipeline execution
        run_pipeline         - simulate running a pipeline with status
        check_status         - check status of orchestration runs
        generate_report      - full orchestration health and metrics report
    """

    def __init__(self):
        self.name = "AccountIntelligenceOrchestrator"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "orchestrate_briefing", "run_pipeline",
                            "check_status", "generate_report",
                        ],
                        "description": "The orchestration operation to perform",
                    },
                    "pipeline": {
                        "type": "string",
                        "description": "Pipeline key (full_briefing, quick_snapshot, competitive_deep_dive)",
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Orchestration run ID for status checks",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "orchestrate_briefing")
        dispatch = {
            "orchestrate_briefing": self._orchestrate_briefing,
            "run_pipeline": self._run_pipeline,
            "check_status": self._check_status,
            "generate_report": self._generate_report,
        }
        handler = dispatch.get(op)
        if not handler:
            return f"**Error:** Unknown operation `{op}`."
        return handler(**kwargs)

    # ── orchestrate_briefing ──────────────────────────────────
    def _orchestrate_briefing(self, **kwargs):
        pipeline_key = kwargs.get("pipeline", "full_briefing")
        pipe = _PIPELINES.get(pipeline_key)
        if not pipe:
            return f"**Error:** Pipeline `{pipeline_key}` not found. Available: {', '.join(_PIPELINES.keys())}"

        est = _estimate_duration(pipeline_key)
        agent_count = _total_agents_in_pipeline(pipeline_key)
        health = _pipeline_health(pipeline_key)

        stage_rows = ""
        for s in pipe["stages"]:
            mode = "Parallel" if s["parallel"] else "Sequential"
            agents = ", ".join(s["agents"])
            stage_rows += f"| {s['stage']} | {s['name']} | {agents} | {mode} | {s['avg_duration_sec']}s |\n"

        return (
            f"**Pipeline Execution Plan: {pipe['name']}**\n\n"
            f"| Property | Value |\n|---|---|\n"
            f"| Pipeline ID | {pipe['id']} |\n"
            f"| Total Stages | {len(pipe['stages'])} |\n"
            f"| Total Agents | {agent_count} |\n"
            f"| Est. Duration | {est:.1f}s |\n"
            f"| Pipeline Health | {health.title()} |\n"
            f"| Avg Success Rate | {_avg_success_rate(pipeline_key)}% |\n\n"
            f"**Stage Sequence:**\n\n"
            f"| Stage | Name | Agents | Mode | Avg Time |\n|---|---|---|---|---|\n"
            f"{stage_rows}\n"
            f"**Agent Readiness:**\n"
            + "".join(
                f"- {a}: {_AGENT_HEALTH[a]['status'].title()} "
                f"({_AGENT_HEALTH[a]['avg_latency_ms']}ms avg latency)\n"
                for s in pipe["stages"] for a in s["agents"] if a in _AGENT_HEALTH
            )
            + f"\nSource: [Orchestration Engine + Agent Registry]\n"
            f"Agents: AccountIntelligenceOrchestrator"
        )

    # ── run_pipeline ──────────────────────────────────────────
    def _run_pipeline(self, **kwargs):
        pipeline_key = kwargs.get("pipeline", "full_briefing")
        pipe = _PIPELINES.get(pipeline_key)
        if not pipe:
            return f"**Error:** Pipeline `{pipeline_key}` not found."

        est = _estimate_duration(pipeline_key)
        agent_count = _total_agents_in_pipeline(pipeline_key)

        stage_status = ""
        for i, s in enumerate(pipe["stages"]):
            if i < 3:
                icon = "DONE"
                dur = f"{s['avg_duration_sec']}s"
            elif i == 3:
                icon = "RUNNING"
                dur = "in progress"
            else:
                icon = "PENDING"
                dur = "waiting"
            stage_status += f"| {s['stage']} | {s['name']} | {icon} | {dur} |\n"

        completed_agents = sum(len(s["agents"]) for s in pipe["stages"][:3])
        running_agents = len(pipe["stages"][3]["agents"]) if len(pipe["stages"]) > 3 else 0

        return (
            f"**Pipeline Execution: {pipe['name']}**\n\n"
            f"| Property | Value |\n|---|---|\n"
            f"| Run ID | run-2005 |\n"
            f"| Status | Running |\n"
            f"| Progress | Stage 4 of {len(pipe['stages'])} |\n"
            f"| Agents Completed | {completed_agents}/{agent_count} |\n"
            f"| Agents Running | {running_agents} |\n"
            f"| Elapsed Time | {sum(s['avg_duration_sec'] for s in pipe['stages'][:3]):.1f}s |\n"
            f"| Est. Remaining | {sum(s['avg_duration_sec'] for s in pipe['stages'][3:]):.1f}s |\n\n"
            f"**Stage Progress:**\n\n"
            f"| Stage | Name | Status | Duration |\n|---|---|---|---|\n"
            f"{stage_status}\n"
            f"**Live Agent Output:**\n"
            f"- AccountProfileAgent: Returned firmographics for target account\n"
            f"- StakeholderMappingAgent: Mapped 8 stakeholders across buying committee\n"
            f"- CompetitiveIntelligenceAgent: Identified 2 active competitors\n"
            f"- DealRiskAssessmentAgent: Processing risk factors...\n\n"
            f"Source: [Orchestration Engine]\n"
            f"Agents: AccountIntelligenceOrchestrator"
        )

    # ── check_status ──────────────────────────────────────────
    def _check_status(self, **kwargs):
        run_id = kwargs.get("run_id", "run-2001")
        run = _ORCHESTRATION_RUNS.get(run_id)
        if not run:
            return f"**Error:** Run `{run_id}` not found. Available: {', '.join(_ORCHESTRATION_RUNS.keys())}"

        pipe = _PIPELINES.get(run["pipeline"], {})
        pipe_name = pipe.get("name", run["pipeline"]) if pipe else run["pipeline"]

        started = run["started_at"] or "Not started"
        completed = run["completed_at"] or "In progress"
        failed_note = ""
        if run["agents_failed"] > 0:
            failed_note = f"\n**Warning:** {run['agents_failed']} agent(s) failed during execution. Check agent health dashboard."

        return (
            f"**Orchestration Run Status: {run_id}**\n\n"
            f"| Property | Value |\n|---|---|\n"
            f"| Pipeline | {pipe_name} |\n"
            f"| Account | {run['account']} |\n"
            f"| Requested By | {run['requested_by']} |\n"
            f"| Status | {run['status'].title()} |\n"
            f"| Stages | {run['stages_completed']}/{run['stages_total']} |\n"
            f"| Agents Invoked | {run['agents_invoked']} |\n"
            f"| Agents Succeeded | {run['agents_succeeded']} |\n"
            f"| Agents Failed | {run['agents_failed']} |\n"
            f"| Duration | {run['total_duration_sec']}s |\n"
            f"| Output Tokens | {run['output_tokens']:,} |\n"
            f"| Started | {started} |\n"
            f"| Completed | {completed} |\n"
            f"{failed_note}\n"
            f"Source: [Orchestration Engine + Run History]\n"
            f"Agents: AccountIntelligenceOrchestrator"
        )

    # ── generate_report ───────────────────────────────────────
    def _generate_report(self, **kwargs):
        total_runs = len(_ORCHESTRATION_RUNS)
        completed_runs = sum(1 for r in _ORCHESTRATION_RUNS.values() if r["status"] == "completed")
        running_runs = sum(1 for r in _ORCHESTRATION_RUNS.values() if r["status"] == "running")
        queued_runs = sum(1 for r in _ORCHESTRATION_RUNS.values() if r["status"] == "queued")
        total_agents_invoked = sum(r["agents_invoked"] for r in _ORCHESTRATION_RUNS.values())
        total_failures = sum(r["agents_failed"] for r in _ORCHESTRATION_RUNS.values())
        avg_duration = sum(r["total_duration_sec"] for r in _ORCHESTRATION_RUNS.values() if r["status"] == "completed") / max(completed_runs, 1)

        pipeline_rows = ""
        for key, pipe in _PIPELINES.items():
            est = _estimate_duration(key)
            health = _pipeline_health(key)
            cnt = _total_agents_in_pipeline(key)
            pipeline_rows += f"| {pipe['name']} | {len(pipe['stages'])} stages | {cnt} agents | {est:.1f}s est. | {health.title()} |\n"

        agent_rows = ""
        for agent_name, health in sorted(_AGENT_HEALTH.items()):
            agent_rows += (
                f"| {agent_name} | {health['status'].title()} | "
                f"{health['avg_latency_ms']}ms | {health['success_rate']}% |\n"
            )

        run_rows = ""
        for run_id, run in _ORCHESTRATION_RUNS.items():
            run_rows += (
                f"| {run_id} | {run['account']} | {run['pipeline']} | "
                f"{run['status'].title()} | {run['total_duration_sec']}s |\n"
            )

        return (
            f"**Orchestration Health Report**\n\n"
            f"**Summary:**\n"
            f"| Metric | Value |\n|---|---|\n"
            f"| Total Runs | {total_runs} |\n"
            f"| Completed | {completed_runs} |\n"
            f"| Running | {running_runs} |\n"
            f"| Queued | {queued_runs} |\n"
            f"| Total Agents Invoked | {total_agents_invoked} |\n"
            f"| Agent Failures | {total_failures} |\n"
            f"| Avg Completion Time | {avg_duration:.1f}s |\n\n"
            f"**Available Pipelines:**\n\n"
            f"| Pipeline | Stages | Agents | Est. Duration | Health |\n|---|---|---|---|---|\n"
            f"{pipeline_rows}\n"
            f"**Agent Health Dashboard:**\n\n"
            f"| Agent | Status | Avg Latency | Success Rate |\n|---|---|---|---|\n"
            f"{agent_rows}\n"
            f"**Recent Runs:**\n\n"
            f"| Run ID | Account | Pipeline | Status | Duration |\n|---|---|---|---|---|\n"
            f"{run_rows}\n"
            f"Source: [Orchestration Engine + Agent Registry + Run History]\n"
            f"Agents: AccountIntelligenceOrchestrator"
        )


if __name__ == "__main__":
    agent = AccountIntelligenceOrchestrator()
    for op in ["orchestrate_briefing", "run_pipeline", "check_status", "generate_report"]:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
