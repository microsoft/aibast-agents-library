# Time Entry and Billing Agent — personless Easy mode

Open GitHub Copilot Chat in VS Code, select **Agent mode**, and paste this one
sentence:

```text
Use my local RAPP Brainstem at http://localhost:7071: hot-load https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/easy/time_entry_billing_workshop_agent.py through /agents/import, ask /chat to run the Time Entry and Billing Agent workshop, execute every handoff it returns until Brainstem reports complete, and stop before publish.
```

## What pulls the harness

1. GitHub Copilot checks the local Brainstem and imports the raw workshop
   cartridge through `/agents/import`.
2. Brainstem invokes `TimeEntryBillingWorkshop`, which downloads the reviewed
   GitHub assets, verifies their pinned source hash, and hot-loads the business
   agent into its live agents directory.
3. The workshop cartridge runs every locked local case, prepares or pushes the
   Copilot Studio Draft through the active PAC environment, and returns the
   exact front-door actions still required.
4. Copilot performs those actions, sends the captured Preview evidence back to
   Brainstem, and continues until Brainstem returns `status: complete`.
5. The final gate requires **Draft** and `published: false`.

Workshop cartridge: https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/solutions/time-entry-billing/easy/time_entry_billing_workshop_agent.py

This is the default Easy path. The person sets the destination and reads the
verdict; Brainstem + Copilot pull the harness.
