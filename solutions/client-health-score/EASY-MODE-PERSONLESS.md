# Client Health Score Agent — personless Easy mode

## 1. Attach the Brainstem skill

Download [SKILL.md](https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode-brainstem/SKILL.md), open GitHub
Copilot Chat in VS Code, select **Agent mode**, and drag `SKILL.md` into the
chat. This skill fixes the lane to Brainstem and owns startup, agent
acquisition, testing, deployment, browser validation, and the final verdict.

Brainstem is the learner's personal, on-device training AI. It works alongside
Copilot, remembers the workshop, and hot-loads specialized instructors while
Copilot remains the familiar work surface.

Then send these two short messages:

## 2. Build and test the solution

```text
Give me Client Health Score using Easy Mode and test it for me.
```

## 3. Deploy the validated Draft

```text
Deploy it into Copilot Studio for me.
```

## What pulls the harness

1. The attached skill starts the installed Brainstem, finds
   `@aibast-agents-library/workshop` in the AIBAST registry, and imports it
   through `/agents/import`.
2. `AIBASTWorkshopAgent` resolves the named solution from `registry.json`,
   retrieves its standard package, and hot-loads and tests the business agent.
3. The same generic engine remembers the active solution, so “Deploy it” runs
   the validated Draft flow without the attendee repeating URLs or context.
4. Copilot executes any real front-door handoff returned by Brainstem, sends
   the captured Preview evidence back, and continues until Brainstem returns
   `status: complete`.
5. The final gate requires **Draft** and `published: false`.

Generic workshop engine: https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/agents/@aibast-agents-library/templates/workshop_agent.py

The person sets the destination and reads the
verdict; Brainstem + Copilot pull the harness.
