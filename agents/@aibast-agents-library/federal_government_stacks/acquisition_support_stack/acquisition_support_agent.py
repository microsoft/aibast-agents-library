"""
Acquisition Support Agent — Federal Government Stack

Provides acquisition lifecycle support including FAR/DFAR compliance,
vendor evaluation, procurement timelines, and compliance checklists
for federal acquisition professionals.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/acquisition-support",
    "version": "1.0.0",
    "display_name": "Acquisition Support Agent",
    "description": "Federal acquisition lifecycle support with FAR/DFAR compliance, vendor evaluation, and procurement timeline management.",
    "author": "AIBAST",
    "tags": ["acquisition", "FAR", "DFAR", "procurement", "vendor-evaluation", "federal"],
    "category": "federal_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

# ---------------------------------------------------------------------------
# Synthetic domain data
# ---------------------------------------------------------------------------

FAR_REQUIREMENTS = {
    "FAR 15.3": {
        "title": "Source Selection",
        "description": "Policies and procedures for negotiated competitive acquisitions",
        "key_provisions": [
            "Evaluation factors must be stated in solicitation",
            "Cost/price evaluation required for all competitive acquisitions",
            "Past performance must be evaluated for acquisitions over $1M",
        ],
        "threshold": 1000000,
    },
    "FAR 19.5": {
        "title": "Small Business Set-Asides",
        "description": "Requirements for setting aside acquisitions for small businesses",
        "key_provisions": [
            "Acquisitions between $10K-$250K reserved for small business",
            "Market research required to identify small business capability",
            "SBA size standards apply by NAICS code",
        ],
        "threshold": 250000,
    },
    "FAR 12.6": {
        "title": "Commercial Item Streamlining",
        "description": "Streamlined procedures for acquiring commercial items",
        "key_provisions": [
            "Use of simplified evaluation procedures permitted",
            "Standard commercial warranties acceptable",
            "Reduced documentation requirements for commercial items",
        ],
        "threshold": 7500000,
    },
    "FAR 8.4": {
        "title": "Federal Supply Schedules",
        "description": "Ordering procedures under GSA Federal Supply Schedules",
        "key_provisions": [
            "Three or more quotes required for orders over micro-purchase",
            "Best value determination required",
            "Statement of work required for services",
        ],
        "threshold": 0,
    },
}

DFAR_SUPPLEMENTS = {
    "DFARS 252.204-7012": {
        "title": "Safeguarding Covered Defense Information",
        "applicability": "All DoD contracts with CDI",
        "compliance_standard": "NIST SP 800-171",
        "assessment_required": True,
    },
    "DFARS 252.204-7021": {
        "title": "CMMC Requirements",
        "applicability": "DoD contracts requiring CMMC certification",
        "compliance_standard": "CMMC Level 2",
        "assessment_required": True,
    },
    "DFARS 215.403-1": {
        "title": "Certified Cost or Pricing Data",
        "applicability": "Acquisitions exceeding $2M threshold",
        "compliance_standard": "TINA",
        "assessment_required": False,
    },
}

VENDOR_PROPOSALS = {
    "VP-2025-001": {
        "vendor": "Meridian Defense Systems",
        "cage_code": "3AB47",
        "naics": "541512",
        "proposal_amount": 4750000,
        "technical_score": 88.5,
        "past_performance_rating": "Satisfactory",
        "small_business": False,
        "cmmc_level": 2,
        "delivery_days": 180,
    },
    "VP-2025-002": {
        "vendor": "Patriot Tech Solutions",
        "cage_code": "7KF92",
        "naics": "541512",
        "proposal_amount": 3980000,
        "technical_score": 91.2,
        "past_performance_rating": "Highly Satisfactory",
        "small_business": True,
        "cmmc_level": 2,
        "delivery_days": 210,
    },
    "VP-2025-003": {
        "vendor": "Centurion Analytics Group",
        "cage_code": "5DL83",
        "naics": "541519",
        "proposal_amount": 5120000,
        "technical_score": 85.0,
        "past_performance_rating": "Satisfactory",
        "small_business": False,
        "cmmc_level": 3,
        "delivery_days": 150,
    },
    "VP-2025-004": {
        "vendor": "Osprey Federal Services",
        "cage_code": "1RM56",
        "naics": "541512",
        "proposal_amount": 4200000,
        "technical_score": 79.8,
        "past_performance_rating": "Neutral",
        "small_business": True,
        "cmmc_level": 1,
        "delivery_days": 240,
    },
}

EVALUATION_CRITERIA = {
    "technical_approach": {"weight": 35, "max_score": 100},
    "past_performance": {"weight": 25, "max_score": 100},
    "cost_price": {"weight": 20, "max_score": 100},
    "management_approach": {"weight": 10, "max_score": 100},
    "small_business_plan": {"weight": 10, "max_score": 100},
}

PROCUREMENT_TIMELINES = {
    "PRJ-FY25-101": {
        "title": "Enterprise Cloud Migration Services",
        "acquisition_type": "Full & Open Competition",
        "estimated_value": 12500000,
        "milestones": {
            "acquisition_plan_approval": {"target": "2025-02-15", "actual": "2025-02-18", "status": "complete"},
            "market_research": {"target": "2025-03-01", "actual": "2025-03-01", "status": "complete"},
            "solicitation_release": {"target": "2025-04-15", "actual": None, "status": "in_progress"},
            "proposal_due": {"target": "2025-05-30", "actual": None, "status": "pending"},
            "evaluation_complete": {"target": "2025-07-15", "actual": None, "status": "pending"},
            "award_decision": {"target": "2025-08-01", "actual": None, "status": "pending"},
        },
    },
    "PRJ-FY25-102": {
        "title": "Cybersecurity Operations Center Staffing",
        "acquisition_type": "8(a) Sole Source",
        "estimated_value": 3200000,
        "milestones": {
            "acquisition_plan_approval": {"target": "2025-01-10", "actual": "2025-01-10", "status": "complete"},
            "market_research": {"target": "2025-01-25", "actual": "2025-01-28", "status": "complete"},
            "solicitation_release": {"target": "2025-02-20", "actual": "2025-02-22", "status": "complete"},
            "proposal_due": {"target": "2025-03-15", "actual": "2025-03-14", "status": "complete"},
            "evaluation_complete": {"target": "2025-04-01", "actual": None, "status": "in_progress"},
            "award_decision": {"target": "2025-04-15", "actual": None, "status": "pending"},
        },
    },
    "PRJ-FY25-103": {
        "title": "Data Analytics Platform Modernization",
        "acquisition_type": "GSA Schedule",
        "estimated_value": 850000,
        "milestones": {
            "acquisition_plan_approval": {"target": "2025-03-01", "actual": None, "status": "in_progress"},
            "market_research": {"target": "2025-03-20", "actual": None, "status": "pending"},
            "solicitation_release": {"target": "2025-04-10", "actual": None, "status": "pending"},
            "proposal_due": {"target": "2025-04-25", "actual": None, "status": "pending"},
            "evaluation_complete": {"target": "2025-05-10", "actual": None, "status": "pending"},
            "award_decision": {"target": "2025-05-20", "actual": None, "status": "pending"},
        },
    },
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _compute_weighted_score(proposal):
    """Compute weighted evaluation score for a vendor proposal."""
    pp_scores = {"Highly Satisfactory": 95, "Satisfactory": 80, "Neutral": 60, "Unsatisfactory": 30}
    tech = proposal["technical_score"]
    pp = pp_scores.get(proposal["past_performance_rating"], 50)
    cost_efficiency = max(0, 100 - (proposal["proposal_amount"] / 100000))
    sb_bonus = 90 if proposal["small_business"] else 60
    mgmt = min(100, tech * 0.9)
    weighted = (
        tech * EVALUATION_CRITERIA["technical_approach"]["weight"]
        + pp * EVALUATION_CRITERIA["past_performance"]["weight"]
        + cost_efficiency * EVALUATION_CRITERIA["cost_price"]["weight"]
        + mgmt * EVALUATION_CRITERIA["management_approach"]["weight"]
        + sb_bonus * EVALUATION_CRITERIA["small_business_plan"]["weight"]
    ) / 100.0
    return round(weighted, 2)


def _get_applicable_far(value):
    """Return applicable FAR clauses based on acquisition value."""
    applicable = []
    for ref, data in FAR_REQUIREMENTS.items():
        if value >= data["threshold"]:
            applicable.append((ref, data["title"]))
    return applicable


def _timeline_progress(project):
    """Calculate milestone completion percentage."""
    milestones = project["milestones"]
    total = len(milestones)
    complete = sum(1 for m in milestones.values() if m["status"] == "complete")
    return round((complete / total) * 100, 1) if total else 0.0


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class AcquisitionSupportAgent(BasicAgent):
    """Federal acquisition support agent for procurement lifecycle management."""

    def __init__(self):
        self.name = "@aibast-agents-library/acquisition-support"
        self.metadata = {
            "name": self.name,
            "display_name": "Acquisition Support Agent",
            "description": __manifest__["description"],
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "acquisition_overview",
                            "vendor_evaluation",
                            "compliance_checklist",
                            "timeline_tracker",
                        ],
                    },
                    "project_id": {"type": "string"},
                    "vendor_id": {"type": "string"},
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "acquisition_overview")
        dispatch = {
            "acquisition_overview": self._acquisition_overview,
            "vendor_evaluation": self._vendor_evaluation,
            "compliance_checklist": self._compliance_checklist,
            "timeline_tracker": self._timeline_tracker,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`."
        return handler(**kwargs)

    # -- Operations ----------------------------------------------------------

    def _acquisition_overview(self, **kwargs) -> str:
        lines = ["# Federal Acquisition Overview\n"]
        lines.append("## Active Procurements\n")
        lines.append("| Project ID | Title | Type | Est. Value | Progress |")
        lines.append("|---|---|---|---|---|")
        for pid, proj in PROCUREMENT_TIMELINES.items():
            pct = _timeline_progress(proj)
            lines.append(
                f"| {pid} | {proj['title']} | {proj['acquisition_type']} "
                f"| ${proj['estimated_value']:,.0f} | {pct}% |"
            )
        total_value = sum(p["estimated_value"] for p in PROCUREMENT_TIMELINES.values())
        lines.append(f"\n**Total Pipeline Value:** ${total_value:,.0f}")
        lines.append(f"\n**Active Vendor Proposals:** {len(VENDOR_PROPOSALS)}")
        lines.append("\n## Applicable Regulatory Framework\n")
        for ref, data in FAR_REQUIREMENTS.items():
            lines.append(f"- **{ref}** — {data['title']}")
        for ref, data in DFAR_SUPPLEMENTS.items():
            lines.append(f"- **{ref}** — {data['title']}")
        return "\n".join(lines)

    def _vendor_evaluation(self, **kwargs) -> str:
        vendor_id = kwargs.get("vendor_id")
        if vendor_id and vendor_id in VENDOR_PROPOSALS:
            vp = VENDOR_PROPOSALS[vendor_id]
            score = _compute_weighted_score(vp)
            lines = [f"# Vendor Evaluation: {vp['vendor']}\n"]
            lines.append(f"- **Proposal ID:** {vendor_id}")
            lines.append(f"- **CAGE Code:** {vp['cage_code']}")
            lines.append(f"- **NAICS:** {vp['naics']}")
            lines.append(f"- **Proposal Amount:** ${vp['proposal_amount']:,.0f}")
            lines.append(f"- **Technical Score:** {vp['technical_score']}/100")
            lines.append(f"- **Past Performance:** {vp['past_performance_rating']}")
            lines.append(f"- **Small Business:** {'Yes' if vp['small_business'] else 'No'}")
            lines.append(f"- **CMMC Level:** {vp['cmmc_level']}")
            lines.append(f"- **Delivery:** {vp['delivery_days']} days")
            lines.append(f"\n**Weighted Composite Score:** {score}")
            return "\n".join(lines)

        lines = ["# Vendor Evaluation Summary\n"]
        lines.append("| Proposal | Vendor | Amount | Technical | PP Rating | Weighted Score |")
        lines.append("|---|---|---|---|---|---|")
        ranked = []
        for vid, vp in VENDOR_PROPOSALS.items():
            score = _compute_weighted_score(vp)
            ranked.append((vid, vp, score))
        ranked.sort(key=lambda x: x[2], reverse=True)
        for vid, vp, score in ranked:
            lines.append(
                f"| {vid} | {vp['vendor']} | ${vp['proposal_amount']:,.0f} "
                f"| {vp['technical_score']} | {vp['past_performance_rating']} | {score} |"
            )
        lines.append(f"\n**Recommendation:** {ranked[0][1]['vendor']} (highest weighted score: {ranked[0][2]})")
        return "\n".join(lines)

    def _compliance_checklist(self, **kwargs) -> str:
        project_id = kwargs.get("project_id", "PRJ-FY25-101")
        proj = PROCUREMENT_TIMELINES.get(project_id, list(PROCUREMENT_TIMELINES.values())[0])
        value = proj["estimated_value"]
        applicable_far = _get_applicable_far(value)
        lines = [f"# Compliance Checklist: {proj['title']}\n"]
        lines.append(f"**Estimated Value:** ${value:,.0f}\n")
        lines.append("## FAR Requirements\n")
        for ref, title in applicable_far:
            provisions = FAR_REQUIREMENTS[ref]["key_provisions"]
            lines.append(f"### {ref} — {title}\n")
            for p in provisions:
                lines.append(f"- [ ] {p}")
            lines.append("")
        lines.append("## DFARS Supplements\n")
        for ref, data in DFAR_SUPPLEMENTS.items():
            lines.append(f"### {ref} — {data['title']}\n")
            lines.append(f"- **Applicability:** {data['applicability']}")
            lines.append(f"- **Standard:** {data['compliance_standard']}")
            status = "Required" if data["assessment_required"] else "Not Required"
            lines.append(f"- **Assessment:** {status}")
            lines.append("")
        return "\n".join(lines)

    def _timeline_tracker(self, **kwargs) -> str:
        lines = ["# Procurement Timeline Tracker\n"]
        for pid, proj in PROCUREMENT_TIMELINES.items():
            pct = _timeline_progress(proj)
            lines.append(f"## {pid}: {proj['title']}\n")
            lines.append(f"- **Type:** {proj['acquisition_type']}")
            lines.append(f"- **Value:** ${proj['estimated_value']:,.0f}")
            lines.append(f"- **Completion:** {pct}%\n")
            lines.append("| Milestone | Target | Actual | Status |")
            lines.append("|---|---|---|---|")
            for mname, mdata in proj["milestones"].items():
                display = mname.replace("_", " ").title()
                actual = mdata["actual"] or "—"
                status_icon = {"complete": "Done", "in_progress": "In Progress", "pending": "Pending"}
                lines.append(
                    f"| {display} | {mdata['target']} | {actual} "
                    f"| {status_icon.get(mdata['status'], mdata['status'])} |"
                )
            lines.append("")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent = AcquisitionSupportAgent()
    print(agent.perform(operation="acquisition_overview"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="vendor_evaluation"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="vendor_evaluation", vendor_id="VP-2025-002"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="compliance_checklist", project_id="PRJ-FY25-101"))
    print("\n" + "=" * 80 + "\n")
    print(agent.perform(operation="timeline_tracker"))
