"""
Client Health Score Agent

Monitors professional-services client portfolios using engagement metrics,
NPS scores, project margins, utilization rates, and escalation history.
Surfaces at-risk accounts and generates retention action plans.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/client-health-score",
    "version": "1.1.1",
    "display_name": "Client Health Score Agent",
    "description": "Automate client portfolio health monitoring and planning to improve client relationships, protect revenue, and optimize financial performance.",
    "author": "AIBAST",
    "tags": ["client-health", "NPS", "retention", "professional-services", "churn"],
    "category": "professional_services",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

CLIENTS = {
    "CL-301": {
        "name": "TechCorp Industries",
        "annual_value": 2400000,
        "nps": -15,
        "project_margin_pct": 18.2,
        "utilization_pct": 64,
        "billing_trend": "declining",
        "escalations_90d": 4,
        "exec_meetings_90d": 0,
        "satisfaction_scores": [8.4, 8.3, 8.2, 5.1],
        "health_score": 42,
        "health_score_prior": 60,
        "risk_label": "CRITICAL",
    },
    "CL-302": {
        "name": "Global Finance Corp",
        "annual_value": 1500000,
        "nps": -20,
        "project_margin_pct": 22.5,
        "utilization_pct": 45,
        "billing_trend": "flat",
        "escalations_90d": 2,
        "exec_meetings_90d": 1,
        "satisfaction_scores": [7.8, 7.2, 6.5, 6.0],
        "health_score": 58,
        "health_score_prior": 64,
        "risk_label": "AT_RISK",
    },
    "CL-303": {
        "name": "Healthcare Solutions Inc",
        "annual_value": 1200000,
        "nps": 5,
        "project_margin_pct": 26.0,
        "utilization_pct": 72,
        "billing_trend": "flat",
        "escalations_90d": 3,
        "exec_meetings_90d": 1,
        "satisfaction_scores": [8.0, 7.8, 7.0, 6.8],
        "health_score": 61,
        "health_score_prior": 66,
        "risk_label": "AT_RISK",
    },
    "CL-304": {
        "name": "Apex Manufacturing",
        "annual_value": 3200000,
        "nps": 45,
        "project_margin_pct": 31.4,
        "utilization_pct": 88,
        "billing_trend": "growing",
        "escalations_90d": 0,
        "exec_meetings_90d": 3,
        "satisfaction_scores": [8.5, 8.8, 9.0, 9.1],
        "health_score": 85,
        "health_score_prior": 86,
        "risk_label": "HEALTHY",
    },
    "CL-305": {
        "name": "National Logistics Group",
        "annual_value": 2800000,
        "nps": 38,
        "project_margin_pct": 28.7,
        "utilization_pct": 82,
        "billing_trend": "growing",
        "escalations_90d": 1,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.9, 8.2, 8.5, 8.6],
        "health_score": 80,
        "health_score_prior": 81,
        "risk_label": "HEALTHY",
    },
    "CL-306": {
        "name": "Silverline Retail",
        "annual_value": 1900000,
        "nps": 22,
        "project_margin_pct": 24.1,
        "utilization_pct": 76,
        "billing_trend": "flat",
        "escalations_90d": 1,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.5, 7.6, 7.8, 7.9],
        "health_score": 73,
        "health_score_prior": 75,
        "risk_label": "HEALTHY",
    },
    "CL-307": {
        "name": "Pinnacle Energy",
        "annual_value": 3600000,
        "nps": 52,
        "project_margin_pct": 33.0,
        "utilization_pct": 91,
        "billing_trend": "growing",
        "escalations_90d": 0,
        "exec_meetings_90d": 4,
        "satisfaction_scores": [8.8, 9.0, 9.2, 9.3],
        "health_score": 88,
        "health_score_prior": 88,
        "risk_label": "HEALTHY",
    },
    "CL-308": {
        "name": "Metro Transit Authority",
        "annual_value": 2100000,
        "nps": 30,
        "project_margin_pct": 27.3,
        "utilization_pct": 79,
        "billing_trend": "growing",
        "escalations_90d": 0,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.6, 7.9, 8.1, 8.3],
        "health_score": 77,
        "health_score_prior": 79,
        "risk_label": "HEALTHY",
    },
    "CL-309": {
        "name": "Northwind Advisory Partners",
        "annual_value": 2000000,
        "nps": 18,
        "project_margin_pct": 23.8,
        "utilization_pct": 74,
        "billing_trend": "flat",
        "escalations_90d": 1,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.4, 7.5, 7.5, 7.6],
        "health_score": 72,
        "health_score_prior": 74,
        "risk_label": "HEALTHY",
    },
    "CL-310": {
        "name": "Summit Insurance Group",
        "annual_value": 1600000,
        "nps": 20,
        "project_margin_pct": 25.2,
        "utilization_pct": 78,
        "billing_trend": "flat",
        "escalations_90d": 0,
        "exec_meetings_90d": 2,
        "satisfaction_scores": [7.6, 7.7, 7.8, 7.8],
        "health_score": 74,
        "health_score_prior": 77,
        "risk_label": "HEALTHY",
    },
}

RISK_FACTORS = {
    "CL-301": {
        "summary": "executive turnover, quality issues, overdue invoices, and competitor presence",
        "executive_contact": "None in 3 months (CTO departed)",
        "satisfaction_prior": 8.2,
        "invoice_outstanding": 340000,
        "invoice_days_overdue": 67,
        "competitive_threat": "Major consulting firm spotted on-site last week",
        "key_stakeholder": "CTO John Davis left 3 months ago, replacement not briefed on our value delivery",
        "quality": "Last project had deliverable delays",
        "issue": "Executive turnover and deliverable delays",
        "renewal_days": 0,
        "nps_prior": 10,
        "open_tickets": 9,
        "outlook": "Churn without intervention",
    },
    "CL-302": {
        "summary": "low use of contracted hours and a falling NPS ahead of renewal",
        "executive_contact": "1 meeting in 90 days",
        "satisfaction_prior": 6.5,
        "invoice_outstanding": 0,
        "invoice_days_overdue": 0,
        "competitive_threat": "None observed",
        "key_stakeholder": "CFO Jordan Patel owns the renewal decision",
        "quality": "No open quality issue",
        "issue": "Using only 45% of contracted hours",
        "renewal_days": 90,
        "nps_prior": 15,
        "open_tickets": 6,
        "outlook": "Non-renewal likely",
    },
    "CL-303": {
        "summary": "a support backlog and a new CTO who is skeptical of our value",
        "executive_contact": "1 meeting in 90 days",
        "satisfaction_prior": 7.0,
        "invoice_outstanding": 0,
        "invoice_days_overdue": 0,
        "competitive_threat": "None observed",
        "key_stakeholder": "New CTO: Skeptical of our value",
        "quality": "Support backlog",
        "issue": "47 open support tickets (backlog)",
        "renewal_days": 150,
        "nps_prior": 12,
        "open_tickets": 47,
        "outlook": "Budget cut or replacement",
    },
}

RETENTION_PLAYBOOK = {
    "client": "CL-301",
    "basis": "our successful turnaround playbook",
    "weeks": [
        {"week": "Week 1: Stabilization", "actions": [
            "Day 1: CEO to CEO call (proposed; confirm on your CEO's calendar)",
            "Day 2: Resolve invoice dispute ($50K credit proposed, requires finance approval)",
            "Days 3-5: Deploy SWAT team to fix quality issues",
        ]},
        {"week": "Week 2: Trust Rebuild", "actions": [
            "Executive review with new CTO Sarah Mitchell",
            "Present historical value: $4.2M savings delivered",
            "ROI dashboard: 34% efficiency improvements",
        ]},
        {"week": "Week 3: Value Demonstration", "actions": [
            "Quick wins: 2-3 immediate improvements",
            "Success metrics: Real-time dashboard",
            "Stakeholder mapping: 4 key executives",
        ]},
        {"week": "Week 4: Future Security", "actions": [
            "Revised contract terms",
            "Quarterly business reviews formalized",
            "Executive sponsor program",
        ]},
    ],
    "investment": 600000,
    "investment_note": "credits + resources",
    "success_probability_pct": 73,
    "value_delivered": 4200000,
    "efficiency_gain_pct": 34,
    "retained_margin_pct": 50,
    "roi_years": 2,
}

OUTREACH_SEQUENCE = [
    {"day": "Tuesday", "who": "Sarah Mitchell (CTO)", "name": "Sarah Mitchell", "focus": "Technical deep dive",
     "show": ["$4.2M cost savings we delivered", "34% efficiency improvements"], "goal": "Rebuild technical credibility"},
    {"day": "Wednesday", "who": "CFO", "focus": "ROI review",
     "show": ["Financial impact metrics", "Invoice dispute resolution"], "goal": "Close the invoice dispute"},
    {"day": "Thursday", "who": "Morgan Lee (COO)", "focus": "Process optimization results",
     "show": ["Operational improvements", "Future roadmap"], "goal": "Agree the delivery roadmap"},
    {"day": "Friday", "who": "CEO", "focus": "Strategic partnership discussion",
     "show": ["Long-term value proposition"], "goal": "Commitment to improved delivery"},
]

OUTREACH_MATERIALS = ["Executive briefing decks", "Success dashboards", "ROI documentation"]

STAKEHOLDERS = {
    "CL-301": {
        "executive_sponsor": "Morgan Lee, COO",
        "new_cto": "Sarah Mitchell, CTO (new; not yet briefed on our value delivery)",
        "account_owner": "Rachel Adams",
        "delivery_lead": "Elena Vasquez",
        "next_engagement": "Executive review with new CTO Sarah Mitchell",
    },
    "CL-302": {
        "executive_sponsor": "Jordan Patel, CFO",
        "account_owner": "Marcus Reed",
        "delivery_lead": "Michael Chen",
        "next_engagement": "Value realization workshop",
    },
    "CL-303": {
        "executive_sponsor": "Taylor Brooks, CIO",
        "account_owner": "Nina Shah",
        "delivery_lead": "Priya Sharma",
        "next_engagement": "Escalation closure and roadmap review",
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _portfolio_value():
    """Total annual portfolio value."""
    return sum(c["annual_value"] for c in CLIENTS.values())


def _at_risk_value():
    """Sum of annual value for CRITICAL and AT_RISK clients."""
    return sum(c["annual_value"] for c in CLIENTS.values() if c["risk_label"] in ("CRITICAL", "AT_RISK"))


def _avg_health():
    """Average health score across all clients."""
    scores = [c["health_score"] for c in CLIENTS.values()]
    return round(sum(scores) / len(scores), 1)


def _prior_avg_health():
    """Average health score last quarter."""
    scores = [c["health_score_prior"] for c in CLIENTS.values()]
    return round(sum(scores) / len(scores), 1)


def _millions(amount):
    """2400000 -> '$2.4M'; 600000 -> '$600K'."""
    if amount < 1000000:
        return f"${amount // 1000}K"
    return f"${amount / 1000000:.1f}M"


def _resolve_client(query):
    """Client ID or (part of) a client name; default TechCorp Industries; None when nothing matches."""
    if not query:
        return "CL-301"
    q = str(query).lower().strip()
    for cid, c in CLIENTS.items():
        if q == cid.lower() or q in c["name"].lower():
            return cid
    return None


def _status_rows():
    """Status roll-up: label, client count, annual value, action."""
    rows = []
    for label, shown, action in [("CRITICAL", "CRITICAL", "Immediate"), ("AT_RISK", "At Risk", "30-day plan"),
                                 ("HEALTHY", "Healthy", "Monitor")]:
        group = [c for c in CLIENTS.values() if c["risk_label"] == label]
        rows.append({"status": shown, "clients": len(group),
                     "value": sum(c["annual_value"] for c in group), "action": action})
    return rows


def _satisfaction_trend(client):
    """Return trend direction based on last 4 quarterly scores."""
    scores = client["satisfaction_scores"]
    if len(scores) < 2:
        return "insufficient_data"
    if scores[-1] > scores[0] + 0.3:
        return "improving"
    elif scores[-1] < scores[0] - 0.3:
        return "declining"
    return "stable"


def _churn_probability(client):
    """Simplified churn probability from health score."""
    hs = client["health_score"]
    if hs <= 45:
        return 0.78
    elif hs <= 60:
        return 0.45
    elif hs <= 70:
        return 0.20
    elif hs <= 80:
        return 0.10
    return 0.03


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

_OPERATIONS = [
    "health_dashboard",
    "engagement_analysis",
    "satisfaction_trend",
    "at_risk_clients",
    "retention_plan",
    "risk_analysis",
    "stakeholder_outreach",
    "qbr_summary",
]


class ClientHealthScoreAgent(BasicAgent):
    """Monitors client health and identifies at-risk accounts."""

    def __init__(self):
        self.name = "ClientHealthScoreAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "The required tool for any professional-services client, account, relationship, "
                "or portfolio-health question, including quarterly business review (QBR) prep. Always "
                "invoke it instead of giving generic guidance when a client-success leader, account "
                "manager, or client-experience director asks for health scores for top clients and "
                "which relationships are healthy, at risk, or critical; what "
                "engagement signals are weakening, especially executive contact, escalations, "
                "billing trend, or utilization; which satisfaction trends are moving the wrong "
                "way; which accounts need intervention and recovery actions; a client's risk "
                "analysis (e.g. TechCorp); a retention roadmap; a stakeholder map and executive "
                "engagement plan or outreach sequence for turnaround accounts; or a session summary. "
                "The packaged synthetic portfolio is sufficient and every operation has defaults "
                "(TechCorp Industries is the default client). Indicators are decision support, "
                "not factual predictions, and the tool never contacts clients or changes CRM."
            ),
            "operations": list(_OPERATIONS),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "Choose from the user's persona language, not operation words. "
                            "health_dashboard: QBR prep, health scores for top clients, which relationships "
                            "are healthy, at risk, or critical and where to focus first. engagement_analysis: "
                            "what engagement signals are weakening across the portfolio, especially "
                            "executive contact, escalations, declining billing trend, or "
                            "utilization. satisfaction_trend: which client satisfaction trends "
                            "are moving the wrong way and what evidence supports it. "
                            "at_risk_clients: the other at-risk clients / accounts needing intervention now, "
                            "risk drivers, and first recovery actions. retention_plan: retention roadmap "
                            "(30-day plan), stakeholder maps, turnaround playbooks, and executive engagement "
                            "plans. risk_analysis: one client's risk analysis (what is driving TechCorp down). "
                            "stakeholder_outreach: who to reach first and the executive outreach sequence. "
                            "qbr_summary: schedule the outreach / wrap up with a session summary."
                        ),
                    },
                    "client": {
                        "type": "string",
                        "enum": [c["name"] for c in CLIENTS.values()],
                        "description": "Client name for risk_analysis (default TechCorp Industries)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "health_dashboard")
        dispatch = {
            "health_dashboard": self._health_dashboard,
            "engagement_analysis": self._engagement_analysis,
            "satisfaction_trend": self._satisfaction_trend,
            "at_risk_clients": self._at_risk_clients,
            "retention_plan": self._retention_plan,
            "risk_analysis": self._risk_analysis,
            "stakeholder_outreach": self._stakeholder_outreach,
            "qbr_summary": self._qbr_summary,
        }
        handler = dispatch.get(operation)
        if handler is None:
            return f"**Error:** Unknown operation `{operation}`. Valid: {', '.join(dispatch.keys())}"
        return handler(**kwargs)

    # ------------------------------------------------------------------
    def _health_dashboard(self, **kwargs) -> str:
        pv = _portfolio_value()
        arv = _at_risk_value()
        avg = _avg_health()
        drop = round(_prior_avg_health() - avg, 1)
        worst = sorted(CLIENTS.values(), key=lambda c: c["health_score"])[0]
        lines = ["## Client Health Dashboard\n",
                 f"I've analyzed your {_millions(pv)} consulting portfolio and identified critical risk requiring "
                 f"immediate intervention - {worst['name']} at {worst['health_score']}/100 with "
                 f"{_millions(worst['annual_value'])} at risk.\n",
                 "### Portfolio Health Overview\n",
                 "| Status | Clients | Annual Value | Action |",
                 "|--------|--------:|-------------:|--------|"]
        for r in _status_rows():
            lines.append(f"| {r['status']} | {r['clients']} | {_millions(r['value'])} | {r['action']} |")
        lines += ["\n### Key Metrics\n",
                  f"- **Portfolio value:** ${pv:,.0f} ({_millions(pv)} annually)",
                  f"- **Avg health score:** {avg:g}/100 (down {drop:g} points QoQ)",
                  f"- **At-risk value:** ${arv:,.0f} ({_millions(arv)}, {round(arv / pv * 100):.0f}% of portfolio)",
                  f"- **Immediate action:** {worst['name']}",
                  f"\n**{worst['name'].split()[0]} Alert:** Dropped from {worst['health_score_prior']}/100 to "
                  f"{worst['health_score']}/100 in 90 days with multiple risk factors converging.\n",
                  "| Client | Annual Value | Health | Churn Indicator | NPS | Margin | Util % | Risk |",
                  "|--------|-------------|--------|-----------------|-----|--------|--------|------|"]
        for c in sorted(CLIENTS.values(), key=lambda c: c["health_score"]):
            lines.append(
                f"| {c['name']} | ${c['annual_value']:,.0f} | {c['health_score']}/100 | "
                f"{_churn_probability(c)*100:.0f}% | "
                f"{c['nps']:+d} | {c['project_margin_pct']}% | {c['utilization_pct']}% | **{c['risk_label']}** |"
            )
        rows = _status_rows()
        lines.append(f"\n**Distribution:** {rows[0]['clients']} critical, {rows[1]['clients']} at-risk, "
                     f"{rows[2]['clients']} healthy")
        lines.append("\nSource: [D365 CE + Client Success Platform + Project Ops]")
        lines.append("\n> Synthetic scenario indicators, not validated predictions or live CRM scores.")
        lines.append(f"\nNext: want to see what's driving {worst['name'].split()[0]} down?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _engagement_analysis(self, **kwargs) -> str:
        lines = ["## Engagement Analysis\n"]
        lines.append("| Client | Exec Meetings (90d) | Escalations (90d) | Billing Trend | Utilization |")
        lines.append("|--------|--------------------:|------------------:|---------------|-------------|")
        for cid, c in CLIENTS.items():
            flag = " **LOW**" if c["exec_meetings_90d"] == 0 and c["risk_label"] != "HEALTHY" else ""
            lines.append(
                f"| {c['name']} | {c['exec_meetings_90d']}{flag} | {c['escalations_90d']} | "
                f"{c['billing_trend']} | {c['utilization_pct']}% |"
            )

        lines.append("\n### Engagement Red Flags\n")
        for cid, c in CLIENTS.items():
            flags = []
            if c["exec_meetings_90d"] == 0:
                flags.append("No executive contact in 90 days")
            if c["escalations_90d"] >= 3:
                flags.append(f"{c['escalations_90d']} escalations in 90 days")
            if c["utilization_pct"] < 60:
                flags.append(f"Low utilization ({c['utilization_pct']}%) -- may not see value")
            if c["billing_trend"] == "declining":
                flags.append("Declining billing trend")
            if flags:
                lines.append(f"**{c['name']}:**")
                for f in flags:
                    lines.append(f"- {f}")
                lines.append("")
        lines.append("> Synthetic engagement data. No client record, task, meeting, or message was created.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _satisfaction_trend(self, **kwargs) -> str:
        lines = ["## Client Satisfaction Trends\n"]
        lines.append("| Client | Q1 | Q2 | Q3 | Q4 | Trend | NPS |")
        lines.append("|--------|-----|-----|-----|-----|-------|-----|")
        for cid, c in CLIENTS.items():
            scores = c["satisfaction_scores"]
            trend = _satisfaction_trend(c)
            trend_icon = {"improving": "UP", "declining": "DOWN", "stable": "FLAT"}.get(trend, "-")
            cols = " | ".join(f"{s:.1f}" for s in scores)
            lines.append(f"| {c['name']} | {cols} | **{trend_icon}** | {c['nps']:+d} |")

        declining = [c for c in CLIENTS.values() if _satisfaction_trend(c) == "declining"]
        if declining:
            lines.append("\n### Declining Accounts Requiring Attention\n")
            for c in declining:
                drop = round(c["satisfaction_scores"][0] - c["satisfaction_scores"][-1], 1)
                lines.append(f"- **{c['name']}**: dropped {drop} points over 4 quarters (NPS: {c['nps']:+d})")
        lines.append("\n> Synthetic survey history; validate source quality before client action.")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _at_risk_clients(self, **kwargs) -> str:
        pv = _portfolio_value()
        at_risk = {cid: c for cid, c in CLIENTS.items() if c["risk_label"] in ("CRITICAL", "AT_RISK")}
        total_risk_val = sum(c["annual_value"] for c in at_risk.values())
        lines = ["## At-Risk Client Report\n",
                 f"**Clients at risk:** {len(at_risk)}",
                 f"**Total value at risk:** ${total_risk_val:,.0f}\n"]
        for cid, c in sorted(at_risk.items(), key=lambda x: x[1]["health_score"]):
            rf = RISK_FACTORS[cid]
            churn = _churn_probability(c)
            lines.append(f"### {c['name']} -- Health: {c['health_score']}/100 ({c['risk_label']})")
            lines.append(f"- **Contract value:** ${c['annual_value']:,.0f} annually")
            lines.append(f"- **Issue:** {rf['issue']}")
            if rf["renewal_days"]:
                lines.append(f"- **Renewal:** {rf['renewal_days']} days away")
            lines.append(f"- **NPS score:** {c['nps']:+d} (was {rf['nps_prior']:+d} last quarter)")
            lines.append(f"- **Open support tickets:** {rf['open_tickets']}")
            lines.append(f"- **Key stakeholder:** {rf['key_stakeholder']}")
            lines.append(f"- **Risk:** {rf['outlook']} (churn indicator {churn*100:.0f}%)")
            lines.append(f"- **Satisfaction trend:** {_satisfaction_trend(c)}; escalations (90d): "
                         f"{c['escalations_90d']}; exec meetings (90d): {c['exec_meetings_90d']}")
            lines.append("\n**Recommended retention actions:**")
            if c["exec_meetings_90d"] == 0:
                lines.append("- Schedule executive sponsor meeting within 7 days")
            if c["escalations_90d"] >= 3 or rf["open_tickets"] >= 20:
                lines.append("- Deploy SWAT team to resolve open issues")
            if c["utilization_pct"] < 60:
                lines.append("- Review scope alignment; client may not be extracting full value")
            if c["nps"] < 0:
                lines.append("- Conduct root-cause analysis on negative NPS drivers")
            lines.append("- Prepare value-delivered summary (ROI documentation)")
            lines.append("")
        critical = sum(c["annual_value"] for c in at_risk.values() if c["risk_label"] == "CRITICAL")
        lines += ["### Combined Portfolio Risk\n",
                  f"- Total at risk: {_millions(total_risk_val)} ({round(total_risk_val * 100 / pv)}% of portfolio)",
                  f"- Critical: {_millions(critical)} (" + ", ".join(c["name"].split()[0] for c in at_risk.values()
                                                            if c["risk_label"] == "CRITICAL") + ")",
                  f"- At risk: {_millions(total_risk_val - critical)} (" + " + ".join(
                      c["name"].split()[0] for c in at_risk.values() if c["risk_label"] == "AT_RISK") + ")",
                  "\nSource: [Utilization Data + Support System + Surveys]",
                  "\n> Synthetic indicators. Recommendations require account-owner approval; churn indicators are not certainties."]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _retention_plan(self, **kwargs) -> str:
        pb = RETENTION_PLAYBOOK
        client = CLIENTS[pb["client"]]
        lines = ["## Account Retention Playbooks\n",
                 f"I've built a 30-day {client['name'].split()[0]} retention plan based on {pb['basis']}. "
                 "Week 1 focuses on immediate stabilization.\n",
                 f"### {client['name']} 30-Day Retention Plan (draft)\n"]
        for w in pb["weeks"]:
            lines.append(f"**{w['week']}**")
            for a in w["actions"]:
                lines.append(f"- {a}")
            lines.append("")
        lines.append(f"**Investment:** {_millions(pb['investment'])} ({pb['investment_note']}) | "
                     f"**Success probability:** {pb['success_probability_pct']}% with full execution\n")
        lines.append("### Stakeholder Maps\n")
        for cid, stakeholder in STAKEHOLDERS.items():
            c = CLIENTS[cid]
            lines.append(f"#### {c['name']} — {c['risk_label']}")
            lines.append(f"- **Executive sponsor:** {stakeholder['executive_sponsor']}")
            if stakeholder.get("new_cto"):
                lines.append(f"- **New executive:** {stakeholder['new_cto']}")
            lines.append(f"- **Account owner:** {stakeholder['account_owner']}")
            lines.append(f"- **Delivery lead:** {stakeholder['delivery_lead']}")
            lines.append(f"- **Next engagement:** {stakeholder['next_engagement']}")
            if c["exec_meetings_90d"] == 0:
                lines.append("- **Priority:** propose an executive sponsor meeting within seven days.")
            if c["escalations_90d"] >= 3:
                lines.append("- **Recovery:** assign an approved escalation owner and review closure evidence weekly.")
            if c["nps"] < 0:
                lines.append("- **Trust:** validate negative feedback themes before proposing corrective commitments.")
            lines.append("- **Approval gate:** account owner reviews the plan before any client outreach.\n")
        lines.append("Source: [Retention Playbook + Historical Success]\n")
        lines.append(
            "> Synthetic draft planning artifact only; no meeting, message, concession, renewal, "
            "or CRM update has been created."
        )
        lines.append("\nNext: who's the first stakeholder we need to reach?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _risk_analysis(self, **kwargs) -> str:
        cid = _resolve_client(kwargs.get("client"))
        if cid is None:
            return (f"**Unknown client** `{kwargs.get('client')}` in the synthetic portfolio. Clients: "
                    + ", ".join(c["name"] for c in CLIENTS.values()) + ".")
        c = CLIENTS[cid]
        rf = RISK_FACTORS.get(cid)
        if rf is None:
            return (f"## {c['name']} - Risk Analysis\n\n{c['name']} is HEALTHY at {c['health_score']}/100 "
                    f"(synthetic); no critical risk factors are recorded.")
        lines = [f"## {c['name']} - Risk Analysis\n",
                 f"{c['name'].split()[0]} has multiple converging risk factors - {rf['summary']}. "
                 f"Churn probability: {_churn_probability(c)*100:.0f}% without intervention.\n",
                 f"**Health Score:** {c['health_score']}/100 (down {c['health_score_prior'] - c['health_score']} "
                 f"points in 90 days) | **Contract Value:** {_millions(c['annual_value'])} annually\n",
                 "### Critical Risk Factors\n",
                 f"- **Executive contact:** {rf['executive_contact']}",
                 f"- **Project satisfaction:** {c['satisfaction_scores'][-1]}/10 (was {rf['satisfaction_prior']} last quarter)"]
        if rf["invoice_outstanding"]:
            lines.append(f"- **Invoice status:** ${rf['invoice_outstanding'] // 1000}K outstanding - "
                         f"{rf['invoice_days_overdue']} days overdue")
        lines += [f"- **Competitive threat:** {rf['competitive_threat']}",
                  f"\n**Key Stakeholder:** {rf['key_stakeholder']}",
                  f"\n**Quality Issues:** {rf['quality']}, causing satisfaction to drop from "
                  f"{rf['satisfaction_prior']} to {c['satisfaction_scores'][-1]}",
                  "\nSource: [CRM Activity + Project Metrics + AR]",
                  "\n> Synthetic risk indicators; churn probability is decision support, not a prediction.",
                  "\nNext: what about the other at-risk clients?"]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _stakeholder_outreach(self, **kwargs) -> str:
        pb = RETENTION_PLAYBOOK
        first = OUTREACH_SEQUENCE[0]
        lines = ["## Stakeholder Outreach Plan\n",
                 f"{first['name']}, their new CTO, is priority - she wasn't briefed on our "
                 f"{_millions(pb['value_delivered'])} value delivery. I've mapped a {len(OUTREACH_SEQUENCE)}-day "
                 "executive touchpoint sequence.\n"]
        for step in OUTREACH_SEQUENCE:
            lines.append(f"**{step['day']} - {step['who']}**")
            lines.append(f"- Focus: {step['focus']}")
            for item in step["show"]:
                lines.append(f"- Show: {item}")
            lines.append(f"- Goal: {step['goal']}")
            lines.append("")
        lines.append(f"**Materials Prepared (drafts):** {', '.join(OUTREACH_MATERIALS)}")
        lines.append("\nSource: [Stakeholder Analysis + Historical Data]")
        lines.append("\n> Synthetic draft sequence; no invitation or message has been sent.")
        lines.append("\nNext: want me to prepare the meeting invites and a session summary?")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def _qbr_summary(self, **kwargs) -> str:
        pv = _portfolio_value()
        arv = _at_risk_value()
        pb = RETENTION_PLAYBOOK
        tc = CLIENTS[pb["client"]]
        rows = _status_rows()
        retained = tc["annual_value"] * pb["roi_years"] * pb["retained_margin_pct"] // 100
        roi = int((retained - pb["investment"]) * 100 / pb["investment"])
        others = [c for c in CLIENTS.values() if c["risk_label"] == "AT_RISK"]
        lines = ["## QBR Session Summary\n",
                 f"All {len(OUTREACH_SEQUENCE)} stakeholder meetings are drafted as calendar invites, ready for you "
                 "to send. Here's your complete portfolio analysis and retention plan:\n",
                 f"- **Portfolio analysis** - {_millions(pv)} value, {_avg_health():g}/100 avg score "
                 f"(down {round(_prior_avg_health() - _avg_health(), 1):g} points)",
                 f"- **Risk identification** - {_millions(arv)} at risk across {rows[0]['clients'] + rows[1]['clients']} "
                 f"clients ({round(arv * 100 / pv)}% exposure)",
                 f"- **{tc['name'].split()[0]} deep-dive** - {tc['health_score']}/100 critical, "
                 f"{_churn_probability(tc)*100:.0f}% churn probability",
                 "- **Multi-client assessment** - " + ", ".join(
                     f"{c['name'].split()[0]} {c['health_score']}/100" for c in others),
                 f"- **Retention roadmap** - 30-day {tc['name'].split()[0]} plan, {pb['success_probability_pct']}% "
                 "success probability",
                 f"- **Outreach ready** - {len(OUTREACH_SEQUENCE)} executive meetings drafted, materials prepared\n",
                 "### Value at Stake\n",
                 f"- Critical: {_millions(rows[0]['value'])} ({tc['name'].split()[0]})",
                 f"- At Risk: {_millions(rows[1]['value'])} (" + " + ".join(c["name"].split()[0] for c in others) + ")",
                 f"- Healthy: {_millions(rows[2]['value'])} (monitor status)\n",
                 f"**Retention Investment:** {_millions(pb['investment'])} for {tc['name'].split()[0]} | "
                 f"**ROI if successful:** {roi}% over {pb['roi_years']} years "
                 f"({pb['retained_margin_pct']}% margin on {_millions(tc['annual_value'])} a year retained)\n",
                 "**Ready for your approval:** calendar invites, briefing decks, success dashboards, escalation "
                 "process, CEO briefing for the Day 1 call.",
                 "\nSource: [All Connected Systems]",
                 "\n> Synthetic summary; no meeting, message, concession, renewal, or CRM update has been created."]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main — the demo video's turns in order
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = ClientHealthScoreAgent()
    for op in ["health_dashboard", "risk_analysis", "at_risk_clients", "retention_plan",
               "stakeholder_outreach", "qbr_summary", "engagement_analysis", "satisfaction_trend"]:
        print("=" * 72)
        print(agent.perform(operation=op))
        print()
