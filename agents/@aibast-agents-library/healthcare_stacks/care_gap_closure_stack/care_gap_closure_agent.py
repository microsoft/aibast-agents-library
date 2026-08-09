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
        "Handles synthetic care-gap and quality-measure questions: use gap_analysis for the "
        "largest evidence-review queue or priority gaps, cohort_review to organize review cohorts, "
        "outreach_draft to draft unsent outreach, and quality_dashboard for source completeness. "
        "Human clinical and quality review is required; it never determines eligibility or contacts patients."
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

ALIASES = {
    "patient_prioritization": "cohort_review",
    "outreach_campaign": "outreach_draft",
    "hedis_dashboard": "quality_dashboard",
}


def _notice(title):
    return [f"# {title}", "", f"> {SAFETY}", ""]


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
                        "enum": ["gap_analysis", "cohort_review", "outreach_draft", "quality_dashboard"],
                        "description": (
                            "Route by intent: gap_analysis for 'largest evidence-review queue', "
                            "'priority gaps', or measure analysis; cohort_review for organizing cohorts "
                            "without clinical risk scoring; outreach_draft for drafting but not sending "
                            "outreach; quality_dashboard for a qualitative source-completeness dashboard."
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


if __name__ == "__main__":
    agent = CareGapClosureAgent()
    for op in agent.metadata["parameters"]["properties"]["operation"]["enum"]:
        print(agent.perform(operation=op))
