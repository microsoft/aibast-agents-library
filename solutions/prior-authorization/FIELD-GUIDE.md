# Prior Authorization Agent — customer field guide

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

## Native r4 Manual pilot verified; historical import withheld

On 2026-09-13, all four unchanged locked prompts passed once each in separate fresh native Preview conversations on one fully saved/reopened r4 Manual build using Claude Sonnet 4.6. The complete policy, all four definitions and both Ready sources matched. All 18 student checkpoints have personally reviewed references with their actual construction, replacement and readback scopes; they are not a continuous fresh-build film. The same agent remained Draft. No native publication, live integration or production certification is claimed.

See [evals/manual-pilot-review.json](evals/manual-pilot-review.json).


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
   [public cohort trigger](https://github.com/microsoft/aibast-agents-library/issues/new?title=%5BWorkshop+cohort%5D+Prior+Authorization+Agent&body=%3C%21--+aibast-workshop-cohort%3Av1+--%3E%0A%23%23+Public+workshop+cohort+trigger%0A%0A-+Schema%3A+%60aibast-workshop-cohort%2F1.0%60%0A-+Workshop%3A+%60prior-authorization%60%0A-+Agent%3A+%60%40aibast-agents-library%2Fprior-authorization%60%0A-+Cohort+code%3A+%60REPLACE-WITH-PUBLIC-CODE%60%0A-+Session+date%3A+%60YYYY-MM-DD%60%0A-+Attendee+count%3A+%60REPLACE-WITH-NUMBER%60%0A-+Private+facilitator+form+submitted%3A+%60yes%60%0A-+Public+progress+consent%3A+%60yes%60%0A). Replace every placeholder first.

### Candidate qualification for this module

1. Import
   [`AIBAST-Badge-Qualification.docx`](../_shared/AIBAST-Badge-Qualification.docx)
   into Microsoft Forms. Allow external responses when customer attendees
   need access; keep the response workbook private to approved reviewers.
2. The candidate completes this workshop normally. The existing workshop
   achievement control may be used to submit canonical progress from the
   candidate's own signed-in GitHub account.
3. The candidate submits the private qualification form with the cohort code,
   GitHub username, workshop slug `prior-authorization`, progress-issue URL, consent,
   and answers to the manual module check below.
4. From that same GitHub account, the candidate submits the
   [public badge qualification trigger](https://github.com/microsoft/aibast-agents-library/issues/new?title=%5BBadge+qualification%5D+Prior+Authorization+Agent&body=%3C%21--+aibast-badge-qualification%3Av1+--%3E%0A%23%23+Public+badge+qualification+trigger%0A%0A-+Schema%3A+%60aibast-badge-qualification%2F1.0%60%0A-+Workshop%3A+%60prior-authorization%60%0A-+Agent%3A+%60%40aibast-agents-library%2Fprior-authorization%60%0A-+Cohort+code%3A+%60REPLACE-WITH-PUBLIC-CODE%60%0A-+Achievement+progress+issue%3A+%60https%3A%2F%2Fgithub.com%2Fmicrosoft%2Faibast-agents-library%2Fissues%2FREPLACE%60%0A-+Private+qualification+form+submitted%3A+%60yes%60%0A-+Public+profile+consent%3A+%60yes%60%0A). The public
   issue is only a processing trigger; answers and private identity fields
   never belong in GitHub.
5. A reviewer matches the GitHub issue author to the private response,
   validates canonical progress, checks the answers, and applies
   `badge-qualified` only when every gate passes.

### Manual module check

Submit these answers in the **private qualification form**, never in the
public issue:

1. Which locked case IDs did you complete? Expected scope: `PA-01, PA-02, PA-03, PA-04`.
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

This preparation guide uses the canonical
[AIBAST Brainstem installer](https://github.com/microsoft/aibast-agents-library). The former upstream Grail
installer is not used by this Microsoft/AIBAST workshop path.

### Pre-work: every Brainstem-track participant installs it themselves

**macOS / Linux**

```bash
curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash
```

**Windows PowerShell**

```powershell
irm https://microsoft.github.io/aibast-agents-library/install.ps1 | iex
```

The one-liner installs the runtime, starts Brainstem, opens GitHub
authorization when needed, and opens `http://localhost:7071`. Participants do
not run `gh auth login` or `brainstem` separately. Before the session, verify:

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

Historical assisted/Easy and source-agent transcripts remain separate from current native Manual r4 acceptance. Their old pass flags and the incomplete Prior Authorization Pilot import archive do not reproduce or certify this Manual build. No current Easy-lane regression or native import is accepted.

Both Easy lanes preserve every recorded case prompt:

- `PA-01` — What evidence is present or missing for synthetic request SYN-AUTH-001?
- `PA-02` — Show the synthetic criteria checklist for SYN-AUTH-001 without deciding medical necessity.
- `PA-03` — What workflow state is recorded for SYN-AUTH-001, and what does it not mean?
- `PA-04` — Prepare a minimum-necessary reconsideration evidence outline for SYN-AUTH-001.

## Manual mode — literal browser construction

Manual mode is for reviewers who want to reproduce the build in the browser.
Do not use PAC CLI, YAML import, or a plugin architect in Manual mode.

1. Open `manual-tutorial.html`.
2. Follow each action and its explicit evidence boundary; an open step is not captured proof.
3. Use the linked `manual/GLOBAL-INSTRUCTIONS.md`, knowledge files, and
   `SKILL.md` files; do not retype or silently revise them.
4. Compare each action with its reviewed reference and expected-result boundary.
5. Run each unchanged locked Preview prompt once in a separate fresh conversation.
6. Resume the same owned manual agent without duplicate uploads; keep it in **Draft**. Do not choose Publish.

### Current Manual preparation

1. For a new build, follow the 18 steps in order. When resuming, use the existing owned Prior Authorization Manual Draft; do not create a duplicate or attach another copy of an unchanged file.
2. Use exactly the seven inputs in evals/manual-inputs-r4.json and the unchanged locked cases. Download links target the staging workshop that carries this repair, not an older Microsoft-main payload.
3. Use Claude Sonnet 4.6, four frontmatter-named skills, two knowledge sources, zero configured Tools and no default web search. Production connections are future seams only.
4. For an existing mismatched knowledge file, remove only its assignment from this Draft, then add the verified replacement through Add knowledge and wait for Ready. The details editor does not replace file contents.
5. For an existing mismatched skill, use its Replace action once. Replacement closes the old dialog; reopen the same skill and compare the full new name, description and body before assuming failure or uploading again.
6. Paste the entire policy with normal keyboard events, allow it to settle, blur, Save, leave through Agents and reopen the same Draft. Compare the full policy and all four definitions; a visible editor value or Save click alone is insufficient.
7. Reference steps 3, 6-10 document actual existing-Draft repairs. Step 9 retains its unchanged r2 capture; steps 1, 2, 5 and 11 retain their real initial-build provenance. Captions do not claim new first-time uploads.
8. Use New chat for each exact prompt, verify greeting-only history and an exact composer value, and submit once. Review the complete final answer, actual matching skill/search activity, citations and footer. Preserve failures; a material source change requires a separately labelled full regression.
9. Report only the requested operation. Recorded state, evidence presence and causal rationale are separate facts; absent rationale is not an invitation to invent a cause or append a corrective-action requirement.
10. Finish by confirming the same agent is Draft. Do not choose Publish. The input ZIP is not an importable solution or a standalone guide; use the separately published current tutorial and reviewed references.


## Production replacement seams

- Replace packaged synthetic inputs with an approved Approved read-only EHR or FHIR evidence source connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved Approved payer policy source connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved Microsoft Teams utilization-review coordination connection; preserve the reviewed input and output contract.

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
