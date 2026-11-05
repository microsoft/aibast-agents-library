import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent
import json
from datetime import datetime, timedelta
import random

class D365BaseAgent(BasicAgent):
    """
    1-minute demo: AI-powered deal progression tracking with stage velocity analysis, next-best-actions, and pipeline acceleration
    
    Demo Persona: Jennifer Walsh - Regional Sales Director at CloudScale Solutions
    Context: Managing $18M pipeline across 12 reps, Q4 close pressure, need to identify at-risk deals
    """
    
    # Synthetic demo data - populated from published demo scripts
    DEMO_PERSONA = {
        "name": "Jennifer Walsh",
        "title": "Regional Sales Director",
        "company": "CloudScale Solutions",
        "context": "Managing $18M pipeline across 12 reps, Q4 close pressure, need to identify at-risk deals"
}
    
    BUSINESS_VALUE = {
        "problem": "$4.2M in stalled pipeline, 12 deals stuck averaging 21 days, Q4 close pressure",
        "solution": "AI-powered deal progression with root cause analysis, action plans, and automated tracking",
        "roi": "$2.4M added to Q4 commit, reduce stall time from 21 to 10 days, 78% pipeline health",
        "performance": "21 specific actions assigned, automated early warning, weekly accountability cadence"
}
    
    TRIGGER_PHRASES = [
        "Show me which deals are stalled in my pipeline and what actions will move them forward.",
        "analyze deal velocity",
        "identify stalled opportunities"
]
    
    AGENTS_UTILIZED = [
        {
                "name": "PipelineAnalyticsAgent",
                "description": "Analyzes full pipeline health with deal-level metrics and trends",
                "data_sources": [
                        "Salesforce CRM",
                        "Pipeline Analytics"
                ]
        },
        {
                "name": "StalledDealDetectionAgent",
                "description": "Identifies deals stuck in stage beyond normal velocity thresholds",
                "data_sources": [
                        "CRM",
                        "Activity Logs",
                        "Email Analytics"
                ]
        },
        {
                "name": "DealDiagnosticsAgent",
                "description": "Deep-dives into individual deals to identify root cause of stalls",
                "data_sources": [
                        "CRM",
                        "Meeting Notes",
                        "Email Threads",
                        "Call Transcripts"
                ]
        },
        {
                "name": "NextBestActionAgent",
                "description": "Generates specific action plans to move deals forward",
                "data_sources": [
                        "Sales Playbook",
                        "Win Patterns",
                        "Best Practices DB"
                ]
        },
        {
                "name": "PipelineAccelerationAgent",
                "description": "Identifies opportunities to pull deals forward across the pipeline",
                "data_sources": [
                        "Historical Close Data",
                        "Conversion Analytics"
                ]
        },
        {
                "name": "TaskAssignmentAgent",
                "description": "Assigns actions to reps based on capacity and expertise",
                "data_sources": [
                        "Team Directory",
                        "Capacity Dashboard",
                        "Skills Matrix"
                ]
        },
        {
                "name": "PipelineReportAgent",
                "description": "Generates executive summaries and tracking dashboards",
                "data_sources": [
                        "All Pipeline Systems"
                ]
        }
]
    
    INTEGRATED_SYSTEMS = ["Activity Logs", "All Pipeline Systems", "Best Practices DB", "CRM", "Call Transcripts", "Capacity Dashboard", "Conversion Analytics", "Email Analytics", "Email Threads", "Historical Close Data", "Meeting Notes", "Pipeline Analytics", "Sales Playbook", "Salesforce CRM", "Skills Matrix", "Team Directory", "Win Patterns"]
    
    CONVERSATION_FLOW = [
        {
            "step": 1,
            "trigger": """Show me which deals are stalled in my pipeline and what actions will move them forward.""",
            "response": """I've analyzed your $18M pipeline across 47 active opportunities. 12 deals are stalled, representing $4.2M at risk.

**Pipeline Health Summary:**

| Status | Deals | Value | Avg Days Stalled |
|--------|-------|-------|------------------|
| On Track | 28 | $9.8M | - |
| At Risk | 7 | $4.0M | 8 days |
| Stalled | 12 | $4.2M | 21 days |

**Critical Stalled Deals:**

1. **TechCorp Industries** - $890K - 34 days in Proposal
2. **Global Manufacturing** - $720K - 28 days in Negotiation
3. **Apex Financial** - $580K - 25 days in Evaluation
4. **Metro Healthcare** - $440K - 22 days in Proposal

**Root Cause Analysis:**
- 5 deals: Missing executive sponsor
- 4 deals: Competitor evaluation ongoing
- 3 deals: Budget approval pending

Source: [Salesforce + Activity Analytics]
Agents: PipelineAnalyticsAgent, StalledDealDetectionAgent

Want detailed analysis on the top stalled deals?""",
            "data": {}
        },
        {
            "step": 2,
            "trigger": """Yes, give me the details on TechCorp and Global Manufacturing""",
            "response": """Deep analysis complete on both deals. Different root causes require different interventions.

**TechCorp Industries - $890K**

| Factor | Status |
|--------|--------|
| Days stalled | 34 (3x average) |
| Last contact | 18 days ago |
| Champion | VP IT (went silent) |
| Blocker | New CFO reviewing all purchases |

**Diagnosis:** Champion disengaged, economic buyer changed
**Action:** Re-engage through different stakeholder, prepare CFO-specific business case

**Global Manufacturing - $720K**

| Factor | Status |
|--------|--------|
| Days stalled | 28 days |
| Last contact | 5 days ago |
| Champion | Active but frustrated |
| Blocker | Legal review on contract terms |

**Diagnosis:** Process bottleneck, not relationship issue
**Action:** Offer pre-approved contract template, escalate with legal concession

**Velocity Comparison:** Your average deal closes in 45 days - both are significantly over.

Source: [CRM + Email Analytics + Contract System]
Agents: DealDiagnosticsAgent, StalledDealDetectionAgent

Generate specific action plans for each?""",
            "data": {}
        },
        {
            "step": 3,
            "trigger": """Yes, create action plans with specific next steps""",
            "response": """Action plans created with specific tasks, owners, and deadlines for both deals.

**TechCorp Industries Action Plan:**

**Week 1:**
- Day 1: Research new CFO background (LinkedIn, news)
- Day 2: Call VP IT - acknowledge gap, request CFO intro
- Day 3: Send CFO-tailored ROI analysis
- Day 5: Executive sponsor outreach (your VP to their CFO)

**Week 2:**
- Schedule CFO meeting with business case
- Re-present proposal with finance lens

**Global Manufacturing Action Plan:**

**This Week:**
- Today: Call champion - acknowledge legal delay
- Tomorrow: Send pre-approved contract template (removes 80% of redlines)
- Day 3: Offer 30-day out clause to reduce perceived risk
- Day 5: Legal-to-legal call to resolve remaining items

**Assigned Resources:**
- TechCorp: Sarah Kim (exec alignment specialist)
- Global: Legal team fast-track review

**Expected Outcome:** Both deals back on track within 10 days

Source: [Sales Playbook + Win Patterns]
Agents: NextBestActionAgent

Want to see the full pipeline acceleration plan?""",
            "data": {}
        },
        {
            "step": 4,
            "trigger": """Yes, show me how to accelerate the entire pipeline""",
            "response": """Pipeline acceleration strategy identified $6.8M that can be pulled forward with targeted interventions.

**Acceleration Opportunities:**

| Action | Deals Impacted | Value | Days Saved |
|--------|----------------|-------|------------|
| Executive alignment | 8 | $3.2M | 12 days avg |
| Contract fast-track | 5 | $1.8M | 8 days avg |
| Proof-of-value offer | 6 | $1.8M | 15 days avg |

**Quick Wins (Close This Week):**
- DataFlow Corp: $340K - verbal commit, awaiting signature
- Summit Industries: $280K - final approval meeting Friday
- Tech Dynamics: $190K - contract in DocuSign

**Rep-Level Actions:**

| Rep | Stalled Deals | Priority Action |
|-----|---------------|----------------|
| Mike Chen | 3 | Executive introductions |
| Lisa Torres | 2 | Contract negotiations |
| James Park | 4 | Re-engagement campaign |

**Forecast Impact:** Accelerating these deals adds $2.4M to Q4 commit.

Source: [Pipeline Analytics + Historical Patterns]
Agents: PipelineAccelerationAgent

Want me to assign tasks to the team?""",
            "data": {}
        },
        {
            "step": 5,
            "trigger": """Yes, assign tasks and set up tracking""",
            "response": """Tasks assigned to all reps with deadlines. Automated tracking enabled for accountability.

**Task Assignments Completed:**

| Rep | Tasks | Deadline | Deals |
|-----|-------|----------|-------|
| Mike Chen | 6 tasks | This week | 3 stalled |
| Lisa Torres | 4 tasks | Next 5 days | 2 stalled |
| James Park | 8 tasks | Next 7 days | 4 stalled |
| Sarah Kim | 3 tasks | This week | Exec support |

**Automated Monitoring:**
- Daily Slack alerts for overdue tasks
- Deal stage change notifications
- Weekly pipeline velocity report
- Stall warning at 7 days (vs current 21)

**Accountability Cadence:**
- Daily: Automated task reminders
- Wednesday: Pipeline review meeting (30 min)
- Friday: Deal progression scorecard

**Success Metrics:**
- Target: Reduce avg stall time from 21 to 10 days
- Goal: Move $4.2M stalled back to active
- Forecast: Add $2.4M to Q4 commit

Source: [Salesforce + Task Management]
Agents: TaskAssignmentAgent

Generate the executive summary?""",
            "data": {}
        },
        {
            "step": 6,
            "trigger": """Yes, summarize everything we accomplished""",
            "response": """Pipeline acceleration program activated. Here's your complete action plan.

**Session Summary:**

| Analysis | Result |
|----------|--------|
| Pipeline analyzed | $18M across 47 deals |
| Stalled identified | 12 deals, $4.2M at risk |
| Root causes | Champion gaps, legal delays, budget holds |
| Actions created | 21 specific tasks assigned |
| Acceleration target | $6.8M can be pulled forward |

**Immediate Impact:**
- $810K in quick wins closing this week
- TechCorp ($890K) action plan activated
- Global Manufacturing ($720K) fast-track initiated
- All 12 stalled deals have intervention plans

**Process Improvements:**
- Early warning at 7 days (was 21)
- Daily automated task tracking
- Weekly velocity reviews scheduled
- Rep accountability scorecard active

**Expected Outcomes:**
- Reduce stall time: 21 days to 10 days
- Q4 forecast improvement: +$2.4M commit
- Pipeline health: 78% on-track (from 60%)

Source: [All Pipeline Systems]
Agents: PipelineReportAgent (orchestrating all agents)

Your pipeline acceleration program transforms $4.2M in stalled deals into active opportunities with 21 assigned actions and automated tracking.""",
            "data": {}
        },
    ]
    
    def __init__(self):
        self.name = "D365BaseAgent"
        self.metadata = {
            "name": self.name,
            "description": """1-minute demo: AI-powered deal progression tracking with stage velocity analysis, next-best-actions, and pipeline acceleration""",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["execute", "analyze", "report", "optimize", "demo"],
                        "description": "Action to perform"
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Unique identifier for the entity"
                    },
                    "data": {
                        "type": "object",
                        "description": "Additional data for the operation"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["real-time", "batch", "scheduled"],
                        "description": "Processing mode"
                    },
                    "step": {
                        "type": "integer",
                        "description": "Demo conversation step (1-6)"
                    }
                },
                "required": ["action"]
            }
        }
        super().__init__(name=self.name, metadata=self.metadata)
    
    def perform(self, **kwargs):
        action = kwargs.get('action', 'execute')
        
        if action == 'demo':
            return self._demo(kwargs)
        elif action == 'execute':
            return self._execute(kwargs)
        elif action == 'analyze':
            return self._analyze(kwargs)
        elif action == 'report':
            return self._report(kwargs)
        elif action == 'optimize':
            return self._optimize(kwargs)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
    
    def _demo(self, params):
        """Run demo conversation step with synthetic data."""
        step_num = params.get('step', 1)
        if step_num < 1 or step_num > len(self.CONVERSATION_FLOW):
            return {
                "status": "error",
                "message": f"Step {step_num} not found. Available steps: 1-{len(self.CONVERSATION_FLOW)}",
                "available_steps": len(self.CONVERSATION_FLOW),
                "trigger_phrases": self.TRIGGER_PHRASES
            }
        step = self.CONVERSATION_FLOW[step_num - 1]
        return {
            "status": "success",
            "step": step_num,
            "total_steps": len(self.CONVERSATION_FLOW),
            "persona": self.DEMO_PERSONA,
            "user_message": step["trigger"],
            "agent_response": step["response"],
            "data": step.get("data", {}),
            "integrated_systems": self.INTEGRATED_SYSTEMS,
            "next_step": step_num + 1 if step_num < len(self.CONVERSATION_FLOW) else None
        }
    
    def _execute(self, params):
        """Execute primary operation with realistic synthetic data."""
        # Use first demo step as the default execute response
        first_step = self.CONVERSATION_FLOW[0] if self.CONVERSATION_FLOW else {}
        return {
            "status": "success",
            "message": f"{self.name} executed successfully",
            "data": {
                "operation_id": f"OP{random.randint(100000, 999999)}",
                "entity_id": params.get('entity_id', f"ENT{random.randint(1000, 9999)}"),
                "timestamp": datetime.now().isoformat(),
                "integrated_systems": self.INTEGRATED_SYSTEMS,
                "persona": self.DEMO_PERSONA,
                "response": first_step.get("response", "Operation completed"),
                "results": {
                    "processed_items": random.randint(10, 100),
                    "success_rate": f"{random.randint(85, 99)}%",
                    "processing_time": f"{random.randint(1, 10)} seconds"
                }
            }
        }
    
    def _analyze(self, params):
        """Perform analysis with domain-specific synthetic insights."""
        # Use second demo step for analysis content  
        analysis_step = self.CONVERSATION_FLOW[1] if len(self.CONVERSATION_FLOW) > 1 else {}
        agents_info = [a["name"] for a in self.AGENTS_UTILIZED] if self.AGENTS_UTILIZED else []
        return {
            "status": "success",
            "message": "Analysis completed",
            "data": {
                "analysis_id": f"AN{random.randint(10000, 99999)}",
                "agents_used": agents_info,
                "response": analysis_step.get("response", "Analysis complete"),
                "business_value": self.BUSINESS_VALUE,
                "confidence_score": random.randint(75, 95)
            }
        }
    
    def _report(self, params):
        """Generate report with business value metrics."""
        return {
            "status": "success",
            "message": "Report generated",
            "data": {
                "report_id": f"RPT{random.randint(10000, 99999)}",
                "summary": self.metadata["description"],
                "business_value": self.BUSINESS_VALUE,
                "persona": self.DEMO_PERSONA,
                "integrated_systems": self.INTEGRATED_SYSTEMS,
                "agents_utilized": [a["name"] for a in self.AGENTS_UTILIZED],
                "total_demo_steps": len(self.CONVERSATION_FLOW)
            }
        }
    
    def _optimize(self, params):
        """Perform optimization with domain context."""
        last_step = self.CONVERSATION_FLOW[-1] if self.CONVERSATION_FLOW else {}
        return {
            "status": "success",
            "message": "Optimization completed",
            "data": {
                "optimization_id": f"OPT{random.randint(10000, 99999)}",
                "response": last_step.get("response", "Optimization complete"),
                "business_value": self.BUSINESS_VALUE,
                "next_steps": ["Review results", "Adjust parameters", "Scale operations"]
            }
        }


if __name__ == "__main__":
    agent = D365BaseAgent()
    
    # Run demo flow
    print(f"=== {agent.name} Demo ===")
    print(f"Persona: {agent.DEMO_PERSONA.get('name', 'N/A')} - {agent.DEMO_PERSONA.get('title', 'N/A')}")
    print(f"Systems: {agent.INTEGRATED_SYSTEMS}")
    print(f"Demo steps: {len(agent.CONVERSATION_FLOW)}")
    print()
    
    for i in range(1, len(agent.CONVERSATION_FLOW) + 1):
        result = agent.perform(action="demo", step=i)
        print(f"--- Step {i} ---")
        print(f"User: {result['user_message'][:80]}...")
        print(f"Agent: {result['agent_response'][:120]}...")
        print()
