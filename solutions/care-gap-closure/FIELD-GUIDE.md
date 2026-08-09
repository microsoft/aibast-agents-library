# Care Gap Closure Agent — customer field guide

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

- `CG-01` — Which synthetic quality measure has the largest evidence-review queue?
- `CG-02` — Organize the synthetic evidence-review cohorts without clinical risk scoring.
- `CG-03` — Draft outreach for the synthetic screening measure, but do not send it or state that anyone is eligible.
- `CG-04` — Show the qualitative source-completeness dashboard and its limitations.

## Hard mode — literal browser construction

Hard mode is for reviewers who want to reproduce the build in the browser.
Do not use PAC CLI, YAML import, or a plugin architect in Hard mode.

1. Open `manual-tutorial.html`.
2. Perform exactly one browser action per captured frame.
3. Use the linked `manual/GLOBAL-INSTRUCTIONS.md`, knowledge files, and
   `SKILL.md` files; do not retype or silently revise them.
4. Compare each action with its real screenshot and expected-result boundary.
5. Replay only the Preview cases recorded in `evals/manual-build-evidence.json`.
6. Keep the manual duplicate in **Draft**. Do not choose Publish.

## Production replacement seams

- Replace packaged synthetic inputs with an approved Dynamics 365 care-coordination workflow connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved Microsoft Teams review and approval connection; preserve the reviewed input and output contract.

The pilot must never claim a side effect, live lookup, or system update unless
an approved production tool returns evidence that it succeeded.

## Failure recovery

| Symptom | Recovery |
| --- | --- |
| A required evidence file is missing | Stop. Capture or restore the real file; never substitute a mockup. |
| A browser frame disagrees with the tutorial | Treat the frame and evidence JSON as authoritative, correct the package metadata, and regenerate. |
| Knowledge is still processing | Wait for ingestion to finish before Preview; do not interpret a partial answer as evidence. |
| A skill upload fails | Download the linked raw `SKILL.md`, correct the reviewed source if necessary, and retry visibly. |
| Easy and Hard inventories differ | Stop the comparison and restore exact instruction, knowledge, skill, and model parity. |
| A recorded identifier is absent | Mark the case failed and investigate; do not retry until it happens to pass. |
| Publish is offered | Stop at Draft unless a separate approver explicitly authorizes publication. |

## Evidence gates

- **Source gate:** deployment source and isolated transcripts exist.
- **Easy gate:** available Easy evidence identifies the agent, environment,
  model, inventory, cases, and Draft state.
- **Manual gate:** manual evidence passes, every browserfilm frame exists, and
  the tutorial maps one action to each frame.
- **Parity gate:** Easy and Hard use the reviewed instructions, knowledge,
  skills, model, and case identifiers.
- **Draft gate:** the package records `published: false`; publication is not
  part of scaffolding.
- **Customer gate:** replacement connections, governance, telemetry, support,
  and success measures are agreed before production.
