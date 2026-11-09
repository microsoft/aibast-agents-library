# Engineering Standards Agent

Give designers and field crews cited answers from engineering standards in seconds: vetted values first, clearly labeled interpretations when no vetted value exists, an engineer review loop that turns good interpretations into vetted guidance, and standards-based job scoping.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/engineering-standards-advisor/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Design Technician, Standards Engineer, Field Engineering Lead
- **Industries:** Energy and Utilities

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What is the minimum clearance for a primary conductor over a public road?` | Design Technician: Vetted standards lookup |
| `Can I use a Class 5 pole on a 35-degree corner that carries a 75 kVA transformer?` | Design Technician: Labeled standards interpretation |
| `Send the corner-pole interpretation to a standards engineer to confirm.` | Design Technician: Engineer review request |
| `What is waiting in my standards review queue?` | Standards Engineer: Standards review queue |
| `Show the overhead clearances quick-reference sheet and anything due for re-vetting.` | Standards Engineer: Quick-reference sheet |
| `Scope the Maple Ridge pole replacement job: risk, effort and the standards that apply.` | Field Engineering Lead: Standards-based job scoping |

## What the agent does

- Answers with vetted values and section and page citations
- Labels interpretations as unvetted when no vetted value exists
- Routes interpretations to a standards engineer for vetting
- Gives engineers one queue of interpretations to confirm

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_EngineeringStandardsManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `flag-for-review` - Use when someone wants a standards engineer to confirm an interpretation; prepares a draft only.
  - `interpretation` - Use when a question has no vetted value and needs a cited, clearly unvetted interpretation.
  - `quick-reference` - Use when someone asks for a standard's vetted quick-reference sheet or its re-vetting status.
  - `review-queue` - Use when a standards engineer asks what is waiting for review or re-vetting.
  - `scope-job` - Use when someone asks to scope a job's risk, effort and applicable standards.
  - `vetted-lookup` - Use when someone asks for a clearance, depth or limit that has a vetted quick-reference value.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_engineering-standards-advisor-rules-and-guardrails.md`
  - `aibast_engineering-standards-advisor-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Engineering Standards Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Vetted values answered in seconds, with citations
- Interpretations labeled unvetted and routed to an engineer
- Jobs scoped against the right standards, gaps flagged

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
