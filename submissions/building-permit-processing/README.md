# Building Permit Processing Agent

Automate building permit review processes to enable faster service, lower operational costs, and higher citizen satisfaction.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/building-permit-processing/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Permit Technicians, Plan Reviewers, Inspectors
- **Industries:** State and Local Government

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which permit applications have been sitting too long, and which resident is going to complain first?` | Find the permit most likely to trigger a complaint |
| `Anything at the front counter I should not be accepting today?` | Triage today’s front-counter submissions |
| `The restaurant fit-out on Harbor Way just came in. Who needs to review it and when is it due back?` | Route the Harbor Way restaurant fit-out |
| `My front desk is drowning in status calls. What can we send out today so people stop calling?` | Stop avoidable applicant status calls |
| `What inspections are on the board for the solar job, and who is covering them?` | See the solar inspection board |

## What the agent does

- Classify and validate permit applications at intake
- Route requests automatically to the correct review teams
- Centralize communication and provide instant updates to applicants
- Provide inspectors with mobile access and real‑time assignments

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_BuildingPermitManualBuildBuild`) with instructions and a greeting that lists the sample prompts.
- 12 agent skills, one per operation:
  - `approval-workflow-tracking` - Use to track the approval workflow of BP-2024-3847; shows the timeline, reviewer feedback, the contractor resubmission, and correction status.
  - `automated-code-compliance-review` - Use for code compliance checking or plan review of BP-2024-3847 against building, electrical, plumbing, and zoning codes.
  - `inspector-board-and-coverage` - Use for the inspection board, solar-job schedule, inspector specialty, availability, and service-zone questions while avoiding any claim that an assignment was changed.
  - `intake-triage-and-review-routing` - Use for front-counter and newly arrived applications to identify duplicates, missing documents, acceptance readiness, review desks, and fixed statutory due dates.
  - `new-application-intake-check` - Use when a permitting supervisor asks to process or review the new residential application; shows the completeness table, fee, and hold or accept recommendation for BP-2024-3847.
  - `permit-backlog-and-complaint-risk` - Use for department-wide delay, statutory-clock, backlog, and likely-status-call questions; ranks every open synthetic permit and identifies the first intervention.
  - `permit-issuance-package` - Use to show the permit issuance for BP-2024-3847; assembles the permit package, the four required inspections, and a citizen notification draft for staff to issue and send.
  - `permit-review-checklist` - Use when a technician or reviewer needs the fixed common and permit-type-specific review scope for a synthetic application without making a compliance finding.
  - `permit-status-and-zoning-detail` - Use for a named permit, applicant, parcel, address, project, or full dashboard to report the synthetic record and quote its zoning reference standards.
  - `plan-review-routing` - Use to route BP-2024-3847 for expert review; recommends the plans examiner by specialization and workload, the review packet, parallel reviews, and an applicant notification draft.
  - `proactive-applicant-updates` - Use when staff want to reduce status calls by drafting specific synthetic updates for every open applicant, prioritized by overdue and correction risk.
  - `synthetic-permit-fee-estimate` - Use for permit cost, fee breakdown, or formula questions to calculate all seven synthetic fee categories from declared valuation and label the result as an estimate.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_building-permit-synthetic-records.md`
  - `aibast_permit-rules-and-schedules.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Building Permit Processing Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Accelerated approvals with consistent, automated workflows
- Reduced status‑check calls through transparent, self‑service tracking
- Improved coordination across planning, zoning, code, and inspections
- Delivered a faster, more predictable permitting experience for residents

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
