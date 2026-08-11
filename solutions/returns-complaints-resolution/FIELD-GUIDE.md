# Returns and Complaints Resolution Agent — customer field guide

Use this guide with the customer at the keyboard. The goal is to inspect the
portable source, reproduce the synthetic workflow, review the deployment
blueprint, and decide what production integration would require.

## Workshop mission

Turn motivated, open-minded, non-technical sales professionals into AI superheroes who can match the practical output and problem-solving pace of technical peers who are not using AI, while staying evidence-grounded, governed, and honest about what the tools proved.

## Evidence boundary

- All packaged records and outcomes are synthetic.
- Recorded cases provide qualitative workflow evidence only.
- They are not customer KPIs, measured production results, forecasts,
  commitments, or proof of a live system connection.
- A screenshot proves only the visible state in that frame.
- No image, GIF, transcript, connector result, or publication state is implied
  unless the corresponding file is present in `export-manifest.json`.

<!-- aibast-facilitator-certification:v1 -->
## Optional badge certification onboarding

This is a **facilitator-led, opt-in layer**. It does not change the workshop.
Anyone may complete the workshop anonymously with device-local progress and
skip every step in this section; anonymous completion is not badge-certified
and is not included in cohort reporting.

### Facilitator enrollment and cohort registration

1. Import
   [`AIBAST-Facilitator-Cohort-Registration.docx`](../_shared/AIBAST-Facilitator-Cohort-Registration.docx)
   into Microsoft Forms with Quick Import.
2. Restrict this form to the Microsoft organization, record the respondent
   identity, and limit response access to the approved reviewers.
3. Before delivery, submit one private response with the facilitator's
   Microsoft identity and MSIX ID, GitHub username, public non-identifying
   cohort code, private audience details, session date, module, attendee
   count, and the candidate GitHub usernames supplied for matching.
4. Each badge candidate must separately opt in. A facilitator may register a
   cohort, but cannot consent to a public profile on an attendee's behalf.
5. From the same GitHub account named in the private form, open and submit the
   [public cohort trigger](https://github.com/microsoft/aibast-agents-library/issues/new?title=%5BWorkshop+cohort%5D+Returns+and+Complaints+Resolution+Agent&body=%3C%21--+aibast-workshop-cohort%3Av1+--%3E%0A%23%23+Public+workshop+cohort+trigger%0A%0A-+Schema%3A+%60aibast-workshop-cohort%2F1.0%60%0A-+Workshop%3A+%60returns-complaints-resolution%60%0A-+Agent%3A+%60%40aibast-agents-library%2Freturns-complaints-resolution%60%0A-+Cohort+code%3A+%60REPLACE-WITH-PUBLIC-CODE%60%0A-+Session+date%3A+%60YYYY-MM-DD%60%0A-+Attendee+count%3A+%60REPLACE-WITH-NUMBER%60%0A-+Private+facilitator+form+submitted%3A+%60yes%60%0A-+Public+progress+consent%3A+%60yes%60%0A). Replace every placeholder first.

### Candidate qualification for this module

1. Import
   [`AIBAST-Badge-Qualification.docx`](../_shared/AIBAST-Badge-Qualification.docx)
   into Microsoft Forms. Allow external responses when customer attendees
   need access; keep the response workbook private to approved reviewers.
2. The candidate completes this workshop normally. The existing workshop
   achievement control may be used to submit canonical progress from the
   candidate's own signed-in GitHub account.
3. The candidate submits the private qualification form with the cohort code,
   GitHub username, workshop slug `returns-complaints-resolution`, progress-issue URL, consent,
   and answers to the manual module check below.
4. From that same GitHub account, the candidate submits the
   [public badge qualification trigger](https://github.com/microsoft/aibast-agents-library/issues/new?title=%5BBadge+qualification%5D+Returns+and+Complaints+Resolution+Agent&body=%3C%21--+aibast-badge-qualification%3Av1+--%3E%0A%23%23+Public+badge+qualification+trigger%0A%0A-+Schema%3A+%60aibast-badge-qualification%2F1.0%60%0A-+Workshop%3A+%60returns-complaints-resolution%60%0A-+Agent%3A+%60%40aibast-agents-library%2Freturns-complaints-resolution%60%0A-+Cohort+code%3A+%60REPLACE-WITH-PUBLIC-CODE%60%0A-+Achievement+progress+issue%3A+%60https%3A%2F%2Fgithub.com%2Fmicrosoft%2Faibast-agents-library%2Fissues%2FREPLACE%60%0A-+Private+qualification+form+submitted%3A+%60yes%60%0A-+Public+profile+consent%3A+%60yes%60%0A). The public
   issue is only a processing trigger; answers and private identity fields
   never belong in GitHub.
5. A reviewer matches the GitHub issue author to the private response,
   validates canonical progress, checks the answers, and applies
   `badge-qualified` only when every gate passes.

### Manual module check

Submit these answers in the **private qualification form**, never in the
public issue:

1. Which locked case IDs did you complete? Expected scope: `RCR-01, RCR-02, RCR-03, RCR-04`.
2. What determines a pass: the deterministic validator or similar wording?
3. What is the publication boundary for this workshop?
4. What must you do when required evidence is missing?
5. State one evidence-grounded result from this module and one unsupported
   claim you deliberately did not make.

### Public and private data boundary

| Public GitHub record | Private Microsoft Forms record |
| --- | --- |
| GitHub issue author/login | Microsoft identity and MSIX ID |
| Non-identifying cohort code | Customer, organization, or audience details |
| Workshop slug and canonical agent | Roster matching and internal notes |
| Session date and attendee count | Module-test answers and reviewer scoring |
| Canonical achievement IDs or issue URL | Email and other contact details |
| Processing and reviewer labels | Approved retention and deletion record |

Never place credentials, tokens, customer data, MSIX IDs, email addresses,
private rosters, or test answers in a public GitHub issue. A cohort contributes
to facilitator expertise only after `cohort-verified`; a candidate contributes
to badge-qualified reporting only after `badge-qualified`.


## Facilitator crash course — optional Brainstem track

Brainstem is the learner's local-first, inspectable agent runtime. GitHub
Copilot remains the familiar work surface; Brainstem adds persistent local
workshop context, hot-loaded Python agents, and a visible tool-calling loop.
Core setup uses the learner's GitHub account with Copilot access and does not
require a separate model API key.

For current workshop stability, this preparation guide intentionally uses the
[Grail installer](https://github.com/kody-w/rapp-installer) from `kody-w/rapp-installer`, pinned to
audited commit `5fbde1776a72715935c3d597a9ddfce28a04032b` (Brainstem `0.6.16`). It does not change
the workshop package or the default Copilot-only lane.

### Pre-work: every Brainstem-track participant installs it themselves

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/kody-w/rapp-installer/5fbde1776a72715935c3d597a9ddfce28a04032b/install.sh | bash -s -- --version 5fbde1776a72715935c3d597a9ddfce28a04032b
```

**Windows PowerShell**

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/kody-w/rapp-installer/5fbde1776a72715935c3d597a9ddfce28a04032b/install.ps1))) --version 5fbde1776a72715935c3d597a9ddfce28a04032b
```

Then, in a new terminal:

```bash
gh auth login
brainstem
```

Open `http://localhost:7071`. Before the session, verify:

```bash
curl -s localhost:7071/health | python3 -m json.tool
```

The facilitator should complete this setup first, then ask participants to run
the one-liner themselves before workshop day. Do not collect GitHub tokens or
run a shared installation on their behalf.

### Run the built-in five-minute interview loop

Use **New here? Take the 5-minute guided tour** in the Brainstem chat UI. Let
participants click and type; do not turn it into a slide lecture.

1. **Interview:** click **What can you do?** Treat the answer as a resume, not
   proof.
2. **Teach:** enter a non-sensitive preference such as
   `Remember that I prefer concise answers.` Watch the visible agent call that
   decides whether the memory is worth keeping.
3. **Reset:** clear the conversation. Explain that chat history is short-term
   context, while approved memory persists locally.
4. **Verify:** click **What do you remember?** Reinforce the operating loop:
   **claim -> test -> verify**.
5. **Inspect:** open the agents panel. Every capability is a readable local
   `*_agent.py` file; the visible inventory is the governance boundary.
6. **Trade safely (when the tour offers it):** export a removable agent,
   delete it, ask Brainstem to use it, and confirm it reports the capability
   honestly. Drag the exported file back to hot-load it without a restart.
7. **Use the registry (optional):** open the book panel, find
   `@rapp/learn_new`, and add it. Skip this step if the registry is unavailable.
8. **Create:** ask the new agent to create a small `QuoteOfTheDay` agent.
   Confirm the file appears in the agents panel.
9. **Continue:** click **What should I do next?** Summarize the method:
   **interview, teach, correct, trade, create**.

The tour automatically skips the export/delete/restore sequence when no safe
removable agent exists. Never delete memory agents or ask participants to use
customer, credential, health, financial, or other sensitive information for
the memory demonstration.

### Connect the tour to this workshop

After the tour, participants choosing the optional Brainstem lane select
**GitHub Copilot + Brainstem** in Workshop settings and use the Brainstem
Easy-mode skill already linked below. Brainstem preserves the local training
context and hot-loads specialized instructors; GitHub Copilot still performs
the build and deployment work. The same synthetic evidence, deterministic
tests, and Draft-only publication boundary apply to both lanes.

### Facilitator recovery

| Symptom | Recovery |
| --- | --- |
| `brainstem` is not found | Open a new terminal so the installer-updated PATH is loaded, then retry. |
| GitHub authentication fails | Run `gh auth login`; never ask a participant to share a token. |
| The UI does not open | Start `brainstem`, then visit `http://localhost:7071`. |
| Health check fails | Read the terminal error, correct the local prerequisite, and rerun the health check. |
| Port 7071 is occupied | Stop the conflicting local process or use the Brainstem `PORT` setting deliberately. |
| No removable agent exists | Continue; the built-in tour skips the surgery sequence. |
| Registry or agent creation is unavailable | Skip the optional step and preserve the core interview, memory, reset, inspect, and verify loop. |


## Easy mode — GitHub Copilot (default)

1. Open GitHub Copilot Chat in VS Code and select **Agent mode**.
2. Download `skills/aibast-easy-mode-copilot/SKILL.md` and drag it into the
   chat.
3. Open `EASY-MODE-COPILOT-CHAT.md`.
4. Send its two short messages in order: build and test the named solution,
   then deploy the validated Draft.
5. The skill installs and verifies the official Microsoft Copilot Studio
   plugin and supported PAC CLI, then performs discovery, testing, deployment,
   and Preview validation directly through GitHub Copilot.
6. Stop at **Draft**. Publishing remains a separate human approval gate.

## Easy mode — GitHub Copilot + Brainstem (optional)

Brainstem is the learner's personal, on-device training AI working alongside
GitHub Copilot. Copilot stays the familiar work surface; Brainstem remembers
the workshop and hot-loads the specialized instructors.

Download `skills/aibast-easy-mode-brainstem/SKILL.md`, drag it into Copilot
Chat, open `EASY-MODE-PERSONLESS.md`, and send the same two short messages.
The skill starts Brainstem, installs the generic AIBAST Workshop agent, and
continues its front-door handoffs until functional validation returns
`status: complete`.

Both lanes use the same immutable assets, locked cases, real Preview gate, and
`published: false` boundary.

Both Easy lanes preserve every recorded case prompt:

- `RCR-01` — As Customer Service Agent, summarize the anonymous return review evidence and approval boundary.
- `RCR-02` — As Customer Service Agent, classify this product concern without echoing personal information or sending a response.
- `RCR-03` — As Customer Service Agent, draft a policy-grounded option and keep all actions behind authorization.
- `RCR-04` — As Quality Team, summarize aggregate defect and return patterns without accusing any person.

## Manual mode — literal browser construction

Manual mode is for reviewers who want to reproduce the build in the browser.
Do not use PAC CLI, YAML import, or a plugin architect in Manual mode.

1. Open `manual-tutorial.html`.
2. Perform exactly one browser action per captured frame.
3. Use the linked `manual/GLOBAL-INSTRUCTIONS.md`, knowledge files, and
   `SKILL.md` files; do not retype or silently revise them.
4. Compare each action with its real screenshot and expected-result boundary.
5. Replay only the Preview cases recorded in `evals/manual-build-evidence.json`.
6. Keep the manual duplicate in **Draft**. Do not choose Publish.

## Production replacement seams

- Replace packaged synthetic inputs with an approved Approved read-only CRM case feed connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved Approved read-only order and policy evidence connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved Authorized resolution workflow connection; preserve the reviewed input and output contract.

The pilot must never claim a side effect, live lookup, or system update unless
an approved production tool returns evidence that it succeeded.

## Failure recovery

| Symptom | Recovery |
| --- | --- |
| A required evidence file is missing | Stop. Capture or restore the real file; never substitute a mockup. |
| A browser frame disagrees with the tutorial | Treat the frame and evidence JSON as authoritative, correct the package metadata, and regenerate. |
| Knowledge is still processing | Wait for ingestion to finish before Preview; do not interpret a partial answer as evidence. |
| A skill upload fails | Download the linked raw `SKILL.md`, correct the reviewed source if necessary, and retry visibly. |
| Easy and Manual inventories differ | Stop the comparison and restore exact instruction, knowledge, skill, and model parity. |
| A recorded identifier is absent | Mark the case failed and investigate; do not retry until it happens to pass. |
| Publish is offered | Stop at Draft unless a separate approver explicitly authorizes publication. |

## Evidence gates

- **Source gate:** deployment source and isolated transcripts exist.
- **Easy gate:** available Easy evidence identifies the agent, environment,
  model, inventory, cases, and Draft state.
- **Manual gate:** manual evidence passes, every browserfilm frame exists, and
  the tutorial maps one action to each frame.
- **Parity gate:** Easy and Manual use the reviewed instructions, knowledge,
  skills, model, and case identifiers.
- **Draft gate:** the package records `published: false`; publication is not
  part of scaffolding.
- **Customer gate:** replacement connections, governance, telemetry, support,
  and success measures are agreed before production.
