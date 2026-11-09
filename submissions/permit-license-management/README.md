# Permit Management Agent

Deliver real-time insights, automate critical workflows, and enable guided decision making—boosting efficiency while reducing operational and compliance risk for energy organizations.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/permit-license-management/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Plant Manager / Reliability Engineer, Compliance Manager, Sustainability Lead, Data Analyst
- **Industries:** Energy and Utilities

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Show me our permit status and any expiring soon` | Facility Manager: Permit status and expiring permits |
| `Which permit renewals have already missed their lead time, and how many days are left?` | Permit Coordinator: Renewal deadlines and lead times |
| `What permit evidence gap needs immediate authorized review?` | Compliance Manager: Compliance gap triage |
| `Where does the Imperial Valley Solar Phase 2 application stand, and did we submit anything today?` | Environmental Counsel: Application tracking |
| `Start emergency renewals for the critical permits.` | Operations Director: Emergency renewal package |

## What the agent does

- Predict failures with real-time analysis and automated planning
- Automate permit tracking and renewals with intelligent workflows
- Generate audit-ready reports quickly with streamlined data collection
- Consolidate fragmented data into real-time insights for easy centralized monitoring

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PermitManagementPilot`) with instructions and a greeting that lists the sample prompts.
- 5 agent skills, one per operation:
  - `permit-license-management-application-status` - Use when a Environmental Counsel asks to track existing applications without filing or amendment.
  - `permit-license-management-compliance-gaps` - Use when a Compliance Manager asks to triage gaps without declaring legal compliance.
  - `permit-license-management-permit-inventory` - Use when a Facility Manager asks to review the synthetic permit register by facility.
  - `permit-license-management-renewal-calendar` - Use when a Permit Coordinator asks to prepare a read-only renewal calendar.
  - `permit-license-management-renewal-plan` - "Use when a Operations Director asks to prepare the emergency renewal package for the critical permits with costs, production protected, and draft stakeholder alerts"
- 2 knowledge files holding the synthetic records and operating rules:
  - `permit-license-management-rules-and-controls.md`
  - `permit-license-management-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Permit Management Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Improved asset reliability, reducing unplanned downtime and costs
- Maintained compliance and operational continuity across facilities
- Streamlined compliance reporting and minimized audit risk
- Gained real-time visibility and strategic planning support to achieve emissions goals

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
