# Time Entry and Billing Agent — Copilot-only Easy mode comparison

## 1. Attach the shared skill

Download [SKILL.md](https://raw.githubusercontent.com/kody-w/aibast-agents-library/easy-mode-copilot-chat-pilot/skills/aibast-easy-mode/SKILL.md), open GitHub
Copilot Chat in VS Code, select **Agent mode**, and drag `SKILL.md` into the
chat.

This comparison lane intentionally omits Brainstem so workshop participants can
answer “why not just use GitHub Copilot by itself?” The attached skill carries
the discovery, testing, deployment, and validation harness so the attendee
still uses short messages instead of supplying URLs and mechanics.

Then send these two short messages:

## 2. Build and test without Brainstem

```text
Give me Time Entry and Billing using Easy Mode without Brainstem and test it for me.
```

## 3. Deploy the validated Draft

```text
Deploy it into Copilot Studio for me.
```

## Completion boundary

Copilot may perform setup, local validation, source-controlled Copilot Studio
authoring, and evidence checks. It must stop at **Draft**. Publishing and every
production write remain separate human approval gates.
