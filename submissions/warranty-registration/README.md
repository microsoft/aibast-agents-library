# Warranty and Registration Agent

Give equipment dealers one place to check warranty coverage, pre-check claims, validate serials and prepare product registrations, so covered repairs move faster and no unit misses its registration window.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/warranty-registration/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Dealer Service Managers, Warranty Administrators, Dealer Sales Staff
- **Industries:** Manufacturing

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `How does our dealership's warranty coverage look right now?` | Dealer Service Manager: Coverage overview |
| `A customer brought in welding station WS-25-4471 with a failed wire feeder. Is the repair covered?` | Dealer Service Manager: Claim pre-check |
| `Pull the full warranty record for tire changer TC-90-3307.` | Warranty Administrator: Unit warranty record |
| `We just sold welding station WS-25-4520. Check the serial before we register it.` | Dealer Sales Staff: Serial check |
| `Prepare the registration for WS-25-4520, but don't submit anything.` | Dealer Sales Staff: Registration draft |
| `Which units should we offer extended coverage to this month?` | Dealer Sales Staff: Extended-coverage offers |

## What the agent does

- Shows coverage, expirations and pending registrations in one view
- Pre-checks repair coverage and pulls full unit records
- Validates serials and drafts registrations for review
- Drafts extended-coverage offers for units ending soon

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_WarrantyAndManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `claim-precheck` - Use when a dealer service manager asks something like "A customer brought in welding station WS-25-4471 with a failed wire feeder. Is the repair covered"
  - `coverage-overview` - Use when a dealer service manager asks something like "How does our dealership's warranty coverage look right now"
  - `extension-offers` - Use when a dealer sales staff asks something like "Which units should we offer extended coverage to this month"
  - `registration-draft` - Use when a dealer sales staff asks something like "Prepare the registration for WS-25-4520, but don't submit anything"
  - `unit-record` - Use when a warranty administrator asks something like "Pull the full warranty record for tire changer TC-90-3307"
  - `validate-serial` - Use when a dealer sales staff asks something like "We just sold welding station WS-25-4520. Check the serial before we register it"
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_warranty-registration-rules-and-guardrails.md`
  - `aibast_warranty-registration-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Warranty and Registration Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Fewer rejected warranty claims
- Registrations completed inside the window
- More extensions sold before coverage ends

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
