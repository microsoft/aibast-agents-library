---
name: deploy-to-copilot-studio
description: Deploy an AIBAST Agents Library solution (for example Tiered Huddle Board) into the user's own Copilot Studio environment with their own sign-in. Use when someone asks to deploy, install or try a library solution in Copilot Studio, or to remove one.
---

# Deploy a library solution to Copilot Studio

You help the user put one library solution into their own Copilot Studio
environment. Everything runs through one script with the user's own Power
Platform sign-in. Show each command before you run it.

## Get the script (once)

```bash
curl -fsSLo copilot_studio_deploy_agent.py https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/templates/copilot_studio_deploy_agent.py
```

It needs Python 3 and the Power Platform CLI (`pac`). If `pac` is missing,
tell the user how to install it (`dotnet tool install --global
Microsoft.PowerApps.CLI.Tool`, or the Windows installer) and stop.

## Steps

1. **Sign in.** Run `python3 copilot_studio_deploy_agent.py check`.
   If it says they are not signed in, have them run
   `pac auth create --deviceCode` themselves and finish the sign-in in
   their browser. Never ask for or type a password.
2. **Pick an environment.** Run `python3 copilot_studio_deploy_agent.py envs`
   and ask which one to use. Suggest a test environment, not production.
3. **Check first.** Run
   `python3 copilot_studio_deploy_agent.py plan <solution> --env "<environment>"`.
   Tell the user, in plain words, what will happen and every note (already
   installed, missing connections). Nothing changes in this step.
4. **Deploy only after the user says yes.** Run the same command with
   `deploy ... --yes`. Add `--replace` only if they asked to overwrite an
   existing install.
5. **Report.** Give the summary, then the `test_question` for them to ask in
   Copilot Studio's test pane.
6. **Undo, if asked.** `python3 copilot_studio_deploy_agent.py undo <solution> --env "<environment>" --yes`
   after the user confirms.

## Rules

- Never pass `--yes` until the user has seen the plan and agreed.
- Never store or print tokens or passwords.
- If a step fails, read the summary to the user and stop. Do not retry with
  different flags on your own.
- Solution names are the library's folder names, such as
  `tiered-huddle-board`.
