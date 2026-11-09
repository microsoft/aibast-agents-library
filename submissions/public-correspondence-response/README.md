# Public Correspondence Agent

Answer every part of every resident enquiry from approved precedent: triage the correspondence queue, break multi-part letters into separate questions, cite approved past responses, route unanswered points to the owning team, and prepare a reviewable draft reply.

This is a working Copilot Studio agent built on a fixed, fully synthetic dataset. It needs no connections, so you can import it and start chatting in the test pane. It comes from the [AIBAST Agents Library](https://microsoft.github.io/aibast-agents-library/solutions/public-correspondence-response/quest.html), Microsoft's catalog of industry agent templates.

## Who it is for

- **Personas:** Correspondence Officer, Correspondence Team Lead, Knowledge Owner
- **Industries:** State and Local Government

## What you can try

Send one prompt at a time in a new chat.

| Prompt | What happens |
| --- | --- |
| `What correspondence do I need to answer this week?` | Correspondence Officer: Correspondence queue triage |
| `Break down the scanned letter from E. Okafor into its separate questions.` | Correspondence Officer: Enquiry breakdown |
| `Which approved past responses already answer each question in the Okafor letter?` | Correspondence Officer: Approved precedent match |
| `Who owns each part of the Okafor letter, and what should I ask the team about the part we can't answer?` | Correspondence Team Lead: Team routing and referral |
| `Draft the reply to the Okafor letter for my review.` | Correspondence Officer: Cited draft reply |
| `Property and Land will send approved wording for the Okafor compensation question. How do we add it to the precedent library so nobody has to ask again?` | Knowledge Owner: Precedent library update |

## What the agent does

- Triages letters, emails, forms and phone notes into one queue
- Splits multi-part enquiries so every question is answered
- Finds approved past responses for each question and cites them
- Routes unanswered points to the owning team with the question

## What the solution contains

- One CLI-authored Copilot Studio agent (`aibast_PublicCorrespondenceManualBuild`) with instructions and a greeting that lists the sample prompts.
- 6 agent skills, one per operation:
  - `break-down-enquiry` - Use when an officer wants one letter split into its separate questions so none is missed.
  - `draft-response` - Use when an officer asks for a draft reply that answers every question with citations.
  - `find-precedents` - Use when an officer asks which approved past responses already answer each question.
  - `inbox-queue` - Use when a correspondence officer asks what is waiting to be answered, soonest due first.
  - `library-update` - Use when someone asks how newly approved wording becomes reusable so the question is not re-asked.
  - `route-and-refer` - Use when an officer asks who owns each part and what to ask the team about an unanswered part.
- 2 knowledge files holding the synthetic records and operating rules:
  - `aibast_public-correspondence-response-rules-and-guardrails.md`
  - `aibast_public-correspondence-response-synthetic-records.md`
- No connectors, flows, or connection references. Nothing to bind after import.

## Prerequisites and import

Use a Dataverse environment with Copilot Studio access and support for CLI-authored agents. You need permission to import an unmanaged solution.

1. Import the unmanaged solution through Power Platform Solutions. Use the ready ZIP, or package the contents of `solution/` yourself with `solution.xml` and `customizations.xml` at its root. Do not include the gallery metadata or this README.
2. Open **Public Correspondence Agent** in Copilot Studio and start a new test chat. The greeting lists the prompts above.
3. Publish and share the agent when you are ready for others to use it.

Running examples consumes Copilot Credits.

## Outcomes this pattern targets

- Every question in every letter is addressed in the draft
- Approved wording is reused with a citation instead of rewritten
- Gaps reach the right team in minutes and become precedent

## Boundaries

- Every organization, person, record, date, and amount is invented. The agent labels its evidence as synthetic and never claims access to a live system.
- The agent prepares drafts and recommendations. It does not book, change, send, or approve anything; a person confirms every action.
- To use it on real data, replace the synthetic knowledge files with your own sources and bind approved connections after your security and business-owner review.

### Before you rely on it

This is a sample, not a production system. Its outputs are illustrative, may be wrong or incomplete, and are not professional advice (medical, legal, financial, tax, safety, regulatory or otherwise). A qualified person must review every output before it informs a real decision, record, message or action.

This submission contains an editable **unmanaged** solution exported from Copilot Studio. Source environment export recorded 2026-10-08.
