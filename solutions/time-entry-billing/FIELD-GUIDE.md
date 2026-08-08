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

## Easy mode — GitHub Copilot Chat in VS Code

1. Open this repository in VS Code.
2. Open GitHub Copilot Chat and select **Agent mode**.
3. Open `EASY-MODE-COPILOT-CHAT.md`.
4. Paste the fast-path message, or paste messages 1–5 in order.
5. Let Copilot own terminal commands, file edits, plugin calls, validation, and
   evidence gathering. Do not translate its natural-language instructions into
   shell commands for the user.
6. Stop at **Draft**. Publishing remains a separate human approval gate.

The exact copy/paste messages include every recorded case prompt:

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
