# Product Line Optimization — customer field guide

Use this guide with the customer at the keyboard. The goal is to install and
exercise the portable agent, inspect the Copilot Studio pilot, and identify the
production integration seams without presenting synthetic figures as outcomes.

## Evidence already established

- Strict-isolation Brainstem: PLO-01 through PLO-04 passed (4/4).
- Copilot Studio Preview: PLO-01 through PLO-04 passed in kodyv8.
- Agent identity: `Product Line Optimization Pilot`,
  `aibast_ProductLineOptimizationPilot`,
  bot `643beb44-c693-44b6-b58d-7631cd1f190c`.
- Model and inventory: Sonnet46, four skills, two knowledge files.
- Deployment state: seven changes pushed; **Draft, not published**.
- Manual agent: `Product Line Manual Build`, bot
  `ee4836e5-16a4-4d23-8bd6-342155d3a2af`; 23 screenshots and 4/4 Preview
  cases captured; **Draft, not published**.

`evals/transcripts.json`, `evals/copilot-studio-preview-evidence.json`, and
`evals/manual-build-evidence.json` record the source, Easy, and Hard evidence.

## Easy mode — Copilot-assisted

**Audience:** customer participants, sellers, and specialists.

The customer opens GitHub Copilot Agent mode and pastes the Easy-mode prompt
from the library or `quest.html`. Copilot performs the terminal work: checks the
platform, installs or reuses Brainstem, downloads the portable source, verifies
it, starts the service, and runs the smoke case.

Do not continue until the evidence shows:

1. Brainstem health is `ok`.
2. `ProductionLineOptimizationAgent` is the loaded tool.
3. The smoke prompt called that exact tool.
4. The answer names Polymer Molding Line C and Electronics Assembly Line A.

Then use the four canonical prompts:

- PLO-01: “Which production line needs attention today, and what is driving the loss?”
- PLO-02: “Where is the bottleneck on each line, and which station should the plant team address first?”
- PLO-03: “Give me the practical options to improve throughput without hiding the quality tradeoffs.”
- PLO-04: “Translate the current line performance into a day, swing, and night shift plan.”

Say explicitly: “The workflow is real; every figure is synthetic planning
evidence and is not a customer KPI.”

## Hard mode — literal browser construction

Hard mode does **not** use PAC CLI, Copilot Studio YAML import, or the plugin
architect. Open `manual-tutorial.html` and reproduce the agent through the
Copilot Studio browser:

1. Create a blank agent and name the manual duplicate.
2. Enter and save the reviewed instructions.
3. Remove default web search.
4. Upload both knowledge files.
5. Upload all four `SKILL.md` files individually.
6. Select Claude Sonnet 4.6.
7. Audit four skills, two knowledge files, and no web search.
8. Run PLO-01 through PLO-04 in Preview.
9. Capture the Draft state and do not publish.

The captured 23-frame sequence is declared in
`screenshots/manual/browserfilm.json` and rendered as
`screenshots/manual/manual-build-walkthrough.gif`.

## Production replacement seams

The pilot is self-contained. For production, replace:

- synthetic line and order context with approved Dynamics 365 ERP access;
- synthetic station and downtime records with approved Azure IoT Hub, MES, or
  plant API access;
- packaged reporting views with governed Power BI semantic models;
- recommendation-only outputs with approved workflows that require human
  authorization before maintenance, scheduling, staffing, or investment action.

Preserve the routing, evidence boundary, quality tradeoff, non-invention rule,
and “recommend only” safety contract. Never claim a side effect occurred unless
the production tool returns evidence of success.

## Failure recovery

| Symptom | Recovery |
| --- | --- |
| Brainstem health is unavailable | Have Copilot rerun the official installer and policy-clean launcher from `deployment.json`. |
| Source verification fails | Stop. Refresh the registry and recheck the raw source path before installing. |
| Wrong agent answers | Remove other solution agents and rerun strict isolation; fix routing rather than retrying blindly. |
| Knowledge remains processing | Wait. Do not run Preview until both files are accepted and available. |
| A skill upload fails | Redownload the raw `SKILL.md`, preserve that exact filename, and upload the file rather than its folder or `.mcs.yml`. |
| Required Preview identifier is missing | Treat the case as failed. Check instructions, knowledge, skill inventory, model, and web-search removal; then start a fresh Preview conversation. |
| Model is unavailable | Use an approved substitute, record it, and avoid claiming model parity. |
| Publish is offered | Stop at Draft unless publication has a separate explicit approval and governance record. |

## Evidence gates

Before calling the package reproducible, retain:

- portable-agent source identity and strict-isolation transcripts;
- environment ID, schema, bot ID, model, component inventory, and push result;
- all four Preview prompts, responses, expected identifiers, and timestamps;
- 23 real manual screenshots using the declared filenames;
- manual and Easy-mode Draft status;
- unresolved connector, security, data-governance, and human-approval work.

Do not call the pilot production-ready and do not translate synthetic deltas,
costs, gains, or projected scores into customer KPI claims.
