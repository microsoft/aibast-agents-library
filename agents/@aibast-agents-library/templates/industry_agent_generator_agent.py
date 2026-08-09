"""
Industry Agent Generator — AIBAST Agents Library

Generates a complete, constitution-compliant industry solution agent from a
one-pager brief, in one shot.

Every rule in AGENT_CONSTITUTION.md was written from a real failure: 27 agents
that could never load because self.name held the package slug, 9 with no
parameters schema so only their default operation was reachable, 66 whose tool
description was marketing copy the model could not route on, and a whole family
whose dates were pinned to a year that had already passed. Writing those rules
down does not stop the next author repeating them; generating the file does.

Operations:
    constitution   the standard an agent must meet (default; needs no arguments)
    brief_template the JSON a caller fills in, with a worked example
    scaffold       emit a complete agent.py from a brief
    demo_cases     emit the locked tests/demo_cases/<slug>.json for that brief
    audit          check an existing agent file against the mechanical articles

The generated agent carries a static synthetic data plane shaped to the real
source system named in the brief, so it delivers the full value of the solution
with no endpoint, no credentials and no network.
"""

import json
import os
import re
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from basic_agent import BasicAgent

__manifest__ = {
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/industry-agent-generator",
    "version": "1.0.0",
    "display_name": "Industry Agent Generator",
    "description": "Generates a complete, constitution-compliant AIBAST industry solution agent from a one-pager brief, with its locked demo cases.",
    "author": "AIBAST",
    "tags": ["meta", "generator", "scaffolding", "constitution", "agent-authoring"],
    "category": "general",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}

TODAY = date.today()

TOOL_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

CONSTITUTION = [
    ("I.2", "Every advertised capability bullet gets exactly one operation, named after what the bullet does."),
    ("I.3", "display_name and description are the one-pager's title and executive summary, verbatim."),
    ("II.1", "self.name is the TOOL name and must match ^[A-Za-z0-9_-]{1,64}$. The package slug stays in __manifest__['name']."),
    ("II.2", "The filename ends in _agent.py or the Brainstem never discovers it."),
    ("II.4", "perform(**kwargs) -> str returns Markdown."),
    ("III.1", "A parameters schema is mandatory, or only the default operation is reachable from chat."),
    ("III.2", "The tool description is routing prose naming the surfaces users ask about in their own words — not the marketing summary."),
    ("III.3", "Each operation carries a description mapping business phrasing to it."),
    ("III.4", "The default operation needs no identifiers: it is the roll-up that answers 'what do I look at today'."),
    ("IV.1", "Static synthetic data shaped to the real source system. No network, no credentials."),
    ("IV.3", "Dates are computed from the run date via a _d(offset) helper."),
    ("IV.4", "Real computation — derived scores, subtracted ages, compared thresholds. Never canned strings."),
    ("IV.5", "The data contains the problem the one-pager describes, or the demo has nothing to find."),
    ("V.1", "Name the entity. Every roll-up row cites its worst offender by identifier."),
    ("VI.1", "Locked demo cases, one per advertised bullet, phrased the way the persona talks."),
    ("VI.3", "Assert on entities the agent computed, never on the model's phrasing."),
]

BRIEF_EXAMPLE = {
    "solution": "Grid Outage Response Agent",
    "slug": "grid-outage-response",
    "class_name": "GridOutageResponseAgent",
    "category": "energy",
    "industry": "Energy and Utilities",
    "executive_summary": "Coordinate outage detection, crew dispatch and customer communication to restore power faster and protect regulatory performance.",
    "personas": ["Control Room Operator", "Field Dispatch Supervisor", "Regulatory Reporting Manager"],
    "featured_tools": ["Dynamics 365 Field Service", "Azure IoT Hub", "Microsoft Teams"],
    "source_systems": "Outage Management System (OMS), SCADA, and the regulator's reliability filing",
    "customer_scenario": [
        "Storm outages were detected by customer calls before SCADA",
        "Crews were dispatched without knowing which circuits carried critical care customers",
    ],
    "capabilities": [
        {"bullet": "Detect and rank active outages by customer impact",
         "operation": "outage_overview",
         "routing_words": "what is out, how many customers are off supply, worst outage"},
    ],
    "entity": {
        "record_name": "outage",
        "id_prefix": "OTG",
        "fields": ["circuit", "customers_affected", "cause", "status"],
    },
}


def _d(offset_days):
    return (TODAY + timedelta(days=offset_days)).isoformat()


def _render_value(v):
    """Render a brief value as source. {"_d": -3} becomes a run-relative date."""
    if isinstance(v, dict) and "_d" in v:
        return f'_d({int(v["_d"])})'
    if isinstance(v, dict) and "_h" in v:
        return f'_h({int(v["_h"])})'
    return json.dumps(v)


def _slug_to_class(slug):
    return "".join(p.capitalize() for p in re.split(r"[-_\s]+", slug) if p) + "Agent"


def _op_from_bullet(bullet):
    """Derive a snake_case operation name from a capability bullet."""
    words = re.findall(r"[a-z]+", bullet.lower())
    stop = {"and", "the", "a", "an", "to", "for", "of", "with", "all", "their",
            "in", "on", "by", "from", "into", "that", "this", "at", "or"}
    keep = [w for w in words if w not in stop][:3]
    return "_".join(keep) or "review"


class IndustryAgentGeneratorAgent(BasicAgent):
    """Generates constitution-compliant industry solution agents."""

    def __init__(self):
        self.name = "IndustryAgentGenerator"
        self.metadata = {
            "name": self.name,
            "display_name": "Industry Agent Generator",
            # Article III.2 applies to this agent too: route on how an author
            # actually asks, not on the marketing line.
            "description": (
                "Authors new AIBAST industry solution agents. Use this for any request to "
                "create, generate, scaffold, write or stand up a new industry agent or "
                "solution; to see the AIBAST agent constitution or the standard an agent must "
                "meet; to get the brief format for a new solution; to produce the locked demo "
                "test cases for a solution; or to audit an existing agent file for whether it "
                "would load, whether the model can route to it, and whether it meets the "
                "library standard."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": (
                            "constitution: the standard an agent must meet. "
                            "brief_template: the JSON a caller fills in, with a worked example. "
                            "scaffold: emit a complete agent.py from a brief — use for 'build me "
                            "an agent for X'. "
                            "one_pager: emit the advertised listing — the SharePoint one-pager "
                            "narrative and the solutions.json entry that puts it on the catalog "
                            "and solution pages. "
                            "demo_cases: emit the locked demo case file for a brief. "
                            "audit: check an existing agent file against the mechanical articles."
                        ),
                        "enum": ["constitution", "brief_template", "scaffold",
                                 "one_pager", "demo_cases", "audit"],
                    },
                    "brief": {
                        "type": "string",
                        "description": "JSON brief for the solution. See brief_template.",
                    },
                    "agent_path": {
                        "type": "string",
                        "description": "Path to an existing agent file, for audit.",
                    },
                },
                "required": ["operation"],
            },
        }
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "constitution")
        dispatch = {
            "constitution": self._constitution,
            "one_pager": self._one_pager,
            "brief_template": self._brief_template,
            "scaffold": self._scaffold,
            "demo_cases": self._demo_cases,
            "audit": self._audit,
        }
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{operation}`. Available: {', '.join(dispatch)}."
        return handler(**kwargs)

    # ------------------------------------------------------------------ ops
    def _constitution(self, **kwargs) -> str:
        L = ["# AIBAST Agent Constitution — what an agent must be\n",
             "Each rule exists because it was broken in production and cost a demo.\n",
             "| Article | Rule |", "|---|---|"]
        for art, rule in CONSTITUTION:
            L.append(f"| **{art}** | {rule} |")
        L.append("\n## Verify\n")
        L.append("```\npython tools/validate_agent.py <agent.py>   # mechanical, articles II-V")
        L.append("python tools/run_demo_cases.py <slug>       # live, article VI\n```")
        L.append("\nFull text: `agents/@aibast-agents-library/AGENT_CONSTITUTION.md`.")
        return "\n".join(L)

    def _one_pager(self, **kwargs) -> str:
        """The advertised listing, in the shape the AIBAST SharePoint publishes.

        A solution is not in the library because code exists; it is in the
        library because it was advertised (Article I.1). This emits the same
        structure every published one-pager uses — executive summary, the
        customer situation, what the agent did, the outcomes, and the
        Industries / Personas / Agent requirements / Featured tools row — plus
        the solutions.json entry that renders it on library.html and
        solution.html alongside the advertised set.
        """
        brief, err = self._parse_brief(kwargs)
        if err:
            return err
        caps = brief["capabilities"]
        for c in caps:
            c.setdefault("operation", _op_from_bullet(c["bullet"]))
        scenario = brief.get("customer_scenario", [])
        outcomes = brief.get("outcomes", [])
        actor = brief.get("actor", "the organisation")

        L = [f"# {brief['solution']} — one-pager\n",
             f"*{brief['executive_summary']}*\n"]
        if scenario:
            L.append(f"**{actor.capitalize()} faced:**\n")
            for x in scenario:
                L.append(f"- {x}")
            L.append("")
        if outcomes:
            L.append(f"**With the agent, {actor}:**\n")
            for x in outcomes:
                L.append(f"- {x}")
            L.append("")
        L.append(f"**{actor.capitalize()} used the {brief['solution']} to:**\n")
        for c in caps:
            L.append(f"- {c['bullet']}")
        L.append("")
        L.append("| Industries | Personas | Agent requirements | Featured tools |")
        L.append("|---|---|---|---|")
        L.append(f"| {brief.get('industry', '')} | {'<br>'.join(brief.get('personas', []))} "
                 f"| {brief.get('agent_requirements', 'Microsoft Copilot Studio')} "
                 f"| {'<br>'.join(brief.get('featured_tools', []))} |")

        entry = {
            "slot": brief.get("slot"),
            "advertised_name": brief["solution"],
            "advertised_display": brief["solution"],
            "sharepoint_list_name": brief.get("sharepoint_list_name", brief["solution"]),
            "canonical_name": brief["solution"],
            "repo_agent": f"@aibast-agents-library/{brief['slug']}",
            "executive_summary": brief["executive_summary"],
            "industries": [brief.get("industry")] if brief.get("industry") else [],
            "personas": brief.get("personas", []),
            "featured_tools": brief.get("featured_tools", []),
            "customer_scenario": scenario,
            "outcomes": outcomes,
            "capabilities": [c["bullet"] for c in caps],
            "capability_map": [{"advertised": c["bullet"], "operation": c["operation"]}
                               for c in caps],
            "is_primary": True,
            "source": brief.get("source", "GENERATED — not yet advertised on the AIBAST "
                                          "SharePoint. Article I.1: it ships only once it is."),
        }
        L.append("\n## solutions.json entry\n")
        L.append("Append to `solutions.json` so it renders on the catalog and its own "
                 "solution page:\n")
        L.append("```json\n" + json.dumps(entry, indent=1) + "\n```")
        L.append("\n> Article I.1: generating a listing does not make a solution advertised. "
                 "Until it exists on the SharePoint, this ships as a draft.")
        return "\n".join(L)

    def _brief_template(self, **kwargs) -> str:
        return ("# Brief format\n\nFill this in from the published one-pager and pass it as "
                "`brief`:\n\n```json\n" + json.dumps(BRIEF_EXAMPLE, indent=2) + "\n```\n\n"
                "`capabilities` is the one-pager's \"the company used the X Agent to:\" list. "
                "Each entry becomes exactly one operation (Article I.2). `routing_words` are "
                "the phrases the persona would actually type — they go into the tool "
                "description so the model can find the agent (Article III.2).")

    def _parse_brief(self, kwargs):
        raw = kwargs.get("brief")
        if not raw:
            return None, "**Error:** no `brief` supplied. Run `brief_template` for the format."
        if isinstance(raw, dict):
            return raw, None
        try:
            return json.loads(raw), None
        except json.JSONDecodeError as e:
            return None, f"**Error:** brief is not valid JSON — {e}"

    def _scaffold(self, **kwargs) -> str:
        brief, err = self._parse_brief(kwargs)
        if err:
            return err
        missing = [f for f in ("solution", "slug", "category", "industry",
                               "executive_summary", "capabilities")
                   if not brief.get(f)]
        if missing:
            return f"**Error:** brief missing required field(s): {', '.join(missing)}."

        cls = brief.get("class_name") or _slug_to_class(brief["slug"])
        if not TOOL_NAME_RE.match(cls):
            return f"**Error:** class name {cls!r} is not a legal tool name (Article II.1)."

        caps = brief["capabilities"]
        for c in caps:
            c.setdefault("operation", _op_from_bullet(c["bullet"]))
        default_op = caps[0]["operation"]

        src = _render_agent(brief, cls, caps, default_op)
        return (f"# Generated: {brief['solution']}\n\n"
                f"- {len(caps)} operation(s), one per advertised capability bullet (Article I.2)\n"
                f"- tool name `{cls}` — legal, so it will load (Article II.1)\n"
                f"- default operation `{default_op}` needs no identifiers (Article III.4)\n"
                f"- dates computed from the run date (Article IV.3)\n\n"
                f"Write to `agents/@aibast-agents-library/{brief['category']}_stacks/"
                f"{brief['slug'].replace('-', '_')}_stack/"
                f"{brief['slug'].replace('-', '_')}_agent.py`:\n\n"
                f"```python\n{src}\n```")

    def _demo_cases(self, **kwargs) -> str:
        brief, err = self._parse_brief(kwargs)
        if err:
            return err
        caps = brief["capabilities"]
        for c in caps:
            c.setdefault("operation", _op_from_bullet(c["bullet"]))
        personas = brief.get("personas") or ["Operator"]
        prefix = "".join(w[0] for w in brief["solution"].split()[:3]).upper()
        doc = {
            "solution": brief["solution"],
            "agent": f"@aibast-agents-library/{brief['slug']}",
            "agent_files": [brief["slug"].replace("-", "_") + "_agent"],
            "note": ("Locked demo cases, one per advertised capability bullet. Phrased the way "
                     "the persona talks - no operation names, no record ids."),
            "assertion_principle": ("must_include names entities the agent computed. "
                                    "must_not_include names stall phrases proving the agent was "
                                    "never called. Never assert on the model's phrasing."),
            "cases": [
                {
                    "id": f"{prefix}-{i+1:02d}",
                    "persona": personas[i % len(personas)],
                    "onepager_bullet": c["bullet"],
                    "prompt": c.get("demo_prompt", f"TODO: how would a {personas[i % len(personas)]} "
                                                   f"ask for this in their own words?"),
                    "must_include": [f"TODO: an identifier the agent computes, e.g. "
                                     f"{brief.get('entity', {}).get('id_prefix', 'ID')}-0001"],
                    "must_not_include": ["I don't have access", "give me a", "provide the"],
                    "min_words": 25,
                }
                for i, c in enumerate(caps)
            ],
        }
        return ("# Locked demo cases\n\nWrite to `tests/demo_cases/"
                f"{brief['slug']}.json`, then replace each TODO with the phrasing the persona "
                "would really use and an identifier your data actually contains:\n\n```json\n"
                + json.dumps(doc, indent=1) + "\n```")

    def _audit(self, **kwargs) -> str:
        path = kwargs.get("agent_path")
        if not path:
            return "**Error:** no `agent_path` supplied."
        if not os.path.exists(path):
            return f"**Error:** no file at `{path}`."
        src = open(path, encoding="utf-8").read()
        findings = []

        m = re.search(r"self\.name\s*=\s*['\"]([^'\"]+)['\"]", src)
        if not m:
            findings.append(("II.1", "self.name is not a literal"))
        elif not TOOL_NAME_RE.match(m.group(1)):
            findings.append(("II.1", f"self.name {m.group(1)!r} is not a legal tool name — "
                                     f"this agent CANNOT be loaded by the Brainstem"))
        if not path.endswith("_agent.py"):
            findings.append(("II.2", "filename does not end in _agent.py — never discovered"))
        if '"parameters"' not in src:
            findings.append(("III.1", "no parameters schema — only the default operation is "
                                      "reachable from chat"))
        if '"description": __manifest__["description"]' in src:
            findings.append(("III.2", "tool description is the advertised marketing summary; "
                                      "the model routes on this string"))
        if "date.today()" not in src and "datetime.now()" not in src:
            findings.append(("IV.3", "no run-date anchor — check for dates that will go stale"))
        if re.search(r"requests\.|urllib\.request", src):
            findings.append(("IV.1", "makes network calls — the data plane must be offline"))
        if "__manifest__" not in src:
            findings.append(("I.3", "no __manifest__"))

        L = [f"# Constitution audit — `{os.path.basename(path)}`\n"]
        if not findings:
            L.append("**Passes every mechanical article.** Article I (implements an advertised "
                     "one-pager) and Article VI (locked cases green) still need a human and a "
                     "live Brainstem.")
            return "\n".join(L)
        L.append(f"**{len(findings)} violation(s).**\n")
        L.append("| Article | Finding |")
        L.append("|---|---|")
        for art, f in findings:
            L.append(f"| **{art}** | {f} |")
        return "\n".join(L)


# --------------------------------------------------------------------- render

def _render_agent(brief, cls, caps, default_op):
    """Emit the agent source. Everything the constitution can enforce, it enforces."""
    slug = brief["slug"]
    module = slug.replace("-", "_")
    entity = brief.get("entity", {}) or {}
    idp = entity.get("id_prefix", "REC")
    record = entity.get("record_name", "record")
    fields = entity.get("fields", ["owner", "status"])
    personas = ", ".join(brief.get("personas", []))
    tools = ", ".join(brief.get("featured_tools", []))
    routing = "; ".join(c.get("routing_words", "") for c in caps if c.get("routing_words"))
    closed_statuses = [str(x).lower() for x in (entity.get("closed_statuses") or [])]
    rank = brief.get("ranking") or {}
    ranking_expr = rank.get("expression",
                            'min(100, max(0, _days_over(r)) * 6 + r["severity"] * 10)')
    ranking_doc = rank.get("doc", "0-100 priority. Rises with time past target and severity.")
    routing_examples = "; ".join(
        f"'{c['routing_words']}'" for c in caps
        if c.get("routing_words")) or brief["executive_summary"][:120]

    supplied = entity.get("records")
    records = []
    if supplied:
        # Real domain rows from the brief. Emitted verbatim so the data plane
        # carries the shape of the actual source system (Article IV.1) and the
        # problem the one-pager describes (Article IV.5).
        for rid, rec in supplied.items():
            body = ",\n        ".join(
                f'"{k}": {_render_value(v)}' for k, v in rec.items())
            records.append(f'    "{rid}": {{\n        {body},\n    }},')
    else:
        for i in range(1, 6):
            vals = ",\n        ".join(f'"{f}": "TODO real {f}"' for f in fields)
            records.append(
                f'    "{idp}-{1000+i}": {{\n'
                f'        {vals},\n'
                f'        "opened": _d(-{i * 7}),\n'
                f'        "severity": {[3, 1, 5, 2, 4][i-1]},\n'
                f'        "target_days": {[5, 10, 5, 15, 10][i-1]},\n'
                f'    }},')
    records_block = "\n".join(records)

    op_methods = []
    for i, c in enumerate(caps):
        op = c["operation"]
        bullet = c["bullet"].replace('"', "'")
        if i == 0:
            body = f'''
    def _{op}(self, **kwargs) -> str:
        """{bullet}

        Article III.4: the default view takes no identifiers — it answers
        "what do I look at today".
        """
        rows = sorted(_records().items(), key=lambda kv: -_pressure(kv[1]))
        breached = [r for r in rows if _days_over(r[1]) > 0]
        L = [f"# {brief['solution']} — {{TODAY.isoformat()}}\\n"]
        L.append(f"**{{len(rows)}} open {record}(s) · {{len(breached)}} past target**\\n")
        L.append("| {idp} | " + " | ".join({fields!r}) + " | Age | Target | State | Pressure |")
        L.append("|" + "---|" * ({len(fields)} + 6))
        for rid, r in rows:
            over = _days_over(r)
            state = "BREACHED" if over > 0 else ("AT RISK" if over > -3 else "ON TRACK")
            L.append(f"| {{rid}} | " + " | ".join(str(r[f]) for f in {fields!r})
                     + f" | {{_age(r)}}d | {{r['target_days']}}d | {{state}}"
                     + (f" (+{{over}}d)" if over > 0 else "")
                     + f" | {{_pressure(r)}}/100 |")
        if rows:
            rid, top = rows[0]
            # Article V.1: name the worst offender, or a summarising answer
            # loses the only thing a customer can act on.
            L.append(f"\\n## Act on this first\\n")
            L.append(f"**{{rid}}** — {{_describe(top)}} · {{_age(top)}} days open against a "
                     f"{{top['target_days']}}-day target, pressure {{_pressure(top)}}/100.")
        return "\\n".join(L)
'''
        else:
            body = f'''
    def _{op}(self, **kwargs) -> str:
        """{bullet}"""
        rid = (kwargs.get("record_id") or "").upper()
        data = _records()
        rows = ([(rid, data[rid])] if rid in data
                else sorted(data.items(), key=lambda kv: -_pressure(kv[1]))[:3])
        if not rows:
            return "No {record}s match."
        L = ["# {bullet}\\n"]
        for rid, r in rows:
            L.append(f"## {{rid}} — {{_describe(r)}}\\n")
            L.append(f"- Open {{_age(r)}} days against a {{r['target_days']}}-day target "
                     f"({{'BREACHED by ' + str(_days_over(r)) + 'd' if _days_over(r) > 0 else 'within target'}})")
            L.append(f"- Pressure score {{_pressure(r)}}/100 "
                     f"(severity {{r['severity']}}/5, {{max(0, _days_over(r))}} days over)")
            L.append(f"- Recommended: {{_next_action(r)}}")
            L.append("")
        return "\\n".join(L)
'''
        op_methods.append(body)

    enum_lines = ",\n                            ".join(f'"{c["operation"]}"' for c in caps)
    op_desc = " ".join(f'{c["operation"]}: {c["bullet"]}'
                       + (f' — ask about {c["routing_words"]}.' if c.get("routing_words") else ".")
                       for c in caps)

    return f'''"""
{brief["solution"]} — {brief["industry"]}

Implements the published AIBAST one-pager "{brief["solution"]}" end to end. Each
advertised capability bullet is one operation (Article I.2):

{chr(10).join(f"  {c['operation']:<24} {c['bullet']}" for c in caps)}

Personas: {personas}
Featured tools: {tools}

Where a real deployment would connect to {brief.get("source_systems", "the systems of record")},
this agent uses a static synthetic data layer shaped to those sources, so it runs
with no endpoint and no credentials. Dates are computed from the run date, so a
demo never goes stale.

Generated by the Industry Agent Generator against AGENT_CONSTITUTION.md.
"""

import os
import sys
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "templates"))
from basic_agent import BasicAgent

__manifest__ = {{
    "schema": "rapp-agent/1.0",
    "name": "@aibast-agents-library/{slug}",
    "version": "1.0.0",
    "display_name": "{brief["solution"]}",
    "description": "{brief["executive_summary"]}",
    "author": "AIBAST",
    "tags": {json.dumps(brief.get("tags", [brief["category"], "industry-solution"]))},
    "category": "{brief["category"]}",
    "quality_tier": "verified",
    "requires_env": [],
    "dependencies": ["@rapp/basic-agent"],
}}

TODAY = date.today()
NOW = datetime.now()


def _d(offset_days):
    """Article IV.3: every date is relative to the run date."""
    return (TODAY + timedelta(days=offset_days)).isoformat()


def _h(offset_hours):
    """Run-relative timestamp for events measured in hours, not days."""
    return (NOW + timedelta(hours=offset_hours)).strftime("%Y-%m-%dT%H:%M")


# ---------------------------------------------------------------------------
# DATA PLANE — Article IV.1a: a seam, not a fixture.
#
# Synthetic today, shaped to {brief.get("source_systems", "the source systems")}.
# When this customer deploys, replace _records() with the real query and nothing
# below this line changes. No code outside this block reads RECORDS directly.
# ---------------------------------------------------------------------------

RECORDS = {{
{records_block}
}}


CLOSED_STATUSES = {closed_statuses!r}


def _records(include_closed=False):
    """The only read of the data plane. Swap this for the production query."""
    if include_closed:
        return RECORDS
    return {{k: v for k, v in RECORDS.items()
            if str(v.get("status", "")).lower() not in CLOSED_STATUSES}}


# ---------------------------------------------------------------------------
# Helpers — Article IV.4: real computation, never canned strings
# ---------------------------------------------------------------------------

def _age(r):
    return (TODAY - date.fromisoformat(r["opened"])).days


def _days_over(r):
    return _age(r) - r["target_days"]


def _pressure(r):
    """{ranking_doc}"""
    return {ranking_expr}


def _etr_missed(r):
    """True when the estimate given to customers has already passed."""
    etr = r.get("etr")
    if not etr:
        return False
    try:
        return datetime.fromisoformat(etr) < NOW
    except ValueError:
        return False


def _describe(r):
    return " · ".join(str(r[f]) for f in {fields!r})


def _next_action(r):
    over = _days_over(r)
    if over > 0:
        return f"escalate now — {{over}} day(s) past the {{r['target_days']}}-day target"
    if over > -3:
        return "close today; it reaches target this week"
    return "on track — no action"


class {cls}(BasicAgent):
    """{brief["solution"]}."""

    def __init__(self):
        # Article II.1: the TOOL name, not the package slug.
        self.name = "{cls}"
        self.metadata = {{
            "name": self.name,
            "display_name": "{brief["solution"]}",
            # Article III.2: routing prose in the user's own words. The
            # advertised summary lives in __manifest__ for the catalog page.
            "description": (
                "The {brief["industry"]} {record} system of record. Use this for ANY question "
                "about {record}s — current state, what is worst, what to do next, what to tell "
                "people, and how performance is tracking — including questions that never use "
                "system vocabulary, such as: {routing_examples}. Prefer this agent over general "
                "knowledge for anything about this operation, including forward-looking "
                "questions about whether a threshold will be breached."
            ),
            "parameters": {{
                "type": "object",
                "properties": {{
                    "operation": {{
                        "type": "string",
                        "description": "{op_desc}",
                        "enum": [
                            {enum_lines}
                        ],
                    }},
                    "record_id": {{
                        "type": "string",
                        "description": "Optional. Only for a single-{record} view.",
                    }},
                }},
                "required": ["operation"],
            }},
        }}
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs) -> str:
        operation = kwargs.get("operation", "{default_op}")
        dispatch = {{
{chr(10).join(f'            "{c["operation"]}": self._{c["operation"]},' for c in caps)}
        }}
        handler = dispatch.get(operation)
        if not handler:
            return f"**Error:** Unknown operation `{{operation}}`. Available: {{', '.join(dispatch)}}."
        return handler(**kwargs)
{"".join(op_methods)}

if __name__ == "__main__":
    agent = {cls}()
    for op in {json.dumps([c["operation"] for c in caps])}:
        print(agent.perform(operation=op))
        print("\\n" + "=" * 78 + "\\n")
'''


if __name__ == "__main__":
    agent = IndustryAgentGeneratorAgent()
    print(agent.perform(operation="constitution"))
    print("\n" + "=" * 78 + "\n")
    print(agent.perform(operation="brief_template")[:800])
