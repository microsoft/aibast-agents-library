# M&A Target Sourcing Agent

Turn an acquisition thesis into a transparent, cited target shortlist: screening criteria, a weighted ranking of a synthetic market universe, target dossiers with sources and diligence questions, a weighting challenge, evidence-gap review, and an investment committee screening memo draft. The agent is read-only; it never contacts a target, updates a CRM, shares a document, or makes an investment decision.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/ma-target-sourcing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Corporate Development Associate, Head of Corporate Development, Research Analyst
- **Industries:** Financial Services, Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `We want to buy a profitable compliance-workflow software company in Europe within our revenue band. Turn that into a screen we can run.` | Corporate Development Associate: Thesis to screening criteria |
| `Run the screen and rank the companies that pass.` | Corporate Development Associate: Ranked target longlist |
| `Give me the dossier on the top-ranked target, with its sources and diligence questions.` | Corporate Development Associate: Cited target dossier |
| `Does the ranking hold if we weight financial quality more heavily?` | Head of Corporate Development: Weighting challenge |
| `Where is our evidence thin or out of date?` | Research Analyst: Evidence-gap review |
| `Draft the screening memo for the investment committee.` | Head of Corporate Development: Investment committee memo draft |

## What the agent does

- Convert the thesis into filters and weights in one conversation
- Rank the passing companies and show how each score is built
- Open cited dossiers and flag thin or stale evidence as research requests
- Draft the screening memo, leaving approval to the team

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_MATargetSourcingManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `build-thesis` - Use when someone describes an acquisition thesis and wants it turned into screening criteria and filters.
  - `challenge-ranking` - Use when someone asks whether the ranking holds under different weightings, such as weighting financial quality more heavily.
  - `evidence-gaps` - Use when someone asks where the evidence behind the targets is thin, missing or out of date.
  - `ic-memo-draft` - Use when someone asks for the investment committee screening memo draft for the shortlist.
  - `screen-targets` - Use when someone wants the screen run and the passing companies ranked with a transparent weighted score.
  - `target-dossier` - Use when someone wants one target's profile, synthetic financials, criteria scores, sources and diligence questions.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_ma-target-sourcing-rules-and-guardrails.md`
  - `aibast_ma-target-sourcing-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **M&A Target Sourcing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Moved from thesis to a ranked shortlist in a single working session
- Gave the committee rankings it could audit and challenge
- Started outreach only after evidence gaps were closed

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
