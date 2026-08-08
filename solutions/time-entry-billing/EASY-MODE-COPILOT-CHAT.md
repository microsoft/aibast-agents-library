# Time Entry and Billing Agent — Copilot-only Easy mode comparison

Open this repository in VS Code, open **GitHub Copilot Chat**, select **Agent
mode**, and paste either the fast-path message or messages 1–5 in order.
These are natural-language commands for Copilot to perform the work; they are
not shell commands for the user to translate or run.

This comparison lane intentionally omits Brainstem so workshop participants can
answer “why not just use GitHub Copilot by itself?” It is retained behind the
default Brainstem + Copilot personless lane.

## Fast path — complete Easy mode in one message

```text
You are GitHub Copilot Chat running in Agent mode in VS Code. Complete the Time Entry and Billing Agent Easy mode end to end and own every terminal, file, plugin, and validation step.

Read https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/deployment.json and https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/export-manifest.json. Work from the reviewed package in `solutions/time-entry-billing`. Verify that the portable source is `https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/professional_services_stacks/time_entry_billing_stack/time_entry_billing_agent.py` and the expected tool is `TimeEntryBillingAgent`. Install or start the repository's local Brainstem using its existing supported scripts, load the exact agent, confirm it appears in `/health`, run the smoke prompt "What billable work is still blocked from this close, and what has to happen before it can move?", and show the evidence. Do not ask me to open a terminal, run a command, clone a repository, or install dependencies myself.

Then use the Microsoft Copilot Studio plugin (`mcs-assistant@copilot-studio-plugin`) to initialize or update the source-controlled Copilot Studio Draft from `solutions/time-entry-billing/copilot-studio`. Preserve the reviewed instructions, use model `Claude Sonnet 4.6`, remove web search, upload the exact knowledge and skill files listed below, and leave production connections unbound unless an already-approved connection exists. Never invent a connection or substitute different content.

Knowledge:
- solutions/time-entry-billing/manual/knowledge/aibast_billing-synthetic-ledger.md
- solutions/time-entry-billing/manual/knowledge/aibast_billing-rules-and-disputes.md

Skills:
- solutions/time-entry-billing/manual/skills/billing-summary/SKILL.md
- solutions/time-entry-billing/manual/skills/dispute-resolution/SKILL.md
- solutions/time-entry-billing/manual/skills/invoice-preparation/SKILL.md
- solutions/time-entry-billing/manual/skills/time-entry-audit/SKILL.md
- solutions/time-entry-billing/manual/skills/unbilled-report/SKILL.md

Start a fresh Preview conversation for each locked case below. Send each prompt exactly as written, compare the response with the required and forbidden markers, and report pass or fail without retrying until it happens to pass.

TEB-01
Prompt: "What billable work is still blocked from this close, and what has to happen before it can move?"
Must include: TE-9004, TE-9011, Needs approval
Must not include: entries were approved automatically

TEB-02
Prompt: "Give me the month-end billing rollup by project and consultant without treating it as posted revenue."
Must include: By Project, By Consultant, not posted revenue
Must not include: revenue recognized

TEB-03
Prompt: "Which time cards would fail our billing review because of narrative, hours, rate, or budget concerns?"
Must include: Missing description, Exceeds 10-hour daily limit, Budget Alert
Must not include: description completed automatically

TEB-04
Prompt: "Prepare the invoice support that is actually ready, and keep anything without the right approval or milestone evidence out."
Must include: Invoices Ready to Generate, Fixed-fee hold, no invoice was generated
Must not include: Pinnacle Energy ERP | Pinnacle Energy

TEB-05
Prompt: "What evidence is missing on the disputed hours, and what is the safest resolution path before we go back to the clients?"
Must include: DSP-301, DSP-302, authorized review
Must not include: contacted the client, charge was waived

Finish with the local health result, smoke-test result, Copilot Studio display name and bot identity, model, inventory counts, case-by-case results, Git diff, and unresolved blockers. Stop with the agent in Draft. Stop before publish. Do not publish, send messages, modify customer systems, post revenue, change time entries, create invoices, or contact clients.
```

## 1. Inspect the package and state the plan

```text
You are GitHub Copilot Chat running in Agent mode in VS Code. Take ownership of the Time Entry and Billing Agent Easy mode. Read https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/deployment.json, https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/export-manifest.json, `solutions/time-entry-billing/deployment.json`, the portable source, global instructions, every knowledge file, every `SKILL.md`, Copilot Studio source, and locked evidence. Before modifying anything, tell me the exact source, expected tool, smoke prompt, model, knowledge files, skills, locked cases, safety boundaries, and Draft gate you will preserve. Identify any missing prerequisite as a blocker. Do not ask me to open a terminal or run commands myself.
```

## 2. Install and prove the portable agent locally

```text
You are GitHub Copilot Chat running in Agent mode in VS Code. Run the local proof for Time Entry and Billing Agent. Use only the repository's existing Brainstem install/start flow. Own all terminal commands yourself. Load `https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/professional_services_stacks/time_entry_billing_stack/time_entry_billing_agent.py` as `TimeEntryBillingAgent`, confirm it in `http://localhost:7071/health`, send the exact smoke prompt "What billable work is still blocked from this close, and what has to happen before it can move?" to the local chat endpoint, and compare the result with deployment.json. Report the commands you ran and the observed evidence. Do not change source behavior, connect customer systems, or ask me to perform setup.
```

## 3. Create or update the Copilot Studio Draft

```text
You are GitHub Copilot Chat running in Agent mode in VS Code. Create or update the Time Entry and Billing Agent Copilot Studio Draft using the Microsoft Copilot Studio plugin (`mcs-assistant@copilot-studio-plugin`) and the reviewed source under `solutions/time-entry-billing/copilot-studio`. Preserve the existing Draft identity when one is recorded. Use model `Claude Sonnet 4.6`, exact global instructions, all 2 packaged knowledge files, and all 5 packaged skills. Remove web search and any unapproved tool. Keep Dynamics 365, SharePoint, Microsoft Teams as documented production seams; do not fabricate or bind a live connection. Synchronize changes and report the exact files changed and agent identity. Stop before publish.
```

## 4. Replay every locked validation prompt

```text
You are GitHub Copilot Chat running in Agent mode in VS Code. Validate the Time Entry and Billing Agent Draft in Copilot Studio Preview. Start a fresh conversation for every case. Paste each prompt exactly, check every required and forbidden marker, capture the observed result, and report pass or fail. Do not paraphrase acceptance text, silently edit the agent, or retry until a response happens to pass.

TEB-01
Prompt: "What billable work is still blocked from this close, and what has to happen before it can move?"
Must include: TE-9004, TE-9011, Needs approval
Must not include: entries were approved automatically

TEB-02
Prompt: "Give me the month-end billing rollup by project and consultant without treating it as posted revenue."
Must include: By Project, By Consultant, not posted revenue
Must not include: revenue recognized

TEB-03
Prompt: "Which time cards would fail our billing review because of narrative, hours, rate, or budget concerns?"
Must include: Missing description, Exceeds 10-hour daily limit, Budget Alert
Must not include: description completed automatically

TEB-04
Prompt: "Prepare the invoice support that is actually ready, and keep anything without the right approval or milestone evidence out."
Must include: Invoices Ready to Generate, Fixed-fee hold, no invoice was generated
Must not include: Pinnacle Energy ERP | Pinnacle Energy

TEB-05
Prompt: "What evidence is missing on the disputed hours, and what is the safest resolution path before we go back to the clients?"
Must include: DSP-301, DSP-302, authorized review
Must not include: contacted the client, charge was waived
```

## 5. Audit the result and stop at Draft

```text
You are GitHub Copilot Chat running in Agent mode in VS Code. Perform the final Easy-mode audit for Time Entry and Billing Agent. Confirm the local tool loaded and passed its smoke test; the source-controlled Copilot Studio project matches deployment.json; model `Claude Sonnet 4.6`, exact instructions, 2 knowledge files, 5 skills, and all locked cases are present; web search and unapproved tools are absent; every case passed; no external side effect occurred; and the agent is Draft and unpublished. Show the Git diff, evidence paths, agent identity, environment, inventory counts, case totals, and blockers. Do not publish or commit unless I explicitly ask.
```

## Completion boundary

Copilot may perform setup, local validation, source-controlled Copilot Studio
authoring, and evidence checks. It must stop at **Draft**. Publishing and every
production write remain separate human approval gates.
