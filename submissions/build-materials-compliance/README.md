# Build Materials Compliance Agent

Keep grant-funded construction bills of materials compliant every week: flag items that newly fall out of the program's materials sourcing rule with cited evidence, find same-specification compliant alternates, watch vendor certificates, and keep the audit evidence package ready.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/build-materials-compliance/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Procurement Compliance Leads, Buyers, Supplier Quality Managers, Program Compliance Reviewers
- **Industries:** Manufacturing, Construction, Public Infrastructure

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What changed on our approved bills of materials this week?` | Procurement Compliance Lead: Weekly BOM change scan |
| `Is anything newly out of compliance, and why?` | Procurement Compliance Lead: Materials compliance check |
| `Find me a compliant replacement for the gate valve with the same spec.` | Buyer: Compliant alternates |
| `Which vendor certificates have lapsed or are about to?` | Supplier Quality Manager: Vendor certificate watch |
| `Are we ready if the program auditor asks for our evidence package?` | Program Compliance Reviewer: Audit evidence readiness |
| `I approve the hold, the GV-08B substitution and the vendor follow-ups. Prepare the drafts.` | Procurement Compliance Lead: Approved next-step drafts |

## What the agent does

- Scans approved bills of materials and reports what changed
- Flags newly non-compliant items with the cited evidence
- Finds same-spec compliant alternates and sizes the switch
- Keeps certificates and audit evidence current and drafts approved next steps

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_BuildMaterialsManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `action-drafts` - Use when a person has approved next steps and wants the hold notice, renewal, substitution and document request drafts.
  - `audit-evidence` - Use when someone asks whether the audit evidence package is ready for each project.
  - `compliance-check` - Use when someone asks which items are out of compliance or newly non-compliant and why.
  - `compliant-alternates` - Use when someone asks for a compliant replacement or alternate part with the same specification.
  - `vendor-watch` - Use when someone asks which vendor certificates have expired or expire soon.
  - `weekly-changes` - Use when someone asks what is new or changed on the approved bills of materials this week.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_build-materials-compliance-rules-and-guardrails.md`
  - `aibast_build-materials-compliance-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Build Materials Compliance Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Catches compliance problems before materials are ordered
- Ties every finding to its evidence
- Stays audit-ready every week

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
