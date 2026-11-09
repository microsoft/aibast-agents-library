# Returns and Complaints Resolution Agent

Automate return decisions and complaint handling to speed resolution, reduce fraud, and protect customer loyalty.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/returns-complaints-resolution/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Customer Service Agents, Quality Teams, Loss Prevention Teams
- **Industries:** Retail, Consumable Products Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Summarize the anonymous return review evidence and approval boundary.` | Review an anonymous return case |
| `Classify this product concern without echoing personal information or sending a response.` | Classify a complaint safely |
| `Draft a policy-grounded option and keep all actions behind authorization.` | Draft a resolution option |
| `Summarize aggregate defect and return patterns without accusing any person.` | Analyze aggregate quality trends |

## What the agent does

- Automatically evaluate and classify return requests
- Prioritize complaints with high sentiment, draft tailored responses, and execute resolution options
- Analyze SKU patterns for quality issues and suspicious behavior
- Recommend resolution strategies based on customer value

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ReturnsandComplaintsResolut`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `aggregate-returns-quality-trends` - Helps Quality and Loss Prevention teams review aggregate synthetic patterns without accusing people.
  - `anonymous-return-review-queue` - Helps a Customer Service Agent review anonymous synthetic return evidence without approving or processing a return.
  - `escalation-snapshot` - "Use when a service manager asks something like \"As Service Manager, I have an escalated customer complaint about a defective laptop and the customer is very upset; help me resolve it quickly\""
  - `executive-summary` - "Use when a service manager asks something like \"As Service Manager, create the executive summary and recap what we accomplished\""
  - `follow-up-plan` - "Use when a service manager asks something like \"As Service Manager, the call went well and the customer accepted; what is our follow-up plan\""
  - `human-approved-resolution-options` - Drafts policy-grounded resolution options for a Customer Service Agent without executing them.
  - `privacy-safe-complaint-classification` - Classifies a complaint for a Customer Service Agent without repeating personal or sensitive content.
  - `recovery-performance` - "Use when a service manager asks something like \"As Service Manager, show me the service recovery performance and financial impact\""
  - `recovery-tiers` - "Use when a service manager asks something like \"As Service Manager, show me resolution options that will keep this VIP customer satisfied\""
  - `resolution-execution-plan` - "Use when a service manager asks something like \"As Service Manager, Tier 1 is approved; get it ready and prepare my talking points for the call\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_returns-complaints-rules-and-safety.md`
  - `aibast_returns-complaints-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Returns and Complaints Resolution Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Accelerated return and complaint resolution
- Delivered consistent, empathetic customer communications
- Reduced fraudulent returns and improved early defect detection
- Increased customer retention by applying recovery strategies that preserve lifetime value

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
