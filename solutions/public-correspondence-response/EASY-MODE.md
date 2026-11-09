# Public Correspondence Agent — Easy Mode

## 1. Brief Copilot with one line

Open GitHub Copilot Chat, select **Agent mode**, and send:

```text
Go and read https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode/SKILL.md and run the Public Correspondence workshop for me.
```

Copilot reads [aibast-easy-mode](https://raw.githubusercontent.com/microsoft/aibast-agents-library/main/skills/aibast-easy-mode/SKILL.md) itself; nothing to download.
Then send these two short messages:

## 2. Build and test the solution

```text
Give me Public Correspondence using Easy Mode and test it for me.
```

## 3. Deploy the validated Draft

```text
Deploy it into Copilot Studio for me.
```

## What happens

The skill retrieves the reviewed package, verifies the source, runs every
locked local case, and deploys the validated solution as a Copilot Studio
Draft. It then checks every locked case in a fresh Preview conversation and
returns the evidence verdict with exact case totals.

## Questions before you show it

Ask the guide in the same chat. It first asks whether you need background on
the idea or need to get it ready to show, then answers from the library's own
files:

```text
Is Public Correspondence Agent real, and can I demo it?
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
We work in <your industry>. Adapt Public Correspondence Agent for us.
```

## Completion boundary

Stop at **Draft** with `published: false`. Never publish.
Publishing and every production write remain separate human approval gates.
