---
name: get-supplier-risk-monitoring
description: Add Supply Risk Monitoring Agent to the user's own Copilot Studio. Use when asked to get, add or deploy Supply Risk Monitoring Agent.
---

# Add Supply Risk Monitoring Agent to Copilot Studio

Do all of this yourself. The user only answers one question: yes or no.
Speak in plain words. Never show JSON, commands, file paths, account names or IDs unless asked.
Keep every reply to three short lines or fewer (the one question in step 5 may take five).

1. Get the agent and check it is the right file:
   `curl -fsSLo copilot_studio_deploy_agent.py https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/templates/copilot_studio_deploy_agent.py`
   Its SHA-256 must be `e359fc2259ef1ed98b83a76da68b5fbdd6eb35d48db2e7a98dd0e33240cb385d`. If not, stop.
2. Brainstem is optional. If `curl -fs http://localhost:7071/health` answers, it is already
   running: use it (step 2b) and do not mention it.
   If it does not answer, remember to offer it in step 5. Never push it; "no" is a fine answer.
   2a. Only if the user said yes to Brainstem in step 5, install it with the official one-liner
       (macOS/Linux: `curl -fsSL https://microsoft.github.io/aibast-agents-library/install.sh | bash`,
       Windows: `irm https://github.com/microsoft/aibast-agents-library/releases/download/installers/install.ps1 | iex`).
       Wait up to two minutes for the health check. If it never answers, say so in one line and
       carry on without it.
   2b. Hot-load the agent into Brainstem:
       `curl -fs -F file=@copilot_studio_deploy_agent.py -F sha256=e359fc2259ef1ed98b83a76da68b5fbdd6eb35d48db2e7a98dd0e33240cb385d http://localhost:7071/agents/import`
       From then on, send each step below to Brainstem in plain words with
       `curl -fs http://localhost:7071/chat -H 'Content-Type: application/json' -d '{"user_input": "..."}'`
       (for example "CopilotStudioDeploy: plan supplier-risk-monitoring") and read the `response` field.
   Without Brainstem, run the same steps with `python3 copilot_studio_deploy_agent.py <step>`.
3. Check the sign-in (`check`).
   - If `pac` is missing, install it with
     `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` and check again.
   - If not signed in, run `pac auth create --deviceCode` and tell the user:
     "Sign in with your Microsoft account in the browser window." Never ask for a password.
4. Look before you ask (`look supplier-risk-monitoring --env <environment>`). It checks which of the user's own
   systems are connected there and says which to recommend:
   - `recommend: yours`: the agent can run on their own data, read-only, with their own sign-in.
     Use `--shape yours` (to Brainstem: "shape yours") on `plan`, `deploy` and `undo` from here on.
   - `recommend: sample` and no `write_your_own`: use the sample data, as the library ships it.
     Add nothing to the commands.
   - The result has `write_your_own`: the library has no ready mapping for this solution, but one
     of the user's systems may hold the data. Do the work yourself:
     1. Read the template agent it names (same download address as the deploy agent, with that
        path) to learn what each operation answers.
     2. Write `mapping.json` in the `mapping_form` it gives, for one connected system that really
        holds that data. Read operations only. Counts and sums come from the query. Cover only the
        operations the data can answer honestly and leave the rest out.
     3. Check it: `probe supplier-risk-monitoring --env <environment> --mapping mapping.json`.
     4. Every query ran and returned data: use `--shape yours --mapping mapping.json` from here on.
        Anything failed after two tries, or the data is not there: use the sample data and say so.
   Never ask the user about fields, tables, stages or thresholds. Use the defaults `look` returns.
   Then get the plan (`plan`).
5. Ask the one question. Send one short message, five lines at most, with your choice already
   made. Pick the one wording that fits and fill it in:
   - Shaped, new: "I found <system> in <environment>, so I will set this up on your own data,
     read-only. Say 'sample' if you would rather see the demo data. Go ahead?"
   - Shaped, already installed: "<agent name> is already in <environment>, on your own <system>
     data. I will update it in place. Go ahead?"
   - Sample, new: "This adds the demo with sample data to <environment>. Go ahead?"
   - Sample, already installed: "<agent name> is already in <environment>. I will update it in
     place. Go ahead?"
   If you wrote the mapping yourself, add: "I worked out how to read <system> myself, so check the
   first answers."
   End the message with: "Experimental, not an officially supported Microsoft product."
   A yes to an "already installed" wording is the user asking to overwrite.
   Use the environment's name from `check`, not its address. Wait for yes. Do not explain how you
   are running.
   If Brainstem is not running, add one optional line to that same message, once, in these words:
   "Optional: I can also set up Brainstem, a free AI that runs on your computer. It keeps this
   agent, so later you can just say 'remove it' or 'add another one'. Say 'yes, with Brainstem'
   if you want it." Then do step 2a and 2b before deploying. Plain "yes" deploys without it.
6. Deploy it with confirmation (`deploy ... --yes`, or "confirm yes" to Brainstem).
   If it was already installed and the user said yes to updating it, add `--replace`
   ("replace yes" to Brainstem). Never replace an existing install without that yes.
   The deploy takes a few minutes and prints nothing until it ends: allow it ten minutes.
7. Say: "Done. Open Copilot Studio, pick <environment>, open Supply Risk Monitoring Agent, and ask:" and the test question.
   If it was shaped to their data, use the agent name and the test question from the deploy
   result (the name ends in "(your data)"), and add the result's `expect_says` sentence if it
   has one.
   Add: "To remove it later, just ask me."
   If Brainstem was used, add one last line: "Any time, ask me to 'start up the Brainstem' to use it
   for learning and quick prototypes."
8. If the user asks to remove it, run `undo` with confirmation.
9. If the user asks to "start up the Brainstem": if the health check answers, say it is running at
   http://localhost:7071 and open that page. Otherwise start it with `~/.brainstem/src/rapp_brainstem/start.sh`
   (Windows: `%USERPROFILE%/.brainstem/src/rapp_brainstem/start.ps1`) in the background, wait for the
   health check, then open http://localhost:7071. If Brainstem was never installed, offer to install it (step 2a).

If anything fails, say what happened in one sentence and stop.
