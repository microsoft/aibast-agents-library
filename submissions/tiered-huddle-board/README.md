# Tiered Huddle Board Agent

Help a hospital run its daily tiered huddles from one live board: every lane and clock, what is past target and waiting on the person asking, escalations drafted with the restarted clock, the reason and the people to page, mitigated issues kept open until the person who raised them confirms the fix held, and the decisions the leadership huddle needs today.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/tiered-huddle-board/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Nurse Manager, Department Director, Chief Nursing Officer
- **Industries:** Healthcare, Hospitals & Health Systems

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `I'm between patients. Show me the huddle board: what's past target and what's waiting on me?` | Nurse Manager: Whole board view |
| `4 West can't fix the IV pump problem at our level. Get the escalation ready for the next tier, but don't page anyone until I confirm.` | Nurse Manager: Escalation draft |
| `Biomed fixed the bed alarm in room 412 yesterday. Can we take it off the board?` | Nurse Manager: Closure check |
| `For the 10:30 leadership huddle, what needs a decision from us today?` | Chief Nursing Officer: Leadership huddle decisions |

## What the agent does

- Show every lane, clock and item waiting on the person asking
- Draft each escalation with its reason, new clock and pages
- Keep mitigated items open until the originator confirms
- Bring leadership every decision with its reason and clock

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_TieredHuddleBoardManualBuild`) with instructions and a greeting that lists the sample prompts.
- 4 agent skills, one per operation:
  - `board-view` - Use when a nurse manager, charge nurse or director asks for the huddle board, every lane and clock, what is past target, or what is waiting on them.
  - `closure-check` - Use when someone asks whether a fixed or mitigated issue can be closed or taken off the board; mitigated is not closed until the person who raised it confirms the fix held.
  - `escalation-draft` - Use when someone says the unit or department cannot fix an issue and asks to escalate it, move it up a tier, or who would be paged; returns an escalation draft that is never sent.
  - `leadership-decisions` - Use when a leader asks what the 10:30 leadership huddle needs to decide today, with the reason and clock for each item.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_tiered-huddle-board-rules-and-guardrails.md`
  - `aibast_tiered-huddle-board-synthetic-records.md`
- 1 tools:
  - `Work IQ MCP Server` - 

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

This package declares these connections. Importing asks you to pick or create a connection for each; nothing is read until you do:

- Work IQ MCP (`shared_workiqmcp`)

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Tiered Huddle Board Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Ran every huddle tier from one live board
- Escalated unresolved issues faster, with nothing lost
- Closed issues only when the fix had truly held
- Gave the 10:30 huddle a clear list of decisions

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-29.
