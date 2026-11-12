"""Read-only, synthetic care-gap operations support."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent


__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/care-gap-closure",
    "version": "1.1.0",
    "display_name": "Care Gap Closure Agent",
    "description": (
        "Prioritizes synthetic Medicare Advantage care gaps before the HEDIS deadline: panel status, "
        "top gaps by revenue and reachability, diabetes risk tiers and barriers, a barrier-specific "
        "outreach strategy, campaign projection, and monitoring alerts, plus source-evidence views "
        "(gap_analysis, cohort_review, outreach_draft, quality_dashboard). Human clinical and quality "
        "review is required; it never determines eligibility, launches campaigns, or contacts patients."
    ),
    "author": "AIBAST",
    "tags": ["care-gaps", "quality-measures", "outreach-draft", "healthcare", "human-review"],
    "category": "healthcare",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

SAFETY = (
    "Synthetic aggregate data only. Measure eligibility, exclusions, clinical interpretation, "
    "and outreach approval remain with authorized quality and clinical reviewers. This agent "
    "does not diagnose, contact patients, schedule care, or change records."
)

MEASURES = {
    "SYN-BCS": {
        "name": "Synthetic Breast Screening Measure",
        "source_population": 400,
        "source_closed": 292,
        "evidence_as_of": "2026-07-31",
        "limitations": "Eligibility and exclusions are unvalidated synthetic source fields.",
    },
    "SYN-COL": {
        "name": "Synthetic Colorectal Screening Measure",
        "source_population": 520,
        "source_closed": 338,
        "evidence_as_of": "2026-07-31",
        "limitations": "Clinical exclusions and external claims may be incomplete.",
    },
    "SYN-CDC": {
        "name": "Synthetic Diabetes Monitoring Measure",
        "source_population": 310,
        "source_closed": 257,
        "evidence_as_of": "2026-07-31",
        "limitations": "Recent labs and measure-year attribution require reviewer validation.",
    },
}

COHORTS = {
    "multiple_source_gaps": {"count": 42, "barrier": "mixed evidence completeness", "draft_channel": "staff review queue"},
    "single_source_gap": {"count": 117, "barrier": "recent evidence may be missing", "draft_channel": "portal draft"},
    "contact_data_review": {"count": 19, "barrier": "contact preference not confirmed", "draft_channel": "privacy review queue"},
}

# Medicare Advantage panel (synthetic) for the HEDIS prioritization demo.
PANEL = {
    "population": "Medicare Advantage",
    "patients": 2847,
    "hedis_score": 72.3,
    "hedis_target": 75.0,
    "star_impact": -0.5,
    "days_to_deadline": 23,
}

HEDIS_MEASURES = [
    {"measure": "Diabetes A1C test", "patients": 387, "revenue_risk": 189450, "reachable_pct": 76},
    {"measure": "Breast cancer screen", "patients": 243, "revenue_risk": 94170, "reachable_pct": 89},
    {"measure": "Colorectal screen", "patients": 198, "revenue_risk": 76890, "reachable_pct": 62},
    {"measure": "Statin therapy", "patients": 176, "revenue_risk": 43120, "reachable_pct": 91},
    {"measure": "Blood pressure control", "patients": 138, "revenue_risk": 25270, "reachable_pct": 84},
]

A1C_TIERS = [
    {"tier": "A1C >9.0 (Critical)", "avg_gap": "8.7 months", "priority": "Immediate"},
    {"tier": "A1C 7-9 (Moderate)", "avg_gap": "7.2 months", "priority": "High"},
    {"tier": "Never tested", "avg_gap": "New diagnosis", "priority": "High"},
]

A1C_BARRIERS = [
    {"barrier": "Transportation", "patients": 132},
    {"barrier": "No-show history", "patients": 108},
    {"barrier": "Language (Spanish)", "patients": 70},
    {"barrier": "Insurance lapsed", "patients": 46},
]

A1C_COMPLEXITY = 4.2

INTERVENTIONS = [
    {"barrier": "Transportation barriers", "intervention": "Mobile clinic slots + ride vouchers"},
    {"barrier": "No-show history", "intervention": "SMS reminders (48h, 24h, 2h intervals)"},
    {"barrier": "Language barriers", "intervention": "Spanish-speaking MA staff + translated materials"},
    {"barrier": "High-risk A1C", "intervention": "Direct RN outreach within 48 hours"},
]

CHANNEL_PLAN = {
    "valid_mobile_pct": 76,
    "voicemail": 387,
    "portal": 312,
    "rn_callbacks": 94,
    "response": {"SMS": 42, "Patient portal": 28, "Voice calls": 35, "RN outreach": 78},
    "mobile_clinic_slots": 47,
    "ride_vouchers": 132,
    "close_rate_pct": 68,
}

MONITORING = {
    "features": [
        "Daily 8 AM summary via Teams",
        "Real-time close rate tracking",
        "Weekly trend vs last HEDIS cycle",
        "Barrier analysis by patient cohort",
    ],
    "alerts": [
        "Close rate drops below 60%",
        "3 failed contact attempts",
        "Critical patient non-response >48h",
        "Campaign budget variance >15%",
    ],
}

OPERATIONS = [
    "gap_analysis",
    "cohort_review",
    "outreach_draft",
    "quality_dashboard",
    "hedis_status",
    "top_gaps",
    "risk_stratification",
    "outreach_strategy",
    "campaign_projection",
    "monitoring_plan",
]

ALIASES = {
    "patient_prioritization": "cohort_review",
    "outreach_campaign": "outreach_draft",
    "hedis_dashboard": "quality_dashboard",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


def _gap_totals():
    patients, revenue = 0, 0
    for row in HEDIS_MEASURES:
        patients += row["patients"]
        revenue += row["revenue_risk"]
    return patients, revenue


def _a1c():
    return HEDIS_MEASURES[0]


def _sms_count():
    return _a1c()["patients"] * CHANNEL_PLAN["valid_mobile_pct"] // 100


def _projected_saved():
    """Closed patients = close rate x A1C gap patients; saved = closed x per-patient incentive, to the nearest $100."""
    a1c = _a1c()
    closed = a1c["patients"] * CHANNEL_PLAN["close_rate_pct"] // 100
    return closed, int(round(closed * a1c["revenue_risk"] / a1c["patients"], -2))


def _selected_measure(measure_id):
    if not measure_id:
        return MEASURES.items()
    if measure_id not in MEASURES:
        return []
    return [(measure_id, MEASURES[measure_id])]


class CareGapClosureAgent(BasicAgent):
    """Summarize aggregate source evidence without making clinical decisions."""

    def __init__(self):
        self.name = "CareGapClosureAgent"
        self.metadata = {
            "name": self.name,
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(OPERATIONS),
                        "description": (
                            "Medicare Advantage HEDIS demo flow: hedis_status for 'prioritize care gaps "
                            "for our Medicare Advantage population' / current status; top_gaps for the "
                            "top gaps and which are most actionable; risk_stratification for the diabetes "
                            "cohort analysis; outreach_strategy to design (and launch) the outreach "
                            "strategy; campaign_projection for campaign deployment and projected impact; "
                            "monitoring_plan to configure monitoring and alerts. Source-evidence views: "
                            "gap_analysis for the 'largest evidence-review queue' across SYN- measures; "
                            "cohort_review for organizing review cohorts without clinical risk scoring; "
                            "outreach_draft for drafting but not sending a measure letter; "
                            "quality_dashboard for a qualitative source-completeness dashboard."
                        ),
                    },
                    "measure_id": {
                        "type": "string",
                        "enum": sorted(MEASURES),
                        "description": "Optional synthetic measure identifier.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = ALIASES.get(kwargs.get("operation", ""), kwargs.get("operation", ""))
        routes = {
            "gap_analysis": self._gap_analysis,
            "cohort_review": self._cohort_review,
            "outreach_draft": self._outreach_draft,
            "quality_dashboard": self._quality_dashboard,
            "hedis_status": self._hedis_status,
            "top_gaps": self._top_gaps,
            "risk_stratification": self._risk_stratification,
            "outreach_strategy": self._outreach_strategy,
            "campaign_projection": self._campaign_projection,
            "monitoring_plan": self._monitoring_plan,
        }
        if operation not in routes:
            return f"**Error:** Unknown operation `{operation}`. No action was taken."
        return routes[operation](kwargs.get("measure_id"))

    def _gap_analysis(self, measure_id=None):
        rows = list(_selected_measure(measure_id))
        if not rows:
            return f"# Gap Analysis\n\n> {SAFETY}\n\nNo synthetic measure matched `{measure_id}`."
        lines = _notice("Source-Evidence Gap Analysis")
        largest_id, largest = max(
            rows,
            key=lambda item: item[1]["source_population"] - item[1]["source_closed"],
        )
        largest_queue = largest["source_population"] - largest["source_closed"]
        lines.extend([
            f"**Largest evidence-review queue:** {largest_id} — {largest_queue} records.",
            "",
        ])
        for mid, measure in rows:
            source_gap = measure["source_population"] - measure["source_closed"]
            lines.extend([
                f"## {measure['name']} ({mid})",
                f"- Source population: {measure['source_population']}",
                f"- Source-recorded closed: {measure['source_closed']}",
                f"- Records requiring evidence review: {source_gap}",
                f"- Limitation: {measure['limitations']}",
                "",
            ])
        return "\n".join(lines)

    def _cohort_review(self, _measure_id=None):
        lines = _notice("Aggregate Cohort Review")
        lines.append("Ordering is operational triage only, not clinical risk scoring.")
        lines.append("")
        for cohort, data in COHORTS.items():
            lines.extend([
                f"## {cohort.replace('_', ' ').title()}",
                f"- Synthetic count: {data['count']}",
                f"- Evidence barrier: {data['barrier']}",
                f"- Draft handling route: {data['draft_channel']}",
                "",
            ])
        return "\n".join(lines)

    def _outreach_draft(self, measure_id=None):
        rows = list(_selected_measure(measure_id))
        if not rows:
            return f"# Outreach Draft\n\n> {SAFETY}\n\nNo synthetic measure matched `{measure_id}`."
        lines = _notice("Outreach Draft")
        lines.append("No message is sent. Privacy, consent, accessibility, and clinical content require approval.")
        lines.append("")
        for mid, measure in rows:
            lines.extend([
                f"## {measure['name']} ({mid})",
                "- Draft: We are reviewing our records and invite you to contact the care team if you have questions.",
                "- Do not state that care is overdue or that the recipient is eligible until a reviewer validates the record.",
                "- Approval route: quality reviewer → clinician when needed → authorized outreach operator.",
                "",
            ])
        return "\n".join(lines)

    def _quality_dashboard(self, measure_id=None):
        rows = list(_selected_measure(measure_id))
        if not rows:
            return f"# Quality Dashboard\n\n> {SAFETY}\n\nNo synthetic measure matched `{measure_id}`."
        lines = _notice("Qualitative Quality Dashboard")
        lines.extend([
            "| Measure | Source completeness signal | Evidence date | Reviewer note |",
            "|---|---:|---|---|",
        ])
        for mid, measure in rows:
            rate = round(measure["source_closed"] / measure["source_population"] * 100, 1)
            lines.append(f"| {mid} | {rate}% source-recorded closed | {measure['evidence_as_of']} | {measure['limitations']} |")
        return "\n".join(lines)

    # ── Medicare Advantage HEDIS demo flow (video turns 1-6) ───
    def _hedis_status(self, _measure_id=None):
        patients, revenue = _gap_totals()
        a1c = _a1c()
        pct = round(patients * 100 / PANEL["patients"], 1)
        lines = _notice("HEDIS Performance Summary")
        lines.extend([
            f"I've analyzed your {PANEL['population']} panel across the synthetic HEDIS quality measures. "
            "You have significant gaps affecting your Star Rating and revenue.",
            "",
            "| Metric | Current | Impact |",
            "|---|---|---|",
            f"| Total MA patients | {PANEL['patients']:,} | Active panel |",
            f"| Patients with gaps | {patients:,} ({pct}%) | Action needed |",
            f"| HEDIS score | {PANEL['hedis_score']}% | Target: {PANEL['hedis_target']:g}% |",
            f"| Star rating impact | {PANEL['star_impact']} stars | Below threshold |",
            f"| Revenue at risk | ${revenue:,} | {PANEL['days_to_deadline']} days to deadline |",
            "",
            f"**Top Concern:** {a1c['measure']} gaps affecting {a1c['patients']} patients and "
            f"${a1c['revenue_risk']:,} in quality incentives.",
            "",
            "Source: [EHR + HEDIS Analytics (synthetic)]",
            "",
            "Should I break down the top gaps by measure?",
        ])
        return "\n".join(lines)

    def _top_gaps(self, _measure_id=None):
        a1c = _a1c()
        lines = _notice("Top 5 Care Gap Measures")
        lines.extend([
            "Ranked by revenue impact and patient reachability:",
            "",
            "| Measure | Patients | Revenue Risk | Reachable |",
            "|---|---|---|---|",
        ])
        for row in HEDIS_MEASURES:
            lines.append(f"| {row['measure']} | {row['patients']} | ${row['revenue_risk']:,} | {row['reachable_pct']}% |")
        patients, revenue = _gap_totals()
        lines.extend([
            f"| **Total** | **{patients:,}** | **${revenue:,}** | |",
            "",
            f"**Best Opportunity:** {a1c['measure']} group - {a1c['patients']} patients with high closure "
            "potential and the largest revenue impact.",
            "",
            "Source: [HEDIS Engine + Patient Engagement Data (synthetic)]",
            "",
            "Want to see the diabetes cohort analysis?",
        ])
        return "\n".join(lines)

    def _risk_stratification(self, _measure_id=None):
        a1c = _a1c()
        lines = _notice("Diabetes Cohort Risk Stratification")
        lines.extend([
            f"Analysis of {a1c['patients']} diabetic patients shows clear risk tiers and addressable "
            "barriers (stratification from synthetic source fields for reviewer prioritization; not a diagnosis).",
            "",
            "| Risk Level | Avg Gap | Priority |",
            "|---|---|---|",
        ])
        for tier in A1C_TIERS:
            lines.append(f"| {tier['tier']} | {tier['avg_gap']} | {tier['priority']} |")
        lines.extend(["", "**Engagement Barriers:**"])
        for b in A1C_BARRIERS:
            pct = round(b["patients"] * 100 / a1c["patients"])
            lines.append(f"- {b['barrier']}: {pct}% ({b['patients']} patients)")
        lines.extend([
            f"- Complexity: Average {A1C_COMPLEXITY} chronic conditions per patient",
            "",
            "Source: [EHR Clinical Data + Social Determinants (synthetic)]",
            "",
            "Shall I design a targeted outreach campaign?",
        ])
        return "\n".join(lines)

    def _outreach_strategy(self, _measure_id=None):
        plan = CHANNEL_PLAN
        lines = _notice("Outreach Strategy Draft")
        lines.extend([
            "Multi-channel campaign designed with barrier-specific interventions. It is ready for your "
            "approval to launch; no message is sent until an authorized outreach operator launches it.",
            "",
            "**Personalized Interventions:**",
        ])
        for i in INTERVENTIONS:
            lines.append(f"- {i['barrier']}: {i['intervention']}")
        lines.extend([
            "",
            "**Campaign Scope (drafted):**",
            f"- {_sms_count()} SMS ({plan['valid_mobile_pct']}% valid mobile)",
            f"- {plan['voicemail']} voicemails (next 3 days)",
            f"- {plan['portal']} patient portal messages",
            f"- {plan['rn_callbacks']} RN callbacks prioritized",
            "",
            "Source: [Patient Engagement Platform (synthetic)]",
            "",
            "Want to see the campaign deployment plan and projected impact?",
        ])
        return "\n".join(lines)

    def _campaign_projection(self, _measure_id=None):
        plan = CHANNEL_PLAN
        a1c = _a1c()
        closed, saved = _projected_saved()
        volumes = {
            "SMS": f"{_sms_count()} patients",
            "Patient portal": f"{plan['portal']} messages",
            "Voice calls": f"{plan['voicemail']} queued",
            "RN outreach": f"{plan['rn_callbacks']} scheduled",
        }
        lines = _notice("Campaign Deployment Plan and Projected Impact")
        lines.extend([
            "Deployment plan across all channels (ready to launch on approval) with projected outcomes.",
            "",
            "| Channel | Planned Volume | Response Rate |",
            "|---|---|---|",
        ])
        for channel, rate in plan["response"].items():
            lines.append(f"| {channel} | {volumes[channel]} | {rate}% expected |")
        lines.extend([
            "",
            "**Resource Allocation (requests for approval):**",
            f"- Mobile clinic slots: {plan['mobile_clinic_slots']} to reserve (next 2 weeks)",
            f"- Ride vouchers: {plan['ride_vouchers']} to issue",
            "- Appointment capacity: next-day Tue/Thu slots to open",
            "",
            "**Projected Outcomes:**",
            f"- Close rate: {plan['close_rate_pct']}% (based on historical campaigns) = {closed} of {a1c['patients']} patients",
            f"- Revenue saved: ${saved:,} of ${a1c['revenue_risk']:,} at risk",
            "",
            "Source: [Campaign Management + Historical Analytics (synthetic)]",
            "",
            "Want to set up monitoring?",
        ])
        return "\n".join(lines)

    def _monitoring_plan(self, _measure_id=None):
        lines = _notice("Monitoring and Alert Configuration")
        lines.extend([
            "Recommended monitoring dashboard and alerting, ready for your team to turn on.",
            "",
            "**Dashboard Features:**",
        ])
        lines += [f"- {f}" for f in MONITORING["features"]]
        lines.extend(["", "**Alert Triggers:**"])
        lines += [f"- {a}" for a in MONITORING["alerts"]]
        lines.extend([
            "",
            "Data flow: data lake -> Power BI -> Teams notifications.",
            "",
            "Source: [Power BI + Teams (synthetic)]",
            "",
            "Want a full campaign summary?",
        ])
        return "\n".join(lines)


if __name__ == "__main__":
    agent = CareGapClosureAgent()
    for op in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
        print(agent.perform(operation=op))
