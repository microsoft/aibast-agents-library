# AIBAST Agent Constitution

What an agent must be to belong in this library.

Every rule below was written from a failure we actually hit — an agent that was
advertised with a one-pager and a demo video but could not load, could not be
routed to, or could not do what the slide promised. The rules are ordered by how
badly breaking them hurts in front of a customer.

---

## Article I — The one-pager is the specification

**I.1 — An agent exists because a solution was advertised.** The AIBAST
SharePoint "Agents Library" is the approved catalog. If a solution is not
advertised there, it does not belong in the public repo. The repo aligns to
SharePoint; SharePoint never aligns to the repo.

**I.2 — Every advertised capability bullet gets one operation.** The one-pager's
"the company used the X Agent to:" list is the operation list. Four bullets, four
operations, mapped one to one and named after what the bullet does. A bullet with
no operation is a lie told to a customer who watched the demo video.

**I.3 — The advertised name and executive summary are copied verbatim.**
`__manifest__["display_name"]` is the one-pager's title. `__manifest__["description"]`
is its executive summary, word for word. The field was sold those words.

**I.4 — The scenario is honoured.** The one-pager names an industry, a customer
situation and a set of personas. The synthetic data must be that industry and
that situation. A one-pager about an investment firm's trading desk is not
satisfied by a bank compliance programme, however good the code is.

---

## Article II — It must actually load

**II.1 — `self.name` is the tool name, not the package name.** It must match
`^[a-zA-Z0-9_-]{1,64}$`. The package slug (`@aibast-agents-library/claims-processing`)
contains `@` and `/` and is rejected by function calling, so the Brainstem
discovers the file, finds nothing usable, and registers silently nothing. Use the
class name. The slug lives in `__manifest__["name"]` and stays there.

**II.2 — The file is discovered as `agents/*_agent.py`.** A file that does not end
in `_agent.py` is never loaded, no matter how good it is.

**II.3 — It subclasses `BasicAgent` and constructs with no arguments.**

**II.4 — `perform(**kwargs) -> str` returns Markdown.** Never a dict, never None.

---

## Article III — It must be reachable in conversation

**III.0 — The description and the parameters are the entire contract.** They are
the only thing the Brainstem sees about this agent: what it does, when to reach
for it, and what the caller must supply. There is no README in the model's
context, no examples, no memory of how the agent was built. If the model picks
the wrong tool, omits a required argument, or asks the user for something it
could have inferred, the contract is at fault — not the model, and not luck.
Fix the description or the parameter descriptions; never paper over it with
retries.

**III.1 — A `parameters` schema is mandatory.** Without one, `BasicAgent.to_tool()`
falls back to `{"type": "object", "properties": {}}` and the model can only ever
call the default operation. Every other operation — the payoff screens in the
demo video — becomes unreachable from chat.

**III.2 — The tool description is written for routing, not for marketing.**
`__manifest__["description"]` is the advertised summary and belongs on the catalog
page. `self.metadata["description"]` is what the model reads when choosing a tool,
so it must name the surfaces people ask about **in their own words**: "front
counter", "the board", "status calls", "the solar job", "about to go live".
A permitting agent described only as "automates building permit review processes"
will not be selected by someone who types "anything I shouldn't be accepting today".

**III.3 — Each operation carries its own description.** The `operation` enum needs
prose mapping business phrasing to operations, or "is anything about to go live"
routes to staffing instead of algorithm sign-off.

**III.4 — The default operation needs no identifiers.** A business user does not
know a claim ID. The default must be the portfolio, backlog or roll-up view that
answers "what should I look at today". Single-record views take an optional id.

---

## Article IV — The data plane

**IV.1 — Static synthetic data, shaped to the real source.** No live endpoint, no
credentials, no network. The shape must be what the real system would hand over:
real field numbers, real identifier formats, real status codes, real regulatory
vocabulary. The Regulatory Compliance Agent carries MiFIR RTS 22 Annex I field
numbers, ISO 17442 LEIs, FIRDS venue admission and genuine ARM rejection codes —
so a compliance officer can reconcile its output against a real response file.

**IV.1a — The data plane is a seam, not a fixture.** These agents are templates.
The synthetic block exists to be *replaced* by the customer's real system —
Dynamics 365, ServiceNow, an OMS, an ARM — once they deploy. So it must sit
behind one clearly marked boundary with named accessors, never scattered through
the logic:

```python
# ---- DATA PLANE ---------------------------------------------------------
# Synthetic today; swap this block for the customer's system of record.
# Nothing below this line reads the constants directly — it calls _records().
RECORDS = {...}

def _records():
    """Replace with the real query. Everything downstream is unchanged."""
    return RECORDS
```

Going live must be a change to the accessor, not a rewrite of the agent. The
connector templates under `templates/` (Salesforce, ServiceNow, SharePoint,
PowerPoint) are the production end of that seam: they legitimately make network
calls and are exempt from IV.1, because they *are* the thing the seam is
eventually wired to. Article IV governs industry solution agents under
`*_stacks/`, not connector templates.

**IV.1b — Scoring must be the domain's, not a generic age score.** An outage
ranks by customers off supply and critical-care load; a claim ranks by exposure
and fraud signal; a permit ranks by statutory clock. A generic "days overdue"
ranking is a scaffold that was never finished.

**IV.2 — Never a real customer, never real personal data.** Correctly formatted
but synthetic identifiers. Fictional companies. No customer names, no employee
names, no internal identifiers.

**IV.3 — Dates are computed from the run date.** Anchor with a `_d(offset)` helper.
A pinned date means the demo shows an eighteen-month-old backlog the first time
someone opens it next year.

**IV.4 — Real computation, not canned strings.** Scores are derived, ages are
subtracted, thresholds are compared. An agent that returns a fixed paragraph is a
mock, and a customer will ask it a second question.

**IV.5 — The data must contain the problem the one-pager describes.** If the slide
says duplicate applications caused rework, there is a duplicate in the data. The
demo has nothing to find otherwise.

---

## Article V — The output

**V.1 — Name the entity.** "Two traders are lapsed" is worthless; "T-2041 (EU
Equities) and T-2233 (Credit)" is the demo. Every roll-up row cites its worst
offender by identifier, because the model summarises and the identifier is what
survives.

**V.2 — Lead with the decision.** The first lines answer "what do I do now",
before any table.

**V.3 — One screen.** Markdown tables and short bullets. An answer that scrolls
off the screen loses the room.

**V.4 — State the synthetic data plane in the module docstring**, so nobody who
was shown "real-time surveillance" is surprised by a dict.

---

## Article VI — It is not done until it is proven

**VI.1 — Locked demo cases, one per advertised bullet.** Stored in
`tests/demo_cases/<slug>.json`. Each case names the persona and the bullet it
proves.

**VI.2 — Cases are written the way the persona talks.** No operation names, no
record ids, no jargon a Permit Technician would not use. If the case has to name
the operation to pass, the agent is not reachable and Article III has failed.

**VI.3 — Assert on entities, never on phrasing.** `must_include` holds identifiers
and figures the agent computed. The model's prose varies between runs; asserting
on "RTS 22" or "reporting" makes a good answer flake red. `must_not_include` holds
the stall phrases that prove the agent was never called — "I don't have access",
"give me an id".

**VI.4 — Verified live, one solution at a time.** `python tools/run_demo_cases.py <slug>`
hot-loads only that solution's agents, replays the cases against a running
Brainstem, and unloads. Loading the whole catalog at once makes tool selection
noisy and the model picks nothing — that is a harness failure that will make a
good agent look broken.

**VI.5 — "Done" means the cases are green against a live Brainstem**, not that the
file imports.

---

## Article VII — Boundaries

**VII.1 — Work content stays in the work repo.** Customer names, internal
transcripts and tenant data never enter an agent file.

**VII.2 — Auth-gated links are never committed.** SharePoint `:p:/` and `:v:/`
share links are corp-gated; they break publicly and may expose internal data.
Reference the artifact by name.

**VII.3 — One file, no new dependencies.** An agent is a single `.py` importing
only the standard library and `BasicAgent`. It must run on a Brainstem with
nothing installed.

---

## The checklist

```
python tools/validate_agent.py <path/to/agent.py>     # Articles II–V, mechanical
python tools/run_demo_cases.py <slug>                 # Article VI, live
```

An agent that passes both, implements an advertised one-pager, and honours
Article I is in the library. Anything else is a draft.
