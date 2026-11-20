---
name: get-financial-advisor-copilot
description: Add Financial Advisor Agent to the user's own Copilot Studio. Use when asked to get, add or deploy Financial Advisor Agent.
---

# Add Financial Advisor Agent to Copilot Studio

Do all of this yourself. The user only answers one question: yes or no.
Speak in plain words. Never show JSON, commands, file paths, account names or IDs unless asked.
Keep every reply to three short lines or fewer.

1. Get the agent and check it is the right file:
   `curl -fsSLo copilot_studio_deploy_agent.py https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/templates/copilot_studio_deploy_agent.py`
   Its SHA-256 must be `3f6b555e3e028a8e66a32270ff09ecb085c3a55d7a86a67b24f89f63de3e6d43`. If not, stop.
2. Brainstem is optional. If `curl -fs http://localhost:7071/health` answers, it is already
   running: use it (step 2b) and do not mention it.
   If it does not answer, remember to offer it in step 5. Never push it; "no" is a fine answer.
   2a. Only if the user said yes to Brainstem in step 5, install it with the official one-liner
       (macOS/Linux: `curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash`,
       Windows: `irm https://github.com/microsoft/aibast-agents-library/releases/download/installers/install.ps1 | iex`).
       Wait up to two minutes for the health check. If it never answers, say so in one line and
       carry on without it.
   2b. Hot-load the agent into Brainstem:
       `curl -fs -F file=@copilot_studio_deploy_agent.py -F sha256=3f6b555e3e028a8e66a32270ff09ecb085c3a55d7a86a67b24f89f63de3e6d43 http://localhost:7071/agents/import`
       From then on, send each step below to Brainstem in plain words with
       `curl -fs http://localhost:7071/chat -H 'Content-Type: application/json' -d '{"user_input": "..."}'`
       (for example "CopilotStudioDeploy: plan financial-advisor-copilot") and read the `response` field.
   Without Brainstem, run the same steps with `python3 copilot_studio_deploy_agent.py <step>`.
3. Check the sign-in (`check`).
   - If `pac` is missing, install it with
     `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` and check again.
   - If not signed in, run `pac auth create --deviceCode` and tell the user:
     "Sign in with your Microsoft account in the browser window." Never ask for a password.
4. Look before you ask (`look financial-advisor-copilot --env <environment>`). It checks which of the user's own
   systems are connected there and says which to recommend:
   - `recommend: yours`: the agent can run on their own data, read-only, with their own sign-in.
     Use `--shape yours` (to Brainstem: "shape yours") on `plan`, `deploy` and `undo` from here on.
   - `recommend: sample`: use the sample data, as the library ships it. Add nothing to the commands.
   - It found another system (`other_systems_connected`) and lists what the agent `needs`: you may
     write a mapping for that system in the same form as the `fit.systems` entry in
     `solutions/financial-advisor-copilot/deployment.json` (connector, one read operation, one query per operation,
     the rule in words) and pass it with `--mapping`. Read operations only. If you are not sure it
     is right, use the sample data and say so.
   Never ask the user about fields, tables, stages or thresholds. Use the defaults `look` returns.
   Then get the plan (`plan`).
5. Tell the user in one or two sentences what will happen and where, with your choice already made.
   - Shaped: "I found <system> in <environment>, so I will set this up on your own data, read-only.
     Say 'sample' if you would rather see the demo data. Go ahead?"
   - Sample: "This adds the demo with sample data to <environment>. Go ahead?"
   - If the plan says `already_installed: true`, say so in the same question instead of asking
     twice: "<name> is already in <environment>. I will update it in place. Go ahead?" A yes to
     that is the user asking to overwrite.
   Both are experimental and not an officially supported Microsoft product: say so once.
   This is the only question. Send it as one message and wait for yes. Do not explain how you
   are running. Use the environment's name from `check`, not its address.
   If Brainstem is not running, add one optional line to that same message, once, in these words:
   "Optional: I can also set up Brainstem, a free AI that runs on your computer. It keeps this
   agent, so later you can just say 'remove it' or 'add another one'. Say 'yes, with Brainstem'
   if you want it." Then do step 2a and 2b before deploying. Plain "yes" deploys without it.
6. Deploy it with confirmation (`deploy ... --yes`, or "confirm yes" to Brainstem).
   If it was already installed and the user said yes to updating it, add `--replace`
   ("replace yes" to Brainstem). Never replace an existing install without that yes.
   The deploy takes a few minutes and prints nothing until it ends: allow it ten minutes.
7. Say: "Done. Open Copilot Studio, pick <environment>, open Financial Advisor Agent, and ask:" and the test question.
   If it was shaped to their data, use the agent name and the test question from the deploy
   result (the name ends in "(your data)"), and if the result has `expect`, add the numbers
   they should see, for example "You should see 128 open deals."
   Add: "To remove it later, just ask me."
   If Brainstem was used, add one last line: "Any time, ask me to 'start up the Brainstem' to use it
   for learning and quick prototypes."
8. If the user asks to remove it, run `undo` with confirmation.
9. If the user asks to "start up the Brainstem": if the health check answers, say it is running at
   http://localhost:7071 and open that page. Otherwise start it with `~/.brainstem/src/rapp_brainstem/start.sh`
   (Windows: `%USERPROFILE%/.brainstem/src/rapp_brainstem/start.ps1`) in the background, wait for the
   health check, then open http://localhost:7071. If Brainstem was never installed, offer to install it (step 2a).

If anything fails, say what happened in one sentence and stop.
