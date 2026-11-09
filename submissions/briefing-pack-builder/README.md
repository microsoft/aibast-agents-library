# Briefing Pack Builder Agent

Turn a government team's source documents into cited, template-ready briefs in minutes, with conflicting figures flagged and missing content named, so specialists verify instead of rebuild.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/briefing-pack-builder/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Briefing Coordinators, Budget Analysts, Department Directors
- **Industries:** State and Local Government

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What briefing formats can you build for us?` | Briefing Coordinator: Briefing formats |
| `What do we hold on the Elm Street Bridge Replacement?` | Budget Analyst: Content scan |
| `Before I draft anything, do any of the figures disagree?` | Budget Analyst: Figure check |
| `Draft the budget hearing brief on the Elm Street bridge.` | Briefing Coordinator: Cited draft brief |
| `Which sections of that brief still need input?` | Briefing Coordinator: Gap report |
| `Who signs this brief off, and how long does it take?` | Department Director: Approval route |

## What the agent does

- Lists formats and scans what the content set holds
- Flags figures that disagree across documents
- Drafts the brief with a citation for every section
- Names gaps and the review and approval route

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_BriefingPackBuilderManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `approval-route` - Use when a department director asks something like "Who signs this brief off, and how long does it take"
  - `content-scan` - Use when a budget analyst asks something like "What do we hold on the Elm Street Bridge Replacement"
  - `draft-brief` - Use when a briefing coordinator asks something like "Draft the budget hearing brief on the Elm Street bridge"
  - `figure-check` - Use when a budget analyst asks something like "Before I draft anything, do any of the figures disagree"
  - `gap-report` - Use when a briefing coordinator asks something like "Which sections of that brief still need input"
  - `list-templates` - Use when a briefing coordinator asks something like "What briefing formats can you build for us"
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_briefing-pack-builder-rules-and-guardrails.md`
  - `aibast_briefing-pack-builder-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Briefing Pack Builder Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Faster first drafts that specialists verify, not rebuild
- Fewer wrong figures in front of decision makers
- Earlier requests for missing content

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
