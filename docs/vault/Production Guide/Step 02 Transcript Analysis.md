---
title: Step 02 Transcript Analysis
section: Production Guide
status: published
hook: How the transcript is turned into structured project JSON and audited at Quality Gate 1.
source: "docs/rapp-guide.html#step2"
---

# Step 02 Transcript Analysis

**Transcript analysis** turns the raw discovery transcript into structured **project JSON**.
An AI agent does the extraction. A person audits the result.
This is **Quality Gate 1**: did we extract the right problem?

Guide section: [Step 2 in the production guide](../rapp-guide.html#step2)

## At a glance

- **Type:** Audit (Quality Gate 1)
- **Duration:** about 15 minutes; the AI is instant, the human review takes the time
- **Owner:** Delivery Team, the people who will build the solution
- **Input:** the transcript from [[Step 01 Discovery Call]]
- **Output:** validated `[customer]-project.json`, audit sign-off, go/no-go decision

## The tool

The **Transcript-to-Project Agent** is a Copilot Studio declarative agent.
If its link is down, the guide includes a manual fallback prompt to paste into Copilot.

How to use it:

1. Open the agent in Copilot Studio.
2. Paste the whole transcript.
3. The agent returns JSON with the extracted fields.
4. Save it as `[customer]-project.json` or import it into the project tracker.

## Example output

From the guide (a fictional company):

```json
{
 "id": "1735840999",
 "customerName": "Acme Insurance",
 "status": "planning",
 "type": "legal",
 "description": "Legal operations AI bot for contract automation",
 "stakeholders": "VP Legal, Legal Operations Manager",
 "competingSolution": "Salesforce",
 "agents": ["ContractTemplate", "ContractAnalysis", "ContractRouting"],
 "mvpUseCase": "NDA Automation Bot",
 "mvpDescription": "Automated NDA generation, analysis, and routing with approval workflows",
 "mvpTimeline": "6 weeks POC",
 "notes": "Competing with Salesforce, focus on contract automation. Latency requirement under 2 seconds.",
 "createdDate": "2025-10-15",
 "updatedDate": "2025-10-15"
}
```

The prompt constrains some fields:

- `status` is one of `planning`, `poc`, `active`, `production`, `completed`. Use `planning` unless a POC has started.
- `type` is one of `legal`, `hr`, `it`, `compliance`, `customer-service`, `sales`, `finance`, `other`.
- `agents` names are PascalCase, no spaces.

## The human audit checklist

- **Customer name:** correct legal entity?
- **Stakeholders:** all decision makers, correct titles?
- **MVP use case:** matches what the customer said?
- **Competing solutions:** noted?
- **Timeline:** realistic and confirmed?
- **Data sources:** captured?

Common corrections:

- One broad `ContractManagement` agent → three focused agents.
- `status` "active" → "planning" (nothing is built yet).
- Timeline "ASAP" → a concrete timeframe.

## Gate decision

- **Pass:** the JSON accurately represents the problem → [[Step 03 Generate MVP Poke]].
- **Fail:** key information missing or wrong → follow-up call.

**Do not proceed if:**

- The MVP use case is vague ("improve efficiency").
- No data sources were identified.
- The decision maker was not on the call.
- The problem is "nice to have", not "must solve".

Fifteen minutes here prevents weeks of building the wrong thing.

## How rapp/1 underpins this step

Only lightly. The project JSON is a delivery-tracking record. The upstream RAPP/1 specification does not define its schema.

One forward link is real. The `agents` array names the capabilities that become agent files in [[Step 05 Generate Agent Code]], each following [[The Agent Contract]].

## Related

- [[Step 01 Discovery Call]]
- [[Step 03 Generate MVP Poke]]
- [[Step 04 Customer Validation]]
- [[Production Guide Overview]]
- [[The Agent Contract]]
