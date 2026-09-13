# Portfolio Rebalancing Agent — GitHub Copilot Easy mode

## Evidence lane boundary

Historical assisted/Easy and deterministic Brainstem evidence is retained separately; it is not native Manual r5 final-answer acceptance. No current Easy-lane regression or fresh-from-empty Manual construction is certified.

The steps below describe the Easy workflow, not a newly accepted run. For the current Manual build and its open gates, use [the Manual tutorial](manual-tutorial.html) and [the dated review](evals/manual-pilot-review.json).

## 1. Attach the Copilot-only skill

Download [SKILL.md](https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode-copilot/SKILL.md), open GitHub
Copilot Chat in VS Code, select **Agent mode**, and drag `SKILL.md` into the
chat.

The attached skill carries the discovery, testing, deployment, and validation
harness directly in GitHub Copilot, so the attendee still uses the same short
messages instead of supplying URLs or mechanics. Before deployment it installs
and verifies the official `microsoft/copilot-studio-plugin`, its
`mcs-assistant@copilot-studio-plugin` capabilities, and a supported PAC CLI.

Then send these two short messages:

## 2. Build and test the solution

```text
Give me Portfolio Rebalancing using Easy Mode and test it for me.
```

## 3. Deploy the validated Draft

```text
Deploy it into Copilot Studio for me.
```

## Completion boundary

Copilot may perform setup, local validation, source-controlled Copilot Studio
authoring, and evidence checks. It must stop at **Draft**. Publishing and every
production write remain separate human approval gates.
