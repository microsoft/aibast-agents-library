# Worked example: equipment requests, from a discovery call

A synthetic discovery call (`pack/samples/discovery-call.txt`): a facilities team tracks equipment
requests in a shared spreadsheet that's often locked, approvals over $500 wait on the plant manager
by email for up to a week, and requesters never know where their order is.

## One command

```bash
brainstem-proto new --transcript pack/samples/discovery-call.txt "equipment requests"
```

What happened (2026-10-11, `pack/test-pack.sh`):

| Step | Result |
|---|---|
| Project created from the template, own ports picked (7100/7101) | ✓ |
| Its Brainstem started (the unchanged kernel, loading only `Discovery` and `Idea`), app started | ✓ |
| `check.sh`: tests, Brainstem, app, live round trip | 4 of 4 ✓ |
| RAPP Step 2: `DISCOVERY.md` written from the transcript | ✓ |
| Kernel fingerprint before and after | identical (`3553b660…`, 0 modified files) |
| Total time | 20 seconds |

## What DISCOVERY.md said (excerpt)

- **Problem:** requests sit in a locked spreadsheet, approvals can take a week, requesters call the
  ops lead for status.
- **Users (roles, no names):** floor worker, ops lead, plant manager, purchasing.
- **MVP poke:** "a phone form that submits a request, which then appears on an open-requests list
  by line, with the $500 rule deciding who approves it." Agents: Request Intake, Approval Router,
  Status Tracker.
- **Honest gaps:** "shorter approval waits (direction stated, no target given)"; open question:
  "is the $500 threshold per request or per line item?"

## Then

Gate 1: the person reads `DISCOVERY.md` and says yes (or edits it). Their AI, following `AGENTS.md`,
builds only the first slice on made-up data, runs `check.sh` until it's ✓, and tells them what to
show the customer. That's RAPP Steps 1 to 4 on a laptop, before lunch.
