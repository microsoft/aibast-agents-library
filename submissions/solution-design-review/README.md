# Solution Design Review Agent

Help architects draft and self-check a solution design document before the architecture review board: intake of the template, discovery notes and initiative brief, an architecture vision, the current-state baseline, the non-functional requirements matrix with owners and gaps, the target design with its inventory changes, and a readiness check with a confidence score and severity-ranked gaps. The agent is read-only; it never submits to the review board, changes an inventory record, or approves a design.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/solution-design-review/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Solution Architect, Enterprise Architecture Lead, Review Board Coordinator
- **Industries:** Professional Services, Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `I have the design template, the discovery notes and the initiative brief for the delivery notifications project. Walk me through where to start.` | Solution Architect: Design intake and plan |
| `Draft the vision: scope, stakeholders and which architecture domains are impacted.` | Solution Architect: Architecture vision draft |
| `What does the current state look like for the systems in scope?` | Solution Architect: Current-state baseline |
| `Which non-functional requirements apply, and who owns each one?` | Enterprise Architecture Lead: Non-functional requirements matrix |
| `Draft the target design and list what changes in the inventory.` | Solution Architect: Target design and inventory delta |
| `Is this design ready for the review board?` | Review Board Coordinator: Review-board readiness check |

## What the agent does

- Plan the design from the template, notes and brief in one step
- Draft the vision, baseline and target design with inventory changes
- Build the requirements matrix with owners, gaps and variances
- Run a readiness check with a confidence score before each review

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_SolutionDesignReviewManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `architecture-vision` - Use when an architect asks for the vision: business driver, scope, stakeholders, impacted domains, constraints and review workgroups.
  - `current-state` - Use when an architect asks what the current state looks like for the systems or components in scope.
  - `design-intake` - Use when an architect hands over the design template, discovery notes and initiative brief and asks where to start.
  - `readiness-check` - Use when someone asks whether the design is ready for the review board, its confidence score or its gaps.
  - `requirements-matrix` - Use when someone asks which non-functional requirements apply, who owns each one, and where the gaps and variances are.
  - `target-design` - Use when an architect asks for the target design and what changes in the component inventory.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_solution-design-review-rules-and-guardrails.md`
  - `aibast_solution-design-review-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Solution Design Review Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Produced first drafts of design sections in hours instead of days
- Arrived at review with owners named and variances answered
- Reduced designs sent back for avoidable checklist gaps

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
