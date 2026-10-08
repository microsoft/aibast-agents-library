"""
Engineering Standards Agent

Gives distribution design and field staff fast, cited answers from a utility's
engineering standards: vetted quick-reference values first (authoritative), and
clearly labeled unvetted interpretations of the full standard text when no
vetted value exists. Unvetted answers can be prepared for engineer review, the
review queue and quick-reference sheets can be inspected, and a job can be
scoped against the standards and risk factors that apply.

Where a real deployment would read a standards document library, a vetted
quick-reference table and a work-management system, this agent uses a fixed
synthetic snapshot so it runs anywhere without credentials.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/engineering-standards-advisor",
    "version": "1.0.0",
    "display_name": "Engineering Standards Agent",
    "description": "Give designers and field crews cited answers from engineering standards in seconds: vetted values first, clearly labeled interpretations when no vetted value exists, an engineer review loop that turns good interpretations into vetted guidance, and standards-based job scoping.",
    "author": "AIBAST",
    "tags": ["energy", "utilities", "engineering-standards", "distribution-design", "knowledge-management", "field-operations"],
    "category": "energy",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed snapshot: Monday 9 March 2026)
# ═══════════════════════════════════════════════════════════════

_SNAPSHOT = "Mon 9 Mar 2026"
_ORG = "Fabrikam Energy Distribution"
_REVIEWER = "Sam Ortiz, standards engineer"
_REVIEW_SLA_DAYS = 3

_STANDARDS = {
    "DS-210": {"title": "Overhead Line Clearances", "rev": "Rev 4, 2025"},
    "DS-315": {"title": "Pole Selection and Loading", "rev": "Rev 3, 2024"},
    "DS-420": {"title": "Underground Residential Services", "rev": "Rev 2, 2025"},
    "DS-505": {"title": "Grounding and Bonding", "rev": "Rev 5, 2025"},
}

# Tier 1: vetted quick-reference rows (authoritative once vetted by a standards engineer)
_QUICK_REF = {
    "QR-210-01": {"standard": "DS-210", "item": "Primary conductor over a public road, minimum vertical clearance",
                  "value": "6.5 m", "section": "4.2, Table 4-1", "page": 14, "vetted": "3 Nov 2025", "status": "Vetted"},
    "QR-210-02": {"standard": "DS-210", "item": "Primary conductor over a driveway or private lane",
                  "value": "5.5 m", "section": "4.2, Table 4-1", "page": 14, "vetted": "3 Nov 2025", "status": "Vetted"},
    "QR-210-03": {"standard": "DS-210", "item": "Service drop over a public road",
                  "value": "5.0 m", "section": "4.3", "page": 16, "vetted": "3 Nov 2025", "status": "Vetted"},
    "QR-210-04": {"standard": "DS-210", "item": "Primary conductor horizontal clearance to a building",
                  "value": "2.5 m", "section": "5.1, Table 5-2", "page": 21, "vetted": "14 Mar 2024",
                  "status": "Re-vetting due (standard revised)"},
    "QR-315-01": {"standard": "DS-315", "item": "Minimum pole class, straight-line (tangent) structure",
                  "value": "Class 5", "section": "3.1", "page": 8, "vetted": "9 Sep 2025", "status": "Vetted"},
    "QR-315-02": {"standard": "DS-315", "item": "Minimum setting depth, 12 m pole",
                  "value": "1.8 m", "section": "3.4", "page": 11, "vetted": "9 Sep 2025", "status": "Vetted"},
    "QR-420-01": {"standard": "DS-420", "item": "Residential service cable burial depth",
                  "value": "0.75 m", "section": "2.3", "page": 6, "vetted": "21 Jan 2026", "status": "Vetted"},
    "QR-505-01": {"standard": "DS-505", "item": "Maximum ground resistance at a transformer pole",
                  "value": "25 ohms", "section": "6.2", "page": 19, "vetted": "2 Feb 2026", "status": "Vetted"},
}

# Topics a user can ask about; tier 1 topics point at a vetted row, tier 2 topics carry an interpretation
_TOPICS = {
    "road_clearance": {"tier": 1, "row": "QR-210-01", "related": "QR-210-02"},
    "driveway_clearance": {"tier": 1, "row": "QR-210-02", "related": "QR-210-01"},
    "pole_setting_depth": {"tier": 1, "row": "QR-315-02", "related": "QR-315-01"},
    "service_depth": {"tier": 1, "row": "QR-420-01", "related": "QR-505-01"},
    "ground_resistance": {"tier": 1, "row": "QR-505-01", "related": "QR-420-01"},
    "corner_transformer_pole": {
        "tier": 2, "id": "INT-0318",
        "question": "Can a Class 5 pole be used on a 35-degree corner structure carrying a 75 kVA transformer?",
        "answer": "Class 3 is indicated (two class steps above the Class 5 tangent minimum)",
        "reasoning": [
            ("DS-315", "3.2", 9, "Angle structures above 30 degrees step up one pole class."),
            ("DS-315", "3.6", 12, "A pole-mounted transformer above 50 kVA adds one further class step."),
            ("DS-315", "3.1", 8, "The straight-line minimum is Class 5 (vetted row QR-315-01)."),
        ],
        "why_unvetted": "The answer combines two sections; no vetted row covers angle plus transformer loading.",
    },
    "road_crossing_depth": {
        "tier": 2, "id": "INT-0319",
        "question": "How deep must a residential service cable be where it crosses under a public road?",
        "answer": "1.0 m is indicated under the road surface, with a protective duct",
        "reasoning": [
            ("DS-420", "2.3", 6, "Residential service burial depth is 0.75 m (vetted row QR-420-01)."),
            ("DS-420", "2.7", 9, "Road crossings add 0.25 m of cover and require a protective duct."),
        ],
        "why_unvetted": "The road-crossing case is not in the vetted quick-reference table.",
    },
}
_TOPIC_ORDER = list(_TOPICS)

_REVIEW_QUEUE = [
    {"id": "REV-0311", "topic": "Guy anchor spacing on soft ground", "standard": "DS-315", "age": 6, "from": "Field crew, North depot"},
    {"id": "REV-0314", "topic": "Bonding of a fence near a pad-mount transformer", "standard": "DS-505", "age": 4, "from": "Design technician"},
    {"id": "REV-0316", "topic": "Service drop clearance over a carport", "standard": "DS-210", "age": 2, "from": "Design technician"},
]

_JOBS = {
    "job-7712": {
        "id": "JOB-7712", "name": "Maple Ridge feeder pole replacement", "work_type": "Batch pole replacement",
        "units": 8, "unit_label": "poles", "base_days": 5.0, "per_unit": 0.3,
        "factors": [("Work near energized conductors", 3), ("Span over a public road", 2),
                    ("Steep access to two pole sites", 2), ("Planned customer outage", 2)],
        "standards": ["DS-210", "DS-315", "DS-505"],
        "open_review": "INT-0318 (corner pole with transformer at pole 6)",
    },
    "job-7720": {
        "id": "JOB-7720", "name": "Aspen Lane underground service conversion", "work_type": "Overhead to underground services",
        "units": 6, "unit_label": "services", "base_days": 4.0, "per_unit": 0.5,
        "factors": [("Existing buried utilities", 1), ("Road-opening permit required", 1),
                    ("Planned customer outage", 2)],
        "standards": ["DS-420", "DS-505"],
        "open_review": "INT-0319 (service crossing under Aspen Lane)",
    },
}
_JOB_ORDER = ["job-7712", "job-7720"]

_GATE = (
    "Synthetic engineering guidance only. Vetted values are authoritative only after engineer vetting; "
    "unvetted interpretations are not design approval. This agent does not approve a design, change a "
    "standard, submit a review, or release work."
)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _cite(std, section, page):
    return f"{std} {_STANDARDS[std]['title']}, section {section}, page {page}"


def _footer(source):
    return f"{_GATE}\n\nSource: [{source}]\nAgents: EngineeringStandardsAgent"


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "vetted_lookup", "interpretation", "flag_for_review",
    "review_queue", "quick_reference", "scope_job",
]


class EngineeringStandardsAgent(BasicAgent):
    """
    Engineering standards assistant for distribution design and field work.

    Operations:
        vetted_lookup    - Tier 1 vetted value with section and page citation
        interpretation   - Tier 2 unvetted interpretation of the full standard text, clearly labeled
        flag_for_review  - draft review item that asks a standards engineer to confirm an interpretation
        review_queue     - what is waiting for standards-engineer review
        quick_reference  - vetted quick-reference sheet for one standard, with re-vetting status
        scope_job        - risk score, effort estimate and applicable standards for a job
    """

    def __init__(self):
        self.name = "EngineeringStandardsAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Use this tool for questions about a fictional electric distribution utility's engineering "
                "standards and for scoping field jobs against them. Clearances, setting depths, burial depths and "
                "ground resistance use vetted_lookup (Tier 1, vetted). Questions the vetted table does not cover, "
                "such as which pole class a corner structure with a transformer needs, use interpretation (Tier 2, "
                "unvetted, with section citations). Asking an engineer to confirm or check an interpretation uses "
                "flag_for_review (prepares a draft, never submits). 'What is waiting for my review' uses "
                "review_queue. A quick-reference sheet or re-vetting status for a standard uses quick_reference. "
                "Scoping a job's risk, effort and applicable standards uses scope_job (it scopes the Maple Ridge pole "
                "replacement, JOB-7712, and summarizes the other job in the planning queue). Topics: road_clearance, "
                "driveway_clearance, pole_setting_depth, service_depth, ground_resistance, corner_transformer_pole, "
                "road_crossing_depth. Never present an unvetted interpretation as approved."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "vetted_lookup for a value with a vetted answer (clearances, depths, ground resistance); "
                            "interpretation for a question with no vetted value (corner pole with a transformer, road "
                            "crossing depth); flag_for_review to send an interpretation to an engineer; review_queue "
                            "for a standards engineer's pending reviews; quick_reference for a standard's vetted sheet; "
                            "scope_job for job risk, effort and standards."
                        ),
                    },
                    "topic": {
                        "type": "string",
                        "enum": list(_TOPIC_ORDER),
                        "description": "Question topic for vetted_lookup, interpretation and flag_for_review.",
                    },
                    "standard_id": {
                        "type": "string",
                        "enum": list(_STANDARDS),
                        "description": "Standard for quick_reference (DS-210 overhead clearances is the default).",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation", "vetted_lookup")
        if op == "vetted_lookup":
            return self._vetted_lookup(kwargs.get("topic") or "road_clearance")
        if op == "interpretation":
            return self._interpretation(kwargs.get("topic") or "corner_transformer_pole")
        if op == "flag_for_review":
            return self._flag_for_review(kwargs.get("topic") or "corner_transformer_pole")
        if op == "review_queue":
            return self._review_queue()
        if op == "quick_reference":
            return self._quick_reference(kwargs.get("standard_id") or "DS-210")
        if op == "scope_job":
            return self._scope_job("job-7712")
        return f"Unknown operation: {op}"

    # ── vetted_lookup ─────────────────────────────────────────
    def _vetted_lookup(self, topic):
        t = _TOPICS.get(topic)
        if t is None:
            return f"Unknown topic: {topic}. Topics: {', '.join(_TOPIC_ORDER)}.\n\n{_footer('Synthetic Standards Snapshot')}"
        if t["tier"] == 2:
            return (
                f"**No Vetted Value: {topic}**\n\n"
                f"The vetted quick-reference table has no row for this question ({t['question']}). "
                f"Ask for a Tier 2 interpretation, which is labeled unvetted and cites the standard sections.\n\n"
                f"{_footer('Synthetic Vetted Quick-Reference Table')}"
            )
        r = _QUICK_REF[t["row"]]
        rel = _QUICK_REF[t["related"]]
        return (
            f"**Tier 1 Answer (VETTED): {r['item']}**\n\n"
            f"| Detail | Value |\n|---|---|\n"
            f"| Answer | {r['value']} |\n"
            f"| Citation | {_cite(r['standard'], r['section'], r['page'])} |\n"
            f"| Quick-reference row | {t['row']} ({_STANDARDS[r['standard']]['rev']}) |\n"
            f"| Vetted | {r['vetted']} by {_REVIEWER} |\n"
            f"| Status | {r['status']} |\n\n"
            f"**Related vetted value:** {rel['item']}: {rel['value']} ({rel['standard']} section {rel['section']}).\n\n"
            f"Confirm site conditions and any local exceptions in the design record before use.\n\n"
            f"{_footer('Synthetic Vetted Quick-Reference Table')}"
        )

    # ── interpretation ────────────────────────────────────────
    def _interpretation(self, topic):
        t = _TOPICS.get(topic)
        if t is None:
            return f"Unknown topic: {topic}. Topics: {', '.join(_TOPIC_ORDER)}.\n\n{_footer('Synthetic Standards Snapshot')}"
        if t["tier"] == 1:
            r = _QUICK_REF[t["row"]]
            return (
                f"**Already Vetted: {r['item']}**\n\n"
                f"No interpretation is needed: vetted row {t['row']} gives {r['value']} "
                f"({_cite(r['standard'], r['section'], r['page'])}).\n\n"
                f"{_footer('Synthetic Vetted Quick-Reference Table')}"
            )
        rows = "\n".join(f"| {_cite(s, sec, p)} | {txt} |" for s, sec, p, txt in t["reasoning"])
        return (
            f"**Tier 2 Interpretation (UNVETTED): {t['id']}**\n\n"
            f"**Question:** {t['question']}\n\n"
            f"**Interpretation:** {t['answer']}.\n\n"
            f"| Cited section | What it says |\n|---|---|\n{rows}\n\n"
            f"**Why unvetted:** {t['why_unvetted']}\n\n"
            f"Not authoritative. Confirm with a standards engineer before using it in a design.\n\n"
            f"{_footer('Synthetic Standards Text Snapshot')}"
        )

    # ── flag_for_review ───────────────────────────────────────
    def _flag_for_review(self, topic):
        t = _TOPICS.get(topic)
        if t is None:
            return f"Unknown topic: {topic}. Topics: {', '.join(_TOPIC_ORDER)}.\n\n{_footer('Synthetic Standards Snapshot')}"
        if t["tier"] == 1:
            return (
                f"**No Review Needed: {topic}**\n\n"
                f"This topic already has a vetted value (row {t['row']}), so there is nothing to send for review.\n\n"
                f"{_footer('Synthetic Review Queue')}"
            )
        rev_id = "REV-0318" if t["id"] == "INT-0318" else "REV-0319"
        sections = "; ".join(f"{s} section {sec}" for s, sec, _p, _x in t["reasoning"])
        return (
            f"**Review Request Draft: {rev_id} (Not Submitted)**\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| Interpretation | {t['id']}: {t['answer']} |\n"
            f"| Original question | {t['question']} |\n"
            f"| Sections cited | {sections} |\n"
            f"| Reviewer | {_REVIEWER} |\n"
            f"| Review target | {_REVIEW_SLA_DAYS} business days (Thu 12 Mar 2026) |\n"
            f"| Queue position | {len(_REVIEW_QUEUE) + 1} of {len(_REVIEW_QUEUE) + 1} once submitted |\n"
            f"| Status | Draft for requester review |\n\n"
            f"**If approved:** the engineer promotes the answer to a vetted quick-reference row, so the next person "
            f"who asks gets a Tier 1 answer. **If rejected:** the engineer records the correct reading.\n\n"
            f"Submit it through the standards review workflow. Nothing was submitted.\n\n"
            f"{_footer('Synthetic Review Queue')}"
        )

    # ── review_queue ──────────────────────────────────────────
    def _review_queue(self):
        rows = "\n".join(
            f"| {r['id']} | {r['topic']} | {r['standard']} | {r['from']} | {r['age']} business days |"
            for r in _REVIEW_QUEUE
        )
        overdue = sum(1 for r in _REVIEW_QUEUE if r["age"] > _REVIEW_SLA_DAYS)
        revet = [k for k, r in _QUICK_REF.items() if r["status"] != "Vetted"]
        oldest = max(_REVIEW_QUEUE, key=lambda r: r["age"])
        return (
            f"**Standards Review Queue: {_REVIEWER}** (snapshot {_SNAPSHOT})\n\n"
            f"| Review | Topic | Standard | Raised by | Waiting |\n|---|---|---|---|---|\n{rows}\n\n"
            f"**Pending reviews:** {len(_REVIEW_QUEUE)}; {overdue} past the {_REVIEW_SLA_DAYS}-business-day target "
            f"(oldest {oldest['id']}, {oldest['age']} business days).\n"
            f"**Re-vetting due:** {len(revet)} quick-reference row ({', '.join(revet)}) after a standard revision.\n"
            f"**Expected next:** REV-0318 (corner pole with transformer) once its requester submits it.\n\n"
            f"Approving promotes an interpretation to a vetted row; rejecting records the correct reading. "
            f"Both are the engineer's decision.\n\n"
            f"{_footer('Synthetic Review Queue')}"
        )

    # ── quick_reference ───────────────────────────────────────
    def _quick_reference(self, std):
        if std not in _STANDARDS:
            return f"Unknown standard: {std}. Standards: {', '.join(_STANDARDS)}.\n\n{_footer('Synthetic Standards Snapshot')}"
        rows = [(k, r) for k, r in _QUICK_REF.items() if r["standard"] == std]
        table = "\n".join(
            f"| {k} | {r['item']} | {r['value']} | {r['section']} | {r['page']} | {r['status']} |" for k, r in rows
        )
        current = sum(1 for _k, r in rows if r["status"] == "Vetted")
        return (
            f"**Quick-Reference Sheet: {std} {_STANDARDS[std]['title']}** ({_STANDARDS[std]['rev']})\n\n"
            f"| Row | Item | Value | Section | Page | Status |\n|---|---|---|---|---|---|\n{table}\n\n"
            f"**Rows:** {len(rows)}; {current} vetted and current; {len(rows) - current} due for re-vetting.\n\n"
            f"Use a row marked for re-vetting only after a standards engineer confirms it against the current "
            f"revision.\n\n"
            f"{_footer('Synthetic Vetted Quick-Reference Table')}"
        )

    # ── scope_job ─────────────────────────────────────────────
    @staticmethod
    def _score(j):
        score = sum(w for _n, w in j["factors"])
        band = "High" if score >= 9 else "Medium" if score >= 5 else "Low"
        return score, band, j["base_days"] + j["per_unit"] * j["units"]

    def _scope_job(self, key):
        j = _JOBS[key]
        score, band, effort = self._score(j)
        others = []
        for k in _JOB_ORDER:
            if k != key:
                o = _JOBS[k]
                o_score, o_band, o_effort = self._score(o)
                others.append(f"{o['id']} {o['name']}: risk {o_score} ({o_band}), {o_effort:.1f} crew-days, "
                              f"open item {o['open_review']}")
        factors = "\n".join(f"| {n} | {w} |" for n, w in j["factors"])
        stds = "\n".join(f"- {s} {_STANDARDS[s]['title']} ({_STANDARDS[s]['rev']})" for s in j["standards"])
        return (
            f"**Job Scope: {j['id']} {j['name']}**\n\n"
            f"| Risk factor | Weight |\n|---|---|\n{factors}\n| **Total risk score** | **{score} ({band})** |\n\n"
            f"| Effort | Value |\n|---|---|\n"
            f"| Work type | {j['work_type']} |\n"
            f"| Units | {j['units']} {j['unit_label']} |\n"
            f"| Estimate | {j['base_days']:g} base + {j['per_unit']:g} x {j['units']} = {effort:.1f} crew-days |\n\n"
            f"**Applicable standards:**\n{stds}\n\n"
            f"**Open item:** {j['open_review']} is still unvetted; resolve it before the design is issued.\n\n"
            f"**Also in the planning queue:** {'; '.join(others)}.\n\n"
            f"Risk bands: Low 0-4, Medium 5-8, High 9 or more. The estimate is a planning aid; the design engineer "
            f"confirms scope, crews and outages.\n\n"
            f"{_footer('Synthetic Work Snapshot + Standards Snapshot')}"
        )


if __name__ == "__main__":
    agent = EngineeringStandardsAgent()
    for op in _OPERATIONS:
        print("=" * 60)
        print(agent.perform(operation=op))
        print()
