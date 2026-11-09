# Cross-Selling Opportunities Agent

Identify and prioritize expansion opportunities to drive revenue growth and strengthen customer relationships.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/cross-selling/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Sales Leader, Sales Operations Manager, Enablement Manager
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Scan synthetic customer CUST-001 (Acme Corp) for product gaps, usage signals, buying signals, and budget timing.` | Scan product gaps |
| `Explain the synthetic product-affinity and benchmark assumptions without treating them as observed conversion performance.` | Review affinity assumptions |
| `Draft engagement strategies, talking points, and an outreach sequence for synthetic customer CUST-001 (Acme Corp) without sending outreach.` | Draft product recommendations |
| `Show me the revenue impact and conversion timeline for the cross-sell plan, without treating the scenario as committed revenue.` | Compare portfolio scenarios |
| `Analyze our top 100 enterprise accounts and identify cross-selling opportunities based on their current product usage.` | Portfolio Scan |
| `Show me the top 5 highest-value cross-sell opportunities and a deep dive on the first account.` | Top Opportunities |
| `Assign the opportunity accounts to reps by expertise and draft this week's action plan.` | Account Assignments |

## What the agent does

- Analyze usage patterns and benchmark gaps across all accounts
- Detect buying signals from feature requests and usage anomalies
- Generate prioritized lists with confidence scores and ARR potential
- Create personalized outreach sequences aligned to customer needs and budget timing

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CrossSellingOpportunitiesPi`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `account-assignments` - "Assign the opportunity accounts to reps by expertise and draft this week's action plan."
  - `opportunity-scan` - "Scan synthetic customer CUST-001 (Acme Corp) for product gaps, usage signals, buying signals, and budget timing."
  - `portfolio-scan` - "Analyze our top 100 enterprise accounts and identify cross-selling opportunities based on their current product usage."
  - `product-affinity` - "Review the synthetic affinity rules and benchmark assumptions without treating them as observed conversion performance."
  - `recommendation-engine` - "Draft engagement strategies, talking points, and an outreach sequence for synthetic customer CUST-001 (Acme Corp) without sending outreach."
  - `revenue-impact` - "Show me the revenue impact and conversion timeline for the cross-sell plan, without treating the scenario as committed revenue."
  - `top-opportunities` - "Show me the top 5 highest-value cross-sell opportunities and a deep dive on the first account."
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_cross-selling-operating-rules.md`
  - `aibast_cross-selling-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Cross-Selling Opportunities Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Increased expansion pipeline through systematic opportunity identification
- Cut account research time from hours to minutes
- Accelerated deal cycles by aligning outreach with budget windows
- Strengthened customer relationships through proactive, value-driven engagement

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
