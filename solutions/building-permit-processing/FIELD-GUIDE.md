# Building Permit Processing — customer field guide

This guide is for a seller, specialist, architect, or customer champion running
the Building Permit Processing solution with the customer at the keyboard.

The goal is not to show a slide. The goal is to let the customer install the
portable agent, experience the synthetic workflow, inspect the production
blueprint, and decide how it should connect to their environment.

## What is proven

The approved one-pager promises:

1. Intake classification and completeness checks.
2. Intelligent routing to review teams.
3. Proactive application tracking and updates.
4. Inspector access and assignment visibility.

Those promises are mapped in `evals/onepager-map.json`.

The Python agent was loaded by itself into a freshly installed Brainstem and all
five persona-language cases passed. The exact responses are stored in
`evals/transcripts.json`.

The same five cases passed against the published Copilot Studio pilot in kodyv8.
Those results are stored in `evals/copilot-studio-transcripts.json`.

## Customer session: Easy mode

**Audience:** nontechnical customer participants and account teams.

**Customer requirement:** GitHub Copilot Agent mode in VS Code and a browser for
the supported GitHub/Copilot authentication step.

**Customer does not need to:**

- open a terminal,
- clone a repository,
- install Brainstem manually,
- find an agent file,
- calculate a checksum,
- start a server,
- or construct an API request.

### Facilitation sequence

1. Open the solution in `library.html`.
2. Open **Architecture → Easy mode**.
3. Give the customer control of the keyboard.
4. Have the customer paste **Try locally — one prompt, no terminal** into
   GitHub Copilot Agent mode.
5. Let Copilot perform every command. Intervene only if a browser asks the
   customer to approve GitHub/Copilot authentication.
6. Do not continue until Copilot reports:
   - Brainstem health is `ok`,
   - the downloaded source matches the registry SHA-256,
   - `BuildingPermitProcessingAgent` is loaded,
   - and the smoke prompt fired that exact agent.
7. Ask the customer to choose one of the five example prompts and compare the
   live answer with the M365 Copilot-style canned demo.

### Conversation starters

- “Which permit applications have been sitting too long, and which resident is
  going to complain first?”
- “Anything at the front counter I should not be accepting today?”
- “The restaurant fit-out on Harbor Way just came in. Who needs to review it
  and when is it due back?”
- “My front desk is drowning in status calls. What can we send out today so
  people stop calling?”
- “What inspections are on the board for the solar job, and who is covering
  them?”

### What to say while it runs

- “This is a portable Python agent, not a pre-recorded bot response.”
- “The data is synthetic, but it has the shape and domain language of a permit
  system.”
- “The production seam is the data accessor. The workflow does not need to be
  rewritten when the customer replaces the static records.”
- “Copilot Studio is the default deployment surface, not the only possible
  host.”

## Customer session: Copilot Studio promotion

Use the second Easy-mode prompt only after the local workflow is accepted.

The customer supplies:

- target Power Platform environment ID,
- approved publisher prefix,
- and any required browser authentication.

Copilot performs:

1. PAC version and authentication checks.
2. `pac copilot init` with `cli-copilot` authoring.
3. Modern YAML authoring through the Copilot Studio Architect workflow.
4. Component review and validation.
5. Pull-before-push synchronization.
6. `pac copilot push`.
7. The five canonical acceptance prompts.

Publishing remains a separate, explicit approval because it makes the agent live
for users it is shared with.

## Hard mode

Hard mode exists for technical reviewers and AI skeptics who want to reproduce
every browser action without the plugin architect or PAC CLI.

Open `screenshots/copilot-assisted-walkthrough.gif` to see the real kodyv8
plugin-assisted Easy-mode sequence.

Open `manual-tutorial.html` for the complete Microsoft Learn-style Hard-mode
walkthrough. It includes every action, expected result, screenshot,
troubleshooting note, and raw GitHub download.

### Manual sequence

1. Create a blank Copilot Studio agent.
2. Enter and save the reviewed global instructions.
3. Remove default web search.
4. Upload the two GitHub-hosted knowledge files.
5. Upload all seven GitHub-hosted `SKILL.md` files individually.
6. Correct any validation error instead of silently skipping a skill.
7. Set the same model used by the Easy-mode pilot.
8. Audit the complete skill and knowledge inventory.
9. Run the exact canonical backlog prompt in Preview.
10. Verify permit `BP-2025-0104`, `Metro School District`, and the overdue
    escalation appear in the answer.
11. Keep the duplicate manual agent in Draft unless publication is separately
    approved.

The validated manual build is `Building Permit Manual Build`, bot ID
`0d89cb6b-4276-46f9-b453-478b2ddde265`.

## Production replacement seams

The pilot deliberately has no customer connection dependencies.

For production:

- replace permit records and case state with Dynamics 365 Customer Service,
- replace plan and policy documents with SharePoint-backed tools or knowledge,
- replace draft communications and field coordination with approved Microsoft
  Teams or workflow tools,
- preserve the same routing, clarification, safety, and output contracts.

The agent must never claim a side effect occurred unless the production tool
returns evidence that it succeeded.

## Failure recovery

| Symptom | Response |
| --- | --- |
| Brainstem health is unavailable | Have Copilot rerun the official installer and policy-clean launcher from the deployment recipe. |
| Downloaded hash differs | Stop. Do not install the file. Refresh `registry.json` and verify the source URL and branch. |
| The wrong agent answers | Remove other solution agents and rerun the strict-isolation test. Fix the tool description rather than retrying blindly. |
| PAC push reports conflict | Pull, inspect the changed files, reconcile deliberately, then push again. |
| Agentic runtime returns 404 | The agent is not published or the schema/environment is wrong. Verify before publishing. |
| Copilot Studio answer misses a stable entity | Treat the deployment as failed. Fix instructions/skills and rerun the identical canonical case. |

## Evidence that must leave the session

- source-agent SHA-256,
- PowerPoint SHA-256,
- isolated Brainstem transcripts,
- Copilot Studio transcripts,
- target environment and schema name,
- pull/push/publish results,
- screenshots of the manual Copilot Studio path,
- unresolved connector or governance work.

Do not call the solution production-ready without this evidence.
