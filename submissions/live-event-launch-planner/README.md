# Live Event Launch Planner Agent

Help live operations, community, and marketing teams launch seasonal in-game events from one plan by building the timeline from communications approval to launch day, compiling readiness across teams with owners and status, and checking player announcements before publishing, while nothing is published or sent without a person's approval.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/live-event-launch-planner/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Live Operations Manager, Community Manager, Marketing Lead
- **Industries:** Gaming, Interactive Media

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Lay out the Frostveil Festival plan from comms approval to launch day. What comes first?` | Live Operations Manager: Launch timeline |
| `Who owns each task across live ops, community and marketing for Frostveil, and where does each one stand?` | Live Operations Manager: Cross-team readiness checklist |
| `Can we post the Frostveil player announcement yet? Show me the copy but hold it.` | Community Manager: Player announcement check |
| `What's late or blocked for Frostveil, and who needs a nudge? Don't message anyone yet.` | Marketing Lead: Launch status summary |

## What the agent does

- Build each event's timeline, from approvals to launch day
- Compile one readiness checklist across live ops and marketing
- Draft player announcements and check publishing permission
- Summarize launch status for every team in one place

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_LiveEventLaunchManualBuild`) with instructions and a greeting that lists the sample prompts.
- 4 agent skills, one per operation:
  - `announcement-check` - Use when someone asks whether the player announcement is approved and may be published, or wants to see the copy; returns a draft that is never published.
  - `launch-summary` - Use when someone asks what is late, missing, or blocked and who needs a reminder; returns reminder drafts that are never sent.
  - `launch-timeline` - Use when someone asks for an event's milestones from communications approval to launch day, or what comes first.
  - `readiness-checklist` - Use when someone asks which launch tasks each team owns, who owns them, and where each one stands.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_live-event-launch-planner-rules-and-guardrails.md`
  - `aibast_live-event-launch-planner-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Live Event Launch Planner Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Delivered smoother seasonal event launches
- Drew bigger player turnout on launch day
- Kept teams aligned without extra status meetings
- Published announcements only once approved

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-23.
