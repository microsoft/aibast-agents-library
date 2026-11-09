# Supplier Claim Engagement Agent

Help retail claims teams recover more from suppliers by triaging damage, shortage, quality, and pricing claims, assembling evidence packs, drafting supplier claim notices, tracking response deadlines, and evaluating supplier responses, while every send, credit acceptance, and escalation stays with an authorized coordinator.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/supplier-claim-engagement/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Supplier Claims Coordinator, Receiving Supervisor, Claims Team Lead, Category Manager
- **Industries:** Retail, Consumer Goods

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Show me our open supplier claims and what needs attention today.` | Supplier Claims Coordinator: Supplier claims queue |
| `Triage the new damage claim CLM-5201. Who is responsible and what are the terms?` | Supplier Claims Coordinator: Claim triage |
| `Is the evidence for CLM-5201 complete, and what is the claim worth?` | Receiving Supervisor: Evidence pack check |
| `Draft the claim notice to the supplier for CLM-5201, but don't send it.` | Supplier Claims Coordinator: Supplier claim notice draft |
| `Which supplier claims are at risk of missing their response deadline?` | Claims Team Lead: Response deadline tracker |
| `Litware Snacks replied on CLM-5204. What did they offer, and what's the gap?` | Supplier Claims Coordinator: Supplier response evaluation |
| `Prepare an escalation for the overdue shortage claim CLM-5202.` | Claims Team Lead: Escalation brief draft |

## What the agent does

- Triages damage, shortage, quality and pricing claims
- Assembles evidence packs and drafts claim notices
- Tracks response windows and drafts escalations before value is lost
- Evaluates supplier responses to surface unrecovered value

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_SupplierClaimManualBuild`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `claims-queue` - Use when a coordinator asks for open supplier claims, their value and severity, recovery to date, or what needs attention today.
  - `draft-supplier-claim` - Use when a coordinator asks to prepare or draft the claim to a supplier; the notice stays Not Sent with the response dates it would carry.
  - `escalation-brief` - Use when the team asks to escalate a claim that is past its supplier response window; returns a draft for approval.
  - `evidence-pack` - Use when someone asks which photos and documents a claim needs, what is on file, and the claim value by line.
  - `sla-tracker` - Use when the team asks which claims are breached, at risk, or on track against supplier response windows.
  - `supplier-response` - Use when a coordinator asks what a supplier replied or offered and how it compares with the claim value.
  - `triage-claim` - Use when a coordinator asks for a claim's severity, responsible supplier, purchase order, and supplier response and resolution windows.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_supplier-claim-engagement-rules-and-guardrails.md`
  - `aibast_supplier-claim-engagement-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Supplier Claim Engagement Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- More value recovered: every open claim and its value in one queue
- Faster filing: evidence packs arrive as ready drafts
- Fewer missed deadlines: at-risk claims surface early

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
