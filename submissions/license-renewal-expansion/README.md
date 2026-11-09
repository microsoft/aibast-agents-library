# License Renewal and Expansion Agent

Streamline subscription renewal management and expansion planning, turning risk into growth opportunities while increasing win probability.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/license-renewal-expansion/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Account Executives, Customer Success Managers, Sales Leadership
- **Industries:** Software Tech

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Review the bundled synthetic renewal pipeline, risk bands, and preparation checklist without changing CRM or forecast records.` | Review the renewal pipeline |
| `Identify synthetic demand signals and draft packaging options that still require authorized pricing review.` | Find expansion signals |
| `Which synthetic accounts show churn or competitor risk, and what switching-cost assumptions require validation?` | Assess churn and switching risk |
| `Compare the bundled synthetic renewal, expansion, and churn scenarios without making revenue commitments.` | Compare renewal scenarios |
| `GlobalBank license expires in 45 days. Currently 2,000 seats at $1M ARR. Usage shows they need 500 more seats. Competitor offering 30% discount.` | Account Executive: Strategic account analysis |
| `Yes, show me the competitive defense strategy.` | Customer Success Manager: Competitive defense and switching costs |
| `Yes, build the renewal and expansion proposal.` | Account Executive: Renewal and expansion proposal draft |
| `Yes, create the executive presentation with talking points.` | Account Executive: Executive presentation outline |
| `Yes, show me negotiation strategy and what approvals I need.` | Sales Leadership: Negotiation boundaries and approvals |
| `Yes, send the proposal and summarize our renewal strategy.` | Sales Leadership: Renewal strategy summary |

## What the agent does

- Analyze customer health, feature adoption, usage spikes, and waitlisted demand
- Compare competitive offers and calculate true switching costs
- Identify credible expansion opportunities tied to user demand
- Get a pricing and packaging strategy with pre‑approved concessions

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_LicenseRenewalandExpansion`) with instructions and a greeting that lists the sample prompts.
- 10 agent skills, one per operation:
  - `account-health` - "Use for the account health step of the GlobalBank renewal walkthrough, for example: GlobalBank license expires in 45 days. Currently 2,000 seats at $1M ARR. Usage shows they need 500 more seats. Competitor offering 30% discount."
  - `competitive-defense` - "Use for the competitive defense step of the GlobalBank renewal walkthrough, for example: Yes, show me the competitive defense strategy."
  - `deal-summary` - "Use for the deal summary step of the GlobalBank renewal walkthrough, for example: Yes, send the proposal and summarize our renewal strategy."
  - `executive-brief` - "Use for the executive brief step of the GlobalBank renewal walkthrough, for example: Yes, create the executive presentation with talking points."
  - `license-renewal-expansion-churn-risk` - Assess synthetic churn signals and evidence without initiating customer outreach.
  - `license-renewal-expansion-expansion-opportunities` - Identify synthetic demand signals and draft expansion options for authorized review.
  - `license-renewal-expansion-renewal-pipeline` - Review the synthetic renewal pipeline and risk bands without changing CRM or forecast records.
  - `license-renewal-expansion-revenue-impact` - Compare synthetic renewal, expansion, and churn scenarios without making revenue commitments.
  - `negotiation-plan` - "Use for the negotiation plan step of the GlobalBank renewal walkthrough, for example: Yes, show me negotiation strategy and what approvals I need."
  - `renewal-proposal` - "Use for the renewal proposal step of the GlobalBank renewal walkthrough, for example: Yes, build the renewal and expansion proposal."
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_license-renewal-expansion-operating-rules.md`
  - `aibast_license-renewal-expansion-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **License Renewal and Expansion Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Delivered a tailored renewal and expansion proposal
- Countered competitive threats with data‑driven switching‑cost analysis
- Secured expansion by validating unmet demand and aligning pricing to requirements
- Accelerated internal approvals and positioned the renewal as a multi‑year strategic partnership

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
