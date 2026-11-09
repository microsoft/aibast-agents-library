# Proposal Generation Agent

Automate proposal creation to accelerate deal cycles, improve win rates, and deliver consistent, high-quality responses.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/proposal-generation/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Account Executive, Sales Leader, Bid Manager
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Analyze the synthetic Meridian Healthcare RFP and show the traceable requirement checklist.` | Analyze the RFP |
| `Draft an executive summary for the synthetic Meridian Healthcare opportunity that reflects the buyer priorities and remains subject to review.` | Draft the executive summary |
| `Compare the synthetic solution and pricing assumptions for Meridian Healthcare without approving a price, discount, or concession.` | Review pricing assumptions |
| `Prepare synthetic reference and competitive positioning options for Meridian Healthcare, with availability checks before use.` | Prepare competitive positioning |
| `Outline the synthetic Meridian Healthcare proposal package and every human review required before delivery.` | Outline the proposal package |
| `Summarize the synthetic Meridian Healthcare draft readiness and the decisions authorized reviewers must make next.` | Summarize draft readiness |

## What the agent does

- Parse RFP requirements and draft compliance checklists instantly
- Assemble tailored executive summaries and competitive positioning
- Optimize pricing and bundle recommendations
- Draft client-ready proposal materials

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ProposalGenerationPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `proposal-generation-analyze-rfp` - Analyze the Meridian Healthcare synthetic RFP and produce a traceable requirement checklist.
  - `proposal-generation-compile-proposal` - Prepare a reviewable proposal package outline; do not claim a final document was generated or approved.
  - `proposal-generation-delivery-summary` - Summarize draft proposal readiness and human-governed next-step options without sending anything.
  - `proposal-generation-executive-summary` - Draft a synthetic executive summary aligned to stated buyer priorities for human review.
  - `proposal-generation-references-positioning` - Draft reference and competitive positioning options using synthetic evidence only.
  - `proposal-generation-solution-pricing` - Compare the synthetic solution and pricing assumptions without approving a price or concession.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_proposal-generation-operating-rules.md`
  - `aibast_proposal-generation-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Proposal Generation Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Developed a complete, branded proposal package in minutes
- Improved proposal quality and alignment with buyer priorities
- Enabled same-day turnaround for competitive opportunities
- Freed sales teams to pursue more deals without sacrificing proposal quality

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
