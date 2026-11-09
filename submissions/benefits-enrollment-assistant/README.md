# Benefits Enrollment Agent

Guide employees through open enrollment and life-event benefit changes by explaining the enrollment window and change rules, comparing plan costs for their coverage tier, checking whether their providers are in network, tracking required documents, and preparing a draft election, while eligibility decisions and submissions stay with the employee and benefits staff.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/benefits-enrollment-assistant/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Employee, Benefits Specialist, HR Operations Staff
- **Industries:** Cross-Industry

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `When does open enrollment close, and what can I change?` | Employee: Enrollment window explanation |
| `We just had a baby. What benefit changes can I make, and by when?` | Employee: Life-event change rules |
| `Compare the three medical plans for family coverage.` | Employee: Plan cost comparison |
| `Are Lakeside Family Clinic and Riverbend Pediatrics in network on each plan?` | Employee: Provider network check |
| `What documents do I still need to send?` | Employee: Document checklist |
| `Draft my election changes, but don't submit anything.` | Employee: Election draft preview |
| `What benefits deadlines should I put on my calendar?` | Employee: Personal deadline list |

## What the agent does

- Explains the enrollment window and change rules plainly
- Compares tier costs and checks provider networks
- Tracks documents and deadlines so changes are not missed
- Prepares a draft election for the employee to submit

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_BenefitsEnrollmentManualBuild`) with instructions and a greeting that lists the sample prompts.
- 7 agent skills, one per operation:
  - `compare-plans` - Use when an employee asks to compare medical plan costs, deductibles, out-of-pocket maximums, and networks for their coverage tier.
  - `deadline-reminders` - Use when an employee asks which benefits deadlines are coming up and in what order.
  - `document-checklist` - Use when an employee or benefits specialist asks which supporting documents are received, missing, and when they are due.
  - `election-draft` - Use when an employee asks to draft or preview election changes; the draft stays Not Submitted and shows the per-paycheck cost change.
  - `enrollment-window` - Use when an employee asks when open enrollment opens or closes, how many days are left, or what can change.
  - `life-event-change` - Use when an employee states a life event such as a new child, marriage, loss of other coverage, or divorce and asks what can change and by when.
  - `provider-network` - Use when an employee asks whether their doctors or clinics are in network on each plan.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_benefits-enrollment-assistant-rules-and-guardrails.md`
  - `aibast_benefits-enrollment-assistant-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Benefits Enrollment Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Fewer missed windows: each employee sees their own deadline
- Clearer choices: tier costs and network gaps side by side
- Lighter help desk: consistent, sourced answers

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
