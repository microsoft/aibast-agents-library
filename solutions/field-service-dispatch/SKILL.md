---
name: get-field-service-dispatch
description: Add Field Service Dispatch Agent to the user's own Copilot Studio. Use when asked to get, add or deploy Field Service Dispatch Agent.
---

# Add Field Service Dispatch Agent to Copilot Studio

Do all of this yourself. The user only answers one question: yes or no.
Speak in plain words. Never show JSON, commands, file paths, account names or IDs unless asked.
Keep every reply to three short lines or fewer.

1. Get the agent and check it is the right file:
   `curl -fsSLo copilot_studio_deploy_agent.py https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/templates/copilot_studio_deploy_agent.py`
   Its SHA-256 must be `fe3046c1372ee78812bddd29fba26d159c798916960ca9ab68d855e598eb4095`. If not, stop.
2. Brainstem is optional. If `curl -fs http://localhost:7071/health` answers, it is already
   running: use it (step 2b) and do not mention it.
   If it does not answer, remember to offer it in step 5. Never push it; "no" is a fine answer.
   2a. Only if the user said yes to Brainstem in step 5, install it with the official one-liner
       (macOS/Linux: `curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash`,
       Windows: `irm https://github.com/microsoft/aibast-agents-library/releases/download/installers/install.ps1 | iex`).
       Wait up to two minutes for the health check. If it never answers, say so in one line and
       carry on without it.
   2b. Hot-load the agent into Brainstem:
       `curl -fs -F file=@copilot_studio_deploy_agent.py -F sha256=fe3046c1372ee78812bddd29fba26d159c798916960ca9ab68d855e598eb4095 http://localhost:7071/agents/import`
       From then on, send each step below to Brainstem in plain words with
       `curl -fs http://localhost:7071/chat -H 'Content-Type: application/json' -d '{"user_input": "..."}'`
       (for example "CopilotStudioDeploy: plan field-service-dispatch") and read the `response` field.
   Without Brainstem, run the same steps with `python3 copilot_studio_deploy_agent.py <step>`.
3. Check the sign-in (`check`).
   - If `pac` is missing, install it with
     `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` and check again.
   - If not signed in, run `pac auth create --deviceCode` and tell the user:
     "Sign in with your Microsoft account in the browser window." Never ask for a password.
4. Get the plan for field-service-dispatch in the active environment from the check (`plan`).
5. Tell the user in one or two sentences what will happen and where, plus any note.
   Ask: "Go ahead?" Wait for yes. Do not explain how you are running.
   If Brainstem is not running, add one optional line, once, in these words:
   "Optional: I can also set up Brainstem, a free AI that runs on your computer. It keeps this
   agent, so later you can just say 'remove it' or 'add another one'. Say 'yes, with Brainstem'
   if you want it." Then do step 2a and 2b before deploying. Plain "yes" deploys without it.
6. Deploy it with confirmation (`deploy ... --yes`, or "confirm yes" to Brainstem).
   Never replace an existing install unless the user asked to overwrite.
7. Say: "Done. Open Copilot Studio, pick <environment>, open Field Service Dispatch Agent, and ask:" and the test question.
   Add: "To remove it later, just ask me."
   If Brainstem was used, add one last line: "Any time, ask me to 'start up the Brainstem' to use it
   for learning and quick prototypes."
8. If the user asks to remove it, run `undo` with confirmation.
9. If the user asks to "start up the Brainstem": if the health check answers, say it is running at
   http://localhost:7071 and open that page. Otherwise start it with `~/.brainstem/src/rapp_brainstem/start.sh`
   (Windows: `%USERPROFILE%/.brainstem/src/rapp_brainstem/start.ps1`) in the background, wait for the
   health check, then open http://localhost:7071. If Brainstem was never installed, offer to install it (step 2a).

If anything fails, say what happened in one sentence and stop.
