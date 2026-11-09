# Personalized Shopping Agent

Deliver intelligent personal styling to strengthen customer experience, increase revenue, and elevate associate efficiency at scale.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/personalized-shopping-assistant/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Personal Shoppers, Clienteling Specialists, Retail Managers
- **Industries:** Retail

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Suggest transparent options for Synthetic Shopper A using only stated preferences.` | Recommend products transparently |
| `Summarize Synthetic Shopper B’s opt-in preferences without inferring anything else.` | Summarize stated preferences |
| `Show the synthetic size-level availability and verification gate for the sweater.` | Check availability safely |
| `Draft coordinated outfit options and transparent totals without ordering anything.` | Draft coordinated outfits |

## What the agent does

- Build a complete customer style profile to guide faster, more consistent recommendations
- Generate curated outfit options suited to the customer’s needs
- Check real‑time availability and propose strong alternatives
- Apply loyalty benefits automatically to present a clear, optimized price

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PersonalizedShoppingPilot`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `opt-in-style-profile-summary` - Helps a Clienteling Specialist summarize stated preferences without sensitive inference.
  - `pricing-offer` - "Use when a personal shopper asks something like \"As Personal Shopper, what is the best offer I can give Jennifer with her loyalty benefits\""
  - `read-only-shopping-inventory-check` - Gives a Retail Manager a synthetic size-level inventory snapshot with a verification gate.
  - `review-only-outfit-builder` - Drafts coordinated outfit options for a Personal Shopper without ordering or reserving items.
  - `session-summary` - "Use when a clienteling specialist asks something like \"As Clienteling Specialist, wrap up Jennifer's styling session and prepare the updates for her profile\""
  - `transparent-product-recommendations` - Gives a Personal Shopper explainable product options based only on stated synthetic preferences.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_shopping-assistant-rules-and-safety.md`
  - `aibast_shopping-assistant-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Personalized Shopping Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Delivered polished, occasion- specific outfits in minutes
- Raised consistency and quality across all stylist recommendations
- Increased conversion with better suggestions and pricing clarity
- Reduced returns via closer size matching and aligned preferences
- Enabled seamless follow‑ups

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
