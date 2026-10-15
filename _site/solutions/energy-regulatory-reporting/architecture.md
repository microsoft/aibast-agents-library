# Regulatory Reporting Agent architecture

## Local decision-support path

`persona question -> RegulatoryReportingAgent -> synthetic records -> deterministic analysis -> approval-gated recommendation`

The portable agent is read-only. Its four operations remain independently routable and return strings suitable for Brainstem or Copilot Studio.

## Production replacement seams

- Regulatory data lake
- Controlled reporting workspace
- Approved regulator filing connector

Replace synthetic dictionaries with least-privilege read connectors first. Any later write tool must be separate from analysis, require explicit confirmation by an authorized role, validate current source state, and append an immutable audit event.

## Safety boundary

The agent may summarize, screen, compare, estimate, and draft. It may not execute an operational, regulatory, financial, environmental, procurement, customer, or field action. A model response is never proof that a write occurred.
