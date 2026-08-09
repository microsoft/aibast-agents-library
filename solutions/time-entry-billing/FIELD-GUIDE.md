# Time Entry and Billing Agent — customer field guide

Use this guide with the customer at the keyboard. The goal is to inspect the
portable source, reproduce the synthetic workflow, review the deployment
blueprint, and decide what production integration would require.

## Evidence boundary

- All packaged records and outcomes are synthetic.
- Recorded cases provide qualitative workflow evidence only.
- They are not customer KPIs, measured production results, forecasts,
  commitments, or proof of a live system connection.
- A screenshot proves only the visible state in that frame.
- No image, GIF, transcript, connector result, or publication state is implied
  unless the corresponding file is present in `export-manifest.json`.

## Easy mode — with Brainstem (default)

Brainstem is the learner's personal, on-device training AI working alongside
GitHub Copilot. Copilot stays the familiar work surface; Brainstem remembers
the workshop and hot-loads the specialized instructors.

1. Open GitHub Copilot Chat in VS Code and select **Agent mode**.
2. Download `skills/aibast-easy-mode-brainstem/SKILL.md` and drag it into the
   chat.
3. Open `EASY-MODE-PERSONLESS.md`.
4. Send its two short messages in order: build and test the named solution,
   then deploy the validated Draft.
5. The attached skill starts Brainstem and installs the reusable AIBAST Easy
   Mode agent into the learner's personal, on-device training AI.
6. Easy Mode resolves and hot-loads the task-specific workshop cartridge.
7. Brainstem retrieves the reviewed GitHub assets, hot-loads the business
   agent, proves it locally, drives Draft setup, and returns front-door actions.
8. Copilot executes each handoff and sends evidence back until Brainstem
   returns `status: complete`.
9. Stop at **Draft**. Publishing remains a separate human approval gate.

## Easy mode — without Brainstem (comparison)

Download `skills/aibast-easy-mode-copilot/SKILL.md` instead. That skill fixes
the harness to GitHub Copilot alone, so the participant uses the exact same two
messages without repeatedly saying “without Brainstem.” It performs discovery,
testing, deployment, and Preview validation directly through GitHub Copilot.

## Teaching comparison

| Dimension | With Brainstem | GitHub Copilot only |
| --- | --- | --- |
| Strength | Persistent state, reusable hot-loaded agents, autonomous handoffs, and a durable verdict | Familiar VS Code entry point with no additional engine for the participant to understand |
| Tradeoff | Requires the governed local Brainstem runtime | Orchestration and state live primarily in the active Copilot session |
| Person's role | Set the destination and read the engine verdict | Attach the skill, steer through Copilot, and read its verdict |
| Workshop lesson | Shows the personless harness and reusable engine model | Shows how far Copilot Agent mode can go with a strong portable skill |

Both approaches are valid for getting started. They use the same immutable
assets, locked cases, real Preview gate, and `published: false` boundary.

Both Easy lanes preserve every recorded case prompt:

- `TEB-01` — What billable work is still blocked from this close, and what has to happen before it can move?
- `TEB-02` — Give me the month-end billing rollup by project and consultant without treating it as posted revenue.
- `TEB-03` — Which time cards would fail our billing review because of narrative, hours, rate, or budget concerns?
- `TEB-04` — Prepare the invoice support that is actually ready, and keep anything without the right approval or milestone evidence out.
- `TEB-05` — What evidence is missing on the disputed hours, and what is the safest resolution path before we go back to the clients?

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

- Replace packaged synthetic inputs with an approved Dynamics 365 connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved SharePoint connection; preserve the reviewed input and output contract.
- Replace packaged synthetic inputs with an approved Microsoft Teams connection; preserve the reviewed input and output contract.

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
