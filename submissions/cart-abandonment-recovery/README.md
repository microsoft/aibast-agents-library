# Cart Abandonment Recovery Agent

Automate abandoned cart analysis and recovery campaigns to convert lost sales, protect margins, and improve customer engagement.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/cart-abandonment-recovery/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Marketing Manager, Digital Marketing Lead, Growth Manager
- **Industries:** Cross-Industry, Software Tech

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Show where the anonymous synthetic cart journey is breaking down and what needs review.` | Diagnose anonymous cart friction |
| `Outline a consent-aware draft sequence without sending or scheduling anything.` | Draft a consent-aware sequence |
| `Compare margin-aware value scenarios and keep every concept behind approval.` | Compare incentive concepts |
| `Summarize the fixed recovery metrics and separate benchmarks from planning estimates.` | Review recovery scenarios |

## What the agent does

- Segment abandoned carts by value and recovery likelihood
- Generate personalized offers and urgency messaging for each segment
- Deploy multi-touch campaigns across email, SMS, and retargeting with optimized timing
- Forecast recovery rates and revenue impact for leadership reporting

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CartAbandonmentRecoveryPilo`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `anonymous-cart-abandonment-analysis` - Helps a Marketing Manager review anonymous synthetic abandonment patterns without contacting shoppers.
  - `consent-aware-recovery-campaign-draft` - Gives a Digital Marketing Lead a proposed recovery sequence without sending or scheduling outreach.
  - `margin-aware-incentive-scenarios` - Helps a Growth Manager compare optional incentive concepts without issuing value.
  - `optimization-recommendations` - "Use when a growth manager asks something like \"As Growth Manager, what else could we change to lift our recovery rate further\""
  - `recovery-forecast` - "Use when a growth manager asks something like \"As Growth Manager, how much revenue should we expect to win back over the next two days, and how does that compare to the industry\""
  - `recovery-strategies` - "Use when a marketing manager asks something like \"As Marketing Manager, what personalized offers should we make to win back our top abandoned-cart shoppers\""
  - `synthetic-recovery-conversion-tracking` - Summarizes fixed aggregate recovery metrics for a Growth Manager without claiming live performance.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_cart-recovery-rules-and-safety.md`
  - `aibast_cart-recovery-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Cart Abandonment Recovery Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Increased recovery rates through precision targeting and personalized incentives
- Protected margins with discount guardrails and alternative offers
- Reduced manual workloads and response times
- Improved decision-making with real-time performance dashboards

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
