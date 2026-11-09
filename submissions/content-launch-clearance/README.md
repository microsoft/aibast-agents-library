# Content Launch Clearance Agent

Help programming, distribution, and rights teams confirm where, when, and on which platform a title can launch by citing the exact contract clause behind each clearance answer, showing the distribution window and any holdback that blocks an earlier date, and checking what is still missing before rights approval, while every approval stays with the rights team.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/content-launch-clearance/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Programming Manager, Distribution Lead, Rights & Clearances Lead
- **Industries:** Media & Entertainment, Streaming, Broadcasting

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `Can we put Silver Harbor on our streaming service in the UK, and which contract clause says so?` | Programming Manager: Launch clearance |
| `Programming wants Paper Lantern live in Canada in about a month. Is there a holdback that blocks that date?` | Distribution Lead: Distribution window and holdback |
| `Is Northern Signal ready to come to the rights team for sign-off? What is still missing?` | Rights & Clearances Lead: Approval readiness draft |

## What the agent does

- Confirm where, when, and on which platforms each title can launch
- Cite the exact contract clause behind every clearance answer
- Flag holdbacks that block earlier launch dates
- Show which approvals are still needed before launch

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_ContentLaunchManualBuild`) with instructions and a greeting that lists the sample prompts.
- 3 agent skills, one per operation:
  - `approval-readiness` - Use when someone asks whether a launch request is ready for rights-team approval or what is still missing; returns an approval request draft that is never submitted.
  - `distribution-window` - Use when someone asks when a title's rights window opens, which holdback applies, or whether a requested launch date is open.
  - `launch-clearance` - Use when someone asks whether a title can launch in a territory on the owned streaming service, or which contract clause supports the answer.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_content-launch-clearance-rules-and-guardrails.md`
  - `aibast_content-launch-clearance-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Content Launch Clearance Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Brought titles to audiences faster
- Confirmed launch dates with the contract terms cited
- Caught holdbacks before they became launch problems
- Freed rights teams to focus on deals, not lookups

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-23.
