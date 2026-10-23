"""
Briefing Pack Builder Agent

Builds draft government briefs (budget hearing brief, council question brief,
rapid response brief, executive brief, council decision memo) from a single
synthetic document library. Each draft cites the document behind every
statement, lists any measure whose value differs between documents for a
person to settle, and marks uncovered sections as needing input.

Where a real deployment would search an approved document library, this agent
uses a fixed synthetic content set so it runs anywhere without credentials. It
never approves, files, sends or publishes a brief: it returns drafts for the
responsible officers to check and route for sign-off.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))

from basic_agent import BasicAgent

# ═══════════════════════════════════════════════════════════════
# RAPP AGENT MANIFEST
# ═══════════════════════════════════════════════════════════════
__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/briefing-pack-builder",
    "version": "1.0.0",
    "display_name": "Briefing Pack Builder Agent",
    "description": "Turn a government team's source documents into cited, template-ready briefs in minutes, with conflicting figures flagged and missing content named, so specialists verify instead of rebuild.",
    "author": "AIBAST",
    "tags": ["government", "state-and-local", "briefing", "budget-hearing", "document-drafting"],
    "category": "slg_government",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}


# ═══════════════════════════════════════════════════════════════
# SYNTHETIC DATA LAYER (fixed content set, indexed 2026-04-06)
# ═══════════════════════════════════════════════════════════════

_ORG = "City of Contoso"
_TEAM = "Budget Office briefing team"
_INDEXED = "2026-04-06"

_TEMPLATES = {
    "budget_hearing": {
        "title": "Budget Hearing Brief", "audience": "Mayor and council members, for the annual budget hearing",
        "sections": ["Summary", "Key figures", "Budget status", "Cost change explanation",
                     "Staffing", "Talking points", "Likely questions", "Risks"],
        "route": ("Deputy City Manager", "City Manager", 8),
    },
    "council_question": {
        "title": "Council Question Brief", "audience": "Mayor, for a council question session",
        "sections": ["Likely question", "Proposed answer", "Facts to cite", "Follow-up lines"],
        "route": ("Department Director", "Mayor's Office", 2),
    },
    "rapid_response": {
        "title": "Rapid Response Brief", "audience": "Mayor and City Manager",
        "sections": ["Situation", "Where things stand", "Recent changes", "Public and press interest", "Suggested lines"],
        "route": ("City Manager", "Mayor's Office", 1),
    },
    "executive": {
        "title": "Executive Brief", "audience": "City Manager",
        "sections": ["Why this brief", "Context", "Progress", "Cost picture", "Recommended action"],
        "route": ("Deputy City Manager", "City Manager", 4),
    },
    "decision_memo": {
        "title": "Council Decision Memo", "audience": "City Council",
        "sections": ["Decision sought", "Context", "Issues to weigh", "Cost picture", "Recommended action", "Sign-off"],
        "route": ("City Manager", "City Council", 6),
    },
}

_TOPICS = {
    "elm_street_bridge": "Elm Street Bridge Replacement",
    "library_renovation": "Central Library Renovation",
}

_DOCS = {
    "DOC-01": "FY27 Adopted Capital Budget - Transportation",
    "DOC-02": "Elm Street Bridge Project Fact Sheet (January)",
    "DOC-03": "Quarterly Capital Status Report (Q2 FY27)",
    "DOC-04": "Public Works Staffing Workbook",
    "DOC-05": "Council Meeting Transcript (February 10)",
    "DOC-06": "Community Engagement Summary - Elm Street Bridge",
    "DOC-07": "Central Library Renovation Scope Note",
    "DOC-08": "Briefing Approval Route Guide",
}

# Passages: (doc, topic, section tags, text). Sections are tagged when the content set was indexed.
_PASSAGES = [
    ("DOC-01", "elm_street_bridge", ["Summary", "Context", "Why this brief", "Situation", "Decision sought"],
     "The Elm Street Bridge Replacement replaces the 1962 two-lane bridge with a four-lane structure and a shared path."),
    ("DOC-01", "elm_street_bridge", ["Key figures", "Budget status", "Cost picture", "Facts to cite"],
     "Approved budget $48.6 million; $19.2 million expended to date; completion forecast Q3 FY28."),
    ("DOC-02", "elm_street_bridge", ["Key figures", "Progress", "Where things stand"],
     "Approved budget $48.6 million. Foundations complete; deck works 40 percent complete."),
    ("DOC-03", "elm_street_bridge", ["Budget status", "Cost change explanation", "Recent changes", "Cost picture", "Issues to weigh", "Follow-up lines"],
     "Revised approved budget $51.3 million after change order CO-7; $21.7 million expended to date. The $2.7 million increase reflects steel price escalation and utility relocation."),
    ("DOC-03", "elm_street_bridge", ["Risks", "Issues to weigh", "Follow-up lines"],
     "Utility relocation is two months behind schedule; the Q3 FY28 completion date is at risk if it slips further."),
    ("DOC-04", "elm_street_bridge", ["Staffing"],
     "Project team establishment 16 FTE; 14 FTE filled after 2 engineer vacancies in December."),
    ("DOC-05", "elm_street_bridge", ["Likely questions", "Likely question"],
     "Council members asked how long the Elm Street detour will last and whether the project will exceed its budget."),
    ("DOC-06", "elm_street_bridge", ["Public and press interest", "Risks"],
     "312 public comments received; detour length was the top concern, raised in 141 comments."),
    ("DOC-07", "library_renovation", ["Summary", "Context", "Why this brief", "Situation", "Decision sought"],
     "The Central Library Renovation refurbishes the 1978 building and adds a children's learning floor."),
    ("DOC-07", "library_renovation", ["Key figures", "Budget status", "Cost picture", "Facts to cite"],
     "Approved budget $12.4 million; design phase complete; construction tender planned for July."),
]

# Measures cross-checked across documents for each topic.
_FIGURES = {
    "elm_street_bridge": [
        ("Approved budget", [("$48.6 million", ["DOC-01", "DOC-02"]), ("$51.3 million", ["DOC-03"])]),
        ("Expended to date", [("$19.2 million", ["DOC-01"]), ("$21.7 million", ["DOC-03"])]),
        ("Completion forecast", [("Q3 FY28", ["DOC-01", "DOC-03"])]),
    ],
    "library_renovation": [
        ("Approved budget", [("$12.4 million", ["DOC-07"])]),
    ],
}

_GATE = (
    "Synthetic content set only. This agent drafts; it does not approve, file, send or "
    "publish a brief. Responsible officers verify every figure and route the brief for sign-off."
)
_SOURCE = "Source: [Synthetic Briefing Content Set, indexed 2026-04-06]\nAgents: BriefingPackBuilderAgent"
_GAP_TEXT = "Not covered by the content set - input needed from the owning department."


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _resolve(value, options, default):
    if not value:
        return default
    q = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    for key in options:
        if key == q or key in q:
            return key
    return None


def _topic_passages(topic):
    return [p for p in _PASSAGES if p[1] == topic]


def _section_sources(topic, section):
    return [p for p in _topic_passages(topic) if section in p[2]]


def _conflicts(topic):
    return [(m, vals) for m, vals in _FIGURES[topic] if len(vals) > 1]


# ═══════════════════════════════════════════════════════════════
# AGENT CLASS
# ═══════════════════════════════════════════════════════════════

_OPERATIONS = [
    "list_templates", "content_scan", "figure_check",
    "draft_brief", "gap_report", "approval_route",
]


class BriefingPackBuilderAgent(BasicAgent):
    """
    Briefing pack builder.

    Operations:
        list_templates - available briefing formats, audiences and sections
        content_scan   - what the content set holds on a topic, by document
        figure_check   - measures that carry different values in different documents
        draft_brief    - cited draft of a template on a topic, gaps named, never approved
        gap_report     - sections of a template with no supporting content
        approval_route - reviewer, approver and turnaround for a template
    """

    def __init__(self):
        self.name = "BriefingPackBuilderAgent"
        self.metadata = {
            "name": self.name,
            "description": (
                "Briefing desk for the fictional City of Contoso Budget Office. Always use this tool to "
                "list briefing formats, scan the content set, check figures, draft a brief, find gaps and "
                "look up the approval route. Routing: 'what formats/templates' -> list_templates; 'what do "
                "we hold/have on <topic>' -> content_scan; 'do any figures disagree/conflict' -> "
                "figure_check; 'draft/prepare/build the <format> brief' -> draft_brief; 'which sections "
                "need input/are missing' -> gap_report; 'who signs off/how long' -> approval_route. Topics: "
                "elm_street_bridge (Elm Street Bridge Replacement, the default) and library_renovation "
                "(Central Library Renovation). Templates: budget_hearing (default), council_question, "
                "rapid_response, executive, decision_memo. Every operation has a demo default, so call it "
                "right away. Never approves, files, sends or publishes a brief."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": list(_OPERATIONS),
                        "description": (
                            "list_templates for formats; content_scan for what the content set holds; "
                            "figure_check for conflicting figures; draft_brief to draft; gap_report for "
                            "missing sections; approval_route for sign-off."
                        ),
                    },
                    "template": {
                        "type": "string",
                        "enum": list(_TEMPLATES),
                        "description": "Briefing format (default budget_hearing)",
                    },
                    "topic": {
                        "type": "string",
                        "enum": list(_TOPICS),
                        "description": "Brief topic (default elm_street_bridge)",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        op = kwargs.get("operation") or "list_templates"
        if op not in _OPERATIONS:
            return f"Unknown operation: {op}. Available: {', '.join(_OPERATIONS)}."
        template = _resolve(kwargs.get("template"), _TEMPLATES, "budget_hearing")
        if template is None:
            return (f"No briefing template named '{kwargs.get('template')}'. Templates: "
                    f"{', '.join(_TEMPLATES)}.\n\n{_GATE}\n\n{_SOURCE}")
        topic = _resolve(kwargs.get("topic"), _TOPICS, "elm_street_bridge")
        if topic is None:
            return (f"The content set holds nothing on '{kwargs.get('topic')}'. Topics: "
                    f"{', '.join(_TOPICS.values())}.\n\n{_GATE}\n\n{_SOURCE}")
        if op == "list_templates":
            return self._list_templates()
        if op == "content_scan":
            return self._content_scan(topic)
        if op == "figure_check":
            return self._figure_check(topic)
        if op == "draft_brief":
            return self._draft_brief(template, topic)
        if op == "gap_report":
            return self._gap_report(template, topic)
        return self._approval_route(template)

    # ── list_templates ────────────────────────────────────────
    def _list_templates(self):
        rows = "\n".join(
            f"| {key} | {t['title']} | {t['audience']} | {len(t['sections'])}: {', '.join(t['sections'])} |"
            for key, t in _TEMPLATES.items()
        )
        return (
            f"**Briefing Templates: {_ORG} {_TEAM}**\n\n"
            f"| Key | Format | Audience | Sections |\n|---|---|---|---|\n{rows}\n\n"
            f"Each format is a template entry, so adding a format needs no code change. "
            f"Content set: {len(_DOCS)} documents indexed {_INDEXED}.\n\n"
            f"**Next step:** name a topic and I will show what the content set holds on it.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── content_scan ──────────────────────────────────────────
    def _content_scan(self, topic):
        passages = _topic_passages(topic)
        counts = {}
        for p in passages:
            counts[p[0]] = counts.get(p[0], 0) + 1
        rows = "\n".join(f"| {d} | {_DOCS[d]} | {n} |" for d, n in counts.items())
        conflicts = len(_conflicts(topic))
        return (
            f"**Content Scan: {_TOPICS[topic]}**\n\n"
            f"Searched {len(_DOCS)} indexed documents ({len(_PASSAGES)} passages); {len(passages)} passages "
            f"on topic across {len(counts)} documents.\n\n"
            f"| Document | Title | Passages on topic |\n|---|---|---|\n{rows}\n\n"
            f"**Measures with conflicting values:** {conflicts}. Run a figure check before drafting.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── figure_check ──────────────────────────────────────────
    def _figure_check(self, topic):
        lines = []
        for measure, vals in _FIGURES[topic]:
            shown = "; ".join(f"{v} ({', '.join(d)})" for v, d in vals)
            status = "Conflict - confirm before use" if len(vals) > 1 else "Consistent"
            lines.append(f"| {measure} | {shown} | {status} |")
        n = len(_conflicts(topic))
        note = (
            "**Figures needing confirmation:** the content set carries two values for these measures. The later "
            "status report reflects change order CO-7, but the brief owner must confirm which is current; "
            "this agent does not choose between them."
            if n else "**No conflicting figures** for this topic in the content set."
        )
        return (
            f"**Figure Check: {_TOPICS[topic]}**\n\n"
            f"| Measure | Values found (documents) | Status |\n|---|---|---|\n" + "\n".join(lines) + "\n\n"
            f"{n} conflicting measures.\n\n{note}\n\n{_GATE}\n\n{_SOURCE}"
        )

    # ── draft_brief ───────────────────────────────────────────
    def _draft_brief(self, template, topic):
        t = _TEMPLATES[template]
        body, gaps, cited = [], [], []
        for section in t["sections"]:
            sources = _section_sources(topic, section)
            if not sources:
                gaps.append(section)
                body.append(f"### {section}\n{_GAP_TEXT}")
                continue
            text = " ".join(f"{p[3]} [{p[0]}]" for p in sources)
            for p in sources:
                if p[0] not in cited:
                    cited.append(p[0])
            body.append(f"### {section}\n{text}")
        conflicts = _conflicts(topic)
        confirm = ""
        if conflicts:
            confirm = "### Figures needing confirmation\n" + "\n".join(
                f"- {m}: " + " vs ".join(f"{v} ({', '.join(d)})" for v, d in vals) for m, vals in conflicts
            ) + "\n\n"
        reviewer, approver, days = t["route"]
        return (
            f"**{t['title']} - {_TOPICS[topic]}** (DRAFT - not approved)\n\n"
            f"Audience: {t['audience']}. Drafted from {len(_DOCS)} indexed documents "
            f"({len(_topic_passages(topic))} passages on topic).\n\n"
            + "\n\n".join(body) + "\n\n" + confirm +
            f"**Sources:** " + "; ".join(f"{d} {_DOCS[d]}" for d in cited) + "\n\n"
            f"**Gaps:** {len(gaps)} ({', '.join(gaps) if gaps else 'none'}).\n"
            f"**Approval route:** {reviewer} reviews, {approver} approves, {days} working days.\n\n"
            f"Status: Draft for officer review - not approved, filed or sent.\n\n{_GATE}\n\n{_SOURCE}"
        )

    # ── gap_report ────────────────────────────────────────────
    def _gap_report(self, template, topic):
        t = _TEMPLATES[template]
        rows, gaps = [], 0
        for section in t["sections"]:
            n = len(_section_sources(topic, section))
            if n == 0:
                gaps += 1
            rows.append(f"| {section} | {n} | {'Gap - needs input' if n == 0 else 'Covered'} |")
        owner = "Communications and the project director" if template == "budget_hearing" else "the owning department"
        return (
            f"**Gap Report: {t['title']} - {_TOPICS[topic]}**\n\n"
            f"| Section | Cited passages | Status |\n|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"**{gaps} of {len(t['sections'])} sections need input.** Gap sections are left as \"{_GAP_TEXT}\" "
            f"and are never filled from general knowledge.\n\n"
            f"**Next step:** request the missing content from {owner} before the brief goes for review.\n\n"
            f"{_GATE}\n\n{_SOURCE}"
        )

    # ── approval_route ────────────────────────────────────────
    def _approval_route(self, template):
        t = _TEMPLATES[template]
        reviewer, approver, days = t["route"]
        rows = "\n".join(
            f"| {x['title']} | {x['route'][0]} | {x['route'][1]} | {x['route'][2]} |" for x in _TEMPLATES.values()
        )
        return (
            f"**Approval Route: {t['title']}**\n\n"
            f"| Step | Owner |\n|---|---|\n"
            f"| 1. Draft and cite | {_TEAM} (this agent prepares the draft) |\n"
            f"| 2. Verify figures and fill gaps | Owning department |\n"
            f"| 3. Review | {reviewer} |\n"
            f"| 4. Approve | {approver} |\n\n"
            f"**Turnaround:** {days} working days from a complete draft.\n\n"
            f"| Format | Reviewer | Approver | Working days |\n|---|---|---|---|\n{rows}\n\n"
            f"Sign-off stays with people: the agent never marks a draft as approved, and the briefing "
            f"log stays the record of status. No brief was sent for approval.\n\n{_GATE}\n\n{_SOURCE}"
        )


if __name__ == "__main__":
    agent = BriefingPackBuilderAgent()
    story = [
        {"operation": "list_templates"},
        {"operation": "content_scan", "topic": "elm_street_bridge"},
        {"operation": "figure_check", "topic": "elm_street_bridge"},
        {"operation": "draft_brief", "template": "budget_hearing", "topic": "elm_street_bridge"},
        {"operation": "gap_report", "template": "budget_hearing", "topic": "elm_street_bridge"},
        {"operation": "approval_route", "template": "budget_hearing"},
    ]
    for kw in story:
        print("=" * 60)
        print(agent.perform(**kw))
        print()
