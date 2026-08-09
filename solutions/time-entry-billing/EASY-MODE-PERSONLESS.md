# Time Entry and Billing Agent — personless Easy mode

## 1. Attach the shared skill

Download [SKILL.md](https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/skills/aibast-easy-mode/SKILL.md), open GitHub
Copilot Chat in VS Code, select **Agent mode**, and drag `SKILL.md` into the
chat. The skill defaults to Brainstem and owns startup, agent acquisition,
testing, deployment, browser validation, and the final verdict.

Brainstem is the learner's personal, on-device training AI. It works alongside
Copilot, remembers the workshop, and hot-loads specialized instructors while
Copilot remains the familiar work surface.

Then send these two short messages:

## 2. Build and test the solution

```text
Give me Time Entry and Billing using Easy Mode and test it for me.
```

## 3. Deploy the validated Draft

```text
Deploy it into Copilot Studio for me.
```

## What pulls the harness

1. The attached skill starts the installed Brainstem, finds
   `@aibast-agents-library/easy-mode` in the AIBAST registry, and imports it
   through `/agents/import`.
2. `AIBASTEasyModeAgent` resolves the named solution, integrity-checks and
   hot-loads its task-specific workshop cartridge, then asks that cartridge to
   hot-load and test the business agent.
3. The same Easy Mode agent remembers the active solution, so “Deploy it” runs
   the validated Draft flow without the attendee repeating URLs or context.
4. Copilot executes any real front-door handoff returned by Brainstem, sends
   the captured Preview evidence back, and continues until Brainstem returns
   `status: complete`.
5. The final gate requires **Draft** and `published: false`.

Reusable Easy Mode agent: https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/agents/@aibast-agents-library/templates/easy_mode_agent.py

Task workshop cartridge: https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/easy/time_entry_billing_workshop_agent.py

This is the default Easy path. The person sets the destination and reads the
verdict; Brainstem + Copilot pull the harness.
