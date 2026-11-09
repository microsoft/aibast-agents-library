# Care Gap Closure Agent

Automate quality gap analysis and targeted outreach to improve HEDIS performance, campaign ROI, and care gap closure efficiency.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/care-gap-closure/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Quality Managers, Care Coordinators, Clinical Operation Leads
- **Industries:** Healthcare

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Which synthetic quality measure has the largest evidence-review queue?` | Quality Manager: Gap Analysis |
| `Organize the synthetic evidence-review cohorts without clinical risk scoring.` | Care Coordinator: Cohort Review |
| `Draft outreach for the synthetic screening measure, but do not send it or state that anyone is eligible.` | Care Coordinator: Outreach Draft |
| `Show the qualitative source-completeness dashboard and its limitations.` | Clinical Operations Lead: Quality Dashboard |
| `I need to prioritize care gaps for our Medicare Advantage population before the HEDIS reporting deadline. What's our current status?` | Quality Manager: Hedis Status |
| `Show me the top care gaps and which ones are most actionable.` | Quality Manager: Top Gaps |
| `Show me the diabetes cohort analysis with risk tiers and engagement barriers.` | Care Coordinator: Risk Stratification |
| `Design a barrier-specific outreach strategy for the diabetes gap patients.` | Care Coordinator: Outreach Strategy |
| `Show me the campaign deployment plan and projected impact.` | Clinical Operations Lead: Campaign Projection |
| `Configure monitoring for the campaign and alert me if performance drops.` | Clinical Operations Lead: Monitoring Plan |

## What the agent does

- Analyze quality measures and surface high‑priority gaps
- Stratify outreach based on risk, condition severity, and engagement
- Identify common barriers that impacted care completion
- Launch targeted multi‑channel outreach campaigns with real‑time progress tracking

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_CareGapClosurePilot`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `campaign-projection` - "Use when a clinical operations lead asks something like \"Show me the campaign deployment plan and projected impact\""
  - `care-gap-closure-cohort-review` - Organizes operational evidence-review cohorts without clinical risk scoring.
  - `care-gap-closure-gap-analysis` - Summarizes aggregate synthetic source counts and limitations without deciding measure eligibility.
  - `care-gap-closure-outreach-draft` - Drafts privacy-aware language but does not contact anyone.
  - `care-gap-closure-quality-dashboard` - Shows source-completeness signals for quality and clinical validation.
  - `hedis-status` - "Use when a quality manager asks something like \"I need to prioritize care gaps for our Medicare Advantage population before the HEDIS reporting deadline. What's our current status\""
  - `monitoring-plan` - "Use when a clinical operations lead asks something like \"Configure monitoring for the campaign and alert me if performance drops\""
  - `outreach-strategy` - "Use when a care coordinator asks something like \"Design a barrier-specific outreach strategy for the diabetes gap patients\""
  - `risk-stratification` - "Use when a care coordinator asks something like \"Show me the diabetes cohort analysis with risk tiers and engagement barriers\""
  - `top-gaps` - "Use when a quality manager asks something like \"Show me the top care gaps and which ones are most actionable\""
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_care-gap-closure-review-rules.md`
  - `aibast_care-gap-closure-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Care Gap Closure Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Strengthened their HEDIS performance and Star Rating
- Improved care‑gap closure rates via targeted outreach
- Reduced admin workloads by automating patient identification and personalizing outreach
- Gained clear visibility into campaign progress to adjust strategies mid‑cycle

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
