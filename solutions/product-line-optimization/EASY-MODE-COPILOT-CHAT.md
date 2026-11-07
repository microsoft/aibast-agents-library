# Product Line Optimization Agent — GitHub Copilot Easy mode

## 1. Brief Copilot with one line

Open GitHub Copilot Chat in VS Code, select **Agent mode**, and send:

```text
Go and read https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode-copilot/SKILL.md and run the Product Line Optimization workshop for me.
```

Copilot reads [SKILL.md](https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode-copilot/SKILL.md) itself;
nothing to download.

The skill it read carries the discovery, testing, deployment, and validation
harness directly in GitHub Copilot, so the attendee still uses the same short
messages instead of supplying URLs or mechanics. Before deployment it installs
and verifies the official `microsoft/copilot-studio-plugin`, its
`mcs-assistant@copilot-studio-plugin` capabilities, and a supported PAC CLI.

Then send these two short messages:

## 2. Build and test the solution

```text
Give me Product Line Optimization using Easy Mode and test it for me.
```

## 3. Deploy the validated Draft

```text
Deploy it into Copilot Studio for me.
```

## Questions before you show it

Ask the guide in the same chat. It first asks whether you need background on
the idea or need to get it ready to show, then answers from the library's own
files:

```text
Is Product Line Optimization Agent real, and can I demo it?
```

- **Is it real:** whether it came from the catalog or the field, and its test
  and Copilot Studio Preview results.
- **How to demo it:** this workshop, Easy mode, the demo video if one is
  published, and the one-pager.
- **Customer results:** only published proof. If none is published, the guide
  says so plainly.
- **Who to talk to:** the library request form and the weekly office hours
  listed on the library site.
- **Assets:** request the one-pager or video through the library request form.

If several library solutions fit what you describe, the guide lists them with
one line each and asks which one you want.

## Adapt it to another industry

If nothing fits your industry, ask the guide to adapt this solution. It
explains each step as it goes:

1. It says which solution is closest to your need and why.
2. It lists the changes it would make for your industry (roles, terms,
   systems and synthetic sample data), each with a reason, and asks you to
   confirm. Nothing is written yet.
3. After you confirm, it writes the adapted copy on your computer and gives
   you a summary of every change.

The original solution and its tests are never edited, and the sample data stays
synthetic.

```text
We work in <your industry>. Adapt Product Line Optimization Agent for us.
```

## Completion boundary

Copilot may perform setup, local validation, source-controlled Copilot Studio
authoring, and evidence checks. It must stop at **Draft**. Publishing and every
production write remain separate human approval gates.
