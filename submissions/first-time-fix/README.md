# First-Time Fix Agent

Help contact center and field service teams resolve connection issues on the first call by guiding the right fix for each customer's service, checking local network work and past visits before a technician is sent, and preparing the technician's job when a visit is needed, while every booking stays with a person to confirm.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/first-time-fix/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Contact Center Agent, Field Service Dispatcher
- **Industries:** Telecommunications, Broadband & Cable

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `The customer on Alder Grove Service keeps dropping. What guided fix should I walk them through right now?` | Contact Center Agent: Guided connection fix |
| `Is there any network work near Meadow Lane that could explain the outage?` | Contact Center Agent: Local work check |
| `What did the last technician find at Alder Grove Service?` | Field Service Dispatcher: Previous visit review |
| `If the light stays red, which technician should go to Alder Grove and what should they prepare? Don't book it yet.` | Field Service Dispatcher: Technician booking draft |

## What the agent does

- Guide agents through the right fix for each customer's service
- Check local work and past visits before sending a technician
- Prepare each job with the fault history and the parts to bring
- Keep a person in control of every technician booking

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_FirstTimeFixManualBuild`) with instructions and a greeting that lists the sample prompts.
- 4 agent skills, one per operation:
  - `guided-fix` - Use when a contact center agent asks which fix to walk the customer through during the call, or what the service status is.
  - `local-work-check` - Use when the agent asks whether planned or emergency network work near the service could explain the issue.
  - `technician-booking` - Use when someone asks which technician to send and what job preparation is needed; returns a booking draft that is never booked.
  - `visit-history` - Use when someone asks what earlier technician visits found or what the technician notes say.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_first-time-fix-rules-and-guardrails.md`
  - `aibast_first-time-fix-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **First-Time Fix Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Solved more connection issues on the first call
- Avoided unneeded truck rolls during area outages
- Sent technicians who arrived prepared for the fault
- Put technicians where they add the most value

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-23.
