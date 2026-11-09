# Supply Risk Monitoring Agent

Deliver real-time risk intelligence and planning to protect production continuity and reduce disruption exposure.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/supplier-risk-monitoring/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Procurement Manager, Supply Chain Director
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Where is supplier exposure concentrated, and which relationships should leadership review first?` | Review concentrated supplier exposure |
| `Explain why TechnoCore is elevated and show me the evidence by risk dimension.` | Explain an elevated supplier |
| `Which recorded disruptions could threaten continuity, and what exposure should we validate?` | Review continuity threats |
| `Compare backup sourcing options for review, but do not contact, qualify, select, or order from any supplier.` | Compare backup sourcing options |

## What the agent does

- Unify risk data and score suppliers in real time
- Provide visibility into financial health, operational capacity, and logistics reliability
- Recommend mitigation actions like safety stock and dual sourcing
- Model cost exposure and ROI

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_SupplyRiskMonitoringPilot`) with instructions and a greeting that lists the sample prompts.
- 8 agent skills, one per operation:
  - `alternative-sourcing` - Use when a procurement manager asks for backup options without taking supplier action.
  - `disruption-alerts` - Use when a supply chain director asks what recorded incidents may affect continuity.
  - `financial-impact` - "Use when a supply chain director asks something like \"What would those mitigations cost us, and is the investment worth it\""
  - `implementation-roadmap` - "Use when a supply chain director asks something like \"Lay out a twelve-month plan for putting these protections in place\""
  - `mitigation-plan` - "Use when a procurement manager asks something like \"What mitigation strategies do you recommend for each of our semiconductor suppliers\""
  - `monitoring-plan` - "Use when a procurement manager asks something like \"How would we keep watching these suppliers after the plan is in place\""
  - `risk-dashboard` - Use when a supply chain director asks where supplier exposure deserves review.
  - `supplier-scorecard` - Use when a procurement manager asks why a supplier is rated for review.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_supplier-risk-monitoring-review-rules.md`
  - `aibast_supplier-risk-monitoring-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Supply Risk Monitoring Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Reduced disruption exposure with early risk detection and mitigation
- Protected revenue by preventing supply chain interruptions
- Improved procurement agility with real-time insights
- Strengthened supplier relationships with better risk communication and proactive planning

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
